# TODO: QSPI FPGA-to-MPU Fast Data Transfer

### Mission Target

Demonstrate bit-accurate sustained data transfer from FPGA to STM32MP135
MPU using the QUADSPI peripheral:

- Single-lane path: prove at least 100 Mbps wall-rate on the
  auto-consume stream path with `a 1`, `p 5 1`, and
  `A 33554432 0 1`; expected summary includes `stream ... firsterr=-1
  ... auto=on, presc=5, qspi_hz=656000000`.
- Quad-lane requirement: at least 200 Mbps, ideally higher, with no data
  errors.

### Mission Snapshot - 2026-05-01T10:15-07:00

- Single-lane mission target is achieved on the fast auto-stream path.
  Multiple ordered runs passed block 6 with `A 33554432 0 1`, CRC match,
  `firsterr=-1`, `auto=on`, and wall rates above 100 Mbps. Latest
  evidence before this snapshot: ledger `2026-05-01T10:08:20 spi 6`,
  blocks 1-6 passed, single-lane wall rate `106.861Mbps`.
- Quad-lane mission target is not yet achieved. The active ordered-suite
  blocker is block 7, `Check quad stream @ presc=11 wall rate >= 200
  Mbps`. The transfer path reaches roughly `169.4Mbps`, but correctness
  fails before the 200 Mbps floor can be accepted.
- The quad failure is now narrowed upstream of auto-consume, DDR, MDMA,
  and hardware CRC. A 16-byte CPU-polled raw quad probe at the same
  `p 11 1` setting failed with `firsterr=7` and prefix
  `00 01 02 03 04 05 06 60 77 08 09 0a 00 00 0f f1`.
- The existing `spi_quad_debug.bin` observer also failed to show a clean
  intended quad nibble stream during a 16-byte raw probe. Treat that as
  diagnostic evidence for a quad selected-frame / FPGA state-framing
  problem, not as a bit-identical reproduction because the debug
  bitstream shifted the MP135 prefix to `firsterr=8`.
- Next active handoff is evidence-only:
  `quad-registered-prefix-model`. Build a deterministic local model of
  the current registered quad state machine and inferred CS-selected
  microframe boundaries. Stop after it either reproduces the normal
  short16 bad prefix and names one narrow source edit, or identifies the
  one missing observable needed before source work.

### Next Steps

- Current SPI working tree has an unverified 1-lane IO0 timing change:
  IO0 is direct/unregistered for STM32 peripheral reads while IO1 stays
  falling-edge registered for GPIO bit-bang preflight.
- Corrected diagnosis: this is not a DFU polling race. When the MP135 is
  in bootloader it presents an MSC interface, so no device is expected to
  match `dfu`; the MP135 must be reset via `bench_mcu` into the expected
  state before any `dfu:flash_layout` step.
- Iteration 3 Worker added an `mp135: reset into DFU before flash` chunk
  (`bench_mcu:reset_dut` plus `delay ms=1200`) and applied it to later
  DFU flash blocks. The single hardware baseline failed at block 1 GPIO
  preflight because that tested build also delayed block 1, shifting the
  timed FPGA pin-walk observations.
- Iteration 4 regenerated `build/spi/TEST.md` from current source and ran
  one baseline. `make sim`, `make bitstream`, and `make all` passed, but
  hardware failed at block 1 `Check SPI header wiring via GPIO preflight`:
  `LookupError: no device matches dfu`, no `JEDEC ID:`, required devices
  `bench_mcu`, `dfu`, `fpga`, `mp135`.
- User correction: while the MP135 bootloader presents MSC, no device is
  expected to match `dfu`; this is not a DFU polling race. Block 1 must
  also reset the MP135 via `bench_mcu` into the DFU-capable state before
  `dfu:flash_layout`.
- Iteration 5 fixed the block 1 DFU/no-device issue by using the
  bench-MCU reset plus 1200 ms settle before `dfu:flash_layout` and
  moving `fpga:program bin=@spi_pin_walk.bin` after the flash. `make sim`,
  `make bitstream`, and `make all` passed. Hardware reached `JEDEC ID:`,
  proving the DFU path is no longer the active blocker.
- Current hardware blocker is still block 1 GPIO preflight. Iteration 6
  added one extra `G` sample after only 100 ms. Latest observed masks were
  `0x3a 0x12 0x00 0x01 0x02 0x04 0x08 0x10 0x10` versus expected trailing
  masks `0x00 0x01 0x02 0x04 0x08 0x10 0x20`.
- Likely cause: moving `fpga:program` after the firmware flash starts the
  timed `spi_pin_walk` high-Z/one-hot schedule after the MP135 app is
  already booted or producing early `g/G` readbacks. The first two masks
  are therefore pre-drive/transient observations; the real pin walk then
  begins at `0x00` but the test closes before sampling final `0x20`.
- Iteration 7 made block 1 pass by using a full 2100 ms dwell before the
  final `G` sample, and block 2 passed. `make sim`, `make bitstream`,
  and `make all` passed with no warning delta. Hardware then failed at
  block 3 `Check 1lane peripheral raw read returns 1024-byte
  incrementing pattern`: `1lane raw mismatch at 1: got 00, expected 01`;
  capture was all zeroes. This isolated the active failure to the dirty
  1-lane peripheral/raw path, because the same `spi_1lane.bin` still
  returned the incrementing pattern through the IO1 GPIO bit-bang
  preflight.
- Iteration 8 applied the narrow 1-lane timing fix: explicit fabric
  falling-edge launch state feeds unregistered output-enable pads for
  IO0 and IO1, with the SPI `SB_IO` model, 1-lane testbench, and netlist
  checker updated to match. The Worker reported `make sim`,
  `make bitstream`, and `make all` passed. Latest hardware evidence is
  ledger `2026-04-30T17:40:42 spi 5`: blocks 1-5 passed, block 3 is
  fixed, and the first failure is block 6 `Check 1lane @ presc=203
  pattern correct`.
- Block 6 timeout root cause is proven stale MP135 QSPI firmware. The
  Worker rebuilt only `stm32mp135_test_board/baremetal/qspi` with
  `make all`; `fpga/build/spi/main.stm32` is a symlink to the rebuilt
  `main.stm32`, hash
  `8435717a4558cac0f55b560f1890b8983e78c3ea208fefb30e40b5a6e989eb8d`.
  A new hardware run from `fpga/build/spi` with the required shared
  ledger/log passed blocks 1-6. Block 6 UART reached
  `BENCHDBG poll_enter`, `BENCHDBG poll_done`, `BENCHDBG cmd_post`, and
  final `firsterr=-1`, so the previous block 6 stall is no longer active.
- Latest hardware evidence after the stale MP135 QSPI firmware rebuild is
  ledger `2026-04-30T19:30:03 spi 7`: blocks 1-7 passed. Block 8
  `Check 1lane @ presc=15 pattern correct` failed. The generated block is
  the same 1-lane 1 MiB bench command as block 7 except `p 15` instead of
  `p 63` and an 8000 ms sentinel timeout. UART reached
  `BENCHDBG poll_done` and `cmd_post` with `firsterr=2`; the firmware
  reported `crc32=d1bcc1e2`, `expect=04d0e435`, and first bytes
  `00 01 04 0c 20 41 83 88 14 41 46 0c 38 79 02 4a`. The active question
  is why the 1-lane stream corrupts immediately at byte 2 at `presc=15`
  while `presc=63` passes.
- Latest Worker evidence-only comparison of block 7 and block 8 artifacts
  passed: the only mission-relevant stimulus change before corruption is
  QSPI prescaler. Both blocks used the same generated sequence, firmware
  image hash
  `8435717a4558cac0f55b560f1890b8983e78c3ea208fefb30e40b5a6e989eb8d`,
  opcode `0b`, length `1048576`, line mode `1`, dummy `0`,
  reset/DFU/UART sequence, and bench command `b 1048576 0 1`; block 7
  `p 63` passed and block 8 `p 15` failed. Block 8 reached
  `poll_enter`, `poll_done`, and `cmd_post`; firmware reported
  `firsterr=2`, CRC `d1bcc1e2` versus expected `04d0e435`, and bytes
  `00 01 04 0c 20 41 83 88 14 41 46 0c 38 79 02 4a`.
  `errors.log` contained only the expected sentinel timeout after the
  firmware had already reported the bad transfer.
- Latest Worker evidence-only timing inspection answered the prior
  timing-margin question. The QSPI kernel clock is 656 MHz. At `p 63`,
  SCLK is 10.25 MHz, period is 97.560975610 ns, and the FPGA
  falling-edge IO0 launch to the next STM32 mode-0 rising-edge sample is
  48.780487805 ns; block 7 passes. At `p 15`, SCLK is 41.0 MHz, period
  is 24.390243902 ns, and the same launch-to-sample interval is
  12.195121951 ns; block 8 fails. The current simulation/model drives
  IO0/IO1 directly with no pad delay, board delay, STM32 input
  delay/setup/hold, or duty-cycle distortion, so local ideal simulation
  passes and cannot distinguish the passing `p 63` case from the failing
  `p 15` case.
- Latest Worker evidence-only sample-shift experiment disproved STM32
  sample shifting as a sufficient fix. The Worker confirmed from
  `stm32mp135_test_board/baremetal/qspi/src/cli.c` that `p 15 1` sets
  `sshift=1`, temporarily changed only generated `build/spi/TEST.md`
  block 8 from `p 15` to `p 15 1`, restored `TEST.md` afterward, and ran
  hardware. Ledger `2026-04-30T19:43:32 spi 7` passed block 7 `p 63`;
  modified block 8 `p 15 1` failed with the same signature:
  `presc=15 sshift=1 dlyb=0 unit=0`, `firsterr=2`,
  `crc32=d1bcc1e2` versus expected `04d0e435`, first bytes
  `00 01 04 0c 20 41 83 88 14 41 46 0c 38 79 02 4a`. The active
  question moves to FPGA IO0 launch timing for the 1-lane STM32
  peripheral path.
- The previous iteration cap has been removed by the user. Source remains
  uncommitted and not fully verified: `src/spi.nw`,
  `tb/tb_spi_1lane.sv`, `verilog/SB_IO.v`, and generated
  `verilog/spi.v` are modified in the `fpga` worktree. Do not commit
  these changes until all required SPI hardware blocks have been
  attempted and passed.
- Latest Worker implemented the IO0-only launch-delay LUT experiment in
  the existing SPI worktree. Local `make -C build/spi sim`,
  `make -C build/spi bitstream`, and `make -C build/spi all` passed with
  no final warning delta.
- The selected hardware evidence for that IO0-delay edit was invalid and
  inconclusive. Ledger entries `2026-04-30T19:50:01 spi 0` and
  `2026-04-30T19:50:30 spi 0` came from isolated `run_md.py --block 7`
  and `--block 6` invocations. Those generated blocks do not contain
  `fpga:program bin=@spi_1lane.bin`; programming occurs earlier in the
  normal TEST.md sequence. The observed all-`ff`/`JEDEC ID: ff ff ff`
  style result and `p 63` CRC `956bac74` with `firsterr=0` therefore
  looked like the FPGA was not driving the intended SPI stream, not like
  a valid repeat of the prior immediate byte-2 `p 15` corruption.
- Valid ordered-path evidence now disproves the one-LUT IO0-only launch
  delay as a fix. Ledger `2026-04-30T19:56:30 spi 7` came from one normal
  ordered `run_md.py` invocation with the current IO0-only LUT-delay edit,
  no `--block`, no `--full`, and no source edits. The normal path included
  the FPGA programming blocks. Blocks before block 8 passed, including the
  control `[7/31 PASS] Check 1lane @ presc=63 pattern correct` with CRC
  `04d0e435`. The first failing block remained `[8/31] Check 1lane @
  presc=15 pattern correct`, hash `7c67dd08de9536a0`, with the same
  signature: `presc=15 sshift=0 dlyb=0 unit=0`, `firsterr=2`, CRC
  `d1bcc1e2` versus expected `04d0e435`, first bytes
  `00 01 04 0c 20 41 83 88 14 41 46 0c 38 79 02 4a`, and timeout waiting
  for `, firsterr=-1`. The IO0-only LUT delay did not disturb `p63` but
  did not fix `p15`; do not commit it unless a later Manager explicitly
  keeps it for diagnostic value.
- Latest Worker cleanup removed the failed IO0-only LUT diagnostic and
  returned the 1-lane path to the symmetric shape. `fpga/src/spi.nw` now
  has one fabric `negedge sclk` `dout_one` launch register feeding both
  IO0 and IO1; regenerated `verilog/spi.v`, `verilog/SB_IO.v`, and
  `tb/tb_spi_1lane.sv` are consistent. Searches found no
  `SB_LUT4`, `io0_launch_delay`, `launch-delay`, `LUT buffer`,
  `LUT_INIT`, or `dout_one_io0` in the SPI source/generated/checker files.
  `make -C build/spi sim`, `make -C build/spi bitstream`, and
  `make -C build/spi all` passed with no warning delta.
- Current valid ordered-path baseline after cleanup is ledger
  `2026-04-30T20:02:24 spi 7`: block 7 `[7/31 PASS] Check 1lane @
  presc=63 pattern correct` remained green with CRC `04d0e435` and
  `firsterr=-1`; block 8 `[8/31 FAIL] Check 1lane @ presc=15 pattern
  correct` still failed with the same byte-2 signature:
  `presc=15 sshift=0 dlyb=0 unit=0`, `firsterr=2`, CRC `d1bcc1e2`,
  and first bytes `00 01 04 0c 20 41 83 88 14 41 46 0c 38 79 02 4a`.
  A symmetric earlier-launch experiment was the next timing question.
- Latest Worker implemented that symmetric earlier-launch experiment by
  changing the 1-lane path so shared `dout_one` updates on
  `posedge sclk` after each sample edge and feeds unregistered
  output-enable pads for both IO0 and IO1. `verilog/spi.v` was
  regenerated; IO0/IO1 symmetry was preserved; `make -C build/spi sim`,
  `make -C build/spi bitstream`, and `make -C build/spi all` passed with
  no warning delta.
- Ordered hardware evidence invalidates the symmetric earlier-launch
  edit. Ledger `2026-04-30T20:08:19 spi 1` passed block 1, then failed
  block 2 `Check 1lane bit-bang read returns incrementing pattern`
  before reaching blocks 7 or 8. Block 2 expected incrementing bytes but
  got only even bytes:
  `00 02 04 06 08 0a 0c 0e 10 12 14 16 18 1a 1c 1e`. The sentinel had
  `n_errors=0` and there was no `errors.log` tail. Therefore the
  posedge/unregistered symmetric earlier-launch strategy does not answer
  the block 7/8 prescaler question and should not be committed unless a
  later Manager explicitly keeps it for diagnostic value.
- Latest Worker reverted only the failed symmetric
  posedge/unregistered earlier-launch diagnostic and restored the last
  valid shared falling-edge 1-lane launch shape. `fpga/src/spi.nw`
  `<<SPI streaming: single lane>>` again launches one shared `dout_one`
  with `always @(posedge cs_n or negedge sclk)` and mirrors it to IO0 and
  IO1; `verilog/spi.v` was regenerated, and generated support files
  remain consistent. `make -C build/spi sim`, `make -C build/spi
  bitstream`, and `make -C build/spi all` passed with no warning delta.
- Current valid ordered-path baseline after restored cleanup is ledger
  `2026-04-30T20:14:41 spi 7`: block 2 passed again with
  `00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f`, block 7 `p63`
  passed with CRC `04d0e435`, and block 8 `p15` remains the active
  blocker. Block 8 failed with `presc=15 sshift=0 dlyb=0 unit=0`,
  `firsterr=2`, CRC `d1bcc1e2` versus expected `04d0e435`, and first
  bytes `00 01 04 0c 20 41 83 88 14 41 46 0c 38 79 02 4a`.
- Latest Worker evidence-only bit/phase analysis made no edits and ran
  no build or hardware. Using ledger/log `2026-04-30T20:14:41 spi 7`,
  expected first bytes `00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e
  0f`, and observed block 8 `p15` bytes `00 01 04 0c 20 41 83 88 14 41
  46 0c 38 79 02 4a`, the Worker tested fixed byte slip, fixed
  MSB-first bit slip, LSB/MSB reversal, per-byte rotate, single
  dropped/duplicated bit, and periodic one-bit drop. None fit well. The
  best-supported relationship is deterministic corruption starting at
  `firsterr=2` but not a stable realignment, consistent with STM32
  sampling near the IO0 data transition at `p15`: a data-valid/setup/hold
  failure rather than a clean byte or bit slip. Since `p63` passes while
  `p15` fails, the active question remains launch-to-sample margin.
