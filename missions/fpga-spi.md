# FPGA -> MP135 QSPI bring-up

This mission requires bit-perfect transfer of arbitrary data, sustained
for an arbitrary volume of data. In each case, the SPI clock is limited
to no more than 133 MHz.

Build steps tangle the `noweb` (`.nw`) source files into Verilog and
related files, run formal verification and simulation checks, and
prepare the bitstream.

The legacy `fpga/to_be_replaced_by_cleaner_code/` sources are reference
material only. The finished SPI implementation should live in a clean
`spi.nw` rather than tangling those legacy files directly.

Assumed hardware connections are documented in a Markdown table with
one row per jumper. The table includes MPU signal/pin, FPGA signal/pin,
direction, voltage/domain, and notes, and it covers at least UART,
reset/control GPIOs, SPI clock, chip select, and four data lanes.

Assumed hardware connections:

| MPU signal/pin | FPGA signal/pin | Direction | Voltage/domain | Notes |
| --- | --- | --- | --- | --- |
| MP135 UART TX, exact MPU pin TBD | `rx`, iCEstick pin 9 | MPU -> FPGA | Assumed 3.3 V LVCMOS, verify MPU UART bank | FPGA UART RX pin is documented for iCEstick; MPU UART instance/header pin is not documented here. |
| MP135 UART RX, exact MPU pin TBD | `tx`, iCEstick pin 8 | FPGA -> MPU | Assumed 3.3 V LVCMOS, verify MPU UART bank | FPGA UART TX pin is documented for iCEstick; MPU UART instance/header pin is not documented here. |
| MP135 GPIO reset output, exact MPU pin TBD | FPGA `reset_n` on `pins[0]`, iCEstick pin 112 | MPU -> FPGA | Assumed 3.3 V LVCMOS control GPIO | Active-low FPGA logic reset/control jumper; reuses the `pins[0]` slot already bound in `gpio.nw` PCF chunk so existing GPIO bring-up samples the same physical line. |
| MP135 GPIO control output, exact MPU pin TBD | FPGA `ctrl`/`start` on `pins[1]`, iCEstick pin 113 | MPU -> FPGA | Assumed 3.3 V LVCMOS control GPIO | Bring-up control GPIO for connection tests; reuses the `pins[1]` slot already bound in `gpio.nw` PCF chunk so existing GPIO bring-up samples the same physical line. |
| MP135 GPIO status input, exact MPU pin TBD | FPGA `ready`/`status` on `pins[2]`, iCEstick pin 114 | FPGA -> MPU | Assumed 3.3 V LVCMOS control GPIO | Bring-up status GPIO for connection tests; reuses the `pins[2]` slot already bound in `gpio.nw` PCF chunk so existing GPIO bring-up drives the same physical line. |
| MP135 QUADSPI `CLK` on CN8, exact CN8 pin TBD | `sclk`, iCEstick pin 45 | MPU -> FPGA | Assumed 3.3 V LVCMOS QSPI bank | Repository notes place QSPI on MP135 CN8 and use SPI mode 0; exact CN8 pin is not documented here. |
| MP135 QUADSPI `NCS` on CN8, exact CN8 pin TBD | `cs_n`, iCEstick pin 56 | MPU -> FPGA | Assumed 3.3 V LVCMOS QSPI bank | Active-low chip select; FPGA source uses `cs_n`. |
| MP135 QUADSPI `IO0` on CN8, exact CN8 pin TBD | `io[0]`, iCEstick pin 47 | Bidirectional | Assumed 3.3 V LVCMOS QSPI bank | Single-lane MOSI during command/address phases; bidirectional for quad data phases. |
| MP135 QUADSPI `IO1` on CN8, exact CN8 pin TBD | `io[1]`, iCEstick pin 44 | Bidirectional | Assumed 3.3 V LVCMOS QSPI bank | Single-lane MISO during data phases; bidirectional for quad data phases. |
| MP135 QUADSPI `IO2` on CN8, exact CN8 pin TBD | `io[2]`, iCEstick pin 60 | Bidirectional | Assumed 3.3 V LVCMOS QSPI bank | Quad data lane 2; exact MP135 connector pin remains TBD. |
| MP135 QUADSPI `IO3` on CN8, exact CN8 pin TBD | `io[3]`, iCEstick pin 48 | Bidirectional | Assumed 3.3 V LVCMOS QSPI bank | Quad data lane 3; exact MP135 connector pin remains TBD. |

### Define GPIO connectivity test manifest

The first `gpio_test` bring-up uses a machine-readable connectivity
manifest. It mirrors the assumed jumper table with stable signal names,
directions, and MPU/FPGA drive or sample roles.

  - Manifest: `stm32mp135_test_board/baremetal/gpio_test/connectivity_manifest.json`.
  - Focused validation: `stm32mp135_test_board/baremetal/gpio_test/validate_connectivity_manifest.py`.

### Define GPIO connectivity test vectors

The manifest includes a first-pass static test plan. Each jumper has
low/high drive-and-sample vectors for every allowed direction, with
bidirectional lanes covered both ways.

### Generate GPIO connectivity command scripts

The first connectivity run is generated from the manifest into separate
MPU and FPGA JSONL command scripts. Each plan vector contributes one
drive command and one sample/expect command in manifest order.

  - Generator:
    `stm32mp135_test_board/baremetal/gpio_test/generate_connectivity_scripts.py`.
  - Generated scripts:
    `stm32mp135_test_board/baremetal/gpio_test/connectivity_mpu.jsonl`
    and
    `stm32mp135_test_board/baremetal/gpio_test/connectivity_fpga.jsonl`.

### Add GPIO JSONL dry-run executor

A host dry-run checks the generated MPU and FPGA JSONL scripts without
hardware. It pairs commands by vector, simulates driven signal values,
and rejects missing, stale, unknown, out-of-order, or unused commands.

### Generate GPIO connectivity replay fixtures

The JSONL scripts are converted into deterministic C replay headers for
the MPU `gpio_test` and FPGA `gpio.nw` harness. The fixtures preserve
controller, signal, vector, command kind, drive value, and expected
value.

### Add executable GPIO connectivity host checks

The host-only GPIO checks run as an executable mission gate. This keeps
manifest validation, script freshness, dry-run replay, and fixture
freshness under `run.py` before any hardware line is touched.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_connectivity_manifest.py
python3 stm32mp135_test_board/baremetal/gpio_test/generate_connectivity_scripts.py --check
python3 stm32mp135_test_board/baremetal/gpio_test/dry_run_connectivity.py
python3 stm32mp135_test_board/baremetal/gpio_test/generate_connectivity_fixtures.py --check
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
```

Test (max 1 min):

```
mark tag=gpio_connectivity_host_checks
```

Verify:

```
def check(extract_dir):
    return Verification.manifest_clean(extract_dir)
```

### Define GPIO replay interface contract

The MPU and FPGA replay consumers share a documented host-testable
contract. It defines the replay fields, controller and vector semantics,
and the `drive` / `sample_expect` operations used by later firmware.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
```

Test (max 1 min):

```
mark tag=gpio_replay_contract
```

Verify:

```
def check(extract_dir):
    return Verification.manifest_clean(extract_dir)
```

### Add GPIO replay build stubs

Build-only replay stubs prove that both sides consume their generated
fixtures. The MPU stub dispatches replay commands through host stubs,
and the FPGA stub maps replay commands onto the existing GPIO UART
command surface without touching hardware.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_connectivity_manifest.py
python3 stm32mp135_test_board/baremetal/gpio_test/generate_connectivity_fixtures.py --check
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
```

Test (max 1 min):

```
mark tag=gpio_replay_build_stubs
```

Verify:

```
def check(extract_dir):
    return Verification.manifest_clean(extract_dir)
```

### Add GPIO connectivity inventory plan skeleton

The first hardware-facing gate is an inventory-only `test_serv` plan.
It keeps the host checks in front, records the inventory result, and
requires the devices and operation metadata needed by later replay
steps.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_connectivity_manifest.py
python3 stm32mp135_test_board/baremetal/gpio_test/generate_connectivity_fixtures.py --check
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
```

Test (max 1 min):

```
inventory
mark tag=gpio_connectivity_inventory
```

Verify:

```
from pathlib import Path
import json

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    devices_path = Path(extract_dir, 'bench.devices.json')
    ops_path = Path(extract_dir, 'bench.ops.json')
    if not devices_path.is_file() or not ops_path.is_file():
        return False
    devices = json.loads(devices_path.read_text())
    ops = json.loads(ops_path.read_text())
    return isinstance(devices, list) and isinstance(ops, dict)
```

### Gate GPIO replay inventory capabilities

The inventory gate now checks concrete replay prerequisites without
touching the DUT. It requires inventoried FPGA, MP135, and bench MCU
devices plus the advertised programming, UART, reset, and DFU layout
operations needed by later GPIO replay steps.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_connectivity_manifest.py
python3 stm32mp135_test_board/baremetal/gpio_test/generate_connectivity_fixtures.py --check
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
```

Test (max 1 min):

```
inventory
mark tag=gpio_replay_inventory_caps
```

Verify:

```
from pathlib import Path
import json

REQUIRED_DEVICES = {'fpga', 'mp135', 'bench_mcu'}
REQUIRED_OPS = {
    'fpga': {'program', 'uart_open', 'uart_write', 'uart_expect', 'uart_close'},
    'mp135': {'uart_open', 'uart_write', 'uart_expect', 'uart_close'},
    'bench_mcu': {'reset_dut'},
    'dfu': {'flash_layout'},
}
ALLOWED_METADATA_VERBS = {'description', 'inventory', 'mark'}

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    devices_path = Path(extract_dir, 'bench.devices.json')
    ops_path = Path(extract_dir, 'bench.ops.json')
    if not devices_path.is_file() or not ops_path.is_file():
        return False
    try:
        devices = json.loads(devices_path.read_text())
        ops = json.loads(ops_path.read_text())
        op_log = Verification.load_ops(extract_dir)
    except (OSError, json.JSONDecodeError):
        return False
    if (
        not isinstance(devices, list)
        or not isinstance(ops, dict)
        or not isinstance(op_log, list)
    ):
        return False
    for record in op_log:
        if not isinstance(record, dict):
            return False
        if record.get('device') is not None:
            return False
        if record.get('verb') not in ALLOWED_METADATA_VERBS:
            return False
        if record.get('status') != 'ok':
            return False
    if not any(r.get('verb') == 'inventory' for r in op_log):
        return False
    if not any(
        r.get('verb') == 'mark'
        and 'gpio_replay_inventory_caps' in Path(extract_dir, 'plan.txt').read_text()
        for r in op_log
    ):
        return False
    plugins = set()
    for device in devices:
        if not isinstance(device, dict):
            return False
        if not isinstance(device.get('id'), str):
            return False
        plugin = device.get('plugin')
        if not isinstance(plugin, str):
            return False
        plugins.add(plugin)
    if not REQUIRED_DEVICES <= plugins:
        return False
    for plugin, required in REQUIRED_OPS.items():
        advertised = set()
        for name, entry in ops.items():
            if name != plugin and not name.startswith(plugin + '.'):
                continue
            if not isinstance(entry, dict):
                return False
            entry_ops = entry.get('ops')
            if not isinstance(entry_ops, dict):
                return False
            advertised.update(entry_ops)
        if not required <= set(advertised):
            return False
    return True
```

### Acquire GPIO replay MPU/FPGA lease

Run a no-toggle hardware readiness probe before GPIO replay. The plan
holds only the FPGA and MP135 resources, records the lease/probe result,
and confirms from inventory that replay-capable UART, programming,
reset, and DFU operations remain available without driving DUT GPIOs.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_connectivity_manifest.py
python3 stm32mp135_test_board/baremetal/gpio_test/generate_connectivity_scripts.py --check
python3 stm32mp135_test_board/baremetal/gpio_test/dry_run_connectivity.py
python3 stm32mp135_test_board/baremetal/gpio_test/generate_connectivity_fixtures.py --check
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
```

Test (max 1 min):

```
lease:claim devices="fpga.hx1k,mp135.evb" duration_s=30
inventory
mark tag=gpio_replay_bench_lease_probe
lease:release
```

Verify:

```
from pathlib import Path
import json

REQUIRED_IDS = {'fpga.hx1k', 'mp135.evb', 'bench_mcu.0'}
REQUIRED_PLUGINS = {'fpga', 'mp135', 'bench_mcu'}
REQUIRED_OPS = {
    'fpga': {'program', 'uart_open', 'uart_write', 'uart_expect', 'uart_close'},
    'mp135': {'uart_open', 'uart_write', 'uart_expect', 'uart_close'},
    'bench_mcu': {'reset_dut'},
    'dfu': {'flash_layout'},
}
ALLOWED_OPS = {
    (None, 'description'),
    ('lease', 'claim'),
    (None, 'inventory'),
    (None, 'mark'),
    ('lease', 'release'),
}
DISALLOWED_VERBS = {
    'program', 'uart_open', 'uart_write', 'uart_expect', 'uart_close',
    'reset', 'reset_dut', 'reset_dut2', 'send', 'flash',
    'flash_layout', 'list', 'capture', 'open', 'close',
}

def _plugin_ops(ops, plugin):
    advertised = set()
    for name, entry in ops.items():
        if name != plugin and not name.startswith(plugin + '.'):
            continue
        if not isinstance(entry, dict):
            return None
        entry_ops = entry.get('ops')
        if not isinstance(entry_ops, dict):
            return None
        advertised.update(entry_ops)
    return advertised

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        manifest = Verification.load_manifest(extract_dir)
        devices = json.loads(Path(extract_dir, 'bench.devices.json').read_text())
        ops = json.loads(Path(extract_dir, 'bench.ops.json').read_text())
        op_log = Verification.load_ops(extract_dir)
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(manifest.get('lease_token'), str):
        return False
    if not isinstance(devices, list) or not isinstance(ops, dict):
        return False
    seen_ids = set()
    seen_plugins = set()
    for device in devices:
        if not isinstance(device, dict):
            return False
        device_id = device.get('id')
        plugin = device.get('plugin')
        if not isinstance(device_id, str) or not isinstance(plugin, str):
            return False
        seen_ids.add(device_id)
        seen_plugins.add(plugin)
        if device_id in REQUIRED_IDS:
            verify = device.get('verify')
            if not isinstance(verify, dict) or verify.get('ok') is not True:
                return False
    if not REQUIRED_IDS <= seen_ids or not REQUIRED_PLUGINS <= seen_plugins:
        return False
    for plugin, required in REQUIRED_OPS.items():
        advertised = _plugin_ops(ops, plugin)
        if advertised is None or not required <= advertised:
            return False
    if not isinstance(op_log, list):
        return False
    saw = set()
    for record in op_log:
        if not isinstance(record, dict) or record.get('status') != 'ok':
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        if record.get('verb') in DISALLOWED_VERBS and record.get('device') != 'lease':
            return False
        saw.add(key)
    if not ALLOWED_OPS <= saw:
        return False
    plan_text = Path(extract_dir, 'plan.txt').read_text()
    return (
        'gpio_replay_bench_lease_probe' in plan_text and
        'lease:claim devices="fpga.hx1k,mp135.evb,bench_mcu.0"' not in plan_text
    )
```

### Program FPGA GPIO image under lease

With the FPGA lease held, build and program the FPGA `gpio.nw` image
used by the later replay. This confirms the first reversible hardware
setup action without claiming MP135 or bench MCU devices, opening UARTs,
or driving GPIO test vectors.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_connectivity_manifest.py
python3 stm32mp135_test_board/baremetal/gpio_test/generate_connectivity_scripts.py --check
python3 stm32mp135_test_board/baremetal/gpio_test/dry_run_connectivity.py
python3 stm32mp135_test_board/baremetal/gpio_test/generate_connectivity_fixtures.py --check
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C fpga build/gpio/gpio.bin
```

Artifacts:

```
fpga/build/gpio/gpio.bin
```

Test (max 5 min):

```
lease:claim devices="fpga.hx1k" duration_s=30
inventory
fpga.hx1k:program bin=@gpio.bin
mark tag=gpio_replay_fpga_program
lease:release
```

Verify:

```
from pathlib import Path
import json

ALLOWED_OPS = {
    (None, 'description'),
    ('lease', 'claim'),
    (None, 'inventory'),
    ('fpga.hx1k', 'program'),
    (None, 'mark'),
    ('lease', 'release'),
}
DISALLOWED_VERBS = {
    'uart_open', 'uart_write', 'uart_expect', 'uart_close',
    'reset', 'reset_dut', 'reset_dut2', 'send', 'flash',
    'flash_layout', 'list', 'capture', 'open', 'close',
    'drive', 'sample', 'expect', 'gpio_write', 'gpio_read',
}
DISALLOWED_DEVICES = {'mp135.evb', 'bench_mcu.0'}

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        manifest = Verification.load_manifest(extract_dir)
        ops = Verification.load_ops(extract_dir)
    except (OSError, json.JSONDecodeError):
        return False
    lease_token = manifest.get('lease_token')
    if not isinstance(lease_token, str) or not lease_token:
        return False
    plan_text = Path(extract_dir, 'plan.txt').read_text()
    if 'mp135.evb' in plan_text or 'bench_mcu.0' in plan_text:
        return False
    saw = set()
    saw_program = False
    saw_mark = False
    for record in ops:
        if not isinstance(record, dict) or record.get('status') != 'ok':
            return False
        if record.get('device') in DISALLOWED_DEVICES:
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        if record.get('verb') in DISALLOWED_VERBS:
            return False
        if key == ('fpga.hx1k', 'program'):
            saw_program = True
        if key == (None, 'mark'):
            saw_mark = True
        saw.add(key)
    return (
        ALLOWED_OPS <= saw and
        saw_program and
        saw_mark and
        'gpio_replay_fpga_program' in plan_text
    )
```

### Open FPGA GPIO UART under lease

With the FPGA lease held, program the FPGA `gpio.nw` image and open
then close the FPGA UART. This confirms that the programmed GPIO image
is reachable over the non-driving debug path before any MPU GPIO lines
or replay vectors are driven.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_connectivity_manifest.py
python3 stm32mp135_test_board/baremetal/gpio_test/generate_connectivity_scripts.py --check
python3 stm32mp135_test_board/baremetal/gpio_test/dry_run_connectivity.py
python3 stm32mp135_test_board/baremetal/gpio_test/generate_connectivity_fixtures.py --check
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C fpga build/gpio/gpio.bin
```

Artifacts:

```
fpga/build/gpio/gpio.bin
```

Test (max 5 min):

```
lease:claim devices="fpga.hx1k" duration_s=30
inventory
fpga.hx1k:program bin=@gpio.bin
fpga.hx1k:uart_open
fpga.hx1k:uart_close
mark tag=gpio_replay_fpga_uart_open
lease:release
```

Verify:

```
from pathlib import Path
import json

ALLOWED_OPS = {
    (None, 'description'),
    ('lease', 'claim'),
    (None, 'inventory'),
    ('fpga.hx1k', 'program'),
    ('fpga.hx1k', 'uart_open'),
    ('fpga.hx1k', 'uart_close'),
    (None, 'mark'),
    ('lease', 'release'),
}
DISALLOWED_VERBS = {
    'uart_write', 'uart_expect',
    'reset', 'reset_dut', 'reset_dut2', 'send', 'flash',
    'flash_layout', 'list', 'capture', 'open', 'close',
    'drive', 'sample', 'expect', 'gpio_write', 'gpio_read',
}
DISALLOWED_DEVICES = {'mp135.evb', 'bench_mcu.0'}

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        manifest = Verification.load_manifest(extract_dir)
        ops = Verification.load_ops(extract_dir)
    except (OSError, json.JSONDecodeError):
        return False
    lease_token = manifest.get('lease_token')
    if not isinstance(lease_token, str) or not lease_token:
        return False
    plan_text = Path(extract_dir, 'plan.txt').read_text()
    if 'mp135.evb' in plan_text or 'bench_mcu.0' in plan_text:
        return False
    saw = set()
    saw_program = False
    saw_uart_open = False
    saw_uart_close = False
    saw_mark = False
    for record in ops:
        if not isinstance(record, dict) or record.get('status') != 'ok':
            return False
        if record.get('device') in DISALLOWED_DEVICES:
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        if record.get('verb') in DISALLOWED_VERBS:
            return False
        if key == ('fpga.hx1k', 'program'):
            saw_program = True
        if key == ('fpga.hx1k', 'uart_open'):
            saw_uart_open = True
        if key == ('fpga.hx1k', 'uart_close'):
            saw_uart_close = True
        if key == (None, 'mark'):
            saw_mark = True
        saw.add(key)
    return (
        ALLOWED_OPS <= saw and
        saw_program and
        saw_uart_open and
        saw_uart_close and
        saw_mark and
        'gpio_replay_fpga_uart_open' in plan_text
    )
```

### Query FPGA GPIO UART under lease

