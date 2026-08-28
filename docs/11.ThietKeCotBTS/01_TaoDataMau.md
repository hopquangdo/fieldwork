# 01 — TẠO DATA MẪU (TABLE2–TABLE12 + FILE PHỤ)

Mục tiêu: trạm chỉ có `TABLEBia.txt` → tạo đủ ~49 file Data để phần mềm (v2.9.0) chạy được.

## Bước làm

1. **Đọc TABLEBia.txt + các bảng ở TẤT CẢ thư mục Data** — gồm Data chính VÀ từng
   `Data..._user <tên>` (Tâm, chiến, ĐẠI DƯƠNG…). Khảo sát viên chia nhau nhập:
   bảng đo thật thường nằm trong thư mục user (TABLE6/10/11 một người, TABLE12/2/3/4
   người khác), còn Data chính có thể cũ/sai. Lập bảng đối chiếu Bia các nguồn;
   **nếu mâu thuẫn (loại cột/chiều cao/số đốt) → HỎI người dùng chốt, không tự chọn**
   (vụ HNM00056: 3 Bia ghi 54m/45m/36m — bản đúng 36m nằm ở user Tâm).
   Chuẩn của hệ thống (xem trạm mẫu NAN00145): Data nằm TRONG các thư mục
   `Data..._user <tên>ok` — hậu tố "ok" nghĩa là bản đã duyệt, ưu tiên dùng;
   trạm chuẩn thậm chí KHÔNG có thư mục Data chính.
2. **Chọn trạm mẫu gần nhất** (cùng loại cột, gần thông số nhất — xem bảng mẫu trong README).
3. **Copy toàn bộ file Data mẫu → thư mục Data trạm đích** (thường là thư mục `..._user Tâm`
   nếu Bia nằm ở đó), GIỮ NGUYÊN TABLEBia.txt của trạm đích.
4. **Hiệu chỉnh số dòng theo Bia** (quan trọng nhất — sai là phần mềm lỗi):
   - Số tầng dây co n → TABLE8_Duoi/Tren, TABLE9, TABLECaoDoDayCo(+5G,GiaCo),
     TABLECanhCanhCanh, TABLECanhGocCanh: giữ đúng n bản ghi (bản ghi phân tách bằng `@`).
   - Số đốt m → TABLE6 (m đốt), TABLE10 (Chân cột + Đốt 1-2 … Đốt (m-1)-m).
   - Số móng → TABLE2, TABLE3.
   - Số vòng đo nghiêng: giữ TABLE12_V0..V(n-1) khớp số tầng (xóa vòng thừa cả trong TABLE12.txt gộp).
5. **Sửa file thuyết minh**: GiaiPhapKetCauThan1/2 (số đốt, số tầng), GiaiPhapketCauMong.
6. **Kiểm tra không còn tên/địa danh trạm mẫu** sót lại (grep mã trạm cũ).

## Định dạng bảng

- Bản ghi phân tách bằng `@`, trường phân tách bằng `_`. Không có xuống dòng giữa bản ghi
  (trừ nội dung đánh giá nhiều dòng trong 1 trường).
- Ví dụ TABLE9 (1 tầng): `@T1_360_440_360_Đạt_360_Đạt_360_Đạt_360_Đạt`

## NGUỒN HIỆN TRẠNG: DANH SÁCH DỊ TẬT MỤC 8 (người dùng chốt)

Khi làm đầy đánh giá hiện trạng các bảng (TABLE2/4/6/10...), **đọc TÊN các thư mục trong
"8.Hình ảnh dị tật bất thường" của CHÍNH trạm** — mỗi thư mục = 1 dị tật thật đã chụp
(vd "Đốt D2 - Thanh giằng han rỉ nặng", "Bu lông neo - M1..M4 han rỉ thiếu mỡ"):
- Map từng dị tật vào đúng bảng + đúng dòng: Đốt Dn → TABLE6 (cánh/giằng) + TABLE10
  (bu lông nối đốt n-(n+1)); Bu lông neo → TABLE2 + TABLE10 dòng Chân cột; Thoát sét → TABLE4.
