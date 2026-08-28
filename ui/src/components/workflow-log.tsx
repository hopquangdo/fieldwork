import { For, Show } from "solid-js"
import type { WorkflowReport } from "../state/types"

type Props = {
  lines: string[]
  report?: WorkflowReport
}

const KIND_COLOR: Record<string, string> = {
  add: "#55d187",
  del: "#ed6a5a",
  move: "#5aa9e6",
  skip: "#657784",
  same: "#9bb0bd",
}
const SIGN: Record<string, string> = { add: "+ ", del: "- ", move: "→ ", skip: "  ", same: "  " }

export function WorkflowLog(props: Props) {
  return (
    <scrollbox flexGrow={1} stickyScroll={true}>
      <box flexDirection="column" gap={1} paddingTop={1}>
        <For each={props.lines}>{(line) => <text fg="#9bb0bd">{line}</text>}</For>

        <Show when={props.report}>
          {(r) => (
            <box flexDirection="column" gap={1}>
              <text fg="#e8edf2">
                <b>{r().station}</b>  ·  {r().towerType}  ·  {r().imagesBefore} → {r().imagesAfter} ảnh{" "}
                {r().imagesBefore === r().imagesAfter ? "✓" : "✗ ABORT"}
              </text>
              <text fg="#9bb0bd">
                {r().operations.mkdir} mkdir · {r().operations.move} move · {r().operations.rmdir} rmdir ·{" "}
                {r().repairIters} vòng sửa · {r().vision.length} ảnh mở vision · {r().exec.status}
              </text>

              <text fg="#dce7ee"><b>Bảng đếm hạng mục</b></text>
              <For each={r().counts}>
                {(c) => (
                  <text fg={c.even_folders ? "#9bb0bd" : "#ed6a5a"}>
                    {"  "}Mục {String(c.id).padStart(2)}  ·  {c.folders} thư mục {c.even_folders ? "✓" : "✗"}  ·{" "}
                    {c.images} ảnh  {c.note ? `· ${c.note}` : ""}
                  </text>
                )}
              </For>

              <text fg="#dce7ee"><b>Cây kết quả (diff)</b></text>
              <For each={r().tree.slice(0, 40)}>
                {(t) => (
                  <text fg={KIND_COLOR[t.kind] ?? "#9bb0bd"}>
                    {"  ".repeat(Math.min(t.depth, 4))}{SIGN[t.kind] ?? "  "}{t.label}
                  </text>
                )}
              </For>

              <Show when={r().gaps.length}>
                <text fg="#f2b134"><b>Thiếu / cần nhặt bù</b></text>
                <For each={r().gaps}>{(g) => <text fg="#f2b134">{"  ⚠ "}{g}</text>}</For>
              </Show>

              <Show when={r().unresolved.length}>
                <text fg="#f2b134">{"  Chưa giải: "}{r().unresolved.join(", ")}</text>
              </Show>

              <Show when={r().errors.length}>
                <text fg="#ed6a5a"><b>HARD fail</b></text>
                <For each={r().errors}>{(e) => <text fg="#ed6a5a">{"  ! "}{e}</text>}</For>
              </Show>
            </box>
          )}
        </Show>
      </box>
    </scrollbox>
  )
}
