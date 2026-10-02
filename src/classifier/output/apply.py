"""Ghi kết quả: dựng MỤC LỤC trước → COPY ảnh (input không đổi) → xoá thư mục mẫu rỗng.

Giữ lại dù rỗng: 'Hình ảnh khác' ở gốc + 'khác' của hạng mục có ảnh (SOP: luôn giữ 'khác').
"""
from __future__ import annotations

import shutil
from pathlib import Path

from infrastructure.filesystem import longpath

from classifier.catalog import Catalog


def apply(moves, cat: Catalog, out_root: Path, extras: list[Path] = ()) -> dict:
    out_root = Path(out_root)
    for leaf in cat.leaves():                                   # 1. mục lục
        longpath(out_root / leaf).mkdir(parents=True, exist_ok=True)
    for m in moves:                                             # 2. ảnh
        dst = longpath(out_root / m.folder / m.name)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(longpath(m.src), dst)
    for x in extras:                                            # 3. file đi kèm (PDF…)
        shutil.copy2(longpath(x), longpath(out_root / x.name))
    used_hm = {m.folder.split("/", 1)[0] for m in moves}
    keep = {cat.root_khac} | {s.khac.option for s in cat.sections if s.folder in used_hm}
    removed = 0                                                 # 4. bỏ thư mục mẫu rỗng
    for d in sorted((p for p in out_root.rglob("*") if p.is_dir()),
                    key=lambda p: len(p.parts), reverse=True):
        rel = d.relative_to(out_root).as_posix()
        if rel in keep or any(k.startswith(rel + "/") for k in keep):
            continue
        if not any(d.iterdir()):
            d.rmdir()
            removed += 1
    return {"copied": len(moves), "extras": len(extras), "empty_removed": removed}
