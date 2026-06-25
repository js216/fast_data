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

### Local WebSocket protocol self-test

Build a native host copy of the streamer and receive a 1 MiB PRBS
payload over loopback using the package-free receiver. This catches
WebSocket framing, PRBS byte-order, SHA-256, and CRC32 regressions
before using the bench.

Build:

```
mkdir -p tmp/local-bin
gcc -O2 -Wall -Wextra -o tmp/local-bin/stream_ws_prbs_stream stm32mp135_test_board/tools/stream_ws_prbs_stream.c
```

Local test:

```
tmp/local-bin/stream_ws_prbs_stream --port 18765 --bytes 1048576 --seed 0x12345678 --frame-bytes 131072 >tmp/local-stream-1m.out 2>&1 & srv=$!; sleep 0.2; python3 stm32mp135_test_board/tools/stream_ws_receive.py --host 127.0.0.1 --port 18765 --bytes 1048576 --min-rate-Bps 1 --expect-sha256 5b64b12ad6e657f403f9e3e57e4ad6fbd1d8fb14c53a0c7e1dc5dbd2257166b1 --expect-crc32 0xe6568d53 >tmp/local-recv-1m.out 2>&1; rc=$?; kill $srv 2>/dev/null; wait $srv 2>/dev/null || true; cat tmp/local-stream-1m.out tmp/local-recv-1m.out; exit $rc
```

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
    needed_devices = {"bench_mcu.0", "mp135.custom", "ssh.any"}
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

### Build custom rootfs, bootloader, and WebSocket streamer

Build the Buildroot output, custom-board bootloader, and separate
target-side WebSocket PRBS streamer binary. The streamer is copied to
the running board by the hardware section; it is not baked into the
Buildroot overlay. It listens on TCP port 8765, performs the WebSocket
opening handshake, and sends xorshift32 PRBS bytes using the same seed
and byte order as `test_serv/plugins/_prbs.py`.

Build:

```
mkdir -p stm32mp135_test_board/build
make -C stm32mp135_test_board br
stm32mp135_test_board/buildroot/output/host/bin/arm-buildroot-linux-uclibcgnueabihf-gcc -O2 -Wall -Wextra -o stm32mp135_test_board/build/stream_ws_prbs_stream stm32mp135_test_board/tools/stream_ws_prbs_stream.c
make -C stm32mp135_test_board boot
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
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

    bootloader = Path("stm32mp135_test_board/bootloader/build/main.stm32")
    if not bootloader.exists() or bootloader.stat().st_size == 0:
        return False

    desc = subprocess.check_output(["file", str(binary)], text=True)
    return "ARM" in desc and "ELF" in desc
```

### Build custom kernel and SD image

Build the SD card image from Buildroot's kernel and device-tree
outputs. The SSH host key is trusted at runtime for the board's
captured `{{BOARD_IP}}` (see the boot section), so there is no
build-time known_hosts plan with a hardcoded IP.

Build:

```
make -C stm32mp135_test_board DTS=custom sd
```

Artifacts:

```
stm32mp135_test_board/buildroot/output/images/sdcard.img
```

Test: no hardware.

Verify:

```
def check(extract_dir):
    from pathlib import Path

    sd = Path("stm32mp135_test_board/buildroot/output/images/sdcard.img")
    return sd.exists() and sd.stat().st_size > 0
```

### Provision custom SD

Write the custom-board SD image once and leave the board stopped at the
bootloader prompt.

Build: nothing required.

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/sdcard.img
```

Test (max 5 min):

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
mark tag=stream_ws_custom_sd_written
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    return Verification.op_succeeded(ops, "msc.custom", "write")
```

### Load and jump custom Linux and capture its address

Run `two` from the bootloader to load the kernel and device tree, jump
into Linux, wait for the login prompt, and read eth0's DHCP address.
The `Capture:` block stores it as `{{BOARD_IP}}` for the following SSH
and WebSocket sections, so no IP is hardcoded.

Build: nothing required.

Test (max 1 min):

