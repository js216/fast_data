# DD-FF direction ladder (DSP -> FPGA, 2 lane(s))
#### DD-FF 128B

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport_rx2
cd fpga && yosys -q -p "read_verilog verilog/sport_rx.v verilog/uart_tx.v; chparam -set N 2 -set MIN_DONE_WORDS 32 sport_rx; synth_ice40 -top sport_rx -json build/sport_rx2/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_rx2/s.json --pcf verilog/sport_rx_hx8k.pcf --asc build/sport_rx2/s.asc --freq 75 --timing-allow-fail --seed 20 -q --pcf-allow-unconstrained && icepack build/sport_rx2/s.asc build/sport_rx2/sport_rx2.bin
make -C adsp2156/sport_fpga_rx clean
make -j -C adsp2156/sport_fpga_rx CFLAGS_EXTRA="-DNCH=2U -DN_WORDS=32U -DDATA_INDEP_FS=1 -DHALF_WORDS=32768U -DSPORT_SCLK_HZ=59375000U"
cp adsp2156/sport_fpga_rx/build/main.ldr adsp2156/sport_fpga_rx/build/dma_128b.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_rx2/sport_rx2.bin
adsp2156/sport_fpga_rx/build/dma_128b.ldr
```

Test (max 14 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_rx2.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@dma_128b.ldr timeout_ms=15000
fpga.hx8k:uart_expect sentinel="sport_rx lanes=" timeout_ms=15000
delay ms=3000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=dd_ff_128b
```

Verify:

```
def _corruption_gate(extract_dir):
    # Any received-data error is a deterministic FAIL (jk 2026-06-11):
    # a corrupted word is a real defect, never a bench transient, so
    # retrying would only hide it. Scans the raw streams so it fires
    # even when the op timed out before the final report line.
    import sys
    for stream, pats in (
            ('dsp.uart', (r'rx h=\d+ e=(\d+)', r'rx_errors=(\d+)')),
            ('fpga.uart', (r'rx w=[0-9a-f]+ e=([0-9a-f]+)',
                           r'errors_hex=([0-9a-f]+)', r'(ERR) w='))):
        try:
            txt = Verification.load_stream_text(extract_dir, stream)
        except Exception:
            continue
        for pat in pats:
            for m in re.finditer(pat, txt):
                v = m.group(1)
                if v == 'ERR' or int(v, 16) != 0:
                    sys.stderr.write('\033[1;31mDATA CORRUPTION\033[0m '
                                     + stream + ': ' + m.group(0) + '\n')
                    raise HardFail('data corruption: '
                                   + stream + ' ' + m.group(0))


def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    _corruption_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'fpga.uart')
    m = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', text)
    if not m:
        raise HardFail('no sport_rx report')
    lanes, words, errors = int(m.group(1)), int(m.group(2), 16), int(m.group(3), 16)
    if lanes == 2 and errors == 0 and words >= 32 and m.group(4) == 'PASS':
        return True
    raise HardFail(f'FAIL: lanes={lanes} words={words} errors={errors}')
```

### DD-FF 1MiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport_rx2
cd fpga && yosys -q -p "read_verilog -D EYE_DELAY verilog/sport_rx.v verilog/uart_tx.v; chparam -set N 2 -set MIN_DONE_WORDS 262144 -set RESYNC 1 sport_rx; synth_ice40 -top sport_rx -json build/sport_rx2/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_rx2/s.json --pcf verilog/sport_rx_hx8k.pcf --asc build/sport_rx2/s.asc --freq 75 --timing-allow-fail --seed 20 -q --pcf-allow-unconstrained && icepack build/sport_rx2/s.asc build/sport_rx2/sport_rx2.bin
make -C adsp2156/sport_fpga_rx clean
make -j -C adsp2156/sport_fpga_rx CFLAGS_EXTRA="-DNCH=2U -DN_WORDS=262208U -DDATA_INDEP_FS=0 -DHALF_WORDS=32768U -DSPORT_SCLK_HZ=59375000U"
cp adsp2156/sport_fpga_rx/build/main.ldr adsp2156/sport_fpga_rx/build/dma_1mib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_rx2/sport_rx2.bin
adsp2156/sport_fpga_rx/build/dma_1mib.ldr
```

Test (max 14 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_rx2.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@dma_1mib.ldr timeout_ms=15000
fpga.hx8k:uart_expect sentinel="sport_rx lanes=" timeout_ms=15000
delay ms=3000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=dd_ff_1mib
```

