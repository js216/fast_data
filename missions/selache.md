# Selache toolchain regression sweep

Compile every `selache/xtest/cases/cctest_*.c` through gcc, clang, cces,
and sel; verify host toolchains (gcc/clang) at build time and target
toolchains (cces/sel) by booting each `.ldr` image on the SHARC+ board
and matching the UART `got NN` against the expected value encoded in the
loader filename.

## WIP

### selache cctest sweep

Build cargo + selcc, compile every cctest case through all four
toolchains, run the host (gcc/clang) cases at build time and fail the
build on any mismatch, emit cces/sel loader images named
`cctest_<case>.<expect>.ldr`, then boot each loader on the SHARC+ board
and compare its UART output against the expected value parsed from the
filename.

Build:

```
cd selache && cargo build --release
cd selache && cargo test --all-targets
cd selache && cargo clippy --all-targets --release -- -D warnings
make -C selache/xtest gcc -j$(nproc)
make -C selache/xtest clang -j$(nproc)
make -C selache/xtest cces -j$(nproc)
make -C selache/xtest sel -j$(nproc)
```

Foreach:

```
ldr in selache/xtest/build/*/cctest_*.0x*.ldr
```

Test:

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
