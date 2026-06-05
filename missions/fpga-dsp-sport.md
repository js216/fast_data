# DSP <-> FPGA SPORT link: max error-free rate for 2 GB, and parallel scaling

Prove the ADSP-2156 <-> iCE40-HX8K SPORT link transfer arbitrary amount
of arbitrary PRBS data patterns with zero bit errors, then multiply the
data rate by running multiple SPORTs in parallel (two SPORTs to double
it, four to quadruple).

### Bench inventory probe

Test (max 1 min):

```
inventory
mark tag=sport_inventory_probe
```

Verify:

```
from pathlib import Path
import json

def _adv(ops, plugin):
    out = set()
    for name, entry in ops.items():
        if name == plugin or name.startswith(plugin + '.'):
            out.update((entry or {}).get('ops') or {})
    return out

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    devices = json.loads(Path(extract_dir, 'bench.devices.json').read_text())
    ops_map = json.loads(Path(extract_dir, 'bench.ops.json').read_text())
    plugins = {d.get('plugin') for d in devices if isinstance(d, dict)}
    if not {'fpga', 'dsp'} <= plugins:
        return False
    return {'program', 'uart_open', 'uart_write', 'uart_close'} <= _adv(ops_map, 'fpga') \
        and {'reset', 'boot', 'uart_open', 'uart_expect', 'uart_close'} <= _adv(ops_map, 'dsp')
```

### Build firmware

