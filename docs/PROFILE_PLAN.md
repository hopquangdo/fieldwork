# PLAN — photo-sort: tri thức SOP → 1 file "profile" (công ty tự cấu hình)

> Mục tiêu: đưa **toàn bộ tri thức SOP đang hard-code trong Python** vào **1 file
> TOML mỗi họ SOP** (`profiles/<tên>.toml`). Công ty kiểm định khác chỉ sửa file,
> không đụng code. Thuật toán thuần (dot_range, scaffold split, reconcile) vẫn là
> code nhưng **nhận tham số** từ profile.
>
> Nguyên tắc: mỗi phase giữ **23 test xanh** + **parity TQG00006** (`plan · N move`
> không đổi trừ khi có lý do rõ). Tick `[x]` khi xong.

---

## 0. Nền tảng — `core/profile.py` + validation

- [x] **P0.1** `core/profile.py`: dataclass `Profile` (frozen) — `Structure / Folders /
  Filename / Metadata` + `hang_muc / rules / naming / dot_range / vision / groups / prompts`.
  **Mặc định mọi field = hành vi hard-code hiện tại** (day co) → profile chỉ có `[[rule]]`
  vẫn chạy y như trước.
- [x] **P0.2** `Profile.load(path)` / `Profile.from_dict(data)` → `ProfileError` khi TOML hỏng
  / list sai kiểu. (Validate sâu hơn: thêm dần khi field trở nên bắt buộc.)
- [x] **P0.3** `Profile.of(ctx)` — build 1 lần từ `ctx.config.data`, cache `ctx.data["profile"]`.
- [ ] **P0.4** `pipeline/feature.py` `rules_for()` giữ nguyên; đổi tên `rules/` → `profiles/`
  (làm ở P5 cùng `_base.toml`).
- [ ] **P0.5** `docs/PROFILE_SCHEMA.md` — mô tả từng field + ví dụ (làm ở P5).
- [x] **P0.6** `core/__init__.py` export `Profile, ProfileError`. 23 test xanh, chưa thay step nào.

**Verify:** `Profile.load(profiles/day_co.toml)` ra đủ field; test parity chưa đổi
(chưa thay code step nào).

---

## Phase 1 — `[structure]` + `[folders]`  (giá trị cao nhất, rủi ro thấp)

Thay hard-code trong `domain/folders.py` + `steps/validate.py` + `steps/scaffold.py`
+ `steps/even_four.py`.

### `[structure]`  ✅
- [x] **P1.1** `validate._collect` đọc `Profile.of(ctx).structure.*`.
- [x] **P1.2** Check `too_few / odd_folders / missing_khac / odd_images` theo
  `min_cong_tac / pair_folders / require_khac / even_images`.

### `[folders]`
- [x] **P1.3** Logic SOP-aware chuyển từ `domain/folders.py` → `core/profile.Names`
  (bound vào 1 Profile): `is_cong_tac / is_khac / is_appendix / is_kept / in_no_trim /
  is_ultrasound / hm_base / core_of / khac_folder`. `domain/folders.py` giữ THUẦN path
  (`leaf_of / hm_of / existing_dir`).
- [x] **P1.4** `validate / scaffold / even_four / dot_range / conservation / agent_repair`
  → `nm = Profile.of(ctx).names()`. `_make_tools(..., nm=None)` fallback `Profile.default()`.
- [x] **P1.5** `even_four` dùng `nm.is_appendix()` thay list hard-code.
- [x] **BUG fixed:** `is_khac` phải **neo đầu** (`startswith`) — tên khác chứa "công tác"
  ("Hình ảnh khác công tác…") ⇒ `is_cong_tac`/`is_appendix` return False khi `is_khac`.

**Verify:** ✅ 23 test · parity `check 24 · scaffold 9 · even_four 54 · validate hợp lệ ·
plan 110 move · đổi tên 16 · convert→jpg 12` (khớp trạng thái pre-P1).

---

## Phase 2 — `[filename]` + `[groups]`  ✅

