---
description: Wiki Maintainer step — consolidate sampled execution traces into the persistent wiki
allowed-tools: Bash(python3:*), Read, Write, Edit, Glob, Grep, Task
---

## Context

- Stratified sample: !`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/wikiskill.py" sample`

## Your task

Act as the **Wiki Maintainer** of the WikiSkill framework (arXiv:2608.27454, §3.2.2 and Appendix E.2): perform deep analysis of the sampled execution traces above and consolidate them into the persistent wiki at `.wikiskill/wiki/`. Follow the `wikiskill-methodology` skill for exact formats. If nothing was sampled, say so and stop.

You may delegate the trace analysis to the `wikiskill-consolidator` agent (pass it the sampled digest and raw-log paths) and apply its proposed wiki updates yourself.

1. **Deep trace analysis (critical).** Read each sampled digest, and its raw log where the digest's errors are insufficient to determine a root cause (respect the character cap printed above). Read the agent's actual actions — what commands were issued; compare successful vs. failed sessions — what did successful ones do differently; identify ACTION PATTERNS and strategies, not just error messages; check whether active skills were followed and whether their guidance helped or misled.
2. **Update pattern pages** under `.wikiskill/wiki/patterns/` (one page per pattern, kebab-case):
   - Document BOTH failure patterns (what went wrong, root cause — WHY, not just WHAT — and how to avoid it) and success patterns (strategies that consistently lead to completion), with exact command sequences from the traces and concrete workarounds.
   - Do NOT create duplicates — update existing pages with new evidence instead, using minimal incremental edits (append evidence, replace refined text). Add an evidence line per sighting, e.g. `Evidence: Iter 2: session ab12cd | Iter 3: persists`.
   - Keep pages 10–30 lines. Only create patterns for meaningful, generalizable observations. Never include secrets (tokens, keys, credentials).
3. **Update `wiki/index.md` (always, in full).** One line per pattern in exactly this format — it decides whether the pattern page ever gets read:
   `- [pattern-name](patterns/pattern-name.md): PROBLEM + ROOT CAUSE + FIX in one or two sentences.`
4. **Append to `wiki/log.md` (always,** even if no patterns changed**):** a brief entry for this consolidation — date, iteration (from `python3 .wikiskill/bin/wikiskill.py status`), traces analyzed, patterns created/updated, recurring errors observed.
5. **Harvest validation tasks** (skip if `auto_generate_validation` is false in `.wikiskill/config.json`): if `.wikiskill/validation/tasks.md` has fewer than 3 `VT-*` tasks, distill 1–3 new ones from the analyzed traces so gating stays quantitative without manual authoring. A good harvested task comes from a **representative, completed** request: rewrite the session's goal as a self-contained prompt, derive objective success criteria from what "done" actually looked like in the trace (a command exiting 0, a file containing X — never "looks good"), and add cleanup steps. Append them in the VT-format with `(auto-generated from session <id>)` in the name. Never harvest tasks that would leak secrets, mutate shared state without cleanup, or duplicate an existing task.
6. Mark the sampled traces done: `python3 .wikiskill/bin/wikiskill.py mark-consolidated <sampled digest paths>` (use `--all` only if you actually analyzed all pending traces).
7. Report: patterns created/updated, validation tasks harvested (if any), and the key root causes found. If the wiki gained substantive knowledge, suggest `/wikiskill:evolve` next.

Never delete or reset wiki content — the Wiki Layer compounds and is never rolled back.
