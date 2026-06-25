# DDDD-FFFF direction ladder (DSP -> FPGA, 4 lane(s))
#### DDDD-FFFF 128B

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
make -C fpga sport-verilog
mkdir -p fpga/build/sport_bidir_4xrx
cd fpga && yosys -q -p "read_verilog -D EYE_DELAY verilog/sport_tx_sync_nopll.v verilog/sport_tx_prbs_ser.v verilog/sport_rx.v verilog/sport_bidir.v verilog/uart_tx.v; chparam -set TX_TO_DSP_N 1 -set RX_FROM_DSP_N 4 -set SYNC_TX 1 -set NOPLL 1 -set FROM_DSP_EN 1 -set REPORT_LANE0 0 -set MIN_DONE_WORDS 32 sport_bidir; synth_ice40 -top sport_bidir; setattr -unset src; write_json build/sport_bidir_4xrx/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_bidir_4xrx/s.json --pcf verilog/sport_bidir_4xrx_hx8k.pcf --asc build/sport_bidir_4xrx/s.asc --freq 75 --timing-allow-fail --seed 20 -q --pcf-allow-unconstrained && icepack build/sport_bidir_4xrx/s.asc build/sport_bidir_4xrx/sport_bidir_4xrx.bin
make -C adsp2156/sport clean
make -j -C adsp2156/sport CFLAGS_EXTRA="-DRX_N=0U -DTX_N=4U -DTOTAL_WORDS=32U -DTX_FIRST -DSPORT_SCLK_HZ=57291667U -DSPORT_CLKDIV=0U -DFPGA_LOAD_DELAY_MS=12000U"
cp adsp2156/sport/build/main.ldr adsp2156/sport/build/dma_128b.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_bidir_4xrx/sport_bidir_4xrx.bin
adsp2156/sport/build/dma_128b.ldr
```

Test (max 14 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@blinky.bin
dsp:uart_open
dsp:boot ldr=@dma_128b.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_bidir_concurrent" timeout_ms=10000
fpga.hx8k:program bin=@sport_bidir_4xrx.bin
fpga.hx8k:uart_open
fpga.hx8k:uart_expect sentinel="sport_rx lanes=" timeout_ms=15000
delay ms=3000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=dddd_ffff_128b
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


def _liveness_gate(extract_dir):
    # jk: HARD fail (no retry) if any heartbeat is >5 s late -- a >5 s GAP in the
    # live heartbeat stream while the transfer runs. Heartbeats (tx h=, rx h=,
    # rx w=) fire every 8 MiB, so a sub-8 MiB transfer emits none and is fine as
    # long as it completed (final report present); no heartbeats AND no report is
    # a dead link.
    import os
    try:
        _tl = open(os.path.join(extract_dir, 'timeline.log'),
                   encoding='ascii', errors='replace').read().splitlines()
    except OSError:
        raise HardFail('liveness: no timeline.log to verify heartbeats')
    _hb = re.compile(r'(?:tx h=\d+|rx h=\d+|rx w=[0-9a-fA-F]+)')
    _rep = re.compile(r'sport_rx lanes=|sport_bidir rx_lanes=')
    _row = re.compile(r'^\S+\s+([0-9]+\.[0-9]+)\s+>\s+STREAM\s+(?:dsp|fpga)\.uart')
    _hbs = []
    _rt = None
    for _ln in _tl:
        _m = _row.match(_ln)
        if not _m:
            continue
        _t = float(_m.group(1))
        if _hb.search(_ln):
            _hbs.append(_t)
        if _rt is None and _rep.search(_ln):
            _rt = _t
    _hbs.sort()
    for _a, _b in zip(_hbs, _hbs[1:]):
        if _b - _a > 5.0:
            raise HardFail('liveness: heartbeat gap %.1fs > 5.0s (stall near t=%.1fs)'
                           % (_b - _a, _a))
    if _hbs:
        if _rt is None:
            raise HardFail('liveness: heartbeats stopped with no completion report -- stalled')
        if _rt - _hbs[-1] > 5.0:
            raise HardFail('liveness: %.1fs from last heartbeat to report > 5.0s -- stalled near end'
                           % (_rt - _hbs[-1]))
    elif _rt is None:
        raise HardFail('liveness: no heartbeats and no completion report -- link never came alive')


def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    _corruption_gate(extract_dir)
    _liveness_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'fpga.uart')
    m = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', text)
    if not m:
        raise HardFail('no sport_rx report')
    lanes, words, errors = int(m.group(1)), int(m.group(2), 16), int(m.group(3), 16)
    if lanes == 4 and errors == 0 and words >= 32 and m.group(4) == 'PASS':
        return True
    raise HardFail(f'FAIL: lanes={lanes} words={words} errors={errors}')
```

