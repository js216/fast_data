# Confirm clk_ignore_unused is required

Verify the current boot behavior on the eval board with and without
`clk_ignore_unused` in the kernel boot arguments. The expected outcome is
that the board boots successfully with the flag. Without the flag, the
generated image must reach the kernel handoff and print a kernel command
line that omits `clk_ignore_unused`, while not reaching userspace within
the observation window. This establishes a reproducible baseline before
root-cause work.

### EVB boots with clk_ignore_unused

Builds the current EVB SD image from the checked-in DTS, which carries
`clk_ignore_unused`, then writes it to the eval board and proves Linux
reaches the userspace login prompt.

Build (apply `config/patch.linux` if needed, rebuild the bootloader and
kernel, refresh the EVB DTB, assemble an SD image, and keep a named copy
for this mission; skips `make br` and reuses the existing Buildroot
rootfs):

```
mkdir -p stm32mp135_test_board/build/kernel-clock-bringup
make -C stm32mp135_test_board patch
make -C stm32mp135_test_board/bootloader -j$(nproc)
make -C stm32mp135_test_board kernel
make -C stm32mp135_test_board DTS=stm32mp135f-dk dtb
make -C stm32mp135_test_board DTS=stm32mp135f-dk sd
cp stm32mp135_test_board/buildroot/output/images/sdcard.img stm32mp135_test_board/build/kernel-clock-bringup/sdcard.clk-ignore-unused.img
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/build/kernel-clock-bringup/sdcard.clk-ignore-unused.img
```

Test (max 10 min):

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
msc.evb:write data=@sdcard.clk-ignore-unused.img offset_lba=0
msc.evb:verify data=@sdcard.clk-ignore-unused.img offset_lba=0
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
mp135.evb:uart_close
mark tag=evb_boot_with_clk_ignore_unused
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    return ('clk_ignore_unused' in uart and
            'Welcome to STM32MP135 EVB' in uart and
            'login:' in uart)
```

### EVB reaches kernel command line without clk_ignore_unused

Builds a second SD image from a generated EVB DTS with only
`clk_ignore_unused` removed from `bootargs`. The source DTS is not
changed. The board must still reach the bootloader jump and kernel
command line, but it must not reach userspace within the same boot
window.

Build (reuses the existing Buildroot rootfs, rebuilds bootloader/kernel
inputs, then generates the no-flag DTS and image under
`stm32mp135_test_board/build/kernel-clock-bringup/`):

```
make -C stm32mp135_test_board patch
make -C stm32mp135_test_board/bootloader -j$(nproc)
make -C stm32mp135_test_board kernel
python3 scripts/build_no_clk_ignore_unused_sd.py
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/build/kernel-clock-bringup/stm32mp135f-dk-no-clk-ignore-unused.dts
stm32mp135_test_board/build/kernel-clock-bringup/sdcard.no-clk-ignore-unused.img
```

Test (max 10 min):

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
msc.evb:write data=@sdcard.no-clk-ignore-unused.img offset_lba=0
msc.evb:verify data=@sdcard.no-clk-ignore-unused.img offset_lba=0
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
mp135.evb:uart_expect sentinel="Kernel command line:" timeout_ms=10000
delay ms=45000
mp135.evb:uart_close
mark tag=evb_boot_without_clk_ignore_unused_no_userspace
```

Verify:

```
from pathlib import Path

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    dts = Path(
        artifacts['stm32mp135f-dk-no-clk-ignore-unused.dts']).read_text()
    uart = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    no_flag_dts = ('root=/dev/mmcblk0p3' in dts and
                   'clk_ignore_unused' not in dts)
    cmdline = next((line for line in uart.splitlines()
                    if 'Kernel command line:' in line), '')
    handoff = ('Jumping to address' in uart and
               'Linux version' in uart)
    cmdline_without_flag = ('Kernel command line:' in cmdline and
                            'root=/dev/mmcblk0p3' in cmdline and
                            'clk_ignore_unused' not in cmdline)
    no_userspace = ('Welcome to STM32MP135 EVB' not in uart and
                    'login:' not in uart)
    return no_flag_dts and handoff and cmdline_without_flag and no_userspace
```

### Trace unused-clock shutdown hang

Instrument the kernel unused-clock shutdown path to print each clock name
immediately before it is disabled. Build an EVB SD image whose bootargs
omit `clk_ignore_unused`, boot it, and capture the UART log. This
diagnostic step must identify the final unused-clock trace emitted before
the boot stops, without changing the source DTS bootargs or attempting a
functional fix.

Diagnostic result: the final emitted unused-clock trace before the boot
stops is `stgen_k`; the previous trace is `i2c4_k`, and userspace is not
reached.

Build (apply `config/patch.linux` if needed, add temporary trace output
under the existing Linux patch workflow, rebuild kernel inputs, then
generate the no-flag EVB image):

```
make -C stm32mp135_test_board patch
make -C stm32mp135_test_board/bootloader -j$(nproc)
make -C stm32mp135_test_board kernel
python3 scripts/build_no_clk_ignore_unused_sd.py
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
stm32mp135_test_board/build/kernel-clock-bringup/stm32mp135f-dk-no-clk-ignore-unused.dts
stm32mp135_test_board/build/kernel-clock-bringup/sdcard.no-clk-ignore-unused.img
```

Test (max 10 min):

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
msc.evb:write data=@sdcard.no-clk-ignore-unused.img offset_lba=0
msc.evb:verify data=@sdcard.no-clk-ignore-unused.img offset_lba=0
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
mp135.evb:uart_expect sentinel="Kernel command line:" timeout_ms=10000
mp135.evb:uart_expect sentinel="clk_disable_unused trace:" timeout_ms=30000
delay ms=45000
mp135.evb:uart_close
mark tag=evb_no_flag_unused_clock_trace
```

Verify:

```
from pathlib import Path

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    dts = Path(
        artifacts['stm32mp135f-dk-no-clk-ignore-unused.dts']).read_text()
    uart = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    cmdline = next((line for line in uart.splitlines()
                    if 'Kernel command line:' in line), '')
    traces = [line for line in uart.splitlines()
              if 'clk_disable_unused trace:' in line]
    no_flag = ('clk_ignore_unused' not in dts and
               'clk_ignore_unused' not in cmdline)
    no_userspace = ('Welcome to STM32MP135 EVB' not in uart and
                    'login:' not in uart)
    last_trace_has_clock = bool(traces and
                                traces[-1].split('trace:', 1)[1].strip())
    return no_flag and no_userspace and last_trace_has_clock
```

## WIP

# Kernel clock bring-up

Find and fix the root cause that makes `clk_ignore_unused` necessary for
kernel boot. Determine whether the issue comes from the kernel patching
workflow, device tree contents, or another clock configuration problem.
After fixing the eval board, verify that the custom board also boots
without relying on `clk_ignore_unused`.
