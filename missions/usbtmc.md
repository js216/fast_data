# USBTMC Gadget From STM32MP135 Linux

Prove that Linux on STM32MP135 owns the USB device controller after
boot and exposes a real USB Test & Measurement Class instrument to the
bench host.

The pass condition is:

- the board boots the Linux image built by this tree,
- ROM DFU and the bare-metal MSC bootloader are no longer the active
  USB device once Linux starts,
- Linux configures the STM32MP135 UDC as a USBTMC-capable gadget,
- the host sees a USBTMC USB488 interface descriptor and endpoints,
- required USBTMC/USB488 control requests return valid status packets,
- USBTMC bulk transfers use proper message headers, tags, EOM, and
  transfer-size fields,
- mandatory USB488 common commands return deterministic responses,
- invalid or unsupported commands return a controlled error,
- binary payload transfers are bit-perfect, and
- sustained USBTMC bulk throughput meets the mission floor.

Kernel source must not be edited in place; out-of-tree driver or
support code belongs under `stm32mp135_test_board/config/drivers`, and
boot-time setup belongs in board configuration or the rootfs overlay.

### Inventory Exposes USB Gadget Test Surface

Confirm the bench exposes the devices and operations needed to boot the
EVB, write its SD image, control UART, and inspect the host-side USB
device created by Linux.

Build: nothing required.

Test (max 30 s):

```
inventory
mark tag=usbtmc_inventory
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
    needed_devices = {"bench_mcu.0", "mp135.evb"}
    if not needed_devices.issubset(device_ids):
        return False

    ops = json.loads(Path(extract_dir, "bench.ops.json").read_text())
    required_ops = {
        "bench_mcu": {"reset_dut"},
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

    # The concrete host-side USB operation names may be added while this
    # mission is implemented. Inventory must at least advertise a USB
    # plugin namespace so the later tests can be made machine-checkable.
    return any(k == "usb" or k.startswith("usb.") for k in ops)
```

### Build EVB Base USBTMC Inputs

Prepare the EVB kernel tree, Buildroot output, and EVB bootloader input
needed by the final image packaging step. This section does not touch
hardware.

Build:

```
make -C stm32mp135_test_board patch
make -C stm32mp135_test_board br
make -C stm32mp135_test_board/bootloader clean
make -C stm32mp135_test_board/bootloader -j$(nproc) CFLAGS_EXTRA=-DEVB
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

### Package EVB Linux USBTMC Image

Build the EVB kernel image, install the USBTMC gadget daemon in the
rootfs, and package the final SD image. This section does not touch
hardware.

Build:

```
make -C stm32mp135_test_board kernel
make -C stm32mp135_test_board DTS=stm32mp135f-dk dtb
make -C stm32mp135_test_board usbtmc-gadget
make -C stm32mp135_test_board rootfs
make -C stm32mp135_test_board DTS=stm32mp135f-dk sd
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

### Write EVB SD Image

Flash the EVB bootloader, stop at the bootloader prompt, and write the
prepared SD image over MSC. This section does not verify or boot Linux.

Build: nothing required.

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/sdcard.img
```

Test (max 1 min):

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
msc.evb:write data=@sdcard.img offset_lba=0 min_rate_Bps=3000000
mark tag=evb_sd_written
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    return (
        Verification.op_succeeded(ops, "dfu.evb", "flash_layout")
        and Verification.op_succeeded(ops, "msc.evb", "write")
    )
```

### Verify EVB SD Image And Load Linux

Verify the already-written EVB SD image, then load Linux/DTB with
`two`. This section does not jump into Linux.

Build: nothing required.

Artifacts:

```
stm32mp135_test_board/buildroot/output/images/sdcard.img
```

Test (inherits the bootloader-at-`> ` state and written SD image from
the previous section; max 1 min):

