import base64
import io
from pathlib import Path

from PIL import Image

from fs_tools.view import load_image_b64, make_view_tool


def test_load_image_downscales_to_jpeg(tmp_path: Path) -> None:
    Image.new("RGB", (4000, 30), "green").save(tmp_path / "wide.png")
    data, mime = load_image_b64(tmp_path, "wide.png", max_edge=512)

    assert mime == "image/jpeg"
    with Image.open(io.BytesIO(base64.b64decode(data))) as im:
        assert max(im.size) <= 512


def test_view_tool_emits_image_content_block(tmp_path: Path) -> None:
    Image.new("RGB", (10, 10), "red").save(tmp_path / "a.jpg")
    tool = make_view_tool(tmp_path)

    msg = tool.invoke({"type": "tool_call", "id": "1", "name": "view", "args": {"path": "a.jpg"}})
    block = msg.content[0]
    assert block["type"] == "image"
    assert block["source_type"] == "base64"
    assert msg.artifact == {"path": "a.jpg"}
