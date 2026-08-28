"""layouts -> ordered, deduped list[FileOperation]  (mkdir → move → rmdir)."""
from __future__ import annotations

from bts_organizer.domain.models import FileOperation, Inventory, LayoutResult
from bts_organizer.layout.base import current_dir


def build_operations(layouts: dict[int, LayoutResult], inventory: Inventory) -> list[FileOperation]:
    ops: list[FileOperation] = []

    wanted_dirs = {f.path for L in layouts.values() for f in L.folders}
    existing = {sd for hm in inventory.values() for sd in hm.subdirs}
    for d in sorted(wanted_dirs - existing, key=lambda p: p.count("/")):
        ops.append(FileOperation("mkdir", d))

    for L in layouts.values():
        for f in L.folders:
            for img in f.images:
                if current_dir(img) != f.path:
                    ops.append(FileOperation("move", img, f.path))

    junk = {d for L in layouts.values() for d in L.delete_dirs}
    for d in sorted(junk, key=len, reverse=True):
        ops.append(FileOperation("rmdir", d))

    return ops


def summarize(ops: list[FileOperation]) -> dict:
    return {
        "mkdir": sum(o.action == "mkdir" for o in ops),
        "move": sum(o.action == "move" for o in ops),
        "rmdir": sum(o.action == "rmdir" for o in ops),
        "total": len(ops),
    }
