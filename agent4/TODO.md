# TODO: QSPI FPGA-to-MPU Fast Data Transfer

### Mission Target

Demonstrate bit-accurate sustained data transfer from FPGA to STM32MP135
MPU using the QUADSPI peripheral, **on the agent4 rig**:

- Single-lane path: at least 100 Mbps wall-rate. **ACHIEVED on the
  agent4 rig 2026-04-30**: `wall_rate=107.331 Mbps` at presc=5 sshift=1
  on a 32 MiB DDR ping-pong auto-consume stream
  (`A 33554432 0 1`, opcode-less `LANES=1` framed read through
  `stream_direct_crc_read` -> `qspi_mdma_crc_read`, hardware CRC1 +
  MDMA path), `firsterr=-1`, `crc32=310d8327` matches expected,
  `auto=on`, `chunk=16777216 chunks=2`. Ledger row
  `2026-04-30T19:28:17 spi_1lane_stream 5`. Block 5 of the new
  `src/spi_1lane_stream.nw` chapter (spi_1lane_stream FSM iter 1).
- Quad-lane requirement: at least 200 Mbps, ideally higher, with no
  data errors. **STILL OPEN**: quad-lane integrity preflight broke at
  byte 15 in spi_quad iter 1 (0x6B opcode, presc=203); iter 2
  diagnostic discrimination localized the bug to qspi.nw slave RTL on
  the 0x6B code path (0x6F nibble-ramp passes, 0x6B fails at the same
  byte boundary).

User mandate (CRITICAL): demonstrate >=100 Mbps 1-lane wall-rate on the
agent4 rig FIRST, before any further quad-lane work. NEVER stop until
both 1-lane >=100 Mbps AND quad-lane >=200 Mbps are demonstrated on this
actual rig. Insert tests/chapters/scopes BEFORE the failing block to
bypass it -- do not accept BLOCKED as final.

Mission status synthesis (2026-04-30): step 1 (1-lane >=100 Mbps)
COMPLETE. Step 2 (quad-lane >=200 Mbps) still OPEN -- spi_quad FSM
resumes at iter 3 with the iter-2 diagnostic discrimination evidence
in hand.

### DONE: spi_1lane_stream FSM iter 1 -- MISSION STEP 1 ACHIEVED

Status: DONE. 1/8 iteration budget consumed; 7 returned to pool. Single
WORK iteration on the brand-new `src/spi_1lane_stream.nw` chapter
landed all 5 blocks GREEN, including the mission-target
`Check 1lane stream @ presc=5 wall rate >= 100 Mbps`. User mandate
step 1 (1-lane >=100 Mbps wall-rate on the agent4 rig) is satisfied.

#### Mission-target evidence (verbatim from persistent log)

Block 5 (mission target), `2026-04-30T19:28:17`:
```
[5/5 PASS] Check 1lane stream @ presc=5 wall rate >= 100 Mbps
  (1lane stream @ presc=5 bytes=33554432 sclk=109.3MHz
  effective=109.3Mbps bench=2460ms crc32=310d8327 expect=310d8327
  chunk=16777216 chunks=2 buf=crc auto=on qspi_hz=656000000
  wall=2501ms wall_rate=107.331Mbps wall_rate_floor=100.000Mbps)
```

Wall-rate computation independently verified by Verifier:
`33,554,432 B x 8 / 2.501 s = 107.331 Mbps` -- matches reported value
exactly. firsterr=-1 (full pattern match), CRC matches expected,
auto-consume on, chunk shape (16 MiB x 2) as designed. Ledger row:
`2026-04-30T19:28:17 spi_1lane_stream 5`. Persistent log shows rc=0,
all 5 sentinels `n_errors=0 early_done=false`, all bench_start /
bench_done marks reconcile to reported wall rates exactly.

#### 5-block summary

1. `Check 1lane peripheral raw read at presc=203 returns
   1024-byte incrementing pattern` (preflight, `j 1024 0` at
   `p 203 0`) -- PASS.
2. `Check 1lane stream @ presc=203 pattern correct` (slow
   sanity, `A 1000000 0 1`) -- PASS, wall_rate ~3.09 Mbps.
3. `Check 1lane stream @ presc=63 pattern correct`
   (`A 2097152 0 1`) -- PASS, wall_rate ~10.04 Mbps.
4. `Check 1lane stream @ presc=5 pattern correct`
   (`A 16842752 0 1`, ping-pong DDR auto-consume,
   `p 5 1` sshift=1) -- PASS, wall_rate ~107 Mbps observed
   (this block is itself novel proof that 1-lane sample
   margin at ~83 MHz SCLK is clean over 16 MiB).
5. `Check 1lane stream @ presc=5 wall rate >= 100 Mbps`
   (`A 33554432 0 1`) -- PASS, **wall_rate=107.331 Mbps**
   vs floor 100.000 Mbps. **MISSION TARGET BLOCK.**

#### Cumulative project state after this iteration

- Mission step 1 (1-lane >=100 Mbps on agent4 rig): COMPLETE.
- Mission step 2 (quad-lane >=200 Mbps on agent4 rig): OPEN.
  spi_quad FSM iter 1 RED (creation + first preflight test
  showed byte-15 corruption on 0x6B). spi_quad FSM iter 2 RED
  (diagnostic blocks 0x6C/6D/6E/6F all PASS, 0x6B still fails
  at byte 15) -- the failure is now localized to the
  `quad_next_nibble`/`quad_data_byte_inc` cadence in
  qspi.nw slave RTL specific to opcode 0x6B.
- spi block 8 BLOCKED (1lane @ presc=15 pattern correct,
  ~21 MHz timing margin) remains -- but is NO LONGER on the
  critical path because spi_1lane_stream demonstrated
  100 Mbps via a different prescaler / different mechanism
  (presc=5 sshift=1 MDMA stream, no presc=15 dependency).
- spi_quad chapter (494 -> ~750 lines after iter 2 diagnostic
  insertions) is in working tree and ready for iter 3
  HDL-triage Manager.

#### Iter 1 rig reset evidence (planning Manager)

- Command: `cd /home/agent4/fast_data/fpga/build/uart && python3 -u
  $TEST_SERV/run_md.py --ledger /home/agent4/fast_data/agent4/ledger.txt
  --module uart --log /home/agent4/fast_data/agent4/log.txt`.
- Exit code: 0. Result: `1 BLOCK PASSED`, sub-checks 3/3 PASS.
  Sentinel `n_ops=10, n_errors=0, early_done=false`.
- New ledger row: `2026-04-30T19:17:01 uart 3`. Rig is up: yes.

#### Iter 1 budget

spi_1lane_stream: 1/8 consumed. 7 iterations remain unused (returned
to pool; the FSM is DONE because the mission-target block PASSED on
the first WORK iteration). No follow-up iteration is needed for this
FSM scope. The 512 MB block and the MDMA single-buffer wall-rate
variants were intentionally omitted from iter 1 (out of scope for
hitting the 100 Mbps threshold) and remain available as
discretionary follow-ups if the user wants additional confidence.

#### Files involved (Worker iter 1 actuals)

- NEW: `fpga/src/spi_1lane_stream.nw` (666 lines, 5 blocks).
- NEW (auto-tangled at build): `fpga/build/spi_1lane_stream/`
  tree -- TEST.md, verify.py, Makefile, spi_1lane_stream.mk,
  spi_1lane.bin symlink, flash.tsv symlink, main.stm32 symlink.
- UNCHANGED by this iteration: `fpga/src/spi.nw`,
  `fpga/src/spi_quad.nw`, `fpga/src/qspi.nw`, `fpga/Makefile`.

### Active FSM: spi_quad (RESUMED)

Status: PLANNING (iter 3, starting at 3/8 -- iter 1 RED + iter 2 RED
already burned 2/8 prior; 5 iterations remain). The iter-2 diagnostic
discrimination already proved the failure is localized to qspi.nw
slave RTL on the 0x6B code path; iter 3 begins with HDL triage.

The user mandate prohibition on quad-lane work (in effect during the
1-lane mission) has been LIFTED now that mission step 1 is
demonstrated. Per the user mandate, spi_quad FSM resumes immediately
to chase mission step 2 (>=200 Mbps quad-lane wall-rate on the
agent4 rig).

#### Iter 2 evidence summary (carried forward)

- Diagnostics 0x6C (`Y 32`, one-hot), 0x6D (`Z 32`, byte sequence),
  0x6E (`W 32`, nibble-hold), 0x6F (`U 32`, nibble-ramp) all PASS
  on the rig at presc=203.
- 0x6B preflight (`q 0 1024`) FAILS with structurally corrupted
  pattern starting at byte 15 -- the same byte boundary observed in
  iter 1.
- Decision-matrix conclusion (per TODO.md "Phase B" / "Phase C"
  in the spi_quad iter 2 record): the failure is unique to the
  `quad_data_byte_inc` cadence in qspi.nw 0x6B (since the
  diagnostic cadences 0x6C/6E/6F all pass). The 0x6F path uses the
  same SB_IO presenter and the same `negedge sclk` registration --
  yet only 0x6B breaks. Therefore the bug is in the 0x6B-specific
  state machine path: most likely in the byte-counter wrap or the
  nibble-mux fall-through case in the `quad_next_nibble` /
  `quad_data_byte_inc` arms of the `quad_data` state.

#### Iter 3 plan

