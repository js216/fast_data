#!/usr/bin/env python3
"""Walk a regression-plan .md file, run Build -> Test -> Verify per
section, print a PASS/FAIL line for each.

Usage: python3 run.py ssh.md
"""
import argparse
import datetime
import json
import re
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path


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
    WAIT_S = 600                     # generous upper bound
    LEASE_PLACEHOLDER = '{{LEASE_TOKEN}}'

    def __init__(self, md_path):
        self.md_path = Path(md_path)
        self.workdir = Path(tempfile.mkdtemp(prefix='runpy-'))
        self.log_path = Path.cwd() / 'log.txt'
        self.log_fh = None
        # Most recent lease token captured from a section's
        # streams/lease.token.bin, used to substitute {{LEASE_TOKEN}}
        # in subsequent sections. Cleared when a section's plan
        # contains lease:release.
        self.lease_token = None

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
        """Yield (title, build, artifacts, test, verify, test_max_s,
        foreach) per '### ' section. ``test_max_s`` is set from a
        per-block specifier like ``Test (max 5 min):``; None when
        omitted. ``foreach`` is the raw text of an optional Foreach
        block (parsed lazily by ``parse_foreach``)."""
        text = self.md_path.read_text()
        parts = re.split(r'^### (.+)$', text, flags=re.M)
        for i in range(1, len(parts), 2):
            title = parts[i].strip()
            body = parts[i + 1]
            blocks = {}
            specs = {}
            for label in ('Build', 'Artifacts', 'Test', 'Verify',
                          'Foreach'):
                m = re.search(
                    rf'^{label}\s*(?:\(([^)]+)\))?\s*:\s*\n+```\n(.*?)\n```',
                    body, re.M | re.S)
                blocks[label.lower()] = m.group(2) if m else None
                specs[label.lower()] = m.group(1) if m else None
            yield (title, blocks['build'], blocks['artifacts'],
                   blocks['test'], blocks['verify'],
                   self.parse_max(specs['test']),
                   blocks['foreach'])

    @staticmethod
    def parse_foreach(text):
        """Parse a Foreach block ('<var> in <glob-pattern>') into
        (var_name, pattern). Returns None when the block is absent."""
        if text is None:
            return None
        m = re.match(r'\s*(\w+)\s+in\s+(.+?)\s*$', text.strip())
        if not m:
            raise RuntimeError(f'invalid Foreach block: {text!r}')
        return m.group(1), m.group(2)

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
        per-test run.log and to log.txt. Skip when missing or 'nothing'."""
        if build is None or build.strip().lower().startswith('nothing'):
            return True
        for line in build.splitlines():
            if not line.strip():
                continue
            self._log(f'$ {line}')
            with log.open('ab') as f:
                f.write(f'$ {line}\n'.encode())
                proc = subprocess.run(line, shell=True, cwd=self.FAST_DATA,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT)
                f.write(proc.stdout)
            for ln in proc.stdout.decode('utf-8', 'replace').splitlines():
                self._log(ln)
            if proc.returncode != 0:
                self._log(f'  (build line returned rc={proc.returncode})')
                return False
        return True

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
                        f'# runpy {time.time_ns()}'] + tail)
        plan_path.write_text('\n'.join(body) + '\n')
        blob_args = []
        for name in sorted(artifacts):
            blob_args += ['--blob', f'{name}={artifacts[name]}']
        cmd = ['python3', str(self.SUBMIT_PY),
               '--server', self.SERVER,
               '--wait', str(self.WAIT_S),
               '--extract', str(extract_dir)]
        if max_s is not None:
            cmd += ['--runtime', str(int(max_s))]
        cmd += [*blob_args, str(plan_path)]
        log_fh = log.open('ab')
        log_fh.write(f'$ {" ".join(cmd)}\n'.encode())
        proc = subprocess.Popen(
            cmd, cwd=self.FAST_DATA, stdout=log_fh,
            stderr=subprocess.STDOUT)
        rc = self._watch_submit(proc, log_fh, description, max_s,
                                line_prefix)
        log_fh.close()
        digest = None
        if extract_dir.exists():
            tars = list(extract_dir.glob('*.tar'))
            if tars:
                digest = tars[0].stem
        return rc, digest

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
              're': re}
        exec(verify_text, ns)
        if 'check' not in ns:
            raise RuntimeError("verify block defines no check()")
        fn = ns['check']
        if fn.__code__.co_argcount >= 2:
            return bool(fn(str(extract_dir), item))
        return bool(fn(str(extract_dir)))

    def _watch_submit(self, proc, log_fh, description, max_s, line_prefix):
        """Block until ``proc`` exits, polling ``GET /jobs`` once a
        second to find our submission (matched by description) and
        repaint ``line_prefix`` + a queued/running status with a
        countdown when ``max_s`` is known. Enforces an agent-side
        watchdog at ``max_s + 30`` so a stuck submit.py can't outlive
        its budget. Returns the subprocess return code."""
        live = (line_prefix is not None and sys.stdout.isatty())
        started_at = time.monotonic()
        deadline = (max_s + 30) if max_s else None
        running_since = None
        rc = None
        while True:
            rc = proc.poll()
            if rc is not None:
                break
            if deadline and (time.monotonic() - started_at) > deadline:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                log_fh.write(b'  (agent watchdog: submit.py exceeded '
                             b'budget; killed)\n')
                rc = proc.poll() or 1
                break
            if live:
                try:
                    with urllib.request.urlopen(
                            f'{self.SERVER}/jobs', timeout=2) as r:
                        jobs = json.load(r)
                except Exception:
                    jobs = []
                hit = next(
                    (j for j in jobs
                     if j.get('meta', {}).get('description') == description
                     and j.get('status') in ('queued', 'running')),
                    None)
                if hit and hit['status'] == 'queued':
                    elapsed = int(time.monotonic() - started_at)
                    msg = f'queued ({elapsed}s)'
                elif hit and hit['status'] == 'running':
                    if running_since is None:
                        running_since = hit.get('picked_up_at') or time.time()
                    elapsed = time.time() - running_since
                    if max_s:
                        remaining = max(0.0, max_s - elapsed)
                        msg = f'running ({remaining:.0f}s left)'
                    else:
                        msg = f'running ({elapsed:.0f}s)'
                else:
                    msg = None
                if msg is not None:
                    sys.stdout.write(f'\r{line_prefix}{msg}\033[K')
                    sys.stdout.flush()
            time.sleep(1)
        if live:
            sys.stdout.write(f'\r{line_prefix}\033[K')
            sys.stdout.flush()
        return rc

    def capture_lease_token(self, extract_dir, plan_text):
        """Refresh ``self.lease_token`` from this section's artefact:
        if a `lease.token` stream exists, the section ran a fresh
        ``lease:claim`` and we adopt the new token. If the section's
        plan body contains ``lease:release``, drop the captured token
        regardless -- it's no longer usable."""
        stream = extract_dir / 'streams' / 'lease.token.bin'
        if stream.exists():
            tok = stream.read_text().strip()
            if tok:
                self.lease_token = tok
        if 'lease:release' in plan_text:
            self.lease_token = None

    def delete_job(self, digest):
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
        matches = sorted(self.FAST_DATA.glob(pattern))
        sub_total = len(matches)
        sys.stdout.write(f'{sub_total} items:\n')
        sys.stdout.flush()
        if not matches:
            return True
        sub_w = len(str(sub_total))
        for j, path in enumerate(matches, 1):
            label = path.name
            sub_artifacts = dict(artifacts)
            sub_artifacts[var_name] = str(path.relative_to(self.FAST_DATA))
            sub_dir = section_dir / f'item_{j:0{sub_w}d}'
            sub_dir.mkdir()
            sub_extract = sub_dir / 'artefact'
            sub_log = sub_dir / 'run.log'
            sub_started = datetime.datetime.now().strftime('%H:%M:%S')
            sub_t0 = time.monotonic()
            sys.stdout.write(
                f'  [{j:>{sub_w}}/{sub_total}] [{sub_started}] '
                f'{label} ... ')
            sys.stdout.flush()

            def emit(verdict, extra_dump=None, extra_msg=None):
                el = time.monotonic() - sub_t0
                sys.stdout.write(
                    f'{colored(verdict)} (+{el:.1f}s)\n')
                sys.stdout.flush()
                self._log(f'  [{j:>{sub_w}}/{sub_total}] [{sub_started}] '
                          f'{verdict} {label} (+{el:.1f}s)')
                if extra_msg:
                    print(extra_msg); self._log(extra_msg)
                if extra_dump is not None:
                    dump(sub_log, extra_dump)

            rc, digest = self.submit_plan(
                test, sub_artifacts, sub_extract, sub_log,
                f'{title} :: {label}', test_max_s)
            if rc != 0:
                emit('FAIL')
                dump(sub_log)
                return False
            try:
                ok = self.run_verify(verify, sub_artifacts, sub_extract,
                                     str(path))
            except Exception as e:
                emit('FAIL', sub_extract,
                     f'   verify {type(e).__name__}: {e}')
                return False
            if not ok:
                emit('FAIL', sub_extract,
                     '   verify check() returned False')
                return False
            self.delete_job(digest)
            emit('PASS')
        return True

    def run_all(self):
        """Iterate sections in order. Per test prints
        `[i/N] [HH:MM:SS] title (<=Bs) ... build ... run ... check ... PASS|FAIL|SKIP (+Ts)`
        where B is the sum of timeout_ms in the plan (the upper bound
        on in-plan waits) and T is the actual elapsed. Halts on first
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
        use_color = sys.stdout.isatty()

        self.log_fh = self.log_path.open('a')
        ts = datetime.datetime.now().isoformat(timespec='seconds')
        self._log(f'=== {ts}  {self.md_path}  workdir={self.workdir} ===')

        def colored(label):
            if not use_color:
                return label
            code = {'PASS': '32', 'FAIL': '31', 'SKIP': '33'}[label]
            return f'\033[{code}m{label}\033[0m'

        def stage(word):
            sys.stdout.write(f'{word} ... ')
            sys.stdout.flush()

        def result(i, label, title, elapsed, started, budget):
            sys.stdout.write(f'{colored(label)} (+{elapsed:.1f}s)\n')
            sys.stdout.flush()
            self._log(f'[{i:>{w}}/{total}] [{started}] {label} {title} '
                      f'(<={budget:.0f}s budget, +{elapsed:.1f}s actual)')

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
                    test_max_s, foreach_text) in enumerate(sections, 1):
                slug = re.sub(r'[^a-z0-9]+', '_', title.lower()).strip('_')
                section_dir = self.workdir / slug
                section_dir.mkdir()
                extract_dir = section_dir / 'artefact'
                log = section_dir / 'run.log'
                artifacts = self.parse_artifacts(artifacts_text)
                budget = self.budget_seconds(test)

                started = datetime.datetime.now().strftime('%H:%M:%S')
                t0 = time.monotonic()
                el = lambda: time.monotonic() - t0
                head = (f'[{i:>{w}}/{total}] [{started}] {title} '
                        f'(<={budget:.0f}s) ... ')
                sys.stdout.write(head)
                sys.stdout.flush()

                if build is not None and not build.strip().lower().startswith(
                        'nothing'):
                    stage('build')
                    head += 'build ... '
                    if not self.run_build(build, log):
                        result(i, 'FAIL', title, el(), started, budget)
                        dump(log)
                        return 1
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
                if test is None:
                    result(i, 'SKIP', title, el(), started, budget)
                    skipped += 1
                    continue
                stage('run')
                head += 'run ... '
                rc, digest = self.submit_plan(test, artifacts, extract_dir,
                                              log, title, test_max_s,
                                              line_prefix=head)
                if rc != 0:
                    result(i, 'FAIL', title, el(), started, budget)
                    dump(log)
                    return 1
                self.capture_lease_token(extract_dir, test)
                stage('check')
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
                self.delete_job(digest)
                result(i, 'PASS', title, el(), started, budget)

            summary = f'-- {total - skipped}/{total} passed --'
            print(summary); self._log(summary)
            return 0
        finally:
            self.log_fh.close()
            self.log_fh = None

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
