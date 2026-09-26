"""Chuyển ``assign`` (đích mong muốn) thành danh sách ``Move`` cụ thể.

Ảnh chưa đúng quy ước tên → đổi theo profile ``[filename].build`` (thư mục 'khác'
giữ tên gốc). ``.png`` → đánh dấu convert JPEG. Tên trùng trong 1 thư mục → thêm
hậu tố. Không đụng đĩa — chỉ tính toán; ``apply`` mới thực thi.
"""
from __future__ import annotations

from pathlib import Path

from runtime import node

from domain.models import Move
from domain.profile import Profile
from domain.capture_time import timestamp_of
from domain.filename import build_name, conforms, content_name
from domain import sections as S
from domain.state import state


@node("plan")
def plan(ctx) -> None:
    prof = Profile.of(ctx)
    nm = prof.names()
    fn = prof.filename
    naming_rules = prof.naming
    force_ext = fn.ext
    strips = prof.folders.strip_prefixes
    trail_re = nm.trail_regex()
    root = Path(state(ctx).root)

    moves: list[Move] = []
    landing: list[tuple[str, str]] = []
    renamed = converted = 0

    for target, paths in state(ctx).assign.items():
        leaf = target.rsplit("/", 1)[-1]
        rename_here = not nm.is_khac(leaf)                        # 'khác' = kho, giữ tên gốc
        content = content_name(leaf, naming_rules, strip_prefixes=strips, trail_re=trail_re,
                               relabel=nm.trail_label)
        has_primary = any(conforms(p, fn.conform) and fn.primary_marker in p for p in paths)
        used: set[str] = set()
        first_rename = True

        for p in sorted(paths):
            name = p.rsplit("/", 1)[-1]
            cur = p.rsplit("/", 1)[0] if "/" in p else ""
            src_ext = Path(name).suffix.lower()
            new_name, convert = None, False

            if rename_here and not conforms(name, fn.conform):
                ext = (force_ext or src_ext) or ".jpg"
                convert = ext.lower() in (".jpg", ".jpeg") and src_ext not in (".jpg", ".jpeg")
                ts = timestamp_of(name, root / p, ts_pattern=fn.ts_pattern,
                                  ts_fallback=fn.ts_fallback, primary_marker=fn.primary_marker)
                primary = first_rename and not has_primary
                mk = dict(fmt=fn.build, primary_yes=fn.primary_yes, primary_no=fn.primary_no)
                cand = build_name(content, ts, primary=primary, ext=ext, **mk)
                seq = 1
                while cand in used:
                    cand = build_name(content, ts, primary=primary, ext=ext, seq=seq, **mk)
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

    state(ctx).moves = moves
    state(ctx).landing = landing
    detail = f"{len(moves)} move"
    if renamed:
        detail += f" · đổi tên {renamed}"
    if converted:
        detail += f" · convert→jpg {converted}"
    ctx.report.stages[-1].detail = detail
    ctx.report.sections[S.PLAN] = [
        f"{m.src}  ->  {m.dest_dir}/{m.new_name or m.src.rsplit('/', 1)[-1]}" for m in moves
    ]
    for m in moves:
        ctx.emit("step", f"{m.src.rsplit('/', 1)[-1]}  →  {m.dest_dir}")
