# Remote provisioning checks for the STM32MP135 EVB

Drive an STM32MP135 board through the remote-provisioning chain
`test_serv` exposes: DFU-load the bootloader, interrupt autoload,
write+verify an SD image via MSC, boot Linux via UART, reach it over
SSH. Plans escalate from a poller-alive probe to a full reset -> flash
-> boot -> SSH round trip.

### Inventory smoke

Done: 05/12/2026 16:37:43

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
    needed = {'mp135.evb', 'bench_mcu.0', 'ssh.evb', 'lease._default'}
    devs = Verification.load_devices(extract_dir)
    return needed.issubset({d['id'] for d in devs})
```

### Bootloader hold via DFU + UART

Done: 05/12/2026 16:37:51

DFU + UART end-to-end with autoload-stop. Resets, DFU-loads the
bootloader, opens UART, sends three blind `x` bytes during the
dot-only autoload countdown (~5 s window), waits for `> `, kicks `\r`
to reconfirm the prompt, closes UART. Leaves the board parked at the
bootloader so the next section can use MSC immediately.

Build (EVB must be explicit because the bootloader object files do not
track `CFLAGS_EXTRA`; always clean before switching board variants):

```
make -C stm32mp135_test_board/bootloader clean
make -C stm32mp135_test_board/bootloader -j$(nproc) CFLAGS_EXTRA=-DEVB
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
```

Test (max 30 s):

```
lease:claim devices="bench_mcu.0" duration_s=10
bench_mcu:reset_dut
lease:release
delay ms=2000
lease:claim devices="mp135.evb,ssh.evb" duration_s=3600
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
    uart = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    return (Verification.op_succeeded(ops, 'dfu.evb', 'flash_layout') and
            Verification.op_succeeded(ops, 'mp135.evb', 'uart_expect') and
            'Board EVB' in uart and 'Board custom' not in uart)
```

### MSC enumeration smoke

Done: 05/12/2026 16:38:46

Inherits the bootloader-at-`> ` state from the previous test---no reset,
no DFU, no autoload-stop preamble. Refreshes inventory so `msc.evb`
shows up after the bootloader exposed the MSC interface, then reads 1
MiB from the card. Read-only. The later write/verify/readback sections
prove the actual SD image content.

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
    return len(data) == 1048576
```

### SD image write

Done: 05/13/2026 11:37:54

Confirms the build instructions actually produce a usable SD image.
Builds a fresh `sdcard.img` and writes it to the card via MSC. The next
sections verify and read it back separately so slow/failing media ops
are isolated.

