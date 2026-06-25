# USBTMC Gadget From Custom STM32MP135 Linux

Prove that the custom STM32MP135 board exposes the same Linux-owned
USBTMC/USB488 instrument behavior as the EVB mission.

The pass condition is:

- the custom board boots the Linux image built by this tree,
- Linux configures the STM32MP135 UDC as a USBTMC-capable gadget,
- the host sees one USBTMC USB488 interface and no active ROM DFU or
  bare-metal MSC bootloader device,
- required USBTMC/USB488 control requests return valid status packets,
- mandatory USB488 common commands return deterministic responses,
- invalid or unsupported commands return a controlled error,
- binary payload transfers are bit-perfect, and
- sustained USBTMC bulk throughput meets the mission floor.

### Inventory Exposes Custom USB Gadget Test Surface

Confirm the bench exposes the devices and operations needed to boot the
custom board, write its SD image, control UART, inspect host-side USB,
and read host-side dmesg.

Build: nothing required.

Test (max 30 s):

```
inventory
mark tag=usbtmc_custom_inventory
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
    needed_devices = {"bench_mcu.0", "mp135.custom"}
    if not needed_devices.issubset(device_ids):
        return False

    ops = json.loads(Path(extract_dir, "bench.ops.json").read_text())
    required_ops = {
        "bench_mcu": {"reset_dut2"},
        "dmesg": {"tail"},
        "dfu": {"flash_layout"},
        "msc": {"write", "verify"},
        "mp135": {"uart_open", "uart_write", "uart_expect", "uart_close"},
        "usbtmc": {"identify", "list"},
    }
    for plugin, names in required_ops.items():
        available = set(ops.get(plugin, {}).get("ops", {}))
        if not names.issubset(available):
            return False

    return any(k == "usb" or k.startswith("usb.") for k in ops)
```

### Build Custom Base USBTMC Inputs

Prepare the Buildroot output, including the custom-board kernel and
device trees, plus the custom bootloader input needed by the final image
packaging step. This section does not touch hardware.

Build:

```
make -C stm32mp135_test_board br
make -C stm32mp135_test_board/bootloader clean
make -C stm32mp135_test_board/bootloader -j$(nproc)
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
    return (
        Path("stm32mp135_test_board/bootloader/scripts/flash.tsv").is_file()
        and Path("stm32mp135_test_board/bootloader/build/main.stm32").stat().st_size > 0
    )
```

### Package Custom Linux USBTMC Image

Install the USBTMC gadget daemon in the rootfs and package the final SD
image using Buildroot's kernel and DTB outputs. This section does not
touch hardware.

Build:

```
make -C stm32mp135_test_board usbtmc-gadget
make -C stm32mp135_test_board rootfs
make -C stm32mp135_test_board DTS=custom sd
```

Artifacts:

```
stm32mp135_test_board/buildroot/output/images/sdcard.img
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(_extract_dir):
    return (
        Path("stm32mp135_test_board/buildroot/output/images/sdcard.img").stat().st_size > 0
        and Path("stm32mp135_test_board/build/usbtmc_gadget").stat().st_size > 0
    )
```

### Write Custom SD Image

Flash the custom-board bootloader, stop at the bootloader prompt, and
write the prepared SD image over MSC. This section does not verify or
boot Linux.

Build: nothing required.

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/sdcard.img
```

Test (max 1 min):

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
mp135.custom:uart_expect sentinel="Board custom" timeout_ms=3000
mp135.custom:uart_expect sentinel="> " timeout_ms=3000
mp135.custom:uart_close
delay ms=5000
inventory refresh=true verify=false
msc.custom:write data=@sdcard.img offset_lba=0 min_rate_Bps=3000000
mark tag=usbtmc_custom_sd_written
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False

    ops = Verification.load_ops(extract_dir)
    return (
        Verification.op_succeeded(ops, "dfu.custom", "flash_layout")
        and Verification.op_succeeded(ops, "msc.custom", "write")
    )
```

### Verify Custom SD Image And Load Linux

Verify the already-written custom SD image, then load Linux/DTB with
`two`. This section does not jump into Linux.

Build: nothing required.

Artifacts:

```
stm32mp135_test_board/buildroot/output/images/sdcard.img
```

Test (inherits the bootloader-at-`> ` state and written SD image from
the previous section; max 1 min):

```
msc.custom:verify data=@sdcard.img offset_lba=0 min_rate_Bps=3000000
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
mp135.custom:uart_expect sentinel="DDR addr 0xC4000000" timeout_ms=15000
mp135.custom:uart_expect sentinel="> " timeout_ms=5000
mp135.custom:uart_close
mark tag=usbtmc_custom_sd_verified_linux_loaded
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False

    ops = Verification.load_ops(extract_dir)
    return Verification.op_succeeded(ops, "msc.custom", "verify")
```

### Boot Custom Linux USBTMC Gadget

Boot Linux from the already-written custom SD image and prove the
USBTMC gadget is configured by Linux on the custom board. This section
starts at `jump` and ends at the Linux login.

Build: nothing required.

Artifacts:

```
stm32mp135_test_board/buildroot/output/images/sdcard.img
```

Test (inherits the loaded Linux/DTB-at-`> ` state and written SD image
from the previous section; max 1 min):

