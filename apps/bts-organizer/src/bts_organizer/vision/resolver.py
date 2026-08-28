"""Resolve Question objects into Answers. Two backends: heuristic (default) and LLM vision."""
from __future__ import annotations

import base64
import io
from pathlib import Path
from typing import Protocol

from bts_organizer.domain.catalog import KHAC_TONG_THE
from bts_organizer.domain.models import Answer, Question
from bts_organizer.domain.naming import looks_like_blueprint_name, parse
from bts_organizer.winpath import longpath


def load_image_b64(root: Path, rel: str, *, max_edge: int = 1024, quality: int = 80) -> tuple[str, str]:
    """base64 JPEG (downscaled) for a station-relative image path. MAX_PATH-safe."""
    p = longpath(Path(root) / rel)
    raw = p.read_bytes()
    try:
        from PIL import Image

        with Image.open(io.BytesIO(raw)) as im:
            im = im.convert("RGB")
            if max(im.size) > max_edge:
                im.thumbnail((max_edge, max_edge))
            buf = io.BytesIO()
            im.save(buf, format="JPEG", quality=quality)
        return base64.b64encode(buf.getvalue()).decode(), "image/jpeg"
    except ModuleNotFoundError:
        return base64.b64encode(raw).decode(), "image/jpeg"


class Resolver(Protocol):
    def run(
        self, questions: list[Question], answers: dict[str, Answer], attempts: dict[str, int]
    ) -> dict: ...


def _pending(questions, answers, attempts, max_attempts) -> list[Question]:
    return [
        q for q in questions
        if q.id not in answers and attempts.get(q.id, 0) < max_attempts
    ]


class HeuristicResolver:
    """No LLM. Confirms blueprints by filename, otherwise gives up gracefully (folder=None -> 'khác')."""

    def __init__(self, max_attempts: int = 1) -> None:
        self.max_attempts = max_attempts

    def run(self, questions, answers, attempts):
        out: dict[str, Answer] = {}
        bumped: dict[str, int] = {}
        for q in _pending(questions, answers, attempts, self.max_attempts):
            comp = parse(q.image)
            prefix = comp.prefix if comp else ""
            is_bp = q.kind == "is_blueprint" or looks_like_blueprint_name(prefix)
            out[q.id] = Answer(
                q_id=q.id,
                folder=KHAC_TONG_THE if is_bp else None,
                is_blueprint=is_bp,
                confidence=0.4,
                attempt=attempts.get(q.id, 0) + 1,
            )
            bumped[q.id] = attempts.get(q.id, 0) + 1
        return {"answers": out, "q_attempts": bumped}


class LLMResolver:
    """Batches question images into one structured-output call. Escalates image size on retry."""

    SYSTEM = (
        "Bạn phân loại ảnh kiểm định cột BTS. Với mỗi ảnh, chọn 'folder' đúng nhất "
        "trong danh sách ứng viên, hoặc null nếu không hợp. Đánh dấu is_blueprint=true "
        "nếu là ảnh chụp BẢN VẼ TAY (nền giấy trắng, nét bút vẽ cột/mặt cắt/kích thước)."
    )

    def __init__(self, model, root: Path, *, max_attempts=2, edge_first=1024, edge_retry=1568):
        from bts_organizer.vision.schemas import BatchAnswer

        self._llm = model.with_structured_output(BatchAnswer)
        self._root = Path(root)
        self.max_attempts = max_attempts
        self.edge_first, self.edge_retry = edge_first, edge_retry

    def run(self, questions, answers, attempts):
        batch = _pending(questions, answers, attempts, self.max_attempts)
        if not batch:
            return {"answers": {}, "q_attempts": {}}

        edge = self.edge_first if all(attempts.get(q.id, 0) == 0 for q in batch) else self.edge_retry
        content = [{"type": "text", "text": self.SYSTEM}]
        for q in batch:
            data, mime = load_image_b64(self._root, q.image, max_edge=edge)
            content.append({"type": "text", "text": f"[{q.id}] kind={q.kind} candidates={q.candidates}"})
            content.append({"type": "image", "source_type": "base64", "mime_type": mime, "data": data})

        result = self._llm.invoke([{"role": "user", "content": content}])
        out = {
            a.q_id: Answer(a.q_id, a.folder, a.is_blueprint, a.confidence, attempts.get(a.q_id, 0) + 1)
            for a in result.answers
        }
        bumped = {q.id: attempts.get(q.id, 0) + 1 for q in batch}
        return {"answers": out, "q_attempts": bumped}


def build_resolver(config, root: Path) -> Resolver:
    v = config.vision
    if not config.vision_enabled():
        return HeuristicResolver(max_attempts=1)
    try:
        return LLMResolver(
            config.chat_model, root,
            max_attempts=v.max_attempts, edge_first=v.max_edge_first, edge_retry=v.max_edge_retry,
        )
    except Exception:  # no key / import problem -> degrade, never crash the pipeline
        return HeuristicResolver(max_attempts=1)
