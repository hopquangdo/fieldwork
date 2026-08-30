from pathlib import Path

import pytest

from fs_tools import copytree, is_empty_dir, rmdir_if_empty, safe_move, walk_files


def test_safe_move_never_overwrites(tmp_path: Path):
    (tmp_path / "a.jpg").write_bytes(b"new")
    (tmp_path / "dst").mkdir()
    (tmp_path / "dst" / "a.jpg").write_bytes(b"old")

    dest = safe_move(tmp_path / "a.jpg", tmp_path / "dst")
    assert dest.name == "a (1).jpg"
    assert (tmp_path / "dst" / "a.jpg").read_bytes() == b"old"
    assert not (tmp_path / "a.jpg").exists()


def test_safe_move_missing_source(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        safe_move(tmp_path / "nope.jpg", tmp_path / "x")


def test_copytree_and_walk(tmp_path: Path):
    src = tmp_path / "src" / "deep" / "deeper"
    src.mkdir(parents=True)
    (src / "x.txt").write_text("hi", encoding="utf-8")
    n = copytree(tmp_path / "src", tmp_path / "out")
    assert n == 1
    assert {p.name for p in walk_files(tmp_path / "out")} == {"x.txt"}


def test_rmdir_if_empty(tmp_path: Path):
    (tmp_path / "empty").mkdir()
    (tmp_path / "full").mkdir()
    (tmp_path / "full" / "f").write_text("x", encoding="utf-8")
    assert rmdir_if_empty(tmp_path / "empty") is True
    assert rmdir_if_empty(tmp_path / "full") is False
    assert not is_empty_dir(tmp_path / "full")
