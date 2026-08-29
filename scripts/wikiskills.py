#!/usr/bin/env python3
"""WikiSkills CLI — deterministic storage layer for the WikiSkill framework.

Implements the three-layer separation from "WikiSkill: Compiling Agent
Experience into Persistent Knowledge for Skill Evolution" (arXiv:2608.27454):

  1. traces/   — raw execution experience (captured by hooks, ephemeral)
  2. wiki/     — persistent consolidated knowledge (never rolled back)
  3. skills    — executable skills (versioned, validated, rollback-able)

This script is intentionally dependency-free (stdlib only, Python 3.8+).
The LLM does the thinking (consolidation, evolution, validation judging);
this script does the bookkeeping (init, snapshots, rollback, records).
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone

WIKISKILLS_DIR = ".wikiskills"


# ---------------------------------------------------------------- helpers

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def now_stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def find_root(start=None):
    """Walk upward from start (or cwd) looking for a .wikiskills directory."""
    d = os.path.abspath(start or os.getcwd())
    while True:
        candidate = os.path.join(d, WIKISKILLS_DIR)
        if os.path.isdir(candidate):
            return candidate
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def require_root():
    root = find_root()
    if not root:
        print("error: no .wikiskills directory found. Run `wikiskills.py init` "
              "(or the /wikiskills:init command) in the project root first.",
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


def load_state(root):
    return load_json(state_path(root), {"version": 1, "skills": {}, "log": []})


def log_event(state, kind, detail):
    state.setdefault("log", []).append({"ts": now_iso(), "event": kind, "detail": detail})
    # keep the log bounded
    state["log"] = state["log"][-500:]


# ---------------------------------------------------------------- init

SEED_INDEX = """# WikiSkills Wiki — Index

This wiki is the persistent knowledge layer of the WikiSkill framework
(arXiv:2608.27454). It accumulates lessons distilled from execution traces.
It is **append/refine only**: entries are strengthened, generalized, or
corrected with evidence — never deleted merely because a skill was rolled back.

## Pages

_None yet. Run `/wikiskills:consolidate` after a few working sessions._

## Conventions

- One page per topic under `pages/`, kebab-case filenames.
- Every entry carries an evidence counter and last-seen date, e.g. `(evidence: 3, last: 2026-08-29)`.
- Entries are one of: **Fact**, **Pitfall**, **Procedure**, **Preference**.
"""

SEED_TASKS = """# WikiSkills Validation Tasks

Skill updates are gated on this suite (the validation-gating step of
WikiSkill, arXiv:2608.27454). Each task is a prompt plus objective success
criteria that the validator can check. Add tasks that represent the work
this project's skills are supposed to make easier.

Format — one task per section:

## VT-1: <short name>
- **Prompt:** <what to ask the agent to do, self-contained>
- **Success criteria:** <objectively checkable outcome, e.g. "tests in X pass", "output contains Y", "file Z compiles">
- **Cleanup:** <how to undo any side effects, or "none">

