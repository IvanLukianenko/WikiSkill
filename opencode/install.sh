#!/usr/bin/env bash
# Install WikiSkill into a project for opencode.
#
# Usage:  opencode/install.sh [target-project-dir]   (default: current directory)
#
# Copies the wikiskill-* commands, the trace-capture plugin, the CLI, and the
# methodology reference into <target>/.opencode/, then initializes the
# .wikiskill workspace.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="$(cd "${1:-.}" && pwd)"

if ! command -v python3 >/dev/null 2>&1; then
  echo "error: python3 is required" >&2
  exit 1
fi

mkdir -p "$TARGET/.opencode/command" "$TARGET/.opencode/plugin" "$TARGET/.opencode/wikiskill"

cp "$REPO_DIR"/opencode/command/wikiskill-*.md "$TARGET/.opencode/command/"
cp "$REPO_DIR"/opencode/plugin/wikiskill.js "$TARGET/.opencode/plugin/"
cp "$REPO_DIR"/scripts/wikiskill.py "$TARGET/.opencode/wikiskill/wikiskill.py"
cp "$REPO_DIR"/skills/wikiskill-methodology/SKILL.md "$TARGET/.opencode/wikiskill/METHODOLOGY.md"

python3 "$TARGET/.opencode/wikiskill/wikiskill.py" init --dir "$TARGET"

cat <<EOF

WikiSkill installed for opencode in $TARGET
  commands:  /wikiskill-init /wikiskill-status /wikiskill-consolidate
             /wikiskill-evolve /wikiskill-validate /wikiskill-loop /wikiskill-rollback
  plugin:    .opencode/plugin/wikiskill.js (captures traces on session.idle)

Next: add validation tasks to .wikiskill/validation/tasks.md, work normally,
then run /wikiskill-loop periodically.

Tip: opencode also reads Claude-format skills; set "skills_dir" in
.wikiskill/config.json if you keep skills somewhere other than .claude/skills.
EOF
