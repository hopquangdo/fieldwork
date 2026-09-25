# RULE — Quy tắc sắp xếp ảnh phụ lục kiểm định cột BTS

> Quy trình chuẩn để bất kỳ ai cũng sắp xếp được thư mục ảnh của trạm mà không cần đào tạo lại.
> Nguyên tắc xuyên suốt: **ưu tiên đọc TÊN FILE, hạn chế mở ảnh**.

---

## 0. Nguyên tắc vàng (đọc trước khi làm)

1. **Tên file là nguồn thông tin chính.** Nếu tên ảnh đã có tên cấu kiện/vị trí
   (ví dụ `Móng M1`, `Đốt D6`, `Ma ní đầu dưới Móng M4`, `Thoát sét cho chân cột`)
   → phân loại ngay theo tên, **không cần mở ảnh**.
2. **Chỉ mở ảnh khi bắt buộc:** tên file chỉ có dấu thời gian mà không có ghi chú
   (ví dụ `@15@19@06`), hoặc nghi là ảnh bản vẽ tay, hoặc cần kiểm tra chất lượng.
3. **Không bao giờ xóa ảnh.** Chỉ tạo mới / đổi tên / di chuyển thư mục.
   Ảnh thừa để lại trong "Hình ảnh khác".
4. **Luôn giữ thư mục "Hình ảnh khác"** — không xóa nó trong bất kỳ trường hợp nào.
5. **Số thư mục chứa ảnh của mỗi hạng mục phải là số chẵn.**
6. **Số ảnh mỗi thư mục công tác phải chẵn.** Mặc định **giữ full** (nhặt hết ảnh đúng
   nội dung, dư 1 lẻ → "Hình ảnh khác"). Bật `trim_to_prefer` → cắt về 4, dư sang "khác".
7. **Cấm tuyệt đối lấy ảnh trạm khác** (kể cả cắt/che tem GPS) chèn vào trạm này.
   Chỉ sắp xếp ảnh của chính trạm.

### Quy ước tên file ảnh
- Dấu `@` ngăn cách: phần đầu là **nội dung / cấu kiện**, phần sau là **giờ chụp**.
  Ví dụ: `Ma ní đầu dưới Móng M4@14@58@07@--0--.jpg`
- Đuôi `--1--` = ảnh chính / đại diện (thường có ghi chú, chọn làm ảnh đầu).
- Đuôi `--0--` = ảnh phụ (chụp thêm góc khác).

### Thông số trạm — đọc từ file `TABLEBia.txt`
File này nằm trong thư mục Data của trạm (`Data..._user <tên>ok`, hậu tố `ok` = đã duyệt).

| Trường | Ý nghĩa | Dùng để |
|---|---|---|
| Số đốt | Tổng số đốt cột | Chia thư mục Mục 2 (khe hở) |
| Số móng co | Số móng dây co | Chia thư mục Mục 3, 4, 5 |
| Số tầng dây co | Số tầng dây | Đối chiếu cấu kiện dây co |
| Loại cột | Dây co / tự đứng / monopole | Xác định hạng mục áp dụng |

> ⚠️ Nếu số liệu khai báo lệch với ảnh thực tế (ví dụ khai 8 đốt nhưng ảnh chỉ chụp tới D6)
> → **ưu tiên ảnh thực tế**. Tên đốt/móng đặt theo ảnh thật, không theo số khai báo.

> **Trạm chuẩn tham chiếu (dây co):**
> `E:\Bao Cao Kiem Dinh\2025\KD NAN\1307\NAN00145_Quỳ Hợp,Nghệ An` — khi sắp xếp,
> mở trạm này xem cấu trúc thư mục con thật trước để đối chiếu.

> **Lưu ý loại cột:** một số trạm `TABLEBia` ghi "Dây co" nhưng thực tế là tự đứng
> → phải mở ảnh mặt đứng kiểm tra, làm theo loại cột THẬT.

