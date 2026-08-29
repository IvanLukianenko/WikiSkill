---
description: Initialize the WikiSkill workspace (raw traces / wiki / gated skills) in this project
allowed-tools: Bash(python3:*), Read
---

## Context

- Init output: !`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/wikiskills.py" init`

## Your task

The WikiSkill workspace was just initialized (or refreshed) — the output above shows the layout. Now:

1. Briefly explain the three layers to the user, mapping them to the framework (arXiv:2608.27454, Figure 2):
   - **Raw Layer** `.wikiskills/raw/` — immutable execution traces, captured automatically by the plugin's Stop hook from now on (git-ignored).
   - **Wiki Layer** `.wikiskills/wiki/` — persistent knowledge: `patterns/` (failure/success patterns), `index.md` (catalog), `log.md` (evolution log), `skill-impact.md` (proposal diffs + gating outcomes). Compounds across iterations, **never rolled back**.
   - **Skill Layer** (directory shown in the output) — each skill is `SKILL.md` + `PURPOSE.md`, versioned via snapshots and gated on validation against R_best.
2. Recommend the user add validation tasks to `.wikiskills/validation/tasks.md` (open it and show the template) — the suite is the paper's D_val, and gating is only as good as it is.
3. Tell them the workflow: work normally (sessions become training rollouts), then periodically run `/wikiskills:loop` for one full evolution iteration. The first loop will establish the R_best baseline automatically.

Do not create any wiki patterns or skills yet — those must be earned from real traces.
