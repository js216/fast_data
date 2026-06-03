### Build the kernel + SD image

Build:

```
rm -f unix-v7-c99/boot/unix
TMPDIR=$PWD/tmp make -C unix-v7-c99 BOARD=qemu \
    KFEATURES="-DQEMU -DPL011 -DVIRTIO" \
    KLDSCRIPT=usr/sys/conf/arm_qemu.ld boot/rootfs.img
make -C unix-v7-c99 BOARD=mp135 \
    KFEATURES="-DMP135 -DSTM32USART -DSTM32SD" \
    KLDSCRIPT=usr/sys/conf/sysram.ld boot/unix
arm-none-eabi-objcopy -O binary unix-v7-c99/boot/unix unix-v7-c99/boot/unix.bin
python3 stm32mp135_test_board/bootloader/scripts/stm32_header.py \
    -e unix-v7-c99/boot/unix -b unix-v7-c99/boot/unix.bin \
    -o unix-v7-c99/boot/unix.stm32 -t .text
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' '-' '0x01' 'fsbl1-boot' 'Binary' 'none' '0x0' 'unix.stm32' > unix-v7-c99/boot/unix.tsv
make -C stm32mp135_test_board/bootloader -j$(nproc)
```

Artifacts:

```
unix-v7-c99/boot/unix.stm32
unix-v7-c99/boot/rootfs.img
unix-v7-c99/boot/unix.tsv
stm32mp135_test_board/bootloader/build/main.stm32
```

### Provision the SD card with the V7 root filesystem

Build (reset the DUT into ROM/DFU):

```
printf '%s\n' 'description "reset custom DUT"' "# runpy reset $(date +%s%N)" 'bench_mcu:reset_dut2' > "$RUNPY_WORKDIR/reset.plan"
python3 test_serv/submit.py --server http://localhost:8080 --wait 20 "$RUNPY_WORKDIR/reset.plan"
```

Artifacts:

```
stm32mp135_test_board/bootloader/scripts/flash.tsv
stm32mp135_test_board/bootloader/build/main.stm32
unix-v7-c99/boot/rootfs.img
```

Test (max 45 s):

```
bench_mcu:reset_dut2
delay ms=3000
dfu.custom:flash_layout layout=@flash.tsv no_reconnect=true
mp135.custom:uart_open
delay ms=300
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
delay ms=200
mp135.custom:uart_write data="x"
mp135.custom:uart_expect sentinel="> " timeout_ms=8000
mp135.custom:uart_close
inventory
msc.custom:write data=@rootfs.img offset_lba=0 min_rate_Bps=2000000
mark tag=sd_provisioned
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    ops = Verification.load_ops(extract_dir)
    return Verification.op_succeeded(ops, 'msc.custom', 'write')
```

### Boot UNIX and reach the shell

Build (reset the DUT into ROM/DFU):

```
printf '%s\n' 'description "reset custom DUT"' "# runpy reset $(date +%s%N)" 'bench_mcu:reset_dut2' > "$RUNPY_WORKDIR/reset.plan"
python3 test_serv/submit.py --server http://localhost:8080 --wait 20 "$RUNPY_WORKDIR/reset.plan"
```

Artifacts:

```
unix-v7-c99/boot/unix.stm32
unix-v7-c99/boot/unix.tsv
```

Test (max 30 s):

```
bench_mcu:reset_dut2
delay ms=2000
dfu.custom:flash_layout layout=@unix.tsv no_reconnect=true
mp135.custom:uart_open
mp135.custom:uart_expect sentinel="# " timeout_ms=20000
mp135.custom:uart_write data="stty -lcase nl0 cr0 ff0 tabs\r"
mp135.custom:uart_expect sentinel="stty -lcase nl0 cr0 ff0 tabs\r\n# " timeout_ms=3000
mp135.custom:uart_write data="ls /etc/passwd ; echo MP135_UNIX_OK\r"
mp135.custom:uart_expect sentinel="MP135_UNIX_OK\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=boot_unix
```

Verify:

```
def check(extract_dir):
    if not Verification.manifest_clean(extract_dir):
        return False
    uart = Verification.load_stream(
        extract_dir, 'mp135.uart').decode('utf-8', 'replace')
    return (
        'stty -lcase nl0 cr0 ff0 tabs' in uart
        and 'MP135_UNIX_OK\r\n# ' in uart
        and '\r\n/etc/passwd\r\n' in uart)
```

