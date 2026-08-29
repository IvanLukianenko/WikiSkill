#!/usr/bin/env python3
"""WikiSkills SessionStart hook — loop status nudge (and optional wiki injection).

By default this injects only a short status note (pending traces, loop hints).
The wiki index is NOT injected: in the WikiSkill framework the Inference Agent
is restricted from Wiki Layer access during rollouts — the paper's ablation
(arXiv:2608.27454 §5.1) shows that wiki access during execution makes traces
less informative and degrades final skill quality. Skills (the Skill Layer)
reach the agent through the normal skill mechanism instead.

Set "inject_wiki_context": true in .wikiskills/config.json to inject the wiki
index anyway (trading paper-faithful evolution for ambient knowledge).
No-ops when the project has no .wikiskills workspace.
"""

import json
import os
import sys


def find_root(start):
    d = os.path.abspath(start or os.getcwd())
    while True:
        candidate = os.path.join(d, ".wikiskills")
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
        "# WikiSkills (auto-injected status)",
        "",
        "This project runs the WikiSkill evolution loop (arXiv:2608.27454): sessions",
        "are traced into `.wikiskills/raw/`, consolidated into the persistent wiki, and",
        "used to evolve validated skills. Work normally; do not read `.wikiskills/wiki/`",
        "during ordinary tasks — the framework restricts the inference agent from wiki",
        "access so that traces stay informative for skill evolution.",
    ]
    if pending:
        lines += ["", f"{pending} trace(s) pending consolidation ({failing} with errors). "
                      "If the user is between tasks, suggest /wikiskills:loop "
                      "(or /wikiskills:consolidate)."]

    if cfg.get("inject_wiki_context"):
        max_chars = int(cfg.get("session_context_max_chars", 3000))
        index = ""
        try:
            with open(os.path.join(root, "wiki", "index.md"), encoding="utf-8") as f:
                index = f.read().strip()
        except OSError:
            pass
        if len(index) > max_chars:
            index = index[:max_chars] + "\n…(truncated — read .wikiskills/wiki/index.md for the rest)"
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
