# F-D direction ladder (FPGA -> DSP, 1 lane)
#### F-D 128B

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport
cd fpga && yosys -q -p "read_verilog -D SPORT_TX_POSEDGE_OUT verilog/sport_tx_from_dsp_clk.v; chparam -set N 1 sport_tx_from_dsp_clk; synth_ice40 -top sport_tx_from_dsp_clk -json build/sport/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport/s.json --pcf verilog/sport_tx_prbs_hx8k.pcf --asc build/sport/s.asc --freq 40 -q --pcf-allow-unconstrained && icepack build/sport/s.asc build/sport/sport_tx_prbs.bin
make -C adsp2156/sport_fpga_tx clean
make -j -C adsp2156/sport_fpga_tx build/main.ldr CFLAGS_EXTRA="-DTOTAL_BYTES=128ULL -DTOTAL_WORDS=32U -DRX_SAMPLE_RISING=1 -DRX_SHIFT_LEFT_1=1 -DSPORT_FSDIV=31U"
cp adsp2156/sport_fpga_tx/build/main.ldr adsp2156/sport_fpga_tx/build/fd_128b.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport/sport_tx_prbs.bin
adsp2156/sport_fpga_tx/build/fd_128b.ldr
```

Test (max 6 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@blinky.bin
fpga.hx8k:program bin=@sport_tx_prbs.bin
dsp:uart_open
dsp:boot ldr=@fd_128b.ldr timeout_ms=30000
dsp:uart_expect sentinel="sport_fpga_tx_prbs_long bytes=" timeout_ms=15000
delay ms=200
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=f_d_128b
```

Verify:

```
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'dsp.uart')
    m = re.search(r'sport_fpga_tx_prbs_long bytes=(\d+) words=\d+ errors=(\d+) firsterr=-?\d+.*? timeouts=(\d+) overruns=(\d+).*? (PASS|FAIL)', text)
    if not m:
        raise HardFail('no SPORT report on dsp.uart')
    nbytes, errors, timeouts, overruns = (int(x) for x in m.groups()[:4])
    sys.stderr.write(f'bytes={nbytes} errors={errors} timeouts={timeouts} overruns={overruns} {m.group(5)}\n')
    if nbytes >= 128 and errors == 0 and timeouts == 0 and overruns == 0 and m.group(5) == 'PASS':
        return True
    raise HardFail(f'FAIL: bytes={nbytes} errors={errors} timeouts={timeouts} overruns={overruns}')
```

### F-D 1MiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport
cd fpga && yosys -q -p "read_verilog -D SPORT_TX_POSEDGE_OUT verilog/sport_tx_from_dsp_clk.v; chparam -set N 1 sport_tx_from_dsp_clk; synth_ice40 -top sport_tx_from_dsp_clk -json build/sport/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport/s.json --pcf verilog/sport_tx_prbs_hx8k.pcf --asc build/sport/s.asc --freq 40 -q --pcf-allow-unconstrained && icepack build/sport/s.asc build/sport/sport_tx_prbs.bin
make -C adsp2156/sport_fpga_tx clean
make -j -C adsp2156/sport_fpga_tx build/main.ldr CFLAGS_EXTRA="-DTOTAL_BYTES=1048576ULL -DTOTAL_WORDS=262144U -DRX_SAMPLE_RISING=1 -DRX_SHIFT_LEFT_1=1 -DSPORT_FSDIV=31U"
cp adsp2156/sport_fpga_tx/build/main.ldr adsp2156/sport_fpga_tx/build/fd_1mib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport/sport_tx_prbs.bin
adsp2156/sport_fpga_tx/build/fd_1mib.ldr
```

Test (max 6 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@blinky.bin
fpga.hx8k:program bin=@sport_tx_prbs.bin
dsp:uart_open
dsp:boot ldr=@fd_1mib.ldr timeout_ms=30000
dsp:uart_expect sentinel="sport_fpga_tx_prbs_long bytes=" timeout_ms=15000
delay ms=200
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=f_d_1mib
```

Verify:

```
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'dsp.uart')
    m = re.search(r'sport_fpga_tx_prbs_long bytes=(\d+) words=\d+ errors=(\d+) firsterr=-?\d+.*? timeouts=(\d+) overruns=(\d+).*? (PASS|FAIL)', text)
    if not m:
        raise HardFail('no SPORT report on dsp.uart')
    nbytes, errors, timeouts, overruns = (int(x) for x in m.groups()[:4])
    sys.stderr.write(f'bytes={nbytes} errors={errors} timeouts={timeouts} overruns={overruns} {m.group(5)}\n')
    if nbytes >= 1048576 and errors == 0 and timeouts == 0 and overruns == 0 and m.group(5) == 'PASS':
        return True
    raise HardFail(f'FAIL: bytes={nbytes} errors={errors} timeouts={timeouts} overruns={overruns}')
```

### F-D 64MiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport
cd fpga && yosys -q -p "read_verilog -D SPORT_TX_POSEDGE_OUT verilog/sport_tx_from_dsp_clk.v; chparam -set N 1 sport_tx_from_dsp_clk; synth_ice40 -top sport_tx_from_dsp_clk -json build/sport/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport/s.json --pcf verilog/sport_tx_prbs_hx8k.pcf --asc build/sport/s.asc --freq 40 -q --pcf-allow-unconstrained && icepack build/sport/s.asc build/sport/sport_tx_prbs.bin
make -C adsp2156/sport_fpga_tx clean
make -j -C adsp2156/sport_fpga_tx build/main.ldr CFLAGS_EXTRA="-DTOTAL_BYTES=67108864ULL -DTOTAL_WORDS=16777216U -DRX_SAMPLE_RISING=1 -DRX_SHIFT_LEFT_1=1 -DSPORT_FSDIV=31U"
cp adsp2156/sport_fpga_tx/build/main.ldr adsp2156/sport_fpga_tx/build/fd_64mib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport/sport_tx_prbs.bin
adsp2156/sport_fpga_tx/build/fd_64mib.ldr
```

Test (max 8 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@blinky.bin
fpga.hx8k:program bin=@sport_tx_prbs.bin
dsp:uart_open
dsp:boot ldr=@fd_64mib.ldr timeout_ms=30000
dsp:uart_expect sentinel="sport_fpga_tx_prbs_long bytes=" timeout_ms=60000
delay ms=200
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=f_d_64mib
```

Verify:

```
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'dsp.uart')
    m = re.search(r'sport_fpga_tx_prbs_long bytes=(\d+) words=\d+ errors=(\d+) firsterr=-?\d+.*? timeouts=(\d+) overruns=(\d+).*? (PASS|FAIL)', text)
    if not m:
        raise HardFail('no SPORT report on dsp.uart')
    nbytes, errors, timeouts, overruns = (int(x) for x in m.groups()[:4])
    sys.stderr.write(f'bytes={nbytes} errors={errors} timeouts={timeouts} overruns={overruns} {m.group(5)}\n')
    if nbytes >= 67108864 and errors == 0 and timeouts == 0 and overruns == 0 and m.group(5) == 'PASS':
        return True
    raise HardFail(f'FAIL: bytes={nbytes} errors={errors} timeouts={timeouts} overruns={overruns}')
```

### F-D 256MiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport
cd fpga && yosys -q -p "read_verilog -D SPORT_TX_POSEDGE_OUT verilog/sport_tx_from_dsp_clk.v; chparam -set N 1 sport_tx_from_dsp_clk; synth_ice40 -top sport_tx_from_dsp_clk -json build/sport/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport/s.json --pcf verilog/sport_tx_prbs_hx8k.pcf --asc build/sport/s.asc --freq 40 -q --pcf-allow-unconstrained && icepack build/sport/s.asc build/sport/sport_tx_prbs.bin
make -C adsp2156/sport_fpga_tx clean
make -j -C adsp2156/sport_fpga_tx build/main.ldr CFLAGS_EXTRA="-DTOTAL_BYTES=268435456ULL -DTOTAL_WORDS=67108864U -DRX_SAMPLE_RISING=1 -DRX_SHIFT_LEFT_1=1 -DSPORT_FSDIV=31U"
cp adsp2156/sport_fpga_tx/build/main.ldr adsp2156/sport_fpga_tx/build/fd_256mib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport/sport_tx_prbs.bin
adsp2156/sport_fpga_tx/build/fd_256mib.ldr
```

Test (max 10 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@blinky.bin
fpga.hx8k:program bin=@sport_tx_prbs.bin
dsp:uart_open
dsp:boot ldr=@fd_256mib.ldr timeout_ms=30000
dsp:uart_expect sentinel="sport_fpga_tx_prbs_long bytes=" timeout_ms=120000
delay ms=200
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=f_d_256mib
```

