# FPGA <-> DSP SPORT link

Directions and required per-lane SPORT bit clocks:

| Direction | FPGA-originated lanes | DSP-originated lanes | OK? |
| --------- | --------------------: | -------------------: | --- |
| D-F       |                     - |             60+ Mbps | x   |
| DD-FF     |                     - |             60+ Mbps | x   |
| DDDD-FFFF |                     - |             60+ Mbps | x   |
| F-D       |              30+ Mbps |                    - | x   |
| FF-DD     |              30+ Mbps |                    - | x   |
| FFFF-DDDD |              30+ Mbps |                    - | x   |
| FD-DF     |              30+ Mbps |             60+ Mbps | x   |
| FFDD-DDFF |              30+ Mbps |             60+ Mbps | x   |

The FPGA-originated rate is capped by the ADSP-2156x programmed SPORT
clock limit when receiving data/frame sync. The DSP-originated rate uses
the programmed SPORT transmit clock.

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
make -j -C adsp2156/sport_fpga_rx CFLAGS_EXTRA="-DNCH=1U -DN_WORDS=536870912U -DDATA_INDEP_FS=1 -DHALF_WORDS=65536U -DSPORT_SCLK_HZ=60000000U"
cp adsp2156/sport_fpga_rx/build/main.ldr adsp2156/sport_fpga_rx/build/dma_2gib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_rx1/sport_rx1.bin
adsp2156/sport_fpga_rx/build/dma_2gib.ldr
```

Test (max 14 min):

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
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
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
    sys.stderr.write(f'lanes={lanes} words={words} errors={errors} {m.group(4)} heartbeats={nprog}\n')
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'fpga.hx8k' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[-1]['t_end'] - boots[0]['t_start']
    rate = int(words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'rate per_lane_bps={rate} ({rate/1e6:.1f} Mbps)\n')
    if rate < 58000000:
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
cd fpga && yosys -q -p "read_verilog verilog/sport_rx.v verilog/uart_tx.v; chparam -set N 2 -set MIN_DONE_WORDS 536870912 sport_rx; synth_ice40 -top sport_rx -json build/sport_rx2/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_rx2/s.json --pcf verilog/sport_rx_hx8k.pcf --asc build/sport_rx2/s.asc --freq 65 --seed 20 -q --pcf-allow-unconstrained && icepack build/sport_rx2/s.asc build/sport_rx2/sport_rx2.bin
make -C adsp2156/sport_fpga_rx clean
make -j -C adsp2156/sport_fpga_rx CFLAGS_EXTRA="-DNCH=2U -DN_WORDS=536870912U -DDATA_INDEP_FS=1 -DHALF_WORDS=65536U -DSPORT_SCLK_HZ=60833333U"
cp adsp2156/sport_fpga_rx/build/main.ldr adsp2156/sport_fpga_rx/build/dma_2gib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_rx2/sport_rx2.bin
adsp2156/sport_fpga_rx/build/dma_2gib.ldr
```

