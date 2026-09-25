# Profile SOP — schema (`rules/<tên>.toml`)

Mỗi file = 1 chuẩn kiểm định. Công ty khác tạo file mới, **không sửa code**.
**Mọi field đều optional** — thiếu thì lấy mặc định = SOP cột dây co.
`Profile.load()` báo lỗi rõ nếu TOML hỏng hoặc list sai kiểu.

---

## Top-level

| Field | Mặc định | Nghĩa |
|---|---|---|
| `name` | tên file | nhãn hiển thị |
| `tower_type` | `"day_co"` | `day_co` / `tu_dung` / `monopole` — auto chọn theo TABLEBia (`feature.rules_for`) |

## `[structure]` — quy tắc "phụ lục đạt chuẩn"

| Field | Mặc định | Nghĩa |
|---|---|---|
| `min_cong_tac` | `2` | mỗi hạng mục cần ≥ N thư mục "Công tác" |
| `pair_folders` | `true` | số thư mục công tác phải CHẴN |
| `require_khac` | `true` | mỗi hạng mục phải có "Hình ảnh khác" |
| `even_images` | `true` | mỗi thư mục công tác: số ảnh CHẴN |
| `prefer_images` | `4` | ưu tiên ≤ N ảnh/thư mục (dư → "khác") |
| `even_no_trim` | `["9."]` | hạng mục bắt đầu bằng các prefix này: chỉ ép chẵn, KHÔNG cắt về 4 |
| `keep_as_is` | `["1.", "10."]` | hạng mục giữ nguyên — không ép cặp/chẵn |
| `even_skip` | `["siêu âm", "sieu am"]` | thư mục chứa chuỗi này: bỏ qua ép chẵn (SOP giữ nguyên) |
| `keep_singletons` | `false` | `true` → thư mục phụ lục CHỈ 1 ảnh giữ nguyên (SOP TH3), không bị đẩy sang "khác" và không tính là lẻ |
| `odd_fix` | `"split"` | số thư mục phụ lục lẻ: `"split"` chia đôi thư mục đông nhất · `"sibling"` thêm thư mục CẶP rỗng (tên chuẩn) cho thư mục cuối (sắp tự nhiên, vd "…đốt 7") |
| `trim_earliest` | `[]` | hạng mục chứa chuỗi này: ép chẵn bỏ ảnh SỚM nhất (mặc định bỏ ảnh MUỘN nhất) |
| `odd_folders_skip` | `[]` | hạng mục chứa chuỗi này: không ép số thư mục phụ lục chẵn (vd đo kích thước: mỗi cấu kiện 1 thư mục) |

Thứ tự GIỮ khi ép chẵn (`even_four`): ảnh chính (`--1--`) → ảnh cùng prefix với ảnh chính →
ảnh có prefix → theo giờ chụp (giữ sớm / bỏ muộn, hoặc ngược lại với `trim_earliest`).

## `[folders]` — nhận diện loại thư mục theo tên

| Field | Mặc định | Nghĩa |
|---|---|---|
| `cong_tac_markers` | `["công tác", "chuẩn bị"]` | leaf CHỨA 1 trong các chuỗi này → thư mục "Công tác" (trừ khi là "khác") |
| `khac_markers` | `["hình ảnh khác", "hinh anh khac"]` | leaf BẮT ĐẦU bằng → thư mục "khác" |
| `appendix_markers` | `["công tác", "chuẩn bị", "đo kích thước", …]` | thư mục nào bị ép chẵn/≤prefer |
| `strip_prefixes` | `["Công tác chuẩn bị ", "Công tác đo ", …]` | bóc prefix khi suy tên cấu kiện |
| `khac_name` | `"Hình ảnh khác"` | tên thư mục "khác" khi phải tạo mới |

Tiền tố `pair_names` DÀI nhất khớp được bóc để lấy phần chung của cặp (`pair_core`) —
vd tự đứng dùng `["Công tác chuẩn bị ", "Công tác "]`: "Công tác chuẩn bị kiểm tra X" ↔ "Công tác kiểm tra X".

## `[scan]` — lọc đầu vào (`domain/intake.py`)

