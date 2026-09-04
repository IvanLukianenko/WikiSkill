---
description: Skill usage & usefulness report — which evolved skills get used, which help, which are suspect or unused
---

Run `python3 .wikiskill/bin/wikiskill.py skill-stats` (add `--all` to include
non-evolved skills) and present it as a short table (skill · invocations ·
sessions · errors-after-use rate · verdict). Interpret: HELPFUL → leave alone;
SUSPECT (errors keep following its use) → recommend `/wikiskill-evolve <skill>`
for a trace-grounded patch; UNUSED → recommend a description-sharpening patch
or manual retirement (the framework never deletes skills itself). Note the
caveats: invocations come from the plugin's tool hook, outcomes from session
traces; "errors after use" is correlation the Wiki Maintainer's trace analysis
must confirm.
