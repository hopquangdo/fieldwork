"""A real ReAct agent (agent_core) that fixes edge-case structure issues `validate` flags.

The agent has a small, safe tool set that mutates only the in-memory ``assign`` — it
cannot touch disk or delete photos. Every tool call + result (and errors) is logged into
the report, same as the other nodes. Conservation `check` still HARD-gates afterwards.
"""
from __future__ import annotations

import json

from graphrun import node
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from photo_sort import llm
from photo_sort.domain.folders import hm_of, is_cong_tac, is_khac, leaf_of

_SYSTEM = (
    "Bạn là trợ lý sắp xếp thư mục phụ lục kiểm định cột BTS. Nhiệm vụ: sửa các 'issue' để "
    "mỗi hạng mục đạt chuẩn SOP:\n"
    "• ≥2 thư mục 'Công tác …' đi theo cặp → SỐ CHẴN thư mục\n"
    "• mỗi thư mục công tác: SỐ ẢNH CHẴN (ưu tiên ≤4)\n"
    "• luôn có 1 'Hình ảnh khác'\n"
    "Chỉ được dùng các tool. KHÔNG xoá ảnh, KHÔNG tạo hạng mục mới. Ảnh dư → chuyển sang "
    "'Hình ảnh khác' của chính hạng mục đó.\n"
    "LUÔN gọi `inspect` trước để lấy TÊN ẢNH CHÍNH XÁC — chỉ dùng tên có trong kết quả inspect, "
    "không tự bịa tên. Sửa xong gọi `finish`."
)


@node("agent_repair", soft=True)
def agent_repair(ctx) -> None:
    st = ctx.report.stages[-1]
    issues = ctx.data.get("issues", [])
    ctx.data["repair_iters"] = ctx.data.get("repair_iters", 0) + 1
    it = ctx.data["repair_iters"]

    if not issues:
        st.status = "skipped"
        return
    if not llm.available():
        st.status = "skipped"
        st.detail = "không có LLM_API_KEY — bỏ qua (scaffold đã lo phần cơ bản)"
        return

    assign: dict = ctx.data["assign"]
    hms = sorted({i.hm for i in issues})
    log: list[str] = ctx.report.sections.setdefault("agent_repair · nhật ký tool", [])

    def emit(kind: str, msg: str) -> None:
        ctx.emit(f"agent:{kind}", msg)

    emit("head", f"{len(issues)}\t{it}")
    for i in issues:
        emit("issue", f"{i.hm}\t{i.kind}\t{i.detail}")
    tools = _make_tools(assign, it, log, emit)

    issue_text = "\n".join(f"- {i.hm} · {i.kind} · {i.detail}" for i in issues)
    try:
        bot = llm.agent(tools, system=_SYSTEM)
        bot.run(
            f"[vòng {it}] Các issue cần sửa:\n{issue_text}\n"
            f"Hạng mục liên quan: {hms}\nDùng `inspect` xem hiện trạng trước khi sửa.",
            config={"recursion_limit": 40},
        )
    except Exception as exc:  # noqa: BLE001
        log.append(f"[vòng {it}] AGENT LỖI: {type(exc).__name__}: {exc}")
        st.status = "skipped"
        st.detail = f"agent lỗi: {type(exc).__name__}"
        return

    calls = sum(1 for e in log if e.startswith(f"[{it}]"))
    errs = sum(1 for e in log if "-> LỖI" in e and e.startswith(f"[{it}]"))
    st.detail = f"vòng {it} · {calls} tool call" + (f" · {errs} lỗi" if errs else "")


