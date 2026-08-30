from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RunRequest(BaseModel):
    input: str = Field(..., description="Input folder path.")
    output: str = Field(..., description="Output folder path.")
    apply: bool = Field(True, description="Write changes (default: true).")
    rules: str | None = Field(None, description="Path to a rules .toml (default: the feature's).")
    overrides: dict[str, Any] = Field(default_factory=dict, description="Config key overrides.")


class FeatureInfo(BaseModel):
    name: str
    summary: str
