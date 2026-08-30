"""SOP filename convention: ``<cấu kiện>@<giờ>@<phút>@<giây>@--<1|0>--.jpg``."""
from __future__ import annotations

import os
import re
from datetime import datetime
from pathlib import Path

from photo_sort.domain.naming import parse

_CONFORM = re.compile(r".+@\s*\d{1,2}@\s*\d{1,2}@\s*\d{1,2}@--[01]--\.[A-Za-z0-9]+$")
_HHMMSS = re.compile(r"(?<!\d)([01]?\d|2[0-3])[ ._-]?([0-5]\d)[ ._-]?([0-5]\d)(?!\d)")

_STRIP = (
    "Hình ảnh chuẩn bị ", "Hình ảnh khác ", "Hình ảnh ",
    "Công tác chuẩn bị ", "Công tác đo ", "Công tác kiểm tra ", "Công tác ",
)
_TRAIL_KEY = re.compile(r"\s+((?:M\d+)|(?:D\d+)|(?:Tầng dây \d+)|(?:Lần \d+))$")


def conforms(filename: str) -> bool:
    return bool(_CONFORM.match(Path(filename).name))


def timestamp_of(filename: str, path: Path | None = None) -> tuple[int, int, int]:
    ts = parse(filename).ts
    if ts != (0, 0, 0):
        return ts
    m = _HHMMSS.search(Path(filename).stem)
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
    """EXIF DateTimeOriginal (0x9003) 'YYYY:MM:DD HH:MM:SS' — the real capture time."""
    try:
        from fs_tools import longpath
        from PIL import Image

        with Image.open(longpath(path)) as im:
            raw = (im.getexif().get_ifd(0x8769) or {}).get(0x9003) or im.getexif().get(0x0132)
        if raw and " " in str(raw):
            hh, mm, ss = str(raw).split(" ", 1)[1].split(":")[:3]
            return int(hh), int(mm), int(ss)
    except Exception:  # noqa: BLE001
        pass
    return None


def content_name(folder_leaf: str, naming_rules: list[dict]) -> str:
    lo = folder_leaf.casefold()
    trail = _TRAIL_KEY.search(folder_leaf)
    key = f" {trail[1]}" if trail else ""            # keep 'M2' / 'D3' / 'Tầng dây 1'
    key = key.replace(" M", " Móng M") if key.strip().startswith("M") else key

    for r in naming_rules:
        if any(s.casefold() in lo for s in r.get("folder", [])):
            return (r["name"] + key).strip()
    for pre in _STRIP:
        if folder_leaf.startswith(pre):
            return (folder_leaf[len(pre):] or folder_leaf)
    return folder_leaf


def build_name(content: str, ts: tuple[int, int, int], *, primary: bool, ext: str, seq: int = 0) -> str:
    h, m, s = ts
    suffix = f"@--{'1' if primary else '0'}--"
    tag = f"@{h}@{m:02d}@{s:02d}" + (f"@{seq}" if seq else "")
    return f"{content}{tag}{suffix}{ext}"
