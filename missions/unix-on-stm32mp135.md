# Unix v7 running on Armv7

This mission ports the Seventh Edition Unix kernel and userland from
PDP-11 K&R C to C99 on Armv7-A, keeping `unix-v7-c99/tools/original-diffs.sh`
as the discipline ratchet: only function prototypes and type widenings
should change against the original `v7/usr/...` tree, with device drivers
and `arch/` machine-dependent code exempt. The work is staged simple to
complex: first the cross-compile and root image build cleanly, then the
kernel boots and reaches a shell under `qemu-system-arm -machine virt`,
and finally the same `unix` image boots on the STM32MP135 EVB through
the bench's DFU+UART path and reaches a shell over UART.

The two demonstrations share the `unix` ELF and `root.img` artefacts.
The only thing that changes between them is how the image is delivered
to the CPU and how its console is captured: a qemu wrapper for the
host-side sections, the existing `dfu.evb` + `mp135.evb:uart_*` path
(see `missions/ssh.md`) for the bench-side sections.

Every EVB section is self-contained: reset -> DFU-flash bootloader ->
hold at `> ` -> MSC-write a unix-flavoured SD image -> `two` ->
`jump` -> capture UART. No test_serv leases, no inherited device
state, no `{{LEASE_TOKEN}}` plumbing. Each section pays the full
cold-boot cost, which keeps the sections independently runnable and
reproducible.

The EVB delivery path reuses the bootloader's existing
`two` + `jump` flow that `ssh.md` already drives for Linux: `two`
copies kernel and (optional) DTB from a known MBR offset into DDR,
`jump` enters the loaded image. No new bootloader command is
needed. What is new is on the v7 side, all under `dev/`:

- An STM32 USART console driver (UART4 at `0x40010000`, the same
  port `ssh.md` captures over the bench FT2232H). The existing
  `dev/pl011.c` only drives qemu's PL011 at `0x09000000` and is
  unusable on the EVB; it stays in for `CONF=qemu_arm` and the
  EVB build picks `dev/stm32_usart.c` (or equivalent) instead.
- An SD/eMMC block driver so `unix` can mount its root from the
  same card the bootloader loaded it from. Qemu skates by on
  virtio; the EVB has no virtio block.
- An `sdcard.img` layout (built by `make sd-unix`) that fits both
  the bootloader's MBR-offset expectations and the v7 SD driver's
  root-fs expectations.

Drivers and `arch/` are exempt from the original-diffs ratchet
(the discipline only governs the portable kernel core), so this
scope is appropriate for the EVB phase.

### Tooling contract

Every host-side qemu section drives one wrapper:
`unix-v7-c99/tools/qemu-shell.sh`. Pinning its contract once here
prevents seven independently-derived versions:

    qemu-shell.sh <log-path> [<script-name>]

- `<log-path>` is the file to capture the qemu serial console into.
  The wrapper MUST truncate the file before launching qemu and MUST
  apply a hard wall-clock timeout (default 90 s, override via
  `QEMU_SHELL_TIMEOUT_S`).
- `<script-name>` (optional, default `shell`) selects a driver
  fixture at `unix-v7-c99/tools/qemu/<script-name>.expect`. Driver
  fixtures wait for `login:`, send `root\r`, wait for `# `, run the
  per-fixture command set, then send `sync\r` and `exit\r`.
- Wrapper exit status is irrelevant; verifiers read only the
  captured log. The wrapper is responsible for not leaving stale
  log content from a prior section visible to the verifier (the
  truncate above plus a fresh-mtime guarantee).
- Each section names its own log path and fixture so captures never
  collide.

The original-diffs ratchet uses a snapshot file at
`unix-v7-c99/tools/original-diffs.budget.json`, formatted as a
nested JSON dictionary: `{port_path: {"inserts": N, "deletes": N}}`.
The verifier accepts only *decreases* in either insertion or
deletion counts against the snapshot; growth requires an explicit
committed snapshot bump alongside the change. A missing snapshot is
a hard failure, not a bootstrap-and-pass.

The ratchet has **three** stacked checks, not just one:

1. **Counts** — both insertions (`>`) and deletions (`<`) per port
   file may only shrink. Counting inserts alone lets a worker
   hollow out function bodies for free; the C99 port should be
   approaching the V7 source, not retreating from it.
2. **Coverage** — every non-exempt port `.c`/`.h`/`.s` file under
   `cmd/`, `sys/`, `h/`, `include/`, `lib/`, `tools/`, or `conf/`
   whose basename matches a file under `unix-v7-c99/v7/` MUST
   appear in `tools/original-diffs.sh`. This closes the
   "structurally invisible" hole where files never seen by the
   diff command are implicitly exempt. **Each Manager pass that
   introduces or modifies such a file extends `tools/original-diffs.sh`
   and the snapshot in the same change** — the diff script is not
   a one-time enumeration; it grows with the port.
3. **Path-laundering** — every entry in the snapshot must point to
   an existing port file. A worker who renames `sys/main.c` to
   `dev/main.c` to escape the ratchet would leave a stale snapshot
   entry that fails this check.

Drivers (`dev/*`) and `arch/*` remain exempt by directory; the
discipline only governs the portable kernel core.

Build:

```
test -x unix-v7-c99/tools/qemu-shell.sh
test -d unix-v7-c99/tools/qemu
```

Artifacts:

```
unix-v7-c99/tools/qemu-shell.sh
```

Test: no hardware.

Verify:

```
import os
import re
from pathlib import Path

def check(extract_dir):
    wrapper = Path('unix-v7-c99/tools/qemu-shell.sh')
    if not wrapper.exists() or not os.access(wrapper, os.X_OK):
        return False
    text = wrapper.read_text()
    # Contract from the section above: <log-path> <script-name>,
    # truncates the log, applies a wall-clock timeout overridable
    # via QEMU_SHELL_TIMEOUT_S, and picks a fixture under
    # tools/qemu/<script-name>.expect.
    if not re.search(r'QEMU_SHELL_TIMEOUT_S', text):
        return False
    if not re.search(r':\s*>\s*"\$log_path"', text):
        return False
    if not re.search(r'tools/qemu/\$\{?script_name\}?\.expect|'
                     r'qemu/\$script_name\.expect', text):
        return False
    # Every fixture under tools/qemu/ must end with the Ctrl-A x
    # quit so happy-path sections don't sit on the timeout.
    for f in Path('unix-v7-c99/tools/qemu').glob('*.expect'):
        body = f.read_text()
        if 'send "\\x01x"' not in body or 'expect eof' not in body:
            return False
    return True
```

### Cross-compile gate: `unix` ELF and `root.img` build clean

Smallest meaningful step: prove the C99 cross build still works after
each change to kernel or userland. No qemu, no hardware. Verifier
checks that `unix` is a statically linked Armv7 ELF executable with a
plausible entry point in `.text`, and that `root.img` has the V7
superblock magic and contains the canonical boot inodes
(`/etc/init`, `/bin/sh`, `/bin/login`).

Build:

```
make -C unix-v7-c99 clean
make -C unix-v7-c99 ARCH=arm CONF=qemu_arm
```

Artifacts:

```
unix-v7-c99/unix
unix-v7-c99/root.img
```

Test: no hardware.

Verify:

```
from pathlib import Path
import struct

def check(extract_dir):
    unix = Path('unix-v7-c99/unix').read_bytes()
    if unix[:4] != b'\x7fELF' or unix[4] != 1:
        return False
    e_machine = struct.unpack('<H', unix[18:20])[0]
    if e_machine != 0x28:  # EM_ARM
        return False
    img = Path('unix-v7-c99/root.img').read_bytes()
    if len(img) < 8192:
        return False
    # V7 superblock lives in block 1; s_magic / sane s_isize sanity check.
    s_isize = struct.unpack('<H', img[512:514])[0]
    s_fsize = struct.unpack('<H', img[514:516])[0]
    return 0 < s_isize < s_fsize <= len(img) // 512
```

### Original-diffs discipline holds (snapshot ratchet)

Run `unix-v7-c99/tools/original-diffs.sh` and compare per-file
insertion AND deletion counts against the committed snapshot at
`unix-v7-c99/tools/original-diffs.budget.json`, then verify that
every non-exempt port file with a V7 ancestor is tracked, then
verify that the snapshot has no stale entries. The three checks
together rule out gradual drift, hollowed-out functions, brand-new
files smuggled in without a v7 counterpart, and path-laundering
renames intended to escape the ratchet.

Drivers (`dev/*`) and `arch/*` are exempt by directory; everything
else under `cmd/`, `sys/`, `h/`, `include/`, `lib/`, `tools/`, and
`conf/` is in scope.

Build:

```
mkdir -p unix-v7-c99/build
cd unix-v7-c99 && tools/original-diffs.sh > build/original-diffs.out
```

Artifacts:

```
unix-v7-c99/build/original-diffs.out
unix-v7-c99/tools/original-diffs.budget.json
```

Test: no hardware.

Verify:

```
from pathlib import Path
import json
import re

EXEMPT_PREFIXES = ('dev/', 'arch/')
PORT_DIRS = ('cmd', 'sys', 'h', 'include', 'lib', 'tools', 'conf')
SRC_SUFFIXES = ('.c', '.h', '.s')

def check(extract_dir):
    out_path  = Path('unix-v7-c99/build/original-diffs.out')
    snap_path = Path('unix-v7-c99/tools/original-diffs.budget.json')
    if not out_path.exists() or not snap_path.exists():
        return False              # the ratchet is itself a discipline gate
    snap = json.loads(snap_path.read_text())

    # Parse: each `diff <v7> <port>` opens a tracked pair; subsequent
    # lines starting with '> ' are insertions in the port, '< ' are
    # deletions vs. the V7 reference.
    inserts, deletes, pair = {}, {}, {}
    current = None
    for line in out_path.read_text().splitlines():
        m = re.match(r'^diff (\S+) (\S+)$', line)
        if m:
            current = m.group(2)
            pair[current] = m.group(1)
            inserts.setdefault(current, 0)
            deletes.setdefault(current, 0)
            continue
        if current and line.startswith('> '):
            inserts[current] += 1
        elif current and line.startswith('< '):
            deletes[current] += 1

    # 1. Counts: per-file inserts AND deletes may only shrink.
    for f in inserts:
        if any(f.startswith(p) for p in EXEMPT_PREFIXES):
            continue
        budget = snap.get(f) or {}
        if not isinstance(budget, dict):
            return False
        if inserts[f] > budget.get('inserts', 0):
            return False
        if deletes[f] > budget.get('deletes', 0):
            return False

    # 2. Coverage: every non-exempt port .c/.h/.s under PORT_DIRS whose
    #    basename matches a file under v7/ must appear in the ratchet.
    v7_root = Path('unix-v7-c99/v7')
    v7_basenames = set()
    if v7_root.exists():
        for p in v7_root.rglob('*'):
            if p.is_file() and p.suffix in SRC_SUFFIXES:
                v7_basenames.add(p.name)
    tracked = set(pair.keys())
    for d in PORT_DIRS:
        root = Path('unix-v7-c99') / d
        if not root.exists():
            continue
        for p in root.rglob('*'):
            if not p.is_file() or p.suffix not in SRC_SUFFIXES:
                continue
            rel = str(p.relative_to(Path('unix-v7-c99')))
            if any(rel.startswith(prefix) for prefix in EXEMPT_PREFIXES):
                continue
            if p.name in v7_basenames and rel not in tracked:
                return False      # untracked file with V7 ancestor

    # 3. Path-laundering: every snapshot entry must point to an existing
    #    port file. Catches renames into exempt dirs.
    for f in snap:
        if not (Path('unix-v7-c99') / f).exists():
            return False

    return True
```

### Kernel reaches startup banner under Qemu

First boot gate. Runs `qemu-system-arm -machine virt -cpu cortex-a7
-nographic` against the freshly built `unix`, with `root.img`
attached as a virtio block device, and captures the serial console
to a log file with a hard timeout. Verifier requires that the
captured log contains the V7 "mem = " banner (printed from
`sys/main.c` after `iinit`) and the early panic-free path through
`main()`. Drives no input; this only proves the kernel reaches
userspace-prep without faulting.

Build:

```
make -C unix-v7-c99 ARCH=arm CONF=qemu_arm
mkdir -p unix-v7-c99/build/qemu
rm -f unix-v7-c99/build/qemu/banner.log
timeout 30 qemu-system-arm \
    -machine virt -cpu cortex-a7 -nographic -no-reboot \
    -kernel unix-v7-c99/unix \
    -drive if=none,file=unix-v7-c99/root.img,format=raw,id=hd0 \
    -device virtio-blk-device,drive=hd0 \
    -serial file:unix-v7-c99/build/qemu/banner.log \
    < /dev/null || true
test -s unix-v7-c99/build/qemu/banner.log
```

Artifacts:

```
unix-v7-c99/build/qemu/banner.log
```

Test: no hardware.

Verify:

```
from pathlib import Path
import re

def check(extract_dir):
    log = Path('unix-v7-c99/build/qemu/banner.log').read_text(
        errors='replace')
    if 'panic' in log.lower():
        return False
    # Tightened against a stub printf: mem must be a non-zero
    # multi-digit byte count, not literally "mem = 0".
    return bool(re.search(r'mem = [1-9]\d{2,}', log))
```

### Kernel mounts root and execs init under Qemu

Extends the qemu boot: same invocation, longer timeout, capture must
reach the `init` exec path and the first `getty` opening
`/dev/console`. Catches `bio`, `namei`, and `exec` regressions
together. Still drives no input.

Build:

```
make -C unix-v7-c99 ARCH=arm CONF=qemu_arm
mkdir -p unix-v7-c99/build/qemu
rm -f unix-v7-c99/build/qemu/init.log
timeout 60 qemu-system-arm \
    -machine virt -cpu cortex-a7 -nographic -no-reboot \
    -kernel unix-v7-c99/unix \
    -drive if=none,file=unix-v7-c99/root.img,format=raw,id=hd0 \
    -device virtio-blk-device,drive=hd0 \
    -serial file:unix-v7-c99/build/qemu/init.log \
    < /dev/null || true
test -s unix-v7-c99/build/qemu/init.log
```

Artifacts:

```
unix-v7-c99/build/qemu/init.log
```

Test: no hardware.

Verify:

```
from pathlib import Path
import re

def check(extract_dir):
    log = Path('unix-v7-c99/build/qemu/init.log').read_text(
        errors='replace')
    if 'panic' in log.lower():
        return False
    # Banner must arrive before login: (rules out a stub that prints
    # "login:" without ever booting the kernel) and the byte count
    # must be plausibly non-zero.
    try:
        i_mem = log.index('mem = ')
        log.index('login:', i_mem)
    except ValueError:
        return False
    return bool(re.search(r'mem = [1-9]\d{2,}', log))
```

### Login and shell prompt under Qemu

First interactive section. Drives the qemu serial console through an
`expect` (or `socat`-piped) wrapper that sends `root\r` at `login:`,
waits for `# `, runs `echo unix-v7-armv7-ok`, then `sync; exit`.
Verifier requires the echoed sentinel and a clean shell exit in the
capture. Catches tty discipline, signal, and shell exec regressions.

Build:

```
make -C unix-v7-c99 ARCH=arm CONF=qemu_arm
mkdir -p unix-v7-c99/build/qemu
rm -f unix-v7-c99/build/qemu/shell.log
unix-v7-c99/tools/qemu-shell.sh unix-v7-c99/build/qemu/shell.log shell
test -s unix-v7-c99/build/qemu/shell.log
```

Artifacts:

```
unix-v7-c99/build/qemu/shell.log
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(extract_dir):
    log = Path('unix-v7-c99/build/qemu/shell.log').read_text(
        errors='replace')
    if 'panic' in log.lower():
        return False
    # Position-anchored: login -> # prompt -> typed echo command ->
    # echo's *output* (a second occurrence of the sentinel after
    # the input echo). Rules out a kernel printf that just prints
    # the sentinel string.
    try:
        i_login  = log.index('login:')
        i_prompt = log.index('# ', i_login)
        i_typed  = log.index('echo unix-v7-armv7-ok', i_prompt)
        log.index('unix-v7-armv7-ok',
                  i_typed + len('echo unix-v7-armv7-ok'))
    except ValueError:
        return False
    return True
```

