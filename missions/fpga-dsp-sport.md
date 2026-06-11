# FPGA <-> DSP SPORT link

Directions and required per-lane SPORT bit clocks:

| Direction | FPGA-originated lanes | DSP-originated lanes | OK? |
| --------- | --------------------: | -------------------: | --- |
| D-F       |                     - |             56+ Mbps | x   |
| DD-FF     |                     - |             56+ Mbps | x   |
| DDDD-FFFF |                     - |             56+ Mbps | x   |
| F-D       |              56+ Mbps |                    - | x   |
| FF-DD     |              56+ Mbps |                    - | x   |
| FFFF-DDDD |              56+ Mbps |                    - | x   |
| FD-DF     |              56+ Mbps |             56+ Mbps | x   |
| FFDD-DDFF |              56+ Mbps |             56+ Mbps | x   |

Every lane in every direction runs from the one DSP-programmed SPORT
clock, configured at 59.375 MHz (CGU MSEL=57, 95% of the 62.5 MHz
datasheet caps -- fSPTCLKPROG TX for DSP-originated lanes, fSPTCLKEXT RX
for FPGA-originated lanes, which forward the DSP clock with no PLL).
The 56+ Mbps goal is 90% of the datasheet cap, measured per lane by
bench wall clock end to end.

Success criteria for each direction:

- 2 GiB data per lane
- zero bit error rate
- PRBS-31 data pattern on every data lane
- DSP is the SPORT clock/frame-sync master for every lane
- FPGA uses DSP-generated SPORT clock/frame sync directly, with no PLL,
  clock generation, clock multiplication, or clock phase locking
- SPORT frame sync is the protocol word boundary
- DSP DAI1_PIN06 drives FPGA ball R10 as the shared RUN signal
- Both endpoint LFSRs use the same PRBS-31 seed and are held at that
  seed while RUN is inactive
- Word zero is the first active SPORT frame sync after RUN is active
- No phase search, training pattern, resync, skipped-word alignment, or
  data-dependent sync mechanism is allowed

### D-F 2GiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport_rx1
cd fpga && yosys -q -p "read_verilog verilog/sport_rx.v verilog/uart_tx.v; chparam -set N 1 -set MIN_DONE_WORDS 536870912 sport_rx; synth_ice40 -top sport_rx -json build/sport_rx1/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_rx1/s.json --pcf verilog/sport_rx1_hx8k.pcf --asc build/sport_rx1/s.asc --freq 65 --seed 20 -q --pcf-allow-unconstrained && icepack build/sport_rx1/s.asc build/sport_rx1/sport_rx1.bin
make -C adsp2156/sport_fpga_rx clean
make -j -C adsp2156/sport_fpga_rx CFLAGS_EXTRA="-DNCH=1U -DN_WORDS=536870912U -DDATA_INDEP_FS=1 -DHALF_WORDS=65536U -DSPORT_SCLK_HZ=59375000U"
cp adsp2156/sport_fpga_rx/build/main.ldr adsp2156/sport_fpga_rx/build/dma_2gib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_rx1/sport_rx1.bin
adsp2156/sport_fpga_rx/build/dma_2gib.ldr
```

Test (max 18 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_rx1.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@dma_2gib.ldr timeout_ms=15000
dsp:uart_expect sentinel="tx h=32\r" timeout_ms=10000
fpga.hx8k:uart_expect sentinel="rx w=00200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=64\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=96\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=128\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=160\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=192\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=224\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=00e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=256\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=288\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=320\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=352\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=384\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=416\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=448\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=480\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=01e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=512\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=544\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=576\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=608\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=640\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=672\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=704\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=736\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=02e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=768\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=800\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=832\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=864\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=896\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=928\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=960\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=992\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=03e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1024\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1056\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1088\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1120\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1152\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1184\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1216\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1248\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=04e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1280\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1312\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1344\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1376\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1408\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1440\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1472\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1504\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=05e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1536\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1568\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1600\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1632\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1664\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1696\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1728\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1760\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=06e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1792\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1824\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1856\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1888\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1920\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1952\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=1984\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2016\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=07e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2048\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=08000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2080\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=08200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2112\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=08400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2144\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=08600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2176\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=08800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2208\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=08a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2240\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=08c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2272\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=08e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2304\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=09000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2336\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=09200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2368\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=09400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2400\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=09600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2432\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=09800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2464\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=09a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2496\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=09c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2528\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=09e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2560\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0a000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2592\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0a200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2624\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0a400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2656\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0a600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2688\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0a800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2720\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0aa00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2752\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0ac00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2784\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0ae00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2816\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0b000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2848\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0b200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2880\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0b400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2912\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0b600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2944\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0b800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=2976\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0ba00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3008\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0bc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3040\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0be00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3072\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0c000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3104\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0c200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3136\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0c400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3168\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0c600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3200\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0c800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3232\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0ca00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3264\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0cc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3296\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0ce00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3328\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0d000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3360\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0d200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3392\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0d400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3424\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0d600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3456\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0d800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3488\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0da00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3520\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0dc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3552\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0de00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3584\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0e000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3616\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0e200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3648\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0e400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3680\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0e600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3712\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0e800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3744\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0ea00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3776\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0ec00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3808\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0ee00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3840\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0f000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3872\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0f200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3904\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0f400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3936\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0f600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=3968\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0f800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4000\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0fa00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4032\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0fc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4064\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=0fe00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4096\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=10000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4128\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=10200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4160\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=10400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4192\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=10600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4224\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=10800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4256\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=10a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4288\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=10c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4320\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=10e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4352\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=11000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4384\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=11200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4416\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=11400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4448\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=11600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4480\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=11800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4512\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=11a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4544\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=11c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4576\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=11e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4608\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=12000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4640\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=12200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4672\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=12400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4704\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=12600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4736\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=12800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4768\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=12a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4800\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=12c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4832\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=12e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4864\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=13000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4896\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=13200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4928\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=13400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4960\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=13600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=4992\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=13800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5024\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=13a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5056\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=13c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5088\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=13e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5120\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=14000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5152\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=14200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5184\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=14400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5216\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=14600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5248\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=14800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5280\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=14a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5312\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=14c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5344\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=14e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5376\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=15000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5408\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=15200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5440\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=15400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5472\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=15600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5504\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=15800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5536\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=15a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5568\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=15c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5600\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=15e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5632\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=16000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5664\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=16200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5696\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=16400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5728\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=16600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5760\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=16800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5792\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=16a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5824\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=16c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5856\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=16e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5888\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=17000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5920\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=17200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5952\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=17400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=5984\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=17600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6016\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=17800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6048\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=17a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6080\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=17c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6112\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=17e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6144\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=18000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6176\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=18200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6208\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=18400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6240\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=18600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6272\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=18800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6304\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=18a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6336\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=18c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6368\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=18e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6400\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=19000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6432\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=19200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6464\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=19400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6496\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=19600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6528\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=19800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6560\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=19a00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6592\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=19c00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6624\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=19e00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6656\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1a000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6688\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1a200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6720\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1a400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6752\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1a600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6784\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1a800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6816\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1aa00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6848\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1ac00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6880\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1ae00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6912\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1b000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6944\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1b200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=6976\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1b400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7008\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1b600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7040\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1b800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7072\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1ba00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7104\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1bc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7136\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1be00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7168\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1c000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7200\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1c200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7232\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1c400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7264\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1c600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7296\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1c800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7328\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1ca00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7360\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1cc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7392\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1ce00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7424\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1d000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7456\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1d200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7488\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1d400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7520\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1d600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7552\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1d800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7584\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1da00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7616\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1dc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7648\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1de00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7680\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1e000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7712\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1e200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7744\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1e400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7776\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1e600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7808\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1e800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7840\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1ea00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7872\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1ec00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7904\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1ee00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7936\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1f000000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=7968\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1f200000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8000\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1f400000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8032\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1f600000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8064\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1f800000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8096\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1fa00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8128\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1fc00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8160\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="rx w=1fe00000 " timeout_ms=5000
dsp:uart_expect sentinel="tx h=8192\r" timeout_ms=5000
fpga.hx8k:uart_expect sentinel="sport_rx lanes=" timeout_ms=15000
delay ms=3000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=d_f_hb_2gib
```