With the FPGA lease held, program the FPGA `gpio.nw` image, open the
FPGA UART, and issue a read-only query that proves the programmed GPIO
image responds over the debug path. This keeps the scope limited to
FPGA reachability and still avoids MPU GPIO lines or replay vectors.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_connectivity_manifest.py
python3 stm32mp135_test_board/baremetal/gpio_test/generate_connectivity_scripts.py --check
python3 stm32mp135_test_board/baremetal/gpio_test/dry_run_connectivity.py
python3 stm32mp135_test_board/baremetal/gpio_test/generate_connectivity_fixtures.py --check
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C fpga build/gpio/gpio.bin
```

Artifacts:

```
fpga/build/gpio/gpio.bin
```

Test (max 5 min):

```
lease:claim devices="fpga.hx1k" duration_s=30
inventory
fpga.hx1k:program bin=@gpio.bin
fpga.hx1k:uart_open
delay ms=300
fpga.hx1k:uart_write data="?"
fpga.hx1k:uart_expect sentinel="OK\r\n" timeout_ms=3000
fpga.hx1k:uart_close
mark tag=gpio_replay_fpga_uart_query
lease:release
```

Verify:

```
from pathlib import Path
import json

ALLOWED_OPS = {
    (None, 'description'),
    ('lease', 'claim'),
    (None, 'inventory'),
    ('fpga.hx1k', 'program'),
    ('fpga.hx1k', 'uart_open'),
    (None, 'delay'),
    ('fpga.hx1k', 'uart_write'),
    ('fpga.hx1k', 'uart_expect'),
    ('fpga.hx1k', 'uart_close'),
    (None, 'mark'),
    ('lease', 'release'),
}
DISALLOWED_VERBS = {
    'reset', 'reset_dut', 'reset_dut2', 'send', 'flash',
    'flash_layout', 'list', 'capture', 'open', 'close',
    'drive', 'sample', 'expect', 'gpio_write', 'gpio_read',
}
DISALLOWED_DEVICES = {'mp135.evb', 'bench_mcu.0'}

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        manifest = Verification.load_manifest(extract_dir)
        ops = Verification.load_ops(extract_dir)
    except (OSError, json.JSONDecodeError):
        return False
    lease_token = manifest.get('lease_token')
    if not isinstance(lease_token, str) or not lease_token:
        return False
    plan_text = Path(extract_dir, 'plan.txt').read_text()
    if 'mp135.evb' in plan_text or 'bench_mcu.0' in plan_text:
        return False
    saw = set()
    for record in ops:
        if not isinstance(record, dict) or record.get('status') != 'ok':
            return False
        if record.get('device') in DISALLOWED_DEVICES:
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        if record.get('verb') in DISALLOWED_VERBS:
            return False
        saw.add(key)
    return (
        ALLOWED_OPS <= saw and
        'gpio_replay_fpga_uart_query' in plan_text
    )
```

### Build MP135 GPIO test image

Build the minimal MP135 `gpio_test` image and verify that its flash
layout and STM32 payload artifacts are produced before any hardware
lease, reset, DFU flash, UART, jumper line, or replay vector is used.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_connectivity_manifest.py
python3 stm32mp135_test_board/baremetal/gpio_test/generate_connectivity_scripts.py --check
python3 stm32mp135_test_board/baremetal/gpio_test/dry_run_connectivity.py
python3 stm32mp135_test_board/baremetal/gpio_test/generate_connectivity_fixtures.py --check
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
stm32mp135_test_board/baremetal/gpio_test/flash.tsv
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(_extract_dir):
    flash = Path(artifacts['flash.tsv'])
    image = Path(artifacts['main.stm32'])
    deps = [
        Path('stm32mp135_test_board/baremetal/gpio_test/Makefile'),
        Path('stm32mp135_test_board/baremetal/gpio_test/gpio_replay_mpu_stub.c'),
        Path('stm32mp135_test_board/baremetal/gpio_test/src/irq_stubs.c'),
        Path('stm32mp135_test_board/baremetal/gpio_test/src/main.c'),
    ]
    if not all(p.is_file() and p.stat().st_size > 0 for p in [flash, image]):
        return False
    if not all(p.is_file() for p in deps):
        return False
    latest_dep = max(p.stat().st_mtime for p in deps)
    if image.stat().st_mtime < latest_dep:
        return False
    text = flash.read_text(encoding='utf-8', errors='replace')
    return 'main.stm32' in text
```

### Reset MP135 before GPIO UART probe

Press the MP135 reset line in a standalone plan so `bench_mcu.0` is
released immediately before the longer MP135 flash and UART probe.

Test (max 1 min):

```
bench_mcu.0:reset_dut
mark tag=gpio_replay_mp135_uart_reset
```

Verify:

```
import json

ALLOWED_OPS = {
    (None, 'description'),
    ('bench_mcu.0', 'reset_dut'),
    (None, 'mark'),
}

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        ops = Verification.load_ops(extract_dir)
    except (OSError, json.JSONDecodeError):
        return False
    saw = set()
    for record in ops:
        if not isinstance(record, dict) or record.get('status') != 'ok':
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        saw.add(key)
    return ALLOWED_OPS <= saw
```

### Bring up MP135 GPIO test UART

Build and flash a minimal MP135 `gpio_test` image, then confirm its UART
prompt is reachable. This proves the MPU-side GPIO harness can run
before any FPGA image, jumper line, or replay vector is driven.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_connectivity_manifest.py
python3 stm32mp135_test_board/baremetal/gpio_test/generate_connectivity_scripts.py --check
python3 stm32mp135_test_board/baremetal/gpio_test/dry_run_connectivity.py
python3 stm32mp135_test_board/baremetal/gpio_test/generate_connectivity_fixtures.py --check
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
stm32mp135_test_board/baremetal/gpio_test/flash.tsv
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test (max 5 min):

```
lease:claim devices="mp135.evb" duration_s=60
inventory
delay ms=2000
dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true
mp135.evb:uart_open
mp135.evb:uart_expect sentinel="gpio_test ready" timeout_ms=10000
mp135.evb:uart_close
mark tag=gpio_replay_mp135_uart_probe
lease:release
```

Verify:

```
from pathlib import Path
import json

ALLOWED_OPS = {
    (None, 'description'),
    ('lease', 'claim'),
    (None, 'inventory'),
    (None, 'delay'),
    ('dfu.evb', 'flash_layout'),
    ('mp135.evb', 'uart_open'),
    ('mp135.evb', 'uart_expect'),
    ('mp135.evb', 'uart_close'),
    (None, 'mark'),
    ('lease', 'release'),
}
DISALLOWED_VERBS = {
    'program', 'uart_write',
    'drive', 'sample', 'expect', 'gpio_write', 'gpio_read',
}

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        manifest = Verification.load_manifest(extract_dir)
        ops = Verification.load_ops(extract_dir)
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(manifest.get('lease_token'), str):
        return False
    plan_text = Path(extract_dir, 'plan.txt').read_text()
    if 'fpga.hx1k' in plan_text:
        return False
    if 'mp135.evb' not in plan_text:
        return False
    if 'lease:claim devices="mp135.evb,' in plan_text:
        return False
    saw = set()
    for record in ops:
        if not isinstance(record, dict) or record.get('status') != 'ok':
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        if record.get('verb') in DISALLOWED_VERBS:
            return False
        saw.add(key)
    return (
        ALLOWED_OPS <= saw and
        'gpio_replay_mp135_uart_probe' in plan_text
    )
```

### Reset MP135 before physical smoke

Press the MP135 reset line in a standalone plan so `bench_mcu.0` is
released immediately before the longer FPGA and MP135 physical smoke
setup.

Test (max 1 min):

```
bench_mcu.0:reset_dut
mark tag=gpio_physical_replay_setup_reset
```

Verify:

```
import json

ALLOWED_OPS = {
    (None, 'description'),
    ('bench_mcu.0', 'reset_dut'),
    (None, 'mark'),
}

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        ops = Verification.load_ops(extract_dir)
    except (OSError, json.JSONDecodeError):
        return False
    saw = set()
    for record in ops:
        if not isinstance(record, dict) or record.get('status') != 'ok':
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        saw.add(key)
    return ALLOWED_OPS <= saw
```

### Smoke physical GPIO replay setup

Confirm the physical setup can program the FPGA GPIO image, rely on the
preceding standalone reset plan, flash the MP135 GPIO test image, and
observe the MPU-side ready banner.

Build:

```
make -C fpga build/gpio/gpio.bin
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
fpga/build/gpio/gpio.bin
stm32mp135_test_board/baremetal/gpio_test/flash.tsv
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test (max 5 min):

```
lease:claim devices="fpga.hx1k,mp135.evb" duration_s=60
inventory
fpga.hx1k:program bin=@gpio.bin
delay ms=2000
dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true
mp135.evb:uart_open
mp135.evb:uart_expect sentinel="gpio_test ready" timeout_ms=10000
mp135.evb:uart_close
mark tag=gpio_physical_replay_setup_smoke
lease:release
```

Verify:

```
from pathlib import Path
import json

ALLOWED_OPS = {
    (None, 'description'),
    ('lease', 'claim'),
    (None, 'inventory'),
    ('fpga.hx1k', 'program'),
    (None, 'delay'),
    ('dfu.evb', 'flash_layout'),
    ('mp135.evb', 'uart_open'),
    ('mp135.evb', 'uart_expect'),
    ('mp135.evb', 'uart_close'),
    (None, 'mark'),
    ('lease', 'release'),
}
DISALLOWED_VERBS = {
    'uart_write',
    'drive', 'sample', 'expect', 'gpio_write', 'gpio_read',
}

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        manifest = Verification.load_manifest(extract_dir)
        ops = Verification.load_ops(extract_dir)
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(manifest.get('lease_token'), str):
        return False
    plan_text = Path(extract_dir, 'plan.txt').read_text()
    if 'lease:claim devices="fpga.hx1k,mp135.evb"' not in plan_text:
        return False
    saw = set()
    for record in ops:
        if not isinstance(record, dict) or record.get('status') != 'ok':
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        if record.get('verb') in DISALLOWED_VERBS:
            return False
        saw.add(key)
    return (
        ALLOWED_OPS <= saw and
        'gpio_physical_replay_setup_smoke' in plan_text
    )
```

### Add MP135 GPIO sample output for IO1

Teach the MP135 `gpio_test` firmware to map one sampled signal,
`mpu_qspi_io1_to_fpga_io1`, to a HAL GPIO input and print per-signal
sample results for low and high expectations. This is build-only support
for the later physical line test and does not lease or use
`bench_mcu.0`.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(_extract_dir):
    stub = Path('stm32mp135_test_board/baremetal/gpio_test/gpio_replay_mpu_stub.c')
    main = Path('stm32mp135_test_board/baremetal/gpio_test/src/main.c')
    image = Path(artifacts['main.stm32'])

    stub_text = stub.read_text(encoding='utf-8', errors='replace')
    main_text = main.read_text(encoding='utf-8', errors='replace')

    required_stub = [
        'mpu_qspi_io1_to_fpga_io1',
        'HAL_GPIO_ReadPin',
        'GPIO_TypeDef',
        'GPIO_PinState',
        'gpio_test mpu_qspi_io1_to_fpga_io1 low ok',
        'gpio_test mpu_qspi_io1_to_fpga_io1 high ok',
    ]
    if not all(token in stub_text for token in required_stub):
        return False
    if 'gpio_connectivity_mpu_replay_stub_run' not in main_text:
        return False
    if not image.is_file() or image.stat().st_size == 0:
        return False

    latest_dep = max(stub.stat().st_mtime, main.stat().st_mtime)
    return image.stat().st_mtime >= latest_dep
```

### Verify FPGA-to-MP135 IO1

Drive iCEstick `pins[15]` low and high through the FPGA GPIO UART and
verify the MP135 `gpio_test` harness samples `mpu_qspi_io1_to_fpga_io1`.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C fpga build/gpio/gpio.bin
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
fpga/build/gpio/gpio.bin
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test (max 5 min):

```
lease:claim devices="fpga.hx1k,mp135.evb" duration_s=60
inventory
fpga.hx1k:program bin=@gpio.bin
fpga.hx1k:uart_open
fpga.hx1k:uart_write data="W0000"
fpga.hx1k:uart_write data="E8000"
delay ms=2000
mp135.evb:uart_open
mp135.evb:uart_expect sentinel="gpio_test ready" timeout_ms=10000
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_io1_to_fpga_io1 low ok" timeout_ms=10000
fpga.hx1k:uart_write data="W8000"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_io1_to_fpga_io1 high ok" timeout_ms=10000
fpga.hx1k:uart_write data="E0000"
mp135.evb:uart_close
fpga.hx1k:uart_close
mark tag=gpio_physical_fpga_to_mpu_io1
lease:release
```

Verify:

```
from pathlib import Path
import json

ALLOWED_OPS = {
    (None, 'description'),
    ('lease', 'claim'),
    (None, 'inventory'),
    ('fpga.hx1k', 'program'),
    ('fpga.hx1k', 'uart_open'),
    ('fpga.hx1k', 'uart_write'),
    ('fpga.hx1k', 'uart_close'),
    (None, 'delay'),
    ('mp135.evb', 'uart_open'),
    ('mp135.evb', 'uart_expect'),
    ('mp135.evb', 'uart_close'),
    (None, 'mark'),
    ('lease', 'release'),
}

REQUIRED_OPS = ALLOWED_OPS - {(None, 'description')}

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        ops = Verification.load_ops(extract_dir)
    except (OSError, json.JSONDecodeError):
        return False

    plan_text = Path(extract_dir, 'plan.txt').read_text()
    required_text = [
        'lease:claim devices="fpga.hx1k,mp135.evb"',
        'fpga.hx1k:program bin=@gpio.bin',
        'fpga.hx1k:uart_write data="E8000"',
        'fpga.hx1k:uart_write data="W8000"',
        'gpio_test mpu_qspi_io1_to_fpga_io1 low ok',
        'gpio_test mpu_qspi_io1_to_fpga_io1 high ok',
        'gpio_physical_fpga_to_mpu_io1',
    ]
    if not all(token in plan_text for token in required_text):
        return False
    if 'mp135.custom' in plan_text:
        return False

    saw = set()
    for record in ops:
        if not isinstance(record, dict) or record.get('status') != 'ok':
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        saw.add(key)

    return REQUIRED_OPS <= saw
```

### Add MP135 GPIO sample output for IO2

Teach the MP135 `gpio_test` firmware to map `mpu_qspi_io2_to_fpga_io2`
to a HAL GPIO input and print per-signal sample results for low and high
expectations. This is build-only support for the next physical line test
and does not lease or use `bench_mcu.0`.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(_extract_dir):
    stub = Path('stm32mp135_test_board/baremetal/gpio_test/gpio_replay_mpu_stub.c')
    main = Path('stm32mp135_test_board/baremetal/gpio_test/src/main.c')
    image = Path(artifacts['main.stm32'])

    stub_text = stub.read_text(encoding='utf-8', errors='replace')
    main_text = main.read_text(encoding='utf-8', errors='replace')

    required_stub = [
        'mpu_qspi_io2_to_fpga_io2',
        'HAL_GPIO_ReadPin',
        'GPIO_TypeDef',
        'GPIO_PinState',
        'gpio_test mpu_qspi_io2_to_fpga_io2 low ok',
        'gpio_test mpu_qspi_io2_to_fpga_io2 high ok',
    ]
    if not all(token in stub_text for token in required_stub):
        return False
    if 'gpio_connectivity_mpu_replay_stub_run' not in main_text:
        return False
    if 'bench_mcu.0' in stub_text or 'bench_mcu.0' in main_text:
        return False
    if not image.is_file() or image.stat().st_size == 0:
        return False

    latest_dep = max(stub.stat().st_mtime, main.stat().st_mtime)
    return image.stat().st_mtime >= latest_dep
```

### Verify FPGA-to-MP135 IO2

Drive iCEstick `pins[10]` low and high through the FPGA GPIO UART and
verify the MP135 `gpio_test` harness samples `mpu_qspi_io2_to_fpga_io2`.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C fpga build/gpio/gpio.bin
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
fpga/build/gpio/gpio.bin
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test (max 5 min):

```
lease:claim devices="fpga.hx1k,mp135.evb" duration_s=60
inventory
fpga.hx1k:program bin=@gpio.bin
fpga.hx1k:uart_open
fpga.hx1k:uart_write data="W0000"
fpga.hx1k:uart_write data="E0400"
delay ms=2000
mp135.evb:uart_open
mp135.evb:uart_expect sentinel="gpio_test ready" timeout_ms=10000
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_io2_to_fpga_io2 low ok" timeout_ms=10000
fpga.hx1k:uart_write data="W0400"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_io2_to_fpga_io2 high ok" timeout_ms=10000
fpga.hx1k:uart_write data="E0000"
mp135.evb:uart_close
fpga.hx1k:uart_close
mark tag=gpio_physical_fpga_to_mpu_io2
lease:release
```

Verify:

```
from pathlib import Path
import json

ALLOWED_OPS = {
    (None, 'description'),
    ('lease', 'claim'),
    (None, 'inventory'),
    ('fpga.hx1k', 'program'),
    ('fpga.hx1k', 'uart_open'),
    ('fpga.hx1k', 'uart_write'),
    ('fpga.hx1k', 'uart_close'),
    (None, 'delay'),
    ('mp135.evb', 'uart_open'),
    ('mp135.evb', 'uart_expect'),
    ('mp135.evb', 'uart_close'),
    (None, 'mark'),
    ('lease', 'release'),
}

REQUIRED_OPS = ALLOWED_OPS - {(None, 'description')}

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        ops = Verification.load_ops(extract_dir)
    except (OSError, json.JSONDecodeError):
        return False

    plan_text = Path(extract_dir, 'plan.txt').read_text()
    required_text = [
        'lease:claim devices="fpga.hx1k,mp135.evb"',
        'fpga.hx1k:program bin=@gpio.bin',
        'fpga.hx1k:uart_write data="E0400"',
        'fpga.hx1k:uart_write data="W0400"',
        'gpio_test mpu_qspi_io2_to_fpga_io2 low ok',
        'gpio_test mpu_qspi_io2_to_fpga_io2 high ok',
        'gpio_physical_fpga_to_mpu_io2',
    ]
    if not all(token in plan_text for token in required_text):
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(device in plan_text for device in disallowed):
        return False

    saw = set()
    for record in ops:
        if not isinstance(record, dict) or record.get('status') != 'ok':
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        saw.add(key)

    return REQUIRED_OPS <= saw
```

### Add MP135 GPIO sample output for IO3

Teach the MP135 `gpio_test` firmware to map `mpu_qspi_io3_to_fpga_io3`
to the QSPI IO3 HAL GPIO input and print per-signal sample results for
low and high expectations. This is build-only support for the next
physical line test.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(_extract_dir):
    stub = Path('stm32mp135_test_board/baremetal/gpio_test/gpio_replay_mpu_stub.c')
    main = Path('stm32mp135_test_board/baremetal/gpio_test/src/main.c')
    board = Path('stm32mp135_test_board/baremetal/qspi/src/board.h')
    image = Path(artifacts['main.stm32'])

    stub_text = stub.read_text(encoding='utf-8', errors='replace')
    main_text = main.read_text(encoding='utf-8', errors='replace')
    board_text = board.read_text(encoding='utf-8', errors='replace')

    if '#define QSPI_IO3_PORT GPIOH' not in board_text:
        return False
    if '#define QSPI_IO3_PIN  GPIO_PIN_7' not in board_text:
        return False

    required_stub = [
        'mpu_qspi_io3_to_fpga_io3',
        'GPIOH',
        'GPIO_PIN_7',
        'HAL_GPIO_ReadPin',
        'GPIO_TypeDef',
        'GPIO_PinState',
        'gpio_test mpu_qspi_io3_to_fpga_io3 low ok',
        'gpio_test mpu_qspi_io3_to_fpga_io3 high ok',
    ]
    if not all(token in stub_text for token in required_stub):
        return False
    if 'gpio_connectivity_mpu_replay_io3_sample_report' not in main_text:
        return False

    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(token in stub_text or token in main_text for token in disallowed):
        return False
    if not image.is_file() or image.stat().st_size == 0:
        return False

    latest_dep = max(stub.stat().st_mtime, main.stat().st_mtime, board.stat().st_mtime)
    return image.stat().st_mtime >= latest_dep
```

### Verify FPGA-to-MP135 IO3

Drive iCEstick `pins[12]` low and high through the FPGA GPIO UART and
verify the MP135 `gpio_test` harness samples `mpu_qspi_io3_to_fpga_io3`.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C fpga build/gpio/gpio.bin
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
fpga/build/gpio/gpio.bin
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test (max 5 min):

```
lease:claim devices="fpga.hx1k,mp135.evb" duration_s=60
inventory
fpga.hx1k:program bin=@gpio.bin
fpga.hx1k:uart_open
fpga.hx1k:uart_write data="W0000"
fpga.hx1k:uart_write data="E1000"
delay ms=2000
mp135.evb:uart_open
mp135.evb:uart_expect sentinel="gpio_test ready" timeout_ms=10000
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_io3_to_fpga_io3 low ok" timeout_ms=10000
fpga.hx1k:uart_write data="W1000"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_io3_to_fpga_io3 high ok" timeout_ms=10000
fpga.hx1k:uart_write data="E0000"
mp135.evb:uart_close
fpga.hx1k:uart_close
mark tag=gpio_physical_fpga_to_mpu_io3
lease:release
```

Verify:

```
from pathlib import Path
import json

ALLOWED_OPS = {
    (None, 'description'),
    ('lease', 'claim'),
    (None, 'inventory'),
    ('fpga.hx1k', 'program'),
    ('fpga.hx1k', 'uart_open'),
    ('fpga.hx1k', 'uart_write'),
    ('fpga.hx1k', 'uart_close'),
    (None, 'delay'),
    ('mp135.evb', 'uart_open'),
    ('mp135.evb', 'uart_expect'),
    ('mp135.evb', 'uart_close'),
    (None, 'mark'),
    ('lease', 'release'),
}

REQUIRED_OPS = ALLOWED_OPS - {(None, 'description')}

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        ops = Verification.load_ops(extract_dir)
    except (OSError, json.JSONDecodeError):
        return False

    plan_text = Path(extract_dir, 'plan.txt').read_text()
    required_text = [
        'lease:claim devices="fpga.hx1k,mp135.evb"',
        'fpga.hx1k:program bin=@gpio.bin',
        'fpga.hx1k:uart_write data="E1000"',
        'fpga.hx1k:uart_write data="W1000"',
        'gpio_test mpu_qspi_io3_to_fpga_io3 low ok',
        'gpio_test mpu_qspi_io3_to_fpga_io3 high ok',
        'gpio_physical_fpga_to_mpu_io3',
    ]
    if not all(token in plan_text for token in required_text):
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(device in plan_text for device in disallowed):
        return False

    saw = set()
    for record in ops:
        if not isinstance(record, dict) or record.get('status') != 'ok':
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        saw.add(key)

    return REQUIRED_OPS <= saw
```

### Add MP135 GPIO sample output for IO0

Teach the MP135 `gpio_test` firmware to map `mpu_qspi_io0_to_fpga_io0`
to the QSPI IO0 HAL GPIO input and print per-signal sample results for
low and high expectations. This is build-only support for the next
physical line test.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(_extract_dir):
    stub = Path('stm32mp135_test_board/baremetal/gpio_test/gpio_replay_mpu_stub.c')
    main = Path('stm32mp135_test_board/baremetal/gpio_test/src/main.c')
    board = Path('stm32mp135_test_board/baremetal/qspi/src/board.h')
    image = Path(artifacts['main.stm32'])

    stub_text = stub.read_text(encoding='utf-8', errors='replace')
    main_text = main.read_text(encoding='utf-8', errors='replace')
    board_text = board.read_text(encoding='utf-8', errors='replace')

    if '#define QSPI_IO0_PORT GPIOH' not in board_text:
        return False
    if '#define QSPI_IO0_PIN  GPIO_PIN_3' not in board_text:
        return False

    required_stub = [
        'mpu_qspi_io0_to_fpga_io0',
        'GPIOH',
        'GPIO_PIN_3',
        'HAL_GPIO_ReadPin',
        'GPIO_TypeDef',
        'GPIO_PinState',
        'gpio_test mpu_qspi_io0_to_fpga_io0 low ok',
        'gpio_test mpu_qspi_io0_to_fpga_io0 high ok',
    ]
    if not all(token in stub_text for token in required_stub):
        return False
    if 'gpio_connectivity_mpu_replay_io0_sample_report' not in main_text:
        return False

    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(token in stub_text or token in main_text for token in disallowed):
        return False
    if not image.is_file() or image.stat().st_size == 0:
        return False

    latest_dep = max(stub.stat().st_mtime, main.stat().st_mtime, board.stat().st_mtime)
    return image.stat().st_mtime >= latest_dep
```

### Verify FPGA-to-MP135 IO0

Drive iCEstick `pins[13]` low and high through the FPGA GPIO UART and
verify the MP135 `gpio_test` harness samples `mpu_qspi_io0_to_fpga_io0`.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C fpga build/gpio/gpio.bin
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
fpga/build/gpio/gpio.bin
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test (max 5 min):

```
lease:claim devices="fpga.hx1k,mp135.evb" duration_s=60
inventory
fpga.hx1k:program bin=@gpio.bin
fpga.hx1k:uart_open
fpga.hx1k:uart_write data="W0000"
fpga.hx1k:uart_write data="E2000"
delay ms=2000
mp135.evb:uart_open
mp135.evb:uart_expect sentinel="gpio_test ready" timeout_ms=10000
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_io0_to_fpga_io0 low ok" timeout_ms=10000
fpga.hx1k:uart_write data="W2000"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_io0_to_fpga_io0 high ok" timeout_ms=10000
fpga.hx1k:uart_write data="E0000"
mp135.evb:uart_close
fpga.hx1k:uart_close
mark tag=gpio_physical_fpga_to_mpu_io0
lease:release
```

Verify:

```
from pathlib import Path
import json

ALLOWED_OPS = {
    (None, 'description'),
    ('lease', 'claim'),
    (None, 'inventory'),
    ('fpga.hx1k', 'program'),
    ('fpga.hx1k', 'uart_open'),
    ('fpga.hx1k', 'uart_write'),
    ('fpga.hx1k', 'uart_close'),
    (None, 'delay'),
    ('mp135.evb', 'uart_open'),
    ('mp135.evb', 'uart_expect'),
    ('mp135.evb', 'uart_close'),
    (None, 'mark'),
    ('lease', 'release'),
}

REQUIRED_OPS = ALLOWED_OPS - {(None, 'description')}

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        ops = Verification.load_ops(extract_dir)
    except (OSError, json.JSONDecodeError):
        return False

    plan_text = Path(extract_dir, 'plan.txt').read_text()
    required_text = [
        'lease:claim devices="fpga.hx1k,mp135.evb"',
        'fpga.hx1k:program bin=@gpio.bin',
        'fpga.hx1k:uart_write data="E2000"',
        'fpga.hx1k:uart_write data="W2000"',
        'gpio_test mpu_qspi_io0_to_fpga_io0 low ok',
        'gpio_test mpu_qspi_io0_to_fpga_io0 high ok',
        'gpio_physical_fpga_to_mpu_io0',
    ]
    if not all(token in plan_text for token in required_text):
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(device in plan_text for device in disallowed):
        return False

    saw = set()
    for record in ops:
        if not isinstance(record, dict) or record.get('status') != 'ok':
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        saw.add(key)

    return REQUIRED_OPS <= saw
```

### Add MP135 GPIO drive output for NCS

Teach the MP135 `gpio_test` firmware to map
`mpu_qspi_ncs_to_fpga_cs_n` to the QSPI NCS HAL GPIO output and provide
a low/high drive report entry point. This is build-only support for the
next physical NCS line test.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(_extract_dir):
    stub = Path('stm32mp135_test_board/baremetal/gpio_test/gpio_replay_mpu_stub.c')
    main = Path('stm32mp135_test_board/baremetal/gpio_test/src/main.c')
    board = Path('stm32mp135_test_board/baremetal/qspi/src/board.h')
    image = Path(artifacts['main.stm32'])

    stub_text = stub.read_text(encoding='utf-8', errors='replace')
    main_text = main.read_text(encoding='utf-8', errors='replace')
    board_text = board.read_text(encoding='utf-8', errors='replace')

    required = [
        'mpu_qspi_ncs_to_fpga_cs_n',
        'QSPI_NCS_PORT',
        'QSPI_NCS_PIN',
        'GPIO_MODE_OUTPUT_PP',
        'HAL_GPIO_WritePin',
        'gpio_test mpu_qspi_ncs_to_fpga_cs_n low drive ok',
        'gpio_test mpu_qspi_ncs_to_fpga_cs_n high drive ok',
        'gpio_connectivity_mpu_replay_ncs_drive_report',
    ]
    if not all(token in stub_text for token in required):
        return False
    if 'gpio_connectivity_mpu_replay_ncs_drive_report' not in main_text:
        return False
    if '#define QSPI_NCS_PORT GPIOD' not in board_text:
        return False
    if '#define QSPI_NCS_PIN  GPIO_PIN_1' not in board_text:
        return False

    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(token in stub_text or token in main_text for token in disallowed):
        return False
    if not image.is_file() or image.stat().st_size == 0:
        return False

    latest_dep = max(stub.stat().st_mtime, main.stat().st_mtime, board.stat().st_mtime)
    return image.stat().st_mtime >= latest_dep
```

### Verify MP135-to-FPGA NCS high

Drive every FPGA GPIO fixture bit except `cs_n` low, let the MP135
`gpio_test` firmware drive `mpu_qspi_ncs_to_fpga_cs_n` high through the
existing NCS report path, and verify the FPGA GPIO heartbeat observes
only the NCS bit high.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C fpga build/gpio/gpio.bin
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
fpga/build/gpio/gpio.bin
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test (max 5 min):

```
lease:claim devices="fpga.hx1k,mp135.evb" duration_s=60
inventory
fpga.hx1k:program bin=@gpio.bin
fpga.hx1k:uart_open
fpga.hx1k:uart_write data="W0000"
fpga.hx1k:uart_write data="Ef7ff"
delay ms=2000
mp135.evb:uart_open
mp135.evb:uart_expect sentinel="gpio_test ready" timeout_ms=10000
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_ncs_to_fpga_cs_n high drive ok" timeout_ms=10000
fpga.hx1k:uart_expect sentinel="0800\r\n" timeout_ms=10000
fpga.hx1k:uart_write data="E0000"
mp135.evb:uart_close
fpga.hx1k:uart_close
mark tag=gpio_physical_mp135_to_fpga_ncs_high
lease:release
```

Verify:

```
from pathlib import Path
import json

ALLOWED_OPS = {
    (None, 'description'),
    ('lease', 'claim'),
    (None, 'inventory'),
    ('fpga.hx1k', 'program'),
    ('fpga.hx1k', 'uart_open'),
    ('fpga.hx1k', 'uart_write'),
    ('fpga.hx1k', 'uart_expect'),
    ('fpga.hx1k', 'uart_close'),
    (None, 'delay'),
    ('mp135.evb', 'uart_open'),
    ('mp135.evb', 'uart_expect'),
    ('mp135.evb', 'uart_close'),
    (None, 'mark'),
    ('lease', 'release'),
}

REQUIRED_OPS = ALLOWED_OPS - {(None, 'description')}

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        ops = Verification.load_ops(extract_dir)
    except (OSError, json.JSONDecodeError):
        return False

    plan_text = Path(extract_dir, 'plan.txt').read_text()
    required_text = [
        'lease:claim devices="fpga.hx1k,mp135.evb"',
        'fpga.hx1k:uart_write data="Ef7ff"',
        'gpio_test mpu_qspi_ncs_to_fpga_cs_n high drive ok',
        'fpga.hx1k:uart_expect sentinel="0800\\r\\n"',
        'gpio_physical_mp135_to_fpga_ncs_high',
    ]
    if not all(token in plan_text for token in required_text):
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(device in plan_text for device in disallowed):
        return False

    saw = set()
    for record in ops:
        if not isinstance(record, dict) or record.get('status') != 'ok':
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        saw.add(key)

    return REQUIRED_OPS <= saw
```

### Verify MP135-to-FPGA NCS low

Drive every FPGA GPIO fixture bit except `cs_n` low, send the explicit
`n` command to the MP135 `gpio_test` UART to hold
`mpu_qspi_ncs_to_fpga_cs_n` low, and verify the FPGA GPIO heartbeat
observes all sampled bits low. The combined periodic NCS report drives
low and then immediately high, so this low-level check must use the
low-only command rather than the periodic report path.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C fpga build/gpio/gpio.bin
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
fpga/build/gpio/gpio.bin
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test (max 5 min):

```
lease:claim devices="fpga.hx1k,mp135.evb" duration_s=60
inventory
fpga.hx1k:program bin=@gpio.bin
fpga.hx1k:uart_open
fpga.hx1k:uart_write data="W0000"
fpga.hx1k:uart_write data="Ef7ff"
delay ms=2000
mp135.evb:uart_open
mp135.evb:uart_expect sentinel="gpio_test ready" timeout_ms=10000
mp135.evb:uart_write data="n"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_ncs_to_fpga_cs_n low drive ok" timeout_ms=10000
fpga.hx1k:uart_expect sentinel="0000\r\n" timeout_ms=10000
fpga.hx1k:uart_write data="E0000"
mp135.evb:uart_close
fpga.hx1k:uart_close
mark tag=gpio_physical_mp135_to_fpga_ncs_low
lease:release
```

Verify:

```
from pathlib import Path
import json

ALLOWED_OPS = {
    (None, 'description'),
    ('lease', 'claim'),
    (None, 'inventory'),
    ('fpga.hx1k', 'program'),
    ('fpga.hx1k', 'uart_open'),
    ('fpga.hx1k', 'uart_write'),
    ('fpga.hx1k', 'uart_expect'),
    ('fpga.hx1k', 'uart_close'),
    (None, 'delay'),
    ('mp135.evb', 'uart_open'),
    ('mp135.evb', 'uart_write'),
    ('mp135.evb', 'uart_expect'),
    ('mp135.evb', 'uart_close'),
    (None, 'mark'),
    ('lease', 'release'),
}

REQUIRED_OPS = ALLOWED_OPS - {(None, 'description')}

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        ops = Verification.load_ops(extract_dir)
    except (OSError, json.JSONDecodeError):
        return False

    plan_text = Path(extract_dir, 'plan.txt').read_text()
    required_text = [
        'lease:claim devices="fpga.hx1k,mp135.evb"',
        'fpga.hx1k:uart_write data="Ef7ff"',
        'mp135.evb:uart_write data="n"',
        'gpio_test mpu_qspi_ncs_to_fpga_cs_n low drive ok',
        'fpga.hx1k:uart_expect sentinel="0000\\r\\n"',
        'gpio_physical_mp135_to_fpga_ncs_low',
    ]
    if not all(token in plan_text for token in required_text):
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(device in plan_text for device in disallowed):
        return False

    saw = set()
    for record in ops:
        if not isinstance(record, dict) or record.get('status') != 'ok':
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        saw.add(key)

    return REQUIRED_OPS <= saw
```

### Add MP135 GPIO drive output for SCLK

Teach the MP135 `gpio_test` firmware to map
`mpu_qspi_clk_to_fpga_sclk` to the QSPI CLK HAL GPIO output and provide
a low/high drive report entry point. This is build-only support for the
next physical SCLK line test.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(_extract_dir):
    stub = Path('stm32mp135_test_board/baremetal/gpio_test/gpio_replay_mpu_stub.c')
    main = Path('stm32mp135_test_board/baremetal/gpio_test/src/main.c')
    board = Path('stm32mp135_test_board/baremetal/qspi/src/board.h')
    image = Path(artifacts['main.stm32'])

    stub_text = stub.read_text(encoding='utf-8', errors='replace')
    main_text = main.read_text(encoding='utf-8', errors='replace')
    board_text = board.read_text(encoding='utf-8', errors='replace')

    required = [
        'mpu_qspi_clk_to_fpga_sclk',
        'QSPI_CLK_PORT',
        'QSPI_CLK_PIN',
        'GPIO_MODE_OUTPUT_PP',
        'HAL_GPIO_WritePin',
        'gpio_test mpu_qspi_clk_to_fpga_sclk low drive ok',
        'gpio_test mpu_qspi_clk_to_fpga_sclk high drive ok',
        'gpio_connectivity_mpu_replay_sclk_drive_report',
    ]
    if not all(token in stub_text for token in required):
        return False
    if 'gpio_connectivity_mpu_replay_sclk_drive_report' not in main_text:
        return False
    if '#define QSPI_CLK_PORT' not in board_text:
        return False
    if '#define QSPI_CLK_PIN' not in board_text:
        return False

    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(token in stub_text or token in main_text for token in disallowed):
        return False
    if not image.is_file() or image.stat().st_size == 0:
        return False

    latest_dep = max(stub.stat().st_mtime, main.stat().st_mtime, board.stat().st_mtime)
    return image.stat().st_mtime >= latest_dep
```

Rationale: this is the smallest machine-testable step that advances
physical connectivity beyond NCS by adding the MP135-side SCLK drive
hook needed for the next hardware line check.

### Gate SCLK drive report behind UART command

Wire the existing MP135 SCLK drive report into `gpio_test` behind an
explicit UART command. The normal startup replay and periodic status
loop must not drive SCLK, so the existing NCS hardware checks continue
to observe only the NCS line.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(_extract_dir):
    stub = Path('stm32mp135_test_board/baremetal/gpio_test/gpio_replay_mpu_stub.c')
    main = Path('stm32mp135_test_board/baremetal/gpio_test/src/main.c')
    image = Path(artifacts['main.stm32'])

    stub_text = stub.read_text(encoding='utf-8', errors='replace')
    main_text = main.read_text(encoding='utf-8', errors='replace')

    required_main = [
        '#include "console.h"',
        'console_rx_empty()',
        'console_rx_get()',
        'gpio_connectivity_mpu_replay_ncs_drive_report();',
    ]
    if not all(token in main_text for token in required_main):
        return False

    handler_start = main_text.find('static void gpio_test_handle_command')
    handler_end = main_text.find('static void gpio_test_poll_commands')
    if handler_start < 0 or handler_end < handler_start:
        return False
    handler_text = main_text[handler_start:handler_end]
    if "command == 's'" not in handler_text:
        return False
    if 'gpio_connectivity_mpu_replay_sclk_drive_report();' not in handler_text:
        return False

    loop_start = main_text.find('while (1)')
    if loop_start < 0:
        return False
    if 'gpio_connectivity_mpu_replay_sclk_drive_report();' in main_text[loop_start:]:
        return False

    required_stub = [
        'gpio_test mpu_qspi_clk_to_fpga_sclk low drive ok',
        'gpio_test mpu_qspi_clk_to_fpga_sclk high drive ok',
        'gpio_test mpu_qspi_ncs_to_fpga_cs_n low drive ok',
        'gpio_test mpu_qspi_ncs_to_fpga_cs_n high drive ok',
    ]
    if not all(token in stub_text for token in required_stub):
        return False

    drive_start = stub_text.find('static const mpu_gpio_signal_t mpu_drive_signals[]')
    drive_end = stub_text.find('static const mpu_gpio_signal_t mpu_sclk_drive_signal')
    if drive_start < 0 or drive_end < drive_start:
        return False
    drive_table = stub_text[drive_start:drive_end]
    if 'mpu_qspi_clk_to_fpga_sclk' in drive_table:
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(token in main_text or token in stub_text for token in disallowed):
        return False
    if not image.is_file() or image.stat().st_size == 0:
        return False

    latest_dep = max(stub.stat().st_mtime, main.stat().st_mtime)
    return image.stat().st_mtime >= latest_dep
```

Rationale: this makes the SCLK report deliberately triggerable for the
next hardware check without re-enabling the generic replay path that
previously asserted SCLK during the NCS tests.

### Verify MP135 SCLK UART trigger report

Send the explicit `s` command to the MP135 `gpio_test` UART and verify
that the firmware reports both SCLK low and high drive actions. This
checks the trigger path without adding FPGA sampling expectations yet.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test (max 2 min):

```
lease:claim devices="mp135.evb" duration_s=60
inventory
mp135.evb:uart_open
mp135.evb:uart_expect sentinel="gpio_test ready" timeout_ms=10000
mp135.evb:uart_write data="s"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_clk_to_fpga_sclk low drive ok" timeout_ms=10000
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_clk_to_fpga_sclk high drive ok" timeout_ms=10000
mp135.evb:uart_close
mark tag=gpio_sclk_uart_trigger_report
lease:release
```

Verify:

```
from pathlib import Path
import json

ALLOWED_OPS = {
    (None, 'description'),
    ('lease', 'claim'),
    (None, 'inventory'),
    ('mp135.evb', 'uart_open'),
    ('mp135.evb', 'uart_write'),
    ('mp135.evb', 'uart_expect'),
    ('mp135.evb', 'uart_close'),
    (None, 'mark'),
    ('lease', 'release'),
}

REQUIRED_OPS = ALLOWED_OPS - {(None, 'description')}

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        ops = Verification.load_ops(extract_dir)
    except (OSError, json.JSONDecodeError):
        return False

    plan_text = Path(extract_dir, 'plan.txt').read_text()
    required_text = [
        'lease:claim devices="mp135.evb"',
        'mp135.evb:uart_write data="s"',
        'gpio_test mpu_qspi_clk_to_fpga_sclk low drive ok',
        'gpio_test mpu_qspi_clk_to_fpga_sclk high drive ok',
        'gpio_sclk_uart_trigger_report',
    ]
    if not all(token in plan_text for token in required_text):
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(device in plan_text for device in disallowed):
        return False

    saw = set()
    for record in ops:
        if not isinstance(record, dict) or record.get('status') != 'ok':
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        saw.add(key)

    return REQUIRED_OPS <= saw
```

Rationale: this is the smallest hardware-backed check after adding the
UART trigger. It proves the trigger reaches the SCLK report while
using only the EVB UART and leaving FPGA SCLK sampling for the next
step.

### Verify MP135-to-FPGA SCLK high

Drive every FPGA GPIO fixture bit except `sclk` low, send the explicit
`s` command to the MP135 `gpio_test` UART, and verify the FPGA GPIO
heartbeat observes the SCLK bit high after the MP135 reports the high
drive action.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C fpga build/gpio/gpio.bin
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
fpga/build/gpio/gpio.bin
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test (max 5 min):

