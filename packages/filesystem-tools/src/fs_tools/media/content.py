"""LangChain-style multimodal content block."""
from __future__ import annotations


def image_block(data_b64: str, mime: str = "image/jpeg") -> dict:
    return {"type": "image", "source_type": "base64", "mime_type": mime, "data": data_b64}
