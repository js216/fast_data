# FFFF-DDDD direction ladder (FPGA -> DSP, 4 lanes)
#### FFFF-DDDD 128B

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport4x
cd fpga && yosys -q -p "read_verilog -D SPORT_TX_POSEDGE_OUT verilog/sport_tx_from_dsp_clk.v; chparam -set N 4 sport_tx_from_dsp_clk; synth_ice40 -top sport_tx_from_dsp_clk -json build/sport4x/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport4x/s.json --pcf verilog/sport_tx_prbs_multi_4x_hx8k.pcf --asc build/sport4x/s.asc --freq 40 -q --pcf-allow-unconstrained && icepack build/sport4x/s.asc build/sport4x/sport4x.bin
make -C adsp2156/sport_fpga_4x clean
make -j -C adsp2156/sport_fpga_4x CFLAGS_EXTRA="-DTOTAL_WORDS=32U"
cp adsp2156/sport_fpga_4x/build/main.ldr adsp2156/sport_fpga_4x/build/m4x_128b.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport4x/sport4x.bin
adsp2156/sport_fpga_4x/build/m4x_128b.ldr
```

Test (max 6 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@blinky.bin
fpga.hx8k:program bin=@sport4x.bin
dsp:uart_open
dsp:boot ldr=@m4x_128b.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_4x agg_bytes=" timeout_ms=15000
delay ms=200
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=ffff_dddd_128b
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
    text = Verification.load_stream_text(extract_dir, 'dsp.uart')
    m = re.search(r'sport_4x agg_bytes=(\d+) per_ch_bytes=(\d+) errors0=(\d+) errors1=(\d+) errors2=(\d+) errors3=(\d+).*? timeouts=(\d+) overruns=(\d+) (PASS|FAIL)', text)
    if not m:
        raise HardFail('no sport_4x report')
    agg, pc, e0, e1, e2, e3, to, ov = (int(x) for x in m.groups()[:8])
    if (pc >= 128 and e0 == e1 == e2 == e3 == 0 and to == 0 and ov == 0 and m.group(9) == 'PASS'):
        return True
    raise HardFail(f'FAIL: per_ch={pc} errors=({e0},{e1},{e2},{e3}) timeouts={to}')
```

### FFFF-DDDD 1MiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
make -C adsp2156/sport_fpga_bidir clean
make -j -C adsp2156/sport_fpga_bidir CFLAGS_EXTRA="-DRX_N=4U -DTX_N=2U -DTOTAL_WORDS=262144U -DTX_NO_REFILL -DSPORT_SCLK_HZ=59375000U -DSPORT_CLKDIV=0U"
cp adsp2156/sport_fpga_bidir/build/main.ldr adsp2156/sport_fpga_bidir/build/ffff1mib.ldr
mkdir -p fpga/build/sport_bidir_4x
cd fpga && yosys -q -p "read_verilog -D SHARE_COPIES verilog/sport_tx_sync_nopll.v verilog/sport_tx_prbs_ser.v verilog/sport_rx.v verilog/sport_bidir.v verilog/uart_tx.v; chparam -set TX_TO_DSP_N 4 -set RX_FROM_DSP_N 2 -set SYNC_TX 1 -set NOPLL 1 -set SHARE_PAIRS 1 -set FROM_DSP_EN 0 -set REPORT_LANE0 0 -set MIN_DONE_WORDS 262144 sport_bidir; synth_ice40 -top sport_bidir -json build/sport_bidir_4x/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_bidir_4x/s.json --pcf verilog/sport_bidir_4x_hx8k.pcf --asc build/sport_bidir_4x/s.asc --freq 62 --seed 9 -q --pcf-allow-unconstrained && icepack build/sport_bidir_4x/s.asc build/sport_bidir_4x/sport_bidir_4x.bin
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_bidir_4x/sport_bidir_4x.bin
adsp2156/sport_fpga_bidir/build/ffff1mib.ldr
```

Test (max 8 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_bidir_4x.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@ffff1mib.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_bidir rx_lanes=4" timeout_ms=60000
delay ms=2000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=ffff_dddd_1mib
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
    dtxt = Verification.load_stream_text(extract_dir, 'dsp.uart')
    dm = re.search(r'sport_bidir rx_lanes=(\d+) tx_lanes=(\d+) rx_words=(\d+) rx_errors=(\d+) e0=(\d+) e1=(\d+) e2=(\d+) e3=(\d+) timeouts=(\d+) tx_timeouts=(\d+) overruns=(\d+) slips=(\d+)', dtxt)
    if not dm:
        raise HardFail('no sport_bidir report')
    lanes, words, errs, to, txto, ov, slips = (int(dm.group(i)) for i in (1,3,4,9,10,11,12))
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'uart_expect']
    elapsed = expects[0]['t_end'] - boots[0]['t_start'] if boots and expects else 0
    rate = int(words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'{rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if (lanes == 4 and words == 262144 and errs == 0 and to == 0
            and txto == 0 and ov == 0):
        return True
    raise HardFail(f'FFFF-DDDD: errors={errs} ov={ov} words={words}')
```

