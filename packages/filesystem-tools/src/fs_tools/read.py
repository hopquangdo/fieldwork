"""`read` — wraps LangChain's ReadFileTool.

Pure passthrough for now. Customize `_read` to add encoding handling, size caps,
binary detection, etc.
"""
from __future__ import annotations

from pathlib import Path

from langchain_community.tools.file_management import ReadFileTool
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field


class ReadArgs(BaseModel):
    path: str = Field(..., description="Text file path relative to the root.")


def make_read_tool(root: str | Path) -> StructuredTool:
    backend = ReadFileTool(root_dir=str(Path(root).resolve()))

    def _read(path: str) -> str:
        # customize here (e.g. truncate, decode fallbacks)
        return backend.run({"file_path": path})

    return StructuredTool.from_function(
        _read,
        name="read",
        args_schema=ReadArgs,
        description="Read a text file's contents.",
    )
