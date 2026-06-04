# FPGA <-> custom MP135 QUADSPI connection

Prove data transfer from the iCE40-HX8K-B-EVN to the custom STM32MP135
board over the QUADSPI bus. The FPGA ball assignments come from the
discovery sweep in `fpga-mpu-gpio-custom.md` and are baked into
`spi_hx8k.pcf` (QUADSPI_CLK->L3, QUADSPI_CS->N3, IO0->F1, IO1->T7,
IO2->B1, IO3->G1). The MP135 QUADSPI master streams a known pattern from
the FPGA slave and checks the received CRC, byte-for-byte correctness, and
rate.

Two sections: a single-lane warm-up (>100 Mbps), and the headline 4-lane
run that streams >=2 GB of PRBS data at >=400 Mbps bit-perfect. The 4-lane
slave runs at presc=4 (131 MHz SCLK x 4 lanes = 524 Mbps). At that SCLK
the integer-byte high/low nibble pairing needs a half-SCLK-cycle launch
shift to center the sample, so the headline bitstream combines
`QUAD_HIGH_LEAD=1` (byte-level nibble pairing), `QUAD_LAUNCH_POSEDGE=1`
(half-cycle launch), and `QUAD_SEED_BIAS=255` (cancels the one-count
advance the pairing adds); the master aligns with dummy=9. `PRBS_MODE=1`
replaces the incrementing counter with `prbs8(index)` (eight 8-bit Galois
LFSR steps, mask 0xB8) so every lane sees ~50%-density bit transitions;
the master mirrors the same `prbs8` so the CRC/validate path is unchanged.

The custom-board QUADSPI firmware (`BOARD_DEFINE=-DBOARD_CUSTOM`) runs a
bring-up with clocks + PMIC + DDR + UART + ETZPC + GIC + QUADSPI (no MMU).
The high-volume 4-lane run takes the direct QSPI->CRC FIFO DMA path (MDMA
feeds the hardware CRC32 straight from the QUADSPI FIFO, no DDR buffer and
no CPU validation), so the wall rate equals the link rate.

### 1-lane QUADSPI

Build the custom-board 1-lane bitstream and the QUADSPI firmware.
`tangle`/`weave` live in `~/.cargo/bin`.

Build:

```
PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH" make -C fpga build/spi/spi_1lane_hx8k.bin
make -C stm32mp135_test_board/baremetal/qspi BOARD_DEFINE=-DBOARD_CUSTOM clean
make -C stm32mp135_test_board/baremetal/qspi BOARD_DEFINE=-DBOARD_CUSTOM build/main.stm32
```

Artifacts:

```
fpga/build/spi/spi_1lane_hx8k.bin
stm32mp135_test_board/baremetal/qspi/build/main.stm32
stm32mp135_test_board/baremetal/qspi/flash.tsv
```

Test (max 5 min):

```
fpga.hx8k:program bin=@spi_1lane_hx8k.bin
bench_mcu.0:reset_dut2
delay ms=2000
dfu.custom:flash_layout layout=@flash.tsv no_reconnect=true
mp135.custom:uart_open
delay ms=500
mp135.custom:uart_write data="a 1\r"
mp135.custom:uart_expect sentinel="auto=on" timeout_ms=5000
mp135.custom:uart_write data="p 5 1\r"
mp135.custom:uart_expect sentinel="presc=5 sshift=1" timeout_ms=10000

mp135.custom:uart_write data="A 268435456 0 1\r"
mp135.custom:uart_expect sentinel="A 268435456 0 1" timeout_ms=15000
mp135.custom:uart_expect sentinel="qspi_hz" timeout_ms=120000

mp135.custom:uart_close
mark tag=onelane
```

Verify:

```
def check(extract_dir):
    """Pass iff:
      - The result line for the full 268435456-byte stream is present,
      - It reports firsterr=-1 (zero byte errors anywhere in the stream),
      - Its received crc32 matches the firmware's expected crc32,
      - Effective rate is at least 100 Mbps.
    A short / constant-data run cannot pass -- the result line is keyed
    to the exact byte count."""
    import os, re
    p = os.path.join(extract_dir, 'streams', 'mp135.uart.bin')
    if not os.path.exists(p):
        return False
    raw = open(p, 'rb').read().replace(b'\r', b'').decode('latin-1')
    for line in raw.split('\n'):
        if 'stream 268435456' not in line:
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

### 4-lane QUADSPI, 2 GB of 32-bit-LFSR PRBS at >=400 Mbps

Build the headline 4-lane 32-bit-PRBS bitstream and the QUADSPI firmware.
`tangle`/`weave` live in `~/.cargo/bin`. The FPGA emits a continuous 32-bit
maximal Galois LFSR (mask 0xA3000000, 8 steps/byte, period 2^32-1 bytes ~=
4 GiB), and the master streams the whole 2 GiB in one CS-low QSPI read (MDMA
re-armed in 256 MiB segments) so the LFSR never reseeds -- the pattern does
not repeat within the 2 GiB. The received hardware CRC32 is checked against
an independent combined LFSR+CRC GF(2)-matrix computation in firmware
(prbs32_match_offset), so a CRC match proves the stream is exactly the LFSR
sequence, bit for bit.

Build:

```
PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH" make -C fpga build/spi/spi_quad_prbs32_hx8k.bin
make -C stm32mp135_test_board/baremetal/qspi BOARD_DEFINE=-DBOARD_CUSTOM clean
make -C stm32mp135_test_board/baremetal/qspi BOARD_DEFINE=-DBOARD_CUSTOM build/main.stm32
```

Artifacts:

```
fpga/build/spi/spi_quad_prbs32_hx8k.bin
stm32mp135_test_board/baremetal/qspi/build/main.stm32
stm32mp135_test_board/baremetal/qspi/flash.tsv
```

Test (max 5 min):

```
fpga.hx8k:program bin=@spi_quad_prbs32_hx8k.bin
bench_mcu.0:reset_dut2
delay ms=2000
dfu.custom:flash_layout layout=@flash.tsv no_reconnect=true
mp135.custom:uart_open
delay ms=500
mp135.custom:uart_write data="a 1 1 0 1\r"
mp135.custom:uart_expect sentinel="prbs32=on" timeout_ms=5000
mp135.custom:uart_write data="p 4 1\r"
mp135.custom:uart_expect sentinel="presc=4 sshift=1" timeout_ms=10000

mp135.custom:uart_write data="A 2147483648 1 1 9\r"
mp135.custom:uart_expect sentinel="A 2147483648 1 1 9" timeout_ms=15000
mp135.custom:uart_expect sentinel="qspi_hz" timeout_ms=120000

mp135.custom:uart_close
mark tag=quad_prbs32
```

Verify:

```
def check(extract_dir):
    """Pass iff the full 2147483648-byte (2 GiB) 4-lane 32-bit-PRBS stream:
      - has a result line for the exact byte count,
      - reports firsterr=-1 (the received hardware CRC32 equals the
        firmware's independent combined LFSR+CRC matrix value -> the
        stream is exactly the 32-bit LFSR sequence, bit for bit),
      - received crc32 matches that expected crc32,
      - effective rate is at least 400 Mbps.
    The byte count and the LFSR CRC are both keyed, so a short or
    wrong-pattern run cannot pass."""
    import os, re
    p = os.path.join(extract_dir, 'streams', 'mp135.uart.bin')
    if not os.path.exists(p):
        return False
    raw = open(p, 'rb').read().replace(b'\r', b'').decode('latin-1')
    for line in raw.split('\n'):
        if 'stream 2147483648' not in line:
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
        if rate_x10 < 4000:
            return False
        return True
    return False
```
