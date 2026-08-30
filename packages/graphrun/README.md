# graphrun

LangGraph execution harness. You bring a `StateGraph`; graphrun gives you a
CLI, an HTTP API, dry-run, a resumable journal, staged reporting, config/rules
merging, and a feature registry — so every graph runs the same way.

## Install

```bash
pip install graphrun            # core (CLI + library)
pip install "graphrun[api]"     # + FastAPI / uvicorn HTTP server
```

Requires Python 3.10+.

## Concepts

| Piece | What it is |
|-------|-----------|
| **Feature** | A `Feature` subclass with a `FeatureSpec` (name, summary, optional default rules) and a `build_graph(config) -> StateGraph`. Registered via the `graphrun.features` entry-point group. |
| **Node** | A `(ctx: RunContext) -> None` function wrapped with `@node("name")`. Records a timed `Stage`, no-ops once the run is aborted, and can be `soft=True` to skip on error instead of aborting. |
| **RunContext** | Passed to every node: `input`, `output`, `config`, `report`, `dry_run`, `journal`, plus `data` scratch space shared between nodes and `emit()` for live progress. Lives in the graph state under `state["ctx"]`. |
| **Config** | Read-only view over a rules `.toml` merged with `KEY=VALUE` overrides. Dotted access: `config.get("vision.max", 10)`. |
| **Report / Journal** | Every run gets a `run_id`. The report (`.json`) is the staged summary; the journal (`.jsonl`) is the op log used to resume. Both land in `--report-dir` (default `.output/`). |

## CLI

```bash
graphrun list                                   # registered features
graphrun run <feature> <input> <output>         # run (writes changes by default)
graphrun run <feature> <in> <out> --dry-run     # plan only, no writes
graphrun run <feature> <in> <out> --rules r.toml --set vision.max=50
graphrun run <feature> <in> <out> --resume .output/<target>-<run_id>.jsonl
graphrun run <feature> <in> <out> --json        # report as JSON on stdout
graphrun serve --host 127.0.0.1 --port 8765     # HTTP API (needs graphrun[api])
```

## HTTP API

`graphrun serve` (or `uvicorn graphrun.api.app:app`). Endpoints are defined in
`graphrun.api.routes`; `graphrun.api.app` just builds the `FastAPI` app.

| Method | Path | Purpose |
|--------|------|---------|
| GET  | `/health` | liveness |
| GET  | `/features` | list registered features |
| POST | `/features/{name}/run` | start a job → `{job_id}`; `?wait=true` blocks for the result |
| GET  | `/jobs` | recent jobs (last 50) |
| GET  | `/jobs/{id}` | job status + report |
| GET  | `/jobs/{id}/events` | SSE stream of per-node progress |

`POST` body: `{"input": "...", "output": "...", "apply": true, "rules": null, "overrides": {}}`.

Set `GRAPHRUN_ALLOWED_ROOTS` (os-pathsep-separated) to restrict which paths the
API will accept for `input`/`output`; requests outside those roots get a 403.

## Library

```python
from graphrun import run_feature

report = run_feature(
    "my-feature", "in/", "out/",
    apply=False,                 # dry-run
    rules="rules.toml",
    on_log=print,                # live progress sink
    **{"vision.max": 50},        # config overrides
)
print(report.aborted, [s.name for s in report.stages])
```

`run_feature` is the single entry point the CLI, API, and notebooks all share.

## Writing a feature

```python
# mypkg/feature.py
from graphrun import Feature, FeatureSpec, node
from langgraph.graph import StateGraph, START, END
from graphrun.core.state import GraphState

@node("scan")
def scan(ctx):
    ctx.data["items"] = list(ctx.input.iterdir())

@node("write", soft=False)
def write(ctx):
    for p in ctx.data["items"]:
        if not ctx.dry_run:
            ...  # do the work
        ctx.journal.record(...)

class MyFeature(Feature):
    spec = FeatureSpec(name="my-feature", summary="does the thing",
                       default_rules="rules.toml")

    def build_graph(self, config) -> StateGraph:
        g = StateGraph(GraphState)
        g.add_node("scan", scan)
        g.add_node("write", write)
        g.add_edge(START, "scan")
        g.add_edge("scan", "write")
        g.add_edge("write", END)
        return g
```

Register it so graphrun can discover it:

```toml
# pyproject.toml of the package that ships the feature
[project.entry-points."graphrun.features"]
my-feature = "mypkg.feature:MyFeature"
```

## Development

```bash
pip install -e "packages/graphrun[api]"
pytest packages/graphrun/tests
```
