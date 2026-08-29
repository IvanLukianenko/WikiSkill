---
description: Evolve skills grounded in the wiki — create or refine skills, with snapshots for rollback
---

Requested focus (optional): $ARGUMENTS

Run the skill-evolution step of WikiSkill (arXiv:2608.27454). First read
`.opencode/wikiskills/METHODOLOGY.md` and follow its evolution rules.

1. Read the whole wiki (`.wikiskills/wiki/`) and the existing skills in the
   `skills_dir` from `.wikiskills/config.json` (default `.claude/skills`).
2. Decide ONE change grounded only in the wiki: refine an existing skill, create a
   new skill (only for a coherent cluster of ≥3 related wiki entries), or honestly
   no-op (then say so and stop).
3. Snapshot before editing: `python3 .wikiskills/bin/wikiskills.py snapshot <name>`
4. Apply a minimal, concise change; cite wiki entries in a trailing HTML comment
   changelog: `<!-- evolved <date> from wiki: <page>#<entries> -->`.
5. Report what changed and why, and tell the user the update is provisional until
   `/wikiskills-validate <name>` runs.
