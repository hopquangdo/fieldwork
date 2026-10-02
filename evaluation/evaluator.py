"""So kết quả pipeline với ground truth (GT) — đo độ chính xác, không phụ thuộc trạm nào.

Hai thư mục được so bằng NỘI DUNG ảnh (sha1), không bằng tên — pipeline có thể đổi tên
ảnh nhưng ảnh vẫn là ảnh đó. Với mỗi ảnh khớp: đúng ⇔ nằm cùng thư mục (đường dẫn
tương đối từ thư mục ảnh) với GT. Ngoài ra so cả cấu trúc thư mục (kể cả thư mục rỗng).

    layout = read_layout(path)            # thư mục ảnh của 1 trạm (kết quả hoặc GT)
    res = compare(read_layout(out), read_layout(gt))
    print(format_result(res))

Không đụng LLM / pipeline ở đây; ``run_and_compare`` là lớp mỏng chạy pipeline rồi so.
"""
from __future__ import annotations

import hashlib
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from infrastructure.filesystem import WalkDirsTool, WalkFilesTool, longpath

from domain.station import image_root

walk_files, walk_dirs = WalkFilesTool(), WalkDirsTool()


@dataclass
class Layout:
    """Ảnh của một trạm: ``files`` = [(sha1, thư mục tương đối, tên)], ``dirs`` = mọi thư mục."""
    root: Path
    files: list[tuple[str, str, str]] = field(default_factory=list)
    dirs: set[str] = field(default_factory=set)


def _rel(p: Path, root: Path) -> str:
    return str(p.relative_to(root)).replace("\\", "/")


def read_layout(path: str | Path) -> Layout:
    """Đọc cấu trúc + băm ảnh. ``path`` là thư mục trạm HOẶC thư mục ảnh (tự tìm)."""
    root = image_root(Path(path).absolute())
    lay = Layout(root=root)
    for f in walk_files(root, images_only=True):
        digest = hashlib.sha1(longpath(f).read_bytes()).hexdigest()
        rel = _rel(f, root)
        folder, _, name = rel.rpartition("/")
        lay.files.append((digest, folder, name))
    lay.dirs = {_rel(d, root) for d in walk_dirs(root)}
    return lay


@dataclass
class Result:
    total: int                                   # số ảnh GT
    correct: int                                 # ảnh khớp và đúng thư mục
    wrong: list[tuple[str, str, str]]            # (tên GT, thư mục GT, thư mục kết quả)
    missing: list[tuple[str, str]]               # ảnh GT không thấy trong kết quả (tên, thư mục GT)
    extra: list[tuple[str, str]]                 # ảnh kết quả không có trong GT
    dirs_missing: list[str]                      # thư mục GT có mà kết quả thiếu
    dirs_extra: list[str]                        # thư mục kết quả có mà GT không
    per_group: dict[str, tuple[int, int]]        # {hạng mục: (đúng, tổng)}
    dir_score: float = 1.0                       # độ giống cấu trúc thư mục (Jaccard)

    @property
    def accuracy(self) -> float:
        return self.correct / self.total if self.total else 1.0


def _group(folder: str) -> str:
    return folder.split("/", 1)[0] if folder else "(gốc)"