```
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="\r"
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
mp135.custom:uart_write data="root\r"
mp135.custom:uart_expect sentinel="Password:" timeout_ms=10000
mp135.custom:uart_write data="root\r"
mp135.custom:uart_expect sentinel="# " timeout_ms=15000
delay ms=4000
mp135.custom:uart_write data="dmesg -n 1 2>/dev/null; true\r"
mp135.custom:uart_expect sentinel="# " timeout_ms=3000
mp135.custom:uart_write data="test -s /run/usbtmc_gadget.ready && echo USBTMC_READY_OK\r"
mp135.custom:uart_expect sentinel="USBTMC_READY_OK" timeout_ms=5000
mp135.custom:uart_write data="echo MANUFACTURER_$(cat /sys/kernel/config/usb_gadget/usbtmc/strings/0x409/manufacturer)\r"
mp135.custom:uart_expect sentinel="MANUFACTURER_STMicroelectronics" timeout_ms=5000
mp135.custom:uart_write data="echo SERIAL_$(cat /sys/kernel/config/usb_gadget/usbtmc/strings/0x409/serialnumber)\r"
mp135.custom:uart_expect sentinel="SERIAL_custom-linux-usbtmc-0001" timeout_ms=5000
mp135.custom:uart_write data="echo VID_$(cat /sys/kernel/config/usb_gadget/usbtmc/idVendor)\r"
mp135.custom:uart_expect sentinel="VID_0x0483" timeout_ms=5000
mp135.custom:uart_write data="echo PID_$(cat /sys/kernel/config/usb_gadget/usbtmc/idProduct)\r"
mp135.custom:uart_expect sentinel="PID_0x571e" timeout_ms=5000
mp135.custom:uart_write data="echo UDC_STATE_$(cat /sys/class/udc/*/state)\r"
mp135.custom:uart_expect sentinel="UDC_STATE_configured" timeout_ms=5000
mp135.custom:uart_write data="stty -echo; echo STTYDONE\r"
mp135.custom:uart_expect sentinel="STTYDONE" timeout_ms=4000
mp135.custom:uart_close
delay ms=8000
inventory refresh=true verify=false
usbtmc.any:list
dmesg.any:tail lines=300 timeout_ms=5000
mark tag=usbtmc_custom_boot
```

Verify:

```
def check(extract_dir):
    import json

    if not Verification.manifest_clean(extract_dir):
        return False

    uart = Verification.load_stream_text(extract_dir, "mp135.uart")
    for s in [
        "USBTMC_READY_OK",
        "MANUFACTURER_STMicroelectronics",
        "SERIAL_custom-linux-usbtmc-0001",
        "VID_0x0483",
        "PID_0x571e",
        "UDC_STATE_configured",
    ]:
        if s not in uart:
            return False

    devices = json.loads(Verification.load_stream_text(extract_dir, "usbtmc.list"))
    custom_devices = [
        d for d in devices
        if d.get("serial") == "custom-linux-usbtmc-0001"
    ]
    if len(custom_devices) != 1:
        return False
    dev = custom_devices[0]
    expected = {
        "manufacturer": "STMicroelectronics",
        "pid": "571e",
        "product": "STM32MP135 Linux USBTMC",
        "serial": "custom-linux-usbtmc-0001",
        "vid": "0483",
    }
    for k, v in expected.items():
        if dev.get(k) != v:
            return False

    dmesg = Verification.load_stream_text(extract_dir, "dmesg.tail")
    lines = dmesg.splitlines()
    enum_indexes = [
        i for i, line in enumerate(lines)
        if "New USB device found, idVendor=0483, idProduct=571e" in line
    ]
    if not enum_indexes:
        return False

    after_enum = "\n".join(lines[enum_indexes[-1]:])
    required = [
        "New USB device found, idVendor=0483, idProduct=571e",
        "Product: STM32MP135 Linux USBTMC",
        "Manufacturer: STMicroelectronics",
        "SerialNumber: custom-linux-usbtmc-0001",
    ]
    forbidden = [
        "usb_control_msg returned -110",
        "can't read capabilities",
        "Device sent reply with wrong MsgID",
    ]
    return all(s in after_enum for s in required) and not any(
        s in after_enum for s in forbidden
    )
```

### Custom Board USBTMC Command Parity

Run the USBTMC/USB488 command-behavior checks on the already-booted custom
board, before the payload-size sweep. Binary integrity and sustained
throughput are covered by the size sweep and foreach that follow.

Build: nothing required.

Test (reuse the booted custom Linux USBTMC gadget; max 1 min):

```
delay ms=1500
inventory refresh=true verify=false
usbtmc.any:list
usbtmc.any:identify serial="custom-linux-usbtmc-0001" expect="STM32MP135-USBTMC"
usbtmc.any:query serial="custom-linux-usbtmc-0001" data="*OPC?" length=32 timeout_ms=2000
usbtmc.any:query serial="custom-linux-usbtmc-0001" data="*TST?" length=32 timeout_ms=2000
usbtmc.any:query serial="custom-linux-usbtmc-0001" data="*STB?" length=32 timeout_ms=2000
usbtmc.any:write serial="custom-linux-usbtmc-0001" data="*CLS" timeout_ms=2000
usbtmc.any:query serial="custom-linux-usbtmc-0001" data="UNKNOWN:HDR?" length=128 timeout_ms=2000
usbtmc.any:query serial="custom-linux-usbtmc-0001" data="SYST:ERR?" length=128 timeout_ms=2000
mark tag=usbtmc_custom_command_parity
```

Verify: the custom board (addressed by serial, never by `/dev/usbtmcN`
index) identifies and answers the USB488 common commands deterministically
(`*OPC?`->1, `*TST?`->0, `*STB?`->0), and an unknown header is reported via
`SYST:ERR?`:

```
def check(extract_dir):
    import json

    if not Verification.manifest_clean(extract_dir):
        return False

    idn = Verification.load_stream_text(extract_dir, "usbtmc.idn")
    if "STM32MP135-USBTMC" not in idn:
        return False

    cmds = Verification.load_stream_text(extract_dir, "usbtmc.query")
    if "1\n0\n0\n" not in cmds:
        return False
    if "Undefined header: UNKNOWN:HDR?" not in cmds:
        return False

    devices = json.loads(Verification.load_stream_text(extract_dir, "usbtmc.list"))
    return any(d.get("serial") == "custom-linux-usbtmc-0001" for d in devices)
```

