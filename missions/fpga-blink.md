# Blinky bring-up on iCEstick and HX8K-B-EVN

Hardware bring-up for the blinky chapter: build the demo bitstream for
each supported iCE40 board, program the FPGA, and confirm `test_serv`
reports a clean program path. The 1 Hz blink on the on-board LED is the
manual sanity check; the automated path covers only the program-and-
verify round trip since no UART or other sensor is wired to the LEDs on
these boards. The two sections are identical apart from the per-board
build artifact and the `fpga.<id>:` prefix, so a programming regression
on either board surfaces immediately.

## WIP

### Blinky on iCEstick (hx1k)

Build the per-board bitstream and submit a one-op plan that programs it
onto the iCEstick. Verifier checks that the test_serv manifest reports
zero errors --- visual confirmation of the D1 blink rate is the manual
step described in the chapter prose.

Build:

```
make -C fpga build/blinky/hx1k/blinky.bin
```

Artifacts:

```
fpga/build/blinky/hx1k/blinky.bin
```

Test (max 1 min):

```
fpga.hx1k:program bin=@blinky.bin
mark tag=blinky_hx1k
```

Verify:

```
def check(extract_dir):
    return Verification.manifest_clean(extract_dir)
```

### Blinky on HX8K-B-EVN (hx8k)

Same plan as the iCEstick section, addressing the `fpga.hx8k` instance
instead. The HX8K-B-EVN's D2 LED is driven by the single blinky output;
visual confirmation of the blink rate remains the manual step described
in the chapter prose.

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
```

Test (max 1 min):

```
fpga.hx8k:program bin=@blinky.bin
mark tag=blinky_hx8k
```

Verify:

```
def check(extract_dir):
    return Verification.manifest_clean(extract_dir)
```
