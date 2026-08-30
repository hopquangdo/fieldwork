from pathlib import Path

from graphrun import Config, Report, RunContext, run

from photo_sort.domain.naming import group_key, parse
from photo_sort.feature import PhotoSortFeature

FEATURE = PhotoSortFeature()


def _run(inp: Path, out: Path, rules: Path, *, apply: bool) -> Report:
    cfg = Config.load(rules)
    ctx = RunContext(inp, out, cfg,
                     Report(feature="photo-sort", target=inp.name, dry_run=not apply),
                     dry_run=not apply)
    return run(FEATURE, ctx)


def test_naming():
    c = parse("Móng M2@ 10@05@22@--1--.jpg")
    assert c.prefix == "móng m2" and c.is_primary
    assert group_key(c.prefix, "mong") == "M2"
    assert parse("@8@05@00@--0--.jpg").prefix == ""


def test_registered_as_graphrun_feature():
    from graphrun import load_features
    assert "photo-sort" in load_features()


def test_dry_run_writes_nothing(station, tmp_path, rules_file):
    out = tmp_path / "out"
    rep = _run(station, out, rules_file, apply=False)
    assert not rep.aborted
    names = [s.name for s in rep.stages]
    assert names[:3] == ["scan", "check", "classify"]      # reconcile chain always starts here
    assert names[-2:] == ["apply", "delete_empty"]
    assert {"scaffold", "even_four", "validate", "plan", "verify"} <= set(names)
    assert [s.status for s in rep.stages if s.name == "apply"] == ["skipped"]
    assert rep.sections["images_before"] == rep.sections["images_after"] == 13
    assert not out.exists()


def test_apply_moves_by_rules(station, tmp_path, rules_file):
    out = tmp_path / "out"
    rep = _run(station, out, rules_file, apply=True)
    assert not rep.aborted, rep.errors
    work = out / station.name / station.name

    assert (work / "3" / "chuan bi M1").is_dir()
    assert len(list((work / "3" / "chuan bi M2").glob("*.jpg"))) == 3
    assert len(list((work / "1" / "bien nha tram").glob("*.jpg"))) == 1
    assert len(list(work.rglob("*.jpg"))) == 13           # conservation


def test_input_untouched(station, tmp_path, rules_file):
    before = len(list(station.rglob("*.jpg")))
    _run(station, tmp_path / "out", rules_file, apply=True)
    assert len(list(station.rglob("*.jpg"))) == before


def test_conservation_catches_name_clash(station, tmp_path, rules_file):
    from photo_sort.models import Photo
    from photo_sort.steps.conservation import conservation

    ctx = RunContext(station, tmp_path / "o", Config.load(rules_file),
                     Report(feature="x"), dry_run=True)
    ctx.data["photos"] = [Photo("a/x.jpg", "", False), Photo("b/x.jpg", "", False)]
    ctx.data["assign"] = {"z": ["a/x.jpg", "b/x.jpg"]}   # both land as z/x.jpg
    ctx.data["moves"] = []
    ctx.data["landing"] = [("z", "x.jpg"), ("z", "x.jpg")]
    conservation.__wrapped__(ctx)
    assert ctx.report.aborted and "trùng" in ctx.report.errors[0]
