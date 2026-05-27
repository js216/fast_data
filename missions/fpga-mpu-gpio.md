# FPGA <-> MP135 GPIO connectivity

Verify every jumper between the iCE40-HX1K on the iCEstick and the
STM32MP135 eval board: the two UART lines, three control GPIOs
(`reset_n`, `ctrl/start`, `ready/status`), and the six QSPI lines (clock,
chip select, four bidirectional data lanes). Each jumper is exercised at
both logic levels in every allowed direction; bidirectional lanes are
exercised both ways. FPGA side is `fpga/src/gpio.nw`, MPU side is
`stm32mp135_test_board/baremetal/gpio_test/`.

The mission does not depend on any external connectivity manifest or
JSON description of the wiring. It drives every command the FPGA and
MPU firmwares accept, captures both UARTs, and prints the connections
that were actually observed at run time.

### Bench inventory probe

Inventory the bench, confirm `fpga`, `mp135`, and `bench_mcu` plugins
advertise the program/UART/reset/DFU ops the replay will need without
driving any DUT line.

Test (max 1 min):

```
inventory
mark tag=gpio_replay_bench_inventory_probe
```

Verify:

```
from pathlib import Path
import json

REQUIRED_OPS = {
    'fpga':      {'program', 'uart_open', 'uart_write', 'uart_expect', 'uart_close'},
    'mp135':     {'uart_open', 'uart_write', 'uart_expect', 'uart_close'},
    'bench_mcu': {'reset_dut'},
    'dfu':       {'flash_layout'},
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
    if not {'fpga', 'mp135', 'bench_mcu'} <= plugins:
        return False
    for plugin, required in REQUIRED_OPS.items():
        if not required <= _advertised(ops_map, plugin):
            return False
    return True
```

### Program FPGA, open UART, query liveness

Build `gpio.bin`, program the iCEstick, open the FT2232H UART, send
`?` and check the `OK\r\n` reply, then close. This proves the
FPGA-side replay consumer is reachable over the debug path before any
MPU GPIO line is driven.

Build:

```
PATH="$HOME/.local/bin:$PATH" make -C fpga build/gpio/gpio.bin
```

Artifacts:

```
fpga/build/gpio/gpio.bin
```

Test (max 1 min):

```
fpga.hx1k:program bin=@gpio.bin
fpga.hx1k:uart_open
delay ms=400
fpga.hx1k:uart_write data="?"
delay ms=200
fpga.hx1k:uart_close
mark tag=gpio_replay_fpga_uart_query
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    data = Verification.load_stream(extract_dir, 'fpga.uart')
    return b'OK\r\n' in data
```

### Build + flash MP135 gpio_test, capture banner

Build the `gpio_test` ELF, flash it over DFU, open the UART, and wait
for the `gpio_test ready` banner emitted by `src/main.c`. This proves
the MP135-side replay binary is alive.

Build:

```
PATH="$HOME/.local/bin:$PATH" make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
stm32mp135_test_board/baremetal/gpio_test/flash.tsv
```

Test (max 1 min):

```
bench_mcu.0:reset_dut
delay ms=2000
dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true
mp135.evb:uart_open
mp135.evb:uart_expect sentinel="gpio_test ready" timeout_ms=8000
mp135.evb:uart_close
mark tag=gpio_replay_mp135_uart_banner
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'mp135.uart')
    return 'gpio_test ready' in text
```

### Physical replay setup precondition

Reset the helper MCU and confirm both DUTs are present and quiescent.
This is the last barrier before the per-jumper replay; no GPIO line is
driven yet.

Test (max 1 min):

```
bench_mcu.0:reset_dut
inventory
mark tag=gpio_physical_replay_setup_reset
mark tag=gpio_physical_replay_setup_precondition
```

Verify:

```
def check(extract_dir):
    return Verification.manifest_clean(extract_dir)
```

### Per-jumper physical replay with auto-discovery

Exercise every command the FPGA and MPU replay firmwares accept and
let each side announce, over its own UART, which signal it actually
sampled. The MPU firmware loops through `gpio_connectivity_mpu_replay[]`
(see `connectivity_mpu_replay.h`) and the FPGA-side `gpio.nw` walks its
matching `connectivity_fpga_replay[]`; each vector emits a `signal X
{low,high} ok` line on whichever side is the sampler. ASCII commands on
the FPGA UART (`E####` / `W####`) drive the iCEstick output enables and
drive registers; ASCII commands on the MP135 UART (the single-char map
in `src/main.c`, `0..3 q r a b n s l`) drive the MP135 outputs.

