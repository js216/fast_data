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
mp135.evb:uart_write data="dmesg -n 1 2>/dev/null;true\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
delay ms=2000
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data="cf=/sys/kernel/config;ug=$cf/usb_gadget\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data="mok=0;gok=0;dok=0;echo\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data="mountpoint -q $cf&&mok=1;echo\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data="grep -q ' /sys/kernel/config configfs ' /proc/mounts&&gok=1;echo\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data="test -d $ug&&dok=1;echo\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data='test "$mok$gok$dok" = 111&&printf CONFIGFS_&&printf OK;echo\r'
mp135.evb:uart_expect sentinel="CONFIGFS_OK" timeout_ms=5000
mp135.evb:uart_write data="printf configfs\ ;grep ' /sys/kernel/config configfs ' /proc/mounts\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data="printf usb_;printf gadget_dir\ ;ls -ld $ug\r"
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
bytes may be zero padding. This step depends on configfs availability.
It may leave no gadget, or an unbound gadget with no functions, or
only `mass_storage.usbtmc` either unlinked or linked into
`c.1/mass_storage.usbtmc`; the assertion tolerates either no configs
symlinks or that single expected link, and accepts either an empty UDC
or one bound to `49000000.usb` since later steps bind the gadget.

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
mp135.evb:uart_write data="dmesg -n 1 2>/dev/null;true\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
delay ms=2000
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data="p=/var/lib/usbtmc/msc-backing.bin\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data="g=/sys/kernel/config/usb_gadget/usbtmc\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data="test -f $p&&printf M&&printf SC_BACKING_FILE_OK;echo\r"
mp135.evb:uart_expect sentinel="MSC_BACKING_FILE_OK" timeout_ms=5000
mp135.evb:uart_write data='s=$(wc -c < $p 2>/dev/null);printf M;printf SC_BACKING_SIZE_%s "$s";echo\r'
mp135.evb:uart_expect sentinel="MSC_BACKING_SIZE_4096" timeout_ms=5000
mp135.evb:uart_write data='w="USBTMC EVB MSC BACKING";echo\r'
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data='IFS= read -r m < $p;echo\r'
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data='test "$m" = "$w"&&echo MSC_BACKING_MARKER_$w;echo\r'
mp135.evb:uart_expect sentinel="MSC_BACKING_MARKER_USBTMC EVB MSC BACKING" timeout_ms=5000
mp135.evb:uart_write data='ok=0;fok=0;cok=0;uok=0;want=mass_storage.usbtmc;printf MSCB_A;echo\r'
mp135.evb:uart_expect sentinel="MSCB_A" timeout_ms=3000
mp135.evb:uart_write data='test ! -d $g&&ok=1;fs=BAD;test -d $g/functions&&fs="$(LS_COLORS= ls -A --color=never $g/functions 2>/dev/null)";printf MSCB_B;echo\r'
mp135.evb:uart_expect sentinel="MSCB_B" timeout_ms=3000
mp135.evb:uart_write data='cs=BAD;test -d $g/configs&&cs="$(find $g/configs -type l -print -quit)";printf MSCB_C;echo\r'
mp135.evb:uart_expect sentinel="MSCB_C" timeout_ms=3000
mp135.evb:uart_write data='udc=BAD;test -f $g/UDC&&udc="$(cat $g/UDC)";printf MSCB_D;echo\r'
mp135.evb:uart_expect sentinel="MSCB_D" timeout_ms=3000
mp135.evb:uart_write data='test "$fs" = ""&&fok=1;test "$fs" = "$want"&&fok=1;test "$cs" = ""&&cok=1;test "$cs" = "$g/configs/c.1/mass_storage.usbtmc"&&cok=1;test "$udc" = ""&&uok=1;test "$udc" = "49000000.usb"&&uok=1;printf MSCB_E;echo\r'
mp135.evb:uart_expect sentinel="MSCB_E" timeout_ms=3000
mp135.evb:uart_write data='test "$cok$uok" = 11&&ok=1;printf MSCB_F;echo\r'
mp135.evb:uart_expect sentinel="MSCB_F" timeout_ms=3000
mp135.evb:uart_write data='test $ok = 1&&printf M&&printf SC_BACKING_NO_&&printf EXPOSED_GADGET_OK;echo\r'
mp135.evb:uart_expect sentinel="MSC_BACKING_NO_EXPOSED_GADGET_OK" timeout_ms=5000
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
            'MSC_BACKING_NO_EXPOSED_GADGET_OK' in out and
            'MSC_BACKING_FAIL' not in out)