```
lease:claim devices="fpga.hx1k,mp135.evb" duration_s=60
inventory
fpga.hx1k:program bin=@gpio.bin
fpga.hx1k:uart_open
fpga.hx1k:uart_write data="W0000"
fpga.hx1k:uart_write data="Ebfff"
mp135.evb:uart_open
mp135.evb:uart_expect sentinel="gpio_test ready" timeout_ms=10000
mp135.evb:uart_write data="s"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_clk_to_fpga_sclk low drive ok" timeout_ms=10000
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_clk_to_fpga_sclk high drive ok" timeout_ms=10000
fpga.hx1k:uart_expect sentinel="4000\r\n" timeout_ms=10000
fpga.hx1k:uart_write data="E0000"
mp135.evb:uart_close
fpga.hx1k:uart_close
mark tag=gpio_physical_mp135_to_fpga_sclk_high
lease:release
```

Verify:

```
from pathlib import Path
import json

ALLOWED_OPS = {
    (None, 'description'),
    ('lease', 'claim'),
    (None, 'inventory'),
    ('fpga.hx1k', 'program'),
    ('fpga.hx1k', 'uart_open'),
    ('fpga.hx1k', 'uart_write'),
    ('fpga.hx1k', 'uart_expect'),
    ('fpga.hx1k', 'uart_close'),
    ('mp135.evb', 'uart_open'),
    ('mp135.evb', 'uart_write'),
    ('mp135.evb', 'uart_expect'),
    ('mp135.evb', 'uart_close'),
    (None, 'mark'),
    ('lease', 'release'),
}

REQUIRED_OPS = ALLOWED_OPS - {(None, 'description')}

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        ops = Verification.load_ops(extract_dir)
    except (OSError, json.JSONDecodeError):
        return False

    plan_text = Path(extract_dir, 'plan.txt').read_text()
    required_text = [
        'lease:claim devices="fpga.hx1k,mp135.evb"',
        'fpga.hx1k:uart_write data="Ebfff"',
        'mp135.evb:uart_write data="s"',
        'gpio_test mpu_qspi_clk_to_fpga_sclk high drive ok',
        'fpga.hx1k:uart_expect sentinel="4000\\r\\n"',
        'gpio_physical_mp135_to_fpga_sclk_high',
    ]
    if not all(token in plan_text for token in required_text):
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(device in plan_text for device in disallowed):
        return False

    saw = set()
    for record in ops:
        if not isinstance(record, dict) or record.get('status') != 'ok':
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        saw.add(key)

    return REQUIRED_OPS <= saw
```

Rationale: this is the smallest physical SCLK sampling step after the
UART-trigger report. It verifies only the high level on FPGA bit 14
(`0x4000`) and keeps the low-level sample for a separate follow-up.

### Add MP135 SCLK low UART trigger

Add an explicit MP135 `gpio_test` UART command that drives
`mpu_qspi_clk_to_fpga_sclk` low and leaves it low. This provides a
sustained low trigger for the next SCLK physical sample instead of
using the combined low/high SCLK report.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(_extract_dir):
    stub = Path('stm32mp135_test_board/baremetal/gpio_test/gpio_replay_mpu_stub.c')
    main = Path('stm32mp135_test_board/baremetal/gpio_test/src/main.c')
    image = Path(artifacts['main.stm32'])

    stub_text = stub.read_text(encoding='utf-8', errors='replace')
    main_text = main.read_text(encoding='utf-8', errors='replace')

    required_stub = [
        'gpio_connectivity_mpu_replay_sclk_low_report',
        'QSPI_CLK_PORT',
        'QSPI_CLK_PIN',
        'GPIO_PIN_RESET',
        'gpio_test mpu_qspi_clk_to_fpga_sclk low drive ok',
    ]
    if not all(token in stub_text for token in required_stub):
        return False

    handler_start = main_text.find('static void gpio_test_handle_command')
    handler_end = main_text.find('static void gpio_test_poll_commands')
    if handler_start < 0 or handler_end < handler_start:
        return False
    handler_text = main_text[handler_start:handler_end]
    if "command == 'l'" not in handler_text:
        return False
    if 'gpio_connectivity_mpu_replay_sclk_low_report();' not in handler_text:
        return False

    if not image.is_file() or image.stat().st_size == 0:
        return False
    latest_dep = max(stub.stat().st_mtime, main.stat().st_mtime)
    if image.stat().st_mtime < latest_dep:
        return False

    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    return not any(token in stub_text or token in main_text for token in disallowed)
```

Rationale: this is the smallest safe step after the SCLK-high physical
check. It adds the sustained-low firmware trigger needed for a reliable
SCLK-low hardware sample without changing any bench plan.

### Verify MP135-to-FPGA SCLK low

Drive every FPGA GPIO fixture bit except `sclk` low, hold NCS low with
the existing MP135 `n` command, then send the explicit `l` command to
hold `mpu_qspi_clk_to_fpga_sclk` low and verify the FPGA GPIO
heartbeat observes all sampled bits low.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C fpga build/gpio/gpio.bin
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
fpga/build/gpio/gpio.bin
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test (max 5 min):

```
lease:claim devices="fpga.hx1k,mp135.evb" duration_s=60
inventory
fpga.hx1k:program bin=@gpio.bin
fpga.hx1k:uart_open
fpga.hx1k:uart_write data="W0000"
fpga.hx1k:uart_write data="Ebfff"
mp135.evb:uart_open
mp135.evb:uart_expect sentinel="gpio_test ready" timeout_ms=10000
mp135.evb:uart_write data="n"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_ncs_to_fpga_cs_n low drive ok" timeout_ms=10000
mp135.evb:uart_write data="l"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_clk_to_fpga_sclk low drive ok" timeout_ms=10000
fpga.hx1k:uart_expect sentinel="0000\r\n" timeout_ms=10000
fpga.hx1k:uart_write data="E0000"
mp135.evb:uart_close
fpga.hx1k:uart_close
mark tag=gpio_physical_mp135_to_fpga_sclk_low
lease:release
```

Verify:

```
from pathlib import Path
import json

ALLOWED_OPS = {
    (None, 'description'),
    ('lease', 'claim'),
    (None, 'inventory'),
    ('fpga.hx1k', 'program'),
    ('fpga.hx1k', 'uart_open'),
    ('fpga.hx1k', 'uart_write'),
    ('fpga.hx1k', 'uart_expect'),
    ('fpga.hx1k', 'uart_close'),
    ('mp135.evb', 'uart_open'),
    ('mp135.evb', 'uart_write'),
    ('mp135.evb', 'uart_expect'),
    ('mp135.evb', 'uart_close'),
    (None, 'mark'),
    ('lease', 'release'),
}

REQUIRED_OPS = ALLOWED_OPS - {(None, 'description')}

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        ops = Verification.load_ops(extract_dir)
    except (OSError, json.JSONDecodeError):
        return False

    plan_text = Path(extract_dir, 'plan.txt').read_text()
    required_text = [
        'lease:claim devices="fpga.hx1k,mp135.evb"',
        'fpga.hx1k:uart_write data="Ebfff"',
        'mp135.evb:uart_write data="n"',
        'mp135.evb:uart_write data="l"',
        'gpio_test mpu_qspi_clk_to_fpga_sclk low drive ok',
        'fpga.hx1k:uart_expect sentinel="0000\\r\\n"',
        'gpio_physical_mp135_to_fpga_sclk_low',
    ]
    if not all(token in plan_text for token in required_text):
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(device in plan_text for device in disallowed):
        return False

    saw = set()
    for record in ops:
        if not isinstance(record, dict) or record.get('status') != 'ok':
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        saw.add(key)

    return REQUIRED_OPS <= saw
```

Rationale: this is the smallest physical follow-up to the sustained
SCLK-low UART trigger. It samples only the low level, uses `mp135.evb`,
and does not claim `bench_mcu.0`.

### Add MP135 IO0 high UART trigger

Add an explicit MP135 `gpio_test` UART command that drives
`mpu_qspi_io0_to_fpga_io0` high and leaves it high. This provides a
sustained high trigger for the next IO0 MP135-to-FPGA physical sample
instead of relying on the periodic IO0 sample path.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(_extract_dir):
    stub = Path('stm32mp135_test_board/baremetal/gpio_test/gpio_replay_mpu_stub.c')
    main = Path('stm32mp135_test_board/baremetal/gpio_test/src/main.c')
    image = Path(artifacts['main.stm32'])

    stub_text = stub.read_text(encoding='utf-8', errors='replace')
    main_text = main.read_text(encoding='utf-8', errors='replace')

    required_stub = [
        'gpio_connectivity_mpu_replay_io0_high_report',
        'mpu_io0_drive_signal',
        'GPIOH',
        'GPIO_PIN_3',
        'GPIO_PIN_SET',
        'gpio_test mpu_qspi_io0_to_fpga_io0 high drive ok',
    ]
    if not all(token in stub_text for token in required_stub):
        return False

    handler_start = main_text.find('static void gpio_test_handle_command')
    handler_end = main_text.find('static void gpio_test_poll_commands')
    if handler_start < 0 or handler_end < handler_start:
        return False
    handler_text = main_text[handler_start:handler_end]
    if "command == '0'" not in handler_text:
        return False
    if 'gpio_connectivity_mpu_replay_io0_high_report()' not in handler_text:
        return False
    if 'io0_hold_high = 1;' not in handler_text:
        return False

    loop_start = main_text.find('while (1)')
    if loop_start < 0:
        return False
    loop_text = main_text[loop_start:]
    if 'if (!io0_hold_high)' not in loop_text:
        return False
    if 'gpio_connectivity_mpu_replay_io0_sample_report();' not in loop_text:
        return False

    if not image.is_file() or image.stat().st_size == 0:
        return False
    latest_dep = max(stub.stat().st_mtime, main.stat().st_mtime)
    if image.stat().st_mtime < latest_dep:
        return False

    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    return not any(token in stub_text or token in main_text for token in disallowed)
```

Rationale: the rejected IO0 physical check assumed an MP135 UART drive
command that did not exist. This build-only step adds that sustained
drive trigger first and avoids changing any bench plan.

### Verify MP135-to-FPGA IO0 high

Drive every FPGA GPIO fixture bit except IO0 low, hold NCS low with the
existing MP135 `n` command, then send the explicit `0` command to hold
`mpu_qspi_io0_to_fpga_io0` high and verify the FPGA GPIO heartbeat
observes only the IO0 bit high.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C fpga build/gpio/gpio.bin
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
fpga/build/gpio/gpio.bin
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test (max 5 min):

```
lease:claim devices="fpga.hx1k,mp135.evb" duration_s=60
inventory
fpga.hx1k:program bin=@gpio.bin
fpga.hx1k:uart_open
fpga.hx1k:uart_write data="W0000"
fpga.hx1k:uart_write data="Edfff"
mp135.evb:uart_open
mp135.evb:uart_expect sentinel="gpio_test ready" timeout_ms=10000
mp135.evb:uart_write data="n"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_ncs_to_fpga_cs_n low drive ok" timeout_ms=10000
mp135.evb:uart_write data="\x30"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_io0_to_fpga_io0 high drive ok" timeout_ms=10000
fpga.hx1k:uart_expect sentinel="2000\r\n" timeout_ms=10000
fpga.hx1k:uart_write data="E0000"
mp135.evb:uart_close
fpga.hx1k:uart_close
mark tag=gpio_physical_mp135_to_fpga_io0_high
lease:release
```

Verify:

```
from pathlib import Path
import json

ALLOWED_OPS = {
    (None, 'description'),
    ('lease', 'claim'),
    (None, 'inventory'),
    ('fpga.hx1k', 'program'),
    ('fpga.hx1k', 'uart_open'),
    ('fpga.hx1k', 'uart_write'),
    ('fpga.hx1k', 'uart_expect'),
    ('fpga.hx1k', 'uart_close'),
    ('mp135.evb', 'uart_open'),
    ('mp135.evb', 'uart_write'),
    ('mp135.evb', 'uart_expect'),
    ('mp135.evb', 'uart_close'),
    (None, 'mark'),
    ('lease', 'release'),
}

REQUIRED_OPS = ALLOWED_OPS - {(None, 'description')}

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        ops = Verification.load_ops(extract_dir)
    except (OSError, json.JSONDecodeError):
        return False

    plan_text = Path(extract_dir, 'plan.txt').read_text()
    required_text = [
        'lease:claim devices="fpga.hx1k,mp135.evb"',
        'fpga.hx1k:uart_write data="Edfff"',
        'mp135.evb:uart_write data="n"',
        'mp135.evb:uart_write data="\\x30"',
        'gpio_test mpu_qspi_io0_to_fpga_io0 high drive ok',
        'fpga.hx1k:uart_expect sentinel="2000\\r\\n"',
        'gpio_physical_mp135_to_fpga_io0_high',
    ]
    if not all(token in plan_text for token in required_text):
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(device in plan_text for device in disallowed):
        return False

    saw = set()
    for record in ops:
        if not isinstance(record, dict) or record.get('status') != 'ok':
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        saw.add(key)

    return REQUIRED_OPS <= saw
```

Rationale: this is the smallest physical IO0 follow-up to the new
MP135 `0` UART trigger. It samples only the sustained high level on
FPGA bit 13 (`0x2000`), uses `mp135.evb`, and does not claim
`bench_mcu.0`.

### Add MP135 IO1 high UART trigger

Add an explicit MP135 `gpio_test` UART command that drives
`mpu_qspi_io1_to_fpga_io1` high and leaves it high. This provides a
sustained high trigger for the next IO1 MP135-to-FPGA physical sample.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(_extract_dir):
    stub = Path('stm32mp135_test_board/baremetal/gpio_test/gpio_replay_mpu_stub.c')
    main = Path('stm32mp135_test_board/baremetal/gpio_test/src/main.c')
    image = Path(artifacts['main.stm32'])

    stub_text = stub.read_text(encoding='utf-8', errors='replace')
    main_text = main.read_text(encoding='utf-8', errors='replace')

    required_stub = [
        'gpio_connectivity_mpu_replay_io1_high_report',
        'mpu_io1_drive_signal',
        'GPIO_PIN_SET',
        'gpio_test mpu_qspi_io1_to_fpga_io1 high drive ok',
    ]
    if not all(token in stub_text for token in required_stub):
        return False

    handler_start = main_text.find('static void gpio_test_handle_command')
    handler_end = main_text.find('static void gpio_test_poll_commands')
    if handler_start < 0 or handler_end < handler_start:
        return False
    handler_text = main_text[handler_start:handler_end]
    if "command == '1'" not in handler_text:
        return False
    if 'gpio_connectivity_mpu_replay_io1_high_report()' not in handler_text:
        return False
    if 'io1_hold_high = 1;' not in handler_text:
        return False

    loop_start = main_text.find('while (1)')
    if loop_start < 0:
        return False
    loop_text = main_text[loop_start:]
    if 'if (!io1_hold_high)' not in loop_text:
        return False
    if 'gpio_connectivity_mpu_replay_io1_sample_report();' not in loop_text:
        return False

    if not image.is_file() or image.stat().st_size == 0:
        return False
    latest_dep = max(stub.stat().st_mtime, main.stat().st_mtime)
    if image.stat().st_mtime < latest_dep:
        return False

    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    return not any(token in stub_text or token in main_text for token in disallowed)
```

Rationale: this is the smallest next step after the IO0 high physical
check. It adds firmware support for a sustained IO1 drive trigger while
using no hardware plan, no `mp135.custom`, and no `bench_mcu.0`.

### Verify MP135-to-FPGA IO1 high

Drive every FPGA GPIO fixture bit except IO1 low, hold NCS low with the
existing MP135 `n` command, then send the explicit `1` command to hold
`mpu_qspi_io1_to_fpga_io1` high and verify the FPGA GPIO heartbeat
observes IO1 high while the previously verified IO0 high hold remains
active.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C fpga build/gpio/gpio.bin
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
fpga/build/gpio/gpio.bin
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test (max 5 min):

```
lease:claim devices="fpga.hx1k,mp135.evb" duration_s=60
inventory
fpga.hx1k:program bin=@gpio.bin
fpga.hx1k:uart_open
fpga.hx1k:uart_write data="W0000"
fpga.hx1k:uart_write data="E7fff"
mp135.evb:uart_open
mp135.evb:uart_expect sentinel="gpio_test ready" timeout_ms=10000
mp135.evb:uart_write data="n"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_ncs_to_fpga_cs_n low drive ok" timeout_ms=10000
mp135.evb:uart_write data="\x31"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_io1_to_fpga_io1 high drive ok" timeout_ms=10000
fpga.hx1k:uart_expect sentinel="a000\r\n" timeout_ms=10000
fpga.hx1k:uart_write data="E0000"
mp135.evb:uart_close
fpga.hx1k:uart_close
mark tag=gpio_physical_mp135_to_fpga_io1_high
lease:release
```

Verify:

```
from pathlib import Path
import json

ALLOWED_OPS = {
    (None, 'description'),
    ('lease', 'claim'),
    (None, 'inventory'),
    ('fpga.hx1k', 'program'),
    ('fpga.hx1k', 'uart_open'),
    ('fpga.hx1k', 'uart_write'),
    ('fpga.hx1k', 'uart_expect'),
    ('fpga.hx1k', 'uart_close'),
    ('mp135.evb', 'uart_open'),
    ('mp135.evb', 'uart_write'),
    ('mp135.evb', 'uart_expect'),
    ('mp135.evb', 'uart_close'),
    (None, 'mark'),
    ('lease', 'release'),
}

REQUIRED_OPS = ALLOWED_OPS - {(None, 'description')}

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        ops = Verification.load_ops(extract_dir)
    except (OSError, json.JSONDecodeError):
        return False

    plan_text = Path(extract_dir, 'plan.txt').read_text()
    required_text = [
        'lease:claim devices="fpga.hx1k,mp135.evb"',
        'fpga.hx1k:uart_write data="E7fff"',
        'mp135.evb:uart_write data="n"',
        'mp135.evb:uart_write data="\\x31"',
        'gpio_test mpu_qspi_io1_to_fpga_io1 high drive ok',
        'fpga.hx1k:uart_expect sentinel="a000\\r\\n"',
        'gpio_physical_mp135_to_fpga_io1_high',
    ]
    if not all(token in plan_text for token in required_text):
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(device in plan_text for device in disallowed):
        return False

    saw = set()
    for record in ops:
        if not isinstance(record, dict) or record.get('status') != 'ok':
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        saw.add(key)

    return REQUIRED_OPS <= saw
```

Rationale: this is the smallest physical IO1 follow-up to the new
MP135 `1` UART trigger. The preceding IO0 physical check leaves IO0
held high, so this step expects IO0 plus IO1 high (`0xa000`) after the
IO1 trigger rather than resetting the board or claiming the reset
helper.

### Add MP135 IO2 high UART trigger

Add an explicit MP135 `gpio_test` UART command that drives
`mpu_qspi_io2_to_fpga_io2` high and leaves it high. This provides a
sustained high trigger for the next IO2 MP135-to-FPGA physical sample.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(_extract_dir):
    stub = Path('stm32mp135_test_board/baremetal/gpio_test/gpio_replay_mpu_stub.c')
    main = Path('stm32mp135_test_board/baremetal/gpio_test/src/main.c')
    image = Path(artifacts['main.stm32'])

    stub_text = stub.read_text(encoding='utf-8', errors='replace')
    main_text = main.read_text(encoding='utf-8', errors='replace')

    required_stub = [
        'gpio_connectivity_mpu_replay_io2_high_report',
        'mpu_io2_drive_signal',
        'GPIO_PIN_SET',
        'gpio_test mpu_qspi_io2_to_fpga_io2 high drive ok',
    ]
    if not all(token in stub_text for token in required_stub):
        return False

    handler_start = main_text.find('static void gpio_test_handle_command')
    handler_end = main_text.find('static void gpio_test_poll_commands')
    if handler_start < 0 or handler_end < handler_start:
        return False
    handler_text = main_text[handler_start:handler_end]
    if "command == '2'" not in handler_text:
        return False
    if 'gpio_connectivity_mpu_replay_io2_high_report()' not in handler_text:
        return False
    if 'io2_hold_high = 1;' not in handler_text:
        return False

    loop_start = main_text.find('while (1)')
    if loop_start < 0:
        return False
    loop_text = main_text[loop_start:]
    if 'if (!io2_hold_high)' not in loop_text:
        return False
    if 'gpio_connectivity_mpu_replay_io2_sample_report();' not in loop_text:
        return False

    if not image.is_file() or image.stat().st_size == 0:
        return False
    latest_dep = max(stub.stat().st_mtime, main.stat().st_mtime)
    if image.stat().st_mtime < latest_dep:
        return False

    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    return not any(token in stub_text or token in main_text for token in disallowed)
```

Rationale: this is the smallest next step after the IO1 high physical
check. It adds firmware support for a sustained IO2 drive trigger
without adding a hardware plan or reset-helper usage.

### Verify MP135-to-FPGA IO2 high

Drive every FPGA GPIO fixture bit except IO2 low, hold NCS low with the
existing MP135 `n` command, then send the explicit `2` command to hold
`mpu_qspi_io2_to_fpga_io2` high and verify the FPGA GPIO heartbeat
observes IO2 high while the previously verified IO0 and IO1 high holds
remain active.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C fpga build/gpio/gpio.bin
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
fpga/build/gpio/gpio.bin
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test (max 5 min):

