"""Đóng gói photo-sort thành thư mục chạy OFFLINE cho máy client (Windows x64).

    uv run python scripts/build_dist.py            # -> dist/photo-sort/ + dist/photo-sort.zip
    uv run python scripts/build_dist.py --client   # -> dist/photo-sort-client/ (chỉ UI, backend ở Docker)
    python scripts/build_dist.py --harden <site-packages>   # chỉ nhúng rules + ẩn source (Dockerfile dùng)

Kết quả (không cần cài Python / uv / Bun trên máy client):

    photo-sort/
      Chay.bat          nhấp đúp: mở UI, UI tự bật backend
      ui.exe            UI terminal (bun build --compile)
      python/           CPython độc lập + mọi thư viện đã cài sẵn
      HUONG_DAN.txt

Bảo vệ IP: code của mình (mọi package trong src/) chỉ còn bytecode ``.pyc``; rules/*.toml được
nhúng vào ``pipeline/_embedded_rules.pyc`` (không có file .toml trên đĩa). Chỉ chống đọc/sửa
thông thường, không chống dịch ngược bytecode.

Cần trên máy build: uv, bun, mạng (lần đầu tải thư viện).
"""
from __future__ import annotations

import compileall
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DIST = REPO / "dist"
OUT = DIST / "photo-sort"
PY_VERSION = "3.12"
#: Tên file đính kèm GitHub Release — npm/install.js tải đúng tên này.
ASSET = "photo-sort-win-x64"
# Phần của CPython không cần khi chạy.
PY_SKIP = {"Lib/test", "Lib/idlelib", "Lib/tkinter", "Lib/turtledemo", "Lib/ensurepip",
           "Lib/site-packages", "Lib/EXTERNALLY-MANAGED", "tcl", "include", "libs", "Scripts"}


def run(*cmd: str, cwd: Path = REPO) -> str:
    print("  $", " ".join(cmd))
    exe = shutil.which(cmd[0]) or cmd[0]   # bun cài qua npm là bun.cmd
    return subprocess.run([exe, *cmd[1:]], cwd=cwd, check=True, text=True, capture_output=True).stdout


def copy_python() -> Path:
    run("uv", "python", "install", PY_VERSION)   # bản độc lập (python-build-standalone), copy được
    exe = run("uv", "python", "find", "--managed-python", PY_VERSION).strip()
    # find có thể trả python của .venv → lấy bản gốc qua sys.base_prefix
    home = Path(run(exe, "-c", "import sys; print(sys.base_prefix)").strip())
    dst = OUT / "python"

    def ignore(d: str, names: list[str]) -> set[str]:
        rel = Path(d).relative_to(home)
        return {n for n in names
                if (rel / n).as_posix() in PY_SKIP or n == "__pycache__"}

    shutil.copytree(home, dst, ignore=ignore)
    (dst / "Lib" / "site-packages").mkdir()
    return dst / "python.exe"


def install_packages(py: Path) -> Path:
    # Khoá đúng phiên bản như uv.lock; bỏ các gói local (cài riêng từ path, không editable).
    req = DIST / "requirements.txt"
    run("uv", "export", "--frozen", "--no-dev", "--no-hashes", "--no-emit-project",
        "-o", str(req))
    run("uv", "pip", "install", "--python", str(py), "--no-deps", "-r", str(req))
    run("uv", "pip", "install", "--python", str(py), "--no-deps", ".")
    site = py.parent / "Lib" / "site-packages"
    # __pycache__ chứa tên file dài nhất (…cpython-312.pyc) — bỏ để đường dẫn khi cài qua
    # npm (%APPDATA%\npm\node_modules\…\vendor\…) còn xa giới hạn 260 ký tự của Windows.
    for cache in list(site.rglob("__pycache__")):
        shutil.rmtree(cache)
    return site


def embed_rules(site: Path) -> None:
    rules = {p.name: p.read_text(encoding="utf-8") for p in sorted((REPO / "rules").glob("*.toml"))}
    body = "".join(f"    {name!r}: {text!r},\n" for name, text in rules.items())
    (site / "pipeline" / "_embedded_rules.py").write_text(
        f'"""Sinh bởi scripts/build_dist.py — KHÔNG sửa tay."""\nRULES = {{\n{body}}}\n',
        encoding="utf-8")
    print(f"  nhúng {len(rules)} rules: {', '.join(rules)}")


def strip_sources(site: Path) -> None:
    """Chỉ giữ .pyc (đặt cạnh, kiểu legacy) cho code của mình."""
    ours = [site / p.name for p in (REPO / "src").iterdir()
            if p.name != "__pycache__" and (p.is_dir() or p.suffix == ".py")]
    n = 0
    for root in ours:
        if not root.exists():
            raise SystemExit(f"thiếu {root} — wheel photo-sort không cài đúng?")
        if root.is_file():
            compileall.compile_file(str(root), legacy=True, quiet=1)
            root.unlink(); n += 1
            continue
        compileall.compile_dir(str(root), legacy=True, quiet=1)
        for py in root.rglob("*.py"):
            py.unlink(); n += 1
        for cache in root.rglob("__pycache__"):
            shutil.rmtree(cache)
    print(f"  bỏ {n} file .py (còn .pyc)")


