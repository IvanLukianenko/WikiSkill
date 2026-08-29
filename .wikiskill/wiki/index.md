# Wiki Pattern Index

Concise catalog of known patterns — one line per pattern, in the format:
`- [pattern-name](patterns/pattern-name.md): PROBLEM + ROOT CAUSE + FIX.`

## Patterns

- [egress-blocked-domains](patterns/egress-blocked-domains.md): WebFetch/apt to most external domains fails with EGRESS_BLOCKED because the sandbox proxy enforces an allowlist — use WebSearch, user-uploaded files, or pip (pypi is allowed) instead of retrying.
- [backticks-mangle-commit-messages](patterns/backticks-mangle-commit-messages.md): `git commit -m "..."` silently corrupts messages with backticks/`$` because double-quoted bash interpolates them — write the message to a file with a quoted heredoc and use `git commit -F`.
- [gitignore-before-first-add](patterns/gitignore-before-first-add.md): `git add -A` committed `__pycache__` artifacts because tests ran before any .gitignore existed — create .gitignore first and review `git status --short` before committing.
- [cwd-leaks-in-compound-commands](patterns/cwd-leaks-in-compound-commands.md): git commands after `cd $SCRATCH && tests` failed with "not a git repository" because cd persists within a compound command (but never across tool calls) — separate calls, use absolute paths or `git -C`.
- [plugin-release-hygiene](patterns/plugin-release-hygiene.md): `claude plugin update` no-ops and `.wikiskill/bin` stays stale after merges because updates key on plugin.json's version field — bump the version every release and re-run init to refresh the bin copy.
- [pdf-extraction-in-sandbox](patterns/pdf-extraction-in-sandbox.md): PDFs are unreadable out of the box (no poppler, apt 404s, pypdf import crashes on the broken system cryptography) — `pip install pypdf` + `pip install --upgrade cffi cryptography`, then extract text per page with PdfReader.
