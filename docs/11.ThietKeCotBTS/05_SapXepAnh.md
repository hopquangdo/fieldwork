# 05 — SẮP XẾP / NHẶT HÌNH ẢNH PHỤ LỤC

> **SOP CHÍNH THỨC (người dùng cấp):** `HUONG_DAN_SAP_XEP_HINH_ANH.md` (cùng thư mục này).
> ĐỌC FILE ĐÓ TRƯỚC. Vài điểm hay quên:
> - **Ảnh đo THEO TỪNG CẤU KIỆN → mỗi cấu kiện 1 thư mục "Công tác đo …"** (vd cường độ
>   bê tông móng có ảnh `Móng M1/M2/M3/M4` → tách "…cường độ bê tông móng M1", "…M2", …
>   MỖI móng 1 thư mục; KHÔNG gộp tất cả vào "chuẩn bị"). Chỉ khi cấu kiện **chỉ có 1 ảnh**
>   mới dùng cặp "Công tác chuẩn bị …" + "Công tác đo/làm …".
> - Số thư mục chứa ảnh mỗi hạng mục là **số chẵn**; hạng mục/cấu kiện lẻ → tách 1 cái
>   thành chuẩn bị + đo cho chẵn (vd trạm chỉ có 1 móng → 2 thư mục).
> - Phân loại theo TÊN FILE trước (đỡ tốn token); chỉ mở ảnh khi tên chỉ có giờ chụp.
> - Không xóa ảnh; luôn giữ "Hình ảnh khác".
>
> **3 TÌNH HUỐNG nhặt ảnh đo kích thước (mục 7) — người dùng chốt:**
> - **TH1 — nhiều ảnh, nhiều cấu kiện** (tên `Móng M1/M2…`, `Đốt D1/D2…`, thanh cánh,
>   thanh giằng, bu lông neo, gá treo, mặt bích…): mỗi cấu kiện 1 thư mục "Đo kích thước
>   <cấu kiện>", nhặt NHIỀU ảnh vào (đừng cắt còn 4), chỉ cần **số chẵn** (dư 1 lẻ → khác).
> - **TH2 — nhiều ảnh nhưng chỉ 1 cấu kiện** (chỉ đo 1 loại): để **"Công tác chuẩn bị …"
>   + "Công tác đo …"** (2 thư mục).
> - **TH3 — chỉ 1 ảnh duy nhất**: vẫn tạo đủ **2 thư mục "Công tác chuẩn bị …" + "Công tác
>   đo …"**, để ảnh vào 1 trong 2 (thư mục kia rỗng — ĐỪNG xoá).
> - **Đặc biệt — không có ảnh nào**: vẫn để ≥2 thư mục (rỗng) để người dùng nhặt bù từ
>   hạng mục khác.
> - Ưu tiên phân loại **theo TÊN FILE trước**, hết cách mới mở ảnh xem.
> - **Cột TỰ ĐỨNG: KHÔNG có ảnh siêu âm thân cột, không có ống monopole** — các ảnh loại
>   này (nếu lỡ có) để ở "Hình ảnh khác", không tạo thư mục đo cho chúng.