### Receive 1 MiB over USBTMC

Request a fresh 1 MiB (1048576 bytes) PRBS payload over USBTMC while recording the
board console on UART throughout the transfer, read it host-side with streaming
CRC32 verification, and report achieved Mbps and core temperature. The console
must carry nothing but the temperature: the Verify permits only the bare temp
number before its sentinel, so any kernel message or Oops fails the section and
is dumped. No rate gate (overhead-dominated).

Build: nothing required.

Test (max 3 min):

```
mp135.custom:uart_open
delay ms=300
usbtmc.any:write serial="custom-linux-usbtmc-0001" data="DATA:PRBS? 1048576\n" timeout_ms=5000
usbtmc.any:read serial="custom-linux-usbtmc-0001" length=1048576 exact=true expect_crc32=0xe6568d53 timeout_ms=30000
delay ms=500
mp135.custom:uart_write data="cat /sys/class/thermal/thermal_zone0/temp; echo ENDOFTEMP\r"
mp135.custom:uart_expect sentinel="ENDOFTEMP" timeout_ms=4000
mp135.custom:uart_close
mark tag=usbtmc_sweep_1mib
```

Verify:

```
def check(extract_dir):
    import sys
    rate = temp = None
    try:
        crcs = [c for c in Verification.load_manifest(extract_dir).get("checks", [])
                if c.get("kind") == "usbtmc_read_crc32"]
        if crcs:
            ev = crcs[-1].get("evidence") or {}
            b, el = ev.get("bytes"), ev.get("elapsed_s")
            if b and el:
                rate = b * 8.0 / el / 1e6
    except Exception:
        pass
    uart = ""
    try:
        uart = Verification.load_stream_text(extract_dir, "mp135.uart")
    except Exception:
        pass
    # Shell echo is off, so everything on the console before the ENDOFTEMP
    # sentinel must be ONLY the bare temperature (a number). Empty is allowed
    # (temp simply not captured); anything else -- a kernel message or Oops --
    # is non-numeric, fails the section, and is dumped verbatim.
    pre = uart.split("ENDOFTEMP")[0].strip()
    clean = (pre == "" or pre.isdigit())
    if pre.isdigit():
        temp = int(pre) / 1000.0
    out = ""
    if rate is not None:
        out += "%.1fMbps " % rate
    if temp is not None:
        out += "%.1fC " % temp
    if not clean:
        out += "UART-UNEXPECTED[%dB] %s " % (len(pre), repr(pre[:220]))
    if out:
        sys.stderr.write(out); sys.stderr.flush()
    if not Verification.manifest_clean(extract_dir):
        return False
    if not clean:
        return False
    crcs = [c for c in Verification.load_manifest(extract_dir).get("checks", [])
            if c.get("kind") == "usbtmc_read_crc32"]
    return len(crcs) >= 1 and all(c.get("status") == "hit" for c in crcs)
```

### Receive 2 MiB over USBTMC

Request a fresh 2 MiB (2097152 bytes) PRBS payload over USBTMC while recording the
board console on UART throughout the transfer, read it host-side with streaming
CRC32 verification, and report achieved Mbps and core temperature. The console
must carry nothing but the temperature: the Verify permits only the bare temp
number before its sentinel, so any kernel message or Oops fails the section and
is dumped. No rate gate (overhead-dominated).

Build: nothing required.

Test (max 3 min):

```
mp135.custom:uart_open
delay ms=300
usbtmc.any:write serial="custom-linux-usbtmc-0001" data="DATA:PRBS? 2097152\n" timeout_ms=5000
usbtmc.any:read serial="custom-linux-usbtmc-0001" length=2097152 exact=true expect_crc32=0x10ea3bbe timeout_ms=30000
delay ms=500
mp135.custom:uart_write data="cat /sys/class/thermal/thermal_zone0/temp; echo ENDOFTEMP\r"
mp135.custom:uart_expect sentinel="ENDOFTEMP" timeout_ms=4000
mp135.custom:uart_close
mark tag=usbtmc_sweep_2mib
```

Verify:

```
def check(extract_dir):
    import sys
    rate = temp = None
    try:
        crcs = [c for c in Verification.load_manifest(extract_dir).get("checks", [])
                if c.get("kind") == "usbtmc_read_crc32"]
        if crcs:
            ev = crcs[-1].get("evidence") or {}
            b, el = ev.get("bytes"), ev.get("elapsed_s")
            if b and el:
                rate = b * 8.0 / el / 1e6
    except Exception:
        pass
    uart = ""
    try:
        uart = Verification.load_stream_text(extract_dir, "mp135.uart")
    except Exception:
        pass
    # Shell echo is off, so everything on the console before the ENDOFTEMP
    # sentinel must be ONLY the bare temperature (a number). Empty is allowed
    # (temp simply not captured); anything else -- a kernel message or Oops --
    # is non-numeric, fails the section, and is dumped verbatim.
    pre = uart.split("ENDOFTEMP")[0].strip()
    clean = (pre == "" or pre.isdigit())
    if pre.isdigit():
        temp = int(pre) / 1000.0
    out = ""
    if rate is not None:
        out += "%.1fMbps " % rate
    if temp is not None:
        out += "%.1fC " % temp
    if not clean:
        out += "UART-UNEXPECTED[%dB] %s " % (len(pre), repr(pre[:220]))
    if out:
        sys.stderr.write(out); sys.stderr.flush()
    if not Verification.manifest_clean(extract_dir):
        return False
    if not clean:
        return False
    crcs = [c for c in Verification.load_manifest(extract_dir).get("checks", [])
            if c.get("kind") == "usbtmc_read_crc32"]
    return len(crcs) >= 1 and all(c.get("status") == "hit" for c in crcs)
```

