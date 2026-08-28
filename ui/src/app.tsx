import { createSignal, Show } from "solid-js"
import { scanWorkspace, organizeStation, applyStation } from "./api/client"
import { StationList } from "./components/station-list"
import { WorkflowLog } from "./components/workflow-log"
import type { Station, WorkflowReport, WorkspaceReport } from "./state/types"

export function App() {
  const [root, setRoot] = createSignal("")
  const [report, setReport] = createSignal<WorkspaceReport>()
  const [run, setRun] = createSignal<WorkflowReport>()
  const [target, setTarget] = createSignal("")
  const [lines, setLines] = createSignal<string[]>([])
  const [busy, setBusy] = createSignal(false)

  const fail = (e: unknown) => setLines([`ERROR: ${e instanceof Error ? e.message : String(e)}`])

  const chooseFolder = async () => {
    if (busy()) return
    setBusy(true)
    try {
      const command = [
        "Add-Type -AssemblyName System.Windows.Forms;",
        "$d = New-Object System.Windows.Forms.FolderBrowserDialog;",
        "$d.Description = 'Select BTS workspace folder';",
        "if ($d.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) { $d.SelectedPath }",
      ].join(" ")
      const proc = Bun.spawn(["powershell.exe", "-NoProfile", "-STA", "-Command", command], { stdout: "pipe" })
      const selected = (await new Response(proc.stdout).text()).trim()
      await proc.exited
      if (selected) {
        setRoot(selected)
        await scanPath(selected)
      }
    } catch (e) {
      fail(e)
    } finally {
      setBusy(false)
    }
  }

  const scanPath = async (path: string) => {
    setBusy(true)
    setRun(undefined)
    setLines([`Scanning workspace: ${path}`])
    try {
      setReport(await scanWorkspace(path))
      setLines(["✓ Workspace scan complete."])
    } catch (e) {
      fail(e)
    } finally {
      setBusy(false)
    }
  }

  const dryRun = async (station?: Station) => {
    const path = station ? `${root()}\\${station.path}` : root()
    setTarget(path)
    setBusy(true)
    setRun(undefined)
    setLines([`Dry-run: ${path}`])
    try {
      setRun(await organizeStation(path, { dryRun: true }))
      setLines([`✓ Dry-run xong — xem kế hoạch bên dưới. Bấm "Apply" nếu ổn.`])
    } catch (e) {
      fail(e)
    } finally {
      setBusy(false)
    }
  }

  const apply = async () => {
    setBusy(true)
    setLines([`Applying: ${target()}`])
    try {
      const r = await applyStation(target())
      setRun(r)
      setLines([`✓ Đã áp dụng — ${r.exec.applied} thao tác, ${r.exec.failed} lỗi.`])
    } catch (e) {
      fail(e)
    } finally {
      setBusy(false)
    }
  }

  const canApply = () => !busy() && !!run() && !run()!.aborted && run()!.exec.status === "dry_run"

  return (
    <box flexDirection="column" height="100%" padding={2}>
      <box flexDirection="column" gap={1}>
        <text fg="#e8edf2"><b>BTS workspace organizer</b></text>
        <text fg="#9bb0bd">discover → meta → inventory → layout ↺vision → validate ↺repair → execute</text>
        <box flexDirection="row" gap={1}>
          <input flexGrow={1} value={root()} placeholder="Workspace folder" onInput={(v) => setRoot(v)} />
          <Button label="Browse" active={!busy()} onClick={chooseFolder} />
          <Button label="Scan" active={!busy() && !!root().trim()} onClick={() => scanPath(root().trim())} />
          <Button label="Dry-run all" active={!busy() && !!report()} onClick={() => dryRun()} />
          <Button label="Apply" active={canApply()} accent onClick={apply} />
        </box>
      </box>

      <scrollbox flexGrow={1} marginTop={1}>
        <box flexDirection="column" gap={2}>
          <Show when={report()}>
            {(w) => (
              <box flexDirection="column" gap={1}>
                <text>
                  ✓ {w().directories.toLocaleString()} folders   ✓ {w().files.toLocaleString()} files   ✓{" "}
                  {w().images.toLocaleString()} images
                </text>
                <StationList stations={w().stations} onOrganize={dryRun} />
              </box>
            )}
          </Show>
          <WorkflowLog lines={lines()} report={run()} />
        </box>
      </scrollbox>

      <text fg="#657784">{busy() ? "Working..." : canApply() ? "Dry-run sẵn sàng — bấm Apply" : "Ready"}</text>
    </box>
  )
}

function Button(props: { label: string; active: boolean; accent?: boolean; onClick: () => void }) {
  return (
    <box
      backgroundColor={!props.active ? "#273746" : props.accent ? "#f2b134" : "#31465a"}
      paddingLeft={1}
      paddingRight={1}
      onMouseUp={() => props.active && props.onClick()}
    >
      <text fg={!props.active ? "#657784" : props.accent ? "#101820" : "#e8edf2"}>{props.label}</text>
    </box>
  )
}