```
msc.evb:verify data=@sdcard.img offset_lba=0 min_rate_Bps=3000000
mp135.evb:uart_open
delay ms=300
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="> " timeout_ms=5000
mp135.evb:uart_write data="two\r"
mp135.evb:uart_expect sentinel="> " timeout_ms=15000
mp135.evb:uart_close
mark tag=evb_sd_verified_linux_loaded
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    return Verification.op_succeeded(ops, "msc.evb", "verify")
```

### Boot EVB Linux Gadget Baseline

Boot EVB Linux from the already-written SD image and prove that Linux,
not ROM DFU or the bare-metal MSC bootloader, owns the USB device
controller. This section starts at `jump` and ends at the Linux login.

Build: nothing required.

Artifacts:

```
stm32mp135_test_board/buildroot/output/images/sdcard.img
```

Test (inherits the loaded Linux/DTB-at-`> ` state and written SD image
from the previous section; max 1 min):

```
mp135.evb:uart_open
delay ms=300
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="> " timeout_ms=5000
mp135.evb:uart_write data="jump\r"
mp135.evb:uart_expect sentinel="Jumping to address" timeout_ms=5000
mp135.evb:uart_expect sentinel="Linux version" timeout_ms=10000
mp135.evb:uart_expect sentinel="Welcome to STM32MP135 EVB" timeout_ms=10000
mp135.evb:uart_expect sentinel="login:" timeout_ms=15000
mp135.evb:uart_write data="root\r"
mp135.evb:uart_expect sentinel="Password:" timeout_ms=5000
mp135.evb:uart_write data="root\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=5000
mp135.evb:uart_write data="dmesg -n 1 2>/dev/null; true\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data="test -s /run/usbtmc_gadget.ready && echo USBTMC_READY_OK\r"
mp135.evb:uart_expect sentinel="USBTMC_READY_OK" timeout_ms=5000
mp135.evb:uart_write data="set -- /sys/class/udc/*; udc=${1##*/}; echo MANUFACTURER_$(cat /sys/kernel/config/usb_gadget/usbtmc/strings/0x409/manufacturer); echo SERIAL_$(cat /sys/kernel/config/usb_gadget/usbtmc/strings/0x409/serialnumber); echo VID_$(cat /sys/kernel/config/usb_gadget/usbtmc/idVendor); echo PID_$(cat /sys/kernel/config/usb_gadget/usbtmc/idProduct); echo UDC_NAME_$udc; echo UDC_STATE_$(cat /sys/class/udc/$udc/state 2>/dev/null); echo ___USBTMC_EVB_SYSFS_DONE___\r"
mp135.evb:uart_expect sentinel="MANUFACTURER_STMicroelectronics" timeout_ms=5000
mp135.evb:uart_expect sentinel="SERIAL_evb-linux-usbtmc-0001" timeout_ms=5000
mp135.evb:uart_expect sentinel="VID_0x0483" timeout_ms=5000
mp135.evb:uart_expect sentinel="PID_0x571e" timeout_ms=5000
mp135.evb:uart_expect sentinel="UDC_STATE_configured" timeout_ms=5000
mp135.evb:uart_expect sentinel="___USBTMC_EVB_SYSFS_DONE___" timeout_ms=5000
mp135.evb:uart_close
mark tag=evb_linux_gadget_baseline
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    uart = Verification.load_stream_text(extract_dir, "mp135.uart")
    for s in [
        "USBTMC_READY_OK",
        "MANUFACTURER_STMicroelectronics",
        "SERIAL_evb-linux-usbtmc-0001",
        "VID_0x0483",
        "PID_0x571e",
        "UDC_STATE_configured",
    ]:
        if s not in uart:
            return False
    return True
```

### EVB USBTMC Enumeration And Capabilities

Replace the baseline gadget with the USBTMC implementation. The host
must see one USBTMC USB488 interface:

- `bInterfaceClass = 0xfe`,
- `bInterfaceSubClass = 0x03`,
- `bInterfaceProtocol = 0x01`,
- exactly one bulk OUT endpoint,
- exactly one bulk IN endpoint,
- exactly one interrupt IN endpoint for 488.2 status reporting, and
- no mass-storage interface.