### FFFF-DDDD 64MiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
make -C adsp2156/sport_fpga_bidir clean
make -j -C adsp2156/sport_fpga_bidir CFLAGS_EXTRA="-DRX_N=4U -DTX_N=2U -DTOTAL_WORDS=16777216U -DTX_NO_REFILL -DSPORT_SCLK_HZ=59375000U -DSPORT_CLKDIV=0U"
cp adsp2156/sport_fpga_bidir/build/main.ldr adsp2156/sport_fpga_bidir/build/ffff64mib.ldr
mkdir -p fpga/build/sport_bidir_4x
cd fpga && yosys -q -p "read_verilog -D SHARE_COPIES verilog/sport_tx_sync_nopll.v verilog/sport_tx_prbs_ser.v verilog/sport_rx.v verilog/sport_bidir.v verilog/uart_tx.v; chparam -set TX_TO_DSP_N 4 -set RX_FROM_DSP_N 2 -set SYNC_TX 1 -set NOPLL 1 -set SHARE_PAIRS 1 -set FROM_DSP_EN 0 -set REPORT_LANE0 0 -set MIN_DONE_WORDS 16777216 sport_bidir; synth_ice40 -top sport_bidir -json build/sport_bidir_4x/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_bidir_4x/s.json --pcf verilog/sport_bidir_4x_hx8k.pcf --asc build/sport_bidir_4x/s.asc --freq 62 --seed 9 -q --pcf-allow-unconstrained && icepack build/sport_bidir_4x/s.asc build/sport_bidir_4x/sport_bidir_4x.bin
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_bidir_4x/sport_bidir_4x.bin
adsp2156/sport_fpga_bidir/build/ffff64mib.ldr
```

Test (max 10 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_bidir_4x.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@ffff64mib.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_bidir rx_lanes=4" timeout_ms=60000
delay ms=2000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=ffff_dddd_64mib
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
    dtxt = Verification.load_stream_text(extract_dir, 'dsp.uart')
    dm = re.search(r'sport_bidir rx_lanes=(\d+) tx_lanes=(\d+) rx_words=(\d+) rx_errors=(\d+) e0=(\d+) e1=(\d+) e2=(\d+) e3=(\d+) timeouts=(\d+) tx_timeouts=(\d+) overruns=(\d+) slips=(\d+)', dtxt)
    if not dm:
        raise HardFail('no sport_bidir report')
    lanes, words, errs, to, txto, ov, slips = (int(dm.group(i)) for i in (1,3,4,9,10,11,12))
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'uart_expect']
    elapsed = expects[0]['t_end'] - boots[0]['t_start'] if boots and expects else 0
    rate = int(words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'{rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if (lanes == 4 and words == 16777216 and errs == 0 and to == 0
            and txto == 0 and ov == 0):
        return True
    raise HardFail(f'FFFF-DDDD: errors={errs} ov={ov} words={words}')
```

