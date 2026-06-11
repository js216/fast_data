# F-D direction ladder (bidir 1x1 chain)
#### F-D 128B

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
make -C adsp2156/sport_fpga_bidir clean
make -j -C adsp2156/sport_fpga_bidir CFLAGS_EXTRA="-DRX_N=1U -DTX_N=1U -DTOTAL_WORDS=32U -DTX_FIRST"
cp adsp2156/sport_fpga_bidir/build/main.ldr adsp2156/sport_fpga_bidir/build/bidir1x1_128b.ldr
mkdir -p fpga/build/sport_bidir_1x1
cd fpga && yosys -q -p "read_verilog -D EYE_DELAY verilog/sport_tx_sync_nopll.v verilog/sport_tx_prbs_ser.v verilog/sport_rx.v verilog/sport_bidir.v verilog/uart_tx.v; chparam -set TX_TO_DSP_N 1 -set RX_FROM_DSP_N 1 -set SYNC_TX 1 -set NOPLL 1 -set REPORT_LANE0 0 -set MIN_DONE_WORDS 536870912 sport_bidir; synth_ice40 -top sport_bidir -json build/sport_bidir_1x1/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_bidir_1x1/s.json --pcf verilog/sport_bidir_1x1_hx8k.pcf --asc build/sport_bidir_1x1/s.asc --freq 65 -q --pcf-allow-unconstrained && icepack build/sport_bidir_1x1/s.asc build/sport_bidir_1x1/sport_bidir_1x1.bin
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_bidir_1x1/sport_bidir_1x1.bin
adsp2156/sport_fpga_bidir/build/bidir1x1_128b.ldr
```

Test (max 6 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_bidir_1x1.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@bidir1x1_128b.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_bidir rx_lanes=1" timeout_ms=15000
fpga.hx8k:uart_expect sentinel="sport_rx lanes=1" timeout_ms=60000
delay ms=2000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=f_d_128b
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
    ftxt = Verification.load_stream_text(extract_dir, 'fpga.uart')
    dm = re.search(r'sport_bidir rx_lanes=(\d+) tx_lanes=(\d+) rx_words=(\d+) rx_errors=(\d+) timeouts=(\d+) tx_timeouts=(\d+) overruns=(\d+) slips=(\d+) tx_sent=(\d+) (PASS|FAIL)', dtxt)
    if not dm:
        raise HardFail('no sport_bidir report')
    rx_lanes, rx_words, rx_errors, to, txto, ov, slips = (int(dm.group(i)) for i in (1,3,4,5,6,7,8))
    fm = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', ftxt)
    if not fm:
        sys.stderr.write('no FPGA from_dsp report\n')
        return False
    fpga_words = int(fm.group(2), 16)
    fpga_errors = int(fm.group(3), 16)
    if not (fpga_errors == 0 and fpga_words >= 32 and fm.group(4) == 'PASS'):
        raise HardFail(f'D->F FAIL: words={fpga_words} errors={fpga_errors}')
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[0]['t_end'] - boots[0]['t_start']
    fd_rate = int(rx_words * 32 / elapsed) if elapsed > 0 else 0
    df_rate = int(fpga_words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'fd={fd_rate/1e6:.1f}Mbps df={df_rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if (rx_lanes == 1 and rx_errors == 0 and to == 0 and txto == 0 and ov == 0
            and slips == 0 and rx_words >= 32 and dm.group(10) == 'PASS'):
        return True
    raise HardFail(f'FAIL: rx_words={rx_words} rx_errors={rx_errors} slips={slips}')
```

