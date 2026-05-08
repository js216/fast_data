### Inventory lists required streaming devices

Confirm the bench inventory exposes the device IDs needed to begin the
WebSocket streaming mission: STM32MP135 UART, root SSH target,
WebSocket receiver, and default lease control. This is a device
discovery check only; it must not boot, flash, or modify the board, and
it does not yet validate operation metadata.

Build: nothing required.

Test (max 30 s):

```
inventory
mark tag=stream_ws_devices
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    devices = Verification.load_devices(extract_dir)
    device_ids = {d["id"] for d in devices}
    needed_devices = {"mp135.evb", "ssh.target", "ws.any", "lease._default"}
    return needed_devices.issubset(device_ids)
```

# Fast data streaming over WebSockets

Build and validate a minimal STM32MP135 Linux-side WebSocket streaming
path. The target must stream deterministic PRBS bytes, and the host-side
test must prove byte-perfect integrity and report transfer rate.

Live inventory on 2026-05-07 showed that `test_serv` exposes `ssh:put`
for blob upload using scp, `ssh:exec` for target commands, and `ws:recv`
for WebSocket receive/checksum/rate tests. These are the infrastructure
pieces needed once a Worker has compiled and booted a Linux image with
networking and SSH enabled; `ssh.target` is not expected to answer before
that image is running.

### Inventory exposes WebSocket mission control surface

Confirm the bench exposes the device and operation surface needed to
start the mission: STM32MP135 UART, root SSH command execution, scp-style
blob upload, WebSocket receive verification, lease control, and inventory
operation metadata. This is a capability check only; it must not boot,
flash, or modify the board.

Build: nothing required.

Test (max 30 s):

```
inventory
mark tag=stream_ws_inventory
```

Verify:

```
def check(extract_dir):
    import json
    from pathlib import Path

    if not Verification.manifest_clean(extract_dir):
        return False

    devices = Verification.load_devices(extract_dir)
    device_ids = {d["id"] for d in devices}
    needed_devices = {"mp135.evb", "ssh.target", "ws.any", "lease._default"}
    if not needed_devices.issubset(device_ids):
        return False

    ops = json.loads(Path(extract_dir, "bench.ops.json").read_text())
    required_ops = {
        "ssh": {"exec", "put", "pubkey", "trust_host_key"},
        "ws": {"recv"},
        "mp135": {"uart_open", "uart_write", "uart_expect", "uart_close"},
        "lease": {"claim", "resume", "release", "list"},
    }
    for plugin, names in required_ops.items():
        available = set(ops.get(plugin, {}).get("ops", {}))
        if not names.issubset(available):
            return False

    return True
```

### SSH target advertises a concrete target address

Confirm `ssh.target` exposes the configured STM32MP135 Linux target
address in inventory metadata before attempting any network operation.
This is a discovery check only; it must not boot, flash, connect to, or
modify the board.

Build: nothing required.

Test (max 30 s):

```
inventory
mark tag=stream_ws_ssh_address
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False

    devices = Verification.load_devices(extract_dir)
    ssh_targets = [d for d in devices if d["id"] == "ssh.target"]
    if len(ssh_targets) != 1:
        return False

    target = ssh_targets[0]
    if target.get("plugin") != "ssh":
        return False

    spec = target.get("spec")
    if not isinstance(spec, dict):
        return False

    ip = spec.get("ip")
    return isinstance(ip, str) and bool(ip.strip())
```

### Keep Linux boot arguments in board DTS

Remove the forced kernel command line from the STM32MP135 Linux config
and keep the SD-card root and clock workaround in the board device tree
`/chosen/bootargs`. This preserves the current boot fix without
hardcoding DTS-expressible board policy into the kernel image.

Build:

```
make -C stm32mp135_test_board kernel
make -C stm32mp135_test_board DTS=stm32mp135f-dk dtb
```

Artifacts:

```
stm32mp135_test_board/config/linux.conf
stm32mp135_test_board/config/stm32mp135f-dk.dts
stm32mp135_test_board/linux/.config
stm32mp135_test_board/linux/arch/arm/boot/dts/stm32mp135f-dk.dtb
```

Test: no hardware.

Verify:

```
def check(extract_dir):
    from pathlib import Path

    linux_conf = Path("stm32mp135_test_board/config/linux.conf").read_text()
    if 'CONFIG_CMDLINE="root=/dev/mmcblk0p3 clk_ignore_unused"' in linux_conf:
        return False
    if "CONFIG_CMDLINE_FORCE=y" in linux_conf:
        return False

    board_dts = Path("stm32mp135_test_board/config/stm32mp135f-dk.dts").read_text()
    return 'bootargs = "root=/dev/mmcblk0p3 clk_ignore_unused";' in board_dts
```

### Provision SD image with SSH keys

Build the STM32MP135 EVB Linux SD image from the tracked Buildroot
overlay, then write and verify it on the board's SD card through the
bootloader MSC interface. This ensures the later SSH reachability probe
boots an image that contains the bench public key in
`/root/.ssh/authorized_keys`, the deterministic Dropbear host key, and
the network/dropbear startup configuration needed for key-only root SSH.
The kernel image must not force a built-in command line; boot arguments
remain in the selected DTS `/chosen/bootargs`.

Build:

```
make -C stm32mp135_test_board br
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
stm32mp135_test_board/linux/arch/arm/boot/dts/stm32mp135f-dk.dtb
stm32mp135_test_board/buildroot/output/images/sdcard.img
```

Test (max 15 min):

```
lease:claim devices="bench_mcu.0,mp135.evb,ssh.target" duration_s=900 auto_release_on_session_end=true
bench_mcu:reset_dut
delay ms=2000
inventory refresh=true verify=false
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
lease:release
mark tag=stream_ws_provision_sd
```

Verify:

```
def check(extract_dir):
    from pathlib import Path
    import subprocess
    import tempfile

    if not Verification.manifest_clean(extract_dir):
        return False
    kernel_config = Path("stm32mp135_test_board/config/linux.conf").read_text()
    if 'CONFIG_CMDLINE="root=' in kernel_config:
        return False
    if "CONFIG_CMDLINE_FORCE=y" in kernel_config:
        return False
    sd_image = Path(artifacts["sdcard.img"])
    with sd_image.open("rb") as f:
        f.seek(446 + 16)
        dtb_entry = f.read(16)
        dtb_lba = int.from_bytes(dtb_entry[8:12], "little")
        dtb_sectors = int.from_bytes(dtb_entry[12:16], "little")
        if not dtb_lba or not dtb_sectors:
            return False
        f.seek(dtb_lba * 512)
        dtb_blob = f.read(dtb_sectors * 512)
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(dtb_blob)
        tmp.flush()
        bootargs = subprocess.check_output(
            ["fdtget", tmp.name, "/chosen", "bootargs"],
            text=True).strip()
    if bootargs != "root=/dev/mmcblk0p3 clk_ignore_unused":
        return False
    ops = Verification.load_ops(extract_dir)
    return (Verification.op_succeeded(ops, "msc.evb", "write") and
            Verification.op_succeeded(ops, "msc.evb", "verify"))
```

### Boot Linux for SSH reachability

Reset the EVB, DFU-load the bootloader, interrupt autoload, and boot the
provisioned SD-card Linux image far enough to reach the `login:` prompt.
This establishes the live target state required before any `ssh.target`
operation; it does not rewrite the SD card.

Build:

```
make -C stm32mp135_test_board/bootloader -j$(nproc)
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
```

Test (max 4 min):

```
lease:claim devices="bench_mcu.0,mp135.evb,ssh.target" duration_s=600
bench_mcu:reset_dut
delay ms=2000
inventory refresh=true verify=false
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
mp135.evb:uart_write data="two\r"
mp135.evb:uart_expect sentinel="> " timeout_ms=15000
mp135.evb:uart_write data="jump"
delay ms=200
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="Jumping to address" timeout_ms=5000
mp135.evb:uart_expect sentinel="Linux version" timeout_ms=10000
mp135.evb:uart_expect sentinel="login:" timeout_ms=60000
mp135.evb:uart_close
mark tag=stream_ws_boot_linux
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream_text(
        extract_dir, "mp135.uart", encoding="utf-8")
    return "login:" in uart and "STM32MP135" in uart
```

### SSH exec reaches the live target

Confirm `ssh.target` can execute one command on the running STM32MP135
Linux image. This is a reachability probe only; it must not upload
files, start services, or modify the target filesystem. It resumes the
lease from the boot step so the SSH command runs against the board state
that just reached Linux.

Build: nothing required.

Test (max 2 min):

