#!/bin/sh
# Append one duty-cycle log line under an exclusive flock so that
# timestamp capture and write are atomic across parallel hooks. Without
# the lock, two hooks racing to read $(date) and append their line can
# emit out-of-order timestamps and break the strict reporter.
#
# Usage: sh log_event.sh '<jq filter that references $ts>' < hook_json
set -eu
LOG="$(cd "$(dirname "$0")" && pwd -P)/claude_duty_cycle.log"
( flock 9; ts=$(date +%s.%N); jq -r --arg ts "$ts" "$1" >&9 ) 9>>"$LOG"
