"""Mục 1 — Hình ảnh tổng thể cột anten. Named report folders; timestamp-only names -> vision."""
from __future__ import annotations

from collections import defaultdict

from bts_organizer.domain.catalog import KHAC_TONG_THE
from bts_organizer.domain.models import Answer, HangMucInventory, LayoutResult, StationMeta
from bts_organizer.layout.base import folder, place_or_ask

MAP = {
    "biển": "Biển nhà trạm", "bien": "Biển nhà trạm",
    "mặt bằng": "Tổng thể mặt bằng trạm BTS", "mat bang": "Tổng thể mặt bằng trạm BTS",
    "mặt đứng": "Mặt đứng cột anten", "mat dung": "Mặt đứng cột anten",
    "thiết bị": "Thiết bị trên cột", "thiet bi": "Thiết bị trên cột",
}
CANDIDATES = [
    "Biển nhà trạm", "Tổng thể mặt bằng trạm BTS", "Mặt đứng cột anten",
    "Thiết bị trên cột", KHAC_TONG_THE,
]


def _match(prefix: str) -> str | None:
    for k, v in MAP.items():
        if k in prefix:
            return v
    return None


def _existing_name(inv: HangMucInventory, canonical: str) -> str:
    """Reuse an already-correct subfolder if the station has one (SOP: 'đủ thì giữ nguyên')."""
    key = canonical.casefold()
    for sd in inv.subdirs:
        leaf = sd.rsplit("/", 1)[-1].casefold()
        if key in leaf or leaf in key:
            return sd.rsplit("/", 1)[-1]
    return canonical


def plan(inv: HangMucInventory, meta: StationMeta, answers: dict[str, Answer]) -> LayoutResult:
    named: dict[str, list[str]] = defaultdict(list)
    khac_tt: list[str] = []
    questions = []
    khac_name = _existing_name(inv, KHAC_TONG_THE)
    for f in inv.files:
        fld, q, is_bp = place_or_ask(
            f, inv, answers, match=_match, kind="pick_muc1", candidates=CANDIDATES
        )
        if is_bp or fld == KHAC_TONG_THE:
            khac_tt.append(f)
        elif fld:
            named[_existing_name(inv, fld)].append(f)
        else:
            if q:
                questions.append(q)
            khac_tt.append(f)

    folders = [folder(inv, name, imgs) for name, imgs in sorted(named.items())]
    folders.append(folder(inv, khac_name, khac_tt, khac=True))
    return LayoutResult(inv.id, folders, delete_dirs=inv.template_junk, questions=questions)
