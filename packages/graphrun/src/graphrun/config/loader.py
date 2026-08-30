from __future__ import annotations

import os
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # py310
    import tomli as tomllib


def _dig(d: dict, dotted: str, default: Any) -> Any:
    cur: Any = d
    for part in dotted.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return default
    return cur


class Config:
    """Read-only view over merged config (rules TOML + CLI/env overrides)."""

    def __init__(self, data: dict[str, Any] | None = None) -> None:
        self._data = data or {}

    def get(self, key: str, default: Any = None) -> Any:
        return _dig(self._data, key, default)

    def __getitem__(self, key: str) -> Any:
        return _dig(self._data, key, None)

    @property
    def data(self) -> dict[str, Any]:
        return self._data

    @classmethod
    def load(cls, rules: str | Path | None = None, overrides: dict | None = None) -> "Config":
        data: dict[str, Any] = {}
        if rules:
            data = tomllib.loads(Path(rules).read_text(encoding="utf-8"))
        for k, v in (overrides or {}).items():
            if v is None:
                continue
            cur = data
            *parents, leaf = k.split(".")          # 'vision.max=50' -> data['vision']['max']
            for p in parents:
                cur = cur.setdefault(p, {}) if isinstance(cur.get(p), (dict, type(None))) else cur[p]
            cur[leaf] = _coerce(v)
        return cls(data)


def _coerce(v: Any) -> Any:
    if not isinstance(v, str):
        return v
    low = v.lower()
    if low in ("true", "false"):
        return low == "true"
    try:
        return int(v)
    except ValueError:
        try:
            return float(v)
        except ValueError:
            return v


def load_dotenv(start: str | Path | None = None) -> None:
    base = Path(start or Path.cwd())
    env = next((p / ".env" for p in [base, *base.parents] if (p / ".env").is_file()), None)
    if not env:
        return
    for raw in env.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, val = line.partition("=")
        os.environ.setdefault(k.strip(), val.strip().strip('"').strip("'"))