---

## 1. Cấu trúc hạng mục theo loại cột

### Cột dây co — 10 hạng mục (giữ nguyên, không chuyển 8)
```
1.Hình ảnh tổng thể cột anten
2.Công tác kiểm tra khe hở cấu kiện lắp ghép
3.Công tác đo lực căng trong dây co
4.Công tác kiểm tra lực siết khóa cáp
5.Công tác kiểm tra cường độ bê tông móng
6.Công tác đo điện trở nối đất hệ thống chống sét
7.Công tác đo nghiêng cột anten
8.Công tác trèo cao (kiểm tra đường hàn, lực siết ê-cu,..)
9.Công tác đo kích thước cấu kiện cột và siêu âm thanh cánh
10.Hình ảnh dị tật bất thường
```

### Cột tự đứng — 8 hạng mục (bỏ mục 3, 4 dây co rồi đánh số lại)
```
1.Hình ảnh tổng thể cột anten
2.Công tác kiểm tra khe hở cấu kiện lắp ghép
3.Công tác kiểm tra cường độ bê tông móng
4.Công tác đo điện trở nối đất hệ thống chống sét
5.Công tác đo nghiêng cột anten
6.Công tác trèo cao (kiểm tra đường hàn, lực siết ê-cu,..)
7.Công tác đo kích thước cấu kiện cột anten
8.Hình ảnh dị tật bất thường
```

- Cột **tự đứng KHÔNG có:** ảnh siêu âm thân cột, ống monopole, và các cấu kiện dây co
  (dây co / móc co / khóa cáp / ma ní / tăng đơ / vòng ốp). Các ảnh loại này (nếu lỡ có)
  → để ở "Hình ảnh khác", không tạo thư mục đo cho chúng.
- Khi chuyển dây co → tự đứng: xóa hạng mục 3–4 cũ; xóa mọi thư mục con dây co trong
  mục dị tật và mục đo kích thước.

---

## 2. Quy tắc thư mục con (quan trọng — sai là phần mềm xuất phụ lục lỗi)

1. **Mỗi hạng mục phải có tối thiểu 2 thư mục công tác + 1 "Hình ảnh khác", kể cả khi
   không có ảnh** (thư mục rỗng vẫn phải tồn tại). Hạng mục 0 thư mục con → phần mềm lỗi.
2. Thư mục con đi theo **cặp:** "Công tác chuẩn bị X" + "Công tác kiểm tra/đo X"
   → số thư mục "công tác" mỗi hạng mục là số chẵn.
3. **Số ảnh mỗi thư mục công tác phải chẵn.** Mặc định **giữ FULL** — nhặt hết ảnh đúng
   cấu kiện/vị trí vào thư mục (dư 1 ảnh lẻ mới để "Hình ảnh khác"). Nếu bật tham số
   `trim_to_prefer` thì cắt về 4 ảnh/thư mục, phần dư sang "Hình ảnh khác".
4. **Xử lý số lẻ:** hạng mục/cấu kiện lẻ (ví dụ trạm chỉ có 1 móng) → tách 1 cái thành
   cặp "Công tác chuẩn bị …" + "Công tác đo …" cho tổng số thư mục thành chẵn.
5. **Không có kho ảnh để bù** (ví dụ Mục 8, mỗi vị trí chỉ 1 ảnh) → giữ nguyên,
   không ép chẵn được.
6. Thư mục mẫu mặc định sai tên, không có ảnh → **xóa hẳn** (trừ "Hình ảnh khác").

### Vai trò 2 loại thư mục con
- **Thư mục "Công tác …" (có tên cụ thể)** = thư mục đưa vào phụ lục báo cáo.
- **"Hình ảnh khác …"** = kho chứa ảnh linh tinh còn lại của hạng mục (giữ nguyên,
  không đưa vào phụ lục). Khi phân loại: chuyển đủ 4 (hoặc 2) ảnh vào thư mục công tác,
  phần dư để lại ở "khác".

