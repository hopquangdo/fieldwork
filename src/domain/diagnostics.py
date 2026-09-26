"""Phát hiện vi phạm SOP trên một assignment — hàm THUẦN (``assign`` + ``Profile`` →
``list[Issue]``), không ``ctx``.

* ``structural_issues`` — bất biến trên thư mục 'Công tác' (đủ cặp, chẵn ảnh, có 'khác').
  Dùng cho cả chẩn đoán đầu vào lẫn vòng lặp ``validate ↔ agent_repair``.
* ``classification_issues`` — ảnh chưa xếp / xếp sai chỗ (so với rule engine). Chỉ dùng
  ở lần chẩn đoán đầu vào.
* ``dot_range_issues`` — hạng mục còn nhiều thư mục per-đốt cần gộp (SOP §2).
"""
from __future__ import annotations

import re

from domain.issues import Issue
from domain.profile import Names, Profile
from domain.folders import hm_of, leaf_of
from domain.matching import RuleMatcher

_D_TAIL = re.compile(r"\bD(\d+)\s*$")


def per_dot(assign: dict, hm_prefix: str, names: Names) -> set[int]:
    """Số đốt của các thư mục công-tác per-đốt (…D1, …D2) dưới hạng mục ``hm_prefix``."""
    return {
        int(m[1]) for k in assign
        if k.startswith(hm_prefix) and not names.is_khac(leaf_of(k))
        and (m := _D_TAIL.search(leaf_of(k)))
    }


def structural_issues(assign: dict[str, list[str]], prof: Profile) -> list[Issue]:
    nm, s = prof.names(), prof.structure
    per_hm: dict[str, list[str]] = {}
    for f in assign:
        if f[:1].isdigit():
            per_hm.setdefault(hm_of(f), []).append(f)

    issues: list[Issue] = []
    for hm, folders in sorted(per_hm.items()):
        if nm.is_kept(hm):
            continue
        # đếm thư mục ĐƯA VÀO PHỤ LỤC (is_appendix: công tác / chuẩn bị / thao tác / đo kích
        # thước) — cùng tiêu chí với scaffold, nếu không 2 bước "cãi nhau" mãi.
        ct = [f for f in folders if nm.is_appendix(leaf_of(f))]
        if len(ct) < s.min_cong_tac:
            issues.append(Issue(hm, "too_few", f"{len(ct)} thư mục công tác (cần ≥{s.min_cong_tac})"))
        elif s.pair_folders and len(ct) % 2 and not nm.odd_ok(hm):
            issues.append(Issue(hm, "odd_folders", f"{len(ct)} thư mục công tác — lẻ"))
        if s.require_khac and not any(nm.is_khac(leaf_of(f)) for f in folders):
            issues.append(Issue(hm, "missing_khac", "thiếu 'Hình ảnh khác'"))
        for f in ct:
            if nm.is_ultrasound(leaf_of(f)):
                continue
            n = len(assign[f])
            if s.even_images and n % 2 and not nm.is_paired_singleton(assign, hm, f):
                issues.append(Issue(hm, "odd_images", f"{leaf_of(f)}: {n} ảnh — lẻ", folder=f))
            elif s.trim_to_prefer and n > s.prefer_images and not nm.in_no_trim(hm):
                issues.append(Issue(hm, "too_many", f"{leaf_of(f)}: {n} ảnh (>{s.prefer_images})", folder=f))
    return issues


def classification_issues(assign: dict[str, list[str]], photos, hm_dirs: dict, prof: Profile) -> list[Issue]:
    nm = prof.names()
    matcher = RuleMatcher(prof.rules, hm_dirs, nm, nm.ordinal_totals(p.prefix for p in photos))
    where = {p: f for f, ps in assign.items() for p in ps}
    issues: list[Issue] = []
    for photo in photos:
        cur = where.get(photo.path, "")
        if "/" not in cur:                                   # chưa vào thư mục con nào
            issues.append(Issue("(ảnh)", "unclassified", f"{photo.name}  (ở '{cur or '/'}')"))
            continue
        target, soft = matcher.match(photo, current_folder=cur)
        # Ảnh trong 'khác' vẫn được thử khớp rule — chỉ giữ nguyên khi không có rule
        # nào khớp CHẮC CHẮN (from_folder xác nhận); khớp lỏng bị bỏ qua để tránh
        # "hút" nhầm ảnh vốn đã được triage đúng ở nguồn.
        if nm.is_khac(leaf_of(cur)) and soft:
            continue
        if target and "/" in target and target != cur:
            issues.append(Issue(hm_of(target), "misplaced",
                                f"{photo.name}: {cur} → {target}{' (lỏng)' if soft else ''}"))
    return issues


def dot_range_issues(assign: dict[str, list[str]], prof: Profile) -> list[Issue]:
    nm = prof.names()
    out: list[Issue] = []
    for spec in prof.dot_range:
        dots = per_dot(assign, spec["hm_prefix"], nm)
        if len(dots) >= 2:
            out.append(Issue(spec["hm_prefix"].rstrip("/"), "dot_range",
                             f"{len(dots)} thư mục theo đốt → gộp cực trị"))
    return out


def baseline_issues(assign: dict[str, list[str]], photos, hm_dirs: dict, prof: Profile) -> list[Issue]:
    """Toàn bộ vi phạm của đầu vào THÔ (cấu trúc + phân loại + dot_range)."""
    return (structural_issues(assign, prof)
            + classification_issues(assign, photos, hm_dirs, prof)
            + dot_range_issues(assign, prof))
