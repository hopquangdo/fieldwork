# @hopquangdo/photo-sort

Sắp ảnh kiểm định cột BTS vào cấu trúc thư mục phụ lục. Windows x64.

```
npm i -g @hopquangdo/photo-sort     # lần đầu tự tải bản build
photo-sort                          # mở giao diện; backend tự chạy
```

Lần đầu: dán API key (OpenRouter) vào ô **API key** rồi Enter — lưu ở `%APPDATA%\photo-sort`.
Không có key vẫn chạy, bỏ bước AI.

Báo cáo + log: `%LOCALAPPDATA%\photo-sort\.output`. Không cần cài Python / Bun.

## Phát hành (người bảo trì)

Tự động bằng GitHub Actions (`.github/workflows/release.yml`):

```
git tag v0.1.1
git push origin v0.1.1
```

→ test → build `photo-sort-win-x64.zip` → GitHub Release `v0.1.1` → `npm publish` bản `0.1.1`.

Cần một lần: secret `NPM_TOKEN` (npm → Access Tokens → Automation) trong
Settings → Secrets and variables → Actions của repo `hopquangdo/fieldwork`. Repo phải **public**
để client tải được file Release (hoặc đổi `photoSort.distUrl` sang server của bạn).

Thử cài từ zip build trên máy: `PHOTO_SORT_DIST_URL=<đường dẫn zip> npm i -g ./npm`.
