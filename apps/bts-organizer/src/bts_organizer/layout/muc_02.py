"""Mục 2 — Kiểm tra khe hở cấu kiện lắp ghép. Two 'chuẩn bị' folders by actual đốt range."""
from __future__ import annotations

from bts_organizer.domain.models import Answer, HangMucInventory, LayoutResult, StationMeta
from bts_organizer.domain.naming import dot_key
from bts_organizer.layout.base import ensure_min_two, folder, group_by, with_khac

BASE = "kiểm tra khe hở cấu kiện lắp ghép"


def plan(inv: HangMucInventory, meta: StationMeta, answers: dict[str, Answer]) -> LayoutResult:
    groups = group_by(inv.files, dot_key)
    khac = list(groups.pop(None, []))
    dots = sorted(d for d in groups if isinstance(d, int))

    if len(dots) >= 2:
        lo, hi = {dots[0], dots[1]}, {dots[-2], dots[-1]}
        lo_imgs = [f for d in lo for f in groups.get(d, [])]
        hi_imgs = [f for d in hi for f in groups.get(d, [])]
        khac += [f for d in groups for f in groups[d] if d not in lo and d not in hi]
        folders = [
            folder(inv, f"Công tác chuẩn bị {BASE} đốt {min(lo)}-{min(lo) + 1}", lo_imgs, cong_tac=True),
            folder(inv, f"Công tác chuẩn bị {BASE} đốt {max(hi) - 1}-{max(hi)}", hi_imgs, cong_tac=True),
        ]
    else:
        allimg = [f for d in groups for f in groups[d]]
        folders = ensure_min_two(
            inv, [folder(inv, f"Công tác chuẩn bị {BASE}", allimg, cong_tac=True)], BASE
        )

    return LayoutResult(
        inv.id, with_khac(inv, folders, khac), delete_dirs=inv.template_junk
    )
