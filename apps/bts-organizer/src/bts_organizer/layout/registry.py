"""Pick a strategy per hạng mục by name (works for both tower types).

A strategy is a pure function ``(HangMucInventory, StationMeta, answers) -> LayoutResult``.
"""
from __future__ import annotations

from functools import partial
from typing import Callable

from bts_organizer.domain.models import Answer, HangMucInventory, LayoutResult, StationMeta
from bts_organizer.domain.naming import mong_key
from bts_organizer.layout import muc_01, muc_02, muc_06, muc_08, muc_09, muc_10
from bts_organizer.layout.generic import per_group, skeleton_only

Strategy = Callable[[HangMucInventory, StationMeta, dict[str, Answer]], LayoutResult]


def _per_mong(inv, meta, answers, *, base: str, folder_word: str, pair_when_odd: bool = False) -> LayoutResult:
    return per_group(
        inv, meta, answers,
        keyfn=mong_key,
        name_for=lambda m: f"Công tác {folder_word} {base} {m}",
        base=base,
        pair_when_odd=pair_when_odd,
    )


def strategy_for(inv: HangMucInventory) -> Strategy:
    n = inv.name.casefold()
    # order matters — check the most specific / most easily-confused names first
    if "tổng thể" in n:
        return muc_01.plan
    if "trèo cao" in n:
        return muc_08.plan
    if "dị tật" in n:
        return muc_10.plan
    if "khe hở" in n:
        return muc_02.plan
    if "điện trở" in n:
        return muc_06.plan
    if "kích thước" in n or "siêu âm" in n:
        return muc_09.plan
    if "lực căng" in n:
        return partial(_per_mong, base="đo lực căng trong dây co", folder_word="chuẩn bị")
    if "khóa cáp" in n:
        return partial(_per_mong, base="kiểm tra lực siết ê-cu khóa cáp", folder_word="chuẩn bị")
    if "bê tông" in n:
        return partial(_per_mong, base="kiểm tra cường độ bê tông móng", folder_word="chuẩn bị", pair_when_odd=True)
    return partial(skeleton_only, base="kiểm tra")


def run_strategy(inv: HangMucInventory, meta: StationMeta, answers: dict[str, Answer]) -> LayoutResult:
    return strategy_for(inv)(inv, meta, answers)
