from __future__ import annotations

from pydantic import BaseModel


class ScanRequest(BaseModel):
    root: str


class OrganizeRequest(BaseModel):
    root: str
    dry_run: bool = True
    no_vision: bool = False
    only: list[int] | None = None


class ApplyRequest(BaseModel):
    root: str