Test (max 17 min):

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
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'fpga.uart')
    m = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', text)
    if not m:
        raise HardFail('no sport_rx report')
    lanes, words, errors = int(m.group(1)), int(m.group(2), 16), int(m.group(3), 16)
    sys.stderr.write(f'lanes={lanes} words={words} errors={errors} {m.group(4)}\n')
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'fpga.hx8k' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[0]['t_end'] - boots[0]['t_start']
    rate = int(words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'rate per_lane_bps={rate} ({rate/1e6:.1f} Mbps)\n')
    if rate < 60000000:
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
cd fpga && yosys -q -p "read_verilog verilog/sport_rx.v verilog/uart_tx.v; chparam -set N 4 -set MIN_DONE_WORDS 536870912 sport_rx; synth_ice40 -top sport_rx -json build/sport_rx4/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_rx4/s.json --pcf verilog/sport_rx4_hx8k.pcf --asc build/sport_rx4/s.asc --pre-pack prepack_rx4.py --seed 20 -q --pcf-allow-unconstrained && icepack build/sport_rx4/s.asc build/sport_rx4/sport_rx4.bin
make -C adsp2156/sport_fpga_rx clean
make -j -C adsp2156/sport_fpga_rx CFLAGS_EXTRA="-DNCH=4U -DN_WORDS=536870912U -DDATA_INDEP_FS=1 -DHALF_WORDS=65536U -DSPORT_SCLK_HZ=60833333U"
cp adsp2156/sport_fpga_rx/build/main.ldr adsp2156/sport_fpga_rx/build/dma_2gib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_rx4/sport_rx4.bin
adsp2156/sport_fpga_rx/build/dma_2gib.ldr
```

Test (max 17 min):

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
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'fpga.uart')
    m = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', text)
    if not m:
        raise HardFail('no sport_rx report')
    lanes, words, errors = int(m.group(1)), int(m.group(2), 16), int(m.group(3), 16)
    sys.stderr.write(f'lanes={lanes} words={words} errors={errors} {m.group(4)}\n')
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'fpga.hx8k' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[0]['t_end'] - boots[0]['t_start']
    rate = int(words * 32 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'rate per_lane_bps={rate} ({rate/1e6:.1f} Mbps)\n')
    if rate < 60000000:
        raise HardFail(f'rate {rate} < 60000000')
    if lanes == 4 and errors == 0 and words >= 536870912 and m.group(4) == 'PASS':
        return True
    raise HardFail(f'FAIL: lanes={lanes} words={words} errors={errors}')
```

### F-D 2GiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
mkdir -p fpga/build/sport
cd fpga && yosys -q -p "read_verilog -D SPORT_TX_POSEDGE_OUT verilog/sport_tx_from_dsp_clk.v; chparam -set N 1 sport_tx_from_dsp_clk; synth_ice40 -top sport_tx_from_dsp_clk -json build/sport/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport/s.json --pcf verilog/sport_tx_prbs_hx8k.pcf --asc build/sport/s.asc --freq 40 -q --pcf-allow-unconstrained && icepack build/sport/s.asc build/sport/sport_tx_prbs.bin
make -C adsp2156/sport_fpga_tx clean
make -j -C adsp2156/sport_fpga_tx build/main.ldr CFLAGS_EXTRA="-DTOTAL_BYTES=2147483648ULL -DTOTAL_WORDS=536870912U -DRX_SAMPLE_RISING=1 -DRX_SHIFT_LEFT_1=1 -DSPORT_FSDIV=31U"
cp adsp2156/sport_fpga_tx/build/main.ldr adsp2156/sport_fpga_tx/build/fd_2gib.ldr
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport/sport_tx_prbs.bin
adsp2156/sport_fpga_tx/build/fd_2gib.ldr
```

Test (max 14 min):

```
delay ms=3000
dsp:reset
fpga.hx8k:program bin=@blinky.bin
fpga.hx8k:program bin=@sport_tx_prbs.bin
dsp:uart_open
dsp:boot ldr=@fd_2gib.ldr timeout_ms=30000
dsp:uart_expect sentinel="sport_fpga_tx_prbs_long bytes=" timeout_ms=720000
delay ms=200
scope:capture chans="C2"
dsp:uart_close
fpga.hx8k:program bin=@blinky.bin
mark tag=f_d_2gib
```

Verify:

```
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    text = Verification.load_stream_text(extract_dir, 'dsp.uart')
    m = re.search(r'sport_fpga_tx_prbs_long bytes=(\d+) words=\d+ errors=(\d+) firsterr=-?\d+.*? timeouts=(\d+) overruns=(\d+).*? (PASS|FAIL)', text)
    if not m:
        raise HardFail('no SPORT report on dsp.uart')
    nbytes, errors, timeouts, overruns = (int(x) for x in m.groups()[:4])
    sys.stderr.write(f'bytes={nbytes} errors={errors} timeouts={timeouts} overruns={overruns} {m.group(5)}\n')
    ops = Verification.load_ops(extract_dir)
    programs = [op for op in ops if op.get('device') == 'fpga.hx8k' and op.get('verb') == 'program']
    expects = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'uart_expect']
    if len(programs) < 2 or not expects:
        return False
    elapsed = expects[0]['t_end'] - programs[1]['t_start']
    rate = int(nbytes * 8 / elapsed) if elapsed > 0 else 0
    sys.stderr.write(f'rate bps={rate} ({rate/1e6:.1f} Mbps)\n')
    if rate < 30000000:
        raise HardFail(f'rate {rate} < 30000000')
    if nbytes >= 2147483648 and errors == 0 and timeouts == 0 and overruns == 0 and m.group(5) == 'PASS':
        return True
    raise HardFail(f'FAIL: bytes={nbytes} errors={errors} timeouts={timeouts} overruns={overruns}')