> **TRẠM CHUẨN THAM CHIẾU (dây co):** `E:\Bao Cao Kiem Dinh\2025\KD NAN\1307\NAN00145_Quỳ Hợp,Nghệ An`
> Khi sắp xếp ảnh, mở trạm này xem cấu trúc thật trước. Các quy tắc chuẩn rút từ đó:
> 1. Thư mục con chia đến TỪNG VỊ TRÍ/CẤU KIỆN: khe hở → "tại Chân cột" + "Đốt 1-2/2-3/...";
>    lực căng, khóa cáp, bê tông → từng móng ("Công tác kiểm tra cường độ bê tông móng M1",
>    "Đo lực căng trong dây co Móng M1"); đo kích thước → từng tầng dây ("Đo kích thước
>    vòng ốp và bu lông dây co" chứa ảnh "Vòng ốp và bulong Tầng dây 1/2/3"); siêu âm →
>    "01.Hình ảnh siêu âm thanh cánh <c> Đốt D<d>" từng cánh từng đốt.
> 2. Vai trò 2 loại thư mục con:
>    - **Thư mục "công tác ..." (có tên)** = thư mục ĐƯA VÀO PHỤ LỤC. Số ảnh trong mỗi
>      thư mục phải là SỐ CHẴN — **ưu tiên 4 ảnh; không đủ 4 thì để 2**.
>    - **"Hình ảnh khác ..."** = kho chứa ảnh linh tinh còn lại của hạng mục (giữ nguyên,
>      không đưa vào phụ lục). Khi phân loại: chuyển đủ 4 (hoặc 2) ảnh vào thư mục công tác,
>      phần dư để ở "khác".
>    - Hạng mục KHÔNG có ảnh: vẫn phải đủ **2 thư mục công tác (rỗng) + 1 "Hình ảnh khác"**.
>    - **ẢNH BẢN VẼ TAY (mặt đứng/mặt cắt/mặt bằng — ảnh chụp trang giấy) CHỈ ĐƯỢC
>      NẰM Ở "Hình ảnh khác tổng thể cột anten".** KHÔNG để trong bất kỳ thư mục phụ lục
>      nào của mục 1 (mặt bằng trạm BTS / mặt đứng cột / biển nhà trạm / thiết bị trên cột)
>      vì các thư mục đó đưa vào báo cáo. Nếu thấy ảnh bản vẽ lạc ở đó → CHUYỂN về "khác".
>      (Người dùng nhắc: vd HNM00001 bản vẽ bị để nhầm ở "mặt bằng trạm BTS" — phải move.)
>      Tên bản vẽ có thể là @giờ@phút (giống ảnh thường), số dài, HOẶC có tiền tố **"Móng M0"**
>      (đã gặp: bản vẽ bị đặt tên "Móng M0@..." nằm trong "mặt bằng trạm BTS") → phải MỞ XEM
>      để phân biệt, không dựa vào tên. Bản vẽ = nền giấy trắng, nét bút vẽ cột/mặt cắt/kích
>      thước, thường ghi "HNMxxxxx H=..m" + chiều cao từng đốt. Script nhặt ảnh chỉ move file
>      prefix cấu kiện nên không đụng; nhưng phải QUÉT RIÊNG các ảnh "Móng*" trong mục 1.
>    - **CHIỀU CAO ĐỐT THẬT nằm trên bản vẽ mặt đứng** (vd "đốt 1 5M, đốt 2 5.2M"...) — khi
>      dựng MSTOWER phải đọc số này, ĐỪNG mặc định 6m. TABLE6 "Cao:" nếu có cũng là nguồn tin.
> 3. Tên file = `<Cấu kiện + vị trí>@ <giờ>@<phút>@<giây>@--x--.jpg`
>    (vd "Ma ní đầu trên Tầng dây 1@ 9@40@38@--0--.jpg") — prefix là căn cứ phân loại.
> 4. Data trạm nằm trong các thư mục `Data..._user <tên>ok` (hậu tố ok = đã duyệt),
>    KHÔNG cần thư mục Data chính.

Mục tiêu: thư mục phụ lục ảnh đúng cấu trúc để phần mềm xuất phụ lục không lỗi, không trống.

## Cấu trúc hạng mục theo loại cột

### Dây co — 10 hạng mục (GIỮ NGUYÊN, không chuyển 8)
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

### Tự đứng — 8 hạng mục (bỏ mục 3,4 dây co rồi đánh số lại)
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
Khi chuyển dây co → tự đứng: xóa hạng mục 3–4 cũ; xóa mọi thư mục con dây co
(dây co, móc co, khóa cáp, ma ní, tăng đơ, vòng ốp) trong mục dị tật & đo kích thước.

## Quy tắc thư mục con (QUAN TRỌNG — sai là phần mềm lỗi)

1. **Mỗi hạng mục PHẢI có tối thiểu 2 thư mục công tác + 1 "Hình ảnh khác", kể cả khi
   không có ảnh** (thư mục rỗng vẫn phải tồn tại). Hạng mục 0 thư mục con → phần mềm lỗi.
2. Thư mục con đi theo CẶP: "Công tác chuẩn bị X" + "Công tác kiểm tra/đo X"
   → số thư mục "công tác" mỗi hạng mục là SỐ CHẴN.
3. **Số ảnh mỗi thư mục công tác phải CHẴN: ưu tiên 4 ảnh, không đủ 4 thì 2.**
   Phần ảnh dư để lại trong "Hình ảnh khác" của hạng mục đó.
4. Hạng mục 1 (tổng thể): Hình ảnh biển nhà trạm / mặt đứng / thiết bị trên cột /
   tổng thể mặt bằng trạm BTS.
5. Hạng mục trèo cao: chuẩn bị / tại chân cột / tại giữa cột / tại đỉnh cột (+ bin khác).

## Nhặt ảnh từ "Hình ảnh khác"

Ảnh thường dồn hết vào bin `Hình ảnh khác ...` → phụ lục trống. Phải chuyển ảnh sang
thư mục con đúng tên; bin "khác" chỉ giữ phần dư (hoặc xoá nếu rỗng).

## Tách thư mục theo TỪNG CẤU KIỆN (quy tắc .md của người dùng)

Tên file ảnh mã hoá cấu kiện TRƯỚC dấu `@` đầu tiên: `Móng M2@15@22@49@--0--.jpg`.
Nếu 1 hạng mục có ảnh của nhiều cấu kiện có tên → tách mỗi cấu kiện 1 thư mục:
- Hạng mục đo kích thước: `Đo kích thước Móng M0`, `Đo kích thước Móng M1`, ...,
  `Đo kích thước Bu lông neo` (+ thư mục `Hình ảnh chuẩn bị đo kích thước...`).
- Hạng mục bê tông móng: `Kiểm tra cường độ bê tông Móng M1`, ... (+ thư mục chuẩn bị).
- Hạng mục đo nghiêng: tên file là ĐIỂM ĐO (Toạ độ vòng x-y, Chân cột, Đỉnh cột) —
  KHÔNG phải cấu kiện, để nguyên trong thư mục đo độ thẳng đứng.

## Cấm tuyệt đối

**KHÔNG lấy ảnh trạm khác** (kể cả cắt/che tem GPS) chèn vào trạm này. Chỉ sắp xếp ảnh
của chính trạm. Hạng mục không có ảnh: giữ thư mục khung rỗng và BÁO người dùng danh sách thiếu.

## Kiểm tra sau khi làm

- Mọi hạng mục ≥2 thư mục con? (liệt kê hạng mục <2)
- Còn bin "khác" chứa ảnh chưa nhặt? (trừ bin trèo cao hợp lệ)
- Còn thư mục dây co sót trong trạm tự đứng?
- In bảng đếm ảnh mỗi hạng mục để người dùng thấy hạng mục nào còn trống.