### LS

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls /\r"
mp135.custom:uart_expect sentinel="ls /\r\n.profile\r\nbin\r\ndev\r\netc\r\ntmp\r\nunix\r\nusr\r\n# " timeout_ms=10000
mp135.custom:uart_write data="ls /etc\r"
mp135.custom:uart_expect sentinel="# ls /etc\r\naccton\r\natrun\r\ncron\r\nddate\r\ngetty\r\ngroup\r\ninit\r\npasswd\r\nrc\r\nttys\r\nupdate\r\nutmp\r\n# " timeout_ms=10000
mp135.custom:uart_write data="ls /tmp\r"
mp135.custom:uart_expect sentinel="# ls /tmp\r\n.keep\r\n# " timeout_ms=10000
mp135.custom:uart_write data="ls /usr\r"
mp135.custom:uart_expect sentinel="# ls /usr\r\nadm\r\ndict\r\ngames\r\nlib\r\nspool\r\n# " timeout_ms=10000
mp135.custom:uart_write data="ls /usr/lib\r"
mp135.custom:uart_expect sentinel="# ls /usr/lib\r\ncrontab\r\ndiffh\r\nmakekey\r\nunits\r\n# " timeout_ms=10000
mp135.custom:uart_write data="ls /usr/dict\r"
mp135.custom:uart_expect sentinel="# ls /usr/dict\r\nwords\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=ls
```

Verify:

```
expected = """ls /
.profile
bin
dev
etc
tmp
unix
usr
# ls /etc
accton
atrun
cron
ddate
getty
group
init
passwd
rc
ttys
update
utmp
# ls /tmp
.keep
# ls /usr
adm
dict
games
lib
spool
# ls /usr/lib
crontab
diffh
makekey
units
# ls /usr/dict
words
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### UPDATE_DAEMON

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls /etc/update\r"
mp135.custom:uart_expect sentinel="ls /etc/update\r\n/etc/update\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/etc/update\r"
mp135.custom:uart_expect sentinel="# /etc/update\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo UPDATE_STATUS:$?\r"
mp135.custom:uart_expect sentinel="# echo UPDATE_STATUS:$?\r\nUPDATE_STATUS:0\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo POST_UPDATE_OK\r"
mp135.custom:uart_expect sentinel="# echo POST_UPDATE_OK\r\nPOST_UPDATE_OK\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=update_daemon
```

Verify:

```
expected = """ls /etc/update
/etc/update
# /etc/update
# echo UPDATE_STATUS:$?
UPDATE_STATUS:0
# echo POST_UPDATE_OK
POST_UPDATE_OK
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### AT_SPOOL

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls /bin/at /etc/atrun\r"
mp135.custom:uart_expect sentinel="ls /bin/at /etc/atrun\r\n/bin/at\r\n/etc/atrun\r\n# " timeout_ms=10000
mp135.custom:uart_write data="date 7001010000 >/tmp/date.set 2>&1\r"
mp135.custom:uart_expect sentinel="# date 7001010000 >/tmp/date.set 2>&1\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo DATE_STATUS:$?\r"
mp135.custom:uart_expect sentinel="# echo DATE_STATUS:$?\r\nDATE_STATUS:0\r\n# " timeout_ms=10000
mp135.custom:uart_write data="rm -f /usr/spool/at/70.000.0001.* /tmp/at.in /tmp/at.stdin\r"
mp135.custom:uart_expect sentinel="# rm -f /usr/spool/at/70.000.0001.* /tmp/at.in /tmp/at.stdin\r\n# " timeout_ms=10000
mp135.custom:uart_write data='echo \"echo AT_STDIN >/tmp/at.stdin\" >/tmp/at.in\r'
mp135.custom:uart_expect sentinel='# echo \"echo AT_STDIN >/tmp/at.stdin\" >/tmp/at.in\r\n# ' timeout_ms=10000
mp135.custom:uart_write data="at 0001 /tmp/at.in\r"
mp135.custom:uart_expect sentinel="# at 0001 /tmp/at.in\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cat /usr/spool/at/70.000.0001.*\r"
mp135.custom:uart_expect sentinel="# cat /usr/spool/at/70.000.0001.*\r\ncd /\r\nPATH=/bin:/usr/bin\r\necho AT_STDIN >/tmp/at.stdin\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=at_spool
```

Verify:

```
expected = """ls /bin/at /etc/atrun
/bin/at
/etc/atrun
# date 7001010000 >/tmp/date.set 2>&1
# echo DATE_STATUS:$?
DATE_STATUS:0
# rm -f /usr/spool/at/70.000.0001.* /tmp/at.in /tmp/at.stdin
# echo "echo AT_STDIN >/tmp/at.stdin" >/tmp/at.in
# at 0001 /tmp/at.in
# cat /usr/spool/at/70.000.0001.*
cd /
PATH=/bin:/usr/bin
echo AT_STDIN >/tmp/at.stdin
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### CRON_STARTUP

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls /etc/cron /usr/lib/crontab\r"
mp135.custom:uart_expect sentinel="ls /etc/cron /usr/lib/crontab\r\n/etc/cron\r\n/usr/lib/crontab\r\n# " timeout_ms=10000
mp135.custom:uart_write data="rm -f /tmp/cron.mark\r"
mp135.custom:uart_expect sentinel="# rm -f /tmp/cron.mark\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo '* * * * * echo CRON_OK >> /tmp/cron.mark' >/usr/lib/crontab\r"
mp135.custom:uart_expect sentinel="# echo '* * * * * echo CRON_OK >> /tmp/cron.mark' >/usr/lib/crontab\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/etc/cron\r"
mp135.custom:uart_expect sentinel="# /etc/cron\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo CRON_STATUS:$?\r"
mp135.custom:uart_expect sentinel="# echo CRON_STATUS:$?\r\nCRON_STATUS:0\r\n# " timeout_ms=10000
mp135.custom:uart_write data="for i in 1 2 3 4 5 6 7 8 9 10 11 12; do sleep 1; test -r /tmp/cron.mark && cat /tmp/cron.mark && break; done\r"
mp135.custom:uart_expect sentinel="# for i in 1 2 3 4 5 6 7 8 9 10 11 12; do sleep 1; test -r /tmp/cron.mark && cat /tmp/cron.mark && break; done\r\nCRON_OK\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=cron_startup
```

Verify:

```
expected = """ls /etc/cron /usr/lib/crontab
/etc/cron
/usr/lib/crontab
# rm -f /tmp/cron.mark
# echo '* * * * * echo CRON_OK >> /tmp/cron.mark' >/usr/lib/crontab
# /etc/cron
# echo CRON_STATUS:$?
CRON_STATUS:0
# for i in 1 2 3 4 5 6 7 8 9 10 11 12; do sleep 1; test -r /tmp/cron.mark && cat /tmp/cron.mark && break; done
CRON_OK
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### PASSWD_CHANGE

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="grep '^dmr:' /etc/passwd\r"
mp135.custom:uart_expect sentinel="grep '^dmr:' /etc/passwd\r\ndmr::7:3::/usr/dmr:\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/passwd dmr\r"
mp135.custom:uart_expect sentinel="/bin/passwd dmr\r\nNew password:" timeout_ms=10000
mp135.custom:uart_write data="abc123\r"
mp135.custom:uart_expect sentinel="Retype new password:" timeout_ms=10000
mp135.custom:uart_write data="abc123\r"
mp135.custom:uart_expect sentinel="Retype new password:\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo PASSWD_STATUS:$?\r"
mp135.custom:uart_expect sentinel="echo PASSWD_STATUS:$?\r\nPASSWD_STATUS:1\r\n# " timeout_ms=10000
mp135.custom:uart_write data="grep '^dmr::' /etc/passwd\r"
mp135.custom:uart_expect sentinel="grep '^dmr::' /etc/passwd\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo EMPTY_PASSWORD_STATUS:$?\r"
mp135.custom:uart_expect sentinel="echo EMPTY_PASSWORD_STATUS:$?\r\nEMPTY_PASSWORD_STATUS:1\r\n# " timeout_ms=10000
mp135.custom:uart_write data='awk -F: '"'"'/^dmr:/ { if ($2 != \"\" && $2 != \"abc123\") print \"dmr-password-field-ok\" }'"'"' /etc/passwd\r'
mp135.custom:uart_expect sentinel='awk -F: '"'"'/^dmr:/ { if ($2 != \"\" && $2 != \"abc123\") print \"dmr-password-field-ok\" }'"'"' /etc/passwd\r\ndmr-password-field-ok\r\n# ' timeout_ms=10000
mp135.custom:uart_write data="grep abc123 /etc/passwd\r"
mp135.custom:uart_expect sentinel="grep abc123 /etc/passwd\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo PLAINTEXT_STATUS:$?\r"
mp135.custom:uart_expect sentinel="echo PLAINTEXT_STATUS:$?\r\nPLAINTEXT_STATUS:1\r\n# " timeout_ms=10000
mp135.custom:uart_write data='awk -F: '"'"'{ if ($1 == \"dmr\") $2 = \"\"; print $1 \":\" $2 \":\" $3 \":\" $4 \":\" $5 \":\" $6 \":\" $7 }'"'"' /etc/passwd >/tmp/passwd.reset\r'
mp135.custom:uart_expect sentinel='awk -F: '"'"'{ if ($1 == \"dmr\") $2 = \"\"; print $1 \":\" $2 \":\" $3 \":\" $4 \":\" $5 \":\" $6 \":\" $7 }'"'"' /etc/passwd >/tmp/passwd.reset\r\n# ' timeout_ms=10000
mp135.custom:uart_write data="cp /tmp/passwd.reset /etc/passwd\r"
mp135.custom:uart_expect sentinel="cp /tmp/passwd.reset /etc/passwd\r\n# " timeout_ms=10000
mp135.custom:uart_write data="rm /tmp/passwd.reset\r"
mp135.custom:uart_expect sentinel="# rm /tmp/passwd.reset\r\n# " timeout_ms=10000
mp135.custom:uart_write data="grep '^dmr::' /etc/passwd\r"
mp135.custom:uart_expect sentinel="grep '^dmr::' /etc/passwd\r\ndmr::7:3::/usr/dmr:\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=passwd_change
```

Verify:

```
expected = """grep '^dmr:' /etc/passwd
dmr::7:3::/usr/dmr:
# /bin/passwd dmr
New password:
Retype new password:
# echo PASSWD_STATUS:$?
PASSWD_STATUS:1
# grep '^dmr::' /etc/passwd
# echo EMPTY_PASSWORD_STATUS:$?
EMPTY_PASSWORD_STATUS:1
# awk -F: '/^dmr:/ { if ($2 != "" && $2 != "abc123") print "dmr-password-field-ok" }' /etc/passwd
dmr-password-field-ok
# grep abc123 /etc/passwd
# echo PLAINTEXT_STATUS:$?
PLAINTEXT_STATUS:1
# awk -F: '{ if ($1 == "dmr") $2 = ""; print $1 ":" $2 ":" $3 ":" $4 ":" $5 ":" $6 ":" $7 }' /etc/passwd >/tmp/passwd.reset
# cp /tmp/passwd.reset /etc/passwd
# rm /tmp/passwd.reset
# grep '^dmr::' /etc/passwd
dmr::7:3::/usr/dmr:
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### DMESG

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls /bin/dmesg\r"
mp135.custom:uart_expect sentinel="ls /bin/dmesg\r\n/bin/dmesg\r\n# " timeout_ms=10000
mp135.custom:uart_write data="dmesg >/tmp/dmesg.out\r"
mp135.custom:uart_expect sentinel="# dmesg >/tmp/dmesg.out\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo DMESG_STATUS:$?\r"
mp135.custom:uart_expect sentinel="# echo DMESG_STATUS:$?\r\nDMESG_STATUS:0\r\n# " timeout_ms=10000
mp135.custom:uart_write data="test -s /tmp/dmesg.out\r"
mp135.custom:uart_expect sentinel="# test -s /tmp/dmesg.out\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo DMESG_NONEMPTY:$?\r"
mp135.custom:uart_expect sentinel="# echo DMESG_NONEMPTY:$?\r\nDMESG_NONEMPTY:0\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=dmesg
```

Verify:

```
expected = """ls /bin/dmesg
/bin/dmesg
# dmesg >/tmp/dmesg.out
# echo DMESG_STATUS:$?
DMESG_STATUS:0
# test -s /tmp/dmesg.out
# echo DMESG_NONEMPTY:$?
DMESG_NONEMPTY:0
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### DU

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="rm -r dut\r"
mp135.custom:uart_expect sentinel="rm -r dut\r\nrm: dut nonexistent\r\n# " timeout_ms=10000
mp135.custom:uart_write data="mkdir dut\r"
mp135.custom:uart_expect sentinel="# mkdir dut\r\n# " timeout_ms=10000
mp135.custom:uart_write data="mkdir dut/sub\r"
mp135.custom:uart_expect sentinel="# mkdir dut/sub\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/echo alpha >dut/a\r"
mp135.custom:uart_expect sentinel="# /bin/echo alpha >dut/a\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/echo beta >dut/sub/b\r"
mp135.custom:uart_expect sentinel="# /bin/echo beta >dut/sub/b\r\n# " timeout_ms=10000
mp135.custom:uart_write data="ln dut/a dut/alink\r"
mp135.custom:uart_expect sentinel="# ln dut/a dut/alink\r\n# " timeout_ms=10000
mp135.custom:uart_write data="du dut\r"
mp135.custom:uart_expect sentinel="# du dut\r\n2\tdut/sub\r\n4\tdut\r\n# " timeout_ms=10000
mp135.custom:uart_write data="du -a dut\r"
mp135.custom:uart_expect sentinel="# du -a dut\r\n1\tdut/sub/b\r\n2\tdut/sub\r\n1\tdut/a\r\n4\tdut\r\n# " timeout_ms=10000
mp135.custom:uart_write data="du -s dut\r"
mp135.custom:uart_expect sentinel="# du -s dut\r\n4\tdut\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cd dut\r"
mp135.custom:uart_expect sentinel="# cd dut\r\n# " timeout_ms=10000
mp135.custom:uart_write data="du -a a alink\r"
mp135.custom:uart_expect sentinel="# du -a a alink\r\n1\ta\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cd /\r"
mp135.custom:uart_expect sentinel="# cd /\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=du
```

Verify:

```
expected = """rm -r dut
rm: dut nonexistent
# mkdir dut
# mkdir dut/sub
# /bin/echo alpha >dut/a
# /bin/echo beta >dut/sub/b
# ln dut/a dut/alink
# du dut
2	dut/sub
4	dut
# du -a dut
1	dut/sub/b
2	dut/sub
1	dut/a
4	dut
# du -s dut
4	dut
# cd dut
# du -a a alink
1	a
# cd /
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### CONSOLE_SINGLE_USER_PATH

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="who am i\r"
mp135.custom:uart_expect sentinel="who am i\r\n# " timeout_ms=10000
mp135.custom:uart_write data="tty\r"
mp135.custom:uart_expect sentinel="# tty\r\n/dev/console\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cat /etc/ttys\r"
mp135.custom:uart_expect sentinel="# cat /etc/ttys\r\n14console\r\n00tty00\r\n00tty01\r\n00tty02\r\n00tty03\r\n00tty04\r\n00tty05\r\n00tty06\r\n00tty07\r\n00tty08\r\n00tty09\r\n00tty10\r\n00tty11\r\n00tty12\r\n00tty13\r\n00tty14\r\n00tty15\r\n00tty16\r\n00tty17\r\n00tty18\r\n00tty19\r\n00tty20\r\n00tty21\r\n00tty22\r\n00tty23\r\n00tty24\r\n00tty25\r\n00tty26\r\n00tty27\r\n00tty28\r\n00tty29\r\n00tty30\r\n00tty31\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo getty-login-path-ok\r"
mp135.custom:uart_expect sentinel="# echo getty-login-path-ok\r\ngetty-login-path-ok\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=console_single_user_path
```

Verify:

```
expected = """who am i
# tty
/dev/console
# cat /etc/ttys
14console
00tty00
00tty01
00tty02
00tty03
00tty04
00tty05
00tty06
00tty07
00tty08
00tty09
00tty10
00tty11
00tty12
00tty13
00tty14
00tty15
00tty16
00tty17
00tty18
00tty19
00tty20
00tty21
00tty22
00tty23
00tty24
00tty25
00tty26
00tty27
00tty28
00tty29
00tty30
00tty31
# echo getty-login-path-ok
getty-login-path-ok
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### JOIN_OPTIONS

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="/bin/echo 'a 1' >j1\r"
mp135.custom:uart_expect sentinel="/bin/echo 'a 1' >j1\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/echo 'b 2' >>j1\r"
mp135.custom:uart_expect sentinel="# /bin/echo 'b 2' >>j1\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/echo 'c 3' >>j1\r"
mp135.custom:uart_expect sentinel="# /bin/echo 'c 3' >>j1\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/echo 'a A' >j2\r"
mp135.custom:uart_expect sentinel="# /bin/echo 'a A' >j2\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/echo 'b B' >>j2\r"
mp135.custom:uart_expect sentinel="# /bin/echo 'b B' >>j2\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/echo 'd D' >>j2\r"
mp135.custom:uart_expect sentinel="# /bin/echo 'd D' >>j2\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/join j1 j2\r"
mp135.custom:uart_expect sentinel="# /bin/join j1 j2\r\na 1 A\r\nb 2 B\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/join -a1 j1 j2\r"
mp135.custom:uart_expect sentinel="# /bin/join -a1 j1 j2\r\na 1 A\r\nb 2 B\r\nc 3\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/join -a2 j1 j2\r"
mp135.custom:uart_expect sentinel="# /bin/join -a2 j1 j2\r\na 1 A\r\nb 2 B\r\nd D\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/join -a1 -e EMPTY -o 1.1 1.2 2.2 j1 j2\r"
mp135.custom:uart_expect sentinel="# /bin/join -a1 -e EMPTY -o 1.1 1.2 2.2 j1 j2\r\na 1 A\r\nb 2 B\r\nc 3 EMPTY\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/echo 'a:1' >jt1\r"
mp135.custom:uart_expect sentinel="# /bin/echo 'a:1' >jt1\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/echo 'b:2' >>jt1\r"
mp135.custom:uart_expect sentinel="# /bin/echo 'b:2' >>jt1\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/echo 'a:A' >jt2\r"
mp135.custom:uart_expect sentinel="# /bin/echo 'a:A' >jt2\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/echo 'b:B' >>jt2\r"
mp135.custom:uart_expect sentinel="# /bin/echo 'b:B' >>jt2\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/join -t: jt1 jt2\r"
mp135.custom:uart_expect sentinel="# /bin/join -t: jt1 jt2\r\na:1:A\r\nb:2:B\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cat j1 | /bin/join - j2\r"
mp135.custom:uart_expect sentinel="# cat j1 | /bin/join - j2\r\na 1 A\r\nb 2 B\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=join_options
```

Verify:

```
expected = """/bin/echo 'a 1' >j1
# /bin/echo 'b 2' >>j1
# /bin/echo 'c 3' >>j1
# /bin/echo 'a A' >j2
# /bin/echo 'b B' >>j2
# /bin/echo 'd D' >>j2
# /bin/join j1 j2
a 1 A
b 2 B
# /bin/join -a1 j1 j2
a 1 A
b 2 B
c 3
# /bin/join -a2 j1 j2
a 1 A
b 2 B
d D
# /bin/join -a1 -e EMPTY -o 1.1 1.2 2.2 j1 j2
a 1 A
b 2 B
c 3 EMPTY
# /bin/echo 'a:1' >jt1
# /bin/echo 'b:2' >>jt1
# /bin/echo 'a:A' >jt2
# /bin/echo 'b:B' >>jt2
# /bin/join -t: jt1 jt2
a:1:A
b:2:B
# cat j1 | /bin/join - j2
a 1 A
b 2 B
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### KILL_DIAGNOSTICS

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="/bin/kill\r"
mp135.custom:uart_expect sentinel="/bin/kill\r\nusage: kill [ -signo ] pid ...\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo KILL_USAGE_STATUS:$?\r"
mp135.custom:uart_expect sentinel="# echo KILL_USAGE_STATUS:$?\r\nKILL_USAGE_STATUS:2\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/kill xyz\r"
mp135.custom:uart_expect sentinel="# /bin/kill xyz\r\nusage: kill [ -signo ] pid ...\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo KILL_XYZ_STATUS:$?\r"
mp135.custom:uart_expect sentinel="# echo KILL_XYZ_STATUS:$?\r\nKILL_XYZ_STATUS:2\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/kill 99999\r"
mp135.custom:uart_expect sentinel="# /bin/kill 99999\r\n99999: No such process\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo KILL_NOPROC_STATUS:$?\r"
mp135.custom:uart_expect sentinel="# echo KILL_NOPROC_STATUS:$?\r\nKILL_NOPROC_STATUS:1\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/kill -9 99999\r"
mp135.custom:uart_expect sentinel="# /bin/kill -9 99999\r\n99999: No such process\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo KILL_SIG9_STATUS:$?\r"
mp135.custom:uart_expect sentinel="# echo KILL_SIG9_STATUS:$?\r\nKILL_SIG9_STATUS:1\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/kill -0 1\r"
mp135.custom:uart_expect sentinel="# /bin/kill -0 1\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo KILL_ZERO_STATUS:$?\r"
mp135.custom:uart_expect sentinel="# echo KILL_ZERO_STATUS:$?\r\nKILL_ZERO_STATUS:0\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=kill_diagnostics
```

Verify:

```
expected = """/bin/kill
usage: kill [ -signo ] pid ...
# echo KILL_USAGE_STATUS:$?
KILL_USAGE_STATUS:2
# /bin/kill xyz
usage: kill [ -signo ] pid ...
# echo KILL_XYZ_STATUS:$?
KILL_XYZ_STATUS:2
# /bin/kill 99999
99999: No such process
# echo KILL_NOPROC_STATUS:$?
KILL_NOPROC_STATUS:1
# /bin/kill -9 99999
99999: No such process
# echo KILL_SIG9_STATUS:$?
KILL_SIG9_STATUS:1
# /bin/kill -0 1
# echo KILL_ZERO_STATUS:$?
KILL_ZERO_STATUS:0
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### LN_DIAGNOSTICS

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="rm -f a b x dlink\r"
mp135.custom:uart_expect sentinel="rm -f a b x dlink\r\n# " timeout_ms=10000
mp135.custom:uart_write data="rm -r d\r"
mp135.custom:uart_expect sentinel="# rm -r d\r\nrm: d nonexistent\r\n# " timeout_ms=10000
mp135.custom:uart_write data="mkdir d\r"
mp135.custom:uart_expect sentinel="# mkdir d\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo data >a\r"
mp135.custom:uart_expect sentinel="# echo data >a\r\n# " timeout_ms=10000
mp135.custom:uart_write data="ln a b\r"
mp135.custom:uart_expect sentinel="# ln a b\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cmp a b\r"
mp135.custom:uart_expect sentinel="# cmp a b\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo CMP_STATUS:$?\r"
mp135.custom:uart_expect sentinel="# echo CMP_STATUS:$?\r\nCMP_STATUS:0\r\n# " timeout_ms=10000
mp135.custom:uart_write data="ln a d\r"
mp135.custom:uart_expect sentinel="# ln a d\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cmp a d/a\r"
mp135.custom:uart_expect sentinel="# cmp a d/a\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo DIR_LINK_STATUS:$?\r"
mp135.custom:uart_expect sentinel="# echo DIR_LINK_STATUS:$?\r\nDIR_LINK_STATUS:0\r\n# " timeout_ms=10000
mp135.custom:uart_write data="ln missing x\r"
mp135.custom:uart_expect sentinel="# ln missing x\r\nln: missing does not exist\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo MISSING_STATUS:$?\r"
mp135.custom:uart_expect sentinel="# echo MISSING_STATUS:$?\r\nMISSING_STATUS:1\r\n# " timeout_ms=10000
mp135.custom:uart_write data="ln d dlink\r"
mp135.custom:uart_expect sentinel="# ln d dlink\r\nln: d is a directory\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo DIR_STATUS:$?\r"
mp135.custom:uart_expect sentinel="# echo DIR_STATUS:$?\r\nDIR_STATUS:1\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=ln_diagnostics
```

Verify:

```
expected = """rm -f a b x dlink
# rm -r d
rm: d nonexistent
# mkdir d
# echo data >a
# ln a b
# cmp a b
# echo CMP_STATUS:$?
CMP_STATUS:0
# ln a d
# cmp a d/a
# echo DIR_LINK_STATUS:$?
DIR_LINK_STATUS:0
# ln missing x
ln: missing does not exist
# echo MISSING_STATUS:$?
MISSING_STATUS:1
# ln d dlink
ln: d is a directory
# echo DIR_STATUS:$?
DIR_STATUS:1
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### MKDIR_DIAGNOSTICS

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="rm -r mbase\r"
mp135.custom:uart_expect sentinel="rm -r mbase\r\nrm: mbase nonexistent\r\n# " timeout_ms=10000
mp135.custom:uart_write data="rm -r mdup\r"
mp135.custom:uart_expect sentinel="# rm -r mdup\r\nrm: mdup nonexistent\r\n# " timeout_ms=10000
mp135.custom:uart_write data="mkdir mbase\r"
mp135.custom:uart_expect sentinel="# mkdir mbase\r\n# " timeout_ms=10000
mp135.custom:uart_write data="mkdir mbase/child\r"
mp135.custom:uart_expect sentinel="# mkdir mbase/child\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo NESTED_STATUS:$?\r"
mp135.custom:uart_expect sentinel="# echo NESTED_STATUS:$?\r\nNESTED_STATUS:0\r\n# " timeout_ms=10000
mp135.custom:uart_write data="mkdir missing/child\r"
mp135.custom:uart_expect sentinel="# mkdir missing/child\r\nmkdir: cannot access missing/.\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo MISSING_PARENT_STATUS:$?\r"
mp135.custom:uart_expect sentinel="# echo MISSING_PARENT_STATUS:$?\r\nMISSING_PARENT_STATUS:1\r\n# " timeout_ms=10000
mp135.custom:uart_write data="mkdir mdup\r"
mp135.custom:uart_expect sentinel="# mkdir mdup\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo FIRST_DUP_STATUS:$?\r"
mp135.custom:uart_expect sentinel="# echo FIRST_DUP_STATUS:$?\r\nFIRST_DUP_STATUS:0\r\n# " timeout_ms=10000
mp135.custom:uart_write data="mkdir mdup\r"
mp135.custom:uart_expect sentinel="# mkdir mdup\r\nmkdir: cannot make directory mdup\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo DUP_STATUS:$?\r"
mp135.custom:uart_expect sentinel="# echo DUP_STATUS:$?\r\nDUP_STATUS:1\r\n# " timeout_ms=10000
mp135.custom:uart_write data="rmdir mbase/child\r"
mp135.custom:uart_expect sentinel="# rmdir mbase/child\r\n# " timeout_ms=10000
mp135.custom:uart_write data="rmdir mbase\r"
mp135.custom:uart_expect sentinel="# rmdir mbase\r\n# " timeout_ms=10000
mp135.custom:uart_write data="rmdir mdup\r"
mp135.custom:uart_expect sentinel="# rmdir mdup\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo CLEANUP_STATUS:$?\r"
mp135.custom:uart_expect sentinel="# echo CLEANUP_STATUS:$?\r\nCLEANUP_STATUS:0\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=mkdir_diagnostics
```

Verify:

```
expected = """rm -r mbase
rm: mbase nonexistent
# rm -r mdup
rm: mdup nonexistent
# mkdir mbase
# mkdir mbase/child
# echo NESTED_STATUS:$?
NESTED_STATUS:0
# mkdir missing/child
mkdir: cannot access missing/.
# echo MISSING_PARENT_STATUS:$?
MISSING_PARENT_STATUS:1
# mkdir mdup
# echo FIRST_DUP_STATUS:$?
FIRST_DUP_STATUS:0
# mkdir mdup
mkdir: cannot make directory mdup
# echo DUP_STATUS:$?
DUP_STATUS:1
# rmdir mbase/child
# rmdir mbase
# rmdir mdup
# echo CLEANUP_STATUS:$?
CLEANUP_STATUS:0
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### DIFF3_MERGE

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="/bin/echo a >/tmp/base\r"
mp135.custom:uart_expect sentinel="/bin/echo a >/tmp/base\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/echo b >>/tmp/base\r"
mp135.custom:uart_expect sentinel="# /bin/echo b >>/tmp/base\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/echo c >>/tmp/base\r"
mp135.custom:uart_expect sentinel="# /bin/echo c >>/tmp/base\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/echo a >/tmp/left\r"
mp135.custom:uart_expect sentinel="# /bin/echo a >/tmp/left\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/echo B-left >>/tmp/left\r"
mp135.custom:uart_expect sentinel="# /bin/echo B-left >>/tmp/left\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/echo c >>/tmp/left\r"
mp135.custom:uart_expect sentinel="# /bin/echo c >>/tmp/left\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/echo a >/tmp/right\r"
mp135.custom:uart_expect sentinel="# /bin/echo a >/tmp/right\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/echo B-right >>/tmp/right\r"
mp135.custom:uart_expect sentinel="# /bin/echo B-right >>/tmp/right\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/echo c >>/tmp/right\r"
mp135.custom:uart_expect sentinel="# /bin/echo c >>/tmp/right\r\n# " timeout_ms=10000
mp135.custom:uart_write data="diff /tmp/left /tmp/base >/tmp/d13\r"
mp135.custom:uart_expect sentinel="# diff /tmp/left /tmp/base >/tmp/d13\r\n# " timeout_ms=10000
mp135.custom:uart_write data="diff /tmp/right /tmp/base >/tmp/d23\r"
mp135.custom:uart_expect sentinel="# diff /tmp/right /tmp/base >/tmp/d23\r\n# " timeout_ms=10000
mp135.custom:uart_write data="diff3 /tmp/d13 /tmp/d23 /tmp/left /tmp/right /tmp/base\r"
mp135.custom:uart_expect sentinel="# diff3 /tmp/d13 /tmp/d23 /tmp/left /tmp/right /tmp/base\r\n====\r\n1:2c\r\n  B-left\r\n2:2c\r\n  B-right\r\n3:2c\r\n  b\r\n# " timeout_ms=10000
mp135.custom:uart_write data="diff3 -e /tmp/d13 /tmp/d23 /tmp/left /tmp/right /tmp/base\r"
mp135.custom:uart_expect sentinel="# diff3 -e /tmp/d13 /tmp/d23 /tmp/left /tmp/right /tmp/base\r\n2c\r\nb\r\n.\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo DIFF3_E_STATUS:$?\r"
mp135.custom:uart_expect sentinel="# echo DIFF3_E_STATUS:$?\r\nDIFF3_E_STATUS:0\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=diff3_merge
```

Verify:

```
expected = """/bin/echo a >/tmp/base
# /bin/echo b >>/tmp/base
# /bin/echo c >>/tmp/base
# /bin/echo a >/tmp/left
# /bin/echo B-left >>/tmp/left
# /bin/echo c >>/tmp/left
# /bin/echo a >/tmp/right
# /bin/echo B-right >>/tmp/right
# /bin/echo c >>/tmp/right
# diff /tmp/left /tmp/base >/tmp/d13
# diff /tmp/right /tmp/base >/tmp/d23
# diff3 /tmp/d13 /tmp/d23 /tmp/left /tmp/right /tmp/base
====
1:2c
  B-left
2:2c
  B-right
3:2c
  b
# diff3 -e /tmp/d13 /tmp/d23 /tmp/left /tmp/right /tmp/base
2c
b
.
# echo DIFF3_E_STATUS:$?
DIFF3_E_STATUS:0
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### COMPARE

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="cmp /etc/passwd /etc/passwd\r"
mp135.custom:uart_expect sentinel="cmp /etc/passwd /etc/passwd\r\n# " timeout_ms=10000
mp135.custom:uart_write data="diff /etc/passwd /etc/passwd\r"
mp135.custom:uart_expect sentinel="# diff /etc/passwd /etc/passwd\r\n# " timeout_ms=10000
mp135.custom:uart_write data='echo \"a 1\" > /tmp/j1\r'
mp135.custom:uart_expect sentinel='# echo \"a 1\" > /tmp/j1\r\n# ' timeout_ms=10000
mp135.custom:uart_write data='echo \"a x\" > /tmp/j2\r'
mp135.custom:uart_expect sentinel='# echo \"a x\" > /tmp/j2\r\n# ' timeout_ms=10000
mp135.custom:uart_write data="join /tmp/j1 /tmp/j2\r"
mp135.custom:uart_expect sentinel="# join /tmp/j1 /tmp/j2\r\na 1 x\r\n# " timeout_ms=10000
mp135.custom:uart_write data='echo \"a b\" | tsort\r'
mp135.custom:uart_expect sentinel='# echo \"a b\" | tsort\r\na\r\nb\r\n# ' timeout_ms=10000
mp135.custom:uart_write data="rm /tmp/j1 /tmp/j2\r"
mp135.custom:uart_expect sentinel="# rm /tmp/j1 /tmp/j2\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=compare
```

Verify:

```
expected = """cmp /etc/passwd /etc/passwd
# diff /etc/passwd /etc/passwd
# echo "a 1" > /tmp/j1
# echo "a x" > /tmp/j2
# join /tmp/j1 /tmp/j2
a 1 x
# echo "a b" | tsort
a
b
# rm /tmp/j1 /tmp/j2
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### TEST

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="test -f /etc/passwd\r"
mp135.custom:uart_expect sentinel="test -f /etc/passwd\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo TEST_FILE_STATUS:$?\r"
mp135.custom:uart_expect sentinel="# echo TEST_FILE_STATUS:$?\r\nTEST_FILE_STATUS:0\r\n# " timeout_ms=10000
mp135.custom:uart_write data="test -d /etc\r"
mp135.custom:uart_expect sentinel="# test -d /etc\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo TEST_DIR_STATUS:$?\r"
mp135.custom:uart_expect sentinel="# echo TEST_DIR_STATUS:$?\r\nTEST_DIR_STATUS:0\r\n# " timeout_ms=10000
mp135.custom:uart_write data="test -f /nonexistent\r"
mp135.custom:uart_expect sentinel="# test -f /nonexistent\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo TEST_MISSING_STATUS:$?\r"
mp135.custom:uart_expect sentinel="# echo TEST_MISSING_STATUS:$?\r\nTEST_MISSING_STATUS:1\r\n# " timeout_ms=10000
mp135.custom:uart_write data="test -r /etc/passwd\r"
mp135.custom:uart_expect sentinel="# test -r /etc/passwd\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo TEST_READ_STATUS:$?\r"
mp135.custom:uart_expect sentinel="# echo TEST_READ_STATUS:$?\r\nTEST_READ_STATUS:0\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=test
```

Verify:

```
expected = """test -f /etc/passwd
# echo TEST_FILE_STATUS:$?
TEST_FILE_STATUS:0
# test -d /etc
# echo TEST_DIR_STATUS:$?
TEST_DIR_STATUS:0
# test -f /nonexistent
# echo TEST_MISSING_STATUS:$?
TEST_MISSING_STATUS:1
# test -r /etc/passwd
# echo TEST_READ_STATUS:$?
TEST_READ_STATUS:0
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### FOR

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="for i in 1 2 3\r"
mp135.custom:uart_expect sentinel="for i in 1 2 3\r\n> " timeout_ms=10000
mp135.custom:uart_write data="do\r"
mp135.custom:uart_expect sentinel="> do\r\n> " timeout_ms=10000
mp135.custom:uart_write data="echo loop $i\r"
mp135.custom:uart_expect sentinel="> echo loop $i\r\n> " timeout_ms=10000
mp135.custom:uart_write data="done\r"
mp135.custom:uart_expect sentinel="> done\r\nloop 1\r\nloop 2\r\nloop 3\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=for
```

Verify:

```
expected = """for i in 1 2 3
> do
> echo loop $i
> done
loop 1
loop 2
loop 3
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### CASE

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="case foo in\r"
mp135.custom:uart_expect sentinel="case foo in\r\n> " timeout_ms=10000
mp135.custom:uart_write data="foo) echo matched;;\r"
mp135.custom:uart_expect sentinel="> foo) echo matched;;\r\n> " timeout_ms=10000
mp135.custom:uart_write data="bar) echo bar;;\r"
mp135.custom:uart_expect sentinel="> bar) echo bar;;\r\n> " timeout_ms=10000
mp135.custom:uart_write data="esac\r"
mp135.custom:uart_expect sentinel="> esac\r\nmatched\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=case
```

Verify:

```
expected = """case foo in
> foo) echo matched;;
> bar) echo bar;;
> esac
matched
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### IF

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="if test -f /etc/passwd\r"
mp135.custom:uart_expect sentinel="if test -f /etc/passwd\r\n> " timeout_ms=10000
mp135.custom:uart_write data="then\r"
mp135.custom:uart_expect sentinel="> then\r\n> " timeout_ms=10000
mp135.custom:uart_write data="echo passwd_exists\r"
mp135.custom:uart_expect sentinel="> echo passwd_exists\r\n> " timeout_ms=10000
mp135.custom:uart_write data="fi\r"
mp135.custom:uart_expect sentinel="> fi\r\npasswd_exists\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=if
```

Verify:

```
expected = """if test -f /etc/passwd
> then
> echo passwd_exists
> fi
passwd_exists
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### GLOB

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls /etc/p*\r"
mp135.custom:uart_expect sentinel="ls /etc/p*\r\n/etc/passwd\r\n# " timeout_ms=10000
mp135.custom:uart_write data="ls /b??\r"
mp135.custom:uart_expect sentinel="# ls /b??\r\n1\r\n[\r\nac\r\narcv\r\nat\r\nawk\r\nbasename\r\ncal\r\ncalendar\r\ncat\r\ncb\r\ncheckeq\r\nchgrp\r\nchmod\r\nchown\r\nclri\r\ncmp\r\ncol\r\ncomm\r\ncp\r\ncrypt\r\ndate\r\ndc\r\ndcheck\r\ndd\r\nderoff\r\ndf\r\ndiff\r\ndiff3\r\ndmesg\r\ndu\r\ndump\r\ndumpdir\r\necho\r\ned\r\negrep\r\nexpr\r\nfactor\r\nfalse\r\nfgrep\r\nfile\r\nfind\r\ngraph\r\ngrep\r\nicheck\r\niostat\r\njoin\r\nkill\r\nln\r\nlogin\r\nlook\r\nls\r\nmesg\r\nmkdir\r\nmknod\r\nmount\r\nmv\r\nncheck\r\nnewgrp\r\nnice\r\nnohup\r\nod\r\nosh\r\npasswd\r\npr\r\nprimes\r\nprof\r\nps\r\npstat\r\nptx\r\npwd\r\nquot\r\nrandom\r\nrestor\r\nrev\r\nrm\r\nrmdir\r\nsa\r\nsed\r\nsh\r\nsleep\r\nsort\r\nsp\r\nspline\r\nsplit\r\nstty\r\nsu\r\nsum\r\nsync\r\ntabs\r\ntail\r\ntar\r\ntc\r\ntee\r\ntest\r\ntime\r\ntk\r\ntouch\r\ntp\r\ntr\r\ntrue\r\ntsort\r\ntty\r\numount\r\nuniq\r\nunits\r\nvpr\r\nwall\r\nwc\r\nwho\r\nwrite\r\nyes\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=glob
```

Verify:

```
expected = """ls /etc/p*
/etc/passwd
# ls /b??
1
[
ac
arcv
at
awk
basename
cal
calendar
cat
cb
checkeq
chgrp
chmod
chown
clri
cmp
col
comm
cp
crypt
date
dc
dcheck
dd
deroff
df
diff
diff3
dmesg
du
dump
dumpdir
echo
ed
egrep
expr
factor
false
fgrep
file
find
graph
grep
icheck
iostat
join
kill
ln
login
look
ls
mesg
mkdir
mknod
mount
mv
ncheck
newgrp
nice
nohup
od
osh
passwd
pr
primes
prof
ps
pstat
ptx
pwd
quot
random
restor
rev
rm
rmdir
sa
sed
sh
sleep
sort
sp
spline
split
stty
su
sum
sync
tabs
tail
tar
tc
tee
test
time
tk
touch
tp
tr
true
tsort
tty
umount
uniq
units
vpr
wall
wc
who
write
yes
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### CAL

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="cal 1 1970\r"
mp135.custom:uart_expect sentinel="cal 1 1970\r\n   January 1970\r\n S  M Tu  W Th  F  S\r\n             1  2  3\r\n 4  5  6  7  8  9 10\r\n11 12 13 14 15 16 17\r\n18 19 20 21 22 23 24\r\n25 26 27 28 29 30 31\r\n\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cal 12 1969\r"
mp135.custom:uart_expect sentinel="# cal 12 1969\r\n   December 1969\r\n S  M Tu  W Th  F  S\r\n    1  2  3  4  5  6\r\n 7  8  9 10 11 12 13\r\n14 15 16 17 18 19 20\r\n21 22 23 24 25 26 27\r\n28 29 30 31\r\n\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=cal
```

Verify:

```
expected = """cal 1 1970
   January 1970
 S  M Tu  W Th  F  S
             1  2  3
 4  5  6  7  8  9 10