- Latest Worker implemented the true falling-edge registered `SB_IO`
  pad-launch experiment by restoring direct
  `dout_lane[0/1] = data_byte[7 - phase]`, removing the fabric
  `dout_one` presenter, keeping the 1-lane pads at
  `PIN_TYPE=6'b100101` and `NEG_TRIGGER=1'b1`, and updating the
  simulation/netlist prose and checks. Local `make -C build/spi sim`,
  `make -C build/spi bitstream`, and `make -C build/spi all` passed with
  no warning delta, but ordered hardware failed early at ledger
  `2026-04-30T20:25:32 spi 1`: block 1 passed, block 2 `Check 1lane
  bit-bang read returns incrementing pattern` failed with `sentinel not
  JSON: Expecting value: line 1 column 1 (char 0)`. Blocks 7 `p63` and 8
  `p15` were not reached. This pad-launch experiment does not preserve
  the slow bit-bang preflight and should not be committed unless a later
  Manager explicitly retains it for diagnostic value.
- Latest Worker cleanup after the failed registered-pad experiment
  succeeded. The SPI worktree is back to the last valid shared fabric
  presenter baseline: `dout_one` launches on
  `always @(posedge cs_n or negedge sclk)`, the 1-lane `SB_IO` pads are
  unregistered output-enable pads with `PIN_TYPE=6'b101001`, and 4-lane
  remains registered falling-edge. The Worker regenerated
  `verilog/spi.v`, `verilog/SB_IO.v`, and `tb/tb_spi_1lane.sv`; final
  `make -C build/spi sim`, `make -C build/spi bitstream`, and
  `make -C build/spi all` passed with no warnings in the final runs.
- Current valid ordered-path hardware baseline after registered-pad
  cleanup is ledger `2026-04-30T20:34:28 spi 7`: block 2 passed again
  with `00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f`, block 7
  `p63` passed with CRC `04d0e435` and `firsterr=-1`, and block 8 `p15`
  remains the active blocker. Block 8 failed with
  `presc=15 sshift=0 dlyb=0 unit=0`, `firsterr=2`, CRC `d1bcc1e2`, and
  first bytes `00 01 04 0c 20 41 83 88 14 41 46 0c 38 79 02 4a`.
  Disproven approaches so far: STM32 sample shift `p 15 1`, IO0-only LUT
  launch delay, symmetric posedge earlier launch, and true falling-edge
  registered `SB_IO` pad launch.
- Latest Worker evidence-only firmware/peripheral static inspection made
  no edits, build, or hardware run. It mapped generated block 7
  `p 63` plus `b 1048576 0 1` and block 8 `p 15` plus the same bench
  command through the CLI and QSPI source. Conclusion: block 7 versus
  block 8 differ only by QUADSPI prescaler. Both use `sshift=0`;
  DLYB is disabled (`dlyb=0 unit=0`); FIFO threshold is FTHRES=15;
  there is no DMA/MDMA in this raw bench path, only CPU 32-bit reads of
  `QUADSPI->DR`; the opcode `0x0b` is ignored on the wire because the
  raw data-only path sets IMODE=0 and ADMODE=0; DMODE=1 for 1-lane data;
  there is no address and dummy cycles are 0. Optional DLYB is the only
  exposed firmware-side knob not already identical in the generated pair.
- Latest Worker evidence-only DLYB hardware experiment made no source
  edits. The Worker temporarily changed only generated
  `fpga/build/spi/TEST.md` block 8 from `p 15` to exactly
  `p 15 0 1 127`, ran one ordered `run_md.py` invocation, then restored
  `TEST.md`. New ledger `2026-04-30T20:44:46 spi 7`: block 7 `p63`
  control passed with `presc=63 sshift=0 dlyb=0 unit=0`,
  `firsterr=-1`, CRC `04d0e435`. Modified block 8 hash
  `1b828924949f6bc2` confirmed `presc=15 sshift=0 dlyb=1 unit=127`;
  it reached `BENCHDBG poll_enter` but did not reach `poll_done`,
  `cmd_post`, CRC, `firsterr`, or bytes before the 8000 ms sentinel
  timeout. The DLYB setting changed the known completed bad-transfer
  signature (`firsterr=2`, CRC `d1bcc1e2`, known byte prefix) into a
  no-completed-result stall. `TEST.md` was restored. Current unmodified
  baseline remains the shared fabric `dout_one` presenter with block 2
  pass, block 7 `p63` pass, and block 8 `p15` fail with the known byte-2
  signature.
- Latest Worker evidence-only static DLYB semantics inspection made no
  edits, build, or hardware run. It found that
  `p <presc> <sshift> <dlyb> <unit>` is parsed in `cmd_prescaler`;
  prescaler is capped at `<=255`, `sshift` is forced to `0/1`,
  `dlyb_sel` defaults to `0`, and if `dlyb_sel != 0` then omitted
  `unit` defaults to `0x7f`. `qspi_set_dlyb(sel, unit)` rejects
  `sel > 15` or `unit > 127`, so `unit=127` is legal. Local STM32 CMSIS
  definitions show DLYB UNIT as 7-bit `[14:8]` with range `0..127`, and
  local LL delay-block code scans `i < 0x80`. `sel=1` is not suspicious.
  Active firmware DLYB setup writes `CR=0`; if enabled, writes
  `CR=DEN|SEN`, writes CFGR sel/unit, then writes `CR=DEN`. It does not
  wait for `LNGF`, run delay-line calibration, or handle lock status.
  Conclusion: `unit=127` is a legal maximum delay, suspicious only as an
  extreme uncalibrated maximum. The next smallest DLYB unit worth testing
  is `p 15 0 1 1`.
- Latest Worker evidence-only DLYB hardware probe made no source edits.
  The Worker temporarily changed only generated `fpga/build/spi/TEST.md`
  block 8 from `p 15` to exactly `p 15 0 1 1`, ran one ordered SPI
  `run_md.py`, then restored `TEST.md`. New ledger
  `2026-04-30T20:54:58 spi 7`: block 7 unmodified `p63` passed with CRC
  `04d0e435` and `firsterr=-1`. Modified block 8 hash
  `6b37fd3b09b285f4` confirmed `presc=15 sshift=0 dlyb=1 unit=1`; it
  reached `BENCHDBG poll_enter` but did not reach `poll_done`,
  `cmd_post`, CRC, `firsterr`, or byte dump before the 8000 ms timeout.
  This changed the known unmodified `p15` completed bad-transfer
  signature (`firsterr=2`, CRC `d1bcc1e2`, known byte prefix) to the same
  broad no-completed-result stall class as prior DLYB `unit=127`.
  `TEST.md` was restored and the diff was empty. Current unmodified
  baseline remains shared fabric `dout_one`: block 2 passes, block 7
  `p63` passes, and block 8 `p15` fails with the known byte-2 signature.
- User correction supersedes the prior DLYB-priority handoff. The
  `b LEN 0 1` / `cmd_bench` / `qspi_bench_read` path is CPU-polled
  correctness diagnostics and cannot sustain the >=100 Mbps mission
  wall-rate. The current block 8 `b 1048576 0 1` at `p 15` failure is a
  real data-integrity diagnostic and should remain recorded, but it is
  not the single-lane throughput gate. The single-lane throughput gate is
  the auto-consume stream path: `a 1`, `p 5 1`, and
  `A 33554432 0 1`. Verified external numbers for that path are 32 MiB
  at `presc=5 sshift=1` in 2.501 s for 107.331 Mbps, and 16 MiB for
  103.807 Mbps.
- Static inspection confirms current `fpga/src/spi.nw` and generated
  `fpga/build/spi/TEST.md` already contain the required auto-stream
  block: `p 5 1`, `a 1`, `A 33554432 0 1`,
  `stream_xfer 33554432 B`, and `, firsterr=-1`. The verifier already
  has `STREAM_RE`, `_stream_pick`, `check_stream_pattern`, and
  `check_stream_wall_rate_at_least("1lane", 5, 100.0, 33554432, ...)`
  support. The problem is ordered-suite reachability: CPU-polled
  diagnostic block 8 currently runs before the auto-stream wall-rate
  proof and aborts the normal ordered run.
- The user specifically asked whether block 8 should switch to the fast
  path. Manager determination: current block 8 is not intended as the
  throughput gate; it is a CPU-polled correctness diagnostic for the raw
  `b` path at `p15`. Do not replace it with `A` as though it were the
  mission wall-rate proof. Preserve the diagnostic, but move/defer it as
  needed so it does not block the existing `A 33554432 0 1` single-lane
  throughput proof unless the ordered suite is intentionally testing that
  diagnostic after the mission proof.
- Latest Worker reordered the 1-lane CPU-polled `b 1048576 0 1`
  diagnostics in `fpga/src/spi.nw` so the generated ordered suite now
  runs the single-lane auto-consume stream blocks first and preserves the
  `b` diagnostics after `A 33554432 0 1`. Generated
  `fpga/build/spi/TEST.md` confirms `A 33554432 0 1` at lines 219-240,
  followed by the preserved CPU-polled diagnostics at presc 203, 63, 15,
  and 5. Local `make -C build/spi sim`, `make -C build/spi bitstream`,
  and `make -C build/spi all` passed with no warning delta. The required
  ordered hardware run stopped at the first earlier auto-stream failure,
  before the 32 MiB wall-rate proof: ledger `2026-04-30T21:11:27 spi 8`
  passed blocks 1-8, including stream blocks at presc 203, 255, and 63,
  then failed block 9 `Check 1lane stream @ presc=15 pattern correct`.
  The failing UART summary was `stream_xfer 1500000 B 1lane in 292 ms,
  41.0 Mbps` followed by `stream 1500000 B 1lane in 297 ms, 41.0 Mbps,
  crc32=c854ab1a, expect=8ec8f9f3, firsterr=-2, chunk=16777216,
  chunks=2, buf=crc, auto=on, presc=15, qspi_hz=656000000`; the sentinel
  then timed out waiting for `, firsterr=-1`. The 32 MiB `p 5 1` wall-rate
  proof was not reached because the stop condition required stopping at
  this earlier auto-stream failure.
- Manager determination after inspecting generated `fpga/build/spi/TEST.md`:
  block 9 `Check 1lane stream @ presc=15 pattern correct` is also a
  diagnostic, not a setup prerequisite for the `p5` mission proof. It
  uses its own reset/DFU/UART sequence and does not carry state into the
  later `p 5 1`, `a 1`, `A 33554432 0 1` block. The `p15` auto-stream
  failure is real and must remain recorded and preserved later in the
  suite, but it should not block the mission single-lane wall-rate proof.
- Latest Worker moved the preserved `p15` auto-stream diagnostic after
  the `p 5 1`, `a 1`, `A 33554432 0 1` wall-rate block and left the
  CPU-polled diagnostics after the mission proof. Generated
  `fpga/build/spi/TEST.md` now has the 16 MiB `p5` stream block at lines
  173-194, the 32 MiB `p5` wall-rate block at lines 196-217, the
  preserved `p15` auto-stream diagnostic at lines 219-240, and
  CPU-polled diagnostics starting at line 242. `make -C build/spi sim`,
  `make -C build/spi bitstream`, and `make -C build/spi all` passed with
  no warning delta. The single ordered hardware run stopped at the first
  earlier failure before the 32 MiB wall-rate proof: ledger
  `2026-04-30T21:18:54 spi 8` passed blocks 1-8, including auto-stream
  controls at presc 203, 255, and 63, then failed block 9
  `Check 1lane stream @ presc=5 pattern correct`, waiting for
  `, firsterr=-1` within 15000 ms. The 32 MiB wall-rate block was not
  reached.
- Manager inspection of `fpga/build/spi/TEST.md` and `verify.py`
  confirms block 9 is a separate 16 MiB `p5` auto-stream pattern
  diagnostic (`A 16842752 0 1`, expected chunk `16777216`, `min_chunks=2`)
  immediately before the mission block. It uses its own
  reset/DFU/UART/auto-enable sequence and is not a setup prerequisite for
  the required `a 1`, `p 5 1`, `A 33554432 0 1` wall-rate proof. The
  failing ordered run proved the preceding auto-stream controls:
  presc=203 `firsterr=-1` at 3.200 Mbps, presc=255 `firsterr=-1` at
  2.539 Mbps, and presc=63 `firsterr=-1` at 9.823 Mbps, all with
  `auto=on` and `qspi_hz=656000000`.
- Current blocker: the 16 MiB `p5` diagnostic timed out waiting for
  `, firsterr=-1` after the `stream_xfer 16842752 B` sentinel path; the
  shared log records only the sentinel timeout and no verifier stream
  summary for block 9. This is not enough evidence to justify weakening
  the timeout, and it should not hide the mission proof. Preserve the
  diagnostic later in the ordered suite and let the 32 MiB wall-rate
  block run first.
- Latest Worker moved the existing 32 MiB `p5` auto-stream wall-rate
  proof before the current 16 MiB `p5` auto-stream diagnostic while
  preserving the 16 MiB diagnostic immediately afterward, then preserving
  the `p15` auto-stream diagnostic and CPU-polled `b` diagnostics later.
  Generated `fpga/build/spi/TEST.md` now has the 32 MiB wall-rate block
  at lines 173-194, the 16 MiB `p5` diagnostic at lines 196-217, the
  `p15` auto-stream diagnostic at lines 219-240, and CPU-polled
  diagnostics starting at line 242. Local `make -C build/spi sim`,
  `make -C build/spi bitstream`, and `make -C build/spi all` passed with
  no warning delta. Ordered hardware ledger `2026-04-30T21:26:48 spi 10`
  proved the mission block at `[9/31 PASS] Check 1lane stream @ presc=5
  wall rate >= 100 Mbps`: `bytes=33554432`, `bench=2460ms`,
  `crc32=310d8327`, `expect=310d8327`, `chunk=16777216`, `chunks=2`,
  `buf=crc`, `auto=on`, `qspi_hz=656000000`, `wall=2506ms`, and
  `wall_rate=107.117Mbps`. The run could not be interrupted through the
  closed tool stdin after that proof and continued into preserved
  diagnostics: block 10 16 MiB `p5` diagnostic also passed at
  `wall_rate=103.568Mbps`, then block 11 preserved `p15` auto-stream
  diagnostic failed by timeout waiting for `, firsterr=-1` within
  12000 ms. This confirms the single-lane 32 MiB wall-rate proof is no
  longer hidden behind the 16 MiB `p5` diagnostic.
- Review Manager accepted the latest Verifier's limited PASS for the
  single-lane mission proof only. Ledger `2026-04-30T21:26:48 spi 10`
  block 9 passed `Check 1lane stream @ presc=5 wall rate >= 100 Mbps`
  with `bytes=33554432`, `crc32=310d8327`, `expect=310d8327`,
  `chunk=16777216`, `chunks=2`, `buf=crc`, `auto=on`,
  `qspi_hz=656000000`, `wall=2506ms`, `wall_rate=107.117Mbps`,
  `wall_rate_floor=100.000Mbps`, and `firsterr=-1`. Block 10 also
  passed the 16 MiB `p5` diagnostic at `wall_rate=103.568Mbps`. This is
  not a full SPI-suite green result: the same ordered run failed at block
  11, the preserved `p15` auto-stream diagnostic, and only 10 of 31
  blocks were attempted. The full mission remains incomplete until a
  quad-lane path is demonstrated at >=200 Mbps with no data errors.
- Latest Worker evidence-only quad inspection made no source, generated,
  build, or hardware changes. It found firmware and verifier support are
  already present for quad auto-consume streaming: `a 1` enables
  auto-consume; `A <bytes> [q] [raw]` accepts q/raw arguments; the
  required quad raw stream command is `A 33554432 1 1`; `q=1` selects
  `QSPI_LINES_4` with opcode `0x6b`; `raw=1` disables IMODE/ADMODE and
  uses dummy 0. The generated/source verifier already accepts
  `1lane|quad` in `STREAM_RE`, `_stream_pick(mode, byte_count, presc)`
  works with `quad`, `_physical_max_mbps` uses four lanes, and
  `check_stream_wall_rate_at_least("quad", 11, 200.0, 33554432,
  expected_chunk=16777216, min_chunks=2)` is the intended validation.
  At `p 11`, the physical max is 218.667 Mbps; the 90% physical floor is
  196.8 Mbps, so the explicit wall-rate floor remains 200 Mbps. The
  missing source work is only to add the quad TEST block after the
  verified single-lane proof and before preserved diagnostics, plus add
  the matching verifier dispatch key.
