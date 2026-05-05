#!/usr/bin/env python3
"""
Scan claude_duty_cycle.log for `start` events whose Claude PID is dead
(terminal closed, claude crashed, SIGKILL) or whose PID has been reused
since the start was logged, and emit synthetic close events on stdout.

Caller is expected to invoke us under the same flock as the real log
writer and redirect our stdout into the log. We compute everything in
memory and emit in one write at the end so a partial failure cannot
leave a half-written line behind.

Synthetic closes are emitted at the timestamp of the most recent log
event seen so far -- the tightest upper bound on liveness that still
respects the strict reporter's monotonic-timestamp requirement.

Legacy `start` lines without a stamped PID can't be verified and are
deliberately left alone -- we cannot tell them apart from a still-live
session that wrote with old code.
"""
import os
import sys
from collections import defaultdict


def proc_starttime(pid):
    """Return /proc/PID/stat field 22 (process start time in jiffies),
    or None if the PID is gone. comm (field 2) is parenthesised and
    can contain spaces or even `)`, so split on the LAST `) ` to
    recover fields 3+; starttime is then the 20th token."""
    try:
        with open(f"/proc/{pid}/stat") as f:
            line = f.read()
    except OSError:
        return None
    try:
        return line.rsplit(") ", 1)[1].split()[19]
    except (IndexError, ValueError):
        return None


def is_alive(pid_str, starttime_str):
    if not pid_str:
        return True
    try:
        pid = int(pid_str)
    except ValueError:
        return True
    actual = proc_starttime(pid)
    if actual is None:
        return False
    if starttime_str and actual != starttime_str:
        return False
    return True


def compute(log_path):
    if not os.path.exists(log_path) or os.path.getsize(log_path) == 0:
        return []

    open_starts = {}                  # (sid, detail) -> (ts, pid, starttime)
    open_tools = defaultdict(list)    # (sid, detail) -> [ts, ts, ...]
    open_bg = {}                      # uuid -> sid
    last_ts = None

    with open(log_path) as f:
        for line in f:
            cols = line.rstrip("\n").split("\t")
            if len(cols) < 4:
                continue
            ts, event, sid, detail = cols[0], cols[1], cols[2], cols[3]
            extra = cols[4:]
            last_ts = ts
            if event == "start":
                pid = extra[0] if len(extra) > 0 else ""
                stime = extra[1] if len(extra) > 1 else ""
                open_starts[(sid, detail)] = (ts, pid, stime)
            elif event == "stop":
                open_starts.pop((sid, detail), None)
            elif event == "tool_pre":
                open_tools[(sid, detail)].append(ts)
            elif event == "tool_post":
                if open_tools[(sid, detail)]:
                    open_tools[(sid, detail)].pop()
            elif event == "bg_spawn":
                if extra:
                    open_bg[extra[0]] = sid
            elif event == "bg_done":
                if extra:
                    open_bg.pop(extra[0], None)

    if last_ts is None:
        return []

    dead_sids = {
        sid
        for (sid, detail), (_t, pid, stime) in open_starts.items()
        if detail == "main" and not is_alive(pid, stime)
    }
    if not dead_sids:
        return []

    # Order: tool_post / bg_done / subagent stop come BEFORE main stop
    # for each sid, because report.py's aggregate() only credits tool
    # time while the main session is still open.
    out = []
    for sid in sorted(dead_sids):
        for (s, tool), pres in open_tools.items():
            if s != sid:
                continue
            for _ in pres:
                out.append(f"{last_ts}\ttool_post\t{sid}\t{tool}")
        for uuid, s in open_bg.items():
            if s != sid:
                continue
            out.append(f"{last_ts}\tbg_done\t{sid}\tBash\t{uuid}\t?")
        for (s, detail) in open_starts:
            if s != sid or detail == "main":
                continue
            out.append(f"{last_ts}\tstop\t{sid}\t{detail}")
        out.append(f"{last_ts}\tstop\t{sid}\tmain")

    return out


def main():
    try:
        lines = compute(sys.argv[1])
    except Exception:
        return
    if lines:
        sys.stdout.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