Build the benign blinky bitstream, the FPGA SPORT PRBS-31 streamer
(`sport_tx_prbs`, live-ball pcf), and the DSP SPORT receiver variants
(64 MB / 512 MB / 2 GB). The FPGA bit-clock rate is set by the PLL in
`fpga/verilog/sport_tx_prbs.v` (DIVF/DIVQ).

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
make -C adsp2156/sport_fpga_tx
make -C adsp2156/sport_fpga_2x
make -C adsp2156/sport_fpga_4x
make -C adsp2156/sport_fpga_rx
make -C adsp2156/sport_fpga_rx4
make -C adsp2156/sport_fpga_bidir
make -C adsp2156/sport_fpga_bidir_2x2
mkdir -p fpga/build/sport
cd fpga && yosys -q -p "read_verilog verilog/sport_tx_prbs.v; synth_ice40 -top sport_tx_prbs -json build/sport/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport/s.json --pcf verilog/sport_tx_prbs_hx8k.pcf --asc build/sport/s.asc --freq 90 -q --pcf-allow-unconstrained && icepack build/sport/s.asc build/sport/sport_tx_prbs.bin
mkdir -p fpga/build/sport2x fpga/build/sport4x fpga/build/sport_rx2 fpga/build/sport_rx4 fpga/build/sport_bidir_1x1 fpga/build/sport_bidir_2x2
cd fpga && yosys -q -p "read_verilog verilog/sport_tx_prbs_multi.v; chparam -set N 2 sport_tx_prbs_multi; synth_ice40 -top sport_tx_prbs_multi -json build/sport2x/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport2x/s.json --pcf verilog/sport_tx_prbs_multi_hx8k.pcf --asc build/sport2x/s.asc --freq 90 -q --pcf-allow-unconstrained && icepack build/sport2x/s.asc build/sport2x/sport2x.bin
cd fpga && yosys -q -p "read_verilog verilog/sport_tx_prbs_multi.v; chparam -set N 4 sport_tx_prbs_multi; synth_ice40 -top sport_tx_prbs_multi -json build/sport4x/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport4x/s.json --pcf verilog/sport_tx_prbs_multi_4x_hx8k.pcf --asc build/sport4x/s.asc --freq 90 -q --pcf-allow-unconstrained && icepack build/sport4x/s.asc build/sport4x/sport4x.bin
cd fpga && yosys -q -p "read_verilog verilog/sport_rx.v verilog/uart_tx.v; chparam -set N 2 sport_rx; synth_ice40 -top sport_rx -json build/sport_rx2/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_rx2/s.json --pcf verilog/sport_rx_hx8k.pcf --asc build/sport_rx2/s.asc --freq 90 -q --pcf-allow-unconstrained && icepack build/sport_rx2/s.asc build/sport_rx2/sport_rx2.bin
cd fpga && yosys -q -p "read_verilog verilog/sport_rx.v verilog/uart_tx.v; chparam -set N 4 sport_rx; synth_ice40 -top sport_rx -json build/sport_rx4/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_rx4/s.json --pcf verilog/sport_rx4_hx8k.pcf --asc build/sport_rx4/s.asc --freq 90 -q --pcf-allow-unconstrained && icepack build/sport_rx4/s.asc build/sport_rx4/sport_rx4.bin
cd fpga && yosys -q -p "read_verilog verilog/sport_tx_prbs_multi.v verilog/sport_rx.v verilog/sport_bidir.v verilog/uart_tx.v; chparam -set TX_TO_DSP_N 1 sport_bidir; chparam -set RX_FROM_DSP_N 1 sport_bidir; synth_ice40 -top sport_bidir -json build/sport_bidir_1x1/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_bidir_1x1/s.json --pcf verilog/sport_bidir_1x1_hx8k.pcf --asc build/sport_bidir_1x1/s.asc --freq 90 -q --pcf-allow-unconstrained && icepack build/sport_bidir_1x1/s.asc build/sport_bidir_1x1/sport_bidir_1x1.bin
cd fpga && yosys -q -p "read_verilog verilog/sport_tx_prbs_multi.v verilog/sport_rx.v verilog/sport_bidir.v verilog/uart_tx.v; chparam -set TX_TO_DSP_N 2 sport_bidir; chparam -set RX_FROM_DSP_N 2 sport_bidir; synth_ice40 -top sport_bidir -json build/sport_bidir_2x2/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_bidir_2x2/s.json --pcf verilog/sport_bidir_2x2_hx8k.pcf --asc build/sport_bidir_2x2/s.asc --freq 90 -q --pcf-allow-unconstrained && icepack build/sport_bidir_2x2/s.asc build/sport_bidir_2x2/sport_bidir_2x2.bin
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport/sport_tx_prbs.bin
fpga/build/sport2x/sport2x.bin
fpga/build/sport4x/sport4x.bin
fpga/build/sport_rx2/sport_rx2.bin
fpga/build/sport_rx4/sport_rx4.bin
fpga/build/sport_bidir_1x1/sport_bidir_1x1.bin
fpga/build/sport_bidir_2x2/sport_bidir_2x2.bin
adsp2156/sport_fpga_tx/build/mainprbs64.ldr
adsp2156/sport_fpga_tx/build/mainprbs512.ldr
adsp2156/sport_fpga_tx/build/mainprbs2048.ldr
adsp2156/sport_fpga_2x/build/main.ldr
adsp2156/sport_fpga_4x/build/main.ldr
adsp2156/sport_fpga_rx/build/main.ldr
adsp2156/sport_fpga_rx4/build/main.ldr
adsp2156/sport_fpga_bidir/build/main.ldr
adsp2156/sport_fpga_bidir_2x2/build/main.ldr
```

Test: no hardware.

Verify:

```
def check(extract_dir):
    from pathlib import Path
    paths = (
        'fpga/build/blinky/hx8k/blinky.bin',
        'fpga/build/sport/sport_tx_prbs.bin',
        'fpga/build/sport2x/sport2x.bin',
        'fpga/build/sport4x/sport4x.bin',
        'fpga/build/sport_rx2/sport_rx2.bin',
        'fpga/build/sport_rx4/sport_rx4.bin',
        'fpga/build/sport_bidir_1x1/sport_bidir_1x1.bin',
        'fpga/build/sport_bidir_2x2/sport_bidir_2x2.bin',
        'adsp2156/sport_fpga_tx/build/mainprbs64.ldr',
        'adsp2156/sport_fpga_tx/build/mainprbs512.ldr',
        'adsp2156/sport_fpga_tx/build/mainprbs2048.ldr',
        'adsp2156/sport_fpga_2x/build/main.ldr',
        'adsp2156/sport_fpga_4x/build/main.ldr',
        'adsp2156/sport_fpga_rx/build/main.ldr',
        'adsp2156/sport_fpga_rx4/build/main.ldr',
        'adsp2156/sport_fpga_bidir/build/main.ldr',
        'adsp2156/sport_fpga_bidir_2x2/build/main.ldr',
    )
    for rel in paths:
        p = Path(rel)
        if not (p.exists() and p.stat().st_size > 0):
            return False
    return True
```

### Single-SPORT link integrity (64 MB)

Prove the SPORT link carries PRBS-31 error-free over 64 MB on the
current wiring. Blinky first, boot the receiver, swap in the streamer,
wait for the DSP's verification report, require `errors=0`.

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport/sport_tx_prbs.bin
adsp2156/sport_fpga_tx/build/mainprbs64.ldr
```

Test (max 6 min):

