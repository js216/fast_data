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

    return expected.issubset(bins) and expected.issubset(targets)
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

### sel csmith 0f4d7af9 checksum

Fix the next focused draft runtime mismatch from the full foreach sweep:
`selache/xtest/build/drafts/sel/cctest_csmith_0f4d7af9.0xaa43ccd0.ldr`
boots after writing the full `230400/230400` bytes and prints
`got efad66fa` on the DSP, but the source declares the expected checksum
encoded in the artifact name, `0xaa43ccd0`. Keep this step scoped to
this single Selache-built draft and the compiler/runtime behavior needed
to make it report the expected checksum on hardware. Do not rewrite the
expected checksum, delete the draft, weaken the foreach test, or replace
this with a full draft-sweep fix.

Build:

```
make -C selache/xtest build/drafts/sel/cctest_csmith_0f4d7af9.0xaa43ccd0.ldr -j$(nproc)
```

Artifacts:

```
selache/xtest/build/drafts/sel/cctest_csmith_0f4d7af9.0xaa43ccd0.ldr
```

Test (max 1 min):

```
dsp:reset
dsp:uart_open
dsp:boot ldr=@cctest_csmith_0f4d7af9.0xaa43ccd0.ldr timeout_ms=2500
dsp:uart_expect sentinel="got " timeout_ms=2500
delay ms=2500
dsp:uart_close
mark tag=cctest_run
```

Verify:

```
def check(extract_dir):
    uart = Verification.load_stream_text(extract_dir, 'dsp.uart')
    got = re.findall(r'got\s+([0-9a-fA-F]+)', uart)
    return bool(got) and int(got[-1], 16) == 0xaa43ccd0
```

### cces csmith c19baf86 checksum

Fix the next focused draft runtime mismatch from the full foreach sweep:
`selache/xtest/build/drafts/cces/cctest_csmith_c19baf86.0x83abec32.ldr`
boots after writing the full `13312/13312` bytes and prints
`got df7bba29` on the DSP, but the source declares the expected checksum
encoded in the artifact name, `0x83abec32`. Keep this step scoped to
this single CCES-built draft and the compiler/runtime behavior needed to
make it report the expected checksum on hardware. Do not rewrite the
expected checksum, delete the draft, weaken the foreach test, or replace
this with a full draft-sweep fix.

Build:

```
make -C selache/xtest build/drafts/cces/cctest_csmith_c19baf86.0x83abec32.ldr -j$(nproc)
```

Artifacts:

```
selache/xtest/build/drafts/cces/cctest_csmith_c19baf86.0x83abec32.ldr
```

Test (max 1 min):

```
dsp:reset
dsp:uart_open
dsp:boot ldr=@cctest_csmith_c19baf86.0x83abec32.ldr timeout_ms=2500
dsp:uart_expect sentinel="got " timeout_ms=2500
delay ms=2500
dsp:uart_close
mark tag=cctest_run
```

Verify:

```
def check(extract_dir):
    uart = Verification.load_stream_text(extract_dir, 'dsp.uart')
    got = re.findall(r'got\s+([0-9a-fA-F]+)', uart)
    return bool(got) and int(got[-1], 16) == 0x83abec32
```

### cces csmith 95d42820 checksum

Fix the next focused draft runtime mismatch from the full foreach sweep:
`selache/xtest/build/drafts/cces/cctest_csmith_95d42820.0x298c9077.ldr`
boots after writing the full `29696/29696` bytes and prints
`got af87f644` on the DSP, but the source declares the expected
checksum encoded in the artifact name, `0x298c9077`. Keep this step
scoped to this single CCES-built draft and the compiler/runtime
behavior needed to make it report the expected checksum on hardware. Do
not rewrite the expected checksum, delete the draft, weaken the foreach
test, or replace this with a full draft-sweep fix.

Build:

```
make -C selache/xtest build/drafts/cces/cctest_csmith_95d42820.0x298c9077.ldr -j$(nproc)
```

Artifacts:

```
selache/xtest/build/drafts/cces/cctest_csmith_95d42820.0x298c9077.ldr
```

Test (max 1 min):

