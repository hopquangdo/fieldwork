"""`move` — wraps LangChain's MoveFileTool, adding a never-overwrite guarantee.

MoveFileTool clobbers an existing destination. Here we resolve a free name
(`a (1).jpg`) first, then delegate the actual move to the built-in tool.
"""
from __future__ import annotations

from pathlib import Path

from langchain_community.tools.file_management import MoveFileTool
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from fs_tools import resolve_within


class MoveArgs(BaseModel):
    path: str = Field(..., description="Source file/folder path relative to the root.")
    dest_dir: str = Field(..., description="Destination folder (relative to root). Created if missing.")


def unique_destination(dest_dir: Path, name: str) -> Path:
    """A path inside dest_dir that does not exist yet ('name (1).ext', ...)."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    stem, suffix = Path(name).stem, Path(name).suffix
    candidate = dest_dir / name
    n = 1
    while candidate.exists():
        candidate = dest_dir / f"{stem} ({n}){suffix}"
        n += 1
    return candidate


def make_move_tool(root: str | Path) -> StructuredTool:
    root = Path(root).resolve()
    backend = MoveFileTool(root_dir=str(root))

    def _move(path: str, dest_dir: str) -> str:
        src = resolve_within(root, path)
        if not src.exists():
            raise FileNotFoundError(str(src))
        dest = unique_destination(resolve_within(root, dest_dir), src.name)
        rel_dest = dest.relative_to(root)
        backend.run({"source_path": path, "destination_path": str(rel_dest)})
        return f"moved -> {rel_dest}"

    return StructuredTool.from_function(
        _move,
        name="move",
        args_schema=MoveArgs,
        description="Move a file/folder into another folder. Never overwrites, never deletes.",
    )
