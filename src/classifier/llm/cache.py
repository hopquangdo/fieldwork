"""Cache JSON đơn giản — khoá do bên gọi dựng (vd sha1 ảnh + vân tay mục lục + model)."""
from __future__ import annotations

import json
from pathlib import Path


class JsonCache:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        try:
            self._data: dict = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self._data = {}

    def get(self, key: str):
        return self._data.get(key)

    def put(self, key: str, value) -> None:
        self._data[key] = value

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._data, ensure_ascii=False, indent=1), encoding="utf-8")
