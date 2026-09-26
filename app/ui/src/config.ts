/** Cấu hình người dùng (API key LLM) — lưu ở %APPDATA%\photo-sort\config.json, ngoài repo / gói cài. */
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs"
import { homedir } from "node:os"
import { join } from "node:path"

export type UserConfig = { apiKey?: string }

const DIR = join(process.env.APPDATA || join(homedir(), ".config"), "photo-sort")
const FILE = join(DIR, "config.json")

export function loadConfig(): UserConfig {
  try {
    return existsSync(FILE) ? (JSON.parse(readFileSync(FILE, "utf-8")) as UserConfig) : {}
  } catch {
    return {}
  }
}

export function saveConfig(cfg: UserConfig): void {
  mkdirSync(DIR, { recursive: true })
  writeFileSync(FILE, JSON.stringify(cfg, null, 2), "utf-8")
}

/** "••••••1a2b" — chỉ lộ 4 ký tự cuối. */
export function maskKey(key: string): string {
  return key ? "•".repeat(Math.min(12, Math.max(0, key.length - 4))) + key.slice(-4) : ""
}