---

## 3. Quy tắc sắp xếp TỪNG hạng mục

### Mục 1 — Hình ảnh tổng thể cột anten
- Các thư mục con: biển nhà trạm / tổng thể mặt bằng trạm BTS / mặt đứng cột anten /
  thiết bị trên cột.
- Mỗi thư mục con **phải có ít nhất 1 ảnh đúng nội dung** với tên thư mục.
- Thiếu → nhặt bù từ "Hình ảnh khác tổng thể cột anten" (các ảnh này thường chỉ có giờ
  chụp → **phải mở xem** để chọn đúng: cửa/biển trạm, toàn cảnh mặt bằng, cụm thiết bị
  trên đỉnh cột). Đã đủ → giữ nguyên.
- **Ảnh bản vẽ tay** (mặt đứng / mặt cắt / mặt bằng — ảnh chụp trang giấy) **chỉ được
  nằm ở "Hình ảnh khác tổng thể cột anten".** Không để trong bất kỳ thư mục phụ lục nào
  của Mục 1. Thấy ảnh bản vẽ lạc ở đó → chuyển về "khác".
  - Bản vẽ hay bị để nhầm ở **"Hình ảnh tổng thể mặt bằng trạm BTS"** — phải kiểm tra
    cả 2 thư mục, thấy thì nhặt về "Hình ảnh khác tổng thể cột anten".
  - Tên bản vẽ có thể là `@giờ@phút` (giống ảnh thường), số dài, hoặc có tiền tố
    `Móng M0` → **phải mở xem** để phân biệt, không dựa vào tên.
  - Dấu hiệu bản vẽ: nền giấy trắng, nét bút vẽ cột / mặt cắt / kích thước, thường ghi
    mã trạm + chiều cao (`H=..m`) và chiều cao từng đốt.
  - **Kiểm tra mã trạm ghi trên tờ giấy** — đề phòng tờ bản vẽ lạc từ trạm khác
    (đã gặp: bản vẽ trạm 00048 lạc vào trạm 00056). Bản vẽ trạm khác → không dùng.
- **Chiều cao đốt thật nằm trên bản vẽ mặt đứng** (ví dụ "đốt 1: 5M, đốt 2: 5.2M"…) —
  khi dựng MSTOWER phải đọc số này, đừng mặc định 6m.

### Mục 2 — Kiểm tra khe hở cấu kiện lắp ghép
- **Mặc định (`mode = "all"`): mỗi đốt 1 thư mục** — ảnh `Đốt Dn*` →
  `Công tác chuẩn bị kiểm tra khe hở cấu kiện lắp ghép đốt {n}`. Đặt tên theo **đốt
  CÓ ẢNH THỰC TẾ**. Số đốt lẻ → tách đốt trên cùng thành cặp chuẩn bị + kiểm tra.
- Chế độ cũ (`mode = "extremes"`): chỉ **2 thư mục cực trị** (`đốt 1-2` + `đốt 6-7`),
  ảnh đốt ở giữa → "Hình ảnh khác".
- Thư mục mẫu mặc định không đúng, không có ảnh → xóa hẳn.
- Ảnh không thuộc đốt nào (ví dụ `Chân cột*`) → để lại "Hình ảnh khác".

### Mục 3 — Đo lực căng trong dây co *(chỉ cột dây co)*
- Đếm số móng theo ảnh trong "Hình ảnh khác" (dựa vào tên `Móng Mx`).
- Mỗi móng 1 thư mục: `Công tác chuẩn bị đo lực căng trong dây co Móng M1`, `… Móng M2`, …
- Đổi tên thư mục "Công tác chuẩn bị…" hiện có thành "… Móng Mx", nhặt ảnh từng móng vào.
- Thư mục mẫu mặc định không có ảnh → xóa hẳn.

