"""Helper THUẦN cho cây thư mục phụ lục và bảng ``assign`` (``{thư mục: [ảnh]}``).

Chỉ thao tác chuỗi / dict — không I/O, không ``ctx``, không tri thức SOP (cái đó ở
:class:`domain.profile.Names`).
"""
from __future__ import annotations

from collections.abc import Iterable


def leaf_of(folder: str) -> str:
    """Tên thư mục cuối: ``"3.X/Công tác đo Y"`` → ``"Công tác đo Y"``."""
    return folder.rsplit("/", 1)[-1]


def hm_of(folder: str) -> str:
    """Thư mục hạng mục (cấp 1): ``"3.X/Công tác đo Y"`` → ``"3.X"``."""
    return folder.split("/", 1)[0]


def reverse_assign(assign: dict[str, list[str]]) -> dict[str, str]:
    """``{ảnh: thư mục đang chứa}`` — mỗi ảnh xuất hiện đúng 1 lần trong ``assign``."""
    return {photo: folder for folder, photos in assign.items() for photo in photos}


def existing_dir(existing: Iterable[str], hm: str, predicate) -> str | None:
    """Thư mục con (1 cấp) đã có trên đĩa dưới ``hm`` mà ``predicate(leaf)`` đúng."""
    for d in sorted(existing):
        if hm_of(d) == hm and d.count("/") == 1 and predicate(leaf_of(d)):
            return d
    return None
