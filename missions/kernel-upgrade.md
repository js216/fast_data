## WIP

### Record the current Linux baseline commit

Create `stm32mp135_test_board/config/kernel-upgrade-baseline.md` and record
the exact commit currently checked out in `stm32mp135_test_board/linux` before
changing any tracked source.

Build: nothing required.

Test: no hardware.

Verify:
```
def check(extract_dir):
    from pathlib import Path
    import subprocess

    root = Path.cwd()
    linux = root / 'stm32mp135_test_board/linux'
    notes = root / 'stm32mp135_test_board/config/kernel-upgrade-baseline.md'

    if not notes.exists():
        raise AssertionError('missing kernel upgrade baseline notes')

    text = notes.read_text()
    if 'current linux commit:' not in text:
        raise AssertionError('baseline notes missing current commit label')

    current = subprocess.check_output(
        ['git', '-C', str(linux), 'rev-parse', 'HEAD'],
        text=True).strip()
    if current not in text:
        raise AssertionError('baseline notes do not name current commit')

    return True
```

### Document the current kernel upgrade baseline

Record the exact starting kernel commit, the latest target kernel commit, and
the board boot constraints before changing any tracked source. The target is
the latest ST `v6.6-stm32mp` branch available from
`stm32mp135_test_board/linux`'s `origin` remote. The boot chain must remain the
local single-stage bootloader path: no TF-A, no OP-TEE, and no U-Boot.

Build: nothing required.

Test: no hardware.

Verify:
```
def check(extract_dir):
    from pathlib import Path
    import subprocess

    root = Path.cwd()
    board = root / 'stm32mp135_test_board'
    linux = board / 'linux'
    notes = board / 'config/kernel-upgrade-baseline.md'

    if not notes.exists():
        raise AssertionError('missing kernel upgrade baseline notes')

    text = notes.read_text()
    for required in [
        'current linux commit:',
        'target linux commit:',
        'target branch: origin/v6.6-stm32mp',
        'no TF-A',
        'no OP-TEE',
        'no U-Boot',
        'local single-stage bootloader',
    ]:
        if required not in text:
            raise AssertionError('baseline notes missing: ' + required)

    current = subprocess.check_output(
        ['git', '-C', str(linux), 'rev-parse', 'HEAD'],
        text=True).strip()
    target = subprocess.check_output(
        ['git', '-C', str(linux), 'rev-parse', 'origin/v6.6-stm32mp'],
        text=True).strip()
    if current not in text:
        raise AssertionError('baseline notes do not name current commit')
    if target not in text:
        raise AssertionError('baseline notes do not name target commit')

    return True
```

### Update the pinned Linux checkout to latest ST v6.6

Move `stm32mp135_test_board/linux` to the latest
`origin/v6.6-stm32mp` commit and update the parent gitlink. Do not apply local
driver overlays yet. Keep the Linux checkout clean and detached only if that is
the parent repo's submodule style.

Build: nothing required.

Test: no hardware.

Verify:
```
def check(extract_dir):
    from pathlib import Path
    import subprocess

    root = Path.cwd()
    linux = root / 'stm32mp135_test_board/linux'

    head = subprocess.check_output(
        ['git', '-C', str(linux), 'rev-parse', 'HEAD'],
        text=True).strip()
    target = subprocess.check_output(
        ['git', '-C', str(linux), 'rev-parse', 'origin/v6.6-stm32mp'],
        text=True).strip()
    if head != target:
        raise AssertionError(f'linux HEAD {head} is not latest target {target}')

    status = subprocess.check_output(
        ['git', '-C', str(linux), 'status', '--porcelain'],
        text=True)
    if status:
        raise AssertionError('linux checkout is dirty: ' + status)

    return True
```

### Preserve non-secure kernel entry without PSCI

Keep the kernel independent of secure monitor calls by ensuring STM32 ARM
Kconfig does not select PSCI for this board kernel. This may be a small patch
or a refreshed patch file, but it must apply cleanly to the updated kernel.

