# Selache core cctest sweep

Compile every promoted `selache/xtest/cases/cctest_*.c` through the
host toolchains and the Selache target toolchain. Host builds verify
correctness at build time. Target runs verify both the expected answer
and the hardware tick budget encoded in each source file.

Each promoted case must carry both:

```
/* @expect ... */
/* @exp_ticks ... */
```

### Selache core target sweep

Build:

```
cd selache && CARGO_TARGET_DIR=/home/agent1/fast_data/tmp/cargo-target cargo build --release
cd selache && CARGO_TARGET_DIR=/home/agent1/fast_data/tmp/cargo-target cargo test --all-targets
cd selache && CARGO_TARGET_DIR=/home/agent1/fast_data/tmp/cargo-target cargo clippy --all-targets --release -- -D warnings
CARGO_TARGET_DIR=/home/agent1/fast_data/tmp/cargo-target make -C selache/xtest clean
CARGO_TARGET_DIR=/home/agent1/fast_data/tmp/cargo-target make -C selache/xtest gcc -j$(nproc)
CARGO_TARGET_DIR=/home/agent1/fast_data/tmp/cargo-target make -C selache/xtest clang -j$(nproc)
CARGO_TARGET_DIR=/home/agent1/fast_data/tmp/cargo-target make -C selache/xtest sel -j$(nproc)
```

Foreach:

```
ldr in selache/xtest/build/sel/cctest_*.0x*.ldr
```

Test (max 60 sec):

```
dsp:reset
dsp:uart_open
dsp:boot ldr=@ldr timeout_ms=2500
dsp:uart_expect sentinel="start\r\n" timeout_ms=2500
dsp:uart_expect sentinel="got " timeout_ms=60000
scope:capture chans="C2"
dsp:uart_close
mark tag=cctest_core_run
```

Verify:

```
def check(extract_dir, ldr):
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    name = ldr.split('/')[-1]
    m = re.match(r'(cctest_.*)\.(0x[0-9a-fA-F]+)\.ldr$', name)
    if not m:
        return False
    source = '/home/agent1/fast_data/selache/xtest/cases/' + m.group(1) + '.c'
    with open(source) as f:
        src = f.read()
    em = re.search(r'@expect\s+(0x[0-9a-fA-F]+|[0-9]+)', src)
    tm = re.search(r'@exp_ticks\s+(0x[0-9a-fA-F]+|[0-9]+)', src)
    if not em or not tm:
        return False
    expect = int(em.group(1), 0)
    if int(m.group(2), 16) != expect:
        return False
    exp_ticks = int(tm.group(1), 0)
    uart = Verification.load_stream_text(extract_dir, 'dsp.uart')
    g = re.search(r'got\s+([0-9a-fA-F]+)\s+ticks\s+([0-9a-fA-F]+)', uart)
    if not g:
        return False
    if int(g.group(1), 16) != expect:
        return False
    ticks = int(g.group(2), 16)
    limit = (exp_ticks * 6 + 4) // 5
    if ticks <= 0 or ticks > limit:
        print(f'{name}: ticks 0x{ticks:x} exceed limit 0x{limit:x} from @exp_ticks 0x{exp_ticks:x}')
        return False
    return True
```
