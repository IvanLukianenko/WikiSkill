#!/usr/bin/env python3
"""WikiSkills SessionStart hook — inject the persistent wiki into new sessions.

Outputs additionalContext containing the wiki index (layer 2 of WikiSkill,
arXiv:2608.27454) plus a nudge when traces are pending consolidation.
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
    max_chars = int(cfg.get("session_context_max_chars", 3000))

    index = ""
    try:
        with open(os.path.join(root, "wiki", "index.md"), encoding="utf-8") as f:
            index = f.read().strip()
    except OSError:
        pass
    if len(index) > max_chars:
        index = index[:max_chars] + "\n…(index truncated — read .wikiskills/wiki/index.md for the rest)"

    pages_dir = os.path.join(root, "wiki", "pages")
    pages = []
    if os.path.isdir(pages_dir):
        pages = sorted(p for p in os.listdir(pages_dir) if p.endswith(".md"))

    pending = 0
    traces_dir = os.path.join(root, "traces")
    if os.path.isdir(traces_dir):
        for name in os.listdir(traces_dir):
            if not name.endswith(".json"):
                continue
            try:
                with open(os.path.join(traces_dir, name), encoding="utf-8") as f:
                    if not (json.load(f) or {}).get("consolidated"):
                        pending += 1
            except (OSError, ValueError):
                continue

    lines = [
        "# WikiSkills — persistent project knowledge (auto-injected)",
        "",
        "This project runs the WikiSkill loop (arXiv:2608.27454). Consult the wiki",
        "pages under `.wikiskills/wiki/pages/` when a topic below is relevant to the",
        "task; they hold lessons distilled from past sessions in this repository.",
        "",
        index,
    ]
    if pages:
        lines += ["", "Wiki pages available: " + ", ".join(pages)]
    if pending:
        lines += ["", f"Note: {pending} execution trace(s) are pending consolidation. "
                      "If the user is between tasks, suggest running /wikiskills:consolidate "
                      "(or the full /wikiskills:loop)."]

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
