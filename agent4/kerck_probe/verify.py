#!/usr/bin/env python3
"""Minimal verify for kerck-probe blocks. Pass if the firmware emitted a
twin summary line for 16777216 B; print pass1_ms so we can analyze."""
import os, re, sys

UART = "streams/mp135.uart.bin"


def _read():
    if not os.path.isfile(UART):
        sys.stderr.write(f"{UART} missing\n")
        return b""
    with open(UART, "rb") as f:
        return f.read()


def main(argv):
    bullet = argv[1] if len(argv) > 1 else ""
    raw = _read()
    pat = rb"twin\s+16777216\s+B\s+quad\s+raw[^\r\n]*"
    m = re.search(pat, raw)
    if not m:
        sys.stderr.write("no twin summary line\n")
        sys.stderr.write(raw[-512:].decode("ascii", "replace") + "\n")
        return 1
    line = m.group(0).decode("ascii", "replace")
    pass1_m = re.search(r"pass1=(\d+)\s+ms", line)
    presc_m = re.search(r"presc=(\d+)", line)
    fe_m = re.search(r"firsterr=(-?\d+)", line)
    crc_m = re.search(r"crc32=([0-9a-f]+)", line)
    pass1_ms = int(pass1_m.group(1)) if pass1_m else None
    presc = int(presc_m.group(1)) if presc_m else None
    fe = int(fe_m.group(1)) if fe_m else None
    crc = crc_m.group(1) if crc_m else "?"
    sys.stdout.write(
        f"presc={presc} pass1_ms={pass1_ms} firsterr={fe} crc32={crc} "
        f"line={line}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
