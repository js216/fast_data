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

### EVB marks after bkpsram skip during unused-clock shutdown

Build an EVB SD image whose bootargs omit `clk_ignore_unused` and whose
temporary Linux patch keeps `i2c4_k`, `stgen_k`, `tim15_k`, and
`bkpsram` enabled during unused-clock shutdown. The previous diagnostic
still stalled after printing the trace tail `i2c4_k`, `stgen_k`,
`tim15_k`, `bkpsram`; because each trace is printed before the guarded
disable/skip call, this narrower diagnostic prints an `after` marker
once the branch returns so the next run distinguishes a stall inside the
`bkpsram` skip/disable path from a stall later in traversal.

Build (apply `config/patch.linux` if needed, add the temporary
keep-enabled and post-branch marker change under the existing Linux
patch workflow, rebuild kernel inputs, then generate the no-flag EVB
image):

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
mp135.evb:uart_expect sentinel="clk_disable_unused trace: bkpsram" timeout_ms=30000
mp135.evb:uart_expect sentinel="clk_disable_unused after: bkpsram" timeout_ms=5000
delay ms=45000
mp135.evb:uart_close
mark tag=evb_no_flag_bkpsram_after_marker
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
    no_flag = ('clk_ignore_unused' not in dts and
               'clk_ignore_unused' not in cmdline)
    no_userspace = ('Welcome to STM32MP135 EVB' not in uart and
                    'login:' not in uart)
    return (no_flag and
            'Linux version' in uart and
            'clk_disable_unused trace: i2c4_k' in uart and
            'clk_disable_unused trace: stgen_k' in uart and
            'clk_disable_unused trace: tim15_k' in uart and
            'clk_disable_unused trace: bkpsram' in uart and
            'clk_disable_unused after: bkpsram' in uart and
            no_userspace)
```

### EVB names the clock visited after bkpsram

Build an EVB SD image whose bootargs omit `clk_ignore_unused` and whose
temporary Linux patch keeps `i2c4_k`, `stgen_k`, `tim15_k`, and
`bkpsram` enabled during unused-clock shutdown. Extend the existing
diagnostic markers only enough to print the next unused-clock traversal
entry reached after `clk_disable_unused after: bkpsram`, so the captured
UART log identifies the first post-`bkpsram` clock name or proves that
the traversal stops before another named entry.

Diagnostic result: the first unused-clock traversal entry reached after
`clk_disable_unused after: bkpsram` is `mdma`.

Build (apply `config/patch.linux` if needed, add the temporary
post-`bkpsram` next-entry marker under the existing Linux patch
workflow, rebuild kernel inputs, then generate the no-flag EVB image):

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
mp135.evb:uart_expect sentinel="clk_disable_unused after: bkpsram" timeout_ms=30000
mp135.evb:uart_expect sentinel="clk_disable_unused post-bkpsram next:" timeout_ms=5000
delay ms=45000
mp135.evb:uart_close
mark tag=evb_no_flag_post_bkpsram_next_clock
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
    lines = uart.splitlines()
    after_indexes = [i for i, line in enumerate(lines)
                     if 'clk_disable_unused after: bkpsram' in line]
    next_indexes = [(i, line) for i, line in enumerate(lines)
                    if 'clk_disable_unused post-bkpsram next:' in line]
    if not after_indexes or len(next_indexes) != 1:
        return False
    next_index, next_line = next_indexes[0]
    next_value = next_line.split('next:', 1)[1].strip()
    no_flag = ('clk_ignore_unused' not in dts and
               'clk_ignore_unused' not in cmdline)
    no_userspace = ('Welcome to STM32MP135 EVB' not in uart and
                    'login:' not in uart)
    return (no_flag and
            'Linux version' in uart and
            'clk_disable_unused after: bkpsram' in uart and
            after_indexes[-1] < next_index and
            bool(next_value) and
            no_userspace)
```

### EVB marks after mdma skip during unused-clock shutdown

Build an EVB SD image whose bootargs omit `clk_ignore_unused` and whose
temporary Linux patch keeps the prior four implicated clocks, `i2c4_k`,
`stgen_k`, `tim15_k`, and `bkpsram`, plus `mdma` enabled during
unused-clock shutdown. The previous diagnostic proved that the first
traversal entry reached after
`clk_disable_unused after: bkpsram` is `mdma`; this step adds only the
minimal `mdma` guard and an `after` marker so the next run distinguishes
a stall inside the `mdma` disable/skip branch from a stall later in
traversal.

