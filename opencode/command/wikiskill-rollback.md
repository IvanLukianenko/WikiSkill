---
description: Roll a skill back to a previous snapshot (the wiki is never touched)
---

Target: $ARGUMENTS (skill name, optionally followed by a snapshot timestamp).

1. If no skill name was given, run `python3 .wikiskill/bin/wikiskill.py status`,
   show the skills with snapshots, and ask which to roll back.
2. List snapshots: `python3 .wikiskill/bin/wikiskill.py snapshots <name>`
3. Roll back: `python3 .wikiskill/bin/wikiskill.py rollback <name>` (add
   `--ts <timestamp>` if one was specified).
4. Confirm the result and note that the wiki keeps everything learned — a future
   `/wikiskill-evolve` can attempt a better update from the same knowledge.
