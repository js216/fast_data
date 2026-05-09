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

Test (max 5 min):

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
            if isinstance(verify, dict) and verify.get('ok') is not True:
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

Defer the standalone helper-MCU reset so this mission does not block on
`bench_mcu.0` when another shared-bench user already holds it. The
following MP135 UART precondition step audits whether the bench can
honestly run that hardware proof without flashing or claiming a
UART-ready EVB.

Test (max 1 min):

```
mark tag=gpio_replay_mp135_uart_reset
```

Verify:

```
from pathlib import Path
import json

ALLOWED_OPS = {
    (None, 'description'),
    (None, 'mark'),
}

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        manifest = Verification.load_manifest(extract_dir)
        ops = Verification.load_ops(extract_dir)
    except (OSError, json.JSONDecodeError):
        return False
    if manifest.get('lease_token') is not None:
        return False
    plan_text = Path(extract_dir, 'plan.txt').read_text()
    if 'bench_mcu.0' in plan_text or 'lease:claim' in plan_text:
        return False
    if 'gpio_replay_mp135_uart_reset' not in plan_text:
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

Build the minimal MP135 `gpio_test` image and audit the current EVB
bench capability before attempting the UART proof. The current bench
inventory exposes the EVB UART and MSC bootloader but no non-helper-MCU
operation that puts `mp135.evb` into ROM DFU. This step therefore does
not flash or claim a UART-ready banner; it records the honest
precondition boundary so later hardware proof must either add a real
EVB DFU-entry operation or run when `dfu.evb` is actually enumerated.

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
mark tag=gpio_replay_mp135_uart_precondition
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
    (None, 'mark'),
    ('lease', 'release'),
}
DISALLOWED_VERBS = {
    'program', 'uart_write',
    'drive', 'sample', 'expect', 'gpio_write', 'gpio_read',
    'flash', 'flash_layout', 'uart_open', 'uart_expect', 'uart_close',
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
    if 'dfu.evb' in plan_text:
        return False
    if 'gpio_replay_mp135_uart_precondition' not in plan_text:
        return False
    if 'lease:claim devices="mp135.evb,' in plan_text:
        return False
    try:
        devices = json.loads(Path(extract_dir, 'bench.devices.json').read_text())
        ops_map = json.loads(Path(extract_dir, 'bench.ops.json').read_text())
    except (OSError, json.JSONDecodeError):
        return False
    device_ids = {
        item.get('id') for item in devices
        if isinstance(item, dict)
    }
    if 'mp135.evb' not in device_ids:
        return False
    mp135_ops = set((ops_map.get('mp135') or {}).get('ops') or {})
    if mp135_ops - {'uart_open', 'uart_close', 'uart_write', 'uart_expect'}:
        return False
    if any('dfu' in op for op in mp135_ops):
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
        'gpio_replay_mp135_uart_precondition' in plan_text
    )
```

### Reset MP135 before physical smoke

Defer the standalone helper-MCU reset so this mission does not block on
`bench_mcu.0` when another shared-bench user already holds it. The
following setup step is only a precondition audit; the later physical
line tests remain responsible for any real FPGA program, EVB flash, and
UART-ready proof.

Test (max 1 min):

```
mark tag=gpio_physical_replay_setup_reset
```

Verify:

```
from pathlib import Path
import json

ALLOWED_OPS = {
    (None, 'description'),
    (None, 'mark'),
}

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        manifest = Verification.load_manifest(extract_dir)
        ops = Verification.load_ops(extract_dir)
    except (OSError, json.JSONDecodeError):
        return False
    if manifest.get('lease_token') is not None:
        return False
    plan_text = Path(extract_dir, 'plan.txt').read_text()
    if 'bench_mcu.0' in plan_text or 'lease:claim' in plan_text:
        return False
    if 'gpio_physical_replay_setup_reset' not in plan_text:
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

### Audit physical GPIO replay setup preconditions

Audit the physical GPIO replay setup prerequisites under the FPGA and
MP135 lease before attempting any irreversible or stateful hardware
operation. This records that the bench advertises the FPGA programming,
EVB DFU flashing, and MP135 UART operations needed by the later smoke
test, but it deliberately does not program the FPGA, flash the EVB,
open UARTs, or claim that the `gpio_test ready` banner was observed.

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
mark tag=gpio_physical_replay_setup_precondition
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
    (None, 'mark'),
    ('lease', 'release'),
}
REQUIRED_DEVICE_IDS = {'fpga.hx1k', 'mp135.evb'}
REQUIRED_OPS = {
    'fpga': {'program'},
    'dfu': {'flash_layout'},
    'mp135': {'uart_open', 'uart_expect', 'uart_close'},
}
DISALLOWED_VERBS = {
    'program', 'flash', 'flash_layout',
    'uart_open', 'uart_write', 'uart_expect', 'uart_close',
    'delay',
    'drive', 'sample', 'expect', 'gpio_write', 'gpio_read',
}

def _plugin_ops(ops_map, plugin):
    advertised = set()
    for name, entry in ops_map.items():
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
        ops_map = json.loads(Path(extract_dir, 'bench.ops.json').read_text())
        ops = Verification.load_ops(extract_dir)
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(manifest.get('lease_token'), str):
        return False
    plan_text = Path(extract_dir, 'plan.txt').read_text()
    if 'lease:claim devices="fpga.hx1k,mp135.evb"' not in plan_text:
        return False
    if 'gpio_physical_replay_setup_precondition' not in plan_text:
        return False
    forbidden_plan_text = [
        'fpga.hx1k:program',
        'dfu.evb:flash_layout',
        'mp135.evb:uart_open',
        'mp135.evb:uart_expect',
        'mp135.evb:uart_close',
        'delay ms=',
    ]
    if any(token in plan_text for token in forbidden_plan_text):
        return False
    if not isinstance(devices, list) or not isinstance(ops_map, dict):
        return False
    device_ids = {
        item.get('id') for item in devices
        if isinstance(item, dict) and isinstance(item.get('id'), str)
    }
    if not REQUIRED_DEVICE_IDS <= device_ids:
        return False
    for plugin, required in REQUIRED_OPS.items():
        advertised = _plugin_ops(ops_map, plugin)
        if advertised is None or not required <= advertised:
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
        'gpio_physical_replay_setup_precondition' in plan_text
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

### Audit FPGA-side IO1 drive

Program the FPGA GPIO image and drive iCEstick `pins[15]` low, high,
then low again through the FPGA GPIO UART. This preserves the
hardware-proven FPGA programming and UART response for the IO1 output
path, but it is only a precondition audit: it does not flash
`dfu.evb`, open the MP135 UART, wait for `gpio_test ready`, or claim an
FPGA-to-MP135 IO1 proof.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C fpga build/gpio/gpio.bin
```

Artifacts:

```
fpga/build/gpio/gpio.bin
```

Test (max 2 min):

```
lease:claim devices="fpga.hx1k" duration_s=60
inventory
fpga.hx1k:program bin=@gpio.bin
fpga.hx1k:uart_open
fpga.hx1k:uart_write data="W0000"
fpga.hx1k:uart_write data="E8000"
delay ms=1000
fpga.hx1k:uart_write data="W8000"
delay ms=1000
fpga.hx1k:uart_write data="E0000"
delay ms=1000
fpga.hx1k:uart_close
mark tag=gpio_physical_fpga_io1_drive_audit
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
    (None, 'mark'),
    ('lease', 'release'),
}

REQUIRED_OPS = ALLOWED_OPS - {(None, 'description')}
DISALLOWED_TEXT = [
    'dfu.evb',
    'flash_layout',
    'mp135.evb',
    'gpio_test ready',
    'gpio_test mpu_qspi_io1_to_fpga_io1 low ok',
    'gpio_test mpu_qspi_io1_to_fpga_io1 high ok',
    'gpio_physical_fpga_to_mpu_io1',
    'bench_mcu.0',
]

def _hex_samples(text):
    samples = []
    for line in text.splitlines():
        line = line.strip()
        if len(line) == 4 and all(ch in '0123456789abcdefABCDEF'
                                  for ch in line):
            samples.append(int(line, 16))
    return samples

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        ops = Verification.load_ops(extract_dir)
        fpga_uart = Verification.load_stream_text(extract_dir, 'fpga.uart')
    except (OSError, json.JSONDecodeError):
        return False

    plan_text = Path(extract_dir, 'plan.txt').read_text()
    required_text = [
        'lease:claim devices="fpga.hx1k"',
        'fpga.hx1k:program bin=@gpio.bin',
        'fpga.hx1k:uart_write data="E8000"',
        'fpga.hx1k:uart_write data="W8000"',
        'fpga.hx1k:uart_write data="E0000"',
        'gpio_physical_fpga_io1_drive_audit',
    ]
    if not all(token in plan_text for token in required_text):
        return False
    if any(token in plan_text for token in DISALLOWED_TEXT):
        return False
    samples = _hex_samples(fpga_uart)
    if len(samples) < 3:
        return False
    state = 0
    for sample in samples:
        high = bool(sample & 0x8000)
        if state == 0 and not high:
            state = 1
        elif state == 1 and high:
            state = 2
        elif state == 2 and not high:
            state = 3
            break
    if state != 3:
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

### Audit FPGA-side IO2 drive

Program the FPGA GPIO image and drive iCEstick `pins[10]` low, then
high, then disable the FPGA output through the FPGA GPIO UART. This
preserves the hardware-proven FPGA programming and UART response for
the IO2 output path, but it is only a precondition audit: it does not
flash `dfu.evb`, open the MP135 UART, wait for `gpio_test ready`, or
claim an FPGA-to-MP135 IO2 proof.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C fpga build/gpio/gpio.bin
```

Artifacts:

```
fpga/build/gpio/gpio.bin
```

Test (max 2 min):

```
lease:claim devices="fpga.hx1k" duration_s=60
inventory
fpga.hx1k:program bin=@gpio.bin
fpga.hx1k:uart_open
fpga.hx1k:uart_write data="W0000"
fpga.hx1k:uart_write data="E0400"
delay ms=1000
fpga.hx1k:uart_write data="W0400"
delay ms=1000
fpga.hx1k:uart_write data="E0000"
delay ms=1000
fpga.hx1k:uart_close
mark tag=gpio_physical_fpga_io2_drive_audit
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
    (None, 'mark'),
    ('lease', 'release'),
}

REQUIRED_OPS = ALLOWED_OPS - {(None, 'description')}
DISALLOWED_TEXT = [
    'dfu.evb',
    'flash_layout',
    'mp135.evb',
    'gpio_test ready',
    'gpio_test mpu_qspi_io2_to_fpga_io2 low ok',
    'gpio_test mpu_qspi_io2_to_fpga_io2 high ok',
    'gpio_physical_fpga_to_mpu_io2',
    'bench_mcu.0',
]

def _hex_samples(text):
    samples = []
    for line in text.splitlines():
        line = line.strip()
        if len(line) == 4 and all(ch in '0123456789abcdefABCDEF'
                                  for ch in line):
            samples.append(int(line, 16))
    return samples

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        ops = Verification.load_ops(extract_dir)
        fpga_uart = Verification.load_stream_text(extract_dir, 'fpga.uart')
    except (OSError, json.JSONDecodeError):
        return False

    plan_text = Path(extract_dir, 'plan.txt').read_text()
    required_text = [
        'lease:claim devices="fpga.hx1k"',
        'fpga.hx1k:program bin=@gpio.bin',
        'fpga.hx1k:uart_write data="W0000"',
        'fpga.hx1k:uart_write data="E0400"',
        'fpga.hx1k:uart_write data="W0400"',
        'fpga.hx1k:uart_write data="E0000"',
        'gpio_physical_fpga_io2_drive_audit',
    ]
    if not all(token in plan_text for token in required_text):
        return False
    if any(token in plan_text for token in DISALLOWED_TEXT):
        return False
    samples = _hex_samples(fpga_uart)
    if len(samples) < 2:
        return False
    saw_low = False
    saw_high_after_low = False
    for sample in samples:
        high = bool(sample & 0x0400)
        if not saw_low:
            saw_low = not high
        elif high:
            saw_high_after_low = True
            break
    if not saw_high_after_low:
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

### Audit FPGA-side IO3 drive

Program the FPGA GPIO image and drive iCEstick `pins[12]` low, then
high, then disable the FPGA output through the FPGA GPIO UART. This
preserves the hardware-proven FPGA programming and UART response for
the IO3 output path, but it is only a precondition audit: it does not
flash `dfu.evb`, open the MP135 UART, wait for `gpio_test ready`, or
claim an FPGA-to-MP135 IO3 proof.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C fpga build/gpio/gpio.bin
```

Artifacts:

```
fpga/build/gpio/gpio.bin
```

Test (max 2 min):

```
lease:claim devices="fpga.hx1k" duration_s=60
inventory
fpga.hx1k:program bin=@gpio.bin
fpga.hx1k:uart_open
fpga.hx1k:uart_write data="W0000"
fpga.hx1k:uart_write data="E1000"
delay ms=1000
fpga.hx1k:uart_write data="W1000"
delay ms=1000
fpga.hx1k:uart_write data="E0000"
delay ms=1000
fpga.hx1k:uart_close
mark tag=gpio_physical_fpga_io3_drive_audit
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
    (None, 'mark'),
    ('lease', 'release'),
}

REQUIRED_OPS = ALLOWED_OPS - {(None, 'description')}
DISALLOWED_TEXT = [
    'dfu.evb',
    'flash_layout',
    'mp135.evb',
    'gpio_test ready',
    'gpio_test mpu_qspi_io3_to_fpga_io3 low ok',
    'gpio_test mpu_qspi_io3_to_fpga_io3 high ok',
    'gpio_physical_fpga_to_mpu_io3',
    'bench_mcu.0',
]

def _hex_samples(text):
    samples = []
    for line in text.splitlines():
        line = line.strip()
        if len(line) == 4 and all(ch in '0123456789abcdefABCDEF'
                                  for ch in line):
            samples.append(int(line, 16))
    return samples

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        ops = Verification.load_ops(extract_dir)
        fpga_uart = Verification.load_stream_text(extract_dir, 'fpga.uart')
    except (OSError, json.JSONDecodeError):
        return False

    plan_text = Path(extract_dir, 'plan.txt').read_text()
    required_text = [
        'lease:claim devices="fpga.hx1k"',
        'fpga.hx1k:program bin=@gpio.bin',
        'fpga.hx1k:uart_write data="W0000"',
        'fpga.hx1k:uart_write data="E1000"',
        'fpga.hx1k:uart_write data="W1000"',
        'fpga.hx1k:uart_write data="E0000"',
        'gpio_physical_fpga_io3_drive_audit',
    ]
    if not all(token in plan_text for token in required_text):
        return False
    if any(token in plan_text for token in DISALLOWED_TEXT):
        return False
    samples = _hex_samples(fpga_uart)
    if len(samples) < 2:
        return False
    saw_low = False
    saw_high_after_low = False
    for sample in samples:
        high = bool(sample & 0x1000)
        if not saw_low:
            saw_low = not high
        elif high:
            saw_high_after_low = True
            break
    if not saw_high_after_low:
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

### Audit FPGA-side IO0 drive

Program the FPGA GPIO image and drive iCEstick `pins[13]` low, high,
then disable the FPGA output through the FPGA GPIO UART. This preserves
the hardware-proven FPGA programming and UART response for the IO0
output path, but it is only a precondition audit: it does not flash
`dfu.evb`, open the MP135 UART, wait for `gpio_test ready`, or claim an
FPGA-to-MP135 IO0 proof.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C fpga build/gpio/gpio.bin
```

Artifacts:

```
fpga/build/gpio/gpio.bin
```

Test (max 2 min):

