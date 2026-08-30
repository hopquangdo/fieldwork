"""Diagnose SOP violations over the current assignment -> ctx.data["issues"].

Two nodes share one implementation:

* ``check`` (baseline, right after scan) — full issue set incl. classification
  problems (unclassified / misplaced / dot_range / too_many). Never gates; writes
  the "vấn đề đầu vào" report. The deterministic fixers gate on this list.
* ``validate`` (before plan, loops with agent_repair) — structural invariants only,
  recomputed fresh each iteration so the loop terminates.
"""
from __future__ import annotations

import re

from graphrun import node

from photo_sort.domain.folders import hm_of, is_cong_tac, is_khac, leaf_of
from photo_sort.domain.matching import match_photo
from photo_sort.issues import Issue

_D_TAIL = re.compile(r"\bD(\d+)\s*$")


def _per_dot(assign: dict, prefix: str) -> set[int]:
    """Số đốt của các thư mục công-tác per-đốt (…D1, …D2) dưới hạng mục ``prefix``."""
    return {
        int(m[1]) for k in assign
        if k.startswith(prefix) and not is_khac(leaf_of(k)) and (m := _D_TAIL.search(leaf_of(k)))
    }


@node("check")
def check(ctx) -> None:
    issues = _collect(ctx, baseline=True)
    ctx.data["issues"] = issues
    ctx.data.setdefault("repair_iters", 0)
    st = ctx.report.stages[-1]
    st.detail = "đầu vào đạt chuẩn" if not issues else f"{len(issues)} vấn đề đầu vào"
    if issues:
        ctx.report.sections["vấn đề đầu vào"] = [
            f"{i.hm} · {i.kind} · {i.detail}" for i in issues
        ]
        _emit_summary(ctx, issues)


@node("validate")
def validate(ctx) -> None:
    issues = _collect(ctx, baseline=False)
    ctx.data["issues"] = issues
    ctx.data["repair_iters"] = ctx.data.get("repair_iters", 0)
    st = ctx.report.stages[-1]
    st.detail = "hợp lệ" if not issues else f"{len(issues)} vấn đề → repair"
    if issues:
        ctx.report.sections["issues (vòng {})".format(ctx.data["repair_iters"])] = [
            f"{i.hm} · {i.kind} · {i.detail}" for i in issues
        ]
        _emit_summary(ctx, issues)
    else:
        ctx.emit("step", "cấu trúc đạt chuẩn cặp/chẵn/khác")


def structural_issues(ctx) -> list[Issue]:
    """Current-state SOP violations over công-tác folders (no classification checks).
    Fixers call this to decide whether they have anything to do *right now*."""
    return _collect(ctx, baseline=False)


def dot_range_pending(ctx) -> bool:
    """True nếu còn hạng mục ``[[dot_range]]`` nào có ≥2 thư mục công-tác per-đốt."""
    assign = ctx.data["assign"]
    return any(
        len(_per_dot(assign, spec["hm_prefix"])) >= 2
        for spec in ctx.config.get("dot_range", [])
    )


def _emit_summary(ctx, issues: list[Issue]) -> None:
    by_hm: dict[str, int] = {}
    for i in issues:
        by_hm[i.hm] = by_hm.get(i.hm, 0) + 1
    for hm, n in sorted(by_hm.items()):
        ctx.emit("step", f"{hm}: {n} vấn đề")


def _collect(ctx, *, baseline: bool) -> list[Issue]:
    keep = ctx.config.get("keep_as_is", ["1.", "10."])
    skip = ctx.config.get("even_skip", ["siêu âm", "sieu am"])
    prefer = int(ctx.config.get("prefer_images", 4))
    no_trim = ctx.config.get("even_no_trim", ["9."])
    assign: dict[str, list[str]] = ctx.data["assign"]

    issues: list[Issue] = []

    # ── structural invariants over công-tác folders ─────────────────────
    per_hm: dict[str, list[str]] = {}
    for f in assign:
        if f[:1].isdigit():
            per_hm.setdefault(hm_of(f), []).append(f)

    for hm, folders in sorted(per_hm.items()):
        if any(hm.startswith(k) for k in keep):
            continue
        ct = [f for f in folders if is_cong_tac(leaf_of(f))]
        if len(ct) < 2:
            issues.append(Issue(hm, "too_few", f"{len(ct)} thư mục công tác (cần ≥2)"))
        elif len(ct) % 2:
            issues.append(Issue(hm, "odd_folders", f"{len(ct)} thư mục công tác — lẻ"))
        if not any(is_khac(leaf_of(f)) for f in folders):
            issues.append(Issue(hm, "missing_khac", "thiếu 'Hình ảnh khác'"))
        for f in ct:
            if any(s.casefold() in leaf_of(f).casefold() for s in skip):
                continue
            n = len(assign[f])
            if n % 2:
                issues.append(Issue(hm, "odd_images", f"{leaf_of(f)}: {n} ảnh — lẻ", folder=f))
            elif n > prefer and not any(hm.startswith(k) for k in no_trim):
                issues.append(Issue(hm, "too_many", f"{leaf_of(f)}: {n} ảnh (>{prefer})", folder=f))

    if not baseline:
        return issues

    # ── classification problems (baseline only) ─────────────────────────
    rules = ctx.config.get("rule", [])
    hm_dirs: dict = ctx.data.get("hm_dirs", {})
    where = {p: f for f, ps in assign.items() for p in ps}
    n_unclassified = n_misplaced = 0
    for photo in ctx.data.get("photos", []):
        cur = where.get(photo.path, "")
        if is_khac(leaf_of(cur)):
            continue
        if "/" not in cur:
            n_unclassified += 1
            if n_unclassified <= 8:
                issues.append(Issue("(ảnh)", "unclassified", f"{photo.name}  (ở '{cur or '/'}')"))
            continue
        target, is_soft = match_photo(photo, rules, hm_dirs)
        if target and "/" in target and target != cur:
            n_misplaced += 1
            if n_misplaced <= 8:
                tail = " (lỏng)" if is_soft else ""
                issues.append(Issue(hm_of(target), "misplaced", f"{photo.name}: {cur} → {target}{tail}"))
    if n_unclassified > 8:
        issues.append(Issue("(ảnh)", "unclassified", f"… +{n_unclassified - 8} ảnh nữa"))
    if n_misplaced > 8:
        issues.append(Issue("(ảnh)", "misplaced", f"… +{n_misplaced - 8} ảnh nữa"))

    # ── Mục 2 per-đốt folders that should collapse ──────────────────────
    for spec in ctx.config.get("dot_range", []):
        dots = _per_dot(assign, spec["hm_prefix"])
        if len(dots) >= 2:
            issues.append(Issue(spec["hm_prefix"].rstrip("/"), "dot_range",
                                f"{len(dots)} thư mục theo đốt → gộp cực trị"))

    return issues
