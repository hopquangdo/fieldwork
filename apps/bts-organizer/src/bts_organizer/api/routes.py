from __future__ import annotations

from fastapi import APIRouter

from bts_organizer.api.deps import assert_allowed
from bts_organizer.api.schemas import ApplyRequest, OrganizeRequest, ScanRequest
from bts_organizer.config import load_config
from bts_organizer.runner import report_to_dict, run_station, scan_workspace

router = APIRouter()


@router.post("/scan")
def scan(req: ScanRequest) -> dict:
    return scan_workspace(assert_allowed(req.root))


@router.post("/organize")
def organize(req: OrganizeRequest) -> dict:
    root = assert_allowed(req.root)
    config = load_config(dry_run=req.dry_run, no_vision=req.no_vision, only=req.only)
    report = report_to_dict(run_station(root, config=config))
    return {**report, **_legacy_view(report)}


@router.post("/apply")
def apply(req: ApplyRequest) -> dict:
    root = assert_allowed(req.root)
    config = load_config(dry_run=False)
    report = report_to_dict(run_station(root, config=config))
    return {**report, **_legacy_view(report)}


def _legacy_view(report: dict) -> dict:
    """Fields the older UI client reads: steps / results / validation_errors."""
    ops = report.get("operations", {})
    steps = [
        {"name": "Kiểm kê", "status": "ok",
         "detail": f"{report.get('images_before', 0)} ảnh."},
        {"name": "Bố cục + vision", "status": "ok",
         "detail": f"{len(report.get('vision', []))} ảnh phải mở."},
        {"name": "Kiểm tra & sửa", "status": "error" if report.get("aborted") else "ok",
         "detail": f"{report.get('repair_iters', 0)} vòng sửa."},
        {"name": "Thao tác", "status": "ok",
         "detail": f"{ops.get('mkdir', 0)} mkdir · {ops.get('move', 0)} move · {ops.get('rmdir', 0)} rmdir."},
        {"name": "Thực thi", "status": "skipped" if report.get("exec", {}).get("status") == "dry_run" else "ok",
         "detail": report.get("exec", {}).get("status", "")},
    ]
    results = [f"{r['kind']}: {r['label']}" for r in report.get("tree", [])]
    return {
        "steps": steps,
        "results": results,
        "validation_errors": report.get("errors", []),
    }
