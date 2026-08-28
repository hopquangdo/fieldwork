"""`rename` — rename in place via LangChain's MoveFileTool (no built-in rename tool).

Same never-overwrite guarantee as `move`; `new_name` must be a bare name.
"""
from __future__ import annotations

from pathlib import Path

from langchain_community.tools.file_management import MoveFileTool
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from fs_tools import resolve_within
from fs_tools.move import unique_destination


class RenameArgs(BaseModel):
    path: str = Field(..., description="Source file/folder path relative to the root.")
    new_name: str = Field(..., description="New name — a bare file/folder name, not a path.")


def make_rename_tool(root: str | Path) -> StructuredTool:
    root = Path(root).resolve()
    backend = MoveFileTool(root_dir=str(root))

    def _rename(path: str, new_name: str) -> str:
        if not new_name or Path(new_name).name != new_name or new_name in {".", ".."}:
            raise ValueError("new_name must be a bare name, not a path")
        src = resolve_within(root, path)
        if not src.exists():
            raise FileNotFoundError(str(src))
        dest = unique_destination(src.parent, new_name)
        rel_dest = dest.relative_to(root)
        backend.run({"source_path": path, "destination_path": str(rel_dest)})
        return f"renamed -> {rel_dest}"

    return StructuredTool.from_function(
        _rename,
        name="rename",
        args_schema=RenameArgs,
        description="Rename a file/folder within its current directory. Never overwrites.",
    )
