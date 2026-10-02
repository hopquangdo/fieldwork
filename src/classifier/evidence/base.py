"""Phiếu bầu của các nguồn bằng chứng.

Mỗi nguồn: ``collect(photos, catalog, ...) -> Ballot`` — ``{photo.id: [Vote…]}``.
``Vote.option`` là khoá ``Slot.option`` của mục lục (mẫu chưa điền biến); ``value`` là giá
trị biến nếu nguồn thấy rõ (vd "M2", "chân cột").
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Vote:
    option: str
    score: float                 # 0..1 — độ tin cậy của CHÍNH nguồn này
    source: str                  # "filename" · "vision" · "sequence"
    value: str | None = None
    reason: str = ""


Ballot = dict[str, list[Vote]]


def merge(*ballots: Ballot) -> Ballot:
    out: Ballot = {}
    for b in ballots:
        for pid, votes in b.items():
            out.setdefault(pid, []).extend(votes)
    return out
