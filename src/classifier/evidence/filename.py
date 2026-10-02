"""Bằng chứng từ TÊN FILE / thư mục đang chứa — dùng ``[[rule]]`` của profile.

Rule khớp ``match`` (+ ``from_folder`` nếu có) → phiếu cho mục lục. Rule nhập nhằng (tên
trùng giữa nhiều hạng mục, folder không xác nhận) → phiếu yếu chia đều. Tên vô nghĩa (Zalo)
→ không phiếu.
"""
from __future__ import annotations

import re

from classifier.catalog import Catalog
from classifier.evidence.base import Ballot, Vote

_NUM = re.compile(r"^\s*(\d+)\s*[.\-_ ]")


def _has(text: str, subs) -> bool:
    return any(s.casefold() in text for s in subs)


def _option_for(target: str, cat: Catalog, nm, prefix: str) -> tuple[str, str | None] | None:
    """Đích của rule (``"5.…/… {group}"``) → (option mục lục, giá trị biến)."""
    head, _, leaf = target.partition("/")
    m = _NUM.match(head)
    if not m:
        return None
    sec = next((s for s in cat.sections if s.no == int(m[1])), None)
    if sec is None:
        return None
    for slot in sec.slots:
        if slot.var is None and slot.template == leaf:
            return slot.option, None
        if slot.var and "{group}" in leaf:
            kind = slot.var[:-2] if slot.var.endswith("_k") else slot.var
            key = nm.group_key(prefix, kind)
            if key is None:
                continue
            if slot.var.endswith("_k"):
                key = str(nm.group_number(prefix, kind) or "")
            if slot.fill(key):
                return slot.option, key
    return None


def collect(photos, cat: Catalog, prof) -> Ballot:
    nm = prof.names()
    out: Ballot = {}
    for p in photos:
        if not p.prefix and not p.folder:
            continue
        folder = p.folder.casefold()
        sure, loose = [], []
        for rule in prof.rules:
            match, tgt = rule.get("match"), rule.get("target", "")
            if not match or tgt == "{keep}" or not _has(p.prefix, match):
                continue
            if _has(p.prefix, rule.get("exclude", [])) or _has(folder, rule.get("not_from_folder", [])):
                continue
            hit = _option_for(tgt, cat, nm, p.prefix)
            if hit is None:
                continue
            ff = rule.get("from_folder")
            (sure if ff and _has(folder, ff) or not ff else loose).append(hit)
        if sure:
            opt, val = sure[0]
            out[p.id] = [Vote(opt, 0.95, "filename", val, f"tên '{p.prefix}'")]
        elif loose:
            uniq = list(dict.fromkeys(loose))
            out[p.id] = [Vote(o, 0.6 / len(uniq), "filename", v, f"tên '{p.prefix}' (nhập nhằng)")
                         for o, v in uniq]
    return out
