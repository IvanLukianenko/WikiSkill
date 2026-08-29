---
description: Show WikiSkill state — iteration, R_best, pending traces, patterns, skills
---

Run `python3 .wikiskills/bin/wikiskills.py status`, present the result in a short
readable summary, and recommend the single most useful next action:
`/wikiskills-init` if uninitialized; `/wikiskills-validate --baseline` if R_best
is not baselined yet; harder validation tasks if R_best = 1.00 (evolution is
early-stopped); `/wikiskills-consolidate` when ≥3 traces are pending;
`/wikiskills-evolve` when the wiki grew since the last proposal;
`/wikiskills-validate <skill>` when a skill was snapshotted but has no
skill-impact entry; otherwise "loop is healthy".