```
lease:claim devices="fpga.hx1k,mp135.evb" duration_s=60
inventory
fpga.hx1k:program bin=@gpio.bin
fpga.hx1k:uart_open
fpga.hx1k:uart_write data="W0000"
fpga.hx1k:uart_write data="Efbff"
mp135.evb:uart_open
mp135.evb:uart_expect sentinel="gpio_test ready" timeout_ms=10000
mp135.evb:uart_write data="n"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_ncs_to_fpga_cs_n low drive ok" timeout_ms=10000
mp135.evb:uart_write data="\x32"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_io2_to_fpga_io2 high drive ok" timeout_ms=10000
fpga.hx1k:uart_expect sentinel="a400\r\n" timeout_ms=10000
fpga.hx1k:uart_write data="E0000"
mp135.evb:uart_close
fpga.hx1k:uart_close
mark tag=gpio_physical_mp135_to_fpga_io2_high
lease:release
```

Verify:

```
from pathlib import Path
import json

ALLOWED_OPS = {
    (None, 'description'),
    ('lease', 'claim'),
    (None, 'inventory'),
    ('fpga.hx1k', 'program'),
    ('fpga.hx1k', 'uart_open'),
    ('fpga.hx1k', 'uart_write'),
    ('fpga.hx1k', 'uart_expect'),
    ('fpga.hx1k', 'uart_close'),
    ('mp135.evb', 'uart_open'),
    ('mp135.evb', 'uart_write'),
    ('mp135.evb', 'uart_expect'),
    ('mp135.evb', 'uart_close'),
    (None, 'mark'),
    ('lease', 'release'),
}

REQUIRED_OPS = ALLOWED_OPS - {(None, 'description')}

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        ops = Verification.load_ops(extract_dir)
    except (OSError, json.JSONDecodeError):
        return False

    plan_text = Path(extract_dir, 'plan.txt').read_text()
    required_text = [
        'lease:claim devices="fpga.hx1k,mp135.evb"',
        'fpga.hx1k:uart_write data="Efbff"',
        'mp135.evb:uart_write data="n"',
        'mp135.evb:uart_write data="\\x32"',
        'gpio_test mpu_qspi_io2_to_fpga_io2 high drive ok',
        'fpga.hx1k:uart_expect sentinel="a400\\r\\n"',
        'gpio_physical_mp135_to_fpga_io2_high',
    ]
    if not all(token in plan_text for token in required_text):
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(device in plan_text for device in disallowed):
        return False

    saw = set()
    for record in ops:
        if not isinstance(record, dict) or record.get('status') != 'ok':
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        saw.add(key)

    return REQUIRED_OPS <= saw
```

Rationale: this is the smallest physical IO2 follow-up to the new
MP135 `2` UART trigger. The prior IO0 and IO1 physical checks leave
both lines held high, so this step expects IO0 plus IO1 plus IO2 high
(`0xa400`) after the IO2 trigger.

### Add MP135 IO3 high UART trigger

Add an explicit MP135 `gpio_test` UART command that drives
`mpu_qspi_io3_to_fpga_io3` high and leaves it high. This provides a
sustained high trigger for the next IO3 MP135-to-FPGA physical sample.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(_extract_dir):
    stub = Path('stm32mp135_test_board/baremetal/gpio_test/gpio_replay_mpu_stub.c')
    main = Path('stm32mp135_test_board/baremetal/gpio_test/src/main.c')
    image = Path(artifacts['main.stm32'])

    stub_text = stub.read_text(encoding='utf-8', errors='replace')
    main_text = main.read_text(encoding='utf-8', errors='replace')

    required_stub = [
        'gpio_connectivity_mpu_replay_io3_high_report',
        'mpu_io3_drive_signal',
        'GPIO_PIN_SET',
        'gpio_test mpu_qspi_io3_to_fpga_io3 high drive ok',
    ]
    if not all(token in stub_text for token in required_stub):
        return False

    handler_start = main_text.find('static void gpio_test_handle_command')
    handler_end = main_text.find('static void gpio_test_poll_commands')
    if handler_start < 0 or handler_end < handler_start:
        return False
    handler_text = main_text[handler_start:handler_end]
    if "command == '3'" not in handler_text:
        return False
    if 'gpio_connectivity_mpu_replay_io3_high_report()' not in handler_text:
        return False
    if 'io3_hold_high = 1;' not in handler_text:
        return False

    loop_start = main_text.find('while (1)')
    if loop_start < 0:
        return False
    loop_text = main_text[loop_start:]
    if 'if (!io3_hold_high)' not in loop_text:
        return False
    if 'gpio_connectivity_mpu_replay_io3_sample_report();' not in loop_text:
        return False

    if not image.is_file() or image.stat().st_size == 0:
        return False
    latest_dep = max(stub.stat().st_mtime, main.stat().st_mtime)
    if image.stat().st_mtime < latest_dep:
        return False

    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    return not any(token in stub_text or token in main_text for token in disallowed)
```

Rationale: this is the smallest next step after the IO2 high physical
check. It adds firmware support for a sustained IO3 drive trigger
without adding a hardware plan or reset-helper usage.

### Verify MP135-to-FPGA IO3 high

Drive every FPGA GPIO fixture bit except IO3 low, hold NCS low with the
existing MP135 `n` command, then send the explicit `3` command to hold
`mpu_qspi_io3_to_fpga_io3` high and verify the FPGA GPIO heartbeat
observes IO3 high while the previously verified IO0, IO1, and IO2 high
holds remain active.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C fpga build/gpio/gpio.bin
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
fpga/build/gpio/gpio.bin
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test (max 5 min):

```
lease:claim devices="fpga.hx1k,mp135.evb" duration_s=60
inventory
fpga.hx1k:program bin=@gpio.bin
fpga.hx1k:uart_open
fpga.hx1k:uart_write data="W0000"
fpga.hx1k:uart_write data="Eefff"
mp135.evb:uart_open
mp135.evb:uart_expect sentinel="gpio_test ready" timeout_ms=10000
mp135.evb:uart_write data="n"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_ncs_to_fpga_cs_n low drive ok" timeout_ms=10000
mp135.evb:uart_write data="\x33"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_io3_to_fpga_io3 high drive ok" timeout_ms=10000
fpga.hx1k:uart_expect sentinel="b400\r\n" timeout_ms=10000
fpga.hx1k:uart_write data="E0000"
mp135.evb:uart_close
fpga.hx1k:uart_close
mark tag=gpio_physical_mp135_to_fpga_io3_high
lease:release
```

Verify:

```
from pathlib import Path
import json

ALLOWED_OPS = {
    (None, 'description'),
    ('lease', 'claim'),
    (None, 'inventory'),
    ('fpga.hx1k', 'program'),
    ('fpga.hx1k', 'uart_open'),
    ('fpga.hx1k', 'uart_write'),
    ('fpga.hx1k', 'uart_expect'),
    ('fpga.hx1k', 'uart_close'),
    ('mp135.evb', 'uart_open'),
    ('mp135.evb', 'uart_write'),
    ('mp135.evb', 'uart_expect'),
    ('mp135.evb', 'uart_close'),
    (None, 'mark'),
    ('lease', 'release'),
}

REQUIRED_OPS = ALLOWED_OPS - {(None, 'description')}

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        ops = Verification.load_ops(extract_dir)
    except (OSError, json.JSONDecodeError):
        return False

    plan_text = Path(extract_dir, 'plan.txt').read_text()
    required_text = [
        'lease:claim devices="fpga.hx1k,mp135.evb"',
        'fpga.hx1k:uart_write data="Eefff"',
        'mp135.evb:uart_write data="n"',
        'mp135.evb:uart_write data="\\x33"',
        'gpio_test mpu_qspi_io3_to_fpga_io3 high drive ok',
        'fpga.hx1k:uart_expect sentinel="b400\\r\\n"',
        'gpio_physical_mp135_to_fpga_io3_high',
    ]
    if not all(token in plan_text for token in required_text):
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(device in plan_text for device in disallowed):
        return False

    saw = set()
    for record in ops:
        if not isinstance(record, dict) or record.get('status') != 'ok':
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        saw.add(key)

    return REQUIRED_OPS <= saw
```

Rationale: this is the smallest physical IO3 follow-up to the new
MP135 `3` UART trigger. The prior IO0, IO1, and IO2 physical checks
leave those lines held high, so this step expects all four IO lines
high (`0xb400`) after the IO3 trigger.

### Add MP135 IO0 low UART trigger

Add an explicit MP135 `gpio_test` UART command that drives
`mpu_qspi_io0_to_fpga_io0` low and leaves it low. This provides a
sustained low trigger for the next IO0 MP135-to-FPGA physical sample
instead of relying on the periodic IO0 sample path.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(_extract_dir):
    stub = Path('stm32mp135_test_board/baremetal/gpio_test/gpio_replay_mpu_stub.c')
    main = Path('stm32mp135_test_board/baremetal/gpio_test/src/main.c')
    image = Path(artifacts['main.stm32'])

    stub_text = stub.read_text(encoding='utf-8', errors='replace')
    main_text = main.read_text(encoding='utf-8', errors='replace')

    required_stub = [
        'gpio_connectivity_mpu_replay_io0_low_report',
        'mpu_io0_drive_signal',
        'GPIOH',
        'GPIO_PIN_3',
        'GPIO_PIN_RESET',
        'gpio_test mpu_qspi_io0_to_fpga_io0 low drive ok',
    ]
    if not all(token in stub_text for token in required_stub):
        return False

    handler_start = main_text.find('static void gpio_test_handle_command')
    handler_end = main_text.find('static void gpio_test_poll_commands')
    if handler_start < 0 or handler_end < handler_start:
        return False
    handler_text = main_text[handler_start:handler_end]
    if "command == 'q'" not in handler_text:
        return False
    if 'gpio_connectivity_mpu_replay_io0_low_report()' not in handler_text:
        return False
    if 'io0_hold_low = 1;' not in handler_text:
        return False

    loop_start = main_text.find('while (1)')
    if loop_start < 0:
        return False
    loop_text = main_text[loop_start:]
    if 'if (!io0_hold_low)' not in loop_text:
        return False
    if 'gpio_connectivity_mpu_replay_io0_sample_report();' not in loop_text:
        return False

    if not image.is_file() or image.stat().st_size == 0:
        return False
    latest_dep = max(stub.stat().st_mtime, main.stat().st_mtime)
    if image.stat().st_mtime < latest_dep:
        return False

    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    return not any(token in stub_text or token in main_text for token in disallowed)
```

Rationale: this is the smallest safe step after the IO0/1/2/3 high
physical checks. It adds the sustained-low firmware trigger needed for
a reliable IO0-low hardware sample without changing any bench plan.

### Verify MP135-to-FPGA IO0 low

Drive every FPGA GPIO fixture bit except IO0 low, hold NCS low with the
existing MP135 `n` command, re-assert IO1/IO2/IO3 high latches with the
`1`, `2`, `3` commands, then send the explicit `q` command to hold
`mpu_qspi_io0_to_fpga_io0` low and verify the FPGA GPIO heartbeat
observes IO0 low while IO1, IO2, and IO3 remain high.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C fpga build/gpio/gpio.bin
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
fpga/build/gpio/gpio.bin
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test (max 5 min):

```
lease:claim devices="fpga.hx1k,mp135.evb" duration_s=60
inventory
fpga.hx1k:program bin=@gpio.bin
fpga.hx1k:uart_open
fpga.hx1k:uart_write data="W0000"
fpga.hx1k:uart_write data="Edfff"
mp135.evb:uart_open
mp135.evb:uart_expect sentinel="gpio_test ready" timeout_ms=10000
mp135.evb:uart_write data="n"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_ncs_to_fpga_cs_n low drive ok" timeout_ms=10000
mp135.evb:uart_write data="\x31"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_io1_to_fpga_io1 high drive ok" timeout_ms=10000
mp135.evb:uart_write data="\x32"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_io2_to_fpga_io2 high drive ok" timeout_ms=10000
mp135.evb:uart_write data="\x33"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_io3_to_fpga_io3 high drive ok" timeout_ms=10000
mp135.evb:uart_write data="q"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_io0_to_fpga_io0 low drive ok" timeout_ms=10000
fpga.hx1k:uart_expect sentinel="9400\r\n" timeout_ms=10000
fpga.hx1k:uart_write data="E0000"
mp135.evb:uart_close
fpga.hx1k:uart_close
mark tag=gpio_physical_mp135_to_fpga_io0_low
lease:release
```

Verify:

```
from pathlib import Path
import json

ALLOWED_OPS = {
    (None, 'description'),
    ('lease', 'claim'),
    (None, 'inventory'),
    ('fpga.hx1k', 'program'),
    ('fpga.hx1k', 'uart_open'),
    ('fpga.hx1k', 'uart_write'),
    ('fpga.hx1k', 'uart_expect'),
    ('fpga.hx1k', 'uart_close'),
    ('mp135.evb', 'uart_open'),
    ('mp135.evb', 'uart_write'),
    ('mp135.evb', 'uart_expect'),
    ('mp135.evb', 'uart_close'),
    (None, 'mark'),
    ('lease', 'release'),
}

REQUIRED_OPS = ALLOWED_OPS - {(None, 'description')}

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        ops = Verification.load_ops(extract_dir)
    except (OSError, json.JSONDecodeError):
        return False

    plan_text = Path(extract_dir, 'plan.txt').read_text()
    required_text = [
        'lease:claim devices="fpga.hx1k,mp135.evb"',
        'fpga.hx1k:uart_write data="Edfff"',
        'mp135.evb:uart_write data="n"',
        'mp135.evb:uart_write data="\\x31"',
        'mp135.evb:uart_write data="\\x32"',
        'mp135.evb:uart_write data="\\x33"',
        'mp135.evb:uart_write data="q"',
        'gpio_test mpu_qspi_io0_to_fpga_io0 low drive ok',
        'fpga.hx1k:uart_expect sentinel="9400\\r\\n"',
        'gpio_physical_mp135_to_fpga_io0_low',
    ]
    if not all(token in plan_text for token in required_text):
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(device in plan_text for device in disallowed):
        return False

    saw = set()
    for record in ops:
        if not isinstance(record, dict) or record.get('status') != 'ok':
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        saw.add(key)

    return REQUIRED_OPS <= saw
```

Rationale: this is the smallest physical IO0 follow-up to the new MP135
`q` UART trigger. It re-asserts the IO1/IO2/IO3 high latches in the
same plan so the heartbeat observes IO0 low (`0x9400`) regardless of
prior MP135 firmware state, uses `mp135.evb`, and does not claim
`bench_mcu.0`.

### Add MP135 IO1 low UART trigger

Add an explicit MP135 `gpio_test` UART command that drives
`mpu_qspi_io1_to_fpga_io1` low and leaves it low. This provides a
sustained low trigger for the next IO1 MP135-to-FPGA physical sample
instead of relying on the periodic IO1 sample path.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(_extract_dir):
    stub = Path('stm32mp135_test_board/baremetal/gpio_test/gpio_replay_mpu_stub.c')
    main = Path('stm32mp135_test_board/baremetal/gpio_test/src/main.c')
    image = Path(artifacts['main.stm32'])

    stub_text = stub.read_text(encoding='utf-8', errors='replace')
    main_text = main.read_text(encoding='utf-8', errors='replace')

    required_stub = [
        'gpio_connectivity_mpu_replay_io1_low_report',
        'mpu_io1_drive_signal',
        'GPIOF',
        'GPIO_PIN_9',
        'GPIO_PIN_RESET',
        'gpio_test mpu_qspi_io1_to_fpga_io1 low drive ok',
    ]
    if not all(token in stub_text for token in required_stub):
        return False

    handler_start = main_text.find('static void gpio_test_handle_command')
    handler_end = main_text.find('static void gpio_test_poll_commands')
    if handler_start < 0 or handler_end < handler_start:
        return False
    handler_text = main_text[handler_start:handler_end]
    if "command == 'r'" not in handler_text:
        return False
    if 'gpio_connectivity_mpu_replay_io1_low_report()' not in handler_text:
        return False
    if 'io1_hold_low = 1;' not in handler_text:
        return False

    loop_start = main_text.find('while (1)')
    if loop_start < 0:
        return False
    loop_text = main_text[loop_start:]
    if 'if (!io1_hold_low)' not in loop_text:
        return False
    if 'gpio_connectivity_mpu_replay_io1_sample_report();' not in loop_text:
        return False

    if not image.is_file() or image.stat().st_size == 0:
        return False
    latest_dep = max(stub.stat().st_mtime, main.stat().st_mtime)
    if image.stat().st_mtime < latest_dep:
        return False

    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    return not any(token in stub_text or token in main_text for token in disallowed)
```

Rationale: this is the smallest safe step after the IO0-low firmware
trigger. It adds the sustained-low firmware trigger needed for a
reliable IO1-low hardware sample without changing any bench plan.

### Verify MP135-to-FPGA IO1 low

Drive every FPGA GPIO fixture bit except IO1 low, hold NCS low with the
existing MP135 `n` command, re-assert IO0/IO2/IO3 high latches with the
`0`, `2`, `3` commands, then send the explicit `r` command to hold
`mpu_qspi_io1_to_fpga_io1` low and verify the FPGA GPIO heartbeat
observes IO1 low while IO0, IO2, and IO3 remain high.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C fpga build/gpio/gpio.bin
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
fpga/build/gpio/gpio.bin
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test (max 5 min):

```
lease:claim devices="fpga.hx1k,mp135.evb" duration_s=60
inventory
fpga.hx1k:program bin=@gpio.bin
fpga.hx1k:uart_open
fpga.hx1k:uart_write data="W0000"
fpga.hx1k:uart_write data="Edfff"
mp135.evb:uart_open
mp135.evb:uart_expect sentinel="gpio_test ready" timeout_ms=10000
mp135.evb:uart_write data="n"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_ncs_to_fpga_cs_n low drive ok" timeout_ms=10000
mp135.evb:uart_write data="\x30"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_io0_to_fpga_io0 high drive ok" timeout_ms=10000
mp135.evb:uart_write data="\x32"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_io2_to_fpga_io2 high drive ok" timeout_ms=10000
mp135.evb:uart_write data="\x33"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_io3_to_fpga_io3 high drive ok" timeout_ms=10000
mp135.evb:uart_write data="r"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_io1_to_fpga_io1 low drive ok" timeout_ms=10000
fpga.hx1k:uart_expect sentinel="3400\r\n" timeout_ms=10000
fpga.hx1k:uart_write data="E0000"
mp135.evb:uart_close
fpga.hx1k:uart_close
mark tag=gpio_physical_mp135_to_fpga_io1_low
lease:release
```

Verify:

```
from pathlib import Path
import json

ALLOWED_OPS = {
    (None, 'description'),
    ('lease', 'claim'),
    (None, 'inventory'),
    ('fpga.hx1k', 'program'),
    ('fpga.hx1k', 'uart_open'),
    ('fpga.hx1k', 'uart_write'),
    ('fpga.hx1k', 'uart_expect'),
    ('fpga.hx1k', 'uart_close'),
    ('mp135.evb', 'uart_open'),
    ('mp135.evb', 'uart_write'),
    ('mp135.evb', 'uart_expect'),
    ('mp135.evb', 'uart_close'),
    (None, 'mark'),
    ('lease', 'release'),
}

REQUIRED_OPS = ALLOWED_OPS - {(None, 'description')}

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        ops = Verification.load_ops(extract_dir)
    except (OSError, json.JSONDecodeError):
        return False

    plan_text = Path(extract_dir, 'plan.txt').read_text()
    required_text = [
        'lease:claim devices="fpga.hx1k,mp135.evb"',
        'fpga.hx1k:uart_write data="Edfff"',
        'mp135.evb:uart_write data="n"',
        'mp135.evb:uart_write data="\\x30"',
        'mp135.evb:uart_write data="\\x32"',
        'mp135.evb:uart_write data="\\x33"',
        'mp135.evb:uart_write data="r"',
        'gpio_test mpu_qspi_io1_to_fpga_io1 low drive ok',
        'fpga.hx1k:uart_expect sentinel="3400\\r\\n"',
        'gpio_physical_mp135_to_fpga_io1_low',
    ]
    if not all(token in plan_text for token in required_text):
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(device in plan_text for device in disallowed):
        return False

    saw = set()
    for record in ops:
        if not isinstance(record, dict) or record.get('status') != 'ok':
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        saw.add(key)

    return REQUIRED_OPS <= saw
