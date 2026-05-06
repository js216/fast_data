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
    g = re.search(r'got\s+([0-9a-fA-F]+)', uart)
    return bool(g) and int(g.group(1), 16) == expect
```
