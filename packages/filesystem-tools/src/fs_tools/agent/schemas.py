"""Pydantic argument models for the LangChain tools."""
from __future__ import annotations

from pydantic import BaseModel, Field


class Sub(BaseModel):
    subdir: str = Field(".", description="Folder relative to the root.")


class PathArg(BaseModel):
    path: str = Field(..., description="Path relative to the root.")


class Move(BaseModel):
    path: str = Field(..., description="Source path relative to the root.")
    dest_dir: str = Field(..., description="Destination folder relative to the root.")