```

### FF-DD 2GiB

Build:

```
make -C fpga build/blinky/hx8k/blinky.bin
make -C adsp2156/sport_fpga_bidir clean
make -j -C adsp2156/sport_fpga_bidir CFLAGS_EXTRA="-DRX_N=2U -DTX_N=2U -DTOTAL_WORDS=536870912U -DTX_NO_REFILL"
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

Test (max 9 min):

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
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    dtxt = Verification.load_stream_text(extract_dir, 'dsp.uart')
    ftxt = Verification.load_stream_text(extract_dir, 'fpga.uart')
    dm = re.search(r'sport_bidir rx_lanes=(\d+) tx_lanes=(\d+) rx_words=(\d+) rx_errors=(\d+) timeouts=(\d+) tx_timeouts=(\d+) overruns=(\d+) slips=(\d+) tx_sent=(\d+) (PASS|FAIL)', dtxt)
    if not dm:
        raise HardFail('no sport_bidir report')
    rx_lanes, rx_words, rx_errors, to, txto, ov, slips = (int(dm.group(i)) for i in (1,3,4,5,6,7,8))
    sys.stderr.write(f'F->D rx_words={rx_words} rx_errors={rx_errors} slips={slips} timeouts={to} overruns={ov} {dm.group(10)}\n')
    ops = Verification.load_ops(extract_dir)
    boots = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'boot']
    expects = [op for op in ops if op.get('device') == 'dsp' and op.get('verb') == 'uart_expect']
    if not boots or not expects:
        return False
    elapsed = expects[0]['t_end'] - boots[0]['t_start']
    fd_rate = int(rx_words * 32 / elapsed) if elapsed > 0 else 0
    df_rate = 0
    sys.stderr.write(f'fd_rate={fd_rate/1e6:.1f} Mbps df_rate={df_rate/1e6:.1f} Mbps\n')
    if fd_rate < 30000000:
        raise HardFail(f'F->D rate {fd_rate} < 30000000')
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
cd fpga && yosys -q -p "read_verilog -D EYE_DELAY verilog/sport_tx_sync_nopll.v verilog/sport_tx_prbs_ser.v verilog/sport_rx.v verilog/sport_bidir.v verilog/uart_tx.v; chparam -set TX_TO_DSP_N 4 -set RX_FROM_DSP_N 2 -set SYNC_TX 1 -set NOPLL 1 -set SHARE_PAIRS 1 -set REPORT_LANE0 0 -set MIN_DONE_WORDS 536870912 sport_bidir; synth_ice40 -top sport_bidir -json build/sport_bidir_4x/s.json" && nextpnr-ice40 --hx8k --package ct256 --json build/sport_bidir_4x/s.json --pcf verilog/sport_bidir_4x_hx8k.pcf --asc build/sport_bidir_4x/s.asc --freq 62 --seed 9 -q --pcf-allow-unconstrained && icepack build/sport_bidir_4x/s.asc build/sport_bidir_4x/sport_bidir_4x.bin
```

Artifacts:

```
fpga/build/blinky/hx8k/blinky.bin
fpga/build/sport_bidir_4x/sport_bidir_4x.bin
adsp2156/sport_fpga_bidir/build/ffff2gib.ldr
```

Test (max 16 min):

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
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
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
    sys.stderr.write(f'FFFF->DDDD lanes={lanes} words={words} errors={errs} ov={ov} slips={slips} per_lane_rate={rate/1e6:.1f} Mbps\n')
    if (lanes == 4 and words == 536870912 and errs == 0 and to == 0
            and txto == 0 and ov == 0 and rate >= 30000000):
        return True
    raise HardFail(f'FFFF-DDDD: errors={errs} ov={ov} words={words}')
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

Test (max 9 min):

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
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    dtxt = Verification.load_stream_text(extract_dir, 'dsp.uart')
    ftxt = Verification.load_stream_text(extract_dir, 'fpga.uart')
    dm = re.search(r'sport_bidir rx_lanes=(\d+) tx_lanes=(\d+) rx_words=(\d+) rx_errors=(\d+) timeouts=(\d+) tx_timeouts=(\d+) overruns=(\d+) slips=(\d+) tx_sent=(\d+) (PASS|FAIL)', dtxt)
    if not dm:
        raise HardFail('no sport_bidir report')
    rx_lanes, rx_words, rx_errors, to, txto, ov, slips = (int(dm.group(i)) for i in (1,3,4,5,6,7,8))
    sys.stderr.write(f'F->D rx_words={rx_words} rx_errors={rx_errors} slips={slips} timeouts={to} overruns={ov} {dm.group(10)}\n')
    fm = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', ftxt)
    if not fm:
        sys.stderr.write('no FPGA from_dsp report\n')
        return False
    fpga_words = int(fm.group(2), 16)
    fpga_errors = int(fm.group(3), 16)
    sys.stderr.write(f'D->F words={fpga_words} errors={fpga_errors} {fm.group(4)}\n')
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
    sys.stderr.write(f'fd_rate={fd_rate/1e6:.1f} Mbps df_rate={df_rate/1e6:.1f} Mbps\n')
    if fd_rate < 60000000:
        raise HardFail(f'F->D rate {fd_rate} < 60000000')
    if df_rate < 60000000:
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

Test (max 9 min):

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
def check(extract_dir):
    import sys
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    dtxt = Verification.load_stream_text(extract_dir, 'dsp.uart')
    ftxt = Verification.load_stream_text(extract_dir, 'fpga.uart')
    dm = re.search(r'sport_bidir rx_lanes=(\d+) tx_lanes=(\d+) rx_words=(\d+) rx_errors=(\d+) timeouts=(\d+) tx_timeouts=(\d+) overruns=(\d+) slips=(\d+) tx_sent=(\d+) (PASS|FAIL)', dtxt)
    if not dm:
        raise HardFail('no sport_bidir report')
    rx_lanes, rx_words, rx_errors, to, txto, ov, slips = (int(dm.group(i)) for i in (1,3,4,5,6,7,8))
    sys.stderr.write(f'F->D rx_words={rx_words} rx_errors={rx_errors} slips={slips} timeouts={to} overruns={ov} {dm.group(10)}\n')
    fm = re.search(r'sport_rx lanes=(\d+) per_ch_words_hex=([0-9a-fA-F]+) errors_hex=([0-9a-fA-F]+) (PASS|FAIL)', ftxt)
    if not fm:
        sys.stderr.write('no FPGA from_dsp report\n')
        return False
    fpga_words = int(fm.group(2), 16)
    fpga_errors = int(fm.group(3), 16)
    sys.stderr.write(f'D->F words={fpga_words} errors={fpga_errors} {fm.group(4)}\n')
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
    sys.stderr.write(f'fd_rate={fd_rate/1e6:.1f} Mbps df_rate={df_rate/1e6:.1f} Mbps\n')
    if fd_rate < 60000000:
        raise HardFail(f'F->D rate {fd_rate} < 60000000')
    if df_rate < 60000000:
        raise HardFail(f'D->F rate {df_rate} < 60000000')
    if (rx_lanes == 2 and rx_errors == 0 and to == 0 and txto == 0 and ov == 0
            and slips == 0 and rx_words >= 536870912 and dm.group(10) == 'PASS'):
        return True
    raise HardFail(f'FAIL: rx_words={rx_words} rx_errors={rx_errors} slips={slips}')
```

