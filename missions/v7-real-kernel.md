# Real V7 kernel on Armv7-A (no shim)

The `unix-on-stm32mp135.md` mission gated on V7 userspace reaching a
multi-user shell on the STM32MP135 EVB.  Every section there was
satisfied by a kernel-side shim in `arch/armboot.c` that re-implements
fork, exec, wait, namei, bread, signal delivery, and the V7 syscall
dispatcher *in parallel* with the real V7 source in `sys/`.  The shim
let us ship a checkpoint; it is not the destination.

This mission removes the shim.  When it's done, the kernel will run
V7's own `sys/main.c::main()`, V7's own `sys/trap.c::trap()` for
syscalls, V7's own `sys/bio.c` buffer cache, V7's own
`sys/fork.c`+`sys/slp.c` for processes and scheduling, V7's own
`sys/sig.c` for signal delivery, V7's own `dev/tty.c` for cooked-mode
line discipline, and `arch/armboot.c` shrinks to zero lines.

The `unix-v7-c99/tools/original-diffs.sh` ratchet enforces that V7
source under `cmd/`, `sys/`, `h/`, `include/`, `lib/`, `tools/`, and
`conf/` only gets *closer* to historic V7 over this mission: every
file we move INTO the build is in unmodified or only-C99-prototyped
form, so the insert/delete counts against `v7/usr/...` strictly
decrease.

Two anchor invariants for every section in this file:

  1. **No regression on hardware.**  After each section lands,
     a fresh cold boot on the EVB still reaches `login:` and accepts
     `root` and `dmr` logins.  The unix-on-stm32mp135.md sections do
     NOT need to keep passing once their behavior is satisfied by
     the real kernel -- their shim-specific test plans can be
     replaced, removed, or marked obsolete in this mission.

  2. **Shim shrinks monotonically.**  `wc -l arch/armboot.c` must
     decrease (or stay the same) at every commit.  The shim cannot
     grow during this mission.  Net code-of-interest moves from
     `arch/armboot.c` into `sys/*.c` and `dev/*.c`.

Section order matters: items earlier on the list unblock items
later on the list.  Tester runs all sections through the WIP marker;
the WIP marker moves forward only when each section's verify check
passes on bench.

### V7 dev/bio.c compiles and links into kernel (no caller)

Smallest forward increment toward the parent section: add
`../dev/bio.o` to `unix-v7-c99/sys/Makefile`'s `OBJS` so that
the V7 buffer-cache translation unit (`bread`, `breada`,
`bwrite`, `bdwrite`, `bawrite`, `brelse`, `getblk`, `iowait`,
`iodone`, `clrbuf`, `geteblk`, `swap`, `physio`) compiles
unmodified V7 source under our `arm-none-eabi-gcc -std=c99`
toolchain alongside the existing kernel headers, and that the
final `unix` ELF still links.

No caller is added in this sub-step.  `bread` and friends
become defined but unreferenced symbols in the kernel ELF;
`arch/armboot.c::bio()` is unchanged and continues to satisfy
every existing kernel block read on hardware.  Behavior on the
EVB is byte-identical to the prior commit.

This sub-step de-risks the much larger parent section by
isolating "does V7 `bio.c` even compile against our header
shims" from "does the bdevsw chain return the right bytes on
hardware."  If `dev/bio.c` needs trivial header touch-ups
(extern declarations, missing prototypes), those land here in
isolation rather than tangled with new driver code.  The
ratchet still shrinks because `dev/bio.c` enters the build in
its historic form.

Build:

```
make -C unix-v7-c99 ARCH=arm CONF=evb_arm
make -C stm32mp135_test_board/bootloader -j$(nproc)
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
mp135.evb:uart_expect sentinel="mem = " timeout_ms=60000
mp135.evb:uart_close
mark tag=v7_bio_link
```

Verify:

```
import subprocess

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream_text(extract_dir, 'mp135.uart')
    if 'panic' in uart.lower():
        return False
    if 'mem = ' not in uart:
        return False
    # Symbol must be defined in the linked kernel ELF.
    out = subprocess.run(
        ['arm-none-eabi-nm', 'unix-v7-c99/unix'],
        capture_output=True, text=True, check=False)
    if out.returncode != 0:
        return False
    for line in out.stdout.splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[1] == 'T' and parts[2] == 'bread':
            return True
    return False
```

### V7 bdevsw[0] wired to dev/mp135_blk.c::mp135_strategy (no caller yet)

Smallest forward increment toward the parent section: introduce a
real block-device strategy routine for the EVB and wire it into
`bdevsw[0]` so that the buffer-cache module linked in iter 1 has a
working back end *before* any kernel caller exercises it.

