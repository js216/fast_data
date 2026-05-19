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
    -not -path 'unix-v7-c99/root/etc/accton' \
    -not -path 'unix-v7-c99/root/etc/atrun' \
    -not -path 'unix-v7-c99/root/etc/update' \
    -not -path 'unix-v7-c99/root/etc/ac' \
    -not -path 'unix-v7-c99/root/etc/cron' \
    -not -path 'unix-v7-c99/root/etc/utmp.empty' \
    -not -path 'unix-v7-c99/root/unix' \
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
unix-v7-c99/arch/arm.h
unix-v7-c99/arch/armboot.c
unix-v7-c99/arch/evb.ld
unix-v7-c99/arch/machdep.c
unix-v7-c99/arch/swtch.s
unix-v7-c99/arch/u_bridge.c
unix-v7-c99/arch/u_stub.c
unix-v7-c99/arch/v7stubs.c
unix-v7-c99/cmd/ac.c
unix-v7-c99/cmd/accton.c
unix-v7-c99/cmd/arithmetic.c
unix-v7-c99/cmd/at.c
unix-v7-c99/cmd/atrun.c
unix-v7-c99/cmd/awk/awk.def
unix-v7-c99/cmd/awk/b.c
unix-v7-c99/cmd/awk/lib.c
unix-v7-c99/cmd/awk/main.c
unix-v7-c99/cmd/awk/parse.c
unix-v7-c99/cmd/awk/proc.c
unix-v7-c99/cmd/awk/run.c
unix-v7-c99/cmd/awk/token.c
unix-v7-c99/cmd/awk/tran.c
unix-v7-c99/cmd/backgammon.c
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
unix-v7-c99/cmd/cron.c
unix-v7-c99/cmd/crypt.c
unix-v7-c99/cmd/date.c
unix-v7-c99/cmd/dc/dc.c
unix-v7-c99/cmd/dc/dc.h
unix-v7-c99/cmd/dcheck.c
unix-v7-c99/cmd/dd.c
unix-v7-c99/cmd/df.c
unix-v7-c99/cmd/diff.c
unix-v7-c99/cmd/diff3.c
unix-v7-c99/cmd/diffh.c
unix-v7-c99/cmd/dkstat.c (port-local: integer-only iostat stand-in)
unix-v7-c99/cmd/dmesg.c
unix-v7-c99/cmd/du.c
unix-v7-c99/cmd/dump.c
unix-v7-c99/cmd/dumpdir.c
unix-v7-c99/cmd/echo.c
unix-v7-c99/cmd/ed.c
unix-v7-c99/cmd/fgrep.c
unix-v7-c99/cmd/file.c
unix-v7-c99/cmd/find.c
unix-v7-c99/cmd/fish.c
unix-v7-c99/cmd/fortune.c
unix-v7-c99/cmd/getty.c
unix-v7-c99/cmd/graph.c
unix-v7-c99/cmd/grep.c
unix-v7-c99/cmd/hangman.c
unix-v7-c99/cmd/icheck.c
unix-v7-c99/cmd/init.c
unix-v7-c99/cmd/iostat.c
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
unix-v7-c99/cmd/passwd.c
unix-v7-c99/cmd/plot/chrtab.c
unix-v7-c99/cmd/pr.c
unix-v7-c99/cmd/ptx.c
unix-v7-c99/cmd/pwd.c
unix-v7-c99/cmd/quiz.c
unix-v7-c99/cmd/quot.c
unix-v7-c99/cmd/random.c
unix-v7-c99/cmd/restor.c
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
unix-v7-c99/cmd/spell/spell.c
unix-v7-c99/cmd/spell/spell.h
unix-v7-c99/cmd/spell/spellin.c
unix-v7-c99/cmd/spell/spellout.c
unix-v7-c99/cmd/spline.c
unix-v7-c99/cmd/split.c
unix-v7-c99/cmd/stty.c
unix-v7-c99/cmd/su.c
unix-v7-c99/cmd/sum.c
unix-v7-c99/cmd/sync.c
unix-v7-c99/cmd/tabs.c
unix-v7-c99/cmd/tail.c
unix-v7-c99/cmd/tar/tar.c
unix-v7-c99/cmd/tee.c
unix-v7-c99/cmd/test.c
unix-v7-c99/cmd/time.c
unix-v7-c99/cmd/tk.c
unix-v7-c99/cmd/touch.c
unix-v7-c99/cmd/tp/tp.h
unix-v7-c99/cmd/tp/tp0.c
unix-v7-c99/cmd/tp/tp1.c
unix-v7-c99/cmd/tp/tp2.c
unix-v7-c99/cmd/tp/tp3.c
unix-v7-c99/cmd/tp/tp_defs.h
unix-v7-c99/cmd/tr.c
unix-v7-c99/cmd/tsort.c
unix-v7-c99/cmd/tty.c
unix-v7-c99/cmd/umount.c
unix-v7-c99/cmd/uniq.c
unix-v7-c99/cmd/units.c
unix-v7-c99/cmd/update.c
unix-v7-c99/cmd/vpr.c
unix-v7-c99/cmd/wall.c
unix-v7-c99/cmd/wc.c
unix-v7-c99/cmd/who.c
unix-v7-c99/cmd/write.c
unix-v7-c99/cmd/wump.c
unix-v7-c99/cmd/yes.c
unix-v7-c99/conf/Makefile
unix-v7-c99/conf/c.c
unix-v7-c99/conf/putchar.c
unix-v7-c99/conf/qemu_arm/auxfs.proto
unix-v7-c99/conf/qemu_arm/root.proto
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
unix-v7-c99/dev/msgbuf.c (port-local: kernel msgbuf storage)
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
unix-v7-c99/include/a.out.h (port-local: hand-written from v7 a.out.h struct decls; ARM/ELF host has no v7-a.out layout)
unix-v7-c99/include/ctype.h
unix-v7-c99/include/dumprestor.h
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
unix-v7-c99/lib/acct.c
unix-v7-c99/lib/atof.c
unix-v7-c99/lib/atoi.c
unix-v7-c99/lib/atol.c
unix-v7-c99/lib/calloc.c
unix-v7-c99/lib/clrerr.c
unix-v7-c99/lib/compat.c
unix-v7-c99/lib/crt0.c
unix-v7-c99/lib/crt0.s
unix-v7-c99/lib/crypt.c
unix-v7-c99/lib/ctime.c
unix-v7-c99/lib/data.c
unix-v7-c99/lib/doprnt.c
unix-v7-c99/lib/doscan.c
unix-v7-c99/lib/endopen.c
unix-v7-c99/lib/errlst.c
unix-v7-c99/lib/execvp.c
unix-v7-c99/lib/fgetc.c
unix-v7-c99/lib/fgets.c
unix-v7-c99/lib/filbuf.c
unix-v7-c99/lib/findiop.c
unix-v7-c99/lib/flsbuf.c
unix-v7-c99/lib/fopen.c
unix-v7-c99/lib/fprintf.c
unix-v7-c99/lib/fputc.c
unix-v7-c99/lib/fputs.c
unix-v7-c99/lib/freopen.c
unix-v7-c99/lib/fseek.c
unix-v7-c99/lib/ftell.c
unix-v7-c99/lib/getchar.c
unix-v7-c99/lib/getenv.c
unix-v7-c99/lib/getlogin.c
unix-v7-c99/lib/getpass.c
unix-v7-c99/lib/getpwent.c
unix-v7-c99/lib/getpwnam.c
unix-v7-c99/lib/getpwuid.c
unix-v7-c99/lib/gets.c
unix-v7-c99/lib/index.c
unix-v7-c99/lib/isatty.c
unix-v7-c99/lib/l3.c
unix-v7-c99/lib/malloc.c
unix-v7-c99/lib/memcpy.c
unix-v7-c99/lib/mktemp.c
unix-v7-c99/lib/nlist.c (port-local: ARM/ELF nlist parser; v7 had a v7-a.out parser at v7/usr/src/libc/gen/nlist.c)
unix-v7-c99/lib/perror.c
unix-v7-c99/lib/printf.c
unix-v7-c99/lib/putchar.c
unix-v7-c99/lib/puts.c
unix-v7-c99/lib/qsort.c
unix-v7-c99/lib/rand.c
unix-v7-c99/lib/rdwr.c
unix-v7-c99/lib/rew.c
unix-v7-c99/lib/rindex.c
unix-v7-c99/lib/scanf.c
unix-v7-c99/lib/setbuf.c
unix-v7-c99/lib/sprintf.c
unix-v7-c99/lib/strcat.c
unix-v7-c99/lib/strcmp.c
unix-v7-c99/lib/strcpy.c
unix-v7-c99/lib/strlen.c
unix-v7-c99/lib/strncat.c
unix-v7-c99/lib/strncmp.c
unix-v7-c99/lib/strncpy.c
unix-v7-c99/lib/strout.c
unix-v7-c99/lib/swab.c
unix-v7-c99/lib/sys.s
unix-v7-c99/lib/syscall.s
unix-v7-c99/lib/system.c
unix-v7-c99/lib/tell.c
unix-v7-c99/lib/timezone.c
unix-v7-c99/lib/ttyname.c
unix-v7-c99/lib/ttyslot.c
unix-v7-c99/lib/u.ld
unix-v7-c99/lib/ungetc.c
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
        -not -path 'unix-v7-c99/root/etc/accton' \
        -not -path 'unix-v7-c99/root/etc/atrun' \
        -not -path 'unix-v7-c99/root/etc/update' \
        -not -path 'unix-v7-c99/root/etc/ac' \
        -not -path 'unix-v7-c99/root/etc/cron' \
        -not -path 'unix-v7-c99/root/etc/utmp.empty' \
        -not -path 'unix-v7-c99/root/unix' \
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
arch/arm.h
arch/armboot.c
arch/evb.ld
arch/machdep.c
arch/swtch.s
arch/u_bridge.c
arch/u_stub.c
arch/v7stubs.c
cmd/dkstat.c
cmd/sh/makefile
conf/Makefile
conf/qemu_arm/auxfs.proto
conf/qemu_arm/root.proto
conf/test_malloc.c
dev/mp135_blk.c
dev/msgbuf.c
dev/pl011.c
dev/stm32_usart.c
dev/virtio_blk.c
h/proto.h
include/a.out.h
include/stdio.h
lib/Makefile
lib/acct.c
lib/compat.c
lib/crt0.c
lib/doprnt.c (port-local: hand-written replacement for v7's PDP-11 doprnt.s; integer + %s/%c specifiers plus a minimal %f/%e/%g using libgcc softfp helpers)
lib/malloc.c
lib/memcpy.c
lib/nlist.c
lib/sys.s
lib/u.ld
root/etc/passwd
root/etc/ttys
sys/Makefile
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
> #include <stdio.h>
> #undef	puts
```

### lib/l3.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/l3.c unix-v7-c99/lib/l3.c || true
```

Expect:

```
3a4,5
> int ltol3(), l3tol();
> int
9c11
< 	register i;
---
> 	register int i;
22d23
< 		b++;
24a26
> 		b++;
26a29
> 	return(0);
28a32
> int
34c38
< 	register i;
---
> 	register int i;
47d50
< 		*a++ = 0;
49a53
> 		*a++ = 0;
51a56
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
17a18,46
> 
> /*
>  * ARM EABI label_t layout used by save/savu/aretu/resume in arch/swtch.s.
>  *
>  * label_t is declared `typedef int label_t[10]` in h/param.h.  The
>  * primitives stmia/ldmia the AAPCS callee-saved registers into it,
>  * followed by sp and lr, in this order:
>  *
>  *   label[0] = r4    label[5] = r9
>  *   label[1] = r5    label[6] = r10
>  *   label[2] = r6    label[7] = r11 (fp)
>  *   label[3] = r7    label[8] = sp
>  *   label[4] = r8    label[9] = lr
>  *
>  * save() captures this on entry and returns 0; aretu()/resume()
>  * restore from a label and make the original save() appear to
>  * return 1.  This mirrors the historic V7 savu/aretu contract on
>  * PDP-11 where label_t held r5 (frame pointer) and sp.
>  */
> #define	LABEL_R4	0
> #define	LABEL_R5	1
> #define	LABEL_R6	2
> #define	LABEL_R7	3
> #define	LABEL_R8	4
> #define	LABEL_R9	5
> #define	LABEL_R10	6
> #define	LABEL_R11	7
> #define	LABEL_SP	8
> #define	LABEL_LR	9
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

### cmd/dmesg.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/dmesg.c unix-v7-c99/cmd/dmesg.c || true
```

Expect:

```
23a24,27
> int done(char *);
> int pdate(void);
> 
> int
24a29
> int argc;
83a89
> int
99a106
> 	return(0);
101a109
> int
105c113
< 	static firstime;
---
> 	static int firstime;
112a121
> 	return(0);
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

### cmd/iostat.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/iostat.c unix-v7-c99/cmd/iostat.c || true
```

Expect:

```
0a1,2
> #include <stdio.h>
> 
7,8c9
< struct
< {
---
> struct nlent {
12,15d12
< } nl[] = {
< 	"_dk_busy", 0, 0,
< 	"_io_info", 0, 0,
< 	"\0\0\0\0\0\0\0\0", 0, 0
17,18c14,24
< struct
< {
---
> struct nlent nl[] = {
> 	{"_dk_busy", 0, 0},
> 	{"_io_info", 0, 0},
> 	{"_dk_time", 0, 0},
> 	{"_dk_numb", 0, 0},
> 	{"_dk_wds",  0, 0},
> 	{"_tk_nin",  0, 0},
> 	{"_tk_nout", 0, 0},
> 	{"\0\0\0\0\0\0\0\0", 0, 0}
> };
> struct sample {
38a45,53
> int	stats(int);
> int	stat1(int);
> int	stats2(double);
> int	stats3(double);
> int	biostats(void);
> int	atoi(char *);
> int	nlist(char *, struct nlent *);
> 
> int
39a55
> int argc;
43c59
< 	register  i;
---
> 	register  int i;
49c65
< 	if(nl[0].type == -1) {
---
> 	if(nl[0].type == 0) {
88a105,108
> 	/* The v7 original assumed dk_busy/etime/numb/wds/tin/tout were
> 	 * laid out contiguously in kernel .bss so a single read() filled
> 	 * `s`.  ELF link order doesn't honour that, so read each symbol
> 	 * individually into the matching slot. */
90c110,130
< 	read(mf, (char *)&s, sizeof s);
---
> 	read(mf, (char *)&s.busy, sizeof(s.busy));
> 	if (nl[2].type != 0) {
> 		lseek(mf, (long)nl[2].value, 0);
> 		read(mf, (char *)s.etime, sizeof(s.etime));
> 	}
> 	if (nl[3].type != 0) {
> 		lseek(mf, (long)nl[3].value, 0);
> 		read(mf, (char *)s.numb, sizeof(s.numb));
> 	}
> 	if (nl[4].type != 0) {
> 		lseek(mf, (long)nl[4].value, 0);
> 		read(mf, (char *)s.wds, sizeof(s.wds));
> 	}
> 	if (nl[5].type != 0) {
> 		lseek(mf, (long)nl[5].value, 0);
> 		read(mf, (char *)&s.tin, sizeof(s.tin));
> 	}
> 	if (nl[6].type != 0) {
> 		lseek(mf, (long)nl[6].value, 0);
> 		read(mf, (char *)&s.tout, sizeof(s.tout));
> 	}
91a132
> 		if (i >= 32) break;
139a181
> 	return(0);
148a191
> int
149a193
> int dn;
151c195
< 	register i;
---
> 	register int i;
165c209
< 		return;
---
> 		return(0);
175a220
> 	return(0);
177a223
> int
178a225
> int o;
180c227
< 	register i;
---
> 	register int i;
194a242
> 	return(0);
196a245
> int
200c249
< 	register i, j;
---
> 	register int i, j;
206a256
> 	return(0);
208a259
> int
212c263
< 	register i;
---
> 	register int i;
251a303
> 	return(0);
253a306
> int
256c309
< register i;
---
> 	register int i;
257a311,312
> 	if (nl[1].type == 0)
> 		return(0);
270a326
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
133c133
< typedef	int		label_t[6];	/* regs 2-7 */
---
> typedef	int		label_t[10];	/* ARM callee-saved: r4-r11, sp, lr (see h/reg.h) */
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
5c5
< typedef	int        	label_t[6]; 	/* program status */
---
> typedef	int        	label_t[10];	/* ARM callee-saved: r4-r11, sp, lr (see h/reg.h) */
```

### sys/iget.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/iget.c unix-v7-c99/sys/iget.c || true
```

Expect:

```
109d108
< 		*p1++ = 0;
111a111
> 		*p1++ = 0;
161c161
< 			return;
---
> 			return(0);
165c165
< 			return;
---
> 			return(0);
177a178,179
> 			*p1++ = *p2++;
> 			*p1++ = *p2++;
181,182d182
< 			*p1++ = *p2++;
< 			*p1++ = *p2++;
213c213
< 		return;
---
> 		return(0);
257c257
< 				return;
---
> 				return(0);
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
131c131,132
< catch()
---
> void
> catch(int sig)
132a134
> 	(void)sig;
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
133c136
< typedef	int		label_t[6];	/* regs 2-7 */
---
> typedef	int		label_t[10];	/* ARM callee-saved: r4-r11, sp, lr (see h/reg.h) */
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

```

### include/ctype.h

Local test:

```
diff unix-v7-c99/v7/usr/include/ctype.h unix-v7-c99/include/ctype.h || true
```

Expect:

```
1,24c1,8
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
> #define	tolower(c)	(isupper(c)?(c)-'A'+'a':(c))
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

### include/sys/dir.h

Local test:

```
diff unix-v7-c99/v7/usr/include/sys/dir.h unix-v7-c99/include/sys/dir.h || true
```

Expect:

```
0a1,2
> #ifndef SYS_DIR_H
> #define SYS_DIR_H
8a11
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
16,28c20,31
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
> #define	S_ISUID	0004000
> #define	S_ISGID	0002000
> #define	S_ISVTX	0001000
> #endif
```

### include/sys/timeb.h

Local test:

```
diff unix-v7-c99/v7/usr/include/sys/timeb.h unix-v7-c99/include/sys/timeb.h || true
```

Expect:

```
0a1,3
> #ifndef SYS_TIMEB_H
> #define SYS_TIMEB_H
> #include <sys/types.h>
9a13
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

### sys/prim.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/prim.c unix-v7-c99/sys/prim.c || true
```

Expect:

```

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
> #include <stdio.h>
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
> #include <stdio.h>
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
> #include <stdio.h>
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
> #include <stdio.h>
6,7c7,10
< extern	char **environ;
< char	*nvmatch();
---
> static char *empty[] = { 0 };
> char **environ = empty;
> int errno;
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
> #include <stdio.h>
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
4a5
> #include <stdio.h>
8c9,10
< char	*sys_errlist[];
---
> char	*sys_errlist[1];
> void
13c15
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
0a1
> #include <stdio.h>
7c8
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
> #include <stdio.h>
17a19
> int f;
23c25
< 	register df;
---
> 	register int df;
```

### lib/qsort.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/qsort.c unix-v7-c99/lib/qsort.c || true
```

Expect:

```
3a4
> static void qs1(), qsexc(), qstexc();
4a6
> void
6c8
< char *a;
---
> void *a;
13c15
< 	qs1(a, a+n*es);
---
> 	qs1(a, (char *)a+n*es);
16c18,19
< static qs1(a, l)
---
> static void
> qs1(a, l)
20,21c23
< 	register es;
< 	char **k;
---
> 	register int es;
30c32
< 	if((n=l-a) <= es)
---
> 	if((n=l-a) <= (unsigned)es)
87c89,90
< static qsexc(i, j)
---
> static void
> qsexc(i, j)
103c106,107
< static qstexc(i, j, k)
---
> static void
> qstexc(i, j, k)
```

### lib/calloc.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/calloc.c unix-v7-c99/lib/calloc.c || true
```

Expect:

```
2a3
> #include <stdio.h>
4d4
< #define NULL 0
11d10
< 	char *malloc();
13c12
< 	register m;
---
> 	register int m;
25a25
> int
29a30
> 	(void)num; (void)size;
30a32
> 	return(0);
```

### lib/tell.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/tell.c unix-v7-c99/lib/tell.c || true
```

Expect:

```
5c5
< long	lseek();
---
> extern long lseek(int, long, int);
7a8
> int f;
```

### lib/system.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/system.c unix-v7-c99/lib/system.c || true
```

Expect:

```
0a1
> #include	<stdio.h>
2a4
> int
13,14c15,16
< 	istat = signal(SIGINT, SIG_IGN);
< 	qstat = signal(SIGQUIT, SIG_IGN);
---
> 	istat = (int (*)())signal(SIGINT, (int)SIG_IGN);
> 	qstat = (int (*)())signal(SIGQUIT, (int)SIG_IGN);
19,20c21,22
< 	signal(SIGINT, istat);
< 	signal(SIGQUIT, qstat);
---
> 	signal(SIGINT, (int)istat);
> 	signal(SIGQUIT, (int)qstat);
```

### lib/timezone.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/timezone.c unix-v7-c99/lib/timezone.c || true
```

Expect:

```
8a9
> #include <stdio.h>
24a26
> int zone, dst;
```

### lib/getlogin.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/getlogin.c unix-v7-c99/lib/getlogin.c || true
```

Expect:

```
0a1
> #include <stdio.h>
1a3
> extern int ttyslot(void);
9c11
< 	register me, uf;
---
> 	register int me, uf;
16c18
< 	lseek( uf, (long)(me*sizeof(ubuf)), 0 );
---
> 	lseek( uf, (long)(me*(int)sizeof(ubuf)), 0 );
```

### lib/atof.c

On disk but not linked into LIB: pulling libgcc's softfp helpers into every
binary overflows the rootfs.  See `lib/Makefile`.

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/atof.c unix-v7-c99/lib/atof.c || true
```

Expect:

```
5d4
< #include <math.h>
6a6,15
> #define LOGHUGE 39
> static double
> ldexp(value, n)
> double value;
> int n;
> {
> 	while (n > 0) { value *= 2.0; n--; }
> 	while (n < 0) { value *= 0.5; n++; }
> 	return(value);
> }
12c21
< 	register c;
---
> 	register int c;
15d23
< 	double ldexp();
17c25
< 	register eexp, exp, neg, negexp, bexp;
---
> 	register int eexp, exp, neg, negexp, bexp;
```


### lib/clrerr.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/clrerr.c unix-v7-c99/lib/clrerr.c || true
```

Expect:

```
2a3
> void
```

### lib/data.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/data.c unix-v7-c99/lib/data.c || true
```

Expect:

```

```

### lib/doscan.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/doscan.c unix-v7-c99/lib/doscan.c || true
```

Expect:

```
2a3
> #include	<stdarg.h>
13a15
> int	_innum(), _instr();
25a28
> int
29c32
< register int **argp;
---
> va_list *argp;
30a34
> 	int *slot;
44,46c48,51
< 		if (ch != '*')
< 			ptr = argp++;
< 		else
---
> 		if (ch != '*') {
> 			slot = va_arg(*argp, int *);
> 			ptr = &slot;
> 		} else
96a102
> int
98a105
> int type, len, size;
104c111
< 	register c, base;
---
> 	register int c, base;
204a212
> int
206a215
> int type, len;
210c219
< 	register ch;
---
> 	register int ch;
254c263
< 	register c, t;
---
> 	register int c, t;
```

### lib/endopen.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/endopen.c unix-v7-c99/lib/endopen.c || true
```

Expect:

```
2a3
> static int create();
```

### lib/fgetc.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/fgetc.c unix-v7-c99/lib/fgetc.c || true
```

Expect:

```
2a3
> int
```

### lib/fgets.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/fgets.c unix-v7-c99/lib/fgets.c || true
```

Expect:

```
6a7
> int n;
8c9
< 	register c;
---
> 	register int c;
```

### lib/filbuf.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/filbuf.c unix-v7-c99/lib/filbuf.c || true
```

Expect:

```

```

### lib/findiop.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/findiop.c unix-v7-c99/lib/findiop.c || true
```

Expect:

```

```

### lib/flsbuf.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/flsbuf.c unix-v7-c99/lib/flsbuf.c || true
```

Expect:

```
11c11
< 	register n, rn;
---
> 	register int n, rn;
63c63
< 	register n;
---
> 	register int n;
80a81
> void
94c95
< 	register r;
---
> 	register int r;
107,108c108,109
< 	iop->_flag &=
< 		~(_IOREAD|_IOWRT|_IONBF|_IOMYBUF|_IOERR|_IOEOF|_IOSTRG|_IORW);
---
> 	iop->_flag = (char)(iop->_flag &
> 		~(_IOREAD|_IOWRT|_IONBF|_IOMYBUF|_IOERR|_IOEOF|_IOSTRG|_IORW));
```

### lib/fopen.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/fopen.c unix-v7-c99/lib/fopen.c || true
```

Expect:

```

```

### lib/fprintf.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/fprintf.c unix-v7-c99/lib/fprintf.c || true
```

Expect:

```
1a2,3
> #include	<stdarg.h>
> extern void _doprnt();
3,5c5,6
< fprintf(iop, fmt, args)
< FILE *iop;
< char *fmt;
---
> int
> fprintf(FILE *iop, char *fmt, ...)
7c8,11
< 	_doprnt(fmt, &args, iop);
---
> 	va_list ap;
> 	va_start(ap, fmt);
> 	_doprnt(fmt, &ap, iop);
> 	va_end(ap);
```

### lib/fputc.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/fputc.c unix-v7-c99/lib/fputc.c || true
```

Expect:

```
2a3
> int
3a5
> int c;
```

### lib/fputs.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/fputs.c unix-v7-c99/lib/fputs.c || true
```

Expect:

```
2a3
> int
7,8c8,9
< 	register r;
< 	register c;
---
> 	register int r;
> 	register int c;
```

### lib/freopen.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/freopen.c unix-v7-c99/lib/freopen.c || true
```

Expect:

```

```

### lib/fseek.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/fseek.c unix-v7-c99/lib/fseek.c || true
```

Expect:

```
8a9
> int
11a13
> 	int ptrname;
```

### lib/ftell.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/ftell.c unix-v7-c99/lib/ftell.c || true
```

Expect:

```
14c14
< 	register adjust;
---
> 	register int adjust;
```

### lib/getchar.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/getchar.c unix-v7-c99/lib/getchar.c || true
```

Expect:

```
7a8
> int
```

### lib/getpass.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/getpass.c unix-v7-c99/lib/getpass.c || true
```

Expect:

```
12c12
< 	register c;
---
> 	register int c;
15d14
< 	int (*signal())();
22c21
< 	sig = signal(SIGINT, SIG_IGN);
---
> 	sig = (int (*)())signal(SIGINT, (int)SIG_IGN);
36c35
< 	signal(SIGINT, sig);
---
> 	signal(SIGINT, (int)sig);
```

### lib/gets.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/gets.c unix-v7-c99/lib/gets.c || true
```

Expect:

```
7c7
< 	register c;
---
> 	register int c;
```

### lib/printf.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/printf.c unix-v7-c99/lib/printf.c || true
```

Expect:

```
1a2,3
> #include	<stdarg.h>
> extern void _doprnt();
3,4c5,6
< printf(fmt, args)
< char *fmt;
---
> int
> printf(char *fmt, ...)
6c8,11
< 	_doprnt(fmt, &args, stdout);
---
> 	va_list ap;
> 	va_start(ap, fmt);
> 	_doprnt(fmt, &ap, stdout);
> 	va_end(ap);
```

### lib/putchar.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/putchar.c unix-v7-c99/lib/putchar.c || true
```

Expect:

```
7a8
> int
9c10
< register c;
---
> register int c;
11c12
< 	putc(c, stdout);
---
> 	return(putc(c, stdout));
```

### lib/puts.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/puts.c unix-v7-c99/lib/puts.c || true
```

Expect:

```
2a3
> int
6c7
< 	register c;
---
> 	register int c;
```

### lib/rdwr.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/rdwr.c unix-v7-c99/lib/rdwr.c || true
```

Expect:

```
2a3
> int
8c9
< 	register c;
---
> 	register int c;
24a26
> int
```

### lib/rew.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/rew.c unix-v7-c99/lib/rew.c || true
```

Expect:

```
2a3
> void
```

### lib/scanf.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/scanf.c unix-v7-c99/lib/scanf.c || true
```

Expect:

```
1a2,3
> #include	<stdarg.h>
> int	_doscan();
3,4c5,6
< scanf(fmt, args)
< char *fmt;
---
> int
> scanf(char *fmt, ...)
6c8,13
< 	return(_doscan(stdin, fmt, &args));
---
> 	va_list ap;
> 	int r;
> 	va_start(ap, fmt);
> 	r = _doscan(stdin, fmt, &ap);
> 	va_end(ap);
> 	return(r);
9,11c16,17
< fscanf(iop, fmt, args)
< FILE *iop;
< char *fmt;
---
> int
> fscanf(FILE *iop, char *fmt, ...)
13c19,24
< 	return(_doscan(iop, fmt, &args));
---
> 	va_list ap;
> 	int r;
> 	va_start(ap, fmt);
> 	r = _doscan(iop, fmt, &ap);
> 	va_end(ap);
> 	return(r);
16,18c27,28
< sscanf(str, fmt, args)
< register char *str;
< char *fmt;
---
> int
> sscanf(char *str, char *fmt, ...)
20a31,32
> 	va_list ap;
> 	int r;
27c39,42
< 	return(_doscan(&_strbuf, fmt, &args));
---
> 	va_start(ap, fmt);
> 	r = _doscan(&_strbuf, fmt, &ap);
> 	va_end(ap);
> 	return(r);
```

### lib/setbuf.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/setbuf.c unix-v7-c99/lib/setbuf.c || true
```

Expect:

```
2a3
> void
```

### lib/sprintf.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/sprintf.c unix-v7-c99/lib/sprintf.c || true
```

Expect:

```
1a2,3
> #include	<stdarg.h>
> extern void _doprnt();
3,4c5,6
< char *sprintf(str, fmt, args)
< char *str, *fmt;
---
> char *
> sprintf(char *str, char *fmt, ...)
6a9
> 	va_list ap;
11c14,16
< 	_doprnt(fmt, &args, &_strbuf);
---
> 	va_start(ap, fmt);
> 	_doprnt(fmt, &ap, &_strbuf);
> 	va_end(ap);
```

### lib/strout.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/strout.c unix-v7-c99/lib/strout.c || true
```

Expect:

```
2a3
> void
5c6
< register count;
---
> register int count;
7a9
> int fillch;
```

### lib/ungetc.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/ungetc.c unix-v7-c99/lib/ungetc.c || true
```

Expect:

```
2a3
> int
3a5
> int c;
10c12
< 			*iop->_ptr++;
---
> 			iop->_ptr++;
```

### lib/ctime.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/ctime.c unix-v7-c99/lib/ctime.c || true
```

Expect:

```
30c30
<  *	Thu Jan 01 00:00:00 1970n0\\
---
>  *	Thu Jan 01 00:00:00 1970n0\\
72c72
< char		*ct_numb();
---
> static char	*ct_numb();
76a77,79
> static int	sunday();
> int	dysize();
> int	ftime();
91c94
< 	register daylbegin, daylend;
---
> 	register int daylbegin, daylend;
122c125
< static
---
> static int
226a230
> int
227a232
> int y;
236a242
> int n;
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


### cmd/accton.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/accton.c unix-v7-c99/cmd/accton.c || true
```

Expect:

```
0a1,3
> #include <stdio.h>
> 
> int
1a5
> int argc;
4c8,9
< 	extern errno;
---
> 	extern int errno;
> 	int acct();
```

### cmd/update.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/update.c unix-v7-c99/cmd/update.c || true
```

Expect:

```
5a6
> #include <stdio.h>
7a9,10
> int	dosync();
> 
14a18
> int
30a35
> int
34c39
< 	signal(SIGALRM, dosync);
---
> 	signal(SIGALRM, (int)dosync);
35a41
> 	return(0);
```

### cmd/atrun.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/atrun.c unix-v7-c99/cmd/atrun.c || true
```

Expect:

```
13a14,15
> int	makenowtime(), updatetime(), run();
> 
17a20
> int
18a22
> int argc;
24a29
> 	(void)argc; (void)argv;
51a57
> int
55d60
< 	struct tm *localtime();
62a68
> 	return(0);
64a71
> int
65a73
> int t;
74a83
> 	return(0);
76a86
> int
81c91
< 	register pid, i;
---
> 	register int pid, i;
85c95
< 		return;
---
> 		return(0);
99,100c109,110
< 		wait((int *)0);
< 		unlink(file);
---
> 	wait((int *)0);
> 	unlink(file);
107a118
> 	return(0);
```

### cmd/passwd.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/passwd.c unix-v7-c99/cmd/passwd.c || true
```

Expect:

```
13,14d12
< struct	passwd *getpwent();
< int	endpwent();
22a21
> int
24c23,24
< char *argv[];
---
> int	argc;
> char	*argv[];
111,113c111,113
< 	signal(SIGHUP, SIG_IGN);
< 	signal(SIGINT, SIG_IGN);
< 	signal(SIGQUIT, SIG_IGN);
---
> 	signal(SIGHUP, (int)SIG_IGN);
> 	signal(SIGINT, (int)SIG_IGN);
> 	signal(SIGQUIT, (int)SIG_IGN);
```

### cmd/diff3.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/diff3.c unix-v7-c99/cmd/diff3.c || true
```

Expect:

```
6c6
< /* diff3 [-e] d13 d23 f1 f2 f3 
---
> /* diff3 [-e] d13 d23 f1 f2 f3
44a45,49
> int readin(), number(), digit(), getchange(), getline(), merge(),
>     separate(), change(), prange(), keep(), skip(), duplicate(),
>     repos(), trouble(), edit(), edscript();
> 
> int
45a51
> int argc;
48c54
< 	register i,m,n;
---
> 	register int i,m,n;
74a81
> 	return(0);
84a92
> int
89c97
< 	register i;
---
> 	register int i;
127a136
> int
131c140
< 	register nn;
---
> 	register int nn;
137a147
> int
138a149
> int c;
142a154
> int
151a164
> int
155,156c168,169
< 	register i, c;
< 	for(i=0;i<sizeof(line)-1;i++) {
---
> 	register int i, c;
> 	for(i=0;i<(int)sizeof(line)-1;i++) {
168a182
> int
169a184
> int m1, m2;
265a281
> 	return(0);
267a284
> int
271a289
> 	return(0);
277a296
> int
278a298
> int i;
279a300
> int dup;
285c306
< 		return;
---
> 		return(0);
287c308
< 		return;
---
> 		return(0);
290a312
> 	return(0);
295a318
> int
306a330
> 	return(0);
313a338
> int
314a340
> int i;
317c343
< 	register delta;
---
> 	register int delta;
318a345
> 	(void)rold;
322a350
> 	return(0);
328a357
> int
329a359
> int i, from;
332c362
< 	register j,n;
---
> 	register int j,n;
346a377
> int
350,351c381,382
< 	register c,d;
< 	register nchar;
---
> 	register int c,d;
> 	register int nchar;
367c398
< 				return;
---
> 				return(0);
374a406
> int
375a408
> int nchar;
377,378c410,411
< 	register i;
< 	for(i=0;i<2;i++) 
---
> 	register int i;
> 	for(i=0;i<2;i++)
379a413
> 	return(0);
381a416
> int
385a421
> 	return(0);
389a426
> int
391a429
> int dup, j;
405a444
> int
406a446
> int n;
408c448
< 	register j,k;
---
> 	register int j,k;
420a461
> 	return(0);
```

### cmd/fortune.c

Local test:

```
diff unix-v7-c99/v7/usr/src/games/fortune.c unix-v7-c99/cmd/fortune.c || true
```

Expect:

```
5a6
> int
```

### cmd/arithmetic.c

Local test:

```
diff unix-v7-c99/v7/usr/src/games/arithmetic.c unix-v7-c99/cmd/arithmetic.c || true
```

Expect:

```
0a1
> #include <stdio.h>
4a6,7
> int	getnum(), random(), skrand(), score(), getline(), delete();
> 
13a17
> int
14a19
> int	argc;
20c25
< 	extern	delete();
---
> 	extern int delete();
22c27
< 	signal(SIGINT, delete);
---
> 	signal(SIGINT, (int)delete);
120a126
> int
139a146
> 	return(0);
141a149
> int
155a164
> int
156a166
> int range;
161c171,174
< skrand(range){
---
> int
> skrand(range)
> int range;
> {
167a181
> int
175c189
< 	if(rights == 0)	return;
---
> 	if(rights == 0)	return(0);
182a197
> 	return(0);
184a200
> int
192a209
> 	return(0);
```

### cmd/hangman.c

Local test:

```
diff unix-v7-c99/v7/usr/src/games/hangman.c unix-v7-c99/cmd/hangman.c || true
```

Expect:

```
8a9,11
> int	setup(), startnew(), stateout(), getguess(), wordout(),
> 	youwon(), fatal(), getword(), pscore();
> double	frand();
14c17,18
< main(argc,argv) char **argv;
---
> int
> main(argc,argv) int argc; char **argv;
30a35
> int
34c39
< 	time(tvec);
---
> 	time((long *)tvec);
38a44
> 	return(0);
44a51
> int
55a63
> 	return(0);
56a65
> int
63a73
> 	return(0);
64a75
> int
92c103
< 		return;
---
> 		return(0);
95c106
< 		if(word[i]=='.') return;
---
> 		if(word[i]=='.') return(0);
98c109
< 	return;
---
> 	return(0);
99a111
> int
103a116
> 	return(0);
104a118
> int
107a122
> 	return(0);
108a124
> int
112a129
> 	return(0);
113a131
> int
133a152
> 	return(0);
135,136c154,155
< long int freq[]
< {	42066,	9228,	24412,	14500,	55162,
---
> long int freq[]={
> 	42066,	9228,	24412,	14500,	55162,
142a162
> int
145a166
> 	return(0);
```

### cmd/ac.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/ac.c unix-v7-c99/cmd/ac.c || true
```

Expect:

```
35c35,39
< main(argc, argv) 
---
> int	loop(), print(), upall(), update(), among(), newday(), pdate();
> 
> int
> main(argc, argv)
> int argc;
39c43
< 	register i;
---
> 	register int i;
91a96
> int
94c99
< 	register i;
---
> 	register int i;
100c105
< 		return;
---
> 		return(0);
104c109
< 			return;
---
> 			return(0);
108c113
< 		return;
---
> 		return(0);
125c130
< 		return;
---
> 		return(0);
134a140
> 	return(0);
136a143
> int
157a165
> 	return(0);
159a168
> int
160a170
> int f;
165a176
> 	return(0);
167a179
> int
169a182
> int f;
186c199
< 		return;
---
> 		return(0);
189c202
< 		return;
---
> 		return(0);
200a214
> 	return(0);
202a217
> int
203a219
> int i;
205c221
< 	register j, k;
---
> 	register int j, k;
222a239
> int
237a255
> 	return(0);
239a258
> int
246c265
< 		return;
---
> 		return(0);
248a268
> 	return(0);
```

### cmd/at.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/at.c unix-v7-c99/cmd/at.c || true
```

Expect:

```
10a11
> #define	utime	at_utime
28c29
< 	char *mname; 
---
> 	char *mname;
56a58
> int	pclose(FILE *f);
57a60,62
> int	makeutime(), makeuday(), filename(), onintr();
> 
> int
58a64
> int argc;
61,62c67,68
< 	extern onintr();
< 	register c;
---
> 	extern int onintr();
> 	register int c;
92,93c98,99
< 	if (signal(SIGINT, SIG_IGN) != SIG_IGN)
< 		signal(SIGINT, onintr);
---
> 	if ((int (*)())signal(SIGINT, (int)SIG_IGN) != (int (*)())SIG_IGN)
> 		signal(SIGINT, (int)onintr);
117a124
> int
119c126
< char *pp; 
---
> char *pp;
121c128
< 	register val;
---
> 	register int val;
197a205
> 	return(0);
200a209
> int
201a211
> int argc;
287a298
> int
289a301
> int y, d, t;
291c303
< 	register i;
---
> 	register int i;
297c309
< 			return;
---
> 			return(0);
300a313
> int
304a318
> 	return(0);
```

### cmd/cron.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/cron.c unix-v7-c99/cmd/cron.c || true
```

Expect:

```
24a25,27
> int	slp(), ex(), init(), number();
> 
> int
38,40c41,43
< 	signal(SIGHUP, SIG_IGN);
< 	signal(SIGINT, SIG_IGN);
< 	signal(SIGQUIT, SIG_IGN);
---
> 	signal(SIGHUP, (int)SIG_IGN);
> 	signal(SIGINT, (int)SIG_IGN);
> 	signal(SIGQUIT, (int)SIG_IGN);
70a74
> 	return(0);
75a80
> int v;
109a115
> int
112c118
< 	register i;
---
> 	register int i;
118a125
> 	return(0);
120a128
> int
128c136
< 		return;
---
> 		return(0);
134a143
> 	return(0);
136a146
> int
139c149
< 	register i, c;
---
> 	register int i, c;
232c242
< 			return;
---
> 			return(0);
238a249
> int
240c251
< register c;
---
> register int c;
242c253
< 	register n = 0;
---
> 	register int n = 0;
```

### cmd/quot.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/quot.c unix-v7-c99/cmd/quot.c || true
```

Expect:

```
44a45
> int	scanf(char *fmt, ...);
45a47,49
> int	check(), acct(), bread(), qcmp(), report();
> 
> int
46a51
> int argc;
86a92
> int
91c97
< 	register c;
---
> 	register int c;
96c102
< 		return;
---
> 		return(0);
115a122
> 	return(0);
117a125
> int
121c129
< 	register n;
---
> 	register int n;
123c131
< 	static fino;
---
> 	static int fino;
126c134
< 		return;
---
> 		return(0);
129c137
< 			return;
---
> 			return(0);
136c144
< 		return;
---
> 		return(0);
139c147
< 		return;
---
> 		return(0);
146,149c154,157
< 				return;
< 		if (fino > ino)
< 			return;
< 		if (fino<ino) {
---
> 				return(0);
> 		if (fino > (int)ino)
> 			return(0);
> 		if (fino<(int)ino) {
167a176
> 	return(0);
169a179
> int
172a183
> int cnt;
179a191
> 	return(0);
181a194
> int
191a205
> int
194c208
< 	register i;
---
> 	register int i;
197c211
< 		return;
---
> 		return(0);
206c220
< 		return;
---
> 		return(0);
211c225
< 			return;
---
> 			return(0);
219a234
> 	return(0);
227c242
< 	register n;
---
> 	register int n;
```

### cmd/dump.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/dump.c unix-v7-c99/cmd/dump.c || true
```

Expect:

```
52a53,55
> int	pass(), otape(), bread(), spclrec(), bitmap(), bmapest(), CLR(),
> 	getitime(), putitime(), est(), indir(), flusht(), taprec();
> int	l3tol();
57a61
> int
58a63
> int argc;
62c67
< 	register i;
---
> 	register int i;
174a180
> int
179c185
< 	register i, j;
---
> 	register int i, j;
210a217
> 	return(0);
212a220
> int
217c225
< 	register i;
---
> 	register int i;
228a237
> 	return(0);
230a240
> int
233a244
> int n;
235c246
< 	register i;
---
> 	register int i;
242c253
< 		for(i=0; i<NINDIR; i++) {
---
> 		for(i=0; i<(int)NINDIR; i++) {
249c260
< 		for(i=0; i<NINDIR; i++) {
---
> 		for(i=0; i<(int)NINDIR; i++) {
254a266
> 	return(0);
256a269
> int
260c273
< 	register f;
---
> 	register int f;
264c277
< 		return;
---
> 		return(0);
272c285
< 			return;
---
> 			return(0);
274a288
> 	return(0);
276a291
> int
282c297
< 		return;
---
> 		return(0);
293a309
> 	return(0);
295a312
> int
299c316
< 	register i;
---
> 	register int i;
312c329
< 		return;
---
> 		return(0);
314a332
> 	return(0);
316a335
> int
318a338
> int n;
320c340
< 	register i, t;
---
> 	register int i, t;
329a350
> 	return(0);
331a353
> int
333a356
> int typ;
335c358
< 	register i, n;
---
> 	register int i, n;
343c366
< 		return;
---
> 		return(0);
351a375
> 	return(0);
353a378
> int
356c381
< 	register i, *ip, s;
---
> 	register int i, *ip, s;
363c388
< 	for(i=0; i<BSIZE/sizeof(*ip); i++)
---
> 	for(i=0; i<(int)(BSIZE/sizeof(*ip)); i++)
366a392
> 	return(0);
368a395
> int
373c400
< 	register i;
---
> 	register int i;
378c405
< 		return;
---
> 		return(0);
380c407
< 	for(i=0; i<DIRPB; i++) {
---
> 	for(i=0; i<(int)DIRPB; i++) {
393c420
< 			return;
---
> 			return(0);
397a425
> 	return(0);
399a428
> int
401a431
> 	return(0);
403a434
> int
406a438
> int c;
408c440
< 	register n;
---
> 	register int n;
413a446
> 	return(0);
415a449
> int
419c453
< 	register n;
---
> 	register int n;
424a459
> 	return(0);
431a467
> int
435c471
< 	register i;
---
> 	register int i;
443a480
> 	return(0);
445a483
> int
451c489
< 		return;
---
> 		return(0);
456a495
> 	return(0);
458a498
> int
462c502
< 	register i, si;
---
> 	register int i, si;
490a531
> 	return(0);
492a534
> int
504a547
> 	return(0);
519a563
> int
522c566
< 	register i, df;
---
> 	register int i, df;
545c589
< 		return;
---
> 		return(0);
560a605
> int
563c608
< 	register i, n, df;
---
> 	register int i, n, df;
568c613
< 		return;
---
> 		return(0);
608a654
> 	return(0);
610a657
> int
623a671
> 	return(0);
625a674
> int
629c678
< 	register i, n;
---
> 	register int i, n;
636c685
< 		return;
---
> 		return(0);
638a688
> 	return(0);
```

### cmd/dumpdir.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/dumpdir.c unix-v7-c99/cmd/dumpdir.c || true
```

Expect:

```
50a51,56
> int	readhdr(), checkvol(), pass1(), printem(), gethead(), checktype(),
> 	readbits(), flsh(), getfile(), putent(), mseek(), getent(), direq(),
> 	search(), readtape(), clearbuf(), flsht(), copy(), writec(), readc(),
> 	checksum(), putdir(), null();
> 
> int
51a58
> int argc;
86c93
< 	i = 0;
---
> int	i = 0;
90a98
> int
93c101
< 	register i;
---
> 	register int i;
113c121
< 			return;
---
> 			return(0);
126a135
> int
139c148
< 	return;
---
> 	return(0);
145c154
< 			return;
---
> 			return(0);
168a178
> int
174c184
< 	register i;
---
> 	register int i;
177a188
> 	(void)n;
187c198
< 			return;
---
> 			return(0);
205c216
< 				return;
---
> 				return(0);
214a226
> int
218c230
< 	register i;
---
> 	register int i;
249c261
< 			return;
---
> 			return(0);
252a265
> 	return(0);
254a268
> int
257a272
> 	return(0);
259a275
> int
261a278
> int s;
263c280
< 	register i;
---
> 	register int i;
268a286
> 	return(0);
270a289
> int
274c293
< 	register i;
---
> 	register int i;
279a299
> 	return(0);
285a306
> int
289c310
< 	register i;
---
> 	register int i;
291c312
< 	for (i = 0; i < sizeof(ino_t); i++)
---
> 	for (i = 0; i < (int)sizeof(ino_t); i++)
296c317
< 			return;
---
> 			return(0);
298c319
< 	return;
---
> 	return(0);
300a322
> int
304c326
< 	register i;
---
> 	register int i;
306c328
< 	for (i = 0; i < sizeof(ino_t); i++)
---
> 	for (i = 0; i < (int)sizeof(ino_t); i++)
310,311c332,333
< 			return;
< 	return;
---
> 			return(0);
> 	return(0);
316a339
> int
321a345
> 	return(0);
323a348
> int
331a357
> int
335a362
> 	return(0);
337a365
> int
340a369
> 	return(0);
346a376
> int
350c380
< 	register low, high, probe;
---
> 	register int low, high, probe;
367a398
> int
371c402
< 	register i;
---
> 	register int i;
385a417
> int
397a430
> int
405a439
> int
409c443
< 	register i, j;
---
> 	register int i, j;
422a457
> int
431a467
> int
441a478
> int
446c483
< 	register i;
---
> 	register int i;
452a490
> 	return(0);
457a496
> int
461c500
< 	register i;
---
> 	register int i;
470a510
> 	return(0);
473c513
< null() { ; }
---
> int null() { return(0); }
```

### cmd/restor.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/restor.c unix-v7-c99/cmd/restor.c || true
```

Expect:

```
83a84,93
> int	doit(), readhdr(), checkvol(), pass1(), readbits(), gethead(),
> 	checktype(), ishead(), readtape(), flsht(), getfile(), psearch(),
> 	getdino(), putdino(), itrunc(), clri(), dread(), dwrite(),
> 	rstrfile(), rstrskip(), xtrfile(), skip(), checksum(), putent(),
> 	putdir(), null(), copy(), clearbuf(), writec(), readc(), mseek(),
> 	getent(), direq(), flsh(), bfree(), tloop();
> int	l3tol(), ltol3();
> daddr_t	balloc(), bmap();
> 
> int
84a95
> int argc;
120,123c131,134
< 		if (signal(SIGINT, done) == SIG_IGN)
< 			signal(SIGINT, SIG_IGN);
< 		if (signal(SIGTERM, done) == SIG_IGN)
< 			signal(SIGTERM, SIG_IGN);
---
> 		if (signal(SIGINT, (int)done) == (int)SIG_IGN)
> 			signal(SIGINT, (int)SIG_IGN);
> 		if (signal(SIGTERM, (int)done) == (int)SIG_IGN)
> 			signal(SIGTERM, (int)SIG_IGN);
142a154
> int
149c161
< 	register i, k;
---
> 	register int i, k;
179c191
< 		return;
---
> 		return(0);
208c220
< 			return;
---
> 			return(0);
251c263
< 					return;
---
> 					return(0);
300c312
< 			if (gets(tbf) == EOF) {
---
> 			if ((int)gets(tbf) == EOF) {
340c352
< 				return;
---
> 				return(0);
397a410
> 	return(0);
404a418
> int
407c421
< 	register i;
---
> 	register int i;
427c441
< 			return;
---
> 			return(0);
445a460
> int
451c466
< 	register i;
---
> 	register int i;
466c481
< 			return;
---
> 			return(0);
485c500
< 				return;
---
> 				return(0);
494a510
> int
498c514
< 	register i;
---
> 	register int i;
533c549
< 			return;
---
> 			return(0);
536a553
> 	return(0);
538a556
> int
541a560
> 	return(0);
543a563
> int
545a566
> int s;
547c568
< 	register i;
---
> 	register int i;
552a574
> 	return(0);
554a577
> int
558c581
< 	register i;
---
> 	register int i;
563a587
> 	return(0);
570a595
> int
574c599
< 	register i;
---
> 	register int i;
576c601
< 	for (i = 0; i < sizeof(ino_t); i++)
---
> 	for (i = 0; i < (int)sizeof(ino_t); i++)
581c606
< 			return;
---
> 			return(0);
583c608
< 	return;
---
> 	return(0);
585a611
> int
589c615
< 	register i;
---
> 	register int i;
591c617
< 	for (i = 0; i < sizeof(ino_t); i++)
---
> 	for (i = 0; i < (int)sizeof(ino_t); i++)
595,596c621,622
< 			return;
< 	return;
---
> 			return(0);
> 	return(0);
601a628
> int
610a638
> 	return(0);
612a641
> int
621a651
> int
626a657
> 	return(0);
628a660
> int
631a664
> 	return(0);
643c676
< 	register i;
---
> 	register int i;
664a698
> int
692a727
> int
696c731
< 	register i;
---
> 	register int i;
711a747
> int
716c752
< 	register i;
---
> 	register int i;
735a772
> 	return(0);
737a775
> int
740a779
> int cnt;
742c781
< 	register i, j;
---
> 	register int i, j;
751c790
< 			return;
---
> 			return(0);
771a811
> 	return(0);
778a819
> int
787a829
> 	return(0);
792a835
> int
796c839
< 	register i;
---
> 	register int i;
800c843
< 		return;
---
> 		return(0);
803c846
< 		return;
---
> 		return(0);
826a870
> 	return(0);
828a873
> int
833c878
< 	register i;
---
> 	register int i;
850a896
> 	return(0);
852a899
> int
856c903
< 	register i;
---
> 	register int i;
863c910
< 		fbuf.df_nfree = sblock.s_nfree;
---
> 		fbuf.frees.df_nfree = sblock.s_nfree;
865c912
< 			fbuf.df_free[i] = sblock.s_free[i];
---
> 			fbuf.frees.df_free[i] = sblock.s_free[i];
869a917
> 	return(0);
879c927
< 	register i;
---
> 	register int i;
896c944
< 		sblock.s_nfree = fbuf.df_nfree;
---
> 		sblock.s_nfree = fbuf.frees.df_nfree;
898c946
< 			sblock.s_free[i] = fbuf.df_free[i];
---
> 			sblock.s_free[i] = fbuf.frees.df_free[i];
914c962
< 	register i;
---
> 	register int i;
975a1024
> int
987a1037
> int
995a1046
> int
1003a1055
> int
1007c1059
< 	register i, j;
---
> 	register int i, j;
1020a1073
> int
1029a1083
> int
1044a1099
> int
1049a1105
> 	return(0);
1052c1108
< null() {;}
---
> int null() {return(0);}
1053a1110
> int
1056a1114
> 	return(0);
1060a1119
> int
1066a1126
> 	(void)s;
1069a1130
> 	return(0);
1071a1133
> int
1075a1138
> 	(void)b; (void)s;
1076a1140
> 	return(0);
1079a1144
> int
1084c1149
< 	register i;
---
> 	register int i;
1090a1156
> 	return(0);
1096a1163
> int
1107a1175
> 	return(0);
1109a1178
> int
1120a1190
> 	return(0);
1125a1196
> int
1129c1200
< 	register i;
---
> 	register int i;
1138a1210
> 	return(0);
1140a1213
> int
1146a1220
> 	return(0);
```

### cmd/tk.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/tk.c unix-v7-c99/cmd/tk.c || true
```

Expect:

```
36a37,39
> int	init(), sendpt(), kwait(), execom();
> 
> int
41,42c44,45
< 	register i, j;
< 	extern ex();
---
> 	register int i, j;
> 	extern int ex();
67c70
< 	signal(SIGINT, ex);
---
> 	signal(SIGINT, (int)ex);
150a154
> 	return(0);
152a157
> int
168a174
> 	return(0);
170a177
> int
177a185
> 	return(0);
179a188
> int
182c191
< 	register c;
---
> 	register int c;
186c195
< 		return;
---
> 		return(0);
196a206
> 	return(0);
198a209
> int
204,205c215,216
< 		si = signal(SIGINT, SIG_IGN);
< 		sq = signal(SIGQUIT, SIG_IGN);
---
> 		si = (int (*)())signal(SIGINT, (int)SIG_IGN);
> 		sq = (int (*)())signal(SIGQUIT, (int)SIG_IGN);
207,209c218,220
< 		signal(SIGINT, si);
< 		signal(SIGQUIT, sq);
< 		return;
---
> 		signal(SIGINT, (int)si);
> 		signal(SIGQUIT, (int)sq);
> 		return(0);
215a227
> 	return(0);
217a230
> int
218a232
> int a;
220c234
< 	register zz;
---
> 	register int zz;
224c238
< 		return;
---
> 		return(0);
247a262
> 	return(0);
```

### cmd/units.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/units.c unix-v7-c99/cmd/units.c || true
```

Expect:

```
9a10
> int	init(), convr(), units(), pu(), lookup(), equal(), get();
51a53
> int
52a55
> int argc;
55c58
< 	register i;
---
> 	register int i;
72c75
< 	signal(8, fperr);
---
> 	signal(8, (int)fperr);
108a112
> int
113c117
< 	register f, i;
---
> 	register int f, i;
126a131
> 	return(0);
128a134
> int
129a136
> int u, i, f;
146a154
> int
151c159
< 	register c;
---
> 	register int c;
197a206
> int
200a210
> int den, c;
204c214
< 	register i;
---
> 	register int i;
251a262
> int
264a276
> int
301c313
< 		return;
---
> 		return(0);
361c373
< 	register c, i, dp;
---
> 	register int c, i, dp;
414a427
> int
417c430
< 	register c;
---
> 	register int c;
458a472
> int
462c476
< 	signal(8, fperr);
---
> 	signal(8, (int)fperr);
463a478
> 	return(0);
```

### cmd/ptx.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/ptx.c unix-v7-c99/cmd/ptx.c || true
```

Expect:

```
36a37,38
> int diag(), msg(), storeh(), hash(), cmpline(), getsort(), cmpword(),
>     putline(), putout(), onintr();
68a71
> int
77c80
< 	extern onintr();
---
> 	extern int onintr();
82,87c85,90
< 	if(signal(SIGHUP,onintr)==SIG_IGN)
< 		signal(SIGHUP,SIG_IGN);
< 	if(signal(SIGINT,onintr)==SIG_IGN)
< 		signal(SIGINT,SIG_IGN);
< 	signal(SIGPIPE,onintr);
< 	signal(SIGTERM,onintr);
---
> 	if(signal(SIGHUP,(int)onintr)==(int)SIG_IGN)
> 		signal(SIGHUP,(int)SIG_IGN);
> 	if(signal(SIGINT,(int)onintr)==(int)SIG_IGN)
> 		signal(SIGINT,(int)SIG_IGN);
> 	signal(SIGPIPE,(int)onintr);
> 	signal(SIGTERM,(int)onintr);
249a253
> int
255c259
< 	return;
---
> 	return(0);
256a261
> int
262a268
> 	return(0);
269c275
< 	register c;
---
> 	register int c;
301a308
> int
346a354
> 	return(0);
348a357
> int
362a372
> int
376a387
> 	return(0);
378a390
> int
381c393
< 	register c;
---
> 	register int c;
456a469
> 	return(0);
460a474
> int d;
473a488
> int d;
484a500
> int
494a511
> 	return(0);
496a514
> int
502a521
> 	return(0);
504a524
> int
531a552
> int
```

### cmd/spline.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/spline.c unix-v7-c99/cmd/spline.c || true
```

Expect:

```
141c141,142
< rhs(i){
---
> rhs(i)
> int i;{
148a150
> int
215a218,219
> int	getfloat(), numb(), getlim();
> int
220c224
< 		if(!getfloat(&y.val[n])) break; } }
---
> 		if(!getfloat(&y.val[n])) break; } return(0); }
221a226
> int
225c230
< 	register c;
---
> 	register int c;
260a266
> int
267c273
< 	}
---
> 	return(0); }
269a276
> int
270a278
> 	int argc;
319a328
> int
```

### cmd/vpr.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/vpr.c unix-v7-c99/cmd/vpr.c || true
```

Expect:

```
26a27
> int	send(), getline(), putline(), banner();
27a29
> int
28a31
> int argc;
71a75
> int
74c78
< 	register nskipped;
---
> 	register int nskipped;
96a101
> int
99c104
< 	register col, maxcol, c;
---
> 	register int col, maxcol, c;
174a180
> int
175a182
> int ff;
178,179c185,186
< 	register c;
< 	extern errno;
---
> 	register int c;
> 	extern int errno;
188c195
< 		ioctl(fileno(out), SETSTATE, pltmode);
---
> 		ioctl(fileno(out), SETSTATE, (char *)pltmode);
192c199
< 		ioctl(fileno(out), SETSTATE, prtmode);
---
> 		ioctl(fileno(out), SETSTATE, (char *)prtmode);
202a210
> 	return(0);
204a213
> int
232a242
> 	return(0);
```

### cmd/graph.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/graph.c unix-v7-c99/cmd/graph.c || true
```

Evidence summary:

```
43a44,48
> int	init(), setopt(), readin(), transpose(), scale(), axes(), title(),
> 	plot(), erase(), space(), move(), closevt(), numb(), limread(),
> 	badarg(), getfloat(), getstring(), copystring(), getlim(), setlim(),
> 	setmark(), submark(), conv(), symbol(), point(), label(), cont(),
> 	line(), linemod(), axlab(), putsi(), scanf();
65a71,131
> [port-local math helpers: fabs, floor, ceil, log10]
> int
66a133
> int argc;
91a159
> int
96a165
> 	return(0);
98a168
> int
99a170
> int argc;
102c173
< 	char *p1, *p2;
---
> 	char *p0, *p1, *p2;
108a180
> 		p0 = argv[0];
193c265,271
< 			badarg();
---
> 			if(p0[0] == '-')
> 				badarg();
> 			if(freopen(argv[0],"r",stdin)==NULL) {
> 				perror(argv[0]);
> 				exit(1);
> 			}
> 			break;
195a274
> 	return(0);
197a277
> int
209c289
< 		return;
---
> 		return(0);
212c292
< 		return;
---
> 		return(0);
215c295
< 		return;
---
> 		return(0);
216a297
> 	return(0);
218a300
> int
237a320
> int
240c323
< 	register t;
---
> 	register int t;
253c336
< 			return;
---
> 			return(0);
259c342
< 				return;
---
> 				return(0);
261c344
< 			return;
---
> 			return(0);
268c351
< 			return;
---
> 			return(0);
271a355
> int
274c358
< 	register i;
---
> 	register int i;
278c362
< 		return;
---
> 		return(0);
282a367
> 	return(0);
284a370
> int
285a372
> int k;
288c375
< 	register i;
---
> 	register int i;
317a405
> int
322c410
< 	register i;
---
> 	register int i;
331a420
> 	return(0);
337a427
> int
353c443
< 		return;
---
> 		return(0);
392c482
< 			return;
---
> 			return(0);
403a494
> 	return(0);
407a499
> int lbf,ubf;
481a574
> int
494a588
> 	return(0);
496a591
> int
499c594
< 	register i;
---
> 	register int i;
503c598
< 		return;
---
> 		return(0);
527a623
> 	return(0);
529a626
> int
559a657
> int
567a666
> 	return(0);
569a669
> int
594a695
> 	return(0);
596a698
> int
609a712
> int
613c716
< 	register i;
---
> 	register int i;
618a722
> int
621c725
< 	register i;
---
> 	register int i;
648a753
> int
649a755
> int ix,iy,k;
664a771
> int
676a784
> 	return(0);
678a787
> int
686a796
> 	return(0);
688a799
> int
692a804,907
> 	return(0);
> [port-local plot emitters: putsi, space, erase, move, cont, line, point,
> label, linemod, closevt write plot(5)-style bytes directly to stdout]
```

Graph option/file behavior evidence:

- `graph -z` must follow V7 unknown-option behavior and call `badarg()`; the
  port-local file fallback must not strip `-` and try to open `z`.
- `graph datafile` is the only file operand fallback. Bare non-option operands
  are reopened on `stdin` with `freopen()` so file input remains available in
  addition to ordinary stdin input.

### cmd/backgammon.c

Local test:

```
diff unix-v7-c99/v7/usr/src/games/backgammon.c unix-v7-c99/cmd/backgammon.c || true
```

Expect:

```
15c15,19
< int red[]     {0,2,0,0,0,0,0,0,0,0,0,0,5,
---
> int	getstr(), play(), nextmove(), prtmov(), update(), piececount(),
> 	roll(), movegen(), moverecord(), strategy(), eval(),
> 	instructions(), getprob(), prtbrd(), numline(), colorline(),
> 	bg_srand(), bg_rand(), _look(), _store();
> int red[]     = {0,2,0,0,0,0,0,0,0,0,0,0,5,
18c22
< int white[]   {0,2,0,0,0,0,0,0,0,0,0,0,5,
---
> int white[]   = {0,2,0,0,0,0,0,0,0,0,0,0,5,
21c25
< int probability[]{0,11,12,13,14,15,16,
---
> int probability[]={0,11,12,13,14,15,16,
27a32
> int
33c38
< 	srand();
---
> 	bg_srand();
57c62
< 	    exit();
---
> 	    exit(0);
94c99
< 	    exit();
---
> 	    exit(0);
98a104
> int
103a110
> 	return(0);
105a113
> int
148a157
> int
169a179
> int
179a190
> 	return(0);
180a192
> int
194a207
> 	return(0);
195a209
> int
202c216
< 	sum=+player[startrow++];
---
> 	sum+=player[startrow++];
220a235
> int
224,225c239,241
< 	die1=(rand()>>8)%6+1;
< 	die2=(rand()>>8)%6+1;
---
> 	die1=(bg_rand()>>8)%6+1;
> 	die2=(bg_rand()>>8)%6+1;
> 	return(0);
227a244
> int
313a331
> 	return(0);
314a333
> int
353a373
> 	return(0);
356a377
> int
391c412
< 	return(goodmoves[(rand()>>4)%n]);
---
> 	return(goodmoves[(bg_rand()>>4)%n]);
393a415
> int
441c463
< 		sum=+ *p++ * n;	/*remove pieces, but just barely*/
---
> 		sum+= *p++ * n;	/*remove pieces, but just barely*/
449c471
< 	    for(p=newtry;p<q;)sum=- *p++;  /*bad to be on 1st three points*/
---
> 	    for(p=newtry;p<q;)sum-= *p++;  /*bad to be on 1st three points*/
453c475
< 	    *prob=+ n*getprob(newtry,newother,6*n-5,6*n);
---
> 	    *prob+= n*getprob(newtry,newother,6*n-5,6*n);
455a478
> int
482a506
> 	return(0);
484a509
> int
498c523
< 		    if(playee[n]!=0)sum=+probability[k];
---
> 		    if(playee[n]!=0)sum+=probability[k];
503a529
> int
540a567
> 	return(0);
541a569
> int
549a578
> 	return(0);
550a580
> int
562a593
> 	return(0);
565c596
< int rrno 0;
---
> int rrno = 0;
567c598,599
< srand(){
---
> int
> bg_srand(){
569a602
> 	return(0);
572,574c605,608
< rand(){
< 	rrno =* 0106273;
< 	rrno =+ 020202;
---
> int
> bg_rand(){
> 	rrno *= 0106273;
> 	rrno += 020202;
577a612
> int
582c617,618
< _store( p, numb ) int *p; {
---
> int
> _store( p, numb ) int *p; int numb; {
583a620
> 	return(0);
```

### cmd/fish.c

Local test:

```
diff unix-v7-c99/v7/usr/src/games/fish.c unix-v7-c99/cmd/fish.c || true
```

Expect:

```
14a15,18
> int	shuffle(), choose(), draw(), error(), empty(), mark(), deal(),
> 	stats(), phand(), instruct(), game(), move(), madebook(),
> 	score(), guess(), start(), hedrew(), heguessed(), myguess();
> 
24a29
> int
30c35
< 	register i;
---
> 	register int i;
38a44
> 	return(0);
41c47,48
< choose( a, n ) char a[]; {
---
> int
> choose( a, n ) char a[]; int n; {
44c51
< 	register j, t;
---
> 	register int j, t;
53a61
> int
58a67
> int
62a72
> 	return(0);
64a75
> int
66c77
< 	register i;
---
> 	register int i;
74c85,86
< mark( cd, hand ) HAND hand; {
---
> int
> mark( cd, hand ) int cd; HAND hand; {
84c96,97
< deal( hand, n ) HAND hand; {
---
> int
> deal( hand, n ) HAND hand; int n; {
87a101
> 	return(0);
90c104
< char *cname[] {
---
> char *cname[] = {
106a121
> int
108c123
< 	register i, ct, b;
---
> 	register int i, ct, b;
127a143
> 	return(0);
129a146
> int
131c148
< 	register i, j;
---
> 	register int i, j;
141c158
< 			register k;
---
> 			register int k;
154a172
> 	return(0);
157c175,176
< main( argc, argv ) char * argv[]; { 
---
> int
> main( argc, argv ) int argc; char * argv[]; {
159c178
< 	register c;
---
> 	register int c;
175a195
> 	return(0);
180c200
< char *inst[] {
---
> char *inst[] = {
207a228
> int
215a237
> 	return(0);
217a240
> int
229c252
< 		register g;
---
> 		register int g;
256c279,280
< move( hs, ht, g, v ) HAND hs, ht; {
---
> int
> move( hs, ht, g, v ) HAND hs, ht; int g, v; {
259c283
< 	register d;
---
> 	register int d;
315c339,340
< madebook( x ){
---
> int
> madebook( x ) int x; {
316a342
> 	return(0);
318a345
> int
320c347
< 	register my, your, i;
---
> 	register int my, your, i;
345a373
> 	return(0);
349a378
> int
352c381
< 	register g, go;
---
> 	register int g, go;
431a461
> int
432a463
> 	(void)h;
433a465
> 	return(0);
436c468,469
< hedrew( d ){
---
> int
> hedrew( d ) int d; {
437a471
> 	return(0);
440c474,475
< heguessed( d ){
---
> int
> heguessed( d ) int d; {
441a477
> 	return(0);
443a480
> int
446c483
< 	register i, lg, t;
---
> 	register int i, lg, t;
```

### cmd/quiz.c

Local test:

```
diff unix-v7-c99/v7/usr/src/games/quiz.c unix-v7-c99/cmd/quiz.c || true
```

Expect:

```
9a10,14
> int	readline(), cmp(), disj(), string(), eat(), fold(),
> 	publish(), pub1(), segment(), perm(), find(),
> 	readindex(), talloc(), query(), next(), done(),
> 	instruct(), badinfo(), dunno();
> 
27a33
> int
31c37
< 	register c;
---
> 	register int c;
59a66
> int
71a79
> int
72a81
> int s;
110a120
> int
111a122
> int s;
154a166
> int
155a168
> int s;
170a184
> int
178a193
> int
183a199
> 	return(0);
185a202
> int
186a204
> int s;
196c214
< 			return;
---
> 			return(0);
211a230
> int
243a263
> int
244a265
> int m, n;
264a286
> int
265a288
> int m;
276a300
> int
287a312
> 	return(0);
289a315
> int
294a321
> 	return(0);
296a324
> int
297a326
> int argc;
300c329
< 	register j;
---
> 	register int j;
306c335
< 	extern done();
---
> 	extern int done();
315c344
< 			if(argc>2) 
---
> 			if(argc>2)
335c364
< 	signal(SIGINT, done);
---
> 	signal(SIGINT, (int)done);
384a414
> int
403a434
> int
418a450
> int
425a458
> 	return(0);
426a460
> int
462a497
> 	return(0);
464a500
> int
466a503
> 	return(0);
468a506
> int
472a511
> 	return(0);
```

### cmd/wump.c

Local test:

```
diff unix-v7-c99/v7/usr/src/games/wump.c unix-v7-c99/cmd/wump.c || true
```

Expect:

```
0a1
> #include <stdio.h>
12a14,15
> int	tunnel(), rline(), rnum(), rin(), near(), icomp();
> 
19c22
< char	*intro[]
---
> char	*intro[] =
94a98
> int
97c101
< 	register i, j;
---
> 	register int i, j;
159c163
< 			p->flag =| PIT;
---
> 			p->flag |= PIT;
166c170
< 			p->flag =| BAT;
---
> 			p->flag |= BAT;
172c176
< 	room[i].flag =| WUMP;
---
> 	room[i].flag |= WUMP;
270c274
< 	p->flag =& ~WUMP;
---
> 	p->flag &= ~WUMP;
274c278
< 	room[wloc].flag =| WUMP;
---
> 	room[wloc].flag |= WUMP;
284a289
> 	return(0);
286a292
> int
287a294
> int i;
290c297
< 	register n, j;
---
> 	register int n, j;
308a316
> int
317c325
< 			exit();
---
> 			exit(0);
323a332
> int
324a334
> int n;
326c336
< 	static first[2];
---
> 	static int first[2];
329c339
< 		time(first);
---
> 		time((long *)first);
334a345
> int
337c348
< 	register n, c;
---
> 	register int n, c;
345c356
< 					exit();
---
> 					exit(0);
355a367
> int
357a370
> int ahaz;
360c373
< 	register haz, i;
---
> 	register int haz, i;
369a383
> int
```

### cmd/dc/dc.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/dc/dc.c unix-v7-c99/cmd/dc/dc.c || true
```

Expect:

```
3a4,10
> int init(), commnds(), readc(), unreadc(), pushp(), sdump(), chsign(),
>     subt(), eqk(), binop(), dscale(), release(), log2(), print(),
>     load(), seekc(), salterwd(), putwd(), command(), cond(),
>     more(), garbage(), ospace(), redef(), tenot(), oneot(), bigot(),
>     hexot(), onintr();
> 
> int
9a17
> 	return(0);
10a19
> int
62c71
< 			sunputc(p);
---
> 			(void)sunputc(p);
395c404
< 				for(n = 0;n < PTRSZ-1;n++)sputc(q,0);
---
> 				for(n = 0;n < (int)PTRSZ-1;n++)sputc(q,0);
590c599
< 		errorrt("divide by 0\n");
---
> 		{printf("divide by 0\n"); return((struct blk *)1); }
696a706
> int
728a739
> int n;
860a872
> int
867,868c879,880
< 	if (signal(SIGINT, SIG_IGN) != SIG_IGN)
< 		signal(SIGINT,onintr);
---
> 	if (signal(SIGINT, (int)SIG_IGN) != (int)SIG_IGN)
> 		signal(SIGINT,(int)onintr);
918c930
< 	return;
---
> 	return(0);
919a932
> int
922c935
< 	signal(SIGINT,onintr);
---
> 	signal(SIGINT,(int)onintr);
928a942
> 	return(0);
929a944
> int
935c950
< 		return;
---
> 		return(0);
939c954
< 	return;
---
> 	return(0);
1077a1093
> int
1110c1126
< 	return;
---
> 	return(0);
1111a1128
> int
1132a1150
> 	return(0);
1133a1152
> int
1142c1161
< 	return;
---
> 	return(0);
1143a1163
> int
1164c1184
< 	return;
---
> 	return(0);
1165a1186
> int
1181c1202
< 			return;
---
> 			return(0);
1188c1209
< 		return;
---
> 		return(0);
1192c1213
< 	sunputc(p);
---
> 	(void)sunputc(p);
1200c1221
< 		return;
---
> 		return(0);
1204c1225
< 		return;
---
> 		return(0);
1208c1229
< 		return;
---
> 		return(0);
1227c1248
< 		return;
---
> 		return(0);
1243c1264
< 	return;
---
> 	return(0);
1248a1270
> int sc;
1277a1300
> int
1279a1303
> int sc;
1295c1319
< 		return;
---
> 		return(0);
1325c1349
< 	return;
---
> 	return(0);
1326a1351
> int
1328a1354
> int sc;
1344c1370
< 	return;
---
> 	return(0);
1345a1372
> int
1347a1375
> int flg;
1349a1378
> 	(void)flg;
1354c1383
< 		return;
---
> 		return(0);
1360c1389
< 		return;
---
> 		return(0);
1363c1392
< 	return;
---
> 	return(0);
1364a1394
> int
1366a1397
> int flg;
1409c1440
< 			sunputc(strptr);
---
> 			(void)sunputc(strptr);
1414c1445
< 	return;
---
> 	return(0);
1462a1494
> int
1494a1527
> int n;
1525a1559
> int n;
1540a1575
> int
1551a1587
> int
1555c1591
< 	register (*savint)(),pid,rpid;
---
> 	register int (*savint)(),pid,rpid;
1574c1610
< 		savint = signal(SIGINT, SIG_IGN);
---
> 		savint = (int (*)())signal(SIGINT, (int)SIG_IGN);
1576c1612
< 		signal(SIGINT,savint);
---
> 		signal(SIGINT,(int)savint);
1580a1617
> int
1589c1626
< 	sunputc(p);
---
> 	(void)sunputc(p);
1614c1651
< 	if((cc<0 && (c == '<' || c == NG)) ||
---
> 	if(((signed char)cc<0 && (c == '<' || c == NG)) ||
1621a1659
> int
1653c1691
< 	return;
---
> 	return(0);
1654a1693
> int
1740a1780
> int
1749a1790
> 	return(0);
1750a1792
> int
1752a1795
> int n;
1769c1812
< 		return;
---
> 		return(0);
1773c1816
< 	return;
---
> 	return(0);
1774a1818
> int
1782c1826
< 	return;
---
> 	return(0);
1783a1828
> int
1804c1849
< 	return;
---
> 	return(0);
1805a1851
> int
1813a1860
> 	return(0);
1814a1862
> int
1822c1870
< 
---
> 	(void)s;
1859a1908
> 	return(0);
1860a1910
> int
1864c1914
< 	register offset;
---
> 	register int offset;
1881a1932
> 	return(0);
1883a1935
> int
1891a1944
> 	return(0);
1905a1959
> int
1914a1969
> 	return(0);
```

### cmd/dc/dc.h

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/dc/dc.h unix-v7-c99/cmd/dc/dc.h || true
```

Expect:

```
112d111
< int	(*signal())();
114d112
< char	*malloc();
116d113
< char	*realloc();
```

### cmd/spell/spell.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/spell/spell.c unix-v7-c99/cmd/spell/spell.c || true
```

Expect:

```
0a1
> #define unix 1
123a125,128
> int suffix(), strip(), putsuf(), putw(), monosyl(), vowel(),
>     ise(), ztos(), dict();
> 
> int
124a130
> int argc;
180a187
> int
182a190
> int lev;
207a216
> int
212a222
> int
214a225
> int lev;
215a227
> 	(void)d;
218a231
> int
220a234
> int lev;
228a243
> int
230a246
> int lev;
231a248
> 	(void)d;
236a254
> int
238a257
> int lev;
239a259
> 	(void)a;
243a264
> int
245a267
> int lev;
246a269
> 	(void)a;
250a274
> int
252a277
> int lev;
259a285
> int
261a288
> int lev;
268a296
> int
270a299
> int lev;
275a305
> int
277a308
> int lev;
285a317
> int
287a320
> int lev;
303a337
> int
305a340
> int lev;
311a347
> int
313a350
> int lev;
325a363
> int
327a366
> int lev;
362a402
> int
364a405
> int lev;
401a443
> int
403a446
> int lev;
428a472
> int
430a475
> int lev;
432c477
< 	register i, j;
---
> 	register int i, j;
460a506
> int
485a532
> int
486a534
> int c;
500a549
> int
508a558
> 	return(0);
509a560
> int
515a567
> 	return(0);
517a570
> int
524c577
< 	register i;
---
> 	register int i;
527c580
< 	for(i=0; i<NP; i++) {
---
> 	for(i=0; i<(int)NP; i++) {
```

### cmd/spell/spell.h

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/spell/spell.h unix-v7-c99/cmd/spell/spell.h || true
```

Expect:

```
45c45,46
< prime(argc, argv) register char **argv;
---
> int
> prime(argc, argv) int argc; register char **argv;
63c64
< 	for (i=0; i<NP; i++) {
---
> 	for (i=0; i<(int)NP; i++) {
```

### cmd/spell/spellin.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/spell/spellin.c unix-v7-c99/cmd/spell/spellin.c || true
```

Expect:

```
0a1
> #define unix 1
7a9
> int
8a11
> int argc;
11c14
< 	register i, j;
---
> 	register int i, j;
23c26
< 		for (i=0; i<NP; i++) {
---
> 		for (i=0; i<(int)NP; i++) {
```

### cmd/spell/spellout.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/spell/spellout.c unix-v7-c99/cmd/spell/spellout.c || true
```

Expect:

```
0a1
> #define unix 1
2a4
> int
3a6
> int argc;
6c9
< 	register i, j;
---
> 	register int i, j;
30c33
< 		for (i=0; i<NP; i++) {
---
> 		for (i=0; i<(int)NP; i++) {
```

### cmd/plot/chrtab.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/plot/chrtab.c unix-v7-c99/cmd/plot/chrtab.c || true
```

Expect:

```

```

### cmd/tar/tar.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/tar/tar.c unix-v7-c99/cmd/tar/tar.c || true
```

Expect:

```
7,8c7,8
< char	*sprintf();
< char	*strcat();
---
> char	*sprintf(char *buf, char *fmt, ...);
> char	*strcat(char *a, char *b);
9a10,15
> int	usage(), done(), dorep(), doxtract(), dotable(), getdir(),
> 	passtape(), endtape(), getwdir(), putfile(), putempty(),
> 	flushtape(), readtape(), writetape(), backtape(), longt(),
> 	pmode(), select(), checkdir(), onintr(), onquit(), onhup(),
> 	onterm(), tomodes(), checksum(), checkw(), response(),
> 	checkupdate(), prefix(), cmp(), copy();
54a61
> int
140,145c147,152
< 		if (signal(SIGINT, SIG_IGN) != SIG_IGN)
< 			signal(SIGINT, onintr);
< 		if (signal(SIGHUP, SIG_IGN) != SIG_IGN)
< 			signal(SIGHUP, onhup);
< 		if (signal(SIGQUIT, SIG_IGN) != SIG_IGN)
< 			signal(SIGQUIT, onquit);
---
> 		if (signal(SIGINT, (int)SIG_IGN) != (int)SIG_IGN)
> 			signal(SIGINT, (int)onintr);
> 		if (signal(SIGHUP, (int)SIG_IGN) != (int)SIG_IGN)
> 			signal(SIGHUP, (int)onhup);
> 		if (signal(SIGQUIT, (int)SIG_IGN) != (int)SIG_IGN)
> 			signal(SIGQUIT, (int)onquit);
194a202
> int
198a207
> 	return(0);
200a210
> int
253a264
> 	return(0);
255a267
> int
265a278
> int
273c286
< 		return;
---
> 		return(0);
289a303
> 	return(0);
291a306
> int
298c313
< 		return;
---
> 		return(0);
304a320
> 	return(0);
306a323
> int
321c338
< 		return;
---
> 		return(0);
328c345
< 		return;
---
> 		return(0);
332c349
< 		return;
---
> 		return(0);
362c379
< 		return;
---
> 		return(0);
366c383
< 		return;
---
> 		return(0);
376c393
< 		return;
---
> 		return(0);
400c417
< 			return;
---
> 			return(0);
437a455
> 	return(0);
441a460
> int
515a535
> 	return(0);
517a538
> int
531a553
> 	return(0);
533a556
> int
541a565
> 	return(0);
543a568
> int
554a580
> 	return(0);
580a607
> int
587a615
> 	return(0);
589a618
> int
600a630
> 	return(0);
602a633
> int
623a655
> 	return(0);
625a658
> int
628c661
< 	signal(SIGINT, SIG_IGN);
---
> 	signal(SIGINT, (int)SIG_IGN);
629a663
> 	return(0);
631a666
> int
634c669
< 	signal(SIGQUIT, SIG_IGN);
---
> 	signal(SIGQUIT, (int)SIG_IGN);
635a671
> 	return(0);
637a674
> int
640c677
< 	signal(SIGHUP, SIG_IGN);
---
> 	signal(SIGHUP, (int)SIG_IGN);
641a679
> 	return(0);
643a682
> int
646c685
< 	signal(SIGTERM, SIG_IGN);
---
> 	signal(SIGTERM, (int)SIG_IGN);
647a687
> 	return(0);
649a690
> int
661a703
> 	return(0);
663a706
> int
666c709
< 	register i;
---
> 	register int i;
676a720
> int
677a722
> int c;
692a738
> int
703a750
> int
724a772
> int
725a774
> int n;
728a778
> 	return(0);
730a781
> int
741a793
> int
765a818
> 	return(0);
774c827
< 	register i;
---
> 	register int i;
787a841
> int n;
789c843
< 	register i, j;
---
> 	register int i, j;
829a884
> int
831a887
> int n;
833c889
< 	register i;
---
> 	register int i;
845a902
> int
856c913
< 		if ((i = read(mt, tbuf, TBLOCK*j)) < 0) {
---
> 		if ((i = read(mt, (char *)tbuf, TBLOCK*j)) < 0) {
878c935
< 	copy(buffer, &tbuf[recno++]);
---
> 	copy(buffer, (char *)&tbuf[recno++]);
881a939
> int
889c947
< 		if (write(mt, tbuf, TBLOCK*nblock) < 0) {
---
> 		if (write(mt, (char *)tbuf, TBLOCK*nblock) < 0) {
895c953
< 	copy(&tbuf[recno++], buffer);
---
> 	copy((char *)&tbuf[recno++], buffer);
897c955
< 		if (write(mt, tbuf, TBLOCK*nblock) < 0) {
---
> 		if (write(mt, (char *)tbuf, TBLOCK*nblock) < 0) {
905a964
> int
911c970
< 		if (read(mt, tbuf, TBLOCK*nblock) < 0) {
---
> 		if (read(mt, (char *)tbuf, TBLOCK*nblock) < 0) {
916a976
> 	return(0);
918a979
> int
921c982,983
< 	write(mt, tbuf, TBLOCK*nblock);
---
> 	write(mt, (char *)tbuf, TBLOCK*nblock);
> 	return(0);
923a986
> int
927c990
< 	register i;
---
> 	register int i;
932a996
> 	return(0);
```

### cmd/awk/awk.def

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/awk/awk.def unix-v7-c99/cmd/awk/awk.def || true
```

Expect:

```
2c2
< #define yfree free
---
> #define yfree(p) free((char *)(p))
```

### cmd/awk/lib.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/awk/lib.c unix-v7-c99/cmd/awk/lib.c || true
```

Expect:

```
4a5
> int error(), fldbld(), setclvar(), member(), isnumber();
30a32
> int
36c38
< 	register c, sep;
---
> 	register int c, sep;
86a89
> int
98a102
> 	return(0);
100a105
> int
158a164
> 	return(0);
160a167
> int
167c174
< 		return;
---
> 		return(0);
181a189
> 	return(0);
184a193
> int n;
192a202
> int
195a206
> 	return(0);
198c209,213
< error(f, s, a1, a2, a3, a4, a5, a6, a7) {
---
> int
> error(f, s, a1, a2, a3, a4, a5, a6, a7)
> int f, a1, a2, a3, a4, a5, a6, a7;
> char *s;
> {
205a221
> 	return(0);
207a224
> int
208a226
> 	(void)s;
209a228
> 	return(0);
213a233
> int
217c237
< 	register d1, d2;
---
> 	register int d1, d2;
```

### cmd/awk/parse.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/awk/parse.c unix-v7-c99/cmd/awk/parse.c || true
```

Expect:

```
3a4
> int error();
4a6
> int n;
17a20
> int a;
24a28
> int a;
32a37
> int a;
41a47
> int a;
51a58
> int a;
62a70
> int a;
68a77
> int a;
74a84
> int a;
80a91
> int a;
86a98
> int a;
92a105
> int a;
98a112
> int a;
104a119
> int b;
111a127
> int a;
```

### cmd/awk/proc.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/awk/proc.c unix-v7-c99/cmd/awk/proc.c || true
```

Expect:

```
0a1
> #include "stdio.h"
2a4
> char *tokname();
7c9
< } proc[] {
---
> } proc[] = {
60a63
> int
81a85
> 	return(0);
```

### cmd/awk/run.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/awk/run.c unix-v7-c99/cmd/awk/run.c || true
```

Expect:

```
4a5
> #undef NULL
5a7
> int error(), fldbld(), tempfree(), redirprint(), getrec(), match(), freesymtab();
24a27
> int
35a39
> 	(void)printname;
62a67
> int n;
64a70
> 	(void)n;
94a101
> int n;
97a105
> 	(void)n;
110a119
> 	(void)i;
126a136
> int n;
143a154
> int n;
174a186
> int n;
207a220
> int
210c223
< 	if (!istemp(a)) return;
---
> 	if (!istemp(a)) return(0);
212a226
> 	return(0);
232a247
> int n;
236a252
> 	(void)n;
247a264
> int nnn;
251a269
> 	(void)nnn;
286a305
> int nnn;
289a309
> 	(void)nnn;
381a402
> int n;
385a407
> 	(void)n;
397a420
> int n;
440a464
> int n;
461a486
> int n;
504a530
> int q;
508a535
> 	(void)q;
526a554
> int n;
528a557
> 	(void)n;
541a571
> int n;
562a593
> int n;
564a596
> 	(void)n;
576a609
> int nnn;
583a617
> 	(void)nnn;
629a664
> int n;
631a667
> 	(void)n;
645a682
> int n;
647a685
> 	(void)n;
664a703
> int n;
666a706
> 	(void)n;
687a728
> int n;
691a733
> 	(void)n;
712a755
> 	return(true);
715a759
> int n;
717a762
> 	(void)a;
740a786
> int n;
744a791
> 	(void)n;
766a814
> int n;
770a819
> 	(void)n;
792c841
< obj nullproc() {}
---
> obj nullproc() { obj x = {0,0,0}; return(x); }
805c854,855
< redirprint(s, a, b) char *s; node *b;
---
> int
> redirprint(s, a, b) char *s; int a; node *b;
831a882
> 	return(0);
```

### cmd/awk/token.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/awk/token.c unix-v7-c99/cmd/awk/token.c || true
```

Expect:

```
0a1
> #include "stdio.h"
82a84
> int
83a86
> int n;
89c92
< 	return;
---
> 	return(0);
92a96
> int n;
```

### cmd/awk/tran.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/awk/tran.c unix-v7-c99/cmd/awk/tran.c || true
```

Expect:

```
18a19
> int error(), recbld(), checkval(), hash(), isnumber();
19a21
> int
34a37
> 	return(0);
42c45
< 	cp = (char *) malloc(MAXSYM * sizeof(cell *));
---
> 	cp = (cell **) malloc(MAXSYM * sizeof(cell *));
49a53
> int
57c61
< 		return;
---
> 		return(0);
63c67
< 			free(cp);
---
> 			free((char *)cp);
66a71
> 	return(0);
75c80
< 	register h;
---
> 	register int h;
99a105
> int
204a211
> int
212a220
> 	return(0);
226a235
> int
230a240
> 	return(0);
```

### include/dumprestor.h

Local test:

```
diff unix-v7-c99/v7/usr/include/dumprestor.h unix-v7-c99/include/dumprestor.h || true
```

Expect:

```

```

### cmd/awk/b.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/awk/b.c unix-v7-c99/cmd/awk/b.c || true
```

Expect:

```
3a4
> int error(), overflo(), penter(), follow(), first(), notin(), cfoll(), freetr();
59a61
> int
82a85
> 	return(0);
84a88
> int
106a111
> 	return(0);
111c116
< 	register i, c;
---
> 	register int i, c;
138a144
> int
141a148
> 	return(0);
143a151
> int
147c155
< 	register i;
---
> 	register int i;
173a182
> 	return(0);
175a185
> int
179c189
< 	register b;
---
> 	register int b;
209a220
> int
216c227
< 		return;
---
> 		return(0);
222c233
< 				return;
---
> 				return(0);
226c237
< 				return;
---
> 				return(0);
231c242
< 						return;
---
> 						return(0);
236c247
< 				return;
---
> 				return(0);
241c252
< 				return;
---
> 				return(0);
242a254
> 	return(0);
244a257
> int
253a267
> int
255a270
> int n;
257c272
< 	register i, j;
---
> 	register int i, j;
272c287
< int *add(n) {		/* remember setvec */
---
> int *add(n) int n; {		/* remember setvec */
274c289
< 	register i;
---
> 	register int i;
290c305
< 	register i, k;
---
> 	register int i, k;
506a522
> int
511c527
< 	register count;
---
> 	register int count;
```

### cmd/awk/main.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/awk/main.c unix-v7-c99/cmd/awk/main.c || true
```

Expect:

```
3a4
> int logit(), syminit(), run(), msgfiles(), error(), yyparse();
10c11
< extern	errorflag;	/* non-zero if any syntax errors; set by yyerror */
---
> extern int	errorflag;	/* non-zero if any syntax errors; set by yyerror */
14a16
> int
71c73
< 		write(ansfd, &errorflag, sizeof(errorflag));
---
> 		write(ansfd, (char *)&errorflag, sizeof(errorflag));
77c79,80
< logit(n, s) char *s[];
---
> int
> logit(n, s) int n; char *s[];
82,84c85,87
< 		return;
< 	time(tvec);
< 	fprintf(f, "%-8s %s", getlogin(), ctime(tvec));
---
> 		return(0);
> 	time((long *)tvec);
> 	fprintf(f, "%-8s %s", getlogin(), ctime((long *)tvec));
90c93
< 		return;
---
> 		return(0);
94c97
< 		return;
---
> 		return(0);
99a103
> 	return(0);
101a106
> int
106a112
> int
134c140
< 	xargv=s=svargv=malloc(n*sizeof(char *));
---
> 	xargv=s=svargv=(char **)malloc(n*sizeof(char *));
139a146
> 	return(0);
```

### cmd/tp/tp.h

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/tp/tp.h unix-v7-c99/cmd/tp/tp.h || true
```

Expect:

```

```

### cmd/tp/tp0.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/tp/tp0.c unix-v7-c99/cmd/tp/tp0.c || true
```

Expect:

```

```

### cmd/tp/tp1.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/tp/tp1.c unix-v7-c99/cmd/tp/tp1.c || true
```

Expect:

```
1a2
> #include <stdio.h>
2a4,9
> int	optap(), setcom(), useerr(), check(), done(), encode(),
> 	decode(), cmd(), cmr(), cmt(), cmx(),
> 	clrdir(), clrent(), rddir(), gettape(), wrdir(), getfiles(),
> 	update(), delete(), taboc(), extract(), usage();
> 
> int
3a11
> int argc;
7c15,16
< 	extern cmd(), cmr(),cmx(), cmt();
---
> 	extern int cmd(), cmr(),cmx(), cmt();
> 	(void)argc;
62a72
> 	return(0);
64a75
> int
67c78
< 	extern cmr();
---
> 	extern int cmr();
86a98
> 	return(0);
88a101
> int
92c105
< 	extern cmr();
---
> 	extern int cmr();
95a109
> 	return(0);
97a112
> int
101a117
> 	return(0);
104c120
< /*/* COMMANDS */
---
> /* COMMANDS */
105a122
> int
108c125
< 	extern delete();
---
> 	extern int delete();
115a133
> 	return(0);
117a136
> int
124a144
> 	return(0);
126a147
> int
129c150
< 	extern taboc();
---
> 	extern int taboc();
136a158
> 	return(0);
138a161
> int
141c164
< 	extern extract();
---
> 	extern int extract();
146a170
> 	return(0);
148a173
> int
152a178
> 	return(0);
154a181
> int
158a186
> 	return(0);
160a189
> int
168c197
< 	register n;
---
> 	register int n;
185a215
> 	return(0);
187a218
> int
194a226
> 	return(0);
```

### cmd/tp/tp2.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/tp/tp2.c unix-v7-c99/cmd/tp/tp2.c || true
```

Expect:

```
6a7,10
> int	rseek(), wseek(), tread(), twrite(), seekerr(), swabdir(),
> 	encode(), decode(), done(), bitmap(), fserr(), callout(),
> 	expand(), clrent();
> 
9a14
> int
12c17
< 	register j, *p;
---
> 	register int j, *p;
17a23
> 	return(0);
19a26
> int
23c30
< 	register *p, j;
---
> 	register int *p, j;
32c39
< 			return;
---
> 			return(0);
34a42
> 	return(0);
37a46
> int
68c77
< 		for(i=0;i<sizeof(struct tent)/sizeof(short);i++)
---
> 		for(i=0;i<(int)(sizeof(struct tent)/sizeof(short));i++)
100c109
< 			return;
---
> 			return(0);
102a112
> 	return(0);
105a116
> int
130c141
< 		if (count == 0)  return;
---
> 		if (count == 0)  return(0);
149c160
< 				for(i=0;i<sizeof(struct tent)/sizeof(short)-1;i++)
---
> 				for(i=0;i<(int)(sizeof(struct tent)/sizeof(short))-1;i++)
156c167
< 				for(i=0;i<sizeof(struct tent)/sizeof(short);i++)
---
> 				for(i=0;i<(int)(sizeof(struct tent)/sizeof(short));i++)
163a175
> int
166c178
< 	register j, *ptr;
---
> 	register int j, *ptr;
175a188
> 	return(0);
177a191
> int
184a199
> 	return(0);
186a202
> int
187a204
> int blk;
190a208
> 	return(0);
192a211
> int
193a213
> int blk;
195c215
< 	register amt, b;
---
> 	register int amt, b;
204a225
> 	return(0);
206a228
> int
210a233
> 	return(0);
212a236
> int
213a238
> int key;
215c240
< 	register c;
---
> 	register int c;
234a260
> int
244a271
> 	return(0);
247a275
> int
258c286
< 				return;
---
> 				return(0);
276a305
> int
280a310
> 	return(0);
282a313
> int
295c326
< 		if(mode != S_IFREG) return;
---
> 		if(mode != S_IFREG) return(0);
316c347
< 				return;
---
> 				return(0);
318c349
< 		if (verify('r') < 0)	return;
---
> 		if (verify('r') < 0)	return(0);
330c361
< 	if (verify('a') < 0)		return;
---
> 	if (verify('a') < 0)		return(0);
338a370
> 	return(0);
340a373
> int
346a380
> 	return(0);
```

### cmd/tp/tp_defs.h

Local test:

```
diff unix-v7-c99/v7/usr/include/tp_defs.h unix-v7-c99/cmd/tp/tp_defs.h || true
```

Expect:

```

```

### cmd/tp/tp3.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/tp/tp3.c unix-v7-c99/cmd/tp/tp3.c || true
```

Expect:

```
1a2
> #include <stdio.h>
2a4,8
> int	decode(), verify(), clrent(), bitmap(), maperr(), setmap(),
> 	wrdir(), update1(), wseek(), twrite(), phserr(), done(),
> 	rseek(), tread(), usage();
> 
> int
30a37
> 	return(0);
32a40
> int
37a46
> 	return(0);
40a50
> int
44c54
< 	register b, last;
---
> 	register int b, last;
67a78
> 	return(0);
70a82
> int
74c86
< 	register index;
---
> 	register int index;
88c100
< 		if ((d = id) == 0)	return;
---
> 		if ((d = id) == 0)	return(0);
109a122
> int
111c124
< {	printf("%s -- Phase error \n", name);  }
---
> {	printf("%s -- Phase error \n", name); return(0);  }
113a127
> int
117c131
< 	register count;
---
> 	register int count;
127a142
> 	return(0);
129a145
> int
140c156
< 	if ((c += block) >= tapsiz)		maperr();
---
> 	if ((c += block) >= (unsigned)tapsiz)		maperr();
146a163
> 	return(0);
148a166
> int
152a171
> 	return(0);
155a175
> int
158c178
< 	register reg,count;
---
> 	register int reg,count;
160c180
< 	static lused;
---
> 	static int lused;
186a207
> 	return(0);
189a211
> int
193,194c215,216
< 	register  mode;
< 	register *m;
---
> 	register int mode;
> 	register int *m;
196c218
< 	int count, *localtime();
---
> 	int count;
215c237
< 		m = localtime(&dd->d_time);
---
> 		m = (int *)localtime(&dd->d_time);
218a241
> 	return(0);
221a245
> int
225c249
< 	register count, id;
---
> 	register int count, id;
227,228c251,252
< 	if (d->d_size==0)	return;
< 	if (verify('x') < 0)			return;
---
> 	if (d->d_size==0)	return(0);
> 	if (verify('x') < 0)			return(0);
243c267
< 			return;
---
> 			return(0);
247a272
> 	return(0);
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
13c13,16
< #include <a.out.h>
---
> #include <stdlib.h>
> #include <unistd.h>
> #include <fcntl.h>
> #include <time.h>
15,20c18,32
< #include <sys/param.h>
< #include <sys/ino.h>
< #include <sys/inode.h>
< #include <sys/filsys.h>
< #include <sys/fblk.h>
< #include <sys/dir.h>
---
> #include "../include/sys/param.h"
> #include "../include/sys/ino.h"
> #include "../include/sys/inode.h"
> #include "../include/sys/filsys.h"
> #include "../include/sys/fblk.h"
> #include "../include/sys/dir.h"
> /* Pack longs into pure LE 24-bit; matches arch/armboot.c::addr(). */
> int ltol3(cp, lp, n) char *cp; long *lp; int n; {
> 	int i; long v;
> 	for(i=0; i<n; i++) {
> 		v = lp[i];
> 		*cp++ = v; *cp++ = v >> 8; *cp++ = v >> 16;
> 	}
> 	return(0);
> }
32c44
< 	struct fblk fb;
---
> 	struct fblk;
35,37d46
< #ifndef STANDALONE
< struct exec head;
< #endif
40c49
< 	struct filsys fs;
---
> 	struct filsys;
117c126
< 		printf("isize = %D\n", n*NIPB);
---
> 		printf("isize = %ld\n", n*NIPB);
125c134
< 	 * and read onto block 0
---
> 	 * (skipped: PDP-11 a.out format is not used on this port)
130,148c139,142
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
< 
< f1:
< 	close(f);
---
> 	if(f < 0)
> 		printf("%s: cannot open init\n", string);
> 	else
> 		close(f);
155d148
< f2:
312a306
> 	int m[4] = {m0, m1, m2, m3};
316c310
< 			return((&m0)[i]);
---
> 			return(m[i]);
395c389
< 		printf("write error: %D\n", bno);
---
> 		printf("write error: %ld\n", bno);
```
