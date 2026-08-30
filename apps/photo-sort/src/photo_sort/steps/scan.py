"""Locate the image root, copy input -> output (apply only), inventory every photo."""
from __future__ import annotations

import re
from pathlib import Path

from fs_tools import copytree, list_dir, rmtree, walk_dirs, walk_files
from graphrun import node

from photo_sort.domain.metadata import read_meta
from photo_sort.domain.naming import parse
from photo_sort.models import Photo

_NUMDIR = re.compile(r"^\s*\d+\s*([.\-_ ]|$)")


def _bad_image(p: Path) -> bool:
    from fs_tools import longpath

    try:
        lp = longpath(p)
        if lp.stat().st_size == 0:
            return True
        from PIL import Image

        with Image.open(lp) as im:
            im.verify()
        return False
    except Exception:  # noqa: BLE001
        return True


def _has_numbered(d: Path) -> bool:
    try:
        return any(p.is_dir() and _NUMDIR.match(p.name) for p in list_dir(d))
    except OSError:
        return False


_NUMPREFIX = re.compile(r"^\s*(\d+)\s*[.\-_ ]")


def image_root(station: Path) -> Path:
    if _has_numbered(station):
        return station
    same = station / station.name
    if same.is_dir() and _has_numbered(same):
        return same
    for p in list_dir(station):
        if p.is_dir() and _has_numbered(p):
            return p
    return station


def hang_muc_dirs(root: Path) -> dict[int, str]:
    """{2: '02.Khe hở', 3: '3.Công tác…'} — actual on-disk name per hạng mục number."""
    out: dict[int, str] = {}
    for p in list_dir(root):
        m = _NUMPREFIX.match(p.name)
        if p.is_dir() and m:
            out[int(m[1])] = p.name
    return out


@node("scan")
def scan(ctx) -> None:
    if not ctx.dry_run:
        i, o = ctx.input.resolve(), ctx.output.resolve()
        if o == i or i in o.parents or o in i.parents:
            ctx.report.abort("output không được trùng / nằm trong / chứa input")
            return

    if ctx.dry_run:
        work = ctx.input
    else:
        work = ctx.output / ctx.input.name
        if not ctx.journal.done("__copied__"):
            rmtree(work)                         # fresh copy (unless resuming)
            n = copytree(ctx.input, work)
            ctx.journal.record("__copied__", files=n)
            ctx.report.stages[-1].detail = f"copied {n} file · "
        else:
            ctx.report.stages[-1].detail = "resume (copy skipped) · "
    ctx.data["work"] = work

    root = image_root(work)
    ctx.data["root"] = root
    ctx.data["hm_dirs"] = hang_muc_dirs(root)
    photos: list[Photo] = []
    bad: list[str] = []
    for p in walk_files(root, images_only=True):
        rel = str(p.relative_to(root)).replace("\\", "/")
        if _bad_image(p):
            bad.append(rel)
            continue
        c = parse(p.name)
        photos.append(Photo(path=rel, prefix=c.prefix, is_primary=c.is_primary))
    ctx.data["photos"] = photos
    # initial assignment = raw placement (every photo where it physically sits).
    # `diagnose` reads this; `classify` overwrites it only when it actually runs.
    raw: dict[str, list[str]] = {}
    for p in photos:
        raw.setdefault(p.folder or "Hình ảnh khác", []).append(p.path)
    ctx.data["assign"] = raw
    if bad:
        ctx.report.sections["ảnh lỗi / rỗng (bỏ qua)"] = bad
    ctx.data["existing_dirs"] = {
        str(d.relative_to(root)).replace("\\", "/") for d in walk_dirs(root)
    }

    meta = read_meta(work)
    ctx.data["meta"] = meta
    cfg_tt = ctx.config.get("tower_type", "day_co")
    if meta.tower_type != cfg_tt:
        meta.warnings.append(f"TABLEBia = '{meta.tower_type}' nhưng rules = '{cfg_tt}' — kiểm tra lại.")
    ctx.report.sections["meta"] = {
        "tower_type": meta.tower_type, "n_dot": meta.n_dot, "n_mong": meta.n_mong,
        "n_tang": meta.n_tang, "source": meta.source,
    }
    for w in meta.warnings:
        ctx.report.errors.append(f"scan: {w}")

    ctx.report.stages[-1].detail += f"{len(photos)} ảnh · {meta.tower_type}"
    ctx.report.sections["images_before"] = len(photos)

    ctx.emit("step", f"cột {meta.tower_type} · {meta.n_dot} đốt · {meta.n_mong} móng "
                     f"· {meta.n_tang} tầng dây  (nguồn: {meta.source})")
    if bad:
        ctx.emit("step", f"{len(bad)} ảnh lỗi/rỗng — bỏ qua")
    for w in meta.warnings:
        ctx.emit("step", f"⚠ {w}")
