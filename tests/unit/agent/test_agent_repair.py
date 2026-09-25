"""``agent_repair`` node + bộ tool. soft=True → thiếu LLM = stage skipped, không abort.
Các phép sửa ``AssignEditor`` là thuần, test trực tiếp ở đây."""
from pathlib import Path

from config.loader import Config
from infrastructure.observability.report import Report
from runtime import RunContext

from tools.repair import AssignEditor, build_tools
from domain.issues import Issue
from domain.profile import Profile
from steps.agent_repair import agent_repair

_RULES = Path(__file__).resolve().parents[3] / "rules"
_NM = Profile.load(_RULES / "_base.toml").names()


def _ctx(tmp_path: Path, assign: dict) -> RunContext:
    c = RunContext(tmp_path, tmp_path / "o", Config.load(Path(__file__).resolve().parents[2] / "rules_test.toml"),
                   Report(feature="x"), dry_run=True)
    c.data["assign"] = assign
    c.data["issues"] = [Issue("3.X", "odd_images", "3 ảnh", "3.X/Công tác chuẩn bị M1")]
    return c


def test_soft_skips_without_llm(tmp_path):
    ctx = _ctx(tmp_path, {"3.X/Công tác chuẩn bị M1": ["3.X/a/x.jpg"]})
    agent_repair({"ctx": ctx})
    assert ctx.report.stages[-1].status == "skipped"
    assert not ctx.report.aborted


def test_tools_mutate_assign(tmp_path):
    assign = {
        "3.X/Công tác chuẩn bị M1": [f"3.X/khac/Móng M1@10@0{i}@00@--0--.jpg" for i in range(3)],
        "3.X/Công tác chuẩn bị M2": ["3.X/khac/Móng M2@10@10@00@--0--.jpg", "3.X/khac/Móng M2@10@11@00@--0--.jpg"],
        "3.X/Hình ảnh khác": [],
    }
    log: list[str] = []
    editor = AssignEditor(assign, _NM)
    tools = {t.name: t for t in build_tools(editor, log=log, emit=lambda *_: None, iteration=1)}

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


def test_split_folder_keeps_photos_already_in_pair():
    """Tách vào cặp thư mục ĐÃ có ảnh → gộp, không ghi đè (từng mất ảnh ở trạm thật)."""
    la, lb = _NM.pair(_NM.core_of("Đo X"))
    assign = {"2.A/Đo X": ["2.A/Đo X/a.jpg", "2.A/Đo X/b.jpg"],
              f"2.A/{la}": ["2.A/x.jpg"], f"2.A/{lb}": ["2.A/y.jpg"]}
    AssignEditor(assign, _NM).split_folder("2.A/Đo X")
    assert sorted(p for ps in assign.values() for p in ps) == sorted(
        ["2.A/Đo X/a.jpg", "2.A/Đo X/b.jpg", "2.A/x.jpg", "2.A/y.jpg"])
