#!/bin/sh
# SPDX-License-Identifier: MIT
# log_event.sh --- TODO: description
# Copyright (c) 2026 Jakob Kastelic
# Append one duty-cycle log line under an exclusive flock so that
# timestamp capture and write are atomic across parallel hooks. Without
# the lock, two hooks racing to read $(date) and append their line can
# emit out-of-order timestamps and break the strict reporter.
#
# When the resulting line is a `start <sid> main` and the log already
# has an open `start ... main` for the same session that never got a
# matching `stop`, prepend a synthetic `stop` (1 us before the new
# `start`'s timestamp) so the strict reporter stays balanced. Open
# starts happen when the user interrupts a turn before the model
# emits its terminal Stop hook.
#
# Usage: sh log_event.sh '<jq filter that references $ts>' < hook_json
set -eu
LOG="$(cd "$(dirname "$0")" && pwd -P)/claude_duty_cycle.log"
(
  flock 9
  ts=$(date +%s.%N)
  line=$(jq -r --arg ts "$ts" "$1")
  case "$line" in
    *"	start	"*"	main")
      sid=$(printf '%s' "$line" | awk -F'	' '{print $3}')
      open=$(awk -F'	' -v sid="$sid" '
        $3==sid && $4=="main" && $2=="start" { o=1 }
        $3==sid && $4=="main" && $2=="stop"  { o=0 }
        END { print o+0 }
      ' "$LOG" 2>/dev/null || echo 0)
      if [ "$open" = "1" ]; then
        synth=$(awk -v t="$ts" 'BEGIN{printf "%.9f", t - 0.000001}')
        printf '%s	stop	%s	main\n' "$synth" "$sid" >&9
      fi
      ;;
  esac
  printf '%s\n' "$line" >&9
) 9>>"$LOG"
