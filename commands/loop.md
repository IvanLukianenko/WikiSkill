---
description: Run one iteration of the WikiSkill evolution loop (Algorithm 1) — consolidate → propose → validate → gate
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Task
---

## Context

- Status: !`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/wikiskill.py" status`

## Your task

Execute one iteration 𝑘 of the WikiSkill evolution loop (arXiv:2608.27454, Algorithm 1), in order, in this one conversation. Rollouts happen organically — the user's normal sessions are the training rollouts, captured automatically into `.wikiskill/raw/`.

0. **Early-stop check (Alg. 1, line 4):** if the status shows R_best = 1.00, stop — tell the user evolution is early-stopped until harder validation tasks are added. If status shows "not baselined yet", first establish the baseline per `/wikiskill:validate --baseline`, then continue.
1. **Wiki Maintenance:** follow `/wikiskill:consolidate` — stratified-sample pending traces, consolidate into patterns/index/log, and harvest validation tasks when the suite has fewer than 3 (keeps the loop fully automated). If nothing is pending, note it and continue (the wiki may still hold unexploited knowledge).
2. **Skill Proposal:** follow `/wikiskill:evolve` — one atomic proposal (create/patch), grounded in the wiki, never repeating a rejected diff from `skill-impact.md`, snapshot before applying. An honest **no action** ends the iteration here — report and stop; do not force a change.
3. **Gating:** follow `/wikiskill:validate` for the skill touched in step 2 — run the suite, `record-validation` (which writes the diff and outcome to `wiki/skill-impact.md` and advances the iteration), and on REJECTED roll the skill back. The wiki is retained regardless of the outcome.

End with a ≤10-line iteration report: iteration number, traces consolidated, patterns touched, the proposal (or no-action and why), validation score vs. R_best, the gating outcome, and the iteration's measured token cost (the phases' `record-tokens` entries — `status` shows the running total).
