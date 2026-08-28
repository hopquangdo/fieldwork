"""Helpers shared by every hạng mục strategy. Pure — no I/O, no LLM."""
from __future__ import annotations

from collections import defaultdict
from typing import Callable

from bts_organizer.domain.catalog import KHAC
from bts_organizer.domain.models import (
    Answer,
    DesiredFolder,
    HangMucInventory,
    LayoutResult,
    Question,
)
from bts_organizer.domain.naming import parse


def current_dir(rel_path: str) -> str:
    return rel_path.rsplit("/", 1)[0] if "/" in rel_path else ""


def is_primary(rel_path: str) -> bool:
    return "--1--" in rel_path


def folder(inv: HangMucInventory, name: str, imgs, *, cong_tac=False, khac=False) -> DesiredFolder:
    return DesiredFolder(
        path=f"{inv.dir}/{name}", images=list(imgs), is_cong_tac=cong_tac, is_khac=khac
    )


def group_by(files: list[str], keyfn: Callable[[str], object]) -> dict[object, list[str]]:
    """Group by keyfn(component_prefix). None key = filename had no parseable component."""
    out: dict[object, list[str]] = defaultdict(list)
    for f in files:
        c = parse(f)
        out[keyfn(c.prefix) if c else None].append(f)
    return dict(out)


def trim_even(imgs: list[str], prefer: int = 4) -> tuple[list[str], list[str]]:
    """Return (kept, surplus): kept has an even length ≤ prefer, primary + earliest first."""
    ordered = sorted(imgs, key=lambda f: (not is_primary(f), f))
    n = min(prefer, len(ordered))
    if n % 2:
        n -= 1
    return ordered[:n], ordered[n:]


def split_labels(leaf: str) -> tuple[str, str]:
    """('Công tác chuẩn bị X', 'Công tác X') from any existing folder leaf name."""
    core = leaf
    for pre in ("Công tác chuẩn bị ", "Công tác đo ", "Công tác kiểm tra ", "Công tác "):
        if core.startswith(pre):
            core = core[len(pre):]
            break
    return f"Công tác chuẩn bị {core}", f"Công tác {core}"


def scaffold(inv: HangMucInventory, base: str) -> list[DesiredFolder]:
    return [
        folder(inv, f"Công tác chuẩn bị {base}", [], cong_tac=True),
        folder(inv, f"Công tác {base}", [], cong_tac=True),
    ]


def ensure_min_two(inv: HangMucInventory, folders: list[DesiredFolder], base: str) -> list[DesiredFolder]:
    ct = [f for f in folders if f.is_cong_tac]
    if len(ct) >= 2:
        return folders
    if len(ct) == 1 and ct[0].images:
        imgs = ct[0].images
        half = (len(imgs) + 1) // 2
        prep, main = split_labels(ct[0].path.rsplit("/", 1)[1])
        rest = [f for f in folders if not f.is_cong_tac]
        return [
            folder(inv, prep, imgs[:half], cong_tac=True),
            folder(inv, main, imgs[half:], cong_tac=True),
            *rest,
        ]
    rest = [f for f in folders if not f.is_cong_tac]
    return [*scaffold(inv, base), *rest]


def with_khac(inv: HangMucInventory, folders: list[DesiredFolder], extra: list[str]) -> list[DesiredFolder]:
    for f in folders:
        if f.is_khac:
            f.images.extend(extra)
            return folders
    folders.append(folder(inv, KHAC, extra, khac=True))
    return folders


def place_or_ask(
    file: str,
    inv: HangMucInventory,
    answers: dict[str, Answer],
    *,
    match: Callable[[str], str | None],
    kind: str,
    candidates: list[str],
) -> tuple[str | None, Question | None, bool]:
    """Returns (folder_name, question, is_blueprint). folder_name None => unresolved."""
    qid = f"m{inv.id}:{file}"
    if qid in answers:
        a = answers[qid]
        return a.folder, None, a.is_blueprint
    c = parse(file)
    if c is not None:
        hit = match(c.prefix)
        if hit is not None:
            return hit, None, False
    return None, Question(id=qid, image=file, hm_id=inv.id, kind=kind, candidates=candidates), False


def keep_in_place(inv: HangMucInventory) -> LayoutResult:
    """Group every file into its current directory -> zero moves."""
    from bts_organizer.domain.catalog import is_cong_tac_folder, is_khac_folder

    groups: dict[str, list[str]] = defaultdict(list)
    for f in inv.files:
        groups[current_dir(f) or inv.dir].append(f)
    folders = []
    for d, imgs in sorted(groups.items()):
        name = d.rsplit("/", 1)[-1]
        folders.append(
            DesiredFolder(path=d, images=imgs, is_cong_tac=is_cong_tac_folder(name), is_khac=is_khac_folder(name))
        )
    return LayoutResult(inv.id, folders, delete_dirs=[])