### Mục 4 — Kiểm tra lực siết khóa cáp *(chỉ cột dây co)*
- Làm **giống Mục 3**, tên gốc: `Công tác chuẩn bị kiểm tra lực siết ê-cu khóa cáp Móng Mx`.
- Thư mục mẫu mặc định không có ảnh → xóa hẳn.

### Mục 5 (dây co) / Mục 3 (tự đứng) — Kiểm tra cường độ bê tông móng
- Phân theo móng như Mục 3/4: `Công tác chuẩn bị kiểm tra cường độ bê tông móng Móng Mx`.
- **Số móng lẻ** → tách 1 móng thành cặp "Công tác chuẩn bị …" + "Công tác đo …"
  để tổng số thư mục thành chẵn.

### Mục 6 (dây co) / Mục 4 (tự đứng) — Đo điện trở nối đất / hệ thống thoát sét
- Chia theo **vị trí đo**, mỗi vị trí = 1 "Lần":
  `Công tác đo điện trở nối đất hệ thống thoát sét tại Lần 1`, `… Lần 2`, …
  - Ví dụ: Lần 1 = chân cột, Lần 2 = kim thu sét, Lần 3 = thiết bị treo trên cột.
- Nhặt ảnh theo tên `Thoát sét cho …` vào đúng "Lần".

### Mục 7 (dây co) / Mục 5 (tự đứng) — Đo nghiêng cột anten
- Chia theo **từng vòng / điểm đo**: `Đo tại Chân cột`, `Đo tại đỉnh cột`,
  vòng `0-1`, `1-2`, …
- Tên file ở đây là **điểm đo** (Toạ độ vòng x-y, Chân cột, Đỉnh cột), không phải cấu kiện
  → để nguyên trong thư mục đo độ thẳng đứng.
- Số thư mục chứa ảnh phải chẵn.
- ⚠️ Nhiều trạm **không có** hạng mục này → nếu không tồn tại thì **bỏ qua**.

### Mục 8 (dây co) / Mục 6 (tự đứng) — Trèo cao (kiểm tra đường hàn, lực siết ê-cu…)
- Nhặt ảnh vào **3 vị trí trèo** đang có: chân cột / giữa cột / đỉnh cột.
- Thư mục nào không có ảnh thì xóa; đảm bảo số ảnh chẵn.
- Nếu mỗi vị trí chỉ có 1 ảnh và **không có kho ảnh để bù** → giữ nguyên 3 thư mục
  (không ép chẵn được).

### Mục 9 (dây co) — Đo kích thước cấu kiện & siêu âm thanh cánh
- Giữ nguyên các thư mục siêu âm dạng `NN.Hình ảnh siêu âm thanh cánh <cánh> Đốt D<đốt>`.
- Mỗi cấu kiện 1 thư mục "Đo kích thước <cấu kiện>", nhặt ảnh khớp tên cấu kiện:
  | Ảnh tên bắt đầu bằng | → Thư mục |
  |---|---|
  | `Ma ní*` | Đo kích thước ma ní |
  | `Tăng đơ*` | Đo kích thước tăng đơ |
  | `Vòng ốp*` / `Bu lông dây co*` / `Dây co*` | Đo kích thước vòng ốp và bu lông dây co |
  | `Móng M*` (móng thuần) | Đo kích thước móng cột anten |
  | `Thanh cánh*` | Đo kích thước thanh cánh |
  | `Thanh giằng*` | Đo kích thước thanh giằng |
  | `Bu lông neo*` | Đo kích thước tiết diện bu lông neo |
  | `Thân cột*` | Đo kích thước thân cột |
  | `Móc co*` | Đo kích thước móc co |
  | `Chốt ma ní*` | Đo kích thước chốt ma ní |
- Ảnh không có thư mục cấu kiện tương ứng (ví dụ `Khóa cáp đầu dưới Móng M4`)
  → **để lại "Hình ảnh khác"**.

