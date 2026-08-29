---
description: Validate a skill update against the task suite and gate it (accept or rollback)
argument-hint: <skill-name>
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Task
---

## Context

- Status: !`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/wikiskills.py" status`
- Validation suite: @.wikiskills/validation/tasks.md
- Skill to validate: "$ARGUMENTS"

## Your task

Run the **validation-gating** step of the WikiSkill framework (arXiv:2608.27454) for the skill named above (if none was given, pick the most recently snapshotted skill from the status output, and say which you picked).

**If the suite defines tasks (VT-* sections):**

1. For each task, execute it honestly against its success criteria. Use the `wikiskills-validator` agent (one per task, in parallel where independent) so each task runs with the current skills but without this conversation's bias; give each agent the task's prompt, success criteria, and cleanup instructions verbatim, and require a PASS/FAIL verdict with concrete evidence.
2. Count passes and record the result:
   `python3 .wikiskills/bin/wikiskills.py record-validation --skill <name> --passed <M> --total <N> --note "<one-line context>"`
3. Obey the printed verdict:
   - **IMPROVED / BASELINE** → accept; tell the user the skill update is confirmed.
   - **REGRESSED** → roll back: `python3 .wikiskills/bin/wikiskills.py rollback <name>`, then tell the user the skill was reverted. **Do not revert any wiki change** — per the framework, the wiki persists so the next evolution attempt builds on it. Optionally append the failure lesson to the relevant wiki page.
   - **UNCHANGED** → keep the update only if it made the skill simpler/shorter; otherwise roll back for parsimony. State your choice.
4. Run any per-task cleanup steps.

**If the suite has no tasks yet:** fall back to soft gating — diff the skill against its latest snapshot (`.wikiskills/archive/<name>/<ts>/`), adversarially self-review the changes (Does each addition trace to a wiki entry? Could any instruction misfire on plausible tasks? Did the skill get bloated?), fix what the review finds, record the result with `--passed 1 --total 1 --note "soft review (no task suite)"`, and remind the user that adding tasks to `.wikiskills/validation/tasks.md` enables real gating.

Finish with a one-paragraph report: verdict, score vs. previous, and what happened to the skill.