### DDDD-FFFF 1MiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
make -C fpga sport-verilog
mkdir -p fpga/build/sport_bidir_4xrx
cd fpga && yosys -q -p "read_verilog -D EYE_DELAY verilog/sport_tx_sync_nopll.v verilog/sport_tx_prbs_ser.v verilog/sport_rx.v verilog/sport_bidir.v verilog/uart_tx.v; chparam -set TX_TO_DSP_N 1 -set RX_FROM_DSP_N 4 -set SYNC_TX 1 -set NOPLL 1 -set FROM_DSP_EN 1 -set REPORT_LANE0 0 -set MIN_DONE_WORDS 262144 sport_bidir; synth_ice40 -top sport_bidir; setattr -unset src; write_json build/sport_bidir_4xrx/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_bidir_4xrx/s.json --pcf verilog/sport_bidir_4xrx_hx8k.pcf --asc build/sport_bidir_4xrx/s.asc --freq 75 --timing-allow-fail --seed 20 -q --pcf-allow-unconstrained && icepack build/sport_bidir_4xrx/s.asc build/sport_bidir_4xrx/sport_bidir_4xrx.bin
make -C adsp2156/sport clean
make -j -C adsp2156/sport CFLAGS_EXTRA="-DRX_N=0U -DTX_N=4U -DTOTAL_WORDS=262208U -DTX_FIRST -DSPORT_SCLK_HZ=57291667U -DSPORT_CLKDIV=0U -DFPGA_LOAD_DELAY_MS=12000U"
cp adsp2156/sport/build/main.ldr adsp2156/sport/build/dma_1mib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_bidir_4xrx/sport_bidir_4xrx.bin
adsp2156/sport/build/dma_1mib.ldr
```

Test (max 14 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@blinky.bin
dsp:uart_open
dsp:boot ldr=@dma_1mib.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_bidir_concurrent" timeout_ms=10000
fpga.hx8k:program bin=@sport_bidir_4xrx.bin
fpga.hx8k:uart_open
fpga.hx8k:uart_expect sentinel="sport_rx lanes=" timeout_ms=15000
delay ms=3000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=dddd_ffff_1mib
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


def _liveness_gate(extract_dir):
    # jk: HARD fail (no retry) if any heartbeat is >5 s late -- a >5 s GAP in the
    # live heartbeat stream while the transfer runs. Heartbeats (tx h=, rx h=,
    # rx w=) fire every 8 MiB, so a sub-8 MiB transfer emits none and is fine as
    # long as it completed (final report present); no heartbeats AND no report is
    # a dead link.
    import os
    try:
        _tl = open(os.path.join(extract_dir, 'timeline.log'),
                   encoding='ascii', errors='replace').read().splitlines()
    except OSError:
        raise HardFail('liveness: no timeline.log to verify heartbeats')
    _hb = re.compile(r'(?:tx h=\d+|rx h=\d+|rx w=[0-9a-fA-F]+)')
    _rep = re.compile(r'sport_rx lanes=|sport_bidir rx_lanes=')
    _row = re.compile(r'^\S+\s+([0-9]+\.[0-9]+)\s+>\s+STREAM\s+(?:dsp|fpga)\.uart')
    _hbs = []
    _rt = None
    for _ln in _tl:
        _m = _row.match(_ln)
        if not _m:
            continue
        _t = float(_m.group(1))
        if _hb.search(_ln):
            _hbs.append(_t)
        if _rt is None and _rep.search(_ln):
            _rt = _t
    _hbs.sort()
    for _a, _b in zip(_hbs, _hbs[1:]):
        if _b - _a > 5.0:
            raise HardFail('liveness: heartbeat gap %.1fs > 5.0s (stall near t=%.1fs)'
                           % (_b - _a, _a))
    if _hbs:
        if _rt is None:
            raise HardFail('liveness: heartbeats stopped with no completion report -- stalled')
        if _rt - _hbs[-1] > 5.0:
            raise HardFail('liveness: %.1fs from last heartbeat to report > 5.0s -- stalled near end'
                           % (_rt - _hbs[-1]))
    elif _rt is None:
        raise HardFail('liveness: no heartbeats and no completion report -- link never came alive')


def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    _corruption_gate(extract_dir)
    _liveness_gate(extract_dir)
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
    _xs = None
    try:
        import os as _os, re as _re
        for _ln in open(_os.path.join(extract_dir, 'timeline.log'), encoding='utf-8', errors='replace'):
            _mm = _re.match(r"^\S+\s+([0-9]+\.[0-9]+)\s+>\s+STREAM\s+dsp\.uart\b", _ln)
            if _mm and 'xfer' in _ln:
                _xs = float(_mm.group(1)); break
    except (OSError, ImportError):
        pass
    elapsed = (expects[-1]['t_end'] - (_xs if _xs is not None else boots[0]['t_start'])) if (boots and expects) else 0
    rate = int(words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'{rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if lanes == 4 and errors == 0 and words >= 262144 and m.group(4) == 'PASS':
        return True
    raise HardFail(f'FAIL: lanes={lanes} words={words} errors={errors}')
```

