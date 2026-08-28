# 02 — TẠO FILE INPUT (ĐẦU VÀO PHẦN MỀM, DẠNG DOT_TD)

Mục tiêu: file `<Ma>_INPUT.txt` để phần mềm nội bộ đọc.
**MẪU CHUẨN ĐÃ DUYỆT: `ThuVien/HNM00112_INPUT_mau_tu_dung.txt`** (cột tự đứng 4 chân,
có đốt ghép M1K1) — khi tạo file mới hãy MỞ MẪU NÀY và bám đúng từng dòng khung.

## Quy tắc khung file (theo mẫu chuẩn)

1. Mở đầu/kết thúc file bằng dòng `==================================================`,
   cuối file có `END` giữa 2 dòng đó.
2. GIỮ NGUYÊN các dòng chú thích `$ ...` mô tả cột của từng bảng (phần mềm/người đọc
   dựa vào đó) — kể cả bảng trống.
3. Đủ 8 mục `$$$ 1..8`. **Cột tự đứng vẫn giữ khung mục 4 (dây co) và mục 7 (cạnh/góc)**
   với giá trị `X` — KHÔNG xoá mục.

## Mục 1 — THONG TIN CHUNG
TEN_DU_AN, DIA_DIEM, LOAI_HE_THONG (TU_DUNG/DAY_CO), TIET_DIEN_COT (bề rộng đỉnh),
RONG_DINH, CHIEU_CAO_COT, VUNG_GIO IV, DANG_DIA_HINH, CAO_DO_CHAN_COT,
CHIEU_CAO_NHA_TRAM, VI_TRI_DAT (Duoi/Tren mai), MAC_BE_TONG, SO_MONG, SO_CHAN_COT,
SO_DOT, CHIEU_CAO_DOT X, SO_TANG_DAY X, TANG_CO_GCX X (X khi tự đứng/không áp dụng).

## Mục 2 — MONG
- **M0 = móng chân cột; M1, M2… = móng neo (dây co).**
- Cột TỰ ĐỨNG: thường chỉ cần 1 dòng `MONG_KICHTHUOC  M0  B  H  Cao  L0`.
- Cột DÂY CO: thêm bảng tọa độ móng neo (MONG_DAY_CO) + kích thước M1..Mn.

## Mục 3 — BANG DOT (DOT_TD) — 1 dòng = 1 ĐỐT thực tế, đốt 1 dưới cùng

```
DOT_TD 2  CAO_DO 6   B_CHAN 6.05   MAT_CAT PL2A   THAN M1K1   SPACE 2   BOLT M24
  LEGS V150x10   BRACING V60x5
  SECTIONS M1:LEG=V150x10,BR1=V60x5,H1=V100x10;K1:LEG=V150x10,BR1=V60x5,H1=V100x10
```
(viết trên 1 dòng; xuống dòng ở đây chỉ để dễ đọc)

- `CAO_DO` = chiều cao đốt. `B_CHAN` = bề rộng CHÂN đốt — giảm dần liên tục.
- `MAT_CAT`: PLX / PL3S / PL2A / PLD.
- `THAN`: loại thân theo danh mục phần mềm — **cho phép TỪ KHOÁ GHÉP khi 1 đốt cấu tạo
  từ 2 loại panel**: ví dụ `M1K1` (= M1 nửa dưới + K1 nửa trên, đốt hình thoi).
  Các loại: K1, M1, M1K1, K2, KMG/KMGD, XMA, XDM, M, DLM...
  (MSTOWER tách 2 panel M1 + K1 riêng, còn INPUT gộp 1 dòng THAN M1K1 — khác biệt
  là do INPUT tính theo ĐỐT còn MSTOWER tính theo PANEL.)
- `SPACE`: số khoang giằng của đốt (đốt M1K1 → SPACE 2 vì gồm 2 nửa).
- `SECTIONS`: liệt kê tiết diện theo TỪNG PANEL trong đốt, phân tách `;`:
  `M1:LEG=..,BR1=..,H1=..;K1:LEG=..,BR1=..,H1=..` — đốt ghép phải khai đủ CẢ 2 panel.
  Panel PLAN khai thêm `PL2A:PB1=..,PB2=..,PB3=..(,PB4=..)`; PLX dùng PB1,PB3,PB4.
  **Không viết `PB=` chung.**
