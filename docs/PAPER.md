# Mapping the WikiSkill paper to this plugin

Paper: *WikiSkill: Compiling Agent Experience into Persistent Knowledge for Skill
Evolution* — [arXiv:2608.27454](https://arxiv.org/abs/2608.27454), Tang, Rashtchian,
Ferng, Tomkins, Juan, Vu (Google Research & Virginia Tech, Aug 2026). This document
maps the paper, section by section, to this implementation, and states every
deliberate adaptation.

## The paper in one paragraph

Skill-evolution methods (EvoSkill, Trace2Skill, SkillOpt) roll out an agent,
analyze traces, propose skill edits, and gate them on validation — but keep what
was learned scattered across optimization history. WikiSkill adds a structured
knowledge layer between raw experience and executable skills. The workspace has
three layers: a **Raw Layer** (`raw/`, immutable execution traces), a **Wiki
Layer** (`wiki/`, compounding knowledge: pattern pages, an index catalog, an
evolution log, and a skill-impact tracker), and a **Skills Layer** (`skills/`,
active procedural skills). Each iteration (Algorithm 1): the **Inference Agent**
rolls out with active skills injected (and *no* wiki access), the **Wiki
Maintainer** consolidates a stratified sample of traces into the wiki, the
**Skill Proposer** (a ReAct agent reading the wiki and traces on demand) emits
one atomic proposal, and **Gating** accepts it only if validation score strictly
exceeds R_best — otherwise the skills roll back while the wiki, including the
rejected proposal's diff, is retained. Across 5 benchmarks × 5 models WikiSkill
beats the strongest baseline by 3.3–12.0 points; ablations show the persistent
wiki drives the gains (+15.0 avg for Proposer wiki access) and that giving the
inference agent wiki access during rollouts *hurts* (−2.8 avg); evolved skills
transfer across model families and sometimes beat self-evolved ones.

## Component-by-component mapping

| Paper (section) | This plugin |
|---|---|
| Raw Layer `raw/`, immutable, write-once (§3.1) | `.wikiskill/raw/traces/`: per-session `trace-<id>.json` digest **plus** `trace-<id>.log.jsonl`, a copy of the full transcript (capped at `max_raw_log_bytes`, default 2 MB, tail-kept) so the Maintainer/Proposer can do deep root-cause analysis. Captured by the Claude Code `Stop` hook / opencode `session.idle` plugin. Never edited or deleted; git-ignored. |
| Wiki Layer `wiki/` (§3.1): `patterns/`, `index.md`, `logs.md`, `skill-impact.md` | Same four artifacts under `.wikiskill/wiki/` (`log.md` per the Appendix E.2 prompt). Pattern pages: 10–30 lines, failure AND success patterns, root cause + exact command sequences + concrete workarounds, evidence lines per sighting. Index entries in the paper's mandated format: `- [name](patterns/name.md): PROBLEM + ROOT CAUSE + FIX`. Never reset. |
| `skill-impact.md` updated programmatically by the outer-loop harness (§3.2.4) | `wikiskill.py record-validation` appends the entry deterministically: iteration, target skill, **unified diff** of the proposal (computed snapshot → current with difflib), validation score, Accepted/Rejected. Rejected diffs are preserved verbatim so the Proposer never repeats them. |
| Skills Layer: each skill = `SKILL.md` + `PURPOSE.md` (§3.1) | Enforced by the evolve command and methodology skill. `SKILL.md`: frontmatter + When to Apply + When NOT to Apply + Instructions (App. E.3). `PURPOSE.md`: Origin + Patterns Addressed + Evolution History. |
| Inference Agent: skills injected, **wiki access restricted** (§3.2.1, ablation §5.1) | Skills load through the native skill mechanism. The SessionStart hook injects only a loop-status note and explicitly tells the agent not to read `wiki/` during ordinary work. `inject_wiki_context: true` in config opts into wiki injection, documented as deviating from the paper's recommended configuration. |
| Wiki Maintainer, one call over sampled traces (§3.2.2, App. E.2) | The `/wikiskill:consolidate` command + `wikiskill-consolidator` agent, whose prompt adapts App. E.2: deep trace analysis rules, both-pattern documentation, no-duplicate/patch-based editing, mandatory full `index.md` and `log.md` entries. |
| Stratified sampling: ≤8 traces = ≤5 failing + ≤3 passing, logs capped at 15,000 chars (App. C) | `wikiskill.py sample`: newest-first pending traces, ≤`sample_max_failing` (5) with errors + ≤`sample_max_passing` (3) without, printing the `trace_char_cap` (15,000) reading instruction. |
| Skill Proposer: ReAct agent; starts from wiki index + skill-impact + outcome summary; reads pattern pages and ≥4 traces on demand; one atomic create/patch/no_action; prefer patch; don't repeat rejected proposals (§3.2.3, App. E.3) | The `/wikiskill:evolve` command + `wikiskill-evolver` agent mirror the App. E.3 workflow and rules, including the ≥4-traces requirement (relaxed to "all, if fewer exist") and the abstract-vs-concrete lesson from the §5.3 case study. |
| Gating: accept iff R(T_val,k) > R_best; R_best initialized from a baseline run of the current skill set; early stop at R_best = 1.0; rollback on rejection; wiki retained (§3.2.4, Alg. 1) | `record-validation` implements Eq. 4 exactly: `--baseline` initializes R_best; gated runs are ACCEPTED only when strictly above R_best (ties rejected), update R_best on acceptance, print the rollback command on rejection, flag early stop at 1.0, and advance the iteration counter. `rollback` restores the snapshot and can touch nothing in `wiki/`. |
| Iteration bookkeeping for evidence lines and logs (Fig. 3) | `state.json` tracks the iteration k; trace digests are stamped with the iteration they were captured in; pattern evidence lines and log/skill-impact entries reference it. |
| Skill transfer across models (§4.2.2) | Skills and wiki are plain markdown in the repo; both Claude Code and opencode (any underlying models) read the same skill set and feed the same wiki, so the transfer setting comes for free. |

## Deliberate adaptations (and why)

The paper evolves skills against benchmarks with train/val/test splits and a
programmatic scoring function 𝑓(ŷ, y). A development plugin has neither, so:

1. **Rollouts are the user's real sessions**, not a training split. There is no
   ground-truth label per session, so `sample` classifies a trace as *failing* if
   it contains tool errors and *passing* otherwise — a heuristic stand-in for the
   paper's pass/fail stratification.
2. **D_val is user-defined** (`validation/tasks.md`): representative tasks with
   objective success criteria, executed by validator subagents that report
   PASS/FAIL with evidence. With an empty suite the plugin degrades to a soft
   self-review and says so, rather than pretending to measure.
3. **Skill provisioning** uses the host CLI's native skill loading rather than
   full prompt injection. The paper injects full skill content to eliminate
   retrieval failures as a confound (§3.2.1) — a study-design choice; in a real
   CLI the native mechanism is the deployment target itself.
4. **Maintainer/Proposer output JSON patch ops** (`append`/`replace`/`insert_after`)
   in the paper because a harness applies them. Here the applying agent edits
   files directly; the prompts keep the same discipline (minimal targeted edits,
   full index rewrite, exact-substring replace targets).
5. **One iteration per `/wikiskill:loop` run**, user-triggered, instead of K
   automated iterations — the human decides cadence; the iteration counter,
   early-stop rule, and per-iteration atomicity are preserved.
6. The paper notes it lacks wiki pruning (Limitations); this plugin inherits
   that limitation and likewise leaves the wiki append-only.

## References

- [arXiv:2608.27454 (abs)](https://arxiv.org/abs/2608.27454) · [HTML](https://arxiv.org/html/2608.27454) · [HF paper page](https://huggingface.co/papers/2608.27454)
- Karpathy's LLM Wiki gist (the paper's stated inspiration): https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
