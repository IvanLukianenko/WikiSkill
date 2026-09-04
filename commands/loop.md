---
description: Run one iteration of the WikiSkill evolution loop (Algorithm 1) — consolidate → propose → validate → gate
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Task
---

## Context

- Status: !`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/wikiskill.py" status`

## Your task

Execute one iteration 𝑘 of the WikiSkill evolution loop (arXiv:2608.27454, Algorithm 1), in order, in this one conversation. Rollouts happen organically — the user's normal sessions are the training rollouts, captured automatically into `.wikiskill/raw/`.

0. **Early-stop check (Alg. 1, line 4, suite-aware):** R_best = 1.00 stops the iteration **only if** step 1's harvesting adds no new task (an unchanged, saturated suite has no headroom) — so never stop before running step 1. "Not baselined yet" is handled in step 1b.
1. **Wiki Maintenance:** follow `/wikiskill:consolidate` — stratified-sample pending traces, consolidate into patterns/index/log, retire saturated validation tasks when the suite is at cap, and harvest new ones (failure-derived first; this is what keeps evolution unblocked while validation cost stays bounded). If nothing is pending, note it and continue (the wiki may still hold unexploited knowledge).
1b. **Re-anchor R_best when the suite changed:** re-run status; if it reports the suite CHANGED since baseline (harvesting added tasks) or "not baselined yet", run the full suite with the **current** skill set via `wikiskill-validator` agents and record `record-validation --baseline --passed <M> --total <N> --note "re-anchor on suite change"` (plus `record-tokens`). Pass rates are only comparable within one suite, so this fresh baseline is what makes the coming gating decision meaningful — and it is how a saturated R_best = 1.00 gets unblocked. If after this R_best = 1.00 and no proposal could beat it, stop here with that explanation.
2. **Skill Proposal:** follow `/wikiskill:evolve` — one atomic proposal (create/patch), grounded in the wiki, never repeating a rejected diff from `skill-impact.md`, snapshot before applying. An honest **no action** ends the iteration here — report and stop; do not force a change.
3. **Gating:** follow `/wikiskill:validate` for the skill touched in step 2 — run the suite, `record-validation` (which writes the diff and outcome to `wiki/skill-impact.md` and advances the iteration), and on REJECTED roll the skill back. The wiki is retained regardless of the outcome.

End with a ≤10-line iteration report: iteration number, traces consolidated, patterns touched, the proposal (or no-action and why), validation score vs. R_best, the gating outcome, and the iteration's measured token cost (the phases' `record-tokens` entries — `status` shows the running total).