### DDDD-FFFF 64MiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
make -C fpga sport-verilog
mkdir -p fpga/build/sport_bidir_4xrx
cd fpga && yosys -q -p "read_verilog -D EYE_DELAY verilog/sport_tx_sync_nopll.v verilog/sport_tx_prbs_ser.v verilog/sport_rx.v verilog/sport_bidir.v verilog/uart_tx.v; chparam -set TX_TO_DSP_N 1 -set RX_FROM_DSP_N 4 -set SYNC_TX 1 -set NOPLL 1 -set FROM_DSP_EN 1 -set REPORT_LANE0 0 -set MIN_DONE_WORDS 16777216 sport_bidir; synth_ice40 -top sport_bidir; setattr -unset src; write_json build/sport_bidir_4xrx/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_bidir_4xrx/s.json --pcf verilog/sport_bidir_4xrx_hx8k.pcf --asc build/sport_bidir_4xrx/s.asc --freq 75 --timing-allow-fail --seed 20 -q --pcf-allow-unconstrained && icepack build/sport_bidir_4xrx/s.asc build/sport_bidir_4xrx/sport_bidir_4xrx.bin
make -C adsp2156/sport clean
make -j -C adsp2156/sport CFLAGS_EXTRA="-DRX_N=0U -DTX_N=4U -DTOTAL_WORDS=16777280U -DTX_FIRST -DSPORT_SCLK_HZ=57291667U -DSPORT_CLKDIV=0U -DFPGA_LOAD_DELAY_MS=12000U"
cp adsp2156/sport/build/main.ldr adsp2156/sport/build/dma_64mib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_bidir_4xrx/sport_bidir_4xrx.bin
adsp2156/sport/build/dma_64mib.ldr
```

Test (max 16 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@blinky.bin
dsp:uart_open
dsp:boot ldr=@dma_64mib.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_bidir_concurrent" timeout_ms=10000
fpga.hx8k:program bin=@sport_bidir_4xrx.bin
fpga.hx8k:uart_open
fpga.hx8k:uart_expect sentinel="sport_rx lanes=" timeout_ms=45000
delay ms=3000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=dddd_ffff_64mib
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


def _liveness_gate(extract_dir):
    # jk: HARD fail (no retry) if any heartbeat is >5 s late -- a >5 s GAP in the
    # live heartbeat stream while the transfer runs. Heartbeats (tx h=, rx h=,
    # rx w=) fire every 8 MiB, so a sub-8 MiB transfer emits none and is fine as
    # long as it completed (final report present); no heartbeats AND no report is
    # a dead link.
    import os
    try:
        _tl = open(os.path.join(extract_dir, 'timeline.log'),
                   encoding='ascii', errors='replace').read().splitlines()
    except OSError:
        raise HardFail('liveness: no timeline.log to verify heartbeats')
    _hb = re.compile(r'(?:tx h=\d+|rx h=\d+|rx w=[0-9a-fA-F]+)')
    _rep = re.compile(r'sport_rx lanes=|sport_bidir rx_lanes=')
    _row = re.compile(r'^\S+\s+([0-9]+\.[0-9]+)\s+>\s+STREAM\s+(?:dsp|fpga)\.uart')
    _hbs = []
    _rt = None
    for _ln in _tl:
        _m = _row.match(_ln)
        if not _m:
            continue
        _t = float(_m.group(1))
        if _hb.search(_ln):
            _hbs.append(_t)
        if _rt is None and _rep.search(_ln):
            _rt = _t
    _hbs.sort()
    for _a, _b in zip(_hbs, _hbs[1:]):
        if _b - _a > 5.0:
            raise HardFail('liveness: heartbeat gap %.1fs > 5.0s (stall near t=%.1fs)'
                           % (_b - _a, _a))
    if _hbs:
        if _rt is None:
            raise HardFail('liveness: heartbeats stopped with no completion report -- stalled')
        if _rt - _hbs[-1] > 5.0:
            raise HardFail('liveness: %.1fs from last heartbeat to report > 5.0s -- stalled near end'
                           % (_rt - _hbs[-1]))
    elif _rt is None:
        raise HardFail('liveness: no heartbeats and no completion report -- link never came alive')


def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    _corruption_gate(extract_dir)
    _liveness_gate(extract_dir)
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
    _xs = None
    try:
        import os as _os, re as _re
        for _ln in open(_os.path.join(extract_dir, 'timeline.log'), encoding='utf-8', errors='replace'):
            _mm = _re.match(r"^\S+\s+([0-9]+\.[0-9]+)\s+>\s+STREAM\s+dsp\.uart\b", _ln)
            if _mm and 'xfer' in _ln:
                _xs = float(_mm.group(1)); break
    except (OSError, ImportError):
        pass
    elapsed = expects[0]['t_end'] - (_xs if _xs is not None else boots[0]['t_start'])
    rate = int(words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'{rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if lanes == 4 and errors == 0 and words >= 16777216 and m.group(4) == 'PASS':
        return True
    raise HardFail(f'FAIL: lanes={lanes} words={words} errors={errors}')
```

