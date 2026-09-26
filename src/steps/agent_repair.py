"""Agent (LLM) chạy cuối vòng reconcile — hai việc:

1. **Sửa cấu trúc**: các vi phạm mà ``validate`` còn để lại sau các fixer deterministic.
2. **Rà soát ảnh** (``[agent].review``, chỉ lượt đầu): ảnh đang ở thư mục 'khác' — nơi
   rule không đủ thông tin để xếp. Agent mở ảnh bằng tool ``look`` (vision model, theo
   đúng các thư mục con của hạng mục đó), chỉ chuyển khi độ tin cậy ≥ ``[agent].min_conf``,
   rồi tự ``check`` để giữ cấu trúc hợp lệ. Ngân sách xem ảnh: ``[agent].max_look``.

``soft=True``: thiếu ``LLM_API_KEY`` hoặc agent lỗi → stage 'skipped', pipeline vẫn
chạy tiếp. Mọi tool call + kết quả + lỗi được ghi vào report như các node khác.
Bounded bởi ``_MAX_REPAIR_ITERS`` trong ``pipeline/pipeline.py``.

``Agent.run`` (``agent.agent``) là ``async def`` — node graph là hàm ĐỒNG BỘ nên phải
chạy qua ``llm.run_sync`` (``asyncio.run`` có bảo vệ), KHÔNG gọi ``.run(...)`` trực
tiếp: gọi trực tiếp chỉ tạo coroutine rồi bỏ đó, không raise, không sửa gì — no-op
câm lặng (từng là bug thật, xem ``RuntimeWarning: coroutine ... was never awaited``).
"""
from __future__ import annotations

from runtime import node

from agent.prompt import SYSTEM
from domain.diagnostics import structural_issues
from domain.folders import hm_of, leaf_of
from domain.profile import Profile
from infrastructure import llm
from tools.look import Looker
from tools.repair import AssignEditor, build_tools
from domain import sections as S
from domain.state import state


def review_queue(assign: dict[str, list[str]], nm) -> dict[str, list[str]]:
    """Ảnh cần rà soát: đang ở thư mục 'khác' của hạng mục CÓ thư mục cụ thể để chuyển sang.
    → ``{hạng mục: [tên ảnh]}``."""
    has_specific = {hm_of(f) for f in assign if "/" in f and not nm.is_khac(leaf_of(f))}
    out: dict[str, list[str]] = {}
    for f, photos in sorted(assign.items()):
        if "/" in f and f[:1].isdigit() and nm.is_khac(leaf_of(f)) and photos and hm_of(f) in has_specific:
            out.setdefault(hm_of(f), []).extend(sorted(leaf_of(p) for p in photos))
    return out


@node("agent_repair", soft=True)
def agent_repair(ctx) -> None:
    st = ctx.report.stages[-1]
    prof = Profile.of(ctx)
    cfg = prof.agent
    issues = state(ctx).issues
    s = state(ctx)
    s.repair_iters += 1
    it = s.repair_iters

    first_review = cfg.get("review", False) and not state(ctx).reviewed
    state(ctx).reviewed = True                      # rà soát tối đa 1 lần / lượt chạy
    queue = review_queue(state(ctx).assign, prof.names()) if first_review else {}
    if not issues and not queue:
        st.status = "skipped"
        return

    log: list[str] = ctx.report.sections.setdefault(S.AGENT_LOG, [])

    def emit(kind: str, msg: str) -> None:
        ctx.emit(f"agent:{kind}", msg)

    emit("head", f"{len(issues)}\t{it}")
    for i in issues:
        emit("issue", f"{i.hm}\t{i.kind}\t{i.detail}")

    editor = AssignEditor(state(ctx).assign, prof.names())

    def check() -> list[str]:
        return [f"{i.hm} · {i.kind} · {i.detail}" for i in structural_issues(editor.assign, prof)]

    looker = Looker(ctx, editor, budget=int(cfg.get("max_look", 40)),
                    blueprint_hint=prof.vision.get("blueprint_hint", "")) if queue else None
    tools = build_tools(editor, log=log, emit=emit, iteration=it, check=check,
                        look=looker.look if looker else None)

    parts = [f"[vòng {it}]"]
    if issues:
        parts.append("Các issue cấu trúc cần sửa:\n" + "\n".join(f"- {i.hm} · {i.kind} · {i.detail}" for i in issues))
    if queue:
        min_conf = float(cfg.get("min_conf", 0.7))
        parts.append(
            f"Ảnh cần rà soát (đang ở thư mục 'khác'; ngưỡng tin cậy để chuyển: {min_conf}; "
            f"ngân sách look: {looker.budget} ảnh):\n"
            + "\n".join(f"- {hm}: {', '.join(names)}" for hm, names in queue.items())
        )
    parts.append("Dùng `inspect` xem hiện trạng trước khi sửa.")

    # giao dịch: agent lỗi / làm cấu trúc XẤU hơn → trả assign về như trước khi chạy
    before = {k: list(v) for k, v in editor.assign.items()}
    n_before = len(check())

    def rollback(why: str) -> None:
        editor.assign.clear()
        editor.assign.update(before)
        log.append(f"[vòng {it}] HOÀN TÁC: {why}")

    bot = llm.agent(tools, system=SYSTEM)
    try:
        llm.run_sync(bot.run("\n\n".join(parts),
                             config={"recursion_limit": int(cfg.get("max_steps", 60))}, track=True))
    except Exception as exc:  # noqa: BLE001
        log.append(f"[vòng {it}] AGENT LỖI: {type(exc).__name__}: {str(exc).splitlines()[0]}")
        rollback("agent lỗi")
        st.status = "skipped"
        st.detail = f"agent lỗi: {type(exc).__name__} — đã hoàn tác"
        return
    finally:
        if bot.usage is not None:
            llm.usage(ctx).add(bot.usage)
        llm.publish_usage(ctx)

    if len(check()) > n_before:
        rollback(f"cấu trúc xấu hơn ({n_before} → {len(check())} vi phạm)")
        st.detail = f"vòng {it} · hoàn tác (agent làm cấu trúc xấu hơn)"
        return

    calls = sum(1 for e in log if e.startswith(f"[{it}]"))
    moved = sum(1 for e in log if e.startswith(f"[{it}] reassign") or e.startswith(f"[{it}] swap"))
    errs = sum(1 for e in log if e.startswith(f"[{it}]") and "-> LỖI" in e)
    st.detail = (f"vòng {it} · {calls} tool call · {moved} chuyển/đổi"
                 + (f" · rà soát {sum(map(len, queue.values()))} ảnh" if queue else "")
                 + (f" · {errs} lỗi" if errs else ""))
