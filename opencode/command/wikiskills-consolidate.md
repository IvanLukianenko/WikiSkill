---
description: Consolidate captured execution traces into the persistent knowledge wiki
---

Run the experience-consolidation step of WikiSkill (arXiv:2608.27454). First read
`.opencode/wikiskills/METHODOLOGY.md` and follow its wiki formats and rules.

1. List pending traces: `python3 .wikiskills/bin/wikiskills.py pending --paths`.
   If none, say so and stop.
2. Read each trace file and extract only durable, reusable lessons (Facts,
   Pitfalls, Procedures, Preferences). Discard one-offs, transient state, secrets.
3. Update `.wikiskills/wiki/pages/*.md` append/refine style: matching entries get
   evidence counters incremented and wording generalized/corrected; new lessons go
   to the right topical page (create kebab-case pages as needed). Never delete
   entries. Keep `.wikiskills/wiki/index.md` current.
4. Mark done: `python3 .wikiskills/bin/wikiskills.py mark-consolidated --all`
5. Report traces consolidated, pages changed, and the top lessons; suggest
   `/wikiskills-evolve` if the wiki gained substantive knowledge.