Add `dev/mp135_blk.c` (new) containing `mp135_strategy(struct buf *bp)`.
The body does exactly what `arch/armboot.c::bio()` does today on EVB:
inspect `bp->b_blkno`, `bp->b_bcount`, and `bp->b_flags & B_READ`, then
memcpy between the V7 buffer (`bp->b_un.b_addr`) and the DDR-staged
rootfs at `0xC4400000` plus `blkno * BSIZE`.  On completion, set
`B_DONE` in `bp->b_flags`, clear `B_BUSY`, and call `iodone(bp)`.
No interrupt handling is needed: the memcpy is synchronous.

Also add `dev/virtio_blk.c` (new) containing `virtio_strategy()` for
qemu, factored out of the virtio code currently inside
`arch/armboot.c`.  The qemu path is preserved for parity but is not
the focus of this section's bench verifier.

Replace the `{0,0,0,0}` placeholder for `bdevsw[0]` in
`arch/v7stubs.c` with `{nulldev, nulldev, mp135_strategy, &mp135_tab}`
(EVB build) or the virtio equivalent (qemu build), gated by
`CONF=evb_arm` vs `CONF=qemu_arm`.  `mp135_tab` is a zero-initialised
`struct buf` used as the per-device buffer-list head, matching the V7
`bdevsw` ABI.

No kernel-side caller of `bread()` is added in this sub-step.
`arch/armboot.c::bio()` remains the active block-I/O path on
hardware, byte-for-byte identical to today.  The only observable
change is that the `bdevsw[0].d_strategy` slot now points at a real
function symbol in the ELF, and a fresh cold boot must still reach
the `mem = ` banner with no panic.

This sub-step de-risks the parent section by isolating "does the
bdevsw wiring compile and not break boot" from "does `bread()`
actually pull the right bytes through the cache."  If header
plumbing for `struct buf`, `B_READ`, `iodone`, etc. needs
adjustment, it lands here in isolation rather than tangled with a
new kernel caller.  The ratchet still shrinks because the new
strategy routines are net additions in `dev/` (not V7 source) and
no V7 file regresses.

Build:

```
make -C unix-v7-c99 ARCH=arm CONF=evb_arm
make -C stm32mp135_test_board/bootloader -j$(nproc)
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
mp135.evb:uart_expect sentinel="mem = " timeout_ms=60000
mp135.evb:uart_close
mark tag=v7_bdevsw0_wired
```

Verify:

```
import subprocess

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream_text(extract_dir, 'mp135.uart')
    if 'panic' in uart.lower():
        return False
    if 'mem = ' not in uart:
        return False
    # Strategy routine must be defined in the linked kernel ELF.
    out = subprocess.run(
        ['arm-none-eabi-nm', 'unix-v7-c99/unix'],
        capture_output=True, text=True, check=False)
    if out.returncode != 0:
        return False
    for line in out.stdout.splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[1] == 'T' and parts[2] == 'mp135_strategy':
            return True
    return False
```

### V7 bread(rootdev, SUPERB) sentinel from startup()

Smallest forward increment toward the parent section: add the first
real V7-style caller of `bread()` so the linked buffer cache and the
`bdevsw[0].d_strategy` slot (already wired in the prior two
sub-steps) are exercised end-to-end on hardware -- without yet
retiring `arch/armboot.c::bio()` or any of the shim's `shim_bread`
call sites.

Add `int rootdev = 0;` (a fake `makedev(0,0)`) to `arch/v7stubs.c`
if not already present, so the new caller has a device number to
pass.  In `arch/machdep.c::startup()`, immediately after the
existing `printf("mem = ...")` line, call
`bp = bread((dev_t)rootdev, (daddr_t)SUPERB)`, then print
`v7: sb isize=%d fsize=%d\n` reading `((struct filsys *)bp->b_un.b_addr)->s_isize` and
`->s_fsize` from the returned buffer.  Call `brelse(bp)` afterwards.
This walks `bdevsw[0].d_strategy` (the EVB's `mp135_strategy` /
qemu's `virtio_strategy`) for LBA `SUPERB` (block 1 of the V7
filesystem), pulls it through `getblk`, and exercises the full
`bread -> getblk -> strategy -> iowait -> iodone` path that V7
expects.

`arch/armboot.c::bio()` and its `shim_bread`/`shim_bwrite` callers
are untouched.  The shim continues to satisfy every kernel block
read elsewhere; this new sentinel call is additive.  `arch/machdep.c`
lives outside the V7 ratchet's purview (it is `arch/`-prefixed),
so the modification is allowed without affecting the ratchet's
insert/delete bookkeeping against `v7/usr/...`.

The point of this sub-step is to prove on real hardware that the
chain we wired in iterations 1 and 2 actually returns the right
bytes: `s_isize` and `s_fsize` for a V7 filesystem are small,
non-zero, plausible integers (typically `s_isize` in the tens to
low thousands, `s_fsize` larger than `s_isize`).  Reading garbage,
zeros, or `0xdeadbeef`-style sentinels means the buffer cache,
the strategy routine, or the DDR-staged rootfs offset is wrong --
and we want to find that out *now*, before retiring the shim's
block-I/O path in the next iteration.

