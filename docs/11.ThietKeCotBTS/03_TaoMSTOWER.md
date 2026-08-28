# 03 — TẠO ĐẦU VÀO MSTOWER (.td / .ms) — GIÁO TRÌNH TỪ SỐ 0

Dành cho người/chat CHƯA BIẾT GÌ. Đọc tuần tự. Mẫu chuẩn cuối file là HNM00112
(bản người dùng đã duyệt) — cột ghép 3 kiểu đốt: KMGD + (M1+K1) + XDM.

---

## PHẦN A — KHÁI NIỆM CƠ BẢN

- **Cột** = chồng các **đốt** (segment thực tế, nối nhau bằng mặt bích + bu lông).
- Trong MStower, mỗi đốt được mô hình bằng 1 hoặc NHIỀU **PANEL**.
- **PANEL** khai báo trong PROFILE, **đánh số từ TRÊN xuống**: panel số lớn nhất = đỉnh,
  PANEL 1 = đáy. Trong file viết panel đỉnh trước.
- **HT** = chiều cao panel (m). **TW** = bề rộng cột tại ĐỈNH panel (m).
  Bề rộng tại đáy panel = TW của panel NẰM DƯỚI nó (panel dưới cùng lấy **WBASE**).
- **FACE** = kiểu giằng của mặt cột trong panel đó (chọn từ thư viện đốt MStower).
- **SPACE n @ h** = chia panel thành n khoang giằng, mỗi khoang cao h (n×h PHẢI = HT).
- **PLAN** = giằng mặt bằng (nằm ngang) tại đỉnh panel.
- **FACES 3|4** = cột 3 chân (mặt tam giác) hay 4 chân (mặt vuông).

## PHẦN B — QUY TRÌNH 7 BƯỚC (phương pháp chuẩn của người dùng)

### Bước 1. Nhìn ảnh/bản vẽ TỪNG ĐỐT một
Zoom ảnh mặt đứng, đi từ chân lên đỉnh, với mỗi đốt trả lời:
- Hình giằng gì? (X đơn, X nhiều tầng, hình thoi, chữ K, đáy xòe kiểu Eiffel…)
- Có thanh ngang trên/dưới/giữa không? Có giằng góc/giằng vai không?
- Đốt cao bao nhiêu, bề rộng chân/đỉnh đốt bao nhiêu (ước từ tỉ lệ ảnh hoặc bản vẽ)?

### Bước 2. So với THƯ VIỆN ĐỐT MStower, chọn loại SÁT NHẤT
(bảng nhận diện ở PHẦN C). Không có loại nào khớp 100% → chọn gần nhất,
hoặc sang Bước 3.

### Bước 3. Đốt phức tạp = GHÉP 2 LOẠI FACE
Ví dụ chuẩn: đốt hình thoi lớn KHÔNG có sẵn trong thư viện dạng 1 panel
→ ghép 2 panel: **M1 (nửa dưới thoi, chữ V mở ngửa ⋀⋀) + K1 (nửa trên thoi, úp xuống)**.
Cách chia: đốt cao h, đáy Wb, đỉnh Wt → PANEL M1 (HT=h/2, TW=(Wb+Wt)/2 tại eo thoi)
rồi PANEL K1 (HT=h/2, TW=Wt). Nguyên tắc chung: bất kỳ đốt nào không có face đơn
tương ứng đều có thể ghép từ 2+ panel các face đơn giản hơn.

### Bước 4. Đặt chiều cao và SPACE
- HT mỗi panel theo chiều cao đốt thực (hoặc nửa đốt nếu ghép M1/K1).
- Đếm số KHOANG GIẰNG trong ảnh → SPACE. Kiểm tra n×h = HT.
- FACE X KHÔNG chia SPACE được (1 khoang/panel) — muốn nhiều khoang X phải tách panel.
- Tổng HT toàn bộ panel = chiều cao cột trong Bia.
- **Bề rộng TW giảm dần LIÊN TỤC từ đáy lên đỉnh** — không có đoạn nào bằng nhau.

### Bước 5. GÁN TIẾT DIỆN từng thanh (phần hay bị làm ẩu — đọc kỹ PHẦN D)

### Bước 6. BOLT từng panel
`BOLT LEG n M..-1 BR1 n M..-1 H1 n M..-1 ...` — số bu lông + tên bolt cho mỗi loại thanh.
Mọi tên bolt phải khai trong BOLTDATA. Thường: neo chân M24; nối đốt to M22/M24;
giằng lớn M20/M22; giằng nhỏ M14/M16.

### Bước 7. Kiểm tra số học + render
ΣHT = H cột; SPACE×@ = HT; TW liên tục; tên tiết diện có trong thuvienthep;
bolt có trong BOLTDATA. Xuất render cho NGƯỜI DÙNG DUYỆT trước khi nhân ra trạm khác.

