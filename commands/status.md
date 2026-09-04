---
description: Show WikiSkill state — iteration, R_best, pending traces, patterns, skills
allowed-tools: Bash(python3:*), Read
---

## Context

- Status: !`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/wikiskill.py" status`

## Your task

Present the status above in a short, readable summary and recommend the single most useful next action:

- Not initialized → `/wikiskill:init`.
- R_best "not baselined yet" and validation tasks exist → `/wikiskill:validate --baseline`.
- Suite "CHANGED since baseline" → `/wikiskill:validate --baseline` (re-anchors R_best on the new suite).
- R_best = 1.00 with an unchanged suite → run `/wikiskill:loop`: its harvesting adds trace-derived tasks, which re-anchors R_best and unblocks evolution.
- Pending traces ≥ 3 → `/wikiskill:consolidate` (or the full `/wikiskill:loop`).
- Wiki grew since the last proposal (compare log.md against skill-impact.md) → `/wikiskill:evolve`.
- A skill was snapshotted but `wiki/skill-impact.md` has no entry for it → `/wikiskill:validate <skill>`.
- Otherwise → the loop is healthy; nothing needed right now.
