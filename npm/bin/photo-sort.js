#!/usr/bin/env node
// Mở UI (ui.exe); UI tự bật backend Python đi kèm. Tham số / env chuyển thẳng cho ui.exe.
"use strict"
const path = require("node:path")
const fs = require("node:fs")
const { spawnSync } = require("node:child_process")

const exe = path.join(__dirname, "..", "vendor", "photo-sort", "ui.exe")
if (!fs.existsSync(exe)) {
  console.error("Chưa có bản build (bước tải khi cài bị lỗi?). Chạy:  npm rebuild -g @hopquangdo/photo-sort")
  process.exit(1)
}
const r = spawnSync(exe, process.argv.slice(2), {
  stdio: "inherit",
  env: { ...process.env, PYTHONUTF8: "1" },
})
process.exit(r.status ?? 1)
