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
