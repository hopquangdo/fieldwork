#!/usr/bin/env node
// postinstall: tải bản build sẵn (Python + backend .pyc + ui.exe) về vendor/.
//   Nguồn: package.json → photoSort.distUrl ({version} = version của package).
//   Ghi đè: PHOTO_SORT_DIST_URL=<url hoặc đường dẫn .zip trên máy>  (test / mirror nội bộ).
"use strict"
const fs = require("node:fs")
const path = require("node:path")
const { execFileSync } = require("node:child_process")
const { Readable } = require("node:stream")
const { pipeline } = require("node:stream/promises")

const pkg = require("./package.json")
const VENDOR = path.join(__dirname, "vendor")
const APP = path.join(VENDOR, "photo-sort")
const STAMP = path.join(VENDOR, ".version")

async function download(src, dest) {
  if (!/^https?:\/\//.test(src)) return fs.copyFileSync(src, dest) // file trên máy
  const res = await fetch(src, { redirect: "follow" })
  if (!res.ok || !res.body) throw new Error(`HTTP ${res.status} khi tải ${src}`)
  const total = Number(res.headers.get("content-length")) || 0
  let got = 0
  let last = 0
  const body = Readable.fromWeb(res.body)
  body.on("data", (c) => {
    got += c.length
    const pct = total ? Math.floor((got / total) * 100) : 0
    if (pct >= last + 10) {
      last = pct
      console.log(`  ${pct}% (${(got / 1e6).toFixed(0)} MB)`)
    }
  })
  await pipeline(body, fs.createWriteStream(dest))
}

function extract(zip, dir) {
  try {
    // tar.exe của Windows (bsdtar, có từ Win10) — không lấy nhầm GNU tar của Git Bash
    const tar = path.join(process.env.SystemRoot || "C:\\Windows", "System32", "tar.exe")
    execFileSync(tar, ["-xf", zip, "-C", dir], { stdio: "inherit" })
  } catch {
    execFileSync("powershell.exe", ["-NoProfile", "-Command",
      `Expand-Archive -LiteralPath '${zip}' -DestinationPath '${dir}' -Force`], { stdio: "inherit" })
  }
}

async function main() {
  if (process.platform !== "win32" || process.arch !== "x64") {
    console.warn("photo-sort hiện chỉ có bản Windows x64 — bỏ qua tải bản build.")
    return
  }
  if (fs.existsSync(path.join(APP, "ui.exe")) && fs.existsSync(STAMP) &&
      fs.readFileSync(STAMP, "utf-8").trim() === pkg.version) return // đã có đúng bản

  const src = process.env.PHOTO_SORT_DIST_URL || pkg.photoSort.distUrl.replace("{version}", pkg.version)
  console.log(`photo-sort: tải bản ${pkg.version} từ\n  ${src}`)
  fs.rmSync(VENDOR, { recursive: true, force: true })
  fs.mkdirSync(VENDOR, { recursive: true })
  const zip = path.join(VENDOR, "dist.zip")
  await download(src, zip)
  console.log("photo-sort: giải nén…")
  extract(zip, VENDOR)
  fs.rmSync(zip, { force: true })
  if (!fs.existsSync(path.join(APP, "ui.exe"))) {
    throw new Error("giải nén xong nhưng không thấy photo-sort/ui.exe — file zip sai cấu trúc?")
  }
  fs.writeFileSync(STAMP, pkg.version)
  console.log("photo-sort: xong. Gõ  photo-sort  để mở.")
}

main().catch((e) => {
  console.error(`photo-sort: cài bản build thất bại — ${e.message}`)
  console.error("  Thử lại: npm rebuild -g @hopquangdo/photo-sort")
  process.exit(1)
})
