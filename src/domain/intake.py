"""Lọc đầu vào trước khi kiểm kê: bản sao LỒNG của trạm, thư mục không chứa ảnh, và ảnh
trùng NỘI DUNG (sha1). Dùng bởi ``steps/scan.py`` theo ``[scan]`` của profile.

Một số bản export lồng nguyên cây trạm vào chính nó (``TRẠM/TRẠM/1.…``, ``2.…``) → mỗi
ảnh xuất hiện 2 lần, output sinh thư mục rác. Bản lồng nhận ra bằng CẤU TRÚC (thư mục
con đánh số trùng tên với hạng mục của gốc), không bằng tên trạm. Ảnh trùng nội dung
giữ bản NÔNG nhất (rồi theo đường dẫn), các bản còn lại bị bỏ và ghi báo cáo.
Module không sửa đĩa — chỉ trả về danh sách đường dẫn tương đối cần loại.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

from infrastructure.filesystem import ListDirTool, WalkDirsTool, WalkFilesTool, longpath

list_dir, walk_dirs, walk_files = ListDirTool(), WalkDirsTool(), WalkFilesTool()

_NUMBERED = re.compile(r"^\s*\d+\s*([.\-_ ]|$)")


@dataclass
class Intake:
    skip_dirs: list[str] = field(default_factory=list)        # thư mục bỏ cả cây (tương đối)
    duplicates: list[tuple[str, str]] = field(default_factory=list)   # (bản bỏ, bản giữ)

    def skipped(self, rel: str) -> bool:
        return any(rel == d or rel.startswith(d + "/") for d in self.skip_dirs)


def _rel(p: Path, root: Path) -> str:
    return str(p.relative_to(root)).replace("\\", "/")


def _numbered_children(d: Path) -> set[str]:
    try:
        return {p.name.casefold() for p in list_dir(d) if p.is_dir() and _NUMBERED.match(p.name)}
    except OSError:
        return set()


def nested_copies(root: Path, *, min_overlap: int = 2) -> list[str]:
    """Thư mục con (mọi cấp) có ≥ ``min_overlap`` thư mục đánh số TRÙNG TÊN với hạng mục
    của ``root`` → bản sao lồng của trạm."""
    top = _numbered_children(root)
    if not top:
        return []
    out: list[str] = []
    for d in sorted(walk_dirs(root), key=lambda p: len(p.parts)):
        rel = _rel(d, root)
        if any(rel.startswith(o + "/") for o in out):
            continue
        if len(_numbered_children(d) & top) >= min_overlap:
            out.append(rel)
    return out


def imageless_dirs(root: Path) -> list[str]:
    """Thư mục cấp 1 KHÔNG đánh số và không chứa ảnh nào (Data, res…) — không thuộc phụ lục."""
    out = []
    for p in list_dir(root):
        if p.is_dir() and not _NUMBERED.match(p.name) and not any(walk_files(p, images_only=True)):
            out.append(p.name)
    return out


def content_duplicates(root: Path, files: list[Path], *, scope: str = "hang_muc") -> list[tuple[str, str]]:
    """(bản bỏ, bản giữ) cho ảnh trùng sha1. Giữ bản nông nhất, rồi theo đường dẫn.

    ``scope = "hang_muc"``: chỉ gộp bản trùng TRONG CÙNG hạng mục (thư mục cấp 1) — ảnh cố
    ý đặt ở 2 hạng mục (vd dị tật + trèo cao) được giữ cả hai. ``"all"``: gộp toàn trạm."""
    seen: dict[tuple[str, str], str] = {}
    dups: list[tuple[str, str]] = []
    for f in sorted(files, key=lambda p: (len(p.parts), str(p))):
        try:
            h = hashlib.sha1(longpath(f).read_bytes()).hexdigest()
        except OSError:
            continue
        rel = _rel(f, root)
        key = (rel.split("/", 1)[0] if scope == "hang_muc" else "", h)
        if key in seen:
            dups.append((rel, seen[key]))
        else:
            seen[key] = rel
    return dups


def survey(root: Path, cfg: dict) -> Intake:
    """Áp ``[scan]``: ``skip_nested_copies`` · ``skip_imageless_dirs`` · ``dedupe_content``
    (+ ``dedupe_scope``)."""
    it = Intake()
    if cfg.get("skip_nested_copies"):
        it.skip_dirs += nested_copies(root, min_overlap=int(cfg.get("nested_min_overlap", 2)))
    if cfg.get("skip_imageless_dirs"):
        it.skip_dirs += [d for d in imageless_dirs(root) if d not in it.skip_dirs]
    if cfg.get("dedupe_content"):
        files = [f for f in walk_files(root, images_only=True) if not it.skipped(_rel(f, root))]
        it.duplicates = content_duplicates(root, files, scope=str(cfg.get("dedupe_scope", "hang_muc")))
    return it
