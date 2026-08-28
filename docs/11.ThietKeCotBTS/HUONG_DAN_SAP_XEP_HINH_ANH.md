# Hướng dẫn sắp xếp hình ảnh kiểm định cột BTS (A → Z)

> Tài liệu quy trình chuẩn (SOP) để bất kỳ người/trợ lý mới nào cũng sắp xếp được thư mục hình ảnh của dự án mà **không cần đào tạo lại**.
> Nguyên tắc xuyên suốt: **ưu tiên đọc TÊN FILE, hạn chế mở ảnh** để tiết kiệm thời gian và token.

---

## 0. Nguyên tắc vàng (đọc trước khi làm)

1. **Tên file là nguồn thông tin chính.** Nếu tên ảnh đã có tên cấu kiện/vị trí (ví dụ `Móng M1`, `Đốt D6`, `Ma ní đầu dưới Móng M4`, `Thoát sét cho chân cột`) → phân loại NGAY theo tên, **không cần mở ảnh**.
2. **Chỉ mở ảnh khi bắt buộc:** khi tên file chỉ có dấu thời gian mà không có ghi chú (ví dụ `@15@19@06@--0--.jpg`), hoặc khi cần kiểm tra chất lượng.
3. **Không bao giờ xóa ảnh.** Chỉ tạo mới / đổi tên / di chuyển thư mục. Ảnh thừa để lại trong "Hình ảnh khác".
4. **Luôn giữ thư mục "Hình ảnh khác"** — không xóa nó trong bất kỳ trường hợp nào.
5. **Số thư mục chứa ảnh của mỗi hạng mục phải là số chẵn** (xem Mục 5, 8 để biết cách xử lý khi lẻ).

---

## 1. Cấu trúc một trạm

Mỗi trạm (ví dụ `HDG00046_Tân Kỳ,Hải Phòng`) gồm **2 thư mục con**:

- **Thư mục ảnh** (trùng tên trạm): chứa ảnh hiện trường, chia theo các hạng mục kiểm định đánh số 1–10.
- **Thư mục Data** (`Data<mã trạm>_user...`): các file `TABLE*.txt` — số liệu khảo sát xuất từ phần mềm.

### Đọc thông số trạm từ file `TABLEBia.txt`
File này cho biết các con số cần cho việc chia thư mục:

| Trường | Ý nghĩa | Dùng để |
|---|---|---|
| `Số đốt` | Tổng số đốt cột | Chia thư mục Mục 2 (khe hở) |
| `Số móng co` | Số móng dây co | Chia thư mục Mục 3, 4 |
| `Số tầng dây co` | Số tầng dây | Đối chiếu cấu kiện dây co |
| `Loại cột` | Dây co / tự đứng / monopole | Xác định hạng mục áp dụng |

> ⚠️ Nếu **số liệu khai báo lệch với ảnh thực tế** (ví dụ khai 8 đốt nhưng ảnh chỉ chụp tới D6) → **ưu tiên ảnh thực tế** (xem Mục 2).

### Quy ước tên file ảnh
- Ký tự `@` ngăn cách, phần đầu là **nội dung/cấu kiện**, phần sau là **giờ chụp**.
  Ví dụ: `Ma ní đầu dưới Móng M4@14@58@07@--0--.jpg`
- Đuôi `--1--` = **ảnh chính/đại diện** (thường có ghi chú, chọn làm ảnh đầu).
- Đuôi `--0--` = ảnh phụ (chụp thêm góc khác).

---

## 2. Quy tắc sắp xếp TỪNG hạng mục

### Mục 1 — Hình ảnh tổng thể cột anten
- Mỗi thư mục con (biển nhà trạm, mặt bằng trạm BTS, thiết bị trên cột…) **phải có ít nhất 1 ảnh đúng nội dung** với tên thư mục.
- Nếu thiếu → **nhặt bù từ "Hình ảnh khác tổng thể cột anten"** (các ảnh này thường chỉ có tên là giờ chụp → **phải mở xem** để chọn đúng: cửa/biển trạm, toàn cảnh mặt bằng, cụm thiết bị trên đỉnh cột).
- Nếu đã đủ → **giữ nguyên**.

