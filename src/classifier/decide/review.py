"""Quyết định cuối cho từng ảnh: không bằng chứng / dưới ngưỡng / thiếu biến → 'khác' (của
hạng mục nếu biết, không thì gốc) + ghi lý do cần người xem. Không bao giờ đoán biến."""
from __future__ import annotations

from classifier.catalog import Catalog
from classifier.decide.fuse import Decision


def resolve(decisions: dict[str, Decision], cat: Catalog, *, min_conf: float) -> None:
    opts = cat.by_option()
    for d in decisions.values():
        if d.option is None:
            d.folder, d.review = cat.root_khac, "không có bằng chứng"
            continue
        slot = opts[d.option]
        sec = cat.section_of(d.option)
        if d.confidence < min_conf:
            d.folder = sec.khac.option if d.confidence >= min_conf / 2 else cat.root_khac
            d.review = f"độ tin cậy {d.confidence:.2f} < {min_conf} (gợi ý: {d.option})"
            continue
        filled = slot.fill(d.value)
        if filled is None:
            d.folder = sec.khac.option
            d.review = f"đúng hạng mục, chưa rõ {{{slot.var}}} (gợi ý: {d.option})"
            continue
        d.folder = filled
