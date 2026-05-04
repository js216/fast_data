# Blinky bring-up on iCEstick

Hardware bring-up for the iCE40-HX1K on the Lattice iCEstick: tangle and
build the blinky bitstream, program the FPGA, and confirm `test_serv`
reports a clean program path. The 1 Hz blink on the on-board D1 is the
manual sanity check; the automated path covers only the program-and-
verify round trip since no UART or other sensor is wired to the LED on
this board.

## WIP

### Program blinky on iCEstick

Build the blinky bitstream and submit a one-op plan that programs it
onto the FPGA. Verifier checks that the test_serv manifest reports zero
errors --- visual confirmation of the LED blink rate is the manual step
described in the chapter prose.

Build:

```
make -C fpga build/blinky/blinky.bin
```

Artifacts:

```
fpga/build/blinky/blinky.bin
```

Test (max 1 min):

```
fpga.hx1k:program bin=@blinky.bin
mark tag=blinky_program
```

Verify:

```
def check(extract_dir):
    return Verification.manifest_clean(extract_dir)
```