```
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
mp135.custom:uart_expect sentinel="Linux version" timeout_ms=5000
mp135.custom:uart_expect sentinel="login:" timeout_ms=15000
mp135.custom:uart_write data="root\r"
mp135.custom:uart_expect sentinel="Password:" timeout_ms=10000
mp135.custom:uart_write data="root\r"
mp135.custom:uart_expect sentinel="# " timeout_ms=15000
mp135.custom:uart_write data="dmesg -n 1 2>/dev/null; true\r"
mp135.custom:uart_expect sentinel="# " timeout_ms=3000
delay ms=5000
mp135.custom:uart_write data="killall -q -9 stream_ws_prbs_stream 2>/dev/null; ip -4 -o addr show dev eth0; ip route; uname -a\r"
mp135.custom:uart_expect sentinel="inet 172.25.0." timeout_ms=5000
mp135.custom:uart_close
mark tag=stream_ws_custom_boot_ip
```

Capture:

```
BOARD_IP = mp135.uart /inet (172\.25\.0\.\d+)/
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream_text(
        extract_dir, "mp135.uart", encoding="utf-8")
    return ("Copying 1 blocks" in uart and
            "DDR addr 0xC4000000" in uart and
            "Linux version" in uart and
            "inet 172.25.0." in uart)
```

### Trust host key and start the WebSocket streamer

Trust the board's SSH host key for its captured `{{BOARD_IP}}`, upload
the streamer, and start it (left running for the receive test). The
host key is extracted host-side from the Buildroot output and trusted
at runtime against the captured IP exported to the build as
`$RUNPY_BOARD_IP`.

Build:

```
python3 -c "import base64,os,struct; d=open('stm32mp135_test_board/buildroot/output/target/etc/dropbear/dropbear_ed25519_host_key.bin','rb').read(); i=0; n=struct.unpack('>I',d[i:i+4])[0]; i+=4; assert d[i:i+n]==b'ssh-ed25519','unexpected key type'; i+=n; n=struct.unpack('>I',d[i:i+4])[0]; i+=4; pub=d[i:i+n][-32:]; line='ssh-ed25519 '+base64.b64encode(struct.pack('>I',11)+b'ssh-ed25519'+struct.pack('>I',32)+pub).decode()+' root@buildroot'; ip=os.environ['RUNPY_BOARD_IP']; open(os.environ['RUNPY_WORKDIR']+'/trust.plan','w').write('description \"trust host key for '+ip+'\"'+chr(10)+'ssh.any:trust_host_key key=\"'+line+'\" ip=\"'+ip+'\"'+chr(10))"
python3 test_serv/submit.py --server http://localhost:8080 --wait 120 "$RUNPY_WORKDIR/trust.plan"
```

Artifacts:

```
stm32mp135_test_board/build/stream_ws_prbs_stream
```

Test (max 1 min):

```
ssh.any:put data=@stream_ws_prbs_stream path="/tmp/stream_ws_prbs_stream" ip="{{BOARD_IP}}" timeout_ms=20000
ssh.any:exec command="chmod +x /tmp/stream_ws_prbs_stream; killall -q -9 stream_ws_prbs_stream; /tmp/stream_ws_prbs_stream --port 8765 --bytes 134217728 --seed 0x12345678 --frame-bytes 131072 >/tmp/stream_ws_prbs_stream.log 2>&1 & echo stream_ws_started=$!" ip="{{BOARD_IP}}" timeout_ms=10000
mark tag=stream_ws_custom_boot_started
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    ssh = Verification.load_stream_text(
        extract_dir, "ssh.exec", encoding="utf-8")
    return (Verification.op_succeeded(ops, "ssh.any", "put") and
            Verification.op_succeeded(ops, "ssh.any", "exec") and
            "stream_ws_started=" in ssh)
```

### Receive 1 MiB

Restart the one-shot streamer for 1 MiB (1048576 bytes), receive it, crc-verify,
and report achieved Mbps and core temperature. No rate gate (overhead-dominated).

