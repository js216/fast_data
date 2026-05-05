#!/usr/bin/env python3
"""
report.py: read the duty-cycle log and print how busy Claude has been.

Counts every second since the first event, including overnight idle
gaps -- the goal is "agents busy 24/7" so nights show up as idle.

Always validates the log strictly. On any inconsistency (malformed
line, non-monotonic timestamp, unmatched start/stop or pre/post or
spawn/done, duplicate uuid, unknown event), prints a red ERROR: line
to stderr and exits with status 1.
"""
import argparse
import os
import sys
import time
from collections import defaultdict

LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "claude_duty_cycle.log")
WINDOWS = [
    ("last hour",     3600),
    ("last 24h",      86400),
    ("last 7 days",   7 * 86400),
    ("all time",      None),
]


def die(msg):
    if sys.stderr.isatty():
        prefix = "\033[31mERROR:\033[0m"
    else:
        prefix = "ERROR:"
    print(f"{prefix} {msg}", file=sys.stderr)
    sys.exit(1)


def parse(path):
    out = []
    last_ts = None
    with open(path) as f:
        for lineno, line in enumerate(f, 1):
            cols = line.rstrip("\n").split("\t")
            if len(cols) < 4:
                die(f"{path}:{lineno}: malformed line "
                    f"(need >=4 tab-separated fields, got {len(cols)})")
            try:
                ts = float(cols[0])
            except ValueError:
                die(f"{path}:{lineno}: non-numeric timestamp {cols[0]!r}")
            if last_ts is not None and ts < last_ts:
                die(f"{path}:{lineno}: timestamp {ts} goes backward "
                    f"from previous {last_ts}")
            last_ts = ts
            event, sid, detail = cols[1], cols[2], cols[3]
            extra = cols[4:] if len(cols) > 4 else []
            out.append((ts, event, sid, detail, extra))
    return out


def validate(rows):
    """Strict pairing checks; calls die() on any inconsistency.

    Open events at end (start without stop, tool_pre without tool_post,
    bg_spawn without bg_done) are NOT errors -- they represent the
    currently running session, whose closes haven't fired yet.
    """
    # Main and subagent events share session_id (Claude Code reports the
    # parent's session_id for subagent hooks), so key sessions on
    # (session_id, kind) where kind is "main" or "subagent:...".
    open_starts = {}
    open_tools = defaultdict(list)
    open_bg = {}
    for ts, event, sid, detail, extra in rows:
        if event == "start":
            key = (sid, detail)
            if key in open_starts:
                die(f"duplicate start for session {sid} kind={detail} at ts={ts} "
                    f"(previous start at ts={open_starts[key]} never closed)")
            open_starts[key] = ts
        elif event == "stop":
            key = (sid, detail)
            if key not in open_starts:
                die(f"stop for session {sid} kind={detail} at ts={ts} "
                    f"with no matching start")
            del open_starts[key]
        elif event == "tool_pre":
            open_tools[(sid, detail)].append(ts)
        elif event == "tool_post":
            if not open_tools[(sid, detail)]:
                die(f"tool_post {detail!r} for session {sid} at ts={ts} "
                    f"with no matching tool_pre")
            open_tools[(sid, detail)].pop()
        elif event == "bg_spawn":
            uuid = extra[0] if extra else None
            if not uuid:
                die(f"bg_spawn at ts={ts} missing uuid")
            if uuid in open_bg:
                die(f"duplicate bg_spawn uuid {uuid} at ts={ts}")
            open_bg[uuid] = ts
        elif event == "bg_done":
            uuid = extra[0] if extra else None
            if not uuid:
                die(f"bg_done at ts={ts} missing uuid")
            if uuid not in open_bg:
                die(f"bg_done uuid {uuid} at ts={ts} with no matching bg_spawn")
            del open_bg[uuid]
        else:
            die(f"unknown event {event!r} at ts={ts}")


def fmt(s):
    s = max(0, int(s))
    d, s = divmod(s, 86400)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    if d:
        body = f"{d}d{h:02d}h{m:02d}m"
    elif h:
        body = f"{h}h{m:02d}m{s:02d}s"
    elif m:
        body = f"{m}m{s:02d}s"
    else:
        body = f"{s}s"
    return f"{body:>10}"


def aggregate(rows, t_start, t_end):
    """Walk events and produce intervals clipped to [t_start, t_end].

    Assumes rows have already been validated.

    Returns: (main_busy_intervals, command_seconds_in_main)
      main_busy_intervals: list of (start, end) for parent (main) turns
      command_seconds_in_main: tool time inside main sessions only
    """
    open_main = {}        # sid -> ts (main sessions only)
    open_other = {}       # (sid, detail) -> ts (subagents; not counted)
    open_tools = defaultdict(list)
    open_bg = {}
    main_busy = []
    main_command = 0.0

    def clip(a, b):
        a = max(a, t_start)
        b = min(b, t_end)
        return max(0.0, b - a)

    for ts, event, sid, detail, extra in rows:
        if event == "start":
            if detail == "main":
                open_main[sid] = ts
            else:
                open_other[(sid, detail)] = ts
        elif event == "stop":
            if detail == "main":
                if sid in open_main:
                    t0 = open_main.pop(sid)
                    main_busy.append((t0, ts))
            else:
                open_other.pop((sid, detail), None)
        elif event == "tool_pre":
            open_tools[(sid, detail)].append(ts)
        elif event == "tool_post":
            if open_tools[(sid, detail)]:
                t0 = open_tools[(sid, detail)].pop()
                dt = clip(t0, ts)
                if sid in open_main:
                    main_command += dt
        elif event == "bg_spawn":
            open_bg[extra[0]] = (sid, ts, detail)
        elif event == "bg_done":
            bsid, t0, _ = open_bg.pop(extra[0])
            dt = clip(t0, ts)
            if bsid in open_main:
                main_command += dt

    for sid, t0 in open_main.items():
        main_busy.append((t0, t_end))

    clipped = []
    for a, b in main_busy:
        a = max(a, t_start)
        b = min(b, t_end)
        if b > a:
            clipped.append((a, b))
    clipped.sort()
    merged = []
    for a, b in clipped:
        if merged and a <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], b))
        else:
            merged.append((a, b))

    return merged, main_command


