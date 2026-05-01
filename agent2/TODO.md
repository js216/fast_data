# TODO: QSPI FPGA-to-MPU Fast Data Transfer

### Mission Target

Demonstrate bit-accurate sustained data transfer from FPGA to STM32MP135 MPU
using the QUADSPI peripheral:

- Single-lane path: already demonstrated above 100 Mbps wall-rate with 512 MB
  transfer.
- Quad-lane requirement: at least 200 Mbps, ideally higher, with no data
  errors.

### Next Steps

1. (spi.nw) Stabilize the 0x6B quad peripheral read.
   - Current blocker is byte assembly/cadence for `op=6b`.
   - The passing 0x6F nibble-ramp proves the STM32 peripheral can capture
     ordered quad nibbles correctly.
   - The 0x6B stream still captures as `00 10 20 ...` or related byte-phase
     variants depending on FPGA cadence changes.
   - Future agents should avoid relying on GPIO bit-bang results as proof of
     QUADSPI peripheral behavior.

2. (spi.nw) Add a low-cost 0x6B-specific diagnostic if needed.
   - Avoid the previous synthesis-heavy q6b/q60/q61 debug RAM/printing; it
     caused iCE40 placement failure.
   - Prefer a small opcode or mode that emits a simple repeating 0x6B-compatible
     byte pattern through the same peripheral framing.
   - Keep diagnostics late or non-blocking only if they are not the mission
     path; do not delete them.

3. (spi.nw) Once `q 0 1024` passes, continue through the existing quad sweep.
   - Required next gates are quad pattern checks at presc=203, 63, 15, and 5.
   - Then add/enable a real quad wall-rate floor of at least 200 Mbps.
   - Use wall timing markers already defined by the test policy: before UART
     start command, after firmware reports transfer completion/check.

4. (spi.nw) Make quad streaming use the proven DMA/CRC structure.
   - Single-lane uses DDR ping-pong/auto-consume and hardware CRC path
     successfully.
   - Quad path should use the same sustained-transfer validation model once the
     basic 0x6B peripheral read is bit-correct.
   - Do not claim throughput success until a large transfer is checked for
     correctness.
