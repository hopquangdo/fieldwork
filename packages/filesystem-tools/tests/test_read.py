from pathlib import Path

import pytest

from fs_tools.read import make_read_tool


def test_read_returns_contents(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("hello", encoding="utf-8")
    assert "hello" in make_read_tool(tmp_path).invoke({"path": "a.txt"})


def test_read_missing_file(tmp_path: Path) -> None:
    out = make_read_tool(tmp_path).invoke({"path": "nope.txt"})
    assert "no such file" in out.lower() or "error" in out.lower()


def test_read_is_sandboxed(tmp_path: Path) -> None:
    out = make_read_tool(tmp_path).invoke({"path": "../secret"})
    assert "outside" in out.lower() or "error" in out.lower()