```
fpga.hx8k:program bin=@blinky.bin
dsp:reset
dsp:uart_open
dsp:boot ldr=@mainprbs64.ldr timeout_ms=15000
delay ms=600
fpga.hx8k:program bin=@sport_tx_prbs.bin
dsp:uart_expect sentinel="sport_fpga_tx_prbs_long bytes=" timeout_ms=60000
delay ms=200
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=sport_64mb
```

Verify:

```
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'dsp.uart')
    m = re.search(r'sport_fpga_tx_prbs_long bytes=(\d+) words=\d+ errors=(\d+).*?rate_bps=(\d+)', text)
    if not m:
        sys.stderr.write('no SPORT report on dsp.uart\n')
        return False
    nbytes, errors, fw_rate = int(m.group(1)), int(m.group(2)), int(m.group(3))
    ops = Verification.load_ops(extract_dir)
    programs = [op for op in ops if op.get('device') == 'fpga.hx8k'
                and op.get('verb') == 'program']
    expects = [op for op in ops if op.get('device') == 'dsp'
               and op.get('verb') == 'uart_expect']
    if len(programs) < 2 or not expects:
        sys.stderr.write('missing bench timing ops\n')
        return False
    elapsed = expects[0]['t_end'] - programs[1]['t_start']
    rate = int((nbytes * 8) / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'SPORT 64MB: bytes={nbytes} errors={errors} '
                     f'bench_elapsed_s={elapsed:.6f} bench_rate_bps={rate} '
                     f'({rate/1e6:.1f} Mbps) fw_rate_bps={fw_rate}\n')
    if nbytes == 67108864 and errors == 0:
        return True
    raise HardFail(f'64MB FAIL: bytes={nbytes} errors={errors}')
```

### Single-SPORT max error-free rate over 2 GB

The headline measurement: transfer the full **2 GB** and require zero
bit errors.

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport/sport_tx_prbs.bin
adsp2156/sport_fpga_tx/build/mainprbs2048.ldr
```

Test (max 6 min):

```
fpga.hx8k:program bin=@blinky.bin
dsp:reset
dsp:uart_open
dsp:boot ldr=@mainprbs2048.ldr timeout_ms=15000
delay ms=600
fpga.hx8k:program bin=@sport_tx_prbs.bin
dsp:uart_expect sentinel="sport_fpga_tx_prbs_long bytes=" timeout_ms=345000
delay ms=200
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=sport_2gb
```

Verify:

```
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'dsp.uart')
    m = re.search(r'sport_fpga_tx_prbs_long bytes=(\d+) words=\d+ errors=(\d+) firsterr=-?\d+ timeouts=(\d+) overruns=(\d+).*?rate_bps=(\d+)', text)
    if not m:
        sys.stderr.write('no SPORT report on dsp.uart\n')
        return False
    nbytes, errors, timeouts, overruns, fw_rate = (int(x) for x in m.groups())
    ops = Verification.load_ops(extract_dir)
    programs = [op for op in ops if op.get('device') == 'fpga.hx8k'
                and op.get('verb') == 'program']
    expects = [op for op in ops if op.get('device') == 'dsp'
               and op.get('verb') == 'uart_expect']
    if len(programs) < 2 or not expects:
        sys.stderr.write('missing bench timing ops\n')
        return False
    elapsed = expects[0]['t_end'] - programs[1]['t_start']
    rate = int((nbytes * 8) / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'SPORT 2GB: bytes={nbytes} errors={errors} '
                     f'timeouts={timeouts} overruns={overruns} '
                     f'bench_elapsed_s={elapsed:.6f} bench_rate_bps={rate} '
                     f'({rate/1e6:.1f} Mbps) fw_rate_bps={fw_rate}\n')
    if nbytes == 2147483648 and errors == 0 and timeouts == 0 and overruns == 0:
        return True
    raise HardFail(f'2GB FAIL: bytes={nbytes} errors={errors} '
                   f'timeouts={timeouts} overruns={overruns}')
```

### Two SPORTs: 2 x (FPGA -> DSP)

Double the data rate by receiving on SPORT4B + SPORT0B at once.  The
FPGA streams two synchronized PRBS-31 channels off one PLL.

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport2x/sport2x.bin
adsp2156/sport_fpga_2x/build/main.ldr
```

Test (max 6 min):

```
fpga.hx8k:program bin=@blinky.bin
dsp:reset
dsp:uart_open
dsp:boot ldr=@main.ldr timeout_ms=15000
delay ms=600
fpga.hx8k:program bin=@sport2x.bin
dsp:uart_expect sentinel="sport_2x agg_bytes=" timeout_ms=120000
delay ms=200
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=sport_2x
```

