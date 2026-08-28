"""Reusable strategy shapes: per-component grouping + skeleton-only."""
from __future__ import annotations

from typing import Callable

from bts_organizer.domain.models import Answer, HangMucInventory, LayoutResult, StationMeta
from bts_organizer.layout.base import (
    ensure_min_two,
    folder,
    group_by,
    scaffold,
    split_labels,
    trim_even,
    with_khac,
)


def per_group(
    inv: HangMucInventory,
    meta: StationMeta,
    answers: dict[str, Answer],
    *,
    keyfn: Callable[[str], object],
    name_for: Callable[[object], str],
    base: str,
    prefer: int = 4,
    pair_when_odd: bool = False,
) -> LayoutResult:
    groups = group_by(inv.files, keyfn)
    khac_extra = list(groups.pop(None, []))  # unparseable -> khác
    folders = []
    for key in sorted(groups, key=str):
        kept, surplus = trim_even(groups[key], prefer)
        folders.append(folder(inv, name_for(key), kept, cong_tac=True))
        khac_extra += surplus

    if pair_when_odd and len([f for f in folders if f.is_cong_tac]) % 2 == 1 and folders:
        last = folders.pop()
        imgs = last.images
        half = (len(imgs) + 1) // 2
        prep, main = split_labels(last.path.rsplit("/", 1)[1])
        folders += [
            folder(inv, prep, imgs[:half], cong_tac=True),
            folder(inv, main, imgs[half:], cong_tac=True),
        ]

    folders = ensure_min_two(inv, folders, base)
    folders = with_khac(inv, folders, khac_extra)
    return LayoutResult(inv.id, folders, delete_dirs=inv.template_junk)


def skeleton_only(inv: HangMucInventory, meta, answers, *, base: str) -> LayoutResult:
    """No usable component names / no images: just the empty appendix skeleton."""
    folders = [*scaffold(inv, base)]
    folders = with_khac(inv, folders, list(inv.files))  # any stray images kept in khác
    return LayoutResult(inv.id, folders, delete_dirs=inv.template_junk)
