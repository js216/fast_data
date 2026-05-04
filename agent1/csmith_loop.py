#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# csmith_loop.py --- Generate + verify csmith cctest drafts in batches.
# Copyright (c) 2026 Jakob Kastelic
"""Generate csmith cases until N pass cleanly under cces and sel.

The Orchestrator drives this loop directly:
- Generate one case at a fresh seed via new_csmith.py.
- Run cces + sel on the board against the new draft.
- Classify the result:
    * `clean`        -- gcc == cces == sel; case ready for promotion.
    * `sel_bug`      -- gcc == cces != sel; selache codegen bug exposed.
                        Loop stops so a Worker can be dispatched.
    * `host_diverge` -- gcc != cces; csmith hit undefined behaviour or
                        another non-selache divergence. Discard the
                        case and move on.
- Keep counters and write each clean case path to a manifest so the
  Orchestrator can promote them in bulk later.

The script does *not* edit `xtest/cases/`. Cases live in
`xtest/draft_cases/` until the Orchestrator promotes them. That keeps
the live cctest sweep's input set under explicit human / Orchestrator
control.

Usage:
  python3 csmith_loop.py --target 1000               # add up to 1000 clean
  python3 csmith_loop.py --target 5 --report-every 1
  python3 csmith_loop.py --resume                    # continue last run
"""

import argparse
import os
import pathlib
import re
import subprocess
import sys
import time

REPO = pathlib.Path("/home/agent1/fast_data")
NEW_CSMITH = REPO / "selache/xtest/new_csmith.py"
DRAFT_DIR = REPO / "selache/xtest/draft_cases"
MANIFEST = pathlib.Path("/tmp/csmith_clean_manifest.txt")
LOG = pathlib.Path("/tmp/csmith_loop.log")

# Toolchain env -- the board needs cces-qemu / cces tools on PATH.
ENV = os.environ.copy()
ENV["PATH"] = "/opt/cces-qemu:/opt/analog/cces/3.0.3:" + ENV.get("PATH", "")

# Run a single case through cces + sel, return (cces_got, sel_got)
# or (None, None) if the build failed before reaching the board.
RUN_ONE_TEMPLATE = '''
import sys, pathlib, subprocess, re
sys.path.insert(0, "/home/agent1/fast_data/agent1")
import run
run.CASES_DIR = "{cases_dir}"
run.LEDGER = "/tmp/csmith_loop_ledger.txt"
run.LOG = pathlib.Path("/tmp/csmith_loop_run.log")
def _cj(idx, cmd, oc, nb):
    if not nb: return idx, oc, cmd, "", False
    p = subprocess.run(cmd, shell=True, executable="/bin/bash",
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if p.returncode: raise subprocess.CalledProcessError(p.returncode, cmd, output=p.stdout)
    return idx, oc, cmd, p.stdout or "", True
def sh_nw(cmd):
    p = subprocess.Popen(cmd, shell=True, executable="/bin/bash",
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    for line in p.stdout: sys.stdout.write(line); sys.stdout.flush()
    p.wait()
    if p.returncode: raise subprocess.CalledProcessError(p.returncode, cmd)
run._compile_job = _cj
run.sh = sh_nw
sys.argv = ["run.py", "--cces", "--sel", "{stem}"]
try: run.main()
except SystemExit: pass
'''


def gen_case(seed):
    """Run new_csmith.py at the given seed, return the draft Path."""
    p = subprocess.run(
        ["python3", str(NEW_CSMITH), "--seed", str(seed)],
        capture_output=True, text=True, env=ENV,
    )
    if p.returncode != 0:
        sys.stderr.write(f"new_csmith.py failed for seed {seed}:\n{p.stderr}")
        return None
    # new_csmith prints `wrote <path>  (@expect 0xNN)`; recover the path.
    m = re.search(r"wrote\s+(\S+)\s+\(@expect\s+(0x[0-9a-fA-F]+)\)", p.stdout)
    if not m:
        sys.stderr.write(f"could not parse new_csmith output:\n{p.stdout}")
        return None
    return pathlib.Path(m.group(1)), int(m.group(2), 16)


