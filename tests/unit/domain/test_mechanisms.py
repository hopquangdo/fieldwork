"""Test các cơ chế tổng quát: lọc đầu vào (bản lồng / trùng nội dung), nhóm theo số
thứ tự (ordinal), tên thư mục chuẩn (``[[subfolders]]``), ảnh bác TABLEBia, thứ tự ép chẵn.
Dữ liệu SOP lấy từ ``rules/tu_dung.toml`` — test không tự đặt chuỗi SOP vào code."""
from __future__ import annotations

from pathlib import Path

import pytest

from domain.profile import Profile
from domain.canonical import CanonicalNamer
from domain.diagnostics import structural_issues
from domain.intake import survey
from domain.metadata import refine_tower_type
from steps.even_four import _trim

from conftest import _w

_RULES = Path(__file__).resolve().parents[3] / "rules"
TU = Profile.load(_RULES / "tu_dung.toml")
BASE = Profile.load(_RULES / "_base.toml")

HM2 = "2.Công tác kiểm tra khe hở cấu kiện lắp ghép"
HM3 = "3.Công tác kiểm tra cường độ bê tông móng"
HM7 = "7.Công tác đo kích thước cấu kiện cột anten"


# ── D. lọc đầu vào ───────────────────────────────────────────────────────
def test_intake_skips_nested_copy_and_duplicates(tmp_path: Path):
    root = tmp_path / "ST"
    _w(root, "1.A/x", ["a@1@1@1@--0--.jpg"])
    _w(root, "2.B/y", ["b@1@1@2@--0--.jpg"])
    # bản sao lồng: ≥2 thư mục đánh số trùng tên với gốc
    (root / "ST" / "1.A").mkdir(parents=True)
    (root / "ST" / "2.B").mkdir(parents=True)
    (root / "Data").mkdir()                                  # không ảnh, không đánh số
    # trùng nội dung trong CÙNG hạng mục → bỏ; khác hạng mục → giữ
    src = root / "2.B/y/b@1@1@2@--0--.jpg"
    (root / "2.B/z").mkdir()
    (root / "2.B/z/b copy.jpg").write_bytes(src.read_bytes())
    (root / "1.A/x/b cross.jpg").write_bytes(src.read_bytes())

    it = survey(root, BASE.scan)
    assert "ST" in it.skip_dirs and "Data" in it.skip_dirs
    dropped = [d for d, _ in it.duplicates]
    assert dropped == ["2.B/z/b copy.jpg"]


def test_intake_does_not_flag_numbered_subfolders(tmp_path: Path):
    """'9.X/01.Siêu âm…' có con đánh số nhưng KHÔNG trùng tên hạng mục gốc → không phải bản lồng."""
    root = tmp_path / "ST"
    _w(root, "1.A", ["a@1@1@1@--0--.jpg"])
    _w(root, "9.X/01.Sieu am 1", ["s@1@1@1@--0--.jpg"])
    _w(root, "9.X/02.Sieu am 2", ["t@1@1@1@--0--.jpg"])
    assert survey(root, BASE.scan).skip_dirs == []


# ── C. nhóm theo số thứ tự ───────────────────────────────────────────────
@pytest.mark.parametrize("n, expect", [
    (7, ["chân cột"] * 2 + ["giữa cột"] * 3 + ["đỉnh cột"] * 2),
    (8, ["chân cột"] * 3 + ["giữa cột"] * 2 + ["đỉnh cột"] * 3),
    (3, ["chân cột", "giữa cột", "đỉnh cột"]),
])
def test_ordinal_bucket(n, expect):
    nm = TU.names()
    got = [nm.group_key(f"đốt d{k}", "vitri_dot", {"n_dot": n}) for k in range(1, n + 1)]
    assert got == expect


def test_ordinal_totals_prefer_observed():
    class Meta:
        n_dot = 6
    nm = TU.names()
    assert nm.ordinal_totals(["đốt d1", "đốt d8", "móng m1"], Meta())["n_dot"] == 8
    assert nm.ordinal_totals(["móng m1"], Meta())["n_dot"] == 6
    # group_by list: vị trí ghi trong tên thắng vị trí suy ra
    assert nm.group_key("đốt d7 chân cột", ["vitri", "vitri_dot"], {"n_dot": 7}) == "chân cột"