- Latest Worker added the quad wall-rate proof block and matching
  verifier dispatch key in `fpga/src/spi.nw`; regenerated
  `fpga/build/spi/TEST.md` and `fpga/build/spi/verify.py`; and reported
  `make -C build/spi sim`, `make -C build/spi bitstream`, and
  `make -C build/spi all` all passed without warnings. Ordered hardware
  ledger `2026-04-30T21:41:57 spi 5` passed blocks 1-5, then failed
  block 6 `Check 1lane stream @ presc=203 pattern correct` by timeout
  waiting for `, firsterr=-1` within 40000 ms (`firsterr=-1` was not
  observed). The new quad wall-rate block was not attempted. This is
  analogous to prior diagnostic ordering blockers: before this source
  edit, ledger `2026-04-30T21:26:48 spi 10` reached and passed the
  single-lane 32 MiB `p5` mission proof and the 16 MiB `p5` diagnostic,
  then failed later at the preserved `p15` diagnostic. Current blocker is
  ordered-suite reachability, not evidence that the single-lane mission
  proof regressed or that quad failed.
- Manager determination: the early 1-lane low-speed auto-stream checks at
  presc 203, 255, and 63 are diagnostics, not setup prerequisites for
  the single-lane `p 5 1`/`A 33554432 0 1` mission proof or the new quad
  `p 11 1`/`A 33554432 1 1` mission proof. Each block has its own
  reset/DFU/UART/auto-enable sequence and should remain in the suite, but
  it should run after both mission proofs so a diagnostic timeout cannot
  hide the quad wall-rate result.
- Latest Worker reordered the low-speed diagnostics after both mission
  proofs and made no datapath or firmware changes. Local
  `make -C build/spi sim`, `make -C build/spi bitstream`, and
  `make -C build/spi all` passed. Ordered hardware ledger
  `2026-04-30T21:48:42 spi 6` passed block 6
  `Check 1lane stream @ presc=5 wall rate >= 100 Mbps` with
  `bytes=33554432`, matching CRC `310d8327`, `firsterr=-1`, `auto=on`,
  `qspi_hz=656000000`, `wall=2515ms`, and
  `wall_rate=106.734Mbps`.
- The same ordered run attempted the new quad mission proof at block 7
  `Check quad stream @ presc=11 wall rate >= 200 Mbps` and failed. The
  shared log only showed the harness timeout waiting for
  `, firsterr=-1` within 15000 ms, so the initial Worker report did not
  prove whether UART produced no stream summary, a bad CRC/firsterr, or
  some other output.
- Manager inspection of the latest block artifact found the missing quad
  transcript in
  `fpga/build/spi/test_out/c563dc02d32837c8/timeline.log` and
  `streams/mp135.uart.bin`. The firmware did complete the quad stream:
  `stream_xfer 33554432 B quad in 1583 ms, 169.5 Mbps`, followed by
  `stream 33554432 B quad in 2212 ms, 169.5 Mbps, crc32=9b9310a2,
  expect=310d8327, firsterr=5, chunk=16777216, chunks=2, buf=ddr,
  auto=on, presc=11, qspi_hz=656000000`. The active quad blocker is
  therefore a completed transfer with data corruption starting at byte 5
  and measured wall rate below 200 Mbps, not a no-output UART stall.
- Latest Worker evidence-only classification of quad block
  `c563dc02d32837c8` confirmed the same class from existing artifacts.
  The block command sequence was `p 11 1`, `a 1`,
  `A 33554432 1 1`; sentinels reached JEDEC, auto=on, and
  `stream_xfer 33554432 B`. Final raw UART was
  `stream_xfer 33554432 B quad in 1583 ms, 169.5 Mbps` followed by
  `stream 33554432 B quad in 2212 ms, 169.5 Mbps, crc32=9b9310a2,
  expect=310d8327, firsterr=5, chunk=16777216, chunks=2, buf=ddr,
  auto=on, presc=11, qspi_hz=656000000`. This proves a completed bad
  quad transfer followed by harness timeout waiting for the success
  sentinel. It is not a no-output stall and not a verifier parsing issue;
  `verify.py` would parse the stream summary and fail first on wall rate,
  then on data.
- Latest Worker evidence-only hardware probe temporarily changed only the
  generated quad block command to `A 1048576 1 1`, ran one ordered SPI
  run, and restored `fpga/build/spi/TEST.md`. New ledger
  `2026-04-30T21:58:20 spi 6`: blocks 1-6 passed, including the
  single-lane mission proof at block 6 with matching CRC `310d8327`,
  `firsterr=-1`, `auto=on`, `qspi_hz=656000000`, `wall=2507ms`, and
  `wall_rate=107.074Mbps`.
- The modified short quad block failed with a completed transfer, not a
  no-output stall:
  `stream_xfer 1048576 B quad in 38 ms, 218.6 Mbps`, followed by
  `stream 1048576 B quad in 81 ms, 218.6 Mbps, crc32=56d6d150,
  expect=04d0e435, firsterr=5, chunk=16777216, chunks=1, buf=ddr,
  auto=on, presc=11, qspi_hz=656000000`. This proves quad corruption is
  already present in a short 1 MiB raw auto-consume transfer and is not
  limited to the 32 MiB DDR length. It also shows the raw xfer path can
  reach the target physical rate class at `p11` (`218.6 Mbps`) before
  correctness fails. Because both 1 MiB and 32 MiB quad failures report
  `firsterr=5`, the next useful question is lane/nibble/bit-phase
  evidence, not transfer length.
- Latest Worker evidence-only static mapping inspection made no edits,
  build, or hardware run. It found no single fixed quad
  lane/nibble/bit-phase mapping model explains the repeated
  `firsterr=5` signature. FPGA source emits the high nibble then low
  nibble on `io[3:0]`; the STM32 raw quad auto-stream path checks DDR
  bytes against `i & 0xff`; and `firsterr=5` means bytes 0 through 4
  matched before byte 5 failed. Across all 24 lane permutations with
  nibble swap and one-nibble phase variants, the predicted first-error
  distribution did not include 5. Contrived one-time nibble
  drop/duplicate models can produce `firsterr=5`, but they are not unique
  and the CRCs did not match the observed failures. The smallest missing
  evidence is a quad raw/auto-path dump of the first 16 received bytes
  for failing `A 1048576 1 1`, or equivalent firmware-side `got16`
  reporting for the auto-stream DDR buffer.
- Latest Worker attempted that temporary firmware `got16`
  instrumentation path but did not obtain quad bytes. The Worker reported
  temporary MP135 QSPI firmware instrumentation was restored, the QSPI
  firmware was rebuilt back to the original hash
  `8435717a4558cac0f55b560f1890b8983e78c3ea208fefb30e40b5a6e989eb8d`,
  the temporary generated `fpga/build/spi/TEST.md` edit was restored, and
  `stm32mp135_test_board` is clean.
- The single ordered hardware run for that attempt did not reach the
  single-lane mission proof or the quad block. Latest ledger is
  `2026-04-30T22:09:35 spi 2`: blocks 1 and 2 passed, then block 3
  `Check 1lane peripheral raw read returns 1024-byte incrementing
  pattern` failed with `1lane raw mismatch at 1: got 00, expected 01`;
  the captured 1024-byte raw read was all zeroes. The block artifact is
  `fpga/build/spi/test_out/70c61f3362c613c0/`; block 2 immediately before
  it passed after programming `@spi_1lane.bin` and reading
  `00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f` via bit-bang.
- Manager inspection after that blocker found no clean-source basis for
  an FPGA datapath edit yet. `stm32mp135_test_board` is clean;
  `fpga/build/spi/main.stm32` is a symlink to the restored QSPI firmware
  and hashes to
  `8435717a4558cac0f55b560f1890b8983e78c3ea208fefb30e40b5a6e989eb8d`.
  The current SPI worktree remains intentionally dirty with tracked
  changes in `src/spi.nw`, `tb/tb_spi_1lane.sv`, `verilog/SB_IO.v`, and
  `verilog/spi.v`. Current artifact hashes observed by Manager:
  `fpga/build/spi/spi_1lane.bin`
  `702c4641f4e2d77d60ee2d502c2beea506c6506e55eaa39c06779bc4c30e7941`,
  `fpga/build/spi/TEST.md`
  `b1427528b5ef9c807229f2e1653016448c79dab8075c7554c2e74f4637f5e87d`,
  and `fpga/verilog/spi.v`
  `3059574a7ae8a1e047aa63a82e6f4874b2f1eb22bc3ae5f339ca8fe500bb27a0`.
  The next step must treat the early all-zero block 3 result as an
  artifact/programming/device-state freshness blocker before any source
  changes.
- Latest Worker read-only artifact inspection found a supported
  artifact/device-state mismatch. Failed run `2026-04-30T22:09:35 spi 2`
  block 3 all-zero cannot be attributed to the current restored
  `main.stm32`, because the current target hash
  `8435717a4558cac0f55b560f1890b8983e78c3ea208fefb30e40b5a6e989eb8d`
  was written after the failed run. `fpga/build/spi/TEST.md` is also
  newer than the failed run. FPGA bitstream evidence still looks sane:
  block 2 programmed intended `spi_1lane.bin` and passed before block 3;
  `spi_1lane.bin` and `verilog/spi.v` predate the run and match expected
  hashes. `stm32mp135_test_board` is clean and the temporary firmware
  instrumentation is absent. The current question is no longer static
  artifact inspection; it is whether a fresh ordered run from the current
  restored artifacts still fails at block 3 with all-zero data.
- Latest Worker evidence-only ordered hardware run from the current
  restored artifacts cleared the block 3 freshness blocker. Pre-run
  hashes were recorded, and ledger `2026-04-30T22:20:07 spi 6` passed
  blocks 1-6. Block 3 passed with the expected 1024-byte incrementing
  1-lane peripheral raw read, so the prior all-zero block 3 failure did
  not reproduce. Block 6 passed the single-lane mission proof:
  `bytes=33554432`, matching CRC `310d8327`, `firsterr=-1`, `auto=on`,
  `presc=5`, `qspi_hz=656000000`, and `wall_rate=107.074Mbps`.
- The same fresh ordered run reached the quad mission proof at block 7
  and failed with a completed bad transfer. The UART transcript showed
  `stream_xfer 33554432 B quad in 1584 ms, 169.4 Mbps`, followed by
  `stream 33554432 B quad in 2212 ms, 169.4 Mbps, crc32=9b9310a2,
  expect=310d8327, firsterr=5, chunk=16777216, chunks=2, buf=ddr,
  auto=on, presc=11, qspi_hz=656000000`. The active blocker is again
  quad raw auto-stream corruption beginning at byte 5 plus wall rate
  below 200 Mbps. The smallest missing evidence remains the first 16
  received DDR bytes for failing short quad `A 1048576 1 1`.
- A second temporary firmware `got16` instrumentation attempt repeated
  the same infrastructure blocker class. The Worker temporarily edited
  MP135 QSPI firmware `cli.c` plus generated `fpga/build/spi/TEST.md`,
  rebuilt/reran/restored, and reported clean restoration:
  `stm32mp135_test_board` clean, `fpga/build/spi/main.stm32` restored to
  hash
  `8435717a4558cac0f55b560f1890b8983e78c3ea208fefb30e40b5a6e989eb8d`,
  generated `TEST.md` restored, and the `fpga` worktree dirty only in
  pre-existing tracked files. New ledger `2026-04-30T22:25:25 spi 2`
  passed blocks 1 and 2, then failed block 3
  `Check 1lane peripheral raw read returns 1024-byte incrementing
  pattern` with an all-zero raw read before reaching the single-lane
  mission proof or quad block. Because an uninstrumented fresh run between
  the two attempts reached quad and passed block 3, repeated temporary
  firmware instrumentation is now recorded as a blocker/perturbation and
  should not be assigned again as the next path to `got16`.
- Latest WORK(infrastructure) attempted the non-firmware SWD capture
  route by editing `/home/agent2/test_serv/plugins/mp135.py` to add
  `mp135:swd_read8`; `python3 -m py_compile` passed and the temporary
  generated `fpga/build/spi/TEST.md` proof edit was restored. Ordered SPI
  ledger `2026-04-30T22:36:33 spi 6` passed blocks 1-6, including the
  single-lane mission proof, then failed before SWD execution during
  server-side validation of the quad block: `validation: line 15: 'mp135'
  has no op 'swd_read8'`. No `mp135.swd_read8` stream was produced.
  `/home/agent2/test_serv` is intentionally dirty only in
  `plugins/mp135.py`. Manager inspection confirms the local
  `Mp135Plugin.ops` dictionary in that file contains `swd_read8`, so the
  active blocker is plugin registration/loaded-server inventory, not SPI
  hardware and not the CubeProgrammer SWD command.
- Latest Worker infrastructure inventory check completed. Local
  `/home/agent2/test_serv/plugins/mp135.py` compiles/imports, and
  `sorted(Mp135Plugin.ops)` includes `swd_read8` along with
  `uart_close`, `uart_expect`, `uart_open`, and `uart_write`. A
  no-hardware `inventory refresh=false` against the running test server
  still omitted `swd_read8` and advertised only the UART ops for
  `mp135`; the latest validation artifact remains
  `fpga/build/spi/test_out/357c5e255fa870d7/errors.log` with
  `validation: line 15: 'mp135' has no op 'swd_read8'`. This classifies
  the blocker as stale running poller/plugin inventory or a poller
  running a different loaded checkout, not a local
  `/home/agent2/test_serv/plugins/mp135.py` code miss. Manager inspection
  also found `/home/agent2/test_serv/README.md` says plugin additions
  require `kill -HUP $(pgrep -f poller.py)` or restart, and
  `/home/agent2/test_serv/poller.py` handles SIGHUP by reloading plugins,
  refreshing devices, and publishing status.
- Manager rig reset before this infrastructure handoff was green as
  required by `AGENTS.md`: from `/home/agent2/fast_data/fpga/build/uart`,
  `python3 -u $TEST_SERV/run_md.py --ledger
  /home/agent2/fast_data/agent2/ledger.txt --module uart --log
  /home/agent2/fast_data/agent2/log.txt` exited 0, attempted one block,
  passed all 3 checks with no `test_serv` errors, and recorded ledger
  `2026-04-30T22:43:10 uart 3`.
- Latest evidence supersedes the stale `NO_RUNNING_POLLER` / external
  blocker conclusion. The user proved the bench is live:
  `TEST_SERV=~agent2/test_serv make test` from
  `/home/agent2/fast_data/fpga/build/uart` passes, and Orchestrator ran
  `inventory refresh=true verify=false` against `http://localhost:8080`
  successfully. The refreshed bench devices include `fpga.0`, `mp135.0`,
  `msc.mp135`, and related bench entries, so the problem is not a missing
  bench poller or missing FPGA device.
- Corrected active infrastructure blocker: authoritative
  `bench.ops.json` still advertises only the MP135 UART ops and omits the
  locally added `/home/agent2/test_serv/plugins/mp135.py` op
  `swd_read8`. Local import of `/home/agent2/test_serv` shows
  `Mp135Plugin.ops` includes `swd_read8`, and
  `/home/agent2/test_serv/plugins/mp135.py` remains intentionally dirty
  with that op. The latest failed SPI proof edit still stopped at
  server-side validation:
  `validation: line 15: 'mp135' has no op 'swd_read8'`. The mismatch is
  between the running/authoritative bench inventory and the local dirty
  plugin code, not SPI hardware and not CubeProgrammer SWD syntax.
- The stale `fpga/build/uart/test_out` reset blocker was cleared by
  Orchestrator by moving the jk-owned tree aside. The required UART reset
  gate was made green afterward: ledger `2026-05-01T05:16:40 uart 3`.
