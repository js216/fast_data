# D-F direction ladder with 1 Hz heartbeats

#### D-F 128B

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport_rx1
cd fpga && yosys -q -p "read_verilog verilog/sport_rx.v verilog/uart_tx.v; chparam -set N 1 -set MIN_DONE_WORDS 32 sport_rx; synth_ice40 -top sport_rx -json build/sport_rx1/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_rx1/s.json --pcf verilog/sport_rx1_hx8k.pcf --asc build/sport_rx1/s.asc --freq 65 --seed 20 -q --pcf-allow-unconstrained && icepack build/sport_rx1/s.asc build/sport_rx1/sport_rx1.bin
make -C adsp2156/sport_fpga_rx clean
make -j -C adsp2156/sport_fpga_rx CFLAGS_EXTRA="-DNCH=1U -DN_WORDS=32U -DDATA_INDEP_FS=1 -DHALF_WORDS=32768U -DSPORT_SCLK_HZ=60000000U"
cp adsp2156/sport_fpga_rx/build/main.ldr adsp2156/sport_fpga_rx/build/dma_128b.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_rx1/sport_rx1.bin
adsp2156/sport_fpga_rx/build/dma_128b.ldr
```

Test (max 6 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_rx1.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@dma_128b.ldr timeout_ms=15000
fpga.hx8k:uart_expect sentinel="sport_rx lanes=" timeout_ms=15000
delay ms=3000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=d_f_hb_128b
```

Verify:

```
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'fpga.uart')
    if 'ERR w=' in text:
        raise HardFail('FPGA reported first-error line: ' +
                       text[text.index('ERR w='):][:64])
    m = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', text)
    if not m:
        raise HardFail('no sport_rx report')
    lanes, words, errors = int(m.group(1)), int(m.group(2), 16), int(m.group(3), 16)
    nprog = len(re.findall(r'rx w=[0-9a-f]{8} ', text))
    sys.stderr.write(f'lanes={lanes} words={words} errors={errors} {m.group(4)} heartbeats={nprog}\n')
    if lanes == 1 and errors == 0 and words >= 32 and m.group(4) == 'PASS':
        return True
    raise HardFail(f'FAIL: lanes={lanes} words={words} errors={errors}')
```

### D-F 1MiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport_rx1
cd fpga && yosys -q -p "read_verilog verilog/sport_rx.v verilog/uart_tx.v; chparam -set N 1 -set MIN_DONE_WORDS 262144 sport_rx; synth_ice40 -top sport_rx -json build/sport_rx1/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_rx1/s.json --pcf verilog/sport_rx1_hx8k.pcf --asc build/sport_rx1/s.asc --freq 65 --seed 20 -q --pcf-allow-unconstrained && icepack build/sport_rx1/s.asc build/sport_rx1/sport_rx1.bin
make -C adsp2156/sport_fpga_rx clean
make -j -C adsp2156/sport_fpga_rx CFLAGS_EXTRA="-DNCH=1U -DN_WORDS=262144U -DDATA_INDEP_FS=1 -DHALF_WORDS=32768U -DSPORT_SCLK_HZ=60000000U"
cp adsp2156/sport_fpga_rx/build/main.ldr adsp2156/sport_fpga_rx/build/dma_1mib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_rx1/sport_rx1.bin
adsp2156/sport_fpga_rx/build/dma_1mib.ldr
```

Test (max 6 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_rx1.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@dma_1mib.ldr timeout_ms=15000
fpga.hx8k:uart_expect sentinel="sport_rx lanes=" timeout_ms=15000
delay ms=3000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=d_f_hb_1mib
```

Verify:

```
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'fpga.uart')
    if 'ERR w=' in text:
        raise HardFail('FPGA reported first-error line: ' +
                       text[text.index('ERR w='):][:64])
    m = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', text)
    if not m:
        raise HardFail('no sport_rx report')
    lanes, words, errors = int(m.group(1)), int(m.group(2), 16), int(m.group(3), 16)
    nprog = len(re.findall(r'rx w=[0-9a-f]{8} ', text))
    sys.stderr.write(f'lanes={lanes} words={words} errors={errors} {m.group(4)} heartbeats={nprog}\n')
    if lanes == 1 and errors == 0 and words >= 262144 and m.group(4) == 'PASS':
        return True
    raise HardFail(f'FAIL: lanes={lanes} words={words} errors={errors}')
```

