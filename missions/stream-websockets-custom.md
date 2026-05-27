# Fast Ethernet Data Streaming From STM32MP135 Custom Linux

Prove that the STM32MP135 custom board can boot Linux, start a
deterministic userspace WebSocket streamer, and move data over Ethernet
to a desktop at 90 Mbps or faster with byte-perfect integrity.

The pass condition is:

- the custom board is running the Linux image built by this tree,
- Ethernet is configured on the board,
- a target-side streamer sends deterministic PRBS bytes over WebSocket,
- the desktop receives the full payload,
- SHA-256 and CRC32 match the expected PRBS digest, and
- measured wall-time payload throughput is at least 90 Mbps.

### Inventory exposes required custom streaming control surface

Confirm the bench exposes the operation surface needed to boot the
custom board and drive its UART. This is a discovery check only; it
must not boot, flash, or modify the board.

Build: nothing required.

Test (max 30 s):

```
inventory
mark tag=stream_ws_custom_inventory
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
    needed_devices = {"bench_mcu.0", "mp135.custom", "ssh.custom"}
    if not needed_devices.issubset(device_ids):
        return False

    ops = json.loads(Path(extract_dir, "bench.ops.json").read_text())
    required_ops = {
        "mp135": {"uart_open", "uart_write", "uart_expect", "uart_close"},
        "dfu": {"flash_layout"},
        "msc": {"write", "verify"},
        "bench_mcu": {"reset_dut2"},
    }
    for plugin, names in required_ops.items():
        available = set(ops.get(plugin, {}).get("ops", {}))
        if not names.issubset(available):
            return False

    return True
```

### Build custom Linux image and WebSocket streamer

Build the custom-board SD image and a separate target-side WebSocket
PRBS streamer binary. The streamer is copied to the running board by
the hardware section; it is not baked into the Buildroot overlay. It
listens on TCP port 8765, performs the WebSocket opening handshake, and
sends xorshift32 PRBS bytes using the same seed and byte order as
`test_serv/plugins/_prbs.py`.

Build:

```
mkdir -p stm32mp135_test_board/build
stm32mp135_test_board/buildroot/output/host/bin/arm-buildroot-linux-uclibcgnueabihf-gcc -O2 -Wall -Wextra -o stm32mp135_test_board/build/stream_ws_prbs_stream stm32mp135_test_board/tools/stream_ws_prbs_stream.c
make -C stm32mp135_test_board br
make -C stm32mp135_test_board patch
make -C stm32mp135_test_board boot
make -C stm32mp135_test_board kernel
make -C stm32mp135_test_board DTS=custom dtb
make -C stm32mp135_test_board DTS=custom sd
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/sdcard.img
stm32mp135_test_board/tools/stream_ws_prbs_stream.c
stm32mp135_test_board/build/stream_ws_prbs_stream
```

Test: no hardware.

Verify:

```
def check(extract_dir):
    from pathlib import Path
    import subprocess

    src = Path("stm32mp135_test_board/tools/stream_ws_prbs_stream.c")
    if not src.exists():
        return False
    text = src.read_text()
    required = [
        "xorshift32",
        "Sec-WebSocket-Accept",
        "htons(",
        "bind(",
        "listen(",
        "accept(",
        "stream_ws_prbs",
    ]
    if not all(item in text for item in required):
        return False

    binary = Path("stm32mp135_test_board/build/stream_ws_prbs_stream")
    if not binary.exists() or binary.stat().st_size == 0:
        return False

    desc = subprocess.check_output(["file", str(binary)], text=True)
    return "ARM" in desc and "ELF" in desc
```

### Local WebSocket protocol self-test

Build a native host copy of the streamer and receive a 1 MiB PRBS
payload over loopback using the package-free receiver. This catches
WebSocket framing, PRBS byte-order, SHA-256, and CRC32 regressions
before using the bench.

Build: nothing required.

Local test:

```
mkdir -p logs/local-bin
gcc -O2 -Wall -Wextra -o logs/local-bin/stream_ws_prbs_stream stm32mp135_test_board/tools/stream_ws_prbs_stream.c
logs/local-bin/stream_ws_prbs_stream --port 18765 --bytes 1048576 --seed 0x12345678 --frame-bytes 131072 >logs/local-stream-1m.out 2>&1 & srv=$!; sleep 0.2; python3 logs/stream_ws_receive.py --host 127.0.0.1 --port 18765 --bytes 1048576 --min-rate-Bps 1 --expect-sha256 5b64b12ad6e657f403f9e3e57e4ad6fbd1d8fb14c53a0c7e1dc5dbd2257166b1 --expect-crc32 0xe6568d53 >logs/local-recv-1m.out 2>&1; rc=$?; wait $srv || true; cat logs/local-stream-1m.out logs/local-recv-1m.out; exit $rc
```

