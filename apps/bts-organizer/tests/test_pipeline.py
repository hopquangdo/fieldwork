from pathlib import Path

from bts_organizer.config import AppConfig
from bts_organizer.discovery import locate, take_inventory
from bts_organizer.domain.metadata import read_meta
from bts_organizer.execution import original_images, simulate
from bts_organizer.layout import run_strategy
from bts_organizer.planning import build_operations
from bts_organizer.repair import repair
from bts_organizer.validation import validate
from bts_organizer.runner import run_station


def _layouts(station: Path):
    paths = locate(station)
    meta = read_meta(Path(paths.data_dir) if paths.data_dir else None)
    inv = take_inventory(station, paths.image_root, meta)
    return {i: run_strategy(inv[i], meta, {}) for i in inv}, inv


def test_meta_read(station):
    paths = locate(station)
    meta = read_meta(Path(paths.data_dir))
    assert meta.tower_type == "day_co" and meta.n_dot == 6 and meta.n_mong == 4


def test_inventory_finds_hang_muc(station):
    paths = locate(station)
    inv = take_inventory(station, paths.image_root, read_meta(Path(paths.data_dir)))
    assert set(inv) == {1, 2, 3, 5, 8, 10}
    assert inv[3].image_count == 10


def test_layout_per_mong_groups(station):
    layouts, _ = _layouts(station)
    m3 = layouts[3]
    ct = [f for f in m3.folders if f.is_cong_tac]
    assert {f.path[-2:] for f in ct} >= {"M1", "M2", "M3"}
    assert any(f.is_khac for f in m3.folders)


def test_conservation_after_repair_loop(station):
    layouts, inv = _layouts(station)
    original = original_images(inv)
    for _ in range(6):
        issues = validate(simulate(layouts, inv), original=original, answers={})
        if not [i for i in issues if i.severity == "REPAIRABLE"]:
            break
        layouts, _ = repair(layouts, issues)
    tree = simulate(layouts, inv)
    assert tree.images_after == original                      # không mất / không đẻ ảnh
    remaining = validate(tree, original=original, answers={})
    assert not [i for i in remaining if i.severity in ("HARD", "REPAIRABLE")]


def test_build_operations_are_mkdir_then_move(station):
    layouts, inv = _layouts(station)
    ops = build_operations(layouts, inv)
    kinds = [o.action for o in ops]
    assert kinds and kinds.index("mkdir") < (kinds.index("move") if "move" in kinds else len(kinds))


def test_full_run_dry_run(station):
    report = run_station(station, config=AppConfig(dry_run=True, no_vision=True))
    assert report.images_before == report.images_after
    assert not report.aborted
    assert report.exec["status"] == "dry_run"
    assert {c["id"] for c in report.counts} == {1, 2, 3, 5, 8, 10}
    assert all(c["even_folders"] for c in report.counts)


def test_full_run_apply_moves_files(station, tmp_path):
    report = run_station(station, config=AppConfig(dry_run=False, no_vision=True))
    assert report.exec["status"] == "applied"
    assert report.exec["failed"] == 0, report.exec["failures"]
    img_root = station / station.name
    # M3's folder now holds its 4 photos, none left loose in "Hình ảnh khác"
    m3 = list((img_root / "3.Công tác đo lực căng trong dây co").glob("*M3/*.jpg"))
    assert len(m3) == 4
