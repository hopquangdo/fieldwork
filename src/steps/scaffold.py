"""Fixer cho ``too_few / odd_folders / missing_khac``: mỗi hạng mục cần ≥ min_cong_tac
thư mục ĐƯA VÀO PHỤ LỤC (đi cặp → chẵn) + 1 'Hình ảnh khác', kể cả rỗng. Thư mục mẫu
rỗng bị bỏ khi hạng mục đã đủ. Tên thư mục dựng mới (khác / cặp) theo ``[[subfolders]]``
nếu profile khai báo; số thư mục lẻ xử lý theo ``[structure] odd_fix``. Cấu kiện 1 ảnh (móng, vị trí…) được ghép cặp riêng bởi
:class:`~domain.singleton_pairing.SingletonPairer` trước khi cân bằng tổng.

Nhận diện "thư mục phụ lục" qua ``is_appendix`` (công tác / chuẩn bị / thao tác / đo
kích thước — xem ``[folders] appendix_markers``), KHÔNG phải ``is_cong_tac`` (chỉ
"công tác"/"chuẩn bị"): nếu dùng ``is_cong_tac`` thì "Thao tác trèo cao tại X" hay "Đo
kích thước X" bị coi là 0 thư mục phụ lục → scaffold bịa thêm cặp "Công tác chuẩn bị…
1/2" chồng lên thư mục thật.
"""
from __future__ import annotations

from runtime import node

from domain.issues import SCAFFOLD_KINDS
from domain.profile import Profile
from domain.canonical import CanonicalNamer, natural_key
from domain.folders import hm_of, leaf_of
from domain.singleton_pairing import SingletonPairer
from steps.validate import issues_now
from domain import sections as S
from domain.state import state


@node("scaffold")
def scaffold(ctx) -> None:
    if not any(i.kind in SCAFFOLD_KINDS for i in issues_now(ctx)):
        st = ctx.report.stages[-1]
        st.status = "skipped"
        st.detail = "mọi hạng mục đủ cặp công tác + khác — bỏ qua"
        return

    prof = Profile.of(ctx)
    nm = prof.names()
    canon = CanonicalNamer(prof)
    pairer = SingletonPairer(nm, allowed=canon.allowed)
    assign: dict[str, list[str]] = state(ctx).assign
    existing: set[str] = state(ctx).existing_dirs

    hms = sorted({hm_of(k) for k in assign if k[:1].isdigit()})
    created = 0
    for hm in hms:
        if nm.is_kept(hm):
            continue
        base = nm.hm_base(hm)
        keys = [k for k in assign if hm_of(k) == hm]

        if canon.spec_for(hm) is None:        # hạng mục có [[subfolders]]: canonicalize đã ghép cặp
            created += pairer.pair_all(assign, hm, keys)

        keys = [k for k in assign if hm_of(k) == hm]
        ct_full = [k for k in keys if nm.is_appendix(leaf_of(k)) and assign[k]]
        has_khac = any(nm.is_khac(leaf_of(k)) for k in keys)

        # 1. 'Hình ảnh khác'
        if not has_khac:
            ck = canon.khac_name(hm)
            k = f"{hm}/{ck}" if ck else nm.khac_folder(assign, hm, existing=existing, base=base)
            assign.setdefault(k, [])
            created += 1

        ct = list(ct_full)
        if len(ct) >= 2 and (len(ct) % 2 == 0 or nm.odd_ok(hm)):
            continue

        for d in existing:
            if (hm_of(d) == hm and d.count("/") == 1 and nm.is_appendix(leaf_of(d))
                    and canon.allowed(hm, leaf_of(d))):
                assign.setdefault(d, [])
        ct = [k for k in assign if hm_of(k) == hm and nm.is_appendix(leaf_of(k))]

        while len(ct) < 2:
            k = f"{hm}/{nm.prep_folder(f'{base} {len(ct) + 1}')}"
            assign.setdefault(k, [])
            ct.append(k)
            created += 1

        if len(ct) % 2 == 1 and not nm.odd_ok(hm):
            empties = [k for k in ct if not assign[k]]
            sib = _empty_sibling(nm, canon, assign, hm, ct) if prof.structure.odd_fix == "sibling" else None
            if sib:
                assign[sib] = []
                ct.append(sib)
            elif empties:
                assign.pop(empties[-1])
                ct.remove(empties[-1])
            else:
                biggest = max(ct, key=lambda k: len(assign[k]))
                la, lb = nm.pair(nm.pair_core(leaf_of(biggest)))
                if not (canon.allowed(hm, la) and canon.allowed(hm, lb)):
                    # tên cặp không có trong [[subfolders]] — không tự chế, để người xem
                    ctx.report.sections.setdefault(S.NEEDS_REVIEW, []).append(
                        f"{hm}: {len(ct)} thư mục phụ lục (lẻ) — không có tên chuẩn để tách cặp")
                    continue
                imgs = assign.pop(biggest)
                ct.remove(biggest)
                half = (len(imgs) + 1) // 2
                a, b = f"{hm}/{la}", f"{hm}/{lb}"
                assign[a], assign[b] = imgs[:half], imgs[half:]
                ct += [a, b]
            created += 1

    ctx.report.stages[-1].detail = f"chỉnh {created} thư mục khung"


def _empty_sibling(nm, canon, assign: dict, hm: str, ct: list[str]) -> str | None:
    """``odd_fix = "sibling"``: thư mục cặp RỖNG (tên chuẩn) cho thư mục phụ lục CUỐI
    (sắp tự nhiên) có ảnh — vd "…đốt 7" → "Công tác kiểm tra … đốt 7". Không có → None."""
    for k in sorted((k for k in ct if assign.get(k)), key=natural_key, reverse=True):
        sib = nm.sibling_leaf(leaf_of(k))
        if sib and f"{hm}/{sib}" not in assign and canon.allowed(hm, sib):
            return f"{hm}/{sib}"
    return None
