"""Đổi tên thư mục con về tên CHUẨN của SOP (``[[subfolders]]`` trong profile).

Chạy sau ``dot_range`` (đã có thư mục theo đốt), trước ``scaffold`` (để cặp/khác được
dựng trên tên chuẩn). Thư mục trùng tên chuẩn thì GỘP (vd "01.… cánh 1 Đốt D1",
"01.… cánh 2 Đốt D1" → "… Đốt D1"); không khớp mẫu nào → giữ nguyên hoặc dồn 'khác'
theo ``unmatched`` — luôn ghi "cần người xem", không tự chế tên. Logic ở
:class:`~domain.canonical.CanonicalNamer`.
"""
from __future__ import annotations

from runtime import node

from domain.profile import Profile
from domain.canonical import CanonicalNamer
from domain import sections as S
from domain.state import state


@node("canonicalize")
def canonicalize(ctx) -> None:
    prof = Profile.of(ctx)
    st = ctx.report.stages[-1]
    if not prof.subfolders:
        st.status = "skipped"
        st.detail = "profile không khai [[subfolders]] — bỏ qua"
        return

    nm = prof.names()
    out = CanonicalNamer(prof).apply(state(ctx).assign, kept=nm.is_kept)
    if out["renamed"]:
        ctx.report.sections[S.RENAMED_DIRS] = out["renamed"]
    if out["review"]:
        ctx.report.sections.setdefault(S.NEEDS_REVIEW, []).extend(out["review"])
        for r in out["review"][:5]:
            ctx.emit("step", f"⚠ {r}")
    st.detail = f"đổi tên {len(out['renamed'])} thư mục · {len(out['review'])} cần người xem"
