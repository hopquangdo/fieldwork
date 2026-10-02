"""Danh mục profile SOP trong ``rules/`` — NƠI DUY NHẤT biết thư mục rules nằm đâu.

    list_rules()            → [RuleInfo(name="tu_dung", title=…, path=…), …]  (bỏ file "_*.toml")
    resolve_rules("tu_dung") → Path(".../rules/tu_dung.toml")   (nhận cả tên lẫn đường dẫn)

Bản đóng gói (``scripts/build_dist.py``) không có thư mục ``rules/`` trên đĩa — rules nhúng
trong bytecode (``pipeline._embedded_rules``) và đăng ký làm file ảo.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from config.loader import load_toml, register_virtual_files, toml_exists

RULES_DIR = Path(__file__).resolve().parents[2] / "rules"   # <repo>/rules
_EMBEDDED: dict[str, str] = {}
if not RULES_DIR.is_dir():
    from pipeline._embedded_rules import RULES as _EMBEDDED

    RULES_DIR = Path(__file__).resolve().parents[1] / "pipeline" / "_rules"
    register_virtual_files({RULES_DIR / name: text for name, text in _EMBEDDED.items()})

BASE = RULES_DIR / "_base.toml"


@dataclass(frozen=True)
class RuleInfo:
    name: str          # tên file không đuôi — người dùng chọn bằng tên này
    title: str         # dòng mô tả (comment "photo-sort · …" đầu file, nếu có)
    path: Path


def _names() -> list[str]:
    if _EMBEDDED:
        files = list(_EMBEDDED)
    else:
        files = [p.name for p in RULES_DIR.glob("*.toml")]
    return sorted(Path(f).stem for f in files if not f.startswith("_"))


def _title(path: Path, name: str) -> str:
    try:
        text = _EMBEDDED.get(path.name) or path.read_text(encoding="utf-8")
    except OSError:
        return name
    for line in text.splitlines()[:6]:
        if "·" in line and line.lstrip().startswith("#"):
            return line.strip("# ").split("·", 1)[-1].strip()
    return name


def list_rules() -> list[RuleInfo]:
    return [RuleInfo(n, _title(RULES_DIR / f"{n}.toml", n), RULES_DIR / f"{n}.toml") for n in _names()]


def resolve_rules(rules: str | Path) -> Path:
    """Tên profile (``"tu_dung"``) hoặc đường dẫn file .toml → đường dẫn. Sai → ``ValueError``."""
    p = Path(rules)
    if p.suffix == ".toml" and toml_exists(p):
        return p
    cand = RULES_DIR / f"{p.stem}.toml"
    if toml_exists(cand) and not p.stem.startswith("_"):
        return cand
    names = ", ".join(_names())
    raise ValueError(f"không có rule '{rules}' — chọn một trong: {names}")


def tower_type_of(path: Path) -> str:
    return str(load_toml(path).get("tower_type", ""))