Build: nothing required.

Test (max 3 min):

```
ssh.any:exec command="killall -q -9 stream_ws_prbs_stream 2>/dev/null; sleep 1; setsid /tmp/stream_ws_prbs_stream --port 8765 --bytes 1048576 --seed 0x12345678 --frame-bytes 131072 >/tmp/sw.log 2>&1 </dev/null & echo started=$!" ip="{{BOARD_IP}}" timeout_ms=10000
delay ms=800
ws.any:recv url="ws://{{BOARD_IP}}:8765/" bytes=1048576 expect_crc32=0xe6568d53 timeout_ms=30000
ssh.any:exec command="echo TEMP=`cat /sys/class/thermal/thermal_zone0/temp`" ip="{{BOARD_IP}}" timeout_ms=10000
mark tag=ws_sweep_1mib
```

Verify:

```
def check(extract_dir):
    import sys, os
    rate = temp = None
    try:
        tl = open(os.path.join(extract_dir, "timeline.log"), errors="replace").read()
        m = re.search(r"ws:recv\s+\d+B in [\d.]+s @ (\d+) B/s", tl)
        if m:
            rate = int(m.group(1)) * 8.0 / 1e6
    except Exception:
        pass
    try:
        se = open(os.path.join(extract_dir, "streams", "ssh.exec.bin"), errors="replace").read()
        mt = re.search(r"TEMP=(\d+)", se)
        if mt:
            temp = int(mt.group(1)) / 1000.0
    except Exception:
        pass
    out = ""
    if rate is not None:
        out += "%.1fMbps " % rate
    if temp is not None:
        out += "%.1fC " % temp
    if out:
        sys.stderr.write(out); sys.stderr.flush()
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    return Verification.op_succeeded(ops, "ws.any", "recv")
```

### Receive 2 MiB

Restart the one-shot streamer for 2 MiB (2097152 bytes), receive it, crc-verify,
and report achieved Mbps and core temperature. No rate gate (overhead-dominated).

Build: nothing required.

Test (max 3 min):

```
ssh.any:exec command="killall -q -9 stream_ws_prbs_stream 2>/dev/null; sleep 1; setsid /tmp/stream_ws_prbs_stream --port 8765 --bytes 2097152 --seed 0x12345678 --frame-bytes 131072 >/tmp/sw.log 2>&1 </dev/null & echo started=$!" ip="{{BOARD_IP}}" timeout_ms=10000
delay ms=800
ws.any:recv url="ws://{{BOARD_IP}}:8765/" bytes=2097152 expect_crc32=0x10ea3bbe timeout_ms=30000
ssh.any:exec command="echo TEMP=`cat /sys/class/thermal/thermal_zone0/temp`" ip="{{BOARD_IP}}" timeout_ms=10000
mark tag=ws_sweep_2mib
```

Verify:

```
def check(extract_dir):
    import sys, os
    rate = temp = None
    try:
        tl = open(os.path.join(extract_dir, "timeline.log"), errors="replace").read()
        m = re.search(r"ws:recv\s+\d+B in [\d.]+s @ (\d+) B/s", tl)
        if m:
            rate = int(m.group(1)) * 8.0 / 1e6
    except Exception:
        pass
    try:
        se = open(os.path.join(extract_dir, "streams", "ssh.exec.bin"), errors="replace").read()
        mt = re.search(r"TEMP=(\d+)", se)
        if mt:
            temp = int(mt.group(1)) / 1000.0
    except Exception:
        pass
    out = ""
    if rate is not None:
        out += "%.1fMbps " % rate
    if temp is not None:
        out += "%.1fC " % temp
    if out:
        sys.stderr.write(out); sys.stderr.flush()
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    return Verification.op_succeeded(ops, "ws.any", "recv")
```

### Receive 4 MiB

Restart the one-shot streamer for 4 MiB (4194304 bytes), receive it, crc-verify,
and report achieved Mbps and core temperature. No rate gate (overhead-dominated).

