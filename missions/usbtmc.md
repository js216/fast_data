# USB Test & Measurement Class from kernel

Bring up the STM32MP135 USB device port under Linux and implement a
USBTMC gadget-style device without modifying the kernel source tree in
place. New out-of-tree driver or support code belongs under
`stm32mp135_test_board/config/drivers`; boot-time setup belongs in the
board configuration or rootfs overlay. The USBTMC specification is
available at `temp/USBTMC_1_006a.zip`.

The same physical USB interface is used by ROM DFU and the bare-metal
MSC bootloader before Linux starts. The mission proves that Linux can
take ownership of that interface after boot, then progresses from a
known in-tree gadget function to USBTMC-shaped enumeration, simple
instrument commands, and sustained bulk transfer. Test the EVB first,
then repeat the completed behavior on the custom board.

### EVB Linux configfs availability

Enable only the minimum EVB Linux pieces needed for userspace to mount
configfs and expose the USB gadget configfs directory. Boot the EVB
image far enough for that setup to run and record target artefacts
proving configfs is mounted and `/sys/kernel/config/usb_gadget` is
available. Do not create a backing file, gadget function, configuration
link, or UDC binding in this step.

Build:

```
make -C stm32mp135_test_board patch
make -C stm32mp135_test_board/bootloader -j$(nproc)
make -C stm32mp135_test_board kernel
make -C stm32mp135_test_board DTS=stm32mp135f-dk dtb
make -C stm32mp135_test_board br
make -C stm32mp135_test_board DTS=stm32mp135f-dk sd
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/sdcard.img
```

Test (max 15 min):

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
msc.evb:write data=@sdcard.img offset_lba=0
msc.evb:verify data=@sdcard.img offset_lba=0
mp135.evb:uart_open
delay ms=300
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="> " timeout_ms=5000
mp135.evb:uart_write data="two\r"
mp135.evb:uart_expect sentinel="> " timeout_ms=15000
mp135.evb:uart_write data="jump"
delay ms=200
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="Jumping to address" timeout_ms=5000
mp135.evb:uart_expect sentinel="Linux version" timeout_ms=10000
mp135.evb:uart_expect sentinel="Welcome to STM32MP135 EVB" timeout_ms=10000
mp135.evb:uart_expect sentinel="login:" timeout_ms=15000
mp135.evb:uart_write data="root\r"
mp135.evb:uart_expect sentinel="Password:" timeout_ms=5000
mp135.evb:uart_write data="root\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=5000
mp135.evb:uart_write data="if mountpoint -q /sys/kernel/config && grep -q ' /sys/kernel/config configfs ' /proc/mounts && test -d /sys/kernel/config/usb_gadget; then printf 'CONFIGFS_OK\\n'; printf 'configfs '; grep ' /sys/kernel/config configfs ' /proc/mounts; printf 'usb_gadget_dir '; ls -ld /sys/kernel/config/usb_gadget; else printf 'CONFIGFS_FAIL\\n'; cat /proc/mounts; ls -ld /sys/kernel/config /sys/kernel/config/usb_gadget; fi\r"
mp135.evb:uart_expect sentinel="usb_gadget_dir " timeout_ms=5000
mp135.evb:uart_close
mark tag=evb_configfs_usb_gadget
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    out = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    return (Verification.op_succeeded(ops, 'dfu.evb', 'flash_layout') and
            Verification.op_succeeded(ops, 'msc.evb', 'verify') and
            Verification.op_succeeded(ops, 'mp135.evb', 'uart_expect') and
            'CONFIGFS_OK' in out and
            ' /sys/kernel/config configfs ' in out and
            'usb_gadget_dir ' in out)
