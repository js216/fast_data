#!/usr/bin/env python3
"""
duty-cycle.py: read the duty-cycle log and print how busy Claude has been.

Wall-clock counts every second since the first event, including overnight
idle gaps -- the goal is "agents busy 24/7" so nights show up as idle.
"""
import os
import time
from collections import defaultdict

LOG = os.path.expanduser("~/fast_data/duty_cycle/claude_duty_cycle.log")
WINDOWS = [
    ("last hour",     3600),
    ("last 24h",      86400),
    ("last 7 days",   7 * 86400),
    ("all time",      None),
]


def parse(path):
    out = []
    with open(path) as f:
        for line in f:
            cols = line.rstrip("\n").split("\t")
            if len(cols) < 4:
                continue
            try:
                ts = float(cols[0])
            except ValueError:
                continue
            event, sid, detail = cols[1], cols[2], cols[3]
            extra = cols[4:] if len(cols) > 4 else []
            out.append((ts, event, sid, detail, extra))
    return out


def fmt(s):
    s = max(0, int(s))
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    if h:
        return f"{h:>3d}h{m:02d}m{s:02d}s"
    if m:
        return f"    {m:>2d}m{s:02d}s"
    return f"        {s:>2d}s"


def aggregate(rows, t_start, t_end):
    """Walk events and produce intervals clipped to [t_start, t_end].

    Returns: (main_busy_intervals, command_seconds_in_main, by_tool)
      main_busy_intervals: list of (start, end) for parent (main) turns
      command_seconds_in_main: tool time inside main sessions only
      by_tool: dict tool_name -> seconds (across all sessions, for the table)
    """
    open_starts = {}              # sid -> turn start ts
    session_kind = {}             # sid -> "main" or "subagent:..."
    open_tools = defaultdict(list)
    open_bg = {}
    main_busy = []
    main_command = 0.0
    by_tool = defaultdict(float)

    def clip(a, b):
        a = max(a, t_start)
        b = min(b, t_end)
        return max(0.0, b - a)

    for ts, event, sid, detail, extra in rows:
        if event == "start":
            session_kind[sid] = detail
            open_starts[sid] = ts
        elif event == "stop":
            t0 = open_starts.pop(sid, None)
            if t0 is not None and session_kind.get(sid) == "main":
                main_busy.append((t0, ts))
        elif event == "tool_pre":
            open_tools[(sid, detail)].append(ts)
        elif event == "tool_post":
            stack = open_tools[(sid, detail)]
            if stack:
                t0 = stack.pop()
                dt = clip(t0, ts)
                by_tool[detail] += dt
                if session_kind.get(sid) == "main":
                    main_command += dt
        elif event == "bg_spawn":
            uuid = extra[0] if extra else None
            if uuid:
                open_bg[uuid] = (sid, ts, detail)
        elif event == "bg_done":
            uuid = extra[0] if extra else None
            if uuid and uuid in open_bg:
                bsid, t0, tool = open_bg.pop(uuid)
                dt = clip(t0, ts)
                by_tool[tool + "(bg)"] += dt
                if session_kind.get(bsid) == "main":
                    main_command += dt

    # Carry forward open turns whose stop hasn't fired yet (current session).
    for sid, t0 in open_starts.items():
        if session_kind.get(sid) == "main":
            main_busy.append((t0, t_end))

    # Clip & merge overlapping main intervals.
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

    return merged, main_command, by_tool


def main():
    if not os.path.exists(LOG):
        print(f"no log at {LOG}")
        return
    rows = parse(LOG)
    if not rows:
        print("log is empty")
        return

    now = time.time()
    first_ts = rows[0][0]

    print(f"{'window':<14}  {'wall':>9}  {'busy':>9}  {'working':>9}  {'command':>9}  {'idle':>9}  busy%")
    print("-" * 80)
    for label, span in WINDOWS:
        t_start = (now - span) if span else first_ts
        t_end = now
        if t_start >= t_end:
            continue
        intervals, command, _ = aggregate(rows, t_start, t_end)
        wall = t_end - t_start
        busy = sum(b - a for a, b in intervals)
        working = max(0.0, busy - command)
        idle = max(0.0, wall - busy)
        pct = (busy / wall * 100) if wall > 0 else 0.0
        print(f"{label:<14}  {fmt(wall)}  {fmt(busy)}  {fmt(working)}  "
              f"{fmt(command)}  {fmt(idle)}  {pct:>4.1f}%")

    # Per-tool breakdown (all-time)
    _, _, by_tool = aggregate(rows, first_ts, now)
    if by_tool:
        print()
        print(f"{'tool':<24}  {'time':>9}")
        print("-" * 36)
        for tool, dt in sorted(by_tool.items(), key=lambda kv: -kv[1])[:10]:
            print(f"{tool:<24}  {fmt(dt)}")


if __name__ == "__main__":
    main()
