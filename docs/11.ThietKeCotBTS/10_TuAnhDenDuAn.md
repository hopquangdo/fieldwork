# 10 — TỪ MỘT THƯ MỤC ẢNH PHẲNG → DỰ ÁN HOÀN CHỈNH (ẢNH + DATA) CHO CỘT DÂY CO & TỰ ĐỨNG

> Viết sau lô 5 trạm Hà Tĩnh 22–23/09/2026 (545 ảnh Zalo, tên hash, không Data, không bảng đăng ký).
> Đây là quy trình A→Z khi **đầu vào chỉ có 1 thư mục ảnh của mỗi trạm** và đầu ra phải là
> thư mục dự án mà phần mềm KiemDinhCotAnten v2.9.0 mở được ngay.
> Các file liên quan: `05_SapXepAnh.md` (chi tiết nhặt ảnh), `01_TaoDataMau.md` (chi tiết Data),
> `08_NhanDienLoaiDot.md` (loại đốt cho MStower — bước sau, không thuộc file này).

---

## 0. KẾT QUẢ PHẢI ĐẠT (kiểm tra ngược từ đây)

```
<LÔ>/3. DU AN/
├── 00_TONG HOP LO ....md                       ← bảng thông số + danh sách CẦN XÁC NHẬN
└── <MÃ TRẠM>_<Địa điểm>/                       ← BẮT BUỘC có dấu "_" sau mã trạm
    ├── Data<MÃ TRẠM>_<Địa điểm>/               ← 50 file .txt (danh sách mục 5)
    └── <MÃ TRẠM>_<Địa điểm>/                   ← cây ảnh: 10 hạng mục (dây co) | 8 hạng mục (tự đứng)
        ├── 1.Hình ảnh tổng thể cột anten/
        │     ├── <thư mục công tác> (≥1 ảnh)  ...
        │     └── Hình ảnh khác ... (toàn bộ ảnh còn lại của hạng mục)
        └── ...
```

Tiêu chí nghiệm thu (chạy script mục 6 trước khi báo xong):
1. Mở được trong phần mềm — tức là: tên thư mục đúng mẫu, `TABLEBia` đủ 17 khoá, mọi trường số là số.
2. Mỗi hạng mục ≥ 2 thư mục công tác, mỗi thư mục công tác ≥ 1 ảnh đúng chủ đề, có 1 "Hình ảnh khác…".
3. **Tổng ảnh gốc = tổng ảnh trong các bin "Hình ảnh khác…"** (không mất ảnh; ảnh gốc giữ nguyên, chỉ copy).
4. Số dòng các bảng khớp Bia: TABLE6 = số đốt; TABLE10 = 1 + (số đốt − 1); TABLE8/9 = số tầng dây co;
   TABLE2/3 = số móng; TABLE12 = 4 vòng × số chân.
5. Không còn ô "chưa có số liệu" — mọi cột đánh giá là câu mô tả thật; bảng số đo có giá trị khung chuẩn.
6. Mục dị tật (10 hoặc 8) có thư mục `<Cấu kiện> - <tình trạng>` khớp 1-1 với câu đánh giá trong Data.

---

## 1. BƯỚC 1 — NHÌN ẢNH XONG PHẢI TRẢ LỜI ĐƯỢC 6 CÂU

| # | Câu hỏi | Cách trả lời từ ảnh |
|---|---|---|
| 1 | **Dây co hay tự đứng?** | Có cáp căng chéo từ thân xuống đất + móng neo M1..M4 + tăng đơ/ma ní/khoá cáp → **dây co**. Chân cột xoè 3–4 móng riêng, không cáp → **tự đứng**. Không tin tên thư mục lô (HNM00061 nằm trong "tudungchuan" nhưng là dây co). |
| 2 | **Mấy chân?** | Nhìn mặt bằng chân cột / mặt cắt tam giác hay vuông; dây co thân 0.6 m thường 3 chân; tự đứng Eiffel thường 4. |
| 3 | **Cao bao nhiêu, mấy đốt, mấy tầng dây?** | Ưu tiên **PHIẾU KHẢO SÁT** (mục 2). Không có → đếm vạch sơn `D1…Dn` trên mặt bích và `T1…Tn` trên bản mã dây co trong ảnh trèo cao; đọc số trên bản vẽ tay. |
| 4 | **Số móng?** | Nhãn `M0…M4` trên dấu GPS của ảnh; dây co = M0 + 4 móng co; tự đứng = M1..Mn (n = số chân), KHÔNG có M0 trong Data. |
| 5 | **Đợt khảo sát hay đợt kiểm định?** | Có ảnh súng bật nảy / máy đo điện trở / toàn đạc / đồng hồ lực căng / cờ-lê lực → kiểm định. Chỉ thước cặp + thước dây + trèo cao → **khảo sát** → các bảng số đo sẽ là khung chuẩn (mục 5.3). |
| 6 | **Dị tật thấy được?** | Ghi lại theo ảnh: han rỉ (nhẹ/nặng) mặt bích, bu lông, vòng ốp, ma ní; móng ngập nước/phủ đất/cây cỏ; dây co đứt/tuột; ngói/vật liệu che móng… — đây là nguồn cho toàn bộ cột "Đánh giá". |