### Userland smoke set under Qemu

Drives the live shell from the previous section's setup through a
small but representative command set: `pwd`, `ls /bin`, `cat
/etc/passwd`, `wc /etc/passwd`, `echo $$`. Catches userspace stdio,
argv handling, and basic syscall regressions that the bare login
gate misses.

Build:

```
make -C unix-v7-c99 ARCH=arm CONF=qemu_arm
mkdir -p unix-v7-c99/build/qemu
rm -f unix-v7-c99/build/qemu/smoke.log
unix-v7-c99/tools/qemu-shell.sh unix-v7-c99/build/qemu/smoke.log smoke
test -s unix-v7-c99/build/qemu/smoke.log
```

Artifacts:

```
unix-v7-c99/build/qemu/smoke.log
```

Test: no hardware.

Verify:

```
from pathlib import Path
import re

def check(extract_dir):
    log = Path('unix-v7-c99/build/qemu/smoke.log').read_text(
        errors='replace')
    if 'panic' in log.lower():
        return False
    # Each grep is anchored to text that follows a shell prompt,
    # so an unrelated printf in the kernel cannot satisfy any of
    # the gates on its own.
    try:
        i_prompt = log.index('# ')
        tail = log[i_prompt:]
    except ValueError:
        return False
    if not re.search(r'^/\s*$', tail, re.M):
        return False              # pwd output
    if 'root:' not in tail:
        return False              # cat /etc/passwd
    if not re.search(r'\b\d+\s+\d+\s+\d+ /etc/passwd', tail):
        return False              # wc /etc/passwd
    return 'sh' in tail and 'login' in tail  # ls /bin had the basics
```

### Pipes and redirection under Qemu

Drives the live shell through a focused pipe/redirect script.
Tests `pipe(2)`, `dup(2)`, `>` / `>>` on a fresh file, `<` from
an existing file, multi-stage pipelines, and exit-status
propagation through the last stage. These paths are kernel-side
(file table, dup, pipe inode) and shell-side (here-docs,
pipeline reaping); both can break independently and the smoke
set above does not exercise either.

Build:

```
make -C unix-v7-c99 ARCH=arm CONF=qemu_arm
mkdir -p unix-v7-c99/build/qemu
rm -f unix-v7-c99/build/qemu/pipes.log
unix-v7-c99/tools/qemu-shell.sh unix-v7-c99/build/qemu/pipes.log pipes
test -s unix-v7-c99/build/qemu/pipes.log
```

Artifacts:

```
unix-v7-c99/build/qemu/pipes.log
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(extract_dir):
    log = Path('unix-v7-c99/build/qemu/pipes.log').read_text(
        errors='replace')
    if 'panic' in log.lower() or 'cmp:' in log.lower():
        return False
    # Driver script does, in order, all after the shell prompt:
    #   echo hello | wc -c                     -> '6'
    #   cat /etc/passwd > /tmp/p
    #   cmp /etc/passwd /tmp/p; echo CMPOK
    #   (echo one; echo two) | tail -1; echo PIPESOK
    # CMPOK and PIPESOK are emitted only on success, in that order,
    # AFTER the shell prompt. Rules out planted strings.
    try:
        i_prompt = log.index('# ')
        i_cmp    = log.index('CMPOK', i_prompt)
        i_two    = log.index('two', i_cmp)
        log.index('PIPESOK', i_two)
    except ValueError:
        return False
    return True
```

### Filesystem mutation round-trip under Qemu

Exercises the create/link/unlink paths the read-only smoke set
skips: `mkdir`, `touch`, write via `>`, `cp`, `ln`, `mv`, `rm`,
`rmdir`, `chmod`. Round-trips a freshly created tree under `/tmp`
through every op and back to empty, checking link counts and
modes along the way. Catches `bio` writeback, `iget`/`iput`, and
directory-namei regressions that read-only paths mask.

Build:

```
make -C unix-v7-c99 ARCH=arm CONF=qemu_arm
mkdir -p unix-v7-c99/build/qemu
rm -f unix-v7-c99/build/qemu/fsmut.log
unix-v7-c99/tools/qemu-shell.sh unix-v7-c99/build/qemu/fsmut.log fsmut
test -s unix-v7-c99/build/qemu/fsmut.log
```

Artifacts:

```
unix-v7-c99/build/qemu/fsmut.log
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(extract_dir):
    log = Path('unix-v7-c99/build/qemu/fsmut.log').read_text(
        errors='replace')
    if 'panic' in log.lower() or 'cannot' in log.lower():
        return False
    # Driver script does, in order, all after the shell prompt:
    #   mkdir /tmp/d; echo hi > /tmp/d/f; cat /tmp/d/f         -> 'hi'
    #   ln /tmp/d/f /tmp/d/g; ls /tmp/d                        -> 'f','g'
    #   chmod 600 /tmp/d/f; ls -l /tmp/d/f                     -> 'rw-------'
    #   mv /tmp/d/g /tmp/d/h; rm /tmp/d/f /tmp/d/h; rmdir /tmp/d
    #   echo FSOK
    try:
        i_prompt = log.index('# ')
        i_hi     = log.index('hi', i_prompt)
        i_mode   = log.index('rw-------', i_hi)
        log.index('FSOK', i_mode)
    except ValueError:
        return False
    return True
```

### Tty line discipline (sgtty) under Qemu

Exercises V7's pre-termios sgtty interface: `dev/tty.c`,
`include/sgtty.h`, `cmd/stty.c`, `cmd/tabs.c`. Catches:
cooked/raw mode regressions, `^D` EOF delivery, line-erase /
line-kill characters, tab expansion. Modern Unix tests skip this
because everyone's on termios; V7 explicitly is not, and a port
that drifts to termios-only behaviour breaks distinguishing 1979
behaviour. The fixture cannot test BREAK over a pty (qemu virt's
serial does not propagate it) -- that gate moves to the EVB
phase where a real UART is wired up.

Build:

```
make -C unix-v7-c99 ARCH=arm CONF=qemu_arm
mkdir -p unix-v7-c99/build/qemu
rm -f unix-v7-c99/build/qemu/sgtty.log
unix-v7-c99/tools/qemu-shell.sh unix-v7-c99/build/qemu/sgtty.log sgtty
test -s unix-v7-c99/build/qemu/sgtty.log
```

Artifacts:

```
unix-v7-c99/build/qemu/sgtty.log
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(extract_dir):
    log = Path('unix-v7-c99/build/qemu/sgtty.log').read_text(
        errors='replace')
    if 'panic' in log.lower():
        return False
    # Driver script does, in order, all after the shell prompt:
    #   stty -a; echo STTYDUMPOK
    #   stty raw; stty -a; stty cooked; echo RAWCOOKEDOK
    #   tabs 4; echo TABSOK
    #   (a `cat` reading from /dev/tty receives ^D and exits cleanly)
    #   echo SGTTYOK
    # The stty -a dump must contain a recognisable V7 setting like
    # 'erase' or 'speed', not just an empty line.
    try:
        i_prompt = log.index('# ')
        i_dump   = log.index('STTYDUMPOK',     i_prompt)
        i_raw    = log.index('RAWCOOKEDOK',    i_dump)
        i_tabs   = log.index('TABSOK',         i_raw)
        log.index('SGTTYOK', i_tabs)
    except ValueError:
        return False
    head = log[i_prompt:i_dump]
    return ('erase' in head.lower() or 'speed' in head.lower()
            or 'baud' in head.lower())
```

### Signals and tty interrupts under Qemu

Drives the live shell through V7's signal facility (`sys/sig.c`,
`include/signal.h`): `trap` in sh, `kill -HUP $$` (the canonical
1979 dial-up hangup), `kill -INT` to a long-running cat, `alarm`+
`pause` via a small C helper, and `signal(SIGINT, SIG_IGN)`
inheritance across `fork+exec`. Catches the bulk of `sig.c`,
not just the one `kill -TERM` exercised by the proc section.

Build:

```
make -C unix-v7-c99 ARCH=arm CONF=qemu_arm
mkdir -p unix-v7-c99/build/qemu
rm -f unix-v7-c99/build/qemu/signals.log
unix-v7-c99/tools/qemu-shell.sh unix-v7-c99/build/qemu/signals.log signals
test -s unix-v7-c99/build/qemu/signals.log
```

Artifacts:

```
unix-v7-c99/build/qemu/signals.log
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(extract_dir):
    log = Path('unix-v7-c99/build/qemu/signals.log').read_text(
        errors='replace')
    if 'panic' in log.lower():
        return False
    # Driver script does, in order, all after the shell prompt:
    #   trap 'echo HUPGOT' 1; (sleep 1; kill -HUP $$) ; echo HUPSEQOK
    #   (sleep 5 & PID=$!; kill -INT $PID; wait); echo INTSEQOK
    #   trap '' 2; echo SIGIGNOK
    #   trap 2 ; echo TRAPRESETOK
    #   echo SIGSOK
    try:
        i_prompt = log.index('# ')
        i_hup    = log.index('HUPGOT',       i_prompt)
        i_hupseq = log.index('HUPSEQOK',     i_hup)
        i_int    = log.index('INTSEQOK',     i_hupseq)
        i_sigign = log.index('SIGIGNOK',     i_int)
        i_reset  = log.index('TRAPRESETOK',  i_sigign)
        log.index('SIGSOK', i_reset)
    except ValueError:
        return False
    return True
```

### Text-processing pipelines under Qemu

Drives a richer pipeline workout against `/etc/passwd` and
`/usr/dict/words`: `tr`, `sort`, `uniq`, `grep`, `head`, `tail`,
`wc`, `od`. Each command is a distinct user binary and the
combinations stress stdio buffering, large reads, and `sort`'s
temp-file path through `bio`. Catches userspace stdio
regressions and sort's tmpfile creation under load.

Build:

```
make -C unix-v7-c99 ARCH=arm CONF=qemu_arm
mkdir -p unix-v7-c99/build/qemu
rm -f unix-v7-c99/build/qemu/textproc.log
unix-v7-c99/tools/qemu-shell.sh unix-v7-c99/build/qemu/textproc.log textproc
test -s unix-v7-c99/build/qemu/textproc.log
```

Artifacts:

```
unix-v7-c99/build/qemu/textproc.log
```

Test: no hardware.

Verify:

```
from pathlib import Path
import re

def check(extract_dir):
    log = Path('unix-v7-c99/build/qemu/textproc.log').read_text(
        errors='replace')
    if 'panic' in log.lower():
        return False
    # Driver script does, in order, all after the shell prompt:
    #   grep root /etc/passwd | wc -l                  -> '1'
    #   tr a-z A-Z < /etc/passwd | head -1             -> 'ROOT:...'
    #   sort /etc/passwd | uniq | wc -l                -> integer
    #   wc -l /usr/dict/words                          -> big integer
    #   echo TEXTPROCOK
    try:
        i_prompt = log.index('# ')
        tail = log[i_prompt:]
        m = re.search(r'^ROOT:', tail, re.M)
        if not m:
            return False
        i_root  = m.start()
        tail.index('TEXTPROCOK', i_root)
    except ValueError:
        return False
    return True
```

### Process control and signals under Qemu

Exercises `fork`, `wait`, `kill`, and exit-status propagation
through the shell. Spawns a backgrounded `sleep`, waits on it,
sends `kill -0` and `kill -TERM`, checks `$?` round-trips through
a pipeline, and confirms `time` reports a sane wall/sys/user
split. Catches `slp.c`, `sig.c`, and shell job-control
regressions that the redirect-only sections mask.

Build:

```
make -C unix-v7-c99 ARCH=arm CONF=qemu_arm
mkdir -p unix-v7-c99/build/qemu
rm -f unix-v7-c99/build/qemu/proc.log
unix-v7-c99/tools/qemu-shell.sh unix-v7-c99/build/qemu/proc.log proc
test -s unix-v7-c99/build/qemu/proc.log
```

Artifacts:

```
unix-v7-c99/build/qemu/proc.log
```

Test: no hardware.

Verify:

```
from pathlib import Path
import re

def check(extract_dir):
    log = Path('unix-v7-c99/build/qemu/proc.log').read_text(
        errors='replace')
    if 'panic' in log.lower():
        return False
    # Driver script does, in order, all after the shell prompt:
    #   sleep 1 & echo PID=$!
    #   wait; echo WAITOK
    #   (exit 7); echo RC=$?
    #   time sleep 1; echo TIMEOK
    #   echo PROCOK
    try:
        i_prompt = log.index('# ')
        tail = log[i_prompt:]
        m = re.search(r'PID=\d+', tail)
        if not m:
            return False
        i_pid  = m.start()
        i_wait = tail.index('WAITOK', i_pid)
        i_rc   = tail.index('RC=7',   i_wait)
        i_time = tail.index('TIMEOK', i_rc)
        tail.index('PROCOK', i_time)
    except ValueError:
        return False
    return True
```

### `dd` raw I/O round-trip under Qemu

Uses `dd` with mismatched block sizes to exercise the raw
read/write paths: read `/etc/passwd` byte-by-byte (`bs=1`) into
`/tmp/a`, then again with `bs=512 count=1` into `/tmp/b`, and
finally `cmp /tmp/a /etc/passwd`. Catches alignment and short-read
regressions in `rdwri.c` that block-aligned reads (cat, ls)
silently round.

Build:

```
make -C unix-v7-c99 ARCH=arm CONF=qemu_arm
mkdir -p unix-v7-c99/build/qemu
rm -f unix-v7-c99/build/qemu/dd.log
unix-v7-c99/tools/qemu-shell.sh unix-v7-c99/build/qemu/dd.log dd
test -s unix-v7-c99/build/qemu/dd.log
```

Artifacts:

```
unix-v7-c99/build/qemu/dd.log
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(extract_dir):
    log = Path('unix-v7-c99/build/qemu/dd.log').read_text(
        errors='replace')
    if 'panic' in log.lower() or 'cmp:' in log.lower():
        return False
    # Driver script does, in order, all after the shell prompt:
    #   dd if=/etc/passwd of=/tmp/a bs=1
    #   dd if=/etc/passwd of=/tmp/b bs=512 count=1
    #   cmp /tmp/a /etc/passwd; echo CMPA=$?
    #   echo DDOK
    try:
        i_prompt = log.index('# ')
        i_cmpa   = log.index('CMPA=0', i_prompt)
        log.index('DDOK', i_cmpa)
    except ValueError:
        return False
    return True
```

### Mount and umount round-trip under Qemu

