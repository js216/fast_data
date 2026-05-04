# GPIO bring-up on iCEstick

Hardware bring-up for the gpio chapter: program the bitstream onto the
iCEstick, capture the heartbeat that prints all 16 expansion-header
pins as four hex digits every 100 ms, and exercise the `E`/`W` ASCII
command pair so the verifier has concrete oracles for the read-back
lines. Expansion headers J1 and J3 may be left unconnected --- the
drive phase overrides whatever the floating pins read.

## WIP

### Program and exercise gpio on iCEstick

Build the gpio bitstream, program the iCEstick, open the FT2232H UART,
let a few power-on heartbeats arrive, then drive a sequence of two
known 16-bit patterns through the `E`/`W` command pair. The verifier
counts well-formed heartbeat lines and confirms both driven patterns
appear in order.

Build:

```
make -C fpga build/gpio/gpio.bin
```

Artifacts:

```
fpga/build/gpio/gpio.bin
```

Test (max 1 min):

```
fpga.hx1k:program bin=@gpio.bin
fpga.hx1k:uart_open
delay ms=400
fpga.hx1k:uart_write data="EFFFF"
delay ms=200
fpga.hx1k:uart_write data="W1234"
delay ms=400
fpga.hx1k:uart_write data="Wabcd"
delay ms=400
fpga.hx1k:uart_write data="E0000"
delay ms=200
fpga.hx1k:uart_close
mark tag=gpio_program
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    data = Verification.load_stream(extract_dir, 'fpga.uart')
    lines = re.findall(rb'([0-9a-f]{4})\r\n', data)
    if len(lines) < 4:
        return False
    cursor = 0
    for target in (b'1234', b'abcd'):
        while cursor < len(lines) and lines[cursor] != target:
            cursor += 1
        if cursor >= len(lines):
            return False
        cursor += 1
    return True
```
