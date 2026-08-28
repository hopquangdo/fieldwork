"""Deterministic fixes. Each: (LayoutResult, Issue) -> mutates/returns LayoutResult."""
from __future__ import annotations

from bts_organizer.domain.catalog import KHAC, KHAC_TONG_THE
from bts_organizer.domain.models import DesiredFolder, Issue, LayoutResult
from bts_organizer.layout.base import is_primary, split_labels


def _khac(L: LayoutResult) -> DesiredFolder:
    for f in L.folders:
        if f.is_khac:
            return f
    hm_dir = L.folders[0].path.rsplit("/", 1)[0] if L.folders else ""
    name = KHAC_TONG_THE if L.hm_id == 1 else KHAC
    f = DesiredFolder(path=f"{hm_dir}/{name}", images=[], is_khac=True)
    L.folders.append(f)
    return f


def fix_odd_images(L: LayoutResult, iss: Issue) -> LayoutResult:
    target = next((f for f in L.folders if f.path == iss.folder), None)
    if not target or len(target.images) % 2 == 0 or not target.images:
        return L
    worst = sorted(target.images, key=lambda p: (is_primary(p), p))[0]  # non-primary, earliest name
    target.images.remove(worst)
    _khac(L).images.append(worst)
    return L


def fix_missing_khac(L: LayoutResult, iss: Issue) -> LayoutResult:
    _khac(L)
    return L


def fix_too_few_folders(L: LayoutResult, iss: Issue) -> LayoutResult:
    ct = [f for f in L.folders if f.is_cong_tac]
    hm_dir = L.folders[0].path.rsplit("/", 1)[0]
    if len(ct) == 1 and ct[0].images:
        return _split(L, ct[0])
    for i in range(2 - len(ct)):
        L.folders.insert(0, DesiredFolder(path=f"{hm_dir}/Công tác chuẩn bị {i + 1}", images=[], is_cong_tac=True))
    return L


def fix_odd_folder_count(L: LayoutResult, iss: Issue) -> LayoutResult:
    ct = [f for f in L.folders if f.is_cong_tac]
    if len(ct) % 2 == 0:
        return L
    biggest = max(ct, key=lambda f: len(f.images))
    return _split(L, biggest)


def fix_blueprint_in_report(L: LayoutResult, iss: Issue) -> LayoutResult:
    src = next((f for f in L.folders if f.path == iss.folder), None)
    if not src:
        return L
    dest = _khac(L)
    # move any image that isn't clearly placed — conservatively move all in that folder's flagged set
    moved = [i for i in src.images]
    src.images.clear()
    dest.images.extend(moved)
    return L


def _split(L: LayoutResult, folder: DesiredFolder) -> LayoutResult:
    imgs = folder.images
    half = (len(imgs) + 1) // 2
    base, leaf = folder.path.rsplit("/", 1)
    prep, main = split_labels(leaf)
    L.folders.remove(folder)
    L.folders += [
        DesiredFolder(path=f"{base}/{prep}", images=imgs[:half], is_cong_tac=True),
        DesiredFolder(path=f"{base}/{main}", images=imgs[half:], is_cong_tac=True),
    ]
    return L


FIXERS = {
    "odd_images": fix_odd_images,
    "missing_khac": fix_missing_khac,
    "too_few_folders": fix_too_few_folders,
    "odd_folder_count": fix_odd_folder_count,
    "blueprint_in_report": fix_blueprint_in_report,
}
