"""Image adapters — needs the ``image`` extra (pillow)."""
from fs_tools.media.content import image_block
from fs_tools.media.image import load_image_b64, to_jpeg_bytes

__all__ = ["image_block", "load_image_b64", "to_jpeg_bytes"]