Verify:

```
def _corruption_gate(extract_dir):
    # Any received-data error is a deterministic FAIL (jk 2026-06-11):
    # a corrupted word is a real defect, never a bench transient, so
    # retrying would only hide it. Scans the raw streams so it fires
    # even when the op timed out before the final report line.
    import sys
    for stream, pats in (
            ('dsp.uart', (r'rx h=\d+ e=(\d+)', r'rx_errors=(\d+)')),
            ('fpga.uart', (r'rx w=[0-9a-f]+ e=([0-9a-f]+)',
                           r'errors_hex=([0-9a-f]+)', r'(ERR) w='))):
        try:
            txt = Verification.load_stream_text(extract_dir, stream)
        except Exception:
            continue
        for pat in pats:
            for m in re.finditer(pat, txt):
                v = m.group(1)
                if v == 'ERR' or int(v, 16) != 0:
                    sys.stderr.write('\033[1;31mDATA CORRUPTION\033[0m '
                                     + stream + ': ' + m.group(0) + '\n')
                    raise HardFail('data corruption: '
                                   + stream + ' ' + m.group(0))


def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    _corruption_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'fpga.uart')
    m = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', text)
    if not m:
        raise HardFail('no sport_rx report')
    lanes, words, errors = int(m.group(1)), int(m.group(2), 16), int(m.group(3), 16)
    if lanes == 2 and errors == 0 and words >= 262144 and m.group(4) == 'PASS':
        return True
    raise HardFail(f'FAIL: lanes={lanes} words={words} errors={errors}')
```

### DD-FF 64MiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport_rx2
cd fpga && yosys -q -p "read_verilog -D EYE_DELAY verilog/sport_rx.v verilog/uart_tx.v; chparam -set N 2 -set MIN_DONE_WORDS 16777216 -set RESYNC 1 sport_rx; synth_ice40 -top sport_rx -json build/sport_rx2/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_rx2/s.json --pcf verilog/sport_rx_hx8k.pcf --asc build/sport_rx2/s.asc --freq 75 --timing-allow-fail --seed 20 -q --pcf-allow-unconstrained && icepack build/sport_rx2/s.asc build/sport_rx2/sport_rx2.bin
make -C adsp2156/sport_fpga_rx clean
make -j -C adsp2156/sport_fpga_rx CFLAGS_EXTRA="-DNCH=2U -DN_WORDS=16777280U -DDATA_INDEP_FS=0 -DHALF_WORDS=65536U -DSPORT_SCLK_HZ=59375000U"
cp adsp2156/sport_fpga_rx/build/main.ldr adsp2156/sport_fpga_rx/build/dma_64mib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_rx2/sport_rx2.bin
adsp2156/sport_fpga_rx/build/dma_64mib.ldr
```

Test (max 16 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_rx2.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@dma_64mib.ldr timeout_ms=15000
fpga.hx8k:uart_expect sentinel="sport_rx lanes=" timeout_ms=45000
delay ms=3000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=dd_ff_64mib
```

Verify:

```
def _corruption_gate(extract_dir):
    # Any received-data error is a deterministic FAIL (jk 2026-06-11):
    # a corrupted word is a real defect, never a bench transient, so
    # retrying would only hide it. Scans the raw streams so it fires
    # even when the op timed out before the final report line.
    import sys
    for stream, pats in (
            ('dsp.uart', (r'rx h=\d+ e=(\d+)', r'rx_errors=(\d+)')),
            ('fpga.uart', (r'rx w=[0-9a-f]+ e=([0-9a-f]+)',
                           r'errors_hex=([0-9a-f]+)', r'(ERR) w='))):
        try:
            txt = Verification.load_stream_text(extract_dir, stream)
        except Exception:
            continue
        for pat in pats:
            for m in re.finditer(pat, txt):
                v = m.group(1)
                if v == 'ERR' or int(v, 16) != 0:
                    sys.stderr.write('\033[1;31mDATA CORRUPTION\033[0m '
                                     + stream + ': ' + m.group(0) + '\n')
                    raise HardFail('data corruption: '
                                   + stream + ' ' + m.group(0))


def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    _corruption_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'fpga.uart')
    m = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', text)
    if not m:
        raise HardFail('no sport_rx report')
    lanes, words, errors = int(m.group(1)), int(m.group(2), 16), int(m.group(3), 16)
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'fpga.hx8k' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[0]['t_end'] - boots[0]['t_start']
    rate = int(words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'{rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if rate < 56250000:
        raise HardFail(f'rate {rate} < 50000000')
    if lanes == 2 and errors == 0 and words >= 16777216 and m.group(4) == 'PASS':
        return True
    raise HardFail(f'FAIL: lanes={lanes} words={words} errors={errors}')
```

