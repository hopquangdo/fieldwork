from __future__ import annotations

import json
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class Stage:
    name: str
    status: str = "ok"          # ok | error | skipped
    detail: str = ""
    seconds: float = 0.0


@dataclass
class Report:
    feature: str = ""
    target: str = ""
    run_id: str = ""
    dry_run: bool = True
    aborted: bool = False
    stages: list[Stage] = field(default_factory=list)
    sections: dict = field(default_factory=dict)     # feature payload
    errors: list[str] = field(default_factory=list)

    @contextmanager
    def stage(self, name: str):
        st = Stage(name=name)
        self.stages.append(st)
        t0 = time.monotonic()
        try:
            yield st
        except Exception as exc:  # noqa: BLE001 — recorded; caller decides
            st.status = "error"
            st.detail = f"{type(exc).__name__}: {exc}"
            self.errors.append(f"{name}: {st.detail}")
            raise
        finally:
            st.seconds = round(time.monotonic() - t0, 3)

    def abort(self, reason: str) -> None:
        self.aborted = True
        self.errors.append(reason)

    def to_dict(self) -> dict:
        return asdict(self)

    def write_json(self, path: str | Path) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    def render_sections(self, *, skip: tuple[str, ...] = ()) -> None:
        """Print only the feature payload (``sections``) + abort info — use after a
        live renderer has already streamed the stages."""
        for k, v in self.sections.items():
            if k in skip:
                continue
            if isinstance(v, list):
                if not v:
                    continue
                print(f"\n{k}  ({len(v)}):")
                for row in v[:12]:
                    print(f"  {row}")
                if len(v) > 12:
                    print(f"  … (+{len(v) - 12}, xem report .json)")
            else:
                print(f"{k}: {v}")
        if self.aborted:
            print("\nABORTED:")
            for e in self.errors:
                print(f"  ! {e}")

    def render_console(self) -> None:
        rid = f" · {self.run_id}" if self.run_id else ""
        print(f"\n=== {self.feature} · {self.target}{rid} · {'DRY-RUN' if self.dry_run else 'APPLIED'} ===")
        for s in self.stages:
            mark = {"ok": "✓", "error": "!", "skipped": "-"}.get(s.status, "?")
            print(f"  {mark} {s.name:<18}{s.detail}  ({s.seconds}s)")
        for k, v in self.sections.items():
            if isinstance(v, list):
                print(f"  · {k}:")
                for row in v[:50]:
                    print(f"      {row}")
            else:
                print(f"  · {k}: {v}")
        if self.aborted:
            print("  ABORTED:")
            for e in self.errors:
                print(f"    ! {e}")
