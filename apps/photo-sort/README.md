# photo-sort

A `graphrun` feature: sort BTS inspection photos into the report-appendix folder structure.

```
scan → [vision] → classify → [even_four] → plan → check ─(ok)→ apply → [delete_empty]
                                                    └(HARD fail)→ report
```

- **scan** — locate the image root, (apply only) copy input→output, inventory every photo.
- **vision** *(opt)* — timestamp-only / blueprint-suspect photos → ask an LLM which folder.
- **classify** — rules (`rules/day_co.toml`) assign each photo to exactly one folder.
- **even_four** *(opt)* — công-tác folders keep an even count ≤ `prefer_images`; surplus → "Hình ảnh khác".
- **plan** — assignment → concrete moves (only where the photo isn't already there).
- **check** — HARD: assignment covers every photo once, no `(folder, filename)` clash.
- **apply** — `safe_move` + journal + retry; skipped on dry-run.
- **delete_empty** *(opt)* — remove empty folders left behind (keeps names containing "khác").

## Rules (`rules/day_co.toml`) — client edits this, not code

```toml
even_four = true
prefer_images = 4
delete_empty = true
vision_assist = false

[[rule]]                              # keep everything already in Mục 1 / Mục 10
from_folder = ["1.hình ảnh tổng thể", "10.hình ảnh dị tật"]
target = "{keep}"

[[rule]]
match       = ["móng m", "mong m"]
from_folder = ["3.công tác đo lực căng"]   # only when the photo sits in Mục 3
target      = "3.Công tác đo lực căng trong dây co/Công tác chuẩn bị đo lực căng {group}"
group_by    = "mong"                        # {group} -> M1, M2, ...
```

Rule keys: `match`, `exclude`, `from_folder`, `not_from_folder`, `group_by`, `target`
(`target = "{keep}"` = leave the photo where it is). No matching rule + no `[fallback]` = photo stays put.

## Run

```bash
photo-sort "<station>" "<output>"                       # dry-run
photo-sort "<station>" "<output>" --apply
graphrun run photo-sort <in> <out> --set vision_assist=true --rules custom.toml
```

`vision_assist` needs `photo-sort[llm]` + `LLM_API_KEY` (OpenRouter works).
