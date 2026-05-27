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
        "dfu": {"flash_layout"},
        "msc": {"write", "verify"},
        "mp135": {"uart_open", "uart_write", "uart_expect", "uart_close"},
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

### Build EVB Linux USBTMC Image

Build the EVB Linux image with the minimal pieces needed for Linux to
configure the USB device controller and expose the USBTMC implementation.
This section does not touch hardware.

Build:

```
make -C stm32mp135_test_board patch
make -C stm32mp135_test_board br
make -C stm32mp135_test_board/bootloader clean
make -C stm32mp135_test_board/bootloader -j$(nproc) CFLAGS_EXTRA=-DEVB
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

Test: no hardware.

Verify:

```
from pathlib import Path

def check(_extract_dir):
    return (
        Path("stm32mp135_test_board/bootloader/scripts/flash.tsv").is_file()
        and Path("stm32mp135_test_board/bootloader/build/main.stm32").stat().st_size > 0
        and Path("stm32mp135_test_board/buildroot/output/images/sdcard.img").stat().st_size > 0
    )
```

### EVB Linux Gadget Baseline

Boot EVB Linux and prove that Linux, not ROM DFU or the bare-metal MSC
bootloader, owns the USB device controller. A known in-tree gadget such
as mass-storage is enough for this baseline; this is only a UDC,
configfs, and cable-path proof.

Build: nothing required.

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/sdcard.img
```

Test (max 5 min):

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
msc.evb:verify data=@sdcard.img offset_lba=0 min_rate_Bps=3000000
mp135.evb:uart_open
delay ms=300
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="> " timeout_ms=5000
mp135.evb:uart_write data="two\r"
mp135.evb:uart_expect sentinel="> " timeout_ms=15000
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
mp135.evb:uart_write data="test -d /sys/kernel/config/usb_gadget && echo USB_GADGET_CONFIGFS_OK\r"
mp135.evb:uart_expect sentinel="USB_GADGET_CONFIGFS_OK" timeout_ms=5000
mp135.evb:uart_write data="test -e /sys/class/udc/49000000.usb && echo USB_UDC_PRESENT_OK\r"
mp135.evb:uart_expect sentinel="USB_UDC_PRESENT_OK" timeout_ms=5000
mp135.evb:uart_write data="s=$(cat /sys/class/udc/49000000.usb/state 2>/dev/null); echo USB_UDC_STATE_$s\r"
mp135.evb:uart_expect sentinel="USB_UDC_STATE_" timeout_ms=5000
mp135.evb:uart_close
usb.host:descriptor vendor=0x0483 product=0x571e class=0x00 configured=true
mark tag=evb_linux_gadget_baseline
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    uart = Verification.load_stream_text(extract_dir, "mp135.uart")
    return (
        Verification.op_succeeded(ops, "dfu.evb", "flash_layout")
        and Verification.op_succeeded(ops, "msc.evb", "verify")
        and "USB_GADGET_CONFIGFS_OK" in uart
        and "USB_UDC_PRESENT_OK" in uart
    )
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

Build:

```
make -C stm32mp135_test_board br
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

Test: boot EVB Linux, wait for the Linux-created USB gadget to
enumerate, capture host-side descriptors, and issue the USBTMC and
USB488 capability requests from the host.

Verify: the manifest is clean, descriptor fields and endpoint counts
match the USBTMC USB488 contract, no mass-storage interface remains
exposed, and capability requests return valid success responses.

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

Build:

```
make -C stm32mp135_test_board br
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

Test: boot EVB Linux, verify USBTMC enumeration, then issue the command
suite from the host through USBTMC-framed bulk transfers.

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

Test: boot EVB Linux, verify USBTMC enumeration, transfer deterministic
PRBS payloads in both supported directions using USBTMC headers, and
have the host verify length, SHA-256, and CRC32 without trusting
target-side summaries.

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

Test: boot EVB Linux, verify USBTMC enumeration, transfer a large
deterministic payload, and record wall-clock throughput at the host.

Verify: SHA-256 and CRC32 match the expected PRBS digest, the full byte
count is received, and host-observed throughput is at least the mission
floor selected during implementation.

### Custom Board USBTMC Parity

Run the completed USBTMC behavior on the custom board. The custom board
must enumerate as USBTMC, answer the command suite, preserve binary
payload integrity, and meet the same throughput floor unless the mission
explicitly documents a board-specific hardware limit.

Build:

```
make -C stm32mp135_test_board br
make -C stm32mp135_test_board/bootloader clean
make -C stm32mp135_test_board/bootloader -j$(nproc)
make -C stm32mp135_test_board kernel
make -C stm32mp135_test_board DTS=custom dtb
make -C stm32mp135_test_board DTS=custom sd
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/sdcard.img
```

Test: boot the custom-board Linux image, verify host-side USBTMC
enumeration, run the command suite, run binary integrity transfers, and
run the sustained throughput transfer.

Verify: descriptor enumeration passes, all command responses match,
binary transfers are bit-perfect, throughput meets the selected floor,
and the UART transcript contains no USB gadget, UDC, or endpoint errors.
