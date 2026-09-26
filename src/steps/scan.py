"""Ingest: nạp một trạm vào ``ctx`` để các bước sau xử lý.

Định vị thư mục ảnh, copy nó (chỉ nó) sang output, kiểm kê từng ảnh và
đọc số liệu TABLEBia. Sau bước này ``ctx.data`` có:

    root          thư mục chứa các hạng mục đánh số
    photos        list[Photo] — mọi ảnh mở được
    assign        {thư mục hiện tại: [ảnh]} — vị trí THÔ ban đầu
    existing_dirs mọi thư mục có sẵn trên đĩa
    (ảnh trong bản sao LỒNG của trạm / trùng nội dung bị loại theo ``[scan]`` — xem
    :mod:`domain.intake`; loại cả khỏi bản làm việc, input không đổi)
    hm_dirs       {số hạng mục: tên thư mục thực tế}
    meta          StationMeta (loại cột, số đốt/móng/tầng)
"""
from __future__ import annotations

from infrastructure.filesystem import CopyTreeTool, RemoveTreeTool, WalkDirsTool, WalkFilesTool
from runtime import node

copy_tree, remove_tree = CopyTreeTool(), RemoveTreeTool()
walk_dirs, walk_files = WalkDirsTool(), WalkFilesTool()

from domain.models import Photo
from domain.profile import Profile
from domain.intake import survey
from domain.metadata import read_meta, refine_tower_type
from domain.naming import parse
from domain.station import hang_muc_dirs, image_root, is_broken_image
from domain import sections as S
from domain.state import state


def _copy_station(ctx, src_root):
    """Bản làm việc trong output — chỉ copy thư mục ảnh, không mang Data hay tầng bọc theo."""
    work = ctx.output / src_root.name
    if ctx.journal.done("__copied__"):
        ctx.report.stages[-1].detail = "resume (copy skipped) · "
    else:
        remove_tree(work)
        n = copy_tree(src_root, work)
        ctx.journal.record("__copied__", files=n)
        ctx.report.stages[-1].detail = f"copied {n} file · "
    return work


@node("scan")
def scan(ctx) -> None:
    i, o = ctx.input.resolve(), ctx.output.resolve()
    if o == i or i in o.parents or o in i.parents:
        ctx.report.abort("output không được trùng / nằm trong / chứa input")
        return

    prof = Profile.of(ctx)
    fn = prof.filename
    src_root = image_root(ctx.input)
    intake = survey(src_root, prof.scan)
    work = root = _copy_station(ctx, src_root)
    dropped = {d for d, _ in intake.duplicates}
    _drop_from_copy(work, intake.skip_dirs, dropped)
    state(ctx).root = root
    state(ctx).hm_dirs = hang_muc_dirs(root)
    _report_intake(ctx, intake)

    photos: list[Photo] = []
    bad: list[str] = []
    for p in walk_files(root, images_only=True):
        rel = str(p.relative_to(root)).replace("\\", "/")
        if intake.skipped(rel) or rel in dropped:
            continue
        if is_broken_image(p):
            bad.append(rel)
            continue
        c = parse(p.name, ts_pattern=fn.ts_pattern, primary_marker=fn.primary_marker)
        photos.append(Photo(path=rel, prefix=c.prefix, is_primary=c.is_primary))

    state(ctx).photos = photos
    state(ctx).assign = _raw_assign(photos, prof)
    state(ctx).existing_dirs = {
        rel for d in walk_dirs(root)
        if not intake.skipped(rel := str(d.relative_to(root)).replace("\\", "/"))
    }
    if bad:
        ctx.report.sections[S.BAD_IMAGES] = bad

    meta = read_meta(ctx.input, prof.metadata)
    refined, why = refine_tower_type(src_root, meta.tower_type, prof.tower_evidence,
                                     skip=intake.skipped)
    if refined != meta.tower_type:
        meta.warnings.append(f"TABLEBia = '{meta.tower_type}' nhưng ảnh cho thấy '{refined}' ({why})")
        meta.tower_type = refined
    state(ctx).meta = meta
    if meta.tower_type != prof.tower_type:
        meta.warnings.append(
            f"TABLEBia = '{meta.tower_type}' nhưng profile = '{prof.tower_type}' — kiểm tra lại."
        )
    ctx.report.sections[S.META] = {
        "tower_type": meta.tower_type, "n_dot": meta.n_dot,
        "n_mong": meta.n_mong, "n_tang": meta.n_tang, "source": meta.source,
    }
    ctx.report.errors.extend(f"scan: {w}" for w in meta.warnings)
    if not meta.resolved:
        ctx.report.abort(
            "không xác định được loại cột từ TABLEBia — kiểm tra thư mục Data "
            "(cạnh hoặc trong thư mục trạm) rồi chạy lại"
        )
        return
    ctx.report.sections[S.IMAGES_BEFORE] = len(photos)
    ctx.report.stages[-1].detail += f"{len(photos)} ảnh · {meta.tower_type}"

    ctx.emit("step", f"cột {meta.tower_type} · {meta.n_dot} đốt · {meta.n_mong} móng "
                     f"· {meta.n_tang} tầng dây  (nguồn: {meta.source})")
    if bad:
        ctx.emit("step", f"{len(bad)} ảnh lỗi/rỗng — bỏ qua")
    for w in meta.warnings:
        ctx.emit("step", f"⚠ {w}")


def _drop_from_copy(work, skip_dirs: list[str], dropped: set[str]) -> None:
    """Gỡ khỏi BẢN LÀM VIỆC (output) các thư mục bỏ qua + bản ảnh trùng. Input không đổi."""
    from infrastructure.filesystem import longpath

    for d in skip_dirs:
        remove_tree(work / d)
    for rel in dropped:
        f = longpath(work / rel)
        if f.exists():
            f.unlink()


def _report_intake(ctx, intake) -> None:
    if intake.skip_dirs:
        ctx.report.sections[S.SKIPPED_DIRS] = list(intake.skip_dirs)
        ctx.emit("step", f"bỏ qua {len(intake.skip_dirs)} thư mục: {', '.join(intake.skip_dirs[:3])}")
    if intake.duplicates:
        ctx.report.sections[S.DUPLICATES] = [
            f"{d}  (trùng {k})" for d, k in intake.duplicates
        ]
        ctx.emit("step", f"bỏ qua {len(intake.duplicates)} ảnh trùng nội dung")


def _raw_assign(photos: list[Photo], prof: Profile) -> dict[str, list[str]]:
    """Vị trí thô: mỗi ảnh nằm ở đúng thư mục đang chứa nó. ``check`` đọc bản này;
    ``classify`` chỉ ghi đè khi nó thực sự chạy."""
    khac = prof.folders.khac_name
    out: dict[str, list[str]] = {}
    for p in photos:
        out.setdefault(p.folder or khac, []).append(p.path)
    return out
