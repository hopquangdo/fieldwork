import { join, resolve } from "node:path"
import { createEffect, createSignal, For, onMount } from "solid-js"
import { useKeyboard, useTerminalDimensions } from "@opentui/solid"
import { getJob, listFeatures, startRun, streamJob } from "./api/client"
import { BUNDLED, WORKDIR, ownsBackend, restartBackend } from "./backend"
import { loadConfig, maskKey, saveConfig } from "./config"
import { formatLog } from "./state/format"
import type { Feature, LlmUsage, Report } from "./state/types"

// Defaults — override with BTS_INPUT / BTS_OUTPUT. Bản cài (npm) để trống; chạy từ repo thì điền trạm thử.
const REPO = resolve(import.meta.dir, "..", "..", "..")
const FALLBACK_INPUT = BUNDLED ? "" : join(REPO, "data", "RAW", "DBN00009_2")
const FALLBACK_OUTPUT = BUNDLED ? "" : join(REPO, ".output", "thu-DBN00009_2")

const nf = new Intl.NumberFormat("vi-VN")

/** " · 12.345 in · 678 out · 1.000 cache · ~123 VND" từ section ``llm_usage`` (không gọi LLM → toàn 0). */
/** 83_400 ms → "1 phút 23s"; < 1 phút → "12,3s". */
function elapsed(ms: number): string {
  const s = ms / 1000
  if (s < 60) return `${s.toFixed(1).replace(".", ",")}s`
  return `${Math.floor(s / 60)} phút ${Math.round(s % 60)}s`
}

function usageText(report: Report | null): string {
  const u = (report?.sections?.llm_usage ?? {}) as Partial<LlmUsage>
  const n = (x?: number) => nf.format(Math.round(x ?? 0))
  return ` · ${n(u.input_tokens)} in · ${n(u.output_tokens)} out · ` +
    `${n(u.cache_read_tokens)} cache · ~${n(u.cost_vnd)} VND`
}

function lineColor(l: string): string {
  const s = l.trimStart()
  if (s.startsWith("⏺")) return "#7dd3fc"
  if (s.startsWith("→")) return "#5eead4"
  if (s.startsWith("•")) return "#94a3b8"
  if (s.startsWith("✗") || s.startsWith("!") || s.startsWith("ERROR")) return "#f87171"
  if (s.startsWith("✓")) return "#4ade80"
  if (s.startsWith("⎿")) return "#9fb3c8"
  return "#cbd5e1"
}

type Field = "key" | "input" | "output"
const FIELDS: Field[] = ["key", "input", "output"]

