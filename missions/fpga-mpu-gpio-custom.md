# FPGA <-> custom MP135 GPIO connectivity discovery (hx8k)

Discover which iCE40-HX8K-B-EVN ball each STM32MP135 SPI/QUADSPI pin on
the custom board's header J503 is wired to. The MPU firmware
(`baremetal/gpio_test`, built `BOARD=custom`) drives one of its 22
SPI/QUADSPI pins low at a time; the FPGA `mpu_probe` bitstream samples
every bonded CT256 ball (all held at their weak internal pull-up, so a
released ball reads 1) and returns the full vector as a hex line on each
`S` snapshot. The single ball that drops to 0 names the connection.

This mission DISCOVERS connections and prints them; it does not require
any particular pin to be wired (a missing connection is reported, not a
failure). The custom SPI mission consumes the discovered QUADSPI ball
assignments. The eval-board `fpga-mpu-gpio.md` mission is unchanged.

### Discover MP135 SPI/QUADSPI -> hx8k connectivity

Build the FPGA sampler bitstream and the custom-board GPIO firmware.
`tangle`/`weave` live in `~/.cargo/bin`; `gpio_test clean` is required
because the EVB and custom builds share `build/`.

Build:

```
PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH" make -C fpga build/mpu_probe/hx8k/mpu_probe.bin
make -C stm32mp135_test_board/baremetal/gpio_test clean
make -C stm32mp135_test_board/baremetal/gpio_test BOARD=custom build/main.stm32
```

Artifacts:

```
fpga/build/mpu_probe/hx8k/mpu_probe.bin
fpga/verilog/mpu_probe_hx8k.pcf
stm32mp135_test_board/baremetal/gpio_test/build/main.stm32
stm32mp135_test_board/baremetal/gpio_test/flash.tsv
```

Test (max 3 min):

```
fpga.hx8k:program bin=@mpu_probe.bin
bench_mcu.0:reset_dut2
delay ms=2000
dfu.custom:flash_layout layout=@flash.tsv no_reconnect=true
fpga.hx8k:uart_open
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="R"
mp135.custom:uart_expect sentinel="gpio_test release all ok" timeout_ms=8000
fpga.hx8k:uart_write data="?"
delay ms=200
mp135.custom:uart_write data="R"
delay ms=100
fpga.hx8k:uart_write data="S"
delay ms=150
mp135.custom:uart_write data="R"
delay ms=40
mp135.custom:uart_write data="D00L"
delay ms=80
fpga.hx8k:uart_write data="S"
delay ms=150
mp135.custom:uart_write data="R"
delay ms=40
mp135.custom:uart_write data="D01L"
delay ms=80
fpga.hx8k:uart_write data="S"
delay ms=150
mp135.custom:uart_write data="R"
delay ms=40
mp135.custom:uart_write data="D02L"
delay ms=80
fpga.hx8k:uart_write data="S"
delay ms=150
mp135.custom:uart_write data="R"
delay ms=40
mp135.custom:uart_write data="D03L"
delay ms=80
fpga.hx8k:uart_write data="S"
delay ms=150
mp135.custom:uart_write data="R"
delay ms=40
mp135.custom:uart_write data="D04L"
delay ms=80
fpga.hx8k:uart_write data="S"
delay ms=150
mp135.custom:uart_write data="R"
delay ms=40
mp135.custom:uart_write data="D05L"
delay ms=80
fpga.hx8k:uart_write data="S"
delay ms=150
mp135.custom:uart_write data="R"
delay ms=40
mp135.custom:uart_write data="D06L"
delay ms=80
fpga.hx8k:uart_write data="S"
delay ms=150
mp135.custom:uart_write data="R"
delay ms=40
mp135.custom:uart_write data="D07L"
delay ms=80
fpga.hx8k:uart_write data="S"
delay ms=150
mp135.custom:uart_write data="R"
delay ms=40
mp135.custom:uart_write data="D08L"
delay ms=80
fpga.hx8k:uart_write data="S"
delay ms=150
mp135.custom:uart_write data="R"
delay ms=40
mp135.custom:uart_write data="D09L"
delay ms=80
fpga.hx8k:uart_write data="S"
delay ms=150
mp135.custom:uart_write data="R"
delay ms=40
mp135.custom:uart_write data="D0AL"
delay ms=80
fpga.hx8k:uart_write data="S"
delay ms=150
mp135.custom:uart_write data="R"
delay ms=40
mp135.custom:uart_write data="D0BL"
delay ms=80
fpga.hx8k:uart_write data="S"
delay ms=150
mp135.custom:uart_write data="R"
delay ms=40
mp135.custom:uart_write data="D0CL"
delay ms=80
fpga.hx8k:uart_write data="S"
delay ms=150
mp135.custom:uart_write data="R"
delay ms=40
mp135.custom:uart_write data="D0DL"
delay ms=80
fpga.hx8k:uart_write data="S"
delay ms=150
mp135.custom:uart_write data="R"
delay ms=40
mp135.custom:uart_write data="D0EL"
delay ms=80
fpga.hx8k:uart_write data="S"
delay ms=150
mp135.custom:uart_write data="R"
delay ms=40
mp135.custom:uart_write data="D0FL"
delay ms=80
fpga.hx8k:uart_write data="S"
delay ms=150
mp135.custom:uart_write data="R"
delay ms=40
mp135.custom:uart_write data="D10L"
delay ms=80
fpga.hx8k:uart_write data="S"
delay ms=150
mp135.custom:uart_write data="R"
delay ms=40
mp135.custom:uart_write data="D11L"
delay ms=80
fpga.hx8k:uart_write data="S"
delay ms=150
mp135.custom:uart_write data="R"
delay ms=40
mp135.custom:uart_write data="D12L"
delay ms=80
fpga.hx8k:uart_write data="S"
delay ms=150
mp135.custom:uart_write data="R"
delay ms=40
mp135.custom:uart_write data="D13L"
delay ms=80
fpga.hx8k:uart_write data="S"
delay ms=150
mp135.custom:uart_write data="R"
delay ms=40
mp135.custom:uart_write data="D14L"
delay ms=80
fpga.hx8k:uart_write data="S"
delay ms=150
mp135.custom:uart_write data="R"
delay ms=40
mp135.custom:uart_write data="D15L"
delay ms=80
fpga.hx8k:uart_write data="S"
delay ms=150
mp135.custom:uart_close
fpga.hx8k:uart_close
mark tag=mpu_gpio_discovery
```

