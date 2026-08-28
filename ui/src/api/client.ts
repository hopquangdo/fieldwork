import type { WorkflowReport, WorkspaceReport } from "../state/types"

const API_URL = process.env.BTS_API_URL ?? "http://127.0.0.1:8765"

type WorkspacePayload = {
  root: string
  directories: number
  files: number
  images: number
  stations: Array<{ name: string; path: string; image_count: number }>
}

export async function scanWorkspace(root: string): Promise<WorkspaceReport> {
  const payload = await post<WorkspacePayload>("/scan", { root })
  return {
    root: payload.root,
    directories: payload.directories,
    files: payload.files,
    images: payload.images,
    stations: payload.stations.map((s) => ({
      name: s.name,
      path: s.path,
      imageCount: s.image_count,
      status: s.name.toLowerCase().startsWith("unknown") ? "unknown" : "ready",
    })),
  }
}

/** Dry-run by default — computes the plan without touching disk. */
export function organizeStation(root: string, opts: { dryRun?: boolean; noVision?: boolean } = {}) {
  return runOrganize("/organize", { root, dry_run: opts.dryRun ?? true, no_vision: opts.noVision ?? false })
}

/** Apply: re-run and write to disk. */
export function applyStation(root: string) {
  return runOrganize("/apply", { root })
}

async function runOrganize(path: string, body: Record<string, unknown>): Promise<WorkflowReport> {
  const p = await post<any>(path, body)
  return {
    station: p.station ?? "",
    towerType: p.tower_type ?? "",
    imagesBefore: p.images_before ?? 0,
    imagesAfter: p.images_after ?? 0,
    aborted: Boolean(p.aborted),
    repairIters: p.repair_iters ?? 0,
    counts: p.counts ?? [],
    tree: p.tree ?? [],
    vision: p.vision ?? [],
    gaps: p.gaps ?? [],
    unresolved: p.unresolved ?? [],
    manualReview: p.manual_review ?? [],
    exec: p.exec ?? { status: "", applied: 0, failed: 0, failures: [] },
    operations: p.operations ?? { mkdir: 0, move: 0, rmdir: 0, total: 0 },
    steps: p.steps ?? [],
    errors: p.errors ?? [],
  }
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`${path} failed (${res.status}): ${await res.text()}`)
  return (await res.json()) as T
}