### FFFF-DDDD 256MiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
make -C adsp2156/sport_fpga_bidir clean
make -j -C adsp2156/sport_fpga_bidir CFLAGS_EXTRA="-DRX_N=4U -DTX_N=2U -DTOTAL_WORDS=67108864U -DTX_NO_REFILL -DSPORT_SCLK_HZ=59375000U -DSPORT_CLKDIV=0U"
cp adsp2156/sport_fpga_bidir/build/main.ldr adsp2156/sport_fpga_bidir/build/ffff256mib.ldr
mkdir -p fpga/build/sport_bidir_4x
cd fpga && yosys -q -p "read_verilog -D SHARE_COPIES verilog/sport_tx_sync_nopll.v verilog/sport_tx_prbs_ser.v verilog/sport_rx.v verilog/sport_bidir.v verilog/uart_tx.v; chparam -set TX_TO_DSP_N 4 -set RX_FROM_DSP_N 2 -set SYNC_TX 1 -set NOPLL 1 -set SHARE_PAIRS 1 -set FROM_DSP_EN 0 -set REPORT_LANE0 0 -set MIN_DONE_WORDS 67108864 sport_bidir; synth_ice40 -top sport_bidir -json build/sport_bidir_4x/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_bidir_4x/s.json --pcf verilog/sport_bidir_4x_hx8k.pcf --asc build/sport_bidir_4x/s.asc --freq 62 --seed 9 -q --pcf-allow-unconstrained && icepack build/sport_bidir_4x/s.asc build/sport_bidir_4x/sport_bidir_4x.bin
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_bidir_4x/sport_bidir_4x.bin
adsp2156/sport_fpga_bidir/build/ffff256mib.ldr
```

Test (max 10 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_bidir_4x.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@ffff256mib.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_bidir rx_lanes=4" timeout_ms=75000
delay ms=2000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=ffff_dddd_256mib
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
    dtxt = Verification.load_stream_text(extract_dir, 'dsp.uart')
    dm = re.search(r'sport_bidir rx_lanes=(\d+) tx_lanes=(\d+) rx_words=(\d+) rx_errors=(\d+) e0=(\d+) e1=(\d+) e2=(\d+) e3=(\d+) timeouts=(\d+) tx_timeouts=(\d+) overruns=(\d+) slips=(\d+)', dtxt)
    if not dm:
        raise HardFail('no sport_bidir report')
    lanes, words, errs, to, txto, ov, slips = (int(dm.group(i)) for i in (1,3,4,9,10,11,12))
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'uart_expect']
    elapsed = expects[0]['t_end'] - boots[0]['t_start'] if boots and expects else 0
    rate = int(words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'{rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if rate < 56250000:
        raise HardFail(f'FFFF-DDDD rate {rate} < 56250000')
    if (lanes == 4 and words == 67108864 and errs == 0 and to == 0
            and txto == 0 and ov == 0):
        return True
    raise HardFail(f'FFFF-DDDD: errors={errs} ov={ov} words={words}')
```

### FFFF-DDDD 512MiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
make -C adsp2156/sport_fpga_bidir clean
make -j -C adsp2156/sport_fpga_bidir CFLAGS_EXTRA="-DRX_N=4U -DTX_N=2U -DTOTAL_WORDS=134217728U -DTX_NO_REFILL -DSPORT_SCLK_HZ=59375000U -DSPORT_CLKDIV=0U"
cp adsp2156/sport_fpga_bidir/build/main.ldr adsp2156/sport_fpga_bidir/build/ffff512mib.ldr
mkdir -p fpga/build/sport_bidir_4x
cd fpga && yosys -q -p "read_verilog -D SHARE_COPIES verilog/sport_tx_sync_nopll.v verilog/sport_tx_prbs_ser.v verilog/sport_rx.v verilog/sport_bidir.v verilog/uart_tx.v; chparam -set TX_TO_DSP_N 4 -set RX_FROM_DSP_N 2 -set SYNC_TX 1 -set NOPLL 1 -set SHARE_PAIRS 1 -set FROM_DSP_EN 0 -set REPORT_LANE0 0 -set MIN_DONE_WORDS 134217728 sport_bidir; synth_ice40 -top sport_bidir -json build/sport_bidir_4x/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_bidir_4x/s.json --pcf verilog/sport_bidir_4x_hx8k.pcf --asc build/sport_bidir_4x/s.asc --freq 62 --seed 9 -q --pcf-allow-unconstrained && icepack build/sport_bidir_4x/s.asc build/sport_bidir_4x/sport_bidir_4x.bin
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_bidir_4x/sport_bidir_4x.bin
adsp2156/sport_fpga_bidir/build/ffff512mib.ldr
```

Test (max 12 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_bidir_4x.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@ffff512mib.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_bidir rx_lanes=4" timeout_ms=150000
delay ms=2000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=ffff_dddd_512mib
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
    dtxt = Verification.load_stream_text(extract_dir, 'dsp.uart')
    dm = re.search(r'sport_bidir rx_lanes=(\d+) tx_lanes=(\d+) rx_words=(\d+) rx_errors=(\d+) e0=(\d+) e1=(\d+) e2=(\d+) e3=(\d+) timeouts=(\d+) tx_timeouts=(\d+) overruns=(\d+) slips=(\d+)', dtxt)
    if not dm:
        raise HardFail('no sport_bidir report')
    lanes, words, errs, to, txto, ov, slips = (int(dm.group(i)) for i in (1,3,4,9,10,11,12))
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'uart_expect']
    elapsed = expects[0]['t_end'] - boots[0]['t_start'] if boots and expects else 0
    rate = int(words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'{rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if rate < 56250000:
        raise HardFail(f'FFFF-DDDD rate {rate} < 56250000')
    if (lanes == 4 and words == 134217728 and errs == 0 and to == 0
            and txto == 0 and ov == 0):
        return True
    raise HardFail(f'FFFF-DDDD: errors={errs} ov={ov} words={words}')
```

