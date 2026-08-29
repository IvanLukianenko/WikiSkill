---
description: Show WikiSkills state — pending traces, wiki pages, skills, validations
allowed-tools: Bash(python3:*), Read
---

## Context

- Status: !`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/wikiskills.py" status`

## Your task

Present the status above to the user in a short, readable summary and recommend the single most useful next action:

- Not initialized → suggest `/wikiskills:init`.
- Pending traces ≥ 3 → suggest `/wikiskills:consolidate` (or `/wikiskills:loop`).
- Wiki has grown since the last evolution (check `.wikiskills/state.json` log) → suggest `/wikiskills:evolve`.
- A skill was evolved but never validated → suggest `/wikiskills:validate`.
- Otherwise → say the loop is healthy and nothing is needed right now.
