/**
 * WikiSkills plugin for opencode — trace capture (layer 1 of WikiSkill,
 * arXiv:2608.27454).
 *
 * On session.idle, writes a compact per-session trace digest into
 * .wikiskills/traces/, in the same schema the Claude Code hook uses, so the
 * consolidate/evolve/validate commands work identically under opencode.
 * No-ops until the project has a .wikiskills/ workspace (run the
 * wikiskills-init command first).
 *
 * Install: copy into .opencode/plugin/ (opencode/install.sh does this).
 */

import * as fs from "node:fs"
import * as path from "node:path"

const MAX_TEXT = 400
const MAX_LAST = 1200
const MAX_ITEMS = 25

const clip = (s, n = MAX_TEXT) => {
  const t = String(s ?? "").replace(/\s+/g, " ").trim()
  return t.length <= n ? t : t.slice(0, n - 1) + "…"
}

const findRoot = (start) => {
  let d = path.resolve(start || process.cwd())
  for (;;) {
    const candidate = path.join(d, ".wikiskills")
    if (fs.existsSync(candidate) && fs.statSync(candidate).isDirectory()) return candidate
    const parent = path.dirname(d)
    if (parent === d) return null
    d = parent
  }
}

export const WikiSkillsPlugin = async ({ client, directory, worktree }) => {
  const projectDir = worktree || directory || process.cwd()

  const captureSession = async (sessionID) => {
    const root = findRoot(projectDir)
    if (!root || !sessionID) return
    let messages = []
    try {
      const res = await client.session.messages({ path: { id: sessionID } })
      messages = res?.data ?? []
    } catch {
      return
    }

    const userRequests = []
    const errors = []
    const tools = {}
    let lastAssistant = ""

    for (const msg of messages) {
      const role = msg?.info?.role
      for (const part of msg?.parts ?? []) {
        if (part.type === "text" && part.text) {
          if (role === "assistant") lastAssistant = clip(part.text, MAX_LAST)
          else if (role === "user" && !part.synthetic) userRequests.push(clip(part.text))
        } else if (part.type === "tool") {
          const name = part.tool || "?"
          tools[name] = (tools[name] || 0) + 1
          if (part.state?.status === "error") {
            errors.push(clip(part.state.error || part.state.output || "tool error"))
          }
        }
      }
    }

    const tracesDir = path.join(root, "traces")
    fs.mkdirSync(tracesDir, { recursive: true })
    const safeSid = String(sessionID).replace(/[^A-Za-z0-9_-]/g, "").slice(0, 64) || "unknown"
    const file = path.join(tracesDir, `trace-${safeSid}.json`)

    let firstSeen = new Date().toISOString().replace(/\.\d+Z$/, "Z")
    try {
      firstSeen = JSON.parse(fs.readFileSync(file, "utf8")).first_seen || firstSeen
    } catch {}

    const digest = {
      session_id: sessionID,
      agent: "opencode",
      first_seen: firstSeen,
      updated: new Date().toISOString().replace(/\.\d+Z$/, "Z"),
      cwd: projectDir,
      transcript_path: null,
      user_requests: userRequests.slice(-MAX_ITEMS),
      tools_used: tools,
      errors: errors.slice(-MAX_ITEMS),
      last_assistant_message: lastAssistant,
      consolidated: false,
    }
    const tmp = file + ".tmp"
    fs.writeFileSync(tmp, JSON.stringify(digest, null, 2) + "\n")
    fs.renameSync(tmp, file)
  }

  return {
    event: async ({ event }) => {
      try {
        if (event?.type === "session.idle") {
          await captureSession(event.properties?.sessionID)
        }
      } catch {
        // Trace capture must never break the session.
      }
    },
  }
}
