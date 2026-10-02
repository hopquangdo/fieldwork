"""Folder PHẲNG: mọi ảnh (đệ quy) là chưa xếp; thứ tự = thứ tự tên file (tên Zalo bắt đầu
bằng mốc thời gian gửi tính bằng ms ≈ thứ tự chụp)."""
from __future__ import annotations

from pathlib import Path

from classifier.intake.dedupe import dedupe
from classifier.intake.photo import Batch
from classifier.intake.sources._common import is_image, make_photo


def read(root: Path, prof) -> Batch:
    files = sorted((p for p in root.rglob("*") if p.is_file()), key=lambda p: p.as_posix())
    photos, broken, extras = [], [], []
    for p in files:
        if not is_image(p):
            extras.append(p)
            continue
        ph = make_photo(p, root, len(photos), prof)
        if ph is None:
            broken.append(p.relative_to(root).as_posix())
        else:
            photos.append(ph)
    photos, dups = dedupe(photos)
    return Batch(root.name, root, photos, extras, dups, broken, flat=True)
