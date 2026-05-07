#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Jakob Kastelic

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOARD = ROOT / "stm32mp135_test_board"
LINUX = BOARD / "linux"
OUT_DIR = BOARD / "build" / "kernel-clock-bringup"
DTS_NAME = "stm32mp135f-dk-no-clk-ignore-unused"
SRC_DTS = BOARD / "config" / "stm32mp135f-dk.dts"
OUT_DTS = OUT_DIR / f"{DTS_NAME}.dts"
LINUX_DTS = LINUX / "arch" / "arm" / "boot" / "dts" / f"{DTS_NAME}.dts"
LINUX_DTB = LINUX / "arch" / "arm" / "boot" / "dts" / f"{DTS_NAME}.dtb"
OUT_IMG = OUT_DIR / "sdcard.no-clk-ignore-unused.img"
ROOTFS = BOARD / "buildroot" / "output" / "images" / "rootfs.ext2"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not ROOTFS.exists():
        subprocess.run(["make", "-C", str(BOARD), "br"], check=True)

    text = SRC_DTS.read_text()
    old = 'bootargs = "root=/dev/mmcblk0p3 clk_ignore_unused";'
    new = 'bootargs = "root=/dev/mmcblk0p3";'
    if old not in text:
        raise SystemExit(f"{SRC_DTS} does not contain expected bootargs")
    OUT_DTS.write_text(text.replace(old, new, 1))

    try:
        LINUX_DTS.write_text(OUT_DTS.read_text())
        subprocess.run(
            [
                "make",
                "-C",
                str(LINUX),
                "ARCH=arm",
                "CROSS_COMPILE=arm-linux-gnueabihf-",
                f"{DTS_NAME}.dtb",
            ],
            check=True,
        )
        subprocess.run(
            [
                "python3",
                str(BOARD / "bootloader" / "scripts" / "sdimage.py"),
                str(OUT_IMG),
                str(BOARD / "bootloader" / "build" / "main.stm32"),
                "--partition",
                str(LINUX / "arch" / "arm" / "boot" / "zImage"),
                "--partition",
                str(LINUX_DTB),
                "--partition",
                str(ROOTFS),
            ],
            check=True,
        )
    finally:
        LINUX_DTS.unlink(missing_ok=True)
        LINUX_DTB.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