### DDDD-FFFF 256MiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
make -C fpga sport-verilog
mkdir -p fpga/build/sport_bidir_4xrx
cd fpga && yosys -q -p "read_verilog -D EYE_DELAY verilog/sport_tx_sync_nopll.v verilog/sport_tx_prbs_ser.v verilog/sport_rx.v verilog/sport_bidir.v verilog/uart_tx.v; chparam -set TX_TO_DSP_N 1 -set RX_FROM_DSP_N 4 -set SYNC_TX 1 -set NOPLL 1 -set FROM_DSP_EN 1 -set REPORT_LANE0 0 -set MIN_DONE_WORDS 67108864 sport_bidir; synth_ice40 -top sport_bidir; setattr -unset src; write_json build/sport_bidir_4xrx/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_bidir_4xrx/s.json --pcf verilog/sport_bidir_4xrx_hx8k.pcf --asc build/sport_bidir_4xrx/s.asc --freq 75 --timing-allow-fail --seed 20 -q --pcf-allow-unconstrained && icepack build/sport_bidir_4xrx/s.asc build/sport_bidir_4xrx/sport_bidir_4xrx.bin
make -C adsp2156/sport clean
make -j -C adsp2156/sport CFLAGS_EXTRA="-DRX_N=0U -DTX_N=4U -DTOTAL_WORDS=67108928U -DTX_FIRST -DSPORT_SCLK_HZ=57291667U -DSPORT_CLKDIV=0U -DFPGA_LOAD_DELAY_MS=12000U"
cp adsp2156/sport/build/main.ldr adsp2156/sport/build/dma_256mib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_bidir_4xrx/sport_bidir_4xrx.bin
adsp2156/sport/build/dma_256mib.ldr
```

Test (max 16 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@blinky.bin
dsp:uart_open
dsp:boot ldr=@dma_256mib.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_bidir_concurrent" timeout_ms=10000
fpga.hx8k:program bin=@sport_bidir_4xrx.bin
fpga.hx8k:uart_open
fpga.hx8k:uart_expect sentinel="sport_rx lanes=" timeout_ms=75000
delay ms=3000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=dddd_ffff_256mib
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


def _liveness_gate(extract_dir):
    # jk: HARD fail (no retry) if any heartbeat is >5 s late -- a >5 s GAP in the
    # live heartbeat stream while the transfer runs. Heartbeats (tx h=, rx h=,
    # rx w=) fire every 8 MiB, so a sub-8 MiB transfer emits none and is fine as
    # long as it completed (final report present); no heartbeats AND no report is
    # a dead link.
    import os
    try:
        _tl = open(os.path.join(extract_dir, 'timeline.log'),
                   encoding='ascii', errors='replace').read().splitlines()
    except OSError:
        raise HardFail('liveness: no timeline.log to verify heartbeats')
    _hb = re.compile(r'(?:tx h=\d+|rx h=\d+|rx w=[0-9a-fA-F]+)')
    _rep = re.compile(r'sport_rx lanes=|sport_bidir rx_lanes=')
    _row = re.compile(r'^\S+\s+([0-9]+\.[0-9]+)\s+>\s+STREAM\s+(?:dsp|fpga)\.uart')
    _hbs = []
    _rt = None
    for _ln in _tl:
        _m = _row.match(_ln)
        if not _m:
            continue
        _t = float(_m.group(1))
        if _hb.search(_ln):
            _hbs.append(_t)
        if _rt is None and _rep.search(_ln):
            _rt = _t
    _hbs.sort()
    for _a, _b in zip(_hbs, _hbs[1:]):
        if _b - _a > 5.0:
            raise HardFail('liveness: heartbeat gap %.1fs > 5.0s (stall near t=%.1fs)'
                           % (_b - _a, _a))
    if _hbs:
        if _rt is None:
            raise HardFail('liveness: heartbeats stopped with no completion report -- stalled')
        if _rt - _hbs[-1] > 5.0:
            raise HardFail('liveness: %.1fs from last heartbeat to report > 5.0s -- stalled near end'
                           % (_rt - _hbs[-1]))
    elif _rt is None:
        raise HardFail('liveness: no heartbeats and no completion report -- link never came alive')


def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    _corruption_gate(extract_dir)
    _liveness_gate(extract_dir)
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
    _xs = None
    try:
        import os as _os, re as _re
        for _ln in open(_os.path.join(extract_dir, 'timeline.log'), encoding='utf-8', errors='replace'):
            _mm = _re.match(r"^\S+\s+([0-9]+\.[0-9]+)\s+>\s+STREAM\s+dsp\.uart\b", _ln)
            if _mm and 'xfer' in _ln:
                _xs = float(_mm.group(1)); break
    except (OSError, ImportError):
        pass
    elapsed = expects[0]['t_end'] - (_xs if _xs is not None else boots[0]['t_start'])
    rate = int(words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'{rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if rate < 56250000:
        raise HardFail(f'rate {rate} < 56250000')
    if lanes == 4 and errors == 0 and words >= 67108864 and m.group(4) == 'PASS':
        return True
    raise HardFail(f'FAIL: lanes={lanes} words={words} errors={errors}')
```

