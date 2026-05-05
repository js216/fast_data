#!/bin/sh
# UserPromptSubmit hook. Three jobs in order:
#
#   1. Sweep the log for orphaned `start` events whose Claude PID is
#      gone (terminal closed, claude crashed, SIGKILL) and emit
#      synthetic close events. Without this, every dirty exit leaks an
#      open `start` and the strict reporter trips on it forever.
#
#   2. Self-heal THIS session's previous turn iff its `start` is still
#      open -- happens when the user pressed Esc mid-turn and Claude
#      Code's Stop hook never fires.
#
#   3. Emit a fresh `start main` line stamped with PID + procfs
#      starttime so future sweeps can verify liveness. starttime guards
#      against PID reuse (kill -0 alone would false-positive on a
#      reused PID and leave the orphan in place).
#
# All three steps run inside an exclusive flock on $LOG (fd 9) so
# concurrent Pre/PostToolUse hooks can't interleave between them.
set -eu
DC="$(cd "$(dirname "$0")" && pwd -P)"
LOG="$DC/claude_duty_cycle.log"
sid=$(jq -r '.session_id // "?"')

# $PPID is the process that invoked this hook -- if it dies, no future
# hook can fire for this session, which is exactly what we want to
# detect later. comm (field 2) of /proc/PID/stat is parenthesised and
# can contain spaces or `)`, hence rsplit on the LAST `) `.
my_pid=$PPID
my_stime=$(python3 -c '
import sys
try:
    with open("/proc/" + sys.argv[1] + "/stat") as f:
        line = f.read()
    print(line.rsplit(") ", 1)[1].split()[19])
except Exception:
    print("?")
' "$my_pid" 2>/dev/null) || my_stime="?"
[ -n "$my_stime" ] || my_stime="?"

(
   flock 9
   ts=$(date +%s.%N)

   # 1. Sweep dead orphans. `|| true` so a sweep failure can't abort
   #    the new-start write and break the next stop's pairing.
   python3 "$DC/sweep_dead.py" "$LOG" >&9 || true

   # 2. Self-heal: previous turn for THIS session never closed.
   if [ -s "$LOG" ]; then
      last=$(tac "$LOG" | awk -F'\t' -v sid="$sid" '
         $3==sid && $4=="main" && ($2=="start" || $2=="stop") {
            print $2; exit
         }')
      if [ "$last" = "start" ]; then
         printf '%s\tstop\t%s\tmain\n' "$ts" "$sid" >&9
      fi
   fi

   # 3. New start, with PID + starttime stamped for future sweeps.
   printf '%s\tstart\t%s\tmain\t%s\t%s\n' "$ts" "$sid" "$my_pid" "$my_stime" >&9
) 9>>"$LOG"
