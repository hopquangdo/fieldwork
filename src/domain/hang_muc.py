"""Khớp tên hạng mục (đã bỏ số thứ tự) với danh mục chuẩn ``profile.hang_muc`` của
một loại cột — dùng bởi ``steps/normalize.py`` để chuẩn hoá input đánh số theo loại
cột khác (vd input 10 hạng mục dây co, chạy profile tự đứng 8 hạng mục).
"""
from __future__ import annotations

import re

_STOP = {"công", "tác", "hình", "ảnh", "của", "và", "cho"}
_WORD = re.compile(r"[^\W\d_]+", re.UNICODE)
_MIN_SCORE = 0.55  # tỉ lệ token trùng / token tên hạng mục chuẩn, tối thiểu để nhận


class HangMucMatcher:
    """Khớp theo ``hang_muc_alias`` (từ khoá → số hoặc ``"drop"``) trước, rồi
    token-overlap với ``hang_muc``."""

    def __init__(self, hang_muc: dict[int, str], alias: dict[str, str]) -> None:
        self._hang_muc = hang_muc
        self._alias = alias

    @staticmethod
    def _tokens(name: str) -> set[str]:
        return {w for w in _WORD.findall(name.casefold()) if w not in _STOP}

    def match(self, name: str) -> tuple[int | None, bool]:
        """→ ``(số hạng mục chuẩn hoặc None nếu không chắc, is_drop)``."""
        low = name.casefold()
        for kw, target in self._alias.items():
            if kw in low:
                return (None, True) if target == "drop" else (int(target), False)
        toks = self._tokens(name)
        best, best_score = None, 0.0
        for num, cname in self._hang_muc.items():
            cts = self._tokens(cname)
            if not cts:
                continue
            score = len(toks & cts) / len(cts)
            if score > best_score:
                best, best_score = num, score
        return (best, False) if best_score >= _MIN_SCORE else (None, False)