### DDDD-FFFF 512MiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
make -C fpga sport-verilog
mkdir -p fpga/build/sport_bidir_4xrx
cd fpga && yosys -q -p "read_verilog -D EYE_DELAY verilog/sport_tx_sync_nopll.v verilog/sport_tx_prbs_ser.v verilog/sport_rx.v verilog/sport_bidir.v verilog/uart_tx.v; chparam -set TX_TO_DSP_N 1 -set RX_FROM_DSP_N 4 -set SYNC_TX 1 -set NOPLL 1 -set FROM_DSP_EN 1 -set REPORT_LANE0 0 -set MIN_DONE_WORDS 134217728 sport_bidir; synth_ice40 -top sport_bidir; setattr -unset src; write_json build/sport_bidir_4xrx/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_bidir_4xrx/s.json --pcf verilog/sport_bidir_4xrx_hx8k.pcf --asc build/sport_bidir_4xrx/s.asc --freq 75 --timing-allow-fail --seed 20 -q --pcf-allow-unconstrained && icepack build/sport_bidir_4xrx/s.asc build/sport_bidir_4xrx/sport_bidir_4xrx.bin
make -C adsp2156/sport clean
make -j -C adsp2156/sport CFLAGS_EXTRA="-DRX_N=0U -DTX_N=4U -DTOTAL_WORDS=134217792U -DTX_FIRST -DSPORT_SCLK_HZ=57291667U -DSPORT_CLKDIV=0U -DFPGA_LOAD_DELAY_MS=12000U"
cp adsp2156/sport/build/main.ldr adsp2156/sport/build/dma_512mib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_bidir_4xrx/sport_bidir_4xrx.bin
adsp2156/sport/build/dma_512mib.ldr
```

Test (max 18 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@blinky.bin
dsp:uart_open
dsp:boot ldr=@dma_512mib.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_bidir_concurrent" timeout_ms=10000
fpga.hx8k:program bin=@sport_bidir_4xrx.bin
fpga.hx8k:uart_open
fpga.hx8k:uart_expect sentinel="sport_rx lanes=" timeout_ms=150000
delay ms=3000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=dddd_ffff_512mib
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


def _liveness_gate(extract_dir):
    # jk: HARD fail (no retry) if any heartbeat is >5 s late -- a >5 s GAP in the
    # live heartbeat stream while the transfer runs. Heartbeats (tx h=, rx h=,
    # rx w=) fire every 8 MiB, so a sub-8 MiB transfer emits none and is fine as
    # long as it completed (final report present); no heartbeats AND no report is
    # a dead link.
    import os
    try:
        _tl = open(os.path.join(extract_dir, 'timeline.log'),
                   encoding='ascii', errors='replace').read().splitlines()
    except OSError:
        raise HardFail('liveness: no timeline.log to verify heartbeats')
    _hb = re.compile(r'(?:tx h=\d+|rx h=\d+|rx w=[0-9a-fA-F]+)')
    _rep = re.compile(r'sport_rx lanes=|sport_bidir rx_lanes=')
    _row = re.compile(r'^\S+\s+([0-9]+\.[0-9]+)\s+>\s+STREAM\s+(?:dsp|fpga)\.uart')
    _hbs = []
    _rt = None
    for _ln in _tl:
        _m = _row.match(_ln)
        if not _m:
            continue
        _t = float(_m.group(1))
        if _hb.search(_ln):
            _hbs.append(_t)
        if _rt is None and _rep.search(_ln):
            _rt = _t
    _hbs.sort()
    for _a, _b in zip(_hbs, _hbs[1:]):
        if _b - _a > 5.0:
            raise HardFail('liveness: heartbeat gap %.1fs > 5.0s (stall near t=%.1fs)'
                           % (_b - _a, _a))
    if _hbs:
        if _rt is None:
            raise HardFail('liveness: heartbeats stopped with no completion report -- stalled')
        if _rt - _hbs[-1] > 5.0:
            raise HardFail('liveness: %.1fs from last heartbeat to report > 5.0s -- stalled near end'
                           % (_rt - _hbs[-1]))
    elif _rt is None:
        raise HardFail('liveness: no heartbeats and no completion report -- link never came alive')


def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    _corruption_gate(extract_dir)
    _liveness_gate(extract_dir)
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
    _xs = None
    try:
        import os as _os, re as _re
        for _ln in open(_os.path.join(extract_dir, 'timeline.log'), encoding='utf-8', errors='replace'):
            _mm = _re.match(r"^\S+\s+([0-9]+\.[0-9]+)\s+>\s+STREAM\s+dsp\.uart\b", _ln)
            if _mm and 'xfer' in _ln:
                _xs = float(_mm.group(1)); break
    except (OSError, ImportError):
        pass
    elapsed = expects[0]['t_end'] - (_xs if _xs is not None else boots[0]['t_start'])
    rate = int(words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'{rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if rate < 56250000:
        raise HardFail(f'rate {rate} < 56250000')
    if lanes == 4 and errors == 0 and words >= 134217728 and m.group(4) == 'PASS':
        return True
    raise HardFail(f'FAIL: lanes={lanes} words={words} errors={errors}')
```