### D-F 64MiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport_rx1
cd fpga && yosys -q -p "read_verilog verilog/sport_rx.v verilog/uart_tx.v; chparam -set N 1 -set MIN_DONE_WORDS 16777216 sport_rx; synth_ice40 -top sport_rx -json build/sport_rx1/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_rx1/s.json --pcf verilog/sport_rx1_hx8k.pcf --asc build/sport_rx1/s.asc --freq 65 --seed 20 -q --pcf-allow-unconstrained && icepack build/sport_rx1/s.asc build/sport_rx1/sport_rx1.bin
make -C adsp2156/sport_fpga_rx clean
make -j -C adsp2156/sport_fpga_rx CFLAGS_EXTRA="-DNCH=1U -DN_WORDS=16777216U -DDATA_INDEP_FS=1 -DHALF_WORDS=65536U -DSPORT_SCLK_HZ=60000000U"
cp adsp2156/sport_fpga_rx/build/main.ldr adsp2156/sport_fpga_rx/build/dma_64mib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_rx1/sport_rx1.bin
adsp2156/sport_fpga_rx/build/dma_64mib.ldr
```

Test (max 8 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_rx1.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@dma_64mib.ldr timeout_ms=15000
dsp:uart_expect sentinel="tx h=32\r" timeout_ms=10000
fpga.hx8k:uart_expect sentinel="rx w=00200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=64\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=96\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=128\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=160\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=192\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=224\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=256\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="sport_rx lanes=" timeout_ms=15000
delay ms=3000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=d_f_hb_64mib
```

Verify:

```
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'fpga.uart')
    if 'ERR w=' in text:
        raise HardFail('FPGA reported first-error line: ' +
                       text[text.index('ERR w='):][:64])
    m = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', text)
    if not m:
        raise HardFail('no sport_rx report')
    lanes, words, errors = int(m.group(1)), int(m.group(2), 16), int(m.group(3), 16)
    nprog = len(re.findall(r'rx w=[0-9a-f]{8} ', text))
    sys.stderr.write(f'lanes={lanes} words={words} errors={errors} {m.group(4)} heartbeats={nprog}\n')
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'fpga.hx8k' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[-1]['t_end'] - boots[0]['t_start']
    rate = int(words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'rate per_lane_bps={rate} ({rate/1e6:.1f} Mbps)\n')
    if rate < 50000000:
        raise HardFail(f'rate {rate} < 50000000')
    if lanes == 1 and errors == 0 and words >= 16777216 and m.group(4) == 'PASS':
        return True
    raise HardFail(f'FAIL: lanes={lanes} words={words} errors={errors}')
```

### D-F 256MiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport_rx1
cd fpga && yosys -q -p "read_verilog verilog/sport_rx.v verilog/uart_tx.v; chparam -set N 1 -set MIN_DONE_WORDS 67108864 sport_rx; synth_ice40 -top sport_rx -json build/sport_rx1/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_rx1/s.json --pcf verilog/sport_rx1_hx8k.pcf --asc build/sport_rx1/s.asc --freq 65 --seed 20 -q --pcf-allow-unconstrained && icepack build/sport_rx1/s.asc build/sport_rx1/sport_rx1.bin
make -C adsp2156/sport_fpga_rx clean
make -j -C adsp2156/sport_fpga_rx CFLAGS_EXTRA="-DNCH=1U -DN_WORDS=67108864U -DDATA_INDEP_FS=1 -DHALF_WORDS=65536U -DSPORT_SCLK_HZ=60000000U"
cp adsp2156/sport_fpga_rx/build/main.ldr adsp2156/sport_fpga_rx/build/dma_256mib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_rx1/sport_rx1.bin
adsp2156/sport_fpga_rx/build/dma_256mib.ldr
```

Test (max 10 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_rx1.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@dma_256mib.ldr timeout_ms=15000
dsp:uart_expect sentinel="tx h=32\r" timeout_ms=10000
fpga.hx8k:uart_expect sentinel="rx w=00200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=64\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=96\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=128\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=160\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=192\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=224\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=256\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=288\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=320\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=352\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=384\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=416\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=448\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=480\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=512\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=544\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=576\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=608\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=640\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=672\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=704\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=736\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=768\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=800\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=832\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=864\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=896\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=928\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=960\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=992\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1024\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="sport_rx lanes=" timeout_ms=15000
delay ms=3000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=d_f_hb_256mib
```

Verify:

```
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'fpga.uart')
    if 'ERR w=' in text:
        raise HardFail('FPGA reported first-error line: ' +
                       text[text.index('ERR w='):][:64])
    m = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', text)
    if not m:
        raise HardFail('no sport_rx report')
    lanes, words, errors = int(m.group(1)), int(m.group(2), 16), int(m.group(3), 16)
    nprog = len(re.findall(r'rx w=[0-9a-f]{8} ', text))
    sys.stderr.write(f'lanes={lanes} words={words} errors={errors} {m.group(4)} heartbeats={nprog}\n')
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'fpga.hx8k' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[-1]['t_end'] - boots[0]['t_start']
    rate = int(words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'rate per_lane_bps={rate} ({rate/1e6:.1f} Mbps)\n')
    if rate < 58000000:
        raise HardFail(f'rate {rate} < 58000000')
    if lanes == 1 and errors == 0 and words >= 67108864 and m.group(4) == 'PASS':
        return True
    raise HardFail(f'FAIL: lanes={lanes} words={words} errors={errors}')
```