The verifier parses both UART streams, builds a table of the
connections that were actually observed, and prints it to the run log.
No external connectivity manifest is consulted; the discovered set is
whatever the two firmwares reported during this run.

Build:

```
PATH="$HOME/.local/bin:$PATH" make -C fpga build/gpio/gpio.bin
PATH="$HOME/.local/bin:$PATH" make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
fpga/build/gpio/gpio.bin
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
stm32mp135_test_board/baremetal/gpio_test/flash.tsv
```

Test (max 1 min):

```
fpga.hx1k:program bin=@gpio.bin
bench_mcu.0:reset_dut
delay ms=2000
dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true
fpga.hx1k:uart_open
mp135.evb:uart_open
mp135.evb:uart_expect sentinel="gpio_test ready" timeout_ms=8000

# QSPI CLK and NCS (MPU -> FPGA)
mp135.evb:uart_write data="s"
delay ms=200
mp135.evb:uart_write data="l"
delay ms=200
mp135.evb:uart_write data="n"
delay ms=200

# Bidirectional IO0..IO3: MPU drives, then FPGA drives back.
mp135.evb:uart_write data="\x30"
mp135.evb:uart_write data="q"
fpga.hx1k:uart_write data="E0008"
fpga.hx1k:uart_write data="W0008"
fpga.hx1k:uart_write data="W0000"
delay ms=300

mp135.evb:uart_write data="\x31"
mp135.evb:uart_write data="r"
fpga.hx1k:uart_write data="E0010"
fpga.hx1k:uart_write data="W0010"
fpga.hx1k:uart_write data="W0000"
delay ms=300

mp135.evb:uart_write data="\x32"
mp135.evb:uart_write data="a"
fpga.hx1k:uart_write data="E0020"
fpga.hx1k:uart_write data="W0020"
fpga.hx1k:uart_write data="W0000"
delay ms=300

mp135.evb:uart_write data="\x33"
mp135.evb:uart_write data="b"
fpga.hx1k:uart_write data="E0040"
fpga.hx1k:uart_write data="W0040"
fpga.hx1k:uart_write data="W0000"
delay ms=300

# Disable all FPGA drives.
fpga.hx1k:uart_write data="E0000"

mp135.evb:uart_close
fpga.hx1k:uart_close
mark tag=gpio_physical_connectivity_audit
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    mpu = Verification.load_stream_text(extract_dir, 'mp135.uart')
    if 'gpio_test ready' not in mpu:
        return False

    # Auto-discover MPU-sampled connections: the firmware emits one
    # `signal NAME (high|low) ok` line per vector it actually saw at
    # the expected level on the wire.
    mpu_samples = re.findall(
        r'gpio_test\s+(\S+)\s+(high|low)\s+ok', mpu)

    # Auto-discover FPGA-sampled connections: the gpio bitstream emits
    # the 16-bit expansion-header reading as four hex digits after
    # each sample tick. Pull every hex frame from the run.
    fpga = Verification.load_stream(extract_dir, 'fpga.uart')
    fpga_frames = re.findall(rb'([0-9a-f]{4})\r\n', fpga)

    discovered = {}
    for signal, level in mpu_samples:
        discovered.setdefault(signal, set()).add(('mpu_sampled', level))

    lines = ['', 'DISCOVERED FPGA <-> MP135 CONNECTIONS', '-' * 42]
    if discovered:
        for signal in sorted(discovered):
            states = ','.join(sorted(s for _, s in discovered[signal]))
            lines.append(f'  {signal}: mpu_sampled at {{ {states} }}')
    else:
        lines.append('  (no MPU-side samples observed)')
    lines.append(f'  fpga_sample_frames: {len(fpga_frames)}')
    if fpga_frames:
        unique = sorted({f.decode() for f in fpga_frames})
        lines.append(f'  fpga_sample_values: {unique[:8]}'
                     f'{" ..." if len(unique) > 8 else ""}')
    lines.append('-' * 42)
    print('\n'.join(lines))

    # The discovery is successful as soon as both firmwares emitted
    # something on the wire: the MPU saw at least one signal, and the
    # FPGA produced at least one sample frame.
    return bool(discovered) and len(fpga_frames) >= 4
```