Iter 3 is HDL triage. Manager (planning) reads
`fpga/src/qspi.nw` lines ~245-310 (the quad nibble emit cadence),
identifies the exact 0x6B code path that differs from the
working 0x6F path, and proposes a concrete HDL edit. Concretely:

- Open qspi.nw and locate the `quad_data` state's
  `quad_next_nibble` mux fall-through and the
  `quad_data_byte_inc` byte-counter advance.
- Compare the exact RTL paths feeding `quad_next_nibble`
  for `op=6B` vs `op=6F` (the 0x6F path passed; the 0x6B
  path fails).
- Hypothesize whether the byte-15 break is (a) a 4-bit
  counter wrap (0xF -> 0x10 transition not handled),
  (b) a nibble-mux fall-through at a state that 0x6B
  reaches but 0x6F does not, or (c) a one-cycle stall
  in the byte-increment path that misaligns the
  HI/LO nibble pairing across the 16-byte FIFO trigger.
- Propose ONE concrete RTL edit + an in-chapter
  diagnostic block (e.g., 0x6B short read at exactly
  16 bytes vs 17 bytes) that would discriminate the
  hypothesis.

NOTE: The prior iter 3 planning Manager was killed by the
user directive "do 1-lane FIRST". That triage work was
NEVER completed and is NOT in TODO.md. The iter 3 Manager
prompt SHOULD redo the HDL triage from scratch using the
iter 2 diagnostic evidence (which IS recorded above in the
spi_quad iter 2 section).

#### Iter 3 rig reset

NOT YET DONE. Iter 3 planning Manager runs the standard
`uart` rig reset before handing off to Worker, per
AGENTS.md. The rig was last reset at `2026-04-30T19:17:01
uart 3` (about 11 minutes before this DONE record was
written), but a fresh reset for the iter 3 FSM is still
required.

#### Iter 3 budget

spi_quad: 2/8 consumed prior, iter 3 starting => 3/8 after
iter 3. 5 iterations remain.

### Active FSM: spi_1lane_stream (NEW chapter, retired)

Status: PLANNING -> WORK iter 1/8. Fresh FSM run on a new chapter
`src/spi_1lane_stream.nw` that scopes the 1-lane stream blocks
(currently buried after the failing 1-lane @ presc=15 pattern-correct
block 8 in `src/spi.nw`) so they become reachable in isolation. This is
the path to the user's mandate: 1-lane >=100 Mbps wall-rate on the
agent4 rig.

(The full planning record is preserved verbatim below for
historical reference; the FSM is now DONE per the
"DONE: spi_1lane_stream FSM iter 1" record at the top of this file.)

#### Why a new chapter (mirrors spi_quad pattern)

`make test` aborts on the first failing block (no `--full`); blocks
past the first failure are NOT executed. The spi FSM hit BLOCKED at
block 8 (1lane @ presc=15 pattern correct, ~21 MHz SDR margin failure),
so blocks 9+ (which include `Check 1lane stream @ presc=5 wall rate >=
100 Mbps` at spi.nw:1496 -- the mission-target 1-lane test) have NEVER
been attempted on this rig.

The qspi/spi_quad FSMs already proved the chapter-scoping pattern:
parent Makefile auto-discovers `src/*.nw` (Makefile:1
`CHAPTERS := $(notdir $(basename $(wildcard src/*.nw)))`) and applies
CHAP_RULES (Makefile:43-86) to produce
`build/<ex>/{TEST.md,verify.py,Makefile,<ex>.mk}`. Adding
`src/spi_1lane_stream.nw` creates the `spi_1lane_stream` chapter with
no parent-Makefile changes.

#### Phase A -- 1-lane stream blocks in spi.nw (Manager survey)

Six 1-lane stream blocks exist in spi.nw, all unattempted on this rig:

1. `Check 1lane stream @ presc=203 pattern correct`
   (spi.nw:1360-1381, command `A 1000000 0 1`, 40 s timeout).
2. `Check 1lane stream @ presc=255 pattern correct`
   (spi.nw:1383-1404, command `A 1048576 0 1`, 20 s timeout).
3. `Check 1lane stream @ presc=63 pattern correct`
   (spi.nw:1406-1427, command `A 2097152 0 1`, 15 s timeout).
4. `Check 1lane stream @ presc=15 pattern correct`
   (spi.nw:1429-1450, command `A 1500000 0 1`, 12 s timeout, uses
   `p 15 1 1` -- sshift=1 + DLYB=1 from spi iter 5 working tree).
5. `Check 1lane stream @ presc=5 pattern correct`
   (spi.nw:1452-1473, command `A 16842752 0 1`, 15 s timeout, ping-pong
   DDR auto-consume, uses `p 5 1` -- sshift=1).
6. **`Check 1lane stream @ presc=5 wall rate >= 100 Mbps`**
   (spi.nw:1475-1496, command `A 33554432 0 1`, 15 s timeout, **the
   mission-target block**).
7. `Check 1lane stream @ presc=5 512 MB stream_xfer wall rate >=
   100 Mbps within 45 s, then pattern correct`
   (spi.nw:1498-1523, command `A 512000000 0 1`, 45 s timeout).

Plus 4 MDMA blocks at spi.nw:1776-1889:
- `Check 1lane single-buffer DDR MDMA @ presc=203/63/15/5 pattern
  correct` (4 blocks, command `m 1000000 0 1`).
- `Check 1lane single-buffer DDR MDMA @ presc=5 wall rate >= 100 Mbps`
  (spi.nw:1868-1889, command `m 1000000 0 1`, the MDMA mission-target
  variant).

The verify dispatch entries for all of the above are in spi.nw:2972-3000.

#### Phase A -- bench command mechanism difference

The 1-lane stream uses `A` (cmd_auto_stream, cli.c:1236), NOT `b`
(cmd_bench, cli.c:1003). Critical mechanism difference:

- `b 1048576 0 1` (block 8): single-shot `qspi_bench_read`
  (qspi.c:436), CPU polls QUADSPI->DR / drains FIFO byte-by-byte.
- `A 33554432 0 1` (mission-target stream): goes through the
  `stream_direct_crc_eligible(quad=0, raw=1) && auto_consume` path
  (cli.c:1272-1278) -> `stream_direct_crc_read` ->
  `qspi_mdma_crc_read` (qspi.c:790). Hardware MDMA + hardware CRC1
  drain through the DMA path; CPU never touches the FIFO data words.
  Throughput is bounded by the QUADSPI peripheral SCLK rate, not by
  CPU FIFO drain time.
- `m 1000000 0 1` (MDMA single-buffer): `cmd_mdma` ->
  `qspi_mdma_start` -> regular MDMA into DDR, then CPU validates
  pattern after DMA completes. Different from `A` (no ping-pong, no
  HW direct CRC); same QUADSPI sample logic.

Both `A` and `m` use the SAME QUADSPI peripheral with the SAME SSHIFT
and DLYB settings as `b`. The data-eye / sample-margin issue is a
property of the QUADSPI sample flop on the SCLK rising edge -- it
does NOT depend on whether CPU or MDMA drains the FIFO. So the
sample-margin failure that broke block 8 at presc=15 will affect
stream/MDMA at the same prescaler equally.

#### Phase A -- verify helpers (verbatim)

`check_stream_wall_rate_at_least` (spi.nw:2913-2932):
```python
def check_stream_wall_rate_at_least(mode, presc, min_mbps, byte_count=1000000,
                                    max_wall_ms=None, expected_chunk=None,
                                    min_chunks=None):
    if not check_stream_pattern(mode, presc, byte_count, max_wall_ms,
                                expected_chunk, min_chunks):
        return False
    m = _stream_pick(mode, byte_count, presc)
    rate = _stream_rate_text(mode, presc, m)
    _effective, wall = _stream_rates(m)
    if wall is None:
        sys.stderr.write(f"{rate}: wall_rate=unknown ...\n")
        return False
    if wall < min_mbps:
        sys.stderr.write(f"{rate}: wall_rate={wall:.3f}Mbps below ...\n")
        return False
    sys.stdout.write(rate + f" wall_rate_floor={min_mbps:.3f}Mbps\n")
    return True
```

`check_mdma_wall_rate_at_least` (spi.nw:2797-2838):
```python
def check_mdma_wall_rate_at_least(mode, presc, min_mbps):
    ... # same pattern: parses MDMA_RE, checks CRC + firsterr,
        # then compares wall_rate (computed from bench_start/done marks
        # via _bench_wall_ms divided into byte_count*8) to min_mbps.
```

Both helpers compute wall-rate from `bench_start`/`bench_done` marks
in the timeline (`_bench_wall_ms`, spi.nw:2480-2488) divided into
`byte_count * 8 / (wall_ms * 1000)` (`_wall_rate_mbps`,
spi.nw:2491-2494). The mission-target check parses the
`stream <bytes> B 1lane in <ms> ms, ...` summary line via
`STREAM_RE` (spi.nw:1935-1940) and the `stream_xfer <bytes> B`
sentinel (cli.c:178).

The `check_stream_pattern` precondition for the wall-rate helper does
several things: pattern-correctness (firsterr=-1), CRC32 match,
`auto-consume on`, `chunk` size match, `chunks` count >= min, and
optional `max_wall_ms`. So the wall-rate floor is gated on full
pattern correctness -- if presc=5 stream produces corrupted data,
the helper fails on CRC long before the wall-rate check runs.

