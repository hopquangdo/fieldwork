from pathlib import Path

import pytest

from fs_tools.rename import make_rename_tool


def test_rename_in_place(tmp_path: Path) -> None:
    (tmp_path / "a.jpg").write_bytes(b"a")
    assert make_rename_tool(tmp_path).invoke({"path": "a.jpg", "new_name": "b.jpg"}) == "renamed -> b.jpg"
    assert (tmp_path / "b.jpg").exists()


def test_rename_never_overwrites(tmp_path: Path) -> None:
    (tmp_path / "a.jpg").write_bytes(b"a")
    (tmp_path / "b.jpg").write_bytes(b"b")
    assert make_rename_tool(tmp_path).invoke({"path": "a.jpg", "new_name": "b.jpg"}) == "renamed -> b (1).jpg"


def test_rename_rejects_path_as_name(tmp_path: Path) -> None:
    (tmp_path / "a.jpg").write_bytes(b"a")
    with pytest.raises(ValueError, match="bare name"):
        make_rename_tool(tmp_path).invoke({"path": "a.jpg", "new_name": "sub/b.jpg"})