Build: nothing required.

Test (max 3 min):

```
ssh.any:exec command="killall -q -9 stream_ws_prbs_stream 2>/dev/null; sleep 1; setsid /tmp/stream_ws_prbs_stream --port 8765 --bytes 4194304 --seed 0x12345678 --frame-bytes 131072 >/tmp/sw.log 2>&1 </dev/null & echo started=$!" ip="{{BOARD_IP}}" timeout_ms=10000
delay ms=800
ws.any:recv url="ws://{{BOARD_IP}}:8765/" bytes=4194304 expect_crc32=0xc832783e timeout_ms=30000
ssh.any:exec command="echo TEMP=`cat /sys/class/thermal/thermal_zone0/temp`" ip="{{BOARD_IP}}" timeout_ms=10000
mark tag=ws_sweep_4mib
```

Verify:

```
def check(extract_dir):
    import sys, os
    rate = temp = None
    try:
        tl = open(os.path.join(extract_dir, "timeline.log"), errors="replace").read()
        m = re.search(r"ws:recv\s+\d+B in [\d.]+s @ (\d+) B/s", tl)
        if m:
            rate = int(m.group(1)) * 8.0 / 1e6
    except Exception:
        pass
    try:
        se = open(os.path.join(extract_dir, "streams", "ssh.exec.bin"), errors="replace").read()
        mt = re.search(r"TEMP=(\d+)", se)
        if mt:
            temp = int(mt.group(1)) / 1000.0
    except Exception:
        pass
    out = ""
    if rate is not None:
        out += "%.1fMbps " % rate
    if temp is not None:
        out += "%.1fC " % temp
    if out:
        sys.stderr.write(out); sys.stderr.flush()
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    return Verification.op_succeeded(ops, "ws.any", "recv")
```

### Receive 8 MiB

Restart the one-shot streamer for 8 MiB (8388608 bytes), receive it, crc-verify,
and report achieved Mbps and core temperature. No rate gate (overhead-dominated).

Build: nothing required.

Test (max 3 min):

```
ssh.any:exec command="killall -q -9 stream_ws_prbs_stream 2>/dev/null; sleep 1; setsid /tmp/stream_ws_prbs_stream --port 8765 --bytes 8388608 --seed 0x12345678 --frame-bytes 131072 >/tmp/sw.log 2>&1 </dev/null & echo started=$!" ip="{{BOARD_IP}}" timeout_ms=10000
delay ms=800
ws.any:recv url="ws://{{BOARD_IP}}:8765/" bytes=8388608 expect_crc32=0xf1e9a5ef timeout_ms=30000
ssh.any:exec command="echo TEMP=`cat /sys/class/thermal/thermal_zone0/temp`" ip="{{BOARD_IP}}" timeout_ms=10000
mark tag=ws_sweep_8mib
```

Verify:

```
def check(extract_dir):
    import sys, os
    rate = temp = None
    try:
        tl = open(os.path.join(extract_dir, "timeline.log"), errors="replace").read()
        m = re.search(r"ws:recv\s+\d+B in [\d.]+s @ (\d+) B/s", tl)
        if m:
            rate = int(m.group(1)) * 8.0 / 1e6
    except Exception:
        pass
    try:
        se = open(os.path.join(extract_dir, "streams", "ssh.exec.bin"), errors="replace").read()
        mt = re.search(r"TEMP=(\d+)", se)
        if mt:
            temp = int(mt.group(1)) / 1000.0
    except Exception:
        pass
    out = ""
    if rate is not None:
        out += "%.1fMbps " % rate
    if temp is not None:
        out += "%.1fC " % temp
    if out:
        sys.stderr.write(out); sys.stderr.flush()
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    return Verification.op_succeeded(ops, "ws.any", "recv")
```

### Receive 16 MiB

Restart the one-shot streamer for 16 MiB (16777216 bytes), receive it, crc-verify,
and report achieved Mbps and core temperature. No rate gate (overhead-dominated).

Build: nothing required.

Test (max 3 min):