```

### EVB Linux MSC backing file

Add only the target-side boot-time creation of
`/var/lib/usbtmc/msc-backing.bin`, a deterministic 4096-byte regular
file that will later back the mass-storage function. The file content
must begin with the ASCII marker `USBTMC EVB MSC BACKING\n`; remaining
bytes may be zero padding. This step depends on configfs availability
but must not create a gadget function, gadget directory, configuration
link, or UDC binding.

Build:

```
make -C stm32mp135_test_board patch
make -C stm32mp135_test_board/bootloader -j$(nproc)
make -C stm32mp135_test_board kernel
make -C stm32mp135_test_board DTS=stm32mp135f-dk dtb
make -C stm32mp135_test_board br
make -C stm32mp135_test_board DTS=stm32mp135f-dk sd
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/buildroot/output/images/sdcard.img
```

Test (max 15 min):

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
msc.evb:write data=@sdcard.img offset_lba=0
msc.evb:verify data=@sdcard.img offset_lba=0
mp135.evb:uart_open
delay ms=300
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="> " timeout_ms=5000
mp135.evb:uart_write data="two\r"
mp135.evb:uart_expect sentinel="> " timeout_ms=15000
mp135.evb:uart_write data="jump"
delay ms=200
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="Jumping to address" timeout_ms=5000
mp135.evb:uart_expect sentinel="Linux version" timeout_ms=10000
mp135.evb:uart_expect sentinel="Welcome to STM32MP135 EVB" timeout_ms=10000
mp135.evb:uart_expect sentinel="login:" timeout_ms=15000
mp135.evb:uart_write data="root\r"
mp135.evb:uart_expect sentinel="Password:" timeout_ms=5000
mp135.evb:uart_write data="root\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=5000
mp135.evb:uart_write data="p=/var/lib/usbtmc/msc-backing.bin\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data="g=/sys/kernel/config/usb_gadget/usbtmc\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data="test -f $p&&printf M&&printf SC_BACKING_FILE_OK;echo\r"
mp135.evb:uart_expect sentinel="MSC_BACKING_FILE_OK" timeout_ms=5000
mp135.evb:uart_write data='s=$(wc -c < $p 2>/dev/null);printf M;printf SC_BACKING_SIZE_%s "$s";echo\r'
mp135.evb:uart_expect sentinel="MSC_BACKING_SIZE_4096" timeout_ms=5000
mp135.evb:uart_write data='m=$(dd if=$p bs=22 count=1 2>/dev/null);printf M;printf SC_BACKING_MARKER_%s "$m";echo\r'
mp135.evb:uart_expect sentinel="MSC_BACKING_MARKER_USBTMC EVB MSC BACKING" timeout_ms=5000
mp135.evb:uart_write data="test ! -d $g&&printf M&&printf SC_BACKING_NO_GADGET_OK;echo\r"
mp135.evb:uart_expect sentinel="MSC_BACKING_NO_GADGET_OK" timeout_ms=5000
mp135.evb:uart_close
mark tag=evb_msc_backing_file
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    out = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    return (Verification.op_succeeded(ops, 'dfu.evb', 'flash_layout') and
            Verification.op_succeeded(ops, 'msc.evb', 'verify') and
            Verification.op_succeeded(ops, 'mp135.evb', 'uart_expect') and
            'Welcome to STM32MP135 EVB' in out and
            'MSC_BACKING_FILE_OK' in out and
            'MSC_BACKING_SIZE_4096' in out and
            'MSC_BACKING_MARKER_USBTMC EVB MSC BACKING' in out and
            'MSC_BACKING_NO_GADGET_OK' in out and
            'MSC_BACKING_FAIL' not in out)
```

## WIP

### EVB Linux MSC function creation

Create only the target-side configfs gadget directory, descriptors,
strings, and one mass-storage function that points at the backing file
as read-only media. Do not link the function into a configuration or
bind the gadget to the UDC in this step.

Build:

```
make -C stm32mp135_test_board patch
make -C stm32mp135_test_board/bootloader -j$(nproc)
make -C stm32mp135_test_board kernel
make -C stm32mp135_test_board DTS=stm32mp135f-dk dtb
make -C stm32mp135_test_board br
make -C stm32mp135_test_board DTS=stm32mp135f-dk sd
```

Test: boot the EVB Linux image through the existing DFU/MSC/SD path,
wait for userspace, and capture target-side evidence that the
mass-storage function exists and references the backing file in
read-only mode.

Verify: Linux reached userspace and the captured target artefact shows
the mass-storage function was created but is not linked or bound.

### EVB Linux MSC configuration link

Add only the target-side configfs configuration and symlink the
mass-storage function into it. Leave the gadget unbound from the UDC in
this step.

Build:

```
make -C stm32mp135_test_board patch
make -C stm32mp135_test_board/bootloader -j$(nproc)
make -C stm32mp135_test_board kernel
make -C stm32mp135_test_board DTS=stm32mp135f-dk dtb
make -C stm32mp135_test_board br
make -C stm32mp135_test_board DTS=stm32mp135f-dk sd
```

Test: boot the EVB Linux image through the existing DFU/MSC/SD path,
wait for userspace, and capture target-side evidence that the
mass-storage function is linked into a configuration while `UDC` is
empty.

Verify: Linux reached userspace and the captured target artefact shows
the configured mass-storage gadget remains unbound.

### EVB Linux MSC UDC binding

Bind the already configured EVB Linux mass-storage gadget to the UDC.
This step adds only the final target-side UDC binding after configfs,
the backing file, the mass-storage function, and the configuration link
already exist.

Build:

```
make -C stm32mp135_test_board patch
make -C stm32mp135_test_board/bootloader -j$(nproc)
make -C stm32mp135_test_board kernel
make -C stm32mp135_test_board DTS=stm32mp135f-dk dtb
make -C stm32mp135_test_board br
make -C stm32mp135_test_board DTS=stm32mp135f-dk sd
```

