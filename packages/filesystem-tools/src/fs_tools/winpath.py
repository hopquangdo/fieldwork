r"""Windows MAX_PATH survival. Prefix absolute paths with \\?\ before touching the FS —
plain ``Path.iterdir`` / ``rglob`` silently stop mid-tree past 260 chars."""
from __future__ import annotations

import os
from pathlib import Path

PREFIX = "\\\\?\\"


def longpath(p: str | os.PathLike) -> Path:
    q = Path(p).resolve()
    if os.name == "nt" and not str(q).startswith(PREFIX):
        return Path(PREFIX + str(q))
    return q


def raw(p: str | os.PathLike) -> str:
    """String form suitable for os.* calls (adds the prefix, resolves)."""
    s = str(p)
    return PREFIX + os.path.abspath(s) if os.name == "nt" and not s.startswith(PREFIX) else s


def strip(p: str | os.PathLike) -> str:
    s = str(p)
    return s[len(PREFIX):] if s.startswith(PREFIX) else s
