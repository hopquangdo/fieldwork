"""Ràng buộc SOP sau khi đã có quyết định: mỗi thư mục công tác có số ảnh CHẴN
(``[structure].even_images``) — thừa 1 thì ảnh kém tin cậy nhất sang 'khác' của hạng mục.
Bỏ qua: 'khác', hạng mục ``keep_as_is``, thư mục ``even_skip``; thư mục 1 ảnh giữ nguyên
nếu ``keep_singletons``."""
from __future__ import annotations

from classifier.catalog import Catalog
from classifier.decide.fuse import Decision


def enforce(decisions: dict[str, Decision], cat: Catalog, prof) -> list[str]:
    st = prof.structure
    if not st.even_images:
        return []
    groups: dict[str, list[Decision]] = {}
    for d in decisions.values():
        groups.setdefault(d.folder, []).append(d)
    moved: list[str] = []
    for folder, ds in groups.items():
        sec = cat.section_of(folder)
        if sec is None or folder == sec.khac.option or len(ds) % 2 == 0:
            continue
        if any(sec.folder.startswith(k) for k in st.keep_as_is):
            continue
        if any(k.casefold() in folder.casefold() for k in st.even_skip):
            continue
        if len(ds) == 1 and st.keep_singletons:
            continue
        worst = min(ds, key=lambda d: d.confidence)
        worst.folder = sec.khac.option
        moved.append(f"{worst.photo_id}: {folder} lẻ ảnh → {sec.khac.template}")
    return moved
