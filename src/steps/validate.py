"""Kiểm tra lại cấu trúc trong vòng lặp ``validate ↔ agent_repair``.

Chỉ soát bất biến cấu trúc (không soát phân loại — việc đó ``check`` làm 1 lần đầu),
tính TƯƠI mỗi vòng để vòng lặp hội tụ. Hết vi phạm → đi ``plan``.

Cũng cung cấp adapter cho các fixer (``scaffold`` / ``even_four`` / ``dot_range``)
để chúng tự quyết có việc làm hay không dựa trên trạng thái ``assign`` hiện tại.
"""
from __future__ import annotations

from runtime import node

from domain.issues import Issue
from domain.profile import Profile
from domain.diagnostics import per_dot, structural_issues
from domain import sections as S
from domain.state import state


@node("validate")
def validate(ctx) -> None:
    issues = issues_now(ctx)
    state(ctx).issues = issues

    st = ctx.report.stages[-1]
    st.detail = "hợp lệ" if not issues else f"{len(issues)} vấn đề → repair"
    if not issues:
        ctx.emit("step", "cấu trúc đạt chuẩn cặp/chẵn/khác")
        return
    ctx.report.sections[S.issues_round(state(ctx).repair_iters)] = [
        f"{i.hm} · {i.kind} · {i.detail}" for i in issues
    ]
    by_hm: dict[str, int] = {}
    for i in issues:
        by_hm[i.hm] = by_hm.get(i.hm, 0) + 1
    for hm, n in sorted(by_hm.items()):
        ctx.emit("step", f"{hm}: {n} vấn đề")


def issues_now(ctx) -> list[Issue]:
    """Vi phạm cấu trúc HIỆN TẠI — fixer gọi để biết còn việc không."""
    return structural_issues(state(ctx).assign, Profile.of(ctx))


def dot_range_pending(ctx) -> bool:
    """Còn hạng mục ``[[dot_range]]`` nào có ≥2 thư mục công-tác per-đốt không."""
    prof = Profile.of(ctx)
    nm = prof.names()
    return any(len(per_dot(state(ctx).assign, s["hm_prefix"], nm)) >= 2 for s in prof.dot_range)