### 1.1 Đọc 500 ảnh với ~35 sheet (không mở từng ảnh)
- Ảnh Zalo: tên hash, không EXIF. Dấu GPS của app khảo sát nằm **ĐÁY ảnh**: ngày / toạ độ / địa chỉ /
  **dòng cuối = tên trạm (+ mã móng M0..M4)**. Nhãn này KHÔNG cho biết công tác → phải nhìn nội dung.
- Contact sheet chuẩn: tile = thumbnail **300×400** + dải **46 px** cắt `x 50–100 %, y 95.5–100 %`
  (phóng to dòng nhãn), lưới **4×4**, đánh số `#n` (nền đen chữ vàng). Sheet ≈ 1200×1784 ≈ 2.9k token.
- Ghi ngay dải chỉ số → hạng mục trong lúc đọc (vd `1–9 đo kích thước M0`, `61–110 trèo cao`).
- Script: mục 8.1.

### 1.2 Bảng nhận dạng nội dung ảnh → hạng mục

| Thấy gì trong ảnh | Hạng mục (dây co / tự đứng) | Thư mục con |
|---|---|---|
| Cột chụp xa toàn thân | 1 / 1 | Hình ảnh mặt đứng cột anten |
| Cận anten, RRU, viba trên đỉnh | 1 / 1 | Hình ảnh thiết bị trên cột |
| Nhà trạm, tủ, sân, đường vào | 1 / 1 | Hình ảnh tổng thể mặt bằng trạm BTS; nhà trạm → Hình ảnh biển nhà trạm |
| Tờ giấy: bản vẽ tay, phiếu khảo sát | 1 / 1 | **CHỈ** "Hình ảnh khác tổng thể cột anten" (không bao giờ vào phụ lục) |
| Mặt bích nối đốt chụp gần (khe hở) | 2 / 2 | Công tác kiểm tra khe hở… |
| Cáp dây co + đồng hồ lực căng (hoặc dây co tại móng) | 3 / – | Công tác đo lực căng… móng Mx |
| Khoá cáp U-bolt + cờ-lê lực (hoặc cận khoá cáp) | 4 / – | Công tác kiểm tra lực siết ê-cu khoá cáp móng Mx |
| Bê tông móng + súng bật nảy (hoặc thước dây trên bê tông) | 5 / 3 | …cường độ bê tông móng Mx |
| Máy đo điện trở, cọc, kẹp dây tiếp địa | 6 / 4 | …điện trở nối đất… |
| Máy toàn đạc, gương, cột chụp từ 2 hướng | 7 / 5 | …đo độ thẳng đứng… |
| Ảnh chụp từ trên cột xuống, mặt bích D1..Dn, bản mã T1..Tn | 8 / 6 | Trèo cao: chân / giữa / đỉnh cột (theo thứ tự chụp: đốt thấp → cao) |
| Thước cặp / thước dây trên thanh cánh, giằng, bu lông, cáp, ma ní, tăng đơ, móng | 9 / 7 | Đo kích thước <cấu kiện> |
| Han rỉ, đứt, nứt, ngập, lấp… | 10 / 8 | `<Cấu kiện> - <tình trạng>` |

---

## 2. BƯỚC 2 — TÌM "PHIẾU KHẢO SÁT" VÀ "BẢN VẼ TAY" TRƯỚC KHI LÀM BẤT CỨ GÌ

Trong mỗi thư mục ảnh luôn có **1–3 tờ giấy chụp lại** (đầu hoặc cuối dãy, nền trắng, không dấu GPS):
1. **Phiếu khảo sát hiện trường** (form in sẵn, điền tay) — ghi: Mã trạm, Tên trạm, **H cột, chiều cao đốt,
   số đốt (vd "6+1"), số tầng co, vị trí gá chống xoay, kích thước cột (600×600), loại cột (tam giác/vuông),
   đường kính ống cột / thanh giằng, tăng đơ, ma ní trên/dưới, khoá cáp trên/dưới, dây co, bu lông neo,
   móc co, cầu cáp, bảng kích thước móng M0–M4 + hiện trạng, ghi chú khác** (dây co đứt, thân han rỉ…).
   → Cắt `y 0–62 %`, resize rộng 1100, `ImageOps.autocontrast` rồi đọc. Đây là nguồn cho TABLEBia,
   TABLE2, TABLE6, TABLE7, GiaiPhap*.