# 7-row block letters, 12 cols each. Concatenated they're ~48 cols
# wide for "STOP", ~36 for "RUN" -- both fit under the 58-col table.
GLYPHS = {
    'R': ['##########  ',
          '##      ##  ',
          '##      ##  ',
          '##########  ',
          '## ##       ',
          '##  ##      ',
          '##   ##     '],
    'U': ['##      ##  ',
          '##      ##  ',
          '##      ##  ',
          '##      ##  ',
          '##      ##  ',
          '##      ##  ',
          ' ########   '],
    'N': ['##      ##  ',
          '###     ##  ',
          '####    ##  ',
          '## ##   ##  ',
          '##  ##  ##  ',
          '##   ## ##  ',
          '##    ####  '],
    'S': [' ########   ',
          '##      ##  ',
          '##          ',
          ' ########   ',
          '        ##  ',
          '##      ##  ',
          ' ########   '],
    'T': ['##########  ',
          '    ##      ',
          '    ##      ',
          '    ##      ',
          '    ##      ',
          '    ##      ',
          '    ##      '],
    'O': [' ########   ',
          '##      ##  ',
          '##      ##  ',
          '##      ##  ',
          '##      ##  ',
          '##      ##  ',
          ' ########   '],
    'P': ['##########  ',
          '##      ##  ',
          '##      ##  ',
          '##########  ',
          '##          ',
          '##          ',
          '##          '],
}


def render_word(word):
    """Return a list of 7 strings, one per row, with the glyphs for
    the letters in ``word`` laid out side by side."""
    return [''.join(GLYPHS[c][r] for c in word) for r in range(7)]


def is_active(rows):
    """True iff there's an open `main` session start without a
    matching stop, OR an open `bg_spawn` without a matching `bg_done`.
    Either condition means the agent is doing work right now -- a model
    turn is in progress, or a background bash task it kicked off is
    still running independently of whether the model itself is idle
    between turns. Subagent events don't count -- the parent session
    bracket is the source of truth."""
    open_main = 0
    open_bg = set()
    for _ts, event, _sid, detail, extra in rows:
        if event == "start" and detail == "main":
            open_main += 1
        elif event == "stop" and detail == "main":
            open_main = max(0, open_main - 1)
        elif event == "bg_spawn":
            uuid = extra[0] if extra else None
            if uuid:
                open_bg.add(uuid)
        elif event == "bg_done":
            uuid = extra[0] if extra else None
            if uuid:
                open_bg.discard(uuid)
    return open_main > 0 or len(open_bg) > 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--color", choices=("auto", "always", "never"),
                    default="auto",
                    help="ANSI color in the status line "
                         "(default: auto, ANSI when stdout is a TTY)")
    args = ap.parse_args()

    if args.color == "always":
        use_color = True
    elif args.color == "never":
        use_color = False
    else:
        use_color = sys.stdout.isatty()

    if not os.path.exists(LOG):
        print(f"no log at {LOG}")
        return
    rows = parse(LOG)
    if not rows:
        print("log is empty")
        return
    validate(rows)

    now = time.time()
    first_ts = rows[0][0]

    print(f"{'window':<12}  {'working':>10}  {'command':>10}  {'idle':>10}    {'busy%':>6}")
    print("-" * 58)
    for label, span in WINDOWS:
        t_start = (now - span) if span else first_ts
        t_end = now
        if t_start >= t_end:
            continue
        intervals, command = aggregate(rows, t_start, t_end)
        wall = t_end - t_start
        busy = sum(b - a for a, b in intervals)
        working = max(0.0, busy - command)
        idle = max(0.0, wall - busy)
        pct = (busy / wall * 100) if wall > 0 else 0.0
        print(f"{label:<12}  {fmt(working)}  {fmt(command)}  {fmt(idle)}    {pct:>5.1f}%")

    if is_active(rows):
        word, code = "RUN", "32"   # green
    else:
        word, code = "STOP", "31"  # red
    # `watch` (ncurses) collapses fully-empty lines on some terms;
    # a single space renders as a blank line but isn't dropped.
    print(" ")
    for line in render_word(word):
        if use_color:
            print(f"\033[1;{code}m{line}\033[0m")
        else:
            print(line)


if __name__ == "__main__":
    main()
