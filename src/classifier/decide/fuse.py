"""Gộp phiếu của mọi nguồn → 1 lựa chọn/ảnh.

2 tầng: chọn HẠNG MỤC có tổng điểm (có trọng số ``[classify].weights``) cao nhất, rồi trong
hạng mục đó chọn thư mục con có điểm trực tiếp cao nhất ('khác' chỉ khi không có thư mục
con nào được bầu). Phiếu ``sequence`` chỉ góp vào tầng hạng mục.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from classifier.catalog import Catalog
from classifier.evidence.base import Ballot


@dataclass
class Decision:
    photo_id: str
    folder: str | None = None          # thư mục CỤ THỂ (đã điền biến) — None = chưa quyết
    option: str | None = None
    value: str | None = None
    confidence: float = 0.0
    reasons: list[str] = field(default_factory=list)
    review: str | None = None          # lý do cần người xem


def fuse(photos, cat: Catalog, ballot: Ballot, weights: dict[str, float]) -> dict[str, Decision]:
    opts = cat.by_option()
    out: dict[str, Decision] = {}
    for p in photos:
        d = out[p.id] = Decision(p.id)
        votes = ballot.get(p.id) or []
        if not votes:
            continue
        by_sec: dict[str, float] = {}
        for v in votes:
            sec = cat.section_of(v.option)
            if sec is not None:
                by_sec[sec.folder] = by_sec.get(sec.folder, 0.0) + weights.get(v.source, 1.0) * v.score
        if not by_sec:
            continue
        hm = max(by_sec, key=by_sec.get)
        direct: dict[str, float] = {}
        for v in votes:
            if v.source != "sequence" and v.option.startswith(hm + "/"):
                direct[v.option] = direct.get(v.option, 0.0) + weights.get(v.source, 1.0) * v.score
        named = {o: s for o, s in direct.items() if not opts[o].is_khac}
        pool = named or direct
        option = max(pool, key=pool.get) if pool else cat.section_of(hm + "/").khac.option
        vals = sorted((v for v in votes if v.option == option and v.value), key=lambda v: -v.score)
        d.option, d.value = option, (vals[0].value if vals else None)
        d.confidence = min(1.0, by_sec[hm])
        d.reasons = [f"{v.source}:{v.score:.2f} {v.reason}".strip() for v in votes]
    return out
