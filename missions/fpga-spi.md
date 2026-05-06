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
| MP135 GPIO reset output, exact MPU pin TBD | FPGA `reset_n`, exact FPGA pin TBD | MPU -> FPGA | Assumed 3.3 V LVCMOS control GPIO | Active-low FPGA logic reset/control jumper; no committed FPGA package pin found yet. |
| MP135 GPIO control output, exact MPU pin TBD | FPGA `ctrl`/`start`, exact FPGA pin TBD | MPU -> FPGA | Assumed 3.3 V LVCMOS control GPIO | Optional bring-up control GPIO for connection tests; exact signal name and pin remain TBD. |
| MP135 GPIO status input, exact MPU pin TBD | FPGA `ready`/`status`, exact FPGA pin TBD | FPGA -> MPU | Assumed 3.3 V LVCMOS control GPIO | Optional FPGA-to-MPU status GPIO for connection tests; exact signal name and pin remain TBD. |
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
