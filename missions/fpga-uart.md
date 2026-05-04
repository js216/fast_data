# UART bring-up on iCEstick and HX8K-B-EVN

Hardware bring-up for the uart chapter: program the demo bitstream onto
each supported iCE40 board, capture the serial output through the
on-board FT2232H, and confirm both the periodic "Hello from iCE40"
heartbeat and the per-byte echo loopback are alive end-to-end. The two
sections are byte-for-byte identical apart from the `fpga.<id>:` prefix,
so a regression on either board surfaces immediately.

## WIP

### UART on iCEstick (hx1k)

Build the per-board bitstream, program the iCEstick, open the FT2232H
UART, let two heartbeat periods elapse so the banner is captured
cleanly, send two single-byte echo probes, and close the capture.

Build:

```
make -C fpga build/uart/hx1k/uart.bin
```

Artifacts:

```
fpga/build/uart/hx1k/uart.bin
```

Test (max 1 min):

```
fpga.hx1k:uart_close
fpga.hx1k:program bin=@uart.bin
delay ms=2000
fpga.hx1k:uart_open
delay ms=2200
fpga.hx1k:uart_write data="x"
delay ms=300
fpga.hx1k:uart_write data="y"
delay ms=300
fpga.hx1k:uart_close
mark tag=uart_hx1k
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'fpga.uart')
    if 'Hello from iCE40' not in text:
        return False
    stripped = text.replace('Hello from iCE40', '')
    stripped = stripped.replace('\r', '').replace('\n', '')
    return any(p in stripped for p in ('x', 'y'))
```

### UART on HX8K-B-EVN (hx8k)

Same plan as the iCEstick section, addressing the `fpga.hx8k` instance
instead. The HX8K-B-EVN's eight on-board LEDs (D2..D9) display the
ASCII code of the last received byte, but the automated path only
checks the UART round-trip.

Build:

```
make -C fpga build/uart/hx8k/uart.bin
```

Artifacts:

```
fpga/build/uart/hx8k/uart.bin
```

Test (max 1 min):

```
fpga.hx8k:uart_close
fpga.hx8k:program bin=@uart.bin
delay ms=2000
fpga.hx8k:uart_open
delay ms=2200
fpga.hx8k:uart_write data="x"
delay ms=300
fpga.hx8k:uart_write data="y"
delay ms=300
fpga.hx8k:uart_close
mark tag=uart_hx8k
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'fpga.uart')
    if 'Hello from iCE40' not in text:
        return False
    stripped = text.replace('Hello from iCE40', '')
    stripped = stripped.replace('\r', '').replace('\n', '')
    return any(p in stripped for p in ('x', 'y'))
```
