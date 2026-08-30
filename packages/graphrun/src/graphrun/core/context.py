from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from graphrun.config.loader import Config
from graphrun.observability.journal import Journal, NullJournal
from graphrun.observability.report import Report


@dataclass
class RunContext:
    """Everything a node needs. Lives in the graph state under ``state["ctx"]`` (mutable)."""

    input: Path
    output: Path
    config: Config
    report: Report
    dry_run: bool = True
    journal: Journal = field(default_factory=NullJournal)
    data: dict[str, Any] = field(default_factory=dict)   # scratch space shared between nodes
    on_log: Callable[[str, str], None] | None = None     # (channel, message) live progress sink

    def __post_init__(self) -> None:
        self.input = Path(self.input)
        self.output = Path(self.output)

    def emit(self, channel: str, message: str) -> None:
        """Stream a live progress line (node start/end, agent tool calls, …).

        A no-op unless a listener is attached. Listener errors are swallowed.
        """
        if self.on_log:
            try:
                self.on_log(channel, message)
            except Exception:
                pass
