---
description: Run one full WikiSkill evolution cycle — consolidate → evolve → validate
---

Run one full cycle of the WikiSkill loop (arXiv:2608.27454), in order:

1. **Consolidate** — everything `/wikiskills-consolidate` specifies (skip cleanly
   if no traces are pending).
2. **Evolve** — everything `/wikiskills-evolve` specifies (an honest no-op ends
   the cycle here).
3. **Validate** — everything `/wikiskills-validate` specifies for the skill
   touched in step 2, accepting or rolling back per the verdict. The wiki is
   never rolled back.

End with a ≤10-line cycle report: traces consolidated, wiki pages touched, skill
change (or no-op and why), validation verdict.
