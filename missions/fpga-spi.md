# FPGA -> MP135 QSPI bring-up

Bit-perfect FPGA -> STM32MP135 QSPI streaming (firsterr=-1):

- 1 lane: >= 100 Mbps
- 4 lanes: >= 400 Mbps

Each section streams ~4 GiB (0xFF000000 = 4,278,190,080 B, the
firmware's uint32-aligned cap). Runtime: 5:42 at 100 Mbps, 1:26 at 400
Mbps; budgets add ~60 s for reset+DFU+boot plus ~20% headroom.

### 1-lane stream, ~4 GiB, >=100 Mbps

Run `A 4278190080 0 1` against `spi_1lane.bin` at presc=5 sshift=1
(108.7 MHz). Firmware streams the FPGA's incrementing `addr[7:0]`
pattern through hardware CRC32 and prints a `stream` summary line.
Verifier asserts firsterr=-1 and Mbps >= 100.

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

Test (max 8 min):

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
mp135.evb:uart_write data="A 4278190080 0 1\r"
mp135.evb:uart_expect sentinel="stream_xfer 4278190080 B" timeout_ms=420000
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
    pat = (r'stream\s+4278190080\s+B\s+1lane\s+in\s+\d+\s+ms,\s+'
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

## WIP

### Raw 4-lane stream, 16 MiB twin-DDR, >=400 Mbps

Steps up from 1-lane to bit-perfect 4-lane streaming before adding the
memory-mapped wrapper. Programs `spi_quad.bin` (LANES=4, no flash
framing -- drives all 4 IOs from CS-low), boots the MP135 firmware,
sets `p 3 0` (164 MHz SCLK, the same clock the headline section uses),
and runs `T 16777216`: two consecutive `qspi_mdma_read` reads in raw
mode (IMODE=ADMODE=0, dummy=0) into ping-pong DDR slots followed by a
byte-compare. firsterr=-1 means pass1 == pass2 byte-for-byte, which is
real data-integrity validation that does not depend on the master's
first-sample alignment relative to the slave's output presenter.
Verifier parses the firmware's `twin <bytes> B quad raw pass1=<ms> ms
... firsterr=<n>` summary, computes pass1 rate from pass1_ms (less
noisy than wall-clock which includes the validate scan), and asserts
firsterr=-1 plus pass1_rate >= 400 Mbps.

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
mark tag=spi_quad_twin_done
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
    return firsterr == -1 and pass1_rate >= 400.0
```

### Quad memory-mapped, ~4 GiB, >=400 Mbps

Headline target. Run `I 4278190080` against `jedec.bin` (its 0x6B Quad
Output Read returns byte K = (start_addr + K) & 0xff) in FMODE=11
memory-mapped mode -- the path that lifts the ~337 Mbps indirect-MDMA
ceiling. Verifier asserts firsterr=-1 and Mbps >= 400.

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

Test (max 3 min):

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
mp135.evb:uart_write data="I 4278190080\r"
mp135.evb:uart_expect sentinel="mmap_int 4278190080 B" timeout_ms=180000
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
        r'mmap_int\s+4278190080\s+B\s+in\s+\d+\s+ms,\s+'
        r'(\d+\.\d+)\s+Mbps[^\n]*firsterr=(-?\d+)', text)
    if not m:
        return False
    mbps = float(m.group(1))
    firsterr = int(m.group(2))
    return firsterr == -1 and mbps >= 400.0
```