The host must also issue `GET_CAPABILITIES` and verify a successful
USBTMC status byte, `bcdUSBTMC >= 0x0100`, USB488 capability fields
consistent with the descriptor, and reserved bytes/bits cleared.

Build: nothing required; this section reuses the EVB image built in
`Build EVB Linux USBTMC Image`.

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/sdcard.img
```

Test (inherits the booted EVB Linux USBTMC gadget from the previous
section; max 30 s):

```
delay ms=1500
inventory refresh=true verify=false
usbtmc.any:list
dmesg.any:tail lines=300 timeout_ms=5000
mark tag=evb_usbtmc_enumeration
```

Verify:

```
def check(extract_dir):
    import json

    if not Verification.manifest_clean(extract_dir):
        return False

    devices = json.loads(Verification.load_stream_text(extract_dir, "usbtmc.list"))
    evb_devices = [
        d for d in devices
        if d.get("serial") == "evb-linux-usbtmc-0001"
    ]
    if len(evb_devices) != 1:
        return False
    dev = evb_devices[0]
    expected = {
        "manufacturer": "STMicroelectronics",
        "pid": "571e",
        "product": "STM32MP135 Linux USBTMC",
        "serial": "evb-linux-usbtmc-0001",
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
        "SerialNumber: evb-linux-usbtmc-0001",
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

### EVB USBTMC Command Behavior

Verify the minimum USB488 instrument command contract through USBTMC
bulk messages, not raw USB bulk bytes. Host requests must use
`DEV_DEP_MSG_OUT` and `REQUEST_DEV_DEP_MSG_IN` with valid `bTag`,
inverse tag, transfer size, EOM, and required alignment padding.

The command suite must cover:

- `*IDN?` returns a deterministic identification string,
- `*CLS` clears status,
- `*ESE` and `*ESE?` set and report the standard-event enable mask,
- `*ESR?` reports and clears the standard event register,
- `*RST` succeeds and leaves the instrument responsive,
- `*OPC` completes,
- `*OPC?` returns completion,
- `*SRE` and `*SRE?` set and report the service-request enable mask,
- `*STB?` reports the status byte,
- `*TRG` and USB488 `TRIGGER` are accepted,
- `*TST?` returns a deterministic self-test result,
- `*WAI` completes,
- an unsupported command records a controlled error, and
- `SYST:ERR?` reports and clears that error.

Build: nothing required; this section reuses the booted EVB Linux
USBTMC gadget from the previous section.

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/sdcard.img
```

Test: reuse the booted EVB Linux USBTMC gadget, verify enumeration,
then issue the command suite from the host through USBTMC-framed bulk
transfers.

Verify: every response exactly matches the mission contract and the
device remains responsive after the invalid-command path.

### EVB USBTMC Binary Integrity

Transfer deterministic binary payloads through USBTMC-framed bulk
messages and verify exact contents. Payload sizes should cover small
control-like messages, one USB packet, multiple packets, transfer sizes
that require USBTMC alignment padding, and at least one multi-megabyte
transfer.

Build: nothing required.

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/sdcard.img
```

Test: reuse the booted EVB Linux USBTMC gadget, verify enumeration,
transfer deterministic PRBS payloads in both supported directions using
USBTMC headers, and have the host verify length, SHA-256, and CRC32
without trusting target-side summaries.

Verify: every tested payload is bit-perfect and no USBTMC transfer
wedges the device.

### EVB USBTMC Sustained Throughput

Measure the real host-observed throughput of a large USBTMC binary
transfer while still enforcing bit-perfect integrity.

Build: nothing required.

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/sdcard.img
```

Test: reuse the booted EVB Linux USBTMC gadget, verify enumeration,
transfer a large deterministic payload, and record wall-clock
throughput at the host.

Verify: SHA-256 and CRC32 match the expected PRBS digest, the full byte
count is received, and host-observed throughput is at least the mission
floor selected during implementation.