### FFFF-DDDD 1GiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
make -C adsp2156/sport_fpga_bidir clean
make -j -C adsp2156/sport_fpga_bidir CFLAGS_EXTRA="-DRX_N=4U -DTX_N=2U -DTOTAL_WORDS=268435456U -DTX_NO_REFILL -DSPORT_SCLK_HZ=59375000U -DSPORT_CLKDIV=0U"
cp adsp2156/sport_fpga_bidir/build/main.ldr adsp2156/sport_fpga_bidir/build/ffff1gib.ldr
mkdir -p fpga/build/sport_bidir_4x
cd fpga && yosys -q -p "read_verilog -D SHARE_COPIES verilog/sport_tx_sync_nopll.v verilog/sport_tx_prbs_ser.v verilog/sport_rx.v verilog/sport_bidir.v verilog/uart_tx.v; chparam -set TX_TO_DSP_N 4 -set RX_FROM_DSP_N 2 -set SYNC_TX 1 -set NOPLL 1 -set SHARE_PAIRS 1 -set FROM_DSP_EN 0 -set REPORT_LANE0 0 -set MIN_DONE_WORDS 268435456 sport_bidir; synth_ice40 -top sport_bidir -json build/sport_bidir_4x/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_bidir_4x/s.json --pcf verilog/sport_bidir_4x_hx8k.pcf --asc build/sport_bidir_4x/s.asc --freq 62 --seed 9 -q --pcf-allow-unconstrained && icepack build/sport_bidir_4x/s.asc build/sport_bidir_4x/sport_bidir_4x.bin
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_bidir_4x/sport_bidir_4x.bin
adsp2156/sport_fpga_bidir/build/ffff1gib.ldr
```

Test (max 16 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_bidir_4x.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@ffff1gib.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_bidir rx_lanes=4" timeout_ms=210000
delay ms=2000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=ffff_dddd_1gib
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
    dtxt = Verification.load_stream_text(extract_dir, 'dsp.uart')
    dm = re.search(r'sport_bidir rx_lanes=(\d+) tx_lanes=(\d+) rx_words=(\d+) rx_errors=(\d+) e0=(\d+) e1=(\d+) e2=(\d+) e3=(\d+) timeouts=(\d+) tx_timeouts=(\d+) overruns=(\d+) slips=(\d+)', dtxt)
    if not dm:
        raise HardFail('no sport_bidir report')
    lanes, words, errs, to, txto, ov, slips = (int(dm.group(i)) for i in (1,3,4,9,10,11,12))
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'uart_expect']
    elapsed = expects[0]['t_end'] - boots[0]['t_start'] if boots and expects else 0
    rate = int(words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'{rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if rate < 56250000:
        raise HardFail(f'FFFF-DDDD rate {rate} < 56250000')
    if (lanes == 4 and words == 268435456 and errs == 0 and to == 0
            and txto == 0 and ov == 0):
        return True
    raise HardFail(f'FFFF-DDDD: errors={errs} ov={ov} words={words}')
```

