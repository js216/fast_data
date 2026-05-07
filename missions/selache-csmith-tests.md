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