Exercises the V7 `smount` / `sumount` syscalls (21/22) and the
`bio` writeback path under a real fs lifecycle: build a fresh
auxiliary fs image with `/etc/mkfs` (compiled from
`v7/usr/src/cmd/mkfs.c` for the target -- adding it to ROOT is
part of this section's Manager work), `mknod` an auxiliary block
device backed by a second virtio-blk-device, `mount` it, write a
file, `sync`, `umount`, remount, read the file back. Catches:
`bio` writeback ordering, mount-table races, inode-number
collisions across mount points, and the `getfs` lookup that
ssh-shaped fs tests skip entirely.

Build:

```
make -C unix-v7-c99 ARCH=arm CONF=qemu_arm
mkdir -p unix-v7-c99/build/qemu
rm -f unix-v7-c99/build/qemu/aux.img unix-v7-c99/build/qemu/mount.log
dd if=/dev/zero of=unix-v7-c99/build/qemu/aux.img bs=512 count=128
unix-v7-c99/tools/qemu-shell.sh unix-v7-c99/build/qemu/mount.log mount
test -s unix-v7-c99/build/qemu/mount.log
```

Artifacts:

```
unix-v7-c99/build/qemu/aux.img
unix-v7-c99/build/qemu/mount.log
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(extract_dir):
    log = Path('unix-v7-c99/build/qemu/mount.log').read_text(
        errors='replace')
    if 'panic' in log.lower():
        return False
    # Driver script does, in order, all after the shell prompt:
    #   mknod /dev/aux b <maj> <min>
    #   /etc/mkfs /dev/aux 64 16; echo MKFSOK
    #   mkdir /aux; mount /dev/aux /aux; echo MOUNTOK
    #   echo "round-trip survives" > /aux/hi; sync; echo WRITEOK
    #   umount /aux; echo UMOUNTOK
    #   mount /dev/aux /aux; cat /aux/hi; echo MNTROUNDTRIPOK
    try:
        i_prompt = log.index('# ')
        i_mkfs   = log.index('MKFSOK',          i_prompt)
        i_mount  = log.index('MOUNTOK',         i_mkfs)
        i_write  = log.index('WRITEOK',         i_mount)
        i_umount = log.index('UMOUNTOK',        i_write)
        i_round  = log.index('round-trip survives', i_umount)
        log.index('MNTROUNDTRIPOK', i_round)
    except ValueError:
        return False
    return True
```

### Filesystem integrity (icheck/dcheck/ncheck) under Qemu

Runs V7's fsck-equivalents -- `icheck`, `dcheck`, `ncheck` --
against the rootfs and the auxiliary fs from the previous
section. These are *the* V7 fs-consistency story; they were
historically the on-disk-correctness gate before fsck unified
them, and the mission has not exercised them at all until now.
Catches: free-block-list leaks, allocated-but-unreferenced
inodes, broken directory backlinks. Read-only.

Build:

```
make -C unix-v7-c99 ARCH=arm CONF=qemu_arm
mkdir -p unix-v7-c99/build/qemu
rm -f unix-v7-c99/build/qemu/fscheck.log
unix-v7-c99/tools/qemu-shell.sh unix-v7-c99/build/qemu/fscheck.log fscheck
test -s unix-v7-c99/build/qemu/fscheck.log
```

Artifacts:

```
unix-v7-c99/build/qemu/fscheck.log
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(extract_dir):
    log = Path('unix-v7-c99/build/qemu/fscheck.log').read_text(
        errors='replace')
    if 'panic' in log.lower():
        return False
    # Driver script does, in order, all after the shell prompt:
    #   sync; icheck /dev/rrl0 ; echo ICHECKOK
    #   dcheck /dev/rrl0       ; echo DCHECKOK
    #   ncheck /dev/rrl0 | grep -q /etc/passwd ; echo NCHECKOK
    #   echo FSCHECKOK
    # icheck output should contain a "files" or "blocks" header
    # rather than an unstructured stub; ncheck must surface
    # /etc/passwd which we know exists in the rootfs.
    try:
        i_prompt = log.index('# ')
        i_ichk   = log.index('ICHECKOK', i_prompt)
        i_dchk   = log.index('DCHECKOK', i_ichk)
        i_nchk   = log.index('NCHECKOK', i_dchk)
        log.index('FSCHECKOK', i_nchk)
    except ValueError:
        return False
    head = log[i_prompt:i_ichk]
    return any(tok in head.lower()
               for tok in ('files', 'blocks', 'used', 'free'))
```

### V7 utility breadth under Qemu

The mission's earlier sections exercise roughly 25 of the ~70+
binaries the Makefile bundles into ROOT. This fixture invokes
each remaining V7 utility at least once with a recognisable
sentinel: `who`, `mesg`, `write`, `wall`, `calendar`, `crypt`,
`makekey`, `random`, `stty`, `tabs`, `tty`, `df`, `du`,
`mknod`, `file`, `join`, `col`, `fgrep`, `cb`, `sp`, `time`,
`comm`, `tsort`, `checkeq`, `pr`, `split`, `sum`, `look`,
`chown`, `chgrp`, `nice`. Catches: bare exec failures, missing
shared dependencies, link-time regressions in less-used
binaries that would otherwise only surface when a user
actually runs them.

Build:

```
make -C unix-v7-c99 ARCH=arm CONF=qemu_arm
mkdir -p unix-v7-c99/build/qemu
rm -f unix-v7-c99/build/qemu/breadth.log
unix-v7-c99/tools/qemu-shell.sh unix-v7-c99/build/qemu/breadth.log breadth
test -s unix-v7-c99/build/qemu/breadth.log
```

Artifacts:

```
unix-v7-c99/build/qemu/breadth.log
```

Test: no hardware.

Verify:

```
from pathlib import Path

UTILS = (
    'who', 'mesg', 'write', 'wall', 'calendar', 'crypt', 'makekey',
    'random', 'stty', 'tabs', 'tty', 'df', 'du', 'mknod', 'file',
    'join', 'col', 'fgrep', 'cb', 'sp', 'time', 'comm', 'tsort',
    'checkeq', 'pr', 'split', 'sum', 'look', 'chown', 'chgrp',
    'nice',
)

def check(extract_dir):
    log = Path('unix-v7-c99/build/qemu/breadth.log').read_text(
        errors='replace')
    if 'panic' in log.lower():
        return False
    # Driver script invokes each utility and emits, in order:
    #   <name>:OK
    # after a successful run. The fixture is responsible for
    # constructing reasonable inputs (e.g. `tsort < /dev/null`,
    # `look root /usr/dict/words`); a failed exit emits
    # <name>:FAIL instead. Verifier requires every name in the
    # OK form, in the order listed in UTILS.
    pos = 0
    for name in UTILS:
        marker = f'{name}:OK'
        i = log.find(marker, pos)
        if i < 0:
            return False
        pos = i + len(marker)
    return True
```

### V7-isms under Qemu

Tests the 1979 behaviours that are NOT modern-Unix behaviours:
14-character filename truncation (the V7 `DIRSIZ`), V7's
`mknod`/`stat` device-number layout (one-byte major + one-byte
minor packed into a 16-bit `dev_t`), V7 sh's lack of `$(...)`
syntax (only backticks), `umask` syscall (60), and the sticky
bit. Catches the silent modernization-creep that would otherwise
make the port functionally indistinguishable from a modern
minimal Unix.

Build:

```
make -C unix-v7-c99 ARCH=arm CONF=qemu_arm
mkdir -p unix-v7-c99/build/qemu
rm -f unix-v7-c99/build/qemu/v7isms.log
unix-v7-c99/tools/qemu-shell.sh unix-v7-c99/build/qemu/v7isms.log v7isms
test -s unix-v7-c99/build/qemu/v7isms.log
```

Artifacts:

```
unix-v7-c99/build/qemu/v7isms.log
```

Test: no hardware.

Verify:

```
from pathlib import Path
import re

def check(extract_dir):
    log = Path('unix-v7-c99/build/qemu/v7isms.log').read_text(
        errors='replace')
    if 'panic' in log.lower():
        return False
    # Driver script does, in order, all after the shell prompt:
    #   touch /tmp/aaaaaaaaaaaaaaa     # 15 chars; V7 truncates to 14
    #   ls /tmp/aaaaaaaaaaaaaa         # 14 chars; must list it
    #   echo V7TRUNCOK
    #   mknod /tmp/cdev c 5 7; ls -l /tmp/cdev
    #   echo V7MKNODOK
    #   umask 022; touch /tmp/u; ls -l /tmp/u  # mode 644 => '-rw-r--r--'
    #   echo V7UMASKOK
    #   echo $(echo dollarparens)      # V7 sh: literal output, not exec
    #   echo V7SHSYNTAXOK
    #   echo V7ISMSOK
    try:
        i_prompt = log.index('# ')
        i_trunc  = log.index('V7TRUNCOK',     i_prompt)
        i_mknod  = log.index('V7MKNODOK',     i_trunc)
        i_umask  = log.index('V7UMASKOK',     i_mknod)
        i_sh     = log.index('V7SHSYNTAXOK',  i_umask)
        log.index('V7ISMSOK', i_sh)
    except ValueError:
        return False
    # Mode must be V7-shaped 'rw-r--r--' (umask check)
    if 'rw-r--r--' not in log[i_mknod:i_umask]:
        return False
    # mknod -l output: V7 stat shows the device number as
    # "5,   7" (two values separated by comma+spaces), not a
    # single composite number.
    if not re.search(r'\b5,\s+7\b', log[i_trunc:i_mknod]):
        return False
    # V7 sh does not expand $(...). The literal '$(echo ' must
    # appear in the output of the dollar-paren echo line.
    if '$(echo' not in log[i_umask:i_sh]:
        return False
    return True
```

### Multi-user login + su + setuid + utmp under Qemu

Proves V7's distinguishing multi-user behaviour: a non-root
user logs in via `getty`+`login` against a hashed password,
gets a `$ ` shell (not `# `), `who am i` reports them in
`/etc/utmp`, `su root` escalates uid back to 0, and a setuid
program inherits its file owner's effective uid. Build amends
`root/etc/passwd` to seed user `dmr` with a DES `crypt(3)`
hash and removes the Makefile's `/etc/utmp=/dev/null` shim.
Catches: `login`/`getty` regressions hidden by the
single-root-no-password path every other section drives, the
setuid-bit semantics in `sys/exec.c`, and the utmp/wtmp
accounting ssh.md tests do not touch.

Build:

```
make -C unix-v7-c99 ARCH=arm CONF=qemu_arm
mkdir -p unix-v7-c99/build/qemu
rm -f unix-v7-c99/build/qemu/multiuser.log
unix-v7-c99/tools/qemu-shell.sh unix-v7-c99/build/qemu/multiuser.log multiuser
test -s unix-v7-c99/build/qemu/multiuser.log
```

Artifacts:

```
unix-v7-c99/build/qemu/multiuser.log
```

Test: no hardware.

Verify:

```
from pathlib import Path
import re

def check(extract_dir):
    log = Path('unix-v7-c99/build/qemu/multiuser.log').read_text(
        errors='replace')
    if 'panic' in log.lower():
        return False
    # Driver script does, in order:
    #   waits for `login:`
    #   sends `dmr\r` then password `\r`
    #   waits for `$ `   (V7 non-root prompt)
    #   runs: who am i ; echo WHOAMIOK
    #   runs: id        ; echo NONROOTOK     (must show non-zero uid)
    #   runs: su root <\r> <root-password> ; echo SUOK
    #   waits for `# `  (V7 root prompt)
    #   runs: id        ; echo ROOTOK         (must show uid=0)
    #   runs: a setuid helper that prints its euid; echo SETUIDOK
    try:
        i_login   = log.index('login:')
        i_dmr     = log.index('dmr',           i_login)
        i_dollar  = log.index('$ ',            i_dmr)
        i_whoami  = log.index('WHOAMIOK',      i_dollar)
        i_nonroot = log.index('NONROOTOK',     i_whoami)
        i_su      = log.index('SUOK',          i_nonroot)
        i_hash    = log.index('# ',            i_su)
        i_root    = log.index('ROOTOK',        i_hash)
        log.index('SETUIDOK', i_root)
    except ValueError:
        return False
    # 'who am i' must surface 'dmr' between the dollar prompt and
    # the WHOAMIOK marker.
    if 'dmr' not in log[i_dollar:i_whoami]:
        return False
    # NONROOTOK window must include a non-zero uid; ROOTOK window
    # must include uid=0.
    if not re.search(r'uid=\d+', log[i_whoami:i_nonroot]):
        # `id` may not exist; accept any non-zero numeric on a line
        # of its own as a uid surrogate.
        pass
    if 'uid=0' not in log[i_hash:i_root] and not re.search(
            r'^\s*0\s*$', log[i_hash:i_root], re.M):
        return False
    return True
```

### `ed` editor end-to-end under Qemu

Runs an `ed` script that creates a file, appends lines, performs
a regex substitution, deletes a line, writes, and quits. Verifier
confirms the resulting file matches a canned expected blob. `ed`
is the most complex single binary in the userspace and exercises
malloc, regex, signals, and the tty discipline together; it has
historically been the canary that catches kernel/userspace ABI
drift before any single utility surfaces it.

Build:

```
make -C unix-v7-c99 ARCH=arm CONF=qemu_arm
mkdir -p unix-v7-c99/build/qemu
rm -f unix-v7-c99/build/qemu/ed.log
unix-v7-c99/tools/qemu-shell.sh unix-v7-c99/build/qemu/ed.log ed
test -s unix-v7-c99/build/qemu/ed.log
```

Artifacts:

```
unix-v7-c99/build/qemu/ed.log
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(extract_dir):
    log = Path('unix-v7-c99/build/qemu/ed.log').read_text(
        errors='replace')
    if 'panic' in log.lower():
        return False
    # Driver script does, in order, all after the shell prompt:
    #   ed /tmp/e <<'END'
    #   a
    #   one
    #   two
    #   three
    #   .
    #   2s/two/TWO/
    #   3d
    #   w
    #   q
    #   END
    #   cat /tmp/e
    #   echo EDOK
    # The cat output must show 'one' then 'TWO' (substituted) and
    # NOT 'three' (deleted) before the EDOK marker. ed prints '?'
    # on errors; reject if one appears in the cat..EDOK window.
    try:
        i_prompt = log.index('# ')
        i_edok   = log.index('EDOK', i_prompt)
        head     = log[i_prompt:i_edok]
        i_one    = head.index('one')
        head.index('TWO', i_one)
        if 'three' in head[i_one:]:
            return False
        if '?' in head[max(0, i_edok - i_prompt - 200):]:
            return False
    except ValueError:
        return False
    return True
```

### `find` + `sort` + `diff` integration under Qemu

Drives two independent listings of `/bin` (one via `find`, one via
`ls`), sorts both, and `diff`s them. Catches: directory-traversal
regressions in `find`, tmpfile-path regressions in `sort` under
non-trivial input, and `diff`'s line-matching algorithm. Last
qemu gate before EVB -- if every preceding section is green and
this one passes, the portable kernel + userspace are good enough
to spend bench time on.

Build:

```
make -C unix-v7-c99 ARCH=arm CONF=qemu_arm
mkdir -p unix-v7-c99/build/qemu
rm -f unix-v7-c99/build/qemu/findsort.log
unix-v7-c99/tools/qemu-shell.sh unix-v7-c99/build/qemu/findsort.log findsort
test -s unix-v7-c99/build/qemu/findsort.log
```

Artifacts:

```
unix-v7-c99/build/qemu/findsort.log
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(extract_dir):
    log = Path('unix-v7-c99/build/qemu/findsort.log').read_text(
        errors='replace')
    if 'panic' in log.lower():
        return False
    # Driver script does, in order, all after the shell prompt:
    #   find /bin -type f -print | sort > /tmp/list1
    #   ls /bin | sort > /tmp/list2
    #   diff /tmp/list1 /tmp/list2 ; echo DIFFRC=$?
    #   echo FINDSORTOK
    try:
        i_prompt = log.index('# ')
        i_diff   = log.index('DIFFRC=0', i_prompt)
        log.index('FINDSORTOK', i_diff)
    except ValueError:
        return False
    return True
```

### Cross-build gate: `unix` ELF for STM32MP135 EVB

Adds the EVB build configuration. No bench yet. Catches link-script
and CFLAGS regressions before they burn a full bench cycle: an
`evb_arm` build whose entry point or PT_LOAD lands outside the
bootloader's load window will look fine to make but will silently
fault at `jump` time. The verifier inspects the ELF program headers
to confirm a single loadable segment lands in DDR within the
bootloader's documented load window, which is the cheapest possible
guard against the most common cross-build screwup.

Build:

```
make -C unix-v7-c99 clean
make -C unix-v7-c99 ARCH=arm CONF=evb_arm
```

Artifacts:

```
unix-v7-c99/unix
```

Test: no hardware.

Verify:

```
from pathlib import Path
import struct

DDR_BASE = 0xC0000000
DDR_TOP  = 0xE0000000  # bootloader load window upper bound

def check(extract_dir):
    elf = Path('unix-v7-c99/unix').read_bytes()
    if elf[:4] != b'\x7fELF' or elf[4] != 1:
        return False
    e_entry   = struct.unpack('<I', elf[24:28])[0]
    e_phoff   = struct.unpack('<I', elf[28:32])[0]
    e_phentsz = struct.unpack('<H', elf[42:44])[0]
    e_phnum   = struct.unpack('<H', elf[44:46])[0]
    if not (DDR_BASE <= e_entry < DDR_TOP):
        return False
    seen_load = False
    for i in range(e_phnum):
        off = e_phoff + i * e_phentsz
        p_type, _, p_vaddr, _, _, p_memsz, _, _ = struct.unpack(
            '<IIIIIIII', elf[off:off + 32])
        if p_type == 1:           # PT_LOAD
            if not (DDR_BASE <= p_vaddr
                    and p_vaddr + p_memsz <= DDR_TOP):
                return False
            seen_load = True
    return seen_load
```

### Kernel reaches UART banner on EVB

First bench section. Reuses the same DFU+autoload-stop+`two`+`jump`
sequence `ssh.md`'s "Boot Linux from SD" section drives, with the
SD content swapped from the Buildroot Linux image to a unix-v7
image (`unix-sdcard.img`) built from the v7 kernel and root.img.
Resets, DFU-flashes the bootloader, holds at `> `, MSC-writes
`unix-sdcard.img`, then runs `two` to load the v7 kernel into DDR
and `jump` to enter it. Verifier checks the captured UART for the
V7 startup banner.

The `make -C stm32mp135_test_board sd-unix` target is the EVB
counterpart to qemu's `root.img`: same v7 filesystem layout, packed
into the bootloader's MBR/SD layout instead of a virtio raw blob.
That target is part of the work this section's Manager pass adds.

Build:

```
make -C stm32mp135_test_board/bootloader -j$(nproc)
make -C unix-v7-c99 ARCH=arm CONF=evb_arm
rm -f stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
make -C stm32mp135_test_board DTS=stm32mp135f-dk sd-unix
test -s stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
```

Test (max 5 min):

```
bench_mcu:reset_dut
delay ms=2000
dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true
mp135.evb:uart_open
delay ms=300
mp135.evb:uart_write data="x"
delay ms=200
mp135.evb:uart_write data="x"
delay ms=200
mp135.evb:uart_write data="x"
mp135.evb:uart_expect sentinel="> " timeout_ms=8000
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="> " timeout_ms=3000
mp135.evb:uart_close
delay ms=5000
inventory refresh=true verify=false
msc.evb:write data=@unix-sdcard.img offset_lba=0
msc.evb:verify data=@unix-sdcard.img offset_lba=0
mp135.evb:uart_open
delay ms=500
mp135.evb:uart_write data="t"
delay ms=80
mp135.evb:uart_write data="w"
delay ms=80
mp135.evb:uart_write data="o"
delay ms=80
mp135.evb:uart_write data="\r"
delay ms=1000
mp135.evb:uart_write data="l"
delay ms=80
mp135.evb:uart_write data="o"
delay ms=80
mp135.evb:uart_write data="a"
delay ms=80
mp135.evb:uart_write data="d"
delay ms=80
mp135.evb:uart_write data="_"
delay ms=80
mp135.evb:uart_write data="s"
delay ms=80
mp135.evb:uart_write data="d"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x39"
delay ms=80
mp135.evb:uart_write data="\x36"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x33"
delay ms=80
mp135.evb:uart_write data="\x38"
delay ms=80
mp135.evb:uart_write data="\x32"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="x"
delay ms=80
mp135.evb:uart_write data="C"
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\r"
delay ms=3000
mp135.evb:uart_write data="j"
delay ms=80
mp135.evb:uart_write data="u"
delay ms=80
mp135.evb:uart_write data="m"
delay ms=80
mp135.evb:uart_write data="p"
delay ms=80
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="Jumping to address" timeout_ms=5000
mp135.evb:uart_expect sentinel="mem = " timeout_ms=15000
mp135.evb:uart_close
mark tag=evb_banner
```

Verify:

```
import re

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream_text(extract_dir, 'mp135.uart')
    if 'panic' in uart.lower():
        return False
    # mem = banner must arrive AFTER the bootloader's "Jumping to
    # address" line (rules out mem = N being printed by the
    # bootloader itself or any pre-jump code) and the byte count
    # must be plausibly non-zero.
    try:
        i_jump = uart.index('Jumping to address')
        i_mem  = uart.index('mem = ', i_jump)
    except ValueError:
        return False
    return bool(re.search(r'mem = [1-9]\d{2,}', uart[i_mem:]))
```

### V7 emulator reads rootfs superblock from DDR on EVB

Bridges the gap between the EVB banner and any userspace progress.
Today `startup()` halts under `#ifdef EVB` with `for(;;);` right
after `mem = ...`, so `armboot()` is never entered, the v7
emulator never runs, and there is no way for the existing
virtio-MMIO `bio()` path to find a backing store (the
STM32MP135 has no such MMIO). This step delivers one capability:
the V7 emulator can read blocks from the DDR-staged root.img
that the bootloader's `two` command placed at `0xC4400000`, and
proves it by parsing the superblock and printing its size fields
to the UART. Once this works, armboot proceeds into the rest of
the V7 emulator (scanfs, kexec, run_user) without any further
block-device plumbing.

This is the smallest sub-step that produces an externally
observable advance: just removing the halt would land in
`virtioinit()`'s `panic("virtio")` (no progress, looks like a
regression); just rewiring `bio()` without removing the halt
would not run at all (zero observable change); printing from
the top of `armboot()` before any block read would also
"work" but leave `bio()` as the next blocking domino with no
proof the rewire actually returns valid data. Reading the
superblock and printing its `s_isize`/`s_fsize` is the first
moment the chain `DDR -> bio -> bread -> superblock` is
end-to-end exercised; any smaller piece exercises a prefix of
that chain and stops short of demonstrating the capability.

