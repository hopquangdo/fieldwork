# ui — BTS organizer (terminal UI)

Bun + SolidJS + OpenTUI. Talks to the `bts-organizer` HTTP API.

## Run

```bash
# 1. start the API (from repo root)
uv run uvicorn "bts_organizer.api.app:app" --port 8765

# 2. start the UI
cd ui
bun install
bun run src/index.tsx
```

Override the API URL with `BTS_API_URL`.

## Flow

1. **Browse / Scan** a workspace → station list with image counts.
2. **Dry-run** a station (or "Dry-run all") → the graph runs without touching
   disk; the log shows: bảng đếm hạng mục, cây kết quả (diff), gaps, ảnh cần
   vision, HARD fails.
3. **Apply** → re-runs and writes to disk (`move` never overwrites, journal makes
   it resumable). Button only enables after a clean dry-run.
