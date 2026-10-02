"""Thông số trạm: TABLEBia nếu có (loại cột, số đốt/móng); không có → loại cột do người
dùng chọn, hoặc ``default_tower_type`` của ``_base``."""
from __future__ import annotations

from pathlib import Path

from domain.metadata import StationMeta, read_meta

from classifier.catalog import load_profile


def station_meta(root: Path, tower_type: str | None = None) -> StationMeta:
    base = load_profile("_base")
    meta = read_meta(root, base.metadata)
    if tower_type:
        if meta.resolved and meta.tower_type != tower_type:
            meta.warnings.append(f"TABLEBia = '{meta.tower_type}' nhưng chọn '{tower_type}'")
        meta.tower_type = tower_type
    return meta