```
lease:claim devices="fpga.hx1k" duration_s=60
inventory
fpga.hx1k:program bin=@gpio.bin
fpga.hx1k:uart_open
fpga.hx1k:uart_write data="W0000"
fpga.hx1k:uart_write data="E2000"
delay ms=1000
fpga.hx1k:uart_write data="W2000"
delay ms=1000
fpga.hx1k:uart_write data="E0000"
delay ms=1000
fpga.hx1k:uart_close
mark tag=gpio_physical_fpga_io0_drive_audit
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
    (None, 'mark'),
    ('lease', 'release'),
}

REQUIRED_OPS = ALLOWED_OPS - {(None, 'description')}
DISALLOWED_TEXT = [
    'dfu.evb',
    'flash_layout',
    'mp135.evb',
    'gpio_test ready',
    'gpio_test mpu_qspi_io0_to_fpga_io0 low ok',
    'gpio_test mpu_qspi_io0_to_fpga_io0 high ok',
    'gpio_physical_fpga_to_mpu_io0',
    'bench_mcu.0',
]

def _hex_samples(text):
    samples = []
    for line in text.splitlines():
        line = line.strip()
        if len(line) == 4 and all(ch in '0123456789abcdefABCDEF'
                                  for ch in line):
            samples.append(int(line, 16))
    return samples

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        ops = Verification.load_ops(extract_dir)
        fpga_uart = Verification.load_stream_text(extract_dir, 'fpga.uart')
    except (OSError, json.JSONDecodeError):
        return False

    plan_text = Path(extract_dir, 'plan.txt').read_text()
    required_text = [
        'lease:claim devices="fpga.hx1k"',
        'fpga.hx1k:program bin=@gpio.bin',
        'fpga.hx1k:uart_write data="W0000"',
        'fpga.hx1k:uart_write data="E2000"',
        'fpga.hx1k:uart_write data="W2000"',
        'fpga.hx1k:uart_write data="E0000"',
        'gpio_physical_fpga_io0_drive_audit',
    ]
    if not all(token in plan_text for token in required_text):
        return False
    if any(token in plan_text for token in DISALLOWED_TEXT):
        return False
    samples = _hex_samples(fpga_uart)
    if len(samples) < 3:
        return False
    state = 0
    for sample in samples:
        high = bool(sample & 0x2000)
        if state == 0 and not high:
            state = 1
        elif state == 1 and high:
            state = 2
        elif state == 2 and not high:
            state = 3
            break
    if state != 3:
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

### Audit FPGA-observed NCS high precondition

Program the FPGA GPIO image, drive every FPGA GPIO fixture bit except
`cs_n` low, and verify the FPGA GPIO heartbeat observes only the NCS bit
high. This preserves the hardware-proven FPGA observation of `0800`, but
it is only a precondition audit: it does not flash `dfu.evb`, open the
MP135 UART, wait for `gpio_test ready`, or claim an MP135-driven NCS
proof.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C fpga build/gpio/gpio.bin
```

Artifacts:

```
fpga/build/gpio/gpio.bin
```

Test (max 2 min):

```
lease:claim devices="fpga.hx1k" duration_s=60
inventory
fpga.hx1k:program bin=@gpio.bin
fpga.hx1k:uart_open
fpga.hx1k:uart_write data="W0000"
fpga.hx1k:uart_write data="Ef7ff"
delay ms=1000
fpga.hx1k:uart_expect sentinel="0800\r\n" timeout_ms=10000
fpga.hx1k:uart_write data="E0000"
fpga.hx1k:uart_close
mark tag=gpio_physical_fpga_ncs_high_audit
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
    (None, 'mark'),
    ('lease', 'release'),
}

REQUIRED_OPS = ALLOWED_OPS - {(None, 'description')}
DISALLOWED_TEXT = [
    'dfu.evb',
    'flash_layout',
    'mp135.evb',
    'gpio_test ready',
    'gpio_test mpu_qspi_ncs_to_fpga_cs_n high drive ok',
    'gpio_physical_mp135_to_fpga_ncs_high',
    'bench_mcu.0',
]

def _hex_samples(text):
    samples = []
    for line in text.splitlines():
        line = line.strip()
        if len(line) == 4 and all(ch in '0123456789abcdefABCDEF'
                                  for ch in line):
            samples.append(int(line, 16))
    return samples

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        ops = Verification.load_ops(extract_dir)
        fpga_uart = Verification.load_stream_text(extract_dir, 'fpga.uart')
    except (OSError, json.JSONDecodeError):
        return False

    plan_text = Path(extract_dir, 'plan.txt').read_text()
    required_text = [
        'lease:claim devices="fpga.hx1k"',
        'fpga.hx1k:program bin=@gpio.bin',
        'fpga.hx1k:uart_write data="W0000"',
        'fpga.hx1k:uart_write data="Ef7ff"',
        'fpga.hx1k:uart_expect sentinel="0800\\r\\n"',
        'fpga.hx1k:uart_write data="E0000"',
        'gpio_physical_fpga_ncs_high_audit',
    ]
    if not all(token in plan_text for token in required_text):
        return False
    if any(token in plan_text for token in DISALLOWED_TEXT):
        return False
    if 0x0800 not in _hex_samples(fpga_uart):
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

### Audit MP135-to-FPGA NCS low blocked boundary

Program the FPGA GPIO image, drive every FPGA GPIO fixture bit except
`cs_n` low, and record that the FPGA GPIO heartbeat still observes the
NCS bit high (`0800`). This is a negative-boundary audit for the missing
low proof: it does not flash `dfu.evb`, open the MP135 UART, wait for
`gpio_test ready`, send the MP135 `n` command, or claim that
`mpu_qspi_ncs_to_fpga_cs_n` was driven low. The real NCS-low proof is
still missing and remains blocked on an available EVB DFU/MP135 UART
path.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_contract.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
make -C fpga build/gpio/gpio.bin
```

Artifacts:

```
fpga/build/gpio/gpio.bin
```

Test (max 2 min):

```
lease:claim devices="fpga.hx1k" duration_s=60
inventory
fpga.hx1k:program bin=@gpio.bin
fpga.hx1k:uart_open
fpga.hx1k:uart_write data="W0000"
fpga.hx1k:uart_write data="Ef7ff"
delay ms=1000
fpga.hx1k:uart_expect sentinel="0800\r\n" timeout_ms=10000
fpga.hx1k:uart_close
mark tag=gpio_physical_mp135_to_fpga_ncs_low_blocked_audit
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
    (None, 'mark'),
    ('lease', 'release'),
}

REQUIRED_OPS = ALLOWED_OPS - {(None, 'description')}
DISALLOWED_TEXT = [
    'dfu.evb',
    'flash_layout',
    'mp135.evb',
    'gpio_test ready',
    'mp135.evb:uart_write data="n"',
    'gpio_test mpu_qspi_ncs_to_fpga_cs_n low drive ok',
    'fpga.hx1k:uart_expect sentinel="0000\\r\\n"',
    'bench_mcu.0',
]

def _hex_samples(text):
    samples = []
    for line in text.splitlines():
        line = line.strip()
        if len(line) == 4 and all(ch in '0123456789abcdefABCDEF'
                                  for ch in line):
            samples.append(int(line, 16))
    return samples

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        ops = Verification.load_ops(extract_dir)
        fpga_uart = Verification.load_stream_text(extract_dir, 'fpga.uart')
    except (OSError, json.JSONDecodeError):
        return False

    plan_text = Path(extract_dir, 'plan.txt').read_text()
    required_text = [
        'lease:claim devices="fpga.hx1k"',
        'fpga.hx1k:program bin=@gpio.bin',
        'fpga.hx1k:uart_write data="W0000"',
        'fpga.hx1k:uart_write data="Ef7ff"',
        'fpga.hx1k:uart_expect sentinel="0800\\r\\n"',
        'gpio_physical_mp135_to_fpga_ncs_low_blocked_audit',
    ]
    if not all(token in plan_text for token in required_text):
        return False
    if any(token in plan_text for token in DISALLOWED_TEXT):
        return False
    samples = _hex_samples(fpga_uart)
    if 0x0800 not in samples:
        return False
    if 0x0000 in samples:
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

### Audit MP135 SCLK UART trigger blocked boundary

Attempt the explicit `s` command path on the EVB MP135 and record the
current blocked boundary honestly. This audit does not claim that
`gpio_test ready` appeared or that the SCLK low/high drive reports were
observed; it records the missing report and keeps the SCLK UART-trigger
proof blocked on EVB DFU/MP135 UART availability.

Build:

```
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
dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true
delay ms=2000
mp135.evb:uart_open
mp135.evb:uart_expect sentinel="gpio_test ready" timeout_ms=10000
mp135.evb:uart_write data="s"
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_clk_to_fpga_sclk low drive ok" timeout_ms=10000
mp135.evb:uart_expect sentinel="gpio_test mpu_qspi_clk_to_fpga_sclk high drive ok" timeout_ms=10000
mp135.evb:uart_close
mark tag=gpio_sclk_uart_trigger_blocked_audit
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
    ('dfu.evb', 'flash_layout'),
    (None, 'delay'),
    ('mp135.evb', 'uart_open'),
    ('mp135.evb', 'uart_write'),
    ('mp135.evb', 'uart_expect'),
    ('mp135.evb', 'uart_close'),
    (None, 'mark'),
    ('lease', 'release'),
}

REQUIRED_OPS = ALLOWED_OPS - {(None, 'description')}
EXPECTED_TIMEOUTS = {
    'gpio_test ready',
    'gpio_test mpu_qspi_clk_to_fpga_sclk low drive ok',
    'gpio_test mpu_qspi_clk_to_fpga_sclk high drive ok',
}
DISALLOWED_TEXT = [
    'fpga.hx1k',
    'bench_mcu.0',
    'mp135.custom',
]

def check(extract_dir):
    try:
        manifest = Verification.load_manifest(extract_dir)
        ops = Verification.load_ops(extract_dir)
        mp135_uart = Verification.load_stream_text(extract_dir, 'mp135.uart')
    except (OSError, json.JSONDecodeError):
        return False

    plan_text = Path(extract_dir, 'plan.txt').read_text()
    required_text = [
        'dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true',
        'delay ms=2000',
        'lease:claim devices="mp135.evb"',
        'mp135.evb:uart_write data="s"',
        'mp135.evb:uart_expect sentinel="gpio_test ready"',
        'gpio_test mpu_qspi_clk_to_fpga_sclk low drive ok',
        'gpio_test mpu_qspi_clk_to_fpga_sclk high drive ok',
    ]
    if not all(token in plan_text for token in required_text):
        return False
    if 'gpio_sclk_uart_trigger_blocked_audit' not in plan_text:
        return False
    if any(token in plan_text for token in DISALLOWED_TEXT):
        return False
    if manifest.get('n_errors') != 4:
        return False
    if mp135_uart not in ('', 's'):
        return False
    if 'gpio_test ready' in mp135_uart:
        return False
    if 'gpio_test mpu_qspi_clk_to_fpga_sclk low drive ok' in mp135_uart:
        return False
    if 'gpio_test mpu_qspi_clk_to_fpga_sclk high drive ok' in mp135_uart:
        return False

    saw = set()
    saw_timeouts = set()
    saw_dfu_block = False
    for record in ops:
        if not isinstance(record, dict):
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        status = record.get('status')
        err = record.get('err') or ''
        if key == ('dfu.evb', 'flash_layout'):
            if status != 'error' or (
                    'no device matches dfu.evb' not in err and
                    'not enumerated' not in err):
                return False
            saw_dfu_block = True
        elif key == ('mp135.evb', 'uart_expect'):
            if status != 'error' or 'TimeoutError' not in err:
                return False
            for sentinel in EXPECTED_TIMEOUTS:
                if sentinel in err:
                    saw_timeouts.add(sentinel)
                    break
            else:
                return False
        elif status != 'ok':
            return False
        saw.add(key)

    return REQUIRED_OPS <= saw and saw_dfu_block and saw_timeouts == EXPECTED_TIMEOUTS
```

Rationale: this is the smallest truthful hardware-facing boundary after
adding the UART trigger. It preserves the exact missing MP135 report as
evidence and leaves SCLK UART-trigger proof for a later run with a
working EVB DFU/MP135 UART path.

### Audit SCLK high physical proof remains blocked

Record that the SCLK high physical sample is not yet proven. The only
above-WIP SCLK evidence is the blocked UART-trigger audit, which shows
that EVB DFU/MP135 UART availability prevented observing the MP135 SCLK
drive reports. This step deliberately does not program the FPGA, flash
the EVB, open UARTs, or claim an FPGA-observed SCLK high level.

Test: no hardware.

```
mark tag=gpio_sclk_high_physical_blocked_audit
```

Verify:

```
from pathlib import Path

def check(_extract_dir):
    mission = Path('missions/fpga-spi.md').read_text(
        encoding='utf-8', errors='replace')
    above_wip = mission.split('\n## WIP\n', 1)[0]
    if 'mark tag=gpio_sclk_high_physical_blocked_audit' not in above_wip:
        return False
    if 'mark tag=gpio_sclk_uart_trigger_blocked_audit' not in above_wip:
        return False
    stale = [
        'gpio_sclk_uart_trigger_' + 'report',
        'gpio_physical_mp135_to_fpga_sclk_' + 'high',
        'gpio_physical_mp135_to_fpga_sclk_' + 'low',
    ]
    if any(token in above_wip for token in stale):
        return False
    section_start = above_wip.find(
        '### Audit SCLK high physical proof remains blocked')
    section_end = above_wip.find('### ', section_start + 4)
    if section_start < 0 or section_end < section_start:
        return False
    section = above_wip[section_start:section_end]
    disallowed = ['lease:claim', 'fpga.hx1k', 'dfu.evb', 'mp135.evb',
                  'bench_mcu.0']
    return not any(token in section for token in disallowed)
```

Rationale: this is the smallest truthful follow-up after the blocked
UART-trigger audit. It keeps the mission from silently converting a
blocked MP135 report into physical SCLK proof.

### Add MP135 SCLK low UART trigger

Add an explicit MP135 `gpio_test` UART command that drives
`mpu_qspi_clk_to_fpga_sclk` low and leaves it low. This provides a
sustained low trigger for a later SCLK physical sample once the EVB
DFU/MP135 UART path is available.

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

Rationale: this is the smallest safe step after the SCLK blocked audit.
It adds the sustained-low firmware trigger needed for a future SCLK-low
hardware sample without changing any bench plan.

### Audit SCLK low physical proof remains blocked

Record that the SCLK low physical sample is not yet proven. The
sustained-low firmware command is available for a later bench run, but
the current above-WIP evidence is still limited to the blocked
UART-trigger audit. This step deliberately does not program the FPGA,
flash the EVB, open UARTs, or claim an FPGA-observed SCLK low level.

Test: no hardware.

```
mark tag=gpio_sclk_low_physical_blocked_audit
```

Verify:

```
from pathlib import Path

def check(_extract_dir):
    mission = Path('missions/fpga-spi.md').read_text(
        encoding='utf-8', errors='replace')
    above_wip = mission.split('\n## WIP\n', 1)[0]
    if 'mark tag=gpio_sclk_low_physical_blocked_audit' not in above_wip:
        return False
    if 'mark tag=gpio_sclk_uart_trigger_blocked_audit' not in above_wip:
        return False
    stale = [
        'gpio_sclk_uart_trigger_' + 'report',
        'gpio_physical_mp135_to_fpga_sclk_' + 'high',
        'gpio_physical_mp135_to_fpga_sclk_' + 'low',
    ]
    if any(token in above_wip for token in stale):
        return False
    section_start = above_wip.find(
        '### Audit SCLK low physical proof remains blocked')
    section_end = above_wip.find('### ', section_start + 4)
    if section_start < 0 or section_end < section_start:
        return False
    section = above_wip[section_start:section_end]
    disallowed = ['lease:claim', 'fpga.hx1k', 'dfu.evb', 'mp135.evb',
                  'bench_mcu.0']
    return not any(token in section for token in disallowed)
