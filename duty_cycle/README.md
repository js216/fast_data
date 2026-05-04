# duty_cycle

A small Claude Code harness that asks **"are my agents busy 24/7?"** and
gives an honest answer. Hooks log every turn, every tool call, and every
backgrounded shell; a reporter prints the working / command / idle split
across rolling windows.

## Install

```
$HOME/fast_data/duty_cycle/install.sh
```

Then type `/hooks` in Claude Code once so the watcher reloads.

Prereqs: `jq`, `uuidgen` (`uuid-runtime` on Debian), `python3`, `bash`.
The repo must live under `$HOME` so the install hard-link has a partner
on the same filesystem.

## Read

```
$HOME/fast_data/duty_cycle/duty-cycle.py
```

prints:

```
window               wall       busy    working    command       idle  busy%
--------------------------------------------------------------------------------
last hour         1h00m00s       6m42s       6m41s           1s      53m18s  11.2%
last 24h         24h00m00s    7h12m13s    7h11m02s       1m11s   16h47m47s  30.0%
last 7 days     168h00m00s    7h12m13s    7h11m02s       1m11s  160h47m47s   4.3%
all time         20h28m31s    7h12m13s    7h11m02s       1m11s   13h16m18s  35.2%

tool                          time
------------------------------------
Bash                          5m23s
Edit                          1m02s
Read                            48s
...
```

`busy%` is the fraction of the window during which a session was actively
running (generating tokens or running a tool). Everything else is `idle`
— overnight gaps included, by design.

## What's in this folder

| file | role |
|---|---|
| `claude_settings.json` | the canonical Claude Code settings; the live `~/.claude/settings.json` is a hard link to this file |
| `hooks/bg_bash_wrap.sh` | `PreToolUse` hook that catches `run_in_background=true` bashes and rewrites the command to echo a `bg_done` marker on subprocess exit |
| `duty-cycle.py` | the reporter. no flags, just run it |
| `install.sh` | one-shot installer; idempotent |
| `claude_duty_cycle.log` | the log (gitignored) |

## Log format

Tab-separated, one event per line:
`<unix_ts> <event> <session_id> <detail> [<extra>...]`

| event | detail | extra |
|---|---|---|
| `start` / `stop` | `main` or `subagent:<type>` | — |
| `tool_pre` / `tool_post` | tool name | — |
| `bg_spawn` / `bg_done` | `Bash` | uuid (and exit code on `bg_done`) |

## Caveats

- Claude Code's `Edit` tool writes via atomic-rename, which **breaks hard
  links**. After editing `claude_settings.json`, re-run `install.sh` to
  re-establish the link.
- Backgrounded subprocesses spawned outside the `Bash` tool (none today)
  would be invisible to the wrapper.
- The watcher only auto-reloads settings if `~/.claude/settings.json`
  existed when Claude Code started. First install requires a `/hooks`
  reload (or a restart) before hooks fire.