```
ssh.any:exec command="killall -q -9 stream_ws_prbs_stream 2>/dev/null; sleep 1; setsid /tmp/stream_ws_prbs_stream --port 8765 --bytes 16777216 --seed 0x12345678 --frame-bytes 131072 >/tmp/sw.log 2>&1 </dev/null & echo started=$!" ip="{{BOARD_IP}}" timeout_ms=10000
delay ms=800
ws.any:recv url="ws://{{BOARD_IP}}:8765/" bytes=16777216 expect_crc32=0xf89e248a timeout_ms=30000
ssh.any:exec command="echo TEMP=`cat /sys/class/thermal/thermal_zone0/temp`" ip="{{BOARD_IP}}" timeout_ms=10000
mark tag=ws_sweep_16mib
```

Verify:

```
def check(extract_dir):
    import sys, os
    rate = temp = None
    try:
        tl = open(os.path.join(extract_dir, "timeline.log"), errors="replace").read()
        m = re.search(r"ws:recv\s+\d+B in [\d.]+s @ (\d+) B/s", tl)
        if m:
            rate = int(m.group(1)) * 8.0 / 1e6
    except Exception:
        pass
    try:
        se = open(os.path.join(extract_dir, "streams", "ssh.exec.bin"), errors="replace").read()
        mt = re.search(r"TEMP=(\d+)", se)
        if mt:
            temp = int(mt.group(1)) / 1000.0
    except Exception:
        pass
    out = ""
    if rate is not None:
        out += "%.1fMbps " % rate
    if temp is not None:
        out += "%.1fC " % temp
    if out:
        sys.stderr.write(out); sys.stderr.flush()
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    return Verification.op_succeeded(ops, "ws.any", "recv")
```

### Receive 32 MiB

Restart the one-shot streamer for 32 MiB (33554432 bytes), receive it, crc-verify,
and report achieved Mbps and core temperature. No rate gate (overhead-dominated).

Build: nothing required.

Test (max 3 min):

```
ssh.any:exec command="killall -q -9 stream_ws_prbs_stream 2>/dev/null; sleep 1; setsid /tmp/stream_ws_prbs_stream --port 8765 --bytes 33554432 --seed 0x12345678 --frame-bytes 131072 >/tmp/sw.log 2>&1 </dev/null & echo started=$!" ip="{{BOARD_IP}}" timeout_ms=10000
delay ms=800
ws.any:recv url="ws://{{BOARD_IP}}:8765/" bytes=33554432 expect_crc32=0xe0a414c5 timeout_ms=30000
ssh.any:exec command="echo TEMP=`cat /sys/class/thermal/thermal_zone0/temp`" ip="{{BOARD_IP}}" timeout_ms=10000
mark tag=ws_sweep_32mib
```

Verify:

```
def check(extract_dir):
    import sys, os
    rate = temp = None
    try:
        tl = open(os.path.join(extract_dir, "timeline.log"), errors="replace").read()
        m = re.search(r"ws:recv\s+\d+B in [\d.]+s @ (\d+) B/s", tl)
        if m:
            rate = int(m.group(1)) * 8.0 / 1e6
    except Exception:
        pass
    try:
        se = open(os.path.join(extract_dir, "streams", "ssh.exec.bin"), errors="replace").read()
        mt = re.search(r"TEMP=(\d+)", se)
        if mt:
            temp = int(mt.group(1)) / 1000.0
    except Exception:
        pass
    out = ""
    if rate is not None:
        out += "%.1fMbps " % rate
    if temp is not None:
        out += "%.1fC " % temp
    if out:
        sys.stderr.write(out); sys.stderr.flush()
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    return Verification.op_succeeded(ops, "ws.any", "recv")
```

### Receive 64 MiB

Restart the one-shot streamer for 64 MiB (67108864 bytes), receive it, crc-verify,
and report achieved Mbps and core temperature. No rate gate (overhead-dominated).

Build: nothing required.

Test (max 3 min):

