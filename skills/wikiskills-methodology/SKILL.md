---
name: wikiskills-methodology
description: The WikiSkill framework's rules for maintaining a persistent knowledge wiki and evolving skills from it (arXiv:2608.27454). Use whenever working inside a .wikiskills/ workspace — consolidating traces into wiki pages, writing or refining wiki entries, evolving skills from wiki knowledge, or gating skill updates on validation.
---

# WikiSkills Methodology

This project maintains three separated layers (WikiSkill, arXiv:2608.27454).
Keeping them separated is the point — do not shortcut across them:

| Layer | Location | Lifecycle |
|---|---|---|
| 1. Execution traces | `.wikiskills/traces/*.json` | Raw, disposable. Auto-captured by hooks. Marked consolidated after distillation. |
| 2. Knowledge wiki | `.wikiskills/wiki/` | **Persistent. Never rolled back.** Grows by append/refine only. |
| 3. Executable skills | `skills_dir` from `.wikiskills/config.json` (default `.claude/skills/`) | Versioned. Snapshot before every edit; gated on validation; rollback on regression. |

The flow is strictly `traces → wiki → skills`. Skills are grounded in the wiki,
never directly in traces; the wiki is grounded in traces, never in speculation.

## Wiki page format

One page per topic, kebab-case, under `.wikiskills/wiki/pages/`. Structure:

```markdown
# <Topic title>

> One-line scope of this page.

## Facts
- **<Entry title>** — <1–3 sentence statement>. (evidence: 2, last: 2026-08-29)

## Pitfalls
- **<Entry title>** — Symptom: <…>. Cause: <…>. Remedy: <…>. (evidence: 1, last: 2026-08-29)

## Procedures
- **<Entry title>** — 1) <step> 2) <step> 3) <step>. (evidence: 3, last: 2026-08-29)

## Preferences
- **<Entry title>** — <what the user wants and when>. (evidence: 1, last: 2026-08-29)
```

Omit empty sections. Keep `.wikiskills/wiki/index.md` listing every page with a
one-line description — the index is auto-injected into new sessions, so it must
stay short and high-signal.

## Consolidation rules (traces → wiki)

- Extract only lessons that would change a future session's behavior. One-off
  details, transient state, and secrets (tokens, keys, credentials) never enter the wiki.
- **Refine over append**: if a lesson matches an existing entry, increment its
  evidence counter, update `last:`, and generalize or correct the wording.
- **Never delete**: an entry contradicted by new evidence is rewritten to state the
  corrected knowledge (optionally noting "supersedes earlier belief that …").
- Generalize past the incident: "pin package X below 3.0 because its 3.x API broke
  module Y" beats "got an ImportError on Tuesday".

## Evolution rules (wiki → skills)

- One change per cycle: refine one skill, create one skill, or honestly no-op.
- Create a new skill only for a coherent cluster of ≥3 related wiki entries that
  form a recurring, triggerable capability; otherwise refine.
- **Snapshot first**, always: `python3 .wikiskills/bin/wikiskills.py snapshot <name>`.
- Skills stay concise: instructions that change behavior, not knowledge archives.
  If a wiki entry doesn't change what the agent should *do*, it stays wiki-only.
- Weight by evidence: entries with evidence ≥ 2 can become firm instructions;
  single-evidence entries at most hedged ones ("if X occurs, try Y").
- Traceability: end each evolved SKILL.md with
  `<!-- evolved <date> from wiki: <page>#<entry titles> -->`.

## Validation gating (accept / rollback)

- Every skill change is provisional until validated against
  `.wikiskills/validation/tasks.md`.
- Record results with `record-validation`; the CLI prints the verdict:
  IMPROVED/BASELINE → accept; REGRESSED → `rollback <name>`; UNCHANGED → keep only
  if the skill got simpler.
- **Asymmetric rollback is the core invariant**: rolling back a skill never touches
  the wiki. A failed evolution still leaves its knowledge behind, and the failure
  itself is worth a wiki entry (Pitfall on the relevant page) so the next
  evolution attempt does better.
