#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# run.py --- TODO: description
# Copyright (c) 2026 Jakob Kastelic
"""Walk a regression-plan .md file, run Build -> Test -> Verify per
section, print a PASS/FAIL line for each.

Usage: python3 run.py ssh.md
"""
import argparse
import csv
import datetime
import getpass
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path


class HardFail(Exception):
    """Raised inside a verify `check()` to signal a deterministic FAIL
    that must NOT be retried. `_submit_with_retries` catches it and
    fails the section immediately instead of burning the transient-error
    backoff sequence. Use for verdicts that re-running cannot change
    (e.g. the DSP is in a fault state)."""


class Verification:
    """Read-only namespace of helpers consumed by inline
    `check(extract_dir)` blocks in plan .md files. The Runner
    pre-injects this class plus an `artifacts` dict (basename ->
    absolute path) into the verify block's namespace, so .md blocks
    can call e.g. `Verification.manifest_clean(extract_dir)` and
    `Path(artifacts['sdcard.img']).read_bytes()` without imports.
    `extract_dir` is the directory passed to `submit.py --extract`
    (the unpacked artefact tarball: manifest.json, ops.jsonl,
    streams/...)."""

    def load_manifest(extract_dir):
        return json.loads(Path(extract_dir, 'manifest.json').read_text())

    def manifest_clean(extract_dir):
        """True iff the plan completed with zero op-level errors."""
        return Verification.load_manifest(extract_dir).get('n_errors', 1) == 0

    def load_devices(extract_dir):
        """Parse the bench.devices.json artefact (list of device dicts)."""
        return json.loads(
            Path(extract_dir, 'bench.devices.json').read_bytes())

    def load_ops(extract_dir):
        """Parse ops.jsonl (one JSON record per executed op)."""
        return [json.loads(l) for l in
                Path(extract_dir, 'ops.jsonl').read_text().splitlines()
                if l.strip()]

    def load_stream(extract_dir, stream_name):
        """Raw bytes of streams/<stream_name>.bin (e.g. 'msc.read')."""
        return Path(extract_dir, f'streams/{stream_name}.bin').read_bytes()

    def load_stream_text(extract_dir, stream_name, encoding='ascii'):
        """Decoded text of streams/<stream_name>.bin (errors='replace')."""
        return Verification.load_stream(extract_dir, stream_name).decode(
            encoding, 'replace')

    def scope_columns(extract_dir):
        """Parse streams/scope.csv into {channel: [float, ...]} keyed by
        CSV header, so a verify block can read a captured trace by
        channel name without caring about column order. Returns {} when
        the trace has no rows."""
        rows = list(csv.reader(
            Verification.load_stream_text(
                extract_dir, 'scope.csv').splitlines()))
        if not rows:
            return {}
        header = rows[0]
        cols = {name: [] for name in header}
        for r in rows[1:]:
            for i, name in enumerate(header):
                if i < len(r):
                    try:
                        cols[name].append(float(r[i]))
                    except ValueError:
                        pass
        return cols

    def dsp_fault_gate(extract_dir, chan='C2', active_below=150.0):
        """Gate every DSP test on the fault line before trusting any
        later check. The DSP fault LED (scope C2 = DSP_FAULT, see
        config.json scope.signals) idles above `active_below` on a
        healthy board and is pinned low when faulted. A fault is a
        deterministic verdict, so this prints 'DSP FAULT' in red and
        raises HardFail -- run.py then fails the section immediately
        instead of burning the transient-retry backoff. No-op if the
        channel wasn't captured."""
        col = Verification.scope_columns(extract_dir).get(chan, [])
        if col and sum(col) / len(col) < active_below:
            sys.stderr.write('\033[1;31mDSP FAULT\033[0m\n')
            raise HardFail('DSP FAULT')

    def uart_golden(extract_dir, expected, stream='mp135.uart'):
        if not Verification.manifest_clean(extract_dir):
            return False
        actual = Verification.load_stream_text(extract_dir, stream, 'utf-8')
        return expected.replace('\n', '\r\n') in actual

    def op_succeeded(ops, device, verb):
        """True iff `device:verb` appears in `ops` with status='ok'."""
        return any(o.get('device') == device and o.get('verb') == verb
                   and o.get('status') == 'ok' for o in ops)