```
ssh.any:exec command="killall -q -9 stream_ws_prbs_stream 2>/dev/null; sleep 1; setsid /tmp/stream_ws_prbs_stream --port 8765 --bytes 67108864 --seed 0x12345678 --frame-bytes 131072 >/tmp/sw.log 2>&1 </dev/null & echo started=$!" ip="{{BOARD_IP}}" timeout_ms=10000
delay ms=800
ws.any:recv url="ws://{{BOARD_IP}}:8765/" bytes=67108864 expect_crc32=0x9bffbe60 timeout_ms=40000
ssh.any:exec command="echo TEMP=`cat /sys/class/thermal/thermal_zone0/temp`" ip="{{BOARD_IP}}" timeout_ms=10000
mark tag=ws_sweep_64mib
```

Verify:

```
def check(extract_dir):
    import sys, os
    rate = temp = None
    try:
        tl = open(os.path.join(extract_dir, "timeline.log"), errors="replace").read()
        m = re.search(r"ws:recv\s+\d+B in [\d.]+s @ (\d+) B/s", tl)
        if m:
            rate = int(m.group(1)) * 8.0 / 1e6
    except Exception:
        pass
    try:
        se = open(os.path.join(extract_dir, "streams", "ssh.exec.bin"), errors="replace").read()
        mt = re.search(r"TEMP=(\d+)", se)
        if mt:
            temp = int(mt.group(1)) / 1000.0
    except Exception:
        pass
    out = ""
    if rate is not None:
        out += "%.1fMbps " % rate
    if temp is not None:
        out += "%.1fC " % temp
    if out:
        sys.stderr.write(out); sys.stderr.flush()
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    return Verification.op_succeeded(ops, "ws.any", "recv")
```

### Receive 128 MiB

Restart the one-shot streamer for 128 MiB (134217728 bytes), receive it, crc-verify,
and report achieved Mbps and core temperature. The 93 Mbps rate gate applies.

Build: nothing required.

Test (max 3 min):

```
ssh.any:exec command="killall -q -9 stream_ws_prbs_stream 2>/dev/null; sleep 1; setsid /tmp/stream_ws_prbs_stream --port 8765 --bytes 134217728 --seed 0x12345678 --frame-bytes 131072 >/tmp/sw.log 2>&1 </dev/null & echo started=$!" ip="{{BOARD_IP}}" timeout_ms=10000
delay ms=800
ws.any:recv url="ws://{{BOARD_IP}}:8765/" bytes=134217728 expect_crc32=0xf48e5cf5 min_rate_Bps=11625000 timeout_ms=60000
ssh.any:exec command="echo TEMP=`cat /sys/class/thermal/thermal_zone0/temp`" ip="{{BOARD_IP}}" timeout_ms=10000
mark tag=ws_sweep_128mib
```

Verify:

```
def check(extract_dir):
    import sys, os
    rate = temp = None
    try:
        tl = open(os.path.join(extract_dir, "timeline.log"), errors="replace").read()
        m = re.search(r"ws:recv\s+\d+B in [\d.]+s @ (\d+) B/s", tl)
        if m:
            rate = int(m.group(1)) * 8.0 / 1e6
    except Exception:
        pass
    try:
        se = open(os.path.join(extract_dir, "streams", "ssh.exec.bin"), errors="replace").read()
        mt = re.search(r"TEMP=(\d+)", se)
        if mt:
            temp = int(mt.group(1)) / 1000.0
    except Exception:
        pass
    out = ""
    if rate is not None:
        out += "%.1fMbps " % rate
    if temp is not None:
        out += "%.1fC " % temp
    if out:
        sys.stderr.write(out); sys.stderr.flush()
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    return Verification.op_succeeded(ops, "ws.any", "recv")
```

### Receive 256 MiB

Restart the one-shot streamer for 256 MiB (268435456 bytes), receive it, crc-verify,
and report achieved Mbps and core temperature. The 93 Mbps rate gate applies.

Build: nothing required.

Test (max 3 min):

