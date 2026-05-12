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

## Policy: fix the toolchain, never demote the case

Per AGENTS.md "Root cause only": when the bench sweep fails on a
case, the only acceptable remediation is a root-cause fix in
`selache/` (selcc, selas, seld, selload, or libsel as appropriate)
so the same case passes on the next sweep. The Minimizer must reject
any proposed sub-step that:

- moves the failing case from `xtest/cases/` into `xtest/draft_cases/`;
- adds a `.deferred.md` note or per-case bypass under WIP;
- deletes or excludes the case's `.ldr` from the build output;
- edits `xtest/Makefile` or `xtest/build_rules.*` to skip the case;
- modifies the case's `.c` source to dodge the failure (the host
  gcc / host clang sweep already validates each case's source; a
  selache-target-only failure means the bug is in the toolchain, not
  the source);
- or any equivalent that hides the failure without correcting the
  toolchain.

The `## WIP` marker advances only after a real toolchain change
makes a previously-failing case pass on the bench. Cases already in
`xtest/draft_cases/` with `.deferred.md` notes (currently
`cctest_csmith_4270e7c5`, `cctest_csmith_95d42820`,
`cctest_csmith_cb987b7b`, `cctest_csmith_8c175802`) predate this
policy and remain there as historical workarounds; each is unblocked
only when a corresponding selache root-cause fix lands, after which
the case is re-promoted into `xtest/cases/`.

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
