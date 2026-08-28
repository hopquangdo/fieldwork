"""Mục 6 — Đo điện trở nối đất / thoát sét. Group by measurement position -> 'Lần N'."""
from __future__ import annotations

from functools import partial

from bts_organizer.domain.models import Answer, HangMucInventory, LayoutResult, StationMeta
from bts_organizer.layout.generic import per_group, skeleton_only

BASE = "đo điện trở nối đất hệ thống thoát sét"
_POS = [
    ("chân cột", "Lần 1"), ("chan cot", "Lần 1"),
    ("kim thu", "Lần 2"), ("thu sét", "Lần 2"), ("thu set", "Lần 2"),
    ("thiết bị", "Lần 3"), ("thiet bi", "Lần 3"), ("treo", "Lần 3"),
]


def _pos(prefix: str) -> str | None:
    for k, v in _POS:
        if k in prefix:
            return v
    return None


def plan(inv: HangMucInventory, meta: StationMeta, answers: dict[str, Answer]) -> LayoutResult:
    if not any(_pos(f.casefold()) for f in inv.files):
        return skeleton_only(inv, meta, answers, base=BASE)
    return per_group(
        inv, meta, answers,
        keyfn=_pos,
        name_for=lambda v: f"Công tác {BASE} {v}",
        base=BASE,
    )
