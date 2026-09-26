from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _no_real_llm(monkeypatch, tmp_path):
    """Không test nào được gọi LLM thật (tốn tiền, chậm, không lặp lại được): xoá key khỏi
    môi trường và chạy từ thư mục tạm để không đọc ``.env`` ở gốc repo. Test cần LLM thì
    dùng model giả / bản ghi (xem tests/unit/agent)."""
    for k in ("LLM_API_KEY", "OPENROUTER_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"):
        monkeypatch.setenv(k, "")
    monkeypatch.chdir(tmp_path)


import itertools

_SEQ = itertools.count(1)   # mỗi ảnh fixture một nội dung riêng — scan loại ảnh trùng sha1

try:
    from PIL import Image

    def _bytes(ext: str) -> bytes:
        import io

        n = next(_SEQ)
        buf = io.BytesIO()
        fmt = "JPEG" if ext.lower() in (".jpg", ".jpeg") else "PNG"
        Image.new("RGB", (2 + n % 50, 2 + n // 50), "white").save(buf, format=fmt)
        return buf.getvalue()
except ModuleNotFoundError:  # pragma: no cover
    def _bytes(ext: str) -> bytes:
        return b"img%d" % next(_SEQ)


def _w(base: Path, rel: str, names: list[str]) -> None:
    d = base / rel
    d.mkdir(parents=True, exist_ok=True)
    for n in names:
        (d / n).write_bytes(_bytes(Path(n).suffix))


@pytest.fixture(autouse=True)
def _offline(monkeypatch):
    """Unit tests never touch a real LLM — vision / agent_repair soft-skip when the key
    is absent (a prior test running the API may have loaded .env into os.environ)."""
    monkeypatch.delenv("LLM_API_KEY", raising=False)


@pytest.fixture
def station(tmp_path: Path) -> Path:
    """Compact fake station — short folder names to stay under MAX_PATH in test temp dirs."""
    root = tmp_path / "NAN00145"
    img = root / root.name

    _w(img, "1/khac tong the",
       ["Biển nhà trạm@9@30@11@--1--.jpg", "Mặt đứng cột anten@9@31@00@--0--.jpg"])
    _w(img, "2/khac khe ho",
       [f"Đốt D{i}@8@{i:02d}@00@--0--.jpg" for i in (1, 2, 5, 6)] + ["@8@05@00@--0--.jpg"])
    _w(img, "3/khac luc cang",
       [f"Móng M1@10@01@{i:02d}@--0--.jpg" for i in range(2)]
       + [f"Móng M2@10@05@{i:02d}@--0--.jpg" for i in range(3)])
    _w(img, "10", ["Han rỉ thanh giằng@1@1@1@--0--.jpg"])

    data = root / "DataNAN00145 ok"
    data.mkdir(parents=True)
    (data / "TABLEBia.txt").write_text("Loại cột: Dây co\n", encoding="utf-8")
    return root


@pytest.fixture
def rules_file() -> Path:
    return Path(__file__).parent / "rules_test.toml"
