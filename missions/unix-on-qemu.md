# Unix v7 on Qemu (Armv7-A)

### Build unix

Build:

```
make -C unix-v7-c99 ARCH=arm CONF=qemu_arm
```

### LS

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
ls /
ls /etc
ls /tmp
ls /usr
ls /usr/lib
ls /usr/dict
echo __TEST_DONE__
```

Expect:

```
ls /
bin
dev
etc
tmp
usr
# ls /etc
auxfs
getty
init
passwd
ttys
utmp
# ls /tmp
.keep
# ls /usr
dict
lib
# ls /usr/lib
diffh
makekey
# ls /usr/dict
words
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### MKDIR LN

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
mkdir /tmp/d
ls -la /tmp
rmdir /tmp/d
ln /etc/passwd /tmp/pwlink
ls -li /etc/passwd /tmp/pwlink
rm /tmp/pwlink
echo __TEST_DONE__
```

Expect:

```
mkdir /tmp/d
# ls -la /tmp
total 3
drwxrwxrwx 1 root       64 Jan  1 00:00 .
drwxr-xr-x 1 root      112 Jan  1 00:00 ..
-rw-r--r-- 1 root        0 Jan  1 00:00 .keep
drwxrwxr-x 1 root       32 Jan  1 00:00 d
# rmdir /tmp/d
# ln /etc/passwd /tmp/pwlink
# ls -li /etc/passwd /tmp/pwlink
   85 -rw-r--r-- 1 root       51 Jan  1 00:00 /etc/passwd
   85 -rw-r--r-- 1 root       51 Jan  1 00:00 /tmp/pwlink
# rm /tmp/pwlink
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### COMPARE

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
cmp /etc/passwd /etc/passwd
diff /etc/passwd /etc/passwd
echo "a 1" > /tmp/j1
echo "a x" > /tmp/j2
join /tmp/j1 /tmp/j2
echo "a b" | tsort
rm /tmp/j1 /tmp/j2
echo __TEST_DONE__
```

Expect:

```
cmp /etc/passwd /etc/passwd
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
# 
```

### TEST

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
test -f /etc/passwd
echo $?
test -d /etc
echo $?
test -f /nonexistent
echo $?
test -r /etc/passwd
echo $?
echo __TEST_DONE__
```

Expect:

```
test -f /etc/passwd
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
# 
```