- Latest Worker then ran exactly one no-hardware authoritative inventory
  refresh with `refresh=true verify=false`. It classified the SWD route
  as `ABSENT_IN_AUTHORITATIVE_INVENTORY`: local
  `/home/agent2/test_serv/plugins/mp135.py` compiles/imports and local
  `Mp135Plugin.ops` includes `swd_read8`, but authoritative
  `/home/agent2/fast_data/agent2/inventory_20260501T0522_mp135_refresh/streams/bench.ops.json.bin`
  lists MP135 ops only
  `['uart_close', 'uart_expect', 'uart_open', 'uart_write']`.
  The prior validation artifact remains
  `/home/agent2/fast_data/fpga/build/spi/test_out/357c5e255fa870d7/errors.log`:
  `validation: line 15: 'mp135' has no op 'swd_read8'`.
- Because the authoritative server inventory still omits
  `mp135:swd_read8`, do not assign another SWD proof edit until the
  loaded bench plugin inventory is fixed. For the immediate quad
  byte-evidence question, prefer the existing MP135 firmware fallback:
  `j <n> [q]` performs a raw data-only read and prints up to 1024 bytes
  via UART. `m <n> [q] [raw]` validates DDR and prints CRC/firsterr but
  not received bytes, and `b` prints `got16` but uses the polling path.
  Temporary firmware `got16` instrumentation perturbed block 3 twice and
  must not be retried unless a later Manager explicitly justifies it.
- Manager ran the required pre-WORK rig reset exactly once for this
  handoff from `/home/agent2/fast_data/fpga/build/uart` with
  `/home/agent2/test_serv/run_md.py`. It exited 0, attempted one block,
  passed all three UART checks with `n_errors=0`, and recorded ledger
  `2026-05-01T05:19:54 uart 3`.
- Latest WORK(evidence-only) captured the existing firmware `j` raw
  data-only UART dump for the quad peripheral path without source or
  firmware edits. The temporary generated TEST change used `p 11 1`,
  `a 1`, and `j 1024 1`; `fpga/build/spi/TEST.md` was restored to hash
  `b1427528b5ef9c807229f2e1653016448c79dab8075c7554c2e74f4637f5e87d`.
  Ledger `2026-05-01T05:22:37 spi 0` failed only because the final
  success sentinel was intentionally unchanged after the dump. The block
  artifact is `fpga/build/spi/test_out/03f4a7b74c9f83ee/`. The first
  16 received bytes were
  `00 01 02 03 04 01 02 03 04 01 02 03 04 01 02 03`; first mismatch
  was index 5, got `01`, expected `05`. This matches the prior quad
  auto-stream failures (`firsterr=5`) and proves the byte-5 corruption
  is independent of MDMA/auto-consume buffering. The repeating
  `01 02 03 04` pattern after the initial `00 01 02 03 04` points to a
  source-side quad byte counter, phase, or framing reset/wrap after byte
  4 rather than random lane mapping.
- Manager ran the required pre-WORK rig reset exactly once for this
  handoff from `/home/agent2/fast_data/fpga/build/uart` with
  `/home/agent2/test_serv/run_md.py`. It exited 0, attempted one block,
  passed all three UART checks with `n_errors=0`, and recorded ledger
  `2026-05-01T05:25:33 uart 3`.
- Latest Worker/source attempt implemented one localized quad experiment
  in `fpga/src/spi.nw`: quad switched from registered IOB pad outputs
  with a posedge presenter to a fabric negedge `dout_quad` presenter plus
  unregistered `PIN_TYPE=101001` pads; the netlist checker was updated
  to allow both registered and unregistered variants. Local
  `make -C build/spi sim`, `make -C build/spi bitstream`, and
  `make -C build/spi all` passed.
- Ordered hardware from `fpga/build/spi` with the shared ledger/log
  invalidated that quad experiment before it reached the quad block.
  Ledger `2026-05-01T05:29:50 spi 2` passed blocks 1 and 2, then failed
  block 3 `Check 1lane peripheral raw read returns 1024-byte incrementing
  pattern`: `1lane raw mismatch at 1: got 00, expected 01`. Artifact:
  `fpga/build/spi/test_out/70c61f3362c613c0/`. UART shows `p 203 0`,
  `j 1024 0`, then an all-zero raw dump. Block 2 immediately before
  passed the 1-lane bit-bang bytes `00 01 02 03 04 05 06 07 08 09 0a
  0b 0c 0d 0e 0f`. This resembles prior transient all-zero block 3
  failures, but because it occurred after the source/bitstream change,
  the patch is red and must not be considered valid.
- Manager ran the required pre-WORK rig reset exactly once for this
  handoff from `/home/agent2/fast_data/fpga/build/uart` with
  `/home/agent2/test_serv/run_md.py`. It exited 0, attempted one block,
  passed all three UART checks with `n_errors=0`, and recorded ledger
  `2026-05-01T05:31:03 uart 3`.
- Latest Worker cleanup reverted only the failed quad unregistered-pad /
  fabric-negedge diagnostic experiment back to the prior quad
  registered-pad shape while preserving the valid 1-lane fabric
  `dout_one` changes. Local `make -C build/spi sim`,
  `make -C build/spi bitstream`, and `make -C build/spi all` passed.
- Current valid ordered-path baseline after that cleanup is ledger
  `2026-05-01T05:34:42 spi 6`: blocks 1-6 passed. Block 3 1-lane raw
  is restored, and block 6 passed the single-lane mission proof with a
  matching CRC, `firsterr=-1`, `auto=on`, `presc=5`, and
  `wall_rate=107.117Mbps`.
- The same ordered run returned the first failure to block 7
  `Check quad stream @ presc=11 wall rate >= 200 Mbps`. Artifact:
  `fpga/build/spi/test_out/c563dc02d32837c8/`. UART summary:
  `stream_xfer 33554432 B quad in 1583 ms, 169.5 Mbps`, followed by
  `stream 33554432 B quad in 2212 ms, 169.5 Mbps, crc32=9b9310a2,
  expect=310d8327, firsterr=5, chunk=16777216, chunks=2, buf=ddr,
  auto=on, presc=11, qspi_hz=656000000`.
- Prior evidence-only raw dump at `j 1024 1` with `p 11` showed first
  16 bytes `00 01 02 03 04 01 02 03 04 01 02 03 04 01 02 03`; first
  mismatch index 5, got `01`, expected `05`. Because both auto-stream
  and existing raw data-only UART diagnostics fail at byte 5 with the
  same repeated `01 02 03 04` pattern, the next smallest question is
  whether the STM32 raw data-only transaction framing / chip-select
  behavior restarts the FPGA quad stream after five bytes, or whether the
  FPGA quad generator itself wraps/restarts after byte 4 independent of
  STM32 transaction boundaries. Do not inspect or modify a speculative
  5-byte preamble in source until this framing question is answered.
- Manager ran the required pre-WORK rig reset exactly once for this
  handoff from `/home/agent2/fast_data/fpga/build/uart` with
  `/home/agent2/test_serv/run_md.py`. It exited 0, attempted one block,
  passed all three UART checks with `n_errors=0`, and recorded ledger
  `2026-05-01T05:36:17 uart 3`.
- Latest Worker evidence-only framing inventory classifies the current
  state as `NO_EXISTING_OBSERVABILITY`. The raw dump artifact
  `fpga/build/spi/test_out/03f4a7b74c9f83ee/` was overwritten by later
  ordered runs and is no longer present under `build/spi/test_out`; the
  byte prefix is preserved in this TODO and agent output. The current
  quad mission artifact `fpga/build/spi/test_out/c563dc02d32837c8/`
  contains only MP135 UART/DFU streams, with no FPGA UART or scope trace.
  `/scope/signals` maps C1-C4 to DSP signals only, not QSPI
  `CS/SCLK/IOx`. Existing `spi_debug` observes only the 1-lane IO1 path,
  and the command-aware `jedec` UART diagnostics observe framed JEDEC
  commands rather than the raw `spi_quad.bin` data-only path used by
  `j 1024 1` and `A ... 1 1`. Therefore existing artifacts and
  diagnostics cannot prove whether the byte-5 repeat is a continuous
  quad data phase or a CS/transaction boundary. The smallest next useful
  diagnostic is a new, narrowly-scoped quad raw observer bitstream or
  supported scope wiring that records CS/SCLK edge counts and the first
  16 quad nibbles for one `j 1024 1` transaction, without touching MP135
  firmware or test expectations.
- Latest diagnostic bitstream `spi_quad_debug.bin`, built from
  `fpga/src/spi.nw` with temporary block `65b555ed8c4da745`, answered
  the raw-dump framing question. Ledger `2026-05-01T05:46:43 spi 0`
  intentionally failed only after collecting evidence. Artifact
  `fpga/build/spi/test_out/65b555ed8c4da745/` contains the MP135 raw
  `j 1024 1` dump
  `00 01 02 03 04 01 02 03 04...`, and FPGA UART repeatedly reports
  lines including
  `Q F=1d E=0008 N=00000000000000000000000004010203`.
  Manager interpretation: the selected observed frames are only 8 quad
  rising edges, i.e. 4 bytes, not one continuous 1024-byte data phase.
  This explains the repeated `01 02 03 04` raw-dump pattern as CS/SCLK
  framing reset behavior. The observer source edits are diagnostic only
  and are not a mission fix.
- Current mission state: single-lane auto-stream at `presc=5` is already
  proven above 100 Mbps by prior ordered hardware evidence. Quad
  auto-stream remains red at `presc=11`: latest valid mission evidence
  still shows a completed bad transfer with `firsterr=5` and about
  `169.5 Mbps`, below the required 200 Mbps. The new framing evidence
  was collected with `j 1024 1`, so the next question must not assume
  the same 4-byte framing applies to the quad auto-stream `A ... 1 1`
  path until checked directly.
- User suggestion noted: block/rate checks should use the fast
  auto-stream path where they are intended as throughput gates. This is
  already proven for the single-lane mission path and should guide quad
  routing, but the next step should answer one primary question only.
- Latest ordered mission evidence with explicit per-transfer FTHRES and
  idle-JEDEC gating is ledger `2026-05-01T06:40:06 spi 6`: blocks 1-6
  passed, including the single-lane mission proof at `wall_rate=107.032
  Mbps`, CRC match, `firsterr=-1`, `auto=on`, and `presc=5`. Quad block
  7 remains red with `p 11 1`, `N 0`, and `A 33554432 1 1`:
  `stream_xfer ... 169.4 Mbps`, `stream_got16 base=0 bytes=00 01 02 03
  04 05 06 60 77 08 09 0a 00 00 0f f1`, CRC `01620a7e` versus
  `310d8327`, `firsterr=7`, `chunk=16777216`, `chunks=2`, `buf=ddr`.
- Disproven/negative steps after that evidence: the unregistered
  CS-preload quad FPGA experiment passed local sim but worsened hardware
  to `firsterr=4`, so it was reverted to the registered carry-across
  quad path. `p 11 0` was worse (`firsterr=0`, first byte `80`).
  `p 11 1 1 127` hung before `stream_xfer`. Slowing to `p 15 1`
  was also worse (`firsterr=1`, prefix `00 12 03 04 05 06 07 70 ...`).
  Therefore the current blocker is not solved by idle-JEDEC gating,
  sample-shift off, max DLYB, or slower `p15` timing.
- Firmware changes currently kept because they preserve block 6 and add
  useful observability: `N 0|1` gates the background JEDEC loop, both
  MDMA start paths explicitly set FTHRES (`15` for 1-lane, `3` for
  quad), and stream CRC mismatches print `stream_got16`.
- The single-pad legality question after the failed bridge experiment is
  answered. A temporary quad "first sample" bridge using two `SB_IO`
  cells per `io[n]` passed local simulation but failed local bitstream:
  nextpnr reported `No wire found for port PACKAGE_PIN on destination
  cell g_quad_io.g_io[3].iob_first`. The bridge was removed, the netlist
  checker was restored to expect exactly four physical pads, and local
  `make -C build/spi sim` plus `make -C build/spi bitstream` passed
  again. Therefore future quad timing experiments must use one physical
  `SB_IO` per pad or move the question into firmware/peripheral framing.
- The quad FIFO-threshold framing experiment is also red. After the
  required UART reset (`2026-05-01T08:20:18 uart 3`), firmware hash
  `892bbc118b6c2e20e885a7c0f8fb81cc432770ff29fe59374d11eccd89577035`
  changed both MDMA start paths to `FTHRES=15` for quad. Ordered
  hardware ledger `2026-05-01T08:22:21 spi 6` kept block 6 green at
  `wall_rate=107.032Mbps`, but block 7 still failed with the same quad
  prefix: `stream_got16 ... 00 01 02 03 04 05 06 60 77 08 09 0a 00 00
  0f f1`, `firsterr=7`, and `stream_xfer ... 169.5 Mbps`. The failed
  threshold diagnostic was reverted to the prior `3` for quad and `15`
  for 1-lane selector.
- The single-pad unregistered quad/CS-preload experiment is red. After
  UART reset `2026-05-01T08:23:42 uart 3`, local `make -C build/spi
  sim`, `bitstream`, and `all` passed with one `PIN_TYPE=101001`
  `SB_IO` per quad pad. Ordered hardware ledger
  `2026-05-01T08:28:40 spi 6` kept block 6 green at
  `wall_rate=107.117Mbps`, but block 7 failed earlier with
  `stream_got16 base=0 bytes=00 01 02 03 40 f0 f0 f0 f0 f0 f0 f0 f0
  f0 f0 f0`, `firsterr=4`, CRC `09d65370`, and `stream_xfer ... 169.4
  Mbps`. This proves the unregistered quad output/preload shape changes
  the failure mode but does not fix the fast path; revert it before the
  next experiment.
- The low-tap DLYB evidence-only sweep answered the sampling-window
  question. After UART reset `2026-05-01T08:31:03 uart 3`, temporary
  generated block artifact `fpga/build/spi/test_out/2e29c63b06b16366/`
  ran the normal registered quad bitstream. Tap 0 reproduced the
  baseline: `stream_got16 ... 00 01 02 03 04 05 06 60 77 08 09 0a 00
  00 0f f1`, `firsterr=7`, and `169.4 Mbps`. Tap 4 accepted
  `presc=11 sshift=1 dlyb=1 unit=4`, then `A 33554432 1 1` produced no
  new `stream_xfer`; later `p` commands timed out because the firmware
  command loop was still stuck in that transfer. This hits the stop
  condition for a low-tap hang and argues against chasing a DLYB window.
  The generated `TEST.md` was restored from `src/spi.nw` afterward.
- The existing framed quad bitstream plus non-raw transfer is not a fix.
  After UART reset `2026-05-01T08:34:12 uart 3`, diagnostic artifact
  `fpga/build/spi/test_out/054f1b993652781a/` programmed
  `spi_quad_framed.bin` and ran `A 33554432 1 0`. It reached
  `stream_xfer 33554432 B quad in 1584 ms, 169.4 Mbps`, but failed with
  `stream_got16 base=0 bytes=00 01 02 03 04 44 44 44 44 44 44 44 46 66
  66 66`, CRC `a4097976` versus `310d8327`, and `firsterr=5`. The
  generated `TEST.md` was restored from `src/spi.nw` afterward.
- The fast `A` frame observer answered the missing framing question.
  After UART reset `2026-05-01T08:36:42 uart 3`, diagnostic artifact
  `fpga/build/spi/test_out/0fad7353bb40972e/` programmed
  `spi_quad_debug.bin` and ran `A 1048576 1 1`. MP135 reported
  `stream_xfer ... 215.0 Mbps`, but CRC failed with
  `stream_got16 base=0 bytes=00 01 02 03 04 05 06 07 89 0a 0b cc 0d
  d0 ee 0f` and `firsterr=8`. FPGA UART captured selected frame lengths
  including `E=0003`, `E=0004`, `E=000b`, `E=000d`, and `E=0015`.
  Therefore the fast `A` path has variable, sometimes odd-length
  selected frames; quad state must carry phase across CS and must present
  the current nibble immediately on CS-low, not only after a falling
  edge.
- The pure combinational quad carry-across implementation is red. After
  local sim/bitstream/all passed and UART reset `2026-05-01T08:40:00
  uart 3`, the first ordered run failed block 6 once with a direct-CRC
  mismatch, but repeat reset `2026-05-01T08:43:06 uart 3` restored block
  6 green at `wall_rate=107.117Mbps`. The repeat reached block 7 and
  failed worse than baseline: artifact `97cf3ab620cd5124`, ledger
  `2026-05-01T08:44:52 spi 6`, `stream_got16 base=0 bytes=00 10 20 00
  41 54 77 80 91 08 b8 40 d8 f0 70 11`, CRC `b752f8e3`, `firsterr=1`,
  `stream_xfer ... 169.4 Mbps`. This proves direct combinational quad
  output violates the STM32 sample edge; revert it before the next
  experiment.