Verify:

```
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'dsp.uart')
    m = re.search(r'sport_2x agg_bytes=(\d+) per_ch_bytes=\d+ errors0=(\d+) errors1=(\d+) timeouts=(\d+) overruns=(\d+)', text)
    if not m:
        sys.stderr.write('no sport_2x report on dsp.uart\n')
        return False
    agg, e0, e1, to, ov = (int(x) for x in m.groups())
    ops = Verification.load_ops(extract_dir)
    programs = [op for op in ops if op.get('device') == 'fpga.hx8k'
                and op.get('verb') == 'program']
    expects = [op for op in ops if op.get('device') == 'dsp'
               and op.get('verb') == 'uart_expect']
    if len(programs) < 2 or not expects:
        sys.stderr.write('missing bench timing ops\n')
        return False
    elapsed = expects[0]['t_end'] - programs[1]['t_start']
    rate = int((agg * 8) / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'SPORT 2x: agg_bytes={agg} errors0={e0} errors1={e1} '
                     f'timeouts={to} overruns={ov} '
                     f'bench_elapsed_s={elapsed:.6f} bench_rate_bps={rate} '
                     f'({rate/1e6:.1f} Mbps)\n')
    if e0 == 0 and e1 == 0 and to == 0 and ov == 0 and agg >= 134217728:
        return True
    raise HardFail(f'2x FPGA->DSP FAIL: agg={agg} errors0={e0} errors1={e1} '
                   f'timeouts={to} overruns={ov}')
```

### Two SPORTs: 2 x (DSP -> FPGA)

Transmit two 64 MB PRBS lanes from the DSP into the FPGA receiver.  The
FPGA verifies both lanes and reports measured word/error counts on its
UART; the mission computes the aggregate Mbps from bench wall clock.

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_rx2/sport_rx2.bin
adsp2156/sport_fpga_rx/build/main.ldr
```

Test (max 6 min):

```
fpga.hx8k:program bin=@sport_rx2.bin
fpga.hx8k:uart_open
dsp:reset
dsp:uart_open
dsp:boot ldr=@main.ldr timeout_ms=15000
fpga.hx8k:uart_expect sentinel=" PASS" timeout_ms=180000
delay ms=200
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=sport_dsp_to_fpga_2x
```

Verify:

```
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'fpga.uart')
    m = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', text)
    if not m:
        sys.stderr.write('no sport_rx report on fpga.uart\n')
        return False
    lanes, min_words, errors = int(m.group(1)), int(m.group(2), 16), int(m.group(3), 16)
    nbytes = lanes * min_words * 4
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'fpga.hx8k'
               and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        sys.stderr.write('missing bench timing ops\n')
        return False
    elapsed = expects[0]['t_end'] - boots[0]['t_start']
    rate = int((nbytes * 8) / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'SPORT DSP->FPGA 2x: bytes={nbytes} lanes={lanes} '
                     f'per_ch_words={min_words} errors={errors} '
                     f'bench_elapsed_s={elapsed:.6f} bench_rate_bps={rate} '
                     f'({rate/1e6:.1f} Mbps)\n')
    return lanes == 2 and nbytes >= 134217728 and errors == 0 and m.group(4) == 'PASS'
```

### Two SPORTs: (DSP -> FPGA) and (FPGA -> DSP)

Run one SPORT lane in each direction at the same time.  The DSP verifies
the FPGA->DSP lane; the FPGA verifies the DSP->FPGA lane.

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_bidir_1x1/sport_bidir_1x1.bin
adsp2156/sport_fpga_bidir/build/main.ldr
```

Test (max 6 min):

```
fpga.hx8k:program bin=@sport_bidir_1x1.bin
fpga.hx8k:uart_open
dsp:reset
dsp:uart_open
dsp:boot ldr=@main.ldr timeout_ms=15000
fpga.hx8k:uart_expect sentinel=" PASS" timeout_ms=180000
dsp:uart_expect sentinel=" PASS" timeout_ms=30000
delay ms=200
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=sport_bidir_1x1
```

Verify:

