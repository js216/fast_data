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
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'dsp.uart')
    m = re.search(r'sport_4x agg_bytes=(\d+) per_ch_bytes=(\d+) errors0=(\d+) errors1=(\d+) errors2=(\d+) errors3=(\d+).*? timeouts=(\d+) overruns=(\d+) (PASS|FAIL)', text)
    if not m:
        raise HardFail('no sport_4x report')
    agg, pc, e0, e1, e2, e3, to, ov = (int(x) for x in m.groups()[:8])
    sys.stderr.write(f'per_ch_bytes={pc} errors=({e0},{e1},{e2},{e3}) timeouts={to} overruns={ov} {m.group(9)}\n')
    if (pc >= 128 and e0 == e1 == e2 == e3 == 0 and to == 0 and ov == 0 and m.group(9) == 'PASS'):
        return True
    raise HardFail(f'FAIL: per_ch={pc} errors=({e0},{e1},{e2},{e3}) timeouts={to}')
```

#### (stale open-loop design, superseded by the pair-shared recipe) FFFF-DDDD 1MiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport4x
cd fpga && yosys -q -p "read_verilog -D SPORT_TX_POSEDGE_OUT verilog/sport_tx_from_dsp_clk.v; chparam -set N 4 sport_tx_from_dsp_clk; synth_ice40 -top sport_tx_from_dsp_clk -json build/sport4x/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport4x/s.json --pcf verilog/sport_tx_prbs_multi_4x_hx8k.pcf --asc build/sport4x/s.asc --freq 40 -q --pcf-allow-unconstrained && icepack build/sport4x/s.asc build/sport4x/sport4x.bin
make -C adsp2156/sport_fpga_4x clean
make -j -C adsp2156/sport_fpga_4x CFLAGS_EXTRA="-DTOTAL_WORDS=262144U"
cp adsp2156/sport_fpga_4x/build/main.ldr adsp2156/sport_fpga_4x/build/m4x_1mib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport4x/sport4x.bin
adsp2156/sport_fpga_4x/build/m4x_1mib.ldr
```

Test (max 6 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@blinky.bin
fpga.hx8k:program bin=@sport4x.bin
dsp:uart_open
dsp:boot ldr=@m4x_1mib.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_4x agg_bytes=" timeout_ms=15000
delay ms=200
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=ffff_dddd_1mib
```

Verify:

```
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'dsp.uart')
    m = re.search(r'sport_4x agg_bytes=(\d+) per_ch_bytes=(\d+) errors0=(\d+) errors1=(\d+) errors2=(\d+) errors3=(\d+).*? timeouts=(\d+) overruns=(\d+) (PASS|FAIL)', text)
    if not m:
        raise HardFail('no sport_4x report')
    agg, pc, e0, e1, e2, e3, to, ov = (int(x) for x in m.groups()[:8])
    sys.stderr.write(f'per_ch_bytes={pc} errors=({e0},{e1},{e2},{e3}) timeouts={to} overruns={ov} {m.group(9)}\n')
    if (pc >= 1048576 and e0 == e1 == e2 == e3 == 0 and to == 0 and ov == 0 and m.group(9) == 'PASS'):
        return True
    raise HardFail(f'FAIL: per_ch={pc} errors=({e0},{e1},{e2},{e3}) timeouts={to}')
```

#### (stale open-loop design, superseded by the pair-shared recipe) FFFF-DDDD 64MiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport4x
cd fpga && yosys -q -p "read_verilog -D SPORT_TX_POSEDGE_OUT verilog/sport_tx_from_dsp_clk.v; chparam -set N 4 sport_tx_from_dsp_clk; synth_ice40 -top sport_tx_from_dsp_clk -json build/sport4x/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport4x/s.json --pcf verilog/sport_tx_prbs_multi_4x_hx8k.pcf --asc build/sport4x/s.asc --freq 40 -q --pcf-allow-unconstrained && icepack build/sport4x/s.asc build/sport4x/sport4x.bin
make -C adsp2156/sport_fpga_4x clean
make -j -C adsp2156/sport_fpga_4x CFLAGS_EXTRA="-DTOTAL_WORDS=16777216U"
cp adsp2156/sport_fpga_4x/build/main.ldr adsp2156/sport_fpga_4x/build/m4x_64mib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport4x/sport4x.bin
adsp2156/sport_fpga_4x/build/m4x_64mib.ldr
```