2. **Bản vẽ tay mặt đứng** — chiều cao từng đốt, cao độ tầng dây, số thứ tự đốt.
3. **Bản vẽ mặt bằng móng** — khoảng cách móng co, hướng.

Đọc xong 3 tờ này rồi mới sinh Data. Số liệu ưu tiên: phiếu > bản vẽ > đếm vạch sơn trên ảnh.

---

## 3. BƯỚC 3 — ĐẶT TÊN VÀ DỰNG KHUNG THƯ MỤC

### 3.1 Tên thư mục (sai là phần mềm crash)
```
<MÃ TRẠM>_<Địa điểm>          vd  HTH00009_Đức Thanh,Hà Tĩnh
Data<MÃ TRẠM>_<Địa điểm>      vd  DataHTH00009_Đức Thanh,Hà Tĩnh
```
- Phần mềm tách tại **dấu `_` đầu tiên** để lấy mã trạm → thiếu `_` = `IndexOutOfRangeException`.
- Chưa có mã CSHT → đặt **mã tạm đúng mẫu 3 chữ + 5 số**, dải 9xxxx (vd `HTH90001`), ghi rõ trong file tổng hợp.
- Mã trạm trong tên thư mục **phải trùng** `Mã trạm:_` trong TABLEBia.

### 3.2 Khung ảnh CỘT DÂY CO — 10 hạng mục (tên con chuẩn, copy nguyên)
```
1.Hình ảnh tổng thể cột anten
    Hình ảnh biển nhà trạm | Hình ảnh mặt đứng cột anten | Hình ảnh thiết bị trên cột
    Hình ảnh tổng thể mặt bằng trạm BTS | Hình ảnh khác tổng thể cột anten
2.Công tác kiểm tra khe hở cấu kiện lắp ghép
    Công tác chuẩn bị kiểm tra khe hở cấu kiện lắp ghép | Công tác kiểm tra khe hở giữa cấu kiện lắp ghép
    Hình ảnh khác công tác kiểm tra khe hở lắp ghép
3.Công tác đo lực căng trong dây co
    Công tác đo lực căng trong dây co móng M1 … M4 | Hình ảnh khác công tác đo lực căng trong dây co
4.Công tác kiểm tra lực siết khóa cáp
    Công tác kiểm tra lực siết ê-cu khóa cáp móng M1 … M4 | Hình ảnh khác công tác kiểm tra lực siết khóa cáp
5.Công tác kiểm tra cường độ bê tông móng
    Công tác kiểm tra cường độ bê tông móng M0 … M4 | Hình ảnh khác công tác kiểm tra cường độ bê tông móng
6.Công tác đo điện trở nối đất hệ thống chống sét
    Công tác chuẩn bị đo điện trở nối đất hệ thống chống sét
    Công tác đo điện trở nối đất hệ thống thoát sét lần 1
    Hình ảnh khác công tác đo điện trở nối đất hệ thống chống sét
7.Công tác đo nghiêng cột anten
    Công tác chuẩn bị đo nghiêng cột anten | Công tác đo độ thẳng đứng của cột anten các vòng
    Công tác đo độ thẳng đứng của cột anten hướng bắc | Hình ảnh khác công tác đo nghiêng cột anten
8.Công tác trèo cao (kiểm tra đường hàn, lực siết ê-cu,..)
    Công tác chuẩn bị trèo cao | Thao tác trèo cao tại chân cột | Thao tác trèo cao tại giữa cột
    Thao tác trèo cao tại đỉnh cột | Hình ảnh khác công tác trèo cao
9.Công tác đo kích thước cấu kiện cột và siêu âm thanh cánh
    Hình ảnh chuẩn bị đo kích thước cấu kiện cột anten | Đo kích thước thanh cánh | Đo kích thước thanh giằng
    Đo kích thước thân cột | Đo kích thước móng cột anten | Đo kích thước tiết diện bu lông neo
    Đo kích thước dây co | Đo kích thước ma ní | Đo kích thước chốt ma ní | Đo kích thước khóa cáp
    Đo kích thước tăng đơ | Đo kích thước móc co | Đo kích thước vòng ốp và bu lông dây co
    Đo kích thước dây tiếp địa | Hình ảnh khác đo kích thước cấu kiện cột anten
10.Hình ảnh dị tật bất thường
    <Cấu kiện> - <tình trạng>  (mỗi dị tật 1 thư mục, ≥2 ảnh) | Hình ảnh khác dị tật bất thường
```

