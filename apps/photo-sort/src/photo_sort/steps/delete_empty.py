"""Optional (rules: delete_empty=true): after apply, remove empty folders that are NOT
part of the plan (stale template sub-folders). Every folder in the assignment — including
the SOP's empty scaffold pairs and 'Hình ảnh khác' — is kept."""
from __future__ import annotations

from fs_tools import rmdir_if_empty, walk_dirs
from graphrun import node


@node("delete_empty")
def delete_empty(ctx) -> None:
    if ctx.dry_run:
        ctx.report.stages[-1].status = "skipped"
        ctx.report.stages[-1].detail = "dry-run"
        return

    root = ctx.data["root"]
    wanted = {k.replace("\\", "/") for k in ctx.data["assign"]}
    removed = 0
    for d in sorted(walk_dirs(root), key=lambda p: len(str(p)), reverse=True):
        rel = str(d.relative_to(root)).replace("\\", "/")
        if rel in wanted:
            continue
        if rmdir_if_empty(d):
            removed += 1
    ctx.report.stages[-1].detail = f"xoá {removed} thư mục rỗng ngoài kế hoạch"
