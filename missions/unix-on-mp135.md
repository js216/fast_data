### Build the kernel + SD image

Build:

```
make -C unix-v7-c99 BOARD=mp135 boot/unix boot/rootfs.img
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
printf '%s\n' 'description "reset custom DUT"' 'bench_mcu:reset_dut2' > "$RUNPY_WORKDIR/reset.plan"
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
delay ms=2000
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
printf '%s\n' 'description "reset custom DUT"' 'bench_mcu:reset_dut2' > "$RUNPY_WORKDIR/reset.plan"
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
mp135.custom:uart_write data="ls /bin | wc -l ; cat /etc/passwd ; echo MP135_UNI''X_OK\r"
mp135.custom:uart_expect sentinel="MP135_UNIX_OK" timeout_ms=10000
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
    # Reaching the final sentinel means the shell processed every prior command
    # and stayed responsive: the "ls /bin | wc -l" pipe exercises fork + two
    # execs off the SD + a pipe; "cat /etc/passwd" reads a file from the SD;
    # and the echo proves the shell itself ran (the empty-string concatenation
    # means the literal MP135_UNIX_OK appears only as output, not echoed input).
    # root's entry in /etc/passwd confirms cat actually read the file.
    return 'MP135_UNIX_OK' in uart and 'root:' in uart
```

