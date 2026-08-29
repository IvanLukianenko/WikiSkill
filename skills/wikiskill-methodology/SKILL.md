---
name: wikiskill-methodology
description: The WikiSkill framework's rules for the three-layer workspace and evolution loop (arXiv:2608.27454). Use whenever working inside a .wikiskill/ workspace — consolidating traces into wiki patterns, proposing or applying skill updates, or running validation gating.
---

# WikiSkill Methodology

This project runs the WikiSkill evolution loop over three separated layers
(arXiv:2608.27454, Figure 2). Keeping them separated is the point — never
shortcut across them:

| Layer | Location | Lifecycle |
|---|---|---|
| Raw | `.wikiskill/raw/traces/` | **Permanent, write once.** Auto-captured digests + raw logs. Marked consolidated, never edited or deleted. |
| Wiki | `.wikiskill/wiki/` | **Compounding, never reset.** Grows by create/patch only; retained across all iterations regardless of skill gating. |
| Skills | `skills_dir` from `.wikiskill/config.json` (default `.claude/skills/`) | **Reversible, conditional.** Snapshot before every change; accepted only if validation beats R_best; otherwise rolled back. |

One iteration = Inference rollouts (the user's normal sessions) → Wiki
Maintenance → Skill Proposal → Apply → Validate → Gate (Algorithm 1). The
inference agent is restricted from reading the wiki during ordinary work — the
paper's ablation (§5.1) shows wiki access during rollouts degrades final skill
quality.

## Wiki Layer structure

- `wiki/index.md` — catalog, one line per pattern, exactly:
  `- [pattern-name](patterns/pattern-name.md): PROBLEM + ROOT CAUSE + FIX in one or two sentences.`
  Index quality is critical: it determines whether pattern pages get read.
- `wiki/log.md` — chronological evolution log; the Wiki Maintainer appends one
  entry per consolidation (iteration, findings, actions).
- `wiki/skill-impact.md` — appended **programmatically by the CLI** at
  `record-validation`: proposal diff, validation score, Accepted/Rejected.
  Consult before proposing; never repeat a rejected diff. Do not edit by hand.
- `wiki/patterns/<kebab-name>.md` — one page per pattern, 10–30 lines:
  description; root cause (WHY, not just WHAT); exact command sequences from
  traces; concrete solutions/workarounds; evidence lines per sighting
  (`Evidence: Iter 2: session ab12cd | Iter 3: persists`). Document both
  failure AND success patterns. Update existing pages instead of duplicating;
  use minimal incremental edits. No secrets, ever.

## Skill Layer structure

Each skill directory contains exactly two authored files:

- `SKILL.md` — YAML frontmatter (`name`, `description`), then sections
  **When to Apply**, **When NOT to Apply**, **Instructions**. Concrete action
  patterns and strategies, not abstract advice (the paper's accepted skills use
  rules like "Never return an item to its origin location", not "act
  goal-directedly"). Concise: instructions that change behavior; supporting
  knowledge stays in the wiki.
- `PURPOSE.md` — maps the skill back to its motivating wiki patterns:
  **Origin**, **Patterns Addressed**, **Evolution History** (dated line per
  accepted change).

## Evolution rules (Skill Proposer)

- Exactly ONE atomic proposal per iteration: create one skill, patch one skill,
  or honestly no-action.
- Read order: index → skill-impact (rejected diffs!) → relevant patterns →
  existing skills → ≥4 raw traces (or all, if fewer).
- Prefer patching a partially-correct skill over creating a new one; patches are
  minimal targeted edits, not rewrites.
- Snapshot first, always: `python3 .wikiskill/bin/wikiskill.py snapshot <name>`.

## Gating and rollback (Eq. 4)

- R_best is initialized by a baseline validation run (`record-validation
  --baseline`) and updated only on acceptance.
- Accept iff score **strictly >** R_best. Ties and regressions are rejected →
  `rollback <name>` immediately. There is no "keep if unchanged".
- R_best = 1.0 → evolution early-stops; harder validation tasks are needed.
- **The asymmetry is the core invariant:** rollback touches only the skill; the
  wiki — patterns, log, and the recorded rejection itself — is retained, so the
  next proposal builds on everything learned, including what failed.