def compare(out: Layout, gt: Layout) -> Result:
    """Ghép ảnh theo nội dung. Ảnh trùng nội dung được ghép ưu tiên cùng thư mục trước."""
    pool: dict[str, list[tuple[str, str]]] = defaultdict(list)   # sha1 -> [(thư mục, tên)] của kết quả
    for h, folder, name in out.files:
        pool[h].append((folder, name))

    correct = 0
    wrong: list[tuple[str, str, str]] = []
    missing: list[tuple[str, str]] = []
    per_group: dict[str, list[int]] = defaultdict(lambda: [0, 0])

    # lượt 1: ghép cặp cùng thư mục; lượt 2: phần còn lại
    left: list[tuple[str, str, str]] = []
    for h, folder, name in gt.files:
        g = per_group[_group(folder)]
        g[1] += 1
        cands = pool.get(h, [])
        hit = next((c for c in cands if c[0] == folder), None)
        if hit:
            cands.remove(hit)
            correct += 1
            g[0] += 1
        else:
            left.append((h, folder, name))
    for h, folder, name in left:
        cands = pool.get(h, [])
        if cands:
            wrong.append((name, folder, cands.pop(0)[0]))
        else:
            missing.append((name, folder))
    extra = [(name, folder) for lst in pool.values() for folder, name in lst]

    dmiss = sorted(gt.dirs - out.dirs)
    dextra = sorted(out.dirs - gt.dirs)
    union = len(gt.dirs | out.dirs)
    return Result(
        total=len(gt.files), correct=correct, wrong=wrong, missing=missing, extra=extra,
        dirs_missing=dmiss, dirs_extra=dextra,
        per_group={k: (v[0], v[1]) for k, v in sorted(per_group.items())},
        dir_score=len(gt.dirs & out.dirs) / union if union else 1.0,
    )


def format_result(res: Result, *, name: str = "", limit: int = 25) -> str:
    out = [f"── {name or 'kết quả'} ──",
           f"ảnh đúng thư mục : {res.correct}/{res.total}  ({res.accuracy:.1%})",
           f"cấu trúc thư mục : {res.dir_score:.1%}  "
           f"(thiếu {len(res.dirs_missing)}, thừa {len(res.dirs_extra)})",
           f"ảnh thiếu/thừa   : {len(res.missing)} / {len(res.extra)}",
           "theo hạng mục:"]
    for g, (ok, n) in res.per_group.items():
        out.append(f"  {'✓' if ok == n else '✗'} {ok:>3}/{n:<3} {g}")
    if res.wrong:
        out.append(f"ảnh sai chỗ ({len(res.wrong)}):")
        by_pair: dict[tuple[str, str], int] = defaultdict(int)
        for _, want, got in res.wrong:
            by_pair[(got, want)] += 1
        for (got, want), n in sorted(by_pair.items(), key=lambda kv: -kv[1])[:limit]:
            out.append(f"  {n:>3} × {got or '(gốc)'}  →cần→  {want or '(gốc)'}")
    if res.dirs_missing:
        out.append("thư mục thiếu: " + "; ".join(res.dirs_missing[:limit]))
    if res.dirs_extra:
        out.append("thư mục thừa : " + "; ".join(res.dirs_extra[:limit]))
    return "\n".join(out)


def discover_pairs(data_dir: str | Path, gt_dir: str | Path) -> list[tuple[str, Path, Path]]:
    """Quy ước: ``<gt_dir>/<tên>_gt`` là đáp án của ``<data_dir>/<tên>``."""
    pairs = []
    for gt in sorted(Path(gt_dir).glob("*_gt")):
        src = Path(data_dir) / gt.name[: -len("_gt")]
        if src.is_dir():
            pairs.append((src.name, src, gt))
    return pairs


def run_and_compare(input_dir: str | Path, gt_dir: str | Path, work_dir: str | Path,
                    *, rules: str | Path | None = None) -> Result:
    """Chạy pipeline (ghi thật) vào ``work_dir`` rồi so với GT.

    Cache vision đặt trong ``work_dir/_report`` nên chạy lại là replay — không tốn request."""
    from application.services.sort_photos import sort_photos
    import shutil

    work = Path(work_dir)
    out = work / "out"
    if out.exists():
        shutil.rmtree(longpath(out), ignore_errors=True)
    r = sort_photos(input_dir, out, rules=rules, report_dir=work / "_report")
    if r.aborted:
        raise RuntimeError(f"pipeline dừng: {'; '.join(r.errors)}")
    return compare(read_layout(out), read_layout(gt_dir))
