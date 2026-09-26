"""Chạy agent THẬT (LangGraph ReAct + tool thật) với model giả chạy theo kịch bản — test
luồng agent mà không cần key / không tốn tiền / kết quả lặp lại được.

``ScriptedChat`` trả lần lượt các ``AIMessage`` (kèm tool_calls) đã soạn sẵn; tool thật
chạy trên ``assign`` thật. ``look`` dùng câu trả lời vision giả (không gọi model)."""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from agent.agent import Agent
from agent.vision import VisionAnswer
from config.loader import Config
from domain.issues import Issue
from domain.profile import Profile
from domain.state import state
from infrastructure.observability.report import Report
from runtime import RunContext
import importlib

agent_step = importlib.import_module("steps.agent_repair")   # module (steps/__init__ xuất hàm cùng tên)
from tools import look as look_mod
from tools.look import Looker
from tools.repair import AssignEditor, build_tools

_RULES = Path(__file__).resolve().parents[3] / "rules"
_NM = Profile.load(_RULES / "_base.toml").names()
_TEST_RULES = Path(__file__).resolve().parents[2] / "rules_test.toml"


class ScriptedChat(BaseChatModel):
    """Model giả: mỗi lần được gọi trả tin nhắn kế tiếp trong ``script``."""

    script: list[AIMessage]
    calls: int = 0

    @property
    def _llm_type(self) -> str:
        return "scripted"

    def bind_tools(self, tools: Any, **kw: Any) -> "ScriptedChat":
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kw) -> ChatResult:
        msg = self.script[min(self.calls, len(self.script) - 1)]
        self.calls += 1
        return ChatResult(generations=[ChatGeneration(message=msg)])


def _call(name: str, i: int, **args) -> AIMessage:
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": f"c{i}"}])


def _ctx(tmp_path: Path, assign: dict, issues: list[Issue]) -> RunContext:
    c = RunContext(tmp_path, tmp_path / "o", Config.load(_TEST_RULES), Report(feature="x"))
    s = state(c)
    s.assign, s.issues, s.root = assign, issues, tmp_path
    return c


def _use_script(monkeypatch, script: list[AIMessage]) -> ScriptedChat:
    chat = ScriptedChat(script=script)
    monkeypatch.setattr(agent_step.llm, "agent",
                        lambda tools, system="": Agent.create(tools, model=chat, system=system))
    return chat


def test_agent_fixes_structure_then_finishes(tmp_path, monkeypatch):
    """Thư mục lẻ ảnh: agent inspect → đẩy 1 ảnh sang 'khác' → check → finish (được chấp nhận)."""
    hm = "3.X"
    odd = f"{hm}/Công tác chuẩn bị M1"
    assign = {odd: [f"{hm}/a/Móng M1@10@0{i}@00@--0--.jpg" for i in range(3)],
              f"{hm}/Công tác đo M1": [f"{hm}/a/Móng M1@11@0{i}@00@--0--.jpg" for i in range(2)],
              f"{hm}/Hình ảnh khác": []}
    ctx = _ctx(tmp_path, assign, [Issue(hm, "odd_images", "3 ảnh — lẻ", odd)])
    _use_script(monkeypatch, [
        _call("inspect", 1, hang_muc=hm),
        _call("reassign", 2, photo="Móng M1@10@02@00@--0--.jpg", to_folder=f"{hm}/Hình ảnh khác"),
        _call("check", 3),
        _call("finish", 4, note="xong"),
        AIMessage(content="đã sửa xong"),
    ])

    agent_step.agent_repair({"ctx": ctx})

    assert len(assign[odd]) == 2 and len(assign[f"{hm}/Hình ảnh khác"]) == 1
    log = ctx.report.sections["agent_repair · nhật ký tool"]
    assert any("finish" in l and "hoàn tất" in l for l in log)
    assert ctx.report.stages[-1].status == "ok"


def test_finish_refused_while_structure_invalid():
    editor = AssignEditor({"3.X/Công tác đo": ["3.X/a.jpg"]}, _NM)
    tools = {t.name: t for t in build_tools(editor, log=[], emit=lambda *_: None, iteration=1,
                                            check=lambda: ["3.X · odd_images · lẻ"])}
    assert "CHƯA" in tools["finish"].invoke({"note": ""})
    assert "còn vi phạm" in tools["check"].invoke({})


