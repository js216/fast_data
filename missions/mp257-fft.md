# STM32MP257F-DK basic demo

Build the bare-metal FSBL (stm32mp257_test_board/bootloader -- replaces TF-A,
OP-TEE and U-Boot), DFU-load it without changing boot switches, stage the
kernel + dtb on the SD card through the FSBL's USB mass-storage export, boot
Linux through the FSBL's own EL3 PSCI, and confirm `fft_cpu` renders on LVDS.

The Linux image follows the upstream STM32MP257F-DK Buildroot setup with only
the extra packages and assets needed for this FFT demo; the kernel Image and
dtb are taken from the existing Buildroot output tree (a prior `make` in
buildroot/ must have populated output/).

### Flash the FSBL and stage Linux on the SD card

Build the bootloader, DFU-load it (SYSRAM-resident, never re-enters DFU:
no_reconnect), export the SD card over USB MSC, and write the kernel Image
and dtb to the raw staging area (kernel at LBA 262144 = 128 MiB, dtb at LBA
327680 = 160 MiB -- clear of the GPT partitions and the backup GPT). The
FSBL's `boot` command loads up to 24 MiB of kernel, hence the size guard.

Build:

```
make -C stm32mp257_test_board/bootloader \
  CROSS_COMPILE=$PWD/stm32mp257_test_board/buildroot/output/host/bin/aarch64-none-linux-gnu-
test -f stm32mp257_test_board/bootloader/build/bootloader.stm32
cp stm32mp257_test_board/buildroot/output/build/linux-custom/arch/arm64/boot/Image \
  stm32mp257_test_board/bootloader/build/linux-image.bin
cp stm32mp257_test_board/buildroot/output/images/stm32mp257f-dk.dtb \
  stm32mp257_test_board/bootloader/build/linux-dtb.bin
test $(stat -c%s stm32mp257_test_board/bootloader/build/linux-image.bin) -le 25165824
test $(stat -c%s stm32mp257_test_board/bootloader/build/linux-dtb.bin) -le 262144
```

Artifacts:

```
stm32mp257_test_board/bootloader/build/bootloader.stm32
stm32mp257_test_board/bootloader/flash.tsv
stm32mp257_test_board/bootloader/build/linux-image.bin
stm32mp257_test_board/bootloader/build/linux-dtb.bin
```

Test (max 240 s):

```
bench_mcu:reset_dut
mp257.evb-uart1:uart_open
delay ms=4000
inventory
dfu.mp257:flash_layout layout=@flash.tsv no_reconnect=true
mp257.evb-uart1:uart_expect sentinel="bootloader" timeout_ms=10000
mp257.evb-uart1:uart_write data="usb\n"
mp257.evb-uart1:uart_expect sentinel="USB MSC up" timeout_ms=20000
delay ms=8000
msc.mp257:write data=@linux-image.bin offset_lba=262144
msc.mp257:write data=@linux-dtb.bin offset_lba=327680
mp257.evb-uart1:uart_write data="q"
mp257.evb-uart1:uart_expect sentinel="stopped" timeout_ms=5000
mp257.evb-uart1:uart_close
mark tag=fsbl_stage
```

Verify:

```
def check(extract_dir):
    import re
    if not Verification.manifest_clean(extract_dir):
        return False
    t = Verification.load_stream_text(extract_dir, 'mp257.evb-uart1.uart', 'utf-8')
    # host wrote the staged images through our WRITE10 path
    m = re.search(r'stopped \(rd \d+ wr (\d+)', t)
    return ('USB MSC up' in t) and m is not None and int(m.group(1)) > 0
```

### Boot Linux via the bare-metal FSBL

The FSBL is still at its console prompt. `boot` initialises DDR, loads the
staged kernel + dtb into DDR, opens the RIF/RISAF firewalls and the GIC to
the non-secure world, and enters the kernel at EL2 with the FSBL's minimal
PSCI resident at EL3 (CPU_ON brings up the second core).

Build: nothing required.

Test (max 180 s):

```
mp257.evb-uart1:uart_open
mp257.evb-uart1:uart_write data="\r"
mp257.evb-uart1:uart_expect sentinel=">" timeout_ms=5000
mp257.evb-uart1:uart_write data="boot\n"
mp257.evb-uart1:uart_expect sentinel="Linux version 6.6.78" timeout_ms=60000
mp257.evb-uart1:uart_expect sentinel="~ #" timeout_ms=90000
mp257.evb-uart1:uart_close
mark tag=fsbl_boot
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    t = Verification.load_stream_text(extract_dir, 'mp257.evb-uart1.uart', 'utf-8')
    return ('boot: Linux Image@0x84000000 dtb@0x86000000' in t) \
        and ('Linux version 6.6.78' in t) \
        and ('SMP: Total of 2 processors activated' in t) \
        and ('~ #' in t)
```

### Verify both A35 cores are online

Inherits the root shell. Read `/proc/cpuinfo` and require both Cortex-A35
cores to appear as online Linux processors before continuing to network tests.

Build: nothing required.

Test (max 60 s):

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
ssh.any:trust_host_key key="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIH7w8Lo6ZZnmCgaHoE8IUnEgupawdkSdh0rfPmhyjjjV mp257-fft" ip="172.25.0.159"
ssh.any:put data=@fft_cpu path="/usr/bin/fft_cpu" ip="172.25.0.159"
ssh.any:exec command="chmod +x /usr/bin/fft_cpu; setsid /usr/bin/fft_cpu >/tmp/fft_cpu.log 2>&1 </dev/null & sleep 3; uname -a; echo FFTPID=$(pidof fft_cpu); echo SSH_LOGIN_OK; head -8 /tmp/fft_cpu.log" ip="172.25.0.159" timeout_ms=15000
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
