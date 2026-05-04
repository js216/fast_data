# `duty_cycle`

A small Claude Code harness that asks **"are my agents busy 24/7?"** Hooks log
every turn, every tool call, and every backgrounded shell; a reporter prints the
working / command / idle split across rolling windows.

## Install

Prereqs: `jq`, `uuidgen` (`uuid-runtime` on Debian), `python3`, `sh`, `flock`.
The repo must live under `$HOME` so the install hard-link has a partner
on the same filesystem.

```
sh $HOME/fast_data/duty_cycle/install.sh
```

Then restart Claude Code so the new settings are picked up.

## Read

```
python3 $HOME/fast_data/duty_cycle/report.py
```

prints:

```
window           working     command        idle     busy%
----------------------------------------------------------
last hour          6m41s          1s      53m18s     11.2%
last 24h        7h11m02s       1m11s   16h47m47s     30.0%
last 7 days     7h11m02s       1m11s    6d23h47m      4.3%
all time        7h11m02s       1m11s    6d23h47m     35.2%
```

`busy%` is the fraction of the window during which a session was actively
running (generating tokens or running a tool). Everything else is `idle`
-- overnight gaps included, by design.

## What's in this folder

- `claude_settings.json` -- the canonical Claude Code settings; the live
  `~/.claude/settings.json` is a hard link to this file
- `bg_bash_wrap.sh` -- `PreToolUse` hook that catches
  `run_in_background=true` bashes and rewrites the command to echo a `bg_done`
  marker on subprocess exit
- `report.py` -- the reporter. no flags, just run it
- `install.sh` -- one-shot installer; idempotent
- `claude_duty_cycle.log` -- the log (gitignored)

## Log format

Tab-separated, one event per line:
`<unix_ts> <event> <session_id> <detail> [<extra>...]`

| event                    | detail                      | extra                             |
|--------------------------|-----------------------------|-----------------------------------|
| `start` / `stop`         | `main` or `subagent:<type>` | --                                |
| `tool_pre` / `tool_post` | tool name                   | --                                |
| `bg_spawn` / `bg_done`   | `Bash`                      | uuid (and exit code on `bg_done`) |
