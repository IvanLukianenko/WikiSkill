# backticks-mangle-commit-messages

> Failure pattern: inline `git commit -m "..."` corrupts messages containing shell-active characters.

**What happens:** a commit message passed via `-m "..."` containing backticks
executed command substitution (`sample: command not found`) and the word was
silently dropped from the pushed message; a later attempt with `§` escapes
landed literally. Both required `--amend` + force-push to repair.

**Root cause:** double-quoted bash strings interpret `` ` ``, `$`, `\` — commit
messages are shell input when passed inline.

**Fix (verified):** write the message to a file and use `git commit -F <file>`
(and `git commit --amend -F <file>` for repairs). Compose the file with a
Write/heredoc-quoted (`<<'EOF'`) mechanism so nothing is interpolated. Check
`git log -1 --format=%B` after committing a non-trivial message.

Evidence: Iter 0: session 4d9b89c8-main (two separate manglings, two amend+force-push repairs)
