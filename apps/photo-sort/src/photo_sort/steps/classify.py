"""Fixer cho issue ``unclassified`` / ``misplaced``: rule-match mỗi ảnh → đúng 1
thư mục đích, ghi đè ``ctx.data["assign"]``. Tự bỏ qua nếu đầu vào đã đúng chỗ.

Ưu tiên: rule khớp (from_folder xác nhận) > soft-match (chỉ 1 rule khớp) >
(fallback.target HOẶC giữ nguyên vị trí).
"""
from __future__ import annotations

from graphrun import node

from photo_sort.domain.matching import match_photo
from photo_sort.issues import CLASSIFY_KINDS


@node("classify")
def classify(ctx) -> None:
    if not any(i.kind in CLASSIFY_KINDS for i in ctx.data.get("issues", [])):
        st = ctx.report.stages[-1]
        st.status = "skipped"
        st.detail = "mọi ảnh đã đúng chỗ — bỏ qua"
        return

    rules = ctx.config.get("rule", [])
    hm_dirs: dict = ctx.data.get("hm_dirs", {})
    fallback = ctx.config.get("fallback.target")

    assign: dict[str, list[str]] = {}
    unmatched: list = []
    matched = soft = 0
    for photo in ctx.data["photos"]:
        target, is_soft = match_photo(photo, rules, hm_dirs)
        if target is None:
            target = fallback or photo.folder or "Hình ảnh khác"
            unmatched.append(photo)
        elif is_soft:
            soft += 1
            ctx.report.sections.setdefault("khớp lỏng (from_folder không khớp)", []).append(
                f"{photo.path} → {target}"
            )
        else:
            matched += 1
        assign.setdefault(target, []).append(photo.path)

    ctx.data["assign"] = assign
    ctx.data["unmatched"] = unmatched
    ctx.report.stages[-1].detail = (
        f"{matched} khớp rule" + (f" · {soft} khớp lỏng" if soft else "")
        + f" · {len(unmatched)} chưa xếp / {len(ctx.data['photos'])}"
    )
    for p in unmatched[:5]:
        ctx.emit("step", f"chưa xếp: {p.name}  (giữ ở {p.folder or '/'})")
    if len(unmatched) > 5:
        ctx.emit("step", f"… +{len(unmatched) - 5} ảnh chưa xếp nữa")
