"""Directory creation — MAX_PATH-safe."""
from __future__ import annotations

import os
from pathlib import Path

from fs_tools.winpath import raw


def makedirs(p: Path) -> None:
    os.makedirs(raw(p), exist_ok=True)