### 3.3 Khung ảnh CỘT TỰ ĐỨNG — 8 hạng mục (bỏ lực căng + khoá cáp, đánh số lại)
```
1.Hình ảnh tổng thể cột anten                       (5 con như dây co)
2.Công tác kiểm tra khe hở cấu kiện lắp ghép
    Công tác kiểm tra khe hở cấu kiện lắp ghép tại Chân cột | … tại Đốt D1 | … tại Đốt D2 | …
    Hình ảnh khác công tác kiểm tra khe hở lắp ghép
3.Công tác kiểm tra cường độ bê tông móng
    Công tác chuẩn bị kiểm tra cường độ bê tông móng | Công tác kiểm tra cường độ bê tông móng
    (hoặc tách "…bê tông móng M1 … Mn" nếu ảnh có nhãn từng móng) | Hình ảnh khác …
4.Công tác đo điện trở nối đất hệ thống chống sét
    Công tác chuẩn bị đo điện trở nối đất hệ thống thoát sét | Công tác đo điện trở nối đất hệ thống thoát sét
    Hình ảnh khác …
5.Công tác đo nghiêng cột anten
    Công tác chuẩn bị kiểm tra độ thẳng đứng của cột anten | Công tác đo độ thẳng đứng của cột anten
    Hình ảnh khác …
6.Công tác trèo cao (kiểm tra đường hàn, lực siết ê-cu,..)   (5 con như dây co)
7.Công tác đo kích thước cấu kiện cột và siêu âm thanh cánh
    Đo kích thước Móng M1 … Mn | Đo kích thước thanh cánh | Đo kích thước thanh giằng
    Đo kích thước tiết diện bu lông neo | Hình ảnh khác đo kích thước cấu kiện cột anten
    (KHÔNG có dây co / ma ní / tăng đơ / khoá cáp / vòng ốp / móc co)
8.Hình ảnh dị tật bất thường                          (như mục 10 dây co)
```
Quy tắc chung: mỗi hạng mục **≥ 2 thư mục công tác + 1 "Hình ảnh khác…"**, số thư mục công tác nên chẵn;
hạng mục không có ảnh vẫn tạo đủ thư mục (rỗng thì bỏ 1 ảnh gần chủ đề nhất "cho có" — xem 4.2).

---

## 4. BƯỚC 4 — NHẶT ẢNH (quy tắc 17/09/2026, người dùng chốt)

### 4.1 Nguyên tắc
1. **COPY, không MOVE** — thư mục ảnh gốc giữ nguyên làm bản lưu.
2. **Toàn bộ ảnh của hạng mục nào → bin "Hình ảnh khác…" của hạng mục đó** (theo dải chỉ số đã ghi ở 1.1).
3. **Mỗi thư mục công tác chỉ đặt 1–2 ảnh đúng chủ đề** (chọn đích danh chỉ số; mục 8/6 trèo cao:
   chân cột = ảnh đốt thấp nhất, đỉnh = đốt cao nhất; mục 9/7: đúng ảnh thước cặp trên cấu kiện đó).
4. Tên file copy: `<Tên trạm>_<số thứ tự 3 chữ số>.jpg` — **giữ đúng 1 quy tắc tên trong cả lô**;
   đổi quy tắc giữa chừng sẽ sinh bản trùng (đã mắc: `Phúc_Đồng_001` vs `Phúc_Đồng_2_001`).
5. Hàm copy phải **idempotent** (`if not exists`) vì copy > 500 ảnh có thể quá 120 s timeout → chạy lại được.
6. Video `.mp4` → "Hình ảnh khác tổng thể cột anten".

### 4.2 Hạng mục không có ảnh đúng chủ đề (đợt khảo sát thường thiếu 3,4,5,6,7)
- Vẫn tạo đủ thư mục; bỏ **1 ảnh gần chủ đề nhất** vào mỗi thư mục công tác (lực căng ← ảnh cáp tại móng;
  khoá cáp ← ảnh khoá cáp; bê tông ← ảnh cổ móng; điện trở ← ảnh dây tiếp địa/chân cột; nghiêng ← ảnh cột toàn thân).
- **BÁO người dùng** danh sách hạng mục dùng ảnh "cho có" trong file tổng hợp.

### 4.3 Mục dị tật = nguồn của mọi cột "Đánh giá"
- Tên thư mục **đúng câu sẽ ghi trong Data**: `Mặt bích nối đốt - Han rỉ nặng, thiếu mỡ bảo dưỡng`,
  `Cáp thép dây co - Đứt tại vị trí móc neo`, `Móng co M1-M4 - Đất và cây cỏ phủ lấp cổ móng`,
  `Thoát sét cho cáp thép dây co - Chưa có dây thoát sét`, `Thân cột - Thanh cánh, thanh giằng han rỉ nặng`…
- Mỗi thư mục ≥ 2 ảnh minh chứng. Không bịa dị tật không có ảnh/phiếu.

---

## 5. BƯỚC 5 — SINH 50 FILE DATA (khung DNG cho dây co, khung DBN/NDH cho tự đứng)

