"""Apply fixers for REPAIRABLE issues. One fix per (hm, kind, folder) per call — the loop iterates."""
from __future__ import annotations

from bts_organizer.domain.models import Issue, LayoutResult
from bts_organizer.repair.fixers import FIXERS

# order matters: structure first, then image counts
_PRIORITY = ["missing_khac", "blueprint_in_report", "too_few_folders", "odd_folder_count", "odd_images"]


def repair(layouts: dict[int, LayoutResult], issues: list[Issue]) -> tuple[dict[int, LayoutResult], list[int]]:
    repairable = [i for i in issues if i.severity == "REPAIRABLE"]
    applied: set[tuple] = set()
    touched: set[int] = set()

    for kind in _PRIORITY:
        for iss in repairable:
            if iss.kind != kind or iss.hm_id is None:
                continue
            key = (iss.hm_id, iss.kind, iss.folder)
            if key in applied:
                continue
            L = layouts.get(iss.hm_id)
            if L is None:
                continue
            layouts[iss.hm_id] = FIXERS[iss.kind](L, iss)
            applied.add(key)
            touched.add(iss.hm_id)

    return layouts, sorted(touched)


def failing_hang_muc(issues: list[Issue]) -> list[int]:
    return sorted({i.hm_id for i in issues if i.severity == "REPAIRABLE" and i.hm_id is not None})