```
dsp:reset
dsp:uart_open
dsp:boot ldr=@cctest_csmith_95d42820.0x298c9077.ldr timeout_ms=2500
dsp:uart_expect sentinel="got " timeout_ms=2500
delay ms=2500
dsp:uart_close
mark tag=cctest_run
```

Verify:

```
def check(extract_dir):
    uart = Verification.load_stream_text(extract_dir, 'dsp.uart')
    got = re.findall(r'got\s+([0-9a-fA-F]+)', uart)
    return bool(got) and int(got[-1], 16) == 0x298c9077
```

### cces csmith 62d5d342 checksum

Fix the next focused draft runtime mismatch from the full foreach sweep:
`selache/xtest/build/drafts/cces/cctest_csmith_62d5d342.0x925dcb2e.ldr`
boots after writing the full `10240/10240` bytes and prints
`got bb9654c2` on the DSP, but the source declares the expected checksum
encoded in the artifact name, `0x925dcb2e`. Keep this step scoped to
this single CCES-built draft and the compiler/runtime behavior needed to
make it report the expected checksum on hardware. Do not rewrite the
expected checksum, delete the draft, weaken the foreach test, or replace
this with a full draft-sweep fix.

Build:

```
make -C selache/xtest build/drafts/cces/cctest_csmith_62d5d342.0x925dcb2e.ldr -j$(nproc)
```

Artifacts:

```
selache/xtest/build/drafts/cces/cctest_csmith_62d5d342.0x925dcb2e.ldr
```

Test (max 1 min):

```
dsp:reset
dsp:uart_open
dsp:boot ldr=@cctest_csmith_62d5d342.0x925dcb2e.ldr timeout_ms=2500
dsp:uart_expect sentinel="got " timeout_ms=2500
delay ms=2500
dsp:uart_close
mark tag=cctest_run
```

Verify:

```
def check(extract_dir):
    uart = Verification.load_stream_text(extract_dir, 'dsp.uart')
    got = re.findall(r'got\s+([0-9a-fA-F]+)', uart)
    return bool(got) and int(got[-1], 16) == 0x925dcb2e
```

### cces csmith 58953aa9 boot timeout

Fix the next focused draft bench failure from the full foreach sweep:
`selache/xtest/build/drafts/cces/cctest_csmith_58953aa9.0xf57f2c63.ldr`
times out during `dsp:boot` after a partial transfer
(`2048/20480`) and produces no UART output. Keep this step scoped to
this single CCES-built draft and the loader/artefact behavior needed to
make it boot reliably. Do not rewrite the expected checksum, delete the
draft, weaken the foreach test, or replace this with a full draft-sweep
fix. The corrected CCES-built draft must boot on hardware and report
the source's expected checksum.

Build:

```
make -C selache/xtest build/drafts/cces/cctest_csmith_58953aa9.0xf57f2c63.ldr -j$(nproc)
```

Artifacts:

```
selache/xtest/build/drafts/cces/cctest_csmith_58953aa9.0xf57f2c63.ldr
```

Test (max 1 min):

```
dsp:reset
dsp:uart_open
dsp:boot ldr=@cctest_csmith_58953aa9.0xf57f2c63.ldr timeout_ms=2500
dsp:uart_expect sentinel="got " timeout_ms=2500
delay ms=2500
dsp:uart_close
mark tag=cctest_run
```

Verify:

```
def check(extract_dir):
    uart = Verification.load_stream_text(extract_dir, 'dsp.uart')
    got = re.findall(r'got\s+([0-9a-fA-F]+)', uart)
    return bool(got) and int(got[-1], 16) == 0xf57f2c63
```

### cces csmith 4c2338b1 boot timeout

Fix the next focused draft bench failure from the full foreach sweep:
`selache/xtest/build/drafts/cces/cctest_csmith_4c2338b1.0xab757f71.ldr`
times out during `dsp:boot` after a partial transfer
(`8192/19456`) and produces no UART output. Keep this step scoped to
this single CCES-built draft and the loader/artefact behavior needed to
make it boot reliably. Do not rewrite the expected checksum, delete the
draft, weaken the foreach test, or replace this with a full draft-sweep
fix. The corrected CCES-built draft must boot on hardware and report
the source's expected checksum.

Build:

```
make -C selache/xtest build/drafts/cces/cctest_csmith_4c2338b1.0xab757f71.ldr -j$(nproc)
```

Artifacts:

