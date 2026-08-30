"""Assignment -> concrete moves. Non-conforming filenames get the SOP name
``<cấu kiện>@h@m@s@--x--.ext`` in their target folder ('khác' folders keep original
names); names stay unique within a folder."""
from __future__ import annotations

from pathlib import Path

from graphrun import node

from photo_sort.domain.folders import is_khac, leaf_of
from photo_sort.domain.renaming import build_name, conforms, content_name, timestamp_of
from photo_sort.models import Move


@node("plan")
def plan(ctx) -> None:
    naming_rules = ctx.config.get("naming", [])
    force_ext = ctx.config.get("rename_ext", ".jpg")
    root = Path(ctx.data["root"])

    moves: list[Move] = []
    landing: list[tuple[str, str]] = []
    renamed = converted = 0

    for target, paths in ctx.data["assign"].items():
        rename_here = not is_khac(leaf_of(target))   # 'khác' = kho, giữ tên gốc
        content = content_name(target.rsplit("/", 1)[-1], naming_rules)
        has_primary = any(conforms(p) and "--1--" in p for p in paths)
        used: set[str] = set()
        first_rename = True

        for p in sorted(paths):
            name = p.rsplit("/", 1)[-1]
            cur = p.rsplit("/", 1)[0] if "/" in p else ""
            src_ext = Path(name).suffix.lower()
            new_name, convert = None, False

            if rename_here and not conforms(name):
                ext = (force_ext or src_ext) or ".jpg"
                convert = ext.lower() in (".jpg", ".jpeg") and src_ext not in (".jpg", ".jpeg")
                ts = timestamp_of(name, root / p)
                primary = first_rename and not has_primary
                cand = build_name(content, ts, primary=primary, ext=ext)
                seq = 1
                while cand in used:
                    cand = build_name(content, ts, primary=primary, ext=ext, seq=seq)
                    seq += 1
                new_name, first_rename = cand, False
                renamed += 1
                converted += convert

            final = new_name or name
            if final in used:                          # keep-name collision -> disambiguate
                stem, ext = final.rsplit(".", 1) if "." in final else (final, "")
                i = 2
                while f"{stem} ({i}).{ext}" in used:
                    i += 1
                new_name = f"{stem} ({i}).{ext}"
                final = new_name

            used.add(final)
            landing.append((target, final))
            if cur != target or (new_name and new_name != name):
                moves.append(Move(p, target, new_name, convert))

    ctx.data["moves"] = moves
    ctx.data["landing"] = landing
    detail = f"{len(moves)} move"
    if renamed:
        detail += f" · đổi tên {renamed}"
    if converted:
        detail += f" · convert→jpg {converted}"
    ctx.report.stages[-1].detail = detail
    ctx.report.sections["plan"] = [
        f"{m.src}  ->  {m.dest_dir}/{m.new_name or m.src.rsplit('/', 1)[-1]}" for m in moves[:50]
    ]
    for m in moves[:6]:
        ctx.emit("step", f"{m.src.rsplit('/', 1)[-1]}  →  {m.dest_dir}")
    if len(moves) > 6:
        ctx.emit("step", f"… +{len(moves) - 6} move nữa (xem 'plan' trong report)")
