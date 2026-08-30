@echo off
rem  Mo giao dien (UI): tu bat API + UI.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0chay-ui.ps1" %*
