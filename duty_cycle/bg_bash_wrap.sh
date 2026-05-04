#!/bin/sh
# PreToolUse(Bash) hook: if run_in_background=true, log a bg_spawn line and
# rewrite the command to append a bg_done marker on subprocess exit.
# bg_done fires on normal exit, error exit, or catchable signals (INT,
# TERM, HUP). Signals reach the wrapped process promptly because we run
# it in the background and block on `wait`. bg_done cannot fire on
# SIGKILL (uncatchable) or if the wrapper sh is itself crashed.
# No-op for foreground bash.
LOG="$HOME/fast_data/duty_cycle/claude_duty_cycle.log"
INPUT=$(cat)
if [ "$(echo "$INPUT" | jq -r '.tool_input.run_in_background // false')" != "true" ]; then
  exit 0
fi
ORIG=$(echo "$INPUT" | jq -r '.tool_input.command')
SID=$(echo "$INPUT"  | jq -r '.session_id // "?"')
ID=$(uuidgen)
( flock 9; printf '%s\tbg_spawn\t%s\tBash\t%s\n' "$(date +%s.%N)" "$SID" "$ID" >&9 ) 9>>"$LOG"
WRAPPED="log_bg_done() { ( flock 9; printf '%s\tbg_done\t%s\tBash\t%s\t%s\n' \"\$(date +%s.%N)\" '$SID' '$ID' \"\$1\" >&9 ) 9>>$LOG; }
trap 'log_bg_done \$?' EXIT
trap 'kill \"\$_pid\" 2>/dev/null; exit 130' INT
trap 'kill \"\$_pid\" 2>/dev/null; exit 143' TERM
trap 'kill \"\$_pid\" 2>/dev/null; exit 129' HUP
( $ORIG ) &
_pid=\$!
wait \"\$_pid\""
jq -n --arg cmd "$WRAPPED" '{hookSpecificOutput:{hookEventName:"PreToolUse",updatedInput:{command:$cmd,run_in_background:true}}}'
