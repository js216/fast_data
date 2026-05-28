## WIP

# Unix v7 on STM32MP135 EVB

Sister mission to `unix-on-qemu.md`. Both port the Seventh Edition
Unix kernel and userland from PDP-11 K&R C to C99 on Armv7-A,
keeping `unix-v7-c99/tools/original-diffs.sh` as the discipline
ratchet: only function prototypes and type widenings should change
against the original `v7/usr/...` tree, with device drivers and
`arch/` machine-dependent code exempt. The two demonstrations share
the `unix` ELF and `root.img` artefacts; this file owns the
bench-side EVB sections, where the image is delivered through the
bench's DFU+UART path (see `missions/ssh.md`) and the console is
captured over UART4.

Every EVB section is self-contained: reset -> DFU-flash bootloader ->
hold at `> ` -> MSC-write a unix-flavoured SD image -> `two` ->
`jump` -> capture UART. Each section pays the full cold-boot cost,
which keeps the sections independently runnable and reproducible.

The EVB delivery path reuses the bootloader's existing `two` + `jump`
flow that `ssh.md` already drives for Linux: `two` copies kernel and
(optional) DTB from a known MBR offset into DDR, `jump` enters the
loaded image. No new bootloader command is needed. What is new is
on the v7 side, all under `dev/`:

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
scope is appropriate for the EVB work.

The mission has two phases. **Phase 1** ("V7 userspace reaches a
multi-user shell on the EVB", sections below up to and including
`### Full end-to-end on EVB: cold reset -> SD -> shell`) gates V7
cold-boot via a kernel-side shim in `arch/armboot.c` that
re-implements fork, exec, wait, namei, bread, signal delivery, and
the V7 syscall dispatcher in parallel with the real V7 source in
`sys/`. The shim let us ship a checkpoint; it is not the
destination. **Phase 2** ("Remove the kernel shim", sections from
`### V7 dev/bio.c compiles and links into kernel (no caller)`
onward) removes the shim: the kernel ends up running V7's own
`sys/main.c::main()`, V7's own `sys/trap.c::trap()` for syscalls,
V7's own `sys/bio.c` buffer cache, V7's own `sys/fork.c`+`sys/slp.c`
for processes and scheduling, V7's own `sys/sig.c` for signal
delivery, V7's own `dev/tty.c` for cooked-mode line discipline,
and `arch/armboot.c` shrinks to zero lines.

Two anchor invariants for every Phase 2 section:

  1. **No regression on hardware.**  After each section lands,
     a fresh cold boot on the EVB still reaches `login:` and accepts
     `root` and `dmr` logins.  The Phase 1 sections above do NOT
     need to keep passing once their behavior is satisfied by the
     real kernel -- their shim-specific test plans can be replaced,
     removed, or marked obsolete in Phase 2.

  2. **Shim shrinks monotonically.**  `wc -l arch/armboot.c` must
     decrease (or stay the same) at every commit.  The shim cannot
     grow during Phase 2.  Net code-of-interest moves from
     `arch/armboot.c` into `sys/*.c` and `dev/*.c`.

Section order matters: items earlier on the list unblock items
later on the list.  Tester runs all sections through the WIP marker;
the WIP marker moves forward only when each section's verify check
passes on bench.

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

### shim_bread/shim_bwrite delegate to real V7 bread/bwrite

Smallest forward increment toward the parent section: re-implement
the bodies of `arch/armboot.c::shim_bread(blkno, buf)` and
`shim_bwrite(blkno, buf)` to call the real V7 `bread(rootdev, blkno)`
/ `bwrite(bp)` chain (linked in iter 1, wired in iter 2a, proven on
hardware in iter 3 by the `v7: sb isize=16 fsize=4096` sentinel)
instead of the shim's `bio()` byte-pump.  After this sub-step:

  - `shim_bread(blkno, buf)` becomes:
    `bp = bread((dev_t)rootdev, (daddr_t)blkno);
     bcopy(bp->b_un.b_addr, buf, BSIZE);
     brelse(bp);`
  - `shim_bwrite(blkno, buf)` becomes:
    `bp = getblk((dev_t)rootdev, (daddr_t)blkno);
     bcopy(buf, bp->b_un.b_addr, BSIZE);
     bwrite(bp);`
  - `arch/armboot.c::bio()` is left in place but is now unreferenced
    (its sole callers were the two `shim_*` wrappers).  Removing the
    dead `bio()` function and the EVB DDR-staging memcpy / qemu virtio
    code inside it is the *next* sub-step's job, not this one.  Keeping
    `bio()` resident this iteration limits the blast radius if real
    `bread`/`bwrite` misbehaves on any of the ~13 call sites
    (`loadino`, `readi`, `writei`, `namei`, `iupdat`, etc.) -- a
    single-line revert of the two shim bodies brings the working
    iter-3 state back.

