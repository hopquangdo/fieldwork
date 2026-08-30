"""Read station numbers from the Data folder's TABLE*.txt (SOP §1)."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from fs_tools import longpath, walk_files

_FIELDS = {
    "n_dot": re.compile(r"s[ốô]\s*đ[ốô]t\D*(\d+)", re.I),
    "n_mong": re.compile(r"s[ốô]\s*m[óo]ng(?:\s*co)?\D*(\d+)", re.I),
    "n_tang": re.compile(r"s[ốô]\s*t[ầa]ng\s*d[âa]y(?:\s*co)?\D*(\d+)", re.I),
}


@dataclass
class StationMeta:
    tower_type: str = "day_co"          # day_co | tu_dung | monopole
    n_dot: int = 0
    n_mong: int = 0
    n_tang: int = 0
    source: str = ""
    warnings: list[str] = field(default_factory=list)


def _tower_type(text: str) -> str:
    low = text.casefold()
    if "monopole" in low:
        return "monopole"
    if "tự đứng" in low or "tu dung" in low:
        return "tu_dung"
    if "dây co" in low or "day co" in low:
        return "day_co"
    return ""


def find_table_bia(root: Path) -> Path | None:
    for p in walk_files(root):
        if p.suffix.lower() == ".txt" and p.name.casefold().startswith("tablebia"):
            return p
    return None


def read_meta(root: Path) -> StationMeta:
    """`root` = the station folder (contains the Data... subfolder)."""
    meta = StationMeta()
    bia = find_table_bia(root)
    if bia is None:
        meta.warnings.append("Không thấy TABLEBia.txt — giả định cột dây co.")
        return meta

    text = longpath(bia).read_text(encoding="utf-8", errors="replace")
    meta.source = bia.name
    tt = _tower_type(text)
    if tt:
        meta.tower_type = tt
    else:
        meta.warnings.append("TABLEBia.txt không ghi rõ loại cột — giả định dây co.")
    for attr, rx in _FIELDS.items():
        m = rx.search(text)
        if m:
            setattr(meta, attr, int(m[1]))
    return meta


def peek_tower_type(root: Path) -> str:
    """Cheap read used before config is loaded, to pick the right rules file."""
    bia = find_table_bia(root)
    if bia is None:
        return ""
    try:
        return _tower_type(longpath(bia).read_text(encoding="utf-8", errors="replace"))
    except OSError:
        return ""
