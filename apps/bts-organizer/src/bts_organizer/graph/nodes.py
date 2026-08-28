"""Graph nodes as closures over AppConfig. Each: StationState -> partial StationState."""
from __future__ import annotations

from pathlib import Path

from bts_organizer.config import AppConfig
from bts_organizer.discovery import locate, take_inventory
from bts_organizer.domain.catalog import OPTIONAL_WHEN_EMPTY
from bts_organizer.domain.metadata import read_meta
from bts_organizer.execution import apply_plan, original_images, simulate
from bts_organizer.graph.state import StationState
from bts_organizer.layout import run_strategy
from bts_organizer.planning import build_operations
from bts_organizer.repair import failing_hang_muc, repair
from bts_organizer.reporting import build_report
from bts_organizer.validation import validate
from bts_organizer.vision import build_resolver


def make_nodes(config: AppConfig) -> dict:
    def discover(s: StationState) -> dict:
        p = locate(s["root"])
        return {
            "root": str(Path(s["root"]).resolve()),
            "image_root": str(p.image_root),
            "data_dir": str(p.data_dir) if p.data_dir else "",
        }

    def read_meta_node(s: StationState) -> dict:
        return {"meta": read_meta(Path(s["data_dir"]) if s.get("data_dir") else None)}

    def inventory_node(s: StationState) -> dict:
        inv = take_inventory(Path(s["root"]), Path(s["image_root"]), s["meta"])
        present = [
            i for i, hm in sorted(inv.items())
            if (config.only is None or i in config.only)
            and not (i in OPTIONAL_WHEN_EMPTY and hm.image_count == 0)
        ]
        return {"inventory": inv, "present": present, "repair_iters": 0}

    def plan_layout(s: StationState) -> dict:
        answers = s.get("answers", {})
        layouts, questions = {}, []
        for i in s["present"]:
            L = run_strategy(s["inventory"][i], s["meta"], answers)
            layouts[i] = L
            questions.extend(L.questions)
        return {"layouts": layouts, "questions": questions}

    def resolve_ambiguity(s: StationState) -> dict:
        args = (s["questions"], s.get("answers", {}), s.get("q_attempts", {}))
        try:
            return build_resolver(config, Path(s["root"])).run(*args)
        except Exception as exc:  # bad key / network / provider -> degrade, don't abort
            import sys

            from bts_organizer.vision import HeuristicResolver

            print(f"[vision] LLM failed, using heuristic: {type(exc).__name__}: {exc}", file=sys.stderr)
            return HeuristicResolver(max_attempts=1).run(*args)

    def build_ops(s: StationState) -> dict:
        return {"operations": build_operations(s["layouts"], s["inventory"])}

    def simulate_node(s: StationState) -> dict:
        return {"projected": simulate(s["layouts"], s["inventory"])}

    def validate_node(s: StationState) -> dict:
        issues = validate(
            s["projected"],
            original=original_images(s["inventory"]),
            answers=s.get("answers", {}),
        )
        return {"issues": issues}

    def repair_node(s: StationState) -> dict:
        layouts, _ = repair(s["layouts"], s["issues"])
        return {"layouts": layouts, "repair_iters": s.get("repair_iters", 0) + 1}

    def drop_failing(s: StationState) -> dict:
        bad = set(failing_hang_muc(s["issues"]))
        layouts = {k: v for k, v in s["layouts"].items() if k not in bad}
        return {"layouts": layouts, "manual_review": sorted(bad), "skip_validate": True}

    def execute(s: StationState) -> dict:
        if s.get("dry_run", True):
            return {"exec_results": []}
        return {"exec_results": apply_plan(s["root"], s["operations"], passes=config.max_exec_passes)}

    def report_node(s: StationState) -> dict:
        rep = build_report(
            station=Path(s["root"]).name,
            meta=s["meta"],
            inventory=s["inventory"],
            layouts=s["layouts"],
            tree=s["projected"],
            operations=s["operations"],
            issues=s.get("issues", []),
            answers=s.get("answers", {}),
            questions=s.get("questions", []),
            repair_iters=s.get("repair_iters", 0),
            exec_results=s.get("exec_results", []),
            manual_review=s.get("manual_review", []),
            dry_run=s.get("dry_run", True),
        )
        return {"report": rep}

    return {
        "discover": discover,
        "read_meta": read_meta_node,
        "inventory": inventory_node,
        "plan_layout": plan_layout,
        "resolve_ambiguity": resolve_ambiguity,
        "build_ops": build_ops,
        "simulate": simulate_node,
        "validate": validate_node,
        "repair": repair_node,
        "drop_failing": drop_failing,
        "execute": execute,
        "report": report_node,
    }
