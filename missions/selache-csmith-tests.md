### selache draft gcc host sweep

Compile and run every csmith draft through host `gcc`, using the
existing xtest draft target to compare each program's `got NN` output
against its source `@expect` value. This is the first reference gate for
the draft suite and does not exercise clang, CCES, Selache, or hardware.

Build:

```
make -C selache/xtest drafts-gcc -j$(nproc)
```

Test: no hardware.

Verify:

```
def check(extract_dir):
    from pathlib import Path

    xtest = Path('selache/xtest')
    drafts = sorted((xtest / 'draft_cases').glob('cctest_*.c'))
    if not drafts:
        return True

    out = xtest / 'build/drafts/gcc'
    expected = {p.stem for p in drafts}
    runs = {p.stem for p in out.glob('cctest_*.run')}
    bins = {p.stem for p in out.glob('cctest_*.bin') if p.stat().st_size}

    return runs == expected and bins == expected
```

### selache draft clang host sweep

Compile and run every csmith draft through host `clang`, mirroring the
gcc draft sweep above. Adds a second reference toolchain gate before any
of the embedded toolchains (cces, sel) or bench hardware get involved.
Host-only; no bench required.

Build:

```
make -C selache/xtest drafts-clang -j$(nproc)
```

Test: no hardware.

Verify:

```
def check(extract_dir):
    from pathlib import Path

    xtest = Path('selache/xtest')
    drafts = sorted((xtest / 'draft_cases').glob('cctest_*.c'))
    if not drafts:
        return True

    out = xtest / 'build/drafts/clang'
    expected = {p.stem for p in drafts}
    runs = {p.stem for p in out.glob('cctest_*.run')}
    bins = {p.stem for p in out.glob('cctest_*.bin') if p.stat().st_size}

    return runs == expected and bins == expected
```

### selache draft cces compile gate

Compile every csmith draft through the embedded `cces` toolchain,
mirroring the gcc and clang draft sweeps above. This is the third
reference toolchain gate and the first that exercises the embedded
target ABI (producing `cctest_*.0xNN.ldr` siblings). Host-only; no
bench hardware required. Locks cces in as a reference before we start
chasing selcc/seld bugs surfaced by `make drafts-sel`.

Build:

```
make -C selache/xtest drafts-cces -j$(nproc)
```

Test: no hardware.

Verify:

```
def check(extract_dir):
    from pathlib import Path
    import re

    xtest = Path('selache/xtest')
    drafts = sorted((xtest / 'draft_cases').glob('cctest_*.c'))
    if not drafts:
        return True

    out = xtest / 'build/drafts/cces'
    expected = {p.stem for p in drafts}
    bins = {p.stem for p in out.glob('cctest_*.ldr')
            if p.stat().st_size and not re.search(r'\.0x[0-9a-f]+\.ldr$', p.name)}
    targets = {re.sub(r'\.0x[0-9a-f]+$', '', p.stem)
               for p in out.glob('cctest_*.0x*.ldr') if p.stat().st_size}

    return bins == expected and targets == expected
```

### selcc narrow-array brace-elided scalar initializer

Fix a selcc C99 conformance bug: a scalar element of a `char` / `short`
narrow array initializer surrounded by braces (`int8_t arr[N] = { ...,
{1}, ... }`) crashes the global initializer emitter with
`narrow array element requires a numeric constant initializer; got
InitList([IntLit(1, UL)])`. C99 6.7.8 explicitly allows extra braces
around a scalar initializer (brace-elision is the inverse direction).

The faulty path is the leaf-scalar arm of `flatten_narrow_array_init`
in `selache/selcc/src/emit_asm.rs:863-883`: it calls
`eval_const_expr_i64(init)` directly on whatever `init` it received,
even when `init` is `Expr::InitList` containing a single inner scalar.
The fix is local: when the leaf branch sees an `Expr::InitList` with
exactly one element, recurse on that single element (or peel the brace
and re-evaluate). InitLists with zero or more than one element at a
scalar position remain hard errors. The same brace-elision should also
be tolerated by the local-initializer twin in
`selache/selcc/src/lower.rs` (`flatten_narrow_array_local`, around line
5929) so file-scope and block-scope narrow arrays stay consistent.

