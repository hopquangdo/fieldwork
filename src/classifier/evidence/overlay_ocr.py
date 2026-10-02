"""Giờ chụp: tên file → EXIF → CHỮ IN TRÊN ẢNH (app GPS/Timestamp Camera, đọc bằng vision
— xem ``evidence.vision``). Không bỏ phiếu; chỉ điền ``Photo.taken_at`` cho ``sequence``."""
from __future__ import annotations

import re

from domain.capture_time import _exif_time

_HMS = re.compile(r"(\d{1,2})\s*[:h]\s*(\d{2})(?:\s*[:m]\s*(\d{2}))?")


def parse_hms(text: str | None) -> tuple[int, int, int] | None:
    m = _HMS.search(text or "")
    if not m:
        return None
    h, mi, s = int(m[1]), int(m[2]), int(m[3] or 0)
    return (h, mi, s) if h < 24 and mi < 60 and s < 60 else None


def fill_times(photos, overlay: dict[str, str | None]) -> int:
    """Điền ``taken_at`` còn thiếu: EXIF, rồi giờ vision đọc trên ảnh. → số ảnh có giờ."""
    for p in photos:
        if p.taken_at is None:
            p.taken_at = _exif_time(p.path) or parse_hms(overlay.get(p.id))
    return sum(p.taken_at is not None for p in photos)
