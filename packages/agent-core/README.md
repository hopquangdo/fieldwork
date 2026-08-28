# agent-core

Reusable LLM-agent runtime on the LangChain ecosystem. Task-agnostic: you give
it any LangChain tools, it runs the loop.

## What's inside

| Symbol | Use |
|---|---|
| `Agent.create(tools, model=, system=)` | LangGraph ReAct agent. `.run(user_content)` / `.stream(...)`. `user_content` may be a string or a list of content blocks (text + images). |
| `ToolExecutor` / `ToolCall` / `ToolResult` | Deterministic, auditable execution of tools **without** an LLM — for replaying plans or scripted workflow steps. |
| `get_chat_model("anthropic:claude-sonnet-5")` | Provider-agnostic model factory (`init_chat_model` under the hood). |
| `model_from_env()` | Build the model from `LLM_API_KEY` / `LLM_MODEL_NAME` / `LLM_BASE_URL` (auto-loads a `.env`). `Agent.create(tools)` with no `model=` uses this. |
| `load_dotenv()` | Zero-dependency `.env` loader; walks up from cwd. |
| `tool`, `BaseTool`, `StructuredTool` | Re-exported from `langchain_core` for authoring tools. |
| `text_block(...)`, `image_block(b64, mime)` | Build multimodal content blocks; return `([image_block(...)], artifact)` from a tool declared `response_format="content_and_artifact"`. |

## Example

```python
from agent_core import Agent

agent = Agent.create(my_tools, model="anthropic:claude-sonnet-5", system="You sort files.")
messages = agent.run("Organize the images in ./inbox")
```

Or drive it from a `.env` (no explicit `model=`):

```dotenv
LLM_API_KEY=sk-...
LLM_MODEL_NAME=claude-sonnet-5          # bare name -> Anthropic; with LLM_BASE_URL -> OpenAI-compatible
LLM_BASE_URL=                           # optional: any OpenAI-compatible endpoint
```

```python
agent = Agent.create(my_tools, system="You sort files.")   # model pulled from the env
```

`model_from_env()` also accepts `"provider:name"` in `LLM_MODEL_NAME` to force a provider.
`ANTHROPIC_API_KEY` / `OPENAI_API_KEY` still work if you'd rather not use `LLM_API_KEY`. Depends only on LangChain packages —
nothing here knows about the filesystem or any specific task. See the
`filesystem-tools` package for a ready-made tool set.