_Add your first task above. With no tasks defined, /wikiskills:validate
falls back to a self-review of the skill diff instead of hard gating._
"""

SEED_CONFIG = {
    "skills_dir": ".claude/skills",
    "session_context_max_chars": 3000,
    "trace_max_items": 20,
    "notes": "skills_dir is relative to the project root. Set to .opencode/skill for opencode-native skills."
}


def cmd_init(args):
    project = os.path.abspath(args.dir or os.getcwd())
    root = os.path.join(project, WIKISKILLS_DIR)
    created = not os.path.isdir(root)
    for sub in ("traces", os.path.join("wiki", "pages"), "archive", "validation", "bin"):
        os.makedirs(os.path.join(root, sub), exist_ok=True)

    def seed(rel, content):
        path = os.path.join(root, rel)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

    seed(os.path.join("wiki", "index.md"), SEED_INDEX)
    seed(os.path.join("validation", "tasks.md"), SEED_TASKS)
    seed(".gitignore", "traces/\nbin/\n")
    if not os.path.exists(os.path.join(root, "config.json")):
        save_json(os.path.join(root, "config.json"), SEED_CONFIG)
    if not os.path.exists(state_path(root)):
        state = {"version": 1, "created": now_iso(), "skills": {}, "log": []}
        log_event(state, "init", {"project": project})
        save_json(state_path(root), state)

    # Copy this CLI into the project so commands/agents can call it without
    # knowing the plugin install location.
    try:
        self_path = os.path.abspath(__file__)
        dest = os.path.join(root, "bin", "wikiskills.py")
        if os.path.realpath(self_path) != os.path.realpath(dest):
            shutil.copy2(self_path, dest)
    except OSError as e:
        print(f"warning: could not copy CLI into .wikiskills/bin: {e}", file=sys.stderr)

    print(f"{'Initialized' if created else 'Refreshed'} WikiSkills workspace at {root}")
    print("Layout:")
    print("  .wikiskills/traces/            raw execution traces (layer 1, git-ignored)")
    print("  .wikiskills/wiki/              persistent knowledge wiki (layer 2)")
    print("  .wikiskills/archive/           skill snapshots for rollback")
    print("  .wikiskills/validation/        validation task suite + results")
    print("  .wikiskills/bin/wikiskills.py  project-local copy of this CLI")
    print(f"  skills dir (layer 3): {skills_dir(root)}")


# ---------------------------------------------------------------- traces

def iter_traces(root):
    tdir = os.path.join(root, "traces")
    if not os.path.isdir(tdir):
        return
    for name in sorted(os.listdir(tdir)):
        if name.endswith(".json"):
            path = os.path.join(tdir, name)
            data = load_json(path, None)
            if isinstance(data, dict):
                yield path, data


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
            print(f"  {p}  turns={len(d.get('user_requests') or [])} "
                  f"tools={sum(tools.values())} errors={len(d.get('errors') or [])} "
                  f"updated={d.get('updated', '?')}")


def cmd_mark_consolidated(args):
    root = require_root()
    targets = []
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
    rec = state["skills"].setdefault(args.skill, {"snapshots": [], "validations": []})
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
    snap = None
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
    print("note: the wiki is persistent by design — rollback touches only the skill (arXiv:2608.27454).")


def cmd_snapshots(args):
    root = require_root()
    state = load_state(root)
    rec = state["skills"].get(args.skill, {})
    for s in rec.get("snapshots", []):
        print(f"{s['ts']}  existed={s['existed']}  {s['path']}")
    if not rec.get("snapshots"):
        print("(none)")


# ---------------------------------------------------------------- validation

def cmd_record_validation(args):
    root = require_root()
    total = args.total
    passed = args.passed
    if total <= 0:
        print("error: --total must be > 0", file=sys.stderr)
        sys.exit(2)
    score = round(passed / total, 4)
    entry = {"ts": now_iso(), "skill": args.skill, "passed": passed,
             "total": total, "score": score, "note": args.note or ""}
    results = os.path.join(root, "validation", "results.jsonl")
    prev = None
    if os.path.exists(results):
        with open(results, encoding="utf-8") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if rec.get("skill") == args.skill:
                    prev = rec
    with open(results, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    state = load_state(root)
    srec = state["skills"].setdefault(args.skill, {"snapshots": [], "validations": []})
    srec["validations"].append(entry)
    srec["validations"] = srec["validations"][-50:]
    log_event(state, "validation", entry)
    save_json(state_path(root), state)

    if prev is None:
        verdict = "BASELINE"
        detail = "first recorded validation for this skill — treat as the baseline"
    elif score > prev["score"]:
        verdict = "IMPROVED"
        detail = f"{prev['score']:.2f} -> {score:.2f}: ACCEPT the skill update"
    elif score < prev["score"]:
        verdict = "REGRESSED"
        detail = (f"{prev['score']:.2f} -> {score:.2f}: ROLLBACK the skill "
                  f"(`wikiskills.py rollback {args.skill}`) — keep the wiki as is")
    else:
        verdict = "UNCHANGED"
        detail = f"score held at {score:.2f}: keep the update only if it simplifies the skill"
    print(f"{verdict}: {args.skill} passed {passed}/{total} ({score:.2f}). {detail}")


# ---------------------------------------------------------------- status

def cmd_status(args):
    root = find_root()
    if not root:
        print("WikiSkills: not initialized here. Run /wikiskills:init "
              "(or `python3 wikiskills.py init`).")
        return
    traces = list(iter_traces(root))
    pending = [t for _, t in traces if not t.get("consolidated")]
    pages_dir = os.path.join(root, "wiki", "pages")
    pages = sorted(p for p in os.listdir(pages_dir)) if os.path.isdir(pages_dir) else []
    sdir = skills_dir(root)
    skills = sorted(d for d in os.listdir(sdir)
                    if os.path.isdir(os.path.join(sdir, d))) if os.path.isdir(sdir) else []
    state = load_state(root)
    print(f"WikiSkills workspace: {root}")
    print(f"  traces:  {len(traces)} captured, {len(pending)} pending consolidation")
    print(f"  wiki:    {len(pages)} page(s): {', '.join(pages) if pages else '(none)'}")
    print(f"  skills:  {len(skills)} in {sdir}: {', '.join(skills) if skills else '(none)'}")
    for name, rec in sorted(state.get("skills", {}).items()):
        vals = rec.get("validations", [])
        last = vals[-1] if vals else None
        lastv = f"last validation {last['passed']}/{last['total']} ({last['score']:.2f}) at {last['ts']}" \
            if last else "never validated"
        print(f"  skill '{name}': {len(rec.get('snapshots', []))} snapshot(s), {lastv}")
    log = state.get("log", [])
    if log:
        print("  recent events:")
        for e in log[-5:]:
            print(f"    {e['ts']}  {e['event']}  {json.dumps(e['detail'], ensure_ascii=False)[:100]}")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(prog="wikiskills.py", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init", help="initialize .wikiskills in a project")
    p.add_argument("--dir", help="project root (default: cwd)")
    p.set_defaults(fn=cmd_init)

    p = sub.add_parser("status", help="summarize workspace state")
    p.set_defaults(fn=cmd_status)

    p = sub.add_parser("pending", help="list traces awaiting consolidation")
    p.add_argument("--paths", action="store_true", help="print file paths only")
    p.set_defaults(fn=cmd_pending)

    p = sub.add_parser("mark-consolidated", help="mark traces as consolidated into the wiki")
    p.add_argument("files", nargs="*", help="trace file paths")
    p.add_argument("--all", action="store_true", help="mark all pending traces")
    p.set_defaults(fn=cmd_mark_consolidated)

    p = sub.add_parser("snapshot", help="snapshot a skill before evolving it")
    p.add_argument("skill")
    p.set_defaults(fn=cmd_snapshot)

    p = sub.add_parser("snapshots", help="list snapshots for a skill")
    p.add_argument("skill")
    p.set_defaults(fn=cmd_snapshots)

    p = sub.add_parser("rollback", help="restore a skill to a snapshot (wiki is untouched)")
    p.add_argument("skill")
    p.add_argument("--ts", help="snapshot timestamp (default: latest)")
    p.set_defaults(fn=cmd_rollback)

    p = sub.add_parser("record-validation", help="record a validation run and print the gate verdict")
    p.add_argument("--skill", required=True)
    p.add_argument("--passed", type=int, required=True)
    p.add_argument("--total", type=int, required=True)
    p.add_argument("--note", default="")
    p.set_defaults(fn=cmd_record_validation)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
