"""Chốt chặn CỨNG trước khi ghi (node ``verify``).

Bảo đảm: mọi ảnh xuất hiện đúng 1 lần trong ``assign``; không có 2 ảnh cùng đích
``(thư mục, tên file)``. Vi phạm → ``ctx.report.abort()`` (apply/delete_empty tự
no-op). Đây là bất biến DUY NHẤT không bao giờ giao cho fixer.

Ngoài ra (mềm): báo hạng mục mà mọi thư mục 'Công tác' đều rỗng — SOP yêu cầu
NHẶT BÙ ảnh thủ công.
"""
from __future__ import annotations

from collections import Counter

from runtime import node

from domain.profile import Profile
from domain.folders import hm_of, leaf_of
from domain import sections as S
from domain.state import state


@node("verify")
def conservation(ctx) -> None:
    photos = {p.path for p in state(ctx).photos}
    assign = state(ctx).assign
    assigned = [p for paths in assign.values() for p in paths]

    dup = [p for p, c in Counter(assigned).items() if c > 1]
    if dup:
        ctx.report.abort(f"{len(dup)} ảnh bị gán nhiều lần: {dup[:3]}")
        return
    if set(assigned) != photos:
        lost, extra = photos - set(assigned), set(assigned) - photos
        ctx.report.abort(f"assignment lệch: mất {len(lost)}, thừa {len(extra)} — {sorted(lost | extra)[:3]}")
        return

    clash = [k for k, c in Counter(state(ctx).landing).items() if c > 1]
    if clash:
        ctx.report.abort(f"{len(clash)} cặp (thư mục, tên file) trùng: {clash[:3]}")
        return

    # --- soft: hạng mục thiếu ảnh --------------------------------------------
    nm = Profile.of(ctx).names()
    by_hm: dict[str, int] = {}
    khac_only: dict[str, int] = {}
    for folder, imgs in assign.items():
        if not folder[:1].isdigit():
            continue
        hm = hm_of(folder)
        if nm.is_kept(hm):
            continue
        if nm.is_cong_tac(leaf_of(folder)):
            by_hm[hm] = by_hm.get(hm, 0) + len(imgs)
        elif nm.is_khac(leaf_of(folder)):
            khac_only[hm] = khac_only.get(hm, 0) + len(imgs)
    gaps = sorted(hm for hm in set(by_hm) | set(khac_only) if by_hm.get(hm, 0) == 0)
    if gaps:
        ctx.report.sections[S.SHORT_OF_PHOTOS] = [
            f"{hm}  (chỉ có {khac_only.get(hm, 0)} ảnh trong 'Hình ảnh khác')" for hm in gaps
        ]
        for hm in gaps:
            ctx.emit("step", f"⚠ THIẾU ảnh công tác: {hm}")

    ctx.report.stages[-1].detail = f"{len(photos)} ảnh · {len(state(ctx).moves)} move hợp lệ"