### Receive 4 MiB over USBTMC

Request a fresh 4 MiB (4194304 bytes) PRBS payload over USBTMC while recording the
board console on UART throughout the transfer, read it host-side with streaming
CRC32 verification, and report achieved Mbps and core temperature. The console
must carry nothing but the temperature: the Verify permits only the bare temp
number before its sentinel, so any kernel message or Oops fails the section and
is dumped. No rate gate (overhead-dominated).

Build: nothing required.

Test (max 3 min):

```
mp135.custom:uart_open
delay ms=300
usbtmc.any:write serial="custom-linux-usbtmc-0001" data="DATA:PRBS? 4194304\n" timeout_ms=5000
usbtmc.any:read serial="custom-linux-usbtmc-0001" length=4194304 exact=true expect_crc32=0xc832783e timeout_ms=30000
delay ms=500
mp135.custom:uart_write data="cat /sys/class/thermal/thermal_zone0/temp; echo ENDOFTEMP\r"
mp135.custom:uart_expect sentinel="ENDOFTEMP" timeout_ms=4000
mp135.custom:uart_close
mark tag=usbtmc_sweep_4mib
```

Verify:

```
def check(extract_dir):
    import sys
    rate = temp = None
    try:
        crcs = [c for c in Verification.load_manifest(extract_dir).get("checks", [])
                if c.get("kind") == "usbtmc_read_crc32"]
        if crcs:
            ev = crcs[-1].get("evidence") or {}
            b, el = ev.get("bytes"), ev.get("elapsed_s")
            if b and el:
                rate = b * 8.0 / el / 1e6
    except Exception:
        pass
    uart = ""
    try:
        uart = Verification.load_stream_text(extract_dir, "mp135.uart")
    except Exception:
        pass
    # Shell echo is off, so everything on the console before the ENDOFTEMP
    # sentinel must be ONLY the bare temperature (a number). Empty is allowed
    # (temp simply not captured); anything else -- a kernel message or Oops --
    # is non-numeric, fails the section, and is dumped verbatim.
    pre = uart.split("ENDOFTEMP")[0].strip()
    clean = (pre == "" or pre.isdigit())
    if pre.isdigit():
        temp = int(pre) / 1000.0
    out = ""
    if rate is not None:
        out += "%.1fMbps " % rate
    if temp is not None:
        out += "%.1fC " % temp
    if not clean:
        out += "UART-UNEXPECTED[%dB] %s " % (len(pre), repr(pre[:220]))
    if out:
        sys.stderr.write(out); sys.stderr.flush()
    if not Verification.manifest_clean(extract_dir):
        return False
    if not clean:
        return False
    crcs = [c for c in Verification.load_manifest(extract_dir).get("checks", [])
            if c.get("kind") == "usbtmc_read_crc32"]
    return len(crcs) >= 1 and all(c.get("status") == "hit" for c in crcs)
```

### Receive 8 MiB over USBTMC

Request a fresh 8 MiB (8388608 bytes) PRBS payload over USBTMC while recording the
board console on UART throughout the transfer, read it host-side with streaming
CRC32 verification, and report achieved Mbps and core temperature. The console
must carry nothing but the temperature: the Verify permits only the bare temp
number before its sentinel, so any kernel message or Oops fails the section and
is dumped. No rate gate (overhead-dominated).

Build: nothing required.

Test (max 3 min):

```
mp135.custom:uart_open
delay ms=300
usbtmc.any:write serial="custom-linux-usbtmc-0001" data="DATA:PRBS? 8388608\n" timeout_ms=5000
usbtmc.any:read serial="custom-linux-usbtmc-0001" length=8388608 exact=true expect_crc32=0xf1e9a5ef timeout_ms=30000
delay ms=500
mp135.custom:uart_write data="cat /sys/class/thermal/thermal_zone0/temp; echo ENDOFTEMP\r"
mp135.custom:uart_expect sentinel="ENDOFTEMP" timeout_ms=4000
mp135.custom:uart_close
mark tag=usbtmc_sweep_8mib
```

Verify:

```
def check(extract_dir):
    import sys
    rate = temp = None
    try:
        crcs = [c for c in Verification.load_manifest(extract_dir).get("checks", [])
                if c.get("kind") == "usbtmc_read_crc32"]
        if crcs:
            ev = crcs[-1].get("evidence") or {}
            b, el = ev.get("bytes"), ev.get("elapsed_s")
            if b and el:
                rate = b * 8.0 / el / 1e6
    except Exception:
        pass
    uart = ""
    try:
        uart = Verification.load_stream_text(extract_dir, "mp135.uart")
    except Exception:
        pass
    # Shell echo is off, so everything on the console before the ENDOFTEMP
    # sentinel must be ONLY the bare temperature (a number). Empty is allowed
    # (temp simply not captured); anything else -- a kernel message or Oops --
    # is non-numeric, fails the section, and is dumped verbatim.
    pre = uart.split("ENDOFTEMP")[0].strip()
    clean = (pre == "" or pre.isdigit())
    if pre.isdigit():
        temp = int(pre) / 1000.0
    out = ""
    if rate is not None:
        out += "%.1fMbps " % rate
    if temp is not None:
        out += "%.1fC " % temp
    if not clean:
        out += "UART-UNEXPECTED[%dB] %s " % (len(pre), repr(pre[:220]))
    if out:
        sys.stderr.write(out); sys.stderr.flush()
    if not Verification.manifest_clean(extract_dir):
        return False
    if not clean:
        return False
    crcs = [c for c in Verification.load_manifest(extract_dir).get("checks", [])
            if c.get("kind") == "usbtmc_read_crc32"]
    return len(crcs) >= 1 and all(c.get("status") == "hit" for c in crcs)
```