- Thép ký hiệu V150x10, V130x10, V100x10, V75x8, V75x5, V60x5, V50x5 (V = thép góc L).

## Mục 4 — DAY CO
Tự đứng: `TIET_DIEN_DAY_CO X`, `LOAI_KHOA_CAP X`,
`GA_CHONG_XOAY LOAI X SR X TIET_DIEN1 X TIET_DIEN2 X` (giữ khung, giá trị X).
Dây co: khai các tầng co (CAO_DO, LOAI_CAP, GA, LUC_CANG).

## Mục 5 — ANTEN
Theo ĐÚNG THỨ TỰ GIÁ TRỊ của file mẫu đã chạy (chú ý: thứ tự giá trị thực tế
trong mẫu là kích thước → khối lượng → tên loại):
```
ANTEN 1  CAO_DO 39.0   LOAI 2580x262x116   KICH_THUOC 25.3   TRONG_LUONG 2G_900   SO_LUONG 3
```
Lấy dữ liệu từ TABLE11/ảnh thiết bị; viba ghi `600x600` + `-` + `Viba_D600`.

## Mục 6 — VAT LIEU
`BULONG  M20   GR6.6   D 16   FY 360   FU 600` (1 dòng theo mẫu).

## Mục 7 — CANH/KHOANG CACH
Tự đứng: chỉ giữ 2 khối chú thích bảng (trống). Dây co: điền bảng cạnh–góc, cạnh–cạnh.

## Mục 8 — PHU/CHI TIET
`NOI_DAY_CO X` / `MONG_NOI_CHUNG M1` / `PHUONG_THUC_NOI Bu` (theo mẫu; dây co điền thật).

## Đồng bộ với MSTOWER

INPUT và MSTOWER phải khớp: số đốt, B_CHAN ↔ TW, loại thân ↔ face (M1K1 ↔ cặp panel
M1+K1), SPACE, tiết diện từng thanh. Sửa 1 file → sửa file kia ngay.

## CẬP NHẬT 24-25/08/2026 — QUY TẮC INPUT CHO LOẠT TRẠM DỰNG THEO BẢN VẼ TAY

Từ khóa THAN mở rộng (đã dùng, tool cần hiểu):
- `THAN KM  SPACE n` — đốt gồm n panel K/M xen kẽ (2 panel = 1 cặp K+M, M dưới K trên, R1=0).
  SPACE luôn = SỐ PANEL, không phải số cặp (00040 chốt SPACE 4 = 2 cặp).
- `THAN K1K1 SPACE 2` — đốt 2 lần K1 (BR2=0) chồng nhau (00046 D2-D3).
- `THAN KMX` — đốt hỗn hợp: cặp K+M dưới + khoang X trên (chỉ khi bản vẽ thể hiện, vd 00046 cũ).
- `THAN M1K1` — thoi lớn M1 dưới + K1 (F1=0.5) trên (00040/00069 giữa).
- `THAN X SPACE n` — n khoang X đơn (nét ✕ mỗi khoang trên bản vẽ, vd 00001 12 đốt).
- `THAN DMH SPACE n` / `THAN K2 SPACE n` / `THAN ONG` như cũ.

Các trường bắt buộc đồng bộ với MSTOWER sau MỖI lần chỉnh thiết kế:
1. `TIET_DIEN_COT` = bề rộng CHÂN cột; `RONG_DINH` = bề rộng đỉnh; `CHIEU_CAO_COT`, `SO_DOT`
   (SO_DOT đếm CẢ đốt ống monopole nếu có — 00010 = 14, 00056 = 10).
2. `B_CHAN` từng DOT_TD = bề rộng CHÂN đốt; chuỗi B_CHAN phải khớp mốc bản vẽ + user chỉnh tay
   (vd 00040: user đổi eo Đ2/đỉnh Đ3 → B_CHAN Đ4 đổi theo 1.89→1.70).
3. `MONG_KICHTHUOC M0` duy nhất (không M1..Mn) — format tool CAD.
4. Đốt có VAI/bậc thụt: KHÔNG tách DOT_TD riêng — ghi trong comment ngay trên bảng
   ("D8 = VAI X 0.3m + DMH ... deu"), B_CHAN đốt đó = bề rộng SAU bậc (0.60).
