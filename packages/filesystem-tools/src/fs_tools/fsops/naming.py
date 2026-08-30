"""Collision-free destination naming."""
from __future__ import annotations

import os
from pathlib import Path

from fs_tools.winpath import raw


def free_name(dest_dir: Path, name: str) -> Path:
    """A path in dest_dir that does not exist yet ('name (1).ext', ...)."""
    stem, suffix = Path(name).stem, Path(name).suffix
    cand = dest_dir / name
    n = 1
    while os.path.exists(raw(cand)):
        cand = dest_dir / f"{stem} ({n}){suffix}"
        n += 1
    return cand
