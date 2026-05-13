# Unix v7 -> C99 historical accuracy

### File inventory

Local test:

```
bash -c "\
  find unix-v7-c99 -type f \
    -not -path 'unix-v7-c99/v7/*' \
    -not -name '*.o' -not -name '*.a' -not -name '*.out' \
    -not -name '*.swp' -not -name '*.elf' \
    -not -path 'unix-v7-c99/build/*' \
    -not -path 'unix-v7-c99/root/bin/*' \
    -not -path 'unix-v7-c99/root/usr/*' \
    -not -path 'unix-v7-c99/root/etc/init' \
    -not -path 'unix-v7-c99/root/etc/getty' \
    -not -path 'unix-v7-c99/root.img' \
    -not -path 'unix-v7-c99/unix' \
    -not -path 'unix-v7-c99/conf/test_malloc' \
    -not -path 'unix-v7-c99/sys/unix' \
    | LC_ALL=C sort"
```

Expect:

```
unix-v7-c99/.git
unix-v7-c99/.gitignore
unix-v7-c99/LICENSE
unix-v7-c99/Makefile
unix-v7-c99/README
unix-v7-c99/arch/a7.ld
unix-v7-c99/arch/a7.s
unix-v7-c99/arch/armboot.c
unix-v7-c99/arch/evb.ld
unix-v7-c99/arch/machdep.c
unix-v7-c99/arch/v7stubs.c
unix-v7-c99/cmd/basename.c
unix-v7-c99/cmd/cal.c
unix-v7-c99/cmd/calendar.c
unix-v7-c99/cmd/cat.c
unix-v7-c99/cmd/cb.c
unix-v7-c99/cmd/checkeq.c
unix-v7-c99/cmd/chgrp.c
unix-v7-c99/cmd/chmod.c
unix-v7-c99/cmd/chown.c
unix-v7-c99/cmd/clri.c
unix-v7-c99/cmd/cmp.c
unix-v7-c99/cmd/col.c
unix-v7-c99/cmd/comm.c
unix-v7-c99/cmd/cp.c
unix-v7-c99/cmd/crypt.c
unix-v7-c99/cmd/date.c
unix-v7-c99/cmd/dcheck.c
unix-v7-c99/cmd/dd.c
unix-v7-c99/cmd/df.c
unix-v7-c99/cmd/diff.c
unix-v7-c99/cmd/diffh.c
unix-v7-c99/cmd/du.c
unix-v7-c99/cmd/echo.c
unix-v7-c99/cmd/ed.c
unix-v7-c99/cmd/fgrep.c
unix-v7-c99/cmd/file.c
unix-v7-c99/cmd/find.c
unix-v7-c99/cmd/getty.c
unix-v7-c99/cmd/grep.c
unix-v7-c99/cmd/icheck.c
unix-v7-c99/cmd/id.c
unix-v7-c99/cmd/init.c
unix-v7-c99/cmd/join.c
unix-v7-c99/cmd/kill.c
unix-v7-c99/cmd/ln.c
unix-v7-c99/cmd/login.c
unix-v7-c99/cmd/look.c
unix-v7-c99/cmd/ls.c
unix-v7-c99/cmd/makekey.c
unix-v7-c99/cmd/mesg.c
unix-v7-c99/cmd/mkdir.c
unix-v7-c99/cmd/mknod.c
unix-v7-c99/cmd/mount.c
unix-v7-c99/cmd/mv.c
unix-v7-c99/cmd/ncheck.c
unix-v7-c99/cmd/newgrp.c
unix-v7-c99/cmd/nice.c
unix-v7-c99/cmd/od.c
unix-v7-c99/cmd/pr.c
unix-v7-c99/cmd/pwd.c
unix-v7-c99/cmd/random.c
unix-v7-c99/cmd/rev.c
unix-v7-c99/cmd/rm.c
unix-v7-c99/cmd/rmdir.c
unix-v7-c99/cmd/sh/args.c
unix-v7-c99/cmd/sh/blok.c
unix-v7-c99/cmd/sh/brkincr.h
unix-v7-c99/cmd/sh/builtin.c
unix-v7-c99/cmd/sh/cmd.c
unix-v7-c99/cmd/sh/ctype.c
unix-v7-c99/cmd/sh/ctype.h
unix-v7-c99/cmd/sh/defs.h
unix-v7-c99/cmd/sh/dup.h
unix-v7-c99/cmd/sh/error.c
unix-v7-c99/cmd/sh/expand.c
unix-v7-c99/cmd/sh/fault.c
unix-v7-c99/cmd/sh/io.c
unix-v7-c99/cmd/sh/mac.h
unix-v7-c99/cmd/sh/macro.c
unix-v7-c99/cmd/sh/main.c
unix-v7-c99/cmd/sh/makefile
unix-v7-c99/cmd/sh/mode.h
unix-v7-c99/cmd/sh/msg.c
unix-v7-c99/cmd/sh/name.c
unix-v7-c99/cmd/sh/name.h
unix-v7-c99/cmd/sh/print.c
unix-v7-c99/cmd/sh/service.c
unix-v7-c99/cmd/sh/setbrk.c
unix-v7-c99/cmd/sh/stak.c
unix-v7-c99/cmd/sh/stak.h
unix-v7-c99/cmd/sh/string.c
unix-v7-c99/cmd/sh/sym.h
unix-v7-c99/cmd/sh/timeout.h
unix-v7-c99/cmd/sh/word.c
unix-v7-c99/cmd/sh/xec.c
unix-v7-c99/cmd/sleep.c
unix-v7-c99/cmd/sort.c
unix-v7-c99/cmd/sp.c
unix-v7-c99/cmd/split.c
unix-v7-c99/cmd/stty.c
unix-v7-c99/cmd/su.c
unix-v7-c99/cmd/sum.c
unix-v7-c99/cmd/sync.c
unix-v7-c99/cmd/tabs.c
unix-v7-c99/cmd/tail.c
unix-v7-c99/cmd/tee.c
unix-v7-c99/cmd/test.c
unix-v7-c99/cmd/time.c
unix-v7-c99/cmd/touch.c
unix-v7-c99/cmd/tr.c
unix-v7-c99/cmd/tsort.c
unix-v7-c99/cmd/tty.c
unix-v7-c99/cmd/umount.c
unix-v7-c99/cmd/uniq.c
unix-v7-c99/cmd/wall.c
unix-v7-c99/cmd/wc.c
unix-v7-c99/cmd/who.c
unix-v7-c99/cmd/write.c
unix-v7-c99/cmd/yes.c
unix-v7-c99/conf/Makefile
unix-v7-c99/conf/c.c
unix-v7-c99/conf/putchar.c
unix-v7-c99/conf/test_malloc.c
unix-v7-c99/dev/bio.c
unix-v7-c99/dev/cat.c
unix-v7-c99/dev/dc.c
unix-v7-c99/dev/dh.c
unix-v7-c99/dev/dhdm.c
unix-v7-c99/dev/dhfdm.c
unix-v7-c99/dev/dkleave.c
unix-v7-c99/dev/dn.c
unix-v7-c99/dev/dsort.c
unix-v7-c99/dev/du.c
unix-v7-c99/dev/dz.c
unix-v7-c99/dev/hp.c
unix-v7-c99/dev/ht.c
unix-v7-c99/dev/kl.c
unix-v7-c99/dev/mem.c
unix-v7-c99/dev/mp135_blk.c
unix-v7-c99/dev/mx1.c
unix-v7-c99/dev/mx2.c
unix-v7-c99/dev/partab.c
unix-v7-c99/dev/pk0.c
unix-v7-c99/dev/pk1.c
unix-v7-c99/dev/pk2.c
unix-v7-c99/dev/pk3.c
unix-v7-c99/dev/pl011.c
unix-v7-c99/dev/rf.c
unix-v7-c99/dev/rk.c
unix-v7-c99/dev/rl.c
unix-v7-c99/dev/rp.c
unix-v7-c99/dev/stm32_usart.c
unix-v7-c99/dev/sys.c
unix-v7-c99/dev/tc.c
unix-v7-c99/dev/tm.c
unix-v7-c99/dev/tty.c
unix-v7-c99/dev/virtio_blk.c
unix-v7-c99/dev/vp.c
unix-v7-c99/dev/vs.c
unix-v7-c99/h/acct.h
unix-v7-c99/h/arm.h
unix-v7-c99/h/buf.h
unix-v7-c99/h/callo.h
unix-v7-c99/h/conf.h
unix-v7-c99/h/dir.h
unix-v7-c99/h/fblk.h
unix-v7-c99/h/file.h
unix-v7-c99/h/filsys.h
unix-v7-c99/h/ino.h
unix-v7-c99/h/inode.h
unix-v7-c99/h/map.h
unix-v7-c99/h/mount.h
unix-v7-c99/h/mpx.h
unix-v7-c99/h/mx.h
unix-v7-c99/h/pack.h
unix-v7-c99/h/param.h
unix-v7-c99/h/pk.h
unix-v7-c99/h/prim.h
unix-v7-c99/h/proc.h
unix-v7-c99/h/proto.h
unix-v7-c99/h/pwd.h
unix-v7-c99/h/reg.h
unix-v7-c99/h/seg.h
unix-v7-c99/h/smallparam.h
unix-v7-c99/h/stat.h
unix-v7-c99/h/systm.h
unix-v7-c99/h/text.h
unix-v7-c99/h/timeb.h
unix-v7-c99/h/tty.h
unix-v7-c99/h/types.h
unix-v7-c99/h/user.h
unix-v7-c99/include/ctype.h
unix-v7-c99/include/errno.h
unix-v7-c99/include/execargs.h
unix-v7-c99/include/grp.h
unix-v7-c99/include/pwd.h
unix-v7-c99/include/setjmp.h
unix-v7-c99/include/sgtty.h
unix-v7-c99/include/signal.h
unix-v7-c99/include/stdio.h
unix-v7-c99/include/sys/dir.h
unix-v7-c99/include/sys/fblk.h
unix-v7-c99/include/sys/filsys.h
unix-v7-c99/include/sys/ino.h
unix-v7-c99/include/sys/inode.h
unix-v7-c99/include/sys/param.h
unix-v7-c99/include/sys/stat.h
unix-v7-c99/include/sys/timeb.h
unix-v7-c99/include/sys/times.h
unix-v7-c99/include/sys/types.h
unix-v7-c99/include/time.h
unix-v7-c99/include/utmp.h
unix-v7-c99/lib/Makefile
unix-v7-c99/lib/abs.c
unix-v7-c99/lib/atoi.c
unix-v7-c99/lib/atol.c
unix-v7-c99/lib/compat.c
unix-v7-c99/lib/crt0.c
unix-v7-c99/lib/crt0.s
unix-v7-c99/lib/crypt.c
unix-v7-c99/lib/errlst.c
unix-v7-c99/lib/execvp.c
unix-v7-c99/lib/getenv.c
unix-v7-c99/lib/getpwent.c
unix-v7-c99/lib/getpwnam.c
unix-v7-c99/lib/getpwuid.c
unix-v7-c99/lib/index.c
unix-v7-c99/lib/isatty.c
unix-v7-c99/lib/l3.c
unix-v7-c99/lib/mktemp.c
unix-v7-c99/lib/perror.c
unix-v7-c99/lib/rand.c
unix-v7-c99/lib/rindex.c
unix-v7-c99/lib/strcat.c
unix-v7-c99/lib/strcmp.c
unix-v7-c99/lib/strcpy.c
unix-v7-c99/lib/strlen.c
unix-v7-c99/lib/strncat.c
unix-v7-c99/lib/strncmp.c
unix-v7-c99/lib/strncpy.c
unix-v7-c99/lib/swab.c
unix-v7-c99/lib/syscall.s
unix-v7-c99/lib/ttyname.c
unix-v7-c99/lib/ttyslot.c
unix-v7-c99/lib/u.h
unix-v7-c99/lib/u.ld
unix-v7-c99/root/etc/passwd
unix-v7-c99/root/etc/ttys
unix-v7-c99/sys/Makefile
unix-v7-c99/sys/acct.c
unix-v7-c99/sys/alloc.c
unix-v7-c99/sys/clock.c
unix-v7-c99/sys/fakemx.c
unix-v7-c99/sys/fio.c
unix-v7-c99/sys/iget.c
unix-v7-c99/sys/machdep.c
unix-v7-c99/sys/main.c
unix-v7-c99/sys/malloc.c
unix-v7-c99/sys/nami.c
unix-v7-c99/sys/pipe.c
unix-v7-c99/sys/prf.c
unix-v7-c99/sys/prim.c
unix-v7-c99/sys/rdwri.c
unix-v7-c99/sys/sig.c
unix-v7-c99/sys/slp.c
unix-v7-c99/sys/subr.c
unix-v7-c99/sys/sys1.c
unix-v7-c99/sys/sys2.c
unix-v7-c99/sys/sys3.c
unix-v7-c99/sys/sys4.c
unix-v7-c99/sys/sysent.c
unix-v7-c99/sys/text.c
unix-v7-c99/sys/trap.c
unix-v7-c99/sys/ureg.c
unix-v7-c99/tools/minimkfs
unix-v7-c99/tools/mkfs
unix-v7-c99/tools/mkfs.c
unix-v7-c99/tools/qemu-shell.py
```

### Files NOT diffed

Local test:

```
bash -c "\
  export LC_ALL=C; \
  comm -23 \
    <(find unix-v7-c99 -type f \
        -not -path 'unix-v7-c99/v7/*' \
        -not -name '*.o' -not -name '*.a' -not -name '*.out' \
        -not -name '*.swp' -not -name '*.elf' \
        -not -path 'unix-v7-c99/build/*' \
        -not -path 'unix-v7-c99/root/bin/*' \
        -not -path 'unix-v7-c99/root/usr/*' \
        -not -path 'unix-v7-c99/root/etc/init' \
        -not -path 'unix-v7-c99/root/etc/getty' \
        -not -path 'unix-v7-c99/root.img' \
        -not -path 'unix-v7-c99/unix' \
        -not -path 'unix-v7-c99/conf/test_malloc' \
        -not -path 'unix-v7-c99/sys/unix' \
        | sed 's|^unix-v7-c99/||' | LC_ALL=C sort) \
    <(grep '^diff unix-v7-c99/v7/' \
        \$(find . -name 'unix-historical-accuracy.md' \
            -not -path '*/.workdir/*' | head -1) \
        | awk '{print \$3}' \
        | sed 's|^unix-v7-c99/||' | LC_ALL=C sort)"
```

Expect:

```
.git
.gitignore
LICENSE
Makefile
README
arch/a7.ld
arch/a7.s
arch/armboot.c
arch/evb.ld
arch/machdep.c
arch/v7stubs.c
cmd/id.c
cmd/sh/makefile
conf/Makefile
conf/test_malloc.c
dev/mp135_blk.c
dev/pl011.c
dev/stm32_usart.c
dev/virtio_blk.c
h/arm.h
h/proto.h
lib/Makefile
lib/compat.c
lib/crt0.c
lib/u.h
lib/u.ld
root/etc/passwd
root/etc/ttys
sys/Makefile
tools/minimkfs
tools/mkfs
tools/qemu-shell.py
```

### cmd/echo.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/echo.c unix-v7-c99/cmd/echo.c || true
```

Expect:

```
3,5c3,4
< main(argc, argv)
< int argc;
< char *argv[];
---
> int
> main(int argc, char *argv[])
```

### cmd/cat.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/cat.c unix-v7-c99/cmd/cat.c || true
```

Expect:

```
11,12c11,12
< main(argc, argv)
< char **argv;
---
> int
> main(int argc, char *argv[])
16c16
< 	register c;
---
> 	register int c;
```

### cmd/sync.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sync.c unix-v7-c99/cmd/sync.c || true
```

Expect:

```
1c1,4
< main()
---
> void sync(void);
> 
> int
> main(void)
```

### cmd/rev.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/rev.c unix-v7-c99/cmd/rev.c || true
```

Expect:

```
9,10c9,10
< main(argc,argv)
< char **argv;
---
> int
> main(int argc, char *argv[])
12c12
< 	register i,c;
---
> 	register int i,c;
```

### cmd/yes.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/yes.c unix-v7-c99/cmd/yes.c || true
```

Expect:

```
1,2c1,4
< main(argc, argv)
< char **argv;
---
> int printf(char *fmt, ...);
> 
> int
> main(int argc, char *argv[])
```

### cmd/wc.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/wc.c unix-v7-c99/cmd/wc.c || true
```

Expect:

```
5,6c5,8
< main(argc, argv)
< char **argv;
---
> void wcp(register char *wd, long charct, long wordct, long linect);
> 
> int
> main(int argc, char *argv[])
69,71c71,72
< wcp(wd, charct, wordct, linect)
< register char *wd;
< long charct; long wordct; long linect;
---
> void
> wcp(register char *wd, long charct, long wordct, long linect)
```

### cmd/basename.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/basename.c unix-v7-c99/cmd/basename.c || true
```

Expect:

```
3,4c3,4
< main(argc, argv)
< char **argv;
---
> int
> main(int argc, char *argv[])
```

### cmd/sum.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sum.c unix-v7-c99/cmd/sum.c || true
```

Expect:

```
7,8c7,8
< main(argc,argv)
< char **argv;
---
> int
> main(int argc, char *argv[])
11c11
< 	register i, c;
---
> 	register int i, c;
```

### cmd/tty.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/tty.c unix-v7-c99/cmd/tty.c || true
```

Expect:

```
5a6,8
> int strcmp(char *a, char *b);
> int printf(char *fmt, ...);
> void exit(int n);
7,8c10,11
< main(argc, argv)
< char **argv;
---
> int
> main(int argc, char *argv[])
```

### cmd/cmp.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/cmp.c unix-v7-c99/cmd/cmp.c || true
```

Expect:

```
12c12
< long	otoi();
---
> long	otoi(char *s);
14,15c14,15
< main(argc, argv)
< char **argv;
---
> int
> main(int argc, char *argv[])
17c17
< 	register c1, c2;
---
> 	register int c1, c2;
108,109c108,109
< long otoi(s)
< char *s;
---
> long
> otoi(char *s)
```

### cmd/comm.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/comm.c unix-v7-c99/cmd/comm.c || true
```

Expect:

```
11,13c11,18
< FILE *openfil();
< main(argc,argv)
< char	*argv[];
---
> FILE *openfil(char *s);
> int rd(FILE *file, char *buf);
> void wr(char *str, int n);
> void copy(FILE *ibuf, char *lbuf, int n);
> int compare(char *a, char *b);
> 
> int
> main(int argc, char *argv[])
93,95c98,99
< rd(file,buf)
< FILE *file;
< char *buf;
---
> int
> rd(FILE *file, char *buf)
112,113c116,117
< wr(str,n)
< 	char	*str;
---
> void
> wr(char *str, int n)
132,134c136,137
< copy(ibuf,lbuf,n)
< FILE *ibuf;
< char *lbuf;
---
> void
> copy(FILE *ibuf, char *lbuf, int n)
143,144c146,147
< compare(a,b)
< 	char	*a,*b;
---
> int
> compare(char *a, char *b)
155,156c158,159
< FILE *openfil(s)
< char *s;
---
> FILE *
> openfil(char *s)
```

### cmd/od.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/od.c unix-v7-c99/cmd/od.c || true
```

Expect:

```
14,15c14,22
< main(argc, argv)
< char **argv;
---
> void offset(register char *s);
> void line(long a, unsigned short *w, int n);
> void putx(unsigned n, int c);
> void cput(int c);
> void putn(long n, int b, int c);
> void pre(int n);
> 
> int
> main(int argc, char *argv[])
18c25
< 	register n, f, same;
---
> 	register int n, f, same;
97,99c104,105
< line(a, w, n)
< long a;
< unsigned short *w;
---
> void
> line(long a, unsigned short *w, int n)
101c107
< 	register i, f, c;
---
> 	register int i, f, c;
120,121c126,127
< putx(n, c)
< unsigned n;
---
> void
> putx(unsigned n, int c)
158c164,165
< cput(c)
---
> void
> cput(int c)
190,191c197,198
< putn(n, b, c)
< long n;
---
> void
> putn(long n, int b, int c)
193c200
< 	register d;
---
> 	register int d;
205c212,213
< pre(n)
---
> void
> pre(int n)
213,214c221,222
< offset(s)
< register char *s;
---
> void
> offset(register char *s)
```

### cmd/tail.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/tail.c unix-v7-c99/cmd/tail.c || true
```

Expect:

```
20,21c20,23
< main(argc,argv)
< char **argv;
---
> int digit(int c);
> 
> int
> main(int argc, char *argv[])
24c26
< 	register i,j,k;
---
> 	register int i,j,k;
181c183,184
< digit(c)
---
> int
> digit(int c)
```

### cmd/test.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/test.c unix-v7-c99/cmd/test.c || true
```

Expect:

```
18,19c18,30
< main(argc, argv)
< char *argv[];
---
> char *nxtarg(int mt);
> int exp(void);
> int e1(void);
> int e2(void);
> int e3(void);
> int tio(char *a, int f);
> int ftype(char *f);
> int fsizep(char *f);
> void synbad(char *s1, char *s2);
> int length(char *s);
> 
> int
> main(int argc, char *argv[])
32c43
< char *nxtarg(mt) {
---
> char *nxtarg(int mt) {
44c55,56
< exp() {
---
> int
> exp(void) {
53c65,66
< e1() {
---
> int
> e1(void) {
62c75,76
< e2() {
---
> int
> e2(void) {
69c83,84
< e3() {
---
> int
> e3(void) {
136a152
> 	return(0);
139,141c155,156
< tio(a, f)
< char *a;
< int f;
---
> int
> tio(char *a, int f)
152,153c167,168
< ftype(f)
< char *f;
---
> int
> ftype(char *f)
164,165c179,180
< fsizep(f)
< char *f;
---
> int
> fsizep(char *f)
173,174c188,189
< synbad(s1,s2)
< char *s1, *s2;
---
> void
> synbad(char *s1, char *s2)
183,184c198,199
< length(s)
< 	char *s;
---
> int
> length(char *s)
```

### cmd/look.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/look.c unix-v7-c99/cmd/look.c || true
```

Expect:

```
14,15c14,19
< main(argc,argv)
< char **argv;
---
> void canon(char *old, char *new);
> int compare(register char *s, register char *t);
> int getword(char *w);
> 
> int
> main(int argc, char *argv[])
17c21
< 	register c;
---
> 	register int c;
44c48
< 		return;
---
> 		return(0);
87c91
< 			return;
---
> 			return(0);
91c95
< 			return;
---
> 			return(0);
111a116
> 	return(0);
114,115c119,120
< compare(s,t)
< register char *s,*t;
---
> int
> compare(register char *s, register char *t)
126,127c131,132
< getword(w)
< char *w;
---
> int
> getword(char *w)
129c134
< 	register c;
---
> 	register int c;
142,143c147,148
< canon(old,new)
< char *old,*new;
---
> void
> canon(char *old, char *new)
145c150
< 	register c;
---
> 	register int c;
```

### cmd/rm.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/rm.c unix-v7-c99/cmd/rm.c || true
```

Expect:

```
8c8,12
< char	*sprintf();
---
> char	*sprintf(char *buf, char *fmt, ...);
> void	rm(char *arg, int fflg, int rflg, int iflg, int level);
> int	dotname(char *s);
> int	rmdir(char *f, int iflg);
> int	yes(void);
10,11c14,15
< main(argc, argv)
< char *argv[];
---
> int
> main(int argc, char *argv[])
51,52c55,56
< rm(arg, fflg, rflg, iflg, level)
< char arg[];
---
> void
> rm(char arg[], int fflg, int rflg, int iflg, int level)
116,117c120,121
< dotname(s)
< char *s;
---
> int
> dotname(char *s)
130,131c134,135
< rmdir(f, iflg)
< char *f;
---
> int
> rmdir(char *f, int iflg)
151a156
> 	return(1);
154c159,160
< yes()
---
> int
> yes(void)
```

### cmd/ln.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/ln.c unix-v7-c99/cmd/ln.c || true
```

Expect:

```
10,11c10,11
< main(argc, argv)
< char **argv;
---
> int
> main(int argc, char **argv)
```

### cmd/mkdir.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/mkdir.c unix-v7-c99/cmd/mkdir.c || true
```

Expect:

```
10a11
> void	mkdir(char *d);
12,13c13,14
< main(argc, argv)
< char *argv[];
---
> int
> main(int argc, char *argv[])
31,32c32,33
< mkdir(d)
< char *d;
---
> void
> mkdir(char *d)
35c36
< 	register i, slash = 0;
---
> 	register int i, slash = 0;
```

### cmd/rmdir.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/rmdir.c unix-v7-c99/cmd/rmdir.c || true
```

Expect:

```
13a14
> void	rmdir(char *d);
15,17c16,17
< main(argc,argv)
< int argc;
< char **argv;
---
> int
> main(int argc, char **argv)
29,30c29,30
< rmdir(d)
< char *d;
---
> void
> rmdir(char *d)
```

### cmd/tee.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/tee.c unix-v7-c99/cmd/tee.c || true
```

Expect:

```
18c18
< extern errno;
---
> int errno;
19a20,24
> int	creat(char *path, int mode);
> int	stat(char *path, struct stat *buf);
> int	signal(int sig, int fun);
> void	stash(int p);
> void	puts(char *s);
21,22c26,27
< main(argc,argv)
< char **argv;
---
> int
> main(int argc, char **argv)
24c29
< 	int register r,w,p;
---
> 	register int r,w,p;
70c75
< 					return;
---
> 					return(0);
79c84,85
< stash(p)
---
> void
> stash(int p)
90,91c96,97
< puts(s)
< char *s;
---
> void
> puts(char *s)
```

### cmd/uniq.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/uniq.c unix-v7-c99/cmd/uniq.c || true
```

Expect:

```
11a12,15
> int	gline(char *buf);
> void	pline(char *buf);
> int	equal(char *b1, char *b2);
> void	printe(char *p, char *s);
13,15c17,18
< main(argc, argv)
< int argc;
< char *argv[];
---
> int
> main(int argc, char *argv[])
65,66c68,69
< gline(buf)
< register char buf[];
---
> int
> gline(char buf[])
68c71
< 	register c;
---
> 	register int c;
79,80c82,83
< pline(buf)
< register char buf[];
---
> void
> pline(char buf[])
104,105c107,108
< equal(b1, b2)
< register char b1[], b2[];
---
> int
> equal(char b1[], char b2[])
123c126
< 	register nf, nl;
---
> 	register int nf, nl;
137,138c140,141
< printe(p,s)
< char *p,*s;
---
> void
> printe(char *p, char *s)
```

### cmd/date.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/date.c unix-v7-c99/cmd/date.c || true
```

Expect:

```
9a10
> #include <stdio.h>
14c15,17
< char	*timezone();
---
> int	gtime(void);
> int	gp(int dfault);
> void	exit(int n);
33,37c36
< char	*ctime();
< char	*asctime();
< struct	tm *localtime();
< struct	tm *gmtime();
< 
---
> int
38a38
> int argc;
93a94
> int
151a153
> int
152a155
> int dfault;
```

### cmd/kill.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/kill.c unix-v7-c99/cmd/kill.c || true
```

Expect:

```
5a6
> #include <stdio.h>
6a8,14
> int kill(int pid, int sig);
> int atoi(char *s);
> void exit(int n);
> extern char *sys_errlist[];
> int errno;
> 
> int
7a16
> int argc;
10c19
< 	register signo, pid, res;
---
> 	register int signo, pid, res;
12,13d20
< 	extern char *sys_errlist[];
< 	extern errno;
```

### cmd/nice.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/nice.c unix-v7-c99/cmd/nice.c || true
```

Expect:

```
4a5,12
> int atoi(char *s);
> int nice(int incr);
> int execvp(char *name, char **argv);
> void exit(int n);
> int errno;
> extern char *sys_errlist[];
> 
> int
10,11d17
< 	extern errno;
< 	extern char *sys_errlist[];
```

### cmd/mknod.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/mknod.c unix-v7-c99/cmd/mknod.c || true
```

Expect:

```
0a1,5
> #include <stdio.h>
> 
> int number(char *s);
> 
> int
29a35
> int
```

### cmd/who.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/who.c unix-v7-c99/cmd/who.c || true
```

Expect:

```
10d9
< struct passwd *getpwuid();
12a12,17
> int getuid(void);
> int time(long *t);
> void putline(void);
> void exit(int n);
> 
> int
13a19
> int argc;
54a61
> void
```

### cmd/mesg.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/mesg.c unix-v7-c99/cmd/mesg.c || true
```

Expect:

```
18a19,23
> void error(char *s);
> void newmode(int m);
> void exit(int n);
> 
> int
19a25
> int argc;
43a50
> void
50a58
> void
51a60
> int m;
```

### cmd/time.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/time.c unix-v7-c99/cmd/time.c || true
```

Expect:

```
8c8
< extern int errno;
---
> int errno;
10a11,14
> void printt(char *s, long a);
> void exit(int n);
> 
> int
11a16
> int argc;
16c21
< 	register p;
---
> 	register int p;
52a58
> void
58c64
< 	register i;
---
> 	register int i;
```

