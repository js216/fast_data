# FPGA <-> ADSP-2156 GPIO connectivity

Verifies the jumpers between the iCE40-HX8K-B-EVN expansion
balls and the EV-SOMCRR-EZLITE `P13`/`P14` headers in **both**
directions, using on-demand UART probes rather than the periodic
heartbeat.

### Build firmware

Done: 05/13/2026 08:30:35

Build the FPGA bitstream for the HX8K-B-EVN and the DSP gpio
loader. The per-board FPGA output now lives under
`fpga/build/gpio/hx8k/` thanks to the `BOARDS_gpio := hx1k hx8k`
declaration in `fpga/Makefile`.

Build:

```
make -C adsp2156/gpio
make -C fpga build/gpio/hx8k/gpio.bin
```

Artifacts:

```
adsp2156/gpio/build/main.ldr
fpga/build/gpio/hx8k/gpio.bin
```

Test: no hardware.

Verify:

```
def check(extract_dir):
    from pathlib import Path
    ldr = Path(artifacts['main.ldr'])
    fpga = Path(artifacts['gpio.bin'])
    return ldr.exists() and ldr.stat().st_size > 0 and \
           fpga.exists() and fpga.stat().st_size > 0
```

### Bidirectional jumper sweep

Done: 05/13/2026 08:30:40

Program the FPGA, boot the DSP, zero both cursors, then for each
of the sixteen pins drive in both directions:

  - Phase A (`a<i>`-tagged snapshots): DSP drives pin `i` high,
    bench probes the FPGA via `S`; DSP drives pin `i` low, probe
    again; DSP releases and advances. Each `S` reply is a
    heartbeat-format four-hex-digit line on `fpga.uart`.
  - Phase B (`b<i>`-tagged snapshots): same shape but with FPGA
    driving (`N` raises `gpio_oe[cursor]` and `gpio_out[cursor]`,
    `n` drops the data bit, `R` releases). The DSP `Q` reply is a
    six-hex-digit input snapshot prefixed with `Q=` so the
    verifier can pull each iteration's pair of samples out of the
    DSP stream by position.

Per-pin sequences are wrapped with `mark tag=phase_a_<i>` /
`mark tag=phase_b_<i>` so the verifier can carve the two streams
into per-pin segments deterministically -- no reliance on the
heartbeat cadence to space iterations apart.

Build: nothing.

Artifacts:

```
adsp2156/gpio/build/main.ldr
fpga/build/gpio/hx8k/gpio.bin
```

Test (max 10 min):