### Mục 2 — Kiểm tra khe hở cấu kiện lắp ghép
- Xác định số đốt, sau đó tạo **2 thư mục chuẩn bị** (khe hở **dưới cùng** và **trên cùng**), giữ nguyên "Hình ảnh khác".
- **Đặt tên theo ĐỐT CÓ ẢNH THỰC TẾ**, không theo số đốt khai báo:
  - Thư mục dưới: `Công tác chuẩn bị kiểm tra khe hở cấu kiện lắp ghép đốt 1-2` ← ảnh `Đốt D1*`
  - Thư mục trên: `Công tác chuẩn bị kiểm tra khe hở cấu kiện lắp ghép đốt 5-6` ← ảnh `Đốt D6*`
  - Đối với các thư mục trước đó là thư mục mẫu mặc định không đúng đúng nên không có ảnh thì cứ xoá hẳn đi.
  - (Nếu cột có ảnh tới đốt khác thì đổi số cho khớp, luôn giữ **2 thư mục = số chẵn**.)
- Ảnh không thuộc đốt nào (ví dụ `Chân cột*`) → để lại "Hình ảnh khác".

### Mục 3 — Đo lực căng trong dây co
- Đếm số móng **theo ảnh có trong "Hình ảnh khác"** (dựa vào tên `Móng Mx`).
- Mỗi móng tạo 1 thư mục: `Công tác chuẩn bị đo lực căng trong dây co Móng M1`, `... Móng M2`, …
- Đổi tên thư mục "Công tác chuẩn bị…" hiện có thành "… Móng Mx" tương ứng, nhặt ảnh từng móng vào đúng thư mục.
- Đối với các thư mục trước đó là thư mục mẫu mặc định không đúng đúng nên không có ảnh thì cứ xoá hẳn đi.

### Mục 4 — Kiểm tra lực siết khóa cáp
- Làm **giống Mục 3**, tên gốc: `Công tác chuẩn bị kiểm tra lực siết ê-cu khóa cáp Móng Mx`.
- Đối với các thư mục trước đó là thư mục mẫu mặc định không đúng đúng nên không có ảnh thì cứ xoá hẳn đi.

### Mục 5 — Kiểm tra cường độ bê tông móng
- Cũng phân theo móng như Mục 3/4: `Công tác chuẩn bị kiểm tra cường độ bê tông móng Móng Mx`.
- **Xử lý số lẻ:** nếu số móng lẻ → tách **1 móng** thành cặp `Công tác chuẩn bị …` + `Công tác đo …` để tổng số thư mục thành chẵn.

### Mục 6 — Đo điện trở nối đất / hệ thống thoát sét
- Chia theo **VỊ TRÍ ĐO**, mỗi vị trí = 1 "Lần": `Công tác đo điện trở nối đất hệ thống thoát sét Lần 1`, `… Lần 2`, …
  - Ví dụ: Lần 1 = chân cột, Lần 2 = kim thu sét, Lần 3 = thiết bị treo trên cột.
- Nhặt ảnh theo tên `Thoát sét cho …` vào đúng "Lần".

### Mục 7 — Đo nghiêng cột anten
- Chia theo **từng vòng đo**: `Đo tại Chân cột`, `Đo tại đỉnh cột`, vòng `0-1`, `1-2`, …
- Số thư mục chứa ảnh phải **chẵn**.
- ⚠️ Nhiều trạm **không có** hạng mục này → nếu không tồn tại thì **bỏ qua**.

### Mục 8 — Trèo cao (kiểm tra đường hàn, lực siết ê-cu…)
- Nhặt ảnh vào **3 vị trí trèo** đang có: chân cột / giữa cột / đỉnh cột.
- Thư mục nào **không có ảnh thì xóa**; đảm bảo số ảnh chẵn.
- Nếu mỗi vị trí chỉ có 1 ảnh và **không có kho ảnh để bù** → **giữ nguyên 3 thư mục** (không ép chẵn được vì không có ảnh bù).

