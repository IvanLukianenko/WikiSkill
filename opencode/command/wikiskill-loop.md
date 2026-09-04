---
description: Run one iteration of the WikiSkill evolution loop (Algorithm 1)
---

Execute one iteration of the WikiSkill loop (arXiv:2608.27454, Algorithm 1),
in order:

0. `python3 .wikiskill/bin/wikiskill.py status` — note R_best and the suite
   state, but never stop before step 1: a saturated R_best = 1.00 is
   unblocked by harvesting.
1. **Wiki Maintenance** — everything `/wikiskill-consolidate` specifies,
   including per-iteration validation-task harvesting (skip cleanly if
   nothing is pending).
1b. Re-run status; if the suite CHANGED since baseline or is not baselined
   yet, run the full suite with the current skills and record
   `record-validation --baseline` — this re-anchors R_best on the new suite
   (pass rates across different suites are not comparable). Stop here only
   if R_best is 1.00 on an unchanged suite.
2. **Skill Proposal** — everything `/wikiskill-evolve` specifies; an honest
   no-action ends the iteration here.
3. **Gating** — everything `/wikiskill-validate` specifies for the skill touched
   in step 2; on REJECTED roll the skill back. The wiki is retained either way.

End with a ≤10-line iteration report: iteration number, traces consolidated,
patterns touched, the proposal (or no-action and why), score vs. R_best, outcome.