```

### EVB Linux MSC gadget descriptors

Create only the target-side configfs gadget directory, device
descriptors, and English strings for the EVB Linux mass-storage
baseline. This step validates the descriptors and strings while allowing
either no gadget functions or only an unlinked
`mass_storage.usbtmc` function. The configs check tolerates either an
empty `$g/configs` directory or exactly the expected `c.1` configuration
directory (which holds the `mass_storage.usbtmc` symlink in later
steps). The UDC check accepts either an empty UDC file or one already
bound to `49000000.usb`, since later steps bind the gadget at boot.

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
mp135.evb:uart_write data="dmesg -n 1 2>/dev/null;true\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
delay ms=2000
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data="g=/sys/kernel/config/usb_gadget/usbtmc\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data="s=$g/strings/0x409\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data="test -d $g&&printf GAD&&printf GET_DIR_OK;echo\r"
mp135.evb:uart_expect sentinel="GADGET_DIR_OK" timeout_ms=5000
mp135.evb:uart_write data='ids="$(cat $g/idVendor) $(cat $g/idProduct) ";echo\r'
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data='ids="$ids$(cat $g/bcdDevice) $(cat $g/bcdUSB) ";echo\r'
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data='ids="$ids$(cat $g/bDeviceClass) ";echo\r'
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data='ids="$ids$(cat $g/bDeviceSubClass) $(cat $g/bDeviceProtocol) ";echo\r'
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data='printf GAD;printf GET_IDS_;printf %s "$ids";echo\r'
mp135.evb:uart_expect sentinel="GADGET_IDS_0x0483 0x571e 0x0100 0x0200 0x00 0x00 0x00 " timeout_ms=5000
mp135.evb:uart_write data='man="$(cat $s/manufacturer)";echo\r'
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data='prod="$(cat $s/product)";echo\r'
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data='ser="$(cat $s/serialnumber)";echo\r'
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data='printf GAD;printf GET_STRINGS_;printf %s "$man|$prod|$ser|";echo\r'
mp135.evb:uart_expect sentinel="GADGET_STRINGS_Stanford Research Systems|STM32MP135 EVB Linux MSC|evb-linux-msc-0001|" timeout_ms=5000
mp135.evb:uart_write data='fs="";test -d $g/functions&&fs=$(LS_COLORS= ls -A --color=never $g/functions 2>/dev/null|tr "\n" ",");printf GAD;printf GET_FUNCTIONS_LIST_;printf "[%s]" "$fs";echo\r'
mp135.evb:uart_expect sentinel="GADGET_FUNCTIONS_LIST_" timeout_ms=5000
mp135.evb:uart_write data='fs="";test -d $g/functions&&fs="$(LS_COLORS= ls -A --color=never $g/functions 2>/dev/null)";case "$fs" in ""|mass_storage.usbtmc) printf GAD;printf GET_FUNCTIONS_;printf UNLINKED_OK;; esac;echo\r'
mp135.evb:uart_expect sentinel="GADGET_FUNCTIONS_UNLINKED_OK" timeout_ms=5000
mp135.evb:uart_write data='cs="$(LS_COLORS= ls -A --color=never $g/configs 2>/dev/null)";case "$cs" in ""|c.1) printf GAD;printf GET_NO_;printf CONFIGS_OK;; esac;echo\r'
mp135.evb:uart_expect sentinel="GADGET_NO_CONFIGS_OK" timeout_ms=5000
mp135.evb:uart_write data='udc=BAD;test -f $g/UDC&&udc="$(cat $g/UDC)";echo\r'
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data='udcok=0;test -z "$udc"&&udcok=1;test "$udc" = "49000000.usb"&&udcok=1;echo\r'
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data='test $udcok = 1&&{ printf GAD;printf GET_UDC_;printf EMPTY_OK;};echo\r'
mp135.evb:uart_expect sentinel="GADGET_UDC_EMPTY_OK" timeout_ms=5000
mp135.evb:uart_close
mark tag=evb_msc_gadget_descriptors
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    out = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    lines = out.replace('\r', '\n').splitlines()
    return (Verification.op_succeeded(ops, 'dfu.evb', 'flash_layout') and
            Verification.op_succeeded(ops, 'msc.evb', 'verify') and
            Verification.op_succeeded(ops, 'mp135.evb', 'uart_expect') and
            'Welcome to STM32MP135 EVB' in out and
            'GADGET_DIR_OK' in lines and
            'GADGET_IDS_0x0483 0x571e 0x0100 0x0200 0x00 0x00 0x00 ' in lines and
            'GADGET_STRINGS_Stanford Research Systems|STM32MP135 EVB Linux MSC|evb-linux-msc-0001|' in lines and
            'GADGET_FUNCTIONS_UNLINKED_OK' in lines and
            'GADGET_NO_CONFIGS_OK' in lines and
            'GADGET_UDC_EMPTY_OK' in lines and
            'GADGET_FAIL' not in out)
```

