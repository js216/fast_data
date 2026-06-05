# FPGA <-> ADSP-2156 GPIO connectivity

Discover, at run time, which FPGA balls are jumpered to which
ADSP-2156 header pins, and print the connections actually observed.
No external connectivity manifest or hardcoded wiring map is used:
the FPGA bitstream simply watches **every usable I/O ball** as a
pulled-up input, the DSP drives each of its pins high then low, and
whichever ball toggles is the one physically wired to that DSP pin.
Because the wiring is re-jumpered often (sometimes daily), nothing
here assumes a fixed ball<->pin map -- it is rediscovered each run.

The DSP labels come from the firmware's own `?` pin-index table
(`adsp2156/gpio/main.c`); the FPGA ball names come from the
bitstream's pin-constraint order (`gpioscan_hx8k.pcf`), which is the
physical watch-list, not a connection map.

**Boot-bus ordering.** FPGA J1 is wired to the DSP SPI2/OSPI boot
bus, so a bitstream driving those balls during boot trips
`SYS_FAULT`. The run programs the benign **blinky** bitstream first,
boots the DSP over a clean SPI2, then swaps in the input-only
**gpioscan** bitstream (it never drives any ball, so it cannot
contend the bus). Blinky is reloaded at the end so the next DSP load
stays clean.

### Bench inventory probe

Test (max 1 min):

```
inventory
mark tag=fpga_dsp_gpio_inventory_probe
```

Verify:

```
from pathlib import Path
import json

REQUIRED_OPS = {
    'fpga': {'program', 'uart_open', 'uart_write', 'uart_close'},
    'dsp':  {'reset', 'boot', 'uart_open', 'uart_write',
             'uart_expect', 'uart_close'},
}

def _advertised(ops, plugin):
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
    for plugin, required in REQUIRED_OPS.items():
        if not required <= _advertised(ops_map, plugin):
            return False
    return True
```

### Build firmware

Build the DSP gpio loader, the benign blinky bitstream, and the
watch-all **gpioscan** bitstream (built directly, outside the noweb
chapter system).

Build:

```
make -C adsp2156/gpio
make -C fpga build/blinky/hx8k/blinky.bin
cd fpga && mkdir -p build/gpioscan && yosys -q -p "read_verilog verilog/gpioscan.v verilog/uart_tx.v verilog/uart_rx.v; synth_ice40 -top gpioscan -json build/gpioscan/gpioscan.json" && nextpnr-ice40 --hx8k --package ct256 --json build/gpioscan/gpioscan.json --pcf verilog/gpioscan_hx8k.pcf --asc build/gpioscan/gpioscan.asc --freq 12 -q --pcf-allow-unconstrained && icepack build/gpioscan/gpioscan.asc build/gpioscan/gpioscan.bin
```

Artifacts:

```
adsp2156/gpio/build/main.ldr
fpga/build/blinky/hx8k/blinky.bin
fpga/build/gpioscan/gpioscan.bin
```

Test: no hardware.

Verify:

```
def check(extract_dir):
    from pathlib import Path
    for key in ('main.ldr', 'blinky.bin', 'gpioscan.bin'):
        p = Path(artifacts[key])
        if not (p.exists() and p.stat().st_size > 0):
            return False
    return True
```

### FPGA-benign DSP boot liveness

Artifacts:

```
adsp2156/gpio/build/main.ldr
fpga/build/blinky/hx8k/blinky.bin
```

Test (max 2 min):

```
fpga.hx8k:program bin=@blinky.bin
dsp:reset
dsp:uart_open
dsp:boot ldr=@main.ldr timeout_ms=15000
dsp:uart_expect sentinel="=== scan 0 done ===" timeout_ms=12000
mark tag=liveness_pin_table_start
dsp:uart_write data="?"
delay ms=600
mark tag=liveness_pin_table_end
scope:capture chans="C2"
dsp:uart_close
mark tag=fpga_dsp_gpio_liveness
```

Verify:

```
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'dsp.uart')
    if '=== scan 0 done ===' not in text:
        sys.stderr.write('no boot-scan completion banner on dsp.uart\n')
        return False
    table = re.findall(
        r'^\s*([0-9a-zA-Z])\s+(\S+)\s+\(([^)]*)\)',
        text, re.MULTILINE)
    sys.stderr.write(f'parsed {len(table)} pin-table rows\n')
    return len(table) >= 10
```

### Per-pin connectivity sweep (DSP drives, FPGA watches all balls)

Program blinky, boot the DSP, capture the `?` table, swap in the
input-only gpioscan bitstream, then for each DSP pin drive it high,
snapshot every FPGA ball (`S`), drive it low, snapshot again. The
verifier XORs the two snapshots; whichever ball bit flipped is the
ball jumpered to that DSP pin. There is no Phase B -- gpioscan never
drives, so the DSP-drive direction alone maps the wiring.

Artifacts:

```
adsp2156/gpio/build/main.ldr
fpga/build/blinky/hx8k/blinky.bin
fpga/build/gpioscan/gpioscan.bin
```

Test (max 10 min):

```
fpga.hx8k:program bin=@blinky.bin
dsp:reset
dsp:uart_open
dsp:boot ldr=@main.ldr timeout_ms=15000
dsp:uart_expect sentinel="=== scan 0 done ===" timeout_ms=12000
mark tag=pin_table_start
dsp:uart_write data="?"
delay ms=600
mark tag=pin_table_end
fpga.hx8k:program bin=@gpioscan.bin
fpga.hx8k:uart_open
dsp:uart_write data="Z"
delay ms=300
mark tag=phase_a_start
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_00
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_01
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_02
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_03
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_04
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_05
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_06
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_07
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_08
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_09
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_10
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_11
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_12
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_13
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_14
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_15
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_16
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_17
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_18
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_19
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_20
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_21
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_22
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_23
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_24
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_25
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_26
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_27
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_28
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_29
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_30
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_31
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_32
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_33
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_34
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_35
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_36
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_37
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_38
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_39
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_40
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_41
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_42
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=200
dsp:uart_write data="R"
mark tag=phase_a_43
fpga.hx8k:uart_close
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=fpga_dsp_gpio_done
```

Verify:

```
def check(extract_dir):
    import sys
    import ast
    from pathlib import Path

    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        sys.stderr.write('manifest dirty (op-level errors)\n')
        return False

    timeline = (Path(extract_dir) / 'timeline.log').read_text()
    stream_re = re.compile(r"> STREAM\s+(\S+)\s+('.*')\s*$")
    mark_re = re.compile(r"MARK\s+ctrl\s+(\S+)\s*$")

    def collect(start_mark, end_mark, stream_name):
        in_window = False
        out = []
        for line in timeline.splitlines():
            m = mark_re.search(line)
            if m:
                tag = m.group(1)
                if tag == start_mark:
                    in_window = True
                    continue
                if tag == end_mark:
                    in_window = False
                    continue
            if in_window:
                s = stream_re.search(line)
                if s and s.group(1) == stream_name:
                    try:
                        out.append(ast.literal_eval(s.group(2)))
                    except (ValueError, SyntaxError):
                        pass
        return ''.join(out)

    # DSP labels from the firmware `?` table (idx char -> header/sig).
    table_text = collect('pin_table_start', 'pin_table_end', 'dsp.uart')

    def idx_of(ch):
        if '0' <= ch <= '9':
            return ord(ch) - ord('0')
        if 'a' <= ch <= 'z':
            return 10 + ord(ch) - ord('a')
        if 'A' <= ch <= 'Z':
            return 36 + ord(ch) - ord('A')
        return -1

    dsp_label = {}
    for ch, hdr, sig in re.findall(
            r'(?m)^\s*([0-9a-zA-Z])\s+(\S+)\s+\(([^)]*)\)', table_text):
        i = idx_of(ch)
        if i >= 0:
            dsp_label[i] = f'{hdr} ({sig})'

    def lbl(i):
        return dsp_label.get(i, f'idx{i} (unlabelled)')

    # FPGA ball names in pins[] order (the gpioscan_hx8k.pcf watch list).
    SCAN_BALLS = [
        'A1', 'A2', 'A5', 'A6', 'A7', 'A9', 'A10', 'A11', 'A15', 'A16', 'B1', 'B2',
        'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B11', 'B13', 'B14', 'B15', 'B16',
        'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'C11', 'C12',
        'C13', 'C14', 'C16', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9',
        'D10', 'D11', 'D13', 'D14', 'D15', 'D16', 'E2', 'E3', 'E4', 'E5', 'E6', 'E9',
        'E10', 'E11', 'E13', 'E14', 'E16', 'F1', 'F2', 'F3', 'F4', 'F5', 'F7', 'F9',
        'F11', 'F12', 'F13', 'F14', 'F15', 'F16', 'G1', 'G2', 'G3', 'G4', 'G5', 'G10',
        'G11', 'G12', 'G13', 'G14', 'G15', 'G16', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6',
        'H11', 'H12', 'H13', 'H14', 'H16', 'J1', 'J2', 'J4', 'J5', 'J10', 'J11', 'J12',
        'J13', 'J14', 'J15', 'J16', 'K1', 'K3', 'K4', 'K5', 'K9', 'K11', 'K12', 'K13',
        'K14', 'K15', 'K16', 'L1', 'L3', 'L4', 'L5', 'L6', 'L7', 'L9', 'L10', 'L11',
        'L12', 'L13', 'L14', 'L16', 'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8',
        'M9', 'M11', 'M12', 'M13', 'M14', 'M15', 'M16', 'N2', 'N3', 'N4', 'N5', 'N6',
        'N7', 'N9', 'N10', 'N12', 'N16', 'P1', 'P2', 'P4', 'P5', 'P6', 'P7', 'P8',
        'P9', 'P10', 'P11', 'P12', 'P13', 'P14', 'P15', 'P16', 'R1', 'R2', 'R3', 'R4',
        'R5', 'R6', 'R9', 'R10', 'R11', 'R12', 'R14', 'R15', 'R16', 'T1', 'T2', 'T3',
        'T5', 'T6', 'T7', 'T8', 'T9', 'T10', 'T11', 'T13', 'T14', 'T15', 'T16',
    ]

    N_A = 44

    def snaps(i):
        start = 'phase_a_start' if i == 0 else f'phase_a_{i-1:02d}'
        seg = collect(start, f'phase_a_{i:02d}', 'fpga.uart')
        return [int(s, 16) for s in re.findall(r'([0-9a-fA-F]{20,})\r?\n', seg)]

    samples = [snaps(i) for i in range(N_A)]
    streams_ok = min((len(s) for s in samples), default=0) >= 1

    def flips(ss):
        if not ss:
            return []
        ref = ss[0]
        mask = 0
        for s in ss[1:]:
            mask |= (s ^ ref)
        return [b for b in range(len(SCAN_BALLS)) if mask & (1 << b)]

    out = []
    out.append('')
    out.append('=== DISCOVERED FPGA <-> ADSP-2156 CONNECTIONS ===')
    out.append(f'DSP labels: {len(dsp_label)} from ? table; '
               f'FPGA watching {len(SCAN_BALLS)} balls')
    out.append('')
    found = 0
    for i in range(N_A):
        fb = flips(samples[i])
        if not fb:
            out.append(f'  DSP {lbl(i):<24} ->  (no ball flipped, '
                       f'{len(samples[i])} snapshots)')
        else:
            for b in fb:
                found += 1
                out.append(f'  DSP {lbl(i):<24} ->  FPGA ball {SCAN_BALLS[b]}')
    out.append('')
    out.append(f'total connections discovered: {found}')
    out.append('=== end discovered connections ===')
    sys.stderr.write('\n'.join(out) + '\n')

    return streams_ok and bool(dsp_label)
```