### D-F 512MiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport_rx1
cd fpga && yosys -q -p "read_verilog verilog/sport_rx.v verilog/uart_tx.v; chparam -set N 1 -set MIN_DONE_WORDS 134217728 sport_rx; synth_ice40 -top sport_rx -json build/sport_rx1/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_rx1/s.json --pcf verilog/sport_rx1_hx8k.pcf --asc build/sport_rx1/s.asc --freq 65 --seed 20 -q --pcf-allow-unconstrained && icepack build/sport_rx1/s.asc build/sport_rx1/sport_rx1.bin
make -C adsp2156/sport_fpga_rx clean
make -j -C adsp2156/sport_fpga_rx CFLAGS_EXTRA="-DNCH=1U -DN_WORDS=134217728U -DDATA_INDEP_FS=1 -DHALF_WORDS=65536U -DSPORT_SCLK_HZ=60000000U"
cp adsp2156/sport_fpga_rx/build/main.ldr adsp2156/sport_fpga_rx/build/dma_512mib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_rx1/sport_rx1.bin
adsp2156/sport_fpga_rx/build/dma_512mib.ldr
```

Test (max 12 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_rx1.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@dma_512mib.ldr timeout_ms=15000
dsp:uart_expect sentinel="tx h=32\r" timeout_ms=10000
fpga.hx8k:uart_expect sentinel="rx w=00200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=64\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=96\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=128\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=160\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=192\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=224\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=256\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=288\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=320\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=352\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=384\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=416\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=448\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=480\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=512\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=544\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=576\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=608\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=640\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=672\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=704\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=736\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=768\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=800\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=832\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=864\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=896\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=928\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=960\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=992\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1024\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1056\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1088\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1120\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1152\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1184\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1216\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1248\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1280\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1312\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1344\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1376\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1408\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1440\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1472\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1504\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1536\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1568\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1600\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1632\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1664\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1696\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1728\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1760\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1792\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1824\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1856\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1888\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1920\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1952\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1984\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2016\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2048\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="sport_rx lanes=" timeout_ms=15000
delay ms=3000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=d_f_hb_512mib
```

Verify:

```
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'fpga.uart')
    if 'ERR w=' in text:
        raise HardFail('FPGA reported first-error line: ' +
                       text[text.index('ERR w='):][:64])
    m = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', text)
    if not m:
        raise HardFail('no sport_rx report')
    lanes, words, errors = int(m.group(1)), int(m.group(2), 16), int(m.group(3), 16)
    nprog = len(re.findall(r'rx w=[0-9a-f]{8} ', text))
    sys.stderr.write(f'lanes={lanes} words={words} errors={errors} {m.group(4)} heartbeats={nprog}\n')
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'fpga.hx8k' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[-1]['t_end'] - boots[0]['t_start']
    rate = int(words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'rate per_lane_bps={rate} ({rate/1e6:.1f} Mbps)\n')
    if rate < 58000000:
        raise HardFail(f'rate {rate} < 58000000')
    if lanes == 1 and errors == 0 and words >= 134217728 and m.group(4) == 'PASS':
        return True
    raise HardFail(f'FAIL: lanes={lanes} words={words} errors={errors}')
```

