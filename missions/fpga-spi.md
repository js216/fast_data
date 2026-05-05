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

! Add a machine-readable connectivity manifest for the first
`gpio_test` bring-up pass. It lists every jumper row from the assumed
hardware connection table with stable signal names, direction, and
whether `gpio.nw` or `stm32mp135_test_board/baremetal/gpio_test` is
responsible for driving or sampling it. A repo test must fail if any
table row is missing from the manifest or if the manifest mentions a
signal not in the table.

  - Manifest: `stm32mp135_test_board/baremetal/gpio_test/connectivity_manifest.json`.
  - Focused validation: `stm32mp135_test_board/baremetal/gpio_test/validate_connectivity_manifest.py`.

### Define GPIO connectivity test vectors

! Extend the existing GPIO connectivity manifest and validator with a
machine-readable first-pass test plan. For every manifest jumper, the
plan must describe the controller that drives the line, the controller
that samples it, and two static test vectors: drive 0 and expect 0, then
drive 1 and expect 1. Bidirectional jumpers must have one low/high pair
in each direction. A repo test must fail if any manifest jumper lacks
the required vectors, if a vector uses a controller not allowed by that
jumper's drive/sample roles, or if any vector references a signal not in
the manifest.

## WIP

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