```
ssh.any:exec command="killall -q -9 stream_ws_prbs_stream 2>/dev/null; sleep 1; setsid /tmp/stream_ws_prbs_stream --port 8765 --bytes 268435456 --seed 0x12345678 --frame-bytes 131072 >/tmp/sw.log 2>&1 </dev/null & echo started=$!" ip="{{BOARD_IP}}" timeout_ms=10000
delay ms=800
ws.any:recv url="ws://{{BOARD_IP}}:8765/" bytes=268435456 expect_crc32=0x96e039fa min_rate_Bps=11625000 timeout_ms=90000
ssh.any:exec command="echo TEMP=`cat /sys/class/thermal/thermal_zone0/temp`" ip="{{BOARD_IP}}" timeout_ms=10000
mark tag=ws_sweep_256mib
```

Verify:

```
def check(extract_dir):
    import sys, os
    rate = temp = None
    try:
        tl = open(os.path.join(extract_dir, "timeline.log"), errors="replace").read()
        m = re.search(r"ws:recv\s+\d+B in [\d.]+s @ (\d+) B/s", tl)
        if m:
            rate = int(m.group(1)) * 8.0 / 1e6
    except Exception:
        pass
    try:
        se = open(os.path.join(extract_dir, "streams", "ssh.exec.bin"), errors="replace").read()
        mt = re.search(r"TEMP=(\d+)", se)
        if mt:
            temp = int(mt.group(1)) / 1000.0
    except Exception:
        pass
    out = ""
    if rate is not None:
        out += "%.1fMbps " % rate
    if temp is not None:
        out += "%.1fC " % temp
    if out:
        sys.stderr.write(out); sys.stderr.flush()
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    return Verification.op_succeeded(ops, "ws.any", "recv")
```

### Receive 512 MiB

Restart the one-shot streamer for 512 MiB (536870912 bytes), receive it, crc-verify,
and report achieved Mbps and core temperature. The 93 Mbps rate gate applies.

Build: nothing required.

Test (max 4 min):

```
ssh.any:exec command="killall -q -9 stream_ws_prbs_stream 2>/dev/null; sleep 1; setsid /tmp/stream_ws_prbs_stream --port 8765 --bytes 536870912 --seed 0x12345678 --frame-bytes 131072 >/tmp/sw.log 2>&1 </dev/null & echo started=$!" ip="{{BOARD_IP}}" timeout_ms=10000
delay ms=800
ws.any:recv url="ws://{{BOARD_IP}}:8765/" bytes=536870912 expect_crc32=0xa05a6a2f min_rate_Bps=11625000 timeout_ms=150000
ssh.any:exec command="echo TEMP=`cat /sys/class/thermal/thermal_zone0/temp`" ip="{{BOARD_IP}}" timeout_ms=10000
mark tag=ws_sweep_512mib
```

Verify:

```
def check(extract_dir):
    import sys, os
    rate = temp = None
    try:
        tl = open(os.path.join(extract_dir, "timeline.log"), errors="replace").read()
        m = re.search(r"ws:recv\s+\d+B in [\d.]+s @ (\d+) B/s", tl)
        if m:
            rate = int(m.group(1)) * 8.0 / 1e6
    except Exception:
        pass
    try:
        se = open(os.path.join(extract_dir, "streams", "ssh.exec.bin"), errors="replace").read()
        mt = re.search(r"TEMP=(\d+)", se)
        if mt:
            temp = int(mt.group(1)) / 1000.0
    except Exception:
        pass
    out = ""
    if rate is not None:
        out += "%.1fMbps " % rate
    if temp is not None:
        out += "%.1fC " % temp
    if out:
        sys.stderr.write(out); sys.stderr.flush()
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    return Verification.op_succeeded(ops, "ws.any", "recv")
```

### Receive 1 GiB

Restart the one-shot streamer for 1 GiB (1073741824 bytes), receive it, crc-verify,
and report achieved Mbps and core temperature. The 93 Mbps rate gate applies.

Build: nothing required.

