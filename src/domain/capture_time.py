"""Giờ chụp của một ảnh — ``(giờ, phút, giây)``.

Thứ tự ưu tiên: giờ trong TÊN FILE (``ts_pattern``) → chuỗi HH:MM:SS trong stem
(``ts_fallback``) → EXIF DateTimeOriginal → mtime file → ``(0, 0, 0)``.
"""
from __future__ import annotations

import os
import re
from datetime import datetime
from pathlib import Path

from domain.naming import parse


def timestamp_of(filename: str, path: Path | None, *, ts_pattern: str, ts_fallback: str,
                 primary_marker: str) -> tuple[int, int, int]:
    ts = parse(filename, ts_pattern=ts_pattern, primary_marker=primary_marker).ts
    if ts != (0, 0, 0):
        return ts
    m = re.search(ts_fallback, Path(filename).stem)
    if m:
        return int(m[1]), int(m[2]), int(m[3])
    if path is not None:
        exif = _exif_time(path)
        if exif:
            return exif
        try:
            t = datetime.fromtimestamp(os.path.getmtime(str(path)))
            return t.hour, t.minute, t.second
        except OSError:
            pass
    return (0, 0, 0)


def _exif_time(path: Path) -> tuple[int, int, int] | None:
    """EXIF DateTimeOriginal (0x9003) 'YYYY:MM:DD HH:MM:SS' — chuẩn EXIF, không phải SOP."""
    try:
        from infrastructure.filesystem import longpath
        from PIL import Image

        with Image.open(longpath(path)) as im:
            raw = (im.getexif().get_ifd(0x8769) or {}).get(0x9003) or im.getexif().get(0x0132)
        if raw and " " in str(raw):
            hh, mm, ss = str(raw).split(" ", 1)[1].split(":")[:3]
            return int(hh), int(mm), int(ss)
    except Exception:  # noqa: BLE001
        pass
    return None