#### Phase A -- 1-lane raw read at presc=5 PASSED on this rig

The block 4 of spi (`Check 1lane peripheral raw read at presc=5
returns 512-byte incrementing pattern`, spi.nw:1223-1240, command
`j 512 0` with `p 5 1`) PASSED in spi FSM iter 3 evidence. Mechanism:
`cmd_data_only_read` reads 512 bytes via the QUADSPI peripheral at
sshift=1, no opcode/addr framing. So at presc=5 with sshift=1, the
QUADSPI master DOES correctly sample the FPGA-driven SPI stream for
short (~512 B) transfers.

What's different at the stream block (presc=5, 33 MB):
- Length: 512 B vs 33 MB (65 000x more bytes -- if there's any
  per-byte error rate, it accumulates).
- Mechanism: CPU FIFO drain (`j` -> `cmd_data_only_read`) vs MDMA
  ping-pong DDR + HW CRC (`A` -> `stream_direct_crc_read`).
- Bench timing: `j` doesn't have bench_start/bench_done marks; `A`
  does (so we get a wall_rate readout we can floor-check).

The 1-lane @ presc=15 (block 8) FAILURE used `b 1048576 0 1` which
is the CPU-driven indirect read with raw=1. So the failure already
showed up at 1 MB CPU-drained. The stream test at the same presc=15
(stream block 4 above, spi.nw:1429-1450) would likely also fail at
1.5 MB.

#### Phase B -- risk assessment

The mission-target stream test (`A 33554432 0 1` at presc=5 sshift=1)
might pass on this rig, with MEDIUM-LOW confidence. Reasoning:

The 1-lane peripheral raw read PASSED at presc=5 sshift=1 over 512 B,
confirming the SCLK ~83 MHz sample point CAN land in the FPGA SB_IO
output flop's data eye for that prescaler/shift combination on this
rig. The block 8 failure was at presc=15 sshift=1 (~21 MHz) -- a
DIFFERENT data eye position because at lower SCLK the FPGA flop has
more time to settle but the master's sample edge is also further from
the FPGA edge. There is no monotone relationship between SCLK and
margin in real hardware: a presc that fails at 21 MHz can pass at 83
MHz if the eye lands in a different spot on the timing diagram.

Counter-argument: 33 MB at ~83 MHz is ~4 seconds of continuous SDR
sampling -- about 264 million sample edges. Even a 1e-9 per-bit error
rate gives ~0.25 errors per run, so any margin issue that's anywhere
near the eye will produce CRC mismatches. The 512 B raw-read sample
size (4096 bits) is far too small to detect a 1e-9 error rate.

Best estimate: presc=5 stream MAY pass. If it does, 100 Mbps wall-rate
is comfortably under the ~83 Mbps SCLK 1-lane physical max ... wait,
that's a problem. 1-lane SDR at SCLK = QSPI_KER_HZ / (presc+1) =
656 MHz / 6 = 109.3 MHz. So presc=5 1-lane physical max = ~109.3 Mbps
(SDR, 1 bit per cycle). 100 Mbps target is achievable at ~91% of
physical max -- the existing `STREAM_WALL_RATE_FLOOR=0.90` would just
barely allow this. If MDMA + DDR + CRC overhead drops the wall rate
below 100 Mbps, the test fails on the rate floor even if the data is
correct.

If the mission-target block fails (corruption OR rate floor):
- Insert variations BEFORE the failing block (per user mandate):
  sshift=0 vs sshift=1, DLYB tap sweep, MDMA single-buffer (`m`)
  variant, slower presc (presc=3 is faster but might still work at
  ~125 Mbps physical max).
- presc=3 doesn't match the existing test plan but would give 109
  Mbps physical max ... actually presc=3 = 656/4 = 164 MHz, much
  faster. 164 Mbps physical max. presc=2 = 218 Mbps physical max,
  presc=1 = 328 Mbps physical max. So if presc=5 passes pattern but
  fails rate, going to presc=3 or presc=2 is the next move.

NOTE: The existing block 4 of stream (`presc=15 pattern correct`,
spi.nw:1429-1450) uses `p 15 1 1` (sshift=1, DLYB=1) -- the iter 5
working-tree state that hung on `b`. If this stream variant ALSO
hangs (DLYB midrange tap fails sample-edge entirely), Worker should
revert that to `p 15 1` (sshift=1, no DLYB) before running. But
spi_1lane_stream chapter doesn't have to include the presc=15 block
at all (per user mandate: insert tests BEFORE the failing block).

#### Phase C -- chosen iter 1 step: Option (B) sweep chapter

Option chosen: **(B) Sweep chapter**, presc=203 + presc=63 + presc=5
pattern correct + presc=5 wall-rate. Justification:

- Option (A) single-block (just presc=5 wall-rate) gives one bit of
  evidence: pass or fail. Insufficient to discriminate "data
  corruption at all rates" from "wall-rate floor missed but pattern
  OK" from "MDMA timing race" from "auto-consume not engaging".
- Option (C) sweep + variations is too much for iter 1. Variations
  belong in iter 2 conditioned on iter 1 evidence (e.g., if presc=5
  pattern fails, iter 2 inserts sshift=0 variant; if rate floor is
  the only failure, iter 2 increases byte_count to amortize start-up
  cost).
- **(B)** gives 4 blocks of evidence per iteration: presc=203 (very
  slow, unambiguous control), presc=63 (proven-good ~10 MHz baseline
  from spi block 7), presc=5 pattern correct (cheaper than rate
  floor, isolates corruption from rate), presc=5 rate floor (the
  mission target). That's 4-fold discriminative power vs 1.

**Skip presc=15** in iter 1: the equivalent `b` test already failed
(block 8). Including it would risk aborting the regression before the
mission-target presc=5 block runs. Per user mandate, insert tests
BEFORE the failing block (so presc=5 runs first if at risk), and
exclude the known-failing prescaler entirely.

**Order matters**: TEST.md is executed top-to-bottom and aborts on
first fail. Order should put the mission-target block EARLY (so even
if a sweep below it fails for unrelated reasons, the mission target
still runs). But mission-target depends on 1-lane bitstream being
loaded and MP135 firmware being up. Proposed order:

1. Preflight: 1-lane bit-bang or peripheral raw read at presc=203
   (spi.nw:1186-1240; cheap, proves bitstream loaded).
2. Phase 1 -- 1lane stream at presc=203 pattern correct (slowest,
   most likely to pass; if even this fails, infrastructure broken).
3. Phase 1 -- 1lane stream at presc=63 pattern correct.
4. **Phase 1 -- 1lane stream at presc=5 pattern correct** (mission
   prerequisite).
5. **Phase 1 -- 1lane stream at presc=5 wall rate >= 100 Mbps**
   (mission target).

If iter 1 lands all 5 blocks green, mission step 1 (1-lane >=100
Mbps) is achieved; FSM moves to a follow-up that validates the
512 MB variant or pivots back to spi_quad for the 200 Mbps step.

Worker iter 1 creates `src/spi_1lane_stream.nw` with:
- `<<TEST.md>>=` chunk: 5 blocks copy-adapted from
  spi.nw:1186-1240 (preflight) and spi.nw:1360-1496 (4 stream
  blocks; SKIP presc=255 sweep, SKIP presc=15 sweep, SKIP 512 MB
  block).
- `<<verify.py>>=` chunk: copy-adapted from spi.nw verify.py
  (`STREAM_RE`, `_stream_pick`, `_stream_rates`, `_stream_rate_text`,
  `check_stream_pattern`, `check_stream_wall_rate_at_least`,
  `check_raw_read_pattern`, `_bench_wall_ms`, `_check_rates_with_clock`,
  helpers). Trim to JUST what the 5 blocks need; do NOT pull in
  bench/quad/MDMA/diagnostic helpers. DISPATCH has 5 entries.
- `<<Makefile>>=` chunk modeled on `src/spi_quad.nw:688-723`:
  bitstreams target depends on `spi_1lane.bin` (built by spi
  chapter), symlinks `spi_1lane.bin`, `flash.tsv`, `main.stm32`.
  `--module spi_1lane_stream`. `sim:` is no-op.
- `<<spi_1lane_stream.mk>>=` chunk for parent Makefile aggregate.
- Brief prose chapter intro (one paragraph): mission step 1, why a
  separate chapter, what's intentionally excluded.

#### Working tree recommendation

Leave the 5 uncommitted `src/spi.nw` edit groups in place AND leave
`src/spi_quad.nw` (750 lines, just had iter 2 land green per ledger
row `2026-04-30T19:02:44 spi_quad 4`). Rationale:

- Option (B) does NOT touch `src/spi.nw` at all. The
  `spi_1lane_stream` chapter is fully self-contained.
- Reverting iter 5's `p 15 1 1 -> p 15 1` edits would conflate
  spi_1lane_stream-iter-1 noise with spi-FSM cleanup, violating the
  per-`<ex>` commit-scope rule.
- Worker SHOULD use the `delay ms=1500` after every `bench_mcu:reset_dut`
  pattern (proven helpful in iter 2 of spi -- prevents DFU race) when
  copy-adapting blocks into the new chapter.

#### Files involved (Worker iter 1)

- NEW: `fpga/src/spi_1lane_stream.nw` (single new file).
- NEW (auto-tangled at build): `fpga/build/spi_1lane_stream/` tree --
  TEST.md, verify.py, Makefile, spi_1lane_stream.mk, spi_1lane.bin
  symlink, flash.tsv symlink, main.stm32 symlink.