### DDDD-FFFF 1GiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
make -C fpga sport-verilog
mkdir -p fpga/build/sport_bidir_4xrx
cd fpga && yosys -q -p "read_verilog -D EYE_DELAY verilog/sport_tx_sync_nopll.v verilog/sport_tx_prbs_ser.v verilog/sport_rx.v verilog/sport_bidir.v verilog/uart_tx.v; chparam -set TX_TO_DSP_N 1 -set RX_FROM_DSP_N 4 -set SYNC_TX 1 -set NOPLL 1 -set FROM_DSP_EN 1 -set REPORT_LANE0 0 -set MIN_DONE_WORDS 268435456 sport_bidir; synth_ice40 -top sport_bidir; setattr -unset src; write_json build/sport_bidir_4xrx/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_bidir_4xrx/s.json --pcf verilog/sport_bidir_4xrx_hx8k.pcf --asc build/sport_bidir_4xrx/s.asc --freq 75 --timing-allow-fail --seed 20 -q --pcf-allow-unconstrained && icepack build/sport_bidir_4xrx/s.asc build/sport_bidir_4xrx/sport_bidir_4xrx.bin
make -C adsp2156/sport clean
make -j -C adsp2156/sport CFLAGS_EXTRA="-DRX_N=0U -DTX_N=4U -DTOTAL_WORDS=268435520U -DTX_FIRST -DSPORT_SCLK_HZ=57291667U -DSPORT_CLKDIV=0U -DFPGA_LOAD_DELAY_MS=12000U"
cp adsp2156/sport/build/main.ldr adsp2156/sport/build/dma_1gib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_bidir_4xrx/sport_bidir_4xrx.bin
adsp2156/sport/build/dma_1gib.ldr
```

Test (max 16 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@blinky.bin
dsp:uart_open
dsp:boot ldr=@dma_1gib.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_bidir_concurrent" timeout_ms=10000
fpga.hx8k:program bin=@sport_bidir_4xrx.bin
fpga.hx8k:uart_open
fpga.hx8k:uart_expect sentinel="sport_rx lanes=" timeout_ms=210000
delay ms=3000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=dddd_ffff_1gib
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


def _liveness_gate(extract_dir):
    # jk: HARD fail (no retry) if any heartbeat is >5 s late -- a >5 s GAP in the
    # live heartbeat stream while the transfer runs. Heartbeats (tx h=, rx h=,
    # rx w=) fire every 8 MiB, so a sub-8 MiB transfer emits none and is fine as
    # long as it completed (final report present); no heartbeats AND no report is
    # a dead link.
    import os
    try:
        _tl = open(os.path.join(extract_dir, 'timeline.log'),
                   encoding='ascii', errors='replace').read().splitlines()
    except OSError:
        raise HardFail('liveness: no timeline.log to verify heartbeats')
    _hb = re.compile(r'(?:tx h=\d+|rx h=\d+|rx w=[0-9a-fA-F]+)')
    _rep = re.compile(r'sport_rx lanes=|sport_bidir rx_lanes=')
    _row = re.compile(r'^\S+\s+([0-9]+\.[0-9]+)\s+>\s+STREAM\s+(?:dsp|fpga)\.uart')
    _hbs = []
    _rt = None
    for _ln in _tl:
        _m = _row.match(_ln)
        if not _m:
            continue
        _t = float(_m.group(1))
        if _hb.search(_ln):
            _hbs.append(_t)
        if _rt is None and _rep.search(_ln):
            _rt = _t
    _hbs.sort()
    for _a, _b in zip(_hbs, _hbs[1:]):
        if _b - _a > 5.0:
            raise HardFail('liveness: heartbeat gap %.1fs > 5.0s (stall near t=%.1fs)'
                           % (_b - _a, _a))
    if _hbs:
        if _rt is None:
            raise HardFail('liveness: heartbeats stopped with no completion report -- stalled')
        if _rt - _hbs[-1] > 5.0:
            raise HardFail('liveness: %.1fs from last heartbeat to report > 5.0s -- stalled near end'
                           % (_rt - _hbs[-1]))
    elif _rt is None:
        raise HardFail('liveness: no heartbeats and no completion report -- link never came alive')


def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    _corruption_gate(extract_dir)
    _liveness_gate(extract_dir)
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
    _xs = None
    try:
        import os as _os, re as _re
        for _ln in open(_os.path.join(extract_dir, 'timeline.log'), encoding='utf-8', errors='replace'):
            _mm = _re.match(r"^\S+\s+([0-9]+\.[0-9]+)\s+>\s+STREAM\s+dsp\.uart\b", _ln)
            if _mm and 'xfer' in _ln:
                _xs = float(_mm.group(1)); break
    except (OSError, ImportError):
        pass
    elapsed = expects[0]['t_end'] - (_xs if _xs is not None else boots[0]['t_start'])
    rate = int(words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'{rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if rate < 56250000:
        raise HardFail(f'rate {rate} < 56250000')
    if lanes == 4 and errors == 0 and words >= 268435456 and m.group(4) == 'PASS':
        return True
    raise HardFail(f'FAIL: lanes={lanes} words={words} errors={errors}')
```