### F-D 1MiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
make -C adsp2156/sport_fpga_bidir clean
make -j -C adsp2156/sport_fpga_bidir CFLAGS_EXTRA="-DRX_N=1U -DTX_N=1U -DTOTAL_WORDS=262144U -DTX_FIRST"
cp adsp2156/sport_fpga_bidir/build/main.ldr adsp2156/sport_fpga_bidir/build/bidir1x1_1mib.ldr
mkdir -p fpga/build/sport_bidir_1x1
cd fpga && yosys -q -p "read_verilog -D EYE_DELAY verilog/sport_tx_sync_nopll.v verilog/sport_tx_prbs_ser.v verilog/sport_rx.v verilog/sport_bidir.v verilog/uart_tx.v; chparam -set TX_TO_DSP_N 1 -set RX_FROM_DSP_N 1 -set SYNC_TX 1 -set NOPLL 1 -set REPORT_LANE0 0 -set MIN_DONE_WORDS 262144 sport_bidir; synth_ice40 -top sport_bidir -json build/sport_bidir_1x1/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_bidir_1x1/s.json --pcf verilog/sport_bidir_1x1_hx8k.pcf --asc build/sport_bidir_1x1/s.asc --freq 65 -q --pcf-allow-unconstrained && icepack build/sport_bidir_1x1/s.asc build/sport_bidir_1x1/sport_bidir_1x1.bin
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_bidir_1x1/sport_bidir_1x1.bin
adsp2156/sport_fpga_bidir/build/bidir1x1_1mib.ldr
```

Test (max 6 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_bidir_1x1.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@bidir1x1_1mib.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_bidir rx_lanes=1" timeout_ms=15000
fpga.hx8k:uart_expect sentinel="sport_rx lanes=1" timeout_ms=60000
delay ms=2000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=f_d_1mib
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
    ftxt = Verification.load_stream_text(extract_dir, 'fpga.uart')
    dm = re.search(r'sport_bidir rx_lanes=(\d+) tx_lanes=(\d+) rx_words=(\d+) rx_errors=(\d+) timeouts=(\d+) tx_timeouts=(\d+) overruns=(\d+) slips=(\d+) tx_sent=(\d+) (PASS|FAIL)', dtxt)
    if not dm:
        raise HardFail('no sport_bidir report')
    rx_lanes, rx_words, rx_errors, to, txto, ov, slips = (int(dm.group(i)) for i in (1,3,4,5,6,7,8))
    fm = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', ftxt)
    if not fm:
        sys.stderr.write('no FPGA from_dsp report\n')
        return False
    fpga_words = int(fm.group(2), 16)
    fpga_errors = int(fm.group(3), 16)
    if not (fpga_errors == 0 and fpga_words >= 262144 and fm.group(4) == 'PASS'):
        raise HardFail(f'D->F FAIL: words={fpga_words} errors={fpga_errors}')
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[0]['t_end'] - boots[0]['t_start']
    fd_rate = int(rx_words * 32 / elapsed) if elapsed > 0 else 0
    df_rate = int(fpga_words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'fd={fd_rate/1e6:.1f}Mbps df={df_rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if (rx_lanes == 1 and rx_errors == 0 and to == 0 and txto == 0 and ov == 0
            and slips == 0 and rx_words >= 262144 and dm.group(10) == 'PASS'):
        return True
    raise HardFail(f'FAIL: rx_words={rx_words} rx_errors={rx_errors} slips={slips}')
```

