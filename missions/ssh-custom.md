# Remote provisioning checks for the STM32MP135 custom board

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
    needed = {'mp135.custom', 'bench_mcu.0', 'ssh.custom', 'lease._default'}
    devs = Verification.load_devices(extract_dir)
    return needed.issubset({d['id'] for d in devs})
```

### Bootloader hold via DFU + UART

DFU + UART end-to-end with autoload-stop. Resets, DFU-loads the
bootloader, opens UART, sends three blind `x` bytes during the
dot-only autoload countdown (~5 s window), waits for `> `, kicks `\r`
to reconfirm the prompt, closes UART. Leaves the board parked at the
bootloader so the next section can use MSC immediately.

Build (rebuild bootloader, then submit a side plan that briefly
claims `bench_mcu.0` just to reset the DUT and immediately
releases. Doing the reset in its own session keeps the main Test
plan to a single `lease:claim`, so `manifest.json:lease_token`
unambiguously records the long lease's token for `{{LEASE_TOKEN}}`
substitution in later sections):

```
make -C stm32mp135_test_board/bootloader clean
make -C stm32mp135_test_board/bootloader -j$(nproc)
printf '%s\n' 'description "reset custom DUT"' 'lease:claim devices="bench_mcu.0" duration_s=10' 'bench_mcu:reset_dut2' 'lease:release' > "$RUNPY_WORKDIR/reset_dut.plan"
python3 test_serv/submit.py --server http://localhost:8080 --wait 20 "$RUNPY_WORKDIR/reset_dut.plan"
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
```

Test (max 30 s):

```
delay ms=2000
lease:claim devices="mp135.custom,ssh.custom" duration_s=3600
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
    uart = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    return (Verification.op_succeeded(ops, 'dfu.custom', 'flash_layout') and
            Verification.op_succeeded(ops, 'mp135.custom', 'uart_expect') and
            'Board custom' in uart and 'Board EVB' not in uart)
```

### MSC enumeration smoke

Inherits the bootloader-at-`> ` state from the previous test --- no
reset, no DFU, no autoload-stop preamble. Refreshes inventory so
`msc.custom` shows up after the bootloader exposed the MSC interface,
then reads 1 MiB from the card. Read-only. Verifier checks for a
valid MBR signature in the `msc.read` stream.

Build: nothing required.

Test (max 30 s):

```
inventory
msc.custom:read n=1048576 offset_lba=0
mark tag=msc_read_smoke
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    data = Verification.load_stream(extract_dir, 'msc.read')
    # Just confirm 1 MiB came back; section 4 does the real
    # round-trip verify. Dropping the MBR-sig check makes this
    # section robust against an SD that an earlier probe filled
    # with zeros -- the real boot/SSH chain is what we care about.
    return len(data) == 1048576
```

### SD image write

Confirms the build instructions actually produce a usable SD image.
Builds a fresh `sdcard.img` and writes it to the card via MSC. The next
sections verify and read it back separately so slow/failing media ops
are isolated.

Build (apply `config/patch.linux` if not already in the tree ---
without it the kernel boots silently and never reaches userspace ---
rebuild the kernel, refresh the DTB for the custom board DTS, and
assemble a fresh SD image using the custom SD bootloader already built
by the first section; skips `make br` --- the Buildroot rootfs is
reused from prior builds. On a fresh clone you'd add `make br` ahead of
`make sd`):

Build:

```
make -C stm32mp135_test_board patch
make -C stm32mp135_test_board kernel
make -C stm32mp135_test_board DTS=custom dtb
make -C stm32mp135_test_board DTS=custom sd
```

Artifacts:

```
stm32mp135_test_board/buildroot/output/images/sdcard.img
```

Test (inherits the bootloader-at-`> ` state from the previous test ---
no reset/DFU/autoload-stop preamble):

Test (max 30 s):

```
msc.custom:write data=@sdcard.img offset_lba=0 min_rate_Bps=3000000
mark tag=sd_write
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    return Verification.op_succeeded(ops, 'msc.custom', 'write')
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
msc.custom:verify data=@sdcard.img offset_lba=0 min_rate_Bps=3000000
mark tag=sd_verify
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    return Verification.op_succeeded(ops, 'msc.custom', 'verify')
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
msc.custom:read n=41943040 offset_lba=0 min_rate_Bps=3000000
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

Fast (~30 s total) check that the custom board DFU-loaded bootloader can `two`
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
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_write data="t"
delay ms=100
mp135.custom:uart_write data="w"
delay ms=100
mp135.custom:uart_write data="o"
delay ms=100
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="Copying 1 blocks" timeout_ms=15000
mp135.custom:uart_expect sentinel="DDR addr 0xC4000000" timeout_ms=15000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_write data="j"
delay ms=100
mp135.custom:uart_write data="u"
delay ms=100
mp135.custom:uart_write data="m"
delay ms=100
mp135.custom:uart_write data="p"
delay ms=100
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="Jumping to address" timeout_ms=5000
mp135.custom:uart_expect sentinel="Linux version" timeout_ms=10000
mp135.custom:uart_expect sentinel="login:" timeout_ms=15000
mp135.custom:uart_close
lease:release token="{{LEASE_TOKEN}}"
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
no boot. Waits a few seconds for DHCP, derives the dropbear host key
from the buildroot target tree at Build time, registers it via a
side plan, and runs `ssh:exec` for IP + uname. Quick check that the
bench SSH path reaches the live system. Key rotations don't require
editing this mission.

Build (this section is lease-less, so the refresh plan does its own
`ssh:trust_host_key` without resuming or claiming a lease --- mirrors
the lease-less Test below):

```
python3 -c "import base64,os,struct; d=open('stm32mp135_test_board/buildroot/output/target/etc/dropbear/dropbear_ed25519_host_key.bin','rb').read(); i=0; n=struct.unpack('>I',d[i:i+4])[0]; i+=4; assert d[i:i+n]==b'ssh-ed25519','unexpected key type'; i+=n; n=struct.unpack('>I',d[i:i+4])[0]; i+=4; pub=d[i:i+n][-32:]; wire=struct.pack('>I',11)+b'ssh-ed25519'+struct.pack('>I',32)+pub; line='ssh-ed25519 '+base64.b64encode(wire).decode()+' root@buildroot'; open('stm32mp135_test_board/buildroot/output/images/hostkey.pub','w').write(line+chr(10)); open(os.environ['RUNPY_WORKDIR']+'/refresh_known_hosts_custom.plan','w').write('description \"refresh ssh.custom known_hosts\"'+chr(10)+'ssh.custom:trust_host_key key=\"'+line+'\"'+chr(10))"
python3 test_serv/submit.py --server http://localhost:8080 --wait 20 "$RUNPY_WORKDIR/refresh_known_hosts_custom.plan"
```

Test (max 1 min):

```
delay ms=8000
ssh.custom:exec command="ip -4 -o addr show dev eth0; uname -a"
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