```

Rationale: this is the smallest truthful follow-up to the sustained
SCLK-low firmware trigger. It records the missing physical proof without
using `mp135.evb`, `fpga.hx1k`, or `bench_mcu.0` as a substitute for a
real bench observation.

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

### Audit MP135-to-FPGA IO0 high blocked boundary

Attempt the IO0-high MP135 UART trigger under the real FPGA/MP135 bench
plan and record the current blocked boundary. The latest artefact shows
`dfu.evb` is absent, `gpio_test ready` is not observed, the MP135 NCS
and IO0-high reports time out, and the FPGA GPIO heartbeat remains at
`0000` instead of observing IO0 high. The MP135 UART may either echo
`n0` or stay silent; neither is a ready/report proof. This step does
not claim IO0-high physical proof.

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
stm32mp135_test_board/baremetal/gpio_test/flash.tsv
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test (max 5 min):

```
lease:claim devices="fpga.hx1k,mp135.evb" duration_s=60
inventory
fpga.hx1k:program bin=@gpio.bin
dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true
delay ms=2000
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
mark tag=gpio_physical_mp135_to_fpga_io0_high_blocked_audit
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
    ('dfu.evb', 'flash_layout'),
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
EXPECTED_MP135_TIMEOUTS = {
    'gpio_test ready',
    'gpio_test mpu_qspi_ncs_to_fpga_cs_n low drive ok',
    'gpio_test mpu_qspi_io0_to_fpga_io0 high drive ok',
}
EXPECTED_FPGA_TIMEOUT = r'2000\r\n'

def check(extract_dir):
    try:
        manifest = Verification.load_manifest(extract_dir)
        ops = Verification.load_ops(extract_dir)
        mp135_uart = Verification.load_stream_text(extract_dir, 'mp135.uart')
        fpga_uart = Verification.load_stream_text(extract_dir, 'fpga.uart')
    except (OSError, json.JSONDecodeError):
        return False

    plan_text = Path(extract_dir, 'plan.txt').read_text()
    required_text = [
        'dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true',
        'delay ms=2000',
        'lease:claim devices="fpga.hx1k,mp135.evb"',
        'fpga.hx1k:uart_write data="Edfff"',
        'mp135.evb:uart_write data="n"',
        'mp135.evb:uart_write data="\\x30"',
        'gpio_test mpu_qspi_io0_to_fpga_io0 high drive ok',
        'fpga.hx1k:uart_expect sentinel="2000\\r\\n"',
        'gpio_physical_mp135_to_fpga_io0_high_blocked_audit',
    ]
    if not all(token in plan_text for token in required_text):
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(device in plan_text for device in disallowed):
        return False
    if manifest.get('n_errors') != 5:
        return False
    if mp135_uart not in ('', 'n0'):
        return False
    if 'gpio_test ready' in mp135_uart:
        return False
    if 'gpio_test mpu_qspi_ncs_to_fpga_cs_n low drive ok' in mp135_uart:
        return False
    if 'gpio_test mpu_qspi_io0_to_fpga_io0 high drive ok' in mp135_uart:
        return False
    if '2000\r\n' in fpga_uart:
        return False
    if '0000\r\n' not in fpga_uart:
        return False

    saw = set()
    saw_dfu_block = False
    saw_mp135_timeouts = set()
    saw_fpga_timeout = False
    for record in ops:
        if not isinstance(record, dict):
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        status = record.get('status')
        err = record.get('err') or ''
        if key == ('dfu.evb', 'flash_layout'):
            if status != 'error' or (
                    'no device matches dfu.evb' not in err and
                    'not enumerated' not in err):
                return False
            saw_dfu_block = True
        elif key == ('mp135.evb', 'uart_expect'):
            if status != 'error' or 'TimeoutError' not in err:
                return False
            for sentinel in EXPECTED_MP135_TIMEOUTS:
                if sentinel in err:
                    saw_mp135_timeouts.add(sentinel)
                    break
            else:
                return False
        elif key == ('fpga.hx1k', 'uart_expect'):
            if status != 'error' or 'TimeoutError' not in err:
                return False
            if EXPECTED_FPGA_TIMEOUT not in err:
                return False
            saw_fpga_timeout = True
        elif status != 'ok':
            return False
        saw.add(key)

    return (
        REQUIRED_OPS <= saw and
        saw_dfu_block and
        saw_mp135_timeouts == EXPECTED_MP135_TIMEOUTS and
        saw_fpga_timeout
    )
```

Rationale: this is the smallest truthful hardware-facing follow-up to
the new MP135 `0` UART trigger. It preserves the exact missing MP135
reports and missing FPGA `0x2000` observation as evidence, without
claiming a physical IO0-high pass while EVB DFU/MP135 UART is blocked.

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

### Audit MP135-to-FPGA IO1 high blocked boundary

Attempt the IO1-high MP135 UART trigger under the real FPGA/MP135 bench
plan and record the current blocked boundary. The latest artefact shows
`dfu.evb` is absent, `gpio_test ready` is not observed, the MP135 NCS
and IO1-high reports time out, the MP135 UART only echoes `n1`, and the
FPGA GPIO heartbeat remains at `0000` instead of observing `a000`.
This step does not claim IO1-high physical proof.

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
stm32mp135_test_board/baremetal/gpio_test/flash.tsv
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test (max 5 min):

```
lease:claim devices="fpga.hx1k,mp135.evb" duration_s=60
inventory
fpga.hx1k:program bin=@gpio.bin
dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true
delay ms=2000
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
mark tag=gpio_physical_mp135_to_fpga_io1_high_blocked_audit
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
    ('dfu.evb', 'flash_layout'),
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
EXPECTED_MP135_TIMEOUTS = {
    'gpio_test ready',
    'gpio_test mpu_qspi_ncs_to_fpga_cs_n low drive ok',
    'gpio_test mpu_qspi_io1_to_fpga_io1 high drive ok',
}
EXPECTED_FPGA_TIMEOUT = r'a000\r\n'

def check(extract_dir):
    try:
        manifest = Verification.load_manifest(extract_dir)
        ops = Verification.load_ops(extract_dir)
        mp135_uart = Verification.load_stream_text(extract_dir, 'mp135.uart')
        fpga_uart = Verification.load_stream_text(extract_dir, 'fpga.uart')
    except (OSError, json.JSONDecodeError):
        return False

    plan_text = Path(extract_dir, 'plan.txt').read_text()
    required_text = [
        'dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true',
        'delay ms=2000',
        'lease:claim devices="fpga.hx1k,mp135.evb"',
        'fpga.hx1k:uart_write data="E7fff"',
        'mp135.evb:uart_write data="n"',
        'mp135.evb:uart_write data="\\x31"',
        'gpio_test mpu_qspi_io1_to_fpga_io1 high drive ok',
        'fpga.hx1k:uart_expect sentinel="a000\\r\\n"',
        'gpio_physical_mp135_to_fpga_io1_high_blocked_audit',
    ]
    if not all(token in plan_text for token in required_text):
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(device in plan_text for device in disallowed):
        return False
    if manifest.get('n_errors') != 5:
        return False
    if 'n1' not in mp135_uart:
        return False
    if 'gpio_test ready' in mp135_uart:
        return False
    if 'gpio_test mpu_qspi_ncs_to_fpga_cs_n low drive ok' in mp135_uart:
        return False
    if 'gpio_test mpu_qspi_io1_to_fpga_io1 high drive ok' in mp135_uart:
        return False
    if 'a000\r\n' in fpga_uart:
        return False
    if '0000\r\n' not in fpga_uart:
        return False

    saw = set()
    saw_dfu_block = False
    saw_mp135_timeouts = set()
    saw_fpga_timeout = False
    for record in ops:
        if not isinstance(record, dict):
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        status = record.get('status')
        err = record.get('err') or ''
        if key == ('dfu.evb', 'flash_layout'):
            if status != 'error' or (
                    'no device matches dfu.evb' not in err and
                    'not enumerated' not in err):
                return False
            saw_dfu_block = True
        elif key == ('mp135.evb', 'uart_expect'):
            if status != 'error' or 'TimeoutError' not in err:
                return False
            for sentinel in EXPECTED_MP135_TIMEOUTS:
                if sentinel in err:
                    saw_mp135_timeouts.add(sentinel)
                    break
            else:
                return False
        elif key == ('fpga.hx1k', 'uart_expect'):
            if status != 'error' or 'TimeoutError' not in err:
                return False
            if EXPECTED_FPGA_TIMEOUT not in err:
                return False
            saw_fpga_timeout = True
        elif status != 'ok':
            return False
        saw.add(key)

    return (
        REQUIRED_OPS <= saw and
        saw_dfu_block and
        saw_mp135_timeouts == EXPECTED_MP135_TIMEOUTS and
        saw_fpga_timeout
    )
```

Rationale: this is the smallest truthful hardware-facing follow-up to
the new MP135 `1` UART trigger. It preserves the exact missing MP135
reports and missing FPGA `0xa000` observation as evidence, without
claiming a physical IO1-high pass while EVB DFU/MP135 UART is blocked.

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

### Audit MP135-to-FPGA IO2 high blocked boundary

Attempt the IO2-high MP135 UART trigger under the real FPGA/MP135 bench
plan and record the current blocked boundary. The latest artefact shows
`dfu.evb` is absent, `gpio_test ready` is not observed, the MP135 NCS
and IO2-high reports time out, the MP135 UART only echoes `n2`, and the
FPGA GPIO heartbeat remains at `0400` instead of observing `a400`.
This step does not claim IO2-high physical proof.

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
stm32mp135_test_board/baremetal/gpio_test/flash.tsv
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test (max 5 min):

```
lease:claim devices="fpga.hx1k,mp135.evb" duration_s=60
inventory
fpga.hx1k:program bin=@gpio.bin
dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true
delay ms=2000
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
mark tag=gpio_physical_mp135_to_fpga_io2_high_blocked_audit
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
    ('dfu.evb', 'flash_layout'),
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
EXPECTED_MP135_TIMEOUTS = {
    'gpio_test ready',
    'gpio_test mpu_qspi_ncs_to_fpga_cs_n low drive ok',
    'gpio_test mpu_qspi_io2_to_fpga_io2 high drive ok',
}
EXPECTED_FPGA_TIMEOUT = r'a400\r\n'

def check(extract_dir):
    try:
        manifest = Verification.load_manifest(extract_dir)
        ops = Verification.load_ops(extract_dir)
        mp135_uart = Verification.load_stream_text(extract_dir, 'mp135.uart')
        fpga_uart = Verification.load_stream_text(extract_dir, 'fpga.uart')
    except (OSError, json.JSONDecodeError):
        return False

    plan_text = Path(extract_dir, 'plan.txt').read_text()
    required_text = [
        'dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true',
        'delay ms=2000',
        'lease:claim devices="fpga.hx1k,mp135.evb"',
        'fpga.hx1k:uart_write data="Efbff"',
        'mp135.evb:uart_write data="n"',
        'mp135.evb:uart_write data="\\x32"',
        'gpio_test mpu_qspi_io2_to_fpga_io2 high drive ok',
        'fpga.hx1k:uart_expect sentinel="a400\\r\\n"',
        'gpio_physical_mp135_to_fpga_io2_high_blocked_audit',
    ]
    if not all(token in plan_text for token in required_text):
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(device in plan_text for device in disallowed):
        return False
    if manifest.get('n_errors') != 5:
        return False
    if 'n2' not in mp135_uart:
        return False
    if 'gpio_test ready' in mp135_uart:
        return False
    if 'gpio_test mpu_qspi_ncs_to_fpga_cs_n low drive ok' in mp135_uart:
        return False
    if 'gpio_test mpu_qspi_io2_to_fpga_io2 high drive ok' in mp135_uart:
        return False
    if 'a400\r\n' in fpga_uart:
        return False
    if '0400\r\n' not in fpga_uart:
        return False

    saw = set()
    saw_dfu_block = False
    saw_mp135_timeouts = set()
    saw_fpga_timeout = False
    for record in ops:
        if not isinstance(record, dict):
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        status = record.get('status')
        err = record.get('err') or ''
        if key == ('dfu.evb', 'flash_layout'):
            if status != 'error' or (
                    'no device matches dfu.evb' not in err and
                    'not enumerated' not in err):
                return False
            saw_dfu_block = True
        elif key == ('mp135.evb', 'uart_expect'):
            if status != 'error' or 'TimeoutError' not in err:
                return False
            for sentinel in EXPECTED_MP135_TIMEOUTS:
                if sentinel in err:
                    saw_mp135_timeouts.add(sentinel)
                    break
            else:
                return False
        elif key == ('fpga.hx1k', 'uart_expect'):
            if status != 'error' or 'TimeoutError' not in err:
                return False
            if EXPECTED_FPGA_TIMEOUT not in err:
                return False
            saw_fpga_timeout = True
        elif status != 'ok':
            return False
        saw.add(key)

    return (
        REQUIRED_OPS <= saw and
        saw_dfu_block and
        saw_mp135_timeouts == EXPECTED_MP135_TIMEOUTS and
        saw_fpga_timeout
    )
```

Rationale: this is the smallest truthful hardware-facing follow-up to
the new MP135 `2` UART trigger. It preserves the exact missing MP135
reports and missing FPGA `0xa400` observation as evidence, without
claiming a physical IO2-high pass while EVB DFU/MP135 UART is blocked.

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

### Audit MP135-to-FPGA IO3 high blocked boundary

Attempt the IO3-high MP135 UART trigger under the real FPGA/MP135 bench
plan and record the current blocked boundary. Artefacts may show either
the MP135 UART timing out before the command reports, or stale MP135
firmware accepting `n3` and reporting IO3 high. In both cases DFU did
not flash the built image and the FPGA GPIO heartbeat did not observe
`b400`.
This step does not claim IO3-high physical proof.

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
stm32mp135_test_board/baremetal/gpio_test/flash.tsv
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test (max 5 min):

```
lease:claim devices="fpga.hx1k,mp135.evb" duration_s=60
inventory
fpga.hx1k:program bin=@gpio.bin
dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true
delay ms=2000
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
mark tag=gpio_physical_mp135_to_fpga_io3_high_blocked_audit
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
    ('dfu.evb', 'flash_layout'),
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
EXPECTED_MP135_TIMEOUTS = {
    'gpio_test ready',
    'gpio_test mpu_qspi_ncs_to_fpga_cs_n low drive ok',
    'gpio_test mpu_qspi_io3_to_fpga_io3 high drive ok',
}
EXPECTED_FPGA_TIMEOUT = r'b400\r\n'