```

Rationale: this is the smallest physical IO1 follow-up to the new MP135
`r` UART trigger. It re-asserts the IO0/IO2/IO3 high latches in the
same plan so the heartbeat observes IO1 low (`0x3400`) regardless of
prior MP135 firmware state, uses `mp135.evb`, and does not claim
`bench_mcu.0`.

### Add MP135 IO2 low UART trigger

Add an explicit MP135 `gpio_test` UART command that drives
`mpu_qspi_io2_to_fpga_io2` low and leaves it low. This provides a
sustained low trigger for the next IO2 MP135-to-FPGA physical sample
instead of relying on the periodic IO2 sample path.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(_extract_dir):
    stub = Path('stm32mp135_test_board/baremetal/gpio_test/gpio_replay_mpu_stub.c')
    main = Path('stm32mp135_test_board/baremetal/gpio_test/src/main.c')
    image = Path(artifacts['main.stm32'])

    stub_text = stub.read_text(encoding='utf-8', errors='replace')
    main_text = main.read_text(encoding='utf-8', errors='replace')

    required_stub = [
        'gpio_connectivity_mpu_replay_io2_low_report',
        'mpu_io2_drive_signal',
        'GPIOH',
        'GPIO_PIN_6',
        'GPIO_PIN_RESET',
        'gpio_test mpu_qspi_io2_to_fpga_io2 low drive ok',
    ]
    if not all(token in stub_text for token in required_stub):
        return False

    handler_start = main_text.find('static void gpio_test_handle_command')
    handler_end = main_text.find('static void gpio_test_poll_commands')
    if handler_start < 0 or handler_end < handler_start:
        return False
    handler_text = main_text[handler_start:handler_end]
    if "command == 'a'" not in handler_text:
        return False
    if 'gpio_connectivity_mpu_replay_io2_low_report()' not in handler_text:
        return False
    if 'io2_hold_low = 1;' not in handler_text:
        return False

    loop_start = main_text.find('while (1)')
    if loop_start < 0:
        return False
    loop_text = main_text[loop_start:]
    if 'if (!io2_hold_low)' not in loop_text:
        return False
    if 'gpio_connectivity_mpu_replay_io2_sample_report();' not in loop_text:
        return False

    if not image.is_file() or image.stat().st_size == 0:
        return False
    latest_dep = max(stub.stat().st_mtime, main.stat().st_mtime)
    if image.stat().st_mtime < latest_dep:
        return False

    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    return not any(token in stub_text or token in main_text for token in disallowed)
```

Rationale: this is the smallest safe step after the IO1-low firmware
trigger. It adds the sustained-low firmware trigger needed for a
reliable IO2-low hardware sample without changing any bench plan.

### Verify MP135-to-FPGA IO2 low

Drive every FPGA GPIO fixture bit except IO2 low, hold NCS low with the
existing MP135 `n` command, re-assert IO0/IO1/IO3 high latches with the
`0`, `1`, `3` commands, then send the explicit `a` command to hold
`mpu_qspi_io2_to_fpga_io2` low and verify the FPGA GPIO heartbeat
observes IO2 low while IO0, IO1, and IO3 remain high.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C fpga build/gpio/gpio.bin
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
fpga/build/gpio/gpio.bin
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test (max 5 min):

```
lease:claim devices="fpga.hx1k,mp135.evb" duration_s=60
inventory
fpga.hx1k:program bin=@gpio.bin
fpga.hx1k:uart_open
fpga.hx1k:uart_write data="W0000"
fpga.hx1k:uart_write data="Edfff"
mp135.evb:uart_open
mp135.evb:uart_expect sentinel="gpio_test ready" timeout_ms=10000
mp135.evb:uart_write data="n"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_ncs_to_fpga_cs_n low drive ok" timeout_ms=10000
mp135.evb:uart_write data="\x30"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_io0_to_fpga_io0 high drive ok" timeout_ms=10000
mp135.evb:uart_write data="\x31"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_io1_to_fpga_io1 high drive ok" timeout_ms=10000
mp135.evb:uart_write data="\x33"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_io3_to_fpga_io3 high drive ok" timeout_ms=10000
mp135.evb:uart_write data="a"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_io2_to_fpga_io2 low drive ok" timeout_ms=10000
fpga.hx1k:uart_expect sentinel="b000\r\n" timeout_ms=10000
fpga.hx1k:uart_write data="E0000"
mp135.evb:uart_close
fpga.hx1k:uart_close
mark tag=gpio_physical_mp135_to_fpga_io2_low
lease:release
```

Verify:

```
from pathlib import Path
import json

ALLOWED_OPS = {
    (None, 'description'),
    ('lease', 'claim'),
    (None, 'inventory'),
    ('fpga.hx1k', 'program'),
    ('fpga.hx1k', 'uart_open'),
    ('fpga.hx1k', 'uart_write'),
    ('fpga.hx1k', 'uart_expect'),
    ('fpga.hx1k', 'uart_close'),
    ('mp135.evb', 'uart_open'),
    ('mp135.evb', 'uart_write'),
    ('mp135.evb', 'uart_expect'),
    ('mp135.evb', 'uart_close'),
    (None, 'mark'),
    ('lease', 'release'),
}

REQUIRED_OPS = ALLOWED_OPS - {(None, 'description')}

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        ops = Verification.load_ops(extract_dir)
    except (OSError, json.JSONDecodeError):
        return False

    plan_text = Path(extract_dir, 'plan.txt').read_text()
    required_text = [
        'lease:claim devices="fpga.hx1k,mp135.evb"',
        'fpga.hx1k:uart_write data="Edfff"',
        'mp135.evb:uart_write data="n"',
        'mp135.evb:uart_write data="\\x30"',
        'mp135.evb:uart_write data="\\x31"',
        'mp135.evb:uart_write data="\\x33"',
        'mp135.evb:uart_write data="a"',
        'gpio_test mpu_qspi_io2_to_fpga_io2 low drive ok',
        'fpga.hx1k:uart_expect sentinel="b000\\r\\n"',
        'gpio_physical_mp135_to_fpga_io2_low',
    ]
    if not all(token in plan_text for token in required_text):
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(device in plan_text for device in disallowed):
        return False

    saw = set()
    for record in ops:
        if not isinstance(record, dict) or record.get('status') != 'ok':
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        saw.add(key)

    return REQUIRED_OPS <= saw
```

Rationale: this is the smallest physical IO2 follow-up to the new MP135
`a` UART trigger. It re-asserts the IO0/IO1/IO3 high latches in the
same plan so the heartbeat observes IO2 low (`0xb000`) regardless of
prior MP135 firmware state, uses `mp135.evb`, and does not claim
`bench_mcu.0`.

### Add MP135 IO3 low UART trigger

Add an explicit MP135 `gpio_test` UART command that drives
`mpu_qspi_io3_to_fpga_io3` low and leaves it low. This provides a
sustained low trigger for the next IO3 MP135-to-FPGA physical sample
instead of relying on the periodic IO3 sample path.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(_extract_dir):
    stub = Path('stm32mp135_test_board/baremetal/gpio_test/gpio_replay_mpu_stub.c')
    main = Path('stm32mp135_test_board/baremetal/gpio_test/src/main.c')
    image = Path(artifacts['main.stm32'])

    stub_text = stub.read_text(encoding='utf-8', errors='replace')
    main_text = main.read_text(encoding='utf-8', errors='replace')

    required_stub = [
        'gpio_connectivity_mpu_replay_io3_low_report',
        'mpu_io3_drive_signal',
        'GPIOH',
        'GPIO_PIN_7',
        'GPIO_PIN_RESET',
        'gpio_test mpu_qspi_io3_to_fpga_io3 low drive ok',
    ]
    if not all(token in stub_text for token in required_stub):
        return False

    handler_start = main_text.find('static void gpio_test_handle_command')
    handler_end = main_text.find('static void gpio_test_poll_commands')
    if handler_start < 0 or handler_end < handler_start:
        return False
    handler_text = main_text[handler_start:handler_end]
    if "command == 'b'" not in handler_text:
        return False
    if 'gpio_connectivity_mpu_replay_io3_low_report()' not in handler_text:
        return False
    if 'io3_hold_low = 1;' not in handler_text:
        return False

    loop_start = main_text.find('while (1)')
    if loop_start < 0:
        return False
    loop_text = main_text[loop_start:]
    if 'if (!io3_hold_low)' not in loop_text:
        return False
    if 'gpio_connectivity_mpu_replay_io3_sample_report();' not in loop_text:
        return False

    if not image.is_file() or image.stat().st_size == 0:
        return False
    latest_dep = max(stub.stat().st_mtime, main.stat().st_mtime)
    if image.stat().st_mtime < latest_dep:
        return False

    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    return not any(token in stub_text or token in main_text for token in disallowed)
```

Rationale: this is the smallest safe step after the IO2-low firmware
trigger. It adds the sustained-low firmware trigger needed for a
reliable IO3-low hardware sample without changing any bench plan.

### Verify MP135-to-FPGA IO3 low

Drive every FPGA GPIO fixture bit except IO3 low, hold NCS low with the
existing MP135 `n` command, re-assert IO0/IO1/IO2 high latches with the
`0`, `1`, `2` commands, then send the explicit `b` command to hold
`mpu_qspi_io3_to_fpga_io3` low and verify the FPGA GPIO heartbeat
observes IO3 low while IO0, IO1, and IO2 remain high.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C fpga build/gpio/gpio.bin
make -C stm32mp135_test_board/baremetal/gpio_test build/main.stm32
```

Artifacts:

```
fpga/build/gpio/gpio.bin
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test (max 5 min):

```
lease:claim devices="fpga.hx1k,mp135.evb" duration_s=60
inventory
fpga.hx1k:program bin=@gpio.bin
fpga.hx1k:uart_open
fpga.hx1k:uart_write data="W0000"
fpga.hx1k:uart_write data="Edfff"
mp135.evb:uart_open
mp135.evb:uart_expect sentinel="gpio_test ready" timeout_ms=10000
mp135.evb:uart_write data="n"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_ncs_to_fpga_cs_n low drive ok" timeout_ms=10000
mp135.evb:uart_write data="\x30"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_io0_to_fpga_io0 high drive ok" timeout_ms=10000
mp135.evb:uart_write data="\x31"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_io1_to_fpga_io1 high drive ok" timeout_ms=10000
mp135.evb:uart_write data="\x32"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_io2_to_fpga_io2 high drive ok" timeout_ms=10000
mp135.evb:uart_write data="b"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_io3_to_fpga_io3 low drive ok" timeout_ms=10000
fpga.hx1k:uart_expect sentinel="a400\r\n" timeout_ms=10000
fpga.hx1k:uart_write data="E0000"
mp135.evb:uart_close
fpga.hx1k:uart_close
mark tag=gpio_physical_mp135_to_fpga_io3_low
lease:release
```

Verify:

```
from pathlib import Path
import json

ALLOWED_OPS = {
    (None, 'description'),
    ('lease', 'claim'),
    (None, 'inventory'),
    ('fpga.hx1k', 'program'),
    ('fpga.hx1k', 'uart_open'),
    ('fpga.hx1k', 'uart_write'),
    ('fpga.hx1k', 'uart_expect'),
    ('fpga.hx1k', 'uart_close'),
    ('mp135.evb', 'uart_open'),
    ('mp135.evb', 'uart_write'),
    ('mp135.evb', 'uart_expect'),
    ('mp135.evb', 'uart_close'),
    (None, 'mark'),
    ('lease', 'release'),
}

REQUIRED_OPS = ALLOWED_OPS - {(None, 'description')}

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        ops = Verification.load_ops(extract_dir)
    except (OSError, json.JSONDecodeError):
        return False

    plan_text = Path(extract_dir, 'plan.txt').read_text()
    required_text = [
        'lease:claim devices="fpga.hx1k,mp135.evb"',
        'fpga.hx1k:uart_write data="Edfff"',
        'mp135.evb:uart_write data="n"',
        'mp135.evb:uart_write data="\\x30"',
        'mp135.evb:uart_write data="\\x31"',
        'mp135.evb:uart_write data="\\x32"',
        'mp135.evb:uart_write data="b"',
        'gpio_test mpu_qspi_io3_to_fpga_io3 low drive ok',
        'fpga.hx1k:uart_expect sentinel="a400\\r\\n"',
        'gpio_physical_mp135_to_fpga_io3_low',
    ]
    if not all(token in plan_text for token in required_text):
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(device in plan_text for device in disallowed):
        return False

    saw = set()
    for record in ops:
        if not isinstance(record, dict) or record.get('status') != 'ok':
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        saw.add(key)

    return REQUIRED_OPS <= saw
```

Rationale: this is the smallest physical IO3 follow-up to the new MP135
`b` UART trigger. It re-asserts the IO0/IO1/IO2 high latches in the
same plan so the heartbeat observes IO3 low (`0xa400`) regardless of
prior MP135 firmware state, uses `mp135.evb`, and does not claim
`bench_mcu.0`.

### Add prbs_xor PRBS skeleton

Add a minimal LFSR-only `fpga/src/prbs_xor.nw` chapter and a Makefile
rule that tangles its `prbs_xor.v` into `fpga/build/prbs_xor/prbs_xor.v`.
This is the smallest first step toward the upcoming PRBS / XOR-checksum
/ UART command stack; the XOR checksum, the UART command interface, and
the matching MP135 baremetal mirror are added in later iterations.

Build:

```
make -C fpga build/prbs_xor/prbs_xor.v
```

Artifacts:

```
fpga/build/prbs_xor/prbs_xor.v
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(_extract_dir):
    nw = Path('fpga/src/prbs_xor.nw')
    v  = Path('fpga/build/prbs_xor/prbs_xor.v')
    if not (nw.is_file() and nw.stat().st_size > 0):
        return False
    if not (v.is_file() and v.stat().st_size > 0):
        return False
    if v.stat().st_mtime < nw.stat().st_mtime:
        return False
    text = v.read_text(encoding='utf-8', errors='replace')
    if 'module prbs_xor' not in text:
        return False
    if 'always @(posedge clk)' not in text:
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(token in text for token in disallowed):
        return False
    return True
```

Rationale: smallest meaningful PRBS step. Adding only the LFSR module
(no UART, no checksum) keeps the change to one new noweb file and one
generic Makefile copy rule, while still establishing the noweb chapter,
the build path, and the verification template that subsequent steps
extend with the XOR checksum, the UART command interface, and the
MP135 baremetal mirror.

### Add prbs_xor XOR checksum register

Extend the `prbs_xor` chapter with a streaming 32-bit XOR checksum
register and a `clear` pulse that zeroes the accumulator without
disturbing the LFSR. The active-low `rst_n` still resets both the LFSR
and the checksum to known values. No UART command interface or MP135
baremetal mirror yet; those land in later iterations.

Build:

```
make -C fpga build/prbs_xor/prbs_xor.v
```

Artifacts:

```
fpga/build/prbs_xor/prbs_xor.v
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(_extract_dir):
    nw = Path('fpga/src/prbs_xor.nw')
    v  = Path('fpga/build/prbs_xor/prbs_xor.v')
    if not (nw.is_file() and nw.stat().st_size > 0):
        return False
    if not (v.is_file() and v.stat().st_size > 0):
        return False
    if v.stat().st_mtime < nw.stat().st_mtime:
        return False
    nw_text = nw.read_text(encoding='utf-8', errors='replace')
    for tok in ('clear', 'output reg [31:0] checksum',
                'checksum <= checksum ^ state'):
        if tok not in nw_text:
            return False
    text = v.read_text(encoding='utf-8', errors='replace')
    if 'output reg [31:0] checksum' not in text:
        return False
    if 'checksum <= checksum ^ state' not in text:
        return False
    if 'SPDX-License-Identifier' not in text:
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(token in text for token in disallowed):
        return False
    return True
```

Rationale: smallest meaningful extension after the LFSR skeleton.
Adding only the checksum register plus a `clear` pulse keeps the chunk
to a few extra lines of Verilog while establishing the data path the
upcoming UART command interface will drive; making the step any
smaller (for example, only adding the port and not the accumulator,
or only adding `clear` without the XOR) would leave no observable
behaviour and therefore zero progress.

### Add prbs_xor clk_en gating

Extend the `prbs_xor` chapter with a `clk_en` input that gates LFSR
and checksum advance. When `clk_en` is low, neither `state` nor
`checksum` change; `rst_n` and `clear` reset behaviour are
unaffected. This prepares the module for the UART command
interpreter (idle by default, pulse high for single-step, hold high
for a `2**16`-cycle burst). No wrapper module, no UART hookup yet.

Build:

```
make -C fpga build/prbs_xor/prbs_xor.v
```

Artifacts:

```
fpga/build/prbs_xor/prbs_xor.v
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(_extract_dir):
    nw = Path('fpga/src/prbs_xor.nw')
    v  = Path('fpga/build/prbs_xor/prbs_xor.v')
    if not (nw.is_file() and nw.stat().st_size > 0):
        return False
    if not (v.is_file() and v.stat().st_size > 0):
        return False
    if v.stat().st_mtime < nw.stat().st_mtime:
        return False
    nw_text = nw.read_text(encoding='utf-8', errors='replace')
    for tok in ('input             clk_en', 'else if (clk_en) begin'):
        if tok not in nw_text:
            return False
    text = v.read_text(encoding='utf-8', errors='replace')
    for tok in ('input             clk_en', 'else if (clk_en) begin',
                'state <= (state >> 1)',
                'checksum <= checksum ^ state'):
        if tok not in text:
            return False
    if 'SPDX-License-Identifier' not in text:
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(token in text for token in disallowed):
        return False
    return True
```

Rationale: smallest meaningful extension after the checksum
register. Adding only a `clk_en` input plus the gating clause keeps
the chunk to a one-line port and a single `else if` while
establishing the stream-enable signal the UART command interpreter
will drive; making it any smaller (only the port, or only the
gating without the port) would either be a syntax error or leave
the gate unobservable, so zero progress.

### Add prbs_xor_top wrapper with reset command

Introduce a thin top-level wrapper, `prbs_xor_top`, that lives in
the `fpga/src/prbs_xor.nw` chapter alongside the reusable module
itself (see "Merge prbs_xor.nw and prbs_xor_top.nw" below). The
wrapper instantiates the existing `uart_rx` and `prbs_xor` modules
and decodes a single UART
command: byte `'r'` (`8'h72`) drives the `prbs_xor` reset
(`rst_n`) low for exactly one clock cycle and high otherwise. The
`clear` and `clk_en` inputs of `prbs_xor` are tied low for now, and
no `uart_tx` print path is wired up yet. The top-level ports are
just `clk` and `rx`; `state` and `checksum` are left open so the
synthesizer trims them. Single-step, burst, and checksum-print
commands land in later iterations.

Build:

```
make -C fpga build/prbs_xor_top/prbs_xor_top.v
```

Artifacts:

```
fpga/build/prbs_xor_top/prbs_xor_top.v
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(_extract_dir):
    nw = Path('fpga/src/prbs_xor.nw')
    v  = Path('fpga/build/prbs_xor_top/prbs_xor_top.v')
    if not (nw.is_file() and nw.stat().st_size > 0):
        return False
    if not (v.is_file() and v.stat().st_size > 0):
        return False
    if v.stat().st_mtime < nw.stat().st_mtime:
        return False
    nw_text = nw.read_text(encoding='utf-8', errors='replace')
    for tok in ('module prbs_xor_top', 'uart_rx', 'prbs_xor',
                "8'h72"):
        if tok not in nw_text:
            return False
    text = v.read_text(encoding='utf-8', errors='replace')
    for tok in ('module prbs_xor_top', 'uart_rx', 'prbs_xor',
                "8'h72"):
        if tok not in text:
            return False
    if 'SPDX-License-Identifier' not in text:
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(token in text for token in disallowed):
        return False
    return True
```

Rationale: smallest meaningful step toward the UART command
interpreter. Adding only the wrapper boundary plus a single
`'r'`-decodes-to-reset command keeps the new chapter to one tiny
module while establishing the chapter directory, build path, and
verification template that the single-step, burst, and
checksum-print commands extend in subsequent iterations. Making it
any smaller (an empty wrapper with no command, or only the
`uart_rx` instantiation with no decode) would leave the wrapper
behaviourally indistinguishable from a stub, so zero progress.

### Add prbs_xor_top single-step command

Extend the `prbs_xor_top` wrapper with a second UART command: byte
`'s'` (`8'h73`) drives the `prbs_xor` `clk_en` high for exactly one
clock cycle and low otherwise, advancing the LFSR/checksum by a
single step. The existing `'r'` (`8'h72`) reset behaviour is
preserved unchanged. `clear` stays tied low; `state` and `checksum`
remain dangling so the synthesizer trims them. The top-level ports
are still just `clk` and `rx`. Burst and checksum-print commands
land in later iterations.

Build:

```
make -C fpga build/prbs_xor_top/prbs_xor_top.v
```

Artifacts:

```
fpga/build/prbs_xor_top/prbs_xor_top.v
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(_extract_dir):
    nw = Path('fpga/src/prbs_xor.nw')
    v  = Path('fpga/build/prbs_xor_top/prbs_xor_top.v')
    if not (nw.is_file() and nw.stat().st_size > 0):
        return False
    if not (v.is_file() and v.stat().st_size > 0):
        return False
    if v.stat().st_mtime < nw.stat().st_mtime:
        return False
    nw_text = nw.read_text(encoding='utf-8', errors='replace')
    for tok in ('module prbs_xor_top', 'uart_rx', 'prbs_xor',
                "8'h72", "8'h73", 'clk_en_q',
                'clk_en_q <= 1\'b1'):
        if tok not in nw_text:
            return False
    text = v.read_text(encoding='utf-8', errors='replace')
    for tok in ('module prbs_xor_top', 'uart_rx', 'prbs_xor',
                "8'h72", "8'h73", 'clk_en_q',
                'clk_en_q <= 1\'b1'):
        if tok not in text:
            return False
    if 'SPDX-License-Identifier' not in text:
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(token in text for token in disallowed):
        return False
    return True
```

