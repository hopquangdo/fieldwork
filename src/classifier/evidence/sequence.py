"""Bằng chứng từ THỨ TỰ CHỤP — ảnh chụp liền nhau thường cùng 1 công tác.

Với mỗi ảnh, các ảnh lân cận (cách ≤ ``window_sec`` giây theo ``taken_at``; thiếu giờ thì
±``window_n`` ảnh theo thứ tự nguồn) góp phiếu YẾU cho HẠNG MỤC của chúng — dồn vào
'khác' của hạng mục đó, để ``fuse`` chỉ dùng như lực kéo khi nguồn chính lưỡng lự.
"""
from __future__ import annotations

from classifier.catalog import Catalog
from classifier.evidence.base import Ballot, Vote


def _secs(t) -> int | None:
    return None if t is None else t[0] * 3600 + t[1] * 60 + t[2]


def collect(photos, cat: Catalog, base: Ballot, *, window_sec: int = 120, window_n: int = 2,
            weight: float = 0.3) -> Ballot:
    ordered = sorted(photos, key=lambda p: (_secs(p.taken_at) is None, _secs(p.taken_at) or 0, p.order))
    best = {pid: max(vs, key=lambda v: v.score) for pid, vs in base.items() if vs}
    out: Ballot = {}
    for i, p in enumerate(ordered):
        t = _secs(p.taken_at)
        for j in range(max(0, i - window_n), min(len(ordered), i + window_n + 1)):
            q = ordered[j]
            if q is p or q.id not in best:
                continue
            tq = _secs(q.taken_at)
            if t is not None and tq is not None and abs(t - tq) > window_sec:
                continue
            sec = cat.section_of(best[q.id].option)
            if sec is None:
                continue
            out.setdefault(p.id, []).append(
                Vote(sec.khac.option, weight * best[q.id].score, "sequence",
                     reason=f"cạnh {q.name}"))
    return out
