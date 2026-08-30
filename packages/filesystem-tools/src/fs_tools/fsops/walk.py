"""Directory traversal that survives Windows MAX_PATH. Paths yielded have the prefix stripped."""
from __future__ import annotations

import os
from pathlib import Path

from fs_tools.exts import IMAGE_EXTS
from fs_tools.winpath import raw, strip


def walk_files(root: Path, *, images_only: bool = False):
    lroot = raw(root)
    for r, _, files in os.walk(lroot):
        for f in files:
            if images_only and Path(f).suffix.lower() not in IMAGE_EXTS:
                continue
            yield Path(strip(os.path.join(r, f)))


def walk_dirs(root: Path):
    lroot = raw(root)
    for r, dirs, _ in os.walk(lroot):
        for d in dirs:
            yield Path(strip(os.path.join(r, d)))


def list_dir(path: Path):
    """Immediate children (files + dirs), prefix stripped."""
    for name in sorted(os.listdir(raw(path))):
        yield Path(path) / name
