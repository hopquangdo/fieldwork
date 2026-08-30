"""Parse BTS image filenames: ``<prefix>@ h@ m@ s@ --x--.jpg``."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Component:
    prefix: str          # casefolded, whitespace-collapsed; "" when timestamp-only
    is_primary: bool
    ts: tuple[int, int, int]


_TS = re.compile(r"@\s*(\d{1,2})\s*@\s*(\d{1,2})\s*@\s*(\d{1,2})")
_MONG = re.compile(r"\bm[oó]ng\s*(m?\d+)\b", re.I)
_DOT = re.compile(r"\b[đd][oố]t\s*d?\s*(\d+)\b", re.I)
_TANG = re.compile(r"\bt[aầ]ng\s*d[aâ]y\s*(?:co\s*)?(\d+)\b", re.I)


def parse(filename: str) -> Component:
    stem = Path(filename).name
    head, sep, _ = stem.partition("@")
    prefix = re.sub(r"\s+", " ", head).strip().casefold() if sep else ""
    m = _TS.search(stem)
    ts = (int(m[1]), int(m[2]), int(m[3])) if m else (0, 0, 0)
    return Component(prefix=prefix, is_primary="--1--" in stem, ts=ts)


_LAN = re.compile(r"\bl[aầ]n\s*(?:đo\s*)?(\d+)\b", re.I)


def group_key(prefix: str, kind: str) -> str | None:
    if kind == "mong":
        m = _MONG.search(prefix)
        return f"M{m[1].lstrip('mM')}" if m else None
    if kind == "dot":
        m = _DOT.search(prefix)
        return f"D{m[1]}" if m else None
    if kind == "tang":
        m = _TANG.search(prefix)
        return f"Tầng dây {m[1]}" if m else None
    if kind == "lan":
        m = _LAN.search(prefix)
        return f"Lần {m[1]}" if m else None
    if kind == "vitri":            # Mục 6 / 7 / 8 — vị trí / điểm đo trên cột
        mv = re.search(r"\bv[oò]ng\s*(\d+\s*[-–]\s*\d+)", prefix)
        if mv:
            return "vòng " + re.sub(r"\s+", "", mv[1]).replace("–", "-")
        for kw, name in (
            ("chân cột", "chân cột"), ("chan cot", "chân cột"), ("chân đế", "chân cột"),
            ("kim thu", "kim thu sét"), ("thu sét", "kim thu sét"), ("thu set", "kim thu sét"),
            ("kim chống sét", "kim thu sét"), ("kim chong set", "kim thu sét"),
            ("giữa cột", "giữa cột"), ("giua cot", "giữa cột"),
            ("đỉnh cột", "đỉnh cột"), ("dinh cot", "đỉnh cột"), ("đỉnh trụ", "đỉnh cột"),
            ("toạ độ vòng", "toạ độ vòng"), ("tọa độ vòng", "toạ độ vòng"), ("toa do vong", "toạ độ vòng"),
            ("thiết bị", "thiết bị treo trên cột"), ("thiet bi", "thiết bị treo trên cột"),
        ):
            if kw in prefix:
                return name
        return None
    return None


def looks_like_blueprint(prefix: str) -> bool:
    return bool(re.search(r"\bm[oó]ng\s*m0\b|b[aả]n\s*v[eẽ]|drawing", prefix, re.I))