- [x] **P2.1** `Filename` thêm `build` (format string). `renaming.conforms(name, regex)`,
  `build_name(..., fmt=, primary_yes/no=)`, `content_name(leaf, rules, strip_prefixes=, trail_re=)`.
- [x] **P2.2** `Names.trail_regex()` sinh regex đuôi nhóm từ `groups[*].fmt`
  (`M{k}` → `M\d+`…).
- [x] **P2.3** `plan.py` truyền `prof.filename` + `strip_prefixes` + `trail_re`.
- [x] **P2.4** `Names.group_key(prefix, kind)` — đọc `pattern/fmt/strip/keywords/ring_pattern`
  từ `profile.groups` (`_DEFAULT_GROUPS` + `[groups]` TOML). `naming.group_key` XOÁ.
  `naming.py` chỉ còn `parse` + `Component` (đọc input, không cấu hình).
- [x] **P2.5** `Names.looks_like_blueprint(prefix)` — `groups["blueprint"]["pattern"]`.
- [x] **P2.6** `matching.match_photo(photo, rules, hm_dirs, names)` — thêm param `names`;
  callers `classify` + `validate` truyền `nm`.

**Verify:** ✅ 23 test · parity `check 24 · scaffold 9 · even_four 54 · validate hợp lệ ·
plan 110/16/12` · tên file `Biển nhà trạm@20@25@07@--1--.jpg` đúng.

---

## Phase 3 — `[[hang_muc]]` + `[metadata]`

### `[[hang_muc]]`  (thay `domain/catalog.py` — hiện đã gần chết)
```toml
[[hang_muc]] n = 1  ; name = "Hình ảnh tổng thể cột anten" ; keep = true
[[hang_muc]] n = 2  ; name = "Công tác kiểm tra khe hở cấu kiện lắp ghép"
# … tới n = 10
```
- [ ] **P3.1** `Profile.hang_muc: dict[int, HangMuc(name, keep)]`.
- [ ] **P3.2** `keep_as_is` suy từ `hang_muc[*].keep` (bỏ field riêng ở `[structure]`,
  hoặc giữ cả 2 — chốt 1).
- [ ] **P3.3** Xoá `domain/catalog.py` + export ở `domain/__init__.py`.
- [ ] **P3.4** `_resolve`/`resolve_target` trong `matching` dùng `hang_muc` để map số → tên
  thật (đang dựa `hm_dirs` từ đĩa; thêm fallback là `hang_muc[n].name`).

### `[metadata]`
```toml
[metadata]
table_glob = "TABLEBia*.txt"
[metadata.tower_type]
day_co   = ["dây co", "day co"]
tu_dung  = ["tự đứng", "tu dung"]
monopole = ["monopole"]
[metadata.fields]
n_dot  = 's[ốô]\s*đ[ốô]t\D*(\d+)'
n_mong = 's[ốô]\s*m[óo]ng(?:\s*co)?\D*(\d+)'
n_tang = 's[ốô]\s*t[ầa]ng\s*d[âa]y(?:\s*co)?\D*(\d+)'
```
- [ ] **P3.5** `domain/metadata.py`: `read_meta(root, meta_cfg)`, `_tower_type(text, map)`.
- [ ] **P3.6** `peek_tower_type` — chicken/egg: chạy TRƯỚC khi load profile. Giải: đọc
  `metadata.tower_type` từ 1 **profile mặc định** (`profiles/_base.toml`) hoặc quét
  tất cả `profiles/*.toml` lấy union các pattern. → chốt: `_base.toml` chứa
  `[metadata]` dùng chung, các profile khác kế thừa.

**Verify:** 23 test + parity + chạy `tu_dung` nếu có data.

---

## Phase 4 — `[prompts]`

```toml
[prompts]
repair = """
Bạn là trợ lý sắp xếp thư mục phụ lục kiểm định. Sửa các 'issue' để mỗi hạng mục đạt:
• ≥{min_cong_tac} thư mục 'Công tác' theo cặp → SỐ CHẴN
• mỗi thư mục công tác: SỐ ẢNH CHẴN (ưu tiên ≤{prefer_images})
• luôn có 1 'Hình ảnh khác'
…
"""
vision = """Bạn phân loại ảnh kiểm định. Với mỗi ảnh chọn 'folder' đúng nhất…"""
```
- [ ] **P4.1** `agent_repair._SYSTEM` → `p.prompts.repair` (format với `structure.*`).
- [ ] **P4.2** `vision._PROMPT` → `p.prompts.vision`.
- [ ] **P4.3** Fallback: nếu profile thiếu `[prompts]` → prompt mặc định trong code.

