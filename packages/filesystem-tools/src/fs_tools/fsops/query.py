"""Read-only filesystem inspection — MAX_PATH-safe."""
from __future__ import annotations

import os
from pathlib import Path

from fs_tools.winpath import raw


def exists(p: Path) -> bool:
    return os.path.exists(raw(p))


def is_empty_dir(p: Path) -> bool:
    lp = raw(p)
    return os.path.isdir(lp) and not os.listdir(lp)
