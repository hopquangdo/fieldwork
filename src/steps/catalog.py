"""Dựng MỤC LỤC thư mục chuẩn của trạm TRƯỚC khi phân loại (``[hang_muc]`` +
``[[subfolders]]`` — xem :mod:`classifier.catalog`).

Thư mục được tạo sẵn trên bản làm việc; thư mục mẫu nào cuối cùng không có ảnh và không
nằm trong kế hoạch sẽ bị ``delete_empty`` xoá (SOP: "thư mục mẫu không có ảnh thì xoá").
Folder ảnh PHẲNG (không có hạng mục đánh số) → dùng ``photo-classify`` (:mod:`classifier`).
"""
from __future__ import annotations

from infrastructure.filesystem import MakeDirTool
from runtime import node

from classifier.catalog import build_catalog
from domain.profile import Profile
from domain import sections as S
from domain.state import state

make_dir = MakeDirTool()


@node("catalog")
def catalog(ctx) -> None:
    prof = Profile.of(ctx)
    st = ctx.report.stages[-1]
    if not prof.hang_muc:
        st.status = "skipped"
        st.detail = "profile không khai [hang_muc] — bỏ qua"
        return
    s = state(ctx)
    cat = build_catalog(prof, s.meta, s.hm_dirs)
    leaves = [x for x in cat.leaves() if x != cat.root_khac]
    for rel in leaves:
        make_dir(s.root / rel)
    ctx.report.sections[S.CATALOG] = leaves
    st.detail = f"{len(cat.sections)} hạng mục · {len(leaves)} thư mục"
    ctx.emit("step", st.detail)
