"""layouts -> ProjectedTree (in-memory). No disk access."""
from __future__ import annotations

from bts_organizer.domain.models import Inventory, LayoutResult, ProjectedTree, ProjFolder, ProjHangMuc


def simulate(layouts: dict[int, LayoutResult], inventory: Inventory) -> ProjectedTree:
    hang_muc: list[ProjHangMuc] = []
    after: set[str] = set()
    for hm_id, L in sorted(layouts.items()):
        folders = []
        for f in L.folders:
            after.update(f.images)
            folders.append(ProjFolder(f.path, list(f.images), f.is_cong_tac, f.is_khac))
        hang_muc.append(ProjHangMuc(hm_id, folders))
    return ProjectedTree(hang_muc, after)


def original_images(inventory: Inventory) -> set[str]:
    return {f for hm in inventory.values() for f in hm.files}
