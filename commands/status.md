---
description: Show WikiSkill state — iteration, R_best, pending traces, patterns, skills
allowed-tools: Bash(python3:*), Read
---

## Context

- Status: !`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/wikiskills.py" status`

## Your task

Present the status above in a short, readable summary and recommend the single most useful next action:

- Not initialized → `/wikiskills:init`.
- R_best "not baselined yet" and validation tasks exist → `/wikiskills:validate --baseline`.
- R_best = 1.00 → evolution is early-stopped; suggest adding harder tasks to `.wikiskills/validation/tasks.md`.
- Pending traces ≥ 3 → `/wikiskills:consolidate` (or the full `/wikiskills:loop`).
- Wiki grew since the last proposal (compare log.md against skill-impact.md) → `/wikiskills:evolve`.
- A skill was snapshotted but `wiki/skill-impact.md` has no entry for it → `/wikiskills:validate <skill>`.
- Otherwise → the loop is healthy; nothing needed right now.
