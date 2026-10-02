"""Cây trạm có sẵn hạng mục đánh số: thư mục đang chứa ảnh được giữ làm bằng chứng
(``Photo.folder``) cho ``evidence.filename``."""
from __future__ import annotations

from pathlib import Path

from domain.station import hang_muc_dirs, image_root

from classifier.intake.dedupe import dedupe
from classifier.intake.photo import Batch
from classifier.intake.sources._common import is_image, make_photo


def detect(root: Path) -> bool:
    return bool(hang_muc_dirs(image_root(root)))


def read(root: Path, prof) -> Batch:
    img_root = image_root(root)
    photos, broken = [], []
    for p in sorted(img_root.rglob("*"), key=lambda p: p.as_posix()):
        if not (p.is_file() and is_image(p)):
            continue
        folder = p.parent.relative_to(img_root).as_posix()
        ph = make_photo(p, img_root, len(photos), prof, "" if folder == "." else folder)
        if ph is None:
            broken.append(p.relative_to(img_root).as_posix())
        else:
            photos.append(ph)
    photos, dups = dedupe(photos)
    return Batch(root.name, img_root, photos, [], dups, broken, flat=False)