## Cleanup notes (agent1 code review, 2026-06-09 — no changes applied yet)

Review of all fpga/verilog SPORT RTL and adsp2156 SPORT firmware, prompted by
the suspicion that the code is more complicated than simple PRBS shifting
needs. Verdict: the *live* data paths are sound (ping-pong DMA TX/RX is the
documented fix for polled underruns; the no-PLL bidir transmitter is already
minimal), but roughly half the source volume is dead experiments, copy-paste,
and diagnostics with no build. FPGA cleanups are gated on placement risk:
proven bitstreams are placement-sensitive, so each item is tagged
**safe** (not elaborated into any mission netlist; verify by rebuilding each
proven config and bin-diffing) or **re-place** (changes a proven netlist;
needs a scheduled re-prove pass at 2 GB — per-direction proofs, not the small
debug cases).

#### Timeout sizing rule (applied 2026-06-09)

transfer_s = N_WORDS * 32 / bit_clk per lane. uart_expect timeout_ms >=
1.25 * transfer + 30 s. Case budget >= build (~40 s) + 2 * (bench overhead
~30 s + 1.15 * transfer) + one 30 s retry backoff, rounded up to whole
minutes — one transient bench flake must not fail a 2 GB proof. (Observed
flake: fpga.uart emitted ~200 garbage bytes during a 2.3 s dsp:reset and the
FPGA never reported; retry passed cleanly.)

