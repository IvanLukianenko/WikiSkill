---
description: Show WikiSkill state — iteration, R_best, pending traces, patterns, skills
---

Run `python3 .wikiskill/bin/wikiskill.py status`, present the result in a short
readable summary, and recommend the single most useful next action:
`/wikiskill-init` if uninitialized; `/wikiskill-validate --baseline` if R_best
is not baselined yet; harder validation tasks if R_best = 1.00 (evolution is
early-stopped); `/wikiskill-consolidate` when ≥3 traces are pending;
`/wikiskill-evolve` when the wiki grew since the last proposal;
`/wikiskill-validate <skill>` when a skill was snapshotted but has no
skill-impact entry; otherwise "loop is healthy".
