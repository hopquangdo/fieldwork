from pathlib import Path

from langgraph.graph import END, START, StateGraph

from config.loader import Config
from infrastructure.observability.report import Report
from runtime import Feature, FeatureSpec, GraphState, RunContext, node, run


@node("collect")
def collect(ctx):
    ctx.data["items"] = list(range(ctx.config.get("n", 3)))
    ctx.report.stages[-1].detail = f"{len(ctx.data['items'])} items"


@node("guard")
def guard(ctx):
    if ctx.config.get("boom"):
        ctx.report.abort("boom requested")


@node("write")
def write(ctx):
    ctx.report.sections["written"] = [] if ctx.dry_run else ctx.data["items"]


class Demo(Feature):
    spec = FeatureSpec("demo", "test feature")

    def build_graph(self, cfg) -> StateGraph:
        g = StateGraph(GraphState)
        g.add_node("collect", collect)
        g.add_node("guard", guard)
        g.add_node("write", write)
        g.add_edge(START, "collect")
        g.add_edge("collect", "guard")
        g.add_conditional_edges("guard", lambda s: "write" if not s["ctx"].report.aborted else END,
                                {"write": "write", END: END})
        g.add_edge("write", END)
        return g


def _ctx(tmp_path: Path, cfg: dict, dry=True) -> RunContext:
    return RunContext(tmp_path, tmp_path, Config(cfg), Report(feature="demo"), dry_run=dry)


def test_happy_path(tmp_path):
    ctx = _ctx(tmp_path, {"n": 5})
    rep = run(Demo(), ctx)
    assert [s.name for s in rep.stages] == ["collect", "guard", "write"]
    assert all(s.status == "ok" for s in rep.stages)
    assert not rep.aborted


def test_abort_routes_around_downstream(tmp_path):
    rep = run(Demo(), _ctx(tmp_path, {"boom": True}))
    assert rep.aborted
    assert [s.name for s in rep.stages] == ["collect", "guard"]   # conditional edge -> END
    assert "boom requested" in rep.errors[0]


def test_node_exception_marks_abort(tmp_path):
    @node("kaboom")
    def kaboom(ctx):
        raise RuntimeError("nope")

    class Broken(Demo):
        def build_graph(self, cfg):
            g = StateGraph(GraphState)
            g.add_node("kaboom", kaboom)
            g.add_edge(START, "kaboom")
            g.add_edge("kaboom", END)
            return g

    rep = run(Broken(), _ctx(tmp_path, {}))
    assert rep.aborted and "nope" in rep.errors[0]


def test_report_json_roundtrip(tmp_path):
    ctx = _ctx(tmp_path, {"n": 2})
    run(Demo(), ctx)
    out = tmp_path / "r.json"
    ctx.report.write_json(out)
    assert out.exists() and "collect" in out.read_text(encoding="utf-8")
