"""Tool ``look`` cho agent: mở ảnh bằng vision model, gợi ý thư mục con TRONG 1 hạng mục.

Khác bước ``vision`` (chọn trong danh sách ``[vision].candidates`` cố định), ``look`` hỏi
theo đúng các thư mục con HIỆN CÓ của hạng mục agent đang xét — nên sửa được ảnh nằm
nhầm ở 'khác' của bất kỳ hạng mục nào. Không tự áp kết quả: agent đọc gợi ý rồi mới
``reassign``. Kết quả cache theo (ảnh, danh sách thư mục) → chạy lại không tốn request.
Ngân sách số ảnh mỗi lượt chạy: ``[agent].max_look``.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from agent.vision import ask_vision, cache_key
from domain.folders import hm_of, leaf_of, reverse_assign
from infrastructure import llm
from tools.repair import AssignEditor
from domain.state import state


class Looker:
    def __init__(self, ctx, editor: AssignEditor, *, budget: int, blueprint_hint: str = "") -> None:
        self.ctx = ctx
        self.editor = editor
        self.budget = budget
        self.blueprint_hint = blueprint_hint
        self.root = Path(state(ctx).root)
        self.cache_path = Path(ctx.journal.path).parent / "look-cache.json"
        try:
            self.cache: dict = json.loads(self.cache_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self.cache = {}

    def _key(self, path: str, folders: list[str]) -> str:
        sig = hashlib.sha1("\n".join(folders).encode()).hexdigest()[:10]
        return f"{cache_key(self.root / path)}:{sig}"

    def look(self, hang_muc: str, photos: list[str]) -> str:
        hm = self.editor._resolve_hm(hang_muc)
        folders = sorted(k for k in self.editor.assign if hm_of(k) == hm)
        if not folders:
            return f"không có hạng mục '{hang_muc}'"
        where = reverse_assign(self.editor.assign)
        paths, unknown = [], []
        for ref in photos:
            p = self.editor._find_photo(ref)
            (paths if p and hm_of(where[p]) == hm else unknown).append(p or ref)

        todo = [p for p in paths if self._key(p, folders) not in self.cache]
        if len(todo) > self.budget:
            return (f"vượt ngân sách xem ảnh (còn {self.budget}, cần {len(todo)} ảnh chưa xem) "
                    "— chọn ít ảnh hơn, ưu tiên ảnh đáng ngờ nhất")
        if todo:
            try:
                answers = ask_vision(todo, root=self.root, folders=folders,
                                     config=llm.tracked(self.ctx, llm.model()),
                                     blueprint_hint=self.blueprint_hint, context=f"hạng mục {hm}")
            finally:
                llm.publish_usage(self.ctx)
            self.budget -= len(todo)
            for p in todo:
                a = answers.get(p)
                if a is not None:
                    self.cache[self._key(p, folders)] = a.model_dump()
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            self.cache_path.write_text(json.dumps(self.cache, ensure_ascii=False, indent=1), encoding="utf-8")

        out = []
        for p in paths:
            a = self.cache.get(self._key(p, folders))
            if not a:
                out.append({"ảnh": leaf_of(p), "lỗi": "model không trả lời ảnh này"})
                continue
            out.append({
                "ảnh": leaf_of(p),
                "đang ở": leaf_of(where[p]),
                "gợi ý": leaf_of(a["folder"]) if a.get("folder") else None,
                "độ tin cậy": round(float(a.get("confidence", 0)), 2),
                "bản vẽ": bool(a.get("is_blueprint")),
                "mô tả": a.get("description", ""),
            })
        for ref in unknown:
            out.append({"ảnh": ref, "lỗi": f"không thấy trong hạng mục {hm}"})
        return json.dumps({"ngân sách còn": self.budget, "kết quả": out}, ensure_ascii=False)