### EVB Linux MSC function creation

Create only the target-side configfs mass-storage function
`functions/mass_storage.usbtmc` for the existing EVB Linux gadget. Set
LUN 0 to use `/var/lib/usbtmc/msc-backing.bin` as read-only media. The
gadget directory, descriptors, strings, and backing file already exist
from previous steps. This step validates the function while allowing
either no configuration symlinks or only the expected
`c.1/mass_storage.usbtmc` link from the next step. The UDC check accepts
either an empty UDC file or one already bound to `49000000.usb`, since
later steps bind the gadget at boot.

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
mp135.evb:uart_write data="dmesg -n 1 2>/dev/null;true\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
delay ms=2000
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data="g=/sys/kernel/config/usb_gadget/usbtmc\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data="f=$g/functions/mass_storage.usbtmc\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data="p=/var/lib/usbtmc/msc-backing.bin\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data="test -d $f&&printf MSC&&printf _FUNCTION_DIR_OK;echo\r"
mp135.evb:uart_expect sentinel="MSC_FUNCTION_DIR_OK" timeout_ms=5000
mp135.evb:uart_write data='fl=BAD;test -f $f/lun.0/file&&fl="$(cat $f/lun.0/file)";echo\r'
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data='test $fl = $p&&{ printf MSC;printf _FUNCTION_;printf FILE_OK;};echo\r'
mp135.evb:uart_expect sentinel="MSC_FUNCTION_FILE_OK" timeout_ms=5000
mp135.evb:uart_write data='ro=BAD;test -f $f/lun.0/ro&&ro="$(cat $f/lun.0/ro)";echo\r'
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data='test $ro = 1&&{ printf MSC;printf _FUNCTION_;printf RO_OK;};echo\r'
mp135.evb:uart_expect sentinel="MSC_FUNCTION_RO_OK" timeout_ms=5000
mp135.evb:uart_write data='ok=0;ls=$(find $g/configs -type l 2>/dev/null);test -z "$ls"&&ok=1;test "$ls" = "$g/configs/c.1/mass_storage.usbtmc"&&ok=1;test $ok = 1&&{ printf MSC;printf _FUNCTION_;printf UNLINKED_OK;};echo\r'
mp135.evb:uart_expect sentinel="MSC_FUNCTION_UNLINKED_OK" timeout_ms=5000
mp135.evb:uart_write data='udc=BAD;test -f $g/UDC&&udc="$(cat $g/UDC)";echo\r'
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data='udcok=0;test -z "$udc"&&udcok=1;test "$udc" = "49000000.usb"&&udcok=1;echo\r'
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data='test $udcok = 1&&{ printf MSC;printf _FUNCTION_UDC_;printf EMPTY_OK;};echo\r'
mp135.evb:uart_expect sentinel="MSC_FUNCTION_UDC_EMPTY_OK" timeout_ms=5000
mp135.evb:uart_close
mark tag=evb_msc_function_creation
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    out = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    lines = out.replace('\r', '\n').splitlines()
    return (Verification.op_succeeded(ops, 'dfu.evb', 'flash_layout') and
            Verification.op_succeeded(ops, 'msc.evb', 'verify') and
            Verification.op_succeeded(ops, 'mp135.evb', 'uart_expect') and
            'Welcome to STM32MP135 EVB' in out and
            'MSC_FUNCTION_DIR_OK' in lines and
            'MSC_FUNCTION_FILE_OK' in lines and
            'MSC_FUNCTION_RO_OK' in lines and
            'MSC_FUNCTION_UNLINKED_OK' in lines and
            'MSC_FUNCTION_UDC_EMPTY_OK' in lines and
            'MSC_FUNCTION_FAIL' not in out)