### D-F 1GiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport_rx1
cd fpga && yosys -q -p "read_verilog verilog/sport_rx.v verilog/uart_tx.v; chparam -set N 1 -set MIN_DONE_WORDS 268435456 sport_rx; synth_ice40 -top sport_rx -json build/sport_rx1/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_rx1/s.json --pcf verilog/sport_rx1_hx8k.pcf --asc build/sport_rx1/s.asc --freq 65 --seed 20 -q --pcf-allow-unconstrained && icepack build/sport_rx1/s.asc build/sport_rx1/sport_rx1.bin
make -C adsp2156/sport_fpga_rx clean
make -j -C adsp2156/sport_fpga_rx CFLAGS_EXTRA="-DNCH=1U -DN_WORDS=268435456U -DDATA_INDEP_FS=1 -DHALF_WORDS=65536U -DSPORT_SCLK_HZ=60000000U"
cp adsp2156/sport_fpga_rx/build/main.ldr adsp2156/sport_fpga_rx/build/dma_1gib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_rx1/sport_rx1.bin
adsp2156/sport_fpga_rx/build/dma_1gib.ldr
```

Test (max 18 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_rx1.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@dma_1gib.ldr timeout_ms=15000
dsp:uart_expect sentinel="tx h=32\r" timeout_ms=10000
fpga.hx8k:uart_expect sentinel="rx w=00200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=64\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=96\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=128\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=160\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=192\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=224\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=256\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=288\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=320\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=352\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=384\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=416\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=448\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=480\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=512\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=544\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=576\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=608\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=640\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=672\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=704\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=736\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=768\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=800\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=832\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=864\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=896\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=928\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=960\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=992\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1024\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1056\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1088\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1120\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1152\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1184\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1216\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1248\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1280\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1312\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1344\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1376\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1408\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1440\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1472\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1504\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1536\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1568\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1600\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1632\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1664\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1696\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1728\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1760\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1792\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1824\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1856\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1888\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1920\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1952\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1984\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2016\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2048\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=08000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2080\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=08200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2112\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=08400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2144\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=08600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2176\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=08800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2208\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=08a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2240\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=08c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2272\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=08e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2304\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=09000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2336\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=09200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2368\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=09400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2400\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=09600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2432\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=09800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2464\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=09a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2496\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=09c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2528\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=09e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2560\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0a000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2592\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0a200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2624\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0a400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2656\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0a600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2688\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0a800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2720\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0aa00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2752\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0ac00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2784\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0ae00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2816\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0b000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2848\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0b200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2880\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0b400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2912\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0b600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2944\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0b800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2976\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0ba00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3008\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0bc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3040\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0be00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3072\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0c000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3104\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0c200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3136\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0c400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3168\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0c600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3200\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0c800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3232\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0ca00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3264\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0cc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3296\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0ce00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3328\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0d000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3360\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0d200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3392\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0d400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3424\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0d600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3456\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0d800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3488\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0da00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3520\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0dc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3552\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0de00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3584\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0e000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3616\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0e200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3648\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0e400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3680\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0e600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3712\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0e800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3744\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0ea00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3776\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0ec00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3808\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0ee00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3840\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0f000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3872\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0f200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3904\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0f400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3936\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0f600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3968\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0f800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4000\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0fa00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4032\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0fc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4064\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0fe00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4096\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="sport_rx lanes=" timeout_ms=15000
delay ms=3000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=d_f_hb_1gib
```

Verify:

```
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'fpga.uart')
    if 'ERR w=' in text:
        raise HardFail('FPGA reported first-error line: ' +
                       text[text.index('ERR w='):][:64])
    m = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', text)
    if not m:
        raise HardFail('no sport_rx report')
    lanes, words, errors = int(m.group(1)), int(m.group(2), 16), int(m.group(3), 16)
    nprog = len(re.findall(r'rx w=[0-9a-f]{8} ', text))
    sys.stderr.write(f'lanes={lanes} words={words} errors={errors} {m.group(4)} heartbeats={nprog}\n')
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'fpga.hx8k' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[-1]['t_end'] - boots[0]['t_start']
    rate = int(words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'rate per_lane_bps={rate} ({rate/1e6:.1f} Mbps)\n')
    if rate < 58000000:
        raise HardFail(f'rate {rate} < 58000000')
    if lanes == 1 and errors == 0 and words >= 268435456 and m.group(4) == 'PASS':
        return True
    raise HardFail(f'FAIL: lanes={lanes} words={words} errors={errors}')
```

