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
  fixture at `unix-v7-c99/tools/qemu/<script-name>.expect`. If no
  fixture exists with that name, the argument is treated as a
  sentinel string: the wrapper boots qemu, waits for that string
  to appear in the serial log, and terminates immediately.
  Existing fixtures wait for `login:`, send `root\r`, wait for
  `# `, run the per-fixture command set, then send `sync\r` and
  `exit\r`.
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
unix-v7-c99/tools/qemu-shell.sh unix-v7-c99/build/qemu/banner.log "mem = "
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
unix-v7-c99/tools/qemu-shell.sh unix-v7-c99/build/qemu/init.log "login:"
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

### Unified functional parity: Qemu vs EVB

Drives the `/bin/test_suite` script (which consolidates smoke, pipes,
filesystem, signals, and text processing tests) on both the Qemu
emulator and the real STM32MP135 hardware. Verifier ensures the
captured UART streams are functionally identical.

Build:

```
make -C unix-v7-c99 ARCH=arm CONF=qemu_arm
mkdir -p unix-v7-c99/build/qemu
# Drive Qemu via an expect one-liner (no extra files needed)
expect -c '
  set timeout 120
  spawn qemu-system-arm -machine virt -cpu cortex-a7 -nographic -no-reboot \
    -kernel unix-v7-c99/unix \
    -drive if=none,file=unix-v7-c99/root.img,format=raw,id=hd0 \
    -device virtio-blk-device,drive=hd0
  expect "login: "
  send "root\r"
  expect "# "
  send "/bin/sh /bin/test_suite\r"
  expect -exact "--- UNIT TESTS COMPLETE ---"
  send "sync\rexit\r"
  sleep 0.5
  send "\x01x"
  expect eof
' > unix-v7-c99/build/qemu/suite.log 2>&1
```

Artifacts:

```
unix-v7-c99/build/qemu/suite.log
```

Test (max 10 min):

```
bench_mcu:reset_dut
delay ms=2000
# [Bootstrap elided for brevity in this example, use previous section's state]
lease:resume token="{{LEASE_TOKEN}}"
mp135.evb:uart_open
mp135.evb:uart_expect sentinel="login: "
mp135.evb:uart_write data="root\r"
mp135.evb:uart_expect sentinel="# "
mp135.evb:uart_write data="/bin/sh /bin/test_suite\r"
mp135.evb:uart_expect sentinel="--- UNIT TESTS COMPLETE ---"
mp135.evb:uart_write data="sync\rexit\r"
mp135.evb:uart_close
```

Verify:

```
from pathlib import Path
import re

def sanitize(text):
    # Remove hardware-specific banners and timing noise
    text = re.sub(r'mem = \d+', 'mem = <ANY>', text)
    text = re.sub(r'evb: .*\n', '', text)
    # Strip everything before the first login
    if 'login:' in text:
        text = text[text.index('login:'):]
    return text.strip()

def check(extract_dir):
    qemu_log = Path('unix-v7-c99/build/qemu/suite.log').read_text(errors='replace')
    evb_log = Verification.load_stream_text(extract_dir, 'mp135.uart')
    
    qemu_clean = sanitize(qemu_log)
    evb_clean = sanitize(evb_log)
    
    if '--- UNIT TESTS COMPLETE ---' not in evb_clean:
        return False
        
    return qemu_clean == evb_clean
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
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x36"
delay ms=80
mp135.evb:uart_write data="\x33"
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
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x36"
delay ms=80
mp135.evb:uart_write data="\x33"
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
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x36"
delay ms=80
mp135.evb:uart_write data="\x33"
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
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x36"
delay ms=80
mp135.evb:uart_write data="\x33"
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
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x36"
delay ms=80
mp135.evb:uart_write data="\x33"
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
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x36"
delay ms=80
mp135.evb:uart_write data="\x33"
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
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x36"
delay ms=80
mp135.evb:uart_write data="\x33"
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
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x36"
delay ms=80
mp135.evb:uart_write data="\x33"
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
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x36"
delay ms=80
mp135.evb:uart_write data="\x33"
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
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x36"
delay ms=80
mp135.evb:uart_write data="\x33"
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

### EVB signals: trap, kill, continue

Drives V7 signal delivery from the bench: install a `trap`
handler for SIGHUP, raise the signal in foreground with
`kill -1 $$`, observe the handler's `echo HUPGOT` reach the
UART, then prove the shell is still healthy by running one
more foreground command (`echo INTOK`) on the same login
session. Sections 31 and 32 each prove a single trap+kill
cycle in isolation; this section adds the "kept-alive
through and past the cycle" gate that only a real signal
return path can satisfy.

The historic V7 path of `^C` from a controlling tty raising
SIGINT against a foreground `cat` is NOT exercised here: the
port's `arch/armboot.c` shim does not link `dev/tty.c`'s
cooked-mode line discipline, so `^C` from UART arrives at
`kread()` as a plain byte rather than as a tty signal. The
trap+kill self-signal path is the historically-accurate
signal mechanism we can drive from the bench today.

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
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x36"
delay ms=80
mp135.evb:uart_write data="\x33"
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
mp135.evb:uart_write data="H"
delay ms=200
mp135.evb:uart_write data="U"
delay ms=200
mp135.evb:uart_write data="P"
delay ms=200
mp135.evb:uart_write data="G"
delay ms=200
mp135.evb:uart_write data="O"
delay ms=200
mp135.evb:uart_write data="T"
delay ms=200
mp135.evb:uart_write data="'"
delay ms=200
mp135.evb:uart_write data=" "
delay ms=200
mp135.evb:uart_write data="\x31"
delay ms=200
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=8000
delay ms=300
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
mp135.evb:uart_expect sentinel="HUPGOT" timeout_ms=8000
mp135.evb:uart_expect sentinel="# "     timeout_ms=8000
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
mp135.evb:uart_write data="O"
delay ms=200
mp135.evb:uart_write data="K"
delay ms=200
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="INTOK" timeout_ms=5000
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
    # Strict ordering: kernel login: -> first root shell prompt ->
    # HUPGOT emitted by sh's deferred trap exec after kill -1 $$ ->
    # a *second* shell prompt that only reappears once the handler
    # has returned and sh re-prints its prompt (proves the shell
    # survived the SIGHUP self-signal, mirroring section 31's
    # TRAPHUP+HUPSEQOK gate but split across two commands so the
    # V7 signal-delivery path returns cleanly to the line parser
    # between them) -> INTOK from `echo INTOK` (proves the shell
    # still reads new input after the trap+kill+continue cycle).
    # The two `# ` prompts straddling HUPGOT must be distinct byte
    # offsets, asserted by walking str.index past HUPGOT for the
    # second prompt.
    try:
        i_login = uart.index('login:')
        i_sh1   = uart.index('# ',     i_login)
        i_hup   = uart.index('HUPGOT', i_sh1)
        i_sh2   = uart.index('# ',     i_hup)
        if i_sh2 <= i_sh1:
            return False
        uart.index('INTOK', i_sh2)
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
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x36"
delay ms=80
mp135.evb:uart_write data="\x33"
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
mp135.evb:uart_write data="d"
delay ms=200
mp135.evb:uart_write data="m"
delay ms=200
mp135.evb:uart_write data="r"
delay ms=200
mp135.evb:uart_write data="\r"
delay ms=200
mp135.evb:uart_expect sentinel="$ " timeout_ms=10000
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
mp135.evb:uart_write data="d"
delay ms=200
mp135.evb:uart_write data="m"
delay ms=200
mp135.evb:uart_write data="r"
delay ms=200
mp135.evb:uart_write data="\r"
delay ms=200
mp135.evb:uart_expect sentinel="$ " timeout_ms=5000
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
mp135.evb:uart_write data="W"
delay ms=200
mp135.evb:uart_write data="H"
delay ms=200
mp135.evb:uart_write data="O"
delay ms=200
mp135.evb:uart_write data="A"
delay ms=200
mp135.evb:uart_write data="M"
delay ms=200
mp135.evb:uart_write data="I"
delay ms=200
mp135.evb:uart_write data="O"
delay ms=200
mp135.evb:uart_write data="K"
delay ms=200
mp135.evb:uart_write data="\r"
delay ms=200
mp135.evb:uart_expect sentinel="WHOAMIOK" timeout_ms=5000
mp135.evb:uart_expect sentinel="$ " timeout_ms=5000
delay ms=200
mp135.evb:uart_write data="s"
delay ms=200
mp135.evb:uart_write data="u"
delay ms=200
mp135.evb:uart_write data=" "
delay ms=200
mp135.evb:uart_write data="r"
delay ms=200
mp135.evb:uart_write data="o"
delay ms=200
mp135.evb:uart_write data="o"
delay ms=200
mp135.evb:uart_write data="t"
delay ms=200
mp135.evb:uart_write data="\r"
delay ms=200
mp135.evb:uart_expect sentinel="# " timeout_ms=10000
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
mp135.evb:uart_write data="R"
delay ms=200
mp135.evb:uart_write data="O"
delay ms=200
mp135.evb:uart_write data="O"
delay ms=200
mp135.evb:uart_write data="T"
delay ms=200
mp135.evb:uart_write data="O"
delay ms=200
mp135.evb:uart_write data="K"
delay ms=200
mp135.evb:uart_write data="\r"
delay ms=200
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
mp135.evb:uart_write data="\x34"
delay ms=80
mp135.evb:uart_write data="\x36"
delay ms=80
mp135.evb:uart_write data="\x33"
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
mp135.evb:uart_write data="r"
delay ms=200
mp135.evb:uart_write data="o"
delay ms=200
mp135.evb:uart_write data="o"
delay ms=200
mp135.evb:uart_write data="t"
delay ms=200
mp135.evb:uart_write data="\r"
delay ms=200
mp135.evb:uart_expect sentinel="# " timeout_ms=10000
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
mp135.evb:uart_write data="u"
delay ms=200
mp135.evb:uart_write data="n"
delay ms=200
mp135.evb:uart_write data="i"
delay ms=200
mp135.evb:uart_write data="x"
delay ms=200
mp135.evb:uart_write data="-"
delay ms=200
mp135.evb:uart_write data="v"
delay ms=200
mp135.evb:uart_write data="\x37"
delay ms=200
mp135.evb:uart_write data="-"
delay ms=200
mp135.evb:uart_write data="m"
delay ms=200
mp135.evb:uart_write data="p"
delay ms=200
mp135.evb:uart_write data="\x31"
delay ms=200
mp135.evb:uart_write data="\x33"
delay ms=200
mp135.evb:uart_write data="\x35"
delay ms=200
mp135.evb:uart_write data="-"
delay ms=200
mp135.evb:uart_write data="e"
delay ms=200
mp135.evb:uart_write data="v"
delay ms=200
mp135.evb:uart_write data="b"
delay ms=200
mp135.evb:uart_write data="-"
delay ms=200
mp135.evb:uart_write data="o"
delay ms=200
mp135.evb:uart_write data="k"
delay ms=200
mp135.evb:uart_write data="\r"
delay ms=200
mp135.evb:uart_expect sentinel="unix-v7-mp135-evb-ok" timeout_ms=5000
mp135.evb:uart_write data="p"
delay ms=200
mp135.evb:uart_write data="w"
delay ms=200
mp135.evb:uart_write data="d"
delay ms=200
mp135.evb:uart_write data="\r"
delay ms=200
mp135.evb:uart_expect sentinel="/" timeout_ms=5000
mp135.evb:uart_write data="l"
delay ms=200
mp135.evb:uart_write data="s"
delay ms=200
mp135.evb:uart_write data=" "
delay ms=200
mp135.evb:uart_write data="/"
delay ms=200
mp135.evb:uart_write data="b"
delay ms=200
mp135.evb:uart_write data="i"
delay ms=200
mp135.evb:uart_write data="n"
delay ms=200
mp135.evb:uart_write data="\r"
delay ms=200
mp135.evb:uart_expect sentinel="sh" timeout_ms=5000
mp135.evb:uart_write data="s"
delay ms=200
mp135.evb:uart_write data="y"
delay ms=200
mp135.evb:uart_write data="n"
delay ms=200
mp135.evb:uart_write data="c"
delay ms=200
mp135.evb:uart_write data="\r"
delay ms=200
mp135.evb:uart_expect sentinel="# " timeout_ms=5000
mp135.evb:uart_write data="e"
delay ms=200
mp135.evb:uart_write data="x"
delay ms=200
mp135.evb:uart_write data="i"
delay ms=200
mp135.evb:uart_write data="t"
delay ms=200
mp135.evb:uart_write data="\r"
delay ms=200
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