This unblocks csmith draft `g_56` and any other draft that lands an
extra brace around a narrow-array scalar element.

Build:

```
cd selache && cargo build --release
cd selache && cargo test -p selcc --release narrow_array_brace_elided_scalar_init -- --nocapture
cd selache && cargo clippy --all-targets --release -- -D warnings
```

The new `narrow_array_brace_elided_scalar_init` test must live in
`selache/selcc/src/emit_asm.rs` alongside the other `#[test]` items.
It should call `selcc::compile_to_asm` (with `cli::Options { char_size:
8, ..Default::default() }`) on a minimal source like

```c
signed char arr[3] = { 0, {1}, 2 };
```

and assert the call returns `Ok` (and, ideally, that the emitted asm
contains the byte 0x01 packed into the expected word). The test must
fail before the fix and pass after it.

Test: no hardware.

Verify:

```
def check(extract_dir):
    return True
```

### selcc sub-word struct field global init

Fix the first link in a chain of selcc bugs that block sub-word struct
fields in global initializers: the struct branch of `build_init_words`
in `selache/selcc/src/emit_asm.rs:1163-1188` hard-errors on every field
whose `byte_off % 4 != 0` with `field <name> at byte offset N is not
word-aligned; sub-word struct fields in global initializers are not
supported`. Sub-word fields (`int8_t`, `int16_t`, etc.) inside a struct
global must be packed into their containing 32-bit word's initializer
value, not rejected, since SHARC addresses memory in 32-bit words and
the struct layout already places multiple sub-word fields per word.

Replace the unconditional error with packing logic in `field_map`
construction and in the positional / `Expr::DesignatedInit` paths that
write into `v` (around lines 1186-1232). For each containing word
(`byte_off / 4`), compute a single `InitWord::Num` whose value is the
bitwise OR of each sub-word field's value shifted left by
`(byte_off % 4) * 8`. Width comes from `size_bytes_ctx(fty, tctx)`
(1 or 2 bytes typical) and the field's value is masked to that width
before shifting so adjacent fields do not collide.

Scope this iteration narrowly to sub-word fields whose values are
**constant integer literals** (the simplest and most common shape).
Bitfields, nested aggregates packed into a sub-word slot, string
literals, and addresses remain rejected with the existing error so the
fix stays auditable. Word-aligned fields keep their existing per-word
emission unchanged.

This is the **first of several iterations** required to unblock csmith
drafts that mix sub-word struct fields with harder shapes (e.g.
`cctest_csmith_9405adb0.c` mixes a `#pragma pack(1)` struct, a 10-bit
bitfield, and a nested aggregate, plus separately overflows seld layout).
Subsequent iterations will extend packing to bitfields, then nested
aggregates, mirror the fix in the local-scope twin
`flatten_struct_init_local`/`build_struct_local_init` in
`selache/selcc/src/lower.rs`, and address the seld layout overflow as
an independent bug. This step alone unblocks any future draft (or
hand-shrunk reproducer) that lands only the constant-int sub-word
pattern; the unit test below exercises exactly that capability and
fails before the fix.

Build:

```
cd selache && cargo build --release
cd selache && cargo test -p selcc --release sub_word_struct_field_global_init -- --nocapture
cd selache && cargo clippy --all-targets --release -- -D warnings
```

The new `sub_word_struct_field_global_init` test must live in
`selache/selcc/src/emit_asm.rs` alongside the other `#[test]` items.
It should call `selcc::compile_to_asm` (with `cli::Options { char_size:
8, ..Default::default() }`) on a minimal source that places two
sub-word fields into one word, e.g.

```c
struct S { signed char a; signed char b; int w; };
struct S g = { 0x12, 0x34, 0x55667788 };
```

and assert the call returns `Ok` (and ideally that the emitted asm
contains `0x3412` packed into the first word). The test must fail
before the fix and pass after it.

Test: no hardware.

Verify:

```
def check(extract_dir):
    return True
```

### selcc bitfield struct global init

