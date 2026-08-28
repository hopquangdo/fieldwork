from __future__ import annotations

from typing import Annotated, Any, TypedDict


def _merge(a: dict | None, b: dict | None) -> dict:
    return {**(a or {}), **(b or {})}


class StationState(TypedDict, total=False):
    root: str
    dry_run: bool

    image_root: str
    data_dir: str
    meta: Any                       # StationMeta
    inventory: Any                  # Inventory
    present: list[int]

    layouts: dict[int, Any]         # id -> LayoutResult
    questions: list[Any]
    answers: Annotated[dict[str, Any], _merge]
    q_attempts: Annotated[dict[str, int], _merge]

    operations: list[Any]
    projected: Any
    issues: list[Any]
    repair_iters: int
    skip_validate: bool
    manual_review: list[int]

    exec_results: list[Any]
    report: Any
