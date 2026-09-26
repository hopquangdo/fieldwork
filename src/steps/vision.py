"""Fixer bằng LLM — chạy sau ``classify``, vét những ảnh rule không xếp được
(tên chỉ có giờ chụp / ảnh .png / nghi bản vẽ).

Chỉ nhận kết quả khi thư mục model chọn nằm trong danh sách hợp lệ VÀ confidence ≥
``vision.min_conf``; còn lại → ghi "cần người xem". Kết quả cache theo trạm nên chạy
lại không tốn thêm request. ``soft=True`` — thiếu key / model lỗi thì bỏ qua.
"""
from __future__ import annotations

import json
from pathlib import Path

from runtime import node

from agent.vision import ask_vision, cache_key
from infrastructure import llm
from domain.profile import Profile
from domain.folders import reverse_assign
from domain import sections as S
from domain.state import state


def _candidate_folders(prof: Profile) -> set[str]:
    """Thư mục model được phép chọn: từ ``[vision].candidates`` + mọi ``target`` của rule."""
    out = set(prof.vision.get("candidates", []))
    for r in prof.rules:
        t = r.get("target", "")
        if t and t != "{keep}" and "{group}" not in t:     # mẫu còn biến = tên dở, không hợp lệ
            out.add(t)
    return out


def _needs_eyes(p, where: dict, unplaced: set, nm, recheck: list[str]) -> bool:
    """Ảnh cần mở: nghi bản vẽ / .png, hoặc chưa xếp được mà đang ở 'khác' / ngoài hạng
    mục. Ảnh chỉ có giờ chụp nhưng ĐANG nằm trong thư mục cụ thể (không phải 'khác')
    thì vị trí thô đó là bằng chứng — giữ nguyên, trừ hạng mục ``[vision].recheck_in``."""
    if nm.looks_like_blueprint(p.prefix) or p.name.lower().endswith(".png"):
        return True
    if p.path not in unplaced and p.prefix:
        return False
    cur = where.get(p.path, p.folder)
    if "/" not in cur or nm.is_khac(cur.rsplit("/", 1)[-1]):
        return True
    return any(k.casefold() in cur.casefold() for k in recheck)


@node("vision", soft=True)
def vision(ctx) -> None:
    st = ctx.report.stages[-1]
    prof = Profile.of(ctx)
    nm = prof.names()
    min_conf = float(prof.vision.get("min_conf", 0.6))
    bp_folder = prof.vision.get("blueprint_folder")
    limit = int(prof.vision.get("max", 120))

    unplaced = {p.path for p in state(ctx).unmatched}
    recheck = list(prof.vision.get("recheck_in", []))
    where0 = reverse_assign(state(ctx).assign)
    targets = [p for p in state(ctx).photos
               if _needs_eyes(p, where0, unplaced, nm, recheck)][:limit]
    if not targets:
        st.detail = "không có ảnh cần mở"
        return

    valid = _candidate_folders(prof)
    folders = list(prof.vision.get("candidates") or sorted(valid))
    root = Path(state(ctx).root)
    cache_path = Path(ctx.journal.path).parent / "vision-cache.json"
    cache: dict = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}

    todo = [p for p in targets if cache_key(root / p.path) not in cache]
    if todo:
        try:
            try:
                answers = ask_vision([p.path for p in todo], root=root, folders=folders,
                                     config=llm.tracked(ctx, llm.model()),
                                     blueprint_hint=prof.vision.get("blueprint_hint", ""))
            finally:
                llm.publish_usage(ctx)
            for p in todo:
                a = answers.get(p.path)
                if a is not None:
                    cache[cache_key(root / p.path)] = {
                        "folder": a.folder, "is_blueprint": a.is_blueprint, "conf": a.confidence,
                    }
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
        except Exception as exc:  # noqa: BLE001
            st.status = "skipped"
            st.detail = f"LLM lỗi: {type(exc).__name__} — dùng cache/heuristic"

    assign = state(ctx).assign
    where = reverse_assign(assign)
    accepted = review = blueprints = 0
    for p in targets:
        ans = cache.get(cache_key(root / p.path))
        if not ans:
            continue
        folder = bp_folder if (ans["is_blueprint"] and bp_folder) else ans["folder"]
        if not folder:
            continue
        if folder != bp_folder and (folder not in valid or ans["conf"] < min_conf):
            review += 1
            ctx.report.sections.setdefault(S.NEEDS_REVIEW, []).append(
                f"{p.path}  → {ans['folder']} (conf {ans['conf']:.2f})"
            )
            continue
        old = where.get(p.path)
        if old and old != folder:
            assign[old].remove(p.path)
            assign.setdefault(folder, []).append(p.path)
            where[p.path] = folder
            accepted += 1
            blueprints += ans["is_blueprint"]

    st.detail = (st.detail or "") + f"{accepted} ảnh xếp lại ({blueprints} bản vẽ) · {review} cần người xem"