Diagnostic result: the kernel reaches `clk_disable_unused after: mdma`,
so the function's tail-marker fires for `mdma`'s traversal entry and
its keep-enabled branch returns cleanly, but boot still does not reach
userspace; the stall is later in traversal than `mdma`.

Build (apply `config/patch.linux` if needed, add the temporary
keep-enabled and post-`mdma` marker change under the existing Linux
patch workflow, rebuild kernel inputs, then generate the no-flag EVB
image):

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
mp135.evb:uart_expect sentinel="clk_disable_unused post-bkpsram next: mdma" timeout_ms=30000
mp135.evb:uart_expect sentinel="clk_disable_unused after: mdma" timeout_ms=5000
delay ms=45000
mp135.evb:uart_close
mark tag=evb_no_flag_mdma_after_marker
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
    lines = uart.splitlines()
    next_indexes = [i for i, line in enumerate(lines)
                    if 'clk_disable_unused post-bkpsram next: mdma' in line]
    after_indexes = [i for i, line in enumerate(lines)
                     if 'clk_disable_unused after: mdma' in line]
    if len(next_indexes) != 1 or len(after_indexes) != 1:
        return False
    no_flag = ('clk_ignore_unused' not in dts and
               'clk_ignore_unused' not in cmdline)
    no_userspace = ('Welcome to STM32MP135 EVB' not in uart and
                    'login:' not in uart)
    return (no_flag and
            'Linux version' in uart and
            next_indexes[0] < after_indexes[0] and
            no_userspace)
```

### EVB names the clock visited after mdma

Build an EVB SD image whose bootargs omit `clk_ignore_unused` and whose
temporary Linux patch keeps `i2c4_k`, `stgen_k`, `tim15_k`, `bkpsram`,
and `mdma` enabled during unused-clock shutdown. Extend the existing
diagnostic markers only enough to print the next unused-clock traversal
entry reached after `clk_disable_unused after: mdma`, so the captured
UART log identifies the first post-`mdma` clock name or proves that the
traversal stops before another named entry.

Diagnostic result: the first unused-clock traversal entry reached after
`clk_disable_unused after: mdma` is `eth1tx`.

Build (apply `config/patch.linux` if needed, add the temporary
post-`mdma` next-entry marker under the existing Linux patch workflow,
rebuild kernel inputs, then generate the no-flag EVB image):

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
mp135.evb:uart_expect sentinel="clk_disable_unused after: mdma" timeout_ms=30000
mp135.evb:uart_expect sentinel="clk_disable_unused post-mdma next:" timeout_ms=5000
delay ms=45000
mp135.evb:uart_close
mark tag=evb_no_flag_post_mdma_next_clock
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
    lines = uart.splitlines()
    after_indexes = [i for i, line in enumerate(lines)
                     if 'clk_disable_unused after: mdma' in line]
    next_indexes = [(i, line) for i, line in enumerate(lines)
                    if 'clk_disable_unused post-mdma next:' in line]
    if not after_indexes or len(next_indexes) != 1:
        return False
    next_index, next_line = next_indexes[0]
    next_value = next_line.split('next:', 1)[1].strip()
    no_flag = ('clk_ignore_unused' not in dts and
               'clk_ignore_unused' not in cmdline)
    no_userspace = ('Welcome to STM32MP135 EVB' not in uart and
                    'login:' not in uart)
    return (no_flag and
            'Linux version' in uart and
            'clk_disable_unused after: mdma' in uart and
            after_indexes[-1] < next_index and
            bool(next_value) and
            no_userspace)
```

### EVB marks after eth1tx skip during unused-clock shutdown

Build an EVB SD image whose bootargs omit `clk_ignore_unused` and whose
temporary Linux patch keeps the prior five implicated clocks, `i2c4_k`,
`stgen_k`, `tim15_k`, `bkpsram`, and `mdma`, plus `eth1tx` enabled
during unused-clock shutdown. The previous diagnostic proved that the
first traversal entry reached after `clk_disable_unused after: mdma` is
`eth1tx`; this step adds only the minimal `eth1tx` entry to the
keep-enabled list in both the `disable_unused` and `disable` branches
and an `after` marker so the next run distinguishes a stall inside the
`eth1tx` disable/skip branch from a stall later in traversal.

