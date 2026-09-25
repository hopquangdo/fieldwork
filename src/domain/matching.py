"""Rule engine: khớp 1 ảnh với 1 thư mục đích theo các ``[[rule]]`` của profile.

``RuleMatcher`` bọc ``rules`` + ``hm_dirs`` + ``Names`` một lần (từ profile), rồi gọi
``.match(photo, current_folder)`` cho từng ảnh. Rule keys: ``match`` · ``exclude`` ·
``from_folder`` · ``not_from_folder`` · ``group_by`` (tên 1 nhóm ``[groups]`` hoặc list —
thử lần lượt; nhóm ``ordinal`` cần ``totals``) ·
``target`` (``"{keep}"`` = giữ nguyên, ``"{group}"`` = chèn khoá nhóm) ·
``strict_folder`` (xem dưới).
"""
from __future__ import annotations

import re

_NUM = re.compile(r"^\s*(\d+)\s*[.\-_ ]\s*")


def _has(text: str, subs) -> bool:
    return any(s.casefold() in text for s in subs)


def resolve_target(target: str, hm_dirs: dict[int, str]) -> str:
    """Đổi segment đầu ('5.Công tác…') sang tên thư mục hạng mục THỰC TẾ của trạm
    (khi số khác / tên không khớp chính xác)."""
    head, sep, rest = target.partition("/")
    m = _NUM.match(head)
    if not m:
        return target
    real = hm_dirs.get(int(m[1]))
    if not real:
        return target
    return f"{real}/{rest}" if sep else real


class RuleMatcher:
    """Khớp ảnh → thư mục đích theo danh sách ``rules`` của 1 profile.

    ``strict_folder = true`` trên 1 rule: khi tên file trùng quy ước với hạng mục
    KHÁC (vd "Đốt D1" dùng chung cho cả khe hở lẫn trèo cao) mà ``from_folder``
    không xác nhận, rule này BỎ QUA hẳn thay vì góp vào khớp lỏng — tránh "hút"
    nhầm ảnh từ hạng mục khác chỉ vì tên file trùng mẫu.
    """

    def __init__(self, rules: list[dict], hm_dirs: dict[int, str], names,
                 totals: dict[str, int] | None = None) -> None:
        self._rules = rules
        self._hm_dirs = hm_dirs
        self._names = names
        self._totals = totals or {}      # tổng cho nhóm ``ordinal`` (vd n_dot) — xem Names.group_key

    def match(self, photo, current_folder: str | None = None) -> tuple[str | None, bool]:
        """→ ``(target, is_soft)``.

        * rule đầu tiên khớp **và** ``from_folder`` xác nhận → ``(target, False)`` (chắc chắn)
        * chỉ 1 rule khớp ``match`` nhưng ``from_folder`` không khớp → ``(target, True)`` (lỏng)
        * không rule nào → ``(None, False)``

        ``current_folder``: vị trí LOGIC hiện tại của ảnh (sau ``normalize``…) dùng để
        so ``from_folder``/``not_from_folder`` — mặc định ``photo.folder`` (đường dẫn
        vật lý trên đĩa, không đổi dù đã đổi số hạng mục).
        """
        names = self._names
        prefix = photo.prefix
        cur = current_folder if current_folder is not None else photo.folder
        folder = cur.casefold()
        soft: str | None = None

        for rule in self._rules:
            match = rule.get("match")
            if match and not _has(prefix, match):
                continue
            if not match and not prefix and not rule.get("from_folder"):
                continue
            if _has(prefix, rule.get("exclude", [])):
                continue
            if _has(folder, rule.get("not_from_folder", [])):
                continue

            raw_target = rule["target"]
            ff = rule.get("from_folder")
            ff_ok = not ff or _has(folder, ff)
            if rule.get("strict_folder") and ff and not ff_ok:
                continue

            if raw_target == "{keep}":
                if ff_ok:
                    return cur, False            # giữ nguyên (vị trí logic) — chỉ khi folder xác nhận
                continue

            gb = rule.get("group_by")
            if gb:
                key = names.group_key(prefix, gb, self._totals)
                if key is None:
                    continue
                raw_target = raw_target.replace("{group}", key)
            target = resolve_target(raw_target, self._hm_dirs)

            if ff_ok:
                return target, False             # chắc chắn
            if soft is None:
                soft = target
            elif soft != target:
                soft = ""                        # nhập nhằng → bỏ soft

        return (soft, True) if soft else (None, False)