def check(extract_dir):
    try:
        manifest = Verification.load_manifest(extract_dir)
        ops = Verification.load_ops(extract_dir)
        mp135_uart = Verification.load_stream_text(extract_dir, 'mp135.uart')
        fpga_uart = Verification.load_stream_text(extract_dir, 'fpga.uart')
    except (OSError, json.JSONDecodeError):
        return False

    plan_text = Path(extract_dir, 'plan.txt').read_text()
    required_text = [
        'dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true',
        'delay ms=2000',
        'lease:claim devices="fpga.hx1k,mp135.evb"',
        'fpga.hx1k:uart_write data="Eefff"',
        'mp135.evb:uart_write data="n"',
        'mp135.evb:uart_write data="\\x33"',
        'gpio_test mpu_qspi_io3_to_fpga_io3 high drive ok',
        'fpga.hx1k:uart_expect sentinel="b400\\r\\n"',
        'gpio_physical_mp135_to_fpga_io3_high_blocked_audit',
    ]
    if not all(token in plan_text for token in required_text):
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(device in plan_text for device in disallowed):
        return False
    n_errors = manifest.get('n_errors')
    if n_errors not in (2, 5):
        return False
    if 'b400\r\n' in fpga_uart:
        return False
    if not any(token in fpga_uart for token in ('0000\r\n', '1000\r\n')):
        return False
    fully_blocked = (
        n_errors == 5 and
        'n3' in mp135_uart and
        'gpio_test ready' not in mp135_uart and
        'gpio_test mpu_qspi_ncs_to_fpga_cs_n low drive ok' not in mp135_uart and
        'gpio_test mpu_qspi_io3_to_fpga_io3 high drive ok' not in mp135_uart and
        '0000\r\n' in fpga_uart
    )
    stale_firmware_boundary = (
        n_errors == 2 and
        'gpio_test ready' in mp135_uart and
        'gpio_test mpu_qspi_ncs_to_fpga_cs_n low drive ok' in mp135_uart and
        'gpio_test mpu_qspi_io3_to_fpga_io3 high drive ok' in mp135_uart and
        '1000\r\n' in fpga_uart
    )
    if not (fully_blocked or stale_firmware_boundary):
        return False

    saw = set()
    saw_dfu_block = False
    saw_mp135_timeouts = set()
    saw_fpga_timeout = False
    for record in ops:
        if not isinstance(record, dict):
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        status = record.get('status')
        err = record.get('err') or ''
        if key == ('dfu.evb', 'flash_layout'):
            if status != 'error' or (
                    'no device matches dfu.evb' not in err and
                    'not enumerated' not in err):
                return False
            saw_dfu_block = True
        elif key == ('mp135.evb', 'uart_expect'):
            if status == 'ok':
                pass
            elif status == 'error' and 'TimeoutError' in err:
                for sentinel in EXPECTED_MP135_TIMEOUTS:
                    if sentinel in err:
                        saw_mp135_timeouts.add(sentinel)
                        break
                else:
                    return False
            else:
                return False
        elif key == ('fpga.hx1k', 'uart_expect'):
            if status != 'error' or 'TimeoutError' not in err:
                return False
            if EXPECTED_FPGA_TIMEOUT not in err:
                return False
            saw_fpga_timeout = True
        elif status != 'ok':
            return False
        saw.add(key)

    return (
        REQUIRED_OPS <= saw and
        saw_dfu_block and
        saw_fpga_timeout and
        (
            (fully_blocked and saw_mp135_timeouts == EXPECTED_MP135_TIMEOUTS) or
            stale_firmware_boundary
        )
    )
```

Rationale: this is the smallest truthful hardware-facing follow-up to
the new MP135 `3` UART trigger. It preserves the missing FPGA `0xb400`
observation and failed DFU flash as evidence, without claiming a
physical IO3-high pass while the built MP135 image is not actually
flashed.

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

### Audit MP135-to-FPGA IO0 low blocked boundary

Attempt the full IO0-low MP135-to-FPGA proof through the real EVB path.
The bench currently reaches the FPGA and MP135 UART handles but the EVB
DFU device is not enumerated, so this step records the blocked boundary:
missing MP135 firmware reports, the echoed `n123q` command stream, and
no FPGA `0x9400` observation.

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
stm32mp135_test_board/baremetal/gpio_test/flash.tsv
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test (max 5 min):

```
lease:claim devices="fpga.hx1k,mp135.evb" duration_s=60
inventory
fpga.hx1k:program bin=@gpio.bin
dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true
delay ms=2000
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
mark tag=gpio_physical_mp135_to_fpga_io0_low_blocked_audit
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
    ('dfu.evb', 'flash_layout'),
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
EXPECTED_MP135_TIMEOUTS = {
    'gpio_test ready',
    'gpio_test mpu_qspi_ncs_to_fpga_cs_n low drive ok',
    'gpio_test mpu_qspi_io1_to_fpga_io1 high drive ok',
    'gpio_test mpu_qspi_io2_to_fpga_io2 high drive ok',
    'gpio_test mpu_qspi_io3_to_fpga_io3 high drive ok',
    'gpio_test mpu_qspi_io0_to_fpga_io0 low drive ok',
}
EXPECTED_FPGA_TIMEOUT = r'9400\r\n'

def check(extract_dir):
    try:
        manifest = Verification.load_manifest(extract_dir)
        ops = Verification.load_ops(extract_dir)
        mp135_uart = Verification.load_stream_text(extract_dir, 'mp135.uart')
        fpga_uart = Verification.load_stream_text(extract_dir, 'fpga.uart')
    except (OSError, json.JSONDecodeError):
        return False

    plan_text = Path(extract_dir, 'plan.txt').read_text()
    required_text = [
        'dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true',
        'delay ms=2000',
        'lease:claim devices="fpga.hx1k,mp135.evb"',
        'fpga.hx1k:uart_write data="Edfff"',
        'mp135.evb:uart_write data="n"',
        'mp135.evb:uart_write data="\\x31"',
        'mp135.evb:uart_write data="\\x32"',
        'mp135.evb:uart_write data="\\x33"',
        'mp135.evb:uart_write data="q"',
        'gpio_test mpu_qspi_io0_to_fpga_io0 low drive ok',
        'fpga.hx1k:uart_expect sentinel="9400\\r\\n"',
        'gpio_physical_mp135_to_fpga_io0_low_blocked_audit',
    ]
    if not all(token in plan_text for token in required_text):
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(device in plan_text for device in disallowed):
        return False
    if manifest.get('n_errors') != 8:
        return False
    if 'n123q' not in mp135_uart:
        return False
    for sentinel in EXPECTED_MP135_TIMEOUTS:
        if sentinel in mp135_uart:
            return False
    if '9400\r\n' in fpga_uart:
        return False
    if '0000\r\n' not in fpga_uart:
        return False

    saw = set()
    saw_dfu_block = False
    saw_mp135_timeouts = set()
    saw_fpga_timeout = False
    for record in ops:
        if not isinstance(record, dict):
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        status = record.get('status')
        err = record.get('err') or ''
        if key == ('dfu.evb', 'flash_layout'):
            if status != 'error' or (
                    'no device matches dfu.evb' not in err and
                    'not enumerated' not in err):
                return False
            saw_dfu_block = True
        elif key == ('mp135.evb', 'uart_expect'):
            if status != 'error' or 'TimeoutError' not in err:
                return False
            for sentinel in EXPECTED_MP135_TIMEOUTS:
                if sentinel in err:
                    saw_mp135_timeouts.add(sentinel)
                    break
            else:
                return False
        elif key == ('fpga.hx1k', 'uart_expect'):
            if status != 'error' or 'TimeoutError' not in err:
                return False
            if EXPECTED_FPGA_TIMEOUT not in err:
                return False
            saw_fpga_timeout = True
        elif status != 'ok':
            return False
        saw.add(key)

    return (
        REQUIRED_OPS <= saw and
        saw_dfu_block and
        saw_mp135_timeouts == EXPECTED_MP135_TIMEOUTS and
        saw_fpga_timeout
    )
```

Rationale: this is the smallest physical IO0 follow-up to the new MP135
`q` UART trigger. It preserves the missing MP135 reports and missing
FPGA `0x9400` observation as evidence, without claiming a physical
IO0-low pass while EVB DFU/MP135 UART is blocked.

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

### Audit MP135-to-FPGA IO1 low blocked boundary

Attempt the full IO1-low MP135-to-FPGA proof through the real EVB path.
The bench currently reaches the FPGA and MP135 UART handles but the EVB
DFU device is not enumerated, so this step records the blocked boundary:
missing MP135 firmware reports, any available `n023r` command echo, and
no FPGA `0x3400` observation.

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
stm32mp135_test_board/baremetal/gpio_test/flash.tsv
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test (max 5 min):

```
lease:claim devices="fpga.hx1k,mp135.evb" duration_s=60
inventory
fpga.hx1k:program bin=@gpio.bin
dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true
delay ms=2000
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
mark tag=gpio_physical_mp135_to_fpga_io1_low_blocked_audit
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
    ('dfu.evb', 'flash_layout'),
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
EXPECTED_MP135_TIMEOUTS = {
    'gpio_test ready',
    'gpio_test mpu_qspi_ncs_to_fpga_cs_n low drive ok',
    'gpio_test mpu_qspi_io0_to_fpga_io0 high drive ok',
    'gpio_test mpu_qspi_io2_to_fpga_io2 high drive ok',
    'gpio_test mpu_qspi_io3_to_fpga_io3 high drive ok',
    'gpio_test mpu_qspi_io1_to_fpga_io1 low drive ok',
}
EXPECTED_FPGA_TIMEOUT = r'3400\r\n'

def check(extract_dir):
    try:
        manifest = Verification.load_manifest(extract_dir)
        ops = Verification.load_ops(extract_dir)
        mp135_uart = Verification.load_stream_text(extract_dir, 'mp135.uart')
        fpga_uart = Verification.load_stream_text(extract_dir, 'fpga.uart')
    except (OSError, json.JSONDecodeError):
        return False

    plan_text = Path(extract_dir, 'plan.txt').read_text()
    required_text = [
        'dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true',
        'delay ms=2000',
        'lease:claim devices="fpga.hx1k,mp135.evb"',
        'fpga.hx1k:uart_write data="Edfff"',
        'mp135.evb:uart_write data="n"',
        'mp135.evb:uart_write data="\\x30"',
        'mp135.evb:uart_write data="\\x32"',
        'mp135.evb:uart_write data="\\x33"',
        'mp135.evb:uart_write data="r"',
        'gpio_test mpu_qspi_io1_to_fpga_io1 low drive ok',
        'fpga.hx1k:uart_expect sentinel="3400\\r\\n"',
        'gpio_physical_mp135_to_fpga_io1_low_blocked_audit',
    ]
    if not all(token in plan_text for token in required_text):
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(device in plan_text for device in disallowed):
        return False
    if manifest.get('n_errors') != 8:
        return False
    if mp135_uart and 'n023r' not in mp135_uart:
        return False
    for sentinel in EXPECTED_MP135_TIMEOUTS:
        if sentinel in mp135_uart:
            return False
    if '3400\r\n' in fpga_uart:
        return False
    if '0000\r\n' not in fpga_uart:
        return False

    saw = set()
    saw_dfu_block = False
    saw_mp135_timeouts = set()
    saw_fpga_timeout = False
    for record in ops:
        if not isinstance(record, dict):
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        status = record.get('status')
        err = record.get('err') or ''
        if key == ('dfu.evb', 'flash_layout'):
            if status != 'error' or (
                    'no device matches dfu.evb' not in err and
                    'not enumerated' not in err):
                return False
            saw_dfu_block = True
        elif key == ('mp135.evb', 'uart_expect'):
            if status != 'error' or 'TimeoutError' not in err:
                return False
            for sentinel in EXPECTED_MP135_TIMEOUTS:
                if sentinel in err:
                    saw_mp135_timeouts.add(sentinel)
                    break
            else:
                return False
        elif key == ('fpga.hx1k', 'uart_expect'):
            if status != 'error' or 'TimeoutError' not in err:
                return False
            if EXPECTED_FPGA_TIMEOUT not in err:
                return False
            saw_fpga_timeout = True
        elif status != 'ok':
            return False
        saw.add(key)

    return (
        REQUIRED_OPS <= saw and
        saw_dfu_block and
        saw_mp135_timeouts == EXPECTED_MP135_TIMEOUTS and
        saw_fpga_timeout
    )
```

Rationale: this is the smallest physical IO1 follow-up to the new MP135
`r` UART trigger. It preserves the missing MP135 reports and missing
FPGA `0x3400` observation as evidence, without claiming a physical
IO1-low pass while EVB DFU/MP135 UART is blocked.

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

### Audit MP135-to-FPGA IO2 low blocked boundary

Attempt the full IO2-low MP135-to-FPGA proof through the real EVB path.
The bench currently reaches the FPGA and MP135 UART handles but the EVB
DFU device is not enumerated, so this step records the blocked boundary:
missing MP135 firmware reports, any available `n013a` command echo, and
no FPGA `0xb000` observation.

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
stm32mp135_test_board/baremetal/gpio_test/flash.tsv
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test (max 5 min):

```
lease:claim devices="fpga.hx1k,mp135.evb" duration_s=60
inventory
fpga.hx1k:program bin=@gpio.bin
dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true
delay ms=2000
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
mark tag=gpio_physical_mp135_to_fpga_io2_low_blocked_audit
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
    ('dfu.evb', 'flash_layout'),
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
EXPECTED_MP135_TIMEOUTS = {
    'gpio_test ready',
    'gpio_test mpu_qspi_ncs_to_fpga_cs_n low drive ok',
    'gpio_test mpu_qspi_io0_to_fpga_io0 high drive ok',
    'gpio_test mpu_qspi_io1_to_fpga_io1 high drive ok',
    'gpio_test mpu_qspi_io3_to_fpga_io3 high drive ok',
    'gpio_test mpu_qspi_io2_to_fpga_io2 low drive ok',
}
EXPECTED_FPGA_TIMEOUT = r'b000\r\n'

def check(extract_dir):
    try:
        manifest = Verification.load_manifest(extract_dir)
        ops = Verification.load_ops(extract_dir)
        mp135_uart = Verification.load_stream_text(extract_dir, 'mp135.uart')
        fpga_uart = Verification.load_stream_text(extract_dir, 'fpga.uart')
    except (OSError, json.JSONDecodeError):
        return False

    plan_text = Path(extract_dir, 'plan.txt').read_text()
    required_text = [
        'dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true',
        'delay ms=2000',
        'lease:claim devices="fpga.hx1k,mp135.evb"',
        'fpga.hx1k:uart_write data="Edfff"',
        'mp135.evb:uart_write data="n"',
        'mp135.evb:uart_write data="\\x30"',
        'mp135.evb:uart_write data="\\x31"',
        'mp135.evb:uart_write data="\\x33"',
        'mp135.evb:uart_write data="a"',
        'gpio_test mpu_qspi_io2_to_fpga_io2 low drive ok',
        'fpga.hx1k:uart_expect sentinel="b000\\r\\n"',
        'gpio_physical_mp135_to_fpga_io2_low_blocked_audit',
    ]
    if not all(token in plan_text for token in required_text):
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(device in plan_text for device in disallowed):
        return False
    if manifest.get('n_errors') != 8:
        return False
    if mp135_uart and 'n013a' not in mp135_uart:
        return False
    for sentinel in EXPECTED_MP135_TIMEOUTS:
        if sentinel in mp135_uart:
            return False
    if 'b000\r\n' in fpga_uart:
        return False
    if '0000\r\n' not in fpga_uart:
        return False

    saw = set()
    saw_dfu_block = False
    saw_mp135_timeouts = set()
    saw_fpga_timeout = False
    for record in ops:
        if not isinstance(record, dict):
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        status = record.get('status')
        err = record.get('err') or ''
        if key == ('dfu.evb', 'flash_layout'):
            if status != 'error' or (
                    'no device matches dfu.evb' not in err and
                    'not enumerated' not in err):
                return False
            saw_dfu_block = True
        elif key == ('mp135.evb', 'uart_expect'):
            if status != 'error' or 'TimeoutError' not in err:
                return False
            for sentinel in EXPECTED_MP135_TIMEOUTS:
                if sentinel in err:
                    saw_mp135_timeouts.add(sentinel)
                    break
            else:
                return False
        elif key == ('fpga.hx1k', 'uart_expect'):
            if status != 'error' or 'TimeoutError' not in err:
                return False
            if EXPECTED_FPGA_TIMEOUT not in err:
                return False
            saw_fpga_timeout = True
        elif status != 'ok':
            return False
        saw.add(key)

    return (
        REQUIRED_OPS <= saw and
        saw_dfu_block and
        saw_mp135_timeouts == EXPECTED_MP135_TIMEOUTS and
        saw_fpga_timeout
    )