### Mục 7 (tự đứng) — Đo kích thước cấu kiện cột anten
- Cột tự đứng **không có siêu âm, không có cấu kiện dây co**.
  | Ảnh tên bắt đầu bằng | → Thư mục |
  |---|---|
  | `Móng M*` | Đo kích thước móng cột anten |
  | `Thanh cánh*` | Đo kích thước thanh cánh |
  | `Thanh giằng*` | Đo kích thước thanh giằng |
  | `Bu lông neo*` | Đo kích thước tiết diện bu lông neo |
  | `Thân cột*` | Đo kích thước thân cột |
  | `Mặt bích*` / `Gá treo*` | Đo kích thước mặt bích và gá treo |

### Mục 10 (dây co) / Mục 8 (tự đứng) — Hình ảnh dị tật bất thường
- **Giữ nguyên.** Tên thư mục/ảnh đã mô tả lỗi (han rỉ, sơn bong tróc, không mỡ bảo dưỡng…).
  Dùng để lập bảng thống kê dị tật, không sắp xếp lại.

### 3 tình huống nhặt ảnh đo kích thước 
- **TH1 — nhiều ảnh, nhiều cấu kiện:** mỗi cấu kiện 1 thư mục "Đo kích thước <cấu kiện>",
  nhặt **nhiều** ảnh vào (đừng cắt còn 4), chỉ cần **số chẵn** (dư 1 lẻ → để ở "khác").
- **TH2 — nhiều ảnh nhưng chỉ 1 cấu kiện:** để "Công tác chuẩn bị …" + "Công tác đo …"
  (2 thư mục).
- **TH3 — chỉ 1 ảnh duy nhất:** vẫn tạo đủ 2 thư mục "Công tác chuẩn bị …" + "Công tác
  đo …", để ảnh vào 1 trong 2 (thư mục kia rỗng — đừng xoá).
- **Không có ảnh nào:** vẫn để ≥ 2 thư mục rỗng để người dùng nhặt bù sau.

---

## 4. Khi nào PHẢI mở ảnh 

| Tình huống | Có cần mở ảnh? | Cách tiết kiệm |
|---|---|---|
| Tên file có tên cấu kiện / vị trí | ❌ Không | Phân loại theo tên |
| Tên file chỉ có giờ chụp (Mục 1 "Hình ảnh khác") | ✅ Có | Chỉ mở 1–2 ảnh ứng viên, không quét cả thư mục |
| Nghi ảnh bản vẽ tay trong Mục 1 | ✅ Có | Mở xem: nền giấy trắng, nét vẽ → chuyển về "khác" |
| Kiểm tra chất lượng (mờ, chụp nhầm) | ✅ Tùy chọn | Chỉ mở ảnh `--1--` đại diện |
| Đối chiếu số đốt / móng | ❌ Không | Đọc `TABLEBia.txt` + tên file |

---

## 5. Đặt tên cấu kiện khi đổi tên ảnh

Tên cấu kiện suy từ tên thư mục đích:

| Thư mục đích chứa | Tên cấu kiện |
|---|---|
| biển nhà trạm | Biển nhà trạm |
| mặt bằng trạm BTS | Tổng thể mặt bằng trạm BTS |
| mặt đứng | Mặt đứng cột anten |
| thiết bị trên cột | Thiết bị trên cột |
| lực căng / bê tông / lực siết | Móng |
| khe hở | Khe hở đốt |
| điện trở / thoát sét | Thoát sét |
| thẳng đứng / nghiêng | Độ thẳng đứng cột |
| trèo cao | Trèo cao |

---

## 6. Checklist kiểm tra sau khi sắp xếp 