No call-site changes in `arch/armboot.c` are made in this sub-step:
all ~13 existing `shim_bread(...)`/`shim_bwrite(...)` invocations
(loadino, readi, writei, namei, iupdat, etc.) keep the same caller
ABI -- only the wrapper body changes.  This means *every* kernel
block read and write that armboot.c performs on hardware now flows
through the real V7 buffer-cache chain
(`bread` -> `getblk` -> `bdevsw[0].d_strategy` -> `iowait` ->
`iodone`), the same chain that iter 3 proved good on a single
superblock read.  Where iter 3 hit `bread` exactly once for
`SUPERB`, this iteration hits it dozens of times during root inode
walks, `/etc/init` load, exec(), and the multi-user-shell init
chain -- a much heavier exercise of the cache, of `getblk`'s LRU
list, and of `mp135_strategy`'s memcpy path under repeated calls.

The ratchet stays flat: only `arch/armboot.c` changes (outside the
V7-source purview), and `wc -l arch/armboot.c` decreases by a few
lines (the two shim bodies shrink; `bio()` is unchanged for now).

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
mark tag=v7_shim_bread_delegates
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
    # Iter-3 sentinel must still appear: the bread(rootdev, SUPERB)
    # call from startup() still hits the real V7 buffer cache and
    # pulls a plausible superblock through mp135_strategy.
    m = re.search(r'v7: sb isize=(\d+) fsize=(\d+)', uart)
    if not m:
        return False
    isize = int(m.group(1))
    fsize = int(m.group(2))
    if isize <= 0 or isize > 100000:
        return False
    if fsize <= isize or fsize > 10000000:
        return False
    # And the heavier exercise: cold boot reaches login:, root\r
    # yields a shell prompt, and a typed `echo SHELLOK` echoes
    # back through cooked-mode tty -- proving every shim_bread/
    # shim_bwrite call site (loadino, readi, writei, namei,
    # iupdat, etc.) still returns correct bytes when routed
    # through the real V7 buffer cache.
    try:
        i_login = uart.index('login:')
        i_shell = uart.index('# ', i_login)
        uart.index('SHELLOK', i_shell)
    except ValueError:
        return False
    return True
```

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
mark tag=v7_bio_retired
```

Verify:

```
import re
import subprocess

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
    if not (0 < isize < 100000 and isize < fsize):
        return False
    # The shim's bio() must be gone from the ELF -- proves the parent
    # section's intent (shim bio() retired).
    out = subprocess.run(
        ['arm-none-eabi-nm', 'unix-v7-c99/unix'],
        capture_output=True, text=True, check=False)
    if out.returncode != 0:
        return False
    for line in out.stdout.splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[2] == 'bio':
            return False
    return True
```

### V7 sys/nami.c + sys/iget.c compile and link (no caller)

Smallest forward increment toward the parent section: add
`iget.o` and `nami.o` to `unix-v7-c99/sys/Makefile`'s `OBJS` so
the V7 inode-lookup translation units (`namei`, `iget`, `iput`,
`iupdat`, `itrunc`, `maknode`, `wdir`, `schar`, `uchar`) compile
unmodified V7 source (with C99 prototype conversion and one
macro-correctness touch-up to use the `i_lastr` / `i_addr` macros
defined in `h/inode.h`) under our `arm-none-eabi-gcc -std=c99`
toolchain, and that the final `unix` ELF still links.

No caller is added in this sub-step.  `namei`, `iget`, `iput`
and friends become defined-but-unreferenced symbols in the
kernel ELF; `arch/armboot.c::namei`, `loadino`, `parenti`,
and the file-scope `iget` shim are unchanged and continue to
satisfy every existing kernel path-walk on hardware.  Behavior
on the EVB is byte-identical to the prior commit.

