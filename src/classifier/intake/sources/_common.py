"""Phần dùng chung của các nguồn: lọc ảnh lỗi, tách prefix/giờ từ tên file."""
from __future__ import annotations

from pathlib import Path

from domain.naming import parse
from domain.station import is_broken_image
from infrastructure.filesystem import IMAGE_EXTS

from classifier.intake.photo import Photo


def is_image(p: Path) -> bool:
    return p.suffix.lower() in IMAGE_EXTS


def make_photo(p: Path, root: Path, order: int, prof, folder: str = "") -> Photo | None:
    if is_broken_image(p):
        return None
    fn = prof.filename
    c = parse(p.name, ts_pattern=fn.ts_pattern, primary_marker=fn.primary_marker)
    return Photo(id=p.relative_to(root).as_posix(), path=p, order=order, prefix=c.prefix,
                 folder=folder, taken_at=c.ts if c.ts != (0, 0, 0) else None)
