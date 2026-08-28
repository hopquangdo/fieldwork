# filesystem-tools

One module per tool (`src/fs_tools/`), each a thin **wrapper around LangChain's
file-management tools** — so there's a single place to add project rules or swap
the backend. `view` is fully custom (LangChain has no image tool).

| Tool | Module | Backend | Custom logic added |
|---|---|---|---|
| `scan` | `scan.py` | `ListDirectoryTool` | recursion + JSON metadata (`type/size/is_image`) |
| `read` | `read.py` | `ReadFileTool` | passthrough (extend for decode/size) |
| `view` | `view.py` | — (custom, Pillow) | downscale to JPEG for the model |
| `move` | `move.py` | `MoveFileTool` | never overwrite (`a (1).jpg`) |
| `rename` | `rename.py` | `MoveFileTool` | in-place, bare-name only, never overwrite |
| `mkdir` | `mkdir.py` | — (custom) | parents, idempotent |

Every path also passes `resolve_within(root, path)` → `SandboxError` if it escapes.

```python
from langgraph.prebuilt import create_react_agent
from fs_tools import make_fs_tools

tools = make_fs_tools("/data/inbox", max_edge=1024)   # list[BaseTool]
agent = create_react_agent(model, tools)
```

Each module exposes `make_<tool>_tool(root)`; import one and customize its inner
function. No `copy` / `delete` / `write` — these tools never destroy data.

> Note: `langchain-community` (where the file-management tools live) is being
> sunset. There's no dedicated replacement package yet; wrapping the tools here
> means only the six module internals change if they move.
