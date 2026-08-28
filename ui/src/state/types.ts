export type Station = {
  name: string
  path: string
  imageCount: number
  status: "ready" | "unknown"
}

export type WorkspaceReport = {
  root: string
  directories: number
  files: number
  images: number
  stations: Station[]
}

export type WorkflowStep = {
  name: string
  status: "ok" | "error" | "skipped"
  detail: string
}

export type CountRow = {
  id: number
  folders: number
  even_folders: boolean
  images: number
  note: string
}

export type TreeRow = {
  kind: "add" | "del" | "move" | "skip" | "same"
  label: string
  depth: number
}

export type VisionRow = {
  q: string
  folder: string | null
  blueprint: boolean
  confidence: number
  attempt: number
}

export type WorkflowReport = {
  station: string
  towerType: string
  imagesBefore: number
  imagesAfter: number
  aborted: boolean
  repairIters: number
  counts: CountRow[]
  tree: TreeRow[]
  vision: VisionRow[]
  gaps: string[]
  unresolved: string[]
  manualReview: number[]
  exec: { status: string; applied: number; failed: number; failures: string[] }
  operations: { mkdir: number; move: number; rmdir: number; total: number }
  steps: WorkflowStep[]
  errors: string[]
}
