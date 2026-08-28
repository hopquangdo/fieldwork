"""Deterministic tool execution for plans and non-LLM workflow steps."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from langchain_core.tools import BaseTool


class ToolExecutorError(RuntimeError):
    """Base error for deterministic tool execution."""


class UnknownToolError(ToolExecutorError):
    """Raised when a plan refers to a tool that was not registered."""


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class ToolResult:
    call: ToolCall
    output: Any = None
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None


class ToolExecutor:
    """Execute registered LangChain tools in a predictable, auditable order."""

    def __init__(self, tools: Iterable[BaseTool]) -> None:
        self._tools: dict[str, BaseTool] = {}
        for tool in tools:
            if tool.name in self._tools:
                raise ValueError(f"duplicate tool name: {tool.name!r}")
            self._tools[tool.name] = tool

    @property
    def tool_names(self) -> tuple[str, ...]:
        return tuple(self._tools)

    def invoke(self, call: ToolCall) -> ToolResult:
        tool = self._tools.get(call.name)
        if tool is None:
            raise UnknownToolError(f"unknown tool: {call.name!r}")
        try:
            return ToolResult(call=call, output=tool.invoke(call.arguments))
        except Exception as exc:
            return ToolResult(call=call, error=f"{type(exc).__name__}: {exc}")

    def run(self, calls: Iterable[ToolCall], *, stop_on_error: bool = True) -> list[ToolResult]:
        """Execute calls in order, optionally continuing after a failed call."""
        results: list[ToolResult] = []
        for call in calls:
            result = self.invoke(call)
            results.append(result)
            if stop_on_error and not result.ok:
                break
        return results