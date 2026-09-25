"""Gộp/đặt tên các thư mục per-đốt (SOP §2 Mục 2) — dùng bởi ``steps/dot_range.py``.

``mode``:
* ``"all"`` (MẶC ĐỊNH) — mỗi đốt 1 thư mục: ``…Dn`` → ``target_fmt`` với ``{a}=n``
  (``target_fmt = "…đốt {a}"``). Không đẩy ảnh sang 'khác'.
* ``"extremes"`` — gộp về đúng 2 thư mục cực trị ``…đốt {lo}-{lo+1}`` + ``…đốt {hi-1}-{hi}``
  (cần ``target_fmt = "…đốt {a}-{b}"``); đốt ở giữa → thư mục 'khác'.
"""
from __future__ import annotations

import re

from domain.folders import hm_of, leaf_of

_D = re.compile(r"\bD(\d+)\s*$")


class DotGrouper:
    """Bọc 1 :class:`~core.profile.Names` — thao tác thuần trên ``assign``."""

    def __init__(self, names) -> None:
        self._nm = names

    def per_dot(self, assign: dict, hm_prefix: str) -> dict[int, str]:
        """Số đốt của các thư mục công-tác per-đốt (…D1, …D2) dưới ``hm_prefix``."""
        out: dict[int, str] = {}
        for k in assign:
            if not k.startswith(hm_prefix) or self._nm.is_khac(leaf_of(k)):
                continue
            m = _D.search(leaf_of(k))
            if m:
                out[int(m[1])] = k
        return out

    def apply(self, assign: dict, spec: dict) -> set[str] | None:
        """Áp 1 khai báo ``[[dot_range]]`` lên ``assign``. ``None`` nếu <2 thư mục
        per-đốt (chưa cần gộp). Trả về set thư mục được giữ."""
        hm_prefix = spec["hm_prefix"]
        fmt = spec["target_fmt"]
        per_dot = self.per_dot(assign, hm_prefix)
        if len(per_dot) < 2:
            return None

        dots = sorted(per_dot)
        lo, hi = dots[0], dots[-1]
        hm = hm_of(per_dot[lo])
        khac = spec.get("khac") or self._nm.khac_folder(assign, hm)

        if spec.get("mode", "all") == "extremes":
            keep = self._apply_extremes(assign, per_dot, fmt, lo, hi, khac)
        else:
            keep = self._apply_all(assign, per_dot, fmt)

        self._sweep_leftovers(assign, hm_prefix, keep, khac)
        return keep

    def _apply_extremes(self, assign, per_dot, fmt, lo, hi, khac) -> set[str]:
        lo_folder = fmt.format(a=lo, b=lo + 1)
        hi_folder = fmt.format(a=hi - 1, b=hi)
        for d, key in per_dot.items():
            imgs = assign.pop(key)
            if d <= lo + 1:
                assign.setdefault(lo_folder, []).extend(imgs)
            elif d >= hi - 1:
                assign.setdefault(hi_folder, []).extend(imgs)
            else:
                assign.setdefault(khac, []).extend(imgs)
        return {lo_folder, hi_folder}

    def _apply_all(self, assign, per_dot, fmt) -> set[str]:
        keep: set[str] = set()
        for d, key in per_dot.items():
            imgs = assign.pop(key)
            folder = fmt.format(a=d, b=d + 1)   # {b} bỏ qua nếu fmt chỉ có {a}
            keep.add(folder)
            assign.setdefault(folder, []).extend(imgs)
        return keep

    def _sweep_leftovers(self, assign: dict, hm_prefix: str, keep: set[str], khac: str) -> None:
        """Dọn thư mục phụ lục KHÔNG phải per-đốt còn sót (thư mục mẫu cũ kiểu
        "chuẩn bị"/"kiểm tra giữa" — bị per-đốt thay thế hoàn toàn): ảnh (nếu có)
        dồn sang 'khác', xoá thư mục."""
        for k in [k for k in list(assign)
                  if k.startswith(hm_prefix) and self._nm.is_appendix(leaf_of(k)) and k not in keep]:
            leftover = assign.pop(k)
            if leftover:
                assign.setdefault(khac, []).extend(leftover)