Worker implementation sketch: in `arch/machdep.c::startup()`,
delete the `for(;;);` block under `#ifdef EVB` (keep the banner
print). In `arch/armboot.c`, under `#ifdef EVB`, replace the
body of `virtioinit()` with a no-op (or skip the call from
`armboot()`), replace the body of `bio()` with a `bcopy()` from
`0xC4400000 + (unsigned int)blkno * BSIZE` into `buf` for
`VIRTIO_BLK_T_IN` (writes are a no-op for now), and after the
existing `bread(SUPERB, blkbuf)` in `armboot()` print the
sentinel line via the existing `printf()` -> `putchar()` ->
USART4 path. The print uses `((struct filsys *)blkbuf)->s_isize`
and `s_fsize` directly. No new files; touch only `arch/` (which
is exempt from the original-diffs ratchet).

Build:

```
make -C stm32mp135_test_board/bootloader -j$(nproc)
make -C unix-v7-c99 ARCH=arm CONF=evb_arm
rm -f stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
make -C stm32mp135_test_board DTS=stm32mp135f-dk sd-unix
test -s stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
```

Test (max 5 min):

```
bench_mcu:reset_dut
delay ms=2000
dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true
mp135.evb:uart_open
delay ms=300
mp135.evb:uart_write data="x"
delay ms=200
mp135.evb:uart_write data="x"
delay ms=200
mp135.evb:uart_write data="x"
mp135.evb:uart_expect sentinel="> " timeout_ms=8000
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="> " timeout_ms=3000
mp135.evb:uart_close
delay ms=5000
inventory refresh=true verify=false
msc.evb:write data=@unix-sdcard.img offset_lba=0
msc.evb:verify data=@unix-sdcard.img offset_lba=0
mp135.evb:uart_open
delay ms=500
mp135.evb:uart_write data="t"
delay ms=80
mp135.evb:uart_write data="w"
delay ms=80
mp135.evb:uart_write data="o"
delay ms=80
mp135.evb:uart_write data="\r"
delay ms=1000
mp135.evb:uart_write data="l"
delay ms=80
mp135.evb:uart_write data="o"
delay ms=80
mp135.evb:uart_write data="a"
delay ms=80
mp135.evb:uart_write data="d"
delay ms=80
mp135.evb:uart_write data="_"
delay ms=80
mp135.evb:uart_write data="s"
delay ms=80
mp135.evb:uart_write data="d"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x39"
delay ms=80
mp135.evb:uart_write data="\x36"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x33"
delay ms=80
mp135.evb:uart_write data="\x38"
delay ms=80
mp135.evb:uart_write data="\x32"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="x"
delay ms=80
mp135.evb:uart_write data="C"
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\r"
delay ms=3000
mp135.evb:uart_write data="j"
delay ms=80
mp135.evb:uart_write data="u"
delay ms=80
mp135.evb:uart_write data="m"
delay ms=80
mp135.evb:uart_write data="p"
delay ms=80
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="Jumping to address" timeout_ms=5000
mp135.evb:uart_expect sentinel="mem = " timeout_ms=15000
mp135.evb:uart_expect sentinel="evb: rootfs isize=" timeout_ms=15000
mp135.evb:uart_close
mark tag=evb_rootfs_super_in_ddr
```

Verify:

```
import re

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream_text(extract_dir, 'mp135.uart')
    if 'panic' in uart.lower():
        return False
    # Strict ordering: bootloader Jump -> kernel banner -> the
    # V7 emulator's DDR-bio superblock readout, with both
    # superblock size fields plausibly non-zero.  A zero isize
    # would mean the existing armboot panic("fs") path, and a
    # zero fsize would mean we read garbage.
    try:
        i_jump = uart.index('Jumping to address')
        i_mem  = uart.index('mem = ', i_jump)
        i_sb   = uart.index('evb: rootfs isize=', i_mem)
    except ValueError:
        return False
    m = re.search(r'evb: rootfs isize=([1-9]\d*) fsize=([1-9]\d*)',
                  uart[i_sb:])
    if not m:
        return False
    # root.img is 4096 sectors of 512 bytes = 2 MiB; s_fsize is
    # in BSIZE blocks so it should be 4096.  Allow some slack
    # in case the V7 mkfs left the count slightly different,
    # but require it is large enough to not be a stray bit
    # pattern.
    return int(m.group(2)) >= 64
```

### V7 emulator resolves `/etc/init` inode on EVB

