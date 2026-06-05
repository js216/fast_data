# DSP fault and blink demo

### Fault

Boot the `adsp2156/fault` firmware that immediately faults the core, and
confirm the DSP fault line (scope C2 = `DSP_FAULT`) asserts.

Build:

```
make -C adsp2156/fault
```

Artifacts:

```
adsp2156/fault/build/main.ldr
```

Test (max 2 min):

```
dsp:reset
dsp:uart_open
dsp:boot ldr=@main.ldr timeout_ms=15000
delay ms=1000
scope:capture chans="C2"
dsp:uart_close
mark tag=dsp_fault
```

Verify:

```
def check(extract_dir):
    c2 = Verification.scope_columns(extract_dir).get('C2', [])
    if not c2:
        return False
    # Fault asserted = C2 pinned below the DSP_FAULT active_below (150).
    if sum(c2) / len(c2) < 150.0:
        return True
    if not Verification.manifest_clean(extract_dir):
        return False   # transient boot/USB glitch -- worth a retry
    # Clean boot but SYS_FAULT never asserted: deterministic, so fail
    # hard rather than burning run.py's retry backoff.
    raise HardFail('fault not asserted')
```

### Blink

Boot the `adsp2156/blink` firmware and prove, from the scope, that the
on-SOM LED actually blinks (scope C1 = `DSP_LED`) while the DSP is NOT in
a fault state (scope C2 = `DSP_FAULT`).

Build:

```
make -C adsp2156/blink
```

Artifacts:

```
adsp2156/blink/build/main.ldr
```

Test (max 2 min):

```
dsp:reset
dsp:uart_open
dsp:boot ldr=@main.ldr timeout_ms=15000
delay ms=3000
scope:capture chans="C1,C2"
dsp:uart_close
mark tag=dsp_blink
```

Verify:

```
MIN_BLINKS = 2
LED_ACTIVE_BELOW = 68.0   # config.json scope.signals.C1


def count_active_edges(vals, threshold):
    """Active-going crossings (a sample >= threshold followed by one
    below it)."""
    edges = 0
    prev = None
    for v in vals:
        active = v < threshold
        if prev is not None and active and not prev:
            edges += 1
        prev = active
    return edges


def check(extract_dir):
    cols = Verification.scope_columns(extract_dir)
    if not cols:
        return False
    # Fault gate first: a faulted DSP is a deterministic verdict.
    Verification.dsp_fault_gate(extract_dir)
    if not Verification.manifest_clean(extract_dir):
        return False
    # Clean boot, no fault: too few edges means the LED genuinely isn't
    # blinking (dead LED / wrong firmware / too-short window), which is
    # deterministic, so fail hard rather than retry.
    edges = count_active_edges(cols.get('C1', []), LED_ACTIVE_BELOW)
    if edges < MIN_BLINKS:
        raise HardFail(f'no blink: C1 edges={edges} < {MIN_BLINKS}')
    return True
```
