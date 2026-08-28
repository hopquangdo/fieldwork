# 08 — NHẬN DIỆN LOẠI ĐỐT MSTOWER TỪ HÌNH ẢNH/BẢN VẼ (học từ manual "Standard Panels" 47 trang)

> Nguồn gốc: `ThuVien/~hhED5B.pdf` (chương 6 Standard Panels của MStower — CHÍNH THỨC)
> + `ThuVien/FaceMStower_DINHNGHIA.txt` (danh sách tham số từng face).
> Mục tiêu: **nhìn bản vẽ tay/ảnh 1 đốt → gọi đúng tên face + tham số trong ≤ 30 giây.**

## A. QUY TRÌNH NHÌN 1 ĐỐT (4 câu hỏi, theo thứ tự)

1. **Xiên chính vẽ hình gì?**
   - 1 nét chéo đơn (Z) → họ **D/V** (DL, DR, DLM…)
   - 2 nét chéo cắt nhau thành **X** → họ **X** (X, XM1, XH1…)
   - 2 nét chụm lên ĐỈNH giữa (⋀ đọc từ dưới) → họ **K** (nếu đỉnh ở trên) / họ **M** (2 đỉnh nhọn, ngang ở ĐÁY)
   - Chuỗi **hình thoi ⋄** liên tiếp → **XMA/XM** (thoi cả mặt) hoặc **KXM** (chevron + 2 ngang)
   - Chỉ có ống tròn, không giằng → **SH4** (monopole)
2. **Có thanh ngang không? Nằm ở đâu?** (đỉnh = H1; giữa/eo = H2; các mức = SPACE)
3. **Có thanh phụ (redundant R) không? Kiểu gì?** (nấc thang ngang / tam giác nhỏ / giằng vai chéo)
4. **Đốt chia mấy KHOANG theo chiều cao?** (số SPACE; mỗi mức ngang = 1 ranh giới khoang)

## B. BẢNG NHẬN DIỆN NHANH (các face DÙNG THẬT trong dự án)

| Nhìn thấy trên bản vẽ | FACE | Cú pháp + thanh | Đã dùng ở |
|---|---|---|---|
| Chữ **X to đơn** chiếm cả đốt, ngang đỉnh | **X / XTN** | `FACE X LEG a BR1 b H1 c` (X không chia SPACE — nhiều X = nhiều PANEL) | DNG monopole chân, 00051 |
| X + ngang đỉnh + **giằng vai R1/R2 chéo ở góc trên** | **XH1** | LEG BR1 H1 R1 R2 | |
| X + **nấc thang R ngang** phía trên (1-3 tầng) | **XM1/XM2/XM3** | LEG BR1 R1..Rn | |
| **⋀ (chevron) + ngang đỉnh H1 + ngang đáy H2**, lặp theo khoang | **KXM** | `FACE KXM SPACE n @ h LEG a BR1 b H1 c H2 d` | HNM00056/85 thân |
| ⋀ chụm đỉnh + ngang đỉnh, có **R2 ngang giữa + BR2 ngang đáy** | **K1** | `FACE K1 LEG a BR1 b BR2 c H1 d R1 e R2 f` — **BR2=0 nếu bản vẽ không có ngang đáy** | HNM00010 thân (user chốt) |
| K1 nhưng nửa mặt (eo tại F1.H) | **K1U** | `FACE K1U F1 0.5 LEG.. BR1.. H1.. R1 R2` | DNG00045 thoi trên |
| ⋀ + **2 tầng nấc R** (R1-R4), chia SPACE được | **K2** | `FACE K2 SPACE n @ h LEG a BR1 b H1 c R1 d R2 e` (manual: K2 có R1–R4, "all redundants R1") | NBH00063 Đ1, 00010 5 đốt đáy |
| Chân xoè Eiffel + xiên dài + **nhiều tầng tam giác/nấc (NTR/ND levels)** | **KMG/KMGA/KMGD** | `FACE KMGD ND n LEG.. BR1.. H1.. R1..R2n` | DNG cơ bản, 00040 đáy |
| Chân xoè + đỉnh **chữ M có H2 ngang giữa** + nấc thang dưới | **KMPA** | `FACE KMPA ND n F1 x LEG BR1 BR2 BR3 H1 H2 R1..R3` | (đã thử NBH00063 Đ1) |
| **Nửa DƯỚI thoi**: 2 xiên chụm lên đỉnh giữa ⋀⋀, ngang ở ĐÁY | **M1** | `FACE M1 LEG a BR1 b H1 c R1 d R2 e` (R1 ngang góc, R2 chéo góc) | NBH00063/00112 thoi dưới |
| **Chuỗi thoi ⋄ liên tục** cả mặt (4 mặt giống nhau), ngang mỗi mức | **XMA / XM** | `FACE XMA SPACE S1..Sn LEG..R4 [DTOP][DBTM]` — XMA có redundant, XM không | NBH00063 Đ6-Đ9 |
| Chuỗi thoi nhưng mặt X/Y **so le nhau** | **XDM/XDMA** | `FACE XDMA SPACE S1..Sn [D]` | HNM00040/46 thân |
| **1 nét chéo đơn mỗi khoang (Z-Z-Z so le)** + ngang mỗi mức | **DLM/DRM (DM/DMH)** | `FACE DLM SPACE S1..Sn LEG..` DLM trái/DRM phải; DMH có R so le | DNG00023/173 CHS; 00010 Data ghi DLM |
| Ống tròn trơn (monopole) | **SH4/SH3/SH1** | `FACE SH4 LEG n R1 m` (R1 = nan bán kính) | DNG00034 MNP |
| Chữ **W** (3-4 đỉnh nhọn xuống) ở đốt chuyển tiếp | **W4/WD/WS2/WS3** | LEG BR1..BR3 H1 (WSx dùng PLWx + HWH) | |