Verify:

```
def _corruption_gate(extract_dir):
    # Any received-data error is a deterministic FAIL (jk 2026-06-11):
    # a corrupted word is a real defect, never a bench transient, so
    # retrying would only hide it. Scans the raw streams so it fires
    # even when the op timed out before the final report line.
    import sys
    for stream, pats in (
            ('dsp.uart', (r'rx h=\d+ e=(\d+)', r'rx_errors=(\d+)')),
            ('fpga.uart', (r'rx w=[0-9a-f]+ e=([0-9a-f]+)',
                           r'errors_hex=([0-9a-f]+)', r'(ERR) w='))):
        try:
            txt = Verification.load_stream_text(extract_dir, stream)
        except Exception:
            continue
        for pat in pats:
            for m in re.finditer(pat, txt):
                v = m.group(1)
                if v == 'ERR' or int(v, 16) != 0:
                    sys.stderr.write('\033[1;31mDATA CORRUPTION\033[0m '
                                     + stream + ': ' + m.group(0) + '\n')
                    raise HardFail('data corruption: '
                                   + stream + ' ' + m.group(0))


def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    _corruption_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'fpga.uart')
    if 'ERR w=' in text:
        raise HardFail('FPGA reported first-error line: ' +
                       text[text.index('ERR w='):][:64])
    m = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', text)
    if not m:
        raise HardFail('no sport_rx report')
    lanes, words, errors = int(m.group(1)), int(m.group(2), 16), int(m.group(3), 16)
    nprog = len(re.findall(r'rx w=[0-9a-f]{8} ', text))
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'fpga.hx8k' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[-1]['t_end'] - boots[0]['t_start']
    rate = int(words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'{rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if rate < 56250000:
        raise HardFail(f'rate {rate} < 58000000')
    if lanes == 1 and errors == 0 and words >= 536870912 and m.group(4) == 'PASS':
        return True
    raise HardFail(f'FAIL: lanes={lanes} words={words} errors={errors}')
```

### DD-FF 2GiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport_rx2
cd fpga && yosys -q -p "read_verilog -D EYE_DELAY verilog/sport_rx.v verilog/uart_tx.v; chparam -set N 2 -set MIN_DONE_WORDS 536870912 -set RESYNC 1 sport_rx; synth_ice40 -top sport_rx -json build/sport_rx2/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_rx2/s.json --pcf verilog/sport_rx_hx8k.pcf --asc build/sport_rx2/s.asc --freq 75 --timing-allow-fail --seed 20 -q --pcf-allow-unconstrained && icepack build/sport_rx2/s.asc build/sport_rx2/sport_rx2.bin
make -C adsp2156/sport_fpga_rx clean
make -j -C adsp2156/sport_fpga_rx CFLAGS_EXTRA="-DNCH=2U -DN_WORDS=536870976U -DDATA_INDEP_FS=0 -DHALF_WORDS=65536U -DSPORT_SCLK_HZ=59375000U"
cp adsp2156/sport_fpga_rx/build/main.ldr adsp2156/sport_fpga_rx/build/dma_2gib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_rx2/sport_rx2.bin
adsp2156/sport_fpga_rx/build/dma_2gib.ldr
```

Test (max 21 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_rx2.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@dma_2gib.ldr timeout_ms=15000
fpga.hx8k:uart_expect sentinel="sport_rx lanes=" timeout_ms=390000
delay ms=3000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=dd_ff_2gib
```

Verify:

