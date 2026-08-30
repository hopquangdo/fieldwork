"""HARD invariant: assignment covers every photo once; no (folder, final name) clash.
Also reports (soft) hạng mục whose 'công tác' folders are all empty — SOP: BÁO người dùng."""
from __future__ import annotations

from collections import Counter

from graphrun import node

from photo_sort.domain.folders import hm_of, is_cong_tac, is_khac, leaf_of


@node("verify")
def conservation(ctx) -> None:
    photos = {p.path for p in ctx.data["photos"]}
    assign = ctx.data["assign"]
    assigned = [p for paths in assign.values() for p in paths]

    dup = [p for p, c in Counter(assigned).items() if c > 1]
    if dup:
        ctx.report.abort(f"{len(dup)} ảnh bị gán nhiều lần: {dup[:3]}")
        return
    if set(assigned) != photos:
        lost, extra = photos - set(assigned), set(assigned) - photos
        ctx.report.abort(f"assignment lệch: mất {len(lost)}, thừa {len(extra)} — {sorted(lost | extra)[:3]}")
        return

    clash = [k for k, c in Counter(ctx.data["landing"]).items() if c > 1]
    if clash:
        ctx.report.abort(f"{len(clash)} cặp (thư mục, tên file) trùng: {clash[:3]}")
        return

    # --- soft: hạng mục thiếu ảnh --------------------------------------------
    keep = ctx.config.get("keep_as_is", ["1.", "10."])
    by_hm: dict[str, int] = {}
    khac_only: dict[str, int] = {}
    for folder, imgs in assign.items():
        if not folder[:1].isdigit():
            continue
        hm = hm_of(folder)
        if any(hm.startswith(k) for k in keep):
            continue
        if is_cong_tac(leaf_of(folder)):
            by_hm[hm] = by_hm.get(hm, 0) + len(imgs)
        elif is_khac(leaf_of(folder)):
            khac_only[hm] = khac_only.get(hm, 0) + len(imgs)
    gaps = sorted(hm for hm in set(by_hm) | set(khac_only) if by_hm.get(hm, 0) == 0)
    if gaps:
        ctx.report.sections["hạng mục thiếu ảnh (cần nhặt bù)"] = [
            f"{hm}  (chỉ có {khac_only.get(hm, 0)} ảnh trong 'Hình ảnh khác')" for hm in gaps
        ]
        for hm in gaps:
            ctx.emit("step", f"⚠ THIẾU ảnh công tác: {hm}")

    ctx.report.stages[-1].detail = f"{len(photos)} ảnh · {len(ctx.data['moves'])} move hợp lệ"
