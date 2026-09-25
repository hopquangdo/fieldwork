"""Ghép cặp "chuẩn bị X / đo X" cho cấu kiện CHỈ 1 ẢNH (SOP §2.4) — dùng bởi
``steps/scaffold.py``. Chỉ áp dụng cho thư mục đặt tên theo ``[folders] pair_names``
("Công tác chuẩn bị X" / "Công tác đo X"); thư mục nhóm khác (Thao tác tại…, Đo kích
thước…) giữ nguyên, không đụng. ``allowed`` (từ ``[[subfolders]]``) chặn việc dựng thư
mục cặp KHÔNG có trong danh sách tên chuẩn của hạng mục.
"""
from __future__ import annotations

from domain.folders import leaf_of


class SingletonPairer:
    def __init__(self, names, allowed=lambda hm, leaf: True) -> None:
        self._nm = names
        self._allowed = allowed          # (hm, leaf) → tên thư mục cặp có hợp lệ (tên chuẩn) không

    def pair_all(self, assign: dict, hm: str, keys: list[str]) -> int:
        """Với mỗi thư mục phụ lục 1 ảnh chưa ghép cặp hợp lệ: tạo thư mục cặp rỗng
        (ảnh giữ nguyên ở thư mục cũ). Trả về số thư mục đã tạo."""
        created = 0
        singles = [k for k in keys if self._nm.is_appendix(leaf_of(k)) and len(assign.get(k, [])) == 1]
        for k in singles:
            sibling = self._sibling_of(hm, k)
            if sibling is None or sibling in assign or not self._allowed(hm, leaf_of(sibling)):
                continue
            assign.setdefault(sibling, [])
            created += 1
        return created

    def _sibling_of(self, hm: str, folder: str) -> str | None:
        sib = self._nm.sibling_leaf(leaf_of(folder))
        return f"{hm}/{sib}" if sib else None
