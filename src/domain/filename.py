"""Tên file phụ lục — theo quy ước trong profile ``[filename]``.

* ``conforms`` — tên đã đúng quy ước chưa (đúng → giữ nguyên)
* ``content_name`` — suy "tên cấu kiện" từ tên thư mục đích (dùng ``[[naming]]`` +
  ``strip_prefixes``, giữ đuôi nhóm M2/D3…)
* ``build_name`` — ráp tên mới theo ``build`` format
"""
from __future__ import annotations

import re
from pathlib import Path


def conforms(filename: str, regex: str) -> bool:
    return bool(re.match(regex, Path(filename).name))


def content_name(folder_leaf: str, naming_rules: list[dict], *,
                 strip_prefixes: tuple[str, ...], trail_re: re.Pattern | None) -> str:
    lo = folder_leaf.casefold()
    trail = trail_re.search(folder_leaf) if trail_re else None
    key = f" {trail[1]}" if trail else ""              # giữ 'M2' / 'D3' / 'Tầng dây 1'
    key = key.replace(" M", " Móng M") if key.strip().startswith("M") else key

    for r in naming_rules:
        if any(s.casefold() in lo for s in r.get("folder", [])):
            return (r["name"] + key).strip()
    for pre in strip_prefixes:
        if folder_leaf.startswith(pre):
            return folder_leaf[len(pre):] or folder_leaf
    return folder_leaf


def build_name(content: str, ts: tuple[int, int, int], *, primary: bool, ext: str,
               fmt: str, primary_yes: str, primary_no: str, seq: int = 0) -> str:
    h, m, s = ts
    return fmt.format(
        content=content, h=h, m=m, s=s,
        seq=f"@{seq}" if seq else "",
        primary=primary_yes if primary else primary_no,
        ext=ext,
    )
