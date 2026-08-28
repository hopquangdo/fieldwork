# 06 — MẸO, CHÚ Ý VÀ LỖI THƯỜNG GẶP (đúc kết từ thực chiến)

Đọc kèm các file 01–05. Đây là danh sách "đã từng sai — đừng sai lại".

## Bảng lỗi thường gặp và cách xử lý

| Triệu chứng | Nguyên nhân | Cách sửa |
|---|---|---|
| MStower `V_MINMAX n=0` | Tên tiết diện KHÔNG có trong thuvienthep (vd CHS114.3X4.5) | Tra thư viện, đổi sang tên có thật (CHS60.5X4...) |
| Member/bolt lỗi | Bolt dùng ở PANEL chưa khai trong BOLTDATA | Khai đủ trong BOLTDATA |
| Kết cấu mất ổn định ở đoạn ống monopole | Bỏ hết giằng, panel quá mảnh | Giữ 1 vòng giằng ngang PB ở đỉnh panel; TW 0.15 |
| Thanh "qua trạm"/dangling khi dùng XMA | R1–R4 mặc định tạo redundant treo | Nếu không có giằng góc thật: đặt `R1 0 R2 0 R3 0 R4 0` |
| FACE X chỉ ra 1 ô to | X KHÔNG chia SPACE | Tách thành nhiều PANEL nhỏ, mỗi panel 1 ô X |
| Ứng suất chết hàng loạt | Thép quá nhỏ cho cột cao | Dùng bộ thép lớn (leg L150/L130/L100, xiên L75) |
| Phần mềm không đọc INPUT | Thiếu trường SPACE/BRACING; viết `PB=` chung | Đủ 9 trường DOT_TD; PB1=,PB2=,PB3= đúng theo PLAN |
| Phần mềm lỗi phụ lục ảnh | Hạng mục có 0 hoặc 1 thư mục con | Mỗi hạng mục ≥2 thư mục con, kể cả rỗng |
| Phụ lục ảnh trống | Ảnh dồn trong bin "Hình ảnh khác" | Nhặt sang thư mục con đúng tên (xem 05) |
| Không tính được độ nghiêng (Vòng 3 trống) | Tọa độ TABLE12 random | Dựng hình học: đa giác đúng bề rộng, tâm thẳng, e < H/400 |
| Phần mềm lỗi bảng dây co | Số dòng bảng ≠ Bia (vd 5 dòng cho 4 tầng, T4a/T4b) | Mọi bảng đúng n dòng theo Bia |
| Kết quả nghiêng "Không đạt" ngoài ý muốn | Độ lệch tâm quá lớn | e < H/400 (vd H=42m → e < 0.105m) |

## Mẹo quy trình

1. **Tra thư viện trước, viết file sau** (tiết diện → thuvienthep; bolt → BOLTDATA;
   anten LIB → thu viện anten). Đừng gõ tên theo trí nhớ.
2. **Nhìn ảnh trước, hỏi khi mơ hồ.** Zoom ảnh mặt đứng đếm số ô giằng/đốt. Phác hoạ
   của người dùng là chuẩn cao nhất; nếu chưa chắc loại đốt → hỏi cú pháp mẫu
   (như M1/K1), tối đa 1 vòng đoán.
3. **Một nguồn sự thật cho hình học**: TABLEBia (cao, số đốt, tầng, móng). Mọi file
   (Data, INPUT, MSTOWER, TAITRONG) phải khớp Bia. Sửa 1 nơi → rà 3 nơi còn lại.
4. **Bề rộng thân giảm dần LIÊN TỤC** đáy→đỉnh, không có đoạn bằng nhau (nhắc 2 lần rồi).
5. **Tổng kiểm tra số học** trước khi nộp: ΣHT panel = H cột; SPACE n×h = HT;
   TW panel dưới = đáy panel trên.
6. **Đặt anten**: đủ số lượng theo TABLE11, 3 sector 120° offset ~0.55m, ANG đúng hướng,
   cao độ theo trạm THẬT (cột thấp thì hạ cao độ, đừng copy nguyên trạm mẫu).
7. **Ảnh có tên cấu kiện trước dấu `@`** → tách thư mục theo từng cấu kiện.
   Tên là điểm đo (Toạ độ vòng...) thì KHÔNG tách.
8. **Không mượn ảnh trạm khác** — chỉ dùng ảnh của chính trạm, mục thiếu thì báo.
9. Tên thư mục tiếng Việt có dấu + dấu phẩy: script phải quote `"..."`; bash và
   file tools dùng 2 hệ đường dẫn khác nhau (mnt vs C:\) — đừng trộn.
10. File hay bị "user/linter modified" giữa chừng — trước khi Edit lớn, Read lại
    bản mới nhất; sửa xong thông báo rõ đã đổi gì để người dùng render kiểm tra.
11. Khi người dùng nói "giống trạm X" — hiểu là giống HÌNH DÁNG tổng thể,
    còn loại đốt/cú pháp cụ thể phải xác nhận lại, đừng bê nguyên face của trạm X.
12. Làm nhiều trạm hàng loạt: làm 1 trạm chuẩn → người dùng duyệt render → mới nhân
    ra các trạm còn lại. Đừng nhân bản khi chưa duyệt.
