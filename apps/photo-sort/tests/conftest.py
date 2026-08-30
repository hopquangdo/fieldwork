from __future__ import annotations

from pathlib import Path

import pytest


try:
    from PIL import Image

    _PNG = None

    def _bytes(ext: str) -> bytes:
        import io

        global _PNG
        if _PNG is None:
            buf = io.BytesIO()
            Image.new("RGB", (2, 2), "white").save(buf, format="PNG")
            _PNG = buf.getvalue()
        if ext.lower() in (".jpg", ".jpeg"):
            buf = io.BytesIO()
            Image.new("RGB", (2, 2), "white").save(buf, format="JPEG")
            return buf.getvalue()
        return _PNG
except ModuleNotFoundError:  # pragma: no cover
    def _bytes(ext: str) -> bytes:
        return b"img"


def _w(base: Path, rel: str, names: list[str]) -> None:
    d = base / rel
    d.mkdir(parents=True, exist_ok=True)
    for n in names:
        (d / n).write_bytes(_bytes(Path(n).suffix))


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
