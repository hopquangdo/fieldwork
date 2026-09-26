"""NƠI DUY NHẤT chứa các hàm ``main`` — mọi console-script trỏ về đây.

    photo-sort       -> cli_main    (chạy 1 lần, in ra console)
    photo-sort-eval  -> eval_main   (so kết quả với ground truth)
    photo-sort-engine -> engine_main (list / run / serve; `python -m app.cli.commands serve`)

Toàn bộ logic nằm ở ``core``; file này chỉ
phân tích tham số dòng lệnh rồi gọi vào đó.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from infrastructure.observability.console import ConsoleRenderer
from runtime.registry import load_features
from application.services.run_graph import run_feature

from application.services.sort_photos import sort_photos
from domain import sections as S


# ── photo-sort ────────────────────────────────────────────────────────────
def cli_main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="photo-sort",
        description="Sắp ảnh kiểm định cột BTS vào cấu trúc thư mục phụ lục.",
    )
    ap.add_argument("input", help="thư mục trạm đầu vào")
    ap.add_argument("output", help="thư mục kết quả")
    ap.add_argument("--rules", help="đường dẫn file rules .toml")
    ap.add_argument("--report-dir", default=".output")
    ap.add_argument("--resume", metavar="JOURNAL", help="dùng lại .jsonl của lần chạy trước")
    ap.add_argument("--compact", action="store_true", help="rút gọn log từng tool-call / step")
    ap.add_argument("--json", action="store_true", help="in SortResult dạng JSON")
    args = ap.parse_args(argv)

    renderer = None
    if not args.json:
        from infrastructure.observability.console import ConsoleRenderer

        renderer = ConsoleRenderer(compact=args.compact)

    result = sort_photos(
        args.input, args.output,
        rules=args.rules,
        report_dir=args.report_dir, resume=args.resume,
        on_progress=(lambda msg: renderer("step", msg)) if renderer else None,
    )

    if args.json:
        d = asdict(result)
        d["report_path"] = str(result.report_path)
        d["output_dir"] = str(result.output_dir)
        print(json.dumps(d, ensure_ascii=False, indent=2))
    else:
        for row in result.input_issues:
            print(f"  · {row}")
        print(
            f"\n{result.moves} move · {result.images_before}→{result.images_after} ảnh"
        )
        print(f"output: {result.output_dir}")
        print(f"report: {result.report_path}")
        if result.aborted:
            print("\nABORTED:")
            for e in result.errors:
                print(f"  ! {e}")
    return 1 if result.aborted else 0


# ── photo-sort-eval ──────────────────────────────────────────────────────
def eval_main(argv: list[str] | None = None) -> int:
    from pathlib import Path

    from evaluation.evaluator import discover_pairs, format_result, run_and_compare

    ap = argparse.ArgumentParser(
        prog="photo-sort-eval",
        description="Chạy pipeline rồi so với ground truth (theo nội dung ảnh).",
    )
    ap.add_argument("--input", help="thư mục trạm đầu vào")
    ap.add_argument("--gt", help="thư mục đáp án tương ứng")
    ap.add_argument("--auto", nargs=2, metavar=("DATA", "GT_DIR"),
                    help="quét GT_DIR/*_gt, ghép với DATA/<tên>")
    ap.add_argument("--work", default=".output/_eval", help="thư mục làm việc + cache vision")
    ap.add_argument("--rules", help="file rules .toml (mặc định: tự chọn theo TABLEBia)")
    ap.add_argument("--min-accuracy", type=float, default=0.0,
                    help="dưới ngưỡng này (0-1) thì exit 1 — dùng cho CI")
    args = ap.parse_args(argv)

    if args.auto:
        pairs = discover_pairs(*args.auto)
    elif args.input and args.gt:
        pairs = [(Path(args.input).name, Path(args.input), Path(args.gt))]
    else:
        ap.error("cần --input + --gt, hoặc --auto DATA GT_DIR")
    if not pairs:
        print("không có cặp (input, gt) nào")
        return 1

    worst = 1.0
    for name, src, gt in pairs:
        res = run_and_compare(src, gt, Path(args.work) / name, rules=args.rules)
        print(format_result(res, name=name))
        worst = min(worst, res.accuracy)
    if len(pairs) > 1:
        print(f"\nkém nhất: {worst:.1%}")
    return 0 if worst >= args.min_accuracy else 1


# ── photo-sort-engine ──────────────────────────────────────────────────────────────
def _kv(pairs: list[str]) -> dict:
    return dict(p.split("=", 1) for p in pairs)


def engine_main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="photo-sort-engine")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="list registered features")

    r = sub.add_parser("run", help="run a feature")
    r.add_argument("feature")
    r.add_argument("input")
    r.add_argument("output")
    r.add_argument("--rules", help="path to a rules .toml")
    r.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    r.add_argument("--report-dir", default=".output")
    r.add_argument("--resume", metavar="JOURNAL", help="reuse a previous run's .jsonl to skip done work")
    r.add_argument("--json", action="store_true", help="print the report as JSON")
    r.add_argument("--compact", action="store_true", help="collapse per-tool-call / step detail in the log")

    s = sub.add_parser("serve", help="start the HTTP API ")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=8765)

    args = ap.parse_args(argv)

    if args.cmd == "list":
        for name, feat in sorted(load_features().items()):
            print(f"  {name:<20} {feat.spec.summary}")
        return 0

    if args.cmd == "serve":
        import uvicorn

        uvicorn.run("app.api.app:app", host=args.host, port=args.port)
        return 0

    report = run_feature(
        args.feature, args.input, args.output,
        rules=args.rules, resume=args.resume,
        report_dir=args.report_dir,
        on_log=None if args.json else ConsoleRenderer(compact=args.compact),
        **_kv(args.set),
    )

    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        report.render_sections(skip=(S.AGENT_LOG,))
        base = Path(args.report_dir) / f"{Path(args.input).name}-{report.run_id}"
        print(f"\nreport:  {base}.json")
        print(f"journal: {base}.jsonl")
    return 1 if report.aborted else 0


if __name__ == "__main__":
    sys.exit(engine_main())