### F-D 64MiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
make -C adsp2156/sport_fpga_bidir clean
make -j -C adsp2156/sport_fpga_bidir CFLAGS_EXTRA="-DRX_N=1U -DTX_N=1U -DTOTAL_WORDS=16777216U -DTX_FIRST"
cp adsp2156/sport_fpga_bidir/build/main.ldr adsp2156/sport_fpga_bidir/build/bidir1x1_64mib.ldr
mkdir -p fpga/build/sport_bidir_1x1
cd fpga && yosys -q -p "read_verilog -D EYE_DELAY verilog/sport_tx_sync_nopll.v verilog/sport_tx_prbs_ser.v verilog/sport_rx.v verilog/sport_bidir.v verilog/uart_tx.v; chparam -set TX_TO_DSP_N 1 -set RX_FROM_DSP_N 1 -set SYNC_TX 1 -set NOPLL 1 -set REPORT_LANE0 0 -set MIN_DONE_WORDS 16777216 sport_bidir; synth_ice40 -top sport_bidir -json build/sport_bidir_1x1/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_bidir_1x1/s.json --pcf verilog/sport_bidir_1x1_hx8k.pcf --asc build/sport_bidir_1x1/s.asc --freq 65 -q --pcf-allow-unconstrained && icepack build/sport_bidir_1x1/s.asc build/sport_bidir_1x1/sport_bidir_1x1.bin
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_bidir_1x1/sport_bidir_1x1.bin
adsp2156/sport_fpga_bidir/build/bidir1x1_64mib.ldr
```

Test (max 8 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_bidir_1x1.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@bidir1x1_64mib.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_bidir rx_lanes=1" timeout_ms=45000
fpga.hx8k:uart_expect sentinel="sport_rx lanes=1" timeout_ms=60000
delay ms=2000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=f_d_64mib
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
    ftxt = Verification.load_stream_text(extract_dir, 'fpga.uart')
    dm = re.search(r'sport_bidir rx_lanes=(\d+) tx_lanes=(\d+) rx_words=(\d+) rx_errors=(\d+) timeouts=(\d+) tx_timeouts=(\d+) overruns=(\d+) slips=(\d+) tx_sent=(\d+) (PASS|FAIL)', dtxt)
    if not dm:
        raise HardFail('no sport_bidir report')
    rx_lanes, rx_words, rx_errors, to, txto, ov, slips = (int(dm.group(i)) for i in (1,3,4,5,6,7,8))
    fm = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', ftxt)
    if not fm:
        sys.stderr.write('no FPGA from_dsp report\n')
        return False
    fpga_words = int(fm.group(2), 16)
    fpga_errors = int(fm.group(3), 16)
    if not (fpga_errors == 0 and fpga_words >= 16777216 and fm.group(4) == 'PASS'):
        raise HardFail(f'D->F FAIL: words={fpga_words} errors={fpga_errors}')
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[0]['t_end'] - boots[0]['t_start']
    fd_rate = int(rx_words * 32 / elapsed) if elapsed > 0 else 0
    df_rate = int(fpga_words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'fd={fd_rate/1e6:.1f}Mbps df={df_rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if (rx_lanes == 1 and rx_errors == 0 and to == 0 and txto == 0 and ov == 0
            and slips == 0 and rx_words >= 16777216 and dm.group(10) == 'PASS'):
        return True
    raise HardFail(f'FAIL: rx_words={rx_words} rx_errors={rx_errors} slips={slips}')
```

### F-D 256MiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
make -C adsp2156/sport_fpga_bidir clean
make -j -C adsp2156/sport_fpga_bidir CFLAGS_EXTRA="-DRX_N=1U -DTX_N=1U -DTOTAL_WORDS=67108864U -DTX_FIRST"
cp adsp2156/sport_fpga_bidir/build/main.ldr adsp2156/sport_fpga_bidir/build/bidir1x1_256mib.ldr
mkdir -p fpga/build/sport_bidir_1x1
cd fpga && yosys -q -p "read_verilog -D EYE_DELAY verilog/sport_tx_sync_nopll.v verilog/sport_tx_prbs_ser.v verilog/sport_rx.v verilog/sport_bidir.v verilog/uart_tx.v; chparam -set TX_TO_DSP_N 1 -set RX_FROM_DSP_N 1 -set SYNC_TX 1 -set NOPLL 1 -set REPORT_LANE0 0 -set MIN_DONE_WORDS 67108864 sport_bidir; synth_ice40 -top sport_bidir -json build/sport_bidir_1x1/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_bidir_1x1/s.json --pcf verilog/sport_bidir_1x1_hx8k.pcf --asc build/sport_bidir_1x1/s.asc --freq 65 -q --pcf-allow-unconstrained && icepack build/sport_bidir_1x1/s.asc build/sport_bidir_1x1/sport_bidir_1x1.bin
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_bidir_1x1/sport_bidir_1x1.bin
adsp2156/sport_fpga_bidir/build/bidir1x1_256mib.ldr
```

Test (max 8 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_bidir_1x1.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@bidir1x1_256mib.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_bidir rx_lanes=1" timeout_ms=75000
fpga.hx8k:uart_expect sentinel="sport_rx lanes=1" timeout_ms=60000
delay ms=2000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=f_d_256mib
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
    ftxt = Verification.load_stream_text(extract_dir, 'fpga.uart')
    dm = re.search(r'sport_bidir rx_lanes=(\d+) tx_lanes=(\d+) rx_words=(\d+) rx_errors=(\d+) timeouts=(\d+) tx_timeouts=(\d+) overruns=(\d+) slips=(\d+) tx_sent=(\d+) (PASS|FAIL)', dtxt)
    if not dm:
        raise HardFail('no sport_bidir report')
    rx_lanes, rx_words, rx_errors, to, txto, ov, slips = (int(dm.group(i)) for i in (1,3,4,5,6,7,8))
    fm = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', ftxt)
    if not fm:
        sys.stderr.write('no FPGA from_dsp report\n')
        return False
    fpga_words = int(fm.group(2), 16)
    fpga_errors = int(fm.group(3), 16)
    if not (fpga_errors == 0 and fpga_words >= 67108864 and fm.group(4) == 'PASS'):
        raise HardFail(f'D->F FAIL: words={fpga_words} errors={fpga_errors}')
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[0]['t_end'] - boots[0]['t_start']
    fd_rate = int(rx_words * 32 / elapsed) if elapsed > 0 else 0
    df_rate = int(fpga_words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'fd={fd_rate/1e6:.1f}Mbps df={df_rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if (rx_lanes == 1 and rx_errors == 0 and to == 0 and txto == 0 and ov == 0
            and slips == 0 and rx_words >= 67108864 and dm.group(10) == 'PASS'):
        return True
    raise HardFail(f'FAIL: rx_words={rx_words} rx_errors={rx_errors} slips={slips}')
```