Build: `make -C stm32mp135_test_board patch`

Test: no hardware.

Verify:
```
def check(extract_dir):
    from pathlib import Path
    import subprocess

    root = Path.cwd()
    board = root / 'stm32mp135_test_board'
    linux = board / 'linux'
    patch = board / 'config/patch.linux'

    if not patch.exists():
        raise AssertionError('missing config/patch.linux')
    patch_text = patch.read_text()
    if 'select ARM_PSCI if ARCH_MULTI_V7' not in patch_text:
        raise AssertionError('patch.linux does not document PSCI removal')
    if 'drivers/clk/' in patch_text or 'drivers/mfd/' in patch_text or 'drivers/regulator/' in patch_text:
        raise AssertionError('patch.linux carries driver edits; keep this patch narrow')

    subprocess.run(
        ['git', '-C', str(linux), 'apply', '--check', '../config/patch.linux'],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    return True
```

### Port only still-needed PMIC changes

Refresh the STPMIC regulator and MFD changes against the updated kernel as
small patches or source edits derived from the new upstream files. Do not copy
old full driver files over the latest kernel drivers. The regulator SW_OUT
voltage must remain 3.3 V, and the PMIC must tolerate the board's missing PMIC
IRQ without failing probe.

Build:
```
make -C stm32mp135_test_board kernel
```

Test: no hardware.

Verify:
```
def check(extract_dir):
    from pathlib import Path
    import subprocess

    root = Path.cwd()
    board = root / 'stm32mp135_test_board'

    for rel in [
        'linux/drivers/regulator/stpmic1_regulator.c',
        'linux/drivers/mfd/stpmic1.c',
    ]:
        if not (board / rel).exists():
            raise AssertionError('missing updated PMIC file: ' + rel)

    regulator = (board / 'linux/drivers/regulator/stpmic1_regulator.c').read_text()
    mfd = (board / 'linux/drivers/mfd/stpmic1.c').read_text()
    if '.fixed_uV = 3300000' not in regulator:
        raise AssertionError('SW_OUT regulator is not fixed at 3.3 V')
    if 'of_irq_get' not in mfd:
        raise AssertionError('PMIC probe no longer inspects IRQ')
    if 'devm_regmap_add_irq_chip' not in mfd:
        raise AssertionError('PMIC IRQ chip support was removed instead of gated')
    if 'ddata->irq >= 0' not in mfd and 'ddata->irq > 0' not in mfd:
        raise AssertionError('PMIC IRQ chip registration is not gated on valid IRQ')

    subprocess.run(
        ['git', '-C', str(board / 'linux'), 'apply', '--check', '../config/patch.linux'],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    return True
```

### Drop obsolete clock overlays

Use the updated ST clock and reset implementation unless a specific local
behavior is still missing. Do not overwrite latest ST clock files with old
full-file copies. If a clock fix is still needed, carry it as a narrow patch
against the latest ST sources and document why upstream is insufficient.

Build: `make -C stm32mp135_test_board kernel`

Test: no hardware.

Verify:
```
def check(extract_dir):
    from pathlib import Path

    root = Path.cwd()
    board = root / 'stm32mp135_test_board'
    makefile = board / 'Makefile'
    text = makefile.read_text()

    obsolete_copies = [
        'config/drivers/clk/stm32/clk-stm32-core.h',
        'config/drivers/clk/stm32/clk-stm32-core.c',
        'config/drivers/clk/stm32/clk-stm32mp13.c',
    ]
    for rel in obsolete_copies:
        if rel in text:
            raise AssertionError('old full-file clock overlay still wired: ' + rel)

    for rel in [
        'linux/drivers/clk/stm32/clk-stm32-core.h',
        'linux/drivers/clk/stm32/clk-stm32-core.c',
        'linux/drivers/clk/stm32/clk-stm32mp13.c',
    ]:
        source = board / rel
        if not source.exists():
            raise AssertionError('missing latest clock source: ' + rel)

    core = (board / 'linux/drivers/clk/stm32/clk-stm32-core.c').read_text()
    mp13 = (board / 'linux/drivers/clk/stm32/clk-stm32mp13.c').read_text()
    if 'stm32_rcc_reset_init(dev, match, base)' not in core:
        raise AssertionError('clock core does not use latest reset API shape')
    if 'stm32mp13_clock_cfg' not in mp13:
        raise AssertionError('STM32MP13 clock config missing')

    return True
```

