# Remote provisioning checks for the STM32MP135 EVB

Drive an STM32MP135 board through the remote-provisioning chain
`test_serv` exposes: DFU-load the bootloader, interrupt autoload,
write+verify an SD image via MSC, boot Linux via UART, reach it over
SSH. Plans escalate from a poller-alive probe to a full reset -> flash
-> boot -> SSH round trip.

Sections that need device state to survive across submissions claim
a test_serv lease and pass the issued token to the next plan. The
mission file spells the lifecycle out: the first lease-using section
runs `lease:claim devices="..." duration_s=N`, every subsequent
section starts with `lease:resume token="{{LEASE_TOKEN}}"`, and the
last section before the flagship ends with `lease:release token=...`.
The runner (`run.py`) substitutes `{{LEASE_TOKEN}}` from the prior
section's `streams/lease.token.bin` and does no other lease plumbing.
The flagship runs lease-less on purpose -- it proves the cold path
(reset -> DFU -> write -> boot -> SSH) still works end-to-end without
inheriting any state.

## WIP

### Inventory smoke

Confirms the poller is up and every configured device probes and
verifies. Surfaces `bench.devices.json` (instance ids) and
`bench.ops.json` (op signatures) for later tests. No hardware touched
beyond the verify sweep.

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
    needed = {'mp135.evb', 'bench_mcu.0', 'ssh.target', 'lease._default'}
    devs = Verification.load_devices(extract_dir)
    return needed.issubset({d['id'] for d in devs})
```

### Bootloader hold via DFU + UART

DFU + UART end-to-end with autoload-stop. Resets, DFU-loads the
bootloader, opens UART, sends three blind `x` bytes during the
dot-only autoload countdown (~5 s window), waits for `> `, kicks `\r`
to reconfirm the prompt, closes UART. Leaves the board parked at the
bootloader so the next section can use MSC immediately.

Build:

```
make -C stm32mp135_test_board/bootloader -j$(nproc)
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
```

Test (max 30 s):

```
lease:claim devices="bench_mcu,dfu.evb,mp135.evb,ssh.target" duration_s=3600
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
mark tag=bootloader_hold
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    return (Verification.op_succeeded(ops, 'dfu.evb', 'flash_layout') and
            Verification.op_succeeded(ops, 'mp135.evb', 'uart_expect'))
```

### MSC enumeration smoke

Inherits the bootloader-at-`> ` state from the previous test --- no
reset, no DFU, no autoload-stop preamble. Refreshes inventory so
`msc.evb` shows up after the bootloader exposed the MSC interface,
then reads 1 MiB from the card. Read-only. Verifier checks for a
valid MBR signature in the `msc.read` stream.

Build: nothing required.

Test (max 30 s):

```
lease:resume token="{{LEASE_TOKEN}}"
inventory
msc.evb:read n=1048576 offset_lba=0
mark tag=msc_read_smoke
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    data = Verification.load_stream(extract_dir, 'msc.read')
    return len(data) == 1048576 and data[510:512] == b'\x55\xaa'
```

### SD image round-trip: write -> verify -> read -> diff

Confirms the build instructions actually produce a usable SD image.
Builds a fresh `sdcard.img`, writes it to the card via MSC, has the
bench bit-perfect-`verify` it, reads back the leading bytes, and the
verifier diffs the captured stream against the source file
**offline**. The next test (Boot Linux from SD) then boots whatever
this test left on the card.

Build (apply `config/patch.linux` if not already in the tree ---
without it the kernel boots silently and never reaches userspace ---
rebuild bootloader and kernel, refresh the DTB for the EVB DTS, and
assemble a fresh SD image; skips `make br` --- the Buildroot rootfs
is reused from prior builds. On a fresh clone you'd add `make br`
ahead of `make sd`):

Build:

```
make -C stm32mp135_test_board patch
make -C stm32mp135_test_board/bootloader -j$(nproc)
make -C stm32mp135_test_board kernel
make -C stm32mp135_test_board DTS=stm32mp135f-dk dtb
make -C stm32mp135_test_board DTS=stm32mp135f-dk sd
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/sdcard.img
```

Test (inherits the bootloader-at-`> ` state from the previous test ---
no reset/DFU/autoload-stop preamble):

Test (max 10 min):

```
lease:resume token="{{LEASE_TOKEN}}"
msc.evb:write data=@sdcard.img offset_lba=0
msc.evb:verify data=@sdcard.img offset_lba=0
msc.evb:read n=36700160 offset_lba=0
mark tag=sd_round_trip
```

Verify:

```
from pathlib import Path

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    img = Path(artifacts['sdcard.img']).read_bytes()
    got = Verification.load_stream(extract_dir, 'msc.read')
    return got[:len(img)] == img
