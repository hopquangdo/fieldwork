"""Khởi tạo LLM cho các node cần AI (``vision``, ``agent_repair``).

Một chỗ duy nhất đọc ``Settings`` và dựng model/agent — timeout & retry thống nhất.
"""
from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Any, Awaitable, TypeVar

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool

from config.settings import get_settings, require_llm
from infrastructure.llm.factory import get_chat_model
from infrastructure.llm.tracker import UsageTracker
from infrastructure.llm.usage import Usage
from infrastructure.llm.utils import model_name_of
from domain import sections as S

if TYPE_CHECKING:
    from agent.agent import Agent

_T = TypeVar("_T")


def available() -> bool:
    """Có LLM_API_KEY để gọi model không."""
    return bool(get_settings().llm_api_key.strip())


def model(**overrides: Any) -> BaseChatModel:
    """Chat model từ .env (LLM_MODEL_NAME / LLM_API_KEY / LLM_BASE_URL)."""
    s = require_llm()
    kwargs: dict[str, Any] = {"timeout": s.llm_timeout, "max_retries": s.llm_max_retries}
    kwargs.update(overrides)
    return get_chat_model(**kwargs)


def agent(tools: list[BaseTool], *, system: str = "", **overrides: Any) -> "Agent":
    """ReAct agent (:class:`agent.agent.Agent`) với timeout/retry theo Settings."""
    from agent.agent import Agent   # muộn: agent.agent import infrastructure.llm.factory
    s = require_llm()
    kwargs: dict[str, Any] = {"timeout": s.llm_timeout, "max_retries": s.llm_max_retries}
    kwargs.update(overrides)
    return Agent.create(tools, system=system, **kwargs)


def usage(ctx) -> Usage:
    """Token/chi phí cộng dồn của CẢ lượt chạy (mọi node gọi LLM ghi vào đây)."""
    u = ctx.data.get("llm_usage")
    if u is None:
        u = ctx.data["llm_usage"] = Usage()
    return u


def tracked(ctx, chat_model: BaseChatModel) -> dict:
    """``config`` cho ``.invoke(..., config=...)``: đếm token của lời gọi vào :func:`usage`."""
    u = usage(ctx)
    u.model = u.model or model_name_of(chat_model)
    return {"callbacks": [UsageTracker(u)]}


def publish_usage(ctx) -> None:
    """Ghi usage hiện tại vào báo cáo (section ``llm_usage``) — UI đọc để hiện token + VND."""
    ctx.report.sections[S.LLM_USAGE] = usage(ctx).to_dict()


def run_sync(coro: Awaitable[_T]) -> _T:
    """Chạy 1 coroutine (vd ``Agent.run(...)``) từ code ĐỒNG BỘ (node graph là hàm sync).

    Node graph luôn chạy ngoài event loop (CLI / worker thread của API server) nên bình
    thường chỉ cần ``asyncio.run``; nếu lỡ có event loop đang chạy sẵn (gọi từ context
    async) thì lùi về 1 thread riêng để không đụng loop đó.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    with ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()