# ── A. tên thư mục chuẩn ─────────────────────────────────────────────────
def test_canonical_merges_and_renames():
    cn = CanonicalNamer(TU)
    assign = {
        f"{HM7}/01.Hình ảnh siêu âm thanh cánh 1 Đốt D1": ["a"],
        f"{HM7}/01.Hình ảnh siêu âm thanh cánh 2 Đốt D1": ["b"],
        f"{HM7}/Hình ảnh khác kích thước cấu kiện cột anten": ["c"],
        f"{HM7}/Đo kích thước dây tiếp địa": ["d"],                # không có tên chuẩn
        f"{HM7}/Công tác đo Đo kích thước cấu kiện cột anten": [],  # mẫu sai tên, rỗng
    }
    out = cn.apply(assign, kept=TU.names().is_kept)
    assert assign[f"{HM7}/Hình ảnh siêu âm thanh cánh Đốt D1"] == ["a", "b"]
    assert assign[f"{HM7}/Hình ảnh khác đo kích thước cấu kiện cột anten"] == ["c", "d"]
    assert f"{HM7}/Hình ảnh chuẩn bị đo kích thước cấu kiện cột anten" in assign   # ensure
    assert not any("dây tiếp địa" in k or "Công tác đo Đo" in k for k in assign)
    assert len(out["review"]) == 1


def test_canonical_pairing_modes():
    cn = CanonicalNamer(TU)
    assign = {
        f"{HM3}/Công tác chuẩn bị kiểm tra cường độ bê tông móng Móng M1": ["a", "b"],
        f"{HM2}/Công tác chuẩn bị kiểm tra khe hở cấu kiện lắp ghép đốt 7": ["c"],
    }
    cn.apply(assign)
    assert assign[f"{HM3}/Công tác kiểm tra cường độ bê tông móng Móng M1"] == []   # pairing = all
    assert f"{HM2}/Công tác kiểm tra khe hở cấu kiện lắp ghép đốt 7" not in assign   # pairing = none
    assert cn.allowed(HM2, "Công tác kiểm tra khe hở cấu kiện lắp ghép đốt 7")
    assert not cn.allowed(HM2, "Công tác đo kiểm tra khe hở cấu kiện lắp ghép đốt 7")


# ── ảnh bác khai báo TABLEBia ───────────────────────────────────────────
def test_tower_evidence_overrides_declared(tmp_path: Path):
    root = tmp_path / "ST"
    _w(root, "1.Hình ảnh tổng thể", ["a@1@1@1@--0--.jpg"])
    (root / "3.Công tác đo lực căng trong dây co" / "x").mkdir(parents=True)
    (root / "4.Công tác kiểm tra lực siết khóa cáp").mkdir()
    tt, why = refine_tower_type(root, "day_co", BASE.tower_evidence)
    assert tt == "tu_dung" and why
    _w(root, "3.Công tác đo lực căng trong dây co/x", ["Móng M1@1@1@1@--0--.jpg"])
    assert refine_tower_type(root, "day_co", BASE.tower_evidence)[0] == "day_co"


# ── ép chẵn: thứ tự giữ / bỏ ──────────────────────────────────────────
def test_trim_keeps_primary_group_and_drops_latest():
    info = {
        "tc d1": ("thanh cánh đốt d1", False, (9, 19, 41)),
        "tc d7a": ("thanh cánh đốt d7", False, (10, 33, 18)),
        "tc d7b": ("thanh cánh đốt d7", True, (10, 33, 50)),
    }
    keep, drop = _trim(list(info), 10_000, info=info)
    assert drop == ["tc d1"]                       # lạc nhóm với ảnh chính → bỏ trước
    info = {f"p{i}": ("đốt d3", False, (10, 30, i)) for i in range(3)}
    assert _trim(list(info), 10_000, info=info)[1] == ["p2"]                 # bỏ ảnh muộn nhất
    assert _trim(list(info), 10_000, info=info, earliest=True)[1] == ["p0"]  # trim_earliest


def test_odd_folders_skip_and_singletons():
    assign = {
        f"{HM7}/Đo kích thước thanh cánh": ["a", "b"],
        f"{HM7}/Đo kích thước thân cột": ["c", "d"],
        f"{HM7}/Đo kích thước thanh giằng": ["e"],             # 1 ảnh: keep_singletons
        f"{HM7}/Hình ảnh khác đo kích thước cấu kiện cột anten": [],
    }
    kinds = {i.kind for i in structural_issues(assign, TU)}
    assert "odd_folders" not in kinds and "odd_images" not in kinds