```

### Boot Linux from SD

Fast (~30 s total) check that the EVB DFU-loaded bootloader can `two`
+ `jump` into Linux from the SD already on the card and reach the
userspace `login:` prompt. Skips MSC entirely --- the only timing
that matters is bootloader startup + SD load + kernel boot + init.
Linux boot itself is ~10-20 s, so the late expects are tight; if the
SD is unprovisioned or unbootable this fails fast and the slower
end-to-end below will do the writing.

Build:

```
make -C stm32mp135_test_board/bootloader -j$(nproc)
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
```

Test (inherits the bootloader-at-`> ` state from the previous test ---
no reset/DFU/autoload-stop, just open UART, kick the prompt, `two`,
`jump`):

Test (max 1 min):

```
lease:resume token="{{LEASE_TOKEN}}"
mp135.evb:uart_open
delay ms=300
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="> " timeout_ms=5000
mp135.evb:uart_write data="two\r"
mp135.evb:uart_expect sentinel="> " timeout_ms=15000
mp135.evb:uart_write data="jump"
delay ms=200
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="Jumping to address" timeout_ms=5000
mp135.evb:uart_expect sentinel="Linux version" timeout_ms=10000
mp135.evb:uart_expect sentinel="login:" timeout_ms=15000
mp135.evb:uart_close
mark tag=boot_linux
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    return 'login:' in uart and 'STM32MP135' in uart
```

### SSH smoke (no reload)

Inherits the running Linux from the previous test --- no DFU, no MSC,
no boot. Waits a few seconds for DHCP, registers the dropbear host
key, and runs `ssh:exec` for IP + uname. Quick check that the bench
SSH path reaches the live system.

Build: nothing required.

Test (max 1 min):

```
lease:resume token="{{LEASE_TOKEN}}"
delay ms=8000
ssh:trust_host_key key="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIq2/Qf4lNrw/weZ9Aod1VTCvett2F/iNjzDBuA/gKe/ stm32mp135-evb-recovery"
ssh:exec command="ip -4 -o addr show dev eth0; uname -a"
lease:release token="{{LEASE_TOKEN}}"
mark tag=ssh_smoke
```

Verify:

```
import re

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    out = Verification.load_stream(
        extract_dir, 'ssh.exec').decode('utf-8', 'replace')
    return (bool(re.search(r'eth0\s+inet \d+\.\d+\.\d+\.\d+/\d+', out))
            and 'Linux' in out and 'armv7l' in out)
```

### Full end-to-end: DFU -> write+verify golden -> boot Linux -> SSH IP

Flagship: exercises every link. Resets, DFU-loads the bootloader,
stops autoload, **writes and bit-perfect-verifies** the recovery SD
image via MSC, reopens UART for `two` (loads kernel+DTB from MBR)
then `jump`, waits for the kernel banner, board model, userspace
banner, and `login:`, then registers the host key and runs `ssh:exec`
for IP and uname.

Build:

```
make -C stm32mp135_test_board/bootloader -j$(nproc)
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/sdcard.img
```

The plan's `ssh-ed25519` key is the public half of
`config/overlay/etc/dropbear/dropbear_ed25519_host_key`; rebuild with
a different private key and `ssh:trust_host_key` must be regenerated.

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
msc.evb:write data=@sdcard.img offset_lba=0
msc.evb:verify data=@sdcard.img offset_lba=0
mp135.evb:uart_open
delay ms=300
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="> " timeout_ms=5000
mp135.evb:uart_write data="two\r"
mp135.evb:uart_expect sentinel="> " timeout_ms=15000
mp135.evb:uart_write data="jump"
delay ms=200
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="Jumping to address" timeout_ms=5000
mp135.evb:uart_expect sentinel="Linux version" timeout_ms=10000
mp135.evb:uart_expect sentinel="Welcome to STM32MP135 EVB" timeout_ms=10000
mp135.evb:uart_expect sentinel="login:" timeout_ms=15000
mp135.evb:uart_close
delay ms=8000
ssh:trust_host_key key="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIq2/Qf4lNrw/weZ9Aod1VTCvett2F/iNjzDBuA/gKe/ stm32mp135-evb-recovery"
ssh:exec command="ip -4 -o addr show dev eth0; uname -a; cat /etc/os-release | head -3"
mark tag=full_end_to_end
```

Verify:

```
import re

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    out = Verification.load_stream(extract_dir, 'ssh.exec').decode('utf-8', 'replace')
    has_ipv4 = bool(re.search(r'eth0\s+inet \d+\.\d+\.\d+\.\d+/\d+', out))
    has_uname = 'Linux' in out and 'armv7l' in out
    return has_ipv4 and has_uname
```
