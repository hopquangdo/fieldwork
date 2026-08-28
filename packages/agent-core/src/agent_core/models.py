from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from langchain_core.language_models import BaseChatModel

DEFAULT_MODEL = "anthropic:claude-sonnet-5"

# Env vars the project uses to describe "whatever LLM endpoint we're pointed at".
ENV_API_KEY = "LLM_API_KEY"
ENV_MODEL_NAME = "LLM_MODEL_NAME"
ENV_BASE_URL = "LLM_BASE_URL"


def load_dotenv(path: str | os.PathLike[str] | None = None, *, override: bool = False) -> dict[str, str]:
    """Minimal ``.env`` loader (no third-party dependency).

    Walks up from ``path`` (or cwd) looking for a ``.env`` file and loads
    ``KEY=VALUE`` lines into ``os.environ``. Existing values are kept unless
    ``override=True``. Returns the parsed pairs.
    """
    start = Path(path) if path is not None else Path.cwd()
    if start.is_file():
        env_file: Path | None = start
    else:
        env_file = next(
            (p / ".env" for p in [start, *start.parents] if (p / ".env").is_file()),
            None,
        )
    parsed: dict[str, str] = {}
    if env_file is None:
        return parsed
    for raw in env_file.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        parsed[key] = value
        if override or key not in os.environ:
            os.environ[key] = value
    return parsed


def get_chat_model(model: str | BaseChatModel = DEFAULT_MODEL, **kwargs: Any) -> BaseChatModel:
    """Resolve a chat model.

    `model` may be an already-built BaseChatModel, or a provider-prefixed string
    understood by langchain's ``init_chat_model`` (e.g. ``"anthropic:claude-sonnet-5"``,
    ``"openai:gpt-4o"``). Keeping this indirection is what makes agent-core
    provider-agnostic while still defaulting to Claude.
    """
    if isinstance(model, BaseChatModel):
        return model
    from langchain.chat_models import init_chat_model

    kwargs.setdefault("temperature", 0)
    return init_chat_model(model, **kwargs)


def model_from_env(*, load_env: bool = True, **overrides: Any) -> BaseChatModel:
    """Build a chat model from ``LLM_*`` environment variables.

    Reads ``LLM_MODEL_NAME`` (falls back to :data:`DEFAULT_MODEL`), ``LLM_API_KEY``
    and ``LLM_BASE_URL``. A bare model name with no ``provider:`` prefix is treated
    as Anthropic. ``LLM_BASE_URL`` implies an OpenAI-compatible endpoint, so an
    unprefixed name is sent as ``openai:<name>`` in that case. Anything in
    ``overrides`` wins over the env-derived values.
    """
    if load_env:
        load_dotenv()

    name = (os.getenv(ENV_MODEL_NAME) or "").strip() or DEFAULT_MODEL
    api_key = (os.getenv(ENV_API_KEY) or "").strip()
    base_url = (os.getenv(ENV_BASE_URL) or "").strip()

    kwargs: dict[str, Any] = {}
    if ":" not in name:
        name = f"openai:{name}" if base_url else f"anthropic:{name}"
    if api_key:
        kwargs["api_key"] = api_key
    if base_url:
        kwargs["base_url"] = base_url
    kwargs.update(overrides)
    return get_chat_model(name, **kwargs)
