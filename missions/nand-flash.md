# NAND-flash boot for the STM32MP135 custom board

Drive the custom PCB through reset -> DFU bootloader -> write
`nand.img` to NAND -> boot Linux from NAND -> SSH.

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

## WIP

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
lease:claim devices="mp135.custom,ssh.target" duration_s=3600 auto_release_on_session_end=true
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
mp135.custom:uart_expect sentinel="written" timeout_ms=30000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_write data="fmc_bload\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=30000
mp135.custom:uart_write data="jump"
delay ms=200
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="Linux version" timeout_ms=10000
mp135.custom:uart_expect sentinel="UBI: attached mtd" timeout_ms=20000
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
    return ('UBI: attached mtd' in uart and 'login:' in uart
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
    needed = {'mp135.custom', 'bench_mcu.0', 'ssh.target',
              'lease._default'}
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

Reset (D12 via `reset_dut2`) and DFU-load the NAND bootloader. Keep
the lease alive for the UART hold step.

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
lease:claim devices="mp135.custom,ssh.target" duration_s=3600
bench_mcu:reset_dut2
delay ms=2000
dfu.custom:flash_layout layout=@flash.tsv no_reconnect=true
mark tag=dfu_nand_flash
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    return Verification.op_succeeded(ops, 'dfu.custom', 'flash_layout')
```

### Bootloader hold via UART

Inherits the DFU-loaded NAND bootloader state, stops autoload, and
parks at `> `.

Build: nothing required.

Test (max 15 s):

```
lease:resume token="{{LEASE_TOKEN}}"
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
PRBS and verify the poison landed, so a no-op `fmc_load` cannot pass by
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
lease:claim devices="mp135.custom,ssh.target" duration_s=3600
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
mp135.custom:uart_expect sentinel="written" timeout_ms=10000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_close
msc.custom:write_prbs n=4194304 seed=3735928559 offset_lba=0 min_rate_Bps=3000000
msc.custom:verify_prbs n=4194304 seed=3735928559 offset_lba=0 min_rate_Bps=3000000
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
serial console rather than SSH. Logs in as `root`/`root`, prints
`/proc/mtd`, `ubinfo -a`, `mtdinfo -a`, and a filtered `dmesg`.
Asserts the expected partitions are present, UBI reports zero corrupted
PEBs, and `dmesg` is clear of UBI/UBIFS/ECC errors.
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
mp135.custom:uart_expect sentinel="> " timeout_ms=30000
mp135.custom:uart_write data="jump"
delay ms=200
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="Jumping to address" timeout_ms=5000
mp135.custom:uart_expect sentinel="Linux version" timeout_ms=10000
mp135.custom:uart_expect sentinel="UBI: attached mtd" timeout_ms=20000
mp135.custom:uart_expect sentinel="login:" timeout_ms=30000
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
`nand.img`, `fmc_bload` + `jump`, SSH. The 3 MB/s MSC write floor is a
hard requirement; lowering it hides a broken NAND boot path.

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
mp135.custom:uart_expect sentinel="written" timeout_ms=10000
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