## PHẦN C — THƯ VIỆN ĐỐT: NHẬN DIỆN + THANH CỦA TỪNG FACE

Mỗi FACE có bộ thanh RIÊNG phải gán tiết diện (số sau tên thanh = số thứ tự SECTION).

| Face | Nhận diện trong ảnh | Thanh phải gán | Ghi chú |
|---|---|---|---|
| **M1** | nửa DƯỚI hình thoi: 2 xiên chụm lên đỉnh giữa (⋀⋀) | LEG, BR1, H1 | ghép với K1 thành 1 thoi |
| **K1** | nửa TRÊN hình thoi / khung K úp: xiên từ giữa toả xuống 2 chân + ngang đỉnh | LEG, BR1, H1 | |
| **XDM** | X nhiều tầng + ngang trên và dưới mỗi khoang | LEG, BR1, BR2, H1, H2 | chia SPACE được |
| **XMA** | 1 hình thoi/khoang 4 mặt | LEG, BR1, BR2, H1, H2, R1–R4 | không có giằng góc thật → R1..R4 = 0 |
| **KMGD** | đáy xòe Eiffel: K + giằng phụ chia bậc | LEG, BR1, H1, R1..R2n (theo ND), + HIP HP1.. | cần `ND 1..3`, `HIP HK NTR n`; càng rộng ND càng lớn, R càng nhiều |
| **K2** | chữ K có giằng vai (3 chân, đốt đáy) | LEG, BR1, H1, R1, R2 | |
| **KXM** | K+X+M giằng dày (3 chân) | LEG, BR1, H1, H2 | chia SPACE được |
| **X** | 1 chữ X to duy nhất | LEG, BR1, H1 | KHÔNG SPACE |
| **DMH/DMH2** | double-warren + ngang, R1/R2 xen kẽ | LEG, BR1, BR2, H1, H2 (R xen kẽ) | S1..Sn, n≤40 |

PLAN (giằng mặt bằng): 4 mặt dùng PL2A (PB1..PB3/PB4) hoặc PLX (PB1,PB3,PB4)
hoặc PL3S (PB1..PB5); 3 mặt dùng PT2 (PB1..PB3). Chỉ KMGD mới có HIP.

## CỘT LATTICE TỰ ĐỨNG KIỂU EIFFEL (tam giác 3 chân) — FACE K1, BR2=0 (bài học HNM00085)

- Mỗi đốt cột Eiffel (bản vẽ có xiên chevron/chữ V + ngang) = **FACE K1 với BR2 = 0**:
  `FACE K1 LEG a BR1 b BR2 0 H1 d R1 e R2 f` (1 xiên BR1 + ngang H1 + 2 giằng góc R1/R2).
  KHÔNG dùng KXM/K2/DLM cho các đốt này.
- **Bề rộng GIẢM DẦN LIÊN TỤC** chân→đỉnh — không để các đốt trên TW thẳng tuột 1.0m
  (người dùng bắt lỗi 2 lần: "bề rộng giảm dần chứ có thẳng tuột đâu").
- Tiết diện theo TABLE6 ĐO ĐẠC (đừng đoán): cánh thường **thép góc ĐÔI** (2V120x12/2V130x11
  → 2_L..); xiên+ngang cùng cỡ (V75x6→L75X75X6); giằng góc R nhỏ (V50x5). Đỉnh ống monopole
  = PANEL leg-only (FACE KXM SPACE 1 LEG=CHS.., BR1 0 H1 0).
- **LUÔN kiểm tra thư mục cũ `POTECO-Huy/tudung` + `tudung/TramChuan` xem đã có thiết kế
  đúng của CHÍNH trạm chưa TRƯỚC KHI tự dựng.** Đừng auto-sinh DLM (đã sai cả loạt tudungchuan).

## ĐỐT HÌNH THOI CÓ THANH CHỐNG GÓC + HIP — làm theo khuôn thiết kế THẬT (bài học NBH00063)

MẪU CHUẨN: `ThuVien/DNG_ThietKe/DNG00045_SST4-H45M-WB5.0M.txt` (cột 4 chân thép góc).
Đây là cách designer thật mô hình — LUÔN mở file này xem trước khi dựng cột tự đứng 4 chân.

- Đốt thoi = CẶP panel: **M1 (nửa dưới) + K1 F1 0.5 (nửa trên)** — CẢ HAI đều nhận
  `R1 x R2 x` = thanh chống góc (R1 = thanh NGANG góc, R2 = thanh CHÉO góc; gán tiết diện
  riêng từng thanh theo bản vẽ, có thể khác nhau giữa M1 và K1). VD đã duyệt (NBH00063):
  `FACE K1 F1 0.5 LEG 1 BR1 4 H1 4 R1 6 R2 8` / `FACE M1 LEG 1 BR1 4 H1 4 R1 5 R2 6`.
  (Kho DNG dùng K1U F1 0.5 — bản duyệt cuối của người dùng dùng K1 F1 0.5.)
