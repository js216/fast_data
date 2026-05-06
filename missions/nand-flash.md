# NAND-flash boot for the STM32MP135 custom board

Drive the custom PCB through reset -> DFU bootloader -> write
`nand.img` to NAND -> boot Linux from NAND.

Bootloader is built with `-DNAND_FLASH` (swaps `two`/`load_sd` for
`fmc_*`; autoboot calls `fmc_bload`). Two DTS files differ only in
`chosen/bootargs`: `config/custom.dts` keeps `root=/dev/mmcblk0p3`,
`config/custom-nand.dts` carries `ubi.mtd=rootfs root=ubi0:rootfs
rootfstype=ubifs ...`. Provisioning: `nand.img` -> DDR via
`msc.custom:write` -> `fmc_flush` over UART -> NAND.

The 3 MB/s MSC floor is a hard boot/provisioning correctness
requirement. Do not lower any `min_rate_Bps=3000000` threshold to pass
the mission. A sub-3 MB/s MSC read or write means the NAND boot path is
broken and the code must be fixed.

## Tests

Provisioning & first boot:

- [Temporary: fix stale UBI rootfs tail panic](#temporary-fix-stale-ubi-rootfs-tail-panic)
- [NAND image round-trip: write -> fmc_flush -> poison -> fmc_load -> diff](#nand-image-round-trip-write---fmc_flush---poison---fmc_load---diff)
- [Full end-to-end: DFU -> NAND write+commit -> boot Linux console](#full-end-to-end-dfu---nand-writecommit---boot-linux-console)
- [NAND reboot persistence: Linux reboot -> bootloader reload -> second NAND boot](#nand-reboot-persistence-linux-reboot---bootloader-reload---second-nand-boot)

Smoke tests:

- [Inventory smoke](#inventory-smoke)
- [DFU bootloader artifact preflight](#dfu-bootloader-artifact-preflight)
- [DFU NAND bootloader flash smoke](#dfu-nand-bootloader-flash-smoke)
- [Bootloader hold via UART](#bootloader-hold-via-uart)
- [MSC + NAND probe smoke](#msc--nand-probe-smoke)
- [NAND health (bootloader-side)](#nand-health-bootloader-side)
- [NAND + UBI health (Linux-side via UART)](#nand--ubi-health-linux-side-via-uart)

Writable persistent state:

- [NAND writable persistent state: write marker -> reboot same image](#nand-writable-persistent-state-write-marker---reboot-same-image)
- [NAND writable persistent state: verify marker after same-image reboot](#nand-writable-persistent-state-verify-marker-after-same-image-reboot)
- [NAND writable rootfs: write marker on `/` -> reboot same image](#nand-writable-rootfs-write-marker-on----reboot-same-image)
- [NAND writable rootfs: verify marker after same-image reboot](#nand-writable-rootfs-verify-marker-after-same-image-reboot)
- [NAND writable rootfs: five 50MiB write and reboot cycles](#nand-writable-rootfs-five-50mib-write-and-reboot-cycles)

Production-hardening regressions (WIP):

- [Hardened ECC: refuse to jump on uncorrectable kernel page](#hardened-ecc-refuse-to-jump-on-uncorrectable-kernel-page)
- [Hardened P/E status: program-fail marks block bad at runtime](#hardened-pe-status-program-fail-marks-block-bad-at-runtime)
- [Hardened BBT: on-flash BBT survives `fmc_flush` tail-erase](#hardened-bbt-on-flash-bbt-survives-fmc_flush-tail-erase)
- [ECC fault-injection visible in dmesg: bit-flip is corrected](#ecc-fault-injection-visible-in-dmesg-bit-flip-is-corrected)
- [Hardened kernel image: bootloader refuses to jump on hash mismatch](#hardened-kernel-image-bootloader-refuses-to-jump-on-hash-mismatch)
- [Hardened PT/DTB: redundant copy boots when primary is corrupted](#hardened-ptdtb-redundant-copy-boots-when-primary-is-corrupted)
- [Crash recovery: power-cut mid-write leaves UBIFS mountable](#crash-recovery-power-cut-mid-write-leaves-ubifs-mountable)
- [Round-trip: full-image diff between MSC write and `fmc_load` readback](#round-trip-full-image-diff-between-msc-write-and-fmc_load-readback)
- [Wear-leveling stress: 100 cycles of full-volume churn, even erase counts](#wear-leveling-stress-100-cycles-of-full-volume-churn-even-erase-counts)

### Temporary: fix stale UBI rootfs tail panic

The current NAND boot reaches Linux but panics while mounting UBIFS
because UBI sees stale eraseblocks after the newly written image. The
observed signature was:

```
ubi0: attaching mtd4
ubi0 error: scan_peb.constprop.0: bad image sequence number 540517424 in PEB 46, expected 1951870196
ubi_attach_mtd_dev: failed to attach mtd4, error -22
VFS: Cannot open root device "ubi0:rootfs" or unknown-block(0,0): error -19
Kernel panic - not syncing: VFS: Unable to mount root fs on unknown-block(0,0)
```

At the time, `fmc_flush` reported `FMC flush: 114 blocks`; the rootfs
partition starts at block 68, so UBI PEB 46 maps to physical block 114,
the first block after the flushed image. The next fix should make NAND
provisioning erase or otherwise invalidate the rootfs tail after
`nand.img` while preserving the factory/runtime bad-block OOB markers.
Do not solve this by bulk-erasing bad-block metadata or lowering MSC
rate requirements.

Build:

```
make -C stm32mp135_test_board patch
make -C stm32mp135_test_board/bootloader -j$(nproc) CFLAGS_EXTRA=-DNAND_FLASH
make -C stm32mp135_test_board kernel
make -C stm32mp135_test_board DTS=custom-nand dtb
make -C stm32mp135_test_board br
make -C stm32mp135_test_board DTS=custom-nand nand
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/nand.img
```

Test (max 3 min):

```
lease:claim devices="mp135.custom" duration_s=3600 auto_release_on_session_end=true
bench_mcu:reset_dut2
delay ms=2000
dfu.custom:flash_layout layout=@flash.tsv no_reconnect=true
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
mp135.custom:uart_expect sentinel="> " timeout_ms=8000
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_close
delay ms=2000
inventory refresh=true verify=false
msc.custom:write data=@nand.img offset_lba=0 min_rate_Bps=3000000
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_write data="fmc_flush\r"
mp135.custom:uart_expect sentinel="FMC flush:" timeout_ms=3000
mp135.custom:uart_expect sentinel="tail-erased" timeout_ms=30000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_write data="fmc_bload\r"
mp135.custom:uart_expect sentinel="bload: done" timeout_ms=30000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_write data="jump"
delay ms=200
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="Linux version" timeout_ms=10000
mp135.custom:uart_expect sentinel="ubi0: attached mtd" timeout_ms=20000
mp135.custom:uart_expect sentinel="login:" timeout_ms=30000
mp135.custom:uart_close
lease:release
mark tag=stale_ubi_tail_panic_fixed
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    bad = ('bad image sequence number', 'cannot attach mtd4',
           'Unable to mount root fs', 'Kernel panic')
    return ('ubi0: attached mtd' in uart and 'login:' in uart
            and not any(s in uart for s in bad))
```

### Inventory smoke

Build: nothing required.

Test (max 30 s):

```
inventory refresh=true verify=true
mark tag=inventory_smoke
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    needed = {'mp135.custom', 'bench_mcu.0', 'lease._default'}
    devs = Verification.load_devices(extract_dir)
    return needed.issubset({d['id'] for d in devs})
```

### DFU bootloader artifact preflight

Build the NAND-flash bootloader and verify the DFU layout names the
expected bootloader image before touching hardware. This is a cheap
gate for the following DFU + UART hold step.

Build:

```
make -C stm32mp135_test_board/bootloader -j$(nproc) CFLAGS_EXTRA=-DNAND_FLASH
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(_extract_dir):
    tsv = Path('stm32mp135_test_board/bootloader/scripts/flash.tsv')
    image = Path('stm32mp135_test_board/bootloader/build/main.stm32')
    if not tsv.is_file() or not image.is_file() or image.stat().st_size == 0:
        return False
    text = tsv.read_text(encoding='utf-8', errors='replace')
    return 'main.stm32' in text and 'P' in text
```

### DFU NAND bootloader flash smoke

Reset (D12 via `reset_dut2`), DFU-load the NAND bootloader, and stop
autoboot before the bootloader can fall through to Linux. Keep the
lease alive for the UART hold step.

Build:

```
make -C stm32mp135_test_board/bootloader -j$(nproc) CFLAGS_EXTRA=-DNAND_FLASH
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
```

Test (max 30 s):

```
lease:claim devices="mp135.custom" duration_s=3600
bench_mcu:reset_dut2
delay ms=2000
dfu.custom:flash_layout layout=@flash.tsv no_reconnect=true
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
mp135.custom:uart_expect sentinel="> " timeout_ms=8000
mp135.custom:uart_close
mark tag=dfu_nand_flash
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    return (Verification.op_succeeded(ops, 'dfu.custom', 'flash_layout')
            and Verification.op_succeeded(ops, 'mp135.custom', 'uart_expect'))
```

### Bootloader hold via UART

Inherits the DFU-loaded NAND bootloader state and confirms it is still
parked at `> `.

Build: nothing required.

Test (max 15 s):

```
lease:resume token="{{LEASE_TOKEN}}"
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_close
mark tag=bootloader_hold
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    return Verification.op_succeeded(ops, 'mp135.custom', 'uart_expect')
```

### MSC + NAND probe smoke

Inherits the bootloader-at-`> ` state. Refresh inventory so
`msc.custom` shows up, read 1 MiB from the DDR window, and run
`fmc_test_boot` to confirm the FMC controller is initialised. The
3 MB/s MSC read floor is a hard requirement; failing it means the
bootloader path is broken, not that the test threshold should be
reduced.

Build: nothing required.

Test (max 30 s):

```
lease:resume token="{{LEASE_TOKEN}}"
inventory
msc.custom:read n=1048576 offset_lba=0 min_rate_Bps=3000000
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_write data="fmc_test_boot\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_close
mark tag=msc_nand_smoke
lease:release token="{{LEASE_TOKEN}}"
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    if len(Verification.load_stream(extract_dir, 'msc.read')) != 1048576:
        return False
    uart = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    return 'FDT magic' in uart or 'partition' in uart or 'FMC' in uart
```

### NAND image round-trip: write -> fmc_flush -> poison -> fmc_load -> diff

Write `nand.img` to DDR via MSC, `fmc_flush` to NAND, `fmc_load` back
into DDR, MSC-read and offline-diff the leading bytes. Before
`fmc_load`, overwrite the leading DDR staging window with deterministic
zeroes and verify the poison landed, so a no-op `fmc_load` cannot pass by
reading back the original MSC write. The image build can outlive an
in-memory bench lease if the poller restarts, so this step claims a
fresh lease after the build and re-enters the bootloader state it
needs. The 3 MB/s MSC write and read floors are hard requirements for
NAND provisioning; sub-3 MB/s results are code failures.

Build:

```
make -C stm32mp135_test_board patch
make -C stm32mp135_test_board/bootloader -j$(nproc) CFLAGS_EXTRA=-DNAND_FLASH
make -C stm32mp135_test_board kernel
make -C stm32mp135_test_board DTS=custom-nand dtb
make -C stm32mp135_test_board br
make -C stm32mp135_test_board DTS=custom-nand nand
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/nand.img
```

Test (max 2 min):

```
lease:claim devices="mp135.custom" duration_s=3600
bench_mcu:reset_dut2
delay ms=2000
dfu.custom:flash_layout layout=@flash.tsv no_reconnect=true
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
mp135.custom:uart_expect sentinel="> " timeout_ms=8000
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_close
inventory
msc.custom:write data=@nand.img offset_lba=0 min_rate_Bps=3000000
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_write data="fmc_flush\r"
mp135.custom:uart_expect sentinel="FMC flush:" timeout_ms=3000
mp135.custom:uart_expect sentinel="tail-erased" timeout_ms=30000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_close
msc.custom:write_zeroes n=4194304 offset_lba=0 min_rate_Bps=3000000
msc.custom:verify_zeroes n=4194304 offset_lba=0 min_rate_Bps=3000000
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_write data="fmc_load\r"
mp135.custom:uart_expect sentinel="FMC load:" timeout_ms=3000
mp135.custom:uart_expect sentinel="rd errs" timeout_ms=10000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_close
msc.custom:read n=4194304 offset_lba=0 min_rate_Bps=3000000
mark tag=nand_round_trip
```

Verify:

```
from pathlib import Path

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    img = Path(artifacts['nand.img']).read_bytes()
    got = Verification.load_stream(extract_dir, 'msc.read')
    n = min(len(img), len(got), 4194304)
    return got[:n] == img[:n]
```

### NAND health (bootloader-side)

Inherits the bootloader-at-`> ` state from the round-trip. Runs
`fmc_scan` (reads OOB on every block, prints `bad: blk N` per bad
block then `scan done: K bad / N total`) and `fmc_test_boot`
(validates magic+checksum of bootloader blocks, partition table, and
DTB header in NAND). No Linux. Cheap gate before `fmc_bload`.

Build: nothing required.

Test (max 2 min):

```
lease:resume token="{{LEASE_TOKEN}}"
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_write data="fmc_scan\r"
mp135.custom:uart_expect sentinel="scan done:" timeout_ms=60000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_write data="fmc_test_boot\r"
mp135.custom:uart_expect sentinel="FDT magic OK" timeout_ms=10000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_close
mark tag=nand_health
```

Verify:

```
import re

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    m = re.search(r'scan done:\s+(\d+)\s+bad\s+/\s+(\d+)\s+total', uart)
    if not m:
        return False
    bad, total = int(m.group(1)), int(m.group(2))
    if total == 0 or bad > total // 100:   # <=1% bad blocks
        return False
    if 'checksum MISMATCH' in uart or 'bad magic' in uart:
        return False
    if 'checksum OK' not in uart or 'FDT magic OK' not in uart:
        return False
    return True
```

### NAND + UBI health (Linux-side via UART)

Inherits the bootloader-at-`> ` state from the previous test, boots
Linux from NAND with `fmc_bload` + `jump`, then talks to Linux over the
serial console. Logs in as `root`/`root`, prints
`/proc/mtd`, `ubinfo -a`, `mtdinfo -a`, and a filtered `dmesg`.
Asserts the expected partitions are present, UBI reports zero corrupted
PEBs, factory bad PEBs stay within a board-realistic bound, and `dmesg`
is clear of UBI/UBIFS/ECC errors.
Requires `BR2_PACKAGE_MTD=y` in `config/buildroot.conf` for the
mtd-utils binaries.

Build: nothing required.

Test (max 1 min):

```
lease:resume token="{{LEASE_TOKEN}}"
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_write data="fmc_bload\r"
mp135.custom:uart_expect sentinel="bload: done" timeout_ms=30000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_write data="jump"
delay ms=200
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="Jumping to address" timeout_ms=5000
mp135.custom:uart_expect sentinel="Linux version" timeout_ms=10000
mp135.custom:uart_expect sentinel="ubi0: attached mtd" timeout_ms=20000
mp135.custom:uart_expect sentinel="login:" timeout_ms=30000
mp135.custom:uart_write data="root\r"
mp135.custom:uart_expect sentinel="Password:" timeout_ms=3000
mp135.custom:uart_write data="root\r"
mp135.custom:uart_expect sentinel="# " timeout_ms=5000
mp135.custom:uart_write data="echo ___MTD___; cat /proc/mtd; echo ___UBI___; ubinfo -a; echo ___MTDI___; mtdinfo -a; echo ___DMESG___; dmesg | grep -iE 'ubi|ubifs|nand|fmc|bch|ecc' | tail -50; echo ___END___\r"
mp135.custom:uart_expect sentinel="___END___" timeout_ms=15000
mp135.custom:uart_expect sentinel="# " timeout_ms=3000
mp135.custom:uart_close
lease:release token="{{LEASE_TOKEN}}"
mark tag=nand_health_linux
```

Verify:

```
import re

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    body = uart.split('___END___')[0]
    for label in ('bootloader', 'ptable', 'dtb', 'kernel', 'rootfs'):
        if label not in body:
            return False
    corr = re.search(r'corrupted PEBs:\s+(\d+)', body, re.I)
    if not corr or int(corr.group(1)) != 0:
        return False
    bad = re.search(r'(?:Count of bad physical eraseblocks|bad PEBs):\s+(\d+)',
                    body, re.I)
    if not bad or int(bad.group(1)) > 32:
        return False
    if re.search(r'UBIFS error|UBI error|ECC unrecoverable|uncorrectable',
                 body, re.I):
        return False
    return True
```

### Full end-to-end: DFU -> NAND write+commit -> boot Linux console

Cold path. Reset, DFU NAND bootloader, stop autoload, write+commit
`nand.img`, `fmc_bload` + `jump`, and reach the Linux login prompt on
the serial console. The 3 MB/s MSC write floor is a hard requirement;
lowering it hides a broken NAND boot path.

Build:

```
make -C stm32mp135_test_board/bootloader -j$(nproc) CFLAGS_EXTRA=-DNAND_FLASH
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/nand.img
```

Test (max 2 min):

```
bench_mcu:reset_dut2
delay ms=2000
dfu.custom:flash_layout layout=@flash.tsv no_reconnect=true
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
mp135.custom:uart_expect sentinel="> " timeout_ms=8000
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_close
delay ms=5000
inventory refresh=true verify=false
msc.custom:write data=@nand.img offset_lba=0 min_rate_Bps=3000000
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_write data="fmc_flush\r"
mp135.custom:uart_expect sentinel="FMC flush:" timeout_ms=3000
mp135.custom:uart_expect sentinel="tail-erased" timeout_ms=30000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_write data="fmc_bload\r"
mp135.custom:uart_expect sentinel="bload: done" timeout_ms=30000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_write data="jump"
delay ms=200
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="Jumping to address" timeout_ms=5000
mp135.custom:uart_expect sentinel="Linux version" timeout_ms=10000
mp135.custom:uart_expect sentinel="ubi0: attached mtd" timeout_ms=20000
mp135.custom:uart_expect sentinel="login:" timeout_ms=30000
mp135.custom:uart_close
mark tag=full_end_to_end_nand
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    bad = ('Kernel panic', 'Unable to mount root fs', 'UBIFS error',
           'UBI error', 'ECC error', 'uncorrectable', 'unrecoverable')
    return ('Linux version' in uart and 'ubi0: attached mtd' in uart
            and 'login:' in uart and not any(s in uart for s in bad))
```

### NAND reboot persistence: Linux reboot -> bootloader reload -> second NAND boot

After a successful Linux boot from NAND, ask Linux to reboot. The board
returns to DFU, so reload only the bootloader and do not rewrite or
flush `nand.img`. The same NAND image may be modified by Linux during
normal operation, but it must remain bootable across repeated reboot
cycles.

Build: nothing required.

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
```

Test (max 2 min):

```
lease:claim devices="mp135.custom" duration_s=3600 auto_release_on_session_end=true
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="login:" timeout_ms=5000
mp135.custom:uart_write data="root\r"
mp135.custom:uart_expect sentinel="Password:" timeout_ms=3000
mp135.custom:uart_write data="root\r"
mp135.custom:uart_expect sentinel="# " timeout_ms=5000
mp135.custom:uart_write data="mount | grep ' / '; sync; reboot\r"
mp135.custom:uart_expect sentinel="Restarting system" timeout_ms=15000
mp135.custom:uart_close
delay ms=12000
dfu.custom:flash_layout layout=@flash.tsv no_reconnect=true
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
mp135.custom:uart_expect sentinel="> " timeout_ms=8000
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_write data="fmc_bload\r"
mp135.custom:uart_expect sentinel="bload: done" timeout_ms=30000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_write data="jump"
delay ms=200
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="Linux version" timeout_ms=10000
mp135.custom:uart_expect sentinel="ubi0: attached mtd" timeout_ms=20000
mp135.custom:uart_expect sentinel="login:" timeout_ms=30000
mp135.custom:uart_close
lease:release
mark tag=nand_reboot_persistence
```

Verify:

```
import re

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    bad = (r'Kernel panic', r'Unable to mount root fs', r'UBIFS error',
           r'UBI error', r'ECC error', r'uncorrectable', r'unrecoverable')
    return ('Linux version' in uart and 'ubi0: attached mtd' in uart
            and 'login:' in uart and not any(re.search(p, uart, re.I)
                                             for p in bad))
```

### NAND writable persistent state: write marker -> reboot same image

NAND must provide usable persistent state, not only a read-only boot
medium. After Linux boots from NAND, create or reuse a writable UBI
volume named `state`, mount it as UBIFS, write a marker with a unique
payload, sync and unmount it, then reboot Linux. The board returns to
DFU, so reload only the bootloader and do not rewrite or flush
`nand.img`. Boot Linux from the same NAND contents and reject
UBI/UBIFS/ECC/rootfs panic signatures.

Build: nothing required.

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
```

Test (max 3 min):

```
lease:claim devices="mp135.custom" duration_s=3600 auto_release_on_session_end=true
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="login:" timeout_ms=5000
mp135.custom:uart_write data="root\r"
mp135.custom:uart_expect sentinel="Password:" timeout_ms=3000
mp135.custom:uart_write data="root\r"
mp135.custom:uart_expect sentinel="# " timeout_ms=5000
mp135.custom:uart_write data="echo ___STATE_WRITE___; ubinfo -a; ubimkvol /dev/ubi0 -N state -s 8MiB || true; mkdir -p /run/state; mount -t ubifs ubi0:state /run/state; echo nand-state-v1 >/run/state/marker.txt; sync; cat /run/state/marker.txt; umount /run/state; echo ___STATE_REBOOT___; sync; reboot\r"
mp135.custom:uart_expect sentinel="___STATE_WRITE___" timeout_ms=5000
mp135.custom:uart_expect sentinel="nand-state-v1" timeout_ms=20000
mp135.custom:uart_expect sentinel="___STATE_REBOOT___" timeout_ms=5000
mp135.custom:uart_expect sentinel="Restarting system" timeout_ms=15000
mp135.custom:uart_close
delay ms=12000
dfu.custom:flash_layout layout=@flash.tsv no_reconnect=true
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
mp135.custom:uart_expect sentinel="> " timeout_ms=8000
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_write data="fmc_bload\r"
mp135.custom:uart_expect sentinel="bload: done" timeout_ms=30000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_write data="jump"
delay ms=200
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="Linux version" timeout_ms=10000
mp135.custom:uart_expect sentinel="ubi0: attached mtd" timeout_ms=20000
mp135.custom:uart_expect sentinel="login:" timeout_ms=30000
mp135.custom:uart_close
lease:release
mark tag=nand_writable_persistent_state_reboot
```

Verify:

```
import re

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    bad = (r'Kernel panic', r'Unable to mount root fs', r'UBIFS error',
           r'UBI error', r'ECC error', r'uncorrectable', r'unrecoverable')
    return ('___STATE_WRITE___' in uart
            and 'nand-state-v1' in uart
            and '___STATE_REBOOT___' in uart
            and 'ubi0: attached mtd' in uart
            and 'login:' in uart
            and not any(re.search(p, uart, re.I) for p in bad))
```

### NAND writable persistent state: verify marker after same-image reboot

After the previous step has rebooted Linux from the same NAND image,
start a fresh UART session at the login prompt. Log in locally, mount
the `state` UBIFS volume, read the marker, and check dmesg for
UBI/UBIFS, ECC, or panic failures. This is split from the write/reboot
step so repeated UART sentinels cannot be satisfied by bytes captured
before the reboot.

Build: nothing required.

Artifacts: none.

Test (max 1 min):

```
lease:claim devices="mp135.custom" duration_s=3600 auto_release_on_session_end=true
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="login:" timeout_ms=5000
mp135.custom:uart_write data="root\r"
mp135.custom:uart_expect sentinel="Password:" timeout_ms=3000
mp135.custom:uart_write data="root\r"
mp135.custom:uart_expect sentinel="# " timeout_ms=5000
mp135.custom:uart_write data="echo ___STATE_READ___; mkdir -p /run/state; mount -t ubifs ubi0:state /run/state; cat /run/state/marker.txt; umount /run/state; dmesg | grep -iE 'UBI|UBIFS|ECC|uncorrect|panic' || true; echo ___STATE_END___\r"
mp135.custom:uart_expect sentinel="___STATE_READ___" timeout_ms=5000
mp135.custom:uart_expect sentinel="nand-state-v1" timeout_ms=20000
mp135.custom:uart_expect sentinel="___STATE_END___" timeout_ms=15000
mp135.custom:uart_close
lease:release
mark tag=nand_writable_persistent_state_verify
```

Verify:

```
import re

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    bad = (r'Kernel panic', r'Unable to mount root fs', r'UBIFS error',
           r'UBI error', r'ECC error', r'uncorrectable', r'unrecoverable')
    return ('___STATE_READ___' in uart
            and 'nand-state-v1' in uart
            and '___STATE_END___' in uart
            and not any(re.search(p, uart, re.I) for p in bad))
```

### NAND writable rootfs: write marker on `/` -> reboot same image

The root UBIFS volume itself must tolerate ordinary persistent writes.
Starting from the authenticated UART shell left by the previous
same-image marker check, remount `/` read-write, write a marker directly
into the root filesystem, sync it, remount `/` read-only, and reboot.
The board returns to DFU, so reload only the bootloader and do not
rewrite or flush `nand.img`. Boot Linux from the same NAND contents and
reject UBI/UBIFS/ECC or rootfs-mount failures. This test intentionally
does not use the separate `state` volume.

Using a combined writable rootfs volume is the rigorous UBIFS test here:
Linux has to mount, update, sync, unmount, and boot again from the same
UBIFS volume that contains the operating system, not just append one
tiny file to a separate scratch volume. Future fixes must keep this
combined-root test instead of working around it by moving all writes to
another volume.

The root UBIFS image must be built with `mkfs.ubifs -F` so Linux fixes
free space before first use. The bootloader flasher writes the UBI image
as raw NAND pages, so UBIFS free pages in the image cannot be treated as
unprogrammed erase state until Linux has performed the free-space fixup.

Build: nothing required.

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
```

Test (max 3 min):

```
lease:claim devices="mp135.custom" duration_s=3600 auto_release_on_session_end=true
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="# " timeout_ms=5000
mp135.custom:uart_write data="echo ___ROOT_WRITE___; mount -o remount,rw /; echo nand-root-v1 >/root/root-marker.txt; sync; cat /root/root-marker.txt; mount -o remount,ro /; echo ___ROOT_REBOOT___; sync; reboot\r"
mp135.custom:uart_expect sentinel="___ROOT_WRITE___" timeout_ms=5000
mp135.custom:uart_expect sentinel="nand-root-v1" timeout_ms=20000
mp135.custom:uart_expect sentinel="___ROOT_REBOOT___" timeout_ms=5000
mp135.custom:uart_expect sentinel="Restarting system" timeout_ms=15000
mp135.custom:uart_close
delay ms=12000
dfu.custom:flash_layout layout=@flash.tsv no_reconnect=true
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
mp135.custom:uart_expect sentinel="> " timeout_ms=8000
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_write data="fmc_bload\r"
mp135.custom:uart_expect sentinel="bload: done" timeout_ms=30000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_write data="jump"
delay ms=200
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="Linux version" timeout_ms=10000
mp135.custom:uart_expect sentinel="ubi0: attached mtd" timeout_ms=20000
mp135.custom:uart_expect sentinel="login:" timeout_ms=30000
mp135.custom:uart_close
lease:release
mark tag=nand_writable_rootfs_reboot
```

Verify:

```
import re

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    bad = (r'Kernel panic', r'Unable to mount root fs', r'UBIFS error',
           r'UBI error', r'ECC error', r'uncorrectable', r'unrecoverable')
    return ('___ROOT_WRITE___' in uart
            and 'free space fixup complete' in uart
            and '___ROOT_REBOOT___' in uart
            and 'ubi0: attached mtd' in uart
            and 'login:' in uart
            and not any(re.search(p, uart, re.I) for p in bad))
```

### NAND writable rootfs: verify marker after same-image reboot

After the previous step has rebooted Linux from the same NAND image,
start a fresh UART session at the login prompt. Log in locally, read
the marker from `/root/root-marker.txt`, and check dmesg for UBI/UBIFS,
ECC, or panic failures. This is split from the write/reboot step so the
UART expect stream cannot satisfy `login:`, `Password:`, `# `, or marker
matches from bytes captured before the reboot.

Build: nothing required.

Artifacts: none.

Test (max 1 min):

```
lease:claim devices="mp135.custom" duration_s=3600 auto_release_on_session_end=true
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="login:" timeout_ms=5000
mp135.custom:uart_write data="root\r"
mp135.custom:uart_expect sentinel="Password:" timeout_ms=3000
mp135.custom:uart_write data="root\r"
mp135.custom:uart_expect sentinel="# " timeout_ms=5000
mp135.custom:uart_write data="echo ___ROOT_READ___; cat /root/root-marker.txt; dmesg | grep -iE 'UBI|UBIFS|ECC|uncorrect|panic' || true; echo ___ROOT_END___\r"
mp135.custom:uart_expect sentinel="___ROOT_READ___" timeout_ms=5000
mp135.custom:uart_expect sentinel="nand-root-v1" timeout_ms=20000
mp135.custom:uart_expect sentinel="___ROOT_END___" timeout_ms=15000
mp135.custom:uart_close
lease:release
mark tag=nand_writable_rootfs_verify
```

Verify:

```
import re

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    bad = (r'Kernel panic', r'Unable to mount root fs', r'UBIFS error',
           r'UBI error', r'ECC error', r'uncorrectable', r'unrecoverable')
    return ('___ROOT_READ___' in uart
            and 'nand-root-v1' in uart
            and '___ROOT_END___' in uart
            and not any(re.search(p, uart, re.I) for p in bad))
```

### NAND writable rootfs: five 50MiB write and reboot cycles

The combined writable rootfs must survive repeated large writes and
same-image reboots, not just a tiny marker file. This stress test loops
five times with `Foreach`. Each iteration starts from the authenticated
UART shell left by the previous section or previous loop iteration,
checks an existing `/root/bigfile` against `/root/bigfile.sha256` when
present, writes a fresh 50 MiB random file on `/`, stores its checksum
beside it, reboots Linux, reloads only the bootloader through DFU, boots
from the same NAND contents, logs in, and verifies the checksum again.
The rootfs UBI volume is intentionally the operating-system volume; do
not replace this with a separate scratch volume.

Build: nothing required.

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
```

Foreach:

```
loop in count(5)
```

Test (max 8 min):

```
lease:claim devices="mp135.custom" duration_s=3600 auto_release_on_session_end=true
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="# " timeout_ms=5000
mp135.custom:uart_write data="echo ___ROOT_LOOP_START___; mount -o remount,rw /; if [ -f /root/bigfile ] && [ -f /root/bigfile.sha256 ]; then sha256sum -c /root/bigfile.sha256 || echo ___ROOT_LOOP_PRECHECK_FAIL___; else echo ___ROOT_LOOP_NO_PRECHECK___; fi; echo ___ROOT_LOOP_DD_BEGIN___; rm -f /root/bigfile /root/bigfile.sha256; dd if=/dev/urandom of=/root/bigfile bs=1M count=50; rc=$?; echo ___ROOT_LOOP_DD_RC_${rc}___; sha256sum /root/bigfile >/root/bigfile.sha256; cat /root/bigfile.sha256; sync; mount -o remount,ro /; echo ___ROOT_LOOP_REBOOT___; sync; reboot\r"
mp135.custom:uart_expect sentinel="___ROOT_LOOP_START___" timeout_ms=5000
mp135.custom:uart_expect sentinel="___ROOT_LOOP_DD_BEGIN___" timeout_ms=30000
mp135.custom:uart_expect sentinel="___ROOT_LOOP_DD_RC_0___" timeout_ms=240000
mp135.custom:uart_expect sentinel="/root/bigfile" timeout_ms=120000
mp135.custom:uart_expect sentinel="___ROOT_LOOP_REBOOT___" timeout_ms=10000
mp135.custom:uart_expect sentinel="Restarting system" timeout_ms=30000
mp135.custom:uart_close
delay ms=12000
dfu.custom:flash_layout layout=@flash.tsv no_reconnect=true
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
mp135.custom:uart_expect sentinel="> " timeout_ms=8000
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_write data="fmc_bload\r"
mp135.custom:uart_expect sentinel="bload: done" timeout_ms=30000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_write data="jump"
delay ms=200
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="Linux version" timeout_ms=10000
mp135.custom:uart_expect sentinel="ubi0: attached mtd" timeout_ms=20000
mp135.custom:uart_expect sentinel="login:" timeout_ms=30000
mp135.custom:uart_write data="root\r"
mp135.custom:uart_expect sentinel="Password:" timeout_ms=3000
mp135.custom:uart_write data="root\r"
mp135.custom:uart_expect sentinel="# " timeout_ms=5000
mp135.custom:uart_write data="echo ___ROOT_LOOP_VERIFY___; sha256sum -c /root/bigfile.sha256; dmesg | grep -iE 'UBI|UBIFS|ECC|uncorrect|panic' || true; echo ___ROOT_LOOP_END___\r"
mp135.custom:uart_expect sentinel="___ROOT_LOOP_VERIFY___" timeout_ms=5000
mp135.custom:uart_expect sentinel="/root/bigfile: OK" timeout_ms=120000
mp135.custom:uart_expect sentinel="___ROOT_LOOP_END___" timeout_ms=15000
mp135.custom:uart_close
lease:release
mark tag=nand_writable_rootfs_50m_reboot_loop
```

Verify:

```
import re

def check(extract_dir, loop):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    bad = (r'Kernel panic', r'Unable to mount root fs', r'UBIFS error',
           r'UBI error', r'ECC error', r'uncorrectable', r'unrecoverable',
           r'___ROOT_LOOP_PRECHECK_FAIL___',
           r'/root/bigfile: FAILED',
           r'No space left on device')
    return ('___ROOT_LOOP_DD_RC_0___' in uart
            and '/root/bigfile: OK' in uart
            and '___ROOT_LOOP_END___' in uart
            and not any(re.search(p, uart, re.I) for p in bad))
```

## WIP

The sections below are production-hardening regression tests requested
by an adversarial audit. Each section names a concrete data-loss path
and proves end-to-end that the system either (a) detects and refuses
to act on corrupted state or (b) survives the failure with no silent
corruption. Every test must FAIL on the current bootloader code and
PASS only after the corresponding fix lands; a test that passes today
on the unfixed code is, by construction, not exercising the fix.

Tests below assume the prior 16 sections have left a freshly
provisioned NAND. Each new section re-flashes `nand.img` at its start
so a deliberately-corrupted run cannot leak into the next section.
They also tolerate a degraded final state by re-flashing on Verify if
needed (covered in each section's plan).

### Hardened ECC: refuse to jump on uncorrectable kernel page

After a clean boot from NAND, write one kernel-region NAND page raw
with bad ECC bytes so BCH cannot correct it. Reload the bootloader
via DFU and run `fmc_bload` followed by `jump`. The bootloader must
detect uncorrectable ECC during the kernel read, print
`fmc: ECC unrecoverable` (a sentinel that the verify keys on), refuse
to load the kernel, and stay at `> ` instead of jumping to garbage.

Today's bootloader (`bootloader/src/fmc.c:read_page`) discards
`HAL_NAND_GetEccState()` / `EccStatistics.BadSectorCount` and reports
`HAL_OK` even on DUE; this test only passes after `read_page`
propagates uncorrectable-ECC up through `read_block` and `fmc_bload`,
and `fmc_bload` aborts on first uncorrectable kernel page.

The corruption uses `mtd_debug write` (or `nandwrite --raw --noecc`)
on the kernel mtd partition. Linux must keep `mtdX` for the kernel
slot (currently kernel is at NAND blocks 4..67 per `nand_pt.h`); if
the kernel partition is not exposed as an mtd device, the bootloader
must add a debug command (`fmc_corrupt_ecc blk=N`) to do the
corruption from `> ` instead — the test plan should accommodate
either path.

After the verify, re-flash `nand.img` so subsequent sections start
clean.

Build:

```
make -C stm32mp135_test_board patch
make -C stm32mp135_test_board/bootloader -j$(nproc) CFLAGS_EXTRA=-DNAND_FLASH
make -C stm32mp135_test_board kernel
make -C stm32mp135_test_board DTS=custom-nand dtb
make -C stm32mp135_test_board br
make -C stm32mp135_test_board DTS=custom-nand nand
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/nand.img
```

Test (max 4 min):

```
lease:claim devices="mp135.custom" duration_s=3600 auto_release_on_session_end=true
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="# " timeout_ms=5000
mp135.custom:uart_write data="echo ___ECC_INJECT___; mtd=$(grep -E '\"kernel\"' /proc/mtd | cut -d: -f1); echo MTD=$mtd; dd if=/dev/urandom of=/tmp/page.bin bs=2048 count=1; mtd_debug write /dev/$mtd 0 2048 /tmp/page.bin; sync; echo ___ECC_REBOOT___; sync; reboot\r"
mp135.custom:uart_expect sentinel="___ECC_INJECT___" timeout_ms=5000
mp135.custom:uart_expect sentinel="___ECC_REBOOT___" timeout_ms=15000
mp135.custom:uart_expect sentinel="Restarting system" timeout_ms=30000
mp135.custom:uart_close
delay ms=12000
dfu.custom:flash_layout layout=@flash.tsv no_reconnect=true
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
mp135.custom:uart_expect sentinel="> " timeout_ms=8000
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_write data="fmc_bload\r"
mp135.custom:uart_expect sentinel="fmc: ECC unrecoverable" timeout_ms=30000
mp135.custom:uart_expect sentinel="bload: refused" timeout_ms=5000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_write data="jump\r"
mp135.custom:uart_expect sentinel="jump: no kernel loaded" timeout_ms=3000
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_close
inventory refresh=true verify=false
msc.custom:write data=@nand.img offset_lba=0 min_rate_Bps=3000000
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_write data="fmc_flush\r"
mp135.custom:uart_expect sentinel="tail-erased" timeout_ms=30000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_close
lease:release
mark tag=ecc_unrecoverable_refuses_jump
```

Verify:

```
import re

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    must = ('___ECC_INJECT___', 'fmc: ECC unrecoverable',
            'bload: refused', 'jump: no kernel loaded',
            'tail-erased')
    if not all(s in uart for s in must):
        return False
    # The corrupted boot must NOT have actually jumped.
    if 'Linux version' in uart.split('fmc: ECC unrecoverable')[1]:
        return False
    # And the post-test reflash must succeed.
    if 'FMC flush:' not in uart:
        return False
    return True
```

### Hardened P/E status: program-fail marks block bad at runtime

After a clean boot to bootloader, exercise a debug command
`fmc_inject_pgm_fail blk=N` (added by the fix) that makes the next
program of block N return a status FAIL. The bootloader must then
attempt a program of that block (e.g. via `fmc_test_write blk=N`),
issue `NAND_CMD_STATUS` (0x70), see the FAIL bit, mark the block bad
in its in-memory bad list, write a runtime bad marker to OOB on that
block, and surface the failure on UART. A subsequent `fmc_scan` must
include the block in its bad list.

Today's bootloader skips the status read entirely
(`HAL_NAND_WriteEnd` does only WaitReady) so the unfixed code returns
HAL_OK on every program-fail. The test passes only after every
program/erase op reads the NAND status register and runtime-marks
bad on FAIL.

Build, Artifacts: same as the prior section.

Test (max 3 min):

```
lease:claim devices="mp135.custom" duration_s=3600 auto_release_on_session_end=true
bench_mcu:reset_dut2
delay ms=2000
dfu.custom:flash_layout layout=@flash.tsv no_reconnect=true
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
mp135.custom:uart_expect sentinel="> " timeout_ms=8000
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_write data="fmc_scan\r"
mp135.custom:uart_expect sentinel="scan done:" timeout_ms=60000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_write data="fmc_inject_pgm_fail blk=1500\r"
mp135.custom:uart_expect sentinel="inject: blk 1500 next-pgm FAIL" timeout_ms=3000
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_write data="fmc_test_write blk=1500\r"
mp135.custom:uart_expect sentinel="pgm: blk 1500 status FAIL" timeout_ms=10000
mp135.custom:uart_expect sentinel="bad: blk 1500 runtime-marked" timeout_ms=3000
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_write data="fmc_scan\r"
mp135.custom:uart_expect sentinel="bad: blk 1500" timeout_ms=60000
mp135.custom:uart_expect sentinel="scan done:" timeout_ms=5000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
inventory refresh=true verify=false
msc.custom:write data=@nand.img offset_lba=0 min_rate_Bps=3000000
mp135.custom:uart_write data="fmc_flush\r"
mp135.custom:uart_expect sentinel="tail-erased" timeout_ms=30000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_close
lease:release
mark tag=program_fail_marks_bad
```

Verify:

```
import re

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    must = ('inject: blk 1500 next-pgm FAIL',
            'pgm: blk 1500 status FAIL',
            'bad: blk 1500 runtime-marked',
            'tail-erased')
    if not all(s in uart for s in must):
        return False
    # The post-inject scan must show 1500 as bad.
    post = uart.split('bad: blk 1500 runtime-marked')[1]
    return 'bad: blk 1500' in post and 'scan done:' in post
```

### Hardened BBT: on-flash BBT survives `fmc_flush` tail-erase

After a clean boot, Linux writes a synthetic on-flash BBT pattern
into the last four blocks of the NAND (blocks N-4..N-1 — the area
Linux's `NAND_BBT_SCAN_MAXBLOCKS = 4` covers). Capture the sha256 of
those four blocks. Reboot to the bootloader and run `fmc_flush`,
which today erases blocks N-2..N-1 (`FMC_BBT_RESERVED_BLOCKS = 2`).
Reboot to Linux and re-read the same four blocks. The hash must
match.

Today's bootloader (`fmc.c:39`) reserves only 2 blocks while Linux
covers 4, so the test fails. The fix is either to bump
`FMC_BBT_RESERVED_BLOCKS` to `4` or to read+restore those blocks
across `fmc_flush`. Either way, the on-flash BBT must round-trip
identically.

Build, Artifacts: same as the prior section.

Test (max 4 min):

```
lease:claim devices="mp135.custom" duration_s=3600 auto_release_on_session_end=true
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="# " timeout_ms=5000
mp135.custom:uart_write data="echo ___BBT_SETUP___; nand=$(ls /sys/class/mtd | grep -E '^mtd[0-9]+$' | tail -1); pages=$(cat /sys/class/mtd/$nand/erasesize); blocks=$(( $(cat /sys/class/mtd/$nand/size) / pages )); for i in 1 2 3 4; do blk=$((blocks - i)); off=$((blk * pages)); printf 'BBT-%d-CANARY' $blk | dd of=/dev/$nand bs=$pages seek=$blk conv=notrunc 2>/dev/null; done; sync; sha256sum /dev/$nand | head -c 64; echo; (for i in 1 2 3 4; do blk=$((blocks - i)); dd if=/dev/$nand bs=$pages skip=$blk count=1 2>/dev/null | sha256sum | head -c 64; echo; done) > /tmp/bbt_pre.txt; cat /tmp/bbt_pre.txt; echo ___BBT_PRE_DONE___; sync; reboot\r"
mp135.custom:uart_expect sentinel="___BBT_SETUP___" timeout_ms=5000
mp135.custom:uart_expect sentinel="___BBT_PRE_DONE___" timeout_ms=20000
mp135.custom:uart_expect sentinel="Restarting system" timeout_ms=30000
mp135.custom:uart_close
delay ms=12000
dfu.custom:flash_layout layout=@flash.tsv no_reconnect=true
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
mp135.custom:uart_expect sentinel="> " timeout_ms=8000
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_write data="fmc_flush\r"
mp135.custom:uart_expect sentinel="tail-erased" timeout_ms=30000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_write data="fmc_bload\r"
mp135.custom:uart_expect sentinel="bload: done" timeout_ms=30000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_write data="jump\r"
mp135.custom:uart_expect sentinel="login:" timeout_ms=60000
mp135.custom:uart_write data="root\r"
mp135.custom:uart_expect sentinel="Password:" timeout_ms=3000
mp135.custom:uart_write data="root\r"
mp135.custom:uart_expect sentinel="# " timeout_ms=5000
mp135.custom:uart_write data="echo ___BBT_VERIFY___; nand=$(ls /sys/class/mtd | grep -E '^mtd[0-9]+$' | tail -1); pages=$(cat /sys/class/mtd/$nand/erasesize); blocks=$(( $(cat /sys/class/mtd/$nand/size) / pages )); (for i in 1 2 3 4; do blk=$((blocks - i)); dd if=/dev/$nand bs=$pages skip=$blk count=1 2>/dev/null | sha256sum | head -c 64; echo; done) > /tmp/bbt_post.txt; diff /tmp/bbt_pre.txt /tmp/bbt_post.txt && echo ___BBT_MATCH___ || echo ___BBT_MISMATCH___; echo ___BBT_VERIFY_END___\r"
mp135.custom:uart_expect sentinel="___BBT_VERIFY___" timeout_ms=5000
mp135.custom:uart_expect sentinel="___BBT_MATCH___" timeout_ms=15000
mp135.custom:uart_expect sentinel="___BBT_VERIFY_END___" timeout_ms=5000
mp135.custom:uart_close
lease:release
mark tag=bbt_preserved_across_fmc_flush
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    return ('___BBT_PRE_DONE___' in uart
            and '___BBT_MATCH___' in uart
            and '___BBT_MISMATCH___' not in uart
            and '___BBT_VERIFY_END___' in uart
            and 'tail-erased' in uart)
```

### ECC fault-injection visible in dmesg: bit-flip is corrected

From a clean Linux boot, choose a known-good UBI PEB, raw-write it
with one data-bit flipped, then read the page back via `dd
if=/dev/mtdN`. The kernel BCH driver must report the bit-flip in
`dmesg` (e.g. `nand_bch: corrected N errors`) and the read must
return the corrected data. This proves BCH actually corrects rather
than passing-through silently.

Today there is no regression evidence that BCH does anything; the
bootloader's `fmc_test_write`/`fmc_test_read` exist but are never
invoked, and the kernel side is untested. This test pins the
correction path. The fix scope is small: it only requires
`mtd-utils` in buildroot and a counter exposed by the BCH driver
(both already present in mainline).

Build, Artifacts: same as the prior section.

Test (max 3 min):

```
lease:claim devices="mp135.custom" duration_s=3600 auto_release_on_session_end=true
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="# " timeout_ms=5000
mp135.custom:uart_write data="echo ___BCH_PROBE___; mtd=$(grep -E '\"rootfs\"' /proc/mtd | cut -d: -f1); pgsz=$(cat /sys/class/mtd/$mtd/writesize); peb=$(cat /sys/class/mtd/$mtd/erasesize); blocks=$(( $(cat /sys/class/mtd/$mtd/size) / peb )); good=$((blocks - 8)); off=$((good * peb)); dd if=/dev/$mtd bs=$pgsz skip=$((off / pgsz)) count=1 of=/tmp/orig.bin 2>/dev/null; cp /tmp/orig.bin /tmp/flipped.bin; printf '\\x01' | dd of=/tmp/flipped.bin bs=1 seek=128 conv=notrunc 2>/dev/null; flash_erase /dev/$mtd $off 1; nandwrite -p -s $off --noskipbad /dev/$mtd /tmp/flipped.bin; dmesg -c >/dev/null; dd if=/dev/$mtd bs=$pgsz skip=$((off / pgsz)) count=1 of=/tmp/read.bin 2>/dev/null; cmp /tmp/orig.bin /tmp/read.bin && echo ___BCH_DATA_OK___ || echo ___BCH_DATA_MISMATCH___; dmesg | grep -iE 'bch|bitflip|corrected' | head -5; echo ___BCH_END___\r"
mp135.custom:uart_expect sentinel="___BCH_PROBE___" timeout_ms=5000
mp135.custom:uart_expect sentinel="___BCH_DATA_OK___" timeout_ms=30000
mp135.custom:uart_expect sentinel="___BCH_END___" timeout_ms=5000
mp135.custom:uart_close
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="# " timeout_ms=3000
mp135.custom:uart_write data="reboot\r"
mp135.custom:uart_expect sentinel="Restarting system" timeout_ms=30000
mp135.custom:uart_close
delay ms=12000
dfu.custom:flash_layout layout=@flash.tsv no_reconnect=true
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
mp135.custom:uart_expect sentinel="> " timeout_ms=8000
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
inventory refresh=true verify=false
msc.custom:write data=@nand.img offset_lba=0 min_rate_Bps=3000000
mp135.custom:uart_write data="fmc_flush\r"
mp135.custom:uart_expect sentinel="tail-erased" timeout_ms=30000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_close
lease:release
mark tag=bch_bitflip_corrected
```

Verify:

```
import re

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    if '___BCH_DATA_OK___' not in uart:
        return False
    if '___BCH_DATA_MISMATCH___' in uart:
        return False
    # dmesg must show at least one BCH/bitflip correction.
    if not re.search(r'(?i)(bitflip|corrected\s+\d+\s+(errors|bitflips))',
                     uart.split('___BCH_DATA_OK___')[1].split(
                         '___BCH_END___')[0]):
        return False
    return 'tail-erased' in uart
```

### Hardened kernel image: bootloader refuses to jump on hash mismatch

The fix adds an SHA-256 of the kernel image to the partition-table
struct (`nand_pt_t`) at flash time. After a clean provision, corrupt
one byte inside the kernel area (raw write that does NOT also fix
ECC, so the read has correctable bit errors but the kernel content
itself is altered). Reload the bootloader, run `fmc_bload`. The
bootloader must compute the SHA-256 over the loaded kernel, compare
against the PT-stored hash, log `kernel: hash mismatch (expected ... got ...)`
on UART, and refuse to `jump`.

This catches the failure mode where ECC silently corrects too few
errors, or a future code path skips the ECC check, or someone builds
a kernel that the partition table doesn't actually point at.

Build, Artifacts: same as the prior section.

Test (max 4 min):

```
lease:claim devices="mp135.custom" duration_s=3600 auto_release_on_session_end=true
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="# " timeout_ms=5000
mp135.custom:uart_write data="echo ___KHASH_INJECT___; mtd=$(grep -E '\"kernel\"' /proc/mtd | cut -d: -f1); pgsz=$(cat /sys/class/mtd/$mtd/writesize); dd if=/dev/$mtd bs=$pgsz count=1 of=/tmp/k0.bin 2>/dev/null; cp /tmp/k0.bin /tmp/k0_corrupt.bin; printf '\\xa5' | dd of=/tmp/k0_corrupt.bin bs=1 seek=64 conv=notrunc 2>/dev/null; flash_erase /dev/$mtd 0 1; nandwrite -p -s 0 /dev/$mtd /tmp/k0_corrupt.bin; sync; echo ___KHASH_REBOOT___; sync; reboot\r"
mp135.custom:uart_expect sentinel="___KHASH_INJECT___" timeout_ms=5000
mp135.custom:uart_expect sentinel="___KHASH_REBOOT___" timeout_ms=15000
mp135.custom:uart_expect sentinel="Restarting system" timeout_ms=30000
mp135.custom:uart_close
delay ms=12000
dfu.custom:flash_layout layout=@flash.tsv no_reconnect=true
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
mp135.custom:uart_expect sentinel="> " timeout_ms=8000
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_write data="fmc_bload\r"
mp135.custom:uart_expect sentinel="kernel: hash mismatch" timeout_ms=30000
mp135.custom:uart_expect sentinel="bload: refused" timeout_ms=5000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_write data="jump\r"
mp135.custom:uart_expect sentinel="jump: no kernel loaded" timeout_ms=3000
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
inventory refresh=true verify=false
msc.custom:write data=@nand.img offset_lba=0 min_rate_Bps=3000000
mp135.custom:uart_write data="fmc_flush\r"
mp135.custom:uart_expect sentinel="tail-erased" timeout_ms=30000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_close
lease:release
mark tag=kernel_hash_refuses_jump
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    must = ('___KHASH_INJECT___', 'kernel: hash mismatch',
            'bload: refused', 'jump: no kernel loaded',
            'tail-erased')
    if not all(s in uart for s in must):
        return False
    after = uart.split('kernel: hash mismatch')[1]
    return 'Linux version' not in after.split('tail-erased')[0]
```

### Hardened PT/DTB: redundant copy boots when primary is corrupted

The fix places redundant partition-table and DTB copies at known
offsets (PT-mirror and DTB-mirror). After a clean provision, corrupt
the primary PT block (block 2) so its checksum fails; reload the
bootloader, run `fmc_bload`. The bootloader must log
`pt: primary checksum mismatch` and `pt: using mirror`, then load
the DTB and kernel and proceed; `jump` must boot Linux. Repeat for
the primary DTB block: it must log `dtb: bad magic` and
`dtb: using mirror`, and Linux must boot.

This catches the single-uncorrectable-bit-bricks-the-board failure
mode that the audit flagged.

Build, Artifacts: same as the prior section.

Test (max 5 min):

```
lease:claim devices="mp135.custom" duration_s=3600 auto_release_on_session_end=true
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="# " timeout_ms=5000
mp135.custom:uart_write data="echo ___PT_CORRUPT___; mtd=$(grep -E '\"ptable\"' /proc/mtd | cut -d: -f1); peb=$(cat /sys/class/mtd/$mtd/erasesize); flash_erase /dev/$mtd 0 1; dd if=/dev/urandom of=/tmp/junk.bin bs=$peb count=1 2>/dev/null; nandwrite -p -s 0 /dev/$mtd /tmp/junk.bin; sync; echo ___PT_REBOOT___; sync; reboot\r"
mp135.custom:uart_expect sentinel="___PT_CORRUPT___" timeout_ms=5000
mp135.custom:uart_expect sentinel="___PT_REBOOT___" timeout_ms=15000
mp135.custom:uart_expect sentinel="Restarting system" timeout_ms=30000
mp135.custom:uart_close
delay ms=12000
dfu.custom:flash_layout layout=@flash.tsv no_reconnect=true
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
mp135.custom:uart_expect sentinel="> " timeout_ms=8000
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_write data="fmc_bload\r"
mp135.custom:uart_expect sentinel="pt: primary checksum mismatch" timeout_ms=30000
mp135.custom:uart_expect sentinel="pt: using mirror" timeout_ms=3000
mp135.custom:uart_expect sentinel="bload: done" timeout_ms=30000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_write data="jump\r"
mp135.custom:uart_expect sentinel="login:" timeout_ms=60000
mp135.custom:uart_write data="root\r"
mp135.custom:uart_expect sentinel="Password:" timeout_ms=3000
mp135.custom:uart_write data="root\r"
mp135.custom:uart_expect sentinel="# " timeout_ms=5000
mp135.custom:uart_write data="echo ___DTB_CORRUPT___; mtd=$(grep -E '\"dtb\"' /proc/mtd | cut -d: -f1); peb=$(cat /sys/class/mtd/$mtd/erasesize); flash_erase /dev/$mtd 0 1; dd if=/dev/urandom of=/tmp/junk.bin bs=$peb count=1 2>/dev/null; nandwrite -p -s 0 /dev/$mtd /tmp/junk.bin; sync; echo ___DTB_REBOOT___; sync; reboot\r"
mp135.custom:uart_expect sentinel="___DTB_CORRUPT___" timeout_ms=5000
mp135.custom:uart_expect sentinel="___DTB_REBOOT___" timeout_ms=15000
mp135.custom:uart_expect sentinel="Restarting system" timeout_ms=30000
mp135.custom:uart_close
delay ms=12000
dfu.custom:flash_layout layout=@flash.tsv no_reconnect=true
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
mp135.custom:uart_expect sentinel="> " timeout_ms=8000
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_write data="fmc_bload\r"
mp135.custom:uart_expect sentinel="dtb: bad magic" timeout_ms=30000
mp135.custom:uart_expect sentinel="dtb: using mirror" timeout_ms=3000
mp135.custom:uart_expect sentinel="bload: done" timeout_ms=30000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_write data="jump\r"
mp135.custom:uart_expect sentinel="login:" timeout_ms=60000
mp135.custom:uart_close
inventory refresh=true verify=false
msc.custom:write data=@nand.img offset_lba=0 min_rate_Bps=3000000
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_write data="fmc_flush\r"
mp135.custom:uart_expect sentinel="tail-erased" timeout_ms=30000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_close
lease:release
mark tag=pt_dtb_mirror_failover
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    must = ('___PT_CORRUPT___', 'pt: primary checksum mismatch',
            'pt: using mirror',
            '___DTB_CORRUPT___', 'dtb: bad magic',
            'dtb: using mirror',
            'tail-erased')
    if not all(s in uart for s in must):
        return False
    # Both fail-over paths must reach the Linux login prompt.
    return uart.count('login:') >= 2
```

### Crash recovery: power-cut mid-write leaves UBIFS mountable

From a clean Linux boot, start a 200 MiB write to `/root/cleanup.bin`
in the background, sleep ~2 s, then trigger a hardware reset via
`bench_mcu:reset_dut2` mid-write. Reload only the bootloader via DFU
and boot Linux from the same NAND. UBI/UBIFS must attach without
errors; `dmesg` must contain no `UBIFS error`, no `UBI error`, no
`uncorrectable`/`unrecoverable`, and no `Kernel panic`. The
filesystem must be mountable read-write, and a follow-up
`/root/recovered_marker.txt` write+sync must succeed.

This is the only test in the suite that exercises the journaled
recovery path. UBIFS is supposed to handle this; the test pins it.

Build, Artifacts: same as the prior section.

Test (max 5 min):

```
lease:claim devices="mp135.custom" duration_s=3600 auto_release_on_session_end=true
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="# " timeout_ms=5000
mp135.custom:uart_write data="echo ___CRASH_BEGIN___; mount -o remount,rw /; ( dd if=/dev/urandom of=/root/cleanup.bin bs=1M count=200 conv=fsync; echo ___CRASH_DD_DONE___ ) & echo ___CRASH_DD_BG_PID_$!___; sleep 2; echo ___CRASH_RESET_NOW___\r"
mp135.custom:uart_expect sentinel="___CRASH_DD_BG_PID_" timeout_ms=5000
mp135.custom:uart_expect sentinel="___CRASH_RESET_NOW___" timeout_ms=10000
mp135.custom:uart_close
bench_mcu:reset_dut2
delay ms=4000
dfu.custom:flash_layout layout=@flash.tsv no_reconnect=true
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
mp135.custom:uart_expect sentinel="> " timeout_ms=8000
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_write data="fmc_bload\r"
mp135.custom:uart_expect sentinel="bload: done" timeout_ms=30000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_write data="jump\r"
mp135.custom:uart_expect sentinel="Linux version" timeout_ms=10000
mp135.custom:uart_expect sentinel="ubi0: attached mtd" timeout_ms=20000
mp135.custom:uart_expect sentinel="login:" timeout_ms=60000
mp135.custom:uart_write data="root\r"
mp135.custom:uart_expect sentinel="Password:" timeout_ms=3000
mp135.custom:uart_write data="root\r"
mp135.custom:uart_expect sentinel="# " timeout_ms=5000
mp135.custom:uart_write data="echo ___CRASH_CHECK___; mount -o remount,rw /; echo recovered-$(date +%s) >/root/recovered_marker.txt; sync; cat /root/recovered_marker.txt; dmesg | grep -iE 'UBIFS error|UBI error|ECC|uncorrect|panic' | head -5; echo ___CRASH_CHECK_END___\r"
mp135.custom:uart_expect sentinel="___CRASH_CHECK___" timeout_ms=5000
mp135.custom:uart_expect sentinel="recovered-" timeout_ms=10000
mp135.custom:uart_expect sentinel="___CRASH_CHECK_END___" timeout_ms=10000
mp135.custom:uart_close
lease:release
mark tag=power_loss_ubifs_recovers
```

Verify:

```
import re

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    must = ('___CRASH_RESET_NOW___', '___CRASH_CHECK___',
            'recovered-', '___CRASH_CHECK_END___',
            'ubi0: attached mtd', 'login:')
    if not all(s in uart for s in must):
        return False
    post_reset = uart.split('___CRASH_RESET_NOW___')[1]
    bad = (r'Kernel panic', r'Unable to mount root fs', r'UBIFS error',
           r'UBI error', r'ECC error', r'uncorrectable',
           r'unrecoverable')
    return not any(re.search(p, post_reset, re.I) for p in bad)
```

### Round-trip: full-image diff between MSC write and `fmc_load` readback

Today's round-trip section diffs only the leading 4 MiB of `nand.img`
against the MSC readback (`min(len(img), len(got), 4194304)`). A bug
that corrupts blocks past 16 (4 MiB / 256 KiB erase block) silently
passes. Replace the 4 MiB cap with a full-image diff: poison the
entire DDR window (`msc.custom:write_zeroes` for the full nand.img
length, then `verify_zeroes` to prove the poison landed), `fmc_load`
the full image, MSC-read the full image, diff every byte.

The fix is purely a test-side change: extend the existing
round-trip to use `len(img)` instead of `min(..., 4194304)` and
extend the poison/verify-zeroes range accordingly. No bootloader
change should be needed if `fmc_load` is correct; if it is not, this
test exposes that.

Build, Artifacts: same as the existing round-trip section.

Test (max 4 min):

```
lease:claim devices="mp135.custom" duration_s=3600
bench_mcu:reset_dut2
delay ms=2000
dfu.custom:flash_layout layout=@flash.tsv no_reconnect=true
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
mp135.custom:uart_expect sentinel="> " timeout_ms=8000
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_close
inventory
msc.custom:write data=@nand.img offset_lba=0 min_rate_Bps=3000000
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_write data="fmc_flush\r"
mp135.custom:uart_expect sentinel="FMC flush:" timeout_ms=3000
mp135.custom:uart_expect sentinel="tail-erased" timeout_ms=30000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_close
msc.custom:write_zeroes data=@nand.img offset_lba=0 min_rate_Bps=3000000
msc.custom:verify_zeroes data=@nand.img offset_lba=0 min_rate_Bps=3000000
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_write data="fmc_load\r"
mp135.custom:uart_expect sentinel="FMC load:" timeout_ms=3000
mp135.custom:uart_expect sentinel="rd errs" timeout_ms=120000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_close
msc.custom:read data=@nand.img offset_lba=0 min_rate_Bps=3000000
lease:release
mark tag=nand_round_trip_full_image
```

Verify:

```
from pathlib import Path

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    img = Path(artifacts['nand.img']).read_bytes()
    got = Verification.load_stream(extract_dir, 'msc.read')
    if len(got) < len(img):
        return False
    return got[:len(img)] == img
```

Note: `msc.custom:write_zeroes` and `msc.custom:verify_zeroes`
already accept a sized buffer — the existing 4 MiB round-trip uses
`n=4194304`. The full-image variant requires either a `data=@nand.img`
form (size taken from the file) or an `n=$(stat -c %s nand.img)`
substitution at submission time. If neither form is supported, add
the smaller form — sizing the poison from the artifact file is
cleaner than hand-rolling the byte count.

### Wear-leveling stress: 100 cycles of full-volume churn, even erase counts

Extend the existing 5-iteration 50 MiB loop to 100 iterations of
nearly-full-volume churn (e.g. `dd if=/dev/urandom of=/root/big.bin
bs=1M count=300`), and assert at the end that the per-PEB erase-count
histogram from `ubinfo -a` is reasonably even (max/min ratio < 4
across the data PEBs that were touched). Wear-leveling that does not
spread writes within an order of magnitude across cycles is not
production-grade.

This test is long-running (estimated ~3 hours; ~100 reboots × ~50 s
each). It should be its own section behind a non-default flag if
runtime concerns force a tradeoff, but the suite must include it for
any production-grade claim. The current 5-iteration test demonstrates
clean-shutdown durability, not wear-leveling.

Build, Artifacts: same as the prior section.

Foreach:

```
loop in count(100)
```

Test (max 4 min):

```
lease:claim devices="mp135.custom" duration_s=3600 auto_release_on_session_end=true
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="# " timeout_ms=5000
mp135.custom:uart_write data="echo ___WEAR_START___; mount -o remount,rw /; rm -f /root/big.bin /root/big.sha256; dd if=/dev/urandom of=/root/big.bin bs=1M count=300 conv=fsync; rc=$?; echo ___WEAR_DD_RC_${rc}___; sha256sum /root/big.bin >/root/big.sha256; sync; mount -o remount,ro /; ubinfo -a > /tmp/ubi_before.txt 2>&1; echo ___WEAR_REBOOT___; sync; reboot\r"
mp135.custom:uart_expect sentinel="___WEAR_START___" timeout_ms=5000
mp135.custom:uart_expect sentinel="___WEAR_DD_RC_0___" timeout_ms=240000
mp135.custom:uart_expect sentinel="___WEAR_REBOOT___" timeout_ms=15000
mp135.custom:uart_expect sentinel="Restarting system" timeout_ms=30000
mp135.custom:uart_close
delay ms=12000
dfu.custom:flash_layout layout=@flash.tsv no_reconnect=true
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
mp135.custom:uart_expect sentinel="> " timeout_ms=8000
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_write data="fmc_bload\r"
mp135.custom:uart_expect sentinel="bload: done" timeout_ms=30000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_write data="jump\r"
mp135.custom:uart_expect sentinel="login:" timeout_ms=60000
mp135.custom:uart_write data="root\r"
mp135.custom:uart_expect sentinel="Password:" timeout_ms=3000
mp135.custom:uart_write data="root\r"
mp135.custom:uart_expect sentinel="# " timeout_ms=5000
mp135.custom:uart_write data="echo ___WEAR_VERIFY___; sha256sum -c /root/big.sha256; ubinfo -a | awk '/Erase counter/ {print}' | head -50; echo ___WEAR_END___\r"
mp135.custom:uart_expect sentinel="/root/big.bin: OK" timeout_ms=120000
mp135.custom:uart_expect sentinel="___WEAR_END___" timeout_ms=15000
mp135.custom:uart_close
lease:release
mark tag=wear_level_100_cycles
```

Verify:

```
import re

def check(extract_dir, loop):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    if '/root/big.bin: OK' not in uart:
        return False
    if '___WEAR_END___' not in uart:
        return False
    bad = (r'Kernel panic', r'Unable to mount root fs', r'UBIFS error',
           r'UBI error', r'ECC error', r'uncorrectable', r'unrecoverable',
           r'/root/big.bin: FAILED', r'No space left on device')
    if any(re.search(p, uart, re.I) for p in bad):
        return False
    # On the FINAL iteration only, check erase-count evenness.
    if loop == '100':
        ec = [int(m.group(1)) for m in
              re.finditer(r'Erase counter[^\d]*?(\d+)', uart)]
        if len(ec) < 32:
            return False
        ec = sorted(ec)
        # Drop the smallest 5% (cold reserved PEBs) before computing
        # the spread; UBI keeps a few PEBs that genuinely never get
        # touched.
        active = ec[max(1, len(ec) // 20):]
        if not active:
            return False
        if active[-1] / max(active[0], 1) > 4:
            return False
    return True
```