#### FPGA (fpga/verilog) — delete first, all "safe" tier (~450 lines)

- `sport_tx_sync.v`: dead + violates the no-PLL criterion. Not on any mission
  read_verilog line; only referenced by the never-elaborated `withpll` branch
  in sport_bidir.v:51-61 (mission always sets NOPLL=1). Its PH_PATTERN path
  also rotted (transmits a counter, lfsr regs feed nothing). Delete file +
  `withpll` branch + `SYNC_PH` param + unused `s_ad0/s_aclk/s_afs` wires.
- `sport_tx_prbs.v`: dead, PLL-based, superseded. Its namesake pcf
  (sport_tx_prbs_hx8k.pcf) no longer even matches its ports — the pcf now
  serves sport_tx_from_dsp_clk. Delete file + `BOARDS_sport_tx_prbs` Makefile
  row.
- `sport_tx_prbs_multi.v`: dead, PLL-based. The "multi" pcfs are used with
  sport_tx_from_dsp_clk as top. Delete.
- `sport_tx_prbs_ser.v`: read by both bidir recipes but never instantiated
  (SYNC_TX=1 makes the `free_tx` branch dead); yosys drops it at hierarchy.
  Deleting it requires touching the two mission build lines — do as one
  commit with bin-diff check, or leave (costs nothing at synth).
- `sport_rx.v` `RESYNC` parameter: declared/forwarded at 4 sites, set to 1 by
  sport_bidir.v:82, but NO logic reads it — so proven bitstreams contain no
  resync (criteria factually met) while the source *claims* a forbidden
  mechanism. Delete the parameter at all 4 sites (safe: drives nothing).
- `sport_tx_from_dsp_clk.v`: `sport_tx_from_dsp_clk_1` wrapper (143-158)
  never used as a top — delete (safe). `SPORT_TX_FORCE_ZERO/ONE` ifdefs are
  dead but their removal is re-place tier.
- Stale literate sources can clobber proven RTL: fpga/Makefile rule
  `verilog/%.v: src/%.nw` + outdated `src/sport_rx.nw` / `src/sport_tx_prbs.nw`
  (2026-05-22, pre-mission) will silently regenerate and REPLACE the proven
  667-line sport_rx.v (and two pcfs) if the .nw ever looks newer. Delete the
  stale .nw files (or re-tangle them from the current .v). Safe; removes a
  real hazard.

#### FPGA — re-place tier (schedule with a 2 GB re-prove pass)

- `sport_rx.v` DIAG forest: only `DIAG_WORDS` is used (D-F 10 words case).
  Dead defines: DIAG_RAW, DIAG_FORCE_REPORT, DIAG_FORCE_LIVE, DIAG_FIRST,
  DIAG_MISMATCH, DIAG_INDEX, DIAG_WINDOW_START, SAMPLE_POS/NEG, NO_IOREG —
  plus 13 constant-zero 32-bit ports per lane (first_rx/first_exp/first_idx,
  diag0..9) threaded through arrays and instantiations. ~200 of 667 lines.
  Netlist should be bit-identical after strip (all ifdef-d out or
  constant-trimmed) — gate on bin-diff of every proven config.
