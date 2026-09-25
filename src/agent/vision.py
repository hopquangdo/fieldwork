"""Gọi vision model phân loại một lô ảnh — 1 request, structured output.

Prompt TỔNG QUÁT; danh sách thư mục hợp lệ truyền vào ở runtime. Không cache ở đây
(``steps/vision.py`` lo cache), không áp kết quả — chỉ trả lời của model.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

from infrastructure.filesystem import longpath
from pydantic import BaseModel

from infrastructure.filesystem.image import image_block, load_image_b64
from infrastructure.llm.client import model

PROMPT = (
    "Phân loại ảnh kỹ thuật hiện trường. Với mỗi ảnh (kèm đường dẫn hiện tại): chọn "
    "'folder' đúng nhất trong danh sách 'folders' (null nếu không hợp), kèm 'confidence' 0-1. "
    "Đặt is_blueprint=true nếu ảnh là BẢN VẼ TAY chụp trên giấy (nền trắng, nét bút vẽ "
    "sơ đồ / mặt cắt / kích thước)."
)


class VisionAnswer(BaseModel):
    path: str
    folder: str | None = None
    is_blueprint: bool = False
    confidence: float = 0.0


class _Batch(BaseModel):
    answers: list[VisionAnswer]


def cache_key(path: Path) -> str:
    """Khoá cache theo tên + kích thước file — đổi tên/đổi ảnh thì đổi khoá."""
    size = os.path.getsize(longpath(path))
    return hashlib.sha1(f"{Path(path).name}|{size}".encode()).hexdigest()[:16]


def ask_vision(rel_paths: list[str], *, root: Path, folders: list[str],
               config: dict | None = None) -> dict[str, VisionAnswer]:
    """``{đường dẫn tương đối: VisionAnswer}`` cho các ảnh trong ``rel_paths``.
    ``config`` chuyển thẳng cho ``invoke`` (vd callbacks đếm token)."""
    llm = model().with_structured_output(_Batch)
    content: list = [{"type": "text", "text": PROMPT + "\nfolders:\n- " + "\n- ".join(folders)}]
    for rel in rel_paths:
        data, mime = load_image_b64(root / rel, max_edge=1024)
        content.append({"type": "text", "text": rel})
        content.append(image_block(data, mime))
    res = llm.invoke([{"role": "user", "content": content}], config=config)
    return {a.path: a for a in res.answers}
