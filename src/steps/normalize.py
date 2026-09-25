"""Chuẩn hoá SỐ/TÊN hạng mục input về đúng danh mục ``[hang_muc]`` của profile.

Xử lý trường hợp thư mục input đánh số theo LOẠI CỘT KHÁC với profile đang chạy (vd
input 10 hạng mục dây co, chạy profile tự đứng 8 hạng mục) — nếu không có bước này,
số hạng mục input và số profile lệch nhau → ``scaffold``/``dot_range`` dựng nhầm thư
mục (trùng số, lồng chéo).

Deterministic, không gọi LLM: khớp tên qua :class:`HangMucMatcher`. Hạng mục không
map được (không đủ tin cậy) → GIỮ NGUYÊN + để ``agent_repair`` xử lý sau. Chạy ngay
sau ``scan``.
"""
from __future__ import annotations

import re

from runtime import node

from domain.profile import Profile
from domain.folders import hm_of
from domain.hang_muc import HangMucMatcher

_NUM = re.compile(r"^\s*\d+\s*[.\-_ ]\s*")


@node("normalize")
def normalize(ctx) -> None:
    prof = Profile.of(ctx)
    hang_muc = prof.hang_muc
    if not hang_muc:
        ctx.report.stages[-1].status = "skipped"
        ctx.report.stages[-1].detail = "profile không khai [hang_muc] — bỏ qua"
        return

    matcher = HangMucMatcher(hang_muc, prof.hang_muc_alias)
    assign: dict[str, list[str]] = ctx.data["assign"]
    remap: dict[str, str] = {}
    for hm in sorted({hm_of(k) for k in assign if k[:1].isdigit()}):
        name = _NUM.sub("", hm)
        canon_num, drop = matcher.match(name)
        if drop:
            remap[hm] = ""
        elif canon_num is not None:
            canon = f"{canon_num}.{hang_muc[canon_num]}"
            if canon != hm:
                remap[hm] = canon
        # không map được (điểm thấp) → giữ nguyên, không thêm vào remap

    if not remap:
        ctx.report.stages[-1].status = "skipped"
        ctx.report.stages[-1].detail = "đánh số hạng mục đã khớp profile"
        return

    new_assign: dict[str, list[str]] = {}
    moved_drop = renamed = 0
    for k, photos in assign.items():
        hm = hm_of(k)
        target_hm = remap.get(hm, hm)
        if target_hm == hm:
            new_assign.setdefault(k, []).extend(photos)
        elif target_hm == "":
            new_assign.setdefault("", []).extend(photos)
            moved_drop += len(photos)
        else:
            new_assign.setdefault(target_hm + k[len(hm):], []).extend(photos)
            renamed += 1

    ctx.data["assign"] = new_assign
    # thư mục trên đĩa đã đổi tên trong assign — existing_dirs/hm_dirs lấy lại theo
    # trạng thái mới (best-effort; scaffold/apply tự dựng thư mục mới nếu chưa có).
    ctx.data["existing_dirs"] = {k.rsplit("/", 1)[0] for k in new_assign if "/" in k}
    ctx.data["hm_dirs"] = {num: f"{num}.{name}" for num, name in hang_muc.items()}

    detail = []
    if renamed:
        detail.append(f"đổi số {len(remap) - (1 if moved_drop else 0)} hạng mục")
    if moved_drop:
        detail.append(f"{moved_drop} ảnh (hạng mục ngoài profile) → chờ xếp lại")
    ctx.report.stages[-1].detail = "; ".join(detail) or "không đổi"
    for old, new in sorted(remap.items()):
        ctx.emit("step", f"{old} → {new or '(chưa xếp — nhặt lại theo rule)'}")
