"""Execute the moves (apply only). safe_move + journal; retry sharing violations."""
from __future__ import annotations

import time

from fs_tools import SharingViolation, makedirs, safe_move
from graphrun import node


@node("apply")
def apply(ctx) -> None:
    root = ctx.data["root"]
    moves = ctx.data["moves"]

    if ctx.dry_run:
        ctx.report.stages[-1].status = "skipped"
        ctx.report.stages[-1].detail = f"dry-run — {len(moves)} move chưa ghi"
        ctx.report.sections["images_after"] = ctx.report.sections["images_before"]
        return

    done = 0
    pending = list(moves)
    retry: list = []
    for attempt in range(3):
        retry = []
        for m in pending:
            key = m.src
            if ctx.journal.done(key):
                continue
            try:
                dest = safe_move(root / m.src, root / m.dest_dir,
                                 rename=m.new_name, convert_jpeg=m.convert, on_exist="raise")
                ctx.journal.record(key, dest=str(dest.relative_to(root)))
                done += 1
            except FileNotFoundError:
                ctx.journal.record(key, dest="(source gone)")
            except FileExistsError as exc:
                ctx.report.sections.setdefault("conflicts", []).append(str(exc))
                retry.append(m)
            except SharingViolation:
                retry.append(m)
        if not retry:
            break
        pending = retry
        time.sleep(0.4 * (attempt + 1))
    failed = len(retry)

    for folder in ctx.data["assign"]:
        makedirs(root / folder)     # materialise every assigned folder, incl. empty scaffold ones

    ctx.report.stages[-1].detail = f"moved {done}, failed {failed}"
    ctx.report.sections["images_after"] = ctx.report.sections["images_before"]
    if failed:
        ctx.report.abort(f"{failed} move không thực hiện được (file bị khoá)")