### DDDD-FFFF 2GiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
make -C fpga sport-verilog
mkdir -p fpga/build/sport_bidir_4xrx
cd fpga && yosys -q -p "read_verilog -D EYE_DELAY verilog/sport_tx_sync_nopll.v verilog/sport_tx_prbs_ser.v verilog/sport_rx.v verilog/sport_bidir.v verilog/uart_tx.v; chparam -set TX_TO_DSP_N 1 -set RX_FROM_DSP_N 4 -set SYNC_TX 1 -set NOPLL 1 -set FROM_DSP_EN 1 -set REPORT_LANE0 0 -set MIN_DONE_WORDS 536870912 sport_bidir; synth_ice40 -top sport_bidir; setattr -unset src; write_json build/sport_bidir_4xrx/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_bidir_4xrx/s.json --pcf verilog/sport_bidir_4xrx_hx8k.pcf --asc build/sport_bidir_4xrx/s.asc --freq 75 --timing-allow-fail --seed 20 -q --pcf-allow-unconstrained && icepack build/sport_bidir_4xrx/s.asc build/sport_bidir_4xrx/sport_bidir_4xrx.bin
make -C adsp2156/sport clean
make -j -C adsp2156/sport CFLAGS_EXTRA="-DRX_N=0U -DTX_N=4U -DTOTAL_WORDS=536870976U -DTX_FIRST -DSPORT_SCLK_HZ=57291667U -DSPORT_CLKDIV=0U -DFPGA_LOAD_DELAY_MS=12000U"
cp adsp2156/sport/build/main.ldr adsp2156/sport/build/dma_2gib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_bidir_4xrx/sport_bidir_4xrx.bin
adsp2156/sport/build/dma_2gib.ldr
```

Test (max 21 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@blinky.bin
dsp:uart_open
dsp:boot ldr=@dma_2gib.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_bidir_concurrent" timeout_ms=10000
fpga.hx8k:program bin=@sport_bidir_4xrx.bin
fpga.hx8k:uart_open
fpga.hx8k:uart_expect sentinel="sport_rx lanes=" timeout_ms=390000
delay ms=3000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=dddd_ffff_2gib
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


def _liveness_gate(extract_dir):
    # jk: HARD fail (no retry) if any heartbeat is >5 s late -- a >5 s GAP in the
    # live heartbeat stream while the transfer runs. Heartbeats (tx h=, rx h=,
    # rx w=) fire every 8 MiB, so a sub-8 MiB transfer emits none and is fine as
    # long as it completed (final report present); no heartbeats AND no report is
    # a dead link.
    import os
    try:
        _tl = open(os.path.join(extract_dir, 'timeline.log'),
                   encoding='ascii', errors='replace').read().splitlines()
    except OSError:
        raise HardFail('liveness: no timeline.log to verify heartbeats')
    _hb = re.compile(r'(?:tx h=\d+|rx h=\d+|rx w=[0-9a-fA-F]+)')
    _rep = re.compile(r'sport_rx lanes=|sport_bidir rx_lanes=')
    _row = re.compile(r'^\S+\s+([0-9]+\.[0-9]+)\s+>\s+STREAM\s+(?:dsp|fpga)\.uart')
    _hbs = []
    _rt = None
    for _ln in _tl:
        _m = _row.match(_ln)
        if not _m:
            continue
        _t = float(_m.group(1))
        if _hb.search(_ln):
            _hbs.append(_t)
        if _rt is None and _rep.search(_ln):
            _rt = _t
    _hbs.sort()
    for _a, _b in zip(_hbs, _hbs[1:]):
        if _b - _a > 5.0:
            raise HardFail('liveness: heartbeat gap %.1fs > 5.0s (stall near t=%.1fs)'
                           % (_b - _a, _a))
    if _hbs:
        if _rt is None:
            raise HardFail('liveness: heartbeats stopped with no completion report -- stalled')
        if _rt - _hbs[-1] > 5.0:
            raise HardFail('liveness: %.1fs from last heartbeat to report > 5.0s -- stalled near end'
                           % (_rt - _hbs[-1]))
    elif _rt is None:
        raise HardFail('liveness: no heartbeats and no completion report -- link never came alive')


def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    _corruption_gate(extract_dir)
    _liveness_gate(extract_dir)
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
    _xs = None
    try:
        import os as _os, re as _re
        for _ln in open(_os.path.join(extract_dir, 'timeline.log'), encoding='utf-8', errors='replace'):
            _mm = _re.match(r"^\S+\s+([0-9]+\.[0-9]+)\s+>\s+STREAM\s+dsp\.uart\b", _ln)
            if _mm and 'xfer' in _ln:
                _xs = float(_mm.group(1)); break
    except (OSError, ImportError):
        pass
    elapsed = expects[0]['t_end'] - (_xs if _xs is not None else boots[0]['t_start'])
    rate = int(words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'{rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if rate < 56250000:
        raise HardFail(f'rate {rate} < 56250000')
    if lanes == 4 and errors == 0 and words >= 536870912 and m.group(4) == 'PASS':
        return True
    raise HardFail(f'FAIL: lanes={lanes} words={words} errors={errors}')
```