**Verify:** 23 test + 1 run thật có agent_repair (tạo trạm lệch chuẩn) — log tool call OK.

---

## Phase 4 — prompt  ✅

- [x] `_SYSTEM` (agent_repair) + `_PROMPT` (vision) viết lại **TỔNG QUÁT** (không gắn
  SOP/BTS) và GIỮ trong code — chi tiết SOP đến từ danh sách issue + danh sách folder
  hợp lệ truyền runtime. KHÔNG có `[prompts]` trong profile (chốt với user).

## Phase 5 — 0 fallback + dọn + bàn giao  ✅

- [x] **P5.1** `rules/_base.toml` = TOÀN BỘ cơ chế SOP. `day_co.toml`/`tu_dung.toml`/
  `tests/rules_test.toml` → `extends = "_base"`.
- [x] **P5.2** `graphrun.config.loader.load_toml()` giải `extends` (deep-merge, đệ quy,
  bắt vòng lặp). `Config.load` dùng nó.
- [x] **P5.3** `Profile` — **0 giá trị mặc định trong code**. Thiếu section/field →
  `ProfileError` (chỉ rõ `[section] thiếu 'key'`). Bỏ `Profile.default()`.
- [x] **P5.4** `naming.parse` / `renaming.*` nhận pattern từ profile (`ts_pattern`,
  `ts_fallback`, `conform`, `build`, `primary_marker`) — bỏ mọi regex module-level.
- [x] **P5.5** `[folders].pair_names` — scaffold + agent split_folder/new_empty_pair
  dựng tên cặp thư mục từ config (hết hard-code "Công tác chuẩn bị "/"Công tác đo ").
- [x] **P5.6** `core/profile.py` → package `core/profile/` : `spec.py` (dataclass) +
  `names.py` (Names) + `profile.py` (Profile + load) + `__init__.py`.
- [x] **P5.7** `docs/PROFILE_SCHEMA.md` + `tests/test_profile.py` (0 fallback, extends).
- [ ] **P5.8** `HUONG_DAN_DUNG_TOOL.md §5` + `docs/TAO_SOP_MOI.md` (còn).

**Verify cuối:** ✅ 33 test · TQG00006 apply → `plan 110/16/12` · validator ✅ HỢP LỆ ·
`src/` KHÔNG còn chuỗi/regex SOP (chỉ vài warning-message trong metadata.py).

---

## Cái KHÔNG đưa vào config (vẫn là code, nhận tham số)

| Logic | Vì sao |
|---|---|
| Thuật toán `dot_range` (lo, lo+1, hi-1, hi) | không diễn đạt được bằng TOML; chỉ `hm_prefix/target_fmt` là config |
| `scaffold` tách thư mục lẻ (chia đôi ảnh) | thuật toán |
| Thứ tự dựng timestamp (parse → HHMMSS → EXIF → mtime) | thuật toán |
| Vòng reconcile + `verify` (HARD conservation) | kiến trúc, không được phép cấu hình |
| `image_root` dò folder đánh số | heuristic FS |

---

## Ước lượng

| Phase | Nội dung | Effort |
|---|---|---|
| 0 | `Profile` + validation + schema doc | ~3h |
| 1 | structure + folders | ~3h |
| 2 | filename + groups | ~4h |
| 3 | hang_muc + metadata (+ `_base.toml`) | ~4h |
| 4 | prompts | ~1h |
| 5 | dọn + docs + test | ~2h |
| | **Tổng** | **~2 ngày** |

Rủi ro chính: regression do đổi hàng loạt string cứng → lookup. Chặn bằng parity
TQG00006 + validator sau MỖI phase, không gộp.
