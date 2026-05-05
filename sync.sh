#!/bin/sh
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Jakob Kastelic
set -e

git -C adsp2156 pull && git -C adsp2156 push
git -C fpga pull && git -C fpga push
git -C selache pull && git -C selache push
git -C test_serv pull && git -C test_serv push
git -C stm32mp135_test_board/bootloader pull && git -C stm32mp135_test_board/bootloader push
git -C stm32mp135_test_board pull && git -C stm32mp135_test_board push
git -c submodule.recurse=false pull && git push
