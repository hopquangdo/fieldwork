"""Locate the image root + Data folder of a station, and enumerate stations in a workspace."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from fs_tools import IMAGE_EXTS

from bts_organizer.winpath import longpath, strip

_NUM_DIR = re.compile(r"^\s*(\d+)\s*[.\-_ ]")
_STATION = re.compile(r"^[A-Z]{2,4}\d{3,6}[_ ]", re.I)


@dataclass
class StationPaths:
    root: Path
    image_root: Path
    data_dir: Path | None


def locate(station_root: str | Path) -> StationPaths:
    root = Path(strip(longpath(station_root)))
    image_root = _find_image_root(root)
    data_dir = next(
        (
            Path(strip(d))
            for d in sorted(longpath(root).rglob("Data*"), key=lambda p: (not p.name.casefold().endswith("ok"), len(str(p))))
            if d.is_dir()
        ),
        None,
    )
    return StationPaths(root, image_root, data_dir)


def _find_image_root(root: Path) -> Path:
    if _has_numbered_dirs(root):
        return root
    same = root / root.name
    if same.is_dir() and _has_numbered_dirs(same):
        return same
    for d in sorted(p for p in longpath(root).iterdir() if p.is_dir()):
        if _has_numbered_dirs(Path(strip(d))):
            return Path(strip(d))
    return root


def _has_numbered_dirs(d: Path) -> bool:
    try:
        return any(p.is_dir() and _NUM_DIR.match(p.name) for p in longpath(d).iterdir())
    except OSError:
        return False


def find_stations(workspace: str | Path) -> list[Path]:
    ws = longpath(workspace)
    out: list[Path] = []
    for d in sorted(p for p in ws.iterdir() if p.is_dir()):
        real = Path(strip(d))
        if _STATION.match(real.name) or _has_numbered_dirs(real) or _has_numbered_dirs(real / real.name):
            out.append(real)
    return out


def count_images(d: Path) -> int:
    return sum(1 for p in longpath(d).rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTS)
