/** Tự bật backend (``uv run photo-sort-engine serve``) nếu API chưa chạy; tắt theo UI khi thoát.
 *  Log backend ghi vào ``.output/backend.log`` (terminal đã dành cho UI).
 *  API key nhập trên UI truyền vào backend qua biến môi trường (env thắng .env). */
import { existsSync, mkdirSync, openSync } from "node:fs"
import { homedir } from "node:os"
import { dirname, join, resolve } from "node:path"
import type { Subprocess } from "bun"

const API_URL = process.env.BTS_API_URL ?? "http://127.0.0.1:8765"
// Bản đóng gói (ui.exe): có python\python.exe cạnh exe → dùng nó; không thì chạy từ repo bằng uv.
const BUNDLED_PY = join(dirname(process.execPath), "python", "python.exe")
const BUNDLED = existsSync(BUNDLED_PY)
const REPO = resolve(import.meta.dir, "..", "..", "..")
/** Thư mục làm việc của backend (báo cáo .output/, log). Bản cài: %LOCALAPPDATA%\photo-sort — không mất khi npm update. */
export const WORKDIR = BUNDLED
  ? join(process.env.LOCALAPPDATA || join(homedir(), ".local", "share"), "photo-sort")
  : REPO
export { BUNDLED }
// Mặc định khi người dùng chỉ nhập key (OpenRouter).
const LLM_DEFAULTS = { LLM_BASE_URL: "https://openrouter.ai/api/v1", LLM_MODEL_NAME: "google/gemini-2.5-flash" }

let proc: Subprocess | null = null // backend do UI bật (null = dùng backend có sẵn)

async function alive(): Promise<boolean> {
  try {
    return (await fetch(`${API_URL}/features`, { signal: AbortSignal.timeout(1000) })).ok
  } catch {
    return false
  }
}

function stop(): void {
  if (!proc) return
  try {
    // Windows: kill() chỉ dừng uv, python con vẫn sống → tắt cả cây tiến trình
    if (process.platform === "win32") Bun.spawnSync(["taskkill", "/PID", String(proc.pid), "/T", "/F"])
    else proc.kill()
  } catch {}
  proc = null
}

process.on("exit", stop)
process.on("SIGINT", () => { stop(); process.exit(0) })
process.on("SIGTERM", () => { stop(); process.exit(0) })

/** UI có tự quản backend không (false = backend ngoài: Docker / máy chủ / cửa sổ khác). */
export const ownsBackend = () => proc !== null

export async function ensureBackend(apiKey?: string): Promise<void> {
  if (await alive()) return // đã có backend chạy sẵn → dùng luôn
  if (process.env.BTS_BACKEND === "external") {
    // backend ở Docker / máy chủ: không tự bật, chỉ báo nếu chưa với tới
    throw new Error(`Không kết nối được backend ${API_URL} — kiểm tra Docker (docker compose up -d) / địa chỉ BTS_API_URL`)
  }

  const url = new URL(API_URL)
  const logDir = join(WORKDIR, ".output")
  mkdirSync(logDir, { recursive: true })
  const log = openSync(join(logDir, "backend.log"), "a")

  console.log(`Đang bật backend ${API_URL} ... (log: ${join(logDir, "backend.log")})`)
  const serve = ["serve", "--host", url.hostname, "--port", url.port || "8765"]
  const cmd = BUNDLED ? [BUNDLED_PY, "-m", "app.cli.commands", ...serve] : ["uv", "run", "photo-sort-engine", ...serve]
  const env: Record<string, string | undefined> = { ...process.env, PYTHONUTF8: "1" }
  if (apiKey) {
    env.LLM_API_KEY = apiKey
    for (const [k, v] of Object.entries(LLM_DEFAULTS)) env[k] ||= v
  }
  proc = Bun.spawn(cmd, { cwd: WORKDIR, env, stdout: log, stderr: log })

  for (let i = 0; i < 120; i++) { // chờ tối đa ~60s (lần đầu uv có thể phải cài gói)
    if (proc.exitCode !== null) throw new Error(`Backend thoát sớm (mã ${proc.exitCode}) — xem .output/backend.log`)
    if (await alive()) return
    await Bun.sleep(500)
  }
  stop()
  throw new Error("Backend không lên sau 60s — xem .output/backend.log")
}

/** Bật lại backend với key mới (chỉ khi UI đang tự quản backend). */
export async function restartBackend(apiKey?: string): Promise<void> {
  if (!proc) return
  stop()
  for (let i = 0; i < 20 && (await alive()); i++) await Bun.sleep(250) // chờ cổng nhả ra
  await ensureBackend(apiKey)
}
