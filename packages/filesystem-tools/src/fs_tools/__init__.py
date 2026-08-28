"""Filesystem tools for LangChain agents.

Each tool is its own module (`scan`, `read`, `view`, `move`, `rename`, `mkdir`).
Where LangChain ships a built-in (`langchain_community` file-management tools) we
wrap it so there is exactly one place to add project-specific rules — e.g. the
"never overwrite / never delete" guarantees here. `view` is fully custom because
LangChain has no image tool.

    from fs_tools import make_fs_tools
    tools = make_fs_tools("/some/root")          # list[BaseTool]
    agent = create_react_agent(model, tools)
"""
from __future__ import annotations

from pathlib import Path

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff"}

__all__ = [
    "IMAGE_EXTS",
    "SandboxError",
    "resolve_within",
    "make_fs_tools",
    "make_scan_tool",
    "make_read_tool",
    "make_view_tool",
    "make_move_tool",
    "make_rename_tool",
    "make_mkdir_tool",
]


class SandboxError(ValueError):
    """Raised when a path would escape the sandbox root."""


def resolve_within(root: str | Path, target: str | Path) -> Path:
    """Resolve `target` (absolute, or relative to `root`) and keep it inside `root`."""
    root = Path(root).resolve()
    p = Path(target)
    p = (p if p.is_absolute() else root / p).resolve()
    if p != root and root not in p.parents:
        raise SandboxError(f"path escapes sandbox root: {target}")
    return p


# tool modules import from this package, so import them after the definitions above
from .scan import make_scan_tool
from .read import make_read_tool
from .view import make_view_tool
from .move import make_move_tool
from .rename import make_rename_tool
from .mkdir import make_mkdir_tool


def make_fs_tools(root: str | Path, *, max_edge: int = 1024):
    """All six tools bound to one sandbox `root`."""
    return [
        make_scan_tool(root),
        make_read_tool(root),
        make_view_tool(root, max_edge=max_edge),
        make_move_tool(root),
        make_rename_tool(root),
        make_mkdir_tool(root),
    ]
