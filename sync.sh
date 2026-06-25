#!/bin/sh
set -e

echo unix-v7-c99 && git -C unix-v7-c99 pull && git -C unix-v7-c99 push
echo adsp2156 && git -C adsp2156 pull && git -C adsp2156 push
echo fpga && git -C fpga pull && git -C fpga push
echo selache && git -C selache pull && git -C selache push
echo test_serv && git -C test_serv pull && git -C test_serv push
echo stm32mp135_test_board/bootloader && git -C stm32mp135_test_board/bootloader pull && git -C stm32mp135_test_board/bootloader push
echo stm32mp135_test_board && git -C stm32mp135_test_board pull && git -C stm32mp135_test_board push
echo stm32mp135_test_board/linux && git -C stm32mp135_test_board submodule update --init linux
echo stm32mp257_test_board && git -C stm32mp257_test_board pull && git -C stm32mp257_test_board push
git -c submodule.recurse=false pull && git push
