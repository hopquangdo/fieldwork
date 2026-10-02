"""Báo cáo 1 lượt chạy: phân bổ ảnh theo thư mục, ảnh cần người xem, chi phí LLM."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class Report:
    station: str
    tower_type: str = ""
    flat: bool = True
    photos: int = 0
    catalog: list[str] = field(default_factory=list)
    distribution: dict[str, int] = field(default_factory=dict)
    review: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    duplicates: list[str] = field(default_factory=list)
    broken: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    decisions: list[dict] = field(default_factory=list)
    applied: dict = field(default_factory=dict)
    llm: dict = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def save(self, path: Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), ensure_ascii=False, indent=1), encoding="utf-8")
        return path

    def summary(self) -> str:
        lines = [f"{self.station} · {self.tower_type} · {self.photos} ảnh"
                 + (" · đầu vào phẳng" if self.flat else "")]
        for folder, n in sorted(self.distribution.items()):
            lines.append(f"  {n:3d}  {folder}")
        if self.review:
            lines.append(f"cần người xem: {len(self.review)}")
        if self.llm:
            lines.append(f"LLM: {self.llm.get('model')} · {self.llm.get('total_tokens', '?')} token")
        lines += [f"⚠ {w}" for w in self.warnings] + [f"✗ {e}" for e in self.errors]
        return "\n".join(lines)
