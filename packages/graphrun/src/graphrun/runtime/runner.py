from __future__ import annotations

from typing import Callable

from graphrun.core.context import RunContext
from graphrun.core.feature import Feature
from graphrun.observability.report import Report

Event = Callable[[str, dict], None]   # (node_name, state_delta) -> None


def run(feature: Feature, ctx: RunContext, *, recursion_limit: int = 100,
        on_event: Event | None = None,
        on_log: Callable[[str, str], None] | None = None) -> Report:
    """Compile the feature's graph and drive it. Per-node stages are recorded by @node.

    ``on_event(node, delta)`` fires after every node — use it to stream progress.
    ``on_log(channel, message)`` is attached to ``ctx`` so nodes can stream sub-steps
    live (node start/end, agent tool calls) as they happen.
    """
    if on_log is not None:
        ctx.on_log = on_log
    graph = feature.build_graph(ctx.config).compile()
    try:
        for update in graph.stream(
            {"ctx": ctx},
            stream_mode="updates",
            config={"recursion_limit": recursion_limit},
        ):
            if on_event:
                for node_name, delta in update.items():
                    try:
                        on_event(node_name, delta if isinstance(delta, dict) else {})
                    except Exception:  # a bad listener must not kill the run
                        pass
    except Exception as exc:  # noqa: BLE001
        ctx.report.abort(f"pipeline crashed: {type(exc).__name__}: {exc}")
    return ctx.report
