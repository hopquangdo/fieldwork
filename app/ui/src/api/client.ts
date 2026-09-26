import type { Feature, JobSummary } from "../state/types"

const API_URL = process.env.BTS_API_URL ?? "http://127.0.0.1:8765"

export async function listFeatures(): Promise<Feature[]> {
  const r = await fetch(`${API_URL}/features`)
  if (!r.ok) throw new Error(`GET /features failed (${r.status})`)
  return (await r.json()) as Feature[]
}

/** Start a run and return its job id (async). */
export async function startRun(
  feature: string,
  body: { input: string; output: string; rules?: string | null; overrides?: Record<string, unknown> },
): Promise<string> {
  const r = await fetch(`${API_URL}/features/${encodeURIComponent(feature)}/run`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ overrides: {}, ...body }),
  })
  if (!r.ok) throw new Error(`run failed (${r.status}): ${await r.text()}`)
  return ((await r.json()) as { job_id: string }).job_id
}

export async function getJob(id: string): Promise<JobSummary> {
  const r = await fetch(`${API_URL}/jobs/${id}`)
  if (!r.ok) throw new Error(`GET /jobs/${id} failed (${r.status})`)
  return (await r.json()) as JobSummary
}

/** Subscribe to per-node progress via SSE. Returns an unsubscribe fn.
 *  Uses fetch streaming (no global `EventSource` needed under Bun). */
export function streamJob(
  id: string,
  on: (event: string, data: unknown) => void,
): () => void {
  const ctrl = new AbortController()

  ;(async () => {
    const r = await fetch(`${API_URL}/jobs/${id}/events`, {
      headers: { accept: "text/event-stream" },
      signal: ctrl.signal,
    })
    if (!r.body) return
    const reader = r.body.pipeThrough(new TextDecoderStream()).getReader()
    let buf = ""
    for (;;) {
      const { value, done } = await reader.read()
      if (done) break
      buf += value
      const chunks = buf.split("\n\n")
      buf = chunks.pop() ?? ""
      for (const chunk of chunks) {
        let ev = "message"
        let data = ""
        for (const line of chunk.split("\n")) {
          if (line.startsWith("event:")) ev = line.slice(6).trim()
          else if (line.startsWith("data:")) data += line.slice(5).trim()
        }
        if (!data) continue
        try {
          on(ev, JSON.parse(data))
        } catch {
          /* ignore malformed frame */
        }
      }
    }
  })().catch(() => {
    /* aborted or network drop — polling in app.tsx still resolves the job */
  })

  return () => ctrl.abort()
}
