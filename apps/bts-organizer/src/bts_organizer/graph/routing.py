from __future__ import annotations

from bts_organizer.config import AppConfig
from bts_organizer.graph.state import StationState


def make_gate_vision(config: AppConfig):
    def gate_vision(s: StationState) -> str:
        if config.no_vision:
            return "build_ops"
        attempts = s.get("q_attempts", {})
        answers = s.get("answers", {})
        pending = [
            q for q in s.get("questions", [])
            if q.id not in answers and attempts.get(q.id, 0) < config.vision.max_attempts
        ]
        return "resolve_ambiguity" if pending else "build_ops"

    return gate_vision


def make_gate_repair(config: AppConfig):
    def gate_repair(s: StationState) -> str:
        issues = s.get("issues", [])
        if s.get("skip_validate"):
            return "execute"
        if any(i.severity == "HARD" for i in issues):
            return "report"
        repairable = [i for i in issues if i.severity == "REPAIRABLE"]
        if not repairable:
            return "execute"
        if s.get("repair_iters", 0) < config.max_repair_iters:
            return "repair"
        return "drop_failing"

    return gate_repair