### Receive 16 MiB over USBTMC

Request a fresh 16 MiB (16777216 bytes) PRBS payload over USBTMC while recording the
board console on UART throughout the transfer, read it host-side with streaming
CRC32 verification, and report achieved Mbps and core temperature. The console
must carry nothing but the temperature: the Verify permits only the bare temp
number before its sentinel, so any kernel message or Oops fails the section and
is dumped. No rate gate (overhead-dominated).

Build: nothing required.

Test (max 3 min):

```
mp135.custom:uart_open
delay ms=300
usbtmc.any:write serial="custom-linux-usbtmc-0001" data="DATA:PRBS? 16777216\n" timeout_ms=5000
usbtmc.any:read serial="custom-linux-usbtmc-0001" length=16777216 exact=true expect_crc32=0xf89e248a timeout_ms=30000
delay ms=500
mp135.custom:uart_write data="cat /sys/class/thermal/thermal_zone0/temp; echo ENDOFTEMP\r"
mp135.custom:uart_expect sentinel="ENDOFTEMP" timeout_ms=4000
mp135.custom:uart_close
mark tag=usbtmc_sweep_16mib
```

Verify:

```
def check(extract_dir):
    import sys
    rate = temp = None
    try:
        crcs = [c for c in Verification.load_manifest(extract_dir).get("checks", [])
                if c.get("kind") == "usbtmc_read_crc32"]
        if crcs:
            ev = crcs[-1].get("evidence") or {}
            b, el = ev.get("bytes"), ev.get("elapsed_s")
            if b and el:
                rate = b * 8.0 / el / 1e6
    except Exception:
        pass
    uart = ""
    try:
        uart = Verification.load_stream_text(extract_dir, "mp135.uart")
    except Exception:
        pass
    # Shell echo is off, so everything on the console before the ENDOFTEMP
    # sentinel must be ONLY the bare temperature (a number). Empty is allowed
    # (temp simply not captured); anything else -- a kernel message or Oops --
    # is non-numeric, fails the section, and is dumped verbatim.
    pre = uart.split("ENDOFTEMP")[0].strip()
    clean = (pre == "" or pre.isdigit())
    if pre.isdigit():
        temp = int(pre) / 1000.0
    out = ""
    if rate is not None:
        out += "%.1fMbps " % rate
    if temp is not None:
        out += "%.1fC " % temp
    if not clean:
        out += "UART-UNEXPECTED[%dB] %s " % (len(pre), repr(pre[:220]))
    if out:
        sys.stderr.write(out); sys.stderr.flush()
    if not Verification.manifest_clean(extract_dir):
        return False
    if not clean:
        return False
    crcs = [c for c in Verification.load_manifest(extract_dir).get("checks", [])
            if c.get("kind") == "usbtmc_read_crc32"]
    return len(crcs) >= 1 and all(c.get("status") == "hit" for c in crcs)
```

### Receive 32 MiB over USBTMC

Request a fresh 32 MiB (33554432 bytes) PRBS payload over USBTMC while recording the
board console on UART throughout the transfer, read it host-side with streaming
CRC32 verification, and report achieved Mbps and core temperature. The console
must carry nothing but the temperature: the Verify permits only the bare temp
number before its sentinel, so any kernel message or Oops fails the section and
is dumped. No rate gate (overhead-dominated).

Build: nothing required.

Test (max 3 min):

```
mp135.custom:uart_open
delay ms=300
usbtmc.any:write serial="custom-linux-usbtmc-0001" data="DATA:PRBS? 33554432\n" timeout_ms=5000
usbtmc.any:read serial="custom-linux-usbtmc-0001" length=33554432 exact=true expect_crc32=0xe0a414c5 timeout_ms=30000
delay ms=500
mp135.custom:uart_write data="cat /sys/class/thermal/thermal_zone0/temp; echo ENDOFTEMP\r"
mp135.custom:uart_expect sentinel="ENDOFTEMP" timeout_ms=4000
mp135.custom:uart_close
mark tag=usbtmc_sweep_32mib
```

Verify:

```
def check(extract_dir):
    import sys
    rate = temp = None
    try:
        crcs = [c for c in Verification.load_manifest(extract_dir).get("checks", [])
                if c.get("kind") == "usbtmc_read_crc32"]
        if crcs:
            ev = crcs[-1].get("evidence") or {}
            b, el = ev.get("bytes"), ev.get("elapsed_s")
            if b and el:
                rate = b * 8.0 / el / 1e6
    except Exception:
        pass
    uart = ""
    try:
        uart = Verification.load_stream_text(extract_dir, "mp135.uart")
    except Exception:
        pass
    # Shell echo is off, so everything on the console before the ENDOFTEMP
    # sentinel must be ONLY the bare temperature (a number). Empty is allowed
    # (temp simply not captured); anything else -- a kernel message or Oops --
    # is non-numeric, fails the section, and is dumped verbatim.
    pre = uart.split("ENDOFTEMP")[0].strip()
    clean = (pre == "" or pre.isdigit())
    if pre.isdigit():
        temp = int(pre) / 1000.0
    out = ""
    if rate is not None:
        out += "%.1fMbps " % rate
    if temp is not None:
        out += "%.1fC " % temp
    if not clean:
        out += "UART-UNEXPECTED[%dB] %s " % (len(pre), repr(pre[:220]))
    if out:
        sys.stderr.write(out); sys.stderr.flush()
    if not Verification.manifest_clean(extract_dir):
        return False
    if not clean:
        return False
    crcs = [c for c in Verification.load_manifest(extract_dir).get("checks", [])
            if c.get("kind") == "usbtmc_read_crc32"]
    return len(crcs) >= 1 and all(c.get("status") == "hit" for c in crcs)
```

### Receive 64 MiB over USBTMC

