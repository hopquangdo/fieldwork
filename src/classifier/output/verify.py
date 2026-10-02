"""Bất biến CỨNG trước khi ghi: mỗi ảnh vào đúng 1 lần, không trùng (thư mục, tên)."""
from __future__ import annotations


def verify(photos, moves) -> list[str]:
    errs: list[str] = []
    srcs = [m.src for m in moves]
    if sorted(map(str, srcs)) != sorted(str(p.path) for p in photos):
        errs.append(f"số ảnh: vào {len(photos)} ≠ kế hoạch {len(moves)}")
    seen: set[tuple[str, str]] = set()
    for m in moves:
        k = (m.folder.casefold(), m.name.casefold())
        if k in seen:
            errs.append(f"trùng đích: {m.folder}/{m.name}")
        seen.add(k)
    return errs
