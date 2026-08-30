"""filesystem-tools — Windows-safe FS primitives + optional LangChain tools.

Layers (one-way deps): ``winpath`` / ``exts`` -> ``fsops`` -> ``media`` -> ``agent``.
``fs_tools.agent`` needs the ``agent`` extra and is imported explicitly.
"""
from fs_tools.exts import IMAGE_EXTS
from fs_tools.fsops import (
    SharingViolation,
    copytree,
    exists,
    free_name,
    is_empty_dir,
    list_dir,
    makedirs,
    rmdir_if_empty,
    rmtree,
    safe_copy,
    safe_move,
    walk_dirs,
    walk_files,
)
from fs_tools.media import image_block, load_image_b64, to_jpeg_bytes
from fs_tools.winpath import longpath, raw, strip

__all__ = [
    "IMAGE_EXTS",
    "SharingViolation", "copytree", "exists", "free_name", "is_empty_dir",
    "list_dir", "makedirs", "rmdir_if_empty", "rmtree", "safe_copy", "safe_move",
    "walk_dirs", "walk_files",
    "image_block", "load_image_b64", "to_jpeg_bytes",
    "longpath", "raw", "strip",
]
