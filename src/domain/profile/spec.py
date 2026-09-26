"""Các dataclass mô tả 1 profile SOP — KHÔNG có giá trị mặc định (0 fallback trong code).
Giá trị đến từ ``rules/*.toml``; thiếu field → :class:`ProfileError`.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class ProfileError(ValueError):
    """Profile TOML thiếu field bắt buộc / sai kiểu."""


def need(d: dict, key: str, where: str) -> Any:
    if key not in d:
        raise ProfileError(f"[{where}] thiếu '{key}'")
    return d[key]


def strs(v: Any, where: str) -> tuple[str, ...]:
    if not isinstance(v, (list, tuple)):
        raise ProfileError(f"[{where}] cần list, gặp {type(v).__name__}")
    return tuple(str(x) for x in v)


@dataclass(frozen=True)
class Structure:
    """"Phụ lục đạt chuẩn" nghĩa là gì — ``[structure]``."""
    min_cong_tac: int
    pair_folders: bool          # số thư mục 'Công tác' phải CHẴN
    require_khac: bool
    even_images: bool           # mỗi thư mục công tác: số ảnh CHẴN
    prefer_images: int
    trim_to_prefer: bool        # true → cắt thư mục về prefer_images; false (mặc định) → giữ FULL, chỉ ép chẵn
    even_no_trim: tuple[str, ...]
    keep_as_is: tuple[str, ...]
    even_skip: tuple[str, ...]
    keep_singletons: bool = False   # thư mục phụ lục CHỈ 1 ảnh: giữ nguyên, không đẩy sang 'khác' (SOP TH3)
    odd_fix: str = "split"          # số thư mục lẻ: "split" (chia đôi thư mục đông nhất) · "sibling" (thêm thư mục cặp RỖNG cho thư mục cuối)
    trim_earliest: tuple[str, ...] = ()
    odd_folders_skip: tuple[str, ...] = ()   # hạng mục chứa chuỗi này: KHÔNG ép số thư mục phụ lục chẵn   # hạng mục chứa chuỗi này: ép chẵn bỏ ảnh SỚM nhất (mặc định bỏ ảnh MUỘN nhất)


@dataclass(frozen=True)
class Folders:
    """Nhận diện loại thư mục theo tên — ``[folders]``."""
    hm_prefix: str              # regex bóc 'N.' đầu tên hạng mục
    cong_tac_markers: tuple[str, ...]
    khac_markers: tuple[str, ...]
    appendix_markers: tuple[str, ...]
    strip_prefixes: tuple[str, ...]
    khac_name: str
    pair_names: tuple[str, str]     # tiền tố 2 thư mục 1 cặp (vd "Công tác chuẩn bị ", "Công tác đo ")


@dataclass(frozen=True)
class Filename:
    """Quy ước tên file phụ lục — ``[filename]``."""
    conform: str                # regex: tên đã đúng chưa
    build: str                  # format dựng tên
    ts_pattern: str             # regex trích giờ chụp trong tên
    ts_fallback: str            # regex trích giờ dự phòng (từ stem)
    primary_marker: str         # chuỗi đánh dấu ảnh chính
    primary_yes: str
    primary_no: str
    ext: str


@dataclass(frozen=True)
class Metadata:
    """Đọc TABLEBia*.txt — ``[metadata]``."""
    table_glob: str
    tower_type: dict[str, tuple[str, ...]]
    default_tower_type: str       # loại cột giả định khi TABLEBia không có / không ghi rõ
    fields: dict[str, str]