- [ ] Mỗi thư mục con của Mục 1 có ≥ 1 ảnh đúng nội dung.
- [ ] Mục 2, 3, 4, 5, 7: số thư mục chứa ảnh là **số chẵn**.
- [ ] Mỗi thư mục "Chuẩn bị / Đo … Móng Mx" chứa đúng ảnh của móng đó.
- [ ] Mục 6: mỗi "Lần" đúng vị trí đo.
- [ ] Mục 9: ảnh nằm đúng thư mục cấu kiện theo tên.
- [ ] Không còn ảnh bản vẽ tay trong thư mục phụ lục của Mục 1.
- [ ] "Hình ảnh khác" vẫn còn (dù có thể rỗng) — chưa bị xóa.
- [ ] Không còn thư mục dây co sót trong trạm tự đứng.
- [ ] **Tổng số ảnh trước = sau** (không mất ảnh nào).
- [ ] In bảng đếm ảnh mỗi hạng mục để thấy hạng mục nào còn trống, báo người dùng danh sách thiếu.

---

## 6b. Cơ chế tự động hoá tương ứng (profile TOML — xem `PROFILE_SCHEMA.md`)

| Quy tắc | Cơ chế | Khai báo |
|---|---|---|
| TABLEBia ghi "Dây co" nhưng thực tế tự đứng | hạng mục đặc trưng dây co (lực căng / khóa cáp) đều 0 ảnh → chạy profile tự đứng | `_base.toml [[tower_evidence]]` |
| Đầu vào lồng bản sao trạm / ảnh trùng | bỏ bản lồng + ảnh trùng sha1 trong cùng hạng mục, ghi report | `_base.toml [scan]` |
| Tên thư mục con phải đúng SOP | khớp mờ về tên chuẩn, gộp trùng, dựng `ensure`; không khớp → "cần người xem" | `tu_dung.toml [[subfolders]]` |
| Ảnh trong "Hình ảnh khác" chưa được xếp | ảnh ở "khác" vẫn qua rule/vision; chỉ phần còn lại ở "khác" | rule + `[vision] recheck_in` |
| Trèo cao chia chân / giữa / đỉnh theo đốt | đốt k / tổng đốt (ưu tiên số đốt thấy trong ảnh) → 3 vùng đều | `[groups.vitri_dot]` + rule `group_by = ["vitri", "vitri_dot"]` |
| Khe hở: mỗi đốt 1 thư mục, lẻ → cặp rỗng cho đốt cuối | `pairing = "none"` + `odd_fix = "sibling"` | `tu_dung.toml` |
| Bê tông: mỗi móng "chuẩn bị" + "kiểm tra" rỗng | `pairing = "all"` | `tu_dung.toml [[subfolders]]` |
| Cấu kiện chỉ 1 ảnh → giữ ảnh (TH3) | `keep_singletons = true` | `[structure]` |
| Ép chẵn: bỏ ảnh nào | giữ ảnh chính → cùng nhóm ảnh chính → có tên → theo giờ (bỏ muộn; `trim_earliest` bỏ sớm) | `[structure]` |
| Đo kích thước: không ép số thư mục chẵn | `odd_folders_skip` | `[structure]` |

---

## 7. Các quyết định chuẩn đã thống nhất

1. Tên đốt/móng đặt **theo ảnh thực tế**, không theo số khai báo nếu lệch.
2. Số lẻ → **tách "Chuẩn bị" + "Đo"** cho phần lẻ để thành chẵn.
3. Hạng mục chỉ có 1 móng → tách thành "Công tác chuẩn bị…" + "Công tác đo…".
4. Xóa hẳn thư mục không liên quan, **trừ "Hình ảnh khác"**.
5. Không có kho ảnh để bù (Mục 8) → giữ nguyên, không ép chẵn.
6. Mục 7 không tồn tại ở trạm → bỏ qua.
7. Ảnh bản vẽ tay chỉ nằm ở "Hình ảnh khác tổng thể cột anten".
8. Không lấy ảnh trạm khác chèn vào trạm này trong mọi trường hợp.