Request a fresh 64 MiB (67108864 bytes) PRBS payload over USBTMC while recording the
board console on UART throughout the transfer, read it host-side with streaming
CRC32 verification, and report achieved Mbps and core temperature. The console
must carry nothing but the temperature: the Verify permits only the bare temp
number before its sentinel, so any kernel message or Oops fails the section and
is dumped. No rate gate (overhead-dominated).

Build: nothing required.

Test (max 3 min):

```
mp135.custom:uart_open
delay ms=300
usbtmc.any:write serial="custom-linux-usbtmc-0001" data="DATA:PRBS? 67108864\n" timeout_ms=5000
usbtmc.any:read serial="custom-linux-usbtmc-0001" length=67108864 exact=true expect_crc32=0x9bffbe60 timeout_ms=30000
delay ms=500
mp135.custom:uart_write data="cat /sys/class/thermal/thermal_zone0/temp; echo ENDOFTEMP\r"
mp135.custom:uart_expect sentinel="ENDOFTEMP" timeout_ms=4000
mp135.custom:uart_close
mark tag=usbtmc_sweep_64mib
```

Verify:

```
def check(extract_dir):
    import sys
    rate = temp = None
    try:
        crcs = [c for c in Verification.load_manifest(extract_dir).get("checks", [])
                if c.get("kind") == "usbtmc_read_crc32"]
        if crcs:
            ev = crcs[-1].get("evidence") or {}
            b, el = ev.get("bytes"), ev.get("elapsed_s")
            if b and el:
                rate = b * 8.0 / el / 1e6
    except Exception:
        pass
    uart = ""
    try:
        uart = Verification.load_stream_text(extract_dir, "mp135.uart")
    except Exception:
        pass
    # Shell echo is off, so everything on the console before the ENDOFTEMP
    # sentinel must be ONLY the bare temperature (a number). Empty is allowed
    # (temp simply not captured); anything else -- a kernel message or Oops --
    # is non-numeric, fails the section, and is dumped verbatim.
    pre = uart.split("ENDOFTEMP")[0].strip()
    clean = (pre == "" or pre.isdigit())
    if pre.isdigit():
        temp = int(pre) / 1000.0
    out = ""
    if rate is not None:
        out += "%.1fMbps " % rate
    if temp is not None:
        out += "%.1fC " % temp
    if not clean:
        out += "UART-UNEXPECTED[%dB] %s " % (len(pre), repr(pre[:220]))
    if out:
        sys.stderr.write(out); sys.stderr.flush()
    if not Verification.manifest_clean(extract_dir):
        return False
    if not clean:
        return False
    crcs = [c for c in Verification.load_manifest(extract_dir).get("checks", [])
            if c.get("kind") == "usbtmc_read_crc32"]
    return len(crcs) >= 1 and all(c.get("status") == "hit" for c in crcs)
```

### Receive 128 MiB over USBTMC

Request a fresh 128 MiB (134217728 bytes) PRBS payload over USBTMC while recording the
board console on UART throughout the transfer, read it host-side with streaming
CRC32 verification, and report achieved Mbps and core temperature. The console
must carry nothing but the temperature: the Verify permits only the bare temp
number before its sentinel, so any kernel message or Oops fails the section and
is dumped. The 90 Mbps rate gate applies.

Build: nothing required.

Test (max 3 min):

```
mp135.custom:uart_open
delay ms=300
usbtmc.any:write serial="custom-linux-usbtmc-0001" data="DATA:PRBS? 134217728\n" timeout_ms=5000
usbtmc.any:read serial="custom-linux-usbtmc-0001" length=134217728 exact=true expect_crc32=0xf48e5cf5 min_rate_Bps=11250000 timeout_ms=60000
delay ms=500
mp135.custom:uart_write data="cat /sys/class/thermal/thermal_zone0/temp; echo ENDOFTEMP\r"
mp135.custom:uart_expect sentinel="ENDOFTEMP" timeout_ms=4000
mp135.custom:uart_close
mark tag=usbtmc_sweep_128mib
```

Verify:

```
def check(extract_dir):
    import sys
    rate = temp = None
    try:
        crcs = [c for c in Verification.load_manifest(extract_dir).get("checks", [])
                if c.get("kind") == "usbtmc_read_crc32"]
        if crcs:
            ev = crcs[-1].get("evidence") or {}
            b, el = ev.get("bytes"), ev.get("elapsed_s")
            if b and el:
                rate = b * 8.0 / el / 1e6
    except Exception:
        pass
    uart = ""
    try:
        uart = Verification.load_stream_text(extract_dir, "mp135.uart")
    except Exception:
        pass
    # Shell echo is off, so everything on the console before the ENDOFTEMP
    # sentinel must be ONLY the bare temperature (a number). Empty is allowed
    # (temp simply not captured); anything else -- a kernel message or Oops --
    # is non-numeric, fails the section, and is dumped verbatim.
    pre = uart.split("ENDOFTEMP")[0].strip()
    clean = (pre == "" or pre.isdigit())
    if pre.isdigit():
        temp = int(pre) / 1000.0
    out = ""
    if rate is not None:
        out += "%.1fMbps " % rate
    if temp is not None:
        out += "%.1fC " % temp
    if not clean:
        out += "UART-UNEXPECTED[%dB] %s " % (len(pre), repr(pre[:220]))
    if out:
        sys.stderr.write(out); sys.stderr.flush()
    if not Verification.manifest_clean(extract_dir):
        return False
    if not clean:
        return False
    crcs = [c for c in Verification.load_manifest(extract_dir).get("checks", [])
            if c.get("kind") == "usbtmc_read_crc32"]
    return len(crcs) >= 1 and all(c.get("status") == "hit" for c in crcs)
```

### Receive 256 MiB over USBTMC

