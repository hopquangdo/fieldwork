"""Ảnh cho LLM: nạp base64 (thu nhỏ) + block multimodal + re-encode JPEG.

Tách khỏi ``filesystem.operations`` (thuần filesystem, zero-dep) — phần này cần pillow.
"""
from __future__ import annotations

import base64
import io
from pathlib import Path

from infrastructure.filesystem import raw

_MIME = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp",
    ".gif": "image/gif", ".bmp": "image/bmp", ".tif": "image/tiff", ".tiff": "image/tiff",
}


def image_block(data_b64: str, mime: str = "image/jpeg") -> dict:
    """Block ảnh kiểu LangChain multimodal."""
    return {"type": "image", "source_type": "base64", "mime_type": mime, "data": data_b64}


def load_image_b64(path: Path, *, max_edge: int = 1024, quality: int = 80) -> tuple[str, str]:
    """Trả (base64, mime). Ảnh lớn → thu nhỏ về JPEG để tiết kiệm token."""
    with open(raw(path), "rb") as f:
        data = f.read()
    try:
        from PIL import Image
    except ModuleNotFoundError:
        return base64.b64encode(data).decode(), _MIME.get(Path(path).suffix.lower(), "image/jpeg")

    with Image.open(io.BytesIO(data)) as im:
        im = im.convert("RGB")
        if max(im.size) > max_edge:
            im.thumbnail((max_edge, max_edge))
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=quality)
    return base64.b64encode(buf.getvalue()).decode(), "image/jpeg"


def to_jpeg_bytes(data: bytes, *, quality: int = 90) -> bytes:
    """Re-encode ảnh bất kỳ (vd screenshot PNG) sang JPEG."""
    from PIL import Image

    with Image.open(io.BytesIO(data)) as im:
        im = im.convert("RGB")
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=quality)
    return buf.getvalue()
