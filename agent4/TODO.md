# TODO: QSPI FPGA→MP135 — 1 GiB at 0 BER + 400 Mbps

## Mission

Demonstrate FPGA→STM32MP135 QSPI quad-output transfer of arbitrary data at **≥400 Mbps wall rate with ZERO bit errors verified end-to-end over ≥1 GiB**. Final state of the repo must be a SINGLE canonical chapter (`src/mission.nw`) that reproduces the result; all exploratory chapters (`mmap_slave.nw`, `mmap_prbs.nw`, `mmap_spi.nw`, `spi_quad.nw`, `spi_simple.nw`, `spi_1lane_stream.nw`, optionally `spi.nw`/`qspi.nw`) must be deletable by a human reviewer when their milestone is fulfilled by `mission.nw`.

## Rules of engagement

Each step below is one self-contained task that must fit within a single agent context. After each step that lands a milestone, the agent commits the diffs, writes a one-line entry under "Done" at the bottom of this file, and explicitly lists which old chapters can be deleted. No step creates new exploratory chapters; every step either modifies firmware, modifies an existing chapter (preferring `qspi.nw` until Step 5 forks a new canonical), or migrates content into `mission.nw`.

## Step 1 — Honest BER measurement in firmware

Replace the `c` and `A` commands' `firsterr` early-exit with a true scan that counts ALL byte mismatches against the expected ramp pattern, records `total_errors`, `last_err_pos`, and a small fixed-size array of the first 64 error positions. Without this, every existing BER claim is bounded above by 100% (we only verify 0..firsterr−1). Validate by deliberately poisoning a buffer in DDR and confirming the count matches. No HDL changes; firmware-only. After this step, the existing `c`/`A` reports become trustworthy.

## Step 2 — Find the highest presc that gives BER=0 at 1 GiB on qspi.bin

Using the Step-1 firmware and the existing `qspi.bin` slave (untouched), sweep presc 15→3 with `c 1073741824 65536 9 107` per presc. Identify the highest presc (lowest SCLK) where `total_errors=0` over a full 1 GiB. Capture wall rate. This is today's true ground-truth ceiling — likely well below 400 Mbps. No HDL or chapter changes.

## Step 3 — Classify the failure mode at the first failing presc

At one presc step faster than the Step-2 ceiling, run 10 separate firmware boots, each capturing `total_errors` and the error-position array. Classify: (a) deterministic-per-boot positions with values that vary across boots → SI metastability (attack via Step 5/6); (b) deterministic-across-boots → master sampling timing (attack via Step 7); (c) random → likely cabling. Decision matrix recorded in this file.

## Step 4 — Slave HDL fix candidate A: registered IOB output in qspi.nw

Modify `src/qspi.nw`'s four quad-output `SB_IO` cells from `PIN_TYPE = 6'b101001` to `6'b100101` with `NEG_TRIGGER(1'b1)` and `OUTPUT_CLK(sclk)`, mirroring `src/spi.nw`'s 645 Mbps streaming pattern. Remove the now-redundant fabric `io_pad_out` register. Rebuild `qspi.bin`, re-run Step 2's full sweep. If the BER=0 ceiling moves up by ≥1 presc step, keep the change; otherwise revert. No new chapter — modify `qspi.nw` in place.

## Step 5 — Slave HDL fix candidate B: SB_GB_IO + settle gate in qspi.nw

If Step 4 didn't move the ceiling: in `src/qspi.nw`, promote `sclk` to a global clock net via `SB_GB_IO` AND add a one-`clk`-cycle "settled" qualifier that gates the `cmd_sr` shift-in arm so the FSM ignores any sclk edge arriving within 1 fclk cycle of `cs_async_rst` deasserting. Both pieces are needed together (the prior SB_GB-alone attempt caused MDMA timeout). Rebuild, re-run Step 2 sweep.

## Step 6 — Master timing tuning at the new ceiling

At one presc step faster than the post-Step-5 ceiling, sweep DLYB tap ∈ {0, 8, 16, 32, 48, 64, 96, 128} × sshift ∈ {0, 1} × dummy_cycles ∈ {8, 9, 10, 12} with 64 KiB reads. Find the combo giving `total_errors=0` at this presc. Record the winning combo in `firmware/cli.c` defaults so subsequent steps inherit it. Firmware-only changes.

## Step 7 — Demonstrate provisional mission target on `qspi.bin` + winning combo

Combine the post-Step-5 `qspi.nw` HDL with the post-Step-6 master settings and run `c 1073741824 65536 9 107`. Mission gate: `total_errors=0` AND wall rate ≥400 Mbps in a single run. If this passes, the channel itself is mission-capable; the remaining work is just consolidation.

## Step 8 — Fork the canonical `src/mission.nw` from `qspi.nw`

Create `src/mission.nw`. Copy ONLY the slave logic needed for the mission: the post-Step-5 cs-sync chain, the FSM that decodes opcode 0x6B and drives the address-derived ramp via the post-Step-4 IOB launch, and the four `SB_IO` cells. Drop everything else (other opcodes, SFDP, write/erase, JEDEC). Add the Makefile fragment, `mission.pcf`, and a TEST.md whose only block is the Step-7 mission run with the verifier asserting both `total_errors=0` and `mbps≥400`. Confirm `mission.bin` reproduces the Step-7 result bit-for-bit.

## Step 9 — Add slave-side end-to-end CRC32 to `mission.nw`

In `src/mission.nw`, add a 32-bit CRC accumulator that updates on every emitted byte during the data phase, plus a separate single-lane read opcode (e.g., 0x5A SFDP-style) that returns the current CRC32 value. Add a firmware command that issues 1 GiB of 0x6B reads, computes master CRC32 via the HW peripheral, then issues the slave-side CRC read and asserts equality. This closes the "trust the receiver-side check" gap — both sides must agree.

## Step 10 — Switch from address ramp to PRBS-15 in `mission.nw`

In `src/mission.nw`, replace the address-derived byte source with PRBS-15 (`x^15 + x^14 + 1`, seed `15'h7E5F`), advancing 4 bits per emitted nibble via the standard Galois recurrence. The slave-side CRC from Step 9 still works (CRC is data-agnostic). The firmware verifier no longer needs to know the expected pattern — it just compares the two CRC32 values. This satisfies the mission's "arbitrary data" requirement and removes the last dependency on the ramp pattern matching.

## Step 11 — Final mission run + cleanup

Run `mission.bin` with PRBS data and end-to-end CRC over 1 GiB at the Step-6 SCLK. Confirm `total_errors=0` (no expected-byte comparison anymore — just CRC equality), wall rate ≥400 Mbps, single run. Once green: delete `src/mmap_slave.nw`, `src/mmap_prbs.nw`, `src/mmap_spi.nw`, `src/spi_quad.nw`, `src/spi_simple.nw`, `src/spi_1lane_stream.nw` (and corresponding `verilog/*.v`, `verilog/*.pcf`, `build/*` dirs). Trim `src/qspi.nw` and `src/spi.nw` to whatever bring-up history is still load-bearing for the SFDP/flash-emulation use cases (or delete if not). Final repo state: one canonical `src/mission.nw` plus whatever non-QSPI chapters remain (`uart.nw`, `gpio.nw`, etc.).

## Done

(append one line per landed milestone here, format: `YYYY-MM-DD step N — outcome — chapters now deletable: <list>`)
