"""Build the Report shown to the user / returned by the API."""
from __future__ import annotations

from bts_organizer.domain.catalog import is_cong_tac_folder
from bts_organizer.domain.models import Answer, Inventory, Issue, LayoutResult, ProjectedTree, Report
from bts_organizer.planning import summarize, tree_diff


def build_report(
    *,
    station: str,
    meta,
    inventory: Inventory,
    layouts: dict[int, LayoutResult],
    tree: ProjectedTree,
    operations,
    issues: list[Issue],
    answers: dict[str, Answer],
    questions,
    repair_iters: int,
    exec_results,
    manual_review: list[int],
    dry_run: bool,
) -> Report:
    before = sum(hm.image_count for hm in inventory.values())
    after = len(tree.images_after)

    counts = []
    for hm in tree.hang_muc:
        ct = [f for f in hm.folders if f.is_cong_tac]
        counts.append({
            "id": hm.id,
            "folders": len(hm.folders),
            "even_folders": len(ct) % 2 == 0,
            "images": sum(len(f.images) for f in hm.folders),
            "note": _note(hm),
        })

    gaps = [f"Mục {hm.id}: 0 ảnh — khung rỗng, cần nhặt bù"
            for hm in tree.hang_muc
            if sum(len(f.images) for f in hm.folders) == 0 and any(f.is_cong_tac for f in hm.folders)]

    unresolved = sorted(q.id for q in questions if q.id not in answers or answers[q.id].folder is None)

    return Report(
        station=station,
        tower_type=meta.tower_type,
        images_before=before,
        images_after=after,
        counts=counts,
        tree=tree_diff(operations, inventory),
        operations=summarize(operations),
        vision=[
            {"q": a.q_id, "folder": a.folder, "blueprint": a.is_blueprint,
             "confidence": a.confidence, "attempt": a.attempt}
            for a in answers.values()
        ],
        repair_iters=repair_iters,
        gaps=gaps,
        unresolved=unresolved,
        manual_review=manual_review,
        exec={
            "status": "dry_run" if dry_run else "applied",
            "applied": sum(1 for r in exec_results if r.ok),
            "failed": sum(1 for r in exec_results if not r.ok),
            "failures": [r.detail for r in exec_results if not r.ok][:20],
        },
        aborted=any(i.severity == "HARD" for i in issues),
        errors=[f"{i.kind}: {i.detail}" for i in issues if i.severity == "HARD"],
    )


def _note(hm) -> str:
    total = sum(len(f.images) for f in hm.folders)
    if total == 0 and any(f.is_cong_tac for f in hm.folders):
        return "khung rỗng"
    odd = [f.path.rsplit("/", 1)[-1] for f in hm.folders if f.is_cong_tac and len(f.images) % 2]
    return f"lẻ: {', '.join(odd)}" if odd else ""