### Mục 9 — Đo kích thước cấu kiện & siêu âm thanh cánh
- Mỗi thư mục cấu kiện **nhặt thêm ảnh từ "Hình ảnh khác đo kích thước…"** sao cho **khớp tên cấu kiện**:
  - `Ma ní*` → `Đo kích thước ma ní`
  - `Tăng đơ*` → `Đo kích thước tăng đơ`
  - `Dây co*` → `Đo kích thước vòng ốp và bu lông dây co`
  - `Móng M*` (móng thuần) → `Đo kích thước móng cột anten`
- Ảnh không có thư mục cấu kiện tương ứng (ví dụ `Khóa cáp đầu dưới Móng M4`) → **để lại "Hình ảnh khác"**.

### Mục 10 — Hình ảnh dị tật bất thường
- **Giữ nguyên.** Tên thư mục/ảnh đã mô tả lỗi (han rỉ, sơn bong tróc, ko mỡ bd…). Dùng để lập bảng thống kê dị tật, không sắp xếp lại.

---

## 3. Khi nào PHẢI mở ảnh (và cách hạn chế)

| Tình huống | Có cần mở ảnh? | Cách tiết kiệm |
|---|---|---|
| Tên file có tên cấu kiện/vị trí | ❌ Không | Phân loại theo tên |
| Tên file chỉ có giờ chụp (Mục 1 "Hình ảnh khác") | ✅ Có | Chỉ mở 1–2 ảnh ứng viên, không quét cả thư mục |
| Kiểm tra chất lượng (mờ, chụp nhầm) | ✅ Tùy chọn | Chỉ mở ảnh `--1--` đại diện |
| Đối chiếu số đốt/móng | ❌ Không | Đọc `TABLEBia.txt` + tên file |

---

## 4. Cách chạy nhanh bằng script (khuyến nghị)

1. File `reorg.ps1` (logic sắp xếp) + `chay_sap_xep.bat` (bộ chạy) đặt ở gốc thư mục dự án.
2. Mở **File Explorer**, dán đường dẫn `...\chay_sap_xep.bat` vào thanh địa chỉ, Enter.
3. Script tự: tạo thư mục → đổi tên → di chuyển ảnh theo tên file. **Không xóa ảnh.**
4. Với nhiều trạm cùng cấu trúc: có thể nâng script thành **bản tổng quát** (tự dò số đốt/móng/lần từ tên file) để chạy **cả loạt trạm trong 1 lượt**, gần như không tốn token.

> Nếu chạy tay: luôn **Move (di chuyển)**, không Copy, để tránh nhân đôi ảnh.

---

## 5. Checklist kiểm tra sau khi sắp xếp (bắt buộc)

- [ ] Mỗi thư mục con của Mục 1 có ≥ 1 ảnh đúng nội dung.
- [ ] Mục 2, 3, 4, 5, 7: số thư mục chứa ảnh là **số chẵn**.
- [ ] Mỗi thư mục "Chuẩn bị/Đo … Móng Mx" chứa đúng ảnh của móng đó.
- [ ] Mục 6: mỗi "Lần" đúng vị trí đo.
- [ ] Mục 9: ảnh nằm đúng thư mục cấu kiện theo tên.
- [ ] "Hình ảnh khác" vẫn còn (dù có thể rỗng) — **chưa bị xóa**.
- [ ] **Tổng số ảnh trước = sau** (không mất ảnh nào).

---

## 6. Các quyết định chuẩn đã thống nhất (ghi nhớ)

1. Tên đốt/móng đặt **theo ảnh thực tế**, không theo số khai báo nếu lệch.
2. Số lẻ → **tách "Chuẩn bị" + "Đo"** cho phần lẻ để thành chẵn.
3. Hạng mục chỉ có 1 móng → tách thành `Công tác chuẩn bị…` + `Công tác đo…`.
4. Xóa hẳn thư mục không liên quan, **trừ "Hình ảnh khác"**.
5. Không có kho ảnh để bù (Mục 8) → giữ nguyên, không ép chẵn.
6. Mục 7 không tồn tại ở trạm → bỏ qua.
