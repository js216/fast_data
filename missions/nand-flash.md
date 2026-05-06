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

## WIP

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
loop in missions/data/nand-root-loop/*.iter
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
           r'___ROOT_LOOP_PRECHECK_FAIL___', r'FAILED',
           r'No space left on device')
    return ('___ROOT_LOOP_DD_RC_0___' in uart
            and '/root/bigfile: OK' in uart
            and '___ROOT_LOOP_END___' in uart
            and not any(re.search(p, uart, re.I) for p in bad))
```