**LƯU Ý PHÂN BIỆT hay nhầm nhất:**
- **X có thanh ngang GIỮA (qua tâm chữ X) → là XH1, KHÔNG phải X**: `FACE XH1 LEG a BR1 b
  H1 c R1 0 R2 0` (H1 của XH1 nằm GIỮA; R1+/R2+ là thanh đứng chỉ sinh khi VU/VD → để 0).
  X thường thì H1 nằm ĐỈNH. (Người dùng chốt ở HNM00040 Đ5-Đ7.)
- **KXM ≠ X**: KXM là ⋀ chevron (2 xiên chụm đỉnh, KHÔNG bắt chéo qua nhau); X là 2 xiên CẮT NHAU.
- **K1 ≠ KXM**: K1 có giằng vai/nấc R1 R2 ở góc + BR2 ngang đáy (có thể =0); KXM chỉ có H1 H2 (không R).
- **K2 ≠ K1**: K2 nhiều tầng nấc R (R1–R4) và trong dự án cho phép `SPACE n` (chia nhiều khoang);
  bản vẽ "đốt có ≥2-3 khoang ngang chia tầng + ⋀" → K2. 1 khoang đơn → K1.
- **XMA ≠ M1+K1**: XMA vẽ THOI NHỎ LIÊN TỤC nhiều mức; đốt chỉ có MỘT thoi LỚN choán cả đốt
  → phải ghép M1 (nửa dưới) + K1/K1U (nửa trên), KHÔNG dùng XMA SPACE 1 (ra chữ X).
- **DLM ≠ X**: DLM mỗi khoang chỉ 1 nét chéo (so le trái/phải các khoang), X có 2 nét.
- Mặt cắt TAM GIÁC (3 chân) → PLAN họ **PT** (PT1/PT2/PTT); VUÔNG (4 chân) → PL/PD/PDM/PWD/PLW.
- **HIP (giằng hông)** — bản vẽ thường có CỘT TAM GIÁC NHỎ bên cạnh mặt đứng = giằng hông
  từng đốt, ĐỪNG BỎ SÓT (người dùng bắt lỗi ở HNM00010). Giới hạn NTR theo face (đã thử thật):
  **K1/M1/K1U → NTR 1**; **K2 → NTR TỐI ĐA 2** (NTR 3 báo `hip bracing incompatible`);
  **KMGD ND n → NTR ≤ n (≤3)**; **XMA/X/KXM → KHÔNG nhận HIP**.
  Cú pháp: `HIP HK NTR n HP1 0 HP2 <sec nhỏ>` + BOLT thêm `HP1 1 M16-1 HP2 1 M16-1`.

## B2. TÊN TIẾT DIỆN TRONG THƯ VIỆN MSTOWER — DÙNG TÊN NGẮN

