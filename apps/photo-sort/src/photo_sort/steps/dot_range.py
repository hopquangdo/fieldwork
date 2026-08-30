"""Fixer cho issue ``dot_range`` (SOP §2 Mục 2): gộp các thư mục per-đốt
(…D1, …D2, …) thành 2 thư mục cực trị — '…đốt {lo}-{lo+1}' (đốt thấp nhất có ảnh)
+ '…đốt {hi-1}-{hi}' (cao nhất); đốt giữa → 'Hình ảnh khác'.
Cấu hình ``[[dot_range]]`` trong rules TOML.
"""
from __future__ import annotations

import re

from graphrun import node

from photo_sort.domain.folders import hm_of, is_cong_tac, is_khac, khac_folder, leaf_of
from photo_sort.steps.validate import dot_range_pending

_D = re.compile(r"\bD(\d+)\s*$")


@node("dot_range")
def dot_range(ctx) -> None:
    specs = ctx.config.get("dot_range", [])
    if not specs or not dot_range_pending(ctx):
        ctx.report.stages[-1].status = "skipped"
        ctx.report.stages[-1].detail = "không có thư mục theo đốt cần gộp"
        return

    assign: dict[str, list[str]] = ctx.data["assign"]
    done = 0
    for spec in specs:
        hm_prefix = spec["hm_prefix"]
        fmt = spec["target_fmt"]

        per_dot: dict[int, str] = {}
        for k in list(assign):
            if not k.startswith(hm_prefix) or is_khac(leaf_of(k)):
                continue
            m = _D.search(leaf_of(k))
            if m:
                per_dot[int(m[1])] = k
        if len(per_dot) < 2:
            continue

        dots = sorted(per_dot)
        lo, hi = dots[0], dots[-1]
        lo_folder = fmt.format(a=lo, b=lo + 1)
        hi_folder = fmt.format(a=hi - 1, b=hi)
        hm = hm_of(per_dot[lo])
        khac = spec.get("khac") or khac_folder(assign, hm)

        for d, key in per_dot.items():
            imgs = assign.pop(key)
            if d <= lo + 1:
                assign.setdefault(lo_folder, []).extend(imgs)
            elif d >= hi - 1:
                assign.setdefault(hi_folder, []).extend(imgs)
            else:
                assign.setdefault(khac, []).extend(imgs)

        # SOP §2: đúng 2 thư mục — bỏ các thư mục công tác mẫu rỗng còn lại
        for k in [k for k in assign
                  if k.startswith(hm_prefix) and is_cong_tac(leaf_of(k))
                  and k not in (lo_folder, hi_folder) and not assign[k]]:
            assign.pop(k)
        done += 1

    ctx.report.stages[-1].detail = f"gộp {done} hạng mục theo đốt cực trị"