- UNCHANGED: `fpga/src/spi.nw`, `fpga/src/spi_quad.nw`,
  `fpga/src/qspi.nw`, `fpga/Makefile`.

#### Blast radius

Small. Worst case the tangle pattern is wrong and `make -C
build/spi_1lane_stream all` fails -- caught locally by Worker
before the regression run. The bitstream itself (spi_1lane.bin) is
built clean by the spi chapter and is unchanged from spi-FSM
working-tree state.

The regression run is:
```
cd /home/agent4/fast_data/fpga
make -C build/spi_1lane_stream all
make -C build/spi_1lane_stream bitstreams
cd build/spi_1lane_stream
python3 -u $TEST_SERV/run_md.py \
  --ledger /home/agent4/fast_data/agent4/ledger.txt \
  --module spi_1lane_stream \
  --log /home/agent4/fast_data/agent4/log.txt
```

#### Open questions / risks for Worker

- The MDMA + HW direct CRC path (`stream_direct_crc_eligible(0, 1) &&
  crc32_hw_begin_direct()`) is the CRITICAL stream code path. Make
  sure `auto_consume` is on (`a 1\r` before the `A` command, and the
  `auto=on` field shows up in the stream summary line) -- otherwise
  the slower fallback path runs and the wall-rate floor will likely
  fail.
- The `_stream_pick(mode, byte_count, presc)` helper requires the
  stream summary line to include `auto=on`; if firmware emits
  `auto=off` the helper still picks but `check_stream_pattern`
  fails on the `auto-consume is not on` check
  (spi.nw:2894-2896).
- The mission-target `check_stream_wall_rate_at_least("1lane", 5,
  100.0, 33554432, expected_chunk=16777216, min_chunks=2)` requires
  `chunk=16777216` and `chunks>=2`. The 33 MB transfer with
  STREAM_CHUNK_BYTES=16 MiB yields exactly 2 chunks (16777216 +
  16777216 = 33554432). Don't change byte_count from 33 MB or the
  chunk shape will mismatch.
- Verify.py needs `_check_rates_with_clock`,
  `_check_physical_floor`, `_check_physical_ceiling`,
  `_physical_max_mbps`, `STREAM_EFFECTIVE_RATE_FLOOR`,
  `STREAM_WALL_RATE_FLOOR` -- copy these too.
- The `_stream_rate_text` calls `_sclk_mhz(presc)` which uses
  `QSPI_KER_HZ = 656_000_000`. Copy this constant verbatim.
- `lib/verify_lib` is shared via `sys.path.insert(0, ...)` (see
  spi_quad.nw verify.py line 268-270). Reuse that pattern.
- Iter 1 evidence to collect:
  - Block 1 (preflight) pass = bitstream loaded OK.
  - Block 2 (presc=203 pattern) pass = 1lane stream path works at
    very low rate.
  - Block 3 (presc=63 pattern) pass = 1lane stream path works at
    ~10 MHz (analogous to spi block 7 which already PASSED).
  - Block 4 (presc=5 pattern) pass = 1lane sample margin OK at
    ~83 MHz with sshift=1; this is itself novel evidence on this
    rig.
  - Block 5 (presc=5 wall-rate floor) pass = MISSION STEP 1
    ACHIEVED.
- Most likely failure mode: block 4 or 5 corrupts at presc=5 or
  rate-floors below 100 Mbps. Iter 2 then inserts sshift=0 and/or
  presc=3/2/1 sweep to find a working combination.

#### Iter 1 rig reset evidence (planning Manager)

- Command: `cd /home/agent4/fast_data/fpga/build/uart && python3 -u
  $TEST_SERV/run_md.py --ledger /home/agent4/fast_data/agent4/ledger.txt
  --module uart --log /home/agent4/fast_data/agent4/log.txt`.
- Exit code: 0.
- Result: `1 BLOCK PASSED`, sub-checks 3/3 PASS:
  `[1/3 PASS] Check test_serv had no errors`,
  `[2/3 PASS] Check heartbeat banner present (3 banner hits)`,
  `[3/3 PASS] Check echo loop returned the probe bytes (2/2 probes
  echoed)`. Sentinel `n_ops=10, n_errors=0, early_done=false`.
- New ledger row: `2026-04-30T19:17:01 uart 3`.
- Rig is up: yes.

#### Iteration budget

spi_1lane_stream: 1/8 starting (this iteration is the first WORK
iteration). After Worker reports a green regression on the 5-block
TEST.md, Verifier runs. If green and the 100 Mbps wall-rate check
passes, mission step 1 is achieved and the FSM can either declare
DONE for spi_1lane_stream and pivot to spi_quad for step 2, or run
a follow-up iteration that validates the 512 MB block and the MDMA
single-buffer variant for additional evidence.

### BLOCKED: spi block 8 (1lane @ presc=15 pattern correct)

Status: BLOCKED per AGENTS.md "3 same-issue reds" rule. spi FSM
stopped after iter 5. Source NOT committed. Working tree carries
5 uncommitted edit groups in `src/spi.nw` (see "Working tree
state" below). This BLOCKED entry is recorded uncommitted; do
not commit unless the user explicitly requests a blocker-only
commit.

#### The blocker

Block 8 (`Check 1lane @ presc=15 pattern correct`, ~21 MHz SCLK
at MP135 QUADSPI kernel/(presc+1)) failed in three consecutive
iterations with three distinct symptom variants, exhausting the
same-issue retry cap:

- Iter 3 (sshift=0, dlyb=0): timeout waiting for `, firsterr=-1`
  on the bench output; bench finished but pattern was wrong; got
  `... 20 41 83 88 14 41 46 0c ...`.
- Iter 4 (sshift=1, dlyb=0, via `p 15 1\r`): firmware confirmed
  `presc=15 sshift=1 dlyb=0 unit=0`. Bench finished but reported
  `firsterr=2`, `crc32=bf364bed expect=04d0e435`, got
  `00 01 04 0c 20 61 83 88 14 61 c6 0e 38 79 02 4a` -- a
  *different* corruption pattern from iter 3, proving the failure
  is non-deterministic timing margin, not a deterministic HDL or
  protocol bug.
- Iter 5 (sshift=1, dlyb=1 @ unit=0x7F, via `p 15 1 1\r`):
  firmware confirmed `dlyb=1 unit=127`. Bench enters `poll_enter`
  and never returns within the 8000 ms timeout -- DLYB at the
  default midrange tap wedges the QUADSPI sample logic entirely.

#### Cumulative achievements (blocks 1-7 confirmed PASS)

All blocks 1 through 7 produce valid byte patterns and CRCs that
match the expected `crc32=04d0e435` over a 1 MB transfer:

1. GPIO header wiring preflight (iter 3 fix: 22 G samples at
   900 ms spacing + verify.py `check_gpio_wiring` collapsed
   subsequence)
2. 1lane bit-bang read
3. 1lane peripheral raw 1024 B
4. 1lane peripheral raw presc=5 512 B (`j 512 0`)
5. MP135 128 KiB XOR timing
6. 1lane @ presc=203 pattern correct (~3.09 Mbps wall rate)
7. 1lane @ presc=63 pattern correct (~3.79 Mbps wall rate)

So presc=63 (~10 MHz) and presc=203 (~3 MHz) sample cleanly with
generous margin, and presc=5 (~83 MHz) passes on a 512 B raw
read because it finishes before sample-window drift accumulates.
The sole failure is the 1 MB integrity benchmark at presc=15
(~21 MHz).

#### Best-known root cause hypothesis

The MP135 QUADSPI master samples within the FPGA SB_IO output
flop's metastable / setup-hold window at ~21 MHz SDR. The
margin is at the edge: lower frequencies pass, the exact
corrupted bit positions vary run to run, and naive DLYB
engagement at the midrange tap tips the sample point off the
data eye in the other direction (hang). This is consistent with
a real analog timing-margin failure on the FPGA→MP135 path at
~21 MHz, not a protocol or HDL counter bug.

#### Open paths for future work (out of FSM scope)

- DLYB tap calibration in MP135 firmware: sweep `unit` from 0
  to 127 with `dlyb_sel=1`, run a short integrity check at each
  tap, and record the working window. Requires firmware changes
  outside `src/spi.nw` (cli.c / qspi.c::setup_dlyb in the MP135
  source tree).
- FPGA SB_IO output-flop timing review for the QUADSPI slave
  data lanes -- possible in `src/spi.nw` but high risk and would
  also touch the LANES=4 path the mission depends on.
- Lower the MP135 QUADSPI clock at this prescaler -- defeats
  the purpose of the test.
- Mission pivot: the mission target (>=200 Mbps quad-lane) is
  in `qspi.nw`, not `spi.nw`. spi block 8 is a 1-lane integrity
  baseline at ~21 Mbps; it is not on the critical path to the
  mission. A fresh FSM run on qspi.nw is unblocked by this
  spi BLOCKED state.

#### Working tree state (uncommitted, in `git diff src/spi.nw`)

1. Iter 2: 31 x `delay ms=1500` after `bench_mcu:reset_dut`
   (cleared the DFU enumeration race; helpful, keep).
2. Iter 3: block 1 GPIO walk -- 22 G samples at 900 ms spacing
   plus verify.py `check_gpio_wiring` run-length-collapsed
   subsequence (block 1 PASSES; helpful, keep).
3. Iter 4: 4 x `p 15\r` -> `p 15 1\r` (sites at lines 1329,
   1438, 1691, 1831) and 1 x bare `p 5\r` -> `p 5 1\r` to force
   sshift=1 (partially helpful; sshift=1 is now in effect at
   presc=15).
4. Iter 5: 4 x `p 15 1\r` -> `p 15 1 1\r` to enable DLYB at the
   default tap (unit=0x7F). This change converted block 8 from
   a CRC-mismatch failure into a transfer hang and is the
   worst of the three symptoms.

Recommended cleanup before any future work on this tree:
revert iter 5's DLYB enable (revert `p 15 1 1\r` back to
`p 15 1\r` at the 4 sites) so the working tree sits at the
"least bad" partial -- sshift=1 with no DLYB. Iter 4's
behaviour (CRC mismatch on block 8, blocks 1-7 PASS) is more
informative than iter 5's hang for any future tap-calibration
work.

