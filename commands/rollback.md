---
description: Roll a skill back to a previous snapshot (the wiki is never touched)
argument-hint: <skill-name> [timestamp]
allowed-tools: Bash(python3:*), Read
---

## Context

- Target: "$ARGUMENTS"
- Status: !`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/wikiskills.py" status`

## Your task

Roll back the named skill using the project-local CLI:

1. If no skill name was given, show the skills with snapshots (from the status output) and ask which to roll back.
2. List its snapshots: `python3 .wikiskills/bin/wikiskills.py snapshots <name>`
3. Roll back: `python3 .wikiskills/bin/wikiskills.py rollback <name>` (add `--ts <timestamp>` if the user picked a specific one, or if a second argument was provided above).
4. Confirm what happened and remind the user that, per the WikiSkill framework, the wiki keeps everything learned — a future `/wikiskills:evolve` can attempt a better update from the same knowledge.
