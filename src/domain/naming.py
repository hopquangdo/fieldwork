"""Parse tên file ảnh hiện trường. Pattern lấy từ profile ``[filename]``
(``ts_pattern`` + ``primary_marker``) — không hard-code định dạng nào.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Component:
    prefix: str          # casefold, gộp khoảng trắng; "" khi chỉ có giờ chụp
    is_primary: bool
    ts: tuple[int, int, int]


def parse(filename: str, *, ts_pattern: str, primary_marker: str) -> Component:
    stem = Path(filename).name
    head, sep, _ = stem.partition("@")
    prefix = re.sub(r"\s+", " ", head).strip().casefold() if sep else ""
    m = re.search(ts_pattern, stem)
    ts = (int(m[1]), int(m[2]), int(m[3])) if m else (0, 0, 0)
    return Component(prefix=prefix, is_primary=primary_marker in stem, ts=ts)
