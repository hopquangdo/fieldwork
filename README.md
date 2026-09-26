# photo-sort

Sắp ảnh kiểm định cột BTS vào thư mục phụ lục. Chạy trên Windows 64-bit.

## Cách 1: cài qua npm (khuyên dùng)

Cần [Node.js](https://nodejs.org) ≥ 18.

```
npm i -g @hopquangdo/photo-sort
photo-sort
```

## Cách 2: chạy trực tiếp từ repo

Cần [Git](https://git-scm.com), [uv](https://docs.astral.sh/uv/) và [Bun](https://bun.sh).

```
git clone https://github.com/hopquangdo/fieldwork.git
cd fieldwork
uv sync
cd app/ui
bun install
bun run dev
```

Các lần sau chỉ cần chạy:

```
cd fieldwork/app/ui
bun run dev
```

## Dùng giao diện

1. **API key:** dán key rồi bấm Enter. Chỉ làm lần đầu.
2. **Thư mục trạm:** chọn thư mục ảnh.
3. **Thư mục kết quả:** chọn nơi lưu kết quả.
4. Bấm **▶ CHẠY**.

`Tab` để chuyển ô. `Esc` để thoát.

## Cập nhật

```
npm i -g @hopquangdo/photo-sort@latest      # cách 1
git pull && uv sync                         # cách 2 (trong thư mục fieldwork)
```

## Gỡ

```
npm rm -g @hopquangdo/photo-sort            # cách 1
```
Cách 2: xoá thư mục `fieldwork`.

## Lưu ý

- **Ảnh gốc:** giữ nguyên. Kết quả là bản copy.
- **Thư mục kết quả đã có dữ liệu:** kết quả ghi sang `(2)`, `(3)`…
- **Không có key:** vẫn chạy được, nhưng bỏ qua bước AI.
- **Báo cáo:** `%LOCALAPPDATA%\photo-sort\.output` (cách 1), `fieldwork\.output` (cách 2)
- **Lỗi khi cài (cách 1):**
  ```
  npm rebuild -g @hopquangdo/photo-sort
  ```
