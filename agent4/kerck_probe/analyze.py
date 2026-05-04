#!/usr/bin/env python3
"""Compute T_overhead for each kerck-probe variant and compare to
ker_ck-paced (7.55 cyc/byte) vs HCLK6-paced (11.5 ns) predictions."""
import glob, os, re, sys

# (ck_qspi_hz, presc) per variant, in test-plan order.
VARIANTS = [
    ("528 MHz", 528_000_000, 3),
    ("656 MHz", 656_000_000, 3),
    ("800 MHz", 800_000_000, 4),
]
N_BYTES = 16777216
LANES = 4

def read_uart(d):
    p = os.path.join(d, "streams", "mp135.uart.bin")
    if not os.path.isfile(p):
        return b""
    with open(p, "rb") as f:
        return f.read()

def find_pass1(raw):
    m = re.search(rb"twin\s+16777216\s+B\s+quad\s+raw[^\r\n]*", raw)
    if not m:
        return None
    line = m.group(0).decode("ascii", "replace")
    pass1_m = re.search(r"pass1=(\d+)\s+ms", line)
    return int(pass1_m.group(1)) if pass1_m else None

# Glob test_out and pair with VARIANTS in chronological order.
out_dirs = sorted(glob.glob("test_out/*"), key=os.path.getmtime)
results = []
for d in out_dirs:
    raw = read_uart(d)
    if raw:
        pm = find_pass1(raw)
        if pm:
            results.append((d, pm))

print(f"Found {len(results)} captures with twin pass1_ms.")

# Pair with variants by order.
for i, (label, ck, presc) in enumerate(VARIANTS):
    if i >= len(results):
        print(f"VARIANT {label} ck={ck} presc={presc}: NO DATA")
        continue
    d, pass1_ms = results[i]
    sclk_hz = ck / (presc + 1)
    t_sclk_byte_ns = 8.0 / LANES / sclk_hz * 1e9
    t_meas_byte_ns = pass1_ms * 1e6 / N_BYTES
    t_ovhd_ns = t_meas_byte_ns - t_sclk_byte_ns
    ker_ck_cyc = t_ovhd_ns * ck / 1e9
    pred_kerck_ns = 7.55 / ck * 1e9
    pred_hclk6_ns = 11.5
    print(f"\n{label}: presc={presc} SCLK={sclk_hz/1e6:.1f}MHz")
    print(f"  pass1_ms={pass1_ms}")
    print(f"  T_sclk_byte={t_sclk_byte_ns:.2f} ns  T_meas_byte={t_meas_byte_ns:.2f} ns")
    print(f"  T_overhead measured = {t_ovhd_ns:.2f} ns ({ker_ck_cyc:.2f} ker_ck cycles)")
    print(f"  ker_ck model predicts {pred_kerck_ns:.2f} ns  | HCLK6 model predicts {pred_hclk6_ns:.2f} ns")
    err_kerck = abs(t_ovhd_ns - pred_kerck_ns)
    err_hclk6 = abs(t_ovhd_ns - pred_hclk6_ns)
    print(f"  err vs ker_ck: {err_kerck:.2f} ns | err vs HCLK6: {err_hclk6:.2f} ns")
    print(f"  -> {'KER_CK' if err_kerck < err_hclk6 else 'HCLK6'} model wins")
