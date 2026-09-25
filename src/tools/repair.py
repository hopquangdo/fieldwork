"""5 tool an toàn cho agent sửa cấu trúc: ``inspect / reassign / split_folder /
new_empty_pair / finish``.

Mọi thao tác chỉ mutate bảng ``assign`` (dict trong bộ nhớ) và luôn giữ ảnh trong
cùng một hạng mục — conservation ``verify`` vẫn HARD-gate sau đó.
"""
from __future__ import annotations

import json

from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel, Field

from domain.profile import Names
from domain.folders import hm_of, leaf_of, reverse_assign


class AssignEditor:
    """Các phép sửa ``assign`` mà agent được phép làm. Trả chuỗi mô tả kết quả
    (hoặc lý do từ chối) — không raise cho lỗi nghiệp vụ."""

    def __init__(self, assign: dict[str, list[str]], names: Names) -> None:
        self.assign = assign
        self.nm = names

    # -- tra cứu -------------------------------------------------------
    def _find_photo(self, ref: str) -> str | None:
        allp = {p for ps in self.assign.values() for p in ps}
        if ref in allp:
            return ref
        base = ref.rsplit("/", 1)[-1]
        hits = [p for p in allp if p.rsplit("/", 1)[-1] == base]
        return hits[0] if len(hits) == 1 else None

    def _resolve_hm(self, hang_muc: str) -> str:
        """Chuẩn hoá prefix hạng mục do agent cung cấp về namespace THỰC của ``assign``
        (agent có thể nhớ nhầm số hạng mục cũ sau khi ``normalize`` đã đổi số — vd
        "6.X" trong khi ``assign`` chỉ còn "8.X" — tránh tạo shadow-namespace rỗng
        mà ``scaffold``/conservation sau đó coi là hạng mục thật)."""
        hms = {hm_of(k) for k in self.assign if k[:1].isdigit()}
        if hang_muc in hms:
            return hang_muc
        name = hang_muc.split(".", 1)[-1]
        for hm in hms:
            if hm.split(".", 1)[-1] == name:
                return hm
        return hang_muc

    def _find_folder(self, ref: str, hm: str) -> str:
        if ref in self.assign:
            return ref
        if "/" in ref and ref[:1].isdigit() and hm_of(ref) != hm:
            return ref                                   # trỏ sang hạng mục khác → caller từ chối
        for k in self.assign:
            if hm_of(k) == hm and (k == ref or leaf_of(k) == leaf_of(ref)):
                return k
        return ref if ref.startswith(hm + "/") else f"{hm}/{leaf_of(ref)}"

    # -- tool ---------------------------------------------------------
    def inspect(self, hang_muc: str) -> str:
        hang_muc = self._resolve_hm(hang_muc)
        out: dict = {}
        for f in sorted(self.assign):
            if hm_of(f) != hang_muc:
                continue
            names = sorted(p.rsplit("/", 1)[-1] for p in self.assign[f])
            loai = ("công tác" if self.nm.is_cong_tac(leaf_of(f))
                    else "khác" if self.nm.is_khac(leaf_of(f)) else "-")
            out[f] = {"loại": loai, "số ảnh": len(names),
                      "ảnh": names if len(names) <= 15 else names[:15] + ["…"]}
        return json.dumps(out, ensure_ascii=False)

    def reassign(self, photo: str, to_folder: str) -> str:
        p = self._find_photo(photo)
        if not p:
            return "không tìm thấy ảnh"
        src = reverse_assign(self.assign)[p]
        dst = self._find_folder(to_folder, hm_of(src))
        if hm_of(dst) != hm_of(src):
            return "thư mục đích khác hạng mục — từ chối"
        if dst == src:
            return "ảnh đã ở đó"
        self.assign[src].remove(p)
        self.assign.setdefault(dst, []).append(p)
        return f"chuyển '{leaf_of(p)}' : {leaf_of(src)} -> {leaf_of(dst)}"

    def split_folder(self, folder: str) -> str:
        f = self._find_folder(folder, hm_of(folder))
        if not self.assign.get(f):
            return "thư mục rỗng / không tồn tại"
        imgs = self.assign.pop(f)
        base, leaf = f.rsplit("/", 1)
        la, lb = self.nm.pair(self.nm.pair_core(leaf))
        half = (len(imgs) + 1) // 2
        # GỘP vào đích (không ghi đè) — thư mục cặp có thể đã tồn tại và đang chứa ảnh
        self.assign.setdefault(f"{base}/{la}", []).extend(imgs[:half])
        self.assign.setdefault(f"{base}/{lb}", []).extend(imgs[half:])
        return f"tách '{leaf}' -> '{la}' + '{lb}'"

    def new_empty_pair(self, hang_muc: str, base: str) -> str:
        hang_muc = self._resolve_hm(hang_muc)
        la, lb = self.nm.pair(base)
        self.assign.setdefault(f"{hang_muc}/{la}", [])
        self.assign.setdefault(f"{hang_muc}/{lb}", [])
        return f"tạo cặp thư mục rỗng '{base}'"


# ── pydantic schema cho từng tool ─────────────────────────────────────
class _HM(BaseModel):
    hang_muc: str = Field(..., description="Prefix hạng mục (thư mục cấp 1), vd '3.<tên hạng mục>'")


class _Reassign(BaseModel):
    photo: str = Field(..., description="Tên ảnh (hoặc đường dẫn) cần chuyển")
    to_folder: str = Field(..., description="Thư mục đích, CÙNG hạng mục với ảnh")


class _Folder(BaseModel):
    folder: str = Field(..., description="Đường dẫn thư mục cần tách đôi")


class _Pair(BaseModel):
    hang_muc: str
    base: str = Field(..., description="Tên gốc của cặp thư mục cần tạo")


class _Done(BaseModel):
    note: str = ""


def _clip(s: str, n: int) -> str:
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[:n] + " …"


def build_tools(editor: AssignEditor, *, log: list[str], emit, iteration: int) -> list[BaseTool]:
    """Bọc các phép sửa của ``editor`` thành StructuredTool có ghi log + stream sự kiện."""

    def logged(name: str, fn):
        def wrapper(**kw):
            sig = ", ".join(f"{k}={v!r}" for k, v in kw.items())
            emit("tool", f"{name}({_clip(sig, 140)})")
            try:
                out = fn(**kw)
                log.append(f"[{iteration}] {name}({sig}) -> {out}")
                emit("result", _clip(out, 160))
                return out
            except Exception as e:  # noqa: BLE001
                log.append(f"[{iteration}] {name}({sig}) -> LỖI: {type(e).__name__}: {e}")
                emit("error", f"{type(e).__name__}: {e}")
                return f"LỖI: {e}"
        return wrapper

    def finish(note: str = "") -> str:
        return f"hoàn tất. {note}".strip()

    specs = [
        ("inspect", editor.inspect, _HM, "Xem các thư mục + số ảnh của 1 hạng mục."),
        ("reassign", editor.reassign, _Reassign, "Chuyển 1 ảnh sang thư mục khác cùng hạng mục."),
        ("split_folder", editor.split_folder, _Folder, "Tách 1 thư mục thành cặp 'chuẩn bị' + 'đo'."),
        ("new_empty_pair", editor.new_empty_pair, _Pair, "Tạo 1 cặp thư mục rỗng."),
        ("finish", finish, _Done, "Gọi khi đã sửa xong tất cả issue."),
    ]
    return [
        StructuredTool.from_function(logged(name, fn), name=name, args_schema=schema, description=desc)
        for name, fn, schema, desc in specs
    ]
