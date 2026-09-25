"""``Issue`` (một vi phạm SOP) + các nhóm loại issue mà mỗi fixer chịu trách nhiệm.

Module trung lập (không phụ thuộc ``steps`` / ``domain``) để mọi bên dùng chung mà
không tạo vòng import.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Issue:
    hm: str          # hạng mục (hoặc "(ảnh)" cho vấn đề mức ảnh)
    kind: str        # xem các *_KINDS bên dưới
    detail: str
    folder: str = ""


# fixer  ->  các kind nó xử lý
CLASSIFY_KINDS = ("unclassified", "misplaced")
SCAFFOLD_KINDS = ("too_few", "odd_folders", "missing_khac")
EVEN_KINDS = ("odd_images", "too_many")
DOT_RANGE_KINDS = ("dot_range",)