def run_case(case_path, expect):
    """Run cces + sel on `case_path` against the board.

    Returns (cces_got, sel_got, build_failed_tool). build_failed_tool
    is None on success, otherwise the toolchain name (e.g. "sel" or
    "cces") whose build/link failed before producing a board result.
    """
    stem = case_path.stem.replace("cctest_", "")  # e.g. csmith_00000001
    script = RUN_ONE_TEMPLATE.format(
        cases_dir=str(case_path.parent), stem=stem,
    )
    proc = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, env=ENV,
        timeout=600,
    )
    out = proc.stdout + proc.stderr
    # PASS / FAIL lines look like:
    # [1/1 cces] PASS cctest_csmith_NN expect=0xN got=0xN
    # [1/1 sel ] FAIL cctest_csmith_NN expect=0xN got=0xN n_errors=0
    cces_got = None
    sel_got = None
    build_failed = None
    for line in out.splitlines():
        # Strip ANSI for matching.
        plain = re.sub(r"\033\[[0-9;]*m", "", line)
        m = re.search(r"\[\d+/\d+ (cces|sel) ?\]\s+(PASS|FAIL)\s+\S+\s+expect=0x([0-9a-fA-F]+)\s+got=(\S+)",
                      plain)
        if not m:
            continue
        tool = m.group(1)
        got_str = m.group(4)
        # got could be "0xNN", "BUILD", or "NONE"
        if got_str.startswith("0x"):
            got_val = int(got_str, 16)
        elif got_str == "BUILD":
            build_failed = tool
            got_val = None
        else:
            got_val = None  # NONE = no UART output
        if tool == "cces":
            cces_got = got_val
        else:
            sel_got = got_val
    return cces_got, sel_got, build_failed


def append_log(msg):
    with LOG.open("a") as f:
        f.write(msg + "\n")
    print(msg, flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--target", type=int, default=1000,
                    help="number of clean csmith cases to collect "
                         "(default: 1000)")
    ap.add_argument("--report-every", type=int, default=10,
                    help="status line cadence (default: every 10 cases)")
    ap.add_argument("--resume", action="store_true",
                    help="continue from the existing manifest counter "
                         "instead of starting from 0")
    args = ap.parse_args()

    DRAFT_DIR.mkdir(parents=True, exist_ok=True)

    # Manifest tracks the clean cases we've collected. One absolute
    # path per line. A `# stop: <reason>` line ends the file when the
    # loop halts on a sel bug; the Orchestrator removes that marker
    # after dispatching the Worker that fixes it.
    if args.resume and MANIFEST.exists():
        clean = [p for p in MANIFEST.read_text().splitlines()
                 if p and not p.startswith("#")]
    else:
        clean = []
        MANIFEST.write_text("")
        LOG.write_text("")

    append_log(f"# csmith_loop start, target={args.target}, "
               f"resume={args.resume}, current={len(clean)}")

    examined = 0
    discarded = 0
    while len(clean) < args.target:
        examined += 1
        # Random seed in [1, 2**31). Filter out 0 (csmith default
        # picks its own seed when --seed 0 / unset and the resulting
        # filename would not embed it cleanly).
        seed = int.from_bytes(os.urandom(4), "big") | 1
        gen = gen_case(seed)
        if gen is None:
            discarded += 1
            continue
        case_path, expect = gen
        cces_got, sel_got, build_failed = run_case(case_path, expect)
        # Classify.
        if build_failed:
            append_log(f"DISCARD seed={seed:08x} build_failed={build_failed} "
                       f"path={case_path}")
            case_path.unlink(missing_ok=True)
            discarded += 1
        elif cces_got is None and sel_got is None:
            append_log(f"DISCARD seed={seed:08x} no_uart "
                       f"path={case_path}")
            case_path.unlink(missing_ok=True)
            discarded += 1
        elif cces_got != expect:
            # csmith likely emitted UB; cces and gcc disagree.
            append_log(f"DISCARD seed={seed:08x} host_diverge "
                       f"expect=0x{expect:x} cces=0x{cces_got:x} "
                       f"path={case_path}")
            case_path.unlink(missing_ok=True)
            discarded += 1
        elif sel_got != expect:
            # cces matched host but sel didn't. Real sel bug.
            append_log(f"SEL_BUG seed={seed:08x} expect=0x{expect:x} "
                       f"sel=0x{sel_got:x} path={case_path}")
            with MANIFEST.open("a") as f:
                f.write(f"# stop: sel_bug seed={seed:08x} "
                        f"path={case_path}\n")
            sys.exit(2)
        else:
            # Clean.
            clean.append(str(case_path))
            with MANIFEST.open("a") as f:
                f.write(f"{case_path}\n")
            if len(clean) % args.report_every == 0:
                append_log(f"PROGRESS clean={len(clean)}/{args.target} "
                           f"examined={examined} discarded={discarded}")

    append_log(f"# csmith_loop done, clean={len(clean)} "
               f"examined={examined} discarded={discarded}")


if __name__ == "__main__":
    main()
