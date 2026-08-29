---
description: Run one iteration of the WikiSkill evolution loop (Algorithm 1)
---

Execute one iteration of the WikiSkill loop (arXiv:2608.27454, Algorithm 1),
in order:

0. `python3 .wikiskill/bin/wikiskill.py status` — if R_best = 1.00, stop
   (early-stopped until harder validation tasks exist). If not baselined yet,
   first run the baseline per `/wikiskill-validate --baseline`.
1. **Wiki Maintenance** — everything `/wikiskill-consolidate` specifies,
   including validation-task harvesting (skip cleanly if nothing is pending).
2. **Skill Proposal** — everything `/wikiskill-evolve` specifies; an honest
   no-action ends the iteration here.
3. **Gating** — everything `/wikiskill-validate` specifies for the skill touched
   in step 2; on REJECTED roll the skill back. The wiki is retained either way.

End with a ≤10-line iteration report: iteration number, traces consolidated,
patterns touched, the proposal (or no-action and why), score vs. R_best, outcome.
