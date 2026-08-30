@echo off
rem  Nhấp đúp để chạy, hoặc kéo-thả thư mục trạm lên file này.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0chay.ps1" %*