**Thư viện dùng tên NGẮN `L<cạnh>x<dày>`** (vd `L130X10`, `L120x10`, `L100X10`, `L90x8`,
`L75x6`, `L65x5`, `L50x5`, `L130x11`) — KHÔNG phải dạng dài `L130X130X10` (người dùng chốt:
"trong mstower không có L130X130X10 chỉ có L130x10 thôi, các tiết diện khác cũng thế").
- Viết đúng HOA/thường như trong `thuvienthep.txt` (có cả L100X10 lẫn L100x10 — grep lấy đúng).
- Góc đôi: tiền tố `2_` + tên ngắn, vd `2_L130x11`, `2_L90x90x9` (kiểu DNG) — khai
  `FY 235 Fu 400 BH 20 CONNECT L`.
- LUÔN grep `thuvienthep.txt` xác nhận tên tồn tại trước khi viết SECTIONS (tên sai →
  lỗi `V_MINMAX n=0`).

## C. THAM SỐ QUAN TRỌNG (từ manual)

- `SPACE S1 S2 ... Sn` — mỗi Si là CHIỀU CAO 1 khoang, **tổng Si = HT của panel** (DM/DLM/XDMA/XMA/KXM
  cho phép từng khoang cao KHÁC nhau — không cần chia đều!). Sn ≤ 40 khoang.
- `[DTOP]/[DBTM]` (XMA): thoi bắt đầu/kết thúc kiểu diamond ở đỉnh/đáy; bỏ → đầu chữ "X".
- `[LEFT]` (DM2/DLM2/DMH2): nét chéo bắt đầu từ góc trái.
- `F1/F2` (K1U/KH/KMH/K5L5/KMPA...): tỷ lệ eo/đỉnh — F1 bỏ trống mặc định 0.2, F2 mặc định 0.4.
- `ND/NTR` (KMG/KMGD/KMPA/KM/KMA): số tầng nấc diagonal/triangular — nhìn bản vẽ ĐẾM SỐ NẤC.
- Thanh có dấu `+` trong manual (R1+, R2+...) chỉ sinh khi có keyword `VU`/`VD`.
- "May be inverted" (KB, KBP, KMG, XM3, XV...): có thể lật ngược — bản vẽ úp/ngửa vẫn cùng face.

## D. QUY TRÌNH CHUẨN KHI DỰNG 1 CỘT (ràng buộc bởi bài học đã sai)

1. Mở bản vẽ tay của CHÍNH trạm (thường ở "Hình ảnh khác tổng thể cột anten").
2. Chép ra giấy: TỔNG CAO, số đốt, chiều cao TỪNG đốt (đọc lề trái bản vẽ; nếu tổng
   các đốt ≠ tổng cao ghi ở đầu bản vẽ → HỎI, không tự chia).
3. Với TỪNG đốt: trả lời 4 câu hỏi mục A → gọi tên face theo bảng B (đối chiếu hình trong PDF nếu nghi ngờ).
4. Bề rộng: WBASE = đáy; TW từng panel giảm dần LIÊN TỤC theo bản vẽ (taper); đỉnh theo bản vẽ.
5. Tiết diện: đọc nhãn trên bản vẽ (V130x11...) + TABLE6 đo đạc; quy đổi V→L tra thuvienthep.
6. So sánh với thiết kế cũ trong `tudung`/`TramChuan`/`DNG_ThietKe` nếu có.
7. Render → đưa người dùng duyệt → mới nhân rộng.

## D2. ỐNG MONOPOLE TRÊN ĐỈNH LATTICE

**⚠️ SH3/SH4 CHỈ dùng được khi cả cột FACES=1** (thuần monopole như DNG00034).
Trộn SH3 vào tháp FACES 3/4 → MStower báo `Use SH3/SH4 panels only if NFACE=1` (đã dính).

- Cột THUẦN monopole (FACES 1): `FACE SH4 LEG <PG/CHS> R1 <DUMMY>` — LEG là 1 thanh ống
  thật tại tâm, R1 = tay cứng master-slave (mẫu DNG00034: SH4 + PG + DUMMY FY 245).