Lift the next link in the sub-word struct-field chain: the `field_map`
construction loop in `selache/selcc/src/emit_asm.rs` (around lines
1215-1244, just added by the prior step) hard-errors on every struct
field whose type is `Type::Bitfield(_, _)` with `field <name> is a
bitfield; bitfields in struct global initializers are not supported`.
Csmith draft `cctest_csmith_9405adb0.c` defines `struct S0 { signed f0
: 6; }` and `struct S1 { int8_t f0; unsigned f1 : 10; uint8_t f2;
uint64_t f3; struct S0 f4; }` (under `#pragma pack(1)`), and any global
initializer for `S1` therefore trips this rejection even after the
constant-int sub-word packing fix landed.

Replace the up-front bitfield rejection with packing into the
containing 32-bit word. The bit offset and width come from
`crate::types::struct_field_layout_ctx(fields, fname, tctx)`, which
already returns `(byte_offset, Some(bit_offset), Some(bit_width))` for
bitfields (see `selache/selcc/src/types.rs:488-533`). For each
bitfield-typed field, evaluate its initializer as a constant integer,
mask to `bit_width` bits (`value & ((1u64 << bit_width) - 1)`), shift
left by `(byte_offset % 4) * 8 + bit_offset_within_byte` so the bits
land at the correct position inside the containing word, and OR into
the existing `InitWord::Num` slot at `byte_offset / 4`. Designated
initializers for bitfield fields take the same packed path.

Scope this iteration narrowly:
- Bitfield value must still be a constant integer literal (no symbol,
  no `Expr::InitList`, no `Expr::StringLit`).
- Cross-word bitfields (a bitfield whose `bit_offset + bit_width`
  exceeds the containing storage unit) keep a hard error so the fix
  stays auditable.
- Nested aggregates packed at sub-word slots stay rejected (deferred
  to the next iteration).
- Word-aligned non-bitfield fields keep their existing recursive
  emission unchanged.
- The local-scope twin in `selache/selcc/src/lower.rs` stays untouched
  (a later iteration will mirror the fix there).

This is the **third link** in the chain that ultimately unblocks
`cctest_csmith_9405adb0.c`'s `struct S1 g_166[3][4][3]` global. After
this step, the remaining links are: nested aggregate sub-word fields
(e.g. `struct S0 f4` packed at a sub-word offset inside `S1`), the
local-scope twin in `lower.rs`, and the independent seld layout
overflow surfaced by the same draft. None of those are addressed here.

Build:

```
cd selache && cargo build --release
cd selache && cargo test -p selcc --release bitfield_struct_global_init -- --nocapture
cd selache && cargo clippy --all-targets --release -- -D warnings
```

The new `bitfield_struct_global_init` test must live in
`selache/selcc/src/emit_asm.rs` alongside the other `#[test]` items.
It should call `selcc::compile_to_asm` (with `cli::Options { char_size:
8, ..Default::default() }`) on a minimal source that places a bitfield
into the containing word of a struct global, e.g.

```c
struct S { unsigned f0 : 10; unsigned f1 : 6; int w; };
struct S g = { 0x123, 0x2A, 0x55667788 };
```

and assert the call returns `Ok` (and ideally that the emitted asm
contains `((0x2A & 0x3F) << 10) | (0x123 & 0x3FF) == 0xA923` packed
into the first word). The test must fail before the fix and pass after
it.

Test: no hardware.

Verify:

```
def check(extract_dir):
    return True
```

### selcc cap block0 helper spill against L1 budget

When the csmith root is too large for block0 (`root_instrs > 24_000`),
selcc currently sends `func_1` to `block1_swco` and dumps every other
"large" csmith body (`is_large_csmith_generated_body`) into
`seg_l1_block0_swco`. For draft `cctest_csmith_9405adb0`, the resulting
block0 input totals 132064 units versus a 130064-unit budget (after the
64KB `stack_reserve` carve-out), so seld fails with:

```
%seld - FATAL ERROR
layout overflow: section `block0_sw_code` requires 132064 units in
segment `mem_l1_block0` but only 130064 units remain
```

