"""LLM fallback — runs AFTER classify. For photos rules couldn't place (+ timestamp-only /
.png / blueprint-suspect): ask a vision model, accept only if the folder is a real
candidate and confidence >= vision.min_conf. Cached across runs. Needs LLM_API_KEY.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from fs_tools import image_block, load_image_b64, longpath
from graphrun import node
from pydantic import BaseModel

from photo_sort.domain.naming import looks_like_blueprint
from photo_sort.llm import available, chat_model


class _Ans(BaseModel):
    path: str
    folder: str | None = None
    is_blueprint: bool = False
    confidence: float = 0.0


class _Batch(BaseModel):
    answers: list[_Ans]

_PROMPT = (
    "Bạn phân loại ảnh kiểm định cột BTS. Với mỗi ảnh (kèm đường dẫn hiện tại): "
    "chọn 'folder' đúng nhất trong danh sách 'folders' (null nếu không hợp), kèm 'confidence' 0-1. "
    "Đặt is_blueprint=true nếu ảnh là BẢN VẼ TAY chụp trang giấy: nền trắng, nét bút vẽ "
    "cột / mặt cắt / kích thước, thường ghi mã trạm + chiều cao đốt."
)


def _key(path: Path) -> str:
    size = os.path.getsize(longpath(path))
    return hashlib.sha1(f"{Path(path).name}|{size}".encode()).hexdigest()[:16]


def _valid_targets(config) -> set[str]:
    out = set(config.get("vision.candidates", []))
    for r in config.get("rule", []):
        t = r.get("target", "")
        if t and t != "{keep}":
            out.add(t.replace(" {group}", "").replace("{group}", "").strip())
    return out


@node("vision", soft=True)   # LLM fallback — never aborts the pipeline
def vision(ctx) -> None:
    st = ctx.report.stages[-1]
    if not available():
        st.status = "skipped"
        st.detail = "không có LLM_API_KEY"
        return

    min_conf = float(ctx.config.get("vision.min_conf", 0.6))
    bp_folder = ctx.config.get("vision.blueprint_folder")
    limit = int(ctx.config.get("vision.max", 120))

    unmatched = {p.path for p in ctx.data.get("unmatched", [])}
    targets = [
        p for p in ctx.data["photos"]
        if p.path in unmatched or not p.prefix or looks_like_blueprint(p.prefix)
        or p.name.lower().endswith(".png")
    ][:limit]
    if not targets:
        st.detail = "không có ảnh cần mở"
        return

    valid = _valid_targets(ctx.config)
    folders = ctx.config.get("vision.candidates") or sorted(valid)
    root = Path(ctx.data["root"])
    cache_path = Path(ctx.journal.path).parent / "vision-cache.json"
    cache: dict = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}

    todo = [p for p in targets if _key(root / p.path) not in cache]
    if todo:
        try:
            llm = chat_model().with_structured_output(_Batch)
            content: list = [{"type": "text", "text": _PROMPT + "\nfolders:\n- " + "\n- ".join(folders)}]
            for p in todo:
                data, mime = load_image_b64(root / p.path, max_edge=1024)
                content.append({"type": "text", "text": p.path})
                content.append(image_block(data, mime))
            res = llm.invoke([{"role": "user", "content": content}])

            by_path = {a.path: a for a in res.answers}
            for p in todo:
                a = by_path.get(p.path)
                if a is None:
                    continue
                cache[_key(root / p.path)] = {
                    "folder": a.folder, "is_blueprint": a.is_blueprint, "conf": a.confidence,
                }
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
        except Exception as exc:  # noqa: BLE001
            st.status = "skipped"
            st.detail = f"LLM lỗi: {type(exc).__name__} — dùng cache/heuristic"

    # apply cached answers to the assignment
    assign = ctx.data["assign"]
    where = {p: f for f, ps in assign.items() for p in ps}
    accepted = review = bp = 0
    for p in targets:
        ans = cache.get(_key(root / p.path))
        if not ans:
            continue
        folder = bp_folder if (ans["is_blueprint"] and bp_folder) else ans["folder"]
        if not folder:
            continue
        if folder != bp_folder and (folder not in valid or ans["conf"] < min_conf):
            review += 1
            ctx.report.sections.setdefault("cần người xem", []).append(
                f"{p.path}  → {ans['folder']} (conf {ans['conf']:.2f})"
            )
            continue
        old = where.get(p.path)
        if old and old != folder:
            assign[old].remove(p.path)
            assign.setdefault(folder, []).append(p.path)
            where[p.path] = folder
            accepted += 1
            bp += ans["is_blueprint"]

    st.detail = (st.detail or "") + f"{accepted} ảnh xếp lại ({bp} bản vẽ) · {review} cần người xem"