- Tháp lattice FACES 3/4 có ống trên đỉnh: mô hình ống = panel **leg-only 3 cạnh CHS
  chụm sát**: `FACE KXM SPACE 1 LEG <CHS> BR1 0 H1 0 H2 0`, **TW 0.10**, PLAN PB đều 0
  — gần đúng 1 ống đơn. Muốn 1 thanh ống THẬT: import xong dùng GUI thêm nút tâm +
  1 member ống (không làm được trong file text).
- Chiều cao ống = TỔNG CAO CHỐT − tổng lattice (vd HNM00010: 35.0 − 30.2 = 4.8m).

## D3. FORMAT INPUT CHUẨN CHO TOOL CAD (học từ file NGƯỜI DÙNG TỰ SỬA — 00010/00040)

So sánh bản người dùng sửa tay với bản tôi viết, các quy ước CHÍNH THỨC của INPUT:

1. **MONG_KICHTHUOC dùng M0** (móng chân cột, vd `M0 1.2 1.2 1.2 L0`) — INPUT của tool
   CAD GIỮ M0; chỉ có Data TABLE2/TABLE3 mới bỏ M0. (Tôi từng đổi INPUT sang M1..Mn —
   người dùng sửa lại M0 → INPUT theo M0.)
2. Mục 1 có thêm trường **CHIEU_CAO_MODUL X**; mục 7 có **BAN_KINH_CO X X**;
   mục 2 có dòng "BANG TOA DO MONG CHO MSTOWER (MONG_MSTOWER, khong xoay)".
3. **MAT_CAT đốt đáy có thể là PR1** (00010 đốt 1), các đốt trên PT2/PL1A theo số chân.
4. **PLAN PT2 trong INPUT có thể PB1=0,PB2=0,PB3=V50x5** (chỉ 1 thanh thật) — theo cấu tạo thật.
5. **THAN ONG** cho đốt ống monopole: `THAN ONG ... LEGS D114 ... SECTIONS ONG:LEG=D114(CHS114x4.5),BR1=0,H1=0`.
6. **PHUONG_THUC_NOI THAN_1GA** (không phải "Bu").
7. Anten: `LOAI` = TÊN loại (RRU/8P/4G/Viba), `KICH_THUOC` = kích thước WxHxD hoặc D600,
   `TRONG_LUONG` = giá trị cản gió/khối lượng — đúng thứ tự bản user sửa.
8. TIET_DIEN_COT = BỀ RỘNG CHÂN cột (7.20/5.60), RONG_DINH = bề rộng đỉnh.
9. SPACE trong INPUT = số khoang theo bản vẽ từng đốt (K2 SPACE 5/3/2; K1 SPACE 2/1; KM SPACE 4).
10. SO_DOT đếm CẢ đốt ống (00010: 13 lattice + 1 ống = 14).

## E. VÍ DỤ CHUẨN ĐÃ CHỐT

- **HNM00040** (4 chân 36m, người dùng chú thích + chốt qua nhiều vòng):
  - Đ1 K2 SPACE 2 (chân 5.6→3.4, xiên V90x8, neo 32-M36).
  - Đ2-Đ4 thoi M1+K1 F1 0.5 (V120x10/V100x10, thoi V75x6).
  - **Đ5-Đ7 = cặp K (trên) + M (dưới) với R1=0**, mỗi đốt 4.2m = 2 panel 2.1m
    (ảnh thật: chevron ⋀/⋁ xen kẽ có ngang giữa — KHÔNG phải XH1/X đơn).
  - Đ8 DMH 7.3m SPACE 6 (X + R so le, đỉnh 0.6).
  - **HIP Đ1-Đ4 = kiểu HD** (giằng hông chéo, bỏ ngang trung gian). ⚠️ Số tầng ND phải
    KHỚP face (như HK/NTR): **K1/M1 → `HIP HD ND 1 HP1 x HP2 x HP3 0`**;
    **K2 → `HIP HD ND 2 HP1 x HP2 x HP3 0 HP4 x HP5 0`** (ND 4 trên K1/M1 → lỗi
    `hip bracing incompatible`). HP lẻ (3/5/7) = ngang trung gian → 0.
  - **BỀ RỘNG GIẢM DẦN LIÊN TỤC** 5.6 → 3.4 → 2.65 → 2.5 → 2.04 → 1.89 → 1.47 → 1.37 →
    1.27 → 1.18 → 1.09 → 1.0 → 0.9 → 0.8 → 0.6 (KHÔNG để đoạn nào bằng nhau).
  - PLAN PL1A; bu lông nối M18; tên tiết diện NGẮN (L130X10, L120x10, L90x8...).
  - **BẬC THỤT bề rộng giữa 2 đốt** (vd đỉnh Đ7 = 1.0 nhưng Đ8 thẳng đều 0.6):
    KHÔNG nhảy TW trực tiếp — thêm **PANEL VAI chuyển tiếp ngắn** (HT ~0.3m, FACE X,
    taper 1.0→0.6) nằm TRONG tổng chiều cao của đốt trên (Đ8 7.3 = vai 0.3 + DMH 7.0).
  - "Mỗi đốt 2 lần K+M" = 4 panel × HT/4 (K,M,K,M từ trên xuống), TW nội suy giảm dần
    trong đốt; BOLT LEG chỉ ở panel đáy đốt, PLAN chỉ ở panel đỉnh đốt.