```

### EVB Linux MSC configuration link

Create only the target-side configfs configuration directory `c.1`
under the existing EVB Linux gadget, populate its `MaxPower` attribute
with the standard value `0`, and symlink the existing mass-storage
function `mass_storage.usbtmc` into it. The gadget directory,
descriptors, strings, backing file, and mass-storage function already
exist from previous steps. The UDC check accepts either an empty UDC
file or one already bound to `49000000.usb`, since the next step binds
the gadget at boot.

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
mp135.evb:uart_write data="dmesg -n 1 2>/dev/null;true\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
delay ms=2000
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data="g=/sys/kernel/config/usb_gadget/usbtmc\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data="c=$g/configs/c.1\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data="l=$c/mass_storage.usbtmc\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data="test -d $c&&printf MSC&&printf _CONFIG_DIR_OK;echo\r"
mp135.evb:uart_expect sentinel="MSC_CONFIG_DIR_OK" timeout_ms=5000
mp135.evb:uart_write data='mp=BAD;test -f $c/MaxPower&&mp="$(cat $c/MaxPower)";echo\r'
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data='test $mp = 0&&{ printf MSC;printf _CONFIG_;printf MAXPOWER_OK;};echo\r'
mp135.evb:uart_expect sentinel="MSC_CONFIG_MAXPOWER_OK" timeout_ms=5000
mp135.evb:uart_write data='test -L $l&&{ printf MSC;printf _CONFIG_;printf LINK_OK;};echo\r'
mp135.evb:uart_expect sentinel="MSC_CONFIG_LINK_OK" timeout_ms=5000
mp135.evb:uart_write data='tgt=BAD;test -L $l&&tgt="$(readlink $l)";echo\r'
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data='case "$tgt" in *functions/mass_storage.usbtmc) printf MSC;printf _CONFIG_LINK_;printf TARGET_OK;; esac;echo\r'
mp135.evb:uart_expect sentinel="MSC_CONFIG_LINK_TARGET_OK" timeout_ms=5000
mp135.evb:uart_write data='udc=BAD;test -f $g/UDC&&udc="$(cat $g/UDC)";echo\r'
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data='udcok=0;test -z "$udc"&&udcok=1;test "$udc" = "49000000.usb"&&udcok=1;echo\r'
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data='test $udcok = 1&&{ printf MSC;printf _CONFIG_UDC_;printf EMPTY_OK;};echo\r'
mp135.evb:uart_expect sentinel="MSC_CONFIG_UDC_EMPTY_OK" timeout_ms=5000
mp135.evb:uart_close
mark tag=evb_msc_configuration_link
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    out = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    lines = out.replace('\r', '\n').splitlines()
    return (Verification.op_succeeded(ops, 'dfu.evb', 'flash_layout') and
            Verification.op_succeeded(ops, 'msc.evb', 'verify') and
            Verification.op_succeeded(ops, 'mp135.evb', 'uart_expect') and
            'Welcome to STM32MP135 EVB' in out and
            'MSC_CONFIG_DIR_OK' in lines and
            'MSC_CONFIG_MAXPOWER_OK' in lines and
            'MSC_CONFIG_LINK_OK' in lines and
            'MSC_CONFIG_LINK_TARGET_OK' in lines and
            'MSC_CONFIG_UDC_EMPTY_OK' in lines and
            'MSC_CONFIG_FAIL' not in out)
```

### EVB Linux MSC UDC binding