### DD-FF 256MiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport_rx2
cd fpga && yosys -q -p "read_verilog -D EYE_DELAY verilog/sport_rx.v verilog/uart_tx.v; chparam -set N 2 -set MIN_DONE_WORDS 67108864 -set RESYNC 1 sport_rx; synth_ice40 -top sport_rx -json build/sport_rx2/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_rx2/s.json --pcf verilog/sport_rx_hx8k.pcf --asc build/sport_rx2/s.asc --freq 75 --timing-allow-fail --seed 20 -q --pcf-allow-unconstrained && icepack build/sport_rx2/s.asc build/sport_rx2/sport_rx2.bin
make -C adsp2156/sport_fpga_rx clean
make -j -C adsp2156/sport_fpga_rx CFLAGS_EXTRA="-DNCH=2U -DN_WORDS=67108928U -DDATA_INDEP_FS=0 -DHALF_WORDS=65536U -DSPORT_SCLK_HZ=59375000U"
cp adsp2156/sport_fpga_rx/build/main.ldr adsp2156/sport_fpga_rx/build/dma_256mib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_rx2/sport_rx2.bin
adsp2156/sport_fpga_rx/build/dma_256mib.ldr
```

Test (max 16 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_rx2.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@dma_256mib.ldr timeout_ms=15000
fpga.hx8k:uart_expect sentinel="sport_rx lanes=" timeout_ms=75000
delay ms=3000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=dd_ff_256mib
```

Verify:

```
def _corruption_gate(extract_dir):
    # Any received-data error is a deterministic FAIL (jk 2026-06-11):
    # a corrupted word is a real defect, never a bench transient, so
    # retrying would only hide it. Scans the raw streams so it fires
    # even when the op timed out before the final report line.
    import sys
    for stream, pats in (
            ('dsp.uart', (r'rx h=\d+ e=(\d+)', r'rx_errors=(\d+)')),
            ('fpga.uart', (r'rx w=[0-9a-f]+ e=([0-9a-f]+)',
                           r'errors_hex=([0-9a-f]+)', r'(ERR) w='))):
        try:
            txt = Verification.load_stream_text(extract_dir, stream)
        except Exception:
            continue
        for pat in pats:
            for m in re.finditer(pat, txt):
                v = m.group(1)
                if v == 'ERR' or int(v, 16) != 0:
                    sys.stderr.write('\033[1;31mDATA CORRUPTION\033[0m '
                                     + stream + ': ' + m.group(0) + '\n')
                    raise HardFail('data corruption: '
                                   + stream + ' ' + m.group(0))


def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    _corruption_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'fpga.uart')
    m = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', text)
    if not m:
        raise HardFail('no sport_rx report')
    lanes, words, errors = int(m.group(1)), int(m.group(2), 16), int(m.group(3), 16)
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'fpga.hx8k' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[0]['t_end'] - boots[0]['t_start']
    rate = int(words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'{rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if rate < 56250000:
        raise HardFail(f'rate {rate} < 58000000')
    if lanes == 2 and errors == 0 and words >= 67108864 and m.group(4) == 'PASS':
        return True
    raise HardFail(f'FAIL: lanes={lanes} words={words} errors={errors}')
```

