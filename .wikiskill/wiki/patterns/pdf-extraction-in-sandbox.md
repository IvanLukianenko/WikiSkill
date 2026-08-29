# pdf-extraction-in-sandbox

> Success pattern: reliable PDF text extraction in the remote sandbox.

**What happens without it:** the Read tool needs `pdftoppm` (poppler) for page
rendering — not installed, and `apt-get install poppler-utils` 404s on the
mirror; a bare `pip install pypdf` then fails at import time with
`ModuleNotFoundError: _cffi_backend` / pyo3 panic from the broken *system*
`cryptography` package.

**Working procedure (verified):**
1. `pip install pypdf` and `pip install --upgrade cffi cryptography` — the
   cryptography upgrade partially fails (debian-owned RECORD) but installing
   `cffi` is enough to make `pypdf` importable.
2. Extract text per page with `pypdf.PdfReader`, writing one `.txt` per page to
   the scratchpad, then read pages in chunks — full papers fit in a few reads.

Evidence: Iter 0: session 4d9b89c8-main (28-page arXiv paper extracted and read in 4 chunks)
