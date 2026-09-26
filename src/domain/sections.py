"""Tên các mục trong ``report.sections`` — MỘT chỗ duy nhất.

Các bước ghi vào, còn ``application.services.sort_photos``, CLI, eval và UI đọc lại, nên
đổi chữ ở đây là đổi cho mọi bên. Giá trị là chuỗi hiển thị cho người đọc báo cáo
(``llm_usage`` giữ nguyên vì UI đọc theo khoá này).
"""
from __future__ import annotations

META = "meta"
IMAGES_BEFORE = "images_before"
IMAGES_AFTER = "images_after"
WRITTEN = "written"
PLAN = "plan"
CONFLICTS = "conflicts"
LLM_USAGE = "llm_usage"
OUTPUT_DIR = "output_dir"          # thư mục kết quả THỰC (có thể đã thêm hậu tố " (2)")

NEEDS_REVIEW = "cần người xem"
INPUT_ISSUES = "vấn đề đầu vào"
BAD_IMAGES = "ảnh lỗi / rỗng (bỏ qua)"
DUPLICATES = "ảnh trùng nội dung (bỏ qua)"
SKIPPED_DIRS = "thư mục bỏ qua (bản lồng / không có ảnh)"
RENAMED_DIRS = "đổi tên thư mục chuẩn"
LOOSE_MATCH = "khớp lỏng (from_folder không khớp)"
SHORT_OF_PHOTOS = "hạng mục thiếu ảnh (cần nhặt bù)"
AGENT_LOG = "agent_repair · nhật ký tool"


def issues_round(n: int) -> str:
    """Vi phạm cấu trúc còn lại ở vòng ``validate`` thứ ``n``."""
    return f"issues (vòng {n})"
