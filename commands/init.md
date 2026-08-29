---
description: Initialize the WikiSkills workspace (traces / wiki / skill archive) in this project
allowed-tools: Bash(python3:*), Read
---

## Context

- Init output: !`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/wikiskills.py" init`

## Your task

The WikiSkills workspace was just initialized (or refreshed) — the output above shows the layout. Now:

1. Briefly explain to the user the three layers that now exist, mapping them to the WikiSkill framework (arXiv:2608.27454):
   - `.wikiskills/traces/` — raw execution experience, captured automatically by the plugin's Stop hook from now on (git-ignored).
   - `.wikiskills/wiki/` — the persistent knowledge wiki. It is injected into every new session and is **never rolled back**.
   - The skills directory (shown in the output) — executable skills, versioned via snapshots and gated on validation.
2. Recommend the user add one or two validation tasks to `.wikiskills/validation/tasks.md` (open it and show them the template format) so future skill updates can be gated objectively.
3. Tell them the workflow: just work normally; then periodically run `/wikiskills:loop` (or the individual steps `/wikiskills:consolidate` → `/wikiskills:evolve` → `/wikiskills:validate`).

Do not create any wiki pages or skills yet — those must be earned from real traces.
