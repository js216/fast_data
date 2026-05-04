# STM32MP135 EVB Skills

Work repo: `/home/agent3/fast_data/stm32mp135_test_board`.  Remote
bench: `/home/agent3/fast_data/test_serv/submit.py --server
http://localhost:8080` (test_serv lives as a sibling subdir of the
work repo so plans and helpers can reference it via simple relative
paths).

## Rules

- Hardware is locked only for the duration of a single job. Put DFU
  restore (reset via bench MCU), autoload stop, inventory, MSC
  write/verify, boot, and UART checks in one plan.
- **The bench has multiple `mp135` instances** (currently `mp135.evb`
  and `mp135.custom`). Plain `mp135:op` errors with `ambiguous: 2
  instances` when more than one is configured --- always qualify with
  the instance id, e.g. `mp135.evb:uart_open`. The grammar
  (per the `_control` plugin doc in `bench.ops.json`) is:
  `device:op` for currently-unique instances, `device.id:op` for a
  specific instance, and bare `control-verb args...` for verbs like
  `delay`, `inventory`, `mark`. Read `bench.devices.json` for the
  current instance ids per plugin.
- The MSC device belongs to the bootloader, not Linux. It only remains
  available if the bootloader autoload countdown is interrupted. After
  DFU flash, open UART and immediately send a stop byte (the current
  bootloader prints **only dots** during autoload --- there is no
  `Press any key to stop autoload` text), then confirm the `> ` prompt
  before attempting `msc:*` ops. If the bootloader reaches Linux,
  `msc.mp135` disappears.
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

- Inventory: `inventory refresh=true verify=true`. The `bench.ops.json`
  stream is the source of truth for op signatures and device specs ---
  do not consult the local `test_serv/` checkout for op semantics
  (the running server is at `/home/jk/projects/test_serv/` and may
  diverge).
- UART (plugin ops): `mp135:uart_open`, `mp135:uart_write data="..."`,
  `mp135:uart_expect sentinel="..." timeout_ms=N`, `mp135:uart_close`.
  `mp135:open` / `mp135:close` are **control verbs** from the plan
  grammar (`open`/`close` on any device pin/release its handle for
  the rest of the session) --- they will not appear in the inventory
  ops list and are usually unnecessary; the session lock already
  acquires the device lazily.
- MSC: `msc:write data=@sdcard.img offset_lba=0`, `msc:verify
  data=@sdcard.img offset_lba=0`, `msc:read n=... offset_lba=...`.
  `msc:read` is the **read-only** way to byte-compare what is on the
  card to a candidate image without touching the card --- pull `n`
  bytes into the `msc.read` stream and diff locally; useful before
  considering a `msc:write`. `msc:verify` is also read-only but only
  reports the *first* mismatch, not a count.
- DFU restore: `dfu:flash_layout layout=@flash.tsv no_reconnect=true`.
- Blobs: `flash.tsv=.scratch/test-serv/bootloader_flash.tsv`,
  `main.stm32=stm32mp135_test_board/bootloader/build/main.stm32`,
  `sdcard.img=stm32mp135_test_board/buildroot/output/images/sdcard.img`.
- `submit.py` crashes locally with `KeyError: 'timeline.log'` when the
  server rejects the plan (e.g. validation failure). The real reason
  is in `manifest.json` / sentinel `.txt` of the extracted artefact
  --- always read those, do not trust the submit-script exit code or
  traceback alone.
- `ssh.target.spec.ip` is **not stable** (currently DHCP-assigned by
  the lab network, but the bench config may also point it at a USB
  OTG ethernet gadget IP like `192.168.7.2`). Re-check `inventory`
  before assuming an address; before first `ssh:exec`, register the
  target's host key with `ssh:trust_host_key key="<algo> <base64>"`.

## Boot Test Pattern

Use the qualified instance id throughout (`mp135.evb:` and
`dfu.evb:`/`dfu.custom:` as appropriate) so the plan keeps working
when the bench has multiple boards configured. Examples below show the
EVB; swap `.evb` for `.custom` for the other board.

1. Reset DUT with bench MCU, DFU flash bootloader, open UART. The
   bootloader prints **only dots** (no autoload-prompt text); the stop
   window is roughly 5 s of dots at ~600 ms intervals. Send `x`
   blindly a few times right after `uart_open` to land within the
   window, then expect `> ` to confirm.
2. Send `\r` to clear the stop byte from the command buffer; expect
   `> ` again.
3. Optionally run `help` and expect a marker.
4. Close UART, wait/refresh inventory until `msc.mp135` appears, then
   write and verify `sdcard.img`. If `msc.mp135` is absent, assume the
   bootloader was not stopped or USB has not re-enumerated yet; reload
   the bootloader by DFU and repeat the autoload stop.
5. Reopen UART. Use `two` to load partitions 1 and 2 from MBR
   (kernel to `0xC2000000`, DTB to `0xC4000000`) --- avoid long
   `load_sd <n> <lba> <addr>` lines, which the bootloader UART has
   been observed to drop characters from. Then `jump`. **Send `jump`
   and `\r` as separate writes**, with a small delay between them ---
   sending `"jump\r"` in one write has been observed to concatenate
   with the next byte and turn the command into `jumproot` etc.
6. Expect `Linux version`, expected DTS model string, `Welcome to
   STM32MP135 EVB`, and `login:`.
7. Login as `root` / `root` when command execution is needed.

Minimal MSC stop/write fragment (bootloader has just been DFU-loaded):

```text
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
msc.mp135:write data=@sdcard.img offset_lba=0
msc.mp135:verify data=@sdcard.img offset_lba=0
```

Boot fragment (after MSC, with UART reopened at `> ` prompt):

```text
mp135.evb:uart_write data="two\r"
delay ms=9000
mp135.evb:uart_write data="jump"
delay ms=200
mp135.evb:uart_write data="\r"
mp135.evb:uart_expect sentinel="Jumping to address" timeout_ms=5000
mp135.evb:uart_expect sentinel="Linux version" timeout_ms=30000
mp135.evb:uart_expect sentinel="Welcome to STM32MP135 EVB" timeout_ms=30000
mp135.evb:uart_expect sentinel="login:" timeout_ms=15000
```

## SD vs NAND

- SD: MBR partition 1 kernel, partition 2 DTB, partition 3 rootfs on
  `/dev/mmcblk0p3`.
- NAND: build `nand`, use NAND bootloader config/commands, and use UBIFS
  bootargs: `ubi.mtd=rootfs root=ubi0:rootfs rootfstype=ubifs`.
