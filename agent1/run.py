#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# run.py --- Build and run every cctest case on gcc, clang, cces, then sel
# Copyright (c) 2026 Jakob Kastelic

import atexit
import concurrent.futures
import datetime
import glob
import json
import os
import pathlib
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
WORKSPACE_DIR = SCRIPT_DIR.parent
SELACHE_ROOT = pathlib.Path(
    os.environ.get("R", WORKSPACE_DIR / "selache")).resolve()
os.environ["R"] = str(SELACHE_ROOT)

XTEST = "$R/xtest"
CASES = f"{XTEST}/cases"
BUILD = f"{XTEST}/build"
LIBSEL_INC = "$R/libsel/include"
LINK_LDF = "$R/libsel/link.ldf"
SUBMIT_PY = "~/test_serv/submit.py"

# CCES tools (used by the cces toolchain end-to-end).
CC21K = "cc21k"
EASM21K = "easm21k"
ELFLOADER = "elfloader"
ELFAR = "/opt/analog/cces/3.0.3/elfar"

# selache tools (used by the sel toolchain end-to-end). Each one is the
# selache equivalent of a CCES tool: the assembler (selas vs easm21k),
# the linker (seld vs cc21k), the loader-image builder (selload vs
# elfloader), and the archiver (selar vs elfar). Keeping the two
# toolchains fully separate is the point of the sel pipeline -- a sel
# pass means the case ran end-to-end through selache, not a hybrid.
SELCC = "$R/target/release/selcc"
SELAS = "$R/target/release/selas"
SELD = "$R/target/release/seld"
SELLOAD = "$R/target/release/selload"
SELAR = "$R/target/release/selar"

# Per-invocation scratch dir so multiple run.py instances don't clobber
# each other's intermediate .doj/.dxe/.ldr/host_bin/etc. Cleaned up at
# normal exit and on most failure paths via atexit.
OUT = tempfile.mkdtemp(prefix="selache_run_")
atexit.register(lambda: shutil.rmtree(OUT, ignore_errors=True))

CASES_DIR = os.path.expandvars(CASES)
LEDGER = str(SCRIPT_DIR / "ledger.txt")
LOG = SCRIPT_DIR / "log.txt"

CFLAGS = (f"-proc ADSP-21569 -si-revision any -char-size-8 -swc -no-std-inc "
          f"-DBOARD_BAUD_DIV=814U -I{XTEST} -I{LIBSEL_INC}")

LIBSEL_SRC = "$R/libsel/src"
XTEST_HARNESS_C = (f"{XTEST}/uart.c", f"{XTEST}/main.c")

# Toolchains run in order; gcc/clang are local & fast, cces/sel hit the
# shared SHARC+ board. Order matters: a failure in gcc/clang skips the
# remaining (slower) toolchains for that case.
TOOLS = ("gcc", "clang", "cces", "sel")

# Shared-board contention: retry a few times with backoff.
MAX_RETRIES = 4
RETRY_BACKOFF_S = (0, 3, 10, 30)

EXPECT_RE = re.compile(r"/\*\s*@expect\s+(0x[0-9a-fA-F]+|\d+)\s*\*/")

# Host wrapper: provides main() that calls test_main and prints "got NN".
# Written once at startup, linked with each case file under gcc/clang.
HOST_WRAP = """\
#include <stdio.h>
extern int test_main(void);
int main(void) { printf("got %x\\n", test_main()); return 0; }
"""


class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for stream in self.streams:
            stream.write(data)
        return len(data)

    def flush(self):
        for stream in self.streams:
            stream.flush()

    def isatty(self):
        return any(stream.isatty() for stream in self.streams)


def install_log_tee():
    orig_stdout = sys.stdout
    orig_stderr = sys.stderr
    log_fh = open(LOG, "w", buffering=1)
    sys.stdout = Tee(orig_stdout, log_fh)
    sys.stderr = Tee(orig_stderr, log_fh)

    def close_log():
        sys.stdout.flush()
        sys.stderr.flush()
        sys.stdout = orig_stdout
        sys.stderr = orig_stderr
        log_fh.close()

    atexit.register(close_log)
    print(f"log={LOG}", flush=True)