### Update device tree path handling

Adapt the board `dtb` build to the updated kernel DTS layout. Latest ST v6.6
stores STM32 DTS files under `arch/arm/boot/dts/st/`; the custom board DTS must
build in that layout without relying on TF-A, OP-TEE, or U-Boot nodes.

Build:
```
make -C stm32mp135_test_board dtb
```

Test: no hardware.

Verify:
```
def check(extract_dir):
    from pathlib import Path
    import subprocess

    root = Path.cwd()
    board = root / 'stm32mp135_test_board'
    linux = board / 'linux'
    custom = linux / 'arch/arm/boot/dts/st/custom.dts'
    dtb = linux / 'arch/arm/boot/dts/st/custom.dtb'

    if not custom.exists():
        raise AssertionError('custom DTS was not installed under dts/st')
    subprocess.run(
        ['make', '-C', str(linux), 'ARCH=arm', 'CROSS_COMPILE=arm-linux-gnueabihf-', 'st/custom.dtb'],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    if not dtb.exists():
        raise AssertionError('custom DTB was not built under dts/st')

    text = custom.read_text(errors='ignore')
    forbidden = ['optee', 'tf-a', 'u-boot']
    for word in forbidden:
        if word.lower() in text.lower():
            raise AssertionError('custom DTS references forbidden boot component: ' + word)

    return True
```

### Build the upgraded kernel image

Build the upgraded kernel with the board bootloader path and updated kernel
sources. The build must produce `zImage` without requiring TF-A, OP-TEE, or
U-Boot artifacts.

Build:
```
make -C stm32mp135_test_board patch kernel dtb
```

Test: no hardware.

Verify:
```
def check(extract_dir):
    from pathlib import Path
    import subprocess

    root = Path.cwd()
    board = root / 'stm32mp135_test_board'
    zimage = board / 'linux/arch/arm/boot/zImage'

    if not zimage.exists():
        raise AssertionError('missing zImage')
    if zimage.stat().st_size < 1024 * 1024:
        raise AssertionError('zImage is unexpectedly small')

    make_text = (board / 'Makefile').read_text(errors='ignore').lower()
    for forbidden in ['tf-a', 'optee', 'u-boot']:
        if forbidden in make_text:
            raise AssertionError('board Makefile invokes forbidden component: ' + forbidden)

    return True
```

### Boot the upgraded kernel on hardware

Boot the upgraded `zImage` and `custom.dtb` through the local single-stage
bootloader. The boot log must show Linux reaching userspace without TF-A,
OP-TEE, U-Boot, or PSCI dependency failures.

Build: `make -C stm32mp135_test_board all`

Test: hardware.

Verify:
```
def check(extract_dir):
    from pathlib import Path

    log = Path(extract_dir) / 'linux-boot.log'
    if not log.exists():
        raise AssertionError('missing linux boot log artifact')
    text = log.read_text(errors='ignore')

    for required in [
        'Linux version',
        'Freeing unused kernel image',
        'Welcome',
    ]:
        if required not in text:
            raise AssertionError('boot log missing: ' + required)

    forbidden = [
        'U-Boot',
        'OP-TEE',
        'TF-A',
        'PSCI: failed',
        'Unable to handle kernel',
        'Kernel panic',
    ]
    for item in forbidden:
        if item in text:
            raise AssertionError('boot log contains forbidden/fatal text: ' + item)

    return True
```