Diagnostic result: the kernel reaches `clk_disable_unused after: eth1tx`
(eth1tx's keep-enabled branch returns cleanly), but boot still does not
reach userspace, so the stall is later in traversal than eth1tx.

Build (apply `config/patch.linux` if needed, add the temporary
keep-enabled and post-`eth1tx` marker change under the existing Linux
patch workflow, rebuild kernel inputs, then generate the no-flag EVB
image):

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
mp135.evb:uart_expect sentinel="clk_disable_unused post-mdma next: eth1tx" timeout_ms=30000
mp135.evb:uart_expect sentinel="clk_disable_unused after: eth1tx" timeout_ms=5000
delay ms=45000
mp135.evb:uart_close
mark tag=evb_no_flag_eth1tx_after_marker
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
    lines = uart.splitlines()
    next_indexes = [i for i, line in enumerate(lines)
                    if 'clk_disable_unused post-mdma next: eth1tx' in line]
    after_indexes = [i for i, line in enumerate(lines)
                     if 'clk_disable_unused after: eth1tx' in line]
    if len(next_indexes) != 1 or len(after_indexes) != 1:
        return False
    no_flag = ('clk_ignore_unused' not in dts and
               'clk_ignore_unused' not in cmdline)
    no_userspace = ('Welcome to STM32MP135 EVB' not in uart and
                    'login:' not in uart)
    return (no_flag and
            'Linux version' in uart and
            next_indexes[0] < after_indexes[0] and
            no_userspace)
```

### EVB names the clock visited after eth1tx

Build an EVB SD image whose bootargs omit `clk_ignore_unused` and whose
temporary Linux patch keeps `i2c4_k`, `stgen_k`, `tim15_k`, `bkpsram`,
`mdma`, and `eth1tx` enabled during unused-clock shutdown. Extend the
existing diagnostic markers only enough to print the next unused-clock
traversal entry reached after `clk_disable_unused after: eth1tx`, so the
captured UART log identifies the first post-`eth1tx` clock name or
proves that the traversal stops before another named entry.

Diagnostic result: the first unused-clock traversal entry reached after
`clk_disable_unused after: eth1tx` is `eth1rx`.

Build (apply `config/patch.linux` if needed, add the temporary
post-`eth1tx` next-entry marker under the existing Linux patch workflow,
rebuild kernel inputs, then generate the no-flag EVB image):

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
mp135.evb:uart_expect sentinel="clk_disable_unused after: eth1tx" timeout_ms=30000
mp135.evb:uart_expect sentinel="clk_disable_unused post-eth1tx next:" timeout_ms=5000
delay ms=45000
mp135.evb:uart_close
mark tag=evb_no_flag_post_eth1tx_next_clock
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
    lines = uart.splitlines()
    after_indexes = [i for i, line in enumerate(lines)
                     if 'clk_disable_unused after: eth1tx' in line]
    next_indexes = [(i, line) for i, line in enumerate(lines)
                    if 'clk_disable_unused post-eth1tx next:' in line]
    if not after_indexes or len(next_indexes) != 1:
        return False
    next_index, next_line = next_indexes[0]
    next_value = next_line.split('next:', 1)[1].strip()
    no_flag = ('clk_ignore_unused' not in dts and
               'clk_ignore_unused' not in cmdline)
    no_userspace = ('Welcome to STM32MP135 EVB' not in uart and
                    'login:' not in uart)
    return (no_flag and
            'Linux version' in uart and
            'clk_disable_unused after: eth1tx' in uart and
            after_indexes[-1] < next_index and
            bool(next_value) and
            no_userspace)
```

### EVB marks after eth1rx skip during unused-clock shutdown

Build an EVB SD image whose bootargs omit `clk_ignore_unused` and whose
temporary Linux patch keeps the prior six implicated clocks, `i2c4_k`,
`stgen_k`, `tim15_k`, `bkpsram`, `mdma`, and `eth1tx`, plus `eth1rx`
enabled during unused-clock shutdown. The previous diagnostic proved
that the first traversal entry reached after
`clk_disable_unused after: eth1tx` is `eth1rx`; this step adds only the
minimal `eth1rx` entry to the keep-enabled list in both the
`disable_unused` and `disable` branches and an `after` marker so the
next run distinguishes a stall inside the `eth1rx` disable/skip branch
from a stall later in traversal.

Diagnostic result: the kernel reaches `clk_disable_unused after: eth1rx` (eth1rx's keep-enabled branch returns cleanly), but boot still does not reach userspace, so the stall is later in traversal than eth1rx.

Build (apply `config/patch.linux` if needed, add the temporary
keep-enabled and post-`eth1rx` marker change under the existing Linux
patch workflow, rebuild kernel inputs, then generate the no-flag EVB
image):

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
mp135.evb:uart_expect sentinel="clk_disable_unused post-eth1tx next: eth1rx" timeout_ms=30000
mp135.evb:uart_expect sentinel="clk_disable_unused after: eth1rx" timeout_ms=5000
delay ms=45000
mp135.evb:uart_close
mark tag=evb_no_flag_eth1rx_after_marker
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
    lines = uart.splitlines()
    next_indexes = [i for i, line in enumerate(lines)
                    if 'clk_disable_unused post-eth1tx next: eth1rx' in line]
    after_indexes = [i for i, line in enumerate(lines)
                     if 'clk_disable_unused after: eth1rx' in line]
    if len(next_indexes) != 1 or len(after_indexes) != 1:
        return False
    no_flag = ('clk_ignore_unused' not in dts and
               'clk_ignore_unused' not in cmdline)
    no_userspace = ('Welcome to STM32MP135 EVB' not in uart and
                    'login:' not in uart)
    return (no_flag and
            'Linux version' in uart and
            next_indexes[0] < after_indexes[0] and
            no_userspace)
```

## WIP

### EVB names the clock visited after eth1rx

Build an EVB SD image whose bootargs omit `clk_ignore_unused` and whose
temporary Linux patch keeps `i2c4_k`, `stgen_k`, `tim15_k`, `bkpsram`,
`mdma`, `eth1tx`, and `eth1rx` enabled during unused-clock shutdown.
Extend the existing diagnostic markers only enough to print the next
unused-clock traversal entry reached after
`clk_disable_unused after: eth1rx`, so the captured UART log identifies
the first post-`eth1rx` clock name or proves that the traversal stops
before another named entry.

Build (apply `config/patch.linux` if needed, add the temporary
post-`eth1rx` next-entry marker under the existing Linux patch workflow,
rebuild kernel inputs, then generate the no-flag EVB image):

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
mp135.evb:uart_expect sentinel="clk_disable_unused after: eth1rx" timeout_ms=30000
mp135.evb:uart_expect sentinel="clk_disable_unused post-eth1rx next:" timeout_ms=5000
delay ms=45000
mp135.evb:uart_close
mark tag=evb_no_flag_post_eth1rx_next_clock
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
    lines = uart.splitlines()
    after_indexes = [i for i, line in enumerate(lines)
                     if 'clk_disable_unused after: eth1rx' in line]
    next_indexes = [(i, line) for i, line in enumerate(lines)
                    if 'clk_disable_unused post-eth1rx next:' in line]
    if not after_indexes or len(next_indexes) != 1:
        return False
    next_index, next_line = next_indexes[0]
    next_value = next_line.split('next:', 1)[1].strip()
    no_flag = ('clk_ignore_unused' not in dts and
               'clk_ignore_unused' not in cmdline)
    no_userspace = ('Welcome to STM32MP135 EVB' not in uart and
                    'login:' not in uart)
    return (no_flag and
            'Linux version' in uart and
            'clk_disable_unused after: eth1rx' in uart and
            after_indexes[-1] < next_index and
            bool(next_value) and
            no_userspace)
```

# Kernel clock bring-up

Find and fix the root cause that makes `clk_ignore_unused` necessary for
kernel boot. Determine whether the issue comes from the kernel patching
workflow, device tree contents, or another clock configuration problem.
After fixing the eval board, verify that the custom board also boots
without relying on `clk_ignore_unused`.
