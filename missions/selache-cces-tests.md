# Selache CCES target regression sweep

Compile every `selache/xtest/cases/cctest_*.c` through the CCES target
toolchain, boot each `.ldr` image on the SHARC+ board, and match the
UART `got NN` against the expected value encoded in the filename.

This mission is the CCES-built counterpart to the selache-built target
sweep in `selache-core-tests.md`.

## WIP

### CCES-built target cctest sweep

Compile every promoted core cctest case through the CCES target
toolchain, emit images named `cctest_<case>.<expect>.ldr`, then boot
each image on the SHARC+ board and compare its UART output against the
expected value parsed from the filename.

Build:

```
make -C selache/xtest cces -j$(nproc)
```

Foreach:

```
ldr in selache/xtest/build/cces/cctest_*.0x*.ldr
```

Test (max 10 min):

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
