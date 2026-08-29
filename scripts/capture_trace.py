#!/usr/bin/env python3
"""WikiSkills Stop hook — capture a compact execution-trace digest (layer 1).

Reads the Claude Code Stop-hook payload from stdin, parses the session
transcript, and writes/updates a per-session trace digest under
.wikiskills/traces/. No-ops (exit 0) when the project has no .wikiskills
workspace, so the plugin stays inert until /wikiskills:init.

Digests are compact on purpose: raw experience is the disposable layer of
WikiSkill (arXiv:2608.27454); durable lessons belong in the wiki after
/wikiskills:consolidate.
"""

import json
import os
import sys
from datetime import datetime, timezone

MAX_TEXT = 400
MAX_LAST = 1200
MAX_ITEMS = 25


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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


def clip(text, limit=MAX_TEXT):
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(
            item.get("text", "") for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        )
    return ""


def parse_transcript(path):
    user_requests, errors, tools = [], [], {}
    last_assistant = ""
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if rec.get("isMeta"):
                continue
            msg = rec.get("message") or {}
            role = msg.get("role")
            content = msg.get("content")
            if isinstance(content, str):
                if role == "user" and rec.get("type") == "user":
                    t = content.strip()
                    if t and not t.startswith("<") and not t.startswith("Caveat:"):
                        user_requests.append(clip(t))
                elif role == "assistant":
                    t = content.strip()
                    if t:
                        last_assistant = clip(t, MAX_LAST)
                continue
            if not isinstance(content, list):
                continue
            for item in content:
                if not isinstance(item, dict):
                    continue
                kind = item.get("type")
                if kind == "text":
                    t = (item.get("text") or "").strip()
                    if not t:
                        continue
                    if role == "assistant":
                        last_assistant = clip(t, MAX_LAST)
                    elif role == "user" and not t.startswith("<") and not t.startswith("Caveat:"):
                        user_requests.append(clip(t))
                elif kind == "tool_use":
                    name = item.get("name", "?")
                    tools[name] = tools.get(name, 0) + 1
                elif kind == "tool_result" and item.get("is_error"):
                    errors.append(clip(text_of(item.get("content"))))
    return user_requests, errors, tools, last_assistant


def main():
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return
    root = find_root(payload.get("cwd"))
    if not root:
        return
    session_id = str(payload.get("session_id") or "unknown")
    transcript = payload.get("transcript_path")

    user_requests, errors, tools, last_assistant = [], [], {}, ""
    if transcript and os.path.exists(transcript):
        try:
            user_requests, errors, tools, last_assistant = parse_transcript(transcript)
        except OSError:
            pass

    traces_dir = os.path.join(root, "traces")
    os.makedirs(traces_dir, exist_ok=True)
    safe_sid = "".join(c for c in session_id if c.isalnum() or c in "-_")[:64] or "unknown"
    path = os.path.join(traces_dir, f"trace-{safe_sid}.json")

    first_seen = now_iso()
    try:
        with open(path, encoding="utf-8") as f:
            first_seen = (json.load(f) or {}).get("first_seen", first_seen)
    except (OSError, ValueError):
        pass

    digest = {
        "session_id": session_id,
        "agent": "claude-code",
        "first_seen": first_seen,
        "updated": now_iso(),
        "cwd": payload.get("cwd"),
        "transcript_path": transcript,
        "user_requests": user_requests[-MAX_ITEMS:],
        "tools_used": tools,
        "errors": errors[-MAX_ITEMS:],
        "last_assistant_message": last_assistant,
        "consolidated": False,
    }
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(digest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, path)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # A trace-capture failure must never break the user's session.
        pass
    sys.exit(0)
