#!/usr/bin/env python3
"""WikiSkill SessionStart hook — loop status nudge (and optional wiki injection).

By default this injects only a short status note (pending traces, loop hints).
The wiki index is NOT injected: in the WikiSkill framework the Inference Agent
is restricted from Wiki Layer access during rollouts — the paper's ablation
(arXiv:2608.27454 §5.1) shows that wiki access during execution makes traces
less informative and degrades final skill quality. Skills (the Skill Layer)
reach the agent through the normal skill mechanism instead.

Set "inject_wiki_context": true in .wikiskill/config.json to inject the wiki
index anyway (trading paper-faithful evolution for ambient knowledge).
No-ops when the project has no .wikiskill workspace.
"""

import json
import os
import sys
from datetime import datetime, timezone


def parse_iso(s):
    try:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None


def find_root(start):
    d = os.path.abspath(start or os.getcwd())
    while True:
        candidate = os.path.join(d, ".wikiskill")
        if os.path.isdir(candidate):
            return candidate
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def main():
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        payload = {}
    root = find_root(payload.get("cwd"))
    if not root:
        return

    cfg = {}
    try:
        with open(os.path.join(root, "config.json"), encoding="utf-8") as f:
            cfg = json.load(f)
    except (OSError, ValueError):
        pass

    pending = failing = 0
    tdir = os.path.join(root, "raw", "traces")
    if os.path.isdir(tdir):
        for name in os.listdir(tdir):
            if not name.endswith(".json"):
                continue
            try:
                with open(os.path.join(tdir, name), encoding="utf-8") as f:
                    d = json.load(f) or {}
            except (OSError, ValueError):
                continue
            if not d.get("consolidated"):
                pending += 1
                if d.get("errors"):
                    failing += 1

    lines = [
        "# WikiSkill (auto-injected status)",
        "",
        "This project runs the WikiSkill evolution loop (arXiv:2608.27454): sessions",
        "are traced into `.wikiskill/raw/`, consolidated into the persistent wiki, and",
        "used to evolve validated skills. Work normally; do not read `.wikiskill/wiki/`",
        "during ordinary tasks — the framework restricts the inference agent from wiki",
        "access so that traces stay informative for skill evolution.",
    ]
    if pending:
        lines += ["", f"{pending} trace(s) pending consolidation ({failing} with errors)."]

    # Auto-loop trigger: due when enough session traces are pending, or enough
    # days have passed since the last loop with at least one trace pending.
    state = {}
    try:
        with open(os.path.join(root, "state.json"), encoding="utf-8") as f:
            state = json.load(f) or {}
    except (OSError, ValueError):
        pass
    mode = str(cfg.get("auto_loop", "suggest")).lower()
    reasons = []
    if mode in ("suggest", "auto") and pending > 0:
        every_sessions = int(cfg.get("loop_every_sessions", 5) or 0)
        if every_sessions > 0 and pending >= every_sessions:
            reasons.append(f"{pending} session trace(s) pending (threshold {every_sessions})")
        every_days = float(cfg.get("loop_every_days", 3) or 0)
        last = parse_iso(state.get("last_loop_at") or state.get("created"))
        if every_days > 0 and last is not None:
            days = (datetime.now(timezone.utc) - last).total_seconds() / 86400
            if days >= every_days:
                reasons.append(f"{days:.1f} day(s) since the last loop (threshold {every_days:g})")
    if reasons:
        why = "; ".join(reasons)
        if mode == "auto":
            lines += ["", f"AUTO-LOOP IS DUE ({why}). After you have fully completed the "
                          "user's current request in this session — never before, and never "
                          "interrupting their task — run one full /wikiskill:loop iteration "
                          "(consolidate → evolve → validate) and report its outcome briefly. "
                          "If the session ends without a natural break, skip it silently."]
        else:
            lines += ["", f"AUTO-LOOP IS DUE ({why}). At the first natural moment (your "
                          "greeting, or when the user is between tasks), briefly suggest "
                          "running /wikiskill:loop. Do not run it uninvited."]
    elif pending:
        lines += ["If the user is between tasks, you may suggest /wikiskill:loop "
                  "(or /wikiskill:consolidate)."]

    if cfg.get("inject_wiki_context"):
        max_chars = int(cfg.get("session_context_max_chars", 3000))
        index = ""
        try:
            with open(os.path.join(root, "wiki", "index.md"), encoding="utf-8") as f:
                index = f.read().strip()
        except OSError:
            pass
        if len(index) > max_chars:
            index = index[:max_chars] + "\n…(truncated — read .wikiskill/wiki/index.md for the rest)"
        if index:
            lines += ["", "---", "",
                      "Wiki index (inject_wiki_context is enabled; note this deviates "
                      "from the paper's recommended configuration):", "", index]

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "\n".join(lines),
        }
    }))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
