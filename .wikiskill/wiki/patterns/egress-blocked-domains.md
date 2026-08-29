# egress-blocked-domains

> Failure pattern: fetching external sites from the remote sandbox fails silently-looking.

**What happens:** `WebFetch` to arbitrary domains returns
`{"error_type":"EGRESS_BLOCKED","domain":"arxiv.org",...}` — observed for
arxiv.org, huggingface.co, academy.dair.ai. `apt-get install` can also 404 on
distro mirrors.

**Root cause:** the remote execution environment routes all HTTPS through an
egress proxy with a network-policy allowlist; most domains and some package
mirrors are simply not on it. Retrying or switching mirrors does not help.

**Fix / workaround (verified):**
1. Use `WebSearch` instead — it goes through an allowed backend and its result
   snippets often carry enough content to work from.
2. For papers/documents: ask the user to upload the file into the session.
3. For tools: prefer `pip install` (pypi.org is allowlisted) over `apt-get`.

Evidence: Iter 0: session 4d9b89c8-main (3 blocked fetches; apt 404; WebSearch + user-uploaded PDF succeeded)
