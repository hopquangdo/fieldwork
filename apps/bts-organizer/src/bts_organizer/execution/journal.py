"""Append-only JSONL of applied ops so a re-run can resume."""
from __future__ import annotations

import json
import time
from pathlib import Path

from bts_organizer.domain.models import FileOperation


class Journal:
    def __init__(self, root: Path) -> None:
        self.path = Path(root) / ".bts_organizer" / "journal.jsonl"
        self._done: set[tuple] = set()
        if self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    e = json.loads(line)
                    self._done.add((e["action"], e["path"], e.get("dest", "")))

    def is_done(self, op: FileOperation) -> bool:
        return (op.action, op.path, op.dest) in self._done

    def record(self, op: FileOperation, result: str) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(
                {"ts": time.time(), "action": op.action, "path": op.path, "dest": op.dest, "result": result},
                ensure_ascii=False,
            ) + "\n")
        self._done.add((op.action, op.path, op.dest))
