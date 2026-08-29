---
description: Full zero-touch WikiSkill setup — workspace, automation, and a validation suite seeded from the project itself
---

Perform the full WikiSkill setup (arXiv:2608.27454) so the user has nothing
left to do manually:

1. Run `python3 .opencode/wikiskill/wikiskill.py init`, then read
   `.opencode/wikiskill/METHODOLOGY.md`.
2. Ask the user one short question (or default if they don't care):
   automation mode — full auto (recommended) / suggest / manual. Apply it:
   `python3 .wikiskill/bin/wikiskill.py config-set auto_loop '"auto"'`
   (or `'"suggest"'` / `'"off"'`).
3. Seed the validation suite: if `.wikiskill/validation/tasks.md` has no VT-*
   tasks, inspect the project's tooling (package.json scripts, pyproject,
   Makefile, CI configs) and append up to 2 `(auto-seeded at init)` tasks with
   commands you have verified by actually running them, objective success
   criteria, and cleanup. Seed at most 2 so trace harvesting still adds a
   behavioral task before the first baseline. Do NOT run the baseline now —
   the first `/wikiskill-loop` does it.
4. Report a full onboarding in the conversation language: three layers and
   lifecycle rules, one loop iteration with strict R_best gating, what was
   configured, and that from now on everything is automatic (trace capture →
   auto-loop by session count/days → harvest → baseline → evolve). Note that
   `.wikiskill/wiki/`, `validation/` and `state.json` are worth committing;
   `/wikiskill-help` re-shows the guide.

Do not create wiki patterns or skills — those must be earned from real traces.
