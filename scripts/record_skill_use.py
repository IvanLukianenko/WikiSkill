#!/usr/bin/env python3
"""WikiSkill PostToolUse(Skill) hook — record every skill invocation.

Appends one line per invocation to .wikiskill/stats/skill-usage.jsonl:
{ts, session_id, iteration, skill, args}. Together with the per-session
"errors after use" signal computed by the Stop hook, this feeds
`wikiskill.py skill-stats`, which tells the Wiki Maintainer and Skill
Proposer which skills are actually used and whether they help.

No-ops when the project has no .wikiskill workspace. Never fails the tool call.
"""

import json
import os
import sys
from datetime import datetime, timezone


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
        return
    if payload.get("tool_name") != "Skill":
        return
    root = find_root(payload.get("cwd"))
    if not root:
        return
    tool_input = payload.get("tool_input") or {}
    skill = str(tool_input.get("skill") or "").strip()
    if not skill:
        return
    iteration = 0
    try:
        with open(os.path.join(root, "state.json"), encoding="utf-8") as f:
            iteration = int((json.load(f) or {}).get("iteration", 0))
    except (OSError, ValueError):
        pass
    args = " ".join(str(tool_input.get("args") or "").split())[:200]
    entry = {
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "session_id": str(payload.get("session_id") or "unknown"),
        "iteration": iteration,
        "skill": skill,
        "args": args,
    }
    stats_dir = os.path.join(root, "stats")
    os.makedirs(stats_dir, exist_ok=True)
    with open(os.path.join(stats_dir, "skill-usage.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
