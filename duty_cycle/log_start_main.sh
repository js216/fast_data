#!/bin/sh
# UserPromptSubmit hook. Emit a "start main" event for this session,
# preceded by a synthetic "stop" iff the previous "main" turn for this
# session never closed -- which happens when the user interrupts mid-turn
# (Esc) and Claude Code's Stop hook never fires. Without this self-heal,
# two starts in a row trip report.py's duplicate-start check.
#
# The flock on $LOG (fd 9) mutually-excludes with log_event.sh's writer,
# so concurrent PreToolUse/PostToolUse hooks can't interleave between
# the synthetic stop and the new start.
set -eu
LOG="$(cd "$(dirname "$0")" && pwd -P)/claude_duty_cycle.log"
sid=$(jq -r '.session_id // "?"')

(
   flock 9
   ts=$(date +%s.%N)
   if [ -s "$LOG" ]; then
      last=$(tac "$LOG" | awk -F'\t' -v sid="$sid" '
         $3==sid && $4=="main" && ($2=="start" || $2=="stop") {
            print $2; exit
         }')
      if [ "$last" = "start" ]; then
         printf '%s\tstop\t%s\tmain\n' "$ts" "$sid" >&9
      fi
   fi
   printf '%s\tstart\t%s\tmain\n' "$ts" "$sid" >&9
) 9>>"$LOG"
