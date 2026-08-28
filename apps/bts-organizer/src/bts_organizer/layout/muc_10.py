"""Mục 10 (dây co) / 8 (tự đứng) — Dị tật bất thường. Keep as-is."""
from __future__ import annotations

from bts_organizer.domain.models import Answer, HangMucInventory, LayoutResult, StationMeta
from bts_organizer.layout.base import keep_in_place


def plan(inv: HangMucInventory, meta: StationMeta, answers: dict[str, Answer]) -> LayoutResult:
    return keep_in_place(inv)
