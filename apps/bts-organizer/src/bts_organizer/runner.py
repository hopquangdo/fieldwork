"""Entry points: one station, or a whole workspace."""
from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path

from bts_organizer.config import AppConfig, load_config
from bts_organizer.discovery import count_images, find_stations
from bts_organizer.domain.models import Report
from bts_organizer.graph import run as run_graph


def run_station(root: str | Path, *, config: AppConfig | None = None) -> Report:
    config = config or load_config()
    final = run_graph(config, str(root))
    return final["report"]


def run_workspace(root: str | Path, *, config: AppConfig | None = None) -> list[Report]:
    config = config or load_config()
    reports: list[Report] = []
    for station in find_stations(root):
        try:
            reports.append(run_station(station, config=config))
        except Exception as exc:  # per-station isolation
            reports.append(Report(station=station.name, errors=[f"{type(exc).__name__}: {exc}"], aborted=True))
    return reports


def scan_workspace(root: str | Path) -> dict:
    root = Path(root).resolve()
    stations = find_stations(root)
    return {
        "root": str(root),
        "directories": sum(1 for _ in root.rglob("*") if _.is_dir()),
        "files": sum(1 for _ in root.rglob("*") if _.is_file()),
        "images": sum(count_images(s) for s in stations),
        "stations": [
            {"name": s.name, "path": s.name, "image_count": count_images(s)} for s in stations
        ],
    }


def report_to_dict(report: Report) -> dict:
    return asdict(report) if is_dataclass(report) else dict(report)
