# ============================================================================
#  chay.ps1 — sắp ảnh 1 trạm, chỉ cần chạy file này.
#  Kéo-thả thư mục trạm vào chay.bat, HOẶC sửa $INPUT bên dưới rồi chạy.
# ============================================================================

# --- SỬA Ở ĐÂY -------------------------------------------------------------
$INPUT   = "D:\Workspace\Client Project\windows-computer-use-agent\data\TQG00006_Chiêm Hóa, Tuyên Quang-20260828T031314Z-1-001\unprocessed\TQG00006_Chiêm Hóa, Tuyên Quang"
$OUTPUT  = ""          # để trống = tạo thư mục "<tên trạm> - da sap" cạnh input
$APPLY   = $true       # $true = ghi thật ; $false = chạy thử (dry-run)
$COMPACT = $false      # $true = log gọn (chỉ tóm tắt mỗi node)
# (vòng AI sửa LUÔN bật — muốn tắt: thêm  --set agent_repair=false  vào $flags)
# --------------------------------------------------------------------------

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repo

if ($args.Count -ge 1 -and $args[0]) { $INPUT = $args[0] }        # thư mục kéo-thả
if (-not $OUTPUT) {
  $name = Split-Path $INPUT -Leaf
  $OUTPUT = Join-Path (Split-Path $INPUT -Parent) "$name - da sap"
}

$flags = @()
if (-not $APPLY) { $flags += "--dry-run" }
if ($COMPACT)    { $flags += "--compact" }

Write-Host "TRẠM   : $INPUT"
Write-Host "KẾT QUẢ: $OUTPUT"
Write-Host ("CHẾ ĐỘ : " + $(if ($APPLY) { "GHI THẬT" } else { "CHẠY THỬ" }) + " + AI sửa")
Write-Host ("-" * 70)

$env:PYTHONUTF8 = "1"
uv run photo-sort "$INPUT" "$OUTPUT" @flags
$code = $LASTEXITCODE

Write-Host ("-" * 70)
if ($code -eq 0) {
  Write-Host "XONG. Mở thư mục kết quả..."
  if (Test-Path $OUTPUT) { explorer $OUTPUT }
} else {
  Write-Host "CÓ LỖI (mã $code) — xem log phía trên / file .output\*.json"
}
Read-Host "`nEnter để đóng"
