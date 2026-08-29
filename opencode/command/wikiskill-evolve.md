---
description: Skill Proposer step — one atomic, wiki-informed skill change (create/patch/no-action)
---

Requested focus (optional): $ARGUMENTS

Act as the Skill Proposer of WikiSkill (arXiv:2608.27454 §3.2.3). Rules are in
`.opencode/wikiskill/METHODOLOGY.md`. Workflow, in order:

1. Read `.wikiskill/wiki/index.md`.
2. Read `.wikiskill/wiki/skill-impact.md` — it contains rejected proposal diffs;
   do NOT repeat a rejected approach.
3. Read the relevant pattern pages and existing skills (SKILL.md + PURPOSE.md in
   the `skills_dir` from `.wikiskill/config.json`).
4. Read ≥4 traces under `.wikiskill/raw/traces/` (or all, if fewer) to confirm
   root causes.
5. Decide ONE atomic change: **patch** an existing skill (preferred when it is
   partially correct; minimal targeted edits), **create** a new skill, or honest
   **no action** (say why and stop).
6. Snapshot first: `python3 .wikiskill/bin/wikiskill.py snapshot <name>`
7. Apply: SKILL.md = frontmatter + When to Apply + When NOT to Apply +
   Instructions (concrete action rules, concise); PURPOSE.md = Origin + Patterns
   Addressed + Evolution History.
8. Report the proposal and its grounding, then tell the user the update is
   provisional until `/wikiskill-validate <name>` gates it.