Request a fresh 256 MiB (268435456 bytes) PRBS payload over USBTMC while recording the
board console on UART throughout the transfer, read it host-side with streaming
CRC32 verification, and report achieved Mbps and core temperature. The console
must carry nothing but the temperature: the Verify permits only the bare temp
number before its sentinel, so any kernel message or Oops fails the section and
is dumped. The 90 Mbps rate gate applies.

Build: nothing required.

Test (max 3 min):

```
mp135.custom:uart_open
delay ms=300
usbtmc.any:write serial="custom-linux-usbtmc-0001" data="DATA:PRBS? 268435456\n" timeout_ms=5000
usbtmc.any:read serial="custom-linux-usbtmc-0001" length=268435456 exact=true expect_crc32=0x96e039fa min_rate_Bps=11250000 timeout_ms=90000
delay ms=500
mp135.custom:uart_write data="cat /sys/class/thermal/thermal_zone0/temp; echo ENDOFTEMP\r"
mp135.custom:uart_expect sentinel="ENDOFTEMP" timeout_ms=4000
mp135.custom:uart_close
mark tag=usbtmc_sweep_256mib
```

Verify:

```
def check(extract_dir):
    import sys
    rate = temp = None
    try:
        crcs = [c for c in Verification.load_manifest(extract_dir).get("checks", [])
                if c.get("kind") == "usbtmc_read_crc32"]
        if crcs:
            ev = crcs[-1].get("evidence") or {}
            b, el = ev.get("bytes"), ev.get("elapsed_s")
            if b and el:
                rate = b * 8.0 / el / 1e6
    except Exception:
        pass
    uart = ""
    try:
        uart = Verification.load_stream_text(extract_dir, "mp135.uart")
    except Exception:
        pass
    # Shell echo is off, so everything on the console before the ENDOFTEMP
    # sentinel must be ONLY the bare temperature (a number). Empty is allowed
    # (temp simply not captured); anything else -- a kernel message or Oops --
    # is non-numeric, fails the section, and is dumped verbatim.
    pre = uart.split("ENDOFTEMP")[0].strip()
    clean = (pre == "" or pre.isdigit())
    if pre.isdigit():
        temp = int(pre) / 1000.0
    out = ""
    if rate is not None:
        out += "%.1fMbps " % rate
    if temp is not None:
        out += "%.1fC " % temp
    if not clean:
        out += "UART-UNEXPECTED[%dB] %s " % (len(pre), repr(pre[:220]))
    if out:
        sys.stderr.write(out); sys.stderr.flush()
    if not Verification.manifest_clean(extract_dir):
        return False
    if not clean:
        return False
    crcs = [c for c in Verification.load_manifest(extract_dir).get("checks", [])
            if c.get("kind") == "usbtmc_read_crc32"]
    return len(crcs) >= 1 and all(c.get("status") == "hit" for c in crcs)
```

### Receive 512 MiB over USBTMC

Request a fresh 512 MiB (536870912 bytes) PRBS payload over USBTMC while recording the
board console on UART throughout the transfer, read it host-side with streaming
CRC32 verification, and report achieved Mbps and core temperature. The console
must carry nothing but the temperature: the Verify permits only the bare temp
number before its sentinel, so any kernel message or Oops fails the section and
is dumped. The 90 Mbps rate gate applies.

Build: nothing required.

Test (max 4 min):

```
mp135.custom:uart_open
delay ms=300
usbtmc.any:write serial="custom-linux-usbtmc-0001" data="DATA:PRBS? 536870912\n" timeout_ms=5000
usbtmc.any:read serial="custom-linux-usbtmc-0001" length=536870912 exact=true expect_crc32=0xa05a6a2f min_rate_Bps=11250000 timeout_ms=150000
delay ms=500
mp135.custom:uart_write data="cat /sys/class/thermal/thermal_zone0/temp; echo ENDOFTEMP\r"
mp135.custom:uart_expect sentinel="ENDOFTEMP" timeout_ms=4000
mp135.custom:uart_close
mark tag=usbtmc_sweep_512mib
```

Verify:

```
def check(extract_dir):
    import sys
    rate = temp = None
    try:
        crcs = [c for c in Verification.load_manifest(extract_dir).get("checks", [])
                if c.get("kind") == "usbtmc_read_crc32"]
        if crcs:
            ev = crcs[-1].get("evidence") or {}
            b, el = ev.get("bytes"), ev.get("elapsed_s")
            if b and el:
                rate = b * 8.0 / el / 1e6
    except Exception:
        pass
    uart = ""
    try:
        uart = Verification.load_stream_text(extract_dir, "mp135.uart")
    except Exception:
        pass
    # Shell echo is off, so everything on the console before the ENDOFTEMP
    # sentinel must be ONLY the bare temperature (a number). Empty is allowed
    # (temp simply not captured); anything else -- a kernel message or Oops --
    # is non-numeric, fails the section, and is dumped verbatim.
    pre = uart.split("ENDOFTEMP")[0].strip()
    clean = (pre == "" or pre.isdigit())
    if pre.isdigit():
        temp = int(pre) / 1000.0
    out = ""
    if rate is not None:
        out += "%.1fMbps " % rate
    if temp is not None:
        out += "%.1fC " % temp
    if not clean:
        out += "UART-UNEXPECTED[%dB] %s " % (len(pre), repr(pre[:220]))
    if out:
        sys.stderr.write(out); sys.stderr.flush()
    if not Verification.manifest_clean(extract_dir):
        return False
    if not clean:
        return False
    crcs = [c for c in Verification.load_manifest(extract_dir).get("checks", [])
            if c.get("kind") == "usbtmc_read_crc32"]
    return len(crcs) >= 1 and all(c.get("status") == "hit" for c in crcs)
```

### Receive 1024 MiB over USBTMC