```
selache/xtest/build/drafts/cces/cctest_csmith_4c2338b1.0xab757f71.ldr
```

Test (max 1 min):

```
dsp:reset
dsp:uart_open
dsp:boot ldr=@cctest_csmith_4c2338b1.0xab757f71.ldr timeout_ms=2500
dsp:uart_expect sentinel="got " timeout_ms=2500
delay ms=2500
dsp:uart_close
mark tag=cctest_run
```

Verify:

```
def check(extract_dir):
    uart = Verification.load_stream_text(extract_dir, 'dsp.uart')
    got = re.findall(r'got\s+([0-9a-fA-F]+)', uart)
    return bool(got) and int(got[-1], 16) == 0xab757f71
```

### cces csmith 3f5ea6f7 checksum

Fix the next focused draft runtime mismatch from the full foreach sweep:
`selache/xtest/build/drafts/cces/cctest_csmith_3f5ea6f7.0x7d4b5790.ldr`
boots and prints `got 46179bc7` on the DSP, but the source declares
`/* @expect 0x7d4b5790 */`. CCES diagnoses the same class of packed
struct / bitfield layout incompatibility here, so keep this step scoped
to removing the nonportable `#pragma pack` wrappers from this single
draft for all toolchains. Do not rewrite the expected checksum, delete
the draft, or duplicate the full sweep. The corrected CCES-built draft
must report the expected checksum on hardware.

Build:

```
make -C selache/xtest build/drafts/cces/cctest_csmith_3f5ea6f7.0x7d4b5790.ldr -j$(nproc)
```

Artifacts:

```
selache/xtest/build/drafts/cces/cctest_csmith_3f5ea6f7.0x7d4b5790.ldr
```

Test (max 1 min):

```
dsp:reset
dsp:uart_open
dsp:boot ldr=@cctest_csmith_3f5ea6f7.0x7d4b5790.ldr timeout_ms=2500
dsp:uart_expect sentinel="got " timeout_ms=2500
delay ms=2500
dsp:uart_close
mark tag=cctest_run
```

Verify:

```
def check(extract_dir):
    uart = Verification.load_stream_text(extract_dir, 'dsp.uart')
    got = re.findall(r'got\s+([0-9a-fA-F]+)', uart)
    return bool(got) and int(got[-1], 16) == 0x7d4b5790
```

### cces csmith 3f1fa455 checksum

Fix the first remaining draft runtime mismatch in the foreach sweep:
`selache/xtest/build/drafts/cces/cctest_csmith_3f1fa455.0x39f2cfc.ldr`
boots and prints `got b17e6505` on the DSP, but the source declares
`/* @expect 0x39f2cfc */`. CCES diagnoses the cause as a packed
bitfield layout that may be incompatible with gcc, so keep this step
scoped to removing that nonportable `#pragma pack` wrapper from this
single draft for all toolchains, without changing the expected value or
the remaining bitfield and aggregate stress. The corrected CCES-built
draft must report the expected checksum on hardware.

Build:

```
make -C selache/xtest build/drafts/cces/cctest_csmith_3f1fa455.0x39f2cfc.ldr -j$(nproc)
```

Artifacts:

```
selache/xtest/build/drafts/cces/cctest_csmith_3f1fa455.0x39f2cfc.ldr
```

Test (max 1 min):

```
dsp:reset
dsp:uart_open
dsp:boot ldr=@cctest_csmith_3f1fa455.0x39f2cfc.ldr timeout_ms=2500
dsp:uart_expect sentinel="got " timeout_ms=2500
delay ms=2500
dsp:uart_close
mark tag=cctest_run
```

Verify:

```
def check(extract_dir):
    uart = Verification.load_stream_text(extract_dir, 'dsp.uart')
    got = re.findall(r'got\s+([0-9a-fA-F]+)', uart)
    return bool(got) and int(got[-1], 16) == 0x39f2cfc
```

### cces csmith 025edc5d checksum