### F-D 512MiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
make -C adsp2156/sport_fpga_bidir clean
make -j -C adsp2156/sport_fpga_bidir CFLAGS_EXTRA="-DRX_N=1U -DTX_N=1U -DTOTAL_WORDS=134217728U -DTX_FIRST"
cp adsp2156/sport_fpga_bidir/build/main.ldr adsp2156/sport_fpga_bidir/build/bidir1x1_512mib.ldr
mkdir -p fpga/build/sport_bidir_1x1
cd fpga && yosys -q -p "read_verilog -D EYE_DELAY verilog/sport_tx_sync_nopll.v verilog/sport_tx_prbs_ser.v verilog/sport_rx.v verilog/sport_bidir.v verilog/uart_tx.v; chparam -set TX_TO_DSP_N 1 -set RX_FROM_DSP_N 1 -set SYNC_TX 1 -set NOPLL 1 -set REPORT_LANE0 0 -set MIN_DONE_WORDS 134217728 sport_bidir; synth_ice40 -top sport_bidir -json build/sport_bidir_1x1/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_bidir_1x1/s.json --pcf verilog/sport_bidir_1x1_hx8k.pcf --asc build/sport_bidir_1x1/s.asc --freq 65 -q --pcf-allow-unconstrained && icepack build/sport_bidir_1x1/s.asc build/sport_bidir_1x1/sport_bidir_1x1.bin
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_bidir_1x1/sport_bidir_1x1.bin
adsp2156/sport_fpga_bidir/build/bidir1x1_512mib.ldr
```

Test (max 10 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_bidir_1x1.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@bidir1x1_512mib.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_bidir rx_lanes=1" timeout_ms=150000
fpga.hx8k:uart_expect sentinel="sport_rx lanes=1" timeout_ms=60000
delay ms=2000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=f_d_512mib
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
    ftxt = Verification.load_stream_text(extract_dir, 'fpga.uart')
    dm = re.search(r'sport_bidir rx_lanes=(\d+) tx_lanes=(\d+) rx_words=(\d+) rx_errors=(\d+) timeouts=(\d+) tx_timeouts=(\d+) overruns=(\d+) slips=(\d+) tx_sent=(\d+) (PASS|FAIL)', dtxt)
    if not dm:
        raise HardFail('no sport_bidir report')
    rx_lanes, rx_words, rx_errors, to, txto, ov, slips = (int(dm.group(i)) for i in (1,3,4,5,6,7,8))
    fm = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', ftxt)
    if not fm:
        sys.stderr.write('no FPGA from_dsp report\n')
        return False
    fpga_words = int(fm.group(2), 16)
    fpga_errors = int(fm.group(3), 16)
    if not (fpga_errors == 0 and fpga_words >= 134217728 and fm.group(4) == 'PASS'):
        raise HardFail(f'D->F FAIL: words={fpga_words} errors={fpga_errors}')
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[0]['t_end'] - boots[0]['t_start']
    fd_rate = int(rx_words * 32 / elapsed) if elapsed > 0 else 0
    df_rate = int(fpga_words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'fd={fd_rate/1e6:.1f}Mbps df={df_rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if fd_rate < 56250000:
        raise HardFail(f'F->D rate {fd_rate} < 55000000')
    if df_rate < 56250000:
        raise HardFail(f'D->F rate {df_rate} < 55000000')
    if (rx_lanes == 1 and rx_errors == 0 and to == 0 and txto == 0 and ov == 0
            and slips == 0 and rx_words >= 134217728 and dm.group(10) == 'PASS'):
        return True
    raise HardFail(f'FAIL: rx_words={rx_words} rx_errors={rx_errors} slips={slips}')
```

