# DỰ ÁN KIỂM ĐỊNH CỘT BTS — HƯỚNG DẪN TỔNG QUAN

Bộ tài liệu này giúp một đoạn chat MỚI tiếp tục công việc mà không cần đọc lại lịch sử.
Đọc file này trước, sau đó đọc file hướng dẫn của chức năng cần làm.

## ⭐ QUY TẮC VÀNG — ĐỌC TRƯỚC TIÊN (vi phạm là làm lại từ đầu)

1. **MỖI TRẠM CÓ BẢN VẼ TAY RIÊNG** (elevation + mặt cắt từng đốt), thường nằm trong
   "Hình ảnh khác tổng thể cột anten" (có thể mang tên "Móng M0@.."). **PHẢI MỞ ĐỌC bản
   vẽ của CHÍNH trạm để dựng thiết kế TỪNG ĐỐT** (loại face, chiều cao, bề rộng, tiết diện).
2. **TUYỆT ĐỐI KHÔNG auto-sinh thiết kế bằng script/đoán** (vd gán DLM 6m/đốt cho cả loạt).
   Đã sai cả loạt tudungchuan vì làm vậy.
3. **TRƯỚC KHI DỰNG: kiểm tra thư mục `POTECO-Huy/tudung` + `tudung/TramChuan` + `DNG_ThietKe`**
   xem đã có thiết kế đúng của chính trạm chưa — nếu có thì dùng lại/đối chiếu, đừng làm lại.
4. **Bề rộng GIẢM DẦN LIÊN TỤC** chân→đỉnh; tiết diện lấy theo **TABLE6 ĐO ĐẠC**, không đoán.
4b. **⚠️ SỐ GHI TRÊN BẢN VẼ TAY = BỀ RỘNG ĐỈNH CỦA TỪNG ĐỐT** (người dùng nhắc NHIỀU LẦN).
   Không phải chân đốt! Chân đốt n = đỉnh đốt (n−1); **chân cột luôn LỚN HƠN số của đốt 1**
   (vd HNM00112: đỉnh Đ1 = 4.36 → chân cột 5.90; HNM00069: đỉnh Đ1 = 4.35 → chân 6.40;
   HNM00073: đỉnh Đ1 = 3.47 → chân 5.90). Chân cột lấy theo số người dùng chốt / đo thực tế.
5. **Loại cột theo bản vẽ THẬT**, sửa TABLEBia (tự đứng: Loại cột=Tự đứng, móng M1..Mn, KHÔNG M0).
6. Face theo bản vẽ: Eiffel tam giác → K1 (BR2=0); thoi 4 chân → M1+K1/XMA; chân xoè → KMGD/K2;
   X 4 mặt → XDM/XMA; ống đỉnh → CHS leg-only. Xem 03_TaoMSTOWER.md PHẦN C.
7. Ảnh đo theo cấu kiện → mỗi cấu kiện 1 thư mục "Công tác đo.."; anten ANG=90−phương vị (ra ngoài).
8. Bản vẽ có thể nằm ở "Hình ảnh tổng thể mặt bằng trạm BTS" — tìm cả 2 thư mục, thấy thì nhặt
   về "Hình ảnh khác"; KIỂM TRA MÃ TRẠM trên tờ giấy (đề phòng tờ lạc trạm khác, vd 00048 lạc vào 00056).
9. Sau MỌI lần đổi thiết kế: đồng bộ đủ 4 nơi **MSTOWER ↔ INPUT ↔ Bia/GiaiPhap ↔ cao độ ANTEN**
   (anten phải thấp hơn đỉnh cột). Hiện trạng các bảng lấy từ tên thư mục dị tật mục 8 (xem 01).
10. Kết luận/Kiến nghị: cột TỰ ĐỨNG dùng prompt riêng `09_Prompt_KetLuanKienNghi_TuDung.md`
   (cấm nhắc dây co/tăng đơ/ma ní/khóa cáp/móc co).

> Nếu số liệu bản vẽ mâu thuẫn/khó đọc → HỎI người dùng, KHÔNG tự bịa.

## 5 chức năng chính

| # | Chức năng | File hướng dẫn |
|---|---|---|
| 1 | Tạo Data mẫu (TABLE2–TABLE12 + file phụ) | `01_TaoDataMau.md` |
| 2 | Tạo file INPUT (đầu vào phần mềm, DOT_TD) | `02_TaoINPUT.md` |
| 3 | Tạo đầu vào MSTOWER (.td) | `03_TaoMSTOWER.md` |
| 4 | Tạo TAITRONG (tải trọng + anten) | `04_TaoTAITRONG.md` |
| 5 | Sắp xếp/nhặt hình ảnh phụ lục | `05_SapXepAnh.md` |
| — | Mẹo, chú ý, bảng lỗi thường gặp + checklist | `06_MeoVaLoi.md` (ĐỌC TRƯỚC KHI LÀM BẤT KỲ VIỆC GÌ) |
| 6 | Viết kết luận & kiến nghị (corpus + quy tắc logic loại cột × vị trí) | `07_KetLuanKienNghi.md` |

## Cấu trúc thư mục 1 trạm (ví dụ HNM00147_Bình Sơn,Ninh Bình)

