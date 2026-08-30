"""``photo-sort`` graphrun feature: pick the rules file, hand off to the graph."""
from __future__ import annotations

from pathlib import Path

from langgraph.graph import StateGraph

from graphrun import Feature, FeatureSpec

from photo_sort.domain.metadata import peek_tower_type
from photo_sort.graph import build_graph

_RULES_DIR = Path(__file__).resolve().parents[2] / "rules"   # apps/photo-sort/rules


class PhotoSortFeature(Feature):
    spec = FeatureSpec(
        name="photo-sort",
        summary="Sắp ảnh kiểm định cột BTS vào cấu trúc thư mục phụ lục",
        # rules/ lives at the app root (apps/photo-sort/rules), not inside the
        # package — it's client-editable config, not code.
        default_rules="../../rules/day_co.toml",
    )

    def rules_for(self, input_path: Path) -> Path:
        """Read TABLEBia to pick day_co / tu_dung rules before Config is loaded."""
        tt = peek_tower_type(Path(input_path))
        cand = _RULES_DIR / f"{tt}.toml"
        return cand if tt and cand.exists() else _RULES_DIR / "day_co.toml"

    def build_graph(self, config) -> StateGraph:
        return build_graph(config)
