#!/usr/bin/env python3
"""WikiSkill CLI — deterministic outer-loop harness for the WikiSkill framework.

Implements the workspace layout and programmatic bookkeeping from "WikiSkill:
Compiling Agent Experience into Persistent Knowledge for Skill Evolution"
(arXiv:2608.27454), Sections 3 and Appendices A/C/E:

  raw/       — immutable execution traces (Raw Layer; write once)
  wiki/      — persistent knowledge base (Wiki Layer; compounds, never reset):
               index.md, log.md, skill-impact.md, patterns/
  skills     — active procedural skills (Skill Layer; reversible, gated)

The LLM agents (Wiki Maintainer, Skill Proposer, validators) do the analysis;
this script does what the paper's outer-loop harness does programmatically:
initialization, stratified trace sampling (App. C), snapshots, validation
gating against R_best (Eq. 4), rollback, and appending proposal diffs and
outcomes to wiki/skill-impact.md (§3.2.4).

Stdlib only, Python 3.8+.
"""

import argparse
import difflib
import json
import os
import shutil
import sys
from datetime import datetime, timezone

WIKISKILL_DIR = ".wikiskill"
DIFF_MAX_LINES = 400


# ---------------------------------------------------------------- helpers

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def now_stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def find_root(start=None):
    d = os.path.abspath(start or os.getcwd())
    while True:
        candidate = os.path.join(d, WIKISKILL_DIR)
        if os.path.isdir(candidate):
            return candidate
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def require_root():
    root = find_root()
    if not root:
        print("error: no .wikiskill directory found. Run `wikiskill.py init` "
              "(or the /wikiskill:init command) in the project root first.",
              file=sys.stderr)
        sys.exit(2)
    return root


def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def save_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, path)


def load_config(root):
    return load_json(os.path.join(root, "config.json"), {})


def skills_dir(root):
    cfg = load_config(root)
    project = os.path.dirname(root)
    return os.path.join(project, cfg.get("skills_dir", os.path.join(".claude", "skills")))


def state_path(root):
    return os.path.join(root, "state.json")


def default_state():
    return {"version": 2, "created": now_iso(), "iteration": 0,
            "best_score": None, "skills": {}, "log": []}


def load_state(root):
    return load_json(state_path(root), default_state())


def log_event(state, kind, detail):
    state.setdefault("log", []).append({"ts": now_iso(), "event": kind, "detail": detail})
    state["log"] = state["log"][-500:]


# ---------------------------------------------------------------- init seeds

SEED_INDEX = """# Wiki Pattern Index

Concise catalog of known patterns — one line per pattern, in the format:

- [pattern-name](patterns/pattern-name.md): PROBLEM + ROOT CAUSE + FIX in one or two sentences.

The description must be specific enough that an agent can judge relevance
without reading the full page.

## Patterns

_None yet. Patterns are added by the Wiki Maintainer during /wikiskill:consolidate._
"""

SEED_LOG = """# Evolution Log

Chronological record of the WikiSkill evolution process (arXiv:2608.27454).
The Wiki Maintainer appends one entry per consolidation with the iteration's
findings and actions; scores and gating outcomes are recorded in
skill-impact.md by the harness.

---
"""

SEED_SKILL_IMPACT = """# Skill Impact Tracker

Ground-truth audit trail of skill proposals, appended programmatically by the
outer-loop harness after each validation gating decision (arXiv:2608.27454,
Section 3.2.4). Each entry records the target skill, the unified diff of the
modification, the validation score, and the acceptance outcome.

Consult this BEFORE proposing a skill change — do not repeat rejected proposals.

---
"""