The linker cascade is contained by adding minimal stubs in
`arch/v7stubs.c` for the symbols `nami.c` / `iget.c` reference
but whose V7 source is not yet linked: `bcopy`, `free`,
`getfs`, `ialloc`, `ifree`, `prele`, `plock`, `access`, `bmap`,
`fubyte`, `writei`.  Storage for the in-core inode table
`inode[NINODE]` is added in `v7stubs.c` as well.  These stubs
do nothing -- they exist solely to make `iget.o` / `nami.o`
link.  When real callers wire up, they will be replaced by
their real V7 implementations in later iterations.

This sub-step de-risks the much larger parent section by
isolating "does V7 `nami.c` / `iget.c` compile against our
header shims" from "does the inode-lookup chain actually
return the right inodes on hardware."  If `nami.c` / `iget.c`
need trivial header touch-ups (extern declarations, missing
prototypes), those land here in isolation rather than tangled
with new caller wiring.  The ratchet still shrinks because
`sys/nami.c` and `sys/iget.c` enter the build in their
unmodified-or-only-C99-prototyped form.

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
mark tag=v7_nami_iget_link
```

Verify:

```
import re
import subprocess

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
    if not (0 < isize < 100000 and isize < fsize):
        return False
    # Both symbols must be defined in the linked kernel ELF.
    out = subprocess.run(
        ['arm-none-eabi-nm', 'unix-v7-c99/unix'],
        capture_output=True, text=True, check=False)
    if out.returncode != 0:
        return False
    have_namei = False
    have_iget = False
    for line in out.stdout.splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[1] == 'T':
            if parts[2] == 'namei':
                have_namei = True
            elif parts[2] == 'iget':
                have_iget = True
    return have_namei and have_iget
```

### shim_namei delegates to real V7 namei

Smallest forward increment toward the parent section: rename
`arch/armboot.c`'s file-local `static ino_t namei(char *path)` to
`shim_namei()` (mirroring iter 4's `shim_bread`/`shim_bwrite`
naming), rewrite its body to delegate to V7's
`sys/nami.c::namei(uchar, 0)`, and update every intra-shim call
site (`kchdir`, `kopen`, `kcreat`, `klink`, `kmknod`, `kchmod`,
`kstat`, `kexec`, the S_ACCESS/S_UTIME dispatch entries, and the
EVB `/etc/init` sentinel) to invoke `shim_namei` instead.  V7's
`namei` returns a locked `struct inode *`; the bridge sets
`u.u_dirp = path`, `u.u_segflg = 1` (system-space path), clears
`u.u_error`, calls `namei(uchar, 0)`, snapshots `ip->i_number`,
and `iput()`s the inode before returning the inum.

`loadino` and `parenti` remain in `arch/armboot.c` for now -- the
shim still owns the dinode-to-`struct file` translation and the
basename-to-parent-inum split.  Retiring those is the *next*
sub-step's job.  This iteration limits the blast radius of the
namei swap: if V7's path walker misbehaves on any of the ~13
existing call sites, only the namei half of the lookup chain
needs to be reverted.

Three supporting changes to `arch/v7stubs.c` make the bridge
viable on a freshly cold-booted system:

  - `prele(ip)` is upgraded from a no-op to actually clearing
    `ILOCK` (V7's `iget` leaves the inode locked on return; the
    no-op stub would have wedged the next `iget` on the same
    inode in our no-op `sleep`).  `plock(ip)` symmetrically
    sets the bit.
  - `getfs(dev)` returns a real zero-initialised `struct filsys`
    instead of `NULL`, so `iupdat`'s `getfs(ip->i_dev)->s_ronly`
    deref is safe even though we never reach that path for
    pure-lookup namei traffic.
  - `bmap(ip, bn, B_READ)` is given a real read-only
    implementation that walks the inode's direct + indirect
    block arrays.  The wrinkle: `sys/iget.c::iexpand()` is the
    historic PDP-11 byte-order packing that produces
    `i_addr[i] = byte0 | (byte1<<16) | (byte2<<24)` on ARM
    little-endian, not the natural `byte0 | (byte1<<8) |
    (byte2<<16)`.  `bmap`'s `unpack_iaddr` helper bridges
    this without touching `sys/iget.c`.

The ratchet stays flat: only `arch/armboot.c` and
`arch/v7stubs.c` change (outside the V7-source purview), and
`wc -l arch/armboot.c` decreases (the ~40-line shim namei body
collapses to a 5-line `v7_namei_inum` delegate).

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
mark tag=v7_shim_namei_delegates
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
    # Iter-3 sentinel must still appear: the bread(rootdev, SUPERB)
    # call from startup() still pulls a plausible V7 superblock
    # through mp135_strategy.
    m = re.search(r'v7: sb isize=(\d+) fsize=(\d+)', uart)
    if not m:
        return False
    isize = int(m.group(1))
    fsize = int(m.group(2))
    if isize <= 0 or isize > 100000:
        return False
    if fsize <= isize or fsize > 10000000:
        return False
    # And the heavier exercise: cold boot reaches login:, root\r
    # yields a shell prompt, and a typed `echo SHELLOK` echoes
    # back through cooked-mode tty -- proving every shim_namei
    # call site (kchdir, kopen, kcreat, kexec, S_ACCESS, etc.)
    # still resolves paths correctly when routed through V7's
    # real namei() with our bmap()/getfs()/prele() stubs.
    try:
        i_login = uart.index('login:')
        i_shell = uart.index('# ', i_login)
        uart.index('SHELLOK', i_shell)
    except ValueError:
        return False
    return True
```

