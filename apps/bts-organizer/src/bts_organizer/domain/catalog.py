"""The inspection categories (hạng mục) per tower type + folder-role helpers."""
from __future__ import annotations

from bts_organizer.domain.models import TowerType

HANG_MUC_DAY_CO: dict[int, str] = {
    1: "Hình ảnh tổng thể cột anten",
    2: "Công tác kiểm tra khe hở cấu kiện lắp ghép",
    3: "Công tác đo lực căng trong dây co",
    4: "Công tác kiểm tra lực siết khóa cáp",
    5: "Công tác kiểm tra cường độ bê tông móng",
    6: "Công tác đo điện trở nối đất hệ thống chống sét",
    7: "Công tác đo nghiêng cột anten",
    8: "Công tác trèo cao (kiểm tra đường hàn, lực siết ê-cu,..)",
    9: "Công tác đo kích thước cấu kiện cột và siêu âm thanh cánh",
    10: "Hình ảnh dị tật bất thường",
}

# tự đứng: bỏ mục 3, 4 của dây co rồi đánh số lại
HANG_MUC_TU_DUNG: dict[int, str] = {
    1: "Hình ảnh tổng thể cột anten",
    2: "Công tác kiểm tra khe hở cấu kiện lắp ghép",
    3: "Công tác kiểm tra cường độ bê tông móng",
    4: "Công tác đo điện trở nối đất hệ thống chống sét",
    5: "Công tác đo nghiêng cột anten",
    6: "Công tác trèo cao (kiểm tra đường hàn, lực siết ê-cu,..)",
    7: "Công tác đo kích thước cấu kiện cột anten",
    8: "Hình ảnh dị tật bất thường",
}

# hạng mục hay vắng ảnh -> nếu 0 ảnh thì bỏ qua hẳn, không dựng khung
OPTIONAL_WHEN_EMPTY = {7}

# hạng mục giữ nguyên, không sắp lại
KEEP_AS_IS_DAY_CO = {10}
KEEP_AS_IS_TU_DUNG = {8}

KHAC = "Hình ảnh khác"
KHAC_TONG_THE = "Hình ảnh khác tổng thể cột anten"


def hang_muc(tower_type: TowerType) -> dict[int, str]:
    return HANG_MUC_TU_DUNG if tower_type == "tu_dung" else HANG_MUC_DAY_CO


def keep_as_is(tower_type: TowerType) -> set[int]:
    return KEEP_AS_IS_TU_DUNG if tower_type == "tu_dung" else KEEP_AS_IS_DAY_CO


def is_khac_folder(name: str) -> bool:
    return name.casefold().startswith("hình ảnh khác")


def is_cong_tac_folder(name: str) -> bool:
    return name.casefold().startswith("công tác") or "chuẩn bị" in name.casefold()