- **KHÔNG dùng XMA SPACE 1 cho đốt thoi** — XMA vẽ ra chữ X, không phải hình thoi
  (đã sai và bị bắt lỗi ở render NBH00063).
- **HIP (giằng hông)**: kho DNG có dùng (chỉ với M1/K1U/KMGD, NTR ≤ 3), nhưng
  **bản duyệt cuối NBH00063 của người dùng BỎ HẲN dòng HIP** — render đúng, chạy sạch.
  → Mặc định KHÔNG viết dòng HIP; bolt HP1/HP2 trong dòng BOLT giữ lại không sao.
  Tuyệt đối không gắn HIP vào K2/XMA/X/KXM — MStower báo
  `No. levels of hip bracing incompatible with face` (đã dính ở NBH00063 Đ1 K2 NTR 5).
  Gặp lỗi cú pháp face → grep kho `ThuVien/DNG_ThietKe/` xem tổ hợp có thật, đừng suy diễn.
- **MẪU ĐÃ DUYỆT HOÀN CHỈNH**: `ThuVien/NBH00063_MSTOWER_mau_tu_dung_4chan_da_duyet.txt`
  (cột tự đứng 4 chân 50m: D1 K2 SPACE 5; D2–D5 thoi M1+K1 F1 0.5 có R1 R2;
  D6–D9 XMA; không HIP; không LEG FIXED). Cột tự đứng 4 chân mới → chép khuôn này.
- K2 SPACE 5 có thể chỉ hiển thị 3 khoang gạch chéo trong render — người dùng đã
  chấp nhận bản render cuối, không tự "sửa" lại điều này.
- **PLAN chỉ đặt ở panel ĐỈNH mỗi đốt** (vòng giằng mặt bằng tại mối nối);
  **BOLT LEG chỉ ở panel ĐÁY đốt** (mối nối đốt). Không rải PLAN mọi panel.
- Thân lưới trên cùng của thiết kế thật: chuỗi panel M/K xen kẽ mỗi khoang ~0.6m
  (không bắt buộc; XMA nhiều khoang với R=0 cũng được người dùng chấp nhận).
- **Đốt ĐÁY xoè chân kiểu "chữ M + nấc thang" → face KMPA** (bài học NBH00063 Đ1):
  dấu hiệu trên bản vẽ = 1 xiên chính RẤT DÀI mỗi bên (BR1, dài ≈ đường chéo đốt),
  thanh ngang giữa H2 nơi 2 xiên gặp, đỉnh chữ M (BR2/BR3) đỡ ngang đỉnh H1, và các
  NẤC THANG ngắn dần xuống chân giữa cánh và BR1 (số nấc = ND, đây KHÔNG phải "space").
  Cú pháp: `FACE KMPA ND 4 F1 0.75 LEG a BR1 b BR2 c BR3 c H1 d H2 e R1..R4 ...`
  (F1 = tỷ lệ cao độ H2 / chiều cao đốt). Đừng nhầm sang K2 — K2 là chữ K lặp
  theo khoang, không có nấc thang (đã nhầm ở NBH00063, render sai).
- SPACE luôn = HT ÷ số khoang, TÍNH LẠI mỗi khi đổi chiều cao đốt (đốt 10.1m 5 khoang
  → @ 2.020; KHÔNG giữ số @ cũ khi HT đã đổi).
- Người dùng gửi danh sách chiều cao đốt nhưng THIẾU một vài đốt → hỏi đủ n số một
  dòng, không tự gán số vào đốt (đã đoán sai vị trí số 7.1 hai lần).

## PHẦN D — GÁN TIẾT DIỆN: NGUYÊN TẮC

1. Khai SECTIONS trước (đánh số 1,2,3…), MỖI TÊN PHẢI TRA `ThuVien/thuvienthep.txt`.
2. Trong dòng FACE, sau mỗi tên thanh là SỐ SECTION: `FACE M1 LEG 1 BR1 6 H1 3`
   nghĩa là: thanh cánh dùng section 1, xiên BR1 dùng section 6, ngang H1 dùng section 3.
