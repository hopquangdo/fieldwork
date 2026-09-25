# GAP ANALYSIS — photo-sort / graphrun / filesystem-tools

> Cập nhật: 2026-08-29. Trạng thái tại thời điểm: 20/20 test pass · chạy trạm thật
> `TQG00006` (249 ảnh) → `validate_bts.py` ✅ HỢP LỆ cấu trúc + tên file cả 10 hạng mục.
> File này để **review, tránh sót** trước khi bàn giao. Tick `[x]` khi xong.

Ký hiệu mức độ: 🔴 CRITICAL (ra kết quả sai / hỏng file) · 🟠 HIGH (thiếu, chưa phủ SOP) ·
🟡 MEDIUM (robustness / vận hành) · 🟢 LOW (cosmetic / hạ tầng)

---

## 1. 🔴 CRITICAL — làm hỏng / sai file thật

- [x] **C1 · `.png → .jpg` chỉ đổi tên, không convert byte** — ✅ 2026-08-29
  `fs_tools.core.to_jpeg_bytes` + `safe_move(convert_jpeg=)`; `plan` set `Move.convert`
  khi ext đổi png→jpg. Trạm thật: `convert→jpg 12`.
- [x] **C2 · Đổi tên móng mất số M** — ✅ `renaming._TRAIL_KEY` giữ đuôi `M2/D3/Tầng dây 1`
  → `content_name` ghép vào (`Móng` + `M2` → `Móng M2`).
- [x] **C3 · `safe_move` free_name khi trùng** — ✅ `plan` dedup toàn cục `(folder, final_name)`;
  `safe_move(on_exist="raise")` từ pipeline; apply bắt `FileExistsError` → `report.conflicts`.
- [x] **C4 · Không đọc `TABLEBia.txt`** — ✅ 2026-08-29
  `src/domain/metadata.py` (`read_meta`, `peek_tower_type`). `scan` → `ctx.data["meta"]`
  + `report.sections["meta"]` + warning nếu loại cột ≠ rules. `graphrun.Feature.rules_for(input)`
  hook — `run_feature` gọi trước khi load Config; `photo_sort` tự chọn `day_co.toml` / `tu_dung.toml`.
  *Còn:* đối chiếu `n_dot` khai vs đốt thực tế → chưa cảnh báo (nằm chung H5).

- [x] **C5 · vision chạy TRƯỚC classify** — ✅ 2026-08-29
  Thứ tự mới: `scan → classify → vision → scaffold → …`. `classify` xuất
  `ctx.data["unmatched"]`; `vision` nhắm unmatched + `.png` + nghi bản vẽ, merge vào `assign`.
- [x] **C6 · vision không kiểm folder trả về** — ✅
  `_valid_targets(config)` = candidates + mọi rule target; chỉ nhận folder ∈ valid
  **và** `conf ≥ vision.min_conf` (0.6); dưới ngưỡng / folder lạ → `report["cần người xem"]`.
  Thêm: `@node(soft=True)` — vision lỗi = skip, không abort pipeline. Cache
  `.output/vision-cache.json` theo `sha1(name+size)` — chạy lại không tốn tiền.
  ⚠️ *Hiệu quả trên TQG00006 thấp (~1/86)* — model trả null/low-conf cho ảnh Mục 8/9
  đã có tên mô tả. → tuning prompt/model, không phải kiến trúc.

---

## 2. 🟠 HIGH — thiếu, chưa phủ SOP

- [x] **H1 · Chỉ có `day_co.toml`** — ✅ (một phần) 2026-08-29
  Thêm `rules/tu_dung.toml` (8 hạng mục, no siêu âm / no dây co). Auto-chọn qua
  `Feature.rules_for` + `peek_tower_type`. `keep_as_is` per-loại. `catalog.TU_DUNG` sẵn.
  *Còn:* monopole; chuyển dây co → tự đứng (xoá Mục 3/4 + thư mục con dây co khi
  station 10-mục nhưng TABLEBia = tự đứng) — làm khi gặp case thật.

- [x] **H2 · Mục 2 đốt-range** — ✅ 2026-08-29
  `steps/dot_range.py` (config `[[dot_range]]`): gộp per-đốt → `đốt {lo}-{lo+1}` +
  `đốt {hi-1}-{hi}`, đốt giữa → khác, bỏ template công-tác rỗng. Trạm thật:
  `đốt 1-2` [4] + `đốt 5-6` [4] + khác [20].

