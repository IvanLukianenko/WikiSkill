# gitignore-before-first-add

> Failure pattern: `git add -A` sweeps generated artifacts into the repo.

**What happens:** running `python3 -m py_compile` created
`scripts/__pycache__/*.pyc`, and a subsequent `git add -A && git commit` pushed
them; a follow-up commit was needed to `git rm -r --cached` and add `.gitignore`.

**Root cause:** test/compile steps generate artifacts, and the repo had no
`.gitignore` yet when `git add -A` ran.

**Fix (verified):** create `.gitignore` (at minimum `__pycache__/`, `*.pyc`,
project state dirs) *before* the first `git add -A`; review `git status --short`
output before every commit rather than trusting `-A`.

Evidence: Iter 0: session 4d9b89c8-main (3 .pyc files committed and removed in a follow-up)
