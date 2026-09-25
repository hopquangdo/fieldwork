"""Đọc số liệu trạm từ file ``TABLEBia*.txt`` trong thư mục Data (SOP §1).

Pattern nhận loại cột + trích số (n_dot / n_mong / n_tang) đến từ profile
``[metadata]``. ``peek_tower_type`` chạy TRƯỚC khi profile đầy đủ được nạp — caller
truyền vào ``Metadata`` của profile ``_base`` để chọn đúng file profile.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from infrastructure.filesystem import ListDirTool, WalkFilesTool, longpath

from domain.profile import Metadata

walk_files = WalkFilesTool()
list_dir = ListDirTool()


@dataclass
class StationMeta:
    tower_type: str = "day_co"
    n_dot: int = 0
    n_mong: int = 0
    n_tang: int = 0
    source: str = ""
    resolved: bool = False          # True = đọc được loại cột từ TABLEBia (không phải mặc định)
    warnings: list[str] = field(default_factory=list)


def _tower_type(text: str, table: dict[str, tuple[str, ...]]) -> str:
    low = text.casefold()
    for tt, kws in table.items():
        if any(k in low for k in kws):
            return tt
    return ""


def _is_table(p: Path, glob: str) -> bool:
    return p.suffix.lower() == ".txt" and p.name.casefold().startswith(glob)


def _find_shallow(d: Path, glob: str, depth: int) -> Path | None:
    """Tìm TABLEBia trong ``d`` tối đa ``depth`` cấp — không quét cả cây ảnh."""
    try:
        entries = list(list_dir(d))
    except OSError:
        return None
    for p in entries:
        if not p.is_dir() and _is_table(p, glob):
            return p
    if depth > 1:
        for p in entries:
            if p.is_dir() and (hit := _find_shallow(p, glob, depth - 1)):
                return hit
    return None


def find_table_bia(root: Path, glob: str = "tablebia") -> Path | None:
    """TABLEBia trong ``root``; không có thì tìm ở các thư mục ANH EM của ``root``
    (đầu vào có thể là thư mục ảnh, còn Data nằm cạnh nó)."""
    for p in walk_files(root):
        if _is_table(p, glob):
            return p
    for sib in list_dir(root.parent) if root.parent != root else []:
        if sib.is_dir() and sib != root and (hit := _find_shallow(sib, glob, 2)):
            return hit
    return None


def read_meta(root: Path, cfg: Metadata) -> StationMeta:
    """``root`` = thư mục trạm (chứa Data…)."""
    meta = StationMeta()
    bia = find_table_bia(root, cfg.table_glob)
    if bia is None:
        meta.warnings.append("Không thấy TABLEBia.txt — giả định cột dây co.")
        return meta

    text = longpath(bia).read_text(encoding="utf-8", errors="replace")
    meta.source = bia.name
    tt = _tower_type(text, cfg.tower_type)
    if tt:
        meta.tower_type = tt
        meta.resolved = True
    else:
        meta.warnings.append("TABLEBia.txt không ghi rõ loại cột — giả định dây co.")
    for attr, pat in cfg.fields.items():
        m = re.search(pat, text, re.I)
        if m and hasattr(meta, attr):
            setattr(meta, attr, int(m[1]))
    return meta


def peek_tower_type(root: Path, cfg: Metadata) -> str:
    """Đọc nhanh loại cột TRƯỚC khi load profile đầy đủ (để chọn đúng file profile).
    ``cfg`` = ``Metadata`` của profile ``_base``."""
    bia = find_table_bia(root, cfg.table_glob)
    if bia is None:
        return ""
    try:
        return _tower_type(longpath(bia).read_text(encoding="utf-8", errors="replace"), cfg.tower_type)
    except OSError:
        return ""


def refine_tower_type(img_root: Path, declared: str, evidence: list[dict],
                      skip=lambda rel: False) -> tuple[str, str]:
    """Ảnh thực tế thắng khai báo (RULE.md: "TABLEBia ghi Dây co nhưng thực tế tự đứng").

    Mỗi ``[[tower_evidence]]``: ``declared`` (loại cột khai) · ``require_photos_in`` (chuỗi
    nhận diện hạng mục ĐẶC TRƯNG của loại đó) · ``otherwise`` (loại cột thay thế). Nếu mọi
    hạng mục đặc trưng đều KHÔNG có ảnh → trả về ``otherwise``. ``skip(rel)`` loại ảnh
    của bản lồng / trùng. → ``(loại cột, lý do)``; không đổi thì lý do rỗng."""
    if not declared or not img_root.is_dir():
        return declared, ""
    tops = [p for p in list_dir(img_root) if p.is_dir() and re.match(r"^\s*\d+", p.name)]
    for ev in evidence:
        if ev.get("declared") != declared or not ev.get("otherwise") or not tops:
            continue
        keys = [k.casefold() for k in ev.get("require_photos_in") or []]
        hits = [p for p in tops if any(k in p.name.casefold() for k in keys)]
        n = sum(
            1 for d in hits for f in walk_files(d, images_only=True)
            if not skip(str(f.relative_to(img_root)).replace("\\", "/"))
        )
        if n == 0:
            names = ", ".join(p.name for p in hits) or "không có thư mục"
            return str(ev["otherwise"]), f"hạng mục đặc trưng không có ảnh: {names}"
    return declared, ""