5. HIP ghi trong SECTIONS của DOT_TD: `HIP:HD,ND=2,HP1=...,HP3=0,HP5=0` (K2) / `ND=1,HP3=0` (K1/M1)
   hoặc `HIP:HK,NTR=...` (kiểu 00010/00046).
6. Tiết diện trong SECTIONS ghi theo tên bản vẽ (V90x8, D114...) kèm ghi chú quy đổi thư viện
   ở dòng "$ Ghi chu" cuối bảng (vd V63x5 -> L65x5, V48x5 -> L50x5, D80 -> CHS76.3X4).
7. **RÀ CAO ĐỘ ANTEN sau khi đổi CHIEU_CAO_COT**: mọi ANTEN CAO_DO phải < H (trừ kim thu sét).
   Vượt thì hạ cả cụm giữ nguyên thứ tự tương đối (00001 39.0→34.9...; 00073 42→41.5; 00111 42/40.5/40→39.5/39.2/38.8).
8. Cột 3 chân: MAT_CAT PT2; 4 chân: PL1A; PTT chỉ khi bản vẽ lưới tam giác đặc (00046 Đ1-Đ2 — đang chờ test zero pivot).

## ĐỐT ỐNG MONOPOLE: KHÔNG KHAI TRONG INPUT (người dùng chốt 25/08/2026)

INPUT của tool CAD **chỉ mô tả phần THÂN GIÀN (lattice)**:
- `SO_DOT` = số đốt giàn, KHÔNG cộng đốt ống (sửa lại quy tắc cũ "đếm cả đốt ống" — đã sai).
- `CHIEU_CAO_COT` = chiều cao phần giàn; `RONG_DINH` = bề rộng đỉnh giàn.
- KHÔNG có dòng `DOT_TD ... THAN ONG ... LEGS D114`.
Ống tip chỉ tồn tại trong MSTOWER (panel KXM leg-only, tiết diện quy đổi) và trong hồ sơ/Bia.
Đã áp: HNM00085 (14 đốt/30m), HNM00010 (13 đốt/30.2m), HNM00056 (9 đốt/35m).


## ⚠️ BẮT BUỘC: INPUT PHẢI ĐÚNG KHUNG MẪU `ThuVien/HNM00112_INPUT_mau_tu_dung.txt`

Phần mềm đọc file theo VỊ TRÍ dòng/trường, không tự bỏ qua dòng lạ. Sai khung → "không đọc được".
Đã bị lỗi thật 25/08 vì tự thêm/sửa. Quy tắc chốt:

1. **KHÔNG thêm dòng nào ngoài mẫu** — đặc biệt KHÔNG có `CHIEU_CAO_MODUL`, `BAN_KINH_CO`,
   `NOI_DAY_CO` ngoài vị trí mẫu. Giữ nguyên toàn bộ dòng chú thích `$`/`$$$` của mẫu.
2. **ANTEN ghi theo ĐÚNG THỨ TỰ CỦA MẪU** (nhãn lệch nhưng phần mềm đọc theo vị trí):
   `ANTEN n  CAO_DO <cao>   LOAI <KÍCH THƯỚC>   KICH_THUOC <KHỐI LƯỢNG kg>   TRONG_LUONG <TÊN LOẠI>   SO_LUONG <n>`
   → ví dụ mẫu: `LOAI 2580x262x116   KICH_THUOC 25.3   TRONG_LUONG 2G_900`.
   Tên loại KHÔNG được có dấu cách (dùng `_`: `DUAL_BAND`, `2G_900`, `Viba_D600`).
3. `PHUONG_THUC_NOI  Bu` (đúng như mẫu), `NOI_DAY_CO X`, `MONG_NOI_CHUNG M1`.
4. Cột tự đứng: mục 4 (dây co) vẫn giữ đủ 3 dòng `TIET_DIEN_DAY_CO X`, `LOAI_KHOA_CAP X`,
   `GA_CHONG_XOAY LOAI X ...`; mục 7 chỉ có dòng chú thích, KHÔNG có `BAN_KINH_CO`.
5. `SO_DOT` = số dòng `DOT_TD` (không đếm đốt ống monopole — ống chỉ có trong MSTOWER).
6. Kết thúc file: `==================================================` / `END` / `==================================================`.

Đã sinh lại đúng khung cho 15 trạm (12 tudungchuan + 3 PCC/tudung) ngày 25/08/2026.
