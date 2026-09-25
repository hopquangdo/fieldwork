"""Tên thư mục con CHUẨN của từng hạng mục — khai báo ở ``[[subfolders]]`` của profile.

Đầu vào thường giữ tên thư mục thô ("01.Hình ảnh siêu âm thanh cánh 1 Đốt D1", thư
mục mẫu do scaffold dựng…); phụ lục cần đúng tên SOP. Mỗi khai báo gồm:

* ``hm``        — chuỗi nhận diện hạng mục (khớp trong tên thư mục hạng mục, casefold);
* ``khac``      — tên "Hình ảnh khác …" chuẩn của hạng mục;
* ``templates`` — mẫu tên thư mục con, có biến ``{<nhóm>}`` (khoá nhóm, vd ``{dot}`` →
  ``D1``, ``{mong}`` → ``M2``, ``{vitri}`` → ``chân cột``) hoặc ``{<nhóm>_k}`` (chỉ số, vd
  ``{dot_k}`` → ``1``). Biến lấy từ CHÍNH tên thư mục đang xét (qua ``[groups]``);
* ``ensure``    — thư mục luôn phải có (kể cả rỗng), cũng là mẫu hợp lệ;
* ``pairing``   — dựng thư mục CẶP rỗng (theo ``[folders] pair_names``, chỉ khi tên cặp là
  tên chuẩn): ``"singletons"`` (mặc định — chỉ thư mục 1 ảnh, SOP TH3) · ``"all"`` (mọi thư
  mục, vd bê tông: mỗi móng "chuẩn bị" + "kiểm tra") · ``"none"`` (vd khe hở: mỗi đốt 1 thư mục);
* ``unmatched`` — thư mục không khớp mẫu nào: ``"keep"`` (giữ, báo người xem) hoặc
  ``"khac"`` (dồn ảnh vào 'khác', báo người xem). Mặc định lấy ``[canonical].unmatched``.

Khớp = độ trùng token (Jaccard) giữa tên thư mục (đã bỏ số thứ tự đầu) và mẫu đã điền
biến; ≥ ``[canonical].min_score`` mới nhận. Không bao giờ tự chế tên ngoài danh sách.
Module thuần: chỉ chuỗi / dict, không I/O, không ``ctx``.
"""
from __future__ import annotations

import re

from domain.folders import hm_of, leaf_of

_VAR = re.compile(r"\{(\w+)\}")
_TOKEN = re.compile(r"\w+", re.UNICODE)


def _tokens(s: str) -> set[str]:
    return set(_TOKEN.findall(s.casefold()))


def natural_key(s: str) -> list:
    """Khoá sắp xếp tự nhiên ('đốt 2' < 'đốt 10')."""
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s.casefold())]


