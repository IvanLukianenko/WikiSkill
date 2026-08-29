#!/usr/bin/env bash
# Install WikiSkills into a project for opencode.
#
# Usage:  opencode/install.sh [target-project-dir]   (default: current directory)
#
# Copies the wikiskills-* commands, the trace-capture plugin, the CLI, and the
# methodology reference into <target>/.opencode/, then initializes the
# .wikiskills workspace.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="$(cd "${1:-.}" && pwd)"

if ! command -v python3 >/dev/null 2>&1; then
  echo "error: python3 is required" >&2
  exit 1
fi

mkdir -p "$TARGET/.opencode/command" "$TARGET/.opencode/plugin" "$TARGET/.opencode/wikiskills"

cp "$REPO_DIR"/opencode/command/wikiskills-*.md "$TARGET/.opencode/command/"
cp "$REPO_DIR"/opencode/plugin/wikiskills.js "$TARGET/.opencode/plugin/"
cp "$REPO_DIR"/scripts/wikiskills.py "$TARGET/.opencode/wikiskills/wikiskills.py"
cp "$REPO_DIR"/skills/wikiskills-methodology/SKILL.md "$TARGET/.opencode/wikiskills/METHODOLOGY.md"

python3 "$TARGET/.opencode/wikiskills/wikiskills.py" init --dir "$TARGET"

cat <<EOF

WikiSkills installed for opencode in $TARGET
  commands:  /wikiskills-init /wikiskills-status /wikiskills-consolidate
             /wikiskills-evolve /wikiskills-validate /wikiskills-loop /wikiskills-rollback
  plugin:    .opencode/plugin/wikiskills.js (captures traces on session.idle)

Next: add validation tasks to .wikiskills/validation/tasks.md, work normally,
then run /wikiskills-loop periodically.

Tip: opencode also reads Claude-format skills; set "skills_dir" in
.wikiskills/config.json if you keep skills somewhere other than .claude/skills.
EOF
