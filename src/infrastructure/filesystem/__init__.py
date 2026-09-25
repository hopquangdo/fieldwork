"""filesystem-tools — Windows-safe filesystem operations as :class:`FsTool` classes.

Zero dependencies. Two modules: ``base`` (the :class:`FsTool` contract) and
``tools`` (the operations + ``longpath`` / ``raw`` / ``strip`` path helpers).

The tool classes are stateless — instantiate what you need::

    from infrastructure.filesystem import MoveFileTool, WalkFilesTool
    move_file, walk_files = MoveFileTool(), WalkFilesTool()
"""
from infrastructure.filesystem.base import FsTool
from infrastructure.filesystem.operations import (
    IMAGE_EXTS,
    CopyFileTool,
    CopyTreeTool,
    FreeNameTool,
    IsEmptyDirTool,
    ListDirTool,
    MakeDirTool,
    MoveFileTool,
    PathExistsTool,
    RemoveEmptyDirTool,
    RemoveTreeTool,
    SharingViolation,
    WalkDirsTool,
    WalkFilesTool,
    longpath,
    raw,
    strip,
)

__all__ = [
    "FsTool", "IMAGE_EXTS", "SharingViolation",
    "MoveFileTool", "CopyFileTool", "CopyTreeTool", "MakeDirTool", "RemoveTreeTool",
    "RemoveEmptyDirTool", "FreeNameTool", "PathExistsTool", "IsEmptyDirTool",
    "WalkFilesTool", "WalkDirsTool", "ListDirTool",
    "longpath", "raw", "strip",
]