Fix the next focused draft runtime mismatch from the full foreach sweep:
`selache/xtest/build/drafts/cces/cctest_csmith_025edc5d.0x2634135d.ldr`
boots on the DSP but does not report the source's expected checksum
`/* @expect 0x2634135d */`. CCES diagnoses the same class of packed
struct / bitfield layout incompatibility here as in the precedent
`cctest_csmith_3f5ea6f7` step, so keep this step scoped to removing the
nonportable `#pragma pack` wrappers from this single draft for all
toolchains. The wrappers live at lines 793-794 and 801 of
`selache/xtest/draft_cases/cctest_csmith_025edc5d.c` and currently
bracket only `struct S0`. Host gcc and host clang already produce
`0x2634135d` both with and without those wrappers (verified with the
xtest `CFLAGS_HOST = -m32 -funsigned-char -std=c99 -w -O0`), so the
removal is checksum-preserving for the reference toolchains. Do not
rewrite the expected checksum, delete the draft, or duplicate the full
sweep. The corrected CCES-built draft must report the expected
checksum on hardware.

Build:

```
make -C selache/xtest build/drafts/cces/cctest_csmith_025edc5d.0x2634135d.ldr -j$(nproc)
```

Artifacts:

```
selache/xtest/build/drafts/cces/cctest_csmith_025edc5d.0x2634135d.ldr
```

Test (max 1 min):

```
dsp:reset
dsp:uart_open
dsp:boot ldr=@cctest_csmith_025edc5d.0x2634135d.ldr timeout_ms=2500
dsp:uart_expect sentinel="got " timeout_ms=2500
delay ms=2500
dsp:uart_close
mark tag=cctest_run
```

Verify:

```
def check(extract_dir):
    uart = Verification.load_stream_text(extract_dir, 'dsp.uart')
    got = re.findall(r'got\s+([0-9a-fA-F]+)', uart)
    return bool(got) and int(got[-1], 16) == 0x2634135d
```

### cces csmith 07baaacc checksum

Fix the next focused draft runtime mismatch from the full foreach sweep:
`selache/xtest/build/drafts/cces/cctest_csmith_07baaacc.0x35b6b6f7.ldr`
boots on the DSP but reports `got bdbbc7b4`, not the source's expected
checksum `/* @expect 0x35b6b6f7 */`. CCES diagnoses the same class of
packed struct / bitfield layout incompatibility here as in the
precedent `cctest_csmith_025edc5d` and `cctest_csmith_3f5ea6f7` steps,
so keep this step scoped to removing the nonportable `#pragma pack`
wrappers from this single draft for all toolchains. The wrappers live
in `selache/xtest/draft_cases/cctest_csmith_07baaacc.c` at five
push/pop pairs (around lines 803-814, 816-821, 831-840, 842-853, and
855-861) and bracket `struct S1`, `struct S2`, `struct S4`, `struct
S5`, and `struct S6`. Host gcc and host clang already produce
`0x35b6b6f7` both with and without those wrappers (verified with the
xtest `CFLAGS_HOST = -m32 -funsigned-char -std=c99 -w -O0` against the
xtest `host_wrap.c`), so the removal is checksum-preserving for the
reference toolchains. Do not rewrite the expected checksum, delete the
draft, or duplicate the full sweep. The corrected CCES-built draft
must report the expected checksum on hardware.

Build:

```
make -C selache/xtest build/drafts/cces/cctest_csmith_07baaacc.0x35b6b6f7.ldr -j$(nproc)
```

Artifacts:

```
selache/xtest/build/drafts/cces/cctest_csmith_07baaacc.0x35b6b6f7.ldr
```

Test (max 1 min):

```
dsp:reset
dsp:uart_open
dsp:boot ldr=@cctest_csmith_07baaacc.0x35b6b6f7.ldr timeout_ms=2500
dsp:uart_expect sentinel="got " timeout_ms=2500
delay ms=2500
dsp:uart_close
mark tag=cctest_run
```

Verify:

```
def check(extract_dir):
    uart = Verification.load_stream_text(extract_dir, 'dsp.uart')
    got = re.findall(r'got\s+([0-9a-fA-F]+)', uart)
    return bool(got) and int(got[-1], 16) == 0x35b6b6f7
```

### cces csmith 0e0cf3fc checksum

