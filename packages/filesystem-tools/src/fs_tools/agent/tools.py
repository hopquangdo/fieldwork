"""LangChain tools over one sandboxed directory. Requires the ``agent`` extra.

    from fs_tools.agent import make_fs_tools
    agent = create_react_agent(model, make_fs_tools("/data/inbox"))
"""
from __future__ import annotations

import json
from pathlib import Path

from langchain_core.tools import StructuredTool

from fs_tools.agent.sandbox import within
from fs_tools.agent.schemas import Move, PathArg, Sub
from fs_tools.exts import IMAGE_EXTS
from fs_tools.fsops import makedirs, safe_move, walk_files
from fs_tools.media import image_block, load_image_b64
from fs_tools.winpath import longpath


def make_fs_tools(root: str | Path, *, max_edge: int = 1024) -> list[StructuredTool]:
    root = Path(root).resolve()

    def scan(subdir: str = ".") -> str:
        base = within(root, subdir)
        rows = [
            {"path": str(p.relative_to(root)), "is_image": p.suffix.lower() in IMAGE_EXTS}
            for p in walk_files(base)
        ]
        return json.dumps(rows, ensure_ascii=False)

    def read(path: str) -> str:
        return longpath(within(root, path)).read_text(encoding="utf-8", errors="replace")[:200_000]

    def view(path: str):
        data, mime = load_image_b64(within(root, path), max_edge=max_edge)
        return [image_block(data, mime)], {"path": path}

    def move(path: str, dest_dir: str) -> str:
        dest = safe_move(within(root, path), within(root, dest_dir))
        return f"moved -> {dest.relative_to(root)}"

    def mkdir(path: str) -> str:
        makedirs(within(root, path))
        return f"created: {path}"

    return [
        StructuredTool.from_function(scan, name="scan", args_schema=Sub,
                                     description="List files under a folder as JSON."),
        StructuredTool.from_function(read, name="read", args_schema=PathArg,
                                     description="Read a text file."),
        StructuredTool.from_function(view, name="view", args_schema=PathArg,
                                     response_format="content_and_artifact",
                                     description="Open an image so you can see it."),
        StructuredTool.from_function(move, name="move", args_schema=Move,
                                     description="Move a file/folder into another folder (never overwrites)."),
        StructuredTool.from_function(mkdir, name="mkdir", args_schema=PathArg,
                                     description="Create a folder (parents included)."),
    ]