#### Mission status

Mission target (`>=200 Mbps quad-lane FPGA->MP135 QUADSPI`) is
NOT blocked by this. The mission lives in `qspi.nw`, which has
its own bitstream (built clean as a side effect of
`make -C build/spi bitstream`), its own TEST.md, and its own
verify.py. The recommended next FSM action is a fresh
Orchestrator run on `ex=qspi`.

Iteration budget on spi: 5/8 consumed, but per AGENTS.md the
3 same-issue reds on block 8 (iters 3, 4, 5) trigger BLOCKED
and stop the loop on spi regardless of remaining iterations.

### DONE: qspi FSM iter 1 (1/8 budget consumed)

Status: DONE. The qspi FSM run terminates here, after a single
green WORK(evidence-only) iteration. This is a per-FSM scoping
decision by the review Manager, not a mission completion: the
qspi chapter's automated test plan is intrinsically trivial
(program-only) and cannot make further mission progress under
the `<ex>=qspi` scope without dragging unrelated MP135 host
infrastructure into `src/qspi.nw`.

#### What iter 1 proved

- The `qspi.bin` bitstream rebuilds cleanly and programs onto
  the iCEstick on the agent4 rig (`fpga:program bin=@qspi.bin`,
  `n_ops=1, n_errors=0, early_done=false` per
  `2026-04-30T18:24:10` sentinel block).
- The qspi build path through `make -C build/qspi all` is
  intact; qspi.nw was NOT modified by the worker.
- Ledger row `2026-04-30T18:24:16 qspi 1` recorded; persistent
  log shows rc=0 and `1 BLOCK PASSED`.

#### What iter 1 did NOT prove (mission gap)

- No QSPI traffic was driven over the wire (the FT4222 master
  is wired to the SHARC carrier QSPI header, not the iCEstick;
  the chapter documents this at qspi.nw:2744-2747).
- No 4-lane sweep, no quad-mode commands, no MP135 host
  integration, no wall-rate measurement.
- The mission target (>=200 Mbps quad-lane FPGA->MP135) was
  not advanced by this iteration. Mission progress signal:
  ~zero.

#### Why end the qspi FSM here (review Manager decision)

The Manager evaluated four options:

- (A) DONE for qspi, fresh FSM elsewhere -- chosen.
- (B) Continue qspi FSM by adding bench_mcu / MP135 / dfu /
  flash.tsv / main.stm32 plumbing to `src/qspi.nw` so qspi
  could drive its own quad-lane wall-rate test. Rejected:
  duplicates infrastructure that already lives end-to-end in
  `src/spi.nw`, large blast radius, very likely to consume the
  remaining 7-iter budget on infra setup before any wall-rate
  measurement.
- (C) Continue qspi FSM by editing `src/spi.nw` to extract the
  4-lane sweep blocks into a new module name. Rejected:
  AGENTS.md "Commit only files relevant to `<ex>`" makes the
  qspi FSM editing spi.nw cross-cutting and awkward to commit.
  The right scope for that edit is a fresh FSM whose `<ex>`
  matches the file-under-edit.
- (D) -- no better option proposed.

Choosing (A) preserves AGENTS.md commit-scoping discipline and
hands the next FSM a clean slate aimed at the mission.

#### Recommended next FSM (for the user / parent Orchestrator)

Spawn a fresh FSM with `<ex>=spi_quad` (a new sibling chapter
to be created, or a new test scope tangled out of `src/spi.nw`
if that's lower-friction). Goals for that FSM:

1. Make the existing 4-lane sweep blocks
   (`src/spi.nw` lines ~1639-1721, `Phase 2 -- 4-lane sweep at
   presc=N` for N in {203, 63, 15, 5}) reachable without the
   1-lane @ presc=15 block (block 8) aborting the regression.
   Mechanism: emit them under a separate module name so
   `run_md.py --module spi_quad` runs them in isolation. The
   spi.nw test runner already builds `qspi.bin` as part of its
   `bitstreams` target, so the bitstream is already available.
2. Once the 4-lane sweeps run cleanly on the agent4 rig, add a
   wall-rate bullet to one or more of those blocks (the
   existing `bench_done - bench_start` mark interval over the
   1 MiB payload gives Mbps directly; verify_lib likely needs
   a `check_wall_rate_at_least` helper, or extend the existing
   bench-result parser).
3. Demonstrate the >=200 Mbps quad-lane mission target on at
   least one presc setting (likely presc=5 ~83 MHz SCLK at
   LANES=4, theoretical ceiling well above 200 Mbps).

Risks for the next FSM:
- The 4-lane sweep blocks have NEVER been observed to pass on
  the agent4 rig today (the spi FSM block 8 fail at iter 3
  aborts the regression before block 9+ ever runs). They may
  hit the same ~21 MHz timing-margin failure mode at
  presc=15 that block 8 hit, OR they may pass cleanly because
  the 4-lane SDR sample point lands differently. Empirical.
- The spi.nw working tree carries 5 uncommitted edit groups
  (see "Working tree state" above). A fresh FSM should decide
  whether to inherit those or revert (recommended: keep iter
  2's `delay ms=1500` and iter 3's GPIO walk; revert iter 4's
  `p 15 1` and iter 5's `p 15 1 1` since the new module
  scope avoids block 8 entirely).

#### Commit recommendation for this iteration

The qspi FSM iter 1 made NO source edits (`src/qspi.nw`
unchanged in the working tree). The only changed file from
this iteration is `agent4/TODO.md` (this update) and the
agent4 ledger/log artifacts which are non-source records.

Recommended commit (Orchestrator should run this; review
Manager does not commit):

- Files: `agent4/TODO.md`, `agent4/ledger.txt`, `agent4/log.txt`,
  and possibly `agent4/AGENTS.md` if it was migrated from
  agent2 paths this session.
- Suggested message: `qspi: record FSM iter 1 green baseline,
  end FSM scope`.
- Do NOT commit `fpga/src/spi.nw` -- it carries unrelated
  uncommitted edits from the prior spi FSM and is not relevant
  to `<ex>=qspi`.
- Do NOT commit the `fpga` submodule pointer bump unless
  there's a substantive submodule change (there isn't from
  this iteration -- the `M fpga` in `git status` is only the
  uncommitted spi.nw edits, which we are explicitly NOT
  committing here).

Iter 1 rig reset evidence (planning Manager):
- Command: `python3 -u $TEST_SERV/run_md.py --ledger
  /home/agent4/fast_data/agent4/ledger.txt --module uart
  --log /home/agent4/fast_data/agent4/log.txt` from
  `/home/agent4/fast_data/fpga/build/uart`.
- Result: 1 BLOCK PASSED, 3/3 sub-checks PASS. New ledger
  row: `2026-04-30T18:16:47 uart 3`.

Iter 1 worker evidence (verified):
- Ledger row: `2026-04-30T18:24:16 qspi 1`.
- Persistent log: rc=0, `1 BLOCK PASSED`, sentinel
  `n_ops=1, n_errors=0, early_done=false`.
- Source diff to `src/qspi.nw`: none.

### spi_quad FSM iter 1 (1/8 budget consumed)

Status: PLANNING -> WORK. Fresh FSM run. New `<ex>=spi_quad`
chapter to be created so the existing 4-lane sweep blocks
(currently buried after the failing 1-lane block 8 in
`src/spi.nw`) become reachable in isolation. Mission target
remains `>=200 Mbps quad-lane FPGA->MP135 QUADSPI no errors`.

#### Strategic choice: option (alpha) -- new `src/spi_quad.nw`

Citations:
- `fpga/Makefile:1` `CHAPTERS := $(notdir $(basename
  $(wildcard src/*.nw)))` auto-discovers chapters from
  `src/*.nw`. Adding `src/spi_quad.nw` creates the
  `spi_quad` chapter with no parent-Makefile changes.
- `fpga/Makefile:43-84` `CHAP_RULES` then provides
  `build/spi_quad/{TEST.md,verify.py,Makefile,spi_quad.mk}`
  tangle rules and the standard `.json -> .asc -> .bin`
  pipeline. Per-chapter `.mk` (line 51, included at line
  118) lets spi_quad's own Makefile fragment append to
  `bitstream` / `sim` / `formal` aggregates if needed.
