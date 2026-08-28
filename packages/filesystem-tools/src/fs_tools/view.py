"""`view` — open an image so a multimodal model can see it."""
from __future__ import annotations

import base64
import io
from pathlib import Path

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from fs_tools import resolve_within

_MIME = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
    ".webp": "image/webp", ".gif": "image/gif", ".bmp": "image/bmp",
    ".tif": "image/tiff", ".tiff": "image/tiff",
}


class ViewArgs(BaseModel):
    path: str = Field(..., description="Image path relative to the root.")


def load_image_b64(root: Path, path: str, *, max_edge: int = 1024, quality: int = 80) -> tuple[str, str]:
    """Return (base64_data, mime_type). Large images are downscaled to JPEG to save tokens."""
    p = resolve_within(root, path)
    if not p.is_file():
        raise FileNotFoundError(str(p))
    raw = p.read_bytes()
    try:
        from PIL import Image
    except ModuleNotFoundError:
        return base64.b64encode(raw).decode(), _MIME.get(p.suffix.lower(), "image/jpeg")

    with Image.open(io.BytesIO(raw)) as im:
        im = im.convert("RGB")
        if max(im.size) > max_edge:
            im.thumbnail((max_edge, max_edge))
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=quality)
    return base64.b64encode(buf.getvalue()).decode(), "image/jpeg"


def _image_block(data_b64: str, mime_type: str) -> dict:
    return {"type": "image", "source_type": "base64", "mime_type": mime_type, "data": data_b64}


def make_view_tool(root: str | Path, *, max_edge: int = 1024) -> StructuredTool:
    root = Path(root).resolve()

    def _view(path: str):
        data, mime = load_image_b64(root, path, max_edge=max_edge)
        return [_image_block(data, mime)], {"path": path}

    return StructuredTool.from_function(
        _view,
        name="view",
        args_schema=ViewArgs,
        response_format="content_and_artifact",
        description="Open an image and return it for viewing. Use when the filename alone is not enough.",
    )
