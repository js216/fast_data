# Unix v7 on the custom STM32MP135 board

### Build the kernel + SD image

Build the MP135 kernel (linked at SYSRAM), wrap it in the STM32 image header
the ROM expects (load/entry = 0x2FFE0000), build the V7 root filesystem image,
and emit a one-line DFU layout that loads `unix.stm32` as the FSBL.

Build:

```
make -C unix-v7-c99 BOARD=mp135 boot/unix boot/rootfs.img
arm-none-eabi-objcopy -O binary unix-v7-c99/boot/unix unix-v7-c99/boot/unix.bin
python3 stm32mp135_test_board/bootloader/scripts/stm32_header.py \
    -e unix-v7-c99/boot/unix -b unix-v7-c99/boot/unix.bin \
    -o unix-v7-c99/boot/unix.stm32 -t .text
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' '-' '0x01' 'fsbl1-boot' 'Binary' 'none' '0x0' 'unix.stm32' > unix-v7-c99/boot/unix.tsv
make -C stm32mp135_test_board/bootloader -j$(nproc)
```

Artifacts:

```
unix-v7-c99/boot/unix.stm32
unix-v7-c99/boot/rootfs.img
unix-v7-c99/boot/unix.tsv
stm32mp135_test_board/bootloader/build/main.stm32
```

Test: no hardware.

### Provision the SD card with the V7 root filesystem

Reset the custom board, DFU-load the test-board bootloader, hold it at its
prompt, then write the V7 filesystem image to the SD card over USB mass
storage starting at LBA 0 (block 0 = the V7 superblock the kernel reads).

Build (reset the DUT into ROM/DFU):

```
printf '%s\n' 'description "reset custom DUT"' 'bench_mcu:reset_dut2' > "$RUNPY_WORKDIR/reset.plan"
python3 test_serv/submit.py --server http://localhost:8080 --wait 20 "$RUNPY_WORKDIR/reset.plan"
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
unix-v7-c99/boot/rootfs.img
```

Test (max 30 s):

```
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
mp135.custom:uart_close
inventory
msc.custom:write data=@rootfs.img offset_lba=0 min_rate_Bps=2000000
mark tag=sd_provisioned
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    return Verification.op_succeeded(ops, 'msc.custom', 'write')
```

### Boot UNIX and reach the shell

Reset the board and DFU-load `unix.stm32` directly: the ROM copies it into
SYSRAM and runs it.  UNIX brings up DDR + SDMMC, mounts root off the SD card,
runs init, and -- in single-user, exactly as the QEMU build does -- execs
`/bin/sh` on the console, reaching the `# ` prompt over UART4.  Running a
command then proves the console (tty line discipline + USART driver), process
creation (fork/exec), and the SD block driver all work: the shell forks,
execs `/bin/echo` off the SD card, and prints the result back over the tty.

Build (reset the DUT into ROM/DFU):

```
printf '%s\n' 'description "reset custom DUT"' 'bench_mcu:reset_dut2' > "$RUNPY_WORKDIR/reset.plan"
python3 test_serv/submit.py --server http://localhost:8080 --wait 20 "$RUNPY_WORKDIR/reset.plan"
```

Artifacts:

```
unix-v7-c99/boot/unix.stm32
unix-v7-c99/boot/unix.tsv
```

Test (max 30 s):

```
delay ms=2000
dfu.custom:flash_layout layout=@unix.tsv no_reconnect=true
mp135.custom:uart_open
mp135.custom:uart_expect sentinel="# " timeout_ms=20000
mp135.custom:uart_write data="ls /bin | wc -l ; cat /etc/passwd ; echo MP135_UNI''X_OK\r"
mp135.custom:uart_expect sentinel="MP135_UNIX_OK" timeout_ms=10000
mp135.custom:uart_close
mark tag=boot_unix
```

A single chained command line lets the shell sequence the three commands
itself, so the bench types once and waits for one end sentinel -- avoiding the
fragile per-command prompt round-trips (typing the next command before the
shell has re-issued its prompt garbles input).  The empty-string concatenation
in `MP135_UNI''X_OK` means that literal appears only as the shell's output, not
in the echoed input line.

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    # Reaching the final sentinel means the shell processed every prior command
    # and stayed responsive: the "ls /bin | wc -l" pipe exercises fork + two
    # execs off the SD + a pipe; "cat /etc/passwd" reads a file from the SD;
    # and the echo proves the shell itself ran (the empty-string concatenation
    # means the literal MP135_UNIX_OK appears only as output, not echoed input).
    # root's entry in /etc/passwd confirms cat actually read the file.
    return 'MP135_UNIX_OK' in uart and 'root:' in uart
```