3. Nguyên tắc chọn:
   - **LEG (thanh cánh)**: to nhất, giảm dần theo chiều cao. Cột 42m điển hình:
     L150X150X10 (đáy) → L130X10 (giữa) → L100X100X10 (trên).
   - **BR (xiên)**: theo chiều dài thanh — xiên đốt rộng/dài dùng L75X75X8,
     đốt hẹp dùng L75X75X5 hay L60X60X5.
   - **H (ngang)**: nhỏ hơn hoặc bằng xiên (L75X75X5 / L50X50X5).
   - **R (giằng vai/phụ), HIP**: L60X60X5.
   - **PB (mặt bằng)**: nhỏ nhất, L50X50X5.
   - Cùng 1 số section dùng được cho nhiều loại thanh ở nhiều panel (ghi chú rõ ở SECTIONS).
4. Ống tròn (monopole đỉnh): CHS60.5X4… — KHÔNG viết CONNECT cho ống.
5. Thép góc: thêm `CONNECT L BH 44`.

## PHẦN E — TRA CỨU THƯ VIỆN (LÀM TRƯỚC KHI VIẾT FILE)

1. Tiết diện → `ThuVien/thuvienthep.txt` (L:JIS). Sai tên → lỗi `V_MINMAX n=0`.
2. Bolt → phải định nghĩa trong BOLTDATA của chính file (D, AS, FY, FU, NSP).
3. Anten LIB (file TAITRONG) → `ThuVien/thu vien anten.txt` (L:MS_ANC).
4. Tên hợp lệ hay dùng: L150X150X10, L130X10, L100X100X10, L75X75X8, L75X75X5,
   L65x6, L60X60X5, L50X50X5, L50x4, CHS60.5X4, CHS76.3X4, CHS89X5, CHS114X4.5.
   (CHS114.3X4.5 KHÔNG tồn tại.)

## PHẦN F — VÍ DỤ HOÀN CHỈNH ĐÃ DUYỆT: HNM00112 (42m, 4 chân, 3 kiểu đốt)

Cột thực tế: đáy xòe Eiffel → 2 đốt hình thoi lớn → thân trên mảnh X dày.
Cách mô hình: đốt 1 = KMGD; đốt 2–3 = mỗi đốt (M1 + K1); đốt 4–7 = XDM SPACE 4.
Bề rộng: 7.50 → 6.05 → 5.05 → 4.20 → 3.40 → 2.70 → 2.00 → 1.18 → 0.78 → 0.70 (giảm liên tục).
File chuẩn đầy đủ: xem `KD2026/NBI/POTECO/Tram co data/HNM00112_Lý Nhân,Ninh Bình/HNM00112_MSTOWER.txt`.
Trích phần PROFILE đặc trưng:

```
PANEL 9  HT 6.00 TW 0.70                        $ dinh - than manh
  FACE XDM SPACE 4 @ 1.500 LEG 3 BR1 5 BR2 5 H1 5 H2 5
  PLAN PL2A PB1 7 PB2 7 PB3 7 PB4 7 TOP
  BOLT LEG 4 M20-1 BR1 1 M20-1 H1 1 M20-1
...
PANEL 5  HT 3.000  TW 2.7000    $ K1 (nua tren thoi dot 3)
  FACE K1 LEG 1 BR1 6 H1 3
  BOLT LEG 2 M24-1 BR1 2 M22-1 H1 2 M22-1
PANEL 4  HT 3.000  TW 3.4000    $ M1 (nua duoi thoi dot 3)
  FACE M1 LEG 1 BR1 6 H1 3
  BOLT LEG 2 M24-1 BR1 2 M22-1 H1 2 M22-1
...
PANEL 1  HT 6.00 TW 6.0500                      $ day xoe
  FACE KMGD ND 3 LEG 1 BR1 3 H1 5 R1 6 R2 6 R3 6 R4 6 R5 6 R6 6
  PLAN PL2A PB1 7 PB2 7 PB3 7 TOP
  HIP HK NTR 3 HP1 6 HP2 6
  BOLT LEG 10 M24-1 BR1 2 M20-1 H1 2 M20-1 R1 2 M20-1 R2 2 M20-1
```

## PHẦN H — KỸ THUẬT HỌC TỪ THIẾT KẾ THẬT DNG (ThuVien/DNG_ThietKe/)

Đúc kết từ 16 file .td chuyên nghiệp của bộ DNG — nhiều kỹ thuật KHÔNG có trong bộ HNM/NDH:

### H1. Cột thân ĐỀU giằng X (SST4-H42M-WB2.5M — mẫu chân ống)
1. **Đánh số panel theo <đốt><khoang>**: PANEL 63 = đốt 6 khoang 3, PANEL 11 = đốt 1
   khoang 1. FACE X không chia SPACE nên MỖI KHOANG = 1 PANEL riêng — đây là cách
   chuyên nghiệp xử lý X nhiều khoang (xác nhận quy tắc ở PHẦN C).
