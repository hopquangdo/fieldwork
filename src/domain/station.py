"""Xác định cấu trúc một trạm trên đĩa.

Một trạm là thư mục có các thư mục con **đánh số** (``1.…``, ``02.…``) — các hạng mục
kiểm định — có thể lồng thêm một cấp trùng tên trạm, kèm thư mục ``Data…``.
"""
from __future__ import annotations

import re
from pathlib import Path

from infrastructure.filesystem import ListDirTool, longpath

list_dir = ListDirTool()

_NUMBERED = re.compile(r"^\s*(\d+)\s*([.\-_ ]|$)")


def _has_numbered_child(d: Path) -> bool:
    try:
        return any(p.is_dir() and _NUMBERED.match(p.name) for p in list_dir(d))
    except OSError:
        return False


def image_root(station: Path) -> Path:
    """Thư mục chứa trực tiếp các hạng mục đánh số — chính ``station``, hoặc một cấp
    lồng bên trong (một số bản export lồng trùng tên trạm)."""
    if _has_numbered_child(station):
        return station
    nested = station / station.name
    if nested.is_dir() and _has_numbered_child(nested):
        return nested
    for p in list_dir(station):
        if p.is_dir() and _has_numbered_child(p):
            return p
    return station


def hang_muc_dirs(root: Path) -> dict[int, str]:
    """``{2: '02.Khe hở', 3: '3.Công tác…'}`` — tên thư mục THỰC TẾ theo số hạng mục."""
    out: dict[int, str] = {}
    for p in list_dir(root):
        m = _NUMBERED.match(p.name)
        if p.is_dir() and m:
            out[int(m[1])] = p.name
    return out


def is_broken_image(path: Path) -> bool:
    """0 byte hoặc PIL không mở/verify được → bỏ qua ảnh này."""
    try:
        lp = longpath(path)
        if lp.stat().st_size == 0:
            return True
        from PIL import Image

        with Image.open(lp) as im:
            im.verify()
        return False
    except Exception:  # noqa: BLE001
        return True
