"""Đăng ký ``photo-sort`` với graphrun.

Chọn profile SOP đúng loại cột (đọc nhanh TABLEBia trước khi Config được nạp) rồi
giao việc dựng graph cho :mod:`pipeline.graph`.
"""
from __future__ import annotations

from pathlib import Path

from langgraph.graph import StateGraph

from runtime import Feature, FeatureSpec
from config.loader import register_virtual_files, toml_exists

from domain.profile import Profile
from domain.metadata import peek_tower_type, refine_tower_type
from domain.station import image_root
from pipeline.pipeline import build_graph

_RULES_DIR = Path(__file__).resolve().parents[2] / "rules"   # <repo>/rules
if not _RULES_DIR.is_dir():
    # Bản đóng gói: rules nhúng trong bytecode (scripts/build_dist.py sinh _embedded_rules).
    from pipeline._embedded_rules import RULES as _EMBEDDED

    _RULES_DIR = Path(__file__).resolve().parent / "_rules"
    register_virtual_files({_RULES_DIR / name: text for name, text in _EMBEDDED.items()})
_BASE = _RULES_DIR / "_base.toml"


class PhotoSortFeature(Feature):
    spec = FeatureSpec(
        name="photo-sort",
        summary="Sắp ảnh kiểm định cột BTS vào cấu trúc thư mục phụ lục",
        # rules/ nằm ở gốc repo, ngoài package; thực tế rules_for() luôn chọn file.
        default_rules="../../rules/day_co.toml",
    )

    def rules_for(self, input_path: Path) -> Path:
        """Đọc TABLEBia (pattern lấy từ _base) để chọn profile day_co / tu_dung, rồi cho
        ẢNH THỰC TẾ bác khai báo theo ``[[tower_evidence]]`` của _base."""
        base = Profile.load(_BASE)
        tt = peek_tower_type(Path(input_path), base.metadata)
        tt, _ = refine_tower_type(image_root(Path(input_path)), tt, base.tower_evidence)
        cand = _RULES_DIR / f"{tt}.toml"
        return cand if tt and toml_exists(cand) else _RULES_DIR / "day_co.toml"

    def build_graph(self, config) -> StateGraph:
        return build_graph(config)