2. **Thân đều**: WBASE = TW = 2.5 ở mọi panel (cột lăng trụ thẳng — kiểu thân cột dây co).
3. **PLAN PL1A** (loại PLAN mới) và chỉ khai Ở KHOANG ĐỈNH MỖI ĐỐT (`PB1 0 PB2 4 PB3 0`),
   các khoang giữa KHÔNG có dòng PLAN — giằng mặt bằng chỉ đặt nơi có thật.
4. **BOLT LEG chỉ khai ở khoang 1 của mỗi đốt** (vị trí mặt bích nối đốt) — khoang giữa
   không có bu lông cánh. Số lượng tăng ở đốt dưới (8 → 12 bu lông).
5. **Chân ỐNG TRÒN CHS làm LEG**: CHS230x10.5 / x11 / x8 (đổi độ dày theo cao) —
   ống KHÔNG có CONNECT.
6. **Thép góc ĐÔI**: tiết diện tiền tố `2_` (2_L90x90x9, 2_L75x75x7) `BH 20 CONNECT L`.
7. **Bu lông cấp bền cao GR8.8** cho giằng (M18-1 GR8.8, FY 640 FU 800) và
   **bu lông chịu kéo hậu tố -T** cho nối đốt/neo: `M36-T GR6.6 D 36 AS 1017.9 ... TENS AT 763.4`
   (khai `TENS AT` thay `NSP`).
8. File chạy được dù SUPPORTS/GUYS/MATERIAL còn để `$ TODO` (MStower dùng mặc định).

### H2. Cột MONOPOLE (MNP-H40M-WB1.05M)
1. `FACES 1` + **FACE SH4** (thân ống đa giác), mỗi panel CHỈ có `LEG <sec> R1 <dummy>`.
2. Thân chia ~60 panel nhỏ (0.45–0.91m), **mỗi panel 1 tiết diện riêng** để taper trơn:
   section dạng **PG<đường kính>x<dày>** (PG1.453x5 … PG62.1050x8) trong `LIB MStower2`.
3. Tiết diện **DUMMY** (số 63) gán cho R1 — thanh không tồn tại thật.
4. Đường kính TĂNG dần từ đỉnh (0.453m) xuống đáy (1.05m); độ dày tăng bậc 5→6→8mm,
   FY 235 (trên) / 245 (dưới).
5. Kết thúc bằng **panel cao 0.0** (nắp đáy) + `SUPPORT COORD 0 0 0 FIXED` (từ khóa
   SUPPORT số ít + tọa độ, khác kiểu LEG FIXED).

### H3. Mã đặt tên thiết kế (dùng khi lưu thư viện)
`SST4-H<cao>M-WB<đáy>M` = tự đứng 4 chân; `MNP-H..M-WB..M` = monopole.
Đặt tên file mẫu theo mã này để tra nhanh (xem ThuVien/DNG_ThietKe/).

## PHẦN I — ĐỌC BẢN VẼ KHẢO SÁT TAY (nguồn ưu tiên số 1)

Thứ tự tin cậy nguồn: **BẢN VẼ TAY > ảnh chụp > Bia/TABLE** (vụ NBH00063: Bia ghi
"Dây co 60m" nhưng bản vẽ tay chốt "Tự đứng 4 chân 50m, chân 10300, đỉnh 450").
Khi người dùng gửi bản vẽ tay từng đốt, đọc theo quy tắc:

1. **Ký hiệu thép V trên bản vẽ → tên thư viện L** (V<cạnh cm>x<dày mm>):
   V16x14 = L160X160X14 ; V14x12 = L140X140X12 ; V12x10 = L120X120X10 ;
   V10x10 = L100X100X10 ; V8x8 = L80X80X8 ; V8x7 = L80X80X7 ; V8x5 = L80X80X5 ;
   V6x5 = L63X63X5 ; V5x5 = L50X50X5 ; V5x4 = L50X50X4 ; V4x3 = L40X40X3.
   Vẫn PHẢI tra `ThuVien/thuvienthep.txt` xác nhận tên tồn tại.
2. **Chiều cao đốt KHÔNG đều nhau** — mỗi đốt vẽ riêng, tính chiều cao đứng từ
   chiều dài cạnh xiên (số trên cạnh leg) và độ thu ngang: h = √(slant² − run²),
   run = (Wđáy − Wđỉnh)/2. Cộng tổng đối chiếu với chiều cao ghi ở đầu bản vẽ.
3. Số trên mỗi thanh = CHIỀU DÀI thanh (mm) + tiết diện V; số ở cạnh đáy/đỉnh
   hình thang = bề rộng đốt tại đó. Bản mã đánh số (1)(2)... = nút nối đốt.
4. **Cột lưới đỉnh** (đốt nhỏ 0.4–0.6m trên cùng, thường V5x4) mô hình là 1 đốt
   riêng (XDM SPACE nhiều khoang) — chiều cao của nó có thể NGOÀI con số "cao cột"
   danh nghĩa (NBH00063: 50m thân + 4m cột đỉnh = 54m mô hình).
