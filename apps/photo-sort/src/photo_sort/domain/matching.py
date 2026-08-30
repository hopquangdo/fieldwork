"""Rule engine: khớp 1 ảnh với 1 thư mục đích theo các ``[[rule]]`` trong TOML.

Hàm thuần, không ``ctx``. Rule keys:
``match`` · ``exclude`` · ``from_folder`` · ``not_from_folder`` · ``group_by``
(mong/dot/tang/lan/vitri) · ``target`` (``"{keep}"`` = giữ nguyên).
"""
from __future__ import annotations

import re

from photo_sort.domain.naming import group_key

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


def match_photo(photo, rules: list[dict], hm_dirs: dict[int, str]) -> tuple[str | None, bool]:
    """→ ``(target, is_soft)``.

    * rule đầu tiên khớp **và** ``from_folder`` xác nhận → ``(target, False)`` (chắc chắn)
    * chỉ 1 rule khớp ``match`` nhưng ``from_folder`` không khớp → ``(target, True)`` (lỏng)
    * không rule nào → ``(None, False)``
    """
    prefix, folder = photo.prefix, photo.folder.casefold()
    soft: str | None = None
    for rule in rules:
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

        if raw_target == "{keep}":
            if ff_ok:
                return photo.folder, False       # giữ nguyên — chỉ khi folder xác nhận
            continue

        gb = rule.get("group_by")
        if gb:
            key = group_key(prefix, gb)
            if key is None:
                continue
            raw_target = raw_target.replace("{group}", key)
        target = resolve_target(raw_target, hm_dirs)

        if ff_ok:
            return target, False                 # chắc chắn
        if soft is None:
            soft = target
        elif soft != target:
            soft = ""                            # nhập nhằng → bỏ soft
    return (soft, True) if soft else (None, False)
