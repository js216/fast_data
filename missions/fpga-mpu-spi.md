# FPGA--MPU SPI connection

Prove data transfer from iCE40-HX1k to the STM32MP135 via single- and
quad-lane SPI. As per MPU datasheet, clock speed is limited to 133 MHz,
allowing us to prove data transfers speeds above 100 Mbps (single lane)
and above 400 Mbps (quad lane).

### 1-lane SPI

Build:

```
make -C fpga build/spi/spi_1lane.bin
make -C stm32mp135_test_board/baremetal/qspi build/main.stm32
```

Artifacts:

```
fpga/build/spi/spi_1lane.bin
stm32mp135_test_board/baremetal/qspi/build/main.stm32
stm32mp135_test_board/baremetal/qspi/flash.tsv
```

Test (max 9 min):

```
fpga.hx1k:program bin=@spi_1lane.bin
bench_mcu.0:reset_dut
delay ms=2000
dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true
mp135.evb:uart_open
mp135.evb:uart_expect sentinel="JEDEC ID:" timeout_ms=10000
delay ms=300
mp135.evb:uart_write data="a 1\r"
mp135.evb:uart_expect sentinel="auto=on" timeout_ms=3000
mp135.evb:uart_write data="p 5 1\r"
mp135.evb:uart_expect sentinel="presc=5 sshift=1" timeout_ms=10000

mp135.evb:uart_write data="A 4294967292 0 1\r"
mp135.evb:uart_expect sentinel="A 4294967292 0 1" timeout_ms=15000
mp135.evb:uart_expect sentinel="qspi_hz" timeout_ms=480000

mp135.evb:uart_close
mark tag=onelane
```

Verify:

```
def check(extract_dir):
    """Pass iff:
      - The result line for the full 4294967292-byte stream is present,
      - It reports firsterr=-1 (zero byte errors anywhere in the stream),
      - Its received crc32 matches the firmware's expected crc32,
      - Effective rate is at least 100 Mbps.
    A short / constant-data run cannot pass — the result line is keyed
    to the exact byte count."""
    import os, re
    p = os.path.join(extract_dir, 'streams', 'mp135.uart.bin')
    if not os.path.exists(p):
        return False
    raw = open(p, 'rb').read().replace(b'\r', b'').decode('latin-1')
    for line in raw.split('\n'):
        if 'stream 4294967292' not in line:
            continue
        m = re.search(r'crc32=([0-9a-f]+), expect=([0-9a-f]+)', line)
        if not m or m.group(1) != m.group(2):
            return False
        if 'firsterr=-1' not in line:
            return False
        m2 = re.search(r'([0-9]+)\.([0-9]+) Mbps', line)
        if not m2:
            return False
        rate_x10 = int(m2.group(1)) * 10 + int(m2.group(2))
        if rate_x10 < 1000:
            return False
        return True
    return False
```

### 4-lane SPI

Build:

```
make -C fpga build/spi/spi_quad.bin
make -C stm32mp135_test_board/baremetal/qspi build/main.stm32
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
bench_mcu.0:reset_dut
delay ms=2000
dfu.evb:flash_layout layout=@flash.tsv no_reconnect=true
mp135.evb:uart_open
mp135.evb:uart_expect sentinel="JEDEC ID:" timeout_ms=10000
delay ms=300
mp135.evb:uart_write data="a 1\r"
mp135.evb:uart_expect sentinel="auto=on" timeout_ms=3000
mp135.evb:uart_write data="p 31 1\r"
mp135.evb:uart_expect sentinel="presc=31 sshift=1" timeout_ms=10000

mp135.evb:uart_write data="A 1073741824 1 1\r"
mp135.evb:uart_expect sentinel="A 1073741824 1 1" timeout_ms=15000
mp135.evb:uart_expect sentinel="qspi_hz" timeout_ms=240000

mp135.evb:uart_close
mark tag=fourlane
```

Verify:

```
def check(extract_dir):
    """Pass iff:
      - The result line for the full 1073741824-byte stream is present,
      - It reports firsterr=-1 (zero byte errors anywhere in the stream),
      - Its received crc32 matches the firmware's expected crc32,
      - Effective rate is at least 80 Mbps.
    A short / constant-data run cannot pass — the result line is keyed
    to the exact byte count."""
    import os, re
    p = os.path.join(extract_dir, 'streams', 'mp135.uart.bin')
    if not os.path.exists(p):
        return False
    raw = open(p, 'rb').read().replace(b'\r', b'').decode('latin-1')
    for line in raw.split('\n'):
        if 'stream 1073741824' not in line:
            continue
        m = re.search(r'crc32=([0-9a-f]+), expect=([0-9a-f]+)', line)
        if not m or m.group(1) != m.group(2):
            return False
        if 'firsterr=-1' not in line:
            return False
        m2 = re.search(r'([0-9]+)\.([0-9]+) Mbps', line)
        if not m2:
            return False
        rate_x10 = int(m2.group(1)) * 10 + int(m2.group(2))
        if rate_x10 < 800:
            return False
        return True
    return False
```