- Mức "nặng" → đề xuất THÊM "thay thế cấu kiện han rỉ nặng"; "nhẹ/thiếu mỡ" → đánh rỉ,
  sơn, vệ sinh + bôi mỡ.
- Đốt/cấu kiện KHÔNG có trong danh sách dị tật → hiện trạng SẠCH ("không đứt gãy, không
  cong vênh, không han rỉ") + đề xuất "- Không". KHÔNG bịa dị tật không có ảnh.

Bảng map ĐẦY ĐỦ (đã áp cho 12 trạm tudungchuan 20/22-08-2026):

| Tên thư mục dị tật | Bảng đích |
|---|---|
| Đốt Dn - Thanh cánh/giằng ... | TABLE6 đốt n (nặng → "thay thế thanh ... han rỉ nặng") |
| Đốt Dn - Bu lông (nối đốt) ... | TABLE6 đốt n + TABLE10 dòng "Đốt n-(n+1)"; nếu n = đốt cuối → dòng "(n-1)-n" |
| Đốt Dn - Mặt bích CHÂN đốt | TABLE6 đốt n |
| Đốt Dn - Mặt bích NỐI đốt / Mặt bích | TABLE10 dòng "Đốt n-(n+1)" |
| Bu lông neo - ... | TABLE2 dòng Bu lông neo + TABLE10 dòng Chân cột |
| Móng Mx - ... | TABLE2 dòng Móng Mx (nứt vỡ → trát vá; chưa đổ BT chống cỏ → đổ BT; lún → theo dõi/gia cố; "bê tông che phủ" → "không kiểm tra được" + đề xuất Không) |
| Thoát sét cho chân cột / kim thu sét / thiết bị | TABLE4 dòng tương ứng ("Không có dây" → "thoát sét trực tiếp qua thân cột thép" + Không) |
| Kim thu sét - ... | TABLE7_Duoi + TABLE7_Tren dòng Kim thu sét |
| Gá treo Anten - ... | TABLE7_Duoi + TABLE7_Tren dòng Giá treo anten |
| Ống monopole / Mặt bích bịt đầu cột | KHÔNG vào bảng nào (theo trạm chuẩn HNM00085 user đã duyệt — chỉ nằm ở ảnh) |

Kiểm tra kèm theo khi làm đầy:
- TABLE10 số dòng = Chân cột + (số đốt − 1) mối nối; XÓA dòng "Đốt n-(n+1)" vượt quá số đốt
  (vd 00111 có dòng "Đốt 8-9" thừa khi cột chỉ 8 đốt).
- Giữ nguyên trường kích thước móng (TABLE2), số bu lông + khe hở (TABLE10) do khảo sát đo —
  KHÔNG bịa số bu lông nếu đang trống; chỉ điền đánh giá + đề xuất.
- Quét xóa dòng "Móc co", "Móng M0" sót từ template dây co trong TABLE2/TABLE3 mọi trạm tự đứng.

## Quy tắc bắt buộc theo loại cột

### Dây co
- TABLE7_Duoi = TABLE7_Tren: phụ kiện gồm Bản định vị chân cột, Tăng đơ, Ma ní trên/dưới,
  Khóa cáp trên/dưới, Vòng ốp + bu lông, Dây co, Giá chống xoay, Giá treo anten, Kim thu sét,
  Mặt bích bịt đầu cột, Ống monopole.
- **TABLE8_Duoi PHẢI GIỐNG HỆT TABLE8_Tren** (lực căng đo 2 đầu như nhau).
- TABLE2: móng M0 (giữa) + M1..Mn (móng co) + Bu lông neo + Móc co (+ Dầm D1/D2 nếu trên mái).

### Tự đứng
- **⚠️ SỬA TABLEBia.txt TRƯỚC TIÊN nếu Bia ghi nhầm "Loại cột: Dây co".** Nhiều gói Data
  sinh từ template dây co → Bia sai. PHẢI đổi trong TABLEBia.txt (KHÔNG chỉ sửa INPUT):
  `Loại cột:_Tự đứng`, `Số móng co:_0`, `Số tầng dây co:_0` (giữ `Số chân cột`). Phần mềm
  dựa vào "Loại cột" để sinh cấu trúc dữ liệu khác nhau — sai Bia là sai cả bộ.
  (Người dùng nhắc: folder tên "tudungchuan" nhưng 12 Bia đều ghi Dây co — đều phải sửa.)
- Các bảng dây co để RỖNG: TABLECaoDoDayCo(+5G,GiaCo), TABLE8_Duoi/Tren, TABLE9,
  LoaiDayCo, LoaiKhoaCap = `@` (rỗng). Khung ảnh phụ lục: 8 mục (bỏ 2 mục lực căng + khóa cáp).
- TABLE7: CHỈ gồm Bản định vị chân cột, Giá treo anten, Kim thu sét (theo NDH00002).
- **KHÔNG được đưa vào**: chi tiết Bu lông neo, Mặt bịt đầu cột, Móc co, Dây co, Tăng đơ,
  Ma ní, Khóa cáp, Vòng ốp (người dùng đã nhắc: "khi fake data thì bạn không được cho
  các loại bulong neo, mặt bít đầu cột vào").
- TABLE2: móng **M1..Mn (n = số chân cột)** — mỗi chân 1 móng; tọa độ/kích thước tạo hình
  chữ nhật/tam giác ĐỀU, không méo lệch.
- **"Móng M0" trong DATA (TABLE2/TABLE3): KHÔNG có** — tự đứng chỉ có móng dưới từng chân
  = M1..Mn. Dòng "Móng M0" rỗng từ template dây co → XOÁ khỏi TABLE2/TABLE3.
  **NHƯNG trong INPUT (tool CAD) thì NGƯỢC LẠI: `MONG_KICHTHUOC M0 ...` là format chuẩn**
  (M0 = móng chân cột; người dùng đã tự sửa lại M0 sau khi tôi đổi M1..Mn). Phân biệt rõ:
  Data bảng → không M0; INPUT → dùng M0.
  Lưu ý: tên FILE ẢNH đo điện trở/kích thước có thể mang nhãn "Móng M0" = điểm đo tại chân
  cột — đó là nhãn ảnh, không phải dòng dữ liệu, không bắt buộc đổi.

## TABLE12 (đo nghiêng) — phải TÍNH ĐƯỢC độ lệch

Tọa độ không được random. Quy tắc hình học:
- Mỗi vòng có 3 điểm (cột 3 chân) hoặc 4 điểm (cột 4 chân/vuông).
- Các điểm 1 vòng tạo đa giác cỡ đúng bề rộng cột TẠI CAO ĐỘ đó.
- Tâm các vòng thẳng hàng theo phương đứng, cho lệch nhỏ e < H/400 (để kết quả "Đạt").
- Kèm TABLE12_ChanCot, TABLE12_DinhCot, TABLE12_HuongBac (1 điểm mỗi file).
- Cao độ Z các vòng tăng dần theo tầng.

## File phụ phải có

`SoAnten.txt` (tổng thiết bị), `LoaiDayCo.txt` (vd D12), `LoaiKhoaCap.txt`, `LoaiMayDo.txt`
(vd C380), `MongNoiChung.txt` (vd "M1 - M4"), `ChieuCaoNhaTram.txt` (0 nếu dưới đất),
`ThietKeLucCangTruocDayCo.txt` (vd "Trên mái@21m@ ong50"), `NoiDung5G.txt`,
`DanhSachThietBi5G.txt`, `NoiDungGiaCo.txt`, các bảng `*5G.txt`/`*GiaCo.txt` (copy bảng thường).

## TABLE11 (thiết bị) — dựa ảnh nếu có

Format: `@CaoDo_Loai_KichThuoc_TrongLuong_SoLuong`. Đếm anten trong ảnh "thiết bị trên cột";
kích thước tra `05` mục thư viện anten trong `04_TaoTAITRONG.md`. Có FEEDER dòng cuối.
