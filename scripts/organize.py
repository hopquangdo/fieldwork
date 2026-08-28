r"""BTS photo organizer — one script, input folder -> output folder.

    uv run python scripts/organize.py <INPUT> <OUTPUT> [--no-vision] [--workspace]

INPUT   a station folder (has the numbered hạng mục sub-folders), OR
        with --workspace, a folder containing several station folders.
        INPUT is copied, never modified.
OUTPUT  where the organized result is written (OUTPUT/<station name>/...).
        Files are actually moved here (no dry-run mode).

JSON reports always go to  <repo>/.output/<input-folder-name>-<runid>.json

Needs .env at repo root for vision:  LLM_API_KEY / LLM_MODEL_NAME / LLM_BASE_URL
All FS ops use \\?\ so deep Vietnamese trees survive Windows MAX_PATH.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from dataclasses import asdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "apps" / "bts-organizer" / "src"))
sys.path.insert(0, str(REPO / "packages" / "agent-core" / "src"))
sys.path.insert(0, str(REPO / "packages" / "filesystem-tools" / "src"))

PREFIX = "\\\\?\\"
OUTPUT_DIR = REPO / ".output"


def lp(p) -> str:
    return PREFIX + os.path.abspath(p) if os.name == "nt" else str(p)


def rmtree(target: Path) -> None:
    if not os.path.exists(lp(target)):
        return
    for root, dirs, files in os.walk(lp(target), topdown=False):
        for f in files:
            os.remove(os.path.join(root, f))
        for d in dirs:
            os.rmdir(os.path.join(root, d))
    os.rmdir(lp(target))


def copytree(src: Path, dst: Path) -> int:
    n = 0
    for root, _, files in os.walk(lp(src)):
        rel = root[len(lp(src)):].strip("\\/")
        out = os.path.join(dst, rel) if rel else str(dst)
        os.makedirs(lp(out), exist_ok=True)
        for f in files:
            with open(os.path.join(root, f), "rb") as r, open(lp(os.path.join(out, f)), "wb") as w:
                w.write(r.read())
            n += 1
    return n


def summary(name: str, d: dict) -> None:
    print(f"\n=== {name} ===")
    print(f"  ảnh {d['images_before']} -> {d['images_after']}   aborted={d['aborted']}   "
          f"repair={d['repair_iters']}   vision={len(d['vision'])}   unresolved={len(d['unresolved'])}")
    print(f"  ops: {d['operations']}   exec: {d['exec']['status']} "
          f"(applied {d['exec']['applied']}, failed {d['exec']['failed']})")
    for c in d["counts"]:
        print(f"    Mục {c['id']:>2}: {c['folders']} thư mục · {c['images']} ảnh"
              f"{'' if c['even_folders'] else '   <-- LẺ'}{('  · ' + c['note']) if c['note'] else ''}")
    for g in d["gaps"]:
        print(f"  ⚠ {g}")
    for e in d["errors"]:
        print(f"  ! {e}")


def one(input_station: Path, out_root: Path, cfg, runid: str) -> dict:
    from bts_organizer.runner import report_to_dict, run_station

    name = input_station.name
    work = out_root / name
    print(f"[{name}] copy -> {work}")
    rmtree(work)
    print(f"  {copytree(input_station, work)} file copied")

    report = report_to_dict(run_station(work, config=cfg))

    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / f"{name}-{runid}.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    summary(name, report)
    return report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--no-vision", action="store_true")
    ap.add_argument("--workspace", action="store_true")
    args = ap.parse_args(argv)

    from agent_core import load_dotenv
    from bts_organizer.config import load_config
    from bts_organizer.discovery import find_stations

    load_dotenv()
    cfg = load_config(dry_run=False, no_vision=args.no_vision)

    inp = Path(args.input).resolve()
    out = Path(args.output).resolve()
    runid = uuid.uuid4().hex
    os.makedirs(lp(out), exist_ok=True)

    stations = find_stations(inp) if args.workspace else [inp]
    if not stations:
        print(f"no stations under {inp}", file=sys.stderr)
        return 2

    reports = []
    for st in stations:
        try:
            reports.append(one(Path(st), out, cfg, runid))
        except Exception as exc:  # per-station isolation
            print(f"  ! {Path(st).name}: {type(exc).__name__}: {exc}", file=sys.stderr)

    ok = sum(1 for r in reports if not r["aborted"])
    print(f"\n{ok}/{len(stations)} station(s) OK  ·  reports: {OUTPUT_DIR}  (run {runid})")
    return 0 if ok == len(stations) else 1


if __name__ == "__main__":
    sys.exit(main())
