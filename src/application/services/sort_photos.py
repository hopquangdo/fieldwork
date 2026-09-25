"""API lập trình của ``photo-sort`` — LÕI dùng chung cho CLI, HTTP, notebook.

Bọc ``engine.run_feature("photo-sort", …)`` và map ``Report`` chung sang
``SortResult`` đúng ngữ cảnh photo-sort. Caller (backend web, service khác, test)
chỉ cần import ``sort_photos`` — không đụng nội bộ ``graphrun``.

    from application.services.sort_photos import sort_photos
    r = sort_photos("D:/in/TRẠM_X", "D:/out", apply=False)
    if r.aborted:
        ...
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from application.services.run_graph import run_feature

#: nhãn section trong Report.sections → thuộc tính SortResult
_INPUT_ISSUES = "vấn đề đầu vào"
_NEEDS_REVIEW = "cần người xem"
_MISSING_PHOTOS = "hạng mục thiếu ảnh (cần nhặt bù)"

ProgressFn = Callable[[str], None]


@dataclass(frozen=True)
class SortResult:
    run_id: str
    aborted: bool
    applied: bool                      # False = dry-run
    tower_type: str
    images_before: int
    images_after: int
    moves: int
    input_issues: list[str] = field(default_factory=list)
    needs_review: list[str] = field(default_factory=list)
    missing_photos: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    report_path: Path | None = None

    @property
    def ok(self) -> bool:
        return not self.aborted


def sort_photos(
    input: str | Path,
    output: str | Path,
    *,
    apply: bool = False,
    rules: str | Path | None = None,
    report_dir: str | Path = ".output",
    resume: str | Path | None = None,
    load_env: bool = True,
    on_progress: ProgressFn | None = None,
) -> SortResult:
    """Chạy feature ``photo-sort``.

    ``apply=False`` (mặc định) → dry-run: chỉ lập kế hoạch, không ghi đĩa.
    ``on_progress`` nhận từng dòng tiến trình (step / node) dạng text.
    """
    on_log = (lambda _channel, message: on_progress(message)) if on_progress else None

    report = run_feature(
        "photo-sort",
        input,
        output,
        apply=apply,
        rules=rules,
        report_dir=report_dir,
        resume=resume,
        load_env=load_env,
        on_log=on_log,
    )
    return _to_result(report, input, report_dir)


def _to_result(report, input: str | Path, report_dir: str | Path) -> SortResult:
    s = report.sections
    meta = s.get("meta") or {}
    return SortResult(
        run_id=report.run_id,
        aborted=report.aborted,
        applied=not report.dry_run,
        tower_type=meta.get("tower_type", ""),
        images_before=int(s.get("images_before", 0) or 0),
        images_after=int(s.get("images_after", 0) or 0),
        moves=len(s.get("plan", []) or []),
        input_issues=list(s.get(_INPUT_ISSUES, []) or []),
        needs_review=list(s.get(_NEEDS_REVIEW, []) or []),
        missing_photos=list(s.get(_MISSING_PHOTOS, []) or []),
        errors=list(report.errors),
        report_path=Path(report_dir) / f"{Path(input).name}-{report.run_id}.json",
    )