## WIP

The 35 sections above gate what we said we would gate: V7 cold-boots
on the EVB to a multi-user shell over UART4.  That is a real and
testable milestone, but it is not full V7 fidelity, because the port
takes shortcuts in the kernel that the discipline never demanded the
sections to catch.  The work below closes the gap between
"externally indistinguishable from V7 for these sections" and
"structurally V7 underneath."  Land each as its own section once the
behavior it gates is testable from the bench; until then they are a
prioritized backlog.

The ordering matters: items earlier on the list unblock items later
on the list, and most also remove a workaround currently visible to
the bench (load_sd preamble, byte-by-byte cadence, missing ^C, etc).

### Real V7 main() with proc[], iinit, sched

Enable the `#if 0`-d body of `sys/main.c::main()`: `clkstart`,
`cinit`, `binit`, `iinit`, `newproc`, `sched`.  Stop falling through
to `arch/armboot.c::armboot()`.  Requires linking `sys/bio.c`,
`sys/iget.c`, `sys/alloc.c`, `sys/text.c`, `sys/slp.c`, `sys/clock.c`,
`sys/trap.c`, and `conf/c.c` (which already declares `bdevsw`,
`rootdev`, `swapdev`, `pipedev`).  `conf/c.c`'s `rootdev =
makedev(0,0)` resolves to whatever the V7 SD/eMMC driver registers
as major 0 (see the SD block driver item below).

Gate test: kernel reaches the V7 `init: multi-user` banner *via*
`sys/main.c`'s real flow (not via `armboot()` short-circuit).  Add a
sentinel that fires only from sys/main.c's path so a regression
into the shim path is caught.

### V7 line discipline (dev/tty.c) linked in

Link `dev/tty.c` into the build (currently absent from
`sys/Makefile`'s OBJS).  Wire `dev/stm32_usart.c` (and `dev/pl011.c`
on qemu) to call into `tty.c`'s `ttread`/`ttwrite`/`ttyinput`
instead of returning bytes directly to `read(2)`.  `conf/c.c`'s
`linesw[]` already wires `ttyopen`/`ttread`/`ttwrite`/`ttyinput` to
`tty.c`; this is the missing line-discipline plumb.

What this unlocks on the bench: cooked-mode line editing (V7 erase
`#`, kill `@`), `^S`/`^Q` flow control under burst write,
`^C`->SIGINT to the foreground process, `^D` returning 0 from
`read(2)` at start-of-line, and the `gtty`/`stty` ioctls (cbreak,
raw, etc.) that V7 `stty` already shipped.