- `fpga/src/spi.nw:1639-1721` 4-lane sweep blocks already
  use `fpga:program bin=@qspi.bin` and
  `b 1048576 1 0` -- they need only the qspi.bin staged
  artifact, no spi-specific bitstream. The new chapter's
  Makefile can reuse the same `bitstreams` / `stage`
  pattern from `spi.nw:3041-3074` to symlink qspi.bin,
  flash.tsv, main.stm32 into `build/spi_quad/`.
- `test_serv/run_md.py:280-315` `--module` is purely a
  ledger label, not a TEST.md selector -- so option (beta)
  (single source, dual TEST.md) would require a custom
  Makefile-level second-tangle hack writing two distinct
  build-dir TEST.md files from one .nw. That breaks the
  one-chapter-one-build-dir convention and AGENTS.md
  "Commit only files relevant to `<ex>`" scoping.

Option (alpha) gives us: clean per-`<ex>` commit scope,
zero touch to `src/spi.nw`, zero touch to the parent
Makefile, free auto-discovery, and the working tree's 5
uncommitted spi.nw edits stay untouched and unblock the
new module entirely.

#### 4-lane structure summary (in current `src/spi.nw`)

- 4 phase-2 4-lane sweep blocks at lines 1639-1721,
  presc in {203, 63, 15, 5}, all `b 1048576 1 0` (quad,
  raw=0 -> opcode 0x6B with 8-cycle dummy).
- Each block already has `mark tag=bench_start` and
  `mark tag=bench_done` bracketing the bench command,
  ready to feed `_bench_wall_ms` (verify.py:2480-2488).
- Verify checks present today are pattern-only:
  `Check quad @ presc={203,63,15,5} pattern correct` ->
  `check_pattern("quad", presc)` (spi.nw:3013-3016 +
  2720-2757). No wall-rate check exists for quad yet.
- 1lane wall-rate template exists at spi.nw:1496 +
  2992-2995 (`check_stream_wall_rate_at_least`) and at
  2977-2978 (`check_mdma_wall_rate_at_least`). The bench
  variant (`b ... 1 0`) wall-rate check would parse the
  `BENCH_RE` line (spi.nw:1923-1927) and compare
  `_bench_rate_text`'s `wall_rate` to a floor.
- Preflight `Check quad peripheral read returns 1024-byte
  incrementing pattern` at spi.nw:1611-1637 is a useful
  smoke test for the new chapter to include first.

#### Bench `b` quad variant (cli.c)

`stm32mp135_test_board/baremetal/qspi/src/cli.c:1003-1062`
`cmd_bench(len, quad, raw)`:
- `b 1048576 1 0` -> opcode 0x6B, QSPI_LINES_4, 8-cycle
  dummy (quad output read mode).
- `b 1048576 1 1` -> opcode 0x6B, QSPI_LINES_4, 0 dummy
  (quad raw, no command framing).
- The summary line `bench %lu B quad @ presc=%lu in %lu
  ms, ... firsterr=%ld` (cli.c:1044-1061) is exactly the
  `BENCH_RE` shape verify.py expects.

So the existing 4-lane sweep blocks ARE wired through a
working bench command, and the existing verify.py
machinery would parse the result correctly if we tangled
those blocks (and the dispatch entries) into a new
spi_quad TEST.md / verify.py.

#### Working tree recommendation

Leave the 5 uncommitted `src/spi.nw` edit groups in place
for this iteration. Rationale:
- Option (alpha) does not touch `src/spi.nw` at all, so
  the uncommitted edits cannot affect the spi_quad build
  or test.
- Reverting iter 4 / iter 5 now would conflate
  spi_quad-iter-1 noise with spi-FSM cleanup, violating
  the per-`<ex>` commit-scope rule.
- A future spi-FSM resume (or explicit user request)
  should decide whether to revert iter 5's `p 15 1 1` ->
  `p 15 1` rollback. Out of spi_quad scope.

#### Iter 1 step: WORK

Worker creates `src/spi_quad.nw` containing:

1. Brief prose chapter intro (one paragraph): "This
   chapter scopes the 4-lane sweep tests so they run
   independently of the 1-lane @ presc=15 block which
   is currently a margin failure in `src/spi.nw`. The
   bitstream is `qspi.bin`, built by the spi chapter as
   a side effect."
2. `<<TEST.md>>=` chunk with these blocks (copy-adapted
   from `src/spi.nw`):
   a. `Preflight -- quad peripheral framed read returns
      the SPI stream` (spi.nw:1611-1637, presc=203,
      `q 0 1024` smoke test). Cheapest sanity check
      that proves the qspi.bin is loaded and that the
      4-lane data-phase reaches the MP135.
   b. `Phase 2 -- 4-lane sweep at presc=203` (well
      below the timing margin; expect PASS).
   c. `Phase 2 -- 4-lane sweep at presc=63` (~10 MHz
      effective, expect PASS by analogy with 1-lane).
   d. `Phase 2 -- 4-lane sweep at presc=5` (~83 MHz
      SCLK x 4 lanes = ~330 Mbps physical max; this is
      the mission-target block).
   Skip `presc=15` initially -- it is the most likely
   to hit the same margin failure that broke spi block
   8, and we want clean evidence at presc=5 first.
3. `<<verify.py>>=` chunk with a minimal dispatch:
   - `Check quad peripheral read returns 1024-byte
     incrementing pattern` -> reuse the
     `check_raw_read_pattern("quad", 1024)` shape (or
     a copy-paste minimal version that doesn't depend
     on lib code we haven't ported).
   - `Check quad @ presc={203,63,5} pattern correct`
     -> `check_pattern("quad", presc)` shape.
   - **NEW** `Check quad @ presc=5 wall rate >=
     200 Mbps` -> new helper
     `check_bench_wall_rate_at_least("quad", 5, 200.0,
     1048576)` parsing `BENCH_RE` and comparing
     `_wall_rate_mbps(byte_count, _bench_wall_ms())`
     to `200.0`. This is the mission-target check.
4. `<<Makefile>>=` chunk modeled on
   `src/spi.nw:3041-3073` but with `--module spi_quad`,
   and a `bitstreams` target that just depends on
   `build/spi/qspi.bin` (delegate to the parent
   Makefile via `$(MAKE) -C ../.. build/spi/qspi.bin`)
   plus symlinks for `flash.tsv`, `main.stm32`, and
   `qspi.bin` into `build/spi_quad/`.
5. No verilog/PCF/sim chunks needed -- this chapter
   reuses the qspi bitstream and adds zero RTL.
   `bitstream` aggregate gets nothing from spi_quad.

#### Files involved (Worker iter 1)

- NEW: `fpga/src/spi_quad.nw` (single new file).
- NEW (auto-tangled at build): `fpga/build/spi_quad/`
  tree -- TEST.md, verify.py, Makefile, qspi.bin
  symlink, flash.tsv symlink, main.stm32 symlink.
- UNCHANGED: `fpga/src/spi.nw` (5 prior edit groups
  remain uncommitted in working tree but irrelevant).
- UNCHANGED: `fpga/src/qspi.nw`.
- UNCHANGED: `fpga/Makefile` (auto-discovery handles
  the new chapter).

#### Blast radius

Small. Worst case, the tangle pattern is wrong and
`make -C build/spi_quad all` fails -- caught locally
by Worker before regression run. The bitstream itself
(qspi.bin) is unchanged from the qspi FSM's verified
build, so there is no FPGA-side regression risk.

The regression run is:
```
cd /home/agent4/fast_data/fpga
make -C build/spi_quad all     # tangle TEST.md, verify.py, Makefile, symlinks
make -C build/spi_quad bitstreams  # delegates to spi/qspi.bin build
cd build/spi_quad
python3 -u $TEST_SERV/run_md.py \
  --ledger /home/agent4/fast_data/agent4/ledger.txt \
  --module spi_quad \
  --log /home/agent4/fast_data/agent4/log.txt
```

Sim is not applicable for spi_quad (no new RTL); skip
`make sim` for this chapter, or have its sim aggregate
be an empty no-op.

#### Open questions / risks for Worker

- The 4-lane sweep blocks have NEVER run on the
  agent4 rig today. Possible failure modes at
  presc=5: (1) data-eye margin failure analogous to
  spi block 8 at presc=15 (but at higher SCLK and on
  4 lanes simultaneously); (2) a benign issue like a
  missing `delay ms=300` after `p 5 1\r`; (3) the
  bench command times out because the prescaler set
  fails silently.
- presc=5 (83 MHz SCLK) is at the upper edge of the
  iCE40 SB_IO timing -- if it fails, fall back to
  presc=15 (~21 MHz x 4 = 84 Mbps physical) or
  presc=7 (~41 MHz x 4 = 164 Mbps physical, just
  under the 200 Mbps target). Mission target may
  require presc=5 to actually pass.
- The verify-side `check_pattern` from spi.nw uses
  `_bench_pick(mode, presc, bytes=None)` and
  `BENCH_RE` -- these have to be copied verbatim
  into spi_quad's verify.py (or extracted into the
  shared `verify_lib`). Worker should COPY rather
  than refactor for iter 1 (smaller diff, no risk
  to spi.nw).
- The wall-rate check requires a `bench_done` mark
  to fire AFTER the bench summary line is printed,
  not before. Inspect the existing 4-lane block at
  spi.nw:1651-1654 -- the mark fires on
  `mp135:uart_expect sentinel=", firsterr=-1"` which
  is the LAST field of the summary line, so the
  mark interval is well-defined.

#### Iter 1 rig reset evidence (planning Manager)

