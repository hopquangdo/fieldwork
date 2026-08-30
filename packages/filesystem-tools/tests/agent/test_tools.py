from pathlib import Path

import pytest

pytest.importorskip("langchain_core")

from fs_tools.agent import SandboxError, make_fs_tools


def test_tool_set_and_sandbox(tmp_path: Path):
    (tmp_path / "a.jpg").write_bytes(b"x")
    tools = {t.name: t for t in make_fs_tools(tmp_path)}
    assert set(tools) == {"scan", "read", "view", "move", "mkdir"}

    assert tools["move"].invoke({"path": "a.jpg", "dest_dir": "sorted"}).startswith("moved ->")
    assert (tmp_path / "sorted" / "a.jpg").exists()

    with pytest.raises(SandboxError):
        tools["move"].invoke({"path": "../evil", "dest_dir": "x"})
