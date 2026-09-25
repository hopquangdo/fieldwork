"""Hai kiểu dữ liệu bất biến đi xuyên pipeline: ``Photo`` (một ảnh đã kiểm kê) và
``Move`` (một thao tác di chuyển đã lên kế hoạch)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Photo:
    path: str            # tương đối so với thư mục ảnh của trạm, dấu '/'
    prefix: str           # phần cấu kiện trong tên ("" nếu tên chỉ có giờ chụp)
    is_primary: bool      # ảnh chính (--1--)

    @property
    def name(self) -> str:
        return self.path.rsplit("/", 1)[-1]

    @property
    def folder(self) -> str:
        return self.path.rsplit("/", 1)[0] if "/" in self.path else ""


@dataclass(frozen=True)
class Move:
    src: str                     # tương đối so với thư mục ảnh của trạm
    dest_dir: str                # thư mục đích, tương đối
    new_name: str | None = None  # đổi tên khi di chuyển (theo quy ước profile)
    convert: bool = False        # re-encode sang JPEG thật (vd .png → .jpg)
