# NAND-flash boot for the STM32MP135 custom board

Drive the custom PCB through reset -> DFU bootloader -> write
`nand.img` to NAND -> boot Linux from NAND -> SSH.

Bootloader is built with `-DNAND_FLASH` (swaps `two`/`load_sd` for
`fmc_*`; autoboot calls `fmc_bload`). Two DTS files differ only in
`chosen/bootargs`: `config/custom.dts` keeps `root=/dev/mmcblk0p3`,
`config/custom-nand.dts` carries `ubi.mtd=rootfs root=ubi0:rootfs
rootfstype=ubifs ...`. Provisioning: `nand.img` -> DDR via
`msc.custom:write` -> `fmc_flush` over UART -> NAND.

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
    needed = {'mp135.custom', 'bench_mcu.0', 'ssh.target',
              'lease._default'}
    devs = Verification.load_devices(extract_dir)
    return needed.issubset({d['id'] for d in devs})
```

## WIP

### Bootloader hold via DFU + UART

Reset (D12 via `reset_dut2`), DFU-load NAND bootloader, stop autoload,
park at `> `.

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
lease:claim devices="bench_mcu.0,mp135.custom,ssh.target" duration_s=3600
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
mark tag=bootloader_hold
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    return (Verification.op_succeeded(ops, 'dfu.custom', 'flash_layout') and
            Verification.op_succeeded(ops, 'mp135.custom', 'uart_expect'))
```

### MSC + NAND probe smoke

Inherits the bootloader-at-`> ` state. Refresh inventory so
`msc.custom` shows up, read 1 MiB from the DDR window, and run
`fmc_test_boot` to confirm the FMC controller is initialised.

Build: nothing required.

Test (max 30 s):

```
lease:resume token="{{LEASE_TOKEN}}"
inventory
msc.custom:read n=1048576 offset_lba=0
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_write data="fmc_test_boot\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_close
mark tag=msc_nand_smoke
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

### NAND image round-trip: write -> fmc_flush -> fmc_load -> diff

Write `nand.img` to DDR via MSC, `fmc_flush` to NAND, `fmc_load` back
into DDR, MSC-read and offline-diff the leading bytes.

Build:

```
make -C stm32mp135_test_board patch
make -C stm32mp135_test_board/bootloader -j$(nproc) CFLAGS_EXTRA=-DNAND_FLASH
make -C stm32mp135_test_board kernel
make -C stm32mp135_test_board DTS=custom-nand dtb
make -C stm32mp135_test_board DTS=custom-nand nand
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/nand.img
```

Test (max 15 min):

```
lease:resume token="{{LEASE_TOKEN}}"
msc.custom:write data=@nand.img offset_lba=0
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_write data="fmc_flush\r"
mp135.custom:uart_expect sentinel="done" timeout_ms=600000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_write data="fmc_load\r"
mp135.custom:uart_expect sentinel="done" timeout_ms=300000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_close
msc.custom:read n=4194304 offset_lba=0
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
DTB header in NAND). No Linux, no SSH. Cheap gate before `fmc_bload`.

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
    if total == 0 or bad > total // 200:   # <0.5% bad blocks
        return False
    if 'checksum MISMATCH' in uart or 'bad magic' in uart:
        return False
    if 'checksum OK' not in uart or 'FDT magic OK' not in uart:
        return False
    return True
```

### NAND + UBI health (Linux-side via UART)

Inherits the running Linux from the previous test, but talks to it
over the serial console rather than SSH. Logs in as `root`/`root`,
prints `/proc/mtd`, `ubinfo -a`, `mtdinfo -a`, and a filtered
`dmesg`. Asserts the expected partitions are present, UBI reports
zero corrupted PEBs, and `dmesg` is clear of UBI/UBIFS/ECC errors.
Requires `BR2_PACKAGE_MTD=y` in `config/buildroot.conf` for the
mtd-utils binaries.

Build: nothing required.

Test (max 1 min):

```
lease:resume token="{{LEASE_TOKEN}}"
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="login:" timeout_ms=5000
mp135.custom:uart_write data="root\r"
mp135.custom:uart_expect sentinel="Password:" timeout_ms=3000
mp135.custom:uart_write data="root\r"
mp135.custom:uart_expect sentinel="# " timeout_ms=5000
mp135.custom:uart_write data="echo ___MTD___; cat /proc/mtd; echo ___UBI___; ubinfo -a; echo ___MTDI___; mtdinfo -a; echo ___DMESG___; dmesg | grep -iE 'ubi|ubifs|nand|fmc|bch|ecc' | tail -50; echo ___END___\r"
mp135.custom:uart_expect sentinel="___END___" timeout_ms=15000
mp135.custom:uart_expect sentinel="# " timeout_ms=3000
mp135.custom:uart_close
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
    corr = re.search(r'Corrupted PEBs:\s+(\d+)', body)
    if not corr or int(corr.group(1)) != 0:
        return False
    bad = re.search(r'Bad PEB count:\s+(\d+)', body)
    if not bad or int(bad.group(1)) > 4:
        return False
    if re.search(r'UBIFS error|UBI error|ECC unrecoverable|uncorrectable',
                 body, re.I):
        return False
    return True
```

### SSH smoke (no reload)

Build: nothing required.

Test (max 1 min):

```
lease:resume token="{{LEASE_TOKEN}}"
delay ms=8000
ssh:trust_host_key key="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIq2/Qf4lNrw/weZ9Aod1VTCvett2F/iNjzDBuA/gKe/ stm32mp135-evb-recovery"
ssh:exec command="ip -4 -o addr show dev eth0; uname -a; mount | grep ' / '"
lease:release token="{{LEASE_TOKEN}}"
mark tag=ssh_smoke_nand
```

Verify (rootfs must be `ubifs`, proving the kernel really came from
NAND):

```
import re

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    out = Verification.load_stream(
        extract_dir, 'ssh.exec').decode('utf-8', 'replace')
    return (bool(re.search(r'eth0\s+inet \d+\.\d+\.\d+\.\d+/\d+', out))
            and 'Linux' in out and 'armv7l' in out
            and 'ubifs' in out)
```

### Full end-to-end: DFU -> NAND write+commit -> boot Linux -> SSH IP

Cold path. Reset, DFU NAND bootloader, stop autoload, write+commit
`nand.img`, `fmc_bload` + `jump`, SSH.

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

Test (max 20 min):

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
msc.custom:write data=@nand.img offset_lba=0
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_write data="fmc_flush\r"
mp135.custom:uart_expect sentinel="done" timeout_ms=600000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_write data="fmc_bload\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=30000
mp135.custom:uart_write data="jump"
delay ms=200
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="Jumping to address" timeout_ms=5000
mp135.custom:uart_expect sentinel="Linux version" timeout_ms=10000
mp135.custom:uart_expect sentinel="UBI: attached mtd" timeout_ms=20000
mp135.custom:uart_expect sentinel="login:" timeout_ms=30000
mp135.custom:uart_close
delay ms=8000
ssh:trust_host_key key="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIq2/Qf4lNrw/weZ9Aod1VTCvett2F/iNjzDBuA/gKe/ stm32mp135-evb-recovery"
ssh:exec command="ip -4 -o addr show dev eth0; uname -a; mount | grep ' / '"
mark tag=full_end_to_end_nand
```

Verify:

```
import re

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    out = Verification.load_stream(extract_dir, 'ssh.exec').decode('utf-8', 'replace')
    return (bool(re.search(r'eth0\s+inet \d+\.\d+\.\d+\.\d+/\d+', out))
            and 'Linux' in out and 'armv7l' in out and 'ubifs' in out)
```
