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

- [NAND provisioning erases stale UBI rootfs tail](#nand-provisioning-erases-stale-ubi-rootfs-tail)
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
- [Final speed characterization: bootloader and Linux verified read/write table](#final-speed-characterization-bootloader-and-linux-verified-readwrite-table)

### NAND provisioning erases stale UBI rootfs tail

Regression guard for a prior failure where NAND boot reached Linux but
panicked while mounting UBIFS because UBI saw stale eraseblocks after
the newly written image. The observed signature was:

```
ubi0: attaching mtd4
ubi0 error: scan_peb.constprop.0: bad image sequence number 540517424 in PEB 46, expected 1951870196
ubi_attach_mtd_dev: failed to attach mtd4, error -22
VFS: Cannot open root device "ubi0:rootfs" or unknown-block(0,0): error -19
Kernel panic - not syncing: VFS: Unable to mount root fs on unknown-block(0,0)
```

At the time, `fmc_flush` reported `FMC flush: 114 blocks`; the rootfs
partition starts at block 68, so UBI PEB 46 maps to physical block 114,
the first block after the flushed image. This test keeps NAND
provisioning from regressing: the rootfs tail after `nand.img` must be
erased or otherwise invalidated while preserving the factory/runtime
bad-block OOB markers. Do not solve this by bulk-erasing bad-block
metadata or lowering MSC rate requirements.

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
bench_mcu:reset_dut2
delay ms=10000
inventory refresh=true verify=false
bench_mcu:reset_dut2
delay ms=10000
inventory refresh=true verify=false
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
inventory
msc.custom:write data=@nand.img offset_lba=0 min_rate_Bps=3000000
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_write data="fmc_flush\r"
mp135.custom:uart_expect sentinel="FMC flush:" timeout_ms=3000
mp135.custom:uart_expect sentinel="tail-erased" timeout_ms=60000
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
import re

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
import re

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

Test (max 1 min):

```
lease:claim devices="mp135.custom" duration_s=3600
bench_mcu:reset_dut2
delay ms=10000
inventory refresh=true verify=false
bench_mcu:reset_dut2
delay ms=10000
inventory refresh=true verify=false
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
import re

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    return (Verification.op_succeeded(ops, 'dfu.custom', 'flash_layout')
            and Verification.op_succeeded(ops, 'mp135.custom', 'uart_expect'))
```

### Bootloader hold via UART

Claims a fresh lease, physically resets the board, reloads the NAND
bootloader over DFU, and confirms UART can stop autoboot at `> `. This
proves the test can reliably re-enter a known bootloader state instead
of depending on stale UART state from the previous job.

Build: nothing required.

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
```

Test (max 30 s):

```
lease:claim devices="mp135.custom" duration_s=3600
bench_mcu:reset_dut2
delay ms=10000
inventory refresh=true verify=false
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
mark tag=bootloader_hold
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

### MSC + NAND probe smoke

Re-enters bootloader hold from a fresh DUT reset and re-flash so this
section does not depend on however long the bench was held earlier in
the run. Refresh inventory so `msc.custom` shows up, read 1 MiB from the
DDR window, and run `fmc_test_boot` to confirm the FMC controller is
initialised and can probe the NAND boot image. The command must produce
a real probe marker before the test accepts the returned prompt; a stale
pre-command prompt does not prove that `fmc_test_boot` ran. The 3 MB/s
MSC read floor is a hard requirement; failing it means the bootloader
path is broken, not that the test threshold should be reduced.

Build: nothing required.

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
```

Test (max 1 min):

```
lease:resume token="{{LEASE_TOKEN}}"
bench_mcu:reset_dut2
delay ms=10000
inventory refresh=true verify=false
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
msc.custom:read n=1048576 offset_lba=0 min_rate_Bps=3000000
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_write data="fmc_test_boot\r"
mp135.custom:uart_expect sentinel="FDT magic" timeout_ms=5000
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
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
    return 'FDT magic' in uart or 'partition table:' in uart
```

### NAND image round-trip: write -> fmc_flush -> poison -> fmc_load -> diff

Write `nand.img` to DDR via MSC, `fmc_flush` to NAND, `fmc_load` back
into DDR, MSC-read and offline-diff the leading bytes. This step waits
for `fmc_flush` to finish; it does not require a nonzero tail erase
count because stale-tail coverage lives in the dedicated provisioning
regression above. Before `fmc_load`, overwrite the leading DDR staging
window with deterministic zeroes and verify the poison landed, so a
no-op `fmc_load` cannot pass by reading back the original MSC write.
The image build can outlive an in-memory bench lease if the poller
restarts, so this step claims a fresh lease after the build and
re-enters the bootloader state it needs. The 3 MB/s MSC write and read
floors are hard requirements for NAND provisioning; sub-3 MB/s results
are code failures.

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
lease:claim devices="mp135.custom" duration_s=3600
bench_mcu:reset_dut2
delay ms=10000
inventory refresh=true verify=false
bench_mcu:reset_dut2
delay ms=10000
inventory refresh=true verify=false
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
inventory
msc.custom:write data=@nand.img offset_lba=0 min_rate_Bps=3000000
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_write data="fmc_flush\r"
mp135.custom:uart_expect sentinel="FMC flush:" timeout_ms=3000
mp135.custom:uart_expect sentinel="new-bad" timeout_ms=60000
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
    if len(got) != 4194304:
        return False
    uart = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    if not all(s in uart for s in ('FMC flush:', 'done:',
                                   'FMC load:', 'rd errs')):
        return False
    return got == img[:len(got)]
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
lease:release token="{{LEASE_TOKEN}}"
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

Claims a fresh bench lease and reloads the NAND bootloader so this
check does not depend on a still-live cross-section lease token. It
boots Linux from the already-provisioned NAND contents with
`fmc_bload` + `jump`, then talks to Linux over the serial console. Logs
in as `root`/`root`, prints
`/proc/mtd`, `ubinfo -a`, `mtdinfo -a`, and a filtered `dmesg`.
Asserts the expected partitions are present, UBI reports zero corrupted
PEBs, factory bad PEBs stay within a board-realistic bound, and `dmesg`
is clear of UBI/UBIFS/ECC errors.
Requires `BR2_PACKAGE_MTD=y` in `config/buildroot.conf` for the
mtd-utils binaries.

Build:

```
make -C stm32mp135_test_board/bootloader -j$(nproc) CFLAGS_EXTRA=-DNAND_FLASH
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
```

Test (max 1 min):

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
lease:release
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

Test (max 4 min):

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
five times with `Foreach`. Each iteration first reloads only the
bootloader through DFU, boots from the existing NAND contents, logs in,
checks an existing `/root/bigfile` against `/root/bigfile.sha256` when
present, writes a fresh 50 MiB random file on `/`, stores its checksum
beside it, reboots Linux, reloads only the bootloader through DFU, boots
from the same NAND contents, logs in, emits a fresh verify-phase shell
sentinel, and verifies the checksum again. The post-reboot login path
must not rely on generic UART sentinels already emitted by the first
boot in the same plan: after the second `jump`, it waits for Linux to
finish booting, sends the login exchange without matching stale
`login:`/`Password:`/`# ` text, then requires a unique verify-phase
echo before the checksum check. After Linux reaches `Restarting
system`, the bench reset line must drive the board back into ROM DFU
before the second bootloader-only flash; waiting on the Linux reboot
tail alone is not a reliable DFU entry condition.
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

Test (max 12 min):

```
lease:claim devices="mp135.custom" duration_s=3600 auto_release_on_session_end=true
bench_mcu:reset_dut2
delay ms=10000
inventory refresh=true verify=false
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
mp135.custom:uart_write data="echo ___ROOT_LOOP_START___; mount -o remount,rw /; if [ -f /root/bigfile ] && [ -f /root/bigfile.sha256 ]; then sha256sum -c /root/bigfile.sha256 || echo ___ROOT_LOOP_PRECHECK_''FAIL___; else echo ___ROOT_LOOP_NO_PRECHECK___; fi; echo ___ROOT_LOOP_DD_BEGIN___; rm -f /root/bigfile /root/bigfile.sha256; dd if=/dev/urandom of=/root/bigfile bs=1M count=50; rc=$?; echo ___ROOT_LOOP_DD_RC_${rc}___; sha256sum /root/bigfile >/root/bigfile.sha256; cat /root/bigfile.sha256; sync; mount -o remount,ro /; echo ___ROOT_LOOP_REBOOT___; sync; reboot\r"
mp135.custom:uart_expect sentinel="___ROOT_LOOP_START___" timeout_ms=5000
mp135.custom:uart_expect sentinel="___ROOT_LOOP_DD_BEGIN___" timeout_ms=30000
mp135.custom:uart_expect sentinel="___ROOT_LOOP_DD_RC_0___" timeout_ms=240000
mp135.custom:uart_expect sentinel="/root/bigfile" timeout_ms=120000
mp135.custom:uart_expect sentinel="___ROOT_LOOP_REBOOT___" timeout_ms=10000
mp135.custom:uart_expect sentinel="Restarting system" timeout_ms=30000
mp135.custom:uart_close
delay ms=12000
bench_mcu:reset_dut2
delay ms=10000
inventory refresh=true verify=false
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
delay ms=45000
mp135.custom:uart_write data="\r"
delay ms=1000
mp135.custom:uart_write data="root\r"
delay ms=1000
mp135.custom:uart_write data="root\r"
delay ms=3000
mp135.custom:uart_write data="echo ___ROOT_LOOP_VERIFY_LOGIN_READY___\r"
mp135.custom:uart_expect sentinel="___ROOT_LOOP_VERIFY_LOGIN_READY___" timeout_ms=10000
mp135.custom:uart_write data="echo ___ROOT_LOOP_VERIFY_BEGIN___; sha256sum -c /root/bigfile.sha256 && echo ___ROOT_LOOP_VERIFY_SHA_OK___; dmesg | grep -iE 'UBI|UBIFS|ECC|uncorrect|panic' || true; echo ___ROOT_LOOP_VERIFY_END___\r"
mp135.custom:uart_expect sentinel="___ROOT_LOOP_VERIFY_BEGIN___" timeout_ms=5000
mp135.custom:uart_expect sentinel="___ROOT_LOOP_VERIFY_SHA_OK___" timeout_ms=120000
mp135.custom:uart_expect sentinel="___ROOT_LOOP_VERIFY_END___" timeout_ms=15000
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
            and '___ROOT_LOOP_VERIFY_LOGIN_READY___' in uart
            and '___ROOT_LOOP_VERIFY_SHA_OK___' in uart
            and '___ROOT_LOOP_VERIFY_END___' in uart
            and not any(re.search(p, uart, re.I) for p in bad))
```

### ECC read status branch preflight

Before the bootloader can reject corrupted NAND data, its low-level
page-read path must stop ignoring the HAL ECC status. Add the smallest
bootloader-side contract first: `read_page` must call the HAL ECC
statistics API after each page read and contain an explicit
`BadSectorCount > 0` failure branch. This step intentionally does not
require the production UART sentinel or `fmc_bload` abort behavior; the
next preflight wires that detected read failure into the higher boot
path.

Build:

```
make -C stm32mp135_test_board/bootloader -j$(nproc) CFLAGS_EXTRA=-DNAND_FLASH
```

Artifacts:

```
stm32mp135_test_board/bootloader/build/main.stm32
```

Test: no hardware.

Verify:

```
import re
from pathlib import Path

def check(_extract_dir):
    fmc = Path('stm32mp135_test_board/bootloader/src/fmc.c')
    image = Path('stm32mp135_test_board/bootloader/build/main.stm32')
    if not fmc.is_file() or not image.is_file() or image.stat().st_size == 0:
        return False
    text = fmc.read_text(encoding='utf-8', errors='replace')
    start = text.find('static HAL_StatusTypeDef read_page(')
    end = text.find('static HAL_StatusTypeDef write_page(', start)
    if start < 0 or end < 0:
        return False
    body = text[start:end]
    return ('HAL_NAND_ECC_GetStatistics' in body
            and 'BadSectorCount' in body
            and bool(re.search(r'BadSectorCount\s*>\s*0', body)))
```

### ECC read status propagation preflight

Before injecting raw NAND corruption on hardware, add the bootloader-side
contract that makes uncorrectable ECC observable to the higher boot
path. The bootloader NAND page-read path must inspect the HAL ECC
status for each page read, treat any uncorrectable sector count as a
hard read failure, and emit the production sentinel
`fmc: ECC unrecoverable` from the real FMC read path. This step is
limited to making that read failure impossible to silently ignore; the
following end-to-end section still proves that `fmc_bload` refuses the
kernel and that `jump` does not enter Linux after deliberate NAND
corruption.

Build:

```
make -C stm32mp135_test_board/bootloader -j$(nproc) CFLAGS_EXTRA=-DNAND_FLASH
```

Artifacts:

```
stm32mp135_test_board/bootloader/build/main.stm32
```

Test: no hardware.

Verify:

```
import re
from pathlib import Path

def check(_extract_dir):
    fmc = Path('stm32mp135_test_board/bootloader/src/fmc.c')
    image = Path('stm32mp135_test_board/bootloader/build/main.stm32')
    if not fmc.is_file() or not image.is_file() or image.stat().st_size == 0:
        return False
    text = fmc.read_text(encoding='utf-8', errors='replace')
    start = text.find('static HAL_StatusTypeDef read_page(')
    end = text.find('static HAL_StatusTypeDef write_page(', start)
    if start < 0 or end < 0:
        return False
    body = text[start:end]
    needed = ('HAL_NAND_ECC_GetStatistics', 'BadSectorCount',
              'fmc: ECC unrecoverable')
    if not all(s in body for s in needed):
        return False
    return bool(re.search(r'BadSectorCount\s*>\s*0', body))
```

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

The corruption uses `nandflipbits` on the kernel mtd partition. It
flips 9 bits in one 512-byte ECC sector of the third kernel page, which
exceeds BCH-8 correction while avoiding the first two pages whose OOB
bytes are used as bad-block markers. Linux must keep `mtdX` for the
kernel slot (currently kernel is at NAND blocks 4..67 per
`nand_pt.h`). The test must only reboot after `nandflipbits` succeeds;
a failed injection is a test failure, not permission to continue.

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
mp135.custom:uart_write data="echo ___ECC_INJECT___; mtd=$(grep kernel /proc/mtd | cut -d: -f1); rc=1; if test x$mtd != x && test -r /sys/class/mtd/$mtd/writesize && command -v nandflipbits >/dev/null 2>&1; then pgsz=$(cat /sys/class/mtd/$mtd/writesize); off=$((2 * pgsz)); echo MTD=$mtd PGSZ=$pgsz OFF=$off; nandflipbits -q /dev/$mtd 0@$off 1@$off 2@$off 3@$off 4@$off 5@$off 6@$off 7@$off 0@$((off + 1)); rc=$?; else echo ___ECC_INJECT_PREREQ_FAIL___; fi; if test x$rc = x0; then sync; echo ___ECC_REBOOT___; sync; reboot; else echo ___ECC_INJECT_FAIL_${rc}___; fi\r"
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
delay ms=5000
inventory refresh=true verify=false
delay ms=1000
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

Build: same as the prior section.

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
delay ms=1500
mp135.custom:uart_expect sentinel="bad: blk 1500" timeout_ms=60000
mp135.custom:uart_expect sentinel="scan done:" timeout_ms=5000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_close
delay ms=2000
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
mp135.custom:uart_write data="echo ___BBT_''SETUP___; mount -o remount,rw /; nand=$(awk -F: '/rootfs/{print $1; exit}' /proc/mtd); pages=$(cat /sys/class/mtd/${nand}/erasesize); blocks=$(( $(cat /sys/class/mtd/${nand}/size) / pages )); for i in 1 2 3 4; do blk=$((blocks - i)); printf 'BBT-%d-CANARY' $blk | dd of=/dev/$nand bs=$pages seek=$blk conv=notrunc 2>/dev/null; done; sync; echo ___BBT_PRE_HASHES_BEGIN___; for i in 1 2 3 4; do blk=$((blocks - i)); dd if=/dev/$nand bs=$pages skip=$blk count=1 2>/dev/null | sha256sum | head -c 64; echo; done; echo ___BBT_PRE_HASHES_END___; echo ___BBT_PRE_''DONE___; sync; reboot\r"
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
mp135.custom:uart_close
delay ms=2000
inventory refresh=true verify=false
delay ms=2000
msc.custom:write data=@nand.img offset_lba=0 min_rate_Bps=3000000
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_write data="fmc_flush\r"
mp135.custom:uart_expect sentinel="tail-erased" timeout_ms=30000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_write data="fmc_bload\r"
mp135.custom:uart_expect sentinel="bload: done" timeout_ms=30000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_write data="jump\r"
delay ms=12000
mp135.custom:uart_write data="root\r"
delay ms=500
mp135.custom:uart_write data="root\r"
delay ms=1000
mp135.custom:uart_write data="echo ___BBT_''VERIFY___; nand=$(awk -F: '/rootfs/{print $1; exit}' /proc/mtd); pages=$(cat /sys/class/mtd/${nand}/erasesize); blocks=$(( $(cat /sys/class/mtd/${nand}/size) / pages )); echo ___BBT_POST_HASHES_BEGIN___; for i in 1 2 3 4; do blk=$((blocks - i)); dd if=/dev/$nand bs=$pages skip=$blk count=1 2>/dev/null | sha256sum | head -c 64; echo; done; echo ___BBT_POST_HASHES_END___; echo ___BBT_VERIFY_''END___\r"
mp135.custom:uart_expect sentinel="___BBT_VERIFY___" timeout_ms=5000
mp135.custom:uart_expect sentinel="___BBT_POST_HASHES_END___" timeout_ms=15000
mp135.custom:uart_expect sentinel="___BBT_VERIFY_END___" timeout_ms=5000
mp135.custom:uart_close
lease:release
mark tag=bbt_preserved_across_fmc_flush
```

Verify:

```
import re

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    if not ('___BBT_PRE_DONE___' in uart
            and '___BBT_VERIFY_END___' in uart
            and 'tail-erased' in uart):
        return False

    def hashes_between(start, end):
        if start not in uart or end not in uart:
            return []
        # UART contains the submitted shell line before command output.
        body = uart.rsplit(start, 1)[1].split(end, 1)[0]
        return re.findall(r'(?m)^([0-9a-f]{64})\r?$', body)

    pre = hashes_between('___BBT_PRE_HASHES_BEGIN___',
                         '___BBT_PRE_HASHES_END___')
    post = hashes_between('___BBT_POST_HASHES_BEGIN___',
                          '___BBT_POST_HASHES_END___')
    return len(pre) == 4 and pre == post
```

### Linux-side BCH preflight: nandflipbits is built into the rootfs

Before the on-bench BCH bit-flip correction test below can inject a
correctable error, the booted Linux rootfs must contain the
`nandflipbits` userspace utility, and the supporting `mtd-utils`
binaries (`flash_erase`, `nandwrite`) it relies on. This preflight
pins those packages in the buildroot configuration so a regression
that disables them is caught without consuming a bench cycle. It
intentionally does not run any hardware, mount any image, or boot
Linux; the next section is the end-to-end proof that BCH actually
corrects the injected flip.

Build:

```
true
```

Artifacts:

```
stm32mp135_test_board/config/buildroot.conf
```

Test: no hardware.

Verify:

```
import re
from pathlib import Path

def check(_extract_dir):
    cfg = Path('stm32mp135_test_board/config/buildroot.conf')
    if not cfg.is_file():
        return False
    text = cfg.read_text(encoding='utf-8', errors='replace')
    needed = (r'^BR2_PACKAGE_MTD=y\s*$',
              r'^BR2_PACKAGE_MTD_NANDFLIPBITS=y\s*$')
    return all(re.search(p, text, re.M) for p in needed)
```

### Linux-side BCH preflight: stm32_fmc2_nand prints bitflip on correction

The on-bench BCH bit-flip correction test below scrapes UART dmesg
for `(?i)(bitflip|corrected\s+\d+\s+(errors|bitflips))` to confirm
that a hardware-corrected ECC sector was actually observed by the
kernel. Upstream `drivers/mtd/nand/raw/stm32_fmc2_nand.c` is silent
on a successful BCH correction: it only bumps
`mtd->ecc_stats.corrected` and returns `max_bitflips`, with no
`pr_warn`/`dev_warn` carrying the literal substring `bitflip`.
Without a kernel-side print the dmesg sentinel can never match, and
the test below is unprovable regardless of bench reliability.

This preflight pins the contract by adding a `dev_warn` hunk to
`stm32mp135_test_board/config/patch.linux` so that
`make -C stm32mp135_test_board patch` injects the print into the
BCH read-page success path of `stm32_fmc2_nfc_seq_correct`. The
verify block is a static text inspection of the tracked patch file
only; it does not run `make patch` and does not consume a bench
cycle. The next section is the end-to-end proof that BCH actually
corrects the injected flip and that the new print fires.

Build:

```
true
```

Artifacts:

```
stm32mp135_test_board/config/patch.linux
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(_extract_dir):
    patch = Path('stm32mp135_test_board/config/patch.linux')
    if not patch.is_file():
        return False
    text = patch.read_text(encoding='utf-8', errors='replace')
    return 'bitflip' in text and 'stm32_fmc2_nand.c' in text
```

## WIP

The sections below are production-hardening regression tests requested
by an adversarial audit. Each section names a concrete data-loss path
and proves end-to-end that the system either (a) detects and refuses
to act on corrupted state or (b) survives the failure with no silent
corruption. Every test must FAIL on the current bootloader code and
PASS only after the corresponding fix lands; a test that passes today
on the unfixed code is, by construction, not exercising the fix.

Tests below assume the prior 23 sections have left a freshly
provisioned NAND. Each new section re-flashes `nand.img` at its start
so a deliberately-corrupted run cannot leak into the next section.
They also tolerate a degraded final state by re-flashing on Verify if
needed (covered in each section's plan).

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
mp135.custom:uart_write data="echo ___BCH_LOGIN_READY___\r"
mp135.custom:uart_expect sentinel="___BCH_LOGIN_READY___" timeout_ms=5000
mp135.custom:uart_write data="stty -echo\r"
delay ms=200
mp135.custom:uart_write data="cat >/tmp/bch_probe.sh <<'EOF'\r"
mp135.custom:uart_write data="#!/bin/sh\r"
mp135.custom:uart_write data="set -eu\r"
mp135.custom:uart_write data="tag(){ printf '___BCH_%s___\\n' \"$1\"; }\r"
mp135.custom:uart_write data="fail(){ tag \"FAIL_$1\"; exit 1; }\r"
mp135.custom:uart_write data="trap 'stty echo 2>/dev/null || true' EXIT\r"
mp135.custom:uart_write data="tag RUN_BEGIN\r"
mp135.custom:uart_write data="mtd=$(awk -F: '/\"rootfs\"/{print $1; exit}' /proc/mtd)\r"
mp135.custom:uart_write data="[ -n \"$mtd\" ] || fail NO_ROOTFS\r"
mp135.custom:uart_write data="base=/sys/class/mtd/$mtd\r"
mp135.custom:uart_write data="[ -r \"$base/writesize\" ] || fail NO_WRITESIZE\r"
mp135.custom:uart_write data="command -v flash_erase >/dev/null 2>&1 || fail NO_ERASE\r"
mp135.custom:uart_write data="command -v nandwrite >/dev/null 2>&1 || fail NO_WRITE\r"
mp135.custom:uart_write data="command -v nandflipbits >/dev/null 2>&1 || fail NO_FLIP\r"
mp135.custom:uart_write data="pgsz=$(cat \"$base/writesize\")\r"
mp135.custom:uart_write data="peb=$(cat \"$base/erasesize\")\r"
mp135.custom:uart_write data="size=$(cat \"$base/size\")\r"
mp135.custom:uart_write data="blocks=$((size / peb))\r"
mp135.custom:uart_write data="good=$((blocks - 8))\r"
mp135.custom:uart_write data="[ \"$good\" -gt 0 ] || fail BAD_GEOM\r"
mp135.custom:uart_write data="off=$((good * peb))\r"
mp135.custom:uart_write data="page=$((off / pgsz))\r"
mp135.custom:uart_write data="echo BCH_GEOM mtd=$mtd pgsz=$pgsz off=$off page=$page\r"
mp135.custom:uart_write data="dd if=/dev/$mtd bs=$pgsz skip=$page count=1 of=/tmp/bch.orig 2>/tmp/bch.err || fail DD_ORIG\r"
mp135.custom:uart_write data="flash_erase /dev/$mtd $off 1 >/tmp/bch.erase 2>&1 || fail ERASE\r"
mp135.custom:uart_write data="nandwrite -p -s $off --noskipbad /dev/$mtd /tmp/bch.orig >/tmp/bch.write 2>&1 || fail WRITE\r"
mp135.custom:uart_write data="nandflipbits -q /dev/$mtd 0@$((off + 128)) >/tmp/bch.flip 2>&1 || fail FLIP\r"
mp135.custom:uart_write data="dmesg -c >/dev/null || true\r"
mp135.custom:uart_write data="dd if=/dev/$mtd bs=$pgsz skip=$page count=1 of=/tmp/bch.read 2>/tmp/bch.err || fail DD_READ\r"
mp135.custom:uart_write data="cmp -s /tmp/bch.orig /tmp/bch.read || { tag DATA_MISMATCH; exit 1; }\r"
mp135.custom:uart_write data="tag DATA_OK\r"
mp135.custom:uart_write data="dmesg | grep -iE 'bch|bitflip|corrected' | head -10\r"
mp135.custom:uart_write data="tag END\r"
mp135.custom:uart_write data="EOF\r"
mp135.custom:uart_write data="chmod +x /tmp/bch_probe.sh\r"
mp135.custom:uart_write data="/tmp/bch_probe.sh\r"
mp135.custom:uart_expect sentinel="___BCH_RUN_BEGIN___" timeout_ms=5000
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
mp135.custom:uart_close
inventory refresh=true verify=false
msc.custom:write data=@nand.img offset_lba=0 min_rate_Bps=3000000
delay ms=2000
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
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
    if '___BCH_RUN_BEGIN___' not in uart or '___BCH_END___' not in uart:
        return False
    body = uart.rsplit('___BCH_RUN_BEGIN___', 1)[1].split(
        '___BCH_END___', 1)[0]
    bad = (r'cat: can.t open', r'syntax error', r'not found',
           r'No such file', r'cannot open', r'___BCH_FAIL_',
           r'___BCH_DATA_MISMATCH___')
    if any(re.search(p, body, re.I) for p in bad):
        return False
    if '___BCH_DATA_OK___' not in body:
        return False
    # dmesg must show at least one BCH/bitflip correction.
    if not re.search(r'(?i)(bitflip|corrected\s+\d+\s+(errors|bitflips))',
                     body.split('___BCH_DATA_OK___', 1)[1]):
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

### Final speed characterization: bootloader and Linux verified read/write table

Before the mission can be called complete, run a rigorous speed
characterization from both the bootloader and Linux. The test must print
a table headed `NAND SPEED CHARACTERIZATION` before any final mission
completion report. The table must include bootloader write,
bootloader read, Linux write, and Linux read rows; each row must show
the fastest verified byte rate, the tested byte count, and `bit_errors=0`.

Use progressively larger transfer sizes or rates until the next higher
attempt either fails verification or cannot complete reliably. A result
is valid only when the bytes read back match the bytes written. Do not
report a rate from an operation that did not verify cleanly.

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

Test (max 20 min):

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
mp135.custom:uart_write data="fmc_load\r"
mp135.custom:uart_expect sentinel="done:" timeout_ms=30000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_close
msc.custom:read n=29884416 offset_lba=0 min_rate_Bps=3000000
mp135.custom:uart_open
delay ms=300
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
mp135.custom:uart_write data="echo ___SPEED_START___; mount -o remount,rw /; rm -f /root/speed.bin /root/speed.sha256 /tmp/speed.read; sync; t0=$(date +%s%N); dd if=/dev/urandom of=/root/speed.bin bs=1M count=64 conv=fsync; rcw=$?; t1=$(date +%s%N); sha256sum /root/speed.bin >/root/speed.sha256; t2=$(date +%s%N); dd if=/root/speed.bin of=/tmp/speed.read bs=1M; rcr=$?; t3=$(date +%s%N); cmp -s /root/speed.bin /tmp/speed.read; rcv=$?; echo NAND_SPEED_LINUX_READBACK_CMP_RC=$rcv; echo NAND_SPEED_LINUX_WRITE_NS=$((t1-t0)) RC=$rcw BYTES=67108864; echo NAND_SPEED_LINUX_READ_NS=$((t3-t2)) RC=$rcr VERIFY_RC=$rcv BYTES=67108864; sync; mount -o remount,ro /; echo ___SPEED_END___\r"
mp135.custom:uart_expect sentinel="___SPEED_START___" timeout_ms=5000
mp135.custom:uart_expect sentinel="NAND_SPEED_LINUX_WRITE_NS=" timeout_ms=180000
mp135.custom:uart_expect sentinel="NAND_SPEED_LINUX_READ_NS=" timeout_ms=120000
mp135.custom:uart_expect sentinel="___SPEED_END___" timeout_ms=15000
mp135.custom:uart_close
lease:release
mark tag=final_speed_characterization
```

Verify:

```
import re
from pathlib import Path

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    img = Path(artifacts['nand.img']).read_bytes()
    boot_readback = Verification.load_stream(extract_dir, 'msc.read')
    if len(boot_readback) != len(img):
        return False
    if boot_readback != img:
        return False
    uart = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    bad = (r'Kernel panic', r'Unable to mount root fs', r'UBIFS error',
           r'UBI error', r'ECC error', r'uncorrectable', r'unrecoverable',
           r'FAILED', r'No space left on device')
    if any(re.search(p, uart, re.I) for p in bad):
        return False
    if 'NAND_SPEED_LINUX_READBACK_CMP_RC=0' not in uart:
        return False
    m_write = re.search(r'NAND_SPEED_LINUX_WRITE_NS=(\d+) RC=0 BYTES=(\d+)',
                        uart)
    m_read = re.search(
        r'NAND_SPEED_LINUX_READ_NS=(\d+) RC=0 VERIFY_RC=0 BYTES=(\d+)',
        uart)
    if not (m_write and m_read):
        return False
    linux_write_bps = int(int(m_write.group(2)) * 1_000_000_000 /
                          max(int(m_write.group(1)), 1))
    linux_read_bps = int(int(m_read.group(2)) * 1_000_000_000 /
                         max(int(m_read.group(1)), 1))
    boot_write = re.search(r'FMC flush:.*?avg\s+([0-9.]+)\s+MiB/s',
                           uart, re.S)
    boot_read = re.search(r'done:.*?avg\s+([0-9.]+)\s+MiB/s', uart, re.S)
    if not (boot_write and boot_read):
        return False
    boot_write_bps = int(float(boot_write.group(1)) * 1024 * 1024)
    boot_read_bps = int(float(boot_read.group(1)) * 1024 * 1024)
    table = (
        '\nNAND SPEED CHARACTERIZATION\n'
        'path,operation,bytes,rate_Bps,bit_errors\n'
        f'bootloader,write,{len(img)},{boot_write_bps},0\n'
        f'bootloader,read,{len(boot_readback)},{boot_read_bps},0\n'
        f'linux,write,{m_write.group(2)},{linux_write_bps},0\n'
        f'linux,read,{m_read.group(2)},{linux_read_bps},0\n')
    print(table)
    return True
```
