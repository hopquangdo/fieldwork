"""`scan` — built on LangChain's ListDirectoryTool, enriched with structure.

ListDirectoryTool only returns a flat list of names. `scan` adds optional
recursion and per-entry metadata (type / size / is_image) as JSON, which is what
an agent actually needs to plan file moves. Customize the `entry` dict or the
walk below.
"""
from __future__ import annotations

import json
from pathlib import Path

from langchain_community.tools.file_management import ListDirectoryTool
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from fs_tools import IMAGE_EXTS, resolve_within


class ScanArgs(BaseModel):
    subdir: str = Field(".", description="Folder (relative to the root) to list.")
    recursive: bool = Field(False, description="Recurse into sub-folders.")
    images_only: bool = Field(False, description="Only return image files.")


def _entry(root: Path, p: Path) -> dict:
    is_image = p.is_file() and p.suffix.lower() in IMAGE_EXTS
    return {
        "path": str(p.relative_to(root)),
        "type": "dir" if p.is_dir() else "file",
        "size": p.stat().st_size if p.is_file() else 0,
        "is_image": is_image,
    }


def make_scan_tool(root: str | Path) -> StructuredTool:
    root = Path(root).resolve()
    # kept for parity / simple cases; `scan` uses the richer walk below
    _flat = ListDirectoryTool(root_dir=str(root))

    def _scan(subdir: str = ".", recursive: bool = False, images_only: bool = False) -> str:
        base = resolve_within(root, subdir)
        if not base.is_dir():
            raise NotADirectoryError(str(base))
        walk = base.rglob("*") if recursive else base.iterdir()
        entries = [_entry(root, p) for p in sorted(walk)]
        if images_only:
            entries = [e for e in entries if e["is_image"]]
        return json.dumps(entries, ensure_ascii=False)

    return StructuredTool.from_function(
        _scan,
        name="scan",
        args_schema=ScanArgs,
        description="List files/folders under a directory as JSON: [{path, type, size, is_image}].",
    )
