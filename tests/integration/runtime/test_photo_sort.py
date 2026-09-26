from pathlib import Path

from config.loader import Config
from infrastructure.observability.report import Report
from runtime import RunContext, run

from domain.profile import Profile
from domain.naming import parse
from pipeline.feature import PhotoSortFeature
from domain.state import state

FEATURE = PhotoSortFeature()
_PROF = Profile.load(Path(__file__).resolve().parents[3] / "rules" / "_base.toml")
_FN = _PROF.filename


def _parse(name: str):
    return parse(name, ts_pattern=_FN.ts_pattern, primary_marker=_FN.primary_marker)


def _run(inp: Path, out: Path, rules: Path) -> Report:
    cfg = Config.load(rules)
    ctx = RunContext(inp, out, cfg, Report(feature="photo-sort", target=inp.name))
    return run(FEATURE, ctx)


def test_naming():
    c = _parse("Móng M2@ 10@05@22@--1--.jpg")
    assert c.prefix == "móng m2" and c.is_primary
    assert _PROF.names().group_key(c.prefix, "mong") == "M2"
    assert _parse("@8@05@00@--0--.jpg").prefix == ""


def test_registered_as_feature():
    from runtime import load_features
    assert "photo-sort" in load_features()


def test_runs_full_chain(station, tmp_path, rules_file):
    rep = _run(station, tmp_path / "out", rules_file)
    assert not rep.aborted
    names = [s.name for s in rep.stages]
    assert names[:4] == ["scan", "normalize", "check", "classify"]  # reconcile chain always starts here
    assert names[-2:] == ["apply", "delete_empty"]
    assert {"scaffold", "even_four", "validate", "plan", "verify"} <= set(names)
    assert rep.sections["images_before"] == rep.sections["images_after"] == 13


def test_apply_moves_by_rules(station, tmp_path, rules_file):
    out = tmp_path / "out"
    rep = _run(station, out, rules_file)
    assert not rep.aborted, rep.errors
    work = out / station.name

    assert (work / "3" / "chuan bi M1").is_dir()
    assert len(list((work / "3" / "chuan bi M2").glob("*.jpg"))) == 3
    assert len(list((work / "1" / "bien nha tram").glob("*.jpg"))) == 1
    assert len(list(work.rglob("*.jpg"))) == 13           # conservation


def test_input_untouched(station, tmp_path, rules_file):
    before = len(list(station.rglob("*.jpg")))
    _run(station, tmp_path / "out", rules_file)
    assert len(list(station.rglob("*.jpg"))) == before


def test_conservation_catches_name_clash(station, tmp_path, rules_file):
    from domain.models import Photo
    from steps.conservation import conservation

    ctx = RunContext(station, tmp_path / "o", Config.load(rules_file),
                     Report(feature="x"))
    state(ctx).photos = [Photo("a/x.jpg", "", False), Photo("b/x.jpg", "", False)]
    state(ctx).assign = {"z": ["a/x.jpg", "b/x.jpg"]}   # both land as z/x.jpg
    state(ctx).moves = []
    state(ctx).landing = [("z", "x.jpg"), ("z", "x.jpg")]
    conservation.__wrapped__(ctx)
    assert ctx.report.aborted and "trùng" in ctx.report.errors[0]


def test_input_may_be_image_dir_with_sibling_data(station, tmp_path, rules_file):
    """Trỏ thẳng vào thư mục ảnh: TABLEBia nằm ở thư mục Data ANH EM vẫn phải được đọc."""
    img = station / station.name
    rep = _run(img, tmp_path / "out", rules_file)
    assert not rep.aborted, rep.errors
    assert rep.sections["meta"]["source"] == "TABLEBia.txt"


def test_output_has_images_only(station, tmp_path, rules_file):
    """Output chỉ chứa thư mục ảnh — không mang Data hay tầng bọc trùng tên."""
    out = tmp_path / "out"
    _run(station, out, rules_file)
    assert [p.name for p in out.iterdir()] == [station.name]
    assert not any(p.suffix == ".txt" for p in out.rglob("*"))
    assert not (out / station.name / station.name).exists()


def test_aborts_when_tower_type_unknown(station, tmp_path, rules_file):
    """Không có TABLEBia → dừng rõ ràng, KHÔNG âm thầm mặc định dây co."""
    (station / "DataNAN00145 ok" / "TABLEBia.txt").unlink()
    rep = _run(station, tmp_path / "out", rules_file)
    assert rep.aborted
    assert any("loại cột" in e for e in rep.errors)


def _img(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def test_evaluation_compare_matches_by_content(tmp_path):
    """So theo nội dung: đổi tên không sao; sai thư mục / thiếu / thừa / thư mục rỗng đều đếm."""
    from evaluation.evaluator import compare, read_layout

    gt, out = tmp_path / "gt" / "S", tmp_path / "out" / "S"
    for root, rows in (
        (gt, {"1.A/x": b"a", "1.A/y": b"b", "2.B/z": b"c", "2.B/w": b"d"}),
        (out, {"1.A/renamed": b"a", "2.B/y": b"b", "2.B/z": b"c", "2.B/extra": b"e"}),
    ):
        for rel, data in rows.items():
            _img(root / (rel + ".jpg"), data)
    (gt / "2.B" / "empty").mkdir()

    res = compare(read_layout(out), read_layout(gt))
    assert (res.total, res.correct) == (4, 2)          # a (đổi tên) + c đúng
    assert res.wrong == [("y.jpg", "1.A", "2.B")]
    assert [m[0] for m in res.missing] == ["w.jpg"]
    assert [e[0] for e in res.extra] == ["extra.jpg"]
    assert res.dirs_missing == ["2.B/empty"] and res.dirs_extra == []
    assert res.per_group == {"1.A": (1, 2), "2.B": (1, 2)}
    assert res.accuracy == 0.5


def test_evaluation_discover_pairs(tmp_path):
    from evaluation.evaluator import discover_pairs

    (tmp_path / "data" / "ST1").mkdir(parents=True)
    (tmp_path / "gt" / "ST1_gt").mkdir(parents=True)
    (tmp_path / "gt" / "NOPE_gt").mkdir()                 # không có input tương ứng → bỏ
    assert [p[0] for p in discover_pairs(tmp_path / "data", tmp_path / "gt")] == ["ST1"]


def test_free_dir_adds_suffix_when_output_has_data(tmp_path):
    from application.services.run_graph import free_dir

    out = tmp_path / "ket qua"
    assert free_dir(out) == out                       # chưa có
    out.mkdir()
    assert free_dir(out) == out                       # rỗng → dùng luôn
    (out / "a.jpg").write_bytes(b"x")
    assert free_dir(out) == tmp_path / "ket qua (2)"
    (tmp_path / "ket qua (2)").mkdir()
    (tmp_path / "ket qua (2)" / "b.jpg").write_bytes(b"x")
    assert free_dir(out) == tmp_path / "ket qua (3)"