11 12 13 14 15 16 17
18 19 20 21 22 23 24
25 26 27 28 29 30 31

# cal 12 1969
   December 1969
 S  M Tu  W Th  F  S
    1  2  3  4  5  6
 7  8  9 10 11 12 13
14 15 16 17 18 19 20
21 22 23 24 25 26 27
28 29 30 31

# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### CD

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="pwd\r"
mp135.custom:uart_expect sentinel="pwd\r\n/\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cd /tmp\r"
mp135.custom:uart_expect sentinel="# cd /tmp\r\n# " timeout_ms=10000
mp135.custom:uart_write data="pwd\r"
mp135.custom:uart_expect sentinel="# pwd\r\n/tmp\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cd /etc\r"
mp135.custom:uart_expect sentinel="# cd /etc\r\n# " timeout_ms=10000
mp135.custom:uart_write data="pwd\r"
mp135.custom:uart_expect sentinel="# pwd\r\n/etc\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cd /\r"
mp135.custom:uart_expect sentinel="# cd /\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=cd
```

Verify:

```
expected = """pwd
/
# cd /tmp
# pwd
/tmp
# cd /etc
# pwd
/etc
# cd /
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### TEXT

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="echo abcde | rev\r"
mp135.custom:uart_expect sentinel="echo abcde | rev\r\nedcba\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo ABC | tr A-Z a-z\r"
mp135.custom:uart_expect sentinel="# echo ABC | tr A-Z a-z\r\nabc\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo aaa | uniq\r"
mp135.custom:uart_expect sentinel="# echo aaa | uniq\r\naaa\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo abc | sum\r"
mp135.custom:uart_expect sentinel="# echo abc | sum\r\n08288     1\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo abc | od -c\r"
mp135.custom:uart_expect sentinel="# echo abc | od -c\r\n0000000   a   b   c  \\n\r\n0000004\r\n# " timeout_ms=10000
mp135.custom:uart_write data="sed 2q /etc/passwd\r"
mp135.custom:uart_expect sentinel="# sed 2q /etc/passwd\r\nroot:VwL97VCAx1Qhs:0:1::/:\r\ndaemon:x:1:1::/:\r\n# " timeout_ms=10000
mp135.custom:uart_write data="tail /etc/passwd\r"
mp135.custom:uart_expect sentinel="# tail /etc/passwd\r\nroot:VwL97VCAx1Qhs:0:1::/:\r\ndaemon:x:1:1::/:\r\nsys::2:2::/usr/sys:\r\nbin::3:3::/bin:\r\nuucp::4:4::/usr/lib/uucp:/usr/lib/uucico\r\ndmr::7:3::/usr/dmr:\r\n# " timeout_ms=10000
mp135.custom:uart_write data="grep root /etc/passwd\r"
mp135.custom:uart_expect sentinel="# grep root /etc/passwd\r\nroot:VwL97VCAx1Qhs:0:1::/:\r\n# " timeout_ms=10000
mp135.custom:uart_write data="fgrep root /etc/passwd\r"
mp135.custom:uart_expect sentinel="# fgrep root /etc/passwd\r\nroot:VwL97VCAx1Qhs:0:1::/:\r\n# " timeout_ms=10000
mp135.custom:uart_write data="sort /etc/passwd\r"
mp135.custom:uart_expect sentinel="# sort /etc/passwd\r\nbin::3:3::/bin:\r\ndaemon:x:1:1::/:\r\ndmr::7:3::/usr/dmr:\r\nroot:VwL97VCAx1Qhs:0:1::/:\r\nsys::2:2::/usr/sys:\r\nuucp::4:4::/usr/lib/uucp:/usr/lib/uucico\r\n# " timeout_ms=10000
mp135.custom:uart_write data="look ro /usr/dict/words\r"
mp135.custom:uart_expect sentinel="# look ro /usr/dict/words\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo abc | tee /tmp/teeout\r"
mp135.custom:uart_expect sentinel="# echo abc | tee /tmp/teeout\r\nabc\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cat /tmp/teeout\r"
mp135.custom:uart_expect sentinel="# cat /tmp/teeout\r\nabc\r\n# " timeout_ms=10000
mp135.custom:uart_write data="rm /tmp/teeout\r"
mp135.custom:uart_expect sentinel="# rm /tmp/teeout\r\n# " timeout_ms=10000
mp135.custom:uart_write data="sed s/x/y/ /etc/passwd\r"
mp135.custom:uart_expect sentinel="# sed s/x/y/ /etc/passwd\r\nroot:VwL97VCAy1Qhs:0:1::/:\r\nroot:VwL97VCAy1Qhs:0:1::/:\r\ndaemon:y:1:1::/:\r\ndaemon:y:1:1::/:\r\nsys::2:2::/usr/sys:\r\nsys::2:2::/usr/sys:\r\nbin::3:3::/bin:\r\nbin::3:3::/bin:\r\nuucp::4:4::/usr/lib/uucp:/usr/lib/uucico\r\nuucp::4:4::/usr/lib/uucp:/usr/lib/uucico\r\ndmr::7:3::/usr/dmr:\r\ndmr::7:3::/usr/dmr:\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo x | sed s/x/y/\r"
mp135.custom:uart_expect sentinel="# echo x | sed s/x/y/\r\ny\r\ny\r\n# " timeout_ms=10000
mp135.custom:uart_write data="awk 1 /etc/passwd\r"
mp135.custom:uart_expect sentinel="# awk 1 /etc/passwd\r\nroot:VwL97VCAx1Qhs:0:1::/:\r\ndaemon:x:1:1::/:\r\nsys::2:2::/usr/sys:\r\nbin::3:3::/bin:\r\nuucp::4:4::/usr/lib/uucp:/usr/lib/uucico\r\ndmr::7:3::/usr/dmr:\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=text
```

Verify:

```
expected = """echo abcde | rev
edcba
# echo ABC | tr A-Z a-z
abc
# echo aaa | uniq
aaa
# echo abc | sum
08288     1
# echo abc | od -c
0000000   a   b   c  \\n
0000004
# sed 2q /etc/passwd
root:VwL97VCAx1Qhs:0:1::/:
daemon:x:1:1::/:
# tail /etc/passwd
root:VwL97VCAx1Qhs:0:1::/:
daemon:x:1:1::/:
sys::2:2::/usr/sys:
bin::3:3::/bin:
uucp::4:4::/usr/lib/uucp:/usr/lib/uucico
dmr::7:3::/usr/dmr:
# grep root /etc/passwd
root:VwL97VCAx1Qhs:0:1::/:
# fgrep root /etc/passwd
root:VwL97VCAx1Qhs:0:1::/:
# sort /etc/passwd
bin::3:3::/bin:
daemon:x:1:1::/:
dmr::7:3::/usr/dmr:
root:VwL97VCAx1Qhs:0:1::/:
sys::2:2::/usr/sys:
uucp::4:4::/usr/lib/uucp:/usr/lib/uucico
# look ro /usr/dict/words
# echo abc | tee /tmp/teeout
abc
# cat /tmp/teeout
abc
# rm /tmp/teeout
# sed s/x/y/ /etc/passwd
root:VwL97VCAy1Qhs:0:1::/:
root:VwL97VCAy1Qhs:0:1::/:
daemon:y:1:1::/:
daemon:y:1:1::/:
sys::2:2::/usr/sys:
sys::2:2::/usr/sys:
bin::3:3::/bin:
bin::3:3::/bin:
uucp::4:4::/usr/lib/uucp:/usr/lib/uucico
uucp::4:4::/usr/lib/uucp:/usr/lib/uucico
dmr::7:3::/usr/dmr:
dmr::7:3::/usr/dmr:
# echo x | sed s/x/y/
y
y
# awk 1 /etc/passwd
root:VwL97VCAx1Qhs:0:1::/:
daemon:x:1:1::/:
sys::2:2::/usr/sys:
bin::3:3::/bin:
uucp::4:4::/usr/lib/uucp:/usr/lib/uucico
dmr::7:3::/usr/dmr:
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### VARS

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="test $$ -gt 0 && echo pid: numeric\r"
mp135.custom:uart_expect sentinel="test $$ -gt 0 && echo pid: numeric\r\npid: numeric\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo $HOME\r"
mp135.custom:uart_expect sentinel="# echo $HOME\r\n\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo $PATH\r"
mp135.custom:uart_expect sentinel="# echo $PATH\r\n/bin:/usr/bin\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo $0\r"
mp135.custom:uart_expect sentinel="# echo $0\r\n-\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo VARS_STATUS:$?\r"
mp135.custom:uart_expect sentinel="# echo VARS_STATUS:$?\r\nVARS_STATUS:0\r\n# " timeout_ms=10000
mp135.custom:uart_write data="sh -c 'echo $1 $2' x A B\r"
mp135.custom:uart_expect sentinel="# sh -c 'echo $1 $2' x A B\r\nA B\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=vars
```

Verify:

```
expected = """test $$ -gt 0 && echo pid: numeric
pid: numeric
# echo $HOME

# echo $PATH
/bin:/usr/bin
# echo $0
-
# echo VARS_STATUS:$?
VARS_STATUS:0
# sh -c 'echo $1 $2' x A B
A B
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### EXPAND

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="echo `echo backtick`\r"
mp135.custom:uart_expect sentinel="echo `echo backtick`\r\nbacktick\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo 'single quote'\r"
mp135.custom:uart_expect sentinel="# echo 'single quote'\r\nsingle quote\r\n# " timeout_ms=10000
mp135.custom:uart_write data='echo \"double quote\"\r'
mp135.custom:uart_expect sentinel='# echo \"double quote\"\r\ndouble quote\r\n# ' timeout_ms=10000
mp135.custom:uart_write data="expr 1 + 2\r"
mp135.custom:uart_expect sentinel="# expr 1 + 2\r\n3\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=expand
```

Verify:

```
expected = """echo `echo backtick`
backtick
# echo 'single quote'
single quote
# echo "double quote"
double quote
# expr 1 + 2
3
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### ED

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ed /tmp/edtest << EOF\r"
mp135.custom:uart_expect sentinel="ed /tmp/edtest << EOF\r\n> " timeout_ms=10000
mp135.custom:uart_write data="a\r"
mp135.custom:uart_expect sentinel="> a\r\n> " timeout_ms=10000
mp135.custom:uart_write data="hello\r"
mp135.custom:uart_expect sentinel="> hello\r\n> " timeout_ms=10000
mp135.custom:uart_write data="world\r"
mp135.custom:uart_expect sentinel="> world\r\n> " timeout_ms=10000
mp135.custom:uart_write data=".\r"
mp135.custom:uart_expect sentinel="> .\r\n> " timeout_ms=10000
mp135.custom:uart_write data="w\r"
mp135.custom:uart_expect sentinel="> w\r\n> " timeout_ms=10000
mp135.custom:uart_write data="q\r"
mp135.custom:uart_expect sentinel="> q\r\n> " timeout_ms=10000
mp135.custom:uart_write data="EOF\r"
mp135.custom:uart_expect sentinel="> EOF\r\n?/tmp/edtest\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cat /tmp/edtest\r"
mp135.custom:uart_expect sentinel="# cat /tmp/edtest\r\ncat: can't open /tmp/edtest\r\n# " timeout_ms=10000
mp135.custom:uart_write data="rm /tmp/edtest\r"
mp135.custom:uart_expect sentinel="# rm /tmp/edtest\r\nrm: /tmp/edtest nonexistent\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=ed
```

Verify:

```
expected = """ed /tmp/edtest << EOF
> a
> hello
> world
> .
> w
> q
> EOF
?/tmp/edtest
# cat /tmp/edtest
cat: can't open /tmp/edtest
# rm /tmp/edtest
rm: /tmp/edtest nonexistent
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### FIND

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="find /usr/lib -print\r"
mp135.custom:uart_expect sentinel="find /usr/lib -print\r\n/usr/lib\r\n/usr/lib/crontab\r\n/usr/lib/diffh\r\n/usr/lib/makekey\r\n/usr/lib/units\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=find
```

Verify:

```
expected = """find /usr/lib -print
/usr/lib
/usr/lib/crontab
/usr/lib/diffh
/usr/lib/makekey
/usr/lib/units
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### DF

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="df\r"
mp135.custom:uart_expect sentinel="df\r\n/dev/root 5644\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=df
```

Verify:

```
expected = """df
/dev/root 5644
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### GREP

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="grep '^root' /etc/passwd\r"
mp135.custom:uart_expect sentinel="grep '^root' /etc/passwd\r\nroot:VwL97VCAx1Qhs:0:1::/:\r\n# " timeout_ms=10000
mp135.custom:uart_write data="grep -v root /etc/passwd\r"
mp135.custom:uart_expect sentinel="# grep -v root /etc/passwd\r\ndaemon:x:1:1::/:\r\nsys::2:2::/usr/sys:\r\nbin::3:3::/bin:\r\nuucp::4:4::/usr/lib/uucp:/usr/lib/uucico\r\ndmr::7:3::/usr/dmr:\r\n# " timeout_ms=10000
mp135.custom:uart_write data="grep -c sh /etc/passwd\r"
mp135.custom:uart_expect sentinel="# grep -c sh /etc/passwd\r\n0\r\n# " timeout_ms=10000
mp135.custom:uart_write data="grep -n sh /etc/passwd\r"
mp135.custom:uart_expect sentinel="# grep -n sh /etc/passwd\r\n# " timeout_ms=10000
mp135.custom:uart_write data="grep '\\(o\\)\\1' /etc/passwd\r"
mp135.custom:uart_expect sentinel="# grep '\\(o\\)\\1' /etc/passwd\r\nroot:VwL97VCAx1Qhs:0:1::/:\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=grep
```

Verify:

```
expected = r"""grep '^root' /etc/passwd
root:VwL97VCAx1Qhs:0:1::/:
# grep -v root /etc/passwd
daemon:x:1:1::/:
sys::2:2::/usr/sys:
bin::3:3::/bin:
uucp::4:4::/usr/lib/uucp:/usr/lib/uucico
dmr::7:3::/usr/dmr:
# grep -c sh /etc/passwd
0
# grep -n sh /etc/passwd
# grep '\(o\)\1' /etc/passwd
root:VwL97VCAx1Qhs:0:1::/:
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### SED

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="sed s/x/y/ /etc/passwd\r"
mp135.custom:uart_expect sentinel="sed s/x/y/ /etc/passwd\r\nroot:VwL97VCAy1Qhs:0:1::/:\r\nroot:VwL97VCAy1Qhs:0:1::/:\r\ndaemon:y:1:1::/:\r\ndaemon:y:1:1::/:\r\nsys::2:2::/usr/sys:\r\nsys::2:2::/usr/sys:\r\nbin::3:3::/bin:\r\nbin::3:3::/bin:\r\nuucp::4:4::/usr/lib/uucp:/usr/lib/uucico\r\nuucp::4:4::/usr/lib/uucp:/usr/lib/uucico\r\ndmr::7:3::/usr/dmr:\r\ndmr::7:3::/usr/dmr:\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo x | sed s/x/y/\r"
mp135.custom:uart_expect sentinel="# echo x | sed s/x/y/\r\ny\r\ny\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=sed
```

Verify:

```
expected = """sed s/x/y/ /etc/passwd
root:VwL97VCAy1Qhs:0:1::/:
root:VwL97VCAy1Qhs:0:1::/:
daemon:y:1:1::/:
daemon:y:1:1::/:
sys::2:2::/usr/sys:
sys::2:2::/usr/sys:
bin::3:3::/bin:
bin::3:3::/bin:
uucp::4:4::/usr/lib/uucp:/usr/lib/uucico
uucp::4:4::/usr/lib/uucp:/usr/lib/uucico
dmr::7:3::/usr/dmr:
dmr::7:3::/usr/dmr:
# echo x | sed s/x/y/
y
y
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### AWK

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="echo edge > /tmp/END\r"
mp135.custom:uart_expect sentinel="echo edge > /tmp/END\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo start > /tmp/BEGIN\r"
mp135.custom:uart_expect sentinel="# echo start > /tmp/BEGIN\r\n# " timeout_ms=10000
mp135.custom:uart_write data="awk '{print $0}' /tmp/END\r"
mp135.custom:uart_expect sentinel="# awk '{print $0}' /tmp/END\r\nedge\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cd /tmp\r"
mp135.custom:uart_expect sentinel="# cd /tmp\r\n# " timeout_ms=10000
mp135.custom:uart_write data="awk '{print $0}' END\r"
mp135.custom:uart_expect sentinel="# awk '{print $0}' END\r\nedge\r\n# " timeout_ms=10000
mp135.custom:uart_write data="awk '{print $0}' BEGIN\r"
mp135.custom:uart_expect sentinel="# awk '{print $0}' BEGIN\r\nstart\r\n# " timeout_ms=10000
mp135.custom:uart_write data="awk 'BEGIN {print 7}'\r"
mp135.custom:uart_expect sentinel="# awk 'BEGIN {print 7}'\r\n7\r\n# " timeout_ms=10000
mp135.custom:uart_write data="awk 'END {print NR}' /etc/passwd\r"
mp135.custom:uart_expect sentinel="# awk 'END {print NR}' /etc/passwd\r\n6\r\n# " timeout_ms=10000
mp135.custom:uart_write data="awk '{n=n+1} END {print n}' /etc/passwd\r"
mp135.custom:uart_expect sentinel="# awk '{n=n+1} END {print n}' /etc/passwd\r\n6\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo 'a b' | awk '{print $2}'\r"
mp135.custom:uart_expect sentinel="# echo 'a b' | awk '{print $2}'\r\nb\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=awk
```

Verify:

```
expected = """echo edge > /tmp/END
# echo start > /tmp/BEGIN
# awk '{print $0}' /tmp/END
edge
# cd /tmp
# awk '{print $0}' END
edge
# awk '{print $0}' BEGIN
start
# awk 'BEGIN {print 7}'
7
# awk 'END {print NR}' /etc/passwd
6
# awk '{n=n+1} END {print n}' /etc/passwd
6
# echo 'a b' | awk '{print $2}'
b
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### CP

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="mkdir /tmp/cpdir\r"
mp135.custom:uart_expect sentinel="mkdir /tmp/cpdir\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo srcA > /tmp/A\r"
mp135.custom:uart_expect sentinel="# echo srcA > /tmp/A\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo srcB > /tmp/B\r"
mp135.custom:uart_expect sentinel="# echo srcB > /tmp/B\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cp /tmp/A /tmp/B /tmp/cpdir\r"
mp135.custom:uart_expect sentinel="# cp /tmp/A /tmp/B /tmp/cpdir\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cat /tmp/cpdir/A\r"
mp135.custom:uart_expect sentinel="# cat /tmp/cpdir/A\r\nsrcA\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cat /tmp/cpdir/B\r"
mp135.custom:uart_expect sentinel="# cat /tmp/cpdir/B\r\nsrcB\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cp /tmp/A /tmp/A\r"
mp135.custom:uart_expect sentinel="# cp /tmp/A /tmp/A\r\ncp: cannot copy file to itself.\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=cp
```

Verify:

```
expected = """mkdir /tmp/cpdir
# echo srcA > /tmp/A
# echo srcB > /tmp/B
# cp /tmp/A /tmp/B /tmp/cpdir
# cat /tmp/cpdir/A
srcA
# cat /tmp/cpdir/B
srcB
# cp /tmp/A /tmp/A
cp: cannot copy file to itself.
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### MV

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="echo content > /tmp/mvsrc\r"
mp135.custom:uart_expect sentinel="echo content > /tmp/mvsrc\r\n# " timeout_ms=10000
mp135.custom:uart_write data="mv /tmp/mvsrc /tmp/mvsrc\r"
mp135.custom:uart_expect sentinel="# mv /tmp/mvsrc /tmp/mvsrc\r\nmv: /tmp/mvsrc and /tmp/mvsrc are identical\r\n# " timeout_ms=10000
mp135.custom:uart_write data="mkdir /tmp/mvA\r"
mp135.custom:uart_expect sentinel="# mkdir /tmp/mvA\r\n# " timeout_ms=10000
mp135.custom:uart_write data="mkdir /tmp/mvB\r"
mp135.custom:uart_expect sentinel="# mkdir /tmp/mvB\r\n# " timeout_ms=10000
mp135.custom:uart_write data="mkdir /tmp/mvA/sub\r"
mp135.custom:uart_expect sentinel="# mkdir /tmp/mvA/sub\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo data > /tmp/mvA/sub/file\r"
mp135.custom:uart_expect sentinel="# echo data > /tmp/mvA/sub/file\r\n# " timeout_ms=10000
mp135.custom:uart_write data="mv /tmp/mvA/sub /tmp/mvB/sub\r"
mp135.custom:uart_expect sentinel="# mv /tmp/mvA/sub /tmp/mvB/sub\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cat /tmp/mvB/sub/file\r"
mp135.custom:uart_expect sentinel="# cat /tmp/mvB/sub/file\r\ndata\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=mv
```

Verify:

```
expected = """echo content > /tmp/mvsrc
# mv /tmp/mvsrc /tmp/mvsrc
mv: /tmp/mvsrc and /tmp/mvsrc are identical
# mkdir /tmp/mvA
# mkdir /tmp/mvB
# mkdir /tmp/mvA/sub
# echo data > /tmp/mvA/sub/file
# mv /tmp/mvA/sub /tmp/mvB/sub
# cat /tmp/mvB/sub/file
data
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### TOUCH

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="touch /tmp/tnew\r"
mp135.custom:uart_expect sentinel="touch /tmp/tnew\r\n# " timeout_ms=10000
mp135.custom:uart_write data="ls /tmp/tnew\r"
mp135.custom:uart_expect sentinel="# ls /tmp/tnew\r\n/tmp/tnew\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo old > /tmp/told\r"
mp135.custom:uart_expect sentinel="# echo old > /tmp/told\r\n# " timeout_ms=10000
mp135.custom:uart_write data="touch /tmp/told\r"
mp135.custom:uart_expect sentinel="# touch /tmp/told\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cat /tmp/told\r"
mp135.custom:uart_expect sentinel="# cat /tmp/told\r\nold\r\n# " timeout_ms=10000
mp135.custom:uart_write data="touch -c /tmp/tabsent\r"
mp135.custom:uart_expect sentinel="# touch -c /tmp/tabsent\r\ntouch: file /tmp/tabsent does not exist.\r\n# " timeout_ms=10000
mp135.custom:uart_write data="ls /tmp/tabsent\r"
mp135.custom:uart_expect sentinel="# ls /tmp/tabsent\r\n/tmp/tabsent not found\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=touch
```

Verify:

```
expected = """touch /tmp/tnew
# ls /tmp/tnew
/tmp/tnew
# echo old > /tmp/told
# touch /tmp/told
# cat /tmp/told
old
# touch -c /tmp/tabsent
touch: file /tmp/tabsent does not exist.
# ls /tmp/tabsent
/tmp/tabsent not found
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### TR

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="echo abcdef | tr -d def\r"
mp135.custom:uart_expect sentinel="echo abcdef | tr -d def\r\nabc\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo aaabbb | tr -s ab AB\r"
mp135.custom:uart_expect sentinel="# echo aaabbb | tr -s ab AB\r\nAB\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo Hello123 | tr -cd 0-9\r"
mp135.custom:uart_expect sentinel="# echo Hello123 | tr -cd 0-9\r\n123# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=tr
```

Verify:

```
expected = """echo abcdef | tr -d def
abc
# echo aaabbb | tr -s ab AB
AB
# echo Hello123 | tr -cd 0-9
123# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### SPLIT

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="echo line1 > /tmp/spi\r"
mp135.custom:uart_expect sentinel="echo line1 > /tmp/spi\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo line2 >> /tmp/spi\r"
mp135.custom:uart_expect sentinel="# echo line2 >> /tmp/spi\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo line3 >> /tmp/spi\r"
mp135.custom:uart_expect sentinel="# echo line3 >> /tmp/spi\r\n# " timeout_ms=10000
mp135.custom:uart_write data="split -1 /tmp/spi /tmp/x\r"
mp135.custom:uart_expect sentinel="# split -1 /tmp/spi /tmp/x\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cat /tmp/xaa\r"
mp135.custom:uart_expect sentinel="# cat /tmp/xaa\r\nline1\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cat /tmp/xab\r"
mp135.custom:uart_expect sentinel="# cat /tmp/xab\r\nline2\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cat /tmp/xac\r"
mp135.custom:uart_expect sentinel="# cat /tmp/xac\r\nline3\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=split
```

Verify:

```
expected = """echo line1 > /tmp/spi
# echo line2 >> /tmp/spi
# echo line3 >> /tmp/spi
# split -1 /tmp/spi /tmp/x
# cat /tmp/xaa
line1
# cat /tmp/xab
line2
# cat /tmp/xac
line3
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### TSORT

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="echo a b > /tmp/ts\r"
mp135.custom:uart_expect sentinel="echo a b > /tmp/ts\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo b c >> /tmp/ts\r"
mp135.custom:uart_expect sentinel="# echo b c >> /tmp/ts\r\n# " timeout_ms=10000
mp135.custom:uart_write data="tsort /tmp/ts\r"
mp135.custom:uart_expect sentinel="# tsort /tmp/ts\r\na\r\nb\r\nc\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=tsort
```

Verify:

```
expected = """echo a b > /tmp/ts
# echo b c >> /tmp/ts
# tsort /tmp/ts
a
b
c
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### WRITE

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="write\r"
mp135.custom:uart_expect sentinel="write\r\nusage: write user [ttyname]\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=write
```

Verify:

```
expected = """write
usage: write user [ttyname]
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### COMM

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="comm /etc/passwd /etc/passwd\r"
mp135.custom:uart_expect sentinel="comm /etc/passwd /etc/passwd\r\n\t\troot:VwL97VCAx1Qhs:0:1::/:\r\n\t\tdaemon:x:1:1::/:\r\n\t\tsys::2:2::/usr/sys:\r\n\t\tbin::3:3::/bin:\r\n\t\tuucp::4:4::/usr/lib/uucp:/usr/lib/uucico\r\n\t\tdmr::7:3::/usr/dmr:\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=comm
```

Verify:

```
expected = """comm /etc/passwd /etc/passwd
		root:VwL97VCAx1Qhs:0:1::/:
		daemon:x:1:1::/:
		sys::2:2::/usr/sys:
		bin::3:3::/bin:
		uucp::4:4::/usr/lib/uucp:/usr/lib/uucico
		dmr::7:3::/usr/dmr:
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### CRYPT

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="echo hello | crypt key | crypt key\r"
mp135.custom:uart_expect sentinel="echo hello | crypt key | crypt key\r\nhello\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=crypt
```

Verify:

```
expected = """echo hello | crypt key | crypt key
hello
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### TIME

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="time\r"
mp135.custom:uart_expect sentinel="time\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=time
```

Verify:

```
expected = """time
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### OSH

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls /bin/osh\r"
mp135.custom:uart_expect sentinel="ls /bin/osh\r\n/bin/osh\r\n# " timeout_ms=10000
mp135.custom:uart_write data='osh -c \"echo OSH_OK\"\r'
mp135.custom:uart_expect sentinel='# osh -c \"echo OSH_OK\"\r\nOSH_OK\r\n# ' timeout_ms=10000
mp135.custom:uart_write data='echo hi | osh -c \"cat\"\r'
mp135.custom:uart_expect sentinel='# echo hi | osh -c \"cat\"\r\nhi\r\n# ' timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=osh
```

Verify:

```
expected = """ls /bin/osh
/bin/osh
# osh -c "echo OSH_OK"
OSH_OK
# echo hi | osh -c "cat"
hi
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### UNITS

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls /usr/lib/units\r"
mp135.custom:uart_expect sentinel="ls /usr/lib/units\r\n/usr/lib/units\r\n# " timeout_ms=10000
mp135.custom:uart_write data="(echo foot; echo inch) | units\r"
mp135.custom:uart_expect sentinel="# (echo foot; echo inch) | units\r\n437 units; 3191 bytes\r\n\r\nyou have: you want: \t* 1.200000e+01\r\n\t/ 8.333333e-02\r\nyou have: \r\n# " timeout_ms=10000
mp135.custom:uart_write data="(echo mile; echo foot) | units\r"
mp135.custom:uart_expect sentinel="# (echo mile; echo foot) | units\r\n437 units; 3191 bytes\r\n\r\nyou have: you want: \t* 5.280000e+03\r\n\t/ 1.893939e-04\r\nyou have: \r\n# " timeout_ms=10000
mp135.custom:uart_write data="(echo hour; echo minute) | units\r"
mp135.custom:uart_expect sentinel="# (echo hour; echo minute) | units\r\n437 units; 3191 bytes\r\n\r\nyou have: you want: \t* 6.000000e+01\r\n\t/ 1.666667e-02\r\nyou have: \r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=units
```

Verify:

```
expected = """ls /usr/lib/units
/usr/lib/units
# (echo foot; echo inch) | units
437 units; 3191 bytes