### cmd/checkeq.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/checkeq.c unix-v7-c99/cmd/checkeq.c || true
```

Expect:

```
8c8,15
< main(argc, argv) char **argv; {
---
> void check(FILE *f);
> void exit(int n);
> 
> int
> main(argc, argv)
> int argc;
> char **argv;
> {
32a40
> void
```

### cmd/calendar.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/calendar.c unix-v7-c99/cmd/calendar.c || true
```

Expect:

```
7a8
> #include <stdio.h>
26a28,31
> void tprint(long t);
> int time(long *t);
> 
> void
35a41
> int
44a51
> 		/* FALLTHROUGH */
47a55
> 		/* FALLTHROUGH */
```

### cmd/col.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/col.c unix-v7-c99/cmd/col.c || true
```

Expect:

```
19a20,28
> void outc(int c);
> void store(int lno);
> void fetch(int lno);
> void emit(char *s, int lineno);
> void incr(void);
> void decr(void);
> char *malloc(unsigned n);
> void free(char *p);
> void exit(int n);
20a30
> int
161a172
> void
163c174
< 	register char c;
---
> 	register int c;
207a219
> void
208a221
> 	int lno;
210,211d222
< 	char *malloc();
< 
222a234
> void
223a236
> int lno;
235a249
> void
293a308
> void
307a323
> void
```

### cmd/fgrep.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/fgrep.c unix-v7-c99/cmd/fgrep.c || true
```

Expect:

```
32a33,40
> void execute(char *file);
> int getargc(void);
> void cgotofn(void);
> void overflo(void);
> void cfail(void);
> void exit(int n);
> 
> int
33a42
> int argc;
111a121
> void
117c127
< 	register ccount;
---
> 	register int ccount;
224a235
> int
227c238
< 	register c;
---
> 	register int c;
234a246
> void
236c248
< 	register c;
---
> 	register int c;
297a310
> void
301a315
> void
```

### cmd/su.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/su.c unix-v7-c99/cmd/su.c || true
```

Expect:

```
8a9
> int
```

### cmd/newgrp.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/newgrp.c unix-v7-c99/cmd/newgrp.c || true
```

Expect:

```
8a9,11
> void done(void);
> 
> int
13c16
< 	register i;
---
> 	register int i;
44a48
> void
47c51
< 	register i;
---
> 	register int i;
```

### cmd/random.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/random.c unix-v7-c99/cmd/random.c || true
```

Expect:

```
7c7,8
< main(argc,argv) char **argv;
---
> int
> main(int argc, char **argv)
```

### cmd/crypt.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/crypt.c unix-v7-c99/cmd/crypt.c || true
```

Expect:

```
15,16c15,16
< setup(pw)
< char *pw;
---
> void
> setup(char *pw)
68,69c68,69
< main(argc, argv)
< char *argv[];
---
> int
> main(int argc, char *argv[])
71c71
< 	register i, n1, n2;
---
> 	register int i, n1, n2;
```

### cmd/makekey.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/makekey.c unix-v7-c99/cmd/makekey.c || true
```

Expect:

```
8a9,10
> int	read();
> int	write();
10c12,13
< main()
---
> int
> main(void)
```

### cmd/diffh.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/diffh.c unix-v7-c99/cmd/diffh.c || true
```

Expect:

```
17a18,29
> char	*getl(int f, long n);
> void	clrl(int f, long n);
> void	movstr(char *s, char *t);
> int	easysynch(void);
> int	output(int a, int b);
> void	change(long a, int b, long c, int d, char *s);
> void	range(long a, int b);
> int	cmp(char *s, char *t);
> FILE	*dopen(char *f1, char *f2);
> void	progerr(char *s);
> void	error(char *s, char *t);
> int	hardsynch(void);
20,21c32
< char *getl(f,n)
< long n;
---
> char *getl(int f, long n)
24,25c35
< 	char *malloc();
< 	register delta, nt;
---
> 	register int delta, nt;
55,56c65,66
< clrl(f,n)
< long n;
---
> void
> clrl(int f, long n)
58c68
< 	register i,j;
---
> 	register int i,j;
66,67c76,77
< movstr(s,t)
< register char *s, *t;
---
> void
> movstr(register char *s, register char *t)
73,74c83,84
< main(argc,argv)
< char **argv;
---
> int
> main(int argc, char **argv)
103c113
< 		return;
---
> 		return(0);
111c121,122
< easysynch()
---
> int
> easysynch(void)
114c125
< 	register k,m;
---
> 	register int k,m;
143c154,155
< output(a,b)
---
> int
> output(int a, int b)
145c157
< 	register i;
---
> 	register int i;
174,176c186,187
< change(a,b,c,d,s)
< long a,c;
< char *s;
---
> void
> change(long a, int b, long c, int d, char *s)
184,185c195,196
< range(a,b)
< long a;
---
> void
> range(long a, int b)
195,196c206,207
< cmp(s,t)
< char *s,*t;
---
> int
> cmp(char *s, char *t)
213,214c224,225
< FILE *dopen(f1,f2)
< char *f1,*f2;
---
> FILE *
> dopen(char *f1, char *f2)
242,243c253,254
< progerr(s)
< char *s;
---
> void
> progerr(char *s)
248,249c259,260
< error(s,t)
< char *s,*t;
---
> void
> error(char *s, char *t)
256c267,268
< hardsynch()
---
> int
> hardsynch(void)
```

### cmd/stty.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/stty.c unix-v7-c99/cmd/stty.c || true
```

Expect:

```
178a179,182
> int	eq(char *string);
> void	prmodes(void);
> void	delay(int m, char *s);
> void	prspeed(char *c, int s);
180,181c184,185
< main(argc, argv)
< char	*argv[];
---
> int
> main(int argc, char *argv[])
232,233c236,237
< eq(string)
< char *string;
---
> int
> eq(char *string)
249c253,254
< prmodes()
---
> void
> prmodes(void)
251c256
< 	register m;
---
> 	register int m;
284,285c289,290
< delay(m, s)
< char *s;
---
> void
> delay(int m, char *s)
296,297c301,302
< prspeed(c, s)
< char *c;
---
> void
> prspeed(char *c, int s)
```

### cmd/tabs.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/tabs.c unix-v7-c99/cmd/tabs.c || true
```

Expect:

```
44a45,58
> int	syslook(char *w);
> void	clear(int n);
> void	delay(int n);
> void	tabs(int n);
> void	margin(int n);
> void	escape(int c);
> void	bs(int n);
> void	nl(void);
> void	dasi450(void);
> void	tty37(void);
> void	dasi300(void);
> void	tn300(void);
> void	hp2645(void);
> void	misc(void);
46,47c60,61
< syslook(w)
< char *w;
---
> int
> syslook(char *w)
57,58c71,72
< main(argc,argv)
< int argc; char **argv;
---
> int
> main(int argc, char **argv)
99c113,114
< clear(n)
---
> void
> clear(int n)
106c121,122
< delay(n)
---
> void
> delay(int n)
111c127,128
< tabs(n)
---
> void
> tabs(int n)
125c142,143
< margin(n)
---
> void
> margin(int n)
134c152,153
< escape(c)
---
> void
> escape(int c)
139c158,159
< bs(n)
---
> void
> bs(int n)
144c164,165
< nl()
---
> void
> nl(void)
153c174,175
< dasi450()
---
> void
> dasi450(void)
163c185,186
< tty37()
---
> void
> tty37(void)
168c191,192
< dasi300()
---
> void
> dasi300(void)
173c197,198
< tn300()
---
> void
> tn300(void)
183c208,209
< hp2645()
---
> void
> hp2645(void)
191c217,218
< misc()
---
> void
> misc(void)
```

### cmd/wall.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/wall.c unix-v7-c99/cmd/wall.c || true
```

Expect:

```
9a10
> void	sendmes(char *tty);
11,12c12,13
< main(argc, argv)
< char *argv[];
---
> int
> main(int argc, char *argv[])
14c15
< 	register i;
---
> 	register int i;
43,44c44,45
< sendmes(tty)
< char *tty;
---
> void
> sendmes(char *tty)
46c47
< 	register i;
---
> 	register int i;
```

### cmd/df.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/df.c unix-v7-c99/cmd/df.c || true
```

Expect:

```
17a18
> int	errno;
18a20,21
> void	dfree(char *file);
> void	bread(daddr_t bno, char *buf, int cnt);
20,21c23,24
< main(argc, argv)
< char **argv;
---
> int
> main(int argc, char **argv)
35,36c38,39
< dfree(file)
< char *file;
---
> void
> dfree(char *file)
83,85c86,87
< bread(bno, buf, cnt)
< daddr_t bno;
< char *buf;
---
> void
> bread(daddr_t bno, char *buf, int cnt)
88d89
< 	extern errno;
```

### cmd/clri.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/clri.c unix-v7-c99/cmd/clri.c || true
```

Expect:

```
6a7
> #include <stdio.h>
15a17
> int	isnumber(char *s);
17,18c19,20
< main(argc, argv)
< char *argv[];
---
> int
> main(int argc, char *argv[])
20c22
< 	register i, f;
---
> 	register int i, f;
22c24,25
< 	int j, k;
---
> 	int j;
> 	unsigned k;
70,71c73,74
< isnumber(s)
< char *s;
---
> int
> isnumber(char *s)
73c76
< 	register c;
---
> 	register int c;
```

### cmd/cb.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/cb.c unix-v7-c99/cmd/cb.c || true
```

Expect:

```
1a2,11
> #define	puts	cb_puts
> #define	gets	cb_gets
> int	getch(void);
> int	lookup(char **tab);
> int	gotelse(void);
> int	getnl(void);
> int	ptabs(void);
> int	comment(void);
> int	puts(void);
> int	gets(void);
38a49
> int
41a53,54
> 	(void)argc;
> 	(void)argv;
259a273
> 	return(0);
260a275
> int
263a279
> 	return(0);
264a281
> int
270a288
> int
290a309
> 	return(0);
291a311
> int
306a327
> int
324a346
> int
329a352
> 	return(0);
330a354
> int
351a376
> int
363a389
> 	return(0);
```

### cmd/sp.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sp.c unix-v7-c99/cmd/sp.c || true
```

Expect:

```
10a11,14
> int	getit(void);
> int	putit(int ntab);
> int	clean(void);
> int
13c17
< 	register c;
---
> 	register int c;
33a38
> int
34a40
> int ntab;
37a44
> 	return(0);
38a46
> int
41a50
> 	return(0);
42a52
> int
43a54
> int argc;
```

### cmd/ed.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/ed.c unix-v7-c99/cmd/ed.c || true
```

Expect:

```
7a8,10
> #define	puts	u_puts
> #include "../lib/u.h"
> #undef	puts
```

### lib/l3.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/l3.c unix-v7-c99/lib/l3.c || true
```

Expect:

```
3a4,7
> int ltol3(char *cp, long *lp, int n);
> int l3tol(long *lp, char *cp, int n);
> 
> int
9c13
< 	register i;
---
> 	register int i;
26a31
> 	return(0);
28a34
> int
34c40
< 	register i;
---
> 	register int i;
51a58
> 	return(0);
```

### include/sys/filsys.h

Local test:

```
diff unix-v7-c99/v7/usr/include/sys/filsys.h unix-v7-c99/include/sys/filsys.h || true
```

Expect:

```

```

### include/sys/fblk.h

Local test:

```
diff unix-v7-c99/v7/usr/include/sys/fblk.h unix-v7-c99/include/sys/fblk.h || true
```

Expect:

```

```

### include/sys/ino.h

Local test:

```
diff unix-v7-c99/v7/usr/include/sys/ino.h unix-v7-c99/include/sys/ino.h || true
```

Expect:

```

```

### include/sgtty.h

Local test:

```
diff unix-v7-c99/v7/usr/include/sgtty.h unix-v7-c99/include/sgtty.h || true
```

Expect:

```

```

### h/acct.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/acct.h unix-v7-c99/h/acct.h || true
```

Expect:

```

```

### h/callo.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/callo.h unix-v7-c99/h/callo.h || true
```

Expect:

```

```

### h/conf.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/conf.h unix-v7-c99/h/conf.h || true
```

Expect:

```

```

### h/fblk.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/fblk.h unix-v7-c99/h/fblk.h || true
```

Expect:

```

```

### h/file.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/file.h unix-v7-c99/h/file.h || true
```

Expect:

```

```

### h/filsys.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/filsys.h unix-v7-c99/h/filsys.h || true
```

Expect:

```

```

### h/ino.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/ino.h unix-v7-c99/h/ino.h || true
```

Expect:

```

```

### h/mount.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/mount.h unix-v7-c99/h/mount.h || true
```

Expect:

```

```

### h/mpx.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/mpx.h unix-v7-c99/h/mpx.h || true
```

Expect:

```

```

### h/mx.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/mx.h unix-v7-c99/h/mx.h || true
```

Expect:

```

```

### h/pack.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/pack.h unix-v7-c99/h/pack.h || true
```

Expect:

```

```

### h/pk.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/pk.h unix-v7-c99/h/pk.h || true
```

Expect:

```

```

### h/prim.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/prim.h unix-v7-c99/h/prim.h || true
```

Expect:

```

```

### h/pwd.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/pwd.h unix-v7-c99/h/pwd.h || true
```

Expect:

```

```

### h/reg.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/reg.h unix-v7-c99/h/reg.h || true
```

Expect:

```

```

### h/seg.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/seg.h unix-v7-c99/h/seg.h || true
```

Expect:

```

```

### h/stat.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/stat.h unix-v7-c99/h/stat.h || true
```

Expect:

```

```

### h/text.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/text.h unix-v7-c99/h/text.h || true
```

Expect:

```

```

### h/timeb.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/timeb.h unix-v7-c99/h/timeb.h || true
```

Expect:

```

```

### h/tty.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/tty.h unix-v7-c99/h/tty.h || true
```

Expect:

```

```

### sys/acct.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/acct.c unix-v7-c99/sys/acct.c || true
```

Expect:

```

```

### sys/alloc.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/alloc.c unix-v7-c99/sys/alloc.c || true
```

Expect:

```

```

### sys/clock.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/clock.c unix-v7-c99/sys/clock.c || true
```

Expect:

```

```

### sys/fakemx.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/fakemx.c unix-v7-c99/sys/fakemx.c || true
```

Expect:

```

```

### sys/fio.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/fio.c unix-v7-c99/sys/fio.c || true
```

Expect:

```

```

### sys/machdep.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/machdep.c unix-v7-c99/sys/machdep.c || true
```

Expect:

```

```

### sys/pipe.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/pipe.c unix-v7-c99/sys/pipe.c || true
```

Expect:

```

```

### sys/rdwri.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/rdwri.c unix-v7-c99/sys/rdwri.c || true
```

Expect:

```

```

### sys/sig.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/sig.c unix-v7-c99/sys/sig.c || true
```

Expect:

```

```

### sys/subr.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/subr.c unix-v7-c99/sys/subr.c || true
```

Expect:

```

```

### sys/sys1.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/sys1.c unix-v7-c99/sys/sys1.c || true
```

Expect:

```

```

### sys/sys2.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/sys2.c unix-v7-c99/sys/sys2.c || true
```

Expect:

```

```

### sys/sys3.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/sys3.c unix-v7-c99/sys/sys3.c || true
```

Expect:

```

```

### sys/sys4.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/sys4.c unix-v7-c99/sys/sys4.c || true
```

Expect:

```

```

### sys/sysent.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/sysent.c unix-v7-c99/sys/sysent.c || true
```

Expect:

```

```

### sys/text.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/text.c unix-v7-c99/sys/text.c || true
```

Expect:

```

```

### sys/trap.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/trap.c unix-v7-c99/sys/trap.c || true
```

Expect:

```

```

### sys/ureg.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/ureg.c unix-v7-c99/sys/ureg.c || true
```

Expect:

```

```

### dev/cat.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/cat.c unix-v7-c99/dev/cat.c || true
```

Expect:

```

```

### dev/dc.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/dc.c unix-v7-c99/dev/dc.c || true
```

Expect:

```

```

### dev/dh.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/dh.c unix-v7-c99/dev/dh.c || true
```

Expect:

```

```

### dev/dhdm.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/dhdm.c unix-v7-c99/dev/dhdm.c || true
```

Expect:

```

```

### dev/dhfdm.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/dhfdm.c unix-v7-c99/dev/dhfdm.c || true
```

Expect:

```

```

### dev/dkleave.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/dkleave.c unix-v7-c99/dev/dkleave.c || true
```

Expect:

```

```

### dev/dn.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/dn.c unix-v7-c99/dev/dn.c || true
```

Expect:

```

```

### dev/dsort.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/dsort.c unix-v7-c99/dev/dsort.c || true
```

Expect:

```

```

### dev/du.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/du.c unix-v7-c99/dev/du.c || true
```

Expect:

```

```

### dev/dz.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/dz.c unix-v7-c99/dev/dz.c || true
```

Expect:

```

```

### dev/hp.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/hp.c unix-v7-c99/dev/hp.c || true
```

Expect:

```

```

### dev/ht.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/ht.c unix-v7-c99/dev/ht.c || true
```

Expect:

```

```

### dev/kl.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/kl.c unix-v7-c99/dev/kl.c || true
```

Expect:

```

```

### dev/mem.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/mem.c unix-v7-c99/dev/mem.c || true
```

Expect:

```

```

### dev/mx1.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/mx1.c unix-v7-c99/dev/mx1.c || true
```

Expect:

```

```

### dev/mx2.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/mx2.c unix-v7-c99/dev/mx2.c || true
```

Expect:

```

```

### dev/partab.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/partab.c unix-v7-c99/dev/partab.c || true
```

Expect:

```

```

### dev/pk0.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/pk0.c unix-v7-c99/dev/pk0.c || true
```

Expect:

```

```

### dev/pk1.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/pk1.c unix-v7-c99/dev/pk1.c || true
```

Expect:

```

```

### dev/pk2.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/pk2.c unix-v7-c99/dev/pk2.c || true
```

Expect:

```

```

### dev/pk3.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/pk3.c unix-v7-c99/dev/pk3.c || true
```

Expect:

```

```

### dev/rf.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/rf.c unix-v7-c99/dev/rf.c || true
```

Expect:

```

```

### dev/rk.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/rk.c unix-v7-c99/dev/rk.c || true
```

Expect:

```

```

### dev/rl.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/rl.c unix-v7-c99/dev/rl.c || true
```

Expect:

```

```

### dev/rp.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/rp.c unix-v7-c99/dev/rp.c || true
```

Expect:

```

```

### dev/sys.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/sys.c unix-v7-c99/dev/sys.c || true
```

Expect:

```

```

### dev/tc.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/tc.c unix-v7-c99/dev/tc.c || true
```

Expect:

```

```

### dev/tm.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/tm.c unix-v7-c99/dev/tm.c || true
```

Expect:

```

```

### dev/tty.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/tty.c unix-v7-c99/dev/tty.c || true
```

Expect:

```

```

### dev/vp.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/vp.c unix-v7-c99/dev/vp.c || true
```

Expect:

```

```

### dev/vs.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/vs.c unix-v7-c99/dev/vs.c || true
```

Expect:

```

```

### cmd/sh/blok.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/blok.c unix-v7-c99/cmd/sh/blok.c || true
```

Expect:

```

```

### cmd/sh/brkincr.h

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/brkincr.h unix-v7-c99/cmd/sh/brkincr.h || true
```

Expect:

```

```

### cmd/sh/builtin.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/builtin.c unix-v7-c99/cmd/sh/builtin.c || true
```

Expect:

```

```

### cmd/sh/cmd.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/cmd.c unix-v7-c99/cmd/sh/cmd.c || true
```

Expect:

```

```

### cmd/sh/ctype.h

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/ctype.h unix-v7-c99/cmd/sh/ctype.h || true
```

Expect:

```

```

### cmd/sh/dup.h

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/dup.h unix-v7-c99/cmd/sh/dup.h || true
```

Expect:

```

```

### cmd/sh/error.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/error.c unix-v7-c99/cmd/sh/error.c || true
```

Expect:

```

```

### cmd/sh/fault.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/fault.c unix-v7-c99/cmd/sh/fault.c || true
```

Expect:

```

```

### cmd/sh/io.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/io.c unix-v7-c99/cmd/sh/io.c || true
```

Expect:

```

```

### cmd/sh/mac.h

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/mac.h unix-v7-c99/cmd/sh/mac.h || true
```

Expect:

```
10c10
< #define LOCAL	static
---
> #define LOCAL
```

### cmd/sh/macro.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/macro.c unix-v7-c99/cmd/sh/macro.c || true
```

Expect:

```

```

### cmd/sh/main.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/main.c unix-v7-c99/cmd/sh/main.c || true
```

Expect:

```

```

### cmd/sh/name.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/name.c unix-v7-c99/cmd/sh/name.c || true
```

Expect:

```

```

### cmd/sh/name.h

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/name.h unix-v7-c99/cmd/sh/name.h || true
```

Expect:

```

```

### cmd/sh/print.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/print.c unix-v7-c99/cmd/sh/print.c || true
```

Expect:

```

```

### cmd/sh/setbrk.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/setbrk.c unix-v7-c99/cmd/sh/setbrk.c || true
```

Expect:

```

```

### cmd/sh/stak.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/stak.c unix-v7-c99/cmd/sh/stak.c || true
```

Expect:

```

```

### cmd/sh/stak.h

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/stak.h unix-v7-c99/cmd/sh/stak.h || true
```

Expect:

```

```

### cmd/sh/string.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/string.c unix-v7-c99/cmd/sh/string.c || true
```

Expect:

```

```

### cmd/sh/sym.h

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/sym.h unix-v7-c99/cmd/sh/sym.h || true
```

Expect:

```

```

### cmd/sh/timeout.h

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/timeout.h unix-v7-c99/cmd/sh/timeout.h || true
```

Expect:

```

```

### conf/c.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/conf/c.c unix-v7-c99/conf/c.c || true
```

Expect:

```

```

### include/execargs.h

Local test:

```
diff unix-v7-c99/v7/usr/include/execargs.h unix-v7-c99/include/execargs.h || true
```

Expect:

```
1c1
< char **execargs = (char**)(-2);
---
> char **execargs = (char **)(-2);
```

### include/utmp.h

Local test:

```
diff unix-v7-c99/v7/usr/include/utmp.h unix-v7-c99/include/utmp.h || true
```

Expect:

```

```

### cmd/pwd.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/pwd.c unix-v7-c99/cmd/pwd.c || true
```

Expect:

```
17c17,21
< main()
---
> void prname(void);
> void cat(void);
> 
> int
> main(void)
38c42
< 				if (read(file, (char *)&dir, sizeof(dir)) < sizeof(dir)) {
---
> 				if (read(file, (char *)&dir, sizeof(dir)) < (int)sizeof(dir)) {
45c49
< 				if(read(file, (char *)&dir, sizeof(dir)) < sizeof(dir)) {
---
> 				if(read(file, (char *)&dir, sizeof(dir)) < (int)sizeof(dir)) {
56c60,61
< prname()
---
> void
> prname(void)
66c71,72
< cat()
---
> void
> cat(void)
68c74
< 	register i, j;
---
> 	register int i, j;
```

### cmd/cal.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/cal.c unix-v7-c99/cmd/cal.c || true
```

Expect:

```
10,11c10,17
< main(argc, argv)
< char *argv[];
---
> int printf(char *fmt, ...);
> void exit(int n);
> int number(char *str);
> void pstr(char *str, int n);
> void cal(int m, int y, char *p, int w);
> int jan1(int yr);
> int
> main(int argc, char *argv[])
13c19
< 	register y, i, j;
---
> 	register int y, i, j;
71,72c77,78
< number(str)
< char *str;
---
> int
> number(char *str)
74c80
< 	register n, c;
---
> 	register int n, c;
87,88c93,94
< pstr(str, n)
< char *str;
---
> void
> pstr(char *str, int n)
90c96
< 	register i;
---
> 	register int i;
113,114c119,120
< cal(m, y, p, w)
< char *p;
---
> void
> cal(int m, int y, char *p, int w)
116c122
< 	register d, i;
---
> 	register int d, i;
173c179,180
< jan1(yr)
---
> int
> jan1(int yr)
175c182
< 	register y, d;
---
> 	register int y, d;
```

### cmd/grep.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/grep.c unix-v7-c99/cmd/grep.c || true
```

Expect:

```
59,60c59,66
< main(argc, argv)
< char **argv;
---
> void compile(char *astr);
> void execute(char *file);
> int advance(register char *lp, register char *ep);
> void succeed(char *f);
> int ecmp(char *a, char *b, int count);
> void errexit(char *s, char *f);
> int
> main(int argc, char *argv[])
145,146c151,152
< compile(astr)
< char *astr;
---
> void
> compile(char *astr)
148c154
< 	register c;
---
> 	register int c;
262,263c268,269
< execute(file)
< char *file;
---
> void
> execute(char *file)
266c272
< 	register c;
---
> 	register int c;
324,325c330,331
< advance(lp, ep)
< register char *lp, *ep;
---
> int
> advance(register char *lp, register char *ep)
439,440c445,446
< succeed(f)
< char *f;
---
> void
> succeed(char *f)
464,465c470,471
< ecmp(a, b, count)
< char	*a, *b;
---
> int
> ecmp(char *a, char *b, int count)
467c473
< 	register cc = count;
---
> 	register int cc = count;
473,474c479,480
< errexit(s, f)
< char *s, *f;
---
> void
> errexit(char *s, char *f)
```

### cmd/cp.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/cp.c unix-v7-c99/cmd/cp.c || true
```

Expect:

```
12,13c12,14
< main(argc, argv)
< char *argv[];
---
> int copy(char *from, char *to);
> int
> main(int argc, char *argv[])
15c16
< 	register i, r;
---
> 	register int i, r;
34,35c35,36
< copy(from, to)
< char *from, *to;
---
> int
> copy(char *from, char *to)
```
### cmd/mv.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/mv.c unix-v7-c99/cmd/mv.c || true
```

Expect:

```
20c20
< char	*sprintf();
---
> char	*sprintf(char *buf, char *fmt, ...);
21a22,25
> int	move(char *source, char *target);
> int	mvdir(char *source, char *target);
> int	check(char *spth, ino_t dinode);
> int	chkdot(char *s);
24,25c28,29
< main(argc, argv)
< register char *argv[];
---
> int
> main(int argc, register char *argv[])
27c31
< 	register i, r;
---
> 	register int i, r;
53,54c57,58
< move(source, target)
< char *source, *target;
---
> int
> move(char *source, char *target)
56c60
< 	register c, i;
---
> 	register int c, i;
122,123c126,127
< mvdir(source, target)
< char *source, *target;
---
> int
> mvdir(char *source, char *target)
126c130
< 	register i;
---
> 	register int i;
232c236
< 	register c;
---
> 	register int c;
259,261c263,264
< check(spth, dinode)
< char *spth;
< ino_t dinode;
---
> int
> check(char *spth, ino_t dinode)
278c281
< 		if (strlen(nspth) > MAXN-2-sizeof(DOTDOT)) {
---
> 		if (strlen(nspth) > (int)(MAXN-2-sizeof(DOTDOT))) {
288,289c291,292
< chkdot(s)
< register char *s;
---
> int
> chkdot(register char *s)
```

### cmd/chmod.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/chmod.c unix-v7-c99/cmd/chmod.c || true
```

Expect:

```
22a23,27
> unsigned newmode(unsigned nm);
> int abs(void);
> int who(void);
> int what(void);
> int where(int om);
24,25c29,30
< main(argc,argv)
< char **argv;
---
> int
> main(int argc, char **argv)
27c32
< 	register i;
---
> 	register int i;
55,56c60,61
< newmode(nm)
< unsigned nm;
---
> unsigned
> newmode(unsigned nm)
58c63
< 	register o, m, b;
---
> 	register int o, m, b;
88c93,94
< abs()
---
> int
> abs(void)
90c96
< 	register c, i;
---
> 	register int c, i;
99c105,106
< who()
---
> int
> who(void)
101c108
< 	register m;
---
> 	register int m;
125c132,133
< what()
---
> int
> what(void)
136,137c144,145
< where(om)
< register om;
---
> int
> where(int om)
139c147
< 	register m;
---
> 	register int m;
```

### cmd/chown.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/chown.c unix-v7-c99/cmd/chown.c || true
```

Expect:

```
14a15
> int	isnumber(char *s);
16,17c17,18
< main(argc, argv)
< char *argv[];
---
> int
> main(int argc, char *argv[])
19c20
< 	register c;
---
> 	register int c;
46,47c47,48
< isnumber(s)
< char *s;
---
> int
> isnumber(char *s)
49c50
< 	register c;
---
> 	register int c;
```

### cmd/chgrp.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/chgrp.c unix-v7-c99/cmd/chgrp.c || true
```

Expect:

```
14a15
> int	isnumber(char *s);
16,17c17,18
< main(argc, argv)
< char *argv[];
---
> int
> main(int argc, char *argv[])
19c20
< 	register c;
---
> 	register int c;
44,45c45,46
< isnumber(s)
< char *s;
---
> int
> isnumber(char *s)
47c48
< 	register c;
---
> 	register int c;
```

### cmd/sleep.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sleep.c unix-v7-c99/cmd/sleep.c || true
```

Expect:

```
1,2c1,3
< main(argc, argv)
< char **argv;
---
> #include <stdio.h>
> int
> main(int argc, char **argv)
```

### cmd/touch.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/touch.c unix-v7-c99/cmd/touch.c || true
```

Expect:

```
2a3
> void touch(int force, char *name);
4,6c5,6
< main(argc,argv)
< int argc;
< char *argv[];
---
> int
> main(int argc, char *argv[])
25,27c25,26
< touch(force, name)
< int force;
< char *name;
---
> void
> touch(int force, char *name)
```

### cmd/tr.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/tr.c unix-v7-c99/cmd/tr.c || true
```

Expect:

```
11a12,13
> int	next(struct string *s);
> int	nextc(struct string *s);
13,14c15,16
< main(argc,argv)
< char **argv;
---
> int
> main(int argc, char **argv)
16c18
< 	register i;
---
> 	register int i;
18c20
< 	register c, d;
---
> 	register int c, d;
88,89c90,91
< next(s)
< struct string *s;
---
> int
> next(struct string *s)
114,115c116,117
< nextc(s)
< struct string *s;
---
> int
> nextc(struct string *s)
117c119
< 	register c, i, n;
---
> 	register int c, i, n;
```
### cmd/du.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/du.c unix-v7-c99/cmd/du.c || true
```

Expect:

```
21,22c21,22
< main(argc, argv)
< char **argv;
---
> int
> main(int argc, char **argv)
24c24
< 	register	i = 1;
---
> 	register int	i = 1;
81c81
< 		static linked = 0;
---
> 		static int linked = 0;
```

### cmd/split.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/split.c unix-v7-c99/cmd/split.c || true
```

Expect:

```
10a11,13
> int atoi(char *s);
> void exit(int n);
> int
11a15
> int argc;
14c18
< 	register i, c, f;
---
> 	register int i, c, f;
56c60
< 	for(i=0; i<count; i++)
---
> 	for(i=0; (unsigned)i<count; i++)
```

### cmd/tsort.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/tsort.c unix-v7-c99/cmd/tsort.c || true
```

Expect:

```
8a9
> #define index tindex
32a34,39
> int present(struct nodelist *i, struct nodelist *j);
> int anypred(struct nodelist *i);
> int cmp(char *s, char *t);
> void error(char *s, char *t);
> void note(char *s, char *t);
> void exit(int n);
37a45
> int
38a47
> int argc;
85a95
> int
97a108
> int
132a144
> int
144a157
> void
151a165
> void
174c188
< 				error("error 1");
---
> 				error("error 1",empty);
185c199
< 				error("error 2");
---
> 				error("error 2",empty);
```

### cmd/file.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/file.c unix-v7-c99/cmd/file.c || true
```

Expect:

```
22a23,33
> void type(char *file);
> int lookup(char *tab[]);
> int ccom(void);
> int ascom(void);
> int english(char *bp, int n);
> void exit(int n);
> #undef major
> #undef minor
> #define major(x)	(((x)>>8)&0377)
> #define minor(x)	((x)&0377)
> int
23a35
> int argc;
55a68
> void
238c251
< 		/*.... */
---
> 		.... */
241a255
> int
259a274
> int
274a290
> int
283a300
> int
285a303
> int n;
```

### cmd/join.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/join.c unix-v7-c99/cmd/join.c || true
```

Expect:

```
24a25,31
> int input(int n);
> void output(int on1, int on2);
> void error(char *s1, char *s2, char *s3, char *s4, char *s5);
> int cmp(char *s1, char *s2);
> int atoi(char *s);
> void exit(int n);
> int
25a33
> int argc;
88c96
< 		error("usage: join [-j1 x -j2 y] [-o list] file1 file2");
---
> 		error("usage: join [-j1 x -j2 y] [-o list] file1 file2", 0, 0, 0, 0);
96c104
< 		error("can't open %s", argv[1]);
---
> 		error("can't open %s", argv[1], 0, 0, 0);
98c106
< 		error("can't open %s", argv[2]);
---
> 		error("can't open %s", argv[2], 0, 0, 0);
141a150
> int
142a152
> int n;
169a180
> void
200a212
> void
202c214
< char *s1;
---
> char *s1, *s2, *s3, *s4, *s5;
209a222
> int
```
### cmd/pr.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/pr.c unix-v7-c99/cmd/pr.c || true
```

Expect:

```
43,45c43,55
< 
< main(argc, argv)
< char **argv;
---
> void	done(void);
> void	fixtty(void);
> void	print(char *fp, char **argp);
> void	mopen(char **ap);
> void	putpage(void);
> void	nexbuf(void);
> int	tpgetc(int ai);
> int	pgetc(int i);
> void	put(int ac);
> void	putcp(int c);
> void	onintr(void);
> int
> main(int argc, char **argv)
48,49d57
< 	int onintr();
< 
52c60
< 		signal(SIGINT, onintr);
---
> 		signal(SIGINT, (int)onintr);
107c115,116
< done()
---
> void
> done(void)
115c124,125
< onintr()
---
> void
> onintr(void)
123c133,134
< fixtty()
---
> void
> fixtty(void)
135,137c146,147
< print(fp, argp)
< char *fp;
< char **argp;
---
> void
> print(char *fp, char **argp)
139d148
< 	extern char *sprintf();
141c150
< 	register sncol;
---
> 	register int sncol;
218,219c227,228
< mopen(ap)
< char **ap;
---
> void
> mopen(char **ap)
238c247,248
< putpage()
---
> void
> putpage(void)
282c292,293
< nexbuf()
---
> void
> nexbuf(void)
305c316,317
< tpgetc(ai)
---
> int
> tpgetc(int ai)
340c352,353
< pgetc(i)
---
> int
> pgetc(int i)
372c385,386
< put(ac)
---
> void
> put(int ac)
418c432,433
< putcp(c)
---
> void
> putcp(int c)
```

### cmd/dd.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/dd.c unix-v7-c99/cmd/dd.c || true
```

Expect:

```
37a38,47
> void	flsh(void);
> int	match(char *s);
> int	number(int big);
> void	cnull(int cc);
> void	null(int c);
> void	ascii(int cc);
> void	ebcdic(int cc);
> void	ibm(int cc);
> void	term(void);
> void	stats(void);
142a153
> int
147c158
< 	int (*conv)();
---
> 	void (*conv)();
149,150c160
< 	register c;
< 	int ebcdic(), ibm(), ascii(), null(), cnull(), term();
---
> 	register int c;
281c291
< 		signal(SIGINT, term);
---
> 		signal(SIGINT, (int)term);
345c355,356
< flsh()
---
> void
> flsh(void)
347c358
< 	register c;
---
> 	register int c;
362,363c373,374
< match(s)
< char *s;
---
> int
> match(char *s)
380c391,392
< number(big)
---
> int
> number(int big)
419c431,432
< cnull(cc)
---
> void
> cnull(int cc)
421c434
< 	register c;
---
> 	register int c;
431c444,445
< null(c)
---
> void
> null(int c)
442c456,457
< ascii(cc)
---
> void
> ascii(int cc)
444c459
< 	register c;
---
> 	register int c;
469c484,485
< ebcdic(cc)
---
> void
> ebcdic(int cc)
471c487
< 	register c;
---
> 	register int c;
498c514,515
< ibm(cc)
---
> void
> ibm(int cc)
500c517
< 	register c;
---
> 	register int c;
527c544,545
< term()
---
> void
> term(void)
534c552,553
< stats()
---
> void
> stats(void)
```

### cmd/diff.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/diff.c unix-v7-c99/cmd/diff.c || true
```

Expect:

```
107a108,129
> void	done(void);
> char	*talloc(int n);
> char	*ralloc(char *p, int n);
> void	noroom(void);
> void	sort(struct line *a, int n);
> void	unsort(struct line *f, int l, int *b);
> void	filename(char **pa1, char **pa2);
> void	prepare(int i, char *arg);
> void	prune(void);
> void	equiv(struct line *a, int n, struct line *b, int m, int *c);
> int	stone(int *a, int n, int *b, int *c);
> int	newcand(int x, int y, int pred);
> int	search(int *c, int k, int y);
> void	unravel(int p);
> void	check(char **argv);
> int	skipline(int f);
> void	output(char **argv);
> void	change(int a, int b, int c, int d);
> void	range(int a, int b, char *separator);
> void	fetch(long *f, int a, int b, FILE *lb, char *s);
> int	readhash(FILE *f);
> void	mesg(char *s, char *t);
109c131,132
< done()
---
> void
> done(void)
115c138
< char *talloc(n)
---
> char *talloc(int n)
122a146
> 	return(NULL);
125,126c149
< char *ralloc(p,n)	/*compacting reallocation */
< char *p;
---
> char *ralloc(char *p, int n)	/*compacting reallocation */
139c162,163
< noroom()
---
> void
> noroom(void)
145,146c169,170
< sort(a,n)	/*shellsort CACM #201*/
< struct line *a;
---
> void
> sort(struct line *a, int n)	/*shellsort CACM #201*/
177,179c201,202
< unsort(f, l, b)
< struct line *f;
< int *b;
---
> void
> unsort(struct line *f, int l, int *b)
191,192c214,215
< filename(pa1, pa2)
< char **pa1, **pa2;
---
> void
> filename(char **pa1, char **pa2)
210,213c233,236
< 		signal(SIGHUP,done);
< 		signal(SIGINT,done);
< 		signal(SIGPIPE,done);
< 		signal(SIGTERM,done);
---
> 		signal(SIGHUP,(int)done);
> 		signal(SIGINT,(int)done);
> 		signal(SIGPIPE,(int)done);
> 		signal(SIGTERM,(int)done);
225,226c248,249
< prepare(i, arg)
< char *arg;
---
> void
> prepare(int i, char *arg)
229c252
< 	register j,h;
---
> 	register int j,h;
244c267,268
< prune()
---
> void
> prune(void)
246c270
< 	register i,j;
---
> 	register int i,j;
261,263c285,286
< equiv(a,n,b,m,c)
< struct line *a, *b;
< int *c;
---
> void
> equiv(struct line *a, int n, struct line *b, int m, int *c)
289,290c312,313
< main(argc, argv)
< char **argv;
---
> int
> main(int argc, char **argv)
358,361c381,382
< stone(a,n,b,c)
< int *a;
< int *b;
< int *c;
---
> int
> stone(int *a, int n, int *b, int *c)
399c420,421
< newcand(x,y,pred)
---
> int
> newcand(int x, int y, int pred)
410,411c432,433
< search(c, k, y)
< int *c;
---
> int
> search(int *c, int k, int y)
431c453,454
< unravel(p)
---
> void
> unravel(int p)
448,449c471,472
< check(argv)
< char **argv;
---
> void
> check(char **argv)
512c535,536
< skipline(f)
---
> int
> skipline(int f)
514c538
< 	register i;
---
> 	register int i;
519,520c543,544
< output(argv)
< char **argv;
---
> void
> output(char **argv)
551c575,576
< change(a,b,c,d)
---
> void
> change(int a, int b, int c, int d)
572,573c597,598
< range(a,b,separator)
< char *separator;
---
> void
> range(int a, int b, char *separator)
581,584c606,607
< fetch(f,a,b,lb,s)
< long *f;
< FILE *lb;
< char *s;
---
> void
> fetch(long *f, int a, int b, FILE *lb, char *s)
602,603c625,626
< readhash(f)
< FILE *f;
---
> int
> readhash(FILE *f)
607,608c630,631
< 	register space;
< 	register t;
---
> 	register int space;
> 	register int t;
641,642c664,665
< mesg(s,t)
< char *s, *t;
---
> void
> mesg(char *s, char *t)
```

### cmd/write.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/write.c unix-v7-c99/cmd/write.c || true
```

Expect:

```
24a25,26
> void	ex(char *bp);
> void	sigs(int sig);
27,28c29,30
< main(argc, argv)
< char *argv[];
---
> int
> main(int argc, char *argv[])
31c33
< 	register i;
---
> 	register int i;
106c108
< 	signal(SIGALRM, timout);
---
> 	signal(SIGALRM, (int)timout);
115c117
< 	sigs(eof);
---
> 	sigs((int)eof);
140c142,143
< timout()
---
> int
> timout(void)
144a148
> 	return(0);
147c151,152
< eof()
---
> int
> eof(void)
151a157
> 	return(0);
154,155c160,161
< ex(bp)
< char *bp;
---
> void
> ex(char *bp)
157c163
< 	register i;
---
> 	register int i;
166c172
< 		sigs((int (*)())0);
---
> 		sigs(0);
174c180
< 	sigs(eof);
---
> 	sigs((int)eof);
177,178c183,184
< sigs(sig)
< int (*sig)();
---
> void
> sigs(int sig)
180c186
< 	register i;
---
> 	register int i;
```
### cmd/dcheck.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/dcheck.c unix-v7-c99/cmd/dcheck.c || true
```

Expect:

```
29a30,33
> int	check(char *file);
> int	pass1(struct dinode *ip);
> int	pass2(struct dinode *ip);
> int	bread(daddr_t bno, char *buf, int cnt);
31a36
> int	l3tol(long *lp, char *cp, int n);
32a38
> int
33a40
> int argc;
36c43
< 	register i;
---
> 	register int i;
64a72
> int
68,69c76,77
< 	register i;
< 	register j;
---
> 	register int i;
> 	register int j;
75c83
< 		return;
---
> 			return(0);
91c99
< 	for (i=0; i<=nfiles; i++)
---
> 	for (i=0; i<=(int)nfiles; i++)
117a126
> 	return(0);
119a129
> int
126c136
< 	register i, j;
---
> 	register int i, j;
132c142
< 		return;
---
> 		return(0);
142c152
< 		for(j=0; j<NDIR; j++) {
---
> 		for(j=0; j<(int)NDIR; j++) {
164a175
> 	return(0);
166a178
> int
170c182
< 	register i;
---
> 	register int i;
174c186
< 		return;
---
> 		return(0);
176c188
< 		return;
---
> 		return(0);
178c190
< 		return;
---
> 		return(0);
184a197
> 	return(0);
186a200
> int
189a204
> int cnt;
191c206
< 	register i;
---
> 	register int i;
198a214
> 	return(0);
203a220
> int i;
210c227
< 	if(i > NINDIR) {
---
> 	if(i > (int)NINDIR) {
```

### cmd/icheck.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/icheck.c unix-v7-c99/cmd/icheck.c || true
```

Expect:

```
42a43,51
> int	check(char *file);
> int	pass1(struct dinode *ip);
> int	chk(daddr_t bno, char *s);
> int	duped(daddr_t bno);
> int	bfree(daddr_t bno);
> int	bread(daddr_t bno, char *buf, int cnt);
> int	bwrite(daddr_t bno, char *buf);
> int	makefree(void);
> int	l3tol(long *lp, char *cp, int n);
46a56
> int
47a58
> int argc;
50c61
< 	register i;
---
> 	register int i;
100a112
> int
104c116
< 	register i, j;
---
> 	register int i, j;
113c125
< 		return;
---
> 		return(0);
134c146
< 	if (n != (unsigned)n) {
---
> 	if (n != (long)(unsigned)n) {
149c161
< 	for(i=0; i<(unsigned)n; i++)
---
> 	for(i=0; i<(int)(unsigned)n; i++)
174c186
< 		return;
---
> 		return(0);
215a228
> 	return(0);
217a231
> int
224c238
< 	register i, j;
---
> 	register int i, j;
230c244
< 		return;
---
> 		return(0);
234c248
< 		return;
---
> 		return(0);
238c252
< 		return;
---
> 		return(0);
246c260
< 		return;
---
> 		return(0);
261c275
< 		for(j=0; j<NINDIR; j++) {
---
> 		for(j=0; j<(int)NINDIR; j++) {
273c287
< 			for(k=0; k<NINDIR; k++) {
---
> 			for(k=0; k<(int)NINDIR; k++) {
285c299
< 				for(l=0; l<NINDIR; l++)
---
> 				for(l=0; l<(int)NINDIR; l++)
292a307
> 	return(0);
294a310
> int
299c315
< 	register n;
---
> 	register int n;
314a331
> int
319c336
< 	register m, n;
---
> 	register int m, n;
355c372
< 		sblock.s_nfree = buf.df_nfree;
---
> 		sblock.s_nfree = buf.fb.df_nfree;
363c380
< 			sblock.s_free[i] = buf.df_free[i];
---
> 			sblock.s_free[i] = buf.fb.df_free[i];
367a385
> int
381c399
< 		buf.df_nfree = sblock.s_nfree;
---
> 		buf.fb.df_nfree = sblock.s_nfree;
383c401
< 			buf.df_free[i] = sblock.s_free[i];
---
> 			buf.fb.df_free[i] = sblock.s_free[i];
388a407
> 	return(0);
390a410
> int
393a414
> int cnt;
395c416
< 	register i;
---
> 	register int i;
406a428
> 	return(0);
408a431
> int
416a440
> 	return(0);
418a443
> int
423c448
< 	register i, j;
---
> 	register int i, j;
474c499
< 	return;
---
> 	return(0);
```

### cmd/ncheck.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/ncheck.c unix-v7-c99/cmd/ncheck.c || true
```

Expect:

```
39a40,47
> int	check(char *file);
> int	pass1(struct dinode *ip);
> int	pass2(struct dinode *ip);
> int	pass3(struct dinode *ip);
> int	dotname(struct direct *dp);
> int	pname(int i, int lev);
> int	bread(daddr_t bno, char *buf, int cnt);
> int	l3tol(long *lp, char *cp, int n);
40a49
> int
41a51
> int argc;
44c54
< 	register i;
---
> 	register int i;
80a91
> int
84c95
< 	register i, j;
---
> 	register int i, j;
91c102
< 		return;
---
> 		return(0);
134a146
> 	return(0);
136a149
> int
142c155
< 			return;
---
> 			return(0);
146c159
< 			return;
---
> 			return(0);
148a162
> 	return(0);
150a165
> int
157c172
< 	register i, j;
---
> 	register int i, j;
164c179
< 		return;
---
> 		return(0);
174c189
< 		for(j=0; j<NDIR; j++) {
---
> 		for(j=0; j<(int)NDIR; j++) {
191a207
> 	return(0);
193a210
> int
200c217
< 	register i, j;
---
> 	register int i, j;
206c223
< 		return;
---
> 		return(0);
216c233
< 		for(j=0; j<NDIR; j++) {
---
> 		for(j=0; j<(int)NDIR; j++) {
240a258
> 	return(0);
242a261
> int
252a272
> int
254c274,275
< ino_t i;
---
> int i;
> int lev;
259c280
< 		return;
---
> 		return(0);
262c283
< 		return;
---
> 		return(0);
266c287
< 		return;
---
> 		return(0);
269a291
> 	return(0);
274a297
> int ef;
293a317
> int
296a321
> int cnt;
298c323
< 	register i;
---
> 	register int i;
305a331
> 	return(0);
309a336
> int i;
316c343
< 	if(i > NINDIR) {
---
> 	if(i > (int)NINDIR) {
```
### cmd/find.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/find.c unix-v7-c99/cmd/find.c || true
```

Expect:

```
2a3
> #define	ctime	find_ctime
42a44,56
> int	pclose(FILE *f);
> int	pr();
> int	descend(char *name, char *fname, struct anode *exlist);
> int	cpio(void);
> int	getunum(char *f, char *s);
> int	gmatch(char *s, char *p);
> int	scomp(int a, int b, int s);
> int	doex(int com);
> int	bwrite(short *rp, int c);
> int	chgreel(int x, int fl);
> int	amatch(char *s, char *p);
> int	umatch(char *s, char *p);
> int
43a58
> int argc;
242a258
> 	return(0);
255c271
< 	static strikes = 0;
---
> 	static int strikes = 0;
269a286
> int
274a292
> int
279a298
> int
284a304
> int
289a310
> int
294a316
> int
299a322
> int
304a328
> int
309a334
> int
314a340
> int
319a346
> int
324a352
> int
329a358
> int
334a364
> int
338c368
< 	register i;
---
> 	register int i;
341a372
> int
346a378
> int
352a385
> int
382a416
> int
400c434
< 	register ifile, ct;
---
> 	register int ifile, ct;
402c436
< 	register i;
---
> 	register int i;
421c455
< 		return;
---
> 		return(0);
425c459
< 		return;
---
> 		return(0);
430c464
< 		return;
---
> 		return(0);
440c474
< 	return;
---
> 	return(0);
441a476
> int
447a483
> int
449,450c485,486
< register a, b;
< register char s;
---
> register int a, b;
> register int s;
458a495
> int
459a497
> int com;
461c499
< 	register np;
---
> 	register int np;
464c502
< 	static ccode;
---
> 	static int ccode;
477c515
< 		execvp(nargv[0], nargv, np);
---
> 		execvp(nargv[0], nargv);
482a521
> int
484c523
< 	register i;
---
> 	register int i;
486c525
< 	register c;
---
> 	register int c;
514a554
> int
611a652
> int
618a660
> int
622c664
< 	register cc;
---
> 	register int cc;
660a703
> int
669a713
> int
672c716
< register c;
---
> register int c;
691a736
> 	return(0);
692a738
> int
693a740
> int x, fl;
695c742
< 	register f;
---
> 	register int f;
718a766
> int
722a771
> 	return(0);
```

### cmd/sort.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sort.c unix-v7-c99/cmd/sort.c || true
```

Expect:

```
5a6
> #define	qsort	sort_qsort
168a170,185
> struct	merg;
> int	copyproto(void);
> int	field(char *s, int k);
> int	diag(char *s, char *t);
> int	safeoutfil(void);
> int	sort(void);
> int	newfile(void);
> int	merge(int a, int b);
> int	oldfile(void);
> int	cant(char *f);
> int	rline(struct merg *mp);
> int	disorder(char *s, char *t);
> int	term(void);
> int	blank(int c);
> int	number(char **ppa);
> int	qsort(char **a, char **l);
169a187
> int
170a189
> int argc;
173c192
< 	register a;
---
> 	register int a;
239a259
> 	ep = (char *)lspace + MEM;
262c282
< 	signal(SIGHUP, term);
---
> 	signal(SIGHUP, (int)term);
264,266c284,286
< 		signal(SIGINT, term);
< 	signal(SIGPIPE,term);
< 	signal(SIGTERM,term);
---
> 		signal(SIGINT, (int)term);
> 	signal(SIGPIPE,(int)term);
> 	signal(SIGTERM,(int)term);
284a305
> 	return(0);
286a308
> int
291c313
< 	register c;
---
> 	register int c;
341a364
> 	return(0);
349a373
> int
350a375
> int a, b;
354c379
< 	register	i;
---
> 	register int	i;
441a467
> 	return(0);
443a470
> int
450c477
< 	register c;
---
> 	register int c;
465a493
> int
473a502
> 	return(0);
475a505
> int
485a516
> 	return(0);
489a521
> int i;
502a535
> int
512a546
> 	return(0);
514a549
> int
521c556
< 		return;
---
> 		return(0);
523c558
< 		return;
---
> 		return(0);
530a566
> 	return(0);
532a569
> int
538a576
> 	return(0);
540a579
> int
547a587
> 	return(0);
549a590
> int
552c593
< 	register i;
---
> 	register int i;
562a604
> 	return(0);
564a607
> int
660a704
> int
680a725
> int j;
682c727
< 	register i;
---
> 	register int i;
724a770
> int
727c773
< 	register i;
---
> 	register int i;
732c778
< 	for(i=0; i<sizeof(proto)/sizeof(*p); i++)
---
> 	for(i=0; i<(int)(sizeof(proto)/sizeof(*p)); i++)
733a780
> 	return(0);
735a783
> int
737a786
> int k;
740c789
< 	register d;
---
> 	register int d;
746c795
< 			return;
---
> 			return(0);
795a845
> 	return(0);
797a848
> int
811a863
> int
812a865
> int c;
821a875
> int
836c890
< 		return;
---
> 		return(0);
```

### lib/crypt.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/crypt.c unix-v7-c99/lib/crypt.c || true
```

Expect:

```
49c49
< static	char	PC1_D[] {
---
> static	char	PC1_D[] = {
97,98c97,98
< setkey(key)
< char *key;
---
> void
> setkey(char *key)
100c100
< 	register i, j, k;
---
> 	register int i, j, k;
146c146
< static	char	e[] {
---
> static	char	e[] = {
162c162
< static	char	S[8][64] {
---
> static	char	S[8][64] = {
208c208
< static	char	P[] {
---
> static	char	P[] = {
235,236c235,236
< encrypt(block, edflag)
< char *block;
---
> void
> encrypt(char *block, int edflag)
239c239
< 	register t, j, k;
---
> 	register int t, j, k;
328c328
< 	register i, j, c;
---
> 	register int i, j, c;
```

### include/sys/param.h

Local test:

```
diff unix-v7-c99/v7/usr/include/sys/param.h unix-v7-c99/include/sys/param.h || true
```

Expect:

```
128a129
> #ifndef SYS_TYPES_H
131c132
< typedef	unsigned int	ino_t;
---
> typedef	unsigned short	ino_t;
135a137,138
> #define	SYS_TYPES_H
> #endif
```

### include/sys/inode.h

Local test:

```
diff unix-v7-c99/v7/usr/include/sys/inode.h unix-v7-c99/include/sys/inode.h || true
```

Expect:

```
14a15
> #ifndef GRP_H
51a53
> #endif
```

### h/smallparam.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/smallparam.h unix-v7-c99/h/smallparam.h || true
```

Expect:

```
131c131
< typedef	unsigned int	ino_t;
---
> typedef	unsigned short	ino_t;
```

### h/systm.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/systm.h unix-v7-c99/h/systm.h || true
```

Expect:

```
51c51
< struct inode *iget();
---
> struct inode *iget(dev_t dev, ino_t ino);
54c54
< struct inode *namei();
---
> struct inode *namei(int (*func)(void), int flag);
56c56
< struct buf *getblk();
---
> struct buf *getblk(dev_t dev, daddr_t blkno);
58,59c58,59
< struct buf *bread();
< struct buf *breada();
---
> struct buf *bread(dev_t dev, daddr_t blkno);
> struct buf *breada(dev_t dev, daddr_t blkno, daddr_t rablkno);
63c63
< int	uchar();
---
> int	uchar(void);
```

### h/types.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/types.h unix-v7-c99/h/types.h || true
```

Expect:

```
3c3
< typedef	unsigned int	ino_t;     	/* i-node number */
---
> typedef	unsigned short	ino_t;     	/* i-node number */
```

### sys/iget.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/iget.c unix-v7-c99/sys/iget.c || true
```

Expect:

```
11a12,34
> /* Stub prototypes - implementations live in v7stubs.c or other sys TUs. */
> extern void bcopy(caddr_t from, caddr_t to, unsigned int count);
> extern void brelse(struct buf *bp);
> extern void bdwrite(struct buf *bp);
> extern struct buf *bread(dev_t dev, daddr_t blkno);
> extern void free(dev_t dev, daddr_t bn);
> extern struct filsys *getfs(dev_t dev);
> extern struct inode *ialloc(dev_t dev);
> extern void ifree(dev_t dev, ino_t ino);
> extern void prele(struct inode *ip);
> extern void printf(char *fmt, ...);
> extern void panic(char *s);
> extern void sleep(caddr_t chan, int pri);
> extern int writei(struct inode *ip);
> 
> void iexpand(struct inode *ip, struct dinode *dp);
> void iput(struct inode *ip);
> void iupdat(struct inode *ip, time_t *ta, time_t *tm);
> void itrunc(struct inode *ip);
> void tloop(dev_t dev, daddr_t bn, int f1, int f2);
> struct inode *maknode(int mode);
> void wdir(struct inode *ip);
> 
30,32c53
< iget(dev, ino)
< dev_t dev;
< ino_t ino;
---
> iget(dev_t dev, ino_t ino)
75c96
< 	ip->i_un.i_lastr = 0;
---
> 	ip->i_lastr = 0;
92,94c113,114
< iexpand(ip, dp)
< register struct inode *ip;
< register struct dinode *dp;
---
> void
> iexpand(struct inode *ip, struct dinode *dp)
105c125
< 	p1 = (char *)ip->i_un.i_addr;
---
> 	p1 = (char *)ip->i_addr;
122,123c142,143
< iput(ip)
< register struct inode *ip;
---
> void
> iput(struct inode *ip)
149,151c169,170
< iupdat(ip, ta, tm)
< register struct inode *ip;
< time_t *ta, *tm;
---
> void
> iupdat(struct inode *ip, time_t *ta, time_t *tm)
175c194
< 		p2 = (char *)ip->i_un.i_addr;
---
> 		p2 = (char *)ip->i_addr;
204,205c223,224
< itrunc(ip)
< register struct inode *ip;
---
> void
> itrunc(struct inode *ip)
207c226
< 	register i;
---
> 	register int i;
216c235
< 		bn = ip->i_un.i_addr[i];
---
> 		bn = ip->i_addr[i];
219c238
< 		ip->i_un.i_addr[i] = (daddr_t)0;
---
> 		ip->i_addr[i] = (daddr_t)0;
242,244c261,262
< tloop(dev, bn, f1, f2)
< dev_t dev;
< daddr_t bn;
---
> void
> tloop(dev_t dev, daddr_t bn, int f1, int f2)
246c264
< 	register i;
---
> 	register int i;
280c298
< maknode(mode)
---
> maknode(int mode)
305,306c323,324
< wdir(ip)
< struct inode *ip;
---
> void
> wdir(struct inode *ip)
```

### sys/nami.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/nami.c unix-v7-c99/sys/nami.c || true
```

Expect:

```
8a9,19
> /* Stub prototypes - implementations live in v7stubs.c or other sys TUs. */
> extern void bcopy(caddr_t from, caddr_t to, unsigned int count);
> extern void brelse(struct buf *bp);
> extern struct buf *bread(dev_t dev, daddr_t blkno);
> extern int access(struct inode *ip, int mode);
> extern daddr_t bmap(struct inode *ip, daddr_t bn, int rwflg);
> extern int fubyte(caddr_t addr);
> extern void plock(struct inode *ip);
> extern void iput(struct inode *ip);
> extern struct inode *iget(dev_t dev, ino_t ino);
> 
21,22c32
< namei(func, flag)
< int (*func)();
---
> namei(int (*func)(void), int flag)
25c35
< 	register c;
---
> 	register int c;
206c216,217
< schar()
---
> int
> schar(void)
216c227,228
< uchar()
---
> int
> uchar(void)
218c230
< 	register c;
---
> 	register int c;
```

### dev/bio.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/bio.c unix-v7-c99/dev/bio.c || true
```

Expect:

```
8a9
> #include "../h/proto.h"
56,58c57
< bread(dev, blkno)
< dev_t dev;
< daddr_t blkno;
---
> bread(dev_t dev, daddr_t blkno)
84,86c83
< breada(dev, blkno, rablkno)
< dev_t dev;
< daddr_t blkno, rablkno;
---
> breada(dev_t dev, daddr_t blkno, daddr_t rablkno)
125,126c122,123
< bwrite(bp)
< register struct buf *bp;
---
> void
> bwrite(struct buf *bp)
128c125
< 	register flag;
---
> 	register int flag;
154,155c151,152
< bdwrite(bp)
< register struct buf *bp;
---
> void
> bdwrite(struct buf *bp)
171,172c168,169
< bawrite(bp)
< register struct buf *bp;
---
> void
> bawrite(struct buf *bp)
182,183c179,180
< brelse(bp)
< register struct buf *bp;
---
> void
> brelse(struct buf *bp)
186c183
< 	register s;
---
> 	register int s;
218,220c215,216
< incore(dev, blkno)
< dev_t dev;
< daddr_t blkno;
---
> int
> incore(dev_t dev, daddr_t blkno)
238,240c234
< getblk(dev, blkno)
< dev_t dev;
< daddr_t blkno;
---
> getblk(dev_t dev, daddr_t blkno)
245c239
< 	register i;
---
> 	register int i;
309c303
< geteblk()
---
> geteblk(void)
343,344c337,338
< iowait(bp)
< register struct buf *bp;
---
> void
> iowait(struct buf *bp)
358,359c352,353
< notavail(bp)
< register struct buf *bp;
---
> void
> notavail(struct buf *bp)
361c355
< 	register s;
---
> 	register int s;
374,375c368,369
< iodone(bp)
< register struct buf *bp;
---
> void
> iodone(struct buf *bp)
392,393c386,387
< clrbuf(bp)
< struct buf *bp;
---
> void
> clrbuf(struct buf *bp)
395,396c389,390
< 	register *p;
< 	register c;
---
> 	register int *p;
> 	register int c;
409,410c403,404
< swap(blkno, coreaddr, count, rdflg)
< register count;
---
> void
> swap(daddr_t blkno, int coreaddr, int count, int rdflg)
413c407
< 	register tcount;
---
> 	register int tcount;
456,457c450,451
< bflush(dev)
< dev_t dev;
---
> void
> bflush(dev_t dev)
484,486c478,479
< physio(strat, bp, dev, rw)
< register struct buf *bp;
< int (*strat)();
---
> void
> physio(int (*strat)(), struct buf *bp, dev_t dev, int rw)
515c508
< 	    && nb < 1024-u.u_ssize)
---
> 	    && nb < (int)(1024-u.u_ssize))
557,558c550,551
< geterror(bp)
< register struct buf *bp;
---
> void
> geterror(struct buf *bp)
```

### cmd/login.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/login.c unix-v7-c99/cmd/login.c || true
```

Expect:

```
25d24
< int	setpwent();
30a30
> void	showmotd(void);
32,33c32,33
< main(argc, argv)
< char **argv;
---
> int
> main(int argc, char **argv)
40,41c40,41
< 	signal(SIGQUIT, SIG_IGN);
< 	signal(SIGINT, SIG_IGN);
---
> 	signal(SIGQUIT, (int)SIG_IGN);
> 	signal(SIGINT, (int)SIG_IGN);
123,124c123,124
< 	signal(SIGQUIT, SIG_DFL);
< 	signal(SIGINT, SIG_DFL);
---
> 	signal(SIGQUIT, (int)SIG_DFL);
> 	signal(SIGINT, (int)SIG_DFL);
131c131,132
< catch()
---
> void
> catch(int sig)
133c134,135
< 	signal(SIGINT, SIG_IGN);
---
> 	(void)sig;
> 	signal(SIGINT, (int)SIG_IGN);
137c139,140
< showmotd()
---
> void
> showmotd(void)
140c143
< 	register c;
---
> 	register int c;
142c145
< 	signal(SIGINT, catch);
---
> 	signal(SIGINT, (int)catch);
148c151
< 	signal(SIGINT, SIG_IGN);
---
> 	signal(SIGINT, (int)SIG_IGN);
```

### cmd/ls.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/ls.c unix-v7-c99/cmd/ls.c || true
```

Expect:

```
45a46,51
> void	pentry(struct lbuf *ap);
> int	getname(int uid, char buf[]);
> void	pmode(int aflag);
> void	select(int *pairp);
> void	readdir(char *dir);
> int	compar(struct lbuf **pp1, struct lbuf **pp2);
49,50c55,56
< main(argc, argv)
< char *argv[];
---
> int
> main(int argc, char *argv[])
163,164c169,170
< pentry(ap)
< struct lbuf *ap;
---
> void
> pentry(struct lbuf *ap)
166,167c172
< 	struct { char dminor, dmajor;};
< 	register t;
---
> 	register int t;
203a209
> int
257c263,264
< pmode(aflag)
---
> void
> pmode(int aflag)
266,267c273,274
< select(pairp)
< register int *pairp;
---
> void
> select(register int *pairp)
297,298c304,305
< readdir(dir)
< char *dir;
---
> void
> readdir(char *dir)
329a337
> int argfl;
331d338
< 	extern char *malloc();
400,401c407,408
< compar(pp1, pp2)
< struct lbuf **pp1, **pp2;
---
> int
> compar(struct lbuf **pp1, struct lbuf **pp2)
```

### cmd/sh/args.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/args.c unix-v7-c99/cmd/sh/args.c || true
```

Expect:

```
12c12
< PROC STRING *copyargs();
---
> PROC DOLPTR	copyargs();
101c101
< LOCAL STRING *	copyargs(from, n)
---
> LOCAL DOLPTR	copyargs(from, n)
104c104
< 	REG STRING *	np=alloc(sizeof(STRING*)*n+3*BYTESPERWORD);
---
> 	REG DOLPTR	np=alloc(sizeof(STRING*)*n+3*BYTESPERWORD);
106c106
< 	REG STRING *	pp=np;
---
> 	REG STRING *	pp;
109,110c109,110
< 	np=np->dolarg;
< 	dolv=np;
---
> 	pp=np->dolarg;
> 	dolv=pp;
113,115c113,115
< 	DO *np++ = make(*fp++) OD
< 	*np++ = ENDARGS;
< 	return(pp);
---
> 	DO *pp++ = make(*fp++) OD
> 	*pp++ = ENDARGS;
> 	return(np);
```

### cmd/sh/ctype.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/ctype.c unix-v7-c99/cmd/sh/ctype.c || true
```

Expect:

```
12c12
< char	_ctype1[] {
---
> char	_ctype1[] = {
61c61
< char	_ctype2[] {
---
> char	_ctype2[] = {
```

### cmd/sh/defs.h

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/defs.h unix-v7-c99/cmd/sh/defs.h || true
```

Expect:

```
284c284
< address	end[];
---
> extern address	end[];
```

### cmd/sh/expand.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/expand.c unix-v7-c99/cmd/sh/expand.c || true
```

Expect:

```
185c185
< 	REG STRING	args;
---
> 	REG ARGPTR	args;
```

### cmd/sh/mode.h

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/mode.h unix-v7-c99/cmd/sh/mode.h || true
```

Expect:

```
46d45
< STRUCT sysnod	SYSTAB[];
55,56c54
< union { int _cheat;};
< #define Lcheat(a)	((a)._cheat)
---
> #define Lcheat(a)	(*(int *)&(a))
75,78d72
< /* for functions that do not return values */
< struct void {INT vvvvvvvv;};
< 
< 
113a108
> STRUCT sysnod	SYSTAB[];
117,118c112,164
< 	INT	tretyp;
< 	IOPTR	treio;
---
> 	union {
> 		struct {
> 			INT	tretyp;
> 			IOPTR	treio;
> 		};
> 		struct {
> 			INT	forktyp;
> 			IOPTR	forkio;
> 			TREPTR	forktre;
> 		};
> 		struct {
> 			INT	comtyp;
> 			IOPTR	comio;
> 			ARGPTR	comarg;
> 			ARGPTR	comset;
> 		};
> 		struct {
> 			INT	iftyp;
> 			TREPTR	iftre;
> 			TREPTR	thtre;
> 			TREPTR	eltre;
> 		};
> 		struct {
> 			INT	whtyp;
> 			TREPTR	whtre;
> 			TREPTR	dotre;
> 		};
> 		struct {
> 			INT	fortyp;
> 			TREPTR	fortre;
> 			STRING	fornam;
> 			COMPTR	forlst;
> 		};
> 		struct {
> 			INT	swtyp;
> 			STRING	swarg;
> 			REGPTR	swlst;
> 		};
> 		struct {
> 			INT	partyp;
> 			TREPTR	partre;
> 		};
> 		struct {
> 			INT	lsttyp;
> 			TREPTR	lstlef;
> 			TREPTR	lstrit;
> 		};
> 		struct {
> 			ARGPTR	regptr;
> 			TREPTR	regcom;
> 			REGPTR	regnxt;
> 		};
> 	};
```

### cmd/sh/msg.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/msg.c unix-v7-c99/cmd/sh/msg.c || true
```

Expect:

```
70c70
< SYSTAB reserved {
---
> SYSTAB reserved = {
89c89
< STRING	sysmsg[] {
---
> STRING	sysmsg[] = {
111c111
< SYSTAB	commands {
---
> SYSTAB	commands = {
```

### cmd/sh/service.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/service.c unix-v7-c99/cmd/sh/service.c || true
```

Expect:

```
343a344
> 	REG ARGPTR	arg;
358c359,360
< 		IF c=expand((argp=endstak(argp))->argval,0)
---
> 		arg=endstak(argp);
> 		IF c=expand(arg->argval,0)
361c363
< 			makearg(argp); count++;
---
> 			makearg(arg); count++;
```

### cmd/sh/word.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/word.c unix-v7-c99/cmd/sh/word.c || true
```

Expect:

```
20a21
> 	REG ARGPTR	arg;
42,43c43,44
< 		argp=endstak(argp);
< 		IF !letter(argp->argval[0]) THEN wdset=0 FI
---
> 		arg=endstak(argp);
> 		IF !letter(arg->argval[0]) THEN wdset=0 FI
46c47
< 		IF argp->argval[1]==0 ANDF (d=argp->argval[0], digit(d)) ANDF (c=='>' ORF c=='<')
---
> 		IF arg->argval[1]==0 ANDF (d=arg->argval[0], digit(d)) ANDF (c=='>' ORF c=='<')
49,50c50,51
< 			IF reserv==FALSE ORF (wdval=syslook(argp->argval,reserved))==0
< 			THEN	wdarg=argp; wdval=0;
---
> 			IF reserv==FALSE ORF (wdval=syslook(arg->argval,reserved))==0
> 			THEN	wdarg=arg; wdval=0;
```

### cmd/sh/xec.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/xec.c unix-v7-c99/cmd/sh/xec.c || true
```

Expect:

```
205c205
<                                                 int c, i
---
> 						int c, i;
```

### conf/putchar.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/putchar.c unix-v7-c99/conf/putchar.c || true
```

Expect:

```
1,4c1,3
< /*
<  * A subroutine version of the macro putchar
<  */
< #include <stdio.h>
---
> void putchar(char ch)
> {
>     long ret;
6c5,16
< #undef putchar
---
>     // syscall numbers for x86_64 Linux:
>     // write = 1
>     // fd 1 = stdout
>     __asm__ volatile (
>         "syscall"
>         : "=a"(ret)                  // output: return value in rax
>         : "a"(1),                    // rax = syscall number 1 (write)
>           "D"(1),                    // rdi = fd 1 (stdout)
>           "S"(&ch),                  // rsi = pointer to buffer
>           "d"(1)                     // rdx = length 1
>         : "rcx", "r11", "memory"
>     );
8,11c18
< putchar(c)
< register c;
< {
< 	putc(c, stdout);
---
>     return (ret == 1) ? c : -1;
```

### h/buf.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/buf.h unix-v7-c99/h/buf.h || true
```

Expect:

```
0a1,3
> #ifndef BUF_H
> #define BUF_H
> 
72a76,77
> 
> #endif
```

### h/dir.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/dir.h unix-v7-c99/h/dir.h || true
```

Expect:

```
0a1,3
> #ifndef DIR_H
> #define DIR_H
> 
8a12,13
> 
> #endif
```

### h/inode.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/inode.h unix-v7-c99/h/inode.h || true
```

Expect:

```
37c37
< 	union {
---
> 	union i_un {
41c41
< 		};
---
> 		} i_f;
45c45
< 		};
---
> 		} i_d;
47a48,52
> 
> #define	i_addr	i_un.i_f.i_addr
> #define	i_lastr	i_un.i_f.i_lastr
> #define	i_rdev	i_un.i_d.i_rdev
> #define	i_group	i_un.i_d.i_group
```

### h/map.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/map.h unix-v7-c99/h/map.h || true
```

Expect:

```
0a1,5
> #ifndef MAP_H
> #define MAP_H
> 
> #include "../h/param.h"
> 
7,8c12,15
< struct map coremap[CMAPSIZ];	/* space for core allocation */
< struct map swapmap[SMAPSIZ];	/* space for swap allocation */
---
> extern struct map coremap[CMAPSIZ];	/* space for core allocation */
> extern struct map swapmap[SMAPSIZ];	/* space for swap allocation */
> 
> #endif
```

### h/param.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/param.h unix-v7-c99/h/param.h || true
```

Expect:

```
0a1,3
> #ifndef PARAM_H
> #define PARAM_H
> 
131c134
< typedef	unsigned int	ino_t;
---
> typedef	unsigned short	ino_t;
144a148,149
> 
> #endif
```

### h/proc.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/proc.h unix-v7-c99/h/proc.h || true
```

Expect:

```
0a1,3
> #ifndef PROC_H
> #define PROC_H
> 
69a73,74
> 
> #endif
```

### h/user.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/user.h unix-v7-c99/h/user.h || true
```

Expect:

```
0a1,5
> #ifndef USER_H
> #define USER_H
> 
> #include "../h/dir.h"
> 
34,35c39,40
< 	union {				/* syscall return values */
< 		struct	{
---
> 	union ret {				/* syscall return values */
> 		struct r	{
38c43
< 		};
---
> 		} r;
135a141,142
> 
> #endif
```

### include/ctype.h

Local test:

```
diff unix-v7-c99/v7/usr/include/ctype.h unix-v7-c99/include/ctype.h || true
```

Expect:

```
1,24c1,7
< #define	_U	01
< #define	_L	02
< #define	_N	04
< #define	_S	010
< #define _P	020
< #define _C	040
< #define	_X	0100
< 
< extern	char	_ctype_[];	/* in /usr/src/libc/gen/ctype_.h */
< 
< #define	isalpha(c)	((_ctype_+1)[c]&(_U|_L))
< #define	isupper(c)	((_ctype_+1)[c]&_U)
< #define	islower(c)	((_ctype_+1)[c]&_L)
< #define	isdigit(c)	((_ctype_+1)[c]&_N)
< #define	isxdigit(c)	((_ctype_+1)[c]&(_N|_X))
< #define	isspace(c)	((_ctype_+1)[c]&_S)
< #define ispunct(c)	((_ctype_+1)[c]&_P)
< #define isalnum(c)	((_ctype_+1)[c]&(_U|_L|_N))
< #define isprint(c)	((_ctype_+1)[c]&(_P|_U|_L|_N))
< #define iscntrl(c)	((_ctype_+1)[c]&_C)
< #define isascii(c)	((unsigned)(c)<=0177)
< #define toupper(c)	((c)-'a'+'A')
< #define tolower(c)	((c)-'A'+'a')
< #define toascii(c)	((c)&0177)
---
> #define	isdigit(c)	((c)>='0'&&(c)<='9')
> #define	islower(c)	((c)>='a'&&(c)<='z')
> #define	isupper(c)	((c)>='A'&&(c)<='Z')
> #define	isalpha(c)	(islower(c)||isupper(c))
> #define	isalnum(c)	(isalpha(c)||isdigit(c))
> #define	isspace(c)	((c)==' '||(c)=='\t'||(c)=='\n'||(c)=='\r'||(c)=='\f')
> #define	toupper(c)	(islower(c)?(c)-'a'+'A':(c))
```

### include/errno.h

Local test:

```
diff unix-v7-c99/v7/usr/include/errno.h unix-v7-c99/include/errno.h || true
```

Expect:

```
2c2,4
<  * Error codes
---
>  * Error codes -- ported from v7/usr/include/errno.h.
>  * Numeric values are unchanged; these are the canonical V7 errnos
>  * the ported libc relies on.
3a6,7
> #ifndef ERRNO_H
> #define ERRNO_H
40a45,63
> 
> extern int errno;
> 
> /* Port-side accommodation: several command sources include
>  * <errno.h> and rely on it for the read/write/fstat/exit
>  * syscall prototypes (a warts-and-all C99 build needs explicit
>  * decls).  Kept here so we do not have to edit every
>  * not-yet-converted-from-K&R command. */
> struct stat;
> int	read(int, char *, int);
> int	write(int, char *, int);
> int	open(char *, int);
> int	close(int);
> long	lseek(int, long, int);
> int	fstat(int, struct stat *);
> int	strlen(char *);
> void	exit(int);
> 
> #endif
```

### include/grp.h

Local test:

```
diff unix-v7-c99/v7/usr/include/grp.h unix-v7-c99/include/grp.h || true
```

Expect:

```
0a1,2
> #ifndef GRP_H
> #define GRP_H
6a9
> #endif
```

### include/pwd.h

Local test:

```
diff unix-v7-c99/v7/usr/include/pwd.h unix-v7-c99/include/pwd.h || true
```

Expect:

```
0a1,2
> #ifndef PWD_H
> #define PWD_H
11a14,20
> 
> extern struct passwd *getpwent(void);
> extern struct passwd *getpwnam(char *);
> extern struct passwd *getpwuid(int);
> extern void setpwent(void);
> extern void endpwent(void);
> #endif
```

### include/setjmp.h

Local test:

```
diff unix-v7-c99/v7/usr/include/setjmp.h unix-v7-c99/include/setjmp.h || true
```

Expect:

```
1c1,3
< typedef int jmp_buf[3];
---
> typedef int jmp_buf[10];
> int	setjmp(jmp_buf);
> void	longjmp(jmp_buf, int);
```

### include/signal.h

Local test:

```
diff unix-v7-c99/v7/usr/include/signal.h unix-v7-c99/include/signal.h || true
```

Expect:

```
7c7
< #define	SIGTRAP	5	/* trace trap (not reset when caught) */
---
> #define	SIGTRAP	5	/* trace trap */
19,21c19,20
< int	(*signal())();
< #define	SIG_DFL	(int (*)())0
< #define	SIG_IGN	(int (*)())1
---
> #define	SIG_DFL	0
> #define	SIG_IGN	1
```

### include/stdio.h

Local test:

```
diff unix-v7-c99/v7/usr/include/stdio.h unix-v7-c99/include/stdio.h || true
```

Expect:

```
1,41c1
< #define	BUFSIZ	512
< #define	_NFILE	20
< # ifndef FILE
< extern	struct	_iobuf {
< 	char	*_ptr;
< 	int	_cnt;
< 	char	*_base;
< 	char	_flag;
< 	char	_file;
< } _iob[_NFILE];
< # endif
< 
< #define	_IOREAD	01
< #define	_IOWRT	02
< #define	_IONBF	04
< #define	_IOMYBUF	010
< #define	_IOEOF	020
< #define	_IOERR	040
< #define	_IOSTRG	0100
< #define	_IORW	0200
< 
< #define	NULL	0
< #define	FILE	struct _iobuf
< #define	EOF	(-1)
< 
< #define	stdin	(&_iob[0])
< #define	stdout	(&_iob[1])
< #define	stderr	(&_iob[2])
< #define	getc(p)		(--(p)->_cnt>=0? *(p)->_ptr++&0377:_filbuf(p))
< #define	getchar()	getc(stdin)
< #define putc(x,p) (--(p)->_cnt>=0? ((int)(*(p)->_ptr++=(unsigned)(x))):_flsbuf((unsigned)(x),p))
< #define	putchar(x)	putc(x,stdout)
< #define	feof(p)		(((p)->_flag&_IOEOF)!=0)
< #define	ferror(p)	(((p)->_flag&_IOERR)!=0)
< #define	fileno(p)	p->_file
< 
< FILE	*fopen();
< FILE	*freopen();
< FILE	*fdopen();
< long	ftell();
< char	*fgets();
---
> #include "../lib/u.h"
```

### include/sys/dir.h

Local test:

```
diff unix-v7-c99/v7/usr/include/sys/dir.h unix-v7-c99/include/sys/dir.h || true
```

Expect:

```
0a1,4
> #ifndef SYS_DIR_H
> #define SYS_DIR_H
> #include <sys/types.h>
> 
8a13
> #endif
```

### include/sys/stat.h

Local test:

```
diff unix-v7-c99/v7/usr/include/sys/stat.h unix-v7-c99/include/sys/stat.h || true
```

Expect:

```
0a1,4
> #ifndef SYS_STAT_H
> #define SYS_STAT_H
> #include <sys/types.h>
> 
7,8c11,12
< 	short  	st_uid;
< 	short  	st_gid;
---
> 	short	st_uid;
> 	short	st_gid;
16,28c20,28
< #define	S_IFMT	0170000		/* type of file */
< #define		S_IFDIR	0040000	/* directory */
< #define		S_IFCHR	0020000	/* character special */
< #define		S_IFBLK	0060000	/* block special */
< #define		S_IFREG	0100000	/* regular */
< #define		S_IFMPC	0030000	/* multiplexed char special */
< #define		S_IFMPB	0070000	/* multiplexed block special */
< #define	S_ISUID	0004000		/* set user id on execution */
< #define	S_ISGID	0002000		/* set group id on execution */
< #define	S_ISVTX	0001000		/* save swapped text even after use */
< #define	S_IREAD	0000400		/* read permission, owner */
< #define	S_IWRITE	0000200		/* write permission, owner */
< #define	S_IEXEC	0000100		/* execute/search permission, owner */
---
> #define	S_IFMT	0170000
> #define		S_IFDIR	0040000
> #define		S_IFCHR	0020000
> #define		S_IFBLK	0060000
> #define		S_IFREG	0100000
> #define	S_IREAD	0000400
> #define	S_IWRITE	0000200
> #define	S_IEXEC	0000100
> #endif
```

### include/sys/timeb.h

Local test:

```
diff unix-v7-c99/v7/usr/include/sys/timeb.h unix-v7-c99/include/sys/timeb.h || true
```

Expect:

```
0a1,2
> #ifndef SYS_TIMEB_H
> #define SYS_TIMEB_H
9a12
> #endif
```

### include/sys/times.h

Local test:

```
diff unix-v7-c99/v7/usr/include/sys/times.h unix-v7-c99/include/sys/times.h || true
```

Expect:

```
0a1,2
> #ifndef SYS_TIMES_H
> #define SYS_TIMES_H
9a12
> #endif
```

### include/sys/types.h

Local test:

```
diff unix-v7-c99/v7/usr/include/sys/types.h unix-v7-c99/include/sys/types.h || true
```

Expect:

```
1,11c1,10
< typedef	long       	daddr_t;  	/* disk address */
< typedef	char *     	caddr_t;  	/* core address */
< typedef	unsigned int	ino_t;     	/* i-node number */
< typedef	long       	time_t;   	/* a time */
< typedef	int        	label_t[6]; 	/* program status */
< typedef	int        	dev_t;    	/* device code */
< typedef	long       	off_t;    	/* offset in file */
< 	/* selectors and constructor for device code */
< #define	major(x)  	(int)(((unsigned)x>>8))
< #define	minor(x)  	(int)(x&0377)
< #define	makedev(x,y)	(dev_t)((x)<<8|(y))
---
> #ifndef SYS_TYPES_H
> #define SYS_TYPES_H
> typedef	long		daddr_t;
> typedef	char *		caddr_t;
> typedef	unsigned short	ino_t;
> typedef	long		time_t;
> typedef	int		label_t[6];
> typedef	int		dev_t;
> typedef	long		off_t;
> #endif
```

### include/time.h

Local test:

```
diff unix-v7-c99/v7/usr/include/time.h unix-v7-c99/include/time.h || true
```

Expect:

```
0a1,2
> #ifndef TIME_H
> #define TIME_H
11a14
> #endif
```

### lib/crt0.s

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/csu/crt0.s unix-v7-c99/lib/crt0.s || true
```

Expect:

```
1,36c1,6
< / C runtime startoff
< 
< .globl	_exit, _environ
< .globl	start
< .globl	_main
< exit = 1.
< 
< start:
< 	setd
< 	mov	2(sp),r0
< 	clr	-2(r0)
< 	mov	sp,r0
< 	sub	$4,sp
< 	mov	4(sp),(sp)
< 	tst	(r0)+
< 	mov	r0,2(sp)
< 1:
< 	tst	(r0)+
< 	bne	1b
< 	cmp	r0,*2(sp)
< 	blo	1f
< 	tst	-(r0)
< 1:
< 	mov	r0,4(sp)
< 	mov	r0,_environ
< 	jsr	pc,_main
< 	cmp	(sp)+,(sp)+
< 	mov	r0,(sp)
< 	jsr	pc,*$_exit
< 	sys	exit
< 
< .bss
< _environ:
< 	.=.+2
< .data
< 	.=.+2		/ loc 0 for I/D; null ptr points here.
---
> .globl _start
> _start:
> 	bl _startc
> 	mov r7, #1
> 	svc #0
> 	b .
```

### lib/syscall.s

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/v6/syscall.s unix-v7-c99/lib/syscall.s || true
```

Expect:

```
1c1,10
< / syscall
---
> .globl syscall3
> syscall3:
> 	mov ip, r7
> 	mov r7, r0
> 	mov r0, r1
> 	mov r1, r2
> 	mov r2, r3
> 	svc #0
> 	mov r7, ip
> 	bx lr
3,24c12,16
< .globl	_syscall,csv,cret,cerror
< _syscall:
< 	jsr	r5,csv
< 	mov	r5,r2
< 	add	$04,r2
< 	mov	$9f,r3
< 	mov	(r2)+,r0
< 	bic	$!0377,r0
< 	bis	$sys,r0
< 	mov	r0,(r3)+
< 	mov	(r2)+,r0
< 	mov	(r2)+,r1
< 	mov	(r2)+,(r3)+
< 	mov	(r2)+,(r3)+
< 	mov	(r2)+,(r3)+
< 	mov	(r2)+,(r3)+
< 	mov	(r2)+,(r3)+
< 	sys	0; 9f
< 	bec	1f
< 	jmp	cerror
< 1:
< 	jmp	cret
---
> .globl setjmp
> setjmp:
> 	stmia r0, {r4-r11, sp, lr}
> 	mov r0, #0
> 	bx lr
26,27c18,24
< 	.data
< 9:	.=.+12.
---
> .globl longjmp
> longjmp:
> 	ldmia r0, {r4-r11, sp, lr}
> 	mov r0, r1
> 	cmp r0, #0
> 	moveq r0, #1
> 	bx lr
```

### sys/main.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/main.c unix-v7-c99/sys/main.c || true
```

Expect:

```
12a13
> #include "../h/proto.h"
30c31,32
< main()
---
> void
> main(void)
33a36
> #if 0
77a81,82
> #endif
> 	armboot();
79a85
> #if 0
109a116
> #endif
125c132
< binit()
---
> void binit(void)
```

### sys/malloc.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/malloc.c unix-v7-c99/sys/malloc.c || true
```

Expect:

```
1,2d0
< #include "../h/param.h"
< #include "../h/systm.h"
3a2,5
> #include "../h/proto.h"
> 
> struct map coremap[CMAPSIZ];	/* space for core allocation */
> struct map swapmap[SMAPSIZ];	/* space for swap allocation */
15,16c17,18
< malloc(mp, size)
< struct map *mp;
---
> int
> malloc(struct map *mp, int size)
29c31
< 				} while ((bp-1)->m_size = bp->m_size);
---
> 				} while (((bp-1)->m_size = bp->m_size));
43,45c45,46
< mfree(mp, size, a)
< struct map *mp;
< register int a;
---
> void
> mfree(struct map *mp, int size, int a)
49a51
> #if 0
53a56,57
> #endif
> 	bp = mp;
77c81
< 			} while (size = t);
---
> 			} while ((size = t));
```

### sys/prf.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/prf.c unix-v7-c99/sys/prf.c || true
```

Expect:

```
2,3d1
< #include "../h/systm.h"
< #include "../h/seg.h"
5c3,4
< #include "../h/conf.h"
---
> #include "../h/proto.h"
> #include <stdarg.h>
14a14
> void printn(long n, int b);
26,28c26,27
< printf(fmt, x1)
< register char *fmt;
< unsigned x1;
---
> void
> printf(char *fmt, ...)
30,31c29,30
< 	register c;
< 	register unsigned int *adx;
---
> 	register int c;
> 	va_list adx;
34c33
< 	adx = &x1;
---
> 	va_start(adx, fmt);
37c36,37
< 		if(c == '\0')
---
> 		if(c == '\0') {
> 			va_end(adx);
38a39
> 		}
43c44
< 		printn((long)*adx, c=='o'? 8: (c=='x'? 16:10));
---
> 		printn((long)va_arg(adx, unsigned), c=='o'? 8: (c=='x'? 16:10));
45,46c46,47
< 		s = (char *)*adx;
< 		while(c = *s++)
---
> 		s = va_arg(adx, char *);
> 		while((c = *s++))
49,50c50
< 		printn(*(long *)adx, 10);
< 		adx += (sizeof(long) / sizeof(int)) - 1;
---
> 		printn(va_arg(adx, long), 10);
52d51
< 	adx++;
59,60c58,59
< printn(n, b)
< long n;
---
> void
> printn(long n, int b)
68c67
< 	if(a = n/b)
---
> 	if((a = n/b))
79,80c78,79
< panic(s)
< char *s;
---
> void
> panic(char *s)
82a82
> #if 0
83a84
> #endif
85a87
> #if 0
86a89,91
> #else
> 		;
> #endif
95,97c100,101
< prdev(str, dev)
< char *str;
< dev_t dev;
---
> void
> prdev(char *str, dev_t dev)
110,111c114,115
< deverror(bp, o1, o2)
< register struct buf *bp;
---
> void
> deverror(register struct buf *bp, int o1, int o2)
```

### cmd/mount.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/mount.c unix-v7-c99/cmd/mount.c || true
```

Expect:

```
11,12c11,12
< main(argc, argv)
< char **argv;
---
> int
> main(int argc, char **argv)
```

### cmd/umount.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/umount.c unix-v7-c99/cmd/umount.c || true
```

Expect:

```
0a1,2
> #include <stdio.h>
> 
9,10c11,12
< main(argc, argv)
< char **argv;
---
> int
> main(int argc, char **argv)
```

### lib/getpwent.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/getpwent.c unix-v7-c99/lib/getpwent.c || true
```

Expect:

```
9a10
> void
17a19
> void
```

### lib/getpwnam.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/getpwnam.c unix-v7-c99/lib/getpwnam.c || true
```

Expect:

```
0a1
> #include "u.h"
```

### lib/getpwuid.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/getpwuid.c unix-v7-c99/lib/getpwuid.c || true
```

Expect:

```
5c5
< register uid;
---
> register int uid;
```

### lib/strncat.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/strncat.c unix-v7-c99/lib/strncat.c || true
```

Expect:

```
10c10
< register n;
---
> register int n;
```

### lib/ttyslot.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/ttyslot.c unix-v7-c99/lib/ttyslot.c || true
```

Expect:

```
6a7
> #include "u.h"
9c10
< char	*getttys();
---
> static char *getttys();
14a16
> int
18c20
< 	register s, tf;
---
> 	register int s, tf;
41a44
> int f;
```

### lib/execvp.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/execvp.c unix-v7-c99/lib/execvp.c || true
```

Expect:

```
4a5
> #include "u.h"
9,10c10,11
< char	*execat(), *getenv();
< extern	errno;
---
> static char *execat();
> extern	int errno;
12,13c13,14
< execlp(name, argv)
< char *name, *argv;
---
> int
> execlp(char *name, char *arg0, ...)
15c16
< 	return(execvp(name, &argv));
---
> 	return(execvp(name, &arg0));
17a19
> int
27c29
< 	register eacces = 0;
---
> 	register int eacces = 0;
```

### lib/getenv.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/getenv.c unix-v7-c99/lib/getenv.c || true
```

Expect:

```
4a5
> #include "u.h"
6,7c7,12
< extern	char **environ;
< char	*nvmatch();
---
> 
> static char *empty[] = { 0 };
> char **environ = empty;
> int errno;
> 
> static char *nvmatch();
```

### lib/atoi.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/atoi.c unix-v7-c99/lib/atoi.c || true
```

Expect:

```
0a1
> int
```

### lib/atol.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/atol.c unix-v7-c99/lib/atol.c || true
```

Expect:

```

```

### lib/abs.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/abs.c unix-v7-c99/lib/abs.c || true
```

Expect:

```
0a1
> int
1a3
> int arg;
```

### lib/index.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/index.c unix-v7-c99/lib/index.c || true
```

Expect:

```

```

### lib/rindex.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/rindex.c unix-v7-c99/lib/rindex.c || true
```

Expect:

```

```

### lib/strcat.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/strcat.c unix-v7-c99/lib/strcat.c || true
```

Expect:

```

```

### lib/strcmp.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/strcmp.c unix-v7-c99/lib/strcmp.c || true
```

Expect:

```
4a5
> int
```

### lib/strcpy.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/strcpy.c unix-v7-c99/lib/strcpy.c || true
```

Expect:

```

```

### lib/strlen.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/strlen.c unix-v7-c99/lib/strlen.c || true
```

Expect:

```
5a6
> int
9c10
< 	register n;
---
> 	register int n;
```

### lib/strncmp.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/strncmp.c unix-v7-c99/lib/strncmp.c || true
```

Expect:

```
4a5
> int
7c8
< register n;
---
> register int n;
```

### lib/strncpy.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/strncpy.c unix-v7-c99/lib/strncpy.c || true
```

Expect:

```
8a9
> int n;
10c11
< 	register i;
---
> 	register int i;
```

### lib/isatty.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/isatty.c unix-v7-c99/lib/isatty.c || true
```

Expect:

```
4a5
> #include "u.h"
6a8
> int
7a10
> int f;
```

### lib/perror.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/perror.c unix-v7-c99/lib/perror.c || true
```

Expect:

```
5a6,7
> #include "u.h"
> 
8c10,11
< char	*sys_errlist[];
---
> char	*sys_errlist[1];
> void
13c16
< 	register n;
---
> 	register int n;
```

### lib/swab.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/swab.c unix-v7-c99/lib/swab.c || true
```

Expect:

```
5a6
> void
8c9
< register n;
---
> register int n;
```

### lib/rand.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/rand.c unix-v7-c99/lib/rand.c || true
```

Expect:

```
2a3
> void
8a10
> int
```

### lib/mktemp.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/mktemp.c unix-v7-c99/lib/mktemp.c || true
```

Expect:

```
0a1,2
> #include "u.h"
> 
7c9
< 	register i;
---
> 	register int i;
```

### lib/errlst.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/errlst.c unix-v7-c99/lib/errlst.c || true
```

Expect:

```

```

### lib/ttyname.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/ttyname.c unix-v7-c99/lib/ttyname.c || true
```

Expect:

```
7a8
> #include "u.h"
17a19
> int f;
23c25
< 	register df;
---
> 	register int df;
```

### cmd/getty.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/getty.c unix-v7-c99/cmd/getty.c || true
```

Expect:

```
10a11,20
> int read(int fd, char *buf, int n);
> int write(int fd, char *buf, int n);
> int ioctl(int fd, int cmd, void *arg);
> int stty(int fd, void *buf);
> int execl(char *path, char *arg0, ...);
> void exit(int n);
> int getname(void);
> void puts(char *as);
> void putchr(int cc);
> 
128,129c138,139
< main(argc, argv)
< char **argv;
---
> int
> main(int argc, char *argv[])
178c188,189
< getname()
---
> int
> getname(void)
181c192
< 	register c;
---
> 	register int c;
222,223c233,234
< puts(as)
< char *as;
---
> void
> puts(char *as)
232c243,244
< putchr(cc)
---
> void
> putchr(int cc)
```

### cmd/init.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/init.c unix-v7-c99/cmd/init.c || true
```

Expect:

```
4a5
> #include <stdio.h>
38c39,53
< main()
---
> int shutdown(void);
> int single(void);
> int runcom(void);
> int multiple(void);
> int merge(void);
> int term(struct tab *p);
> int rline(void);
> int maktty(char *lin);
> int get(void);
> int dfork(struct tab *p);
> int rmut(struct tab *p);
> void reset(void);
> 
> int
> main(void)
40d54
< 	int reset();
43c57
< 	signal(SIGHUP, reset);
---
> 	signal(SIGHUP, (int)reset);
50a65
> 	return(0);
53c68,69
< shutdown()
---
> int
> shutdown(void)
55c71
< 	register i;
---
> 	register int i;
61c77
< 	signal(SIGALRM, reset);
---
> 	signal(SIGALRM, (int)reset);
70a87
> 	return(0);
73c90,91
< single()
---
> int
> single(void)
75c93
< 	register pid;
---
> 	register int pid;
92a111
> 	return(0);
95c114,115
< runcom()
---
> int
> runcom(void)
97c117
< 	register pid;
---
> 	register int pid;
108a129
> 	return(0);
111c132,133
< multiple()
---
> int
> multiple(void)
114c136
< 	register pid;
---
> 	register int pid;
119c141
< 			return;
---
> 			return(0);
128,129c150,151
< term(p)
< register struct tab *p;
---
> int
> term(struct tab *p)
137a160
> 	return(0);
140c163,164
< rline()
---
> int
> rline(void)
142c166
< 	register c, i;
---
> 	register int c, i;
174,175c198,199
< maktty(lin)
< char *lin;
---
> int
> maktty(char *lin)
177c201
< 	register i, j;
---
> 	register int i, j;
185a210
> 	return(0);
188c213,214
< get()
---
> int
> get(void)
199c225,226
< merge()
---
> int
> merge(void)
202c229
< 	register i;
---
> 	register int i;
205c232
< 	signal(SIGINT, merge);
---
> 	signal(SIGINT, (int)merge);
208c235
< 		return;
---
> 		return(0);
240a268
> 	return(0);
243,244c271,272
< dfork(p)
< struct tab *p;
---
> int
> dfork(struct tab *p)
246c274
< 	register pid;
---
> 	register int pid;
263a292
> 	return(0);
266,267c295,296
< rmut(p)
< register struct tab *p;
---
> int
> rmut(struct tab *p)
269c298
< 	register i, f;
---
> 	register int i, f;
296a326
> 	return(0);
299c329,330
< reset()
---
> void
> reset(void)
```

### sys/prim.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/prim.c unix-v7-c99/sys/prim.c || true
```

Expect:

```

```

### sys/slp.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/slp.c unix-v7-c99/sys/slp.c || true
```

Expect:

```

```

## WIP

### tools/mkfs.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/mkfs.c unix-v7-c99/tools/mkfs.c || true
```

Expect:

```
1,11c1,3
< /*
<  * Make a file system prototype.
<  * usage: mkfs filsys proto/size [ m n ]
<  */
< #define	NIPB	(BSIZE/sizeof(struct dinode))
< #define	NINDIR	(BSIZE/sizeof(daddr_t))
< #define	NDIRECT	(BSIZE/sizeof(struct direct))
< #define	LADDR	10
< #define	MAXFN	500
< #define	itoo(x)	(int)((x+15)&07)
< #ifndef STANDALONE
---
> #include <dirent.h>
> #include <errno.h>
> #include <stdint.h>
13c5,19
< #include <a.out.h>
---
> #include <stdlib.h>
> #include <string.h>
> #include <sys/stat.h>
> 
> #define	BSIZE	512
> #define	DIRSIZ	14
> #define	DIRENT	16
> #define	NADDR	13
> #define	NICFREE	50
> #define	NICINOD	100
> #define	IFDIR	0040000
> #define	IFREG	0100000
> #define	ROOTINO	2
> #ifndef FSSIZE
> #define	FSSIZE	4096
15,25c21,22
< #include <sys/param.h>
< #include <sys/ino.h>
< #include <sys/inode.h>
< #include <sys/filsys.h>
< #include <sys/fblk.h>
< #include <sys/dir.h>
< time_t	utime;
< #ifndef STANDALONE
< FILE 	*fin;
< #else
< int	fin;
---
> #ifndef ISIZE
> #define	ISIZE	16
27,36c24,25
< int	fsi;
< int	fso;
< char	*charp;
< char	buf[BSIZE];
< union {
< 	struct fblk fb;
< 	char pad1[BSIZE];
< } fbuf;
< #ifndef STANDALONE
< struct exec head;
---
> #ifndef MAXINO
> #define	MAXINO	128
38,99c27,28
< char	string[50];
< union {
< 	struct filsys fs;
< 	char pad2[BSIZE];
< } filsys;
< char	*fsys;
< char	*proto;
< int	f_n	= MAXFN;
< int	f_m	= 3;
< int	error;
< ino_t	ino;
< long	getnum();
< daddr_t	alloc();
< 
< main(argc, argv)
< char *argv[];
< {
< 	int f, c;
< 	long n;
< 
< #ifndef STANDALONE
< 	time(&utime);
< 	if(argc < 3) {
< 		printf("usage: mkfs filsys proto/size [ m n ]\n");
< 		exit(1);
< 	}
< 	fsys = argv[1];
< 	proto = argv[2];
< #else
< 	{
< 		static char protos[60];
< 
< 		printf("file sys size: ");
< 		gets(protos);
< 		proto = protos;
< 	}
< #endif
< #ifdef STANDALONE
< 	{
< 		char fsbuf[100];
< 
< 		do {
< 			printf("file system: ");
< 			gets(fsbuf);
< 			fso = open(fsbuf, 1);
< 			fsi = open(fsbuf, 0);
< 		} while (fso < 0 || fsi < 0);
< 	}
< 	fin = NULL;
< 	argc = 0;
< #else
< 	fso = creat(fsys, 0666);
< 	if(fso < 0) {
< 		printf("%s: cannot create\n", fsys);
< 		exit(1);
< 	}
< 	fsi = open(fsys, 0);
< 	if(fsi < 0) {
< 		printf("%s: cannot open\n", fsys);
< 		exit(1);
< 	}
< 	fin = fopen(proto, "r");
---
> #ifndef MAXBLK
> #define	MAXBLK	4096
101,145d29
< 	if(fin == NULL) {
< 		n = 0;
< 		for(f=0; c=proto[f]; f++) {
< 			if(c<'0' || c>'9') {
< 				printf("%s: cannot open\n", proto);
< 				exit(1);
< 			}
< 			n = n*10 + (c-'0');
< 		}
< 		filsys.s_fsize = n;
< 		n = n/25;
< 		if(n <= 0)
< 			n = 1;
< 		if(n > 65500/NIPB)
< 			n = 65500/NIPB;
< 		filsys.s_isize = n + 2;
< 		printf("isize = %D\n", n*NIPB);
< 		charp = "d--777 0 0 $ ";
< 		goto f3;
< 	}
< 
< #ifndef STANDALONE
< 	/*
< 	 * get name of boot load program
< 	 * and read onto block 0
< 	 */
< 
< 	getstr();
< 	f = open(string, 0);
< 	if(f < 0) {
< 		printf("%s: cannot  open init\n", string);
< 		goto f2;
< 	}
< 	read(f, (char *)&head, sizeof head);
< 	if(head.a_magic != A_MAGIC1) {
< 		printf("%s: bad format\n", string);
< 		goto f1;
< 	}
< 	c = head.a_text + head.a_data;
< 	if(c > BSIZE) {
< 		printf("%s: too big\n", string);
< 		goto f1;
< 	}
< 	read(f, buf, c);
< 	wtfs((long)0, buf);
147,148c31,39
< f1:
< 	close(f);
---
> struct node {
> 	char path[128];
> 	char host[256];
> 	int ino;
> 	int mode;
> 	int size;
> 	int blocks[MAXBLK];
> 	int nblock;
> };
150,159c41,45
< 	/*
< 	 * get total disk size
< 	 * and inode block size
< 	 */
< 
< f2:
< 	filsys.s_fsize = getnum();
< 	n = getnum();
< 	n /= NIPB;
< 	filsys.s_isize = n + 3;
---
> static unsigned char image[FSSIZE][BSIZE];
> static struct node nodes[MAXINO];
> static int nnodes;
> static int nextino = ROOTINO;
> static int nextblk = 2 + ISIZE;
161,186c47,49
< #endif
< f3:
< 	if(argc >= 5) {
< 		f_m = atoi(argv[3]);
< 		f_n = atoi(argv[4]);
< 		if(f_n <= 0 || f_n >= MAXFN)
< 			f_n = MAXFN;
< 		if(f_m <= 0 || f_m > f_n)
< 			f_m = 3;
< 	}
< 	filsys.s_m = f_m;
< 	filsys.s_n = f_n;
< 	printf("m/n = %d %d\n", f_m, f_n);
< 	if(filsys.s_isize >= filsys.s_fsize) {
< 		printf("%ld/%ld: bad ratio\n", filsys.s_fsize, filsys.s_isize-2);
< 		exit(1);
< 	}
< 	filsys.s_tfree = 0;
< 	filsys.s_tinode = 0;
< 	for(c=0; c<BSIZE; c++)
< 		buf[c] = 0;
< 	for(n=2; n!=filsys.s_isize; n++) {
< 		wtfs(n, buf);
< 		filsys.s_tinode += NIPB;
< 	}
< 	ino = 0;
---
> static void
> put16(unsigned char *p, unsigned int v)
> {
188c51,53
< 	bflist();
---
> 	p[0] = v & 0377;
> 	p[1] = (v >> 8) & 0377;
> }
190c55,57
< 	cfile((struct inode *)0);
---
> static void
> put32(unsigned char *p, unsigned int v)
> {
192,224c59,63
< 	filsys.s_time = utime;
< 	wtfs((long)1, (char *)&filsys);
< 	exit(error);
< }
< 
< cfile(par)
< struct inode *par;
< {
< 	struct inode in;
< 	int dbc, ibc;
< 	char db[BSIZE];
< 	daddr_t ib[NINDIR];
< 	int i, f, c;
< 
< 	/*
< 	 * get mode, uid and gid
< 	 */
< 
< 	getstr();
< 	in.i_mode = gmode(string[0], "-bcd", IFREG, IFBLK, IFCHR, IFDIR);
< 	in.i_mode |= gmode(string[1], "-u", 0, ISUID, 0, 0);
< 	in.i_mode |= gmode(string[2], "-g", 0, ISGID, 0, 0);
< 	for(i=3; i<6; i++) {
< 		c = string[i];
< 		if(c<'0' || c>'7') {
< 			printf("%c/%s: bad octal mode digit\n", c, string);
< 			error = 1;
< 			c = 0;
< 		}
< 		in.i_mode |= (c-'0')<<(15-3*i);
< 	}
< 	in.i_uid = getnum();
< 	in.i_gid = getnum();
---
> 	p[0] = v & 0377;
> 	p[1] = (v >> 8) & 0377;
> 	p[2] = (v >> 16) & 0377;
> 	p[3] = (v >> 24) & 0377;
> }
226,267c65,67
< 	/*
< 	 * general initialization prior to
< 	 * switching on format
< 	 */
< 
< 	ino++;
< 	in.i_number = ino;
< 	for(i=0; i<BSIZE; i++)
< 		db[i] = 0;
< 	for(i=0; i<NINDIR; i++)
< 		ib[i] = (daddr_t)0;
< 	in.i_nlink = 1;
< 	in.i_size = 0;
< 	for(i=0; i<NADDR; i++)
< 		in.i_un.i_addr[i] = (daddr_t)0;
< 	if(par == (struct inode *)0) {
< 		par = &in;
< 		in.i_nlink--;
< 	}
< 	dbc = 0;
< 	ibc = 0;
< 	switch(in.i_mode&IFMT) {
< 
< 	case IFREG:
< 		/*
< 		 * regular file
< 		 * contents is a file name
< 		 */
< 
< 		getstr();
< 		f = open(string, 0);
< 		if(f < 0) {
< 			printf("%s: cannot open\n", string);
< 			error = 1;
< 			break;
< 		}
< 		while((i=read(f, db, BSIZE)) > 0) {
< 			in.i_size += i;
< 			newblk(&dbc, db, &ibc, ib);
< 		}
< 		close(f);
< 		break;
---
> static void
> put24(unsigned char *p, unsigned int v)
> {
269,306c69,71
< 	case IFBLK:
< 	case IFCHR:
< 		/*
< 		 * special file
< 		 * content is maj/min types
< 		 */
< 
< 		i = getnum() & 0377;
< 		f = getnum() & 0377;
< 		in.i_un.i_addr[0] = (i<<8) | f;
< 		break;
< 
< 	case IFDIR:
< 		/*
< 		 * directory
< 		 * put in extra links
< 		 * call recursively until
< 		 * name of "$" found
< 		 */
< 
< 		par->i_nlink++;
< 		in.i_nlink++;
< 		entry(in.i_number, ".", &dbc, db, &ibc, ib);
< 		entry(par->i_number, "..", &dbc, db, &ibc, ib);
< 		in.i_size = 2*sizeof(struct direct);
< 		for(;;) {
< 			getstr();
< 			if(string[0]=='$' && string[1]=='\0')
< 				break;
< 			entry(ino+1, string, &dbc, db, &ibc, ib);
< 			in.i_size += sizeof(struct direct);
< 			cfile(&in);
< 		}
< 		break;
< 	}
< 	if(dbc != 0)
< 		newblk(&dbc, db, &ibc, ib);
< 	iput(&in, &ibc, ib);
---
> 	p[0] = v & 0377;
> 	p[1] = (v >> 8) & 0377;
> 	p[2] = (v >> 16) & 0377;
309,310c74,75
< gmode(c, s, m0, m1, m2, m3)
< char c, *s;
---
> static struct node *
> find(char *path)
314,339c79,82
< 	for(i=0; s[i]; i++)
< 		if(c == s[i])
< 			return((&m0)[i]);
< 	printf("%c/%s: bad mode\n", c, string);
< 	error = 1;
< 	return(0);
< }
< 
< long
< getnum()
< {
< 	int i, c;
< 	long n;
< 
< 	getstr();
< 	n = 0;
< 	i = 0;
< 	for(i=0; c=string[i]; i++) {
< 		if(c<'0' || c>'9') {
< 			printf("%s: bad number\n", string);
< 			error = 1;
< 			return((long)0);
< 		}
< 		n = n*10 + (c-'0');
< 	}
< 	return(n);
---
> 	for(i=0; i<nnodes; i++)
> 		if(strcmp(nodes[i].path, path) == 0)
> 			return(&nodes[i]);
> 	return(NULL);
342c85,86
< getstr()
---
> static struct node *
> addnode(char *path, int mode)
344,360c88
< 	int i, c;
< 
< loop:
< 	switch(c=getch()) {
< 
< 	case ' ':
< 	case '\t':
< 	case '\n':
< 		goto loop;
< 
< 	case '\0':
< 		printf("EOF\n");
< 		exit(1);
< 
< 	case ':':
< 		while(getch() != '\n');
< 		goto loop;
---
> 	struct node *np;
362,397c90,100
< 	}
< 	i = 0;
< 
< 	do {
< 		string[i++] = c;
< 		c = getch();
< 	} while(c!=' '&&c!='\t'&&c!='\n'&&c!='\0');
< 	string[i] = '\0';
< }
< 
< rdfs(bno, bf)
< daddr_t bno;
< char *bf;
< {
< 	int n;
< 
< 	lseek(fsi, bno*BSIZE, 0);
< 	n = read(fsi, bf, BSIZE);
< 	if(n != BSIZE) {
< 		printf("read error: %ld\n", bno);
< 		exit(1);
< 	}
< }
< 
< wtfs(bno, bf)
< daddr_t bno;
< char *bf;
< {
< 	int n;
< 
< 	lseek(fso, bno*BSIZE, 0);
< 	n = write(fso, bf, BSIZE);
< 	if(n != BSIZE) {
< 		printf("write error: %D\n", bno);
< 		exit(1);
< 	}
---
> 	np = find(path);
> 	if(np != NULL)
> 		return(np);
> 	if(nnodes >= MAXINO)
> 		exit(2);
> 	np = &nodes[nnodes++];
> 	memset(np, 0, sizeof(*np));
> 	(void)snprintf(np->path, sizeof(np->path), "%s", path);
> 	np->ino = nextino++;
> 	np->mode = mode;
> 	return(np);
400,401c103,104
< daddr_t
< alloc()
---
> static void
> parent(char *path, char *buf)
403,404c106
< 	int i;
< 	daddr_t bno;
---
> 	char *p;
406,418c108,113
< 	filsys.s_tfree--;
< 	bno = filsys.s_free[--filsys.s_nfree];
< 	if(bno == 0) {
< 		printf("out of free space\n");
< 		exit(1);
< 	}
< 	if(filsys.s_nfree <= 0) {
< 		rdfs(bno, (char *)&fbuf);
< 		filsys.s_nfree = fbuf.df_nfree;
< 		for(i=0; i<NICFREE; i++)
< 			filsys.s_free[i] = fbuf.df_free[i];
< 	}
< 	return(bno);
---
> 	(void)snprintf(buf, 128, "%s", path);
> 	p = strrchr(buf, '/');
> 	if(p == buf)
> 		p[1] = 0;
> 	else if(p != NULL)
> 		*p = 0;
421,422c116,117
< bfree(bno)
< daddr_t bno;
---
> static char *
> base(char *path)
424c119
< 	int i;
---
> 	char *p;
426,434c121,122
< 	filsys.s_tfree++;
< 	if(filsys.s_nfree >= NICFREE) {
< 		fbuf.df_nfree = filsys.s_nfree;
< 		for(i=0; i<NICFREE; i++)
< 			fbuf.df_free[i] = filsys.s_free[i];
< 		wtfs(bno, (char *)&fbuf);
< 		filsys.s_nfree = 0;
< 	}
< 	filsys.s_free[filsys.s_nfree++] = bno;
---
> 	p = strrchr(path, '/');
> 	return(p == NULL ? path : p+1);
437,442c125,126
< entry(inum, str, adbc, db, aibc, ib)
< ino_t inum;
< char *str;
< int *adbc, *aibc;
< char *db;
< daddr_t *ib;
---
> static void
> mkdirs(char *path)
444,445c128,138
< 	struct direct *dp;
< 	int i;
---
> 	char tmp[128];
> 	char *p;
> 
> 	(void)snprintf(tmp, sizeof(tmp), "%s", path);
> 	for(p=tmp+1; *p; p++)
> 		if(*p == '/') {
> 			*p = 0;
> 			(void)addnode(tmp, IFDIR | 0755);
> 			*p = '/';
> 		}
> }
447,463c140,141
< 	dp = (struct direct *)db;
< 	dp += *adbc;
< 	(*adbc)++;
< 	dp->d_ino = inum;
< 	for(i=0; i<DIRSIZ; i++)
< 		dp->d_name[i] = 0;
< 	for(i=0; i<DIRSIZ; i++)
< 		if((dp->d_name[i] = str[i]) == 0)
< 			break;
< 	if(*adbc >= NDIRECT)
< 		newblk(adbc, db, aibc, ib);
< }
< 
< newblk(adbc, db, aibc, ib)
< int *adbc, *aibc;
< char *db;
< daddr_t *ib;
---
> static void
> addfile(char *path, char *host)
465,466c143
< 	int i;
< 	daddr_t bno;
---
> 	struct node *np;
468,479c145,147
< 	bno = alloc();
< 	wtfs(bno, db);
< 	for(i=0; i<BSIZE; i++)
< 		db[i] = 0;
< 	*adbc = 0;
< 	ib[*aibc] = bno;
< 	(*aibc)++;
< 	if(*aibc >= NINDIR) {
< 		printf("indirect block full\n");
< 		error = 1;
< 		*aibc = 0;
< 	}
---
> 	mkdirs(path);
> 	np = addnode(path, IFREG | 0755);
> 	(void)snprintf(np->host, sizeof(np->host), "%s", host);
482c150,151
< getch()
---
> static void
> allocblock(struct node *np, unsigned char *data, int n)
485,491c154,158
< #ifndef STANDALONE
< 	if(charp)
< #endif
< 		return(*charp++);
< #ifndef STANDALONE
< 	return(getc(fin));
< #endif
---
> 	if(np->nblock >= MAXBLK || nextblk >= MAXBLK)
> 		exit(3);
> 	np->blocks[np->nblock++] = nextblk;
> 	memcpy(image[nextblk], data, n);
> 	nextblk++;
494c161,162
< bflist()
---
> static void
> loadfiles(void)
496,513c164,166
< 	struct inode in;
< 	daddr_t ib[NINDIR];
< 	int ibc;
< 	char flg[MAXFN];
< 	int adr[MAXFN];
< 	int i, j;
< 	daddr_t f, d;
< 
< 	for(i=0; i<f_n; i++)
< 		flg[i] = 0;
< 	i = 0;
< 	for(j=0; j<f_n; j++) {
< 		while(flg[i])
< 			i = (i+1)%f_n;
< 		adr[j] = i+1;
< 		flg[i]++;
< 		i = (i+f_m)%f_n;
< 	}
---
> 	FILE *fp;
> 	unsigned char buf[BSIZE];
> 	int i, n;
515,545c168,181
< 	ino++;
< 	in.i_number = ino;
< 	in.i_mode = IFREG;
< 	in.i_uid = 0;
< 	in.i_gid = 0;
< 	in.i_nlink = 0;
< 	in.i_size = 0;
< 	for(i=0; i<NADDR; i++)
< 		in.i_un.i_addr[i] = (daddr_t)0;
< 
< 	for(i=0; i<NINDIR; i++)
< 		ib[i] = (daddr_t)0;
< 	ibc = 0;
< 	bfree((daddr_t)0);
< 	d = filsys.s_fsize-1;
< 	while(d%f_n)
< 		d++;
< 	for(; d > 0; d -= f_n)
< 	for(i=0; i<f_n; i++) {
< 		f = d - adr[i];
< 		if(f < filsys.s_fsize && f >= filsys.s_isize)
< 			if(badblk(f)) {
< 				if(ibc >= NINDIR) {
< 					printf("too many bad blocks\n");
< 					error = 1;
< 					ibc = 0;
< 				}
< 				ib[ibc] = f;
< 				ibc++;
< 			} else
< 				bfree(f);
---
> 	for(i=0; i<nnodes; i++) {
> 		if((nodes[i].mode & IFREG) == 0)
> 			continue;
> 		fp = fopen(nodes[i].host, "rb");
> 		if(fp == NULL) {
> 			perror(nodes[i].host);
> 			exit(1);
> 		}
> 		while((n = (int)fread(buf, 1, sizeof(buf), fp)) > 0) {
> 			allocblock(&nodes[i], buf, n);
> 			nodes[i].size += n;
> 			memset(buf, 0, sizeof(buf));
> 		}
> 		(void)fclose(fp);
547d182
< 	iput(&in, &ibc, ib);
550,553c185,186
< iput(ip, aibc, ib)
< struct inode *ip;
< int *aibc;
< daddr_t *ib;
---
> static void
> dirent(unsigned char *p, int ino, char *name)
555,557d187
< 	struct dinode *dp;
< 	daddr_t d;
< 	int i;
559,593c189,222
< 	filsys.s_tinode--;
< 	d = itod(ip->i_number);
< 	if(d >= filsys.s_isize) {
< 		if(error == 0)
< 			printf("ilist too small\n");
< 		error = 1;
< 		return;
< 	}
< 	rdfs(d, buf);
< 	dp = (struct dinode *)buf;
< 	dp += itoo(ip->i_number);
< 
< 	dp->di_mode = ip->i_mode;
< 	dp->di_nlink = ip->i_nlink;
< 	dp->di_uid = ip->i_uid;
< 	dp->di_gid = ip->i_gid;
< 	dp->di_size = ip->i_size;
< 	dp->di_atime = utime;
< 	dp->di_mtime = utime;
< 	dp->di_ctime = utime;
< 
< 	switch(ip->i_mode&IFMT) {
< 
< 	case IFDIR:
< 	case IFREG:
< 		for(i=0; i<*aibc; i++) {
< 			if(i >= LADDR)
< 				break;
< 			ip->i_un.i_addr[i] = ib[i];
< 		}
< 		if(*aibc >= LADDR) {
< 			ip->i_un.i_addr[LADDR] = alloc();
< 			for(i=0; i<NINDIR-LADDR; i++) {
< 				ib[i] = ib[i+LADDR];
< 				ib[i+LADDR] = (daddr_t)0;
---
> 	memset(p, 0, DIRENT);
> 	put16(p, (unsigned int)ino);
> 	(void)strncpy((char *)p+2, name, DIRSIZ);
> }
> 
> static void
> makedirs(void)
> {
> 	struct node *dp;
> 	unsigned char buf[BSIZE];
> 	char par[128];
> 	int i, off;
> 
> 	for(i=0; i<nnodes; i++) {
> 		dp = &nodes[i];
> 		if((dp->mode & IFDIR) == 0)
> 			continue;
> 		memset(buf, 0, sizeof(buf));
> 		off = 0;
> 		dirent(&buf[off], dp->ino, ".");
> 		off += DIRENT;
> 		parent(dp->path, par);
> 		dirent(&buf[off], find(par)->ino, "..");
> 		off += DIRENT;
> 		for(int j=0; j<nnodes; j++) {
> 			parent(nodes[j].path, par);
> 			if(strcmp(par, dp->path) == 0 && strcmp(nodes[j].path, dp->path) != 0) {
> 				if(off + DIRENT > BSIZE) {
> 					allocblock(dp, buf, BSIZE);
> 					memset(buf, 0, sizeof(buf));
> 					off = 0;
> 				}
> 				dirent(&buf[off], nodes[j].ino, base(nodes[j].path));
> 				off += DIRENT;
595d223
< 			wtfs(ip->i_un.i_addr[LADDR], (char *)ib);
596a225,230
> 		dp->size = off;
> 		if(dp->nblock)
> 			dp->size += (dp->nblock * BSIZE);
> 		allocblock(dp, buf, BSIZE);
> 	}
> }
598,605c232,270
< 	case IFBLK:
< 	case IFCHR:
< 		ltol3(dp->di_addr, ip->i_un.i_addr, NADDR);
< 		break;
< 
< 	default:
< 		printf("bad mode %o\n", ip->i_mode);
< 		exit(1);
---
> static void
> writeinode(struct node *np)
> {
> 	unsigned char *p;
> 	int i, b, o, ib, dib, n;
> 
> 	b = (np->ino + 15) / 8;
> 	o = ((np->ino + 15) & 7) * 64;
> 	p = &image[b][o];
> 	put16(p+0, (unsigned int)np->mode);
> 	put16(p+2, 1);
> 	put16(p+4, 0);
> 	put16(p+6, 0);
> 	put32(p+8, (unsigned int)np->size);
> 	for(i=0; i<np->nblock && i<NADDR-3; i++)
> 		put24(p+12+i*3, (unsigned int)np->blocks[i]);
> 	if(np->nblock > NADDR-3) {
> 		if(nextblk >= MAXBLK)
> 			exit(3);
> 		ib = nextblk++;
> 		put24(p+12+(NADDR-3)*3, (unsigned int)ib);
> 		for(i=NADDR-3; i<np->nblock && i<NADDR-3+128; i++)
> 			put32(&image[ib][(i-(NADDR-3))*4], (unsigned int)np->blocks[i]);
> 	}
> 	if(np->nblock > NADDR-3+128) {
> 		if(nextblk >= MAXBLK)
> 			exit(3);
> 		dib = nextblk++;
> 		put24(p+12+(NADDR-2)*3, (unsigned int)dib);
> 		for(i=NADDR-3+128; i<np->nblock; i++) {
> 			n = i - (NADDR-3+128);
> 			if(n % 128 == 0) {
> 				if(nextblk >= MAXBLK)
> 					exit(3);
> 				ib = nextblk++;
> 				put32(&image[dib][(n/128)*4], (unsigned int)ib);
> 			}
> 			put32(&image[ib][(n%128)*4], (unsigned int)np->blocks[i]);
> 		}
607d271
< 	wtfs(d, buf);
610,611c274,275
< badblk(bno)
< daddr_t bno;
---
> static void
> super(void)
612a277,285
> 	unsigned char *p;
> 
> 	p = image[1];
> 	put16(p+0, ISIZE);
> 	put32(p+2, FSSIZE);
> 	put16(p+6, 0);
> 	put16(p+6+4*NICFREE, 0);
> 	put32(p+6+4*NICFREE+2+4*NICINOD+4, 1);
> }
613a287,318
> int
> main(int argc, char **argv)
> {
> 	FILE *fp;
> 	int i;
> 	char *eq;
> 
> 	if(argc < 3) {
> 		(void)fprintf(stderr, "usage: mkfs image path=file ...\n");
> 		return(1);
> 	}
> 	memset(image, 0, sizeof(image));
> 	addnode("/", IFDIR | 0755);
> 	for(i=2; i<argc; i++) {
> 		eq = strchr(argv[i], '=');
> 		if(eq == NULL)
> 			return(1);
> 		*eq++ = 0;
> 		addfile(argv[i], eq);
> 	}
> 	loadfiles();
> 	makedirs();
> 	for(i=0; i<nnodes; i++)
> 		writeinode(&nodes[i]);
> 	super();
> 	fp = fopen(argv[1], "wb");
> 	if(fp == NULL) {
> 		perror(argv[1]);
> 		return(1);
> 	}
> 	(void)fwrite(image, sizeof(image), 1, fp);
> 	(void)fclose(fp);
```

