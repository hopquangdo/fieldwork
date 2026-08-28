r"""Windows MAX_PATH survival: prefix absolute paths with \\?\ before touching the FS.

Real BTS stations nest Vietnamese folder names 6 levels deep and blow past 260
chars, so plain ``Path.iterdir`` / ``rglob`` silently stop mid-tree.
"""
from __future__ import annotations

import os
from pathlib import Path

_PREFIX = "\\\\?\\"


def longpath(p: str | os.PathLike) -> Path:
    r"""Absolute path safe for deep trees (adds \\?\ on Windows)."""
    q = Path(p).resolve()
    if os.name == "nt" and not str(q).startswith(_PREFIX):
        return Path(_PREFIX + str(q))
    return q


def strip(p: str | os.PathLike) -> str:
    s = str(p)
    return s[len(_PREFIX):] if s.startswith(_PREFIX) else s