### D-F 2GiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport_rx1
cd fpga && yosys -q -p "read_verilog verilog/sport_rx.v verilog/uart_tx.v; chparam -set N 1 -set MIN_DONE_WORDS 536870912 sport_rx; synth_ice40 -top sport_rx -json build/sport_rx1/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_rx1/s.json --pcf verilog/sport_rx1_hx8k.pcf --asc build/sport_rx1/s.asc --freq 65 --seed 20 -q --pcf-allow-unconstrained && icepack build/sport_rx1/s.asc build/sport_rx1/sport_rx1.bin
make -C adsp2156/sport_fpga_rx clean
make -j -C adsp2156/sport_fpga_rx CFLAGS_EXTRA="-DNCH=1U -DN_WORDS=536870912U -DDATA_INDEP_FS=1 -DHALF_WORDS=65536U -DSPORT_SCLK_HZ=60000000U"
cp adsp2156/sport_fpga_rx/build/main.ldr adsp2156/sport_fpga_rx/build/dma_2gib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_rx1/sport_rx1.bin
adsp2156/sport_fpga_rx/build/dma_2gib.ldr
```

Test (max 18 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_rx1.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@dma_2gib.ldr timeout_ms=15000
dsp:uart_expect sentinel="tx h=32\r" timeout_ms=10000
fpga.hx8k:uart_expect sentinel="rx w=00200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=64\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=96\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=128\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=160\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=192\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=224\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=256\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=288\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=320\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=352\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=384\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=416\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=448\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=480\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=512\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=544\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=576\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=608\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=640\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=672\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=704\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=736\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=768\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=800\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=832\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=864\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=896\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=928\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=960\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=992\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1024\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1056\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1088\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1120\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1152\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1184\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1216\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1248\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1280\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1312\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1344\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1376\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1408\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1440\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1472\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1504\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1536\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1568\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1600\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1632\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1664\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1696\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1728\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1760\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1792\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1824\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1856\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1888\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1920\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1952\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1984\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2016\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2048\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=08000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2080\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=08200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2112\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=08400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2144\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=08600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2176\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=08800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2208\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=08a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2240\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=08c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2272\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=08e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2304\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=09000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2336\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=09200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2368\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=09400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2400\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=09600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2432\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=09800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2464\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=09a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2496\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=09c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2528\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=09e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2560\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0a000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2592\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0a200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2624\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0a400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2656\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0a600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2688\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0a800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2720\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0aa00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2752\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0ac00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2784\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0ae00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2816\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0b000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2848\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0b200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2880\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0b400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2912\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0b600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2944\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0b800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2976\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0ba00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3008\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0bc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3040\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0be00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3072\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0c000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3104\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0c200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3136\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0c400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3168\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0c600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3200\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0c800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3232\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0ca00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3264\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0cc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3296\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0ce00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3328\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0d000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3360\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0d200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3392\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0d400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3424\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0d600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3456\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0d800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3488\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0da00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3520\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0dc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3552\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0de00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3584\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0e000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3616\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0e200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3648\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0e400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3680\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0e600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3712\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0e800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3744\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0ea00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3776\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0ec00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3808\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0ee00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3840\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0f000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3872\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0f200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3904\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0f400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3936\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0f600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3968\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0f800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4000\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0fa00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4032\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0fc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4064\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0fe00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4096\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=10000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4128\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=10200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4160\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=10400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4192\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=10600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4224\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=10800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4256\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=10a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4288\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=10c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4320\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=10e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4352\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=11000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4384\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=11200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4416\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=11400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4448\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=11600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4480\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=11800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4512\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=11a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4544\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=11c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4576\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=11e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4608\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=12000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4640\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=12200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4672\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=12400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4704\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=12600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4736\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=12800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4768\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=12a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4800\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=12c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4832\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=12e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4864\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=13000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4896\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=13200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4928\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=13400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4960\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=13600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4992\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=13800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5024\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=13a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5056\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=13c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5088\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=13e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5120\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=14000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5152\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=14200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5184\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=14400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5216\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=14600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5248\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=14800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5280\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=14a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5312\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=14c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5344\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=14e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5376\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=15000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5408\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=15200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5440\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=15400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5472\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=15600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5504\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=15800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5536\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=15a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5568\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=15c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5600\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=15e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5632\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=16000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5664\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=16200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5696\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=16400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5728\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=16600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5760\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=16800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5792\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=16a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5824\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=16c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5856\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=16e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5888\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=17000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5920\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=17200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5952\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=17400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5984\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=17600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6016\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=17800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6048\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=17a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6080\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=17c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6112\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=17e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6144\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=18000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6176\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=18200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6208\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=18400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6240\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=18600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6272\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=18800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6304\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=18a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6336\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=18c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6368\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=18e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6400\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=19000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6432\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=19200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6464\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=19400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6496\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=19600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6528\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=19800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6560\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=19a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6592\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=19c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6624\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=19e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6656\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1a000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6688\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1a200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6720\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1a400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6752\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1a600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6784\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1a800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6816\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1aa00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6848\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1ac00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6880\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1ae00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6912\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1b000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6944\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1b200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6976\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1b400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7008\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1b600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7040\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1b800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7072\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1ba00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7104\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1bc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7136\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1be00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7168\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1c000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7200\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1c200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7232\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1c400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7264\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1c600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7296\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1c800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7328\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1ca00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7360\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1cc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7392\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1ce00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7424\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1d000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7456\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1d200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7488\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1d400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7520\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1d600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7552\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1d800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7584\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1da00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7616\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1dc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7648\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1de00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7680\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1e000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7712\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1e200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7744\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1e400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7776\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1e600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7808\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1e800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7840\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1ea00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7872\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1ec00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7904\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1ee00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7936\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1f000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7968\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1f200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8000\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1f400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8032\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1f600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8064\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1f800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8096\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1fa00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8128\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1fc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8160\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1fe00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8192\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="sport_rx lanes=" timeout_ms=15000
delay ms=3000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=d_f_hb_2gib
```

