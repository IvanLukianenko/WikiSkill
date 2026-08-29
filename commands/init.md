---
description: Full zero-touch WikiSkill setup — workspace, automation, models, and a validation suite seeded from the project itself
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion
---

## Context

- Init output: !`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/wikiskill.py" init`
- Guide: !`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/wikiskill.py" guide`

## Your task

Perform the **full setup** so the user has nothing left to do manually. The workspace was just created (output above); now configure everything.

### 1. Preferences — one question, sensible defaults

If the session is interactive, ask ONE AskUserQuestion round with two questions:
- **Automation**: "Full auto (Recommended)" (Claude runs a loop iteration itself after your task when due) / "Suggest only" (Claude proposes, you confirm) / "Manual" (only explicit `/wikiskill:loop`).
- **Skill Proposer model**: "Same as my sessions (Recommended)" / "Opus (stronger proposals, higher cost)".

If the user cannot be asked (headless run, or they dismiss), apply the recommended defaults. Apply the choices:
- Automation → `python3 .wikiskill/bin/wikiskill.py config-set auto_loop '"auto"'` (or `'"suggest"'` / `'"off"'`).
- Evolver on opus → follow the `/wikiskill:models` mechanism for `evolver=opus` (copy the plugin agent into `.claude/agents/` with `model: opus`, record in `agent_models`). "Same as sessions" needs no action.

### 2. Seed the validation suite from the project's own tooling

If `.wikiskill/validation/tasks.md` has no `VT-*` tasks, inspect the repository — `package.json` scripts, `pyproject.toml`/`pytest.ini`, `Makefile`, `Cargo.toml`, `go.mod`, CI workflow files, README — and append **up to 2** seed tasks in the VT format, named `(auto-seeded at init)`:

- Each must use a command that actually exists in this project and each must be **verified right now** (run it; a fast subset like `--help`/`--version` is NOT verification — if the real command is too slow or fails for pre-existing reasons, don't seed it).
- Objective success criteria only (exit 0, output contains X). Include cleanup.
- Good seeds: the project's test suite, linter/typechecker, or build. These act as regression gates: an evolved skill must never break them.
- Seed at most 2 (not 3) deliberately: the loop's harvesting keeps adding trace-derived behavioral tasks while the suite has fewer than 3, so gating won't consist of trivially-green CI checks alone.
- If the project has no runnable tooling at all, seed nothing and note that harvesting will build the suite from real traces.

Do NOT run the baseline now — the first `/wikiskill:loop` establishes R_best after harvesting has mixed in at least one behavioral task (a purely-green seed suite would set R_best = 1.0 and early-stop evolution prematurely).

### 3. Report — full onboarding

Render the guide's substance in the conversation language (three layers and lifecycle rules; one loop iteration and the strict R_best gating with rollback and early stop; token accounting), then a "what I just configured for you" list: automation mode and thresholds, agent models, seeded validation tasks (with the verification result of each), and what happens next with zero user action — hooks capture every session, the auto-loop trigger fires by session count or days, the first loop harvests + baselines + evolves. Note that `.wikiskill/wiki/`, `validation/`, `state.json` are worth committing to git, and `/wikiskill:help` re-shows the guide anytime.

Do not create any wiki patterns or skills — those must be earned from real traces.
