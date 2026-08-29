---
description: Configure which model each WikiSkill evolution agent uses (consolidator / evolver / validator)
argument-hint: [consolidator=<model>] [evolver=<model>] [validator=<model>] | show | reset
allowed-tools: Bash(python3:*), Bash(cp:*), Bash(ls:*), Read, Write, Edit, Glob
---

## Context

- Arguments: "$ARGUMENTS"
- Plugin agents directory: !`ls "${CLAUDE_PLUGIN_ROOT}/agents"` (root: `${CLAUDE_PLUGIN_ROOT}/agents`)
- Current overrides in project: !`ls .claude/agents/ 2>/dev/null || echo "(none)"`

## Your task

Manage per-project model assignment for the three WikiSkill agents. Mechanism: Claude Code resolves same-named agents by precedence — a copy in the project's `.claude/agents/` overrides the plugin's agent — so a model override is a project-level copy of the plugin agent file with its `model:` frontmatter line changed. Valid model values: `haiku`, `sonnet`, `opus`, `inherit` (use the main conversation's model), or a full model ID.

**`show` (or no arguments):** read the `model:` line of any overrides in `.claude/agents/wikiskill-*.md` (agents without an override run the plugin default, `inherit`) and the `agent_models` record in `.wikiskill/config.json`; report the effective model per agent and stop.

**`reset`:** delete `.claude/agents/wikiskill-consolidator.md`, `wikiskill-evolver.md`, `wikiskill-validator.md` if present, remove `agent_models` from `.wikiskill/config.json`, and confirm that all agents are back to the plugin default.

**Assignments** (e.g. `consolidator=haiku evolver=opus`): for each `<agent>=<model>` pair:

1. Copy the plugin source `${CLAUDE_PLUGIN_ROOT}/agents/wikiskill-<agent>.md` to `.claude/agents/wikiskill-<agent>.md` (overwrite an existing override — it is a derived file).
2. In the copy, set the frontmatter line to `model: <model>`.
3. Record the choice in `.wikiskill/config.json` under `"agent_models": {"<agent>": "<model>", ...}` (merge with existing entries) so the assignment is visible in the repo and survives plugin updates as documentation of intent.

Then report the effective model per agent, and note that overrides are frozen copies: after a plugin update, re-running `/wikiskill:models` with the same arguments refreshes them from the new plugin version.

**Guidance to share when relevant** (from the paper, arXiv:2608.27454):
- **validator** should normally stay `inherit`: in the paper, validation is a rollout of the *Inference Agent* itself (§3.2.4) — gating must measure what *your* everyday model achieves with the skill, not what a different model could.
- **consolidator / evolver** are the optimizer side; §4.2.2 shows skills evolved by one model transfer well to others, and a stronger evolver can outperform self-evolution — so `evolver=opus` with a cheaper daily model is a sound configuration, as is `consolidator=haiku` for budget trace analysis (at some risk of shallower root-cause analysis).
