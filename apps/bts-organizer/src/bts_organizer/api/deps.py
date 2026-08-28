from __future__ import annotations

import os
from pathlib import Path

from fastapi import HTTPException


def allowed_roots() -> list[Path]:
    raw = os.getenv("BTS_ALLOWED_ROOTS", "")
    return [Path(p).resolve() for p in raw.split(os.pathsep) if p.strip()]


def assert_allowed(path: str) -> Path:
    p = Path(path).expanduser().resolve()
    roots = allowed_roots()
    if roots and not any(p == r or r in p.parents for r in roots):
        raise HTTPException(403, f"path outside allowed roots: {p}")
    if not p.exists():
        raise HTTPException(404, f"not found: {p}")
    return p
