"""LLM: dựng model / agent, đếm token + chi phí (VND).

    llm.model() / llm.agent(tools)        model & ReAct agent theo .env (timeout/retry thống nhất)
    llm.usage(ctx) / tracked / publish_usage   token + chi phí cộng dồn cả lượt chạy
    llm.run_sync(coro)                     chạy coroutine từ node đồng bộ

Bảng giá model: ``llm/data/model_prices.json``.
Không import tầng ``agent`` ở cấp module (``agent.agent`` import ngược ``factory``).
"""
from infrastructure.llm.client import agent, available, model, publish_usage, run_sync, tracked, usage
from config.settings import Settings, get_settings, require_llm
from infrastructure.llm.factory import get_chat_model
from infrastructure.llm.pricing import USD_TO_VND, cached_price_for, price_for, usd_to_vnd
from infrastructure.llm.tracker import UsageTracker
from infrastructure.llm.usage import Usage
from infrastructure.llm.utils import model_name_of

__all__ = [
    "agent", "available", "model", "publish_usage", "run_sync", "tracked", "usage",
    "Settings", "get_settings", "require_llm", "get_chat_model",
    "USD_TO_VND", "cached_price_for", "price_for", "usd_to_vnd",
    "Usage", "UsageTracker", "model_name_of",
]
