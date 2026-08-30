# windows-computer-use-agent

uv workspace monorepo.

```
packages/                     libraries — reusable across repos (src layout, own tests/)
├── graphrun/                 LangGraph execution harness: run a graph with dry-run,
│                             resumable journal, staged report, config/rules, feature registry
├── filesystem-tools/         fs_tools.core  — Windows-safe FS primitives, zero deps
│                             fs_tools.agent — LangChain tools  (extra: [agent])
└── agent-core/               LangGraph ReAct runtime + model_from_env  (LLM plumbing)

apps/                         runnable products (also graphrun features via entry-point)
└── photo-sort/               sort BTS inspection photos into the report-appendix structure
```

## Run

```bash
uv sync
uv run photo-sort "<station>" "<output>"                 # dry-run
uv run photo-sort "<station>" "<output>" --apply         # copy input->output, move
uv run graphrun run photo-sort <in> <out> --set even_four=true --set vision_assist=true
uv run graphrun serve --port 8765                        # HTTP API (needs graphrun[api])
```

Every run gets a `run_id`; both artifacts land in `.output/`:

```
.output/<target>-<run_id>.json      the staged report
.output/<target>-<run_id>.jsonl     the journal (op log)
```

Resume an interrupted `--apply`: `--resume .output/<target>-<old_id>.jsonl` (skips done moves).

### HTTP API

| | |
|---|---|
| `GET /features` | list registered features |
| `POST /features/{name}/run` | `{input, output, apply, rules?, overrides?}` → full Report JSON |

`GRAPHRUN_ALLOWED_ROOTS` (os-pathsep list) restricts which paths the API may touch.

### Python

```python
from graphrun import run_feature
report = run_feature("photo-sort", "in", "out", apply=True, even_four=True)
```

Vision / LLM (optional): put `LLM_API_KEY` / `LLM_MODEL_NAME` / `LLM_BASE_URL` in `.env`
(OpenRouter works: `LLM_BASE_URL=https://openrouter.ai/api/v1`, `LLM_MODEL_NAME=google/gemini-2.5-flash`).

## Test

```bash
uv run pytest -q        # PYTHONUTF8=1 on Windows consoles
```

## Add a feature

New package under `apps/`, implement `graphrun.Feature.build_graph(config) -> StateGraph`,
register it:

```toml
[project.entry-points."graphrun.features"]
my-feature = "my_pkg.feature:MyFeature"
```

`uv sync` → `graphrun run my-feature ...` works. Nothing in `graphrun` / `filesystem-tools` changes.

## Notes

- `photo-sort` classification is **rules-driven** (`rules/day_co.toml`) — the client
  edits the TOML, not code. Photos whose filename matches no rule are **left in place** (safe).
- Everything that touches the FS uses `\\?\` extended paths (`fs_tools.core`) — real stations
  nest Vietnamese folder names past Windows' 260-char limit.
- `agent-core` is kept but unused by `photo-sort`; it's for future agentic features.
