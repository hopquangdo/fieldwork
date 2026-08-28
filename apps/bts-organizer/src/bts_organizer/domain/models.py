"""Shared value objects. This module imports nothing internal and no I/O libs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

TowerType = Literal["day_co", "tu_dung", "monopole"]
Severity = Literal["HARD", "REPAIRABLE", "INFO"]


# --- filenames / metadata ---------------------------------------------------

@dataclass(frozen=True)
class Component:
    """Parsed from ``<prefix>@h@m@s@--x--.jpg``."""
    prefix: str
    is_primary: bool
    ts: tuple[int, int, int]


@dataclass
class StationMeta:
    tower_type: TowerType = "day_co"
    n_dot: int = 0
    n_mong: int = 0
    n_tang: int = 0
    source: str = ""
    warnings: list[str] = field(default_factory=list)


# --- inventory -------------------------------------------------------------

@dataclass
class HangMucInventory:
    id: int
    name: str
    dir: str                      # "<n>.<name>" relative to station root
    files: list[str]              # image paths relative to station root
    subdirs: list[str]            # existing subfolders (rel to station root)
    template_junk: list[str] = field(default_factory=list)

    @property
    def image_count(self) -> int:
        return len(self.files)


Inventory = dict[int, HangMucInventory]


# --- layout ---------------------------------------------------------------

@dataclass
class Question:
    id: str
    image: str                   # rel to station root
    hm_id: int
    kind: str                    # "pick_muc1" | "is_blueprint" | "which_component"
    candidates: list[str] = field(default_factory=list)


@dataclass
class Answer:
    q_id: str
    folder: str | None = None    # chosen folder name (rel to hạng mục dir)
    is_blueprint: bool = False
    confidence: float = 0.0
    attempt: int = 0


@dataclass
class DesiredFolder:
    path: str                    # rel to station root, includes the hạng mục dir
    images: list[str] = field(default_factory=list)
    is_cong_tac: bool = False
    is_khac: bool = False


@dataclass
class LayoutResult:
    hm_id: int
    folders: list[DesiredFolder] = field(default_factory=list)
    delete_dirs: list[str] = field(default_factory=list)
    questions: list[Question] = field(default_factory=list)


# --- plan / execution ----------------------------------------------------

@dataclass(frozen=True)
class FileOperation:
    action: Literal["mkdir", "move", "rmdir"]
    path: str                    # mkdir/rmdir: dir; move: source file (rel to station root)
    dest: str = ""               # move: destination folder (rel to station root)


@dataclass(frozen=True)
class Issue:
    hm_id: int | None
    kind: str
    severity: Severity
    detail: str
    fix_hint: str = ""
    folder: str | None = None


@dataclass
class ProjFolder:
    path: str
    images: list[str]
    is_cong_tac: bool = False
    is_khac: bool = False


@dataclass
class ProjHangMuc:
    id: int
    folders: list[ProjFolder]


@dataclass
class ProjectedTree:
    hang_muc: list[ProjHangMuc]
    images_after: set[str]


@dataclass
class Report:
    station: str = ""
    tower_type: str = ""
    images_before: int = 0
    images_after: int = 0
    counts: list[dict] = field(default_factory=list)
    tree: list[dict] = field(default_factory=list)
    operations: dict = field(default_factory=dict)
    vision: list[dict] = field(default_factory=list)
    repair_iters: int = 0
    gaps: list[str] = field(default_factory=list)
    unresolved: list[str] = field(default_factory=list)
    manual_review: list[int] = field(default_factory=list)
    exec: dict = field(default_factory=dict)
    aborted: bool = False
    errors: list[str] = field(default_factory=list)