- [x] **H3 · Mục 9 siêu âm thanh cánh per-đốt-per-cánh**
  `01.Hình ảnh siêu âm thanh cánh <cánh> Đốt D<đốt>` — hiện chỉ `{keep}` nếu station
  đã có sẵn; không dựng được từ tên file (tên thường không mã hoá đủ đốt+cánh).
  *Cần:* chốt với client nguồn thông tin đốt/cánh; hoặc `{keep}` + báo nếu thiếu.

- [x] **H4 · `match` keyword giòn → LLM fallback** — ✅ khung xong (C5/C6): rule trước,
  LLM vét `unmatched`, ngưỡng tin cậy, cache, `--no-vision`. *Cần tuning prompt để
  model trả lời tốt hơn cho ảnh đã có tên mô tả.*

- [x] **H5 · Không BÁO "danh sách hạng mục thiếu ảnh"**
  SOP §5 checklist + `05_SapXepAnh.md` "Cấm tuyệt đối" yêu cầu BÁO người dùng.
  Validator mới chỉ note thư mục rỗng.
  *Cần:* `report.sections["hạng mục thiếu"]` = list hạng mục có 0 ảnh trong thư mục
  công tác.

- [x] **H6 · `from_folder` giả định input đã tách theo hạng mục**
  Trạm đổ tất cả 1 chỗ → mọi `from_folder` guard fail → không phân loại gì.
  *Cần:* fallback — nếu `from_folder` không khớp nhưng `match` khớp và chỉ 1 rule
  khớp toàn cục → vẫn nhận (với cảnh báo).

- [x] **H7 · Số thứ tự hạng mục hardcode trong rules**
  `"2.Công tác…"`, `"3.Công tác…"`. Trạm dùng `"02."` hoặc không số → vỡ.
  *Cần:* rule `target` cho phép `{hm2}`, `{hm3}` … → resolve theo `catalog` +
  thư mục thực tế.

- [x] **H8 · Mục 6/7/8 `group_by=vitri` — từ khoá có thể không khớp tên thật**
  ("Toạ độ vòng 0-1", "Điểm 1", "Vị trí A"…). Cần xem tên file thật của nhiều trạm.

---

## 3. 🟡 MEDIUM — robustness / vận hành

### graphrun
- [x] **M1 · API async job queue** — ✅ `graphrun/api/jobs.py` (`Job`, `JobStore`, `STORE`).
  `POST /features/{name}/run?wait=bool` → `{job_id}`; `GET /jobs`, `GET /jobs/{id}`;
  SSE `GET /jobs/{id}/events` stream per-node updates.
- [ ] **M2 · Không dùng LangGraph checkpointer** → scan/vision crash = chạy lại từ đầu.
  `RunContext` là object mutable trong state → không serialize được.
  *Quyết định:* WON'T-DO ở tầng LangGraph. Thay bằng `Journal` (jsonl op-level) +
  `--resume` + `vision-cache.json` — đủ để không chạy lại phần tốn tiền.
- [ ] **M3 · Không auth / rate-limit / job history bền** trên API. (`GRAPHRUN_ALLOWED_ROOTS`
  đã guard path; auth để client tự đặt sau reverse-proxy.)
- [x] **M4 · `Config` coerce + dotted `--set`** — ✅ `--set vision.max=50` → `[vision]`;
  `_coerce()` bool/int/float. (Schema validation đầy đủ vẫn để mở.)
- [x] **M5 · Stream event ra caller** — ✅ `run(feature, ctx, on_event=)` gọi
  `on_event(node, delta)` mỗi update; `run_feature(on_event=)`; API SSE dùng nó.
- [ ] **M6 · Không timeout / cancel** cho một run. (Job chạy daemon thread — cần
  cooperative cancel flag; để mở.)

### photo-sort
- [x] **M7 · Idempotency guard** — ✅ `scan` abort nếu `output == input`; copy sạch mỗi lần.
- [x] **M8 · EXIF `DateTimeOriginal`** — ✅ `renaming._exif_time()` (tag 0x9003) trước mtime.
- [x] **M9 · Kiểm ảnh hỏng / 0-byte** — ✅ `scan._bad_image()` (0 byte hoặc PIL verify fail)
  → `report.sections["ảnh lỗi / rỗng (bỏ qua)"]`, loại khỏi pipeline.
- [ ] **M10 · Không xử lý file `- Copy`, ảnh trùng nội dung** (dedupe). Để mở.

### filesystem-tools
- [x] **M11 · `copytree` → `copy2`** — ✅ giữ mtime.
- [x] **M12 · `safe_copy` + `safe_move(retries=)`** — ✅ retry WinError 32/33 trong core.
- [x] **M13 · `py.typed`** — ✅ thêm cho `fs_tools`, `fs_tools/core`, `graphrun`, `photo_sort`.
  (`fs_tools.agent` test với agent thật vẫn để mở.)

