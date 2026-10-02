"""Phân loại ảnh PHẲNG (vd ảnh gửi qua Zalo: tên file vô nghĩa, không EXIF, không cây
thư mục) vào MỤC LỤC chuẩn của profile.

Luồng (``classifier.pipeline.run``)::

    catalog  → dựng mục lục từ profile TOML (hạng mục · thư mục con · biến {móng}/{đốt}/{vị trí})
    intake   → đọc nguồn (folder phẳng / cây trạm), gộp ảnh trùng, đọc TABLEBia nếu có
    evidence → mỗi nguồn bằng chứng bỏ phiếu ĐỘC LẬP: filename · vision (+ giờ in trên ảnh) · sequence
    decide   → gộp phiếu có trọng số → 1 thư mục/ảnh; dưới ngưỡng → 'khác' + cần người xem;
               áp ràng buộc SOP (số ảnh chẵn…)
    output   → plan (đích + tên mới) → verify (vào = ra) → apply (COPY, input không đổi) → report

Tri thức SOP nằm ở ``rules/*.toml`` (``[hang_muc]``, ``[[subfolders]]``, ``[catalog]``,
``[vision.hints]``, ``[classify]``); code chỉ là cơ chế.
"""
