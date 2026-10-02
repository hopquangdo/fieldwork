"""Liệt kê giá trị của biến trong mẫu thư mục.

* nhóm ``keywords`` (vd ``vitri``) → tên từng vị trí;
* nhóm đếm (``fmt``, vd ``mong`` → ``M{k}``; ``dot_k`` → ``{k}``) → 1…N, N = trường TABLEBia
  khai ở ``[catalog].counts`` (vd ``n_mong``), thiếu thì ``[catalog].default_counts``.
"""
from __future__ import annotations


def values_of(prof, var: str, meta) -> list[str]:
    kind, raw = (var[:-2], True) if var.endswith("_k") else (var, False)
    g = prof.groups.get(kind) or {}
    if "keywords" in g:
        return [kw["name"] for kw in g["keywords"]]
    cat = prof.raw.get("catalog") or {}
    field_name = (cat.get("counts") or {}).get(kind, "")
    n = int(getattr(meta, field_name, 0) or 0) if meta is not None and field_name else 0
    n = n or int((cat.get("default_counts") or {}).get(kind, 0))
    fmt = "{k}" if raw else g.get("fmt", "{k}")
    return [fmt.format(k=i) for i in range(1, n + 1)]
