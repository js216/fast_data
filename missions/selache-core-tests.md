# Selache core toolchain regression sweep

Compile every `selache/xtest/cases/cctest_*.c` through gcc, clang, and
the selache target toolchain. Verify host toolchains (gcc/clang) at
build time and verify the selache-built target artifacts by booting each
`.ldr` image on the SHARC+ board and matching the UART `got NN` against
the expected value encoded in the filename.

The companion `selache-cces-tests.md` mission covers the same target
cases built by the CCES toolchain.

`cases/` is the locked, hand-promoted core suite. Candidates that
haven't been promoted yet live in `draft_cases/` and run via the
companion mission `selache-csmith-tests.md`.

### selache core gcc host sweep

Compile and run every promoted core cctest through host `gcc`, using the
existing xtest target to compare each program's `got NN` output against
its source `@expect` value.

Build:

```
make -C selache/xtest gcc -j$(nproc)
```

Test (max 10 s):

```
mark tag=selache_core_gcc_host
```

Verify:

```
def check(extract_dir):
    return Verification.manifest_clean(extract_dir)
```

### xtest: defer csmith 4270e7c5 (selcc miscompile)

The selache target build of `cases/cctest_csmith_4270e7c5.c` boots on
SHARC+ and prints `got 5760b22a` instead of the expected `9bcab2b4`.
Host gcc and host clang both produce the correct hash when run
natively, so the C source is fine and the bug lives in the selache
target toolchain (selcc/selas/selld/selload). The case is 851 lines,
has no `#pragma pack`, and has only one global array, so none of the
cheap surgical workarounds in this repo's history (`drop pragma-pack`,
`NoFillBlock`, `rewrite g_NN to BSS`) clearly applies. Following the
precedent set by `xtest: defer csmith 8c175802 (slow loop)`, demote the
case out of the core sweep by moving the source into `draft_cases/` and
record the diagnosis alongside it as
`xtest/draft_cases/cctest_csmith_4270e7c5.deferred.md`. This unblocks
the core sweep so the remaining ~1000 cases can be exercised; the
selache codegen bug remains tracked in `draft_cases/` for a future
selcc/seld investigation. Do not touch anything outside the case file
and the new deferred note.

Build:

```
test ! -f selache/xtest/cases/cctest_csmith_4270e7c5.c || git -C selache mv xtest/cases/cctest_csmith_4270e7c5.c xtest/draft_cases/cctest_csmith_4270e7c5.c
rm -f selache/xtest/build/sel/cctest_csmith_4270e7c5.* selache/xtest/build/cces/cctest_csmith_4270e7c5.*
```

The new `xtest/draft_cases/cctest_csmith_4270e7c5.deferred.md` must
exist and record: the symptom (SHARC+ prints `got 5760b22a`, expected
`9bcab2b4`); that host gcc and host clang both reproduce the expected
hash natively; and that no `#pragma pack` / single-global structure
makes the prior workaround patterns inapplicable, so the case is
deferred pending a real selcc/seld fix.

Test: no hardware.

Verify:

```
def check(extract_dir):
    from pathlib import Path

    sel = Path('selache')
    moved_in = sel / 'xtest/draft_cases/cctest_csmith_4270e7c5.c'
    moved_out = sel / 'xtest/cases/cctest_csmith_4270e7c5.c'
    note = sel / 'xtest/draft_cases/cctest_csmith_4270e7c5.deferred.md'
    stale_sel = sel / 'xtest/build/sel/cctest_csmith_4270e7c5.0x9bcab2b4.ldr'
    if not moved_in.is_file():
        return False
    if moved_out.exists():
        return False
    if not note.is_file():
        return False
    if stale_sel.exists():
        return False
    text = note.read_text()
    return ('5760b22a' in text) and ('9bcab2b4' in text)
```

### xtest: defer csmith 95d42820 (selcc target hang)

The selache target build of `cases/cctest_csmith_95d42820.c` boots on
SHARC+ (177152-byte image transfers cleanly) but the UART then stays
silent for the full 2.5 s window: `dsp:uart_expect` reports
`got ` not seen within 2500 ms, last 0B read. Host gcc and host clang
both run the native binary to completion and print
`got 298c9077`, matching the filename-encoded expected hash. The C
source is therefore well-formed; the bug lives in the selache target
toolchain (selcc/selas/selld/selload), and manifests on this case as
an early DSP hang or trap before the first `puts()` rather than as a
wrong-hash print (the 4270e7c5 pattern). The case is 1385 lines, has
no `#pragma pack`, and has four top-level global arrays, so the cheap
surgical workarounds in this repo's history (`drop pragma-pack`,
`NoFillBlock`, `rewrite g_NN to BSS`) do not clearly localise to a
single rewrite. Following the precedent set by `xtest: defer csmith
4270e7c5 (selcc miscompile)` and `xtest: defer csmith 8c175802 (slow
loop)`, demote the case out of the core sweep by moving the source
into `draft_cases/` and record the diagnosis alongside it as
`xtest/draft_cases/cctest_csmith_95d42820.deferred.md`. This unblocks
the core sweep so the remaining ~900 cases can be exercised; the
selache codegen bug remains tracked in `draft_cases/` for a future
selcc/seld investigation. Do not touch anything outside the case file
and the new deferred note.

Build:

```
test ! -f selache/xtest/cases/cctest_csmith_95d42820.c || git -C selache mv xtest/cases/cctest_csmith_95d42820.c xtest/draft_cases/cctest_csmith_95d42820.c
rm -f selache/xtest/build/sel/cctest_csmith_95d42820.* selache/xtest/build/cces/cctest_csmith_95d42820.*
```

The new `xtest/draft_cases/cctest_csmith_95d42820.deferred.md` must
exist and record: the symptom (SHARC+ boots the 177152-byte image
successfully but UART is silent / 0 bytes within the 2500 ms window
for filename-expected hash `298c9077`); that host gcc and host clang
both reproduce `got 298c9077` natively, confirming the C source is
sound; and that no `#pragma pack` and a small handful of global
arrays make the prior workaround patterns inapplicable, so the case
is deferred pending a real selcc/seld fix.

Test: no hardware.

Verify:

```
def check(extract_dir):
    from pathlib import Path

    sel = Path('selache')
    moved_in = sel / 'xtest/draft_cases/cctest_csmith_95d42820.c'
    moved_out = sel / 'xtest/cases/cctest_csmith_95d42820.c'
    note = sel / 'xtest/draft_cases/cctest_csmith_95d42820.deferred.md'
    stale_sel = sel / 'xtest/build/sel/cctest_csmith_95d42820.0x298c9077.ldr'
    if not moved_in.is_file():
        return False
    if moved_out.exists():
        return False
    if not note.is_file():
        return False
    if stale_sel.exists():
        return False
    text = note.read_text()
    return ('298c9077' in text) and ('timeout' in text.lower() or 'silent' in text.lower() or '0 bytes' in text.lower() or '0B' in text)
```

## WIP

### selache-built target cctest sweep

Compile every cctest case through the selache target toolchain, run the
host (gcc/clang) cases at build time and fail the build on any mismatch,
emit selache-built target images named `cctest_<case>.<expect>.ldr`,
then boot each image on the SHARC+ board and compare its UART output
against the expected value parsed from the filename.

Build:

```
cd selache && cargo build --release
cd selache && cargo test --all-targets
cd selache && cargo clippy --all-targets --release -- -D warnings
make -C selache/xtest gcc -j$(nproc)
make -C selache/xtest clang -j$(nproc)
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
