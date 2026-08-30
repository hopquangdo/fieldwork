"""Load an image as base64 / re-encode to JPEG (needs the ``image`` extra: pillow)."""
from __future__ import annotations

import base64
import io
from pathlib import Path

from fs_tools.winpath import raw

_MIME = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp",
    ".gif": "image/gif", ".bmp": "image/bmp", ".tif": "image/tiff", ".tiff": "image/tiff",
}


def load_image_b64(path: Path, *, max_edge: int = 1024, quality: int = 80) -> tuple[str, str]:
    """Return (base64, mime). Downscales large images to JPEG to save tokens."""
    data = _read_bytes(path)
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


def to_jpeg_bytes(raw: bytes, *, quality: int = 90) -> bytes:
    """Re-encode any image (e.g. a PNG screenshot) as JPEG. Needs the ``image`` extra."""
    from PIL import Image

    with Image.open(io.BytesIO(raw)) as im:
        im = im.convert("RGB")
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=quality)
    return buf.getvalue()


def _read_bytes(path: Path) -> bytes:
    with open(raw(path), "rb") as f:
        return f.read()
