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

### Inventory smoke

Done: 05/13/2026 15:09:43

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

Done: 05/13/2026 15:09:48

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

Done: 05/13/2026 15:09:52

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

Done: 05/13/2026 15:09:57

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

## WIP

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
