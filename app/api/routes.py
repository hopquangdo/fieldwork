"""Route handlers for the photo-sort HTTP interface.

    GET  /features                       list registered features
    POST /features/{name}/run            start a job -> {job_id}   (?wait=true for sync)
    GET  /jobs/{id}                      job status + report
    GET  /jobs/{id}/events               SSE stream of per-node progress
    GET  /jobs                           recent jobs
"""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.api.jobs import STORE, sse_stream, start
from app.api.schemas import FeatureInfo, RunRequest
from runtime.registry import load_features

router = APIRouter()


def _allowed_roots() -> list[Path]:
    raw = os.getenv("GRAPHRUN_ALLOWED_ROOTS", "")
    return [Path(p).resolve() for p in raw.split(os.pathsep) if p.strip()]


def _path_map() -> list[tuple[str, str]]:
    r"""``GRAPHRUN_PATH_MAP="D:\=/host/d;E:\data=/data"`` — client gửi đường dẫn của MÁY NÓ,
    server (vd chạy trong Docker) đổi prefix sang chỗ đã mount. Prefix dài khớp trước."""
    pairs = []
    for item in os.getenv("GRAPHRUN_PATH_MAP", "").split(";"):
        if "=" in item:
            src, dst = item.split("=", 1)
            pairs.append((src.strip().replace("\\", "/").rstrip("/").lower(), dst.strip().rstrip("/")))
    return sorted(pairs, key=lambda x: len(x[0]), reverse=True)


def _map(path: str) -> str:
    norm = path.strip().replace("\\", "/")
    for src, dst in _path_map():
        low = norm.lower()
        if low == src or low.startswith(src + "/"):
            return dst + norm[len(src):]
    return path


def _check(path: str) -> str:
    p = Path(_map(path)).expanduser().resolve()
    roots = _allowed_roots()
    if roots and not any(p == r or r in p.parents for r in roots):
        raise HTTPException(403, f"path outside GRAPHRUN_ALLOWED_ROOTS: {p}")
    return str(p)


@router.get("/health")
def health() -> dict:
    return {"ok": True}


@router.get("/features", response_model=list[FeatureInfo])
def features() -> list[FeatureInfo]:
    return [FeatureInfo(name=n, summary=f.spec.summary) for n, f in sorted(load_features().items())]


@router.post("/features/{name}/run")
def run(name: str, req: RunRequest, wait: bool = Query(False)) -> dict:
    if name not in load_features():
        raise HTTPException(404, f"unknown feature {name!r}")
    params = dict(
        input=_check(req.input), output=_check(req.output),
        rules=req.rules, **req.overrides,
    )
    job = STORE.create(name, params)
    start(job)
    if wait:
        while job.status not in ("done", "error"):
            import time as _t

            _t.sleep(0.1)
        return job.summary()
    return {"job_id": job.id, "status": job.status}


@router.get("/jobs")
def jobs() -> list[dict]:
    return [j.summary() for j in STORE.list()[:50]]


@router.get("/jobs/{jid}")
def job(jid: str) -> dict:
    j = STORE.get(jid)
    if not j:
        raise HTTPException(404, "unknown job")
    return j.summary()


@router.get("/jobs/{jid}/events")
def job_events(jid: str) -> StreamingResponse:
    j = STORE.get(jid)
    if not j:
        raise HTTPException(404, "unknown job")
    return StreamingResponse(sse_stream(j), media_type="text/event-stream")