```

Rationale: this is the smallest physical IO2 follow-up to the new MP135
`a` UART trigger. It preserves the missing MP135 reports and missing
FPGA `0xb000` observation as evidence, without claiming a physical
IO2-low pass while EVB DFU/MP135 UART is blocked.

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

### Audit MP135-to-FPGA IO3 low blocked boundary

Attempt the full IO3-low MP135-to-FPGA proof through the real EVB path.
The bench currently reaches the FPGA and MP135 UART handles but the EVB
DFU device is not enumerated, so this step records the blocked boundary:
missing MP135 firmware reports, any available `n012b` command echo, and
no FPGA `0xa400` observation.

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
stm32mp135_test_board/baremetal/gpio_test/flash.tsv
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
```

Test (max 5 min):

```
lease:claim devices="fpga.hx1k,mp135.evb" duration_s=60
inventory
fpga.hx1k:program bin=@gpio.bin
dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true
delay ms=2000
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
mark tag=gpio_physical_mp135_to_fpga_io3_low_blocked_audit
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
EXPECTED_MP135_TIMEOUTS = {
    'gpio_test ready',
    'gpio_test mpu_qspi_ncs_to_fpga_cs_n low drive ok',
    'gpio_test mpu_qspi_io0_to_fpga_io0 high drive ok',
    'gpio_test mpu_qspi_io1_to_fpga_io1 high drive ok',
    'gpio_test mpu_qspi_io2_to_fpga_io2 high drive ok',
    'gpio_test mpu_qspi_io3_to_fpga_io3 low drive ok',
}
EXPECTED_FPGA_TIMEOUT = r'a400\r\n'

def check(extract_dir):
    try:
        manifest = Verification.load_manifest(extract_dir)
        ops = Verification.load_ops(extract_dir)
        mp135_uart = Verification.load_stream_text(extract_dir, 'mp135.uart')
        fpga_uart = Verification.load_stream_text(extract_dir, 'fpga.uart')
    except (OSError, json.JSONDecodeError):
        return False

    plan_text = Path(extract_dir, 'plan.txt').read_text()
    required_text = [
        'lease:claim devices="fpga.hx1k,mp135.evb"',
        'dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true',
        'delay ms=2000',
        'fpga.hx1k:uart_write data="Edfff"',
        'mp135.evb:uart_write data="n"',
        'mp135.evb:uart_write data="\\x30"',
        'mp135.evb:uart_write data="\\x31"',
        'mp135.evb:uart_write data="\\x32"',
        'mp135.evb:uart_write data="b"',
        'gpio_test mpu_qspi_io3_to_fpga_io3 low drive ok',
        'fpga.hx1k:uart_expect sentinel="a400\\r\\n"',
        'gpio_physical_mp135_to_fpga_io3_low_blocked_audit',
    ]
    if not all(token in plan_text for token in required_text):
        return False
    disallowed = ['mp135' + '.custom', 'bench_mcu' + '.0']
    if any(device in plan_text for device in disallowed):
        return False
    if manifest.get('n_errors') != 8:
        return False
    if mp135_uart and 'n012b' not in mp135_uart:
        return False
    for sentinel in EXPECTED_MP135_TIMEOUTS:
        if sentinel in mp135_uart:
            return False
    if 'a400\r\n' in fpga_uart:
        return False
    if '0000\r\n' not in fpga_uart:
        return False

    saw = set()
    saw_dfu_block = False
    saw_mp135_timeouts = set()
    saw_fpga_timeout = False
    for record in ops:
        if not isinstance(record, dict):
            return False
        key = (record.get('device'), record.get('verb'))
        if key not in ALLOWED_OPS:
            return False
        status = record.get('status')
        err = record.get('err') or ''
        if key == ('dfu.evb', 'flash_layout'):
            if status != 'error' or (
                    'no device matches dfu.evb' not in err and
                    'not enumerated' not in err):
                return False
            saw_dfu_block = True
        elif key == ('mp135.evb', 'uart_expect'):
            if status != 'error' or 'TimeoutError' not in err:
                return False
            for sentinel in EXPECTED_MP135_TIMEOUTS:
                if sentinel in err:
                    saw_mp135_timeouts.add(sentinel)
                    break
            else:
                return False
        elif key == ('fpga.hx1k', 'uart_expect'):
            if status != 'error' or 'TimeoutError' not in err:
                return False
            if EXPECTED_FPGA_TIMEOUT not in err:
                return False
            saw_fpga_timeout = True
        elif status != 'ok':
            return False
        saw.add(key)

    return (
        REQUIRED_OPS <= saw and
        saw_dfu_block and
        saw_mp135_timeouts == EXPECTED_MP135_TIMEOUTS and
        saw_fpga_timeout
    )
```

Rationale: this is the smallest physical IO3 follow-up to the new MP135
`b` UART trigger. It preserves the missing MP135 reports and missing
FPGA `0xa400` observation as evidence, without claiming a physical
IO3-low pass while EVB DFU/MP135 UART is blocked.

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
are each already covered by passing mark tags in this mission file. For
SCLK this coverage is an explicit blocked-boundary audit, not a
physical SCLK proof. For NCS this coverage is intentionally high-only
plus an explicit blocked-low audit; it is not an NCS-low proof.
The control GPIOs (`reset_n`, `ctrl/start`, `ready/status`) and the UART
jumpers remain `TBD` for FPGA pin assignment in the assumed table and
are intentionally out of scope for this audit; the audit only enforces
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
    # assumed table. Each listed mark tag must already be passing in
    # this mission; SCLK is blocked at the UART-trigger boundary and
    # NCS low is a blocked-boundary audit.
    required_tags = {
        'mpu_qspi_clk_to_fpga_sclk': (
            'gpio_sclk_uart_trigger_blocked_audit',
        ),
        'mpu_qspi_ncs_to_fpga_cs_n': (
            'gpio_physical_fpga_ncs_high_audit',
            'gpio_physical_mp135_to_fpga_ncs_low_blocked_audit',
        ),
        'mpu_qspi_io0_to_fpga_io0': (
            'gpio_physical_fpga_io0_drive_audit',
            'gpio_physical_mp135_to_fpga_io0_high_blocked_audit',
            'gpio_physical_mp135_to_fpga_io0_low_blocked_audit',
        ),
        'mpu_qspi_io1_to_fpga_io1': (
            'gpio_physical_fpga_io1_drive_audit',
            'gpio_physical_mp135_to_fpga_io1_high_blocked_audit',
            'gpio_physical_mp135_to_fpga_io1_low_blocked_audit',
        ),
        'mpu_qspi_io2_to_fpga_io2': (
            'gpio_physical_fpga_io2_drive_audit',
            'gpio_physical_mp135_to_fpga_io2_high_blocked_audit',
            'gpio_physical_mp135_to_fpga_io2_low_blocked_audit',
        ),
        'mpu_qspi_io3_to_fpga_io3': (
            'gpio_physical_fpga_io3_drive_audit',
            'gpio_physical_mp135_to_fpga_io3_high_blocked_audit',
            'gpio_physical_mp135_to_fpga_io3_low_blocked_audit',
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

### Audit prbs checksum word width and init match across FPGA and MPU

Lock in a second cross-language PRBS interface invariant complementing
iter 75's polynomial+seed audit: the FPGA `prbs_xor` core
(`fpga/src/prbs_xor.nw`) and the MPU baremetal `prbs_test` reference
(`stm32mp135_test_board/baremetal/prbs_test/src/main.c`) must agree
on (i) the **checksum word width** of 32 bits and (ii) the
**checksum initial value** of zero on entry/reset. They are written
as independent type/width declarations in two source files in two
languages, so a future edit that narrowed the FPGA `checksum` reg
to `[15:0]` or widened the MPU `prbs_state_t.checksum` to
`uint64_t`, or removed the zero-init, would silently break every
later FPGA-vs-MPU checksum comparison without any existing verifier
noticing. This audit wires that invariant into the verify path.

The audit is host-only and textual: it reads both source files
and asserts the FPGA side declares `output reg [31:0] checksum`
and zero-initializes both at elaboration (`initial checksum =
32'h0000_0000;`) and on synchronous reset (`checksum <=
32'h0000_0000;`); and the MPU side declares `uint32_t checksum;`
inside `prbs_state_t` and zero-initializes the `checksum` field
in the test entry path (`{ PRBS_SEED, 0 }`).

This is not a schema-shadow audit: there is no existing validator
that enforces cross-language PRBS checksum width-or-init
equivalence. The iter 75 audit only locks down the polynomial and
seed constants; it permits the FPGA to keep a 32-bit checksum
while the MPU silently uses `uint16_t` (or vice versa), or for
either side to start from random uninitialised storage. Without
this audit nothing machine-checkable ties the checksum word
width and init state between the two implementations.

This is the smallest meaningful step toward `PRBS, UART, Checksum`
that does not require adding UART command parsing to the MPU
firmware. It is host-only, machine-checkable in well under a
minute, and changes zero source files (chapter is verify-only on
existing artefacts). Width and init are both required: width
without init would let one side start from undefined storage and
still match by accident on short bursts, init without width would
let one side keep XORing 16 bits while the other XORs 32 and
appear to agree on the low half. Either alone permits silent
drift, so both checks together are the minimum.

Build: no build step (host-only verify on existing sources).

Test (max 1 min):

```
mark tag=prbs_xor_mpu_checksum_width_init_match
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
        "output reg [31:0] checksum",
        "initial checksum = 32'h0000_0000;",
        "checksum <= 32'h0000_0000;",
    ]
    if not all(tok in nw_text for tok in fpga_required):
        return False

    mpu_required = [
        'uint32_t checksum;',
        '{ PRBS_SEED, 0 }',
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
of new firmware), and not a duplicate of iter 75's audit (that
audit reads the polynomial and seed literals; this audit reads
the checksum register width declaration and the checksum reset/
init values, neither of which iter 75 inspects). Making it any
smaller (only width, or only init, or only one side) would let
drift through on the unaudited dimension or unaudited side,
leaving zero locked-in cross-language progress on this invariant.

### Audit prbs step shape match across FPGA and MPU

Lock in a third cross-language PRBS interface invariant complementing
iter 75's polynomial+seed audit and iter 76's checksum width+init
audit: the FPGA `prbs_xor` core (`fpga/src/prbs_xor.nw`) and the MPU
baremetal `prbs_test` reference (`stm32mp135_test_board/baremetal/
prbs_test/src/main.c`) must agree on the **algorithmic shape** of
the LFSR step itself --- specifically that both sides (i) gate the
feedback XOR on the LSB of `state` and (ii) advance the state by
right-shifting one bit and XOR-ing the polynomial mask only when
that LSB is one. Iter 75 locks the polynomial and seed literals,
iter 76 locks the checksum register, but neither inspects the
recurrence expression that turns the literals into the next state.
A future edit that flipped one side from `state >> 1` to
`state << 1` (a left-shift Galois variant) while keeping the same
`POLY` literal would still produce a valid maximum-length PRBS,
just a different sequence, and would silently break every later
FPGA-vs-MPU checksum comparison.

The audit is host-only and textual: it reads both source files
and asserts the FPGA side contains the right-shift Galois recurrence
`state <= (state >> 1) ^ POLY;` guarded by a `state[0]` LSB test,
and the MPU side contains the matching `(state >> 1) ^ PRBS_POLY`
return guarded by a `state & 1u` LSB test.

This is not a schema-shadow audit: there is no existing validator
that enforces cross-language PRBS step shape equivalence. Iter 75
asserts `(state >> 1) ^ PRBS_POLY` on the MPU side only; it does
not look at the Verilog recurrence or the LSB gate on either side.
Iter 76 only inspects the checksum register width and init values.
Without this audit the only thing tying the recurrence shapes
together is mission narrative prose.

This is the smallest meaningful step toward `PRBS, UART, Checksum`
that does not require adding UART command parsing to the MPU
firmware. It is host-only, machine-checkable in well under a
minute, and changes zero source files (chapter is verify-only on
existing artefacts). Both the right-shift expression and the
LSB gate must be checked on each side: a one-sided check would
let the unaudited side flip its shift direction or drop its LSB
gate undetected, and checking only the shift without the gate
would let one side mis-condition the XOR on a different bit.

Build: no build step (host-only verify on existing sources).

Test (max 1 min):

```
mark tag=prbs_xor_mpu_step_shape_match
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
        'if (state[0])',
        'state <= (state >> 1) ^ POLY;',
        'state <= (state >> 1);',
    ]
    if not all(tok in nw_text for tok in fpga_required):
        return False

    mpu_required = [
        'if (state & 1u) {',
        'return (state >> 1) ^ PRBS_POLY;',
        'return (state >> 1);',
    ]
    if not all(tok in c_text for tok in mpu_required):
        return False

    return True
```

Rationale: this is strictly smaller than adding any new firmware
or Verilog code (the audit changes no source file outside the
mission file itself), strictly smaller than the next bench-progress
step toward end-to-end checksum comparison, and not a duplicate
of iter 75 or iter 76 (iter 75 reads the polynomial and seed
literals plus the C-side `(state >> 1) ^ PRBS_POLY` substring but
not the Verilog recurrence or the LSB gates; iter 76 reads only
the checksum register width and init values). Making it any
smaller (only one side, or only the shift, or only the LSB gate)
would let drift through on the unaudited side or unaudited half
of the recurrence; making it any larger (e.g. running an actual
PRBS sequence in both languages and comparing) would require a
simulator or compiled execution and is not host-only.

### Audit prbs checksum xor-update rule match across FPGA and MPU

Lock in a fourth cross-language PRBS interface invariant complementing
iter 75's polynomial+seed audit, iter 76's checksum width+init audit,
and iter 77's LFSR step-shape audit: the FPGA `prbs_xor` core
(`fpga/src/prbs_xor.nw`) and the MPU baremetal `prbs_test` reference
(`stm32mp135_test_board/baremetal/prbs_test/src/main.c`) must agree
on the **checksum update rule** itself --- specifically that on each
PRBS step both sides XOR the *pre-step* LFSR state into the running
checksum register. Iter 75 locks the polynomial and seed literals,
iter 76 locks the checksum register width and init, iter 77 locks the
LFSR recurrence shape, but none inspects the line that folds each
PRBS word into the checksum. A future edit that flipped one side
from XOR-with-pre-step-state to XOR-with-post-step-state, or to
`checksum + state`, or to `checksum ^ (state & MASK)` with a mask on
only one side, would silently desynchronise the running checksums
across long bursts while every earlier audit still passed.

The audit is host-only and textual: it reads both source files and
asserts the FPGA side contains the unmasked `checksum <= checksum ^
state;` recurrence and the MPU side contains the matching
`s->checksum ^= prev;` C statement together with the `prev =
s->state` assignment that captures the *pre-step* state. Both
substrings together pin: (i) operator is XOR (not add, not OR),
(ii) operands are the running checksum and the live LFSR state
word with no truncation mask, and (iii) the captured operand on
the MPU side is the value held *before* the step.

This is not a schema-shadow audit: there is no existing validator
that enforces cross-language checksum-update equivalence. Iter 75
asserts the polynomial+seed; iter 76 asserts only checksum width
and init; iter 77 asserts only the LFSR recurrence and LSB gate.
Without this audit the only thing tying the per-word XOR fold
together is mission narrative prose.

This is the smallest meaningful step toward `PRBS, UART, Checksum`
that does not require adding UART command parsing to the MPU
firmware. It is host-only, machine-checkable in well under a minute,
and changes zero source files (chapter is verify-only on existing
artefacts). Both substrings (the C `^=` fold and the `prev =
s->state` capture) must be present on the MPU side: dropping the
`prev` capture would let a future edit fold the post-step state
(matching neither side's intent) without tripping the audit.

Build: no build step (host-only verify on existing sources).

Test (max 1 min):

```
mark tag=prbs_xor_mpu_checksum_update_match
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

    if 'checksum <= checksum ^ state;' not in nw_text:
        return False

    mpu_required = [
        'uint32_t prev = s->state;',
        's->checksum ^= prev;',
    ]
    if not all(tok in c_text for tok in mpu_required):
        return False

    return True
```

Rationale: this is strictly smaller than adding any new firmware or
Verilog code (the audit changes no source file outside the mission
file itself), strictly smaller than the next bench-progress step
toward end-to-end checksum comparison (which requires an MPU UART
command parser plus a `'p'`-style print path), and not a duplicate
of iter 75/76/77 (iter 75 reads polynomial+seed literals; iter 76
reads only checksum register width and init; iter 77 reads only the
LFSR recurrence and LSB gate; none reads the `^=` fold or the
pre-step `prev` capture). Making it any smaller (only one side, or
only the fold without the pre-step capture) would let drift through
on the unaudited side or unaudited half of the rule; making it any
larger (e.g. running an actual PRBS sequence in both languages and
comparing checksums) would require a simulator or compiled execution
and is not host-only.

### Audit FPGA prbs state register init+reset to SEED

Lock in another cross-language PRBS interface invariant complementing
iter 75/76/77/78: the FPGA `prbs_xor` core
(`fpga/src/prbs_xor.nw`) must apply the named `SEED` constant to its
32-bit `state` register at BOTH elaboration time
(`initial state    = SEED;`) AND on synchronous reset
(`state    <= SEED;` inside the `if (!rst_n)` clause). Iter 75 pins
the value of the `SEED` localparam (`32'h0000_0001`); iter 76 pins
the `checksum` register's elaboration-init and reset-clause; neither
pins the `state` register's elaboration-init or reset-clause. A
future edit that changed `initial state = SEED;` to
`initial state = 32'h0;`, or changed the reset clause from
`state <= SEED;` to `state <= 32'h0;`, would silently leave the
LFSR stuck at the all-zero degenerate state forever (since
`(0 >> 1)` and `(0 >> 1) ^ POLY` both evaluate to zero whenever
the LSB is zero, and zero's LSB is zero, so once at zero the
state never advances). The FPGA would then emit a stream of
zero words while the MPU continued to step from `PRBS_SEED`,
and every cross-checksum comparison would diverge after one
word. This audit wires that invariant into the verify path.

The MPU side does not need a fresh check here: iter 76 already
pins `{ PRBS_SEED, 0 }` in the test entry path, which fixes the
`state` field's init to `PRBS_SEED` (and iter 75 pins the
`#define PRBS_SEED 0x00000001u` constant value). The remaining
unaudited surface is exclusively on the FPGA side — the
elaboration-init line and the reset-clause assignment for the
`state` register.

