from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from graphrun.runtime.console import ConsoleRenderer
from graphrun.runtime.registry import load_features
from graphrun.runtime.service import run_feature


def _kv(pairs: list[str]) -> dict:
    return dict(p.split("=", 1) for p in pairs)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="graphrun")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="list registered features")

    r = sub.add_parser("run", help="run a feature")
    r.add_argument("feature")
    r.add_argument("input")
    r.add_argument("output")
    r.add_argument("--dry-run", action="store_true", help="plan only, don't write (default: apply)")
    r.add_argument("--rules", help="path to a rules .toml")
    r.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    r.add_argument("--report-dir", default=".output")
    r.add_argument("--resume", metavar="JOURNAL", help="reuse a previous run's .jsonl to skip done work")
    r.add_argument("--json", action="store_true", help="print the report as JSON")
    r.add_argument("--compact", action="store_true", help="collapse per-tool-call / step detail in the log")

    s = sub.add_parser("serve", help="start the HTTP API (needs graphrun[api])")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=8765)

    args = ap.parse_args(argv)

    if args.cmd == "list":
        for name, feat in sorted(load_features().items()):
            print(f"  {name:<20} {feat.spec.summary}")
        return 0

    if args.cmd == "serve":
        import uvicorn

        uvicorn.run("graphrun.api.app:app", host=args.host, port=args.port)
        return 0

    report = run_feature(
        args.feature, args.input, args.output,
        apply=not args.dry_run, rules=args.rules, resume=args.resume,
        report_dir=args.report_dir,
        on_log=None if args.json else ConsoleRenderer(compact=args.compact),
        **_kv(args.set),
    )

    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        report.render_sections(skip=("agent_repair · nhật ký tool",))
        base = Path(args.report_dir) / f"{Path(args.input).name}-{report.run_id}"
        print(f"\nreport:  {base}.json")
        print(f"journal: {base}.jsonl")
    return 1 if report.aborted else 0


if __name__ == "__main__":
    sys.exit(main())