### LS

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls /\r"
mp135.custom:uart_write data="ls /etc\r"
mp135.custom:uart_write data="ls /tmp\r"
mp135.custom:uart_write data="ls /usr\r"
mp135.custom:uart_write data="ls /usr/lib\r"
mp135.custom:uart_write data="ls /usr/dict\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls /etc/update\r"
mp135.custom:uart_write data="/etc/update\r"
mp135.custom:uart_write data="echo UPDATE_STATUS:$?\r"
mp135.custom:uart_write data="echo POST_UPDATE_OK\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls /bin/at /etc/atrun\r"
mp135.custom:uart_write data="date 7001010000 >/tmp/date.set 2>&1\r"
mp135.custom:uart_write data="echo DATE_STATUS:$?\r"
mp135.custom:uart_write data="echo \"echo AT_STDIN >/tmp/at.stdin\" >/tmp/at.in\r"
mp135.custom:uart_write data="at 0001 /tmp/at.in\r"
mp135.custom:uart_write data="cat /usr/spool/at/70.000.0001.*\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls /etc/cron /usr/lib/crontab\r"
mp135.custom:uart_write data="rm -f /tmp/cron.mark\r"
mp135.custom:uart_write data="echo '* * * * * echo CRON_OK >> /tmp/cron.mark' >/usr/lib/crontab\r"
mp135.custom:uart_write data="/etc/cron\r"
mp135.custom:uart_write data="echo CRON_STATUS:$?\r"
mp135.custom:uart_write data="for i in 1 2 3 4 5 6 7 8 9 10 11 12; do sleep 1; test -r /tmp/cron.mark && cat /tmp/cron.mark && break; done\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="grep '^dmr:' /etc/passwd\r"
mp135.custom:uart_write data="/bin/passwd dmr\r"
mp135.custom:uart_write data="abc123\r"
mp135.custom:uart_write data="abc123\r"
mp135.custom:uart_write data="echo PASSWD_STATUS:$?\r"
mp135.custom:uart_write data="grep '^dmr::' /etc/passwd\r"
mp135.custom:uart_write data="echo EMPTY_PASSWORD_STATUS:$?\r"
mp135.custom:uart_write data="awk -F: '/^dmr:/ { if ($2 != \"\" && $2 != \"abc123\") print \"dmr-password-field-ok\" }' /etc/passwd\r"
mp135.custom:uart_write data="grep abc123 /etc/passwd\r"
mp135.custom:uart_write data="echo PLAINTEXT_STATUS:$?\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### DMESG

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls /bin/dmesg\r"
mp135.custom:uart_write data="dmesg >/tmp/dmesg.out\r"
mp135.custom:uart_write data="echo DMESG_STATUS:$?\r"
mp135.custom:uart_write data="test -s /tmp/dmesg.out\r"
mp135.custom:uart_write data="echo DMESG_NONEMPTY:$?\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="rm -r dut\r"
mp135.custom:uart_write data="mkdir dut\r"
mp135.custom:uart_write data="mkdir dut/sub\r"
mp135.custom:uart_write data="/bin/echo alpha >dut/a\r"
mp135.custom:uart_write data="/bin/echo beta >dut/sub/b\r"
mp135.custom:uart_write data="ln dut/a dut/alink\r"
mp135.custom:uart_write data="du dut\r"
mp135.custom:uart_write data="du -a dut\r"
mp135.custom:uart_write data="du -s dut\r"
mp135.custom:uart_write data="cd dut\r"
mp135.custom:uart_write data="du -a a alink\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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
2       dut/sub
4       dut
# du -a dut
1       dut/sub/b
2       dut/sub
1       dut/a
4       dut
# du -s dut
4       dut
# cd dut
# du -a a alink
1       a
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### CONSOLE_SINGLE_USER_PATH

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="who am i\r"
mp135.custom:uart_write data="tty\r"
mp135.custom:uart_write data="cat /etc/ttys\r"
mp135.custom:uart_write data="echo getty-login-path-ok\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="/bin/echo 'a 1' >j1\r"
mp135.custom:uart_write data="/bin/echo 'b 2' >>j1\r"
mp135.custom:uart_write data="/bin/echo 'c 3' >>j1\r"
mp135.custom:uart_write data="/bin/echo 'a A' >j2\r"
mp135.custom:uart_write data="/bin/echo 'b B' >>j2\r"
mp135.custom:uart_write data="/bin/echo 'd D' >>j2\r"
mp135.custom:uart_write data="/bin/join j1 j2\r"
mp135.custom:uart_write data="/bin/join -a1 j1 j2\r"
mp135.custom:uart_write data="/bin/join -a2 j1 j2\r"
mp135.custom:uart_write data="/bin/join -a1 -e EMPTY -o 1.1 1.2 2.2 j1 j2\r"
mp135.custom:uart_write data="/bin/echo 'a:1' >jt1\r"
mp135.custom:uart_write data="/bin/echo 'b:2' >>jt1\r"
mp135.custom:uart_write data="/bin/echo 'a:A' >jt2\r"
mp135.custom:uart_write data="/bin/echo 'b:B' >>jt2\r"
mp135.custom:uart_write data="/bin/join -t: jt1 jt2\r"
mp135.custom:uart_write data="cat j1 | /bin/join - j2\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="/bin/kill\r"
mp135.custom:uart_write data="echo KILL_USAGE_STATUS:$?\r"
mp135.custom:uart_write data="/bin/kill xyz\r"
mp135.custom:uart_write data="echo KILL_XYZ_STATUS:$?\r"
mp135.custom:uart_write data="/bin/kill 99999\r"
mp135.custom:uart_write data="echo KILL_NOPROC_STATUS:$?\r"
mp135.custom:uart_write data="/bin/kill -9 99999\r"
mp135.custom:uart_write data="echo KILL_SIG9_STATUS:$?\r"
mp135.custom:uart_write data="/bin/kill -0 1\r"
mp135.custom:uart_write data="echo KILL_ZERO_STATUS:$?\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="rm -f a b x dlink\r"
mp135.custom:uart_write data="rm -r d\r"
mp135.custom:uart_write data="mkdir d\r"
mp135.custom:uart_write data="echo data >a\r"
mp135.custom:uart_write data="ln a b\r"
mp135.custom:uart_write data="cmp a b\r"
mp135.custom:uart_write data="echo CMP_STATUS:$?\r"
mp135.custom:uart_write data="ln a d\r"
mp135.custom:uart_write data="cmp a d/a\r"
mp135.custom:uart_write data="echo DIR_LINK_STATUS:$?\r"
mp135.custom:uart_write data="ln missing x\r"
mp135.custom:uart_write data="echo MISSING_STATUS:$?\r"
mp135.custom:uart_write data="ln d dlink\r"
mp135.custom:uart_write data="echo DIR_STATUS:$?\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="rm -r mbase\r"
mp135.custom:uart_write data="rm -r mdup\r"
mp135.custom:uart_write data="mkdir mbase\r"
mp135.custom:uart_write data="mkdir mbase/child\r"
mp135.custom:uart_write data="echo NESTED_STATUS:$?\r"
mp135.custom:uart_write data="mkdir missing/child\r"
mp135.custom:uart_write data="echo MISSING_PARENT_STATUS:$?\r"
mp135.custom:uart_write data="mkdir mdup\r"
mp135.custom:uart_write data="echo FIRST_DUP_STATUS:$?\r"
mp135.custom:uart_write data="mkdir mdup\r"
mp135.custom:uart_write data="echo DUP_STATUS:$?\r"
mp135.custom:uart_write data="rmdir mbase/child\r"
mp135.custom:uart_write data="rmdir mbase\r"
mp135.custom:uart_write data="rmdir mdup\r"
mp135.custom:uart_write data="echo CLEANUP_STATUS:$?\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="/bin/echo a >/tmp/base\r"
mp135.custom:uart_write data="/bin/echo b >>/tmp/base\r"
mp135.custom:uart_write data="/bin/echo c >>/tmp/base\r"
mp135.custom:uart_write data="/bin/echo a >/tmp/left\r"
mp135.custom:uart_write data="/bin/echo B-left >>/tmp/left\r"
mp135.custom:uart_write data="/bin/echo c >>/tmp/left\r"
mp135.custom:uart_write data="/bin/echo a >/tmp/right\r"
mp135.custom:uart_write data="/bin/echo B-right >>/tmp/right\r"
mp135.custom:uart_write data="/bin/echo c >>/tmp/right\r"
mp135.custom:uart_write data="diff /tmp/left /tmp/base >/tmp/d13\r"
mp135.custom:uart_write data="diff /tmp/right /tmp/base >/tmp/d23\r"
mp135.custom:uart_write data="diff3 /tmp/d13 /tmp/d23 /tmp/left /tmp/right /tmp/base\r"
mp135.custom:uart_write data="diff3 -e /tmp/d13 /tmp/d23 /tmp/left /tmp/right /tmp/base\r"
mp135.custom:uart_write data="echo DIFF3_E_STATUS:$?\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="cmp /etc/passwd /etc/passwd\r"
mp135.custom:uart_write data="diff /etc/passwd /etc/passwd\r"
mp135.custom:uart_write data="echo \"a 1\" > /tmp/j1\r"
mp135.custom:uart_write data="echo \"a x\" > /tmp/j2\r"
mp135.custom:uart_write data="join /tmp/j1 /tmp/j2\r"
mp135.custom:uart_write data="echo \"a b\" | tsort\r"
mp135.custom:uart_write data="rm /tmp/j1 /tmp/j2\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="test -f /etc/passwd\r"
mp135.custom:uart_write data="echo $?\r"
mp135.custom:uart_write data="test -d /etc\r"
mp135.custom:uart_write data="echo $?\r"
mp135.custom:uart_write data="test -f /nonexistent\r"
mp135.custom:uart_write data="echo $?\r"
mp135.custom:uart_write data="test -r /etc/passwd\r"
mp135.custom:uart_write data="echo $?\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
mp135.custom:uart_close
mark tag=test
```

Verify:

```
expected = """test -f /etc/passwd
# echo $?
0
# test -d /etc
# echo $?
0
# test -f /nonexistent
# echo $?
1
# test -r /etc/passwd
# echo $?
0
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### FOR

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="for i in 1 2 3\r"
mp135.custom:uart_write data="do\r"
mp135.custom:uart_write data="echo loop $i\r"
mp135.custom:uart_write data="done\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="case foo in\r"
mp135.custom:uart_write data="foo) echo matched;;\r"
mp135.custom:uart_write data="bar) echo bar;;\r"
mp135.custom:uart_write data="esac\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="if test -f /etc/passwd\r"
mp135.custom:uart_write data="then\r"
mp135.custom:uart_write data="echo passwd_exists\r"
mp135.custom:uart_write data="fi\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls /etc/p*\r"
mp135.custom:uart_write data="ls /b??\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="cal 1 1970\r"
mp135.custom:uart_write data="cal 12 1969\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="pwd\r"
mp135.custom:uart_write data="cd /tmp\r"
mp135.custom:uart_write data="pwd\r"
mp135.custom:uart_write data="cd /etc\r"
mp135.custom:uart_write data="pwd\r"
mp135.custom:uart_write data="cd /\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="echo abcde | rev\r"
mp135.custom:uart_write data="echo ABC | tr A-Z a-z\r"
mp135.custom:uart_write data="echo aaa | uniq\r"
mp135.custom:uart_write data="echo abc | sum\r"
mp135.custom:uart_write data="echo abc | od -c\r"
mp135.custom:uart_write data="sed 2q /etc/passwd\r"
mp135.custom:uart_write data="tail /etc/passwd\r"
mp135.custom:uart_write data="grep root /etc/passwd\r"
mp135.custom:uart_write data="fgrep root /etc/passwd\r"
mp135.custom:uart_write data="sort /etc/passwd\r"
mp135.custom:uart_write data="look ro /usr/dict/words\r"
mp135.custom:uart_write data="echo abc | tee /tmp/teeout\r"
mp135.custom:uart_write data="cat /tmp/teeout\r"
mp135.custom:uart_write data="rm /tmp/teeout\r"
mp135.custom:uart_write data="sed s/x/y/ /etc/passwd\r"
mp135.custom:uart_write data="echo x | sed s/x/y/\r"
mp135.custom:uart_write data="awk 1 /etc/passwd\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="test $$ -gt 0 && echo pid: numeric\r"
mp135.custom:uart_write data="echo $HOME\r"
mp135.custom:uart_write data="echo $PATH\r"
mp135.custom:uart_write data="echo $0\r"
mp135.custom:uart_write data="echo $?\r"
mp135.custom:uart_write data="sh -c 'echo $1 $2' x A B\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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
# echo $?
0
# sh -c 'echo $1 $2' x A B
A B
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### EXPAND

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="echo `echo backtick`\r"
mp135.custom:uart_write data="echo 'single quote'\r"
mp135.custom:uart_write data="echo \"double quote\"\r"
mp135.custom:uart_write data="expr 1 + 2\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ed /tmp/edtest << EOF\r"
mp135.custom:uart_write data="a\r"
mp135.custom:uart_write data="hello\r"
mp135.custom:uart_write data="world\r"
mp135.custom:uart_write data=".\r"
mp135.custom:uart_write data="w\r"
mp135.custom:uart_write data="q\r"
mp135.custom:uart_write data="EOF\r"
mp135.custom:uart_write data="cat /tmp/edtest\r"
mp135.custom:uart_write data="rm /tmp/edtest\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="find /usr/lib -print\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="df\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
mp135.custom:uart_close
mark tag=df
```

Verify:

```
expected = """df
/dev/root N
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### GREP

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="grep '^root' /etc/passwd\r"
mp135.custom:uart_write data="grep -v root /etc/passwd\r"
mp135.custom:uart_write data="grep -c sh /etc/passwd\r"
mp135.custom:uart_write data="grep -n sh /etc/passwd\r"
mp135.custom:uart_write data="grep '\\(o\\)\\1' /etc/passwd\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
mp135.custom:uart_close
mark tag=grep
```

Verify:

```
expected = """grep '^root' /etc/passwd
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
# grep '\\(o\\)\\1' /etc/passwd
root:VwL97VCAx1Qhs:0:1::/:
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### SED

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="sed s/x/y/ /etc/passwd\r"
mp135.custom:uart_write data="echo x | sed s/x/y/\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="echo edge > /tmp/END\r"
mp135.custom:uart_write data="echo start > /tmp/BEGIN\r"
mp135.custom:uart_write data="awk '{print $0}' /tmp/END\r"
mp135.custom:uart_write data="cd /tmp\r"
mp135.custom:uart_write data="awk '{print $0}' END\r"
mp135.custom:uart_write data="awk '{print $0}' BEGIN\r"
mp135.custom:uart_write data="awk 'BEGIN {print 7}'\r"
mp135.custom:uart_write data="awk 'END {print NR}' /etc/passwd\r"
mp135.custom:uart_write data="awk '{n=n+1} END {print n}' /etc/passwd\r"
mp135.custom:uart_write data="echo 'a b' | awk '{print $2}'\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="mkdir /tmp/cpdir\r"
mp135.custom:uart_write data="echo srcA > /tmp/A\r"
mp135.custom:uart_write data="echo srcB > /tmp/B\r"
mp135.custom:uart_write data="cp /tmp/A /tmp/B /tmp/cpdir\r"
mp135.custom:uart_write data="cat /tmp/cpdir/A\r"
mp135.custom:uart_write data="cat /tmp/cpdir/B\r"
mp135.custom:uart_write data="cp /tmp/A /tmp/A\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="echo content > /tmp/mvsrc\r"
mp135.custom:uart_write data="mv /tmp/mvsrc /tmp/mvsrc\r"
mp135.custom:uart_write data="mkdir /tmp/mvA\r"
mp135.custom:uart_write data="mkdir /tmp/mvB\r"
mp135.custom:uart_write data="mkdir /tmp/mvA/sub\r"
mp135.custom:uart_write data="echo data > /tmp/mvA/sub/file\r"
mp135.custom:uart_write data="mv /tmp/mvA/sub /tmp/mvB/sub\r"
mp135.custom:uart_write data="cat /tmp/mvB/sub/file\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="touch /tmp/tnew\r"
mp135.custom:uart_write data="ls /tmp/tnew\r"
mp135.custom:uart_write data="echo old > /tmp/told\r"
mp135.custom:uart_write data="touch /tmp/told\r"
mp135.custom:uart_write data="cat /tmp/told\r"
mp135.custom:uart_write data="touch -c /tmp/tabsent\r"
mp135.custom:uart_write data="ls /tmp/tabsent\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="echo abcdef | tr -d def\r"
mp135.custom:uart_write data="echo aaabbb | tr -s ab AB\r"
mp135.custom:uart_write data="echo Hello123 | tr -cd 0-9\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="echo line1 > /tmp/spi\r"
mp135.custom:uart_write data="echo line2 >> /tmp/spi\r"
mp135.custom:uart_write data="echo line3 >> /tmp/spi\r"
mp135.custom:uart_write data="split -1 /tmp/spi /tmp/x\r"
mp135.custom:uart_write data="cat /tmp/xaa\r"
mp135.custom:uart_write data="cat /tmp/xab\r"
mp135.custom:uart_write data="cat /tmp/xac\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="echo a b > /tmp/ts\r"
mp135.custom:uart_write data="echo b c >> /tmp/ts\r"
mp135.custom:uart_write data="tsort /tmp/ts\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="write\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="comm /etc/passwd /etc/passwd\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="echo hello | crypt key | crypt key\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="time\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls /bin/osh\r"
mp135.custom:uart_write data="osh -c \"echo OSH_OK\"\r"
mp135.custom:uart_write data="echo hi | osh -c \"cat\"\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls /usr/lib/units\r"
mp135.custom:uart_write data="units <<EOF\r"
mp135.custom:uart_write data="foot\r"
mp135.custom:uart_write data="inch\r"
mp135.custom:uart_write data="EOF\r"
mp135.custom:uart_write data="units <<EOF\r"
mp135.custom:uart_write data="mile\r"
mp135.custom:uart_write data="foot\r"
mp135.custom:uart_write data="EOF\r"
mp135.custom:uart_write data="units <<EOF\r"
mp135.custom:uart_write data="hour\r"
mp135.custom:uart_write data="minute\r"
mp135.custom:uart_write data="EOF\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
mp135.custom:uart_close
mark tag=units
```

Verify:

```
expected = """ls /usr/lib/units
/usr/lib/units
# units <<EOF
> foot
> inch
> EOF
437 units; 3191 bytes