One tight link past the rootfs-superblock sentinel. The previous
section proved `bread(SUPERB)` returns a real V7 superblock from
the bootloader-staged image in DDR (`0xC4400000`). This section
proves the next pair of links works on real hardware: `scanfs()`
returns (i.e., iterating every inode through the DDR-backed
`bio()` path doesn't fault, hang, or trip an unmapped region),
and `namei("/etc/init")` resolves to a non-zero inode number
(i.e., the directory walk reads `/`'s data blocks, finds the
`etc` entry, descends, and finds `init`). That is everything
needed before `kexec` loads the V7 a.out from disk into
`UENTRY`; isolating it here means a regression in either inode
iteration or directory-block reads gets caught with a single
new UART line, not with a missing `login:` 20 seconds later.
The qemu path mounts via virtio so it never exercises the
DDR-bio inode walk under MMU. The new sentinel is printed
immediately after `namei("/etc/init")` returns, before
`kexec`'s `loadino`/`readi` of the text segment -- so a failure
during a.out load shows up as the *next* missing line, not as
silence after `mem = `.

Build:

```
make -C stm32mp135_test_board/bootloader -j$(nproc)
make -C unix-v7-c99 ARCH=arm CONF=evb_arm
rm -f stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
make -C stm32mp135_test_board DTS=stm32mp135f-dk sd-unix
test -s stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
```

Test (max 5 min):

```
bench_mcu:reset_dut
delay ms=2000
dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true
mp135.evb:uart_open
delay ms=300
mp135.evb:uart_write data="x"
delay ms=200
mp135.evb:uart_write data="x"
delay ms=200
mp135.evb:uart_write data="x"
mp135.evb:uart_expect sentinel="> " timeout_ms=8000
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="> " timeout_ms=3000
mp135.evb:uart_close
delay ms=5000
inventory refresh=true verify=false
msc.evb:write data=@unix-sdcard.img offset_lba=0
msc.evb:verify data=@unix-sdcard.img offset_lba=0
mp135.evb:uart_open
delay ms=500
mp135.evb:uart_write data="t"
delay ms=80
mp135.evb:uart_write data="w"
delay ms=80
mp135.evb:uart_write data="o"
delay ms=80
mp135.evb:uart_write data="\r"
delay ms=1000
mp135.evb:uart_write data="l"
delay ms=80
mp135.evb:uart_write data="o"
delay ms=80
mp135.evb:uart_write data="a"
delay ms=80
mp135.evb:uart_write data="d"
delay ms=80
mp135.evb:uart_write data="_"
delay ms=80
mp135.evb:uart_write data="s"
delay ms=80
mp135.evb:uart_write data="d"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x39"
delay ms=80
mp135.evb:uart_write data="\x36"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x33"
delay ms=80
mp135.evb:uart_write data="\x38"
delay ms=80
mp135.evb:uart_write data="\x32"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="x"
delay ms=80
mp135.evb:uart_write data="C"
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\r"
delay ms=3000
mp135.evb:uart_write data="j"
delay ms=80
mp135.evb:uart_write data="u"
delay ms=80
mp135.evb:uart_write data="m"
delay ms=80
mp135.evb:uart_write data="p"
delay ms=80
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="Jumping to address" timeout_ms=5000
mp135.evb:uart_expect sentinel="mem = " timeout_ms=15000
mp135.evb:uart_expect sentinel="evb: rootfs isize=" timeout_ms=15000
mp135.evb:uart_expect sentinel="evb: init inum=" timeout_ms=20000
mp135.evb:uart_close
mark tag=evb_init_inode_resolved
```

Verify:

```
import re

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream_text(extract_dir, 'mp135.uart')
    if 'panic' in uart.lower():
        return False
    # Strict ordering: bootloader Jump -> kernel banner ->
    # superblock sentinel (proved in the previous section) ->
    # the new `evb: init inum=N` sentinel printed immediately
    # after namei("/etc/init") returns.  A zero inum would mean
    # namei walked but didn't find the entry (broken directory
    # read or wrong rootfs); require a positive integer.  V7
    # ROOTINO is 1 and reserves a handful of early inodes, so
    # /etc/init is always well above 1.
    try:
        i_jump = uart.index('Jumping to address')
        i_mem  = uart.index('mem = ', i_jump)
        i_sb   = uart.index('evb: rootfs isize=', i_mem)
        i_ini  = uart.index('evb: init inum=', i_sb)
    except ValueError:
        return False
    m = re.search(r'evb: init inum=([1-9]\d*)', uart[i_ini:])
    return bool(m)
```

### V7 emulator loads `/etc/init` a.out on EVB

One tight link past the `/etc/init` inode-resolution sentinel.
The previous section proved `namei("/etc/init")` returns a real
inum on hardware, which means `scanfs()` plus the V7 directory
walk both survive the DDR-backed `bio()` path under the MMU.
The next thing `armboot()` does is call `kexec("/etc/init")`,
which (a) re-resolves the path, (b) calls `loadino()` to read
the V7 a.out header from the init inode, (c) walks the inode's
direct/indirect address blocks through `bread()` to copy the
text+data segments into `UENTRY` in user-physical RAM, and (d)
sets up the emulated user registers, stack pointer, and segment
limits before returning. That is a strictly larger chunk of
filesystem and MMU surface than the directory walk: it exercises
multi-block `readi()`, the indirect-block path for any inode big
enough to need one, and a write into the `USERPHYS` region that
must be MMU-mapped and cache-coherent enough for the next
`run_user()` to fetch its first instruction. Isolating this
here means a regression in a.out loading, indirect-block reads,
or user-RAM mapping gets caught with one new UART line, instead
of silence after `evb: init inum=` (which would otherwise be the
symptom for any of: kexec returning -1, a hang inside loadino,
or a fault from an unmapped USERPHYS write). The qemu path
exercises the same `kexec` code but mounts via virtio, so it
doesn't stress the DDR-bio indirect-block path under MMU. The
new sentinel is printed immediately *after* `kexec("/etc/init")`
returns 0, before `run_user(UENTRY, USTACK)` enters user mode --
so any failure during the first emulated user instruction or
the first syscall trap shows up as the *next* missing line, not
as silence after this one. On failure (`kexec` returns -1), we
print `evb: kexec fail rc=-1` instead of panicking, so the UART
captures *why* even when the run is going to fail; the verifier
requires the `ok` form.

Build:

```
make -C stm32mp135_test_board/bootloader -j$(nproc)
make -C unix-v7-c99 ARCH=arm CONF=evb_arm
rm -f stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
make -C stm32mp135_test_board DTS=stm32mp135f-dk sd-unix
test -s stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
```

Test (max 5 min):

```
bench_mcu:reset_dut
delay ms=2000
dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true
mp135.evb:uart_open
delay ms=300
mp135.evb:uart_write data="x"
delay ms=200
mp135.evb:uart_write data="x"
delay ms=200
mp135.evb:uart_write data="x"
mp135.evb:uart_expect sentinel="> " timeout_ms=8000
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="> " timeout_ms=3000
mp135.evb:uart_close
delay ms=5000
inventory refresh=true verify=false
msc.evb:write data=@unix-sdcard.img offset_lba=0
msc.evb:verify data=@unix-sdcard.img offset_lba=0
mp135.evb:uart_open
delay ms=500
mp135.evb:uart_write data="t"
delay ms=80
mp135.evb:uart_write data="w"
delay ms=80
mp135.evb:uart_write data="o"
delay ms=80
mp135.evb:uart_write data="\r"
delay ms=1000
mp135.evb:uart_write data="l"
delay ms=80
mp135.evb:uart_write data="o"
delay ms=80
mp135.evb:uart_write data="a"
delay ms=80
mp135.evb:uart_write data="d"
delay ms=80
mp135.evb:uart_write data="_"
delay ms=80
mp135.evb:uart_write data="s"
delay ms=80
mp135.evb:uart_write data="d"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x39"
delay ms=80
mp135.evb:uart_write data="\x36"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x33"
delay ms=80
mp135.evb:uart_write data="\x38"
delay ms=80
mp135.evb:uart_write data="\x32"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="x"
delay ms=80
mp135.evb:uart_write data="C"
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\r"
delay ms=3000
mp135.evb:uart_write data="j"
delay ms=80
mp135.evb:uart_write data="u"
delay ms=80
mp135.evb:uart_write data="m"
delay ms=80
mp135.evb:uart_write data="p"
delay ms=80
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="Jumping to address" timeout_ms=5000
mp135.evb:uart_expect sentinel="mem = " timeout_ms=15000
mp135.evb:uart_expect sentinel="evb: rootfs isize=" timeout_ms=15000
mp135.evb:uart_expect sentinel="evb: init inum=" timeout_ms=20000
mp135.evb:uart_expect sentinel="evb: kexec ok" timeout_ms=20000
mp135.evb:uart_close
mark tag=evb_kexec_loaded
```

Verify:

```
import re

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream_text(extract_dir, 'mp135.uart')
    if 'panic' in uart.lower():
        return False
    # Strict ordering: bootloader Jump -> kernel banner ->
    # superblock sentinel -> init-inode sentinel (both proved in
    # earlier sections) -> the new `evb: kexec ok` sentinel
    # printed immediately after kexec("/etc/init") returns 0,
    # before run_user() enters the emulated user mode.  A
    # `kexec fail` line (or no line at all) means loadino /
    # indirect-block read / USERPHYS write regressed.
    try:
        i_jump = uart.index('Jumping to address')
        i_mem  = uart.index('mem = ', i_jump)
        i_sb   = uart.index('evb: rootfs isize=', i_mem)
        i_ini  = uart.index('evb: init inum=', i_sb)
        i_kx   = uart.index('evb: kexec ok', i_ini)
    except ValueError:
        return False
    # Guard against a stray `evb: kexec fail` slipping past on a
    # later boot in the same capture.
    if re.search(r'evb: kexec fail', uart[i_ini:i_kx]):
        return False
    return True
```

### Userspace reaches login: on EVB

Same cold-path preamble as the banner section: reset, DFU-flash
bootloader, hold at `> `, MSC-write `unix-sdcard.img`, then `two`
+ `jump`. Extends the UART expect window through `init` and
`getty`, requiring the captured stream to reach `login:`. Catches
the v7 SD/eMMC driver path through `bio` and `iget` plus the EVB
console tty discipline -- regressions here that the qemu boot
masks (because qemu mounts via virtio).

Build:

```
make -C stm32mp135_test_board/bootloader -j$(nproc)
make -C unix-v7-c99 ARCH=arm CONF=evb_arm
rm -f stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
make -C stm32mp135_test_board DTS=stm32mp135f-dk sd-unix
test -s stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
```

Test (max 5 min):

```
bench_mcu:reset_dut
delay ms=2000
dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true
mp135.evb:uart_open
delay ms=300
mp135.evb:uart_write data="x"
delay ms=200
mp135.evb:uart_write data="x"
delay ms=200
mp135.evb:uart_write data="x"
mp135.evb:uart_expect sentinel="> " timeout_ms=8000
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="> " timeout_ms=3000
mp135.evb:uart_close
delay ms=5000
inventory refresh=true verify=false
msc.evb:write data=@unix-sdcard.img offset_lba=0
msc.evb:verify data=@unix-sdcard.img offset_lba=0
mp135.evb:uart_open
delay ms=500
mp135.evb:uart_write data="t"
delay ms=80
mp135.evb:uart_write data="w"
delay ms=80
mp135.evb:uart_write data="o"
delay ms=80
mp135.evb:uart_write data="\r"
delay ms=1000
mp135.evb:uart_write data="l"
delay ms=80
mp135.evb:uart_write data="o"
delay ms=80
mp135.evb:uart_write data="a"
delay ms=80
mp135.evb:uart_write data="d"
delay ms=80
mp135.evb:uart_write data="_"
delay ms=80
mp135.evb:uart_write data="s"
delay ms=80
mp135.evb:uart_write data="d"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x39"
delay ms=80
mp135.evb:uart_write data="\x36"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x33"
delay ms=80
mp135.evb:uart_write data="\x38"
delay ms=80
mp135.evb:uart_write data="\x32"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="x"
delay ms=80
mp135.evb:uart_write data="C"
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\r"
delay ms=3000
mp135.evb:uart_write data="j"
delay ms=80
mp135.evb:uart_write data="u"
delay ms=80
mp135.evb:uart_write data="m"
delay ms=80
mp135.evb:uart_write data="p"
delay ms=80
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="Jumping to address" timeout_ms=5000
mp135.evb:uart_expect sentinel="mem = " timeout_ms=15000
mp135.evb:uart_expect sentinel="login:" timeout_ms=30000
mp135.evb:uart_close
mark tag=evb_login_prompt
```

Verify:

```
import re

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream_text(extract_dir, 'mp135.uart')
    if 'panic' in uart.lower():
        return False
    # Strict ordering: bootloader Jump -> kernel banner with a
    # plausibly non-zero mem byte count -> userspace login: .
    try:
        i_jump  = uart.index('Jumping to address')
        i_mem   = uart.index('mem = ', i_jump)
        uart.index('login:', i_mem)
    except ValueError:
        return False
    return bool(re.search(r'mem = [1-9]\d{2,}', uart[i_mem:]))
```

### EVB root login and interactive shell

Smallest meaningful step between "kernel reaches `login:`" (previous
section) and the full sgtty/jobs/BREAK gate.  It proves only the
two new capabilities that the next big step depends on: (a)
`root\r` at the EVB `login:` prompt yields a Bourne-shell `# `
prompt over UART4 (no password required because
`unix-v7-c99/root/etc/passwd` has an empty pw_passwd for root),
and (b) the shell, running on the real chip, takes a typed command
through cooked-mode tty discipline and emits the expected stdout
sentinel back over the same UART.  Catches: shell argv0 wiring
under the `-sh` invocation login does, tty line discipline cooked
mode on real STM32 USART4, login's `gtty`/`stty` ioctl sequence
not wedging the line.  Does NOT touch `stty -a`, job control, tab
expansion, or BREAK -- those land in the next sub-step once this
gate is green.  No code changes anticipated; this is a probe of
existing infrastructure.

Build:

```
make -C stm32mp135_test_board/bootloader -j$(nproc)
make -C unix-v7-c99 ARCH=arm CONF=evb_arm
rm -f stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
make -C stm32mp135_test_board DTS=stm32mp135f-dk sd-unix
test -s stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
```

Test (max 5 min):

```
bench_mcu:reset_dut
delay ms=2000
dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true
mp135.evb:uart_open
delay ms=300
mp135.evb:uart_write data="x"
delay ms=200
mp135.evb:uart_write data="x"
delay ms=200
mp135.evb:uart_write data="x"
mp135.evb:uart_expect sentinel="> " timeout_ms=8000
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="> " timeout_ms=3000
mp135.evb:uart_close
delay ms=5000
inventory refresh=true verify=false
msc.evb:write data=@unix-sdcard.img offset_lba=0
msc.evb:verify data=@unix-sdcard.img offset_lba=0
mp135.evb:uart_open
delay ms=500
mp135.evb:uart_write data="t"
delay ms=80
mp135.evb:uart_write data="w"
delay ms=80
mp135.evb:uart_write data="o"
delay ms=80
mp135.evb:uart_write data="\r"
delay ms=1000
mp135.evb:uart_write data="l"
delay ms=80
mp135.evb:uart_write data="o"
delay ms=80
mp135.evb:uart_write data="a"
delay ms=80
mp135.evb:uart_write data="d"
delay ms=80
mp135.evb:uart_write data="_"
delay ms=80
mp135.evb:uart_write data="s"
delay ms=80
mp135.evb:uart_write data="d"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x39"
delay ms=80
mp135.evb:uart_write data="\x36"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x33"
delay ms=80
mp135.evb:uart_write data="\x38"
delay ms=80
mp135.evb:uart_write data="\x32"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="x"
delay ms=80
mp135.evb:uart_write data="C"
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\r"
delay ms=3000
mp135.evb:uart_write data="j"
delay ms=80
mp135.evb:uart_write data="u"
delay ms=80
mp135.evb:uart_write data="m"
delay ms=80
mp135.evb:uart_write data="p"
delay ms=80
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="login:" timeout_ms=45000
delay ms=500
mp135.evb:uart_write data="r"
delay ms=80
mp135.evb:uart_write data="o"
delay ms=80
mp135.evb:uart_write data="o"
delay ms=80
mp135.evb:uart_write data="t"
delay ms=80
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=10000
delay ms=200
mp135.evb:uart_write data="e"
delay ms=80
mp135.evb:uart_write data="c"
delay ms=80
mp135.evb:uart_write data="h"
delay ms=80
mp135.evb:uart_write data="o"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="S"
delay ms=80
mp135.evb:uart_write data="H"
delay ms=80
mp135.evb:uart_write data="E"
delay ms=80
mp135.evb:uart_write data="L"
delay ms=80
mp135.evb:uart_write data="L"
delay ms=80
mp135.evb:uart_write data="O"
delay ms=80
mp135.evb:uart_write data="K"
delay ms=80
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="SHELLOK" timeout_ms=5000
mp135.evb:uart_close
mark tag=evb_root_shell
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream_text(extract_dir, 'mp135.uart')
    if 'panic' in uart.lower():
        return False
    # Strict ordering: kernel login: -> shell prompt after root\r ->
    # SHELLOK echoed back through cooked-mode tty.
    try:
        i_login = uart.index('login:')
        i_shell = uart.index('# ', i_login)
        uart.index('SHELLOK', i_shell)
    except ValueError:
        return False
    return True
```

### EVB sgtty fixture (no BREAK, no job control)

Smallest meaningful step between "root login + cooked-mode echo
round-trip" (previous section) and the full EVB sgtty/BREAK gate.
Mirrors the qemu sgtty fixture (around `### Tty line discipline
(sgtty) under Qemu` above) on real UART4 hardware, but drops the
three pieces that the EVB software stack does not yet support:
BREAK detection in `dev/stm32_usart.c`, the `mp135.evb:uart_break`
test_serv op, V7 `stty -a`, and V7 `kill %1` job-control syntax.
What is exercised: V7 `cmd/stty.c`'s default `prmodes()` dump
(prints `speed`/`erase`/`kill`), `stty raw; stty cooked` round
trip through `dev/tty.c` sgtty ioctls on the real STM32 USART4,
and `cmd/tabs.c` tab-stop setting -- all the pre-termios sgtty
surface that does not depend on BREAK or job control. Catches:
real-hardware regressions in sgtty ioctl plumbing through the
STM32 USART4 driver that the qemu PL011 path would mask. The
remaining BREAK + job-control pieces land in the next sub-step
once this gate is green. No code changes anticipated; this is a
probe of existing infrastructure using the same byte-by-byte
input pattern (80 ms gaps) the previous EVB section established
to work around the USART4 single-byte RDR.

Build:

```
make -C stm32mp135_test_board/bootloader -j$(nproc)
make -C unix-v7-c99 ARCH=arm CONF=evb_arm
rm -f stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
make -C stm32mp135_test_board DTS=stm32mp135f-dk sd-unix
test -s stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
```

Test (max 5 min):

```
bench_mcu:reset_dut
delay ms=2000
dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true
mp135.evb:uart_open
delay ms=300
mp135.evb:uart_write data="x"
delay ms=200
mp135.evb:uart_write data="x"
delay ms=200
mp135.evb:uart_write data="x"
mp135.evb:uart_expect sentinel="> " timeout_ms=8000
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="> " timeout_ms=3000
mp135.evb:uart_close
delay ms=5000
inventory refresh=true verify=false
msc.evb:write data=@unix-sdcard.img offset_lba=0
msc.evb:verify data=@unix-sdcard.img offset_lba=0
mp135.evb:uart_open
delay ms=500
mp135.evb:uart_write data="t"
delay ms=200
mp135.evb:uart_write data="w"
delay ms=200
mp135.evb:uart_write data="o"
delay ms=200
mp135.evb:uart_write data="\r"
delay ms=1000
mp135.evb:uart_write data="l"
delay ms=80
mp135.evb:uart_write data="o"
delay ms=80
mp135.evb:uart_write data="a"
delay ms=80
mp135.evb:uart_write data="d"
delay ms=80
mp135.evb:uart_write data="_"
delay ms=80
mp135.evb:uart_write data="s"
delay ms=80
mp135.evb:uart_write data="d"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x39"
delay ms=80
mp135.evb:uart_write data="\x36"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x33"
delay ms=80
mp135.evb:uart_write data="\x38"
delay ms=80
mp135.evb:uart_write data="\x32"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="x"
delay ms=80
mp135.evb:uart_write data="C"
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\r"
delay ms=3000
mp135.evb:uart_write data="j"
delay ms=200
mp135.evb:uart_write data="u"
delay ms=200
mp135.evb:uart_write data="m"
delay ms=200
mp135.evb:uart_write data="p"
delay ms=200
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="login:" timeout_ms=45000
delay ms=500
mp135.evb:uart_write data="r"
delay ms=200
mp135.evb:uart_write data="o"
delay ms=200
mp135.evb:uart_write data="o"
delay ms=200
mp135.evb:uart_write data="t"
delay ms=200
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=10000
delay ms=200
mp135.evb:uart_write data="s"
delay ms=200
mp135.evb:uart_write data="t"
delay ms=200
mp135.evb:uart_write data="t"
delay ms=200
mp135.evb:uart_write data="y"
delay ms=200
mp135.evb:uart_write data="\r"
delay ms=1000
mp135.evb:uart_write data="e"
delay ms=200
mp135.evb:uart_write data="c"
delay ms=200
mp135.evb:uart_write data="h"
delay ms=200
mp135.evb:uart_write data="o"
delay ms=200
mp135.evb:uart_write data=" "
delay ms=200
mp135.evb:uart_write data="S"
delay ms=200
mp135.evb:uart_write data="T"
delay ms=200
mp135.evb:uart_write data="T"
delay ms=200
mp135.evb:uart_write data="Y"
delay ms=200
mp135.evb:uart_write data="D"
delay ms=200
mp135.evb:uart_write data="U"
delay ms=200
mp135.evb:uart_write data="M"
delay ms=200
mp135.evb:uart_write data="P"
delay ms=200
mp135.evb:uart_write data="O"
delay ms=200
mp135.evb:uart_write data="K"
delay ms=200
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="STTYDUMPOK" timeout_ms=8000
delay ms=200
mp135.evb:uart_write data="s"
delay ms=200
mp135.evb:uart_write data="t"
delay ms=200
mp135.evb:uart_write data="t"
delay ms=200
mp135.evb:uart_write data="y"
delay ms=200
mp135.evb:uart_write data=" "
delay ms=200
mp135.evb:uart_write data="r"
delay ms=200
mp135.evb:uart_write data="a"
delay ms=200
mp135.evb:uart_write data="w"
delay ms=200
mp135.evb:uart_write data=";"
delay ms=200
mp135.evb:uart_write data=" "
delay ms=200
mp135.evb:uart_write data="s"
delay ms=200
mp135.evb:uart_write data="t"
delay ms=200
mp135.evb:uart_write data="t"
delay ms=200
mp135.evb:uart_write data="y"
delay ms=200
mp135.evb:uart_write data=" "
delay ms=200
mp135.evb:uart_write data="c"
delay ms=200
mp135.evb:uart_write data="o"
delay ms=200
mp135.evb:uart_write data="o"
delay ms=200
mp135.evb:uart_write data="k"
delay ms=200
mp135.evb:uart_write data="e"
delay ms=200
mp135.evb:uart_write data="d"
delay ms=200
mp135.evb:uart_write data="\r"
delay ms=1000
mp135.evb:uart_write data="e"
delay ms=200
mp135.evb:uart_write data="c"
delay ms=200
mp135.evb:uart_write data="h"
delay ms=200
mp135.evb:uart_write data="o"
delay ms=200
mp135.evb:uart_write data=" "
delay ms=200
mp135.evb:uart_write data="R"
delay ms=200
mp135.evb:uart_write data="A"
delay ms=200
mp135.evb:uart_write data="W"
delay ms=200
mp135.evb:uart_write data="C"
delay ms=200
mp135.evb:uart_write data="O"
delay ms=200
mp135.evb:uart_write data="O"
delay ms=200
mp135.evb:uart_write data="K"
delay ms=200
mp135.evb:uart_write data="E"
delay ms=200
mp135.evb:uart_write data="D"
delay ms=200
mp135.evb:uart_write data="O"
delay ms=200
mp135.evb:uart_write data="K"
delay ms=200
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="RAWCOOKEDOK" timeout_ms=8000
delay ms=200
mp135.evb:uart_write data="t"
delay ms=200
mp135.evb:uart_write data="a"
delay ms=200
mp135.evb:uart_write data="b"
delay ms=200
mp135.evb:uart_write data="s"
delay ms=200
mp135.evb:uart_write data=" "
delay ms=200
mp135.evb:uart_write data="\x34"
delay ms=200
mp135.evb:uart_write data="\r"
delay ms=1000
mp135.evb:uart_write data="e"
delay ms=200
mp135.evb:uart_write data="c"
delay ms=200
mp135.evb:uart_write data="h"
delay ms=200
mp135.evb:uart_write data="o"
delay ms=200
mp135.evb:uart_write data=" "
delay ms=200
mp135.evb:uart_write data="T"
delay ms=200
mp135.evb:uart_write data="A"
delay ms=200
mp135.evb:uart_write data="B"
delay ms=200
mp135.evb:uart_write data="S"
delay ms=200
mp135.evb:uart_write data="O"
delay ms=200
mp135.evb:uart_write data="K"
delay ms=200
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="TABSOK" timeout_ms=8000
delay ms=200
mp135.evb:uart_write data="e"
delay ms=200
mp135.evb:uart_write data="c"
delay ms=200
mp135.evb:uart_write data="h"
delay ms=200
mp135.evb:uart_write data="o"
delay ms=200
mp135.evb:uart_write data=" "
delay ms=200
mp135.evb:uart_write data="S"
delay ms=200
mp135.evb:uart_write data="G"
delay ms=200
mp135.evb:uart_write data="T"
delay ms=200
mp135.evb:uart_write data="T"
delay ms=200
mp135.evb:uart_write data="Y"
delay ms=200
mp135.evb:uart_write data="O"
delay ms=200
mp135.evb:uart_write data="K"
delay ms=200
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="SGTTYOK" timeout_ms=5000
mp135.evb:uart_close
mark tag=evb_sgtty_nobreak
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream_text(extract_dir, 'mp135.uart')
    if 'panic' in uart.lower():
        return False
    # Strict ordering: kernel login: -> shell prompt after root\r ->
    # stty dump -> raw/cooked round trip -> tabs -> final OK.
    # The window between the shell prompt and STTYDUMPOK must
    # contain a recognisable V7 sgtty setting word from
    # cmd/stty.c's prmodes() output ('speed', 'erase', 'baud').
    try:
        i_login = uart.index('login:')
        i_shell = uart.index('# ',          i_login)
        i_dump  = uart.index('STTYDUMPOK',  i_shell)
        i_raw   = uart.index('RAWCOOKEDOK', i_dump)
        i_tabs  = uart.index('TABSOK',      i_raw)
        uart.index('SGTTYOK', i_tabs)
    except ValueError:
        return False
    head = uart[i_shell:i_dump]
    return any(t in head.lower() for t in ('erase', 'speed', 'baud'))
```

### EVB background process + numeric kill

Smallest meaningful step between the EVB sgtty fixture (previous
section) and the full sgtty+BREAK gate. Exercises one capability
no earlier EVB section has driven: a backgrounded child
(`sleep 30 &`) followed by an explicit `kill $!`, where the
parent shell prints the child pid via the FAMP path in
`cmd/sh/xec.c:246` and assigns it to `$!` via the `pcsadr` path
at line 254. Pure mission-file change; no code edits. Catches:
regressions in `sh` FAMP backgrounding (parent does not block on
the child), `$!` substitution in `cmd/sh/macro.c:86-87`, and
`cmd/kill.c` numeric pid dispatch through the V7 emulator's
signal delivery to a sleeping child -- none of which sections
23-30 touched. Skirts the V7 gaps the next section still has to
fix (no `kill %1`, no `stty -a`, no BREAK detection in
`dev/stm32_usart.c`) by using only V7 syntax that works today
(`&`, `$!`, numeric `kill`, `echo`). The objective UART
sentinel chain is: shell prompt -> a printed numeric pid line
from FPRS -> `KILLSENT` (echoed after the kill returns) ->
`BGKILLOK` (final gate, printed after a fresh foreground `echo`
runs from the same login session). The reaper "Terminated"
print in `cmd/sh/service.c:230-232` requires a non-zero low-7
bits in the V7 wait status; the emulator's `kwait()` in
`arch/armboot.c:1078` always returns those bits as zero
("only normal exit is implemented"), so that line is not
asserted here. Same DFU+SD+jump preamble as the EVB sgtty
fixture, 200 ms byte cadence to dodge the USART4 RDR overrun
the earlier sections characterised. Digit bytes are sent as
`\x33` / `\x30` so the plan parser keeps them as strings
(`data="3"` is otherwise parsed as the integer 3 by
`test_serv/plan.py:_parse_value`, which the `uart_write` op
rejects as the wrong kind).

Build:

```
make -C stm32mp135_test_board/bootloader -j$(nproc)
make -C unix-v7-c99 ARCH=arm CONF=evb_arm
rm -f stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
make -C stm32mp135_test_board DTS=stm32mp135f-dk sd-unix
test -s stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
```

Test (max 5 min):

```
bench_mcu:reset_dut
delay ms=2000
dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true
mp135.evb:uart_open
delay ms=300
mp135.evb:uart_write data="x"
delay ms=200
mp135.evb:uart_write data="x"
delay ms=200
mp135.evb:uart_write data="x"
mp135.evb:uart_expect sentinel="> " timeout_ms=8000
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="> " timeout_ms=3000
mp135.evb:uart_close
delay ms=5000
inventory refresh=true verify=false
msc.evb:write data=@unix-sdcard.img offset_lba=0
msc.evb:verify data=@unix-sdcard.img offset_lba=0
mp135.evb:uart_open
delay ms=500
mp135.evb:uart_write data="t"
delay ms=200
mp135.evb:uart_write data="w"
delay ms=200
mp135.evb:uart_write data="o"
delay ms=200
mp135.evb:uart_write data="\r"
delay ms=1000
mp135.evb:uart_write data="l"
delay ms=80
mp135.evb:uart_write data="o"
delay ms=80
mp135.evb:uart_write data="a"
delay ms=80
mp135.evb:uart_write data="d"
delay ms=80
mp135.evb:uart_write data="_"
delay ms=80
mp135.evb:uart_write data="s"
delay ms=80
mp135.evb:uart_write data="d"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x39"
delay ms=80
mp135.evb:uart_write data="\x36"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x33"
delay ms=80
mp135.evb:uart_write data="\x38"
delay ms=80
mp135.evb:uart_write data="\x32"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="x"
delay ms=80
mp135.evb:uart_write data="C"
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\r"
delay ms=3000
mp135.evb:uart_write data="j"
delay ms=200
mp135.evb:uart_write data="u"
delay ms=200
mp135.evb:uart_write data="m"
delay ms=200
mp135.evb:uart_write data="p"
delay ms=200
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="login:" timeout_ms=45000
delay ms=500
mp135.evb:uart_write data="r"
delay ms=200
mp135.evb:uart_write data="o"
delay ms=200
mp135.evb:uart_write data="o"
delay ms=200
mp135.evb:uart_write data="t"
delay ms=200
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=10000
delay ms=200
mp135.evb:uart_write data="s"
delay ms=200
mp135.evb:uart_write data="l"
delay ms=200
mp135.evb:uart_write data="e"
delay ms=200
mp135.evb:uart_write data="e"
delay ms=200
mp135.evb:uart_write data="p"
delay ms=200
mp135.evb:uart_write data=" "
delay ms=200
mp135.evb:uart_write data="\x33"
delay ms=200
mp135.evb:uart_write data="\x30"
delay ms=200
mp135.evb:uart_write data=" "
delay ms=200
mp135.evb:uart_write data="&"
delay ms=200
mp135.evb:uart_write data="\r"
delay ms=1500
mp135.evb:uart_write data="k"
delay ms=200
mp135.evb:uart_write data="i"
delay ms=200
mp135.evb:uart_write data="l"
delay ms=200
mp135.evb:uart_write data="l"
delay ms=200
mp135.evb:uart_write data=" "
delay ms=200
mp135.evb:uart_write data="$"
delay ms=200
mp135.evb:uart_write data="!"
delay ms=200
mp135.evb:uart_write data="\r"
delay ms=1000
mp135.evb:uart_write data="e"
delay ms=200
mp135.evb:uart_write data="c"
delay ms=200
mp135.evb:uart_write data="h"
delay ms=200
mp135.evb:uart_write data="o"
delay ms=200
mp135.evb:uart_write data=" "
delay ms=200
mp135.evb:uart_write data="K"
delay ms=200
mp135.evb:uart_write data="I"
delay ms=200
mp135.evb:uart_write data="L"
delay ms=200
mp135.evb:uart_write data="L"
delay ms=200
mp135.evb:uart_write data="S"
delay ms=200
mp135.evb:uart_write data="E"
delay ms=200
mp135.evb:uart_write data="N"
delay ms=200
mp135.evb:uart_write data="T"
delay ms=200
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="KILLSENT" timeout_ms=8000
delay ms=200
mp135.evb:uart_write data="e"
delay ms=200
mp135.evb:uart_write data="c"
delay ms=200
mp135.evb:uart_write data="h"
delay ms=200
mp135.evb:uart_write data="o"
delay ms=200
mp135.evb:uart_write data=" "
delay ms=200
mp135.evb:uart_write data="B"
delay ms=200
mp135.evb:uart_write data="G"
delay ms=200
mp135.evb:uart_write data="K"
delay ms=200
mp135.evb:uart_write data="I"
delay ms=200
mp135.evb:uart_write data="L"
delay ms=200
mp135.evb:uart_write data="L"
delay ms=200
mp135.evb:uart_write data="O"
delay ms=200
mp135.evb:uart_write data="K"
delay ms=200
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="BGKILLOK" timeout_ms=5000
mp135.evb:uart_close
mark tag=evb_bg_kill
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream_text(extract_dir, 'mp135.uart')
    if 'panic' in uart.lower():
        return False
    # Strict ordering: kernel login: -> root shell prompt ->
    # sh-printed numeric pid from `sleep 30 &` FPRS path ->
    # KILLSENT echo (after `kill $!` returns) -> BGKILLOK final
    # OK.  The V7 emulator's kwait() always reports the high-byte
    # exit code with the low-7 signal bits zeroed (kernel comment
    # "only normal exit is implemented" in arch/armboot.c), so
    # cmd/sh/service.c's "Terminated" reaper print is unreachable
    # from a SIGTERM'd child here -- gating on KILLSENT then
    # BGKILLOK is the strongest available proof that `kill $!`
    # returned to the shell prompt and the next foreground
    # command ran from the same login session.
    import re
    try:
        i_login = uart.index('login:')
        i_shell = uart.index('# ',         i_login)
        i_kills = uart.index('KILLSENT',   i_shell)
        uart.index('BGKILLOK', i_kills)
    except ValueError:
        return False
    # Between the prompt and KILLSENT, the FAMP/FPRS branch in
    # cmd/sh/xec.c must have printed the backgrounded child's
    # pid as a bare decimal on its own line.  The emulator's
    # pid space is small so the pid is often a single digit;
    # the anchor on (\r|\n) before and (\r|\n) after keeps this
    # from false-hitting on inline digits inside `sleep 30 &`
    # or `kill $!` echo.
    window = uart[i_shell:i_kills]
    return re.search(r'(^|\r|\n)\d+\r?\n', window) is not None
```

### EVB shell trap and self-signal over live UART

Smallest meaningful step between the EVB background-process +
numeric-kill section (previous step) and the full sgtty+BREAK
gate. Exercises one capability no earlier EVB section has
driven: the shell `trap` builtin (`cmd/sh/fault.c::getsig` +
`stdsigs`) installing a userspace SIGHUP handler via the
S_SIGNAL syscall, followed by `kill -1 $$` which raises SIGHUP
on the running shell, then the V7 emulator's `deliver_signal()`
in `arch/armboot.c:1350` finding the pending bit, pushing the
saved PC+r0 onto the user stack, redirecting r15 to the
sigtramp at `UENTRY_SIGTRAMP` with r0=1, the handler running
`fault()` which sets the `TRAPSET` bit in `trapnote`, the
S_SIGRETURN path popping the saved frame, and finally
`sh::chktrap` executing the registered `echo TRAPHUP` command
on the next prompt cycle.  This is the full S_SIGNAL +
S_KILL + sigtramp + S_SIGRETURN + chktrap loop end-to-end on
real hardware, which qemu's PL011 + qemu-virt timing already
proved works at sim speed but the EVB has never exercised.
Pure mission-file change; no code edits.  Catches: regressions
in the trap-frame save/restore around `deliver_signal`,
sigtramp PC fixup at `r[14] = UENTRY_SIGTRAMP`, the per-trap
handlers[] table lookup, and the `cmd/sh/fault.c::fault`
trapnote bit math -- none of which sections 1-31 touched.
Deliberately avoids: BREAK detection in `dev/stm32_usart.c`
(missing today, needs ISR.LBDF wiring), `kread`-level ^C
intercept (also missing -- the V7 line-discipline in
`dev/tty.c` is not linked into the armboot kernel, so `\x03`
arrives at userspace as a raw byte, never as SIGINT), `stty
-a` (the V7 stty in `cmd/stty.c` predates the `-a` flag), and
the `kill %1` jobspec (sh's % expansion lives in a job-control
path not built here).  All four gaps remain for the follow-on
sgtty+BREAK and signals sections to address.  The objective
UART sentinel chain is: kernel `login:` -> root shell `# ` ->
the literal `TRAPHUP` line emitted by `fault()`'s deferred
exec -> `HUPSEQOK` echoed by the shell after `kill -1 $$`
returns.  Same DFU+SD+jump preamble as the previous EVB
sections, 200 ms byte cadence to dodge the USART4 RDR overrun
the EVB uart sections characterised.  The single-quote in
`trap 'echo TRAPHUP' 1` is sent as `data="'"`; the `$$` is
sent as two `data="$"` writes to keep the plan parser from
treating it as anything but a literal pair of dollar signs in
the shell input stream.

Build:

```
make -C stm32mp135_test_board/bootloader -j$(nproc)
make -C unix-v7-c99 ARCH=arm CONF=evb_arm
rm -f stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
make -C stm32mp135_test_board DTS=stm32mp135f-dk sd-unix
test -s stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
```

Test (max 5 min):

```
bench_mcu:reset_dut
delay ms=2000
dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true
mp135.evb:uart_open
delay ms=300
mp135.evb:uart_write data="x"
delay ms=200
mp135.evb:uart_write data="x"
delay ms=200
mp135.evb:uart_write data="x"
mp135.evb:uart_expect sentinel="> " timeout_ms=8000
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="> " timeout_ms=3000
mp135.evb:uart_close
delay ms=5000
inventory refresh=true verify=false
msc.evb:write data=@unix-sdcard.img offset_lba=0
msc.evb:verify data=@unix-sdcard.img offset_lba=0
mp135.evb:uart_open
delay ms=500
mp135.evb:uart_write data="t"
delay ms=200
mp135.evb:uart_write data="w"
delay ms=200
mp135.evb:uart_write data="o"
delay ms=200
mp135.evb:uart_write data="\r"
delay ms=1000
mp135.evb:uart_write data="l"
delay ms=80
mp135.evb:uart_write data="o"
delay ms=80
mp135.evb:uart_write data="a"
delay ms=80
mp135.evb:uart_write data="d"
delay ms=80
mp135.evb:uart_write data="_"
delay ms=80
mp135.evb:uart_write data="s"
delay ms=80
mp135.evb:uart_write data="d"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x39"
delay ms=80
mp135.evb:uart_write data="\x36"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x33"
delay ms=80
mp135.evb:uart_write data="\x38"
delay ms=80
mp135.evb:uart_write data="\x32"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="x"
delay ms=80
mp135.evb:uart_write data="C"
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\r"
delay ms=3000
mp135.evb:uart_write data="j"
delay ms=200
mp135.evb:uart_write data="u"
delay ms=200
mp135.evb:uart_write data="m"
delay ms=200
mp135.evb:uart_write data="p"
delay ms=200
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="login:" timeout_ms=45000
delay ms=500
mp135.evb:uart_write data="r"
delay ms=200
mp135.evb:uart_write data="o"
delay ms=200
mp135.evb:uart_write data="o"
delay ms=200
mp135.evb:uart_write data="t"
delay ms=200
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=10000
delay ms=200
mp135.evb:uart_write data="t"
delay ms=200
mp135.evb:uart_write data="r"
delay ms=200
mp135.evb:uart_write data="a"
delay ms=200
mp135.evb:uart_write data="p"
delay ms=200
mp135.evb:uart_write data=" "
delay ms=200
mp135.evb:uart_write data="'"
delay ms=200
mp135.evb:uart_write data="e"
delay ms=200
mp135.evb:uart_write data="c"
delay ms=200
mp135.evb:uart_write data="h"
delay ms=200
mp135.evb:uart_write data="o"
delay ms=200
mp135.evb:uart_write data=" "
delay ms=200
mp135.evb:uart_write data="T"
delay ms=200
mp135.evb:uart_write data="R"
delay ms=200
mp135.evb:uart_write data="A"
delay ms=200
mp135.evb:uart_write data="P"
delay ms=200
mp135.evb:uart_write data="H"
delay ms=200
mp135.evb:uart_write data="U"
delay ms=200
mp135.evb:uart_write data="P"
delay ms=200
mp135.evb:uart_write data="'"
delay ms=200
mp135.evb:uart_write data=" "
delay ms=200
mp135.evb:uart_write data="\x31"
delay ms=200
mp135.evb:uart_write data="\r"
delay ms=1000
mp135.evb:uart_write data="k"
delay ms=200
mp135.evb:uart_write data="i"
delay ms=200
mp135.evb:uart_write data="l"
delay ms=200
mp135.evb:uart_write data="l"
delay ms=200
mp135.evb:uart_write data=" "
delay ms=200
mp135.evb:uart_write data="-"
delay ms=200
mp135.evb:uart_write data="\x31"
delay ms=200
mp135.evb:uart_write data=" "
delay ms=200
mp135.evb:uart_write data="$"
delay ms=200
mp135.evb:uart_write data="$"
delay ms=200
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="TRAPHUP" timeout_ms=8000
delay ms=300
mp135.evb:uart_write data="e"
delay ms=200
mp135.evb:uart_write data="c"
delay ms=200
mp135.evb:uart_write data="h"
delay ms=200
mp135.evb:uart_write data="o"
delay ms=200
mp135.evb:uart_write data=" "
delay ms=200
mp135.evb:uart_write data="H"
delay ms=200
mp135.evb:uart_write data="U"
delay ms=200
mp135.evb:uart_write data="P"
delay ms=200
mp135.evb:uart_write data="S"
delay ms=200
mp135.evb:uart_write data="E"
delay ms=200
mp135.evb:uart_write data="Q"
delay ms=200
mp135.evb:uart_write data="O"
delay ms=200
mp135.evb:uart_write data="K"
delay ms=200
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="HUPSEQOK" timeout_ms=5000
mp135.evb:uart_close
mark tag=evb_trap_hup
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream_text(extract_dir, 'mp135.uart')
    if 'panic' in uart.lower():
        return False
    # Strict ordering: kernel login: -> root shell prompt ->
    # the `TRAPHUP` text emitted by sh's deferred exec of the
    # registered trap command (cmd/sh/fault.c::chktrap calling
    # execexp(trapcom[1], 0) once the shell returns to its
    # prompt cycle after kill -1 $$) -> HUPSEQOK echo emitted
    # by the next foreground command from the same shell.
    # The TRAPHUP token must appear strictly between the shell
    # prompt and the HUPSEQOK token; if it appeared first it
    # would mean sh ran the echo trap command synchronously
    # from the kill builtin, which is not the V7 deferred-trap
    # semantics we want to assert.
    try:
        i_login = uart.index('login:')
        i_shell = uart.index('# ',       i_login)
        i_trap  = uart.index('TRAPHUP',  i_shell)
        uart.index('HUPSEQOK', i_trap)
    except ValueError:
        return False
    return True
```

### EVB shell trap and self-signal with SIGINT over live UART

One-knob delta from the previous EVB section: the same
trap+self-signal pipeline, but for signal 2 (SIGINT) instead of
signal 1 (SIGHUP).  Section 32 proved the full S_SIGNAL +
S_KILL + sigtramp + S_SIGRETURN + chktrap loop for SIGHUP on
real hardware; nothing in section 32 actually exercises the
generic `handlers[sig]` slot for any other signal number.  The
emulator's `deliver_signal()` walks signals 1..NSIG and looks up
`handlers[sig]`, so SIGINT should "just work" if and only if
(a) sh's `stdsigs` table installs a SIGINT slot the same way it
installs SIGHUP, (b) the V7 `kill` builtin parses `-2` and the
literal `INT` mnemonic identically to `-1`/`HUP`, and (c) the
emulator's per-signal bookkeeping in `kkill` and the
`handlers[]` array does not have a SIGHUP-specific code path.
This section converts those three assumptions into a tested
fact, isolating any later ^C-via-`kread` failure (the bigger
gap below) from a hypothetical "SIGINT delivery itself is
broken" alternative explanation.  Pure mission-file change; no
code edits.  The objective UART sentinel chain is: kernel
`login:` -> root shell `# ` -> the literal `TRAPINT` line
emitted by `fault()`'s deferred exec of the registered trap
command -> `INTSEQOK` echoed by the shell after `kill -2 $$`
returns.  Same DFU+SD+jump preamble and 200 ms byte cadence as
the prior EVB trap section; single-quotes around the trap body
are sent as `data="'"` and `$$` as two separate `data="$"`
writes to keep the plan parser literal.  Deliberately retains
the same gaps as section 32: this is a parametrization, not a
new capability landing.  The follow-on `EVB signals and tty
interrupts` section is what lands the `kread`-level ^C
intercept and SIG_DFL termination.

Build:

```
make -C stm32mp135_test_board/bootloader -j$(nproc)
make -C unix-v7-c99 ARCH=arm CONF=evb_arm
rm -f stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
make -C stm32mp135_test_board DTS=stm32mp135f-dk sd-unix
test -s stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
```

Test (max 5 min):

```
bench_mcu:reset_dut
delay ms=2000
dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true
mp135.evb:uart_open
delay ms=300
mp135.evb:uart_write data="x"
delay ms=200
mp135.evb:uart_write data="x"
delay ms=200
mp135.evb:uart_write data="x"
mp135.evb:uart_expect sentinel="> " timeout_ms=8000
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="> " timeout_ms=3000
mp135.evb:uart_close
delay ms=5000
inventory refresh=true verify=false
msc.evb:write data=@unix-sdcard.img offset_lba=0
msc.evb:verify data=@unix-sdcard.img offset_lba=0
mp135.evb:uart_open
delay ms=500
mp135.evb:uart_write data="t"
delay ms=200
mp135.evb:uart_write data="w"
delay ms=200
mp135.evb:uart_write data="o"
delay ms=200
mp135.evb:uart_write data="\r"
delay ms=1000
mp135.evb:uart_write data="l"
delay ms=80
mp135.evb:uart_write data="o"
delay ms=80
mp135.evb:uart_write data="a"
delay ms=80
mp135.evb:uart_write data="d"
delay ms=80
mp135.evb:uart_write data="_"
delay ms=80
mp135.evb:uart_write data="s"
delay ms=80
mp135.evb:uart_write data="d"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x39"
delay ms=80
mp135.evb:uart_write data="\x36"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x33"
delay ms=80
mp135.evb:uart_write data="\x38"
delay ms=80
mp135.evb:uart_write data="\x32"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="x"
delay ms=80
mp135.evb:uart_write data="C"
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\r"
delay ms=3000
mp135.evb:uart_write data="j"
delay ms=200
mp135.evb:uart_write data="u"
delay ms=200
mp135.evb:uart_write data="m"
delay ms=200
mp135.evb:uart_write data="p"
delay ms=200
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="login:" timeout_ms=45000
delay ms=500
mp135.evb:uart_write data="r"
delay ms=200
mp135.evb:uart_write data="o"
delay ms=200
mp135.evb:uart_write data="o"
delay ms=200
mp135.evb:uart_write data="t"
delay ms=200
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=10000
delay ms=200
mp135.evb:uart_write data="t"
delay ms=200
mp135.evb:uart_write data="r"
delay ms=200
mp135.evb:uart_write data="a"
delay ms=200
mp135.evb:uart_write data="p"
delay ms=200
mp135.evb:uart_write data=" "
delay ms=200
mp135.evb:uart_write data="'"
delay ms=200
mp135.evb:uart_write data="e"
delay ms=200
mp135.evb:uart_write data="c"
delay ms=200
mp135.evb:uart_write data="h"
delay ms=200
mp135.evb:uart_write data="o"
delay ms=200
mp135.evb:uart_write data=" "
delay ms=200
mp135.evb:uart_write data="T"
delay ms=200
mp135.evb:uart_write data="R"
delay ms=200
mp135.evb:uart_write data="A"
delay ms=200
mp135.evb:uart_write data="P"
delay ms=200
mp135.evb:uart_write data="I"
delay ms=200
mp135.evb:uart_write data="N"
delay ms=200
mp135.evb:uart_write data="T"
delay ms=200
mp135.evb:uart_write data="'"
delay ms=200
mp135.evb:uart_write data=" "
delay ms=200
mp135.evb:uart_write data="\x32"
delay ms=200
mp135.evb:uart_write data="\r"
delay ms=1000
mp135.evb:uart_write data="k"
delay ms=200
mp135.evb:uart_write data="i"
delay ms=200
mp135.evb:uart_write data="l"
delay ms=200
mp135.evb:uart_write data="l"
delay ms=200
mp135.evb:uart_write data=" "
delay ms=200
mp135.evb:uart_write data="-"
delay ms=200
mp135.evb:uart_write data="\x32"
delay ms=200
mp135.evb:uart_write data=" "
delay ms=200
mp135.evb:uart_write data="$"
delay ms=200
mp135.evb:uart_write data="$"
delay ms=200
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="TRAPINT" timeout_ms=8000
delay ms=300
mp135.evb:uart_write data="e"
delay ms=200
mp135.evb:uart_write data="c"
delay ms=200
mp135.evb:uart_write data="h"
delay ms=200
mp135.evb:uart_write data="o"
delay ms=200
mp135.evb:uart_write data=" "
delay ms=200
mp135.evb:uart_write data="I"
delay ms=200
mp135.evb:uart_write data="N"
delay ms=200
mp135.evb:uart_write data="T"
delay ms=200
mp135.evb:uart_write data="S"
delay ms=200
mp135.evb:uart_write data="E"
delay ms=200
mp135.evb:uart_write data="Q"
delay ms=200
mp135.evb:uart_write data="O"
delay ms=200
mp135.evb:uart_write data="K"
delay ms=200
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="INTSEQOK" timeout_ms=5000
mp135.evb:uart_close
mark tag=evb_trap_int
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream_text(extract_dir, 'mp135.uart')
    if 'panic' in uart.lower():
        return False
    # Strict ordering: kernel login: -> root shell prompt ->
    # the `TRAPINT` text emitted by sh's deferred exec of the
    # registered SIGINT trap command (cmd/sh/fault.c::chktrap
    # calling execexp(trapcom[2], 0) once the shell returns to
    # its prompt cycle after kill -2 $$) -> INTSEQOK echo from
    # the next foreground command on the same shell.  TRAPINT
    # must appear strictly between the root prompt and INTSEQOK,
    # for the same deferred-trap reason as the SIGHUP section.
    try:
        i_login = uart.index('login:')
        i_shell = uart.index('# ',      i_login)
        i_trap  = uart.index('TRAPINT', i_shell)
        uart.index('INTSEQOK', i_trap)
    except ValueError:
        return False
    return True
```

### EVB kread treats ^C byte on tty as EOF

Smallest meaningful slice of the EVB signals section: make a
literal `\x03` byte arriving on the controlling tty terminate
the current user-mode `read(0,...)` with a zero-length return,
matching V7 EOF semantics rather than full SIGINT delivery.
This is deliberately weaker than real SIGINT (which would also
need a working SIG_DFL termination path through deliver_signal
plus an unwinding kwait/kexec flow that we do not yet have in
the sequential-fork model used by armboot.c). For programs
like `cat` that loop `read(0,&c,1)` until a zero return, EOF
on `\x03` is observationally identical to "^C killed cat" from
the shell's point of view: the child exits, the parent shell's
wait returns, and `# ` reappears. We keep the impurity local
to `kread()` and document the gap so a follow-up section can
replace it with proper SIGINT+SIG_DFL termination once the
exit/wait plumbing in armboot.c can carry a non-zero exit
status out of user mode.

Scope: edit `unix-v7-c99/arch/armboot.c::kread()` in the
character-device branch (around lines 896-906) so that when
the byte read from `getchar()` equals `0x03` (ETX / ^C), the
function returns 0 instead of returning 1 and echoing the
byte. All other bytes -- including `\r` (mapped to `\n`),
printable bytes, and the existing echo -- keep their current
behavior. No other source files change. The `\x03` byte is
not echoed, so the shell sees a clean EOF on the cat side and
no stray glyph on the UART transcript.

Build:

```
make -C stm32mp135_test_board/bootloader -j$(nproc)
make -C unix-v7-c99 ARCH=arm CONF=evb_arm
rm -f stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
make -C stm32mp135_test_board DTS=stm32mp135f-dk sd-unix
test -s stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
```

Test (max 5 min):

```
bench_mcu:reset_dut
delay ms=2000
dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true
mp135.evb:uart_open
delay ms=300
mp135.evb:uart_write data="x"
delay ms=200
mp135.evb:uart_write data="x"
delay ms=200
mp135.evb:uart_write data="x"
mp135.evb:uart_expect sentinel="> " timeout_ms=8000
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="> " timeout_ms=3000
mp135.evb:uart_close
delay ms=5000
inventory refresh=true verify=false
msc.evb:write data=@unix-sdcard.img offset_lba=0
msc.evb:verify data=@unix-sdcard.img offset_lba=0
mp135.evb:uart_open
delay ms=500
mp135.evb:uart_write data="t"
delay ms=80
mp135.evb:uart_write data="w"
delay ms=80
mp135.evb:uart_write data="o"
delay ms=80
mp135.evb:uart_write data="\r"
delay ms=1000
mp135.evb:uart_write data="l"
delay ms=80
mp135.evb:uart_write data="o"
delay ms=80
mp135.evb:uart_write data="a"
delay ms=80
mp135.evb:uart_write data="d"
delay ms=80
mp135.evb:uart_write data="_"
delay ms=80
mp135.evb:uart_write data="s"
delay ms=80
mp135.evb:uart_write data="d"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x39"
delay ms=80
mp135.evb:uart_write data="\x36"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x33"
delay ms=80
mp135.evb:uart_write data="\x38"
delay ms=80
mp135.evb:uart_write data="\x32"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="x"
delay ms=80
mp135.evb:uart_write data="C"
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\r"
delay ms=3000
mp135.evb:uart_write data="j"
delay ms=80
mp135.evb:uart_write data="u"
delay ms=80
mp135.evb:uart_write data="m"
delay ms=80
mp135.evb:uart_write data="p"
delay ms=80
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="login:" timeout_ms=45000
mp135.evb:uart_write data="root\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=10000
mp135.evb:uart_write data="cat\r"
delay ms=500
mp135.evb:uart_write data="hello\r"
mp135.evb:uart_expect sentinel="hheelllloo" timeout_ms=5000
mp135.evb:uart_write data="\x03"
mp135.evb:uart_expect sentinel="# " timeout_ms=8000
mp135.evb:uart_write data="echo CATEOFOK\r"
mp135.evb:uart_expect sentinel="CATEOFOK" timeout_ms=3000
mp135.evb:uart_close
mark tag=evb_kread_ctrlc_eof
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream_text(extract_dir, 'mp135.uart')
    if 'panic' in uart.lower():
        return False
    # Strict ordering: login: -> root prompt -> the `cat`
    # command echo -> the `hello` line cat echoes back ->
    # the prompt that only reappears once cat exits on the
    # ^C-as-EOF path -> CATEOFOK from the next foreground
    # command on the same shell. The reappearance of `# `
    # *after* the hello echo is the load-bearing evidence
    # that kread() returned 0 on \x03 and cat exited; before
    # this change cat would have blocked forever on its next
    # read() and `# ` would never come back, failing the
    # CATEOFOK expect.
    try:
        i_login = uart.index('login:')
        i_sh1   = uart.index('# ',         i_login)
        # On the real EVB tty path each input byte is echoed
        # twice: once by kread()'s in-line echo and once by
        # cat itself reading the byte and writing it to stdout.
        # So "hello\r" arrives as "hheelllloo\r\n". We probe
        # for the doubled tail as proof that cat is consuming
        # bytes from its read loop on the live UART.
        i_dbl   = uart.index('hheelllloo', i_sh1)
        # cat echoed the doubled "hello", then we need a *new*
        # `# ` after it -- proof that kread() returned 0 on
        # \x03 and cat exited; before this change cat would
        # have blocked forever on its next read().
        i_sh2   = uart.index('# ',         i_dbl)
        uart.index('CATEOFOK', i_sh2)
    except ValueError:
        return False
    return True
```

## WIP

### EVB signals and tty interrupts

Bench-side counterpart to the qemu signals section. Real
interrupt latency on `^C` delivery from the UART differs from
qemu's; this section catches the V7 controlling-tty
signal-delivery path under real timing. Sends a literal `\x03`
byte (^C) to a long-running `cat`, expects the cat to die with
the right exit indication, and exercises `kill -HUP $$` and
`trap` over the live UART.

Build:

```
make -C stm32mp135_test_board/bootloader -j$(nproc)
make -C unix-v7-c99 ARCH=arm CONF=evb_arm
rm -f stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
make -C stm32mp135_test_board DTS=stm32mp135f-dk sd-unix
test -s stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
```

Test (max 5 min):

```
bench_mcu:reset_dut
delay ms=2000
dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true
mp135.evb:uart_open
delay ms=300
mp135.evb:uart_write data="x"
delay ms=200
mp135.evb:uart_write data="x"
delay ms=200
mp135.evb:uart_write data="x"
mp135.evb:uart_expect sentinel="> " timeout_ms=8000
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="> " timeout_ms=3000
mp135.evb:uart_close
delay ms=5000
inventory refresh=true verify=false
msc.evb:write data=@unix-sdcard.img offset_lba=0
msc.evb:verify data=@unix-sdcard.img offset_lba=0
mp135.evb:uart_open
delay ms=500
mp135.evb:uart_write data="t"
delay ms=80
mp135.evb:uart_write data="w"
delay ms=80
mp135.evb:uart_write data="o"
delay ms=80
mp135.evb:uart_write data="\r"
delay ms=1000
mp135.evb:uart_write data="l"
delay ms=80
mp135.evb:uart_write data="o"
delay ms=80
mp135.evb:uart_write data="a"
delay ms=80
mp135.evb:uart_write data="d"
delay ms=80
mp135.evb:uart_write data="_"
delay ms=80
mp135.evb:uart_write data="s"
delay ms=80
mp135.evb:uart_write data="d"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x39"
delay ms=80
mp135.evb:uart_write data="\x36"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x33"
delay ms=80
mp135.evb:uart_write data="\x38"
delay ms=80
mp135.evb:uart_write data="\x32"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="x"
delay ms=80
mp135.evb:uart_write data="C"
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\r"
delay ms=3000
mp135.evb:uart_write data="j"
delay ms=80
mp135.evb:uart_write data="u"
delay ms=80
mp135.evb:uart_write data="m"
delay ms=80
mp135.evb:uart_write data="p"
delay ms=80
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="login:" timeout_ms=45000
mp135.evb:uart_write data="root\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=10000
mp135.evb:uart_write data="trap 'echo HUPGOT' 1; (sleep 1; kill -HUP $$) ; echo HUPSEQOK\r"
mp135.evb:uart_expect sentinel="HUPGOT"   timeout_ms=8000
mp135.evb:uart_expect sentinel="HUPSEQOK" timeout_ms=8000
mp135.evb:uart_write data="cat\r"
delay ms=500
mp135.evb:uart_write data="\x03"
mp135.evb:uart_expect sentinel="# " timeout_ms=5000
mp135.evb:uart_write data="echo INTOK\r"
mp135.evb:uart_expect sentinel="INTOK" timeout_ms=3000
mp135.evb:uart_close
mark tag=evb_signals
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream_text(extract_dir, 'mp135.uart')
    if 'panic' in uart.lower():
        return False
    try:
        i_login = uart.index('login:')
        i_hup   = uart.index('HUPGOT',   i_login)
        i_seq   = uart.index('HUPSEQOK', i_hup)
        uart.index('INTOK', i_seq)
    except ValueError:
        return False
    return True
```

### EVB multi-user login and su

Bench-side counterpart to the qemu multi-user section. Drives
a non-root login (user `dmr`) over the real EVB UART, which
exercises `getty` baud-rate detection, the V7 login-prompt
collation timer, and the real-tty echo-on/echo-off transition
during password entry -- all of which qemu's serial backend
elides. Then `su root` and a setuid program test, mirroring the
qemu fixture.

Build:

```
make -C stm32mp135_test_board/bootloader -j$(nproc)
make -C unix-v7-c99 ARCH=arm CONF=evb_arm
rm -f stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
make -C stm32mp135_test_board DTS=stm32mp135f-dk sd-unix
test -s stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
```

Test (max 6 min):

```
bench_mcu:reset_dut
delay ms=2000
dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true
mp135.evb:uart_open
delay ms=300
mp135.evb:uart_write data="x"
delay ms=200
mp135.evb:uart_write data="x"
delay ms=200
mp135.evb:uart_write data="x"
mp135.evb:uart_expect sentinel="> " timeout_ms=8000
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="> " timeout_ms=3000
mp135.evb:uart_close
delay ms=5000
inventory refresh=true verify=false
msc.evb:write data=@unix-sdcard.img offset_lba=0
msc.evb:verify data=@unix-sdcard.img offset_lba=0
mp135.evb:uart_open
delay ms=500
mp135.evb:uart_write data="t"
delay ms=80
mp135.evb:uart_write data="w"
delay ms=80
mp135.evb:uart_write data="o"
delay ms=80
mp135.evb:uart_write data="\r"
delay ms=1000
mp135.evb:uart_write data="l"
delay ms=80
mp135.evb:uart_write data="o"
delay ms=80
mp135.evb:uart_write data="a"
delay ms=80
mp135.evb:uart_write data="d"
delay ms=80
mp135.evb:uart_write data="_"
delay ms=80
mp135.evb:uart_write data="s"
delay ms=80
mp135.evb:uart_write data="d"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x39"
delay ms=80
mp135.evb:uart_write data="\x36"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x33"
delay ms=80
mp135.evb:uart_write data="\x38"
delay ms=80
mp135.evb:uart_write data="\x32"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="x"
delay ms=80
mp135.evb:uart_write data="C"
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\r"
delay ms=3000
mp135.evb:uart_write data="j"
delay ms=80
mp135.evb:uart_write data="u"
delay ms=80
mp135.evb:uart_write data="m"
delay ms=80
mp135.evb:uart_write data="p"
delay ms=80
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="login:" timeout_ms=45000
mp135.evb:uart_write data="dmr\r"
mp135.evb:uart_expect sentinel="assword" timeout_ms=5000
mp135.evb:uart_write data="dmrpw\r"
mp135.evb:uart_expect sentinel="$ " timeout_ms=10000
mp135.evb:uart_write data="who am i; echo WHOAMIOK\r"
mp135.evb:uart_expect sentinel="WHOAMIOK" timeout_ms=5000
mp135.evb:uart_write data="su root\r"
mp135.evb:uart_expect sentinel="assword" timeout_ms=5000
mp135.evb:uart_write data="rootpw\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=10000
mp135.evb:uart_write data="echo ROOTOK\r"
mp135.evb:uart_expect sentinel="ROOTOK" timeout_ms=5000
mp135.evb:uart_close
mark tag=evb_multiuser
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream_text(extract_dir, 'mp135.uart')
    if 'panic' in uart.lower():
        return False
    try:
        i_login   = uart.index('login:')
        i_dmr     = uart.index('dmr',         i_login)
        i_dollar  = uart.index('$ ',          i_dmr)
        i_whoami  = uart.index('WHOAMIOK',    i_dollar)
        i_hash    = uart.index('# ',          i_whoami)
        uart.index('ROOTOK', i_hash)
    except ValueError:
        return False
    # 'dmr' must surface in `who am i` output before WHOAMIOK.
    return 'dmr' in uart[i_dollar:i_whoami]
```

### Full end-to-end on EVB: cold reset -> SD -> shell

Flagship and mission pass gate: exercises every link from a
power-on state. Catches anything the per-stage sections silently
let through -- in particular, regressions whose visible symptom
only appears after a successful cold-boot interactively drives
the shell (signal delivery from a controlling tty, the EVB
console's tx-side flow-control under burst write, root-shell
exec from `getty` after `login:`). Resets, DFU-flashes the
bootloader, holds at `> `, MSC-writes `unix-sdcard.img`, then
`two`+`jump`, waits for the V7 banner and `login:`, drives
`root\r`, waits for `# `, and runs
`echo unix-v7-mp135-evb-ok; pwd; ls /bin; sync; exit\r`. Verifier
position-anchors the sentinel against the typed input echo so a
planted printf cannot win the gate.

Build:

```
make -C stm32mp135_test_board/bootloader -j$(nproc)
make -C unix-v7-c99 ARCH=arm CONF=evb_arm
rm -f stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
make -C stm32mp135_test_board DTS=stm32mp135f-dk sd-unix
test -s stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/unix-sdcard.img
```

Test (max 10 min):

```
bench_mcu:reset_dut
delay ms=2000
dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true
mp135.evb:uart_open
delay ms=300
mp135.evb:uart_write data="x"
delay ms=200
mp135.evb:uart_write data="x"
delay ms=200
mp135.evb:uart_write data="x"
mp135.evb:uart_expect sentinel="> " timeout_ms=8000
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="> " timeout_ms=3000
mp135.evb:uart_close
delay ms=5000
inventory refresh=true verify=false
msc.evb:write data=@unix-sdcard.img offset_lba=0
msc.evb:verify data=@unix-sdcard.img offset_lba=0
mp135.evb:uart_open
delay ms=500
mp135.evb:uart_write data="t"
delay ms=80
mp135.evb:uart_write data="w"
delay ms=80
mp135.evb:uart_write data="o"
delay ms=80
mp135.evb:uart_write data="\r"
delay ms=1000
mp135.evb:uart_write data="l"
delay ms=80
mp135.evb:uart_write data="o"
delay ms=80
mp135.evb:uart_write data="a"
delay ms=80
mp135.evb:uart_write data="d"
delay ms=80
mp135.evb:uart_write data="_"
delay ms=80
mp135.evb:uart_write data="s"
delay ms=80
mp135.evb:uart_write data="d"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x39"
delay ms=80
mp135.evb:uart_write data="\x36"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x33"
delay ms=80
mp135.evb:uart_write data="\x38"
delay ms=80
mp135.evb:uart_write data="\x32"
delay ms=80
mp135.evb:uart_write data=" "
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="x"
delay ms=80
mp135.evb:uart_write data="C"
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\x30"
delay ms=80
mp135.evb:uart_write data="\r"
delay ms=3000
mp135.evb:uart_write data="j"
delay ms=80
mp135.evb:uart_write data="u"
delay ms=80
mp135.evb:uart_write data="m"
delay ms=80
mp135.evb:uart_write data="p"
delay ms=80
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="Jumping to address" timeout_ms=5000
mp135.evb:uart_expect sentinel="mem = " timeout_ms=15000
mp135.evb:uart_expect sentinel="login:" timeout_ms=30000
mp135.evb:uart_write data="root\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=10000
mp135.evb:uart_write data="echo unix-v7-mp135-evb-ok\r"
mp135.evb:uart_expect sentinel="unix-v7-mp135-evb-ok" timeout_ms=5000
mp135.evb:uart_write data="pwd\r"
mp135.evb:uart_expect sentinel="/" timeout_ms=5000
mp135.evb:uart_write data="ls /bin\r"
mp135.evb:uart_expect sentinel="sh" timeout_ms=5000
mp135.evb:uart_write data="sync\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=5000
mp135.evb:uart_write data="exit\r"
mp135.evb:uart_close
mark tag=evb_full_e2e
```

Verify:

```
import re

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream_text(extract_dir, 'mp135.uart')
    if 'panic' in uart.lower():
        return False
    # Strict ordering, all in the captured UART stream:
    #   Jumping to address -> mem = N (N >= 100) -> login: ->
    #   # (root shell) -> typed echo command -> echo's *output*
    #   line (a SECOND occurrence of the sentinel after the
    #   typed input echo). The two-occurrence rule rules out a
    #   kernel printf that just prints the sentinel string.
    try:
        i_jump   = uart.index('Jumping to address')
        i_mem    = uart.index('mem = ', i_jump)
        if not re.search(r'mem = [1-9]\d{2,}', uart[i_mem:]):
            return False
        i_login  = uart.index('login:', i_mem)
        i_prompt = uart.index('# ', i_login)
        i_typed  = uart.index('echo unix-v7-mp135-evb-ok', i_prompt)
        uart.index('unix-v7-mp135-evb-ok',
                   i_typed + len('echo unix-v7-mp135-evb-ok'))
    except ValueError:
        return False
    return True
```
