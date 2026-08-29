---
description: Consolidate captured execution traces into the persistent knowledge wiki
allowed-tools: Bash(python3:*), Read, Write, Edit, Glob, Grep, Task
---

## Context

- Pending traces: !`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/wikiskills.py" pending`

## Your task

Run the **experience-consolidation** step of the WikiSkill framework (arXiv:2608.27454): distill the pending traces above into the persistent wiki at `.wikiskills/wiki/`. Follow the `wikiskills-methodology` skill for wiki page and entry formats.

If there are **no pending traces**, say so and stop.

Steps:

1. Read every pending trace file listed above. If there are more than ~5, delegate the reading and lesson-extraction to the `wikiskills-consolidator` agent (pass it the file paths) and work from its report.
2. From the traces, extract only **durable, reusable lessons** — things that would change how a future session behaves in this project:
   - **Facts** — stable properties of this codebase/environment (build commands, layout, versions, conventions).
   - **Pitfalls** — errors that occurred and their actual root cause + remedy. The `errors` field of each trace is the primary ore here.
   - **Procedures** — multi-step sequences that worked and are likely to recur.
   - **Preferences** — how the user wants things done (style, tone, workflow).
   Discard one-off details, secrets, transient state, and anything tied to a single dead-end task.
3. Update the wiki **append/refine style**:
   - If a lesson matches an existing entry in `.wikiskills/wiki/pages/*.md`, refine it: increment its evidence counter, update `last:`, generalize the wording if the new evidence broadens it, or correct it if the new evidence contradicts it (note the correction).
   - Otherwise add the entry to the topically right page, creating a new kebab-case page under `.wikiskills/wiki/pages/` if no page fits.
   - Never delete entries; an entry invalidated by evidence is rewritten to state the corrected knowledge.
4. Update `.wikiskills/wiki/index.md`: keep the page list current with a one-line description per page.
5. Mark the traces done: `python3 .wikiskills/bin/wikiskills.py mark-consolidated --all`
6. Report to the user: how many traces were consolidated, which pages changed, and the 2–3 most valuable new lessons. If the wiki gained substantive new knowledge, suggest `/wikiskills:evolve` next.