def shell_path(path):
    """Return a command-friendly path under $R when possible.

    Python filesystem checks use expanded absolute paths, but shell
    commands can keep $R so repeated selache-root prefixes do not fill
    the run.py output.
    """
    root = os.environ["R"]
    path = os.path.abspath(path)
    rel = os.path.relpath(path, root)
    if rel == ".":
        return "$R"
    if rel == ".." or rel.startswith(f"..{os.sep}"):
        return path
    return f"$R/{rel}"


def sh(cmd):
    print(f"\033[37m{cmd}\033[0m")
    p = subprocess.Popen(cmd, shell=True, executable="/bin/bash",
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, bufsize=1)
    saw_warning = False
    warning_re = re.compile(r"\bwarning\b", re.IGNORECASE)
    for line in p.stdout:
        sys.stdout.write(line)
        sys.stdout.flush()
        if warning_re.search(line):
            saw_warning = True
    p.wait()
    if p.returncode:
        raise subprocess.CalledProcessError(p.returncode, cmd)
    if saw_warning:
        # Promote any toolchain warning to a hard failure. No silenced
        # diagnostics: every warning must be addressed at root cause.
        raise subprocess.CalledProcessError(1, cmd,
            output="toolchain emitted warning(s)")


def sh_tee(cmd):
    print(f"\033[37m{cmd}\033[0m")
    p = subprocess.Popen(cmd, shell=True, executable="/bin/bash",
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, bufsize=1)
    out = []
    for line in p.stdout:
        sys.stdout.write(line)
        sys.stdout.flush()
        out.append(line)
    p.wait()
    return "".join(out), p.returncode


def _compile_job(idx, cmd, obj_cmd, needs_build):
    if not needs_build:
        return idx, obj_cmd, cmd, "", False

    p = subprocess.run(cmd, shell=True, executable="/bin/bash",
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       text=True)
    out = p.stdout or ""
    saw_warning = re.search(r"\bwarning\b", out, re.IGNORECASE) is not None
    if p.returncode:
        raise subprocess.CalledProcessError(p.returncode, cmd, output=out)
    if saw_warning:
        raise subprocess.CalledProcessError(1, cmd,
            output=out + "\ntoolchain emitted warning(s)\n")
    return idx, obj_cmd, cmd, out, True


