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

    def op_succeeded(ops, device, verb):
        """True iff `device:verb` appears in `ops` with status='ok'."""
        return any(o.get('device') == device and o.get('verb') == verb
                   and o.get('status') == 'ok' for o in ops)


class Runner:
    """Parses a regression-plan .md file and drives Build (shell
    commands), Test (submit a plan via test_serv), and Verify (exec
    the inline check) for each `### ` section. Wraps the whole suite
    in a single bench-wide lease so no other agent can perturb the
    rig between tests."""

    FAST_DATA = Path(__file__).resolve().parent
    SUBMIT_PY = FAST_DATA / 'test_serv' / 'submit.py'
    SERVER = 'http://localhost:8080'
    WAIT_S = 600                     # generous upper bound
    LEASE_DEVICES = ('bench_mcu', 'dfu.evb', 'mp135.evb', 'ssh.target')
    LEASE_DURATION_S = 3600          # bench MAX_SESSION_S cap
    # Persists the active lease token across run.py invocations so a
    # crashed/killed run cannot leave a ghost lease on the bench.
    LEASE_STATE_FILE = FAST_DATA / '.runpy_lease'

    def __init__(self, md_path):
        self.md_path = Path(md_path)
        self.workdir = Path(tempfile.mkdtemp(prefix='runpy-'))
        self.log_path = Path.cwd() / 'log.txt'
        self.log_fh = None
        # Defensive: release any leftover lease from a prior crashed run.
        if self.LEASE_STATE_FILE.exists():
            ghost = self.LEASE_STATE_FILE.read_text().strip()
            if ghost:
                self.release_lease(ghost)
                print(f'released ghost lease {ghost}')
            self.LEASE_STATE_FILE.unlink()

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
        """Yield (title, build, artifacts, test, verify, test_max_s) per
        '### ' section. ``test_max_s`` is set from a per-block specifier
        like ``Test (max 5 min):``; None when omitted."""
        text = self.md_path.read_text()
        parts = re.split(r'^### (.+)$', text, flags=re.M)
        for i in range(1, len(parts), 2):
            title = parts[i].strip()
            body = parts[i + 1]
            blocks = {}
            specs = {}
            for label in ('Build', 'Artifacts', 'Test', 'Verify'):
                m = re.search(
                    rf'^{label}\s*(?:\(([^)]+)\))?\s*:\s*\n+```\n(.*?)\n```',
                    body, re.M | re.S)
                blocks[label.lower()] = m.group(2) if m else None
                specs[label.lower()] = m.group(1) if m else None
            yield (title, blocks['build'], blocks['artifacts'],
                   blocks['test'], blocks['verify'],
                   self.parse_max(specs['test']))

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
                    description, lease_token=None, max_s=None):
        """Resolve @blob refs from per-test Artifacts, submit. Prepends a
        `lease:resume` (when active), `description "..."`, and unique
        runpy comment to the plan. Returns (rc, digest). When ``max_s``
        is set, X-Test-Runtime caps the bench session at that budget;
        the agent backstops with a slightly larger subprocess timeout in
        case the bench fails to enforce."""
        plan_path = extract_dir.parent / 'plan.txt'
        pre = []
        if lease_token:
            pre.append(f'lease:resume token="{lease_token}"')
        pre.append(f'description "{description}"')
        pre.append(f'# runpy {time.time_ns()}')
        plan_path.write_text('\n'.join(pre) + '\n' + plan_text + '\n')
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
        with log.open('ab') as f:
            f.write(f'$ {" ".join(cmd)}\n'.encode())
            try:
                rc = subprocess.run(
                    cmd, cwd=self.FAST_DATA, stdout=f,
                    stderr=subprocess.STDOUT,
                    timeout=(max_s + 30) if max_s else None,
                ).returncode
            except subprocess.TimeoutExpired:
                f.write(b'  (agent watchdog: submit.py exceeded '
                        b'budget; killed)\n')
                rc = 1
        digest = None
        if extract_dir.exists():
            tars = list(extract_dir.glob('*.tar'))
            if tars:
                digest = tars[0].stem
        return rc, digest

    def run_verify(self, verify_text, artifacts, extract_dir):
        """Exec the verify block (with Verification + abs-path artifacts
        pre-injected) and return its check(extract_dir) bool."""
        if verify_text is None:
            return True
        abs_artifacts = {n: str(self.FAST_DATA / r)
                         for n, r in artifacts.items()}
        ns = {'Verification': Verification, 'artifacts': abs_artifacts}
        exec(verify_text, ns)
        if 'check' not in ns:
            raise RuntimeError("verify block defines no check()")
        return bool(ns['check'](str(extract_dir)))

    def claim_lease(self):
        """Submit a tiny plan that claims every bench device for the
        suite. Returns the token, or None on failure."""
        devs = ','.join(self.LEASE_DEVICES)
        plan = (f'description "lease setup"\n'
                f'lease:claim devices="{devs}" '
                f'duration_s={self.LEASE_DURATION_S}\n'
                f'mark tag=lease_setup\n')
        section = self.workdir / '_lease_setup'
        section.mkdir()
        extract = section / 'artefact'
        plan_path = section / 'plan.txt'
        plan_path.write_text(f'# runpy {time.time_ns()}\n' + plan)
        log = section / 'run.log'
        cmd = ['python3', str(self.SUBMIT_PY),
               '--server', self.SERVER,
               '--wait', '60',
               '--extract', str(extract),
               str(plan_path)]
        with log.open('wb') as f:
            rc = subprocess.run(cmd, cwd=self.FAST_DATA,
                                stdout=f,
                                stderr=subprocess.STDOUT).returncode
        if rc != 0:
            return None
        stream = extract / 'streams' / 'lease.token.bin'
        if not stream.exists():
            return None
        token = stream.read_text().strip()
        if not token:
            return None
        # Persist immediately so a crash before `finally`-release is
        # recoverable on next run.
        self.LEASE_STATE_FILE.write_text(token)
        return token

    def release_lease(self, token):
        """Submit a tiny plan that releases `token`. Best-effort.
        Always clears the persisted state file on the way out, so a
        retry-loop on a long-dead token doesn't keep firing forever."""
        plan = (f'lease:resume token="{token}"\n'
                f'description "lease teardown"\n'
                f'lease:release token="{token}"\n'
                f'mark tag=lease_teardown\n')
        section = self.workdir / f'_lease_teardown_{int(time.time()*1000)}'
        section.mkdir()
        extract = section / 'artefact'
        plan_path = section / 'plan.txt'
        plan_path.write_text(f'# runpy {time.time_ns()}\n' + plan)
        log = section / 'run.log'
        cmd = ['python3', str(self.SUBMIT_PY),
               '--server', self.SERVER,
               '--wait', '60',
               '--extract', str(extract),
               str(plan_path)]
        with log.open('wb') as f:
            subprocess.run(cmd, cwd=self.FAST_DATA,
                           stdout=f, stderr=subprocess.STDOUT)
        if self.LEASE_STATE_FILE.exists():
            self.LEASE_STATE_FILE.unlink()

    def delete_job(self, digest):
        if not digest:
            return
        req = urllib.request.Request(
            f'{self.SERVER}/outputs/{digest}', method='DELETE')
        try:
            urllib.request.urlopen(req, timeout=5).read()
        except Exception:
            pass

    def run_all(self):
        """Iterate sections in order. Per test prints
        `[i/N] [HH:MM:SS] title (<=Bs) ... build ... run ... check ... PASS|FAIL|SKIP (+Ts)`
        where B is the sum of timeout_ms in the plan (the upper bound
        on in-plan waits) and T is the actual elapsed. Halts on first
        FAIL after dumping the per-test log + any errors.log. Wraps
        the whole suite in a single bench-wide lease (released in
        finally). Sends DELETE /outputs/<digest> on PASS to cleanup
        the dashboard. Returns 0 on full pass."""
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

        lease_token = None
        try:
            lease_token = self.claim_lease()
            if lease_token:
                self._log(f'  lease claimed: {lease_token}')
            else:
                self._log('  lease claim FAILED; running without lease')

            skipped = 0
            for i, (title, build, artifacts_text, test, verify,
                    test_max_s) in enumerate(sections, 1):
                # Release the suite-wide lease before the final test so the
                # flagship runs lease-less and re-acquires every device from
                # cold (proves the no-context recovery path).
                if i == total and lease_token:
                    self.release_lease(lease_token)
                    self._log(f'  lease released before flagship: {lease_token}')
                    lease_token = None
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
                sys.stdout.write(
                    f'[{i:>{w}}/{total}] [{started}] {title} '
                    f'(<={budget:.0f}s) ... ')
                sys.stdout.flush()

                if build is not None and not build.strip().lower().startswith(
                        'nothing'):
                    stage('build')
                    if not self.run_build(build, log):
                        result(i, 'FAIL', title, el(), started, budget)
                        dump(log)
                        return 1
                if test is None:
                    result(i, 'SKIP', title, el(), started, budget)
                    skipped += 1
                    continue
                stage('run')
                rc, digest = self.submit_plan(test, artifacts, extract_dir,
                                              log, title, lease_token,
                                              test_max_s)
                if rc != 0:
                    result(i, 'FAIL', title, el(), started, budget)
                    dump(log)
                    return 1
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
            if lease_token:
                self.release_lease(lease_token)
                self._log(f'  lease released: {lease_token}')
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
