## WIP

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
drwxr-xr-x 1 root       64 Jan  1 00:00 .
drwxr-xr-x 1 root      112 Jan  1 00:00 ..
-rwxr-xr-x 1 root        0 Jan  1 00:00 .keep
drwxrwxr-x 1 root       32 Jan  1 00:00 d
# rmdir /tmp/d
# ln /etc/passwd /tmp/pwlink
# ls -li /etc/passwd /tmp/pwlink
   88 -rwxr-xr-x 1 root       51 Jan  1 00:00 /etc/passwd
   88 -rwxr-xr-x 1 root       51 Jan  1 00:00 /tmp/pwlink
# rm /tmp/pwlink
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
   88 /etc/passwd
# ls -l /
total 7
drwxr-xr-x 1 root     1248 Jan  1 00:00 bin
drwxr-xr-x 1 root       48 Jan  1 00:00 dev
drwxr-xr-x 1 root      128 Jan  1 00:00 etc
drwxr-xr-x 1 root       48 Jan  1 00:00 tmp
drwxr-xr-x 1 root       64 Jan  1 00:00 usr
# tty
not a tty
# who
# id
uid=0
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
2
# echo $!
2
# wait
# nice echo niced
niced
# sync
# sleep 100 &
6
# echo $!
6
# kill $!
6: Error 0
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
id
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
