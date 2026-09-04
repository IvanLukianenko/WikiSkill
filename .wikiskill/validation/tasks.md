# WikiSkill Validation Tasks (D_val)

This suite plays the role of the validation split in the WikiSkill framework
(arXiv:2608.27454): each candidate skill update is accepted only if the pass
rate on these tasks strictly exceeds the best score achieved so far (R_best).
Add tasks that represent the work this project's skills should make easier.

Format — one task per section:

## VT-<n>: <short name>
- **Prompt:** <what to ask the agent to do, self-contained>
- **Success criteria:** <objectively checkable outcome, e.g. "tests in X pass", "output contains Y", "file Z compiles">
- **Cleanup:** <how to undo any side effects, or "none">

_Add your first task above. With no tasks defined, /wikiskill:validate
falls back to a self-review of the skill diff instead of hard gating._

## VT-1: CLI gating lifecycle (auto-generated from session 4d9b89c8-main)
- **Prompt:** In a fresh scratch directory, run the WikiSkill CLI end-to-end: `init`; capture one failing and one passing fake trace via `scripts/capture_trace.py` (stdin payloads with a transcript containing / not containing a tool error); `sample` must stratify them as 1 failing + 1 passing; `record-validation --baseline --passed 1 --total 2`; `snapshot demo`; create `.claude/skills/demo/SKILL.md`; `record-validation --skill demo --passed 2 --total 2` must print ACCEPTED; `snapshot demo` again, append a line to the skill, `record-validation --skill demo --passed 2 --total 2` must print REJECTED (tie); `rollback demo` must restore the file without the appended line.
- **Success criteria:** every command exits 0 (rollback path included); output contains the exact verdict words BASELINE, ACCEPTED, REJECTED; after rollback the appended line is gone; `.wikiskill/wiki/skill-impact.md` in the scratch workspace contains a ```diff block.
- **Cleanup:** remove the scratch directory.

## VT-2: repo syntax gate (auto-generated from session 4d9b89c8-main)
- **Prompt:** From the repo root run `python3 -m py_compile scripts/*.py`, `node --check opencode/plugin/wikiskill.js`, and parse `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `hooks/hooks.json` with `json.load`.
- **Success criteria:** all commands exit 0.
- **Cleanup:** delete `scripts/__pycache__/`.

## VT-3: hook no-op safety outside a workspace (auto-generated from session 4d9b89c8-main)
- **Prompt:** Create an empty scratch directory with no `.wikiskill`. Pipe `{"cwd":"<that dir>"}` into `scripts/capture_trace.py` and into `scripts/session_start.py`.
- **Success criteria:** both exit 0; capture_trace prints nothing and creates no files in the directory; session_start prints nothing (no JSON) since the project is uninitialized.
- **Cleanup:** remove the scratch directory.