class Runner:
    """Parses a regression-plan .md file and drives Build (shell
    commands), Test (submit a plan via test_serv), and Verify (exec
    the inline check) for each `### ` section. Cross-section lease
    plumbing: any `{{LEASE_TOKEN}}` placeholder in a section's plan is
    substituted with the token produced by the most recent prior
    section that ran `lease:claim`; sections that want device hold
    across submissions must spell out `lease:claim` / `lease:resume` /
    `lease:release` in the mission file."""

    FAST_DATA = Path(__file__).resolve().parent
    SUBMIT_PY = FAST_DATA / 'test_serv' / 'submit.py'
    SERVER = 'http://localhost:8080'
    WAIT_S = 1200                    # generous shared-bench upper bound
    RUNTIME_GRACE_S = 60             # agent watchdog/upload slack
    INFLIGHT_FALLBACK_S = 60         # bound missing/stale /inflight data
    BUSY_RETRY_DEADLINE_S = WAIT_S   # bound zero-op lease/busy retries
    LONG_BUSY_RETRY_DEADLINE_S = 3600
    FAILED_ATTEMPT_LEASE_RELEASE_WAIT_S = 300
    LONG_BUSY_RETRY_MISSIONS = {'nand-flash.md'}
    LEASE_PLACEHOLDER = '{{LEASE_TOKEN}}'
    # Directory holding the per-invocation workdir and lease-state
    # file. Each run.py creates a unique subdir under here keyed by
    # PID + nanosecond timestamp so two run.py invocations can drive
    # disjoint missions concurrently (e.g., ssh.md on EVB and
    # ssh-custom.md on the custom board) without clobbering each
    # other's `.workdir` or known_hosts lease state.
    WORKDIR_PARENT = FAST_DATA / 'tmp'
    # Bounded retries with backoff for transient bench failures
    # (USB device dropouts, busy queues, FT4222 not-found). The
    # retry sequence is the wait BEFORE the i-th attempt; the first
    # attempt has no wait. Total worst-case extra wait per FAIL is
    # the sum of the non-zero entries.
    RETRY_BACKOFF_S = (0, 30, 90, 300, 900)
    NO_HARDWARE_TEST = '__NO_HARDWARE__'

    def __init__(self, md_path):
        self.md_path = Path(md_path)
        # Unique per-invocation workdir + lease state file. Stays
        # inside the repo so we never touch /tmp.  Removed on a clean
        # PASS at the end of run_all(); kept around on FAIL so the
        # operator can inspect per-section artefacts.
        tag = f'{os.getpid()}-{time.time_ns()}'
        self.workdir = self.WORKDIR_PARENT / f'workdir-{tag}'
        self.workdir.mkdir(parents=True)
        self.lease_state_file = self.WORKDIR_PARENT / f'.runpy_lease-{tag}'
        self.log_path = Path.cwd() / 'tmp/log.txt'
        self.log_fh = None
        self.user = getpass.getuser()
        self.busy_retry_deadline_s = self._busy_retry_deadline_for_md(
            self.md_path)
        self.failed_attempt_lease_tokens = set()
        # Most recent lease token captured from a section's
        # manifest.json, used to substitute {{LEASE_TOKEN}} in
        # subsequent sections. Cleared when a section's plan contains
        # lease:release.
        self.lease_token = None
        # Defensive ghost-lease cleanup: scan for lease-state files
        # left over from prior crashed runs (PID no longer alive) and
        # release each. Per-PID workdirs from those runs aren't
        # touched -- they're kept for post-mortem.
        self._cleanup_orphan_leases()

    def _cleanup_orphan_leases(self):
        for path in sorted(self.WORKDIR_PARENT.glob('.runpy_lease-*')):
            if path == self.lease_state_file:
                continue
            name = path.name[len('.runpy_lease-'):]
            try:
                pid = int(name.split('-', 1)[0])
            except ValueError:
                continue
            # If the owning PID is still alive, leave it alone --
            # another run.py is using it.
            try:
                os.kill(pid, 0)
                continue
            except ProcessLookupError:
                pass
            except PermissionError:
                # Different uid -- not ours to clean up.
                continue
            try:
                ghost = path.read_text().strip()
            except OSError:
                ghost = ''
            if ghost:
                print(f'releasing ghost lease {ghost} from prior run (pid {pid})')
                self._release_ghost(ghost)
            try:
                path.unlink()
            except OSError:
                pass

    def _release_ghost(self, token, wait_s=30):
        """Best-effort release of a stale lease token left over from a
        prior run. Submits the canonical resume+release pair; failures
        are swallowed (the lease may have already expired)."""
        section = self.workdir / f'_ghost_release_{time.time_ns()}'
        section.mkdir()
        plan_path = section / 'plan.txt'
        plan_path.write_text(
            f'# runpy {time.time_ns()}\n'
            f'lease:resume token="{token}"\n'
            f'description "ghost lease cleanup"\n'
            f'lease:release token="{token}"\n')
        log = section / 'run.log'
        cmd = ['python3', str(self.SUBMIT_PY),
               '--server', self.SERVER,
               '--wait', str(int(wait_s)),
               str(plan_path)]
        with log.open('wb') as f:
            result = subprocess.run(cmd, cwd=self.FAST_DATA, stdout=f,
                                    stderr=subprocess.STDOUT)
        return result.returncode == 0

    UNITS = {'s': 1, 'sec': 1, 'min': 60, 'm': 60, 'h': 3600}

    @classmethod
    def parse_max(cls, spec):
        """Parse 'max N <unit>' (s/sec/min/m/h) into seconds. None on miss."""
        if spec is None:
            return None
        m = re.match(r'max\s+(\d+(?:\.\d+)?)\s*(s|sec|min|m|h)\b',
                     spec.strip())
        if not m:
            return None
        return float(m.group(1)) * cls.UNITS[m.group(2)]

    def parse_md(self):
        """Yield (title, build, artifacts, test, verify, local_test,
        inputs, expect, test_max_s, foreach) per '### ' section.
        ``test_max_s`` is set from a per-block specifier like
        ``Test (max 5 min):``; None when omitted. ``foreach`` is the
        raw text of an optional Foreach block (parsed lazily by
        ``parse_foreach``)."""
        text = self.md_path.read_text()
        parts = re.split(r'^### (.+)$', text, flags=re.M)
        for i in range(1, len(parts), 2):
            title = parts[i].strip()
            body = parts[i + 1]
            blocks = {}
            specs = {}
            for label in ('Build', 'Artifacts', 'Test', 'Verify',
                          'Foreach', 'Local test', 'Inputs', 'Expect'):
                key = label.lower().replace(' ', '_')
                m = re.search(
                    rf'^{label}\s*(?:\(([^)]+)\))?\s*:\s*\n+```\n(.*?)^```',
                    body, re.M | re.S)
                blocks[key] = m.group(2) if m else None
                specs[key] = m.group(1) if m else None
            if blocks['test'] is None and re.search(
                    r'^Test:\s*no hardware\.?\s*$',
                    body, re.M | re.I):
                blocks['test'] = self.NO_HARDWARE_TEST
            yield (title, blocks['build'], blocks['artifacts'],
                   blocks['test'], blocks['verify'],
                   blocks['local_test'], blocks['inputs'],
                   blocks['expect'],
                   self.parse_max(specs['test']),
                   blocks['foreach'])

    @staticmethod
    def is_no_hardware_test(test):
        return test == Runner.NO_HARDWARE_TEST

    @staticmethod
    def parse_foreach(text):
        """Parse a Foreach block. Two forms:
            <var> in <glob-pattern>   - iterate over matching files
            <var> in count(<int>)     - iterate <int> times, var bound
                                        to '1'..'<int>' as a string
        Returns (var_name, pattern) or None when the block is absent.
        For the count form, ``pattern`` is the tuple ('count', N)."""
        if text is None:
            return None
        s = text.strip()
        m = re.match(r'(\w+)\s+in\s+count\(\s*(\d+)\s*\)\s*$', s)
        if m:
            n = int(m.group(2))
            if n <= 0:
                raise RuntimeError(f'Foreach count must be positive: {text!r}')
            return m.group(1), ('count', n)
        m = re.match(r'(\w+)\s+in\s+(.+?)\s*$', s)
        if not m:
            raise RuntimeError(f'invalid Foreach block: {text!r}')
        return m.group(1), m.group(2)

    @staticmethod
    def fmt_seconds(seconds):
        return f'{seconds:g}s'

    def parse_artifacts(self, text):
        """Parse Artifacts block into {basename: relative_path}."""
        out = {}
        if text is None:
            return out
        for ln in text.splitlines():
            ln = ln.strip()
            if not ln or ln.startswith('#'):
                continue
            out[Path(ln).name] = ln
        return out

    @staticmethod
    def budget_seconds(plan_text):
        """Sum of timeout_ms across the plan (in seconds). Useful upper
        bound on how long the in-plan waits could take if every expect
        had to fully time out."""
        if plan_text is None:
            return 0.0
        return sum(int(m) for m in re.findall(
            r'timeout_ms=(\d+)', plan_text)) / 1000.0

    def run_build(self, build, log):
        """Execute each non-empty line of `build` as a shell command.
        Mirrors `$ <cmd>` and the full stdout+stderr to both the
        per-test run.log and to log.txt. Skip when missing or 'nothing'.
        Backslash-at-end-of-line continuations are joined into a single
        command, matching the convention used in long qemu invocations.

        Exports ``RUNPY_WORKDIR`` in the subprocess environment so build
        scripts can stash transient files (refresh plans, scratch
        artefacts) under the per-invocation workdir -- which is
        auto-cleaned on a PASS -- instead of leaking into /tmp."""
        if build is None or build.strip().lower().startswith('nothing'):
            return True
        env = dict(os.environ)
        env['RUNPY_WORKDIR'] = str(self.workdir)
        if self.lease_token:
            env['RUNPY_LEASE_TOKEN'] = self.lease_token
        build = re.sub(r'\\\n[ \t]*', ' ', build)
        for line in build.splitlines():
            if not line.strip():
                continue
            self._log(f'$ {line}')
            with log.open('ab') as f:
                cmd_line = f'$ {line}\n'.encode()
                f.write(cmd_line)
                f.flush()
                proc = subprocess.Popen(
                    line, shell=True, cwd=self.FAST_DATA, env=env,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                assert proc.stdout is not None
                self._tee_pipe_to_logs(proc.stdout, f)
                proc.wait()
            if proc.returncode != 0:
                self._log(f'  (build line returned rc={proc.returncode})')
                return False
        return True

    def _tee_pipe_to_logs(self, pipe, log_fh):
        """Copy a subprocess byte stream to the section log and log.txt live."""
        for chunk in iter(pipe.readline, b''):
            log_fh.write(chunk)
            log_fh.flush()
            self._log(chunk.decode('utf-8', 'replace').rstrip('\r\n'))

    def run_local_test(self, local_test, inputs, log):
        """Execute each non-empty line of `local_test` as a shell
        command, piping `inputs` (when not None) to the FIRST line's
        stdin.  Mirrors `$ <cmd>` and the full stdout+stderr to the
        per-test run.log and to log.txt; in addition, writes the
        subprocess stdout (and stderr -- merged) to tmp/local.out
        for byte-exact comparison against the section's Expect block.
        Backslash-at-end-of-line continuations are joined. Returns
        True on success, False on non-zero rc."""
        if local_test is None:
            return True
        local_out = self.FAST_DATA / 'tmp' / 'local.out'
        local_out.parent.mkdir(exist_ok=True)
        local_out.write_bytes(b'')
        local_test = re.sub(r'\\\n[ \t]*', ' ', local_test)
        first = True
        for line in local_test.splitlines():
            if not line.strip():
                continue
            self._log(f'$ {line}')
            with log.open('ab') as f, local_out.open('ab') as lo:
                f.write(f'$ {line}\n'.encode())
                f.flush()
                proc = subprocess.Popen(
                    line, shell=True, cwd=self.FAST_DATA,
                    stdin=subprocess.PIPE if (first and inputs is not None)
                          else subprocess.DEVNULL,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                assert proc.stdout is not None
                if first and inputs is not None:
                    assert proc.stdin is not None
                    proc.stdin.write(inputs.encode())
                    proc.stdin.close()
                first = False
                for chunk in iter(proc.stdout.readline, b''):
                    f.write(chunk); f.flush()
                    lo.write(chunk); lo.flush()
                    self._log(chunk.decode('utf-8', 'replace').rstrip(
                        '\r\n'))
                proc.wait()
            if proc.returncode != 0:
                self._log(f'  (local-test line returned rc={proc.returncode})')
                return False
        return True

    def run_expect(self, expect_text):
        """Byte-exact compare tmp/local.out against expect_text.
        Returns (ok, diff_text).  The markdown fenced-block grammar
        elides the trailing newline of expect_text; we therefore
        compare modulo a single trailing newline on either side."""
        local_out = self.FAST_DATA / 'tmp' / 'local.out'
        actual_bytes = local_out.read_bytes() if local_out.exists() else b''
        # Normalize a single trailing-newline ambiguity between
        # markdown fence (no trailing \n) and emitted file (has \n).
        a = actual_bytes.rstrip(b'\n')
        e = expect_text.encode().rstrip(b'\n')
        if a == e:
            return True, ''
        import difflib
        diff = difflib.unified_diff(
            e.decode('utf-8', 'replace').splitlines(keepends=True),
            a.decode('utf-8', 'replace').splitlines(keepends=True),
            fromfile='expect', tofile='actual', n=3)
        return False, ''.join(diff)

    def submit_plan(self, plan_text, artifacts, extract_dir, log,
                    description, max_s=None, line_prefix=None):
        """Resolve @blob refs from per-test Artifacts, substitute the
        `{{LEASE_TOKEN}}` placeholder against ``self.lease_token``, and
        submit. Inserts `description "..."` and a unique runpy comment;
        if the plan body's first op is `lease:resume`, description goes
        AFTER that op so prescan still binds the token. Returns
        ``(rc, digest)``. When ``max_s`` is set, X-Test-Runtime caps the
        bench session at that budget; the agent backstops with a
        slightly larger subprocess timeout in case the bench fails to
        enforce. When ``line_prefix`` is given and stdout is a TTY,
        in-place \\r updates show queued/running status with a
        countdown against ``max_s`` while submit.py runs."""
        nonce = time.time_ns()
        description = f'{self.user}: {description} [{nonce}]'
        if self.LEASE_PLACEHOLDER in plan_text:
            if not self.lease_token:
                raise RuntimeError(
                    f'plan references {self.LEASE_PLACEHOLDER} but no '
                    f'lease has been claimed yet')
            plan_text = plan_text.replace(
                self.LEASE_PLACEHOLDER, self.lease_token)
        plan_path = extract_dir.parent / 'plan.txt'
        lines = plan_text.splitlines()
        i = 0
        while i < len(lines) and (
                not lines[i].strip() or lines[i].lstrip().startswith('#')):
            i += 1
        if i < len(lines) and lines[i].lstrip().startswith('lease:resume'):
            head = lines[:i + 1]
            tail = lines[i + 1:]
        else:
            head, tail = [], lines
        body = (head + [f'description "{description}"',
                        f'# runpy {nonce}'] + tail)
        plan_path.write_text('\n'.join(body) + '\n')
        blob_args = []
        for name in sorted(artifacts):
            blob_args += ['--blob', f'{name}={artifacts[name]}']
        wait_s, server_runtime_s = self._submit_time_budgets(max_s)
        cmd = ['python3', str(self.SUBMIT_PY),
               '--server', self.SERVER,
               '--wait', str(wait_s),
               '--extract', str(extract_dir)]
        if server_runtime_s is not None:
            cmd += ['--runtime', str(server_runtime_s)]
        cmd += [*blob_args, str(plan_path)]
        log_fh = log.open('ab')
        cmd_line = f'$ {" ".join(cmd)}'
        self._log(cmd_line)
        log_fh.write(f'{cmd_line}\n'.encode())
        log_fh.flush()
        proc = subprocess.Popen(
            cmd, cwd=self.FAST_DATA, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        tee_thread = None
        if proc.stdout is not None:
            tee_thread = threading.Thread(
                target=self._tee_pipe_to_logs,
                args=(proc.stdout, log_fh),
                daemon=True)
            tee_thread.start()
        rc, queue_lock_wait_s = self._watch_submit(
            proc, log_fh, description, max_s, line_prefix)
        if tee_thread is not None:
            tee_thread.join()
        log_fh.close()
        digest = None
        if extract_dir.exists():
            tars = list(extract_dir.glob('*.tar'))
            if tars:
                digest = tars[0].stem
        return rc, digest, queue_lock_wait_s

    @classmethod
    def _submit_time_budgets(cls, max_s):
        """Return (submit.py wait, server runtime) for one attempt.

        ``max_s`` is the post-lock DUT budget from the mission. The
        deployed poller starts X-Test-Runtime when it picks up the job,
        before bench locks are acquired, so giving the server exactly
        ``max_s`` can expire during lock contention. Run.py still
        enforces the post-lock watchdog from the live LOCK-acquired
        event; the server budget is only an outer cap for pickup plus
        lock wait plus that watchdog.
        """
        if max_s is None:
            return cls.WAIT_S, None
        dut_budget_s = int(max_s) + cls.RUNTIME_GRACE_S
        server_runtime_s = cls.WAIT_S + dut_budget_s
        wait_s = server_runtime_s + cls.RUNTIME_GRACE_S
        return wait_s, server_runtime_s

    @classmethod
    def _busy_retry_deadline_for_md(cls, md_path):
        if Path(md_path).name in cls.LONG_BUSY_RETRY_MISSIONS:
            return cls.LONG_BUSY_RETRY_DEADLINE_S
        return cls.BUSY_RETRY_DEADLINE_S

    def run_verify(self, verify_text, artifacts, extract_dir, item=None):
        """Exec the verify block (with Verification, abs-path artifacts,
        and `re` pre-injected) and return its check() bool. When
        ``item`` is provided (Foreach iteration) and the block's
        ``check`` accepts two args, it is called as
        ``check(extract_dir, item)``."""
        if verify_text is None:
            return True
        abs_artifacts = {n: str(self.FAST_DATA / r)
                         for n, r in artifacts.items()}
        ns = {'Verification': Verification, 'artifacts': abs_artifacts,
              're': re, 'HardFail': HardFail}
        exec(verify_text, ns)
        if 'check' not in ns:
            raise RuntimeError("verify block defines no check()")
        fn = ns['check']
        if fn.__code__.co_argcount >= 2:
            return bool(fn(str(extract_dir), item))
        return bool(fn(str(extract_dir)))

    def _manifest_has_errors(self, extract_dir):
        """True if a submitted attempt's manifest reports op-level errors.
        Harness-level backstop so a step whose bench session errored can
        never be accepted as PASS regardless of what its check() returns.
        Missing/unreadable manifest -> False (defer to check())."""
        try:
            m = json.loads((Path(extract_dir) / 'manifest.json').read_text())
        except (OSError, ValueError):
            return False
        return m.get('n_errors', 0) != 0 or m.get('status') == 'errors'

    def _watch_submit(self, proc, log_fh, description, max_s, line_prefix):
        """Block until ``proc`` exits, polling ``GET /jobs`` once a
        second to find our submission (matched by description). When
        stdout is a TTY, render a queued/running countdown on the line
        BELOW the head so the head never wraps; the countdown line is
        cleared and the cursor restored to end-of-head before
        returning. Enforces an agent-side watchdog just beyond
        ``submit.py --wait`` so queued shared-bench jobs are not killed
        before the server has a chance to run them. Returns the
        subprocess return code."""
        live = (line_prefix is not None and sys.stdout.isatty())
        started_at = time.monotonic()
        started_wall = time.time()
        run_deadline = (max_s + self.RUNTIME_GRACE_S) if max_s else None
        running_since = None
        job_running_since = None
        unresolved_inflight_since = None
        last_inflight_elapsed_s = None
        waiting_for_locks = False
        queue_lock_wait_s = 0.0
        countdown_open = False
        rc = None
        while True:
            rc = proc.poll()
            if rc is not None:
                break
            try:
                with urllib.request.urlopen(f'{self.SERVER}/jobs',
                                            timeout=2) as r:
                    jobs = json.load(r)
            except Exception:
                jobs = []
            hit = next(
                (j for j in jobs
                 if j.get('meta', {}).get('description') == description
                 and j.get('status') in ('queued', 'running')),
                None)
            if hit and hit['status'] == 'running' and running_since is None:
                if job_running_since is None:
                    job_running_since = hit.get('picked_up_at') or time.time()
                active = self._find_inflight_job(hit.get('digest'))
                acquired_t = self._lock_acquired_event_t(active)
                if acquired_t is not None:
                    elapsed_s = float(active.get('elapsed_s') or 0.0)
                    running_since = time.time() - max(
                        0.0, elapsed_s - acquired_t)
                    queue_lock_wait_s = max(
                        queue_lock_wait_s, running_since - started_wall)
                    waiting_for_locks = False
                else:
                    state = self._inflight_wait_state(
                        active, last_inflight_elapsed_s,
                        unresolved_inflight_since)
                    last_inflight_elapsed_s = state['elapsed_s']
                    unresolved_inflight_since = state['unresolved_since']
                    if (state['fallback']
                            and (time.time() - unresolved_inflight_since
                                 >= self.INFLIGHT_FALLBACK_S)):
                        running_since = job_running_since
                        waiting_for_locks = False
                        log_fh.write(
                            b'  (agent watchdog: /inflight missing or stale; '
                            b'using job running time)\n')
                        log_fh.flush()
                        self._log(
                            '  (agent watchdog: /inflight missing or stale; '
                            'using job running time)')
                    elif not waiting_for_locks:
                        waiting_for_locks = True
                        log_fh.write(
                            b'  (agent watchdog: waiting for bench locks; '
                            b'test runtime budget starts after locks are '
                            b'acquired)\n')
                        log_fh.flush()
                        self._log(
                            '  (agent watchdog: waiting for bench locks; '
                            'test runtime budget starts after locks are '
                            'acquired)')
            if (run_deadline and running_since is not None
                    and (time.time() - running_since) > run_deadline):
                digest = self._find_active_job_digest(description)
                self.cancel_job(digest)
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                log_fh.write(b'  (agent watchdog: submit.py exceeded '
                             b'budget; killed)\n')
                self._log('  (agent watchdog: submit.py exceeded '
                          'budget; killed)')
                rc = proc.poll() or 1
                break
            if live:
                if hit and hit['status'] == 'queued':
                    elapsed = int(time.monotonic() - started_at)
                    msg = f'\033[33mqueued ({elapsed}s)\033[0m'
                elif hit and hit['status'] == 'running':
                    if running_since is None:
                        elapsed = int(time.monotonic() - started_at)
                        msg = (
                            f'\033[33mwaiting for bench locks '
                            f'({elapsed}s)\033[0m')
                    elif max_s:
                        elapsed = time.time() - running_since
                        remaining = max(0.0, max_s - elapsed)
                        msg = f'\033[36mrunning ({remaining:.0f}s left)\033[0m'
                    else:
                        elapsed = time.time() - running_since
                        msg = f'\033[36mrunning ({elapsed:.0f}s)\033[0m'
                else:
                    msg = None
                if msg is not None:
                    if not countdown_open:
                        sys.stdout.write('\n')
                        countdown_open = True
                    sys.stdout.write(f'\r\033[K{msg}')
                    sys.stdout.flush()
            time.sleep(1)
        if live and countdown_open:
            # Clear countdown line, move up to head, snap cursor back
            # to end-of-head so the verdict from result() appends.
            col = len(line_prefix) + 1
            sys.stdout.write(f'\r\033[K\033[A\033[{col}G')
            sys.stdout.flush()
        if rc != 0:
            digest = self._find_active_job_digest(description)
            self.cancel_job(digest)
        return rc, queue_lock_wait_s

    def _find_inflight_job(self, digest):
        """Return the live /inflight entry for ``digest``, if present."""
        if not digest:
            return None
        try:
            with urllib.request.urlopen(f'{self.SERVER}/inflight',
                                        timeout=2) as r:
                inflight = json.load(r)
        except Exception:
            return None
        return next((j for j in inflight if j.get('digest') == digest), None)

    @staticmethod
    def _inflight_wait_state(inflight_entry, last_elapsed_s,
                             unresolved_since):
        """Track whether missing/stale /inflight should fall back.

        A live inflight entry whose elapsed_s is advancing can represent
        a legitimate bench-lock wait, so it does not consume DUT runtime.
        Missing entries or entries whose elapsed_s stops advancing are
        bounded by INFLIGHT_FALLBACK_S so a real running job cannot hide
        behind bad /inflight data until submit.py's long --wait expires.
        """
        now = time.time()
        try:
            elapsed_s = float((inflight_entry or {}).get('elapsed_s'))
        except (TypeError, ValueError):
            elapsed_s = None
        if elapsed_s is not None and (
                last_elapsed_s is None or elapsed_s > last_elapsed_s):
            return {
                'elapsed_s': elapsed_s,
                'unresolved_since': None,
                'fallback': False,
            }
        return {
            'elapsed_s': last_elapsed_s if elapsed_s is None else elapsed_s,
            'unresolved_since': unresolved_since or now,
            'fallback': True,
        }

    @staticmethod
    def _lock_acquired_event_t(inflight_entry):
        """Session-relative timestamp when hardware ops actually start.

        test_serv marks a job "running" when the poller picks it up, but
        the session may still be blocked behind another job's device
        locks. The run.py watchdog must not charge that lock wait against
        the DUT runtime budget.
        """
        if not inflight_entry:
            return None
        for event in inflight_entry.get('events') or ():
            if (event.get('kind') == 'LOCK'
                    and event.get('source') == 'session'
                    and event.get('msg') == 'acquired; running ops'):
                try:
                    return float(event.get('t'))
                except (TypeError, ValueError):
                    return 0.0
        return None

    def capture_lease_token(self, extract_dir, plan_text):
        """Refresh ``self.lease_token`` from this section's artefact.
        Looks at the LAST lease op in the section's plan to decide
        whether the section ended with an active lease (claim/resume)
        or not (release). A section that does claim/release/claim is
        fine -- the final claim's token (in manifest.json) is
        captured; the intermediate release does NOT clobber it.
        Mirror the active token into ``lease_state_file`` so a crashed
        next-section can be recovered on the following startup."""
        manifest = extract_dir / 'manifest.json'
        lease_ops = re.findall(r'^\s*lease:(\w+)\b', plan_text, re.M)
        last_op = lease_ops[-1] if lease_ops else None
        if last_op == 'release':
            self.lease_token = None
            if self.lease_state_file.exists():
                self.lease_state_file.unlink()
            return
        if last_op in ('claim', 'resume') and manifest.exists():
            tok = json.loads(manifest.read_text()).get('lease_token')
            if tok:
                self.lease_token = tok
                self.lease_state_file.write_text(tok)

    def _find_active_job_digest(self, description):
        """Return the queued/running job digest matching a description."""
        try:
            with urllib.request.urlopen(f'{self.SERVER}/jobs',
                                        timeout=5) as r:
                jobs = json.load(r)
        except Exception:
            return None
        hit = next(
            (j for j in jobs
             if j.get('meta', {}).get('description') == description
             and j.get('status') in ('queued', 'running')),
            None)
        return hit.get('digest') if hit else None

    def cancel_job(self, digest):
        if not digest:
            return
        req = urllib.request.Request(
            f'{self.SERVER}/jobs/{digest}', method='DELETE')
        try:
            urllib.request.urlopen(req, timeout=5).read()
        except Exception:
            pass

    def delete_outputs(self, digest):
        if not digest:
            return
        req = urllib.request.Request(
            f'{self.SERVER}/outputs/{digest}', method='DELETE')
        try:
            urllib.request.urlopen(req, timeout=5).read()
        except Exception:
            pass

    def _run_foreach(self, foreach, title, test, verify, artifacts,
                     section_dir, test_max_s, colored, dump):
        """Glob the Foreach pattern (relative to FAST_DATA), then for
        each match run submit_plan + run_verify and print one indented
        sub-row. The loop variable is registered as a blob, so the
        plan can reference it as `@<var>`. Stops on first failure
        and returns False; True iff every iteration passed (vacuously
        true on zero matches, mirroring `for x in []:` semantics)."""
        var_name, pattern = foreach
        is_count = isinstance(pattern, tuple) and pattern[0] == 'count'
        if is_count:
            n = pattern[1]
            # (label, blob_path-or-None, item_arg-for-verify)
            items = [(f'iter_{j:0{len(str(n))}d}', None, str(j))
                     for j in range(1, n + 1)]
        else:
            matches = sorted(self.FAST_DATA.glob(pattern))
            # Include the immediate parent dir in the label so a sweep
            # like build/{cces,sel}/cctest_*.ldr surfaces which
            # toolchain each iteration is hitting; bare filename is
            # ambiguous when the same stem exists in multiple subdirs.
            items = [(f'{p.parent.name}/{p.name}',
                      str(p.relative_to(self.FAST_DATA)),
                      str(p)) for p in matches]
        sub_total = len(items)
        sys.stdout.write(f'{sub_total} items:\n')
        sys.stdout.flush()
        if not items:
            return True
        sub_w = len(str(sub_total))
        for j, (label, blob_path, item_arg) in enumerate(items, 1):
            sub_artifacts = dict(artifacts)
            # Glob form binds @<var> to the iteration's file blob. The
            # count form has no file, so we skip the blob registration
            # entirely; verify's check() still receives the counter via
            # ``item_arg``.
            if blob_path is not None:
                sub_artifacts[var_name] = blob_path
            sub_dir = section_dir / f'item_{j:0{sub_w}d}'
            sub_dir.mkdir()
            sub_started = datetime.datetime.now().strftime('%H:%M:%S')
            sub_t0 = time.monotonic()
            sub_head = (f'  [{j:>{sub_w}}/{sub_total}] [{sub_started}] '
                        f'{label} ')
            sys.stdout.write(sub_head)
            sys.stdout.flush()

            (ok, digest, fail_reason, fail_extract, fail_log,
             queue_lock_wait_s) = (
                self._submit_with_retries(
                    test, sub_artifacts, sub_dir,
                    f'{title} :: {label}', test_max_s,
                    item_arg, verify))
            el = time.monotonic() - sub_t0
            charged_el = max(0.0, el - queue_lock_wait_s)
            elapsed_text = (
                f'+{charged_el:.1f}s'
                if queue_lock_wait_s <= 0 else
                f'+{charged_el:.1f}s + {queue_lock_wait_s:.1f}s')
            if ok:
                if test_max_s is not None and charged_el > test_max_s:
                    sys.stdout.write(
                        f'{colored("FAIL")} ({elapsed_text})\n')
                    sys.stdout.flush()
                    msg = (f'   exceeded Test (max {self.fmt_seconds(test_max_s)}) '
                           f'hard budget: +{charged_el:.1f}s actual')
                    if queue_lock_wait_s > 0:
                        msg += (f' ({queue_lock_wait_s:.1f}s '
                                f'queue/bench-lock wait excluded)')
                    print(msg); self._log(msg)
                    self._log(f'  [{j:>{sub_w}}/{sub_total}] [{sub_started}] '
                              f'{colored("FAIL")} {label} '
                              f'({elapsed_text})')
                    if fail_log is not None:
                        dump(fail_log, fail_extract)
                    return False
                sys.stdout.write(f'({elapsed_text})\n')
                sys.stdout.flush()
                self._log(f'  [{j:>{sub_w}}/{sub_total}] [{sub_started}] '
                          f'{colored("PASS")} {label} ({elapsed_text})')
                self.delete_outputs(digest)
                continue
            sys.stdout.write(f'{colored("FAIL")} ({elapsed_text})\n')
            sys.stdout.flush()
            self._log(f'  [{j:>{sub_w}}/{sub_total}] [{sub_started}] '
                      f'{colored("FAIL")} {label} ({elapsed_text})')
            if fail_reason:
                print(fail_reason); self._log(fail_reason)
            if fail_log is not None:
                dump(fail_log, fail_extract)
            return False
        return True

    def _submit_with_retries(self, test, artifacts, work_dir, description,
                             max_s, item, verify):
        """Submit + verify with bounded retries on transient failures.
        Each attempt uses a fresh ``work_dir/attempt_<n>/artefact`` so
        stale tarballs don't interfere; submit_plan auto-stamps a fresh
        nonce per call so the bench gives us a fresh digest. Retries
        are uniform across submit-rc != 0, run_verify exceptions, and
        verify-check() returning False -- transient bench failures
        (FT4222 dropouts, queue contention, USB glitches) often mark
        the manifest with op-level errors which fail manifest_clean().
        For deterministic mismatches the cost is the cumulative
        backoff before we conclude. Returns (ok, digest, reason,
        extract, log) -- extract/log point at the LAST attempt's
        artefact directory and run log for dump(). Also returns the
        accumulated queue/bench-lock wait to exclude from hard budgets."""
        last_reason = None
        last_extract = None
        last_log = None
        digest = None
        attempt = 0
        physical_attempt = 0
        busy_retries = 0
        busy_started = None
        self._busy_retry_holder = None
        queue_lock_wait_total_s = 0.0
        while attempt < len(self.RETRY_BACKOFF_S):
            backoff = self.RETRY_BACKOFF_S[attempt]
            if backoff:
                time.sleep(backoff)
            attempt_dir = work_dir / f'attempt_{physical_attempt}'
            physical_attempt += 1
            attempt_dir.mkdir()
            extract = attempt_dir / 'artefact'
            log = attempt_dir / 'run.log'
            last_extract, last_log = extract, log
            rc, digest, queue_lock_wait_s = self.submit_plan(
                test, artifacts, extract, log, description, max_s)
            queue_lock_wait_total_s += queue_lock_wait_s
            busy_before_ops = self._failed_before_ops_due_to_busy(extract)
            if rc != 0:
                last_reason = f'   submit.py rc={rc}'
                self._release_failed_attempt_lease(extract, test)
                if (self._lease_released_in_attempt(extract)
                        and self.LEASE_PLACEHOLDER in test):
                    break
                if busy_before_ops:
                    retry, busy_started, busy_retries, busy_reason = (
                        self._retry_after_busy_before_ops(
                            extract, busy_started, busy_retries))
                    if retry:
                        continue
                    last_reason = busy_reason
                    break
                attempt += 1
                continue
            try:
                ok = self.run_verify(verify, artifacts, extract, item)
            except HardFail as e:
                last_reason = f'   {e}'
                self._release_failed_attempt_lease(extract, test)
                break
            except Exception as e:
                last_reason = f'   verify {type(e).__name__}: {e}'
                self._release_failed_attempt_lease(extract, test)
                if (self._lease_released_in_attempt(extract)
                        and self.LEASE_PLACEHOLDER in test):
                    break
                if busy_before_ops:
                    retry, busy_started, busy_retries, busy_reason = (
                        self._retry_after_busy_before_ops(
                            extract, busy_started, busy_retries))
                    if retry:
                        continue
                    last_reason = busy_reason
                    break
                attempt += 1
                continue
            # Defense in depth against a false PASS: submit.py exits 0 even
            # when the bench session recorded op-level errors, so run.py
            # relies on check() to notice them via manifest_clean(). A check()
            # that forgets manifest_clean (or a transient artefact mismatch)
            # must never be allowed to report PASS over a manifest the bench
            # itself flagged as errored. Treat that as a failed attempt.
            errored = ok and self._manifest_has_errors(extract)
            if not ok or errored:
                last_reason = (
                    '   verify check() returned False' if not ok else
                    '   verify check() True but manifest reports op errors')
                self._release_failed_attempt_lease(extract, test)
                if (self._lease_released_in_attempt(extract)
                        and self.LEASE_PLACEHOLDER in test):
                    break
                if busy_before_ops:
                    retry, busy_started, busy_retries, busy_reason = (
                        self._retry_after_busy_before_ops(
                            extract, busy_started, busy_retries))
                    if retry:
                        continue
                    last_reason = busy_reason
                    break
                attempt += 1
                continue
            return (True, digest, None, extract, log,
                    queue_lock_wait_total_s)
        return (False, digest, last_reason, last_extract, last_log,
                queue_lock_wait_total_s)

    def _retry_after_busy_before_ops(self, extract_dir, busy_started,
                                     busy_retries):
        """Retry zero-op lease/busy rejects until a wall-clock deadline."""
        holder = self._busy_lease_holder(extract_dir)
        if self._is_failed_attempt_lease_token(holder):
            if self._release_failed_attempt_lease_token(holder):
                return True, busy_started, busy_retries, None
            reason = (
                f'   bench busy on unreleased failed-attempt lease '
                f'{holder[:8]}')
            return False, busy_started, busy_retries, reason

        # If the busy holder is the lease we captured from the prior
        # section (which used `lease:claim` without `lease:release`),
        # the next section's fresh `lease:claim` will deadlock until
        # the 1-hour duration expires. Release it ourselves so the
        # next attempt can claim cleanly. Also release if the holder
        # is unknown to us (a prior section may have used
        # `auto_release_on_session_end=true` which clears
        # self.lease_token even though the bench still tracks the
        # token until the device is freed): we own this run's session,
        # so any zero-op busy lease left holding our devices is ours
        # to release. We track each token in
        # `failed_attempt_lease_tokens` so a foreign user's lease
        # rejected against our claim isn't repeatedly fired at.
        if holder and (holder == self.lease_token
                       or not self._other_user_job_running()):
            if self._release_ghost(
                    holder, wait_s=self.FAILED_ATTEMPT_LEASE_RELEASE_WAIT_S):
                if holder == self.lease_token:
                    self.lease_token = None
                if self.lease_state_file.exists():
                    self.lease_state_file.unlink()
                self._failed_attempt_lease_token_set().add(holder)
                return True, busy_started, busy_retries, None

        now = time.monotonic()
        prior_holder = getattr(self, '_busy_retry_holder', None)
        other_user_active = self._other_user_job_running()
        if (busy_started is None or holder != prior_holder
                or other_user_active):
            busy_started = now
            busy_retries = 0
        self._busy_retry_holder = holder
        elapsed = now - busy_started
        deadline_s = self._busy_retry_deadline_s()
        if elapsed >= deadline_s:
            reason = (
                f'   bench busy before ops for >= '
                f'{self._busy_retry_deadline_s()}s')
            return False, busy_started, busy_retries, reason
        busy_retries += 1
        sleep_s = self.RETRY_BACKOFF_S[
            min(busy_retries, len(self.RETRY_BACKOFF_S) - 1)]
        remaining = deadline_s - elapsed
        if sleep_s and remaining > 0:
            time.sleep(min(sleep_s, remaining))
        return True, busy_started, busy_retries, None

    def _busy_retry_deadline_s(self):
        return getattr(self, 'busy_retry_deadline_s',
                       self.BUSY_RETRY_DEADLINE_S)

    def _other_user_job_running(self):
        """True if the shared bench is visibly busy with another user."""
        try:
            with urllib.request.urlopen(f'{self.SERVER}/jobs',
                                        timeout=2) as r:
                jobs = json.load(r)
            with urllib.request.urlopen(f'{self.SERVER}/inflight',
                                        timeout=2) as r:
                inflight = json.load(r)
        except Exception:
            return False
        prefix = f'{getattr(self, "user", getpass.getuser())}: '
        active_digests = {
            job.get('digest') for job in inflight if job.get('digest')
        }
        for job in jobs:
            if job.get('status') != 'running':
                continue
            if job.get('digest') not in active_digests:
                continue
            meta = job.get('meta') or {}
            description = meta.get('description') or meta.get('Description')
            if not description or not description.startswith(prefix):
                return True
        return False

    @staticmethod
    def _failed_before_ops_due_to_busy(extract_dir):
        """True when the bench rejected the attempt before running ops."""
        manifest = extract_dir / 'manifest.json'
        errors = extract_dir / 'errors.log'
        if not manifest.exists():
            return False
        try:
            n_ops = int(json.loads(manifest.read_text()).get('n_ops', 1))
        except Exception:
            return False
        if n_ops != 0:
            return False
        if errors.exists():
            text = errors.read_text(errors='replace')
            if ' is leased to ' in text or 'BusyError' in text:
                return True
        timeline = extract_dir / 'timeline.log'
        if not timeline.exists():
            return False
        text = timeline.read_text(errors='replace')
        return ('LOCK     session              acquired; running ops' in text
                and 'ERROR    session              session exceeded ' in text
                and ' deadline' in text)

    @staticmethod
    def _busy_lease_holder(extract_dir):
        errors = extract_dir / 'errors.log'
        if not errors.exists():
            return None
        text = errors.read_text(errors='replace')
        match = re.search(r" is leased to '([^']+)'", text)
        return match.group(1) if match else None

    def _failed_attempt_lease_token_set(self):
        tokens = getattr(self, 'failed_attempt_lease_tokens', None)
        if tokens is None:
            tokens = set()
            self.failed_attempt_lease_tokens = tokens
        return tokens

    def _is_failed_attempt_lease_token(self, token):
        return bool(token and token in self._failed_attempt_lease_token_set())

    def _release_failed_attempt_lease_token(self, token):
        tokens = self._failed_attempt_lease_token_set()
        tokens.add(token)
        ok = self._release_ghost(
            token, wait_s=self.FAILED_ATTEMPT_LEASE_RELEASE_WAIT_S)
        if ok:
            tokens.discard(token)
        return ok

    def _lease_released_in_attempt(self, extract_dir):
        """Return True if the attempt consumed its lease token."""
        ops = extract_dir / 'ops.jsonl'
        if not ops.exists():
            return False
        try:
            for line in ops.read_text(errors='replace').splitlines():
                op = json.loads(line)
                if (op.get('device') == 'lease'
                        and op.get('verb') == 'release'
                        and op.get('status') == 'ok'):
                    self.lease_token = None
                    if self.lease_state_file.exists():
                        self.lease_state_file.unlink()
                    return True
        except Exception:
            return False
        return False

    def _release_failed_attempt_lease(self, extract_dir, plan_text):
        """Release a freshly claimed lease from a failed retry attempt."""
        if 'lease:claim' not in plan_text or 'lease:release' in plan_text:
            return
        manifest = extract_dir / 'manifest.json'
        if not manifest.exists():
            return
        try:
            token = json.loads(manifest.read_text()).get('lease_token')
        except Exception:
            return
        if token:
            self._release_failed_attempt_lease_token(token)

    def run_all(self):
        """Iterate sections in order. Per test prints
        `[i/N] [HH:MM:SS] title (+Ts)` on success, or
        `[i/N] [HH:MM:SS] title FAIL|SKIP (+Ts)` otherwise. T is the
        actual elapsed. A green `PASS` is printed once at the very end
        when no section failed. Halts on first
        FAIL after dumping the per-test log + any errors.log. Lease
        lifecycle is the mission's responsibility (sections write their
        own lease:claim / lease:resume / lease:release ops); run.py
        only threads the issued token through `{{LEASE_TOKEN}}`. Sends
        DELETE /outputs/<digest> on PASS to cleanup the dashboard.
        Returns 0 on full pass."""
        print(f'workdir: {self.workdir}')
        sections = list(self.parse_md())
        total = len(sections)
        w = len(str(total))
        use_color = True

        self.log_fh = self.log_path.open('a')
        ts = datetime.datetime.now().isoformat(timespec='seconds')
        self._log(f'=== {ts}  {self.md_path}  workdir={self.workdir} ===')

        def colored(label):
            if not use_color:
                return label
            code = {'PASS': '32', 'FAIL': '31', 'SKIP': '33'}[label]
            return f'\033[{code}m{label}\033[0m'

        def result(i, label, title, elapsed, started, budget, excluded=0.0):
            elapsed_text = (
                f'+{elapsed:.1f}s'
                if excluded <= 0 else
                f'+{elapsed:.1f}s + {excluded:.1f}s')
            if label == 'PASS':
                sys.stdout.write(f'({elapsed_text})\n')
            else:
                sys.stdout.write(f'{colored(label)} ({elapsed_text})\n')
            sys.stdout.flush()
            self._log(f'[{i:>{w}}/{total}] [{started}] {colored(label)} {title} '
                      f'(<={budget:.0f}s budget, {elapsed_text})')

        def pass_or_timeout(i, title, started, budget, test_max_s, elapsed):
            if test_max_s is not None and elapsed > test_max_s:
                result(i, 'FAIL', title, elapsed, started, budget)
                msg = (f'   exceeded Test (max {self.fmt_seconds(test_max_s)}) '
                       f'hard budget: +{elapsed:.1f}s actual')
                print(msg); self._log(msg)
                return False
            result(i, 'PASS', title, elapsed, started, budget)
            return True

        def charged_elapsed(elapsed, excluded):
            return max(0.0, elapsed - excluded)

        def pass_or_timeout_excluding_wait(
                i, title, started, budget, test_max_s, elapsed, excluded):
            charged = charged_elapsed(elapsed, excluded)
            if test_max_s is not None and charged > test_max_s:
                result(i, 'FAIL', title, charged, started, budget, excluded)
                msg = (f'   exceeded Test (max {self.fmt_seconds(test_max_s)}) '
                       f'hard budget: +{charged:.1f}s actual')
                if excluded > 0:
                    msg += f' ({excluded:.1f}s queue/bench-lock wait excluded)'
                print(msg); self._log(msg)
                return False
            result(i, 'PASS', title, charged, started, budget, excluded)
            return True

        def dump(log, extract_dir=None):
            for src in (log, (extract_dir / 'errors.log') if extract_dir
                        else None):
                if src is None or not src.exists() or not src.stat().st_size:
                    continue
                hdr = f'   --- {src} ---'
                print(hdr); self._log(hdr)
                for ln in src.read_text(errors='replace').splitlines():
                    print(f'   {ln}'); self._log(f'   {ln}')

        try:
            skipped = 0
            for i, (title, build, artifacts_text, test, verify,
                    local_test, inputs, expect,
                    test_max_s, foreach_text) in enumerate(sections, 1):
                slug = re.sub(r'[^a-z0-9]+', '_', title.lower()).strip('_')
                section_dir = self.workdir / slug
                section_dir.mkdir()
                extract_dir = section_dir / 'artefact'
                log = section_dir / 'run.log'
                artifacts = self.parse_artifacts(artifacts_text)
                budget = (test_max_s if test_max_s is not None
                          else self.budget_seconds(test))

                started = datetime.datetime.now().strftime('%H:%M:%S')
                t0 = time.monotonic()
                el = lambda: time.monotonic() - t0
                head = f'[{i:>{w}}/{total}] [{started}] {title} '
                sys.stdout.write(head)
                sys.stdout.flush()

                if build is not None and not build.strip().lower().startswith(
                        'nothing'):
                    if not self.run_build(build, log):
                        result(i, 'FAIL', title, el(), started, budget)
                        dump(log)
                        return 1
                if local_test is not None:
                    if not self.run_local_test(local_test, inputs, log):
                        result(i, 'FAIL', title, el(), started, budget)
                        dump(log)
                        return 1
                    if expect is not None:
                        ok, diff = self.run_expect(expect)
                        if not ok:
                            result(i, 'FAIL', title, el(), started, budget)
                            self._log('   expect/actual diff:')
                            for ln in diff.splitlines():
                                print(f'   {ln}'); self._log(f'   {ln}')
                            return 1
                    if not pass_or_timeout(
                            i, title, started, budget, test_max_s, el()):
                        return 1
                    continue
                foreach = self.parse_foreach(foreach_text)
                if foreach is not None:
                    if test is None:
                        result(i, 'FAIL', title, el(), started, budget)
                        msg = '   Foreach requires a Test block'
                        print(msg); self._log(msg)
                        return 1
                    if not self._run_foreach(
                            foreach, title, test, verify, artifacts,
                            section_dir, test_max_s, colored, dump):
                        result(i, 'FAIL', title, el(), started, budget)
                        return 1
                    result(i, 'PASS', title, el(), started, budget)
                    continue
                if self.is_no_hardware_test(test):
                    extract_dir.mkdir()
                    try:
                        ok = self.run_verify(verify, artifacts, extract_dir)
                    except Exception as e:
                        result(i, 'FAIL', title, el(), started, budget)
                        msg = f'   verify {type(e).__name__}: {e}'
                        print(msg); self._log(msg)
                        dump(log, extract_dir)
                        return 1
                    if not ok:
                        result(i, 'FAIL', title, el(), started, budget)
                        msg = '   verify check() returned False'
                        print(msg); self._log(msg)
                        dump(log, extract_dir)
                        return 1
                    if not pass_or_timeout(
                            i, title, started, budget, test_max_s, el()):
                        return 1
                    continue
                if test is None:
                    if build is not None and not build.strip().lower(
                            ).startswith('nothing'):
                        result(i, 'PASS', title, el(), started, budget)
                    else:
                        result(i, 'SKIP', title, el(), started, budget)
                        skipped += 1
                    continue
                (ok, digest, fail_reason, fail_extract, fail_log,
                 queue_lock_wait_s) = (
                    self._submit_with_retries(
                        test, artifacts, section_dir, title, test_max_s,
                        None, verify))
                if not ok:
                    result(i, 'FAIL', title,
                           charged_elapsed(el(), queue_lock_wait_s),
                           started, budget, queue_lock_wait_s)
                    if fail_reason:
                        print(fail_reason); self._log(fail_reason)
                    if fail_log is not None:
                        dump(fail_log, fail_extract)
                    return 1
                self.capture_lease_token(fail_extract, test)
                self.delete_outputs(digest)
                if not pass_or_timeout_excluding_wait(
                        i, title, started, budget, test_max_s, el(),
                        queue_lock_wait_s):
                    return 1

            print(colored('PASS'))
            self._log(f'{colored("PASS")} {total - skipped}/{total}')
            success = True
            return 0
        finally:
            self.log_fh.close()
            self.log_fh = None
            if locals().get('success'):
                # Clean PASS -- remove the per-invocation workdir.
                # FAIL paths leave it on disk for post-mortem.
                try:
                    shutil.rmtree(self.workdir)
                except OSError:
                    pass
                try:
                    if self.lease_state_file.exists():
                        self.lease_state_file.unlink()
                except OSError:
                    pass

    def _log(self, line):
        if self.log_fh is not None:
            self.log_fh.write(line + '\n')
            self.log_fh.flush()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('md_file')
    args = ap.parse_args()
    fails = Runner(args.md_file).run_all()
    sys.exit(0 if fails == 0 else 1)


if __name__ == '__main__':
    sys.modules['run'] = sys.modules['__main__']
    main()
