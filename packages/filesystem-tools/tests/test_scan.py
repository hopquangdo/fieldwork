import json
from pathlib import Path

import pytest

from fs_tools import SandboxError
from fs_tools.scan import make_scan_tool


def test_scan_lists_files_and_dirs_sorted(tmp_path: Path) -> None:
    (tmp_path / "b.txt").write_text("bb", encoding="utf-8")
    (tmp_path / "a").mkdir()
    (tmp_path / "pic.jpg").write_bytes(b"x")

    entries = json.loads(make_scan_tool(tmp_path).invoke({"subdir": "."}))

    assert [e["path"] for e in entries] == ["a", "b.txt", "pic.jpg"]
    assert entries[0]["type"] == "dir"
    assert entries[1]["size"] == 2
    assert entries[2]["is_image"] is True


def test_scan_recursive_images_only(tmp_path: Path) -> None:
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "deep.png").write_bytes(b"x")
    (tmp_path / "note.txt").write_text("x", encoding="utf-8")

    entries = json.loads(
        make_scan_tool(tmp_path).invoke({"subdir": ".", "recursive": True, "images_only": True})
    )
    assert [e["path"] for e in entries] == [str(Path("sub") / "deep.png")]


def test_scan_is_sandboxed(tmp_path: Path) -> None:
    with pytest.raises(SandboxError):
        make_scan_tool(tmp_path).invoke({"subdir": ".."})
