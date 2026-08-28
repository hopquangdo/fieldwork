# bts-organizer

Deterministic **LangGraph** pipeline that sorts BTS tower inspection photos into
the report-appendix folder structure. Not an agent loop — the procedure is fixed;
the LLM is used only to look at the handful of ambiguous images.

```
discover → read_meta → inventory → plan_layout ─┐
                                                │ ↺ vision (≤2 / câu hỏi)
                                   resolve_ambiguity ┘
        build_ops → simulate → validate ─┬─ ok ───────→ execute → report
                                         ├─ HARD ─────→ report (abort)
                                         ├─ repairable → repair ↺ (≤5)
                                         └─ exhausted → drop_failing → execute
```

## Layout

`domain/` (pure value objects + naming/metadata/catalog) · `discovery/` ·
`layout/` (one strategy per hạng mục, `registry.py` picks by name) · `vision/`
(only place the LLM lives — `HeuristicResolver` when there's no key) ·
`planning/` · `execution/` (simulator + on-disk executor + journal) ·
`validation/` (invariants) · `repair/` (fixers) · `graph/` (state, nodes,
routing, wiring) · `api/` (FastAPI for the UI) · `config.py` (composition root).

One-way imports: `domain` ← everything; `agent_core`/`fs_tools` only in
`vision/`, `execution/`, `config.py`.

## CLI

```bash
bts-organize "<station folder>"                 # dry-run, prints JSON report
bts-organize "<station folder>" --apply         # write to disk (journal -> resumable)
bts-organize "<workspace>" --workspace [--apply]
#   --only 3,5,9   --no-vision   --report out.json
```

Set `LLM_API_KEY` / `LLM_MODEL_NAME` (see `.env.example`) only if you want the
vision step; otherwise it degrades to filename heuristics.

## API (for the UI)

```bash
uvicorn "bts_organizer.api.app:app" --port 8765
```

| POST | body | returns |
|---|---|---|
| `/scan` | `{root}` | `{directories, files, images, stations[]}` |
| `/organize` | `{root, dry_run, no_vision?, only?}` | full report (+ `steps/results` legacy view) |
| `/apply` | `{root}` | report after writing to disk |

`BTS_ALLOWED_ROOTS` (os-pathsep list) restricts which paths the API will touch.

## Test

```bash
uv run pytest apps/bts-organizer -q
```