```
def _corruption_gate(extract_dir):
    # Any received-data error is a deterministic FAIL (jk 2026-06-11):
    # a corrupted word is a real defect, never a bench transient, so
    # retrying would only hide it. Scans the raw streams so it fires
    # even when the op timed out before the final report line.
    import sys
    for stream, pats in (
            ('dsp.uart', (r'rx h=\d+ e=(\d+)', r'rx_errors=(\d+)')),
            ('fpga.uart', (r'rx w=[0-9a-f]+ e=([0-9a-f]+)',
                           r'errors_hex=([0-9a-f]+)', r'(ERR) w='))):
        try:
            txt = Verification.load_stream_text(extract_dir, stream)
        except Exception:
            continue
        for pat in pats:
            for m in re.finditer(pat, txt):
                v = m.group(1)
                if v == 'ERR' or int(v, 16) != 0:
                    sys.stderr.write('\033[1;31mDATA CORRUPTION\033[0m '
                                     + stream + ': ' + m.group(0) + '\n')
                    raise HardFail('data corruption: '
                                   + stream + ' ' + m.group(0))


def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    _corruption_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'fpga.uart')
    m = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', text)
    if not m:
        raise HardFail('no sport_rx report')
    lanes, words, errors = int(m.group(1)), int(m.group(2), 16), int(m.group(3), 16)
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'fpga.hx8k' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[0]['t_end'] - boots[0]['t_start']
    rate = int(words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'{rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if rate < 56250000:
        raise HardFail(f'rate {rate} < 60000000')
    if lanes == 2 and errors == 0 and words >= 536870912 and m.group(4) == 'PASS':
        return True
    raise HardFail(f'FAIL: lanes={lanes} words={words} errors={errors}')
```

### DDDD-FFFF 2GiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport_rx4
cd fpga && yosys -q -p "read_verilog -D EYE_DELAY verilog/sport_rx.v verilog/uart_tx.v; chparam -set N 4 -set MIN_DONE_WORDS 536870912 -set RESYNC 1 sport_rx; synth_ice40 -top sport_rx -json build/sport_rx4/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_rx4/s.json --pcf verilog/sport_rx4_hx8k.pcf --asc build/sport_rx4/s.asc --freq 75 --timing-allow-fail --seed 20 -q --pcf-allow-unconstrained && icepack build/sport_rx4/s.asc build/sport_rx4/sport_rx4.bin
make -C adsp2156/sport_fpga_rx clean
make -j -C adsp2156/sport_fpga_rx CFLAGS_EXTRA="-DNCH=4U -DN_WORDS=536870976U -DDATA_INDEP_FS=0 -DHALF_WORDS=65536U -DSPORT_SCLK_HZ=59375000U"
cp adsp2156/sport_fpga_rx/build/main.ldr adsp2156/sport_fpga_rx/build/dma_2gib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_rx4/sport_rx4.bin
adsp2156/sport_fpga_rx/build/dma_2gib.ldr
```

Test (max 21 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_rx4.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@dma_2gib.ldr timeout_ms=15000
fpga.hx8k:uart_expect sentinel="sport_rx lanes=" timeout_ms=390000
delay ms=3000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=dddd_ffff_2gib
```

Verify:

```
def _corruption_gate(extract_dir):
    # Any received-data error is a deterministic FAIL (jk 2026-06-11):
    # a corrupted word is a real defect, never a bench transient, so
    # retrying would only hide it. Scans the raw streams so it fires
    # even when the op timed out before the final report line.
    import sys
    for stream, pats in (
            ('dsp.uart', (r'rx h=\d+ e=(\d+)', r'rx_errors=(\d+)')),
            ('fpga.uart', (r'rx w=[0-9a-f]+ e=([0-9a-f]+)',
                           r'errors_hex=([0-9a-f]+)', r'(ERR) w='))):
        try:
            txt = Verification.load_stream_text(extract_dir, stream)
        except Exception:
            continue
        for pat in pats:
            for m in re.finditer(pat, txt):
                v = m.group(1)
                if v == 'ERR' or int(v, 16) != 0:
                    sys.stderr.write('\033[1;31mDATA CORRUPTION\033[0m '
                                     + stream + ': ' + m.group(0) + '\n')
                    raise HardFail('data corruption: '
                                   + stream + ' ' + m.group(0))


def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    _corruption_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'fpga.uart')
    m = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', text)
    if not m:
        raise HardFail('no sport_rx report')
    lanes, words, errors = int(m.group(1)), int(m.group(2), 16), int(m.group(3), 16)
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'fpga.hx8k' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[0]['t_end'] - boots[0]['t_start']
    rate = int(words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'{rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if rate < 56250000:
        raise HardFail(f'rate {rate} < 60000000')
    if lanes == 4 and errors == 0 and words >= 536870912 and m.group(4) == 'PASS':
        return True
    raise HardFail(f'FAIL: lanes={lanes} words={words} errors={errors}')
```

### F-D 2GiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
make -C adsp2156/sport_fpga_bidir clean
make -j -C adsp2156/sport_fpga_bidir CFLAGS_EXTRA="-DRX_N=1U -DTX_N=1U -DTOTAL_WORDS=536870912U -DTX_FIRST"
cp adsp2156/sport_fpga_bidir/build/main.ldr adsp2156/sport_fpga_bidir/build/bidir1x1_2gib.ldr
mkdir -p fpga/build/sport_bidir_1x1
cd fpga && yosys -q -p "read_verilog -D EYE_DELAY verilog/sport_tx_sync_nopll.v verilog/sport_tx_prbs_ser.v verilog/sport_rx.v verilog/sport_bidir.v verilog/uart_tx.v; chparam -set TX_TO_DSP_N 1 -set RX_FROM_DSP_N 1 -set SYNC_TX 1 -set NOPLL 1 -set REPORT_LANE0 0 -set MIN_DONE_WORDS 536870912 sport_bidir; synth_ice40 -top sport_bidir -json build/sport_bidir_1x1/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_bidir_1x1/s.json --pcf verilog/sport_bidir_1x1_hx8k.pcf --asc build/sport_bidir_1x1/s.asc --freq 65 -q --pcf-allow-unconstrained && icepack build/sport_bidir_1x1/s.asc build/sport_bidir_1x1/sport_bidir_1x1.bin
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_bidir_1x1/sport_bidir_1x1.bin
adsp2156/sport_fpga_bidir/build/bidir1x1_2gib.ldr
```

Test (max 18 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_bidir_1x1.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@bidir1x1_2gib.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_bidir rx_lanes=1" timeout_ms=390000
fpga.hx8k:uart_expect sentinel="sport_rx lanes=1" timeout_ms=60000
delay ms=2000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=f_d_2gib
```

Verify:

```
def _corruption_gate(extract_dir):
    # Any received-data error is a deterministic FAIL (jk 2026-06-11):
    # a corrupted word is a real defect, never a bench transient, so
    # retrying would only hide it. Scans the raw streams so it fires
    # even when the op timed out before the final report line.
    import sys
    for stream, pats in (
            ('dsp.uart', (r'rx h=\d+ e=(\d+)', r'rx_errors=(\d+)')),
            ('fpga.uart', (r'rx w=[0-9a-f]+ e=([0-9a-f]+)',
                           r'errors_hex=([0-9a-f]+)', r'(ERR) w='))):
        try:
            txt = Verification.load_stream_text(extract_dir, stream)
        except Exception:
            continue
        for pat in pats:
            for m in re.finditer(pat, txt):
                v = m.group(1)
                if v == 'ERR' or int(v, 16) != 0:
                    sys.stderr.write('\033[1;31mDATA CORRUPTION\033[0m '
                                     + stream + ': ' + m.group(0) + '\n')
                    raise HardFail('data corruption: '
                                   + stream + ' ' + m.group(0))


def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    _corruption_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    dtxt = Verification.load_stream_text(extract_dir, 'dsp.uart')
    ftxt = Verification.load_stream_text(extract_dir, 'fpga.uart')
    dm = re.search(r'sport_bidir rx_lanes=(\d+) tx_lanes=(\d+) rx_words=(\d+) rx_errors=(\d+) timeouts=(\d+) tx_timeouts=(\d+) overruns=(\d+) slips=(\d+) tx_sent=(\d+) (PASS|FAIL)', dtxt)
    if not dm:
        raise HardFail('no sport_bidir report')
    rx_lanes, rx_words, rx_errors, to, txto, ov, slips = (int(dm.group(i)) for i in (1,3,4,5,6,7,8))
    fm = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', ftxt)
    if not fm:
        sys.stderr.write('no FPGA from_dsp report\n')
        return False
    fpga_words = int(fm.group(2), 16)
    fpga_errors = int(fm.group(3), 16)
    if not (fpga_errors == 0 and fpga_words >= 536870912 and fm.group(4) == 'PASS'):
        raise HardFail(f'D->F FAIL: words={fpga_words} errors={fpga_errors}')
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[0]['t_end'] - boots[0]['t_start']
    fd_rate = int(rx_words * 32 / elapsed) if elapsed > 0 else 0
    df_rate = int(fpga_words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'fd={fd_rate/1e6:.1f}Mbps df={df_rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if fd_rate < 56250000:
        raise HardFail(f'F->D rate {fd_rate} < 60000000')
    if df_rate < 56250000:
        raise HardFail(f'D->F rate {df_rate} < 60000000')
    if (rx_lanes == 1 and rx_errors == 0 and to == 0 and txto == 0 and ov == 0
            and slips == 0 and rx_words >= 536870912 and dm.group(10) == 'PASS'):
        return True
    raise HardFail(f'FAIL: rx_words={rx_words} rx_errors={rx_errors} slips={slips}')
```

### FF-DD 2GiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
make -C adsp2156/sport_fpga_bidir clean
make -j -C adsp2156/sport_fpga_bidir CFLAGS_EXTRA="-DRX_N=2U -DTX_N=2U -DTOTAL_WORDS=536870912U -DTX_FIRST"
cp adsp2156/sport_fpga_bidir/build/main.ldr adsp2156/sport_fpga_bidir/build/bidir2x2_2gib.ldr
mkdir -p fpga/build/sport_bidir_2x2
cd fpga && yosys -q -p "read_verilog -D EYE_DELAY verilog/sport_tx_sync_nopll.v verilog/sport_tx_prbs_ser.v verilog/sport_rx.v verilog/sport_bidir.v verilog/uart_tx.v; chparam -set TX_TO_DSP_N 2 -set RX_FROM_DSP_N 2 -set SYNC_TX 1 -set NOPLL 1 -set REPORT_LANE0 0 -set MIN_DONE_WORDS 536870912 sport_bidir; synth_ice40 -top sport_bidir -json build/sport_bidir_2x2/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_bidir_2x2/s.json --pcf verilog/sport_bidir_2x2_hx8k.pcf --asc build/sport_bidir_2x2/s.asc --freq 62 --seed 9 -q --pcf-allow-unconstrained && icepack build/sport_bidir_2x2/s.asc build/sport_bidir_2x2/sport_bidir_2x2.bin
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_bidir_2x2/sport_bidir_2x2.bin
adsp2156/sport_fpga_bidir/build/bidir2x2_2gib.ldr
```

Test (max 18 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_bidir_2x2.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@bidir2x2_2gib.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_bidir rx_lanes=2" timeout_ms=390000
fpga.hx8k:uart_expect sentinel="sport_rx lanes=2" timeout_ms=60000
delay ms=2000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=ff_dd_2gib
```

Verify:

```
def _corruption_gate(extract_dir):
    # Any received-data error is a deterministic FAIL (jk 2026-06-11):
    # a corrupted word is a real defect, never a bench transient, so
    # retrying would only hide it. Scans the raw streams so it fires
    # even when the op timed out before the final report line.
    import sys
    for stream, pats in (
            ('dsp.uart', (r'rx h=\d+ e=(\d+)', r'rx_errors=(\d+)')),
            ('fpga.uart', (r'rx w=[0-9a-f]+ e=([0-9a-f]+)',
                           r'errors_hex=([0-9a-f]+)', r'(ERR) w='))):
        try:
            txt = Verification.load_stream_text(extract_dir, stream)
        except Exception:
            continue
        for pat in pats:
            for m in re.finditer(pat, txt):
                v = m.group(1)
                if v == 'ERR' or int(v, 16) != 0:
                    sys.stderr.write('\033[1;31mDATA CORRUPTION\033[0m '
                                     + stream + ': ' + m.group(0) + '\n')
                    raise HardFail('data corruption: '
                                   + stream + ' ' + m.group(0))


def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    _corruption_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    dtxt = Verification.load_stream_text(extract_dir, 'dsp.uart')
    ftxt = Verification.load_stream_text(extract_dir, 'fpga.uart')
    dm = re.search(r'sport_bidir rx_lanes=(\d+) tx_lanes=(\d+) rx_words=(\d+) rx_errors=(\d+) timeouts=(\d+) tx_timeouts=(\d+) overruns=(\d+) slips=(\d+) tx_sent=(\d+) (PASS|FAIL)', dtxt)
    if not dm:
        raise HardFail('no sport_bidir report')
    rx_lanes, rx_words, rx_errors, to, txto, ov, slips = (int(dm.group(i)) for i in (1,3,4,5,6,7,8))
    fm = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', ftxt)
    if not fm:
        sys.stderr.write('no FPGA from_dsp report\n')
        return False
    fpga_words = int(fm.group(2), 16)
    fpga_errors = int(fm.group(3), 16)
    if not (fpga_errors == 0 and fpga_words >= 536870912 and fm.group(4) == 'PASS'):
        raise HardFail(f'D->F FAIL: words={fpga_words} errors={fpga_errors}')
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[0]['t_end'] - boots[0]['t_start']
    fd_rate = int(rx_words * 32 / elapsed) if elapsed > 0 else 0
    df_rate = int(fpga_words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'fd={fd_rate/1e6:.1f}Mbps df={df_rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if fd_rate < 56250000:
        raise HardFail(f'F->D rate {fd_rate} < 60000000')
    if df_rate < 56250000:
        raise HardFail(f'D->F rate {df_rate} < 60000000')
    if (rx_lanes == 2 and rx_errors == 0 and to == 0 and txto == 0 and ov == 0
            and slips == 0 and rx_words >= 536870912 and dm.group(10) == 'PASS'):
        return True
    raise HardFail(f'FAIL: rx_words={rx_words} rx_errors={rx_errors} slips={slips}')
```

