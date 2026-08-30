"""SOP: every hạng mục needs ≥2 'Công tác' folders (paired -> even count) + a 'Hình ảnh khác',
even when empty. Empty template folders are dropped when the hạng mục is already well-formed."""
from __future__ import annotations

from graphrun import node

from photo_sort.domain.folders import (
    core_of,
    existing_dir,
    hm_base,
    hm_of,
    is_cong_tac,
    is_khac,
    leaf_of,
)
from photo_sort.issues import SCAFFOLD_KINDS
from photo_sort.steps.validate import structural_issues


@node("scaffold")
def scaffold(ctx) -> None:
    if not any(i.kind in SCAFFOLD_KINDS for i in structural_issues(ctx)):
        st = ctx.report.stages[-1]
        st.status = "skipped"
        st.detail = "mọi hạng mục đủ cặp công tác + khác — bỏ qua"
        return

    keep = ctx.config.get("keep_as_is", ["1.", "10."])
    assign: dict[str, list[str]] = ctx.data["assign"]
    existing: set[str] = ctx.data.get("existing_dirs", set())

    hms = sorted({hm_of(k) for k in assign if k[:1].isdigit()})
    created = 0
    for hm in hms:
        if any(hm.startswith(k) for k in keep):
            continue
        base = hm_base(hm)
        keys = [k for k in assign if hm_of(k) == hm]
        ct_full = [k for k in keys if is_cong_tac(leaf_of(k)) and assign[k]]
        has_khac = any(is_khac(leaf_of(k)) for k in keys)

        # 1. 'Hình ảnh khác'
        if not has_khac:
            assign.setdefault(existing_dir(existing, hm, is_khac) or f"{hm}/Hình ảnh khác {base}", [])
            created += 1

        # already ≥2 non-empty công-tác folders (even) -> nothing to scaffold
        ct = list(ct_full)
        if len(ct) >= 2 and len(ct) % 2 == 0:
            continue

        # pull in the station's existing công-tác folders (empty) to reuse names
        for d in existing:
            if hm_of(d) == hm and d.count("/") == 1 and is_cong_tac(leaf_of(d)):
                assign.setdefault(d, [])
        ct = [k for k in assign if hm_of(k) == hm and is_cong_tac(leaf_of(k))]

        while len(ct) < 2:
            k = f"{hm}/Công tác chuẩn bị {base} {len(ct) + 1}"
            assign.setdefault(k, [])
            ct.append(k)
            created += 1

        if len(ct) % 2 == 1:
            empties = [k for k in ct if not assign[k]]
            if empties:
                assign.pop(empties[-1])
                ct.remove(empties[-1])
            else:
                biggest = max(ct, key=lambda k: len(assign[k]))
                imgs = assign.pop(biggest)
                ct.remove(biggest)
                c = core_of(leaf_of(biggest))
                half = (len(imgs) + 1) // 2
                a, b = f"{hm}/Công tác chuẩn bị {c}", f"{hm}/Công tác đo {c}"
                assign[a], assign[b] = imgs[:half], imgs[half:]
                ct += [a, b]
            created += 1

    ctx.report.stages[-1].detail = f"chỉnh {created} thư mục khung"
