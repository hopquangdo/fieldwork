import { For } from "solid-js"
import type { Station } from "../state/types"

type Props = {
  stations: Station[]
  onOrganize: (station: Station) => void
}

export function StationList(props: Props) {
  return (
    <box flexDirection="column" gap={1}>
      <text fg="#dce7ee"><b>Stations</b></text>
      <For each={props.stations}>
        {(station) => (
          <box flexDirection="row" gap={2}>
            <text fg={station.status === "unknown" ? "#f2b134" : "#55d187"}>
              {station.status === "unknown" ? "⚠" : "✓"}
            </text>
            <text flexGrow={1}>{station.name}</text>
            <text fg="#9bb0bd">{station.imageCount.toLocaleString()} images</text>
            <box
              backgroundColor="#273746"
              paddingLeft={1}
              paddingRight={1}
              onMouseUp={() => props.onOrganize(station)}
            >
              <text fg="#f2b134">Dry-run</text>
            </box>
          </box>
        )}
      </For>
    </box>
  )
}