Build (apply `config/patch.linux` if not already in the tree ---
without it the kernel boots silently and never reaches userspace ---
rebuild the kernel, refresh the DTB for the EVB DTS, and assemble a
fresh SD image using the EVB bootloader already built by the first
section; skips `make br` --- the Buildroot rootfs is reused from prior
builds. On a fresh clone you'd add `make br` ahead of `make sd`):

Build:

```
make -C stm32mp135_test_board patch
make -C stm32mp135_test_board kernel
make -C stm32mp135_test_board DTS=stm32mp135f-dk dtb
make -C stm32mp135_test_board DTS=stm32mp135f-dk sd
```

Artifacts:

```
stm32mp135_test_board/buildroot/output/images/sdcard.img
```

Test (inherits the bootloader-at-`> ` state from the previous test ---
no reset/DFU/autoload-stop preamble):

Test (max 30 s):

```
lease:resume token="{{LEASE_TOKEN}}"
msc.evb:write data=@sdcard.img offset_lba=0 min_rate_Bps=3000000
mark tag=sd_write
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    return Verification.op_succeeded(ops, 'msc.evb', 'write')
```

### SD image verify

Has the bench compare the card contents against the generated SD image.

Build: nothing required.

Artifacts:

```
stm32mp135_test_board/buildroot/output/images/sdcard.img
```

Test (inherits the written SD image from the previous section):

Test (max 30 s):

```
lease:resume token="{{LEASE_TOKEN}}"
msc.evb:verify data=@sdcard.img offset_lba=0 min_rate_Bps=3000000
mark tag=sd_verify
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    return Verification.op_succeeded(ops, 'msc.evb', 'verify')
```

### SD image readback

Reads back the leading bytes and diffs the captured stream against the
source file offline. The next test (Boot Linux from SD) then boots
whatever these sections left on the card.

Build: nothing required.

Artifacts:

```
stm32mp135_test_board/buildroot/output/images/sdcard.img
```

Test (inherits the written SD image from the previous sections):

Test (max 30 s):

```
lease:resume token="{{LEASE_TOKEN}}"
msc.evb:read n=41943040 offset_lba=0 min_rate_Bps=3000000
mark tag=sd_readback
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

Done: 05/13/2026 11:38:00

Fast (~30 s total) check that the EVB DFU-loaded bootloader can `two`
+ `jump` into Linux from the SD already on the card and reach the
userspace `login:` prompt. Skips MSC entirely --- the only timing
that matters is bootloader startup + SD load + kernel boot + init.
Linux boot itself is ~10-20 s, so the late expects are tight; if the
SD is unprovisioned or unbootable this fails fast and the slower
end-to-end below will do the writing.

Build: nothing required.

Test (inherits the bootloader-at-`> ` state from the previous test ---
no reset/DFU/autoload-stop, just open UART, kick the prompt, `two`,
`jump`. The bootloader binary is already running on the DUT; this
section only speaks UART, so neither `flash.tsv` nor `main.stm32`
needs to be (re)built here):

Test (max 1 min):

```
lease:resume token="{{LEASE_TOKEN}}"
mp135.evb:uart_open
delay ms=300
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="> " timeout_ms=5000
mp135.evb:uart_write data="t"
delay ms=100
mp135.evb:uart_write data="w"
delay ms=100
mp135.evb:uart_write data="o"
delay ms=100
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="Copying 1 blocks" timeout_ms=15000
mp135.evb:uart_expect sentinel="DDR addr 0xC4000000" timeout_ms=15000
mp135.evb:uart_expect sentinel="> " timeout_ms=5000
mp135.evb:uart_write data="j"
delay ms=100
mp135.evb:uart_write data="u"
delay ms=100
mp135.evb:uart_write data="m"
delay ms=100
mp135.evb:uart_write data="p"
delay ms=100
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

Done: 05/13/2026 11:38:05

Inherits the running Linux from the previous test --- no DFU, no MSC,
no boot. Waits a few seconds for DHCP, derives the dropbear host key
from the buildroot target tree at Build time, registers it via a
side plan, and runs `ssh:exec` for IP + uname. Quick check that the
bench SSH path reaches the live system. Key rotations don't require
editing this mission.

Build:

```
python3 -c "import base64,os,struct; d=open('stm32mp135_test_board/buildroot/output/target/etc/dropbear/dropbear_ed25519_host_key.bin','rb').read(); i=0; n=struct.unpack('>I',d[i:i+4])[0]; i+=4; assert d[i:i+n]==b'ssh-ed25519','unexpected key type'; i+=n; n=struct.unpack('>I',d[i:i+4])[0]; i+=4; pub=d[i:i+n][-32:]; wire=struct.pack('>I',11)+b'ssh-ed25519'+struct.pack('>I',32)+pub; line='ssh-ed25519 '+base64.b64encode(wire).decode()+' root@buildroot'; open('stm32mp135_test_board/buildroot/output/images/hostkey.pub','w').write(line+chr(10)); tok=os.environ['RUNPY_LEASE_TOKEN']; open(os.environ['RUNPY_WORKDIR']+'/refresh_known_hosts.plan','w').write('description \"refresh ssh.evb known_hosts\"'+chr(10)+'lease:resume token=\"'+tok+'\"'+chr(10)+'ssh.evb:trust_host_key key=\"'+line+'\"'+chr(10))"
python3 test_serv/submit.py --server http://localhost:8080 --wait 20 "$RUNPY_WORKDIR/refresh_known_hosts.plan"
```

Test (max 1 min):

```
lease:resume token="{{LEASE_TOKEN}}"
delay ms=8000
ssh.evb:exec command="ip -4 -o addr show dev eth0; uname -a"
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
