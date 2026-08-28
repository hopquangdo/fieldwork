"""Composition root: build the LLM once, hold the tuning knobs."""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property

from langchain_core.language_models import BaseChatModel


@dataclass
class VisionConfig:
    model: str | BaseChatModel | None = None   # None -> agent_core.model_from_env()
    max_attempts: int = 2
    max_edge_first: int = 1024
    max_edge_retry: int = 1568


@dataclass
class AppConfig:
    dry_run: bool = True
    no_vision: bool = False
    only: list[int] | None = None              # limit to these hạng mục ids
    prefer_images: int = 4
    max_repair_iters: int = 5
    max_exec_passes: int = 3
    vision: VisionConfig = field(default_factory=VisionConfig)

    def vision_enabled(self) -> bool:
        import os

        if self.no_vision:
            return False
        return self.vision.model is not None or bool(os.getenv("LLM_API_KEY"))

    @cached_property
    def chat_model(self) -> BaseChatModel:
        from agent_core import model_from_env

        m = self.vision.model
        if isinstance(m, BaseChatModel):
            return m
        # reads LLM_MODEL_NAME / LLM_BASE_URL / LLM_API_KEY together (OpenRouter etc.)
        return model_from_env()


def load_config(**overrides) -> AppConfig:
    import os

    try:
        from agent_core import load_dotenv

        load_dotenv()
    except Exception:
        pass

    cfg = AppConfig()
    if os.getenv("BTS_DRY_RUN", "").lower() in ("0", "false", "no"):
        cfg.dry_run = False
    if os.getenv("BTS_NO_VISION", "").lower() in ("1", "true", "yes"):
        cfg.no_vision = True
    for k, v in overrides.items():
        setattr(cfg, k, v)
    return cfg