- Command:
  `cd /home/agent4/fast_data/fpga/build/uart && python3
  -u $TEST_SERV/run_md.py --ledger
  /home/agent4/fast_data/agent4/ledger.txt --module uart
  --log /home/agent4/fast_data/agent4/log.txt`.
- Exit code: 0.
- Result: `1 BLOCK PASSED`, sub-checks 3/3 PASS:
  `[1/3 PASS] Check test_serv had no errors`,
  `[2/3 PASS] Check heartbeat banner present (3
  banner hits)`, `[3/3 PASS] Check echo loop returned
  the probe bytes (2/2 probes echoed)`. Sentinel
  `n_ops=10, n_errors=0, early_done=false`.
- New ledger row: `2026-04-30T18:36:24 uart 3`.
- Rig is up: yes.

#### Iteration budget

spi_quad: 1/8 starting (this iteration is the first
WORK iteration). After Worker reports a green
regression on the 4-block spi_quad TEST.md, Verifier
runs. If green and the 200 Mbps wall-rate check
passes, the FSM can declare DONE in iter 2. If
presc=5 fails the wall rate or the pattern, iter 2
falls back to presc=7 or adds a wall-rate-only check
without the strict pattern-correct prerequisite.

### spi_quad FSM iter 2 (2/8 budget consumed)

Status: PLANNING -> WORK. Iter 1 built `src/spi_quad.nw`
(494 lines, 4 blocks: preflight + presc=203/63/5) cleanly,
tangled and built. Block 1 preflight (`q 0 1024` at
presc=203 sshift=1) FAILED on the rig with a structurally
corrupted pattern; blocks 2-4 not attempted (regression
aborts on first failure).

Note on procedural noise: iter-1 Worker ran `run_md.py`
twice (identical RED both times). Two ledger rows
`2026-04-30T18:44:44 spi_quad 0` and
`2026-04-30T18:44:59 spi_quad 0`. Append-only ledger,
not "fixed".

#### Iter 1 failure (verbatim from log)

Sentinel: `n_ops=12, n_errors=0` -- infrastructure is
healthy: FPGA programmed, MP135 booted, `q 0 1024`
issued, `op=6b read 1024 @ 0x00000000` sentinel hit.
The read did NOT short-circuit at qspi_xfer; the data
came back but corrupted.

Verifier: `quad raw short capture: got 825 bytes,
expected 1024`. The 825-byte short capture is a side
effect of the verify.py `_bytes_after` parser stopping
at the first non-hexdump line. The MP135 `cmd_quad_read`
returned all 1024 bytes; verify.py just stopped scanning
once it saw the next prompt or other UART chatter. So
"825" is parser truncation, NOT slave under-run.

Got pattern (first 256 bytes, 16 per row):
```
00 10 20 30 40 50 60 70 80 90 a0 b0 c0 d0 e0 10
11 12 13 14 15 16 17 18 19 1a 1b 1c 1d 1e 1f 20
21 22 23 24 25 26 27 28 29 2a 2b 2c 2d 2e 2f 30
...
e1 e2 e3 e4 e5 e6 e7 e8 e9 ea eb ec ed ee ef f0
1f 2f 3f 4f 5f 6f 7f 8f 9f af bf cf df ef f0 00
10 20 30 ...
```
Expected: `00 01 02 03 ... ff 00 01 ...`.

#### Phase A -- source citations

Slave HDL (qspi.nw):
- Quad nibble emit cadence (line 245-310): `quad_start`
  primes `quad_next_nibble = seed[7:4] = 0x0`,
  `quad_data_byte = seed`, `quad_hi_next = 0`. Subsequent
  cycles run `quad_data` arm: when `quad_hi_next=0` emit
  `quad_data_byte[3:0]` and set `quad_hi_next=1`; when
  `quad_hi_next=1` emit `quad_data_byte_inc[7:4]`, store
  `quad_data_byte_inc`, set `quad_hi_next=0`. Net nibble
  stream for byte k: `(k_HI, k_LO, (k+1)_HI, (k+1)_LO,
  ...)`.
- Pad presenter (line 769-795): `io_pad_src` is a 4-bit
  vector identity-mapped from `quad_next_nibble`
  (line 770-775: `{q[3], q[2], q[1] (or shift_out[7]),
  q[0]}`). `io_pad_out` is registered on `negedge sclk`,
  `SB_IO` is unregistered bidirectional pad
  (`PIN_TYPE = 6'b101001`, line 880-916). All four lanes
  use the same identity ordering -- no swap.
- Pin map (verilog/qspi.pcf): `io[0]=47, io[1]=44,
  io[2]=60, io[3]=48`. Identical to verilog/spi.pcf.

Master (cli.c):
- `cmd_quad_read` (line 806-825): instruction=0x6B,
  addr_bytes=3, dummy_cycles=8, inst_lines=1, addr_lines=1,
  data_lines=4, FMODE_READ, READ_CAP=1024.
- `cmd_bench` quad path (line 1011-1013): opcode=0x6B,
  dl=QSPI_LINES_4, dummy=8 (for `b ... 1 0`).
- `qspi_init` (qspi.c:128-175): if `sample_shift`,
  `cr |= QUADSPI_CR_SSHIFT` -- SSHIFT delays the master's
  sample point by half an SCLK cycle.
- FIFO threshold (qspi.c:160): `cr |= (15U << FTHRES_Pos)`
  -- FTHRES=15, threshold trigger at 16 bytes in FIFO.

MP135 board.h pin map (line 271-282, primary variant):
QSPI_IO0=PH3, QSPI_IO1=PF9, QSPI_IO2=PH6, QSPI_IO3=PH7.
This is a wired-up logical mapping; not directly
comparable to FPGA iCEstick pins without the harness
schematic. The same wires DID pass single-lane integrity
in spi blocks 1-7, so the lane mapping matches end-to-
end (single lane uses IO[0]=MOSI, IO[1]=MISO; quad uses
all four). If a lane-swap existed, single-lane MISO
would be on the wrong wire and JEDEC ID would fail --
which it does not.

LANES=4 alternative (spi.nw line 141-160): the
`spi_quad.bin` bitstream is a streaming source that
drives all 4 lanes from CS-fall onwards with no opcode
or framing protocol. It is INCOMPATIBLE with `q` or
`b ... 1 0` (which issue 0x6B + 24-bit addr + 8 dummy
on IO[0] before reading) -- using it would cause a bus
conflict on IO[0] during opcode/addr phases. Dual-
bitstream test (Worker iter 1 hypothesis) is therefore
NOT a clean discriminator.

#### Phase B -- root cause judgment (MEDIUM confidence)

Mechanism: hybrid of (m2) sample-shift / nibble-edge
alignment AND a 16-byte boundary effect (likely FIFO-
related, since FTHRES=15).

Trace under the hypothesis "master starts sampling at
slave nibble index +1" (i.e., misses the first nibble
the slave drives):
- byte 0 master = (n[1], n[2]) interpreted upper-first
  = (0_LO, 1_HI) = (0, 0) = 0x00 [matches]
- byte 1 master = (n[3], n[4]) = (1_LO, 2_HI) = (1, 0)?
  No -- this gives 0x10? Actually (1_LO=1, 2_HI=0)
  packed as upper|lower = (1<<4)|0 = 0x10 [matches]
- byte 2 master = (2_LO, 3_HI) = (2<<4)|0 = 0x20
  [matches]
- ...
- byte 14 master = (E_LO, F_HI) = (E<<4)|0 = 0xE0
  [matches]
- byte 15 master = (F_LO, 10_HI) = (F<<4)|1 = 0xF1
  [BUT OBSERVED 0x10!]

So the +1 nibble-shift hypothesis matches bytes 0-14
exactly, then breaks at byte 15. The 16-byte cycle
strongly suggests that at every 16-byte FIFO threshold
boundary, the master picks up an EXTRA nibble (from
re-arming the FIFO read), so a +1 nibble error
accumulates to +2, +3, etc., per 16-byte chunk, and the
captured pattern shifts. This is consistent with the
QUADSPI's 32-byte word FIFO with FTHRES=15 (16-byte
trigger).

