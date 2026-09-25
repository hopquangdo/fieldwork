from __future__ import annotations

import json
import time
from pathlib import Path


class Journal:
    """Append-only op log so an interrupted run resumes (skips keys already done)."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._done: set[str] = set()
        if self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    self._done.add(json.loads(line)["key"])

    def done(self, key: str) -> bool:
        return key in self._done

    def record(self, key: str, **extra) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": time.time(), "key": key, **extra}, ensure_ascii=False) + "\n")
        self._done.add(key)


class NullJournal(Journal):
    def __init__(self) -> None:  # noqa: D107
        self.path = Path()
        self._done = set()

    def record(self, key: str, **extra) -> None:  # noqa: D102
        self._done.add(key)