### DDDD-FFFF 4GiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
make -C fpga sport-verilog
mkdir -p fpga/build/sport_bidir_4xrx
cd fpga && yosys -q -p "read_verilog -D EYE_DELAY verilog/sport_tx_sync_nopll.v verilog/sport_tx_prbs_ser.v verilog/sport_rx.v verilog/sport_bidir.v verilog/uart_tx.v; chparam -set TX_TO_DSP_N 1 -set RX_FROM_DSP_N 4 -set SYNC_TX 1 -set NOPLL 1 -set FROM_DSP_EN 1 -set REPORT_LANE0 0 -set MIN_DONE_WORDS 1073741824 sport_bidir; synth_ice40 -top sport_bidir; setattr -unset src; write_json build/sport_bidir_4xrx/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_bidir_4xrx/s.json --pcf verilog/sport_bidir_4xrx_hx8k.pcf --asc build/sport_bidir_4xrx/s.asc --freq 75 --timing-allow-fail --seed 20 -q --pcf-allow-unconstrained && icepack build/sport_bidir_4xrx/s.asc build/sport_bidir_4xrx/sport_bidir_4xrx.bin
make -C adsp2156/sport clean
make -j -C adsp2156/sport CFLAGS_EXTRA="-DRX_N=0U -DTX_N=4U -DTOTAL_WORDS=1073741888U -DTX_FIRST -DSPORT_SCLK_HZ=57291667U -DSPORT_CLKDIV=0U -DFPGA_LOAD_DELAY_MS=12000U"
cp adsp2156/sport/build/main.ldr adsp2156/sport/build/dma_4gib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_bidir_4xrx/sport_bidir_4xrx.bin
adsp2156/sport/build/dma_4gib.ldr
```

Test (max 24 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@blinky.bin
dsp:uart_open
dsp:boot ldr=@dma_4gib.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_bidir_concurrent" timeout_ms=10000
fpga.hx8k:program bin=@sport_bidir_4xrx.bin
fpga.hx8k:uart_open
fpga.hx8k:uart_expect sentinel="sport_rx lanes=" timeout_ms=750000
delay ms=3000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=dddd_ffff_4gib
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


def _liveness_gate(extract_dir):
    # jk: HARD fail (no retry) if any heartbeat is >5 s late -- a >5 s GAP in the
    # live heartbeat stream while the transfer runs. Heartbeats (tx h=, rx h=,
    # rx w=) fire every 8 MiB, so a sub-8 MiB transfer emits none and is fine as
    # long as it completed (final report present); no heartbeats AND no report is
    # a dead link.
    import os
    try:
        _tl = open(os.path.join(extract_dir, 'timeline.log'),
                   encoding='ascii', errors='replace').read().splitlines()
    except OSError:
        raise HardFail('liveness: no timeline.log to verify heartbeats')
    _hb = re.compile(r'(?:tx h=\d+|rx h=\d+|rx w=[0-9a-fA-F]+)')
    _rep = re.compile(r'sport_rx lanes=|sport_bidir rx_lanes=')
    _row = re.compile(r'^\S+\s+([0-9]+\.[0-9]+)\s+>\s+STREAM\s+(?:dsp|fpga)\.uart')
    _hbs = []
    _rt = None
    for _ln in _tl:
        _m = _row.match(_ln)
        if not _m:
            continue
        _t = float(_m.group(1))
        if _hb.search(_ln):
            _hbs.append(_t)
        if _rt is None and _rep.search(_ln):
            _rt = _t
    _hbs.sort()
    for _a, _b in zip(_hbs, _hbs[1:]):
        if _b - _a > 5.0:
            raise HardFail('liveness: heartbeat gap %.1fs > 5.0s (stall near t=%.1fs)'
                           % (_b - _a, _a))
    if _hbs:
        if _rt is None:
            raise HardFail('liveness: heartbeats stopped with no completion report -- stalled')
        if _rt - _hbs[-1] > 5.0:
            raise HardFail('liveness: %.1fs from last heartbeat to report > 5.0s -- stalled near end'
                           % (_rt - _hbs[-1]))
    elif _rt is None:
        raise HardFail('liveness: no heartbeats and no completion report -- link never came alive')


def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    _corruption_gate(extract_dir)
    _liveness_gate(extract_dir)
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
    _xs = None
    try:
        import os as _os, re as _re
        for _ln in open(_os.path.join(extract_dir, 'timeline.log'), encoding='utf-8', errors='replace'):
            _mm = _re.match(r"^\S+\s+([0-9]+\.[0-9]+)\s+>\s+STREAM\s+dsp\.uart\b", _ln)
            if _mm and 'xfer' in _ln:
                _xs = float(_mm.group(1)); break
    except (OSError, ImportError):
        pass
    elapsed = expects[0]['t_end'] - (_xs if _xs is not None else boots[0]['t_start'])
    rate = int(words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'{rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if rate < 56250000:
        raise HardFail(f'rate {rate} < 56250000')
    if lanes == 4 and errors == 0 and words >= 1073741824 and m.group(4) == 'PASS':
        return True
    raise HardFail(f'FAIL: lanes={lanes} words={words} errors={errors}')
```

