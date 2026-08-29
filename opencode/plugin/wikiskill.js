/**
 * WikiSkill plugin for opencode — Raw Layer trace capture for the WikiSkill
 * framework (arXiv:2608.27454 §3.1).
 *
 * On session.idle, writes into .wikiskill/raw/traces/ (same schema as the
 * Claude Code hook, so consolidate/evolve/validate work identically):
 *   trace-<session>.json       compact digest
 *   trace-<session>.log.jsonl  raw message log (capped), for deep root-cause
 *                              analysis by the Wiki Maintainer / Skill Proposer
 *
 * No-ops until the project has a .wikiskill/ workspace (run wikiskill-init).
 * Install: copy into .opencode/plugin/ (opencode/install.sh does this).
 */

import * as fs from "node:fs"
import * as path from "node:path"

const MAX_TEXT = 400
const MAX_LAST = 1200
const MAX_ITEMS = 25
const DEFAULT_MAX_RAW_BYTES = 2000000

const clip = (s, n = MAX_TEXT) => {
  const t = String(s ?? "").replace(/\s+/g, " ").trim()
  return t.length <= n ? t : t.slice(0, n - 1) + "…"
}

const findRoot = (start) => {
  let d = path.resolve(start || process.cwd())
  for (;;) {
    const candidate = path.join(d, ".wikiskill")
    if (fs.existsSync(candidate) && fs.statSync(candidate).isDirectory()) return candidate
    const parent = path.dirname(d)
    if (parent === d) return null
    d = parent
  }
}

const readJson = (file) => {
  try {
    return JSON.parse(fs.readFileSync(file, "utf8"))
  } catch {
    return null
  }
}

export const WikiSkillPlugin = async ({ client, directory, worktree }) => {
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

    const cfg = readJson(path.join(root, "config.json")) || {}
    const iteration = (readJson(path.join(root, "state.json")) || {}).iteration ?? 0

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

    const tracesDir = path.join(root, "raw", "traces")
    fs.mkdirSync(tracesDir, { recursive: true })
    const safeSid = String(sessionID).replace(/[^A-Za-z0-9_-]/g, "").slice(0, 64) || "unknown"
    const digestFile = path.join(tracesDir, `trace-${safeSid}.json`)
    const rawLogFile = path.join(tracesDir, `trace-${safeSid}.log.jsonl`)

    // Raw log: one JSON line per message, capped from the tail.
    let haveLog = false
    try {
      const maxBytes = Number(cfg.max_raw_log_bytes) || DEFAULT_MAX_RAW_BYTES
      const lines = messages.map((m) => JSON.stringify(m))
      let total = 0
      const kept = []
      for (let i = lines.length - 1; i >= 0; i--) {
        total += lines[i].length + 1
        if (total > maxBytes) break
        kept.unshift(lines[i])
      }
      fs.writeFileSync(rawLogFile + ".tmp", kept.join("\n") + "\n")
      fs.renameSync(rawLogFile + ".tmp", rawLogFile)
      haveLog = true
    } catch {}

    const prev = readJson(digestFile) || {}
    const nowIso = () => new Date().toISOString().replace(/\.\d+Z$/, "Z")
    const digest = {
      session_id: sessionID,
      agent: "opencode",
      iteration: prev.iteration ?? iteration,
      first_seen: prev.first_seen || nowIso(),
      updated: nowIso(),
      cwd: projectDir,
      transcript_path: null,
      raw_log: haveLog ? rawLogFile : null,
      user_requests: userRequests.slice(-MAX_ITEMS),
      tools_used: tools,
      errors: errors.slice(-MAX_ITEMS),
      last_assistant_message: lastAssistant,
      consolidated: false,
    }
    fs.writeFileSync(digestFile + ".tmp", JSON.stringify(digest, null, 2) + "\n")
    fs.renameSync(digestFile + ".tmp", digestFile)
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