- **HNM00010** (Eiffel 3 chân 40m = 13 đốt lattice + ống monopole 2m): 5 đốt đáy nhiều khoang
  → `K2 SPACE n`; 8 đốt trên 1 khoang có nấc góc → `K1 ... BR2 0`; ống đỉnh D114 leg-only.
- **NBH00063** (4 chân): Đ1 K2 SPACE 5; Đ2-Đ5 thoi lớn = M1 + K1 F1 0.5 (R1 ngang góc, R2 chéo góc);
  Đ6-Đ9 XMA nhiều khoang R=0.
- **HNM00040/46**: thân XDM (thoi so le), đáy KMGD ND n.
- **DNG00023/00173**: thân đều CHS → DLM/DRM xen kẽ (1 nét chéo/khoang, so le).
- **DNG00034**: monopole SH4 + PG.

## VÍ DỤ HNM00046 (người dùng chốt 24/08/2026) — 3 chân, 42m, 7 đốt x 6m

- Cấu trúc: D1 = K2 SPACE 3; **D2, D3 = MỖI ĐỐT 2 LẦN K1** (BR2=0, mỗi panel 3m) — tương tự
  "2 lần K+M" nhưng dùng K1 lặp; D4, D5 = 2 lần (K+M) R1=0 (4 khoang 1.5m);
  **D6 = đốt HỖN HỢP**: K+M (2 khoang dưới) + X (2 khoang trên); D7 = 4 khoang X.
- K/M/X/K1 KHÔNG có tham số SPACE (chỉ K2/XMA/DMH... mới có SPACE) — bỏ "SPACE n @ ..." nếu lỡ ghi.
- Bề rộng giảm dần LIÊN TỤC 7.30 → 0.60: nội suy HÌNH HỌC (taper đều %/m):
  `w(z) = W_chan * (W_dinh/W_chan)^(z/H)` — khớp số người dùng ước (5.11 tại đỉnh D1).
  Đỉnh đốt: 5.11 / 3.57 / 2.50 / 1.75 / 1.23 / 0.86 / 0.60.
- Panel đánh số theo đốt từ trên xuống: 74..71 / 64..61 / 54..51 / 44..41 / 32,31 / 22,21 / 1.
  PLAN chỉ ở panel ĐỈNH đốt; BOLT LEG chỉ ở panel ĐÁY đốt (LEG 8 M22 cho K1, M24 neo K2).
- INPUT: THAN K1K1 (2 lần K1), THAN KMX (đốt hỗn hợp K+M+X), THAN X; M0 cho móng.
- Tên tiết diện thư viện xác nhận grep thuvienthep.txt: L150x10, L130X10, L100X10, L75X8, L75x5, L60x5, L50x5
  (chữ hoa/thường đúng như thư viện, KHÔNG dùng dạng dài L150X150X10).

### Bổ sung HNM00046 (24/08): quy tắc Ô THOI GẦN VUÔNG cho vùng K+M

- Người dùng chốt: các đốt thân trên (kể cả ĐỐT TRÊN CÙNG) đều là K+M; số khoang mỗi đốt
  chọn sao cho **cao 1 cặp K+M ≈ bề rộng cột tại đó** (ô thoi nhìn gần vuông), tổng cao giữ nguyên.