### FFFF-DDDD 2GiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
make -C adsp2156/sport_fpga_bidir clean
make -j -C adsp2156/sport_fpga_bidir CFLAGS_EXTRA="-DRX_N=4U -DTX_N=2U -DTOTAL_WORDS=536870912U -DTX_NO_REFILL"
cp adsp2156/sport_fpga_bidir/build/main.ldr adsp2156/sport_fpga_bidir/build/ffff2gib.ldr
mkdir -p fpga/build/sport_bidir_4x
cd fpga && yosys -q -p "read_verilog -D EYE_DELAY verilog/sport_tx_sync_nopll.v verilog/sport_tx_prbs_ser.v verilog/sport_rx.v verilog/sport_bidir.v verilog/uart_tx.v; chparam -set TX_TO_DSP_N 4 -set RX_FROM_DSP_N 2 -set SYNC_TX 1 -set NOPLL 1 -set SHARE_PAIRS 1 -set FROM_DSP_EN 0 -set REPORT_LANE0 0 -set MIN_DONE_WORDS 536870912 sport_bidir; synth_ice40 -top sport_bidir -json build/sport_bidir_4x/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_bidir_4x/s.json --pcf verilog/sport_bidir_4x_hx8k.pcf --asc build/sport_bidir_4x/s.asc --freq 62 --seed 9 -q --pcf-allow-unconstrained && icepack build/sport_bidir_4x/s.asc build/sport_bidir_4x/sport_bidir_4x.bin
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_bidir_4x/sport_bidir_4x.bin
adsp2156/sport_fpga_bidir/build/ffff2gib.ldr
```

Test (max 20 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_bidir_4x.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@ffff2gib.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_bidir rx_lanes=4" timeout_ms=390000
delay ms=2000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=ffff_dddd_2gib
```

Verify:

```
def _corruption_gate(extract_dir):
    # Any received-data error is a deterministic FAIL (jk 2026-06-11):
    # a corrupted word is a real defect, never a bench transient, so
    # retrying would only hide it. Scans the raw streams so it fires
    # even when the op timed out before the final report line.
    import sys
    for stream, pats in (
            ('dsp.uart', (r'rx h=\d+ e=(\d+)', r'rx_errors=(\d+)')),
            ('fpga.uart', (r'rx w=[0-9a-f]+ e=([0-9a-f]+)',
                           r'errors_hex=([0-9a-f]+)', r'(ERR) w='))):
        try:
            txt = Verification.load_stream_text(extract_dir, stream)
        except Exception:
            continue
        for pat in pats:
            for m in re.finditer(pat, txt):
                v = m.group(1)
                if v == 'ERR' or int(v, 16) != 0:
                    sys.stderr.write('\033[1;31mDATA CORRUPTION\033[0m '
                                     + stream + ': ' + m.group(0) + '\n')
                    raise HardFail('data corruption: '
                                   + stream + ' ' + m.group(0))


def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    _corruption_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    dtxt = Verification.load_stream_text(extract_dir, 'dsp.uart')
    dm = re.search(r'sport_bidir rx_lanes=(\d+) tx_lanes=(\d+) rx_words=(\d+) rx_errors=(\d+) e0=(\d+) e1=(\d+) e2=(\d+) e3=(\d+) timeouts=(\d+) tx_timeouts=(\d+) overruns=(\d+) slips=(\d+)', dtxt)
    if not dm:
        raise HardFail('no sport_bidir report')
    lanes, words, errs, to, txto, ov, slips = (int(dm.group(i)) for i in (1,3,4,9,10,11,12))
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'uart_expect']
    elapsed = expects[0]['t_end'] - boots[0]['t_start'] if boots and expects else 0
    rate = int(words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'{rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if (lanes == 4 and words == 536870912 and errs == 0 and to == 0
            and txto == 0 and ov == 0 and rate >= 56250000):
        return True
    raise HardFail(f'FFFF-DDDD: errors={errs} ov={ov} words={words}')
```

#### (stale open-loop design, superseded by the pair-shared recipe) FFFF-DDDD 4GiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport4x
cd fpga && yosys -q -p "read_verilog -D SPORT_TX_POSEDGE_OUT verilog/sport_tx_from_dsp_clk.v; chparam -set N 4 sport_tx_from_dsp_clk; synth_ice40 -top sport_tx_from_dsp_clk -json build/sport4x/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport4x/s.json --pcf verilog/sport_tx_prbs_multi_4x_hx8k.pcf --asc build/sport4x/s.asc --freq 40 -q --pcf-allow-unconstrained && icepack build/sport4x/s.asc build/sport4x/sport4x.bin
make -C adsp2156/sport_fpga_4x clean
make -j -C adsp2156/sport_fpga_4x CFLAGS_EXTRA="-DTOTAL_WORDS=1073741824U"
cp adsp2156/sport_fpga_4x/build/main.ldr adsp2156/sport_fpga_4x/build/m4x_4gib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport4x/sport4x.bin
adsp2156/sport_fpga_4x/build/m4x_4gib.ldr
```

Test (max 28 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@blinky.bin
fpga.hx8k:program bin=@sport4x.bin
dsp:uart_open
dsp:boot ldr=@m4x_4gib.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_4x agg_bytes=" timeout_ms=1410000
delay ms=200
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=ffff_dddd_4gib
```

