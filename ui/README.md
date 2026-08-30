# ui — photo-sort (terminal UI)

Bun + SolidJS + OpenTUI. Nói chuyện với HTTP API của `graphrun`.

## Chạy

Cần **Bun** (https://bun.sh). Kiểm tra: `bun --version`.

```bash
# 1. API (ở gốc repo)
uv run graphrun serve            # http://127.0.0.1:8765

# 2. UI (thư mục ui/)
cd ui
bun install                      # lần đầu
bun run dev
```

## Điền sẵn để "chỉ ấn Chạy"

Đặt biến môi trường trước khi `bun run dev` — các ô sẽ tự điền:

| Biến | Ý nghĩa |
|---|---|
| `BTS_INPUT` | thư mục trạm mặc định |
| `BTS_OUTPUT` | thư mục kết quả mặc định |
| `BTS_VERBOSE=1` | mở sẵn log "Chi tiết" (mặc định: Gọn) |
| `BTS_API_URL` | địa chỉ API (mặc định `http://127.0.0.1:8765`) |

UI **luôn GHI THẬT** và **vòng AI sửa luôn bật** — không có nút tắt.

PowerShell:

```powershell
$env:BTS_INPUT  = "D:\...\unprocessed\TQG00006_Chiêm Hóa, Tuyên Quang"
$env:BTS_OUTPUT = "D:\...\ket-qua"
cd ui; bun run dev
```

## Luồng

1. Hai ô thư mục **trạm** + **kết quả** đã điền sẵn (đổi bằng cách gõ, hoặc nút `📁`).
   `Tab` = chuyển ô, `Esc` = thoát.
2. Nút `Gọn / Chi tiết` = mức chi tiết của log.
3. Bấm `▶ CHẠY` — luôn ghi thật: copy trạm sang output rồi sắp tại chỗ (`move` không đè,
   có journal nên resume được). `validate` thấy hạng mục lệch chuẩn → AI tự sửa rồi kiểm lại.
4. Log chảy trực tiếp từng bước `⏺ / ⎿ / →`, tự cuộn xuống dòng mới nhất.