- REAL BUG, sport_rx.v:113: the only `done_aclk` clear is inside
  `if (!run && !done_aclk && !started)` — unreachable once done_aclk is set.
  After a spurious done (stale pre-boot SPORT activity with RUN stuck high
  from a wedged DSP), a fresh RUN cycle re-arms shifting with stale
  lfsr/wcount but the one-shot report can never fire again until the FPGA is
  reprogrammed. Fix: clear done_aclk (and clk12-side done_r/reported) on a
  RUN rising edge. Only bites standalone RX configs (bidir ties run=1).
  Schedule as its own change + re-prove, not inside a cleanup commit.
- PCFs: keep the subset-duplicated rx pcfs (nextpnr errors on unknown ports;
  merging changes the flow). The three `sport_tx_prbs*_hx8k.pcf` names are
  fossils (they constrain sport_tx_from_dsp_clk tops) — rename only in
  lockstep with the mission build lines, or just comment.
- PRBS-31 step is duplicated in each surviving module (~2 lines each);
  factoring would touch three proven netlists for no payoff — leave.

#### DSP (adsp2156) — pure deletions, zero behavior change

- `sport_fpga_bidir_2x2/`: 4-line #include wrapper; mission builds 2x2 from
  sport_fpga_bidir with -DRX_N=2 -DTX_N=2. Delete dir.
- `sport_fpga_rx4/`: obsolete polled predecessor (the documented ~51 Mbit/s
  underrunning one). Referenced nowhere. Delete dir.
- `sport_fpga_lb/`: internal SRU loopback demo, not in any mission. Delete
  (it is the only caller of sport_rx_ready and one of two of
  sport_install_internal_loopback).
- `common/sport.c`: `sport_install_external_loopback` (0 callers) and
  `sport_route_rx_master_a_to_pins` (only caller is a never-enabled ifdef in
  sport_fpga_2x) — delete both + sport.h decls (~75 lines).
- `common/dma.c`: `dma_oneshot_config` + `dma_done` have 0 callers anywhere.
  Delete (+ dma.h decls).
- Mission-file wart: `-DTX_FIRST` is passed to all four bidir builds but
  TX_FIRST appears nowhere in the firmware source — no-op flag (historical;
  the old .ldr-size lore about TX_FIRST is stale). Drop from the build lines
  when next touching them.

#### DSP — duplication worth consolidating (~400-450 lines; rebuilt .ldr, same behavior; re-prove 2 GB per affected direction after)

- `put_str`/`put_u32` x7, `put_i32` x3, `put_u64` x3 (two different
  implementations), `put_hex*` x4 across the main.c files → common/print.h.
  Side benefit: assert.c could drop printf (the printf varargs bug is then
  unreachable; note that bug lives in adsp2156/sport/ and sport_dma/ demos,
  NOT in any mission dir — mission firmware never calls printf).
- `prbs31_word` x5 in 2 implementations (unrolled-macro and table-driven;
  same x^31+x^28+1 stream, seed 0x7fffffff, MSB-first) → common/prbs.h.
- `dma_which_half`/`dma_still_on_half` x4 near-identical → common/dma.c.
- `sport_fpga_2x` vs `sport_fpga_4x`: ~80% identical (opposite-direction
  counterpart of sport_fpga_rx); could merge into one NCH-parameterized
  DSP-RX app. 2x also carries dead pin-variant tables (USE_SPORT5_0 etc.),
  a dead 92.1875 MHz clocks block, dead RX_SHIFT_* alignment branches,
  PINPOINT/ACTIVE/CHECK_MASK knobs, and trace prints — ~572 -> ~250 lines
  before merging.
- Dead knobs in used dirs (no build passes them): VOLATILE_TXBUF,
  TXBUF_DEFAULT_SECTION, DIAG (sport_fpga_rx); DIAG_FIRST_WORDS, dbg_got/
  dbg_exp written-never-printed, wrap_misses never incremented, vestigial
  `locked` (sport_fpga_tx); RX_PRBS_SKIP_WORDS, START_TIMEOUT/_WAIT_LOOPS,
  DIAG_FIRST (sport_fpga_bidir).
- Constraint for ALL firmware cleanups: every Verify regex anchors on the
  final report line (prefixes `sport_rx`, `sport_fpga_tx_prbs_long`,
  `sport_2x agg_bytes=`, `sport_4x`, `sport_bidir rx_lanes=`); keep those
  lines byte-compatible. Boot banners and step-trace prints are unmatched
  and freely deletable.