```
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    ftxt = Verification.load_stream_text(extract_dir, 'fpga.uart')
    dtxt = Verification.load_stream_text(extract_dir, 'dsp.uart')
    fm = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', ftxt)
    dm = re.search(r'sport_bidir rx_lanes=(\d+) tx_lanes=(\d+) rx_bytes=(\d+) '
                   r'rx_errors=(\d+) timeouts=(\d+) tx_timeouts=(\d+) '
                   r'overruns=(\d+) rx_measured_rate_bps=(\d+) tx_sent=(\d+) '
                   r'tx_bytes=(\d+) (PASS|FAIL)', dtxt)
    if not fm or not dm:
        sys.stderr.write('missing bidirectional reports\n')
        return False
    fpga_lanes, fpga_words, fpga_errors = int(fm.group(1)), int(fm.group(2), 16), int(fm.group(3), 16)
    rx_lanes, tx_lanes, rx_bytes, rx_errors, to, txto, ov, _, tx_sent, tx_bytes = (
        int(dm.group(i)) for i in range(1, 11))
    total_bytes = rx_bytes + tx_bytes
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('verb') == 'uart_expect']
    if not boots or not expects:
        sys.stderr.write('missing bench timing ops\n')
        return False
    elapsed = max(op['t_end'] for op in expects) - boots[0]['t_start']
    rate = int((total_bytes * 8) / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'SPORT bidir 1x1: total_bytes={total_bytes} rx_bytes={rx_bytes} '
                     f'tx_bytes={tx_bytes} fpga_words={fpga_words} '
                     f'errors_fpga={fpga_errors} errors_dsp={rx_errors} '
                     f'timeouts={to} tx_timeouts={txto} overruns={ov} '
                     f'bench_elapsed_s={elapsed:.6f} bench_rate_bps={rate} '
                     f'({rate/1e6:.1f} Mbps)\n')
    return (fpga_lanes == 1 and rx_lanes == 1 and tx_lanes == 1 and
            rx_bytes >= 67108864 and tx_bytes >= 67108864 and
            fpga_errors == 0 and rx_errors == 0 and to == 0 and txto == 0 and
            ov == 0 and tx_sent >= 16777216 and fm.group(4) == 'PASS' and
            dm.group(11) == 'PASS')
```

### Four SPORTs: 4 x (FPGA -> DSP)

Receive four synchronized FPGA PRBS lanes on SPORT4B, SPORT0B, SPORT5B,
and SPORT1B.  Each lane transfers 64 MB; the aggregate payload is 256 MB.

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport4x/sport4x.bin
adsp2156/sport_fpga_4x/build/main.ldr
```

Test (max 6 min):

```
fpga.hx8k:program bin=@blinky.bin
dsp:reset
dsp:uart_open
dsp:boot ldr=@main.ldr timeout_ms=15000
delay ms=600
fpga.hx8k:program bin=@sport4x.bin
dsp:uart_expect sentinel=" PASS" timeout_ms=180000
delay ms=200
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=sport_fpga_to_dsp_4x
```

Verify:

```
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'dsp.uart')
    m = re.search(r'sport_4x agg_bytes=(\d+) per_ch_bytes=(\d+) errors0=(\d+) '
                  r'errors1=(\d+) errors2=(\d+) errors3=(\d+) timeouts=(\d+) '
                  r'overruns=(\d+)', text)
    if not m:
        sys.stderr.write('no sport_4x report on dsp.uart\n')
        return False
    agg, per_ch, e0, e1, e2, e3, to, ov = (int(x) for x in m.groups())
    ops = Verification.load_ops(extract_dir)
    programs = [op for op in ops if op.get('device') == 'fpga.hx8k'
                and op.get('verb') == 'program']
    expects = [op for op in ops if op.get('device') == 'dsp'
               and op.get('verb') == 'uart_expect']
    if len(programs) < 2 or not expects:
        sys.stderr.write('missing bench timing ops\n')
        return False
    elapsed = expects[0]['t_end'] - programs[1]['t_start']
    rate = int((agg * 8) / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'SPORT FPGA->DSP 4x: agg_bytes={agg} per_ch_bytes={per_ch} '
                     f'errors=({e0},{e1},{e2},{e3}) timeouts={to} overruns={ov} '
                     f'bench_elapsed_s={elapsed:.6f} bench_rate_bps={rate} '
                     f'({rate/1e6:.1f} Mbps)\n')
    return (agg >= 268435456 and per_ch >= 67108864 and
            e0 == e1 == e2 == e3 == 0 and to == 0 and ov == 0)
```

### Four SPORTs: 4 x (DSP -> FPGA)

Transmit four 64 MB DSP PRBS lanes into the FPGA receiver.  The FPGA
reports the minimum completed word count and total bit errors.

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_rx4/sport_rx4.bin
adsp2156/sport_fpga_rx4/build/main.ldr
```

