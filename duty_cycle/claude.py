#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Jakob Kastelic
"""
claude.py: report Claude Code busy/idle time from session transcripts.

Busy time is the union of foreground turns, tool calls, subagent turns,
and background Bash output lifetimes found under
~USER/.claude/projects/**/*.jsonl. Idle time is everything else from the
first timestamp with data through now, split by local calendar day.
"""
import argparse
import json
import os
import re
import sys
from datetime import datetime, time, timedelta
from pathlib import Path
from pwd import getpwnam
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


BACKGROUND_RE = re.compile(r"Output is being written to:\s+(\S+)")


def die(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def user_home(username):
    try:
        return Path(getpwnam(username).pw_dir)
    except KeyError:
        return Path("/home") / username


def parse_iso_timestamp(value, path, lineno):
    if not isinstance(value, str):
        return None
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(value).timestamp()
    except ValueError:
        die(f"{path}:{lineno}: bad timestamp {value!r}")


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


def session_files(root):
    if not root.exists():
        die(f"session directory does not exist: {root}")
    return sorted(root.glob("**/*.jsonl"))


def message_content(row):
    message = row.get("message")
    if not isinstance(message, dict):
        return None
    return message.get("content")


def content_items(row):
    content = message_content(row)
    if isinstance(content, list):
        return [item for item in content if isinstance(item, dict)]
    if isinstance(content, dict):
        return [content]
    return []


def tool_result_text(item):
    content = item.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(str(part) for part in content)
    return ""


def background_output_path(item):
    match = BACKGROUND_RE.search(tool_result_text(item))
    if not match:
        return None
    return Path(match.group(1))


def read_sessions(root, now_ts):
    first_ts = None
    intervals = []
    open_tools = {}
    newest_path = None
    newest_mtime = None

    files = session_files(root)
    for path in files:
        mtime = path.stat().st_mtime
        if newest_mtime is None or mtime > newest_mtime:
            newest_path = path
            newest_mtime = mtime

    for path in files:
        last_ts = None
        try:
            f = path.open(encoding="utf-8")
        except PermissionError:
            die(
                f"cannot read {path}; fix ACLs with: "
                f"setfacl -R -m u:{os.environ.get('USER', '<reader>')}:rwX,m::rwx "
                f"{root.parent}"
            )
        with f:
            for lineno, line in enumerate(f, 1):
                line = line.rstrip("\n")
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as e:
                    die(f"{path}:{lineno}: invalid JSON: {e}")

                ts = parse_iso_timestamp(row.get("timestamp"), path, lineno)
                if ts is None:
                    snapshot = row.get("snapshot")
                    if isinstance(snapshot, dict):
                        ts = parse_iso_timestamp(snapshot.get("timestamp"), path, lineno)
                if ts is None:
                    continue

                first_ts = ts if first_ts is None else min(first_ts, ts)
                last_ts = ts if last_ts is None else max(last_ts, ts)

                if row.get("type") == "system" and row.get("subtype") == "turn_duration":
                    duration_ms = row.get("durationMs")
                    if isinstance(duration_ms, (int, float)) and duration_ms >= 0:
                        intervals.append((ts - duration_ms / 1000.0, ts))

                for item in content_items(row):
                    item_type = item.get("type")
                    if item_type == "tool_use":
                        tool_id = item.get("id")
                        if not tool_id:
                            continue
                        input_data = item.get("input")
                        if not isinstance(input_data, dict):
                            input_data = {}
                        open_tools[tool_id] = {
                            "start": ts,
                            "name": item.get("name"),
                            "input": input_data,
                        }
                    elif item_type == "tool_result":
                        tool_id = item.get("tool_use_id")
                        if not tool_id:
                            continue
                        tool = open_tools.pop(tool_id, None)
                        if tool is None:
                            continue

                        end = ts
                        if tool["name"] == "Bash" and tool["input"].get("run_in_background"):
                            out_path = background_output_path(item)
                            if out_path is not None:
                                try:
                                    out_stat = out_path.stat()
                                except (FileNotFoundError, PermissionError):
                                    out_stat = None
                                if out_stat is not None:
                                    end = max(end, out_stat.st_mtime)

                        if end >= tool["start"]:
                            intervals.append((tool["start"], end))

        if path == newest_path and newest_mtime is not None and now_ts - newest_mtime < 300:
            close_ts = now_ts
        elif last_ts is not None:
            close_ts = max(last_ts, path.stat().st_mtime)
        else:
            continue

        # A live or interrupted tool is still busy until the transcript's
        # last activity; for the currently written transcript, until now.
        for tool_id, tool in list(open_tools.items()):
            if close_ts >= tool["start"]:
                intervals.append((tool["start"], close_ts))
                open_tools.pop(tool_id, None)

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
        description="Print daily Claude Code busy/idle duty cycle from JSONL logs."
    )
    parser.add_argument(
        "username",
        nargs="?",
        default=os.environ.get("USER"),
        help="user whose ~/.claude/projects tree should be analyzed (default: $USER)",
    )
    args = parser.parse_args()

    if not args.username:
        die("no username supplied and $USER is unset")

    root = user_home(args.username) / ".claude" / "projects"
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