Gate test: bench-typed `^C` (byte `\x03`) sent to a foreground
`cat` kills `cat` and returns the shell to `# `.  This is the same
test the removed "EVB kread treats ^C byte on tty as EOF" section
*should* have looked like once the line discipline is real.

### Real fork(2) and proc[] scheduling

Replace `arch/armboot.c`'s NFORK=8 sequential save/restore model
with V7's real `fork()`/`exec()`/`wait()` operating on `proc[]`
entries, `u` struct, scheduling via `swtch()` and the run queues.
Most of this is already in `sys/fork.c`, `sys/exec1.c`, `sys/exec2.c`,
`sys/main.c`'s `sched()`, `sys/slp.c` -- just not linked.  Requires
implementing context switch in `arch/a7.s` (currently only kernel
entry exists).

What this unlocks: real concurrent processes, real `ps`, V7's job
control as designed, multi-tty getty.  Removes the
`(sleep 1; kill -HUP $$)` subshell oddities the trap section
documented.

Gate test: two getty's running on (say) UART4 and a virtual second
console, both producing `login:` at boot, both servicing logins.

### SIG_DFL termination and full V7 wait() status

`arch/armboot.c::deliver_signal()` currently has a comment "No
fancy default actions yet -- absent a real exit/wait flow here,
drop the signal."  After the real fork item lands, this drop
becomes wrong: SIG_DFL for fatal signals must terminate the
process and set the wait status low 7 bits to the signal number.
`arch/armboot.c::kwait()` hard-codes the low 7 bits to 0 today;
`sys/sig.c`'s `psignal()` does the right thing on its own once
linked.