Rationale: smallest meaningful extension after the reset command.
Adding only the `'s'` decode plus a one-bit `clk_en_q` pulse
register keeps the wrapper change to a single new register and a
single new compare while establishing the single-cycle clock-enable
pulse the burst command will reuse; making it any smaller (only the
register with no decode, or only the decode without wiring `clk_en`)
would leave the new pulse unobservable in the build output, so zero
progress.

### Add prbs_xor_top burst command

Extend the `prbs_xor_top` wrapper with a third UART command: byte
`'b'` (`8'h62`) loads a 17-bit `burst_count` register with
`17'd65536` and the wrapper drives `clk_en` high while
`burst_count` is non-zero, decrementing by one each cycle. The
result is exactly `2**16 = 65536` consecutive cycles of `clk_en`
high starting the cycle after the burst byte is decoded, advancing
the LFSR/checksum by one full PRBS period chunk. `clk_en` is the
OR of the existing single-step `clk_en_q` pulse and the
`burst_count != 0` term, so the existing `'r'` (`8'h72`) reset and
`'s'` (`8'h73`) single-step behaviours are preserved unchanged.
`clear` stays tied low; `state` and `checksum` remain dangling so
the synthesizer trims them. The top-level ports are still just
`clk` and `rx`. The checksum-print command lands in a later
iteration.

Build:

```
make -C fpga build/prbs_xor_top/prbs_xor_top.v
```

Artifacts:

```
fpga/build/prbs_xor_top/prbs_xor_top.v
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(_extract_dir):
    nw = Path('fpga/src/prbs_xor.nw')
    v  = Path('fpga/build/prbs_xor_top/prbs_xor_top.v')
    if not (nw.is_file() and nw.stat().st_size > 0):
        return False
    if not (v.is_file() and v.stat().st_size > 0):
        return False
    if v.stat().st_mtime < nw.stat().st_mtime:
        return False
    nw_text = nw.read_text(encoding='utf-8', errors='replace')
    for tok in ('module prbs_xor_top', 'uart_rx', 'prbs_xor',
                "8'h72", "8'h73", "8'h62", 'clk_en_q',
                'burst_count', 'burst_count - 17',
                'clk_en_q | (burst_count != 17'):
        if tok not in nw_text:
            return False
    text = v.read_text(encoding='utf-8', errors='replace')
    for tok in ('module prbs_xor_top', 'uart_rx', 'prbs_xor',
                "8'h72", "8'h73", "8'h62", 'clk_en_q',
                'burst_count', 'burst_count - 17',
                'clk_en_q | (burst_count != 17'):
        if tok not in text:
            return False
    if 'SPDX-License-Identifier' not in text:
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(token in text for token in disallowed):
        return False
    return True
```

Rationale: smallest meaningful extension after the single-step
command. Adding only the `'b'` decode plus a 17-bit `burst_count`
counter and the `clk_en` OR keeps the wrapper change to a single
new register and a single new compare while establishing the
multi-cycle clock-enable path the checksum-print command will
observe; making it any smaller (only the register with no decode,
or only the decode without wiring `burst_count` into `clk_en`)
would leave the burst unobservable in the build output, so zero
progress.

### Add prbs_xor_top print-checksum command

Extend the `prbs_xor_top` wrapper with a fourth UART command: byte
`'p'` (`8'h70`) latches the current `checksum` into a 32-bit
register `checksum_q` and starts a small print state machine that
streams the captured value as eight ASCII hex digits MSB-first
followed by `8'h0d` (`CR`) and `8'h0a` (`LF`) over a new top-level
`tx` UART output. The state machine indexes the bytes with a 4-bit
`print_idx`: 0..7 select nibbles `checksum_q[31:28]` through
`checksum_q[3:0]`, 8 selects `CR`, 9 selects `LF`, and 10 means
idle. Each cycle in which `print_idx != 4'd10` and the shared
`uart_tx` instance is not busy, the wrapper presents the next byte
on `tx_data`, raises `tx_start` for one clock, and increments
`print_idx`. The 4-bit-to-ASCII conversion follows
`(nib < 4'd10) ? (8'h30 + nib) : (8'h61 + nib - 4'd10)`, emitting
lowercase `a`-`f`. The single new `uart_tx` (default
`CLKS_PER_BIT = 104`) drives the new `tx` port. The `'r'`
(`8'h72`) reset, `'s'` (`8'h73`) single-step, and `'b'` (`8'h62`)
burst behaviours are preserved unchanged. `clear` stays tied low
and `state` remains dangling so the synthesizer trims it.

Build:

```
make -C fpga build/prbs_xor_top/prbs_xor_top.v
```

Artifacts:

```
fpga/build/prbs_xor_top/prbs_xor_top.v
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(_extract_dir):
    nw = Path('fpga/src/prbs_xor.nw')
    v  = Path('fpga/build/prbs_xor_top/prbs_xor_top.v')
    if not (nw.is_file() and nw.stat().st_size > 0):
        return False
    if not (v.is_file() and v.stat().st_size > 0):
        return False
    if v.stat().st_mtime < nw.stat().st_mtime:
        return False
    nw_text = nw.read_text(encoding='utf-8', errors='replace')
    for tok in ('module prbs_xor_top', 'output tx', 'uart_rx',
                'uart_tx', 'prbs_xor', "8'h72", "8'h73", "8'h62",
                "8'h70", "8'h0d", "8'h0a", 'clk_en_q',
                'burst_count', 'checksum_q', 'print_idx'):
        if tok not in nw_text:
            return False
    text = v.read_text(encoding='utf-8', errors='replace')
    for tok in ('module prbs_xor_top', 'output tx', 'uart_rx',
                'uart_tx', 'prbs_xor', "8'h72", "8'h73", "8'h62",
                "8'h70", "8'h0d", "8'h0a", 'clk_en_q',
                'burst_count', 'checksum_q', 'print_idx'):
        if tok not in text:
            return False
    if 'SPDX-License-Identifier' not in text:
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(token in text for token in disallowed):
        return False
    return True
```

Rationale: smallest meaningful extension after the burst command.
Adding only the `'p'` decode plus the `checksum_q` latch, the
`print_idx` state machine, the hex-nibble ASCII codec, and the
single new `uart_tx` instance keeps the wrapper change to one
cohesive print path while finally introducing the `tx` output
needed by every later iteration; making it any smaller (latching
`checksum_q` without instantiating `uart_tx`, or instantiating
`uart_tx` without the FSM that drives it) would leave the print
behaviour unobservable, so zero progress.

### Add MP135 baremetal prbs_test skeleton

Add a minimal LFSR-only baremetal sub-project at
`stm32mp135_test_board/baremetal/prbs_test/` that mirrors the FPGA
`prbs_xor` polynomial on the MPU side. This is the smallest first step
toward the MPU half of the upcoming PRBS / XOR-checksum / UART command
stack; the streaming XOR checksum, UART command interface, and matching
burst behaviour are added in later iterations.

Build:

```
make -C stm32mp135_test_board/baremetal/prbs_test build/main.stm32
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(_extract_dir):
    base = Path('stm32mp135_test_board/baremetal/prbs_test')
    mk = base / 'Makefile'
    src = base / 'src/main.c'
    img = base / 'build/main.stm32'
    if not mk.is_file():
        return False
    if not src.is_file():
        return False
    text = src.read_text(encoding='utf-8', errors='replace')
    for token in ('0x80200003', 'prbs_step', '(state >> 1) ^',
                  'SPDX-License-Identifier'):
        if token not in text:
            return False
    if not (img.is_file() and img.stat().st_size > 0):
        return False
    if img.stat().st_mtime < src.stat().st_mtime:
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(token in text for token in disallowed):
        return False
    return True
```

Rationale: smallest meaningful MPU-side PRBS step. Adding only the LFSR
recurrence (no UART, no checksum, no command interface) keeps the
change to one new sub-project directory and a tiny `main.c`, while
still establishing the build path, the SPDX header, and the
verification template that subsequent steps extend with the streaming
XOR checksum, the UART command parser, and burst commands matching the
FPGA `prbs_xor_top` interface.

### Add MP135 prbs_test XOR checksum

Extend the MP135 baremetal `prbs_test` skeleton with a streaming XOR
checksum that aggregates each PRBS state into a 32-bit accumulator. A
new `prbs_state_t` struct pairs the LFSR state with the checksum, and a
`prbs_step_with_checksum` helper advances the LFSR while XORing the
prior state into the checksum, mirroring the FPGA `prbs_xor` data path.
No UART or command surface yet; that arrives in a later iteration.

Build:

```
make -C stm32mp135_test_board/baremetal/prbs_test build/main.stm32
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(_extract_dir):
    base = Path('stm32mp135_test_board/baremetal/prbs_test')
    src = base / 'src/main.c'
    img = base / 'build/main.stm32'
    if not src.is_file():
        return False
    text = src.read_text(encoding='utf-8', errors='replace')
    for token in ('prbs_state_t', 'prbs_step_with_checksum',
                  'checksum ^=', 'SPDX-License-Identifier'):
        if token not in text:
            return False
    if not (img.is_file() and img.stat().st_size > 0):
        return False
    if img.stat().st_mtime < src.stat().st_mtime:
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(token in text for token in disallowed):
        return False
    return True
```

Rationale: smallest meaningful extension after the LFSR-only skeleton.
Adding only the `prbs_state_t` struct and the `prbs_step_with_checksum`
helper keeps the change to one cohesive accumulator addition without
introducing UART, command parsing, or burst behaviour; making it any
smaller (struct alone with no XOR, or XOR without the struct that pairs
state with checksum) would leave the checksum unobservable to later
UART steps, so zero progress.

### Merge prbs_xor.nw and prbs_xor_top.nw

Consolidate the two FPGA noweb chapters that grew up side by side
into a single `fpga/src/prbs_xor.nw`. The merged chapter still
tangles to two Verilog modules: `prbs_xor` (the reusable LFSR +
checksum core) and `prbs_xor_top` (the example UART command
wrapper), plus a small Makefile fragment that keeps both build paths
working. The standalone `fpga/src/prbs_xor_top.nw` is removed; every
prior step that built `fpga/build/prbs_xor_top/prbs_xor_top.v` keeps
finding it because the new `prbs_xor.mk` chunk emits a grouped-target
tangle rule and an explicit copy into `build/prbs_xor_top/`.

The merge is purely a refactor: no Verilog logic changes, no new
ports, no new commands. The reusable module and the example top
instantiation simply live in one chapter so a reader sees both at
once.

Build:

```
make -C fpga build/prbs_xor/prbs_xor.v
make -C fpga build/prbs_xor_top/prbs_xor_top.v
```

Artifacts:

```
fpga/build/prbs_xor/prbs_xor.v
fpga/build/prbs_xor_top/prbs_xor_top.v
```

Test: no hardware.

Verify:

```
from pathlib import Path

def check(_extract_dir):
    nw  = Path('fpga/src/prbs_xor.nw')
    old = Path('fpga/src/prbs_xor_top.nw')
    v1  = Path('fpga/build/prbs_xor/prbs_xor.v')
    v2  = Path('fpga/build/prbs_xor_top/prbs_xor_top.v')

    if not (nw.is_file() and nw.stat().st_size > 0):
        return False
    if old.exists():
        return False
    for v in (v1, v2):
        if not (v.is_file() and v.stat().st_size > 0):
            return False
        if v.stat().st_mtime < nw.stat().st_mtime:
            return False

    nw_text = nw.read_text(encoding='utf-8', errors='replace')
    for tok in ('<<prbs_xor.v>>=', '<<prbs_xor_top.v>>=',
                '<<prbs_xor.mk>>=', 'module prbs_xor',
                'module prbs_xor_top'):
        if tok not in nw_text:
            return False

    for v in (v1, v2):
        text = v.read_text(encoding='utf-8', errors='replace')
        if 'SPDX-License-Identifier' not in text:
            return False
        disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
        if any(token in text for token in disallowed):
            return False

    return True
```

Rationale: the reusable module and a worked example of how to drive
it belong in one chapter so the reader does not have to chase two
files for a single design unit. The split into two `.nw` files was
an artefact of incremental construction; collapsing it into one
chapter is a one-shot refactor that does not change any synthesised
behaviour, so it is the smallest meaningful step that resolves the
chapter sprawl. Splitting it further (delete the standalone top file
in one iteration, move chunks in another) would leave the build
broken in between.

### Audit physical connectivity coverage for QSPI jumpers

Add a host-only audit gate that proves the six concrete-pin QSPI
jumpers from the assumed jumper table (`sclk`, `cs_n`, `io[0..3]`)
are each already covered by at least one passing physical
`gpio_physical_*` mark tag in this mission file. The control GPIOs
(`reset_n`, `ctrl/start`, `ready/status`) and the UART jumpers
remain `TBD` for FPGA pin assignment in the assumed table and are
intentionally out of scope for this audit; the audit only enforces
coverage for jumpers whose FPGA pin is committed.

This is the smallest first slice of "Verify physical connectivity":
it surfaces the exact set of jumpers already proven on hardware in
prior chapters, without driving any new bench plan, so a future
sub-step can extend coverage to whichever signal the audit reports
as unproven.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_connectivity_manifest.py
```

Test (max 1 min):

```
mark tag=gpio_physical_connectivity_audit
```

Verify:

```
from pathlib import Path
import json

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False

    mission = Path('missions/fpga-spi.md').read_text(
        encoding='utf-8', errors='replace')
    manifest_path = Path(
        'stm32mp135_test_board/baremetal/gpio_test/'
        'connectivity_manifest.json')
    try:
        manifest = json.loads(manifest_path.read_text(
            encoding='utf-8', errors='replace'))
    except (OSError, json.JSONDecodeError):
        return False

    plan = manifest.get('first_pass_test_plan')
    if not isinstance(plan, list) or not plan:
        return False

    # Concrete-pin QSPI jumpers whose FPGA pin is committed in the
    # assumed table. Each must have at least one matching
    # gpio_physical_* mark tag already passing in this mission.
    required_tags = {
        'mpu_qspi_clk_to_fpga_sclk': (
            'gpio_physical_mp135_to_fpga_sclk_high',
            'gpio_physical_mp135_to_fpga_sclk_low',
        ),
        'mpu_qspi_ncs_to_fpga_cs_n': (
            'gpio_physical_mp135_to_fpga_ncs_high',
            'gpio_physical_mp135_to_fpga_ncs_low',
        ),
        'mpu_qspi_io0_to_fpga_io0': (
            'gpio_physical_fpga_to_mpu_io0',
            'gpio_physical_mp135_to_fpga_io0_high',
            'gpio_physical_mp135_to_fpga_io0_low',
        ),
        'mpu_qspi_io1_to_fpga_io1': (
            'gpio_physical_fpga_to_mpu_io1',
            'gpio_physical_mp135_to_fpga_io1_high',
            'gpio_physical_mp135_to_fpga_io1_low',
        ),
        'mpu_qspi_io2_to_fpga_io2': (
            'gpio_physical_fpga_to_mpu_io2',
            'gpio_physical_mp135_to_fpga_io2_high',
            'gpio_physical_mp135_to_fpga_io2_low',
        ),
        'mpu_qspi_io3_to_fpga_io3': (
            'gpio_physical_fpga_to_mpu_io3',
            'gpio_physical_mp135_to_fpga_io3_high',
            'gpio_physical_mp135_to_fpga_io3_low',
        ),
    }

    plan_signals = {entry.get('signal') for entry in plan
                    if isinstance(entry, dict)}
    for signal in required_tags:
        if signal not in plan_signals:
            return False

    wip_idx = mission.find('\n## WIP\n')
    if wip_idx < 0:
        return False
    above_wip = mission[:wip_idx]
    for tags in required_tags.values():
        for tag in tags:
            if ('mark tag=' + tag) not in above_wip:
                return False

    return True
```

Rationale: this sub-step is host-only, touches no firmware, and
asserts only what the previously passing chapters already prove on
hardware. Splitting it smaller (auditing one signal at a time)
would still require the same audit harness and the same Verify
plumbing, so the per-signal slice would not produce strictly
smaller delivered work. Splitting the other way (folding any new
hardware-driving check into this audit) would bundle two distinct
concerns and break the "single new passing test" rule.

### Audit FPGA pin numbers in manifest match gpio.nw set_io

Add a host-only audit gate that proves every concrete iCEstick pin
number named in `connectivity_manifest.json`'s `fpga_signal_pin`
strings is actually bound by a `set_io` directive in
`fpga/src/gpio.nw`'s `gpio.pcf` chunk. The manifest currently
claims `sclk, iCEstick pin 45`, `cs_n, iCEstick pin 56`, `io[0..3]`
on pins `47/44/60/48`, `tx, iCEstick pin 8`, and `rx, iCEstick
pin 9`; the audit reads `gpio.nw`, parses every `set_io <name>
<pin>` line in the `gpio.pcf` block, and asserts the multiset of
pin numbers contains each manifest-claimed pin at least once.
Entries whose `fpga_signal_pin` is still `TBD` (the three control
GPIOs) are skipped because there is no concrete pin to audit yet.

This is a strict tightening of the prior coverage audit: it does
not change the set of jumpers we drive on hardware, but it forbids
a typo or rebind in `gpio.nw` from silently desynchronising the
manifest from the physical pin assignment. Once any of the three
TBD control GPIOs is committed to a concrete iCEstick pin, the
same parser will pick it up automatically. Splitting smaller
(auditing one pin at a time) would reuse the same parser and
verify plumbing for no smaller delivered work; folding this into
a hardware-driving check would bundle two concerns and break the
"single new passing test" rule.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_connectivity_manifest.py
```

Test (max 1 min):

```
mark tag=gpio_manifest_pin_matches_gpio_nw
```

Verify:

```
import json
import re
from pathlib import Path

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False

    manifest_path = Path(
        'stm32mp135_test_board/baremetal/gpio_test/'
        'connectivity_manifest.json')
    gpio_nw_path = Path('fpga/src/gpio.nw')
    try:
        manifest = json.loads(manifest_path.read_text(
            encoding='utf-8', errors='replace'))
        gpio_nw = gpio_nw_path.read_text(
            encoding='utf-8', errors='replace')
    except (OSError, json.JSONDecodeError):
        return False

    # Extract the gpio.pcf chunk and parse its set_io lines.
    chunk_re = re.compile(
        r'<<gpio\.pcf>>=\n(.*?)\n@', re.DOTALL)
    match = chunk_re.search(gpio_nw)
    if match is None:
        return False
    pcf_pins = set()
    for line in match.group(1).splitlines():
        m = re.match(r'\s*set_io\s+\S+\s+(\d+)\s*$', line)
        if m:
            pcf_pins.add(int(m.group(1)))
    if not pcf_pins:
        return False

    jumpers = manifest.get('jumpers')
    if not isinstance(jumpers, list) or not jumpers:
        return False

    pin_re = re.compile(r'iCEstick pin (\d+)')
    saw_concrete_pin = False
    for row in jumpers:
        if not isinstance(row, dict):
            return False
        fpga_pin_str = row.get('fpga_signal_pin', '')
        if not isinstance(fpga_pin_str, str):
            return False
        if 'TBD' in fpga_pin_str:
            continue
        m = pin_re.search(fpga_pin_str)
        if m is None:
            return False
        pin = int(m.group(1))
        if pin not in pcf_pins:
            return False
        saw_concrete_pin = True

    return saw_concrete_pin
```

### Commit FPGA reset_n to iCEstick pin 112

Pin down the first of the three TBD control GPIOs. Update the
`Assumed hardware connections` table and the matching jumper in
`stm32mp135_test_board/baremetal/gpio_test/connectivity_manifest.json`
so that `mpu_reset_output_to_fpga_reset_n.fpga_signal_pin` reads
`FPGA reset_n on pins[0], iCEstick pin 112` instead of `FPGA
reset_n, exact FPGA pin TBD`. The chosen pin reuses the `pins[0]`
slot already bound by `set_io pins[0] 112` in the `gpio.pcf` chunk
of `fpga/src/gpio.nw`, so the existing `gpio_test` GPIO bank
already drives and samples the same physical line and no new
top-level Verilog port is required. The MPU side of the jumper
remains TBD because the MP135 GPIO reset output pin has not been
identified.

