from __future__ import annotations

from pathlib import Path

import pytest


def _w(base: Path, rel: str, names: list[str]) -> None:
    d = base / rel
    d.mkdir(parents=True, exist_ok=True)
    for n in names:
        (d / n).write_bytes(b"img")


@pytest.fixture
def station(tmp_path: Path) -> Path:
    root = tmp_path / "NAN00145_Quỳ Hợp,Nghệ An"
    img = root / root.name

    _w(img, "1.Hình ảnh tổng thể cột anten/Hình ảnh khác tổng thể cột anten", [
        "@9@40@38@--0--.jpg",
        "Biển nhà trạm@9@30@11@--1--.jpg",
        "Móng M0@10@15@22@--0--.jpg",
    ])
    _w(img, "2.Công tác kiểm tra khe hở cấu kiện lắp ghép/Hình ảnh khác",
       [f"Đốt D{i}@8@{i:02d}@00@--0--.jpg" for i in (1, 2, 5, 6)] + ["Chân cột@8@05@00@--0--.jpg"])
    _w(img, "3.Công tác đo lực căng trong dây co/Hình ảnh khác",
       [f"Móng M1@10@01@{i:02d}@--{'1' if i == 0 else '0'}--.jpg" for i in range(3)]
       + [f"Móng M2@10@05@{i:02d}@--0--.jpg" for i in range(2)]
       + [f"Móng M3@10@10@{i:02d}@--0--.jpg" for i in range(4)]
       + ["Móng M4@10@15@00@--1--.jpg"])
    _w(img, "5.Công tác kiểm tra cường độ bê tông móng/Hình ảnh khác",
       [f"Móng M{m}@11@{m:02d}@{i:02d}@--0--.jpg" for m in (1, 2, 3) for i in range(2)])
    (img / "8.Công tác trèo cao (kiểm tra đường hàn, lực siết ê-cu,..)" / "Công tác chuẩn bị").mkdir(parents=True)
    _w(img, "10.Hình ảnh dị tật bất thường",
       ["Han rỉ thanh giằng@01@01@01@--0--.jpg", "Sơn bong tróc@01@01@02@--0--.jpg", "Ko mỡ bảo dưỡng@01@01@03@--0--.jpg"])

    data = root / "DataNAN00145_user Quỳ Hợp ok"
    data.mkdir(parents=True)
    (data / "TABLEBia.txt").write_text(
        "Loại cột: Dây co\nSố đốt: 6\nSố móng co: 4\nSố tầng dây co: 3\n", encoding="utf-8"
    )
    return root
