"""Thu nhỏ 1 trạm (+ đáp án) thành bộ dữ liệu eval nhẹ cho CI.

    uv run python scripts/make_eval_fixture.py <trạm thô> <thư mục đáp án> <thư mục ra>
    # vd: data/RAW/DBN00009_2  data/GT/DBN00009_2_gt  tests/fixtures/eval
    #  →  tests/fixtures/eval/raw/DBN00009_2/…   tests/fixtures/eval/gt/DBN00009_2_gt/…

Mỗi ảnh → JPEG 16×16 sinh CỐ ĐỊNH từ sha1 của ảnh gốc (cùng ảnh ở trạm và ở đáp án → cùng
bytes, nên evaluator vẫn ghép theo nội dung), giữ tên file, EXIF (giờ chụp) và mtime.
Ảnh hỏng giữ nguyên là hỏng. File không phải ảnh (TABLEBia…) chép nguyên. Không còn nội
dung ảnh thật. Bước vision/agent không chạy trên bộ này (không có LLM trong CI) → điểm là
của riêng phần cơ chế theo rules.
"""
from __future__ import annotations

import hashlib
import io
import os
import shutil
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from infrastructure.filesystem import IMAGE_EXTS, longpath  # noqa: E402


def _tiny(src: Path) -> bytes:
    raw = longpath(src).read_bytes()
    digest = hashlib.sha1(raw).digest()
    try:
        with Image.open(io.BytesIO(raw)) as im:
            im.verify()
        with Image.open(io.BytesIO(raw)) as im:
            exif = im.info.get("exif", b"")
    except Exception:  # noqa: BLE001 — ảnh hỏng: giữ là hỏng
        return b"" if not raw else b"broken:" + digest
    tile = Image.new("RGB", (16, 16))
    tile.putdata([tuple(digest[(i * 3 + k) % 20] for k in range(3)) for i in range(256)])
    buf = io.BytesIO()
    tile.save(buf, format="JPEG", quality=90, exif=exif)
    return buf.getvalue()


def shrink(src_root: Path, dst_root: Path) -> int:
    n = 0
    for dirpath, _, files in os.walk(longpath(src_root)):
        rel = Path(dirpath.replace("\\\\?\\", "")).relative_to(src_root)
        out_dir = dst_root / rel
        longpath(out_dir).mkdir(parents=True, exist_ok=True)
        for name in files:
            src, dst = Path(dirpath) / name, out_dir / name
            if Path(name).suffix.lower() in IMAGE_EXTS:
                longpath(dst).write_bytes(_tiny(src))
                n += 1
            else:
                shutil.copyfile(src, longpath(dst))
            shutil.copystat(src, longpath(dst))            # mtime — bậc dự phòng của giờ chụp
    return n


def main() -> int:
    raw, gt, out = (Path(a).resolve() for a in sys.argv[1:4])
    name = raw.name
    for src, dst in ((raw, out / "raw" / name), (gt, out / "gt" / f"{name}_gt")):
        if dst.exists():
            shutil.rmtree(longpath(dst))
        print(f"{dst}: {shrink(src, dst)} ảnh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