### F-D 1GiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
make -C adsp2156/sport_fpga_bidir clean
make -j -C adsp2156/sport_fpga_bidir CFLAGS_EXTRA="-DRX_N=1U -DTX_N=1U -DTOTAL_WORDS=268435456U -DTX_FIRST"
cp adsp2156/sport_fpga_bidir/build/main.ldr adsp2156/sport_fpga_bidir/build/bidir1x1_1gib.ldr
mkdir -p fpga/build/sport_bidir_1x1
cd fpga && yosys -q -p "read_verilog -D EYE_DELAY verilog/sport_tx_sync_nopll.v verilog/sport_tx_prbs_ser.v verilog/sport_rx.v verilog/sport_bidir.v verilog/uart_tx.v; chparam -set TX_TO_DSP_N 1 -set RX_FROM_DSP_N 1 -set SYNC_TX 1 -set NOPLL 1 -set REPORT_LANE0 0 -set MIN_DONE_WORDS 268435456 sport_bidir; synth_ice40 -top sport_bidir -json build/sport_bidir_1x1/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_bidir_1x1/s.json --pcf verilog/sport_bidir_1x1_hx8k.pcf --asc build/sport_bidir_1x1/s.asc --freq 65 -q --pcf-allow-unconstrained && icepack build/sport_bidir_1x1/s.asc build/sport_bidir_1x1/sport_bidir_1x1.bin
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_bidir_1x1/sport_bidir_1x1.bin
adsp2156/sport_fpga_bidir/build/bidir1x1_1gib.ldr
```

Test (max 14 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_bidir_1x1.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@bidir1x1_1gib.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_bidir rx_lanes=1" timeout_ms=210000
fpga.hx8k:uart_expect sentinel="sport_rx lanes=1" timeout_ms=60000
delay ms=2000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=f_d_1gib
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
    ftxt = Verification.load_stream_text(extract_dir, 'fpga.uart')
    dm = re.search(r'sport_bidir rx_lanes=(\d+) tx_lanes=(\d+) rx_words=(\d+) rx_errors=(\d+) timeouts=(\d+) tx_timeouts=(\d+) overruns=(\d+) slips=(\d+) tx_sent=(\d+) (PASS|FAIL)', dtxt)
    if not dm:
        raise HardFail('no sport_bidir report')
    rx_lanes, rx_words, rx_errors, to, txto, ov, slips = (int(dm.group(i)) for i in (1,3,4,5,6,7,8))
    fm = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', ftxt)
    if not fm:
        sys.stderr.write('no FPGA from_dsp report\n')
        return False
    fpga_words = int(fm.group(2), 16)
    fpga_errors = int(fm.group(3), 16)
    if not (fpga_errors == 0 and fpga_words >= 268435456 and fm.group(4) == 'PASS'):
        raise HardFail(f'D->F FAIL: words={fpga_words} errors={fpga_errors}')
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[0]['t_end'] - boots[0]['t_start']
    fd_rate = int(rx_words * 32 / elapsed) if elapsed > 0 else 0
    df_rate = int(fpga_words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'fd={fd_rate/1e6:.1f}Mbps df={df_rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if fd_rate < 56250000:
        raise HardFail(f'F->D rate {fd_rate} < 55000000')
    if df_rate < 56250000:
        raise HardFail(f'D->F rate {df_rate} < 55000000')
    if (rx_lanes == 1 and rx_errors == 0 and to == 0 and txto == 0 and ov == 0
            and slips == 0 and rx_words >= 268435456 and dm.group(10) == 'PASS'):
        return True
    raise HardFail(f'FAIL: rx_words={rx_words} rx_errors={rx_errors} slips={slips}')
```