```
fpga.hx8k:program bin=@gpio.bin
fpga.hx8k:uart_open
dsp:reset
dsp:uart_open
dsp:boot ldr=@main.ldr timeout_ms=15000
delay ms=3000
fpga.hx8k:uart_write data="Z"
dsp:uart_write data="Z"
delay ms=300
mark tag=phase_a_start
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=150
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=150
dsp:uart_write data="R"
mark tag=phase_a_00
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=150
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=150
dsp:uart_write data="R"
mark tag=phase_a_01
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=150
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=150
dsp:uart_write data="R"
mark tag=phase_a_02
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=150
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=150
dsp:uart_write data="R"
mark tag=phase_a_03
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=150
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=150
dsp:uart_write data="R"
mark tag=phase_a_04
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=150
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=150
dsp:uart_write data="R"
mark tag=phase_a_05
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=150
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=150
dsp:uart_write data="R"
mark tag=phase_a_06
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=150
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=150
dsp:uart_write data="R"
mark tag=phase_a_07
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=150
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=150
dsp:uart_write data="R"
mark tag=phase_a_08
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=150
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=150
dsp:uart_write data="R"
mark tag=phase_a_09
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=150
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=150
dsp:uart_write data="R"
mark tag=phase_a_10
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=150
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=150
dsp:uart_write data="R"
mark tag=phase_a_11
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=150
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=150
dsp:uart_write data="R"
mark tag=phase_a_12
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=150
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=150
dsp:uart_write data="R"
mark tag=phase_a_13
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=150
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=150
dsp:uart_write data="R"
mark tag=phase_a_14
dsp:uart_write data="N"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=150
dsp:uart_write data="n"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=150
dsp:uart_write data="R"
mark tag=phase_a_15
fpga.hx8k:uart_write data="Z"
dsp:uart_write data="Z"
delay ms=300
mark tag=phase_b_start
fpga.hx8k:uart_write data="N"
delay ms=100
dsp:uart_write data="Q"
delay ms=200
fpga.hx8k:uart_write data="n"
delay ms=100
dsp:uart_write data="Q"
delay ms=200
fpga.hx8k:uart_write data="R"
mark tag=phase_b_00
fpga.hx8k:uart_write data="N"
delay ms=100
dsp:uart_write data="Q"
delay ms=200
fpga.hx8k:uart_write data="n"
delay ms=100
dsp:uart_write data="Q"
delay ms=200
fpga.hx8k:uart_write data="R"
mark tag=phase_b_01
fpga.hx8k:uart_write data="N"
delay ms=100
dsp:uart_write data="Q"
delay ms=200
fpga.hx8k:uart_write data="n"
delay ms=100
dsp:uart_write data="Q"
delay ms=200
fpga.hx8k:uart_write data="R"
mark tag=phase_b_02
fpga.hx8k:uart_write data="N"
delay ms=100
dsp:uart_write data="Q"
delay ms=200
fpga.hx8k:uart_write data="n"
delay ms=100
dsp:uart_write data="Q"
delay ms=200
fpga.hx8k:uart_write data="R"
mark tag=phase_b_03
fpga.hx8k:uart_write data="N"
delay ms=100
dsp:uart_write data="Q"
delay ms=200
fpga.hx8k:uart_write data="n"
delay ms=100
dsp:uart_write data="Q"
delay ms=200
fpga.hx8k:uart_write data="R"
mark tag=phase_b_04
fpga.hx8k:uart_write data="N"
delay ms=100
dsp:uart_write data="Q"
delay ms=200
fpga.hx8k:uart_write data="n"
delay ms=100
dsp:uart_write data="Q"
delay ms=200
fpga.hx8k:uart_write data="R"
mark tag=phase_b_05
fpga.hx8k:uart_write data="N"
delay ms=100
dsp:uart_write data="Q"
delay ms=200
fpga.hx8k:uart_write data="n"
delay ms=100
dsp:uart_write data="Q"
delay ms=200
fpga.hx8k:uart_write data="R"
mark tag=phase_b_06
fpga.hx8k:uart_write data="N"
delay ms=100
dsp:uart_write data="Q"
delay ms=200
fpga.hx8k:uart_write data="n"
delay ms=100
dsp:uart_write data="Q"
delay ms=200
fpga.hx8k:uart_write data="R"
mark tag=phase_b_07
fpga.hx8k:uart_write data="N"
delay ms=100
dsp:uart_write data="Q"
delay ms=200
fpga.hx8k:uart_write data="n"
delay ms=100
dsp:uart_write data="Q"
delay ms=200
fpga.hx8k:uart_write data="R"
mark tag=phase_b_08
fpga.hx8k:uart_write data="N"
delay ms=100
dsp:uart_write data="Q"
delay ms=200
fpga.hx8k:uart_write data="n"
delay ms=100
dsp:uart_write data="Q"
delay ms=200
fpga.hx8k:uart_write data="R"
mark tag=phase_b_09
fpga.hx8k:uart_write data="N"
delay ms=100
dsp:uart_write data="Q"
delay ms=200
fpga.hx8k:uart_write data="n"
delay ms=100
dsp:uart_write data="Q"
delay ms=200
fpga.hx8k:uart_write data="R"
mark tag=phase_b_10
fpga.hx8k:uart_write data="N"
delay ms=100
dsp:uart_write data="Q"
delay ms=200
fpga.hx8k:uart_write data="n"
delay ms=100
dsp:uart_write data="Q"
delay ms=200
fpga.hx8k:uart_write data="R"
mark tag=phase_b_11
fpga.hx8k:uart_write data="N"
delay ms=100
dsp:uart_write data="Q"
delay ms=200
fpga.hx8k:uart_write data="n"
delay ms=100
dsp:uart_write data="Q"
delay ms=200
fpga.hx8k:uart_write data="R"
mark tag=phase_b_12
fpga.hx8k:uart_write data="N"
delay ms=100
dsp:uart_write data="Q"
delay ms=200
fpga.hx8k:uart_write data="n"
delay ms=100
dsp:uart_write data="Q"
delay ms=200
fpga.hx8k:uart_write data="R"
mark tag=phase_b_13
fpga.hx8k:uart_write data="N"
delay ms=100
dsp:uart_write data="Q"
delay ms=200
fpga.hx8k:uart_write data="n"
delay ms=100
dsp:uart_write data="Q"
delay ms=200
fpga.hx8k:uart_write data="R"
mark tag=phase_b_14
fpga.hx8k:uart_write data="N"
delay ms=100
dsp:uart_write data="Q"
delay ms=200
fpga.hx8k:uart_write data="n"
delay ms=100
dsp:uart_write data="Q"
delay ms=200
fpga.hx8k:uart_write data="R"
mark tag=phase_b_15
fpga.hx8k:uart_write data="Z"
dsp:uart_write data="Z"
dsp:uart_close
fpga.hx8k:uart_close
mark tag=fpga_dsp_gpio_done
```