def build_target_objs(compiler):
    """Compile every libsel/src/*/*.c, every libsel/src/*/*.s, and the
    xtest harness sources (uart.c, main.c) to per-source .doj files.
    Cached per-source by mtime. Returns the full explicit list of .doj
    path strings.

    `compiler` is "cc21k" or "selcc". cc21k objects live under
    xtest/build/, selcc objects under xtest/build/sel/. selcc-built
    .doj files are produced by `selcc -S` followed by `selas` so the
    full selache C-frontend + assembler pipeline is exercised.
    Hand-written .s files in libsel/src/*/*.s still go through
    easm21k for now: selas's hand-written-asm coverage (fully-spelled
    M-register loads, packed instruction lines, etc.) is not yet
    complete enough to assemble libsel/support/startup.s, and once
    that gap closes the easm21k call site flips to SELAS in one place.

    The caller bundles those objects into a per-run archive so
    individual test link commands stay short."""
    if compiler not in ("cc21k", "selcc"):
        sys.exit(f"unknown compiler: {compiler}")

    src_dir = os.path.expandvars(LIBSEL_SRC)
    obj_root = os.path.expandvars(BUILD)
    obj_dir = obj_root if compiler == "cc21k" else f"{obj_root}/sel"

    c_sources = sorted(glob.glob(f"{src_dir}/*/*.c"))
    s_sources = sorted(glob.glob(f"{src_dir}/*/*.s"))
    if not c_sources:
        sys.exit(f"no libsel sources under {src_dir}")

    os.makedirs(obj_dir, exist_ok=True)
    jobs = []

    def c_compile_cmd(src_cmd, obj_cmd, asm_cmd):
        if compiler == "cc21k":
            return f"{CC21K} {CFLAGS} -c -o {obj_cmd} {src_cmd}"
        return (f"{SELCC} -proc ADSP-21569 -char-size-8 "
                f"-DBOARD_BAUD_DIV=814U -I{XTEST} -I{LIBSEL_INC} "
                f"-S -o {asm_cmd} {src_cmd} && "
                f"{SELAS} -proc ADSP-21569 -o {obj_cmd} {asm_cmd}")

    for src in s_sources:
        sub = os.path.basename(os.path.dirname(src))
        bn = os.path.splitext(os.path.basename(src))[0]
        obj = f"{obj_dir}/lib_{sub}_{bn}.doj"
        obj_cmd = shell_path(obj)
        src_cmd = shell_path(src)
        needs_build = (not os.path.exists(obj)
                       or os.path.getmtime(obj) < os.path.getmtime(src))
        jobs.append((len(jobs),
                     f"{EASM21K} -proc ADSP-21569 -si-revision any "
                     f"-char-size-8 -swc -o {obj_cmd} {src_cmd}",
                     obj_cmd,
                     needs_build))

    for src in c_sources:
        sub = os.path.basename(os.path.dirname(src))
        bn = os.path.splitext(os.path.basename(src))[0]
        obj = f"{obj_dir}/lib_{sub}_{bn}.doj"
        asm = f"{obj_dir}/lib_{sub}_{bn}.s"
        obj_cmd = shell_path(obj)
        asm_cmd = shell_path(asm)
        src_cmd = shell_path(src)
        needs_build = (not os.path.exists(obj)
                       or os.path.getmtime(obj) < os.path.getmtime(src))
        jobs.append((len(jobs),
                     c_compile_cmd(src_cmd, obj_cmd, asm_cmd),
                     obj_cmd,
                     needs_build))

    for src_cmd in XTEST_HARNESS_C:
        src = os.path.expandvars(src_cmd)
        bn = os.path.splitext(os.path.basename(src))[0]
        obj = f"{obj_dir}/xtest_{bn}.doj"
        asm = f"{obj_dir}/xtest_{bn}.s"
        obj_cmd = shell_path(obj)
        asm_cmd = shell_path(asm)
        needs_build = (not os.path.exists(obj)
                       or os.path.getmtime(obj) < os.path.getmtime(src))
        jobs.append((len(jobs),
                     c_compile_cmd(src_cmd, obj_cmd, asm_cmd),
                     obj_cmd,
                     needs_build))

    objs = [None] * len(jobs)
    build_count = sum(1 for *_, needs_build in jobs if needs_build)
    if build_count:
        workers = os.cpu_count() or 1
        print(f"building {build_count} target support objects "
              f"with {workers} workers ({compiler})")
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=workers) as executor:
            futures = [executor.submit(_compile_job, *job) for job in jobs]
            for future in concurrent.futures.as_completed(futures):
                try:
                    idx, obj_cmd, cmd, out, ran = future.result()
                except subprocess.CalledProcessError as e:
                    print(f"\033[37m{e.cmd}\033[0m")
                    if e.output:
                        sys.stdout.write(e.output)
                        sys.stdout.flush()
                    raise
                objs[idx] = obj_cmd
                if ran:
                    print(f"\033[37m{cmd}\033[0m")
                    if out:
                        sys.stdout.write(out)
                        sys.stdout.flush()
    else:
        for idx, _, obj_cmd, _ in jobs:
            objs[idx] = obj_cmd

    return objs


def build_target_archive(target_objs, archiver=ELFAR, suffix=""):
    """Bundle target support objects into one archive for shorter links.
    The cces pipeline uses elfar, the sel pipeline uses selar -- both
    accept `-c <archive> <obj>...` so the call shape is the same."""
    archive = f"{OUT}/libxtest{suffix}.dlb"
    sh(f"{archiver} -c {archive} " + " ".join(target_objs))
    return archive


def load_cases():
    """Each case file under cases/ already contains prelude + helpers +
    one test function named test_main. The case name is derived from the
    filename stem (e.g. cctest_basic_value). Return (path, name, expect,
    text) tuples in sorted order."""
    paths = sorted(glob.glob(f"{CASES_DIR}/*.c"))
    if not paths:
        sys.exit(f"no case files under {CASES_DIR}")
    cases = []
    for p in paths:
        with open(p) as f:
            text = f.read()
        expects = EXPECT_RE.findall(text)
        if len(expects) != 1:
            sys.exit(f"{p}: expected exactly one @expect ({len(expects)})")
        expect = int(expects[0], 0)
        name = os.path.splitext(os.path.basename(p))[0]
        if not name.startswith("cctest_"):
            sys.exit(f"{p}: filename stem {name!r} must start with 'cctest_'")
        cases.append((p, name, expect, text))
    return cases


