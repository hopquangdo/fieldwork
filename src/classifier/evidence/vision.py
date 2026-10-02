"""Bằng chứng từ NHÌN ẢNH — vision LLM chọn thư mục trong mục lục.

Mỗi request 1 lô ảnh liên tiếp (``[vision].batch``) theo thứ tự chụp → model thấy ngữ cảnh
lân cận. Model trả: ``folder`` (option mục lục), ``value`` (biến nếu THẤY RÕ), ``confidence``,
``taken_at`` (giờ in trên ảnh, nếu có), ``description``. Cache theo (sha1 ảnh, vân tay mục
lục, model) → chạy lại không tốn request.
"""
from __future__ import annotations

from pydantic import BaseModel

from infrastructure.filesystem.image import image_block, load_image_b64

from classifier.catalog import Catalog
from classifier.evidence.base import Ballot, Vote

PROMPT = """Bạn phân loại ảnh hiện trường kiểm định 1 trạm BTS vào phụ lục báo cáo.
Ảnh được gửi theo THỨ TỰ CHỤP; ảnh liền nhau thường cùng một công tác.
Với MỖI ảnh trả về:
- folder: đúng 1 dòng trong DANH SÁCH THƯ MỤC (chép nguyên văn), null nếu không hợp dòng nào
- value: giá trị biến {…} của folder đó CHỈ KHI nhìn thấy rõ trong ảnh (nằm trong danh sách cho phép), không thì null
- confidence: 0-1
- taken_at: giờ chụp in trên ảnh dạng HH:MM:SS nếu có (app GPS / Timestamp Camera), không thì null
- description: 1 câu tả ảnh chụp gì
Quy tắc:
- Chọn thư mục CỤ THỂ nhất; 'Hình ảnh khác …' của 1 hạng mục chỉ khi đúng hạng mục đó nhưng không hợp thư mục con nào.
- Han rỉ / bong sơn KHÔNG tự động là dị tật: ảnh chụp mối nối, chân cột, thanh thép để kiểm tra/đo thì xếp theo công tác đó."""


class _Answer(BaseModel):
    path: str
    folder: str | None = None
    value: str | None = None
    confidence: float = 0.0
    taken_at: str | None = None
    description: str = ""


class _Batch(BaseModel):
    answers: list[_Answer]


def _menu(cat: Catalog) -> str:
    lines = []
    for sec in cat.sections:
        lines.append(f"## {sec.folder}")
        for s in sec.slots:
            extra = []
            if s.var:
                extra.append(f"{{{s.var}}} ∈ {s.values}")
            if s.hint:
                extra.append(s.hint)
            lines.append(f"- {s.option}" + (f"   ← {' · '.join(extra)}" if extra else ""))
    return "\n".join(lines)


def collect(photos, cat: Catalog, llm, cache, *, batch: int = 8, max_edge: int = 1024,
            on_progress=None) -> tuple[Ballot, dict[str, str | None]]:
    """→ (phiếu, {photo.id: giờ in trên ảnh})."""
    opts = cat.by_option()
    fp = f"{cat.fingerprint()}|{llm.name}"
    key = {p.id: f"{p.sha1}|{fp}" for p in photos}
    todo = [p for p in photos if cache.get(key[p.id]) is None]
    if todo:
        menu = _menu(cat)
        model = llm.structured(_Batch)
        try:
            for i in range(0, len(todo), batch):
                chunk = todo[i:i + batch]
                content: list = [{"type": "text", "text": PROMPT + "\n\nDANH SÁCH THƯ MỤC:\n" + menu}]
                for p in chunk:
                    data, mime = load_image_b64(p.path, max_edge=max_edge)
                    content.append({"type": "text", "text": p.id})
                    content.append(image_block(data, mime))
                res = model.invoke([{"role": "user", "content": content}], config=llm.config())
                got = {a.path: a for a in res.answers}
                for p in chunk:
                    a = got.get(p.id)
                    if a is not None:
                        cache.put(key[p.id], a.model_dump())
                if on_progress:
                    on_progress(min(i + batch, len(todo)), len(todo))
        finally:
            cache.save()

    ballot: Ballot = {}
    overlay: dict[str, str | None] = {}
    for p in photos:
        a = cache.get(key[p.id])
        if not a:
            continue
        overlay[p.id] = a.get("taken_at")
        p.description = a.get("description", "")
        if a.get("folder") in opts:
            ballot[p.id] = [Vote(a["folder"], float(a.get("confidence", 0)), "vision",
                                 a.get("value"), p.description)]
    return ballot, overlay
