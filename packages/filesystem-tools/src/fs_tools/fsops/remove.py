"""Directory removal — MAX_PATH-safe."""
from __future__ import annotations

import os
from pathlib import Path

from fs_tools.fsops.query import is_empty_dir
from fs_tools.winpath import raw


def rmdir_if_empty(p: Path) -> bool:
    if is_empty_dir(p):
        os.rmdir(raw(p))
        return True
    return False


def rmtree(target: Path) -> None:
    lt = raw(target)
    if not os.path.exists(lt):
        return
    for root, dirs, files in os.walk(lt, topdown=False):
        for f in files:
            os.remove(os.path.join(root, f))
        for d in dirs:
            os.rmdir(os.path.join(root, d))
    os.rmdir(lt)