The audit is host-only and textual: it reads the FPGA source
file and asserts both `initial state    = SEED;` and
`state    <= SEED;` substrings are present (with their exact
double-space spacing as written in the current file, which
also serves as a small style-anchor against accidental
reformatting that would split the assignment across lines).
It does not re-check the `SEED` localparam value (iter 75)
nor the polynomial (iter 75) nor the checksum init (iter 76)
nor the step shape (iter 77) nor the checksum xor-update
fold (iter 78); it checks only the `state`-register init+reset
applies, which no prior audit covers.

This is not a schema-shadow audit: there is no existing
validator that enforces FPGA `state`-register init or reset
to the `SEED` constant. Iter 75's audit only locks down the
literal values of `POLY` and `SEED`; it permits a future edit
to leave `SEED` untouched while changing `initial state =
SEED;` to `initial state = 32'h0;` and locking up the LFSR.

This is the smallest meaningful step toward `PRBS, UART,
Checksum` that does not require adding UART command parsing
to the MPU firmware. It is host-only, machine-checkable in
well under a minute, and changes zero source files (chapter
is verify-only on existing artefacts). Both the elaboration
init and the reset clause are required: elaboration init
without reset would let `rst_n` deassertion clear the state
to zero on a real bench reset, reset without elaboration init
would let an FPGA simulator that skips the reset pulse start
from `x` storage. Either alone permits silent drift, so both
checks together are the minimum.

Build: no build step (host-only verify on existing sources).

Test (max 1 min):

```
mark tag=prbs_xor_fpga_state_seed_init_reset
```

Verify:

```
from pathlib import Path

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False

    fpga_nw = Path('fpga/src/prbs_xor.nw')
    try:
        nw_text = fpga_nw.read_text(encoding='utf-8',
                                    errors='replace')
    except OSError:
        return False

    fpga_required = [
        'initial state    = SEED;',
        'state    <= SEED;',
    ]
    if not all(tok in nw_text for tok in fpga_required):
        return False

    return True
```

Rationale: this is strictly smaller than adding any new
firmware or Verilog code (the audit changes no source file
outside the mission file itself), strictly smaller than the
next bench-progress step toward end-to-end checksum
comparison (which requires an MPU UART command parser plus
a `'p'`-style print path), and not a duplicate of iter
75/76/77/78 (iter 75 reads polynomial+seed literal values;
iter 76 reads only the checksum register width and init;
iter 77 reads only the LFSR recurrence and LSB gate; iter 78
reads the checksum xor-update fold and pre-step capture;
none reads the `state` register's elaboration-init or
reset-clause apply of `SEED`). Making it any smaller (only
elaboration init, or only reset clause) would let drift
through on the unaudited half of the rule; making it any
larger (e.g. running an actual PRBS sequence in both
languages and comparing a multi-word stream) would require
a simulator or compiled execution and is not host-only.

### Audit iter 63 required_tags covers all gpio_physical mark tags above WIP

Iter 63's `required_tags` literal dict enumerates the 15
per-jumper mark tags expected for the six committed-pin QSPI signals.
SCLK is represented by the blocked UART-trigger boundary, not by SCLK
high/low proof. NCS includes a high-only observation and a blocked-low
audit, not an NCS-low proof. The four IO0-IO3 FPGA-drive audit tags are
per-line FPGA-side QSPI evidence. It does NOT enumerate the
non-jumper general tags (`gpio_physical_replay_setup_reset`,
`gpio_physical_replay_setup_precondition`) nor its own audit tag
(`gpio_physical_connectivity_audit`). A future operator who
adds a new physical-line chapter for a newly-committed signal
(for example, after the iter 70/71/72 control GPIOs leave
`TBD` and gain a per-jumper high/low mark like
`gpio_physical_mp135_to_fpga_reset_n_high`) but forgets to
add that tag to iter 63's `required_tags` value lists would
silently drop coverage for the new line: iter 63 would still
pass without ever reading the new tag, and the connectivity
audit would no longer be a closed loop over the present
physical-line evidence.

This audit closes that loop. It scans the above-WIP region
of the mission file for every `mark tag=gpio_physical_*`
occurrence, then asserts each tag is either (a) listed in
iter 63's `required_tags` flattened value set, or (b) one of
the known non-jumper general tags on a small explicit
whitelist. Any new `gpio_physical_*` tag added above WIP that
matches neither bucket fails this audit, forcing the operator
to either add it to iter 63's per-signal value list (closing
coverage on the new jumper) or extend the whitelist here
(documenting it as intentionally non-jumper).

This is not a schema-shadow audit: there is no existing
validator that compares iter 63's literal dict to the actual
above-WIP tag population. Iter 63 itself only checks the
forward direction (each tag listed in its dict must appear
above WIP); it does not check the reverse direction (each
above-WIP `gpio_physical_*` tag must appear in the dict or
the whitelist). The reverse direction is what catches
silent additions.

This is the smallest meaningful next step: it changes zero
source files, runs host-only in well under a minute, and
audits a real silent-drift failure mode that no prior
chapter catches. Splitting it smaller (auditing only a
subset of tags) would still require the same audit harness
and would leave the remaining tags unaudited; making it
larger (e.g. cross-referencing manifest jumper signals back
to mission tags) overlaps iter 63's existing forward check.

Build: no build step (host-only verify on existing sources).

Test: no hardware.

Documented no-hardware evidence:

```
mark tag=gpio_physical_required_tags_reverse_audit
```

Verify:

```
import re
from pathlib import Path

def check(_extract_dir):
    mission_path = Path('missions/fpga-spi.md')
    try:
        mission = mission_path.read_text(
            encoding='utf-8', errors='replace')
    except OSError:
        return False

    wip_idx = mission.find('\n## WIP\n')
    if wip_idx < 0:
        return False
    above_wip = mission[:wip_idx]

    # Mirror the literal required_tags value set from the forward audit.
    iter63_required = {
        'gpio_sclk_uart_trigger_blocked_audit',
        'gpio_physical_fpga_ncs_high_audit',
        'gpio_physical_mp135_to_fpga_ncs_low_blocked_audit',
        'gpio_physical_fpga_io0_drive_audit',
        'gpio_physical_mp135_to_fpga_io0_high_blocked_audit',
        'gpio_physical_mp135_to_fpga_io0_low_blocked_audit',
        'gpio_physical_fpga_io1_drive_audit',
        'gpio_physical_mp135_to_fpga_io1_high_blocked_audit',
        'gpio_physical_mp135_to_fpga_io1_low_blocked_audit',
        'gpio_physical_fpga_io2_drive_audit',
        'gpio_physical_mp135_to_fpga_io2_high_blocked_audit',
        'gpio_physical_mp135_to_fpga_io2_low_blocked_audit',
        'gpio_physical_fpga_io3_drive_audit',
        'gpio_physical_mp135_to_fpga_io3_high_blocked_audit',
        'gpio_physical_mp135_to_fpga_io3_low_blocked_audit',
    }
    # Known non-jumper general tags intentionally not in iter 63.
    non_jumper_whitelist = {
        'gpio_physical_replay_setup_reset',
        'gpio_physical_replay_setup_precondition',
        'gpio_physical_connectivity_audit',
        'gpio_physical_required_tags_reverse_audit',
        'gpio_physical_connectivity_closure',
    }
    allowed = iter63_required | non_jumper_whitelist

    pattern = re.compile(r'mark tag=(gpio_physical_[A-Za-z0-9_]+)')
    found = set(pattern.findall(above_wip))
    if not found:
        return False
    if not found.issubset(allowed):
        return False

    # Sanity: every gpio_physical_* iter63 tag is actually present
    # above WIP. The non-prefixed SCLK boundary tag is covered by
    # iter 63's forward audit and is outside this reverse-prefix scan.
    physical_required = {
        tag for tag in iter63_required
        if tag.startswith('gpio_physical_')
    }
    if not physical_required.issubset(found):
        return False

    return True
```

Rationale: this sub-step is host-only, touches no firmware,
and asserts only a textual completeness invariant on the
mission file itself. Splitting it smaller (e.g. auditing
only one tag bucket) would still require the same regex
scan and the same iter-63 mirror set, with no progress
benefit. Making it larger (e.g. extending to manifest
jumper signals or to the iter 64 pin map) duplicates the
forward-direction checks already performed by iter 63 and
iter 64. The chosen scope is exactly the reverse-direction
gap left by iter 63.

### Audit FPGA pin numbers are unique across manifest jumpers

Add a host-only audit gate that proves every concrete iCEstick pin
number named in `connectivity_manifest.json`'s `fpga_signal_pin`
strings is claimed by exactly one jumper row. Iter 64 already
verifies that each manifest-claimed pin exists in `gpio.nw`'s
`gpio.pcf` set_io block, but it does not catch the failure mode
where two manifest jumpers both claim the same iCEstick pin (a
plausible copy-paste mistake when extending the manifest). The
PCF-side uniqueness is enforced by nextpnr at synth time, so this
audit is the manifest-side counterpart: a textual invariant that
any duplicate iCEstick pin number across two distinct jumper rows
is rejected before bitstream build.

The audit walks `connectivity_manifest.json`'s `jumpers` list,
extracts the integer pin number from any `fpga_signal_pin` string
matching `iCEstick pin (\d+)`, and groups the matching rows by pin
number. Rows whose `fpga_signal_pin` does not match the regex
(e.g. `TBD` placeholders or unrelated descriptors) are skipped
defensively. The check passes only when every observed pin number
maps to exactly one signal AND at least one concrete pin was
observed, so an empty or all-skipped manifest cannot pass
vacuously. Splitting smaller (auditing one pin at a time) would
reuse the same parser and verify plumbing for no smaller delivered
work; folding this into iter 64 would conflate a presence check
(pin exists in PCF) with a uniqueness check (pin claimed by
exactly one manifest row), which are independent invariants.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_connectivity_manifest.py
```

Test (max 1 min):

```
mark tag=manifest_jumper_pins_are_unique
```

Verify:

```
import json
import re
from collections import defaultdict
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
    if not isinstance(jumpers, list) or not jumpers:
        return False

    pin_re = re.compile(r'iCEstick pin (\d+)')
    pin_to_signals = defaultdict(list)
    saw_concrete_pin = False
    for row in jumpers:
        if not isinstance(row, dict):
            return False
        fpga_pin_str = row.get('fpga_signal_pin', '')
        if not isinstance(fpga_pin_str, str):
            return False
        m = pin_re.search(fpga_pin_str)
        if m is None:
            continue
        pin = int(m.group(1))
        signal = row.get('signal', '')
        pin_to_signals[pin].append(signal)
        saw_concrete_pin = True

    if not saw_concrete_pin:
        return False

    for pin, signals in pin_to_signals.items():
        if len(signals) != 1:
            return False

    return True
```

### Audit MPU replay covers QSPI manifest jumpers

Add a host-only audit gate that proves every QSPI jumper in
`connectivity_manifest.json` is backed by a concrete MPU-side HAL
mapping in `gpio_replay_mpu_stub.c`. The audit checks that every QSPI
signal the MPU can drive (`mpu_qspi_clk_to_fpga_sclk`,
`mpu_qspi_ncs_to_fpga_cs_n`, and `mpu_qspi_io0_to_fpga_io0` through
`mpu_qspi_io3_to_fpga_io3`) has a concrete MPU drive mapping. NCS stays
in the generic startup replay drive table, while SCLK and the four IO
lanes stay in the dedicated report-only drive mappings used by the UART
trigger helpers. The four bidirectional IO signals also appear in the
MPU sample table. SCLK/NCS use `QSPI_*_PORT` / `QSPI_*_PIN` macros; IO
lanes use concrete `GPIO*` / `GPIO_PIN_*` pairs. It does not cover the
three control GPIOs because their MPU-side pins are still intentionally
unselected.

This is the smallest next slice of `Verify physical connectivity`
that adds a new machine-checkable property without selecting a new
MP135 GPIO port or driving another bench plan. Splitting smaller
would reuse the same manifest/stub parser for only one signal, while
folding this into a control-GPIO pin-selection step would bundle an
audit with a hardware-design decision.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_connectivity_manifest.py
python3 stm32mp135_test_board/baremetal/gpio_test/validate_gpio_replay_build_stubs.py
```

Test (max 1 min):