- The pure combinational quad carry-across edit has now been reverted
  locally. Current local build evidence from the user is green:
  `make -B verilog/spi.v verilog/SB_IO.v tb/tb_spi_quad.sv
  build/spi/check_spi_netlist.py && make -C build/spi sim &&
  make -C build/spi bitstream && make -C build/spi all` passes. Manager
  verified firmware hashes are restored to
  `932a68703dd0d8cb4c5ac9be2a5ff31c97aad49cd476898d7c44c35fb77eb659`
  for both `stm32mp135_test_board/baremetal/qspi/build/main.stm32` and
  `fpga/build/spi/main.stm32`. The proven 1-lane path must remain
  untouched.
- Manager ran the required pre-WORK rig reset exactly once for this
  handoff from `/home/agent2/fast_data/fpga/build/uart` with
  `/home/agent2/test_serv/run_md.py`. It exited 0, attempted one block,
  passed all three UART checks with `n_errors=0`, and recorded ledger
  `2026-05-01T08:50:08 uart 3`.
- Latest ordered restored-baseline evidence is ledger
  `2026-05-01T08:53:05 spi 6`: blocks 1-6 passed, including the
  single-lane mission proof at `wall_rate=106.989Mbps`, matching CRC
  `310d8327`, `firsterr=-1`, `auto=on`, and `presc=5`. Block 7
  `Check quad stream @ presc=11 wall rate >= 200 Mbps` failed with a
  completed transfer:
  `stream_xfer 33554432 B quad in 1584 ms, 169.4 Mbps`,
  `stream_got16 base=0 bytes=00 01 02 03 04 05 06 60 77 08 09 0a 00 00
  0f f1`, CRC `f31215b5` versus `310d8327`, `firsterr=7`, `auto=on`,
  and `presc=11`.
- Manager determination: the smallest next source question is the
  inconsistency between proven fast-`A` framing and current quad state.
  Prior observer evidence showed variable, sometimes odd-length selected
  frames on the fast `A` path, so quad nibble phase must carry across
  CS-high gaps. The current source prose says phase carries, but the
  actual quad lane code still executes `phase <= 1'b0` when `cs_n`
  rises. That reset is now the narrowest falsifiable candidate before
  any broader timing or firmware experiment.
- Manager ran the required pre-WORK rig reset for the next handoff from
  `/home/agent2/fast_data/fpga/build/uart`. The first invocation hit the
  documented `$TEST_SERV` unset path, then the allowed fallback
  `/home/agent2/test_serv` retry exited 0, attempted one UART block,
  passed all three checks with `n_errors=0`, and recorded ledger
  `2026-05-01T08:54:35 uart 3`.
- Latest Worker source edit changed only the quad phase path so it no
  longer resets on `cs_n`, while keeping the registered quad pads. Local
  build evidence from the user is green:
  `make -B verilog/spi.v verilog/SB_IO.v tb/tb_spi_quad.sv
  build/spi/check_spi_netlist.py && make -C build/spi sim &&
  make -C build/spi bitstream && make -C build/spi all` passed.
- Ordered hardware ledger `2026-05-01T08:59:22 spi 5` is red before the
  quad block. Blocks 1-5 passed, then block 6
  `Check 1lane stream @ presc=5 wall rate >= 100 Mbps` completed the
  transfer but failed CRC/sentinel:
  `stream_xfer 33554432 B 1lane in 2455 ms, 109.3 Mbps`, final
  `stream 33554432 B 1lane in 2460 ms, 109.3 Mbps, crc32=59450445,
  expect=310d8327, firsterr=-2, chunk=16777216, chunks=2, buf=crc,
  auto=on, presc=5, qspi_hz=656000000`, followed by repeated idle JEDEC
  banners. The quad block was not reached.
- Manager determination: current source is red until proven otherwise,
  even though the quad-only edit should synthesize away for `LANES=1`.
  This exact direct-CRC mismatch class occurred once during the pure
  combinational quad experiment and cleared on an immediate ordered
  repeat. The smallest next falsifiable question is therefore one
  evidence-only ordered repeat with no source edits, to decide whether
  the current quad phase edit truly regresses the proven 1-lane mission
  block or whether the repeat reaches the quad block for valid evidence.
- Manager ran the required pre-WORK rig reset for this handoff from
  `/home/agent2/fast_data/fpga/build/uart`. The first shell invocation
  expanded an unset `$TEST_SERV` to `/run_md.py` before `run_md.py`
  started; the allowed default retry with `/home/agent2/test_serv`
  exited 0, attempted one UART block, passed all three checks with
  `n_errors=0`, and recorded ledger `2026-05-01T09:01:15 uart 3`.
- The ordered repeat answered that question. User-provided current-source
  evidence says local `sim`, `bitstream`, and `all` passed, then ordered
  hardware ledger `2026-05-01T09:06:15 spi 6` passed blocks 1-6,
  including the single-lane mission proof: `wall_rate=107.117Mbps`, CRC
  matched `310d8327`, `firsterr=-1`, `auto=on`, and `presc=5`. Block 7
  still failed the quad mission gate with `stream_xfer 33554432 B quad in
  1585 ms, 169.3 Mbps`, `stream_got16 base=0 bytes=00 01 02 03 04 50 66
  07 09 0a 00 00 0f 11 12 13`, CRC `713b9359` versus `310d8327`,
  `firsterr=5`, `auto=on`, and `presc=11`.
- Manager determination: the quad phase-carry edit is red versus mission.
  It changes the failure signature from the restored registered-baseline
  `firsterr=7` prefix `00 01 02 03 04 05 06 60 77 ...` to `firsterr=5`
  prefix `00 01 02 03 04 50 66 ...`, but it still corrupts data and
  remains below the 200 Mbps floor. The smallest next step is cleanup:
  revert only that failed quad phase/no-`cs_n`-reset diagnostic while
  preserving the proven 1-lane path and the useful firmware observability
  changes.
- Manager ran the required pre-WORK rig reset exactly once for the next
  handoff from `/home/agent2/fast_data/fpga/build/uart` with
  `/home/agent2/test_serv/run_md.py`. It exited 0, attempted one UART
  block, passed all three UART checks with `n_errors=0`, and recorded
  ledger `2026-05-01T09:07:46 uart 3`.
- Latest cleanup Worker removed only the failed quad phase
  no-`cs_n`-reset diagnostic and restored the registered quad baseline
  shape: `always @(posedge cs_n or posedge sclk)` with `phase <= 1'b0`
  on `cs_n`. The intended last-valid quad behavior is again represented
  by ordered ledger `2026-05-01T08:53:05 spi 6`: blocks 1-6 passed,
  including the single-lane mission proof, then quad block 7 failed with
  `firsterr=7` and prefix
  `00 01 02 03 04 05 06 60 77 08 09 0a 00 00 0f f1`. The failed
  no-reset edit remains recorded as ledger `2026-05-01T09:06:15 spi 6`:
  blocks 1-6 passed, but quad block 7 still failed and changed the
  signature to `firsterr=5` with prefix
  `00 01 02 03 04 50 66 07 09 0a 00 00 0f 11 12 13`.
- Cleanup local evidence from the user is green:
  `make -B verilog/spi.v verilog/SB_IO.v tb/tb_spi_quad.sv
  build/spi/check_spi_netlist.py && make -C build/spi sim &&
  make -C build/spi bitstream && make -C build/spi all` passed. No
  hardware run was done for cleanup, so the current hardware baseline
  remains the restored registered quad ledger `2026-05-01T08:53:05
  spi 6`.
- Manager ran the required pre-WORK rig reset exactly once for this
  handoff from `/home/agent2/fast_data/fpga/build/uart` with
  `/home/agent2/test_serv/run_md.py`. It exited 0, attempted one UART
  block, passed all three UART checks with `n_errors=0`, and recorded
  ledger `2026-05-01T09:10:25 uart 3`.
- Latest Worker evidence-only firmware/peripheral inspection made no
  edits, build, or hardware run. It inspected
  `stm32mp135_test_board/baremetal/qspi/src/qspi.c`,
  `stm32mp135_test_board/baremetal/qspi/src/qspi.h`,
  `stm32mp135_test_board/baremetal/qspi/src/cli.c`, and the local Linux
  STM32 QSPI driver. Conclusion: one plausible untested local lever
  exists before another FPGA datapath edit. In `qspi_mdma_start` and
  `qspi_mdma_crc_start`, quad MDMA uses QSPI FIFO threshold `FTHRES=3`
  (4 bytes) but MDMA `tlen=64`, so each QSPI FIFO-threshold request can
  launch a 64-byte MDMA buffer transfer. Prior fast-path observer
  evidence showed variable and sometimes odd selected frames, and quad
  correctness fails with prefixes consistent with framing/drain
  irregularity. The smallest next experiment is quad-only MDMA request
  granularity: set the quad MDMA TLEN/request granularity to 4 bytes,
  keep 1-lane and direct-CRC behavior untouched, rebuild local firmware,
  and run one normal ordered SPI hardware run. TCEN was considered and
  rejected as less defensible; the local ST/Linux driver defines
  `CR_TCEN` as timeout-counter enable and does not use it for normal
  indirect reads.
- Manager ran the required pre-WORK rig reset exactly once for this
  handoff from `/home/agent2/fast_data/fpga/build/uart` with
  `/home/agent2/test_serv/run_md.py`. It exited 0, attempted one UART
  block, passed all three UART checks with `n_errors=0`, and recorded
  ledger `2026-05-01T09:14:10 uart 3`.
- The quad MDMA TLEN/request-granularity firmware experiment is red and
  has been reverted. Worker changed only `qspi.c` quad MDMA TLEN from
  `64U` to `4U`, rebuilt firmware to temporary hash `df75a20d...`, and
  ran one ordered SPI hardware invocation. Ledger `2026-05-01T09:17:45
  spi 6` passed blocks 1-6, including the single-lane mission proof at
  `wall_rate=107.074Mbps`, CRC match, `firsterr=-1`, `auto=on`, and
  `presc=5`. Block 7 still failed the quad mission gate with the same
  restored-baseline first error and prefix but worse throughput:
  `stream_xfer 33554432 B quad in 1734 ms, 154.8 Mbps`,
  `stream_got16 base=0 bytes=00 01 02 03 04 05 06 60 77 08 09 0a 00 00
  0f f1`, CRC `55e2cf3b` versus `310d8327`, `firsterr=7`, `auto=on`,
  and `presc=11`. Therefore TLEN granularity is not the active fix.
- Worker reverted the failed TLEN edit back to `64U`. Manager verified
  both firmware images are restored to
  `932a68703dd0d8cb4c5ac9be2a5ff31c97aad49cd476898d7c44c35fb77eb659`:
  `stm32mp135_test_board/baremetal/qspi/build/main.stm32` and
  `fpga/build/spi/main.stm32`. Current `qspi.c` again contains
  `const uint32_t tlen = 64U` in both MDMA start paths. The remaining
  local firmware diffs are the earlier accepted observability/FTHRES
  edits, not the failed TLEN diagnostic.
- Manager determination: after failed FTHRES=15, TLEN=4, DLYB/sample
  attempts, framed non-raw transfer, and several quad pad timing
  experiments, the smallest unresolved question is no longer another
  blind transfer-tuning knob. The latest discriminating evidence is still
  the fast-`A` observer: selected quad frames on the STM32 path can be
  variable and sometimes odd length. The registered baseline resets
  phase on CS-high and fails with `firsterr=7`; the no-CS-reset edit
  changed the signature to `firsterr=5` but still failed; the
  combinational immediate-output edit failed earlier. The next smallest
  source question is whether the quad presenter can preload the current
  nibble at the start of each selected frame while keeping the
  subsequently sampled data on the proven registered/posedge timing.
- Manager ran the required pre-WORK rig reset exactly once for this
  handoff from `/home/agent2/fast_data/fpga/build/uart` with
  `/home/agent2/test_serv/run_md.py`. It exited 0, attempted one UART
  block, passed all three UART checks with `n_errors=0`, and recorded
  ledger `2026-05-01T09:19:02 uart 3`.
- The minimal quad CS-start preload source experiment is local-red and
  has been reverted. Worker tried to set `phase <= 1'b0` and
  `dout_quad <= data_byte[7:4]` when `cs_n` was high while retaining the
  registered quad pads. Local simulation started, but Yosys failed while
  building `spi_quad.json` with `Warning: Async reset value \data_byte
  [7:4] is not constant!` followed by `ERROR: FF ... cannot be
  legalized: dffs with async set and reset are not supported`. This was
  a synthesis legality failure, not hardware evidence.
- Worker reverted that failed preload and restored the registered quad
  baseline shape. The user-provided cleanup build evidence is green:
  `make -B verilog/spi.v verilog/SB_IO.v tb/tb_spi_quad.sv
  build/spi/check_spi_netlist.py && make -C build/spi sim &&
  make -C build/spi bitstream && make -C build/spi all` passed again.
  No hardware run was done for this failed local experiment or its
  cleanup, so the current ordered hardware baseline remains the restored
  registered quad ledger `2026-05-01T08:53:05 spi 6`.
- Manager verified the firmware images remain restored to
  `932a68703dd0d8cb4c5ac9be2a5ff31c97aad49cd476898d7c44c35fb77eb659`
  for both `stm32mp135_test_board/baremetal/qspi/build/main.stm32` and
  `fpga/build/spi/main.stm32`.
- Manager determination: the failed preload answered only that
  data-derived assignment in the asynchronous `cs_n` branch is illegal
  for the current Yosys/iCE40 flow. Before assigning another source
  experiment, the smallest falsifiable question is whether a CS-high
  update of the fabric `D_OUT_0` source could affect the first selected
  STM32 sample at all when the quad pads are still falling-edge
  registered `SB_IO` cells. If the pad output flop only captures on the
  next SCLK falling edge, then the previous preload strategy cannot fix
  first-nibble selected-frame alignment even if expressed legally.
- Manager ran the required pre-WORK rig reset exactly once for this
  handoff from `/home/agent2/fast_data/fpga/build/uart` with
  `/home/agent2/test_serv/run_md.py`. It exited 0, attempted one UART
  block, passed all three UART checks with `n_errors=0`, and recorded
  ledger `2026-05-01T09:23:22 uart 3`.

### Next Handoff

- Status: ASSIGN WORK(evidence-only/quad-pad-preload-feasibility). The required Manager rig
  reset is already green for this handoff.
- Primary question: with `PIN_TYPE=6'b100101` and `NEG_TRIGGER=1'b1`,
  can changing the fabric `D_OUT_0` value while `cs_n` is high affect
  the first quad value seen by the STM32 on the next selected rising
  edge, or does the pad output necessarily remain the previously latched
  value until the next SCLK falling edge?
- Files/artifacts to inspect or edit: inspect `fpga/src/spi.nw`,
  generated `fpga/verilog/spi.v`, `fpga/tb/tb_spi_quad.sv`,
  `fpga/verilog/SB_IO.v`, `fpga/build/spi/spi_quad.json` if present,
  `fpga/build/spi/TEST.md`, shared `agent2/ledger.txt`, and
  `agent2/log.txt`. Do not edit source for this handoff.
- Commands allowed: inspect with `rg`, `sed`, `nl`, `git diff`, and
  artifact/log reads; from `/home/agent2/fast_data/fpga`, if the current
  generated netlist is missing or stale, run only the local generation
  needed to refresh it:
  `make -B verilog/spi.v verilog/SB_IO.v tb/tb_spi_quad.sv
  build/spi/check_spi_netlist.py`; no hardware run for this
  evidence-only handoff.
- Expected evidence artifact: a short timing/legality note grounded in
  the current `SB_IO` simulation model and generated/netlist structure,
  stating whether a CS-high fabric preload can be visible before the
  first post-CS falling edge on registered quad pads. Include exact file
  lines or JSON cell facts used, and state the next single source
  question only if the preload remains physically plausible.
- Stop condition: stop after answering that one feasibility question. If
  the answer is "not visible until falling edge," recommend abandoning
  CS-high fabric preload as the next source direction. If the answer is
  "visible before first falling edge," recommend one legal way to express
  the preload without any data-derived async reset assignment, but do not
  edit or run hardware in this handoff.
