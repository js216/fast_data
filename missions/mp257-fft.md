# STM32MP257F-DK basic demo

Build a lean STM32MP257F-DK image, flash it over DFU without changing boot
switches, boot from the flashed SD card, and confirm `fft_cpu` renders on LVDS.

The image follows the upstream STM32MP257F-DK Buildroot setup with only the
extra packages and assets needed for this FFT demo.

### Compile the SD-card image

Build the Buildroot image from the local FFT defconfig. This produces
`sdcard.img` plus the USB DFU TF-A/FIP artifacts used by `mp257-flash.tsv`.

Build:

```
make -C stm32mp257_test_board/buildroot \
  BR2_EXTERNAL=$PWD/stm32mp257_test_board/buildroot-external-st \
  BR2_DEFCONFIG=$PWD/stm32mp257_test_board/config/mp257f_dk_fft_defconfig \
  defconfig
make -C stm32mp257_test_board/buildroot optee-os-dirclean
make -C stm32mp257_test_board/buildroot uboot-dirclean
make -C stm32mp257_test_board/buildroot linux-rebuild
make -C stm32mp257_test_board/buildroot
```

Artifacts:

```
stm32mp257_test_board/buildroot/output/images/sdcard.img
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(_extract_dir):
    sd = Path("stm32mp257_test_board/buildroot/output/images/sdcard.img")
    return sd.is_file() and sd.stat().st_size > 30000000
```

### Flash the SD image over DFU

Reset into ROM DFU, serial-boot the generated firmware, and write `sdcard.img`
to mmc0. The board is left in U-Boot `stm32prog` unless it auto-boots.

Artifacts:

```
stm32mp257_test_board/buildroot/output/images/tf-a-stm32mp257_dk_usb.stm32
stm32mp257_test_board/buildroot/output/images/fip-ddr-stm32mp257_dk_usb.bin
stm32mp257_test_board/buildroot/output/images/fip-stm32mp257_dk_usb.bin
stm32mp257_test_board/buildroot/output/images/sdcard.img
stm32mp257_test_board/config/mp257-flash.tsv
```

Test (max 120 s):

```
bench_mcu:reset_dut
mp257.evb-uart1:uart_open
delay ms=6000
inventory
dfu.mp257:flash_layout layout=@mp257-flash.tsv
mp257.evb-uart1:uart_expect sentinel="NOTICE:  CPU: STM32MP257" timeout_ms=3000
mp257.evb-uart1:uart_expect sentinel="Boot over usb0!" timeout_ms=3000
mp257.evb-uart1:uart_expect sentinel="Phase=END" timeout_ms=3000
mp257.evb-uart1:uart_close
mark tag=flash
```

Verify:

```
def check(extract_dir):
    return Verification.manifest_clean(extract_dir)
```

### Boot to the shell prompt

Inherits the flashed board. Exit `stm32prog` if needed, ask U-Boot to boot mmc0,
and wait for the autologin root shell prompt `~ #`.

Build: nothing required.

Test (max 60 s):

```
mp257.evb-uart1:uart_open
mp257.evb-uart1:uart_write data="\x03\x03"
delay ms=2000
mp257.evb-uart1:uart_write data="\r"
mp257.evb-uart1:uart_write data="run bootcmd_mmc0\r"
mp257.evb-uart1:uart_expect sentinel="~ #" timeout_ms=55000
mp257.evb-uart1:uart_close
mark tag=boot
```

Verify:

```
def check(extract_dir):
    return Verification.manifest_clean(extract_dir)
```

### Verify both A35 cores are online

Inherits the root shell. Read `/proc/cpuinfo` and require both Cortex-A35
cores to appear as online Linux processors before continuing to network tests.

Build: nothing required.

Test (max 20 s):

