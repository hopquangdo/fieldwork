from pathlib import Path

import pytest

from fs_tools import SandboxError
from fs_tools.move import make_move_tool


def test_move_into_folder(tmp_path: Path) -> None:
    (tmp_path / "a.jpg").write_bytes(b"a")
    out = make_move_tool(tmp_path).invoke({"path": "a.jpg", "dest_dir": "sorted"})
    assert out == f"moved -> {Path('sorted') / 'a.jpg'}"
    assert (tmp_path / "sorted" / "a.jpg").read_bytes() == b"a"
    assert not (tmp_path / "a.jpg").exists()


def test_move_never_overwrites(tmp_path: Path) -> None:
    (tmp_path / "a.jpg").write_bytes(b"new")
    (tmp_path / "dst").mkdir()
    (tmp_path / "dst" / "a.jpg").write_bytes(b"old")

    out = make_move_tool(tmp_path).invoke({"path": "a.jpg", "dest_dir": "dst"})
    assert out == f"moved -> {Path('dst') / 'a (1).jpg'}"
    assert (tmp_path / "dst" / "a.jpg").read_bytes() == b"old"


def test_move_is_sandboxed(tmp_path: Path) -> None:
    (tmp_path / "a.jpg").write_bytes(b"a")
    with pytest.raises(SandboxError):
        make_move_tool(tmp_path).invoke({"path": "a.jpg", "dest_dir": "../out"})
