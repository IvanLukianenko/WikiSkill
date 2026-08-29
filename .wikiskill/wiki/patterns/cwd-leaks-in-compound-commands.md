# cwd-leaks-in-compound-commands

> Failure pattern: `cd` inside a compound Bash call runs later commands in the wrong directory.

**What happens:** `cd $SCRATCH && <tests> && git add -A && git commit` executed
the git part inside the scratch directory → `fatal: not a git repository`
(exit 128); the commit had to be re-run from the repo root. The harness also
resets cwd between Bash calls, so a `cd` never persists to the next call.

**Root cause:** `cd` affects everything after it within one compound command,
and state does not carry across tool calls — both directions of the assumption
fail.

**Fix (verified):** keep test commands and repo git commands in separate Bash
calls; use absolute paths or `git -C <repo>`; if mixing is unavoidable, isolate
the cd in a subshell: `(cd "$S" && ...) && git -C /repo ...`.

Evidence: Iter 0: session 4d9b89c8-main (exit 128 on commit after scratch-dir tests)