| Field | Mặc định (_base) | Nghĩa |
|---|---|---|
| `skip_nested_copies` | `true` | thư mục con có ≥ `nested_min_overlap` thư mục đánh số TRÙNG TÊN hạng mục gốc = bản sao lồng của trạm → bỏ cả cây (không copy sang output, không kiểm kê) |
| `nested_min_overlap` | `2` | ngưỡng trên |
| `skip_imageless_dirs` | `true` | thư mục cấp 1 không đánh số, không chứa ảnh (Data, res…) → không mang sang output |
| `dedupe_content` | `true` | ảnh trùng sha1 → giữ bản nông nhất, bỏ bản còn lại khỏi bản làm việc (input không đổi), ghi report "ảnh trùng nội dung (bỏ qua)" |
| `dedupe_scope` | `"hang_muc"` | `"hang_muc"`: chỉ gộp trùng trong CÙNG hạng mục (ảnh cố ý đặt ở 2 hạng mục, vd dị tật + trèo cao, giữ cả hai) · `"all"`: toàn trạm |

## `[[tower_evidence]]` — ảnh thực tế bác TABLEBia

```toml
[[tower_evidence]]
declared          = "day_co"                      # loại cột TABLEBia khai
require_photos_in = ["lực căng", "khóa cáp"]      # hạng mục ĐẶC TRƯNG của loại đó
otherwise         = "tu_dung"                     # mọi hạng mục đặc trưng đều 0 ảnh → dùng loại này
```
Dùng khi tự chọn profile (`feature.rules_for`) và ở `scan` (meta + cảnh báo).

## `[canonical]` + `[[subfolders]]` — tên thư mục con CHUẨN (`steps/canonicalize.py`)

```toml
[canonical]
min_score = 0.6        # Jaccard token tối thiểu (tên đã bỏ số thứ tự đầu vs mẫu đã điền biến)
unmatched = "keep"     # mặc định cho thư mục không khớp: "keep" | "khac"

[[subfolders]]
hm        = ["bê tông"]                                   # nhận diện hạng mục (casefold, chứa)
khac      = "Hình ảnh khác công tác kiểm tra cường độ bê tông móng"
templates = ["Công tác chuẩn bị kiểm tra cường độ bê tông móng Móng {mong}",
             "Công tác kiểm tra cường độ bê tông móng Móng {mong}"]
ensure    = []            # luôn tạo (kể cả rỗng); cũng là tên hợp lệ
pairing   = "all"         # "singletons" (mặc định) | "all" | "none" — dựng thư mục cặp rỗng
unmatched = "khac"        # ghi đè [canonical].unmatched
```
- Biến mẫu: `{<nhóm>}` = khoá nhóm `[groups]` (`{dot}`→`D1`, `{mong}`→`M2`, `{vitri}`→`chân cột`);
  `{<nhóm>_k}` = chỉ số (`{dot_k}`→`1`). Giá trị đọc từ CHÍNH tên thư mục đang xét.
- Thư mục trùng tên chuẩn được GỘP ("01.… cánh 1 Đốt D1" + "… cánh 2 Đốt D1" → "… Đốt D1").
- Thư mục "khác" nào của hạng mục cũng đổi về `khac`. Không khớp → `unmatched`; luôn ghi
  "cần người xem"; thư mục mẫu sai tên mà RỖNG thì bỏ. Không bao giờ tự chế tên.
- `scaffold` / `odd_fix` / ghép cặp chỉ dựng thư mục có tên chuẩn khi hạng mục có khai báo.

## `[filename]` — quy ước tên file

| Field | Mặc định | Nghĩa |
|---|---|---|
| `conform` | `.+@\s*\d{1,2}@…@--[01]--\.\w+$` | regex: tên đã đúng quy ước chưa (đúng → không đổi) |
| `build` | `{content}@{h}@{m:02d}@{s:02d}{seq}@--{primary}--{ext}` | format dựng tên. Placeholder: `content h m s seq primary ext` |
| `primary_yes` / `primary_no` | `"1"` / `"0"` | giá trị `{primary}` cho ảnh chính / phụ |
| `ext` | `".jpg"` | đuôi đích (`.png` → convert JPEG thật) |

## `[groups]` — nhận "nhóm" từ prefix tên file (`group_by` trong rule)