### FOR

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
for i in 1 2 3
do
echo loop $i
done
echo __TEST_DONE__
```

Expect:

```
for i in 1 2 3
> do
> echo loop $i
> done
loop 1
loop 2
loop 3
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### CASE

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
case foo in
foo) echo matched;;
bar) echo bar;;
esac
echo __TEST_DONE__
```

Expect:

```
case foo in
> foo) echo matched;;
> bar) echo bar;;
> esac
matched
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### IF

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
if test -f /etc/passwd
then
echo passwd_exists
fi
echo __TEST_DONE__
```

Expect:

```
if test -f /etc/passwd
> then
> echo passwd_exists
> fi
passwd_exists
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### GLOB

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
ls /etc/p*
ls /b??
echo __TEST_DONE__
```

Expect:

```
ls /etc/p*
/etc/passwd
# ls /b??
[
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
dcheck
dd
df
diff
du
echo
ed
fgrep
file
find
grep
icheck
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
od
pr
pwd
random
rev
rm
rmdir
sh
sleep
sort
sp
split
stty
su
sum
sync
tabs
tail
tee
test
time
touch
tr
tsort
tty
umount
uniq
wall
wc
who
write
yes
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### CAL

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
cal 1 1970
cal 12 1969
echo __TEST_DONE__
```

Expect:

```
cal 1 1970
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
# 
```

## WIP

### CD

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
pwd
cd /tmp
pwd
cd /etc
pwd
cd /
echo __TEST_DONE__
```

Expect:

```
pwd
/
# cd /tmp
# pwd
/
# cd /etc
# pwd
/
# cd /
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### FILES

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
echo data > /tmp/a
ls -l /tmp/a
cat /tmp/a
wc /tmp/a
cp /tmp/a /tmp/b
ls /tmp/a /tmp/b
mv /tmp/b /tmp/c
ls /tmp/c
chmod 644 /tmp/c
ls -l /tmp/c
chown root /tmp/c
chgrp 0 /tmp/c
file /tmp/a
du /tmp/a
sum /tmp/a
basename /usr/lib/diffh
rm /tmp/a /tmp/c
echo __TEST_DONE__
```

Expect:

```
echo data > /tmp/a
# ls -l /tmp/a
-rw-rw-r-- 1 root        5 Jan  1 00:00 /tmp/a
# cat /tmp/a
data
# wc /tmp/a
      1      1       5 /tmp/a
# cp /tmp/a /tmp/b
# ls /tmp/a /tmp/b
/tmp/a
/tmp/b
# mv /tmp/b /tmp/c
# ls /tmp/c
/tmp/c
# chmod 644 /tmp/c
# ls -l /tmp/c
-rw-r--r-- 1 root        5 Jan  1 00:00 /tmp/c
# chown root /tmp/c
# chgrp 0 /tmp/c
# file /tmp/a
/tmp/a:	fortran program text
# du /tmp/a
--bad status < /tmp >
# sum /tmp/a
57449     1
# basename /usr/lib/diffh
diffh
# rm /tmp/a /tmp/c
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### TEXT

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
echo abcde | rev
echo ABC | tr A-Z a-z
echo aaa | uniq
echo abc | sum
echo abc | od -c
head /etc/passwd
tail /etc/passwd
grep root /etc/passwd
fgrep root /etc/passwd
sort /etc/passwd
look ro /usr/dict/words
echo abc | tee /tmp/teeout
cat /tmp/teeout
rm /tmp/teeout
sed s/x/y/ /etc/passwd
awk 1 /etc/passwd
echo __TEST_DONE__
```

Expect:

```
echo abcde | rev
edcba
# echo ABC | tr A-Z a-z
abc
# echo aaa | uniq
aaa
# echo abc | sum
08288     1
# echo abc | od -c
0000000   a   b   c  \n
0000004
# head /etc/passwd
head: cannot execute
# tail /etc/passwd
root::0:0:root:/:/bin/sh
dmr::1:1:dennis:/:/bin/sh
# grep root /etc/passwd
root::0:0:root:/:/bin/sh
# fgrep root /etc/passwd
root::0:0:root:/:/bin/sh
# sort /etc/passwd
dmr::1:1:dennis:/:/bin/sh
root::0:0:root:/:/bin/sh
# look ro /usr/dict/words
# echo abc | tee /tmp/teeout
abc
# cat /tmp/teeout
abc
# rm /tmp/teeout
# sed s/x/y/ /etc/passwd
sed: cannot execute
# awk 1 /etc/passwd
awk: cannot execute
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### META

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
ls -i /etc/passwd
ls -l /
tty
who
id
mesg
echo __TEST_DONE__
```

Expect:

```
ls -i /etc/passwd
   85 /etc/passwd
# ls -l /
total 7
drwxr-xr-x 1 root     1232 Jan  1 00:00 bin
drwxr-xr-x 1 root       48 Jan  1 00:00 dev
drwxr-xr-x 1 root      128 Jan  1 00:00 etc
drwxrwxrwx 1 root       48 Jan  1 00:00 tmp
drwxr-xr-x 1 root       64 Jan  1 00:00 usr
# tty
not a tty
# who
# id
id: cannot execute
# mesg
is n
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### CONVERT

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
echo "hello world more" | sp
echo "main(){i=0;}" | cb
echo abc | dd count=1
echo hi | col
echo abc | pr
echo __TEST_DONE__
```

Expect:

```
echo "hello world more" | sp
hello world more
# echo "main(){i=0;}" | cb
main(){
	i=0;
}
# echo abc | dd count=1
abc
0+1 records in
0+1 records out
# echo hi | col
hi
# echo abc | pr


Jan  1 00:00 1970   Page 1


abc




























































# echo __TEST_DONE__
__TEST_DONE__
# 
```

### PROC

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
sleep 1 &
echo $!
wait
nice echo niced
sync
sleep 100 &
echo $!
kill $!
wait
ps
env
true
false
echo __TEST_DONE__
```

Expect:

```
sleep 1 &
5
# echo $!
5
# wait
# nice echo niced
niced
# sync
# sleep 100 &
9
# echo $!
9
# kill $!
9: Error 0
# wait
# ps
ps: cannot execute
# env
env: cannot execute
# true
true: cannot execute
# false
false: cannot execute
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### VARS

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
echo $$
echo $HOME
echo $PATH
echo $0
echo $?
sh -c 'echo $1 $2' x A B
echo __TEST_DONE__
```

Expect:

```
echo $$
1
# echo $HOME

# echo $PATH

# echo $0
-sh
# echo $?
0
# sh -c 'echo $1 $2' x A B
# 
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### EXPAND

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
echo `echo backtick`
echo 'single quote'
echo "double quote"
expr 1 + 2
echo __TEST_DONE__
```

Expect:

```
echo `echo backtick`
backtick
# echo 'single quote'
single quote
# echo "double quote"
double quote
# expr 1 + 2
expr: cannot execute
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### ED

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
ed /tmp/edtest << EOF
a
hello
world
.
w
q
EOF
cat /tmp/edtest
rm /tmp/edtest
echo __TEST_DONE__
```

Expect:

```
ed /tmp/edtest << EOF
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
# 
```

### FIND

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
find /usr/lib -print
echo __TEST_DONE__
```

Expect:

```
find /usr/lib -print
# find: bad status-- /usr/lib
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### DF

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
df
echo __TEST_DONE__
```

Expect:

```
df
cannot open /dev/rp0
cannot open /dev/rp3
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### GREP

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
grep '^root' /etc/passwd
grep -v root /etc/passwd
grep -c sh /etc/passwd
grep -n sh /etc/passwd
grep '\(o\)\1' /etc/passwd
echo __TEST_DONE__
```

Expect:

```
grep '^root' /etc/passwd
root::0:0:root:/:/bin/sh
# grep -v root /etc/passwd
dmr::1:1:dennis:/:/bin/sh
# grep -c sh /etc/passwd
2
# grep -n sh /etc/passwd
1:root::0:0:root:/:/bin/sh
2:dmr::1:1:dennis:/:/bin/sh
# grep '\(o\)\1' /etc/passwd
root::0:0:root:/:/bin/sh
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### CP

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
mkdir /tmp/cpdir
echo srcA > /tmp/A
echo srcB > /tmp/B
cp /tmp/A /tmp/B /tmp/cpdir
cat /tmp/cpdir/A
cat /tmp/cpdir/B
cp /tmp/A /tmp/A
echo __TEST_DONE__
```

Expect:

```
mkdir /tmp/cpdir
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
# 
```

### MV

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
echo content > /tmp/mvsrc
mv /tmp/mvsrc /tmp/mvsrc
mkdir /tmp/mvA
mkdir /tmp/mvB
mkdir /tmp/mvA/sub
echo data > /tmp/mvA/sub/file
mv /tmp/mvA/sub /tmp/mvB/sub
cat /tmp/mvB/sub/file
echo __TEST_DONE__
```

Expect:

```
echo content > /tmp/mvsrc
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
# 
```

### CHMOD

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
echo x > /tmp/cmf
chmod 644 /tmp/cmf
chmod u+x /tmp/cmf
ls -l /tmp/cmf
chmod a-w /tmp/cmf
ls -l /tmp/cmf
chmod og=r /tmp/cmf
ls -l /tmp/cmf
echo __TEST_DONE__
```

Expect:

```
echo x > /tmp/cmf
# chmod 644 /tmp/cmf
# chmod u+x /tmp/cmf
# ls -l /tmp/cmf
-rwxr--r-- 1 root        2 Jan  1 00:00 /tmp/cmf
# chmod a-w /tmp/cmf
# ls -l /tmp/cmf
-r-xr--r-- 1 root        2 Jan  1 00:00 /tmp/cmf
# chmod og=r /tmp/cmf
# ls -l /tmp/cmf
-r-xr--r-- 1 root        2 Jan  1 00:00 /tmp/cmf
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### TOUCH

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
touch /tmp/tnew
ls /tmp/tnew
echo old > /tmp/told
touch /tmp/told
cat /tmp/told
touch -c /tmp/tabsent
ls /tmp/tabsent
echo __TEST_DONE__
```

Expect:

```
touch /tmp/tnew
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
# 
```

### TR

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
echo abcdef | tr -d def
echo aaabbb | tr -s ab AB
echo Hello123 | tr -cd 0-9
echo __TEST_DONE__
```

Expect:

```
echo abcdef | tr -d def
abc
# echo aaabbb | tr -s ab AB
AB
# echo Hello123 | tr -cd 0-9
123# echo __TEST_DONE__
__TEST_DONE__
# 
```

### SPLIT

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
echo line1 > /tmp/spi
echo line2 >> /tmp/spi
echo line3 >> /tmp/spi
split -1 /tmp/spi /tmp/x
cat /tmp/xaa
cat /tmp/xab
cat /tmp/xac
echo __TEST_DONE__
```

Expect:

```
echo line1 > /tmp/spi
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
# 
```

### TSORT

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
echo a b > /tmp/ts
echo b c >> /tmp/ts
tsort /tmp/ts
echo __TEST_DONE__
```

Expect:

```
echo a b > /tmp/ts
# echo b c >> /tmp/ts
# tsort /tmp/ts
a
b
c
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### WRITE

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
write
echo __TEST_DONE__
```

Expect:

```
write
usage: write user [ttyname]
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### COMM

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
comm /etc/passwd /etc/passwd
echo __TEST_DONE__
```

Expect:

```
comm /etc/passwd /etc/passwd
		root::0:0:root:/:/bin/sh
		dmr::1:1:dennis:/:/bin/sh
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### CRYPT

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
echo hello | crypt key | crypt key
echo __TEST_DONE__
```

Expect:

```
echo hello | crypt key | crypt key
hello
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### DATE

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
date
echo __TEST_DONE__
```

Expect:

```
date
Thu Jan  1 00:00:00 GMT 1970
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### TIME

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
time
echo __TEST_DONE__
```

Expect:

```
time
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### MKNOD

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
mknod
echo __TEST_DONE__
```

Expect:

```
mknod
arg count
usage: mknod name b/c major minor
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### NEWGRP

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
newgrp
echo __TEST_DONE__
```

Expect:

```
newgrp
usage: newgrp groupname
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### CLRI

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
clri
echo __TEST_DONE__
```

Expect:

```
clri
usage: clri filsys inumber ...
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### CALENDAR

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
calendar
echo __TEST_DONE__
```

Expect:

```
calendar
(^|[ (,;])(([Jj]an[^ ]* *|1/)0*1)([^0123456789]|$)
(^|[ (,;])(([Jj]an[^ ]* *|1/)0*2)([^0123456789]|$)
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### CHECKEQ

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
echo hello | checkeq
echo __TEST_DONE__
```

Expect:

```
echo hello | checkeq
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### MOUNT

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
mount
echo __TEST_DONE__
```

Expect:

```
mount
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### UMOUNT

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
umount
echo __TEST_DONE__
```

Expect:

```
umount
arg count
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### DCHECK

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
dcheck /etc/auxfs
echo __TEST_DONE__
```

Expect:

```
dcheck /etc/auxfs
/etc/auxfs:
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### ICHECK

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
icheck /etc/auxfs
echo __TEST_DONE__
```

Expect:

```
icheck /etc/auxfs
/etc/auxfs:
files      2 (r=1,d=1,b=0,c=0)
used       1 (i=0,ii=0,iii=0,d=1)
free      56
missing    0
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### NCHECK

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
ncheck /etc/auxfs
echo __TEST_DONE__
```

Expect:

```
ncheck /etc/auxfs
/etc/auxfs:
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### RANDOM

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
echo hi | random 0
echo __TEST_DONE__
```

Expect:

```
echo hi | random 0
hi
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### STTY

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
stty
echo __TEST_DONE__
```

Expect:

```
stty
speed 0 baud
erase = '^@'; kill = '^@'

# echo __TEST_DONE__
__TEST_DONE__
# 
```

### SU

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
su nosuchuser
echo __TEST_DONE__
```

Expect:

```
su nosuchuser
Unknown id: nosuchuser
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### TABS

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
tabs
echo __TEST_DONE__
```

Expect:

```
tabs
# echo __TEST_DONE__
__TEST_DONE__
# 
```

### WALL

Local test:

```
unix-v7-c99/tools/qemu-shell.py
```

Inputs:

```
echo hi | wall
echo __TEST_DONE__
```

Expect:

```
echo hi | wall
# echo __TEST_DONE__
__TEST_DONE__
# 
```

