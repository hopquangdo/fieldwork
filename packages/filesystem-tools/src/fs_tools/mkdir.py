"""`mkdir` — create a folder (parents included)."""
from __future__ import annotations

from pathlib import Path

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from fs_tools import resolve_within


class MkdirArgs(BaseModel):
    path: str = Field(..., description="Folder path (relative to root) to create.")


def mkdir(root: Path, path: str) -> str:
    d = resolve_within(root, path)
    if d.exists() and not d.is_dir():
        raise NotADirectoryError(str(d))
    existed = d.is_dir()
    d.mkdir(parents=True, exist_ok=True)
    return f"exists: {d.relative_to(root)}" if existed else f"created: {d.relative_to(root)}"


def make_mkdir_tool(root: str | Path) -> StructuredTool:
    root = Path(root).resolve()

    def _mkdir(path: str) -> str:
        return mkdir(root, path)

    return StructuredTool.from_function(
        _mkdir,
        name="mkdir",
        args_schema=MkdirArgs,
        description="Create a folder, including parent folders. No error if it already exists.",
    )