- Với 00046 (24m vùng K+M, w 2.5→0.6): D4 = 3 cặp × 2.0m; D5 = 4 cặp × 1.5m; D6 = 6 cặp × 1.0m;
  D7 = 8 cặp × 0.75m (HT panel = nửa cao cặp). Panel đánh số dạng dXnn (406..401, 508..501, 612..601, 716..701).
- INPUT: SPACE = SỐ PANEL của đốt (2 panel = 1 cặp K+M) → D4 SPACE 6, D5 SPACE 8, D6 SPACE 12, D7 SPACE 16.

### HNM00046 bản CHỐT theo bản vẽ tay (24/08) — sửa 3 lỗi tôi mắc

1. **Bề rộng phải lấy từ SỐ GHI TRÊN BẢN VẼ từng đốt**, không tự nội suy toàn cột:
   mốc đốt 00046 = 7300/5100/3700/3100/2400/1800/1200/600 (số cạnh mỗi tam giác mặt cắt
   = bề rộng ĐỈNH đốt đó). Nội suy tuyến tính TRONG từng đốt. Tự nội suy hình học toàn cột
   làm cột thu quá nhanh → "ô nhỏ quá".
2. **Thanh cánh có thể là ỐNG**: nhãn D114/D89 trên bản vẽ chỉ vào thanh cánh
   → LEG = CHS114X4.5 (đốt dưới) / CHS89X4 (đốt trên). Xiên V100x8/V62x7/V62x4.
   V62x7 không có trong thư viện → dùng L62x5 (ghi chú lại).
3. **Các tam giác vẽ riêng từng đốt = MẶT CẮT NGANG (PLAN)**, đặc dần xuống dưới:
   đốt to PB1/PB2 nội + chu vi V100x8; đốt giữa 1 ngang; đốt nhỏ chỉ chu vi.
   HIP: K2 → HK NTR 2; K1 → HK NTR 1 (HP1=0, HP2=V62x5).
   Số cặp K+M sau khi có bề rộng đúng: D4=2×3.0m, D5=3×2.0m, D6=4×1.5m, D7=5×1.2m
   (cao cặp ≈ bề rộng — ô thoi gần vuông). Cặp: M dưới, K trên (giống 00040).

- **PLAN loại PTT** (người dùng chốt cho 00046 đốt 1 VÀ đốt 2 — 2 đốt to nhất): mặt bằng tam giác LƯỚI ĐẶC
  (tam giác lớn chia các tam giác con), có 4 nhóm thanh PB1..PB4 —
  `PLAN PTT PB1 x PB2 x PB3 x PB4 x TOP`. Nhận diện: mặt cắt vẽ tay có lưới tam giác
  con dày đặc (nhiều hơn 1 ngang + 1 X của PT2) → dùng PTT. INPUT: `MAT_CAT PTT`.

### HNM00069 (24/08) — chú ý cách đọc số bề rộng trên bản vẽ

- Số ghi cạnh các ô mặt cắt (4350/3400/2600/1870/1280/1000/600) = bề rộng **ĐỈNH từng đốt**,
  KHÔNG phải chân đốt. Bề rộng CHÂN cột lấy theo kích thước thực người dùng chốt (00069 = 6.4m,
  dù bản vẽ ô dưới cùng ghi 4350 = đỉnh Đ1). Chuỗi 00069: 6.40 → 4.35/3.40/2.60/1.87/1.28/1.00/1.00 (Đ7 đều)/0.60.
- Cùng họ 00040: 4 chân vuông, D8 có VAI X 0.3m xử lý bậc thụt 1.0→0.6 + DMH đều; PLAN PL1A.
- Đọc "V90x0.8"=V90x8 (cánh), "V90x0.10"=V90x10 (xiên dưới), "V64x0.5"=V64x5→L65x5, "V49x0.5"→L50x5
  (bản vẽ ghi bề dày theo cm).

## ĐỢT DỰNG 25/08/2026 — 7 trạm còn lại (tóm tắt đặc thù, bản vẽ ở "Hình ảnh khác"/"mặt bằng trạm BTS")

