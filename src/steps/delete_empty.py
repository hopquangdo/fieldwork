"""Sau ``apply``: xoá các thư mục RỖNG không nằm trong kế hoạch (thư mục mẫu rác còn
sót). Thư mục thuộc ``assign`` — kể cả cặp scaffold rỗng và 'Hình ảnh khác' — luôn
giữ lại.
"""
from __future__ import annotations

from infrastructure.filesystem import RemoveEmptyDirTool, WalkDirsTool
from runtime import node
from domain.state import state

remove_empty_dir, walk_dirs = RemoveEmptyDirTool(), WalkDirsTool()


@node("delete_empty")
def delete_empty(ctx) -> None:
    root = state(ctx).root
    wanted = {k.replace("\\", "/") for k in state(ctx).assign}
    removed = 0
    for d in sorted(walk_dirs(root), key=lambda p: len(str(p)), reverse=True):
        rel = str(d.relative_to(root)).replace("\\", "/")
        if rel in wanted:
            continue
        if remove_empty_dir(d):
            removed += 1
    ctx.report.stages[-1].detail = f"xoá {removed} thư mục rỗng ngoài kế hoạch"
