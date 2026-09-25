"""In-memory async job runner for the HTTP API. Swap for Redis/DB in production."""
from __future__ import annotations

import queue
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field, is_dataclass
from typing import Any

from application.services.run_graph import run_feature

_SENTINEL = object()


@dataclass
class Job:
    id: str
    feature: str
    params: dict
    status: str = "queued"            # queued | running | done | error
    created: float = field(default_factory=time.time)
    report: dict | None = None
    error: str | None = None
    _events: "queue.Queue" = field(default_factory=queue.Queue, repr=False)

    def summary(self) -> dict:
        return {
            "id": self.id, "feature": self.feature, "status": self.status,
            "created": self.created, "error": self.error,
            "report": self.report,
        }


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()

    def create(self, feature: str, params: dict) -> Job:
        with self._lock:
            job = Job(id=uuid.uuid4().hex[:12], feature=feature, params=params)
            self._jobs[job.id] = job
        return job

    def get(self, jid: str) -> Job | None:
        return self._jobs.get(jid)

    def list(self) -> list[Job]:
        return sorted(self._jobs.values(), key=lambda j: j.created, reverse=True)


STORE = JobStore()


def start(job: Job) -> None:
    def worker() -> None:
        job.status = "running"
        job._events.put({"event": "start", "data": {"job": job.id, "feature": job.feature}})

        def on_event(node: str, delta: dict) -> None:
            job._events.put({"event": "node", "data": {"node": node}})

        def on_log(channel: str, message: str) -> None:
            job._events.put({"event": "log", "data": {"channel": channel, "message": message}})

        try:
            report = run_feature(job.feature, **job.params, on_event=on_event, on_log=on_log)
            job.report = asdict(report) if is_dataclass(report) else dict(report)
            job.status = "done"
            job._events.put({"event": "done", "data": job.report})
        except Exception as exc:  # noqa: BLE001
            job.status = "error"
            job.error = f"{type(exc).__name__}: {exc}"
            job._events.put({"event": "error", "data": {"error": job.error}})
        finally:
            job._events.put(_SENTINEL)

    threading.Thread(target=worker, daemon=True).start()


def sse_stream(job: Job):
    """Yield Server-Sent-Event lines until the job finishes."""
    import json

    # replay-ish: if already terminal, emit the final state once
    if job.status in ("done", "error") and job._events.empty():
        payload = job.report if job.status == "done" else {"error": job.error}
        yield f"event: {job.status}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"
        return
    while True:
        item = job._events.get()
        if item is _SENTINEL:
            return
        yield f"event: {item['event']}\ndata: {json.dumps(item['data'], ensure_ascii=False)}\n\n"
