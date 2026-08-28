"""Mục 8 — Trèo cao. Rarely has photos; scaffold the empty skeleton, never force even."""
from __future__ import annotations

from bts_organizer.domain.models import Answer, HangMucInventory, LayoutResult, StationMeta
from bts_organizer.layout.base import folder, with_khac

BASE = "trèo cao (kiểm tra đường hàn, lực siết ê-cu,..)"
_POS = ["chuẩn bị", "tại chân cột", "tại giữa cột", "tại đỉnh cột"]


def plan(inv: HangMucInventory, meta: StationMeta, answers: dict[str, Answer]) -> LayoutResult:
    def bucket(f: str) -> str:
        low = f.casefold()
        for p in _POS[1:]:
            if p.split()[-1] in low:
                return p
        return "chuẩn bị"

    used = {}
    for f in inv.files:
        used.setdefault(bucket(f), []).append(f)

    names = list(used) or _POS[:2]
    folders = [folder(inv, f"Công tác {BASE.split(' (')[0]} {n}".strip(), used.get(n, []), cong_tac=True) for n in names]
    if len(folders) < 2:  # keep at least a pair of (possibly empty) folders — do NOT force even beyond that
        folders += [folder(inv, f"Công tác {BASE.split(' (')[0]} tại chân cột", [], cong_tac=True)]
    return LayoutResult(inv.id, with_khac(inv, folders, []), delete_dirs=inv.template_junk)