SEED_TASKS = """# WikiSkill Validation Tasks (D_val)

This suite plays the role of the validation split in the WikiSkill framework
(arXiv:2608.27454): each candidate skill update is accepted only if the pass
rate on these tasks strictly exceeds the best score achieved so far (R_best).
Add tasks that represent the work this project's skills should make easier.

Format — one task per section:

## VT-1: <short name>
- **Prompt:** <what to ask the agent to do, self-contained>
- **Success criteria:** <objectively checkable outcome, e.g. "tests in X pass", "output contains Y", "file Z compiles">
- **Cleanup:** <how to undo any side effects, or "none">

_Add your first task above. With no tasks defined, /wikiskill:validate
falls back to a self-review of the skill diff instead of hard gating._
"""

SEED_CONFIG = {
    "skills_dir": ".claude/skills",
    "inject_wiki_context": False,
    "session_context_max_chars": 3000,
    "max_raw_log_bytes": 2000000,
    "sample_max_failing": 5,
    "sample_max_passing": 3,
    "trace_char_cap": 15000,
    "notes": ("skills_dir is relative to the project root (set to .opencode/skill for "
              "opencode-native skills). inject_wiki_context=false matches the paper's "
              "default: the Inference Agent is restricted from wiki access during "
              "rollouts (arXiv:2608.27454 §5.1 ablation); set true to inject the wiki "
              "index into new sessions anyway.")
}


def cmd_init(args):
    project = os.path.abspath(args.dir or os.getcwd())
    root = os.path.join(project, WIKISKILL_DIR)
    created = not os.path.isdir(root)
    for sub in (os.path.join("raw", "traces"), os.path.join("wiki", "patterns"),
                "archive", "validation", "bin"):
        os.makedirs(os.path.join(root, sub), exist_ok=True)

    def seed(rel, content):
        path = os.path.join(root, rel)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

    seed(os.path.join("wiki", "index.md"), SEED_INDEX)
    seed(os.path.join("wiki", "log.md"), SEED_LOG)
    seed(os.path.join("wiki", "skill-impact.md"), SEED_SKILL_IMPACT)
    seed(os.path.join("validation", "tasks.md"), SEED_TASKS)
    seed(".gitignore", "raw/\nbin/\n")
    if not os.path.exists(os.path.join(root, "config.json")):
        save_json(os.path.join(root, "config.json"), SEED_CONFIG)
    if not os.path.exists(state_path(root)):
        state = default_state()
        log_event(state, "init", {"project": project})
        save_json(state_path(root), state)

    try:
        self_path = os.path.abspath(__file__)
        dest = os.path.join(root, "bin", "wikiskill.py")
        if os.path.realpath(self_path) != os.path.realpath(dest):
            shutil.copy2(self_path, dest)
    except OSError as e:
        print(f"warning: could not copy CLI into .wikiskill/bin: {e}", file=sys.stderr)

    print(f"{'Initialized' if created else 'Refreshed'} WikiSkill workspace at {root}")
    print("Three-layer layout (arXiv:2608.27454):")
    print("  .wikiskill/raw/traces/         Raw Layer — immutable execution traces (git-ignored)")
    print("  .wikiskill/wiki/               Wiki Layer — compounding, never reset:")
    print("    index.md                        pattern catalog (PROBLEM + ROOT CAUSE + FIX per line)")
    print("    log.md                          chronological evolution log")
    print("    skill-impact.md                 proposal diffs + gating outcomes (harness-written)")
    print("    patterns/                       one page per failure/success pattern")
    print(f"  Skill Layer: {skills_dir(root)}   (each skill: SKILL.md + PURPOSE.md)")
    print("  .wikiskill/validation/tasks.md D_val — validation suite for gating")
    print("  .wikiskill/archive/            skill snapshots for rollback")
    print("  .wikiskill/bin/wikiskill.py   project-local copy of this CLI")


# ---------------------------------------------------------------- traces

def traces_dir(root):
    return os.path.join(root, "raw", "traces")


def iter_traces(root):
    tdir = traces_dir(root)
    if not os.path.isdir(tdir):
        return
    for name in sorted(os.listdir(tdir)):
        if name.endswith(".json"):
            path = os.path.join(tdir, name)
            data = load_json(path, None)
            if isinstance(data, dict):
                yield path, data