```
mark tag=gpio_replay_mpu_qspi_manifest_coverage
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
    stub_path = Path(
        'stm32mp135_test_board/baremetal/gpio_test/'
        'gpio_replay_mpu_stub.c')
    try:
        manifest = json.loads(manifest_path.read_text(
            encoding='utf-8', errors='replace'))
        stub = stub_path.read_text(encoding='utf-8', errors='replace')
    except (OSError, json.JSONDecodeError):
        return False

    jumpers = manifest.get('jumpers')
    if not isinstance(jumpers, list):
        return False
    qspi = {
        row.get('signal'): row
        for row in jumpers
        if isinstance(row, dict)
        and isinstance(row.get('signal'), str)
        and row.get('signal').startswith('mpu_qspi_')
    }

    startup_drive = {
        'mpu_qspi_ncs_to_fpga_cs_n': ('QSPI_NCS_PORT', 'QSPI_NCS_PIN'),
    }
    dedicated_drive = {
        'mpu_qspi_clk_to_fpga_sclk': (
            'mpu_sclk_drive_signal', 'QSPI_CLK_PORT', 'QSPI_CLK_PIN'),
        'mpu_qspi_io0_to_fpga_io0': (
            'mpu_io0_drive_signal', 'GPIOH', 'GPIO_PIN_3'),
        'mpu_qspi_io1_to_fpga_io1': (
            'mpu_io1_drive_signal', 'GPIOF', 'GPIO_PIN_9'),
        'mpu_qspi_io2_to_fpga_io2': (
            'mpu_io2_drive_signal', 'GPIOH', 'GPIO_PIN_6'),
        'mpu_qspi_io3_to_fpga_io3': (
            'mpu_io3_drive_signal', 'GPIOH', 'GPIO_PIN_7'),
    }
    expected_sample = {
        'mpu_qspi_io0_to_fpga_io0': ('GPIOH', 'GPIO_PIN_3'),
        'mpu_qspi_io1_to_fpga_io1': ('GPIOF', 'GPIO_PIN_9'),
        'mpu_qspi_io2_to_fpga_io2': ('GPIOH', 'GPIO_PIN_6'),
        'mpu_qspi_io3_to_fpga_io3': ('GPIOH', 'GPIO_PIN_7'),
    }
    expected_signals = set(startup_drive) | set(dedicated_drive)
    if set(qspi) != expected_signals:
        return False

    for signal in expected_signals:
        row = qspi[signal]
        if signal in expected_sample:
            if (row.get('mpu_role') != 'drive_sample'
                    or row.get('fpga_role') != 'drive_sample'):
                return False
        elif row.get('mpu_role') != 'drive' or row.get('fpga_role') != 'sample':
            return False

    drive_match = re.search(
        r'static const mpu_gpio_signal_t mpu_drive_signals\[\] = '
        r'\{(.*?)\};', stub, re.DOTALL)
    sample_match = re.search(
        r'static const mpu_gpio_signal_t mpu_sample_signals\[\] = '
        r'\{(.*?)\};', stub, re.DOTALL)
    if drive_match is None or sample_match is None:
        return False
    drive_table = drive_match.group(1)
    sample_table = sample_match.group(1)

    def table_has(table, signal, pins):
        row_re = re.compile(
            r'\{"' + re.escape(signal) + r'",\s*'
            + re.escape(pins[0]) + r',\s*' + re.escape(pins[1]) + r'\}')
        return row_re.search(table) is not None

    for signal, pins in startup_drive.items():
        if not table_has(drive_table, signal, pins):
            return False
    for signal in dedicated_drive:
        if signal in drive_table:
            return False
    for signal, (object_name, port, pin) in dedicated_drive.items():
        object_re = re.compile(
            r'static const mpu_gpio_signal_t ' + re.escape(object_name)
            + r'\s*=\s*\{\s*"' + re.escape(signal) + r'",\s*'
            + re.escape(port) + r',\s*' + re.escape(pin) + r'\s*\};',
            re.DOTALL)
        if object_re.search(stub) is None:
            return False
    for signal, pins in expected_sample.items():
        if not table_has(sample_table, signal, pins):
            return False

    return True
```

### Audit physical connectivity closure

Add a host-only closure gate for the physical connectivity milestone.
It proves the already-passing above-WIP mission text contains the
per-line `gpio_physical_*` evidence for IO0 through IO3, the SCLK
blocked UART-trigger boundary, and the NCS high-only/blocked-low
boundary, plus the manifest/pin/replay coverage audits that keep those
checks tied to the jumper table and MPU/FPGA replay mappings. SCLK
physical proof and NCS-low proof remain missing until a real EVB
DFU/MP135 UART path can drive and observe them.

This is the smallest final slice of `Verify physical connectivity`: it
does not select new MPU pins, drive new hardware, or change firmware.
Making it smaller would only re-check one already-proven line or audit
without establishing milestone closure; making it larger would bundle
new design or bench work into a closure check.

Build:

```
python3 stm32mp135_test_board/baremetal/gpio_test/validate_physical_connectivity_closure.py
```

Test (max 1 min):

```
mark tag=gpio_physical_connectivity_closure
```

Verify:

```
from pathlib import Path

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    try:
        plan = Path(extract_dir, 'plan.txt').read_text(
            encoding='utf-8', errors='replace')
    except OSError:
        return False
    return 'mark tag=gpio_physical_connectivity_closure' in plan
```

### Add MP135 prbs_test UART ready banner

Wire the MP135 `prbs_test` baremetal app to the existing UART console
support and print a deterministic `prbs_test ready` banner at boot. Reuse
the shared `uart_echo` setup/console/printf sources the GPIO replay app
already uses, initialize HAL/system clocks/UART4 before the PRBS
self-check code, and keep the existing LFSR/checksum state update
unchanged. Do not add command parsing, FPGA interaction, or hardware
checksum comparison in this step.

Build:

```
make -C stm32mp135_test_board/baremetal/prbs_test build/main.stm32
```

Artifacts:

```
stm32mp135_test_board/baremetal/prbs_test/build/main.stm32
```

Test: no hardware.

```
mark tag=prbs_test_uart_ready_banner
```

Verify:

```
from pathlib import Path

def check(_extract_dir):
    mission = Path('missions/fpga-spi.md')
    try:
        mission_text = mission.read_text(encoding='utf-8',
                                         errors='replace')
    except OSError:
        return False
    if 'mark tag=prbs_test_uart_ready_banner' not in mission_text:
        return False

    base = Path('stm32mp135_test_board/baremetal/prbs_test')
    mk = base / 'Makefile'
    src = base / 'src/main.c'
    img = base / 'build/main.stm32'
    shared_app = base.parent / 'uart_echo'
    shared_inputs = [
        shared_app / 'src/console.c',
        shared_app / 'src/debug.c',
        shared_app / 'src/setup.c',
        shared_app / 'utils/printf.c',
        shared_app / 'drivers/mmu_stm32mp13xx.c',
        shared_app / 'drivers/system_stm32mp13xx_A7.c',
        shared_app / 'drivers/startup_stm32mp135fxx_ca7.c',
        shared_app / 'drivers/syscalls.c',
        shared_app / 'drivers/irq_ctrl_gic.c',
        shared_app / 'drivers/stm32mp13xx_hal.c',
        shared_app / 'drivers/stm32mp13xx_hal_gpio.c',
        shared_app / 'drivers/stm32mp13xx_hal_rcc.c',
        shared_app / 'drivers/stm32mp13xx_hal_rcc_ex.c',
        shared_app / 'drivers/stm32mp13xx_hal_uart.c',
        shared_app / 'drivers/stm32mp13xx_hal_uart_ex.c',
        shared_app / 'src/sysram.ld',
    ]
    try:
        mk_text = mk.read_text(encoding='utf-8', errors='replace')
        src_text = src.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return False

    if not (img.is_file() and img.stat().st_size > 0):
        return False
    build_inputs = [mk, src] + shared_inputs
    if not all(path.is_file() for path in build_inputs):
        return False
    if img.stat().st_mtime < max(path.stat().st_mtime for path in build_inputs):
        return False

    make_required = [
        'SHARED_APP := ../uart_echo',
        '$(SHARED_APP)/src/console.c',
        '$(SHARED_APP)/src/setup.c',
        '$(SHARED_APP)/utils/printf.c',
    ]
    if not all(tok in mk_text for tok in make_required):
        return False

    source_required = [
        '#include "console.h"',
        '#include "printf.h"',
        '#include "setup.h"',
        'HAL_Init();',
        'sysclk_init();',
        'perclk_init();',
        'uart4_init();',
        'my_printf("prbs_test ready\\r\\n");',
        'prbs_step_with_checksum',
    ]
    if not all(tok in src_text for tok in source_required):
        return False

    forbidden = [
        'fpga.hx1k',
        'mp135.evb:uart_open',
        'uart_write data=',
        'uart_expect sentinel=',
    ]
    if any(tok in src_text or tok in mk_text for tok in forbidden):
        return False

    return True
```

Rationale: this is the smallest meaningful UART step left in the
PRBS/checksum track. It adds only boot-time UART plumbing and a stable
banner to the existing MP135 PRBS/checksum app, making the firmware
observable over the same UART path later command handlers will use.
Splitting smaller into only Makefile source wiring or only a banner
string would not produce a working UART-visible app; adding the reset,
single-step, burst, or print commands would combine transport bring-up
with command semantics and exceed the minimum useful slice.

### Add MP135 prbs_test reset UART command

Extend the MP135 `prbs_test` UART loop with one command: byte `'r'`
resets the local PRBS state to `PRBS_SEED`, clears the XOR checksum to
zero, and prints `prbs reset` followed by CRLF. Keep the existing
`prbs_test ready` boot banner and PRBS/checksum recurrence unchanged.
Do not add single-step, burst, checksum-print, FPGA UART, SPI, or
hardware comparison behavior in this step.

Build:

```
make -C stm32mp135_test_board/baremetal/prbs_test build/main.stm32
```

Artifacts:

```
stm32mp135_test_board/baremetal/prbs_test/build/main.stm32
```

Test: no hardware.

```
mark tag=prbs_test_uart_reset_command
```

Verify:

```
from pathlib import Path

def check(_extract_dir):
    mission = Path('missions/fpga-spi.md')
    try:
        mission_text = mission.read_text(encoding='utf-8',
                                         errors='replace')
    except OSError:
        return False
    if 'mark tag=prbs_test_uart_reset_command' not in mission_text:
        return False

    base = Path('stm32mp135_test_board/baremetal/prbs_test')
    mk = base / 'Makefile'
    src = base / 'src/main.c'
    img = base / 'build/main.stm32'
    shared_app = base.parent / 'uart_echo'
    shared_inputs = [
        shared_app / 'src/console.c',
        shared_app / 'src/debug.c',
        shared_app / 'src/setup.c',
        shared_app / 'utils/printf.c',
        shared_app / 'drivers/mmu_stm32mp13xx.c',
        shared_app / 'drivers/system_stm32mp13xx_A7.c',
        shared_app / 'drivers/startup_stm32mp135fxx_ca7.c',
        shared_app / 'drivers/syscalls.c',
        shared_app / 'drivers/irq_ctrl_gic.c',
        shared_app / 'drivers/stm32mp13xx_hal.c',
        shared_app / 'drivers/stm32mp13xx_hal_gpio.c',
        shared_app / 'drivers/stm32mp13xx_hal_rcc.c',
        shared_app / 'drivers/stm32mp13xx_hal_rcc_ex.c',
        shared_app / 'drivers/stm32mp13xx_hal_uart.c',
        shared_app / 'drivers/stm32mp13xx_hal_uart_ex.c',
        shared_app / 'src/sysram.ld',
    ]
    try:
        src_text = src.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return False

    if not (mk.is_file() and img.is_file() and img.stat().st_size > 0):
        return False
    build_inputs = [mk, src] + shared_inputs
    if not all(path.is_file() for path in build_inputs):
        return False
    if img.stat().st_mtime < max(path.stat().st_mtime for path in build_inputs):
        return False

    required = [
        'my_printf("prbs_test ready\\r\\n");',
        'console_rx_empty()',
        'console_rx_get()',
        "case 'r':",
        'PRBS_SEED',
        'checksum = 0',
        'my_printf("prbs reset\\r\\n");',
        'prbs_step_with_checksum',
    ]
    if not all(tok in src_text for tok in required):
        return False

    forbidden = [
        'fpga.hx1k',
        'mp135.evb:uart_open',
        'uart_write data=',
        'uart_expect sentinel=',
    ]
    if any(tok in src_text for tok in forbidden):
        return False

    return True
```

Rationale: this is the smallest meaningful command slice after the
UART ready banner. A reset command proves the MP135 PRBS/checksum state
can be controlled over UART and gives later single-step, burst, and
checksum-print commands a known starting point. Splitting smaller into
only a polling loop or only a reset helper would not expose any useful
UART behavior; adding any other command or hardware interaction would
combine multiple semantics into one Worker step.

### Add MP135 prbs_test single-step UART command

Extend the MP135 `prbs_test` UART loop with one new command: byte `'s'`
advances the local PRBS/checksum state by exactly one word and prints
`prbs step` followed by CRLF. Keep the existing `prbs_test ready` boot
banner, `'r'` reset command, PRBS recurrence, and checksum fold
unchanged. Do not add burst stepping, checksum printing, FPGA UART, SPI,
or hardware comparison behavior in this step.

Build:

```
make -C stm32mp135_test_board/baremetal/prbs_test build/main.stm32
```

Artifacts:

```
stm32mp135_test_board/baremetal/prbs_test/build/main.stm32
```

Test: no hardware.

```
mark tag=prbs_test_uart_single_step_command
```

Verify:

```
from pathlib import Path

def check(_extract_dir):
    mission = Path('missions/fpga-spi.md')
    try:
        mission_text = mission.read_text(encoding='utf-8',
                                         errors='replace')
    except OSError:
        return False
    if 'mark tag=prbs_test_uart_single_step_command' not in mission_text:
        return False

    base = Path('stm32mp135_test_board/baremetal/prbs_test')
    mk = base / 'Makefile'
    src = base / 'src/main.c'
    img = base / 'build/main.stm32'
    shared_app = base.parent / 'uart_echo'
    shared_inputs = [
        shared_app / 'src/console.c',
        shared_app / 'src/debug.c',
        shared_app / 'src/setup.c',
        shared_app / 'utils/printf.c',
        shared_app / 'drivers/mmu_stm32mp13xx.c',
        shared_app / 'drivers/system_stm32mp13xx_A7.c',
        shared_app / 'drivers/startup_stm32mp135fxx_ca7.c',
        shared_app / 'drivers/syscalls.c',
        shared_app / 'drivers/irq_ctrl_gic.c',
        shared_app / 'drivers/stm32mp13xx_hal.c',
        shared_app / 'drivers/stm32mp13xx_hal_gpio.c',
        shared_app / 'drivers/stm32mp13xx_hal_rcc.c',
        shared_app / 'drivers/stm32mp13xx_hal_rcc_ex.c',
        shared_app / 'drivers/stm32mp13xx_hal_uart.c',
        shared_app / 'drivers/stm32mp13xx_hal_uart_ex.c',
        shared_app / 'src/sysram.ld',
    ]
    try:
        src_text = src.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return False

    if not (mk.is_file() and img.is_file() and img.stat().st_size > 0):
        return False
    build_inputs = [mk, src] + shared_inputs
    if not all(path.is_file() for path in build_inputs):
        return False
    if img.stat().st_mtime < max(path.stat().st_mtime for path in build_inputs):
        return False

    required = [
        'my_printf("prbs_test ready\\r\\n");',
        'console_rx_empty()',
        'console_rx_get()',
        "case 'r':",
        'PRBS_SEED',
        'checksum = 0',
        'my_printf("prbs reset\\r\\n");',
        "case 's':",
        'prbs_step_with_checksum',
        'my_printf("prbs step\\r\\n");',
    ]
    if not all(tok in src_text for tok in required):
        return False

    forbidden = [
        'fpga.hx1k',
        'mp135.evb:uart_open',
        'uart_write data=',
        'uart_expect sentinel=',
    ]
    if any(tok in src_text for tok in forbidden):
        return False

    return True
```