| Trạm | Kiểu | H | Đặc thù |
|---|---|---|---|
| 00092 | 4 chân vuông | 44m, 8 đốt x 5.5 | chân 6.0; đỉnh đốt 3.70/2.62/1.83/1.60/1.30 (Đ6-Đ7 đều 1.3); vai + DMH 5.2; cánh V150x12→V130x11→V100x10→V90x7→V63x6; neo M34 |
| 00112 | 4 chân vuông | 45m, 9 đốt | cao đốt KHÔNG đều (5.6/5.2/5/5/4.7/4.5x3/6.0); chân 4.38; Đ6-Đ8 đều 1.0; Đ9 = vai + DMH 5.7; bản vẽ "H=39" bị sửa thành 45 (39+6) |
| 00001 | 3 chân ỐNG | 36m, 12 đốt x 3 | FACE X từng khoang (nét ✕); cánh D143→CHS140X4.5, D80→CHS76.3X4, D60→CHS60.3X4; chân 3.6 SUY TỪ TABLE12_V0 (đo 3.46 tại +0.86m); Bia 42/7 sai đã sửa 36/12 |
| 00051 | 4 chân vuông | 40.5m (7x5+5.5) | trang phác ghi H=45 nhưng trang CHI TIẾT H=40.5 (theo chi tiết); mặt cắt = CHÂN đốt 4300/3440/2500/1920/1400/1000/1000/600; Đ7 taper 1.0→0.6 KHÔNG vai; toàn K+M, không K2 |
| 00056 | 3 chân | 40m = 35 lattice (9 đốt) + monopole 5m | user chốt 25/08; đốt cao 5/5/4.2/4/3.8/3.4/3/1.6/5; chân 3.7; ghi chú bản vẽ "bê tông che phủ không đo được bu lông" giúp nhận diện trạm; ống CHS114X4.5 ước |
| 00073 | 4 chân vuông | 42m | chân 5.90 user chốt; số bản vẽ = ĐỈNH đốt 3.47/3.40/2.60/1.87/1.40/1.00/1.00/0.60; Đ1 5.8m ước để tròn 42; vai + DMH; bản vẽ nằm ở "Hình ảnh tổng thể mặt bằng trạm BTS" |
| 00111 | 4 chân vuông | 40m, 8 đốt x 5 | trang chi tiết ở "mặt bằng trạm BTS" (đã nhặt về "Hình ảnh khác"); mặt cắt = CHÂN đốt 4340/3260/2520/2520 (Đ3 đều)/1370/1000/1000/600; vai + DMH; Bia 45 sai đã sửa 40 |

Quy tắc rút thêm:
- Bản vẽ có thể nằm ở "Hình ảnh tổng thể mặt bằng trạm BTS" — kiểm tra cả 2 thư mục; tìm thấy thì NHẶT về "Hình ảnh khác tổng thể cột anten".
- Ảnh bản vẽ có thể mang tên "Móng M0@..." — đừng bỏ qua.
- Có trạm số mặt cắt = CHÂN đốt (00051, 00111), có trạm = ĐỈNH đốt (00069, 00073) — đối chiếu với kích thước chân thực để phân biệt; không rõ thì HỎI.
- Chân cột không ghi trên bản vẽ → suy từ TABLE12_V0 (đa giác đo kinh vĩ) như 00001.
- Sau khi đổi chiều cao cột PHẢI rà CAO ĐỘ ANTEN trong INPUT/TAITRONG — hạ các anten vượt đỉnh (00001, 00073, 00111 đã hạ).
- Bản vẽ lạc trạm khác (00048 lạc vào 00056) — kiểm tra mã trạm ghi trên giấy trước khi dùng.

## ĐỢT PCC/tudung 25/08/2026 — 3 trạm NBH00064_2 / NBH00089_2 / NBH00136_2

Đặc thù batch này (khác tudungchuan):
- Bia + XML gốc (`<trạm>/data/<mã>_ThongTinChung`) đều ghi "Dây co 45/45/54m" — SAI template.
  Người dùng chốt: TẤT CẢ là TỰ ĐỨNG; chiều cao lấy theo **ĐO KINH VĨ** = Đỉnh cột z − Chân cột z
  (TABLE12_DinhCot − TABLE12_ChanCot): 00064 = 48.84→49m; 00089 = 40.0m; 00136 = 60.0m.
  Bề rộng chân đối chiếu TABLE12_V0 (00064 ~3.8; 00089 4.94 theo bản vẽ; 00136 = 10.0 khớp cả 2 nguồn).
  → Sửa cả TABLEBia LẪN XML ThongTinChung (LoaiCot/ChieuCao/SoDot/TuDung_BeRong*).