Request a fresh 1024 MiB (1073741824 bytes) PRBS payload over USBTMC while recording the
board console on UART throughout the transfer, read it host-side with streaming
CRC32 verification, and report achieved Mbps and core temperature. The console
must carry nothing but the temperature: the Verify permits only the bare temp
number before its sentinel, so any kernel message or Oops fails the section and
is dumped. The 90 Mbps rate gate applies.

Build: nothing required.

Test (max 6 min):

```
mp135.custom:uart_open
delay ms=300
usbtmc.any:write serial="custom-linux-usbtmc-0001" data="DATA:PRBS? 1073741824\n" timeout_ms=5000
usbtmc.any:read serial="custom-linux-usbtmc-0001" length=1073741824 exact=true expect_crc32=0x501f0d96 min_rate_Bps=11250000 timeout_ms=240000
delay ms=500
mp135.custom:uart_write data="cat /sys/class/thermal/thermal_zone0/temp; echo ENDOFTEMP\r"
mp135.custom:uart_expect sentinel="ENDOFTEMP" timeout_ms=4000
mp135.custom:uart_close
mark tag=usbtmc_sweep_1024mib
```

Verify:

```
def check(extract_dir):
    import sys
    rate = temp = None
    try:
        crcs = [c for c in Verification.load_manifest(extract_dir).get("checks", [])
                if c.get("kind") == "usbtmc_read_crc32"]
        if crcs:
            ev = crcs[-1].get("evidence") or {}
            b, el = ev.get("bytes"), ev.get("elapsed_s")
            if b and el:
                rate = b * 8.0 / el / 1e6
    except Exception:
        pass
    uart = ""
    try:
        uart = Verification.load_stream_text(extract_dir, "mp135.uart")
    except Exception:
        pass
    # Shell echo is off, so everything on the console before the ENDOFTEMP
    # sentinel must be ONLY the bare temperature (a number). Empty is allowed
    # (temp simply not captured); anything else -- a kernel message or Oops --
    # is non-numeric, fails the section, and is dumped verbatim.
    pre = uart.split("ENDOFTEMP")[0].strip()
    clean = (pre == "" or pre.isdigit())
    if pre.isdigit():
        temp = int(pre) / 1000.0
    out = ""
    if rate is not None:
        out += "%.1fMbps " % rate
    if temp is not None:
        out += "%.1fC " % temp
    if not clean:
        out += "UART-UNEXPECTED[%dB] %s " % (len(pre), repr(pre[:220]))
    if out:
        sys.stderr.write(out); sys.stderr.flush()
    if not Verification.manifest_clean(extract_dir):
        return False
    if not clean:
        return False
    crcs = [c for c in Verification.load_manifest(extract_dir).get("checks", [])
            if c.get("kind") == "usbtmc_read_crc32"]
    return len(crcs) >= 1 and all(c.get("status") == "hit" for c in crcs)
```

### Receive 512 MiB x10 over USBTMC (rate + temp, console must stay clean)

Request and read the 512 MiB PRBS payload ten times back-to-back over USBTMC, with
the console recorded on UART throughout every iteration. Each iteration CRC32-
verifies the payload, reports rate and core temperature, and permits only the bare
temperature on the console -- so corruption or a kernel Oops under sustained USB
load is caught and dumped across the ten runs. The 90 Mbps gate applies.

Build: nothing required.

Foreach:

```
i in count(10)
```

Test (max 4 min):

```
mp135.custom:uart_open
delay ms=300
usbtmc.any:write serial="custom-linux-usbtmc-0001" data="DATA:PRBS? 536870912\n" timeout_ms=5000
usbtmc.any:read serial="custom-linux-usbtmc-0001" length=536870912 exact=true expect_crc32=0xa05a6a2f min_rate_Bps=11250000 timeout_ms=150000
delay ms=500
mp135.custom:uart_write data="cat /sys/class/thermal/thermal_zone0/temp; echo ENDOFTEMP\r"
mp135.custom:uart_expect sentinel="ENDOFTEMP" timeout_ms=4000
mp135.custom:uart_close
mark tag=usbtmc_512_loop
```

Verify:

```
def check(extract_dir, item):
    import sys
    rate = temp = None
    try:
        crcs = [c for c in Verification.load_manifest(extract_dir).get("checks", [])
                if c.get("kind") == "usbtmc_read_crc32"]
        if crcs:
            ev = crcs[-1].get("evidence") or {}
            b, el = ev.get("bytes"), ev.get("elapsed_s")
            if b and el:
                rate = b * 8.0 / el / 1e6
    except Exception:
        pass
    uart = ""
    try:
        uart = Verification.load_stream_text(extract_dir, "mp135.uart")
    except Exception:
        pass
    # Shell echo is off, so everything on the console before the ENDOFTEMP
    # sentinel must be ONLY the bare temperature (a number). Empty is allowed
    # (temp simply not captured); anything else -- a kernel message or Oops --
    # is non-numeric, fails the section, and is dumped verbatim.
    pre = uart.split("ENDOFTEMP")[0].strip()
    clean = (pre == "" or pre.isdigit())
    if pre.isdigit():
        temp = int(pre) / 1000.0
    out = "iter %s: " % item
    if rate is not None:
        out += "%.1fMbps " % rate
    if temp is not None:
        out += "%.1fC " % temp
    if not clean:
        out += "UART-UNEXPECTED[%dB] %s " % (len(pre), repr(pre[:220]))
    if out:
        sys.stderr.write(out); sys.stderr.flush()
    if not Verification.manifest_clean(extract_dir):
        return False
    if not clean:
        return False
    crcs = [c for c in Verification.load_manifest(extract_dir).get("checks", [])
            if c.get("kind") == "usbtmc_read_crc32"]
    return len(crcs) >= 1 and all(c.get("status") == "hit" for c in crcs)
```
