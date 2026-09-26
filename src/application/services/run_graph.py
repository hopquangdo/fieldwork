"""One call that CLI / API / notebooks all share.

Every run gets a ``run_id``. Both artifacts land in ``report_dir`` (default ``.output``):

    .output/<target>-<run_id>.json     the report
    .output/<target>-<run_id>.jsonl    the journal  (op log, used to resume)
"""
from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any, Callable

from config.loader import Config, load_dotenv
from runtime.context import RunContext
from infrastructure.persistence.journal import Journal
from infrastructure.observability.report import Report
from runtime.registry import get_feature
from runtime.runner import Event, run
from domain import sections as S


def new_run_id() -> str:
    return uuid.uuid4().hex[:12]


def free_dir(path: Path) -> Path:
    """Thư mục kết quả chưa có dữ liệu: ``path`` nếu chưa tồn tại / rỗng, không thì
    ``path (2)``, ``path (3)``… — không bao giờ ghi lẫn vào kết quả cũ."""
    cand, n = path, 1
    while cand.exists() and any(cand.iterdir()):
        n += 1
        cand = path.with_name(f"{path.name} ({n})")
    return cand


def run_feature(
    name: str,
    input: str | Path,
    output: str | Path,
    *,
    rules: str | Path | None = None,
    run_id: str | None = None,
    report_dir: str | Path = ".output",
    resume: str | Path | None = None,
    load_env: bool = True,
    on_event: Event | None = None,
    on_log: Callable[[str, str], None] | None = None,
    **overrides: Any,
) -> Report:
    if load_env:
        load_dotenv()

    feature = get_feature(name)
    inp, out = Path(input).resolve(), Path(output).resolve()
    if not resume:
        out = free_dir(out)
    cfg = Config.load(rules or feature.rules_for(inp), overrides)
    rid = run_id or new_run_id()
    report_dir = Path(report_dir)

    journal_path = (
        Path(resume) if resume and Path(resume).exists()
        else report_dir / f"{inp.name}-{rid}.jsonl"
    )

    ctx = RunContext(
        input=inp,
        output=out,
        config=cfg,
        report=Report(feature=name, target=inp.name, run_id=rid),
        journal=Journal(journal_path),
    )

    report = run(feature, ctx, on_event=on_event, on_log=on_log)
    report.sections[S.OUTPUT_DIR] = str(out)
    report.write_json(report_dir / f"{inp.name}-{rid}.json")
    return report