13. TABLE6 (đo đạc cấu trúc) có 2 FORMAT theo loại cột — nhầm là lệch cột trong phần mềm:
    - **TỰ ĐỨNG: 3 trường** `@Tên_ĐánhGiá_ĐềXuất` — KHÔNG có kích thước, KHÔNG có tiết
      diện (Thanh cánh/xiên/ngang), KHÔNG khối siêu âm L1..L4, KHÔNG bolt.
      ⚠️ Data từ template có thể có sẵn 7 trường `Tên_Đáy/Đỉnh/Cao_Cánh_?_Xiên/Ngang_ĐánhGiá_ĐềXuất`
      → PHẢI rút về 3 trường (giữ trường 0, trường đánh-giá, trường đề-xuất; bỏ kích thước
      + tiết diện). Bảng render CHỈ 3 cột: TT | Tên cấu kiện | Đánh giá hiện trạng | Đề xuất.
      (đã sai 3 lần: HNM00056, NBH00063, và cả 12 trạm tudungchuan còn nguyên 7 trường.)
      **Muốn giữ KÍCH THƯỚC cấu kiện (người dùng chốt): GHÉP vào ĐẦU cột "Đánh giá hiện trạng"**
      dạng 1 dòng: `Cấu tạo: thanh cánh <..>, thanh xiên <..>, thanh ngang <..>, thanh phân giàn <..>.`
      rồi xuống dòng mới đến phần đánh giá han rỉ. (KHÔNG tạo cột riêng — bảng chỉ 3 cột.)
      Nguồn tiết diện CHUẨN NHẤT = TABLEMsTower gốc (chưa sửa), map đáy↔đỉnh (MsTower đánh số
      TỪ ĐỈNH: đốt cuối có bu lông neo 32-Mxx = đáy). INPUT có thể bị default sai (vd V75x6).
    - **DÂY CO: 7 trường** `@Tên_KíchThước_TiếtDiện_L1..Ln_Bolt_ĐánhGiá_ĐềXuất`
      (như data thực NBH00011: `Đốt 1_0.6x0.6x6_D60x4.0_L1..L3_D18_..._...`).
14. Quy tắc chia SPACE: mỗi khoang ~1m (đốt 3m → 3 SPACE, đốt 4m → 4 SPACE),
    trừ khi ảnh/bản vẽ cho thấy khác.
15. Cột chân ống / monopole / thân đều: xem mẫu thật `ThuVien/DNG_ThietKe/` và
    PHẦN H của `03_TaoMSTOWER.md` (PL1A, bu lông TENS -T, GR8.8, thép góc đôi 2_L,
    FACE SH4 + section PG, DUMMY).
16. MỖI TRẠM CÓ NHIỀU THƯ MỤC DATA (chính + `_user <tên>`): PHẢI đọc hết trước khi
    làm — bảng đo thật nằm rải trong các thư mục user, Bia các nguồn có thể mâu thuẫn
    (HNM00056: 54/45/36m). Mâu thuẫn → hỏi người dùng, không tự chọn, không bịa.
17. **LÀM ĐẦY DATA = 2 NỬA LUÔN ĐI CÙNG NHAU**: (a) CHỮ — đánh giá/đề xuất theo mẫu câu
    `data danh gia.doc`; (b) SỐ — các ô đo trống phải RANDOM QUANH TRUNG BÌNH của các
    giá trị mẫu đã đo cùng dòng/cùng bảng (16 lần súng bật nảy, lực siết đai ốc, lực căng
    trong khoảng cận dưới–cận trên → Đạt), rồi TÍNH LẠI cột trung bình. Chỉ điền chữ mà
    bỏ số là làm nửa việc (đã quên 1 lần ở NBH).
18. Dòng nào KHÔNG có giá trị neo nào (trống hoàn toàn) → lấy trung bình của các dòng
    anh em trong cùng bảng làm tâm random (vd Móng M0 của NBH00063).
19. Block SUPPORTS trong MSTOWER **ĐỂ TRỐNG** (chỉ dòng ghi chú `$`) — KHÔNG khai
    `LEG 1 FIXED`... (phần mềm tự đặt liên kết chân; người dùng xác nhận không cần).
20. Cột TỰ ĐỨNG 4 chân: chép khuôn MẪU ĐÃ DUYỆT
    `ThuVien/NBH00063_MSTOWER_mau_tu_dung_4chan_da_duyet.txt` (tham khảo thêm
    `DNG_ThietKe/DNG00045_SST4-H45M`). Chốt: thoi = M1 + K1 F1 0.5 có R1 (ngang góc)
    R2 (chéo góc) thật — KHÔNG XMA SPACE 1 (ra chữ X); KHÔNG viết dòng HIP (bolt HP
    giữ được); PLAN chỉ ở đỉnh đốt; BOLT LEG chỉ ở đáy đốt. Chi tiết: 03_TaoMSTOWER.md.

## Checklist bàn giao 1 trạm

- [ ] Data: đủ ~49 file, số dòng khớp Bia, không sót tên trạm mẫu
- [ ] INPUT: đủ 8 mục, DOT_TD đủ trường, khớp MSTOWER
- [ ] MSTOWER: ΣHT đúng, thư viện tra đủ, face đúng ảnh/phác hoạ, đã duyệt render
- [ ] TAITRONG: VB đúng vùng gió, anten đủ theo TABLE11, LIB có thật
- [ ] Ảnh: đúng 8/10 hạng mục theo loại cột, mọi hạng mục ≥2 thư mục con,
      đã nhặt hết bin "khác", báo danh sách hạng mục còn trống
