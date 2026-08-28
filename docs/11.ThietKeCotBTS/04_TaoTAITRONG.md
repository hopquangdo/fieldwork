# 04 — TẠO FILE TAITRONG (TẢI TRỌNG + ANTEN CHO MSTOWER)

Mục tiêu: file `<Ma>_TAITRONG.txt` gồm PARAMETERS/TERRAIN/LOADS/ANCILLARIES.
Mẫu chuẩn: `NDH00002_TAITRONG.txt`, `NDH00234_TAITRONG.txt`.

## PARAMETERS

```
PARAMETERS
  ANGN     90.0
  CODE     TIA222G
  CLASS-G    2
  TOPCAT-G   1
  VB    50.28        $ Vung gio IV (Ninh Binh). I 32.56 | II 39.37 | III 45.16 | IV 50.28 | V 54.94
  OVERLAP  0
END
TERRAIN
  ANGLE 0 TCAT 2     $ TCAT lay theo TABLEBia (dong bang 2 hoac 3)
END
```

## LOADS (khung cố định)

- CASE 100: Dead Load (DL)
- CASE 1000–1070: gió 8 hướng (0/45/90/135/180/225/270/315) `WL ANGLX <goc> NOICE`
- CASE 3000: 1.20×DL
- CASE 4000–4070: 1.20×DL + 1.60×gió từng hướng
- CASE 5000–5070: 1.00×DL + 1.00×gió từng hướng

## ANCILLARIES

### Feeder (LINEAR)
```
LINEAR   LIBR L:MS_LIN
1_6FD XB -0.22 YB 0.1334 ZB 3.5  XT -0.22 YT 0.1334 ZT <dinh>  LIB 6FD FACT 1 ANG 0
```
2–3 tuyến, ZT đến cao độ anten cao nhất.

### Anten (LARGE, thư viện L:MS_ANC)

Nguồn dữ liệu: **TABLE11 của trạm** (cao độ, loại, số lượng). Đếm cả trong ảnh
"thiết bị trên cột" nếu Bia/TABLE11 thiếu.

Quy tắc đặt:
- 3 sector cách nhau 120° (cột 3 chân/tam giác) — offset bán kính ~0.55 m từ tâm:
  `(0.550, 0)` / `(-0.275, 0.476)` / `(-0.275, -0.476)`.
- Cột 4 chân: 4 hướng hoặc 3 sector tuỳ ảnh thực tế.
- Mỗi dòng: `Ten Xa .. Ya .. Za <caodo> ANG <goc> LIB <ten>`.
- **GÓC XOAY ANG = 90 − (góc phương vị của vị trí)** để anten HƯỚNG RA NGOÀI
  (xác nhận từ code `md_ToaDoAnten.vb` hàm `goc(x,y)`: +X→ANG 90, +Y→ANG 0,
  −X→ANG −90, −Y→ANG 180). Vị trí Xa=r·cosθ, Ya=r·sinθ → ANG=90−θ (chuẩn hoá về (−180,180]).
  VD 3 sector θ=0/120/240 → ANG = 90 / −30 / −150. (TRƯỚC ĐÂY tôi để ANG=θ là SAI —
  anten quay tiếp tuyến, không ra ngoài; đã sửa cho batch tudungchuan. NBH00063 cũ cũng
  cần sửa lại theo công thức này nếu render lại.)
- **Tên anten phải DUY NHẤT** (MStower lỗi nếu trùng): thêm hậu tố cao độ + số chạy,
  vd `RRU39_5`. Đừng để `RRU-1` lặp ở nhiều cao độ.
- LIB Viba/chảo D600 → `MW0.6` (thư viện MW0.3/0.6/0.9/1.2/1.8 theo đường kính).
- Số lượng anten phải ĐỦ theo TABLE11 (đã bị chê "ít anten quá, vị trí, góc xoay sai").

### Thư viện anten (tên LIB + kích thước để đối chiếu TABLE11)

| LIB | Loại | Kích thước (mm) | KL (kg) |
|---|---|---|---|
| SG900 | 2G 900 | 2580×262×116 | 25.3 |
| DUAL-BAND | dual band | 1334×261×146 | 20.3 |
| 4G | 4G | 1471×275×86 | 16.8 |
| 5G | 5G | 1610×307×118 | 46.1 |
| RRU | RRU (TABLE11 ghi "RF" 425×300×190 cũng là RRU) | 425×300×190 | 15 |
| 6P | 6 port | 1995×377×169 | 27.2 |
| 8-P | 8 port | 1224×640×235 | 29.7 |
| 10P_N | 10 port | 2090×448×188 | 42 |
| MW0.6 | Viba chảo D600 | Ø600 | — |

### Sàn thao tác / tháp canh (platform + lan can)

- **KHÔNG dựng thanh sàn/lan can trong PROFILE MSTOWER** (các model chuyên nghiệp DNG
  cũng không dựng) — vành sàn đã được thể hiện bằng dòng PLAN tại panel đó.
- **PHẢI khai vào ANCILLARIES**: trọng lượng ~150–300kg + diện cản gió lớn của lưới
  lan can (vd LARGE dạng BOX/RING, đường kính bao ~3m × cao 1.1m, hệ số đặc 0.3–0.5)
  tại đúng cao độ sàn. Bỏ quên mục này là thiếu tải gió đáng kể.

## Lưu ý

- Anten trên ống monopole: mô hình ống trong MSTOWER trước (xem 03) để Za đặt đúng cao độ thật.
- Cao độ anten của cột thấp hơn phải hạ theo (đừng copy nguyên cao độ trạm mẫu cao hơn).


## QUY TẮC BỐ TRÍ ANTEN THEO CAO ĐỘ (người dùng chốt 26/08/2026)

1. **Không anten nào cao hơn đỉnh cột.** Sau mỗi lần đổi chiều cao cột phải rà lại toàn bộ `Za`.
2. **Dồn thiết bị xuống các ĐỐT CHÍNH (thân giàn); ĐỐT TRÊN CÙNG chỉ để 1 nhóm 3 cái.**
   Đốt trên cùng (ống monopole / đốt đỉnh hẹp) không đủ tiết diện mang nhiều cụm anten.
   Các nhóm trong TABLE11 nằm sát đỉnh → hạ xuống đốt lattice trên cùng (giữ nguyên thứ tự
   cao thấp tương đối, chênh 1.5–2.5m so với số đo).
   Ví dụ HNM00001 (lattice 33m + ống 3m): TABLE11 có 4 nhóm ở 34.4/34.7/34.7/35.1
   → chỉ giữ 10PN @35.1 (3 cái) trên ống; 3 nhóm còn lại hạ về 32.4 / 32.6 / 32.8.
3. **Bán kính gá `Xa` = nửa bề rộng cột tại cao độ đó + 0.45m** (không dùng 1 giá trị cố định
   cho cả cột — đốt dưới rộng, đốt trên hẹp).
4. TABLE11 (hiện trạng đo) GIỮ NGUYÊN, chỉ điều chỉnh cao độ trong TAITRONG + INPUT và ghi chú lý do.
