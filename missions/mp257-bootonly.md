# STM32MP257F-DK boot-only firmware check

Boot the existing SD-card image through the freshly built USB TF-A/FIP firmware
without rewriting the SD card.

### Boot existing SD image

Build: nothing required.

Artifacts:

```
stm32mp257_test_board/buildroot/output/images/tf-a-stm32mp257_dk_usb.stm32
stm32mp257_test_board/buildroot/output/images/fip-ddr-stm32mp257_dk_usb.bin
stm32mp257_test_board/buildroot/output/images/fip-stm32mp257_dk_usb.bin
stm32mp257_test_board/config/mp257-bootonly.tsv
```

Test (max 90 s):

```
bench_mcu:reset_dut
mp257.evb-uart1:uart_open
delay ms=6000
inventory
dfu.mp257:flash_layout layout=@mp257-bootonly.tsv
mp257.evb-uart1:uart_write data="\x03\x03"
delay ms=2000
mp257.evb-uart1:uart_write data="\r"
mp257.evb-uart1:uart_write data="run bootcmd_mmc0\r"
mp257.evb-uart1:uart_expect sentinel="~ #" timeout_ms=55000
mp257.evb-uart1:uart_close
mark tag=boot
```

Verify:

```
def check(extract_dir):
    return Verification.manifest_clean(extract_dir)
```
