---
description: Skill Proposer step — propose one atomic, wiki-informed skill change (create/patch/no-action)
argument-hint: [skill-name (optional focus)]
allowed-tools: Bash(python3:*), Read, Write, Edit, Glob, Grep, Task
---

## Context

- Status: !`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/wikiskill.py" status`
- Requested focus: "$ARGUMENTS"

## Your task

Act as the **Skill Proposer** of the WikiSkill framework (arXiv:2608.27454, §3.2.3 and Appendix E.3): explore the wiki and execution traces ReAct-style, diagnose root causes, and propose exactly ONE atomic skill change. Follow the `wikiskill-methodology` skill for formats. For a large wiki you may delegate proposal drafting to the `wikiskill-evolver` agent and apply its proposal yourself.

Workflow (in this order — read the wiki FIRST):

1. Read `.wikiskill/wiki/index.md` to see what patterns exist.
2. Read `.wikiskill/wiki/skill-impact.md` to see what was tried before. It contains the diffs of rejected proposals — **do NOT repeat a rejected approach.**
3. Read the specific pattern pages relevant to current failures, and the existing skills (each `SKILL.md` + `PURPOSE.md`) in the skills directory shown in the status output.
4. Read execution traces on demand to confirm root causes: read at least 4 trace digests/raw logs under `.wikiskill/raw/traces/` (or all of them if fewer exist), targeting your exploration at the failures the patterns describe.
5. Decide ONE of:
   - **patch** an existing skill — preferred when an existing skill is partially correct. Keep edits minimal and targeted (append / replace short specific sections), not a rewrite.
   - **create** a new skill — when no existing skill covers a documented, recurring pattern cluster.
   - **no action** — if the wiki holds nothing actionable beyond what skills encode, or everything actionable was already rejected. Say so honestly and stop (do not snapshot).
6. Snapshot before touching skill `<name>`: `python3 .wikiskill/bin/wikiskill.py snapshot <name>` (works for a not-yet-existing skill; rollback then deletes it).
7. Apply the change:
   - `SKILL.md`: YAML frontmatter (`name`, `description`), then sections **When to Apply**, **When NOT to Apply**, and **Instructions**. Focus on action patterns and concrete strategies; keep it concise and actionable.
   - `PURPOSE.md`: sections **Origin** (what motivated this skill, including any prior rejected attempt it learns from), **Patterns Addressed** (the wiki pattern pages it draws on), and **Evolution History** (dated one-liners per accepted change).
8. Report the proposal (target skill, change summary, wiki patterns cited), then state that per validation gating the update is **provisional** and run — or tell the user to run — `/wikiskill:validate <name>`.

Honor the requested focus above if one was given, but the rejected-proposal rule still applies.
