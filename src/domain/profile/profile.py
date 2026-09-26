"""``Profile`` — gom 1 file ``rules/<tên>.toml`` (đã giải ``extends``) thành object
có kiểu. 0 fallback: thiếu section/field → :class:`ProfileError`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # py310
    import tomli as tomllib

from domain.profile.names import Names
from domain.profile.spec import (
    Filename,
    Folders,
    Metadata,
    ProfileError,
    Structure,
    need,
    strs,
)


@dataclass(frozen=True)
class Profile:
    name: str
    tower_type: str
    structure: Structure
    folders: Folders
    filename: Filename
    metadata: Metadata
    hang_muc: dict[int, str]
    hang_muc_alias: dict[str, str]
    rules: list[dict]
    naming: list[dict]
    dot_range: list[dict]
    vision: dict
    groups: dict[str, Any]
    subfolders: list[dict] = field(default_factory=list)     # [[subfolders]] — tên thư mục con chuẩn
    canonical: dict = field(default_factory=dict)            # [canonical] — ngưỡng/khớp tên chuẩn
    scan: dict = field(default_factory=dict)                 # [scan] — lọc ảnh trùng / bản lồng
    agent: dict = field(default_factory=dict)                # [agent] — rà soát ảnh bằng agent + look
    tower_evidence: list[dict] = field(default_factory=list) # [[tower_evidence]] — ảnh bác TABLEBia
    raw: dict[str, Any] = field(repr=False, default_factory=dict)

    def names(self) -> Names:
        return Names(self)

    # -- load -----------------------------------------------------------
    @classmethod
    def load(cls, path: str | Path) -> "Profile":
        from config.loader import load_toml   # giải `extends`

        p = Path(path)
        try:
            data = load_toml(p)
        except (OSError, tomllib.TOMLDecodeError, ValueError) as e:
            raise ProfileError(f"{p.name}: {e}") from e
        return cls.from_dict(data, source=p.stem)

    @classmethod
    def of(cls, ctx) -> "Profile":
        """Profile của lần chạy — build 1 lần từ ``ctx.config`` (đã giải extends), cache."""
        p = ctx.data.get("profile")
        if p is None:
            p = cls.from_dict(ctx.config.data, source=str(ctx.config.get("name") or ""))
            ctx.data["profile"] = p
        return p

    @classmethod
    def from_dict(cls, data: dict, *, source: str = "") -> "Profile":
        return cls(
            name=str(data.get("name") or source),
            tower_type=str(need(data, "tower_type", "profile")),
            structure=_structure(need(data, "structure", "profile")),
            folders=_folders(need(data, "folders", "profile")),
            filename=_filename(need(data, "filename", "profile")),
            metadata=_metadata(need(data, "metadata", "profile")),
            hang_muc={int(k): str(v) for k, v in (data.get("hang_muc") or {}).items()},
            hang_muc_alias={str(k): str(v) for k, v in (data.get("hang_muc_alias") or {}).items()},
            rules=list(data.get("rule") or []),
            naming=list(data.get("naming") or []),
            dot_range=list(data.get("dot_range") or []),
            vision=dict(data.get("vision") or {}),
            groups=_groups(need(data, "groups", "profile")),
            subfolders=list(data.get("subfolders") or []),
            canonical=dict(data.get("canonical") or {}),
            scan=dict(data.get("scan") or {}),
            agent=dict(data.get("agent") or {}),
            tower_evidence=list(data.get("tower_evidence") or []),
            raw=data,
        )


# ── section builders ─────────────────────────────────────────────────
def _structure(s: dict) -> Structure:
    return Structure(
        min_cong_tac=int(need(s, "min_cong_tac", "structure")),
        pair_folders=bool(need(s, "pair_folders", "structure")),
        require_khac=bool(need(s, "require_khac", "structure")),
        even_images=bool(need(s, "even_images", "structure")),
        prefer_images=int(need(s, "prefer_images", "structure")),
        trim_to_prefer=bool(s.get("trim_to_prefer", False)),   # mặc định: giữ FULL ảnh
        even_no_trim=strs(need(s, "even_no_trim", "structure"), "structure.even_no_trim"),
        keep_as_is=strs(need(s, "keep_as_is", "structure"), "structure.keep_as_is"),
        even_skip=strs(need(s, "even_skip", "structure"), "structure.even_skip"),
        keep_singletons=bool(s.get("keep_singletons", False)),
        odd_fix=str(s.get("odd_fix", "split")),
        trim_earliest=strs(s.get("trim_earliest", []), "structure.trim_earliest"),
        odd_folders_skip=strs(s.get("odd_folders_skip", []), "structure.odd_folders_skip"),
    )


def _folders(f: dict) -> Folders:
    return Folders(
        hm_prefix=str(need(f, "hm_prefix", "folders")),
        cong_tac_markers=strs(need(f, "cong_tac_markers", "folders"), "folders.cong_tac_markers"),
        khac_markers=strs(need(f, "khac_markers", "folders"), "folders.khac_markers"),
        appendix_markers=strs(need(f, "appendix_markers", "folders"), "folders.appendix_markers"),
        strip_prefixes=strs(need(f, "strip_prefixes", "folders"), "folders.strip_prefixes"),
        khac_name=str(need(f, "khac_name", "folders")),
        pair_names=_pair(strs(need(f, "pair_names", "folders"), "folders.pair_names")),
    )


def _pair(v: tuple[str, ...]) -> tuple[str, str]:
    if len(v) != 2:
        raise ProfileError("[folders.pair_names] cần đúng 2 phần tử")
    return (v[0], v[1])


def _filename(f: dict) -> Filename:
    return Filename(
        conform=str(need(f, "conform", "filename")),
        build=str(need(f, "build", "filename")),
        ts_pattern=str(need(f, "ts_pattern", "filename")),
        ts_fallback=str(need(f, "ts_fallback", "filename")),
        primary_marker=str(need(f, "primary_marker", "filename")),
        primary_yes=str(need(f, "primary_yes", "filename")),
        primary_no=str(need(f, "primary_no", "filename")),
        ext=str(need(f, "ext", "filename")),
    )


def _metadata(m: dict) -> Metadata:
    tt = need(m, "tower_type", "metadata")
    fld = need(m, "fields", "metadata")
    return Metadata(
        table_glob=str(need(m, "table_glob", "metadata")),
        tower_type={k: tuple(str(x) for x in v) for k, v in tt.items()},
        default_tower_type=str(need(m, "default_tower_type", "metadata")),
        fields={k: str(v) for k, v in fld.items()},
    )


def _groups(g: dict) -> dict[str, Any]:
    if not isinstance(g, dict) or not g:
        raise ProfileError("[groups] rỗng")
    return dict(g)
