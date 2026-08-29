---
description: Run one full WikiSkill evolution cycle — consolidate → evolve → validate
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Task
---

## Context

- Status: !`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/wikiskills.py" status`

## Your task

Run one full cycle of the WikiSkill loop (arXiv:2608.27454). Execute the three phases **in order, in this one conversation**, following each phase's own command spec:

1. **Consolidate** — follow `/wikiskills:consolidate`: distill pending traces into the wiki, mark them consolidated. If there are no pending traces, note it and continue (the wiki may still hold unexploited knowledge from earlier cycles).
2. **Evolve** — follow `/wikiskills:evolve`: propose and apply the single highest-value skill change grounded in the wiki, snapshotting first. If the honest answer is no-op, stop here and report — do not force a change just to have something to validate.
3. **Validate** — follow `/wikiskills:validate` for the skill touched in phase 2: run the task suite (or the soft-gating fallback), record the result, and accept or roll back per the verdict. The wiki is never rolled back.

End with a cycle report: traces consolidated, wiki pages touched, skill change made (or no-op and why), validation verdict, and current state of the loop. Keep it under ~10 lines.
