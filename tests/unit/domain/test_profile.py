"""Profile: 0 fallback trong code — mọi field từ TOML (extends _base). Thiếu → ProfileError."""
from pathlib import Path

import pytest

from domain.profile import Profile, ProfileError

_RULES = Path(__file__).resolve().parents[3] / "rules"


def test_base_loads_and_covers_everything():
    p = Profile.load(_RULES / "_base.toml")
    assert p.structure.min_cong_tac == 2
    assert p.structure.prefer_images == 4
    assert p.structure.trim_to_prefer is False        # mặc định: giữ full ảnh
    assert p.folders.khac_name == "Hình ảnh khác"
    assert p.filename.ext == ".jpg"
    assert p.filename.primary_marker == "--1--"
    nm = p.names()
    assert nm.is_khac("Hình ảnh khác công tác X")
    assert not nm.is_cong_tac("Hình ảnh khác công tác X")
    assert nm.is_cong_tac("Công tác chuẩn bị đo Y")
    assert nm.group_key("móng m2 chi tiết", "mong") == "M2"
    assert nm.group_key("đốt d5", "dot") == "D5"
    assert nm.group_key("toạ độ vòng 0-1", "vitri") == "vòng 0-1"


def test_concrete_profiles_extend_base():
    dc = Profile.load(_RULES / "day_co.toml")
    td = Profile.load(_RULES / "tu_dung.toml")
    assert dc.rules and td.rules
    assert dc.structure.even_no_trim == ("9.",)          # từ _base
    assert td.structure.even_no_trim == ("7.",)          # override
    assert td.structure.keep_as_is == ("1.", "8.")
    assert dc.filename.build == td.filename.build        # dùng chung _base


def test_missing_section_raises():
    with pytest.raises(ProfileError):
        Profile.from_dict({"tower_type": "x"})           # thiếu [structure]…


def test_bad_list_type_raises():
    with pytest.raises(ProfileError):
        Profile.from_dict({
            "tower_type": "x",
            "structure": {}, "folders": {}, "filename": {}, "metadata": {}, "groups": {},
        })


def test_load_missing_file_raises(tmp_path):
    with pytest.raises(ProfileError):
        Profile.load(tmp_path / "khong-co.toml")