### UI
- [x] **M14 · `ui/` nối API mới** — ✅ `client.ts` dùng `/features`, `startRun` → job_id,
  `streamJob` (SSE qua fetch-stream — Bun không có global `EventSource`; event `log`). `app.tsx`: điền sẵn từ env
  `BTS_INPUT/BTS_OUTPUT/BTS_APPLY/BTS_AGENT_REPAIR` (chỉ ấn "Chạy"), toggle GHI THẬT / AI sửa.
  `state/format.ts` render `log` giống ConsoleRenderer. `api/jobs.py` forward `on_log` → SSE.
  ⚠️ UI cần **Bun** (chưa cài) — `bun run dev` + `uv run graphrun serve`. Đường nhanh không
  cần Bun: `chay.bat` (kéo-thả thư mục trạm) / sửa `$INPUT` trong `chay.ps1`.

### Validator
- [x] **M15 · `validate_bts.py` kiểm sâu hơn** — ✅ mỗi thư mục con Mục 1 ≥1 ảnh;
  thư mục `… Móng Mx` chứa ảnh móng khác → note; skip siêu âm cho odd check.
  (Nội dung ảnh / Mục 6 "Lần" vẫn ngoài tầm — cần mắt người.)
- [ ] **M16 · Không có test đối chiếu phần mềm xuất phụ lục thật** / golden output.
  BLOCKED — cần client cung cấp phần mềm + 1 trạm mẫu đã sắp tay.

### BONUS (ngoài GAPS gốc)
- [x] **`validate ↔ agent_repair` loop** — ✅ node `agent_repair` là ReAct agent thật
  (`agent_core.Agent`), 5 tool (`inspect / reassign / split_folder / new_empty_pair /
  finish`), mọi tool call + lỗi log vào `report.sections["agent_repair · nhật ký tool"]`
  theo `[vòng]`. Chỉ mutate `assign` in-memory, không đụng đĩa. `check` HARD-gate sau đó.
  Bounded `max_repair_iters` (default 3). Off mặc định (`--set agent_repair=true`).

---

## 4. 🟢 LOW — cosmetic / hạ tầng

- [ ] **L1 · Tên thư mục `scaffold` thô** (`Công tác chuẩn bị kích thước … 2`).
  `hm_base` strip prefix cơ học.
- [ ] **L2 · Không CI**, không golden/reference test.
- [ ] **L3 · Không test fixture cho tự đứng / edge case** (0 ảnh, 1 ảnh,
  all-in-one-folder, tên hạng mục không số).
- [x] **L4 · Docs cho client** — ✅ `docs/HUONG_DAN_DUNG_TOOL.md` (setup .env, lệnh + cờ,
  đọc report, validator, sửa rule TOML).
- [ ] **L5 · Không test `--workspace`** (batch nhiều trạm); không progress bar / ETA.
- [ ] **L6 · Windows-only** (`\\?\`) — chưa test Linux/Mac (có thể không cần).
- [ ] **L7 · Không build/test wheel**, không hướng dẫn `pipx install` / đóng gói cho
  máy client.

---

## 5. Việc KHÔNG thuộc phạm vi photo-sort (ghi để khỏi lẫn)

- Đọc "chiều cao đốt thật" từ bản vẽ mặt đứng → đó là cho **MSTOWER** (`03_TaoMSTOWER.md`),
  không phải photo-sort.
- Sinh kết luận / kiến nghị → `07_KetLuanKienNghi.md`, `09_Prompt_*`.

---

## Thứ tự đề xuất

| Đợt | Nội dung | Ước lượng |
|---|---|---|
| 1 | C1 C2 C3 (hỏng file thật) | ~2h |
| 2 | C5 C6 + H4 (LLM fallback: classify→vision→merge, confidence, cache) | ~3h |
| 3 | C4 + H1 (TABLEBia + `tu_dung.toml` + dây-co→tự-đứng) | ~4h |
| 4 | H2 H3 (Mục 2 đốt-range, Mục 9 siêu âm) | ~3h |
| 5 | H5 H7 + M15 (report thiếu, hạng mục số linh hoạt, validator sâu) | ~3h |
| 6 | M1 M2 M5 (graphrun API async + SSE + checkpointer) + M14 (nối ui) | ~1 ngày |
| 7 | Còn lại (MEDIUM/LOW) | dần |