Verify:

```
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'fpga.uart')
    if 'ERR w=' in text:
        raise HardFail('FPGA reported first-error line: ' +
                       text[text.index('ERR w='):][:64])
    m = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', text)
    if not m:
        raise HardFail('no sport_rx report')
    lanes, words, errors = int(m.group(1)), int(m.group(2), 16), int(m.group(3), 16)
    nprog = len(re.findall(r'rx w=[0-9a-f]{8} ', text))
    sys.stderr.write(f'lanes={lanes} words={words} errors={errors} {m.group(4)} heartbeats={nprog}\n')
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'fpga.hx8k' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[-1]['t_end'] - boots[0]['t_start']
    rate = int(words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'rate per_lane_bps={rate} ({rate/1e6:.1f} Mbps)\n')
    if rate < 58000000:
        raise HardFail(f'rate {rate} < 58000000')
    if lanes == 1 and errors == 0 and words >= 536870912 and m.group(4) == 'PASS':
        return True
    raise HardFail(f'FAIL: lanes={lanes} words={words} errors={errors}')
```

### D-F 4GiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport_rx1
cd fpga && yosys -q -p "read_verilog verilog/sport_rx.v verilog/uart_tx.v; chparam -set N 1 -set MIN_DONE_WORDS 1073741824 sport_rx; synth_ice40 -top sport_rx -json build/sport_rx1/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_rx1/s.json --pcf verilog/sport_rx1_hx8k.pcf --asc build/sport_rx1/s.asc --freq 65 --seed 20 -q --pcf-allow-unconstrained && icepack build/sport_rx1/s.asc build/sport_rx1/sport_rx1.bin
make -C adsp2156/sport_fpga_rx clean
make -j -C adsp2156/sport_fpga_rx CFLAGS_EXTRA="-DNCH=1U -DN_WORDS=1073741824U -DDATA_INDEP_FS=1 -DHALF_WORDS=65536U -DSPORT_SCLK_HZ=60000000U"
cp adsp2156/sport_fpga_rx/build/main.ldr adsp2156/sport_fpga_rx/build/dma_4gib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_rx1/sport_rx1.bin
adsp2156/sport_fpga_rx/build/dma_4gib.ldr
```

Test (max 25 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_rx1.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@dma_4gib.ldr timeout_ms=15000
dsp:uart_expect sentinel="tx h=32\r" timeout_ms=10000
fpga.hx8k:uart_expect sentinel="rx w=00200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=64\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=96\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=128\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=160\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=192\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=224\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=256\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=288\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=320\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=352\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=384\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=416\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=448\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=480\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=512\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=544\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=576\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=608\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=640\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=672\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=704\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=736\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=768\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=800\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=832\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=864\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=896\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=928\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=960\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=992\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1024\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1056\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1088\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1120\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1152\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1184\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1216\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1248\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1280\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1312\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1344\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1376\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1408\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1440\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1472\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1504\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1536\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1568\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1600\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1632\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1664\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1696\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1728\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1760\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1792\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1824\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1856\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1888\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1920\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1952\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1984\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2016\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2048\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=08000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2080\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=08200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2112\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=08400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2144\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=08600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2176\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=08800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2208\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=08a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2240\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=08c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2272\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=08e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2304\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=09000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2336\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=09200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2368\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=09400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2400\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=09600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2432\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=09800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2464\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=09a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2496\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=09c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2528\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=09e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2560\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0a000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2592\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0a200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2624\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0a400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2656\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0a600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2688\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0a800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2720\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0aa00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2752\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0ac00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2784\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0ae00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2816\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0b000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2848\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0b200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2880\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0b400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2912\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0b600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2944\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0b800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2976\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0ba00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3008\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0bc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3040\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0be00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3072\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0c000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3104\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0c200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3136\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0c400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3168\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0c600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3200\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0c800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3232\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0ca00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3264\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0cc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3296\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0ce00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3328\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0d000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3360\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0d200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3392\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0d400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3424\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0d600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3456\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0d800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3488\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0da00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3520\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0dc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3552\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0de00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3584\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0e000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3616\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0e200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3648\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0e400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3680\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0e600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3712\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0e800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3744\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0ea00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3776\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0ec00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3808\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0ee00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3840\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0f000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3872\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0f200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3904\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0f400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3936\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0f600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3968\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0f800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4000\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0fa00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4032\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0fc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4064\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0fe00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4096\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=10000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4128\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=10200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4160\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=10400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4192\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=10600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4224\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=10800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4256\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=10a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4288\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=10c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4320\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=10e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4352\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=11000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4384\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=11200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4416\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=11400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4448\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=11600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4480\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=11800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4512\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=11a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4544\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=11c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4576\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=11e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4608\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=12000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4640\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=12200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4672\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=12400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4704\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=12600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4736\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=12800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4768\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=12a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4800\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=12c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4832\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=12e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4864\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=13000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4896\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=13200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4928\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=13400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4960\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=13600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4992\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=13800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5024\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=13a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5056\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=13c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5088\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=13e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5120\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=14000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5152\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=14200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5184\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=14400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5216\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=14600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5248\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=14800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5280\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=14a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5312\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=14c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5344\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=14e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5376\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=15000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5408\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=15200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5440\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=15400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5472\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=15600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5504\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=15800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5536\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=15a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5568\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=15c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5600\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=15e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5632\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=16000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5664\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=16200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5696\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=16400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5728\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=16600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5760\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=16800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5792\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=16a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5824\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=16c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5856\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=16e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5888\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=17000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5920\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=17200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5952\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=17400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5984\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=17600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6016\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=17800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6048\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=17a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6080\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=17c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6112\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=17e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6144\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=18000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6176\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=18200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6208\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=18400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6240\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=18600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6272\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=18800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6304\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=18a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6336\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=18c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6368\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=18e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6400\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=19000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6432\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=19200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6464\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=19400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6496\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=19600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6528\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=19800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6560\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=19a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6592\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=19c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6624\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=19e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6656\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1a000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6688\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1a200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6720\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1a400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6752\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1a600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6784\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1a800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6816\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1aa00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6848\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1ac00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6880\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1ae00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6912\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1b000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6944\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1b200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6976\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1b400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7008\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1b600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7040\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1b800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7072\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1ba00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7104\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1bc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7136\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1be00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7168\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1c000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7200\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1c200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7232\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1c400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7264\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1c600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7296\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1c800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7328\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1ca00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7360\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1cc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7392\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1ce00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7424\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1d000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7456\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1d200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7488\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1d400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7520\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1d600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7552\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1d800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7584\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1da00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7616\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1dc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7648\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1de00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7680\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1e000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7712\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1e200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7744\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1e400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7776\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1e600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7808\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1e800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7840\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1ea00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7872\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1ec00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7904\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1ee00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7936\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1f000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7968\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1f200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8000\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1f400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8032\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1f600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8064\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1f800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8096\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1fa00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8128\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1fc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8160\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1fe00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8192\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=20000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8224\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=20200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8256\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=20400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8288\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=20600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8320\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=20800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8352\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=20a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8384\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=20c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8416\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=20e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8448\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=21000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8480\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=21200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8512\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=21400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8544\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=21600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8576\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=21800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8608\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=21a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8640\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=21c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8672\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=21e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8704\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=22000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8736\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=22200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8768\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=22400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8800\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=22600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8832\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=22800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8864\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=22a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8896\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=22c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8928\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=22e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8960\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=23000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8992\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=23200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=9024\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=23400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=9056\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=23600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=9088\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=23800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=9120\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=23a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=9152\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=23c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=9184\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=23e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=9216\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=24000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=9248\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=24200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=9280\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=24400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=9312\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=24600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=9344\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=24800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=9376\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=24a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=9408\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=24c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=9440\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=24e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=9472\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=25000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=9504\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=25200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=9536\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=25400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=9568\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=25600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=9600\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=25800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=9632\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=25a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=9664\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=25c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=9696\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=25e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=9728\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=26000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=9760\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=26200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=9792\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=26400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=9824\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=26600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=9856\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=26800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=9888\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=26a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=9920\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=26c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=9952\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=26e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=9984\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=27000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=10016\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=27200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=10048\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=27400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=10080\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=27600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=10112\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=27800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=10144\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=27a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=10176\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=27c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=10208\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=27e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=10240\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=28000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=10272\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=28200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=10304\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=28400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=10336\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=28600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=10368\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=28800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=10400\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=28a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=10432\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=28c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=10464\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=28e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=10496\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=29000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=10528\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=29200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=10560\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=29400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=10592\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=29600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=10624\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=29800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=10656\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=29a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=10688\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=29c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=10720\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=29e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=10752\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2a000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=10784\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2a200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=10816\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2a400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=10848\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2a600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=10880\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2a800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=10912\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2aa00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=10944\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2ac00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=10976\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2ae00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=11008\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2b000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=11040\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2b200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=11072\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2b400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=11104\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2b600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=11136\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2b800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=11168\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2ba00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=11200\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2bc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=11232\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2be00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=11264\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2c000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=11296\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2c200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=11328\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2c400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=11360\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2c600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=11392\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2c800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=11424\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2ca00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=11456\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2cc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=11488\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2ce00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=11520\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2d000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=11552\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2d200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=11584\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2d400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=11616\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2d600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=11648\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2d800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=11680\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2da00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=11712\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2dc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=11744\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2de00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=11776\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2e000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=11808\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2e200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=11840\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2e400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=11872\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2e600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=11904\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2e800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=11936\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2ea00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=11968\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2ec00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=12000\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2ee00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=12032\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2f000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=12064\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2f200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=12096\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2f400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=12128\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2f600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=12160\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2f800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=12192\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2fa00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=12224\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2fc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=12256\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=2fe00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=12288\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=30000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=12320\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=30200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=12352\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=30400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=12384\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=30600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=12416\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=30800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=12448\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=30a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=12480\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=30c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=12512\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=30e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=12544\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=31000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=12576\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=31200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=12608\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=31400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=12640\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=31600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=12672\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=31800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=12704\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=31a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=12736\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=31c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=12768\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=31e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=12800\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=32000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=12832\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=32200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=12864\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=32400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=12896\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=32600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=12928\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=32800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=12960\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=32a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=12992\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=32c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=13024\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=32e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=13056\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=33000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=13088\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=33200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=13120\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=33400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=13152\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=33600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=13184\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=33800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=13216\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=33a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=13248\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=33c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=13280\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=33e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=13312\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=34000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=13344\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=34200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=13376\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=34400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=13408\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=34600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=13440\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=34800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=13472\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=34a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=13504\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=34c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=13536\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=34e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=13568\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=35000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=13600\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=35200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=13632\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=35400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=13664\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=35600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=13696\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=35800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=13728\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=35a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=13760\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=35c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=13792\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=35e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=13824\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=36000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=13856\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=36200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=13888\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=36400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=13920\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=36600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=13952\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=36800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=13984\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=36a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=14016\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=36c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=14048\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=36e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=14080\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=37000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=14112\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=37200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=14144\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=37400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=14176\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=37600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=14208\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=37800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=14240\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=37a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=14272\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=37c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=14304\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=37e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=14336\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=38000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=14368\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=38200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=14400\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=38400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=14432\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=38600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=14464\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=38800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=14496\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=38a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=14528\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=38c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=14560\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=38e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=14592\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=39000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=14624\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=39200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=14656\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=39400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=14688\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=39600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=14720\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=39800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=14752\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=39a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=14784\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=39c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=14816\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=39e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=14848\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3a000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=14880\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3a200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=14912\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3a400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=14944\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3a600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=14976\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3a800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=15008\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3aa00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=15040\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3ac00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=15072\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3ae00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=15104\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3b000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=15136\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3b200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=15168\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3b400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=15200\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3b600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=15232\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3b800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=15264\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3ba00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=15296\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3bc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=15328\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3be00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=15360\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3c000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=15392\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3c200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=15424\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3c400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=15456\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3c600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=15488\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3c800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=15520\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3ca00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=15552\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3cc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=15584\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3ce00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=15616\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3d000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=15648\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3d200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=15680\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3d400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=15712\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3d600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=15744\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3d800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=15776\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3da00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=15808\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3dc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=15840\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3de00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=15872\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3e000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=15904\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3e200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=15936\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3e400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=15968\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3e600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=16000\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3e800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=16032\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3ea00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=16064\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3ec00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=16096\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3ee00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=16128\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3f000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=16160\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3f200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=16192\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3f400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=16224\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3f600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=16256\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3f800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=16288\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3fa00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=16320\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3fc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=16352\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=3fe00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=16384\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="sport_rx lanes=" timeout_ms=15000
delay ms=3000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=d_f_hb_4gib
```

Verify:

```
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'fpga.uart')
    if 'ERR w=' in text:
        raise HardFail('FPGA reported first-error line: ' +
                       text[text.index('ERR w='):][:64])
    m = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', text)
    if not m:
        raise HardFail('no sport_rx report')
    lanes, words, errors = int(m.group(1)), int(m.group(2), 16), int(m.group(3), 16)
    nprog = len(re.findall(r'rx w=[0-9a-f]{8} ', text))
    sys.stderr.write(f'lanes={lanes} words={words} errors={errors} {m.group(4)} heartbeats={nprog}\n')
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'fpga.hx8k' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[-1]['t_end'] - boots[0]['t_start']
    rate = int(words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'rate per_lane_bps={rate} ({rate/1e6:.1f} Mbps)\n')
    if rate < 58000000:
        raise HardFail(f'rate {rate} < 58000000')
    if lanes == 1 and errors == 0 and words >= 1073741824 and m.group(4) == 'PASS':
        return True
    raise HardFail(f'FAIL: lanes={lanes} words={words} errors={errors}')
```

