"""Walk the image root -> per-hạng-mục Inventory."""
from __future__ import annotations

import re
from pathlib import Path

from fs_tools import IMAGE_EXTS

from bts_organizer.domain.catalog import hang_muc
from bts_organizer.domain.models import HangMucInventory, Inventory, StationMeta
from bts_organizer.winpath import longpath

_NUM_DIR = re.compile(r"^\s*(\d+)\s*[.\-_ ]\s*(.*)$")


def take_inventory(root: Path, image_root: Path, meta: StationMeta) -> Inventory:
    lroot = longpath(root)
    limg = longpath(image_root)
    names = hang_muc(meta.tower_type)
    inv: Inventory = {}

    for d in sorted(p for p in limg.iterdir() if p.is_dir()):
        m = _NUM_DIR.match(d.name)
        if not m:
            continue
        hm_id = int(m[1])
        if hm_id not in names:
            continue

        files: list[str] = []
        subdirs: list[str] = []
        junk: list[str] = []
        for child in sorted(d.rglob("*")):
            rel = str(child.relative_to(lroot)).replace("\\", "/")
            if child.is_dir():
                subdirs.append(rel)
                if _is_template_junk(child):
                    junk.append(rel)
            elif child.suffix.lower() in IMAGE_EXTS:
                files.append(rel)

        inv[hm_id] = HangMucInventory(
            id=hm_id,
            name=names[hm_id],
            dir=str(d.relative_to(lroot)).replace("\\", "/"),
            files=files,
            subdirs=subdirs,
            template_junk=junk,
        )
    return inv


def _is_template_junk(d: Path) -> bool:
    """Empty default-template subfolder (created by the report tool, no photos, generic name)."""
    try:
        has_img = any(p.suffix.lower() in IMAGE_EXTS for p in d.rglob("*") if p.is_file())
    except OSError:
        return False
    if has_img:
        return False
    n = d.name.casefold()
    return n.startswith("công tác chuẩn bị") and not re.search(r"m\d|đốt|tầng|lần", n)