Test (max 6 min):

```
fpga.hx8k:program bin=@sport_rx4.bin
fpga.hx8k:uart_open
dsp:reset
dsp:uart_open
dsp:boot ldr=@main.ldr timeout_ms=15000
fpga.hx8k:uart_expect sentinel=" PASS" timeout_ms=180000
delay ms=200
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=sport_dsp_to_fpga_4x
```

Verify:

```
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'fpga.uart')
    m = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', text)
    if not m:
        sys.stderr.write('no sport_rx report on fpga.uart\n')
        return False
    lanes, min_words, errors = int(m.group(1)), int(m.group(2), 16), int(m.group(3), 16)
    nbytes = lanes * min_words * 4
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'fpga.hx8k'
               and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        sys.stderr.write('missing bench timing ops\n')
        return False
    elapsed = expects[0]['t_end'] - boots[0]['t_start']
    rate = int((nbytes * 8) / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'SPORT DSP->FPGA 4x: bytes={nbytes} lanes={lanes} '
                     f'per_ch_words={min_words} errors={errors} '
                     f'bench_elapsed_s={elapsed:.6f} bench_rate_bps={rate} '
                     f'({rate/1e6:.1f} Mbps)\n')
    return lanes == 4 and nbytes >= 268435456 and errors == 0 and m.group(4) == 'PASS'
```

### Four SPORTs: 2 x (FPGA -> DSP) and 2x (DSP -> FPGA)

Run two SPORT lanes in each direction simultaneously.  The aggregate
payload is two 64 MB lanes received by the DSP plus two 64 MB lanes
received by the FPGA.

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_bidir_2x2/sport_bidir_2x2.bin
adsp2156/sport_fpga_bidir_2x2/build/main.ldr
```

Test (max 6 min):

```
fpga.hx8k:program bin=@sport_bidir_2x2.bin
fpga.hx8k:uart_open
dsp:reset
dsp:uart_open
dsp:boot ldr=@main.ldr timeout_ms=15000
fpga.hx8k:uart_expect sentinel=" PASS" timeout_ms=240000
dsp:uart_expect sentinel=" PASS" timeout_ms=30000
delay ms=200
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=sport_bidir_2x2
```

Verify:

```
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    ftxt = Verification.load_stream_text(extract_dir, 'fpga.uart')
    dtxt = Verification.load_stream_text(extract_dir, 'dsp.uart')
    fm = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', ftxt)
    dm = re.search(r'sport_bidir rx_lanes=(\d+) tx_lanes=(\d+) rx_bytes=(\d+) '
                   r'rx_errors=(\d+) timeouts=(\d+) tx_timeouts=(\d+) '
                   r'overruns=(\d+) rx_measured_rate_bps=(\d+) tx_sent=(\d+) '
                   r'tx_bytes=(\d+) (PASS|FAIL)', dtxt)
    if not fm or not dm:
        sys.stderr.write('missing bidirectional reports\n')
        return False
    fpga_lanes, fpga_words, fpga_errors = int(fm.group(1)), int(fm.group(2), 16), int(fm.group(3), 16)
    rx_lanes, tx_lanes, rx_bytes, rx_errors, to, txto, ov, _, tx_sent, tx_bytes = (
        int(dm.group(i)) for i in range(1, 11))
    total_bytes = rx_bytes + tx_bytes
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('verb') == 'uart_expect']
    if not boots or not expects:
        sys.stderr.write('missing bench timing ops\n')
        return False
    elapsed = max(op['t_end'] for op in expects) - boots[0]['t_start']
    rate = int((total_bytes * 8) / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'SPORT bidir 2x2: total_bytes={total_bytes} rx_bytes={rx_bytes} '
                     f'tx_bytes={tx_bytes} fpga_words={fpga_words} '
                     f'errors_fpga={fpga_errors} errors_dsp={rx_errors} '
                     f'timeouts={to} tx_timeouts={txto} overruns={ov} '
                     f'bench_elapsed_s={elapsed:.6f} bench_rate_bps={rate} '
                     f'({rate/1e6:.1f} Mbps)\n')
    return (fpga_lanes == 2 and rx_lanes == 2 and tx_lanes == 2 and
            rx_bytes >= 134217728 and tx_bytes >= 134217728 and
            fpga_errors == 0 and rx_errors == 0 and to == 0 and txto == 0 and
            ov == 0 and tx_sent >= 16777216 and fm.group(4) == 'PASS' and
            dm.group(11) == 'PASS')
```
