"""Cấu hình LLM — CHỖ DUY NHẤT đọc ``LLM_*`` (biến môi trường, rồi ``.env`` gần nhất).

    LLM_API_KEY=sk-or-...
    LLM_MODEL_NAME=google/gemini-2.5-flash
    LLM_BASE_URL=https://openrouter.ai/api/v1
    LLM_TIMEOUT=90            (tuỳ chọn)
    LLM_MAX_RETRIES=1         (tuỳ chọn)

Biến môi trường thắng ``.env`` (UI truyền key nhập trên màn hình qua biến môi trường).
Không cache: đọc lại mỗi lần gọi (rẻ) để đổi key / ``.env`` có hiệu lực ngay.
"""
from __future__ import annotations

from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

#: Default model for :func:`infrastructure.llm.factory.get_chat_model` when passed a bare provider string.
DEFAULT_MODEL = "anthropic:claude-sonnet-5"

_MISSING = (
    "Thiếu LLM_API_KEY. Nhập key trên giao diện, hoặc tạo file .env ở gốc repo:\n"
    "  LLM_API_KEY=sk-...\n"
    "  LLM_MODEL_NAME=google/gemini-2.5-flash\n"
    "  LLM_BASE_URL=https://openrouter.ai/api/v1"
)


def _find_env_file() -> Path | None:
    """Nearest ``.env`` walking up from the cwd (pydantic-settings only checks cwd)."""
    cwd = Path.cwd()
    return next((p / ".env" for p in [cwd, *cwd.parents] if (p / ".env").is_file()), None)


class Settings(BaseSettings):
    """Field names map to upper-case env vars (``llm_model_name`` -> ``LLM_MODEL_NAME``).
    Provider-native aliases are accepted where it helps."""

    model_config = SettingsConfigDict(env_file_encoding="utf-8", extra="ignore")

    llm_model_name: str = Field(default="", validation_alias="LLM_MODEL_NAME")
    llm_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("LLM_API_KEY", "OPENROUTER_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"),
    )
    llm_base_url: str = Field(default="", validation_alias=AliasChoices("LLM_BASE_URL", "BASE_URL"))
    llm_temperature: float = 0.0
    llm_max_tokens: int | None = None
    llm_timeout: int = Field(default=90, validation_alias="LLM_TIMEOUT")
    llm_max_retries: int = Field(default=1, validation_alias="LLM_MAX_RETRIES")


def get_settings(*, use_dotenv: bool = True) -> Settings:
    """:class:`Settings` hiện tại. ``use_dotenv=False`` chỉ đọc biến môi trường."""
    return Settings(_env_file=_find_env_file() if use_dotenv else None)


def require_llm() -> Settings:
    """Như :func:`get_settings` nhưng thiếu ``LLM_API_KEY`` → ``RuntimeError`` có hướng dẫn."""
    s = get_settings()
    if not s.llm_api_key.strip():
        raise RuntimeError(_MISSING)
    return s
