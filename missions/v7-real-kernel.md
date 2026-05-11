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
