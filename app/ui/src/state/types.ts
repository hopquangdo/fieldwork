export type Feature = { name: string; summary: string }

export type Stage = { name: string; status: "ok" | "error" | "skipped"; detail: string; seconds: number }

export type CountRow = {
  id: number
  folders: number
  even_folders: boolean
  images: number
  note: string
}

export type Report = {
  feature: string
  target: string
  run_id: string
  aborted: boolean
  stages: Stage[]
  sections: Record<string, unknown>
  errors: string[]
}

export type JobSummary = {
  id: string
  feature: string
  status: "queued" | "running" | "done" | "error"
  created: number
  error: string | null
  report: Report | null
}

/** ``report.sections.llm_usage`` — token + chi phí cộng dồn cả lượt chạy. */
export type LlmUsage = {
  model: string
  llm_calls: number
  input_tokens: number
  output_tokens: number
  cache_read_tokens: number
  cost_usd: number
  cost_vnd: number
}