5. Trang "Sàn Đ1..Đn" = giằng mặt bằng từng đốt (kích thước + tiết diện PB);
   "chiếu nghỉ" = sàn nghỉ — khai thêm vào TAITRONG (ANCILLARIES) tại cao độ đó.
6. Trang mặt bằng móng cho khoảng cách chân (= WBASE) và bối cảnh (nhà, tường bao).
7. Số đọc mờ/bất thường (vd đốt 11m dài hơn đốt dưới) → GHI CHÚ trong file và
   hỏi lại người dùng, không tự sửa im lặng.

## PHẦN G — BÀI HỌC (tránh lặp lại)

1. Nhìn ảnh từng đốt TRƯỚC, chọn face SAU. Không áp 1 khuôn cho mọi trạm.
2. Không chắc loại đốt → HỎI người dùng cú pháp mẫu (tối đa 1 vòng đoán).
   Vụ M1/K1: đoán 5 vòng sai, người dùng đưa cú pháp 1 lần là xong.
3. "Giống trạm X" = giống HÌNH DÁNG, không có nghĩa là bê nguyên face trạm X.
4. Vá cục bộ trên khung sai → càng sửa càng lệch. Sai từ gốc thì DỰNG LẠI TỪ ĐẦU.
5. Sửa MSTOWER xong phải đồng bộ INPUT ngay.
6. Làm 1 trạm chuẩn → duyệt render → mới nhân hàng loạt.

## PHẦN I — BỘ QUY TẮC CHỐT SAU LOẠT 12 TRẠM TUDUNGCHUAN (24-25/08/2026)

Chi tiết từng trạm + bảng nhận diện nằm ở `08_NhanDienLoaiDot.md`. Tóm tắt thao tác khi dựng MSTOWER:

1. **Đọc bản vẽ trước, không bịa**: bản vẽ ở "Hình ảnh khác tổng thể cột anten" HOẶC
   "Hình ảnh tổng thể mặt bằng trạm BTS" (tìm thấy ở mặt bằng thì nhặt về "Hình ảnh khác").
   Tên file có thể là "Móng M0@..."; kiểm tra MÃ TRẠM ghi trên giấy (đề phòng tờ lạc trạm khác).
2. **Bề rộng**: xác định số mặt cắt là CHÂN đốt hay ĐỈNH đốt bằng cách đối chiếu kích thước
   chân thực (user chốt/TABLE12_V0). Nội suy TUYẾN TÍNH trong từng đốt; TW mỗi panel phải
   GIẢM DẦN (script kiểm `TW[i] <= TW[i+1]` khi đọc top->down). Cột có thể có ĐOẠN ĐỀU (Đ6-Đ7 = 1.0...).
3. **Khung chuẩn họ cột 4 chân (00040/69/92/112/73/111)**: Đ1 = K2 SPACE 2 + HIP HD ND 2
   (HP lẻ = 0); đốt giữa = M1K1 (HIP HD ND 1) hoặc cặp K+M (R1=0, M dưới K trên); đốt đỉnh hẹp
   đều = DMH; bậc thụt (vd 1.0→0.6) = PANEL VAI `FACE X` HT 0.3 nằm trong đốt trên.
4. **Ô thoi gần vuông**: số cặp K+M mỗi đốt sao cho cao 1 cặp ≈ bề rộng tại đó.
5. **Cột 3 chân**: FACES 3, PLAN PT2; chân ống → LEG = CHS (không CONNECT L); khoang vẽ nét ✕
   → FACE X (1 panel/khoang), nét ◇ → cặp K+M; monopole đỉnh → 3 cạnh CHS chụm TW 0.10 (FACES>1 cấm SH3/SH4).
6. **Panel đánh số duy nhất theo đốt** (dXnn: 716..701, 608..601...; vai = X01/81/91...).
   PLAN chỉ ở panel ĐỈNH đốt (TOP); BOLT LEG chỉ ở panel ĐÁY đốt; neo chân theo TABLE10
   (32-M36/32-M34/18-M28...), nối đốt M18/M20/M22 theo bảng.
7. **Tiết diện**: grep thuvienthep.txt lấy TÊN NGẮN đúng chữ hoa/thường; không có cỡ đúng
   → lấy gần nhất + ghi chú trong file ($ V63x5 -> L65x5, V48x5 -> L50x5, D143 -> CHS140X4.5,
   D80 -> CHS76.3X4, V50x3 -> L50x4, L62x7 không có -> L62x5).
