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
mkdir -p fpga/build/sport
cd fpga && yosys -q -p "read_verilog verilog/sport_tx_prbs.v; synth_ice40 -top sport_tx_prbs -json build/sport/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport/s.json --pcf verilog/sport_tx_prbs_hx8k.pcf --asc build/sport/s.asc --freq 90 -q --pcf-allow-unconstrained && icepack build/sport/s.asc build/sport/sport_tx_prbs.bin
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport/sport_tx_prbs.bin
adsp2156/sport_fpga_tx/build/mainprbs64.ldr
adsp2156/sport_fpga_tx/build/mainprbs512.ldr
adsp2156/sport_fpga_tx/build/mainprbs2048.ldr
```

Test: no hardware.

Verify:

```
def check(extract_dir):
    from pathlib import Path
    for k in ('blinky.bin', 'sport_tx_prbs.bin', 'mainprbs64.ldr',
              'mainprbs512.ldr', 'mainprbs2048.ldr'):
        p = Path(artifacts[k])
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

Test (max 3 min):

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
    nbytes, errors, rate = int(m.group(1)), int(m.group(2)), int(m.group(3))
    sys.stderr.write(f'SPORT 64MB: bytes={nbytes} errors={errors} rate_bps={rate}\n')
    return nbytes == 67108864 and errors == 0
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

Test (max 10 min):

```
fpga.hx8k:program bin=@blinky.bin
dsp:reset
dsp:uart_open
dsp:boot ldr=@mainprbs2048.ldr timeout_ms=15000
delay ms=600
fpga.hx8k:program bin=@sport_tx_prbs.bin
dsp:uart_expect sentinel="sport_fpga_tx_prbs_long bytes=" timeout_ms=420000
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
    nbytes, errors, timeouts, overruns, rate = (int(x) for x in m.groups())
    sys.stderr.write(f'SPORT 2GB: bytes={nbytes} errors={errors} '
                     f'timeouts={timeouts} overruns={overruns} '
                     f'rate_bps={rate} ({rate/1e6:.1f} Mbps)\n')
    return nbytes == 2147483648 and errors == 0 and timeouts == 0 and overruns == 0
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

Test (max 5 min):

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
    m = re.search(r'sport_2x agg_bytes=(\d+) per_ch_bytes=\d+ errors0=(\d+) errors1=(\d+) timeouts=(\d+) overruns=(\d+) agg_rate_bps=(\d+)', text)
    if not m:
        sys.stderr.write('no sport_2x report on dsp.uart\n')
        return False
    agg, e0, e1, to, ov, rate = (int(x) for x in m.groups())
    sys.stderr.write(f'SPORT 2x: agg_bytes={agg} errors0={e0} errors1={e1} '
                     f'timeouts={to} overruns={ov} agg_rate_bps={rate} '
                     f'({rate/1e6:.1f} Mbps)\n')
    return e0 == 0 and e1 == 0 and to == 0 and ov == 0 and agg > 0
```

### Two SPORTs: 2 x (DSP -> FPGA)

### Two SPORTs: (DSP -> FPGA) and (FPGA -> DSP)

### Four SPORTs: 4 x (FPGA -> DSP)

### Four SPORTs: 4 x (DSP -> FPGA)

### Four SPORTs: 2 x (FPGA -> DSP) and 2x (DSP -> FPGA)