Test: boot the EVB Linux image through the existing DFU/MSC/SD path,
wait for userspace, and capture target-side evidence that the gadget
`UDC` file contains a non-empty controller name.

Verify: Linux reached userspace and the captured target artefact shows
the mass-storage gadget was bound after Linux boot.

### EVB Linux MSC gadget descriptor smoke

Prove from the host that the EVB Linux-created mass-storage gadget
enumerates with descriptors that distinguish it from the earlier
bare-metal bootloader MSC device. This step uses the configfs gadget
setup from the previous step and adds only the host-side descriptor
smoke check.

Build:

```
make -C stm32mp135_test_board patch
make -C stm32mp135_test_board/bootloader -j$(nproc)
make -C stm32mp135_test_board kernel
make -C stm32mp135_test_board DTS=stm32mp135f-dk dtb
make -C stm32mp135_test_board br
make -C stm32mp135_test_board DTS=stm32mp135f-dk sd
```

Test: boot the EVB Linux image through the existing DFU/MSC/SD path,
wait for userspace, and run the smallest host-side USB descriptor check
that confirms a Linux-created USB mass-storage interface is present.
The check must use an explicit Linux-only VID/PID, product string,
serial string, or equivalent descriptor so it cannot pass on the
bare-metal bootloader MSC device.

Verify: Linux reached userspace and the captured USB descriptor
artefact identifies a mass-storage interface created after Linux boot.

### EVB Linux USB gadget baseline: mass-storage enumeration

Enable the Linux gadget stack needed for configfs and mass storage on
the EVB image. At boot, configure a small read-only mass-storage gadget
backed by a regular file so the host can enumerate it after Linux
reaches userspace. This step proves the MP135 Linux kernel, device tree,
UDC binding, configfs setup, and physical USB connection all work before
any USBTMC-specific implementation is attempted.

Build:

```
make -C stm32mp135_test_board patch
make -C stm32mp135_test_board/bootloader -j$(nproc)
make -C stm32mp135_test_board kernel
make -C stm32mp135_test_board DTS=stm32mp135f-dk dtb
make -C stm32mp135_test_board br
make -C stm32mp135_test_board DTS=stm32mp135f-dk sd
```

Test: boot the EVB Linux image through the existing DFU/MSC/SD path,
wait for userspace, and use the generic `test_serv` USB descriptor
assertion to verify that the host sees a Linux-created USB mass-storage
interface from the board. The host-side test must distinguish this from
the earlier bare-metal bootloader MSC device by checking Linux-specific
VID/PID, product string, serial string, or another explicit descriptor.

Verify: the manifest is clean, Linux reached userspace, the USB
descriptor assertion passed, and the captured descriptor artefact shows
a mass-storage interface bound after Linux boot.

### EVB USBTMC descriptor enumeration

Replace the Linux mass-storage gadget with the first USBTMC-shaped
gadget on the EVB. At this stage the device only needs to enumerate
with USBTMC-compatible descriptors and endpoints; it does not yet need
to process instrument messages. The implementation may use FunctionFS
or an out-of-tree kernel gadget function under
`stm32mp135_test_board/config/drivers`, but it must not require editing
the kernel source tree directly.

Build:

```
make -C stm32mp135_test_board patch
make -C stm32mp135_test_board/bootloader -j$(nproc)
make -C stm32mp135_test_board kernel
make -C stm32mp135_test_board DTS=stm32mp135f-dk dtb
make -C stm32mp135_test_board br
make -C stm32mp135_test_board DTS=stm32mp135f-dk sd
```

Test: boot the EVB Linux image and use the generic `test_serv` USB
descriptor assertion to verify that the host sees a USB interface whose
class, subclass, protocol, endpoint layout, strings, and Linux host
driver binding match the USBTMC profile chosen from the specification.

Verify: the manifest is clean, Linux reached userspace, no mass-storage
gadget is still exposed, the USB descriptor assertion passed, and the
descriptor artefact identifies the interface as USBTMC-compatible.

### EVB USBTMC `*IDN?` command

Implement the minimum USBTMC message handling needed for a host to send
`*IDN?` and receive a deterministic identification response from the
EVB. The implementation should handle normal message framing, bTag
matching, end-of-message behavior, and the required basic control
requests well enough for the Linux host `usbtmc` driver to perform the
query without manual recovery.

Build:

```
make -C stm32mp135_test_board patch
make -C stm32mp135_test_board/bootloader -j$(nproc)
make -C stm32mp135_test_board kernel
make -C stm32mp135_test_board DTS=stm32mp135f-dk dtb
make -C stm32mp135_test_board br
make -C stm32mp135_test_board DTS=stm32mp135f-dk sd
```

Test: boot the EVB Linux image, verify USBTMC enumeration, then issue a
host-side USBTMC query for `*IDN?` through `test_serv` and capture the
response.