8. **Sau khi dựng**: chạy kiểm số học (tổng HT = H; TW giảm dần), đồng bộ INPUT (02),
   rà cao độ anten (TAITRONG/INPUT), sửa Bia + GiaiPhapKetCauThan1 nếu template sai
   (chiều cao/số đốt/số chân — 5/12 trạm Bia sai).
9. **PLAN PTT** (lưới tam giác đặc, PB1..PB4): mới dùng ở 00046 Đ1-Đ2 và đang nghi gây
   "Zero pivot dof 5/6" (nút nội mặt bằng thiếu độ cứng) — chờ kết quả testA/testB trước khi
   dùng cho trạm khác; mặc định an toàn là PT2/PL1A.

### ỐNG MONOPOLE ĐƠN TRÊN ĐỈNH THÁP LATTICE (chốt 25/08 — HNM00085)

Người dùng chỉ rõ: đốt ống trên đỉnh là **1 THANH ỐNG DUY NHẤT**, KHÔNG được mô hình bằng
3 chân CHS chụm lại (cách tôi làm ở HNM00010/00056 là SAI về bản chất).

- MStower: `SH3/SH4` chỉ dùng khi `FACES 1` → tháp 3/4 mặt không thể có panel ống đơn.
- **Cách đúng trong file text**: KHÔNG đưa ống vào `PROFILE`. Lattice kết thúc ở đỉnh giàn;
  ống khai trong TAITRONG dạng **ANCILLARY hình trụ** (chịu gió + trọng lượng):
  ```
  ANCILLARY
  ONG114  CYL  3.000  36.6  0.342  0.342  0 0 0 0 1 1 1 13  0.114 0.114 3.000
  END
  ...
  ONG-TIP  Xa 0.000 Ya 0.000 Za <cao_do_giua_ong> ANG 0 LIB ONG114
  ```
  (Af = chiều dài × đường kính; mass = chiều dài × khối lượng đơn vị của CHS.)
- Nếu cần phần tử thật để tính nội lực ống: sau khi import dùng GUI MStower thêm 1 member
  từ đỉnh giàn lên cao độ đỉnh ống.
- INPUT (tool CAD) vẫn khai `DOT_TD n ... THAN ONG ... LEGS D114`, `B_CHAN = đường kính ống`
  (chân = đỉnh = D), SO_DOT đếm cả đốt ống.

**KẾT LUẬN THỬ NGHIỆM 25/08/2026 (đã chạy thật, KHÔNG thử lại nữa):**
Ghép `FACE SH3/SH4` (panel ống đơn) vào tháp `FACES 3` → MStower báo
`Use SH3/SH4 panels only if NFACE=1`. Không có cách khai FACES khác nhau theo panel trong 1 file
(kiểm chứng thêm: mọi file thật DNG_ThietKe chỉ có 1 khai báo FACES; monopole DNG00034 = FACES 1 + SH4).
→ Ống đơn trên đỉnh tháp lattice CHỈ có 3 cách: (1) ancillary hình trụ trong TAITRONG [mặc định],
(2) file mô hình riêng FACES 1 + SH4 với RLBAS = cao độ đỉnh lattice, (3) thêm member bằng GUI sau import.
Tuyệt đối KHÔNG mô hình ống bằng 3 chân CHS chụm lại (sai bản chất — người dùng đã bác).

### ⚠️ TÊN TIẾT DIỆN: GÓC ĐƠN vs GÓC ĐÔI (lỗi thật 25/08)

- **Góc ĐƠN** → tên NGẮN: `L130x10`, `L75x6`, `L50x5`, `L62x5`… (dùng `L130X130X10` sẽ báo not found).
- **Góc ĐÔI** → tên DÀI, có tiền tố `2_`: `2_L90x90x9`, `2_L75x75x7`, `2_L125x125x12`, `2_L130x130x10`
  (bằng chứng: file thiết kế thật DNG00023 dùng `2_L90x90x9`, `2_L75x75x7`).
  Viết `2_L125X12` → lỗi `Section: 2_L125X12 not found in library`.
- Tra `thuvienthep.txt` để biết bề dày nào có thật (vd L130x130 chỉ có x9/x10/x12 — không có x11).

### KẾT LUẬN: 2 KHỐI PROFILE TRONG 1 FILE — KHÔNG DÙNG ĐƯỢC (đã thử 25/08)

Khai `PROFILE FACES 3 ... END` rồi `PROFILE FACES 1 (SH4) ... END` → MStower lấy FACES của khối
SAU CÙNG cho toàn mô hình, sinh lỗi `PT2 plan brace incompatible with 1 sided tower`.
→ Chốt: ống đơn trên tháp lattice CHỈ có 3 cách (ancillary trong TAITRONG / file riêng FACES 1 /
thêm member bằng GUI hoặc UDP). Không thử lại SH3/SH4 và 2-PROFILE nữa.

