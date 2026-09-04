---
description: Skill usage & usefulness report — which evolved skills get used, which help, which are suspect or unused
argument-hint: [--all]
allowed-tools: Bash(python3:*), Read
---

## Context

- Report: !`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/wikiskill.py" skill-stats $ARGUMENTS`

## Your task

Present the report above as a short table (skill · invocations · sessions · errors-after-use rate · verdict), then interpret it for the user:

- **HELPFUL** skills — used repeatedly with clean sessions afterwards; leave them alone unless the wiki says otherwise.
- **SUSPECT** skills — errors keep following their use; recommend `/wikiskill:evolve <skill>` so the Skill Proposer patches them with trace evidence.
- **UNUSED** skills — never invoked across the traced sessions; either their `description` doesn't match real requests (recommend a description-sharpening patch via `/wikiskill:evolve <skill>`) or the capability isn't needed (recommend retiring it by hand — the framework never deletes skills on its own).
- Note the data source and caveats: invocations come from the PostToolUse(Skill) hook, outcome signals from per-session traces, so a skill used in a session that is still open has no outcome yet, and "errors after use" is correlation, not proof — the Wiki Maintainer's trace analysis decides.

If nothing is recorded yet, say that every skill invocation is logged from now on and the report fills in as sessions are traced.
