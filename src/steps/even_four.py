"""Fixer cho ``odd_images`` / ``too_many``: mỗi thư mục phụ lục ('công tác' / 'đo kích
thước' / 'thao tác'…) giữ số ảnh CHẴN; ảnh dư tràn sang 'Hình ảnh khác' của hạng mục.
Bỏ qua: 'khác', ``keep_as_is``, ``even_skip`` (siêu âm).

``structure.trim_to_prefer``: false (MẶC ĐỊNH) → giữ FULL ảnh, chỉ ép chẵn. true →
cắt về ``prefer_images`` (ảnh dư sang 'khác'); ``even_no_trim`` vẫn được miễn cắt.
"""
from __future__ import annotations

from runtime import node

from domain.issues import EVEN_KINDS
from domain.profile import Profile
from domain.folders import hm_of, leaf_of
from domain.naming import parse
from steps.validate import issues_now
from domain.state import state


def _trim(imgs: list[str], cap: int, *, info: dict | None = None,
          earliest: bool = False) -> tuple[list[str], list[str]]:
    """(giữ, dư) — số giữ luôn CHẴN và ≤ cap. Thứ tự ưu tiên GIỮ:

    1. ảnh chính (``is_primary``);
    2. ảnh CÙNG prefix với ảnh chính (cùng cấu kiện — ảnh lạc nhóm bị đẩy trước);
    3. ảnh có prefix (ảnh chỉ có giờ chụp ít bằng chứng hơn);
    4. theo giờ chụp: mặc định giữ ảnh SỚM, bỏ ảnh MUỘN; ``earliest`` → ngược lại.

    ``info``: ``{path: (prefix, is_primary, ts)}``; thiếu → chỉ xét tên (tương thích cũ).
    """
    info = info or {}

    def meta(p: str):
        return info.get(p) or ("", "--1--" in p, (0, 0, 0))

    lead = {meta(p)[0] for p in imgs if meta(p)[1] and meta(p)[0]}

    def key(p: str):
        prefix, primary, ts = meta(p)
        order = tuple(-x for x in ts) if earliest else ts
        return (not primary, prefix not in lead if lead else False, not prefix, order, p)

    ordered = sorted(imgs, key=key)
    n = min(cap, len(ordered))
    if n % 2:
        n -= 1
    return ordered[:n], ordered[n:]


@node("even_four")
def even_four(ctx) -> None:
    if not any(i.kind in EVEN_KINDS for i in issues_now(ctx)):
        st = ctx.report.stages[-1]
        st.status = "skipped"
        st.detail = "thư mục công tác đã chẵn ≤ mức ưu tiên — bỏ qua"
        return

    prof = Profile.of(ctx)
    nm = prof.names()
    prefer = prof.structure.prefer_images
    trim = prof.structure.trim_to_prefer
    assign = state(ctx).assign
    existing = state(ctx).existing_dirs
    fn = prof.filename
    info = {}
    for p in state(ctx).photos:
        c = parse(p.name, ts_pattern=fn.ts_pattern, primary_marker=fn.primary_marker)
        info[p.path] = (p.prefix, p.is_primary, c.ts)
    moved = 0

    for folder in list(assign):
        leaf = leaf_of(folder)
        if nm.is_khac(leaf) or nm.is_kept(folder) or nm.is_ultrasound(leaf):
            continue
        if not nm.is_appendix(leaf):
            continue                       # chỉ ép chẵn các thư mục ĐƯA VÀO PHỤ LỤC
        if nm.is_paired_singleton(assign, hm_of(folder), folder):
            continue                       # cấu kiện 1 ảnh, đã ghép cặp với thư mục rỗng — giữ nguyên

        imgs = assign[folder]
        cap = prefer if (trim and not nm.in_no_trim(folder)) else 10_000
        if len(imgs) % 2 == 0 and len(imgs) <= cap:
            continue
        if len(imgs) == 1 and prof.structure.keep_singletons:
            continue                       # SOP TH3: 1 ảnh duy nhất — giữ, không làm rỗng thư mục
        early = any(k.casefold() in folder.casefold() for k in prof.structure.trim_earliest)
        keep, surplus = _trim(imgs, cap, info=info, earliest=early)
        assign[folder] = keep
        khac = nm.khac_folder(assign, hm_of(folder), existing=existing)
        assign.setdefault(khac, []).extend(surplus)
        moved += len(surplus)

    ctx.report.stages[-1].detail = f"đẩy {moved} ảnh dư sang 'Hình ảnh khác'"
