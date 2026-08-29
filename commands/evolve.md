---
description: Evolve skills grounded in the wiki — create or refine skills, with snapshots for rollback
argument-hint: [skill-name (optional — otherwise decide from the wiki)]
allowed-tools: Bash(python3:*), Read, Write, Edit, Glob, Grep, Task
---

## Context

- Status: !`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/wikiskills.py" status`
- Requested focus: "$ARGUMENTS"

## Your task

Run the **skill-evolution** step of the WikiSkill framework (arXiv:2608.27454): propose and apply skill updates that are grounded **only in the wiki** (`.wikiskills/wiki/`), never directly in raw traces. Follow the `wikiskills-methodology` skill.

Steps:

1. Read `.wikiskills/wiki/index.md` and every page under `.wikiskills/wiki/pages/`. Read the existing skills in the skills directory shown in the status output (default `.claude/skills/`). For a large wiki, delegate the proposal drafting to the `wikiskills-evolver` agent.
2. Decide the highest-value change (or honor the requested focus above if given). Exactly one of:
   - **Refine an existing skill** — fold in wiki knowledge it lacks, tighten wording, fix knowledge the wiki has since corrected.
   - **Create a new skill** — only when the wiki holds a coherent cluster of ≥3 related entries that describe a recurring, triggerable capability.
   - **No-op** — if the wiki holds nothing actionable beyond what skills already encode, say so and stop. Do not invent changes.
3. Before touching a skill named `<name>`, snapshot it:
   `python3 .wikiskills/bin/wikiskills.py snapshot <name>`
   (this also works for a not-yet-existing skill — rollback will then delete it).
4. Apply the change. Rules:
   - Keep the diff minimal and the skill concise; a skill is instructions, not an archive.
   - Every substantive claim in the skill must trace to a wiki entry. End the SKILL.md with an HTML comment changelog line: `<!-- evolved <date> from wiki: <page>#<entry ids/titles> -->`.
   - New skills need proper frontmatter (`name`, `description` with clear trigger conditions).
5. Report: what changed and why (citing the wiki entries), then tell the user the update is **provisional until validated** and run — or offer to run — `/wikiskills:validate <name>`.
