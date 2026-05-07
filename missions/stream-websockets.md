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