## ⭐ CÁCH CHUẨN MÔ HÌNH ỐNG MONOPOLE TRÊN ĐỈNH THÁP LATTICE (người dùng duyệt 25/08/2026)

Áp dụng cho MỌI trạm có đoạn ống đơn trên đỉnh (HNM00085, HNM00010, HNM00056, NBH...).
KHÔNG dùng SH3/SH4 (chỉ chạy khi FACES 1), KHÔNG dùng 2 khối PROFILE (FACES bị ghi đè),
KHÔNG để ống thành ancillary nếu muốn có phần tử thật.

**Công thức 2 phần:**

1. **VAI CHỤM ngắn** (1 panel, HT 0.30m): 3 (hoặc 4) chân thu từ bề rộng đỉnh lattice xuống
   bề rộng ống quy ước `TWo` — `FACE X LEG <ong> BR1 <giang> H1 <giang>` + PLAN + BOLT LEG.
2. **THÂN ỐNG**: các panel `TW = TWo` ĐỀU (chân = đỉnh), `FACE KXM SPACE 1 @ <HT> LEG <ong> BR1 0 H1 0 H2 0`
   (leg-only, không giằng — 3 chân cách nhau vài cm nên nhìn như 1 ống). PLAN chỉ ở panel đỉnh ống.

**Chọn TWo + tiết diện quy đổi (QUAN TRỌNG — nếu không sẽ cứng gấp 3):**
Cụm 3 thanh trên tam giác đều cạnh `TWo` phải tương đương ống thật:
```
A_cụm = 3·A₁                     ≈ A_ống
I_cụm = 3·(I₁ + A₁·r²),  r = TWo/√3   ≈ I_ống
```
Bảng đã tính sẵn (ống thật ↔ 3 thanh):

| Ống thật | A, I ống | Chọn | TWo | A cụm | I cụm |
|---|---|---|---|---|---|
| D114x4.5 | 15.5 cm², 232 cm⁴ | 3 × CHS48.3X4 | **0.06 m** | 16.7 (1.08×) | 242 (1.04×) |
| D89x4 | 10.7 cm², 96 cm⁴ | 3 × CHS42.4X3 | 0.045 m | 11.1 (1.04×) | ~100 (1.04×) |
| D60x4 | 7.0 cm², 28 cm⁴ | 3 × CHS33.7X3 | 0.035 m | ~8.7 | ~30 |

(Cột 4 chân: r = TWo/√2, chia cho 4 thanh — tính lại theo cùng công thức.)

**Lưu ý kèm theo:**
- TẮT ancillary ống trong TAITRONG khi đã mô hình phần tử thật (tránh tính gió 2 lần);
  diện chắn gió 3 thanh nhỏ lớn hơn ống thật ~25% → thiên về an toàn, chấp nhận được.
- INPUT (tool CAD) vẫn khai `DOT_TD n ... THAN ONG LEGS D114`, `B_CHAN = đường kính ống thật`,
  SO_DOT đếm cả đốt ống; ghi chú quy đổi ở dòng `$ Ghi chu`.
- Tên tiết diện: góc ĐƠN tên ngắn (L75x6); góc ĐÔI tên dài `2_L125x125x12`; ống dùng CHS<D>X<t>.

**Bổ sung (người dùng chốt): ở PANEL VAI CHỤM chỉ dùng THANH THÉP GÓC V** —
`LEG` của panel vai gán tiết diện V (vd L50x5), KHÔNG gán ống CHS. Ống CHS chỉ bắt đầu
từ các panel THÂN ỐNG phía trên (leg-only). Vai chụm là đoạn chuyển tiếp bằng thép góc,
đúng như cấu tạo thật (mặt bích + thép góc thu về ống).

**LỖI THẬT + CÁCH TRÁNH (25/08): vai chụm phải ĐỦ CAO**
```
Some members specified as legs in td/udp files cannot be allocated to adjacent faces of tower.
Load calculations not completed. Possible cause is twist about vertical axis.
```
Nguyên nhân: thu bề rộng quá nhanh (vd 1.00 → 0.06 chỉ trong 0.3m) → thanh chân nghiêng ~61°
so với phương đứng, MStower không gán được chân vào mặt tháp.
Quy tắc: **góc lệch chân ≤ ~25°**, tính bằng `atan(Δr / H_vai)` với `Δr = (W_đỉnh_lattice − TW_ống)/√3`
(cột 4 chân dùng /√2). Chia vai thành 2 panel cho mượt.
Đã áp: 00085 vai 1.2m (2×0.6, 1.00→0.53→0.06, ~24°); 00010 vai 1.2m (0.80→0.43→0.06, ~20°);
00056 vai 0.6m (0.40→0.06, ~18°).