# Same fixed-delay plan as before.
PLAN_TEMPLATE = (
    "# nonce {nonce}\n"
    "dsp:reset\n"
    "dsp:uart_open\n"
    "dsp:boot ldr=@test.ldr\n"
    "delay ms=2500\n"
    "dsp:uart_close\n"
)


def _parse_artefact(extract):
    manifest_path = f"{extract}/manifest.json"
    uart_path = f"{extract}/streams/dsp.uart.bin"
    try:
        with open(manifest_path) as fh:
            manifest = json.load(fh)
    except FileNotFoundError:
        return "", 1
    try:
        with open(uart_path, "rb") as fh:
            uart = fh.read().decode("ascii", errors="replace")
    except FileNotFoundError:
        uart = ""
    n_errors = int(manifest.get("n_errors", 0))
    m = re.search(r"([0-9a-fA-F]+)", uart)
    if m:
        return f"got {m.group(1)}\n", n_errors
    return uart, n_errors


def _submit_one(ldr_abs, plan_path, extract):
    if os.path.isdir(extract):
        for p in pathlib.Path(extract).rglob("*"):
            if p.is_file():
                p.unlink()
    os.makedirs(extract, exist_ok=True)
    cmd = (f"python3 {SUBMIT_PY} {plan_path} "
           f"--blob test.ldr={ldr_abs} "
           f"--wait 60 --extract {extract}")
    out, _ = sh_tee(cmd)
    m = re.search(r"output stale;.*--fetch\s+([0-9a-f]{64})", out, re.S)
    if m:
        digest = m.group(1)
        sh_tee(f"python3 {SUBMIT_PY} --fetch {digest} --extract {extract}")
    return _parse_artefact(extract)


def submit_and_get(ldr):
    ldr_abs = os.path.expandvars(ldr)
    plan_path = f"{OUT}/plan.txt"
    extract = f"{OUT}/artefact"
    out = ""
    n_errors = 1
    for attempt in range(MAX_RETRIES):
        backoff = RETRY_BACKOFF_S[min(attempt, len(RETRY_BACKOFF_S) - 1)]
        if backoff:
            print(f"\033[33m(retry {attempt}, sleeping {backoff} s for "
                  f"server contention)\033[0m")
            time.sleep(backoff)
        with open(plan_path, "w") as fh:
            fh.write(PLAN_TEMPLATE.format(nonce=time.time_ns()))
        out, n_errors = _submit_one(ldr_abs, plan_path, extract)
        got_hex = re.search(r"got\s+[0-9a-fA-F]+", out)
        if n_errors == 0 and got_hex:
            return out, n_errors
        if n_errors > 0:
            print(f"\033[33m(n_errors={n_errors}; shared-board contention, "
                  f"will retry)\033[0m")
        elif not got_hex:
            print(f"\033[33m(empty UART with n_errors=0; capture race, "
                  f"will retry)\033[0m")
    return out, n_errors


def _build_and_run_host(tool, c_path):
    """Build with host gcc/clang, link with HOST_WRAP, run binary,
    parse 'got NN' from stdout. Returns (out_string, n_errors)."""
    binpath = f"{OUT}/host_bin"
    wrap = f"{OUT}/wrap.c"
    if not os.path.exists(wrap):
        with open(wrap, "w") as f:
            f.write(HOST_WRAP)
    # -m32 matches SHARC+ ABI for sizeof(long), sizeof(void*), SIZE_MAX.
    # -funsigned-char matches SHARC+ default char signedness. gcc-multilib
    # provides the i386 runtime for both gcc and clang.
    sh(f"{tool} -m32 -funsigned-char -std=c99 -w -O0 "
       f"-o {binpath} {c_path} {wrap} -lm")
    out, rc = sh_tee(binpath)
    if rc != 0:
        return out, 1
    return out, 0


