"""agent_repair as a real tool-calling node. Without LLM_API_KEY it skips gracefully;
the tool functions themselves are pure and tested here."""
from pathlib import Path

from graphrun import Config, Report, RunContext

from photo_sort.issues import Issue
from photo_sort.steps.agent_repair import _make_tools, agent_repair


def _ctx(tmp_path: Path, assign: dict) -> RunContext:
    c = RunContext(tmp_path, tmp_path / "o", Config({}), Report(feature="x"), dry_run=True)
    c.data["assign"] = assign
    c.data["issues"] = [Issue("3.X", "odd_images", "3 ảnh", "3.X/Công tác chuẩn bị M1")]
    return c


def test_skips_without_api_key(tmp_path, monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    ctx = _ctx(tmp_path, {"3.X/Công tác chuẩn bị M1": ["3.X/a/x.jpg"]})
    agent_repair({"ctx": ctx})
    assert ctx.report.stages[-1].status == "skipped"


def test_tools_mutate_assign(tmp_path):
    assign = {
        "3.X/Công tác chuẩn bị M1": [f"3.X/khac/Móng M1@10@0{i}@00@--0--.jpg" for i in range(3)],
        "3.X/Công tác chuẩn bị M2": ["3.X/khac/Móng M2@10@10@00@--0--.jpg", "3.X/khac/Móng M2@10@11@00@--0--.jpg"],
        "3.X/Hình ảnh khác": [],
    }
    log: list[str] = []
    tools = {t.name: t for t in _make_tools(assign, 1, log)}

    assert "công tác" in tools["inspect"].invoke({"hang_muc": "3.X"})
    out = tools["reassign"].invoke(
        {"photo": "Móng M1@10@02@00@--0--.jpg", "to_folder": "3.X/Hình ảnh khác"}
    )
    assert "chuyển" in out
    assert len(assign["3.X/Công tác chuẩn bị M1"]) == 2
    assert len(assign["3.X/Hình ảnh khác"]) == 1
    assert any("[1] reassign(" in e for e in log)

    # cross-hạng-mục reassign is refused
    bad = tools["reassign"].invoke({"photo": "Móng M2@10@10@00@--0--.jpg", "to_folder": "9.Y/Đo ma ní"})
    assert "từ chối" in bad or "không tìm" in bad
