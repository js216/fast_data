#!/usr/bin/env bash
# Install duty-cycle measurement on this user account.
#
# Prerequisites: jq, uuidgen (uuid-runtime on Debian), python3, bash.
# Assumes this repo is checked out at $HOME/fast_data and you're running
# as the user that will run Claude Code.
#
# Re-running is idempotent.

set -euo pipefail

DC="$HOME/fast_data/duty_cycle"
CLAUDE_DIR="$HOME/.claude"
LIVE="$CLAUDE_DIR/settings.json"
CANON="$DC/claude_settings.json"

for cmd in jq uuidgen python3 bash; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "missing: $cmd" >&2; exit 1; }
done

[ -d "$DC" ] || { echo "expected $DC to exist (this dir contains the canonical files)" >&2; exit 1; }
[ -f "$CANON" ] || { echo "missing $CANON" >&2; exit 1; }

mkdir -p "$CLAUDE_DIR"
chmod +x "$DC/hooks/bg_bash_wrap.sh" "$DC/duty-cycle.py"

# If the live settings is already a hard link to the canonical, we're done.
if [ -e "$LIVE" ]; then
  if [ "$(stat -c %i "$LIVE")" = "$(stat -c %i "$CANON")" ]; then
    echo "already installed (settings.json is hard-linked to $CANON)"
    exit 0
  fi
  BACKUP="$LIVE.preinstall-$(date +%Y%m%dT%H%M%S)"
  echo "existing $LIVE found; backing up to $BACKUP"
  mv "$LIVE" "$BACKUP"
fi

# Hard link must succeed -- $HOME and $DC must be on the same filesystem.
if ! ln "$CANON" "$LIVE" 2>/dev/null; then
  echo "hard link failed -- $HOME and $DC are on different filesystems." >&2
  echo "place fast_data inside \$HOME, or change to a symlink (loses single-inode guarantee)." >&2
  exit 1
fi

echo "installed: $LIVE -> $CANON (inode $(stat -c %i "$LIVE"))"
echo
echo "Next: open Claude Code and type /hooks once so the watcher picks up"
echo "the new settings. After that, the log lives at"
echo "  $DC/claude_duty_cycle.log"
echo "and you can read the breakdown with"
echo "  $DC/duty-cycle.py"