def _build_and_run_target(tool, c_path, doj, dxe, ldr, asm, target_objs):
    if tool == "cces":
        # End-to-end CCES: cc21k compiles, cc21k links, elfloader
        # produces the .ldr image.
        sh(f"{CC21K} {CFLAGS} -c -o {doj} {c_path}")
        sh(f"{CC21K} -proc ADSP-21569 -si-revision any -no-mem "
           f"-no-std-lib -T {LINK_LDF} -o {dxe} "
           f"{doj} " + " ".join(target_objs))
        sh(f"{ELFLOADER} -proc ADSP-21569 -b UARTHOST -f ASCII "
           f"-Width 8 {dxe} -o {ldr}")
    else:  # sel
        # selache for the C frontend, archiver, linker, and loader-
        # image step. easm21k still assembles selcc's output: even
        # selas's 48-bit NW encoding for selcc's stack-frame setup
        # (`I7=MODIFY(I7,-N)(NW); DM(-N,I6)=Rx;`) executes
        # differently on real silicon from cc21k/easm21k's choice,
        # so a 2-D-array stack-frame test reads garbage on the
        # first reload. Once selas's MODIFY/UregMemAccess
        # encodings round-trip against the SHARC+ silicon model
        # this swaps to SELAS in one place. seld + selar + selload
        # already drive every other piece of the per-test path.
        sh(f"{SELCC} -proc ADSP-21569 -char-size-8 "
           f"-DBOARD_BAUD_DIV=814U -I{XTEST} -I{LIBSEL_INC} "
           f"-S -o {asm} {c_path}")
        sh(f"{EASM21K} -proc ADSP-21569 -si-revision any "
           f"-o {doj} {asm}")
        sh(f"{SELD} -proc ADSP-21569 -T {LINK_LDF} -o {dxe} "
           f"{doj} " + " ".join(target_objs))
        sh(f"{SELLOAD} -proc ADSP-21569 -b UARTHOST -f ascii "
           f"-Width 8 -o {ldr} {dxe}")
    return submit_and_get(ldr)


def _build_and_run(tool, c_path, doj, dxe, ldr, asm, target_objs):
    if tool in ("gcc", "clang"):
        return _build_and_run_host(tool, c_path)
    return _build_and_run_target(tool, c_path, doj, dxe, ldr, asm, target_objs)


def _cargo_cmd():
    cargo = shutil.which("cargo")
    if cargo:
        return shlex.quote(cargo)
    cargo = os.path.expanduser("~/.cargo/bin/cargo")
    if os.path.isfile(cargo) and os.access(cargo, os.X_OK):
        return shlex.quote(cargo)
    sys.exit("cargo not found; cannot build selache before running sel tests")


def ensure_selache_release_build(tools):
    """Build and check selache before invoking the sel toolchain."""
    if "sel" not in tools:
        return

    root = shlex.quote(str(SELACHE_ROOT))
    cargo = _cargo_cmd()
    try:
        sh(f"cd {root} && {cargo} build --release")
        sh(f"cd {root} && {cargo} test --all-targets")
        sh(f"cd {root} && {cargo} clippy --all-targets --release -- "
           f"-D warnings")
    except subprocess.CalledProcessError as e:
        sys.exit(f"selache preflight failed: {e.cmd}")

    selcc = os.path.expandvars(SELCC)
    if not os.path.isfile(selcc) or not os.access(selcc, os.X_OK):
        sys.exit(f"selcc was not built at {selcc}")


