---
description: Wiki Maintainer step — consolidate sampled execution traces into the persistent wiki
---

Act as the Wiki Maintainer of WikiSkill (arXiv:2608.27454 §3.2.2). First read
`.opencode/wikiskill/METHODOLOGY.md` and follow its formats exactly.

1. Get the stratified sample: `python3 .wikiskill/bin/wikiskill.py sample`
   (≤5 failing + ≤3 passing pending traces). If empty, say so and stop.
2. Deep analysis: read each sampled digest, and its raw log where needed to find
   root causes (respect the printed character cap). Compare successful vs. failed
   sessions; extract ACTION PATTERNS, not just error messages; note whether
   active skills helped or misled.
3. Update `.wikiskill/wiki/patterns/*.md`: both failure and success patterns,
   root cause + exact command sequences + concrete fixes, 10–30 lines per page,
   evidence lines per sighting, no duplicates (patch existing pages minimally),
   never delete, no secrets.
4. Rewrite `wiki/index.md` in full — one line per pattern:
   `- [name](patterns/name.md): PROBLEM + ROOT CAUSE + FIX in one or two sentences.`
5. Append a brief iteration entry to `wiki/log.md` (always, even with no changes).
6. Mark sampled traces: `python3 .wikiskill/bin/wikiskill.py mark-consolidated <paths>`
7. Report patterns created/updated and key root causes; suggest
   `/wikiskill-evolve` if the wiki gained substantive knowledge.
