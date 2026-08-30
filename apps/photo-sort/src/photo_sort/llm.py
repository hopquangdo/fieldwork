"""Khởi tạo LLM cho các node cần AI (``vision``, ``agent_repair``).

Một chỗ duy nhất đọc ``Settings`` và dựng model/agent — timeout & retry thống nhất.
"""
from __future__ import annotations

from typing import Any

from agent_core import Agent, model_from_env
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool

from photo_sort.config import settings


def available() -> bool:
    """Có LLM_API_KEY để gọi model không."""
    return settings().has_llm


def chat_model(**overrides: Any) -> BaseChatModel:
    """Chat model từ .env (LLM_MODEL_NAME / LLM_API_KEY / LLM_BASE_URL)."""
    s = settings()
    kwargs: dict[str, Any] = {"timeout": s.llm_timeout, "max_retries": s.llm_max_retries}
    kwargs.update(overrides)
    return model_from_env(**kwargs)


def agent(tools: list[BaseTool], *, system: str = "", **overrides: Any) -> Agent:
    """ReAct agent (agent_core) với timeout/retry theo Settings."""
    s = settings()
    kwargs: dict[str, Any] = {"timeout": s.llm_timeout, "max_retries": s.llm_max_retries}
    kwargs.update(overrides)
    return Agent.create(tools, system=system, **kwargs)
