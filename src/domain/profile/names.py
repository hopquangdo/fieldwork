"""``Names`` — mọi phép suy luận SOP-aware bound vào một :class:`Profile`.

Nhận diện loại thư mục (``is_cong_tac`` / ``is_khac`` / ``is_appendix`` …), bóc tên
cấu kiện (``hm_base`` / ``core_of``), đọc "nhóm" từ prefix tên file (``group_key``,
``looks_like_blueprint``), và dựng tên thư mục cặp (``pair``). Toàn bộ marker / regex
lấy từ profile — module này chỉ áp dụng chúng.
"""
from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.profile.profile import Profile


class Names:
    def __init__(self, prof: "Profile") -> None:
        self._f = prof.folders
        self._s = prof.structure
        self._g = prof.groups
        self.filename = prof.filename
        self._hm_prefix = re.compile(prof.folders.hm_prefix)

    # -- loại thư mục -----------------------------------------------------
    def is_khac(self, leaf: str) -> bool:
        lo = leaf.casefold()
        return any(lo.startswith(m) for m in self._f.khac_markers)      # neo đầu

    def is_cong_tac(self, leaf: str) -> bool:
        if self.is_khac(leaf):                                          # khác chứa 'công tác'
            return False
        lo = leaf.casefold()
        return any(m in lo for m in self._f.cong_tac_markers)

    def is_appendix(self, leaf: str) -> bool:
        if self.is_khac(leaf):
            return False
        lo = leaf.casefold()
        return any(m in lo for m in self._f.appendix_markers)

    def is_kept(self, hm: str) -> bool:
        return any(hm.startswith(k) for k in self._s.keep_as_is)

    def odd_ok(self, hm: str) -> bool:
        """Hạng mục được phép có số thư mục phụ lục LẺ (``[structure] odd_folders_skip``)."""
        low = hm.casefold()
        return any(k.casefold() in low for k in self._s.odd_folders_skip)

    def in_no_trim(self, folder: str) -> bool:
        return any(folder.startswith(k) for k in self._s.even_no_trim)

    def is_ultrasound(self, leaf: str) -> bool:
        lo = leaf.casefold()
        return any(m in lo for m in self._s.even_skip)

    # -- bóc tên cấu kiện ----------------------------------------------
    def hm_base(self, hm_folder: str) -> str:
        name = self._hm_prefix.sub("", hm_folder)
        for pre in self._f.strip_prefixes:
            if name.startswith(pre):
                return name[len(pre):].strip(" (") or name
        return name

    def core_of(self, cong_tac_leaf: str) -> str:
        for pre in self._f.strip_prefixes:
            if cong_tac_leaf.startswith(pre):
                return cong_tac_leaf[len(pre):]
        return cong_tac_leaf

    def pair(self, core: str) -> tuple[str, str]:
        """2 tên thư mục 1 cặp cho 'core' (vd 'Công tác chuẩn bị X', 'Công tác đo X')."""
        a, b = self._f.pair_names
        return (a + core, b + core)

    def pair_core(self, leaf: str) -> str:
        """Phần chung của 2 thư mục 1 cặp: bóc tiền tố ``pair_names`` DÀI nhất khớp
        ("Công tác chuẩn bị X" → "X"). Không khớp → ``core_of`` (strip_prefixes)."""
        for pre in sorted(self._f.pair_names, key=len, reverse=True):
            if leaf.startswith(pre):
                return leaf[len(pre):]
        return self.core_of(leaf)

    def sibling_leaf(self, leaf: str) -> str | None:
        """Tên thư mục cặp của ``leaf`` (chuẩn bị ↔ đo); ``None`` nếu ``leaf`` không đặt
        theo ``pair_names``."""
        core = self.pair_core(leaf)
        la, lb = self.pair(core)
        if leaf == la:
            return lb
        if leaf == lb:
            return la
        return None

    def is_paired_singleton(self, assign: dict, hm: str, folder: str) -> bool:
        """SOP: cấu kiện CHỈ 1 ẢNH → cặp chuẩn bị/đo, ảnh ở 1 cái, cái kia rỗng.
        True nếu ``folder`` có đúng 1 ảnh VÀ thư mục cặp của nó (chuẩn bị<->đo, cùng
        'core') đang rỗng — tức đây là cặp hợp lệ, không phải ảnh lẻ thật sự.
        ``[structure] keep_singletons = true`` → mọi thư mục 1 ảnh đều hợp lệ."""
        if len(assign.get(folder, [])) != 1:
            return False
        if self._s.keep_singletons:
            return True
        sib = self.sibling_leaf(folder.rsplit("/", 1)[-1])
        if sib is None:
            return False
        sibling = f"{hm}/{sib}"
        return len(assign.get(sibling, [])) == 0 if sibling in assign else False

    def prep_folder(self, core: str) -> str:
        return self._f.pair_names[0] + core

    # -- nhóm / bản vẽ từ prefix tên file -----------------------------
    def group_number(self, text: str, kind: str) -> int | None:
        """Số thứ tự của nhóm dạng pattern (vd 'đốt d7' → 7); ``None`` nếu không khớp."""
        g = self._g.get(kind) or {}
        pat = g.get("pattern")
        m = re.search(pat, text, re.I) if pat else None
        if not m:
            return None
        val = m[1].lstrip(g["strip"]) if g.get("strip") else m[1]
        return int(val) if val.isdigit() else None

    def group_key(self, prefix: str, kind, totals: dict[str, int] | None = None) -> str | None:
        """Khoá nhóm của ``prefix`` theo ``[groups.<kind>]``. ``kind`` có thể là list →
        thử lần lượt, lấy khoá đầu tiên. Ba dạng nhóm:

        * ``pattern`` + ``fmt`` — số trong tên (``Móng M2`` → ``M2``);
        * ``keywords`` / ``ring_pattern`` — vị trí ghi trong tên;
        * ``ordinal`` + ``total`` + ``buckets`` — vị trí SUY RA từ số thứ tự: lấy số của
          nhóm ``ordinal`` (vd đốt k), tổng ``totals[total]`` (vd n_dot), tính
          ``(k − 0.5) / tổng`` rồi chọn bucket đầu tiên có ``upto`` ≥ giá trị đó.
        """
        if isinstance(kind, (list, tuple)):
            for k in kind:
                key = self.group_key(prefix, k, totals)
                if key is not None:
                    return key
            return None
        g = self._g.get(kind)
        if not g:
            return None
        if "ordinal" in g:
            return self._ordinal_bucket(prefix, g, totals or {})
        if "keywords" in g or "ring_pattern" in g:
            rp = g.get("ring_pattern")
            if rp:
                mv = re.search(rp, prefix)
                if mv:
                    return "vòng " + re.sub(r"\s+", "", mv[1]).replace("–", "-")
            for kw in g.get("keywords", []):
                if any(k in prefix for k in kw["any"]):
                    return kw["name"]
            return None
        m = re.search(g["pattern"], prefix, re.I)
        if not m:
            return None
        val = m[1]
        if g.get("strip"):
            val = val.lstrip(g["strip"])
        return g["fmt"].format(k=val)

    def _ordinal_bucket(self, prefix: str, g: dict, totals: dict[str, int]) -> str | None:
        k = self.group_number(prefix, g["ordinal"])
        total = totals.get(g.get("total", ""), 0)
        if k is None or total <= 0 or k > total:
            return None
        pos = (k - 0.5) / total
        buckets = g.get("buckets") or []
        for b in buckets:
            if pos <= float(b["upto"]):
                return str(b["name"])
        return str(buckets[-1]["name"]) if buckets else None

    def ordinal_totals(self, prefixes, meta=None) -> dict[str, int]:
        """Tổng cho các nhóm ``ordinal`` — ``{tên total: số}``. Ưu tiên SỐ THỰC TẾ trong
        tên ảnh (max số thứ tự thấy được, SOP: "ưu tiên ảnh thực tế"); không thấy thì
        lấy trường cùng tên của ``meta`` (TABLEBia, vd ``n_dot``)."""
        out: dict[str, int] = {}
        prefixes = list(prefixes)
        for g in self._g.values():
            if not isinstance(g, dict) or "ordinal" not in g:
                continue
            name = g.get("total", "")
            seen = [n for p in prefixes if (n := self.group_number(p, g["ordinal"])) is not None]
            observed = max(seen, default=0)
            declared = int(getattr(meta, name, 0) or 0) if meta is not None else 0
            out[name] = observed or declared
        return out

    def looks_like_blueprint(self, prefix: str) -> bool:
        pat = (self._g.get("blueprint") or {}).get("pattern")
        return bool(pat and re.search(pat, prefix, re.I))

    def _trail_groups(self) -> list[tuple[re.Pattern, str]]:
        """``[groups.*]`` có ``trail = true``: (regex khớp đuôi theo ``fmt``, ``trail_label``)."""
        out = []
        for g in self._g.values():
            fmt = g.get("fmt", "") if isinstance(g, dict) and g.get("trail") else ""
            if "{k}" in fmt:
                a, _, b = fmt.partition("{k}")
                out.append((re.compile(re.escape(a) + r"(\d+)" + re.escape(b)), g.get("trail_label", fmt)))
        return out

    def trail_regex(self) -> re.Pattern | None:
        """Regex giữ đuôi nhóm (vd 'M2' / 'D3' / 'Tầng dây 1') khi bóc tên — nhóm nào giữ
        đuôi do rules quyết (``trail = true``)."""
        pats = [p.pattern for p, _ in self._trail_groups()]
        return re.compile(r"\s+((?:" + "|".join(pats) + r"))$") if pats else None

    def trail_label(self, trail: str) -> str:
        """Cách ghi đuôi trong tên file, theo ``trail_label`` của nhóm (vd 'M2' → 'Móng M2')."""
        for pat, label in self._trail_groups():
            if m := pat.fullmatch(trail):
                return label.format(k=m[1])
        return trail

    # -- thư mục 'khác' của 1 hạng mục -------------------------------
    def khac_in_assign(self, assign: dict, hm: str) -> str | None:
        return next((k for k in assign
                     if k.split("/", 1)[0] == hm and self.is_khac(k.rsplit("/", 1)[-1])), None)

    def khac_folder(self, assign: dict, hm: str, *,
                    existing: set[str] | None = None, base: str = "") -> str:
        hit = self.khac_in_assign(assign, hm)
        if hit:
            return hit
        for d in sorted(existing or ()):
            if d.split("/", 1)[0] == hm and d.count("/") == 1 and self.is_khac(d.rsplit("/", 1)[-1]):
                return d
        return f"{hm}/{self._f.khac_name}{f' {base}'.rstrip()}"