def is_failing(digest):
    return bool(digest.get("errors"))


def cmd_pending(args):
    root = require_root()
    rows = [(p, d) for p, d in iter_traces(root) if not d.get("consolidated")]
    if args.paths:
        for p, _ in rows:
            print(p)
    else:
        print(f"{len(rows)} pending trace(s)")
        for p, d in rows:
            tools = d.get("tools_used") or {}
            kind = "failing" if is_failing(d) else "passing"
            print(f"  [{kind}] {p}  iter={d.get('iteration', '?')} "
                  f"turns={len(d.get('user_requests') or [])} "
                  f"tools={sum(tools.values())} errors={len(d.get('errors') or [])} "
                  f"updated={d.get('updated', '?')}")


def cmd_sample(args):
    """Stratified trace sampling per Appendix C: up to 5 failing + 3 passing
    pending traces, newest first; raw logs are read capped at trace_char_cap."""
    root = require_root()
    cfg = load_config(root)
    max_fail = int(cfg.get("sample_max_failing", 5))
    max_pass = int(cfg.get("sample_max_passing", 3))
    cap = int(cfg.get("trace_char_cap", 15000))
    pending = [(p, d) for p, d in iter_traces(root) if not d.get("consolidated")]
    pending.sort(key=lambda pd: pd[1].get("updated", ""), reverse=True)
    failing = [(p, d) for p, d in pending if is_failing(d)][:max_fail]
    passing = [(p, d) for p, d in pending if not is_failing(d)][:max_pass]
    sample = failing + passing
    print(f"Sampled {len(sample)} of {len(pending)} pending trace(s) "
          f"({len(failing)} failing, {len(passing)} passing; "
          f"stratification per arXiv:2608.27454 App. C).")
    if cap:
        print(f"When reading a raw log below, read at most the first {cap} characters.")
    for p, d in sample:
        raw_log = d.get("raw_log") or ""
        line = f"  [{'failing' if is_failing(d) else 'passing'}] digest: {p}"
        if raw_log and os.path.exists(raw_log):
            line += f"\n            raw log: {raw_log}"
        print(line)
    if not sample:
        print("  (nothing pending)")


def cmd_mark_consolidated(args):
    root = require_root()
    if args.all:
        targets = [p for p, d in iter_traces(root) if not d.get("consolidated")]
    else:
        targets = args.files
    if not targets:
        print("nothing to mark")
        return
    n = 0
    for path in targets:
        data = load_json(path, None)
        if isinstance(data, dict):
            data["consolidated"] = True
            data["consolidated_at"] = now_iso()
            save_json(path, data)
            n += 1
    state = load_state(root)
    log_event(state, "consolidate", {"traces": n})
    save_json(state_path(root), state)
    print(f"marked {n} trace(s) consolidated")


# ---------------------------------------------------------------- snapshots

def cmd_snapshot(args):
    root = require_root()
    sdir = skills_dir(root)
    src = os.path.join(sdir, args.skill)
    stamp = now_stamp()
    dest = os.path.join(root, "archive", args.skill, stamp)
    n = 1
    while os.path.exists(dest):
        dest = os.path.join(root, "archive", args.skill, f"{stamp}-{n}")
        n += 1
    stamp = os.path.basename(dest)
    existed = os.path.isdir(src)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if existed:
        shutil.copytree(src, dest)
    else:
        os.makedirs(dest, exist_ok=True)
        with open(os.path.join(dest, ".did-not-exist"), "w", encoding="utf-8") as f:
            f.write("Skill did not exist at snapshot time; rollback removes it.\n")
    state = load_state(root)
    rec = state["skills"].setdefault(args.skill, {"snapshots": []})
    rec["snapshots"].append({"ts": stamp, "existed": existed, "path": dest})
    log_event(state, "snapshot", {"skill": args.skill, "ts": stamp, "existed": existed})
    save_json(state_path(root), state)
    print(f"snapshot {stamp} of skill '{args.skill}' "
          f"({'saved from ' + src if existed else 'skill did not exist yet; rollback will delete it'})")


