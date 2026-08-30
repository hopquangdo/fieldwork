"""Move a file into a folder — MAX_PATH-safe, never overwrites."""
from __future__ import annotations

import os
import shutil
import time
from pathlib import Path

from fs_tools.fsops.mkdir import makedirs
from fs_tools.fsops.naming import free_name
from fs_tools.fsops.query import exists
from fs_tools.winpath import raw, strip


class SharingViolation(OSError):
    """Windows WinError 32/33 — file locked by another process (retryable)."""


def safe_move(src: Path, dest_dir: Path, *, rename: str | None = None,
              convert_jpeg: bool = False, on_exist: str = "bump", retries: int = 0) -> Path:
    """Move src into dest_dir. Never overwrites.

    on_exist: "bump" -> pick a free 'name (1)' variant · "raise" -> FileExistsError.
    convert_jpeg: re-encode the bytes to JPEG at the destination (src is deleted).
    """
    src = Path(src)
    if not exists(src):
        raise FileNotFoundError(str(src))
    makedirs(dest_dir)
    target = Path(dest_dir) / (rename or src.name)
    if exists(target) and strip(str(target)) != strip(str(src)):
        if on_exist == "raise":
            raise FileExistsError(str(target))
        target = free_name(Path(dest_dir), rename or src.name)
    if strip(str(target)) == strip(str(src)) and not convert_jpeg:
        return target
    for attempt in range(retries + 1):
        try:
            if convert_jpeg:
                from fs_tools.media.image import to_jpeg_bytes

                with open(raw(src), "rb") as fh:
                    data = fh.read()
                with open(raw(target), "wb") as fh:
                    fh.write(to_jpeg_bytes(data))
                os.remove(raw(src))
            else:
                shutil.move(raw(src), raw(target))
            return target
        except OSError as e:
            if getattr(e, "winerror", None) in (32, 33):
                if attempt < retries:
                    time.sleep(0.3 * (attempt + 1))
                    continue
                raise SharingViolation(str(e)) from e
            raise
    return target