### 5.1 Danh sách 50 file (đủ tên, không thừa thiếu)
```
TABLEBia  TABLE2  TABLE3  TABLE4  TABLE5  TABLE6  TABLE7_Duoi  TABLE7_Tren  TABLE8_Duoi  TABLE8_Tren
TABLE9  TABLE10  TABLE11  TABLE115G  TABLE12  TABLE12_V0  TABLE12_V1  TABLE12_V2  TABLE12_V3
TABLE12_ChanCot  TABLE12_DinhCot  TABLE12_HuongBac
TABLECaoDoDayCo  TABLECaoDoDayCo5G  TABLECaoDoDayCoGiaCo
TABLECanhCanhCanh  TABLECanhCanhCanh5G  TABLECanhCanhCanhGiaCo
TABLECanhGocCanh  TABLECanhGocCanh5G  TABLECanhGocCanhGiaCo
TABLEMsTower  TABLEMsTower5G  TABLEMsTowerGiaCo  TABLEToaDoMstower  TABLEToaDoMstowerGiaCo
ChieuCaoNhaTram  LoaiDayCo  LoaiKhoaCap  LoaiMayDo  MongNoiChung  SoAnten
ThietKeLucCangTruocDayCo  NoiDung5G  NoiDungGiaCo  DanhSachThietBi5G
GiaiPhapKetCauThan1  GiaiPhapKetCauThan2  GiaiPhapketCauMong  (+ DinhHuongDanhGia — file ghi chú riêng)
```
Định dạng chung: UTF-8 không BOM, không CRLF; bản ghi phân tách `@`, trường phân tách `_`;
xuống dòng chỉ được nằm **bên trong** một trường mô tả nhiều dòng.

### 5.2 TABLEBia — 17 khoá, đúng thứ tự, trường số phải là SỐ
```
@Địa điểm:_<xã>,<tỉnh>@Mã trạm:_<MÃ>@Loại cột:_Dây co|Tự đứng@Chiều cao cột (m):_45
@Kích thước thân cột:_0.6x0.6@Vị trí đặt:_Dưới đất|Trên mái@Bê tông móng:_B15@Số móng co:_4|0
@Số chân cột:_3|4@Chiều cao đốt (m):_6@Số tầng dây co:_5|0@Số đốt:_7@Vị trí có gá cx (Tầng):_0
@Đốt trên cùng (m):_3@Đốt dưới cùng (m):_6@Phiên bản phần mềm:_2.9.0@Dạng địa hình:_Đồng bằng: TCAT=3
```
- `Vị trí có gá cx (Tầng)` = **số tầng có gá chống xoay, 0 = không** (form ghi "0=không"). Ghi chữ → crash.
- `Mã trạm` không rỗng. `Dạng địa hình`: `Đồng bằng: TCAT=3` | `Đồi núi: TCAT=2` | `Đỉnh núi: …`.
- Tự đứng: `Số móng co:_0`, `Số tầng dây co:_0`, `Kích thước thân cột` = bề rộng chân.

### 5.3 Bảng số trường / số dòng / nguồn — DÂY CO (mẫu `KD2026\DNG`, 3 chân)