```
lease:resume token="{{LEASE_TOKEN}}"
delay ms=60000
ssh.target:trust_host_key key="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOxB/ZYPInH4jKwBq8tciowGWEl7NNVhXriVp4ylIxRu stm32mp135-evb-recovery"
ssh.target:exec command="printf %s stream_ws_ssh_reachable"
lease:release token="{{LEASE_TOKEN}}"
mark tag=stream_ws_ssh_exec
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False

    try:
        out = Verification.load_stream_text(
            extract_dir, "ssh.exec", encoding="utf-8")
    except FileNotFoundError:
        return False

    return "stream_ws_ssh_reachable" in out.splitlines()
```

### SSH plugin exposes local put operation

Add local `ssh:put` support to the test server SSH plugin before any
hardware mission section depends on it. This step is limited to the
host-side operation surface: it must expose a `put` op that accepts a
plan artifact as `data`, copies it to a target `path` with key-only scp,
and preserves the existing SSH host-key and cancellation behavior.

Build:

```
python3 -m py_compile test_serv/plugins/ssh.py
```

Artifacts:

```
test_serv/plugins/ssh.py
```

Test: no hardware.

Verify:

```
def check(extract_dir):
    import ast
    from pathlib import Path

    path = Path("test_serv/plugins/ssh.py")
    text = path.read_text()
    tree = ast.parse(text)

    functions = {
        node.name for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
    }
    if "_op_put" not in functions:
        return False

    ops = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "ops":
                    if isinstance(node.value, ast.Dict):
                        for key in node.value.keys:
                            if isinstance(key, ast.Constant):
                                ops.append(key.value)

    if "put" not in ops:
        return False

    required = [
        '"put": Op(',
        'args={"data": "blob", "path": "str"',
        "scp",
        "StrictHostKeyChecking=yes",
        "ssh.put",
    ]
    return all(item in text for item in required)
```

### SSH put uploads one blob to the live target

Prove the host-side `ssh:put` operation works against the STM32MP135
Linux image left running by the earlier boot and SSH reachability
sections. Upload one existing mission artifact to `/tmp`, verify the
target-side bytes by SHA-256 through `ssh:exec`, then remove the file.
This does not boot, flash, start a service, or modify persistent target
storage.

Build: nothing required.

Artifacts:

```
missions/stream-websockets.md
```

Test (max 3 min):

```
lease:claim devices="ssh.target" duration_s=180 auto_release_on_session_end=true
ssh.target:trust_host_key key="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOxB/ZYPInH4jKwBq8tciowGWEl7NNVhXriVp4ylIxRu stm32mp135-evb-recovery"
ssh.target:put data=@stream-websockets.md path=/tmp/stream_ws_put_probe.md timeout_ms=60000
ssh.target:exec command="sha256sum /tmp/stream_ws_put_probe.md; rm -f /tmp/stream_ws_put_probe.md"
lease:release
mark tag=stream_ws_ssh_put_blob
```

Verify:

```
def check(extract_dir):
    from pathlib import Path
    import hashlib

    if not Verification.manifest_clean(extract_dir):
        return False

    ops = Verification.load_ops(extract_dir)
    if not Verification.op_succeeded(ops, "ssh.target", "put"):
        return False
    if not Verification.op_succeeded(ops, "ssh.target", "exec"):
        return False

    expected = hashlib.sha256(
        Path(artifacts["stream-websockets.md"]).read_bytes()).hexdigest()
    out = Verification.load_stream_text(
        extract_dir, "ssh.exec", encoding="utf-8")
    return expected in out
```

## WIP

## Planned Mission Arc

1. Confirm `ssh.target` reaches the booted STM32MP135 Linux image and
   records the configured target IP from inventory or SSH output.
2. Prove `ssh:put` uploads a small blob to `/tmp` on `ssh.target`,
   verify it with `ssh:exec`, and remove it.
3. Upload or build the smallest target-side service, run it under
   `ssh:exec`, then prove the host can connect to it.
4. Replace the trivial service with a minimal WebSocket endpoint that
   sends a fixed short byte string, then verify it with `ws:recv`.
5. Stream a deterministic xorshift32 PRBS payload over WebSocket and
   verify SHA-256 or CRC32 with `ws:recv`, using the same generator
   semantics as `test_serv/plugins/_prbs.py`.
6. Add a throughput measurement for a larger WebSocket PRBS transfer and require
   the mission artefact to report bytes transferred, elapsed time, and
   bytes per second.
7. Clean up target-side temporary files and background server processes
   after each test section so reruns are idempotent.
