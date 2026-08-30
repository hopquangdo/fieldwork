"""Canonical hạng mục folder names, per tower type."""
from __future__ import annotations

DAY_CO = {
    1: "1.Hình ảnh tổng thể cột anten",
    2: "2.Công tác kiểm tra khe hở cấu kiện lắp ghép",
    3: "3.Công tác đo lực căng trong dây co",
    4: "4.Công tác kiểm tra lực siết khóa cáp",
    5: "5.Công tác kiểm tra cường độ bê tông móng",
    6: "6.Công tác đo điện trở nối đất hệ thống chống sét",
    7: "7.Công tác đo nghiêng cột anten",
    8: "8.Công tác trèo cao (kiểm tra đường hàn, lực siết ê-cu,..)",
    9: "9.Công tác đo kích thước cấu kiện cột và siêu âm thanh cánh",
    10: "10.Hình ảnh dị tật bất thường",
}

TU_DUNG = {
    1: "1.Hình ảnh tổng thể cột anten",
    2: "2.Công tác kiểm tra khe hở cấu kiện lắp ghép",
    3: "3.Công tác kiểm tra cường độ bê tông móng",
    4: "4.Công tác đo điện trở nối đất hệ thống chống sét",
    5: "5.Công tác đo nghiêng cột anten",
    6: "6.Công tác trèo cao (kiểm tra đường hàn, lực siết ê-cu,..)",
    7: "7.Công tác đo kích thước cấu kiện cột anten",
    8: "8.Hình ảnh dị tật bất thường",
}

KHAC = "Hình ảnh khác"


def hang_muc(tower_type: str) -> dict[int, str]:
    return TU_DUNG if tower_type == "tu_dung" else DAY_CO