- Must not touch: the proven 1-lane behavior except by proving it remains
  green in later ordered runs, STM32 firmware, generated artifacts
  except normal regeneration if needed, mission pass/fail floors,
  timeouts, `/home/agent2/test_serv`, scope wiring, unrelated examples,
  TCEN, DLYB/sample-shift settings, FTHRES, MDMA TLEN, or any quad
  datapath rewrite.

### Worker Evidence: quad-pad-preload-feasibility

- Timestamp: `2026-05-01T09:26:05-07:00`.
- Status: ANSWERED; no source edits, no hardware run.
- Answer: with the current registered quad pads, changing fabric
  `D_OUT_0` while `cs_n` is high cannot affect the package-pin value
  sampled by the STM32 before a subsequent SCLK falling edge. CS-high
  fabric preload should be abandoned for the current `PIN_TYPE=6'b100101`,
  `NEG_TRIGGER=1'b1` quad pad mode.
- Evidence from the local simulation model: `fpga/verilog/SB_IO.v`
  lines 19-24 own an internal `dout_reg`, capture `D_OUT_0` only on
  `negedge OUTPUT_CLK`, and select that register for `PIN_TYPE=6'b100101`
  before driving `PACKAGE_PIN` through `OUTPUT_ENABLE`.
- Evidence from the upstream Yosys/iCE40 simulation model:
  `/usr/share/yosys/ice40/cells_sim.v` lines 53-60 capture `dout_q_0`
  from `D_OUT_0` on `negedge OUTPUT_CLK` when `NEG_TRIGGER=1`, and lines
  75-87 drive `PACKAGE_PIN` from the selected registered output for
  `PIN_TYPE[5:4] == 2'b10`. For `PIN_TYPE=100101`, bit 3 is 0 and bit 2
  is 1, so line 79 selects `dout_q_0`.
- Evidence from source/netlist: `fpga/src/spi.nw` lines 208-219
  instantiate the quad pads with `PIN_TYPE=6'b100101`,
  `NEG_TRIGGER=1'b1`, `OUTPUT_CLK(sclk)`, and `D_OUT_0(dout_lane[g])`.
  `fpga/build/spi/spi_quad.json` confirms all four quad pads have
  `PIN_TYPE=100101`, `NEG_TRIGGER=1`, shared `OUTPUT_CLK` net `[3]`,
  and `OUTPUT_ENABLE` net `[34]`.
- Next recommendation: route this to Manager as evidence that the
  registered-pad CS-high preload direction is closed. The next source
  question should be a different single mechanism, not another legal
  spelling of CS-high fabric preload.

### Manager Review: next quad FSM iteration

- Timestamp: `2026-05-01T09:27:05-07:00`.
- Manager accepts the latest Worker evidence: with quad pads still
  registered as `PIN_TYPE=6'b100101`, `NEG_TRIGGER=1'b1`, CS-high fabric
  preload cannot change the first package-pin value seen by the STM32
  before the next SCLK falling edge. Abandon CS-high fabric preload as
  the next source direction.
- Remaining active mission blocker is still ordered block 7
  `Check quad stream @ presc=11 wall rate >= 200 Mbps`: latest restored
  registered quad baseline is ledger `2026-05-01T08:53:05 spi 6`, with
  blocks 1-6 passed, single-lane mission proof still green, and quad
  block 7 failing with `stream_xfer 33554432 B quad in 1584 ms,
  169.4 Mbps`, `stream_got16 base=0 bytes=00 01 02 03 04 05 06 60 77 08
  09 0a 00 00 0f f1`, CRC `f31215b5` versus `310d8327`, and
  `firsterr=7`.
- Smallest remaining falsifiable mechanism: registered quad pads make the
  first selected data sample stale until one SCLK falling-edge capture has
  occurred. Instead of another FPGA preload attempt, test whether the
  STM32 QUADSPI raw quad stream can insert/discard exactly one initial
  dummy sample for quad auto-stream reads, leaving the registered FPGA
  datapath and all 1-lane behavior unchanged.
- Manager ran the required pre-WORK rig reset exactly once for this
  handoff from `/home/agent2/fast_data/fpga/build/uart` with
  `/home/agent2/test_serv/run_md.py`. It exited 0, attempted one UART
  block, passed all three UART checks with `n_errors=0`, and recorded
  ledger `2026-05-01T09:27:05 uart 3`.

### Next Handoff

- Status: ASSIGN WORK(firmware/quad-dummy-cycle-alignment). The required
  Manager rig reset is already green for this handoff.
- Primary question: for the quad raw auto-stream path used by block 7
  (`a 1`, `p 11`, `A 33554432 1 1`), does inserting exactly one quad
  dummy SCLK cycle before data capture make the STM32 discard the stale
  registered-pad first sample and pass block 7 correctness/rate?
- Files/artifacts to inspect or edit:
  `stm32mp135_test_board/baremetal/qspi/src/qspi.c`,
  `stm32mp135_test_board/baremetal/qspi/src/qspi.h`,
  `stm32mp135_test_board/baremetal/qspi/src/cli.c`,
  `fpga/build/spi/main.stm32`, `fpga/build/spi/TEST.md`,
  shared `agent2/ledger.txt`, and `agent2/log.txt`.
- Commands allowed: inspect with `rg`, `sed`, `nl`, `git diff`, and
  artifact/log reads; make the smallest quad-only firmware edit needed
  to request one initial dummy cycle/sample for raw quad auto-stream
  transfers; rebuild the QSPI baremetal firmware and ensure
  `fpga/build/spi/main.stm32` points to the rebuilt image; then from
  `/home/agent2/fast_data/fpga` run this iteration's single ordered
  baseline: `make -C build/spi sim`, `make -C build/spi bitstream`,
  `make -C build/spi all`, and
  `python3 -u /home/agent2/test_serv/run_md.py --ledger
  /home/agent2/fast_data/agent2/ledger.txt --module spi --log
  /home/agent2/fast_data/agent2/log.txt`.
- Expected evidence artifact: one ordered SPI ledger/log result showing
  whether block 7 with the quad-only one-dummy-cycle firmware change
  passes or fails, including the block 7 UART tail (`stream_xfer`,
  `stream_got16` if present, CRC, `firsterr`, `auto`, and `presc`).
- Stop condition: stop after that one ordered run answers the primary
  question. If block 7 still fails, revert only the dummy-cycle firmware
  edit and report the new signature. If block 7 passes and later blocks
  fail, keep the edit and report the first later failing block without
  broadening scope.
- Must not touch: FPGA source/generated files, the proven 1-lane
  datapath except by running the ordered baseline, mission pass/fail
  floors, timeouts, `/home/agent2/test_serv`, scope wiring, unrelated
  examples, TCEN, DLYB/sample-shift settings, FTHRES, MDMA TLEN, or any
  quad FPGA datapath rewrite.

### Worker Result: quad-dummy-cycle-alignment

- Status: RED; the one-dummy-cycle firmware experiment does not fix
  block 7 and has been reverted.
- Source edit tested: in
  `stm32mp135_test_board/baremetal/qspi/src/cli.c`, only
  `cmd_auto_stream` changed `dummy` from `raw ? 0U : 8U` to
  `raw ? (quad ? 1U : 0U) : 8U`, so only the `A <n> 1 1` raw quad
  auto-stream path requested one dummy cycle. Polling `b`, bulk-MDMA
  `m`, non-raw, and 1-lane raw paths were restored/left at zero dummy.
- Build evidence: QSPI baremetal firmware rebuilt successfully. The
  temporary dummy-cycle image hash used for the run was
  `2f5e117f269e49dd8742dbe32bb188d5654e22474895c5fa638a137316b9e3ec`;
  `fpga/build/spi/main.stm32` is a symlink to the rebuilt firmware image,
  so the SPI run used that image.
- Local gates before hardware: from `/home/agent2/fast_data/fpga`,
  `make -C build/spi sim`, `make -C build/spi bitstream`, and
  `make -C build/spi all` all exited 0.
- Ordered hardware run: ledger `2026-05-01T09:32:00 spi 6`. Blocks 1-6
  passed. The single-lane mission proof stayed green:
  `1lane stream @ presc=5 bytes=33554432 ... crc32=310d8327
  expect=310d8327 ... auto=on ... wall=2508ms
  wall_rate=107.032Mbps`.
- Block 7 failure tail with the one-dummy-cycle firmware:
  `p 11 1`, `auto=on`, `idle=off`, `A 33554432 1 1`,
  `stream_xfer 33554432 B quad in 1584 ms, 169.4 Mbps`,
  `stream_got16 base=0 bytes=00 10 20 30 40 50 66 07 70 80 90 a0 00 00
  ff 10`, and `stream 33554432 B quad in 2212 ms, 169.4 Mbps,
  crc32=c0693551, expect=310d8327, firsterr=1, chunk=16777216, chunks=2,
  buf=ddr, auto=on, presc=11, qspi_hz=656000000`.
- Interpretation: adding one STM32 dummy cycle changes the error
  signature from the restored registered baseline (`firsterr=7`,
  prefix `00 01 02 03 04 05 06 60 77 ...`) to an immediate nibble-shift
  signature (`firsterr=1`, prefix `00 10 20 30 40 50 ...`) without
  improving throughput. It is not the active fix.
- Revert evidence: the dummy-cycle source line is back to
  `const uint8_t dummy = raw ? 0U : 8U;` in all three CLI command paths,
  and both firmware image paths are restored to
  `932a68703dd0d8cb4c5ac9be2a5ff31c97aad49cd476898d7c44c35fb77eb659`.

### Manager Review: next quad FSM iteration

- Timestamp: `2026-05-01T09:34:12-07:00`.
- Manager accepts the latest Worker result: the quad-only one-dummy-cycle
  firmware experiment is red and was reverted. It kept blocks 1-6 green
  but changed block 7 from the restored registered-baseline signature
  (`firsterr=7`, prefix `00 01 02 03 04 05 06 60 77 ...`) to an
  immediate half-byte/nibble-shift signature (`firsterr=1`, prefix
  `00 10 20 30 40 50 66 07 70 80 90 a0 00 00 ff 10`). That disproves
  "discard exactly one initial quad sample" as the active fix.
- Remaining active mission blocker is still ordered block 7
  `Check quad stream @ presc=11 wall rate >= 200 Mbps`. Latest restored
  firmware image hash is
  `932a68703dd0d8cb4c5ac9be2a5ff31c97aad49cd476898d7c44c35fb77eb659`,
  and the proven single-lane block 6 remains green in the latest run.
- The next smallest missing evidence is not another dummy count or broad
  timing experiment. The key unresolved mechanism is whether the
  restored registered quad failure is fully explained by current source
  resetting `phase <= 1'b0` on every `cs_n` high while the fast `A` path
  has variable, sometimes odd-length selected frames.
- Manager ran the required pre-WORK rig reset exactly once for this
  handoff from `/home/agent2/fast_data/fpga/build/uart` with
  `/home/agent2/test_serv/run_md.py`. It exited 0, attempted one UART
  block, passed all three UART checks with `n_errors=0`, and recorded
  ledger `2026-05-01T09:34:12 uart 3`.

### Next Handoff

- Status: ASSIGN WORK(evidence-only/quad-cs-phase-boundary-model). The
  required Manager rig reset is already green for this handoff.
- Primary question: do the existing fast-`A` frame observer evidence and
  the three block-7 prefixes prove that the restored registered quad
  corruption occurs at a CS-selected frame boundary where source resets
  nibble `phase` to zero after an odd number of quad nibbles/bytes, as
  opposed to lane permutation, fixed dummy-cycle misalignment, or MDMA
  length?
- Files/artifacts to inspect or edit: inspect only
  `fpga/src/spi.nw`, `fpga/verilog/spi.v`, `fpga/tb/tb_spi_quad.sv`,
  `fpga/build/spi/TEST.md`, `fpga/build/spi/test_out/0fad7353bb40972e/`
  if still present, `agent2/TODO.md`, `agent2/ledger.txt`, and
  `agent2/log.txt`. Do not edit source or generated files for this
  handoff.
- Commands allowed: `rg`, `sed`, `nl`, `git diff`, `git status`, and
  artifact/log reads. No build, no firmware rebuild, and no hardware run.
- Expected evidence artifact: a short table/model comparing the current
  registered-baseline prefix (`00 01 02 03 04 05 06 60 77 ...`), the
  no-CS-reset prefix (`00 01 02 03 04 50 66 07 ...`), the one-dummy
  prefix (`00 10 20 30 40 50 66 07 ...`), and any available fast-`A`
  observer frame lengths against the exact quad `phase`, `dout_quad`, and
  `data_byte` transitions in source. The artifact must answer yes/no on
  the primary question and name at most one next mechanism if the answer
  is no.
- Stop condition: stop after answering that one model question. If the
  answer is yes, recommend one narrow source question about preserving
  byte/nibble phase only across selected-frame boundaries without
  touching 1-lane. If the answer is no, report which single competing
  mechanism remains most consistent with the prefixes. Do not edit or run
  hardware in this handoff.
- Must not touch: FPGA source/generated files, STM32 firmware, the proven
  1-lane datapath, mission pass/fail floors, timeouts,
  `/home/agent2/test_serv`, scope wiring, unrelated examples, TCEN,
  DLYB/sample-shift settings, FTHRES, MDMA TLEN, dummy cycles, or any
  quad datapath rewrite.

### Worker Result: quad-stale-first-sample-absorb

- Status: RED; the quad-only stale-first-sample absorb source experiment
  did not fix block 7 and has been reverted.
- Source edit tested: in `fpga/src/spi.nw` quad lane only, Worker added
  `frame_skip` and `ever_selected` state. On `posedge cs_n`, the edit set
  `frame_skip <= 1'b1`; on the first selected post-CS `posedge sclk`
  after the design had already seen a selected edge, it cleared
  `frame_skip` without changing `phase`, `data_byte`, or `dout_quad`.
  The initial transaction after FPGA configuration was allowed to advance
  normally to avoid the known one-dummy immediate nibble-shift failure.
- Local build evidence before hardware: generated `verilog/spi.v`,
  `verilog/SB_IO.v`, `tb/tb_spi_quad.sv`, and
  `build/spi/check_spi_netlist.py`; `make -C build/spi sim` exited 0,
  but the quad behavioral test printed the expected experimental
  post-CS lag signature (`FAIL tb_spi_quad: 4157 mismatches`). Netlist
  checks still passed. `make -C build/spi bitstream` and
  `make -C build/spi all` exited 0.
- Ordered hardware run: ledger `2026-05-01T09:44:27 spi 6`. Blocks 1-6
  passed, including the proven single-lane fast path:
  `1lane stream @ presc=5 bytes=33554432 ... crc32=310d8327
  expect=310d8327 ... auto=on ... wall=2507ms
  wall_rate=107.074Mbps`.
- Block 7 failure tail with stale-first-sample absorb:
  `p 11 1`, `auto=on`, `idle=off`, `A 33554432 1 1`,
  `stream_xfer 33554432 B quad in 1584 ms, 169.4 Mbps`,
  `stream_got16 base=0 bytes=00 01 02 03 04 40 55 06 60 77 89 0a 00 00
  dd 0e`, and `stream 33554432 B quad in 2253 ms, 169.4 Mbps,
  crc32=693bd955, expect=310d8327, firsterr=5, chunk=16777216, chunks=2,
  buf=ddr, auto=on, presc=11, qspi_hz=656000000`.
- Interpretation: absorbing the first selected post-CS sample by holding
  `phase`/`data_byte` is not the active fix. It changes the restored
  registered-baseline `firsterr=7` signature to `firsterr=5` and creates
  mixed-nibble bytes (`40 55 06 60 77 89 ...`) without improving the
  169.4 Mbps transfer-rate ceiling.
- Revert evidence: the quad lane source and generated artifacts were
  restored and rebuilt. Cleanup command
  `make -B verilog/spi.v verilog/SB_IO.v tb/tb_spi_quad.sv
  build/spi/check_spi_netlist.py && make -C build/spi sim &&
  make -C build/spi bitstream && make -C build/spi all` exited 0.
  Cleanup sim printed `PASS tb_spi_1lane` and `PASS tb_spi_quad`, and
  netlist checks passed. Restored artifact hashes:
  `spi_1lane.bin=702c4641f4e2d77d60ee2d502c2beea506c6506e55eaa39c06779bc4c30e7941`,
  `spi_quad.bin=cbca2c3badc1349f818b9bf09fceadae2d64ac95287cbe6d138075d86c1d0f5f`,
  `verilog/spi.v=beb6b3598a159bd27de92626c8d2427e15371992c4a61005ed6a479033917fa7`,
  and both firmware image paths are
  `932a68703dd0d8cb4c5ac9be2a5ff31c97aad49cd476898d7c44c35fb77eb659`.

