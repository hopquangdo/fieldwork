from __future__ import annotations

import functools
from typing import Callable

from graphrun.core.context import RunContext
from graphrun.core.state import GraphState

NodeFn = Callable[[RunContext], None]


def node(name: str, *, soft: bool = False):
    """Turn a ``(ctx) -> None`` function into a LangGraph node.

    - records a timed :class:`~graphrun.observability.report.Stage`
    - no-ops if the run is already aborted
    - on exception: ``soft=False`` -> mark the run aborted (default);
      ``soft=True`` -> mark this stage 'skipped' and carry on (for optional steps).
    """

    def decorator(fn: NodeFn):
        @functools.wraps(fn)
        def graph_node(state: GraphState) -> dict:
            ctx = state["ctx"]
            if ctx.report.aborted:
                ctx.report.stages.append(_skipped(name))
                return {}
            ctx.emit("node:start", name)
            try:
                with ctx.report.stage(name):
                    fn(ctx)
            except Exception as exc:  # already logged inside stage()
                if soft:
                    ctx.report.stages[-1].status = "skipped"
                    ctx.report.stages[-1].detail = f"bỏ qua: {type(exc).__name__}: {exc}"
                    ctx.report.errors.pop() if ctx.report.errors else None
                else:
                    ctx.report.aborted = True
            st = ctx.report.stages[-1]
            ctx.emit("node:end", f"{name}\t{st.status}\t{st.detail}\t{st.seconds}")
            return {}

        graph_node.node_name = name
        return graph_node

    return decorator


def _skipped(name: str):
    from graphrun.observability.report import Stage

    return Stage(name=name, status="skipped", detail="(run aborted)")