Test (max 8 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@blinky.bin
fpga.hx8k:program bin=@sport4x.bin
dsp:uart_open
dsp:boot ldr=@m4x_64mib.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_4x agg_bytes=" timeout_ms=60000
delay ms=200
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=ffff_dddd_64mib
```

Verify:

```
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'dsp.uart')
    m = re.search(r'sport_4x agg_bytes=(\d+) per_ch_bytes=(\d+) errors0=(\d+) errors1=(\d+) errors2=(\d+) errors3=(\d+).*? timeouts=(\d+) overruns=(\d+) (PASS|FAIL)', text)
    if not m:
        raise HardFail('no sport_4x report')
    agg, pc, e0, e1, e2, e3, to, ov = (int(x) for x in m.groups()[:8])
    sys.stderr.write(f'per_ch_bytes={pc} errors=({e0},{e1},{e2},{e3}) timeouts={to} overruns={ov} {m.group(9)}\n')
    if (pc >= 67108864 and e0 == e1 == e2 == e3 == 0 and to == 0 and ov == 0 and m.group(9) == 'PASS'):
        return True
    raise HardFail(f'FAIL: per_ch={pc} errors=({e0},{e1},{e2},{e3}) timeouts={to}')
```

#### (stale open-loop design, superseded by the pair-shared recipe) FFFF-DDDD 256MiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport4x
cd fpga && yosys -q -p "read_verilog -D SPORT_TX_POSEDGE_OUT verilog/sport_tx_from_dsp_clk.v; chparam -set N 4 sport_tx_from_dsp_clk; synth_ice40 -top sport_tx_from_dsp_clk -json build/sport4x/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport4x/s.json --pcf verilog/sport_tx_prbs_multi_4x_hx8k.pcf --asc build/sport4x/s.asc --freq 40 -q --pcf-allow-unconstrained && icepack build/sport4x/s.asc build/sport4x/sport4x.bin
make -C adsp2156/sport_fpga_4x clean
make -j -C adsp2156/sport_fpga_4x CFLAGS_EXTRA="-DTOTAL_WORDS=67108864U"
cp adsp2156/sport_fpga_4x/build/main.ldr adsp2156/sport_fpga_4x/build/m4x_256mib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport4x/sport4x.bin
adsp2156/sport_fpga_4x/build/m4x_256mib.ldr
```

Test (max 10 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@blinky.bin
fpga.hx8k:program bin=@sport4x.bin
dsp:uart_open
dsp:boot ldr=@m4x_256mib.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_4x agg_bytes=" timeout_ms=120000
delay ms=200
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=ffff_dddd_256mib
```

Verify:

```
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'dsp.uart')
    m = re.search(r'sport_4x agg_bytes=(\d+) per_ch_bytes=(\d+) errors0=(\d+) errors1=(\d+) errors2=(\d+) errors3=(\d+).*? timeouts=(\d+) overruns=(\d+) (PASS|FAIL)', text)
    if not m:
        raise HardFail('no sport_4x report')
    agg, pc, e0, e1, e2, e3, to, ov = (int(x) for x in m.groups()[:8])
    sys.stderr.write(f'per_ch_bytes={pc} errors=({e0},{e1},{e2},{e3}) timeouts={to} overruns={ov} {m.group(9)}\n')
    if (pc >= 268435456 and e0 == e1 == e2 == e3 == 0 and to == 0 and ov == 0 and m.group(9) == 'PASS'):
        return True
    raise HardFail(f'FAIL: per_ch={pc} errors=({e0},{e1},{e2},{e3}) timeouts={to}')
```

#### (stale open-loop design, superseded by the pair-shared recipe) FFFF-DDDD 512MiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport4x
cd fpga && yosys -q -p "read_verilog -D SPORT_TX_POSEDGE_OUT verilog/sport_tx_from_dsp_clk.v; chparam -set N 4 sport_tx_from_dsp_clk; synth_ice40 -top sport_tx_from_dsp_clk -json build/sport4x/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport4x/s.json --pcf verilog/sport_tx_prbs_multi_4x_hx8k.pcf --asc build/sport4x/s.asc --freq 40 -q --pcf-allow-unconstrained && icepack build/sport4x/s.asc build/sport4x/sport4x.bin
make -C adsp2156/sport_fpga_4x clean
make -j -C adsp2156/sport_fpga_4x CFLAGS_EXTRA="-DTOTAL_WORDS=134217728U"
cp adsp2156/sport_fpga_4x/build/main.ldr adsp2156/sport_fpga_4x/build/m4x_512mib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport4x/sport4x.bin
adsp2156/sport_fpga_4x/build/m4x_512mib.ldr
```

