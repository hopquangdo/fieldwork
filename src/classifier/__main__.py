"""``python -m classifier INPUT OUTPUT [--tower tu_dung] [--no-vision]``"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from classifier.pipeline import run


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="photo-classify",
                                 description="Phân loại folder ảnh phẳng vào mục lục phụ lục chuẩn.")
    ap.add_argument("input", help="folder ảnh (phẳng, vd tải từ Zalo) hoặc thư mục trạm")
    ap.add_argument("output", help="thư mục kết quả")
    ap.add_argument("--tower", help="loại cột (tu_dung / day_co…) khi không có TABLEBia")
    ap.add_argument("--rules", help="file rules .toml (ghi đè --tower)")
    ap.add_argument("--report-dir", default=".output")
    ap.add_argument("--no-vision", action="store_true", help="chỉ dùng tên file, không gọi LLM")
    a = ap.parse_args(argv)
    rep = run(Path(a.input), Path(a.output), tower_type=a.tower, rules=a.rules,
              cache_dir=Path(a.report_dir), use_vision=not a.no_vision)
    path = rep.save(Path(a.report_dir) / f"classify-{rep.station}.json")
    print(rep.summary())
    print(f"report: {path}")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
