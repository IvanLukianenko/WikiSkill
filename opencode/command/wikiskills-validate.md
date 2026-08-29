---
description: Validate a skill update against the task suite and gate it (accept or rollback)
---

Skill to validate: $ARGUMENTS (if empty, pick the most recently snapshotted skill
per `python3 .wikiskills/bin/wikiskills.py status` and say which you picked).

Run the validation-gating step of WikiSkill (arXiv:2608.27454); rules are in
`.opencode/wikiskills/METHODOLOGY.md`.

1. Read `.wikiskills/validation/tasks.md`. If it defines VT-* tasks: execute each
   task's prompt honestly, judge strictly against its success criteria (run the
   implied checks and capture real output), then run its cleanup.
2. Record: `python3 .wikiskills/bin/wikiskills.py record-validation --skill <name> --passed <M> --total <N> --note "<context>"`
3. Obey the printed verdict: IMPROVED/BASELINE → accept; REGRESSED →
   `python3 .wikiskills/bin/wikiskills.py rollback <name>` (never revert wiki
   changes — the wiki persists by design); UNCHANGED → keep only if the skill got
   simpler.
4. If no tasks are defined: soft-gate instead — diff the skill against its latest
   snapshot in `.wikiskills/archive/<name>/`, adversarially self-review, fix
   findings, record `--passed 1 --total 1 --note "soft review"`, and remind the
   user to add real tasks.

Finish with verdict, score vs. previous, and what happened to the skill.