```
mp257.evb-uart1:uart_open
mp257.evb-uart1:uart_write data="\r"
mp257.evb-uart1:uart_expect sentinel="~ #" timeout_ms=10000
mp257.evb-uart1:uart_write data="n=$(grep -c '^processor' /proc/cpuinfo); echo CPUINFO_CORES:$n; cat /proc/cpuinfo\r"
mp257.evb-uart1:uart_expect sentinel="CPUINFO_CORES:2" timeout_ms=5000
mp257.evb-uart1:uart_expect sentinel="~ #" timeout_ms=5000
mp257.evb-uart1:uart_close
mark tag=cpuinfo_dual_core
```

Verify:

```
def check(extract_dir):
    import re
    if not Verification.manifest_clean(extract_dir):
        return False
    t = Verification.load_stream_text(extract_dir, 'mp257.evb-uart1.uart', 'utf-8')
    return (
        'CPUINFO_CORES:2' in t
        and len(re.findall(r'^processor\s*:', t, flags=re.M)) >= 2)
```

### Verify the board has network + internet

Inherits the root shell. Confirm `eth0` has a bench DHCP address and can ping
8.8.8.8.

Build: nothing required.

Test (max 60 s):

```
mp257.evb-uart1:uart_open
mp257.evb-uart1:uart_write data="\r"
mp257.evb-uart1:uart_expect sentinel="~ #" timeout_ms=10000
mp257.evb-uart1:uart_write data="ip a show eth0\r"
mp257.evb-uart1:uart_expect sentinel="inet 172.25." timeout_ms=8000
mp257.evb-uart1:uart_write data="ping -c1 -W3 8.8.8.8\r"
mp257.evb-uart1:uart_expect sentinel="bytes from 8.8.8.8" timeout_ms=8000
mp257.evb-uart1:uart_close
mark tag=net
```

Verify:

```
def check(extract_dir):
    import re
    if not Verification.manifest_clean(extract_dir):
        return False
    t = Verification.load_stream_text(extract_dir, 'mp257.evb-uart1.uart', 'utf-8')
    return bool(re.search(r'inet 172\.25\.\d+\.\d+', t)) and ('bytes from 8.8.8.8' in t)
```

### Build, deliver, and run fft_cpu over SSH

Inherits the network-up board. Build `fft_cpu`, copy it over SSH, start it
detached, and confirm the process reports its DRM connector. The image contains
the pinned Dropbear host key and bench public key; `ip=` targets the board's
current DHCP lease.

Build:

```
mkdir -p stm32mp257_test_board/tools/build
stm32mp257_test_board/buildroot/output/host/bin/aarch64-none-linux-gnu-gcc \
  --sysroot=stm32mp257_test_board/buildroot/output/staging \
  -O2 -Istm32mp257_test_board/buildroot/output/staging/usr/include/libdrm \
  stm32mp257_test_board/tools/fft_cpu.c -ldrm -lfftw3f -lm \
  -o stm32mp257_test_board/tools/build/fft_cpu
test -x stm32mp257_test_board/tools/build/fft_cpu
```

Artifacts:

```
stm32mp257_test_board/tools/build/fft_cpu
```

Test (max 30 s):

```
ssh.any:trust_host_key key="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIH7w8Lo6ZZnmCgaHoE8IUnEgupawdkSdh0rfPmhyjjjV mp257-fft" ip="172.25.0.131"
ssh.any:put data=@fft_cpu path="/usr/bin/fft_cpu" ip="172.25.0.131"
ssh.any:exec command="chmod +x /usr/bin/fft_cpu; setsid /usr/bin/fft_cpu >/tmp/fft_cpu.log 2>&1 </dev/null & sleep 3; uname -a; echo FFTPID=$(pidof fft_cpu); echo SSH_LOGIN_OK; head -8 /tmp/fft_cpu.log" ip="172.25.0.131" timeout_ms=15000
mark tag=ssh_fft
```

Verify:

```
def check(extract_dir):
    import re
    if not Verification.manifest_clean(extract_dir):
        return False
    t = Verification.load_stream_text(extract_dir, 'ssh.exec', 'utf-8')
    return ('SSH_LOGIN_OK' in t) and ('6.6.78' in t) \
        and bool(re.search(r'FFTPID=\d', t)) and ('DRM: conn' in t)
```