Verify: the manifest is clean, the query operation passed, and the
response exactly matches the expected EVB identification string.

### EVB USBTMC slow command set

Extend the EVB USBTMC implementation from a single fixed query to a
small deterministic slow-command surface suitable for regression tests.
Include at least one command with no response, one query returning a
short scalar value, one query returning a short string, and one invalid
command path that reports a controlled error without wedging the USB
session.

Build:

```
make -C stm32mp135_test_board patch
make -C stm32mp135_test_board/bootloader -j$(nproc)
make -C stm32mp135_test_board kernel
make -C stm32mp135_test_board DTS=stm32mp135f-dk dtb
make -C stm32mp135_test_board br
make -C stm32mp135_test_board DTS=stm32mp135f-dk sd
```

Test: boot the EVB Linux image, verify USBTMC enumeration, run the slow
command sequence through `test_serv`, and query the device again after
the invalid-command case to prove the session recovered.

Verify: the manifest is clean, every expected command response matches,
the invalid command produced the expected controlled error state, and a
final `*IDN?` still succeeds.

### EVB USBTMC bulk loopback integrity

Add arbitrary-length bulk transfer support on the EVB with deterministic
data integrity checking. The host should be able to write and read back
binary payloads that include zero bytes and non-printable data, with
sizes that cross endpoint packet and internal buffer boundaries.

Build:

```
make -C stm32mp135_test_board patch
make -C stm32mp135_test_board/bootloader -j$(nproc)
make -C stm32mp135_test_board kernel
make -C stm32mp135_test_board DTS=stm32mp135f-dk dtb
make -C stm32mp135_test_board br
make -C stm32mp135_test_board DTS=stm32mp135f-dk sd
```

Test: boot the EVB Linux image, verify USBTMC enumeration, send a
deterministic binary pattern through USBTMC at multiple sizes, and read
back or otherwise verify the exact bytes through `test_serv`.

Verify: the manifest is clean and every tested binary transfer matches
the expected byte pattern exactly.

### EVB USBTMC sustained bulk throughput

Optimize the EVB implementation until USBTMC bulk transfer sustains at
least 100 Mbps for arbitrary data patterns and lengths. The test should
measure payload bytes transferred over wall time on the host side and
must include enough data to avoid passing due to startup noise.

Build:

```
make -C stm32mp135_test_board patch
make -C stm32mp135_test_board/bootloader -j$(nproc)
make -C stm32mp135_test_board kernel
make -C stm32mp135_test_board DTS=stm32mp135f-dk dtb
make -C stm32mp135_test_board br
make -C stm32mp135_test_board DTS=stm32mp135f-dk sd
```

Test: boot the EVB Linux image, verify USBTMC enumeration, transfer a
large deterministic binary pattern through USBTMC, and have `test_serv`
record both integrity and sustained payload throughput.

Verify: the manifest is clean, data integrity passes, and the measured
sustained payload rate is at least 100 Mbps.

### Custom-board Linux USB gadget baseline

Repeat the Linux gadget-stack baseline on the custom board. Use the
custom-board boot, device tree, reset line, DFU identity, MSC identity,
and SSH target. The custom board should enumerate as a Linux-created
mass-storage gadget after Linux reaches userspace, distinguished from
the bare-metal bootloader MSC device by explicit descriptors.

Build:

```
make -C stm32mp135_test_board patch
make -C stm32mp135_test_board boot
make -C stm32mp135_test_board kernel
make -C stm32mp135_test_board DTS=custom dtb
make -C stm32mp135_test_board br
make -C stm32mp135_test_board DTS=custom sd
```

Test: boot the custom-board Linux image through the existing
DFU/MSC/SD path, wait for userspace, and use the generic `test_serv`
USB descriptor assertion to verify the Linux-created mass-storage
interface.

Verify: the manifest is clean, Linux reached userspace, the USB
descriptor assertion passed, and the descriptor artefact identifies the
custom-board Linux mass-storage gadget.

### Custom-board USBTMC parity

Port the completed EVB USBTMC behavior to the custom board. The custom
board must enumerate as USBTMC, answer the slow command suite, preserve
bulk data integrity, and meet the same 100 Mbps sustained throughput
target.

Build:

```
make -C stm32mp135_test_board patch
make -C stm32mp135_test_board boot
make -C stm32mp135_test_board kernel
make -C stm32mp135_test_board DTS=custom dtb
make -C stm32mp135_test_board br
make -C stm32mp135_test_board DTS=custom sd
```

Test: boot the custom-board Linux image, verify USBTMC descriptor
enumeration, run the slow command suite, run binary integrity tests,
and run the sustained-throughput test through `test_serv`.

Verify: the manifest is clean, descriptor enumeration passes, all slow
commands match expected responses, binary integrity passes, and the
measured sustained payload rate is at least 100 Mbps.
