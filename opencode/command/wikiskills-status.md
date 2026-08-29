---
description: Show WikiSkills state — pending traces, wiki pages, skills, validations
---

Run `python3 .wikiskills/bin/wikiskills.py status`, present the result in a short
readable summary, and recommend the single most useful next action:
`/wikiskills-init` if uninitialized, `/wikiskills-consolidate` when ≥3 traces are
pending, `/wikiskills-evolve` when the wiki grew since the last evolution,
`/wikiskills-validate` when a skill was evolved but never validated, otherwise
"loop is healthy".
