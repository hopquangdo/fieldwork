from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from bts_organizer.config import load_config
from bts_organizer.runner import report_to_dict, run_station, run_workspace


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="bts-organize", description="Sort BTS inspection photos.")
    ap.add_argument("path")
    ap.add_argument("--apply", action="store_true", help="write to disk (default: dry-run)")
    ap.add_argument("--workspace", action="store_true", help="path holds many stations")
    ap.add_argument("--only", help="comma list of hạng mục ids, e.g. 3,5,9")
    ap.add_argument("--no-vision", action="store_true")
    ap.add_argument("--report", help="write report JSON here")
    args = ap.parse_args(argv)

    config = load_config(
        dry_run=not args.apply,
        no_vision=args.no_vision,
        only=[int(x) for x in args.only.split(",")] if args.only else None,
    )

    if args.workspace:
        reports = [report_to_dict(r) for r in run_workspace(args.path, config=config)]
        out = {"workspace": args.path, "stations": reports}
    else:
        out = report_to_dict(run_station(args.path, config=config))

    text = json.dumps(out, ensure_ascii=False, indent=2)
    if args.report:
        Path(args.report).write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