### Boot custom Linux and start WebSocket streamer

Write the custom-board SD image once, boot Linux, configure Ethernet,
and start the WebSocket PRBS streamer from UART. This section
intentionally leaves the streamer running for the following desktop
receive test. It does not use SSH or a second DFU/SD write cycle.

Build:

```
make -C stm32mp135_test_board boot
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/sdcard.img
stm32mp135_test_board/build/stream_ws_prbs_stream
```

Test (max 15 min):

```
bench_mcu:reset_dut2
delay ms=2000
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
delay ms=5000
inventory refresh=true verify=false
msc.custom:write data=@sdcard.img offset_lba=0
msc.custom:verify data=@sdcard.img offset_lba=0
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_write data="two\r"
mp135.custom:uart_expect sentinel="> " timeout_ms=15000
mp135.custom:uart_write data="jump"
delay ms=200
mp135.custom:uart_write data="\r"
mp135.custom:uart_expect sentinel="Jumping to address" timeout_ms=5000
mp135.custom:uart_expect sentinel="Linux version" timeout_ms=10000
mp135.custom:uart_expect sentinel="login:" timeout_ms=60000
mp135.custom:uart_write data="root\r"
mp135.custom:uart_expect sentinel="Password:" timeout_ms=10000
mp135.custom:uart_write data="root\r"
mp135.custom:uart_expect sentinel="# " timeout_ms=15000
mp135.custom:uart_write data="dmesg -n 1 2>/dev/null; true\r"
mp135.custom:uart_expect sentinel="# " timeout_ms=3000
delay ms=5000
mp135.custom:uart_write data="killall -q -9 udhcpc stream_ws_prbs_stream; ip addr flush dev eth0; ip link set eth0 up\r"
mp135.custom:uart_expect sentinel="# " timeout_ms=10000
mp135.custom:uart_write data="udhcpc -i eth0 -n -T 5 -t 6; echo dhcp_rc=$?\r"
mp135.custom:uart_expect sentinel="dhcp_rc=0" timeout_ms=30000
mp135.custom:uart_write data="ip addr replace 172.25.0.46/16 dev eth0; ip route replace default via 172.25.0.1 dev eth0; ip -4 addr show dev eth0; uname -a\r"
mp135.custom:uart_expect sentinel="172.25.0.46" timeout_ms=5000
mp135.custom:uart_close
ssh.custom:put data=@stream_ws_prbs_stream path="/tmp/stream_ws_prbs_stream" timeout_ms=20000
ssh.custom:exec command="chmod +x /tmp/stream_ws_prbs_stream; killall -q -9 stream_ws_prbs_stream; /tmp/stream_ws_prbs_stream --port 8765 --bytes 134217728 --seed 0x12345678 --frame-bytes 131072 >/tmp/stream_ws_prbs_stream.log 2>&1 & echo stream_ws_started=$!" timeout_ms=10000
mark tag=stream_ws_custom_boot_started
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    uart = Verification.load_stream_text(
        extract_dir, "mp135.uart", encoding="utf-8")
    ssh = Verification.load_stream_text(
        extract_dir, "ssh.exec", encoding="utf-8")
    return (Verification.op_succeeded(ops, "msc.custom", "verify") and
            "Linux version" in uart and
            "dhcp_rc=0" in uart and
            "172.25.0.46" in uart and
            Verification.op_succeeded(ops, "ssh.custom", "put") and
            Verification.op_succeeded(ops, "ssh.custom", "exec") and
            "stream_ws_started=" in ssh)
```

### Receive 128 MiB PRBS over WebSocket at 93 Mbps or faster

Connect from the bench desktop to the already-running custom-board
streamer. Receive exactly 128 MiB, compute SHA-256 and CRC32 while
reading, and fail if the payload is not bit-perfect or if wall-time
payload rate is below 93 Mbps.

Build: nothing required.

Test (max 4 min):

```
ws.any:recv url="ws://172.25.0.46:8765/" bytes=134217728 expect_sha256="ecc7e89ae3b56a33d68ba75ba15639498192d90f0a21bc63ccd88830cb148b7b" expect_crc32=0xf48e5cf5 min_rate_Bps=11625000 timeout_ms=180000
mark tag=stream_ws_custom_128m_93mbps_integrity
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    if not Verification.op_succeeded(ops, "ws.any", "recv"):
        return False
    checks = Verification.load_manifest(extract_dir).get("checks", [])
    text = repr(checks).lower()
    return ("134217728" in text and
            "ecc7e89ae3b56a33d68ba75ba15639498192d90f0a21bc63ccd88830cb148b7b" in text and
            "f48e5cf5" in text)
```
