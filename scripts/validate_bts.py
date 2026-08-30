r"""Check a sorted station folder against the appendix SOP (HUONG_DAN_SAP_XEP_HINH_ANH.md §5).

    uv run python scripts/validate_bts.py "<station folder>" [expected_total_images]
"""
import os
import re
import sys

IMG = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff")
NUMDIR = re.compile(r"^\s*(\d+)\s*[.\-_ ]")
CONFORM = re.compile(r".+@\s*\d{1,2}@\s*\d{1,2}@\s*\d{1,2}@--[01]--\.[A-Za-z0-9]+$")
KEEP_AS_IS = {1, 10}


def lp(p):
    return "\\\\?\\" + os.path.abspath(p) if os.name == "nt" else p


def image_root(station):
    def has_num(d):
        try:
            return any(NUMDIR.match(n) for n in os.listdir(lp(d)) if os.path.isdir(os.path.join(lp(d), n)))
        except OSError:
            return False
    if has_num(station):
        return station
    same = os.path.join(station, os.path.basename(station))
    if os.path.isdir(lp(same)) and has_num(same):
        return same
    for n in sorted(os.listdir(lp(station))):
        p = os.path.join(station, n)
        if os.path.isdir(lp(p)) and has_num(p):
            return p
    return station


def count_imgs(d):
    return sum(1 for _, _, fs in os.walk(lp(d)) for f in fs if f.lower().endswith(IMG))


def main(station, expected=None):
    root = image_root(station)
    problems, notes = [], []
    total = count_imgs(root)

    hm_dirs = sorted(
        (int(NUMDIR.match(n)[1]), n) for n in os.listdir(lp(root))
        if os.path.isdir(os.path.join(lp(root), n)) and NUMDIR.match(n)
    )

    print(f"station image root: ...{os.sep}{os.path.basename(root)}")
    print(f"total images: {total}" + (f"  (expected {expected})" if expected else ""))
    if expected and total != int(expected):
        problems.append(f"TỔNG ẢNH LỆCH: {total} != {expected}")

    for hid, name in hm_dirs:
        base = os.path.join(root, name)
        subs = sorted(n for n in os.listdir(lp(base)) if os.path.isdir(os.path.join(lp(base), n)))
        cong_tac = [s for s in subs if s.casefold().startswith("công tác") or "chuẩn bị" in s.casefold()]
        khac = [s for s in subs if s.casefold().startswith("hình ảnh khác")]
        loose = sum(1 for f in os.listdir(lp(base)) if f.lower().endswith(IMG))
        line = f"  Mục {hid:>2} · {len(subs)} thư mục con"

        if hid in KEEP_AS_IS:
            print(line + "  (giữ nguyên — bỏ qua luật cặp)")
            if not subs and loose == 0:
                problems.append(f"Mục {hid}: rỗng hoàn toàn")
            if hid == 1:                       # SOP §5: mỗi thư mục con Mục 1 phải có ≥1 ảnh
                for s in subs:
                    if "khác" in s.casefold():
                        continue
                    if count_imgs(os.path.join(base, s)) == 0:
                        problems.append(f"Mục 1: '{s}' KHÔNG có ảnh (SOP: mỗi thư mục con ≥1)")
            continue

        flags = []
        if len(cong_tac) < 2:
            problems.append(f"Mục {hid}: chỉ {len(cong_tac)} thư mục công tác (cần ≥2)")
            flags.append("<2 công tác")
        if len(cong_tac) % 2:
            problems.append(f"Mục {hid}: {len(cong_tac)} thư mục công tác — LẺ (phải chẵn)")
            flags.append("lẻ thư mục")
        if not khac:
            problems.append(f"Mục {hid}: thiếu 'Hình ảnh khác'")
            flags.append("thiếu khác")
        elif len(khac) > 1:
            notes.append(f"Mục {hid}: {len(khac)} thư mục 'Hình ảnh khác' — {khac}")
        odd = []
        for s in cong_tac:
            if "siêu âm" in s.casefold():
                continue
            c = count_imgs(os.path.join(base, s))
            if c % 2:
                odd.append(f"{s}={c}")
            # SOP: thư mục '… Móng Mx' phải chứa đúng ảnh móng đó
            mk = re.search(r"\bM(\d+)\b", s)
            if mk:
                for _, _, ff in os.walk(lp(os.path.join(base, s))):
                    for f in ff:
                        pm = re.search(r"m[oó]ng\s*m(\d+)", f, re.I)
                        if pm and pm[1] != mk[1]:
                            notes.append(f"Mục {hid}: '{s}' có ảnh móng M{pm[1]} (khác tên thư mục)")
        if odd:
            problems.append(f"Mục {hid}: thư mục công tác số ảnh LẺ — {odd}")
            flags.append("lẻ ảnh")
        if loose:
            notes.append(f"Mục {hid}: {loose} ảnh nằm ngay dưới thư mục hạng mục (không trong thư mục con)")

        print(line + (f"  ⚠ {', '.join(flags)}" if flags else "  ✓"))

    # filename convention
    bad_names = []
    for r, _, fs in os.walk(lp(root)):
        if "hình ảnh khác" in os.path.basename(r).casefold():
            continue
        for f in fs:
            if f.lower().endswith(IMG) and not CONFORM.match(f):
                bad_names.append(f)
    if bad_names:
        problems.append(f"{len(bad_names)} ảnh tên KHÔNG theo quy ước @h@m@s@--x--: {bad_names[:3]}")

    # empty dirs
    empties = [
        r[len(lp(root)):].strip("\\") for r, ds, fs in os.walk(lp(root))
        if not ds and not fs and "khác" not in os.path.basename(r).casefold()
    ]
    if empties:
        notes.append(f"{len(empties)} thư mục rỗng (không phải 'khác'): {empties[:5]}")

    print("\n--- KẾT LUẬN ---")
    if not problems:
        print("✅ HỢP LỆ theo các luật kiểm được (cặp thư mục chẵn · ảnh chẵn · có 'Hình ảnh khác' · không mất ảnh)")
    else:
        print(f"❌ CHƯA HỢP LỆ — {len(problems)} vấn đề:")
        for p in problems:
            print(f"   ! {p}")
    for n in notes:
        print(f"   · {n}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
