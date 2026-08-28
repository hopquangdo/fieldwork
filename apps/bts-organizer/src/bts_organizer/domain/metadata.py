"""Read station numbers from the ``Data...`` folder's TABLE*.txt files."""
from __future__ import annotations

import re
from pathlib import Path

from bts_organizer.domain.models import StationMeta

_FIELDS = {
    "n_dot": re.compile(r"s[oố]\s*[đd][oố]t\D*(\d+)", re.I),
    "n_mong": re.compile(r"s[oố]\s*m[oó]ng(?:\s*co)?\D*(\d+)", re.I),
    "n_tang": re.compile(r"s[oố]\s*t[aầ]ng\s*d[aâ]y(?:\s*co)?\D*(\d+)", re.I),
}


def read_meta(data_dir: Path | None) -> StationMeta:
    meta = StationMeta()
    bia = _find_table_bia(data_dir) if data_dir else None
    if bia is None:
        meta.warnings.append("Không thấy TABLEBia.txt — suy loại cột từ tên/ảnh.")
        return meta

    text = bia.read_text(encoding="utf-8", errors="replace")
    meta.source = bia.name
    low = text.casefold()
    if "tự đứng" in low or "tu dung" in low:
        meta.tower_type = "tu_dung"
    elif "monopole" in low:
        meta.tower_type = "monopole"
    else:
        meta.tower_type = "day_co"

    for attr, rx in _FIELDS.items():
        m = rx.search(text)
        if m:
            setattr(meta, attr, int(m[1]))
    return meta


def _find_table_bia(data_dir: Path) -> Path | None:
    if not data_dir.is_dir():
        return None
    for p in data_dir.rglob("*.txt"):
        if p.name.casefold().startswith("tablebia"):
            return p
    return None