```
HNM00147_Bình Sơn,Ninh Bình/
├── DataHNM00147_Bình Sơn,Ninh Bình/            <- Data chính (TABLE*.txt)
├── DataHNM00147_..._user Tâm/                  <- Data theo user (thường chứa TABLEBia.txt)
├── HNM00147_Bình Sơn,Ninh Bình/                <- PHỤ LỤC ẢNH (thư mục 1..8 hoặc 1..10)
├── HNM00147_MSTOWER.txt                        <- đầu vào MStower (.td)
├── HNM00147_INPUT.txt                          <- đầu vào phần mềm nội bộ
└── HNM00147_TAITRONG.txt                       <- tải trọng MStower
```

## Thư viện tra cứu (đã copy sẵn vào `ThuVien/` trong thư mục này)

- `ThuVien/thuvienthep.txt` — thư viện tiết diện thép L:JIS. TRA TRƯỚC khi dùng bất kỳ tên tiết diện nào.
- `ThuVien/thu vien anten.txt` — thư viện anten (LIB MS_ANC). Tra trước khi khai anten trong TAITRONG.
- `ThuVien/taitrong mau cot tu dung.txt` — TAITRONG mẫu.
- `ThuVien/thiet ke mau cot tu dung.txt` — thiết kế mẫu cột tự đứng.
- `ThuVien/NDH00002_INPUT_mau.txt` — INPUT mẫu (bản cũ).
- `ThuVien/HNM00112_INPUT_mau_tu_dung.txt` — **INPUT mẫu CHUẨN NHẤT** (tự đứng 4 chân,
  có đốt ghép M1K1, đầy đủ khung 8 mục + chú thích) — bám file này khi tạo INPUT mới.
- `ThuVien/DNG_ThietKe/` — 16 file MSTOWER thật từ các trạm DNG (đã đổi .td → .txt).
  Mã: SST4-HxxM-WByyM = tự đứng 4 chân cao xx, đáy yy; MNP = monopole. Đặc biệt:
  mẫu chân ỐNG TRÒN CHS (CHS230/280 + xiên thép góc đôi 2_L90X90X9) và mẫu monopole
  MNP-H40M — hai kiểu không có trong bộ HNM/NDH. LƯU Ý: .td các file này KHÔNG chứa
  tải trọng (LOADS nằm trong .mst/.arc nhị phân, mở bằng MStower); tải trọng dựng lại
  từ TABLE11 của trạm theo `04_TaoTAITRONG.md`.

## Vị trí dữ liệu dự án (thư mục làm việc KD2026)

- `KD2026/NBI/POTECO/Tram co data/` — các trạm có data.
- `KD2026/NBI/POTECO/Tram linh tinh/` — trạm lẻ, thiếu data.
- `KD2026/NBI/PCC/` — trạm mẫu NDH.

## Trạm MẪU chuẩn (đã chạy đúng phần mềm — luôn lấy làm khuôn)

| Loại | Trạm mẫu | Ghi chú |
|---|---|---|
| Tự đứng 4 chân | `PCC/NDH00002_Giao Ninh,Ninh Bình` | MSTOWER + INPUT + TAITRONG + Data đầy đủ |
| Tự đứng 3 chân | `PCC/NDH00234_2` | TAITRONG mẫu |
| Dây co | `PCC/NDH00289_2` | Data dây co đầy đủ |
| Dây co 21m trên mái | `POTECO/Tram co data/HNM00070_Thanh Bình` | 0.3×0.3, 7 đốt×3m, 4 chân — mẫu cho trạm dây co nhỏ |

## Phân biệt loại cột (đọc TABLEBia.txt: trường "Loại cột")

- **Dây co**: có tầng dây co, móng co, phụ kiện dây co (tăng đơ, ma ní, khóa cáp, móc co, vòng ốp). Phụ lục ảnh 10 hạng mục.
- **Tự đứng**: không dây co. Phụ lục ảnh 8 hạng mục. LƯU Ý: một số trạm Bia ghi sai
  "Dây co" nhưng thực tế tự đứng — PHẢI mở ảnh mặt đứng kiểm tra.

## Nguyên tắc chung (rút từ kinh nghiệm đã trả giá)

1. **Luôn đối chiếu ảnh chụp/phác hoạ trước khi dựng kết cấu.** Không đoán mò nhiều vòng —
   nếu không chắc cấu tạo đốt, HỎI người dùng cú pháp/loại đốt (1 câu hỏi tiết kiệm 5 vòng sửa).
2. **Fake data phải nhất quán nội bộ**: số dòng các bảng khớp Bia (số tầng, số đốt, số móng);
   TABLE8_Duoi = TABLE8_Tren (dây co); không đưa cấu kiện không tồn tại vào (xem 01).
3. **KHÔNG lấy ảnh trạm khác** chèn vào phụ lục trạm này (kể cả cắt tọa độ GPS) — đã từ chối
   nhiều lần, chỉ sắp xếp ảnh CỦA CHÍNH trạm đó.
4. Tên file/thư mục có dấu tiếng Việt + dấu phẩy — khi viết script bash/python phải quote cẩn thận.
5. Sau khi sửa MSTOWER phải đồng bộ INPUT (và ngược lại).
