# KIẾN TRÚC — photo-sort (chuẩn production)

> Trạng thái: đề xuất thiết kế. Đối chiếu với code hiện tại ở §9; lộ trình ở §10.
> Đo chất lượng bằng `photo-sort-eval` (xem §8) — mọi thay đổi kiến trúc phải giữ hoặc tăng số đo.

## 1. Bài toán và ràng buộc

Nhận thư mục ảnh thô của một trạm BTS → xuất cây thư mục phụ lục đúng SOP (hạng mục → cặp
"Công tác chuẩn bị / đo" → "Hình ảnh khác"), đổi tên theo quy ước, **không mất/đè ảnh nào**.

| Ràng buộc | Hệ quả thiết kế |
|---|---|
| Ảnh khách hàng — sai là mất việc, mất ảnh là sự cố | Không sửa input; plan → verify → apply; bảo toàn cứng; hoàn tác được |
| Nhiều trạm, nhiều loại cột, SOP đổi theo thời gian | Code = cơ chế trung lập; SOP = dữ liệu (profile) có schema + version |
| Không có đáp án 100% cho ảnh mơ hồ | Mỗi quyết định có độ tin cậy + nguồn; chưa chắc → hàng đợi người xem, không đoán |
| LLM không tất định, tốn tiền, ảnh có thể nhạy cảm | LLM chỉ ở biên, tập lựa chọn đóng, cache, ngân sách, có thể tắt |
| Rule là tài sản của công ty (IP) | Rule nằm ngoài package, không có UI sửa rule cho khách |
| Windows, đường dẫn dài | Mọi I/O đi qua lớp filesystem MAX_PATH-safe |

## 2. Nguyên tắc

1. **Cơ chế ≠ chính sách.** Không chuỗi/regex/số SOP nào trong `src/`. Thêm SOP hoặc trạm mới = thêm TOML.
2. **Tất định trước, LLM sau.** LLM chỉ nhận phần rule không quyết được, và chỉ chọn trong tập đóng.
3. **Bằng chứng → quyết định → kế hoạch → thực thi** là 4 bước tách bạch, mỗi bước kiểm tra được riêng.
4. **Không đoán.** Thiếu khai báo hoặc độ tin cậy thấp → gắn cờ, không tự chế quy tắc.
5. **Mỗi ảnh truy vết được:** vì sao nằm đây (rule nào / vision conf bao nhiêu / người quyết).
6. **Đo được:** không có "cải thiện" nếu harness GT không xác nhận, trên nhiều trạm.
7. **An toàn khi lỗi:** dừng sớm, không ghi dở; chạy lại (resume) cho cùng kết quả.

## 3. Bố cục hệ thống

```
        ┌────────────── Giao diện ──────────────┐
        │  CLI · HTTP API (FastAPI) · UI · CI   │      chỉ parse tham số, gọi Service
        └───────────────────┬───────────────────┘
                            ▼
        ┌─────────────── Service ───────────────┐
        │  sort_photos()  ·  evaluate()  ·  job │      1 điểm vào duy nhất, trả SortResult
        └───────────────────┬───────────────────┘
                            ▼
        ┌────────── Engine (graphrun) ──────────┐
        │  chạy graph · report · journal/resume │      không biết gì về ảnh hay SOP
        └───────────────────┬───────────────────┘
                            ▼
   ┌──────────────── Pipeline photo-sort (5 pha) ────────────────┐
   │ 1 INGEST → 2 UNDERSTAND → 3 DECIDE → 4 VERIFY → 5 COMMIT    │
   └───────┬───────────────────┬─────────────────────┬───────────┘
           ▼                   ▼                     ▼
      Domain (thuần)     Profile (SOP data)     Adapters
      naming, folders,   _base + day_co /       filesystem MAX_PATH-safe,
      matching, filename tu_dung … + schema     LLM (structured output), cache
```

Phụ thuộc một chiều từ trên xuống. Domain không import adapter; adapter không biết SOP.

## 4. Pipeline 5 pha

```
INGEST      scan · normalize
              ảnh, thư mục nguồn, TABLEBia → Photo[] + StationMeta; loại ảnh hỏng
UNDERSTAND  extract attributes   (rule) → vision (chỉ phần còn lại)
              mỗi ảnh → Evidence[]: {thuộc tính, giá trị, nguồn, độ tin cậy}
DECIDE      place (hàm thuần) → structure (scaffold · even_four · pairing)
              Evidence + Profile → Decision {folder đích, lý do, conf}; conf thấp → REVIEW
VERIFY      check SOP · conservation · unique names        (HARD gate)
COMMIT      plan (Move[]) → apply (journal) → delete_empty → manifest
```