Fix in `selcc/src/emit_asm.rs`: track a running estimate of instruction
units already routed to `seg_l1_block0_swco` while iterating
`compiled`, and once the next large helper would exceed a conservative
block0 cap (e.g. 60_000 emitted instrs ~ 120_000 units, leaving
headroom for `main`/`test_main` and alignment fill), redirect that
helper to the default `seg_swco` (block2) instead. Keep the existing
small-root carve-outs (`crc32_*`, `transparent_crc`, the single
`spill_nonroot_func`) unchanged — they already respect the budget. The
24-bit CJUMP-range comment in `link.ldf` is preserved for the helpers
that still fit; only overflow spills to block2. No changes to
`link.ldf`, `seld`, or any test assertion (no xtest case currently
asserts block0 placement; selcc's own emit_asm tests only require that
"useful generated non-root body should spill into block0 for small
roots", which the small-root path still does).

Build:

```
cd selache && cargo build --release
cd selache && cargo test -p selcc --release -- --nocapture
cd selache && cargo clippy --all-targets --release -- -D warnings
make -C selache/xtest build/drafts/sel/cctest_csmith_9405adb0.ldr -j$(nproc)
```

Test: no hardware.

Verify:

```
def check(extract_dir):
    from pathlib import Path
    p = Path('selache/xtest/build/drafts/sel/cctest_csmith_9405adb0.ldr')
    return p.exists() and p.stat().st_size > 0
```

### dsp reset drains stale uart residue before tests capture

The csmith draft bench-sweep reaches the hardware UART verify phase but
fails because the DSP UART stream captures a `got <hex>` line from the
PRIOR boot's tx tail (lurking in the FT232/USB-host pipeline) BEFORE the
freshly-loaded ldr has produced its own output. Iter-8 timeline for
`cctest_csmith_0f4d7af9.0xaa43ccd0.ldr` shows `STREAM dsp.uart 'got
efad66fa\r\n'` at t=5.060 — after `dsp:uart_open` (t=4.659) and BEFORE
`dsp:boot wrote 230400/230400` (t=5.142). `dsp:uart_expect` then matches
the residue, and bench Verify's `re.findall(r'got\s+([0-9a-fA-F]+)',
uart)` picks up the stale hex (`efad66fa`) instead of the post-boot one
(`aa43ccd0`).

`plugins/dsp.py` `DspHandle.uart_open` only does
`self._ser.reset_input_buffer()` once at the moment the serial port is
opened (line 58), then immediately starts the reader thread. Bytes
already in flight on the USB-host side at that instant are not flushed:
they arrive at the host's serial buffer microseconds AFTER `uart_open`
returns, so the reader thread streams them straight into `dsp.uart`.
The plugin docstring (`"SHARC DSP over FT4222 QSPI master; expander
reset; UART drain."`, line 729) already advertises a UART drain that the
code does not actually perform.

Fix in `_op_reset` (around lines 216-220 of `selache/test_serv/plugins/
dsp.py`, i.e. the `dsp:reset` op handler): after `pulse_reset` and
`init_and_reset` return — i.e. after the SHARC has been driven into the
expander-reset state and re-initialised — open the configured
`h.serial_port` briefly with the same baud as `uart_open` uses, call
`reset_input_buffer()`, then read-and-discard for ~200 ms (or until two
consecutive 0-byte reads with `timeout=0.05` return empty), and close.
This eats any tx-FIFO tail from the prior boot that is still draining
into the host while the bus pulse runs. `dsp:uart_open` afterwards opens
a clean port with no residue. The drain is unconditional and therefore
benefits every consumer of `dsp:reset` (not just this csmith sweep). If
no `serial_port` is configured for the dsp instance (probe returned
None) the drain is a no-op. The reset op already has session-cancel
hooks; the drain loop must respect `session.cancel_event.wait` between
chunks so cancel propagation is preserved.

Add a unit test `test_dsp_reset_drains_uart_residue` to
`test_serv/test_core.py` alongside the existing `test_dsp_boot_*` items.
The test must:

- Monkeypatch `dsp._lazy_serial()` (or `serial.Serial` on the lazy-
  imported module) to return a fake serial object that yields a known
  payload (e.g. `b'got efad66fa\r\n'`) on `read()` and records
  `reset_input_buffer` and `close` calls.
- Monkeypatch `dsp._Expander` so `pulse_reset` and `init_and_reset` are
  cheap no-ops (no FT4222 hardware required).
- Construct a `DspHandle` with a non-empty `serial_port` and a fake
  session (mirroring the `FakeSession` pattern already used by
  `test_dsp_boot_requires_timeout_and_kills_hung_helper`).
- Invoke `dsp._op_reset(session, handle, {})`.
- Assert: the fake serial was opened, `reset_input_buffer` was called,
  the residue payload was consumed (read() returned at least one
  non-empty chunk), and the port was closed before `_op_reset` returned.
- Add a second assertion path with `serial_port=None` confirming
  `_op_reset` returns successfully without trying to open a serial.

The test must fail before the fix (today `_op_reset` opens no serial at
all, so `serial.Serial` is never called on the residue path) and pass
after.

Build:

```
cd test_serv && python3 test_core.py
```

Test: no hardware.

Verify:

```
def check(extract_dir):
    return True
```

### dsp expander reopen retries on DEVICE_NOT_OPENED flake

Item 12 of the bench-sweep (`cctest_csmith_3f1fa455.0x39f2cfc.ldr`)
fails three retries in a row with the same shape: `_Expander.pulse_reset`
crashes at `ft.openByDescription(self.desc)` with
`ft4222.ft4222.FT2XXDeviceError: DEVICE_NOT_OPENED`, and then
`dsp:uart_expect` times out because the chip never booted. Items 1-11
pass back-to-back, so the FT4222 device handle accumulates state across
the sweep: each `dsp:boot` spawns a child that opens the device
(`_open_master`, line 202-211 of `selache/test_serv/plugins/dsp.py`),
streams the LDR, and `dev.close()`s. After enough back-to-back boots,
the FT4222 driver occasionally returns `DEVICE_NOT_OPENED` to the next
`openByDescription` even though no other process holds the handle (a
known FTDI USB-host re-enumeration race; the device is fine a moment
later). Today every `openByDescription` call site in `dsp.py`
(`_Expander.pulse_reset` line 149, `_Expander.init_and_reset` line 132,
and the boot helper at line 364) opens once and propagates any error.
The sweep only fails when this race lands on the very first op of an
item, because that is `dsp:reset` and there is nothing to retry it.

The host gcc build of `cctest_csmith_3f1fa455` runs in 2 ms and emits
exactly `got 39f2cfc` (matches its `@expect 0x39f2cfc`), so the failing
draft is not at fault — the toolchain output is correct, the bench just
never gets to capture it.

Fix in `selache/test_serv/plugins/dsp.py`: add a small private helper
`_open_ft4222_with_retry(desc, session=None, attempts=4, backoff_s=0.2)`
that wraps `_lazy_ft4222().openByDescription(desc)` and retries on
`FT2XXDeviceError` whose `args[0]` is `DEVICE_NOT_OPENED` (string-match
the enum name to avoid hard-importing the ft4222 enum). Between
attempts, sleep `backoff_s * 2**i` (0.2 s, 0.4 s, 0.8 s) via
`session.cancel_event.wait(...)` when a session is supplied so cancel
propagation is preserved, falling back to `time.sleep` when not. After
the last attempt, re-raise the original error verbatim. Use the helper
at the three openByDescription call sites: `_Expander.pulse_reset`
(line 149), `_Expander.init_and_reset` (line 132, no session), and the
inline boot helper code at line 364 (string-replace the
`dsp._open_master(...)` line with a snippet that resolves through the
new helper before calling `dev.spiMaster_Init` — the cleanest shape is
to add a public `dsp._open_ft4222_with_retry` that the helper imports
and calls, then have `_open_master` route through it). Other
`openByDescription` paths (none today) inherit the same retry by going
through the helper. The helper does not catch `BusyError` or any other
exception class.

