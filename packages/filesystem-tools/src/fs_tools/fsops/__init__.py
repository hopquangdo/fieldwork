"""Pure filesystem operations — MAX_PATH-safe, never overwrite, never delete files.

Depends only on ``fs_tools.winpath`` and ``fs_tools.exts``.
"""
from fs_tools.fsops.copy import copytree, safe_copy
from fs_tools.fsops.mkdir import makedirs
from fs_tools.fsops.move import SharingViolation, safe_move
from fs_tools.fsops.naming import free_name
from fs_tools.fsops.query import exists, is_empty_dir
from fs_tools.fsops.remove import rmdir_if_empty, rmtree
from fs_tools.fsops.walk import list_dir, walk_dirs, walk_files

__all__ = [
    "copytree", "safe_copy", "makedirs", "SharingViolation", "safe_move",
    "free_name", "exists", "is_empty_dir", "rmdir_if_empty", "rmtree",
    "list_dir", "walk_dirs", "walk_files",
]