you have: you want:     * 1.200000e+01
        / 8.333333e-02
you have:
# units <<EOF
> mile
> foot
> EOF
437 units; 3191 bytes

you have: you want:     * 5.280000e+03
        / 1.893939e-04
you have:
# units <<EOF
> hour
> minute
> EOF
437 units; 3191 bytes

you have: you want:     * 6.000000e+01
        / 1.666667e-02
you have:
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### MKNOD

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="mknod\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="newgrp\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="clri\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="echo hello | checkeq\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="mount\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="umount\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="dcheck /dev/root\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="icheck /dev/root\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
mp135.custom:uart_close
mark tag=icheck
```

Verify:

```
expected = """icheck /dev/root
/dev/root:
files    165 (r=145,d=14,b=1,c=5)
used   20662 (i=240,ii=115,iii=0,d=20192)
free   11962
missing    0
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### NCHECK

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ncheck /dev/root\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
mp135.custom:uart_close
mark tag=ncheck
```

Verify:

```
expected = """ncheck /dev/root
/dev/root:
3       /bin/.
116     /dev/.
123     /etc/.
136     /tmp/.
138     /usr/.
164     /unix
165     /.profile
4       /bin/1
5       /bin/[
6       /bin/ac
7       /bin/at
8       /bin/arcv
9       /bin/awk
10      /bin/basename
11      /bin/cal
12      /bin/calendar
13      /bin/cat
14      /bin/cb
15      /bin/checkeq
16      /bin/chgrp
17      /bin/chmod
18      /bin/chown
19      /bin/clri
20      /bin/cmp
21      /bin/col
22      /bin/comm
23      /bin/cp
24      /bin/crypt
25      /bin/date
26      /bin/dc
27      /bin/dcheck
28      /bin/dd
29      /bin/df
30      /bin/diff
31      /bin/diff3
32      /bin/deroff
33      /bin/dmesg
34      /bin/du
35      /bin/dump
36      /bin/dumpdir
37      /bin/echo
38      /bin/ed
39      /bin/egrep
40      /bin/expr
41      /bin/fgrep
42      /bin/file
43      /bin/factor
44      /bin/find
45      /bin/false
46      /bin/grep
47      /bin/graph
48      /bin/icheck
49      /bin/iostat
50      /bin/join
51      /bin/kill
52      /bin/ln
53      /bin/login
54      /bin/look
55      /bin/ls
56      /bin/mesg
57      /bin/mkdir
58      /bin/mknod
59      /bin/mount
60      /bin/mv
61      /bin/ncheck
62      /bin/newgrp
63      /bin/nice
64      /bin/nohup
65      /bin/od
66      /bin/osh
67      /bin/passwd
68      /bin/pr
69      /bin/primes
70      /bin/prof
71      /bin/ps
72      /bin/pstat
73      /bin/ptx
74      /bin/pwd
75      /bin/quot
76      /bin/random
77      /bin/restor
78      /bin/rev
79      /bin/rm
80      /bin/rmdir
81      /bin/sa
82      /bin/sed
83      /bin/sh
84      /bin/sleep
85      /bin/sort
86      /bin/sp
87      /bin/spline
88      /bin/split
89      /bin/stty
90      /bin/su
91      /bin/sum
92      /bin/sync
93      /bin/tabs
94      /bin/tail
95      /bin/tar
96      /bin/tc
97      /bin/tee
98      /bin/test
99      /bin/time
100     /bin/tk
101     /bin/touch
102     /bin/tp
103     /bin/tr
104     /bin/true
105     /bin/tsort
106     /bin/tty
107     /bin/umount
108     /bin/uniq
109     /bin/units
110     /bin/vpr
111     /bin/wall
112     /bin/wc
113     /bin/who
114     /bin/write
115     /bin/yes
117     /dev/console
118     /dev/mem
119     /dev/kmem
120     /dev/null
121     /dev/root
122     /dev/tty
124     /etc/accton
125     /etc/atrun
126     /etc/cron
127     /etc/ddate
128     /etc/getty
129     /etc/init
130     /etc/passwd
131     /etc/group
132     /etc/rc
133     /etc/ttys
134     /etc/update
135     /etc/utmp
137     /tmp/.keep
139     /usr/adm/.
142     /usr/dict/.
144     /usr/games/.
154     /usr/lib/.
159     /usr/spool/.
140     /usr/adm/acct
141     /usr/adm/wtmp
143     /usr/dict/words
145     /usr/games/arithmetic
146     /usr/games/backgammon
147     /usr/games/fish
148     /usr/games/fortune
149     /usr/games/hangman
150     /usr/games/lib/.
152     /usr/games/quiz
153     /usr/games/wump
151     /usr/games/lib/fortunes
155     /usr/lib/crontab
156     /usr/lib/diffh
157     /usr/lib/makekey
158     /usr/lib/units
160     /usr/spool/at/.
161     /usr/spool/at/lasttimedone
162     /usr/spool/at/past/.
163     /usr/spool/at/past/.keep
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### RANDOM

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="echo hi | random 0\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="stty\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
mp135.custom:uart_close
mark tag=stty
```

Verify:

```
expected = """stty
speed 0 baud
erase = '#'; kill = '@'
even odd -nl echo -tabs
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### SU

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="su nosuchuser\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="tabs\r"
mp135.custom:uart_write data="echo TABS_STATUS:$?\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="wall </dev/null\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="test $$ -gt 0 && echo top: numeric\r"
mp135.custom:uart_write data="sh -c 'test $$ -gt 0 && echo subshell: numeric'\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="echo data > /dev/null\r"
mp135.custom:uart_write data="echo write_rc=$?\r"
mp135.custom:uart_write data="wc /dev/null\r"
mp135.custom:uart_write data="cat /dev/null\r"
mp135.custom:uart_write data="echo cat_rc=$?\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="sh -c 'sleep 30 & pid=$!; kill -9 $pid; wait; echo done' 2>&1 | sed 's/[0-9][0-9]* Killed/PID Killed/'\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="yes alphabet | sed 3q\r"
mp135.custom:uart_write data="echo done\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="echo count=`yes x | sed 40000q | wc -l`\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="( sleep 1; echo A ) &\r"
mp135.custom:uart_write data="( sleep 2; echo B ) &\r"
mp135.custom:uart_write data="wait\r"
mp135.custom:uart_write data="echo done\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
mp135.custom:uart_close
mark tag=mt_wait_all_bg
```

Verify:

```
expected = """( sleep 1; echo A ) &
<pid>
# ( sleep 2; echo B ) &
<pid>
# A
wait
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="echo before >/tmp/before\r"
mp135.custom:uart_write data="( sleep 2; echo after >/tmp/after ) &\r"
mp135.custom:uart_write data="sleep 3\r"
mp135.custom:uart_write data="wait\r"
mp135.custom:uart_write data="cat /tmp/before /tmp/after\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
mp135.custom:uart_close
mark tag=mt_concurrent_sleep
```

Verify:

```
expected = """echo before >/tmp/before
# ( sleep 2; echo after >/tmp/after ) &
<pid>
# sleep 3
# wait
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls /etc | grep accton\r"
mp135.custom:uart_write data="ls /etc | grep update\r"
mp135.custom:uart_write data="ls /bin | grep passwd\r"
mp135.custom:uart_write data="ls /bin | grep diff3\r"
mp135.custom:uart_write data="ls /usr/games\r"
mp135.custom:uart_write data="diff3 /etc/passwd /etc/ttys /etc/group\r"
mp135.custom:uart_write data="ls /usr/games/lib\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls /bin/dc /bin/tar /bin/tp /bin/ptx /bin/spline /bin/vpr /bin/quot\r"
mp135.custom:uart_write data="ls /bin/dump /bin/dumpdir /bin/restor /bin/tk\r"
mp135.custom:uart_write data="ls /usr/games/backgammon /usr/games/fish /usr/games/quiz /usr/games/wump\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls /usr/games/hangman /usr/games/quiz /bin/spline /bin/tk\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ps | sed 2q\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
mp135.custom:uart_close
mark tag=ps
```

Verify:

```
expected = """ps | sed 2q
   PID TTY TIME CMD
     2 co  0:00 -
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### PSTAT

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="pstat -p | grep 'LOC S'\r"
mp135.custom:uart_write data="pstat -i | grep 'active inodes' | sed 's/^[0-9][0-9]*/N/' | sed 1q\r"
mp135.custom:uart_write data="pstat -f | grep 'open files' | sed 's/^[0-9][0-9]*/N/' | sed 1q\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="prof\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="tc < /dev/null | od -c\r"
mp135.custom:uart_write data="echo hello | tc | od -c\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
mp135.custom:uart_close
mark tag=tc
```

Verify:

```
expected = """tc < /dev/null | od -c
0000000 035   7   l 177       @ 033   ; 037  \\0
0000011
# echo hello | tc | od -c
0000000 035   8   l   o       @ 035   b   @ 035   7   d   y   @ 035   l
0000020   o   @ 035   g   @ 037   b 035 177   @ 033   ; 037  \\0
0000035
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### GRAPH

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls /bin/graph\r"
mp135.custom:uart_write data="/bin/echo \"0 0\" >/tmp/g\r"
mp135.custom:uart_write data="/bin/echo \"1 1\" >>/tmp/g\r"
mp135.custom:uart_write data="graph -g 0 -m 0 /tmp/g | od -c\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
mp135.custom:uart_close
mark tag=graph
```

Verify:

```
expected = """ls /bin/graph
/bin/graph
# /bin/echo "0 0" >/tmp/g
# /bin/echo "1 1" >>/tmp/g
# graph -g 0 -m 0 /tmp/g | od -c
0000000   s  \\0  \\0  \\0  \\0  \\0 020  \\0 020   e   m 310  \\0 214  \\0   p
0000020 310  \\0 310  \\0   p 240 017 240 017   f   s   o   l   i   d  \\n
0000040   m 001  \\0 001  \\0  \\0
0000045
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### TAR

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls /bin/tar\r"
mp135.custom:uart_write data="cd /tmp\r"
mp135.custom:uart_write data="rm -rf tarin tarout tappex arch.tar extra\r"
mp135.custom:uart_write data="mkdir tarin\r"
mp135.custom:uart_write data="mkdir tarin/sub\r"
mp135.custom:uart_write data="echo alpha > tarin/a\r"
mp135.custom:uart_write data="echo beta > tarin/sub/b\r"
mp135.custom:uart_write data="echo gamma > tarin/c\r"
mp135.custom:uart_write data="/bin/tar cf arch.tar tarin\r"
mp135.custom:uart_write data="/bin/tar tf arch.tar\r"
mp135.custom:uart_write data="mkdir tarout\r"
mp135.custom:uart_write data="cd tarout\r"
mp135.custom:uart_write data="/bin/tar xf ../arch.tar\r"
mp135.custom:uart_write data="cat tarin/a\r"
mp135.custom:uart_write data="cat tarin/sub/b\r"
mp135.custom:uart_write data="cat tarin/c\r"
mp135.custom:uart_write data="cd ..\r"
mp135.custom:uart_write data="find /tmp/tarout/tarin -type f -print\r"
mp135.custom:uart_write data="echo delta > extra\r"
mp135.custom:uart_write data="/bin/tar rf arch.tar extra\r"
mp135.custom:uart_write data="/bin/tar tf arch.tar\r"
mp135.custom:uart_write data="mkdir tappex\r"
mp135.custom:uart_write data="cd tappex\r"
mp135.custom:uart_write data="/bin/tar xf ../arch.tar extra\r"
mp135.custom:uart_write data="cat extra\r"
mp135.custom:uart_write data="cd ..\r"
mp135.custom:uart_write data="/bin/tar cf - tarin/a | od -c | sed 1q\r"
mp135.custom:uart_write data="echo zeta > reg1\r"
mp135.custom:uart_write data="echo alpha >> reg1\r"
mp135.custom:uart_write data="sort reg1\r"
mp135.custom:uart_write data="sed s/alpha/ALPHA/ reg1\r"
mp135.custom:uart_write data="find tarout -type d -print | sort\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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
# echo delta > extra
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
0000000   t   a   r   i   n   /   a  \\0  \\0  \\0  \\0  \\0  \\0  \\0  \\0  \\0
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="test $$ -gt 0 && echo pid: numeric\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="date >/tmp/date.out\r"
mp135.custom:uart_write data="awk '/^[A-Z][a-z][a-z] [A-Z][a-z][a-z] [ 0-9][0-9] [0-9][0-9]:[0-9][0-9]:[0-9][0-9] [A-Z][A-Z][A-Z] [0-9][0-9][0-9][0-9]$/ { print \"date: format\" }' /tmp/date.out\r"
mp135.custom:uart_write data="rm /tmp/date.out\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="umask 077\r"
mp135.custom:uart_write data="umask\r"
mp135.custom:uart_write data="umask 022\r"
mp135.custom:uart_write data="umask\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls -l /etc/passwd\r"
mp135.custom:uart_write data="ls -l /etc\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
mp135.custom:uart_close
mark tag=stat_metadata
```

Verify:

```
expected = """ls -l /etc/passwd
-rw-r--r-- 1 root      141 DATE /etc/passwd
# ls -l /etc
total N
-rwxr-xr-x 1 root SIZE DATE accton
-rwxr-xr-x 1 root SIZE DATE atrun
-rwxr-xr-x 1 root SIZE DATE cron
-rw-r--r-- 1 root        0 DATE ddate
-rwxr-xr-x 1 root SIZE DATE getty
-rw-r--r-- 1 root       49 DATE group
-rwxr-xr-x 1 root SIZE DATE init
-rw-r--r-- 1 root      141 DATE passwd
-rwxr-xr-x 1 root SIZE DATE rc
-rw-r--r-- 1 root      266 DATE ttys
-rwxr-xr-x 1 root SIZE DATE update
-rw-r--r-- 1 root        0 DATE utmp
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### CHMOD_METADATA

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="chmod 755 /etc/passwd\r"
mp135.custom:uart_write data="ls -l /etc/passwd\r"
mp135.custom:uart_write data="chmod 644 /etc/passwd\r"
mp135.custom:uart_write data="ls -l /etc/passwd\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
mp135.custom:uart_close
mark tag=chmod_metadata
```

Verify:

```
expected = """chmod 755 /etc/passwd
# ls -l /etc/passwd
-rwxr-xr-x 1 root      141 DATE /etc/passwd
# chmod 644 /etc/passwd
# ls -l /etc/passwd
-rw-r--r-- 1 root      141 DATE /etc/passwd
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### CHOWN_METADATA

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="chown 1 /etc/passwd\r"
mp135.custom:uart_write data="ls -l /etc/passwd\r"
mp135.custom:uart_write data="chown 0 /etc/passwd\r"
mp135.custom:uart_write data="ls -l /etc/passwd\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
mp135.custom:uart_close
mark tag=chown_metadata
```

Verify:

```
expected = """chown 1 /etc/passwd
# ls -l /etc/passwd
-rw-r--r-- 1 daemon    141 DATE /etc/passwd
# chown 0 /etc/passwd
# ls -l /etc/passwd
-rw-r--r-- 1 root      141 DATE /etc/passwd
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### HARD_LINK_METADATA

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="echo hi > /tmp/link_x\r"
mp135.custom:uart_write data="ln /tmp/link_x /tmp/link_y\r"
mp135.custom:uart_write data="ls -l /tmp/link_x /tmp/link_y\r"
mp135.custom:uart_write data="rm /tmp/link_x\r"
mp135.custom:uart_write data="ls -l /tmp/link_y\r"
mp135.custom:uart_write data="rm /tmp/link_y\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
mp135.custom:uart_close
mark tag=hard_link_metadata
```

Verify:

```
expected = """echo hi > /tmp/link_x
# ln /tmp/link_x /tmp/link_y
# ls -l /tmp/link_x /tmp/link_y
-rw-rw-rw- 2 root        3 DATE /tmp/link_x
-rw-rw-rw- 2 root        3 DATE /tmp/link_y
# rm /tmp/link_x
# ls -l /tmp/link_y
-rw-rw-rw- 1 root        3 DATE /tmp/link_y
# rm /tmp/link_y
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### CHDIR_PWD_PATHS

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="cd /etc\r"
mp135.custom:uart_write data="pwd\r"
mp135.custom:uart_write data="cd /\r"
mp135.custom:uart_write data="pwd\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="mknod /tmp/cdev c 1 2\r"
mp135.custom:uart_write data="ls -l /tmp/cdev\r"
mp135.custom:uart_write data="rm /tmp/cdev\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
mp135.custom:uart_close
mark tag=mknod_char_device
```

Verify:

```
expected = """mknod /tmp/cdev c 1 2
# ls -l /tmp/cdev
crw-rw-rw- 1 root    1,  2 DATE /tmp/cdev
# rm /tmp/cdev
# echo __TEST_DONE__
__TEST_DONE__
#"""

def check(extract_dir):
    return Verification.uart_golden(extract_dir, expected)
```

### TEST_FILE_OPERATOR

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="test -e /etc/passwd && echo exists\r"
mp135.custom:uart_write data="test -e /no/such/file && echo wrong || echo absent\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="(echo a; echo hello; echo .; echo p; echo 'w /tmp/edtest'; echo q) | ed -\r"
mp135.custom:uart_write data="cat /tmp/edtest\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls /bin/dc /bin/bc 2>&1\r"
mp135.custom:uart_write data="echo '3 4 + p' | dc 2>&1\r"
mp135.custom:uart_write data="echo '5 3 - 7 * p' | dc 2>&1\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls /bin/diff /bin/diff3 /bin/ptx /bin/vpr 2>&1\r"
mp135.custom:uart_write data="echo \"main(){int x;x=1;}\" | cb\r"
mp135.custom:uart_write data="echo \"a b\" > /tmp/ts; echo \"b c\" >> /tmp/ts; echo \"c d\" >> /tmp/ts; tsort /tmp/ts\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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

Test (max 10 s):

```
mp135.custom:uart_open
mp135.custom:uart_write data="ls /bin/tar /bin/tp /bin/dump 2>&1\r"
mp135.custom:uart_write data="find / -name passwd -print 2>&1\r"
mp135.custom:uart_write data="calendar >/tmp/calendar.out && echo calendar: regex\r"
mp135.custom:uart_write data="rm /tmp/calendar.out\r"
mp135.custom:uart_write data="quot /dev/null 2>&1; echo done\r"
mp135.custom:uart_write data="echo __TEST_DONE__\r"
mp135.custom:uart_expect sentinel="__TEST_DONE__\r\n# " timeout_ms=100
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