Test (max 14 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@blinky.bin
fpga.hx8k:program bin=@sport4x.bin
dsp:uart_open
dsp:boot ldr=@m4x_512mib.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_4x agg_bytes=" timeout_ms=210000
delay ms=200
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=ffff_dddd_512mib
```

Verify:

```
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'dsp.uart')
    m = re.search(r'sport_4x agg_bytes=(\d+) per_ch_bytes=(\d+) errors0=(\d+) errors1=(\d+) errors2=(\d+) errors3=(\d+).*? timeouts=(\d+) overruns=(\d+) (PASS|FAIL)', text)
    if not m:
        raise HardFail('no sport_4x report')
    agg, pc, e0, e1, e2, e3, to, ov = (int(x) for x in m.groups()[:8])
    sys.stderr.write(f'per_ch_bytes={pc} errors=({e0},{e1},{e2},{e3}) timeouts={to} overruns={ov} {m.group(9)}\n')
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[0]['t_end'] - boots[0]['t_start']
    rate = int(pc * 8 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'per_lane bps={rate} ({rate/1e6:.1f} Mbps)\n')
    if rate < 28000000:
        raise HardFail(f'rate {rate} < 28000000')
    if (pc >= 536870912 and e0 == e1 == e2 == e3 == 0 and to == 0 and ov == 0 and m.group(9) == 'PASS'):
        return True
    raise HardFail(f'FAIL: per_ch={pc} errors=({e0},{e1},{e2},{e3}) timeouts={to}')
```

#### (stale open-loop design, superseded by the pair-shared recipe) FFFF-DDDD 1GiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport4x
cd fpga && yosys -q -p "read_verilog -D SPORT_TX_POSEDGE_OUT verilog/sport_tx_from_dsp_clk.v; chparam -set N 4 sport_tx_from_dsp_clk; synth_ice40 -top sport_tx_from_dsp_clk -json build/sport4x/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport4x/s.json --pcf verilog/sport_tx_prbs_multi_4x_hx8k.pcf --asc build/sport4x/s.asc --freq 40 -q --pcf-allow-unconstrained && icepack build/sport4x/s.asc build/sport4x/sport4x.bin
make -C adsp2156/sport_fpga_4x clean
make -j -C adsp2156/sport_fpga_4x CFLAGS_EXTRA="-DTOTAL_WORDS=268435456U"
cp adsp2156/sport_fpga_4x/build/main.ldr adsp2156/sport_fpga_4x/build/m4x_1gib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport4x/sport4x.bin
adsp2156/sport_fpga_4x/build/m4x_1gib.ldr
```

Test (max 18 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@blinky.bin
fpga.hx8k:program bin=@sport4x.bin
dsp:uart_open
dsp:boot ldr=@m4x_1gib.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_4x agg_bytes=" timeout_ms=390000
delay ms=200
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=ffff_dddd_1gib
```

Verify:

```
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'dsp.uart')
    m = re.search(r'sport_4x agg_bytes=(\d+) per_ch_bytes=(\d+) errors0=(\d+) errors1=(\d+) errors2=(\d+) errors3=(\d+).*? timeouts=(\d+) overruns=(\d+) (PASS|FAIL)', text)
    if not m:
        raise HardFail('no sport_4x report')
    agg, pc, e0, e1, e2, e3, to, ov = (int(x) for x in m.groups()[:8])
    sys.stderr.write(f'per_ch_bytes={pc} errors=({e0},{e1},{e2},{e3}) timeouts={to} overruns={ov} {m.group(9)}\n')
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[0]['t_end'] - boots[0]['t_start']
    rate = int(pc * 8 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'per_lane bps={rate} ({rate/1e6:.1f} Mbps)\n')
    if rate < 28000000:
        raise HardFail(f'rate {rate} < 28000000')
    if (pc >= 1073741824 and e0 == e1 == e2 == e3 == 0 and to == 0 and ov == 0 and m.group(9) == 'PASS'):
        return True
    raise HardFail(f'FAIL: per_ch={pc} errors=({e0},{e1},{e2},{e3}) timeouts={to}')
