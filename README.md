# windows-computer-use-agent

photo-sort — ``src/`` sắp theo tầng (mỗi tầng là một package cấp cao nhất).

```
src/
├── domain/          Photo/Move, Issue, Profile SOP (profile/), luật khớp, đặt tên, hạng mục…
├── application/     services/run_graph.py (chạy 1 feature) · services/sort_photos.py
├── runtime/         @node, state, context, runner, registry, feature
├── agent/           ReAct agent · prompt · vision
├── tools/           repair.py — tool cho agent sửa bảng assign
├── pipeline/        pipeline.py (lắp graph) · feature.py (đăng ký photo-sort)
├── steps/           các node của pipeline
├── infrastructure/
│   ├── llm/         client, factory, stream, usage, pricing, tracker, data/model_prices.json
│   ├── filesystem/  base, operations (Windows-safe, `\?\`), image
│   ├── persistence/ journal
│   └── observability/ report, console
├── config/          settings.py (LLM_* / .env) · loader.py (rules TOML)
└── evaluation/      evaluator.py
rules/               SOP profiles (_base / day_co / tu_dung .toml)
tests/               unit/{domain,agent,runtime} · integration/{api,llm,filesystem,runtime}
app/                 lớp giao tiếp: api/ (FastAPI) · cli/ (photo-sort, photo-sort-eval, photo-sort-engine) ·
                     ui/ (Bun + OpenTUI, tự bật backend)
```

## Run

```bash
uv sync
uv run photo-sort "<station>" "<output>"                 # copy input->output, sort (input untouched)
uv run photo-sort-engine run photo-sort <in> <out> --set even_four=true --set vision_assist=true
uv run photo-sort-engine serve --port 8765                        # HTTP API
```

Every run gets a `run_id`; both artifacts land in `.output/`:

```
.output/<target>-<run_id>.json      the staged report
.output/<target>-<run_id>.jsonl     the journal (op log)
```

Resume an interrupted run: `--resume .output/<target>-<old_id>.jsonl` (skips done moves).

### HTTP API

| | |
|---|---|
| `GET /features` | list registered features |
| `POST /features/{name}/run` | `{input, output, apply, rules?, overrides?}` → full Report JSON |

`GRAPHRUN_ALLOWED_ROOTS` (os-pathsep list) restricts which paths the API may touch.

### Python

```python
from application.services.run_graph import run_feature
report = run_feature("photo-sort", "in", "out", apply=True, even_four=True)
```

Vision / LLM (optional): put `LLM_API_KEY` / `LLM_MODEL_NAME` / `LLM_BASE_URL` in `.env`
(OpenRouter works: `LLM_BASE_URL=https://openrouter.ai/api/v1`, `LLM_MODEL_NAME=google/gemini-2.5-flash`).

## Test

```bash
uv run pytest -q        # PYTHONUTF8=1 on Windows consoles
```

## Add a feature

New package under `src/`, implement `runtime.Feature.build_graph(config) -> StateGraph`,
register it:

```toml
[project.entry-points."photo_sort.features"]
my-feature = "my_pkg.feature:MyFeature"
```

`uv sync` → `photo-sort-engine run my-feature ...` works. Nothing in `runtime` / `infrastructure` changes.

## Notes

- `photo-sort` classification is **rules-driven** (`rules/day_co.toml`) — the client
  edits the TOML, not code. Photos whose filename matches no rule are **left in place** (safe).
- Everything that touches the FS uses `\\?\` extended paths (`infrastructure/filesystem`) — real stations
  nest Vietnamese folder names past Windows' 260-char limit.
- `infrastructure/llm` provides the LLM/agent plumbing and is the shared
  foundation for future agentic features.

## Phát hành (npm)

Tự động bằng GitHub Actions (`.github/workflows/release.yml`):

```
git tag v0.1.1
git push origin v0.1.1
```

→ test → build `photo-sort-win-x64.zip` → GitHub Release `v0.1.1` → `npm publish` bản `0.1.1`.

Cần một lần: secret `NPM_TOKEN` (npm → Access Tokens → Automation) trong
Settings → Secrets and variables → Actions của repo `hopquangdo/fieldwork`. Repo phải **public**
để client tải được file Release (hoặc đổi `photoSort.distUrl` sang server của bạn).

Thử cài từ zip build trên máy: `PHOTO_SORT_DIST_URL=<đường dẫn zip> npm i -g ./npm`.