def cmd_rollback(args):
    root = require_root()
    state = load_state(root)
    rec = state["skills"].get(args.skill)
    if not rec or not rec.get("snapshots"):
        print(f"error: no snapshots recorded for skill '{args.skill}'", file=sys.stderr)
        sys.exit(2)
    snaps = rec["snapshots"]
    if args.ts:
        snap = next((s for s in snaps if s["ts"] == args.ts), None)
        if not snap:
            print(f"error: no snapshot {args.ts}; available: {[s['ts'] for s in snaps]}",
                  file=sys.stderr)
            sys.exit(2)
    else:
        snap = snaps[-1]
    sdir = skills_dir(root)
    target = os.path.join(sdir, args.skill)
    if os.path.isdir(target):
        shutil.rmtree(target)
    if snap["existed"]:
        shutil.copytree(snap["path"], target)
        outcome = f"restored skill '{args.skill}' to snapshot {snap['ts']}"
    else:
        outcome = f"removed skill '{args.skill}' (did not exist at snapshot {snap['ts']})"
    log_event(state, "rollback", {"skill": args.skill, "ts": snap["ts"]})
    save_json(state_path(root), state)
    print(outcome)
    print("note: skills roll back; the wiki is retained across all iterations (arXiv:2608.27454 Alg. 1, line 16).")


def cmd_snapshots(args):
    root = require_root()
    state = load_state(root)
    rec = state["skills"].get(args.skill, {})
    for s in rec.get("snapshots", []):
        print(f"{s['ts']}  existed={s['existed']}  {s['path']}")
    if not rec.get("snapshots"):
        print("(none)")


# ---------------------------------------------------------------- gating

def read_tree(base):
    """Return {relpath: lines} for all text files under base ('' if missing)."""
    files = {}
    if not os.path.isdir(base):
        return files
    for dirpath, _dirnames, filenames in os.walk(base):
        for name in sorted(filenames):
            if name == ".did-not-exist":
                continue
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, base)
            try:
                with open(full, encoding="utf-8", errors="replace") as f:
                    files[rel] = f.read().splitlines(keepends=True)
            except OSError:
                files[rel] = ["<unreadable>\n"]
    return files


def skill_diff(root, skill):
    """Unified diff of the skill's latest snapshot vs. its current state."""
    state = load_state(root)
    rec = state["skills"].get(skill, {})
    snaps = rec.get("snapshots", [])
    current = read_tree(os.path.join(skills_dir(root), skill))
    if snaps:
        before = read_tree(snaps[-1]["path"])
        before_label = f"snapshot {snaps[-1]['ts']}"
    else:
        before, before_label = {}, "no snapshot recorded"
    lines = []
    for rel in sorted(set(before) | set(current)):
        old = before.get(rel, [])
        new = current.get(rel, [])
        if old == new:
            continue
        lines.extend(difflib.unified_diff(
            old, new,
            fromfile=f"a/{skill}/{rel} ({before_label})",
            tofile=f"b/{skill}/{rel}",
            n=2))
    text = "".join(lines)
    out_lines = text.splitlines()
    if len(out_lines) > DIFF_MAX_LINES:
        out_lines = out_lines[:DIFF_MAX_LINES] + [f"... (diff truncated at {DIFF_MAX_LINES} lines)"]
    return "\n".join(out_lines) if out_lines else "(no file changes detected)"


def append_skill_impact(root, entry_md):
    path = os.path.join(root, "wiki", "skill-impact.md")
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(SEED_SKILL_IMPACT)
    with open(path, "a", encoding="utf-8") as f:
        f.write(entry_md)


