"""Individual structural invariants over a ProjectedTree. Each yields Issues."""
from __future__ import annotations

from typing import Iterator

from bts_organizer.domain.models import Answer, Issue, ProjectedTree, ProjHangMuc


def i_skeleton(hm: ProjHangMuc) -> Iterator[Issue]:
    ct = [f for f in hm.folders if f.is_cong_tac]
    if not ct:
        return  # mục 1 / 10 — không áp dụng luật cặp
    if len(ct) < 2:
        yield Issue(hm.id, "too_few_folders", "REPAIRABLE",
                    f"chỉ {len(ct)} thư mục công tác", "scaffold ≥2 + 'Hình ảnh khác'")
    if len(ct) % 2:
        yield Issue(hm.id, "odd_folder_count", "REPAIRABLE",
                    f"{len(ct)} thư mục công tác (phải theo cặp)", "tách 1 cấu kiện thành chuẩn bị + đo")


def i_khac(hm: ProjHangMuc) -> Iterator[Issue]:
    if any(f.is_cong_tac for f in hm.folders) and not any(f.is_khac for f in hm.folders):
        yield Issue(hm.id, "missing_khac", "REPAIRABLE", "thiếu 'Hình ảnh khác'", "tạo (rỗng cũng được)")


def i_even_images(hm: ProjHangMuc) -> Iterator[Issue]:
    for f in hm.folders:
        if f.is_cong_tac and len(f.images) % 2:
            yield Issue(hm.id, "odd_images", "REPAIRABLE",
                        f"{_leaf(f.path)}: {len(f.images)} ảnh",
                        "đẩy 1 ảnh (--0--, muộn nhất) → 'Hình ảnh khác'", folder=f.path)
        if f.is_cong_tac and len(f.images) > 4:
            yield Issue(hm.id, "too_many_images", "INFO",
                        f"{_leaf(f.path)}: {len(f.images)} ảnh (SOP ưu tiên 4)", folder=f.path)


def i_blueprint(hm: ProjHangMuc, answers: dict[str, Answer]) -> Iterator[Issue]:
    bp = {a.q_id.split(":", 1)[1] for a in answers.values() if a.is_blueprint}
    for f in hm.folders:
        if f.is_khac:
            continue
        for img in f.images:
            if img in bp:
                yield Issue(hm.id, "blueprint_in_report", "REPAIRABLE",
                            f"bản vẽ {_leaf(img)} trong {_leaf(f.path)}",
                            "move → 'Hình ảnh khác tổng thể cột anten'", folder=f.path)


def i_conservation(tree: ProjectedTree, original: set[str]) -> Iterator[Issue]:
    after = tree.images_after
    if len(after) != len(original):
        yield Issue(None, "count_mismatch", "HARD",
                    f"{len(original)} ảnh gốc → {len(after)} sau khi sắp", "ABORT")
    lost = original - after
    if lost:
        yield Issue(None, "orphan_image", "HARD",
                    f"{len(lost)} ảnh biến mất: {sorted(lost)[:3]}", "ABORT")
    invented = after - original
    if invented:
        yield Issue(None, "invented_image", "HARD",
                    f"{len(invented)} ảnh lạ xuất hiện: {sorted(invented)[:3]}", "ABORT")


def _leaf(path: str) -> str:
    return path.rsplit("/", 1)[-1]
