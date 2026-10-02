"""Quyết định → danh sách Move (thư mục đích + tên mới theo ``[filename].build``).

Ảnh vào thư mục công tác được đổi tên ``Nội dung@giờ@phút@giây@--1/0--.jpg`` (nội dung
theo ``[[naming]]``; ảnh đầu mỗi thư mục là ``--1--``). Ảnh ở 'khác' giữ tên gốc — trừ đầu
vào PHẲNG (``rename_khac``): tên gốc vô nghĩa (Zalo) nên cũng đổi. Thiếu giờ chụp → giữ tên gốc.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from domain.filename import build_name, content_name


@dataclass
class Move:
    src: Path
    folder: str              # tương đối trong trạm output
    name: str


def plan(photos, decisions, prof, *, rename_khac: bool = False) -> list[Move]:
    nm, fn = prof.names(), prof.filename
    mk = dict(fmt=fn.build, primary_yes=fn.primary_yes, primary_no=fn.primary_no)
    by_folder: dict[str, list] = {}
    for p in photos:
        by_folder.setdefault(decisions[p.id].folder, []).append(p)
    moves: list[Move] = []
    for folder, ps in by_folder.items():
        leaf = folder.rsplit("/", 1)[-1]
        rename = rename_khac or not nm.is_khac(leaf)
        content = content_name(leaf, prof.naming, strip_prefixes=prof.folders.strip_prefixes,
                               trail_re=nm.trail_regex(), relabel=nm.trail_label)
        content = content[:1].upper() + content[1:]
        used: set[str] = set()
        ps = sorted(ps, key=lambda p: (p.taken_at is None, p.taken_at or (0, 0, 0), p.order))
        for i, p in enumerate(ps):
            name = p.name
            if rename and p.taken_at is not None:
                ext = fn.ext if p.path.suffix.lower() in (".jpg", ".jpeg") else p.path.suffix.lower()
                seq = 0
                name = build_name(content, p.taken_at, primary=i == 0, ext=ext, **mk)
                while name.casefold() in used:
                    seq += 1
                    name = build_name(content, p.taken_at, primary=i == 0, ext=ext, seq=seq, **mk)
            stem, dot, ext = name.rpartition(".")
            k = 2
            while name.casefold() in used:
                name = f"{stem} ({k}).{ext}" if dot else f"{name} ({k})"
                k += 1
            used.add(name.casefold())
            moves.append(Move(p.path, folder, name))
    return moves