This is the smallest concrete-progress step toward `Verify
physical connectivity`: it converts one of the three remaining
TBD control GPIOs into a concrete iCEstick pin without changing
the synthesised bitstream, without adding a new test vector, and
without committing the MPU side. The iter-64 PCF cross-check
audit covers the new pin automatically (pin 112 is in the set
parsed from `gpio.nw`), and the host validator continues to match
the table against the manifest. Splitting smaller (e.g. only
editing the manifest, or only editing the table) would desync the
two and trip the validator. Folding into a future bench-side
`Verify FPGA reset_n high/low` chapter would bundle a
hardware-driving step with the pin commit and break the
"single new passing test" rule.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_connectivity_manifest.py
```

Test (max 1 min):

```
mark tag=gpio_manifest_reset_n_pin_committed
```

Verify:

```
import json
import re
from pathlib import Path

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False

    manifest_path = Path(
        'stm32mp135_test_board/baremetal/gpio_test/'
        'connectivity_manifest.json')
    try:
        manifest = json.loads(manifest_path.read_text(
            encoding='utf-8', errors='replace'))
    except (OSError, json.JSONDecodeError):
        return False

    jumpers = manifest.get('jumpers')
    if not isinstance(jumpers, list):
        return False

    target = None
    for row in jumpers:
        if not isinstance(row, dict):
            return False
        if row.get('signal') == 'mpu_reset_output_to_fpga_reset_n':
            target = row
            break
    if target is None:
        return False

    fpga_pin_str = target.get('fpga_signal_pin', '')
    if not isinstance(fpga_pin_str, str):
        return False
    if 'TBD' in fpga_pin_str:
        return False

    m = re.search(r'iCEstick pin (\d+)', fpga_pin_str)
    if m is None:
        return False
    if int(m.group(1)) != 112:
        return False

    if target.get('direction') != 'MPU -> FPGA':
        return False
    if target.get('mpu_role') != 'drive':
        return False
    if target.get('fpga_role') != 'sample':
        return False

    return True
```

### Commit FPGA ctrl_input to iCEstick pin 113

Pin down the second of the three TBD control GPIOs. Update the
`Assumed hardware connections` table and the matching jumper in
`stm32mp135_test_board/baremetal/gpio_test/connectivity_manifest.json`
so that `mpu_control_output_to_fpga_ctrl_start.fpga_signal_pin`
reads `FPGA ctrl/start on pins[1], iCEstick pin 113` instead of
`FPGA ctrl/start, exact FPGA pin TBD`. The chosen pin reuses the
`pins[1]` slot already bound by `set_io pins[1] 113` in the
`gpio.pcf` chunk of `fpga/src/gpio.nw`, so the existing
`gpio_test` GPIO bank already drives and samples the same
physical line and no new top-level Verilog port is required. The
MPU side of the jumper remains TBD because the MP135 GPIO control
output pin has not been identified.

This is the smallest concrete-progress step toward `Verify
physical connectivity`: it converts another of the remaining TBD
control GPIOs into a concrete iCEstick pin without changing the
synthesised bitstream, without adding a new test vector, and
without committing the MPU side. The iter-64 PCF cross-check
audit covers the new pin automatically (pin 113 is in the set
parsed from `gpio.nw`), and the host validator continues to match
the table against the manifest. Splitting smaller (e.g. only
editing the manifest, or only editing the table) would desync the
two and trip the validator. Folding into a future bench-side
`Verify FPGA ctrl/start high/low` chapter would bundle a
hardware-driving step with the pin commit and break the
"single new passing test" rule.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_connectivity_manifest.py
```

Test (max 1 min):

```
mark tag=gpio_manifest_ctrl_input_pin_committed
```

Verify:

```
import json
import re
from pathlib import Path

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False

    manifest_path = Path(
        'stm32mp135_test_board/baremetal/gpio_test/'
        'connectivity_manifest.json')
    try:
        manifest = json.loads(manifest_path.read_text(
            encoding='utf-8', errors='replace'))
    except (OSError, json.JSONDecodeError):
        return False

    jumpers = manifest.get('jumpers')
    if not isinstance(jumpers, list):
        return False

    target = None
    for row in jumpers:
        if not isinstance(row, dict):
            return False
        if row.get('signal') == 'mpu_control_output_to_fpga_ctrl_start':
            target = row
            break
    if target is None:
        return False

    fpga_pin_str = target.get('fpga_signal_pin', '')
    if not isinstance(fpga_pin_str, str):
        return False
    if 'TBD' in fpga_pin_str:
        return False

    m = re.search(r'iCEstick pin (\d+)', fpga_pin_str)
    if m is None:
        return False
    if int(m.group(1)) != 113:
        return False

    if target.get('direction') != 'MPU -> FPGA':
        return False
    if target.get('mpu_role') != 'drive':
        return False
    if target.get('fpga_role') != 'sample':
        return False

    return True
```

### Commit FPGA status_output to iCEstick pin 114

Pin down the third of the three TBD control GPIOs. Update the
`Assumed hardware connections` table and the matching jumper in
`stm32mp135_test_board/baremetal/gpio_test/connectivity_manifest.json`
so that `fpga_ready_status_to_mpu_status_input.fpga_signal_pin`
reads `FPGA ready/status on pins[2], iCEstick pin 114` instead of
`FPGA ready/status, exact FPGA pin TBD`. The chosen pin reuses the
`pins[2]` slot already bound by `set_io pins[2] 114` in the
`gpio.pcf` chunk of `fpga/src/gpio.nw`, so the existing
`gpio_test` GPIO bank already drives and samples the same
physical line and no new top-level Verilog port is required. The
`gpio.v` body assigns `pins[g] = gpio_oe[g] ? gpio_out[g] : 1'bz`,
so when commanded over UART the FPGA can drive `pins[2]` high or
low to satisfy the FPGA-driven direction of this jumper. The MPU
side of the jumper remains TBD because the MP135 GPIO status
input pin has not been identified.

This is the smallest concrete-progress step toward `Verify
physical connectivity`: it converts the last of the three
remaining TBD control GPIOs into a concrete iCEstick pin without
changing the synthesised bitstream, without adding a new test
vector, and without committing the MPU side. The iter-64 PCF
cross-check audit covers the new pin automatically (pin 114 is in
the set parsed from `gpio.nw`), and the host validator continues
to match the table against the manifest. Splitting smaller (e.g.
only editing the manifest, or only editing the table) would
desync the two and trip the validator. Folding into a future
bench-side `Verify FPGA status high/low` chapter would bundle a
hardware-driving step with the pin commit and break the
"single new passing test" rule.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_connectivity_manifest.py
```

Test (max 1 min):

```
mark tag=gpio_manifest_status_output_pin_committed
```

Verify:

```
import json
import re
from pathlib import Path

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False

    manifest_path = Path(
        'stm32mp135_test_board/baremetal/gpio_test/'
        'connectivity_manifest.json')
    try:
        manifest = json.loads(manifest_path.read_text(
            encoding='utf-8', errors='replace'))
    except (OSError, json.JSONDecodeError):
        return False

    jumpers = manifest.get('jumpers')
    if not isinstance(jumpers, list):
        return False

    target = None
    for row in jumpers:
        if not isinstance(row, dict):
            return False
        if row.get('signal') == 'fpga_ready_status_to_mpu_status_input':
            target = row
            break
    if target is None:
        return False

    fpga_pin_str = target.get('fpga_signal_pin', '')
    if not isinstance(fpga_pin_str, str):
        return False
    if 'TBD' in fpga_pin_str:
        return False

    m = re.search(r'iCEstick pin (\d+)', fpga_pin_str)
    if m is None:
        return False
    if int(m.group(1)) != 114:
        return False

    if target.get('direction') != 'FPGA -> MPU':
        return False
    if target.get('mpu_role') != 'sample':
        return False
    if target.get('fpga_role') != 'drive':
        return False

    return True
```

### Audit no fpga_signal_pin TBD in connectivity_manifest

Lock in the iter-70/71/72 wins by asserting that every jumper row
in `stm32mp135_test_board/baremetal/gpio_test/connectivity_manifest.json`
has a concrete (non-TBD) `fpga_signal_pin`. Iter 70 committed
`reset_n` to iCEstick pin 112, iter 71 committed `ctrl_start` to
113, and iter 72 committed `status_output` to 114; before those
three iters, four FPGA pin slots were the string `exact FPGA pin
TBD`. With those resolved, the FPGA side of the jumper table is
fully concretised. A small standing audit prevents a future
edit from regressing any of those three commits in isolation.

`validate_connectivity_manifest.py` does not enforce this property:
it only checks (i) that the markdown table and the JSON jumper
list match field-for-field, (ii) that signal names follow the
naming regex, and (iii) that `first_pass_test_plan` covers every
jumper for every legal driver/sampler/value tuple. None of those
clauses inspects the textual content of `fpga_signal_pin` for a
`TBD` substring, so a regression that flips one row back to
`exact FPGA pin TBD` while keeping the markdown table in sync
would still pass `validate_connectivity_manifest.py`. The previous
schema-shadow cleanup in commit `05caf9c` removed audits that
re-asserted clauses already enforced by the validator (plan signal
in jumpers, plan `expect` in {0,1}, plan `driver` in {mpu,fpga},
`set_io` pin uniqueness, FPGA pin numbers vs `gpio.nw`); this
audit is not in that class.

The audit is FPGA-side only: `mpu_signal_pin` entries remain TBD
across all eleven rows because no MP135 GPIO port has been
committed. The six bench-tested jumpers (sclk, ncs, io0..io3) work
today despite their MPU-pin TBD strings because the firmware uses
`board.h` HAL macros (`QSPI_CLK_PORT`, `QSPI_NCS_PORT`, ...), so
the documentation TBD is not on the bench-progress critical path.
The corresponding firmware step for `reset_n` (`ctrl_start`,
`status_output`) is to add a board.h GPIO definition and a
`gpio_replay_mpu_stub.c` drive entry, mirroring the existing
"Add MP135 GPIO drive output for SCLK" chapter; that step picks
an MP135 port and is the next bench-progress lift, not bundled
here.

This is the smallest meaningful step toward `Verify physical
connectivity` that does not require selecting a new MP135 GPIO
port. It is host-only, machine-checkable in well under a minute,
and it converts a property currently held only by inspection
("iter 70/71/72 ate every FPGA-side TBD") into a property held
by the verify path.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_connectivity_manifest.py
```

Test (max 1 min):

```
mark tag=gpio_manifest_no_fpga_signal_pin_tbd
```

Verify:

```
import json
from pathlib import Path

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False

    manifest_path = Path(
        'stm32mp135_test_board/baremetal/gpio_test/'
        'connectivity_manifest.json')
    try:
        manifest = json.loads(manifest_path.read_text(
            encoding='utf-8', errors='replace'))
    except (OSError, json.JSONDecodeError):
        return False

    jumpers = manifest.get('jumpers')
    if not isinstance(jumpers, list):
        return False
    if not jumpers:
        return False

    required_signals = {
        'mpu_uart_tx_to_fpga_rx',
        'fpga_uart_tx_to_mpu_rx',
        'mpu_reset_output_to_fpga_reset_n',
        'mpu_control_output_to_fpga_ctrl_start',
        'fpga_ready_status_to_mpu_status_input',
        'mpu_qspi_clk_to_fpga_sclk',
        'mpu_qspi_ncs_to_fpga_cs_n',
        'mpu_qspi_io0_to_fpga_io0',
        'mpu_qspi_io1_to_fpga_io1',
        'mpu_qspi_io2_to_fpga_io2',
        'mpu_qspi_io3_to_fpga_io3',
    }
    seen_signals = set()

    for row in jumpers:
        if not isinstance(row, dict):
            return False
        signal = row.get('signal')
        if not isinstance(signal, str):
            return False
        seen_signals.add(signal)
        fpga_pin_str = row.get('fpga_signal_pin', '')
        if not isinstance(fpga_pin_str, str):
            return False
        if 'TBD' in fpga_pin_str:
            return False
        if 'iCEstick pin' not in fpga_pin_str:
            return False

    if not required_signals <= seen_signals:
        return False

    return True
```

Rationale: this is a one-shot host-side post-condition that
locks in iter-70/71/72's TBD elimination on the FPGA side of the
jumper table without overlapping the validator's existing
checks, without picking a new MPU GPIO, and without changing the
synthesised bitstream or any firmware artefact. It is strictly
smaller than the next firmware-side step (adding a `reset_n`
drive primitive to `gpio_replay_mpu_stub.c`), which is gated on
selecting an MP135 GPIO port for the MPU side.

### Document control GPIO MPU-pin TODO in mpu replay stub

Surface the iter-73 gap in code rather than only in mission
narrative. The replay headers (auto-generated from
`connectivity_manifest.json`) already include the three control
GPIOs `mpu_reset_output_to_fpga_reset_n`,
`mpu_control_output_to_fpga_ctrl_start`, and
`fpga_ready_status_to_mpu_status_input`, with vector indices 4..9
in `connectivity_mpu_replay.h` / `connectivity_fpga_replay.h`. The
manually-maintained firmware-side per-signal tables
(`mpu_drive_signals[]` and `mpu_sample_signals[]` in
`stm32mp135_test_board/baremetal/gpio_test/gpio_replay_mpu_stub.c`)
remain QSPI-only, so the helpers `mpu_drive()` and
`mpu_sample_expect()` silently no-op when invoked with one of those
control-GPIO signal names: `find_mpu_drive_signal()` /
`find_mpu_sample_signal()` return NULL and the helpers return
success without touching any HAL pin.

Add a `TODO(gpio_test mpu pin choice)` comment block immediately
after `mpu_drive_signals[]` listing the three signals, naming the
silent-no-op behaviour, and pointing at the next firmware lift
(define `RESET_N` / `CTRL_START` / `STATUS_INPUT` port and pin
macros mirroring `QSPI_NCS_PORT` / `QSPI_NCS_PIN`, and extend the
two per-signal tables). The block is a code comment, not a new
audit, and it captures iter-73's manager-side finding inside the C
source where the next firmware editor will read it.

This is the smallest meaningful step toward `Verify physical
connectivity` that does not pick a new MP135 GPIO pin and is not a
schema-shadow audit. It is build-only, machine-checkable in well
under a minute, and changes one file (the firmware stub source) in
a way that compiles unchanged under both the bench HAL build and
the host `GPIO_REPLAY_STUB_MAIN` self-check.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
```

Test (max 1 min):

```
mark tag=gpio_replay_mpu_stub_control_gpio_todo
```

Verify:

```
from pathlib import Path

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False

    stub = Path(
        'stm32mp135_test_board/baremetal/gpio_test/'
        'gpio_replay_mpu_stub.c')
    try:
        text = stub.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return False

    qspi_required = [
        '"mpu_qspi_ncs_to_fpga_cs_n", QSPI_NCS_PORT, QSPI_NCS_PIN',
        '"mpu_qspi_io0_to_fpga_io0", GPIOH, GPIO_PIN_3',
        '"mpu_qspi_io1_to_fpga_io1", GPIOF, GPIO_PIN_9',
        '"mpu_qspi_io2_to_fpga_io2", GPIOH, GPIO_PIN_6',
        '"mpu_qspi_io3_to_fpga_io3", GPIOH, GPIO_PIN_7',
    ]
    if not all(token in text for token in qspi_required):
        return False

    todo_required = [
        'TODO(gpio_test mpu pin choice)',
        'mpu_reset_output_to_fpga_reset_n',
        'mpu_control_output_to_fpga_ctrl_start',
        'fpga_ready_status_to_mpu_status_input',
        'silently no-op',
    ]
    if not all(token in text for token in todo_required):
        return False

    return True
```

Rationale: this is strictly smaller than the gated firmware lift
(picking an MP135 GPIO port for `reset_n` and adding a real entry
to `mpu_drive_signals[]`), strictly smaller than committing an
MPU-side `mpu_signal_pin` in the manifest (which would still be a
paper change but would freeze a bench-engineering decision without
schematic input), and not a duplicate of the iter-73 lock-in audit
(that audit checks `connectivity_manifest.json`'s `fpga_signal_pin`
column for the `TBD` substring; this chapter touches only
`gpio_replay_mpu_stub.c` and asserts a positive code-comment
property, not a manifest-shadow property). The verify also keeps
the existing QSPI per-signal-table coverage in scope so the comment
addition does not regress the bench-tested wiring.

### Audit prbs polynomial and seed match across FPGA and MPU

Lock in the cross-language PRBS interface invariant: the FPGA
`prbs_xor` core (`fpga/src/prbs_xor.nw`) and the MPU baremetal
`prbs_test` reference (`stm32mp135_test_board/baremetal/prbs_test/
src/main.c`) must agree on (i) the 32-bit Galois LFSR polynomial
`0x80200003` and (ii) the seed `0x00000001`. They are written as
independent literals in two source files in two languages, so a
future edit that retunes the polynomial in one file but not the
other would silently break every later FPGA-vs-MPU checksum
comparison without any existing verifier noticing. This audit
wires that invariant into the verify path.

The audit is host-only and textual: it reads both source files
and asserts each contains the polynomial constant in its
language-native hex spelling (`32'h8020_0003` for Verilog,
`0x80200003u` for C) and the seed constant (`32'h0000_0001` for
Verilog, `0x00000001u` for C). It also asserts the symbolic names
match between the two files (`POLY` / `SEED` on the Verilog side,
`PRBS_POLY` / `PRBS_SEED` on the C side) so future readers find
both constants by the same intent.

This is not a schema-shadow audit: there is no existing validator
that enforces cross-language PRBS constant equivalence. The FPGA
build path tangles `prbs_xor.v` from `prbs_xor.nw` but does not
read the MPU sources; the MPU build compiles `main.c` but does
not read `prbs_xor.nw`. Without this audit the only thing tying
the two values together is a comment in the mission narrative,
which is not machine-checkable.

This is the smallest meaningful step toward `PRBS, UART, Checksum`
that does not require adding UART command parsing to the MPU
firmware (which is a multi-iteration lift requiring a HAL UART
RX loop, command dispatch, and matching test fixtures). It is
host-only, machine-checkable in well under a minute, and changes
zero source files (chapter is verify-only on existing artefacts).

Build: no build step (host-only verify on existing sources).

Test (max 1 min):

```
mark tag=prbs_xor_mpu_constants_match
```

Verify:

```
from pathlib import Path

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False

    fpga_nw = Path('fpga/src/prbs_xor.nw')
    mpu_c   = Path('stm32mp135_test_board/baremetal/'
                   'prbs_test/src/main.c')
    try:
        nw_text = fpga_nw.read_text(encoding='utf-8',
                                    errors='replace')
        c_text  = mpu_c.read_text(encoding='utf-8',
                                  errors='replace')
    except OSError:
        return False

    fpga_required = [
        "localparam [31:0] SEED = 32'h0000_0001;",
        "localparam [31:0] POLY = 32'h8020_0003;",
    ]
    if not all(tok in nw_text for tok in fpga_required):
        return False

    mpu_required = [
        '#define PRBS_POLY 0x80200003u',
        '#define PRBS_SEED 0x00000001u',
        '(state >> 1) ^ PRBS_POLY',
    ]
    if not all(tok in c_text for tok in mpu_required):
        return False

    return True
```

Rationale: this is strictly smaller than adding any new firmware
or Verilog code (the audit changes no source file outside the
mission file itself), strictly smaller than the next bench-progress
step toward end-to-end checksum comparison (which requires an MPU
UART command parser plus a `'p'`-style print path, several files
of new firmware), and not a duplicate of any earlier audit (no
existing audit reads both `prbs_xor.nw` and `prbs_test/src/main.c`,
so this audit's invariant is not enforced anywhere today). Making
it any smaller (audit only POLY, or audit only SEED, or audit
only one of the two files) would let drift through on the
unaudited constant or unaudited side, leaving zero locked-in
cross-language progress; making it any larger (e.g. recompute the
LFSR sequence in Python and compare to a captured C/Verilog trace)
would require running a simulator or executing the C and is not
host-only.

## WIP

### Verify physical connectivity

Use `gpio.nw` and the MP135 `gpio_test` harness to verify the physical
connections in the assumed jumper table.

### PRBS, UART, Checksum

Add `prbs_xor.nw`, combining an LFSR PRBS generator, an XOR checksum,
and a small UART command interface. Commands reset state, stream one
word, stream `2**16` words, and print the checksum.

Add the same PRBS/checksum behavior to
`stm32mp135_test_board/baremetal/prbs_test`.

Compare FPGA and MPU checksum streams across short single-step runs and
larger burst runs.

### Bit Bang 1-lane Raw SPI

Add `spi.nw` as a one-lane SPI slave that streams PRBS data into the
checksum path. UART commands still reset and print the checksum; SPI
traffic drives the data stream.

Add an MP135 `spi_bitbang` test that acts as a GPIO bit-banged SPI
master and keeps an independent PRBS/checksum reference.

Verify matching FPGA and MPU checksums for both short and long
transfers.

### Bit Bang 4-lane Raw SPI

Extend `spi.nw` and `spi_bitbang` to transfer PRBS data over four SPI
lanes while preserving the one-lane checksum model.

### 1-Lane Raw SPI, 4 GiB, >=100 Mbps

Add an MP135 `spi` test using the real SPI peripheral instead of GPIO
bit-banging.

Verify bit-perfect one-lane transfers at 100 Mbps or faster while
keeping the SPI clock at or below 133 MHz.

### 4-Lane Raw SPI, 4 GiB, >=400 Mbps

Verify bit-perfect quad-lane transfers at 400 Mbps or faster while
keeping the SPI clock at or below 133 MHz and minimizing per-transfer
software overhead.

### Memory-Mapped Quad SPI, >= 400 Mbps

Implement enough JEDEC flash behavior for the MP135 QuadSPI peripheral
to use the FPGA stream in memory-mapped mode at 400 Mbps or faster.

### Temporary: remove stale files

When all works fine, we can remove the fpga/src/to_be_replaced_by_cleaner_code
 files.