### 4.1 UNDERSTAND — nguồn bằng chứng, xếp theo độ ưu tiên
1. Tên file (`prefix`, số đốt/móng…) — extractor khai báo trong profile
2. Thư mục nguồn (`from_folder`)
3. Thời gian chụp (thứ tự trong nhóm: chuẩn bị trước, đo sau — *giả thuyết, phải kiểm chứng bằng harness*)
4. Vision — chọn trong tập thư mục đích do profile sinh ra, có `unknown`, trả `confidence`
5. Người (file override, §7) — thắng tất cả

Mỗi Evidence mang `source` và `confidence`; DECIDE chỉ đọc Evidence, không biết nó đến từ đâu.

### 4.2 DECIDE — chỉ hàm thuần
- `Evidence[] + Profile → Decision`. Không I/O, không LLM → test tất định, replay được.
- Các cơ chế chung (không hard-code SOP): **gom thuộc tính thành nhóm** (`exact` / `range` / `enum`,
  ranh giới lấy từ khai báo hoặc metadata trạm), **mở rộng template đích**, **ghép cặp** chuẩn bị–đo,
  **ép chẵn**. Ranh giới không có khai báo → không đoán → REVIEW.

### 4.3 Vòng sửa (agent) — lưới an toàn cuối
Chỉ chạy khi còn vi phạm SOP sau DECIDE; ngân sách nhỏ (số vòng, tool call); không được vi phạm bảo toàn.
Ảnh nó phải sửa là **tín hiệu rule thiếu** → ghi vào report để soạn rule, không phải nơi "chữa" lâu dài.

## 5. Mô hình dữ liệu

| Thực thể | Trường chính |
|---|---|
| `Photo` | `id` (sha1 nội dung), `path`, `name`, `source_folder`, `captured_at`, `is_primary` |
| `Evidence` | `photo_id`, `attr`, `value`, `source` (`name`/`folder`/`time`/`vision`/`human`), `confidence` |
| `Decision` | `photo_id`, `target`, `reason` (rule id / vision), `confidence`, `status` (`auto`/`review`) |
| `Plan` | `Move[]` (`src`, `dest_dir`, `new_name`, `convert`) + thư mục cần tạo (kể cả rỗng) |
| `Run` | `run_id`, phiên bản profile, phiên bản prompt/model, số liệu, đường dẫn manifest |

Khoá định danh ảnh là **hash nội dung**, không phải tên/đường dẫn (tên đổi, ảnh vẫn là ảnh đó;
harness GT và cache vision cùng dùng khoá này).

## 6. Profile — SOP là dữ liệu

```
rules/
  _base.toml        cơ chế + mặc định chung (extractor, group, ký hiệu file)
  <loại cột>.toml   extends "_base": cây thư mục đích, rule, ranh giới nhóm, mô tả cho vision
```
- **Schema + kiểm tra khi nạp**: field thiếu → lỗi rõ (hiện đã có `ProfileError`); thêm kiểm tra
  *rule chết* (không khớp ảnh nào ở mọi trạm eval) và *đích không tồn tại trong cây SOP*.
- **Version**: profile có `version`; `Run` ghi lại version dùng → tái lập được kết quả.
- Loại cột chọn từ TABLEBia; **không xác định được → dừng**, không mặc định.
- Rule ở ngoài package (`rules/`), khách không sửa (IP).

## 7. Người trong vòng lặp

Đầu ra mỗi lần chạy gồm **manifest** (mọi Decision + lý do) và **hàng đợi review**
(Decision `status=review`). Người quyết bằng file `overrides.toml`/`json` (`photo_id → target`);
lần chạy sau nạp file này ở mức Evidence cao nhất và **giữ ổn định** (không bị đổi bởi rule/LLM).
Điều này đảm bảo: hệ thống không bao giờ đặt sai âm thầm — hoặc đúng, hoặc bị gắn cờ.

## 8. Chất lượng, đo lường, CI

| Tầng | Nội dung |
|---|---|
| Unit | domain thuần (naming, group, template, pairing), loader profile |
| Property | bảo toàn: mọi ảnh đầu vào có mặt đúng 1 lần ở đầu ra; tên không trùng trong 1 thư mục |
| Golden / eval | `photo-sort-eval`: so theo nội dung với GT; báo **precision** (ảnh tự quyết đúng bao nhiêu) và **coverage** (bao nhiêu ảnh tự quyết) tách riêng, theo hạng mục, kèm cấu trúc thư mục |
| Held-out | trạm dev để tối ưu, trạm held-out chỉ để phát hiện overfit; rule chỉ đúng 1 trạm sẽ lộ ra ở đây |
| Replay | vision chạy qua cache ghi sẵn → CI tất định, không tốn request; chạy live định kỳ để bắt model đổi hành vi |
| Cổng CI | chặn merge nếu precision < ngưỡng hoặc bất kỳ trạm nào tụt so với baseline |

