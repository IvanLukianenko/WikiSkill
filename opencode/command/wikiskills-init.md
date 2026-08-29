---
description: Initialize the WikiSkill workspace (raw traces / wiki / gated skills) in this project
---

Initialize the WikiSkill framework (arXiv:2608.27454) here:

1. Run: `python3 .opencode/wikiskills/wikiskills.py init`
2. Read `.opencode/wikiskills/METHODOLOGY.md` and briefly explain the three layers
   (Raw traces / persistent Wiki with patterns+index+log+skill-impact / gated
   Skills with SKILL.md+PURPOSE.md) to the user.
3. Recommend adding validation tasks to `.wikiskills/validation/tasks.md` (show
   the template format from that file) — the suite is the paper's D_val.
4. Explain the workflow: work normally — the WikiSkills opencode plugin captures
   traces automatically — then periodically run `/wikiskills-loop` for one
   evolution iteration. The first loop establishes the R_best baseline.

Do not create wiki patterns or skills yet; those must be earned from real traces.
