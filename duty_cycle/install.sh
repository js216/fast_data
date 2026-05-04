#!/bin/sh
# Install duty-cycle measurement on this user account.
#
# Prerequisites: jq, uuidgen (uuid-runtime on Debian), python3, sh.
# Assumes this repo is checked out at $HOME/fast_data and you're running
# as the user that will run Claude Code.
#
# Re-running is idempotent. If an existing ~/.claude/settings.json is
# found, prompts for confirmation before replacing it (requires a TTY).

set -eu

DC="$HOME/fast_data/duty_cycle"
CLAUDE_DIR="$HOME/.claude"
LIVE="$CLAUDE_DIR/settings.json"
CANON="$DC/claude_settings.json"

# ---- prereq checks (no side effects past this block) ----

for cmd in jq uuidgen python3 sh; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "missing: $cmd" >&2; exit 1; }
done

[ -d "$DC" ] || { echo "expected $DC to exist (this dir contains the canonical files)" >&2; exit 1; }
[ -f "$CANON" ] || { echo "missing $CANON" >&2; exit 1; }

# Hard link requires $HOME and $DC on the same filesystem.
HOME_DEV=$(stat -c %d "$HOME")
DC_DEV=$(stat -c %d "$DC")
if [ "$HOME_DEV" != "$DC_DEV" ]; then
  echo "\$HOME and $DC are on different filesystems -- hard link impossible." >&2
  echo "place fast_data inside \$HOME, or change to a symlink (loses single-inode guarantee)." >&2
  exit 1
fi

# Need write access to $CLAUDE_DIR (or its parent, if it doesn't exist yet).
if [ -e "$CLAUDE_DIR" ]; then
  [ -w "$CLAUDE_DIR" ] || { echo "no write access to $CLAUDE_DIR" >&2; exit 1; }
else
  [ -w "$(dirname "$CLAUDE_DIR")" ] || { echo "no write access to $(dirname "$CLAUDE_DIR")" >&2; exit 1; }
fi

# Already installed? Bail before touching anything.
if [ -e "$LIVE" ] && [ "$(stat -c %i "$LIVE")" = "$(stat -c %i "$CANON")" ]; then
  echo "already installed (settings.json is hard-linked to $CANON)"
  exit 0
fi

# Confirm before replacing an existing settings.json.
if [ -e "$LIVE" ]; then
  if [ ! -t 0 ]; then
    echo "existing $LIVE present and stdin is not a TTY; refusing to overwrite" >&2
    exit 1
  fi
  printf 'existing %s will be moved to a timestamped backup and replaced. proceed? [y/N] ' "$LIVE" >&2
  read -r ANS
  case "$ANS" in
    y|Y|yes|YES) ;;
    *) echo "aborted." >&2; exit 1 ;;
  esac
fi

# ---- changes start here ----

mkdir -p "$CLAUDE_DIR"

if [ -e "$LIVE" ]; then
  BACKUP="$LIVE.preinstall-$(date +%Y%m%dT%H%M%S)"
  echo "existing $LIVE found; backing up to $BACKUP"
  mv "$LIVE" "$BACKUP"
fi

ln "$CANON" "$LIVE"

echo "installed: $LIVE -> $CANON (inode $(stat -c %i "$LIVE"))"
echo
echo "Next: restart Claude Code so the new settings are picked up."
echo "After that, the log lives at"
echo "  $DC/claude_duty_cycle.log"
echo "and you can read the breakdown with"
echo "  python3 $DC/report.py"
