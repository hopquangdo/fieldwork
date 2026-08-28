"""Apply a plan on disk: mkdir → move (no overwrite) → rmdir (empty only). Retry transient errors.

Every existence/stat/move call goes through the \\?\ extended-length form so
deep Vietnamese station trees (which blow past MAX_PATH) work.
"""
from __future__ import annotations

import os
import shutil
import time
from dataclasses import dataclass
from pathlib import Path

from fs_tools import resolve_within

from bts_organizer.domain.models import FileOperation
from bts_organizer.execution.journal import Journal


def _lp(p: Path | str) -> str:
    s = str(p)
    if os.name == "nt" and not s.startswith("\\\\?\\"):
        return "\\\\?\\" + os.path.abspath(s)
    return s


def _exists(p: Path) -> bool:
    return os.path.exists(_lp(p))


def _is_empty_dir(p: Path) -> bool:
    lp = _lp(p)
    return os.path.isdir(lp) and not os.listdir(lp)


def _free_name(dest_dir: Path, name: str) -> Path:
    stem, suffix = Path(name).stem, Path(name).suffix
    cand = dest_dir / name
    n = 1
    while os.path.exists(_lp(cand)):
        cand = dest_dir / f"{stem} ({n}){suffix}"
        n += 1
    return cand


@dataclass
class ExecResult:
    op: FileOperation
    ok: bool
    detail: str
    transient: bool = False


def apply_plan(root: str | Path, ops: list[FileOperation], *, passes: int = 3) -> list[ExecResult]:
    root = Path(root).resolve()
    journal = Journal(root)
    remaining = [o for o in ops if not journal.is_done(o)]
    results: list[ExecResult] = []

    for attempt in range(passes):
        failed: list[FileOperation] = []
        for op in remaining:
            r = _run_one(root, op)
            if r.ok:
                journal.record(op, r.detail)
                results.append(r)
            elif r.transient:
                failed.append(op)
            else:
                results.append(r)
        if not failed:
            break
        remaining = failed
        time.sleep(0.4 * (attempt + 1))
    else:
        results.extend(ExecResult(o, False, "still failing after retries", transient=True) for o in remaining)

    return results


def _run_one(root: Path, op: FileOperation) -> ExecResult:
    try:
        if op.action == "mkdir":
            os.makedirs(_lp(resolve_within(root, op.path)), exist_ok=True)
            return ExecResult(op, True, f"mkdir {op.path}")

        if op.action == "rmdir":
            d = resolve_within(root, op.path)
            if _is_empty_dir(d):
                os.rmdir(_lp(d))
                return ExecResult(op, True, f"rmdir {op.path}")
            return ExecResult(op, True, f"skip rmdir (not empty / gone) {op.path}")

        src = resolve_within(root, op.path)
        if not _exists(src):
            return ExecResult(op, True, f"skip move (source gone) {op.path}")
        dest_dir = resolve_within(root, op.dest)
        os.makedirs(_lp(dest_dir), exist_ok=True)
        dest = _free_name(dest_dir, src.name)
        if str(dest) != str(src):
            shutil.move(_lp(src), _lp(dest))
        return ExecResult(op, True, f"move {op.path} -> {dest.relative_to(root)}")

    except PermissionError as e:
        return ExecResult(op, False, f"{type(e).__name__}: {e}", transient=True)
    except OSError as e:
        transient = getattr(e, "winerror", None) in (32, 33)  # sharing / lock violation
        return ExecResult(op, False, f"{type(e).__name__}: {e}", transient=transient)
