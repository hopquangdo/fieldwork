// Turn a backend `on_log` (channel, message) event into display lines,
// mirroring infrastructure.observability.console.ConsoleRenderer. Returns [] to drop.
//
// compact=true collapses the noise: keeps node start/end + agent round header
// + first 3 issues + agent errors; drops per-tool-call trace and `step` lines.

const MARK: Record<string, string> = { ok: "✓", error: "✗", skipped: "○" }

export function formatLog(channel: string, message: string, compact = false): string[] {
  const p = message.split("\t")
  switch (channel) {
    case "node:start":
      return ["", `⏺ ${p[0]}`]
    case "node:end": {
      const [name, status, detail, secs] = p
      const body = detail || (status === "ok" ? "hoàn tất" : status)
      const tag = status !== "ok" ? `  ${MARK[status] ?? "?"}` : ""
      return [`  ⎿  ${body}${tag}  (${secs}s)`]
    }
    case "step":
      return compact ? [] : [`  ⎿  ${p.join("\t")}`]
    case "agent:head":
      return [`  ⎿  vòng ${p[1]} · ${p[0]} vấn đề cần sửa`]
    case "agent:issue":
      return [`       • ${p[0]} · ${p[1]} · ${p[2]}`]
    case "agent:tool":
      return compact ? [] : [`     → ${p[0]}`]
    case "agent:result":
      return compact ? [] : [`         ${p.join("; ")}`]
    case "agent:error":
      return [`         ✗ ${p.join("; ")}`]
    default:
      return []
  }
}
