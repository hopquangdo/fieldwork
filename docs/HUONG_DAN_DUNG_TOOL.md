# Hướng dẫn dùng photo-sort (cho người vận hành)

Tool tự sắp ảnh hiện trường của 1 trạm kiểm định BTS vào **cấu trúc thư mục phụ lục**
mà phần mềm xuất báo cáo yêu cầu.

---

## 1. Chuẩn bị 1 lần

Tạo file `.env` ở gốc thư mục dự án (chỉ cần nếu muốn dùng AI cho ảnh mờ):

```
LLM_API_KEY=sk-or-...                       # key OpenRouter
LLM_MODEL_NAME=google/gemini-2.5-flash
LLM_BASE_URL=https://openrouter.ai/api/v1
```

Cài: `uv sync`

---

## 2. Chạy 1 trạm

```
uv run photo-sort "<thư mục trạm>" "<thư mục kết quả>"
```

- **`<thư mục trạm>`** = thư mục chứa các thư mục hạng mục đánh số (`1.…`, `2.…`) + thư mục `Data…`.
  **Không bị sửa** — tool chỉ đọc.
- **`<thư mục kết quả>`** = nơi ghi bản đã sắp (tool copy trạm sang đây rồi sắp tại chỗ).
- Mặc định **ghi thật**. Muốn xem trước không ghi: thêm `--dry-run`.

Tool chạy **MỘT luồng cố định** (xem `graph.py`): `scan → check → classify → vision →
dot_range → scaffold → even_four → (validate ↔ agent_repair) → plan → verify → apply →
delete_empty`. Mỗi bước **tự bỏ qua** khi không có việc — không có cờ bật/tắt.

Trong lúc chạy, tool **in log trực tiếp từng bước** (giống terminal Claude):
`⏺ <node>` khi bắt đầu, `⎿ <kết quả> (Xs)` khi xong, các dòng `⎿` con là chi tiết.
Node `check` liệt kê "vấn đề đầu vào"; `agent_repair` (khi có `LLM_API_KEY`) sửa nốt
phần rule không xử lý được, in từng lệnh `→ reassign(…)` + kết quả.
Thêm `--compact` để chỉ xem dòng tóm tắt mỗi node.

Sau khi chạy, xem file report: `.output/<tên trạm>-<mã>.json`

### Cờ

| Cờ | Ý nghĩa |
|---|---|
| `--dry-run` | chỉ tính kế hoạch, không ghi |
| `--compact` | log gọn — bỏ dòng chi tiết + từng lệnh AI, chỉ giữ tóm tắt mỗi node |
| `--rules <file.toml>` | dùng bộ luật khác (mặc định tự chọn `day_co` / `tu_dung` theo TABLEBia) |
| `--resume <.output/…-….jsonl>` | chạy lại sau khi bị ngắt — bỏ qua việc đã làm |

Bật AI: chỉ cần có `.env` với `LLM_API_KEY` — `vision` + `agent_repair` tự chạy khi cần
(có cache, chạy lại cùng trạm không tốn thêm).

### Nhiều trạm 1 lượt

```
uv run graphrun run photo-sort "<workspace nhiều trạm>" "<output>" --set workspace=true
```

---

## 3. Đọc report

File JSON trong `.output/`. Các phần quan trọng:

| Trường | Ý nghĩa |
|---|---|
| `stages[]` | từng bước: `✓ ok` / `- skipped` / `! error` + thời gian |
| `sections.images_before` / `images_after` | **phải bằng nhau** — không mất ảnh |
| `sections.meta` | loại cột / số đốt / móng đọc từ `TABLEBia.txt` |
| `sections["hạng mục thiếu ảnh (cần nhặt bù)"]` | hạng mục chưa có ảnh trong thư mục công tác — **cần nhặt bù thủ công** |
| `sections["cần người xem"]` | ảnh AI phân loại với độ tin thấp — nên kiểm mắt |
| `sections["khớp lỏng (from_folder không khớp)"]` | ảnh khớp tên nhưng đang ở nhầm hạng mục — tool đã đề xuất chuyển, nên kiểm |
| `sections["ảnh lỗi / rỗng (bỏ qua)"]` | file ảnh hỏng / 0 byte — bỏ qua |
| `aborted: true` | **DỪNG** — có lỗi nghiêm trọng (vd mất ảnh), không được dùng kết quả |

---

## 4. Kiểm tra kết quả

```
uv run python scripts/validate_bts.py "<output>/<tên trạm>/<tên trạm>" <số ảnh gốc>
```

Kiểm: mỗi hạng mục ≥2 thư mục công tác (số CHẴN) · mỗi thư mục công tác số ảnh CHẴN ·
có "Hình ảnh khác" · tên file đúng `@giờ@phút@giây@--x--` · tổng ảnh không đổi.

⚠️ Validator chỉ kiểm **cấu trúc**, không kiểm **nội dung** ảnh. Vẫn phải:
- xem các ảnh trong `"cần người xem"` / `"khớp lỏng"`
- chạy thử **phần mềm xuất phụ lục thật** để xác nhận cuối

---

## 5. Sửa luật phân loại (không cần lập trình)

File `rules/day_co.toml` (dây co) / `tu_dung.toml` (tự đứng).

Mỗi `[[rule]]`:

```toml
[[rule]]
match       = ["móng m", "mong m"]        # tên file (phần trước @) chứa 1 trong các chuỗi này
from_folder = ["3.công tác đo lực căng"]   # CHỈ áp dụng khi ảnh đang ở thư mục chứa chuỗi này
exclude     = ["khóa cáp"]                 # tên file chứa chuỗi này -> bỏ qua rule
group_by    = "mong"                       # tách mỗi móng 1 thư mục ({group} -> M1, M2…)
target      = "3.Công tác đo lực căng trong dây co/Công tác chuẩn bị đo lực căng {group}"
#   target = "{keep}"                      # -> giữ ảnh nguyên vị trí
```

`group_by` nhận: `mong` · `dot` · `tang` · `lan` · `vitri` (chân cột / kim thu sét / đỉnh cột / vòng x-y).

Ảnh không khớp rule nào → **giữ nguyên vị trí** (an toàn). Muốn dồn vào "khác":
```toml
[fallback]
target = "Hình ảnh khác"
```
