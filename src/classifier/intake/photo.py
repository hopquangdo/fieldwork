"""Ảnh đầu vào — 1 dạng chung cho mọi nguồn."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Photo:
    id: str                                   # đường dẫn tương đối trong nguồn ("/" ngăn cách)
    path: Path                                # đường dẫn tuyệt đối
    sha1: str = ""
    order: int = 0                            # thứ tự trong nguồn (tên Zalo = mốc gửi ≈ thứ tự chụp)
    prefix: str = ""                          # nội dung trong tên file ("móng m1"…), "" nếu vô nghĩa
    folder: str = ""                          # thư mục đang chứa (cây trạm) — "" với nguồn phẳng
    taken_at: tuple[int, int, int] | None = None   # giờ chụp (tên file / EXIF / chữ in trên ảnh)
    description: str = ""                     # vision tả ảnh (cho báo cáo)

    @property
    def name(self) -> str:
        return self.path.name


@dataclass
class Batch:
    """Kết quả intake của 1 trạm."""
    station: str
    root: Path
    photos: list[Photo]
    extras: list[Path] = field(default_factory=list)        # file không phải ảnh (PDF bản vẽ…)
    duplicates: list[tuple[str, str]] = field(default_factory=list)   # (bản bỏ, bản giữ)
    broken: list[str] = field(default_factory=list)
    flat: bool = True
