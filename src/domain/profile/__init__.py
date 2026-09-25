"""SOP profile — toàn bộ tri thức "phụ lục trông thế nào" của một chuẩn kiểm định.

``src/`` không chứa dữ liệu SOP nào: mọi chuỗi / regex / tên hạng mục đến
từ ``rules/<tên>.toml`` (profile cụ thể ``extends = "_base"``). Thiếu field →
:class:`ProfileError`, không có giá trị mặc định ẩn. Bảng field: ``docs/PROFILE_SCHEMA.md``.
"""
from domain.profile.names import Names
from domain.profile.profile import Profile
from domain.profile.spec import (
    Filename,
    Folders,
    Metadata,
    ProfileError,
    Structure,
)

__all__ = ["Profile", "ProfileError", "Names", "Structure", "Folders", "Filename", "Metadata"]
