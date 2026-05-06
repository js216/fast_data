#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Jakob Kastelic
"""
codex.py: report Codex busy/idle time from session transcripts.

Busy time is the union of all task_started..task_complete intervals in
~USER/.codex/sessions/**/*.jsonl. Idle time is everything else from the
first timestamp with data through now, split by local calendar day.
"""
import argparse
import json
import os
import sys
from datetime import datetime, time, timedelta
from pathlib import Path
from pwd import getpwnam
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def die(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def user_home(username):
    try:
        return Path(getpwnam(username).pw_dir)
    except KeyError:
        # Keep this useful for mounted homes not present in passwd.
        return Path("/home") / username


def parse_iso_timestamp(value, path, lineno):
    if not isinstance(value, str):
        die(f"{path}:{lineno}: missing string timestamp")
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(value).timestamp()
    except ValueError:
        die(f"{path}:{lineno}: bad timestamp {value!r}")


def session_files(root):
    if not root.exists():
        die(f"session directory does not exist: {root}")
    return sorted(root.glob("**/*.jsonl"))


def local_timezone():
    names = []
    if os.environ.get("TZ"):
        names.append(os.environ["TZ"])

    timezone_file = Path("/etc/timezone")
    if timezone_file.exists():
        names.append(timezone_file.read_text(encoding="utf-8").strip())

    localtime = Path("/etc/localtime")
    if localtime.is_symlink():
        target = localtime.resolve()
        parts = target.parts
        if "zoneinfo" in parts:
            idx = parts.index("zoneinfo")
            names.append("/".join(parts[idx + 1 :]))

    for name in names:
        if not name:
            continue
        try:
            return ZoneInfo(name)
        except ZoneInfoNotFoundError:
            pass

    return datetime.now().astimezone().tzinfo


def read_sessions(root, now_ts):
    first_ts = None
    intervals = []
    newest_path = None
    newest_mtime = None

    files = session_files(root)
    for path in files:
        mtime = path.stat().st_mtime
        if newest_mtime is None or mtime > newest_mtime:
            newest_path = path
            newest_mtime = mtime

    for path in files:
        open_turns = {}
        last_ts = None
        with path.open(encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                line = line.rstrip("\n")
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as e:
                    die(f"{path}:{lineno}: invalid JSON: {e}")

                ts = parse_iso_timestamp(row.get("timestamp"), path, lineno)
                first_ts = ts if first_ts is None else min(first_ts, ts)
                last_ts = ts if last_ts is None else max(last_ts, ts)

                payload = row.get("payload")
                if row.get("type") != "event_msg" or not isinstance(payload, dict):
                    continue

                event = payload.get("type")
                turn_id = payload.get("turn_id")
                if event == "task_started":
                    if not turn_id:
                        die(f"{path}:{lineno}: task_started missing turn_id")
                    open_turns[(path, turn_id)] = ts
                elif event == "task_complete":
                    if not turn_id:
                        die(f"{path}:{lineno}: task_complete missing turn_id")
                    key = (path, turn_id)
                    start = open_turns.pop(key, None)
                    if start is None:
                        duration_ms = payload.get("duration_ms")
                        if not isinstance(duration_ms, (int, float)):
                            die(f"{path}:{lineno}: unmatched task_complete without duration_ms")
                        start = ts - duration_ms / 1000.0
                    if ts >= start:
                        intervals.append((start, ts))

        if last_ts is None:
            continue
        if path == newest_path and newest_mtime is not None and now_ts - newest_mtime < 300:
            end = now_ts
        else:
            end = max(last_ts, path.stat().st_mtime)
        for start in open_turns.values():
            if end >= start:
                intervals.append((start, end))

    if first_ts is None:
        die(f"no transcript data found below {root}")

    return first_ts, merge_intervals(intervals)


def merge_intervals(intervals):
    merged = []
    for start, end in sorted(intervals):
        if end <= start:
            continue
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def add_clipped_seconds(days, intervals, begin_ts, end_ts, local_tz):
    for start, end in intervals:
        start = max(start, begin_ts)
        end = min(end, end_ts)
        if end <= start:
            continue

        cursor = datetime.fromtimestamp(start, local_tz)
        end_dt = datetime.fromtimestamp(end, local_tz)
        while cursor < end_dt:
            day = cursor.date()
            next_midnight = datetime.combine(
                day + timedelta(days=1), time.min, tzinfo=local_tz
            )
            segment_end = min(end_dt, next_midnight)
            days[day] += (segment_end - cursor).total_seconds()
            cursor = segment_end


def fmt_seconds(seconds):
    seconds = max(0.0, seconds)
    whole = int(seconds)
    frac_ms = round((seconds - whole) * 1000)
    if frac_ms == 1000:
        whole += 1
        frac_ms = 0
    hours, rem = divmod(whole, 3600)
    minutes, secs = divmod(rem, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{frac_ms:03d}"


def main():
    parser = argparse.ArgumentParser(
        description="Print daily Codex busy/idle duty cycle from session JSONL logs."
    )
    parser.add_argument(
        "username",
        nargs="?",
        default=os.environ.get("USER"),
        help="user whose ~/.codex/sessions tree should be analyzed (default: $USER)",
    )
    args = parser.parse_args()

    if not args.username:
        die("no username supplied and $USER is unset")

    root = user_home(args.username) / ".codex" / "sessions"
    local_tz = local_timezone()
    now_dt = datetime.now(local_tz)
    now_ts = now_dt.timestamp()

    first_ts, intervals = read_sessions(root, now_ts)
    first_dt = datetime.fromtimestamp(first_ts, local_tz)
    first_day = first_dt.date()
    today = now_dt.date()

    busy_by_day = {}
    day = first_day
    while day <= today:
        busy_by_day[day] = 0.0
        day += timedelta(days=1)

    add_clipped_seconds(busy_by_day, intervals, first_ts, now_ts, local_tz)

    day = first_day
    while day <= today:
        day_start = datetime.combine(day, time.min, tzinfo=local_tz)
        day_end = day_start + timedelta(days=1)
        window_start = max(day_start, first_dt)
        window_end = min(day_end, now_dt)
        total = max(0.0, (window_end - window_start).total_seconds())
        busy = min(busy_by_day[day], total)
        idle = max(0.0, total - busy)
        pct = 0.0 if total == 0 else busy * 100.0 / total
        print(
            f"{day_start.isoformat()} "
            f"{fmt_seconds(busy)} "
            f"{fmt_seconds(idle)} "
            f"{pct:.6f}%"
        )
        day += timedelta(days=1)


if __name__ == "__main__":
    main()
