# STM32MP135 EVB Skills

Work repo: `/home/agent3/fast_data/stm32mp135_test_board`.  Remote
bench: `/home/agent3/test_serv/submit.py --server
http://localhost:8080`.

## Rules

- Hardware is locked only for the duration of a single job. Put DFU
  restore (reset via bench MCU), autoload stop, inventory, MSC
  write/verify, boot, and UART checks in one plan.
- The MSC device belongs to the bootloader, not Linux. It only remains
  available if the bootloader autoload countdown is interrupted. After
  DFU flash, open UART, wait for `Press any key to stop autoload`, send
  one byte immediately, and confirm the `> ` prompt before attempting
  `msc:*` ops. If the bootloader reaches Linux, `msc.mp135` disappears.
- Do not edit the top Makefile just to select EVB. Use command-line
  vars: `CFLAGS_EXTRA=-DEVB DTS=stm32mp135f-dk`.
- Use logs: `... 2>&1 | tee /tmp/stm32mp135-<task>.log` and tell user
  how to tail them if expecting a long build.
- If `msc.mp135` device is absent, reload the bootloader by DFU and stop
  autoload before using MSC.

## Build

- Patch Linux once when needed: `make -C stm32mp135_test_board patch`.
  Git status shows modified files in the kernel when patch is already
  applied. Do not commit to the kernel tree. Any kernel modifications
  must be done as separate patch files following the example of the
  `make patch` recipe.
- EVB SD image: `make -C stm32mp135_test_board CFLAGS_EXTRA=-DEVB
  DTS=stm32mp135f-dk boot kernel dtb br sd`.
- SD artifact: `buildroot/output/images/sdcard.img`.
- NAND artifact: `buildroot/output/images/nand.img`; build target
  `nand`. Eval board does not have NAND --- custom board only.

## Buildroot Changes

- Config: `config/buildroot.conf`; rebuild with `make -C
  stm32mp135_test_board br sd`.
- Rootfs overlay: `config/overlay`. Add simple files/programs there;
  `chmod +x` scripts under `usr/bin`.
- To install a package such as vim, enable its `BR2_PACKAGE_*` option in
  `config/buildroot.conf`, then rebuild `br sd`.

## Board Data

- EVB DTS: `config/stm32mp135f-dk.dts`.
- Custom board DTS: `config/custom.dts`.
- SD root bootargs for EVB: `root=/dev/mmcblk0p3 clk_ignore_unused`.
- Bootloader EVB support requires `CFLAGS_EXTRA=-DEVB`.

## test_serv Essentials

- Inventory: `inventory refresh=true verify=true`.
- UART: `mp135:open`, `mp135:uart_open`, `mp135:uart_write data="..."`,
  `mp135:uart_expect sentinel="..." timeout_ms=N`, `mp135:uart_close`,
  `mp135:close`.
- MSC: `msc:write data=@sdcard.img offset_lba=0`, `msc:verify
  data=@sdcard.img offset_lba=0`, `msc:read n=... offset_lba=...`.
- DFU restore: `dfu:flash_layout layout=@flash.tsv no_reconnect=true`.
- Blobs: `flash.tsv=.scratch/test-serv/bootloader_flash.tsv`,
  `main.stm32=stm32mp135_test_board/bootloader/build/main.stm32`,
  `sdcard.img=stm32mp135_test_board/buildroot/output/images/sdcard.img`.

## Boot Test Pattern

1. Reset DUT with bench MCU, DFU flash bootloader, open UART, wait for
   `Press any key to stop autoload`, then send any byte immediately to
   stop autoload.
2. Send a blank line if the stop byte remains in the command buffer.
3. Optionally run `help` and expect a marker.
4. Close UART, wait/refresh inventory until `msc.mp135` appears, then
   write and verify `sdcard.img`. If `msc.mp135` is absent, assume the
   bootloader was not stopped or USB has not re-enumerated yet; reload
   the bootloader by DFU and repeat the autoload stop.
5. Reopen UART, run `two`, expect `> `, run `jump`.
6. Expect `Linux version`, expected DTS model string, `Welcome to
   STM32MP135 EVB`, and `login:`.
7. Login as `root` / `root` when command execution is needed.

Minimal MSC stop/write fragment:

```text
mp135:uart_expect sentinel="Press any key to stop autoload" timeout_ms=15000
mp135:uart_write data="x"
mp135:uart_expect sentinel="> " timeout_ms=5000
mp135:uart_write data="\r"
mp135:uart_expect sentinel="> " timeout_ms=3000
mp135:uart_close
mp135:close
delay ms=5000
inventory refresh=true verify=false
msc:write data=@sdcard.img offset_lba=0
msc:verify data=@sdcard.img offset_lba=0
```

## SD vs NAND

- SD: MBR partition 1 kernel, partition 2 DTB, partition 3 rootfs on
  `/dev/mmcblk0p3`.
- NAND: build `nand`, use NAND bootloader config/commands, and use UBIFS
  bootargs: `ubi.mtd=rootfs root=ubi0:rootfs rootfstype=ubifs`.