Verify:

```
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'dsp.uart')
    m = re.search(r'sport_fpga_tx_prbs_long bytes=(\d+) words=\d+ errors=(\d+) firsterr=-?\d+.*? timeouts=(\d+) overruns=(\d+).*? (PASS|FAIL)', text)
    if not m:
        raise HardFail('no SPORT report on dsp.uart')
    nbytes, errors, timeouts, overruns = (int(x) for x in m.groups()[:4])
    sys.stderr.write(f'bytes={nbytes} errors={errors} timeouts={timeouts} overruns={overruns} {m.group(5)}\n')
    if nbytes >= 268435456 and errors == 0 and timeouts == 0 and overruns == 0 and m.group(5) == 'PASS':
        return True
    raise HardFail(f'FAIL: bytes={nbytes} errors={errors} timeouts={timeouts} overruns={overruns}')
```

### F-D 512MiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport
cd fpga && yosys -q -p "read_verilog -D SPORT_TX_POSEDGE_OUT verilog/sport_tx_from_dsp_clk.v; chparam -set N 1 sport_tx_from_dsp_clk; synth_ice40 -top sport_tx_from_dsp_clk -json build/sport/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport/s.json --pcf verilog/sport_tx_prbs_hx8k.pcf --asc build/sport/s.asc --freq 40 -q --pcf-allow-unconstrained && icepack build/sport/s.asc build/sport/sport_tx_prbs.bin
make -C adsp2156/sport_fpga_tx clean
make -j -C adsp2156/sport_fpga_tx build/main.ldr CFLAGS_EXTRA="-DTOTAL_BYTES=536870912ULL -DTOTAL_WORDS=134217728U -DRX_SAMPLE_RISING=1 -DRX_SHIFT_LEFT_1=1 -DSPORT_FSDIV=31U"
cp adsp2156/sport_fpga_tx/build/main.ldr adsp2156/sport_fpga_tx/build/fd_512mib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport/sport_tx_prbs.bin
adsp2156/sport_fpga_tx/build/fd_512mib.ldr
```

Test (max 14 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@blinky.bin
fpga.hx8k:program bin=@sport_tx_prbs.bin
dsp:uart_open
dsp:boot ldr=@fd_512mib.ldr timeout_ms=30000
dsp:uart_expect sentinel="sport_fpga_tx_prbs_long bytes=" timeout_ms=210000
delay ms=200
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=f_d_512mib
```

Verify:

```
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'dsp.uart')
    m = re.search(r'sport_fpga_tx_prbs_long bytes=(\d+) words=\d+ errors=(\d+) firsterr=-?\d+.*? timeouts=(\d+) overruns=(\d+).*? (PASS|FAIL)', text)
    if not m:
        raise HardFail('no SPORT report on dsp.uart')
    nbytes, errors, timeouts, overruns = (int(x) for x in m.groups()[:4])
    sys.stderr.write(f'bytes={nbytes} errors={errors} timeouts={timeouts} overruns={overruns} {m.group(5)}\n')
    ops = Verification.load_ops(extract_dir)
    programs = [op for op in ops if op.get('device') == 'fpga.hx8k' and op.get('verb') == 'program']
    expects = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'uart_expect']
    if len(programs) < 2 or not expects:
        return False
    elapsed = expects[0]['t_end'] - programs[1]['t_start']
    rate = int(nbytes * 8 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'rate bps={rate} ({rate/1e6:.1f} Mbps)\n')
    if rate < 28000000:
        raise HardFail(f'rate {rate} < 28000000')
    if nbytes >= 536870912 and errors == 0 and timeouts == 0 and overruns == 0 and m.group(5) == 'PASS':
        return True
    raise HardFail(f'FAIL: bytes={nbytes} errors={errors} timeouts={timeouts} overruns={overruns}')
```

