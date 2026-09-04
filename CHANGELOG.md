# Changelog

All notable changes to the WikiSkill plugin. Versions follow
`.claude-plugin/plugin.json`; `claude plugin update wikiskill` only delivers a
new version when this number changes.

## 0.7.0 — Bounded validation suite
- `record-validation --results "VT-1=pass,VT-2=fail,..."` records per-task
  outcomes (`state.task_history`); warns on disagreement with `--passed/--total`.
- `suite-report`: per-task pass streaks and verdicts (NEW / INFORMATIVE /
  SATURATED = `retire_after_passes` consecutive passes, default 3).
- `retire-saturated [--max N] [--dry-run]`: rotates saturated tasks beyond
  `keep_regression_guards` (default 2) into `validation/retired.md`; nothing
  is deleted; the suite fingerprint changes so R_best is re-anchored.
- `validation_max_tasks` (default 12) caps the suite; consolidate retires at
  cap before harvesting; `status` shows cap / saturated count.
- Fix: `status` referenced config before loading it.

## 0.6.0 — Skill usage & usefulness statistics
- New `PostToolUse(Skill)` hook (`scripts/record_skill_use.py`) logs every
  skill invocation to `.wikiskill/stats/skill-usage.jsonl`; opencode plugin
  mirrors it via `tool.execute.after`.
- Stop hook records per session which skills were invoked and how many tool
  errors followed each (`skills_used` in the digest).
- `skill-stats` CLI and `/wikiskill:skills` command: HELPFUL / SUSPECT / UNUSED
  verdicts; consolidate and evolve consume them (SUSPECT patched first,
  UNUSED gets a description/trigger patch).

## 0.5.0 — Evolution deadlock fix
- Continuous harvesting: up to 2 new validation tasks every iteration from
  daily traces, failure-derived first, semantic dedupe.
- Suite-anchored gating: R_best carries a suite fingerprint; `record-validation`
  refuses with `SUITE CHANGED` when the suite differs, and the loop's new step
  1b re-baselines automatically. A saturated R_best = 1.0 now only pauses
  evolution until the next harvested task.
- Seed template's example header no longer counts as a task.

## 0.4.1 — Init wizard
- `/wikiskill:init` walks through every important setting in two question
  rounds (automation, cadence presets, evolver/consolidator models, seeding,
  harvesting, wiki injection, skills dir) with consequences and recommended
  defaults; the validator model is explained, not asked (§3.2.4).

## 0.4.0 — Zero-touch init
- Init applies preferences, seeds up to 2 validation tasks from the project's
  own verified tooling, and defers the baseline to the first loop.
- `config-set` CLI subcommand.

## 0.3.0 — Guide & token accounting
- `guide` CLI subcommand and `/wikiskill:help` command; init delivers a full
  onboarding.
- Stop hook sums transcript usage per session into the digest; `record-tokens`
  logs measured evolution work to `.wikiskill/stats.jsonl`; `status` shows
  evolution cost by phase.

## 0.2.0 — Automation, models, dogfooding
- Auto-loop triggers: `auto_loop` (suggest / auto / off), `loop_every_sessions`,
  `loop_every_days`, `loop-due` for cron; SessionStart hook nudges or
  instructs.
- Validation-task harvesting from traces (initially while the suite had < 3).
- `/wikiskill:models`: per-project agent model overrides via `.claude/agents/`.
- WikiSkill enabled on its own repository; iteration 0 consolidated 6 wiki
  patterns; `BrokenPipeError` on piped output fixed; MIT license; plugin
  renamed from `wikiskills` to `wikiskill` to match the paper.

## 0.1.0 — Faithful core
- Three-layer workspace (`raw/`, `wiki/` with `patterns/`, `index.md`,
  `log.md`, `skill-impact.md`; skills as `SKILL.md` + `PURPOSE.md`).
- Wiki Maintainer / Skill Proposer / validator agents adapted from the paper's
  Appendix E prompts; stratified trace sampling (Appendix C).
- Eq. 4 gating (strict improvement over R_best) with snapshots and rollback;
  programmatic `skill-impact.md` diffs; wiki injection off by default (§5.1).
- Claude Code plugin (marketplace, commands, hooks) and opencode support
  (JS plugin, command mirrors, installer).
