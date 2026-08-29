---
description: Show the detailed WikiSkill guide — how the framework works, commands, automation, costs
allowed-tools: Bash(python3:*)
---

## Context

- Guide: !`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/wikiskill.py" guide`
- Status: !`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/wikiskill.py" status`

## Your task

Present the guide above to the user in the conversation language, keeping all substance (three layers, the loop, gating, automation knobs, token accounting, command list). Then, from the status output, add a one-paragraph "where this project is right now" — iteration, R_best, pending traces, evolution cost so far — and the single most useful next action.
