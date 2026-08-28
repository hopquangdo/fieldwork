from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from bts_organizer.config import AppConfig
from bts_organizer.graph.nodes import make_nodes
from bts_organizer.graph.routing import make_gate_repair, make_gate_vision
from bts_organizer.graph.state import StationState


def build_graph(config: AppConfig):
    n = make_nodes(config)
    g = StateGraph(StationState)
    for name, fn in n.items():
        g.add_node(name, fn)

    g.add_edge(START, "discover")
    g.add_edge("discover", "read_meta")
    g.add_edge("read_meta", "inventory")
    g.add_edge("inventory", "plan_layout")

    g.add_conditional_edges("plan_layout", make_gate_vision(config),
                            {"resolve_ambiguity": "resolve_ambiguity", "build_ops": "build_ops"})
    g.add_edge("resolve_ambiguity", "plan_layout")          # LOOP 1

    g.add_edge("build_ops", "simulate")
    g.add_edge("simulate", "validate")
    g.add_conditional_edges("validate", make_gate_repair(config),
                            {"repair": "repair", "drop_failing": "drop_failing",
                             "execute": "execute", "report": "report"})
    g.add_edge("repair", "build_ops")                        # LOOP 2
    g.add_edge("drop_failing", "build_ops")

    g.add_edge("execute", "report")
    g.add_edge("report", END)
    return g.compile()


def run(config: AppConfig, root: str) -> "StationState":
    return build_graph(config).invoke(
        {"root": str(root), "dry_run": config.dry_run},
        config={"recursion_limit": 60},
    )