```toml
[groups.mong]  pattern = 'm[oó]ng\s*(m?\d+)' ; fmt = "M{k}" ; strip = "mM"
[groups.dot]   pattern = '[đd][oố]t\s*d?\s*(\d+)' ; fmt = "D{k}"
[groups.vitri]
ring_pattern = 'v[oò]ng\s*(\d+\s*[-–]\s*\d+)'   # "vòng 0-1"
keywords = [
  { any = ["chân cột", "chan cot"], name = "chân cột" },
  { any = ["kim thu", "thu sét"],   name = "kim thu sét" },
]
[groups.blueprint] pattern = '\bm[oó]ng\s*m0\b|b[aả]n\s*v[eẽ]|drawing'
```
- nhóm thường: `pattern` (group 1 = số) + `fmt` (`{k}` = số, sau khi `strip`).
- `vitri`: thử `ring_pattern` trước, rồi `keywords`.
- `blueprint`: prefix khớp → ảnh nghi bản vẽ (vision xét).
- nhóm SUY RA từ số thứ tự (`ordinal`): vị trí không ghi trong tên, tính từ số của nhóm khác:
  ```toml
  [groups.vitri_dot]
  ordinal = "dot"        # lấy số k từ nhóm 'dot'
  total   = "n_dot"      # tổng: max số thấy trong tên ảnh (ưu tiên ảnh thực tế), thiếu → meta.n_dot
  buckets = [ { upto = 0.3333, name = "chân cột" }, { upto = 0.6667, name = "giữa cột" },
              { upto = 1.0, name = "đỉnh cột" } ]   # vị trí = (k − 0.5)/tổng → bucket đầu có upto ≥
  ```
  7 đốt → D1-2 / D3-5 / D6-7 · 8 đốt → 3/2/3 · 3 đốt → 1/1/1.
- `group_by` trong `[[rule]]` nhận 1 tên hoặc LIST (thử lần lượt), vd `["vitri", "vitri_dot"]`.

## `[metadata]` — đọc TABLEBia*.txt

```toml
[metadata]
table_glob = "tablebia"                        # prefix (casefold) tên file .txt
[metadata.tower_type]
day_co  = ["dây co", "day co"]
tu_dung = ["tự đứng", "tu dung"]
[metadata.fields]
n_dot  = 's[ốô]\s*đ[ốô]t\D*(\d+)'
n_mong = 's[ốô]\s*m[óo]ng(?:\s*co)?\D*(\d+)'
```

## `[hang_muc]` — tên chuẩn mỗi hạng mục (tùy chọn)

```toml
[hang_muc]
1 = "1.Hình ảnh tổng thể cột anten"
2 = "2.Công tác kiểm tra khe hở cấu kiện lắp ghép"
```

## `[prompts]` — override prompt AI (tùy chọn)

```toml
[prompts]
repair = """… {min_cong_tac} … {prefer_images} …"""   # {min_cong_tac}/{prefer_images} được điền
vision = """…"""
```

## `[vision]` · `[[rule]]` · `[[naming]]` · `[[dot_range]]`

Giữ nguyên như tài liệu `HUONG_DAN_DUNG_TOOL.md §5`. Thêm ở `[vision]`:

| Field | Nghĩa |
|---|---|
| `recheck_in` | hạng mục (chứa chuỗi) mà ảnh chỉ có giờ chụp nằm trong thư mục con CỤ THỂ vẫn được mở xem (vd `["tổng thể"]` — bản vẽ lạc). Ngoài các hạng mục này, ảnh chỉ có giờ đang ở thư mục cụ thể giữ nguyên; chỉ ảnh ở "khác"/chưa xếp mới gửi vision. |

Ứng viên vision = `candidates` + `target` của rule KHÔNG còn biến `{group}` (tên dở bị loại).

---

## KHÔNG cấu hình được (thuật toán thuần, nhận tham số)

`dot_range` (lo/lo+1/hi-1/hi) · `scaffold` tách thư mục lẻ · thứ tự lấy timestamp
(parse → HHMMSS → EXIF → mtime) · vòng reconcile · `verify` (bảo toàn ảnh) ·
`image_root` dò folder đánh số.