### F-D 2GiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
make -C adsp2156/sport_fpga_bidir clean
make -j -C adsp2156/sport_fpga_bidir CFLAGS_EXTRA="-DRX_N=1U -DTX_N=1U -DTOTAL_WORDS=536870912U -DTX_FIRST"
cp adsp2156/sport_fpga_bidir/build/main.ldr adsp2156/sport_fpga_bidir/build/bidir1x1_2gib.ldr
mkdir -p fpga/build/sport_bidir_1x1
cd fpga && yosys -q -p "read_verilog -D EYE_DELAY verilog/sport_tx_sync_nopll.v verilog/sport_tx_prbs_ser.v verilog/sport_rx.v verilog/sport_bidir.v verilog/uart_tx.v; chparam -set TX_TO_DSP_N 1 -set RX_FROM_DSP_N 1 -set SYNC_TX 1 -set NOPLL 1 -set REPORT_LANE0 0 -set MIN_DONE_WORDS 536870912 sport_bidir; synth_ice40 -top sport_bidir -json build/sport_bidir_1x1/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_bidir_1x1/s.json --pcf verilog/sport_bidir_1x1_hx8k.pcf --asc build/sport_bidir_1x1/s.asc --freq 65 -q --pcf-allow-unconstrained && icepack build/sport_bidir_1x1/s.asc build/sport_bidir_1x1/sport_bidir_1x1.bin
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_bidir_1x1/sport_bidir_1x1.bin
adsp2156/sport_fpga_bidir/build/bidir1x1_2gib.ldr
```

Test (max 18 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_bidir_1x1.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@bidir1x1_2gib.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_bidir rx_lanes=1" timeout_ms=390000
fpga.hx8k:uart_expect sentinel="sport_rx lanes=1" timeout_ms=60000
delay ms=2000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=f_d_2gib
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
    ftxt = Verification.load_stream_text(extract_dir, 'fpga.uart')
    dm = re.search(r'sport_bidir rx_lanes=(\d+) tx_lanes=(\d+) rx_words=(\d+) rx_errors=(\d+) timeouts=(\d+) tx_timeouts=(\d+) overruns=(\d+) slips=(\d+) tx_sent=(\d+) (PASS|FAIL)', dtxt)
    if not dm:
        raise HardFail('no sport_bidir report')
    rx_lanes, rx_words, rx_errors, to, txto, ov, slips = (int(dm.group(i)) for i in (1,3,4,5,6,7,8))
    fm = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', ftxt)
    if not fm:
        sys.stderr.write('no FPGA from_dsp report\n')
        return False
    fpga_words = int(fm.group(2), 16)
    fpga_errors = int(fm.group(3), 16)
    if not (fpga_errors == 0 and fpga_words >= 536870912 and fm.group(4) == 'PASS'):
        raise HardFail(f'D->F FAIL: words={fpga_words} errors={fpga_errors}')
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[0]['t_end'] - boots[0]['t_start']
    fd_rate = int(rx_words * 32 / elapsed) if elapsed > 0 else 0
    df_rate = int(fpga_words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'fd={fd_rate/1e6:.1f}Mbps df={df_rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if fd_rate < 56250000:
        raise HardFail(f'F->D rate {fd_rate} < 60000000')
    if df_rate < 56250000:
        raise HardFail(f'D->F rate {df_rate} < 60000000')
    if (rx_lanes == 1 and rx_errors == 0 and to == 0 and txto == 0 and ov == 0
            and slips == 0 and rx_words >= 536870912 and dm.group(10) == 'PASS'):
        return True
    raise HardFail(f'FAIL: rx_words={rx_words} rx_errors={rx_errors} slips={slips}')
```

