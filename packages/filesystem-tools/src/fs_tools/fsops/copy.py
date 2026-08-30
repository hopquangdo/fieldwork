"""Copy files/trees — MAX_PATH-safe, never overwrites."""
from __future__ import annotations

import os
import shutil
from pathlib import Path

from fs_tools.fsops.mkdir import makedirs
from fs_tools.fsops.naming import free_name
from fs_tools.fsops.query import exists
from fs_tools.winpath import raw


def copytree(src: Path, dst: Path) -> int:
    """Recursive copy, preserving mtime (copy2). MAX_PATH-safe."""
    n = 0
    lsrc = raw(src)
    for root, _, files in os.walk(lsrc):
        rel = root[len(lsrc):].strip("\\/")
        out = os.path.join(str(dst), rel) if rel else str(dst)
        os.makedirs(raw(out), exist_ok=True)
        for f in files:
            shutil.copy2(os.path.join(root, f), raw(os.path.join(out, f)))
            n += 1
    return n


def safe_copy(src: Path, dest_dir: Path, *, rename: str | None = None) -> Path:
    """Copy src into dest_dir without ever overwriting. Returns the final path."""
    src = Path(src)
    if not exists(src):
        raise FileNotFoundError(str(src))
    makedirs(dest_dir)
    dest = free_name(Path(dest_dir), rename or src.name)
    shutil.copy2(raw(src), raw(dest))
    return dest