you have: you want: 	* 1.200000e+01
	/ 8.333333e-02
you have: 
# (echo mile; echo foot) | units
437 units; 3191 bytes

you have: you want: 	* 5.280000e+03
	/ 1.893939e-04
you have: 
# (echo hour; echo minute) | units
437 units; 3191 bytes

you have: you want: 	* 6.000000e+01
	/ 1.666667e-02
you have: 
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### MKNOD

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="mknod\r"
mp135.custom:uart_expect sentinel="mknod\r\narg count\r\nusage: mknod name b/c major minor\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=mknod
```

Verify:

```
expected = """mknod
arg count
usage: mknod name b/c major minor
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### NEWGRP

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="newgrp\r"
mp135.custom:uart_expect sentinel="newgrp\r\nusage: newgrp groupname\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=newgrp
```

Verify:

```
expected = """newgrp
usage: newgrp groupname
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### CLRI

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="clri\r"
mp135.custom:uart_expect sentinel="clri\r\nusage: clri filsys inumber ...\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=clri
```

Verify:

```
expected = """clri
usage: clri filsys inumber ...
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### CHECKEQ

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="echo hello | checkeq\r"
mp135.custom:uart_expect sentinel="echo hello | checkeq\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=checkeq
```

Verify:

```
expected = """echo hello | checkeq
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### MOUNT

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="mount\r"
mp135.custom:uart_expect sentinel="mount\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=mount
```

Verify:

```
expected = """mount
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### UMOUNT

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="umount\r"
mp135.custom:uart_expect sentinel="umount\r\narg count\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=umount
```

Verify:

```
expected = """umount
arg count
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### DCHECK

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="dcheck /dev/root\r"
mp135.custom:uart_expect sentinel="dcheck /dev/root\r\n/dev/root:\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=dcheck
```

Verify:

```
expected = """dcheck /dev/root
/dev/root:
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### ICHECK

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="icheck /dev/root\r"
mp135.custom:uart_expect sentinel="icheck /dev/root\r\n/dev/root:\r\nfiles    204 (r=177,d=21,b=1,c=5)\r\nused    5639 (i=125,ii=4,iii=0,d=5506)\r\nfree    5626\r\nmissing    0\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=icheck
```

Verify:

```
expected = """icheck /dev/root
/dev/root:
files    204 (r=177,d=21,b=1,c=5)
used    5639 (i=125,ii=4,iii=0,d=5506)
free    5626
missing    0
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### NCHECK

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ncheck /dev/root | sed 's/^[0-9][0-9]*/<ino>/' | grep -v '/usr/spool/at/70[.]'\r"
mp135.custom:uart_expect sentinel="<ino>	/dut/alink\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=ncheck
```

Verify:

```
expected = """ncheck /dev/root | sed 's/^[0-9][0-9]*/<ino>/' | grep -v '/usr/spool/at/70[.]'
/dev/root:
/dev/root:
<ino>	/bin/.
<ino>	/bin/.
<ino>	/dev/.
<ino>	/dev/.
<ino>	/etc/.
<ino>	/etc/.
<ino>	/tmp/.
<ino>	/tmp/.
<ino>	/usr/.
<ino>	/usr/.
<ino>	/unix
<ino>	/unix
<ino>	/.profile
<ino>	/.profile
<ino>	/dut/.
<ino>	/dut/.
<ino>	/j1
<ino>	/j1
<ino>	/j2
<ino>	/j2
<ino>	/jt1
<ino>	/jt1
<ino>	/jt2
<ino>	/jt2
<ino>	/d/.
<ino>	/d/.
<ino>	/a
<ino>	/a
<ino>	/b
<ino>	/b
<ino>	/bin/1
<ino>	/bin/1
<ino>	/bin/[
<ino>	/bin/[
<ino>	/bin/ac
<ino>	/bin/ac
<ino>	/bin/at
<ino>	/bin/at
<ino>	/bin/arcv
<ino>	/bin/arcv
<ino>	/bin/awk
<ino>	/bin/awk
<ino>	/bin/basename
<ino>	/bin/basename
<ino>	/bin/cal
<ino>	/bin/cal
<ino>	/bin/calendar
<ino>	/bin/calendar
<ino>	/bin/cat
<ino>	/bin/cat
<ino>	/bin/cb
<ino>	/bin/cb
<ino>	/bin/checkeq
<ino>	/bin/checkeq
<ino>	/bin/chgrp
<ino>	/bin/chgrp
<ino>	/bin/chmod
<ino>	/bin/chmod
<ino>	/bin/chown
<ino>	/bin/chown
<ino>	/bin/clri
<ino>	/bin/clri
<ino>	/bin/cmp
<ino>	/bin/cmp
<ino>	/bin/col
<ino>	/bin/col
<ino>	/bin/comm
<ino>	/bin/comm
<ino>	/bin/cp
<ino>	/bin/cp
<ino>	/bin/crypt
<ino>	/bin/crypt
<ino>	/bin/date
<ino>	/bin/date
<ino>	/bin/dc
<ino>	/bin/dc
<ino>	/bin/dcheck
<ino>	/bin/dcheck
<ino>	/bin/dd
<ino>	/bin/dd
<ino>	/bin/df
<ino>	/bin/df
<ino>	/bin/diff
<ino>	/bin/diff
<ino>	/bin/diff3
<ino>	/bin/diff3
<ino>	/bin/deroff
<ino>	/bin/deroff
<ino>	/bin/dmesg
<ino>	/bin/dmesg
<ino>	/bin/du
<ino>	/bin/du
<ino>	/bin/dump
<ino>	/bin/dump
<ino>	/bin/dumpdir
<ino>	/bin/dumpdir
<ino>	/bin/echo
<ino>	/bin/echo
<ino>	/bin/ed
<ino>	/bin/ed
<ino>	/bin/egrep
<ino>	/bin/egrep
<ino>	/bin/expr
<ino>	/bin/expr
<ino>	/bin/fgrep
<ino>	/bin/fgrep
<ino>	/bin/file
<ino>	/bin/file
<ino>	/bin/factor
<ino>	/bin/factor
<ino>	/bin/find
<ino>	/bin/find
<ino>	/bin/false
<ino>	/bin/false
<ino>	/bin/grep
<ino>	/bin/grep
<ino>	/bin/graph
<ino>	/bin/graph
<ino>	/bin/icheck
<ino>	/bin/icheck
<ino>	/bin/iostat
<ino>	/bin/iostat
<ino>	/bin/join
<ino>	/bin/join
<ino>	/bin/kill
<ino>	/bin/kill
<ino>	/bin/ln
<ino>	/bin/ln
<ino>	/bin/login
<ino>	/bin/login
<ino>	/bin/look
<ino>	/bin/look
<ino>	/bin/ls
<ino>	/bin/ls
<ino>	/bin/mesg
<ino>	/bin/mesg
<ino>	/bin/mkdir
<ino>	/bin/mkdir
<ino>	/bin/mknod
<ino>	/bin/mknod
<ino>	/bin/mount
<ino>	/bin/mount
<ino>	/bin/mv
<ino>	/bin/mv
<ino>	/bin/ncheck
<ino>	/bin/ncheck
<ino>	/bin/newgrp
<ino>	/bin/newgrp
<ino>	/bin/nice
<ino>	/bin/nice
<ino>	/bin/nohup
<ino>	/bin/nohup
<ino>	/bin/od
<ino>	/bin/od
<ino>	/bin/osh
<ino>	/bin/osh
<ino>	/bin/passwd
<ino>	/bin/passwd
<ino>	/bin/pr
<ino>	/bin/pr
<ino>	/bin/primes
<ino>	/bin/primes
<ino>	/bin/prof
<ino>	/bin/prof
<ino>	/bin/ps
<ino>	/bin/ps
<ino>	/bin/pstat
<ino>	/bin/pstat
<ino>	/bin/ptx
<ino>	/bin/ptx
<ino>	/bin/pwd
<ino>	/bin/pwd
<ino>	/bin/quot
<ino>	/bin/quot
<ino>	/bin/random
<ino>	/bin/random
<ino>	/bin/restor
<ino>	/bin/restor
<ino>	/bin/rev
<ino>	/bin/rev
<ino>	/bin/rm
<ino>	/bin/rm
<ino>	/bin/rmdir
<ino>	/bin/rmdir
<ino>	/bin/sa
<ino>	/bin/sa
<ino>	/bin/sed
<ino>	/bin/sed
<ino>	/bin/sh
<ino>	/bin/sh
<ino>	/bin/sleep
<ino>	/bin/sleep
<ino>	/bin/sort
<ino>	/bin/sort
<ino>	/bin/sp
<ino>	/bin/sp
<ino>	/bin/spline
<ino>	/bin/spline
<ino>	/bin/split
<ino>	/bin/split
<ino>	/bin/stty
<ino>	/bin/stty
<ino>	/bin/su
<ino>	/bin/su
<ino>	/bin/sum
<ino>	/bin/sum
<ino>	/bin/sync
<ino>	/bin/sync
<ino>	/bin/tabs
<ino>	/bin/tabs
<ino>	/bin/tail
<ino>	/bin/tail
<ino>	/bin/tar
<ino>	/bin/tar
<ino>	/bin/tc
<ino>	/bin/tc
<ino>	/bin/tee
<ino>	/bin/tee
<ino>	/bin/test
<ino>	/bin/test
<ino>	/bin/time
<ino>	/bin/time
<ino>	/bin/tk
<ino>	/bin/tk
<ino>	/bin/touch
<ino>	/bin/touch
<ino>	/bin/tp
<ino>	/bin/tp
<ino>	/bin/tr
<ino>	/bin/tr
<ino>	/bin/true
<ino>	/bin/true
<ino>	/bin/tsort
<ino>	/bin/tsort
<ino>	/bin/tty
<ino>	/bin/tty
<ino>	/bin/umount
<ino>	/bin/umount
<ino>	/bin/uniq
<ino>	/bin/uniq
<ino>	/bin/units
<ino>	/bin/units
<ino>	/bin/vpr
<ino>	/bin/vpr
<ino>	/bin/wall
<ino>	/bin/wall
<ino>	/bin/wc
<ino>	/bin/wc
<ino>	/bin/who
<ino>	/bin/who
<ino>	/bin/write
<ino>	/bin/write
<ino>	/bin/yes
<ino>	/bin/yes
<ino>	/dev/console
<ino>	/dev/console
<ino>	/dev/mem
<ino>	/dev/mem
<ino>	/dev/kmem
<ino>	/dev/kmem
<ino>	/dev/null
<ino>	/dev/null
<ino>	/dev/root
<ino>	/dev/root
<ino>	/dev/tty
<ino>	/dev/tty
<ino>	/etc/accton
<ino>	/etc/accton
<ino>	/etc/atrun
<ino>	/etc/atrun
<ino>	/etc/cron
<ino>	/etc/cron
<ino>	/etc/ddate
<ino>	/etc/ddate
<ino>	/etc/getty
<ino>	/etc/getty
<ino>	/etc/init
<ino>	/etc/init
<ino>	/etc/passwd
<ino>	/etc/passwd
<ino>	/etc/group
<ino>	/etc/group
<ino>	/etc/rc
<ino>	/etc/rc
<ino>	/etc/ttys
<ino>	/etc/ttys
<ino>	/etc/update
<ino>	/etc/update
<ino>	/etc/utmp
<ino>	/etc/utmp
<ino>	/tmp/.keep
<ino>	/tmp/.keep
<ino>	/tmp/date.set
<ino>	/tmp/date.set
<ino>	/tmp/at.in
<ino>	/tmp/at.in
<ino>	/tmp/cron.mark
<ino>	/tmp/cron.mark
<ino>	/tmp/dmesg.out
<ino>	/tmp/dmesg.out
<ino>	/tmp/base
<ino>	/tmp/base
<ino>	/tmp/left
<ino>	/tmp/left
<ino>	/tmp/right
<ino>	/tmp/right
<ino>	/tmp/d13
<ino>	/tmp/d13
<ino>	/tmp/d23
<ino>	/tmp/d23
<ino>	/tmp/END
<ino>	/tmp/END
<ino>	/tmp/BEGIN
<ino>	/tmp/BEGIN
<ino>	/tmp/cpdir/.
<ino>	/tmp/cpdir/.
<ino>	/tmp/A
<ino>	/tmp/A
<ino>	/tmp/B
<ino>	/tmp/B
<ino>	/tmp/mvsrc
<ino>	/tmp/mvsrc
<ino>	/tmp/mvA/.
<ino>	/tmp/mvA/.
<ino>	/tmp/mvB/.
<ino>	/tmp/mvB/.
<ino>	/tmp/tnew
<ino>	/tmp/tnew
<ino>	/tmp/told
<ino>	/tmp/told
<ino>	/tmp/spi
<ino>	/tmp/spi
<ino>	/tmp/xaa
<ino>	/tmp/xaa
<ino>	/tmp/xab
<ino>	/tmp/xab
<ino>	/tmp/xac
<ino>	/tmp/xac
<ino>	/tmp/ts
<ino>	/tmp/ts
<ino>	/usr/adm/.
<ino>	/usr/adm/.
<ino>	/usr/dict/.
<ino>	/usr/dict/.
<ino>	/usr/games/.
<ino>	/usr/games/.
<ino>	/usr/lib/.
<ino>	/usr/lib/.
<ino>	/usr/spool/.
<ino>	/usr/spool/.
<ino>	/usr/adm/acct
<ino>	/usr/adm/acct
<ino>	/usr/adm/wtmp
<ino>	/usr/adm/wtmp
<ino>	/usr/dict/words
<ino>	/usr/dict/words
<ino>	/usr/games/arithmetic
<ino>	/usr/games/arithmetic
<ino>	/usr/games/backgammon
<ino>	/usr/games/backgammon
<ino>	/usr/games/fish
<ino>	/usr/games/fish
<ino>	/usr/games/fortune
<ino>	/usr/games/fortune
<ino>	/usr/games/hangman
<ino>	/usr/games/hangman
<ino>	/usr/games/lib/.
<ino>	/usr/games/lib/.
<ino>	/usr/games/quiz
<ino>	/usr/games/quiz
<ino>	/usr/games/wump
<ino>	/usr/games/wump
<ino>	/usr/games/lib/fortunes
<ino>	/usr/games/lib/fortunes
<ino>	/usr/lib/crontab
<ino>	/usr/lib/crontab
<ino>	/usr/lib/diffh
<ino>	/usr/lib/diffh
<ino>	/usr/lib/makekey
<ino>	/usr/lib/makekey
<ino>	/usr/lib/units
<ino>	/usr/lib/units
<ino>	/usr/spool/at/.
<ino>	/usr/spool/at/.
<ino>	/usr/spool/at/lasttimedone
<ino>	/usr/spool/at/lasttimedone
<ino>	/usr/spool/at/past/.
<ino>	/usr/spool/at/past/.
<ino>	/usr/spool/at/past/.keep
<ino>	/usr/spool/at/past/.keep
<ino>	/tmp/mvB/sub/file
<ino>	/tmp/mvB/sub/file
<ino>	/tmp/mvB/sub/.
<ino>	/tmp/mvB/sub/.
<ino>	/tmp/cpdir/A
<ino>	/tmp/cpdir/A
<ino>	/tmp/cpdir/B
<ino>	/tmp/cpdir/B
<ino>	/d/a
<ino>	/d/a
<ino>	/dut/sub/b
<ino>	/dut/sub/b
<ino>	/dut/sub/.
<ino>	/dut/sub/.
<ino>	/dut/a
<ino>	/dut/a
<ino>	/dut/alink
<ino>	/dut/alink
# echo __TEST_DONE__
__TEST_DONE__
# """

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### RANDOM

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="echo hi | random 0\r"
mp135.custom:uart_expect sentinel="echo hi | random 0\r\nhi\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=random
```

Verify:

```
expected = """echo hi | random 0
hi
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### STTY

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="stty\r"
mp135.custom:uart_expect sentinel="stty\r\nspeed 0 baud\r\nerase = '#'; kill = '@'\r\neven odd -nl echo \r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=stty
```

Verify:

```
expected = """stty
speed 0 baud
erase = '#'; kill = '@'
even odd -nl echo 
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### SU

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="su nosuchuser\r"
mp135.custom:uart_expect sentinel="su nosuchuser\r\nUnknown id: nosuchuser\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=su
```

Verify:

```
expected = """su nosuchuser
Unknown id: nosuchuser
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### TABS

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="tabs\r"
mp135.custom:uart_expect sentinel="tabs\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo TABS_STATUS:$?\r"
mp135.custom:uart_expect sentinel="# echo TABS_STATUS:$?\r\nTABS_STATUS:0\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=tabs
```

Verify:

```
expected = """tabs
# echo TABS_STATUS:$?
TABS_STATUS:0
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### WALL

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="wall </dev/null\r"
mp135.custom:uart_expect sentinel="wall </dev/null\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=wall
```

Verify:

```
expected = """wall </dev/null
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### PID

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="test $$ -gt 0 && echo top: numeric\r"
mp135.custom:uart_expect sentinel="test $$ -gt 0 && echo top: numeric\r\ntop: numeric\r\n# " timeout_ms=10000
mp135.custom:uart_write data="sh -c 'test $$ -gt 0 && echo subshell: numeric'\r"
mp135.custom:uart_expect sentinel="# sh -c 'test $$ -gt 0 && echo subshell: numeric'\r\nsubshell: numeric\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=pid
```

Verify:

```
expected = """test $$ -gt 0 && echo top: numeric
top: numeric
# sh -c 'test $$ -gt 0 && echo subshell: numeric'
subshell: numeric
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### DEVNULL

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="echo data > /dev/null\r"
mp135.custom:uart_expect sentinel="echo data > /dev/null\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo write_rc=$?\r"
mp135.custom:uart_expect sentinel="# echo write_rc=$?\r\nwrite_rc=0\r\n# " timeout_ms=10000
mp135.custom:uart_write data="wc /dev/null\r"
mp135.custom:uart_expect sentinel="# wc /dev/null\r\n      0      0       0 /dev/null\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cat /dev/null\r"
mp135.custom:uart_expect sentinel="# cat /dev/null\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo cat_rc=$?\r"
mp135.custom:uart_expect sentinel="# echo cat_rc=$?\r\ncat_rc=0\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=devnull
```

Verify:

```
expected = """echo data > /dev/null
# echo write_rc=$?
write_rc=0
# wc /dev/null
      0      0       0 /dev/null
# cat /dev/null
# echo cat_rc=$?
cat_rc=0
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### MT_BG_KILL

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="sh -c 'sleep 30 & pid=$!; kill -9 $pid; wait; echo done' 2>&1 | sed 's/[0-9][0-9]* Killed/PID Killed/'\r"
mp135.custom:uart_expect sentinel="sh -c 'sleep 30 & pid=$!; kill -9 $pid; wait; echo done' 2>&1 | sed 's/[0-9][0-9]* Killed/PID Killed/'\r\nsh: PID Killed\r\nsh: PID Killed\r\ndone\r\ndone\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=mt_bg_kill
```

Verify:

```
expected = """sh -c 'sleep 30 & pid=$!; kill -9 $pid; wait; echo done' 2>&1 | sed 's/[0-9][0-9]* Killed/PID Killed/'
sh: PID Killed
sh: PID Killed
done
done
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### MT_PIPE_INFINITE

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="yes alphabet | sed 3q\r"
mp135.custom:uart_expect sentinel="yes alphabet | sed 3q\r\nalphabet\r\nalphabet\r\nalphabet\r\n\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo done\r"
mp135.custom:uart_expect sentinel="# echo done\r\ndone\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=mt_pipe_infinite
```

Verify:

```
expected = """yes alphabet | sed 3q
alphabet
alphabet
alphabet

# echo done
done
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### MT_BIG_PIPE

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="echo count=`yes x | sed 40000q | wc -l`\r"
mp135.custom:uart_expect sentinel="echo count=`yes x | sed 40000q | wc -l`\r\ncount= 40000\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=mt_big_pipe
```

Verify:

```
expected = """echo count=`yes x | sed 40000q | wc -l`
count= 40000
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### MT_WAIT_ALL_BG

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="sh -c '( sleep 1; echo A ) & ( sleep 2; echo B ) & wait'\r"
mp135.custom:uart_expect sentinel="sh -c '( sleep 1; echo A ) & ( sleep 2; echo B ) & wait'\r\nA\r\nB\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo done\r"
mp135.custom:uart_expect sentinel="# echo done\r\ndone\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=mt_wait_all_bg
```

Verify:

```
expected = """sh -c '( sleep 1; echo A ) & ( sleep 2; echo B ) & wait'
A
B
# echo done
done
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### MT_CONCURRENT_SLEEP

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="echo before >/tmp/before\r"
mp135.custom:uart_expect sentinel="echo before >/tmp/before\r\n# " timeout_ms=10000
mp135.custom:uart_write data="sh -c '( sleep 2; echo after >/tmp/after ) & sleep 3; wait'\r"
mp135.custom:uart_expect sentinel="# sh -c '( sleep 2; echo after >/tmp/after ) & sleep 3; wait'\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cat /tmp/before /tmp/after\r"
mp135.custom:uart_expect sentinel="# cat /tmp/before /tmp/after\r\nbefore\r\nafter\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=mt_concurrent_sleep
```

Verify:

```
expected = """echo before >/tmp/before
# sh -c '( sleep 2; echo after >/tmp/after ) & sleep 3; wait'
# cat /tmp/before /tmp/after
before
after
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### NEWCMDS

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls /etc | grep accton\r"
mp135.custom:uart_expect sentinel="ls /etc | grep accton\r\naccton\r\n# " timeout_ms=10000
mp135.custom:uart_write data="ls /etc | grep update\r"
mp135.custom:uart_expect sentinel="# ls /etc | grep update\r\nupdate\r\n# " timeout_ms=10000
mp135.custom:uart_write data="ls /bin | grep passwd\r"
mp135.custom:uart_expect sentinel="# ls /bin | grep passwd\r\npasswd\r\n# " timeout_ms=10000
mp135.custom:uart_write data="ls /bin | grep diff3\r"
mp135.custom:uart_expect sentinel="# ls /bin | grep diff3\r\ndiff3\r\n# " timeout_ms=10000
mp135.custom:uart_write data="ls /usr/games\r"
mp135.custom:uart_expect sentinel="# ls /usr/games\r\narithmetic\r\nbackgammon\r\nfish\r\nfortune\r\nhangman\r\nlib\r\nquiz\r\nwump\r\n# " timeout_ms=10000
mp135.custom:uart_write data="diff3 /etc/passwd /etc/ttys /etc/group\r"
mp135.custom:uart_expect sentinel="# diff3 /etc/passwd /etc/ttys /etc/group\r\ndiff3: arg count\r\n# " timeout_ms=10000
mp135.custom:uart_write data="ls /usr/games/lib\r"
mp135.custom:uart_expect sentinel="# ls /usr/games/lib\r\nfortunes\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=newcmds
```

Verify:

```
expected = """ls /etc | grep accton
accton
# ls /etc | grep update
update
# ls /bin | grep passwd
passwd
# ls /bin | grep diff3
diff3
# ls /usr/games
arithmetic
backgammon
fish
fortune
hangman
lib
quiz
wump
# diff3 /etc/passwd /etc/ttys /etc/group
diff3: arg count
# ls /usr/games/lib
fortunes
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### NEWCMDS2

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls /bin/dc /bin/tar /bin/tp /bin/ptx /bin/spline /bin/vpr /bin/quot\r"
mp135.custom:uart_expect sentinel="ls /bin/dc /bin/tar /bin/tp /bin/ptx /bin/spline /bin/vpr /bin/quot\r\n/bin/dc\r\n/bin/ptx\r\n/bin/quot\r\n/bin/spline\r\n/bin/tar\r\n/bin/tp\r\n/bin/vpr\r\n# " timeout_ms=10000
mp135.custom:uart_write data="ls /bin/dump /bin/dumpdir /bin/restor /bin/tk\r"
mp135.custom:uart_expect sentinel="# ls /bin/dump /bin/dumpdir /bin/restor /bin/tk\r\n/bin/dump\r\n/bin/dumpdir\r\n/bin/restor\r\n/bin/tk\r\n# " timeout_ms=10000
mp135.custom:uart_write data="ls /usr/games/backgammon /usr/games/fish /usr/games/quiz /usr/games/wump\r"
mp135.custom:uart_expect sentinel="# ls /usr/games/backgammon /usr/games/fish /usr/games/quiz /usr/games/wump\r\n/usr/games/backgammon\r\n/usr/games/fish\r\n/usr/games/quiz\r\n/usr/games/wump\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=newcmds2
```

Verify:

```
expected = """ls /bin/dc /bin/tar /bin/tp /bin/ptx /bin/spline /bin/vpr /bin/quot
/bin/dc
/bin/ptx
/bin/quot
/bin/spline
/bin/tar
/bin/tp
/bin/vpr
# ls /bin/dump /bin/dumpdir /bin/restor /bin/tk
/bin/dump
/bin/dumpdir
/bin/restor
/bin/tk
# ls /usr/games/backgammon /usr/games/fish /usr/games/quiz /usr/games/wump
/usr/games/backgammon
/usr/games/fish
/usr/games/quiz
/usr/games/wump
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### NEWCMDS4

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls /usr/games/hangman /usr/games/quiz /bin/spline /bin/tk\r"
mp135.custom:uart_expect sentinel="ls /usr/games/hangman /usr/games/quiz /bin/spline /bin/tk\r\n/bin/spline\r\n/bin/tk\r\n/usr/games/hangman\r\n/usr/games/quiz\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=newcmds4
```

Verify:

```
expected = """ls /usr/games/hangman /usr/games/quiz /bin/spline /bin/tk
/bin/spline
/bin/tk
/usr/games/hangman
/usr/games/quiz
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### PS

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ps | sed 1q\r"
mp135.custom:uart_expect sentinel="ps | sed 1q\r\n   PID TTY TIME CMD\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=ps
```

Verify:

```
expected = """ps | sed 1q
   PID TTY TIME CMD
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### PSTAT

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="pstat -p | grep 'LOC S'\r"
mp135.custom:uart_expect sentinel="pstat -p | grep 'LOC S'\r\n   LOC S  F  PRI SIGNAL UID TIM CPU NI  PGRP   PID  PPID ADDR SIZE  WCHAN   LINK  TEXTP  CLKT\r\n# " timeout_ms=10000
mp135.custom:uart_write data="pstat -i | grep 'active inodes' | sed 's/^[0-9][0-9]*/N/' | sed 1q\r"
mp135.custom:uart_expect sentinel="# pstat -i | grep 'active inodes' | sed 's/^[0-9][0-9]*/N/' | sed 1q\r\nN active inodes\r\n# " timeout_ms=10000
mp135.custom:uart_write data="pstat -f | grep 'open files' | sed 's/^[0-9][0-9]*/N/' | sed 1q\r"
mp135.custom:uart_expect sentinel="# pstat -f | grep 'open files' | sed 's/^[0-9][0-9]*/N/' | sed 1q\r\nN open files\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=pstat
```

Verify:

```
expected = """pstat -p | grep 'LOC S'
   LOC S  F  PRI SIGNAL UID TIM CPU NI  PGRP   PID  PPID ADDR SIZE  WCHAN   LINK  TEXTP  CLKT
# pstat -i | grep 'active inodes' | sed 's/^[0-9][0-9]*/N/' | sed 1q
N active inodes
# pstat -f | grep 'open files' | sed 's/^[0-9][0-9]*/N/' | sed 1q
N open files
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### PROF

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="prof\r"
mp135.custom:uart_expect sentinel="prof\r\na.out: not found\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=prof
```

Verify:

```
expected = """prof
a.out: not found
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### TC

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="tc < /dev/null | od -c\r"
mp135.custom:uart_expect sentinel="tc < /dev/null | od -c\r\n0000000 035   7   l 177       @ 033   ; 037  \\0\r\n0000011\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo hello | tc | od -c\r"
mp135.custom:uart_expect sentinel="# echo hello | tc | od -c\r\n0000000 035   8   l   o       @ 035   b   @ 035   7   d   y   @ 035   l\r\n0000020   o   @ 035   g   @ 037   b 035 177   @ 033   ; 037  \\0\r\n0000035\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=tc
```

Verify:

```
expected = r"""tc < /dev/null | od -c
0000000 035   7   l 177       @ 033   ; 037  \0
0000011
# echo hello | tc | od -c
0000000 035   8   l   o       @ 035   b   @ 035   7   d   y   @ 035   l
0000020   o   @ 035   g   @ 037   b 035 177   @ 033   ; 037  \0
0000035
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### GRAPH

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls /bin/graph\r"
mp135.custom:uart_expect sentinel="ls /bin/graph\r\n/bin/graph\r\n# " timeout_ms=10000
mp135.custom:uart_write data='/bin/echo \"0 0\" >/tmp/g\r'
mp135.custom:uart_expect sentinel='# /bin/echo \"0 0\" >/tmp/g\r\n# ' timeout_ms=10000
mp135.custom:uart_write data='/bin/echo \"1 1\" >>/tmp/g\r'
mp135.custom:uart_expect sentinel='# /bin/echo \"1 1\" >>/tmp/g\r\n# ' timeout_ms=10000
mp135.custom:uart_write data="graph -g 0 -m 0 /tmp/g | od -c\r"
mp135.custom:uart_expect sentinel="# graph -g 0 -m 0 /tmp/g | od -c\r\n0000000   s  \\0  \\0  \\0  \\0  \\0 020  \\0 020   e   m 310  \\0 214  \\0   p\r\n0000020 310  \\0 310  \\0   p 240 017 240 017   f   s   o   l   i   d  \\n\r\n0000040   m 001  \\0 001  \\0  \\0\r\n0000045\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=graph
```

Verify:

```
expected = r"""ls /bin/graph
/bin/graph
# /bin/echo "0 0" >/tmp/g
# /bin/echo "1 1" >>/tmp/g
# graph -g 0 -m 0 /tmp/g | od -c
0000000   s  \0  \0  \0  \0  \0 020  \0 020   e   m 310  \0 214  \0   p
0000020 310  \0 310  \0   p 240 017 240 017   f   s   o   l   i   d  \n
0000040   m 001  \0 001  \0  \0
0000045
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### TAR

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls /bin/tar\r"
mp135.custom:uart_expect sentinel="ls /bin/tar\r\n/bin/tar\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cd /tmp\r"
mp135.custom:uart_expect sentinel="# cd /tmp\r\n# " timeout_ms=10000
mp135.custom:uart_write data="rm -rf tarin tarout tappex arch.tar extra\r"
mp135.custom:uart_expect sentinel="# rm -rf tarin tarout tappex arch.tar extra\r\n# " timeout_ms=10000
mp135.custom:uart_write data="mkdir tarin\r"
mp135.custom:uart_expect sentinel="# mkdir tarin\r\n# " timeout_ms=10000
mp135.custom:uart_write data="mkdir tarin/sub\r"
mp135.custom:uart_expect sentinel="# mkdir tarin/sub\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo alpha > tarin/a\r"
mp135.custom:uart_expect sentinel="# echo alpha > tarin/a\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo beta > tarin/sub/b\r"
mp135.custom:uart_expect sentinel="# echo beta > tarin/sub/b\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo gamma > tarin/c\r"
mp135.custom:uart_expect sentinel="# echo gamma > tarin/c\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/tar cf arch.tar tarin\r"
mp135.custom:uart_expect sentinel="# /bin/tar cf arch.tar tarin\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/tar tf arch.tar\r"
mp135.custom:uart_expect sentinel="# /bin/tar tf arch.tar\r\nTar: blocksize = 9\r\ntarin/sub/b\r\ntarin/a\r\ntarin/c\r\n# " timeout_ms=10000
mp135.custom:uart_write data="mkdir tarout\r"
mp135.custom:uart_expect sentinel="# mkdir tarout\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cd tarout\r"
mp135.custom:uart_expect sentinel="# cd tarout\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/tar xf ../arch.tar\r"
mp135.custom:uart_expect sentinel="# /bin/tar xf ../arch.tar\r\nTar: blocksize = 9\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cat tarin/a\r"
mp135.custom:uart_expect sentinel="# cat tarin/a\r\nalpha\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cat tarin/sub/b\r"
mp135.custom:uart_expect sentinel="# cat tarin/sub/b\r\nbeta\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cat tarin/c\r"
mp135.custom:uart_expect sentinel="# cat tarin/c\r\ngamma\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cd ..\r"
mp135.custom:uart_expect sentinel="# cd ..\r\n# " timeout_ms=10000
mp135.custom:uart_write data="find /tmp/tarout/tarin -type f -print\r"
mp135.custom:uart_expect sentinel="# find /tmp/tarout/tarin -type f -print\r\n/tmp/tarout/tarin/sub/b\r\n/tmp/tarout/tarin/a\r\n/tmp/tarout/tarin/c\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=tar
```

Verify:

```
expected = """ls /bin/tar
/bin/tar
# cd /tmp
# rm -rf tarin tarout tappex arch.tar extra
# mkdir tarin
# mkdir tarin/sub
# echo alpha > tarin/a
# echo beta > tarin/sub/b
# echo gamma > tarin/c
# /bin/tar cf arch.tar tarin
# /bin/tar tf arch.tar
Tar: blocksize = 9
tarin/sub/b
tarin/a
tarin/c
# mkdir tarout
# cd tarout
# /bin/tar xf ../arch.tar
Tar: blocksize = 9
# cat tarin/a
alpha
# cat tarin/sub/b
beta
# cat tarin/c
gamma
# cd ..
# find /tmp/tarout/tarin -type f -print
/tmp/tarout/tarin/sub/b
/tmp/tarout/tarin/a
/tmp/tarout/tarin/c
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### TAR_APPEND_FILTERS

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="echo delta > extra\r"
mp135.custom:uart_expect sentinel="echo delta > extra\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/tar rf arch.tar extra\r"
mp135.custom:uart_expect sentinel="# /bin/tar rf arch.tar extra\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/tar tf arch.tar\r"
mp135.custom:uart_expect sentinel="# /bin/tar tf arch.tar\r\nTar: blocksize = 11\r\ntarin/sub/b\r\ntarin/a\r\ntarin/c\r\nextra\r\n# " timeout_ms=10000
mp135.custom:uart_write data="mkdir tappex\r"
mp135.custom:uart_expect sentinel="# mkdir tappex\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cd tappex\r"
mp135.custom:uart_expect sentinel="# cd tappex\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/tar xf ../arch.tar extra\r"
mp135.custom:uart_expect sentinel="# /bin/tar xf ../arch.tar extra\r\nTar: blocksize = 11\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cat extra\r"
mp135.custom:uart_expect sentinel="# cat extra\r\ndelta\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cd ..\r"
mp135.custom:uart_expect sentinel="# cd ..\r\n# " timeout_ms=10000
mp135.custom:uart_write data="/bin/tar cf - tarin/a | od -c | sed 1q\r"
mp135.custom:uart_expect sentinel="# /bin/tar cf - tarin/a | od -c | sed 1q\r\n0000000   t   a   r   i   n   /   a  \\0  \\0  \\0  \\0  \\0  \\0  \\0  \\0  \\0\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo zeta > reg1\r"
mp135.custom:uart_expect sentinel="# echo zeta > reg1\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo alpha >> reg1\r"
mp135.custom:uart_expect sentinel="# echo alpha >> reg1\r\n# " timeout_ms=10000
mp135.custom:uart_write data="sort reg1\r"
mp135.custom:uart_expect sentinel="# sort reg1\r\nalpha\r\nzeta\r\n# " timeout_ms=10000
mp135.custom:uart_write data="sed s/alpha/ALPHA/ reg1\r"
mp135.custom:uart_expect sentinel="# sed s/alpha/ALPHA/ reg1\r\nzeta\r\nzeta\r\nALPHA\r\nALPHA\r\n# " timeout_ms=10000
mp135.custom:uart_write data="find tarout -type d -print | sort\r"
mp135.custom:uart_expect sentinel="# find tarout -type d -print | sort\r\ntarout\r\ntarout/tarin\r\ntarout/tarin/sub\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=tar_append_filters
```

Verify:

```
expected = r"""echo delta > extra
# /bin/tar rf arch.tar extra
# /bin/tar tf arch.tar
Tar: blocksize = 11
tarin/sub/b
tarin/a
tarin/c
extra
# mkdir tappex
# cd tappex
# /bin/tar xf ../arch.tar extra
Tar: blocksize = 11
# cat extra
delta
# cd ..
# /bin/tar cf - tarin/a | od -c | sed 1q
0000000   t   a   r   i   n   /   a  \0  \0  \0  \0  \0  \0  \0  \0  \0
# echo zeta > reg1
# echo alpha >> reg1
# sort reg1
alpha
zeta
# sed s/alpha/ALPHA/ reg1
zeta
zeta
ALPHA
ALPHA
# find tarout -type d -print | sort
tarout
tarout/tarin
tarout/tarin/sub
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### GETPID

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="test $$ -gt 0 && echo pid: numeric\r"
mp135.custom:uart_expect sentinel="test $$ -gt 0 && echo pid: numeric\r\npid: numeric\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=getpid
```

Verify:

```
expected = """test $$ -gt 0 && echo pid: numeric
pid: numeric
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### DATE_CLOCK

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="date >/tmp/date.out\r"
mp135.custom:uart_expect sentinel="date >/tmp/date.out\r\n# " timeout_ms=10000
mp135.custom:uart_write data='awk '"'"'/^[A-Z][a-z][a-z] [A-Z][a-z][a-z] [ 0-9][0-9] [0-9][0-9]:[0-9][0-9]:[0-9][0-9] [A-Z][A-Z][A-Z] [0-9][0-9][0-9][0-9]$/ { print \"date: format\" }'"'"' /tmp/date.out\r'
mp135.custom:uart_expect sentinel='# awk '"'"'/^[A-Z][a-z][a-z] [A-Z][a-z][a-z] [ 0-9][0-9] [0-9][0-9]:[0-9][0-9]:[0-9][0-9] [A-Z][A-Z][A-Z] [0-9][0-9][0-9][0-9]$/ { print \"date: format\" }'"'"' /tmp/date.out\r\ndate: format\r\n# ' timeout_ms=10000
mp135.custom:uart_write data="rm /tmp/date.out\r"
mp135.custom:uart_expect sentinel="# rm /tmp/date.out\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=date_clock
```

Verify:

```
expected = """date >/tmp/date.out
# awk '/^[A-Z][a-z][a-z] [A-Z][a-z][a-z] [ 0-9][0-9] [0-9][0-9]:[0-9][0-9]:[0-9][0-9] [A-Z][A-Z][A-Z] [0-9][0-9][0-9][0-9]$/ { print "date: format" }' /tmp/date.out
date: format
# rm /tmp/date.out
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### UMASK_ROUNDTRIP

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="umask 077\r"
mp135.custom:uart_expect sentinel="umask 077\r\n# " timeout_ms=10000
mp135.custom:uart_write data="umask\r"
mp135.custom:uart_expect sentinel="# umask\r\n0077\r\n# " timeout_ms=10000
mp135.custom:uart_write data="umask 022\r"
mp135.custom:uart_expect sentinel="# umask 022\r\n# " timeout_ms=10000
mp135.custom:uart_write data="umask\r"
mp135.custom:uart_expect sentinel="# umask\r\n0022\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=umask_roundtrip
```

Verify:

```
expected = """umask 077
# umask
0077
# umask 022
# umask
0022
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### STAT_METADATA

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls -l /etc/passwd\r"
mp135.custom:uart_expect sentinel="/etc/passwd\r\n# " timeout_ms=10000
mp135.custom:uart_write data="ls -l /etc\r"
mp135.custom:uart_expect sentinel="utmp\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=stat_metadata
```

Verify:

```
expected = """ls -l /etc/passwd
-rw-r--r-- 1 root      141 Jan  1 00:00 /etc/passwd
# ls -l /etc
total 127
-rwxr-xr-x 1 root     4904 Dec 31 19:00 accton
-rwxr-xr-x 1 root    26768 Dec 31 19:00 atrun
-rwxr-xr-x 1 root    12192 Dec 31 19:00 cron
-rw-r--r-- 1 root        0 Dec 31 19:00 ddate
-rwxr-xr-x 1 root     5840 Dec 31 19:00 getty
-rw-r--r-- 1 root       49 Dec 31 19:00 group
-rwxr-xr-x 1 root     7364 Dec 31 19:00 init
-rw-r--r-- 1 root      141 Jan  1 00:00 passwd
-rwxr-xr-x 1 root      273 Dec 31 19:00 rc
-rw-r--r-- 1 root      266 Dec 31 19:00 ttys
-rwxr-xr-x 1 root     4200 Dec 31 19:00 update
-rw-r--r-- 1 root        0 Dec 31 19:00 utmp
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### CHMOD_METADATA

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="chmod 755 /etc/passwd\r"
mp135.custom:uart_expect sentinel="chmod 755 /etc/passwd\r\n# " timeout_ms=10000
mp135.custom:uart_write data="ls -l /etc/passwd\r"
mp135.custom:uart_expect sentinel="-rwxr-xr-x 1 root      141 " timeout_ms=10000
mp135.custom:uart_write data="chmod 644 /etc/passwd\r"
mp135.custom:uart_expect sentinel="# chmod 644 /etc/passwd\r\n# " timeout_ms=10000
mp135.custom:uart_write data="ls -l /etc/passwd\r"
mp135.custom:uart_expect sentinel="-rw-r--r-- 1 root      141 " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=chmod_metadata
```

Verify:

```
expected = """chmod 755 /etc/passwd
# ls -l /etc/passwd
-rwxr-xr-x 1 root      141 Jan  1 00:00 /etc/passwd
# chmod 644 /etc/passwd
# ls -l /etc/passwd
-rw-r--r-- 1 root      141 Jan  1 00:00 /etc/passwd
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### CHOWN_METADATA

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="chown 1 /etc/passwd\r"
mp135.custom:uart_expect sentinel="chown 1 /etc/passwd\r\n# " timeout_ms=10000
mp135.custom:uart_write data="ls -l /etc/passwd\r"
mp135.custom:uart_expect sentinel="-rw-r--r-- 1 daemon    141 " timeout_ms=10000
mp135.custom:uart_write data="chown 0 /etc/passwd\r"
mp135.custom:uart_expect sentinel="# chown 0 /etc/passwd\r\n# " timeout_ms=10000
mp135.custom:uart_write data="ls -l /etc/passwd\r"
mp135.custom:uart_expect sentinel="-rw-r--r-- 1 root      141 " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=chown_metadata
```

Verify:

```
expected = """chown 1 /etc/passwd
# ls -l /etc/passwd
-rw-r--r-- 1 daemon    141 Jan  1 00:00 /etc/passwd
# chown 0 /etc/passwd
# ls -l /etc/passwd
-rw-r--r-- 1 root      141 Jan  1 00:00 /etc/passwd
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### HARD_LINK_METADATA

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="date 7001010001 >/dev/null\r"
mp135.custom:uart_expect sentinel="date 7001010001 >/dev/null\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo hi > /tmp/link_x\r"
mp135.custom:uart_expect sentinel="echo hi > /tmp/link_x\r\n# " timeout_ms=10000
mp135.custom:uart_write data="ln /tmp/link_x /tmp/link_y\r"
mp135.custom:uart_expect sentinel="# ln /tmp/link_x /tmp/link_y\r\n# " timeout_ms=10000
mp135.custom:uart_write data="ls -l /tmp/link_x /tmp/link_y\r"
mp135.custom:uart_expect sentinel="-rw-r--r-- 2 root        3 " timeout_ms=10000
delay ms=100
mp135.custom:uart_write data="rm /tmp/link_x\r"
mp135.custom:uart_expect sentinel="# rm /tmp/link_x\r\n# " timeout_ms=10000
mp135.custom:uart_write data="ls -l /tmp/link_y\r"
mp135.custom:uart_expect sentinel="-rw-r--r-- 1 root        3 " timeout_ms=10000
delay ms=100
mp135.custom:uart_write data="rm /tmp/link_y\r"
mp135.custom:uart_expect sentinel="# rm /tmp/link_y\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=hard_link_metadata
```

Verify:

```
expected = """date 7001010001 >/dev/null
# echo hi > /tmp/link_x
# ln /tmp/link_x /tmp/link_y
# ls -l /tmp/link_x /tmp/link_y
-rw-r--r-- 2 root        3 Jan  1 00:01 /tmp/link_x
-rw-r--r-- 2 root        3 Jan  1 00:01 /tmp/link_y
# rm /tmp/link_x
# ls -l /tmp/link_y
-rw-r--r-- 1 root        3 Jan  1 00:01 /tmp/link_y
# rm /tmp/link_y
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### CHDIR_PWD_PATHS

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="cd /etc\r"
mp135.custom:uart_expect sentinel="cd /etc\r\n# " timeout_ms=10000
mp135.custom:uart_write data="pwd\r"
mp135.custom:uart_expect sentinel="# pwd\r\n/etc\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cd /\r"
mp135.custom:uart_expect sentinel="# cd /\r\n# " timeout_ms=10000
mp135.custom:uart_write data="pwd\r"
mp135.custom:uart_expect sentinel="# pwd\r\n/\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=chdir_pwd_paths
```

Verify:

```
expected = """cd /etc
# pwd
/etc
# cd /
# pwd
/
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### MKNOD_CHAR_DEVICE

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="date 7001010001 >/dev/null\r"
mp135.custom:uart_expect sentinel="date 7001010001 >/dev/null\r\n# " timeout_ms=10000
mp135.custom:uart_write data="mknod /tmp/cdev c 1 2\r"
mp135.custom:uart_expect sentinel="mknod /tmp/cdev c 1 2\r\n# " timeout_ms=10000
mp135.custom:uart_write data="ls -l /tmp/cdev\r"
mp135.custom:uart_expect sentinel="crw-r--r-- 1 root    1,  2 " timeout_ms=10000
mp135.custom:uart_write data="rm /tmp/cdev\r"
mp135.custom:uart_expect sentinel="# rm /tmp/cdev\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=mknod_char_device
```

Verify:

```
expected = """date 7001010001 >/dev/null
# mknod /tmp/cdev c 1 2
# ls -l /tmp/cdev
crw-r--r-- 1 root    1,  2 Jan  1 00:01 /tmp/cdev
# rm /tmp/cdev
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### TEST_FILE_OPERATOR

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="test -e /etc/passwd && echo exists\r"
mp135.custom:uart_expect sentinel="test -e /etc/passwd && echo exists\r\ntest: argument expected\r\n# " timeout_ms=10000
mp135.custom:uart_write data="test -e /no/such/file && echo wrong || echo absent\r"
mp135.custom:uart_expect sentinel="# test -e /no/such/file && echo wrong || echo absent\r\ntest: argument expected\r\nabsent\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=test_file_operator
```

Verify:

```
expected = """test -e /etc/passwd && echo exists
test: argument expected
# test -e /no/such/file && echo wrong || echo absent
test: argument expected
absent
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### EDITORS

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="(echo a; echo hello; echo .; echo p; echo 'w /tmp/edtest'; echo q) | ed -\r"
mp135.custom:uart_expect sentinel="(echo a; echo hello; echo .; echo p; echo 'w /tmp/edtest'; echo q) | ed -\r\nhello\r\n# " timeout_ms=10000
mp135.custom:uart_write data="cat /tmp/edtest\r"
mp135.custom:uart_expect sentinel="# cat /tmp/edtest\r\nhello\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=editors
```

Verify:

```
expected = """(echo a; echo hello; echo .; echo p; echo 'w /tmp/edtest'; echo q) | ed -
hello
# cat /tmp/edtest
hello
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### CALC

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls /bin/dc /bin/bc 2>&1\r"
mp135.custom:uart_expect sentinel="ls /bin/dc /bin/bc 2>&1\r\n/bin/bc not found\r\n/bin/dc\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo '3 4 + p' | dc 2>&1\r"
mp135.custom:uart_expect sentinel="# echo '3 4 + p' | dc 2>&1\r\n7\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo '5 3 - 7 * p' | dc 2>&1\r"
mp135.custom:uart_expect sentinel="# echo '5 3 - 7 * p' | dc 2>&1\r\n14\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=calc
```

Verify:

```
expected = """ls /bin/dc /bin/bc 2>&1
/bin/bc not found
/bin/dc
# echo '3 4 + p' | dc 2>&1
7
# echo '5 3 - 7 * p' | dc 2>&1
14
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### TEXT_TOOLS

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls /bin/diff /bin/diff3 /bin/ptx /bin/vpr 2>&1\r"
mp135.custom:uart_expect sentinel="ls /bin/diff /bin/diff3 /bin/ptx /bin/vpr 2>&1\r\n/bin/diff\r\n/bin/diff3\r\n/bin/ptx\r\n/bin/vpr\r\n# " timeout_ms=10000
mp135.custom:uart_write data='echo \"main(){int x;x=1;}\" | cb\r'
mp135.custom:uart_expect sentinel='# echo \"main(){int x;x=1;}\" | cb\r\nmain(){\r\n\tint x;\r\n\tx=1;\r\n}\r\n# ' timeout_ms=10000
mp135.custom:uart_write data='echo \"a b\" > /tmp/ts; echo \"b c\" >> /tmp/ts; echo \"c d\" >> /tmp/ts; tsort /tmp/ts\r'
mp135.custom:uart_expect sentinel='# echo \"a b\" > /tmp/ts; echo \"b c\" >> /tmp/ts; echo \"c d\" >> /tmp/ts; tsort /tmp/ts\r\na\r\nb\r\nc\r\nd\r\n# ' timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=text_tools
```

Verify:

```
expected = """ls /bin/diff /bin/diff3 /bin/ptx /bin/vpr 2>&1
/bin/diff
/bin/diff3
/bin/ptx
/bin/vpr
# echo "main(){int x;x=1;}" | cb
main(){
	int x;
	x=1;
}
# echo "a b" > /tmp/ts; echo "b c" >> /tmp/ts; echo "c d" >> /tmp/ts; tsort /tmp/ts
a
b
c
d
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### FILE_TOOLS

Test (max 20 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls /bin/tar /bin/tp /bin/dump 2>&1\r"
mp135.custom:uart_expect sentinel="ls /bin/tar /bin/tp /bin/dump 2>&1\r\n/bin/dump\r\n/bin/tar\r\n/bin/tp\r\n# " timeout_ms=10000
mp135.custom:uart_write data="find / -name passwd -print 2>&1\r"
mp135.custom:uart_expect sentinel="# find / -name passwd -print 2>&1\r\n/bin/passwd\r\n/etc/passwd\r\n# " timeout_ms=10000
mp135.custom:uart_write data="calendar >/tmp/calendar.out && echo calendar: regex\r"
mp135.custom:uart_expect sentinel="# calendar >/tmp/calendar.out && echo calendar: regex\r\ncalendar: regex\r\n# " timeout_ms=10000
mp135.custom:uart_write data="rm /tmp/calendar.out\r"
mp135.custom:uart_expect sentinel="# rm /tmp/calendar.out\r\n# " timeout_ms=10000
mp135.custom:uart_write data="quot /dev/null 2>&1; echo done\r"
mp135.custom:uart_expect sentinel="# quot /dev/null 2>&1; echo done\r\n/dev/null:\r\nread error 1\r\ndone\r\n# " timeout_ms=10000
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="# echo __TEST_DONE__\r\n__TEST_DONE__\r\n# " timeout_ms=10000
mp135.custom:uart_close
mark tag=file_tools
```

Verify:

```
expected = """ls /bin/tar /bin/tp /bin/dump 2>&1
/bin/dump
/bin/tar
/bin/tp
# find / -name passwd -print 2>&1
/bin/passwd
/etc/passwd
# calendar >/tmp/calendar.out && echo calendar: regex
calendar: regex
# rm /tmp/calendar.out
# quot /dev/null 2>&1; echo done
/dev/null:
read error 1
done
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```