Verify:

```
import re

def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    mpu = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    fpga = Verification.load_stream(
        extract_dir, 'fpga.uart').decode('utf-8', 'replace')

    # bit -> ball map straight from the tangled pcf artifact.
    pcf = open(artifacts['mpu_probe_hx8k.pcf']).read()
    bit2ball = {int(m.group(1)): m.group(2)
                for m in re.finditer(r'set_io\s+pins\[(\d+)\]\s+(\S+)', pcf)}
    npins = len(bit2ball)

    # Ordered signals the MPU actually drove low, and the snapshot frames
    # the FPGA returned (51 hex nibbles = 203 balls + 1 pad bit, MSB-first).
    names = re.findall(r'gpio_test drive (\S+) low ok', mpu)
    frames = [int(h, 16) for h in re.findall(r'([0-9a-fA-F]{51})\r?\n', fpga)]

    print('\nMP135->hx8k discovery: %d driven signals, %d frames, %d balls'
          % (len(names), len(frames), npins))
    if not names or len(frames) < len(names) + 1:
        # discover-but-not-require: report and still pass if the chain ran.
        return Verification.op_succeeded(
            Verification.load_ops(extract_dir), 'fpga.hx8k', 'program')

    baseline = frames[0]
    base_ones = {i for i in range(npins) if (baseline >> i) & 1}

    found = {}
    lines = ['', 'DISCOVERED MP135 -> hx8k CONNECTIONS', '-' * 44]
    for j, name in enumerate(names):
        v = frames[j + 1]
        cand = [i for i in base_ones if not ((v >> i) & 1)]
        if len(cand) == 1:
            found[name] = bit2ball[cand[0]]
            lines.append('  %-12s -> %s  (bit %d)' % (name, found[name], cand[0]))
        else:
            lines.append('  %-12s -> none/ambiguous (%d candidates)'
                         % (name, len(cand)))
    lines.append('-' * 44)
    lines.append('  resolved %d / %d' % (len(found), len(names)))
    print('\n'.join(lines))

    # Discovery is informational; the mission does not require every pin to
    # be wired. Pass as long as the sweep ran end to end.
    return True

```