def cmd_record_validation(args):
    """Validation gating per Eq. 4: accept iff score > R_best; append the
    proposal's diff and outcome to wiki/skill-impact.md (§3.2.4)."""
    root = require_root()
    if args.total <= 0:
        print("error: --total must be > 0", file=sys.stderr)
        sys.exit(2)
    score = round(args.passed / args.total, 4)
    state = load_state(root)
    best = state.get("best_score")
    iteration = state.get("iteration", 0)

    entry = {"ts": now_iso(), "iteration": iteration, "skill": args.skill,
             "passed": args.passed, "total": args.total, "score": score,
             "note": args.note or ""}
    results = os.path.join(root, "validation", "results.jsonl")
    os.makedirs(os.path.dirname(results), exist_ok=True)

    if args.baseline:
        state["best_score"] = score
        entry["baseline"] = True
        with open(results, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        log_event(state, "baseline", entry)
        save_json(state_path(root), state)
        append_skill_impact(root, (
            f"\n## Baseline (before iteration {iteration})\n\n"
            f"- **Validation score (R_best init):** {args.passed}/{args.total} = {score:.2f}\n"
            f"- **Skills active:** {args.skill or '(current skill set)'}\n"
            f"- **Note:** {args.note or '-'}\n"))
        msg = f"BASELINE: R_best initialized to {score:.2f} ({args.passed}/{args.total})."
        if score >= 1.0:
            msg += (" Validation is already perfect — per the framework, evolution "
                    "stops early; add harder validation tasks to make gating informative.")
        print(msg)
        return

    if not args.skill:
        print("error: --skill is required (the atomic proposal's target skill)", file=sys.stderr)
        sys.exit(2)
    if best is None:
        print("warning: no baseline recorded; treating this run as the baseline. "
              "Run `record-validation --baseline` before the first evolution next time.",
              file=sys.stderr)
        best = 0.0 if score > 0 else -1.0  # ensure first real run can be accepted

    accepted = score > best
    outcome = "Accepted" if accepted else "Rejected"
    diff = skill_diff(root, args.skill)

    entry["best_before"] = best
    entry["outcome"] = outcome
    with open(results, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    append_skill_impact(root, (
        f"\n## Iteration {iteration}: {outcome.lower()} `{args.skill}`\n\n"
        f"- **Validation score:** {args.passed}/{args.total} = {score:.2f} "
        f"(R_best before: {best:.2f})\n"
        f"- **Outcome:** {outcome}"
        f"{'' if accepted else ' — do NOT propose this modification again'}\n"
        f"- **Note:** {args.note or '-'}\n"
        f"- **Proposal diff:**\n\n```diff\n{diff}\n```\n"))

    if accepted:
        state["best_score"] = score
    state["iteration"] = iteration + 1
    log_event(state, "validation", entry)
    save_json(state_path(root), state)

    if accepted:
        print(f"ACCEPTED: '{args.skill}' scored {args.passed}/{args.total} ({score:.2f}) "
              f"> R_best {best:.2f}. R_best updated; keep the skill update.")
        if score >= 1.0:
            print("R_best reached 1.0 — evolution loop terminates early (Alg. 1, line 4). "
                  "Add harder validation tasks to continue evolving.")
    else:
        print(f"REJECTED: '{args.skill}' scored {args.passed}/{args.total} ({score:.2f}) "
              f"<= R_best {best:.2f}. Roll back now: "
              f"`python3 .wikiskill/bin/wikiskill.py rollback {args.skill}`. "
              f"The wiki (including this recorded outcome) is retained.")
    print(f"skill-impact.md updated; iteration advanced to {iteration + 1}.")


# ---------------------------------------------------------------- status

def cmd_status(args):
    root = find_root()
    if not root:
        print("WikiSkill: not initialized here. Run /wikiskill:init "
              "(or `python3 wikiskill.py init`).")
        return
    state = load_state(root)
    traces = list(iter_traces(root))
    pending = [t for _, t in traces if not t.get("consolidated")]
    pat_dir = os.path.join(root, "wiki", "patterns")
    patterns = sorted(p for p in os.listdir(pat_dir) if p.endswith(".md")) \
        if os.path.isdir(pat_dir) else []
    sdir = skills_dir(root)
    skills = sorted(d for d in os.listdir(sdir)
                    if os.path.isdir(os.path.join(sdir, d))) if os.path.isdir(sdir) else []
    best = state.get("best_score")
    print(f"WikiSkill workspace: {root}")
    print(f"  iteration: {state.get('iteration', 0)}   "
          f"R_best: {'not baselined yet' if best is None else f'{best:.2f}'}")
    print(f"  raw:     {len(traces)} trace(s) captured, {len(pending)} pending "
          f"({sum(1 for t in pending if is_failing(t))} failing / "
          f"{sum(1 for t in pending if not is_failing(t))} passing)")
    print(f"  wiki:    {len(patterns)} pattern(s): {', '.join(patterns) if patterns else '(none)'}")
    print(f"  skills:  {len(skills)} in {sdir}: {', '.join(skills) if skills else '(none)'}")
    for name, rec in sorted(state.get("skills", {}).items()):
        print(f"  skill '{name}': {len(rec.get('snapshots', []))} snapshot(s)")
    if best is not None and best >= 1.0:
        print("  NOTE: R_best is 1.0 — evolution is early-stopped until harder "
              "validation tasks are added.")
    log = state.get("log", [])
    if log:
        print("  recent events:")
        for e in log[-5:]:
            print(f"    {e['ts']}  {e['event']}  {json.dumps(e['detail'], ensure_ascii=False)[:100]}")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(prog="wikiskill.py", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init", help="initialize the .wikiskill workspace in a project")
    p.add_argument("--dir", help="project root (default: cwd)")
    p.set_defaults(fn=cmd_init)

    p = sub.add_parser("status", help="summarize workspace state")
    p.set_defaults(fn=cmd_status)

    p = sub.add_parser("pending", help="list traces awaiting consolidation")
    p.add_argument("--paths", action="store_true", help="print digest file paths only")
    p.set_defaults(fn=cmd_pending)

    p = sub.add_parser("sample", help="stratified sample of pending traces "
                                      "(<=5 failing + <=3 passing, per App. C)")
    p.set_defaults(fn=cmd_sample)

    p = sub.add_parser("mark-consolidated", help="mark traces as consolidated into the wiki")
    p.add_argument("files", nargs="*", help="trace digest file paths")
    p.add_argument("--all", action="store_true", help="mark all pending traces")
    p.set_defaults(fn=cmd_mark_consolidated)

    p = sub.add_parser("snapshot", help="snapshot a skill before applying a proposal")
    p.add_argument("skill")
    p.set_defaults(fn=cmd_snapshot)

    p = sub.add_parser("snapshots", help="list snapshots for a skill")
    p.add_argument("skill")
    p.set_defaults(fn=cmd_snapshots)

    p = sub.add_parser("rollback", help="restore a skill to a snapshot (wiki is retained)")
    p.add_argument("skill")
    p.add_argument("--ts", help="snapshot timestamp (default: latest)")
    p.set_defaults(fn=cmd_rollback)

    p = sub.add_parser("record-validation",
                       help="record a validation run, gate against R_best, "
                            "and append the outcome + diff to wiki/skill-impact.md")
    p.add_argument("--skill", default="", help="target skill of the atomic proposal")
    p.add_argument("--passed", type=int, required=True)
    p.add_argument("--total", type=int, required=True)
    p.add_argument("--note", default="")
    p.add_argument("--baseline", action="store_true",
                   help="initialize R_best from this run (no gating, no iteration bump)")
    p.set_defaults(fn=cmd_record_validation)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
