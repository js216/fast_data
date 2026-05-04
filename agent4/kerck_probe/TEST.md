# AXI clock triangulation (round 7)

Round 6 showed AXI matters: at AXI=133 MHz (AXI_Div=2), pass1_ms jumped
from 398 -> 536. Linear model fit:
   T_overhead = 2.19 * AXI_period + 3.27 ns
This round verifies the model with AXI=88.8 MHz (AXI_Div=3) and
AXI=66.6 MHz (AXI_Div=4).

  | AXI MHz | AXI_period | linear-model overhead | pred pass1_ms |
  |---------|------------|------------------------|---------------|
  | 266.5   | 3.76 ns    | 11.51 ns               | 398 (measured) |
  | 133.25  | 7.51 ns    | 19.74 ns               | 536 (measured) |
  | 88.83   | 11.26 ns   | 27.93 ns               | 673           |
  | 66.625  | 15.01 ns   | 36.15 ns               | 811           |

Variant AX88: AXI=88.8 MHz (AXI_Div=3).

```
fpga.hx1k:program bin=@spi_quad.bin
bench_mcu:reset_dut  # blobs: @main_axi_div3.stm32 (referenced from flash_axi_div3.tsv)
delay ms=2500
dfu.evb:flash_layout layout=@flash_axi_div3.tsv no_reconnect=true
mp135.evb:uart_open
mp135.evb:uart_expect sentinel="JEDEC ID:" timeout_ms=10000
delay ms=300
mp135.evb:uart_write data="p 3 0\r"
delay ms=200
mp135.evb:uart_write data="T 16777216\r"
mp135.evb:uart_expect sentinel="twin_pass1_done" timeout_ms=180000
mp135.evb:uart_expect sentinel="twin 16777216 B quad raw" timeout_ms=180000
mp135.evb:uart_close
```

- Check variant AX88 captured

Variant AX66: AXI=66.6 MHz (AXI_Div=4).

```
fpga.hx1k:program bin=@spi_quad.bin
bench_mcu:reset_dut  # blobs: @main_axi_div4.stm32 (referenced from flash_axi_div4.tsv)
delay ms=2500
dfu.evb:flash_layout layout=@flash_axi_div4.tsv no_reconnect=true
mp135.evb:uart_open
mp135.evb:uart_expect sentinel="JEDEC ID:" timeout_ms=10000
delay ms=300
mp135.evb:uart_write data="p 3 0\r"
delay ms=200
mp135.evb:uart_write data="T 16777216\r"
mp135.evb:uart_expect sentinel="twin_pass1_done" timeout_ms=180000
mp135.evb:uart_expect sentinel="twin 16777216 B quad raw" timeout_ms=180000
mp135.evb:uart_close
```

- Check variant AX66 captured