Fix the next focused draft runtime mismatch from the full foreach sweep:
`selache/xtest/build/drafts/cces/cctest_csmith_0e0cf3fc.0x53424b5c.ldr`
boots on the DSP but reports `got 8d19b0d8`, not the source's expected
checksum `/* @expect 0x53424b5c */`. CCES diagnoses the same class of
packed struct / bitfield layout incompatibility here as in the
precedent `cctest_csmith_07baaacc`, `cctest_csmith_025edc5d`, and
`cctest_csmith_3f5ea6f7` steps, so keep this step scoped to removing
the nonportable `#pragma pack` wrappers from this single draft for all
toolchains. The wrappers live in
`selache/xtest/draft_cases/cctest_csmith_0e0cf3fc.c` at two push/pop
pairs (around lines 793-804 and 806-813) and bracket `struct S0` and
`struct S1`, both of which contain bitfields. Host gcc and host clang
already produce `0x53424b5c` both with and without those wrappers
(verified with the xtest `CFLAGS_HOST = -m32 -funsigned-char -std=c99
-w -O0` against the xtest `host_wrap.c`), so the removal is
checksum-preserving for the reference toolchains. Do not rewrite the
expected checksum, delete the draft, or duplicate the full sweep. The
corrected CCES-built draft must report the expected checksum on
hardware.

Build:

```
make -C selache/xtest build/drafts/cces/cctest_csmith_0e0cf3fc.0x53424b5c.ldr -j$(nproc)
```

Artifacts:

```
selache/xtest/build/drafts/cces/cctest_csmith_0e0cf3fc.0x53424b5c.ldr
```

Test (max 1 min):

```
dsp:reset
dsp:uart_open
dsp:boot ldr=@cctest_csmith_0e0cf3fc.0x53424b5c.ldr timeout_ms=2500
dsp:uart_expect sentinel="got " timeout_ms=2500
delay ms=2500
dsp:uart_close
mark tag=cctest_run
```

Verify:

```
def check(extract_dir):
    uart = Verification.load_stream_text(extract_dir, 'dsp.uart')
    got = re.findall(r'got\s+([0-9a-fA-F]+)', uart)
    return bool(got) and int(got[-1], 16) == 0x53424b5c
```

### cces csmith 126ec2e5 checksum

Fix the next focused draft runtime mismatch from the full foreach sweep:
`selache/xtest/build/drafts/cces/cctest_csmith_126ec2e5.0x9ab6c2e8.ldr`
boots on the DSP but reports `got 4bc11295`, not the source's expected
checksum `/* @expect 0x9ab6c2e8 */`. CCES diagnoses the same class of
packed struct / bitfield layout incompatibility here as in the
precedent `cctest_csmith_07baaacc`, `cctest_csmith_025edc5d`,
`cctest_csmith_3f5ea6f7`, and `cctest_csmith_0e0cf3fc` steps, so keep
this step scoped to removing the nonportable `#pragma pack` wrappers
from this single draft for all toolchains. The wrappers live in
`selache/xtest/draft_cases/cctest_csmith_126ec2e5.c` at one push/pop
pair (around lines 793-805) and bracket `struct S0`, which contains
bitfields. Host gcc and host clang already produce `0x9ab6c2e8` both
with and without those wrappers (verified with the xtest `CFLAGS_HOST =
-m32 -funsigned-char -std=c99 -w -O0` against the xtest
`host_wrap.c`), so the removal is checksum-preserving for the reference
toolchains. Do not rewrite the expected checksum, delete the draft, or
duplicate the full sweep. The corrected CCES-built draft must report
the expected checksum on hardware.

Build:

```
make -C selache/xtest build/drafts/cces/cctest_csmith_126ec2e5.0x9ab6c2e8.ldr -j$(nproc)
```

Artifacts:

```
selache/xtest/build/drafts/cces/cctest_csmith_126ec2e5.0x9ab6c2e8.ldr
```

Test (max 1 min):

```
dsp:reset
dsp:uart_open
dsp:boot ldr=@cctest_csmith_126ec2e5.0x9ab6c2e8.ldr timeout_ms=2500
dsp:uart_expect sentinel="got " timeout_ms=2500
delay ms=2500
dsp:uart_close
mark tag=cctest_run
```

Verify:

```
def check(extract_dir):
    uart = Verification.load_stream_text(extract_dir, 'dsp.uart')
    got = re.findall(r'got\s+([0-9a-fA-F]+)', uart)
    return bool(got) and int(got[-1], 16) == 0x9ab6c2e8
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
