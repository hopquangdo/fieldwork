"""Chẩn đoán đầu vào — chạy ngay sau ``scan``, trước mọi fixer.

Liệt kê MỌI vi phạm SOP của trạm ở trạng thái thô (cấu trúc + ảnh chưa xếp/sai chỗ +
dot_range) vào ``state(ctx).issues`` và report ``"vấn đề đầu vào"``. Không sửa gì,
không rẽ nhánh — mỗi fixer tự quyết chạy hay bỏ qua dựa trên danh sách này.
"""
from __future__ import annotations

from runtime import node

from domain.profile import Profile
from domain.diagnostics import baseline_issues
from domain import sections as S
from domain.state import state


@node("check")
def check(ctx) -> None:
    prof = Profile.of(ctx)
    issues = baseline_issues(
        state(ctx).assign, state(ctx).photos, state(ctx).hm_dirs, prof,
    )
    state(ctx).issues = issues
    state(ctx).repair_iters

    st = ctx.report.stages[-1]
    st.detail = "đầu vào đạt chuẩn" if not issues else f"{len(issues)} vấn đề đầu vào"
    if not issues:
        return
    ctx.report.sections[S.INPUT_ISSUES] = [f"{i.hm} · {i.kind} · {i.detail}" for i in issues]

    by_hm: dict[str, int] = {}
    for i in issues:
        by_hm[i.hm] = by_hm.get(i.hm, 0) + 1
    for hm, n in sorted(by_hm.items()):
        ctx.emit("step", f"{hm}: {n} vấn đề")