| File | Số trường | Số dòng | Mẫu 1 bản ghi | Nguồn giá trị |
|---|---|---|---|---|
| TABLE2 | 4 | M0..M4 + Bu lông neo + Móc co = 7 | `@Móng M1_1.84x0.43x0.60_- <đánh giá>_- <đề xuất>` | Kích thước: phiếu; đánh giá: ảnh |
| TABLE3 bê tông | 19 | 5 (M0..M4) | `@Móng M0_<16 số 28–42>_<TB 2 số lẻ>_90` | Khung chuẩn; trường cuối = 90 |
| TABLE4 thoát sét | 4 | 4 | `@Thoát sét cho kim thu sét_Cáp đồng trần D50_- …_- …` | Ảnh; dây co thêm dòng "Thoát sét cho cáp thép dây co" |
| TABLE5 điện trở | 4 | 3 | `@5.10_10_Đạt yêu cầu_` | Khung chuẩn 2.4–8.6 Ω |
| TABLE6 đốt | **7** | = số đốt | `@Đốt 1_0.6x0.6x6_D60x4.0_L1: 4.0\nL2: 3.9\nL3: 4.1_D18_- <đánh giá>_- <đề xuất>` | KT: phiếu; L: khung 3.7–4.3 |
| TABLE7_Duoi = _Tren | 4 | **13 dòng cố định** | `@Tăng đơ_D22_- …_- …` | Tên dòng: mục 5.5 |
| TABLE8_Duoi = _Tren | 8 | = số tầng | `@1_T1_38.5__41.2__36.7_` | Khung 33–44 kN (3 dây) |
| TABLE9 | 9 | = số tầng | `@T1_600_700_635_X_648_X_612_X` | Khung 605–695 |
| TABLE10 | 5 | 1 + (số đốt − 1) | `@Đốt 1-2_18-M20_<3_- …_- …` | Ảnh; số bu lông nếu có |
| TABLE11 | 5 | theo ảnh | `@43.50_2G 900_2580x262x116_25.3_3` | Đếm anten trong ảnh; cuối là `@3.0-43.5_FEEDER 7/8''___6` |
| TABLE12 (+V0..V3) | 4 | 4 vòng × 3 điểm | `@Vòng 0-1_500.000_100.346_1.000` | Dựng hình tam giác cạnh W, lệch đỉnh H/600 |
| TABLE12_ChanCot/DinhCot/HuongBac | 4 | 1 | `@Chân cột_500.000_100.000_1.000` / `@HƯỚNG BĂC_500.000_120.000_1.000` | |
| TABLECanhGocCanh = CanhCanhCanh (+GiaCo) | 3 | 4 | `@1__@2__@3__@4__` | Khung rỗng |
| TABLEToaDoMstower (+GiaCo) | 4 | 4 | `@MóngM1___@MóngM2___@MóngM3___@MóngM4___` | Khung rỗng |
| TABLECaoDoDayCo (+5G,GiaCo), TABLEMsTower*, *5G còn lại | – | – | `@` | Rỗng (giống DNG) |
| TABLE115G | 5 | = TABLE11 | copy TABLE11 | |
| File đơn | | | `LoaiDayCo=Cáp thép mạ kẽm D12`, `LoaiKhoaCap=Khóa cáp D12`, `LoaiMayDo=C380`, `MongNoiChung=M1 - M4`, `ChieuCaoNhaTram=0`, `SoAnten=<tổng>`, `ThietKeLucCangTruocDayCo=Dưới đất @45m @0.6x0.6x0.6`, `NoiDung5G/NoiDungGiaCo/DanhSachThietBi5G` rỗng | |

Cột 4 chân: TABLE8 = 10 trường, TABLE9 = 11 trường (4 cặp giá trị), TABLE12 mỗi vòng 4 điểm.

### 5.4 Khác biệt khi là TỰ ĐỨNG (mẫu `DBI-POTECO\DBN00209_2`, `NDH00002`)

| File | Tự đứng |
|---|---|
| TABLE2 | `Móng M1..Mn` (n = số chân) + `Bu lông neo`; **không có M0, không có Móc co** |
| TABLE3 | `Móng M1..Mn` (trường cuối 0 hoặc 90) |
| TABLE4 | 4 dòng: kim thu sét / thiết bị treo / chân cột / **phòng máy** |
| TABLE6 | **3 trường**: `@Đốt 1_Cấu tạo: 1.0x1.0x6; thanh cánh V100x10; thanh xiên …; thanh ngang …; thanh phân giàn ….\n- Thanh cánh …\n- Thanh giằng …\n- Bu lông …_- Không` |
| TABLE7_Duoi = _Tren | **3 dòng**: Bản định vị chân cột / Giá treo anten / Kim thu sét (không bu lông neo, không mặt bích bịt, không monopole) |
| TABLE8, TABLE9, TABLECaoDoDayCo*, TABLECanh*, LoaiDayCo, LoaiKhoaCap, ThietKeLucCangTruocDayCo | `@` hoặc rỗng |
| TABLE10 | Chân cột `16-M40` + `Đốt i-(i+1)` `88-M20, 172-M18` … |
| TABLE12 | 4 vòng × 4 điểm hình vuông, cạnh = bề rộng cột tại cao độ vòng (thu dần) |
| Bia | `Số móng co:_0`, `Số tầng dây co:_0` |
| GiaiPhap* | dùng mẫu câu tự đứng trong `01_TaoDataMau.md` (tiết diện thu nhỏ dần, thép V, bản ghép) |

### 5.5 TABLE7 dây co — 13 dòng CỐ ĐỊNH (thứ tự và chính tả y hệt)
```
Bản định vị chân cột · Tăng đơ · Ma ní đầu dưới · Ma ní đầu trên · Khóa cáp đầu dưới · Khóa cáp đầu trên
Vòng ốp móc dây co và bu lông vòng ốp dây co · Dây co · Giá chống xoay · Giá treo anten · Kim thu sét
Mặt bích bịt đầu cột · Ống monopole
```
Cột giàn (không monopole) → dòng "Ống monopole" ghi `- Không có (cột dạng giàn, không phải monopole)._- Không`.

### 5.6 Cách viết cột "Đánh giá" và "Đề xuất" (không bao giờ để trống hay "chưa có số liệu")
- Có dị tật trong ảnh/phiếu → mô tả đúng mức: *han rỉ nhẹ / nặng, thiếu mỡ, bong tróc sơn, ngập nước,
  phủ đất, cây cỏ rậm, đứt sợi, tuột khoá, vật liệu che lấp*.