Build:

```
make -C unix-v7-c99 ARCH=arm CONF=evb_arm
make -C stm32mp135_test_board/bootloader -j$(nproc)
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
mp135.evb:uart_expect sentinel="mem = " timeout_ms=60000
mp135.evb:uart_expect sentinel="v7: sb isize=" timeout_ms=15000
mp135.evb:uart_close
mark tag=v7_bread_sentinel
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
    if 'mem = ' not in uart:
        return False
    m = re.search(r'v7: sb isize=(\d+) fsize=(\d+)', uart)
    if not m:
        return False
    isize = int(m.group(1))
    fsize = int(m.group(2))
    # Plausible V7 superblock: small non-zero isize, fsize > isize,
    # and neither value is an obvious garbage sentinel.
    if isize <= 0 or isize > 100000:
        return False
    if fsize <= isize or fsize > 10000000:
        return False
    return True
```

## WIP

### V7 sys/bio.c buffer cache linked, shim bio() retired

Pull `sys/bio.c` into the link.  `bdevsw` already lives in
`conf/c.c` and currently lists only `rkstrategy` (the PDP-11 RK
disk).  Register a placeholder `mp135_strategy()` in
`dev/mp135_blk.c` (new) that initially does exactly what the
shim's `bio()` does today on EVB: memcpy between the V7 buffer
and the DDR-staged rootfs at `0xC4400000`.  On qemu, register
`virtio_strategy()` in `dev/virtio_blk.c` (new) that re-uses the
virtio code currently inside `armboot.c`.  After this section,
`arch/armboot.c::bio()` is unreferenced and deletable.

Build:

```
make -C unix-v7-c99 ARCH=arm CONF=evb_arm
make -C stm32mp135_test_board/bootloader -j$(nproc)
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

Test (max 5 min): cold-boot EVB, drive `two` + `load_sd` + `jump`,
expect kernel banner.  Same preamble as the prior mission's banner
section.  After banner, drive a sentinel that proves the V7 buffer
cache went through `sys/bio.c` (e.g. an `evb: bio.c bread` printf
inside `sys/bio.c`'s `bread()` -- this is a debug print to be
removed in a later section).

Verify: `evb: bio.c bread` appears on UART after `mem = ` and
before any kernel panic.

### V7 sys/iget.c + nami.c linked, shim namei retired

Replace `arch/armboot.c::namei`, `loadino`, `parenti` with
`sys/nami.c::namei()` and `sys/iget.c::iget`/`iput`.  These already
walk `bdevsw` for block I/O; after the prior section's buffer-cache
work this just-works.  `arch/armboot.c`'s versions become
unreferenced and are deleted.

Build / Test / Verify: cold-boot to `login:` on EVB.  Sentinel:
`namei` panic-checked output of the inode for `/etc/init`
(printable from `sys/main.c`'s `iinit` flow).

### sys/main.c::main() takes over from armboot() shim

Re-enable the `#if 0`-wrapped body of `sys/main.c::main()`:
clkstart, cinit, binit, iinit, newproc, sched.  Stop falling
through to `arch/armboot.c::armboot()`.  Link in `sys/alloc.c`,
`sys/text.c`, `sys/clock.c`, and the rest of sys/'s init
prerequisites.  `armboot()` becomes unreachable.  Delete it.

Build / Test / Verify: cold-boot to `login:` on EVB, then drive
`root\r` and confirm `# ` prompt.  Sentinel: a new
`init: real V7 main` printf added to the top of the enabled
sys/main.c block (replacing the existing `init: multi-user`
banner -- not removing it, the V7 init still prints it after
forking).

### sys/trap.c + sys/sys[1-4].c syscall path replaces shim dispatcher

The shim's giant `else if(n == S_*)` chain in `arch/armboot.c::trap`
is replaced by `sys/trap.c::trap()` calling into `sys/sys1.c`
through `sys/sys4.c` per the V7 syscall vector table.  This is the
biggest single replacement and depends on having `proc[]` real
(see next section).  May be done in tandem.

Build / Test / Verify: every shim-section behaviour
(login, shell echo, sgtty, bg+kill, trap+self-signal) still
reaches its sentinel after this lands.  Sentinel
`evb: trap.c entered` printf added once on first syscall (then
removed in a later cleanup).

### Real proc[] + fork + wait + swtch

Link in `sys/fork.c`, `sys/exec1.c`, `sys/exec2.c`, `sys/slp.c`,
`sys/sig.c`.  Write `arch/swtch.s` (new): saves r0-r12, sp, lr,
cpsr to the outgoing proc's u-area, loads the incoming proc's.
~30 lines of assembly.  Delete `arch/armboot.c`'s NFORK=8
save/restore arrays (`fusave`, `ffsave`, `cfsave`, `kuidsave`,
`hsave`, `psave`, `cframe`).