Add a unit test `test_expander_pulse_reset_retries_on_device_not_opened`
to `selache/test_serv/test_core.py` alongside the existing
`test_dsp_reset_*` items. The test must:

- Monkeypatch `_lazy_ft4222()` to return a fake module whose
  `openByDescription` raises a fake `FT2XXDeviceError("DEVICE_NOT_OPENED")`
  on the first two calls and returns a fake dev (with no-op
  `i2cMaster_Init`, `close`, and `__getattr__` for the i2c writes) on
  the third.
- Construct a `FakeSession` (mirror existing `test_dsp_boot_*` fakes)
  with a non-set `cancel_event`.
- Call `_Expander(desc='X')`.pulse_reset(session=fake_session)`.
- Assert: `openByDescription` was called exactly 3 times, the call
  returned without raising, and the fake `cancel_event.wait` was called
  with the expected back-off arguments (0.2, 0.4).

A second sub-test must construct a fake that always raises
`DEVICE_NOT_OPENED` and assert that `pulse_reset` re-raises after 4
attempts (i.e. retries are bounded).

A third sub-test must construct a fake that raises a *different*
`FT2XXDeviceError` (e.g. `OTHER_ERROR`) on the first call and assert
that `pulse_reset` re-raises immediately without retrying — the helper
only retries the specific `DEVICE_NOT_OPENED` shape.

The tests must fail before the fix (today `openByDescription` is called
once and any error propagates) and pass after.

Build:

```
cd test_serv && python3 test_core.py
```

Test: no hardware.

Verify:

```
def check(extract_dir):
    return True
```

## WIP

# Selache csmith draft regression sweep

Validate randomly-generated cctest candidates in
`selache/xtest/draft_cases/` against gcc, clang, cces, and sel before
they get hand-promoted into the locked `cases/` core suite. Same
plan/verify shape as the core sweep (companion mission
`selache-core-tests.md`); the only deltas are the source directory
(`draft_cases/` instead of `cases/`) and the build/output prefix
(`build/drafts/` instead of `build/`).

Selache is a full C99 toolchain. Drafts may intentionally exercise
difficult C99 features such as structs, unions, bitfields, nested
aggregate initializers, aggregate copy/assignment, aggregate function
arguments and returns, exact layout, and the runtime support those
constructs require. A failure in `sel`, `selcc`, `selas`, `seld`, or
`selload` is therefore a toolchain bug to diagnose and fix; do not
weaken, hand-edit, or delete a valid C99 draft merely because it hits a
currently failing implementation path. Use gcc, clang, and cces as
reference implementations for the generated C99 semantics.

Vacuously passes when `draft_cases/` is empty. Otherwise: every draft
must pass on all four toolchains before any of them get promoted. If a
draft is valid C99 and passes the reference toolchains but not Selache,
advance the toolchain until Selache passes it.

### selache cctest drafts

Build:

```
cd selache && cargo build --release
cd selache && cargo test --all-targets
cd selache && cargo clippy --all-targets --release -- -D warnings
make -C selache/xtest drafts-gcc -j$(nproc)
make -C selache/xtest drafts-clang -j$(nproc)
make -C selache/xtest drafts-cces -j$(nproc)
make -C selache/xtest drafts-sel -j$(nproc)
```

Foreach:

```
ldr in selache/xtest/build/drafts/*/cctest_*.0x*.ldr
```

Test (max 1 min):

```
dsp:reset
dsp:uart_open
dsp:boot ldr=@ldr timeout_ms=2500
dsp:uart_expect sentinel="got " timeout_ms=2500
delay ms=2500
dsp:uart_close
mark tag=cctest_run
```

Verify:

```
def check(extract_dir, ldr):
    if not Verification.manifest_clean(extract_dir):
        return False
    m = re.search(r'\.(0x[0-9a-f]+)\.ldr$', ldr)
    if not m:
        return False
    expect = int(m.group(1), 16)
    uart = Verification.load_stream_text(extract_dir, 'dsp.uart')
    got = re.findall(r'got\s+([0-9a-fA-F]+)', uart)
    return bool(got) and int(got[-1], 16) == expect
```

