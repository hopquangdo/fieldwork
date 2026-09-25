from __future__ import annotations

from typing import TypedDict

from runtime.context import RunContext


class GraphState(TypedDict, total=False):
    """Base graph state. Features may subclass to add reducer-managed keys."""

    ctx: RunContext
