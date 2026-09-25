"""Vòng sửa bằng LLM — ReAct agent sửa các vi phạm mà ``validate`` còn để lại sau
các fixer deterministic.

``soft=True``: thiếu ``LLM_API_KEY`` hoặc agent lỗi → stage 'skipped', pipeline vẫn
chạy tiếp. Mọi tool call + kết quả + lỗi được ghi vào report như các node khác.
Bounded bởi ``_MAX_REPAIR_ITERS`` trong ``pipeline/graph.py``.

``Agent.run`` (``agent.agent``) là ``async def`` — node graph là hàm ĐỒNG BỘ nên phải
chạy qua ``llm.run_sync`` (``asyncio.run`` có bảo vệ), KHÔNG gọi ``.run(...)`` trực
tiếp: gọi trực tiếp chỉ tạo coroutine rồi bỏ đó, không raise, không sửa gì — no-op
câm lặng (từng là bug thật, xem ``RuntimeWarning: coroutine ... was never awaited``).
"""
from __future__ import annotations

from runtime import node

from agent.prompt import SYSTEM
from tools.repair import AssignEditor, build_tools
from infrastructure import llm
from domain.profile import Profile


@node("agent_repair", soft=True)
def agent_repair(ctx) -> None:
    st = ctx.report.stages[-1]
    issues = ctx.data.get("issues", [])
    it = ctx.data["repair_iters"] = ctx.data.get("repair_iters", 0) + 1
    if not issues:
        st.status = "skipped"
        return

    log: list[str] = ctx.report.sections.setdefault("agent_repair · nhật ký tool", [])

    def emit(kind: str, msg: str) -> None:
        ctx.emit(f"agent:{kind}", msg)

    emit("head", f"{len(issues)}\t{it}")
    for i in issues:
        emit("issue", f"{i.hm}\t{i.kind}\t{i.detail}")

    editor = AssignEditor(ctx.data["assign"], Profile.of(ctx).names())
    tools = build_tools(editor, log=log, emit=emit, iteration=it)
    issue_text = "\n".join(f"- {i.hm} · {i.kind} · {i.detail}" for i in issues)
    hms = sorted({i.hm for i in issues})

    bot = llm.agent(tools, system=SYSTEM)
    try:
        llm.run_sync(bot.run(
            f"[vòng {it}] Các issue cần sửa:\n{issue_text}\n"
            f"Hạng mục liên quan: {hms}\nDùng `inspect` xem hiện trạng trước khi sửa.",
            config={"recursion_limit": 40}, track=True,
        ))
    except Exception as exc:  # noqa: BLE001
        log.append(f"[vòng {it}] AGENT LỖI: {type(exc).__name__}: {exc}")
        st.status = "skipped"
        st.detail = f"agent lỗi: {type(exc).__name__}"
        return
    finally:
        if bot.usage is not None:
            llm.usage(ctx).add(bot.usage)
        llm.publish_usage(ctx)

    calls = sum(1 for e in log if e.startswith(f"[{it}]"))
    errs = sum(1 for e in log if e.startswith(f"[{it}]") and "-> LỖI" in e)
    st.detail = f"vòng {it} · {calls} tool call" + (f" · {errs} lỗi" if errs else "")