### Worker Evidence: quad-cs-phase-boundary-model

- Status: ANSWERED; no source edits, no build, no firmware rebuild, and
  no hardware run.
- Answer: no, the existing prefixes do not prove the restored registered
  quad corruption is solely the source resetting `phase <= 1'b0` on a
  CS-selected frame boundary after an odd number of quad nibbles. They
  strongly implicate selected-frame boundary / registered-pad phase
  behavior and make lane permutation, fixed one-dummy-cycle misalignment,
  and MDMA length unlikely, but the exact signatures are not reproduced
  by a sufficient "preserve `phase` across CS" model.
- Source transition model: current quad source in `fpga/src/spi.nw`
  lines 145-161 has `phase`, `dout_quad`, and `data_byte`. On every
  selected `posedge sclk`, STM32 samples the current registered pad
  value; then source assigns `dout_quad <= data_byte[3:0]` when
  `phase == 0`, or `dout_quad <= next_byte_upper` and increments
  `data_byte` when `phase == 1`. The registered pads then capture that
  presenter on the following SCLK falling edge. `posedge cs_n` resets
  only `phase` to zero; it does not reset `data_byte` or the IOB output
  flop.
- Boundary model table:

  | Evidence | Prefix / result | Model fit |
  | --- | --- | --- |
  | Restored registered baseline | `00 01 02 03 04 05 06 60 77 08 09 0a 00 00 0f f1`, `firsterr=7`, `169.4 Mbps` | Initial bytes rule out static lane permutation. `x0`/duplicated-nibble style bytes are consistent with a selected-frame boundary disturbing nibble role, but the exact `60 77` pair is not the direct result of one simple odd-nibble CS reset in the source model. |
  | No-CS-reset experiment | `00 01 02 03 04 50 66 07 09 0a 00 00 0f 11 12 13`, `firsterr=5`, `169.3 Mbps` | If phase reset alone were the sufficient root cause, preserving phase across CS would be expected to clear the corruption. It instead moved the first error earlier and produced a different mixed-nibble signature, so the model is incomplete. |
  | One-dummy firmware experiment | `00 10 20 30 40 50 66 07 70 80 90 a0 00 00 ff 10`, `firsterr=1`, `169.4 Mbps` | A fixed one-sample discard creates an immediate half-byte/nibble-shift pattern and does not improve rate, so fixed dummy-cycle misalignment is not the active fix. |
  | TLEN=4 experiment | Same restored-baseline prefix with worse `154.8 Mbps` | MDMA request length is unlikely to be the cause; changing it did not change correctness in the useful direction. |

- Interpretation: the failure is selected-frame / registered-pad
  alignment, not a static lane map. However, the available prefixes do
  not prove that only `phase` carry across CS is enough. The single
  competing mechanism most consistent with all prefixes is that the first
  sample of each STM32-selected microframe is a stale IOB value, and
  source must either present a frame-start-correct nibble through a pad
  mode that can make it visible before the first selected rising edge or
  explicitly model/absorb that stale first sample in the FPGA stream
  state. The prior CS-high preload evidence showed the current
  registered pad mode cannot make a fabric preload visible before the
  first falling edge.
- Next recommendation: Manager should assign one narrow source/evidence
  question around the stale-first-sample registered-pad boundary
  mechanism, not another dummy count, MDMA granularity, lane permutation,
  or generic phase-carry edit.

### Manager Review: next quad FSM iteration

- Timestamp: `2026-05-01T09:37:17-07:00`.
- Manager accepts the latest Worker evidence: the phase-reset-only CS
  boundary model is not proven sufficient. The evidence still implicates
  selected-frame / registered-pad stale-first-sample behavior, and it
  rules out static lane permutation, a fixed one-dummy-cycle discard, and
  MDMA TLEN/request length as primary fixes. Prior evidence also shows
  CS-high fabric preload cannot be visible before the first falling edge
  in the current registered `SB_IO` mode.
- Remaining active mission blocker is ordered block 7
  `Check quad stream @ presc=11 wall rate >= 200 Mbps`. Latest restored
  registered-baseline hardware remains ledger `2026-05-01T08:53:05 spi
  6`: blocks 1-6 passed, including the single-lane mission proof, then
  block 7 failed with `stream_xfer 33554432 B quad in 1584 ms, 169.4
  Mbps`, `stream_got16 base=0 bytes=00 01 02 03 04 05 06 60 77 08 09 0a
  00 00 0f f1`, CRC `f31215b5` versus `310d8327`, and `firsterr=7`.
- Smallest remaining falsifiable mechanism: on the first selected
  rising edge after each CS-low microframe, the STM32 samples the
  previously registered IOB nibble, but the current quad source may
  advance `phase`/`data_byte` as though it had delivered the new
  presenter nibble. Test only whether absorbing that stale first sample
  in the FPGA quad state machine, without changing pad mode or 1-lane
  logic, improves block 7 correctness/rate.
- Manager ran the required pre-WORK rig reset exactly once for this
  handoff from `/home/agent2/fast_data/fpga/build/uart` with
  `/home/agent2/test_serv/run_md.py`. It exited 0, attempted one UART
  block, passed all three UART checks with `n_errors=0`, and recorded
  ledger `2026-05-01T09:37:17 uart 3`.

### Next Handoff

- Status: ASSIGN WORK(source/quad-stale-first-sample-absorb). The
  required Manager rig reset is already green for this handoff.
- Primary question: for the quad raw auto-stream path used by block 7
  (`a 1`, `p 11 1`, `A 33554432 1 1`), does a quad-only FPGA change that
  treats the first selected post-CS rising-edge sample as a stale
  already-registered nibble, and therefore does not advance
  `phase`/`data_byte` for that first sample, make block 7 pass
  correctness and the 200 Mbps wall-rate floor?
- Files/artifacts to inspect or edit: inspect and minimally edit
  `fpga/src/spi.nw`; regenerate only the affected SPI generated
  artifacts such as `fpga/verilog/spi.v`,
  `fpga/tb/tb_spi_quad.sv`, and
  `fpga/build/spi/check_spi_netlist.py` if required by the normal
  literate flow; inspect `fpga/build/spi/TEST.md`,
  shared `agent2/ledger.txt`, and `agent2/log.txt`.
- Commands allowed: inspect with `rg`, `sed`, `nl`, `git diff`, and
  `git status`; make the smallest quad-only source edit for the
  stale-first-sample absorb mechanism; then from
  `/home/agent2/fast_data/fpga` run this iteration's single ordered
  baseline: `make -C build/spi sim`, `make -C build/spi bitstream`,
  `make -C build/spi all`, and
  `python3 -u /home/agent2/test_serv/run_md.py --ledger
  /home/agent2/fast_data/agent2/ledger.txt --module spi --log
  /home/agent2/fast_data/agent2/log.txt`.
- Expected evidence artifact: one ordered SPI ledger/log result showing
  whether block 7 with the stale-first-sample absorb edit passes or
  fails, including the block 7 UART tail (`stream_xfer`,
  `stream_got16` if present, CRC, `firsterr`, `auto`, `presc`, and
  wall-rate). Also report the exact source chunk changed and the diff.
- Stop condition: stop after that one ordered run answers the primary
  question. If block 7 still fails, revert only the stale-first-sample
  absorb source edit and report the new signature. If block 7 passes and
  later blocks fail, keep the edit and report the first later failing
  block without broadening scope.
- Must not touch: STM32 firmware, the proven 1-lane datapath except by
  preserving and verifying it through the ordered baseline, mission
  pass/fail floors, timeouts, `/home/agent2/test_serv`, scope wiring,
  unrelated examples, TCEN, DLYB/sample-shift settings, FTHRES, MDMA
  TLEN, dummy cycles, lane permutation, or any broader quad datapath
  rewrite.

### Manager Review - 2026-05-01T09:48:09-07:00

- Latest Worker result supersedes the stale-first-sample absorb handoff
  above. The quad-only stale-first-sample absorb source experiment failed
  and was reverted. Cleanup `sim`, `bitstream`, and `all` were green with
  restored artifact hashes.
- Latest ordered hardware evidence is ledger `2026-05-01T09:44:27 spi
  6`: blocks 1-6 passed, including the single-lane mission proof at
  block 6 with `bytes=33554432`, matching CRC `310d8327`,
  `firsterr=-1`, `auto=on`, `qspi_hz=656000000`, `wall=2507ms`, and
  `wall_rate=107.074Mbps`.
- The remaining active mission blocker is block 7
  `Check quad stream @ presc=11 wall rate >= 200 Mbps`. Latest failed
  quad evidence completed the transfer but reported corruption:
  `firsterr=5` with prefix
  `00 01 02 03 04 40 55 06 60 77 89 0a 00 00 dd 0e`. This keeps the
  active failure on quad data correctness before the wall-rate proof can
  be accepted.
- Smallest next falsifiable mechanism question: is the block 7
  corruption already present in the non-auto CPU-polled quad raw read
  path at the same `p 11 1` setting, or is it specific to the
  auto-consume `A`/DDR stream path?
- Manager ran the required pre-WORK rig reset exactly once for this
  handoff from `/home/agent2/fast_data/fpga/build/uart` with
  `/home/agent2/test_serv/run_md.py`. It exited 0, attempted one UART
  block, passed all three UART checks with `n_errors=0`, and recorded
  ledger `2026-05-01T09:48:09 uart 3`.

### Next Handoff

- Status: ASSIGN WORK(evidence-only/quad-raw-vs-auto). The required
  Manager rig reset is already green for this handoff.
- Primary question: at the same quad `p 11 1` setting used by block 7,
  does a short non-auto CPU-polled quad raw read return the incrementing
  pattern correctly, or does it reproduce the `firsterr=5`/bad-prefix
  class seen in `A 33554432 1 1`?
- Files/artifacts to inspect or temporarily edit: inspect
  `fpga/build/spi/TEST.md`, `fpga/build/spi/verify.py`,
  `stm32mp135_test_board/baremetal/qspi/src/cli.c`, shared
  `agent2/ledger.txt`, and shared `agent2/log.txt`. If needed, edit only
  generated `fpga/build/spi/TEST.md` for the duration of the experiment
  so the ordered run reaches block 7 with `p 11 1` followed by one short
  CPU-polled quad raw command, then restore `TEST.md` before returning.
- Commands allowed: inspect with `rg`, `sed`, `nl`, `git diff`, and
  `git status`; run no FPGA or firmware source edits; run at most one
  ordered SPI hardware invocation from `/home/agent2/fast_data/fpga/build/spi`
  using `python3 -u /home/agent2/test_serv/run_md.py --ledger
  /home/agent2/fast_data/agent2/ledger.txt --module spi --log
  /home/agent2/fast_data/agent2/log.txt`.
- Expected evidence artifact: one ordered SPI ledger/log result and the
  block 7 UART transcript proving either `quad raw` correctness
  (`firsterr=-1` with the expected incrementing prefix) or the same
  corruption class (`firsterr`, CRC/expect if printed, and first 16
  bytes). Also report the exact temporary `TEST.md` diff and confirm it
  was restored.
- Stop condition: stop immediately after answering that one question. If
  the short CPU-polled quad raw read passes, report auto-consume/DDR
  stream path as the next narrowed suspect. If it fails, report the
  failing prefix as wire/FPGA quad datapath evidence for the next
  Manager. Do not proceed to fixes in the same Worker turn.
- Must not touch: FPGA source, STM32 firmware source, generated
  verifier pass/fail thresholds, timeouts, mission floors,
  `/home/agent2/test_serv`, proven 1-lane behavior, DLYB/sample-shift
  settings, FTHRES, MDMA TLEN, dummy cycles, lane permutation, TCEN, or
  any broad quad rewrite.

### Worker Evidence: quad-raw16-observer

- Status: RED against a clean intended quad nibble stream; no FPGA or
  STM32 source edits. The temporary generated `TEST.md` observer probe
  was restored. Restored `TEST.md` hash:
  `d92088c82284a5defc2fafacea7cc5d7cb88f0d10a16292a4ee88dc715833567`.
- Existing debug bitstream used:
  `fpga/build/spi/spi_quad_debug.bin`, hash
  `8c5b584c74a2e7946e21525750e0dd82c2c772fd71c803dfbc4206db7f677e7e`.
- Temporary generated `TEST.md` diff applied for block 7 only:
  removed `a 1`/`auto=on`, removed `N 0`/`idle=off`, replaced
  `fpga:program bin=@spi_quad.bin` with
  `fpga:program bin=@spi_quad_debug.bin`, opened FPGA UART, kept
  `p 11 1`, replaced `A 33554432 1 1` and
  `stream_xfer 33554432 B` with `b 16 1 1` and sentinel
  `bench 16 B quad @ presc=11`, delayed 1500 ms for observer output,
  and closed FPGA UART. The final `, firsterr=-1` sentinel was removed
  for this observer-only evidence run.
- Ordered hardware run: ledger `2026-05-01T10:08:20 spi 6`. Blocks 1-6
  passed, including the single-lane fast path at
  `wall_rate=106.861Mbps`.
- Block 7 MP135 UART transcript for the observer-backed 16-byte
  CPU-polled quad raw probe:
  `BENCHDBG poll_done t=10238 len=16 firsterr=8` and
  `bench 16 B quad @ presc=11 ... firsterr=8,
  got=00 01 02 03 04 05 06 07 89 0a 0b cc 0d d0 ee 0f`.
- FPGA observer lines from the same run did not show the clean intended
  incrementing quad stream. Early representative lines:
  `Q F=09 E=0001 N=0000000000000000000000000000000f`,
  `Q F=0d E=0004 N=000000000000000000000000002d90b9`,
  `Q F=46 E=0012 N=000b00000b0b000b0990abd09f9fb9f9`, and
  `Q F=e2 E=0014 N=00b000001b0000090d0090db020ba999`.
- Interpretation: the observer-backed run is consistent with a quad
  selected-frame / FPGA state-framing problem before auto/DDR/MDMA.
  The exact MP135 first error shifted under the debug bitstream
  (`firsterr=8`, prefix `00 01 02 03 04 05 06 07 89 0a 0b cc 0d d0 ee
  0f`) versus restored `spi_quad.bin` (`firsterr=7`, prefix
  `00 01 02 03 04 05 06 60 77 08 09 0a 00 00 0f f1`), so the debug
  bitstream should be treated as diagnostic evidence rather than a
  bit-identical reproduction. It still rules out "FPGA observer sees a
  clean intended nibble stream while MP135 alone corrupts it."

### Worker Evidence: quad-raw-vs-auto-short16

- Status: RED against quad raw correctness; no FPGA or STM32 source
  edits. The temporary generated `TEST.md` probe was restored with
  `make -B build/spi/TEST.md`.
- Temporary generated `TEST.md` diff applied for block 7 only:
  removed `a 1`/`auto=on`, removed `N 0`/`idle=off`, kept `p 11 1`,
  kept `fpga:program bin=@spi_quad.bin`, replaced
  `A 33554432 1 1` and `stream_xfer 33554432 B` with
  `b 16 1 1` and sentinel `bench 16 B quad @ presc=11`. The final
  sentinel remained `, firsterr=-1`.
- Ordered hardware run: ledger `2026-05-01T09:59:55 spi 6`. Blocks 1-6
  passed, including the single-lane fast path:
  `1lane stream @ presc=5 bytes=33554432 ... crc32=310d8327
  expect=310d8327 ... firsterr=-1 ... auto=on ... wall=2507ms
  wall_rate=107.074Mbps`.
- Block 7 UART transcript for the 16-byte CPU-polled quad raw probe:
  `p 11 1`, `presc=11 sshift=1 dlyb=0 unit=0`,
  `b 16 1 1`,
  `BENCHDBG cmd_pre t=9930 len=16 quad=1 opcode=6b presc=11`,
  `BENCHDBG poll_enter t=9935 opcode=6b lines=4 dummy=0 len=16`,
  `BENCHDBG poll_done t=9941 len=16 firsterr=7`,
  `BENCHDBG cmd_post t=9945 rc=0 dt=0 firsterr=7`, and
  `bench 16 B quad @ presc=11 in 1 ms, 0.1 Mbps, crc32=9f2f1fc2,
  expect=cecee288, firsterr=7, got=00 01 02 03 04 05 06 60 77 08 09
  0a 00 00 0f f1`.
