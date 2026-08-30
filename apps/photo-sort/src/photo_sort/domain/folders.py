"""Pure helpers for reasoning about appendix folder paths (``"3.Công tác…/Công tác đo …"``).

No I/O, no ``ctx`` — just string logic shared by the steps.
"""
from __future__ import annotations

import re

_NUM = re.compile(r"^\s*\d+\s*[.\-_ ]\s*")


def is_khac(leaf: str) -> bool:
    lo = leaf.casefold()
    return lo.startswith("hình ảnh khác") or lo.startswith("hinh anh khac")


def is_cong_tac(leaf: str) -> bool:
    lo = leaf.casefold()
    return lo.startswith("công tác") or "chuẩn bị" in lo


def leaf_of(folder: str) -> str:
    return folder.rsplit("/", 1)[-1]


def hm_of(folder: str) -> str:
    return folder.split("/", 1)[0]


def hm_base(hm_folder: str) -> str:
    """'2.Công tác kiểm tra khe hở cấu kiện lắp ghép' -> 'kiểm tra khe hở cấu kiện lắp ghép'."""
    name = _NUM.sub("", hm_folder)
    for pre in ("Công tác đo ", "Công tác kiểm tra ", "Công tác trèo cao", "Công tác ", "Hình ảnh "):
        if name.startswith(pre):
            return name[len(pre):].strip(" (") or name
    return name


def core_of(cong_tac_leaf: str) -> str:
    """'Công tác chuẩn bị đo lực căng M2' -> 'đo lực căng M2'."""
    s = cong_tac_leaf
    for pre in ("Công tác chuẩn bị ", "Công tác đo ", "Công tác kiểm tra ", "Công tác "):
        if s.startswith(pre):
            return s[len(pre):]
    return s


def existing_dir(existing: set[str], hm: str, predicate) -> str | None:
    for d in sorted(existing):
        if hm_of(d) == hm and d.count("/") == 1 and predicate(leaf_of(d)):
            return d
    return None


def khac_in_assign(assign: dict, hm: str) -> str | None:
    """The 'Hình ảnh khác' folder already present in ``assign`` for this hạng mục."""
    return next((k for k in assign if hm_of(k) == hm and is_khac(leaf_of(k))), None)


def khac_folder(assign: dict, hm: str, *, existing: set[str] | None = None, base: str = "") -> str:
    """Resolve the hạng mục's 'Hình ảnh khác' folder: reuse one from ``assign``, else one
    that exists on disk, else a fresh name ``"{hm}/Hình ảnh khác {base}"``."""
    hit = khac_in_assign(assign, hm)
    if hit:
        return hit
    if existing:
        d = existing_dir(existing, hm, is_khac)
        if d:
            return d
    return f"{hm}/Hình ảnh khác{f' {base}'.rstrip()}"