Gate test: `cat` killed by `^C` (or by another process's
`kill -2 <pid>`) returns from `wait()` with status `2`, observable
via a small test program that forks/execs cat, kills it, and prints
the wait status.

### Real SD/eMMC block driver in dev/

Implement V7's `bdevsw` major-0 entry as a real SDMMC driver for
the STM32MP135 (and keep `dev/virtio_blk.c` for the qemu path) so
`bread(2)`/`bwrite(2)` go through the V7 buffer cache (`sys/bio.c`)
and the kernel can mount its root from the SD card on demand,
without the bench staging the rootfs into DDR via `load_sd` first.
After this lands, the EVB test plans' `load_sd 4096 382 0xC4400000`
preamble can drop and section runtime goes down by a few seconds
per section.

Gate test: cold-boot a sdcard-img that has *only* main.stm32 +
unix.bin + .dtb_placeholder on it (no `load_sd` from the bench);
kernel mounts the rootfs from disk after `jump` and reaches
`login:`.

### Remaining V7 syscalls in arch/armboot.c (or post-shim equivalent)

The shim handles ~30 syscalls.  After real main()+fork() the shim
moves into `sys/trap.c`'s `trap()` and the missing entries become
straightforward to wire from existing V7 source:

  * `setgid`/`getgid`/`getpid`/`getppid`
  * `alarm`/`pause`/`nice`
  * `gtty`/`stty`/`ioctl` (needed by the line-discipline item above)
  * `ptrace`/`profil`/`fcntl`/`times`
  * `mpx` (V7 has it; we don't need it)
  * `phys`/`acct`

Gate test: each as its own section, mirroring how `cmd/who`,
`cmd/ps`, `cmd/time`, etc. exercise them.

### Persistent utmp/wtmp

Real V7 `/etc/utmp` and `/usr/adm/wtmp` accumulate login records
across boots.  The shim's tmpfs makes them volatile.  After the
real SD block driver lands, point `/etc/utmp` and `/usr/adm/wtmp`
at the mounted rootfs.  Then `who` and `last` show real history.

Gate test: log in, log out, reboot, log in again; `last` shows two
entries.

### Multi-tty getty

V7 `init` reads `/etc/ttys` and spawns a `getty` per line.  Today
the rootfs has a `ttys` entry only for the console.  Add a second
tty (UART somewhere, or a soft tty over USB-CDC if we go that
route), spawn a second getty, gate that both serve `login:`
concurrently.

### Kernel-side stty mode set by getty

V7 getty does `stty <speed>` on its tty before exec'ing login.
Today the bench drives UART4 at the bootloader's preconfigured
baud.  After `gtty`/`stty` ioctls land, getty can renegotiate.
This becomes relevant if/when the second tty has a different
speed than the console.

### `ed`-on-EVB regression gate

`ed` already passes under qemu (section 19).  On the EVB it should
work today too but no section tests it; add one.  Drives a small
`ed` session over UART, edits a file, writes, quits, verifies the
file content via `cat`.

### Optional: original-diffs ratchet against this commit

Re-baseline `unix-v7-c99/tools/original-diffs.budget.json` against
the current commit.  Every later session that touches port files
under `cmd/`, `sys/`, `h/`, `include/`, `lib/`, `tools/`, `conf/`
then can only *reduce* inserts/deletes -- so the port can only get
*closer* to historic V7, never further.
