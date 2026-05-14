# Selache core toolchain regression sweep

Compile every `selache/xtest/cases/cctest_*.c` through gcc, clang, and
the selache target toolchain. Verify host toolchains (gcc/clang) at
build time and verify the selache-built target artifacts by booting each
`.ldr` image on the SHARC+ board and matching the UART `got NN` against
the expected value encoded in the filename.

`cases/` is the locked, hand-promoted core suite. Candidates that
haven't been promoted yet live in `draft_cases/` and run via the
companion mission `selache-csmith-tests.md`.

### Static tests

Build the toolchain and run Cargo tests, then run the host (gcc/clang)
cases and fail the build on any mismatch.

Build:

```
cd selache && cargo clean
cd selache && cargo build --release
cd selache && cargo test --all-targets
cd selache && cargo clippy --all-targets --release -- -D warnings
make -C selache/xtest clean
make -C selache/xtest gcc -j$(nproc)
make -C selache/xtest clang -j$(nproc)
```

### Selache-built target sweep

Compile every cctest case through the selache target toolchain, emit
selache-built target images named `cctest_<case>.<expect>.ldr`, then
boot each image on the SHARC+ board and compare its UART output against
the expected value parsed from the filename.

Build:

```
make -C selache/xtest sel -j$(nproc)
```

Foreach:

```
ldr in selache/xtest/build/sel/cctest_*.0x*.ldr
```

Test (max 10 min):

```
dsp:reset
dsp:uart_open
dsp:boot ldr=@ldr timeout_ms=2500
dsp:uart_expect sentinel="got " timeout_ms=2500
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