Verify:

```
def _corruption_gate(extract_dir):
    # Any received-data error is a deterministic FAIL (jk 2026-06-11):
    # a corrupted word is a real defect, never a bench transient, so
    # retrying would only hide it. Scans the raw streams so it fires
    # even when the op timed out before the final report line.
    import sys
    for stream, pats in (
            ('dsp.uart', (r'rx h=\d+ e=(\d+)', r'rx_errors=(\d+)')),
            ('fpga.uart', (r'rx w=[0-9a-f]+ e=([0-9a-f]+)',
                           r'errors_hex=([0-9a-f]+)', r'(ERR) w='))):
        try:
            txt = Verification.load_stream_text(extract_dir, stream)
        except Exception:
            continue
        for pat in pats:
            for m in re.finditer(pat, txt):
                v = m.group(1)
                if v == 'ERR' or int(v, 16) != 0:
                    sys.stderr.write('\033[1;31mDATA CORRUPTION\033[0m '
                                     + stream + ': ' + m.group(0) + '\n')
                    raise HardFail('data corruption: '
                                   + stream + ' ' + m.group(0))


def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    _corruption_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'dsp.uart')
    m = re.search(r'sport_4x agg_bytes=(\d+) per_ch_bytes=(\d+) errors0=(\d+) errors1=(\d+) errors2=(\d+) errors3=(\d+).*? timeouts=(\d+) overruns=(\d+) (PASS|FAIL)', text)
    if not m:
        raise HardFail('no sport_4x report')
    agg, pc, e0, e1, e2, e3, to, ov = (int(x) for x in m.groups()[:8])
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[0]['t_end'] - boots[0]['t_start']
    rate = int(pc * 8 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'{rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if rate < 56250000:
        raise HardFail(f'rate {rate} < 30000000')
    if (pc >= 4294967296 and e0 == e1 == e2 == e3 == 0 and to == 0 and ov == 0 and m.group(9) == 'PASS'):
        return True
    raise HardFail(f'FAIL: per_ch={pc} errors=({e0},{e1},{e2},{e3}) timeouts={to}')
```

### FD-DF 2GiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
make -C adsp2156/sport_fpga_bidir clean
make -j -C adsp2156/sport_fpga_bidir CFLAGS_EXTRA="-DRX_N=1U -DTX_N=1U -DTOTAL_WORDS=536870912U -DTX_FIRST"
cp adsp2156/sport_fpga_bidir/build/main.ldr adsp2156/sport_fpga_bidir/build/bidir1x1_2gib.ldr
mkdir -p fpga/build/sport_bidir_1x1
cd fpga && yosys -q -p "read_verilog -D EYE_DELAY verilog/sport_tx_sync_nopll.v verilog/sport_tx_prbs_ser.v verilog/sport_rx.v verilog/sport_bidir.v verilog/uart_tx.v; chparam -set TX_TO_DSP_N 1 -set RX_FROM_DSP_N 1 -set SYNC_TX 1 -set NOPLL 1 -set REPORT_LANE0 0 -set MIN_DONE_WORDS 536870912 sport_bidir; synth_ice40 -top sport_bidir -json build/sport_bidir_1x1/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_bidir_1x1/s.json --pcf verilog/sport_bidir_1x1_hx8k.pcf --asc build/sport_bidir_1x1/s.asc --freq 65 -q --pcf-allow-unconstrained && icepack build/sport_bidir_1x1/s.asc build/sport_bidir_1x1/sport_bidir_1x1.bin
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_bidir_1x1/sport_bidir_1x1.bin
adsp2156/sport_fpga_bidir/build/bidir1x1_2gib.ldr
```

Test (max 18 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_bidir_1x1.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@bidir1x1_2gib.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_bidir rx_lanes=1" timeout_ms=390000
fpga.hx8k:uart_expect sentinel="sport_rx lanes=1" timeout_ms=60000
delay ms=2000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=fd_df_2gib
```

Verify:

```
def _corruption_gate(extract_dir):
    # Any received-data error is a deterministic FAIL (jk 2026-06-11):
    # a corrupted word is a real defect, never a bench transient, so
    # retrying would only hide it. Scans the raw streams so it fires
    # even when the op timed out before the final report line.
    import sys
    for stream, pats in (
            ('dsp.uart', (r'rx h=\d+ e=(\d+)', r'rx_errors=(\d+)')),
            ('fpga.uart', (r'rx w=[0-9a-f]+ e=([0-9a-f]+)',
                           r'errors_hex=([0-9a-f]+)', r'(ERR) w='))):
        try:
            txt = Verification.load_stream_text(extract_dir, stream)
        except Exception:
            continue
        for pat in pats:
            for m in re.finditer(pat, txt):
                v = m.group(1)
                if v == 'ERR' or int(v, 16) != 0:
                    sys.stderr.write('\033[1;31mDATA CORRUPTION\033[0m '
                                     + stream + ': ' + m.group(0) + '\n')
                    raise HardFail('data corruption: '
                                   + stream + ' ' + m.group(0))


def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    _corruption_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    dtxt = Verification.load_stream_text(extract_dir, 'dsp.uart')
    ftxt = Verification.load_stream_text(extract_dir, 'fpga.uart')
    dm = re.search(r'sport_bidir rx_lanes=(\d+) tx_lanes=(\d+) rx_words=(\d+) rx_errors=(\d+) timeouts=(\d+) tx_timeouts=(\d+) overruns=(\d+) slips=(\d+) tx_sent=(\d+) (PASS|FAIL)', dtxt)
    if not dm:
        raise HardFail('no sport_bidir report')
    rx_lanes, rx_words, rx_errors, to, txto, ov, slips = (int(dm.group(i)) for i in (1,3,4,5,6,7,8))
    fm = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', ftxt)
    if not fm:
        sys.stderr.write('no FPGA from_dsp report\n')
        return False
    fpga_words = int(fm.group(2), 16)
    fpga_errors = int(fm.group(3), 16)
    if not (fpga_errors == 0 and fpga_words >= 536870912 and fm.group(4) == 'PASS'):
        raise HardFail(f'D->F FAIL: words={fpga_words} errors={fpga_errors}')
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[0]['t_end'] - boots[0]['t_start']
    fd_rate = int(rx_words * 32 / elapsed) if elapsed > 0 else 0
    df_rate = int(fpga_words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'fd={fd_rate/1e6:.1f}Mbps df={df_rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if fd_rate < 56250000:
        raise HardFail(f'F->D rate {fd_rate} < 60000000')
    if df_rate < 56250000:
        raise HardFail(f'D->F rate {df_rate} < 60000000')
    if (rx_lanes == 1 and rx_errors == 0 and to == 0 and txto == 0 and ov == 0
            and slips == 0 and rx_words >= 536870912 and dm.group(10) == 'PASS'):
        return True
    raise HardFail(f'FAIL: rx_words={rx_words} rx_errors={rx_errors} slips={slips}')
```

