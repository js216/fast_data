# FPGA -> MP135 QSPI bring-up

This mission requires bit-perfect transfer of arbitrary data, sustained
for an arbitrary volume of data. In each case, the SPI clock is limited
to no more than 133 MHz.

Build steps tangle the `noweb` (`.nw`) source files into Verilog and
related files, run formal verification and simulation checks, and
prepare the bitstream.

! fpga/to_be_replaced_by_cleaner_code/ code is there for inspiration
only. Do not tangle it directly! At the end of this mission I expect a
single spi.nw file that cleanly implements whatever is needed in this
mission.

## WIP

Assumed hardware connections:

! [insert markdown table of MPU <-> FPGA jumpers needed]

### Verify Connecticity

! make use of gpio.nw and stm32mp135_test_board/baremetal/gpio_test (not
yet implemented) to verify connections are good as per table above.

### PRBS, UART, Checksum

! write prbs_xor.nw that implements a simple LFSR prbs generator and a
super basic XOR-based checksum. prbs_xor.nw should make use of relevant
modules from uart.nw to implement a very simple command language: `r`
over UART resets the PRBS generator to seed 1 and the checksum to 0, `s`
causes it to stream a single word into the checksum engine, and `S`
causes it to stream `2**16` words into the checksum engine, and `p`
prints out the current checksum.

! write stm32mp135_test_board/baremetal/prbs_test (new file) that
implements exactly the same logic, but running on the MPU.

! write tests that compare the outputs of FPGA and MPU streams, for an
interesting range of single-word `s` steps (1,2, 5, ... ?) and big `S`
steps.

### Bit Bang 1-lane Raw SPI

! make spi.nw (new file) that makes use of modules from prbs_xor.nw
where, in addition to streaming the prbs into xor, it streams into SPI
as a slave device. the fpga in this module responds only to the `r`
and `p` commands: the `s` and `S` commands are not needed since the data
streaming is driven by the SPI protocol.

! make a stm32mp135_test_board/baremetal/spi_bitbang (new project) which
acts as an SPI master, but using GPIO to bit bang the data out of the
FPGA. keep also the mpu-based prbs and checksum logic to compare

! verify that no matter how little or how much data is transferred, the
fpga and mpu always report the same checksum.

### Bit Bang 4-lane Raw SPI

! add quad-lane support to spi.nw and
stm32mp135_test_board/baremetal/spi_bitbang but otherwise keep the logic
very similar to the 1-lane case

### 1-Lane Raw SPI, 4 GiB, >=100 Mbps

! make stm32mp135_test_board/baremetal/spi (new project) which does the
same thing as spi_bitbang except it uses the real SPI peripheral

! verify perfect data integrity at 100 Mbps or faster, but careful to
NOT drive SPI clock faster than 133 MHz since that's the limit for the
wiring.

### 4-Lane Raw SPI, 4 GiB, >=400 Mbps

! same thing but using all 4 lanes. Again: DO NOT DRIVE SPI CLOCK FASTER
THAN 133 MHz! most likely 400 Mbps will be hard to achieve because of
per-word or similar DMA overhead --- make sure to minimize all this
overhead as much as possible

### Memory-Mapped Quad SPI, >= 400 Mbps

! Same thing, but implement enough of the JEDEC flash commands so that
the quadspi peripheral can be used in the memory-mapped mode.
