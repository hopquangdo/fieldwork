import pytest
from langchain_core.tools import StructuredTool

from agent_core import ToolCall, ToolExecutor, UnknownToolError


def add(left: int, right: int) -> int:
    """Add two integers."""
    return left + right


def fail() -> None:
    """Raise a predictable test error."""
    raise ValueError("boom")


def test_executor_runs_registered_tools_in_order() -> None:
    executor = ToolExecutor([StructuredTool.from_function(add, name="add")])

    results = executor.run([ToolCall("add", {"left": 2, "right": 3})])

    assert executor.tool_names == ("add",)
    assert results[0].ok
    assert results[0].output == 5


def test_executor_captures_errors_and_can_stop() -> None:
    executor = ToolExecutor([StructuredTool.from_function(fail, name="fail")])

    results = executor.run([
        ToolCall("fail", {}),
        ToolCall("fail", {}),
    ])

    assert len(results) == 1
    assert results[0].error == "ValueError: boom"
    assert not results[0].ok


def test_executor_rejects_unknown_tool() -> None:
    executor = ToolExecutor([])

    with pytest.raises(UnknownToolError, match="unknown tool"):
        executor.invoke(ToolCall("missing", {}))