Cache vision khoá theo `(hash ảnh, model, phiên bản prompt, hash tập lựa chọn)`.

## 9. Quan sát và vận hành

- **Report + journal** mỗi lần chạy (đã có `.output/<trạm>-<run_id>.{json,jsonl}`); thêm provenance từng ảnh.
- Log có cấu trúc (kênh `node` / `step` / `agent`); console cho người, JSON cho máy.
- Số đo mỗi run: thời gian từng node, số lần gọi LLM và chi phí, tỉ lệ auto/review, số vòng agent.
- **Ghi an toàn**: ghi vào output mới (không đụng input), `safe_move` không đè, journal cho `--resume`,
  khoá thư mục output để tránh 2 run song song, retry khi file bị khoá (WinError 32).
- **Bảo mật dữ liệu**: ảnh có thể chứa tem GPS/biển trạm → chỉ gửi ra LLM khi cấu hình cho phép;
  thu nhỏ ảnh trước khi gửi; không log nội dung ảnh; khoá API chỉ từ `.env`/secret store.
- **Triển khai**: CLI cho vận hành, API cho tích hợp (job bất đồng bộ, có huỷ/timeout — gap M6),
  auth cho API (gap M3), phiên bản hoá contract của `SortResult`.

## 10. Đối chiếu với code hiện tại

| Kiến trúc | Hiện có | Còn thiếu |
|---|---|---|
| Engine tách biệt | `graphrun` (graph, report, journal, resume) | timeout/huỷ job |
| INGEST | `scan`, `normalize`, `domain/station`, `domain/metadata` | đã sửa: tìm TABLEBia ở thư mục anh em, dừng khi không xác định loại cột, output không kèm Data |
| UNDERSTAND | `classify` (rule theo tên) + `steps/vision` | `Evidence` có nguồn/conf; vision với tập đóng đầy đủ; bỏ `max`; thứ tự thời gian |
| DECIDE | `classify` + `scaffold` + `even_four` + `dot_range` | tách hàm `place` thuần; cơ chế gom nhóm khai báo (`range`/`enum`); ghép cặp tổng quát |
| VERIFY | `check`, `validate`, `verify` | kiểm tra rule chết / đích ngoài SOP |
| COMMIT | `plan`, `apply` (journal), `delete_empty` | manifest provenance; hoàn tác |
| Người trong vòng lặp | `cần người xem` (section trong report) | `overrides` sticky |
| Đo lường | `photo-sort-eval` (đúng theo ảnh/hạng mục, cấu trúc) | precision/coverage; đa trạm dev/held-out; cổng CI |
| Vòng sửa | `agent_repair` (bounded, log tool) | coi như lưới an toàn; báo rule thiếu |

## 11. Lộ trình (mỗi bước đo bằng harness)

1. **P0 — nền** (xong): tìm TABLEBia, dừng khi không rõ, output gọn; harness GT.
2. **P1 — đo đúng**: precision/coverage, nạp nhiều trạm, tách dev/held-out, cổng CI.
3. **P2 — vision tập đóng**: mở rộng đích từ profile, `unknown` + ngưỡng, bỏ giới hạn `max`, cache theo hash.
4. **P3 — cơ chế gom nhóm khai báo**: `range`/`enum`, ranh giới từ khai báo hoặc metadata; không khai báo → review.
5. **P4 — Evidence/Decision + manifest**: tách `place` thuần, ghi provenance, hàng đợi review, `overrides` sticky.
6. **P5 — vận hành**: timeout/huỷ job, auth API, khoá output, hoàn tác, chỉ số chi phí.
7. **P6 — vòng học từ GT (tuỳ chọn)**: LLM đề xuất sửa profile từ chênh lệch với GT ở *thời điểm soạn rule*,
   người duyệt, harness kiểm chứng trên mọi trạm; lúc chạy vẫn tất định.

## 12. Câu hỏi còn mở

- Ranh giới nhóm (ví dụ đốt → chân/giữa/đỉnh) của SOP tự đứng: khai báo ở đâu, ai sở hữu?
- Thứ tự thời gian có đủ tin cậy để phân biệt "chuẩn bị" với "đo" không (kiểm chứng ở P1/P3)?
- Có được gửi ảnh gốc cho LLM ngoài không, hay phải dùng model chạy nội bộ?
- Trạm nào khác đã có GT để làm held-out?