def _make_tools(assign: dict, it: int, log: list[str], emit=lambda *_: None):
    def _clip(s: str, n: int = 200) -> str:
        s = " ".join(str(s).split())
        return s if len(s) <= n else s[:n] + " …"

    def _tag() -> str:
        return f"[{it}]"

    def _where() -> dict:
        return {p: f for f, ps in assign.items() for p in ps}

    def _find_photo(ref: str) -> str | None:
        allp = {p for ps in assign.values() for p in ps}
        if ref in allp:
            return ref
        base = ref.rsplit("/", 1)[-1]
        hits = [p for p in allp if p.rsplit("/", 1)[-1] == base]
        return hits[0] if len(hits) == 1 else None

    def _find_folder(ref: str, hm: str) -> str:
        if ref in assign:
            return ref
        if "/" in ref and ref[:1].isdigit() and hm_of(ref) != hm:
            return ref                                  # points elsewhere -> caller refuses
        for k in assign:
            if hm_of(k) == hm and (k == ref or leaf_of(k) == leaf_of(ref)):
                return k
        return ref if ref.startswith(hm + "/") else f"{hm}/{leaf_of(ref)}"

    def _logged(name: str):
        def deco(fn):
            def wrapper(**kw):
                sig = ", ".join(f"{k}={v!r}" for k, v in kw.items())
                emit("tool", f"{name}({_clip(sig, 140)})")
                try:
                    out = fn(**kw)
                    log.append(f"{_tag()} {name}({sig}) -> {out}")
                    emit("result", _clip(out, 160))
                    return out
                except Exception as e:  # noqa: BLE001
                    log.append(f"{_tag()} {name}({sig}) -> LỖI: {type(e).__name__}: {e}")
                    emit("error", f"{type(e).__name__}: {e}")
                    return f"LỖI: {e}"
            return wrapper
        return deco

    # ---- tool schemas -----------------------------------------------------
    class _HM(BaseModel):
        hang_muc: str = Field(..., description="Prefix hạng mục, vd '3.Công tác đo lực căng trong dây co'")

    class _Reassign(BaseModel):
        photo: str = Field(..., description="Tên ảnh (hoặc đường dẫn) cần chuyển")
        to_folder: str = Field(..., description="Thư mục đích (cùng hạng mục). Vd '…/Hình ảnh khác'")

    class _Folder(BaseModel):
        folder: str = Field(..., description="Đường dẫn thư mục công tác cần tách đôi")

    class _Pair(BaseModel):
        hang_muc: str
        base: str = Field(..., description="Tên gốc, vd 'kiểm tra lực siết ê-cu khóa cáp'")

    class _Done(BaseModel):
        note: str = ""

    @_logged("inspect")
    def inspect(hang_muc: str) -> str:
        out = {}
        for f in sorted(assign):
            if hm_of(f) != hang_muc:
                continue
            names = sorted(p.rsplit("/", 1)[-1] for p in assign[f])
            out[f] = {
                "loại": "công tác" if is_cong_tac(leaf_of(f)) else ("khác" if is_khac(leaf_of(f)) else "-"),
                "số ảnh": len(names),
                "ảnh": names if len(names) <= 15 else names[:15] + ["…"],
            }
        return json.dumps(out, ensure_ascii=False)

    @_logged("reassign")
    def reassign(photo: str, to_folder: str) -> str:
        p = _find_photo(photo)
        if not p:
            return "không tìm thấy ảnh"
        src = _where()[p]
        dst = _find_folder(to_folder, hm_of(src))
        if hm_of(dst) != hm_of(src):
            return "thư mục đích khác hạng mục — từ chối"
        if dst == src:
            return "ảnh đã ở đó"
        assign[src].remove(p)
        assign.setdefault(dst, []).append(p)
        return f"chuyển '{leaf_of(p)}' : {leaf_of(src)} -> {leaf_of(dst)}"

    @_logged("split_folder")
    def split_folder(folder: str) -> str:
        f = _find_folder(folder, hm_of(folder))
        if not assign.get(f):
            return "thư mục rỗng / không tồn tại"
        imgs = assign.pop(f)
        base, leaf = f.rsplit("/", 1)
        core = leaf.replace("Công tác chuẩn bị ", "").replace("Công tác đo ", "").replace("Công tác ", "")
        assign[f"{base}/Công tác chuẩn bị {core}"] = imgs[: (len(imgs) + 1) // 2]
        assign[f"{base}/Công tác đo {core}"] = imgs[(len(imgs) + 1) // 2:]
        return f"tách '{leaf}' -> chuẩn bị + đo"

    @_logged("new_empty_pair")
    def new_empty_pair(hang_muc: str, base: str) -> str:
        assign.setdefault(f"{hang_muc}/Công tác chuẩn bị {base}", [])
        assign.setdefault(f"{hang_muc}/Công tác {base}", [])
        return f"tạo cặp thư mục rỗng '{base}'"

    @_logged("finish")
    def finish(note: str = "") -> str:
        return f"hoàn tất. {note}".strip()

    return [
        StructuredTool.from_function(inspect, name="inspect", args_schema=_HM,
                                     description="Xem các thư mục + số ảnh của 1 hạng mục."),
        StructuredTool.from_function(reassign, name="reassign", args_schema=_Reassign,
                                     description="Chuyển 1 ảnh sang thư mục khác cùng hạng mục."),
        StructuredTool.from_function(split_folder, name="split_folder", args_schema=_Folder,
                                     description="Tách 1 thư mục công tác thành 'chuẩn bị' + 'đo'."),
        StructuredTool.from_function(new_empty_pair, name="new_empty_pair", args_schema=_Pair,
                                     description="Tạo 1 cặp thư mục công tác rỗng."),
        StructuredTool.from_function(finish, name="finish", args_schema=_Done,
                                     description="Gọi khi đã sửa xong tất cả issue."),
    ]
