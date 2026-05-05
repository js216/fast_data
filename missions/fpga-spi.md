# FPGA -> MP135 QSPI bring-up

Demonstrate FPGA-to-STM32MP135 QSPI streaming at increasing wall rate
with zero bit errors. Each section programs an iCEstick bitstream that
acts as the QSPI slave, boots an MP135 EVB firmware over DFU+UART that
issues the host-side QSPI master commands, captures the firmware's
summary line, and asserts that firsterr=-1 plus the wall-rate floor for
that mode. The headline mission target is the final section: 1 GiB
memory-mapped quad transfer at >=400 Mbps with bit-perfect transport.

The host firmware (`main.stm32`) and flash layout (`flash.tsv`) come
from `stm32mp135_test_board/baremetal/qspi/`; the per-section iCEstick
bitstream is the only artefact that varies. Every section starts cold:
program FPGA, reset MP135, DFU-flash, UART-open, kick the prompt, run.

## WIP

### 1-lane stream, 32 MiB, >=100 Mbps

Programs `spi_1lane.bin` on the iCEstick (raw 1-lane streaming slave),
boots the MP135 firmware, sets prescaler `p 5 1` (108.7 MHz wall-rate),
enables auto-consume `a 1`, and runs the auto-consume streaming command
`A 33554432 0 1` for 32 MiB. Verifier parses the firmware's `stream
<bytes> B 1lane in <ms> ms, <Mbps> Mbps, ..., firsterr=<n>` summary and
asserts firsterr=-1 plus effective Mbps >= 100.

Build:

```
make -C fpga build/spi/spi_1lane.bin
make -C stm32mp135_test_board/baremetal/qspi -j$(nproc)
```

Artifacts:

```
fpga/build/spi/spi_1lane.bin
stm32mp135_test_board/baremetal/qspi/build/main.stm32
stm32mp135_test_board/baremetal/qspi/flash.tsv
```

Test (max 5 min):

```
fpga.hx1k:program bin=@spi_1lane.bin
bench_mcu:reset_dut
delay ms=2500
dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true
mp135.evb:uart_open
mp135.evb:uart_expect sentinel="JEDEC ID:" timeout_ms=10000
delay ms=300
mp135.evb:uart_write data="p 5 1\r"
delay ms=100
mp135.evb:uart_write data="a 1\r"
mp135.evb:uart_expect sentinel="auto=on" timeout_ms=3000
mp135.evb:uart_write data="A 33554432 0 1\r"
mp135.evb:uart_expect sentinel="stream_xfer 33554432 B" timeout_ms=60000
mp135.evb:uart_expect sentinel=", firsterr=-1" timeout_ms=15000
mp135.evb:uart_close
mark tag=spi_1lane_done
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(
        extract_dir, 'mp135.uart', encoding='utf-8')
    pat = (r'stream\s+33554432\s+B\s+1lane\s+in\s+\d+\s+ms,\s+'
           r'(\d+\.\d+)\s+Mbps,[^\n]*firsterr=(-?\d+)')
    last = None
    for m in re.finditer(pat, text):
        last = m
    if last is None:
        return False
    mbps = float(last.group(1))
    firsterr = int(last.group(2))
    return firsterr == -1 and mbps >= 100.0
```

### Quad stream, 16 MiB twin-DDR, >=200 Mbps

Programs `spi_quad.bin` (raw 4-lane streaming slave), boots the MP135
firmware, sets `p 3 0` (164 MHz SCLK), and runs the twin-DDR command
`T 16777216`: two consecutive `qspi_mdma_read` reads into ping-pong
DDR slots followed by a byte-compare. firsterr=-1 means pass-1 == pass-2
byte-for-byte. Verifier parses the `twin <bytes> B quad raw pass1=<ms>
ms ... firsterr=<n>` summary, computes pass1 rate from the firmware-
reported pass1 ms (less noisy than the wall rate which includes UART
overhead), and asserts firsterr=-1 plus pass1_rate >= 200 Mbps.

Build:

```
make -C fpga build/spi/spi_quad.bin
make -C stm32mp135_test_board/baremetal/qspi -j$(nproc)
```

Artifacts:

```
fpga/build/spi/spi_quad.bin
stm32mp135_test_board/baremetal/qspi/build/main.stm32
stm32mp135_test_board/baremetal/qspi/flash.tsv
```

Test (max 5 min):

```
fpga.hx1k:program bin=@spi_quad.bin
bench_mcu:reset_dut
delay ms=2500
dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true
mp135.evb:uart_open
mp135.evb:uart_expect sentinel="JEDEC ID:" timeout_ms=10000
delay ms=300
mp135.evb:uart_write data="p 3 0\r"
delay ms=200
mp135.evb:uart_write data="T 16777216\r"
mp135.evb:uart_expect sentinel="twin 16777216 B quad raw" timeout_ms=180000
mp135.evb:uart_close
mark tag=spi_quad_done
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(
        extract_dir, 'mp135.uart', encoding='utf-8')
    m = re.search(
        r'twin\s+16777216\s+B\s+quad\s+raw[^\n]*'
        r'pass1=(\d+)\s+ms[^\n]*firsterr=(-?\d+)', text)
    if not m:
        return False
    pass1_ms = int(m.group(1))
    firsterr = int(m.group(2))
    if pass1_ms <= 0:
        return False
    pass1_rate = (16777216 * 8.0) / (pass1_ms * 1000.0)
    return firsterr == -1 and pass1_rate >= 200.0
```

### Memory-mapped quad, 1 GiB, >=400 Mbps with bit-perfect transport

The mission target. Programs the JEDEC slave (`jedec.bin`) which
implements 0x6B Quad Output Read with an address-deterministic byte
pattern (byte K returns `(start_addr+K) & 0xff`). Boots the MP135
firmware in memory-mapped mode (FMODE=11) so the QUADSPI peripheral
autonomously refills its prefetch buffer in response to AHB reads from
the `QSPI_MM_BASE` window, lifting the per-word AXI handshake ceiling
that bounds the indirect-MDMA path at ~337 Mbps quad. Issues the 1 GiB
integrity command `I 1073741824` and asserts firsterr=-1 plus wall_rate
> 400 Mbps from the firmware's `mmap_int 1073741824 B` summary.

Build:

```
make -C fpga build/spi/jedec.bin
make -C stm32mp135_test_board/baremetal/qspi -j$(nproc)
```

Artifacts:

```
fpga/build/spi/jedec.bin
stm32mp135_test_board/baremetal/qspi/build/main.stm32
stm32mp135_test_board/baremetal/qspi/flash.tsv
```

Test (max 10 min):

```
fpga.hx1k:program bin=@jedec.bin
bench_mcu:reset_dut
delay ms=2500
dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true
mp135.evb:uart_open
mp135.evb:uart_expect sentinel="JEDEC ID:" timeout_ms=10000
delay ms=300
mp135.evb:uart_write data="p 3 0\r"
delay ms=200
mp135.evb:uart_write data="I 1073741824\r"
mp135.evb:uart_expect sentinel="mmap_int 1073741824 B" timeout_ms=300000
mp135.evb:uart_close
mark tag=mmap_int_done
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(
        extract_dir, 'mp135.uart', encoding='utf-8')
    m = re.search(
        r'mmap_int\s+1073741824\s+B[^\n]*'
        r'(\d+\.\d+)\s+Mbps[^\n]*firsterr=(-?\d+)', text)
    if not m:
        return False
    mbps = float(m.group(1))
    firsterr = int(m.group(2))
    return firsterr == -1 and mbps > 400.0
```