```

### FFFF-DDDD 2GiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
make -C adsp2156/sport_fpga_bidir clean
make -j -C adsp2156/sport_fpga_bidir CFLAGS_EXTRA="-DRX_N=4U -DTX_N=2U -DTOTAL_WORDS=536870912U -DTX_NO_REFILL"
cp adsp2156/sport_fpga_bidir/build/main.ldr adsp2156/sport_fpga_bidir/build/ffff2gib.ldr
mkdir -p fpga/build/sport_bidir_4x
cd fpga && yosys -q -p "read_verilog -D EYE_DELAY verilog/sport_tx_sync_nopll.v verilog/sport_tx_prbs_ser.v verilog/sport_rx.v verilog/sport_bidir.v verilog/uart_tx.v; chparam -set TX_TO_DSP_N 4 -set RX_FROM_DSP_N 2 -set SYNC_TX 1 -set NOPLL 1 -set SHARE_PAIRS 1 -set REPORT_LANE0 0 -set MIN_DONE_WORDS 536870912 sport_bidir; synth_ice40 -top sport_bidir -json build/sport_bidir_4x/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_bidir_4x/s.json --pcf verilog/sport_bidir_4x_hx8k.pcf --asc build/sport_bidir_4x/s.asc --freq 62 --seed 9 -q --pcf-allow-unconstrained && icepack build/sport_bidir_4x/s.asc build/sport_bidir_4x/sport_bidir_4x.bin
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
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
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
    sys.stderr.write(f'FFFF->DDDD lanes={lanes} words={words} errors={errs} ov={ov} slips={slips} per_lane_rate={rate/1e6:.1f} Mbps\n')
    if (lanes == 4 and words == 536870912 and errs == 0 and to == 0
            and txto == 0 and ov == 0 and rate >= 30000000):
        return True
    raise HardFail(f'FFFF-DDDD: errors={errs} ov={ov} words={words}')
```

#### (stale open-loop design, superseded by the pair-shared recipe) FFFF-DDDD 4GiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport4x
cd fpga && yosys -q -p "read_verilog -D SPORT_TX_POSEDGE_OUT verilog/sport_tx_from_dsp_clk.v; chparam -set N 4 sport_tx_from_dsp_clk; synth_ice40 -top sport_tx_from_dsp_clk -json build/sport4x/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport4x/s.json --pcf verilog/sport_tx_prbs_multi_4x_hx8k.pcf --asc build/sport4x/s.asc --freq 40 -q --pcf-allow-unconstrained && icepack build/sport4x/s.asc build/sport4x/sport4x.bin
make -C adsp2156/sport_fpga_4x clean
make -j -C adsp2156/sport_fpga_4x CFLAGS_EXTRA="-DTOTAL_WORDS=1073741824U"
cp adsp2156/sport_fpga_4x/build/main.ldr adsp2156/sport_fpga_4x/build/m4x_4gib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport4x/sport4x.bin
adsp2156/sport_fpga_4x/build/m4x_4gib.ldr
```

Test (max 28 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@blinky.bin
fpga.hx8k:program bin=@sport4x.bin
dsp:uart_open
dsp:boot ldr=@m4x_4gib.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_4x agg_bytes=" timeout_ms=1410000
delay ms=200
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=ffff_dddd_4gib
```

Verify:

```
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'dsp.uart')
    m = re.search(r'sport_4x agg_bytes=(\d+) per_ch_bytes=(\d+) errors0=(\d+) errors1=(\d+) errors2=(\d+) errors3=(\d+).*? timeouts=(\d+) overruns=(\d+) (PASS|FAIL)', text)
    if not m:
        raise HardFail('no sport_4x report')
    agg, pc, e0, e1, e2, e3, to, ov = (int(x) for x in m.groups()[:8])
    sys.stderr.write(f'per_ch_bytes={pc} errors=({e0},{e1},{e2},{e3}) timeouts={to} overruns={ov} {m.group(9)}\n')
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[0]['t_end'] - boots[0]['t_start']
    rate = int(pc * 8 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'per_lane bps={rate} ({rate/1e6:.1f} Mbps)\n')
    if rate < 30000000:
        raise HardFail(f'rate {rate} < 30000000')
    if (pc >= 4294967296 and e0 == e1 == e2 == e3 == 0 and to == 0 and ov == 0 and m.group(9) == 'PASS'):
        return True
    raise HardFail(f'FAIL: per_ch={pc} errors=({e0},{e1},{e2},{e3}) timeouts={to}')
```