### DD-FF 512MiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport_rx2
cd fpga && yosys -q -p "read_verilog -D EYE_DELAY verilog/sport_rx.v verilog/uart_tx.v; chparam -set N 2 -set MIN_DONE_WORDS 134217728 -set RESYNC 1 sport_rx; synth_ice40 -top sport_rx -json build/sport_rx2/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_rx2/s.json --pcf verilog/sport_rx_hx8k.pcf --asc build/sport_rx2/s.asc --freq 75 --timing-allow-fail --seed 20 -q --pcf-allow-unconstrained && icepack build/sport_rx2/s.asc build/sport_rx2/sport_rx2.bin
make -C adsp2156/sport_fpga_rx clean
make -j -C adsp2156/sport_fpga_rx CFLAGS_EXTRA="-DNCH=2U -DN_WORDS=134217792U -DDATA_INDEP_FS=0 -DHALF_WORDS=65536U -DSPORT_SCLK_HZ=59375000U"
cp adsp2156/sport_fpga_rx/build/main.ldr adsp2156/sport_fpga_rx/build/dma_512mib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_rx2/sport_rx2.bin
adsp2156/sport_fpga_rx/build/dma_512mib.ldr
```

Test (max 18 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_rx2.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@dma_512mib.ldr timeout_ms=15000
fpga.hx8k:uart_expect sentinel="sport_rx lanes=" timeout_ms=150000
delay ms=3000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=dd_ff_512mib
```

Verify:

```
def _corruption_gate(extract_dir):
    # Any received-data error is a deterministic FAIL (jk 2026-06-11):
    # a corrupted word is a real defect, never a bench transient, so
    # retrying would only hide it. Scans the raw streams so it fires
    # even when the op timed out before the final report line.
    import sys
    for stream, pats in (
            ('dsp.uart', (r'rx h=\d+ e=(\d+)', r'rx_errors=(\d+)')),
            ('fpga.uart', (r'rx w=[0-9a-f]+ e=([0-9a-f]+)',
                           r'errors_hex=([0-9a-f]+)', r'(ERR) w='))):
        try:
            txt = Verification.load_stream_text(extract_dir, stream)
        except Exception:
            continue
        for pat in pats:
            for m in re.finditer(pat, txt):
                v = m.group(1)
                if v == 'ERR' or int(v, 16) != 0:
                    sys.stderr.write('\033[1;31mDATA CORRUPTION\033[0m '
                                     + stream + ': ' + m.group(0) + '\n')
                    raise HardFail('data corruption: '
                                   + stream + ' ' + m.group(0))


def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    _corruption_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'fpga.uart')
    m = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', text)
    if not m:
        raise HardFail('no sport_rx report')
    lanes, words, errors = int(m.group(1)), int(m.group(2), 16), int(m.group(3), 16)
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'fpga.hx8k' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[0]['t_end'] - boots[0]['t_start']
    rate = int(words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'{rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if rate < 56250000:
        raise HardFail(f'rate {rate} < 58000000')
    if lanes == 2 and errors == 0 and words >= 134217728 and m.group(4) == 'PASS':
        return True
    raise HardFail(f'FAIL: lanes={lanes} words={words} errors={errors}')
```

### DD-FF 1GiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport_rx2
cd fpga && yosys -q -p "read_verilog -D EYE_DELAY verilog/sport_rx.v verilog/uart_tx.v; chparam -set N 2 -set MIN_DONE_WORDS 268435456 -set RESYNC 1 sport_rx; synth_ice40 -top sport_rx -json build/sport_rx2/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_rx2/s.json --pcf verilog/sport_rx_hx8k.pcf --asc build/sport_rx2/s.asc --freq 75 --timing-allow-fail --seed 20 -q --pcf-allow-unconstrained && icepack build/sport_rx2/s.asc build/sport_rx2/sport_rx2.bin
make -C adsp2156/sport_fpga_rx clean
make -j -C adsp2156/sport_fpga_rx CFLAGS_EXTRA="-DNCH=2U -DN_WORDS=268435520U -DDATA_INDEP_FS=0 -DHALF_WORDS=65536U -DSPORT_SCLK_HZ=59375000U"
cp adsp2156/sport_fpga_rx/build/main.ldr adsp2156/sport_fpga_rx/build/dma_1gib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_rx2/sport_rx2.bin
adsp2156/sport_fpga_rx/build/dma_1gib.ldr
```

Test (max 16 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_rx2.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@dma_1gib.ldr timeout_ms=15000
fpga.hx8k:uart_expect sentinel="sport_rx lanes=" timeout_ms=210000
delay ms=3000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=dd_ff_1gib
```

