# Mapping the WikiSkill paper to this plugin

Paper: *WikiSkill: Compiling Agent Experience into Persistent Knowledge for Skill
Evolution* — [arXiv:2608.27454](https://arxiv.org/abs/2608.27454) (Google Research
& Virginia Tech, Aug 2026).

## The paper in one paragraph

Skill-evolution systems usually collapse three different things into one:
the raw traces of what an agent did, the lessons that experience implies, and the
executable skills the agent loads. WikiSkill separates them into three persistent
layers and runs an orchestrated loop over them: experience is **consolidated**
into a wiki of accumulated knowledge; skill refinements are **proposed from the
wiki** (not from raw history); and each refinement is **gated on validation
performance** — a regressing skill update is rolled back, but the wiki is never
rolled back, so every later update builds on increasingly well-supported,
integrated knowledge. Across five benchmarks and five inference models this beats
prior skill-evolution methods (reported gains of ~3.3–12.0 points), ablations
attribute the gain to the persistent wiki layer, and evolved skills transfer
across model families.

## Component-by-component mapping

| Paper component | This plugin |
|---|---|
| Raw execution experience (layer 1) | Per-session JSON digests in `.wikiskills/traces/`, written by `scripts/capture_trace.py` (Claude Code `Stop` hook) or `opencode/plugin/wikiskills.js` (`session.idle` event): user requests, tool usage counts, tool errors, final response. Compact by design; the full transcript path is kept as a pointer for deep dives. Git-ignored — disposable, per the paper. |
| Persistent knowledge wiki (layer 2) | Markdown pages in `.wikiskills/wiki/pages/` + `index.md`, one topic per page. Entries are typed (Fact / Pitfall / Procedure / Preference) and carry evidence counters and last-seen dates. Append/refine only; contradictions rewrite entries rather than delete them. Meant to be committed to git. |
| Executable skills (layer 3) | Standard Claude-format skills in the project's `skills_dir` (default `.claude/skills/`, configurable to `.opencode/skill`). Loadable by both Claude Code and opencode. |
| Experience → wiki consolidation | `/wikiskills:consolidate` + the `wikiskills-consolidator` subagent, governed by the `wikiskills-methodology` skill (what counts as durable, refine-over-append, generalization, no secrets). `mark-consolidated` tracks which traces have been absorbed. |
| Wiki → skill proposal | `/wikiskills:evolve` + the `wikiskills-evolver` subagent. Proposals must be grounded exclusively in wiki entries (cited in a changelog comment inside the SKILL.md), one change per cycle, evidence-weighted (evidence ≥ 2 → firm instruction; 1 → hedged), honest no-op allowed. |
| Validation gating | `/wikiskills:validate` + the `wikiskills-validator` subagent runs the user-defined suite in `.wikiskills/validation/tasks.md`; `wikiskills.py record-validation` compares the pass rate against the skill's previous score and prints the gate verdict (IMPROVED → accept, REGRESSED → rollback, UNCHANGED → parsimony rule). |
| Skill rollback, wiki persistence | `wikiskills.py snapshot` archives a skill (or records its non-existence) before every edit; `rollback` restores it. Nothing in the toolchain can revert the wiki — the asymmetry the paper's ablations identify as the source of the gains. A failed evolution is itself consolidated back into the wiki as a Pitfall. |
| Orchestrated continual loop | `/wikiskills:loop` = consolidate → evolve → validate in one pass; new sessions then generate fresh traces automatically, closing the cycle. The `SessionStart` hook injects the wiki index so accumulated knowledge is ambient even between evolution cycles. |
| Cross-model / cross-agent skill transfer | Skills and the wiki are plain markdown in the repo, shared by Claude Code and opencode (any models they run); the trace schema is identical across both integrations, so experience from either tool feeds one wiki. |

## Deliberate adaptations

The paper evolves skills against benchmarks with programmatic reward; a
development plugin has no benchmark, so:

- **Validation suite is user-defined** (`validation/tasks.md`): representative
  tasks with objective success criteria play the role of the validation split.
  With an empty suite the plugin degrades to soft gating (adversarial
  self-review of the skill diff) rather than pretending to measure.
- **LLM-in-the-loop instead of an offline optimizer**: consolidation, proposal,
  and judging are performed by the agent itself under the methodology skill's
  rules, with the deterministic parts (snapshots, rollback, records, state)
  handled by a dependency-free Python CLI so they cannot be hallucinated.
- **One skill change per cycle** keeps the credit assignment for validation
  scores clean, mirroring the paper's gated update steps.