### FFDD-DDFF 2GiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
make -C adsp2156/sport_fpga_bidir clean
make -j -C adsp2156/sport_fpga_bidir CFLAGS_EXTRA="-DRX_N=2U -DTX_N=2U -DTOTAL_WORDS=536870912U -DTX_FIRST"
cp adsp2156/sport_fpga_bidir/build/main.ldr adsp2156/sport_fpga_bidir/build/bidir2x2_2gib.ldr
mkdir -p fpga/build/sport_bidir_2x2
cd fpga && yosys -q -p "read_verilog -D EYE_DELAY verilog/sport_tx_sync_nopll.v verilog/sport_tx_prbs_ser.v verilog/sport_rx.v verilog/sport_bidir.v verilog/uart_tx.v; chparam -set TX_TO_DSP_N 2 -set RX_FROM_DSP_N 2 -set SYNC_TX 1 -set NOPLL 1 -set REPORT_LANE0 0 -set MIN_DONE_WORDS 536870912 sport_bidir; synth_ice40 -top sport_bidir -json build/sport_bidir_2x2/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_bidir_2x2/s.json --pcf verilog/sport_bidir_2x2_hx8k.pcf --asc build/sport_bidir_2x2/s.asc --freq 62 --seed 9 -q --pcf-allow-unconstrained && icepack build/sport_bidir_2x2/s.asc build/sport_bidir_2x2/sport_bidir_2x2.bin
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_bidir_2x2/sport_bidir_2x2.bin
adsp2156/sport_fpga_bidir/build/bidir2x2_2gib.ldr
```

Test (max 18 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@sport_bidir_2x2.bin
fpga.hx8k:uart_open
dsp:uart_open
dsp:boot ldr=@bidir2x2_2gib.ldr timeout_ms=15000
dsp:uart_expect sentinel="sport_bidir rx_lanes=2" timeout_ms=390000
fpga.hx8k:uart_expect sentinel="sport_rx lanes=2" timeout_ms=60000
delay ms=2000
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=ffdd_ddff_2gib
```

Verify:

```
def _corruption_gate(extract_dir):
    # Any received-data error is a deterministic FAIL (jk 2026-06-11):
    # a corrupted word is a real defect, never a bench transient, so
    # retrying would only hide it. Scans the raw streams so it fires
    # even when the op timed out before the final report line.
    import sys
    for stream, pats in (
            ('dsp.uart', (r'rx h=\d+ e=(\d+)', r'rx_errors=(\d+)')),
            ('fpga.uart', (r'rx w=[0-9a-f]+ e=([0-9a-f]+)',
                           r'errors_hex=([0-9a-f]+)', r'(ERR) w='))):
        try:
            txt = Verification.load_stream_text(extract_dir, stream)
        except Exception:
            continue
        for pat in pats:
            for m in re.finditer(pat, txt):
                v = m.group(1)
                if v == 'ERR' or int(v, 16) != 0:
                    sys.stderr.write('\033[1;31mDATA CORRUPTION\033[0m '
                                     + stream + ': ' + m.group(0) + '\n')
                    raise HardFail('data corruption: '
                                   + stream + ' ' + m.group(0))


def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    _corruption_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    dtxt = Verification.load_stream_text(extract_dir, 'dsp.uart')
    ftxt = Verification.load_stream_text(extract_dir, 'fpga.uart')
    dm = re.search(r'sport_bidir rx_lanes=(\d+) tx_lanes=(\d+) rx_words=(\d+) rx_errors=(\d+) timeouts=(\d+) tx_timeouts=(\d+) overruns=(\d+) slips=(\d+) tx_sent=(\d+) (PASS|FAIL)', dtxt)
    if not dm:
        raise HardFail('no sport_bidir report')
    rx_lanes, rx_words, rx_errors, to, txto, ov, slips = (int(dm.group(i)) for i in (1,3,4,5,6,7,8))
    fm = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', ftxt)
    if not fm:
        sys.stderr.write('no FPGA from_dsp report\n')
        return False
    fpga_words = int(fm.group(2), 16)
    fpga_errors = int(fm.group(3), 16)
    if not (fpga_errors == 0 and fpga_words >= 536870912 and fm.group(4) == 'PASS'):
        raise HardFail(f'D->F FAIL: words={fpga_words} errors={fpga_errors}')
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[0]['t_end'] - boots[0]['t_start']
    fd_rate = int(rx_words * 32 / elapsed) if elapsed > 0 else 0
    df_rate = int(fpga_words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'fd={fd_rate/1e6:.1f}Mbps df={df_rate/1e6:.1f}Mbps '); sys.stderr.flush()
    if fd_rate < 56250000:
        raise HardFail(f'F->D rate {fd_rate} < 60000000')
    if df_rate < 56250000:
        raise HardFail(f'D->F rate {df_rate} < 60000000')
    if (rx_lanes == 2 and rx_errors == 0 and to == 0 and txto == 0 and ov == 0
            and slips == 0 and rx_words >= 536870912 and dm.group(10) == 'PASS'):
        return True
    raise HardFail(f'FAIL: rx_words={rx_words} rx_errors={rx_errors} slips={slips}')
```

