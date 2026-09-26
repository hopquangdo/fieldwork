"""Fixer cho issue ``dot_range`` (SOP §2 Mục 2) — đặt tên thư mục khe hở theo đốt.

Logic gộp/đặt tên nằm ở :class:`~domain.dot_grouping.DotGrouper`; node này
chỉ lặp qua các khai báo ``[[dot_range]]`` của profile và áp dụng. Chỉ chạy khi
profile có block đó.
"""
from __future__ import annotations

from runtime import node

from domain.profile import Profile
from domain.dot_grouping import DotGrouper
from steps.validate import dot_range_pending
from domain.state import state


@node("dot_range")
def dot_range(ctx) -> None:
    prof = Profile.of(ctx)
    specs = prof.dot_range
    if not specs or not dot_range_pending(ctx):
        ctx.report.stages[-1].status = "skipped"
        ctx.report.stages[-1].detail = "không có thư mục theo đốt cần gộp"
        return

    grouper = DotGrouper(prof.names())
    assign: dict[str, list[str]] = state(ctx).assign
    done = sum(1 for spec in specs if grouper.apply(assign, spec) is not None)

    ctx.report.stages[-1].detail = f"đặt tên thư mục theo đốt: {done} hạng mục"
