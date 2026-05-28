# Selache perf draft reference timing

Temporary reference timing collector for `selache/xtest/draft_cases/cctest_*.c`.

### Selache perf draft reference timing

Build:

```
make -C selache/xtest drafts-cces -j$(nproc)
```

Foreach:

```
ldr in selache/xtest/build/drafts/cces/cctest_*.0x*.ldr
```

Test (max 2 min):

```
dsp:reset
dsp:uart_open
dsp:boot ldr=@ldr timeout_ms=2500
dsp:uart_expect sentinel="start\r\n" timeout_ms=2500
dsp:uart_expect sentinel="got " timeout_ms=60000
dsp:uart_close
mark tag=perf_ref_run
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
    g = re.search(r'got\s+([0-9a-fA-F]+)\s+ticks\s+([0-9a-fA-F]+)', uart)
    if not g:
        return False
    got = int(g.group(1), 16)
    ticks = int(g.group(2), 16)
    if got != expect or ticks <= 0:
        return False
    name = re.sub(r'\.0x[0-9a-fA-F]+\.ldr$', '.c', ldr.split('/')[-1])
    with open('/home/agent1/fast_data/tmp/selache-speed-ref-ticks.txt', 'a') as f:
        f.write(f'{name} 0x{ticks:x}\n')
    return True
```