# Plan: unified sport firmware + striped PRBS + cleanup (one re-prove pass)

Goal: integrate three workstreams so the expensive part — re-proving all
8 directions at 2 GiB/lane — happens ONCE, at the end, against one new
codebase instead of three times against moving targets.

Workstreams folded together:
  A. One-PRBS-across-lanes (striping, WORD-round-robin): a single
     PRBS-31 sequence dealt word-by-word across N lanes, so N lanes
     carry one logical stream at N x lane rate. Catches lane
     shorts/swaps/aliasing that today's identical-pattern lanes cannot.
     Aggregate rate numbers become true single-stream throughput.
  B. Firmware merge: one adsp2156/sport app replacing sport_fpga_rx,
     sport_fpga_tx, sport_fpga_bidir. Every direction = a
     (TX_N, RX_N, flags) build point of the same source.
  C. Cleanup notes from missions/fpga-dsp-sport.md (the "## Cleanup
     notes" section): safe-tier deletions, the done_aclk latent bug,
     helper dedup, dead-app removal.

Why together: A changes the on-wire pattern (invalidates proofs), B
changes the binaries (invalidates proofs), C's consolidation tier also
rebuilds binaries. Any one alone forces the same 8-direction re-prove.

---

## Phase 1 — pure deletions (safe tier, ~30 min, no re-prove needed)
From the cleanup notes, items with zero behavior impact on missions:
- FPGA: sport_tx_sync.v, sport_tx_prbs.v, sport_tx_prbs_multi.v (+ their
  orphan pcfs), sport_tx_from_dsp_clk_1 wrapper, dead DIAG forest except
  DIAG_WORDS + DIAG_STATE (keep the tracer infra), literate-source
  Makefile clobber rule fix.
- DSP: sport_fpga_bidir_2x2/, sport_fpga_rx4/, sport_fpga_lb/,
  sport_install_external_loopback, dma_oneshot_config/dma_done,
  -DTX_FIRST warts in mission files, dead knobs (VOLATILE_TXBUF etc).
- Gate: bitstream/ldr bin-diff for the three LIVE apps before/after
  (deletions must not change live binaries). If bin-identical: no bench
  time needed. Run one smoke case (D-F 1 MiB) anyway.

## Phase 2 — the unified app: adsp2156/sport (design + build, no bench)
One main.c, parameterized:
  TX_N      0..4   DSP->FPGA lanes (SPORT4A,0A,5A,1A; clock masters)
  RX_N      0..4   FPGA->DSP lanes (SPORT5B,1B,4B,0B; pair-shared clk/fs)
  TX_NO_REFILL     TX rings free-run as pure clock/FS masters
  TOTAL_WORDS, HALF sizes, SCLK
F-D MIGRATES onto the source-synchronous to_dsp chain here (bidir-style,
~62 Mbps vs the old open-loop 31 Mbps); the open-loop clocking path
retires with sport_fpga_tx.
Carries over (the proven recipe, single copy of each):
  - RUN choreography: low 60 ms at boot, high 500 us before enables,
    trailing 1 ms clock after the last word, low at end.
  - Table-driven PRBS (prbs8_init/prbs31_word_fast) for fills AND checks.
  - tx h= heartbeats (from sport_fpga_rx) on the TX side, now for ALL
    directions; per-lane error fields e0..e3 in the report (from bidir).
  - Expect-chain generator script: emits the per-heartbeat uart_expect
    blocks (hundreds of literal lines per large case) when mission
    cases are (re)generated.
  - Stream pad (+64 words) so the receiver's last counted word flushes.
  - Wrap-flag DMA tracking.
Consolidations from cleanup notes land here for free: single put_str/
put_u32/put_u64, single prbs implementation, dma_which_half/
dma_still_on_half into common/dma.c. sport_fpga_2x/4x die unreferenced.
FPGA side: sport_rx.v + sport_bidir.v stay, with:
  - done_aclk clear bug fixed (cleanup notes, "REAL BUG" item).
  - RESYNC dangling-param note resolved (it is now real logic; update note).
  - PRBS step dedup into a `prbs31_next` include/function.
One report format for every direction (superset line), so all Verify
blocks share one regex.

## Phase 3 — striping (A) on top of the unified app
- TX fill: one sequential PRBS pass dealt round-robin to lane buffers
  (replaces SHARED_TXBUF identical-fill).
- FPGA RX chan: parameter STRIDE_N; expected-LFSR does its 32-bit
  advance per word plus a constant 32*(N-1)-bit jump at word boundary
  (precomputed XOR network; the jump-by-k map is linear).
- FPGA nopll TX: same boundary jump, per-lane start offset = 32*k bits.
- DSP RX check: per-lane LFSR state with table-stepped stride jumps.
- N=1 degenerates to today's behavior exactly (jump = identity), so
  D-F/F-D are regression-safe by construction.
- Verify lines gain stripe=N so a misconfigured build cannot
  silently pass as striped.

## Phase 4 — the single re-prove pass (bench, ~2.5 h)
Order: 1 MiB smoke per direction first (8 x ~2 min, catches gross
breakage cheaply), then the 8 ladders WITH the 128-byte steps restored
(the RUN gate + real handshake should make them viable; park again only
on misbehavior), then the main mission file end-to-end.
Rules: one direction at a time; on failure, fix forward only if the
cause is obvious within ~2 cycles, else fall back to the Phase-0
baseline for that direction and continue (mission must never be
un-runnable). x marks in the table stay untouched (they describe the
criteria, which striping still satisfies: PRBS-31 on every lane).

## Phase 5 — retire the old apps + mission file swap
- Point all mission files at adsp2156/sport; delete sport_fpga_rx,
  sport_fpga_tx, sport_fpga_bidir, sport_fpga_2x, sport_fpga_4x.
- Update the Cleanup notes section: mark items done, leave the
  not-undertaken ones explicitly listed.
- Re-run the main mission file one final time (the "passes completely
  after cleanup" gate).
