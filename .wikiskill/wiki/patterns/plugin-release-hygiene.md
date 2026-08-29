# plugin-release-hygiene

> Failure pattern: shipped plugin changes don't reach installed copies.

**What happens:** after merging feature PRs, `claude plugin update wikiskill`
reported "already at the latest version (0.1.0)" and kept the old code; the
project-local `.wikiskill/bin/wikiskill.py` (copied at init time from the
installed plugin) was likewise stale and missing new subcommands.

**Root cause:** plugin updates are driven by the `version` field in
`.claude-plugin/plugin.json` — merging code without bumping it makes updates
no-ops; the bin copy is frozen at whatever version ran `init`.

**Fix (verified):** bump `version` in plugin.json in every release-worthy PR;
after updating the plugin (or when developing in this repo), refresh the local
CLI with `python3 scripts/wikiskill.py init` (repo checkout) or
re-run `/wikiskill:init` (reinstalled plugin).

Evidence: Iter 0: session 4d9b89c8-main (update no-op at 0.1.0; stale bin lacked loop-due/auto-loop)
