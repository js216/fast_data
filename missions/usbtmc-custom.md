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

Prepare the custom-board kernel tree, Buildroot output, and custom
bootloader input needed by the final image packaging step. This section
does not touch hardware.

Build:

```
make -C stm32mp135_test_board patch
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

Build the custom-board kernel image, install the USBTMC gadget daemon in
the rootfs, and package the final SD image. This section does not touch
hardware.

Build:

```
make -C stm32mp135_test_board kernel
make -C stm32mp135_test_board DTS=custom dtb
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
mp135.custom:uart_write data="dmesg -n 1 2>/dev/null; true\r"
mp135.custom:uart_expect sentinel="# " timeout_ms=3000
mp135.custom:uart_write data="test -s /run/usbtmc_gadget.ready && echo USBTMC_READY_OK\r"
mp135.custom:uart_expect sentinel="USBTMC_READY_OK" timeout_ms=5000
mp135.custom:uart_write data="set -- /sys/class/udc/*; udc=${1##*/}; echo MANUFACTURER_$(cat /sys/kernel/config/usb_gadget/usbtmc/strings/0x409/manufacturer); echo SERIAL_$(cat /sys/kernel/config/usb_gadget/usbtmc/strings/0x409/serialnumber); echo VID_$(cat /sys/kernel/config/usb_gadget/usbtmc/idVendor); echo PID_$(cat /sys/kernel/config/usb_gadget/usbtmc/idProduct); echo UDC_NAME_$udc; echo UDC_STATE_$(cat /sys/class/udc/$udc/state 2>/dev/null); echo ___USBTMC_CUSTOM_SYSFS_DONE___\r"
mp135.custom:uart_expect sentinel="STMicroelectronics" timeout_ms=5000
mp135.custom:uart_expect sentinel="SERIAL_custom-linux-usbtmc-0001" timeout_ms=5000
mp135.custom:uart_expect sentinel="VID_0x0483" timeout_ms=5000
mp135.custom:uart_expect sentinel="PID_0x571e" timeout_ms=5000
mp135.custom:uart_expect sentinel="UDC_STATE_configured" timeout_ms=5000
mp135.custom:uart_expect sentinel="___USBTMC_CUSTOM_SYSFS_DONE___" timeout_ms=5000
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

### Custom Board USBTMC Command And Data Parity

Run the completed USBTMC command behavior, binary integrity, and
sustained throughput checks on the already-booted custom board.

Build: nothing required.

Test: reuse the booted custom Linux USBTMC gadget, verify host-side
USBTMC enumeration, run the command suite, run binary integrity
transfers, and run the sustained throughput transfer.

Verify: descriptor enumeration passes, all command responses match,
binary transfers are bit-perfect, throughput meets the selected floor,
and the UART transcript contains no USB gadget, UDC, or endpoint errors.
