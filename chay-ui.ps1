# ============================================================================
#  chay-ui.ps1 — mở giao diện (UI): tự bật API + UI, điền sẵn thư mục.
#  Cần: uv (Python) + bun.  Nhấp đúp chay-ui.bat.
# ============================================================================

# --- SỬA Ở ĐÂY (để trống nếu muốn tự chọn trong UI) -----------------------
$INPUT           = ""      # thư mục trạm mặc định
$OUTPUT          = ""      # thư mục kết quả mặc định
$VERBOSE         = $false  # $true = UI mở sẵn chế độ log "Chi tiết"
$API_URL         = "http://127.0.0.1:8765"
# --------------------------------------------------------------------------
# UI luôn GHI THẬT + vòng AI sửa luôn bật.

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repo

if (-not (Get-Command bun -ErrorAction SilentlyContinue)) {
  Write-Host "Chưa có 'bun'. Cài bằng:  npm install -g bun   rồi mở lại cửa sổ." -ForegroundColor Yellow
  Read-Host "Enter để đóng"; exit 1
}

# 1) API chạy nền (cửa sổ riêng)
Write-Host "Bật API ($API_URL) ..."
Start-Process powershell -ArgumentList @(
  "-NoProfile", "-NoExit", "-Command",
  "Set-Location '$repo'; `$env:PYTHONUTF8='1'; uv run graphrun serve"
)
Start-Sleep -Seconds 3

# 2) UI
$env:BTS_API_URL = $API_URL
$env:BTS_INPUT   = $INPUT
$env:BTS_OUTPUT  = $OUTPUT
$env:BTS_VERBOSE = $(if ($VERBOSE) { "1" } else { "" })

Set-Location (Join-Path $repo "ui")
if (-not (Test-Path "node_modules")) { bun install }
Write-Host "Mở UI... (Ctrl+C để thoát; nhớ tắt cửa sổ API sau khi xong)"
bun run dev