Test (max 6 min):

```
ssh.any:exec command="killall -q -9 stream_ws_prbs_stream 2>/dev/null; sleep 1; setsid /tmp/stream_ws_prbs_stream --port 8765 --bytes 1073741824 --seed 0x12345678 --frame-bytes 131072 >/tmp/sw.log 2>&1 </dev/null & echo started=$!" ip="{{BOARD_IP}}" timeout_ms=10000
delay ms=800
ws.any:recv url="ws://{{BOARD_IP}}:8765/" bytes=1073741824 expect_crc32=0x501f0d96 min_rate_Bps=11625000 timeout_ms=260000
ssh.any:exec command="echo TEMP=`cat /sys/class/thermal/thermal_zone0/temp`" ip="{{BOARD_IP}}" timeout_ms=10000
mark tag=ws_sweep_1gib
```

Verify:

```
def check(extract_dir):
    import sys, os
    rate = temp = None
    try:
        tl = open(os.path.join(extract_dir, "timeline.log"), errors="replace").read()
        m = re.search(r"ws:recv\s+\d+B in [\d.]+s @ (\d+) B/s", tl)
        if m:
            rate = int(m.group(1)) * 8.0 / 1e6
    except Exception:
        pass
    try:
        se = open(os.path.join(extract_dir, "streams", "ssh.exec.bin"), errors="replace").read()
        mt = re.search(r"TEMP=(\d+)", se)
        if mt:
            temp = int(mt.group(1)) / 1000.0
    except Exception:
        pass
    out = ""
    if rate is not None:
        out += "%.1fMbps " % rate
    if temp is not None:
        out += "%.1fC " % temp
    if out:
        sys.stderr.write(out); sys.stderr.flush()
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    return Verification.op_succeeded(ops, "ws.any", "recv")
```

### Receive 512 MiB x10 (rate + temp under repeated load)

Run the 512 MiB transfer ten times back-to-back. Each iteration restarts the
streamer, receives + crc-verifies, and prints the effective wall-clock data
rate and the core temperature, so any rate degradation, heating, or corruption
onset under sustained load is visible across the ten runs.

Build: nothing required.

Foreach:

```
i in count(10)
```

Test (max 4 min):

```
ssh.any:exec command="killall -q -9 stream_ws_prbs_stream 2>/dev/null; sleep 1; setsid /tmp/stream_ws_prbs_stream --port 8765 --bytes 536870912 --seed 0x12345678 --frame-bytes 131072 >/tmp/sw.log 2>&1 </dev/null & echo started=$!" ip="{{BOARD_IP}}" timeout_ms=10000
delay ms=800
ws.any:recv url="ws://{{BOARD_IP}}:8765/" bytes=536870912 expect_crc32=0xa05a6a2f min_rate_Bps=11625000 timeout_ms=150000
ssh.any:exec command="echo TEMP=`cat /sys/class/thermal/thermal_zone0/temp`" ip="{{BOARD_IP}}" timeout_ms=10000
mark tag=ws_512_loop
```

Verify:

```
def check(extract_dir, item):
    import sys, os
    rate = temp = None
    try:
        tl = open(os.path.join(extract_dir, "timeline.log"), errors="replace").read()
        m = re.search(r"ws:recv\s+\d+B in [\d.]+s @ (\d+) B/s", tl)
        if m:
            rate = int(m.group(1)) * 8.0 / 1e6
    except Exception:
        pass
    try:
        se = open(os.path.join(extract_dir, "streams", "ssh.exec.bin"), errors="replace").read()
        mt = re.search(r"TEMP=(\d+)", se)
        if mt:
            temp = int(mt.group(1)) / 1000.0
    except Exception:
        pass
    out = "iter %s: " % item
    if rate is not None:
        out += "%.1fMbps " % rate
    if temp is not None:
        out += "%.1fC " % temp
    if out:
        sys.stderr.write(out); sys.stderr.flush()
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    return Verification.op_succeeded(ops, "ws.any", "recv")
```
