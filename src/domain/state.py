"""Trạng thái dùng chung giữa các bước của photo-sort — có kiểu, thay cho ``ctx.data["..."]``.

Mỗi lượt chạy có đúng 1 ``SortState``, lấy bằng :func:`state` (tự tạo lần đầu). Gõ sai tên
trường là lỗi ngay khi chạy / IDE báo, không âm thầm trả ``None`` như dict.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from domain.issues import Issue
from domain.metadata import StationMeta
from domain.models import Move, Photo

_KEY = "sort_state"


@dataclass
class SortState:
    # scan / normalize
    root: Path = field(default_factory=Path)              # thư mục ảnh làm việc (bản sao ở output)
    photos: list[Photo] = field(default_factory=list)
    assign: dict[str, list[str]] = field(default_factory=dict)   # thư mục đích → [đường dẫn ảnh]
    hm_dirs: dict[int, str] = field(default_factory=dict)        # số hạng mục → tên thư mục thực
    existing_dirs: set[str] = field(default_factory=set)
    meta: StationMeta | None = None
    # check / classify / validate
    issues: list[Issue] = field(default_factory=list)
    unmatched: list[Photo] = field(default_factory=list)
    # vòng validate ↔ agent_repair
    repair_iters: int = 0
    reviewed: bool = False                                # agent đã rà soát ảnh 'khác' chưa
    # plan
    moves: list[Move] = field(default_factory=list)
    landing: list[tuple[str, str]] = field(default_factory=list)  # (thư mục đích, tên file) của mỗi ảnh


def state(ctx) -> SortState:
    """``SortState`` của lượt chạy (lưu trong ``ctx.data``, tạo lần đầu gọi)."""
    s = ctx.data.get(_KEY)
    if s is None:
        s = ctx.data[_KEY] = SortState()
    return s