### F-D 1GiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport
cd fpga && yosys -q -p "read_verilog -D SPORT_TX_POSEDGE_OUT verilog/sport_tx_from_dsp_clk.v; chparam -set N 1 sport_tx_from_dsp_clk; synth_ice40 -top sport_tx_from_dsp_clk -json build/sport/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport/s.json --pcf verilog/sport_tx_prbs_hx8k.pcf --asc build/sport/s.asc --freq 40 -q --pcf-allow-unconstrained && icepack build/sport/s.asc build/sport/sport_tx_prbs.bin
make -C adsp2156/sport_fpga_tx clean
make -j -C adsp2156/sport_fpga_tx build/main.ldr CFLAGS_EXTRA="-DTOTAL_BYTES=1073741824ULL -DTOTAL_WORDS=268435456U -DRX_SAMPLE_RISING=1 -DRX_SHIFT_LEFT_1=1 -DSPORT_FSDIV=31U"
cp adsp2156/sport_fpga_tx/build/main.ldr adsp2156/sport_fpga_tx/build/fd_1gib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport/sport_tx_prbs.bin
adsp2156/sport_fpga_tx/build/fd_1gib.ldr
```

Test (max 18 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@blinky.bin
fpga.hx8k:program bin=@sport_tx_prbs.bin
dsp:uart_open
dsp:boot ldr=@fd_1gib.ldr timeout_ms=30000
dsp:uart_expect sentinel="sport_fpga_tx_prbs_long bytes=" timeout_ms=390000
delay ms=200
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=f_d_1gib
```

Verify:

```
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'dsp.uart')
    m = re.search(r'sport_fpga_tx_prbs_long bytes=(\d+) words=\d+ errors=(\d+) firsterr=-?\d+.*? timeouts=(\d+) overruns=(\d+).*? (PASS|FAIL)', text)
    if not m:
        raise HardFail('no SPORT report on dsp.uart')
    nbytes, errors, timeouts, overruns = (int(x) for x in m.groups()[:4])
    sys.stderr.write(f'bytes={nbytes} errors={errors} timeouts={timeouts} overruns={overruns} {m.group(5)}\n')
    ops = Verification.load_ops(extract_dir)
    programs = [op for op in ops if op.get('device') == 'fpga.hx8k' and op.get('verb') == 'program']
    expects = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'uart_expect']
    if len(programs) < 2 or not expects:
        return False
    elapsed = expects[0]['t_end'] - programs[1]['t_start']
    rate = int(nbytes * 8 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'rate bps={rate} ({rate/1e6:.1f} Mbps)\n')
    if rate < 28000000:
        raise HardFail(f'rate {rate} < 28000000')
    if nbytes >= 1073741824 and errors == 0 and timeouts == 0 and overruns == 0 and m.group(5) == 'PASS':
        return True
    raise HardFail(f'FAIL: bytes={nbytes} errors={errors} timeouts={timeouts} overruns={overruns}')
```

### F-D 2GiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport
cd fpga && yosys -q -p "read_verilog -D SPORT_TX_POSEDGE_OUT verilog/sport_tx_from_dsp_clk.v; chparam -set N 1 sport_tx_from_dsp_clk; synth_ice40 -top sport_tx_from_dsp_clk -json build/sport/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport/s.json --pcf verilog/sport_tx_prbs_hx8k.pcf --asc build/sport/s.asc --freq 40 -q --pcf-allow-unconstrained && icepack build/sport/s.asc build/sport/sport_tx_prbs.bin
make -C adsp2156/sport_fpga_tx clean
make -j -C adsp2156/sport_fpga_tx build/main.ldr CFLAGS_EXTRA="-DTOTAL_BYTES=2147483648ULL -DTOTAL_WORDS=536870912U -DRX_SAMPLE_RISING=1 -DRX_SHIFT_LEFT_1=1 -DSPORT_FSDIV=31U"
cp adsp2156/sport_fpga_tx/build/main.ldr adsp2156/sport_fpga_tx/build/fd_2gib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport/sport_tx_prbs.bin
adsp2156/sport_fpga_tx/build/fd_2gib.ldr
```

Test (max 18 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@blinky.bin
fpga.hx8k:program bin=@sport_tx_prbs.bin
dsp:uart_open
dsp:boot ldr=@fd_2gib.ldr timeout_ms=30000
dsp:uart_expect sentinel="sport_fpga_tx_prbs_long bytes=" timeout_ms=720000
delay ms=200
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=f_d_2gib
```

Verify:

```
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'dsp.uart')
    m = re.search(r'sport_fpga_tx_prbs_long bytes=(\d+) words=\d+ errors=(\d+) firsterr=-?\d+.*? timeouts=(\d+) overruns=(\d+).*? (PASS|FAIL)', text)
    if not m:
        raise HardFail('no SPORT report on dsp.uart')
    nbytes, errors, timeouts, overruns = (int(x) for x in m.groups()[:4])
    sys.stderr.write(f'bytes={nbytes} errors={errors} timeouts={timeouts} overruns={overruns} {m.group(5)}\n')
    ops = Verification.load_ops(extract_dir)
    programs = [op for op in ops if op.get('device') == 'fpga.hx8k' and op.get('verb') == 'program']
    expects = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'uart_expect']
    if len(programs) < 2 or not expects:
        return False
    elapsed = expects[0]['t_end'] - programs[1]['t_start']
    rate = int(nbytes * 8 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'rate bps={rate} ({rate/1e6:.1f} Mbps)\n')
    if rate < 30000000:
        raise HardFail(f'rate {rate} < 30000000')
    if nbytes >= 2147483648 and errors == 0 and timeouts == 0 and overruns == 0 and m.group(5) == 'PASS':
        return True
    raise HardFail(f'FAIL: bytes={nbytes} errors={errors} timeouts={timeouts} overruns={overruns}')
```

### F-D 4GiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport
cd fpga && yosys -q -p "read_verilog -D SPORT_TX_POSEDGE_OUT verilog/sport_tx_from_dsp_clk.v; chparam -set N 1 sport_tx_from_dsp_clk; synth_ice40 -top sport_tx_from_dsp_clk -json build/sport/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport/s.json --pcf verilog/sport_tx_prbs_hx8k.pcf --asc build/sport/s.asc --freq 40 -q --pcf-allow-unconstrained && icepack build/sport/s.asc build/sport/sport_tx_prbs.bin
make -C adsp2156/sport_fpga_tx clean
make -j -C adsp2156/sport_fpga_tx build/main.ldr CFLAGS_EXTRA="-DTOTAL_BYTES=4294967296ULL -DTOTAL_WORDS=1073741824U -DRX_SAMPLE_RISING=1 -DRX_SHIFT_LEFT_1=1 -DSPORT_FSDIV=31U"
cp adsp2156/sport_fpga_tx/build/main.ldr adsp2156/sport_fpga_tx/build/fd_4gib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport/sport_tx_prbs.bin
adsp2156/sport_fpga_tx/build/fd_4gib.ldr
```

Test (max 28 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@blinky.bin
fpga.hx8k:program bin=@sport_tx_prbs.bin
dsp:uart_open
dsp:boot ldr=@fd_4gib.ldr timeout_ms=30000
dsp:uart_expect sentinel="sport_fpga_tx_prbs_long bytes=" timeout_ms=1410000
delay ms=200
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=f_d_4gib
```

Verify:

```
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'dsp.uart')
    m = re.search(r'sport_fpga_tx_prbs_long bytes=(\d+) words=\d+ errors=(\d+) firsterr=-?\d+.*? timeouts=(\d+) overruns=(\d+).*? (PASS|FAIL)', text)
    if not m:
        raise HardFail('no SPORT report on dsp.uart')
    nbytes, errors, timeouts, overruns = (int(x) for x in m.groups()[:4])
    sys.stderr.write(f'bytes={nbytes} errors={errors} timeouts={timeouts} overruns={overruns} {m.group(5)}\n')
    ops = Verification.load_ops(extract_dir)
    programs = [op for op in ops if op.get('device') == 'fpga.hx8k' and op.get('verb') == 'program']
    expects = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'uart_expect']
    if len(programs) < 2 or not expects:
        return False
    elapsed = expects[0]['t_end'] - programs[1]['t_start']
    rate = int(nbytes * 8 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'rate bps={rate} ({rate/1e6:.1f} Mbps)\n')
    if rate < 30000000:
        raise HardFail(f'rate {rate} < 30000000')
    if nbytes >= 4294967296 and errors == 0 and timeouts == 0 and overruns == 0 and m.group(5) == 'PASS':
        return True
    raise HardFail(f'FAIL: bytes={nbytes} errors={errors} timeouts={timeouts} overruns={overruns}')
```