def build_ui(out: Path = OUT) -> None:
    ui = REPO / "ui"
    if not (ui / "node_modules").exists():
        run("bun", "install", cwd=ui)
    run("bun", "build", "--compile", "src/index.tsx", "--outfile", str(out / "ui.exe"), cwd=ui)


LAUNCHER = r"""@echo off
rem  photo-sort: mo giao dien; giao dien tu bat backend (python\python.exe).
cd /d "%~dp0"
set PYTHONUTF8=1
rem  Thu muc mac dinh dien san trong UI (de trong = nhap tay trong UI)
set BTS_INPUT=
set BTS_OUTPUT=
ui.exe
if errorlevel 1 pause
"""

GUIDE = """photo-sort — sắp ảnh kiểm định cột BTS
========================================

Cài đặt: giải nén cả thư mục này vào ổ đĩa (vd D:\\photo-sort). Không cần cài gì thêm,
không cần mạng (trừ bước AI gọi model).

1. Nhấp đúp Chay.bat (bản cài qua npm: gõ  photo-sort).
2. Lần đầu: dán API key (OpenRouter) vào ô "API key" rồi Enter — lưu ở %APPDATA%\\photo-sort.
   Không có key: vẫn chạy, bỏ bước AI.
3. Nhập thư mục trạm + thư mục kết quả, chạy.   Tab = chuyển ô · Esc = thoát.

Báo cáo + log backend: %LOCALAPPDATA%\\photo-sort\\.output
"""


CLIENT_LAUNCHER = r"""@echo off
rem  photo-sort (client): chi mo giao dien, backend chay o Docker / may chu.
cd /d "%~dp0"
rem  Dia chi backend - doi thanh IP may chu neu backend khong chay tren may nay
set BTS_API_URL=http://127.0.0.1:8765
set BTS_BACKEND=external
set BTS_INPUT=
set BTS_OUTPUT=
ui.exe
if errorlevel 1 pause
"""

CLIENT_GUIDE = """photo-sort — giao diện (client)
================================

Backend chạy riêng trong Docker (xem docker-compose.yml trong repo). Máy này chỉ cần thư mục này.

1. Mở Chay.bat bằng Notepad nếu backend ở máy khác: sửa BTS_API_URL=http://<ip-máy-chủ>:8765
2. Nhấp đúp Chay.bat.
3. Nhập đường dẫn thư mục như bình thường (vd D:\\anh\\DBN00009_2) — backend tự đổi sang
   thư mục đã mount trong Docker (GRAPHRUN_PATH_MAP). Thư mục phải nằm trong ổ đã mount.
"""


def build_client() -> None:
    out = DIST / "photo-sort-client"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    build_ui(out)
    (out / "Chay.bat").write_text(CLIENT_LAUNCHER.replace("\n", "\r\n"), encoding="ascii")
    (out / "HUONG_DAN.txt").write_text(CLIENT_GUIDE.replace("\n", "\r\n"), encoding="utf-8-sig")
    zip_path = shutil.make_archive(str(out), "zip", DIST, out.name)
    print(f"\nXong: {out}\n      {zip_path}")


def write_launcher() -> None:
    (OUT / "Chay.bat").write_text(LAUNCHER.replace("\n", "\r\n"), encoding="ascii")
    (OUT / "HUONG_DAN.txt").write_text(GUIDE.replace("\n", "\r\n"), encoding="utf-8-sig")


def smoke_test(py: Path) -> None:
    out = subprocess.run(
        [str(py), "-c", "from runtime import load_features; import pipeline.feature as f;"
         " print(sorted(load_features()), f._BASE.name, f.toml_exists(f._BASE))"],
        cwd=OUT, check=True, text=True, capture_output=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},   # không sinh lại __pycache__ trước khi nén
    ).stdout.strip()
    print("  smoke:", out)
    if "photo-sort" not in out or not out.endswith("True"):
        raise SystemExit("smoke test hỏng")


def main() -> int:
    args = sys.argv[1:]
    if args[:1] == ["--harden"]:
        site = Path(args[1])
        embed_rules(site); strip_sources(site)
        return 0
    if args[:1] == ["--client"]:
        build_client()
        return 0
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    print("[1/6] copy Python"); py = copy_python()
    print("[2/6] cài thư viện"); site = install_packages(py)
    print("[3/6] nhúng rules"); embed_rules(site)
    print("[4/6] ẩn source"); strip_sources(site)
    print("[5/6] build UI"); build_ui(); write_launcher()
    print("[6/6] kiểm tra + nén"); smoke_test(py)
    zip_path = shutil.make_archive(str(DIST / ASSET), "zip", DIST, "photo-sort")
    size = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file()) / 1e6
    print(f"\nXong: {OUT}  ({size:.0f} MB)\n      {zip_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
