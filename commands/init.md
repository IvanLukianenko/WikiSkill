---
description: Initialize the WikiSkill workspace (raw traces / wiki / gated skills) in this project
allowed-tools: Bash(python3:*), Read
---

## Context

- Init output: !`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/wikiskill.py" init`
- Guide: !`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/wikiskill.py" guide`

## Your task

The WikiSkill workspace was just initialized (or refreshed). Present a thorough onboarding to the user based on the guide above — do not just dump it; render it in the conversation language, keeping all substance:

1. **The three layers** and their lifecycle rules (raw = disposable & auto-captured; wiki = compounding & never rolled back & worth committing to git; skills = gated & reversible), mapped to arXiv:2608.27454 Figure 2.
2. **One loop iteration** — consolidate → evolve → validate — and the gating rule (strict improvement over R_best, automatic rollback, early stop at 1.0).
3. **What runs automatically** (trace capture every session; validation-task harvesting; the auto-loop trigger with its current thresholds from `.wikiskill/config.json`) versus what they can tune (`auto_loop` mode, thresholds, `/wikiskill:models`, `inject_wiki_context`).
4. **Token accounting**: each trace digest records the session's token usage, measured evolution work is logged via `record-tokens`, and `/wikiskill:status` shows the running cost of skill evolution.
5. **Their minimal workflow**: work normally; approve (or let `auto` mode run) `/wikiskill:loop` when nudged; optionally strengthen `.wikiskill/validation/tasks.md` by hand. Mention `/wikiskill:help` re-shows this guide anytime.

Do not create any wiki patterns or skills yet — those must be earned from real traces.
