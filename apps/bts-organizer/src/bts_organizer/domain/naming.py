"""Parse BTS image filenames: ``<prefix>@ h@ m@ s@ --x--.jpg``."""
from __future__ import annotations

import re
from pathlib import Path

from bts_organizer.domain.models import Component

_TS = re.compile(r"@\s*(\d{1,2})\s*@\s*(\d{1,2})\s*@\s*(\d{1,2})")


def parse(filename: str) -> Component | None:
    """Return a Component, or None when the name carries no component (timestamp only)."""
    stem = Path(filename).name
    head, sep, _ = stem.partition("@")
    prefix = normalize(head)
    if not sep or not prefix:
        return None
    m = _TS.search(stem)
    ts = (int(m[1]), int(m[2]), int(m[3])) if m else (0, 0, 0)
    return Component(prefix=prefix, is_primary="--1--" in stem, ts=ts)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


_MONG = re.compile(r"\bm[oó]ng\s*(m?\d+)\b", re.I)
_DOT = re.compile(r"\b[đd][oố]t\s*d?\s*(\d+)\b", re.I)
_TANG = re.compile(r"\bt[aầ]ng\s*d[aâ]y\s*(\d+)\b", re.I)


def mong_key(prefix: str) -> str | None:
    m = _MONG.search(prefix)
    return f"M{m[1].lstrip('mM')}" if m else None


def dot_key(prefix: str) -> int | None:
    m = _DOT.search(prefix)
    return int(m[1]) if m else None


def tang_key(prefix: str) -> int | None:
    m = _TANG.search(prefix)
    return int(m[1]) if m else None


def looks_like_blueprint_name(prefix: str) -> bool:
    """Weak signal only — must be visually confirmed."""
    return bool(re.search(r"\bm[oó]ng\s*m0\b|b[aả]n\s*v[eẽ]|drawing", prefix, re.I))
