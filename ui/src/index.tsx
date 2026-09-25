import { render } from "@opentui/solid"
import { App } from "./app"
import { ensureBackend } from "./backend"
import { loadConfig } from "./config"

await ensureBackend(loadConfig().apiKey)
render(() => <App />)
