"""Human-readable diff of a plan (for the report / UI tree view)."""
from __future__ import annotations

from pathlib import Path

from bts_organizer.domain.models import FileOperation, Inventory


def tree_diff(ops: list[FileOperation], inventory: Inventory) -> list[dict]:
    existing = {sd for hm in inventory.values() for sd in hm.subdirs}
    rows: list[dict] = []
    for o in ops:
        if o.action == "mkdir":
            rows.append({"kind": "add", "label": o.path + "/", "depth": o.path.count("/")})
        elif o.action == "rmdir":
            rows.append({"kind": "del", "label": o.path + "/  (template rỗng)", "depth": o.path.count("/")})
        else:
            rows.append({
                "kind": "move",
                "label": f"{Path(o.path).name}  →  {o.dest}/",
                "depth": o.dest.count("/"),
            })
    rows.sort(key=lambda r: (r["label"]))
    return rows
