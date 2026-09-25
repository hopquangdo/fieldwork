"""All filesystem operations, one :class:`FsTool` class each — plus the tiny
Windows path helpers they need (``longpath`` / ``raw`` / ``strip``) and
``IMAGE_EXTS``. Nothing else lives in this package.

MAX_PATH-safe (every path goes through ``raw``); **never overwrites a file**;
**never deletes a file** — only empty directories or whole trees, on request.

The classes are stateless. Callers instantiate what they need::

    from infrastructure.filesystem import MoveFileTool, WalkFilesTool
    move_file, walk_files = MoveFileTool(), WalkFilesTool()
    for p in walk_files(root, images_only=True):
        move_file(p, dest)
"""
from __future__ import annotations

import os
import shutil
import time
from collections.abc import Callable, Iterator
from pathlib import Path

from infrastructure.filesystem.base import FsTool

# ─────────────────────────── constants + path helpers ───────────────────────────

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff"}

_PREFIX = "\\\\?\\"


def longpath(p: str | os.PathLike) -> Path:
    r"""Absolute Path, prefixed with \\?\ on Windows so os.* survives past MAX_PATH."""
    q = Path(p).resolve()
    if os.name == "nt" and not str(q).startswith(_PREFIX):
        return Path(_PREFIX + str(q))
    return q


def raw(p: str | os.PathLike) -> str:
    """String form for os.* calls (adds the prefix + resolves, on Windows)."""
    s = str(p)
    return _PREFIX + os.path.abspath(s) if os.name == "nt" and not s.startswith(_PREFIX) else s


def strip(p: str | os.PathLike) -> str:
    r"""Drop the leading \\?\ prefix if present."""
    s = str(p)
    return s[len(_PREFIX):] if s.startswith(_PREFIX) else s


class SharingViolation(OSError):
    """Windows WinError 32/33 — file locked by another process (retryable)."""


# ─────────────────────────────────── tools ───────────────────────────────────

class MakeDirTool(FsTool):
    name = "make_dir"
    description = "Create a directory, parents included; ok if it already exists."

    def execute(self, path: Path) -> None:
        os.makedirs(raw(path), exist_ok=True)


class PathExistsTool(FsTool):
    name = "path_exists"
    description = "True if the path exists."

    def execute(self, path: Path) -> bool:
        return os.path.exists(raw(path))


class IsEmptyDirTool(FsTool):
    name = "is_empty_dir"
    description = "True if the path is a directory with no entries."

    def execute(self, path: Path) -> bool:
        lp = raw(path)
        return os.path.isdir(lp) and not os.listdir(lp)


class FreeNameTool(FsTool):
    name = "free_name"
    description = "A path inside dest_dir that does not exist yet ('name (1).ext', ...)."

    def execute(self, dest_dir: Path, name: str) -> Path:
        stem, suffix = Path(name).stem, Path(name).suffix
        cand = Path(dest_dir) / name
        n = 1
        while os.path.exists(raw(cand)):
            cand = Path(dest_dir) / f"{stem} ({n}){suffix}"
            n += 1
        return cand


class WalkFilesTool(FsTool):
    name = "walk_files"
    description = "Yield every file under root (recursive), prefix stripped. MAX_PATH-safe."

    def execute(self, root: Path, *, images_only: bool = False) -> Iterator[Path]:
        for r, _, files in os.walk(raw(root)):
            for f in files:
                if images_only and Path(f).suffix.lower() not in IMAGE_EXTS:
                    continue
                yield Path(strip(os.path.join(r, f)))


class WalkDirsTool(FsTool):
    name = "walk_dirs"
    description = "Yield every directory under root (recursive), prefix stripped. MAX_PATH-safe."

    def execute(self, root: Path) -> Iterator[Path]:
        for r, dirs, _ in os.walk(raw(root)):
            for d in dirs:
                yield Path(strip(os.path.join(r, d)))