export function App() {
  const dims = useTerminalDimensions()
  const [features, setFeatures] = createSignal<Feature[]>([])
  const [feature, setFeature] = createSignal("photo-sort")
  const [input, setInput] = createSignal(process.env.BTS_INPUT || FALLBACK_INPUT)
  const [output, setOutput] = createSignal(process.env.BTS_OUTPUT || FALLBACK_OUTPUT)
  const [compact, setCompact] = createSignal(process.env.BTS_VERBOSE !== "1")
  const [apiKey, setApiKey] = createSignal(loadConfig().apiKey ?? "")
  const [field, setField] = createSignal<Field>(apiKey() ? "input" : "key")
  const [lines, setLines] = createSignal<string[]>([])
  const [busy, setBusy] = createSignal(false)
  const [status, setStatus] = createSignal("Đang kết nối API…")

  let scroller: { scrollTo: (p: { x: number; y: number }) => void; scrollHeight: number } | undefined

  const push = (l: string) => setLines((x) => [...x, l])

  // follow the tail
  createEffect(() => {
    lines()
    queueMicrotask(() => scroller?.scrollTo({ x: 0, y: scroller.scrollHeight }))
  })

  onMount(async () => {
    try {
      const f = await listFeatures()
      setFeatures(f)
      if (f[0]) setFeature(f[0].name)
      setStatus("Tab: đổi ô  ·  chuột: bấm nút  ·  Esc: thoát")
    } catch (e) {
      setStatus(`API offline — mở cửa sổ khác: uv run photo-sort-engine serve  (${e instanceof Error ? e.message : e})`)
    }
  })

  const browse = async (which: "input" | "output") => {
    const cmd =
      "Add-Type -AssemblyName System.Windows.Forms;" +
      "$d=New-Object System.Windows.Forms.FolderBrowserDialog;" +
      "if($d.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK){$d.SelectedPath}"
    const proc = Bun.spawn(["powershell.exe", "-NoProfile", "-STA", "-Command", cmd], { stdout: "pipe" })
    const sel = (await new Response(proc.stdout).text()).trim()
    await proc.exited
    if (sel) (which === "input" ? setInput : setOutput)(sel)
  }

  /** Lưu key (APPDATA) + bật lại backend do UI quản để nhận key mới. */
  const saveKey = async () => {
    const key = apiKey().trim()
    saveConfig({ ...loadConfig(), apiKey: key || undefined })
    setField("input")
    if (!ownsBackend()) return setStatus(key ? "Đã lưu key — backend ngoài dùng key của nó" : "Đã xoá key")
    setStatus("Đã lưu key — đang bật lại backend…")
    try {
      await restartBackend(key || undefined)
      setStatus(key ? "Đã lưu key ✓" : "Đã xoá key — bước AI sẽ bị bỏ qua")
    } catch (e) {
      setStatus(`Backend lỗi: ${e instanceof Error ? e.message : e}`)
    }
  }

  const run = async () => {
    if (busy()) return
    if (!input().trim() || !output().trim()) return setStatus("Thiếu thư mục trạm / kết quả")
    setBusy(true)
    setLines([])
    setStatus("Đang chạy…")
    const t0 = Date.now()
    push(`▶ ${feature()}`)
    try {
      const id = await startRun(feature(), {
        input: input(),
        output: output(),
        overrides: {},
      })
      const stop = streamJob(id, (ev, d) => {
        if (ev === "log") {
          const { channel, message } = d as { channel: string; message: string }
          for (const ln of formatLog(channel, message, compact())) push(ln)
        } else if (ev === "error") {
          push(`✗ ${(d as { error: string }).error}`)
        }
        if (ev === "done" || ev === "error") stop()
      })
      let j = await getJob(id)
      while (j.status === "queued" || j.status === "running") {
        await new Promise((r) => setTimeout(r, 350))
        j = await getJob(id)
      }
      stop()
      push(j.status === "done" ? `✓ Hoàn tất${usageText(j.report)} · ${elapsed(Date.now() - t0)}` : `✗ ${j.error}`)
      const outDir = j.report?.sections?.output_dir as string | undefined
      if (j.status === "done" && outDir && outDir !== output()) push(`  thư mục kết quả đã có → ghi vào: ${outDir}`)
      setStatus(j.status === "done" ? `Xong — kết quả: ${outDir ?? output()} · báo cáo: ${join(WORKDIR, ".output")}` : "Lỗi")
    } catch (e) {
      push(`✗ ${e instanceof Error ? e.message : String(e)}`)
      setStatus("Lỗi")
    } finally {
      setBusy(false)
    }
  }

  useKeyboard((k) => {
    if (k.name === "escape") process.exit(0)
    if (k.ctrl && k.name === "c") process.exit(0)
    if (k.name === "tab") setField((f) => FIELDS[(FIELDS.indexOf(f) + 1) % FIELDS.length])
  })

  const logHeight = () => Math.max(3, dims().height - 11)

  return (
    <box style={{ width: dims().width, height: dims().height, flexDirection: "column", backgroundColor: "#0b1220" }}>
      <box style={{ flexDirection: "column", paddingLeft: 1, paddingRight: 1, flexShrink: 0 }}>
        <text fg="#e2e8f0"><b>{feature()}</b></text>
        <text fg="#64748b">{features().find((f) => f.name === feature())?.summary ?? ""}</text>

        <box style={{ flexDirection: "row", marginTop: 1 }}>
          <box style={{ width: 10, flexShrink: 0 }}>
            <text fg={field() === "key" ? "#fbbf24" : "#64748b"}>{field() === "key" ? "▶ API key" : "  API key"}</text>
          </box>
          {field() === "key" ? (
            <input style={{ flexGrow: 1, backgroundColor: "#111c2e" }} value={apiKey()} focused onInput={(v) => setApiKey(v)} onSubmit={() => void saveKey()} placeholder="dán key LLM (OpenRouter) rồi Enter để lưu" />
          ) : (
            <box style={{ flexGrow: 1, backgroundColor: "#111c2e" }} onMouseUp={() => setField("key")}>
              <text fg={apiKey() ? "#94a3b8" : "#f87171"}>{apiKey() ? maskKey(apiKey()) : "chưa có key — bước AI sẽ bị bỏ qua (bấm để nhập)"}</text>
            </box>
          )}
        </box>
        <box style={{ flexDirection: "row" }}>
          <box style={{ width: 10, flexShrink: 0 }}>
            <text fg={field() === "input" ? "#fbbf24" : "#64748b"}>{field() === "input" ? "▶ Trạm" : "  Trạm"}</text>
          </box>
          <input style={{ flexGrow: 1, backgroundColor: "#111c2e" }} value={input()} focused={field() === "input"} onInput={(v) => setInput(v)} onSubmit={() => void run()} placeholder="thư mục trạm (input)" />
        </box>
        <box style={{ flexDirection: "row" }}>
          <box style={{ width: 10, flexShrink: 0 }}>
            <text fg={field() === "output" ? "#fbbf24" : "#64748b"}>{field() === "output" ? "▶ Kết quả" : "  Kết quả"}</text>
          </box>
          <input style={{ flexGrow: 1, backgroundColor: "#111c2e" }} value={output()} focused={field() === "output"} onInput={(v) => setOutput(v)} onSubmit={() => void run()} placeholder="thư mục kết quả (output)" />
        </box>

        <box style={{ flexDirection: "row", marginTop: 1, gap: 1 }}>
          <Btn label="📁 Trạm" onClick={() => void browse("input")} />
          <Btn label="📁 Kết quả" onClick={() => void browse("output")} />
          <Btn label={compact() ? "○ Gọn" : "● Chi tiết"} onClick={() => setCompact((v) => !v)} />
          <Btn label={busy() ? "… đang chạy" : "▶ CHẠY"} accent onClick={() => void run()} />
        </box>
      </box>

      <scrollbox
        ref={(el: unknown) => (scroller = el as typeof scroller)}
        stickyScroll
        stickyStart="bottom"
        style={{
          height: logHeight(),
          marginTop: 1,
          border: true,
          borderColor: "#1e293b",
          backgroundColor: "#0b1220",
        }}
        contentOptions={{ flexDirection: "column" }}
      >
        <For each={lines()}>
          {(l) => (
            <box style={{ flexShrink: 0, height: 1, overflow: "hidden" }}>
              <text fg={lineColor(l)} style={{ wrapMode: "none", truncate: true }}>{l.length ? l : " "}</text>
            </box>
          )}
        </For>
      </scrollbox>

      <box style={{ flexShrink: 0, paddingLeft: 1 }}>
        <text fg="#64748b">{status()}</text>
      </box>
    </box>
  )
}

function Btn(props: { label: string; accent?: boolean; onClick: () => void }) {
  return (
    <box
      style={{ backgroundColor: props.accent ? "#f59e0b" : "#1e293b", paddingLeft: 1, paddingRight: 1, flexShrink: 0 }}
      onMouseUp={() => props.onClick()}
    >
      <text fg={props.accent ? "#0b1220" : "#e2e8f0"}>{props.label}</text>
    </box>
  )
}