Build / Test / Verify: a new section that forks two processes
that ping-pong via a pipe.  Bench drives them via shell:
`( echo A ) | ( cat )` over UART; verifier asserts the doubled
echo and second prompt.  Until this section, that pipe was a
shim simulation; here it must be a real fork + real wait.

### Real V7 line discipline (dev/tty.c linked into console)

Link `dev/tty.c` into the build.  `dev/stm32_usart.c` and
`dev/pl011.c` register an open/read/write/ioctl entry in
`cdevsw` (already declared in `conf/c.c`) and call
`ttyinput(c, &cons_tty)` per RX byte and `(*linesw[0].l_write)(...)`
per TX path.  The result: ^C raises SIGINT, ^D returns 0 from
`read(2)` at start-of-line, ^S/^Q flow-control, V7 `gtty`/`stty`
ioctls all work.

Build / Test / Verify: bench types `cat\r`, then sends a literal
`\x03` (^C), then expects `# ` prompt within 5s.  Until this
section that test was satisfied by the shim hack (which we
already reverted); here it is satisfied by V7's real
ttyinput->psignal->setrun path.

### Remaining V7 syscalls in sys/sys[1-4].c

After the trap.c switch, syscalls not yet covered (`setgid`,
`getpid`, `getppid`, `alarm`, `pause`, `nice`, `ioctl`, `times`,
`fcntl`, etc.) are pulled in unchanged from V7 source.  Each is
a one-line decrease in `arch/armboot.c`'s dispatcher (already
deleted by this point in the mission, but a few may have leaked
into late-iteration patches).

Build / Test / Verify: per-syscall, exactly the unix-v7-c99 qemu
section that already exercises it (e.g. `cmd/who` for getuid;
`cmd/time` for times; `cmd/stty` for ioctl).  Add an EVB
counterpart per syscall as it lands.

### Real V7 SD/eMMC block driver -- bootloader load_sd preamble drops

Replace `dev/mp135_blk.c`'s memcpy-from-DDR strategy with a real
STM32MP135 SDMMC1 driver: open queue, issue READ_SINGLE_BLOCK /
WRITE_SINGLE_BLOCK over CMD/DAT lines, handle interrupts.  About
~200-400 lines of `dev/sdmmc_mp135.c` (new).  After this lands,
the EVB test plans can drop the `load_sd 4096 382 0xC4400000`
preamble; the kernel mounts the rootfs from disk on demand.

Build / Test / Verify: cold-boot a `unix-sdcard.img` whose layout
has unix.bin at MBR partition 1 and rootfs at partition 2 (no
DDR pre-stage).  Bench drives `two` + `jump` (no `load_sd`).
Kernel reaches `login:`.

### Optional speedup: I-cache + cacheable kernel pages

Postponed from the unix-on-stm32mp135.md commit cycle: enable
SCTLR.I and mark kernel + USERPHYS sections cacheable.  Needs
careful Cortex-A7 / STM32MP135 cache-coherency handling around
exec()'s readi-then-jump-into-text (cleared in a prior attempt
that hit "cannot exec login" due to I/D coherency).  Right home
for this section is *after* `sys/bio.c` lands, because the V7
buffer cache plus an actual SD driver makes the load pattern
predictable.

Build / Test / Verify: `pwd` round-trip from EVB shell completes
in < 250 ms wall-clock (measured by bench between sending
`pwd\r` and observing the `# ` reprompt).  Today on the shim
without cache it is ~4 s; the threshold gates the speedup
without requiring an exact target.

### Persistent utmp/wtmp after real SD driver lands

V7 `/etc/utmp` and `/usr/adm/wtmp` accumulate login records.  In
the shim they were tmpfs-backed and volatile.  After real SD I/O,
point both at the mounted rootfs.

Build / Test / Verify: cold-boot, log in as root, log out, cold-
boot again, log in as dmr, run `last` -- two entries appear.

### Multi-tty getty (second tty on UART-something or USB-CDC)

V7 init reads `/etc/ttys` and spawns one getty per line.  Add a
second `ttys` entry, wire it to a second console device,
spawn a second getty, gate that both serve `login:`
concurrently.

### Final cleanup: arch/armboot.c is empty (or deleted)

By this section every function in `arch/armboot.c` has been
replaced by V7 source.  The file is deleted from the build
(removed from `sys/Makefile`'s OBJS) and from the repo.  Mission
accomplished.

Build / Test / Verify: `test ! -f unix-v7-c99/arch/armboot.c`
AND `wc -l unix-v7-c99/sys/main.c` shows the historic V7 init
body uncommented AND all prior sections still pass on a fresh
hardware run.
