from pathlib import Path

import pytest

from fs_tools import SandboxError
from fs_tools.mkdir import make_mkdir_tool, mkdir


def test_mkdir_creates_nested(tmp_path: Path) -> None:
    assert mkdir(tmp_path, "a/b/c") == f"created: {Path('a') / 'b' / 'c'}"
    assert (tmp_path / "a" / "b" / "c").is_dir()


def test_mkdir_is_idempotent(tmp_path: Path) -> None:
    (tmp_path / "x").mkdir()
    assert mkdir(tmp_path, "x") == "exists: x"


def test_mkdir_tool_sandboxed_and_rejects_file_clash(tmp_path: Path) -> None:
    (tmp_path / "f").write_text("x", encoding="utf-8")
    tool = make_mkdir_tool(tmp_path)
    with pytest.raises(NotADirectoryError):
        tool.invoke({"path": "f"})
    with pytest.raises(SandboxError):
        tool.invoke({"path": "../out"})