class ListDirTool(FsTool):
    name = "list_dir"
    description = "Immediate children (files + dirs), sorted."

    def execute(self, path: Path) -> Iterator[Path]:
        for name in sorted(os.listdir(raw(path))):
            yield Path(path) / name


class RemoveEmptyDirTool(FsTool):
    name = "remove_empty_dir"
    description = "Delete the directory only if it is empty; return whether it was removed."

    def execute(self, path: Path) -> bool:
        lp = raw(path)
        if os.path.isdir(lp) and not os.listdir(lp):
            os.rmdir(lp)
            return True
        return False


class RemoveTreeTool(FsTool):
    name = "remove_tree"
    description = "Recursively delete a directory tree (no-op if it does not exist)."

    def execute(self, path: Path) -> None:
        lt = raw(path)
        if not os.path.exists(lt):
            return
        for root, dirs, files in os.walk(lt, topdown=False):
            for f in files:
                os.remove(os.path.join(root, f))
            for d in dirs:
                os.rmdir(os.path.join(root, d))
        os.rmdir(lt)


class CopyTreeTool(FsTool):
    name = "copy_tree"
    description = "Recursive copy preserving mtime; returns the file count. MAX_PATH-safe."

    def execute(self, source: Path, dest: Path) -> int:
        n = 0
        lsrc = raw(source)
        for root, _, files in os.walk(lsrc):
            rel = root[len(lsrc):].strip("\\/")
            out = os.path.join(str(dest), rel) if rel else str(dest)
            os.makedirs(raw(out), exist_ok=True)
            for f in files:
                shutil.copy2(os.path.join(root, f), raw(os.path.join(out, f)))
                n += 1
        return n


class CopyFileTool(FsTool):
    name = "copy_file"
    description = "Copy a file into dest_dir without ever overwriting. Returns the final path."

    def execute(self, source: Path, dest_dir: Path, *, rename: str | None = None) -> Path:
        source = Path(source)
        if not os.path.exists(raw(source)):
            raise FileNotFoundError(str(source))
        os.makedirs(raw(dest_dir), exist_ok=True)
        dest = FreeNameTool().execute(Path(dest_dir), rename or source.name)
        shutil.copy2(raw(source), raw(dest))
        return dest


class MoveFileTool(FsTool):
    name = "move_file"
    description = "Move a file into another directory. Never overwrites."

    def execute(self, source: Path, dest_dir: Path, *, rename: str | None = None,
                transform: Callable[[bytes], bytes] | None = None,
                on_exist: str = "bump", retries: int = 0) -> Path:
        """on_exist: "bump" -> pick a free 'name (1)' variant · "raise" -> FileExistsError.
        transform: if given, ``target`` gets ``transform(source_bytes)`` and the
        source is deleted (e.g. a caller-supplied PNG->JPEG re-encoder).
        """
        source = Path(source)
        if not os.path.exists(raw(source)):
            raise FileNotFoundError(str(source))
        os.makedirs(raw(dest_dir), exist_ok=True)
        target = Path(dest_dir) / (rename or source.name)
        if os.path.exists(raw(target)) and strip(str(target)) != strip(str(source)):
            if on_exist == "raise":
                raise FileExistsError(str(target))
            target = FreeNameTool().execute(Path(dest_dir), rename or source.name)
        if strip(str(target)) == strip(str(source)) and transform is None:
            return target
        for attempt in range(retries + 1):
            try:
                if transform is not None:
                    with open(raw(source), "rb") as fh:
                        data = fh.read()
                    with open(raw(target), "wb") as fh:
                        fh.write(transform(data))
                    os.remove(raw(source))
                else:
                    shutil.move(raw(source), raw(target))
                return target
            except OSError as e:
                if getattr(e, "winerror", None) in (32, 33):
                    if attempt < retries:
                        time.sleep(0.3 * (attempt + 1))
                        continue
                    raise SharingViolation(str(e)) from e
                raise
        return target
