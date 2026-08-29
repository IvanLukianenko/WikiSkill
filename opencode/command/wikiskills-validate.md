---
description: Gating step — validate against the task suite; accept only if it beats R_best, else roll back
---

Argument: $ARGUMENTS (skill name, or `--baseline`).

Run WikiSkill validation gating (arXiv:2608.27454 §3.2.4, Eq. 4); rules in
`.opencode/wikiskills/METHODOLOGY.md`. Check state first:
`python3 .wikiskills/bin/wikiskills.py status`.

**Baseline mode** (argument `--baseline`, or status shows "not baselined yet"):
run the suite in `.wikiskills/validation/tasks.md` with current skills, then
`python3 .wikiskills/bin/wikiskills.py record-validation --baseline --passed <M> --total <N> --note "baseline"`.

**Gating mode** (skill named, or pick the most recently snapshotted one):

1. Execute each VT-* task honestly against its success criteria; capture real
   output; run its cleanup.
2. Record and gate:
   `python3 .wikiskills/bin/wikiskills.py record-validation --skill <name> --passed <M> --total <N> --note "<context>"`
   (this appends the proposal diff + outcome to `wiki/skill-impact.md` and
   advances the iteration).
3. Obey the verdict: **ACCEPTED** → keep the skill, add a dated Evolution History
   line to its PURPOSE.md. **REJECTED** (ties included) → roll back now:
   `python3 .wikiskills/bin/wikiskills.py rollback <name>` — never revert wiki
   changes; the wiki is retained by design.
4. No VT-* tasks defined → soft-gate: diff the skill vs. its latest snapshot in
   `.wikiskills/archive/<name>/`, adversarially self-review, fix findings, record
   `--passed 1 --total 1 --note "soft review"`, and remind the user to add real
   tasks.

Finish with score vs. R_best, verdict, and what happened to the skill.
