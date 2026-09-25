"""A stateful pretty-printer for ``RunContext.emit`` events — Claude-CLI style.

Wire it as the ``on_log`` sink::

    from infrastructure.observability.console import ConsoleRenderer
    run_feature(..., on_log=ConsoleRenderer())

Event protocol (channel -> tab-joined message):

    node:start   "<name>"
    node:end     "<name>\t<status>\t<detail>\t<seconds>"
    step         "<text>"                     free-form child line under the current node
    agent:head   "<n_issues>\t<iteration>"
    agent:issue  "<hạng mục>\t<kind>\t<detail>"
    agent:tool   "<name>(<args…>)"
    agent:result "<text>"                      result of the last agent:tool
    agent:error  "<text>"
"""
from __future__ import annotations

import sys

_DOT = "⏺"     # ⏺  node / action bullet
_ELB = "⎿"     # ⎿  result elbow
_STATUS = {"ok": "", "error": "  ✗", "skipped": "  ○ (bỏ qua)"}


class ConsoleRenderer:
    """``compact=True`` collapses the noisy detail: keeps node start/end lines,
    the agent round header + first 3 issues, and agent errors — but drops the
    per-tool-call trace and the nodes' ``step`` detail lines."""

    def __init__(self, *, out=None, color: bool | None = None, compact: bool = False) -> None:
        self._out = out or sys.stdout
        self._color = sys.stdout.isatty() if color is None else color
        self._compact = compact
        self._open_node: str | None = None
        self._child_count = 0
        self._pending_tool = False
        self._issue_shown = 0
        self._issue_total = 0

    # -- ansi ----------------------------------------------------------------
    def _c(self, s: str, code: str) -> str:
        return f"\033[{code}m{s}\033[0m" if self._color else s

    def _w(self, line: str = "") -> None:
        self._out.write(line + "\n")
        self._out.flush()

    # -- entry point (matches Callable[[str, str], None]) -------------------
    def __call__(self, channel: str, message: str) -> None:
        p = message.split("\t")
        fn = getattr(self, "_on_" + channel.replace(":", "_"), None)
        if fn:
            fn(p)

    # -- handlers ----------------------------------------------------------
    def _on_node_start(self, p: list[str]) -> None:
        self._close_tool()
        self._w()
        self._w(f"{self._c(_DOT, '1;36')} {self._c(p[0], '1')}")
        self._open_node, self._child_count = p[0], 0

    def _on_node_end(self, p: list[str]) -> None:
        name, status, detail, secs = (p + ["", "", "", ""])[:4]
        self._close_tool()
        body = detail or ("hoàn tất" if status == "ok" else status)
        tail = self._c(f"  ({secs}s)", "2")
        colour = {"ok": "32", "error": "31", "skipped": "33"}.get(status, "0")
        self._w(f"  {self._c(_ELB, colour)}  {body}{_STATUS.get(status, '')}{tail}")
        self._open_node = None

    def _on_step(self, p: list[str]) -> None:
        if self._compact:
            return
        self._close_tool()
        for i, line in enumerate("\t".join(p).split("\n")):
            lead = f"  {self._c(_ELB, '2')}  " if i == 0 else "     "
            self._w(lead + line)
        self._child_count += 1

    def _on_agent_head(self, p: list[str]) -> None:
        n, it = (p + ["?", "?"])[:2]
        self._close_tool()
        self._w(f"  {self._c(_ELB, '2')}  {self._c(f'vòng {it}', '1')} · {n} vấn đề cần sửa")
        self._child_count += 1
        self._issue_shown, self._issue_total = 0, int(n) if n.isdigit() else 0

    def _on_agent_issue(self, p: list[str]) -> None:
        hm, kind, detail = (p + ["", "", ""])[:3]
        cap = 3 if self._compact else 8
        self._issue_shown += 1
        if self._issue_shown <= cap:
            self._w(f"       {self._c('•', '2')} {hm} · {self._c(kind, '33')} · {detail}")
        elif self._issue_shown == cap + 1 and self._issue_total > cap + 1:
            self._w(f"       {self._c(f'… +{self._issue_total - cap} vấn đề nữa', '2')}")

    def _on_agent_tool(self, p: list[str]) -> None:
        if self._compact:
            return
        self._close_tool()
        self._w(f"     {self._c('→', '36')} {self._c(p[0], '36')}")
        self._pending_tool = True
        self._child_count += 1

    def _on_agent_result(self, p: list[str]) -> None:
        if self._compact:
            return
        self._w(f"         {'; '.join(p)}")
        self._pending_tool = False

    def _on_agent_error(self, p: list[str]) -> None:
        self._w(f"         {self._c('✗ ' + '; '.join(p), '31')}")
        self._pending_tool = False

    def _close_tool(self) -> None:
        if self._pending_tool:
            self._w(f"         {self._c('(không có kết quả)', '2')}")
            self._pending_tool = False
