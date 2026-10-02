"""Nguồn đầu vào: tự nhận dạng folder phẳng hay cây trạm."""
from __future__ import annotations

from pathlib import Path

from classifier.intake.sources import flat_folder, station_tree


def read_source(root: Path, prof) -> "Batch":   # noqa: F821
    """Có thư mục hạng mục đánh số → cây trạm; còn lại → folder phẳng."""
    if station_tree.detect(root):
        return station_tree.read(root, prof)
    return flat_folder.read(root, prof)
