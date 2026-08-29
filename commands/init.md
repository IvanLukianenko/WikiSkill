---
description: Full zero-touch WikiSkill setup — workspace, automation, models, and a validation suite seeded from the project itself
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion
---

## Context

- Init output: !`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/wikiskill.py" init`
- Guide: !`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/wikiskill.py" guide`

## Your task

Perform the **full setup** so the user has nothing left to do manually. The workspace was just created (output above); now configure everything.

### 1. Guided configuration — walk the user through every important setting

If the session is interactive, walk the user through the settings in two short AskUserQuestion rounds, each option with a one-line consequence so choices are informed. If the user cannot be asked (headless run) or dismisses a round, apply that round's recommended defaults and say so.

**Round 1 — core behavior:**
- **Automation** ("Full auto (Recommended)" / "Suggest only" / "Manual"): full auto = when a loop is due, Claude runs one iteration itself right after finishing your current task; suggest = Claude proposes and you confirm; manual = only explicit `/wikiskill:loop`.
- **Loop cadence** ("Balanced (Recommended)" 5 sessions / 3 days; "Frequent" 3 / 1; "Rare" 10 / 7): when a loop counts as due — by pending session traces or days since the last loop.
- **Skill Proposer model** ("Same as my sessions (Recommended)" / "Opus — stronger proposals, higher cost" / "Haiku — budget, shallower proposals"): the paper (§4.2.2) shows skills evolved by a stronger model transfer well, so Opus over a cheaper daily model is sound.
- **Seed validation from project tooling** ("Yes (Recommended)" / "No"): whether step 2 below runs.

**Round 2 — advanced (present it as "advanced, defaults are fine"):**
- **Wiki Maintainer model** ("Same as my sessions (Recommended)" / "Haiku — budget trace analysis"): consolidation is more mechanical; haiku saves tokens at some risk of shallower root-cause analysis.
- **Auto-harvest validation tasks** ("On (Recommended)" / "Off"): the loop distills tasks from your real sessions while the suite has fewer than 3.
- **Wiki in session context** ("Off (Recommended — per the paper)" / "On"): the §5.1 ablation shows injecting the wiki into working sessions degrades evolved-skill quality; On trades that for ambient knowledge.
- **Skills directory** (".claude/skills (Recommended)" / ".opencode/skill"): where evolved skills live; pick the second only for opencode-native setups.

Also tell the user (not a question): the **validator always stays on the session model** — validation is a rollout of the inference agent itself (§3.2.4), so gating must measure what *their* daily model achieves with a skill.

Apply every choice immediately:
- `python3 .wikiskill/bin/wikiskill.py config-set auto_loop '"auto"'` (/ `'"suggest"'` / `'"off"'`), `config-set loop_every_sessions N`, `config-set loop_every_days D`, `config-set auto_generate_validation true|false`, `config-set inject_wiki_context true|false`, `config-set skills_dir '".claude/skills"'` (or `'".opencode/skill"'`).
- Non-default evolver/consolidator models → the `/wikiskill:models` mechanism (copy the plugin agent into `.claude/agents/` with the chosen `model:` line, record in `agent_models`).

### 2. Seed the validation suite from the project's own tooling

If `.wikiskill/validation/tasks.md` has no `VT-*` tasks, inspect the repository — `package.json` scripts, `pyproject.toml`/`pytest.ini`, `Makefile`, `Cargo.toml`, `go.mod`, CI workflow files, README — and append **up to 2** seed tasks in the VT format, named `(auto-seeded at init)`:

- Each must use a command that actually exists in this project and each must be **verified right now** (run it; a fast subset like `--help`/`--version` is NOT verification — if the real command is too slow or fails for pre-existing reasons, don't seed it).
- Objective success criteria only (exit 0, output contains X). Include cleanup.
- Good seeds: the project's test suite, linter/typechecker, or build. These act as regression gates: an evolved skill must never break them.
- Seed at most 2 (not 3) deliberately: the loop's harvesting keeps adding trace-derived behavioral tasks while the suite has fewer than 3, so gating won't consist of trivially-green CI checks alone.
- If the project has no runnable tooling at all, seed nothing and note that harvesting will build the suite from real traces.

Do NOT run the baseline now — the first `/wikiskill:loop` establishes R_best after harvesting has mixed in at least one behavioral task (a purely-green seed suite would set R_best = 1.0 and early-stop evolution prematurely).

### 2a. Only if seeding was declined

Skip step 2 when the user answered "No" to seeding; note that harvesting (if enabled) will build the suite from traces instead.

### 3. Report — full onboarding

Render the guide's substance in the conversation language (three layers and lifecycle rules; one loop iteration and the strict R_best gating with rollback and early stop; token accounting), then a "what I just configured for you" table covering **every setting from both rounds** (chosen value + the one-line consequence), the seeded validation tasks (with the verification result of each), and what happens next with zero user action — hooks capture every session, the auto-loop trigger fires by session count or days, the first loop harvests + baselines + evolves. Note that `.wikiskill/wiki/`, `validation/`, `state.json` are worth committing to git, and `/wikiskill:help` re-shows the guide anytime.

Do not create any wiki patterns or skills — those must be earned from real traces.
