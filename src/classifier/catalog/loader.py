"""Profile TOML → :class:`Catalog`. Nguồn: ``[hang_muc]`` + ``[[subfolders]]``
(``ensure`` · ``templates`` · ``khac``) + ``[vision.hints]``."""
from __future__ import annotations

import re
from itertools import product
from pathlib import Path

from domain.canonical import CanonicalNamer
from domain.profile import Profile

from classifier.catalog.expand import values_of
from classifier.catalog.schema import Catalog, Section, Slot

_VAR = re.compile(r"\{(\w+)\}")
RULES_DIR = Path(__file__).resolve().parents[3] / "rules"


def load_profile(tower_type: str | None = None, path: str | Path | None = None) -> Profile:
    """Profile theo đường dẫn, hoặc ``rules/<tower_type>.toml``."""
    if path is None:
        path = RULES_DIR / f"{tower_type}.toml"
    return Profile.load(path)


def _hint(hints: dict, text: str) -> str:
    low = text.casefold()
    return "; ".join(h for k, h in hints.items() if k.casefold() in low)


def build_catalog(prof: Profile, meta=None, hm_dirs: dict[int, str] | None = None) -> Catalog:
    """Mục lục đầy đủ. ``hm_dirs``: tên thư mục hạng mục THỰC TẾ (nếu có) — hạng mục chưa
    có trên đĩa dùng tên chuẩn ``n.Tên``."""
    namer = CanonicalNamer(prof)
    hints = dict(prof.vision.get("hints") or {})
    real = hm_dirs or {}
    sections: list[Section] = []
    for n, title in sorted(prof.hang_muc.items()):
        hm = real.get(n, f"{n}.{title}")
        spec = namer.spec_for(hm) or {}
        sec = Section(n, hm)
        for t in [*(spec.get("ensure") or []), *(spec.get("templates") or [])]:
            vars_ = sorted(set(_VAR.findall(t)))
            if len(vars_) <= 1:
                var = vars_[0] if vars_ else None
                sec.slots.append(Slot(hm, t, var, values_of(prof, var, meta) if var else [],
                                      _hint(hints, f"{hm}/{t}")))
                continue
            for combo in product(*(values_of(prof, v, meta) for v in vars_)):   # nhiều biến: liệt kê sẵn
                name = t
                for v, val in zip(vars_, combo):
                    name = name.replace("{" + v + "}", val)
                sec.slots.append(Slot(hm, name, hint=_hint(hints, f"{hm}/{name}")))
        khac = spec.get("khac") or prof.folders.khac_name
        sec.slots.append(Slot(hm, khac, hint=_hint(hints, hm), is_khac=True))
        sections.append(sec)
    return Catalog(sections, prof.folders.khac_name)
