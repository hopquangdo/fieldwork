"""Confine a path to a single sandbox root."""
from __future__ import annotations

from pathlib import Path


class SandboxError(ValueError):
    pass


def within(root: Path, target: str) -> Path:
    """Resolve ``target`` (relative to ``root``) and reject anything that escapes it."""
    root = Path(root).resolve()
    p = Path(target)
    p = (p if p.is_absolute() else root / p).resolve()
    if p != root and root not in p.parents:
        raise SandboxError(f"path escapes sandbox root: {target}")
    return p
