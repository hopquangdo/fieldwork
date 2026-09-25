"""Logic thuần — không I/O ngoài, không ``ctx``, không giữ trạng thái.

    station        cấu trúc trạm trên đĩa (image_root, hạng mục)
    metadata       đọc TABLEBia*.txt
    naming         parse tên file ảnh đầu vào
    filename       quy ước tên file phụ lục (conform / content_name / build_name)
    capture_time   suy giờ chụp (tên file / EXIF / mtime)
    matching       rule engine — ảnh → thư mục đích
    diagnostics    phát hiện vi phạm SOP (assign → Issue[])
    folders        thao tác đường dẫn / bảng assign

Suy luận SOP-aware (marker, regex, tên) nằm ở :class:`domain.profile.Names`.
Import module con trực tiếp: ``from domain.metadata import read_meta``.
"""