- Bản vẽ = SỔ TAY khảo sát: 1 trang TỔNG (elevation, số đốt, mốc bề rộng) + MỖI ĐỐT 1 TRANG
  (chiều dài thanh cánh L = cao đốt; các thanh đo lẻ; mặt cắt + bản mã). Trang tổng có thể
  chụp tên file dài kiểu "1786407738832_...jpg". Chiều dài L ghi trên trang đốt là số đo tay —
  tổng có thể lệch vài % so kinh vĩ → scale về H kinh vĩ.
- Kiểu kết cấu: 4 chân vuông; đốt dưới thoi lớn M1K1 + HIP HD ND1; đốt trên cặp K+M;
  00064 đốt đỉnh 0.45 đều (vai 0.74→0.45); 00136 có THÁP CON đỉnh 4.56m (vai 1.18→0.86, taper →0.56)
  + 2 sàn thao tác; sàn thao tác ghi ở dị tật "Mặt sàn" → thêm dòng vào TABLE6 đốt đó.
- TAITRONG dựng từ TABLE11 (đo thực): chia 3 sector 0/120/240 (GIẢ ĐỊNH — cần azimuth thật),
  ANG = 90 − phương vị, LIB MS_ANC (10P/8P/5G/SG900/DUAL-BAND/RRU), FEEDER không mô hình riêng.
- Tiết diện lạ: V135x10→L130X10; V100x5→L100X7; V62x... như cũ. Trạm 00064 TABLE2 thiếu Móng M4
  (4 chân) → bổ sung dòng M4.


### SỬA 25/08 (lần 2) — HNM00112 và quy tắc ĐỈNH ĐỐT

Tôi đã sai 2 lần liên tiếp ở 00112, ghi lại để không lặp:
- Số mặt cắt trên sổ tay LUÔN là **bề rộng ĐỈNH đốt**. Chuỗi 00112: đỉnh 4.36/3.42/2.52/1.87/1.28/1.00/1.00/1.00/0.60
  → **chân cột 5.90** (người dùng chốt), chân đốt n = đỉnh đốt n−1.
- Loại đốt 00112 (người dùng chốt): Đ1, Đ2 = **K2** (HIP HD ND 2); Đ3, Đ4, Đ5 = **M1 + K1** (F1 0.5, HIP HD ND 1);
  Đ6, Đ7, Đ8 = **FACE X**; Đ9 = **DMH** (vai X 0.3m 1.0→0.6 + DMH 5.7m đều 0.6).
- CẦN RÀ LẠI các trạm tôi đã dựng theo giả định "số = chân đốt": **HNM00051, HNM00111**
  (và kiểm lại 00092, 00001, 00056) — phải dịch lên 1 bậc + hỏi người dùng kích thước chân cột thực.

### NBH00136 (26/08) — người dùng chốt loại đốt, LƯU Ý CÁCH NHÌN

Tôi nhìn nhầm "thoi lớn" thành M1+K1; thực tế người dùng đọc là:
- **Đ1, Đ2, Đ3 = K2** (1 panel/đốt, SPACE 3/2/2 + HIP HD ND 2) — không phải M1K1.
- **Đ4 = 2 K2 ĐÈ LÊN NHAU** (2 panel K2, mỗi panel SPACE 2).
- **Đ5 = 3 K1 ĐÈ LÊN NHAU** (3 panel K1, BR2=0, HIP HD ND 1).
- **Đ6, Đ7, Đ8 = 3 nhóm K+M đè lên nhau** (6 panel/đốt, R1=0).
- **Đ9 = 5 nhóm K+M, CHÂN = ĐỈNH ĐỀU 0.56** → đoạn giật 1.18→0.56 xử lý bằng
  VAI CHUYỂN TIẾP `FACE X` 0.3m (giống HNM00040/00069/00112).

Bài học: khi bản vẽ vẽ nhiều "chữ A/thoi" chồng nhau trong 1 đốt, đó là **nhiều panel cùng loại
đè lên nhau** (2 K2, 3 K1, 3 nhóm K+M…), KHÔNG phải một cặp M1+K1. Hỏi người dùng nếu không chắc.
