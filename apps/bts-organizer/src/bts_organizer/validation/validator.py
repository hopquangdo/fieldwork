"""Run every invariant over a ProjectedTree -> list[Issue]."""
from __future__ import annotations

from bts_organizer.domain.models import Answer, Issue, ProjectedTree
from bts_organizer.validation import invariants as inv


def validate(tree: ProjectedTree, *, original: set[str], answers: dict[str, Answer]) -> list[Issue]:
    issues: list[Issue] = []
    issues += list(inv.i_conservation(tree, original))
    for hm in tree.hang_muc:
        issues += list(inv.i_skeleton(hm))
        issues += list(inv.i_khac(hm))
        issues += list(inv.i_even_images(hm))
        issues += list(inv.i_blueprint(hm, answers))
    return issues


def worst(issues: list[Issue]) -> str:
    if any(i.severity == "HARD" for i in issues):
        return "HARD"
    if any(i.severity == "REPAIRABLE" for i in issues):
        return "REPAIRABLE"
    return "OK"
