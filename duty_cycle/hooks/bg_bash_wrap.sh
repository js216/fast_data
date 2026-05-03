#!/usr/bin/env bash
# PreToolUse(Bash) hook: if run_in_background=true, log a bg_spawn line and
# rewrite the command to append a bg_done marker on subprocess exit.
# No-op for foreground bash.
LOG="$HOME/fast_data/duty_cycle/claude_duty_cycle.log"
INPUT=$(cat)
if [ "$(echo "$INPUT" | jq -r '.tool_input.run_in_background // false')" != "true" ]; then
  exit 0
fi
ORIG=$(echo "$INPUT" | jq -r '.tool_input.command')
SID=$(echo "$INPUT"  | jq -r '.session_id // "?"')
ID=$(uuidgen)
TS=$(date +%s.%N)
printf '%s\tbg_spawn\t%s\tBash\t%s\n' "$TS" "$SID" "$ID" >> "$LOG"
WRAPPED="( $ORIG ); rc=\$?; printf '%s\tbg_done\t%s\tBash\t%s\t%s\n' \"\$(date +%s.%N)\" '$SID' '$ID' \"\$rc\" >> $LOG; exit \$rc"
jq -n --arg cmd "$WRAPPED" '{hookSpecificOutput:{hookEventName:"PreToolUse",updatedInput:{command:$cmd,run_in_background:true}}}'
