"""Cấu hình runtime — đọc từ biến môi trường.

``.env`` (gốc repo) được nạp 1 lần ở entrypoint (``graphrun.run_feature`` /
``graphrun.cli``), không phải ở đây — module này chỉ ĐỌC ``os.environ``:

    LLM_API_KEY=sk-or-...
    LLM_MODEL_NAME=google/gemini-2.5-flash
    LLM_BASE_URL=https://openrouter.ai/api/v1
"""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    llm_api_key: str
    llm_model: str
    llm_base_url: str
    llm_timeout: int
    llm_max_retries: int

    @property
    def has_llm(self) -> bool:
        return bool(self.llm_api_key)


def settings() -> Settings:
    """Đọc cấu hình hiện tại từ ``os.environ`` (không cache — test đổi env vẫn thấy)."""
    return Settings(
        llm_api_key=(os.getenv("LLM_API_KEY") or "").strip(),
        llm_model=(os.getenv("LLM_MODEL_NAME") or "").strip(),
        llm_base_url=(os.getenv("LLM_BASE_URL") or "").strip(),
        llm_timeout=int(os.getenv("LLM_TIMEOUT") or 90),
        llm_max_retries=int(os.getenv("LLM_MAX_RETRIES") or 1),
    )