Verify:

```
def _corruption_gate(extract_dir):
    # Any received-data error is a deterministic FAIL (jk 2026-06-11):
    # a corrupted word is a real defect, never a bench transient, so
    # retrying would only hide it. Scans the raw streams so it fires
    # even when the op timed out before the final report line.
    import sys
    for stream, pats in (
            ('dsp.uart', (r'rx h=\d+ e=(\d+)', r'rx_errors=(\d+)')),
            ('fpga.uart', (r'rx w=[0-9a-f]+ e=([0-9a-f]+)',
                           r'errors_hex=([0-9a-f]+)', r'(ERR) w='))):
        try:
            txt = Verification.load_stream_text(extract_dir, stream)
        except Exception:
            continue
        for pat in pats:
            for m in re.finditer(pat, txt):
                v = m.group(1)
                if v == 'ERR' or int(v, 16) != 0:
                    sys.stderr.write('\033[1;31mDATA CORRUPTION\033[0m '
                                     + stream + ': ' + m.group(0) + '\n')
                    raise HardFail('data corruption: '
                                   + stream + ' ' + m.group(0))


def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    _corruption_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'fpga.uart')
    m = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', text)
    if not m:
        raise HardFail('no sport_rx report')
    lanes, words, errors = int(m.group(1)), int(m.group(2), 16), int(m.group(3), 16)
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'fpga.hx8k' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[0]['t_end'] - boots[0]['t_start']
    rate = int(words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'{rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if rate < 56250000:
        raise HardFail(f'rate {rate} < 58000000')
    if lanes == 2 and errors == 0 and words >= 268435456 and m.group(4) == 'PASS':
        return True
    raise HardFail(f'FAIL: lanes={lanes} words={words} errors={errors}')
```

### DD-FF 2GiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport_rx2
cd fpga && yosys -q -p "read_verilog -D EYE_DELAY verilog/sport_rx.v verilog/uart_tx.v; chparam -set N 2 -set MIN_DONE_WORDS 536870912 -set RESYNC 1 sport_rx; synth_ice40 -top sport_rx -json build/sport_rx2/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_rx2/s.json --pcf verilog/sport_rx_hx8k.pcf --asc build/sport_rx2/s.asc --freq 75 --timing-allow-fail --seed 20 -q --pcf-allow-unconstrained && icepack build/sport_rx2/s.asc build/sport_rx2/sport_rx2.bin
make -C adsp2156/sport_fpga_rx clean
make -j -C adsp2156/sport_fpga_rx CFLAGS_EXTRA="-DNCH=2U -DN_WORDS=536870976U -DDATA_INDEP_FS=0 -DHALF_WORDS=65536U -DSPORT_SCLK_HZ=59375000U"
cp adsp2156/sport_fpga_rx/build/main.ldr adsp2156/sport_fpga_rx/build/dma_2gib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_rx2/sport_rx2.bin
adsp2156/sport_fpga_rx/build/dma_2gib.ldr
```

Test (max 21 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_rx2.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@dma_2gib.ldr timeout_ms=15000
fpga.hx8k:uart_expect sentinel="sport_rx lanes=" timeout_ms=390000
delay ms=3000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=dd_ff_2gib
```

Verify:

```
def _corruption_gate(extract_dir):
    # Any received-data error is a deterministic FAIL (jk 2026-06-11):
    # a corrupted word is a real defect, never a bench transient, so
    # retrying would only hide it. Scans the raw streams so it fires
    # even when the op timed out before the final report line.
    import sys
    for stream, pats in (
            ('dsp.uart', (r'rx h=\d+ e=(\d+)', r'rx_errors=(\d+)')),
            ('fpga.uart', (r'rx w=[0-9a-f]+ e=([0-9a-f]+)',
                           r'errors_hex=([0-9a-f]+)', r'(ERR) w='))):
        try:
            txt = Verification.load_stream_text(extract_dir, stream)
        except Exception:
            continue
        for pat in pats:
            for m in re.finditer(pat, txt):
                v = m.group(1)
                if v == 'ERR' or int(v, 16) != 0:
                    sys.stderr.write('\033[1;31mDATA CORRUPTION\033[0m '
                                     + stream + ': ' + m.group(0) + '\n')
                    raise HardFail('data corruption: '
                                   + stream + ' ' + m.group(0))


def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    _corruption_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'fpga.uart')
    m = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', text)
    if not m:
        raise HardFail('no sport_rx report')
    lanes, words, errors = int(m.group(1)), int(m.group(2), 16), int(m.group(3), 16)
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'fpga.hx8k' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[0]['t_end'] - boots[0]['t_start']
    rate = int(words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'{rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if rate < 56250000:
        raise HardFail(f'rate {rate} < 60000000')
    if lanes == 2 and errors == 0 and words >= 536870912 and m.group(4) == 'PASS':
        return True
    raise HardFail(f'FAIL: lanes={lanes} words={words} errors={errors}')
```

### DD-FF 4GiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport_rx2
cd fpga && yosys -q -p "read_verilog -D EYE_DELAY verilog/sport_rx.v verilog/uart_tx.v; chparam -set N 2 -set MIN_DONE_WORDS 1073741824 -set RESYNC 1 sport_rx; synth_ice40 -top sport_rx -json build/sport_rx2/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_rx2/s.json --pcf verilog/sport_rx_hx8k.pcf --asc build/sport_rx2/s.asc --freq 75 --timing-allow-fail --seed 20 -q --pcf-allow-unconstrained && icepack build/sport_rx2/s.asc build/sport_rx2/sport_rx2.bin
make -C adsp2156/sport_fpga_rx clean
make -j -C adsp2156/sport_fpga_rx CFLAGS_EXTRA="-DNCH=2U -DN_WORDS=1073741888U -DDATA_INDEP_FS=0 -DHALF_WORDS=65536U -DSPORT_SCLK_HZ=59375000U"
cp adsp2156/sport_fpga_rx/build/main.ldr adsp2156/sport_fpga_rx/build/dma_4gib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_rx2/sport_rx2.bin
adsp2156/sport_fpga_rx/build/dma_4gib.ldr
```

Test (max 24 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_rx2.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@dma_4gib.ldr timeout_ms=15000
fpga.hx8k:uart_expect sentinel="sport_rx lanes=" timeout_ms=750000
delay ms=3000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=dd_ff_4gib
```

Verify:

```
def _corruption_gate(extract_dir):
    # Any received-data error is a deterministic FAIL (jk 2026-06-11):
    # a corrupted word is a real defect, never a bench transient, so
    # retrying would only hide it. Scans the raw streams so it fires
    # even when the op timed out before the final report line.
    import sys
    for stream, pats in (
            ('dsp.uart', (r'rx h=\d+ e=(\d+)', r'rx_errors=(\d+)')),
            ('fpga.uart', (r'rx w=[0-9a-f]+ e=([0-9a-f]+)',
                           r'errors_hex=([0-9a-f]+)', r'(ERR) w='))):
        try:
            txt = Verification.load_stream_text(extract_dir, stream)
        except Exception:
            continue
        for pat in pats:
            for m in re.finditer(pat, txt):
                v = m.group(1)
                if v == 'ERR' or int(v, 16) != 0:
                    sys.stderr.write('\033[1;31mDATA CORRUPTION\033[0m '
                                     + stream + ': ' + m.group(0) + '\n')
                    raise HardFail('data corruption: '
                                   + stream + ' ' + m.group(0))


def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    _corruption_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'fpga.uart')
    m = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', text)
    if not m:
        raise HardFail('no sport_rx report')
    lanes, words, errors = int(m.group(1)), int(m.group(2), 16), int(m.group(3), 16)
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'fpga.hx8k' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[0]['t_end'] - boots[0]['t_start']
    rate = int(words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'{rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if rate < 56250000:
        raise HardFail(f'rate {rate} < 60000000')
    if lanes == 2 and errors == 0 and words >= 1073741824 and m.group(4) == 'PASS':
        return True
    raise HardFail(f'FAIL: lanes={lanes} words={words} errors={errors}')
```

