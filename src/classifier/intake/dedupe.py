"""Gộp ảnh trùng NỘI DUNG (sha1) — giữ bản đầu tiên theo thứ tự nguồn."""
from __future__ import annotations

import hashlib

from infrastructure.filesystem import longpath

from classifier.intake.photo import Photo


def dedupe(photos: list[Photo]) -> tuple[list[Photo], list[tuple[str, str]]]:
    seen: dict[str, str] = {}
    keep: list[Photo] = []
    dups: list[tuple[str, str]] = []
    for p in photos:
        p.sha1 = hashlib.sha1(longpath(p.path).read_bytes()).hexdigest()
        if p.sha1 in seen:
            dups.append((p.id, seen[p.sha1]))
            continue
        seen[p.sha1] = p.id
        keep.append(p)
    for i, p in enumerate(keep):
        p.order = i
    return keep, dups
