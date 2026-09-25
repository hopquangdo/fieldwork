from pathlib import Path

import pytest

from infrastructure.filesystem import (
    CopyTreeTool,
    IsEmptyDirTool,
    MoveFileTool,
    RemoveEmptyDirTool,
    WalkFilesTool,
)

move_file = MoveFileTool()
copy_tree = CopyTreeTool()
walk_files = WalkFilesTool()
is_empty_dir = IsEmptyDirTool()
remove_empty_dir = RemoveEmptyDirTool()


def test_move_file_never_overwrites(tmp_path: Path):
    (tmp_path / "a.jpg").write_bytes(b"new")
    (tmp_path / "dst").mkdir()
    (tmp_path / "dst" / "a.jpg").write_bytes(b"old")

    dest = move_file(tmp_path / "a.jpg", tmp_path / "dst")
    assert dest.name == "a (1).jpg"
    assert (tmp_path / "dst" / "a.jpg").read_bytes() == b"old"
    assert not (tmp_path / "a.jpg").exists()


def test_move_file_transform(tmp_path: Path):
    (tmp_path / "a.txt").write_bytes(b"hi")
    dest = move_file(tmp_path / "a.txt", tmp_path / "d", transform=bytes.upper)
    assert dest.read_bytes() == b"HI"
    assert not (tmp_path / "a.txt").exists()


def test_move_file_missing_source(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        move_file(tmp_path / "nope.jpg", tmp_path / "x")


def test_tool_metadata_and_callable(tmp_path: Path):
    assert MoveFileTool.name == "move_file"
    assert MoveFileTool().description
    (tmp_path / "a.txt").write_bytes(b"x")
    # __call__ delegates to execute
    assert move_file(tmp_path / "a.txt", tmp_path / "d").name == "a.txt"


def test_copy_tree_and_walk(tmp_path: Path):
    src = tmp_path / "src" / "deep" / "deeper"
    src.mkdir(parents=True)
    (src / "x.txt").write_text("hi", encoding="utf-8")
    n = copy_tree(tmp_path / "src", tmp_path / "out")
    assert n == 1
    assert {p.name for p in walk_files(tmp_path / "out")} == {"x.txt"}


def test_remove_empty_dir(tmp_path: Path):
    (tmp_path / "empty").mkdir()
    (tmp_path / "full").mkdir()
    (tmp_path / "full" / "f").write_text("x", encoding="utf-8")
    assert remove_empty_dir(tmp_path / "empty") is True
    assert remove_empty_dir(tmp_path / "full") is False
    assert not is_empty_dir(tmp_path / "full")
