# Selache csmith draft regression sweep

Validate randomly-generated cctest candidates in
`selache/xtest/draft_cases/` against gcc, clang, cces, and sel before
they get hand-promoted into the locked `cases/` core suite. Same
plan/verify shape as the core sweep (companion mission
`selache-core-tests.md`); the only deltas are the source directory
(`draft_cases/` instead of `cases/`) and the build/output prefix
(`build/drafts/` instead of `build/`).

Vacuously passes when `draft_cases/` is empty. Otherwise: every draft
must pass on all four toolchains before any of them get promoted.

## WIP

### temporary: recover stopped sel fault debug

Remove this temporary task once the underlying sel fault is reduced and
fixed. The prior iteration stopped after confirming a real hardware
fault instead of continuing to reduction/fix, which is a process bug.
Known evidence:

- `selache/xtest/build/drafts/sel/cctest_csmith_0e13b955.0x66e2d201.ldr`
  boots with empty UART and `C2 DSP_FAULT` duty cycle `100.0%`.
- The same source built by CCES,
  `selache/xtest/build/drafts/cces/cctest_csmith_0e13b955.0x66e2d201.ldr`,
  prints `got 66e2d201` and measures `C2 DSP_FAULT` duty cycle `0.0%`.
- No leases are currently held.

Next worker should reduce `draft_cases/cctest_csmith_0e13b955.c` to the
smallest sel-built program that still faults, fix the sel compiler or
runtime bug, then delete this temporary task and rerun the full draft
sweep below.

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
dsp:boot ldr=@ldr
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
