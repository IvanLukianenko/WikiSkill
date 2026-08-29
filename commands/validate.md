---
description: Gating step — evaluate the skill set on the validation suite; accept only if it beats R_best, else roll back
argument-hint: <skill-name> | --baseline
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Task
---

## Context

- Status: !`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/wikiskill.py" status`
- Validation suite: @.wikiskill/validation/tasks.md
- Argument: "$ARGUMENTS"

## Your task

Run the **Gating and Rollback** step of the WikiSkill framework (arXiv:2608.27454, §3.2.4, Eq. 4). The acceptance rule is strict: a candidate skill update is kept only if the validation score **strictly exceeds R_best** (the best score recorded so far, shown in the status output).

**Baseline mode** — if the argument is `--baseline`, or status shows "not baselined yet": run the suite with the current skill set and record `python3 .wikiskill/bin/wikiskill.py record-validation --baseline --passed <M> --total <N> --note "baseline"`. This initializes R_best (the paper's R(T_val,0)); report and stop.

**Gating mode** — validate the skill named in the argument (if none, use the most recently snapshotted skill from the status output and say which you picked):

1. For each VT-* task in the suite, execute it honestly against its success criteria. Use one `wikiskill-validator` agent per task (parallel where independent) so tasks run with the current skills but without this conversation's bias; give each agent the task's prompt, success criteria, and cleanup verbatim, and require PASS/FAIL with concrete evidence.
2. Record and gate: `python3 .wikiskill/bin/wikiskill.py record-validation --skill <name> --passed <M> --total <N> --note "<one-line context>"`. The CLI compares against R_best, appends the proposal's unified diff and outcome to `wiki/skill-impact.md`, and advances the iteration counter.
3. Obey the printed verdict:
   - **ACCEPTED** → keep the skill update; append a dated line to the skill's `PURPOSE.md` Evolution History. If R_best hit 1.0, tell the user evolution early-stops until harder tasks are added.
   - **REJECTED** (score ≤ R_best, ties included) → roll back immediately: `python3 .wikiskill/bin/wikiskill.py rollback <name>`. **Never revert any wiki change** — patterns, log.md, and the recorded rejection persist so the next proposal builds on them.
4. Run each task's cleanup steps.
5. Record the measured cost: sum the `subagent_tokens` reported by the validator agents' results and run `python3 .wikiskill/bin/wikiskill.py record-tokens --phase validate --tokens <sum> --note "iteration <k>, <N> tasks"`. Record only measured agent usage — never estimate.

**If the suite defines no VT-* tasks:** first, when `auto_generate_validation` is enabled in config, try to harvest 1–3 tasks from consolidated traces (per the harvesting rules in `/wikiskill:consolidate` step 5) and, if you succeed, gate against them normally. Only when no trace yields an objectively checkable task, soft-gate instead — diff the skill against its latest snapshot (`.wikiskill/archive/<name>/`), adversarially self-review (does each instruction trace to a wiki pattern? could any misfire? is it concise?), fix findings, and record with `--passed 1 --total 1 --note "soft review (no task suite)"`.

Finish with a one-paragraph report: score vs. R_best, verdict, and what happened to the skill.