- Không thấy dị tật → câu "sạch": *không đứt gãy, không cong vênh, không han rỉ; bu lông đủ ê cu, có mỡ; khe hở < 3 mm;
  bê tông cổ móng không nứt vỡ; nền đất không lún, xói*.
- Đề xuất theo từ khoá: han rỉ nhẹ → đánh rỉ, sơn; **nặng → thay thế**; thiếu mỡ → bôi mỡ; thiếu ê cu → bổ sung;
  ngập nước → bơm cạn, tôn nền, đắp bờ; phủ đất/cây cỏ → đào, phát quang, đổ bê tông chống cỏ; đứt cáp → thay đoạn cáp,
  làm lại đầu cáp, căng chỉnh lại; không có dây thoát sét → bổ sung D50.
- Mức "nặng" phải xuất hiện đồng thời ở: TABLE6 đốt tương ứng, TABLE10 mối nối, mục dị tật, DinhHuongDanhGia.

### 5.7 Khung chuẩn cho bảng số đo (ghi rõ trong `DinhHuongDanhGia.txt` là giá trị khung, thay khi có số đo thật)
- Bê tông: 16 lần bắn 28–42, trung bình 2 số lẻ, tuổi 90.
- Điện trở: 3 lần 2.4–8.6 Ω, ngưỡng 10, "Đạt yêu cầu".
- Lực căng: 33–44 kN mỗi dây. Lực siết khoá cáp: 605–695 trong khoảng 600–700.
- L1/L2/L3 chiều dày ống: 3.7–4.3 mm.
- TABLE12: R = W/√3 (tam giác) hoặc W/√2 (vuông); 4 vòng tại z = 1.0, H/3, 2H/3, H−0.5; tâm dịch dần
  đến e = H/600 ở đỉnh (< [H/400] → Đạt); chân cột (500,100,1.0); hướng bắc (500,120,1.0).

---

## 6. BƯỚC 6 — NGHIỆM THU TỰ ĐỘNG (bắt buộc trước khi báo xong)

1. **Tên thư mục**: 3 cấp đều `<MÃ>_<Địa điểm>` / `Data<MÃ>_<Địa điểm>`; mã trùng Bia.
2. **Bia**: 17 khoá đúng thứ tự (so với `DNG00023`); các trường số parse được float/int.
3. **Số trường từng bản ghi** khớp bảng 5.3/5.4; **số dòng** khớp Bia.
4. **Tên dòng TABLE7** đúng 13 (dây co) / 3 (tự đứng).
5. **Danh sách file** = 50 (+DinhHuongDanhGia) — so với thư mục Data mẫu.
6. **Ảnh**: tổng ảnh gốc = tổng ảnh trong các bin "khác"; không thư mục công tác rỗng; mỗi hạng mục ≥ 2 ảnh.
7. `grep -r "CHƯA CÓ\|TODO\|X_X"` trong Data = 0 kết quả (trừ file 5G/GiaCo rỗng).
Script: mục 8.3. Có lệch → sửa rồi chạy lại, không giao khi còn dòng "KHAC".

---

## 7. BƯỚC 7 — FILE TỔNG HỢP `00_TONG HOP LO ….md`
Bắt buộc có: bảng thông số 5–7 cột (H, đốt, tầng, gá CX, phụ kiện), bảng kích thước móng, dị tật chính từng trạm,
bảng "Data đã làm đầy — nguồn", và mục **CẦN BỔ SUNG**: mã CSHT tạm, số liệu khung chuẩn, hạng mục dùng ảnh "cho có",
trường đọc không chắc trên phiếu (ghi "CẦN XÁC NHẬN").

---

## 8. SCRIPT MẪU (đã chạy thật, sửa đường dẫn là dùng)

### 8.1 Contact sheet (PIL)
```python
from PIL import Image,ImageDraw,ImageFont,ImageOps
import os,glob
SRC=r"<thư mục ảnh phẳng>"; OUT=r"<thư mục outputs>/cs"; os.makedirs(OUT,exist_ok=True)
TW,TH,BH,COLS,ROWS=300,400,46,4,4
F=ImageFont.truetype("DejaVuSans-Bold.ttf",22)
fs=sorted(glob.glob(os.path.join(SRC,"*.jpg")))
for k in range(0,len(fs),COLS*ROWS):
    sh=Image.new("RGB",(COLS*TW,ROWS*(TH+BH)),"black"); dr=ImageDraw.Draw(sh)
    for j,f in enumerate(fs[k:k+COLS*ROWS]):
        r,c=divmod(j,COLS); x,y=c*TW,r*(TH+BH); im=Image.open(f); w,h=im.size
        sh.paste(ImageOps.fit(im,(TW,TH)),(x,y))
        sh.paste(im.crop((int(w*.5),int(h*.955),w,h)).resize((TW,BH)),(x,y+TH))   # dòng nhãn GPS đáy ảnh
        dr.rectangle([x+2,y+2,x+54,y+30],fill="black"); dr.text((x+6,y+4),str(k+j+1),fill=(255,220,0),font=F)
    sh.save(f"{OUT}/T_{k//(COLS*ROWS)+1:02d}.jpg",quality=78)
```