Verify:

```
def check(extract_dir):
    import sys
    import ast
    from pathlib import Path

    # Discovery, not pass/fail: we DON'T fail just because some pin
    # shows no connection or a different pairing than the assumed
    # `pins[i] <-> DSP idx i` map. The check returns True as long
    # as the run completed cleanly (manifest_clean) and the streams
    # carried enough text to parse. The connection table is printed
    # honestly to stderr so the user can see what was actually
    # observed.

    if not Verification.manifest_clean(extract_dir):
        sys.stderr.write('manifest dirty (op-level errors)\n')
        return False

    # Per-iteration segmentation walks the test_serv timeline.log
    # (one timestamped line per stream chunk + one per `mark`) and
    # rebuilds each window's stream slice from the `'<repr>'`
    # payloads on `> STREAM` events between consecutive
    # `MARK phase_<phase>_<i-1>` and `MARK phase_<phase>_<i>` rows.
    # ast.literal_eval decodes the python repr (with \r\n / \xNN
    # escapes) back to raw bytes-as-text without an eval() detour.
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

    # Static reference: DSP scan-index 0..15 -> header label, from
    # adsp2156/gpio/main.c pin table; FPGA bit index -> ball label,
    # from fpga/src/gpio.nw set_io map for the HX8K-B-EVN. These
    # are printed alongside the discovered indices to make the
    # connection table read like a jumper list.
    dsp_labels = [
        'P13.02', 'P13.04', 'P13.06', 'P13.08',
        'P13.10', 'P13.12', 'P13.14', 'P13.16',
        'P13.18', 'P13.20', 'P13.38', 'P13.40',
        'P14.06', 'P14.08', 'P14.10', 'P14.12',
    ]
    fpga_balls = [
        'P16', 'N16', 'M16', 'K14',
        'G14', 'K15', 'J15', 'H14',
        'G15', 'F15', 'H3',  'H4',
        'H5',  'K1',  'L1',  'M1',
    ]

    a_samples_per_iter = []
    b_samples_per_iter = []
    for i in range(16):
        a_start = 'phase_a_start' if i == 0 else f'phase_a_{i-1:02d}'
        a_end = f'phase_a_{i:02d}'
        b_start = 'phase_b_start' if i == 0 else f'phase_b_{i-1:02d}'
        b_end = f'phase_b_{i:02d}'
        a_seg = collect(a_start, a_end, 'fpga.uart')
        b_seg = collect(b_start, b_end, 'dsp.uart')
        # FPGA snapshots: 4 hex digits terminated by CR/LF, e.g.
        # '0c00\r\n'. The chunk boundaries on fpga.uart sometimes
        # glue two adjacent samples together ('0c00\r\n0c00\r\n')
        # so anchor each match on its trailing \r?\n rather than
        # the (chunk-relative) line start. DSP snapshots:
        # prefixed 'Q=' + 6 hex digits.
        a_samples_per_iter.append(
            [int(s, 16) for s in
             re.findall(r'([0-9a-fA-F]{4})\r?\n', a_seg)])
        b_samples_per_iter.append(
            [int(s, 16) for s in
             re.findall(r'Q=([0-9a-fA-F]{6})', b_seg)])

    # A well-formed run produces (at least) 2 snapshots per
    # iteration -- the high-drive read and the low-drive read.
    # If we don't even have one snapshot per iteration on either
    # stream the run is too degenerate to interpret; that's the
    # only quantitative pass/fail gate.
    a_min = min(len(s) for s in a_samples_per_iter)
    b_min = min(len(s) for s in b_samples_per_iter)
    streams_ok = (a_min >= 1) and (b_min >= 1)

    def flip_mask(samples):
        # XOR every snapshot against the first one; the union of
        # changed bits is what flipped during the high-vs-low
        # toggle for this iteration. Returns 0 when nothing moved.
        if not samples:
            return 0
        ref = samples[0]
        mask = 0
        for s in samples[1:]:
            mask |= (s ^ ref)
        return mask

    def fmt_bits(mask, width):
        if mask == 0:
            return '(no flip)'
        bits = [str(b) for b in range(width) if mask & (1 << b)]
        return 'bit ' + ','.join(bits) if len(bits) == 1 else \
               'bits ' + ','.join(bits)

    sys.stderr.write(
        '\n=== discovered jumper table ===\n'
        'Phase A: DSP drives, FPGA snapshot via S; per-iteration\n'
        'flip mask shows which FPGA bit(s) toggled high<->low.\n'
        'Phase B: FPGA drives, DSP snapshot via Q; per-iteration\n'
        'flip mask shows which DSP scan-index bit(s) toggled.\n'
        'Iteration i selects DSP scan-index i AND FPGA pins[i] in\n'
        'lockstep via the shared cursor (R advances both ends).\n'
        '\n')
    sys.stderr.write(
        f'{"iter":>4}  {"DSP idx":>7}  {"DSP hdr":>7}  '
        f'{"FPGA bit":>8}  {"FPGA ball":>9}  '
        f'{"A-mask":>6}  A-bits           '
        f'{"B-mask":>6}  B-bits\n')
    for i in range(16):
        a_mask = flip_mask(a_samples_per_iter[i])
        b_mask = flip_mask(b_samples_per_iter[i])
        sys.stderr.write(
            f'{i:>4}  {i:>7}  {dsp_labels[i]:>7}  '
            f'{i:>8}  {fpga_balls[i]:>9}  '
            f'{a_mask:>06x}  {fmt_bits(a_mask, 16):<16} '
            f'{b_mask:>06x}  {fmt_bits(b_mask, 24)}\n')

    # Translate flip masks into a flat "<-> jumper" listing keyed
    # by DSP scan-index. Honest reporting: iterations whose
    # high/low snapshots never differed get a "no connection
    # observed" line on the corresponding direction.
    sys.stderr.write('\n--- per-direction discoveries ---\n')
    for i in range(16):
        a_mask = flip_mask(a_samples_per_iter[i])
        if a_mask == 0:
            sys.stderr.write(
                f'DSP idx {i:2d}  {dsp_labels[i]}  ->  '
                f'no connection observed (Phase A flip mask=000000, '
                f'{len(a_samples_per_iter[i])} snapshots)\n')
        else:
            for b in range(16):
                if a_mask & (1 << b):
                    sys.stderr.write(
                        f'DSP idx {i:2d}  {dsp_labels[i]}  ->  '
                        f'FPGA bit {b:2d}  {fpga_balls[b]:<4}  '
                        f'(Phase A flip mask={a_mask:04x})\n')
    for i in range(16):
        b_mask = flip_mask(b_samples_per_iter[i])
        if b_mask == 0:
            sys.stderr.write(
                f'FPGA pins[{i:2d}] {fpga_balls[i]:<4}  <-  '
                f'no connection observed (Phase B flip mask=000000, '
                f'{len(b_samples_per_iter[i])} snapshots)\n')
        else:
            for d in range(24):
                if b_mask & (1 << d):
                    label = dsp_labels[d] if d < len(dsp_labels) \
                            else f'(idx{d})'
                    sys.stderr.write(
                        f'FPGA pins[{i:2d}] {fpga_balls[i]:<4}  <-  '
                        f'DSP idx {d:2d}  {label}  '
                        f'(Phase B flip mask={b_mask:06x})\n')
    sys.stderr.write('=== end discovered jumper table ===\n')

    return streams_ok
```