class CanonicalNamer:
    """Bọc ``prof.subfolders`` + ``Names`` — đổi tên thư mục con về tên chuẩn."""

    def __init__(self, prof) -> None:
        self._nm = prof.names()
        self._specs = prof.subfolders
        cfg = prof.canonical
        self._min = float(cfg.get("min_score", 0.6))
        self._unmatched = str(cfg.get("unmatched", "keep"))
        self._num = re.compile(prof.folders.hm_prefix)

    # -- tra cứu ----------------------------------------------------------
    def spec_for(self, hm: str) -> dict | None:
        low = hm.casefold()
        for spec in self._specs:
            keys = spec.get("hm") or []
            if isinstance(keys, str):
                keys = [keys]
            if any(k.casefold() in low for k in keys):
                return spec
        return None

    def khac_name(self, hm: str) -> str | None:
        spec = self.spec_for(hm)
        return spec.get("khac") if spec else None

    def ensured(self, hm: str) -> list[str]:
        spec = self.spec_for(hm) or {}
        out = list(spec.get("ensure") or [])
        if spec.get("khac"):
            out.append(spec["khac"])
        return out

    def pairing(self, hm: str) -> str:
        """Chế độ dựng thư mục cặp của hạng mục: ``singletons`` / ``all`` / ``none``."""
        spec = self.spec_for(hm) or {}
        return str(spec.get("pairing", "singletons"))

    def _pair_up(self, assign: dict, hm: str) -> int:
        """Dựng thư mục cặp RỖNG theo ``pairing`` — chỉ khi tên cặp là tên chuẩn."""
        mode = self.pairing(hm)
        if mode == "none":
            return 0
        n = 0
        for key in [k for k in list(assign) if hm_of(k) == hm and k.count("/") == 1]:
            photos = assign.get(key) or []
            if not photos or (mode == "singletons" and len(photos) != 1):
                continue
            sib = self._nm.sibling_leaf(leaf_of(key))
            if sib and f"{hm}/{sib}" not in assign and self.allowed(hm, sib):
                assign[f"{hm}/{sib}"] = []
                n += 1
        return n

    def unmatched_policy(self, hm: str) -> str:
        spec = self.spec_for(hm) or {}
        return str(spec.get("unmatched", self._unmatched))

    # -- khớp ---------------------------------------------------------------
    def _render(self, template: str, leaf_cf: str) -> str | None:
        """Điền biến của ``template`` từ tên thư mục; thiếu biến nào → ``None``."""
        out = template
        for var in set(_VAR.findall(template)):
            kind, raw = (var[:-2], True) if var.endswith("_k") else (var, False)
            if raw:
                val = self._nm.group_number(leaf_cf, kind)
                val = None if val is None else str(val)
            else:
                val = self._nm.group_key(leaf_cf, kind)
            if val is None:
                return None
            out = out.replace("{" + var + "}", val)
        return out

    def resolve(self, hm: str, leaf: str) -> tuple[str | None, float]:
        """→ ``(tên chuẩn, điểm)``; ``(None, điểm tốt nhất)`` nếu không đủ tin cậy.
        Hạng mục không khai báo ``[[subfolders]]`` → ``(leaf, 1.0)`` (giữ nguyên)."""
        spec = self.spec_for(hm)
        if spec is None:
            return leaf, 1.0
        if self._nm.is_khac(leaf) and spec.get("khac"):
            return spec["khac"], 1.0
        bare = self._num.sub("", leaf).strip()
        bare_cf = bare.casefold()
        want = _tokens(bare)
        best, best_score = None, 0.0
        for t in [*(spec.get("templates") or []), *(spec.get("ensure") or [])]:
            name = self._render(t, bare_cf)
            if name is None:
                continue
            if name == leaf:
                return name, 1.0
            have = _tokens(name)
            score = len(want & have) / len(want | have) if want | have else 0.0
            if score > best_score:
                best, best_score = name, score
        return (best, best_score) if best_score >= self._min else (None, best_score)

    def allowed(self, hm: str, leaf: str) -> bool:
        """``leaf`` đã là tên chuẩn của hạng mục (hoặc hạng mục không khai báo)?"""
        name, _ = self.resolve(hm, leaf)
        return name == leaf

    # -- áp lên assign ----------------------------------------------------
    def apply(self, assign: dict[str, list[str]], *, kept=lambda hm: False) -> dict[str, list]:
        """Đổi tên (gộp nếu trùng) mọi thư mục con về tên chuẩn, dựng thư mục ``ensure``.
        Hạng mục ``kept`` (keep_as_is) chỉ chuẩn hoá 'khác' + ``ensure``.
        → ``{"renamed": [...], "review": [...]}`` để báo cáo."""
        renamed: list[str] = []
        review: list[str] = []
        for key in [k for k in list(assign) if "/" in k and k[:1].isdigit()]:
            hm, leaf = hm_of(key), leaf_of(key)
            if key.count("/") != 1 or self.spec_for(hm) is None:
                continue
            if kept(hm) and not self._nm.is_khac(leaf):
                continue
            name, score = self.resolve(hm, leaf)
            if name == leaf:
                continue
            photos = assign.pop(key)
            if name is not None:
                assign.setdefault(f"{hm}/{name}", []).extend(photos)
                renamed.append(f"{key}  →  {name}  ({score:.2f})")
                continue
            if not photos:
                continue                                  # thư mục mẫu sai tên, rỗng → bỏ
            if self.unmatched_policy(hm) == "khac" and self.khac_name(hm):
                assign.setdefault(f"{hm}/{self.khac_name(hm)}", []).extend(photos)
                review.append(f"{key}: không khớp tên chuẩn — {len(photos)} ảnh → 'khác'")
            else:
                assign[key] = photos
                review.append(f"{key}: không khớp tên chuẩn — giữ nguyên ({len(photos)} ảnh)")
        for hm in sorted({hm_of(k) for k in assign if k[:1].isdigit()}):
            if self.spec_for(hm) is None or kept(hm):
                continue
            for leaf in self.ensured(hm):
                assign.setdefault(f"{hm}/{leaf}", [])
            self._pair_up(assign, hm)
        for hm in sorted({hm_of(k) for k in assign if k[:1].isdigit()}):
            if kept(hm):
                for leaf in self.ensured(hm):
                    assign.setdefault(f"{hm}/{leaf}", [])
        return {"renamed": renamed, "review": review}