Bind the already configured EVB Linux mass-storage gadget to the UDC.
This step adds only the final target-side UDC binding after configfs,
the backing file, the mass-storage function, and the configuration link
already exist. The boot-time init script must write the OTG controller
name (e.g. `49000000.usb`) into `$GADGET/UDC` so that the gadget is
attached to a real UDC controller before userspace login.

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
mp135.evb:uart_write data="dmesg -n 1 2>/dev/null;true\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
delay ms=2000
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data="g=/sys/kernel/config/usb_gadget/usbtmc\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data='test -s $g/UDC&&{ printf MSC;printf _UDC_;printf BOUND_OK;};echo\r'
mp135.evb:uart_expect sentinel="MSC_UDC_BOUND_OK" timeout_ms=5000
mp135.evb:uart_write data='udc=BAD;test -s $g/UDC&&udc="$(cat $g/UDC)";echo\r'
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data='case "$udc" in 49000000.usb*) printf MSC;printf _UDC_;printf NAME_OK;; esac;echo\r'
mp135.evb:uart_expect sentinel="MSC_UDC_NAME_OK" timeout_ms=5000
mp135.evb:uart_close
mark tag=evb_msc_udc_binding
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    out = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    lines = out.replace('\r', '\n').splitlines()
    return (Verification.op_succeeded(ops, 'dfu.evb', 'flash_layout') and
            Verification.op_succeeded(ops, 'msc.evb', 'verify') and
            Verification.op_succeeded(ops, 'mp135.evb', 'uart_expect') and
            'Welcome to STM32MP135 EVB' in out and
            'MSC_UDC_BOUND_OK' in lines and
            'MSC_UDC_NAME_OK' in lines and
            'MSC_UDC_FAIL' not in out)
```

## WIP

### EVB Linux MSC gadget descriptor smoke

Prove that the EVB Linux mass-storage gadget configured and bound in
the prior steps actually enumerated on a USB host. We use indirect
host-side proof: after the gadget is bound to the UDC, the file
`/sys/class/udc/49000000.usb/state` reads `configured` IFF a USB host
has completed SET_CONFIGURATION. Without a connected host the state
stays at `default` or `addressed`. We additionally confirm the
configfs product string equals the Linux-specific
`STM32MP135 EVB Linux MSC` to distinguish from the bare-metal
bootloader MSC, whose strings differ.

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
mp135.evb:uart_write data="dmesg -n 1 2>/dev/null;true\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
delay ms=3000
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data='s="";test -f /sys/class/udc/49000000.usb/state&&s="$(cat /sys/class/udc/49000000.usb/state 2>/dev/null)"\r'
mp135.evb:uart_expect sentinel="# " timeout_ms=3000
mp135.evb:uart_write data='printf MSC;printf _SMOKE_STATE_;printf "[%s]" "$s";echo\r'
mp135.evb:uart_expect sentinel="MSC_SMOKE_STATE_" timeout_ms=5000
mp135.evb:uart_write data='test "$s" = "configured"&&printf MSC&&printf _SMOKE_;printf CONFIGURED_OK;echo\r'
mp135.evb:uart_expect sentinel="MSC_SMOKE_CONFIGURED_OK" timeout_ms=5000
mp135.evb:uart_write data='g=/sys/kernel/config/usb_gadget/usbtmc;p="$(cat $g/strings/0x409/product 2>/dev/null)";test "$p" = "STM32MP135 EVB Linux MSC"&&printf MSC&&printf _SMOKE_;printf PRODUCT_OK;echo\r'
mp135.evb:uart_expect sentinel="MSC_SMOKE_PRODUCT_OK" timeout_ms=5000
mp135.evb:uart_close
mark tag=evb_msc_descriptor_smoke
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    out = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    lines = out.replace('\r', '\n').splitlines()
    return (Verification.op_succeeded(ops, 'dfu.evb', 'flash_layout') and
            Verification.op_succeeded(ops, 'msc.evb', 'verify') and
            Verification.op_succeeded(ops, 'mp135.evb', 'uart_expect') and
            'Welcome to STM32MP135 EVB' in out and
            'MSC_SMOKE_CONFIGURED_OK' in lines and
            'MSC_SMOKE_PRODUCT_OK' in lines and
            'MSC_SMOKE_FAIL' not in out)
```

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
