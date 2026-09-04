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
5. **Harvest validation tasks — every iteration** (skip only if `auto_generate_validation` is false in `.wikiskill/config.json`): distill up to 2 new `VT-*` tasks from the analyzed traces whenever they surface work not covered by the existing suite. This keeps gating challenging forever — without fresh tasks a small suite saturates at R_best = 1.0 and evolution stalls. Priorities:
   - **Failure-derived first**: a task built from a session that struggled or failed (rewritten as a self-contained prompt + the success criteria the session was actually trying to meet) is the most valuable — the current skill set does not trivially pass it, which is exactly the headroom evolution needs.
   - Then representative completed requests: self-contained prompt, objective criteria from what "done" looked like in the trace (a command exiting 0, a file containing X — never "looks good"), cleanup steps.
   Append in VT-format with `(auto-generated from session <id>)` in the name. Never duplicate an existing task (semantically, not just verbatim), leak secrets, or mutate shared state without cleanup. Stop adding once the suite reaches ~12 tasks — replace nothing, just be selective. Note: adding tasks changes the suite fingerprint, so the next gating requires a fresh baseline — the loop handles this re-anchoring automatically.
6. Mark the sampled traces done: `python3 .wikiskill/bin/wikiskill.py mark-consolidated <sampled digest paths>` (use `--all` only if you actually analyzed all pending traces).
7. If you delegated to the `wikiskill-consolidator` agent, record its measured cost: `python3 .wikiskill/bin/wikiskill.py record-tokens --phase consolidate --tokens <subagent_tokens from the Task result> --note "iteration <k>"`. Record only measured agent usage — never estimate.
8. Report: patterns created/updated, validation tasks harvested (if any), and the key root causes found. If the wiki gained substantive knowledge, suggest `/wikiskill:evolve` next.

Never delete or reset wiki content — the Wiki Layer compounds and is never rolled back.
