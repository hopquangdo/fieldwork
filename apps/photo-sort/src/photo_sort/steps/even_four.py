"""Fixer cho issue ``odd_images`` / ``too_many``: mỗi thư mục 'công tác' giữ số ảnh
CHẴN và ≤ ``prefer_images``; ảnh dư tràn sang 'Hình ảnh khác' của hạng mục đó.

Bỏ qua: 'khác', hạng mục ``keep_as_is``, thư mục ``even_skip`` (siêu âm thanh cánh —
SOP: giữ nguyên). Hạng mục trong ``even_no_trim``: chỉ ép chẵn, không cắt còn 4.
"""
from __future__ import annotations

from graphrun import node

from photo_sort.domain.folders import hm_of, is_cong_tac, is_khac, khac_folder, leaf_of
from photo_sort.issues import EVEN_KINDS
from photo_sort.steps.validate import structural_issues

_SKIP = ["siêu âm", "sieu am"]


def _trim(imgs: list[str], cap: int) -> tuple[list[str], list[str]]:
    """(giữ, dư) — ưu tiên giữ ảnh chính (--1--), số giữ luôn CHẴN và ≤ cap."""
    ordered = sorted(imgs, key=lambda p: ("--1--" not in p, p))
    n = min(cap, len(ordered))
    if n % 2:
        n -= 1
    return ordered[:n], ordered[n:]


@node("even_four")
def even_four(ctx) -> None:
    if not any(i.kind in EVEN_KINDS for i in structural_issues(ctx)):
        st = ctx.report.stages[-1]
        st.status = "skipped"
        st.detail = "thư mục công tác đã chẵn ≤ mức ưu tiên — bỏ qua"
        return

    prefer = int(ctx.config.get("prefer_images", 4))
    keep_hm = ctx.config.get("keep_as_is", ["1.", "10."])
    no_trim = ctx.config.get("even_no_trim", ["9."])
    skip = ctx.config.get("even_skip", _SKIP)
    assign = ctx.data["assign"]
    existing = ctx.data.get("existing_dirs", set())
    moved = 0

    for folder in list(assign):
        leaf = leaf_of(folder).casefold()
        if is_khac(leaf_of(folder)) or any(folder.startswith(k) for k in keep_hm):
            continue
        if any(s.casefold() in leaf for s in skip):
            continue
        if not (is_cong_tac(leaf_of(folder)) or leaf.startswith("đo kích thước")
                or leaf.startswith("do kich thuoc") or "thao tác" in leaf):
            continue                       # chỉ ép chẵn các thư mục ĐƯA VÀO PHỤ LỤC

        imgs = assign[folder]
        cap = 10_000 if any(folder.startswith(k) for k in no_trim) else prefer
        if len(imgs) % 2 == 0 and len(imgs) <= cap:
            continue
        keep, surplus = _trim(imgs, cap)
        assign[folder] = keep
        khac = khac_folder(assign, hm_of(folder), existing=existing)
        assign.setdefault(khac, []).extend(surplus)
        moved += len(surplus)

    ctx.report.stages[-1].detail = f"đẩy {moved} ảnh dư sang 'Hình ảnh khác'"
