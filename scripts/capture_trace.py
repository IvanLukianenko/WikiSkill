#!/usr/bin/env python3
"""WikiSkill Stop hook — capture execution traces into the Raw Layer.

Implements the Raw Layer (raw/) of the WikiSkill framework (arXiv:2608.27454
§3.1): immutable execution traces capturing the agent's step-by-step
interactions. For each session this writes:

  raw/traces/trace-<session>.json       compact digest (requests, tools, errors,
                                        outcome, iteration stamp)
  raw/traces/trace-<session>.log.jsonl  copy of the full transcript (capped at
                                        config max_raw_log_bytes), so the Wiki
                                        Maintainer and Skill Proposer can perform
                                        deep root-cause analysis on demand

No-ops (exit 0) when the project has no .wikiskill workspace, so the plugin
stays inert until /wikiskill:init. Existing history is never deleted.
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
        candidate = os.path.join(d, ".wikiskill")
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
    tokens = {"input": 0, "output": 0, "cache_read": 0, "cache_creation": 0}
    # Skill invocations (via the Skill tool) and how many tool errors followed
    # each one — the per-session usefulness signal for `skill-stats`.
    skills_used = {}
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
            usage = msg.get("usage")
            if role == "assistant" and isinstance(usage, dict):
                tokens["input"] += int(usage.get("input_tokens") or 0)
                tokens["output"] += int(usage.get("output_tokens") or 0)
                tokens["cache_read"] += int(usage.get("cache_read_input_tokens") or 0)
                tokens["cache_creation"] += int(usage.get("cache_creation_input_tokens") or 0)
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
                    if name == "Skill":
                        skill = str((item.get("input") or {}).get("skill") or "").strip()
                        if skill:
                            rec_s = skills_used.setdefault(
                                skill, {"invocations": 0, "errors_after": 0})
                            rec_s["invocations"] += 1
                elif kind == "tool_result" and item.get("is_error"):
                    errors.append(clip(text_of(item.get("content"))))
                    for rec_s in skills_used.values():
                        rec_s["errors_after"] += 1
    tokens["total"] = tokens["input"] + tokens["output"]
    return user_requests, errors, tools, last_assistant, tokens, skills_used


def copy_raw_log(transcript, dest, max_bytes):
    """Copy the transcript into the Raw Layer; keep the tail if it exceeds the cap."""
    try:
        size = os.path.getsize(transcript)
        with open(transcript, "rb") as src:
            if size > max_bytes:
                src.seek(size - max_bytes)
                src.readline()  # drop the partial first line
            data = src.read()
        tmp = dest + ".tmp"
        with open(tmp, "wb") as out:
            out.write(data)
        os.replace(tmp, dest)
        return True
    except OSError:
        return False


def main():
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return
    root = find_root(payload.get("cwd"))
    if not root:
        return
    cfg = {}
    try:
        with open(os.path.join(root, "config.json"), encoding="utf-8") as f:
            cfg = json.load(f)
    except (OSError, ValueError):
        pass
    iteration = 0
    try:
        with open(os.path.join(root, "state.json"), encoding="utf-8") as f:
            iteration = int((json.load(f) or {}).get("iteration", 0))
    except (OSError, ValueError):
        pass

    session_id = str(payload.get("session_id") or "unknown")
    transcript = payload.get("transcript_path")

    user_requests, errors, tools, last_assistant = [], [], {}, ""
    tokens = {"input": 0, "output": 0, "cache_read": 0, "cache_creation": 0, "total": 0}
    skills_used = {}
    if transcript and os.path.exists(transcript):
        try:
            (user_requests, errors, tools, last_assistant,
             tokens, skills_used) = parse_transcript(transcript)
        except OSError:
            pass

    tdir = os.path.join(root, "raw", "traces")
    os.makedirs(tdir, exist_ok=True)
    safe_sid = "".join(c for c in session_id if c.isalnum() or c in "-_")[:64] or "unknown"
    path = os.path.join(tdir, f"trace-{safe_sid}.json")
    raw_log = os.path.join(tdir, f"trace-{safe_sid}.log.jsonl")

    first_seen = now_iso()
    prev = {}
    try:
        with open(path, encoding="utf-8") as f:
            prev = json.load(f) or {}
            first_seen = prev.get("first_seen", first_seen)
    except (OSError, ValueError):
        pass

    have_log = False
    if transcript and os.path.exists(transcript):
        have_log = copy_raw_log(transcript, raw_log,
                                int(cfg.get("max_raw_log_bytes", 2000000)))

    digest = {
        "session_id": session_id,
        "agent": "claude-code",
        "iteration": prev.get("iteration", iteration),
        "first_seen": first_seen,
        "updated": now_iso(),
        "cwd": payload.get("cwd"),
        "transcript_path": transcript,
        "raw_log": raw_log if have_log else None,
        "user_requests": user_requests[-MAX_ITEMS:],
        "tokens": tokens,
        "tools_used": tools,
        "skills_used": skills_used,
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
