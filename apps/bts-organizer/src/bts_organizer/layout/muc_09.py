"""Mục 9 — Đo kích thước cấu kiện & siêu âm thanh cánh. One folder per component type."""
from __future__ import annotations

from bts_organizer.domain.models import Answer, HangMucInventory, LayoutResult, StationMeta
from bts_organizer.layout.generic import per_group

BASE = "đo kích thước cấu kiện"
_CK = [
    ("ma ní", "Đo kích thước ma ní"), ("ma ni", "Đo kích thước ma ní"),
    ("tăng đơ", "Đo kích thước tăng đơ"), ("tang do", "Đo kích thước tăng đơ"),
    ("vòng ốp", "Đo kích thước vòng ốp và bu lông dây co"),
    ("bu lông", "Đo kích thước vòng ốp và bu lông dây co"),
    ("bulong", "Đo kích thước vòng ốp và bu lông dây co"),
    ("thanh cánh", "Siêu âm thanh cánh"), ("thanh canh", "Siêu âm thanh cánh"),
    ("móng", "Đo kích thước móng cột anten"), ("mong", "Đo kích thước móng cột anten"),
    ("đốt", "Đo kích thước thân cột"), ("dot", "Đo kích thước thân cột"),
]


def _ck(prefix: str) -> str | None:
    for k, v in _CK:
        if k in prefix:
            return v
    return None


def plan(inv: HangMucInventory, meta: StationMeta, answers: dict[str, Answer]) -> LayoutResult:
    return per_group(
        inv, meta, answers, keyfn=_ck, name_for=lambda v: v, base=BASE
    )