### 8.2 Dựng khung + copy ảnh (idempotent)
```python
import os,shutil,glob
FRAME={ "1.Hình ảnh tổng thể cột anten":[...], ... }           # mục 3.2 hoặc 3.3
POOL={H1:[50,51,52,...], H8:range(61,111), H9:range(1,50)}    # chỉ số ảnh → hạng mục (bin "khác")
PICK={(H1,"Hình ảnh mặt đứng cột anten"):[53,55], (H8,"Thao tác trèo cao tại đỉnh cột"):[64,65], ...}
def cp(src,dst):
    if not os.path.exists(dst): shutil.copy2(src,dst)
fs=sorted(glob.glob(os.path.join(SRC,"*.jpg"))); pre=TEN.split(",")[0].replace(" ","_")
for hm,subs in FRAME.items():
    for s in subs: os.makedirs(os.path.join(PHOTO,hm,s),exist_ok=True)
for (hm,sub),idx in PICK.items():
    for i in idx: cp(fs[i-1],os.path.join(PHOTO,hm,sub,f"{pre}_{i:03d}.jpg"))
for hm,idx in POOL.items():
    for i in idx: cp(fs[i-1],os.path.join(PHOTO,hm,KHAC[hm],f"{pre}_{i:03d}.jpg"))
```

### 8.3 Nghiệm thu cấu trúc so với thư mục mẫu
```python
import os,glob
def prof(p):
    r={}
    for fp in glob.glob(os.path.join(p,"TABLE*.txt")):
        recs=[x for x in open(fp,encoding="utf-8").read().split("@") if x.strip()]
        r[os.path.basename(fp)[:-4]]=(len(recs),sorted({len(x.split("_")) for x in recs}) or [0])
    return r
MAU=prof(r"C:\Users\AD\Downloads\KD2026\DNG\DNG00023\DataDNG00023_Hải Châu,Đà Nẵng")   # dây co
# MAU=prof(r"...\DBI-POTECO\DBN00209_2\DataDBN00209_2")                                  # tự đứng
for t in os.listdir(DUAN):
    P=os.path.join(DUAN,t,"Data"+t)
    if not os.path.isdir(P): continue
    assert "_" in t and t.split("_")[0] in open(os.path.join(P,"TABLEBia.txt"),encoding="utf-8").read()
    for k,(n,fields) in prof(P).items():
        if k in MAU and MAU[k][1]!=[0] and not set(fields)<=set(MAU[k][1]+[0]): print("KHAC",t,k,fields,MAU[k][1])
```

---

## 9. CÁC LỖI ĐÃ MẮC — ĐỪNG LẶP LẠI

| Lỗi | Hậu quả | Cách tránh |
|---|---|---|
| Tên thư mục không có `_` (chỉ địa điểm) | Phần mềm crash `IndexOutOfRangeException` ở "Thông tin công trình" | Luôn `<MÃ>_<Địa điểm>`; chưa có mã thì mã tạm 9xxxx |
| `Vị trí có gá cx (Tầng):_Không có` | Crash (trường phải là số) | 0 = không có |
| `Mã trạm:_` rỗng | Crash / mất mã trong báo cáo | Không bao giờ rỗng |
| Ghi "CHƯA CÓ SỐ LIỆU" vào cột Đánh giá | Người dùng bắt lỗi "làm đầy data" | Đánh giá từ ảnh + phiếu; số đo dùng khung chuẩn |
| Tự đặt tên dòng TABLE7 ("Cáp thép dây co", "Cầu cáp") | Sai khung 13 dòng | Copy tên chuẩn mục 5.5 |
| Đổi quy tắc tên file copy giữa chừng | Ảnh trùng bản | 1 quy tắc cho cả lô; script idempotent |
| Copy >500 ảnh trong 1 lệnh | Timeout 120 s, làm dở | Chia theo trạm; `if not exists` để chạy tiếp |
| Coi tờ "Đốt 3 (2)" là panel thứ 2 | Sai số đốt | Đọc tiêu đề tờ (có thể là "đài sàn") |
| Không đối chiếu với thư mục mẫu trước khi giao | Cả lô không mở được | Chạy 8.3 với DNG (dây co) / DBN (tự đứng) |