def test_swap_keeps_folder_sizes():
    assign = {"3.X/A": ["3.X/a1.jpg", "3.X/a2.jpg"], "3.X/Hình ảnh khác": ["3.X/k1.jpg"]}
    out = AssignEditor(assign, _NM).swap("a2.jpg", "k1.jpg")
    assert "đổi chỗ" in out
    assert assign == {"3.X/A": ["3.X/a1.jpg", "3.X/k1.jpg"], "3.X/Hình ảnh khác": ["3.X/a2.jpg"]}
    assert "khác hạng mục" in AssignEditor({"1.A/x": ["1.A/p.jpg"], "2.B/y": ["2.B/q.jpg"]}, _NM).swap("p.jpg", "q.jpg")


def test_look_uses_budget_and_cache(tmp_path, monkeypatch):
    for n in ("p1.jpg", "p2.jpg"):
        (tmp_path / n).write_bytes(b"x" * 10)
    asked: list[list[str]] = []

    def fake_vision(paths, **kw):
        asked.append(paths)
        return {p: VisionAnswer(path=p, folder="3.X/A", confidence=0.9, description="đo móng") for p in paths}

    monkeypatch.setattr(look_mod, "ask_vision", fake_vision)
    monkeypatch.setattr(look_mod, "llm", SimpleNamespace(tracked=lambda *a: {}, model=lambda: None,
                                                        publish_usage=lambda c: None))
    assign = {"3.X/A": [], "3.X/Hình ảnh khác": ["p1.jpg", "p2.jpg"]}
    ctx = _ctx(tmp_path, assign, [])
    looker = Looker(ctx, AssignEditor(assign, _NM), budget=1)

    assert "vượt ngân sách" in looker.look("3.X", ["p1.jpg", "p2.jpg"])   # cần 2, còn 1
    out = looker.look("3.X", ["p1.jpg"])
    assert '"gợi ý": "A"' in out and looker.budget == 0
    looker.look("3.X", ["p1.jpg"])                                       # lần 2: từ cache
    assert asked == [["p1.jpg"]]


@pytest.mark.parametrize("review", [False, True])
def test_review_queue_only_when_enabled(tmp_path, monkeypatch, review):
    """Cấu trúc hợp lệ, không issue: agent chỉ chạy khi [agent].review bật và có ảnh ở 'khác'."""
    assign = {"3.X/A": [], "3.X/Hình ảnh khác": ["3.X/k.jpg"]}
    ctx = _ctx(tmp_path, assign, [])
    Profile.of(ctx).agent["review"] = review
    chat = _use_script(monkeypatch, [AIMessage(content="không có gì để làm")])
    monkeypatch.setattr(agent_step, "Looker", lambda *a, **k: SimpleNamespace(look=lambda *x: "{}", budget=1))

    agent_step.agent_repair({"ctx": ctx})

    assert (chat.calls > 0) is review
    assert ctx.report.stages[-1].status == ("ok" if review else "skipped")
    assert agent_step.review_queue(assign, _NM) == {"3.X": ["k.jpg"]}


def test_agent_error_rolls_back_changes(tmp_path, monkeypatch):
    """Agent đổi assign rồi lỗi giữa chừng (vd chạm giới hạn bước) → trả assign về như cũ."""
    hm = "3.X"
    odd = f"{hm}/Công tác chuẩn bị M1"
    assign = {odd: [f"{hm}/a/p{i}@10@0{i}@00@--0--.jpg" for i in range(3)], f"{hm}/Hình ảnh khác": []}
    snapshot = {k: list(v) for k, v in assign.items()}
    ctx = _ctx(tmp_path, assign, [Issue(hm, "odd_images", "lẻ", odd)])
    # lặp reassign qua lại mãi → GraphRecursionError
    _use_script(monkeypatch, [_call("reassign", 1, photo="p0@10@00@00@--0--.jpg", to_folder=f"{hm}/Hình ảnh khác")])
    Profile.of(ctx).agent["max_steps"] = 6

    agent_step.agent_repair({"ctx": ctx})

    assert assign == snapshot
    assert ctx.report.stages[-1].status == "skipped"
    assert any("HOÀN TÁC" in l for l in ctx.report.sections["agent_repair · nhật ký tool"])


def test_reassign_refuses_to_invent_folders():
    assign = {"3.X/A": ["3.X/a.jpg"], "3.X/Hình ảnh khác": []}
    out = AssignEditor(assign, _NM).reassign("a.jpg", "3.X/Thư mục agent tự bịa")
    assert "chưa có" in out and "3.X/Thư mục agent tự bịa" not in assign


def test_finish_gives_up_on_second_call():
    tools = {t.name: t for t in build_tools(AssignEditor({}, _NM), log=[], emit=lambda *_: None,
                                            iteration=1, check=lambda: ["không sửa được"])}
    assert "CHƯA" in tools["finish"].invoke({"note": ""})
    assert "dừng dù còn 1 vi phạm" in tools["finish"].invoke({"note": ""})