### F-D 4GiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
make -C adsp2156/sport_fpga_bidir clean
make -j -C adsp2156/sport_fpga_bidir CFLAGS_EXTRA="-DRX_N=1U -DTX_N=1U -DTOTAL_WORDS=1073741824U -DTX_FIRST"
cp adsp2156/sport_fpga_bidir/build/main.ldr adsp2156/sport_fpga_bidir/build/bidir1x1_4gib.ldr
mkdir -p fpga/build/sport_bidir_1x1
cd fpga && yosys -q -p "read_verilog -D EYE_DELAY verilog/sport_tx_sync_nopll.v verilog/sport_tx_prbs_ser.v verilog/sport_rx.v verilog/sport_bidir.v verilog/uart_tx.v; chparam -set TX_TO_DSP_N 1 -set RX_FROM_DSP_N 1 -set SYNC_TX 1 -set NOPLL 1 -set REPORT_LANE0 0 -set MIN_DONE_WORDS 1073741824 sport_bidir; synth_ice40 -top sport_bidir -json build/sport_bidir_1x1/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_bidir_1x1/s.json --pcf verilog/sport_bidir_1x1_hx8k.pcf --asc build/sport_bidir_1x1/s.asc --freq 65 -q --pcf-allow-unconstrained && icepack build/sport_bidir_1x1/s.asc build/sport_bidir_1x1/sport_bidir_1x1.bin
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_bidir_1x1/sport_bidir_1x1.bin
adsp2156/sport_fpga_bidir/build/bidir1x1_4gib.ldr
```

Test (max 18 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_bidir_1x1.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@bidir1x1_4gib.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_bidir rx_lanes=1" timeout_ms=720000
fpga.hx8k:uart_expect sentinel="sport_rx lanes=1" timeout_ms=60000
delay ms=2000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=f_d_4gib
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
    ftxt = Verification.load_stream_text(extract_dir, 'fpga.uart')
    dm = re.search(r'sport_bidir rx_lanes=(\d+) tx_lanes=(\d+) rx_words=(\d+) rx_errors=(\d+) timeouts=(\d+) tx_timeouts=(\d+) overruns=(\d+) slips=(\d+) tx_sent=(\d+) (PASS|FAIL)', dtxt)
    if not dm:
        raise HardFail('no sport_bidir report')
    rx_lanes, rx_words, rx_errors, to, txto, ov, slips = (int(dm.group(i)) for i in (1,3,4,5,6,7,8))
    fm = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', ftxt)
    if not fm:
        sys.stderr.write('no FPGA from_dsp report\n')
        return False
    fpga_words = int(fm.group(2), 16)
    fpga_errors = int(fm.group(3), 16)
    if not (fpga_errors == 0 and fpga_words >= 1073741824 and fm.group(4) == 'PASS'):
        raise HardFail(f'D->F FAIL: words={fpga_words} errors={fpga_errors}')
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[0]['t_end'] - boots[0]['t_start']
    fd_rate = int(rx_words * 32 / elapsed) if elapsed > 0 else 0
    df_rate = int(fpga_words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'fd={fd_rate/1e6:.1f}Mbps df={df_rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if fd_rate < 56250000:
        raise HardFail(f'F->D rate {fd_rate} < 60000000')
    if df_rate < 56250000:
        raise HardFail(f'D->F rate {df_rate} < 60000000')
    if (rx_lanes == 1 and rx_errors == 0 and to == 0 and txto == 0 and ov == 0
            and slips == 0 and rx_words >= 1073741824 and dm.group(10) == 'PASS'):
        return True
    raise HardFail(f'FAIL: rx_words={rx_words} rx_errors={rx_errors} slips={slips}')
```

