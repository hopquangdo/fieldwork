"""Cấu hình runtime — CHỖ DUY NHẤT kiểm tra ``.env``.

``.env`` (gốc repo) được nạp ở entrypoint (``application.services.run_graph.run_feature`` / ``cli``);
module này chỉ ĐỌC ``os.environ`` và BÁO LỖI nếu thiếu ``LLM_API_KEY``:

    LLM_API_KEY=sk-or-...
    LLM_MODEL_NAME=google/gemini-2.5-flash
    LLM_BASE_URL=https://openrouter.ai/api/v1
"""
from __future__ import annotations

import os
from dataclasses import dataclass

_MISSING = (
    "Thiếu LLM_API_KEY. Tạo file .env ở gốc repo:\n"
    "  LLM_API_KEY=sk-...\n"
    "  LLM_MODEL_NAME=google/gemini-2.5-flash\n"
    "  LLM_BASE_URL=https://openrouter.ai/api/v1"
)


@dataclass(frozen=True)
class Settings:
    llm_api_key: str
    llm_model: str
    llm_base_url: str
    llm_timeout: int
    llm_max_retries: int


def settings() -> Settings:
    """Đọc cấu hình từ ``os.environ`` (không cache). Thiếu ``LLM_API_KEY`` → ``RuntimeError``."""
    key = (os.getenv("LLM_API_KEY") or "").strip()
    if not key:
        raise RuntimeError(_MISSING)
    return Settings(
        llm_api_key=key,
        llm_model=(os.getenv("LLM_MODEL_NAME") or "").strip(),
        llm_base_url=(os.getenv("LLM_BASE_URL") or "").strip(),
        llm_timeout=int(os.getenv("LLM_TIMEOUT") or 90),
        llm_max_retries=int(os.getenv("LLM_MAX_RETRIES") or 1),
    )