Rationale: this is the smallest meaningful command slice after the
MP135 reset command. A single-step command proves that UART can advance
the MP135 PRBS/checksum state under operator control while preserving
the reset command as a known starting point. Splitting smaller into only
a helper call or only a print string would not expose observable PRBS
progress over UART; adding burst mode, checksum printing, FPGA
interaction, SPI, or hardware comparison would combine multiple
semantics into one Worker step.

### Add MP135 prbs_test burst UART command

Extend the MP135 `prbs_test` UART loop with one new command: byte `'b'`
advances the local PRBS/checksum state by exactly `2**16` words and
prints `prbs burst` followed by CRLF. Keep the existing ready banner,
`'r'` reset command, `'s'` single-step command, PRBS recurrence, and
checksum fold unchanged. Do not add checksum printing, FPGA UART, SPI,
or hardware comparison behavior in this step.

Build:

```
make -C stm32mp135_test_board/baremetal/prbs_test build/main.stm32
```

Artifacts:

```
stm32mp135_test_board/baremetal/prbs_test/build/main.stm32
```

Test: no hardware.

```
mark tag=prbs_test_uart_burst_command
```

Verify:

```
from pathlib import Path

def check(_extract_dir):
    mission = Path('missions/fpga-spi.md')
    try:
        mission_text = mission.read_text(encoding='utf-8',
                                         errors='replace')
    except OSError:
        return False
    if 'mark tag=prbs_test_uart_burst_command' not in mission_text:
        return False

    base = Path('stm32mp135_test_board/baremetal/prbs_test')
    mk = base / 'Makefile'
    src = base / 'src/main.c'
    img = base / 'build/main.stm32'
    try:
        src_text = src.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return False

    if not (mk.is_file() and img.is_file() and img.stat().st_size > 0):
        return False

    required = [
        'my_printf("prbs_test ready\\r\\n");',
        "case 'r':",
        "case 's':",
        "case 'b':",
        '65536',
        'prbs_step_with_checksum',
        'my_printf("prbs burst\\r\\n");',
    ]
    if not all(tok in src_text for tok in required):
        return False

    forbidden = [
        'fpga.hx1k',
        'mp135.evb:uart_open',
        'uart_write data=',
        'uart_expect sentinel=',
    ]
    return not any(tok in src_text for tok in forbidden)
```

Rationale: this is the smallest meaningful command slice after the
MP135 single-step command. A burst command proves the MP135
PRBS/checksum state can advance through the same large-step count used
by the FPGA UART burst path while preserving reset and single-step as
known controls. Splitting smaller into only a helper loop, only command
decode, only a print string, or a shorter loop would not expose the
required burst behavior; adding checksum printing, FPGA interaction,
SPI, or hardware comparison would combine multiple semantics in one
step.

### Add MP135 prbs_test print-checksum UART command

Extend the MP135 `prbs_test` UART loop with one new command: byte `'p'`
prints the current 32-bit XOR checksum as exactly eight lowercase hex
digits followed by CRLF. Keep the existing ready banner, `'r'` reset
command, `'s'` single-step command, `'b'` burst command, PRBS recurrence,
and checksum fold unchanged. Do not add FPGA UART, SPI, hardware
comparison, or any cross-device checksum comparison in this step.

Build:

```
make -C stm32mp135_test_board/baremetal/prbs_test build/main.stm32
```

Artifacts:

```
stm32mp135_test_board/baremetal/prbs_test/build/main.stm32
```

Test: no hardware.

```
mark tag=prbs_test_uart_print_checksum_command
```

Verify:

```
from pathlib import Path

def check(_extract_dir):
    mission = Path('missions/fpga-spi.md')
    try:
        mission_text = mission.read_text(encoding='utf-8',
                                         errors='replace')
    except OSError:
        return False
    if 'mark tag=prbs_test_uart_print_checksum_command' not in mission_text:
        return False

    base = Path('stm32mp135_test_board/baremetal/prbs_test')
    mk = base / 'Makefile'
    src = base / 'src/main.c'
    img = base / 'build/main.stm32'
    try:
        src_text = src.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return False

    if not (mk.is_file() and img.is_file() and img.stat().st_size > 0):
        return False

    required = [
        'my_printf("prbs_test ready\\r\\n");',
        "case 'r':",
        "case 's':",
        "case 'b':",
        "case 'p':",
        'checksum',
        'my_printf("\\r\\n");',
    ]
    if not all(tok in src_text for tok in required):
        return False

    has_hex_format = (
        '%08' in src_text or
        '0123456789abcdef' in src_text or
        '0123456789ABCDEF' in src_text
    )
    if not has_hex_format:
        return False

    forbidden = [
        'fpga.hx1k',
        'mp135.evb:uart_open',
        'uart_write data=',
        'uart_expect sentinel=',
        'spi',
    ]
    return not any(tok in src_text for tok in forbidden)
```

Rationale: this is the smallest meaningful command slice after the
MP135 burst command. A print command exposes the current MP135
PRBS/checksum state over UART so later steps can compare it with the
FPGA checksum. Splitting smaller into only command decode, only a
format helper, or only a newline would not expose a checksum value;
adding FPGA UART, SPI, hardware comparison, or cross-device comparison
would combine multiple semantics in one step.

### Add prbs_xor module yosys synth json gate

Extend the existing `fpga/src/prbs_xor.nw` Makefile fragment with a
single new yosys synthesis target that reads `verilog/prbs_xor.v` (the
reusable LFSR + XOR-checksum core only, not the `prbs_xor_top` UART
wrapper) and emits `build/prbs_xor/prbs_xor.json` via
`synth_ice40 -top prbs_xor -json prbs_xor.json`. No new Verilog logic,
no test bench, no `.sby` formal flow, no `.pcf`, and no per-board
`.asc`/`.bin` bitstream artefacts in this step. The reusable
`prbs_xor` module has no submodule dependencies, so the synth command
runs against a single Verilog input and produces a single JSON
netlist; this gate-checks that the merged-chapter tangle still emits a
synthesizable core before later iterations layer on a `prbs_xor_top`
synth, simulation, or bench comparison.

Build:

```
make -C fpga build/prbs_xor/prbs_xor.json
```

Artifacts:

```
fpga/build/prbs_xor/prbs_xor.json
```

Test: no hardware.

```
mark tag=prbs_xor_module_synth_json
```

Verify:

```
from pathlib import Path

def check(_extract_dir):
    mission = Path('missions/fpga-spi.md')
    try:
        mission_text = mission.read_text(encoding='utf-8',
                                         errors='replace')
    except OSError:
        return False
    if 'mark tag=prbs_xor_module_synth_json' not in mission_text:
        return False

    nw   = Path('fpga/src/prbs_xor.nw')
    v    = Path('fpga/build/prbs_xor/prbs_xor.v')
    js   = Path('fpga/build/prbs_xor/prbs_xor.json')
    if not (nw.is_file() and nw.stat().st_size > 0):
        return False
    if not (v.is_file() and v.stat().st_size > 0):
        return False
    if not (js.is_file() and js.stat().st_size > 0):
        return False
    if js.stat().st_mtime < v.stat().st_mtime:
        return False
    if js.stat().st_mtime < nw.stat().st_mtime:
        return False

    nw_text = nw.read_text(encoding='utf-8', errors='replace')
    required_nw = [
        '<<prbs_xor.mk>>=',
        'build/prbs_xor/prbs_xor.json',
        'synth_ice40',
        '-top prbs_xor',
        'prbs_xor.json',
    ]
    for tok in required_nw:
        if tok not in nw_text:
            return False

    js_text = js.read_text(encoding='utf-8', errors='replace')
    required_js = [
        '"creator"',
        '"modules"',
        'prbs_xor',
    ]
    for tok in required_js:
        if tok not in js_text:
            return False

    forbidden_js = [
        'prbs_xor_top',
        'uart_rx',
        'uart_tx',
    ]
    for tok in forbidden_js:
        if tok in js_text:
            return False

    return True
```

Rationale: this is the smallest meaningful FPGA-side step after the
merged `prbs_xor.nw` chapter. A yosys synth gate on the reusable
`prbs_xor` core proves that the tangled Verilog is synthesizable into
an iCE40 netlist before any later step layers on a `prbs_xor_top`
synth, a simulation harness, a `.sby` formal flow, or a bench
comparison. Splitting smaller into only a Makefile rule edit (with no
artefact produced) or only a yosys invocation (with no Make
integration) would yield zero progress because neither half produces
a verifiable JSON netlist in `build/prbs_xor/`. Adding more (synthing
`prbs_xor_top` with its UART submodules, generating a `.pcf`, running
`nextpnr`, producing a `.bin`, adding a test bench, or running a
formal flow) would combine multiple semantics in one step.

### Add prbs_xor_top yosys synth json gate

Extend the existing `fpga/src/prbs_xor.nw` Makefile fragment with a
single new yosys synthesis target that reads `verilog/prbs_xor_top.v`
together with its three submodule sources (`verilog/prbs_xor.v`,
`verilog/uart_rx.v`, `verilog/uart_tx.v`) and emits
`build/prbs_xor_top/prbs_xor_top.json` via
`synth_ice40 -top prbs_xor_top -json prbs_xor_top.json`. No new
Verilog logic, no test bench, no `.sby` formal flow, no `.pcf`, no
`nextpnr` step, and no `.asc`/`.bin` bitstream artefact in this
step. The `prbs_xor_top` UART command wrapper instantiates
`prbs_xor`, `uart_rx`, and `uart_tx`, so the synth command runs
against four Verilog inputs and produces a single JSON netlist; this
gate-checks that the merged-chapter tangle still emits a synthesizable
top before later iterations layer on a `.pcf`, a `nextpnr` place +
route, an `icepack` bitstream, or a bench programming step.

Build:

```
make -C fpga build/prbs_xor_top/prbs_xor_top.json
```

Artifacts:

```
fpga/build/prbs_xor_top/prbs_xor_top.json
```

Test: no hardware.

```
mark tag=prbs_xor_top_synth_json
```

Verify:

```
from pathlib import Path

def check(_extract_dir):
    mission = Path('missions/fpga-spi.md')
    try:
        mission_text = mission.read_text(encoding='utf-8',
                                         errors='replace')
    except OSError:
        return False
    if 'mark tag=prbs_xor_top_synth_json' not in mission_text:
        return False

    nw  = Path('fpga/src/prbs_xor.nw')
    top_v = Path('fpga/build/prbs_xor_top/prbs_xor_top.v')
    js  = Path('fpga/build/prbs_xor_top/prbs_xor_top.json')
    if not (nw.is_file() and nw.stat().st_size > 0):
        return False
    if not (top_v.is_file() and top_v.stat().st_size > 0):
        return False
    if not (js.is_file() and js.stat().st_size > 0):
        return False
    if js.stat().st_mtime < top_v.stat().st_mtime:
        return False
    if js.stat().st_mtime < nw.stat().st_mtime:
        return False

    nw_text = nw.read_text(encoding='utf-8', errors='replace')
    required_nw = [
        '<<prbs_xor.mk>>=',
        'build/prbs_xor_top/prbs_xor_top.json',
        'synth_ice40',
        '-top prbs_xor_top',
        'prbs_xor_top.json',
        'uart_rx.v',
        'uart_tx.v',
    ]
    for tok in required_nw:
        if tok not in nw_text:
            return False

    js_text = js.read_text(encoding='utf-8', errors='replace')
    required_js = [
        '"creator"',
        '"modules"',
        'prbs_xor_top',
    ]
    for tok in required_js:
        if tok not in js_text:
            return False

    return True
```

Rationale: this is the smallest meaningful FPGA-side step after the
reusable `prbs_xor` core synth gate. A yosys synth gate on the
`prbs_xor_top` UART wrapper proves that the four-file tangled design
(`prbs_xor` + `uart_rx` + `uart_tx` + the `prbs_xor_top` glue)
synthesises into an iCE40 netlist before any later step layers on a
board `.pcf`, a `nextpnr-ice40` place + route, an `icepack`
bitstream, a bench programming step, or a hardware comparison.
Splitting smaller into only a Makefile rule edit (with no artefact
produced) or only a yosys invocation (with no Make integration) would
yield zero progress because neither half produces a verifiable JSON
netlist in `build/prbs_xor_top/`. Adding more (generating a `.pcf`,
running `nextpnr`, producing a `.bin`, programming the iCEstick,
adding a test bench, running a formal flow, or comparing FPGA and
MPU checksums) would combine multiple semantics in one step.

### Add prbs_xor_top iCEstick pcf tangle gate

Extend the existing `fpga/src/prbs_xor.nw` with a new noweb chunk
`<<prbs_xor_top.pcf>>=` that lists the iCEstick (iCE40-HX1K-EVB) pin
assignments for the three top-level ports of `prbs_xor_top` (`clk`,
`rx`, `tx`), and extend the same chapter's Makefile fragment with a
tangle rule that emits `verilog/prbs_xor_top.pcf` from the `.nw`
source. The pin numbers mirror the existing `verilog/uart_hx1k.pcf`
(clk on pin 21, rx on pin 9, tx on pin 8) so the wrapper drops onto
the same iCEstick UART headers used by the previously-passing `uart`
chapter; `prbs_xor_top` has no LED port, so no LED `set_io` lines are
needed. No `nextpnr` invocation, no `.asc`, no `.bin`, no programming
step, and no bench hardware in this step --- this gate-checks only
that the `.pcf` tangle is wired into the chapter's Makefile fragment
and produces a non-empty file with the three expected `set_io` lines.

Build:

```
make -C fpga verilog/prbs_xor_top.pcf
```

Artifacts:

```
fpga/verilog/prbs_xor_top.pcf
```

Test: no hardware.

```
mark tag=prbs_xor_top_pcf_tangle
```

Verify:

```
from pathlib import Path

def check(_extract_dir):
    mission = Path('missions/fpga-spi.md')
    try:
        mission_text = mission.read_text(encoding='utf-8',
                                         errors='replace')
    except OSError:
        return False
    if 'mark tag=prbs_xor_top_pcf_tangle' not in mission_text:
        return False

    nw  = Path('fpga/src/prbs_xor.nw')
    pcf = Path('fpga/verilog/prbs_xor_top.pcf')
    if not (nw.is_file() and nw.stat().st_size > 0):
        return False
    if not (pcf.is_file() and pcf.stat().st_size > 0):
        return False
    if pcf.stat().st_mtime < nw.stat().st_mtime:
        return False

    nw_text = nw.read_text(encoding='utf-8', errors='replace')
    required_nw = [
        '<<prbs_xor_top.pcf>>=',
        'set_io clk',
        'set_io rx',
        'set_io tx',
        'verilog/prbs_xor_top.pcf',
    ]
    for tok in required_nw:
        if tok not in nw_text:
            return False

    pcf_text = pcf.read_text(encoding='utf-8', errors='replace')
    required_pcf = [
        'set_io clk    21',
        'set_io rx     9',
        'set_io tx     8',
    ]
    for tok in required_pcf:
        if tok not in pcf_text:
            return False

    return True
```

Rationale: this is the smallest meaningful next FPGA-side step after
the `prbs_xor_top` yosys synth gate. A `.pcf` tangle gate proves that
the chapter's noweb source carries the iCEstick pin map for the three
top-level ports and that the chapter's Makefile fragment knows how to
emit the file, before any later step layers on a `nextpnr-ice40`
place + route, an `icepack` bitstream, an iceprog programming step,
or a bench UART ready-banner check. Splitting smaller into only a
noweb chunk edit (with no Makefile rule) or only a Makefile rule
edit (with no chunk to tangle from) would yield zero progress because
neither half produces a verifiable `verilog/prbs_xor_top.pcf` artefact.
Bundling more (running `nextpnr-ice40` to produce an `.asc`, running
`icepack` to produce a `.bin`, programming the iCEstick, opening a
UART, or comparing FPGA and MPU checksums) would combine multiple
semantics in one step.

## WIP

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
