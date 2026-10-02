"""Nối các tầng: intake → catalog → evidence → decide → output.

    run(input, output)  →  Report

Input không bao giờ bị sửa (output = bản COPY). Không có LLM_API_KEY → chỉ dùng bằng
chứng tên file; ảnh còn lại vào 'Hình ảnh khác' + cần người xem.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable

from config.loader import load_dotenv

from classifier.catalog import build_catalog, load_profile
from classifier.decide import enforce, fuse, resolve
from classifier.evidence import base as ev
from classifier.evidence import filename, overlay_ocr, sequence, vision
from classifier.intake import read_source
from classifier.intake.metadata import station_meta
from classifier.llm import LLM, JsonCache
from classifier.output import Report, apply, plan, verify

Emit = Callable[[str], None]


def run(src: Path, out: Path, *, tower_type: str | None = None, rules: Path | None = None,
        cache_dir: Path = Path(".output"), use_vision: bool = True,
        emit: Emit = print) -> Report:
    load_dotenv()
    src, out = Path(src).resolve(), Path(out).resolve()
    if out == src or src in out.parents or out in src.parents:
        raise ValueError("output không được trùng / nằm trong / chứa input")

    # 1. thông số trạm + profile
    meta = station_meta(src, tower_type)
    prof = load_profile(meta.tower_type, rules)
    rep = Report(station=src.name, tower_type=meta.tower_type, warnings=list(meta.warnings))

    # 2. intake
    batch = read_source(src, prof)
    rep.flat, rep.photos = batch.flat, len(batch.photos)
    rep.duplicates = [f"{d}  (trùng {k})" for d, k in batch.duplicates]
    rep.broken = batch.broken
    emit(f"intake: {len(batch.photos)} ảnh · {len(batch.duplicates)} trùng · "
         f"{len(batch.extras)} file khác · {'phẳng' if batch.flat else 'cây trạm'}")

    # 3. mục lục — TRƯỚC khi phân loại
    cat = build_catalog(prof, meta)
    rep.catalog = cat.leaves()
    emit(f"catalog: {len(cat.sections)} hạng mục · {len(rep.catalog)} thư mục ({meta.tower_type})")

    # 4. bằng chứng
    cfg = prof.raw.get("classify") or {}
    ballots = [filename.collect(batch.photos, cat, prof)]
    emit(f"filename: {len(ballots[0])} ảnh có phiếu")
    llm = LLM()
    if use_vision and llm.available():
        cache = JsonCache(Path(cache_dir) / "classifier-vision-cache.json")
        vb, overlay = vision.collect(
            batch.photos, cat, llm, cache, batch=int(prof.vision.get("batch", 8)),
            on_progress=lambda i, n: emit(f"vision: {i}/{n}"))
        ballots.append(vb)
        n_time = overlay_ocr.fill_times(batch.photos, overlay)
        emit(f"vision: {len(vb)} ảnh có phiếu · {n_time} ảnh có giờ chụp")
        rep.llm = {"model": llm.usage.model, **llm.usage.to_dict()}
    else:
        rep.warnings.append("không chạy vision (thiếu LLM_API_KEY hoặc tắt) — chỉ dùng tên file")
    base = ev.merge(*ballots)
    seq = cfg.get("sequence") or {}
    ballots.append(sequence.collect(batch.photos, cat, base,
                                    window_sec=int(seq.get("window_sec", 120)),
                                    window_n=int(seq.get("window_n", 2)),
                                    weight=float(seq.get("weight", 0.3))))

    # 5. quyết định
    weights = {k: float(v) for k, v in (cfg.get("weights") or {}).items()}
    decisions = fuse(batch.photos, cat, ev.merge(*ballots), weights)
    resolve(decisions, cat, min_conf=float(cfg.get("min_conf", 0.6)))
    rep.constraints = enforce(decisions, cat, prof)
    rep.review = [f"{d.photo_id}: {d.review}" for d in decisions.values() if d.review]

    # 6. ghi ra
    moves = plan(batch.photos, decisions, prof, rename_khac=batch.flat)
    errs = verify(batch.photos, moves)
    if errs:
        rep.errors = errs
        return rep
    station_out = out / src.name
    rep.applied = apply(moves, cat, station_out, batch.extras)
    for m in moves:
        rep.distribution[m.folder] = rep.distribution.get(m.folder, 0) + 1
    by_id = {p.id: p for p in batch.photos}
    rep.decisions = [
        {"photo": d.photo_id, "folder": d.folder, "confidence": round(d.confidence, 2),
         "taken_at": by_id[d.photo_id].taken_at, "description": by_id[d.photo_id].description,
         "votes": d.reasons, "review": d.review}
        for d in decisions.values()
    ]
    return rep