Confidence: MEDIUM. The exact STM32 QUADSPI behavior at
16-byte FIFO boundaries with sshift=1 is not in our
source tree (it's in ROM/silicon); the empirical pattern
strongly points there but a definitive root-cause needs
discriminative evidence from the diagnostic opcodes
0x6C/0x6D/0x6E/0x6F that already exist in the slave HDL.

Rejected mechanisms:
- (m1 simple): pure HI/LO swap -- breaks at byte 15.
- (m3): wrong opcode -- `op=6b read` sentinel confirms
  the slave saw 0x6B and ran the data phase.
- (m4): 16-byte page buffer -- the slave's `data_byte`
  counter wraps mod-256, not mod-16; reads stream the
  pattern not the page buffer (qspi.nw line 78-84,
  351-359).
- (m5): lane swap -- single-lane integrity passes (spi
  blocks 1-7), so wires are correctly mapped; if quad
  lanes were swapped between FPGA pcf and MP135 pinmux,
  bytes 0-14 would NOT show the clean
  high-nibble-ramp / low-nibble-zero pattern they do.
- (m6 short capture): parser artefact. The `q 0 1024`
  command DID return all 1024 bytes -- the
  `op=6b read 1024 @ 0x00000000` sentinel fired -- but
  verify.py's `_bytes_after` stops at the first non-
  hexdump line.

#### Phase C -- chosen step: WORK

Add diagnostic blocks 0x6C / 0x6D / 0x6E / 0x6F (already
implemented in qspi.nw and cli.c, used in spi.nw lines
1525-1609 + 1723-1749) to `src/spi_quad.nw` BEFORE the
`q 0 1024` preflight. Each diagnostic emits a known
short pattern over 32 bytes:

- 0x6C (`Y 32`): one-hot nibble stream `1, 2, 4, 8,
  1, 2, 4, 8, ...`. Master pairing returns `0x12 0x48
  0x12 0x48 ...`. A clean pass distinguishes "lane-
  isolated drive correct" from "byte/nibble pairing
  shifted" -- if master sees `0x21 0x84` it's pair-
  swapped; if it sees `0x12 0x12 0x48 0x48` it's
  duplicate-sampling.
- 0x6D (`Z 32`): byte sequence around the FIFO-boundary
  region (`06 07 08 09 0a 0b 0c 0d 06 07 ...`).
  Discriminates byte-FIFO faults from nibble-transition
  faults.
- 0x6E (`W 32`): nibble-hold sequence (`00 11 22 33 44
  55 66 77 88 99 aa bb cc dd ee ff` repeating). Each
  byte holds one nibble VALUE across both quad sample
  edges -- the master should NEVER see misalignment
  here regardless of sshift, because both samples per
  byte are the same value. Pass = sample-edge timing
  is fine; fail with shift = sample-edge timing is
  broken.
- 0x6F (`U 32`): continuous nibble ramp (`01 23 45 67
  89 ab cd ef`...). Isolates nibble-to-nibble transition
  timing from byte-boundary effects.

Combined, these four 32-byte diagnostics in one
iteration give a **decision matrix**:
- 0x6E pass + 0x6F fail -> nibble-transition timing
  margin (sshift / data-eye).
- 0x6E fail + 0x6F fail -> sample-edge alignment
  problem.
- 0x6C pass + 0x6B fail at byte 15 -> FIFO-boundary
  byte-pack glitch (16-byte FTHRES side effect).
- 0x6D fail at the same offset -> byte-FIFO fault.
- All four pass + 0x6B still fails -> the failure mode
  is unique to the `quad_data_byte_inc` cadence in
  qspi.nw 0x6B (not the diagnostic cadence).

Worker WILL also keep the existing `q 0 1024` preflight
block (so iter 2 still produces the same comparison
data) but should add the `q 0 32` short version FIRST
(so we see whether the corruption begins at byte 15 or
earlier). This adds ONE more block.

Predicted blast radius: small. Five new TEST.md blocks
+ four new verify.py helper functions copied verbatim
from spi.nw. No HDL changes, no Makefile changes, no
bitstream changes. The qspi.bin in use is unchanged
from the qspi-FSM-verified build.

Fallback if iter 2 also fully reds: iter 3 becomes
WORK with one of the following:
- If 0x6E passes alone, iter 3 tries `p 203 0\r`
  (sshift=0) at the preflight to nail the sample-edge
  hypothesis.
- If all diagnostics also fail at byte 15, iter 3 tries
  `q 0 16` and `q 0 17` to bracket the boundary, AND
  tries `p 203 0\r` to remove sshift as a variable.

Why not "switch to spi_quad.bin": that bitstream is a
raw streaming source incompatible with the framed `q`/
`b 1 0` commands (bus conflict on IO[0] during opcode
phase). It would fail differently and not give clean
discriminative evidence.

Why not "fix slave HDL now": the slave's nibble cadence
is correct on paper; before editing HDL we need
diagnostic evidence telling us WHICH cadence assumption
is wrong. Iter 2 collects exactly that.

Why not "fix firmware q": the MP135 cli.c and qspi.c
are outside the agent4 scope (they're built and flashed
via `bench_mcu:reset_dut` from a pre-built `main.stm32`
blob -- the agent4 rig does NOT rebuild the MP135
firmware per test). Editing cli.c would require an out-
of-scope MP135 firmware re-flash that is not in the
fpga.test plan. BLOCKED for this approach.

#### Iter 2 step: WORK

Worker edits `src/spi_quad.nw` to insert FIVE new
TEST.md blocks BEFORE the existing
`Preflight -- quad peripheral framed read` block:
1. `Diagnostic -- quad peripheral 0x6C one-hot read`
   (copied verbatim from spi.nw:1525-1551).
2. `Diagnostic -- quad peripheral 0x6D byte sequence`
   (copied verbatim from spi.nw:1723-1749).
3. `Diagnostic -- quad peripheral 0x6E nibble-hold`
   (copied verbatim from spi.nw:1553-1580).
4. `Diagnostic -- quad peripheral 0x6F nibble-ramp`
   (copied verbatim from spi.nw:1582-1609).
5. `Preflight -- quad peripheral 0x6B short 32-byte
   read` (new -- same shape as existing preflight but
   `q 0 32` instead of `q 0 1024`, sentinel
   `op=6b read 32 @ 0x00000000`, check
   `check_raw_read_pattern("quad", 32)`).

The `<<verify.py>>=` chunk gets four new helpers
(`check_quad_onehot_read`, `check_quad_byte_diag_read`,
`check_quad_nibble_hold_read`, `check_quad_nibble_ramp_read`)
copied verbatim from spi.nw verify.py (lines 2240-2400).
The DISPATCH dict gets five new entries.

Existing 4 blocks (current preflight + 3 sweeps) stay
in place after the new diagnostic block group. Total
blocks: 9. Even if the diagnostics all pass and the
1024-byte preflight still fails, the sweeps will be
attempted -- which gives us multi-presc evidence in one
shot.

#### Files involved (Worker iter 2)

- EDITED: `fpga/src/spi_quad.nw` -- one or two new chunks
  in TEST.md and verify.py.
- UNCHANGED: every other file. No HDL, no Makefile.

#### Iter 2 rig reset evidence (planning Manager)

- Command: `python3 -u $TEST_SERV/run_md.py --ledger
  /home/agent4/fast_data/agent4/ledger.txt --module uart
  --log /home/agent4/fast_data/agent4/log.txt` from
  `/home/agent4/fast_data/fpga/build/uart`.
- Exit code: 0.
- Result: `1 BLOCK PASSED`, sub-checks 3/3 PASS:
  `[1/3 PASS] Check test_serv had no errors`,
  `[2/3 PASS] Check heartbeat banner present (3 banner
  hits)`, `[3/3 PASS] Check echo loop returned the probe
  bytes (2/2 probes echoed)`. Sentinel
  `n_ops=10, n_errors=0, early_done=false`.
- New ledger row: `2026-04-30T18:54:44 uart 3`.
- Rig is up: yes.

#### Open questions / risks for Worker

- The `_bytes_after` parser in spi_quad's verify.py is
  the same shape as spi.nw's; for 0x6C/0x6D/0x6E/0x6F
  the helpers in spi.nw use `_bytes_after(header)` with
  `header = f"op=6{c} read {count} @ 0x00000000"`. Make
  sure the COPIED helpers either use the same `BENCH_RE`-
  free `_bytes_after`/`HEXLINE_RE`/`HEXBYTE_RE` already
  present in spi_quad.nw verify.py (they are) and don't
  pull in `_write_q6b0_if_present` / `_last_q6b` /
  `_last_q6b_if_present` (those are spi-specific debug
  helpers tied to fpga.uart 'q6b' diagnostic lines that
  are NOT enabled in spi_quad's blocks). DROP those
  diagnostic-only branches when copying.
- Diagnostic blocks in spi.nw pair `fpga:open` /
  `fpga:uart_open` ... `fpga:uart_close` /`fpga:close`
  around the `mp135:uart_*` flow because spi.nw enables
  the FPGA UART diagnostic stream. spi_quad.nw block 1
  does NOT open `fpga.uart` -- that's why the existing
  preflight only uses `mp135:uart_open` / close. Worker
  must DECIDE: either copy the spi.nw blocks verbatim
  including the `fpga:open` / `fpga:close` (which adds
  the `fpga.uart` stream and may slow runs), OR strip
  those out and use only the `mp135:uart` flow like
  spi_quad's existing preflight does (faster, simpler,
  but loses fpga-side correlation evidence). Recommend
  STRIP for iter 2 -- the diagnostic value is in the
  MP135 capture, and the FPGA uart printer log doesn't
  add discriminative value here. (Iter 3 can re-add
  fpga.uart capture if needed.)
- Each new block costs ~6-10 s of test time
  (program + boot + uart_expect + close). Five new
  blocks ~ 50 s extra. Plus the existing 4 blocks: ~80 s
  total for the regression. Well within the test_serv
  budget.
- The `q 0 32` block may PASS -- if it does, that's
  itself important evidence that the corruption appears
  only after the FIFO crosses 16 bytes the first time.
  Verify.py needs `check_raw_read_pattern("quad", 32)`
  to be added to DISPATCH.

#### Iter 2 budget

spi_quad: 2/8 consumed. After iter 2, 6 iterations
remain. The diagnostic evidence collected in iter 2 will
direct iter 3 (HDL fix, sshift sweep, or boundary
investigation) to root-cause within at most 2 more
iterations, leaving 3-4 iterations for the actual
mission target (>=200 Mbps wall-rate at presc=5 in quad
mode), which still requires the preflight to PASS.
