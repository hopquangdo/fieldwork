"""Fixer cho issue ``unclassified`` / ``misplaced``: rule-match mỗi ảnh → đúng 1
thư mục đích, ghi đè ``state(ctx).assign``. Tự bỏ qua nếu đầu vào đã đúng chỗ.

Ưu tiên: rule khớp (from_folder xác nhận) > soft-match (chỉ 1 rule khớp) >
(fallback.target HOẶC vị trí LOGIC hiện tại trong ``assign`` — vd sau khi
``normalize`` đổi số hạng mục — KHÔNG dùng ``photo.folder`` vật lý trên đĩa,
để không hoàn tác việc đổi số đó cho những ảnh rule không khớp).
"""
from __future__ import annotations

from runtime import node

from domain.issues import CLASSIFY_KINDS
from domain.profile import Profile
from domain.folders import reverse_assign
from domain.matching import RuleMatcher
from domain import sections as S
from domain.state import state


@node("classify")
def classify(ctx) -> None:
    if not any(i.kind in CLASSIFY_KINDS for i in state(ctx).issues):
        st = ctx.report.stages[-1]
        st.status = "skipped"
        st.detail = "mọi ảnh đã đúng chỗ — bỏ qua"
        return

    prof = Profile.of(ctx)
    nm = prof.names()
    hm_dirs: dict = state(ctx).hm_dirs
    totals = nm.ordinal_totals((p.prefix for p in state(ctx).photos), state(ctx).meta)
    matcher = RuleMatcher(prof.rules, hm_dirs, nm, totals)
    fallback = ctx.config.get("fallback.target")
    current = reverse_assign(state(ctx).assign)   # vị trí logic hiện tại (sau normalize…)

    assign: dict[str, list[str]] = {}
    unmatched: list = []
    matched = soft = 0
    for photo in state(ctx).photos:
        cur_folder = current.get(photo.path, photo.folder)
        target, is_soft = matcher.match(photo, current_folder=cur_folder)
        if target is None:
            target = fallback or cur_folder or "Hình ảnh khác"
            unmatched.append(photo)
        elif is_soft:
            soft += 1
            ctx.report.sections.setdefault(S.LOOSE_MATCH, []).append(
                f"{photo.path} → {target}"
            )
        else:
            matched += 1
        assign.setdefault(target, []).append(photo.path)

    state(ctx).assign = assign
    state(ctx).unmatched = unmatched
    ctx.report.stages[-1].detail = (
        f"{matched} khớp rule" + (f" · {soft} khớp lỏng" if soft else "")
        + f" · {len(unmatched)} chưa xếp / {len(state(ctx).photos)}"
    )
    for p in unmatched:
        ctx.emit("step", f"chưa xếp: {p.name}  (giữ ở {p.folder or '/'})")