### FFFF-DDDD 2GiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
make -C adsp2156/sport_fpga_bidir clean
make -j -C adsp2156/sport_fpga_bidir CFLAGS_EXTRA="-DRX_N=4U -DTX_N=2U -DTOTAL_WORDS=536870912U -DTX_NO_REFILL -DSPORT_SCLK_HZ=59375000U -DSPORT_CLKDIV=0U"
cp adsp2156/sport_fpga_bidir/build/main.ldr adsp2156/sport_fpga_bidir/build/ffff2gib.ldr
mkdir -p fpga/build/sport_bidir_4x
cd fpga && yosys -q -p "read_verilog -D SHARE_COPIES verilog/sport_tx_sync_nopll.v verilog/sport_tx_prbs_ser.v verilog/sport_rx.v verilog/sport_bidir.v verilog/uart_tx.v; chparam -set TX_TO_DSP_N 4 -set RX_FROM_DSP_N 2 -set SYNC_TX 1 -set NOPLL 1 -set SHARE_PAIRS 1 -set FROM_DSP_EN 0 -set REPORT_LANE0 0 -set MIN_DONE_WORDS 536870912 sport_bidir; synth_ice40 -top sport_bidir -json build/sport_bidir_4x/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_bidir_4x/s.json --pcf verilog/sport_bidir_4x_hx8k.pcf --asc build/sport_bidir_4x/s.asc --freq 62 --seed 9 -q --pcf-allow-unconstrained && icepack build/sport_bidir_4x/s.asc build/sport_bidir_4x/sport_bidir_4x.bin
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_bidir_4x/sport_bidir_4x.bin
adsp2156/sport_fpga_bidir/build/ffff2gib.ldr
```

Test (max 20 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_bidir_4x.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@ffff2gib.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_bidir rx_lanes=4" timeout_ms=390000
delay ms=2000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=ffff_dddd_2gib
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
    dtxt = Verification.load_stream_text(extract_dir, 'dsp.uart')
    dm = re.search(r'sport_bidir rx_lanes=(\d+) tx_lanes=(\d+) rx_words=(\d+) rx_errors=(\d+) e0=(\d+) e1=(\d+) e2=(\d+) e3=(\d+) timeouts=(\d+) tx_timeouts=(\d+) overruns=(\d+) slips=(\d+)', dtxt)
    if not dm:
        raise HardFail('no sport_bidir report')
    lanes, words, errs, to, txto, ov, slips = (int(dm.group(i)) for i in (1,3,4,9,10,11,12))
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'uart_expect']
    elapsed = expects[0]['t_end'] - boots[0]['t_start'] if boots and expects else 0
    rate = int(words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'{rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if rate < 56250000:
        raise HardFail(f'FFFF-DDDD rate {rate} < 56250000')
    if (lanes == 4 and words == 536870912 and errs == 0 and to == 0
            and txto == 0 and ov == 0):
        return True
    raise HardFail(f'FFFF-DDDD: errors={errs} ov={ov} words={words}')
```

### FFFF-DDDD 4GiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
make -C adsp2156/sport_fpga_bidir clean
make -j -C adsp2156/sport_fpga_bidir CFLAGS_EXTRA="-DRX_N=4U -DTX_N=2U -DTOTAL_WORDS=1073741824U -DTX_NO_REFILL -DSPORT_SCLK_HZ=59375000U -DSPORT_CLKDIV=0U"
cp adsp2156/sport_fpga_bidir/build/main.ldr adsp2156/sport_fpga_bidir/build/ffff4gib.ldr
mkdir -p fpga/build/sport_bidir_4x
cd fpga && yosys -q -p "read_verilog -D SHARE_COPIES verilog/sport_tx_sync_nopll.v verilog/sport_tx_prbs_ser.v verilog/sport_rx.v verilog/sport_bidir.v verilog/uart_tx.v; chparam -set TX_TO_DSP_N 4 -set RX_FROM_DSP_N 2 -set SYNC_TX 1 -set NOPLL 1 -set SHARE_PAIRS 1 -set FROM_DSP_EN 0 -set REPORT_LANE0 0 -set MIN_DONE_WORDS 1073741824 sport_bidir; synth_ice40 -top sport_bidir -json build/sport_bidir_4x/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_bidir_4x/s.json --pcf verilog/sport_bidir_4x_hx8k.pcf --asc build/sport_bidir_4x/s.asc --freq 62 --seed 9 -q --pcf-allow-unconstrained && icepack build/sport_bidir_4x/s.asc build/sport_bidir_4x/sport_bidir_4x.bin
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_bidir_4x/sport_bidir_4x.bin
adsp2156/sport_fpga_bidir/build/ffff4gib.ldr
```

Test (max 24 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_bidir_4x.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@ffff4gib.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_bidir rx_lanes=4" timeout_ms=720000
delay ms=2000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=ffff_dddd_4gib
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
    dtxt = Verification.load_stream_text(extract_dir, 'dsp.uart')
    dm = re.search(r'sport_bidir rx_lanes=(\d+) tx_lanes=(\d+) rx_words=(\d+) rx_errors=(\d+) e0=(\d+) e1=(\d+) e2=(\d+) e3=(\d+) timeouts=(\d+) tx_timeouts=(\d+) overruns=(\d+) slips=(\d+)', dtxt)
    if not dm:
        raise HardFail('no sport_bidir report')
    lanes, words, errs, to, txto, ov, slips = (int(dm.group(i)) for i in (1,3,4,9,10,11,12))
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'uart_expect']
    elapsed = expects[0]['t_end'] - boots[0]['t_start'] if boots and expects else 0
    rate = int(words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'{rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if rate < 56250000:
        raise HardFail(f'FFFF-DDDD rate {rate} < 56250000')
    if (lanes == 4 and words == 1073741824 and errs == 0 and to == 0
            and txto == 0 and ov == 0):
        return True
    raise HardFail(f'FFFF-DDDD: errors={errs} ov={ov} words={words}')
```