- Interpretation: quad corruption is already present in the short
  non-auto CPU-polled raw path at the same `p 11 1` setting. This rules
  out auto-consume, DDR buffering, MDMA, and hardware CRC as the primary
  source of the block 7 data error. The failure signature matches the
  restored auto-stream bad-prefix class (`firsterr=7`,
  `00 01 02 03 04 05 06 60 77 08 09 0a 00 00 0f f1`), so the active
  blocker is the quad wire/FPGA datapath or QUADSPI selected-frame
  protocol before the stream engine.
- Restore evidence: block 7 in `fpga/build/spi/TEST.md` is restored to
  the original auto-stream plan with `a 1`, `N 0`,
  `A 33554432 1 1`, and `stream_xfer 33554432 B`.

### Worker Evidence: quad-raw-vs-auto

- Status: INCONCLUSIVE; no FPGA or STM32 source edits. The temporary
  generated `TEST.md` probe was restored.
- Temporary generated `TEST.md` diff applied for block 7 only:
  removed `a 1`/`auto=on`, removed `N 0`/`idle=off`, kept `p 11 1`,
  kept `fpga:program bin=@spi_quad.bin`, replaced
  `A 33554432 1 1` and `stream_xfer 33554432 B` with
  `b 4096 1 1` and sentinel `bench 4096 B quad @ presc=11`. The final
  sentinel remained `, firsterr=-1`.
- Ordered hardware run: ledger `2026-05-01T09:52:15 spi 6`. Blocks 1-6
  passed, including the single-lane fast path:
  `1lane stream @ presc=5 bytes=33554432 ... crc32=310d8327
  expect=310d8327 ... auto=on ... wall=2514ms
  wall_rate=106.776Mbps`.
- Block 7 UART transcript for the 4 KiB CPU-polled quad raw probe:
  `p 11 1`, `presc=11 sshift=1 dlyb=0 unit=0`,
  `b 4096 1 1`,
  `BENCHDBG cmd_pre t=10277 len=4096 quad=1 opcode=6b presc=11`, and
  `BENCHDBG poll_enter t=10282 opcode=6b lines=4 dummy=0 len=4096`.
  No `bench 4096 B quad @ presc=11` line and no `firsterr` summary
  appeared before the 15 s sentinel timeout.
- Interpretation: this did not answer whether CPU-polled quad raw data
  is correct at `p 11 1`; 4096 bytes is too long for the CPU-polled
  path under the existing block timeout. It does not prove auto/DDR is
  at fault and does not prove raw wire/datapath failure. The next
  smallest evidence question should use the same mechanism with a much
  shorter length, likely 16 or 32 bytes, so `cmd_bench` can print
  `got=` and `firsterr` before timeout.
- Restore evidence: `make -B build/spi/TEST.md` restored block 7 to the
  original `A 33554432 1 1` auto-stream plan with `a 1`, `N 0`, and
  `stream_xfer 33554432 B` sentinel.

### Manager Review - 2026-05-01T09:54:30-07:00

- Manager accepts the latest Worker result as inconclusive rather than
  red against either raw or auto path. The temporary 4 KiB CPU-polled
  quad raw probe kept blocks 1-6 green, including the single-lane
  mission proof at `wall_rate=106.776Mbps`, but block 7 produced only
  `BENCHDBG cmd_pre` and `BENCHDBG poll_enter` before the existing
  15 s sentinel timeout. It did not print a `bench ...` summary,
  CRC/firsterr, or first bytes, so it did not answer whether raw quad
  corruption is already present outside the auto-consume DDR stream
  path.
- Remaining active mission blocker is still block 7
  `Check quad stream @ presc=11 wall rate >= 200 Mbps`. Single-lane
  auto-stream remains proven above 100 Mbps by the latest run and prior
  ordered evidence. Quad block 7 remains red on the auto-stream path,
  with the latest valid restored-baseline class completing at about
  `169.4Mbps` and corrupting data before the 200 Mbps proof can be
  accepted.
- Smallest next falsifiable question: repeat the same raw-vs-auto
  distinction with the shortest CPU-polled quad raw read that should
  complete well inside the existing block timeout and print the raw
  bench prefix/firsterr. Use 16 bytes, not another broad probe, source
  edit, firmware edit, or timeout change.
- Manager ran the required pre-WORK rig reset exactly once for this
  handoff from `/home/agent2/fast_data/fpga/build/uart` with
  `/home/agent2/test_serv/run_md.py`. It exited 0, attempted one UART
  block, passed all three UART checks with `n_errors=0`, and recorded
  ledger `2026-05-01T09:54:30 uart 3`.

### Next Handoff

- Status: ASSIGN WORK(evidence-only/quad-raw-vs-auto-short16). The
  required Manager rig reset is already green for this handoff.
- Primary question: at the same quad `p 11 1` setting used by block 7,
  does a 16-byte non-auto CPU-polled quad raw read return the
  incrementing pattern correctly, or does it reproduce the quad
  corruption class seen in `A 33554432 1 1`?
- Files/artifacts to inspect or temporarily edit: inspect
  `fpga/build/spi/TEST.md`, `fpga/build/spi/verify.py`,
  `stm32mp135_test_board/baremetal/qspi/src/cli.c`, shared
  `agent2/ledger.txt`, and shared `agent2/log.txt`. If needed, edit
  only generated `fpga/build/spi/TEST.md` for the duration of the
  experiment so the ordered run reaches block 7 with `p 11 1` followed
  by exactly `b 16 1 1`, then restore `TEST.md` before returning.
- Commands allowed: inspect with `rg`, `sed`, `nl`, `git diff`, and
  `git status`; run no FPGA or firmware source edits; run at most one
  ordered SPI hardware invocation from
  `/home/agent2/fast_data/fpga/build/spi` using
  `python3 -u /home/agent2/test_serv/run_md.py --ledger
  /home/agent2/fast_data/agent2/ledger.txt --module spi --log
  /home/agent2/fast_data/agent2/log.txt`.
- Expected evidence artifact: one ordered SPI ledger/log result and the
  block 7 UART transcript proving either 16-byte quad raw correctness
  (`firsterr=-1` with the expected `00 01 02 ... 0f` prefix) or raw
  quad corruption (`firsterr`/CRC if printed and the first 16 bytes).
  Also report the exact temporary `TEST.md` diff and confirm it was
  restored.
- Stop condition: stop immediately after answering that one 16-byte
  CPU-polled raw question. If it passes, report the auto-consume/DDR
  stream path as the next narrowed suspect. If it fails, report the
  failing prefix as raw wire/FPGA quad datapath evidence for the next
  Manager. If even 16 bytes does not produce a bench summary before the
  existing sentinel, report that as a CPU-polled quad raw hang and do
  not try another length in this Worker turn.
- Must not touch: FPGA source, STM32 firmware source, generated
  verifier pass/fail thresholds, timeouts, mission floors,
  `/home/agent2/test_serv`, proven 1-lane behavior, DLYB/sample-shift
  settings, FTHRES, MDMA TLEN, dummy cycles, lane permutation, TCEN, or
  any broad quad rewrite.

### Manager Review - 2026-05-01T10:02:26-07:00

- Manager accepts the latest Worker evidence `quad-raw-vs-auto-short16`
  as red against quad raw correctness. The restored ordered run ledger
  `2026-05-01T09:59:55 spi 6` passed blocks 1-6, including the
  single-lane mission proof at `wall_rate=107.074Mbps`, then a temporary
  block-7 `p 11 1` / `b 16 1 1` raw quad probe completed and failed
  with `firsterr=7` and first bytes
  `00 01 02 03 04 05 06 60 77 08 09 0a 00 00 0f f1`.
- The generated `fpga/build/spi/TEST.md` has been restored to the
  original block 7 auto-stream sequence: `a 1`, `N 0`,
  `A 33554432 1 1`, and sentinel `stream_xfer 33554432 B`.
- The active blocker is therefore upstream of auto-consume, DDR, MDMA,
  and hardware CRC: quad data is already corrupt in a 16-byte CPU-polled
  raw transfer at the same `p 11 1` setting. Prior observer evidence
  showed selected quad frame lengths vary on the fast path, but the
  latest exact 16-byte raw failure has not yet been paired with
  FPGA-side frame/nibble observation.
- Smallest next falsifiable question: use the already-present diagnostic
  `spi_quad_debug.bin` observer, without source edits, for the same
  16-byte raw command to determine whether the FPGA-side selected-frame
  observations align with the STM32 bad prefix or instead show the
  intended incrementing nibble stream.
- Manager ran the required pre-WORK rig reset exactly once for this
  handoff from `/home/agent2/fast_data/fpga/build/uart` with
  `/home/agent2/test_serv/run_md.py`. It exited 0, attempted one UART
  block, passed all three UART checks with `n_errors=0`, and recorded
  ledger `2026-05-01T10:02:26 uart 3`.

### Next Handoff

- Status: ASSIGN WORK(evidence-only/quad-raw16-observer). The required
  Manager rig reset is already green for this handoff.
- Primary question: for the same `p 11 1` / `b 16 1 1` CPU-polled quad
  raw command that produced `firsterr=7`, does the existing
  `spi_quad_debug.bin` FPGA observer report selected-frame edge counts
  and first nibbles consistent with the STM32 bad prefix, or with the
  intended incrementing quad stream?
- Files/artifacts to inspect or temporarily edit: inspect
  `fpga/build/spi/TEST.md`, `fpga/build/spi/spi_quad_debug.bin`,
  `fpga/verilog/spi_quad_debug.v`, shared `agent2/ledger.txt`, and
  shared `agent2/log.txt`. If needed, edit only generated
  `fpga/build/spi/TEST.md` for the duration of the experiment so ordered
  block 7 programs `@spi_quad_debug.bin`, keeps `p 11 1`, and runs
  exactly `b 16 1 1`; restore `TEST.md` before returning.
- Commands allowed: inspect with `rg`, `sed`, `nl`, `ls`, `sha256sum`,
  `git diff`, and `git status`; run no FPGA or STM32 source edits and
  no rebuild unless `spi_quad_debug.bin` is missing; run at most one
  ordered SPI hardware invocation from
  `/home/agent2/fast_data/fpga/build/spi` using
  `python3 -u /home/agent2/test_serv/run_md.py --ledger
  /home/agent2/fast_data/agent2/ledger.txt --module spi --log
  /home/agent2/fast_data/agent2/log.txt`.
- Expected evidence artifact: one ordered SPI ledger/log result with the
  block 7 MP135 UART transcript and FPGA UART `Q F=... E=... N=...`
  observer lines for the 16-byte raw command, plus the temporary
  `TEST.md` diff and restoration confirmation.
- Stop condition: stop immediately after that one observer-backed
  16-byte raw run answers the primary question; if the FPGA observer
  shows intended nibbles while MP135 reports the bad prefix, report a
  capture/timing/peripheral interpretation suspect, and if the observer
  shows frame/nibble behavior matching the bad prefix, report an FPGA
  quad state/framing suspect.
- Must not touch: FPGA source, STM32 firmware source, generated
  verifier pass/fail thresholds, timeouts, mission floors,
  `/home/agent2/test_serv`, proven 1-lane behavior, DLYB/sample-shift
  settings, FTHRES, MDMA TLEN, dummy cycles, lane permutation, TCEN, or
  any broad quad rewrite.

### Manager Review - 2026-05-01T10:11:17-07:00

- Latest routed evidence is `quad-raw16-observer`, superseding the older
  inconclusive 4 KiB raw probe. Ordered ledger `2026-05-01T10:08:20 spi
  6` passed blocks 1-6, including the proven single-lane fast path at
  `wall_rate=106.861Mbps`, then used the existing
  `spi_quad_debug.bin` at block 7 with `p 11 1` and `b 16 1 1`.
- The 16-byte CPU-polled quad raw probe failed before auto/DDR/MDMA:
  MP135 reported `firsterr=8` and
  `got=00 01 02 03 04 05 06 07 89 0a 0b cc 0d d0 ee 0f`. The companion
  non-debug short16 evidence with normal `spi_quad.bin` reported the
  restored mission signature, `firsterr=7` and
  `got=00 01 02 03 04 05 06 60 77 08 09 0a 00 00 0f f1`.
- The FPGA observer did not show a clean intended stream. Representative
  lines include `Q F=09 E=0001 N=...000f`,
  `Q F=0d E=0004 N=...2d90b9`,
  `Q F=46 E=0012 N=000b00000b0b000b0990abd09f9fb9f9`, and
  `Q F=e2 E=0014 N=00b000001b0000090d0090db020ba999`. Because this
  observer bitstream changes the exact first-error signature, treat it
  as diagnostic evidence that the FPGA/pin-side stream is not clean, not
  as a bit-identical reproduction of block 7.
- Current source inspection shows the quad lane still uses registered
  pads (`PIN_TYPE=6'b100101`, `NEG_TRIGGER=1'b1`) and a posedge
  presenter. The current code resets `phase <= 1'b0` on `cs_n`, while
  prose still says quad byte counter and nibble phase carry across
  CS-high gaps. Prior direct source experiments around no-CS-reset,
  dummy-cycle discard, stale-first-sample absorb, and unregistered
  quad pads were all red, so the next step should not be another broad
  datapath edit.
- Smallest remaining falsifiable step: build a deterministic local model
  of the current registered quad state machine and the known CS-selected
  microframe lengths to see whether the exact normal short16 prefix
  `00 01 02 03 04 05 06 60 77 08 09 0a 00 00 0f f1` is reproducible
  from the present `phase`/`dout_quad`/`data_byte` rules and registered
  pad latency. This should identify one concrete next source mechanism
  or prove the model is missing another observable.
- Manager ran the required pre-WORK rig reset exactly once for this
  handoff from `/home/agent2/fast_data/fpga/build/uart`. The first
  invocation hit the documented unset `$TEST_SERV` expansion failure
  before `run_md.py` started; the allowed default retry with
  `/home/agent2/test_serv/run_md.py` exited 0, attempted one UART block,
  passed all three checks with `n_errors=0`, and recorded ledger
  `2026-05-01T10:11:17 uart 3`.

### Next Handoff

- Status: ASSIGN WORK(evidence-only/quad-registered-prefix-model). The
  required Manager rig reset is already green for this handoff.
- Primary question: can the current registered quad state machine plus
  CS-selected microframe boundaries reproduce the normal short16 raw
  failure prefix `00 01 02 03 04 05 06 60 77 08 09 0a 00 00 0f f1`,
  and what single source mechanism does that model identify next?
- Files/artifacts to inspect or edit: inspect `fpga/src/spi.nw`,
  `fpga/verilog/spi.v`, `fpga/tb/tb_spi_quad.sv`,
  `fpga/verilog/spi_quad_debug.v`, `fpga/build/spi/TEST.md`,
  `fpga/build/spi/test_out/22e840aa6cedf664/`, shared
  `agent2/ledger.txt`, shared `agent2/log.txt`, and this `TODO.md`. Do
  not edit source or generated files for this handoff.
- Commands allowed: `rg`, `sed`, `nl`, `git diff`, `git status`, and
  artifact/log reads. A small throwaway local script or shell one-liner
  may be used only to model nibble/state sequences; no build, firmware
  rebuild, or hardware run.
- Expected evidence artifact: one concise model note/table comparing the
  normal `spi_quad.bin` short16 prefix, the `spi_quad_debug.bin`
  observer short16 prefix, and the current source transitions for
  `phase`, `dout_quad`, `data_byte`, registered pad output, and any
  inferred CS-selected frame boundaries.
- Stop condition: stop after the model either reproduces the normal
  short16 prefix and names one narrow next source edit, or fails to
  reproduce it and names the one missing observable needed before source
  work.
- Must not touch: FPGA source/generated files, STM32 firmware,
  `/home/agent2/test_serv`, mission pass/fail floors, timeouts, proven
  1-lane behavior, DLYB/sample-shift settings, FTHRES, MDMA TLEN, dummy
  cycles, lane permutation rewrites, TCEN, scope wiring, unrelated
  examples, or any hardware run.