def main():
    install_log_tee()
    print(f"R={os.environ['R']}", flush=True)
    os.makedirs(OUT, exist_ok=True)

    # CLI: optional --gcc/--clang/--cces/--sel flags select & order
    # toolchains; positional args select & order specific case names.
    # Accepts case names as "cctest_foo" or bare "foo". No flags = all
    # toolchains in default order. No positional args = run all cases
    # (default sorted-glob order).
    tool_flags = []
    case_args = []
    for a in sys.argv[1:]:
        if a.startswith("--"):
            t = a[2:]
            if t not in TOOLS:
                sys.exit(f"unknown flag: {a} (must be one of "
                         f"{', '.join('--' + x for x in TOOLS)})")
            if t in tool_flags:
                sys.exit(f"flag {a} given twice")
            tool_flags.append(t)
        else:
            case_args.append(a)
    tools = tuple(tool_flags) if tool_flags else TOOLS
    ensure_selache_release_build(tools)
    cases = load_cases()

    # cces and sel each link their own support archive per test.
    # The cces archive is built by elfar from cc21k objects.
    # The sel archive is currently also built from cc21k objects so
    # the cc21k linker (still used to produce the .dxe) can resolve
    # libsel symbols against them; only the per-test case file goes
    # through selcc + selas, exercising the selache C frontend +
    # assembler. Once cc21k can resolve symbols against selas-built
    # archive members (or seld learns the high-end RESERVE
    # placement), the sel archive flips to a full selas/selar build.
    target_objs_by_tool = {}
    if "cces" in tools or "sel" in tools:
        cc21k_objs = build_target_objs("cc21k")
        if "cces" in tools:
            target_objs_by_tool["cces"] = [
                build_target_archive(cc21k_objs, archiver=ELFAR)]
        if "sel" in tools:
            target_objs_by_tool["sel"] = [
                build_target_archive(cc21k_objs, archiver=SELAR,
                                     suffix="_sel")]

    subset = bool(case_args)
    if subset:
        order = {(a if a.startswith("cctest_") else f"cctest_{a}"): i
                 for i, a in enumerate(case_args)}
        by_name = {c[1]: c for c in cases}
        missing = [n for n in order if n not in by_name]
        if missing:
            sys.exit(f"unknown cases: {missing[:10]}"
                     + (f" (+{len(missing)-10} more)" if len(missing) > 10
                        else ""))
        cases = [by_name[n] for n in sorted(order, key=order.get)]

    results = []
    n = len(cases)
    w = len(str(n))

    for case_idx, (case_path, name, expect, text) in enumerate(cases, 1):
        c_path = f"{OUT}/first.c"
        with open(c_path, "w") as f:
            f.write(text)
            if not text.endswith("\n"):
                f.write("\n")

        doj = f"{OUT}/first.doj"
        dxe = f"{OUT}/first.dxe"
        ldr = f"{OUT}/first.ldr"
        asm = f"{OUT}/first.s"

        for tool in tools:
            build_failed = False
            got = None
            n_errors = 0
            tool_objs = target_objs_by_tool.get(tool, [])
            try:
                out, n_errors = _build_and_run(
                    tool, c_path, doj, dxe, ldr, asm, tool_objs)
                m = re.search(r"got\s+([0-9a-fA-F]+)", out)
                got = int(m.group(1), 16) if m else None
            except subprocess.CalledProcessError as e:
                build_failed = True
                print(f"\033[31mBUILD/LINK FAILED\033[0m for {tool} {name}: "
                      f"exit={e.returncode}")
            ok = (not build_failed) and (got == expect) and (n_errors == 0)
            results.append((name, tool, ok, got, expect))
            tw = max(len(t) for t in tools)
            tag = f"[{case_idx:>{w}}/{n} {tool:<{tw}}]"
            if build_failed:
                g = "BUILD"
            elif got is None:
                g = "NONE"
            else:
                g = f"0x{got:x}"
            err_tag = f" n_errors={n_errors}" if n_errors else ""
            body_txt = f"{name} expect=0x{expect:x} got={g}{err_tag}"
            color = "\033[32mPASS\033[0m" if ok else "\033[31mFAIL\033[0m"
            sep = "\n" if tool == tools[-1] else ""
            print(f"{tag} {color} {body_txt}\n{sep}")
            if not ok:
                summary(results)
                sys.exit(1)

    summary(results)
    sys.exit(0)


def summary(results):
    # A case passes only if every toolchain passes for it.
    by_case = {}
    for name, tool, ok, _, _ in results:
        by_case.setdefault(name, []).append(ok)
    passed = sum(1 for oks in by_case.values() if all(oks))
    failed = sum(1 for oks in by_case.values() if not all(oks))
    total = len(by_case)
    print(f"\nSUMMARY: {passed} passed, {failed} failed, {total} total")
    # Ledger: timestamp and selcc pass count only. Skipped entirely
    # when sel was not exercised in this run, so ad-hoc gcc/clang/cces
    # invocations don't pollute the ledger.
    ran_sel = any(r[1] == "sel" for r in results)
    if not ran_sel:
        return
    ps = sum(1 for r in results if r[1] == "sel" and r[2])
    ts = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    with open(LEDGER, "a") as fh:
        fh.write(f"{ts} {ps}\n")


if __name__ == "__main__":
    main()