### V7 sys/iget.c + nami.c linked, shim namei retired

Parent section: the shim's namei wrapper in `arch/armboot.c`
is *gone*.  Every former `shim_namei` call site now invokes
`v7_namei_inum` directly (the arch-resident bridge in
`arch/v7stubs.c` that drives V7's historic
`sys/nami.c::namei(uchar, 0)` and unboxes `struct inode *`
into the legacy `ino_t` shape).  The shim's `loadino` and
`parenti` continue to satisfy the few inode-table walks they
own; their retirement is a later sub-iteration.

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
mp135.evb:uart_close
mark tag=v7_shim_namei_gone
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
    if 'login:' not in uart or '# ' not in uart:
        return False
    # Only V7's real namei (from sys/nami.c) should remain.
    out = subprocess.run(
        ['arm-none-eabi-nm', 'unix-v7-c99/unix'],
        capture_output=True, text=True, check=False)
    if out.returncode != 0:
        return False
    n = sum(1 for line in out.stdout.splitlines()
            if len(line.split()) == 3
            and line.split()[2] == 'namei'
            and line.split()[1] in ('T', 't'))
    return n == 1
```

## WIP

### sys/main.c::main() takes over from armboot() shim

Parent task: re-enable the `#if 0`-wrapped body of
`sys/main.c::main()` (clkstart, cinit, binit, iinit, newproc,
sched), stop falling through to `arch/armboot.c::armboot()`,
link in `sys/alloc.c`, `sys/text.c`, `sys/clock.c`, and the
rest of sys/'s init prerequisites.  `armboot()` becomes
unreachable and is deleted.  This is decomposed into sub-steps;
each landing keeps sections 1-8 green and tightens the bind on
the real V7 sys/.

This iteration takes the first chunk: V7's real
`sys/main.c::binit()` (and its `buffers[NBUF][BSIZE+BSLOP]`
storage) come out of `#if 0` and `arch/v7stubs.c::binit_stub()`
is retired.  `iinit()` stays wrapped (the next sub-iteration).
`arch/machdep.c::startup()` now calls V7's real `binit()`
before the `bread(rootdev, SUPERB)` sentinel.

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
mp135.evb:uart_write data="echo SHELLOK\r"
mp135.evb:uart_expect sentinel="SHELLOK" timeout_ms=8000
mp135.evb:uart_close
mark tag=v7_real_binit_live
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
    if 'login:' not in uart or '# ' not in uart:
        return False
    if 'SHELLOK' not in uart:
        return False
    # V7's real binit() must be live, and the v7stubs binit_stub() gone.
    out = subprocess.run(
        ['arm-none-eabi-nm', 'unix-v7-c99/unix'],
        capture_output=True, text=True, check=False)
    if out.returncode != 0:
        return False
    nm = out.stdout
    has_binit = any(line.split()[-2:] == ['T', 'binit']
        for line in nm.splitlines() if len(line.split()) == 3)
    has_stub = any(line.split()[-1] == 'binit_stub'
        for line in nm.splitlines() if len(line.split()) == 3)
    return has_binit and not has_stub
```

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

The four sections below are stubs (not yet bench-tested sections).
They are topics from the original Phase 2 backlog that the formal
sections above don't cover: SIG_DFL wait-status fidelity after real
fork lands, `stty` mode renegotiation from `getty`, an EVB-side
regression gate for `ed`, and an optional re-baseline of the
original-diffs ratchet. Promote each to a full Build/Test/Verify
section when it becomes the next thing to land.

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
