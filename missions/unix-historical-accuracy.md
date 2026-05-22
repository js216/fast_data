# Unix v7 -> C99 historical accuracy

### Files NOT diffed

Local test:

```
LC_ALL=C bash -c 'm=missions/unix-historical-accuracy.md; \
cd unix-v7-c99; g="git ls-files -co --exclude-standard"; \
comm -23 <($g|xargs grep -Il "" 2>/dev/null|sort) \
<(grep ^diff ../"$m"|cut -d" " -f3|cut -d/ -f2-|sort)'
```

Expect:

```
.gitignore
LICENSE
Makefile
README
arch/arm.c
arch/arm.h
arch/arm.ld
arch/arm.s
cmd/awk/awk.g.c
cmd/awk/awk.h
cmd/awk/awk.lx.c
cmd/awk/awk_math.c
cmd/awk/proctab.c
conf/arm_qemu/auxfs.proto
conf/arm_qemu/conf.c
conf/arm_qemu/config.mk
conf/arm_qemu/root.proto
dev/msgbuf.c
dev/pl011.c
dev/virtio_blk.c
h/proto.h
h/v7_bridge.h
lib/Makefile
lib/compat.c
lib/crt0.c
lib/doprnt.c
lib/math_helpers.c
lib/memcpy.c
lib/mkdir.c
lib/sys.s
lib/u.ld
sys/Makefile
sys/v7_bridge.c
sys/v7stubs.c
tools/extract-old-ar.py
tools/qemu-shell.py
```

### cmd/chroot.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/sys/chroot.s unix-v7-c99/cmd/chroot.c | sed 's/[[:blank:]]*$//' || true
```

Expect:

```
1c1,3
< / C library -- chroot
---
> /* chroot -- run command with NEWROOT as the root directory.  Calls the
>  * v7 chroot(2) syscall (which requires root) then execs argv[2..]; with
>  * no command, falls back to /bin/sh. */
3c5,8
< / error = chroot(string);
---
> #include <stdio.h>
> extern int chroot(char *path);
> extern int execvp(char *file, char **argv);
> extern int chdir(char *path);
5,22c10,31
< .globl	_chroot
< .globl	cerror
< .chroot = 61.
<
< _chroot:
< 	mov	r5,-(sp)
< 	mov	sp,r5
< 	mov	4(r5),0f
< 	sys	0; 9f
< 	bec	1f
< 	jmp	cerror
< 1:
< 	clr	r0
< 	mov	(sp)+,r5
< 	rts	pc
< .data
< 9:
< 	sys	.chroot; 0:..
---
> int
> main(int argc, char *argv[])
> {
> 	static char *shargv[] = { "sh", 0 };
> 	if (argc < 2) {
> 		fprintf(stderr, "usage: chroot newroot [cmd [args...]]\n");
> 		exit(2);
> 	}
> 	if (chroot(argv[1]) < 0) {
> 		fprintf(stderr, "chroot: %s: cannot chroot\n", argv[1]);
> 		exit(1);
> 	}
> 	(void)chdir("/");
> 	if (argc >= 3) {
> 		execvp(argv[2], &argv[2]);
> 		fprintf(stderr, "chroot: %s: exec failed\n", argv[2]);
> 		exit(127);
> 	}
> 	execvp("/bin/sh", shargv);
> 	fprintf(stderr, "chroot: /bin/sh: exec failed\n");
> 	exit(127);
> }
```

### cmd/link.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/sys/link.s unix-v7-c99/cmd/link.c | sed 's/[[:blank:]]*$//' || true
```

Expect:

```
1c1,4
< / C library -- link
---
> /* link FILE1 FILE2  -- create a hard link FILE2 pointing at FILE1.
>  * POSIX-mandated thin wrapper over the link(2) syscall.  Differs from
>  * ln(1) in that it takes exactly two args and never resolves the
>  * target as a directory. */
3c6,7
< / error = link(old-file, new-file);
---
> #include <stdio.h>
> extern int link(char *, char *);
5,23c9,21
< .globl	_link
< .globl	cerror
< .link = 9.
<
< _link:
< 	mov	r5,-(sp)
< 	mov	sp,r5
< 	mov	4(r5),0f
< 	mov	6(r5),0f+2
< 	sys	0; 9f
< 	bec	1f
< 	jmp	cerror
< 1:
< 	clr	r0
< 	mov	(sp)+,r5
< 	rts	pc
< .data
< 9:
< 	sys	.link; 0:..; ..
---
> int
> main(int argc, char *argv[])
> {
> 	if (argc != 3) {
> 		fprintf(stderr, "usage: link FILE1 FILE2\n");
> 		exit(1);
> 	}
> 	if (link(argv[1], argv[2]) < 0) {
> 		fprintf(stderr, "link: %s -> %s: failed\n", argv[1], argv[2]);
> 		exit(1);
> 	}
> 	exit(0);
> }
```

### cmd/mktemp.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/mktemp.c unix-v7-c99/cmd/mktemp.c | sed 's/[[:blank:]]*$//' || true
```

Expect:

```
1,3c1,16
< char *
< mktemp(as)
< char *as;
---
> /* mktemp -- create a unique temporary file or directory.
>  *   mktemp                  -> /tmp/tmp.XXXXXX
>  *   mktemp TEMPLATE         -> TEMPLATE has trailing XXXXXX replaced
>  *   mktemp -d [TEMPLATE]    -> create directory instead of file
>  * Prints the resulting name.  libc's mktemp() picks the suffix; mkdir()
>  * is a libc helper (v7 lacks the syscall) that runs the mknod+link
>  * dance from cmd/mkdir.c. */
>
> #include <stdio.h>
> extern char *mktemp(char *);
> extern int mkdir(char *path, int mode);
> extern int creat(char *path, int mode);
> extern int close(int fd);
>
> int
> main(int argc, char *argv[])
5,7c18,30
< 	register char *s;
< 	register unsigned pid;
< 	register i;
---
> 	static char buf[256];
> 	char *src;
> 	int i, dflag = 0, start = 1;
> 	int fd;
>
> 	if (start < argc && argv[start][0] == '-' && argv[start][1] == 'd' &&
> 	    argv[start][2] == '\0') {
> 		dflag = 1;
> 		start++;
> 	}
> 	src = (start < argc) ? argv[start] : "/tmp/tmp.XXXXXX";
> 	for (i = 0; src[i] && i < (int)sizeof(buf) - 1; i++) buf[i] = src[i];
> 	buf[i] = '\0';
9,16c32,34
< 	pid = getpid();
< 	s = as;
< 	while (*s++)
< 		;
< 	s--;
< 	while (*--s == 'X') {
< 		*s = (pid%10) + '0';
< 		pid /= 10;
---
> 	if (mktemp(buf) == 0 || buf[0] == '\0') {
> 		fprintf(stderr, "mktemp: cannot generate unique name\n");
> 		exit(1);
18,23c36,46
< 	s++;
< 	i = 'a';
< 	while (access(as, 0) != -1) {
< 		if (i=='z')
< 			return("/");
< 		*s = i++;
---
> 	if (dflag) {
> 		if (mkdir(buf, 0700) < 0) {
> 			fprintf(stderr, "mktemp: %s: cannot mkdir\n", buf);
> 			exit(1);
> 		}
> 	} else {
> 		if ((fd = creat(buf, 0600)) < 0) {
> 			fprintf(stderr, "mktemp: %s: cannot create\n", buf);
> 			exit(1);
> 		}
> 		close(fd);
25c48,49
< 	return(as);
---
> 	puts(buf);
> 	exit(0);
```

### cmd/printf.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/printf.c unix-v7-c99/cmd/printf.c | sed 's/[[:blank:]]*$//' || true
```

Expect:

```
1c1,5
< #include	<stdio.h>
---
> /* printf -- minimal printf(1).  V7 didn't ship one; scripts that
>  * port from later Unixes expect it.  Supports %s %d %i %x %o %c %%
>  * and \n \t \\ \r \0 in both format and string args.  Format string
>  * is reused if more args remain.
>  */
3,4c7,116
< printf(fmt, args)
< char *fmt;
---
> #include <stdio.h>
>
> static int
> hexval(char c)
> {
> 	if (c >= '0' && c <= '9') return c - '0';
> 	if (c >= 'a' && c <= 'f') return c - 'a' + 10;
> 	if (c >= 'A' && c <= 'F') return c - 'A' + 10;
> 	return -1;
> }
>
> static int
> expand(char *out, char *in)
> {
> 	char *p = in, *q = out;
> 	int v, h;
> 	while (*p) {
> 		if (*p == '\\' && p[1]) {
> 			p++;
> 			switch (*p) {
> 			case 'n':  *q++ = '\n'; p++; break;
> 			case 't':  *q++ = '\t'; p++; break;
> 			case 'r':  *q++ = '\r'; p++; break;
> 			case '\\': *q++ = '\\'; p++; break;
> 			case 'a':  *q++ = '\a'; p++; break;
> 			case 'b':  *q++ = '\b'; p++; break;
> 			case 'f':  *q++ = '\f'; p++; break;
> 			case 'v':  *q++ = '\v'; p++; break;
> 			case 'x':
> 				p++;
> 				v = 0;
> 				if ((h = hexval(*p)) >= 0) {
> 					v = h;
> 					p++;
> 					if ((h = hexval(*p)) >= 0) {
> 						v = (v << 4) | h;
> 						p++;
> 					}
> 				} else {
> 					/* bare \x with no hex digit: keep literal */
> 					*q++ = '\\';
> 					*q++ = 'x';
> 					break;
> 				}
> 				*q++ = (char)v;
> 				break;
> 			case '0': case '1': case '2': case '3':
> 			case '4': case '5': case '6': case '7':
> 				v = 0;
> 				/* up to 3 octal digits */
> 				for (int i = 0; i < 3 && *p >= '0' && *p <= '7'; i++)
> 					v = (v << 3) | (*p++ - '0');
> 				*q++ = (char)v;
> 				break;
> 			default:   *q++ = '\\'; *q++ = *p; p++; break;
> 			}
> 		} else {
> 			*q++ = *p++;
> 		}
> 	}
> 	*q = '\0';
> 	return q - out;
> }
>
> static char *
> emit(char *spec, char *arg)
> {
> 	char buf[64];
> 	char *p = spec;
> 	int n;
> 	long iv;
> 	while (*p && *p != '%')
> 		putchar(*p++);
> 	if (!*p)
> 		return p;
> 	/* p points at '%' */
> 	buf[0] = *p++;
> 	n = 1;
> 	while (*p && n < (int)sizeof(buf) - 2 &&
> 	    (*p == '-' || *p == '+' || *p == ' ' || *p == '#' || *p == '0' ||
> 	     (*p >= '0' && *p <= '9') || *p == '.'))
> 		buf[n++] = *p++;
> 	if (!*p)
> 		return p;
> 	buf[n++] = *p;
> 	buf[n] = '\0';
> 	switch (*p++) {
> 	case 's':
> 		printf(buf, arg ? arg : "");
> 		break;
> 	case 'c':
> 		printf(buf, arg ? arg[0] : '\0');
> 		break;
> 	case 'd': case 'i':
> 	case 'o': case 'u': case 'x': case 'X':
> 		iv = arg ? atol(arg) : 0;
> 		printf(buf, (int)iv);
> 		break;
> 	case '%':
> 		putchar('%');
> 		break;
> 	default:
> 		printf("%s", buf);
> 		break;
> 	}
> 	return p;
> }
>
> int
> main(int argc, char *argv[])
6,7c118,154
< 	_doprnt(fmt, &args, stdout);
< 	return(ferror(stdout)? EOF: 0);
---
> 	char fmt[512], arg[256];
> 	char *p;
> 	int ai = 2;
>
> 	if (argc < 2)
> 		exit(1);
> 	if (argc == 2 && argv[1][0] == '\0') {
> 		exit(0);
> 	}
> 	{
> 		int n = expand(fmt, argv[1]);
> 		if (argc == 2) {
> 			if (n > 0) write(1, fmt, n);
> 			exit(0);
> 		}
> 	}
> 	while (ai < argc || (ai == argc && !*fmt /* skip */)) {
> 		p = fmt;
> 		while (*p) {
> 			if (*p == '%' && p[1] == '%') {
> 				putchar('%');
> 				p += 2;
> 			} else if (*p == '%') {
> 				if (ai < argc) {
> 					expand(arg, argv[ai++]);
> 					p = emit(p, arg);
> 				} else {
> 					p = emit(p, "");
> 				}
> 			} else {
> 				putchar(*p++);
> 			}
> 		}
> 		if (ai >= argc)
> 			break;
> 	}
> 	exit(0);
```

### cmd/unlink.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/sys/unlink.s unix-v7-c99/cmd/unlink.c | sed 's/[[:blank:]]*$//' || true
```

Expect:

```
1c1,4
< / C library -- unlink
---
> /* unlink FILE -- remove FILE via the unlink(2) syscall.  POSIX-
>  * mandated thin wrapper.  Unlike rm, doesn't prompt or check perms;
>  * unlink(2) returns failure if FILE doesn't exist or isn't writable
>  * (for the parent directory). */
3c6,7
< / error = unlink(string);
---
> #include <stdio.h>
> extern int unlink(char *);
5,22c9,21
< .globl	_unlink,
< .globl	cerror
< .unlink = 10.
<
< _unlink:
< 	mov	r5,-(sp)
< 	mov	sp,r5
< 	mov	4(r5),0f
< 	sys	0; 9f
< 	bec	1f
< 	jmp	cerror
< 1:
< 	clr	r0
< 	mov	(sp)+,r5
< 	rts	pc
< .data
< 9:
< 	sys	.unlink; 0:..
---
> int
> main(int argc, char *argv[])
> {
> 	if (argc != 2) {
> 		fprintf(stderr, "usage: unlink FILE\n");
> 		exit(1);
> 	}
> 	if (unlink(argv[1]) < 0) {
> 		fprintf(stderr, "unlink: %s: failed\n", argv[1]);
> 		exit(1);
> 	}
> 	exit(0);
> }
```

### cmd/sh/makefile

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/makefile unix-v7-c99/cmd/sh/makefile || true
```

Expect:

```

```

### sys/machdep_arm.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/machdep.c unix-v7-c99/sys/machdep_arm.c || true
```

Expect:

```
2,10d1
< #include "../h/systm.h"
< #include "../h/acct.h"
< #include "../h/dir.h"
< #include "../h/user.h"
< #include "../h/inode.h"
< #include "../h/proc.h"
< #include "../h/seg.h"
< #include "../h/map.h"
< #include "../h/reg.h"
12,195c3,33
< 
< /*
<  * Icode is the octal bootstrap
<  * program executed in user mode
<  * to bring up the system.
<  */
< int	icode[] =
< {
< 	0104413,	/* sys exec; init; initp */
< 	0000014,
< 	0000010,
< 	0000777,	/* br . */
< 	0000014,	/* initp: init; 0 */
< 	0000000,
< 	0062457,	/* init: </etc/init\0> */
< 	0061564,
< 	0064457,
< 	0064556,
< 	0000164,
< };
< int	szicode = sizeof(icode);
< 
< /*
<  * Machine-dependent startup code
<  */
< startup()
< {
< 	register i;
< 
< 	/*
< 	 * zero and free all of core
< 	 */
< 
< 	i = ka6->r[0] + USIZE;
< 	UISD->r[0] = 077406;
< 	for(;;) {
< 		UISA->r[0] = i;
< 		if(fuibyte((caddr_t)0) < 0)
< 			break;
< 		clearseg(i);
< 		maxmem++;
< 		mfree(coremap, 1, i);
< 		i++;
< 	}
< 	if(cputype == 70)
< 	for(i=0; i<62; i+=2) {
< 		UBMAP->r[i] = i<<12;
< 		UBMAP->r[i+1] = 0;
< 	}
< 	printf("mem = %D\n", ctob((long)maxmem));
< 	if(MAXMEM < maxmem)
< 		maxmem = MAXMEM;
< 	mfree(swapmap, nswap, 1);
< 	swplo--;
< 
< 	/*
< 	 * determine clock
< 	 */
< 
< 	UISA->r[7] = ka6->r[1]; /* io segment */
< 	UISD->r[7] = 077406;
< }
< 
< /*
<  * set up a physical address
<  * into users virtual address space.
<  */
< sysphys()
< {
< 	register i, s, d;
< 	register struct a {
< 		int	segno;
< 		int	size;
< 		int	phys;
< 	} *uap;
< 
< 	if(!suser())
< 		return;
< 	uap = (struct a *)u.u_ap;
< 	i = uap->segno;
< 	if(i < 0 || i >= 8)
< 		goto bad;
< 	s = uap->size;
< 	if(s < 0 || s > 128)
< 		goto bad;
< 	d = u.u_uisd[i+8];
< 	if(d != 0 && (d&ABS) == 0)
< 		goto bad;
< 	u.u_uisd[i+8] = 0;
< 	u.u_uisa[i+8] = 0;
< 	if(!u.u_sep) {
< 		u.u_uisd[i] = 0;
< 		u.u_uisa[i] = 0;
< 	}
< 	if(s) {
< 		u.u_uisd[i+8] = ((s-1)<<8) | RW|ABS;
< 		u.u_uisa[i+8] = uap->phys;
< 		if(!u.u_sep) {
< 			u.u_uisa[i] = u.u_uisa[i+8];
< 			u.u_uisd[i] = u.u_uisd[i+8];
< 		}
< 	}
< 	sureg();
< 	return;
< 
< bad:
< 	u.u_error = EINVAL;
< }
< 
< /*
<  * Determine which clock is attached, and start it.
<  * panic: no clock found
<  */
< #define	CLOCK1	((physadr)0177546)
< #define	CLOCK2	((physadr)0172540)
< clkstart()
< {
< 	lks = CLOCK1;
< 	if(fuiword((caddr_t)lks) == -1) {
< 		lks = CLOCK2;
< 		if(fuiword((caddr_t)lks) == -1)
< 			panic("no clock");
< 	}
< 	lks->r[0] = 0115;
< }
< 
< /*
<  * Let a process handle a signal by simulating an interrupt
<  */
< sendsig(p, signo)
< caddr_t p;
< {
< 	register unsigned n;
< 
< 	n = u.u_ar0[R6] - 4;
< 	grow(n);
< 	suword((caddr_t)n+2, u.u_ar0[RPS]);
< 	suword((caddr_t)n, u.u_ar0[R7]);
< 	u.u_ar0[R6] = n;
< 	u.u_ar0[RPS] &= ~TBIT;
< 	u.u_ar0[R7] = (int)p;
< }
< 
< /*
<  * 11/70 routine to allocate the
<  * UNIBUS map and initialize for
<  * a unibus device.
<  * The code here and in
<  * rhstart assumes that an rh on an 11/70
<  * is an rh70 and contains 22 bit addressing.
<  */
< int	maplock;
< 
< mapalloc(bp)
< register struct buf *bp;
< {
< 	register i, a;
< 
< 	if(cputype != 70)
< 		return;
< 	spl6();
< 	while(maplock&B_BUSY) {
< 		maplock |= B_WANTED;
< 		sleep((caddr_t)&maplock, PSWP+1);
< 	}
< 	maplock |= B_BUSY;
< 	spl0();
< 	bp->b_flags |= B_MAP;
< 	a = bp->b_xmem;
< 	for(i=16; i<32; i+=2)
< 		UBMAP->r[i+1] = a;
< 	for(a++; i<48; i+=2)
< 		UBMAP->r[i+1] = a;
< 	bp->b_xmem = 1;
< }
< 
< mapfree(bp)
< struct buf *bp;
< {
< 
< 	bp->b_flags &= ~B_MAP;
< 	if(maplock&B_WANTED)
< 		wakeup((caddr_t)&maplock);
< 	maplock = 0;
---
> #include "../h/systm.h"
> #include "../h/proto.h"
> #include "../arch/arm.h"
> void startup(void)
> {
> 	struct buf *bp;
> 	unsigned char *raw;
> 	unsigned int isize, fsize;
> 	/* Qemu virt's default RAM is 128 MiB at 0x40000000.  Print bytes
> 	 * directly; the V7 banner shape lets userspace scrape "mem =". */
> 	printf("mem = %D\n", (long)(128L * 1024 * 1024));
> 	/* v7's startup() probed core via UISA/fuibyte to compute maxmem,
> 	 * then capped it at MAXMEM.  On this port userspace is identity-
> 	 * mapped into a USERSIZE (1 MiB = 16384 click) window, so estabur()'s
> 	 * `nt+nd+ns+USIZE > maxmem` check passes as long as maxmem covers
> 	 * that window.  Seed it directly. */
> 	maxmem = (int)(USERSIZE >> 6) + USIZE;	/* clicks (64 bytes) */
> 	mmuinit();
> 	virtio_init();
> 	binit();
> 	/* Sentinel: bread the rootfs SUPERB and print isize/fsize.  Decode
> 	 * raw bytes -- the on-disk layout packs s_fsize at offset 2 (no
> 	 * alignment padding) while h/filsys.h's struct aligns it to 4. */
> 	bp = bread((dev_t)rootdev, (daddr_t)SUPERB);
> 	raw = (unsigned char *)bp->b_un.b_addr;
> 	isize = (unsigned int)raw[0] | ((unsigned int)raw[1] << 8);
> 	fsize = (unsigned int)raw[2] | ((unsigned int)raw[3] << 8)
> 	      | ((unsigned int)raw[4] << 16)
> 	      | ((unsigned int)raw[5] << 24);
> 	printf("v7: sb isize=%d fsize=%d\n", (int)isize, (int)fsize);
> 	brelse(bp);
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
14a15,18
> 	int nflg = 0, bflg = 0, sflg = 0;
> 	int lineno = 1;
> 	int blank_run = 0;
> 	int at_line_start = 1;
16c20
< 	register c;
---
> 	register int c;
27a32,40
> 		case 'n':
> 			nflg = 1;
> 			continue;
> 		case 'b':	/* -b: number non-blank lines */
> 			bflg = 1;
> 			continue;
> 		case 's':	/* -s: squeeze blank lines */
> 			sflg = 1;
> 			continue;
42c55
< 		if (fflg || (*++argv)[0]=='-' && (*argv)[1]=='\0')
---
> 		if (fflg || ((*++argv)[0]=='-' && (*argv)[1]=='\0'))
57c70,82
< 		while ((c = getc(fi)) != EOF)
---
> 		while ((c = getc(fi)) != EOF) {
> 			if (sflg) {
> 				if (c == '\n' && at_line_start) {
> 					if (++blank_run > 1) continue;
> 				} else if (c != '\n') {
> 					blank_run = 0;
> 				}
> 			}
> 			if (at_line_start && (nflg || bflg)) {
> 				if (!(bflg && c == '\n')) {
> 					printf("%6d\t", lineno++);
> 				}
> 			}
58a84,85
> 			at_line_start = (c == '\n');
> 		}
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
1c1
< /* wc line and word count */
---
> /* wc line, word, char, and longest-line count */
5,6c5,8
< main(argc, argv)
< char **argv;
---
> void wcp(register char *wd, long charct, long wordct, long linect, long longest);
> 
> int
> main(int argc, char *argv[])
10,11c12,13
< 	long linect, wordct, charct;
< 	long tlinect=0, twordct=0, tcharct=0;
---
> 	long linect, wordct, charct, longest, curline;
> 	long tlinect=0, twordct=0, tcharct=0, tlongest=0;
31a34,35
> 		longest = 0;
> 		curline = 0;
37a42,47
> 			if(c == '\n') {
> 				if (curline > longest) longest = curline;
> 				curline = 0;
> 			} else {
> 				curline++;
> 			}
50a61
> 		if (curline > longest) longest = curline;
52c63
< 		wcp(wd, charct, wordct, linect);
---
> 		wcp(wd, charct, wordct, linect, longest);
60a72
> 		if (longest > tlongest) tlongest = longest;
63c75
< 		wcp(wd, tcharct, twordct, tlinect);
---
> 		wcp(wd, tcharct, twordct, tlinect, tlongest);
69,71c81,82
< wcp(wd, charct, wordct, linect)
< register char *wd;
< long charct; long wordct; long linect;
---
> void
> wcp(register char *wd, long charct, long wordct, long linect, long longest)
83a95,98
> 		break;
> 
> 	case 'L':
> 		printf("%7ld", longest);
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
19c19,23
< 		for(p3=argv[2]; *p3; p3++) 
---
> 		/* p1 points just past the basename's last char; p3 just past
> 		 * the suffix's last char.  Walk both backwards in lockstep;
> 		 * if every suffix char matches AND we reach the start of the
> 		 * suffix string before running out of basename, strip it. */
> 		for(p3=argv[2]; *p3; p3++)
24c28,32
< 		*p1 = '\0';
---
> 		/* If p3 reached argv[2], the whole suffix matched -> strip.
> 		 * Otherwise the basename was shorter than the suffix (loop
> 		 * exited because p1==p2) -- leave it intact. */
> 		if (p3 == argv[2])
> 			*p1 = '\0';
27c35
< 	puts(p2, stdout);
---
> 	puts(p2);
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
5c5,8
< char	*ttyname();
---
> char	*ttyname(int f);
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
31c33,66
< 	if(argc<=1 || *arg!='-'&&*arg!='+') {
---
> 	/* POSIX-style: tail -c N FILE  or  tail -n N FILE.
> 	 * Translate to v7-style "-Nc" / "-Nl" so the rest of the parser
> 	 * keeps using its compact form.  Build a stack-local re-shape. */
> 	static char rebuf[32];
> 	int posix_shift = 0;
> 	if (argc >= 3 && arg && arg[0] == '-' && (arg[1] == 'c' || arg[1] == 'n')
> 	    && arg[2] == '\0') {
> 		char *num = argv[2];
> 		int v = 0, neg = 0;
> 		if (*num == '+' || *num == '-') {
> 			if (*num == '-') neg = 1; /* always neg here (from-end) */
> 			num++;
> 		}
> 		while (digit(*num)) { v = v*10 + *num - '0'; num++; }
> 		rebuf[0] = '-';
> 		{
> 			int rl = 1, t = v, dpos;
> 			char digs[12]; int ndig = 0;
> 			if (t == 0) digs[ndig++] = '0';
> 			while (t > 0) { digs[ndig++] = '0' + (t % 10); t /= 10; }
> 			for (dpos = ndig - 1; dpos >= 0; dpos--) rebuf[rl++] = digs[dpos];
> 			rebuf[rl++] = (arg[1] == 'c') ? 'c' : 'l';
> 			rebuf[rl] = '\0';
> 		}
> 		(void)neg;
> 		arg = rebuf;
> 		/* Shift argv so argv[2] becomes the optional filename. */
> 		argv[1] = arg;
> 		argv[2] = (argc > 3) ? argv[3] : (char *)0;
> 		argc = (argc > 3) ? argc - 1 : 2;
> 		posix_shift = 1;
> 	}
> 	(void)posix_shift;
> 	if(argc<=1 || (*arg!='-' && *arg!='+')) {
181c216,217
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
97c112
< 	if(EQ(a, "-t"))
---
> 	if(EQ(a, "-t")) {
101a117
> 	}
136a153
> 	return(0);
139,141c156,157
< tio(a, f)
< char *a;
< int f;
---
> int
> tio(char *a, int f)
152,153c168,169
< ftype(f)
< char *f;
---
> int
> ftype(char *f)
164,165c180,181
< fsizep(f)
< char *f;
---
> int
> fsizep(char *f)
173,174c189,190
< synbad(s1,s2)
< char *s1, *s2;
---
> void
> synbad(char *s1, char *s2)
183,184c199,200
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
119,120c123,124
< 	if(s[0] == '.')
< 		if(s[1] == '.')
---
> 	if(s[0] == '.') {
> 		if(s[1] == '.') {
125c129
< 		else if(s[1] == '\0')
---
> 		} else if(s[1] == '\0')
126a131
> 	}
130,131c135,136
< rmdir(f, iflg)
< char *f;
---
> int
> rmdir(char *f, int iflg)
151a157
> 	return(1);
154c160,161
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
8c8
< char	*rindex();
---
> char	*rindex(char *sp, int c);
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
9,10c9,11
< char	*strcat();
< char	*strcpy();
---
> char	*strcat(char *a, char *b);
> char	*strcpy(char *a, char *b);
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
11,13c11,14
< char	*rindex();
< char	*strcat();
< char	*strcpy();
---
> char	*rindex(char *sp, int c);
> char	*strcat(char *a, char *b);
> char	*strcpy(char *a, char *b);
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
18,19c18,24
< extern errno;
< long	lseek();
---
> int errno;
> long	lseek(int fd, long offset, int ptrname);
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
11c11,15
< char	*skip();
---
> char	*skip(register char *s);
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
120,121c123
< skip(s)
< register char *s;
---
> skip(register char *s)
123c125
< 	register nf, nl;
---
> 	register int nf, nl;
137,138c139,140
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
33,39c36,37
< char	*ctime();
< char	*asctime();
< struct	tm *localtime();
< struct	tm *gmtime();
< 
< main(argc, argv)
< char *argv[];
---
> int
> main(int argc, char *argv[])
51a50,91
> 	/* POSIX "+FORMAT": print the current time using strftime-like
> 	 * codes.  Supports %Y %y %m %d %H %M %S %s %j %a %b %e %p plus
> 	 * literal % via %%.  v7 date had no such mode. */
> 	if (argc > 1 && argv[1][0] == '+') {
> 		struct tm *tp;
> 		char *f = argv[1] + 1;
> 		time(&timbuf);
> 		tp = uflag ? gmtime(&timbuf) : localtime(&timbuf);
> 		while (*f) {
> 			if (*f != '%') { putchar(*f++); continue; }
> 			f++;
> 			switch (*f) {
> 			case 'Y': printf("%04d", tp->tm_year + 1900); break;
> 			case 'y': printf("%02d", tp->tm_year % 100); break;
> 			case 'm': printf("%02d", tp->tm_mon + 1); break;
> 			case 'd': printf("%02d", tp->tm_mday); break;
> 			case 'e': printf("%2d",  tp->tm_mday); break;
> 			case 'H': printf("%02d", tp->tm_hour); break;
> 			case 'M': printf("%02d", tp->tm_min); break;
> 			case 'S': printf("%02d", tp->tm_sec); break;
> 			case 's': printf("%ld",  (long)timbuf); break;
> 			case 'j': printf("%03d", tp->tm_yday + 1); break;
> 			case 'p': fputs(tp->tm_hour < 12 ? "AM" : "PM", stdout); break;
> 			case 'a': {
> 				static char *days[] = {"Sun","Mon","Tue","Wed","Thu","Fri","Sat"};
> 				fputs(days[tp->tm_wday & 7], stdout); break;
> 			}
> 			case 'b': {
> 				static char *mons[] = {"Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"};
> 				fputs(mons[tp->tm_mon % 12], stdout); break;
> 			}
> 			case '%': putchar('%'); break;
> 			case 'n': putchar('\n'); break;
> 			case 't': putchar('\t'); break;
> 			case '\0': putchar('%'); f--; break;
> 			default:  putchar('%'); putchar(*f); break;
> 			}
> 			if (*f) f++;
> 		}
> 		putchar('\n');
> 		exit(0);
> 	}
94c134,135
< gtime()
---
> int
> gtime(void)
152c193,194
< gp(dfault)
---
> int
> gp(int dfault)
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
7,8c8,15
< main(argc, argv)
< char **argv;
---
> int kill(int pid, int sig);
> int atoi(char *s);
> void exit(int n);
> extern char *sys_errlist[];
> int errno;
> 
> int
> main(int argc, char **argv)
10c17
< 	register signo, pid, res;
---
> 	register int signo, pid, res;
12,13d18
< 	extern char *sys_errlist[];
< 	extern errno;
18c23
< 		printf("usage: kill [ -signo ] pid ...\n");
---
> 		printf("usage: kill [ -signo ] pid ...\n       kill -l\n");
19a25,36
> 	}
> 	/* -l : list signal names (v7 had 16 signals; SIGTERM=15). */
> 	if (argv[1][0] == '-' && argv[1][1] == 'l' && argv[1][2] == '\0') {
> 		static char *names[] = {
> 			0, "HUP", "INT", "QUIT", "ILL", "TRAP", "IOT", "EMT",
> 			"FPE", "KILL", "BUS", "SEGV", "SYS", "PIPE", "ALRM",
> 			"TERM"
> 		};
> 		int s;
> 		for (s = 1; s <= 15; s++)
> 			printf("%2d) SIG%s\n", s, names[s]);
> 		return 0;
```

### cmd/nice.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/nice.c unix-v7-c99/cmd/nice.c || true
```

Expect:

```
5,7c5,13
< main(argc, argv)
< int argc;
< char *argv[];
---
> int atoi(char *s);
> int nice(int incr);
> int execvp(char *name, char **argv);
> void exit(int n);
> int errno;
> extern char *sys_errlist[];
> 
> int
> main(int argc, char *argv[])
10,11d15
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
1,3c1,6
< main(argc, argv)
< int argc;
< char **argv;
---
> #include <stdio.h>
> 
> int number(char *s);
> 
> int
> main(int argc, char **argv)
30,31c33,34
< number(s)
< char *s;
---
> int
> number(char *s)
36c39
< 	while(c = *s++) {
---
> 	while((c = *s++)) {
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
12,14c11,19
< char *ttyname(), *rindex(), *ctime(), *strcpy(), *index();
< main(argc, argv)
< char **argv;
---
> char *ttyname(int f), *rindex(char *sp, int c), *ctime(long *t);
> char *strcpy(char *a, char *b), *index(register char *sp, int c);
> int getuid(void);
> int time(long *t);
> void putline(void);
> void exit(int n);
> 
> int
> main(int argc, char **argv)
55c60,61
< putline()
---
> void
> putline(void)
```

### cmd/mesg.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/mesg.c unix-v7-c99/cmd/mesg.c || true
```

Expect:

```
17c17
< char *ttyname();
---
> char *ttyname(int f);
19,20c19,24
< main(argc, argv)
< char *argv[];
---
> void error(char *s);
> void newmode(int m);
> void exit(int n);
> 
> int
> main(int argc, char *argv[])
44,45c48,49
< error(s)
< char *s;
---
> void
> error(char *s)
51c55,56
< newmode(m)
---
> void
> newmode(int m)
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
11,12c11,15
< main(argc, argv)
< char **argv;
---
> void printt(char *s, long a);
> void exit(int n);
> 
> int
> main(int argc, char **argv)
16c19
< 	register p;
---
> 	register int p;
53,55c56,57
< printt(s, a)
< char *s;
< long a;
---
> void
> printt(char *s, long a)
58c60
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
8c8,13
< main(argc, argv) char **argv; {
---
> void check(FILE *f);
> void exit(int n);
> 
> int
> main(int argc, char **argv)
> {
33,34c38,39
< check(f)
< FILE	*f;
---
> void
> check(FILE *f)
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
25c26
< struct tm *localtime();
---
> struct tm *localtime(long *tim);
27,28c28,32
< tprint(t)
< long t;
---
> void tprint(long t);
> int time(long *t);
> 
> void
> tprint(long t)
36c40,41
< main()
---
> int
> main(void)
44a50
> 		/* FALLTHROUGH */
47a54
> 		/* FALLTHROUGH */
```

### cmd/col.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/col.c unix-v7-c99/cmd/col.c || true
```

Expect:

```
19c19,28
< char *strcpy();
---
> char *strcpy(char *a, char *b);
> void outc(int c);
> void store(int lno);
> void fetch(int lno);
> void emit(char *s, int lineno);
> void incr(void);
> void decr(void);
> char *malloc(unsigned n);
> void free(char *p);
> void exit(int n);
21,22c30,31
< main (argc, argv)
< 	int argc; char **argv;
---
> int
> main (int argc, char **argv)
162,163c171,172
< outc (c)
< 	register char c;
---
> void
> outc (register int c)
208c217,218
< store (lno)
---
> void
> store (int lno)
210,211d219
< 	char *malloc();
< 
223c231,232
< fetch(lno)
---
> void
> fetch(int lno)
236,238c245,246
< emit (s, lineno)
< 	char *s;
< 	int lineno;
---
> void
> emit (char *s, int lineno)
294c302,303
< incr()
---
> void
> incr(void)
308c317,318
< decr()
---
> void
> decr(void)
```

### cmd/fgrep.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/fgrep.c unix-v7-c99/cmd/fgrep.c || true
```

Expect:

```
33,34c33,41
< main(argc, argv)
< char **argv;
---
> void execute(char *file);
> int getargc(void);
> void cgotofn(void);
> void overflo(void);
> void cfail(void);
> void exit(int n);
> 
> int
> main(int argc, char **argv)
112,113c119,120
< execute(file)
< char *file;
---
> void
> execute(char *file)
117c124
< 	register ccount;
---
> 	register int ccount;
208c215
< 		if (*p++ == '\n')
---
> 		if (*p++ == '\n') {
215a223
> 		}
225c233,234
< getargc()
---
> int
> getargc(void)
227c236
< 	register c;
---
> 	register int c;
235,236c244,246
< cgotofn() {
< 	register c;
---
> void
> cgotofn(void) {
> 	register int c;
298c308,309
< overflo() {
---
> void
> overflo(void) {
302c313,314
< cfail() {
---
> void
> cfail(void) {
```

### cmd/su.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/su.c unix-v7-c99/cmd/su.c || true
```

Expect:

```
4,6c4,6
< struct	passwd *pwd,*getpwnam();
< char	*crypt();
< char	*getpass();
---
> struct	passwd *pwd;
> char	*crypt(char *pw, char *salt);
> char	*getpass(char *prompt);
9,11c9,10
< main(argc,argv)
< int	argc;
< char	**argv;
---
> int
> main(int argc, char **argv)
```

### cmd/newgrp.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/newgrp.c unix-v7-c99/cmd/newgrp.c || true
```

Expect:

```
5,7c5,7
< struct	group	*getgrnam(), *grp;
< struct	passwd	*getpwuid(), *pwd;
< char	*getpass(), *crypt();
---
> struct	group	*grp;
> struct	passwd	*pwd;
> char	*getpass(char *prompt), *crypt(char *pw, char *salt);
9,11c9,12
< main(argc,argv)
< int	argc;
< char	**argv;
---
> void done(void);
> 
> int
> main(int argc, char **argv)
13c14
< 	register i;
---
> 	register int i;
45c46,47
< done()
---
> void
> done(void)
47c49
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
4c4
< double	atof();
---
> double	atof(char *s);
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
13c13
< char	*getpass();
---
> char	*getpass(char *prompt);
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
8c8,10
< char	*crypt();
---
> char	*crypt(char *pw, char *salt);
> int	read(int fd, char *buf, int n);
> int	write(int fd, char *buf, int n);
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
17a18,36
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
> static int	diffh_isspace(int c);
> 
> static int
> diffh_isspace(int c)
> {
> 	return(c==' ' || c=='\t' || c=='\n' || c=='\v' || c=='\r' || c=='\f');
> }
20,21c39
< char *getl(f,n)
< long n;
---
> char *getl(int f, long n)
24,25c42
< 	char *malloc();
< 	register delta, nt;
---
> 	register int delta, nt;
42c59
< 		if(t==NULL)
---
> 		if(t==NULL) {
46a64
> 		}
55,56c73,74
< clrl(f,n)
< long n;
---
> void
> clrl(int f, long n)
58c76
< 	register i,j;
---
> 	register int i,j;
66,67c84,85
< movstr(s,t)
< register char *s, *t;
---
> void
> movstr(register char *s, register char *t)
69c87
< 	while(*t++= *s++)
---
> 	while((*t++= *s++))
73,74c91,92
< main(argc,argv)
< char **argv;
---
> int
> main(int argc, char **argv)
77c95
< 	FILE *dopen();
---
> 	FILE *dopen(char *f1, char *f2);
103c121
< 		return;
---
> 		return(0);
111c129,130
< easysynch()
---
> int
> easysynch(void)
114c133
< 	register k,m;
---
> 	register int k,m;
143c162,163
< output(a,b)
---
> int
> output(int a, int b)
145c165
< 	register i;
---
> 	register int i;
174,176c194,195
< change(a,b,c,d,s)
< long a,c;
< char *s;
---
> void
> change(long a, int b, long c, int d, char *s)
184,185c203,204
< range(a,b)
< long a;
---
> void
> range(long a, int b)
195,196c214,215
< cmp(s,t)
< char *s,*t;
---
> int
> cmp(char *s, char *t)
201,203c220,222
< 		if(bflag&&isspace(*s)&&isspace(*t)) {
< 			while(isspace(*++s)) ;
< 			while(isspace(*++t)) ;
---
> 		if(bflag&&diffh_isspace(*s)&&diffh_isspace(*t)) {
> 			while(diffh_isspace(*++s)) ;
> 			while(diffh_isspace(*++t)) ;
213,214c232,233
< FILE *dopen(f1,f2)
< char *f1,*f2;
---
> FILE *
> dopen(char *f1, char *f2)
219c238
< 	if(cmp(f1,"-")==0)
---
> 	if(cmp(f1,"-")==0) {
223a243
> 	}
227c247,248
< 		for(bptr=b;*bptr= *f1++;bptr++) ;
---
> 		for(bptr=b;(*bptr= *f1++);bptr++)
> 			;
232c253,254
< 		while(*bptr++= *f2++) ;
---
> 		while((*bptr++= *f2++))
> 			;
242,243c264,265
< progerr(s)
< char *s;
---
> void
> progerr(char *s)
248,249c270,271
< error(s,t)
< char *s,*t;
---
> void
> error(char *s, char *t)
256c278,279
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
13,30c13,30
< 	"0",	B0,
< 	"50",	B50,
< 	"75",	B75,
< 	"110",	B110,
< 	"134",	B134,
< 	"134.5",B134,
< 	"150",	B150,
< 	"200",	B200,
< 	"300",	B300,
< 	"600",	B600,
< 	"1200",	B1200,
< 	"1800",	B1800,
< 	"2400",	B2400,
< 	"4800",	B4800,
< 	"9600",	B9600,
< 	"exta",	EXTA,
< 	"extb",	EXTB,
< 	0,
---
> 	{"0",     B0},
> 	{"50",    B50},
> 	{"75",    B75},
> 	{"110",   B110},
> 	{"134",   B134},
> 	{"134.5", B134},
> 	{"150",   B150},
> 	{"200",   B200},
> 	{"300",   B300},
> 	{"600",   B600},
> 	{"1200",  B1200},
> 	{"1800",  B1800},
> 	{"2400",  B2400},
> 	{"4800",  B4800},
> 	{"9600",  B9600},
> 	{"exta",  EXTA},
> 	{"extb",  EXTB},
> 	{0,       0},
38,39c38
< 	"even",
< 	EVENP, 0,
---
> 	{"even", EVENP, 0},
41,42c40
< 	"-even",
< 	0, EVENP,
---
> 	{"-even", 0, EVENP},
44,45c42
< 	"odd",
< 	ODDP, 0,
---
> 	{"odd", ODDP, 0},
47,48c44
< 	"-odd",
< 	0, ODDP,
---
> 	{"-odd", 0, ODDP},
50,51c46
< 	"raw",
< 	RAW, 0,
---
> 	{"raw", RAW, 0},
53,54c48
< 	"-raw",
< 	0, RAW,
---
> 	{"-raw", 0, RAW},
56,57c50
< 	"cooked",
< 	0, RAW,
---
> 	{"cooked", 0, RAW},
59,60c52
< 	"-nl",
< 	CRMOD, 0,
---
> 	{"-nl", CRMOD, 0},
62,63c54
< 	"nl",
< 	0, CRMOD,
---
> 	{"nl", 0, CRMOD},
65,66c56
< 	"echo",
< 	ECHO, 0,
---
> 	{"echo", ECHO, 0},
68,69c58
< 	"-echo",
< 	0, ECHO,
---
> 	{"-echo", 0, ECHO},
71,72c60
< 	"LCASE",
< 	LCASE, 0,
---
> 	{"LCASE", LCASE, 0},
74,75c62
< 	"lcase",
< 	LCASE, 0,
---
> 	{"lcase", LCASE, 0},
77,78c64
< 	"-LCASE",
< 	0, LCASE,
---
> 	{"-LCASE", 0, LCASE},
80,81c66
< 	"-lcase",
< 	0, LCASE,
---
> 	{"-lcase", 0, LCASE},
83,84c68
< 	"-tabs",
< 	XTABS, 0,
---
> 	{"-tabs", XTABS, 0},
86,87c70
< 	"tabs",
< 	0, XTABS,
---
> 	{"tabs", 0, XTABS},
90,91c73
< 	"cbreak",
< 	CBREAK, 0,
---
> 	{"cbreak", CBREAK, 0},
93,94c75
< 	"-cbreak",
< 	0, CBREAK,
---
> 	{"-cbreak", 0, CBREAK},
96,97c77
< 	"cr0",
< 	CR0, CR3,
---
> 	{"cr0", CR0, CR3},
99,100c79
< 	"cr1",
< 	CR1, CR3,
---
> 	{"cr1", CR1, CR3},
102,103c81
< 	"cr2",
< 	CR2, CR3,
---
> 	{"cr2", CR2, CR3},
105,106c83
< 	"cr3",
< 	CR3, CR3,
---
> 	{"cr3", CR3, CR3},
108,109c85
< 	"tab0",
< 	TAB0, XTABS,
---
> 	{"tab0", TAB0, XTABS},
111,112c87
< 	"tab1",
< 	TAB1, XTABS,
---
> 	{"tab1", TAB1, XTABS},
114,115c89
< 	"tab2",
< 	TAB2, XTABS,
---
> 	{"tab2", TAB2, XTABS},
117,118c91
< 	"nl0",
< 	NL0, NL3,
---
> 	{"nl0", NL0, NL3},
120,121c93
< 	"nl1",
< 	NL1, NL3,
---
> 	{"nl1", NL1, NL3},
123,124c95
< 	"nl2",
< 	NL2, NL3,
---
> 	{"nl2", NL2, NL3},
126,127c97
< 	"nl3",
< 	NL3, NL3,
---
> 	{"nl3", NL3, NL3},
129,130c99
< 	"ff0",
< 	FF0, FF1,
---
> 	{"ff0", FF0, FF1},
132,133c101
< 	"ff1",
< 	FF1, FF1,
---
> 	{"ff1", FF1, FF1},
135,136c103
< 	"bs0",
< 	BS0, BS1,
---
> 	{"bs0", BS0, BS1},
138,139c105
< 	"bs1",
< 	BS1, BS1,
---
> 	{"bs1", BS1, BS1},
141,142c107
< 	"33",
< 	CR1, ALLDELAY,
---
> 	{"33", CR1, ALLDELAY},
144,145c109
< 	"tty33",
< 	CR1, ALLDELAY,
---
> 	{"tty33", CR1, ALLDELAY},
147,148c111
< 	"37",
< 	FF1+CR2+TAB1+NL1, ALLDELAY,
---
> 	{"37", FF1+CR2+TAB1+NL1, ALLDELAY},
150,151c113
< 	"tty37",
< 	FF1+CR2+TAB1+NL1, ALLDELAY,
---
> 	{"tty37", FF1+CR2+TAB1+NL1, ALLDELAY},
153,154c115
< 	"05",
< 	NL2, ALLDELAY,
---
> 	{"05", NL2, ALLDELAY},
156,157c117
< 	"vt05",
< 	NL2, ALLDELAY,
---
> 	{"vt05", NL2, ALLDELAY},
159,160c119
< 	"tn",
< 	CR1, ALLDELAY,
---
> 	{"tn", CR1, ALLDELAY},
162,163c121
< 	"tn300",
< 	CR1, ALLDELAY,
---
> 	{"tn300", CR1, ALLDELAY},
165,166c123
< 	"ti",
< 	CR2, ALLDELAY,
---
> 	{"ti", CR2, ALLDELAY},
168,169c125
< 	"ti700",
< 	CR2, ALLDELAY,
---
> 	{"ti700", CR2, ALLDELAY},
171,174c127
< 	"tek",
< 	FF1, ALLDELAY,
< 
< 	0,
---
> 	{0, 0, 0}
178a132,135
> int	eq(char *string);
> void	prmodes(void);
> void	delay(int m, char *s);
> void	prspeed(char *c, int s);
180,181c137,138
< main(argc, argv)
< char	*argv[];
---
> int
> main(int argc, char *argv[])
232,233c189,190
< eq(string)
< char *string;
---
> int
> eq(char *string)
249c206,207
< prmodes()
---
> void
> prmodes(void)
251c209
< 	register m;
---
> 	register int m;
284,285c242,243
< delay(m, s)
< char *s;
---
> void
> delay(int m, char *s)
296,297c254,255
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
8,9c8,10
< char	*strcpy();
< char	*strcat();
---
> char	*strcpy(char *a, char *b);
> char	*strcat(char *a, char *b);
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
9,10c9
< 	"/dev/rp0",
< 	"/dev/rp3",
---
> 	"/dev/root",
18c17,20
< daddr_t	alloc();
---
> int	errno;
> daddr_t	alloc(void);
> void	dfree(char *file);
> void	bread(daddr_t bno, char *buf, int cnt);
20,21c22,23
< main(argc, argv)
< char **argv;
---
> int
> main(int argc, char **argv)
35,36c37,38
< dfree(file)
< char *file;
---
> void
> dfree(char *file)
55c57
< alloc()
---
> alloc(void)
83,85c85,86
< bread(bno, buf, cnt)
< daddr_t bno;
< char *buf;
---
> void
> bread(daddr_t bno, char *buf, int cnt)
88d88
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
75c78
< 	while(c = *s++)
---
> 	while((c = *s++))
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
39,40c49,50
< main(argc,argv) int argc;
< char argv[];
---
> int
> main(int argc, char *argv[])
41a52,53
> 	(void)argc;
> 	(void)argv;
155c167
< 			if(iflev > 0)
---
> 			if(iflev > 0) {
159a172
> 			}
259a273
> 	return(0);
261c275,276
< ptabs(){
---
> int
> ptabs(void){
263a279
> 	return(0);
265c281,282
< getch(){
---
> int
> getch(void){
271c288,289
< puts(){
---
> int
> puts(void){
290a309
> 	return(0);
292,293c311,312
< lookup(tab)
< char *tab[];
---
> int
> lookup(char *tab[])
307c326,327
< gets(){
---
> int
> gets(void){
325c345,346
< gotelse(){
---
> int
> gotelse(void){
329a351
> 	return(0);
331c353,354
< getnl(){
---
> int
> getnl(void){
352c375,376
< comment(){
---
> int
> comment(void){
363a388
> 	return(0);
```

### cmd/sp.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sp.c unix-v7-c99/cmd/sp.c || true
```

Expect:

```
11c11,15
< getit()
---
> int	getit(void);
> int	putit(int ntab);
> int	clean(void);
> int
> getit(void)
13c17
< 	register c;
---
> 	register int c;
19a24
> 				/* fallthrough */
34c39,40
< putit(ntab)
---
> int
> putit(int ntab)
37a44
> 	return(0);
39c46,47
< clean()
---
> int
> clean(void)
41a50
> 	return(0);
43c52,53
< main(argc,argv) char *argv[];
---
> int
> main(int argc, char *argv[])
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
13a17
> #undef	EOF
101,102c105,166
< main(argc, argv)
< char **argv;
---
> int	commands(void);
> int	*address(void);
> void	setdot(void);
> void	setall(void);
> void	setnoaddr(void);
> void	nonzero(void);
> void	newline(void);
> void	filename(int comm);
> void	exfile(void);
> int	error(char *s);
> void	exitsh(void);
> void	rmtemp(void);
> void	fcomp(void);
> void	dechain(void);
> void	execexp(void);
> int	dosub(void);
> int	arout(void);
> int	command(int *aaddr1);
> int	advance(char *lp, char *ep);
> int	append(int (*f)(void), int *a);
> int	backref(int i, char *lp);
> int	blkio(int b, char *buf, int (*iofcn)());
> int	callunix(void);
> int	cclass(char *set, int c, int af);
> int	compile(int aeof);
> int	compsub(void);
> int	crblock(char *permp, char *buf, int nchar, long startn);
> int	crinit(char *crypt_password, char *block);
> int	delete(void);
> int	execute(int gf, int *addr);
> int	getchr(void);
> int	getcopy(void);
> int	getfile(void);
> int	getsub(void);
> int	gettty(void);
> int	global(int k);
> int	init(void);
> int	join(void);
> int	move(int cflag);
> int	onhup(int sig);
> int	onintr(int sig);
> char	*place(char *sp, char *l1, char *l2);
> int	putchr(int ac);
> int	putd(void);
> int	putfile(void);
> int	puts1(char *sp);
> int	putst(char *sp);
> int	quit(int sig);
> int	reverse(int *a1, int *a2);
> int	setwide(void);
> int	squeeze(int i);
> char	*getblock(int atl, int iof);
> int	unixcom(void);
> int	getkey(void);
> int	puts(char *s);
> int	substitute(int inglob);
> int	putline(void);
> int	rdelete(int *ad1, int *ad2);
> int	makekey(char *kp, char *km);
> 
> int
> main(int argc, char **argv)
108,110c172,174
< 	oldquit = signal(SIGQUIT, SIG_IGN);
< 	oldhup = signal(SIGHUP, SIG_IGN);
< 	oldintr = signal(SIGINT, SIG_IGN);
---
> 	oldquit = (int (*)())(long)signal(SIGQUIT, SIG_IGN);
> 	oldhup = (int (*)())(long)signal(SIGHUP, SIG_IGN);
> 	oldintr = (int (*)())(long)signal(SIGINT, SIG_IGN);
141c205
< 		while (*p2++ = *p1++)
---
> 		while ((*p2++ = *p1++))
154c218
< 	quit();
---
> 	quit(0);
157c221,222
< commands()
---
> int
> commands(void)
159,160c224,225
< 	int getfile(), gettty();
< 	register *a1, c;
---
> 	int getfile(void), gettty(void);
> 	register int *a1, c;
203a269
> 		/* fallthrough */
265a332
> 		/* fallthrough */
281a349
> 		/* fallthrough */
285c353,354
< 		quit();
---
> 		quit(0);
> 		/* fallthrough */
327a397
> 		/* fallthrough */
367c437
< 		return;
---
> 		return(0);
375c445
< address()
---
> address(void)
377c447,448
< 	register *a1, minus, c;
---
> 	register int *a1;
> 	register int minus, c;
471c542,543
< setdot()
---
> void
> setdot(void)
479c551,552
< setall()
---
> void
> setall(void)
490c563,564
< setnoaddr()
---
> void
> setnoaddr(void)
496c570,571
< nonzero()
---
> void
> nonzero(void)
502c577,578
< newline()
---
> void
> newline(void)
504c580
< 	register c;
---
> 	register int c;
518c594,595
< filename(comm)
---
> void
> filename(int comm)
521c598
< 	register c;
---
> 	register int c;
530c607
< 		while (*p2++ = *p1++)
---
> 		while ((*p2++ = *p1++))
550c627
< 		while (*p1++ = *p2++)
---
> 		while ((*p1++ = *p2++))
555c632,633
< exfile()
---
> void
> exfile(void)
565c643,644
< onintr()
---
> int
> onintr(int sig)
566a646
> 	(void)sig;
570a651
> 	return 0;
573c654,655
< onhup()
---
> int
> onhup(int sig)
574a657
> 	(void)sig;
585c668,669
< 	quit();
---
> 	quit(0);
> 	return(0);
588,589c672,673
< error(s)
< char *s;
---
> int
> error(char *s)
591c675
< 	register c;
---
> 	register int c;
611a696
> 	return(0);
614c699,700
< getchr()
---
> int
> getchr(void)
617c703
< 	if (lastc=peekc) {
---
> 	if ((lastc=peekc)) {
633c719,720
< gettty()
---
> int
> gettty(void)
635c722
< 	register c;
---
> 	register int c;
659c746,747
< getfile()
---
> int
> getfile(void)
661c749
< 	register c;
---
> 	register int c;
695c783,784
< putfile()
---
> int
> putfile(void)
699c788
< 	register nib;
---
> 	register int nib;
731a821
> 	return(0);
734,736c824,825
< append(f, a)
< int *a;
< int (*f)();
---
> int
> append(int (*f)(), int *a)
738c827
< 	register *a1, *a2, *rdot;
---
> 	register int *a1, *a2, *rdot;
744c833
< 		if ((dol-zero)+1 >= nlall) {
---
> 		if ((unsigned)((dol-zero)+1) >= nlall) {
768c857,858
< callunix()
---
> int
> callunix(void)
770c860
< 	register (*savint)(), pid, rpid;
---
> 	register int (*savint)(), pid, rpid;
780c870
< 	savint = signal(SIGINT, SIG_IGN);
---
> 	savint = (int (*)())(long)signal(SIGINT, SIG_IGN);
784a875
> 	return(0);
787c878,879
< quit()
---
> int
> quit(int sig)
788a881
> 	(void)sig;
797c890,891
< delete()
---
> int
> delete(void)
802a897
> 	return 0;
805,806c900,901
< rdelete(ad1, ad2)
< int *ad1, *ad2;
---
> int
> rdelete(int *ad1, int *ad2)
808c903
< 	register *a1, *a2, *a3;
---
> 	register int *a1, *a2, *a3;
821a917
> 	return(0);
824c920,921
< gdelete()
---
> int
> gdelete(void)
826c923
< 	register *a1, *a2, *a3;
---
> 	register int *a1, *a2, *a3;
831c928
< 			return;
---
> 			return(0);
842a940
> 	return(0);
846c944
< getline(tl)
---
> getline(int tl)
849c947
< 	register nl;
---
> 	register int nl;
855c953
< 	while (*lp++ = *bp++)
---
> 	while ((*lp++ = *bp++))
863c961,962
< putline()
---
> int
> putline(void)
866c965
< 	register nl;
---
> 	register int nl;
875c974
< 	while (*bp = *lp++) {
---
> 	while ((*bp = *lp++)) {
892c991
< getblock(atl, iof)
---
> getblock(int atl, int iof)
894,895c993
< 	extern read(), write();
< 	register bno, off;
---
> 	register int bno, off;
941,943c1039,1040
< blkio(b, buf, iofcn)
< char *buf;
< int (*iofcn)();
---
> int
> blkio(int b, char *buf, int (*iofcn)())
948a1046
> 	return 0;
951c1049,1050
< init()
---
> int
> init(void)
953c1052
< 	register *markp;
---
> 	register int *markp;
970a1070
> 	return(0);
973c1073,1074
< global(k)
---
> int
> global(int k)
976c1077
< 	register c;
---
> 	register int c;
1012c1113
< 		return;
---
> 		return(0);
1022a1124
> 	return(0);
1025c1127,1128
< join()
---
> int
> join(void)
1028c1131
< 	register *a1;
---
> 	register int *a1;
1033c1136
< 		while (*gp = *lp++)
---
> 		while ((*gp = *lp++))
1039c1142
< 	while (*lp++ = *gp++)
---
> 	while ((*lp++ = *gp++))
1044a1148
> 	return(0);
1047c1151,1152
< substitute(inglob)
---
> int
> substitute(int inglob)
1049c1154
< 	register *markp, *a1, nl;
---
> 	register int *markp, *a1, nl;
1051c1156
< 	int getsub();
---
> 	int getsub(void);
1083a1189
> 	return(0);
1086c1192,1193
< compsub()
---
> int
> compsub(void)
1088c1195
< 	register seof, c;
---
> 	register int seof, c;
1121c1228,1229
< getsub()
---
> int
> getsub(void)
1128c1236
< 	while (*p1++ = *p2++)
---
> 	while ((*p1++ = *p2++))
1134c1242,1243
< dosub()
---
> int
> dosub(void)
1144c1253
< 	while (c = *rp++&0377) {
---
> 	while ((c = *rp++&0377)) {
1158c1267
< 	while (*sp++ = *lp++)
---
> 	while ((*sp++ = *lp++))
1163c1272
< 	while (*lp++ = *sp++)
---
> 	while ((*lp++ = *sp++))
1164a1274
> 	return(0);
1168,1169c1278
< place(sp, l1, l2)
< register char *sp, *l1, *l2;
---
> place(register char *sp, register char *l1, register char *l2)
1180c1289,1290
< move(cflag)
---
> int
> move(int cflag)
1183c1293
< 	int getcopy();
---
> 	int getcopy(void);
1209c1319
< 			return;
---
> 			return(0);
1220a1331
> 	return(0);
1223,1224c1334,1335
< reverse(a1, a2)
< register int *a1, *a2;
---
> int
> reverse(register int *a1, register int *a2)
1231c1342
< 			return;
---
> 			return(0);
1237c1348,1349
< getcopy()
---
> int
> getcopy(void)
1245c1357,1358
< compile(aeof)
---
> int
> compile(int aeof)
1247c1360
< 	register eof, c;
---
> 	register int eof, c;
1259c1372
< 		return;
---
> 		return(0);
1277c1390
< 			return;
---
> 			return(0);
1371a1485
> 	return(0);
1374,1375c1488,1489
< execute(gf, addr)
< int *addr;
---
> int
> execute(int gf, int *addr)
1380,1381c1494,1495
< 		braslist[c] = 0;
< 		braelist[c] = 0;
---
> 		braslist[(unsigned char)c] = 0;
> 		braelist[(unsigned char)c] = 0;
1388c1502
< 		while (*p1++ = *p2++)
---
> 		while ((*p1++ = *p2++))
1425,1426c1539,1540
< advance(lp, ep)
< register char *ep, *lp;
---
> int
> advance(register char *lp, register char *ep)
1467c1581
< 		braslist[*ep++] = lp;
---
> 		braslist[(unsigned char)*ep++] = lp;
1471c1585
< 		braelist[*ep++] = lp;
---
> 		braelist[(unsigned char)*ep++] = lp;
1532,1534c1646,1647
< backref(i, lp)
< register i;
< register char *lp;
---
> int
> backref(register int i, register char *lp)
1545,1546c1658,1659
< cclass(set, c, af)
< register char *set, c;
---
> int
> cclass(register char *set, register int c, int af)
1548c1661
< 	register n;
---
> 	register int n;
1559c1672,1673
< putd()
---
> int
> putd(void)
1561c1675
< 	register r;
---
> 	register int r;
1567a1682
> 	return(0);
1570,1571c1685,1686
< puts(sp)
< register char *sp;
---
> int
> puts(register char *sp)
1576a1692
> 	return(0);
1582c1698,1699
< putchr(ac)
---
> int
> putchr(int ac)
1585c1702
< 	register c;
---
> 	register int c;
1621c1738
< 		return;
---
> 		return(0);
1623a1741
> 	return(0);
1625,1628c1743,1744
< crblock(permp, buf, nchar, startn)
< char *permp;
< char *buf;
< long startn;
---
> int
> crblock(char *permp, char *buf, int nchar, long startn)
1651a1768
> 	return(0);
1654c1771,1772
< getkey()
---
> int
> getkey(void)
1660c1778
< 	register c;
---
> 	register int c;
1662c1780
< 	sig = signal(SIGINT, SIG_IGN);
---
> 	sig = (int (*)())(long)signal(SIGINT, SIG_IGN);
1685,1686c1803,1804
< crinit(keyp, permp)
< char	*keyp, *permp;
---
> int
> crinit(char *keyp, char *permp)
1689c1807
< 	register i;
---
> 	register int i;
1748,1749c1866,1867
< makekey(a, b)
< char *a, *b;
---
> int
> makekey(char *a, char *b)
1761a1880
> 	return(0);
```

### lib/l3.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/l3.c unix-v7-c99/lib/l3.c || true
```

Expect:

```
4,7c4,5
< ltol3(cp, lp, n)
< char	*cp;
< long	*lp;
< int	n;
---
> int
> ltol3(char *cp, long *lp, int n)
9c7
< 	register i;
---
> 	register int i;
22d19
< 		b++;
24a22
> 		b++;
26a25
> 	return(0);
29,32c28,29
< l3tol(lp, cp, n)
< long	*lp;
< char	*cp;
< int	n;
---
> int
> l3tol(long *lp, char *cp, int n)
34c31
< 	register i;
---
> 	register int i;
47d43
< 		*a++ = 0;
49a46
> 		*a++ = 0;
51a49
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

### h/conf.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/conf.h unix-v7-c99/h/conf.h || true
```

Expect:

```
9a10
> struct buf;
12,14c13,15
< 	int	(*d_open)();
< 	int	(*d_close)();
< 	int	(*d_strategy)();
---
> 	int	(*d_open)(dev_t dev, int rw);
> 	int	(*d_close)(dev_t dev, int flag);
> 	int	(*d_strategy)(struct buf *bp);
19c20,21
<  * Character device switch.
---
>  * Character device switch.  v7's d_ioctl, d_stop, d_ttys are gone --
>  * cdevsw[] is empty on this port (no char-device drivers wire it).
23,29c25,28
< 	int	(*d_open)();
< 	int	(*d_close)();
< 	int	(*d_read)();
< 	int	(*d_write)();
< 	int	(*d_ioctl)();
< 	int	(*d_stop)();
< 	struct tty *d_ttys;
---
> 	int	(*d_open)(dev_t dev, int rw);
> 	int	(*d_close)(dev_t dev, int flag);
> 	int	(*d_read)(dev_t dev);
> 	int	(*d_write)(dev_t dev);
32,47d30
< /*
<  * tty line control switch.
<  */
< extern struct linesw
< {
< 	int	(*l_open)();
< 	int	(*l_close)();
< 	int	(*l_read)();
< 	char	*(*l_write)();
< 	int	(*l_ioctl)();
< 	int	(*l_rint)();
< 	int	(*l_rend)();
< 	int	(*l_meta)();
< 	int	(*l_start)();
< 	int	(*l_modem)();
< } linesw[];
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
11c11,15
< 	char	f_count;	/* reference count */
---
> 	short	f_count;	/* reference count.  PORT: widened from
> 				 * char (8-bit, max 255) because every fork
> 				 * bumps every open file's count by 1; with
> 				 * sh's 5+ open FDs, ~250 sequential forks
> 				 * overflowed it and corrupted refcounts. */
12a17,19
> 	/* v7 had a union { off_t f_offset; struct chan *f_chan; } here for
> 	 * the mpx multiplexor channel pointer overlap.  This port doesn't
> 	 * wire mpx, so the union collapses to just the offset field. */
15d21
< 		struct chan *f_chan;	/* mpx channel pointer */
25,28c31,32
< #define FMPX	010
< #define	FMPY	020
< #define	FMP	030
< #define	FKERNEL	040
---
> /* FMP (file is mpx multiplexor channel) gone -- mpx subsystem not wired
>  * on this port; FMP was never set, so the bit-test branches were dead. */
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

### h/seg.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/seg.h unix-v7-c99/h/seg.h || true
```

Expect:

```
2c2,4
<  * KT-11 addresses and bits.
---
>  * v7 KT-11 segmentation-register addresses and access-mode bits.
>  * UDSA (user D-space) and ka6 (kernel ISA reg 6) were used only by
>  * sys/dev/bio.c::physio() (removed earlier), so they are gone.
5,7c7,8
< #define	UISD	((physadr)0177600)	/* first user I-space descriptor register */
< #define	UISA	((physadr)0177640)	/* first user I-space address register */
< #define	UDSA	((physadr)0177660)	/* first user D-space address register */
---
> #define	UISD	((physadr)0177600)	/* first user I-space descriptor reg */
> #define	UISA	((physadr)0177640)	/* first user I-space address reg */
13,23d13
< 
< /*
<  * structure used to address
<  * a sequence of integers.
<  */
< physadr	ka6;		/* 11/40 KISA6; 11/45 KDSA6 */
< 
< /*
<  * address to access 11/70 UNIBUS map
<  */
< #define	UBMAP	((physadr)0170200)
```

### h/stat.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/stat.h unix-v7-c99/h/stat.h || true
```

Expect:

```
21,22c21,22
< #define		S_IFMPC	0030000	/* multiplexed char special */
< #define		S_IFMPB	0070000	/* multiplexed block special */
---
> /* S_IFMPC/S_IFMPB (mpx multiplexor char/block) removed -- mpx is not
>  * wired on this port and no userspace code names these. */
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
27,35d26
< struct tc {
< 	char	t_intrc;	/* interrupt */
< 	char	t_quitc;	/* quit */
< 	char	t_startc;	/* start output */
< 	char	t_stopc;	/* stop output */
< 	char	t_eofc;		/* end-of-file */
< 	char	t_brkc;		/* input delimiter (like nl) */
< };
< 
41,43c32,33
< 	int	(* t_oproc)();	/* routine to start output */
< 	int	(* t_iproc)();	/* routine to start input */
< 	struct chan *t_chan;	/* destination channel */
---
> 	int	(* t_oproc)(void);	/* routine to start output */
> 	int	(* t_iproc)(void);	/* routine to start input */
58,61d47
< 	union {
< 		struct tc;
< 		struct clist t_ctlq;
< 	} t_un;
63,64d48
< 
< #define	tun	tp->t_un
```

### sys/acct.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/acct.c unix-v7-c99/sys/acct.c || true
```

Expect:

```
8c8,9
< #include "../h/seg.h"
---
> 
> /* suser/plock/iput/prele/namei/uchar/writei come from h/systm.h. */
14c15,16
< sysacct()
---
> void
> sysacct(void)
47a50,51
> int compress(time_t t);
> 
51c55,56
< acct()
---
> void
> acct(void)
53c58
< 	register i;
---
> 	register int i;
60c65
< 	for (i=0; i<sizeof(acctbuf.ac_comm); i++)
---
> 	for (i=0; i<(int)sizeof(acctbuf.ac_comm); i++)
88,89c93,94
< compress(t)
< register time_t t;
---
> int
> compress(time_t t)
91c96
< 	register exp = 0, round = 0;
---
> 	register int exp = 0, round = 0;
108,113c113,117
< /*
<  * lock user into core as much
<  * as possible. swapping may still
<  * occur if core grows.
<  */
< syslock()
---
> /* lock(2): v7 toggled SULOCK to pin the process resident.  This port
>  * keeps every proc permanently in RAM, so the only remaining behavior
>  * is to enforce the superuser check (matching v7's EPERM for non-root). */
> void
> syslock(void)
115,126c119
< 	register struct proc *p;
< 	register struct a {
< 		int	flag;
< 	} *uap;
< 
< 	uap = (struct a *)u.u_ap;
< 	if(suser()) {
< 		p = u.u_procp;
< 		p->p_flag &= ~SULOCK;
< 		if(uap->flag)
< 			p->p_flag |= SULOCK;
< 	}
---
> 	(void)suser();
```

### sys/alloc.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/alloc.c unix-v7-c99/sys/alloc.c || true
```

Expect:

```
6d5
< #include "../h/conf.h"
11a11
> #include "../h/proto.h"
13a14,18
> /* bread/getblk/brelse/bwrite/bflush/clrbuf/sleep/wakeup/panic/prdev come from h/proto.h.
>  * iget/iput/iupdat/bcopy come from h/systm.h. */
> 
> int badblock(register struct filsys *fp, daddr_t bn, dev_t dev);
> 
26,27c31
< alloc(dev)
< dev_t dev;
---
> alloc(dev_t dev)
78,80c82,83
< free(dev, bno)
< dev_t dev;
< daddr_t bno;
---
> void
> free(dev_t dev, daddr_t bno)
120,123c123,124
< badblock(fp, bn, dev)
< register struct filsys *fp;
< daddr_t bn;
< dev_t dev;
---
> int
> badblock(register struct filsys *fp, daddr_t bn, dev_t dev)
145,146c146
< ialloc(dev)
< dev_t dev;
---
> ialloc(dev_t dev)
223,225c223,224
< ifree(dev, ino)
< dev_t dev;
< ino_t ino;
---
> void
> ifree(dev_t dev, ino_t ino)
257,258c256
< getfs(dev)
< dev_t dev;
---
> getfs(dev_t dev)
286c284,285
< update()
---
> void
> update(void)
```

### sys/clock.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/clock.c unix-v7-c99/sys/clock.c || true
```

Expect:

```
3,4d2
< #include "../h/callo.h"
< #include "../h/seg.h"
8c6,9
< #include "../h/reg.h"
---
> #include "../h/proto.h"
> 
> extern void addupc(caddr_t pc, void *prof, int inc);	/* sys/v7stubs.c stub */
> /* wakeup/spl1 come from h/proto.h.  psignal/setpri come from h/systm.h. */
28,30c29,30
< clock(dev, sp, r1, nps, r0, pc, ps)
< dev_t dev;
< caddr_t pc;
---
> void
> clock(dev_t dev, int sp, int r1, int nps, int r0, caddr_t pc, int ps)
32d31
< 	register struct callo *p1, *p2;
35a35
> 	(void)dev; (void)sp; (void)r1; (void)nps; (void)r0;
37,59c37,42
< 	/*
< 	 * restart clock
< 	 */
< 
< 	lks->r[0] = 0115;
< 
< 	/*
< 	 * display register
< 	 */
< 
< 	display();
< 	/*
< 	 * callouts
< 	 * if none, just continue
< 	 * else update first non-zero time
< 	 */
< 
< 	if(callout[0].c_func == NULL)
< 		goto out;
< 	p2 = &callout[0];
< 	while(p2->c_time<=0 && p2->c_func!=NULL)
< 		p2++;
< 	p2->c_time--;
---
> 	/* v7 rearmed the KW11-L by writing 0115 to lks->r[0] and snapshotted
> 	 * the front-panel switch register via display(); on this port the
> 	 * timer is rearmed by clock_irq_handler's cntv_tval_set and there is
> 	 * no front panel, so both calls are gone. */
> 	/* v7's per-tick callout[] dispatch is gone on this port -- nothing
> 	 * registers via timeout() so the callout table is permanently empty. */
68,87d50
< 	 * callout
< 	 */
< 
< 	spl5();
< 	if(callout[0].c_time <= 0) {
< 		p1 = &callout[0];
< 		while(p1->c_func != 0 && p1->c_time <= 0) {
< 			(*p1->c_func)(p1->c_arg);
< 			p1++;
< 		}
< 		p2 = &callout[0];
< 		while(p2->c_func = p1->c_func) {
< 			p2->c_time = p1->c_time;
< 			p2->c_arg = p1->c_arg;
< 			p1++;
< 			p2++;
< 		}
< 	}
< 
< 	/*
140,185c103,106
< /*
<  * timeout is called to arrange that
<  * fun(arg) is called in tim/HZ seconds.
<  * An entry is sorted into the callout
<  * structure. The time in each structure
<  * entry is the number of HZ's more
<  * than the previous entry.
<  * In this way, decrementing the
<  * first entry has the effect of
<  * updating all entries.
<  *
<  * The panic is there because there is nothing
<  * intelligent to be done if an entry won't fit.
<  */
< timeout(fun, arg, tim)
< int (*fun)();
< caddr_t arg;
< {
< 	register struct callo *p1, *p2;
< 	register int t;
< 	int s;
< 
< 	t = tim;
< 	p1 = &callout[0];
< 	s = spl7();
< 	while(p1->c_func != 0 && p1->c_time <= t) {
< 		t -= p1->c_time;
< 		p1++;
< 	}
< 	if (p1 >= &callout[NCALL-1])
< 		panic("Timeout table overflow");
< 	p1->c_time -= t;
< 	p2 = p1;
< 	while(p2->c_func != 0)
< 		p2++;
< 	while(p2 >= p1) {
< 		(p2+1)->c_time = p2->c_time;
< 		(p2+1)->c_func = p2->c_func;
< 		(p2+1)->c_arg = p2->c_arg;
< 		p2--;
< 	}
< 	p1->c_time = t;
< 	p1->c_func = fun;
< 	p1->c_arg = arg;
< 	splx(s);
< }
---
> /* v7's timeout() registered fun(arg) for deferred call after tim/HZ
>  * seconds via the callout[] table.  No driver on this port registers
>  * timeouts (the v7 callers were in dh.c / kl.c / etc., none of which
>  * exist here), so the function and the table are removed. */
```

### sys/fio.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/fio.c unix-v7-c99/sys/fio.c || true
```

Expect:

```
9d8
< #include "../h/reg.h"
10a10,13
> #include "../h/proto.h"
> 
> /* wakeup() is declared in h/proto.h.
>  * plock/iput/getfs/namei/uchar/suser/ufalloc/xrele come from h/systm.h. */
20,21c23
< getf(f)
< register int f;
---
> getf(register int f)
45,46c47,48
< closef(fp)
< register struct file *fp;
---
> void
> closef(register struct file *fp)
51,52c53
< 	register int (*cfunc)();
< 	struct chan *cp;
---
> 	register int (*cfunc)(dev_t, int);
62d62
< 	cp = fp->f_un.f_chan;
90,94c90,93
< 	if ((flag & FMP) == 0)
< 		for(fp=file; fp < &file[NFILE]; fp++)
< 			if (fp->f_count && fp->f_inode==ip)
< 				return;
< 	(*cfunc)(dev, flag, cp);
---
> 	for(fp=file; fp < &file[NFILE]; fp++)
> 		if (fp->f_count && fp->f_inode==ip)
> 			return;
> 	(*cfunc)(dev, flag);
97,129c96,99
< /*
<  * openi called to allow handler
<  * of special files to initialize and
<  * validate before actual IO.
<  */
< openi(ip, rw)
< register struct inode *ip;
< {
< 	dev_t dev;
< 	register unsigned int maj;
< 
< 	dev = (dev_t)ip->i_un.i_rdev;
< 	maj = major(dev);
< 	switch(ip->i_mode&IFMT) {
< 
< 	case IFCHR:
< 	case IFMPC:
< 		if(maj >= nchrdev)
< 			goto bad;
< 		(*cdevsw[maj].d_open)(dev, rw);
< 		break;
< 
< 	case IFBLK:
< 	case IFMPB:
< 		if(maj >= nblkdev)
< 			goto bad;
< 		(*bdevsw[maj].d_open)(dev, rw);
< 	}
< 	return;
< 
< bad:
< 	u.u_error = ENXIO;
< }
---
> /* v7 openi() (per-driver d_open dispatch for IFCHR/IFBLK) is gone --
>  * open(2) on this port routes through arch/arm.c::kopen(), which
>  * handles the pseudo-fds and IFREG itself.  The cdevsw[]/bdevsw[]
>  * d_open hook was never reached. */
144,145c114,115
< access(ip, mode)
< register struct inode *ip;
---
> int
> access(register struct inode *ip, int mode)
147c117
< 	register m;
---
> 	register int m;
185c155
< owner()
---
> owner(void)
204c174,175
< suser()
---
> int
> suser(void)
218c189,190
< ufalloc()
---
> int
> ufalloc(void)
220c192
< 	register i;
---
> 	register int i;
232,260c204,206
< /*
<  * Allocate a user file descriptor
<  * and a file structure.
<  * Initialize the descriptor
<  * to point at the file structure.
<  *
<  * no file -- if there are no available
<  * 	file structures.
<  */
< struct file *
< falloc()
< {
< 	register struct file *fp;
< 	register i;
< 
< 	i = ufalloc();
< 	if(i < 0)
< 		return(NULL);
< 	for(fp = &file[0]; fp < &file[NFILE]; fp++)
< 		if(fp->f_count == 0) {
< 			u.u_ofile[i] = fp;
< 			fp->f_count++;
< 			fp->f_un.f_offset = 0;
< 			return(fp);
< 		}
< 	printf("no file\n");
< 	u.u_error = ENFILE;
< 	return(NULL);
< }
---
> /* v7 falloc() (allocate fd + file slot, return file*) is gone -- its
>  * only callers were sys2.c::open1 and pipe.c::pipe, both removed.
>  * arch/arm.c uses its own files[NFD] table instead of file[NFILE]. */
```

### sys/pipe.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/pipe.c unix-v7-c99/sys/pipe.c || true
```

Expect:

```
7c7,10
< #include "../h/reg.h"
---
> #include "../h/proto.h"
> 
> /* readi/writei/plock/prele/psignal/min come from h/systm.h.
>  * sleep/wakeup come from h/proto.h. */
19,56c22,27
< /*
<  * The sys-pipe entry.
<  * Allocate an inode on the root device.
<  * Allocate 2 file structures.
<  * Put it all together with flags.
<  */
< pipe()
< {
< 	register struct inode *ip;
< 	register struct file *rf, *wf;
< 	int r;
< 
< 	ip = ialloc(pipedev);
< 	if(ip == NULL)
< 		return;
< 	rf = falloc();
< 	if(rf == NULL) {
< 		iput(ip);
< 		return;
< 	}
< 	r = u.u_r.r_val1;
< 	wf = falloc();
< 	if(wf == NULL) {
< 		rf->f_count = 0;
< 		u.u_ofile[r] = NULL;
< 		iput(ip);
< 		return;
< 	}
< 	u.u_r.r_val2 = u.u_r.r_val1;
< 	u.u_r.r_val1 = r;
< 	wf->f_flag = FWRITE|FPIPE;
< 	wf->f_inode = ip;
< 	rf->f_flag = FREAD|FPIPE;
< 	rf->f_inode = ip;
< 	ip->i_count = 2;
< 	ip->i_mode = IFREG;
< 	ip->i_flag = IACC|IUPD|ICHG;
< }
---
> /* v7's pipe(2) implementation (allocate inode + two file structs + wire
>  * FREAD/FWRITE) is gone -- arch/arm.c::sys_pipe maintains its own
>  * pipes[NPIPES] table that doesn't touch the v7 inode[]/file[] arrays.
>  * readp() and writep() are still kept because v7's read(2)/write(2)
>  * fast path on FPIPE-flagged file structs lands here, even though new
>  * pipe creation no longer creates such structs in this port. */
61,62c32,33
< readp(fp)
< register struct file *fp;
---
> void
> readp(register struct file *fp)
116,117c87,88
< writep(fp)
< register struct file *fp;
---
> void
> writep(register struct file *fp)
119c90
< 	register c;
---
> 	register int c;
184,216c155,157
< /*
<  * Lock a pipe.
<  * If its already locked,
<  * set the WANT bit and sleep.
<  */
< plock(ip)
< register struct inode *ip;
< {
< 
< 	while(ip->i_flag&ILOCK) {
< 		ip->i_flag |= IWANT;
< 		sleep((caddr_t)ip, PINOD);
< 	}
< 	ip->i_flag |= ILOCK;
< }
< 
< /*
<  * Unlock a pipe.
<  * If WANT bit is on,
<  * wakeup.
<  * This routine is also used
<  * to unlock inodes in general.
<  */
< prele(ip)
< register struct inode *ip;
< {
< 
< 	ip->i_flag &= ~ILOCK;
< 	if(ip->i_flag&IWANT) {
< 		ip->i_flag &= ~IWANT;
< 		wakeup((caddr_t)ip);
< 	}
< }
---
> /* v7's plock/prele are in sys/v7stubs.c -- cooperative-scheduling
>  * variants that just flip ILOCK without ever sleeping, since the ARM
>  * port runs without the v7 sleep()/wakeup() handoff path. */
```

### sys/rdwri.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/rdwri.c unix-v7-c99/sys/rdwri.c || true
```

Expect:

```
7a8,12
> #include "../h/proto.h"
> 
> /* bread/breada/getblk/geteblk/brelse/bdwrite/clrbuf come from h/proto.h.
>  * cpass/passc/copyin/copyout/bmap/min come from h/systm.h. */
> extern void iomove(register caddr_t cp, register int n, int flag);
19,20c24,25
< readi(ip)
< register struct inode *ip;
---
> void
> readi(register struct inode *ip)
26,27c31,32
< 	register on, n;
< 	register type;
---
> 	register int on, n;
> 	register int type;
39c44,45
< 		return((*cdevsw[major(dev)].d_read)(dev));
---
> 		(*cdevsw[major(dev)].d_read)(dev);
> 		return;
83,84c89,90
< writei(ip)
< register struct inode *ip;
---
> void
> writei(register struct inode *ip)
89,90c95,96
< 	register n, on;
< 	register type;
---
> 	register int n, on;
> 	register int type;
116c122
< 		if(n == BSIZE) 
---
> 		if(n == BSIZE)
132,143d137
< /*
<  * Return the logical maximum
<  * of the 2 arguments.
<  */
< max(a, b)
< unsigned a, b;
< {
< 
< 	if(a > b)
< 		return(a);
< 	return(b);
< }
149,150c143,144
< min(a, b)
< unsigned a, b;
---
> unsigned
> min(unsigned a, unsigned b)
173,175c167,168
< iomove(cp, n, flag)
< register caddr_t cp;
< register n;
---
> void
> iomove(register caddr_t cp, register int n, int flag)
177c170
< 	register t;
---
> 	register int t;
181c174,177
< 	if(u.u_segflg != 1 &&
---
> 	/* v7 had a u_segflg==2 (user I-space) branch here that called
> 	 * copyiin/copyiout; this port never sets u_segflg to 2, so the
> 	 * fast path is just user (==0) vs system (==1). */
> 	if(u.u_segflg == 0 &&
186,189c182
< 			if (u.u_segflg==0)
< 				t = copyin(u.u_base, (caddr_t)cp, n);
< 			else
< 				t = copyiin(u.u_base, (caddr_t)cp, n);
---
> 			t = copyin(u.u_base, (caddr_t)cp, n);
191,194c184
< 			if (u.u_segflg==0)
< 				t = copyout((caddr_t)cp, u.u_base, n);
< 			else
< 				t = copyiout((caddr_t)cp, u.u_base, n);
---
> 			t = copyout((caddr_t)cp, u.u_base, n);
```

### sys/sig.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/sig.c unix-v7-c99/sys/sig.c || true
```

Expect:

```
6,9c6,11
< #include "../h/inode.h"
< #include "../h/reg.h"
< #include "../h/text.h"
< #include "../h/seg.h"
---
> #include "../h/proto.h"
> 
> /* setrun comes from h/systm.h.  wakeup/sleep come from h/proto.h. */
> 
> int fsig(struct proc *p);
> void psignal(struct proc *p, int sig);
32,49c34,37
< /*
<  * Send the specified signal to
<  * all processes with 'pgrp' as
<  * process group.
<  * Called by tty.c for quits and
<  * interrupts.
<  */
< signal(pgrp, sig)
< register pgrp;
< {
< 	register struct proc *p;
< 
< 	if(pgrp == 0)
< 		return;
< 	for(p = &proc[0]; p < &proc[NPROC]; p++)
< 		if(p->p_pgrp == pgrp)
< 			psignal(p, sig);
< }
---
> /* v7's signal(pgrp, sig) (broadcast sig to every proc in pgrp) is gone
>  * -- its only caller was sys/tty.c (the v7 line-discipline interrupt
>  * path), which this port doesn't compile.  sys/v7_bridge.c has its own
>  * v7_signal_pgrp that walks armproc[] instead of proc[]. */
55,57c43,44
< psignal(p, sig)
< register struct proc *p;
< register sig;
---
> void
> psignal(register struct proc *p, register int sig)
81c68,69
< issig()
---
> int
> issig(void)
83c71
< 	register n;
---
> 	register int n;
96,166c84,92
< /*
<  * Enter the tracing STOP state.
<  * In this state, the parent is
<  * informed and the process is able to
<  * receive commands from the parent.
<  */
< stop()
< {
< 	register struct proc *pp, *cp;
< 
< loop:
< 	cp = u.u_procp;
< 	if(cp->p_ppid != 1)
< 	for (pp = &proc[0]; pp < &proc[NPROC]; pp++)
< 		if (pp->p_pid == cp->p_ppid) {
< 			wakeup((caddr_t)pp);
< 			cp->p_stat = SSTOP;
< 			swtch();
< 			if ((cp->p_flag&STRC)==0 || procxmt())
< 				return;
< 			goto loop;
< 		}
< 	exit(fsig(u.u_procp));
< }
< 
< /*
<  * Perform the action specified by
<  * the current signal.
<  * The usual sequence is:
<  *	if(issig())
<  *		psig();
<  */
< psig()
< {
< 	register n, p;
< 	register struct proc *rp;
< 
< 	rp = u.u_procp;
< 	if (u.u_fpsaved==0) {
< 		savfp(&u.u_fps);
< 		u.u_fpsaved = 1;
< 	}
< 	if (rp->p_flag&STRC)
< 		stop();
< 	n = fsig(rp);
< 	if (n==0)
< 		return;
< 	rp->p_sig &= ~(1<<(n-1));
< 	if((p=u.u_signal[n]) != 0) {
< 		u.u_error = 0;
< 		if(n != SIGINS && n != SIGTRC)
< 			u.u_signal[n] = 0;
< 		sendsig((caddr_t)p, n);
< 		return;
< 	}
< 	switch(n) {
< 
< 	case SIGQUIT:
< 	case SIGINS:
< 	case SIGTRC:
< 	case SIGIOT:
< 	case SIGEMT:
< 	case SIGFPT:
< 	case SIGBUS:
< 	case SIGSEG:
< 	case SIGSYS:
< 		if(core())
< 			n += 0200;
< 	}
< 	exit(n);
< }
---
> /* v7's stop() (enter SSTOP, signal parent, wait for procxmt cmd) and
>  * its co-routine procxmt() (parent ptrace command dispatcher) were
>  * driven by psig(); removed alongside it on this port. */
> 
> /* The v7 issig()/psig() pair handled signal delivery during trap return.
>  * On this port deliver_signal() in arch/arm.c does it inline so
>  * psig() is never called from C; the resume(u_qsav) path in slp.c's
>  * sleep() loop still uses its own local `psig:` label for the
>  * longjmp-back-on-signal idiom. */
172,173c98,99
< fsig(p)
< struct proc *p;
---
> int
> fsig(struct proc *p)
175c101
< 	register n, i;
---
> 	register int n, i;
186,262c112,113
< /*
<  * Create a core image on the file "core"
<  * If you are looking for protection glitches,
<  * there are probably a wealth of them here
<  * when this occurs to a suid command.
<  *
<  * It writes USIZE block of the
<  * user.h area followed by the entire
<  * data+stack segments.
<  */
< core()
< {
< 	register struct inode *ip;
< 	register unsigned s;
< 	extern schar();
< 
< 	u.u_error = 0;
< 	u.u_dirp = "core";
< 	ip = namei(schar, 1);
< 	if(ip == NULL) {
< 		if(u.u_error)
< 			return(0);
< 		ip = maknode(0666);
< 		if (ip==NULL)
< 			return(0);
< 	}
< 	if(!access(ip, IWRITE) &&
< 	   (ip->i_mode&IFMT) == IFREG &&
< 	   u.u_uid == u.u_ruid) {
< 		itrunc(ip);
< 		u.u_offset = 0;
< 		u.u_base = (caddr_t)&u;
< 		u.u_count = ctob(USIZE);
< 		u.u_segflg = 1;
< 		writei(ip);
< 		s = u.u_procp->p_size - USIZE;
< 		estabur((unsigned)0, s, (unsigned)0, 0, RO);
< 		u.u_base = 0;
< 		u.u_count = ctob(s);
< 		u.u_segflg = 0;
< 		writei(ip);
< 	}
< 	iput(ip);
< 	return(u.u_error==0);
< }
< 
< /*
<  * grow the stack to include the SP
<  * true return if successful.
<  */
< 
< grow(sp)
< unsigned sp;
< {
< 	register si, i;
< 	register struct proc *p;
< 	register a;
< 
< 	if(sp >= -ctob(u.u_ssize))
< 		return(0);
< 	si = (-sp)/64 - u.u_ssize + SINCR;
< 	if(si <= 0)
< 		return(0);
< 	if(estabur(u.u_tsize, u.u_dsize, u.u_ssize+si, u.u_sep, RO))
< 		return(0);
< 	p = u.u_procp;
< 	expand(p->p_size+si);
< 	a = p->p_addr + p->p_size;
< 	for(i=u.u_ssize; i; i--) {
< 		a--;
< 		copyseg(a-si, a);
< 	}
< 	for(i=si; i; i--)
< 		clearseg(--a);
< 	u.u_ssize += si;
< 	return(1);
< }
---
> /* v7's core() wrote a process's u-area + data + stack to ./core on a
>  * fatal signal.  Called from psig(); removed alongside it. */
265a117,122
>  *
>  * v7's PDP-11 libc/sys/ptrace.s shuffled C args -- it copied req, pid,
>  * addr into trailing-word indirect slots and put data in r0 -- so the
>  * kernel's struct a came out (data, pid, addr, req).  On this ARM port
>  * the SYS macro passes args straight in r0..r3, so u.u_arg[0..3] is
>  * (req, pid, addr, data) -- the natural C order.  Match that here.
267c124,125
< ptrace()
---
> void
> ptrace(void)
271c129
< 		int	data;
---
> 		int	req;
274c132
< 		int	req;
---
> 		int	data;
282c140
< 	for (p=proc; p < &proc[NPROC]; p++) 
---
> 	for (p=proc; p < &proc[NPROC]; p++)
308,417c166
< /*
<  * Code that the child process
<  * executes to implement the command
<  * of the parent process in tracing.
<  */
< procxmt()
< {
< 	register int i;
< 	register *p;
< 	register struct text *xp;
< 
< 	if (ipc.ip_lock != u.u_procp->p_pid)
< 		return(0);
< 	i = ipc.ip_req;
< 	ipc.ip_req = 0;
< 	wakeup((caddr_t)&ipc);
< 	switch (i) {
< 
< 	/* read user I */
< 	case 1:
< 		if (fuibyte((caddr_t)ipc.ip_addr) == -1)
< 			goto error;
< 		ipc.ip_data = fuiword((caddr_t)ipc.ip_addr);
< 		break;
< 
< 	/* read user D */
< 	case 2:
< 		if (fubyte((caddr_t)ipc.ip_addr) == -1)
< 			goto error;
< 		ipc.ip_data = fuword((caddr_t)ipc.ip_addr);
< 		break;
< 
< 	/* read u */
< 	case 3:
< 		i = (int)ipc.ip_addr;
< 		if (i<0 || i >= ctob(USIZE))
< 			goto error;
< 		ipc.ip_data = ((physadr)&u)->r[i>>1];
< 		break;
< 
< 	/* write user I */
< 	/* Must set up to allow writing */
< 	case 4:
< 		/*
< 		 * If text, must assure exclusive use
< 		 */
< 		if (xp = u.u_procp->p_textp) {
< 			if (xp->x_count!=1 || xp->x_iptr->i_mode&ISVTX)
< 				goto error;
< 			xp->x_iptr->i_flag &= ~ITEXT;
< 		}
< 		estabur(u.u_tsize, u.u_dsize, u.u_ssize, u.u_sep, RW);
< 		i = suiword((caddr_t)ipc.ip_addr, 0);
< 		suiword((caddr_t)ipc.ip_addr, ipc.ip_data);
< 		estabur(u.u_tsize, u.u_dsize, u.u_ssize, u.u_sep, RO);
< 		if (i<0)
< 			goto error;
< 		if (xp)
< 			xp->x_flag |= XWRIT;
< 		break;
< 
< 	/* write user D */
< 	case 5:
< 		if (suword((caddr_t)ipc.ip_addr, 0) < 0)
< 			goto error;
< 		suword((caddr_t)ipc.ip_addr, ipc.ip_data);
< 		break;
< 
< 	/* write u */
< 	case 6:
< 		i = (int)ipc.ip_addr;
< 		p = (int *)&((physadr)&u)->r[i>>1];
< 		if (p >= (int *)&u.u_fps && p < (int *)&u.u_fps.u_fpregs[6])
< 			goto ok;
< 		for (i=0; i<8; i++)
< 			if (p == &u.u_ar0[regloc[i]])
< 				goto ok;
< 		if (p == &u.u_ar0[RPS]) {
< 			ipc.ip_data |= 0170000;	/* assure user space */
< 			ipc.ip_data &= ~0340;	/* priority 0 */
< 			goto ok;
< 		}
< 		goto error;
< 
< 	ok:
< 		*p = ipc.ip_data;
< 		break;
< 
< 	/* set signal and continue */
< 	/*  one version causes a trace-trap */
< 	case 9:
< 		u.u_ar0[RPS] |= TBIT;
< 	case 7:
< 		if ((int)ipc.ip_addr != 1)
< 			u.u_ar0[PC] = (int)ipc.ip_addr;
< 		u.u_procp->p_sig = 0;
< 		if (ipc.ip_data)
< 			psignal(u.u_procp, ipc.ip_data);
< 		return(1);
< 
< 	/* force exit */
< 	case 8:
< 		exit(fsig(u.u_procp));
< 
< 	default:
< 	error:
< 		ipc.ip_req = -1;
< 	}
< 	return(0);
< }
---
> /* procxmt() removed -- see comment above. */
```

### sys/subr.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/subr.c unix-v7-c99/sys/subr.c || true
```

Expect:

```
3d2
< #include "../h/conf.h"
7a7,10
> #include "../h/proto.h"
> 
> /* bread/bdwrite/brelse come from h/proto.h.
>  * alloc/subyte/fubyte come from h/systm.h. */
18,20c21
< bmap(ip, bn, rwflg)
< register struct inode *ip;
< daddr_t bn;
---
> bmap(register struct inode *ip, daddr_t bn, int rwflg)
22c23
< 	register i;
---
> 	register int i;
117c118
< 	if(i < NINDIR-1)
---
> 	if((unsigned)i < NINDIR-1)
128,129c129,130
< passc(c)
< register c;
---
> int
> passc(register int c)
131,133c132,134
< 	register id;
< 
< 	if((id = u.u_segflg) == 1)
---
> 	/* v7 had a u_segflg==2 (user I-space) branch dispatching to
> 	 * suibyte; this port never sets u_segflg to 2. */
> 	if(u.u_segflg == 1)
135,139c136,139
< 	else
< 		if(id?suibyte(u.u_base, c):subyte(u.u_base, c) < 0) {
< 			u.u_error = EFAULT;
< 			return(-1);
< 		}
---
> 	else if(subyte(u.u_base, c) < 0) {
> 		u.u_error = EFAULT;
> 		return(-1);
> 	}
153c153,154
< cpass()
---
> int
> cpass(void)
155c156
< 	register c, id;
---
> 	register int c;
159c160
< 	if((id = u.u_segflg) == 1)
---
> 	if(u.u_segflg == 1)
161,165c162,165
< 	else
< 		if((c = id==0?fubyte(u.u_base):fuibyte(u.u_base)) < 0) {
< 			u.u_error = EFAULT;
< 			return(-1);
< 		}
---
> 	else if((c = fubyte(u.u_base)) < 0) {
> 		u.u_error = EFAULT;
> 		return(-1);
> 	}
172,204c172,174
< /*
<  * Routine which sets a user error; placed in
<  * illegal entries in the bdevsw and cdevsw tables.
<  */
< nodev()
< {
< 
< 	u.u_error = ENODEV;
< }
< 
< /*
<  * Null routine; placed in insignificant entries
<  * in the bdevsw and cdevsw tables.
<  */
< nulldev()
< {
< }
< 
< /*
<  * copy count bytes from from to to.
<  */
< bcopy(from, to, count)
< caddr_t from, to;
< register count;
< {
< 	register char *f, *t;
< 
< 	f = from;
< 	t = to;
< 	do
< 		*t++ = *f++;
< 	while(--count);
< }
---
> /* v7 bcopy lives in sys/v7stubs.c -- byte-loop tuned for AAPCS softfloat
>  * rather than the PDP-11 mov2/movb instruction layout the original
>  * carried over from v7/usr/sys/sys/subr.c. */
```

### sys/sys1.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/sys1.c unix-v7-c99/sys/sys1.c || true
```

Expect:

```
2,3d1
< #include "../h/systm.h"
< #include "../h/map.h"
7,9d4
< #include "../h/buf.h"
< #include "../h/reg.h"
< #include "../h/inode.h"
11c6
< #include "../h/acct.h"
---
> #include "../h/proto.h"
13,467c8,16
< /*
<  * exec system call, with and without environments.
<  */
< struct execa {
< 	char	*fname;
< 	char	**argp;
< 	char	**envp;
< };
< 
< exec()
< {
< 	((struct execa *)u.u_ap)->envp = NULL;
< 	exece();
< }
< 
< exece()
< {
< 	register nc;
< 	register char *cp;
< 	register struct buf *bp;
< 	register struct execa *uap;
< 	int na, ne, bno, ucp, ap, c;
< 	struct inode *ip;
< 
< 	if ((ip = namei(uchar, 0)) == NULL)
< 		return;
< 	bno = 0;
< 	bp = 0;
< 	if(access(ip, IEXEC))
< 		goto bad;
< 	if((ip->i_mode & IFMT) != IFREG ||
< 	   (ip->i_mode & (IEXEC|(IEXEC>>3)|(IEXEC>>6))) == 0) {
< 		u.u_error = EACCES;
< 		goto bad;
< 	}
< 	/*
< 	 * Collect arguments on "file" in swap space.
< 	 */
< 	na = 0;
< 	ne = 0;
< 	nc = 0;
< 	uap = (struct execa *)u.u_ap;
< 	if ((bno = malloc(swapmap,(NCARGS+BSIZE-1)/BSIZE)) == 0)
< 		panic("Out of swap");
< 	if (uap->argp) for (;;) {
< 		ap = NULL;
< 		if (uap->argp) {
< 			ap = fuword((caddr_t)uap->argp);
< 			uap->argp++;
< 		}
< 		if (ap==NULL && uap->envp) {
< 			uap->argp = NULL;
< 			if ((ap = fuword((caddr_t)uap->envp)) == NULL)
< 				break;
< 			uap->envp++;
< 			ne++;
< 		}
< 		if (ap==NULL)
< 			break;
< 		na++;
< 		if(ap == -1)
< 			u.u_error = EFAULT;
< 		do {
< 			if (nc >= NCARGS-1)
< 				u.u_error = E2BIG;
< 			if ((c = fubyte((caddr_t)ap++)) < 0)
< 				u.u_error = EFAULT;
< 			if (u.u_error)
< 				goto bad;
< 			if ((nc&BMASK) == 0) {
< 				if (bp)
< 					bawrite(bp);
< 				bp = getblk(swapdev, swplo+bno+(nc>>BSHIFT));
< 				cp = bp->b_un.b_addr;
< 			}
< 			nc++;
< 			*cp++ = c;
< 		} while (c>0);
< 	}
< 	if (bp)
< 		bawrite(bp);
< 	bp = 0;
< 	nc = (nc + NBPW-1) & ~(NBPW-1);
< 	if (getxfile(ip, nc) || u.u_error)
< 		goto bad;
< 
< 	/*
< 	 * copy back arglist
< 	 */
< 
< 	ucp = -nc - NBPW;
< 	ap = ucp - na*NBPW - 3*NBPW;
< 	u.u_ar0[R6] = ap;
< 	suword((caddr_t)ap, na-ne);
< 	nc = 0;
< 	for (;;) {
< 		ap += NBPW;
< 		if (na==ne) {
< 			suword((caddr_t)ap, 0);
< 			ap += NBPW;
< 		}
< 		if (--na < 0)
< 			break;
< 		suword((caddr_t)ap, ucp);
< 		do {
< 			if ((nc&BMASK) == 0) {
< 				if (bp)
< 					brelse(bp);
< 				bp = bread(swapdev, swplo+bno+(nc>>BSHIFT));
< 				cp = bp->b_un.b_addr;
< 			}
< 			subyte((caddr_t)ucp++, (c = *cp++));
< 			nc++;
< 		} while(c&0377);
< 	}
< 	suword((caddr_t)ap, 0);
< 	suword((caddr_t)ucp, 0);
< 	setregs();
< bad:
< 	if (bp)
< 		brelse(bp);
< 	if(bno)
< 		mfree(swapmap, (NCARGS+BSIZE-1)/BSIZE, bno);
< 	iput(ip);
< }
< 
< /*
<  * Read in and set up memory for executed file.
<  * Zero return is normal;
<  * non-zero means only the text is being replaced
<  */
< getxfile(ip, nargc)
< register struct inode *ip;
< {
< 	register unsigned ds;
< 	register sep;
< 	register unsigned ts, ss;
< 	register i, overlay;
< 	long lsize;
< 
< 	/*
< 	 * read in first few bytes
< 	 * of file for segment
< 	 * sizes:
< 	 * ux_mag = 407/410/411/405
< 	 *  407 is plain executable
< 	 *  410 is RO text
< 	 *  411 is separated ID
< 	 *  405 is overlaid text
< 	 */
< 
< 	u.u_base = (caddr_t)&u.u_exdata;
< 	u.u_count = sizeof(u.u_exdata);
< 	u.u_offset = 0;
< 	u.u_segflg = 1;
< 	readi(ip);
< 	u.u_segflg = 0;
< 	if(u.u_error)
< 		goto bad;
< 	if (u.u_count!=0) {
< 		u.u_error = ENOEXEC;
< 		goto bad;
< 	}
< 	sep = 0;
< 	overlay = 0;
< 	if(u.u_exdata.ux_mag == 0407) {
< 		lsize = (long)u.u_exdata.ux_dsize + u.u_exdata.ux_tsize;
< 		u.u_exdata.ux_dsize = lsize;
< 		if (lsize != u.u_exdata.ux_dsize) {	/* check overflow */
< 			u.u_error = ENOMEM;
< 			goto bad;
< 		}
< 		u.u_exdata.ux_tsize = 0;
< 	} else if (u.u_exdata.ux_mag == 0411)
< 		sep++;
< 	else if (u.u_exdata.ux_mag == 0405)
< 		overlay++;
< 	else if (u.u_exdata.ux_mag != 0410) {
< 		u.u_error = ENOEXEC;
< 		goto bad;
< 	}
< 	if(u.u_exdata.ux_tsize!=0 && (ip->i_flag&ITEXT)==0 && ip->i_count!=1) {
< 		u.u_error = ETXTBSY;
< 		goto bad;
< 	}
< 
< 	/*
< 	 * find text and data sizes
< 	 * try them out for possible
< 	 * overflow of max sizes
< 	 */
< 	ts = btoc(u.u_exdata.ux_tsize);
< 	lsize = (long)u.u_exdata.ux_dsize + u.u_exdata.ux_bsize;
< 	if (lsize != (unsigned)lsize) {
< 		u.u_error = ENOMEM;
< 		goto bad;
< 	}
< 	ds = btoc(lsize);
< 	ss = SSIZE + btoc(nargc);
< 	if (overlay) {
< 		if (u.u_sep==0 && ctos(ts) != ctos(u.u_tsize) || nargc) {
< 			u.u_error = ENOMEM;
< 			goto bad;
< 		}
< 		ds = u.u_dsize;
< 		ss = u.u_ssize;
< 		sep = u.u_sep;
< 		xfree();
< 		xalloc(ip);
< 		u.u_ar0[PC] = u.u_exdata.ux_entloc & ~01;
< 	} else {
< 		if(estabur(ts, ds, ss, sep, RO))
< 			goto bad;
< 	
< 		/*
< 		 * allocate and clear core
< 		 * at this point, committed
< 		 * to the new image
< 		 */
< 	
< 		u.u_prof.pr_scale = 0;
< 		xfree();
< 		i = USIZE+ds+ss;
< 		expand(i);
< 		while(--i >= USIZE)
< 			clearseg(u.u_procp->p_addr+i);
< 		xalloc(ip);
< 	
< 		/*
< 		 * read in data segment
< 		 */
< 	
< 		estabur((unsigned)0, ds, (unsigned)0, 0, RO);
< 		u.u_base = 0;
< 		u.u_offset = sizeof(u.u_exdata)+u.u_exdata.ux_tsize;
< 		u.u_count = u.u_exdata.ux_dsize;
< 		readi(ip);
< 		/*
< 		 * set SUID/SGID protections, if no tracing
< 		 */
< 		if ((u.u_procp->p_flag&STRC)==0) {
< 			if(ip->i_mode&ISUID)
< 				if(u.u_uid != 0) {
< 					u.u_uid = ip->i_uid;
< 					u.u_procp->p_uid = ip->i_uid;
< 				}
< 			if(ip->i_mode&ISGID)
< 				u.u_gid = ip->i_gid;
< 		} else
< 			psignal(u.u_procp, SIGTRC);
< 	}
< 	u.u_tsize = ts;
< 	u.u_dsize = ds;
< 	u.u_ssize = ss;
< 	u.u_sep = sep;
< 	estabur(ts, ds, ss, sep, RO);
< bad:
< 	return(overlay);
< }
< 
< /*
<  * Clear registers on exec
<  */
< setregs()
< {
< 	register int *rp;
< 	register char *cp;
< 	register i;
< 
< 	for(rp = &u.u_signal[0]; rp < &u.u_signal[NSIG]; rp++)
< 		if((*rp & 1) == 0)
< 			*rp = 0;
< 	for(cp = &regloc[0]; cp < &regloc[6];)
< 		u.u_ar0[*cp++] = 0;
< 	u.u_ar0[PC] = u.u_exdata.ux_entloc & ~01;
< 	for(rp = (int *)&u.u_fps; rp < (int *)&u.u_fps.u_fpregs[6];)
< 		*rp++ = 0;
< 	for(i=0; i<NOFILE; i++) {
< 		if (u.u_pofile[i]&EXCLOSE) {
< 			closef(u.u_ofile[i]);
< 			u.u_ofile[i] = NULL;
< 			u.u_pofile[i] &= ~EXCLOSE;
< 		}
< 	}
< 	/*
< 	 * Remember file name for accounting.
< 	 */
< 	u.u_acflag &= ~AFORK;
< 	bcopy((caddr_t)u.u_dbuf, (caddr_t)u.u_comm, DIRSIZ);
< }
< 
< /*
<  * exit system call:
<  * pass back caller's arg
<  */
< rexit()
< {
< 	register struct a {
< 		int	rval;
< 	} *uap;
< 
< 	uap = (struct a *)u.u_ap;
< 	exit((uap->rval & 0377) << 8);
< }
< 
< /*
<  * Release resources.
<  * Save u. area for parent to look at.
<  * Enter zombie state.
<  * Wake up parent and init processes,
<  * and dispose of children.
<  */
< exit(rv)
< {
< 	register int i;
< 	register struct proc *p, *q;
< 	register struct file *f;
< 
< 	p = u.u_procp;
< 	p->p_flag &= ~(STRC|SULOCK);
< 	p->p_clktim = 0;
< 	for(i=0; i<NSIG; i++)
< 		u.u_signal[i] = 1;
< 	for(i=0; i<NOFILE; i++) {
< 		f = u.u_ofile[i];
< 		u.u_ofile[i] = NULL;
< 		closef(f);
< 	}
< 	plock(u.u_cdir);
< 	iput(u.u_cdir);
< 	if (u.u_rdir) {
< 		plock(u.u_rdir);
< 		iput(u.u_rdir);
< 	}
< 	xfree();
< 	acct();
< 	mfree(coremap, p->p_size, p->p_addr);
< 	p->p_stat = SZOMB;
< 	((struct xproc *)p)->xp_xstat = rv;
< 	((struct xproc *)p)->xp_utime = u.u_cutime + u.u_utime;
< 	((struct xproc *)p)->xp_stime = u.u_cstime + u.u_stime;
< 	for(q = &proc[0]; q < &proc[NPROC]; q++)
< 		if(q->p_ppid == p->p_pid) {
< 			wakeup((caddr_t)&proc[1]);
< 			q->p_ppid = 1;
< 			if (q->p_stat==SSTOP)
< 				setrun(q);
< 		}
< 	for(q = &proc[0]; q < &proc[NPROC]; q++)
< 		if(p->p_ppid == q->p_pid) {
< 			wakeup((caddr_t)q);
< 			swtch();
< 			/* no return */
< 		}
< 	swtch();
< }
< 
< /*
<  * Wait system call.
<  * Search for a terminated (zombie) child,
<  * finally lay it to rest, and collect its status.
<  * Look also for stopped (traced) children,
<  * and pass back status from them.
<  */
< wait()
< {
< 	register f;
< 	register struct proc *p;
< 
< 	f = 0;
< 
< loop:
< 	for(p = &proc[0]; p < &proc[NPROC]; p++)
< 	if(p->p_ppid == u.u_procp->p_pid) {
< 		f++;
< 		if(p->p_stat == SZOMB) {
< 			u.u_r.r_val1 = p->p_pid;
< 			u.u_r.r_val2 = ((struct xproc *)p)->xp_xstat;
< 			u.u_cutime += ((struct xproc *)p)->xp_utime;
< 			u.u_cstime += ((struct xproc *)p)->xp_stime;
< 			p->p_pid = 0;
< 			p->p_ppid = 0;
< 			p->p_pgrp = 0;
< 			p->p_sig = 0;
< 			p->p_flag = 0;
< 			p->p_wchan = 0;
< 			p->p_stat = NULL;
< 			return;
< 		}
< 		if(p->p_stat == SSTOP) {
< 			if((p->p_flag&SWTED) == 0) {
< 				p->p_flag |= SWTED;
< 				u.u_r.r_val1 = p->p_pid;
< 				u.u_r.r_val2 = (fsig(p)<<8) | 0177;
< 				return;
< 			}
< 			continue;
< 		}
< 	}
< 	if(f) {
< 		sleep((caddr_t)u.u_procp, PWAIT);
< 		goto loop;
< 	}
< 	u.u_error = ECHILD;
< }
< 
< /*
<  * fork system call.
<  */
< fork()
< {
< 	register struct proc *p1, *p2;
< 	register a;
< 
< 	/*
< 	 * Make sure there's enough swap space for max
< 	 * core image, thus reducing chances of running out
< 	 */
< 	if ((a = malloc(swapmap, ctod(MAXMEM))) == 0) {
< 		u.u_error = ENOMEM;
< 		goto out;
< 	}
< 	mfree(swapmap, ctod(MAXMEM), a);
< 	a = 0;
< 	p2 = NULL;
< 	for(p1 = &proc[0]; p1 < &proc[NPROC]; p1++) {
< 		if (p1->p_stat==NULL && p2==NULL)
< 			p2 = p1;
< 		else {
< 			if (p1->p_uid==u.u_uid && p1->p_stat!=NULL)
< 				a++;
< 		}
< 	}
< 	/*
< 	 * Disallow if
< 	 *  No processes at all;
< 	 *  not su and too many procs owned; or
< 	 *  not su and would take last slot.
< 	 */
< 	if (p2==NULL || (u.u_uid!=0 && (p2==&proc[NPROC-1] || a>MAXUPRC))) {
< 		u.u_error = EAGAIN;
< 		goto out;
< 	}
< 	p1 = u.u_procp;
< 	if(newproc()) {
< 		u.u_r.r_val1 = p1->p_pid;
< 		u.u_start = time;
< 		u.u_cstime = 0;
< 		u.u_stime = 0;
< 		u.u_cutime = 0;
< 		u.u_utime = 0;
< 		u.u_acflag = AFORK;
< 		return;
< 	}
< 	u.u_r.r_val1 = p2->p_pid;
---
> extern int  estabur(unsigned, unsigned, unsigned, int, int);
> /* copyseg/clearseg come from h/proto.h. */
> extern void expand(int);
> 
> /* v7 sys/sys1.c held exec/exece/getxfile/setregs/rexit/exit/wait/fork.
>  * On this port they're all reimplemented inline in arch/arm.c::trap()
>  * and v7_exec_call(); the v7 versions are linker-dead.  Only sbreak()
>  * (the break(2) syscall, sysent[17]) is kept -- it still drives the v7
>  * data-segment grow/shrink via expand()/copyseg(). */
469,471d17
< out:
< 	u.u_ar0[R7] += NBPW;
< }
477c23,24
< sbreak()
---
> void
> sbreak(void)
482c29
< 	register a, n, d;
---
> 	register int a, n, d;
```

### sys/sys2.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/sys2.c unix-v7-c99/sys/sys2.c || true
```

Expect:

```
5d4
< #include "../h/reg.h"
8a8,21
> /* getf/namei/uchar/maknode/closef/access/readi/writei/plock/prele/iput/suser
>  * come from h/systm.h. */
> extern void readp(struct file *);
> extern void writep(struct file *);
> extern void wdir(struct inode *);
> 
> void rdwr(int mode);
> 
> /* v7's write(), open(), creat() and open1() are gone -- on this port
>  * sys_{write,open,creat}_v7 in arch/arm.c implement those syscalls
>  * directly (pipe/console fast paths + kopen/kcreat for the file tree),
>  * so the v7 entry points were linker-dead.  read() is still routed
>  * here via v7_read_call. */
> 
12c25,26
< read()
---
> void
> read(void)
18,25d31
<  * write system call
<  */
< write()
< {
< 	rdwr(FWRITE);
< }
< 
< /*
30,31c36,37
< rdwr(mode)
< register mode;
---
> void
> rdwr(register int mode)
59,62c65
< 		if (fp->f_flag&FMP)
< 			u.u_offset = 0;
< 		else
< 			u.u_offset = fp->f_un.f_offset;
---
> 		u.u_offset = fp->f_un.f_offset;
71,72c74
< 		if ((fp->f_flag&FMP) == 0)
< 			fp->f_un.f_offset += uap->count-u.u_count;
---
> 		fp->f_un.f_offset += uap->count-u.u_count;
78,160d79
<  * open system call
<  */
< open()
< {
< 	register struct inode *ip;
< 	register struct a {
< 		char	*fname;
< 		int	rwmode;
< 	} *uap;
< 
< 	uap = (struct a *)u.u_ap;
< 	ip = namei(uchar, 0);
< 	if(ip == NULL)
< 		return;
< 	open1(ip, ++uap->rwmode, 0);
< }
< 
< /*
<  * creat system call
<  */
< creat()
< {
< 	register struct inode *ip;
< 	register struct a {
< 		char	*fname;
< 		int	fmode;
< 	} *uap;
< 
< 	uap = (struct a *)u.u_ap;
< 	ip = namei(uchar, 1);
< 	if(ip == NULL) {
< 		if(u.u_error)
< 			return;
< 		ip = maknode(uap->fmode&07777&(~ISVTX));
< 		if (ip==NULL)
< 			return;
< 		open1(ip, FWRITE, 2);
< 	} else
< 		open1(ip, FWRITE, 1);
< }
< 
< /*
<  * common code for open and creat.
<  * Check permissions, allocate an open file structure,
<  * and call the device open routine if any.
<  */
< open1(ip, mode, trf)
< register struct inode *ip;
< register mode;
< {
< 	register struct file *fp;
< 	int i;
< 
< 	if(trf != 2) {
< 		if(mode&FREAD)
< 			access(ip, IREAD);
< 		if(mode&FWRITE) {
< 			access(ip, IWRITE);
< 			if((ip->i_mode&IFMT) == IFDIR)
< 				u.u_error = EISDIR;
< 		}
< 	}
< 	if(u.u_error)
< 		goto out;
< 	if(trf == 1)
< 		itrunc(ip);
< 	prele(ip);
< 	if ((fp = falloc()) == NULL)
< 		goto out;
< 	fp->f_flag = mode&(FREAD|FWRITE);
< 	fp->f_inode = ip;
< 	i = u.u_r.r_val1;
< 	openi(ip, mode&FWRITE);
< 	if(u.u_error == 0)
< 		return;
< 	u.u_ofile[i] = NULL;
< 	fp->f_count--;
< 
< out:
< 	iput(ip);
< }
< 
< /*
163c82,83
< close()
---
> void
> close(void)
181c101,102
< seek()
---
> void
> seek(void)
194c115
< 	if(fp->f_flag&(FPIPE|FMP)) {
---
> 	if(fp->f_flag&FPIPE) {
209c130,131
< link()
---
> void
> link(void)
259c181,182
< mknod()
---
> void
> mknod(void)
290c213,214
< saccess()
---
> void
> saccess(void)
292c216
< 	register svuid, svgid;
---
> 	register int svuid, svgid;
```

### sys/sys3.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/sys3.c unix-v7-c99/sys/sys3.c || true
```

Expect:

```
5d4
< #include "../h/reg.h"
13a13,21
> #include "../h/proto.h"
> 
> /* getf/namei/uchar/closef/update/iupdat/ufalloc/iput/plock/prele
>  * /copyout/bcopy come from h/systm.h.
>  * bread/brelse/geteblk come from h/proto.h. */
> extern void xumount(dev_t);
> 
> void stat1(struct inode *ip, struct stat *ub, off_t pipeadj);
> dev_t getmdev(void);
18c26,27
< fstat()
---
> void
> fstat(void)
36c45,46
< stat()
---
> void
> stat(void)
56,59c66,67
< stat1(ip, ub, pipeadj)
< register struct inode *ip;
< struct stat *ub;
< off_t pipeadj;
---
> void
> stat1(register struct inode *ip, struct stat *ub, off_t pipeadj)
94c102,103
< dup()
---
> void
> dup(void)
101c110
< 	register i, m;
---
> 	register int i, m;
131c140,141
< smount()
---
> void
> smount(void)
197c207,208
< sumount()
---
> void
> sumount(void)
203,205d213
< 	register struct a {
< 		char	*fspec;
< 	};
240c248
< getmdev()
---
> getmdev(void)
```

### sys/sys4.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/sys4.c unix-v7-c99/sys/sys4.c || true
```

Expect:

```
5d4
< #include "../h/reg.h"
8a8,14
> #include "../h/proto.h"
> 
> /* suser/update/namei/uchar/iget/access/owner/iput/writei/prele/plock/iupdat
>  * /xrele/psignal/copyin/copyout come from h/systm.h.
>  * sleep/spl0/spl7 come from h/proto.h. */
> 
> void chdirec(struct inode **ipp);
17c23,24
< gtime()
---
> void
> gtime(void)
26c33,34
< ftime()
---
> void
> ftime(void)
53c61,62
< stime()
---
> void
> stime(void)
64c73,74
< setuid()
---
> void
> setuid(void)
66c76
< 	register uid;
---
> 	register int uid;
80c90,91
< getuid()
---
> void
> getuid(void)
87c98,99
< setgid()
---
> void
> setgid(void)
89c101
< 	register gid;
---
> 	register int gid;
102c114,115
< getgid()
---
> void
> getgid(void)
109c122,123
< getpid()
---
> void
> getpid(void)
115c129,130
< sync()
---
> void
> sync(void)
121c136,137
< nice()
---
> void
> nice(void)
123c139
< 	register n;
---
> 	register int n;
145c161,162
< unlink()
---
> void
> unlink(void)
148,150d164
< 	struct a {
< 		char	*fname;
< 	};
194c208,210
< chdir()
---
> 
> void
> chdir(void)
199c215,216
< chroot()
---
> void
> chroot(void)
205,206c222,223
< chdirec(ipp)
< register struct inode **ipp;
---
> void
> chdirec(register struct inode **ipp)
209,211d225
< 	struct a {
< 		char	*fname;
< 	};
234c248,249
< chmod()
---
> void
> chmod(void)
255c270,271
< chown()
---
> void
> chown(void)
273c289,290
< ssig()
---
> void
> ssig(void)
275c292
< 	register a;
---
> 	register int a;
292c309,310
< kill()
---
> void
> kill(void)
295c313
< 	register a;
---
> 	register int a;
327c345,346
< times()
---
> void
> times(void)
338c357,358
< profil()
---
> void
> profil(void)
357c377,378
< alarm()
---
> void
> alarm(void)
360c381
< 	register c;
---
> 	register int c;
372,381c393,395
< /*
<  * indefinite wait.
<  * no one should wakeup(&u)
<  */
< pause()
< {
< 
< 	for(;;)
< 		sleep((caddr_t)&u, PSLEP);
< }
---
> /* v7's pause(2) implementation is gone -- arch/arm.c has its own
>  * sys_pause_v7 that uses the mt_block_on_pipe + clock-tick wake path
>  * instead of the v7 sleep()/wakeup() handoff. */
386c400,401
< umask()
---
> void
> umask(void)
391c406
< 	register t;
---
> 	register int t;
403c418,419
< utime()
---
> void
> utime(void)
```

### sys/text.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/text.c unix-v7-c99/sys/text.c || true
```

Expect:

```
3d2
< #include "../h/map.h"
10a10,19
> #include "../h/proto.h"
> 
> /* malloc/mfree/panic/wakeup/sleep come from h/proto.h.
>  * iput comes from h/systm.h. */
> extern void xlock(struct text *);
> extern void xunlock(struct text *);
> extern void xccdec(struct text *);
> extern void xuntext(struct text *);
> 
> void xswap(register struct proc *p, int ff, int os);
22,23c31,32
< xswap(p, ff, os)
< register struct proc *p;
---
> void
> xswap(register struct proc *p, int ff, int os)
25c34
< 	register a;
---
> 	register int a;
32d40
< 	p->p_flag |= SLOCK;
38c46
< 	p->p_flag &= ~(SLOAD|SLOCK);
---
> 	p->p_flag &= ~SLOAD;
46,166c54,60
< /*
<  * relinquish use of the shared text segment
<  * of a process.
<  */
< xfree()
< {
< 	register struct text *xp;
< 	register struct inode *ip;
< 
< 	if((xp=u.u_procp->p_textp) == NULL)
< 		return;
< 	xlock(xp);
< 	xp->x_flag &= ~XLOCK;
< 	u.u_procp->p_textp = NULL;
< 	ip = xp->x_iptr;
< 	if(--xp->x_count==0 && (ip->i_mode&ISVTX)==0) {
< 		xp->x_iptr = NULL;
< 		mfree(swapmap, ctod(xp->x_size), xp->x_daddr);
< 		mfree(coremap, xp->x_size, xp->x_caddr);
< 		ip->i_flag &= ~ITEXT;
< 		if (ip->i_flag&ILOCK)
< 			ip->i_count--;
< 		else
< 			iput(ip);
< 	} else
< 		xccdec(xp);
< }
< 
< /*
<  * Attach to a shared text segment.
<  * If there is no shared text, just return.
<  * If there is, hook up to it:
<  * if it is not currently being used, it has to be read
<  * in from the inode (ip); the written bit is set to force it
<  * to be written out as appropriate.
<  * If it is being used, but is not currently in core,
<  * a swap has to be done to get it back.
<  */
< xalloc(ip)
< register struct inode *ip;
< {
< 	register struct text *xp;
< 	register unsigned ts;
< 	register struct text *xp1;
< 
< 	if(u.u_exdata.ux_tsize == 0)
< 		return;
< 	xp1 = NULL;
< 	for (xp = &text[0]; xp < &text[NTEXT]; xp++) {
< 		if(xp->x_iptr == NULL) {
< 			if(xp1 == NULL)
< 				xp1 = xp;
< 			continue;
< 		}
< 		if(xp->x_iptr == ip) {
< 			xlock(xp);
< 			xp->x_count++;
< 			u.u_procp->p_textp = xp;
< 			if (xp->x_ccount == 0)
< 				xexpand(xp);
< 			else
< 				xp->x_ccount++;
< 			xunlock(xp);
< 			return;
< 		}
< 	}
< 	if((xp=xp1) == NULL) {
< 		printf("out of text");
< 		psignal(u.u_procp, SIGKIL);
< 		return;
< 	}
< 	xp->x_flag = XLOAD|XLOCK;
< 	xp->x_count = 1;
< 	xp->x_ccount = 0;
< 	xp->x_iptr = ip;
< 	ip->i_flag |= ITEXT;
< 	ip->i_count++;
< 	ts = btoc(u.u_exdata.ux_tsize);
< 	xp->x_size = ts;
< 	if((xp->x_daddr = malloc(swapmap, (int)ctod(ts))) == NULL)
< 		panic("out of swap space");
< 	u.u_procp->p_textp = xp;
< 	xexpand(xp);
< 	estabur(ts, (unsigned)0, (unsigned)0, 0, RW);
< 	u.u_count = u.u_exdata.ux_tsize;
< 	u.u_offset = sizeof(u.u_exdata);
< 	u.u_base = 0;
< 	u.u_segflg = 2;
< 	u.u_procp->p_flag |= SLOCK;
< 	readi(ip);
< 	u.u_procp->p_flag &= ~SLOCK;
< 	u.u_segflg = 0;
< 	xp->x_flag = XWRIT;
< }
< 
< /*
<  * Assure core for text segment
<  * Text must be locked to keep someone else from
<  * freeing it in the meantime.
<  * x_ccount must be 0.
<  */
< xexpand(xp)
< register struct text *xp;
< {
< 	if ((xp->x_caddr = malloc(coremap, xp->x_size)) != NULL) {
< 		if ((xp->x_flag&XLOAD)==0)
< 			swap(xp->x_daddr, xp->x_caddr, xp->x_size, B_READ);
< 		xp->x_ccount++;
< 		xunlock(xp);
< 		return;
< 	}
< 	if (save(u.u_ssav)) {
< 		sureg();
< 		return;
< 	}
< 	xswap(u.u_procp, 1, 0);
< 	xunlock(xp);
< 	u.u_procp->p_flag |= SSWAP;
< 	qswtch();
< 	/* no return */
< }
---
> /* v7 xfree() (drop process's text reference, free swap+core if last
>  * holder), xalloc() (attach to shared text, swap-in if needed) and
>  * xexpand() (allocate core for text, swap-out current proc if no core)
>  * are gone -- their only callers were sys1.c::exit/getxfile, both of
>  * which are also gone.  The remaining text-table operations (xswap,
>  * xccdec, xumount, xrele, xuntext) stay because they're still reached
>  * via slp.c::expand and umount(2)/closef(). */
171,172c65,66
< xlock(xp)
< register struct text *xp;
---
> void
> xlock(register struct text *xp)
182,183c76,77
< xunlock(xp)
< register struct text *xp;
---
> void
> xunlock(register struct text *xp)
195,196c89,90
< xccdec(xp)
< register struct text *xp;
---
> void
> xccdec(register struct text *xp)
216,217c110,111
< xumount(dev)
< register dev;
---
> void
> xumount(register dev_t dev)
221c115
< 	for (xp = &text[0]; xp < &text[NTEXT]; xp++) 
---
> 	for (xp = &text[0]; xp < &text[NTEXT]; xp++)
229,230c123,124
< xrele(ip)
< register struct inode *ip;
---
> void
> xrele(register struct inode *ip)
234c128
< 	if (ip->i_flag&ITEXT==0)
---
> 	if ((ip->i_flag&ITEXT)==0)
245,246c139,140
< xuntext(xp)
< register struct text *xp;
---
> void
> xuntext(register struct text *xp)
```

### sys/ureg.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/ureg.c unix-v7-c99/sys/ureg.c || true
```

Expect:

```
8a9,10
> int estabur(unsigned nt, unsigned nd, unsigned ns, int sep, int xrw);
> 
10,13c12,18
<  * Load the user hardware segmentation
<  * registers from the software prototype.
<  * The software registers must have
<  * been setup prior by estabur.
---
>  * v7's sureg() pushed the per-proc u_uisa/u_uisd prototype into the
>  * PDP-11's UISA/UISD segment registers at 0177640 / 0177600.  On ARM
>  * those literal addresses fall inside l1[0]'s identity-mapped user
>  * page (USERPHYS+0xFF80..0xFFFE), so the original loop would silently
>  * scribble over the bottom of every process's address space.  ARM
>  * userspace runs out of a single 1 MiB identity-mapped window with
>  * no per-segment registers to reload, so this is a no-op.
15c20,21
< sureg()
---
> void
> sureg(void)
17,34d22
< 	register *udp, *uap, *rdp;
< 	int *rap, *limudp;
< 	int taddr, daddr;
< 	struct text *tp;
< 
< 	taddr = daddr = u.u_procp->p_addr;
< 	if ((tp=u.u_procp->p_textp) != NULL)
< 		taddr = tp->x_caddr;
< 	limudp = &u.u_uisd[16];
< 	if (cputype==40)
< 		limudp = &u.u_uisd[8];
< 	rap = (int *)UISA;
< 	rdp = (int *)UISD;
< 	uap = &u.u_uisa[0];
< 	for (udp = &u.u_uisd[0]; udp < limudp;) {
< 		*rap++ = *uap++ + (*udp&TX? taddr: (*udp&ABS? 0: daddr));
< 		*rdp++ = *udp++;
< 	}
48,49c36,37
< estabur(nt, nd, ns, sep, xrw)
< unsigned nt, nd, ns;
---
> int
> estabur(unsigned nt, unsigned nd, unsigned ns, int sep, int xrw)
51c39
< 	register a, *ap, *dp;
---
> 	register int a, *ap, *dp;
61c49
< 	if(nt+nd+ns+USIZE > maxmem)
---
> 	if((int)(nt+nd+ns+USIZE) > maxmem)
```

### cmd/sh/blok.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/blok.c unix-v7-c99/cmd/sh/blok.c || true
```

Expect:

```
27,28c27
< ADDRESS	alloc(nbytes)
< 	POS		nbytes;
---
> ADDRESS	alloc(POS nbytes)
37c36
< 				IF ADR(q)-ADR(p) >= rbytes
---
> 				IF (POS)(ADR(q)-ADR(p)) >= rbytes
52,53c51
< VOID	addblok(reqd)
< 	POS		reqd;
---
> VOID	addblok(POS reqd)
60c58
< 		rndstak=round(staktop,BYTESPERWORD);
---
> 		rndstak=(STKPTR)round(staktop,BYTESPERWORD);
74a73
> 	return(0);
77,78c76
< VOID	free(ap)
< 	BLKPTR		ap;
---
> VOID	free(BLKPTR ap)
84a83
> 	return(0);
```

### cmd/sh/brkincr.h

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/brkincr.h unix-v7-c99/cmd/sh/brkincr.h || true
```

Expect:

```
1,2c1,6
< #define BRKINCR 01000
< #define BRKMAX 04000
---
> /* PORT: bumped from v7's 01000/04000 (512/2048 bytes).  The original
>  * values capped glob expansion at ~30 matches on stack-allocated
>  * addg() output before sh's working stack ran out.  64KB is trivial
>  * on 128 MiB qemu. */
> #define BRKINCR 010000
> #define BRKMAX 0200000
```

### cmd/sh/builtin.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/builtin.c unix-v7-c99/cmd/sh/builtin.c || true
```

Expect:

```
1c1
< builtin()
---
> int builtin(void)
```

### cmd/sh/cmd.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/cmd.c unix-v7-c99/cmd/sh/cmd.c || true
```

Expect:

```
13,23c13,32
< PROC IOPTR	inout();
< PROC VOID	chkword();
< PROC VOID	chksym();
< PROC TREPTR	term();
< PROC TREPTR	makelist();
< PROC TREPTR	list();
< PROC REGPTR	syncase();
< PROC TREPTR	item();
< PROC VOID	skipnl();
< PROC VOID	prsym();
< PROC VOID	synbad();
---
> PROC IOPTR	inout(IOPTR lastio);
> PROC VOID	chkword(void);
> PROC VOID	chksym(INT sym);
> PROC TREPTR	term(INT flg);
> PROC TREPTR	makelist(INT type, TREPTR i, TREPTR r);
> PROC TREPTR	list(INT flg);
> PROC REGPTR	syncase(REG INT esym);
> PROC TREPTR	item(BOOL flag);
> PROC INT	skipnl(void);
> PROC VOID	prsym(INT sym);
> PROC VOID	synbad(void);
> INT	word(void);
> INT	nextc(INT quote);
> VOID	chkpr(CHAR c);
> VOID	prc(INT c);
> VOID	prs(STRING as);
> VOID	prn(INT n);
> VOID	prp(void);
> VOID	newline(void);
> VOID	exitsh(INT xno);
31,33c40
< TREPTR	makefork(flgs, i)
< 	INT		flgs;
< 	TREPTR		i;
---
> TREPTR	makefork(INT flgs, TREPTR i)
37c44
< 	t=getstak(FORKTYPE);
---
> 	t=(TREPTR)getstak(FORKTYPE);
42,44c49
< LOCAL TREPTR	makelist(type,i,r)
< 	INT		type;
< 	TREPTR		i, r;
---
> LOCAL TREPTR	makelist(INT type, TREPTR i, TREPTR r)
46c51
< 	REG TREPTR	t;
---
> 	REG TREPTR	t = 0;
50c55
< 	ELSE	t = getstak(LSTTYPE);
---
> 	ELSE	t = (TREPTR)getstak(LSTTYPE);
65,67c70
< TREPTR	cmd(sym,flg)
< 	REG INT		sym;
< 	INT		flg;
---
> TREPTR	cmd(REG INT sym, INT flg)
87a91
> 		/* fallthrough */
90c94
< 		IF e=cmd(sym,flg|MTFLG)
---
> 		IF (e=cmd(sym,flg|MTFLG))
98a103
> 		/* fallthrough */
116c121
< LOCAL TREPTR	list(flg)
---
> LOCAL TREPTR	list(INT flg)
134c139
< LOCAL TREPTR	term(flg)
---
> LOCAL TREPTR	term(INT flg)
150,151c155
< LOCAL REGPTR	syncase(esym)
< 	REG INT	esym;
---
> LOCAL REGPTR	syncase(REG INT esym)
156c160
< 	ELSE	REG REGPTR	r=getstak(REGTYPE);
---
> 	ELSE	REG REGPTR	r=(REGPTR)getstak(REGTYPE);
189,190c193
< LOCAL TREPTR	item(flag)
< 	BOOL		flag;
---
> LOCAL TREPTR	item(BOOL flag)
204c207
< 		   t=getstak(SWTYPE);
---
> 		   t=(TREPTR)getstak(SWTYPE);
216c219
< 		   t=getstak(IFTYPE);
---
> 		   t=(TREPTR)getstak(IFTYPE);
227c230
< 		   t=getstak(FORTYPE);
---
> 		   t=(TREPTR)getstak(FORTYPE);
234c237
< 			t->forlst=item(0);
---
> 			t->forlst=(COMPTR)item(0);
248c251
< 		   t=getstak(WHTYPE);
---
> 		   t=(TREPTR)getstak(WHTYPE);
262c265
< 		   p=getstak(PARTYPE);
---
> 		   p=(PARPTR)getstak(PARTYPE);
272a276
> 		/* fallthrough */
280c284
< 		   t=getstak(COMTYPE);
---
> 		   t=(TREPTR)getstak(COMTYPE);
286c290
< 			THEN	argp->argnxt=argset; argset=argp;
---
> 			THEN	argp->argnxt=(ARGPTR)argset; argset=(ARGPTR *)argp;
295c299
< 		   t->comtyp=TCOM; t->comset=argset; *argtail=0;
---
> 		   t->comtyp=TCOM; t->comset=(ARGPTR)argset; *argtail=0;
301c305
< 	IF io=inout(io)
---
> 	IF (io=inout(io))
308c312
< LOCAL VOID	skipnl()
---
> LOCAL INT	skipnl(void)
314,315c318
< LOCAL IOPTR	inout(lastio)
< 	IOPTR		lastio;
---
> LOCAL IOPTR	inout(IOPTR lastio)
334a338
> 		/* fallthrough */
350c354
< 	iop=getstak(IOTYPE); iop->ioname=wdarg->argval; iop->iofile=iof;
---
> 	iop=(IOPTR)getstak(IOTYPE); iop->ioname=wdarg->argval; iop->iofile=iof;
358c362
< LOCAL VOID	chkword()
---
> LOCAL VOID	chkword(void)
362a367
> 	return(0);
365c370
< LOCAL VOID	chksym(sym)
---
> LOCAL VOID	chksym(INT sym)
370a376
> 	return(0);
373c379
< LOCAL VOID	prsym(sym)
---
> LOCAL VOID	prsym(INT sym)
388a395
> 	return(0);
391c398
< LOCAL VOID	synbad()
---
> LOCAL VOID	synbad(void)
405a413
> 	return(0);
```

### cmd/sh/ctype.h

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/ctype.h unix-v7-c99/cmd/sh/ctype.h || true
```

Expect:

```
69c69
< char	_ctype1[];
---
> extern char	_ctype1[];
72,78c72,78
< #define	space(c)	(((c)&QUOTE)==0 ANDF _ctype1[c]&(T_SPC))
< #define eofmeta(c)	(((c)&QUOTE)==0 ANDF _ctype1[c]&(_META|T_EOF))
< #define qotchar(c)	(((c)&QUOTE)==0 ANDF _ctype1[c]&(T_QOT))
< #define eolchar(c)	(((c)&QUOTE)==0 ANDF _ctype1[c]&(T_EOR|T_EOF))
< #define dipchar(c)	(((c)&QUOTE)==0 ANDF _ctype1[c]&(T_DIP))
< #define subchar(c)	(((c)&QUOTE)==0 ANDF _ctype1[c]&(T_SUB|T_QOT))
< #define escchar(c)	(((c)&QUOTE)==0 ANDF _ctype1[c]&(T_ESC))
---
> #define	space(c)	(((c)&QUOTE)==0 ANDF _ctype1[(unsigned char)(c)]&(T_SPC))
> #define eofmeta(c)	(((c)&QUOTE)==0 ANDF _ctype1[(unsigned char)(c)]&(_META|T_EOF))
> #define qotchar(c)	(((c)&QUOTE)==0 ANDF _ctype1[(unsigned char)(c)]&(T_QOT))
> #define eolchar(c)	(((c)&QUOTE)==0 ANDF _ctype1[(unsigned char)(c)]&(T_EOR|T_EOF))
> #define dipchar(c)	(((c)&QUOTE)==0 ANDF _ctype1[(unsigned char)(c)]&(T_DIP))
> #define subchar(c)	(((c)&QUOTE)==0 ANDF _ctype1[(unsigned char)(c)]&(T_SUB|T_QOT))
> #define escchar(c)	(((c)&QUOTE)==0 ANDF _ctype1[(unsigned char)(c)]&(T_ESC))
80c80
< char	_ctype2[];
---
> extern char	_ctype2[];
82,90c82,90
< #define	digit(c)	(((c)&QUOTE)==0 ANDF _ctype2[c]&(T_DIG))
< #define fngchar(c)	(((c)&QUOTE)==0 ANDF _ctype2[c]&(T_FNG))
< #define dolchar(c)	(((c)&QUOTE)==0 ANDF _ctype2[c]&(T_AST|T_BRC|T_DIG|T_IDC|T_SHN))
< #define defchar(c)	(((c)&QUOTE)==0 ANDF _ctype2[c]&(T_DEF))
< #define setchar(c)	(((c)&QUOTE)==0 ANDF _ctype2[c]&(T_SET))
< #define digchar(c)	(((c)&QUOTE)==0 ANDF _ctype2[c]&(T_AST|T_DIG))
< #define	letter(c)	(((c)&QUOTE)==0 ANDF _ctype2[c]&(T_IDC))
< #define alphanum(c)	(((c)&QUOTE)==0 ANDF _ctype2[c]&(_IDCH))
< #define astchar(c)	(((c)&QUOTE)==0 ANDF _ctype2[c]&(T_AST))
---
> #define	digit(c)	(((c)&QUOTE)==0 ANDF _ctype2[(unsigned char)(c)]&(T_DIG))
> #define fngchar(c)	(((c)&QUOTE)==0 ANDF _ctype2[(unsigned char)(c)]&(T_FNG))
> #define dolchar(c)	(((c)&QUOTE)==0 ANDF _ctype2[(unsigned char)(c)]&(T_AST|T_BRC|T_DIG|T_IDC|T_SHN))
> #define defchar(c)	(((c)&QUOTE)==0 ANDF _ctype2[(unsigned char)(c)]&(T_DEF))
> #define setchar(c)	(((c)&QUOTE)==0 ANDF _ctype2[(unsigned char)(c)]&(T_SET))
> #define digchar(c)	(((c)&QUOTE)==0 ANDF _ctype2[(unsigned char)(c)]&(T_AST|T_DIG))
> #define	letter(c)	(((c)&QUOTE)==0 ANDF _ctype2[(unsigned char)(c)]&(T_IDC))
> #define alphanum(c)	(((c)&QUOTE)==0 ANDF _ctype2[(unsigned char)(c)]&(_IDCH))
> #define astchar(c)	(((c)&QUOTE)==0 ANDF _ctype2[(unsigned char)(c)]&(T_AST))
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
11a12,22
> extern void exit(int n) __attribute__((__noreturn__));
> extern int unlink(char *p);
> void	exitsh(INT xno);
> void	rmtemp(IOPTR base);
> INT	assnum(STRING *p, INT n);
> void	prp(void);
> void	newline(void);
> void	done(void);
> void	clearup(void);
> void	execexp(STRING s, UFD f);
> 
15c26
< exitset()
---
> INT exitset(void)
17a29
> 	return(0);
20c32
< sigchk()
---
> INT sigchk(void)
28a41
> 	return(0);
31,32c44
< failed(s1,s2)
< 	STRING	s1, s2;
---
> INT failed(STRING s1, STRING s2)
34c46
< 	prp(); prs(s1); 
---
> 	prp(); prs(s1);
38a51
> 	return(0);
41,42c54
< error(s)
< 	STRING	s;
---
> INT error(STRING s)
44a57
> 	return(0);
47,48c60,61
< exitsh(xno)
< 	INT	xno;
---
> void
> exitsh(INT xno)
65c78
< done()
---
> void done(void)
68c81
< 	IF t=trapcom[0]
---
> 	IF (t=trapcom[0])
76,77c89,90
< rmtemp(base)
< 	IOPTR		base;
---
> void
> rmtemp(IOPTR base)
```

### cmd/sh/fault.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/fault.c unix-v7-c99/cmd/sh/fault.c || true
```

Expect:

```
11a12,27
> extern int signal(int sig, int fun);
> extern void execexp(STRING t, INT in);
> extern void error(STRING s);
> extern void done(void);
> extern INT setbrk(INT n);
> extern void exitset(void);
> extern void free(void *p);
> 
> VOID	stdsigs(void);
> INT	ignsig(INT n);
> VOID	getsig(INT n);
> VOID	oldsigs(void);
> VOID	clrsig(INT i);
> VOID	chktrap(void);
> VOID	fault(INT sig);
> 
19,20c35,36
< VOID	fault(sig)
< 	REG INT		sig;
---
> VOID
> fault(INT sig)
24c40
< 	signal(sig,fault);
---
> 	signal(sig, (int)fault);
36a53
> 	return(0);
39c56,57
< stdsigs()
---
> VOID
> stdsigs(void)
44a63
> 	return(0);
47c66,67
< ignsig(n)
---
> INT
> ignsig(INT n)
57c77,78
< getsig(n)
---
> VOID
> getsig(INT n)
62c83
< 	THEN	signal(i,fault);
---
> 	THEN	signal(i, (int)fault);
63a85
> 	return(0);
66c88,89
< oldsigs()
---
> VOID
> oldsigs(void)
79a103
> 	return(0);
82,83c106,107
< clrsig(i)
< 	INT		i;
---
> VOID
> clrsig(INT i)
87c111
< 	THEN	signal(i,fault);
---
> 	THEN	signal(i, (int)fault);
89a114
> 	return(0);
92c117,118
< chktrap()
---
> VOID
> chktrap(void)
102c128
< 		IF t=trapcom[i]
---
> 		IF (t=trapcom[i])
108a135
> 	return(0);
```

### cmd/sh/io.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/io.c unix-v7-c99/cmd/sh/io.c || true
```

Expect:

```
12a13,30
> extern int close(int fd);
> extern int open(char *p, int f);
> extern int creat(char *p, int m);
> extern int pipe(int *pv);
> extern int dup(int f1, int f2);
> extern int write(int fd, char *buf, int n);
> INT	length(STRING as);
> INT	itos(INT n);
> INT	chkpr(CHAR c);
> INT	readc(void);
> INT	nextc(INT quote);
> INT	failed(STRING s1, STRING s2);
> INT	error(STRING s);
> INT	tmpfil(void);
> INT	create(STRING s);
> INT	cf(STRING s1, STRING s2);
> STRING	mactrim(STRING s);
> 
16,17c34
< initf(fd)
< 	UFD		fd;
---
> INT initf(UFD fd)
23a41
> 	return(0);
26,27c44
< estabf(s)
< 	REG STRING	s;
---
> INT estabf(REG STRING s)
37,38c54
< push(af)
< 	FILE		af;
---
> INT push(FILE af)
44a61
> 	return(0);
47c64
< pop()
---
> INT pop(void)
59,60c76
< chkpipe(pv)
< 	INT		*pv;
---
> INT chkpipe(INT *pv)
64a81
> 	return(0);
67,68c84,85
< chkopen(idf)
< 	STRING		idf;
---
> INT
> chkopen(STRING idf)
75a93
> 	return(0);
78,79c96
< rename(f1,f2)
< 	REG INT		f1, f2;
---
> INT rename(REG INT f1, REG INT f2)
85a103
> 	return(0);
88,89c106,107
< create(s)
< 	STRING		s;
---
> INT
> create(STRING s)
96a115
> 	return(0);
99c118
< tmpfil()
---
> INT tmpfil(void)
108,109c127
< copy(ioparg)
< 	IOPTR		ioparg;
---
> INT copy(IOPTR ioparg)
116c134
< 	IF iop=ioparg
---
> 	IF (iop=ioparg)
132a151
> 	return(0);
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
12a13,32
> LOCAL INT	getch(CHAR endch);
> LOCAL INT	skipto(CHAR endch);
> LOCAL INT	comsubst(void);
> LOCAL INT	flush(INT ot);
> INT	error(STRING s);
> INT	readc(void);
> INT	failed(STRING s1, STRING s2);
> INT	assign(NAMPTR n, STRING v);
> INT	push(FILE af);
> INT	pop(void);
> INT	estabf(REG STRING s);
> INT	trim(STRING at);
> INT	chkpipe(INT *pv);
> INT	initf(UFD fd);
> INT	execute(TREPTR argt, INT execflg, INT *pf1, INT *pf2);
> INT	tdystak(REG STKPTR x);
> INT	await(INT i);
> extern int close(int fd);
> extern int write(int fd, char *buf, int n);
> 
18,19c38
< LOCAL STRING	copyto(endch)
< 	REG CHAR	endch;
---
> LOCAL STRING	copyto(INT endch)
26a46
> 	return(0);
29,30c49
< LOCAL	skipto(endch)
< 	REG CHAR	endch;
---
> LOCAL INT skipto(CHAR endch)
46a66
> 	return(0);
49,50c69
< LOCAL	getch(endch)
< 	CHAR		endch;
---
> LOCAL INT getch(CHAR endch)
62c81
< 		THEN	NAMPTR		n=NIL;
---
> 		THEN	NAMPTR		n=(NAMPTR)NIL;
69c88
< 			IF bra=(c==BRACE) THEN c=readc() FI
---
> 			IF (bra=(c==BRACE)) THEN c=readc() FI
71c90
< 			THEN	argp=relstak();
---
> 			THEN	argp=(STRING)(long)relstak();
83c102
< 				v=((c==0) ? cmdadr : (c<=dolc) ? dolv[c] : (dolg=0));
---
> 				v=((c==0) ? cmdadr : (c<=dolc) ? dolv[c] : (STRING)(long)(dolg=0));
104c123
< 				THEN	argp=relstak();
---
> 				THEN	argp=(STRING)(long)relstak();
115c134
< 				THEN	LOOP WHILE c = *v++
---
> 				THEN	LOOP WHILE (c = *v++)
148,149c167
< STRING	macro(as)
< 	STRING		as;
---
> STRING	macro(STRING as)
158c176
< 	push(&fb); estabf(as);
---
> 	push((FILE)&fb); estabf(as);
168c186
< LOCAL	comsubst()
---
> LOCAL INT comsubst(void)
197c215
< 	WHILE d=readc() DO pushstak(d|quote) OD
---
> 	WHILE (d=readc()) DO pushstak(d|quote) OD
204a223
> 	return(0);
209,210c228
< subst(in,ot)
< 	INT		in, ot;
---
> INT subst(INT in, INT ot)
218c236
< 	WHILE c=(getch(DQUOTE)&STRIP)
---
> 	WHILE (c=(getch(DQUOTE)&STRIP))
225a244
> 	return(0);
228c247
< LOCAL	flush(ot)
---
> LOCAL INT flush(INT ot)
232a252
> 	return(0);
```

### cmd/sh/main.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/main.c unix-v7-c99/cmd/sh/main.c || true
```

Expect:

```
25c25,55
< PROC VOID	exfile();
---
> PROC VOID	exfile(BOOL prof);
> INT	stdsigs(void);
> INT	addblok(POS reqd);
> INT	options(INT argc, STRING *argv);
> INT	assnum(STRING *p, INT n);
> INT	settmp(void);
> INT	dfault(NAMPTR n, STRING v);
> INT	estabf(REG STRING s);
> INT	chkopen(STRING idf);
> INT	pathopen(STRING path, STRING name);
> INT	done(void);
> INT	Ldup(REG INT fa, REG INT fb);
> INT	initf(UFD fd);
> INT	tdystak(REG STKPTR x);
> INT	stakchk(void);
> INT	exitset(void);
> INT	ignsig(INT n);
> INT	execute(TREPTR argt, INT execflg, INT *pf1, INT *pf2);
> INT	itos(INT n);
> INT	getenv(void);
> extern INT setbrk(INT n);
> INT	readc(void);
> VOID	prs(STRING as);
> extern int getpid(void);
> extern int getuid(void);
> extern int gtty();
> extern int alarm(unsigned sec);
> extern int stat(char *p, struct stat *s);
> extern int close(int fd);
> extern int dup();
> extern int ioctl(int fd, int cmd, ...);
30,32c60,61
< main(c, v)
< 	INT		c;
< 	STRING		v[];
---
> int
> main(INT c, STRING v[])
85c114
< 	ELSE	*execargs=dolv;	/* for `ps' cmd */
---
> 	ELSE	*execargs=(char *)dolv;	/* for `ps' cmd */
89a119
> 	return(0);
92,93c122
< LOCAL VOID	exfile(prof)
< BOOL		prof;
---
> LOCAL VOID	exfile(BOOL prof)
95c124
< 	REG L_INT	mailtime = 0;
---
> 	volatile L_INT	mailtime = 0;
122c151
< 	THEN	close(input); return;
---
> 	THEN	close(input); return(0);
146c175
< 		THEN	return;
---
> 		THEN	return(0);
149c178
< 		execute(cmd(NL,MTFLG),0);
---
> 		execute(cmd(NL,MTFLG),0,(INT *)0,(INT *)0);
154,155c183,184
< chkpr(eor)
< char eor;
---
> VOID
> chkpr(INT eor)
159a189
> 	return(0);
162c192
< settmp()
---
> INT settmp(void)
165a196
> 	return(0);
168,169c199
< Ldup(fa, fb)
< 	REG INT		fa, fb;
---
> INT Ldup(REG INT fa, REG INT fb)
173a204
> 	return(0);
```

### cmd/sh/name.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/name.c unix-v7-c99/cmd/sh/name.c || true
```

Expect:

```
12,21c12,42
< PROC BOOL	chkid();
< 
< 
< NAMNOD	ps2nod	= {	NIL,		NIL,		ps2name},
< 	fngnod	= {	NIL,		NIL,		fngname},
< 	pathnod = {	NIL,		NIL,		pathname},
< 	ifsnod	= {	NIL,		NIL,		ifsname},
< 	ps1nod	= {	&pathnod,	&ps2nod,	ps1name},
< 	homenod = {	&fngnod,	&ifsnod,	homename},
< 	mailnod = {	&homenod,	&ps1nod,	mailname};
---
> PROC BOOL	chkid(STRING nam);
> LOCAL VOID	namwalk(REG NAMPTR np);
> VOID	countnam(NAMPTR n);
> VOID	pushnam(NAMPTR n);
> INT	cf(STRING s1, STRING s2);
> INT	blank(void);
> INT	newline(void);
> INT	assign(NAMPTR n, STRING v);
> INT	failed(STRING s1, STRING s2);
> INT	itos(INT n);
> INT	any(REG CHAR c, STRING s);
> INT	push(FILE af);
> INT	initf(UFD fd);
> INT	pop(void);
> INT	nextc(INT quote);
> INT	sigchk(void);
> INT	length(STRING as);
> VOID	prc(INT c);
> VOID	prs(STRING as);
> extern int dup();
> extern long lseek(int fd, long off, int whence);
> extern void free(void *p);
> 
> 
> NAMNOD	ps2nod	= {	0,		0,		ps2name,	NIL, NIL, 0},
> 	fngnod	= {	0,		0,		fngname,	NIL, NIL, 0},
> 	pathnod = {	0,		0,		pathname,	NIL, NIL, 0},
> 	ifsnod	= {	0,		0,		ifsname,	NIL, NIL, 0},
> 	ps1nod	= {	&pathnod,	&ps2nod,	ps1name,	NIL, NIL, 0},
> 	homenod = {	&fngnod,	&ifsnod,	homename,	NIL, NIL, 0},
> 	mailnod = {	&homenod,	&ps1nod,	mailname,	NIL, NIL, 0};
28,30c49
< syslook(w,syswds)
< 	STRING		w;
< 	SYSTAB		syswds;
---
> INT syslook(STRING w, struct sysnod syswds[])
38c57
< 	WHILE s=syscan->sysnam
---
> 	WHILE (s=syscan->sysnam)
48,50c67
< setlist(arg,xp)
< 	REG ARGPTR	arg;
< 	INT		xp;
---
> INT setlist(REG ARGPTR arg, INT xp)
60a78
> 	return(0);
63,65c81
< VOID	setname(argi, xp)
< 	STRING		argi;
< 	INT		xp;
---
> VOID	setname(STRING argi, INT xp)
81c97
< 			return;
---
> 			return(0);
84a101
> 	return(0);
87,89c104,105
< replace(a, v)
< 	REG STRING	*a;
< 	STRING		v;
---
> INT
> replace(REG STRING *a, STRING v)
91a108
> 	return(0);
94,96c111
< dfault(n,v)
< 	NAMPTR		n;
< 	STRING		v;
---
> INT dfault(NAMPTR n, STRING v)
100a116
> 	return(0);
103,105c119
< assign(n,v)
< 	NAMPTR		n;
< 	STRING		v;
---
> INT assign(NAMPTR n, STRING v)
110a125
> 	return(0);
113,114c128
< INT	readvar(names)
< 	STRING		*names;
---
> INT	readvar(STRING *names)
121c135
< 	STKPTR		rel=relstak();
---
> 	STKPTR		rel=(STKPTR)(long)relstak();
153,155c167
< assnum(p, i)
< 	STRING		*p;
< 	INT		i;
---
> INT assnum(STRING *p, INT i)
157a170
> 	return(0);
160,161c173
< STRING	make(v)
< 	STRING		v;
---
> STRING	make(STRING v)
173,174c185
< NAMPTR		lookup(nam)
< 	REG STRING	nam;
---
> NAMPTR		lookup(REG STRING nam)
177c188
< 	REG NAMPTR	*prev;
---
> 	REG NAMPTR	*prev = 0;
194,195c205,206
< 	nscan=alloc(sizeof *nscan);
< 	nscan->namlft=nscan->namrgt=NIL;
---
> 	nscan=(NAMPTR)alloc(sizeof *nscan);
> 	nscan->namlft=nscan->namrgt=0;
201,202c212
< LOCAL BOOL	chkid(nam)
< 	STRING		nam;
---
> LOCAL BOOL	chkid(STRING nam)
217,219c227,229
< LOCAL VOID (*namfn)();
< namscan(fn)
< 	VOID		(*fn)();
---
> LOCAL VOID (*namfn)(NAMPTR);
> INT
> namscan(VOID (*fn)(NAMPTR))
222a233
> 	return(0);
225,226c236
< LOCAL VOID	namwalk(np)
< 	REG NAMPTR	np;
---
> LOCAL VOID	namwalk(REG NAMPTR np)
232a243
> 	return(0);
235,236c246
< VOID	printnam(n)
< 	NAMPTR		n;
---
> VOID	printnam(NAMPTR n)
241c251
< 	IF s=n->namval
---
> 	IF (s=n->namval)
245a256
> 	return(0);
248,249c259
< LOCAL STRING	staknam(n)
< 	REG NAMPTR	n;
---
> LOCAL STRING	staknam(REG NAMPTR n)
259,260c269
< VOID	exname(n)
< 	REG NAMPTR	n;
---
> VOID	exname(REG NAMPTR n)
267a277
> 	return(0);
270,271c280
< VOID	printflg(n)
< 	REG NAMPTR		n;
---
> VOID	printflg(REG NAMPTR n)
281a291
> 	return(0);
284c294
< VOID	getenv()
---
> INT	getenv(void)
286a297
> 	REG STRING	s;
289c300,305
< 	DO setname(*e++, N_ENVNAM) OD
---
> 	DO	s = *e++;
> 		IF any('=', s)
> 		THEN	setname(s, N_ENVNAM);
> 		FI
> 	OD
> 	return(0);
294,295c310
< VOID	countnam(n)
< 	NAMPTR		n;
---
> VOID	countnam(NAMPTR n)
296a312
> 	(void)n;
297a314
> 	return(0);
302,303c319
< VOID	pushnam(n)
< 	NAMPTR		n;
---
> VOID	pushnam(NAMPTR n)
307a324
> 	return(0);
310c327
< STRING	*setenv()
---
> STRING	*setenv(void)
316c333
< 	argnam = er = getstak(namec*BYTESPERWORD+BYTESPERWORD);
---
> 	argnam = er = (STRING *)getstak(namec*BYTESPERWORD+BYTESPERWORD);
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
11a12,17
> extern int write(int fd, char *buf, int n);
> INT	length(STRING as);
> INT	itos(INT n);
> INT	prn(INT n);
> INT	failed(STRING s1, STRING s2);
> 
17,18c23,24
< newline()
< {	prc(NL);
---
> INT newline(void)
> {	prc(NL); return(0);
21,22c27,28
< blank()
< {	prc(SP);
---
> INT blank(void)
> {	prc(SP); return(0);
25c31
< prp()
---
> INT prp(void)
29a36
> 	return(0);
32,33c39
< VOID	prs(as)
< 	STRING		as;
---
> VOID	prs(STRING as)
37c43
< 	IF s=as
---
> 	IF (s=as)
39a46
> 	return(0);
42,43c49
< VOID	prc(c)
< 	CHAR		c;
---
> VOID	prc(INT cc)
44a51
> 	CHAR c = cc;
47a55
> 	return(0);
50,51c58
< prt(t)
< 	L_INT		t;
---
> INT prt(L_INT t)
58c65
< 	IF hr=t/60
---
> 	IF (hr=t/60)
62a70
> 	return(0);
65,66c73
< prn(n)
< 	INT		n;
---
> INT prn(INT n)
68a76
> 	return(0);
71c79
< itos(n)
---
> INT itos(INT n)
80a89
> 	return(0);
83,84c92,93
< stoi(icp)
< STRING	icp;
---
> INT
> stoi(STRING icp)
95a105
> 	return(0);
```

### cmd/sh/setbrk.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/setbrk.c unix-v7-c99/cmd/sh/setbrk.c || true
```

Expect:

```
12c12,14
< setbrk(incr)
---
> extern char *sbrk(int incr);
> 
> BYTPTR setbrk(INT incr)
```

### cmd/sh/stak.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/stak.c unix-v7-c99/cmd/sh/stak.c || true
```

Expect:

```
11a12,15
> extern INT setbrk(INT n);
> extern void free(void *p);
> extern void rmtemp(IOPTR base);
> 
18,19c22
< STKPTR	getstak(asize)
< 	INT		asize;
---
> STKPTR	getstak(INT asize)
30c33
< STKPTR	locstak()
---
> STKPTR	locstak(void)
43c46
< STKPTR	savstak()
---
> STKPTR	savstak(void)
49,50c52
< STKPTR	endstak(argp)
< 	REG STRING	argp;
---
> STKPTR	endstak(REG STRING argp)
54c56
< 	oldstak=stakbot; stakbot=staktop=round(argp,BYTESPERWORD);
---
> 	oldstak=stakbot; stakbot=staktop=(STKPTR)round(argp,BYTESPERWORD);
58,59c60
< VOID	tdystak(x)
< 	REG STKPTR 	x;
---
> VOID	tdystak(REG STKPTR x)
67c68,69
< 	rmtemp(x);
---
> 	rmtemp((IOPTR)x);
> 	return(0);
70c72
< stakchk()
---
> INT stakchk(void)
74a77
> 	return(0);
77,78c80
< STKPTR	cpystak(x)
< 	STKPTR		x;
---
> STKPTR	cpystak(STKPTR x)
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
16,17c16
< STRING	movstr(a,b)
< 	REG STRING	a, b;
---
> STRING	movstr(REG STRING a, REG STRING b)
19c18
< 	WHILE *b++ = *a++ DONE
---
> 	WHILE (*b++ = *a++) DONE
23,25c22
< INT	any(c,s)
< 	REG CHAR	c;
< 	STRING		s;
---
> INT	any(REG CHAR c, STRING s)
29c26
< 	WHILE d = *s++
---
> 	WHILE (d = *s++)
37,38c34
< INT	cf(s1, s2)
< 	REG STRING s1, s2;
---
> INT	cf(REG STRING s1, REG STRING s2)
48,49c44
< INT	length(as)
< 	STRING as;
---
> INT	length(STRING as)
53c48
< 	IF s=as THEN WHILE *s++ DONE FI
---
> 	IF (s=as) THEN WHILE *s++ DONE FI
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
79c85
< 	while(c = *s++) {
---
> 	while((c = *s++)) {
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
12a13,15
> #include <sys/types.h>
> #include <sys/stat.h>
> #include <sys/dir.h>
42a46
> int	rflag;
59,60c63,71
< main(argc, argv)
< char **argv;
---
> void compile(char *astr);
> void execute(char *file);
> void descend(char *path);
> int advance(register char *lp, register char *ep);
> void succeed(char *f);
> int ecmp(char *a, char *b, int count);
> void errexit(char *s, char *f);
> int
> main(int argc, char *argv[])
62,63c73,78
< 	while (--argc > 0 && (++argv)[0][0]=='-')
< 		switch (argv[0][1]) {
---
> 	while (--argc > 0 && (++argv)[0][0]=='-') {
> 		char *fp = argv[0] + 1;
> 		if (*fp == '\0') { /* lone "-" -> stdin marker; bail out */
> 			break;
> 		}
> 		while (*fp) switch (*fp++) {
65a81
> 		case 'i':	/* -i (POSIX) is an alias for -y: case-insensitive */
68a85,89
> 		case 'r':
> 		case 'R':	/* recurse into directory arguments */
> 			rflag++;
> 			continue;
> 
105a127
> 	}
140c162,165
< 		execute(*argv);
---
> 		if (rflag)
> 			descend(*argv);
> 		else
> 			execute(*argv);
145,146c170,210
< compile(astr)
< char *astr;
---
> /* If `path` is a directory, walk its entries and recurse; otherwise
>  * run the compiled regex over the file via execute(). */
> void
> descend(char *path)
> {
> 	struct stat st;
> 	struct direct dent;
> 	FILE *df;
> 	char child[256];
> 	int i, j;
> 	if (stat(path, &st) < 0) {
> 		fprintf(stderr, "grep: can't access %s\n", path);
> 		return;
> 	}
> 	if ((st.st_mode & S_IFMT) != S_IFDIR) {
> 		execute(path);
> 		return;
> 	}
> 	if ((df = fopen(path, "r")) == NULL) {
> 		fprintf(stderr, "grep: can't read dir %s\n", path);
> 		return;
> 	}
> 	/* With -r, each file's name should print, so behave like nfile>1. */
> 	if (nfile < 2) nfile = 2;
> 	while (fread((char *)&dent, sizeof(dent), 1, df) == 1) {
> 		if (dent.d_ino == 0) continue;
> 		if (dent.d_name[0] == '.' &&
> 		    (dent.d_name[1] == '\0' ||
> 		     (dent.d_name[1] == '.' && dent.d_name[2] == '\0')))
> 			continue;
> 		for (i = 0; path[i] && i < 200; i++) child[i] = path[i];
> 		if (i > 0 && child[i-1] != '/') child[i++] = '/';
> 		for (j = 0; j < DIRSIZ && dent.d_name[j]; j++) child[i++] = dent.d_name[j];
> 		child[i] = '\0';
> 		descend(child);
> 	}
> 	fclose(df);
> }
> 
> void
> compile(char *astr)
148c212
< 	register c;
---
> 	register int c;
250a315
> 			goto defchar;
262,263c327,328
< execute(file)
< char *file;
---
> void
> execute(char *file)
266c331
< 	register c;
---
> 	register int c;
324,325c389,390
< advance(lp, ep)
< register char *lp, *ep;
---
> int
> advance(register char *lp, register char *ep)
360c425
< 		braslist[*ep++] = lp;
---
> 		braslist[(unsigned char)*ep++] = lp;
364c429
< 		braelist[*ep++] = lp;
---
> 		braelist[(unsigned char)*ep++] = lp;
368,369c433,434
< 		bbeg = braslist[*ep];
< 		if (braelist[*ep]==0)
---
> 		bbeg = braslist[(unsigned char)*ep];
> 		if (braelist[(unsigned char)*ep]==0)
371c436
< 		ct = braelist[*ep++] - bbeg;
---
> 		ct = braelist[(unsigned char)*ep++] - bbeg;
379,380c444,445
< 		bbeg = braslist[*ep];
< 		if (braelist[*ep]==0)
---
> 		bbeg = braslist[(unsigned char)*ep];
> 		if (braelist[(unsigned char)*ep]==0)
382c447
< 		ct = braelist[*ep++] - bbeg;
---
> 		ct = braelist[(unsigned char)*ep++] - bbeg;
439,440c504,505
< succeed(f)
< char *f;
---
> void
> succeed(char *f)
442c507
< 	long ftell();
---
> 	long ftell(FILE *iop);
464,465c529,530
< ecmp(a, b, count)
< char	*a, *b;
---
> int
> ecmp(char *a, char *b, int count)
467c532
< 	register cc = count;
---
> 	register int cc = count;
473,474c538,539
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
2a3,4
>  * cp f1 ... fn dir
>  * cp -r src dir       (recursive)
8a11,13
> #include <sys/dir.h>
> extern int mkdir(char *path, int mode);
> 
10a16,20
> int	rflag;
> 
> int copy(char *from, char *to);
> int copyfile(char *from, char *to);
> int copydir(char *from, char *to);
12,13c22,23
< main(argc, argv)
< char *argv[];
---
> int
> main(int argc, char *argv[])
15c25,26
< 	register i, r;
---
> 	register int i, r;
> 	int start = 1;
17c28,33
< 	if (argc < 3) 
---
> 	if (argc >= 2 && argv[1][0] == '-' && argv[1][1] == 'r' &&
> 	    argv[1][2] == '\0') {
> 		rflag = 1;
> 		start = 2;
> 	}
> 	if (argc < start + 2)
19c35
< 	if (argc > 3) {
---
> 	if (argc > start + 2) {
22c38
< 		if ((stbuf2.st_mode&S_IFMT) != S_IFDIR) 
---
> 		if ((stbuf2.st_mode&S_IFMT) != S_IFDIR)
26c42
< 	for(i=1; i<argc-1;i++)
---
> 	for (i = start; i < argc - 1; i++)
30c46
< 	fprintf(stderr, "Usage: cp: f1 f2; or cp f1 ... fn d2\n");
---
> 	fprintf(stderr, "Usage: cp [-r] f1 f2; or cp [-r] f1 ... fn d2\n");
34,35c50,53
< copy(from, to)
< char *from, *to;
---
> /* Dispatch to file or directory copy; if target is a dir, append the
>  * source basename so cp foo bar/  ->  bar/foo (matching v7 behavior). */
> int
> copy(char *from, char *to)
37c55
< 	int fold, fnew, n;
---
> 	static char dest[256];
38a57,82
> 	if (stat(from, &stbuf1) < 0) {
> 		fprintf(stderr, "cp: cannot stat %s\n", from);
> 		return 1;
> 	}
> 	if (stat(to, &stbuf2) >= 0 && (stbuf2.st_mode & S_IFMT) == S_IFDIR) {
> 		p1 = from; p2 = to; bp = dest;
> 		while ((*bp++ = *p2++)) ;
> 		bp[-1] = '/';
> 		p2 = bp;
> 		while ((*bp = *p1++)) if (*bp++ == '/') bp = p2;
> 		to = dest;
> 	}
> 	if ((stbuf1.st_mode & S_IFMT) == S_IFDIR) {
> 		if (!rflag) {
> 			fprintf(stderr, "cp: %s is a directory (use -r)\n", from);
> 			return 1;
> 		}
> 		return copydir(from, to);
> 	}
> 	return copyfile(from, to);
> }
> 
> int
> copyfile(char *from, char *to)
> {
> 	int fold, fnew, n;
42c86
< 		return(1);
---
> 		return 1;
46,60d89
< 	/* is target a directory? */
< 	if (stat(to, &stbuf2) >=0 &&
< 	   (stbuf2.st_mode&S_IFMT) == S_IFDIR) {
< 		p1 = from;
< 		p2 = to;
< 		bp = iobuf;
< 		while(*bp++ = *p2++)
< 			;
< 		bp[-1] = '/';
< 		p2 = bp;
< 		while(*bp = *p1++)
< 			if (*bp++ == '/')
< 				bp = p2;
< 		to = iobuf;
< 	}
63c92
< 		   stbuf1.st_ino == stbuf2.st_ino) {
---
> 		    stbuf1.st_ino == stbuf2.st_ino) {
65c94,95
< 			return(1);
---
> 			close(fold);
> 			return 1;
71c101
< 		return(1);
---
> 		return 1;
73c103
< 	while(n = read(fold,  iobuf,  BSIZE)) {
---
> 	while ((n = read(fold, iobuf, BSIZE))) {
76,89c106,158
< 			close(fold);
< 			close(fnew);
< 			return(1);
< 		} else
< 			if (write(fnew, iobuf, n) != n) {
< 				fprintf(stderr, "cp: write error.\n");
< 				close(fold);
< 				close(fnew);
< 				return(1);
< 			}
< 	}
< 	close(fold);
< 	close(fnew);
< 	return(0);
---
> 			close(fold); close(fnew);
> 			return 1;
> 		}
> 		if (write(fnew, iobuf, n) != n) {
> 			fprintf(stderr, "cp: write error.\n");
> 			close(fold); close(fnew);
> 			return 1;
> 		}
> 	}
> 	close(fold); close(fnew);
> 	return 0;
> }
> 
> int
> copydir(char *from, char *to)
> {
> 	struct direct dent;
> 	FILE *df;
> 	char src[256], dst[256];
> 	int errs = 0, i, j;
> 
> 	/* Create the target dir.  If it exists already, that's fine. */
> 	if (stat(to, &stbuf2) < 0) {
> 		if (mkdir(to, 0755) < 0) {
> 			fprintf(stderr, "cp: cannot mkdir %s\n", to);
> 			return 1;
> 		}
> 	} else if ((stbuf2.st_mode & S_IFMT) != S_IFDIR) {
> 		fprintf(stderr, "cp: %s exists and is not a directory\n", to);
> 		return 1;
> 	}
> 	if ((df = fopen(from, "r")) == NULL) {
> 		fprintf(stderr, "cp: cannot read dir %s\n", from);
> 		return 1;
> 	}
> 	while (fread((char *)&dent, sizeof(dent), 1, df) == 1) {
> 		if (dent.d_ino == 0) continue;
> 		if (dent.d_name[0] == '.' &&
> 		    (dent.d_name[1] == '\0' ||
> 		     (dent.d_name[1] == '.' && dent.d_name[2] == '\0')))
> 			continue;
> 		for (i = 0; from[i] && i < 200; i++) src[i] = from[i];
> 		if (i > 0 && src[i-1] != '/') src[i++] = '/';
> 		for (j = 0; j < DIRSIZ && dent.d_name[j]; j++) src[i++] = dent.d_name[j];
> 		src[i] = '\0';
> 		for (i = 0; to[i] && i < 200; i++) dst[i] = to[i];
> 		if (i > 0 && dst[i-1] != '/') dst[i++] = '/';
> 		for (j = 0; j < DIRSIZ && dent.d_name[j]; j++) dst[i++] = dent.d_name[j];
> 		dst[i] = '\0';
> 		errs += copy(src, dst);
> 	}
> 	fclose(df);
> 	return errs;
```

### cmd/mv.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/mv.c unix-v7-c99/cmd/mv.c || true
```

Expect:

```
19,21c19,25
< char	*pname();
< char	*sprintf();
< char	*dname();
---
> char	*pname(register char *name);
> char	*sprintf(char *buf, char *fmt, ...);
> char	*dname(register char *name);
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
229,230c233
< pname(name)
< register char *name;
---
> pname(register char *name)
232c235
< 	register c;
---
> 	register int c;
237c240
< 	while (c = *p++ = *name++)
---
> 	while ((c = *p++ = *name++))
247,248c250
< dname(name)
< register char *name;
---
> dname(register char *name)
259,261c261,262
< check(spth, dinode)
< char *spth;
< ino_t dinode;
---
> int
> check(char *spth, ino_t dinode)
278c279
< 		if (strlen(nspth) > MAXN-2-sizeof(DOTDOT)) {
---
> 		if (strlen(nspth) > (int)(MAXN-2-sizeof(DOTDOT))) {
288,289c289,290
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
7a8
> #include <sys/dir.h>
22a24,31
> int	rflag;
> char	*spec;	/* original mode argument; re-bound to ms before each newmode() */
> unsigned newmode(unsigned nm);
> int abs(void);
> int who(void);
> int what(void);
> int where(int om);
> int do_chmod(char *p);
24,25c33,34
< main(argc,argv)
< char **argv;
---
> int
> main(int argc, char **argv)
27,28c36
< 	register i;
< 	register char *p;
---
> 	register int i;
29a38
> 	int start = 1;
31,32c40,46
< 	if (argc < 3) {
< 		fprintf(stderr, "Usage: chmod [ugoa][+-=][rwxstugo] file ...\n");
---
> 	if (argc >= 2 && argv[1][0] == '-' && argv[1][1] == 'R' &&
> 	    argv[1][2] == '\0') {
> 		rflag = 1;
> 		start = 2;
> 	}
> 	if (argc < start + 2) {
> 		fprintf(stderr, "Usage: chmod [-R] [ugoa][+-=][rwxstugo] file ...\n");
35c49,50
< 	ms = argv[1];
---
> 	spec = argv[start];
> 	ms = spec;
38,50c53,54
< 	for (i = 2; i < argc; i++) {
< 		p = argv[i];
< 		if (stat(p, &st) < 0) {
< 			fprintf(stderr, "chmod: can't access %s\n", p);
< 			++status;
< 			continue;
< 		}
< 		ms = argv[1];
< 		if (chmod(p, newmode(st.st_mode)) < 0) {
< 			fprintf(stderr, "chmod: can't change %s\n", p);
< 			++status;
< 			continue;
< 		}
---
> 	for (i = start + 1; i < argc; i++) {
> 		status += do_chmod(argv[i]);
55,56c59,98
< newmode(nm)
< unsigned nm;
---
> /* Apply the mode change to p; if -R and p is a dir, recurse into entries. */
> int
> do_chmod(char *p)
> {
> 	struct direct dent;
> 	FILE *df;
> 	int errs = 0;
> 	char child[256];
> 	int i, j;
> 
> 	if (stat(p, &st) < 0) {
> 		fprintf(stderr, "chmod: can't access %s\n", p);
> 		return 1;
> 	}
> 	ms = spec;
> 	if (chmod(p, newmode(st.st_mode)) < 0) {
> 		fprintf(stderr, "chmod: can't change %s\n", p);
> 		errs++;
> 	}
> 	if (rflag && (st.st_mode & S_IFMT) == S_IFDIR) {
> 		if ((df = fopen(p, "r")) == NULL)
> 			return errs;
> 		while (fread((char *)&dent, sizeof(dent), 1, df) == 1) {
> 			if (dent.d_ino == 0) continue;
> 			if (dent.d_name[0] == '.' &&
> 			    (dent.d_name[1] == '\0' || (dent.d_name[1] == '.' && dent.d_name[2] == '\0')))
> 				continue;
> 			for (i = 0; p[i] && i < 200; i++) child[i] = p[i];
> 			if (i > 0 && child[i-1] != '/') child[i++] = '/';
> 			for (j = 0; j < DIRSIZ && dent.d_name[j]; j++) child[i++] = dent.d_name[j];
> 			child[i] = '\0';
> 			errs += do_chmod(child);
> 		}
> 		fclose(df);
> 	}
> 	return errs;
> }
> 
> unsigned
> newmode(unsigned nm)
58c100
< 	register o, m, b;
---
> 	register int o, m, b;
65c107
< 		while (o = what()) {
---
> 		while ((o = what())) {
88c130,131
< abs()
---
> int
> abs(void)
90c133
< 	register c, i;
---
> 	register int c, i;
99c142,143
< who()
---
> int
> who(void)
101c145
< 	register m;
---
> 	register int m;
125c169,170
< what()
---
> int
> what(void)
136,137c181,182
< where(om)
< register om;
---
> int
> where(int om)
139c184
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
2c2
<  * chown uid file ...
---
>  * chown [-R] uid file ...
8a9
> #include <sys/dir.h>
14a16,18
> int	rflag;
> int	isnumber(char *s);
> int	do_chown(char *p);
16,17c20,21
< main(argc, argv)
< char *argv[];
---
> int
> main(int argc, char *argv[])
19c23,24
< 	register c;
---
> 	register int c;
> 	int start = 1;
21,27c26,29
< 	if(argc < 3) {
< 		printf("usage: chown uid file ...\n");
< 		exit(4);
< 	}
< 	if(isnumber(argv[1])) {
< 		uid = atoi(argv[1]);
< 		goto cho;
---
> 	if (argc >= 2 && argv[1][0] == '-' && argv[1][1] == 'R' &&
> 	    argv[1][2] == '\0') {
> 		rflag = 1;
> 		start = 2;
29,30c31,32
< 	if((pwd=getpwnam(argv[1])) == NULL) {
< 		printf("unknown user id: %s\n",argv[1]);
---
> 	if (argc < start + 2) {
> 		printf("usage: chown [-R] uid file ...\n");
33c35,43
< 	uid = pwd->pw_uid;
---
> 	if (isnumber(argv[start])) {
> 		uid = atoi(argv[start]);
> 	} else {
> 		if ((pwd = getpwnam(argv[start])) == NULL) {
> 			printf("unknown user id: %s\n", argv[start]);
> 			exit(4);
> 		}
> 		uid = pwd->pw_uid;
> 	}
35,40c45,79
< cho:
< 	for(c=2; c<argc; c++) {
< 		stat(argv[c], &stbuf);
< 		if(chown(argv[c], uid, stbuf.st_gid) < 0) {
< 			perror(argv[c]);
< 			status = 1;
---
> 	for (c = start + 1; c < argc; c++)
> 		status += do_chown(argv[c]);
> 	exit(status ? 1 : 0);
> }
> 
> int
> do_chown(char *p)
> {
> 	struct direct dent;
> 	FILE *df;
> 	int errs = 0, i, j;
> 	char child[256];
> 
> 	if (stat(p, &stbuf) < 0) {
> 		perror(p);
> 		return 1;
> 	}
> 	if (chown(p, uid, stbuf.st_gid) < 0) {
> 		perror(p);
> 		errs++;
> 	}
> 	if (rflag && (stbuf.st_mode & S_IFMT) == S_IFDIR) {
> 		if ((df = fopen(p, "r")) == NULL)
> 			return errs;
> 		while (fread((char *)&dent, sizeof(dent), 1, df) == 1) {
> 			if (dent.d_ino == 0) continue;
> 			if (dent.d_name[0] == '.' &&
> 			    (dent.d_name[1] == '\0' ||
> 			     (dent.d_name[1] == '.' && dent.d_name[2] == '\0')))
> 				continue;
> 			for (i = 0; p[i] && i < 200; i++) child[i] = p[i];
> 			if (i > 0 && child[i-1] != '/') child[i++] = '/';
> 			for (j = 0; j < DIRSIZ && dent.d_name[j]; j++) child[i++] = dent.d_name[j];
> 			child[i] = '\0';
> 			errs += do_chown(child);
41a81
> 		fclose(df);
43c83
< 	exit(status);
---
> 	return errs;
46,47c86,87
< isnumber(s)
< char *s;
---
> int
> isnumber(char *s)
49c89
< 	register c;
---
> 	register int c;
51,52c91,92
< 	while(c = *s++)
< 		if(!isdigit(c))
---
> 	while ((c = *s++))
> 		if (!isdigit(c))
```

### cmd/chgrp.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/chgrp.c unix-v7-c99/cmd/chgrp.c || true
```

Expect:

```
2c2
<  * chgrp gid file ...
---
>  * chgrp [-R] gid file ...
8a9
> #include <sys/dir.h>
14a16,18
> int	rflag;
> int	isnumber(char *s);
> int	do_chgrp(char *p);
16,17c20,21
< main(argc, argv)
< char *argv[];
---
> int
> main(int argc, char *argv[])
19c23,24
< 	register c;
---
> 	register int c;
> 	int start = 1;
21,22c26,32
< 	if(argc < 3) {
< 		printf("usage: chgrp gid file ...\n");
---
> 	if (argc >= 2 && argv[1][0] == '-' && argv[1][1] == 'R' &&
> 	    argv[1][2] == '\0') {
> 		rflag = 1;
> 		start = 2;
> 	}
> 	if (argc < start + 2) {
> 		printf("usage: chgrp [-R] gid file ...\n");
25,26c35,36
< 	if(isnumber(argv[1])) {
< 		gid = atoi(argv[1]);
---
> 	if (isnumber(argv[start])) {
> 		gid = atoi(argv[start]);
28,29c38,39
< 		if((gr=getgrnam(argv[1])) == NULL) {
< 			printf("unknown group: %s\n",argv[1]);
---
> 		if ((gr = getgrnam(argv[start])) == NULL) {
> 			printf("unknown group: %s\n", argv[start]);
34,38c44,78
< 	for(c=2; c<argc; c++) {
< 		stat(argv[c], &stbuf);
< 		if(chown(argv[c], stbuf.st_uid, gid) < 0) {
< 			perror(argv[c]);
< 			status = 1;
---
> 	for (c = start + 1; c < argc; c++)
> 		status += do_chgrp(argv[c]);
> 	exit(status ? 1 : 0);
> }
> 
> int
> do_chgrp(char *p)
> {
> 	struct direct dent;
> 	FILE *df;
> 	int errs = 0, i, j;
> 	char child[256];
> 
> 	if (stat(p, &stbuf) < 0) {
> 		perror(p);
> 		return 1;
> 	}
> 	if (chown(p, stbuf.st_uid, gid) < 0) {
> 		perror(p);
> 		errs++;
> 	}
> 	if (rflag && (stbuf.st_mode & S_IFMT) == S_IFDIR) {
> 		if ((df = fopen(p, "r")) == NULL)
> 			return errs;
> 		while (fread((char *)&dent, sizeof(dent), 1, df) == 1) {
> 			if (dent.d_ino == 0) continue;
> 			if (dent.d_name[0] == '.' &&
> 			    (dent.d_name[1] == '\0' ||
> 			     (dent.d_name[1] == '.' && dent.d_name[2] == '\0')))
> 				continue;
> 			for (i = 0; p[i] && i < 200; i++) child[i] = p[i];
> 			if (i > 0 && child[i-1] != '/') child[i++] = '/';
> 			for (j = 0; j < DIRSIZ && dent.d_name[j]; j++) child[i++] = dent.d_name[j];
> 			child[i] = '\0';
> 			errs += do_chgrp(child);
39a80
> 		fclose(df);
41c82
< 	exit(status);
---
> 	return errs;
44,45c85,86
< isnumber(s)
< char *s;
---
> int
> isnumber(char *s)
47c88
< 	register c;
---
> 	register int c;
49,50c90,91
< 	while(c = *s++)
< 		if(!isdigit(c))
---
> 	while ((c = *s++))
> 		if (!isdigit(c))
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
13c14
< 	while(c = *s++) {
---
> 	while((c = *s++)) {
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
33c32
< if( stat(name,&stbuff) < 0)
---
> if( stat(name,&stbuff) < 0) {
40a40
> 	}
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
46a49,54
> 	/* POSIX `tr -s STRING1` (no STRING2) squeezes runs of characters
> 	 * listed in STRING1.  v7 tr's loop expects STRING2 to populate the
> 	 * squeez[] table, so when only one string is given but -s is set,
> 	 * mirror STRING1 into STRING2 so the squeeze tags land correctly. */
> 	if(sflag && argc==1 && !dflag && !cflag)
> 		string2.p = argv[0];
50c58
< 		while(c = next(&string1))
---
> 		while((c = next(&string1)))
71c79
< 	while(d = next(&string2))
---
> 	while((d = next(&string2)))
81c89
< 		if(c = code[c&0377]&0377)
---
> 		if((c = code[c&0377]&0377))
88,89c96,97
< next(s)
< struct string *s;
---
> int
> next(struct string *s)
114,115c122,123
< nextc(s)
< struct string *s;
---
> int
> nextc(struct string *s)
117c125
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
20,21c20,22
< 	{"_msgbuf"},
< 	{"_msgbufp"}
---
> 	{"_msgbuf",  0, 0},
> 	{"_msgbufp", 0, 0},
> 	{"",         0, 0}
24,25c25,29
< main(argc, argv)
< char **argv;
---
> int done(char *);
> int pdate(void);
> 
> int
> main(int argc, char **argv)
84,85c88,89
< done(s)
< char *s;
---
> int
> done(char *s)
99a104
> 	return(0);
102c107,108
< pdate()
---
> int
> pdate(void)
104,105c110,111
< 	extern char *ctime();
< 	static firstime;
---
> 	extern char *ctime(long *t);
> 	static int firstime;
112a119
> 	return(0);
```

### cmd/du.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/du.c unix-v7-c99/cmd/du.c || true
```

Expect:

```
17,19c17,19
< long	descend();
< char	*rindex();
< char	*strcpy();
---
> long	descend(char *np, char *fname);
> char	*rindex(char *sp, int c);
> char	*strcpy(char *a, char *b);
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
43c43
< 		if(np = rindex(name, '/')) {
---
> 		if((np = rindex(name, '/'))) {
60,61c60
< descend(np, fname)
< char *np, *fname;
---
> descend(char *np, char *fname)
81c80
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
11,12c11,14
< main(argc, argv)
< char *argv[];
---
> int atoi(char *s);
> void exit(int n);
> int
> main(int argc, char *argv[])
14c16
< 	register i, c, f;
---
> 	register int i, c, f;
56c58
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
29,32c30,39
< struct nodelist *index();
< struct nodelist *findloop();
< struct nodelist *mark();
< char *malloc();
---
> struct nodelist *index(char *s);
> struct nodelist *findloop(void);
> struct nodelist *mark(struct nodelist *i);
> char *malloc(unsigned n);
> int present(struct nodelist *i, struct nodelist *j);
> int anypred(struct nodelist *i);
> int cmp(char *s, char *t);
> void error(char *s, char *t);
> void note(char *s, char *t);
> void exit(int n);
38,39c45,46
< main(argc,argv)
< char **argv;
---
> int
> main(int argc, char **argv)
86,87c93,94
< present(i,j)
< struct nodelist *i, *j;
---
> int
> present(struct nodelist *i, struct nodelist *j)
98,99c105,106
< anypred(i)
< struct nodelist *i;
---
> int
> anypred(struct nodelist *i)
111,112c118
< index(s)
< register char *s;
---
> index(register char *s)
129c135,136
< 	while(*t++ = *s++);
---
> 	while((*t++ = *s++))
> 		;
133,134c140,141
< cmp(s,t)
< register char *s, *t;
---
> int
> cmp(register char *s, register char *t)
145,146c152,153
< error(s,t)
< char *s, *t;
---
> void
> error(char *s, char *t)
152,153c159,160
< note(s,t)
< char *s,*t;
---
> void
> note(char *s, char *t)
162c169
< findloop()
---
> findloop(void)
174c181
< 				error("error 1");
---
> 				error("error 1",empty);
185c192
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
23,24c23,34
< main(argc, argv)
< char **argv;
---
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
> main(int argc, char **argv)
56,57c66,67
< type(file)
< char *file;
---
> void
> type(char *file)
104c114
< 
---
> 		/* fallthrough */
238c248
< 		/*.... */
---
> 		.... */
242,243c252,253
< lookup(tab)
< char *tab[];
---
> int
> lookup(char *tab[])
260c270,271
< ccom(){
---
> int
> ccom(void){
275c286,287
< ascom(){
---
> int
> ascom(void){
284,285c296,297
< english (bp, n)
< char *bp;
---
> int
> english (char *bp, int n)
```

### cmd/join.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/join.c unix-v7-c99/cmd/join.c || true
```

Expect:

```
25,26c25,32
< main(argc, argv)
< char *argv[];
---
> int input(int n);
> void output(int on1, int on2);
> void error(char *s1, char *s2, char *s3, char *s4, char *s5);
> int cmp(char *s1, char *s2);
> int atoi(char *s);
> void exit(int n);
> int
> main(int argc, char *argv[])
31c37
< 	long ftell();
---
> 	long ftell(FILE *iop);
88c94
< 		error("usage: join [-j1 x -j2 y] [-o list] file1 file2");
---
> 		error("usage: join [-j1 x -j2 y] [-o list] file1 file2", 0, 0, 0, 0);
96c102
< 		error("can't open %s", argv[1]);
---
> 		error("can't open %s", argv[1], 0, 0, 0);
98c104
< 		error("can't open %s", argv[2]);
---
> 		error("can't open %s", argv[2], 0, 0, 0);
105,106c111,112
< 	while(n1>0 && n2>0 || aflg!=0 && n1+n2>0) {
< 		if(n1>0 && n2>0 && comp()>0 || n1==0) {
---
> 	while((n1>0 && n2>0) || (aflg!=0 && n1+n2>0)) {
> 		if((n1>0 && n2>0 && comp()>0) || n1==0) {
110c116
< 		} else if(n1>0 && n2>0 && comp()<0 || n2==0) {
---
> 		} else if((n1>0 && n2>0 && comp()<0) || n2==0) {
126c132
< 				} else if(n1>0 && n2>0 && comp()<0 || n2==0) {
---
> 				} else if((n1>0 && n2>0 && comp()<0) || n2==0) {
141a148
> int
142a150
> int n;
169a178
> void
188,189c197,198
< 			if(olistf[i]==F1 && on1<=olist[i] ||
< 			   olistf[i]==F2 && on2<=olist[i] ||
---
> 			if((olistf[i]==F1 && on1<=olist[i]) ||
> 			   (olistf[i]==F2 && on2<=olist[i]) ||
201,202c210,211
< error(s1, s2, s3, s4, s5)
< char *s1;
---
> void
> error(char *s1, char *s2, char *s3, char *s4, char *s5)
210,211c219,220
< cmp(s1, s2)
< char *s1, *s2;
---
> int
> cmp(char *s1, char *s2)
```

### cmd/pr.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/pr.c unix-v7-c99/cmd/pr.c || true
```

Expect:

```
41,45c41,55
< char	*ttyname();
< char	*ctime();
< 
< main(argc, argv)
< char **argv;
---
> char	*ttyname(int f);
> char	*ctime(long *t);
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
195c204
< 	while (mflg&&nofile || (!mflg)&&tpgetc(ncol)>0) {
---
> 	while ((mflg&&nofile) || ((!mflg)&&tpgetc(ncol)>0)) {
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
21c21
< char	*sbrk();
---
> char	*sbrk(int);
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
143,145c153,154
< main(argc, argv)
< int	argc;
< char	**argv;
---
> int
> main(int argc, char **argv)
147c156
< 	int (*conv)();
---
> 	void (*conv)();
149,150c158
< 	register c;
< 	int ebcdic(), ibm(), ascii(), null(), cnull(), term();
---
> 	register int c;
281c289
< 		signal(SIGINT, term);
---
> 		signal(SIGINT, (int)term);
345c353,354
< flsh()
---
> void
> flsh(void)
347c356
< 	register c;
---
> 	register int c;
362,363c371,372
< match(s)
< char *s;
---
> int
> match(char *s)
380c389,390
< number(big)
---
> int
> number(int big)
408c418
< 
---
> 		/* fallthrough */
419c429,430
< cnull(cc)
---
> void
> cnull(int cc)
421c432
< 	register c;
---
> 	register int c;
431c442,443
< null(c)
---
> void
> null(int c)
442c454,455
< ascii(cc)
---
> void
> ascii(int cc)
444c457
< 	register c;
---
> 	register int c;
469c482,483
< ebcdic(cc)
---
> void
> ebcdic(int cc)
471c485
< 	register c;
---
> 	register int c;
498c512,513
< ibm(cc)
---
> void
> ibm(int cc)
500c515
< 	register c;
---
> 	register int c;
527c542,543
< term()
---
> void
> term(void)
534c550,551
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
76d75
< FILE *fopen();
106c105
< char *mktemp();
---
> char *mktemp(char *as);
107a107,129
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
> static int	diff_isspace(int c);
109c131,138
< done()
---
> static int
> diff_isspace(int c)
> {
> 	return(c==' ' || c=='\t' || c=='\n' || c=='\v' || c=='\r' || c=='\f');
> }
> 
> void
> done(void)
115c144
< char *talloc(n)
---
> char *talloc(int n)
117c146
< 	extern char *malloc();
---
> 	extern char *malloc(unsigned n);
122a152
> 	return(NULL);
125,126c155
< char *ralloc(p,n)	/*compacting reallocation */
< char *p;
---
> char *ralloc(char *p, int n)	/*compacting reallocation */
129c158
< 	char *realloc();
---
> 	char *realloc(char *p, unsigned n);
139c168,169
< noroom()
---
> void
> noroom(void)
145,146c175,176
< sort(a,n)	/*shellsort CACM #201*/
< struct line *a;
---
> void
> sort(struct line *a, int n)	/*shellsort CACM #201*/
163,164c193,194
< 				   aim->value == ai[0].value &&
< 				   aim->serial > ai[0].serial)
---
> 				   (aim->value == ai[0].value &&
> 				    aim->serial > ai[0].serial))
177,179c207,208
< unsort(f, l, b)
< struct line *f;
< int *b;
---
> void
> unsort(struct line *f, int l, int *b)
191,192c220,221
< filename(pa1, pa2)
< char **pa1, **pa2;
---
> void
> filename(char **pa1, char **pa2)
202c231,232
< 		while(*b1++ = *a1++) ;
---
> 		while((*b1++ = *a1++))
> 			;
205c235
< 		while(*a1++ = *a2++)
---
> 		while((*a1++ = *a2++))
210,213c240,243
< 		signal(SIGHUP,done);
< 		signal(SIGINT,done);
< 		signal(SIGPIPE,done);
< 		signal(SIGTERM,done);
---
> 		signal(SIGHUP,(int)done);
> 		signal(SIGINT,(int)done);
> 		signal(SIGPIPE,(int)done);
> 		signal(SIGTERM,(int)done);
225,226c255,256
< prepare(i, arg)
< char *arg;
---
> void
> prepare(int i, char *arg)
229c259
< 	register j,h;
---
> 	register int j,h;
235c265
< 	for(j=0; h=readhash(input[i]);) {
---
> 	for(j=0; (h=readhash(input[i]));) {
244c274,275
< prune()
---
> void
> prune(void)
246c277
< 	register i,j;
---
> 	register int i,j;
261,263c292,293
< equiv(a,n,b,m,c)
< struct line *a, *b;
< int *c;
---
> void
> equiv(struct line *a, int n, struct line *b, int m, int *c)
289,290c319,320
< main(argc, argv)
< char **argv;
---
> int
> main(int argc, char **argv)
358,361c388,389
< stone(a,n,b,c)
< int *a;
< int *b;
< int *c;
---
> int
> stone(int *a, int n, int *b, int *c)
399c427,428
< newcand(x,y,pred)
---
> int
> newcand(int x, int y, int pred)
410,411c439,440
< search(c, k, y)
< int *c;
---
> int
> search(int *c, int k, int y)
431c460,461
< unravel(p)
---
> void
> unravel(int p)
448,449c478,479
< check(argv)
< char **argv;
---
> void
> check(char **argv)
454c484
< 	char c,d;
---
> 	int c,d;
475c505
< 			if(bflag && isspace(c) && isspace(d)) {
---
> 			if(bflag && diff_isspace(c) && diff_isspace(d)) {
479c509
< 				} while(isspace(c=getc(input[0])));
---
> 				} while(diff_isspace(c=getc(input[0])));
483c513
< 				} while(isspace(d=getc(input[1])));
---
> 				} while(diff_isspace(d=getc(input[1])));
512c542,543
< skipline(f)
---
> int
> skipline(int f)
514c545
< 	register i;
---
> 	register int i;
519,520c550,551
< output(argv)
< char **argv;
---
> void
> output(char **argv)
551c582,583
< change(a,b,c,d)
---
> void
> change(int a, int b, int c, int d)
572,573c604,605
< range(a,b,separator)
< char *separator;
---
> void
> range(int a, int b, char *separator)
581,584c613,614
< fetch(f,a,b,lb,s)
< long *f;
< FILE *lb;
< char *s;
---
> void
> fetch(long *f, int a, int b, FILE *lb, char *s)
602,603c632,633
< readhash(f)
< FILE *f;
---
> int
> readhash(FILE *f)
607,608c637,638
< 	register space;
< 	register t;
---
> 	register int space;
> 	register int t;
617,618c647,648
< 		switch(t=getc(f)) {
< 		case -1:
---
> 		t = getc(f);
> 		if(t == -1)
620,621c650,652
< 		case '\t':
< 		case ' ':
---
> 		if(t == '\n')
> 			break;
> 		if(diff_isspace(t)) {
624,629c655,656
< 		default:
< 			if(space) {
< 				shift += 7;
< 				space = 0;
< 			}
< 			sum += (long)t << (shift%=HALFLONG);
---
> 		}
> 		if(space) {
631,633c658
< 			continue;
< 		case '\n':
< 			break;
---
> 			space = 0;
635c660,661
< 		break;
---
> 		sum += (long)t << (shift%=HALFLONG);
> 		shift += 7;
641,642c667,668
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
11,12c11,12
< char	*strcat();
< char	*strcpy();
---
> char	*strcat(char *a, char *b);
> char	*strcpy(char *a, char *b);
20,21c20,21
< char	*ttyname();
< char	*rindex(), *index();
---
> char	*ttyname(int f);
> char	*rindex(char *sp, int c), *index(register char *sp, int c);
23,24c23,26
< int	eof();
< int	timout();
---
> int	eof(void);
> int	timout(void);
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
33,34c38,39
< main(argc, argv)
< char *argv[];
---
> int
> main(int argc, char *argv[])
36c41
< 	register i;
---
> 	register int i;
65,66c70,71
< check(file)
< char *file;
---
> int
> check(char *file)
68,69c73,74
< 	register i;
< 	register j;
---
> 	register int i;
> 	register int j;
75c80
< 		return;
---
> 			return(0);
91c96
< 	for (i=0; i<=nfiles; i++)
---
> 	for (i=0; i<=(int)nfiles; i++)
117a123
> 	return(0);
120,121c126,127
< pass1(ip)
< register struct dinode *ip;
---
> int
> pass1(register struct dinode *ip)
126c132
< 	register i, j;
---
> 	register int i, j;
132c138
< 		return;
---
> 		return(0);
142c148
< 		for(j=0; j<NDIR; j++) {
---
> 		for(j=0; j<(int)NDIR; j++) {
164a171
> 	return(0);
167,168c174,175
< pass2(ip)
< register struct dinode *ip;
---
> int
> pass2(register struct dinode *ip)
170c177
< 	register i;
---
> 	register int i;
174c181
< 		return;
---
> 		return(0);
176c183
< 		return;
---
> 		return(0);
178c185
< 		return;
---
> 		return(0);
184a192
> 	return(0);
187,189c195,196
< bread(bno, buf, cnt)
< daddr_t bno;
< char *buf;
---
> int
> bread(daddr_t bno, char *buf, int cnt)
191c198
< 	register i;
---
> 	register int i;
198a206
> 	return(0);
203c211
< bmap(i)
---
> bmap(int i)
210c218
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
41,42c41,51
< long	atol();
< daddr_t	alloc();
---
> long	atol(register char *p);
> daddr_t	alloc(void);
> int	check(char *file);
> int	pass1(struct dinode *ip);
> int	chk(daddr_t bno, char *s);
> int	duped(daddr_t bno);
> int	bfree(daddr_t bno);
> int	bread(daddr_t bno, char *buf, int cnt);
> int	bwrite(daddr_t bno, char *buf);
> int	makefree(void);
> int	l3tol(long *lp, char *cp, int n);
44c53
< char	*malloc();
---
> char	*malloc(unsigned n);
47,48c56,57
< main(argc, argv)
< char *argv[];
---
> int
> main(int argc, char *argv[])
50c59
< 	register i;
---
> 	register int i;
101,102c110,111
< check(file)
< char *file;
---
> int
> check(char *file)
104c113
< 	register i, j;
---
> 	register int i, j;
113c122
< 		return;
---
> 		return(0);
134c143
< 	if (n != (unsigned)n) {
---
> 	if (n != (long)(unsigned)n) {
149c158
< 	for(i=0; i<(unsigned)n; i++)
---
> 	for(i=0; i<(int)(unsigned)n; i++)
174c183
< 		return;
---
> 		return(0);
177c186
< 	while(n = alloc()) {
---
> 	while((n = alloc())) {
215a225
> 	return(0);
218,219c228,229
< pass1(ip)
< register struct dinode *ip;
---
> int
> pass1(register struct dinode *ip)
224c234
< 	register i, j;
---
> 	register int i, j;
230c240
< 		return;
---
> 		return(0);
234c244
< 		return;
---
> 		return(0);
238c248
< 		return;
---
> 		return(0);
246c256
< 		return;
---
> 		return(0);
261c271
< 		for(j=0; j<NINDIR; j++) {
---
> 		for(j=0; j<(int)NINDIR; j++) {
273c283
< 			for(k=0; k<NINDIR; k++) {
---
> 			for(k=0; k<(int)NINDIR; k++) {
285c295
< 				for(l=0; l<NINDIR; l++)
---
> 				for(l=0; l<(int)NINDIR; l++)
292a303
> 	return(0);
295,297c306,307
< chk(bno, s)
< daddr_t bno;
< char *s;
---
> int
> chk(daddr_t bno, char *s)
299c309
< 	register n;
---
> 	register int n;
315,316c325,326
< duped(bno)
< daddr_t bno;
---
> int
> duped(daddr_t bno)
319c329
< 	register m, n;
---
> 	register int m, n;
333c343
< alloc()
---
> alloc(void)
355c365
< 		sblock.s_nfree = buf.df_nfree;
---
> 		sblock.s_nfree = buf.fb.df_nfree;
363c373
< 			sblock.s_free[i] = buf.df_free[i];
---
> 			sblock.s_free[i] = buf.fb.df_free[i];
368,369c378,379
< bfree(bno)
< daddr_t bno;
---
> int
> bfree(daddr_t bno)
381c391
< 		buf.df_nfree = sblock.s_nfree;
---
> 		buf.fb.df_nfree = sblock.s_nfree;
383c393
< 			buf.df_free[i] = sblock.s_free[i];
---
> 			buf.fb.df_free[i] = sblock.s_free[i];
388a399
> 	return(0);
391,393c402,403
< bread(bno, buf, cnt)
< daddr_t bno;
< char *buf;
---
> int
> bread(daddr_t bno, char *buf, int cnt)
395c405
< 	register i;
---
> 	register int i;
406a417
> 	return(0);
409,411c420,421
< bwrite(bno, buf)
< daddr_t bno;
< char	*buf;
---
> int
> bwrite(daddr_t bno, char *buf)
416a427
> 	return(0);
419c430,431
< makefree()
---
> int
> makefree(void)
423c435
< 	register i, j;
---
> 	register int i, j;
474c486
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
39,40c45,54
< main(argc, argv)
< char *argv[];
---
> int	stats(int);
> int	stat1(int);
> int	stats2(double);
> int	stats3(double);
> int	biostats(void);
> int	atoi(char *);
> int	nlist(char *, struct nlent *);
> 
> int
> main(int argc, char *argv[])
42,43c56,57
< 	extern char *ctime();
< 	register  i;
---
> 	extern char *ctime(long *t);
> 	register  int i;
49c63
< 	if(nl[0].type == -1) {
---
> 	if(nl[0].type == 0) {
88a103,106
> 	/* The v7 original assumed dk_busy/etime/numb/wds/tin/tout were
> 	 * laid out contiguously in kernel .bss so a single read() filled
> 	 * `s`.  ELF link order doesn't honour that, so read each symbol
> 	 * individually into the matching slot. */
90c108,128
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
91a130
> 		if (i >= 32) break;
139a179
> 	return(0);
149c189,190
< stats(dn)
---
> int
> stats(int dn)
151c192
< 	register i;
---
> 	register int i;
165c206
< 		return;
---
> 		return(0);
172a214,223
> 	/* v7-era arithmetic artifact: f1 is the disk-busy time sampled by
> 	 * the HZ-tick clock IRQ (clock.c's `dk_time[dk_busy&07]++`).  The
> 	 * v7 RK/RF/RP drivers held dk_busy across the seek+transfer (tens
> 	 * of ms), so f1 was always >= the f4*f3 model term.  This port's
> 	 * virtio_blk strategy is a synchronous busy-wait that finishes in
> 	 * microseconds -- almost always inside a single clock tick -- so
> 	 * f1 is usually 0 even with non-zero numb/wds, and f5 = f1 - f4*f3
> 	 * comes out negative (and f6 = -f5).  v7 doesn't clamp, and we
> 	 * deliberately don't either, so the printed msps/mspt match what
> 	 * the original code would have produced on the same inputs. */
175a227
> 	return(0);
178c230,231
< stat1(o)
---
> int
> stat1(int o)
180c233
< 	register i;
---
> 	register int i;
194a248
> 	return(0);
197,198c251,252
< stats2(t)
< double t;
---
> int
> stats2(double t)
200c254
< 	register i, j;
---
> 	register int i, j;
206a261
> 	return(0);
209,210c264,265
< stats3(t)
< double t;
---
> int
> stats3(double t)
212c267
< 	register i;
---
> 	register int i;
251a307
> 	return(0);
254c310,311
< biostats()
---
> int
> biostats(void)
256c313
< register i;
---
> 	register int i;
257a315,316
> 	if (nl[1].type == 0)
> 		return(0);
270a330
> 	return(0);
```

### cmd/ncheck.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/ncheck.c unix-v7-c99/cmd/ncheck.c || true
```

Expect:

```
37,39c37,47
< daddr_t	bmap();
< long	atol();
< struct htab *lookup();
---
> daddr_t	bmap(int i);
> long	atol(register char *p);
> struct htab *lookup(ino_t i, int ef);
> int	check(char *file);
> int	pass1(struct dinode *ip);
> int	pass2(struct dinode *ip);
> int	pass3(struct dinode *ip);
> int	dotname(struct direct *dp);
> int	pname(int i, int lev);
> int	bread(daddr_t bno, char *buf, int cnt);
> int	l3tol(long *lp, char *cp, int n);
41,42c49,50
< main(argc, argv)
< char *argv[];
---
> int
> main(int argc, char *argv[])
44c52
< 	register i;
---
> 	register int i;
81,82c89,90
< check(file)
< char *file;
---
> int
> check(char *file)
84c92
< 	register i, j;
---
> 	register int i, j;
91c99
< 		return;
---
> 		return(0);
134a143
> 	return(0);
137,138c146,147
< pass1(ip)
< register struct dinode *ip;
---
> int
> pass1(register struct dinode *ip)
142c151
< 			return;
---
> 			return(0);
144c153
< 		  || ip->di_mode&(ISUID|ISGID))
---
> 		  || ip->di_mode&(ISUID|ISGID)) {
146c155,157
< 			return;
---
> 			return(0);
> 		}
> 		return(0);
148a160
> 	return(0);
151,152c163,164
< pass2(ip)
< register struct dinode *ip;
---
> int
> pass2(register struct dinode *ip)
157c169
< 	register i, j;
---
> 	register int i, j;
164c176
< 		return;
---
> 		return(0);
174c186
< 		for(j=0; j<NDIR; j++) {
---
> 		for(j=0; j<(int)NDIR; j++) {
191a204
> 	return(0);
194,195c207,208
< pass3(ip)
< register struct dinode *ip;
---
> int
> pass3(register struct dinode *ip)
200c213
< 	register i, j;
---
> 	register int i, j;
206c219
< 		return;
---
> 		return(0);
216c229
< 		for(j=0; j<NDIR; j++) {
---
> 		for(j=0; j<(int)NDIR; j++) {
240a254
> 	return(0);
243,244c257,258
< dotname(dp)
< register struct direct *dp;
---
> int
> dotname(register struct direct *dp)
253,254c267,268
< pname(i, lev)
< ino_t i;
---
> int
> pname(int i, int lev)
259c273
< 		return;
---
> 		return(0);
262c276
< 		return;
---
> 		return(0);
266c280
< 		return;
---
> 		return(0);
269a284
> 	return(0);
273,274c288
< lookup(i, ef)
< ino_t i;
---
> lookup(ino_t i, int ef)
294,296c308,309
< bread(bno, buf, cnt)
< daddr_t bno;
< char *buf;
---
> int
> bread(daddr_t bno, char *buf, int cnt)
298c311
< 	register i;
---
> 	register int i;
305a319
> 	return(0);
309c323
< bmap(i)
---
> bmap(int i)
316c330
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
33,38c34,36
< struct	anode	*exp(),
< 		*e1(),
< 		*e2(),
< 		*e3(),
< 		*mk();
< char	*nxtarg();
---
> struct	anode	*exp(void), *e1(void), *e2(void), *e3(void);
> struct	anode	*mk(int (*f)(), struct anode *l, struct anode *r);
> char	*nxtarg(void);
41,43c39,54
< char *rindex();
< char *sbrk();
< main(argc, argv) char *argv[];
---
> char *rindex(char *sp, int c);
> char *sbrk(int);
> int	pr(char *s);
> int	gethome(void);
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
> main(int argc, char *argv[])
48d58
< 	FILE *pwd, *popen();
51,54c61
< 	pwd = popen("pwd", "r");
< 	fgets(Home, 128, pwd);
< 	pclose(pwd);
< 	Home[strlen(Home) - 1] = '\0';
---
> 	gethome();
77c84
< 		if(cp = rindex(Pathname, '/')) {
---
> 		if((cp = rindex(Pathname, '/'))) {
99,100c106,107
< struct anode *exp() { /* parse ALTERNATION (-o)  */
< 	int or();
---
> struct anode *exp(void) { /* parse ALTERNATION (-o)  */
> 	int or(register struct anode *p);
111,112c118,119
< struct anode *e1() { /* parse CONCATENATION (formerly -a) */
< 	int and();
---
> struct anode *e1(void) { /* parse CONCATENATION (formerly -a) */
> 	int and(register struct anode *p);
128,129c135,136
< struct anode *e2() { /* parse NOT (!) */
< 	int not();
---
> struct anode *e2(void) { /* parse NOT (!) */
> 	int not(register struct anode *p);
141,144c148,153
< struct anode *e3() { /* parse parens and predicates */
< 	int exeq(), ok(), glob(),  mtime(), atime(), ctime(), user(),
< 		group(), size(), perm(), links(), print(),
< 		type(), ino(), cpio(), newer();
---
> struct anode *e3(void) { /* parse parens and predicates */
> 	int exeq(void *vp), ok(void *vp), glob(void *vp);
> 	int mtime(void *vp), atime(void *vp), ctime(void *vp);
> 	int user(void *vp), group(void *vp), size(void *vp), perm(void *vp);
> 	int links(void *vp), print(void), type(void *vp), ino(void *vp);
> 	int cpio(void), newer(void);
166c175
< 		return(mk(mtime, (struct anode *)atoi(b), (struct anode *)s));
---
> 		return(mk(mtime, (struct anode *)(long)atoi(b), (struct anode *)(long)s));
168c177
< 		return(mk(atime, (struct anode *)atoi(b), (struct anode *)s));
---
> 		return(mk(atime, (struct anode *)(long)atoi(b), (struct anode *)(long)s));
170c179
< 		return(mk(ctime, (struct anode *)atoi(b), (struct anode *)s));
---
> 		return(mk(ctime, (struct anode *)(long)atoi(b), (struct anode *)(long)s));
176c185
< 				return mk(user, (struct anode *)atoi(b), (struct anode *)s);
---
> 				return mk(user, (struct anode *)(long)atoi(b), (struct anode *)(long)s);
180c189
< 		return(mk(user, (struct anode *)i, (struct anode *)s));
---
> 		return(mk(user, (struct anode *)(long)i, (struct anode *)(long)s));
183c192
< 		return(mk(ino, (struct anode *)atoi(b), (struct anode *)s));
---
> 		return(mk(ino, (struct anode *)(long)atoi(b), (struct anode *)(long)s));
189c198
< 				return mk(group, (struct anode *)atoi(b), (struct anode *)s);
---
> 				return mk(group, (struct anode *)(long)atoi(b), (struct anode *)(long)s);
193c202
< 		return(mk(group, (struct anode *)i, (struct anode *)s));
---
> 		return(mk(group, (struct anode *)(long)i, (struct anode *)(long)s));
195c204
< 		return(mk(size, (struct anode *)atoi(b), (struct anode *)s));
---
> 		return(mk(size, (struct anode *)(long)atoi(b), (struct anode *)(long)s));
197c206
< 		return(mk(links, (struct anode *)atoi(b), (struct anode *)s));
---
> 		return(mk(links, (struct anode *)(long)atoi(b), (struct anode *)(long)s));
204c213
< 		return(mk(perm, (struct anode *)i, (struct anode *)s));
---
> 		return(mk(perm, (struct anode *)(long)i, (struct anode *)(long)s));
226c235
< 			pr("find: cannot create "), pr(s), pr("\n");
---
> 			pr("find: cannot create "), pr(b), pr("\n");
242a252
> 	return(0);
244,246c254
< struct anode *mk(f, l, r)
< int (*f)();
< struct anode *l, *r;
---
> struct anode *mk(int (*f)(), struct anode *l, struct anode *r)
254,255c262,263
< char *nxtarg() { /* get next arg from command line */
< 	static strikes = 0;
---
> char *nxtarg(void) { /* get next arg from command line */
> 	static int strikes = 0;
270,271c278,279
< and(p)
< register struct anode *p;
---
> int
> and(register struct anode *p)
275,276c283,284
< or(p)
< register struct anode *p;
---
> int
> or(register struct anode *p)
280,281c288,289
< not(p)
< register struct anode *p;
---
> int
> not(register struct anode *p)
285,286c293,294
< glob(p)
< register struct { int f; char *pat; } *p; 
---
> int
> glob(void *vp)
287a296
> 	struct { int f; char *pat; } *p = vp;
290c299,300
< print()
---
> int
> print(void)
295,296c305,306
< mtime(p)
< register struct { int f, t, s; } *p; 
---
> int
> mtime(void *vp)
297a308
> 	struct { int f, t, s; } *p = vp;
300,301c311,312
< atime(p)
< register struct { int f, t, s; } *p; 
---
> int
> atime(void *vp)
302a314
> 	struct { int f, t, s; } *p = vp;
305,306c317,318
< ctime(p)
< register struct { int f, t, s; } *p; 
---
> int
> ctime(void *vp)
307a320
> 	struct { int f, t, s; } *p = vp;
310,311c323,324
< user(p)
< register struct { int f, u, s; } *p; 
---
> int
> user(void *vp)
312a326
> 	struct { int f, u, s; } *p = vp;
315,316c329,330
< ino(p)
< register struct { int f, u, s; } *p;
---
> int
> ino(void *vp)
317a332
> 	struct { int f, u, s; } *p = vp;
320,321c335,336
< group(p)
< register struct { int f, u; } *p; 
---
> int
> group(void *vp)
322a338
> 	struct { int f, u; } *p = vp;
325,326c341,342
< links(p)
< register struct { int f, link, s; } *p; 
---
> int
> links(void *vp)
327a344
> 	struct { int f, link, s; } *p = vp;
330,331c347,348
< size(p)
< register struct { int f, sz, s; } *p; 
---
> int
> size(void *vp)
332a350
> 	struct { int f, sz, s; } *p = vp;
335,336c353,354
< perm(p)
< register struct { int f, per, s; } *p; 
---
> int
> perm(void *vp)
338c356,357
< 	register i;
---
> 	struct { int f, per, s; } *p = vp;
> 	register int i;
342,343c361,362
< type(p)
< register struct { int f, per, s; } *p;
---
> int
> type(void *vp)
344a364
> 	struct { int f, per, s; } *p = vp;
347,348c367,368
< exeq(p)
< register struct { int f, com; } *p;
---
> int
> exeq(void *vp)
349a370
> 	struct { int f, com; } *p = vp;
353,354c374,375
< ok(p)
< struct { int f, com; } *p;
---
> int
> ok(void *vp)
355a377
> 	struct { int f, com; } *p = vp;
373,374c395
< long mklong(v)
< short v[];
---
> long mklong(short v[])
383c404,405
< cpio()
---
> int
> cpio(void)
400c422
< 	register ifile, ct;
---
> 	register int ifile, ct;
402c424
< 	register i;
---
> 	register int i;
421c443
< 		return;
---
> 		return(0);
425c447
< 		return;
---
> 		return(0);
430c452
< 		return;
---
> 		return(0);
440c462
< 	return;
---
> 	return(0);
442c464,465
< newer()
---
> int
> newer(void)
448,450c471,503
< scomp(a, b, s) /* funny signed compare */
< register a, b;
< register char s;
---
> int
> gethome(void)
> {
> 	int fd[2], status;
> 	register int n;
> 
> 	if(pipe(fd) < 0) {
> 		pr("find: cannot run pwd\n");
> 		exit(1);
> 	}
> 	if(fork() == 0) {
> 		close(fd[0]);
> 		dup(fd[1] | 0100, 1);
> 		close(fd[1]);
> 		execl("/bin/pwd", "pwd", 0);
> 		exit(1);
> 	}
> 	close(fd[1]);
> 	n = read(fd[0], Home, sizeof Home - 1);
> 	close(fd[0]);
> 	wait(&status);
> 	if(n <= 0 || status) {
> 		pr("find: cannot run pwd\n");
> 		exit(1);
> 	}
> 	Home[n] = '\0';
> 	if(Home[n - 1] == '\n')
> 		Home[n - 1] = '\0';
> 	return(0);
> }
> 
> int
> scomp(register int a, register int b, register int s) /* funny signed compare */
459c512,513
< doex(com)
---
> int
> doex(int com)
461c515
< 	register np;
---
> 	register int np;
464c518
< 	static ccode;
---
> 	static int ccode;
467c521
< 	while (na=Argv[com++]) {
---
> 	while ((na=Argv[com++])) {
477c531
< 		execvp(nargv[0], nargv, np);
---
> 		execvp(nargv[0], nargv);
483,484c537,539
< getunum(f, s) char *f, *s; { /* find user/group name and return number */
< 	register i;
---
> int
> getunum(char *f, char *s) { /* find user/group name and return number */
> 	register int i;
486c541
< 	register c;
---
> 	register int c;
491a547,548
> 	if(pin == NULL)
> 		return(i);
515,517c572,573
< descend(name, fname, exlist)
< struct anode *exlist;
< char *name, *fname;
---
> int
> descend(char *name, char *fname, struct anode *exlist)
612,613c668,669
< gmatch(s, p) /* string match as in glob */
< register char *s, *p;
---
> int
> gmatch(register char *s, register char *p) /* string match as in glob */
619,620c675,676
< amatch(s, p)
< register char *s, *p;
---
> int
> amatch(register char *s, register char *p)
622c678
< 	register cc;
---
> 	register int cc;
632c688
< 		while (cc = *++p) {
---
> 		while ((cc = *++p)) {
642c698
< 				k |= lc <= scc & scc <= (cc=p[1]);
---
> 				k |= (lc <= scc) & (scc <= (cc=p[1]));
661,662c717,718
< umatch(s, p)
< register char *s, *p;
---
> int
> umatch(register char *s, register char *p)
670,672c726,727
< bwrite(rp, c)
< register short *rp;
< register c;
---
> int
> bwrite(register short *rp, register int c)
691a747
> 	return(0);
693c749,750
< chgreel(x, fl)
---
> int
> chgreel(int x, int fl)
695c752
< 	register f;
---
> 	register int f;
719,720c776,777
< pr(s)
< char *s;
---
> int
> pr(char *s)
722a780
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
24,27c25,28
< int	cmp(), cmpa();
< int	(*compare)() = cmpa;
< char	*eol();
< int	term();
---
> int	cmp(char *i, char *j), cmpa(register char *pa, register char *pb);
> int	(*compare)(char *, char *) = cmpa;
> char	*eol(register char *p);
> int	term(void);
160,162c161,163
< 	0,0,
< 	0,-1,
< 	0,0
---
> 	{0,0},
> 	{0,-1},
> 	{0,0}
166,168c167,185
< char	*setfil();
< char	*sbrk();
< char	*brk();
---
> char	*setfil(int i);
> char	*sbrk(int);
> char	*brk(char *);
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
170,171c187,188
< main(argc, argv)
< char **argv;
---
> int
> main(int argc, char **argv)
173c190
< 	register a;
---
> 	register int a;
199a217,248
> 			case 'k': {
> 				/* POSIX -k N (single-field form) -> v7 +N-1.
> 				 * -k 2 sorts by the second whitespace-separated
> 				 * field.  More complex forms (-k F1,F2) aren't
> 				 * supported; falls back to single field. */
> 				static char kbuf[16];
> 				char *kp;
> 				int n = 0;
> 				if (--argc <= 0) break;
> 				kp = *++argv;
> 				while (*kp >= '0' && *kp <= '9') {
> 					n = n*10 + (*kp++ - '0');
> 				}
> 				if (n > 0) {
> 					int v = n - 1, ki = 0;
> 					char tmp[12]; int ti = 0;
> 					if (v == 0) kbuf[ki++] = '0';
> 					else {
> 						while (v > 0) { tmp[ti++] = '0' + (v%10); v /= 10; }
> 						while (ti > 0) kbuf[ki++] = tmp[--ti];
> 					}
> 					kbuf[ki] = '\0';
> 					if (++nfields >= NF) {
> 						diag("too many keys","");
> 						exit(1);
> 					}
> 					copyproto();
> 					field(kbuf, 0);
> 				}
> 				continue;
> 			}
> 
239a289
> 	ep = (char *)lspace + MEM;
245c295
< 	nlines /= (5*(sizeof(char *)/sizeof(char)));
---
> 	nlines /= (5*(sizeof(char *)));
262c312
< 	signal(SIGHUP, term);
---
> 	signal(SIGHUP, (int)term);
264,266c314,316
< 		signal(SIGINT, term);
< 	signal(SIGPIPE,term);
< 	signal(SIGTERM,term);
---
> 		signal(SIGINT, (int)term);
> 	signal(SIGPIPE,(int)term);
> 	signal(SIGTERM,(int)term);
272c322
< 	for(a = mflg|cflg?0:eargc; a+N<nfiles || unsafeout&&a<eargc; a=i) {
---
> 	for(a = (mflg|cflg)?0:eargc; a+N<nfiles || (unsafeout&&a<eargc); a=i) {
284a335
> 	return(0);
287c338,339
< sort()
---
> int
> sort(void)
291c343
< 	register c;
---
> 	register int c;
341a394
> 	return(0);
350c403,404
< merge(a,b)
---
> int
> merge(int a, int b)
354c408
< 	register	i;
---
> 	register int	i;
392c446
< 	muflg = mflg & uflg | cflg;
---
> 	muflg = (mflg & uflg) | cflg;
441a496
> 	return(0);
444,445c499,500
< rline(mp)
< struct merg *mp;
---
> int
> rline(struct merg *mp)
450c505
< 	register c;
---
> 	register int c;
466,467c521,522
< disorder(s,t)
< char *s, *t;
---
> int
> disorder(char *s, char *t)
473a529
> 	return(0);
476c532,533
< newfile()
---
> int
> newfile(void)
485a543
> 	return(0);
489c547
< setfil(i)
---
> setfil(int i)
492c550
< 	if(i < eargc)
---
> 	if(i < eargc) {
496a555
> 	}
503c562,563
< oldfile()
---
> int
> oldfile(void)
512a573
> 	return(0);
515c576,577
< safeoutfil()
---
> int
> safeoutfil(void)
521c583
< 		return;
---
> 		return(0);
523c585
< 		return;
---
> 		return(0);
530a593
> 	return(0);
533,534c596,597
< cant(f)
< char *f;
---
> int
> cant(char *f)
538a602
> 	return(0);
541,542c605,606
< diag(s,t)
< char *s, *t;
---
> int
> diag(char *s, char *t)
547a612
> 	return(0);
550c615,616
< term()
---
> int
> term(void)
552c618
< 	register i;
---
> 	register int i;
562a629
> 	return(0);
565,566c632,633
< cmp(i, j)
< char *i, *j;
---
> int
> cmp(char *i, char *j)
569c636
< 	char *skip();
---
> 	char *skip(char *pp, struct field *fp, int j);
613c680
< 					if(b = *--ipb - *--ipa)
---
> 					if((b = *--ipb - *--ipa))
629c696
< 					if(a = *pb++ - *pa++)
---
> 					if((a = *pb++ - *pa++))
642c709
< 		while(ignore[*pa])
---
> 		while(ignore[(unsigned char)*pa])
644c711
< 		while(ignore[*pb])
---
> 		while(ignore[(unsigned char)*pb])
646c713
< 		if(pa>=la || *pa=='\n')
---
> 		if(pa>=la || *pa=='\n') {
649a717
> 		}
652c720
< 		if((sa = code[*pb++]-code[*pa++]) == 0)
---
> 		if((sa = code[(unsigned char)*pb++]-code[(unsigned char)*pa++]) == 0)
661,662c729,730
< cmpa(pa, pb)
< register char *pa, *pb;
---
> int
> cmpa(register char *pa, register char *pb)
678,680c746
< skip(pp, fp, j)
< struct field *fp;
< char *pp;
---
> skip(char *pp, struct field *fp, int j)
682c748
< 	register i;
---
> 	register int i;
718,719c784
< eol(p)
< register char *p;
---
> eol(register char *p)
725c790,791
< copyproto()
---
> int
> copyproto(void)
727c793
< 	register i;
---
> 	register int i;
732c798
< 	for(i=0; i<sizeof(proto)/sizeof(*p); i++)
---
> 	for(i=0; i<(int)(sizeof(proto)/sizeof(*p)); i++)
733a800
> 	return(0);
736,737c803,804
< field(s,k)
< char *s;
---
> int
> field(char *s, int k)
740c807
< 	register d;
---
> 	register int d;
746c813
< 			return;
---
> 			return(0);
790c857
< 
---
> 			/* fallthrough */
795a863
> 	return(0);
798,799c866,867
< number(ppa)
< char **ppa;
---
> int
> number(char **ppa)
812c880,881
< blank(c)
---
> int
> blank(int c)
822,823c891,892
< qsort(a,l)
< char **a, **l;
---
> int
> qsort(char **a, char **l)
836c905
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
> static void
> setkey(char *key)
100c100
< 	register i, j, k;
---
> 	register int i, j, k;
146c146
< static	char	e[] {
---
> static	char	e[] = {
162,201c162,201
< static	char	S[8][64] {
< 	14, 4,13, 1, 2,15,11, 8, 3,10, 6,12, 5, 9, 0, 7,
< 	 0,15, 7, 4,14, 2,13, 1,10, 6,12,11, 9, 5, 3, 8,
< 	 4, 1,14, 8,13, 6, 2,11,15,12, 9, 7, 3,10, 5, 0,
< 	15,12, 8, 2, 4, 9, 1, 7, 5,11, 3,14,10, 0, 6,13,
< 
< 	15, 1, 8,14, 6,11, 3, 4, 9, 7, 2,13,12, 0, 5,10,
< 	 3,13, 4, 7,15, 2, 8,14,12, 0, 1,10, 6, 9,11, 5,
< 	 0,14, 7,11,10, 4,13, 1, 5, 8,12, 6, 9, 3, 2,15,
< 	13, 8,10, 1, 3,15, 4, 2,11, 6, 7,12, 0, 5,14, 9,
< 
< 	10, 0, 9,14, 6, 3,15, 5, 1,13,12, 7,11, 4, 2, 8,
< 	13, 7, 0, 9, 3, 4, 6,10, 2, 8, 5,14,12,11,15, 1,
< 	13, 6, 4, 9, 8,15, 3, 0,11, 1, 2,12, 5,10,14, 7,
< 	 1,10,13, 0, 6, 9, 8, 7, 4,15,14, 3,11, 5, 2,12,
< 
< 	 7,13,14, 3, 0, 6, 9,10, 1, 2, 8, 5,11,12, 4,15,
< 	13, 8,11, 5, 6,15, 0, 3, 4, 7, 2,12, 1,10,14, 9,
< 	10, 6, 9, 0,12,11, 7,13,15, 1, 3,14, 5, 2, 8, 4,
< 	 3,15, 0, 6,10, 1,13, 8, 9, 4, 5,11,12, 7, 2,14,
< 
< 	 2,12, 4, 1, 7,10,11, 6, 8, 5, 3,15,13, 0,14, 9,
< 	14,11, 2,12, 4, 7,13, 1, 5, 0,15,10, 3, 9, 8, 6,
< 	 4, 2, 1,11,10,13, 7, 8,15, 9,12, 5, 6, 3, 0,14,
< 	11, 8,12, 7, 1,14, 2,13, 6,15, 0, 9,10, 4, 5, 3,
< 
< 	12, 1,10,15, 9, 2, 6, 8, 0,13, 3, 4,14, 7, 5,11,
< 	10,15, 4, 2, 7,12, 9, 5, 6, 1,13,14, 0,11, 3, 8,
< 	 9,14,15, 5, 2, 8,12, 3, 7, 0, 4,10, 1,13,11, 6,
< 	 4, 3, 2,12, 9, 5,15,10,11,14, 1, 7, 6, 0, 8,13,
< 
< 	 4,11, 2,14,15, 0, 8,13, 3,12, 9, 7, 5,10, 6, 1,
< 	13, 0,11, 7, 4, 9, 1,10,14, 3, 5,12, 2,15, 8, 6,
< 	 1, 4,11,13,12, 3, 7,14,10,15, 6, 8, 0, 5, 9, 2,
< 	 6,11,13, 8, 1, 4,10, 7, 9, 5, 0,15,14, 2, 3,12,
< 
< 	13, 2, 8, 4, 6,15,11, 1,10, 9, 3,14, 5, 0,12, 7,
< 	 1,15,13, 8,10, 3, 7, 4,12, 5, 6,11, 0,14, 9, 2,
< 	 7,11, 4, 1, 9,12,14, 2, 0, 6,10,13,15, 3, 5, 8,
< 	 2, 1,14, 7, 4,10, 8,13,15,12, 9, 0, 3, 5, 6,11,
---
> static	char	S[8][64] = {
> 	{14, 4,13, 1, 2,15,11, 8, 3,10, 6,12, 5, 9, 0, 7,
> 	  0,15, 7, 4,14, 2,13, 1,10, 6,12,11, 9, 5, 3, 8,
> 	  4, 1,14, 8,13, 6, 2,11,15,12, 9, 7, 3,10, 5, 0,
> 	 15,12, 8, 2, 4, 9, 1, 7, 5,11, 3,14,10, 0, 6,13},
> 
> 	{15, 1, 8,14, 6,11, 3, 4, 9, 7, 2,13,12, 0, 5,10,
> 	  3,13, 4, 7,15, 2, 8,14,12, 0, 1,10, 6, 9,11, 5,
> 	  0,14, 7,11,10, 4,13, 1, 5, 8,12, 6, 9, 3, 2,15,
> 	 13, 8,10, 1, 3,15, 4, 2,11, 6, 7,12, 0, 5,14, 9},
> 
> 	{10, 0, 9,14, 6, 3,15, 5, 1,13,12, 7,11, 4, 2, 8,
> 	 13, 7, 0, 9, 3, 4, 6,10, 2, 8, 5,14,12,11,15, 1,
> 	 13, 6, 4, 9, 8,15, 3, 0,11, 1, 2,12, 5,10,14, 7,
> 	  1,10,13, 0, 6, 9, 8, 7, 4,15,14, 3,11, 5, 2,12},
> 
> 	{ 7,13,14, 3, 0, 6, 9,10, 1, 2, 8, 5,11,12, 4,15,
> 	 13, 8,11, 5, 6,15, 0, 3, 4, 7, 2,12, 1,10,14, 9,
> 	 10, 6, 9, 0,12,11, 7,13,15, 1, 3,14, 5, 2, 8, 4,
> 	  3,15, 0, 6,10, 1,13, 8, 9, 4, 5,11,12, 7, 2,14},
> 
> 	{ 2,12, 4, 1, 7,10,11, 6, 8, 5, 3,15,13, 0,14, 9,
> 	 14,11, 2,12, 4, 7,13, 1, 5, 0,15,10, 3, 9, 8, 6,
> 	  4, 2, 1,11,10,13, 7, 8,15, 9,12, 5, 6, 3, 0,14,
> 	 11, 8,12, 7, 1,14, 2,13, 6,15, 0, 9,10, 4, 5, 3},
> 
> 	{12, 1,10,15, 9, 2, 6, 8, 0,13, 3, 4,14, 7, 5,11,
> 	 10,15, 4, 2, 7,12, 9, 5, 6, 1,13,14, 0,11, 3, 8,
> 	  9,14,15, 5, 2, 8,12, 3, 7, 0, 4,10, 1,13,11, 6,
> 	  4, 3, 2,12, 9, 5,15,10,11,14, 1, 7, 6, 0, 8,13},
> 
> 	{ 4,11, 2,14,15, 0, 8,13, 3,12, 9, 7, 5,10, 6, 1,
> 	 13, 0,11, 7, 4, 9, 1,10,14, 3, 5,12, 2,15, 8, 6,
> 	  1, 4,11,13,12, 3, 7,14,10,15, 6, 8, 0, 5, 9, 2,
> 	  6,11,13, 8, 1, 4,10, 7, 9, 5, 0,15,14, 2, 3,12},
> 
> 	{13, 2, 8, 4, 6,15,11, 1,10, 9, 3,14, 5, 0,12, 7,
> 	  1,15,13, 8,10, 3, 7, 4,12, 5, 6,11, 0,14, 9, 2,
> 	  7,11, 4, 1, 9,12,14, 2, 0, 6,10,13,15, 3, 5, 8,
> 	  2, 1,14, 7, 4,10, 8,13,15,12, 9, 0, 3, 5, 6,11},
208c208
< static	char	P[] {
---
> static	char	P[] = {
235,236c235,236
< encrypt(block, edflag)
< char *block;
---
> static void
> encrypt(char *block, int edflag)
239c239
< 	register t, j, k;
---
> 	register int t, j, k;
324,326c324
< crypt(pw,salt)
< char *pw;
< char *salt;
---
> crypt(char *pw, char *salt)
328c326
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
5c5,6
< #define	NBUF	29		/* size of buffer cache */
---
> #define	NBUF	64		/* size of buffer cache (matches kernel-side
> 				 * h/param.h's bumped value). */
10,12c11
< #define	MAXUPRC	25		/* max processes per user */
< #define	SSIZE	20		/* initial stack size (*64 bytes) */
< #define	SINCR	20		/* increment of stack (*64 bytes) */
---
> /* MAXUPRC, SSIZE, NCARGS are gone -- see kernel-side h/param.h. */
14d12
< #define	CANBSIZ	256		/* max size of typewriter line */
17d14
< #define	NCALL	20		/* max simultaneous time callouts */
20d16
< #define	NCLIST	100		/* max total clist size */
25d20
< #define	NCARGS	5120		/* # characters in exec arglist */
39,40c34
< #define	PWAIT	30
< #define	PSLEP	40
---
> /* PWAIT and PSLEP gone -- see kernel-side h/param.h. */
51c45,46
<  * stored in bits in a word.
---
>  * stored in bits in a word.  Only names actually referenced are
>  * defined; the rest are reserved slots in u_signal[NSIG].
56d50
< #define	SIGINS	4	/* illegal instruction */
58,60d51
< #define	SIGIOT	6	/* iot */
< #define	SIGEMT	7	/* emt */
< #define	SIGFPT	8	/* floating exception */
62,64d52
< #define	SIGBUS	10	/* bus error */
< #define	SIGSEG	11	/* segmentation violation */
< #define	SIGSYS	12	/* bad system call */
67d54
< #define	SIGTRM	15	/* Catchable termination */
76,77c63,64
< /* BSLOP can be 0 unless you have a TIU/Spider */
< #define	BSLOP	2		/* In case some device needs bigger buffers */
---
> /* BSLOP was v7 slop for TIU/Spider devices; this port has no such device. */
> #define	BSLOP	0
84c71
< #define	UBASE	0140000		/* abs. addr of user block */
---
> #ifndef NULL
86c73,74
< #define	CMASK	0		/* default mask for file creation */
---
> #endif
> /* CMASK removed -- see kernel h/param.h. */
93,95d80
< #define	INFSIZE	138		/* size of per-proc info for users */
< #define	CBSIZE	14		/* number of chars in a clist block */
< #define	CROUND	017		/* clist rounding: sizeof(int *) + CBSIZE - 1*/
128a114
> #ifndef SYS_TYPES_H
131c117
< typedef	unsigned int	ino_t;
---
> typedef	unsigned short	ino_t;
133c119,122
< typedef	int		label_t[6];	/* regs 2-7 */
---
> /* label_t mirrors h/param.h (R4..R11 + sp + lr).  Exported here only
>  * so cmd/ps + pstat compile their copy of struct user (u_rsav/u_qsav/
>  * u_ssav). */
> typedef	int		label_t[10];
135a125,126
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
13d12
< #define	NINDEX	15
15,25d13
< struct group {
< 	short	g_state;
< 	char	g_index;
< 	char	g_rot;
< 	struct	group	*g_group;
< 	struct	inode	*g_inode;
< 	struct	file	*g_file;
< 	short	g_rotmask;
< 	short	g_datq;
< 	struct	chan *g_chans[NINDEX];
< };
41c29
< 		};
---
> 		} u_reg;
44,45c32
< 			struct	group	i_group;	/*  multiplexor group file */
< 		};
---
> 		} u_dev;
47a35,40
> /* Caller-side shorthand for the named inner structs (kept v7-flavoured).
>  * v7's mpx multiplexor `struct group i_group` field is removed -- the
>  * mpx subsystem isn't wired on this port. */
> #define	i_addr	u_reg.i_addr
> #define	i_lastr	u_reg.i_lastr
> #define	i_rdev	u_dev.i_rdev
51c44
< struct inode *mpxip;		/* mpx virtual inode */
---
> /* mpxip removed -- v7 mpx subsystem not wired on this port. */
```

### h/systm.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/systm.h unix-v7-c99/h/systm.h || true
```

Expect:

```
6d5
< char	canonb[CANBSIZ];	/* buffer for erase and kill (#@) */
23,27c22,24
< /*
<  * Number of character switch entries.
<  * Set by cinit/tty.c
<  */
< int	nchrdev;
---
> /* v7's `int nchrdev` (character-switch row count, set by cinit()) is
>  * gone -- this port doesn't dispatch through cdevsw[], so no caller
>  * ever reads it. */
35c32,34
< physadr	lks;			/* pointer to clock device */
---
> /* `physadr lks` (PDP-11 KW11-L clock-device CSR pointer) is gone --
>  * the ARM port rearms the timer via cntv_tval_set, not by writing
>  * lks->r[0] = 0115. */
37d35
< int	nswap;			/* size of swap space */
44,63c42,86
< dev_t	pipedev;		/* pipe device */
< extern	int	icode[];	/* user init code */
< extern	int	szicode;	/* its size */
< 
< dev_t getmdev();
< daddr_t	bmap();
< struct inode *ialloc();
< struct inode *iget();
< struct inode *owner();
< struct inode *maknode();
< struct inode *namei();
< struct buf *alloc();
< struct buf *getblk();
< struct buf *geteblk();
< struct buf *bread();
< struct buf *breada();
< struct filsys *getfs();
< struct file *getf();
< struct file *falloc();
< int	uchar();
---
> /* `dev_t pipedev` (the device pipe(2) ialloc'd against) is gone --
>  * sys/pipe.c::pipe() was removed; arch/arm.c::kpipe uses its own
>  * pipes[] table that doesn't allocate inodes. */
> dev_t	getmdev(void);
> daddr_t	bmap(struct inode *ip, daddr_t bn, int rwflg);
> void	setrun(struct proc *p);
> int	setpri(struct proc *pp);
> int	issig(void);
> unsigned min(unsigned a, unsigned b);
> int	fubyte(caddr_t addr);
> int	subyte(caddr_t addr, char c);
> struct inode *ialloc(dev_t dev);
> struct inode *iget(dev_t dev, ino_t ino);
> struct inode *owner(void);
> struct inode *maknode(int mode);
> struct inode *namei(int (*func)(void), int flag);
> struct buf *alloc(dev_t dev);
> struct buf *getblk(dev_t dev, daddr_t blkno);
> struct buf *geteblk(void);
> struct buf *bread(dev_t dev, daddr_t blkno);
> struct buf *breada(dev_t dev, daddr_t blkno, daddr_t rablkno);
> struct filsys *getfs(dev_t dev);
> struct file *getf(int fdes);
> /* falloc() (allocate file slot) is gone -- see sys/fio.c. */
> int	uchar(void);
> void	free(dev_t dev, daddr_t bno);
> void	ifree(dev_t dev, ino_t ino);
> void	update(void);
> int	passc(int c);
> int	cpass(void);
> void	closef(struct file *fp);
> int	access(struct inode *ip, int mode);
> void	iput(struct inode *ip);
> void	plock(struct inode *ip);
> void	prele(struct inode *ip);
> void	readi(struct inode *ip);
> void	writei(struct inode *ip);
> int	iupdat(struct inode *ip, time_t *ta, time_t *tm);
> int	suser(void);
> int	ufalloc(void);
> void	xrele(struct inode *ip);
> void	psignal(struct proc *p, int sig);
> void	bcopy(char *f, char *t, unsigned int n);
> int	copyin(caddr_t f, caddr_t t, unsigned int n);
> int	copyout(caddr_t f, caddr_t t, unsigned int n);
74,81d96
< /*
<  * Structure of the system-entry table
<  */
< extern struct sysent {
< 	char	sy_narg;		/* total number of arguments */
< 	char	sy_nrarg;		/* number of args in registers */
< 	int	(*sy_call)();		/* handler */
< } sysent[];
```

### sys/iget.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/iget.c unix-v7-c99/sys/iget.c || true
```

Expect:

```
9d8
< #include "../h/conf.h"
10a10,20
> #include "../h/proto.h"
> 
> /* bread/brelse/bdwrite/sleep/panic come from h/proto.h.
>  * free/ifree/ialloc/getfs/prele/writei/bcopy come from h/systm.h. */
> 
> void iexpand(register struct inode *ip, register struct dinode *dp);
> void itrunc(register struct inode *ip);
> void tloop(dev_t dev, daddr_t bn, int f1, int f2);
> void wdir(struct inode *ip);
> void iput(register struct inode *ip);
> int iupdat(register struct inode *ip, time_t *ta, time_t *tm);
30,32c40
< iget(dev, ino)
< dev_t dev;
< ino_t ino;
---
> iget(dev_t dev, ino_t ino)
92,94c100,101
< iexpand(ip, dp)
< register struct inode *ip;
< register struct dinode *dp;
---
> void
> iexpand(register struct inode *ip, register struct dinode *dp)
109d115
< 		*p1++ = 0;
111a118
> 		*p1++ = 0;
122,123c129,130
< iput(ip)
< register struct inode *ip;
---
> void
> iput(register struct inode *ip)
149,151c156,157
< iupdat(ip, ta, tm)
< register struct inode *ip;
< time_t *ta, *tm;
---
> int
> iupdat(register struct inode *ip, time_t *ta, time_t *tm)
161c167
< 			return;
---
> 			return(0);
165c171
< 			return;
---
> 			return(0);
177a184,185
> 			*p1++ = *p2++;
> 			*p1++ = *p2++;
181,182d188
< 			*p1++ = *p2++;
< 			*p1++ = *p2++;
192a199
> 	return(0);
204,205c211,212
< itrunc(ip)
< register struct inode *ip;
---
> void
> itrunc(register struct inode *ip)
207c214
< 	register i;
---
> 	register int i;
242,244c249,250
< tloop(dev, bn, f1, f2)
< dev_t dev;
< daddr_t bn;
---
> void
> tloop(dev_t dev, daddr_t bn, int f1, int f2)
246c252
< 	register i;
---
> 	register int i;
251a258
> 	bap = NULL;
280c287
< maknode(mode)
---
> maknode(int mode)
305,306c312,313
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
7a8,11
> #include "../h/proto.h"
> 
> /* bread/brelse come from h/proto.h.
>  * iget/iput/plock/access/bcopy/bmap/fubyte come from h/systm.h. */
21,22c25
< namei(func, flag)
< int (*func)();
---
> namei(int (*func)(void), int flag)
25c28
< 	register c;
---
> 	register int c;
66,67d68
< 		if (mpxip!=NULL && c=='!')
< 			break;
76,81c77,78
< 	if (c == '!' && mpxip != NULL) {
< 		iput(dp);
< 		plock(mpxip);
< 		mpxip->i_count++;
< 		return(mpxip);
< 	}
---
> 	/* v7's `path!subpath` mpx multiplexor lookup is gone -- mpxip was
> 	 * never assigned on this port, so the branch was unreachable. */
202,210c199,201
< /*
<  * Return the next character from the
<  * kernel string pointed at by dirp.
<  */
< schar()
< {
< 
< 	return(*u.u_dirp++ & 0377);
< }
---
> /* schar() (kernel-side name-fetcher passed to namei) was only used by
>  * sys/sig.c::core() which is gone on this port; uchar() remains for the
>  * user-space namei path. */
216c207,208
< uchar()
---
> int
> uchar(void)
218c210
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
7,8c7
< #include "../h/proc.h"
< #include "../h/seg.h"
---
> #include "../h/proto.h"
56,58c55
< bread(dev, blkno)
< dev_t dev;
< daddr_t blkno;
---
> bread(dev_t dev, daddr_t blkno)
84,86c81
< breada(dev, blkno, rablkno)
< dev_t dev;
< daddr_t blkno, rablkno;
---
> breada(dev_t dev, daddr_t blkno, daddr_t rablkno)
125,126c120,121
< bwrite(bp)
< register struct buf *bp;
---
> void
> bwrite(struct buf *bp)
128c123
< 	register flag;
---
> 	register int flag;
149,152c144,146
<  * given up (e.g. when writing a partial block where it is
<  * assumed that another write for the same block will soon follow).
<  * This can't be done for magtape, since writes must be done
<  * in the same order as requested.
---
>  * given up.  v7 checked dp->b_flags&B_TAPE here for an
>  * ordered-write tape path, but this port has no magtape device,
>  * so the branch was unreachable and is gone.
154,155c148,149
< bdwrite(bp)
< register struct buf *bp;
---
> void
> bdwrite(struct buf *bp)
157,165c151,152
< 	register struct buf *dp;
< 
< 	dp = bdevsw[major(bp->b_dev)].d_tab;
< 	if(dp->b_flags & B_TAPE)
< 		bawrite(bp);
< 	else {
< 		bp->b_flags |= B_DELWRI | B_DONE;
< 		brelse(bp);
< 	}
---
> 	bp->b_flags |= B_DELWRI | B_DONE;
> 	brelse(bp);
168,177c155,157
< /*
<  * Release the buffer, start I/O on it, but don't wait for completion.
<  */
< bawrite(bp)
< register struct buf *bp;
< {
< 
< 	bp->b_flags |= B_ASYNC;
< 	bwrite(bp);
< }
---
> /* v7's bawrite() (asynchronous bwrite) is gone -- its only callers
>  * were sys1.c::exec (now removed) and the B_TAPE branch of bdwrite
>  * (also gone). */
182,183c162,163
< brelse(bp)
< register struct buf *bp;
---
> void
> brelse(struct buf *bp)
186c166
< 	register s;
---
> 	register int s;
218,220c198,199
< incore(dev, blkno)
< dev_t dev;
< daddr_t blkno;
---
> int
> incore(dev_t dev, daddr_t blkno)
238,240c217
< getblk(dev, blkno)
< dev_t dev;
< daddr_t blkno;
---
> getblk(dev_t dev, daddr_t blkno)
245c222
< 	register i;
---
> 	register int i;
309c286
< geteblk()
---
> geteblk(void)
343,344c320,321
< iowait(bp)
< register struct buf *bp;
---
> void
> iowait(struct buf *bp)
358,359c335,336
< notavail(bp)
< register struct buf *bp;
---
> void
> notavail(struct buf *bp)
361c338
< 	register s;
---
> 	register int s;
374,375c351,352
< iodone(bp)
< register struct buf *bp;
---
> void
> iodone(struct buf *bp)
378,379c355,356
< 	if(bp->b_flags&B_MAP)
< 		mapfree(bp);
---
> 	/* v7's B_MAP/mapfree path (UNIBUS map release after physio) is gone
> 	 * -- no buf on this port carries B_MAP, so the branch was dead. */
392,393c369,370
< clrbuf(bp)
< struct buf *bp;
---
> void
> clrbuf(struct buf *bp)
395,396c372,373
< 	register *p;
< 	register c;
---
> 	register int *p;
> 	register int c;
409,410c386,387
< swap(blkno, coreaddr, count, rdflg)
< register count;
---
> void
> swap(daddr_t blkno, int coreaddr, int count, int rdflg)
413c390
< 	register tcount;
---
> 	register int tcount;
425c402,405
< 		bp->b_flags = B_BUSY | B_PHYS | rdflg;
---
> 		/* v7 set B_PHYS (UNIBUS-mapped physio) and b_xmem (high
> 		 * 6 bits of an 18-bit phys address); neither is ever read
> 		 * on this port, so they are dropped. */
> 		bp->b_flags = B_BUSY | rdflg;
433d412
< 		bp->b_xmem = (coreaddr>>10) & 077;
456,457c435,436
< bflush(dev)
< dev_t dev;
---
> void
> bflush(dev_t dev)
475,551d453
<  * Raw I/O. The arguments are
<  *	The strategy routine for the device
<  *	A buffer, which will always be a special buffer
<  *	  header owned exclusively by the device for this purpose
<  *	The device number
<  *	Read/write flag
<  * Essentially all the work is computing physical addresses and
<  * validating them.
<  */
< physio(strat, bp, dev, rw)
< register struct buf *bp;
< int (*strat)();
< {
< 	register unsigned base;
< 	register int nb;
< 	int ts;
< 
< 	base = (unsigned)u.u_base;
< 	/*
< 	 * Check odd base, odd count, and address wraparound
< 	 */
< 	if (base&01 || u.u_count&01 || base>=base+u.u_count)
< 		goto bad;
< 	ts = (u.u_tsize+127) & ~0177;
< 	if (u.u_sep)
< 		ts = 0;
< 	nb = (base>>6) & 01777;
< 	/*
< 	 * Check overlap with text. (ts and nb now
< 	 * in 64-byte clicks)
< 	 */
< 	if (nb < ts)
< 		goto bad;
< 	/*
< 	 * Check that transfer is either entirely in the
< 	 * data or in the stack: that is, either
< 	 * the end is in the data or the start is in the stack
< 	 * (remember wraparound was already checked).
< 	 */
< 	if ((((base+u.u_count)>>6)&01777) >= ts+u.u_dsize
< 	    && nb < 1024-u.u_ssize)
< 		goto bad;
< 	spl6();
< 	while (bp->b_flags&B_BUSY) {
< 		bp->b_flags |= B_WANTED;
< 		sleep((caddr_t)bp, PRIBIO+1);
< 	}
< 	bp->b_flags = B_BUSY | B_PHYS | rw;
< 	bp->b_dev = dev;
< 	/*
< 	 * Compute physical address by simulating
< 	 * the segmentation hardware.
< 	 */
< 	ts = (u.u_sep? UDSA: UISA)->r[nb>>7] + (nb&0177);
< 	bp->b_un.b_addr = (caddr_t)((ts<<6) + (base&077));
< 	bp->b_xmem = (ts>>10) & 077;
< 	bp->b_blkno = u.u_offset >> BSHIFT;
< 	bp->b_bcount = u.u_count;
< 	bp->b_error = 0;
< 	u.u_procp->p_flag |= SLOCK;
< 	(*strat)(bp);
< 	spl6();
< 	while ((bp->b_flags&B_DONE) == 0)
< 		sleep((caddr_t)bp, PRIBIO);
< 	u.u_procp->p_flag &= ~SLOCK;
< 	if (bp->b_flags&B_WANTED)
< 		wakeup((caddr_t)bp);
< 	spl0();
< 	bp->b_flags &= ~(B_BUSY|B_WANTED);
< 	u.u_count = bp->b_resid;
< 	geterror(bp);
< 	return;
<     bad:
< 	u.u_error = EFAULT;
< }
< 
< /*
557,558c459,460
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
15c15
< struct	passwd nouser = {"", "nope"};
---
> struct	passwd nouser = {"", "nope", 0, 0, 0, 0, 0, 0, 0};
23,29c23,28
< struct	passwd *getpwnam();
< char	*strcat();
< int	setpwent();
< char	*ttyname();
< char	*crypt();
< char	*getpass();
< char	*rindex(), *index();
---
> struct	passwd *getpwnam(char *name);
> char	*strcat(char *a, char *b);
> char	*ttyname(int f);
> char	*crypt(char *pw, char *salt);
> char	*getpass(char *prompt);
> char	*rindex(char *sp, int c), *index(register char *sp, int c);
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
29c29
< int	aflg, dflg, lflg, sflg, tflg, uflg, iflg, fflg, gflg, cflg;
---
> int	aflg, dflg, lflg, sflg, tflg, uflg, iflg, fflg, gflg, cflg, Rflg, Fflg, pflg;
42,45c42,52
< char	*makename();
< struct	lbuf *gstat();
< char	*ctime();
< long	nblock();
---
> char	*makename(char *dir, char *file);
> struct	lbuf *gstat(char *file, int argfl);
> char	*ctime(long *t);
> long	nblock(long size);
> void	pentry(struct lbuf *ap);
> int	getname(int uid, char buf[]);
> void	pmode(int aflag);
> void	select(int *pairp);
> void	readdir(char *dir);
> int	compar(struct lbuf **pp1, struct lbuf **pp2);
> void	descend_R(char *dir, struct lbuf **start, struct lbuf **end);
49,50c56,57
< main(argc, argv)
< char *argv[];
---
> int
> main(int argc, char *argv[])
58c65
< 	int compar();
---
> 	int compar(struct lbuf **pp1, struct lbuf **pp2);
113a121,135
> 		case 'R':
> 			Rflg++;
> 			statreq++;
> 			continue;
> 
> 		case 'F':
> 			Fflg++;
> 			statreq++;
> 			continue;
> 
> 		case 'p':
> 			pflg++;
> 			statreq++;
> 			continue;
> 
146,147c168,169
< 		if (ep->ltype=='d' && dflg==0 || fflg) {
< 			if (argc>1)
---
> 		if ((ep->ltype=='d' && dflg==0) || fflg) {
> 			if (argc>1 || Rflg)
157c179,180
< 		} else 
---
> 			if (Rflg) descend_R(ep->ln.namep, slastp, lastp);
> 		} else
163,164c186,190
< pentry(ap)
< struct lbuf *ap;
---
> /* For each subdirectory under `dir` named by entries in [start,end),
>  * print a header and a recursive listing.  Operates after the caller
>  * has already printed `dir` itself, so output mirrors POSIX ls -R. */
> void
> descend_R(char *dir, struct lbuf **start, struct lbuf **end)
166,167c192,234
< 	struct { char dminor, dmajor;};
< 	register t;
---
> 	struct lbuf **ep;
> 	struct lbuf **save_first;
> 	char path[256];
> 	int i, j;
> 
> 	for (ep = start; ep < end; ep++) {
> 		struct lbuf *e = *ep;
> 		struct lbuf **rstart, **rend;
> 		struct lbuf **p;
> 		if (e->ltype != 'd') continue;
> 		/* Skip . and .. -- both have the directory bit but aren't
> 		 * fresh subtrees.  In v7 ls's lbuf, lname is fixed-width
> 		 * (not necessarily NUL-terminated) so check explicit length. */
> 		if (e->ln.lname[0] == '.' &&
> 		    (e->ln.lname[1] == '\0' ||
> 		     (e->ln.lname[1] == '.' && e->ln.lname[2] == '\0')))
> 			continue;
> 		for (i = 0; dir[i] && i < 200; i++) path[i] = dir[i];
> 		if (i > 0 && path[i-1] != '/') path[i++] = '/';
> 		for (j = 0; j < 14 && e->ln.lname[j]; j++) path[i++] = e->ln.lname[j];
> 		path[i] = '\0';
> 		printf("\n%s:\n", path);
> 		save_first = firstp;
> 		firstp = lastp;	/* start of fresh window */
> 		rstart = lastp;
> 		tblocks = 0;
> 		readdir(path);
> 		rend = lastp;
> 		if (fflg == 0)
> 			qsort(rstart, rend - rstart, sizeof *rstart, compar);
> 		if (lflg || sflg)
> 			printf("total %D\n", tblocks);
> 		for (p = rstart; p < rend; p++)
> 			pentry(*p);
> 		descend_R(path, rstart, rend);
> 		firstp = save_first;
> 	}
> }
> 
> void
> pentry(struct lbuf *ap)
> {
> 	register int t;
199c266
< 		printf("%s\n", p->ln.namep);
---
> 		printf("%s", p->ln.namep);
201c268,274
< 		printf("%.14s\n", p->ln.lname);
---
> 		printf("%.14s", p->ln.lname);
> 	/* -F: directory gets '/', executable gets '*'; -p: directory '/'. */
> 	if (Fflg || pflg) {
> 		if (p->ltype == 'd') putchar('/');
> 		else if (Fflg && (p->lflags & 0111)) putchar('*');
> 	}
> 	putchar('\n');
204,206c277,278
< getname(uid, buf)
< int uid;
< char buf[];
---
> int
> getname(int uid, char buf[])
239,240c311
< nblock(size)
< long size;
---
> nblock(long size)
257c328,329
< pmode(aflag)
---
> void
> pmode(int aflag)
266,267c338,339
< select(pairp)
< register int *pairp;
---
> void
> select(register int *pairp)
278,279c350
< makename(dir, file)
< char *dir, *file;
---
> makename(char *dir, char *file)
297,298c368,369
< readdir(dir)
< char *dir;
---
> void
> readdir(char *dir)
313,314c384,385
< 		 || aflg==0 && dentry.d_name[0]=='.' &&  (dentry.d_name[1]=='\0'
< 			|| dentry.d_name[1]=='.' && dentry.d_name[2]=='\0'))
---
> 		 || (aflg==0 && dentry.d_name[0]=='.' && (dentry.d_name[1]=='\0'
> 			|| (dentry.d_name[1]=='.' && dentry.d_name[2]=='\0'))))
328,329c399
< gstat(file, argfl)
< char *file;
---
> gstat(char *file, int argfl)
331d400
< 	extern char *malloc();
400,401c469,470
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
12c12,13
< PROC STRING *copyargs();
---
> PROC DOLPTR	copyargs(STRING from[], INT n);
> LOCAL STRING	comstring(STRING av[]);
14a16,21
> INT	failed(STRING s1, STRING s2);
> DOLPTR	freeargs(DOLPTR blk);
> INT	assnum(STRING *p, INT n);
> INT	pop(void);
> extern void free(void *p);
> 
27,29c34
< INT	options(argc,argv)
< 	STRING		*argv;
< 	INT		argc;
---
> INT	options(INT argc, STRING *argv)
46c51
< 			THEN	comdiv=argp[2];
---
> 			THEN	comdiv=comstring(&argp[2]);
68,69c73,97
< VOID	setargs(argi)
< 	STRING		argi[];
---
> LOCAL STRING	comstring(STRING av[])
> {
> 	REG STRING	cp;
> 	REG STRING	s, q;
> 	REG INT		n;
> 
> 	IF av[1]
> 	THEN	return(make(*av));
> 	FI
> 
> 	n = 1;
> 	cp = *av;
> 	WHILE *cp++ DO n++ OD
> 	q = alloc(n);
> 	s = q;
> 	cp = *av;
> 	WHILE *cp
> 	DO	*s++ = (*cp == 037 ? SP : *cp);
> 		cp++;
> 	OD
> 	*s = 0;
> 	return(q);
> }
> 
> VOID	setargs(STRING argi[])
80a109
> 	return(0);
83,84c112
< freeargs(blk)
< 	DOLPTR		blk;
---
> DOLPTR freeargs(DOLPTR blk)
90c118
< 	IF argblk=blk
---
> 	IF (argblk=blk)
93c121
< 		THEN	FOR argp=argblk->dolarg; Rcheat(*argp)!=ENDARGS; argp++
---
> 		THEN	FOR argp=(STRING *)argblk->dolarg; Rcheat(*argp)!=ENDARGS; argp++
101,102c129
< LOCAL STRING *	copyargs(from, n)
< 	STRING		from[];
---
> LOCAL DOLPTR	copyargs(STRING from[], INT n)
104c131
< 	REG STRING *	np=alloc(sizeof(STRING*)*n+3*BYTESPERWORD);
---
> 	REG DOLPTR	np=(DOLPTR)alloc(sizeof(STRING*)*n+3*BYTESPERWORD);
106c133
< 	REG STRING *	pp=np;
---
> 	REG STRING *	pp;
109,110c136,137
< 	np=np->dolarg;
< 	dolv=np;
---
> 	pp=(STRING *)np->dolarg;
> 	dolv=pp;
113,115c140,142
< 	DO *np++ = make(*fp++) OD
< 	*np++ = ENDARGS;
< 	return(pp);
---
> 	DO *pp++ = make(*fp++) OD
> 	*pp++ = ENDARGS;
> 	return(np);
118c145
< clearup()
---
> INT clearup(void)
121c148
< 	WHILE argfor=freeargs(argfor) DONE
---
> 	WHILE (argfor=freeargs(argfor)) DONE
124a152
> 	return(0);
127c155
< DOLPTR	useargs()
---
> DOLPTR	useargs(void)
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
79c79,80
< /* result type declarations */
---
> /* result type declarations.  copyto/execs/staknam are LOCAL to their
>  * .c files; REAL expr() was never defined or called, dropped. */
81,108c82,105
< ADDRESS		alloc();
< VOID		addblok();
< STRING		make();
< STRING		movstr();
< TREPTR		cmd();
< TREPTR		makefork();
< NAMPTR		lookup();
< VOID		setname();
< VOID		setargs();
< DOLPTR		useargs();
< REAL		expr();
< STRING		catpath();
< STRING		getpath();
< STRING		*scan();
< STRING		mactrim();
< STRING		macro();
< STRING		execs();
< VOID		await();
< VOID		post();
< STRING		copyto();
< VOID		exname();
< STRING		staknam();
< VOID		printnam();
< VOID		printflg();
< VOID		prs();
< VOID		prc();
< VOID		getenv();
< STRING		*setenv();
---
> ADDRESS		alloc(POS nbytes);
> VOID		addblok(POS reqd);
> STRING		make(STRING v);
> STRING		movstr(REG STRING a, REG STRING b);
> TREPTR		cmd(REG INT sym, INT flg);
> TREPTR		makefork(INT flgs, TREPTR i);
> NAMPTR		lookup(REG STRING nam);
> VOID		setname(STRING argi, INT xp);
> VOID		setargs(STRING argi[]);
> DOLPTR		useargs(void);
> STRING		catpath(REG STRING path, STRING name);
> STRING		getpath(STRING s);
> STRING		*scan(INT argn);
> STRING		mactrim(STRING s);
> STRING		macro(STRING as);
> VOID		await(INT i);
> VOID		post(INT pcsid);
> VOID		exname(REG NAMPTR n);
> VOID		printnam(NAMPTR n);
> VOID		printflg(REG NAMPTR n);
> VOID		prs(STRING as);
> VOID		prc(INT c);
> INT		getenv(void);
> STRING		*setenv(void);
139,147c136,144
< MSG		atline;
< MSG		readmsg;
< MSG		colon;
< MSG		minus;
< MSG		nullstr;
< MSG		sptbnl;
< MSG		unexpected;
< MSG		endoffile;
< MSG		synmsg;
---
> extern MSG	atline;
> extern MSG	readmsg;
> extern MSG	colon;
> extern MSG	minus;
> extern MSG	nullstr;
> extern MSG	sptbnl;
> extern MSG	unexpected;
> extern MSG	endoffile;
> extern MSG	synmsg;
150c147
< SYSTAB		reserved;
---
> extern SYSTAB	reserved;
158,160c155,157
< MSG		stdprompt;
< MSG		supprompt;
< MSG		profile;
---
> extern MSG	stdprompt;
> extern MSG	supprompt;
> extern MSG	profile;
172c169
< MSG		flagadr;
---
> extern MSG	flagadr;
179c176
< MSG		defpath;
---
> extern MSG	defpath;
182,188c179,185
< MSG		mailname;
< MSG		homename;
< MSG		pathname;
< MSG		fngname;
< MSG		ifsname;
< MSG		ps1name;
< MSG		ps2name;
---
> extern MSG	mailname;
> extern MSG	homename;
> extern MSG	pathname;
> extern MSG	fngname;
> extern MSG	ifsname;
> extern MSG	ps1name;
> extern MSG	ps2name;
191c188
< CHAR		tmpout[];
---
> extern CHAR	tmpout[];
200c197
< MSG		devnull;
---
> extern MSG	devnull;
240c237
< VOID		fault();
---
> VOID		fault(INT sig);
242,243c239,240
< STRING		trapcom[];
< BOOL		trapflg[];
---
> extern STRING	trapcom[];
> extern BOOL	trapflg[];
247,249c244,246
< CHAR		numbuf[];
< MSG		export;
< MSG		readonly;
---
> extern CHAR	numbuf[];
> extern MSG	export;
> extern MSG	readonly;
258,282c255,279
< MSG		mailmsg;
< MSG		coredump;
< MSG		badopt;
< MSG		badparam;
< MSG		badsub;
< MSG		nospace;
< MSG		notfound;
< MSG		badtrap;
< MSG		baddir;
< MSG		badshift;
< MSG		illegal;
< MSG		restricted;
< MSG		execpmsg;
< MSG		notid;
< MSG		wtfailed;
< MSG		badcreate;
< MSG		piperr;
< MSG		badopen;
< MSG		badnum;
< MSG		arglist;
< MSG		txtbsy;
< MSG		toobig;
< MSG		badexec;
< MSG		notfound;
< MSG		badfile;
---
> extern MSG	mailmsg;
> extern MSG	coredump;
> extern MSG	badopt;
> extern MSG	badparam;
> extern MSG	badsub;
> extern MSG	nospace;
> extern MSG	notfound;
> extern MSG	badtrap;
> extern MSG	baddir;
> extern MSG	badshift;
> extern MSG	illegal;
> extern MSG	restricted;
> extern MSG	execpmsg;
> extern MSG	notid;
> extern MSG	wtfailed;
> extern MSG	badcreate;
> extern MSG	piperr;
> extern MSG	badopen;
> extern MSG	badnum;
> extern MSG	arglist;
> extern MSG	txtbsy;
> extern MSG	toobig;
> extern MSG	badexec;
> extern MSG	notfound;
> extern MSG	badfile;
284c281
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
27c27,33
< PROC VOID	addg();
---
> PROC VOID	addg(STRING as1, STRING as2, STRING as3);
> INT	gmatch(REG STRING s, REG STRING p);
> INT	makearg(REG ARGPTR args);
> extern int stat(char *p, STATBUF *s);
> extern int open(char *p, int f);
> extern int read(int fd, char *buf, int n);
> extern int close(int fd);
30,31c36
< INT	expand(as,rflg)
< 	STRING		as;
---
> INT	expand(STRING as, INT rflg)
80c85
< 		WHILE read(dirf, &entry, 16) == 16 ANDF (trapnote&SIGSET) == 0
---
> 		WHILE read(dirf, (char *)&entry, 16) == 16 ANDF (trapnote&SIGSET) == 0
108c113
< 	   WHILE c = *s
---
> 	   WHILE (c = *s)
114,115c119,120
< gmatch(s, p)
< 	REG STRING	s, p;
---
> INT
> gmatch(REG STRING s, REG STRING p)
120c125
< 	IF scc = *s++
---
> 	IF (scc = *s++)
125c130
< 	SWITCH c = *p++ IN
---
> 	SWITCH (c = *p++) IN
130c135
< 		WHILE c = *p++
---
> 		WHILE (c = *p++)
142a148
> 		/* fallthrough */
156a163
> 	return(0);
159,160c166
< LOCAL VOID	addg(as1,as2,as3)
< 	STRING		as1, as2, as3;
---
> LOCAL VOID	addg(STRING as1, STRING as2, STRING as3)
168c174
< 	WHILE c = *s1++
---
> 	WHILE (c = *s1++)
176,177c182,183
< 	WHILE *s2 = *s1++ DO s2++ OD
< 	IF s1=as3
---
> 	WHILE (*s2 = *s1++) DO s2++ OD
> 	IF (s1=as3)
179c185
< 		WHILE *s2++ = *++s1 DONE
---
> 		WHILE (*s2++ = *++s1) DONE
181c187,188
< 	makearg(endstak(s2));
---
> 	makearg((ARGPTR)endstak(s2));
> 	return(0);
184,185c191
< makearg(args)
< 	REG STRING	args;
---
> INT makearg(REG ARGPTR args)
188a195
> 	return(0);
```

### cmd/sh/mode.h

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/mode.h unix-v7-c99/cmd/sh/mode.h || true
```

Expect:

```
30,38c30,38
< STRUCT forknod	*FORKPTR;
< STRUCT comnod	*COMPTR;
< STRUCT swnod	*SWPTR;
< STRUCT regnod	*REGPTR;
< STRUCT parnod	*PARPTR;
< STRUCT ifnod	*IFPTR;
< STRUCT whnod	*WHPTR;
< STRUCT fornod	*FORPTR;
< STRUCT lstnod	*LSTPTR;
---
> STRUCT trenod	*FORKPTR;
> STRUCT trenod	*COMPTR;
> STRUCT trenod	*SWPTR;
> STRUCT trenod	*REGPTR;
> STRUCT trenod	*PARPTR;
> STRUCT trenod	*IFPTR;
> STRUCT trenod	*WHPTR;
> STRUCT trenod	*FORPTR;
> STRUCT trenod	*LSTPTR;
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
113a108,125
> STRUCT sysnod	SYSTAB[];
> 
> /* this node is a proforma for those that follow.  C99 strict: the v7
>  * K&R idiom of `t->forktyp' on a TREPTR (where forknod, comnod, etc.
>  * were separate structs with parallel layouts) is replaced with a
>  * single named-union trenod plus #define field aliases below; the
>  * separate forknod/comnod/etc. types are gone (only their `sizeof'
>  * was ever read, now expressed against the union members). */
> struct trenod_tre  { INT tretyp;  IOPTR treio; };
> struct trenod_fork { INT forktyp; IOPTR forkio;  TREPTR forktre; };
> struct trenod_com  { INT comtyp;  IOPTR comio;   ARGPTR comarg; ARGPTR comset; };
> struct trenod_if   { INT iftyp;   TREPTR iftre;  TREPTR thtre;  TREPTR eltre; };
> struct trenod_wh   { INT whtyp;   TREPTR whtre;  TREPTR dotre; };
> struct trenod_for  { INT fortyp;  TREPTR fortre; STRING fornam; COMPTR forlst; };
> struct trenod_sw   { INT swtyp;   STRING swarg;  REGPTR swlst; };
> struct trenod_par  { INT partyp;  TREPTR partre; };
> struct trenod_lst  { INT lsttyp;  TREPTR lstlef; TREPTR lstrit; };
> struct trenod_reg  { ARGPTR regptr; TREPTR regcom; REGPTR regnxt; };
115d126
< /* this node is a proforma for those that follow */
117,118c128,139
< 	INT	tretyp;
< 	IOPTR	treio;
---
> 	union {
> 		struct trenod_tre  _tre;
> 		struct trenod_fork _fork;
> 		struct trenod_com  _com;
> 		struct trenod_if   _if;
> 		struct trenod_wh   _wh;
> 		struct trenod_for  _for;
> 		struct trenod_sw   _sw;
> 		struct trenod_par  _par;
> 		struct trenod_lst  _lst;
> 		struct trenod_reg  _reg;
> 	} u;
133,188d153
< struct forknod {
< 	INT	forktyp;
< 	IOPTR	forkio;
< 	TREPTR	forktre;
< };
< 
< struct comnod {
< 	INT	comtyp;
< 	IOPTR	comio;
< 	ARGPTR	comarg;
< 	ARGPTR	comset;
< };
< 
< struct ifnod {
< 	INT	iftyp;
< 	TREPTR	iftre;
< 	TREPTR	thtre;
< 	TREPTR	eltre;
< };
< 
< struct whnod {
< 	INT	whtyp;
< 	TREPTR	whtre;
< 	TREPTR	dotre;
< };
< 
< struct fornod {
< 	INT	fortyp;
< 	TREPTR	fortre;
< 	STRING	fornam;
< 	COMPTR	forlst;
< };
< 
< struct swnod {
< 	INT	swtyp;
< 	STRING	swarg;
< 	REGPTR	swlst;
< };
< 
< struct regnod {
< 	ARGPTR	regptr;
< 	TREPTR	regcom;
< 	REGPTR	regnxt;
< };
< 
< struct parnod {
< 	INT	partyp;
< 	TREPTR	partre;
< };
< 
< struct lstnod {
< 	INT	lsttyp;
< 	TREPTR	lstlef;
< 	TREPTR	lstrit;
< };
< 
196,204c161,169
< #define	FORKTYPE	(sizeof(struct forknod))
< #define	COMTYPE		(sizeof(struct comnod))
< #define	IFTYPE		(sizeof(struct ifnod))
< #define	WHTYPE		(sizeof(struct whnod))
< #define	FORTYPE		(sizeof(struct fornod))
< #define	SWTYPE		(sizeof(struct swnod))
< #define	REGTYPE		(sizeof(struct regnod))
< #define	PARTYPE		(sizeof(struct parnod))
< #define	LSTTYPE		(sizeof(struct lstnod))
---
> #define	FORKTYPE	(sizeof(struct trenod_fork))
> #define	COMTYPE		(sizeof(struct trenod_com))
> #define	IFTYPE		(sizeof(struct trenod_if))
> #define	WHTYPE		(sizeof(struct trenod_wh))
> #define	FORTYPE		(sizeof(struct trenod_for))
> #define	SWTYPE		(sizeof(struct trenod_sw))
> #define	REGTYPE		(sizeof(struct trenod_reg))
> #define	PARTYPE		(sizeof(struct trenod_par))
> #define	LSTTYPE		(sizeof(struct trenod_lst))
205a171,206
> 
> /* Field-access macros: subsequent code writes `t->forktyp' etc., which
>  * the preprocessor rewrites to `t->u._fork.forktyp' (literal field of
>  * the named-union member).  Macros come AFTER all struct definitions
>  * so the field declarations above stay un-rewritten. */
> #define tretyp  u._tre.tretyp
> #define treio   u._tre.treio
> #define forktyp u._fork.forktyp
> #define forkio  u._fork.forkio
> #define forktre u._fork.forktre
> #define comtyp  u._com.comtyp
> #define comio   u._com.comio
> #define comarg  u._com.comarg
> #define comset  u._com.comset
> #define iftyp   u._if.iftyp
> #define iftre   u._if.iftre
> #define thtre   u._if.thtre
> #define eltre   u._if.eltre
> #define whtyp   u._wh.whtyp
> #define whtre   u._wh.whtre
> #define dotre   u._wh.dotre
> #define fortyp  u._for.fortyp
> #define fortre  u._for.fortre
> #define fornam  u._for.fornam
> #define forlst  u._for.forlst
> #define swtyp   u._sw.swtyp
> #define swarg   u._sw.swarg
> #define swlst   u._sw.swlst
> #define partyp  u._par.partyp
> #define partre  u._par.partre
> #define lsttyp  u._lst.lsttyp
> #define lstlef  u._lst.lstlef
> #define lstrit  u._lst.lstrit
> #define regptr  u._reg.regptr
> #define regcom  u._reg.regcom
> #define regnxt  u._reg.regnxt
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
13c13,50
< PROC VOID	gsort();
---
> PROC VOID	gsort(STRING from[], STRING to[]);
> LOCAL STRING	execs(STRING ap, REG STRING t[]);
> LOCAL INT	split(REG STRING s);
> INT	subst(INT in, INT ot);
> INT	chkopen(STRING idf);
> INT	tmpfil(void);
> INT	stoi(STRING icp);
> INT	failed(STRING s1, STRING s2);
> INT	create(STRING s);
> INT	rename(REG INT f1, REG INT f2);
> INT	cf(STRING s1, STRING s2);
> INT	any(REG CHAR c, STRING s);
> INT	namscan(VOID (*fn)(NAMPTR));
> INT	trim(STRING at);
> INT	sigchk(void);
> INT	clearup(void);
> INT	execexp(STRING t, INT in);
> INT	done(void);
> INT	setargs(STRING argi[]);
> INT	exitsh(INT xno);
> INT	exitset(void);
> INT	expand(STRING as, INT rflg);
> INT	makearg(REG ARGPTR args);
> STRING	*setenv(void);
> VOID	exname(REG NAMPTR n);
> VOID	prc(INT c);
> VOID	prs(STRING as);
> VOID	prn(INT n);
> VOID	prp(void);
> VOID	newline(void);
> VOID	blank(void);
> extern int close(int fd);
> extern int unlink(char *p);
> extern int dup();
> extern int open(char *p, int f);
> extern long lseek(int fd, long off, int whence);
> extern int execve(char *p, char **argv, char **env);
> extern int wait(int *st);
18c55
< STRING		sysmsg[];
---
> extern STRING	sysmsg[];
31,32c68
< VOID	initio(iop)
< 	IOPTR		iop;
---
> VOID	initio(IOPTR iop)
65a102
> 	return(0);
68,69c105,132
< STRING	getpath(s)
< 	STRING		s;
---
> VOID	nullio(IOPTR iop)
> {
> 	REG STRING	ion;
> 	REG INT		iof, fd;
> 
> 	IF iop
> 	THEN	iof=iop->iofile;
> 		ion=mactrim(iop->ioname);
> 		IF *ion ANDF (flags&noexec)==0
> 		THEN	IF iof&IODOC
> 			THEN	fd=tmpfil(); close(fd); unlink(tmpout);
> 			ELIF iof&IOMOV
> 			THEN	;
> 			ELIF (iof&IOPUT)==0
> 			THEN	close(chkopen(ion));
> 			ELIF flags&rshflg
> 			THEN	failed(ion,restricted);
> 			ELIF iof&IOAPP ANDF (fd=open(ion,1))>=0
> 			THEN	lseek(fd, 0L, 2); close(fd);
> 			ELSE	fd=create(ion); close(fd);
> 			FI
> 		FI
> 		nullio(iop->ionxt);
> 	FI
> 	return(0);
> }
> 
> STRING	getpath(STRING s)
80a144
> 	return(0);
83,84c147
< INT	pathopen(path, name)
< 	REG STRING	path, name;
---
> INT	pathopen(REG STRING path, REG STRING name)
93,95c156
< STRING	catpath(path,name)
< 	REG STRING	path;
< 	STRING		name;
---
> STRING	catpath(REG STRING path, STRING name)
112,113c173
< VOID	execa(at)
< 	STRING		at[];
---
> VOID	execa(STRING at[])
122c182
< 		WHILE path=execs(path,t) DONE
---
> 		WHILE (path=execs(path,t)) DONE
124a185
> 	return(0);
127,129c188
< LOCAL STRING	execs(ap,t)
< 	STRING		ap;
< 	REG STRING	t[];
---
> LOCAL STRING	execs(STRING ap, REG STRING t[])
150c209,211
< 		longjmp(subshell,1);
---
> 		execexp(0,input);
> 		done();
> 		/* fallthrough */
153a215
> 		/* fallthrough */
156a219
> 		/* fallthrough */
159a223
> 		/* fallthrough */
162a227
> 		/* fallthrough */
165a231
> 	return(prefix);
173c239
< postclr()
---
> INT postclr(void)
179a246
> 	return(0);
182,183c249
< VOID	post(pcsid)
< 	INT		pcsid;
---
> VOID	post(INT pcsid)
194a261
> 	return(0);
197,198c264
< VOID	await(i)
< 	INT		i;
---
> VOID	await(INT i)
225c291
< 		IF sig = w&0177
---
> 		IF (sig = w&0177)
247a314
> 	return(0);
252,253c319
< trim(at)
< 	STRING		at;
---
> INT trim(STRING at)
259,260c325,326
< 	IF p=at
< 	THEN	WHILE c = *p
---
> 	IF (p=at)
> 	THEN	WHILE (c = *p)
263a330
> 	return(0);
266,267c333
< STRING	mactrim(s)
< 	STRING		s;
---
> STRING	mactrim(STRING s)
274,275c340
< STRING	*scan(argn)
< 	INT		argn;
---
> STRING	*scan(INT argn)
277c342
< 	REG ARGPTR	argp = Rcheat(gchain)&~ARGMK;
---
> 	REG ARGPTR	argp = (ARGPTR)(long)(Rcheat(gchain)&~ARGMK);
280c345
< 	comargn=getstak(BYTESPERWORD*argn+BYTESPERWORD); comargm = comargn += argn; *comargn = ENDARGS;
---
> 	comargn=(STRING *)getstak(BYTESPERWORD*argn+BYTESPERWORD); comargm = comargn += argn; *comargn = ENDARGS;
284c349
< 		IF argp = argp->argnxt
---
> 		IF (argp = argp->argnxt)
292c357
< 		argp = Rcheat(argp)&~ARGMK;
---
> 		argp = (ARGPTR)(long)(Rcheat(argp)&~ARGMK);
297,298c362
< LOCAL VOID	gsort(from,to)
< 	STRING		from[], to[];
---
> LOCAL VOID	gsort(STRING from[], STRING to[])
303c367
< 	IF (n=to-from)<=1 THEN return FI
---
> 	IF (n=to-from)<=1 THEN return(0) FI
318a383
> 	return(0);
323,324c388
< INT	getarg(ac)
< 	COMPTR		ac;
---
> INT	getarg(COMPTR ac)
330c394
< 	IF c=ac
---
> 	IF (c=ac)
340,341c404
< LOCAL INT	split(s)
< 	REG STRING	s;
---
> LOCAL INT	split(REG STRING s)
343a407
> 	REG ARGPTR	arg;
358c422,423
< 		IF c=expand((argp=endstak(argp))->argval,0)
---
> 		arg=(ARGPTR)endstak(argp);
> 		IF (c=expand(arg->argval,0))
361c426
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
12a13,26
> INT	word(void);
> INT	nextc(INT quote);
> INT	readc(void);
> INT	syslook(STRING w, struct sysnod syswds[]);
> INT	estabf(STRING s);
> VOID	prc(INT c);
> VOID	newline(void);
> VOID	sigchk(void);
> VOID	chkpr(CHAR c);
> VOID	copy(struct ionod *ioparg);
> extern int read(int fd, char *buf, int n);
> extern int close(int fd);
> LOCAL	INT readb(void);
> 
17c31
< word()
---
> INT word(void)
20a35
> 	REG ARGPTR	arg;
42,43c57,58
< 		argp=endstak(argp);
< 		IF !letter(argp->argval[0]) THEN wdset=0 FI
---
> 		arg=(ARGPTR)endstak(argp);
> 		IF !letter(arg->argval[0]) THEN wdset=0 FI
46c61
< 		IF argp->argval[1]==0 ANDF (d=argp->argval[0], digit(d)) ANDF (c=='>' ORF c=='<')
---
> 		IF arg->argval[1]==0 ANDF (d=arg->argval[0], digit(d)) ANDF (c=='>' ORF c=='<')
49,50c64,65
< 			IF reserv==FALSE ORF (wdval=syslook(argp->argval,reserved))==0
< 			THEN	wdarg=argp; wdval=0;
---
> 			IF reserv==FALSE ORF (wdval=syslook(arg->argval,reserved))==0
> 			THEN	wdarg=arg; wdval=0;
70,71c85,86
< nextc(quote)
< 	CHAR		quote;
---
> int
> nextc(int quote)
85c100
< readc()
---
> INT readc(void)
116c131
< LOCAL	readb()
---
> LOCAL	INT readb(void)
```

### cmd/sh/xec.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/xec.c unix-v7-c99/cmd/sh/xec.c || true
```

Expect:

```
12a13,76
> void	execexp(STRING s, UFD f);
> INT	sigchk(void);
> INT	getarg(COMPTR ac);
> STRING	*scan(INT argn);
> INT	syslook(STRING w, struct sysnod syswds[]);
> INT	setlist(REG ARGPTR arg, INT xp);
> VOID	prc(INT c);
> VOID	prs(STRING as);
> VOID	prn(INT n);
> INT	blank(void);
> INT	newline(void);
> INT	prt(L_INT t);
> INT	pathopen(REG STRING path, REG STRING name);
> STRING	getpath(STRING s);
> INT	failed(STRING s1, STRING s2);
> INT	exitsh(INT xno);
> INT	stoi(STRING icp);
> VOID	nullio(IOPTR iop);
> INT	clrsig(INT i);
> INT	getsig(INT n);
> INT	ignsig(INT n);
> INT	error(STRING s);
> INT	chktrap(void);
> INT	oldsigs(void);
> VOID	execa(STRING at[]);
> INT	done(void);
> INT	postclr(void);
> INT	settmp(void);
> INT	chkpipe(INT *pv);
> INT	rename(REG INT f1, REG INT f2);
> INT	chkopen(STRING idf);
> VOID	initio(IOPTR iop);
> INT	assnum(STRING *p, INT n);
> INT	assign(NAMPTR n, STRING v);
> INT	readvar(STRING *names);
> INT	options(INT argc, STRING *argv);
> INT	setargs(STRING argi[]);
> INT	replace(REG STRING *a, STRING v);
> DOLPTR	freeargs(DOLPTR blk);
> INT	gmatch(REG STRING s, REG STRING p);
> INT	cf(STRING s1, STRING s2);
> INT	exitset(void);
> INT	namscan(VOID (*fn)(NAMPTR));
> VOID	printnam(NAMPTR n);
> VOID	printflg(REG NAMPTR n);
> INT	push(FILE af);
> INT	pop(void);
> INT	initf(UFD fd);
> INT	estabf(REG STRING s);
> INT	trim(STRING at);
> INT	tdystak(REG STKPTR x);
> VOID	post(INT pcsid);
> INT	builtin(void);
> VOID	await(INT i);
> extern int chdir(char *p);
> extern int signal();
> extern int times(long *t);
> extern int umask(int m);
> extern int fork(void);
> extern int alarm(unsigned sec);
> extern int pause(void);
> extern int close(int fd);
> extern int dup();
> 
15c79
< SYSTAB		commands;
---
> extern SYSTAB	commands;
22,24c86
< execute(argt, execflg, pf1, pf2)
< 	TREPTR		argt;
< 	INT		*pf1, *pf2;
---
> INT execute(TREPTR argt, INT execflg, INT *pf1, INT *pf2)
49c111
< 			argn = getarg(t);
---
> 			argn = getarg((COMPTR)t);
53c115
< 			IF (internal=syslook(com[0],commands)) ORF argn==0
---
> 			IF ((internal=syslook(com[0],commands)) ORF argn==0)
88c150,151
< 	
---
> 					/* fallthrough */
> 
89a153
> 					nullio(io);
136c200,201
< 	
---
> 					/* fallthrough */
> 
140c205,206
< 	
---
> 					/* fallthrough */
> 
185a252
> 					/* fallthrough */
199c266
< 					THEN	execexp(a1,&com[2]);
---
> 					THEN	execexp(a1,(UFD)(long)&com[2]);
205c272
<                                                 int c, i
---
> 						int c, i;
222,223c289,290
< 					internal=builtin(argn,com);
< 	
---
> 					internal=builtin();
> 					(void)argn;
235c302,303
< 	
---
> 			/* fallthrough */
> 
292c360
< 				THEN	execute(t->forktre,1);
---
> 				THEN	execute(t->forktre,1,(INT *)0,(INT *)0);
298a367
> 			break;
302c371
< 			execute(t->partre,execflg);
---
> 			execute(t->partre,execflg,(INT *)0,(INT *)0);
303a373
> 			/* fallthrough */
316,317c386,387
< 			execute(t->lstlef,0);
< 			execute(t->lstrit,execflg);
---
> 			execute(t->lstlef,0,(INT *)0,(INT *)0);
> 			execute(t->lstrit,execflg,(INT *)0,(INT *)0);
321,322c391,392
< 			IF execute(t->lstlef,0)==0
< 			THEN	execute(t->lstrit,execflg);
---
> 			IF execute(t->lstlef,0,(INT *)0,(INT *)0)==0
> 			THEN	execute(t->lstrit,execflg,(INT *)0,(INT *)0);
327,328c397,398
< 			IF execute(t->lstlef,0)!=0
< 			THEN	execute(t->lstrit,execflg);
---
> 			IF execute(t->lstlef,0,(INT *)0,(INT *)0)!=0
> 			THEN	execute(t->lstrit,execflg,(INT *)0,(INT *)0);
349,350c419,420
< 				execute(t->fortre,0);
< 				IF execbrk<0 THEN execbrk=0 FI
---
> 				execute(t->fortre,0,(INT *)0,(INT *)0);
> 				IF (signed char)execbrk<0 THEN execbrk=0 FI
364,366c434,436
< 			   WHILE execbrk==0 ANDF (execute(t->whtre,0)==0)==(type==TWH)
< 			   DO i=execute(t->dotre,0);
< 			      IF execbrk<0 THEN execbrk=0 FI
---
> 			   WHILE execbrk==0 ANDF (execute(t->whtre,0,(INT *)0,(INT *)0)==0)==(type==TWH)
> 			   DO i=execute(t->dotre,0,(INT *)0,(INT *)0);
> 			      IF (signed char)execbrk<0 THEN execbrk=0 FI
374,376c444,446
< 			IF execute(t->iftre,0)==0
< 			THEN	execute(t->thtre,execflg);
< 			ELSE	execute(t->eltre,execflg);
---
> 			IF execute(t->iftre,0,(INT *)0,(INT *)0)==0
> 			THEN	execute(t->thtre,execflg,(INT *)0,(INT *)0);
> 			ELSE	execute(t->eltre,execflg,(INT *)0,(INT *)0);
383c453
< 			   t=t->swlst;
---
> 			   t=(TREPTR)t->swlst;
389c459
< 					THEN	execute(t->regcom,0);
---
> 					THEN	execute(t->regcom,0,(INT *)0,(INT *)0);
394c464
< 				IF t THEN t=t->regnxt FI
---
> 				IF t THEN t=(TREPTR)t->regnxt FI
408,410c478,479
< execexp(s,f)
< 	STRING		s;
< 	UFD		f;
---
> void
> execexp(STRING s, UFD f)
415c484
< 	THEN	estabf(s); fb.feval=f;
---
> 	THEN	estabf(s); fb.feval=(STRING *)(long)f;
419c488
< 	execute(cmd(NL, NLFLG|MTFLG),0);
---
> 	execute(cmd(NL, NLFLG|MTFLG),0,(INT *)0,(INT *)0);
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
38c41,42
< 	char	b_xmem;			/* high order core address */
---
> 	/* v7's `char b_xmem` (high 6 bits of an 18-bit UNIBUS phys
> 	 * address) is gone -- ARM uses a flat 32-bit b_un.b_addr. */
54,55c58,59
< #define	B_PHYS	020	/* Physical IO potentially using UNIBUS map */
< #define	B_MAP	040	/* This block has the UNIBUS map allocated */
---
> /* B_PHYS (physio UNIBUS-map), B_MAP (block has map allocated) and
>  * B_TAPE (ordered-write magtape) are gone -- never read on this port. */
60,62d63
< #define	B_TAPE 02000	/* this is a magtape (no bdwrite) */
< #define	B_PBUSY	04000
< #define	B_PACK	010000
64,72c65
< /*
<  * special redeclarations for
<  * the head of the queue per
<  * device driver.
<  */
< #define	b_actf	av_forw
< #define	b_actl	av_back
< #define	b_active b_bcount
< #define	b_errcnt b_resid
---
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
13d12
< #define	NINDEX	15
15,25d13
< struct group {
< 	short	g_state;
< 	char	g_index;
< 	char	g_rot;
< 	struct	group	*g_group;
< 	struct	inode	*g_inode;
< 	struct	file	*g_file;
< 	short	g_rotmask;
< 	short	g_datq;
< 	struct	chan *g_chans[NINDEX];
< };
41c29
< 		};
---
> 		} u_reg;
44,45c32
< 			struct	group	i_group;	/*  multiplexor group file */
< 		};
---
> 		} u_dev;
46a34,40
> /* Caller-side shorthand for the named inner structs (kept v7-flavoured).
>  * v7's multiplexor `struct group i_group` is gone -- the mpx subsystem
>  * isn't wired on this port and shrinking the inode union by ~80 bytes
>  * saves ~16 KB across NINODE=200 in-core inodes. */
> #define	i_addr	u_reg.i_addr
> #define	i_lastr	u_reg.i_lastr
> #define	i_rdev	u_dev.i_rdev
51c45,46
< struct inode *mpxip;		/* mpx virtual inode */
---
> /* v7 had `struct inode *mpxip` here for the mpx multiplexor server's
>  * virtual inode; never assigned on this port, so removed. */
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
5c8,10
< #define	NBUF	29		/* size of buffer cache */
---
> #define	NBUF	64		/* size of buffer cache (raised from v7's 29
> 				 * to help long-running pipelines; 64*512=32KB
> 				 * BSS, trivial on 128 MiB qemu). */
10,12c15,16
< #define	MAXUPRC	25		/* max processes per user */
< #define	SSIZE	20		/* initial stack size (*64 bytes) */
< #define	SINCR	20		/* increment of stack (*64 bytes) */
---
> /* MAXUPRC, SSIZE, NCARGS were used by sys1.c::fork/exec (deleted -- the
>  * armboot path enforces its own per-pid limits and arg-buffer size). */
14d17
< #define	CANBSIZ	256		/* max size of typewriter line */
17d19
< #define	NCALL	20		/* max simultaneous time callouts */
20d21
< #define	NCLIST	100		/* max total clist size */
25d25
< #define	NCARGS	5120		/* # characters in exec arglist */
39,40c39,41
< #define	PWAIT	30
< #define	PSLEP	40
---
> /* PWAIT (wait priority) and PSLEP (pause priority) are gone -- their
>  * only sleep() callers were sys1.c::wait and sys4.c::pause, both
>  * reimplemented in arch/arm.c using the multithreading primitives. */
51a53,59
>  *
>  * Only the v7 signal names actually referenced by this kernel are
>  * defined here.  SIGINS/IOT/EMT/FPT/BUS/SEG/SYS/TRM are gone -- never
>  * raised or named anywhere; userspace gets the long names from
>  * <signal.h> instead.  The matching numeric slots (4, 6, 7, 8, 10, 11,
>  * 12, 15) remain reserved in u_signal[NSIG]; arm.s raises 4 and 11 by
>  * literal integer (see undef_entry / pabort_entry).
56d63
< #define	SIGINS	4	/* illegal instruction */
58,60d64
< #define	SIGIOT	6	/* iot */
< #define	SIGEMT	7	/* emt */
< #define	SIGFPT	8	/* floating exception */
62,64d65
< #define	SIGBUS	10	/* bus error */
< #define	SIGSEG	11	/* segmentation violation */
< #define	SIGSYS	12	/* bad system call */
67d67
< #define	SIGTRM	15	/* Catchable termination */
76,77c76,77
< /* BSLOP can be 0 unless you have a TIU/Spider */
< #define	BSLOP	2		/* In case some device needs bigger buffers */
---
> /* BSLOP was v7 slop for TIU/Spider devices; this port has no such device. */
> #define	BSLOP	0
84c84
< #define	UBASE	0140000		/* abs. addr of user block */
---
> #ifndef NULL
86c86,88
< #define	CMASK	0		/* default mask for file creation */
---
> #endif
> /* v7 CMASK (initial u.u_cmask from main()) is unused on this port: BSS
>  * zero-init of u.u_cmask already gives the same 0. */
93,95c95,97
< #define	INFSIZE	138		/* size of per-proc info for users */
< #define	CBSIZE	14		/* number of chars in a clist block */
< #define	CROUND	017		/* clist rounding: sizeof(int *) + CBSIZE - 1*/
---
> /* UBASE (PDP-11 user-block VA) and the clist CBSIZE/CROUND constants
>  * are gone -- ARM USERBASE is in arch/arm.h, and the v7 clist subsystem
>  * (prim.c) was removed this session. */
131c133
< typedef	unsigned int	ino_t;
---
> typedef	unsigned short	ino_t;
133c135
< typedef	int		label_t[6];	/* regs 2-7 */
---
> typedef	int		label_t[10];	/* regs 2-7 */
144a147,148
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
31c34,35
< /* stat codes */
---
> /* stat codes.  v7 had SWAIT=2 between SSLEEP and SRUN but the v7 sources
>  * called it "abandoned state" -- never written or read anywhere. */
33d36
< #define	SWAIT	2		/* (abandoned state) */
39c42,45
< /* flag codes */
---
> /* flag codes.  v7's SSYS (scheduling proc 0), SLOCK (text-load swap lock),
>  * SSWAP (swap-out marker) and SULOCK (lock(2) resident pin) are gone --
>  * SSYS was never written; the others were only written, never read,
>  * because this port has no swap path. */
41,43d46
< #define	SSYS	02		/* scheduling process */
< #define	SLOCK	04		/* process cannot be swapped */
< #define	SSWAP	010		/* process is being swapped out */
46d48
< #define	SULOCK	0100		/* user settable lock in core */
69a72,73
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
20,21c20,21
< 	int	u_fper;			/* FP error register */
< 	int	u_fpsaved;		/* FP regs saved for this proc */
---
> 	/* v7 had `int u_fper, u_fpsaved` here -- never read or written on
> 	 * this port, dropped to shrink struct user (proc[] is per-process). */
26c26,27
< 	char	u_segflg;		/* IO flag: 0:user D; 1:system; 2:user I */
---
> 	char	u_segflg;		/* IO flag: 0:user; 1:system (v7's 2
> 					 * "user I" path is not used here) */
38c39
< 		};
---
> 		} u_pair;
41a43,45
> /* Caller-side shorthand for the named inner pair (kept v7-flavoured). */
> #define	r_val1	u_pair.r_val1
> #define	r_val2	u_pair.r_val2
77,86c81,83
< 	struct {			/* header of executable file */
< 		int	ux_mag;		/* magic number */
< 		unsigned ux_tsize;	/* text size */
< 		unsigned ux_dsize;	/* data size */
< 		unsigned ux_bsize;	/* bss size */
< 		unsigned ux_ssize;	/* symbol table size */
< 		unsigned ux_entloc;	/* entry location */
< 		unsigned ux_unused;
< 		unsigned ux_relflg;
< 	} u_exdata;
---
> 	/* v7 had `struct {...} u_exdata` here (the a.out header, populated
> 	 * by sys1.c::getxfile and consumed by setregs).  Both functions are
> 	 * gone; arch/arm.c::v7_exec_call parses the a.out itself. */
90c87,88
< 	short	u_fpflag;		/* unused now, will be later */
---
> 	/* v7 had `short u_fpflag` here (per its comment, "unused now, will
> 	 * be later") -- it never got a "later".  Dropped. */
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
6a9,14
> extern struct group *getgrent(void);
> extern struct group *getgrgid(int gid);
> extern struct group *getgrnam(char *name);
> extern void setgrent(void);
> extern void endgrent(void);
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
1,11c1,12
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
> /* Mirror of the kernel h/param.h label_t (R4..R11 + sp + lr); needed
>  * by cmd/ps and pstat through "../h/user.h". */
> typedef	int		label_t[10];
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
1c1,16
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
> 	cmp r0, #0
> 	bxge lr
> 	rsb r1, r0, #0
> 	ldr r2, =errno
> 	str r1, [r2]
> 	mvn r0, #0
> 	bx lr
3,24c18,22
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
26,27c24,30
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

### lib/malloc.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/malloc.c unix-v7-c99/lib/malloc.c || true
```

Expect:

```
1,57c1,8
< #ifdef debug
< #define ASSERT(p) if(!(p))botch("p");else
< botch(s)
< char *s;
< {
< 	printf("assertion botched: %s\n",s);
< 	abort();
< }
< #else
< #define ASSERT(p)
< #endif
< 
< /*	avoid break bug */
< #ifdef pdp11
< #define GRANULE 64
< #else
< #define GRANULE 0
< #endif
< /*	C storage allocator
<  *	circular first-fit strategy
<  *	works with noncontiguous, but monotonically linked, arena
<  *	each block is preceded by a ptr to the (pointer of) 
<  *	the next following block
<  *	blocks are exact number of words long 
<  *	aligned to the data type requirements of ALIGN
<  *	pointers to blocks must have BUSY bit 0
<  *	bit in ptr is 1 for busy, 0 for idle
<  *	gaps in arena are merely noted as busy blocks
<  *	last block of arena (pointed to by alloct) is empty and
<  *	has a pointer to first
<  *	idle blocks are coalesced during space search
<  *
<  *	a different implementation may need to redefine
<  *	ALIGN, NALIGN, BLOCK, BUSY, INT
<  *	where INT is integer type to which a pointer can be cast
< */
< #define INT int
< #define ALIGN int
< #define NALIGN 1
< #define WORD sizeof(union store)
< #define BLOCK 1024	/* a multiple of WORD*/
< #define BUSY 1
< #define NULL 0
< #define testbusy(p) ((INT)(p)&BUSY)
< #define setbusy(p) (union store *)((INT)(p)|BUSY)
< #define clearbusy(p) (union store *)((INT)(p)&~BUSY)
< 
< union store { union store *ptr;
< 	      ALIGN dummy[NALIGN];
< 	      int calloc;	/*calloc clears an array of integers*/
< };
< 
< static	union store allocs[2];	/*initial arena*/
< static	union store *allocp;	/*search ptr*/
< static	union store *alloct;	/*arena top*/
< static	union store *allocx;	/*for benefit of realloc*/
< char	*sbrk();
---
> /*
>  * Userland bump allocator -- the v7 libc/gen/malloc.c uses brk(2),
>  * which the C99/Armv7 kernel does not yet service.  This is the same
>  * bump scheme u.h's previous static-inline malloc used: each call
>  * advances a private brk pointer; free is a no-op.
>  */
> 
> static char *brkp = (char *)0x00060000;
60,61c11
< malloc(nbytes)
< unsigned nbytes;
---
> malloc(unsigned n)
63,120c13,19
< 	register union store *p, *q;
< 	register nw;
< 	static temp;	/*coroutines assume no auto*/
< 
< 	if(allocs[0].ptr==0) {	/*first time*/
< 		allocs[0].ptr = setbusy(&allocs[1]);
< 		allocs[1].ptr = setbusy(&allocs[0]);
< 		alloct = &allocs[1];
< 		allocp = &allocs[0];
< 	}
< 	nw = (nbytes+WORD+WORD-1)/WORD;
< 	ASSERT(allocp>=allocs && allocp<=alloct);
< 	ASSERT(allock());
< 	for(p=allocp; ; ) {
< 		for(temp=0; ; ) {
< 			if(!testbusy(p->ptr)) {
< 				while(!testbusy((q=p->ptr)->ptr)) {
< 					ASSERT(q>p&&q<alloct);
< 					p->ptr = q->ptr;
< 				}
< 				if(q>=p+nw && p+nw>=p)
< 					goto found;
< 			}
< 			q = p;
< 			p = clearbusy(p->ptr);
< 			if(p>q)
< 				ASSERT(p<=alloct);
< 			else if(q!=alloct || p!=allocs) {
< 				ASSERT(q==alloct&&p==allocs);
< 				return(NULL);
< 			} else if(++temp>1)
< 				break;
< 		}
< 		temp = ((nw+BLOCK/WORD)/(BLOCK/WORD))*(BLOCK/WORD);
< 		q = (union store *)sbrk(0);
< 		if(q+temp+GRANULE < q) {
< 			return(NULL);
< 		}
< 		q = (union store *)sbrk(temp*WORD);
< 		if((INT)q == -1) {
< 			return(NULL);
< 		}
< 		ASSERT(q>alloct);
< 		alloct->ptr = q;
< 		if(q!=alloct+1)
< 			alloct->ptr = setbusy(alloct->ptr);
< 		alloct = q->ptr = q+temp-1;
< 		alloct->ptr = setbusy(allocs);
< 	}
< found:
< 	allocp = p + nw;
< 	ASSERT(allocp<=alloct);
< 	if(q>allocp) {
< 		allocx = allocp->ptr;
< 		allocp->ptr = p->ptr;
< 	}
< 	p->ptr = setbusy(allocp);
< 	return((char *)(p+1));
---
> 	unsigned *p;
> 
> 	n = (n + 3) & ~3;
> 	p = (unsigned *)brkp;
> 	*p++ = n;
> 	brkp += n + sizeof(unsigned);
> 	return((char *)p);
123,126c22,23
< /*	freeing strategy tuned for LIFO allocation
< */
< free(ap)
< register char *ap;
---
> void
> free(char *p)
128d24
< 	register union store *p = (union store *)ap;
130,135c26
< 	ASSERT(p>clearbusy(allocs[1].ptr)&&p<=alloct);
< 	ASSERT(allock());
< 	allocp = --p;
< 	ASSERT(testbusy(p->ptr));
< 	p->ptr = clearbusy(p->ptr);
< 	ASSERT(p->ptr > allocp && p->ptr <= alloct);
---
> 	(void)p;
138,143d28
< /*	realloc(p, nbytes) reallocates a block obtained from malloc()
<  *	and freed since last call of malloc()
<  *	to have new size nbytes, and old content
<  *	returns new location, or 0 on failure
< */
< 
145,147c30
< realloc(p, nbytes)
< register union store *p;
< unsigned nbytes;
---
> realloc(char *p, unsigned n)
149,170c32,33
< 	register union store *q;
< 	union store *s, *t;
< 	register unsigned nw;
< 	unsigned onw;
< 
< 	if(testbusy(p[-1].ptr))
< 		free((char *)p);
< 	onw = p[-1].ptr - p;
< 	q = (union store *)malloc(nbytes);
< 	if(q==NULL || q==p)
< 		return((char *)q);
< 	s = p;
< 	t = q;
< 	nw = (nbytes+WORD-1)/WORD;
< 	if(nw<onw)
< 		onw = nw;
< 	while(onw--!=0)
< 		*t++ = *s++;
< 	if(q<p && q+nw>=p)
< 		(q+(q+nw-p))->ptr = allocx;
< 	return((char *)q);
< }
---
> 	char *q;
> 	unsigned i, old;
172,187c35,45
< #ifdef debug
< allock()
< {
< #ifdef longdebug
< 	register union store *p;
< 	int x;
< 	x = 0;
< 	for(p= &allocs[0]; clearbusy(p->ptr) > p; p=clearbusy(p->ptr)) {
< 		if(p==allocp)
< 			x++;
< 	}
< 	ASSERT(p==alloct);
< 	return(x==1|p==allocp);
< #else
< 	return(1);
< #endif
---
> 	if(p == 0)
> 		return(malloc(n));
> 	old = ((unsigned *)p)[-1];
> 	q = malloc(n);
> 	if(q == 0)
> 		return(0);
> 	if(old > n)
> 		old = n;
> 	for(i=0; i<old; i++)
> 		q[i] = p[i];
> 	return(q);
189d46
< #endif
```

### lib/nlist.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/nlist.c unix-v7-c99/lib/nlist.c || true
```

Expect:

```
0a1,12
> /* ARM/ELF nlist(3) -- v7's nlist parsed v7 a.out, but the C99/ARM
>  * kernel is an ELF32 image, so this walks ELF .symtab/.strtab.  The
>  * v7 C compiler prefixed every C symbol with `_'; strip one leading
>  * underscore from each search-list name before matching against the
>  * ELF symbol-string.  n_name[] is a fixed 8-byte field; we compare
>  * against the ELF name with exact-match semantics, which is enough
>  * for the kernel symbols that dmesg/ps look up (_msgbuf, _msgbufp,
>  * _proc, _file, _swapdev, _dk_xfer, etc., all <=7 chars).  n_type is
>  * mapped to v7's N_TEXT/N_DATA/N_BSS based on the ELF section's
>  * SHF_EXECINSTR/SHF_WRITE flags.
>  */
> 
2,3d13
< int a_magic[] = {A_MAGIC1, A_MAGIC2, A_MAGIC3, A_MAGIC4, 0};
< #define SPACE 100		/* number of symbols read at a time */
5,7c15,67
< nlist(name, list)
< char *name;
< struct nlist *list;
---
> int	open(char *, int);
> int	close(int);
> int	read(int, char *, int);
> long	lseek(int, long, int);
> 
> #define	ELF_NIDENT	16
> #define	ELFMAG0		0177
> #define	SHT_SYMTAB	2
> #define	SHT_STRTAB	3
> #define	SHF_WRITE	1
> #define	SHF_EXECINSTR	4
> 
> struct elfhdr {
> 	unsigned char	e_ident[ELF_NIDENT];
> 	unsigned short	e_type;
> 	unsigned short	e_machine;
> 	unsigned int	e_version;
> 	unsigned int	e_entry;
> 	unsigned int	e_phoff;
> 	unsigned int	e_shoff;
> 	unsigned int	e_flags;
> 	unsigned short	e_ehsize;
> 	unsigned short	e_phentsize;
> 	unsigned short	e_phnum;
> 	unsigned short	e_shentsize;
> 	unsigned short	e_shnum;
> 	unsigned short	e_shstrndx;
> };
> 
> struct elfshdr {
> 	unsigned int	sh_name;
> 	unsigned int	sh_type;
> 	unsigned int	sh_flags;
> 	unsigned int	sh_addr;
> 	unsigned int	sh_offset;
> 	unsigned int	sh_size;
> 	unsigned int	sh_link;
> 	unsigned int	sh_info;
> 	unsigned int	sh_addralign;
> 	unsigned int	sh_entsize;
> };
> 
> struct elfsym {
> 	unsigned int	st_name;
> 	unsigned int	st_value;
> 	unsigned int	st_size;
> 	unsigned char	st_info;
> 	unsigned char	st_other;
> 	unsigned short	st_shndx;
> };
> 
> int
> nlist(char *name, struct nlist *list)
9,13c69,80
< 	register struct nlist *p, *q;
< 	int f, n, m, i;
< 	long sa;
< 	struct exec buf;
< 	struct nlist space[SPACE];
---
> 	struct nlist *p;
> 	struct elfhdr eh;
> 	struct elfshdr sh;
> 	struct elfsym sym;
> 	char strbuf[64];
> 	char nb[9];
> 	char *sn;
> 	int f, i, j, k, nsyms;
> 	int matched;
> 	unsigned int symoff, symsz, symesz;
> 	unsigned int stroff;
> 	unsigned int secflags[64];
22,25c89,116
< 	read(f, (char *)&buf, sizeof buf);
< 	for(i=0; a_magic[i]; i++)
< 		if(a_magic[i] == buf.a_magic) break;
< 	if(a_magic[i] == 0){
---
> 	if(read(f, (char *)&eh, sizeof(eh)) != sizeof(eh)
> 	    || eh.e_ident[0] != ELFMAG0 || eh.e_ident[1] != 'E'
> 	    || eh.e_ident[2] != 'L' || eh.e_ident[3] != 'F') {
> 		close(f);
> 		return(-1);
> 	}
> 	symoff = 0;
> 	symsz = 0;
> 	symesz = sizeof(sym);
> 	stroff = 0;
> 	for(i = 0; i < eh.e_shnum && i < 64; i++) {
> 		lseek(f, (long)(eh.e_shoff + i * eh.e_shentsize), 0);
> 		if(read(f, (char *)&sh, sizeof(sh)) != sizeof(sh)) {
> 			close(f);
> 			return(-1);
> 		}
> 		secflags[i] = sh.sh_flags;
> 		if(sh.sh_type == SHT_SYMTAB) {
> 			symoff = sh.sh_offset;
> 			symsz = sh.sh_size;
> 			if(sh.sh_entsize)
> 				symesz = sh.sh_entsize;
> 			lseek(f, (long)(eh.e_shoff + sh.sh_link * eh.e_shentsize), 0);
> 			read(f, (char *)&sh, sizeof(sh));
> 			stroff = sh.sh_offset;
> 		}
> 	}
> 	if(symoff == 0 || stroff == 0) {
29,49c120,155
< 	sa = buf.a_text + (long)buf.a_data;
< 	if(buf.a_flag != 1) sa *= 2;
< 	sa += sizeof buf;
< 	lseek(f, sa, 0);
< 	n = buf.a_syms;
< 
< 	while(n){
< 		m = sizeof space;
< 		if(n < sizeof space)
< 			m = n;
< 		read(f, (char *)space, m);
< 		n -= m;
< 		for(q = space; (m -= sizeof(struct nlist)) >= 0; q++) {
< 			for(p = list; p->n_name[0]; p++) {
< 				for(i=0;i<8;i++)
< 					if(p->n_name[i] != q->n_name[i]) goto cont;
< 				p->n_value = q->n_value;
< 				p->n_type = q->n_type;
< 				break;
< 		cont:		;
< 			}
---
> 	nsyms = (int)(symsz / symesz);
> 	for(i = 0; i < nsyms; i++) {
> 		lseek(f, (long)(symoff + i * symesz), 0);
> 		if(read(f, (char *)&sym, sizeof(sym)) != sizeof(sym))
> 			break;
> 		if(sym.st_name == 0)
> 			continue;
> 		lseek(f, (long)(stroff + sym.st_name), 0);
> 		k = read(f, strbuf, sizeof(strbuf) - 1);
> 		if(k <= 0)
> 			continue;
> 		strbuf[k] = '\0';
> 		for(p = list; p->n_name[0]; p++) {
> 			for(j = 0; j < 8; j++)
> 				nb[j] = p->n_name[j];
> 			nb[8] = '\0';
> 			sn = nb;
> 			if(*sn == '_')
> 				sn++;
> 			matched = 1;
> 			for(j = 0; sn[j]; j++)
> 				if(sn[j] != strbuf[j]) {
> 					matched = 0;
> 					break;
> 				}
> 			if(!matched || strbuf[j] != '\0')
> 				continue;
> 			p->n_value = sym.st_value;
> 			if(sym.st_shndx == 0 || sym.st_shndx >= 64)
> 				p->n_type = N_UNDF;
> 			else if(secflags[sym.st_shndx] & SHF_EXECINSTR)
> 				p->n_type = N_TEXT | N_EXT;
> 			else if(secflags[sym.st_shndx] & SHF_WRITE)
> 				p->n_type = N_DATA | N_EXT;
> 			else
> 				p->n_type = N_BSS | N_EXT;
```

### sys/main.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/main.c unix-v7-c99/sys/main.c || true
```

Expect:

```
3,10d2
< #include "../h/dir.h"
< #include "../h/user.h"
< #include "../h/filsys.h"
< #include "../h/mount.h"
< #include "../h/map.h"
< #include "../h/proc.h"
< #include "../h/inode.h"
< #include "../h/seg.h"
12a5
> #include "../h/proto.h"
15,28c8,12
<  * Initialization code.
<  * Called from cold start routine as
<  * soon as a stack and segmentation
<  * have been established.
<  * Functions:
<  *	clear and free user core
<  *	turn on clock
<  *	hand craft 0th process
<  *	call all initialization routines
<  *	fork - process 0 to schedule
<  *	     - process 1 execute bootstrap
<  *
<  * loop at low address in user mode -- /etc/init
<  *	cannot be executed.
---
>  * Initialization code.  On this port the ARM-specific cold-start path
>  * (arch/arm.s -> main() -> startup() -> armboot()) drives the actual
>  * boot.  The v7 PDP-11 main body (manually set up proc[0], call
>  * cinit/binit/iinit, fork the init process, jump to sched()) is replaced
>  * by armboot()'s scheduler + ELF loader, so main() is now just glue.
30c14,15
< main()
---
> void
> main(void)
32d16
< 
34,108c18
< 	/*
< 	 * set up system process
< 	 */
< 
< 	proc[0].p_addr = ka6->r[0];
< 	proc[0].p_size = USIZE;
< 	proc[0].p_stat = SRUN;
< 	proc[0].p_flag |= SLOAD|SSYS;
< 	proc[0].p_nice = NZERO;
< 	u.u_procp = &proc[0];
< 	u.u_cmask = CMASK;
< 
< 	/*
< 	 * Initialize devices and
< 	 * set up 'known' i-nodes
< 	 */
< 
< 	clkstart();
< 	cinit();
< 	binit();
< 	iinit();
< 	rootdir = iget(rootdev, (ino_t)ROOTINO);
< 	rootdir->i_flag &= ~ILOCK;
< 	u.u_cdir = iget(rootdev, (ino_t)ROOTINO);
< 	u.u_cdir->i_flag &= ~ILOCK;
< 	u.u_rdir = NULL;
< 
< 	/*
< 	 * make init process
< 	 * enter scheduling loop
< 	 * with system process
< 	 */
< 
< 	if(newproc()) {
< 		expand(USIZE + (int)btoc(szicode));
< 		estabur((unsigned)0, btoc(szicode), (unsigned)0, 0, RO);
< 		copyout((caddr_t)icode, (caddr_t)0, szicode);
< 		/*
< 		 * Return goes to loc. 0 of user init
< 		 * code just copied out.
< 		 */
< 		return;
< 	}
< 	sched();
< }
< 
< /*
<  * iinit is called once (from main)
<  * very early in initialization.
<  * It reads the root's super block
<  * and initializes the current date
<  * from the last modified date.
<  *
<  * panic: iinit -- cannot read the super
<  * block. Usually because of an IO error.
<  */
< iinit()
< {
< 	register struct buf *cp, *bp;
< 	register struct filsys *fp;
< 
< 	(*bdevsw[major(rootdev)].d_open)(rootdev, 1);
< 	bp = bread(rootdev, SUPERB);
< 	cp = geteblk();
< 	if(u.u_error)
< 		panic("iinit");
< 	bcopy(bp->b_un.b_addr, cp->b_un.b_addr, sizeof(struct filsys));
< 	brelse(bp);
< 	mount[0].m_bufp = cp;
< 	mount[0].m_dev = rootdev;
< 	fp = cp->b_un.b_filsys;
< 	fp->s_flock = 0;
< 	fp->s_ilock = 0;
< 	fp->s_ronly = 0;
< 	time = fp->s_time;
---
> 	armboot();
125c35
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
2d1
< #include "../h/systm.h"
3a3,6
> #include "../h/proto.h"
> 
> struct map coremap[CMAPSIZ];	/* space for core allocation */
> struct map swapmap[SMAPSIZ];	/* space for swap allocation */
15,16c18,19
< malloc(mp, size)
< struct map *mp;
---
> int
> malloc(struct map *mp, int size)
29c32
< 				} while ((bp-1)->m_size = bp->m_size);
---
> 				} while (((bp-1)->m_size = bp->m_size));
43,45c46,47
< mfree(mp, size, a)
< struct map *mp;
< register int a;
---
> void
> mfree(struct map *mp, int size, int a)
50,53c52
< 	if ((bp = mp)==coremap && runin) {
< 		runin = 0;
< 		wakeup((caddr_t)&runin);	/* Wake scheduler when freeing core */
< 	}
---
> 	bp = mp;
77c76
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
2,5c2,3
< #include "../h/systm.h"
< #include "../h/seg.h"
< #include "../h/buf.h"
< #include "../h/conf.h"
---
> #include "../h/proto.h"
> #include <stdarg.h>
14a13
> void printn(long n, int b);
26,28c25,26
< printf(fmt, x1)
< register char *fmt;
< unsigned x1;
---
> void
> printf(char *fmt, ...)
30,31c28,29
< 	register c;
< 	register unsigned int *adx;
---
> 	register int c;
> 	va_list adx;
34c32
< 	adx = &x1;
---
> 	va_start(adx, fmt);
37c35,36
< 		if(c == '\0')
---
> 		if(c == '\0') {
> 			va_end(adx);
38a38
> 		}
43c43
< 		printn((long)*adx, c=='o'? 8: (c=='x'? 16:10));
---
> 		printn((long)va_arg(adx, unsigned), c=='o'? 8: (c=='x'? 16:10));
45,46c45,46
< 		s = (char *)*adx;
< 		while(c = *s++)
---
> 		s = va_arg(adx, char *);
> 		while((c = *s++))
49,50c49
< 		printn(*(long *)adx, 10);
< 		adx += (sizeof(long) / sizeof(int)) - 1;
---
> 		printn(va_arg(adx, long), 10);
52d50
< 	adx++;
59,60c57,58
< printn(n, b)
< long n;
---
> void
> printn(long n, int b)
68c66
< 	if(a = n/b)
---
> 	if((a = n/b))
79,80c77,78
< panic(s)
< char *s;
---
> void
> panic(char *s)
83d80
< 	update();
86c83
< 		idle();
---
> 		;
95,97c92,93
< prdev(str, dev)
< char *str;
< dev_t dev;
---
> void
> prdev(char *str, dev_t dev)
103,116d98
< /*
<  * deverr prints a diagnostic from
<  * a device driver.
<  * It prints the device, block number,
<  * and an octal word (usually some error
<  * status register) passed as argument.
<  */
< deverror(bp, o1, o2)
< register struct buf *bp;
< {
< 
< 	prdev("err", bp->b_dev);
< 	printf("bn=%D er=%o,%o\n", bp->b_blkno, o1, o2);
< }
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
10c10,11
< setpwent()
---
> void
> setpwent(void)
18c19,20
< endpwent()
---
> void
> endpwent(void)
27,28c29
< pwskip(p)
< register char *p;
---
> pwskip(register char *p)
37c38
< getpwent()
---
> getpwent(void)
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
4,5c5
< getpwnam(name)
< char *name;
---
> getpwnam(char *name)
8d7
< 	struct passwd *getpwent();
```

### lib/getpwuid.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/getpwuid.c unix-v7-c99/lib/getpwuid.c || true
```

Expect:

```
4,5c4
< getpwuid(uid)
< register uid;
---
> getpwuid(register int uid)
8d6
< 	struct passwd *getpwent();
```

### lib/strncat.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/strncat.c unix-v7-c99/lib/strncat.c || true
```

Expect:

```
8,10c8
< strncat(s1, s2, n)
< register char *s1, *s2;
< register n;
---
> strncat(register char *s1, register char *s2, register int n)
18c16
< 	while (*s1++ = *s2++)
---
> 	while ((*s1++ = *s2++))
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
8,10c9,11
< char	*ttyname();
< char	*getttys();
< char	*rindex();
---
> char	*ttyname(int f);
> static char *getttys(int f);
> char	*rindex(char *sp, int c);
15c16,17
< ttyslot()
---
> int
> ttyslot(void)
18c20
< 	register s, tf;
---
> 	register int s, tf;
29c31
< 	while (tp = getttys(tf)) {
---
> 	while ((tp = getttys(tf))) {
41c43
< getttys(f)
---
> getttys(int f)
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
> static char *execat(register char *s1, register char *s2, char *si);
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
18,19c19,20
< execvp(name, argv)
< char *name, **argv;
---
> int
> execvp(char *name, char **argv)
27c28
< 	register eacces = 0;
---
> 	register int eacces = 0;
41c42
< 			for (i=1; newargs[i+1]=argv[i]; i++) {
---
> 			for (i=1; (newargs[i+1]=argv[i]); i++) {
68,70c69
< execat(s1, s2, si)
< register char *s1, *s2;
< char *si;
---
> execat(register char *s1, register char *s2, char *si)
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
> static char *nvmatch(register char *s1, register char *s2);
10,11c13
< getenv(name)
< register char *name;
---
> getenv(register char *name)
30,31c32
< nvmatch(s1, s2)
< register char *s1, *s2;
---
> nvmatch(register char *s1, register char *s2)
```

### lib/atoi.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/atoi.c unix-v7-c99/lib/atoi.c || true
```

Expect:

```
1,2c1,2
< atoi(p)
< register char *p;
---
> int
> atoi(register char *p)
15a16
> 			/* fallthrough */
```

### lib/atol.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/atol.c unix-v7-c99/lib/atol.c || true
```

Expect:

```
2,3c2
< atol(p)
< register char *p;
---
> atol(register char *p)
16a16
> 			/* fallthrough */
```

### lib/index.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/index.c unix-v7-c99/lib/index.c || true
```

Expect:

```
9,10c9
< index(sp, c)
< register char *sp, c;
---
> index(register char *sp, int c)
13c12
< 		if (*sp == c)
---
> 		if (*sp == (char)c)
```

### lib/rindex.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/rindex.c unix-v7-c99/lib/rindex.c || true
```

Expect:

```
9,10c9
< rindex(sp, c)
< register char *sp, c;
---
> rindex(register char *sp, int c)
16c15
< 		if (*sp == c)
---
> 		if (*sp == (char)c)
```

### lib/strcat.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/strcat.c unix-v7-c99/lib/strcat.c || true
```

Expect:

```
7,8c7
< strcat(s1, s2)
< register char *s1, *s2;
---
> strcat(register char *s1, register char *s2)
16c15
< 	while (*s1++ = *s2++)
---
> 	while ((*s1++ = *s2++))
```

### lib/strcmp.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/strcmp.c unix-v7-c99/lib/strcmp.c || true
```

Expect:

```
5,6c5,6
< strcmp(s1, s2)
< register char *s1, *s2;
---
> int
> strcmp(register char *s1, register char *s2)
```

### lib/strcpy.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/strcpy.c unix-v7-c99/lib/strcpy.c || true
```

Expect:

```
7,8c7
< strcpy(s1, s2)
< register char *s1, *s2;
---
> strcpy(register char *s1, register char *s2)
13c12
< 	while (*s1++ = *s2++)
---
> 	while ((*s1++ = *s2++))
```

### lib/strlen.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/strlen.c unix-v7-c99/lib/strlen.c || true
```

Expect:

```
6,7c6,7
< strlen(s)
< register char *s;
---
> int
> strlen(register char *s)
9c9
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
5,7c5,6
< strncmp(s1, s2, n)
< register char *s1, *s2;
< register n;
---
> int
> strncmp(register char *s1, register char *s2, register int n)
```

### lib/strncpy.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/strncpy.c unix-v7-c99/lib/strncpy.c || true
```

Expect:

```
7,8c7
< strncpy(s1, s2, n)
< register char *s1, *s2;
---
> strncpy(register char *s1, register char *s2, int n)
10c9
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
7c8,9
< isatty(f)
---
> int
> isatty(int f)
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
6,10c7,11
< int	errno;
< int	sys_nerr;
< char	*sys_errlist[];
< perror(s)
< char *s;
---
> extern int	errno;
> extern int	sys_nerr;
> extern char	*sys_errlist[];
> void
> perror(char *s)
13c14
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
6,8c6,7
< swab(pf, pt, n)
< register short *pf, *pt;
< register n;
---
> void
> swab(register short *pf, register short *pt, register int n)
```

### lib/rand.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/rand.c unix-v7-c99/lib/rand.c || true
```

Expect:

```
3,4c3,4
< srand(x)
< unsigned x;
---
> void
> srand(unsigned x)
9c9,10
< rand()
---
> int
> rand(void)
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
2,3c3
< mktemp(as)
< char *as;
---
> mktemp(char *as)
7c7
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
13,14c14,15
< char	*strcpy();
< char	*strcat();
---
> char	*strcpy(char *a, char *b);
> char	*strcat(char *a, char *b);
17c18
< ttyname(f)
---
> ttyname(int f)
23c24
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
2c2
< static int	(*qscmp)();
---
> static int	(*qscmp)(char *, char *);
3a4,6
> static void qs1(char *a, char *l);
> static void qsexc(char *i, char *j);
> static void qstexc(char *i, char *j, char *k);
5,9c8,9
< qsort(a, n, es, fc)
< char *a;
< unsigned n;
< int es;
< int (*fc)();
---
> void
> qsort(void *a, unsigned n, int es, int (*fc)())
13c13
< 	qs1(a, a+n*es);
---
> 	qs1(a, (char *)a+n*es);
16,17c16,17
< static qs1(a, l)
< char *a, *l;
---
> static void
> qs1(char *a, char *l)
20,21c20
< 	register es;
< 	char **k;
---
> 	register int es;
30c29
< 	if((n=l-a) <= es)
---
> 	if((n=l-a) <= (unsigned)es)
87,88c86,87
< static qsexc(i, j)
< char *i, *j;
---
> static void
> qsexc(char *i, char *j)
103,104c102,103
< static qstexc(i, j, k)
< char *i, *j, *k;
---
> static void
> qstexc(char *i, char *j, char *k)
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
7,8c7
< calloc(num, size)
< unsigned num, size;
---
> calloc(unsigned num, unsigned size)
11d9
< 	char *malloc();
13c11
< 	register m;
---
> 	register int m;
26,31d23
< cfree(p, num, size)
< char *p;
< unsigned num, size;
< {
< 	free(p);
< }
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
7c7
< long tell(f)
---
> long tell(int f)
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
3,4c4,5
< system(s)
< char *s;
---
> int
> system(char *s)
13,14c14,15
< 	istat = signal(SIGINT, SIG_IGN);
< 	qstat = signal(SIGQUIT, SIG_IGN);
---
> 	istat = (int (*)())signal(SIGINT, (int)SIG_IGN);
> 	qstat = (int (*)())signal(SIGQUIT, (int)SIG_IGN);
19,20c20,21
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
15,21c16,22
< 	4*60, "AST", "ADT",		/* Atlantic */
< 	5*60, "EST", "EDT",		/* Eastern */
< 	6*60, "CST", "CDT",		/* Central */
< 	7*60, "MST", "MDT",		/* Mountain */
< 	8*60, "PST", "PDT",		/* Pacific */
< 	0, "GMT", 0,			/* Greenwich */
< 	-1
---
> 	{ 4*60, "AST", "ADT" },		/* Atlantic */
> 	{ 5*60, "EST", "EDT" },		/* Eastern */
> 	{ 6*60, "CST", "CDT" },		/* Central */
> 	{ 7*60, "MST", "MDT" },		/* Mountain */
> 	{ 8*60, "PST", "PDT" },		/* Pacific */
> 	{ 0,    "GMT", 0 },		/* Greenwich */
> 	{ -1,   0,     0 }
24c25
< char *timezone(zone, dst)
---
> char *timezone(int zone, int dst)
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
4a7
> static	char	name[9];
7c10
< getlogin()
---
> getlogin(void)
9c12
< 	register me, uf;
---
> 	register int me, uf;
16c19
< 	lseek( uf, (long)(me*sizeof(ubuf)), 0 );
---
> 	lseek( uf, (long)(me*(int)sizeof(ubuf)), 0 );
20,21c23,25
< 	ubuf.ut_name[8] = ' ';
< 	for (cp=ubuf.ut_name; *cp++!=' ';)
---
> 	strncpy(name, ubuf.ut_name, 8);
> 	name[8] = ' ';
> 	for (cp=name; *cp++!=' ';)
24c28
< 	return( ubuf.ut_name );
---
> 	return(name);
```

### lib/atof.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/atof.c unix-v7-c99/lib/atof.c || true
```

Expect:

```
5d4
< #include <math.h>
6a6,13
> #define LOGHUGE 39
> static double
> ldexp(double value, int n)
> {
> 	while (n > 0) { value *= 2.0; n--; }
> 	while (n < 0) { value *= 0.5; n++; }
> 	return(value);
> }
9,10c16
< atof(p)
< register char *p;
---
> atof(register char *p)
12c18
< 	register c;
---
> 	register int c;
15d20
< 	double ldexp();
17c22
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
3,4c3,4
< clearerr(iop)
< register struct _iobuf *iop;
---
> void
> clearerr(register struct _iobuf *iop)
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
13c14,16
< char	*_getccl();
---
> static char	*_getccl(register char *s);
> static int	_innum(int **ptr, int type, int len, int size, struct _iobuf *iop, int *eofptr);
> static int	_instr(register char *ptr, int type, int len, register struct _iobuf *iop, int *eofptr);
26,29c29,30
< _doscan(iop, fmt, argp)
< FILE *iop;
< register char *fmt;
< register int **argp;
---
> int
> _doscan(FILE *iop, register char *fmt, va_list *argp)
30a32
> 	int *slot;
44,46c46,49
< 		if (ch != '*')
< 			ptr = argp++;
< 		else
---
> 		if (ch != '*') {
> 			slot = va_arg(*argp, int *);
> 			ptr = &slot;
> 		} else
97,99c100,101
< _innum(ptr, type, len, size, iop, eofptr)
< int **ptr, *eofptr;
< struct _iobuf *iop;
---
> static int
> _innum(int **ptr, int type, int len, int size, struct _iobuf *iop, int *eofptr)
101c103
< 	extern double atof();
---
> 	extern double atof(char *s);
104c106
< 	register c, base;
---
> 	register int c, base;
135c137
< 		 || base==16 && ('a'<=c && c<='f' || 'A'<=c && c<='F')) {
---
> 		 || (base==16 && (('a'<=c && c<='f') || ('A'<=c && c<='F')))) {
205,208c207,208
< _instr(ptr, type, len, iop, eofptr)
< register char *ptr;
< register struct _iobuf *iop;
< int *eofptr;
---
> static int
> _instr(register char *ptr, int type, int len, register struct _iobuf *iop, int *eofptr)
210c210
< 	register ch;
---
> 	register int ch;
250,252c250,251
< char *
< _getccl(s)
< register char *s;
---
> static char *
> _getccl(register char *s)
254c253
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
> static int create(register char *file, int rw);
5,7c6
< _endopen(file, mode, iop)
< 	char *file, *mode;
< 	register FILE *iop;
---
> _endopen(char *file, char *mode, register FILE *iop)
56,58c55
< create(file, rw)
< 	register char *file;
< 	int rw;
---
> create(register char *file, int rw)
```

### lib/fgetc.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/fgetc.c unix-v7-c99/lib/fgetc.c || true
```

Expect:

```
3,4c3,4
< fgetc(fp)
< FILE *fp;
---
> int
> fgetc(FILE *fp)
```

### lib/fgets.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/fgets.c unix-v7-c99/lib/fgets.c || true
```

Expect:

```
4,6c4
< fgets(s, n, iop)
< char *s;
< register FILE *iop;
---
> fgets(char *s, int n, register FILE *iop)
8c6
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
3c3
< char	*malloc();
---
> char	*malloc(unsigned n);
7,8c7
< _filbuf(iop)
< 	register FILE *iop;
---
> _filbuf(register FILE *iop)
21c20
< 			iop->_base = &smallbuf[fileno(iop)];
---
> 			iop->_base = &smallbuf[(unsigned char)fileno(iop)];
```

### lib/findiop.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/findiop.c unix-v7-c99/lib/findiop.c || true
```

Expect:

```
4c4
< _findiop()
---
> _findiop(void)
```

### lib/flsbuf.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/flsbuf.c unix-v7-c99/lib/flsbuf.c || true
```

Expect:

```
3c3
< char	*malloc();
---
> char	*malloc(unsigned n);
6,8c6
< _flsbuf(c, iop)
< 	int c;
< 	register FILE *iop;
---
> _flsbuf(int c, register FILE *iop)
11c9
< 	register n, rn;
---
> 	register int n, rn;
59,60c57
< fflush(iop)
< 	register FILE *iop;
---
> fflush(register FILE *iop)
63c60
< 	register n;
---
> 	register int n;
81c78,79
< _cleanup()
---
> void
> _cleanup(void)
91,92c89
< fclose(iop)
< 	register FILE *iop;
---
> fclose(register FILE *iop)
94c91
< 	register r;
---
> 	register int r;
107,108c104,105
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
4,5c4
< fopen(file, mode)
< 	char *file, *mode;
---
> fopen(char *file, char *mode)
7c6,7
< 	FILE *_findiop(), *_endopen();
---
> 	FILE *_findiop(void);
> 	FILE *_endopen(char *file, char *mode, register FILE *iop);
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
> extern void _doprnt(char *fmt, va_list *adx, FILE *file);
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
3,4c3,4
< fputc(c, fp)
< FILE *fp;
---
> int
> fputc(int c, FILE *fp)
```

### lib/fputs.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/fputs.c unix-v7-c99/lib/fputs.c || true
```

Expect:

```
3,5c3,4
< fputs(s, iop)
< register char *s;
< register FILE *iop;
---
> int
> fputs(register char *s, register FILE *iop)
7,8c6,7
< 	register r;
< 	register c;
---
> 	register int r = 0;
> 	register int c;
10c9
< 	while (c = *s++)
---
> 	while ((c = *s++))
```

### lib/freopen.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/freopen.c unix-v7-c99/lib/freopen.c || true
```

Expect:

```
4,6c4
< freopen(file, mode, iop)
< 	char *file, *mode;
< 	register FILE *iop;
---
> freopen(char *file, char *mode, register FILE *iop)
8c6
< 	FILE *_endopen();
---
> 	FILE *_endopen(char *file, char *mode, register FILE *iop);
```

### lib/fseek.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/fseek.c unix-v7-c99/lib/fseek.c || true
```

Expect:

```
7c7
< long lseek();
---
> long lseek(int fd, long offset, int ptrname);
9,11c9,10
< fseek(iop, offset, ptrname)
< 	register FILE *iop;
< 	long offset;
---
> int
> fseek(register FILE *iop, long offset, int ptrname)
```

### lib/ftell.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/ftell.c unix-v7-c99/lib/ftell.c || true
```

Expect:

```
7c7
< long	lseek();
---
> long	lseek(int fd, long offset, int ptrname);
10,11c10
< long ftell(iop)
< FILE *iop;
---
> long ftell(FILE *iop)
14c13
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
8c8,9
< getchar()
---
> int
> getchar(void)
```

### lib/getpass.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/getpass.c unix-v7-c99/lib/getpass.c || true
```

Expect:

```
6,7c6
< getpass(prompt)
< char *prompt;
---
> getpass(char *prompt)
12c11
< 	register c;
---
> 	register int c;
15d13
< 	int (*signal())();
22c20
< 	sig = signal(SIGINT, SIG_IGN);
---
> 	sig = (int (*)())signal(SIGINT, (int)SIG_IGN);
36c34
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
4,5c4
< gets(s)
< char *s;
---
> gets(char *s)
7c6
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
> extern void _doprnt(char *fmt, va_list *adx, FILE *file);
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
8,9c8,9
< putchar(c)
< register c;
---
> int
> putchar(register int c)
11c11
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
3,4c3,4
< puts(s)
< register char *s;
---
> int
> puts(register char *s)
6c6
< 	register c;
---
> 	register int c;
8c8
< 	while (c = *s++)
---
> 	while ((c = *s++))
```

### lib/rdwr.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/rdwr.c unix-v7-c99/lib/rdwr.c || true
```

Expect:

```
3,6c3,4
< fread(ptr, size, count, iop)
< unsigned size, count;
< register char *ptr;
< register FILE *iop;
---
> int
> fread(register char *ptr, unsigned size, unsigned count, register FILE *iop)
8c6
< 	register c;
---
> 	register int c;
25,28c23,24
< fwrite(ptr, size, count, iop)
< unsigned size, count;
< register char *ptr;
< register FILE *iop;
---
> int
> fwrite(register char *ptr, unsigned size, unsigned count, register FILE *iop)
```

### lib/rew.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/rew.c unix-v7-c99/lib/rew.c || true
```

Expect:

```
3,4c3,4
< rewind(iop)
< 	register struct _iobuf *iop;
---
> void
> rewind(register struct _iobuf *iop)
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
> int	_doscan(FILE *iop, register char *fmt, va_list *argp);
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
3,5c3,4
< setbuf(iop, buf)
< register struct _iobuf *iop;
< char *buf;
---
> void
> setbuf(register struct _iobuf *iop, char *buf)
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
> extern void _doprnt(char *fmt, va_list *adx, FILE *file);
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
3,7c3,4
< _strout(string, count, adjust, file, fillch)
< register char *string;
< register count;
< int adjust;
< register struct _iobuf *file;
---
> void
> _strout(register char *string, register int count, int adjust, register struct _iobuf *file, int fillch)
```

### lib/ungetc.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/ungetc.c unix-v7-c99/lib/ungetc.c || true
```

Expect:

```
3,4c3,4
< ungetc(c, iop)
< register FILE *iop;
---
> int
> ungetc(int c, register FILE *iop)
8c8
< 	if ((iop->_flag&_IOREAD)==0 || iop->_ptr <= iop->_base)
---
> 	if ((iop->_flag&_IOREAD)==0 || iop->_ptr <= iop->_base) {
10c10
< 			*iop->_ptr++;
---
> 			iop->_ptr++;
12a13
> 	}
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
67,68c67,68
< 	5,	333,	/* 1974: Jan 6 - last Sun. in Nov */
< 	58,	303,	/* 1975: Last Sun. in Feb - last Sun in Oct */
---
> 	{ 5,  333 },	/* 1974: Jan 6 - last Sun. in Nov */
> 	{ 58, 303 },	/* 1975: Last Sun. in Feb - last Sun in Oct */
71,76c71,78
< struct tm	*gmtime();
< char		*ct_numb();
< struct tm	*localtime();
< char	*ctime();
< char	*ct_num();
< char	*asctime();
---
> struct tm	*gmtime(long *tim);
> static char	*ct_numb(register char *cp, int n);
> struct tm	*localtime(long *tim);
> char	*ctime(long *t);
> char	*asctime(struct tm *t);
> static int	sunday(register struct tm *t, register int d);
> int	dysize(int y);
> int	ftime(struct timeb *tp);
79,80c81
< ctime(t)
< long *t;
---
> ctime(long *t)
86,87c87
< localtime(tim)
< long *tim;
---
> localtime(long *tim)
91c91
< 	register daylbegin, daylend;
---
> 	register int daylbegin, daylend;
122,125c122,123
< static
< sunday(t, d)
< register struct tm *t;
< register int d;
---
> static int
> sunday(register struct tm *t, register int d)
133,134c131
< gmtime(tim)
< long *tim;
---
> gmtime(long *tim)
195,196c192
< asctime(t)
< struct tm *t;
---
> asctime(struct tm *t)
202c198,199
< 	for (ncp = "Day Mon 00 00:00:00 1900\n"; *cp++ = *ncp++;);
---
> 	for (ncp = "Day Mon 00 00:00:00 1900\n"; (*cp++ = *ncp++);)
> 		;
227c224,225
< dysize(y)
---
> int
> dysize(int y)
235,236c233
< ct_numb(cp, n)
< register char *cp;
---
> ct_numb(register char *cp, int n)
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
26,44c36,54
< 	'0', 1,
< 	ANYP+RAW+NL1+CR1, ANYP+ECHO+CR1,
< 	B300, B300,
< 	"\n\r\033;\007login: ",
< 
< 	1, 2,
< 	ANYP+RAW+NL1+CR1, ANYP+XTABS+ECHO+CRMOD+FF1,
< 	B1200, B1200,
< 	"\n\r\033;login: ",
< 
< 	2, 3,
< 	ANYP+RAW+NL1+CR1, EVENP+ECHO+FF1+CR2+TAB1+NL1,
< 	B150, B150,
< 	"\n\r\033:\006\006\017login: ",
< 
< 	3, '0',
< 	ANYP+RAW+NL1+CR1, ANYP+ECHO+CRMOD+XTABS+LCASE+CR1,
< 	B110, B110,
< 	"\n\rlogin: ",
---
> 	{ '0', 1,
> 	  ANYP+RAW+NL1+CR1, ANYP+ECHO+CR1,
> 	  B300, B300,
> 	  "\n\r\033;\007login: " },
> 
> 	{ 1, 2,
> 	  ANYP+RAW+NL1+CR1, ANYP+XTABS+ECHO+CRMOD+FF1,
> 	  B1200, B1200,
> 	  "\n\r\033;login: " },
> 
> 	{ 2, 3,
> 	  ANYP+RAW+NL1+CR1, EVENP+ECHO+FF1+CR2+TAB1+NL1,
> 	  B150, B150,
> 	  "\n\r\033:\006\006\017login: " },
> 
> 	{ 3, '0',
> 	  ANYP+RAW+NL1+CR1, ANYP+ECHO+CRMOD+XTABS+LCASE+CR1,
> 	  B110, B110,
> 	  "\n\rlogin: " },
47,50c57,60
< 	'-', '-',
< 	ANYP+RAW+NL1+CR1, ANYP+ECHO+CRMOD+XTABS+LCASE+CR1,
< 	B110, B110,
< 	"\n\rlogin: ",
---
> 	{ '-', '-',
> 	  ANYP+RAW+NL1+CR1, ANYP+ECHO+CRMOD+XTABS+LCASE+CR1,
> 	  B110, B110,
> 	  "\n\rlogin: " },
53,56c63,66
< 	'1', '1',
< 	ANYP+RAW+NL1+CR1, EVENP+ECHO+FF1+CR2+TAB1+NL1,
< 	B150, B150,
< 	"\n\r\033:\006\006\017login: ",
---
> 	{ '1', '1',
> 	  ANYP+RAW+NL1+CR1, EVENP+ECHO+FF1+CR2+TAB1+NL1,
> 	  B150, B150,
> 	  "\n\r\033:\006\006\017login: " },
59,62c69,72
< 	'2', '2',
< 	ANYP+RAW+NL1+CR1, ANYP+XTABS+ECHO+CRMOD+FF1,
< 	B9600, B9600,
< 	"\n\r\033;login: ",
---
> 	{ '2', '2',
> 	  ANYP+RAW+NL1+CR1, ANYP+XTABS+ECHO+CRMOD+FF1,
> 	  B9600, B9600,
> 	  "\n\r\033;login: " },
65,68c75,78
< 	'3', '5',
< 	ANYP+RAW+NL1+CR1, ANYP+XTABS+ECHO+CRMOD+FF1,
< 	B1200, B1200,
< 	"\n\r\033;login: ",
---
> 	{ '3', '5',
> 	  ANYP+RAW+NL1+CR1, ANYP+XTABS+ECHO+CRMOD+FF1,
> 	  B1200, B1200,
> 	  "\n\r\033;login: " },
71,74c81,84
< 	'5', '3',
< 	ANYP+RAW+NL1+CR1, ANYP+ECHO+CR1,
< 	B300, B300,
< 	"\n\r\033;\007login: ",
---
> 	{ '5', '3',
> 	  ANYP+RAW+NL1+CR1, ANYP+ECHO+CR1,
> 	  B300, B300,
> 	  "\n\r\033;\007login: " },
77,80c87,90
< 	'4', '4',
< 	ANYP+RAW, ANYP+ECHO+CRMOD+XTABS,
< 	B300, B300,
< 	"\n\rlogin: ",
---
> 	{ '4', '4',
> 	  ANYP+RAW, ANYP+ECHO+CRMOD+XTABS,
> 	  B300, B300,
> 	  "\n\rlogin: " },
83,86c93,96
< 	'i', 'i',
< 	RAW+CRMOD, CRMOD+ECHO+LCASE,
< 	0, 0,
< 	"\n\rlogin: ",
---
> 	{ 'i', 'i',
> 	  RAW+CRMOD, CRMOD+ECHO+LCASE,
> 	  0, 0,
> 	  "\n\rlogin: " },
89,92c99,102
< 	'l', 'l',
< 	ANYP+RAW/*+HUPCL*/, ANYP+ECHO/*+HUPCL*/,
< 	B300, B300,
< 	"*",
---
> 	{ 'l', 'l',
> 	  ANYP+RAW/*+HUPCL*/, ANYP+ECHO/*+HUPCL*/,
> 	  B300, B300,
> 	  "*" },
94,97c104,107
< 	'6', '6',
< 	ANYP+RAW+NL1+CR1, ANYP+ECHO,
< 	B2400, B2400,
< 	"\n\rlogin: ",
---
> 	{ '6', '6',
> 	  ANYP+RAW+NL1+CR1, ANYP+ECHO,
> 	  B2400, B2400,
> 	  "\n\rlogin: " },
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
1,2c1,4
< main(argc, argv)
< char **argv;
---
> #include <stdio.h>
> 
> int
> main(int argc, char **argv)
4c6,7
< 	extern errno;
---
> 	extern int errno;
> 	int acct(char *file);
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
> int	dosync(void);
> 
15c18,19
< main()
---
> int
> main(void)
31c35,36
< dosync()
---
> int
> dosync(void)
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
> int	makenowtime(void), updatetime(int t), run(char *file), movefile(char *file, char *dir);
> 
18,19c20,21
< main(argc, argv)
< char **argv;
---
> int
> main(int argc, char **argv)
24a27
> 	(void)argc; (void)argv;
52c55,56
< makenowtime()
---
> int
> makenowtime(void)
55d58
< 	struct tm *localtime();
62a66
> 	return(0);
65c69,70
< updatetime(t)
---
> int
> updatetime(int t)
74a80
> 	return(0);
77,78c83,84
< run(file)
< char *file;
---
> int
> run(char *file)
81,82c87
< 	register pid, i;
< 	char sbuf[64];
---
> 	register int pid, i;
85c90
< 		return;
---
> 		return(0);
89,90c94,95
< 	sprintf(sbuf, "/bin/mv %.14s %s", file, PDIR);
< 	system(sbuf);
---
> 	if (movefile(file, PDIR) < 0)
> 		exit(1);
96c101
< 	if (pid = fork()) {
---
> 	if ((pid = fork())) {
99,100c104,105
< 		wait((int *)0);
< 		unlink(file);
---
> 	wait((int *)0);
> 	unlink(file);
104,105c109,112
< 	execl("/bin/sh", "sh", file, 0);
< 	execl("/usr/bin/sh", "sh", file, 0);
---
> 	close(0);
> 	open(file, 0);
> 	execl("/bin/sh", "sh", 0);
> 	execl("/usr/bin/sh", "sh", 0);
107a115,135
> 	return(0);
> }
> 
> int
> movefile(char *file, char *dir)
> {
> 	int pid, status;
> 
> 	pid = fork();
> 	if (pid == 0) {
> 		execl("/bin/mv", "mv", file, dir, 0);
> 		execl("/usr/bin/mv", "mv", file, dir, 0);
> 		exit(1);
> 	}
> 	if (pid == -1)
> 		return(-1);
> 	while (wait(&status) != pid)
> 		;
> 	if (status)
> 		return(-1);
> 	return(0);
```

### cmd/passwd.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/passwd.c unix-v7-c99/cmd/passwd.c || true
```

Expect:

```
13,18c13,16
< struct	passwd *getpwent();
< int	endpwent();
< char	*strcpy();
< char	*crypt();
< char	*getpass();
< char	*getlogin();
---
> char	*strcpy(char *a, char *b);
> char	*crypt(char *pw, char *salt);
> char	*getpass(char *prompt);
> char	*getlogin(void);
23,24c21,22
< main(argc, argv)
< char *argv[];
---
> int
> main(int argc, char *argv[])
75c73
< 	while(c = *p++){
---
> 	while((c = *p++)){
111,113c109,111
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
45,46c45,56
< main(argc,argv)
< char **argv;
---
> int readin(char *name, struct diff *dd), number(char **lc), digit(int c);
> int getchange(FILE *b), getline(FILE *b), merge(int m1, int m2);
> int separate(char *s), change(int i, struct range *rold, int dup);
> int prange(struct range *rold);
> int keep(int i, struct range *rold, struct range *rnew);
> int skip(int i, int from, char *pr);
> int duplicate(struct range *r1, struct range *r2);
> int repos(int nchar), trouble(void);
> int edit(struct diff *diff, int dup, int j), edscript(int n);
> 
> int
> main(int argc, char **argv)
48c58
< 	register i,m,n;
---
> 	register int i,m,n;
74a85
> 	return(0);
85,87c96,97
< readin(name,dd)
< char *name;
< struct diff *dd;
---
> int
> readin(char *name, struct diff *dd)
89c99
< 	register i;
---
> 	register int i;
128,129c138,139
< number(lc)
< char **lc;
---
> int
> number(char **lc)
131c141
< 	register nn;
---
> 	register int nn;
138c148,149
< digit(c)
---
> int
> digit(int c)
143,144c154,155
< getchange(b)
< FILE *b;
---
> int
> getchange(FILE *b)
152,153c163,164
< getline(b)
< FILE *b;
---
> int
> getline(FILE *b)
155,156c166,167
< 	register i, c;
< 	for(i=0;i<sizeof(line)-1;i++) {
---
> 	register int i, c;
> 	for(i=0;i<(int)sizeof(line)-1;i++) {
169c180,181
< merge(m1,m2)
---
> int
> merge(int m1, int m2)
187c199
< 		if(!t2||t1&&d1->new.to < d2->new.from) {
---
> 		if(!t2 || (t1 && d1->new.to < d2->new.from)) {
199c211
< 		if(!t1||t2&&d2->new.to < d1->new.from) {
---
> 		if(!t1 || (t2 && d2->new.to < d1->new.from)) {
265a278
> 	return(0);
268,269c281,282
< separate(s)
< char *s;
---
> int
> separate(char *s)
271a285
> 	return(0);
278,279c292,293
< change(i,rold,dup)
< struct range *rold;
---
> int
> change(int i, struct range *rold, int dup)
285c299
< 		return;
---
> 		return(0);
287c301
< 		return;
---
> 		return(0);
290a305
> 	return(0);
296,297c311,312
< prange(rold)
< struct range *rold;
---
> int
> prange(struct range *rold)
306a322
> 	return(0);
314,315c330,331
< keep(i,rold,rnew)
< struct range *rold, *rnew;
---
> int
> keep(int i, struct range *rold, struct range *rnew)
317c333
< 	register delta;
---
> 	register int delta;
318a335
> 	(void)rold;
322a340
> 	return(0);
329,330c347,348
< skip(i,from,pr)
< char *pr;
---
> int
> skip(int i, int from, char *pr)
332c350
< 	register j,n;
---
> 	register int j,n;
347,348c365,366
< duplicate(r1,r2)
< struct range *r1, *r2;
---
> int
> duplicate(struct range *r1, struct range *r2)
350,351c368,369
< 	register c,d;
< 	register nchar;
---
> 	register int c,d;
> 	register int nchar;
367c385
< 				return;
---
> 				return(0);
375c393,394
< repos(nchar)
---
> int
> repos(int nchar)
377,378c396,397
< 	register i;
< 	for(i=0;i<2;i++) 
---
> 	register int i;
> 	for(i=0;i<2;i++)
379a399
> 	return(0);
382c402,403
< trouble()
---
> int
> trouble(void)
385a407
> 	return(0);
390,391c412,413
< edit(diff,dup,j)
< struct diff *diff;
---
> int
> edit(struct diff *diff, int dup, int j)
406c428,429
< edscript(n)
---
> int
> edscript(int n)
408c431
< 	register j,k;
---
> 	register int j,k;
420a444
> 	return(0);
```

### cmd/fortune.c

Local test:

```
diff unix-v7-c99/v7/usr/src/games/fortune.c unix-v7-c99/cmd/fortune.c || true
```

Expect:

```
6c6,7
< main()
---
> int
> main(void)
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
4a6,8
> int	getnum(char *s), random(int range), skrand(int range);
> int	score(void), getline(char *s), delete(void);
> 
14,15c18,19
< main(argc,argv)
< char	*argv[];
---
> int
> main(int argc, char *argv[])
20c24
< 	extern	delete();
---
> 	extern int delete(void);
22c26
< 	signal(SIGINT, delete);
---
> 	signal(SIGINT, (int)delete);
32c36
< 			while(types[dif] = argv[1][dif])
---
> 			while((types[dif] = argv[1][dif]))
121,122c125,126
< getline(s)
< char *s;
---
> int
> getline(char *s)
139a144
> 	return(0);
142,143c147,148
< getnum(s)
< char *s;
---
> int
> getnum(char *s)
156c161,162
< random(range)
---
> int
> random(int range)
161c167,169
< skrand(range){
---
> int
> skrand(int range)
> {
168c176,177
< score()
---
> int
> score(void)
175c184
< 	if(rights == 0)	return;
---
> 	if(rights == 0)	return(0);
182a192
> 	return(0);
185c195,196
< delete()
---
> int
> delete(void)
192a204
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
> int	setup(void), startnew(void), stateout(void), getguess(void), wordout(void),
> 	youwon(void), fatal(char *s), getword(void), pscore(void);
> double	frand(void);
14c17,18
< main(argc,argv) char **argv;
---
> int
> main(int argc, char **argv)
31c35,36
< setup()
---
> int
> setup(void)
34c39
< 	time(tvec);
---
> 	time((long *)tvec);
38a44
> 	return(0);
40c46
< double frand()
---
> double frand(void)
45c51,52
< startnew()
---
> int
> startnew(void)
55a63
> 	return(0);
57c65,66
< stateout()
---
> int
> stateout(void)
63a73
> 	return(0);
65c75,76
< getguess()
---
> int
> getguess(void)
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
100c111,112
< wordout()
---
> int
> wordout(void)
103a116
> 	return(0);
105c118,119
< youwon()
---
> int
> youwon(void)
107a122
> 	return(0);
109c124,125
< fatal(s) char *s;
---
> int
> fatal(char *s)
112a129
> 	return(0);
114c131,132
< getword()
---
> int
> getword(void)
133a152
> 	return(0);
135,136c154,155
< long int freq[]
< {	42066,	9228,	24412,	14500,	55162,
---
> long int freq[]={
> 	42066,	9228,	24412,	14500,	55162,
143c162,163
< pscore()
---
> int
> pscore(void)
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
35,36c35,39
< main(argc, argv) 
< char **argv;
---
> int	loop(void), print(void), upall(int f), update(struct tbuf *tp, int f);
> int	among(int i), newday(void), pdate(void);
> 
> int
> main(int argc, char **argv)
39c42
< 	register i;
---
> 	register int i;
92c95,96
< loop()
---
> int
> loop(void)
94c98
< 	register i;
---
> 	register int i;
100c104
< 		return;
---
> 		return(0);
104c108
< 			return;
---
> 			return(0);
108c112
< 		return;
---
> 		return(0);
125c129
< 		return;
---
> 		return(0);
134a139
> 	return(0);
137c142,143
< print()
---
> int
> print(void)
157a164
> 	return(0);
160c167,168
< upall(f)
---
> int
> upall(int f)
165a174
> 	return(0);
168,169c177,178
< update(tp, f)
< struct tbuf *tp;
---
> int
> update(struct tbuf *tp, int f)
186c195
< 		return;
---
> 		return(0);
189c198
< 		return;
---
> 		return(0);
200a210
> 	return(0);
203c213,214
< among(i)
---
> int
> among(int i)
205c216
< 	register j, k;
---
> 	register int j, k;
223c234,235
< newday()
---
> int
> newday(void)
227c239
< 	struct tm *localtime();
---
> 	struct tm *localtime(long *tim);
237a250
> 	return(0);
240c253,254
< pdate()
---
> int
> pdate(void)
243c257
< 	char *ctime();
---
> 	char *ctime(long *);
246c260
< 		return;
---
> 		return(0);
248a263
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
55,56c56
< char	*prefix();
< FILE	*popen();
---
> char	*prefix(char *begin, char *full);
58,59c58,64
< main(argc, argv)
< char **argv;
---
> FILE	*openjob(char *name);
> int	makeutime(char *pp), makeuday(int argc, char **argv);
> int	filename(char *dir, int y, int d, int t);
> int	onintr(int sig), getpwd(char *buf, int nbuf);
> 
> int
> main(int argc, char **argv)
61,62c66,67
< 	extern onintr();
< 	register c;
---
> 	extern int onintr(int sig);
> 	register int c;
64d68
< 	FILE *pwfil;
92,95c96,98
< 	if (signal(SIGINT, SIG_IGN) != SIG_IGN)
< 		signal(SIGINT, onintr);
< 	file = fopen(fname, "a");
< 	chmod(fname, 0644);
---
> 	if ((int (*)())signal(SIGINT, (int)SIG_IGN) != (int (*)())SIG_IGN)
> 		signal(SIGINT, (int)onintr);
> 	file = openjob(fname);
100c103
< 	if ((pwfil = popen("pwd", "r")) == NULL) {
---
> 	if (getpwd(pwbuf, sizeof(pwbuf)) < 0) {
104,105d106
< 	fgets(pwbuf, 100, pwfil);
< 	pclose(pwfil);
110c111,114
< 			fprintf(file, "%s\n", *ep++);
---
> 			if (index(*ep, '='))
> 				fprintf(file, "%s\n", *ep++);
> 			else
> 				ep++;
118,119c122,123
< makeutime(pp)
< char *pp; 
---
> FILE *
> openjob(char *name)
121c125,172
< 	register val;
---
> 	int fd;
> 
> 	file = fopen(name, "a");
> 	if (file == NULL) {
> 		fd = creat(name, 0644);
> 		if (fd >= 0)
> 			close(fd);
> 		file = fopen(name, "a");
> 	}
> 	chmod(name, 0644);
> 	return(file);
> }
> 
> int
> getpwd(char *buf, int nbuf)
> {
> 	int fd[2], status;
> 	register int n;
> 
> 	if (pipe(fd) < 0)
> 		return(-1);
> 	if (fork() == 0) {
> 		close(fd[0]);
> 		dup(fd[1] | 0100, 1);
> 		close(fd[1]);
> 		execl("/bin/pwd", "pwd", 0);
> 		exit(1);
> 	}
> 	close(fd[1]);
> 	n = read(fd[0], buf, nbuf-1);
> 	close(fd[0]);
> 	wait(&status);
> 	if (n <= 0 || status)
> 		return(-1);
> 	buf[n] = '\0';
> 	n = 0;
> 	while (buf[n])
> 		if (buf[n++] == '\n') {
> 			buf[n] = '\0';
> 			break;
> 		}
> 	return(0);
> }
> 
> int
> makeutime(char *pp)
> {
> 	register int val;
147c198
< 
---
> 			/* fallthrough */
197a249
> 	return(0);
201,202c253,254
< makeuday(argc,argv)
< char **argv;
---
> int
> makeuday(int argc, char **argv)
273,274c325
< prefix(begin, full)
< char *begin, *full;
---
> prefix(char *begin, char *full)
277c328
< 	while (c = *begin++) {
---
> 	while ((c = *begin++)) {
288,289c339,340
< filename(dir, y, d, t)
< char *dir;
---
> int
> filename(char *dir, int y, int d, int t)
291c342
< 	register i;
---
> 	register int i;
297c348
< 			return;
---
> 			return(0);
301c352,353
< onintr()
---
> int
> onintr(int sig)
302a355
> 	(void)sig;
304a358
> 	return(0);
```

### cmd/cron.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/cron.c unix-v7-c99/cmd/cron.c || true
```

Expect:

```
18,20c18,20
< struct	tm *localtime();
< char	*malloc();
< char	*realloc();
---
> struct	tm *localtime(long *tim);
> char	*malloc(unsigned n);
> char	*realloc(char *p, unsigned n);
25c25,29
< main()
---
> int	slp(void), ex(char *s), init(void), number(register int c);
> int	open(char *path, int mode), close(int fd);
> 
> int
> main(void)
28c32
< 	char *cmp();
---
> 	char *cmp(char *p, int v);
29a34
> 	struct stat cstat;
36,40c41,47
< 	freopen("/", "r", stdout);
< 	freopen("/", "r", stderr);
< 	signal(SIGHUP, SIG_IGN);
< 	signal(SIGINT, SIG_IGN);
< 	signal(SIGQUIT, SIG_IGN);
---
> 	close(1);
> 	open("/", 0);
> 	close(2);
> 	open("/", 0);
> 	signal(SIGHUP, (int)SIG_IGN);
> 	signal(SIGINT, (int)SIG_IGN);
> 	signal(SIGQUIT, (int)SIG_IGN);
45,46c52,70
< 	for (;; itime+=60, slp()) {
< 		struct stat cstat;
---
> 	if (stat(crontab, &cstat) != -1) {
> 		filetime = cstat.st_mtime;
> 		init();
> 		loct = localtime(&itime);
> 		loct->tm_mon++;
> 		for(cp = list; *cp != EOS;) {
> 			flag = 0;
> 			cp = cmp(cp, loct->tm_min);
> 			cp = cmp(cp, loct->tm_hour);
> 			cp = cmp(cp, loct->tm_mday);
> 			cp = cmp(cp, loct->tm_mon);
> 			cp = cmp(cp, loct->tm_wday);
> 			if(flag == 0)
> 				ex(cp);
> 			while(*cp++ != 0)
> 				;
> 		}
> 	}
> 	pause();
47a72
> 	for (;; itime+=60, slp()) {
70a96
> 	return(0);
74,75c100
< cmp(p, v)
< char *p;
---
> cmp(char *p, int v)
110c135,136
< slp()
---
> int
> slp(void)
112c138
< 	register i;
---
> 	register int i;
118a145,147
> 	else
> 		sleep(1);
> 	return(0);
121,122c150,151
< ex(s)
< char *s;
---
> int
> ex(char *s)
124,129d152
< 	int st;
< 
< 	if(fork()) {
< 		wait(&st);
< 		return;
< 	}
131c154
< 		exit(0);
---
> 		return(0);
134a158
> 	return(0);
137c161,162
< init()
---
> int
> init(void)
139c164
< 	register i, c;
---
> 	register int i, c;
232c257
< 			return;
---
> 			return(0);
239,240c264,265
< number(c)
< register c;
---
> int
> number(register int c)
242c267
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
42,44c42,48
< struct	passwd	*getpwent();
< char	*malloc();
< char	*copy();
---
> char	*malloc(unsigned n);
> char	*copy(char *s);
> int	scanf(char *fmt, ...);
> 
> int	check(char *file), acct(register struct dinode *ip);
> int	bread(unsigned bno, char *buf, int cnt);
> int	qcmp(const void *vp1, const void *vp2), report(void);
46,47c50,51
< main(argc, argv)
< char **argv;
---
> int
> main(int argc, char **argv)
87,88c91,92
< check(file)
< char *file;
---
> int
> check(char *file)
91c95
< 	register c;
---
> 	register int c;
96c100
< 		return;
---
> 		return(0);
115a120
> 	return(0);
118,119c123,124
< acct(ip)
< register struct dinode *ip;
---
> int
> acct(register struct dinode *ip)
121c126
< 	register n;
---
> 	register int n;
123c128
< 	static fino;
---
> 	static int fino;
126c131
< 		return;
---
> 		return(0);
129c134
< 			return;
---
> 			return(0);
136c141
< 		return;
---
> 		return(0);
139c144
< 		return;
---
> 		return(0);
146,149c151,154
< 				return;
< 		if (fino > ino)
< 			return;
< 		if (fino<ino) {
---
> 				return(0);
> 		if (fino > (int)ino)
> 			return(0);
> 		if (fino<(int)ino) {
155c160
< 		if (np = du[ip->di_uid].name)
---
> 		if ((np = du[ip->di_uid].name))
167a173
> 	return(0);
170,172c176,177
< bread(bno, buf, cnt)
< unsigned bno;
< char *buf;
---
> int
> bread(unsigned bno, char *buf, int cnt)
179a185
> 	return(0);
182,183c188,189
< qcmp(p1, p2)
< register struct du *p1, *p2;
---
> int
> qcmp(const void *vp1, const void *vp2)
184a191
> 	register const struct du *p1 = vp1, *p2 = vp2;
192c199,200
< report()
---
> int
> report(void)
194c202
< 	register i;
---
> 	register int i;
197c205
< 		return;
---
> 		return(0);
206c214
< 		return;
---
> 		return(0);
211c219
< 			return;
---
> 			return(0);
219a228
> 	return(0);
223,224c232
< copy(s)
< char *s;
---
> copy(char *s)
227c235
< 	register n;
---
> 	register int n;
232c240
< 	for(n=0; p[n] = s[n]; n++)
---
> 	for(n=0; (p[n] = s[n]); n++)
```

### cmd/dump.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/dump.c unix-v7-c99/cmd/dump.c || true
```

Expect:

```
39,41c39,41
< char	*ctime();
< char	*prdate();
< long	atol();
---
> char	*ctime(long *t);
> char	*prdate(time_t d);
> long	atol(register char *p);
46,52c46,60
< int	mark();
< int	add();
< int	dump();
< int	tapsrec();
< int	dmpspc();
< int	dsrch();
< int	nullf();
---
> int	mark(struct dinode *ip);
> int	add(struct dinode *ip);
> int	dump(struct dinode *ip);
> int	tapsrec(daddr_t d);
> int	dmpspc(daddr_t *dp, int n);
> int	dsrch(daddr_t d);
> int	nullf(void);
> int	pass(int (*fn)(), short *map), otape(void);
> int	bread(daddr_t da, char *ba, int c), spclrec(void);
> int	bitmap(short *map, int typ), bmapest(short *map);
> int	CLR(register short *map), getitime(void), putitime(void);
> int	est(struct dinode *ip);
> int	indir(daddr_t d, int (*fn1)(), int (*fn2)(), int n);
> int	flusht(void), taprec(char *dp);
> int	l3tol(long *lp, char *cp, int n);
58,59c66,67
< main(argc, argv)
< char *argv[];
---
> int
> main(int argc, char *argv[])
62c70
< 	register i;
---
> 	register int i;
175,177c183,184
< pass(fn, map)
< int (*fn)();
< short *map;
---
> int
> pass(int (*fn)(), short *map)
179c186
< 	register i, j;
---
> 	register int i, j;
210a218
> 	return(0);
213,215c221,222
< icat(ip, fn1, fn2)
< struct	dinode	*ip;
< int (*fn1)(), (*fn2)();
---
> int
> icat(struct dinode *ip, int (*fn1)(), int (*fn2)())
217c224
< 	register i;
---
> 	register int i;
228a236
> 	return(0);
231,233c239,240
< indir(d, fn1, fn2, n)
< daddr_t d;
< int (*fn1)(), (*fn2)();
---
> int
> indir(daddr_t d, int (*fn1)(), int (*fn2)(), int n)
235c242
< 	register i;
---
> 	register int i;
242c249
< 		for(i=0; i<NINDIR; i++) {
---
> 		for(i=0; i<(int)NINDIR; i++) {
249c256
< 		for(i=0; i<NINDIR; i++) {
---
> 		for(i=0; i<(int)NINDIR; i++) {
254a262
> 	return(0);
257,258c265,266
< mark(ip)
< struct dinode *ip;
---
> int
> mark(struct dinode *ip)
260c268
< 	register f;
---
> 	register int f;
264c272
< 		return;
---
> 		return(0);
272c280
< 			return;
---
> 			return(0);
274a283
> 	return(0);
277,278c286,287
< add(ip)
< struct dinode *ip;
---
> int
> add(struct dinode *ip)
282c291
< 		return;
---
> 		return(0);
293a303
> 	return(0);
296,297c306,307
< dump(ip)
< struct dinode *ip;
---
> int
> dump(struct dinode *ip)
299c309
< 	register i;
---
> 	register int i;
312c322
< 		return;
---
> 		return(0);
314a325
> 	return(0);
317,318c328,329
< dmpspc(dp, n)
< daddr_t *dp;
---
> int
> dmpspc(daddr_t *dp, int n)
320c331
< 	register i, t;
---
> 	register int i, t;
329a341
> 	return(0);
332,333c344,345
< bitmap(map, typ)
< short *map;
---
> int
> bitmap(short *map, int typ)
335c347
< 	register i, n;
---
> 	register int i, n;
343c355
< 		return;
---
> 		return(0);
351a364
> 	return(0);
354c367,368
< spclrec()
---
> int
> spclrec(void)
356c370
< 	register i, *ip, s;
---
> 	register int i, *ip, s;
363c377
< 	for(i=0; i<BSIZE/sizeof(*ip); i++)
---
> 	for(i=0; i<(int)(BSIZE/sizeof(*ip)); i++)
366a381
> 	return(0);
369,370c384,385
< dsrch(d)
< daddr_t d;
---
> int
> dsrch(daddr_t d)
373c388
< 	register i;
---
> 	register int i;
378c393
< 		return;
---
> 		return(0);
380c395
< 	for(i=0; i<DIRPB; i++) {
---
> 	for(i=0; i<(int)DIRPB; i++) {
393c408
< 			return;
---
> 			return(0);
397a413
> 	return(0);
400c416,417
< nullf()
---
> int
> nullf(void)
401a419
> 	return(0);
404,406c422,423
< bread(da, ba, c)
< daddr_t da;
< char *ba;
---
> int
> bread(daddr_t da, char *ba, int c)
408c425
< 	register n;
---
> 	register int n;
413a431
> 	return(0);
416,417c434,435
< CLR(map)
< register short *map;
---
> int
> CLR(register short *map)
419c437
< 	register n;
---
> 	register int n;
424a443
> 	return(0);
432,433c451,452
< taprec(dp)
< char *dp;
---
> int
> taprec(char *dp)
435c454
< 	register i;
---
> 	register int i;
443a463
> 	return(0);
446,447c466,467
< tapsrec(d)
< daddr_t d;
---
> int
> tapsrec(daddr_t d)
451c471
< 		return;
---
> 		return(0);
456a477
> 	return(0);
459c480,481
< flusht()
---
> int
> flusht(void)
462c484
< 	register i, si;
---
> 	register int i, si;
490a513
> 	return(0);
493c516,517
< otape()
---
> int
> otape(void)
504a529
> 	return(0);
508,509c533
< prdate(d)
< time_t d;
---
> prdate(time_t d)
520c544,545
< getitime()
---
> int
> getitime(void)
522c547
< 	register i, df;
---
> 	register int i, df;
545c570
< 		return;
---
> 		return(0);
561c586,587
< putitime()
---
> int
> putitime(void)
563c589
< 	register i, n, df;
---
> 	register int i, n, df;
568c594
< 		return;
---
> 		return(0);
608a635
> 	return(0);
611,612c638,639
< est(ip)
< struct dinode *ip;
---
> int
> est(struct dinode *ip)
623a651
> 	return(0);
626,627c654,655
< bmapest(map)
< short *map;
---
> int
> bmapest(short *map)
629c657
< 	register i, n;
---
> 	register int i, n;
636c664
< 		return;
---
> 		return(0);
638a667
> 	return(0);
```

### cmd/dumpdir.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/dumpdir.c unix-v7-c99/cmd/dumpdir.c || true
```

Expect:

```
51,52c51,77
< main(argc, argv)
< char *argv[];
---
> struct spcl;
> int	readhdr(struct spcl *b);
> int	checkvol(struct spcl *b, int t);
> int	pass1(void);
> int	printem(char *prefix, ino_t inum);
> int	gethead(struct spcl *buf);
> int	checktype(struct spcl *b, int t);
> int	readbits(short *m);
> int	flsh(void);
> int	getfile(ino_t n, int (*f1)(), int (*f2)(), long size);
> int	putent(char *cp);
> int	mseek(daddr_t pt);
> int	getent(char *bf);
> int	direq(char *s1, char *s2);
> int	search(ino_t inum);
> int	readtape(char *b);
> int	clearbuf(char *cp);
> int	flsht(void);
> int	copy(char *f, char *t, int s);
> int	writec(int c);
> int	readc(void);
> int	checksum(int *b);
> int	putdir(char *b);
> int	null(void);
> 
> int
> main(int argc, char *argv[])
54c79
< 	extern char *ctime();
---
> 	extern char *ctime(long *t);
86c111
< 	i = 0;
---
> int	i = 0;
91c116,117
< pass1()
---
> int
> pass1(void)
93c119
< 	register i;
---
> 	register int i;
95c121
< 	int	putdir(), null();
---
> 	int	putdir(char *b), null(void);
113c139
< 			return;
---
> 			return(0);
127,129c153,154
< printem(prefix, inum)
< char *prefix;
< ino_t	inum;
---
> int
> printem(char *prefix, ino_t inum)
139c164
< 	return;
---
> 	return(0);
145c170
< 			return;
---
> 			return(0);
169,172c194,195
< getfile(n, f1, f2, size)
< ino_t	n;
< int	(*f2)(), (*f1)();
< long	size;
---
> int
> getfile(ino_t n, int (*f1)(), int (*f2)(), long size)
174c197
< 	register i;
---
> 	register int i;
177a201
> 	(void)n;
187c211
< 			return;
---
> 			return(0);
205c229
< 				return;
---
> 				return(0);
215,216c239,240
< readtape(b)
< char *b;
---
> int
> readtape(char *b)
218c242
< 	register i;
---
> 	register int i;
249c273
< 			return;
---
> 			return(0);
252a277
> 	return(0);
255c280,281
< flsht()
---
> int
> flsht(void)
257a284
> 	return(0);
260,261c287,288
< copy(f, t, s)
< register char *f, *t;
---
> int
> copy(register char *f, register char *t, int s)
263c290
< 	register i;
---
> 	register int i;
268a296
> 	return(0);
271,272c299,300
< clearbuf(cp)
< register char *cp;
---
> int
> clearbuf(register char *cp)
274c302
< 	register i;
---
> 	register int i;
279a308
> 	return(0);
286,287c315,316
< putent(cp)
< char	*cp;
---
> int
> putent(char *cp)
289c318
< 	register i;
---
> 	register int i;
291c320
< 	for (i = 0; i < sizeof(ino_t); i++)
---
> 	for (i = 0; i < (int)sizeof(ino_t); i++)
296c325
< 			return;
---
> 			return(0);
298c327
< 	return;
---
> 	return(0);
301,302c330,331
< getent(bf)
< register char *bf;
---
> int
> getent(register char *bf)
304c333
< 	register i;
---
> 	register int i;
306c335
< 	for (i = 0; i < sizeof(ino_t); i++)
---
> 	for (i = 0; i < (int)sizeof(ino_t); i++)
310,311c339,340
< 			return;
< 	return;
---
> 			return(0);
> 	return(0);
317,318c346,347
< writec(c)
< char c;
---
> int
> writec(int c)
319a349
> 	char cc = c;
321c351,352
< 	fwrite(&c, 1, 1, df);
---
> 	fwrite(&cc, 1, 1, df);
> 	return(0);
324c355,356
< readc()
---
> int
> readc(void)
332,333c364,365
< mseek(pt)
< daddr_t pt;
---
> int
> mseek(daddr_t pt)
335a368
> 	return(0);
338c371,372
< flsh()
---
> int
> flsh(void)
340a375
> 	return(0);
347,348c382,383
< search(inum)
< ino_t	inum;
---
> int
> search(ino_t inum)
350c385
< 	register low, high, probe;
---
> 	register int low, high, probe;
368,369c403,404
< direq(s1, s2)
< register char *s1, *s2;
---
> int
> direq(register char *s1, register char *s2)
371c406
< 	register i;
---
> 	register int i;
386,387c421,422
< gethead(buf)
< struct spcl *buf;
---
> int
> gethead(struct spcl *buf)
398,400c433,434
< checktype(b, t)
< struct	spcl *b;
< int	t;
---
> int
> checktype(struct spcl *b, int t)
406,407c440,441
< checksum(b)
< int *b;
---
> int
> checksum(int *b)
409c443
< 	register i, j;
---
> 	register int i, j;
423,425c457,458
< checkvol(b, t)
< struct spcl *b;
< int t;
---
> int
> checkvol(struct spcl *b, int t)
432,433c465,466
< readhdr(b)
< struct	spcl *b;
---
> int
> readhdr(struct spcl *b)
442,443c475,476
< putdir(b)
< char *b;
---
> int
> putdir(char *b)
446c479
< 	register i;
---
> 	register int i;
452a486
> 	return(0);
458,459c492,493
< readbits(m)
< short	*m;
---
> int
> readbits(short *m)
461c495
< 	register i;
---
> 	register int i;
470a505
> 	return(0);
473c508
< null() { ; }
---
> int null(void) { return(0); }
```

### cmd/restor.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/restor.c unix-v7-c99/cmd/restor.c || true
```

Expect:

```
84,85c84,128
< main(argc, argv)
< char *argv[];
---
> struct spcl;
> struct dinode;
> int	doit(int command, int argc, char *argv[]);
> int	readhdr(struct spcl *b);
> int	checkvol(struct spcl *b, int t);
> int	pass1(void);
> int	readbits(short *m);
> int	gethead(struct spcl *buf);
> int	checktype(struct spcl *b, int t);
> int	ishead(struct spcl *buf);
> int	readtape(char *b);
> int	flsht(void);
> int	getfile(ino_t n, int (*f1)(), int (*f2)(), long size);
> int	psearch(char *n);
> int	getdino(ino_t inum, struct dinode *b);
> int	putdino(ino_t inum, struct dinode *b);
> int	itrunc(struct dinode *ip);
> int	clri(struct dinode *ip);
> int	dread(daddr_t bno, char *buf, int cnt);
> int	dwrite(daddr_t bno, char *b);
> int	rstrfile(char *b, long s);
> int	rstrskip(char *b, long s);
> int	xtrfile(char *b, long size);
> int	skip(void);
> int	checksum(int *b);
> int	putent(char *cp);
> int	putdir(char *b);
> int	null(void);
> int	copy(char *f, char *t, int s);
> int	clearbuf(char *cp);
> int	writec(int c);
> int	readc(void);
> int	mseek(daddr_t pt);
> int	getent(char *bf);
> int	direq(char *s1, char *s2);
> int	flsh(void);
> int	bfree(daddr_t bn);
> int	tloop(daddr_t bn, int f1, int f2);
> int	l3tol(), ltol3();
> daddr_t	balloc(void);
> daddr_t	bmap(daddr_t iaddr[NADDR], daddr_t bn);
> ino_t	search(ino_t inum, char *cp);
> 
> int
> main(int argc, char *argv[])
89c132
< 	int done();
---
> 	int done(void);
120,123c163,166
< 		if (signal(SIGINT, done) == SIG_IGN)
< 			signal(SIGINT, SIG_IGN);
< 		if (signal(SIGTERM, done) == SIG_IGN)
< 			signal(SIGTERM, SIG_IGN);
---
> 		if (signal(SIGINT, (int)done) == (int)SIG_IGN)
> 			signal(SIGINT, (int)SIG_IGN);
> 		if (signal(SIGTERM, (int)done) == (int)SIG_IGN)
> 			signal(SIGTERM, (int)SIG_IGN);
143,146c186,187
< doit(command, argc, argv)
< char	command;
< int	argc;
< char	*argv[];
---
> int
> doit(int command, int argc, char *argv[])
148,149c189,190
< 	extern char *ctime();
< 	register i, k;
---
> 	extern char *ctime(long *t);
> 	register int i, k;
152c193
< 	int	xtrfile(), skip();
---
> 	int	xtrfile(char *b, long size), skip(void);
154c195
< 	int	rstrfile(), rstrskip();
---
> 	int	rstrfile(char *b, long s), rstrskip(char *b, long s);
179c220
< 		return;
---
> 		return(0);
208c249
< 			return;
---
> 			return(0);
251c292
< 					return;
---
> 				return(0);
300c341
< 			if (gets(tbf) == EOF) {
---
> 			if ((int)gets(tbf) == EOF) {
340c381
< 				return;
---
> 				return(0);
397a439
> 	return(0);
405c447,448
< pass1()
---
> int
> pass1(void)
407c450
< 	register i;
---
> 	register int i;
409c452
< 	int	putdir(), null();
---
> 	int	putdir(char *b), null();
427c470
< 			return;
---
> 			return(0);
446,449c489,490
< getfile(n, f1, f2, size)
< ino_t	n;
< int	(*f2)(), (*f1)();
< long	size;
---
> int
> getfile(ino_t n, int (*f1)(), int (*f2)(), long size)
451c492
< 	register i;
---
> 	register int i;
466c507
< 			return;
---
> 			return(0);
485c526
< 				return;
---
> 				return(0);
495,496c536,537
< readtape(b)
< char *b;
---
> int
> readtape(char *b)
498c539
< 	register i;
---
> 	register int i;
533c574
< 			return;
---
> 			return(0);
536a578
> 	return(0);
539c581,582
< flsht()
---
> int
> flsht(void)
541a585
> 	return(0);
544,545c588,589
< copy(f, t, s)
< register char *f, *t;
---
> int
> copy(register char *f, register char *t, int s)
547c591
< 	register i;
---
> 	register int i;
552a597
> 	return(0);
555,556c600,601
< clearbuf(cp)
< register char *cp;
---
> int
> clearbuf(register char *cp)
558c603
< 	register i;
---
> 	register int i;
563a609
> 	return(0);
571,572c617,618
< putent(cp)
< char	*cp;
---
> int
> putent(char *cp)
574c620
< 	register i;
---
> 	register int i;
576c622
< 	for (i = 0; i < sizeof(ino_t); i++)
---
> 	for (i = 0; i < (int)sizeof(ino_t); i++)
581c627
< 			return;
---
> 			return(0);
583c629
< 	return;
---
> 	return(0);
586,587c632,633
< getent(bf)
< register char *bf;
---
> int
> getent(register char *bf)
589c635
< 	register i;
---
> 	register int i;
591c637
< 	for (i = 0; i < sizeof(ino_t); i++)
---
> 	for (i = 0; i < (int)sizeof(ino_t); i++)
595,596c641,642
< 			return;
< 	return;
---
> 			return(0);
> 	return(0);
602,603c648,649
< writec(c)
< char c;
---
> int
> writec(int c)
610a657
> 	return(0);
613c660,661
< readc()
---
> int
> readc(void)
622,623c670,671
< mseek(pt)
< daddr_t pt;
---
> int
> mseek(daddr_t pt)
626a675
> 	return(0);
629c678,679
< flsh()
---
> int
> flsh(void)
631a682
> 	return(0);
639,641c690
< search(inum, cp)
< ino_t	inum;
< char	*cp;
---
> search(ino_t inum, char *cp)
643c692
< 	register i;
---
> 	register int i;
665,666c714,715
< psearch(n)
< char	*n;
---
> int
> psearch(char *n)
693,694c742,743
< direq(s1, s2)
< register char *s1, *s2;
---
> int
> direq(register char *s1, register char *s2)
696c745
< 	register i;
---
> 	register int i;
712,714c761,762
< dwrite(bno, b)
< daddr_t	bno;
< char	*b;
---
> int
> dwrite(daddr_t bno, char *b)
716c764
< 	register i;
---
> 	register int i;
735a784
> 	return(0);
738,740c787,788
< dread(bno, buf, cnt)
< daddr_t bno;
< char *buf;
---
> int
> dread(daddr_t bno, char *buf, int cnt)
742c790
< 	register i, j;
---
> 	register int i, j;
751c799
< 			return;
---
> 			return(0);
771a820
> 	return(0);
779,780c828,829
< clri(ip)
< struct dinode *ip;
---
> int
> clri(struct dinode *ip)
787a837
> 	return(0);
793,794c843,844
< itrunc(ip)
< register struct dinode *ip;
---
> int
> itrunc(register struct dinode *ip)
796c846
< 	register i;
---
> 	register int i;
800c850
< 		return;
---
> 		return(0);
803c853
< 		return;
---
> 		return(0);
826a877
> 	return(0);
829,831c880,881
< tloop(bn, f1, f2)
< daddr_t	bn;
< int	f1, f2;
---
> int
> tloop(daddr_t bn, int f1, int f2)
833c883
< 	register i;
---
> 	register int i;
850a901
> 	return(0);
853,854c904,905
< bfree(bn)
< daddr_t	bn;
---
> int
> bfree(daddr_t bn)
856c907
< 	register i;
---
> 	register int i;
863c914
< 		fbuf.df_nfree = sblock.s_nfree;
---
> 		fbuf.frees.df_nfree = sblock.s_nfree;
865c916
< 			fbuf.df_free[i] = sblock.s_free[i];
---
> 			fbuf.frees.df_free[i] = sblock.s_free[i];
869a921
> 	return(0);
876c928
< balloc()
---
> balloc(void)
879c931
< 	register i;
---
> 	register int i;
896c948
< 		sblock.s_nfree = fbuf.df_nfree;
---
> 		sblock.s_nfree = fbuf.frees.df_nfree;
898c950
< 			sblock.s_free[i] = fbuf.df_free[i];
---
> 			sblock.s_free[i] = fbuf.frees.df_free[i];
910,912c962
< bmap(iaddr, bn)
< daddr_t	iaddr[NADDR];
< daddr_t	bn;
---
> bmap(daddr_t iaddr[NADDR], daddr_t bn)
914c964
< 	register i;
---
> 	register int i;
976,977c1026,1027
< gethead(buf)
< struct spcl *buf;
---
> int
> gethead(struct spcl *buf)
988,989c1038,1039
< ishead(buf)
< struct spcl *buf;
---
> int
> ishead(struct spcl *buf)
996,998c1046,1047
< checktype(b, t)
< struct	spcl *b;
< int	t;
---
> int
> checktype(struct spcl *b, int t)
1004,1005c1053,1054
< checksum(b)
< int *b;
---
> int
> checksum(int *b)
1007c1056
< 	register i, j;
---
> 	register int i, j;
1021,1023c1070,1071
< checkvol(b, t)
< struct spcl *b;
< int t;
---
> int
> checkvol(struct spcl *b, int t)
1030,1031c1078,1079
< readhdr(b)
< struct	spcl *b;
---
> int
> readhdr(struct spcl *b)
1045,1047c1093,1094
< xtrfile(b, size)
< char	*b;
< long	size;
---
> int
> xtrfile(char *b, long size)
1049a1097
> 	return(0);
1052c1100
< null() {;}
---
> int null(void) {return(0);}
1054c1102,1103
< skip()
---
> int
> skip(void)
1056a1106
> 	return(0);
1061,1063c1111,1112
< rstrfile(b, s)
< char *b;
< long s;
---
> int
> rstrfile(char *b, long s)
1066a1116
> 	(void)s;
1069a1120
> 	return(0);
1072,1074c1123,1124
< rstrskip(b, s)
< char *b;
< long s;
---
> int
> rstrskip(char *b, long s)
1075a1126
> 	(void)b; (void)s;
1076a1128
> 	return(0);
1080,1081c1132,1133
< putdir(b)
< char *b;
---
> int
> putdir(char *b)
1084c1136
< 	register i;
---
> 	register int i;
1090a1143
> 	return(0);
1097,1099c1150,1151
< getdino(inum, b)
< ino_t	inum;
< struct	dinode *b;
---
> int
> getdino(ino_t inum, struct dinode *b)
1107a1160
> 	return(0);
1110,1112c1163,1164
< putdino(inum, b)
< ino_t	inum;
< struct	dinode *b;
---
> int
> putdino(ino_t inum, struct dinode *b)
1120a1173
> 	return(0);
1126,1127c1179,1180
< readbits(m)
< short	*m;
---
> int
> readbits(short *m)
1129c1182
< 	register i;
---
> 	register int i;
1138a1192
> 	return(0);
1141c1195,1196
< done()
---
> int
> done(void)
1146a1202
> 	return(0);
```

### cmd/tk.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/tk.c unix-v7-c99/cmd/tk.c || true
```

Expect:

```
37,39c37,40
< main(argc, argv)
< int argc;
< char **argv;
---
> int	init(void), sendpt(int a), kwait(void), execom(void);
> 
> int
> main(int argc, char **argv)
41,42c42,43
< 	register i, j;
< 	extern ex();
---
> 	register int i, j;
> 	extern int ex(void);
47c48
< 				if (i = atoi(&argv[0][2]))
---
> 				if ((i = atoi(&argv[0][2])))
49c50
< 					yyll = MAXY + 1 - pl;
---
> 				yyll = MAXY + 1 - pl;
52c53
< 				if (i = atoi(&argv[0][1])) {
---
> 				if ((i = atoi(&argv[0][1]))) {
67c68
< 	signal(SIGINT, ex);
---
> 	signal(SIGINT, (int)ex);
75a77
> 			/* fallthrough */
150a153
> 	return(0);
153c156,157
< init()
---
> int
> init(void)
168a173
> 	return(0);
171c176,177
< ex()
---
> int
> ex(void)
177a184
> 	return(0);
180c187,188
< kwait()
---
> int
> kwait(void)
182c190
< 	register c;
---
> 	register int c;
186c194
< 		return;
---
> 		return(0);
196a205
> 	return(0);
199c208,209
< execom()
---
> int
> execom(void)
204,205c214,215
< 		si = signal(SIGINT, SIG_IGN);
< 		sq = signal(SIGQUIT, SIG_IGN);
---
> 		si = (int (*)())signal(SIGINT, (int)SIG_IGN);
> 		sq = (int (*)())signal(SIGQUIT, (int)SIG_IGN);
207,209c217,219
< 		signal(SIGINT, si);
< 		signal(SIGQUIT, sq);
< 		return;
---
> 		signal(SIGINT, (int)si);
> 		signal(SIGQUIT, (int)sq);
> 		return(0);
215a226
> 	return(0);
218c229,230
< sendpt(a)
---
> int
> sendpt(int a)
220c232
< 	register zz;
---
> 	register int zz;
224c236
< 		return;
---
> 		return(0);
228c240
< 	xb = ((xx & 03) + ((zz<<2) & 014) & 017);
---
> 	xb = (((xx & 03) + ((zz<<2) & 014)) & 017);
247a260
> 	return(0);
```

### cmd/units.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/units.c unix-v7-c99/cmd/units.c || true
```

Expect:

```
7,9c7
< double	getflt();
< int	fperr();
< struct	table	*hash();
---
> 
21a20,27
> 
> double	getflt(void);
> int	fperr(int sig);
> struct	table	*hash(char *name);
> int	init(void), convr(struct unit *up), units(struct unit *up);
> int	pu(int u, int i, int f);
> int	lookup(char *name, struct unit *up, int den, int c);
> int	equal(char *s1, char *s2), get(void);
27c33
< } prefix[] = 
---
> } prefix[] =
29,45c35,51
< 	1e-18,	"atto",
< 	1e-15,	"femto",
< 	1e-12,	"pico",
< 	1e-9,	"nano",
< 	1e-6,	"micro",
< 	1e-3,	"milli",
< 	1e-2,	"centi",
< 	1e-1,	"deci",
< 	1e1,	"deka",
< 	1e2,	"hecta",
< 	1e2,	"hecto",
< 	1e3,	"kilo",
< 	1e6,	"mega",
< 	1e6,	"meg",
< 	1e9,	"giga",
< 	1e12,	"tera",
< 	0.0,	0
---
> 	{1e-18,	"atto"},
> 	{1e-15,	"femto"},
> 	{1e-12,	"pico"},
> 	{1e-9,	"nano"},
> 	{1e-6,	"micro"},
> 	{1e-3,	"milli"},
> 	{1e-2,	"centi"},
> 	{1e-1,	"deci"},
> 	{1e1,	"deka"},
> 	{1e2,	"hecta"},
> 	{1e2,	"hecto"},
> 	{1e3,	"kilo"},
> 	{1e6,	"mega"},
> 	{1e6,	"meg"},
> 	{1e9,	"giga"},
> 	{1e12,	"tera"},
> 	{0.0,	0}
52,53c58,59
< main(argc, argv)
< char *argv[];
---
> int
> main(int argc, char *argv[])
55c61
< 	register i;
---
> 	register int i;
72c78
< 	signal(8, fperr);
---
> 	signal(8, (int)fperr);
109,110c115,116
< units(up)
< struct unit *up;
---
> int
> units(struct unit *up)
113c119
< 	register f, i;
---
> 	register int f, i;
126a133
> 	return(0);
129c136,137
< pu(u, i, f)
---
> int
> pu(int u, int i, int f)
140c148
< 			return(2);
---
> 		return(2);
147,148c155,156
< convr(up)
< struct unit *up;
---
> int
> convr(struct unit *up)
151c159
< 	register c;
---
> 	register int c;
198,200c206,207
< lookup(name, up, den, c)
< char *name;
< struct unit *up;
---
> int
> lookup(char *name, struct unit *up, int den, int c)
204c211
< 	register i;
---
> 	register int i;
230c237
< 	for(i=0; cp1 = prefix[i].pname; i++) {
---
> 	for(i=0; (cp1 = prefix[i].pname); i++) {
252,253c259,260
< equal(s1, s2)
< char *s1, *s2;
---
> int
> equal(char *s1, char *s2)
265c272,273
< init()
---
> int
> init(void)
291c299
< 		printf("%l units; %l bytes\n\n", i, cp-names);
---
> 		printf("%d units; %d bytes\n\n", i, (int)(cp-names));
297c305
< 			units(tp);
---
> 			units((struct unit *)tp);
301c309
< 		return;
---
> 		return(0);
333c341
< 	convr(lp);
---
> 	convr((struct unit *)lp);
359c367
< getflt()
---
> getflt(void)
361c369
< 	register c, i, dp;
---
> 	register int c, i, dp;
415c423,424
< get()
---
> int
> get(void)
417c426
< 	register c;
---
> 	register int c;
419c428
< 	if(c=peekc) {
---
> 	if((c=peekc)) {
435,436c444
< hash(name)
< char *name;
---
> hash(char *name)
459c467,468
< fperr()
---
> int
> fperr(int sig)
461,462c470,471
< 
< 	signal(8, fperr);
---
> 	(void)sig;
> 	signal(8, (int)fperr);
463a473
> 	return(0);
```

### cmd/ptx.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/ptx.c unix-v7-c99/cmd/ptx.c || true
```

Expect:

```
34,35c34,36
< extern char *calloc(), *mktemp();
< extern char *getline();
---
> extern char *calloc(unsigned num, unsigned size);
> extern char *mktemp(char *as);
> extern char *getline(void);
36a38,43
> int diag(char *s, char *arg), msg(char *s, char *arg);
> int storeh(int num, char *strtp), hash(char *strtp, char *endp);
> int cmpline(char *pend), getsort(void);
> int cmpword(char *cpp, char *pend, char *hpp);
> int putline(char *strt, char *end), putout(char *strt, char *end);
> int onintr(int sig);
69,71c76,77
< main(argc,argv)
< int argc;
< char **argv;
---
> int
> main(int argc, char **argv)
77c83
< 	extern onintr();
---
> 	extern int onintr(int sig);
82,87c88,93
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
116c122
< 
---
> 			/* fallthrough */
228c234
< 	while(pend=getline())
---
> 	while((pend=getline()))
236c242
< 
---
> 		/* fallthrough */
247c253
< 	onintr();
---
> 	onintr(0);
250,252c256,257
< msg(s,arg)
< char *s;
< char *arg;
---
> int
> msg(char *s, char *arg)
255c260
< 	return;
---
> 	return(0);
257,258c262,263
< diag(s,arg)
< char *s, *arg;
---
> int
> diag(char *s, char *arg)
262a268
> 	return(0);
266c272
< char *getline()
---
> char *getline(void)
269c275
< 	register c;
---
> 	register int c;
302,303c308,309
< cmpline(pend)
< char *pend;
---
> int
> cmpline(char *pend)
316c322
< 		if(isabreak(*pchar++))
---
> 		if(isabreak((unsigned char)*pchar++))
322c328
< 			if(isabreak(*pchar)) {
---
> 			if(isabreak((unsigned char)*pchar)) {
325c331
< 				while(cp = *hp++){
---
> 				while((cp = *hp++)){
346a353
> 	return(0);
349,350c356,357
< cmpword(cpp,pend,hpp)
< char *cpp, *pend, *hpp;
---
> int
> cmpword(char *cpp, char *pend, char *hpp)
363,364c370,371
< putline(strt, end)
< char *strt, *end;
---
> int
> putline(char *strt, char *end)
376a384
> 	return(0);
379c387,388
< getsort()
---
> int
> getsort(void)
381c390
< 	register c;
---
> 	register int c;
385c394
< 	char *rtrim(), *ltrim();
---
> 	char *rtrim(char *a, char *c, int d), *ltrim(char *c, char *b, int d);
452a462
> 			/* fallthrough */
456a467
> 	return(0);
459,460c470
< char *rtrim(a,c,d)
< char *a,*c;
---
> char *rtrim(char *a, char *c, int d)
472,473c482
< char *ltrim(c,b,d)
< char *c,*b;
---
> char *ltrim(char *c, char *b, int d)
485,486c494,495
< putout(strt,end)
< char *strt, *end;
---
> int
> putout(char *strt, char *end)
494a504
> 	return(0);
497c507,508
< onintr()
---
> int
> onintr(int sig)
499c510
< 
---
> 	(void)sig;
502a514
> 	return(0);
505,506c517,518
< hash(strtp,endp)
< char *strtp, *endp;
---
> int
> hash(char *strtp, char *endp)
532,534c544,545
< storeh(num,strtp)
< int num;
< char *strtp;
---
> int
> storeh(int num, char *strtp)
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
> rhs(int i)
> {
149c150,151
< spline(){
---
> int
> spline(void){
205c207
< 		for(j=m;j>0||i==0&&j==0;j--){	/* interpolate */
---
> 		for(j=m;j>0||(i==0&&j==0);j--){	/* interpolate */
216c218,221
< readin() {
---
> int	getfloat(float *p), numb(float *np, int *argcp, char ***argvp);
> int	getlim(struct proj *p);
> int
> readin(void) {
220c225
< 		if(!getfloat(&y.val[n])) break; } }
---
> 		if(!getfloat(&y.val[n])) break; } return(0); }
222,223c227,229
< getfloat(p)
< 	float *p;{
---
> int
> getfloat(float *p)
> {
225c231
< 	register c;
---
> 	register int c;
227c233
< 	extern double atof();
---
> 	extern double atof(char *s);
261,262c267,268
< getlim(p)
< 	struct proj *p; {
---
> int
> getlim(struct proj *p) {
267c273
< 	}
---
> 	return(0); }
270,272c276,279
< main(argc,argv)
< 	char *argv[];{
< 	extern char *malloc();
---
> int
> main(int argc, char *argv[])
> {
> 	extern char *malloc(unsigned n);
320,324c327,330
< numb(np,argcp,argvp)
< 	int *argcp;
< 	float *np;
< 	char ***argvp;{
< 	double atof();
---
> int
> numb(float *np, int *argcp, char ***argvp)
> {
> 	double atof(char *s);
328c334
< 	if(!('0'<=c&&c<='9' || c=='-' || c== '.' )) return(0);
---
> 	if(!(('0'<=c&&c<='9') || c=='-' || c== '.' )) return(0);
```

### cmd/vpr.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/vpr.c unix-v7-c99/cmd/vpr.c || true
```

Expect:

```
26c26,27
< char	*ctime();
---
> char	*ctime(long *t);
> int	send(void), getline(void), putline(int ff), banner(char *s);
28,29c29,30
< main(argc, argv)
< char **argv;
---
> int
> main(int argc, char **argv)
72c73,74
< send()
---
> int
> send(void)
74c76
< 	register nskipped;
---
> 	register int nskipped;
97c99,100
< getline()
---
> int
> getline(void)
99c102
< 	register col, maxcol, c;
---
> 	register int col, maxcol, c;
175c178,179
< putline(ff)
---
> int
> putline(int ff)
178,179c182,183
< 	register c;
< 	extern errno;
---
> 	register int c;
> 	extern int errno;
183c187
< 	while (c = *lp++)
---
> 	while ((c = *lp++))
188c192
< 		ioctl(fileno(out), SETSTATE, pltmode);
---
> 		ioctl(fileno(out), SETSTATE, (char *)pltmode);
192c196
< 		ioctl(fileno(out), SETSTATE, prtmode);
---
> 		ioctl(fileno(out), SETSTATE, (char *)prtmode);
202a207
> 	return(0);
205,206c210,211
< banner(s)
< char *s;
---
> int
> banner(char *s)
232a238
> 	return(0);
236,331c242,337
< 0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000, /*, sp, */
< 0010,0010,0010,0010,0010,0010,0010,0010,0000,0000,0010,0000,0000,0000,0000,0000, /*, !, */
< 0024,0024,0024,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000, /*, ", */
< 0000,0000,0000,0044,0044,0176,0044,0044,0176,0044,0044,0000,0000,0000,0000,0000, /*, #, */
< 0000,0010,0010,0010,0076,0101,0100,0076,0001,0101,0076,0010,0010,0000,0000,0000, /*, $, */
< 0000,0000,0000,0141,0142,0004,0010,0010,0020,0043,0103,0000,0000,0000,0000,0000, /*, %, */
< 0000,0000,0070,0104,0110,0060,0060,0111,0106,0106,0071,0000,0000,0000,0000,0000, /*, &, */
< 0004,0010,0020,0040,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000, /*, ', */
< 0000,0004,0010,0020,0040,0040,0040,0040,0040,0040,0020,0010,0004,0000,0000,0000, /*, (, */
< 0000,0040,0020,0010,0004,0004,0004,0004,0004,0004,0010,0020,0040,0000,0000,0000, /*, ), */
< 0000,0000,0000,0010,0111,0052,0034,0177,0034,0052,0111,0010,0000,0000,0000,0000, /*, *, */
< 0000,0000,0000,0000,0010,0010,0010,0177,0010,0010,0010,0000,0000,0000,0000,0000, /*, +, */
< 0000,0000,0000,0000,0000,0000,0000,0000,0000,0030,0030,0010,0020,0000,0000,0000, /*, ,, */
< 0000,0000,0000,0000,0000,0000,0000,0176,0000,0000,0000,0000,0000,0000,0000,0000, /*, -, */
< 0000,0000,0000,0000,0000,0000,0000,0000,0000,0030,0030,0000,0000,0000,0000,0000, /*, ., */
< 0000,0000,0001,0002,0004,0010,0010,0010,0020,0040,0100,0000,0000,0000,0000,0000, /*, /, */
< 0000,0030,0044,0102,0102,0102,0102,0102,0102,0044,0030,0000,0000,0000,0000,0000, /*, 0, */
< 0000,0010,0030,0010,0010,0010,0010,0010,0010,0010,0034,0000,0000,0000,0000,0000, /*, 1, */
< 0000,0070,0104,0004,0004,0010,0020,0040,0100,0100,0174,0000,0000,0000,0000,0000, /*, 2, */
< 0000,0176,0004,0004,0010,0014,0002,0002,0002,0104,0070,0000,0000,0000,0000,0000, /*, 3, */
< 0000,0004,0014,0024,0044,0104,0176,0004,0004,0004,0004,0000,0000,0000,0000,0000, /*, 4, */
< 0000,0174,0100,0100,0130,0144,0002,0002,0102,0044,0030,0000,0000,0000,0000,0000, /*, 5, */
< 0000,0074,0102,0100,0130,0144,0102,0102,0102,0044,0030,0000,0000,0000,0000,0000, /*, 6, */
< 0000,0176,0004,0004,0010,0010,0020,0020,0040,0040,0040,0000,0000,0000,0000,0000, /*, 7, */
< 0000,0034,0042,0101,0042,0076,0101,0101,0101,0101,0076,0000,0000,0000,0000,0000, /*, 8, */
< 0000,0034,0042,0101,0101,0101,0043,0036,0004,0010,0020,0040,0000,0000,0000,0000, /*, 9, */
< 0000,0000,0000,0000,0000,0000,0030,0030,0000,0030,0030,0000,0000,0000,0000,0000, /*, :, */
< 0000,0000,0000,0000,0000,0000,0030,0030,0000,0030,0030,0020,0040,0000,0000,0000, /*, ;, */
< 0002,0004,0010,0020,0040,0100,0040,0020,0010,0004,0002,0000,0000,0000,0000,0000, /*, <, */
< 0000,0000,0000,0000,0177,0000,0177,0000,0000,0000,0000,0000,0000,0000,0000,0000, /*, =, */
< 0100,0040,0020,0010,0004,0002,0004,0010,0020,0040,0100,0000,0000,0000,0000,0000, /*, >, */
< 0000,0030,0044,0102,0001,0002,0004,0010,0010,0000,0010,0000,0000,0000,0000,0000, /*, ?, */
< 0000,0074,0102,0101,0115,0123,0121,0121,0121,0111,0046,0000,0000,0000,0000,0000, /*, @, */
< 0000,0010,0024,0042,0101,0101,0177,0101,0101,0101,0101,0000,0000,0000,0000,0000, /*, A, */
< 0000,0176,0101,0101,0101,0176,0101,0101,0101,0101,0176,0000,0000,0000,0000,0000, /*, B, */
< 0000,0076,0101,0100,0100,0100,0100,0100,0100,0101,0076,0000,0000,0000,0000,0000, /*, C, */
< 0000,0176,0101,0101,0101,0101,0101,0101,0101,0101,0176,0000,0000,0000,0000,0000, /*, D, */
< 0000,0176,0100,0100,0100,0170,0100,0100,0100,0100,0177,0000,0000,0000,0000,0000, /*, E, */
< 0000,0177,0100,0100,0100,0174,0100,0100,0100,0100,0100,0000,0000,0000,0000,0000, /*, F, */
< 0000,0076,0101,0100,0100,0117,0101,0101,0101,0101,0076,0000,0000,0000,0000,0000, /*, G, */
< 0000,0101,0101,0101,0101,0176,0101,0101,0101,0101,0101,0000,0000,0000,0000,0000, /*, H, */
< 0000,0034,0010,0010,0010,0010,0010,0010,0010,0010,0034,0000,0000,0000,0000,0000, /*, I, */
< 0000,0016,0004,0004,0004,0004,0004,0004,0104,0104,0070,0000,0000,0000,0000,0000, /*, J, */
< 0000,0101,0102,0104,0110,0120,0160,0110,0104,0102,0101,0000,0000,0000,0000,0000, /*, K, */
< 0000,0100,0100,0100,0100,0100,0100,0100,0100,0100,0177,0000,0000,0000,0000,0000, /*, L, */
< 0000,0101,0143,0125,0111,0101,0101,0101,0101,0101,0101,0000,0000,0000,0000,0000, /*, M, */
< 0000,0101,0141,0121,0111,0105,0103,0101,0101,0101,0101,0000,0000,0000,0000,0000, /*, N, */
< 0000,0076,0101,0101,0101,0101,0101,0101,0101,0101,0076,0000,0000,0000,0000,0000, /*, O, */
< 0000,0176,0101,0101,0101,0176,0100,0100,0100,0100,0100,0000,0000,0000,0000,0000, /*, P, */
< 0000,0076,0101,0101,0101,0101,0101,0101,0131,0105,0076,0002,0001,0000,0000,0000, /*, Q, */
< 0000,0176,0101,0101,0101,0176,0104,0102,0101,0101,0101,0000,0000,0000,0000,0000, /*, R, */
< 0000,0076,0101,0100,0100,0076,0001,0001,0001,0101,0076,0000,0000,0000,0000,0000, /*, S, */
< 0000,0177,0010,0010,0010,0010,0010,0010,0010,0010,0010,0000,0000,0000,0000,0000, /*, T, */
< 0000,0101,0101,0101,0101,0101,0101,0101,0101,0101,0076,0000,0000,0000,0000,0000, /*, U, */
< 0000,0101,0101,0101,0101,0101,0101,0101,0042,0024,0010,0000,0000,0000,0000,0000, /*, V, */
< 0000,0101,0101,0101,0101,0111,0111,0125,0143,0101,0101,0000,0000,0000,0000,0000, /*, W, */
< 0000,0101,0101,0042,0024,0010,0024,0042,0101,0101,0101,0000,0000,0000,0000,0000, /*, X, */
< 0000,0101,0042,0024,0010,0010,0010,0010,0010,0010,0010,0000,0000,0000,0000,0000, /*, Y, */
< 0000,0177,0001,0002,0004,0010,0020,0040,0100,0100,0177,0000,0000,0000,0000,0000, /*, Z, */
< 0000,0034,0020,0020,0020,0020,0020,0020,0020,0020,0020,0034,0000,0000,0000,0000, /*, [, */
< 0000,0000,0100,0040,0020,0010,0010,0010,0004,0002,0001,0000,0000,0000,0000,0000, /*, , \, */
< 0000,0070,0010,0010,0010,0010,0010,0010,0010,0010,0010,0070,0000,0000,0000,0000, /*, ], */
< 0010,0024,0042,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000, /*, ^, */
< 0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0377,0000,0000, /*, _, */
< 0040,0020,0010,0004,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000, /*, `, */
< 0000,0000,0000,0000,0000,0074,0002,0076,0102,0102,0076,0000,0000,0000,0000,0000, /*, a, */
< 0000,0100,0100,0100,0100,0174,0102,0102,0102,0102,0174,0000,0000,0000,0000,0000, /*, b, */
< 0000,0000,0000,0000,0000,0074,0102,0100,0100,0102,0074,0000,0000,0000,0000,0000, /*, c, */
< 0002,0002,0002,0002,0002,0076,0102,0102,0102,0102,0076,0000,0000,0000,0000,0000, /*, d, */
< 0000,0000,0000,0000,0000,0074,0102,0174,0100,0102,0074,0000,0000,0000,0000,0000, /*, e, */
< 0000,0016,0020,0020,0020,0176,0020,0020,0020,0020,0020,0000,0000,0000,0000,0000, /*, f, */
< 0000,0000,0000,0000,0000,0076,0102,0102,0102,0102,0076,0002,0002,0102,0076,0000, /*, g, */
< 0000,0100,0100,0100,0100,0174,0102,0102,0102,0102,0102,0000,0000,0000,0000,0000, /*, h, */
< 0000,0000,0000,0010,0000,0030,0010,0010,0010,0010,0034,0000,0000,0000,0000,0000, /*, i, */
< 0000,0000,0000,0010,0000,0030,0010,0010,0010,0010,0010,0010,0010,0050,0020,0000, /*, j, */
< 0000,0100,0100,0100,0100,0106,0110,0120,0160,0110,0106,0000,0000,0000,0000,0000, /*, k, */
< 0000,0030,0010,0010,0010,0010,0010,0010,0010,0010,0034,0000,0000,0000,0000,0000, /*, l, */
< 0000,0000,0000,0000,0000,0166,0111,0111,0111,0111,0111,0000,0000,0000,0000,0000, /*, m, */
< 0000,0000,0000,0000,0100,0174,0102,0102,0102,0102,0102,0000,0000,0000,0000,0000, /*, n, */
< 0000,0000,0000,0000,0000,0074,0102,0102,0102,0102,0074,0000,0000,0000,0000,0000, /*, o, */
< 0000,0000,0000,0000,0000,0174,0102,0102,0102,0102,0174,0100,0100,0100,0100,0000, /*, p, */
< 0000,0000,0000,0000,0000,0076,0102,0102,0102,0102,0076,0002,0002,0002,0002,0000, /*, q, */
< 0000,0000,0000,0000,0000,0134,0142,0100,0100,0100,0100,0000,0000,0000,0000,0000, /*, r, */
< 0000,0000,0000,0000,0000,0076,0100,0074,0002,0102,0074,0000,0000,0000,0000,0000, /*, s, */
< 0000,0020,0020,0020,0020,0176,0020,0020,0020,0020,0014,0000,0000,0000,0000,0000, /*, t, */
< 0000,0000,0000,0000,0000,0102,0102,0102,0102,0102,0075,0000,0000,0000,0000,0000, /*, u, */
< 0000,0000,0000,0000,0000,0101,0101,0101,0042,0024,0010,0000,0000,0000,0000,0000, /*, v, */
< 0000,0000,0000,0000,0000,0111,0111,0111,0111,0111,0066,0000,0000,0000,0000,0000, /*, w, */
< 0000,0000,0000,0000,0000,0102,0044,0030,0030,0044,0102,0000,0000,0000,0000,0000, /*, x, */
< 0000,0000,0000,0000,0000,0102,0102,0102,0042,0024,0010,0020,0040,0100,0000,0000, /*, y, */
< 0000,0000,0000,0000,0000,0176,0004,0010,0020,0040,0176,0000,0000,0000,0000,0000, /*, z, */
< 0000,0014,0020,0020,0020,0020,0040,0020,0020,0020,0020,0014,0000,0000,0000,0000, /*, {, */
< 0000,0010,0010,0010,0010,0000,0000,0010,0010,0010,0010,0000,0000,0000,0000,0000, /*, |, */
< 0000,0030,0010,0010,0010,0010,0004,0010,0010,0010,0010,0030,0000,0000,0000,0000, /*, }, */
< 0020,0052,0004,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000, /*, ~, */
< 0000,0176,0176,0176,0176,0176,0176,0176,0176,0176,0176,0000,0000,0000,0000,0000, /*, del, */
---
> 	{0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000}, /*, sp, */
> 	{0010,0010,0010,0010,0010,0010,0010,0010,0000,0000,0010,0000,0000,0000,0000,0000}, /*, !, */
> 	{0024,0024,0024,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000}, /*, ", */
> 	{0000,0000,0000,0044,0044,0176,0044,0044,0176,0044,0044,0000,0000,0000,0000,0000}, /*, #, */
> 	{0000,0010,0010,0010,0076,0101,0100,0076,0001,0101,0076,0010,0010,0000,0000,0000}, /*, $, */
> 	{0000,0000,0000,0141,0142,0004,0010,0010,0020,0043,0103,0000,0000,0000,0000,0000}, /*, %, */
> 	{0000,0000,0070,0104,0110,0060,0060,0111,0106,0106,0071,0000,0000,0000,0000,0000}, /*, &, */
> 	{0004,0010,0020,0040,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000}, /*, ', */
> 	{0000,0004,0010,0020,0040,0040,0040,0040,0040,0040,0020,0010,0004,0000,0000,0000}, /*, (, */
> 	{0000,0040,0020,0010,0004,0004,0004,0004,0004,0004,0010,0020,0040,0000,0000,0000}, /*, ), */
> 	{0000,0000,0000,0010,0111,0052,0034,0177,0034,0052,0111,0010,0000,0000,0000,0000}, /*, *, */
> 	{0000,0000,0000,0000,0010,0010,0010,0177,0010,0010,0010,0000,0000,0000,0000,0000}, /*, +, */
> 	{0000,0000,0000,0000,0000,0000,0000,0000,0000,0030,0030,0010,0020,0000,0000,0000}, /*, ,, */
> 	{0000,0000,0000,0000,0000,0000,0000,0176,0000,0000,0000,0000,0000,0000,0000,0000}, /*, -, */
> 	{0000,0000,0000,0000,0000,0000,0000,0000,0000,0030,0030,0000,0000,0000,0000,0000}, /*, ., */
> 	{0000,0000,0001,0002,0004,0010,0010,0010,0020,0040,0100,0000,0000,0000,0000,0000}, /*, /, */
> 	{0000,0030,0044,0102,0102,0102,0102,0102,0102,0044,0030,0000,0000,0000,0000,0000}, /*, 0, */
> 	{0000,0010,0030,0010,0010,0010,0010,0010,0010,0010,0034,0000,0000,0000,0000,0000}, /*, 1, */
> 	{0000,0070,0104,0004,0004,0010,0020,0040,0100,0100,0174,0000,0000,0000,0000,0000}, /*, 2, */
> 	{0000,0176,0004,0004,0010,0014,0002,0002,0002,0104,0070,0000,0000,0000,0000,0000}, /*, 3, */
> 	{0000,0004,0014,0024,0044,0104,0176,0004,0004,0004,0004,0000,0000,0000,0000,0000}, /*, 4, */
> 	{0000,0174,0100,0100,0130,0144,0002,0002,0102,0044,0030,0000,0000,0000,0000,0000}, /*, 5, */
> 	{0000,0074,0102,0100,0130,0144,0102,0102,0102,0044,0030,0000,0000,0000,0000,0000}, /*, 6, */
> 	{0000,0176,0004,0004,0010,0010,0020,0020,0040,0040,0040,0000,0000,0000,0000,0000}, /*, 7, */
> 	{0000,0034,0042,0101,0042,0076,0101,0101,0101,0101,0076,0000,0000,0000,0000,0000}, /*, 8, */
> 	{0000,0034,0042,0101,0101,0101,0043,0036,0004,0010,0020,0040,0000,0000,0000,0000}, /*, 9, */
> 	{0000,0000,0000,0000,0000,0000,0030,0030,0000,0030,0030,0000,0000,0000,0000,0000}, /*, :, */
> 	{0000,0000,0000,0000,0000,0000,0030,0030,0000,0030,0030,0020,0040,0000,0000,0000}, /*, ;, */
> 	{0002,0004,0010,0020,0040,0100,0040,0020,0010,0004,0002,0000,0000,0000,0000,0000}, /*, <, */
> 	{0000,0000,0000,0000,0177,0000,0177,0000,0000,0000,0000,0000,0000,0000,0000,0000}, /*, =, */
> 	{0100,0040,0020,0010,0004,0002,0004,0010,0020,0040,0100,0000,0000,0000,0000,0000}, /*, >, */
> 	{0000,0030,0044,0102,0001,0002,0004,0010,0010,0000,0010,0000,0000,0000,0000,0000}, /*, ?, */
> 	{0000,0074,0102,0101,0115,0123,0121,0121,0121,0111,0046,0000,0000,0000,0000,0000}, /*, @, */
> 	{0000,0010,0024,0042,0101,0101,0177,0101,0101,0101,0101,0000,0000,0000,0000,0000}, /*, A, */
> 	{0000,0176,0101,0101,0101,0176,0101,0101,0101,0101,0176,0000,0000,0000,0000,0000}, /*, B, */
> 	{0000,0076,0101,0100,0100,0100,0100,0100,0100,0101,0076,0000,0000,0000,0000,0000}, /*, C, */
> 	{0000,0176,0101,0101,0101,0101,0101,0101,0101,0101,0176,0000,0000,0000,0000,0000}, /*, D, */
> 	{0000,0176,0100,0100,0100,0170,0100,0100,0100,0100,0177,0000,0000,0000,0000,0000}, /*, E, */
> 	{0000,0177,0100,0100,0100,0174,0100,0100,0100,0100,0100,0000,0000,0000,0000,0000}, /*, F, */
> 	{0000,0076,0101,0100,0100,0117,0101,0101,0101,0101,0076,0000,0000,0000,0000,0000}, /*, G, */
> 	{0000,0101,0101,0101,0101,0176,0101,0101,0101,0101,0101,0000,0000,0000,0000,0000}, /*, H, */
> 	{0000,0034,0010,0010,0010,0010,0010,0010,0010,0010,0034,0000,0000,0000,0000,0000}, /*, I, */
> 	{0000,0016,0004,0004,0004,0004,0004,0004,0104,0104,0070,0000,0000,0000,0000,0000}, /*, J, */
> 	{0000,0101,0102,0104,0110,0120,0160,0110,0104,0102,0101,0000,0000,0000,0000,0000}, /*, K, */
> 	{0000,0100,0100,0100,0100,0100,0100,0100,0100,0100,0177,0000,0000,0000,0000,0000}, /*, L, */
> 	{0000,0101,0143,0125,0111,0101,0101,0101,0101,0101,0101,0000,0000,0000,0000,0000}, /*, M, */
> 	{0000,0101,0141,0121,0111,0105,0103,0101,0101,0101,0101,0000,0000,0000,0000,0000}, /*, N, */
> 	{0000,0076,0101,0101,0101,0101,0101,0101,0101,0101,0076,0000,0000,0000,0000,0000}, /*, O, */
> 	{0000,0176,0101,0101,0101,0176,0100,0100,0100,0100,0100,0000,0000,0000,0000,0000}, /*, P, */
> 	{0000,0076,0101,0101,0101,0101,0101,0101,0131,0105,0076,0002,0001,0000,0000,0000}, /*, Q, */
> 	{0000,0176,0101,0101,0101,0176,0104,0102,0101,0101,0101,0000,0000,0000,0000,0000}, /*, R, */
> 	{0000,0076,0101,0100,0100,0076,0001,0001,0001,0101,0076,0000,0000,0000,0000,0000}, /*, S, */
> 	{0000,0177,0010,0010,0010,0010,0010,0010,0010,0010,0010,0000,0000,0000,0000,0000}, /*, T, */
> 	{0000,0101,0101,0101,0101,0101,0101,0101,0101,0101,0076,0000,0000,0000,0000,0000}, /*, U, */
> 	{0000,0101,0101,0101,0101,0101,0101,0101,0042,0024,0010,0000,0000,0000,0000,0000}, /*, V, */
> 	{0000,0101,0101,0101,0101,0111,0111,0125,0143,0101,0101,0000,0000,0000,0000,0000}, /*, W, */
> 	{0000,0101,0101,0042,0024,0010,0024,0042,0101,0101,0101,0000,0000,0000,0000,0000}, /*, X, */
> 	{0000,0101,0042,0024,0010,0010,0010,0010,0010,0010,0010,0000,0000,0000,0000,0000}, /*, Y, */
> 	{0000,0177,0001,0002,0004,0010,0020,0040,0100,0100,0177,0000,0000,0000,0000,0000}, /*, Z, */
> 	{0000,0034,0020,0020,0020,0020,0020,0020,0020,0020,0020,0034,0000,0000,0000,0000}, /*, [, */
> 	{0000,0000,0100,0040,0020,0010,0010,0010,0004,0002,0001,0000,0000,0000,0000,0000}, /*, , \, */
> 	{0000,0070,0010,0010,0010,0010,0010,0010,0010,0010,0010,0070,0000,0000,0000,0000}, /*, ], */
> 	{0010,0024,0042,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000}, /*, ^, */
> 	{0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0377,0000,0000}, /*, _, */
> 	{0040,0020,0010,0004,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000}, /*, `, */
> 	{0000,0000,0000,0000,0000,0074,0002,0076,0102,0102,0076,0000,0000,0000,0000,0000}, /*, a, */
> 	{0000,0100,0100,0100,0100,0174,0102,0102,0102,0102,0174,0000,0000,0000,0000,0000}, /*, b, */
> 	{0000,0000,0000,0000,0000,0074,0102,0100,0100,0102,0074,0000,0000,0000,0000,0000}, /*, c, */
> 	{0002,0002,0002,0002,0002,0076,0102,0102,0102,0102,0076,0000,0000,0000,0000,0000}, /*, d, */
> 	{0000,0000,0000,0000,0000,0074,0102,0174,0100,0102,0074,0000,0000,0000,0000,0000}, /*, e, */
> 	{0000,0016,0020,0020,0020,0176,0020,0020,0020,0020,0020,0000,0000,0000,0000,0000}, /*, f, */
> 	{0000,0000,0000,0000,0000,0076,0102,0102,0102,0102,0076,0002,0002,0102,0076,0000}, /*, g, */
> 	{0000,0100,0100,0100,0100,0174,0102,0102,0102,0102,0102,0000,0000,0000,0000,0000}, /*, h, */
> 	{0000,0000,0000,0010,0000,0030,0010,0010,0010,0010,0034,0000,0000,0000,0000,0000}, /*, i, */
> 	{0000,0000,0000,0010,0000,0030,0010,0010,0010,0010,0010,0010,0010,0050,0020,0000}, /*, j, */
> 	{0000,0100,0100,0100,0100,0106,0110,0120,0160,0110,0106,0000,0000,0000,0000,0000}, /*, k, */
> 	{0000,0030,0010,0010,0010,0010,0010,0010,0010,0010,0034,0000,0000,0000,0000,0000}, /*, l, */
> 	{0000,0000,0000,0000,0000,0166,0111,0111,0111,0111,0111,0000,0000,0000,0000,0000}, /*, m, */
> 	{0000,0000,0000,0000,0100,0174,0102,0102,0102,0102,0102,0000,0000,0000,0000,0000}, /*, n, */
> 	{0000,0000,0000,0000,0000,0074,0102,0102,0102,0102,0074,0000,0000,0000,0000,0000}, /*, o, */
> 	{0000,0000,0000,0000,0000,0174,0102,0102,0102,0102,0174,0100,0100,0100,0100,0000}, /*, p, */
> 	{0000,0000,0000,0000,0000,0076,0102,0102,0102,0102,0076,0002,0002,0002,0002,0000}, /*, q, */
> 	{0000,0000,0000,0000,0000,0134,0142,0100,0100,0100,0100,0000,0000,0000,0000,0000}, /*, r, */
> 	{0000,0000,0000,0000,0000,0076,0100,0074,0002,0102,0074,0000,0000,0000,0000,0000}, /*, s, */
> 	{0000,0020,0020,0020,0020,0176,0020,0020,0020,0020,0014,0000,0000,0000,0000,0000}, /*, t, */
> 	{0000,0000,0000,0000,0000,0102,0102,0102,0102,0102,0075,0000,0000,0000,0000,0000}, /*, u, */
> 	{0000,0000,0000,0000,0000,0101,0101,0101,0042,0024,0010,0000,0000,0000,0000,0000}, /*, v, */
> 	{0000,0000,0000,0000,0000,0111,0111,0111,0111,0111,0066,0000,0000,0000,0000,0000}, /*, w, */
> 	{0000,0000,0000,0000,0000,0102,0044,0030,0030,0044,0102,0000,0000,0000,0000,0000}, /*, x, */
> 	{0000,0000,0000,0000,0000,0102,0102,0102,0042,0024,0010,0020,0040,0100,0000,0000}, /*, y, */
> 	{0000,0000,0000,0000,0000,0176,0004,0010,0020,0040,0176,0000,0000,0000,0000,0000}, /*, z, */
> 	{0000,0014,0020,0020,0020,0020,0040,0020,0020,0020,0020,0014,0000,0000,0000,0000}, /*, {, */
> 	{0000,0010,0010,0010,0010,0000,0000,0010,0010,0010,0010,0000,0000,0000,0000,0000}, /*, |, */
> 	{0000,0030,0010,0010,0010,0010,0004,0010,0010,0010,0010,0030,0000,0000,0000,0000}, /*, }, */
> 	{0020,0052,0004,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000}, /*, ~, */
> 	{0000,0176,0176,0176,0176,0176,0176,0176,0176,0176,0176,0000,0000,0000,0000,0000}, /*, del, */
```

### cmd/graph.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/graph.c unix-v7-c99/cmd/graph.c || true
```

Expect:

```
43c43,77
< double	atof();
---
> double	atof(char *s);
> struct xy;
> struct val;
> int	init(struct xy *p);
> int	setopt(int argc, char *argv[]);
> int	readin(void);
> int	transpose(void);
> int	scale(struct xy *p, struct val *v);
> int	axes(void);
> int	title(void);
> int	plot(void);
> int	erase(void);
> int	space(int x0, int y0, int x1, int y1);
> int	move(int xi, int yi);
> int	closevt(void);
> int	numb(float *np, int *argcp, char ***argvp);
> int	limread(struct xy *p, int *argcp, char ***argvp);
> int	badarg(void);
> int	getfloat(float *p);
> int	getstring(void);
> int	copystring(int k);
> int	getlim(struct xy *p, struct val *v);
> int	setlim(struct xy *p);
> int	setmark(int *xmark, struct xy *p);
> int	submark(int *xmark, int *pxn, float x, struct xy *p);
> int	conv(float xv, struct xy *p, int *ip);
> int	symbol(int ix, int iy, int k);
> int	point(int xi, int yi);
> int	label(char *s);
> int	cont(int xi, int yi);
> int	line(int x0, int y0, int x1, int y1);
> int	linemod(char *s);
> int	axlab(int c, struct xy *p);
> int	putsi(int a);
> int	scanf(char *fmt, ...);
57,58c91,92
< char *realloc();
< char *malloc();
---
> char *realloc(char *p, unsigned n);
> char *malloc(unsigned n);
60,61c94
< double ident(x)
< double x;
---
> double ident(double x)
66,67c99,156
< main(argc,argv)
< char *argv[];
---
> double
> fabs(double x)
> {
> 	return(x < 0 ? -x : x);
> }
> 
> double
> floor(double x)
> {
> 	long n;
> 
> 	n = x;
> 	if((double)n > x)
> 		n--;
> 	return(n);
> }
> 
> double
> ceil(double x)
> {
> 	long n;
> 
> 	n = x;
> 	if((double)n < x)
> 		n++;
> 	return(n);
> }
> 
> double
> log10(double x)
> {
> 	double y, y2, term, sum;
> 	int k, i;
> 
> 	if(x <= 0)
> 		return(-INF);
> 	k = 0;
> 	while(x >= 10) {
> 		x /= 10;
> 		k++;
> 	}
> 	while(x < 1) {
> 		x *= 10;
> 		k--;
> 	}
> 	y = (x - 1)/(x + 1);
> 	y2 = y*y;
> 	term = y;
> 	sum = 0;
> 	for(i=1; i<30; i += 2) {
> 		sum += term/i;
> 		term *= y2;
> 	}
> 	return(k + (2*sum)/2.302585092994046);
> }
> 
> int
> main(int argc, char *argv[])
92,93c181,182
< init(p)
< struct xy *p;
---
> int
> init(struct xy *p)
96a186
> 	return(0);
99,100c189,190
< setopt(argc,argv)
< char *argv[];
---
> int
> setopt(int argc, char *argv[])
102c192
< 	char *p1, *p2;
---
> 	char *p0, *p1, *p2;
108a199
> 		p0 = argv[0];
119c210,211
< 				while (*p1++ = *p2++);
---
> 				while ((*p1++ = *p2++))
> 					;
193c285,291
< 			badarg();
---
> 			if(p0[0] == '-')
> 				badarg();
> 			if(freopen(argv[0],"r",stdin)==NULL) {
> 				perror(argv[0]);
> 				exit(1);
> 			}
> 			break;
195a294
> 	return(0);
198,201c297,298
< limread(p, argcp, argvp)
< register struct xy *p;
< int *argcp;
< char ***argvp;
---
> int
> limread(register struct xy *p, int *argcp, char ***argvp)
209c306
< 		return;
---
> 		return(0);
212c309
< 		return;
---
> 		return(0);
215c312
< 		return;
---
> 		return(0);
216a314
> 	return(0);
219,222c317,318
< numb(np, argcp, argvp)
< int *argcp;
< float *np;
< register char ***argvp;
---
> int
> numb(float *np, int *argcp, register char ***argvp)
230c326
< 	if(!(isdigit(c) || c=='-'&&(*argvp)[1][1]<'A' || c=='.'))
---
> 	if(!(isdigit(c) || (c=='-' && (*argvp)[1][1]<'A') || c=='.'))
238c334,335
< readin()
---
> int
> readin(void)
240c337
< 	register t;
---
> 	register int t;
253c350
< 			return;
---
> 			return(0);
259c356
< 				return;
---
> 				return(0);
261c358
< 			return;
---
> 			return(0);
268c365
< 			return;
---
> 			return(0);
272c369,370
< transpose()
---
> int
> transpose(void)
274c372
< 	register i;
---
> 	register int i;
278c376
< 		return;
---
> 		return(0);
282a381
> 	return(0);
285c384,385
< copystring(k)
---
> int
> copystring(int k)
288c388
< 	register i;
---
> 	register int i;
302,303c402
< modceil(f,t)
< float f,t;
---
> modceil(float f, float t)
311,312c410
< modfloor(f,t)
< float f,t;
---
> modfloor(float f, float t)
318,320c416,417
< getlim(p,v)
< register struct xy *p;
< struct val *v;
---
> int
> getlim(register struct xy *p, struct val *v)
322c419
< 	register i;
---
> 	register int i;
331a429
> 	return(0);
336c434,436
< } setloglim(), setlinlim();
---
> };
> struct z setloglim(int lbf, int ubf, float lb, float ub);
> struct z setlinlim(int lbf, int ubf, float xlb, float xub);
338,339c438,439
< setlim(p)
< register struct xy *p;
---
> int
> setlim(register struct xy *p)
353c453
< 		return;
---
> 		return(0);
392c492
< 			return;
---
> 			return(0);
403a504
> 	return(0);
407,408c508
< setloglim(lbf,ubf,lb,ub)
< float lb,ub;
---
> setloglim(int lbf, int ubf, float lb, float ub)
440,442c540
< setlinlim(lbf,ubf,xlb,xub)
< int lbf,ubf;
< float xlb,xub;
---
> setlinlim(int lbf, int ubf, float xlb, float xub)
482,484c580,581
< scale(p,v)
< register struct xy *p;
< struct val *v;
---
> int
> scale(register struct xy *p, struct val *v)
494a592
> 	return(0);
497c595,596
< axes()
---
> int
> axes(void)
499c598
< 	register i;
---
> 	register int i;
503c602
< 		return;
---
> 		return(0);
527a627
> 	return(0);
530,532c630,631
< setmark(xmark,p)
< int *xmark;
< register struct xy *p;
---
> int
> setmark(int *xmark, register struct xy *p)
560,564c659,660
< submark(xmark,pxn,x,p)
< int *xmark;
< int *pxn;
< float x;
< struct xy *p;
---
> int
> submark(int *xmark, int *pxn, float x, struct xy *p)
567a664
> 	return(0);
570c667,668
< plot()
---
> int
> plot(void)
594a693
> 	return(0);
597,600c696,697
< conv(xv,p,ip)
< float xv;
< register struct xy *p;
< int *ip;
---
> int
> conv(float xv, register struct xy *p, int *ip)
610,611c707,708
< getfloat(p)
< float *p;
---
> int
> getfloat(float *p)
613c710
< 	register i;
---
> 	register int i;
619c716,717
< getstring()
---
> int
> getstring(void)
621c719
< 	register i;
---
> 	register int i;
632a731
> 		/* fallthrough */
649c748,749
< symbol(ix,iy,k)
---
> int
> symbol(int ix, int iy, int k)
661c761
< 		return(!brkf|k<0);
---
> 		return((!brkf)|(k<0));
665c765,766
< title()
---
> int
> title(void)
676a778
> 	return(0);
679,681c781,782
< axlab(c,p)
< char c;
< struct xy *p;
---
> int
> axlab(int c, struct xy *p)
686a788
> 	return(0);
689c791,792
< badarg()
---
> int
> badarg(void)
692a796,891
> 	return(0);
> }
> 
> int
> putsi(int a)
> {
> 	putc(a, stdout);
> 	putc(a >> 8, stdout);
> 	return(0);
> }
> 
> int
> space(int x0, int y0, int x1, int y1)
> {
> 	putc('s', stdout);
> 	putsi(x0);
> 	putsi(y0);
> 	putsi(x1);
> 	putsi(y1);
> 	return(0);
> }
> 
> int
> erase(void)
> {
> 	putc('e', stdout);
> 	return(0);
> }
> 
> int
> move(int xi, int yi)
> {
> 	putc('m', stdout);
> 	putsi(xi);
> 	putsi(yi);
> 	return(0);
> }
> 
> int
> cont(int xi, int yi)
> {
> 	putc('n', stdout);
> 	putsi(xi);
> 	putsi(yi);
> 	return(0);
> }
> 
> int
> line(int x0, int y0, int x1, int y1)
> {
> 	putc('l', stdout);
> 	putsi(x0);
> 	putsi(y0);
> 	putsi(x1);
> 	putsi(y1);
> 	return(0);
> }
> 
> int
> point(int xi, int yi)
> {
> 	putc('p', stdout);
> 	putsi(xi);
> 	putsi(yi);
> 	return(0);
> }
> 
> int
> label(char *s)
> {
> 	int i;
> 
> 	putc('t', stdout);
> 	for(i=0; s[i]; i++)
> 		putc(s[i], stdout);
> 	putc('\n', stdout);
> 	return(0);
> }
> 
> int
> linemod(char *s)
> {
> 	int i;
> 
> 	putc('f', stdout);
> 	for(i=0; s[i]; i++)
> 		putc(s[i], stdout);
> 	putc('\n', stdout);
> 	return(0);
> }
> 
> int
> closevt(void)
> {
> 	fflush(stdout);
> 	return(0);
```

### cmd/backgammon.c

Local test:

```
diff unix-v7-c99/v7/usr/src/games/backgammon.c unix-v7-c99/cmd/backgammon.c || true
```

Expect:

```
15c15,28
< int red[]     {0,2,0,0,0,0,0,0,0,0,0,0,5,
---
> int	getstr(char *s), play(int *player, int *playee, int pos[]);
> int	nextmove(int *player, int *playee), prtmov(int k);
> int	update(int *player, int *playee, int k);
> int	piececount(int *player, int startrow, int endrow);
> int	roll(void), movegen(int *mover, int *movee);
> int	moverecord(int *mover), strategy(int *player, int *playee);
> int	eval(int *player, int *playee, int k, int *prob);
> int	instructions(void);
> int	getprob(int *player, int *playee, int start, int finish);
> int	prtbrd(void);
> int	numline(int *upcol, int *downcol, int start, int fin);
> int	colorline(int *upcol, int c1, int *downcol, int c2, int start, int fin);
> int	bg_srand(void), bg_rand(void), _look(int *p), _store(int *p, int numb);
> int red[]     = {0,2,0,0,0,0,0,0,0,0,0,0,5,
18c31
< int white[]   {0,2,0,0,0,0,0,0,0,0,0,0,5,
---
> int white[]   = {0,2,0,0,0,0,0,0,0,0,0,0,5,
21c34
< int probability[]{0,11,12,13,14,15,16,
---
> int probability[]={0,11,12,13,14,15,16,
28c41,42
< main()
---
> int
> main(void)
33c47
< 	srand();
---
> 	bg_srand();
57c71
< 	    exit();
---
> 	    exit(0);
94c108
< 	    exit();
---
> 	    exit(0);
99,100c113,114
< getstr(s)
< char *s;
---
> int
> getstr(char *s)
103a118
> 	return(0);
106,107c121,122
< play(player,playee,pos)
< int *player,*playee,pos[];
---
> int
> play(int *player, int *playee, int pos[])
149,150c164,165
< nextmove(player,playee)
< int *player,*playee;
---
> int
> nextmove(int *player, int *playee)
170,171c185,186
< prtmov(k)
< int k;
---
> int
> prtmov(int k)
179a195
> 	return(0);
181,182c197,198
< update(player,playee,k)
< int *player,*playee,k;
---
> int
> update(int *player, int *playee, int k)
194a211
> 	return(0);
196,197c213,214
< piececount(player,startrow,endrow)
< int *player,startrow,endrow;
---
> int
> piececount(int *player, int startrow, int endrow)
202c219
< 	sum=+player[startrow++];
---
> 	sum+=player[startrow++];
205,221c222,223
< /*
< prtmovs()
< {
< 	int i1,i2;
< 	printf( "possible moves are\n");
< 	for(i1=0;i1<imoves;i1++){
< 		printf( "\n%d",i1);
< 		for(i2=0;i2<4;i2++){
< 			if(moves[i1].pos[i2]==NIL)break;
< 			printf( "%d, %d",moves[i1].pos[i2],moves[i1].mov[i2]);
< 		}
< 	}
< 	printf( "\n");
< }
< */
< 
< roll()
---
> int
> roll(void)
224,225c226,228
< 	die1=(rand()>>8)%6+1;
< 	die2=(rand()>>8)%6+1;
---
> 	die1=(bg_rand()>>8)%6+1;
> 	die2=(bg_rand()>>8)%6+1;
> 	return(0);
228,229c231,232
< movegen(mover,movee)
< int *mover,*movee;
---
> int
> movegen(int *mover, int *movee)
237c240
< 		if((k=25-i-die1)>0&&movee[k]>=2)
---
> 		if((k=25-i-die1)>0&&movee[k]>=2) {
239a243
> 		}
250c254
< 			if((k=25-j-die2)>0&&movee[k]>=2)
---
> 			if((k=25-j-die2)>0&&movee[k]>=2) {
252a257
> 			}
268c273
< 			    if((k=25-l-die1)>0&&movee[k]>=2)
---
> 			    if((k=25-l-die1)>0&&movee[k]>=2) {
270a276
> 			    }
281c287
< 				if((k=25-m-die1)>=0&&movee[k]>=2)
---
> 				if((k=25-m-die1)>=0&&movee[k]>=2) {
283a290
> 				}
313a321
> 	return(0);
315,316c323,324
< moverecord(mover)
< int *mover;
---
> int
> moverecord(int *mover)
326a335
> 	    /* fallthrough */
329a339
> 	    /* fallthrough */
332a343
> 	    /* fallthrough */
353a365
> 	return(0);
357,358c369,370
< strategy(player,playee)
< int *player,*playee;
---
> int
> strategy(int *player, int *playee)
391c403
< 	return(goodmoves[(rand()>>4)%n]);
---
> 	return(goodmoves[(bg_rand()>>4)%n]);
394,395c406,407
< eval(player,playee,k,prob)
< int *player,*playee,k,*prob;
---
> int
> eval(int *player, int *playee, int k, int *prob)
441c453
< 		sum=+ *p++ * n;	/*remove pieces, but just barely*/
---
> 		sum+= *p++ * n;	/*remove pieces, but just barely*/
449c461
< 	    for(p=newtry;p<q;)sum=- *p++;  /*bad to be on 1st three points*/
---
> 	    for(p=newtry;p<q;)sum-= *p++;  /*bad to be on 1st three points*/
453c465
< 	    *prob=+ n*getprob(newtry,newother,6*n-5,6*n);
---
> 	    *prob+= n*getprob(newtry,newother,6*n-5,6*n);
456c468,469
< instructions()
---
> int
> instructions(void)
482a496
> 	return(0);
485,486c499,500
< getprob(player,playee,start,finish)
< int *player,*playee,start,finish;
---
> int
> getprob(int *player, int *playee, int start, int finish)
498c512
< 		    if(playee[n]!=0)sum=+probability[k];
---
> 		    if(playee[n]!=0)sum+=probability[k];
504c518,519
< prtbrd()
---
> int
> prtbrd(void)
540a556
> 	return(0);
542,543c558,559
< numline(upcol,downcol,start,fin)
< int *upcol,*downcol,start,fin;
---
> int
> numline(int *upcol, int *downcol, int start, int fin)
549a566
> 	return(0);
551,553c568,569
< colorline(upcol,c1,downcol,c2,start,fin)
< int *upcol,*downcol,start,fin;
< char c1,c2;
---
> int
> colorline(int *upcol, int c1, int *downcol, int c2, int start, int fin)
562a579
> 	return(0);
565c582
< int rrno 0;
---
> int rrno = 0;
567,569c584,588
< srand(){
< 	rrno = _look( 0x40000 );
< 	_store( 0x40000, rrno+1 );
---
> int
> bg_srand(void){
> 	rrno = _look( (int *)0x40000 );
> 	_store( (int *)0x40000, rrno+1 );
> 	return(0);
572,574c591,594
< rand(){
< 	rrno =* 0106273;
< 	rrno =+ 020202;
---
> int
> bg_rand(void){
> 	rrno *= 0106273;
> 	rrno += 020202;
578c598,599
< _look(p) int *p; {
---
> int
> _look(int *p) {
582c603,604
< _store( p, numb ) int *p; {
---
> int
> _store(int *p, int numb) {
583a606
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
25c29,30
< shuffle(){
---
> int
> shuffle(void){
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
54c61,62
< draw() {
---
> int
> draw(void) {
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
107,108c121,123
< stats(){
< 	register i, ct, b;
---
> int
> stats(void){
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
208c228,229
< instruct(){
---
> int
> instruct(void){
215a237
> 	return(0);
218c240,241
< game(){
---
> int
> game(void){
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
319,320c345,347
< score(){
< 	register my, your, i;
---
> int
> score(void){
> 	register int my, your, i;
345a373
> 	return(0);
350c378,379
< guess(){
---
> int
> guess(void){
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
444c480,481
< myguess(){
---
> int
> myguess(void){
446c483
< 	register i, lg, t;
---
> 	register int i, lg, t;
457c494
< 		try[ntry++] = i;
---
> 		try[(unsigned char)ntry++] = i;
465c502
< 		if( hehas[try[i]] ) {
---
> 		if( hehas[(unsigned char)try[i]] ) {
474c511
< 		if( haveguessed[try[i]] < lg ) lg = haveguessed[try[i]];
---
> 		if( haveguessed[(unsigned char)try[i]] < lg ) lg = haveguessed[(unsigned char)try[i]];
480c517
< 		if( haveguessed[try[i]] == lg ) try[t++] = try[i];
---
> 		if( haveguessed[(unsigned char)try[i]] == lg ) try[t++] = try[i];
```

### cmd/quiz.c

Local test:

```
diff unix-v7-c99/v7/usr/src/games/quiz.c unix-v7-c99/cmd/quiz.c || true
```

Expect:

```
9a10,17
> int	readline(void), cmp(char *u, char *v), disj(int s), string(int s);
> int	eat(int s, int c), fold(int c), publish(char *t), pub1(int s);
> int	segment(char *u, char *w[]);
> int	perm(char *u[], int m, char *v[], int n, int p[]);
> int	find(char *u[], int m), readindex(void), talloc(void);
> int	query(char *r), next(void), done(void);
> int	instruct(char *info), badinfo(void), dunno(void);
> 
26c34
< char	*malloc();
---
> char	*malloc(unsigned n);
28c36,37
< readline()
---
> int
> readline(void)
31c40
< 	register c;
---
> 	register int c;
60,61c69,70
< cmp(u,v)
< char *u, *v;
---
> int
> cmp(char *u, char *v)
72c81,82
< disj(s)
---
> int
> disj(int s)
86c96
< 			return(t|x&s);
---
> 			return(t|(x&s));
111c121,122
< string(s)
---
> int
> string(int s)
128a140
> 			/* fallthrough */
155,156c167,168
< eat(s,c)
< char c;
---
> int
> eat(int s, int c)
171,172c183,184
< fold(c)
< char c;
---
> int
> fold(int c)
179,180c191,192
< publish(t)
< char *t;
---
> int
> publish(char *t)
183a196
> 	return(0);
186c199,200
< pub1(s)
---
> int
> pub1(int s)
196c210
< 			return;
---
> 			return(0);
204a219
> 			/* fallthrough */
212,213c227,228
< segment(u,w)
< char *u, *w[];
---
> int
> segment(char *u, char *w[])
244,246c259,260
< perm(u,m,v,n,p)
< int p[];
< char *u[], *v[];
---
> int
> perm(char *u[], int m, char *v[], int n, int p[])
265,266c279,280
< find(u,m)
< char *u[];
---
> int
> find(char *u[], int m)
277c291,292
< readindex()
---
> int
> readindex(void)
287a303
> 	return(0);
290c306,307
< talloc()
---
> int
> talloc(void)
294a312
> 	return(0);
297,298c315,316
< main(argc,argv)
< char *argv[];
---
> int
> main(int argc, char *argv[])
300c318
< 	register j;
---
> 	register int j;
306c324
< 	extern done();
---
> 	extern int done(void);
310c328
< 	inc = (int)tm&077774|01;
---
> 	inc = ((int)tm&077774)|01;
315c333
< 			if(argc>2) 
---
> 			if(argc>2)
335c353
< 	signal(SIGINT, done);
---
> 	signal(SIGINT, (int)done);
385,386c403,404
< query(r)
< char *r;
---
> int
> query(char *r)
404c422,423
< next()
---
> int
> next(void)
419c438,439
< done()
---
> int
> done(void)
425a446
> 	return(0);
427,428c448,449
< instruct(info)
< char *info;
---
> int
> instruct(char *info)
462a484
> 	return(0);
465c487,488
< badinfo(){
---
> int
> badinfo(void){
466a490
> 	return(0);
469c493,494
< dunno()
---
> int
> dunno(void)
472a498
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
19c20,23
< char	*intro[]
---
> int	tunnel(int i), rline(void), rnum(int n), rin(void);
> int	near(struct room *ap, int ahaz), icomp(const void *p1, const void *p2);
> 
> char	*intro[] =
95c99,100
< main()
---
> int
> main(void)
97c102
< 	register i, j;
---
> 	register int i, j;
99c104
< 	int k, icomp();
---
> 	int k, icomp(const void *, const void *);
159c164
< 			p->flag =| PIT;
---
> 			p->flag |= PIT;
166c171
< 			p->flag =| BAT;
---
> 			p->flag |= BAT;
172c177
< 	room[i].flag =| WUMP;
---
> 	room[i].flag |= WUMP;
270c275
< 	p->flag =& ~WUMP;
---
> 	p->flag &= ~WUMP;
274c279
< 	room[wloc].flag =| WUMP;
---
> 	room[wloc].flag |= WUMP;
284a290
> 	return(0);
287c293,294
< tunnel(i)
---
> int
> tunnel(int i)
290c297
< 	register n, j;
---
> 	register int n, j;
309c316,317
< rline()
---
> int
> rline(void)
317c325
< 			exit();
---
> 			exit(0);
324c332,333
< rnum(n)
---
> int
> rnum(int n)
326c335
< 	static first[2];
---
> 	static int first[2];
329c338
< 		time(first);
---
> 		time((long *)first);
335c344,345
< rin()
---
> int
> rin(void)
337c347
< 	register n, c;
---
> 	register int n, c;
345c355
< 					exit();
---
> 					exit(0);
356,357c366,367
< near(ap, ahaz)
< struct room *ap;
---
> int
> near(struct room *ap, int ahaz)
360c370
< 	register haz, i;
---
> 	register int haz, i;
370,371c380,381
< icomp(p1, p2)
< int *p1, *p2;
---
> int
> icomp(const void *p1, const void *p2)
374c384
< 	return(*p1 - *p2);
---
> 	return(*(const int *)p1 - *(const int *)p2);
```

### cmd/dc/dc.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/dc/dc.c unix-v7-c99/cmd/dc/dc.c || true
```

Expect:

```
4,6c4,11
< main(argc,argv)
< int argc;
< char *argv[];
---
> int init(), commnds(), readc(), unreadc(), pushp(), sdump(), chsign(),
>     subt(), eqk(), binop(), dscale(), release(), log2(), print(),
>     load(), seekc(), salterwd(), putwd(), command(), cond(),
>     more(), garbage(), ospace(), redef(), tenot(), oneot(), bigot(),
>     hexot(), onintr();
> 
> int
> main(int argc, char *argv[])
9a15
> 	return(0);
11c17,18
< commnds(){
---
> int
> commnds(void){
62c69
< 			sunputc(p);
---
> 			(void)sunputc(p);
395c402
< 				for(n = 0;n < PTRSZ-1;n++)sputc(q,0);
---
> 				for(n = 0;n < (int)PTRSZ-1;n++)sputc(q,0);
577,578c584
< div(ddivd,ddivr)
< struct blk *ddivd,*ddivr;
---
> div(struct blk *ddivd, struct blk *ddivr)
590c596
< 		errorrt("divide by 0\n");
---
> 		{printf("divide by 0\n"); return((struct blk *)1); }
697c703,704
< dscale(){
---
> int
> dscale(void){
727,728c734
< removr(p,n)
< struct blk *p;
---
> removr(struct blk *p, int n)
756,757c762
< sqrt(p)
< struct blk *p;
---
> sqrt(struct blk *p)
807,808c812
< exp(base,ex)
< struct blk *base,*ex;
---
> exp(struct blk *base, struct blk *ex)
861,863c865,866
< init(argc,argv)
< int argc;
< char *argv[];
---
> int
> init(int argc, char *argv[])
867,868c870,871
< 	if (signal(SIGINT, SIG_IGN) != SIG_IGN)
< 		signal(SIGINT,onintr);
---
> 	if (signal(SIGINT, (int)SIG_IGN) != (int)SIG_IGN)
> 		signal(SIGINT,(int)onintr);
918c921
< 	return;
---
> 	return(0);
919a923
> int
922c926
< 	signal(SIGINT,onintr);
---
> 	signal(SIGINT,(int)onintr);
928a933
> 	return(0);
930,931c935,936
< pushp(p)
< struct blk *p;
---
> int
> pushp(struct blk *p)
935c940
< 		return;
---
> 		return(0);
939c944
< 	return;
---
> 	return(0);
942c947
< pop(){
---
> pop(void){
950c955
< readin(){
---
> readin(void){
998,1000c1003
< add0(p,ct)
< int ct;
< struct blk *p;
---
> add0(struct blk *p, int ct)
1023,1024c1026
< mult(p,q)
< struct blk *p,*q;
---
> mult(struct blk *p, struct blk *q)
1078,1079c1080,1081
< chsign(p)
< struct blk *p;
---
> int
> chsign(struct blk *p)
1110c1112
< 	return;
---
> 	return(0);
1112c1114,1115
< readc(){
---
> int
> readc(void){
1132a1136
> 	return(0);
1134,1135c1138,1139
< unreadc(c)
< char c;
---
> int
> unreadc(int c)
1142c1146
< 	return;
---
> 	return(0);
1144,1145c1148,1149
< binop(c)
< char c;
---
> int
> binop(int c)
1164c1168
< 	return;
---
> 	return(0);
1166,1167c1170,1171
< print(hptr)
< struct blk *hptr;
---
> int
> print(struct blk *hptr)
1181c1185
< 			return;
---
> 			return(0);
1188c1192
< 		return;
---
> 		return(0);
1192c1196
< 	sunputc(p);
---
> 	(void)sunputc(p);
1200c1204
< 		return;
---
> 		return(0);
1204c1208
< 		return;
---
> 		return(0);
1208c1212
< 		return;
---
> 		return(0);
1227c1231
< 		return;
---
> 		return(0);
1243c1247
< 	return;
---
> 	return(0);
1247,1248c1251
< getdec(p,sc)
< struct blk *p;
---
> getdec(struct blk *p, int sc)
1278,1279c1281,1282
< tenot(p,sc)
< struct blk *p;
---
> int
> tenot(struct blk *p, int sc)
1295c1298
< 		return;
---
> 		return(0);
1325c1328
< 	return;
---
> 	return(0);
1327,1329c1330,1331
< oneot(p,sc,ch)
< struct blk *p;
< char ch;
---
> int
> oneot(struct blk *p, int sc, int ch)
1344c1346
< 	return;
---
> 	return(0);
1346,1347c1348,1349
< hexot(p,flg)
< struct blk *p;
---
> int
> hexot(struct blk *p, int flg)
1349a1352
> 	(void)flg;
1354c1357
< 		return;
---
> 		return(0);
1360c1363
< 		return;
---
> 		return(0);
1363c1366
< 	return;
---
> 	return(0);
1365,1366c1368,1369
< bigot(p,flg)
< struct blk *p;
---
> int
> bigot(struct blk *p, int flg)
1409c1412
< 			sunputc(strptr);
---
> 			(void)sunputc(strptr);
1414c1417
< 	return;
---
> 	return(0);
1417,1418c1420
< add(a1,a2)
< struct blk *a1,*a2;
---
> add(struct blk *a1, struct blk *a2)
1463c1465,1466
< eqk(){
---
> int
> eqk(void){
1493,1494c1496
< removc(p,n)
< struct blk *p;
---
> removc(struct blk *p, int n)
1515,1516c1517
< scalint(p)
< struct blk *p;
---
> scalint(struct blk *p)
1524,1525c1525
< scale(p,n)
< struct blk *p;
---
> scale(struct blk *p, int n)
1541c1541,1542
< subt(){
---
> int
> subt(void){
1552c1553,1554
< command(){
---
> int
> command(void){
1555c1557
< 	register (*savint)(),pid,rpid;
---
> 	register int (*savint)(),pid,rpid;
1574c1576
< 		savint = signal(SIGINT, SIG_IGN);
---
> 		savint = (int (*)())signal(SIGINT, (int)SIG_IGN);
1576c1578
< 		signal(SIGINT,savint);
---
> 		signal(SIGINT,(int)savint);
1581,1582c1583,1584
< cond(c)
< char c;
---
> int
> cond(int c)
1589c1591
< 	sunputc(p);
---
> 	(void)sunputc(p);
1614,1615c1616,1617
< 	if((cc<0 && (c == '<' || c == NG)) ||
< 		(cc >0) && (c == '>' || c == NL)){
---
> 	if(((signed char)cc<0 && (c == '<' || c == NG)) ||
> 		((cc >0) && (c == '>' || c == NL))){
1622c1624,1625
< load(){
---
> int
> load(void){
1653c1656
< 	return;
---
> 	return(0);
1655,1656c1658,1659
< log2(n)
< long n;
---
> int
> log2(long n)
1668,1669c1671
< salloc(size)
< int size;
---
> salloc(int size)
1688c1690
< morehd(){
---
> morehd(void){
1713,1715c1715
< copy(hptr,size)
< struct blk *hptr;
< int size;
---
> copy(struct blk *hptr, int size)
1741,1743c1741,1742
< sdump(s1,hptr)
< char *s1;
< struct blk *hptr;
---
> int
> sdump(char *s1, struct blk *hptr)
1749a1749
> 	return(0);
1751,1752c1751,1752
< seekc(hptr,n)
< struct blk *hptr;
---
> int
> seekc(struct blk *hptr, int n)
1769c1769
< 		return;
---
> 		return(0);
1773c1773
< 	return;
---
> 	return(0);
1775,1777c1775,1776
< salterwd(hptr,n)
< struct wblk *hptr;
< struct blk *n;
---
> int
> salterwd(struct wblk *hptr, struct blk *n)
1782c1781
< 	return;
---
> 	return(0);
1784,1785c1783,1784
< more(hptr)
< struct blk *hptr;
---
> int
> more(struct blk *hptr)
1804c1803
< 	return;
---
> 	return(0);
1806,1807c1805,1806
< ospace(s)
< char *s;
---
> int
> ospace(char *s)
1813a1813
> 	return(0);
1815,1816c1815,1816
< garbage(s)
< char *s;
---
> int
> garbage(char *s)
1822c1822
< 
---
> 	(void)s;
1859a1860
> 	return(0);
1861,1862c1862,1863
< redef(p)
< struct blk *p;
---
> int
> redef(struct blk *p)
1864c1865
< 	register offset;
---
> 	register int offset;
1881a1883
> 	return(0);
1884,1885c1886,1887
< release(p)
< register struct blk *p;
---
> int
> release(register struct blk *p)
1891a1894
> 	return(0);
1895,1896c1898
< getwd(p)
< struct blk *p;
---
> getwd(struct blk *p)
1906,1907c1908,1909
< putwd(p, c)
< struct blk *p, *c;
---
> int
> putwd(struct blk *p, struct blk *c)
1914a1917
> 	return(0);
1918,1919c1921
< lookwd(p)
< struct blk *p;
---
> lookwd(struct blk *p)
1929,1931c1931
< nalloc(p,nbytes)
< register char *p;
< unsigned nbytes;
---
> nalloc(register char *p, unsigned nbytes)
1933d1932
< 	char *malloc();
```

### cmd/dc/dc.h

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/dc/dc.h unix-v7-c99/cmd/dc/dc.h || true
```

Expect:

```
21a22
> #define DCSCHAR(c)	((signed char)(c))
30,32c31,33
< #define sgetc(p)	(((p)->rd==(p)->wt)?EOF:*(p)->rd++)
< #define slookc(p)	(((p)->rd==(p)->wt)?EOF:*(p)->rd)
< #define sbackc(p)	(((p)->rd==(p)->beg)?EOF:*(--(p)->rd))
---
> #define sgetc(p)	(((p)->rd==(p)->wt)?EOF:DCSCHAR(*(p)->rd++))
> #define slookc(p)	(((p)->rd==(p)->wt)?EOF:DCSCHAR(*(p)->rd))
> #define sbackc(p)	(((p)->rd==(p)->beg)?EOF:DCSCHAR(*(--(p)->rd)))
36c37
< #define sunputc(p)	(*( (p)->rd = --(p)->wt))
---
> #define sunputc(p)	(DCSCHAR(*( (p)->rd = --(p)->wt)))
112d112
< int	(*signal())();
114d113
< char	*malloc();
116d114
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
33,34c34,35
< 	{"ssen",ily,4,"-y+iness","+ness" },
< 	{"ssel",ily,4,"-y+i+less","+less" },
---
> 	{"ssen",ily,4,"-y+iness","+ness",	0, 0, "", ""},
> 	{"ssel",ily,4,"-y+i+less","+less",	0, 0, "", ""},
36,52c37,53
< 	{"s'",s,2,"","+'s"},
< 	{"s",s,1,"","+s"},
< 	{"ecn",ncy,1,"","-t+ce"},
< 	{"ycn",ncy,1,"","-cy+t"},
< 	{"ytilb",nop,0,"",""},
< 	{"ytilib",bility,5,"-le+ility",""},
< 	{"elbaif",i_to_y,4,"-y+iable",""},
< 	{"elba",CCe,4,"-e+able","+able"},
< 	{"yti",CCe,3,"-e+ity","+ity"},
< 	{"ylb",y_to_e,1,"-e+y",""},
< 	{"yl",ily,2,"-y+ily","+ly"},
< 	{"laci",strip,2,"","+al"},
< 	{"latnem",strip,2,"","+al"},
< 	{"lanoi",strip,2,"","+al"},
< 	{"tnem",strip,4,"","+ment"},
< 	{"gni",CCe,3,"-e+ing","+ing"},
< 	{"reta",nop,0,"",""},
---
> 	{"s'",s,2,"","+'s",		0, 0, "", ""},
> 	{"s",s,1,"","+s",		0, 0, "", ""},
> 	{"ecn",ncy,1,"","-t+ce",		0, 0, "", ""},
> 	{"ycn",ncy,1,"","-cy+t",		0, 0, "", ""},
> 	{"ytilb",nop,0,"","",		0, 0, "", ""},
> 	{"ytilib",bility,5,"-le+ility","",		0, 0, "", ""},
> 	{"elbaif",i_to_y,4,"-y+iable","",		0, 0, "", ""},
> 	{"elba",CCe,4,"-e+able","+able",		0, 0, "", ""},
> 	{"yti",CCe,3,"-e+ity","+ity",		0, 0, "", ""},
> 	{"ylb",y_to_e,1,"-e+y","",		0, 0, "", ""},
> 	{"yl",ily,2,"-y+ily","+ly",		0, 0, "", ""},
> 	{"laci",strip,2,"","+al",		0, 0, "", ""},
> 	{"latnem",strip,2,"","+al",		0, 0, "", ""},
> 	{"lanoi",strip,2,"","+al",		0, 0, "", ""},
> 	{"tnem",strip,4,"","+ment",		0, 0, "", ""},
> 	{"gni",CCe,3,"-e+ing","+ing",		0, 0, "", ""},
> 	{"reta",nop,0,"","",		0, 0, "", ""},
55,56c56,57
< 	{"citsi",strip,2,"","+ic"},
< 	{"cihparg",i_to_y,1,"-y+ic",""},
---
> 	{"citsi",strip,2,"","+ic",		0, 0, "", ""},
> 	{"cihparg",i_to_y,1,"-y+ic","",		0, 0, "", ""},
58,76c59,77
< 	{"cirtem",i_to_y,1,"-y+ic",""},
< 	{"yrtem",metry,0,"-ry+er",""},
< 	{"cigol",i_to_y,1,"-y+ic",""},
< 	{"tsigol",i_to_y,2,"-y+ist",""},
< 	{"tsi",VCe,3,"-e+ist","+ist"},
< 	{"msi",VCe,3,"-e+ism","+ist"},
< 	{"noitacif",i_to_y,6,"-y+ication",""},
< 	{"noitazi",ize,5,"-e+ation",""},
< 	{"rota",tion,2,"-e+or",""},
< 	{"noit",tion,3,"-e+ion","+ion"},
< 	{"naino",an,3,"","+ian"},
< 	{"na",an,1,"","+n"},
< 	{"evit",tion,3,"-e+ive","+ive"},
< 	{"ezi",CCe,3,"-e+ize","+ize"},
< 	{"pihs",strip,4,"","+ship"},
< 	{"dooh",ily,4,"-y+ihood","+hood"},
< 	{"luf",ily,3,"-y+iful","+ful"},
< 	{"ekil",strip,4,"","+like"},
< 	0
---
> 	{"cirtem",i_to_y,1,"-y+ic","",		0, 0, "", ""},
> 	{"yrtem",metry,0,"-ry+er","",		0, 0, "", ""},
> 	{"cigol",i_to_y,1,"-y+ic","",		0, 0, "", ""},
> 	{"tsigol",i_to_y,2,"-y+ist","",		0, 0, "", ""},
> 	{"tsi",VCe,3,"-e+ist","+ist",		0, 0, "", ""},
> 	{"msi",VCe,3,"-e+ism","+ist",		0, 0, "", ""},
> 	{"noitacif",i_to_y,6,"-y+ication","",		0, 0, "", ""},
> 	{"noitazi",ize,5,"-e+ation","",		0, 0, "", ""},
> 	{"rota",tion,2,"-e+or","",		0, 0, "", ""},
> 	{"noit",tion,3,"-e+ion","+ion",		0, 0, "", ""},
> 	{"naino",an,3,"","+ian",		0, 0, "", ""},
> 	{"na",an,1,"","+n",		0, 0, "", ""},
> 	{"evit",tion,3,"-e+ive","+ive",		0, 0, "", ""},
> 	{"ezi",CCe,3,"-e+ize","+ize",		0, 0, "", ""},
> 	{"pihs",strip,4,"","+ship",		0, 0, "", ""},
> 	{"dooh",ily,4,"-y+ihood","+hood",		0, 0, "", ""},
> 	{"luf",ily,3,"-y+iful","+ful",		0, 0, "", ""},
> 	{"ekil",strip,4,"","+like",		0, 0, "", ""},
> 	{0, 0, 0, 0, 0, 0, 0, 0, 0}
124,125c125,129
< main(argc,argv)
< char **argv;
---
> int suffix(), strip(), putsuf(), putw(), monosyl(), vowel(),
>     ise(), ztos(), dict();
> 
> int
> main(int argc, char **argv)
172c176
< 			for(cp=original,dp=word; *dp = *cp++; dp++)
---
> 			for(cp=original,dp=word; (*dp = *cp++); dp++)
181,182c185,186
< suffix(ep,lev)
< char *ep;
---
> int
> suffix(char *ep, int lev)
188c192
< 	for(t= &suftab[0];sp=t->suf;t++) {
---
> 	for(t= &suftab[0];(sp=t->suf);t++) {
208c212,213
< nop()
---
> int
> nop(void)
213,214c218,219
< strip(ep,d,a,lev)
< char *ep,*d,*a;
---
> int
> strip(char *ep, char *d, char *a, int lev)
215a221
> 	(void)d;
219,220c225,226
< s(ep,d,a,lev)
< char *ep,*d,*a;
---
> int
> s(char *ep, char *d, char *a, int lev)
229,230c235,236
< an(ep,d,a,lev)
< char *ep,*d,*a;
---
> int
> an(char *ep, char *d, char *a, int lev)
231a238
> 	(void)d;
237,238c244,245
< ize(ep,d,a,lev)
< char *ep,*d,*a;
---
> int
> ize(char *ep, char *d, char *a, int lev)
239a247
> 	(void)a;
244,245c252,253
< y_to_e(ep,d,a,lev)
< char *ep,*d,*a;
---
> int
> y_to_e(char *ep, char *d, char *a, int lev)
246a255
> 	(void)a;
251,252c260,261
< ily(ep,d,a,lev)
< char *ep,*d,*a;
---
> int
> ily(char *ep, char *d, char *a, int lev)
260,261c269,270
< ncy(ep,d,a,lev)
< char *ep, *d, *a;
---
> int
> ncy(char *ep, char *d, char *a, int lev)
269,270c278,279
< bility(ep,d,a,lev)
< char *ep,*d,*a;
---
> int
> bility(char *ep, char *d, char *a, int lev)
276,277c285,286
< i_to_y(ep,d,a,lev)
< char *ep,*d,*a;
---
> int
> i_to_y(char *ep, char *d, char *a, int lev)
286,287c295,296
< es(ep,d,a,lev)
< char *ep,*d,*a;
---
> int
> es(char *ep, char *d, char *a, int lev)
304,305c313,314
< metry(ep,d,a,lev)
< char *ep, *d,*a;
---
> int
> metry(char *ep, char *d, char *a, int lev)
312,313c321,322
< tion(ep,d,a,lev)
< char *ep,*d,*a;
---
> int
> tion(char *ep, char *d, char *a, int lev)
326,327c335,336
< CCe(ep,d,a,lev)
< char *ep,*d,*a;
---
> int
> CCe(char *ep, char *d, char *a, int lev)
344a354
> 		/* fallthrough */
348a359
> 		/* fallthrough */
352a364
> 		/* fallthrough */
363,364c375,376
< VCe(ep,d,a,lev)
< char *ep,*d,*a;
---
> int
> VCe(char *ep, char *d, char *a, int lev)
381,383c393,394
< char *lookuppref(wp,ep)
< char **wp;
< char *ep;
---
> char *
> lookuppref(char **wp, char *ep)
402,403c413,414
< putsuf(ep,a,lev)
< char *ep,*a;
---
> int
> putsuf(char *ep, char *a, int lev)
416c427
< 	while(cp=lookuppref(&bp,ep)) {
---
> 	while((cp=lookuppref(&bp,ep))) {
418c429
< 		while(*pp = *cp++)
---
> 		while((*pp = *cp++))
429,430c440,441
< putw(bp,ep,lev)
< char *bp,*ep;
---
> int
> putw(char *bp, char *ep, int lev)
432c443
< 	register i, j;
---
> 	register int i, j;
461,462c472,473
< monosyl(bp,ep)
< char *bp, *ep;
---
> int
> monosyl(char *bp, char *ep)
476,477c487
< skipv(s)
< char *s;
---
> skipv(char *s)
486c496,497
< vowel(c)
---
> int
> vowel(int c)
501c512,513
< ise()
---
> int
> ise(void)
508a521
> 	return(0);
510,511c523,524
< ztos(s)
< char *s;
---
> int
> ztos(char *s)
515a529
> 	return(0);
518,519c532,533
< dict(bp,ep)
< char *bp, *ep;
---
> int
> dict(char *bp, char *ep)
524c538
< 	register i;
---
> 	register int i;
527c541
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
8,9c9,10
< main(argc,argv)
< char **argv;
---
> int
> main(int argc, char **argv)
11c12
< 	register i, j;
---
> 	register int i, j;
23c24
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
3,4c4,5
< main(argc, argv)
< char **argv;
---
> int
> main(int argc, char **argv)
6c7
< 	register i, j;
---
> 	register int i, j;
30c31
< 		for (i=0; i<NP; i++) {
---
> 		for (i=0; i<(int)NP; i++) {
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
55,57c61,62
< main(argc, argv)
< int	argc;
< char	*argv[];
---
> int
> main(int argc, char *argv[])
140,145c145,150
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
195c200,201
< usage()
---
> int
> usage(void)
198a205
> 	return(0);
201,202c208,209
< dorep(argv)
< char	*argv[];
---
> int
> dorep(char *argv[])
253a261
> 	return(0);
256c264,265
< endtape()
---
> int
> endtape(void)
266c275,276
< getdir()
---
> int
> getdir(void)
273c283
< 		return;
---
> 		return(0);
289a300
> 	return(0);
292c303,304
< passtape()
---
> int
> passtape(void)
298c310
< 		return;
---
> 		return(0);
304a317
> 	return(0);
307,309c320,321
< putfile(longname, shortname)
< char *longname;
< char *shortname;
---
> int
> putfile(char *longname, char *shortname)
321c333
< 		return;
---
> 		return(0);
328c340
< 		return;
---
> 		return(0);
332c344
< 		return;
---
> 		return(0);
336c348,349
< 		for (i = 0, cp = buf; *cp++ = longname[i++];);
---
> 		for (i = 0, cp = buf; (*cp++ = longname[i++]);)
> 			;
362c375
< 		return;
---
> 		return(0);
366c379
< 		return;
---
> 		return(0);
376c389
< 		return;
---
> 		return(0);
400c413
< 			return;
---
> 			return(0);
437a451
> 	return(0);
442,443c456,457
< doxtract(argv)
< char	*argv[];
---
> int
> doxtract(char *argv[])
515a530
> 	return(0);
518c533,534
< dotable()
---
> int
> dotable(void)
531a548
> 	return(0);
534c551,552
< putempty()
---
> int
> putempty(void)
541a560
> 	return(0);
544,545c563,564
< longt(st)
< register struct stat *st;
---
> int
> longt(register struct stat *st)
554a574
> 	return(0);
581,582c601,602
< pmode(st)
< register struct stat *st;
---
> int
> pmode(register struct stat *st)
587a608
> 	return(0);
590,592c611,612
< select(pairp, st)
< int *pairp;
< struct stat *st;
---
> int
> select(int *pairp, struct stat *st)
600a621
> 	return(0);
603,604c624,625
< checkdir(name)
< register char *name;
---
> int
> checkdir(register char *name)
623a645
> 	return(0);
626c648,649
< onintr()
---
> int
> onintr(int sig)
628c651,652
< 	signal(SIGINT, SIG_IGN);
---
> 	(void)sig;
> 	signal(SIGINT, (int)SIG_IGN);
629a654
> 	return(0);
632c657,658
< onquit()
---
> int
> onquit(int sig)
634c660,661
< 	signal(SIGQUIT, SIG_IGN);
---
> 	(void)sig;
> 	signal(SIGQUIT, (int)SIG_IGN);
635a663
> 	return(0);
638c666,667
< onhup()
---
> int
> onhup(int sig)
640c669,670
< 	signal(SIGHUP, SIG_IGN);
---
> 	(void)sig;
> 	signal(SIGHUP, (int)SIG_IGN);
641a672
> 	return(0);
644c675,676
< onterm()
---
> int
> onterm(int sig)
646c678,679
< 	signal(SIGTERM, SIG_IGN);
---
> 	(void)sig;
> 	signal(SIGTERM, (int)SIG_IGN);
647a681
> 	return(0);
650,651c684,685
< tomodes(sp)
< register struct stat *sp;
---
> int
> tomodes(register struct stat *sp)
661a696
> 	return(0);
664c699,700
< checksum()
---
> int
> checksum(void)
666c702
< 	register i;
---
> 	register int i;
677,678c713,714
< checkw(c, name)
< char *name;
---
> int
> checkw(int c, char *name)
693c729,730
< response()
---
> int
> response(void)
704,705c741,742
< checkupdate(arg)
< char	*arg;
---
> int
> checkupdate(char *arg)
710c747
< 	daddr_t	lookup();
---
> 	daddr_t	lookup(char *s);
725c762,763
< done(n)
---
> int
> done(int n)
728a767
> 	return(0);
731,732c770,771
< prefix(s1, s2)
< register char *s1, *s2;
---
> int
> prefix(register char *s1, register char *s2)
742,743c781,782
< getwdir(s)
< char *s;
---
> int
> getwdir(char *s)
765a805
> 	return(0);
771,772c811
< lookup(s)
< char *s;
---
> lookup(char *s)
774c813
< 	register i;
---
> 	register int i;
785,787c824
< bsrch(s, n, l, h)
< daddr_t l, h;
< char *s;
---
> bsrch(char *s, int n, daddr_t l, daddr_t h)
789c826
< 	register i, j;
---
> 	register int i, j;
830,831c867,868
< cmp(b, s, n)
< char *b, *s;
---
> int
> cmp(char *b, char *s, int n)
833c870
< 	register i;
---
> 	register int i;
846,847c883,884
< readtape(buffer)
< char *buffer;
---
> int
> readtape(char *buffer)
856c893
< 		if ((i = read(mt, tbuf, TBLOCK*j)) < 0) {
---
> 		if ((i = read(mt, (char *)tbuf, TBLOCK*j)) < 0) {
878c915
< 	copy(buffer, &tbuf[recno++]);
---
> 	copy(buffer, (char *)&tbuf[recno++]);
882,883c919,920
< writetape(buffer)
< char *buffer;
---
> int
> writetape(char *buffer)
889c926
< 		if (write(mt, tbuf, TBLOCK*nblock) < 0) {
---
> 		if (write(mt, (char *)tbuf, TBLOCK*nblock) < 0) {
895c932
< 	copy(&tbuf[recno++], buffer);
---
> 	copy((char *)&tbuf[recno++], buffer);
897c934
< 		if (write(mt, tbuf, TBLOCK*nblock) < 0) {
---
> 		if (write(mt, (char *)tbuf, TBLOCK*nblock) < 0) {
906c943,944
< backtape()
---
> int
> backtape(void)
911c949
< 		if (read(mt, tbuf, TBLOCK*nblock) < 0) {
---
> 		if (read(mt, (char *)tbuf, TBLOCK*nblock) < 0) {
916a955
> 	return(0);
919c958,959
< flushtape()
---
> int
> flushtape(void)
921c961,962
< 	write(mt, tbuf, TBLOCK*nblock);
---
> 	write(mt, (char *)tbuf, TBLOCK*nblock);
> 	return(0);
924,925c965,966
< copy(to, from)
< register char *to, *from;
---
> int
> copy(register char *to, register char *from)
927c968
< 	register i;
---
> 	register int i;
932a974
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
17c18
< #define	FINIT	{0, NULL, 0.0, FLD|STR}
---
> #define	FINIT	{0, NULL, 0.0, FLD|STR, 0}
19c20
< 	{ "$record", record, 0.0, STR|FLD},
---
> 	{ "$record", record, 0.0, STR|FLD, 0},
31c32,33
< getrec()
---
> int
> getrec(void)
36c38
< 	register c, sep;
---
> 	register int c, sep;
87,88c89,90
< setclvar(s)	/* set var=value from s */
< char *s;
---
> int
> setclvar(char *s)	/* set var=value from s */
98a101
> 	return(0);
101c104,105
< fldbld()
---
> int
> fldbld(void)
158a163
> 	return(0);
161c166,167
< recbld()
---
> int
> recbld(void)
167c173
< 		return;
---
> 		return(0);
171c177
< 		while (*r++ = *p++)
---
> 		while ((*r++ = *p++))
181a188
> 	return(0);
184c191
< cell *fieldadr(n)
---
> cell *fieldadr(int n)
193c200,201
< yyerror(s) char *s; {
---
> int
> yyerror(char *s) {
195a204
> 	return(0);
198c207,209
< error(f, s, a1, a2, a3, a4, a5, a6, a7) {
---
> int
> error(int f, char *s, int a1, int a2, int a3, int a4, int a5, int a6, int a7)
> {
205a217
> 	return(0);
208c220,222
< PUTS(s) char *s; {
---
> int
> PUTS(char *s) {
> 	(void)s;
209a224
> 	return(0);
214,215c229,230
< isnumber(s)
< register char *s;
---
> int
> isnumber(register char *s)
217c232
< 	register d1, d2;
---
> 	register int d1, d2;
248c263
< 	if (!(d1 || point && d2))
---
> 	if (!(d1 || (point && d2)))
```

### cmd/awk/parse.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/awk/parse.c unix-v7-c99/cmd/awk/parse.c || true
```

Expect:

```
4c4,5
< node *ALLOC(n)
---
> int error();
> node *ALLOC(int n)
11c12
< node *exptostat(a) node *a;
---
> node *exptostat(node *a)
17c18
< node *node0(a)
---
> node *node0(int a)
24c25
< node *node1(a,b) node *b;
---
> node *node1(int a, node *b)
32c33
< node *node2(a,b,c) node *b, *c;
---
> node *node2(int a, node *b, node *c)
41c42
< node *node3(a,b,c,d) node *b, *c, *d;
---
> node *node3(int a, node *b, node *c, node *d)
51c52
< node *node4(a,b,c,d,e) node *b, *c, *d, *e;
---
> node *node4(int a, node *b, node *c, node *d, node *e)
62c63
< node *stat3(a,b,c,d) node *b, *c, *d;
---
> node *stat3(int a, node *b, node *c, node *d)
68c69
< node *op2(a,b,c) node *b, *c;
---
> node *op2(int a, node *b, node *c)
74c75
< node *op1(a,b) node *b;
---
> node *op1(int a, node *b)
80c81
< node *stat1(a,b) node *b;
---
> node *stat1(int a, node *b)
86c87
< node *op3(a,b,c,d) node *b, *c, *d;
---
> node *op3(int a, node *b, node *c, node *d)
92c93
< node *stat2(a,b,c) node *b, *c;
---
> node *stat2(int a, node *b, node *c)
98c99
< node *stat4(a,b,c,d,e) node *b, *c, *d, *e;
---
> node *stat4(int a, node *b, node *c, node *d, node *e)
104c105
< node *valtonode(a, b) cell *a;
---
> node *valtonode(cell *a, int b)
106c107
< 	x = node0(a);
---
> 	x = node0((int)a);
111c112
< node *genjump(a)
---
> node *genjump(int a)
117c118
< node *pa2stat(a,b,c) node *a, *b, *c;
---
> node *pa2stat(node *a, node *b, node *c)
123c124
< node *linkum(a,b) node *a, *b;
---
> node *linkum(node *a, node *b)
131c132
< node *genprint()
---
> node *genprint(void)
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
71c74
< 	printf("obj (*proctab[%d])() {\n", SIZE);
---
> 	printf("obj (*proctab[%d])() = {\n", SIZE);
76c79
< 	printf("char *printname[%d] {\n", SIZE);
---
> 	printf("char *printname[%d] = {\n", SIZE);
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
73a80,81
> 	if (a[1] == nullstat && a[2] == nullstat)
> 		return(true);
94a103
> int n;
97a107
> 	(void)n;
110a121
> 	(void)i;
126a138
> int n;
137c149
< 	if (n==MATCH && i==1 || n==NOTMATCH && i==0)
---
> 	if ((n==MATCH && i==1) || (n==NOTMATCH && i==0))
143a156
> int n;
153a167
> 		/* fallthrough */
174a189
> int n;
192a208
> 		/* fallthrough */
207a224
> int
210c227
< 	if (!istemp(a)) return;
---
> 	if (!istemp(a)) return(0);
212a230
> 	return(0);
232a251
> int n;
236a256
> 	(void)n;
247a268
> int nnn;
251a273
> 	(void)nnn;
286a309
> int nnn;
289a313
> 	(void)nnn;
381a406
> int n;
385a411
> 	(void)n;
397a424
> int n;
399c426
< 	awkfloat i,j;
---
> 	awkfloat i,j=0;
413a441
> 		/* fallthrough */
440a469
> int n;
461a491
> int n;
504a535
> int q;
508a540
> 	(void)q;
526a559
> int n;
528a562
> 	(void)n;
541a576
> int n;
562a598
> int n;
564a601
> 	(void)n;
576a614
> int nnn;
583a622
> 	(void)nnn;
612,613c651,652
< 			  || sep == ' ' && (*p == '\t' || *p == '\n')
< 			  || sep == '\t' && *p == '\n')
---
> 			  || (sep == ' ' && (*p == '\t' || *p == '\n'))
> 			  || (sep == '\t' && *p == '\n'))
629a669
> int n;
631a672
> 	(void)n;
645a687
> int n;
647a690
> 	(void)n;
664a708
> int n;
666a711
> 	(void)n;
687a733
> int n;
691a738
> 	(void)n;
712a760
> 	return(true);
715a764
> int n;
717a767
> 	(void)a;
740a791
> int n;
743c794
< 	awkfloat u;
---
> 	awkfloat u=0;
744a796
> 	(void)n;
766a819
> int n;
770a824
> 	(void)n;
774a829,830
> 		if (isfld(y))
> 			fldbld();
792c848
< obj nullproc() {}
---
> obj nullproc() { obj x = {0,0,0}; return(x); }
805c861,862
< redirprint(s, a, b) char *s; node *b;
---
> int
> redirprint(s, a, b) char *s; int a; node *b;
831a889
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
6,81c7,82
< "FIRSTTOKEN", 257,
< "FINAL", 258,
< "FATAL", 259,
< "LT", 260,
< "LE", 261,
< "GT", 262,
< "GE", 263,
< "EQ", 264,
< "NE", 265,
< "MATCH", 266,
< "NOTMATCH", 267,
< "APPEND", 268,
< "ADD", 269,
< "MINUS", 270,
< "MULT", 271,
< "DIVIDE", 272,
< "MOD", 273,
< "UMINUS", 274,
< "ASSIGN", 275,
< "ADDEQ", 276,
< "SUBEQ", 277,
< "MULTEQ", 278,
< "DIVEQ", 279,
< "MODEQ", 280,
< "JUMP", 281,
< "XBEGIN", 282,
< "XEND", 283,
< "NL", 284,
< "PRINT", 285,
< "PRINTF", 286,
< "SPRINTF", 287,
< "SPLIT", 288,
< "IF", 289,
< "ELSE", 290,
< "WHILE", 291,
< "FOR", 292,
< "IN", 293,
< "NEXT", 294,
< "EXIT", 295,
< "BREAK", 296,
< "CONTINUE", 297,
< "PROGRAM", 298,
< "PASTAT", 299,
< "PASTAT2", 300,
< "ASGNOP", 301,
< "BOR", 302,
< "AND", 303,
< "NOT", 304,
< "NUMBER", 305,
< "VAR", 306,
< "ARRAY", 307,
< "FNCN", 308,
< "SUBSTR", 309,
< "LSUBSTR", 310,
< "INDEX", 311,
< "RELOP", 312,
< "MATCHOP", 313,
< "OR", 314,
< "STRING", 315,
< "DOT", 316,
< "CCL", 317,
< "NCCL", 318,
< "CHAR", 319,
< "CAT", 320,
< "STAR", 321,
< "PLUS", 322,
< "QUEST", 323,
< "POSTINCR", 324,
< "PREINCR", 325,
< "POSTDECR", 326,
< "PREDECR", 327,
< "INCR", 328,
< "DECR", 329,
< "FIELD", 330,
< "INDIRECT", 331,
< "LASTTOKEN", 332,
---
> {"FIRSTTOKEN", 258},
> {"FINAL", 259},
> {"FATAL", 260},
> {"LT", 261},
> {"LE", 262},
> {"GT", 263},
> {"GE", 264},
> {"EQ", 265},
> {"NE", 266},
> {"MATCH", 267},
> {"NOTMATCH", 268},
> {"APPEND", 269},
> {"ADD", 270},
> {"MINUS", 271},
> {"MULT", 272},
> {"DIVIDE", 273},
> {"MOD", 274},
> {"UMINUS", 275},
> {"ASSIGN", 276},
> {"ADDEQ", 277},
> {"SUBEQ", 278},
> {"MULTEQ", 279},
> {"DIVEQ", 280},
> {"MODEQ", 281},
> {"JUMP", 282},
> {"XBEGIN", 283},
> {"XEND", 284},
> {"NL", 285},
> {"PRINT", 286},
> {"PRINTF", 287},
> {"SPRINTF", 288},
> {"SPLIT", 289},
> {"IF", 290},
> {"ELSE", 291},
> {"WHILE", 292},
> {"FOR", 293},
> {"IN", 294},
> {"NEXT", 295},
> {"EXIT", 296},
> {"BREAK", 297},
> {"CONTINUE", 298},
> {"PROGRAM", 299},
> {"PASTAT", 300},
> {"PASTAT2", 301},
> {"ASGNOP", 302},
> {"BOR", 303},
> {"AND", 304},
> {"NOT", 305},
> {"NUMBER", 306},
> {"VAR", 307},
> {"ARRAY", 308},
> {"FNCN", 309},
> {"SUBSTR", 310},
> {"LSUBSTR", 311},
> {"INDEX", 312},
> {"RELOP", 313},
> {"MATCHOP", 314},
> {"OR", 315},
> {"STRING", 316},
> {"DOT", 317},
> {"CCL", 318},
> {"NCCL", 319},
> {"CHAR", 320},
> {"CAT", 321},
> {"STAR", 322},
> {"PLUS", 323},
> {"QUEST", 324},
> {"POSTINCR", 325},
> {"PREINCR", 326},
> {"POSTDECR", 327},
> {"PREDECR", 328},
> {"INCR", 329},
> {"DECR", 330},
> {"FIELD", 331},
> {"INDIRECT", 332},
> {"LASTTOKEN", 333},
83c84,85
< ptoken(n)
---
> int
> ptoken(int n)
87c89
< 	else	if(n<LASTTOKEN) printf("lex: %s\n",tok[n-257].tnm);
---
> 	else	if(n<LASTTOKEN) printf("lex: %s\n",tok[n-FIRSTTOKEN].tnm);
89c91
< 	return;
---
> 	return(0);
92c94
< char *tokname(n)
---
> char *tokname(int n)
96c98
< 	return(tok[n-257].tnm);
---
> 	return(tok[n-FIRSTTOKEN].tnm);
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
20c21,22
< syminit()
---
> int
> syminit(void)
34a37
> 	return(0);
37c40
< cell **makesymtab()
---
> cell **makesymtab(void)
42c45
< 	cp = (char *) malloc(MAXSYM * sizeof(cell *));
---
> 	cp = (cell **) malloc(MAXSYM * sizeof(cell *));
50,51c53,54
< freesymtab(ap)	/* free symbol table */
< cell *ap;
---
> int
> freesymtab(cell *ap)	/* free symbol table */
57c60
< 		return;
---
> 		return(0);
63c66
< 			free(cp);
---
> 			free((char *)cp);
66a70
> 	return(0);
69,73c73
< cell *setsymtab(n, s, f, t, tab)
< char *n, *s;
< awkfloat f;
< unsigned t;
< cell **tab;
---
> cell *setsymtab(char *n, char *s, awkfloat f, unsigned t, cell **tab)
75c75
< 	register h;
---
> 	register int h;
77c77
< 	cell *lookup();
---
> 	cell *lookup(register char *s, cell **tab);
100,101c100,101
< hash(s)	/* form hash value for string s */
< register char *s;
---
> int
> hash(register char *s)	/* form hash value for string s */
110,112c110
< cell *lookup(s, tab)	/* look for s in tab */
< register char *s;
< cell **tab;
---
> cell *lookup(register char *s, cell **tab)	/* look for s in tab */
122,124c120
< awkfloat setfval(vp, f)
< register cell *vp;
< awkfloat f;
---
> awkfloat setfval(register cell *vp, awkfloat f)
137,139c133
< char *setsval(vp, s)
< register cell *vp;
< char *s;
---
> char *setsval(register cell *vp, char *s)
155,156c149
< awkfloat getfval(vp)
< register cell *vp;
---
> awkfloat getfval(register cell *vp)
181,182c174
< char *getsval(vp)
< register cell *vp;
---
> char *getsval(register cell *vp)
205,206c197,198
< checkval(vp)
< register cell *vp;
---
> int
> checkval(register cell *vp)
212a205
> 	return(0);
215,216c208
< char *tostring(s)
< register char *s;
---
> char *tostring(register char *s)
227,228c219,220
< yfree(a) char *a;
< {
---
> int
> yfree(char *a) {
230a223
> 	return(0);
235c228
< char *ymalloc(u) unsigned u;
---
> char *ymalloc(unsigned u)
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
108,109c113
< char *cclenter(p)
< register char *p;
---
> char *cclenter(register char *p)
111c115
< 	register i, c;
---
> 	register int i, c;
139c143,144
< overflo()
---
> int
> overflo(void)
141a147
> 	return(0);
144,145c150,151
< cfoll(v)		/* enter follow set of each leaf of vertex v into foll[leaf] */
< register node *v;
---
> int
> cfoll(register node *v)		/* enter follow set of each leaf of vertex v into foll[leaf] */
147c153
< 	register i;
---
> 	register int i;
149c155
< 	int *add();
---
> 	int *add(int n);
173a180
> 	return(0);
176,177c183,184
< first(p)			/* collects initially active leaves of p into setvec */
< register node *p;		/* returns 0 or 1 depending on whether p matches empty string */
---
> int
> first(register node *p)			/* collects initially active leaves of p into setvec; returns 0 or 1 depending on whether p matches empty string */
179c186
< 	register b;
---
> 	register int b;
210,211c217,218
< follow(v)
< node *v;		/* collects leaves that can follow v into setvec */
---
> int
> follow(node *v)		/* collects leaves that can follow v into setvec */
216c223
< 		return;
---
> 		return(0);
222c229
< 				return;
---
> 				return(0);
226c233
< 				return;
---
> 				return(0);
231c238
< 						return;
---
> 						return(0);
236c243
< 				return;
---
> 				return(0);
241c248
< 				return;
---
> 				return(0);
242a250
> 	return(0);
245,246c253,254
< member(c, s)	/* is c in s? */
< register char c, *s;
---
> int
> member(register char c, register char *s)	/* is c in s? */
254,257c262,265
< notin(array, n, prev)		/* is setvec in array[0] thru array[n]? */
< int **array;
< int *prev; {
< 	register i, j;
---
> int
> notin(int **array, int n, int *prev)		/* is setvec in array[0] thru array[n]? */
> {
> 	register int i, j;
272c280
< int *add(n) {		/* remember setvec */
---
> int *add(int n) {		/* remember setvec */
274c282
< 	register i;
---
> 	register int i;
288c296
< struct fa *cgotofn()
---
> struct fa *cgotofn(void)
290c298
< 	register i, k;
---
> 	register int i, k;
347,348c355,356
< 						if (isyms[*p] != 1) {
< 							isyms[*p] = 1;
---
> 						if (isyms[(unsigned char)*p] != 1) {
> 							isyms[(unsigned char)*p] = 1;
408,409c416,417
< 							if (isyms[*p] == 0 && symbol[*p] == 0) {
< 								symbol[*p] = 1;
---
> 							if (isyms[(unsigned char)*p] == 0 && symbol[(unsigned char)*p] == 0) {
> 								symbol[(unsigned char)*p] = 1;
428c436
< 			symbol[c] = 0;
---
> 			symbol[(unsigned char)c] = 0;
435c443
< 					if (k == CHAR && c == (int) right(cp)
---
> 					if ((k == CHAR && c == (int) right(cp))
437,438c445,446
< 					 || k == CCL && member(c, (char *) right(cp))
< 					 || k == NCCL && !member(c, (char *) right(cp))) {
---
> 					 || (k == CCL && member(c, (char *) right(cp)))
> 					 || (k == NCCL && !member(c, (char *) right(cp)))) {
507,509c515,516
< match(pfa, p)
< register struct fa *pfa;
< register char *p;
---
> int
> match(register struct fa *pfa, register char *p)
511c518
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
15c16,87
< main(argc, argv) int argc; char *argv[]; {
---
> char lexbuf[512];
> 
> int
> haschar(char *s, int c)
> {
> 	while (*s)
> 		if (*s++ == c)
> 			return(1);
> 	return(0);
> }
> 
> int
> kwstart(char *s, char *kw)
> {
> 	while (*kw)
> 		if (*s++ != *kw++)
> 			return(0);
> 	return(*s == 0 || *s == '{' || *s == ' ' || *s == '\t');
> }
> 
> int
> awkcmdstart(char *s)
> {
> 	return(*s == '{' || kwstart(s, "BEGIN") || kwstart(s, "END"));
> }
> 
> int
> awkcmdnext(char *s)
> {
> 	return(kwstart(s, "BEGIN") || kwstart(s, "END"));
> }
> 
> int
> awkcmdnextact(int argc, char *argv[], int i)
> {
> 	if (i >= argc || !awkcmdnext(argv[i]))
> 		return(0);
> 	if (haschar(argv[i], '{'))
> 		return(1);
> 	return(i + 1 < argc && argv[i+1][0] == '{');
> }
> 
> int
> awkcmdsplit(int argc, char *argv[])
> {
> 	char *p;
> 	int braces, sawbrace, i;
> 
> 	if (!awkcmdstart(argv[0]))
> 		return(0);
> 	braces = 0;
> 	sawbrace = 0;
> 	for (i = 0; i < argc; i++) {
> 		for (p = argv[i]; *p; p++) {
> 			if (*p == '{') {
> 				braces++;
> 				sawbrace = 1;
> 			} else if (*p == '}') {
> 				braces--;
> 			}
> 		}
> 		if (sawbrace && braces <= 0) {
> 			if (awkcmdnextact(argc, argv, i+1))
> 				continue;
> 			return(i != 0);
> 		}
> 	}
> 	return(0);
> }
> 
> int
> main(int argc, char *argv[]) {
41c113,152
< 			argv[0] = argv[-1];	/* need this space */
---
> 			if (awkcmdsplit(argc, argv)) {
> 				char *cmdname;
> 				char *p;
> 				int braces, n, sawbrace, wantact;
> 
> 				cmdname = argv[-1];
> 				p = lexbuf;
> 				braces = 0;
> 				n = 0;
> 				sawbrace = 0;
> 				wantact = 0;
> 				while (argc > 0) {
> 					char *q;
> 
> 					if (n++ != 0 && p < &lexbuf[sizeof(lexbuf)-1])
> 						*p++ = ' ';
> 					if (awkcmdnext(argv[0]))
> 						wantact = 1;
> 					for (q = argv[0]; *q && p < &lexbuf[sizeof(lexbuf)-1]; q++) {
> 						if (*q == '{') {
> 							braces++;
> 							sawbrace = 1;
> 							wantact = 0;
> 						} else if (*q == '}')
> 							braces--;
> 						*p++ = *q;
> 					}
> 					argc--;
> 					if (sawbrace && braces <= 0 && !wantact &&
> 					    !awkcmdnextact(argc + 1, argv, 1))
> 						break;
> 					argv++;
> 				}
> 				*p = 0;
> 				lexprog = lexbuf;
> 				argc++;
> 				argv[0] = cmdname;
> 			}
> 			else
> 				argv[0] = argv[-1];	/* need this space */
71c182
< 		write(ansfd, &errorflag, sizeof(errorflag));
---
> 		write(ansfd, (char *)&errorflag, sizeof(errorflag));
77c188,189
< logit(n, s) char *s[];
---
> int
> logit(int n, char *s[])
82,84c194,196
< 		return;
< 	time(tvec);
< 	fprintf(f, "%-8s %s", getlogin(), ctime(tvec));
---
> 		return(0);
> 	time((long *)tvec);
> 	fprintf(f, "%-8s %s", getlogin(), ctime((long *)tvec));
90c202
< 		return;
---
> 		return(0);
94c206
< 		return;
---
> 		return(0);
99a212
> 	return(0);
102c215,216
< yywrap()
---
> int
> yywrap(void)
107c221,222
< msgfiles()
---
> int
> msgfiles(void)
134c249
< 	xargv=s=svargv=malloc(n*sizeof(char *));
---
> 	xargv=s=svargv=(char **)malloc(n*sizeof(char *));
139a255
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
diff unix-v7-c99/v7/usr/src/cmd/tp/tp1.c unix-v7-c99/cmd/tp/tp1.c | perl -pe 's/\x0c/^L/g' || true
```

Expect:

```
1a2
> #include <stdio.h>
3,4c4,10
< main(argc,argv)
< char **argv;
---
> int	optap(), setcom(), useerr(), check(), done(), encode(),
> 	decode(), cmd(), cmr(), cmt(), cmx(),
> 	clrdir(), clrent(), rddir(), gettape(), wrdir(), getfiles(),
> 	update(), delete(), taboc(), extract(), usage();
> 
> int
> main(int argc, char **argv)
7c13,14
< 	extern cmd(), cmr(),cmx(), cmt();
---
> 	extern int cmd(), cmr(),cmx(), cmt();
> 	(void)argc;
15c22
< 		while (c = *ptr++) switch(c)  {
---
> 		while ((c = *ptr++)) switch(c)  {
62a70
> 	return(0);
65c73,74
< optap()
---
> int
> optap(void)
67c76
< 	extern cmr();
---
> 	extern int cmr();
86a96
> 	return(0);
89,90c99,100
< setcom(newcom)
< int (*newcom)();
---
> int
> setcom(int (*newcom)(void))
92c102
< 	extern cmr();
---
> 	extern int cmr();
95a106
> 	return(0);
98c109,110
< useerr()
---
> int
> useerr(void)
101a114
> 	return(0);
104c117
< /*^L/* COMMANDS */
---
> /*^L COMMANDS */
106c119,120
< cmd()
---
> int
> cmd(void)
108c122
< 	extern delete();
---
> 	extern int delete(void);
115a130
> 	return(0);
118c133,134
< cmr()
---
> int
> cmr(void)
124a141
> 	return(0);
127c144,145
< cmt()
---
> int
> cmt(void)
129c147
< 	extern taboc();
---
> 	extern int taboc(struct dent *);
136a155
> 	return(0);
139c158,159
< cmx()
---
> int
> cmx(void)
141c161
< 	extern extract();
---
> 	extern int extract(struct dent *);
146a167
> 	return(0);
148a170
> int
152a175
> 	return(0);
154a178
> int
158a183
> 	return(0);
160a186
> int
168c194
< 	register n;
---
> 	register int n;
185a212
> 	return(0);
187a215
> int
194a223
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
10c14,15
< clrdir()
---
> int
> clrdir(void)
12c17
< 	register j, *p;
---
> 	register int j, *p;
17a23
> 	return(0);
20,21c26,27
< clrent(ptr)
< struct	dent *ptr;
---
> int
> clrent(struct dent *ptr)
23c29
< 	register *p, j;
---
> 	register int *p, j;
32c38
< 			return;
---
> 			return(0);
34a41
> 	return(0);
38c45,46
< rddir()
---
> int
> rddir(void)
68c76
< 		for(i=0;i<sizeof(struct tent)/sizeof(short);i++)
---
> 		for(i=0;i<(int)(sizeof(struct tent)/sizeof(short));i++)
92c100
< 	if(sum != 0)
---
> 	if(sum != 0) {
100c108
< 			return;
---
> 			return(0);
101a110
> 	}
102a112
> 	return(0);
106c116,117
< wrdir()
---
> int
> wrdir(void)
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
164c175,176
< tread()
---
> int
> tread(void)
166c178
< 	register j, *ptr;
---
> 	register int j, *ptr;
175a188
> 	return(0);
178c191,192
< twrite()
---
> int
> twrite(void)
184a199
> 	return(0);
187c202,203
< rseek(blk)
---
> int
> rseek(int blk)
190a207
> 	return(0);
193c210,211
< wseek(blk)
---
> int
> wseek(int blk)
195c213
< 	register amt, b;
---
> 	register int amt, b;
204a223
> 	return(0);
207c226,227
< seekerr()
---
> int
> seekerr(void)
210a231
> 	return(0);
213c234,235
< verify(key)
---
> int
> verify(int key)
215c237
< 	register c;
---
> 	register int c;
235c257,258
< getfiles()
---
> int
> getfiles(void)
244a268
> 	return(0);
248c272,273
< expand()
---
> int
> expand(void)
258c283
< 				return;
---
> 				return(0);
276a302
> int
280a307
> 	return(0);
282a310
> int
295c323
< 		if(mode != S_IFREG) return;
---
> 		if(mode != S_IFREG) return(0);
316c344
< 				return;
---
> 				return(0);
318c346
< 		if (verify('r') < 0)	return;
---
> 		if (verify('r') < 0)	return(0);
330c358
< 	if (verify('a') < 0)		return;
---
> 	if (verify('a') < 0)		return(0);
338a367
> 	return(0);
341,342c370,371
< swabdir(tp)
< register struct tent *tp;
---
> int
> swabdir(register struct tent *tp)
346a376
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
3,4c4,9
< gettape(how)
< int (*how)();
---
> int	decode(), verify(), clrent(), bitmap(), maperr(), setmap(),
> 	wrdir(), update1(), wseek(), twrite(), phserr(), done(),
> 	rseek(), tread(), usage();
> 
> int
> gettape(int (*how)(struct dent *))
30a36
> 	return(0);
33,34c39,40
< delete(dd)
< struct dent *dd;
---
> int
> delete(struct dent *dd)
37a44
> 	return(0);
41c48,49
< update()
---
> int
> update(void)
44c52
< 	register b, last;
---
> 	register int b, last;
67a76
> 	return(0);
71c80,81
< update1()
---
> int
> update1(void)
74c84
< 	register index;
---
> 	register int index;
88c98
< 		if ((d = id) == 0)	return;
---
> 		if ((d = id) == 0)	return(0);
101c111
< 		if (index = d->d_size % BSIZE) {
---
> 		if ((index = d->d_size % BSIZE)) {
110,111c120,122
< phserr()
< {	printf("%s -- Phase error \n", name);  }
---
> int
> phserr(void)
> {	printf("%s -- Phase error \n", name); return(0);  }
113a125
> int
117c129
< 	register count;
---
> 	register int count;
127a140
> 	return(0);
130,131c143,144
< setmap(d)
< register struct dent *d;
---
> int
> setmap(register struct dent *d)
140c153
< 	if ((c += block) >= tapsiz)		maperr();
---
> 	if ((c += block) >= (unsigned)tapsiz)		maperr();
146a160
> 	return(0);
149c163,164
< maperr()
---
> int
> maperr(void)
152a168
> 	return(0);
156c172,173
< usage()
---
> int
> usage(void)
158c175
< 	register reg,count;
---
> 	register int reg,count;
160c177
< 	static lused;
---
> 	static int lused;
186a204
> 	return(0);
190,191c208,209
< taboc(dd)
< struct dent *dd;
---
> int
> taboc(struct dent *dd)
193,194c211,212
< 	register  mode;
< 	register *m;
---
> 	register int mode;
> 	register int *m;
196c214
< 	int count, *localtime();
---
> 	int count;
215c233
< 		m = localtime(&dd->d_time);
---
> 		m = (int *)localtime(&dd->d_time);
218a237
> 	return(0);
222,223c241,242
< extract(d)
< register struct dent *d;
---
> int
> extract(register struct dent *d)
225c244
< 	register count, id;
---
> 	register int count, id;
227,228c246,247
< 	if (d->d_size==0)	return;
< 	if (verify('x') < 0)			return;
---
> 	if (d->d_size==0)	return(0);
> 	if (verify('x') < 0)			return(0);
238c257
< 	if (count = d->d_size % BSIZE) {
---
> 	if ((count = d->d_size % BSIZE)) {
243c262
< 			return;
---
> 			return(0);
247a267
> 	return(0);
```

### sys/slp.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/slp.c unix-v7-c99/sys/slp.c || true
```

Expect:

```
10c10,21
< #include "../h/buf.h"
---
> #include "../h/proto.h"
> 
> /* spl0/spl6/splx/panic/malloc/mfree/copyseg/save/resume come from h/proto.h.
>  * issig comes from h/systm.h. */
> extern void sureg(void);
> extern void xswap(struct proc *, int, int);
> 
> void wakeup(register caddr_t chan);
> void setrun(register struct proc *p);
> void setrq(struct proc *p);
> void swtch(void);
> void qswtch(void);
27,28c38,39
< sleep(chan, pri)
< caddr_t chan;
---
> void
> sleep(caddr_t chan, int pri)
31c42
< 	register s, h;
---
> 	register int s, h;
82,83c93,94
< wakeup(chan)
< register caddr_t chan;
---
> void
> wakeup(register caddr_t chan)
86c97
< 	register i;
---
> 	register int i;
112,119c123,127
< /*
<  * when you are sure that it
<  * is impossible to get the
<  * 'proc on q' diagnostic, the
<  * diagnostic loop can be removed.
<  */
< setrq(p)
< struct proc *p;
---
> /* PORT: our scheduler doesn't unlink from v7's runq during swtch, so
>  * wakeup()->setrun() races re-add procs already linked.  Silently
>  * dedupe instead of printing; functionally a no-op. */
> void
> setrq(struct proc *p)
122c130
< 	register s;
---
> 	register int s;
126,129c134
< 		if(q == p) {
< 			printf("proc on q\n");
< 			goto out;
< 		}
---
> 		if(q == p) goto out;
138a144,150
>  *
>  * PORT DIVERGENCE: armboot_setrun(p->p_pid) added so the port's
>  * scheduler (which keeps its own armproc_state[] table) sees the
>  * wakeup.  Without it, v7's wakeup()->setrun() flips p_stat = SRUN
>  * but mt_pick_runnable() never picks the slot because its
>  * armproc_state stays PSTATE_SLEEP.  No semantic change to v7's
>  * state machine; just a cross-side notify.
140,141c152,155
< setrun(p)
< register struct proc *p;
---
> /* armboot_setrun declared in h/proto.h. */
> 
> void
> setrun(register struct proc *p)
151c165
< 	if (w = p->p_wchan) {
---
> 	if ((w = p->p_wchan)) {
156a171
> 	armboot_setrun((int)p->p_pid);
171,172c186,187
< setpri(pp)
< register struct proc *pp;
---
> int
> setpri(register struct proc *pp)
174c189
< 	register p;
---
> 	register int p;
186,322c201,204
< /*
<  * The main loop of the scheduling (swapping)
<  * process.
<  * The basic idea is:
<  *  see if anyone wants to be swapped in;
<  *  swap out processes until there is room;
<  *  swap him in;
<  *  repeat.
<  * The runout flag is set whenever someone is swapped out.
<  * Sched sleeps on it awaiting work.
<  *
<  * Sched sleeps on runin whenever it cannot find enough
<  * core (by swapping out or otherwise) to fit the
<  * selected swapped process.  It is awakened when the
<  * core situation changes and in any case once per second.
<  */
< sched()
< {
< 	register struct proc *rp, *p;
< 	register outage, inage;
< 	int maxsize;
< 
< 	/*
< 	 * find user to swap in;
< 	 * of users ready, select one out longest
< 	 */
< 
< loop:
< 	spl6();
< 	outage = -20000;
< 	for (rp = &proc[0]; rp < &proc[NPROC]; rp++)
< 	if (rp->p_stat==SRUN && (rp->p_flag&SLOAD)==0 &&
< 	    rp->p_time - (rp->p_nice-NZERO)*8 > outage) {
< 		p = rp;
< 		outage = rp->p_time - (rp->p_nice-NZERO)*8;
< 	}
< 	/*
< 	 * If there is no one there, wait.
< 	 */
< 	if (outage == -20000) {
< 		runout++;
< 		sleep((caddr_t)&runout, PSWP);
< 		goto loop;
< 	}
< 	spl0();
< 
< 	/*
< 	 * See if there is core for that process;
< 	 * if so, swap it in.
< 	 */
< 
< 	if (swapin(p))
< 		goto loop;
< 
< 	/*
< 	 * none found.
< 	 * look around for core.
< 	 * Select the largest of those sleeping
< 	 * at bad priority; if none, select the oldest.
< 	 */
< 
< 	spl6();
< 	p = NULL;
< 	maxsize = -1;
< 	inage = -1;
< 	for (rp = &proc[0]; rp < &proc[NPROC]; rp++) {
< 		if (rp->p_stat==SZOMB
< 		 || (rp->p_flag&(SSYS|SLOCK|SULOCK|SLOAD))!=SLOAD)
< 			continue;
< 		if (rp->p_textp && rp->p_textp->x_flag&XLOCK)
< 			continue;
< 		if (rp->p_stat==SSLEEP&&rp->p_pri>=PZERO || rp->p_stat==SSTOP) {
< 			if (maxsize < rp->p_size) {
< 				p = rp;
< 				maxsize = rp->p_size;
< 			}
< 		} else if (maxsize<0 && (rp->p_stat==SRUN||rp->p_stat==SSLEEP)) {
< 			if (rp->p_time+rp->p_nice-NZERO > inage) {
< 				p = rp;
< 				inage = rp->p_time+rp->p_nice-NZERO;
< 			}
< 		}
< 	}
< 	spl0();
< 	/*
< 	 * Swap found user out if sleeping at bad pri,
< 	 * or if he has spent at least 2 seconds in core and
< 	 * the swapped-out process has spent at least 3 seconds out.
< 	 * Otherwise wait a bit and try again.
< 	 */
< 	if (maxsize>=0 || (outage>=3 && inage>=2)) {
< 		p->p_flag &= ~SLOAD;
< 		xswap(p, 1, 0);
< 		goto loop;
< 	}
< 	spl6();
< 	runin++;
< 	sleep((caddr_t)&runin, PSWP);
< 	goto loop;
< }
< 
< /*
<  * Swap a process in.
<  * Allocate data and possible text separately.
<  * It would be better to do largest first.
<  */
< swapin(p)
< register struct proc *p;
< {
< 	register struct text *xp;
< 	register int a;
< 	int x;
< 
< 	if ((a = malloc(coremap, p->p_size)) == NULL)
< 		return(0);
< 	if (xp = p->p_textp) {
< 		xlock(xp);
< 		if (xp->x_ccount==0) {
< 			if ((x = malloc(coremap, xp->x_size)) == NULL) {
< 				xunlock(xp);
< 				mfree(coremap, p->p_size, a);
< 				return(0);
< 			}
< 			xp->x_caddr = x;
< 			if ((xp->x_flag&XLOAD)==0)
< 				swap(xp->x_daddr,x,xp->x_size,B_READ);
< 		}
< 		xp->x_ccount++;
< 		xunlock(xp);
< 	}
< 	swap(p->p_addr, a, p->p_size, B_READ);
< 	mfree(swapmap, ctod(p->p_size), p->p_addr);
< 	p->p_addr = a;
< 	p->p_flag |= SLOAD;
< 	p->p_time = 0;
< 	return(1);
< }
---
> /* v7's sched() main loop (the proc-0 "swapper" task) and its swapin()
>  * helper drove the per-process swap-in/swap-out cycle.  This port keeps
>  * every proc resident, so neither runs -- the C scheduler is in
>  * armboot_swtch() (see swtch() below). */
329c211,212
< qswtch()
---
> void
> qswtch(void)
338,345c221,233
<  * if the calling process is not in RUN state,
<  * arrangements for it to restart must have
<  * been made elsewhere, usually by calling via sleep.
<  * There is a race here. A process may become
<  * ready after it has been examined.
<  * In this case, idle() will be called and
<  * will return in at most 1HZ time.
<  * i.e. its not worth putting an spl() in.
---
>  *
>  * PORT DIVERGENCE (documented in logs/unix-on-qemu.md): the original
>  * v7 body walked `runq` (a linked list of SRUN procs), picked the
>  * lowest p_pri, called save(u.u_rsav) on the current process, and
>  * resume()'d into the picked one -- with idle() / proc 0 swapper
>  * dance for the no-runnable case.  That model assumes per-proc u-
>  * areas swapped in/out of core by an external swapper, which this
>  * port does not have.  Instead we keep every proc's u-area + kernel
>  * stack permanently in RAM (the save-slot pool in arch/arm.c),
>  * and the equivalent save+pick+resume sequence lives in
>  * armboot_swtch().  Routing through it here means v7's
>  * sleep()/wakeup()/setrun()/exit()/wait()/pause() in this TU and
>  * sys/sys1.c / sys/sys4.c / sys/pipe.c work unchanged.
347,350c235
< swtch()
< {
< 	register n;
< 	register struct proc *p, *q, *pp, *pq;
---
> /* armboot_swtch declared in h/proto.h. */
352,418c237,240
< 	/*
< 	 * If not the idle process, resume the idle process.
< 	 */
< 	if (u.u_procp != &proc[0]) {
< 		if (save(u.u_rsav)) {
< 			sureg();
< 			return;
< 		}
< 		if (u.u_fpsaved==0) {
< 			savfp(&u.u_fps);
< 			u.u_fpsaved = 1;
< 		}
< 		resume(proc[0].p_addr, u.u_qsav);
< 	}
< 	/*
< 	 * The first save returns nonzero when proc 0 is resumed
< 	 * by another process (above); then the second is not done
< 	 * and the process-search loop is entered.
< 	 *
< 	 * The first save returns 0 when swtch is called in proc 0
< 	 * from sched().  The second save returns 0 immediately, so
< 	 * in this case too the process-search loop is entered.
< 	 * Thus when proc 0 is awakened by being made runnable, it will
< 	 * find itself and resume itself at rsav, and return to sched().
< 	 */
< 	if (save(u.u_qsav)==0 && save(u.u_rsav))
< 		return;
< loop:
< 	spl6();
< 	runrun = 0;
< 	pp = NULL;
< 	q = NULL;
< 	n = 128;
< 	/*
< 	 * Search for highest-priority runnable process
< 	 */
< 	for(p=runq; p!=NULL; p=p->p_link) {
< 		if((p->p_stat==SRUN) && (p->p_flag&SLOAD)) {
< 			if(p->p_pri < n) {
< 				pp = p;
< 				pq = q;
< 				n = p->p_pri;
< 			}
< 		}
< 		q = p;
< 	}
< 	/*
< 	 * If no process is runnable, idle.
< 	 */
< 	p = pp;
< 	if(p == NULL) {
< 		idle();
< 		goto loop;
< 	}
< 	q = pq;
< 	if(q == NULL)
< 		runq = p->p_link;
< 	else
< 		q->p_link = p->p_link;
< 	curpri = n;
< 	spl0();
< 	/*
< 	 * The rsav (ssav) contents are interpreted in the new address space
< 	 */
< 	n = p->p_flag&SSWAP;
< 	p->p_flag &= ~SSWAP;
< 	resume(p->p_addr, n? u.u_ssav: u.u_rsav);
---
> void
> swtch(void)
> {
> 	armboot_swtch();
426,530c248,252
< newproc()
< {
< 	int a1, a2;
< 	struct proc *p, *up;
< 	register struct proc *rpp, *rip;
< 	register n;
< 
< 	p = NULL;
< 	/*
< 	 * First, just locate a slot for a process
< 	 * and copy the useful info from this process into it.
< 	 * The panic "cannot happen" because fork has already
< 	 * checked for the existence of a slot.
< 	 */
< retry:
< 	mpid++;
< 	if(mpid >= 30000) {
< 		mpid = 0;
< 		goto retry;
< 	}
< 	for(rpp = &proc[0]; rpp < &proc[NPROC]; rpp++) {
< 		if(rpp->p_stat == NULL && p==NULL)
< 			p = rpp;
< 		if (rpp->p_pid==mpid || rpp->p_pgrp==mpid)
< 			goto retry;
< 	}
< 	if ((rpp = p)==NULL)
< 		panic("no procs");
< 
< 	/*
< 	 * make proc entry for new proc
< 	 */
< 
< 	rip = u.u_procp;
< 	up = rip;
< 	rpp->p_stat = SRUN;
< 	rpp->p_clktim = 0;
< 	rpp->p_flag = SLOAD;
< 	rpp->p_uid = rip->p_uid;
< 	rpp->p_pgrp = rip->p_pgrp;
< 	rpp->p_nice = rip->p_nice;
< 	rpp->p_textp = rip->p_textp;
< 	rpp->p_pid = mpid;
< 	rpp->p_ppid = rip->p_pid;
< 	rpp->p_time = 0;
< 	rpp->p_cpu = 0;
< 
< 	/*
< 	 * make duplicate entries
< 	 * where needed
< 	 */
< 
< 	for(n=0; n<NOFILE; n++)
< 		if(u.u_ofile[n] != NULL)
< 			u.u_ofile[n]->f_count++;
< 	if(up->p_textp != NULL) {
< 		up->p_textp->x_count++;
< 		up->p_textp->x_ccount++;
< 	}
< 	u.u_cdir->i_count++;
< 	if (u.u_rdir)
< 		u.u_rdir->i_count++;
< 	/*
< 	 * Partially simulate the environment
< 	 * of the new process so that when it is actually
< 	 * created (by copying) it will look right.
< 	 */
< 	rpp = p;
< 	u.u_procp = rpp;
< 	rip = up;
< 	n = rip->p_size;
< 	a1 = rip->p_addr;
< 	rpp->p_size = n;
< 	/*
< 	 * When the resume is executed for the new process,
< 	 * here's where it will resume.
< 	 */
< 	if (save(u.u_ssav)) {
< 		sureg();
< 		return(1);
< 	}
< 	a2 = malloc(coremap, n);
< 	/*
< 	 * If there is not enough core for the
< 	 * new process, swap out the current process to generate the
< 	 * copy.
< 	 */
< 	if(a2 == NULL) {
< 		rip->p_stat = SIDL;
< 		rpp->p_addr = a1;
< 		xswap(rpp, 0, 0);
< 		rip->p_stat = SRUN;
< 	} else {
< 		/*
< 		 * There is core, so just copy.
< 		 */
< 		rpp->p_addr = a2;
< 		while(n--)
< 			copyseg(a1++, a2++);
< 	}
< 	u.u_procp = rip;
< 	setrq(rpp);
< 	rpp->p_flag |= SSWAP;
< 	return(0);
< }
---
> /* v7 newproc() (alloc proc[] slot, copy parent's image into child) is
>  * gone -- fork(2) routes through arch/arm.c::mt_alloc_slot, which
>  * maintains armproc[NSLOTS] in parallel with proc[NPROC]; the child's
>  * register state is duplicated by the trap frame copy, not by save()/
>  * resume() over the v7 u_ssav. */
545c267,268
< expand(newsize)
---
> void
> expand(int newsize)
547c270
< 	register i, n;
---
> 	register int i, n;
549c272
< 	register a1, a2;
---
> 	register int a1, a2;
566d288
< 		p->p_flag |= SSWAP;
```

### tools/mkfs.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/mkfs.c unix-v7-c99/tools/mkfs.c || true
```

Expect:

```
8a9
> #define	MAXFILEBLK	(LADDR+NINDIR+(NINDIR*NINDIR))
13c14,17
< #include <a.out.h>
---
> #include <stdlib.h>
> #include <unistd.h>
> #include <fcntl.h>
> #include <time.h>
15,20c19,33
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
> /* Pack longs into pure LE 24-bit; matches arch/arm.c::addr(). */
> int ltol3(cp, lp, n) char *cp; long *lp; int n; {
> 	int i; long v;
> 	for(i=0; i<n; i++) {
> 		v = lp[i];
> 		*cp++ = v; *cp++ = v >> 8; *cp++ = v >> 16;
> 	}
> 	return(0);
> }
31c44,47
< union {
---
> /* The v7 K&R-era "anonymous struct as union member" idiom (`struct fblk;`
>  * inside a union) is not strict C99.  Named members + macro aliases keep
>  * the call-site spelling (`fbuf.df_nfree`, `filsys.s_fsize`) unchanged. */
> union fbuf_u {
34,37c50,51
< } fbuf;
< #ifndef STANDALONE
< struct exec head;
< #endif
---
> } fbuf_storage;
> #define fbuf fbuf_storage.fb
39c53
< union {
---
> union filsys_u {
42c56,57
< } filsys;
---
> } filsys_storage;
> #define filsys filsys_storage.fs
49,50c64,78
< long	getnum();
< daddr_t	alloc();
---
> struct	inode;
> long	getnum(void);
> daddr_t	alloc(void);
> void	cfile(struct inode *par);
> void	getstr(void);
> int	gmode(int c, char *s, int m0, int m1, int m2, int m3);
> void	rdfs(daddr_t bno, char *bf);
> void	wtfs(daddr_t bno, char *bf);
> void	bfree(daddr_t bno);
> void	entry(ino_t inum, char *str, int *adbc, char *db, int *aibc, daddr_t *ib);
> void	newblk(int *adbc, char *db, int *aibc, daddr_t *ib);
> int	getch(void);
> void	bflist(void);
> void	iput(struct inode *ip, int *aibc, daddr_t *ib);
> int	badblk(daddr_t bno);
52,53c80,81
< main(argc, argv)
< char *argv[];
---
> int
> main(int argc, char *argv[])
103c131
< 		for(f=0; c=proto[f]; f++) {
---
> 		for(f=0; (c=proto[f]); f++) {
114c142
< 		if(n > 65500/NIPB)
---
> 		if((unsigned long)n > 65500/NIPB)
117c145
< 		printf("isize = %D\n", n*NIPB);
---
> 		printf("isize = %ld\n", n*NIPB);
125c153
< 	 * and read onto block 0
---
> 	 * (skipped: PDP-11 a.out format is not used on this port)
130,148c158,161
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
155d167
< f2:
175c187
< 		printf("%ld/%ld: bad ratio\n", filsys.s_fsize, filsys.s_isize-2);
---
> 		printf("%ld/%d: bad ratio\n", filsys.s_fsize, filsys.s_isize-2);
197,198c209,210
< cfile(par)
< struct inode *par;
---
> void
> cfile(struct inode *par)
203c215
< 	daddr_t ib[NINDIR];
---
> 	daddr_t ib[MAXFILEBLK];
235c247
< 	for(i=0; i<NINDIR; i++)
---
> 	for(i=0; (unsigned)i<MAXFILEBLK; i++)
309,310c321,322
< gmode(c, s, m0, m1, m2, m3)
< char c, *s;
---
> int
> gmode(int c, char *s, int m0, int m1, int m2, int m3)
312a325
> 	int m[4] = {m0, m1, m2, m3};
316c329
< 			return((&m0)[i]);
---
> 			return(m[i]);
323c336
< getnum()
---
> getnum(void)
331c344
< 	for(i=0; c=string[i]; i++) {
---
> 	for(i=0; (c=string[i]) != 0; i++) {
342c355,356
< getstr()
---
> void
> getstr(void)
372,374c386,387
< rdfs(bno, bf)
< daddr_t bno;
< char *bf;
---
> void
> rdfs(daddr_t bno, char *bf)
386,388c399,400
< wtfs(bno, bf)
< daddr_t bno;
< char *bf;
---
> void
> wtfs(daddr_t bno, char *bf)
395c407
< 		printf("write error: %D\n", bno);
---
> 		printf("write error: %ld\n", bno);
401c413
< alloc()
---
> alloc(void)
421,422c433,434
< bfree(bno)
< daddr_t bno;
---
> void
> bfree(daddr_t bno)
437,442c449,450
< entry(inum, str, adbc, db, aibc, ib)
< ino_t inum;
< char *str;
< int *adbc, *aibc;
< char *db;
< daddr_t *ib;
---
> void
> entry(ino_t inum, char *str, int *adbc, char *db, int *aibc, daddr_t *ib)
456c464
< 	if(*adbc >= NDIRECT)
---
> 	if((unsigned)*adbc >= NDIRECT)
460,463c468,469
< newblk(adbc, db, aibc, ib)
< int *adbc, *aibc;
< char *db;
< daddr_t *ib;
---
> void
> newblk(int *adbc, char *db, int *aibc, daddr_t *ib)
467a474,478
> 	if((unsigned)*aibc >= MAXFILEBLK) {
> 		printf("indirect block full\n");
> 		error = 1;
> 		return;
> 	}
475,479d485
< 	if(*aibc >= NINDIR) {
< 		printf("indirect block full\n");
< 		error = 1;
< 		*aibc = 0;
< 	}
482c488,489
< getch()
---
> int
> getch(void)
494c501,502
< bflist()
---
> void
> bflist(void)
525c533
< 	for(i=0; i<NINDIR; i++)
---
> 	for(i=0; (unsigned)i<NINDIR; i++)
535c543
< 		if(f < filsys.s_fsize && f >= filsys.s_isize)
---
> 		if(f < filsys.s_fsize && f >= filsys.s_isize) {
537c545
< 				if(ibc >= NINDIR) {
---
> 				if((unsigned)ibc >= NINDIR) {
545a554
> 		}
550,553c559,560
< iput(ip, aibc, ib)
< struct inode *ip;
< int *aibc;
< daddr_t *ib;
---
> void
> iput(struct inode *ip, int *aibc, daddr_t *ib)
556,557c563,564
< 	daddr_t d;
< 	int i;
---
> 	daddr_t d, single[NINDIR], dbl[NINDIR];
> 	int i, j, k, n;
584,587c591,593
< 		for(i=0; i<*aibc; i++) {
< 			if(i >= LADDR)
< 				break;
< 			ip->i_un.i_addr[i] = ib[i];
---
> 		for(i=0; (unsigned)i<NINDIR; i++) {
> 			single[i] = (daddr_t)0;
> 			dbl[i] = (daddr_t)0;
589c595,602
< 		if(*aibc >= LADDR) {
---
> 		for(i=0; i<*aibc && i<LADDR; i++)
> 			ip->i_un.i_addr[i] = ib[i];
> 		if((unsigned)*aibc > LADDR) {
> 			n = *aibc - LADDR;
> 			if((unsigned)n > NINDIR)
> 				n = (int)NINDIR;
> 			for(i=0; i<n; i++)
> 				single[i] = ib[LADDR+i];
591,593c604,611
< 			for(i=0; i<NINDIR-LADDR; i++) {
< 				ib[i] = ib[i+LADDR];
< 				ib[i+LADDR] = (daddr_t)0;
---
> 			wtfs(ip->i_un.i_addr[LADDR], (char *)single);
> 		}
> 		if((unsigned)*aibc > LADDR+NINDIR) {
> 			n = *aibc - LADDR - NINDIR;
> 			if((unsigned)n > NINDIR*NINDIR) {
> 				printf("indirect block full\n");
> 				error = 1;
> 				n = (int)(NINDIR*NINDIR);
595c613,625
< 			wtfs(ip->i_un.i_addr[LADDR], (char *)ib);
---
> 			ip->i_un.i_addr[LADDR+1] = alloc();
> 			k = LADDR + NINDIR;
> 			for(i=0; (unsigned)i<NINDIR && n>0; i++) {
> 				for(j=0; (unsigned)j<NINDIR; j++)
> 					single[j] = (daddr_t)0;
> 				for(j=0; (unsigned)j<NINDIR && n>0; j++) {
> 					single[j] = ib[k++];
> 					n--;
> 				}
> 				dbl[i] = alloc();
> 				wtfs(dbl[i], (char *)single);
> 			}
> 			wtfs(ip->i_un.i_addr[LADDR+1], (char *)dbl);
596a627
> 		/* fall through */
610,611c641,642
< badblk(bno)
< daddr_t bno;
---
> int
> badblk(daddr_t bno)
613c644
< 
---
> 	(void)bno;
```

### cmd/arcv.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/arcv.c unix-v7-c99/cmd/arcv.c || true
```

Expect:

```
3c3
< */
---
>  */
5a6
> #include <stdio.h>
8c9
< #define	omag	0177555
---
> #define	OMAG	0177555
10,12c11
< struct	ar_hdr nh;
< struct
< {
---
> struct oar_hdr {
14c13
< 	long	odate;
---
> 	char	odate[4];
17,18c16,17
< 	unsigned siz;
< } oh;
---
> 	char	osize[2];
> };
20,24c19,22
< char	*tmp;
< char	*mktemp();
< int	f;
< int	tf;
< union {
---
> static char	*tmp;
> static int	f;
> static int	tf;
> static union {
26c24
< 	int	magic;
---
> 	char	magic[2];
29,30c27,28
< main(argc, argv)
< char *argv[];
---
> static unsigned short
> getshort(char *p)
32c30,32
< 	register i;
---
> 	return ((unsigned short)(unsigned char)p[0]) |
> 	    ((unsigned short)(unsigned char)p[1] << 8);
> }
34,39c34,64
< 	tmp = mktemp("/tmp/arcXXXXX");
< 	for(i=1; i<4; i++)
< 		signal(i, SIG_IGN);
< 	for(i=1; i<argc; i++)
< 		conv(argv[i]);
< 	unlink(tmp);
---
> static void
> putshort(char *p, unsigned short v)
> {
> 	p[0] = v & 0377;
> 	p[1] = (v >> 8) & 0377;
> }
> 
> static void
> putlong(char *p, char *v)
> {
> 	p[0] = v[0];
> 	p[1] = v[1];
> 	p[2] = v[2];
> 	p[3] = v[3];
> }
> 
> static void
> putarhdr(char *p, struct oar_hdr *oh)
> {
> 	int i;
> 
> 	for(i = 0; i < 8; i++)
> 		p[i] = oh->oname[i];
> 	for(; i < 14; i++)
> 		p[i] = 0;
> 	putlong(&p[14], oh->odate);
> 	p[18] = oh->ouid;
> 	p[19] = 1;
> 	putshort(&p[20], 0666);
> 	putshort(&p[22], getshort(oh->osize));
> 	putshort(&p[24], 0);
42,43c67,68
< conv(fil)
< char *fil;
---
> static void
> conv(char *fil)
45c70,72
< 	register unsigned i, n;
---
> 	unsigned int i, n;
> 	struct oar_hdr oh;
> 	char nh[26];
59,61c86,89
< 	b.magic = 0;
< 	read(f, (char *)&b.magic, sizeof(b.magic));
< 	if(b.magic != omag) {
---
> 	b.magic[0] = 0;
> 	b.magic[1] = 0;
> 	read(f, b.magic, sizeof(b.magic));
> 	if(getshort(b.magic) != OMAG) {
67,68c95,96
< 	b.magic = ARMAG;
< 	write(tf, (char *)&b.magic, sizeof(b.magic));
---
> 	putshort(b.magic, ARMAG);
> 	write(tf, b.magic, sizeof(b.magic));
73,81c101,103
< 	for(i=0; i<8; i++)
< 		nh.ar_name[i] = oh.oname[i];
< 	nh.ar_size = oh.siz;
< 	nh.ar_uid = oh.ouid;
< 	nh.ar_gid = 1;
< 	nh.ar_mode = 0666;
< 	nh.ar_date = oh.odate;
< 	n = (oh.siz+1) & ~01;
< 	write(tf, (char *)&nh, sizeof(nh));
---
> 	putarhdr(nh, &oh);
> 	n = (getshort(oh.osize)+1) & ~01;
> 	write(tf, nh, sizeof(nh));
94c116
< 	while((i=read(tf, b.buf, 512)) > 0)
---
> 	while((i = read(tf, b.buf, 512)) > 0)
97a120,134
> }
> 
> int
> main(int argc, char **argv)
> {
> 	int i;
> 	char tbuf[] = "/tmp/arcXXXXX";
> 
> 	tmp = mktemp(tbuf);
> 	for(i = 1; i < 4; i++)
> 		signal(i, SIG_IGN);
> 	for(i = 1; i < argc; i++)
> 		conv(argv[i]);
> 	unlink(tmp);
> 	return 0;
```

### cmd/awk/awk.g.y

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/awk/awk.g.y unix-v7-c99/cmd/awk/awk.g.y || true
```

Expect:

```
166a167,169
> 	| expr	{ PUTS("expr");
> 		$$ = op2(NE, $1, valtonode(lookup("0", symtab), CCON));
> 		}
175d177
< 	|		{ PUTS("null print_list"); $$ = valtonode(lookup("$record", symtab), CFLD); }
```

### cmd/deroff.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/deroff.c unix-v7-c99/cmd/deroff.c || true
```

Expect:

```
51c51
< char *calloc();
---
> char *calloc(unsigned num, unsigned size);
52a53,67
> FILE *opn(register char *p);
> int skeqn(void);
> int eof(void);
> void getfname(void);
> void backsl(void);
> char *copys(register char *s);
> void fatal(char *s, char *p);
> void work(void);
> void regline(int macline);
> void putmac(register char *s);
> void putwords(int macline);
> void comline(void);
> void macro(void);
> void tbl(void);
> void eqn(void);
55,57c70,72
< main(ac, av)
< int ac;
< char **av;
---
> 
> int
> main(int ac, char **av)
62d76
< FILE *opn();
107c121,122
< skeqn()
---
> int
> skeqn(void)
109c124
< while((c = getc(infile)) != rdelim)
---
> while((c = getc(infile)) != rdelim) {
112,113c127,128
< 	else if(c == '"')
< 		while( (c = getc(infile)) != '"')
---
> 	else if(c == '"') {
> 		while( (c = getc(infile)) != '"') {
116c131
< 			else if(c == '\\')
---
> 			else if(c == '\\') {
118a134,137
> 			}
> 		}
> 	}
> }
123,124c142,143
< FILE *opn(p)
< register char *p;
---
> FILE *
> opn(register char *p)
138c157,158
< eof()
---
> int
> eof(void)
158c178,179
< getfname()
---
> void
> getfname(void)
164d184
< char *copys();
192,193c212,213
< fatal(s,p)
< char *s, *p;
---
> void
> fatal(char *s, char *p)
200c220,221
< work()
---
> void
> work(void)
215,216c236,237
< regline(macline)
< int macline;
---
> void
> regline(int macline)
242c263
< if(line[0] != '\0')
---
> if(line[0] != '\0') {
249a271
> }
254,255c276,277
< putmac(s)
< register char *s;
---
> void
> putmac(register char *s)
265c287
< 	if(t>s+2 && chars[ s[0] ]==LETTER && chars[ s[1] ]==LETTER)
---
> 	if(t>s+2 && chars[(unsigned char)s[0]]==LETTER && chars[(unsigned char)s[1]]==LETTER)
276,277c298,299
< putwords(macline)	/* break into words for -w option */
< int macline;
---
> void
> putwords(int macline)	/* break into words for -w option */
286c308
< 	while( chars[*p1] < DIGIT)
---
> 	while( chars[(unsigned char)*p1] < DIGIT)
289c311
< 	for(p = p1 ; (i=chars[*p]) != SPECIAL ; ++p)
---
> 	for(p = p1 ; (i=chars[(unsigned char)*p]) != SPECIAL ; ++p)
293c315
< 	   || (macline && nlet>2 && chars[ p1[0] ]==LETTER && chars[ p1[1] ]==LETTER) )
---
> 	   || (macline && nlet>2 && chars[(unsigned char)p1[0]]==LETTER && chars[(unsigned char)p1[1]]==LETTER) )
308c330,331
< comline()
---
> void
> comline(void)
363c386,387
< macro()
---
> void
> macro(void)
367c391
< 	while(C!='.' || C!='.' || C=='.');	/* look for  .. */
---
> 	while(C!='.' || C!='.' || C=='.');	look for  .. */
375c399,400
< tbl()
---
> void
> tbl(void)
382c407,408
< eqn()
---
> void
> eqn(void)
425c451,452
< backsl()	/* skip over a complete backslash construction */
---
> void
> backsl(void)	/* skip over a complete backslash construction */
449c476
< 
---
> 		/* fallthrough */
483,484c510,511
< char *copys(s)
< register char *s;
---
> char *
> copys(register char *s)
491c518
< while( *t++ = *s++ )
---
> while( (*t++ = *s++) )
```

### cmd/egrep.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/egrep.y unix-v7-c99/cmd/egrep.c || true
```

Expect:

```
7a8,11
>  *
>  * This is a C99 translation of the V7 egrep.y.  The original yacc grammar
>  * is represented by the small recursive-descent parser below; the syntax
>  * tree, follow-set, DFA construction, and executor are kept close to V7.
9,13d12
< %token CHAR DOT CCL NCCL OR CAT STAR PLUS QUEST
< %left OR
< %left CHAR DOT CCL NCCL '('
< %left CAT
< %left STAR PLUS QUEST
15d13
< %{
22a21,31
> 
> #define CHAR 128
> #define DOT 129
> #define CCL 130
> #define NCCL 131
> #define OR 132
> #define CAT 133
> #define STAR 134
> #define PLUS 135
> #define QUEST 136
> 
26c35
< int line 1;
---
> int line = 1;
35c44
< int nxtchar 0;
---
> int nxtchar = 0;
58,59c67
< int	fname;
< %}
---
> char	*fname;
61,103c69,70
< %%
< s:	t
< 		={ unary(FINAL, $1);
< 		  line--;
< 		}
< 	;
< t:	b r
< 		={ $$ = node(CAT, $1, $2); }
< 	| OR b r OR
< 		={ $$ = node(CAT, $2, $3); }
< 	| OR b r
< 		={ $$ = node(CAT, $2, $3); }
< 	| b r OR
< 		={ $$ = node(CAT, $1, $2); }
< 	;
< b:
< 		={ $$ = enter(DOT);
< 		   $$ = unary(STAR, $$); }
< 	;
< r:	CHAR
< 		={ $$ = enter($1); }
< 	| DOT
< 		={ $$ = enter(DOT); }
< 	| CCL
< 		={ $$ = cclenter(CCL); }
< 	| NCCL
< 		={ $$ = cclenter(NCCL); }
< 	;
< 
< r:	r OR r
< 		={ $$ = node(OR, $1, $3); }
< 	| r r %prec CAT
< 		={ $$ = node(CAT, $1, $2); }
< 	| r STAR
< 		={ $$ = unary(STAR, $1); }
< 	| r PLUS
< 		={ $$ = unary(PLUS, $1); }
< 	| r QUEST
< 		={ $$ = unary(QUEST, $1); }
< 	| '(' r ')'
< 		={ $$ = $2; }
< 	| error 
< 	;
---
> int looktok;
> int yylval;
105,106c72,99
< %%
< yyerror(s) {
---
> void yyerror(char *s);
> int yylex(void);
> int nextch(void);
> void synerror(void);
> int enter(int x);
> int cclenter(int x);
> int node(int x, int l, int r);
> int unary(int x, int d);
> void overflo(void);
> void cfoll(int v);
> void cgotofn(void);
> int cstate(int v);
> int member(int symb, int set, int torf);
> int notin(int n);
> void add(int *array, int n);
> void follow(int v);
> int yyparse(void);
> void nexttok(void);
> int parse_alt(void);
> int parse_cat(void);
> int parse_post(void);
> int parse_atom(void);
> int atom_start(int tok);
> void execute(char *file);
> 
> void
> yyerror(char *s)
> {
111,112c104,106
< yylex() {
< 	extern int yylval;
---
> int
> yylex(void)
> {
114,146c108,150
< 	register char c, d;
< 	switch(c = nextch()) {
< 		case '$':
< 		case '^': c = '\n';
< 			goto defchar;
< 		case '|': return (OR);
< 		case '*': return (STAR);
< 		case '+': return (PLUS);
< 		case '?': return (QUEST);
< 		case '(': return (c);
< 		case ')': return (c);
< 		case '.': return (DOT);
< 		case '\0': return (0);
< 		case '\n': return (OR);
< 		case '[': 
< 			x = CCL;
< 			cclcnt = 0;
< 			count = nxtchar++;
< 			if ((c = nextch()) == '^') {
< 				x = NCCL;
< 				c = nextch();
< 			}
< 			do {
< 				if (c == '\0') synerror();
< 				if (c == '-' && cclcnt > 0 && chars[nxtchar-1] != 0) {
< 					if ((d = nextch()) != 0) {
< 						c = chars[nxtchar-1];
< 						while (c < d) {
< 							if (nxtchar >= MAXLIN) overflo();
< 							chars[nxtchar++] = ++c;
< 							cclcnt++;
< 						}
< 						continue;
---
> 	int c, d;
> 
> 	switch (c = nextch()) {
> 	case '$':
> 	case '^':
> 		c = '\n';
> 		goto defchar;
> 	case '|':
> 		return (OR);
> 	case '*':
> 		return (STAR);
> 	case '+':
> 		return (PLUS);
> 	case '?':
> 		return (QUEST);
> 	case '(':
> 	case ')':
> 		return (c);
> 	case '.':
> 		return (DOT);
> 	case '\0':
> 		return (0);
> 	case '\n':
> 		return (OR);
> 	case '[':
> 		x = CCL;
> 		cclcnt = 0;
> 		count = nxtchar++;
> 		if ((c = nextch()) == '^') {
> 			x = NCCL;
> 			c = nextch();
> 		}
> 		do {
> 			if (c == '\0')
> 				synerror();
> 			if (c == '-' && cclcnt > 0 && chars[nxtchar-1] != 0) {
> 				if ((d = nextch()) != 0) {
> 					c = chars[nxtchar-1];
> 					while (c < d) {
> 						if (nxtchar >= MAXLIN)
> 							overflo();
> 						chars[nxtchar++] = ++c;
> 						cclcnt++;
147a152
> 					continue;
149,158c154,169
< 				if (nxtchar >= MAXLIN) overflo();
< 				chars[nxtchar++] = c;
< 				cclcnt++;
< 			} while ((c = nextch()) != ']');
< 			chars[count] = cclcnt;
< 			return (x);
< 		case '\\':
< 			if ((c = nextch()) == '\0') synerror();
< 		defchar:
< 		default: yylval = c; return (CHAR);
---
> 			}
> 			if (nxtchar >= MAXLIN)
> 				overflo();
> 			chars[nxtchar++] = c;
> 			cclcnt++;
> 		} while ((c = nextch()) != ']');
> 		chars[count] = cclcnt;
> 		return (x);
> 	case '\\':
> 		if ((c = nextch()) == '\0')
> 			synerror();
> 		goto defchar;
> 	default:
> 	defchar:
> 		yylval = c;
> 		return (CHAR);
161,162c172,177
< nextch() {
< 	register char c;
---
> 
> int
> nextch(void)
> {
> 	int c;
> 
164c179,181
< 		if ((c = getc(stdin)) == EOF) return(0);
---
> 		if ((c = getc(stdin)) == EOF)
> 			return (0);
> 		return (c);
166,167c183
< 	else c = *input++;
< 	return(c);
---
> 	return (*input++);
170c186,188
< synerror() {
---
> void
> synerror(void)
> {
175,176c193,197
< enter(x) int x; {
< 	if(line >= MAXLIN) overflo();
---
> int
> enter(int x)
> {
> 	if (line >= MAXLIN)
> 		overflo();
180c201
< 	return(line++);
---
> 	return (line++);
183,184c204,208
< cclenter(x) int x; {
< 	register linno;
---
> int
> cclenter(int x)
> {
> 	int linno;
> 
190,191c214,218
< node(x, l, r) {
< 	if(line >= MAXLIN) overflo();
---
> int
> node(int x, int l, int r)
> {
> 	if (line >= MAXLIN)
> 		overflo();
197c224
< 	return(line++);
---
> 	return (line++);
200,201c227,231
< unary(x, d) {
< 	if(line >= MAXLIN) overflo();
---
> int
> unary(int x, int d)
> {
> 	if (line >= MAXLIN)
> 		overflo();
206c236
< 	return(line++);
---
> 	return (line++);
208c238,241
< overflo() {
---
> 
> void
> overflo(void)
> {
213,214c246,370
< cfoll(v) {
< 	register i;
---
> void
> nexttok(void)
> {
> 	looktok = yylex();
> }
> 
> int
> atom_start(int tok)
> {
> 	return (tok == CHAR || tok == DOT || tok == CCL || tok == NCCL ||
> 	    tok == '(');
> }
> 
> int
> yyparse(void)
> {
> 	int b, r;
> 
> 	nexttok();
> 	if (looktok == OR)
> 		nexttok();
> 	b = enter(DOT);
> 	b = unary(STAR, b);
> 	r = parse_alt();
> 	if (looktok == OR)
> 		nexttok();
> 	if (looktok != 0)
> 		synerror();
> 	unary(FINAL, node(CAT, b, r));
> 	line--;
> 	return (0);
> }
> 
> int
> parse_alt(void)
> {
> 	int l, r;
> 
> 	l = parse_cat();
> 	while (looktok == OR) {
> 		nexttok();
> 		if (looktok == 0 || looktok == ')')
> 			break;
> 		r = parse_cat();
> 		l = node(OR, l, r);
> 	}
> 	return (l);
> }
> 
> int
> parse_cat(void)
> {
> 	int l, r;
> 
> 	if (!atom_start(looktok))
> 		synerror();
> 	l = parse_post();
> 	while (atom_start(looktok)) {
> 		r = parse_post();
> 		l = node(CAT, l, r);
> 	}
> 	return (l);
> }
> 
> int
> parse_post(void)
> {
> 	int a;
> 
> 	a = parse_atom();
> 	for (;;) {
> 		if (looktok == STAR) {
> 			nexttok();
> 			a = unary(STAR, a);
> 		} else if (looktok == PLUS) {
> 			nexttok();
> 			a = unary(PLUS, a);
> 		} else if (looktok == QUEST) {
> 			nexttok();
> 			a = unary(QUEST, a);
> 		} else
> 			return (a);
> 	}
> }
> 
> int
> parse_atom(void)
> {
> 	int a;
> 
> 	switch (looktok) {
> 	case CHAR:
> 		a = enter(yylval);
> 		nexttok();
> 		return (a);
> 	case DOT:
> 		a = enter(DOT);
> 		nexttok();
> 		return (a);
> 	case CCL:
> 		a = cclenter(CCL);
> 		nexttok();
> 		return (a);
> 	case NCCL:
> 		a = cclenter(NCCL);
> 		nexttok();
> 		return (a);
> 	case '(':
> 		nexttok();
> 		a = parse_alt();
> 		if (looktok != ')')
> 			synerror();
> 		nexttok();
> 		return (a);
> 	default:
> 		synerror();
> 		return (0);
> 	}
> }
> 
> void
> cfoll(int v)
> {
> 	int i;
> 
217c373,374
< 		for (i=1; i<=line; i++) tmpstat[i] = 0;
---
> 		for (i = 1; i <= line; i++)
> 			tmpstat[i] = 0;
220,221c377,378
< 	}
< 	else if (right[v] == 0) cfoll(left[v]);
---
> 	} else if (right[v] == 0)
> 		cfoll(left[v]);
227,228c384,388
< cgotofn() {
< 	register c, i, k;
---
> 
> void
> cgotofn(void)
> {
> 	int c, i, k;
233a394
> 
235,236c396,398
< 	for (n=3; n<=line; n++) tmpstat[n] = 0;
< 	if (cstate(line-1)==0) {
---
> 	for (n = 3; n <= line; n++)
> 		tmpstat[n] = 0;
> 	if (cstate(line-1) == 0) {
241,242c403,405
< 	for (n=3; n<=line; n++) initstat[n] = tmpstat[n];
< 	count--;		/*leave out position 1 */
---
> 	for (n = 3; n <= line; n++)
> 		initstat[n] = tmpstat[n];
> 	count--;
247,249c410,414
< 	for (s=0; s<=n; s++)  {
< 		if (out[s] == 1) continue;
< 		for (i=0; i<NCHARS; i++) symbol[i] = 0;
---
> 	for (s = 0; s <= n; s++)  {
> 		if (out[s] == 1)
> 			continue;
> 		for (i = 0; i < NCHARS; i++)
> 			symbol[i] = 0;
252c417,418
< 		for (i=3; i<=line; i++) tmpstat[i] = initstat[i];
---
> 		for (i = 3; i <= line; i++)
> 			tmpstat[i] = initstat[i];
254c420
< 		for (i=0; i<num; i++) {
---
> 		for (i = 0; i < num; i++) {
257c423,424
< 				if (c < NCHARS) symbol[c] = 1;
---
> 				if (c < NCHARS)
> 					symbol[c] = 1;
259,262c426,429
< 					for (k=0; k<NCHARS; k++)
< 						if (k!='\n') symbol[k] = 1;
< 				}
< 				else if (c == CCL) {
---
> 					for (k = 0; k < NCHARS; k++)
> 						if (k != '\n')
> 							symbol[k] = 1;
> 				} else if (c == CCL) {
265,267c432,434
< 					for (k=0; k<nc; k++) symbol[chars[pc++]] = 1;
< 				}
< 				else if (c == NCCL) {
---
> 					for (k = 0; k < nc; k++)
> 						symbol[(int)chars[pc++]] = 1;
> 				} else if (c == NCCL) {
272,274c439,444
< 							if (j==chars[pc++]) goto cont;
< 						if (j!='\n') symbol[j] = 1;
< 						cont:;
---
> 							if (j == chars[pc++])
> 								goto cont;
> 						if (j != '\n')
> 							symbol[j] = 1;
> cont:
> 						;
276,277c446,447
< 				}
< 				else printf("something's funny\n");
---
> 				} else
> 					printf("something's funny\n");
281,282c451,452
< 		for (c=0; c<NCHARS; c++) {
< 			if (symbol[c] == 1) { /* nextstate(s,c) */
---
> 		for (c = 0; c < NCHARS; c++) {
> 			if (symbol[c] == 1) {
284c454,455
< 				for (i=3; i <= line; i++) tmpstat[i] = initstat[i];
---
> 				for (i = 3; i <= line; i++)
> 					tmpstat[i] = initstat[i];
286c457
< 				for (i=0; i<num; i++) {
---
> 				for (i = 0; i < num; i++) {
290,293c461,464
< 							(k == c)
< 							| (k == DOT)
< 							| (k == CCL && member(c, right[curpos], 1))
< 							| (k == NCCL && member(c, right[curpos], 0))
---
> 						    (k == c)
> 						    | (k == DOT)
> 						    | (k == CCL && member(c, right[curpos], 1))
> 						    | (k == NCCL && member(c, right[curpos], 0))
297c468
< 							for (k=0; k<number; k++) {
---
> 							for (k = 0; k < number; k++) {
306c477
< 				} /* end nextstate */
---
> 				}
308c479,480
< 					if (n >= NSTATES) overflo();
---
> 					if (n >= NSTATES)
> 						overflo();
310c482,483
< 					if (tmpstat[line] == 1) out[n] = 1;
---
> 					if (tmpstat[line] == 1)
> 						out[n] = 1;
312,313c485
< 				}
< 				else {
---
> 				} else
315d486
< 				}
321,322c492,496
< cstate(v) {
< 	register b;
---
> int
> cstate(int v)
> {
> 	int b;
> 
328,339c502,515
< 		return(1);
< 	}
< 	else if (right[v] == 0) {
< 		if (cstate(left[v]) == 0) return (0);
< 		else if (name[v] == PLUS) return (1);
< 		else return (0);
< 	}
< 	else if (name[v] == CAT) {
< 		if (cstate(left[v]) == 0 && cstate(right[v]) == 0) return (0);
< 		else return (1);
< 	}
< 	else { /* name[v] == OR */
---
> 		return (1);
> 	} else if (right[v] == 0) {
> 		if (cstate(left[v]) == 0)
> 			return (0);
> 		else if (name[v] == PLUS)
> 			return (1);
> 		else
> 			return (0);
> 	} else if (name[v] == CAT) {
> 		if (cstate(left[v]) == 0 && cstate(right[v]) == 0)
> 			return (0);
> 		else
> 			return (1);
> 	} else {
341,342c517,520
< 		if (cstate(left[v]) == 0 || b == 0) return (0);
< 		else return (1);
---
> 		if (cstate(left[v]) == 0 || b == 0)
> 			return (0);
> 		else
> 			return (1);
345a524,527
> int
> member(int symb, int set, int torf)
> {
> 	int i, num, pos;
347,348d528
< member(symb, set, torf) {
< 	register i, num, pos;
351,352c531,533
< 	for (i=0; i<num; i++)
< 		if (symb == chars[pos++]) return (torf);
---
> 	for (i = 0; i < num; i++)
> 		if (symb == chars[pos++])
> 			return (torf);
356,358c537,542
< notin(n) {
< 	register i, j, pos;
< 	for (i=0; i<=n; i++) {
---
> int
> notin(int n)
> {
> 	int i, j, pos;
> 
> 	for (i = 0; i <= n; i++) {
361,362c545,547
< 			for (j=0; j < count; j++)
< 				if (tmpstat[positions[pos++]] != 1) goto nxt;
---
> 			for (j = 0; j < count; j++)
> 				if (tmpstat[positions[pos++]] != 1)
> 					goto nxt;
366c551,552
< 		nxt: ;
---
> nxt:
> 		;
371,373c557,563
< add(array, n) int *array; {
< 	register i;
< 	if (nxtpos + count > MAXPOS) overflo();
---
> void
> add(int *array, int n)
> {
> 	int i;
> 
> 	if (nxtpos + count > MAXPOS)
> 		overflo();
376c566
< 	for (i=3; i <= line; i++) {
---
> 	for (i = 3; i <= line; i++) {
383c573,575
< follow(v) int v; {
---
> void
> follow(int v)
> {
385c577,579
< 	if (v == line) return;
---
> 
> 	if (v == line)
> 		return;
387,389c581,593
< 	switch(name[p]) {
< 		case STAR:
< 		case PLUS:	cstate(v);
---
> 	switch (name[p]) {
> 	case STAR:
> 	case PLUS:
> 		cstate(v);
> 		follow(p);
> 		return;
> 	case OR:
> 	case QUEST:
> 		follow(p);
> 		return;
> 	case CAT:
> 		if (v == left[p]) {
> 			if (cstate(right[p]) == 0) {
392,409c596,605
< 
< 		case OR:
< 		case QUEST:	follow(p);
< 				return;
< 
< 		case CAT:	if (v == left[p]) {
< 					if (cstate(right[p]) == 0) {
< 						follow(p);
< 						return;
< 					}
< 				}
< 				else follow(p);
< 				return;
< 		case FINAL:	if (tmpstat[line] != 1) {
< 					tmpstat[line] = 1;
< 					count++;
< 				}
< 				return;
---
> 			}
> 		} else
> 			follow(p);
> 		return;
> 	case FINAL:
> 		if (tmpstat[line] != 1) {
> 			tmpstat[line] = 1;
> 			count++;
> 		}
> 		return;
413,415c609,610
< 
< main(argc, argv)
< char **argv;
---
> int
> main(int argc, char **argv)
417c612
< 	while (--argc > 0 && (++argv)[0][0]=='-')
---
> 	while (--argc > 0 && (++argv)[0][0] == '-')
419d613
< 
423d616
< 
427d619
< 
431d622
< 
435d625
< 
440d629
< 
444d632
< 
448d635
< 
452d638
< 
456d641
< 
462c647
< 	if (argc<=0)
---
> 	if (argc <= 0)
465c650,651
< 		if (freopen(fname = *argv, "r", stdin) == NULL) {
---
> 		fname = *argv;
> 		if (freopen(fname, "r", stdin) == NULL) {
469,470c655,656
< 	}
< 	else input = *argv;
---
> 	} else
> 		input = *argv;
479,480c665,667
< 	if (argc<=0) {
< 		if (lflag) exit(1);
---
> 	if (argc <= 0) {
> 		if (lflag)
> 			exit(1);
482,486c669,673
< 	}
< 	else while (--argc >= 0) {
< 		execute(*argv);
< 		argv++;
< 	}
---
> 	} else
> 		while (--argc >= 0) {
> 			execute(*argv);
> 			argv++;
> 		}
490,491c677,678
< execute(file)
< char *file;
---
> void
> execute(char *file)
493,495c680,682
< 	register char *p;
< 	register cstat;
< 	register ccount;
---
> 	char *p;
> 	int cstat;
> 	int ccount;
498a686
> 
504,505c692,693
< 	}
< 	else f = 0;
---
> 	} else
> 		f = 0;
511c699,700
< 	if ((ccount = read(f,p,512))<=0) goto done;
---
> 	if ((ccount = read(f, p, 512)) <= 0)
> 		goto done;
514c703,704
< 	if (out[cstat]) goto found;
---
> 	if (out[cstat])
> 		goto found;
516c706
< 		cstat = gotofn[cstat][*p&0377];	/* all input chars made positive */
---
> 		cstat = gotofn[cstat][*p & 0177];
518c708,709
< 		found:	for(;;) {
---
> found:
> 			for (;;) {
521,522c712,715
< 				succeed:	nsucc = 1;
< 						if (cflag) tln++;
---
> succeed:
> 						nsucc = 1;
> 						if (cflag)
> 							tln++;
524c717
< 							;	/* ugh */
---
> 							;
529,533c722,728
< 						}
< 						else {
< 							if (nfile > 1 && hflag) printf("%s:", file);
< 							if (bflag) printf("%ld:", (blkno-ccount-1)/512);
< 							if (nflag) printf("%ld:", lnum);
---
> 						} else {
> 							if (nfile > 1 && hflag)
> 								printf("%s:", file);
> 							if (bflag)
> 								printf("%ld:", (blkno-ccount-1)/512);
> 							if (nflag)
> 								printf("%ld:", lnum);
535c730,731
< 								while (nlp < &buf[1024]) putchar(*nlp++);
---
> 								while (nlp < &buf[1024])
> 									putchar(*nlp++);
538c734,735
< 							while (nlp < p) putchar(*nlp++);
---
> 							while (nlp < p)
> 								putchar(*nlp++);
543c740,741
< 					if ((out[(cstat=istat)]) == 0) goto brk2;
---
> 					if ((out[(cstat = istat)]) == 0)
> 						goto brk2;
545c743
< 				cfound:
---
> cfound:
548,550c746,748
< 						if ((ccount = read(f, p, 512)) <= 0) goto done;
< 					}
< 					else if (p == &buf[1024]) {
---
> 						if ((ccount = read(f, p, 512)) <= 0)
> 							goto done;
> 					} else if (p == &buf[1024]) {
552,555c750,754
< 						if ((ccount = read(f, p, 512)) <= 0) goto done;
< 					}
< 					else {
< 						if ((ccount = read(f, p, &buf[1024]-p)) <= 0) goto done;
---
> 						if ((ccount = read(f, p, 512)) <= 0)
> 							goto done;
> 					} else {
> 						if ((ccount = read(f, p, &buf[1024]-p)) <= 0)
> 							goto done;
557c756
< 					if(nlp>p && nlp<=p+ccount)
---
> 					if (nlp > p && nlp <= p+ccount)
564c763,764
< 			if (vflag) goto succeed;
---
> 			if (vflag)
> 				goto succeed;
568c768,769
< 				if (out[(cstat=istat)]) goto cfound;
---
> 				if (out[(cstat = istat)])
> 					goto cfound;
571c772
< 		brk2:
---
> brk2:
574,576c775,777
< 				if ((ccount = read(f, p, 512)) <= 0) break;
< 			}
< 			else if (p == &buf[1024]) {
---
> 				if ((ccount = read(f, p, 512)) <= 0)
> 					break;
> 			} else if (p == &buf[1024]) {
578,581c779,783
< 				if ((ccount = read(f, p, 512)) <= 0) break;
< 			}
< 			else {
< 				if ((ccount = read(f, p, &buf[1024] - p)) <= 0) break;
---
> 				if ((ccount = read(f, p, 512)) <= 0)
> 					break;
> 			} else {
> 				if ((ccount = read(f, p, &buf[1024] - p)) <= 0)
> 					break;
583c785
< 			if(nlp>p && nlp<=p+ccount)
---
> 			if (nlp > p && nlp <= p+ccount)
588c790,791
< done:	close(f);
---
> done:
> 	close(f);
```

### cmd/expr.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/expr.y unix-v7-c99/cmd/expr.c || true
```

Expect:

```
1c1
< /* Yacc productions for "expr" command: */
---
> #include <stdio.h>
3,4c3,4
< %token OR AND ADD SUBT MULT DIV REM EQ GT GEQ LT LEQ NEQ
< %token A_STRING SUBSTR LENGTH INDEX NOARG MATCH
---
> #define ESIZE	512
> #define NBRA	9
6,24c6,27
< /* operators listed below in increasing precedence: */
< %left OR
< %left AND
< %left EQ LT GT GEQ LEQ NEQ
< %left ADD SUBT
< %left MULT DIV REM
< %left MCH
< %left MATCH
< %left SUBSTR
< %left LENGTH INDEX
< %%
< 
< /* a single `expression' is evaluated and printed: */
< 
< expression:	expr NOARG = {
< 			printf("%s\n", $1);
< 			exit((!strcmp($1,"0")||!strcmp($1,"\0"))? 1: 0);
< 			}
< 	;
---
> enum {
> 	TOK_END = 0,
> 	TOK_STRING = 256,
> 	TOK_OR,
> 	TOK_AND,
> 	TOK_ADD,
> 	TOK_SUB,
> 	TOK_MUL,
> 	TOK_DIV,
> 	TOK_REM,
> 	TOK_COLON,
> 	TOK_EQ,
> 	TOK_GT,
> 	TOK_GEQ,
> 	TOK_LT,
> 	TOK_LEQ,
> 	TOK_NEQ,
> 	TOK_MATCH,
> 	TOK_SUBSTR,
> 	TOK_LENGTH,
> 	TOK_INDEX
> };
25a29,32
> struct token {
> 	int type;
> 	char *text;
> };
27,91c34,249
< expr:	'(' expr ')' = { $$ = $2; }
< 	| expr OR expr   = { $$ = conj(OR, $1, $3); }
< 	| expr AND expr   = { $$ = conj(AND, $1, $3); }
< 	| expr EQ expr   = { $$ = rel(EQ, $1, $3); }
< 	| expr GT expr   = { $$ = rel(GT, $1, $3); }
< 	| expr GEQ expr   = { $$ = rel(GEQ, $1, $3); }
< 	| expr LT expr   = { $$ = rel(LT, $1, $3); }
< 	| expr LEQ expr   = { $$ = rel(LEQ, $1, $3); }
< 	| expr NEQ expr   = { $$ = rel(NEQ, $1, $3); }
< 	| expr ADD expr   = { $$ = arith(ADD, $1, $3); }
< 	| expr SUBT expr   = { $$ = arith(SUBT, $1, $3); }
< 	| expr MULT expr   = { $$ = arith(MULT, $1, $3); }
< 	| expr DIV expr   = { $$ = arith(DIV, $1, $3); }
< 	| expr REM expr   = { $$ = arith(REM, $1, $3); }
< 	| expr MCH expr	 = { $$ = match($1, $3); }
< 	| MATCH expr expr = { $$ = match($2, $3); }
< 	| SUBSTR expr expr expr = { $$ = substr($2, $3, $4); }
< 	| LENGTH expr       = { $$ = length($2); }
< 	| INDEX expr expr = { $$ = index($2, $3); }
< 	| A_STRING
< 	;
< %%
< /*	expression command */
< #include <stdio.h>
< #define ESIZE	256
< #define error(c)	errxx(c)
< #define EQL(x,y) !strcmp(x,y)
< long atol();
< char	**Av;
< int	Ac;
< int	Argi;
< 
< char Mstring[1][128];
< char *malloc();
< extern int nbra;
< 
< main(argc, argv) char **argv; {
< 	Ac = argc;
< 	Argi = 1;
< 	Av = argv;
< 	yyparse();
< }
< 
< char *operators[] = { "|", "&", "+", "-", "*", "/", "%", ":",
< 	"=", "==", "<", "<=", ">", ">=", "!=",
< 	"match", "substr", "length", "index", "\0" };
< int op[] = { OR, AND, ADD,  SUBT, MULT, DIV, REM, MCH,
< 	EQ, EQ, LT, LEQ, GT, GEQ, NEQ,
< 	MATCH, SUBSTR, LENGTH, INDEX };
< yylex() {
< 	register char *p;
< 	register i;
< 
< 	if(Argi >= Ac) return NOARG;
< 
< 	p = Av[Argi++];
< 
< 	if(*p == '(' || *p == ')')
< 		return (int)*p;
< 	for(i = 0; *operator[i]; ++i)
< 		if(EQL(operator[i], p))
< 			return op[i];
< 
< 	yylval = p;
< 	return A_STRING;
---
> static int ac;
> static char **av;
> static int pos;
> static struct token tok;
> static char match_string[128];
> static int nbra;
> 
> static char *parse_or(void);
> static char *parse_and(void);
> static char *parse_rel(void);
> static char *parse_add(void);
> static char *parse_mul(void);
> static char *parse_colon(void);
> static char *parse_unary(void);
> static void next(void);
> static void syntax(void);
> static char *conj(int op, char *r1, char *r2);
> static char *relop(int op, char *r1, char *r2);
> static char *arith(int op, char *r1, char *r2);
> static char *match_op(char *s, char *p);
> static char *substr_op(char *v, char *s, char *w);
> static char *length_op(char *s);
> static char *index_op(char *s, char *t);
> static int isnum(char *s, int sign);
> static char *numstr(long n);
> static char *xalloc(unsigned n);
> static int ematch(char *s, char *p);
> static void re_error(int c);
> 
> int
> main(int argc, char *argv[])
> {
> 	char *r;
> 
> 	ac = argc;
> 	av = argv;
> 	pos = 1;
> 	next();
> 	if (tok.type == TOK_END)
> 		syntax();
> 	r = parse_or();
> 	if (tok.type != TOK_END)
> 		syntax();
> 	printf("%s\n", r);
> 	exit((strcmp(r, "0") == 0 || strcmp(r, "") == 0) ? 1 : 0);
> 	return(0);
> }
> 
> static void
> next(void)
> {
> 	char *p;
> 
> 	if (pos >= ac) {
> 		tok.type = TOK_END;
> 		tok.text = "";
> 		return;
> 	}
> 	p = av[pos++];
> 	tok.text = p;
> 	if (strcmp(p, "(") == 0 || strcmp(p, ")") == 0) {
> 		tok.type = *p;
> 		return;
> 	}
> 	if (strcmp(p, "|") == 0) tok.type = TOK_OR;
> 	else if (strcmp(p, "&") == 0) tok.type = TOK_AND;
> 	else if (strcmp(p, "+") == 0) tok.type = TOK_ADD;
> 	else if (strcmp(p, "-") == 0) tok.type = TOK_SUB;
> 	else if (strcmp(p, "*") == 0) tok.type = TOK_MUL;
> 	else if (strcmp(p, "/") == 0) tok.type = TOK_DIV;
> 	else if (strcmp(p, "%") == 0) tok.type = TOK_REM;
> 	else if (strcmp(p, ":") == 0) tok.type = TOK_COLON;
> 	else if (strcmp(p, "=") == 0 || strcmp(p, "==") == 0) tok.type = TOK_EQ;
> 	else if (strcmp(p, ">") == 0) tok.type = TOK_GT;
> 	else if (strcmp(p, ">=") == 0) tok.type = TOK_GEQ;
> 	else if (strcmp(p, "<") == 0) tok.type = TOK_LT;
> 	else if (strcmp(p, "<=") == 0) tok.type = TOK_LEQ;
> 	else if (strcmp(p, "!=") == 0) tok.type = TOK_NEQ;
> 	else if (strcmp(p, "match") == 0) tok.type = TOK_MATCH;
> 	else if (strcmp(p, "substr") == 0) tok.type = TOK_SUBSTR;
> 	else if (strcmp(p, "length") == 0) tok.type = TOK_LENGTH;
> 	else if (strcmp(p, "index") == 0) tok.type = TOK_INDEX;
> 	else tok.type = TOK_STRING;
> }
> 
> static void
> syntax(void)
> {
> 	fprintf(stderr, "syntax error\n");
> 	exit(2);
> }
> 
> static char *
> parse_or(void)
> {
> 	char *r;
> 
> 	r = parse_and();
> 	while (tok.type == TOK_OR) {
> 		next();
> 		r = conj(TOK_OR, r, parse_and());
> 	}
> 	return(r);
> }
> 
> static char *
> parse_and(void)
> {
> 	char *r;
> 
> 	r = parse_rel();
> 	while (tok.type == TOK_AND) {
> 		next();
> 		r = conj(TOK_AND, r, parse_rel());
> 	}
> 	return(r);
> }
> 
> static char *
> parse_rel(void)
> {
> 	char *r;
> 	int op;
> 
> 	r = parse_add();
> 	while (tok.type == TOK_EQ || tok.type == TOK_GT || tok.type == TOK_GEQ ||
> 	    tok.type == TOK_LT || tok.type == TOK_LEQ || tok.type == TOK_NEQ) {
> 		op = tok.type;
> 		next();
> 		r = relop(op, r, parse_add());
> 	}
> 	return(r);
> }
> 
> static char *
> parse_add(void)
> {
> 	char *r;
> 	int op;
> 
> 	r = parse_mul();
> 	while (tok.type == TOK_ADD || tok.type == TOK_SUB) {
> 		op = tok.type;
> 		next();
> 		r = arith(op, r, parse_mul());
> 	}
> 	return(r);
> }
> 
> static char *
> parse_mul(void)
> {
> 	char *r;
> 	int op;
> 
> 	r = parse_colon();
> 	while (tok.type == TOK_MUL || tok.type == TOK_DIV || tok.type == TOK_REM) {
> 		op = tok.type;
> 		next();
> 		r = arith(op, r, parse_colon());
> 	}
> 	return(r);
> }
> 
> static char *
> parse_colon(void)
> {
> 	char *r;
> 
> 	r = parse_unary();
> 	while (tok.type == TOK_COLON) {
> 		next();
> 		r = match_op(r, parse_unary());
> 	}
> 	return(r);
> }
> 
> static char *
> parse_unary(void)
> {
> 	char *r, *s, *w;
> 
> 	if (tok.type == '(') {
> 		next();
> 		r = parse_or();
> 		if (tok.type != ')')
> 			syntax();
> 		next();
> 		return(r);
> 	}
> 	if (tok.type == TOK_MATCH) {
> 		next();
> 		r = parse_unary();
> 		return(match_op(r, parse_unary()));
> 	}
> 	if (tok.type == TOK_SUBSTR) {
> 		next();
> 		r = parse_unary();
> 		s = parse_unary();
> 		w = parse_unary();
> 		return(substr_op(r, s, w));
> 	}
> 	if (tok.type == TOK_LENGTH) {
> 		next();
> 		return(length_op(parse_unary()));
> 	}
> 	if (tok.type == TOK_INDEX) {
> 		next();
> 		r = parse_unary();
> 		return(index_op(r, parse_unary()));
> 	}
> 	if (tok.type != TOK_STRING)
> 		syntax();
> 	r = tok.text;
> 	next();
> 	return(r);
94,95c252,256
< char *rel(op, r1, r2) register char *r1, *r2; {
< 	register i;
---
> static int
> false_value(char *s)
> {
> 	return(strcmp(s, "0") == 0 || strcmp(s, "") == 0);
> }
97,98c258,278
< 	if(ematch(r1, "-*[0-9]*$") && ematch(r2, "[0-9]*$"))
< 		i = atol(r1) - atol(r2);
---
> static char *
> conj(int op, char *r1, char *r2)
> {
> 	if (op == TOK_OR) {
> 		if (false_value(r1))
> 			return(false_value(r2) ? "0" : r2);
> 		return(r1);
> 	}
> 	if (false_value(r1) || false_value(r2))
> 		return("0");
> 	return(r1);
> }
> 
> static char *
> relop(int op, char *r1, char *r2)
> {
> 	long d;
> 	int i;
> 
> 	if (isnum(r1, 1) && isnum(r2, 0))
> 		d = atol(r1) - atol(r2);
100,107c280,287
< 		i = strcmp(r1, r2);
< 	switch(op) {
< 	case EQ: i = i==0; break;
< 	case GT: i = i>0; break;
< 	case GEQ: i = i>=0; break;
< 	case LT: i = i<0; break;
< 	case LEQ: i = i>=0; break;
< 	case NEQ: i = i!=0; break;
---
> 		d = strcmp(r1, r2);
> 	switch (op) {
> 	case TOK_EQ: i = d == 0; break;
> 	case TOK_GT: i = d > 0; break;
> 	case TOK_GEQ: i = d >= 0; break;
> 	case TOK_LT: i = d < 0; break;
> 	case TOK_LEQ: i = d <= 0; break;
> 	default: i = d != 0; break;
109c289
< 	return i? "1": "0";
---
> 	return(i ? "1" : "0");
112c292,294
< char *arith(op, r1, r2) char *r1, *r2; {
---
> static char *
> arith(int op, char *r1, char *r2)
> {
114d295
< 	register char *rv;
116,117c297,300
< 	if(!(ematch(r1, "[0-9]*$") && ematch(r2, "[0-9]*$")))
< 		yyerror("non-numeric argument");
---
> 	if (!isnum(r1, 0) || !isnum(r2, 0)) {
> 		fprintf(stderr, "non-numeric argument\n");
> 		exit(2);
> 	}
120,199c303,314
< 
< 	switch(op) {
< 	case ADD: i1 = i1 + i2; break;
< 	case SUBT: i1 = i1 - i2; break;
< 	case MULT: i1 = i1 * i2; break;
< 	case DIV: i1 = i1 / i2; break;
< 	case REM: i1 = i1 % i2; break;
< 	}
< 	rv = malloc(16);
< 	sprintf(rv, "%D", i1);
< 	return rv;
< }
< char *conj(op, r1, r2) char *r1, *r2; {
< 	register char *rv;
< 
< 	switch(op) {
< 
< 	case OR:
< 		if(EQL(r1, "0")
< 		|| EQL(r1, ""))
< 			if(EQL(r2, "0")
< 			|| EQL(r2, ""))
< 				rv = "0";
< 			else
< 				rv = r2;
< 		else
< 			rv = r1;
< 		break;
< 	case AND:
< 		if(EQL(r1, "0")
< 		|| EQL(r1, ""))
< 			rv = "0";
< 		else if(EQL(r2, "0")
< 		|| EQL(r2, ""))
< 			rv = "0";
< 		else
< 			rv = r1;
< 		break;
< 	}
< 	return rv;
< }
< 
< char *substr(v, s, w) char *v, *s, *w; {
< register si, wi;
< register char *res;
< 
< 	si = atol(s);
< 	wi = atol(w);
< 	while(--si) if(*v) ++v;
< 
< 	res = v;
< 
< 	while(wi--) if(*v) ++v;
< 
< 	*v = '\0';
< 	return res;
< }
< 
< char *length(s) register char *s; {
< 	register i = 0;
< 	register char *rv;
< 
< 	while(*s++) ++i;
< 
< 	rv = malloc(8);
< 	sprintf(rv, "%d", i);
< 	return rv;
< }
< 
< char *index(s, t) char *s, *t; {
< 	register i, j;
< 	register char *rv;
< 
< 	for(i = 0; s[i] ; ++i)
< 		for(j = 0; t[j] ; ++j)
< 			if(s[i]==t[j]) {
< 				sprintf(rv = malloc(8), "%d", ++i);
< 				return rv;
< 			}
< 	return "0";
---
> 	if ((op == TOK_DIV || op == TOK_REM) && i2 == 0) {
> 		fprintf(stderr, "division by zero\n");
> 		exit(2);
> 	}
> 	switch (op) {
> 	case TOK_ADD: i1 += i2; break;
> 	case TOK_SUB: i1 -= i2; break;
> 	case TOK_MUL: i1 *= i2; break;
> 	case TOK_DIV: i1 /= i2; break;
> 	default: i1 %= i2; break;
> 	}
> 	return(numstr(i1));
202c317,318
< char *match(s, p)
---
> static char *
> substr_op(char *v, char *s, char *w)
204c320,321
< 	register char *rv;
---
> 	int si, wi, len, i;
> 	char *r;
206,211c323,338
< 	sprintf(rv = malloc(8), "%d", ematch(s, p));
< 	if(nbra) {
< 		rv = malloc(strlen(Mstring[0])+1);
< 		strcpy(rv, Mstring[0]);
< 	}
< 	return rv;
---
> 	si = atoi(s);
> 	wi = atoi(w);
> 	len = strlen(v);
> 	if (si < 1)
> 		si = 1;
> 	if (wi < 0)
> 		wi = 0;
> 	if (si > len + 1)
> 		si = len + 1;
> 	if (wi > len - si + 1)
> 		wi = len - si + 1;
> 	r = xalloc((unsigned)wi + 1);
> 	for (i = 0; i < wi; i++)
> 		r[i] = v[si - 1 + i];
> 	r[wi] = '\0';
> 	return(r);
214,219c341,345
< #define INIT	register char *sp = instring;
< #define GETC()		(*sp++)
< #define PEEKC()		(*sp)
< #define UNGETC(c)	(--sp)
< #define RETURN(c)	return
< #define ERROR(c)	errxx(c)
---
> static char *
> length_op(char *s)
> {
> 	return(numstr(strlen(s)));
> }
220a347,357
> static char *
> index_op(char *s, char *t)
> {
> 	int i, j;
> 
> 	for (i = 0; s[i] != '\0'; i++)
> 		for (j = 0; t[j] != '\0'; j++)
> 			if (s[i] == t[j])
> 				return(numstr((long)i + 1));
> 	return("0");
> }
222,224c359,360
< ematch(s, p)
< char *s;
< register char *p;
---
> static char *
> match_op(char *s, char *p)
226,241c362,369
< 	static char expbuf[ESIZE];
< 	char *compile();
< 	register num;
< 	extern char *braslist[], *braelist[], *loc2;
< 
< 	compile(p, expbuf, &expbuf[512], 0);
< 	if(nbra > 1)
< 		yyerror("Too many '\\('s");
< 	if(advance(s, expbuf)) {
< 		if(nbra == 1) {
< 			p = braslist[0];
< 			num = braelist[0] - p;
< 			strncpy(Mstring[0], p, num);
< 			Mstring[0][num] = '\0';
< 		}
< 		return(loc2-s);
---
> 	char *r;
> 	int n;
> 
> 	n = ematch(s, p);
> 	if (nbra == 1) {
> 		r = xalloc((unsigned)strlen(match_string) + 1);
> 		strcpy(r, match_string);
> 		return(r);
243c371,394
< 	return(0);
---
> 	return(numstr(n));
> }
> 
> static int
> isnum(char *s, int sign)
> {
> 	if (sign)
> 		while (*s == '-')
> 			s++;
> 	while (*s >= '0' && *s <= '9')
> 		s++;
> 	return(*s == '\0');
> }
> 
> static char *
> numstr(long n)
> {
> 	char buf[32];
> 	char *r;
> 
> 	sprintf(buf, "%ld", n);
> 	r = xalloc((unsigned)strlen(buf) + 1);
> 	strcpy(r, buf);
> 	return(r);
246c397,398
< errxx(c)
---
> static char *
> xalloc(unsigned n)
248c400,407
< 	yyerror("RE error");
---
> 	char *p;
> 
> 	p = malloc(n);
> 	if (p == 0) {
> 		fprintf(stderr, "out of memory\n");
> 		exit(2);
> 	}
> 	return(p);
259d417
< 
261c419
< #define RNGE	03
---
> #define	RNGE	03
263c421,436
< #define	NBRA	9
---
> static char *braslist[NBRA];
> static char *braelist[NBRA];
> static char *loc2;
> static char *locs;
> static int circf;
> static int low;
> static int size;
> static char bittab[] = { 1, 2, 4, 8, 16, 32, 64, 128 };
> 
> #define PLACE(c)	ep[((c) & 0177) >> 3] |= bittab[(c) & 07]
> #define ISTHERE(c)	(ep[((c) & 0177) >> 3] & bittab[(c) & 07])
> 
> static char *compile_re(char *instring, char *ep, char *endbuf);
> static int advance_re(char *lp, char *ep);
> static void getrnge(char *str);
> static int ecmp(char *a, char *b, int count);
265,266c438,442
< #define PLACE(c)	ep[c >> 3] |= bittab[c & 07]
< #define ISTHERE(c)	(ep[c >> 3] & bittab[c & 07])
---
> static int
> ematch(char *s, char *p)
> {
> 	static char expbuf[ESIZE];
> 	int num;
268,287c444,462
< char	*braslist[NBRA];
< char	*braelist[NBRA];
< int	nbra;
< char *loc1, *loc2, *locs;
< int	sed;
< 
< int	circf;
< int	low;
< int	size;
< 
< char	bittab[] = {
< 	1,
< 	2,
< 	4,
< 	8,
< 	16,
< 	32,
< 	64,
< 	128
< };
---
> 	compile_re(p, expbuf, &expbuf[ESIZE]);
> 	if (nbra > 1) {
> 		fprintf(stderr, "Too many '\\('s\n");
> 		exit(2);
> 	}
> 	locs = 0;
> 	if (advance_re(s, expbuf)) {
> 		if (nbra == 1) {
> 			p = braslist[0];
> 			num = braelist[0] - p;
> 			if (num >= (int)sizeof(match_string))
> 				num = (int)sizeof(match_string) - 1;
> 			strncpy(match_string, p, num);
> 			match_string[num] = '\0';
> 		}
> 		return(loc2 - s);
> 	}
> 	return(0);
> }
289,298c464,469
< char *
< compile(instring, ep, endbuf, seof)
< register char *ep;
< char *instring, *endbuf;
< {
< 	INIT	/* Dependent declarations and initializations */
< 	register c;
< 	register eof = seof;
< 	char *lastep = instring;
< 	int cclcnt;
---
> static char *
> compile_re(char *instring, char *ep, char *endbuf)
> {
> 	char *sp;
> 	int c, eof, cclcnt, closed, lc, i, cflg;
> 	char *lastep;
300,303c471
< 	int closed;
< 	char neg;
< 	int lc;
< 	int i, cflg;
---
> 	int neg;
304a473,474
> 	sp = instring;
> 	eof = '\0';
306,309c476,480
< 	if((c = GETC()) == eof) {
< 		if(*ep == 0 && !sed)
< 			ERROR(41);
< 		RETURN(ep);
---
> 	c = *sp++;
> 	if (c == eof) {
> 		if (*ep == 0)
> 			re_error(41);
> 		return(ep);
316c487
< 		UNGETC(c);
---
> 		sp--;
319,320c490,492
< 			ERROR(50);
< 		if((c = GETC()) != '*' && ((c != '\\') || (PEEKC() != '{')))
---
> 			re_error(50);
> 		c = *sp++;
> 		if (c != '*' && (c != '\\' || *sp != '{'))
324c496
< 			RETURN(ep);
---
> 			return(ep);
327d498
< 
331d501
< 
333c503,504
< 			ERROR(36);
---
> 			re_error(36);
> 			/* fallthrough */
335c506
< 			if (lastep==0 || *lastep==CBRA || *lastep==CKET)
---
> 			if (lastep == 0 || *lastep == CBRA || *lastep == CKET)
339d509
< 
341c511
< 			if(PEEKC() != eof)
---
> 			if (*sp != eof)
345d514
< 
347,349c516,517
< 			if(&ep[17] >= endbuf)
< 				ERROR(50);
< 
---
> 			if (&ep[17] >= endbuf)
> 				re_error(50);
352c520
< 			for(i = 0; i < 16; i++)
---
> 			for (i = 0; i < 16; i++)
354d521
< 
356c523,524
< 			if((c = GETC()) == '^') {
---
> 			c = *sp++;
> 			if (c == '^') {
358c526
< 				c = GETC();
---
> 				c = *sp++;
360d527
< 
362,365c529,533
< 				if(c == '\0' || c == '\n')
< 					ERROR(49);
< 				if(c == '-' && lc != 0) {
< 					if ((c = GETC()) == ']') {
---
> 				if (c == '\0' || c == '\n')
> 					re_error(49);
> 				if (c == '-' && lc != 0) {
> 					c = *sp++;
> 					if (c == ']') {
369c537
< 					while(lc < c) {
---
> 					while (lc < c) {
376,378c544,547
< 			} while((c = GETC()) != ']');
< 			if(neg) {
< 				for(cclcnt = 0; cclcnt < 16; cclcnt++)
---
> 				c = *sp++;
> 			} while (c != ']');
> 			if (neg) {
> 				for (cclcnt = 0; cclcnt < 16; cclcnt++)
382d550
< 
384d551
< 
386d552
< 
388,389c554,555
< 			switch(c = GETC()) {
< 
---
> 			c = *sp++;
> 			switch (c) {
391,393c557,559
< 				if(nbra >= NBRA)
< 					ERROR(43);
< 				*bracketp++ = nbra;
---
> 				if (nbra >= NBRA)
> 					re_error(43);
> 				*bracketp++ = (char)nbra;
397d562
< 
399,400c564,565
< 				if(bracketp <= bracket)
< 					ERROR(42);
---
> 				if (bracketp <= bracket)
> 					re_error(42);
405d569
< 
407c571
< 				if(lastep == (char *) (0))
---
> 				if (lastep == 0)
412c576
< 				c = GETC();
---
> 				c = *sp++;
418,419c582,584
< 						ERROR(16);
< 				} while(((c = GETC()) != '\\') && (c != ','));
---
> 						re_error(16);
> 					c = *sp++;
> 				} while (c != '\\' && c != ',');
421c586
< 					ERROR(11);
---
> 					re_error(11);
424,426c589,592
< 					if(cflg++)
< 						ERROR(44);
< 					if((c = GETC()) == '\\')
---
> 					if (cflg++)
> 						re_error(44);
> 					c = *sp++;
> 					if (c == '\\')
429,430c595,596
< 						UNGETC(c);
< 						goto nlim; /* get 2'nd number */
---
> 						sp--;
> 						goto nlim;
433,435c599,601
< 				if(GETC() != '}')
< 					ERROR(45);
< 				if(!cflg)	/* one number */
---
> 				if (*sp++ != '}')
> 					re_error(45);
> 				if (!cflg)
437,438c603,604
< 				else if((ep[-1] & 0377) < (ep[-2] & 0377))
< 					ERROR(46);
---
> 				else if ((ep[-1] & 0377) < (ep[-2] & 0377))
> 					re_error(46);
440d605
< 
442,447c607,608
< 				ERROR(36);
< 
< 			case 'n':
< 				c = '\n';
< 				goto defchar;
< 
---
> 				re_error(36);
> 				/* fallthrough */
449,451c610,613
< 				if(c >= '1' && c <= '9') {
< 					if((c -= '1') >= closed)
< 						ERROR(25);
---
> 				if (c >= '1' && c <= '9') {
> 					c -= '1';
> 					if (c >= closed)
> 						re_error(25);
456,458c618
< 			}
< 			/* Drop through to default to use \ to turn off special chars */
< 
---
> 			} /* fallthrough */
468,501c628,629
< step(p1, p2)
< register char *p1, *p2;
< {
< 	register c;
< 
< 	if (circf) {
< 		loc1 = p1;
< 		return(advance(p1, p2));
< 	}
< 	/* fast check for first character */
< 	if (*p2==CCHR) {
< 		c = p2[1];
< 		do {
< 			if (*p1 != c)
< 				continue;
< 			if (advance(p1, p2)) {
< 				loc1 = p1;
< 				return(1);
< 			}
< 		} while (*p1++);
< 		return(0);
< 	}
< 		/* regular algorithm */
< 	do {
< 		if (advance(p1, p2)) {
< 			loc1 = p1;
< 			return(1);
< 		}
< 	} while (*p1++);
< 	return(0);
< }
< 
< advance(lp, ep)
< register char *lp, *ep;
---
> static int
> advance_re(char *lp, char *ep)
503,505c631
< 	register char *curlp;
< 	char c;
< 	char *bbeg;
---
> 	char *curlp, c, *bbeg;
509d634
< 
514d638
< 
519d642
< 
521c644
< 		if (*lp==0)
---
> 		if (*lp == 0)
524d646
< 
528d649
< 
531c652
< 		if(ISTHERE(c)) {
---
> 		if (ISTHERE(c)) {
537c658
< 		braslist[*ep++] = lp;
---
> 		braslist[(int)*ep++] = lp;
539d659
< 
541c661
< 		braelist[*ep++] = lp;
---
> 		braelist[(int)*ep++] = lp;
543d662
< 
547,548c666,667
< 		while(low--)
< 			if(*lp++ != c)
---
> 		while (low--)
> 			if (*lp++ != c)
551,552c670,671
< 		while(size--) 
< 			if(*lp++ != c)
---
> 		while (size--)
> 			if (*lp++ != c)
554c673
< 		if(size < 0)
---
> 		if (size < 0)
558d676
< 
561,562c679,680
< 		while(low--)
< 			if(*lp++ == '\0')
---
> 		while (low--)
> 			if (*lp++ == '\0')
565,566c683,684
< 		while(size--)
< 			if(*lp++ == '\0')
---
> 		while (size--)
> 			if (*lp++ == '\0')
568c686
< 		if(size < 0)
---
> 		if (size < 0)
572d689
< 
575c692
< 		while(low--) {
---
> 		while (low--) {
577c694
< 			if(!ISTHERE(c))
---
> 			if (!ISTHERE(c))
581c698
< 		while(size--) {
---
> 		while (size--) {
583c700
< 			if(!ISTHERE(c))
---
> 			if (!ISTHERE(c))
586c703
< 		if(size < 0)
---
> 		if (size < 0)
588c705
< 		ep += 18;		/* 16 + 2 */
---
> 		ep += 18;
590d706
< 
592,595c708,710
< 		bbeg = braslist[*ep];
< 		ct = braelist[*ep++] - bbeg;
< 
< 		if(ecmp(bbeg, lp, ct)) {
---
> 		bbeg = braslist[(int)*ep];
> 		ct = braelist[(int)*ep++] - bbeg;
> 		if (ecmp(bbeg, lp, ct)) {
600d714
< 
602,603c716,717
< 		bbeg = braslist[*ep];
< 		ct = braelist[*ep++] - bbeg;
---
> 		bbeg = braslist[(int)*ep];
> 		ct = braelist[(int)*ep++] - bbeg;
605c719
< 		while(ecmp(bbeg, lp, ct))
---
> 		while (ecmp(bbeg, lp, ct))
607,609c721,723
< 
< 		while(lp >= curlp) {
< 			if(advance(lp, ep))	return(1);
---
> 		while (lp >= curlp) {
> 			if (advance_re(lp, ep))
> 				return(1);
613,614d726
< 
< 
617c729,730
< 		while (*lp++);
---
> 		while (*lp++)
> 			;
619d731
< 
622c734,735
< 		while (*lp++ == *ep);
---
> 		while (*lp++ == *ep)
> 			;
625d737
< 
630c742
< 		} while(ISTHERE(c));
---
> 		} while (ISTHERE(c));
633d744
< 
636c747
< 			if(--lp == locs)
---
> 			if (--lp == locs)
638c749
< 			if (advance(lp, ep))
---
> 			if (advance_re(lp, ep))
642c753,754
< 
---
> 	default:
> 		re_error(0);
646,647c758,759
< getrnge(str)
< register char *str;
---
> static void
> getrnge(char *str)
650c762
< 	size = *str == 255 ? 20000 : (*str &0377) - low;
---
> 	size = *str == 255 ? 20000 : (*str & 0377) - low;
653,655c765,766
< ecmp(a, b, count)
< register char	*a, *b;
< register	count;
---
> static int
> ecmp(char *a, char *b, int count)
657,660c768,772
< 	if(a == b) /* should have been caught in compile() */
< 		error(51);
< 	while(count--)
< 		if(*a++ != *b++)	return(0);
---
> 	if (a == b)
> 		re_error(51);
> 	while (count--)
> 		if (*a++ != *b++)
> 			return(0);
664,665c776,777
< yyerror(s)
< 
---
> static void
> re_error(int c)
667c779,780
< 	fprintf(stderr, "%s\n", s);
---
> 	(void)c;
> 	fprintf(stderr, "RE error\n");
```

### cmd/factor.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/factor.s unix-v7-c99/cmd/factor.c || true
```

Expect:

```
1,351c1,151
< .globl	sqrt
< exit = 1.
< read = 3.
< write = 4.
< ldfps = 170100^tst
< /
< 	ldfps	$240
< 
< 	clr	argflg
< 	cmp	(sp)+,$2
< 	blt	begin
< 	tst	(sp)+
< 	mov	(sp),r2
< 	jsr	r5,atof; getch1
< 	inc	argflg
< 	br	begin1
< begin:
< 	tst	argflg
< 	beq 9f; sys exit; 9:
< 	jsr	r5,atof; getch
< begin1:
< 	tstf	fr0
< 	cfcc
< 	bpl 9f; jmp ouch; 9:
< 	bne 9f; sys exit; 9:
< 	cmpf	big,fr0
< 	cfcc
< 	bgt 9f; jmp ouch; 9:
< /
< 	movf	fr0,n
< 	jsr	pc,sqrt
< 	movf	fr0,v
< 	mov	$1,r0
< 	sys	write; nl; 1
< /
< 	movf	$one,fr0
< 	movf	fr0,fr4
< /
< 	movf	n,fr0
< 	movf	$two,fr1
< 	jsr	r5,xt
< /
< 	movf	n,fr0
< 	movif	$3,fr1
< 	jsr	r5,xt
< /
< 	movf	n,fr0
< 	movif	$5,fr1
< 	jsr	r5,xt
< /
< 	movf	n,fr0
< 	movif	$7,fr1
< 	jsr	r5,xt
< /
< 	movf	n,fr0
< 	movif	$11.,fr1
< 	jsr	r5,xt
< /
< 	movf	n,fr0
< 	movif	$13.,fr1
< 	jsr	r5,xt
< /
< 	movf	n,fr0
< 	movif	$17.,fr1
< 	mov	$tab+6,r4
< 	jsr	pc,xx
< 	jmp	begin
< /
< xt:
< 	movf	fr0,fr2
< 	divf	fr1,fr2
< 	modf	$one,fr2
< 	movf	fr3,fr2
< 	mulf	fr1,fr2
< 	cmpf	fr2,fr0
< 	cfcc
< 	beq	hit2
< 	rts	r5
< /
< /
< out1:
< 	mov	$tab,r4
< 	br	in1
< 
< out2:
< 	modf	fr4,fr2
< 	cfcc
< 	bne 9f; mov $xx0,-(sp); jmp hit; 9:
< 	br	in2
< xx:
< 	mov	(r4)+,kazoo
< xx0:
< 	mov	$kazoo,r0
< 	mov	$100.,r1
< 	clr	r2
< 	mov	$gorp,r3
< 	mov	$gorp+6,r5
< xx1:
< 	movf	fr0,fr2
< 	divf	fr1,fr2
< 	cmp	r4,$tabend
< 	bhis	out1
< in1:
< 	movf	fr2,(r3)
< 	bit	r2,(r5)
< 	beq	out2
< in2:
< kazoo	=.+2
< 	addf	$kazoo,fr1
< 	mov	(r4)+,(r0)
< 	sob	r1,xx1
< 	mov	$100.,r1
< 	mov	$127.,r2
< 	cmpf	v,fr1
< 	cfcc
< 	bge	xx1
< 	cmpf	$one,fr0
< 	cfcc
< 	beq	1f
< 	mov	$1,r0
< 	sys	write; sp5; 5
< 	movf	n,fr0
< 	jsr	r5,ftoa; wrchar
< 	mov	$1,r0
< 	sys	write; nl; 1
< 1:
< 	rts	pc
< /
< /
< /
< hit2:
< 	movf	fr1,t
< 	movf	fr3,n
< 	movf	fr3,fr0
< 	jsr	pc,sqrt
< 	movf	fr0,v
< 	mov	$1,r0
< 	sys	write; sp5; 5
< 	movf	t,fr0
< 	jsr	r5,ftoa; wrchar
< 	mov	$1,r0
< 	sys	write; nl; 1
< 	movf	n,fr0
< 	movf	t,fr1
< 	cmp	r4,$tab
< 	bne	1f
< 	mov	$tabend,r4
< 1:
< 	mov	-(r4),kazoo
< 	jmp	xt
< /
< hit:
< 	movf	fr1,t
< 	movf	fr3,n
< 	movf	fr3,fr0
< 	jsr	pc,sqrt
< 	movf	fr0,v
< 	mov	$1,r0
< 	sys	write; sp5; 5
< 	movf	t,fr0
< 	jsr	r5,ftoa; wrchar
< 	mov	$1,r0
< 	sys	write; nl; 1
< 	movf	n,fr0
< 	movf	t,fr1
< 	mov	$kazoo,r0
< 	rts	pc
< /
< /
< /	get one character from the console.
< /	called from atof.
< /
< getch:
< 	clr	r0
< 	sys	read; ch; 1
< 	bec 9f; sys exit; 9:
< 	tst r0; bne 9f; sys exit; 9:
< 	mov	ch,r0
< 	rts	r5
< /
< /
< /	get one character form the argument string.
< getch1:
< 	movb	(r2)+,r0
< 	rts	r5
< /
< /	write one character on the console
< /	called from ftoa.
< /
< wrchar:
< 	mov	r0,ch
< 	mov	$1,r0
< 	sys	write; ch; 1
< 	rts	r5
< /
< /
< /	read and convert a line from the console into fr0.
< /
< atof:
< 	mov	r1,-(sp)
< 	movif	$10.,r3
< 	clrf	r0
< 1:
< 	jsr	r5,*(r5)
< 	sub	$'0,r0
< 	cmp	r0,$9.
< 	bhi	2f
< 	mulf	r3,r0
< 	movif	r0,r1
< 	addf	r1,r0
< 	br	1b
< 2:
< 	cmp	r0,$' -'0
< 	beq	1b
< /
< 	mov	(sp)+,r1
< 	tst	(r5)+
< 	rts	r5
< 
< /
< /
< /
< /
< ftoa:
< 	mov	$ebuf,r2
< 1:
< 	modf	tenth,fr0
< 	movf	fr0,fr2
< 	movf	fr1,fr0
< 	addf	$epsilon,fr2
< 	modf	$ten,fr2
< 	movfi	fr3,r0
< 	movb	r0,-(r2)
< 	tstf	fr0
< 	cfcc
< 	bne	1b
< 1:
< 	movb	(r2)+,r0
< 	add	$60,r0
< 	jsr	r5,*(r5)
< 	cmp	r2,$ebuf
< 	blo	1b
< 	tst	(r5)+
< 	rts	r5
< /
< epsilon = 037114
< tenth:	037314; 146314; 146314; 146315
< 	.bss
< buf:	.=.+18.
< ebuf:
< 	.text
< /
< /
< /
< /	complain about a number which the program
< /	is unable to digest
< ouch:
< 	mov	$2,r0
< 	sys	write; 1f; 2f-1f
< 	jmp	begin
< /
< 1:	<Ouch.\n>
< 2:	.even
< /
< /
< one	= 40200
< two	= 40400
< four	= 40600
< ten	= 41040
< /
< 	.data
< big:	056177; 177777; 177777; 177777
< nl:	<\n>
< sp5:	<     >
< 	.even
< /
< tab:
< 	41040; 40400; 40600; 40400; 40600; 40700; 40400; 40700
< 	40600; 40400; 40600; 40700; 40700; 40400; 40700; 40600
< 	40400; 40700; 40600; 40700; 41000; 40600; 40400; 40600
< 	40400; 40600; 41000; 40700; 40600; 40700; 40400; 40600
< 	40700; 40400; 40700; 40700; 40600; 40400; 40600; 40700
< 	40400; 40700; 40600; 40400; 40600; 40400; 41040; 40400
< tabend:
< /
< 	.bss
< ch:	.=.+2
< t:	.=.+8
< n:	.=.+8
< v:	.=.+8
< gorp:	.=.+8
< argflg:	.=.+2
< 	.text
< ldfps = 170100^tst
< stfps = 170200^tst
< /
< /	sqrt replaces the f.p. number in fr0 by its
< /	square root.  newton's method
< /
< .globl	sqrt, _sqrt
< /
< /
< _sqrt:
< 	mov	r5,-(sp)
< 	mov	sp,r5
< 	movf	4(r5),fr0
< 	jsr	pc,sqrt
< 	mov	(sp)+,r5
< 	rts	pc
< 
< sqrt:
< 	tstf	fr0
< 	cfcc
< 	bne	1f
< 	clc
< 	rts	pc		/sqrt(0)
< 1:
< 	bgt	1f
< 	clrf	fr0
< 	sec
< 	rts	pc		/ sqrt(-a)
< 1:
< 	mov	r0,-(sp)
< 	stfps	-(sp)
< 	mov	(sp),r0
< 	bic	$!200,r0		/ retain mode
< 	ldfps	r0
< 	movf	fr1,-(sp)
< 	movf	fr2,-(sp)
< /
< 	movf	fr0,fr1
< 	movf	fr0,-(sp)
< 	asr	(sp)
< 	add	$20100,(sp)
< 	movf	(sp)+,fr0	/initial guess
< 	mov	$4,r0
< 1:
< 	movf	fr1,fr2
< 	divf	fr0,fr2
< 	addf	fr2,fr0
< 	mulf	$half,fr0	/ x = (x+a/x)/2
< 	sob	r0,1b
< 2:
< 	movf	(sp)+,fr2
< 	movf	(sp)+,fr1
< 	ldfps	(sp)+
< 	mov	(sp)+,r0
< 	clc
< 	rts	pc
< /
< half	= 40000
---
> #include <stdio.h>
> 
> #define MAXNUM 72057594037927936ULL
> 
> static int
> parse_number(char *s, unsigned long long *out)
> {
> 	unsigned long long n;
> 	int any;
> 
> 	while (*s == ' ' || *s == '\t' || *s == '\n')
> 		s++;
> 	n = 0;
> 	any = 0;
> 	while (*s >= '0' && *s <= '9') {
> 		any = 1;
> 		if (n > (MAXNUM - (unsigned long long)(*s - '0')) / 10ULL)
> 			return(-1);
> 		n = n * 10ULL + (unsigned long long)(*s - '0');
> 		s++;
> 	}
> 	while (*s == ' ' || *s == '\t' || *s == '\n')
> 		s++;
> 	if (!any || *s != '\0' || n >= MAXNUM)
> 		return(-1);
> 	*out = n;
> 	return(0);
> }
> 
> static int
> read_number(unsigned long long *out)
> {
> 	char buf[80];
> 	int c, i, any;
> 
> 	i = 0;
> 	any = 0;
> 	while ((c = getchar()) != EOF) {
> 		if (c != ' ' && c != '\t' && c != '\n')
> 			break;
> 	}
> 	if (c == EOF)
> 		return(0);
> 	do {
> 		any = 1;
> 		if (i < (int)sizeof(buf) - 1)
> 			buf[i++] = (char)c;
> 		c = getchar();
> 	} while (c != EOF && c != ' ' && c != '\t' && c != '\n');
> 	buf[i] = '\0';
> 	if (!any)
> 		return(0);
> 	if (parse_number(buf, out) < 0)
> 		return(-1);
> 	return(1);
> }
> 
> static void
> putnum(unsigned long long n)
> {
> 	char buf[24];
> 	int i;
> 
> 	i = 0;
> 	if (n == 0)
> 		buf[i++] = '0';
> 	else while (n != 0) {
> 		buf[i++] = (char)('0' + (int)(n % 10ULL));
> 		n /= 10ULL;
> 	}
> 	while (i > 0)
> 		putchar(buf[--i]);
> }
> 
> static void
> factor(unsigned long long n)
> {
> 	unsigned long long p;
> 
> 	putchar('\n');
> 	while ((n % 2ULL) == 0) {
> 		printf("     ");
> 		putnum(2ULL);
> 		putchar('\n');
> 		n /= 2ULL;
> 	}
> 	while ((n % 3ULL) == 0) {
> 		printf("     ");
> 		putnum(3ULL);
> 		putchar('\n');
> 		n /= 3ULL;
> 	}
> 	p = 5ULL;
> 	while (p <= n / p) {
> 		while ((n % p) == 0) {
> 			printf("     ");
> 			putnum(p);
> 			putchar('\n');
> 			n /= p;
> 		}
> 		p += 2ULL;
> 		if (p > n / p)
> 			break;
> 		while ((n % p) == 0) {
> 			printf("     ");
> 			putnum(p);
> 			putchar('\n');
> 			n /= p;
> 		}
> 		p += 4ULL;
> 	}
> 	if (n > 1ULL) {
> 		printf("     ");
> 		putnum(n);
> 		putchar('\n');
> 	}
> }
> 
> static void
> ouch(void)
> {
> 	fprintf(stderr, "Ouch.\n");
> }
> 
> int
> main(int argc, char **argv)
> {
> 	unsigned long long n;
> 	int r;
> 
> 	if (argc > 1) {
> 		if (parse_number(argv[1], &n) < 0) {
> 			ouch();
> 			return(1);
> 		}
> 		if (n == 0ULL)
> 			return(0);
> 		factor(n);
> 		return(0);
> 	}
> 	for (;;) {
> 		r = read_number(&n);
> 		if (r == 0 || (r > 0 && n == 0ULL))
> 			return(0);
> 		if (r < 0) {
> 			ouch();
> 			return(1);
> 		}
> 		factor(n);
> 	}
> }
```

### cmd/osh.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/osh.c unix-v7-c99/cmd/osh.c || true
```

Expect:

```
55c55
< char	*mesg[NSIG] {
---
> char	*mesg[NSIG] = {
78,80c78,112
< main(c, av)
< int c;
< char **av;
---
> int *syntax(char **p1, char **p2);
> int execute(int *t, int *pf1, int *pf2);
> int main1(void);
> int word(void);
> int readc(void);
> int prs(char *as);
> int prn(int n);
> int prc(char ac);
> int putc(int c);
> int err(char *s, int code);
> int getc(void);
> int any(int c, char *as);
> int equal(char *s1, char *s2);
> int texec(char *f, int *at);
> int pwait(int pid, int *t);
> int *blkcpy(int **p);
> extern int read(int fd, char *buf, int n);
> extern int write(int fd, char *buf, int n);
> extern int close(int fd);
> extern int open(char *p, int f);
> extern int creat(char *p, int m);
> extern int pipe(int *pv);
> extern int dup();
> extern int fork(void);
> extern int wait(int *st);
> extern int execv(char *p, char **av);
> extern long lseek(int fd, long off, int whence);
> extern int getpid(void);
> extern int getuid(void);
> extern int chdir(char *p);
> extern int signal();
> extern void exit(int n) __attribute__((__noreturn__));
> 
> int
> main(int c, char **av)
82,83c114,115
< 	register f;
< 	register char *acname, **v;
---
> 	register int f;
> 	register char **v;
93d124
< 	acname = "<none>";
137c168,169
< main1()
---
> int
> main1(void)
140c172
< 	register *t;
---
> 	register int *t;
158c190
< 				return;
---
> 				return(0);
163c195
< 			execute(t);
---
> 			execute(t, 0, 0);
164a197
> 	return(0);
167c200,201
< word()
---
> int
> word(void)
187c221
< 				return;
---
> 				return(0);
204c238
< 		return;
---
> 		return(0);
217c251
< 			return;
---
> 			return(0);
223,224c257,258
< tree(n)
< int n;
---
> int *
> tree(int n)
226c260
< 	register *t;
---
> 	register int *t;
229c263
< 	treep =+ n;
---
> 	treep += n;
238c272,273
< getc()
---
> int
> getc(void)
248c283
< 		argp =- 10;
---
> 		argp -= 10;
250c285
< 		argp =+ 10;
---
> 		argp += 10;
256c291
< 		linep =- 10;
---
> 		linep -= 10;
258c293
< 		linep =+ 10;
---
> 		linep += 10;
292c327,328
< readc()
---
> int
> readc(void)
296c332
< 	register c;
---
> 	register int c;
299c335
< 		if (arginp == 1)
---
> 		if (arginp == (char *)1)
302c338
< 			arginp = 1;
---
> 			arginp = (char *)1;
309c345
< 	if((rdstat = read(0, &cc, 1)) != 1)
---
> 	if((rdstat = read(0, &cc, 1)) != 1) {
311a348
> 	}
323,324c360,366
< syntax(p1, p2)
< char **p1, **p2;
---
> int *syn1(char **p1, char **p2);
> int *syn2(char **p1, char **p2);
> int *syn3(char **p1, char **p2);
> int *syntax(char **p1, char **p2);
> 
> int *
> syntax(char **p1, char **p2)
342,343c384,385
< syn1(p1, p2)
< char **p1, **p2;
---
> int *
> syn1(char **p1, char **p2)
346c388
< 	register *t, *t1;
---
> 	register int *t, *t1;
370c412
< 			t[DLEF] = syn2(p1, p);
---
> 			t[DLEF] = (int)(long)syn2(p1, p);
373,374c415,416
< 				t1 = t[DLEF];
< 				t1[DFLG] =| FAND|FPRS|FINT;
---
> 				t1 = (int *)(long)t[DLEF];
> 				t1[DFLG] |= FAND|FPRS|FINT;
376c418
< 			t[DRIT] = syntax(p+1, p2);
---
> 			t[DRIT] = (int)(long)syntax(p+1, p2);
392,393c434,435
< syn2(p1, p2)
< char **p1, **p2;
---
> int *
> syn2(char **p1, char **p2)
415,416c457,458
< 			t[DLEF] = syn3(p1, p);
< 			t[DRIT] = syn2(p+1, p2);
---
> 			t[DLEF] = (int)(long)syn3(p1, p);
> 			t[DRIT] = (int)(long)syn2(p+1, p2);
430,431c472,473
< syn3(p1, p2)
< char **p1, **p2;
---
> int *
> syn3(char **p1, char **p2)
435c477
< 	register *t;
---
> 	register int *t;
440c482
< 		flg =| FPAR;
---
> 		flg |= FPAR;
468c510
< 			flg =| FCAT; else
---
> 			flg |= FCAT; else
469a512
> 		/* fallthrough */
483c526
< 				i = *p;
---
> 				i = (int)(long)*p;
488c531
< 			o = *p;
---
> 			o = (int)(long)*p;
501c544
< 		t[DSPR] = syn1(lp, rp);
---
> 		t[DSPR] = (int)(long)syn1(lp, rp);
510c553
< 		t[l+DCOM] = p1[l];
---
> 		t[l+DCOM] = (int)(long)p1[l];
518,520c561,562
< scan(at, f)
< int *at;
< int (*f)();
---
> int
> scan(int *at, int (*f)())
523c565
< 	register *t;
---
> 	register int *t;
526,527c568,569
< 	while(p = *t++)
< 		while(c = *p)
---
> 	while((p = (char *)(long)*t++))
> 		while((c = *p))
528a571
> 	return(0);
531,532c574,575
< tglob(c)
< int c;
---
> int
> tglob(int c)
540,541c583,584
< trim(c)
< int c;
---
> int
> trim(int c)
547,548c590,591
< execute(t, pf1, pf2)
< int *t, *pf1, *pf2;
---
> int
> execute(int *t, int *pf1, int *pf2)
551c594
< 	register *t1;
---
> 	register int *t1;
553d595
< 	extern errno;
559c601
< 		cp1 = t[DCOM];
---
> 		cp1 = (char *)(long)t[DCOM];
562c604
< 				if(chdir(t[DCOM+1]) < 0)
---
> 				if(chdir((char *)(long)t[DCOM+1]) < 0)
566c608
< 			return;
---
> 			return(0);
571c613
< 				return;
---
> 				return(0);
576c618
< 			return;
---
> 			return(0);
580c622
< 				execv("/bin/login", t+DCOM);
---
> 				execv("/bin/login", (char **)(t+DCOM));
583c625
< 			return;
---
> 			return(0);
587c629
< 				execv("/bin/newgrp", t+DCOM);
---
> 				execv("/bin/newgrp", (char **)(t+DCOM));
590c632
< 			return;
---
> 			return(0);
594c636
< 			return;
---
> 			return(0);
597c639,640
< 			return;
---
> 			return(0);
> 		/* fallthrough */
606c649
< 			return;
---
> 			return(0);
618c661
< 				return;
---
> 				return(0);
621c664
< 			return;
---
> 			return(0);
625c668
< 			i = open(t[DLEF], 0);
---
> 			i = open((char *)(long)t[DLEF], 0);
627c670
< 				prs(t[DLEF]);
---
> 				prs((char *)(long)t[DLEF]);
634c677
< 				i = open(t[DRIT], 1);
---
> 				i = open((char *)(long)t[DRIT], 1);
640c683
< 			i = creat(t[DRIT], 0666);
---
> 			i = creat((char *)(long)t[DRIT], 0666);
642c685
< 				prs(t[DRIT]);
---
> 				prs((char *)(long)t[DRIT]);
672,674c715,717
< 			if(t1 = t[DSPR])
< 				t1[DFLG] =| f&FINT;
< 			execute(t1);
---
> 			if((t1 = (int *)(long)t[DSPR]))
> 				t1[DFLG] |= f&FINT;
> 			execute(t1, 0, 0);
680,681c723,724
< 			t[DSPR] = "/etc/glob";
< 			execv(t[DSPR], t+DSPR);
---
> 			t[DSPR] = (int)(long)"/etc/glob";
> 			execv((char *)(long)t[DSPR], (char **)(t+DSPR));
687c730
< 		texec(t[DCOM], t);
---
> 		texec((char *)(long)t[DCOM], t);
690c733
< 		while(*cp1 = *cp2++)
---
> 		while((*cp1 = *cp2++))
692,693c735,736
< 		cp2 = t[DCOM];
< 		while(*cp1++ = *cp2++);
---
> 		cp2 = (char *)(long)t[DCOM];
> 		while((*cp1++ = *cp2++));
696c739
< 		prs(t[DCOM]);
---
> 		prs((char *)(long)t[DCOM]);
703,704c746,747
< 		t1 = t[DLEF];
< 		t1[DFLG] =| FPOU | (f&(FPIN|FINT|FPRS));
---
> 		t1 = (int *)(long)t[DLEF];
> 		t1[DFLG] |= FPOU | (f&(FPIN|FINT|FPRS));
706,707c749,750
< 		t1 = t[DRIT];
< 		t1[DFLG] =| FPIN | (f&(FPOU|FINT|FAND|FPRS));
---
> 		t1 = (int *)(long)t[DRIT];
> 		t1[DFLG] |= FPIN | (f&(FPOU|FINT|FAND|FPRS));
709c752
< 		return;
---
> 		return(0);
713,719c756,762
< 		if(t1 = t[DLEF])
< 			t1[DFLG] =| f;
< 		execute(t1);
< 		if(t1 = t[DRIT])
< 			t1[DFLG] =| f;
< 		execute(t1);
< 		return;
---
> 		if((t1 = (int *)(long)t[DLEF]))
> 			t1[DFLG] |= f;
> 		execute(t1, 0, 0);
> 		if((t1 = (int *)(long)t[DRIT]))
> 			t1[DFLG] |= f;
> 		execute(t1, 0, 0);
> 		return(0);
721a765
> 	return(0);
724,725c768,769
< texec(f, at)
< int *at;
---
> int
> texec(char *f, int *at)
727c771
< 	extern errno;
---
> 	extern int errno;
731c775
< 	execv(f, t+DCOM);
---
> 	execv(f, (char **)(t+DCOM));
734,736c778,780
< 			t[DCOM] = linep;
< 		t[DSPR] = "/usr/bin/osh";
< 		execv(t[DSPR], t+DSPR);
---
> 			t[DCOM] = (int)(long)linep;
> 		t[DSPR] = (int)(long)"/usr/bin/osh";
> 		execv((char *)(long)t[DSPR], (char **)(t+DSPR));
741c785
< 		prs(t[DCOM]);
---
> 		prs((char *)(long)t[DCOM]);
744a789
> 	return(0);
747,749c792,793
< err(s, exitno)
< char *s;
< int exitno;
---
> int
> err(char *s, int exitno)
757a802
> 	return(0);
760,761c805,806
< prs(as)
< char *as;
---
> int
> prs(char *as)
767a813
> 	return(0);
770c816,817
< putc(c)
---
> int
> putc(int c)
775a823
> 	return(0);
778,779c826,827
< prn(n)
< int n;
---
> int
> prn(int n)
781c829
< 	register a;
---
> 	register int a;
783c831
< 	if (a = n/10)
---
> 	if ((a = n/10))
785a834
> 	return(0);
788,790c837,838
< any(c, as)
< int c;
< char *as;
---
> int
> any(int c, char *as)
801,802c849,850
< equal(as1, as2)
< char *as1, *as2;
---
> int
> equal(char *as1, char *as2)
814,815c862,863
< pwait(i, t)
< int i, *t;
---
> int
> pwait(int i, int *t)
817c865
< 	register p, e;
---
> 	register int p, e;
818a867
> 	(void)t;
840c889
< 		if (e || s&&stoperr)
---
> 		if (e || (s&&stoperr))
842c891
< 		errval =| (s>>8);
---
> 		errval |= (s>>8);
843a893
> 	return(0);
```

### cmd/primes.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/primes.s unix-v7-c99/cmd/primes.c | sed 's/^\([<>]\) $/\1/' || true
```

Expect:

```
1,355c1,149
< ldfps = 170100^tst
< /
< 	ldfps	$240
<
< 	clr	argflg
< 	cmp	(sp)+,$2
< 	blt	begin
< 	tst	(sp)+
< 	mov	(sp),r2
< 	jsr	r5,atof; getch1
< 	inc	argflg
< 	br	begin1
< begin:
< 	tst	argflg
< 	beq 9f; sys exit; 9:
< 	jsr	r5,atof; getch
< begin1:
< 	tstf	fr0
< 	cfcc
< 	bpl 9f; jmp ouch; 9:
< 	bne 9f; sys exit; 9:
< 	cmpf	big,fr0
< 	cfcc
< 	bgt 9f; jmp ouch; 9:
< /
< 	movf	$f100,fr1
< 	cmpf	fr0,fr1
< 	cfcc
< 	bge	1f
< 	mov	$pt,r3
< 3:
< 	cmp	r3,$ptend
< 	bhis	1f
< 	movif	(r3)+,fr1
< 	cmpf	fr1,fr0
< 	cfcc
< 	blt	3b
< 	tst	-(r3)
< 3:
< 	movif	(r3),fr0
< 	jsr	r5,ftoa; wrchar
< 	mov	$'\n,r0
< 	jsr	r5,wrchar
< 	tst	(r3)+
< 	cmp	r3,$ptend
< 	blo	3b
< 	movf	$f100,fr0
< /
< 1:
< 	divf	$two,fr0
< 	modf	$one,fr0
< 	movf	fr1,fr0
< 	mulf	$two,fr0
< 	addf	$one,fr0
< 	movif	$tsiz8,fr1
< 	movf	fr1,fr5
< 	movf	fr0,nn
< /
< /
< /
< /	clear the sieve table
< /
< 2:
< 	mov	$table,r3
< 3:
< 	cmp	r3,$table+tabsiz
< 	bhis	3f
< 	clrb	(r3)+
< 	br	3b
< /
< /	run the sieve
< /
< 3:
< 	movf	nn,fr0
< 	addf	fr5,fr0
< 	jsr	r5,sqrt
< 	movf	fr0,v
< /
< 	movf	nn,fr0
< 	movif	$3.,fr1
< 	jsr	pc,5f
< 	movif	$5.,fr1
< 	jsr	pc,5f
< 	movif	$7.,fr1
< 	jsr	pc,5f
< 	movif	$11.,fr1
< 	mov	$factab+2,r4
< 4:
< 	jsr	pc,5f
< 	mov	(r4)+,kazoo
< kazoo	=.+2
< 	addf	$kazoo,fr1
< 	cmp	r4,$ftabend
< 	blo	3f
< 	mov	$factab,r4
< 3:
< 	cmpf	v,fr1
< 	cfcc
< 	bge	4b
< 	br	1f
< /
< /
< 5:
< 	movf	fr0,fr2
< 	divf	fr1,fr2
< 	modf	$one,fr2
< 	mulf	fr1,fr3
< 	subf	fr0,fr3
< 	cfcc
< 	bpl	3f
< 	addf	fr1,fr3
< 3:
< 	cmpf	fr5,fr3
< 	cfcc
< 	ble	3f
< 	movfi	fr3,r0
< 	ashc	$-3.,r0
< 	ash	$-13.,r1
< 	bic	$177770,r1
< 	bisb	bittab(r1),table(r0)
< 	addf	fr1,fr3
< 	br	3b
< 3:
< 	rts	pc
< /
< /
< /	get one character form the argument string.
< getch1:
< 	movb	(r2)+,r0
< 	rts	r5
< /
< /	now get the primes from the table
< /	and print them.
< /
< 1:
< /
< 	movf	nn,fr0
< 	clr	r3
< 	br	4f
< /
< 1:
< 	inc	r3
< 	inc	r3
< 	cmp	r3,$tsiz8
< 	bge	2b
< /
< 4:
< /
< 	jsr	pc,prime
< 	bec	3f
< 	movf	nn,fr0
< 	jsr	r5,ftoa; wrchar
< 	mov	$'\n,r0
< 	jsr	r5,wrchar
< 3:
< 	movf	nn,fr0
< 	addf	$two,fr0
< 	movf	fr0,nn
< 	br	1b
< /
< /
< /
< /
< prime:
< 	mov	r3,r4
< 	ashc	$-3.,r4
< 	ash	$-13.,r5
< 	bic	$177770,r5
< 	bitb	bittab(r5),table(r4)
< 	bne	1f
< 	sec
< 1:
< 	rts	pc
< /
< /
< /
< /
< one	= 40200
< half	= 40000
< opower	= 34400
< power	= 44000
< f100	= 41710
< /
< /	get one character from the console.
< /	called from atof.
< /
< getch:
< 	clr	r0
< 	sys	read; ch; 1
< 	bec 9f; sys exit; 9:
< 	tst r0; bne 9f; sys exit; 9:
< 	mov	ch,r0
< 	rts	r5
< /
< /
< /	write one character on the console
< /	called from ftoa.
< /
< wrchar:
< 	tst	iobuf
< 	bne	1f
< 	mov	$iobuf+2,iobuf
< 1:
< 	movb	r0,*iobuf
< 	inc	iobuf
< 	cmp	iobuf,$iobuf+514.
< 	blo	1f
< 	mov	$1,r0
< 	sys	write; iobuf+2; 512.
< 	mov	$iobuf+2,iobuf
< 1:
< 	rts	r5
< /
< 	.bss
< iobuf:	.=.+518.
< 	.text
< /
< /
< /	read and convert a line from the console into fr0.
< /
< atof:
< 	mov	r1,-(sp)
< 	movif	$10.,r3
< 	clrf	r0
< 1:
< 	jsr	r5,*(r5)
< 	sub	$'0,r0
< 	cmp	r0,$9.
< 	bhi	2f
< 	mulf	r3,r0
< 	movif	r0,r1
< 	addf	r1,r0
< 	br	1b
< 2:
< 	cmp	r0,$' -'0
< 	beq	1b
< /
< 	mov	(sp)+,r1
< 	tst	(r5)+
< 	rts	r5
< /
< /
< ftoa:
< 	mov	$ebuf,r2
< 1:
< 	movf	fr0,fr1
< 	divf	$ten,fr1
< 	movf	fr1,fr2
< 	modf	$one,fr2
< 	movf	fr3,-(sp)
< 	mulf	$ten,fr3
< 	negf	fr3
< 	addf	fr0,fr3
< 	movfi	fr3,-(r2)
< 	movf	(sp)+,fr0
< 	tstf	fr0
< 	cfcc
< 	bne	1b
< 1:
< 	mov	(r2)+,r0
< 	add	$60,r0
< 	jsr	r5,*(r5)
< 	cmp	r2,$ebuf
< 	blo	1b
< 	tst	(r5)+
< 	rts	r5
< /
< /
< /
< /	replace the f.p. number in fr0 by its square root
< /
< sqrt:
< 	movf	r0,r1		/ a
< 	tstf	fr0
< 	cfcc
< 	beq	2f
< 	bgt	1f
< 	sec
< 	rts	r5		/ sqrt(-a)
< 1:
< 	seti
< 	movf	fr0,-(sp)
< 	asr	(sp)
< 	add	$20100,(sp)
< 	movf	(sp)+,fr0
< 	movif	$2,r3		/ constant 2
< 	mov	$4,r0
< 1:
< 	movf	r1,r2
< 	divf	r0,r2
< 	addf	r2,r0
< 	divf	r3,r0		/ x = (x+a/x)/2
< 	dec	r0
< 	bgt	1b
< 2:
< 	clc
< 	rts	r5
< /
< /
< buf:	.=.+38.
< ebuf:
< /
< /
< /
< /	complain about a number which the program
< /	is unable to digest
< ouch:
< 	mov	$2,r0
< 	sys	write; 1f; 2f-1f
< 	jmp	begin
< /
< 1:	<Ouch.\n>
< 2:	.even
< /
< /
< one	= 40200
< two	= 40400
< four	= 40600
< six	= 40700
< ten	= 41040
< /
< 	.data
< bittab:	.byte	1, 2, 4, 10, 20, 40, 100, 200
< big:	056177; 177777; 177777; 177777
< /
< pt:	2.; 3.; 5.; 7.; 11.; 13.; 17.; 19.; 23.; 29.; 31.; 37.; 41.; 43.
< 	47.; 53.; 59.; 61.; 67.; 71.; 73.; 79.; 83.; 89.; 97.
< ptend:
< nl:	<\n>
< sp5:	<     >
< 	.even
< /
< /
< factab:
< 	41040; 40400; 40600; 40400; 40600; 40700; 40400; 40700
< 	40600; 40400; 40600; 40700; 40700; 40400; 40700; 40600
< 	40400; 40700; 40600; 40700; 41000; 40600; 40400; 40600
< 	40400; 40600; 41000; 40700; 40600; 40700; 40400; 40600
< 	40700; 40400; 40700; 40700; 40600; 40400; 40600; 40700
< 	40400; 40700; 40600; 40400; 40600; 40400; 41040; 40400
< ftabend:
< /
< 	.bss
< ch:	.=.+2
< t:	.=.+8
< n:	.=.+8
< v:	.=.+8
< nn:	.=.+8
< place:	.=.+8
< /
< tabsiz	= 1000.
< tsiz8	= 8000.
< table:	.=.+tabsiz
< argflg:	.=.+2
< 	.text
---
> #include <stdio.h>
>
> #define MAXNUM 72057594037927936ULL
>
> static int
> parse_number(char *s, unsigned long long *out)
> {
> 	unsigned long long n;
> 	int any;
>
> 	while (*s == ' ' || *s == '\t' || *s == '\n')
> 		s++;
> 	n = 0;
> 	any = 0;
> 	while (*s >= '0' && *s <= '9') {
> 		any = 1;
> 		if (n > (MAXNUM - (unsigned long long)(*s - '0')) / 10ULL)
> 			return(-1);
> 		n = n * 10ULL + (unsigned long long)(*s - '0');
> 		s++;
> 	}
> 	while (*s == ' ' || *s == '\t' || *s == '\n')
> 		s++;
> 	if (!any || *s != '\0' || n >= MAXNUM)
> 		return(-1);
> 	*out = n;
> 	return(0);
> }
>
> static int
> read_number(unsigned long long *out)
> {
> 	char buf[80];
> 	int c, i;
>
> 	i = 0;
> 	while ((c = getchar()) != EOF) {
> 		if (c != ' ' && c != '\t' && c != '\n')
> 			break;
> 	}
> 	if (c == EOF)
> 		return(0);
> 	do {
> 		if (i < (int)sizeof(buf) - 1)
> 			buf[i++] = (char)c;
> 		c = getchar();
> 	} while (c != EOF && c != ' ' && c != '\t' && c != '\n');
> 	buf[i] = '\0';
> 	if (parse_number(buf, out) < 0)
> 		return(-1);
> 	return(1);
> }
>
> static void
> putnum(unsigned long long n)
> {
> 	char buf[24];
> 	int i;
>
> 	i = 0;
> 	if (n == 0)
> 		buf[i++] = '0';
> 	else while (n != 0) {
> 		buf[i++] = (char)('0' + (int)(n % 10ULL));
> 		n /= 10ULL;
> 	}
> 	while (i > 0)
> 		putchar(buf[--i]);
> }
>
> static int
> prime(unsigned long long n)
> {
> 	unsigned long long p;
>
> 	if (n < 2ULL)
> 		return(0);
> 	if (n == 2ULL || n == 3ULL)
> 		return(1);
> 	if ((n % 2ULL) == 0 || (n % 3ULL) == 0)
> 		return(0);
> 	p = 5ULL;
> 	while (p <= n / p) {
> 		if ((n % p) == 0)
> 			return(0);
> 		p += 2ULL;
> 		if (p > n / p)
> 			break;
> 		if ((n % p) == 0)
> 			return(0);
> 		p += 4ULL;
> 	}
> 	return(1);
> }
>
> static int
> print_prime(unsigned long long n)
> {
> 	putnum(n);
> 	if (putchar('\n') == EOF)
> 		return(-1);
> 	if (fflush(stdout) == EOF)
> 		return(-1);
> 	return(0);
> }
>
> static void
> ouch(void)
> {
> 	fprintf(stderr, "Ouch.\n");
> }
>
> int
> main(int argc, char **argv)
> {
> 	unsigned long long n;
> 	int r;
>
> 	if (argc > 1) {
> 		if (parse_number(argv[1], &n) < 0) {
> 			ouch();
> 			return(1);
> 		}
> 		if (n == 0ULL)
> 			return(0);
> 	} else {
> 		r = read_number(&n);
> 		if (r <= 0 || n == 0ULL) {
> 			if (r < 0)
> 				ouch();
> 			return(r < 0 ? 1 : 0);
> 		}
> 	}
> 	if (n >= MAXNUM) {
> 		ouch();
> 		return(1);
> 	}
> 	if (n <= 2ULL) {
> 		if (print_prime(2ULL) < 0)
> 			return(0);
> 		n = 3ULL;
> 	} else if ((n % 2ULL) == 0)
> 		n++;
> 	for (;;) {
> 		if (prime(n) && print_prime(n) < 0)
> 			return(0);
> 		n += 2ULL;
> 	}
> }
```

### cmd/prof.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/prof.c unix-v7-c99/cmd/prof.c || true
```

Expect:

```
11a12,16
> int min(unsigned a, unsigned b);
> int max(unsigned a, unsigned b);
> int done(void);
> int timcmp(const void *vp1, const void *vp2), valcmp(const void *vp1, const void *vp2);
> 
42c47
< double	ftime;
---
> double	ftim;
56,57c61
< main(argc, argv)
< char **argv;
---
> int main(int argc, char **argv)
60c64
< 	int timcmp(), valcmp();
---
> 	int timcmp(const void *, const void *), valcmp(const void *, const void *);
61a66
> #ifdef plot
64d68
< 	struct cnt *cp;
65a70,71
> #endif
> 	struct cnt *cp;
83c89
< 				if(lowpc == -1)
---
> 				if(lowpc == (unsigned)-1)
121a128
> #ifdef plot
122a130
> #endif
153,154c161,162
< 		register j;
< 		unsigned UNIT ccnt;
---
> 		register int j;
> 		unsigned short ccnt;
162,165c170,173
< 		ftime = ccnt;
< 		totime += ftime;
< 		if(ftime > maxtime)
< 			maxtime = ftime;
---
> 		ftim = ccnt;
> 		totime += ftim;
> 		if(ftim > maxtime)
> 			maxtime = ftim;
172c180
< 			nl[j].time += overlap*ftime/scale;
---
> 			nl[j].time += overlap*ftim/scale;
201c209
< 		ftime = ccnt;
---
> 		ftim = ccnt;
204c212
< 		lastsx -= 2000.*ftime/totime;
---
> 		lastsx -= 2000.*ftim/totime;
210c218
< 				lastx = -ftime*2000./maxtime;
---
> 				lastx = -ftim*2000./maxtime;
223c231
< 		ftime = np->time/totime;
---
> 		ftim = np->time/totime;
252c260
< 		ftime = np->time/totime;
---
> 		ftim = np->time/totime;
254c262
< 		printf("%8.8s%6.1f%9.2f", np->name, 100*ftime, actime/60);
---
> 		printf("%8.8s%6.1f%9.2f", np->name, 100*ftim, actime/60);
264,265c272
< min(a, b)
< unsigned a, b;
---
> int min(unsigned a, unsigned b)
272,273c279
< max(a, b)
< unsigned a, b;
---
> int max(unsigned a, unsigned b)
280,281c286
< valcmp(p1, p2)
< struct nl *p1, *p2;
---
> int valcmp(const void *vp1, const void *vp2)
282a288
> 	const struct nl *p1 = vp1, *p2 = vp2;
286,287c292
< timcmp(p1, p2)
< struct nl *p1, *p2;
---
> int timcmp(const void *vp1, const void *vp2)
288a294
> 	const struct nl *p1 = vp1, *p2 = vp2;
299c305
< done()
---
> int done(void)
308a315
> 	return(0);
```

### cmd/ps.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/ps.c unix-v7-c99/cmd/ps.c || true
```

Expect:

```
8c8,14
< #include <core.h>
---
> /* core.h is not present in this port; inline the three macros it
>  * defines (v7 PDP-11 values).  Feeds the user-text/data/stack
>  * address-map setup in prcom(); only meaningful when the port can
>  * read a user struct out of swap, which is best-effort. */
> #define TXTRNDSIZ 8192L
> #define stacktop(siz) (0x10000L)
> #define stackbas(siz) (0x10000L-siz)
10,11c16,21
< #include <sys/proc.h>
< #include <sys/tty.h>
---
> /* v7 kernel-internal headers live under h/ in this port. */
> #include "../h/proc.h"
> /* sys/tty.h is not needed by this source (no struct tty fields are
>  * touched here); a forward declaration is enough for the struct tty *
>  * member referenced through u.u_ttyp. */
> struct tty;
13c23
< #include <sys/user.h>
---
> #include "../h/user.h"
16,19c26,30
< 	{ "_proc" },
< 	{ "_swapdev" },
< 	{ "_swplo" },
< 	{ "" },
---
> 	{ "_proc",    0, 0 },
> 	{ "_swapdev", 0, 0 },
> 	{ "_swplo",   0, 0 },
> 	{ "_pcomm",   0, 0 },
> 	{ "",         0, 0 },
21a33,34
> static int cur_slot;	/* index of mproc within proc[]; passed to prcom indirectly */
> 
32,35c45,53
< long	lseek();
< char	*gettty();
< char	*getptr();
< char	*strncmp();
---
> long	lseek(int fd, long offset, int ptrname);
> char	*gettty(void);
> char	*getptr(char **adr);
> /* strncmp() is declared in <stdio.h> with the standard prototype in
>  * this port; the v7 K&R-era `char *strncmp()` line is dropped. */
> int	getdev(void);
> int	prcom(int puid);
> int	getbyte(char *adr);
> int	within(char *adr, long lbd, long ubd);
50,51c68,69
< main(argc, argv)
< char **argv;
---
> int
> main(int argc, char **argv)
145a164
> 		cur_slot = i;
154c173,174
< getdev()
---
> int
> getdev(void)
179,180c199,201
< 		fprintf(stderr, "Can't open /dev/swap\n");
< 		exit(1);
---
> 		/* /dev/swap is absent on the ARM port; ps still prints proc
> 		 * table entries, but cannot reach swapped-out user pages. */
> 		swap = -1;
181a203
> 	return(0);
185,186c207
< round(a, b)
< 	long		a, b;
---
> round(long a, long b)
199c220,221
< prcom(puid)
---
> int
> prcom(int puid)
211a234
> 	(void)lw;
241c264
< 			"0SWRIZT"[mproc.p_stat], puid);
---
> 			"0SWRIZT"[(unsigned char)mproc.p_stat], puid);
272a296,310
> 	/* For parked processes the live USERBASE window doesn't cover their
> 	 * UARGV buffer, so fall back to the per-slot pcomm[] table the
> 	 * kernel populates at exec() time.  The running ps has its own
> 	 * argv in UARGV and prefers that. */
> 	{
> 		char nb[16];
> 		lseek(swmem, (long)nl[3].n_value + (long)cur_slot * 16, 0);
> 		if (read(swmem, nb, 16) == 16) {
> 			nb[15] = '\0';
> 			if (nb[0] && mproc.p_size == 0) {
> 				printf(" %.15s", nb);
> 				return(1);
> 			}
> 		}
> 	}
277,281c315,332
< 	addr += ctob((long)mproc.p_size) - 512;
< 
< 	/* look for sh special */
< 	lseek(file, addr+512-sizeof(char **), 0);
< 	if (read(file, (char *)&ap, sizeof(char *)) != sizeof(char *))
---
> 	/* In real v7, p_addr*64 / p_size*64 describe the swap-clicks layout
> 	 * of a process's user struct + text/data/stack image, and the scan
> 	 * below walks the top of the user stack (where exec() laid out
> 	 * argv[]) byte by byte through a saved struct user{} address map.
> 	 *
> 	 * This port has no swap and only one live user image at a time
> 	 * (USERBASE..USERBASE+USERSIZE), with argv kept as a single
> 	 * NUL-terminated, space-separated buffer at the fixed user VA
> 	 * UARGV (see arch/arm.c::kexec2 / kspawn).  sys/v7_bridge.c::
> 	 * v7_proc_set_current() steers p_addr/p_size for the currently
> 	 * running proc at UARGV/UARGLEN respectively, so the lseek+read
> 	 * below lands directly on that buffer; every other proc gets
> 	 * p_size==0 and we just print pid/tty/time with no command.
> 	 *
> 	 * The "sh special" indirect-argv walk and the backward stack scan
> 	 * from the original v7 source are dropped: our argv buffer is a
> 	 * single contiguous C string, not a v7 user-stack layout. */
> 	if (mproc.p_size == 0)
283,302c334,337
< 	if (ap) {
< 		char b[82];
< 		char *bp = b;
< 		while((cp=getptr(ap++)) && cp && (bp<b+lw) ) {
< 			nbad = 0;
< 			while((c=getbyte(cp++)) && (bp<b+lw)) {
< 				if (c<' ' || c>'~') {
< 					if (nbad++>3)
< 						break;
< 					continue;
< 				}
< 				*bp++ = c;
< 			}
< 			*bp++ = ' ';
< 		}
< 		*bp++ = 0;
< 		printf(lflg?" %.30s":" %.60s", b);
< 		return(1);
< 	}
< 
---
> 	/* Read from the START of UARGV (where kargs lays out NUL-separated
> 	 * argv strings).  Original v7 read at addr+size-512 because v7 placed
> 	 * argv at the top of the user stack; in this port the buffer base is
> 	 * UARGV itself. */
306,332c341,351
< 	for (ip = (int *)&abuf[512]-2; ip > (int *)abuf; ) {
< 		if (*--ip == -1 || *ip==0) {
< 			cp = (char *)(ip+1);
< 			if (*cp==0)
< 				cp++;
< 			nbad = 0;
< 			for (cp1 = cp; cp1 < &abuf[512]; cp1++) {
< 				c = *cp1&0177;
< 				if (c==0)
< 					*cp1 = ' ';
< 				else if (c < ' ' || c > 0176) {
< 					if (++nbad >= 5) {
< 						*cp1++ = ' ';
< 						break;
< 					}
< 					*cp1 = '?';
< 				} else if (c=='=') {
< 					*cp1 = 0;
< 					while (cp1>cp && *--cp1!=' ')
< 						*cp1 = 0;
< 					break;
< 				}
< 			}
< 			while (*--cp1==' ')
< 				*cp1 = 0;
< 			printf(lflg?" %.30s":" %.60s", cp);
< 			return(1);
---
> 	abuf[sizeof(abuf)-1] = '\0';
> 	if (abuf[0] == '\0')
> 		return(1);
> 	/* argv args are NUL-separated; replace NULs between non-empty strings
> 	 * with spaces so the whole command line prints as one row.  Stop at
> 	 * the argv terminator (two NULs in a row -> empty-string sentinel). */
> 	{
> 		int z;
> 		for (z = 0; z < (int)sizeof(abuf) - 1; z++) {
> 			if (abuf[z] == '\0' && abuf[z+1] == '\0') { abuf[z] = '\0'; break; }
> 			if (abuf[z] == '\0') abuf[z] = ' ';
334a354,368
> 	/* Sanitize non-printables and trim trailing space so the line stays
> 	 * one row even if the in-kernel buffer had stale tail bytes. */
> 	for (cp = abuf; *cp; cp++) {
> 		c = *cp & 0177;
> 		if (c < ' ' || c > '~')
> 			*cp = '?';
> 	}
> 	while (cp > abuf && cp[-1] == ' ')
> 		*--cp = '\0';
> 	/* ip/cp1/ap/nbad/getbyte/within/getptr are inherited from the
> 	 * historical v7 argv-scan and become unused once we just print the
> 	 * raw argbuf; cast them to void so -Wunused stays quiet without
> 	 * disturbing the surrounding declarations. */
> 	(void)ap; (void)cp1; (void)ip; (void)nbad;
> 	printf(lflg?" %.30s":" %.60s", abuf);
339c373
< gettty()
---
> gettty(void)
341c375
< 	register i;
---
> 	register int i;
358,359c392
< getptr(adr)
< char **adr;
---
> getptr(char **adr)
363c396
< 	register i;
---
> 	register unsigned int i;
373,374c406,407
< getbyte(adr)
< char *adr;
---
> int
> getbyte(char *adr)
395,397c428,429
< within(adr,lbd,ubd)
< char *adr;
< long lbd, ubd;
---
> int
> within(char *adr, long lbd, long ubd)
399c431
< 	return((unsigned)adr>=lbd && (unsigned)adr<ubd);
---
> 	return((unsigned long)adr>=(unsigned long)lbd && (unsigned long)adr<(unsigned long)ubd);
```

### cmd/pstat.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/pstat.c unix-v7-c99/cmd/pstat.c || true
```

Expect:

```
5a6,12
> /* h/inode.h carries a v7-style `struct group` (the mpx multiplexer
>  * descriptor), which collides with libc's <grp.h> `struct group`
>  * (getgrent).  Suppress the libc form by predefining GRP_H before
>  * any libc header gets a chance to pull <grp.h>; pstat does not
>  * call getgr* and so does not need the POSIX struct. */
> #define GRP_H
> #include <stdio.h>
7,8c14,31
< #include <sys/conf.h>
< #include <sys/tty.h>
---
> /* sys/conf.h is unused by this source.  Pull kernel-internal headers
>  * from the in-tree h/ directory; this port keeps them there.  v7
>  * had these as in-function #includes (just to scope a few struct
>  * defs); C99 chokes on the file-scope `inode[]` / `mpxip` decls
>  * showing up as unused function-local variables, so they are hoisted
>  * to file scope here. */
> #include "../h/tty.h"
> #include "../h/inode.h"
> #include "../h/text.h"
> #include "../h/proc.h"
> #include <sys/dir.h>
> #include "../h/user.h"
> #include "../h/file.h"
> #include <sys/stat.h>
> 
> #include <a.out.h>		/* nlist() prototype */
> /* exit/open/read/lseek prototypes are pulled in via stdio.h on this
>  * port; no extra K&R-style declarations are needed here. */
20c43
< 	"_inode", 0, 0,
---
> 	{"_inode", 0, 0},
22c45
< 	"_text", 0, 0,
---
> 	{"_text", 0, 0},
24c47
< 	"_proc", 0, 0,
---
> 	{"_proc", 0, 0},
26c49
< 	"_dh11", 0, 0,
---
> 	{"_dh11", 0, 0},
28c51
< 	"_ndh11", 0, 0,
---
> 	{"_ndh11", 0, 0},
30c53
< 	"_kl11", 0, 0,
---
> 	{"_kl11", 0, 0},
32,33c55,56
< 	"_file", 0, 0,
< 	0,
---
> 	{"_file", 0, 0},
> 	{"", 0, 0},
45,46c68,79
< main(argc, argv)
< char **argv;
---
> int doinode(void);
> int dotext(void);
> int doproc(void);
> int dotty(void);
> int dousr(void);
> int dofil(void);
> int putf(int v, int n);
> int ttyprt(int n, struct tty *atp);
> int oatoi(char *s);
> 
> int
> main(int argc, char **argv)
92c125
< 	nlist(fnlist, setup);
---
> 	nlist(fnlist, (struct nlist *)setup);
108a142
> 	return(0);
111c145,146
< doinode()
---
> int
> doinode(void)
113d147
< #include <sys/inode.h>
148a183
> 	return(0);
151c186,187
< putf(v, n)
---
> int
> putf(int v, int n)
156a193
> 	return(0);
159c196,197
< dotext()
---
> int
> dotext(void)
161d198
< #include <sys/text.h>
164c201
< 	register loc;
---
> 	register int loc;
193a231
> 	return(0);
196c234,235
< doproc()
---
> int
> doproc(void)
198d236
< #include <sys/proc.h>
201c239
< 	register loc, np;
---
> 	register int loc, np;
233a272
> 	return(0);
236c275,276
< dotty()
---
> int
> dotty(void)
250c290
< 		return;
---
> 		return(0);
257a298
> 	return(0);
260,261c301,302
< ttyprt(n, atp)
< struct tty *atp;
---
> int
> ttyprt(int n, struct tty *atp)
283a325
> 	return(0);
286c328,329
< dousr()
---
> int
> dousr(void)
288,289d330
< #include <sys/dir.h>
< #include <sys/user.h>
295c336
< 	register i;
---
> 	register int i;
352a394
> 	return(0);
355,356c397,398
< oatoi(s)
< char *s;
---
> int
> oatoi(char *s)
358c400
< 	register v;
---
> 	register int v;
366c408,409
< dofil()
---
> int
> dofil(void)
368d410
< #include <sys/file.h>
371c413
< 	register nf;
---
> 	register int nf;
392a435
> 	return(0);
```

### cmd/sa.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sa.c unix-v7-c99/cmd/sa.c || true
```

Expect:

```
0a1,27
> /* sa(1) -- interpret command time accounting.
>  *
>  * Ported from v7/usr/src/cmd/sa.c with the minimum set of K&R -> C99
>  * edits needed to build under the project's strict cmd-build CFLAGS:
>  *
>  *   - Replaced the K&R-style function definitions with C99 prototypes
>  *     for the static helpers used inside this TU.
>  *   - Inlined the v7 sys/acct.h definitions (struct acct, AFORK).  The
>  *     port's include tree carries only kernel-side h/acct.h; userland
>  *     does not get a <sys/acct.h>, so the struct is reproduced here
>  *     instead of adding a new public header.
>  *   - Renamed the file-scope `struct user user[256]` to `usr[]` so it
>  *     does not shadow the kernel's struct user (the cmd build does not
>  *     include h/user.h, but keeping the name distinct is harmless and
>  *     reads more naturally).
>  *   - Switched the v7-only `getpw(uid, buf)` lookup in printmoney() to
>  *     getpwuid(), which is what this libc provides.  The fallback
>  *     printing path (numeric uid) is unchanged.
>  *   - Forward-declared the comparison functions and sum() with proper
>  *     prototypes so qsort()'s function-pointer arg type-checks against
>  *     stdio.h's declaration.
>  *
>  * Everything else (the hash-table enter() / cleanup pass / column()
>  * pretty-printer / expand() pseudo-float decode) is byte-for-byte from
>  * the v7 source.
>  */
> 
3c30
< #include <sys/acct.h>
---
> #include <sys/stat.h>
4a32
> #include <pwd.h>
6c34,75
< /* interpret command time accounting */
---
> /* Acct record layout.
>  *
>  * v7's h/acct.h declares comp_t (16-bit pseudo-float) fields for ac_utime,
>  * ac_stime, ac_etime, ac_io.  The kernel writei()s `&acctbuf` for
>  * `sizeof(acctbuf)` bytes; in this port `acctbuf` is the global declared
>  * in sys/v7stubs.c -- which uses *long* for utime/stime/etime and *short*
>  * for ac_io.  The on-disk record we read back here therefore mirrors that
>  * 44-byte struct, not h/acct.h's 36-byte one.
>  *
>  * (sys/acct.c::acct() truncates its writei() length to sizeof(acctbuf) as
>  * seen from sys/acct.c -- which sees h/acct.h's 36-byte struct via the
>  * include, so the *cut* is at byte 36.  That covers the 10-byte ac_comm,
>  * the 2-byte alignment pad, and the four 4-byte time fields, plus the
>  * three shorts ac_uid/ac_gid/ac_mem and the half of ac_io.  The kernel
>  * never writes ac_tty/ac_flag, so we read them as zero here.)
>  *
>  * comp_t pseudo-float decode is in expand(); ac_btime/ac_uid/ac_gid are
>  * passed through verbatim.  The wider-than-comp_t fields are still
>  * decoded with expand() because compress() in sys/acct.c emits the same
>  * pseudo-float (just zero-extended to a long here). */
> typedef	unsigned short comp_t;
> struct	acct {
> 	char	ac_comm[10];
> 	char	ac_pad[2];	/* alignment pad between ac_comm and ac_utime
> 				 * in sys/v7stubs.c's struct -- the kernel
> 				 * writes this byte-for-byte even though
> 				 * h/acct.h's matching field is comp_t. */
> 	long	ac_utime;
> 	long	ac_stime;
> 	long	ac_etime;
> 	time_t	ac_btime;
> 	short	ac_uid;
> 	short	ac_gid;
> 	short	ac_mem;
> 	short	ac_io;
> 	/* The kernel side never writes ac_tty / ac_flag: sys/acct.c::acct()
> 	 * caps writei() at sizeof(acctbuf) as seen through h/acct.h (36
> 	 * bytes), and that cut lands right after ac_io.  We don't carry
> 	 * the fields in this on-disk struct because their bytes are not
> 	 * actually persisted; the references below treat them as zero. */
> };
> #define	AFORK	01
27c96
< struct	user {
---
> struct	user_acct {
31c100
< } user[256];
---
> } usr[256];
47d115
< time_t	expand();
49,50c117,134
< main(argc, argv)
< char **argv;
---
> /* Forward declarations -- needed under C99 strict prototypes so qsort()
>  * and the inter-routine calls type-check. */
> extern int acct(char *);
> time_t expand(unsigned t);
> int tcmp(struct tab *p1, struct tab *p2);
> int ncmp(struct tab *p1, struct tab *p2);
> int bcmp(struct tab *p1, struct tab *p2);
> float sum(struct tab *p);
> void doacct(char *f);
> int enter(char *np);
> void init(void);
> void strip(void);
> void printmoney(void);
> void column(double n, double a, double b, double c);
> void col(double n, double a, double m);
> 
> int
> main(int argc, char **argv)
54,55d137
< 	extern tcmp(), ncmp(), bcmp();
< 	extern float sum();
135a218,235
> 	/* Force iupdat() of the acct file's in-core inode so armboot's
> 	 * loadino() / kopen() path reads the fresh i_size when we fopen()
> 	 * below.  The kernel writei() in sys/acct.c::acct() bumps the
> 	 * in-core i_size on every process exit, but it leaves IUPD set
> 	 * without writing the dinode block back -- iput() only iupdat()s
> 	 * the inode when its refcount drops to 1, and acctp holds an
> 	 * extra reference that never lets that happen while accounting
> 	 * stays on.
> 	 *
> 	 * Toggling accounting off-then-on takes that extra reference away
> 	 * (sysacct(NULL) iput()s acctp -> i_count drops to 1 -> iupdat()
> 	 * pushes the dinode), then the re-enable sysacct() re-namei()s
> 	 * the (now-flushed) inode so subsequent exits keep accruing.  The
> 	 * read path our fopen() drives next sees the post-iupdat() dinode
> 	 * via armboot's loadino(), and fread() walks all the records on
> 	 * disk. */
> 	(void)acct((char *)0);
> 	(void)acct("/usr/adm/acct");
143c243
< 		return;
---
> 		return 0;
156c256
< 		for(j=0; j<NC; j++)
---
> 		for(j=0; j<(int)NC; j++)
172c272
< 		for(j=0; j<NC; j++)
---
> 		for(j=0; j<(int)NC; j++)
183c283
< 			fwrite((char *)user, sizeof(user), 1, ff);
---
> 			fwrite((char *)usr, sizeof(usr), 1, ff);
202c302
< 	qsort(tab, k, sizeof(tab[0]), nflg? ncmp: (bflg?bcmp:tcmp));
---
> 	qsort((char *)tab, k, sizeof(tab[0]), nflg? ncmp: (bflg?bcmp:tcmp));
210a311
> 	return 0;
213c314,315
< printmoney()
---
> void
> printmoney(void)
215,217c317,318
< 	register i;
< 	char buf[128];
< 	register char *cp;
---
> 	int i;
> 	struct passwd *pw;
220,221c321,323
< 		if (user[i].ncomm) {
< 			if (getpw(i, buf)!=0)
---
> 		if (usr[i].ncomm) {
> 			pw = getpwuid(i);
> 			if (pw == NULL)
223,229c325,326
< 			else {
< 				cp = buf;
< 				while (*cp!=':' &&*cp!='\n' && *cp)
< 					cp++;
< 				*cp = 0;
< 				printf("%-8s", buf);
< 			}
---
> 			else
> 				printf("%-8s", pw->pw_name);
231c328
< 			    user[i].ncomm, user[i].fctime/60);
---
> 			    usr[i].ncomm, usr[i].fctime/60);
236,237c333,334
< column(n, a, b, c)
< double n, a, b, c;
---
> void
> column(double n, double a, double b, double c)
258,259c355,356
< col(n, a, m)
< double n, a, m;
---
> void
> col(double n, double a, double m)
272,273c369,370
< doacct(f)
< char *f;
---
> void
> doacct(char *f)
279,280c376,377
< 	register char *cp;
< 	register int c;
---
> 	char *cp;
> 	int c;
302c399
< 		if (fbuf.ac_flag&AFORK) {
---
> 		if (0/*fbuf.ac_flag*/&AFORK) {
316,317c413,414
< 		user[c].ncomm++;
< 		user[c].fctime += x/60.;
---
> 		usr[c].ncomm++;
> 		usr[c].fctime += x/60.;
334,335c431,432
< ncmp(p1, p2)
< struct tab *p1, *p2;
---
> int
> ncmp(struct tab *p1, struct tab *p2)
345,346c442,443
< bcmp(p1, p2)
< struct tab *p1, *p2;
---
> int
> bcmp(struct tab *p1, struct tab *p2)
349d445
< 	float sum();
365,366c461,463
< tcmp(p1, p2)
< struct tab *p1, *p2;
---
> 
> int
> tcmp(struct tab *p1, struct tab *p2)
368d464
< 	extern float sum();
386,387c482,483
< float sum(p)
< struct tab *p;
---
> float
> sum(struct tab *p)
397c493,494
< init()
---
> void
> init(void)
420c517
< 	fread((char *)user, sizeof(user), 1, f);
---
> 	fread((char *)usr, sizeof(usr), 1, f);
424,425c521,522
< enter(np)
< char *np;
---
> int
> enter(char *np)
429c526
< 	for (i=j=0; i<NC; i++) {
---
> 	for (i=j=0; i<(int)NC; i++) {
435c532
< 	for (i=j=0; j<NC; j++) {
---
> 	for (i=0, j=0; j<(int)NC; j++) {
441c538
< 		for (j=0; j<NC; j++)
---
> 		for (j=0; j<(int)NC; j++)
447c544
< 	for (j=0; j<NC; j++)
---
> 	for (j=0; j<(int)NC; j++)
453c550,551
< strip()
---
> void
> strip(void)
475,476c573
< expand(t)
< unsigned t;
---
> expand(unsigned t)
478c575
< 	register time_t nt;
---
> 	time_t nt;
```

### cmd/sed/sed.h

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sed/sed.h unix-v7-c99/cmd/sed/sed.h || true
```

Expect:

```
35,36c35,36
< union reptr	*abuf[ABUFSIZE];
< union reptr **aptr;
---
> struct reptr	*abuf[ABUFSIZE];
> struct reptr **aptr;
50c50
< union reptr	*ptrend;
---
> struct reptr	*ptrend;
63a64
> int	iflag;
104,107c105,112
< union	reptr {
< 	struct reptr1 {
< 		char	*ad1;
< 		char	*ad2;
---
> /* Strict C99: v7 sed had struct reptr { struct reptr1; struct reptr2; }
>  * where reptr1/reptr2 differed only by re1(char*)/lb1(reptr*) in one
>  * slot.  Collapsed to a single struct with a named inner union for that
>  * slot -- callers reach the slot via ipc->u.re1 / ipc->u.lb1. */
> struct reptr {
> 	char	*ad1;
> 	char	*ad2;
> 	union {
109,128c114,122
< 		char	*rhs;
< 		FILE	*fcode;
< 		char	command;
< 		char	gfl;
< 		char	pfl;
< 		char	inar;
< 		char	negfl;
< 	};
< 	struct reptr2 {
< 		char	*ad1;
< 		char	*ad2;
< 		union reptr	*lb1;
< 		char	*rhs;
< 		FILE	*fcode;
< 		char	command;
< 		char	gfl;
< 		char	pfl;
< 		char	inar;
< 		char	negfl;
< 	};
---
> 		struct reptr	*lb1;
> 	} u;
> 	char	*rhs;
> 	FILE	*fcode;
> 	char	command;
> 	char	gfl;
> 	char	pfl;
> 	char	inar;
> 	char	negfl;
136,137c130,131
< 	union reptr	*chain;
< 	union reptr	*address;
---
> 	struct reptr	*chain;
> 	struct reptr	*address;
151c145
< union reptr	**cmpend[DEPTH];
---
> struct reptr	**cmpend[DEPTH];
153c147
< union reptr	*pending;
---
> struct reptr	*pending;
```

### cmd/sed/sed0.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sed/sed0.c unix-v7-c99/cmd/sed/sed0.c || true
```

Expect:

```
3a4,9
> void	fcomp(void);
> void	dechain(void);
> void	execute(char *file);
> int	rline(char *lbuf);
> int	cmp(char *a, char *b);
> 
21,22c27,28
< main(argc, argv)
< char	*argv[];
---
> int
> main(int argc, char *argv[])
79a86,89
> 		case 'i':
> 			iflag++;
> 			continue;
> 
105c115
< /*	abort();	/*DEBUG*/
---
> /*	abort();	DEBUG */
110c120,140
< 		execute(*eargv++);
---
> 		char *src = *eargv++;
> 		if(iflag && src) {
> 			char tmpname[256];
> 			int i, n = 0;
> 			for(i = 0; src[i] && n < 240; i++) tmpname[n++] = src[i];
> 			tmpname[n++] = '.'; tmpname[n++] = 's'; tmpname[n++] = 'e';
> 			tmpname[n++] = 'd'; tmpname[n++] = 't'; tmpname[n++] = 'm';
> 			tmpname[n++] = 'p'; tmpname[n] = '\0';
> 			if(freopen(tmpname, "w", stdout) == NULL) {
> 				fprintf(stderr, "sed: can't write %s\n", tmpname);
> 				continue;
> 			}
> 			fcode[0] = stdout;
> 			execute(src);
> 			fflush(stdout);
> 			unlink(src);
> 			link(tmpname, src);
> 			unlink(tmpname);
> 		} else {
> 			execute(src);
> 		}
115c145,146
< fcomp()
---
> void
> fcomp(void)
119,120c150,151
< 	char	*address();
< 	union reptr	*pt, *pt1;
---
> 	char	*address(char *expbuf);
> 	struct reptr	*pt, *pt1;
143c174
< /*	fprintf(stdout, "cp: %s\n", cp);	/*DEBUG*/
---
> /*	fprintf(stdout, "cp: %s\n", cp);	DEBUG */
210c241
< 				cmpend[depth++] = &rep->lb1;
---
> 				cmpend[depth++] = &rep->u.lb1;
261c292
< 				if(lpt = search(lab)) {
---
> 				if((lpt = search(lab))) {
290,291c321,322
< 				rep->re1 = p;
< 				p = text(rep->re1);
---
> 				rep->u.re1 = p;
> 				p = text(rep->u.re1);
300,301c331,332
< 				rep->re1 = p;
< 				p = text(rep->re1);
---
> 				rep->u.re1 = p;
> 				p = text(rep->u.re1);
314,315c345,346
< 				rep->re1 = p;
< 				p = text(rep->re1);
---
> 				rep->u.re1 = p;
> 				p = text(rep->u.re1);
345,346c376,377
< 					if(pt = labtab->chain) {
< 						while(pt1 = pt->lb1)
---
> 					if((pt = labtab->chain)) {
> 						while((pt1 = pt->u.lb1))
348c379
< 						pt->lb1 = rep;
---
> 						pt->u.lb1 = rep;
362c393
< 				if(lpt = search(lab)) {
---
> 				if((lpt = search(lab))) {
364c395
< 						rep->lb1 = lpt->address;
---
> 						rep->u.lb1 = lpt->address;
367c398
< 						while(pt1 = pt->lb1)
---
> 						while((pt1 = pt->u.lb1))
369c400
< 						pt->lb1 = rep;
---
> 						pt->u.lb1 = rep;
407,408c438,439
< 				rep->re1 = p;
< 				p = text(rep->re1);
---
> 				rep->u.re1 = p;
> 				p = text(rep->u.re1);
417c448
< 				rep->lb1 = ptrspace;
---
> 				rep->u.lb1 = ptrspace;
435,436c466,467
< 				rep->re1 = p;
< 				p = compile(rep->re1);
---
> 				rep->u.re1 = p;
> 				p = compile(rep->u.re1);
441,442c472,473
< 				if(p == rep->re1) {
< 					rep->re1 = op;
---
> 				if(p == rep->u.re1) {
> 					rep->u.re1 = op;
444c475
< 					op = rep->re1;
---
> 					op = rep->u.re1;
529,530c560,561
< 				rep->re1 = p;
< 				p = ycomp(rep->re1);
---
> 				rep->u.re1 = p;
> 				p = ycomp(rep->u.re1);
588,589c619,620
< char *compile(expbuf)
< char	*expbuf;
---
> char *
> compile(char *expbuf)
591c622
< 	register c;
---
> 	register int c;
749,750c780,781
< rline(lbuf)
< char	*lbuf;
---
> int
> rline(char *lbuf)
753c784
< 	register	t;
---
> 	register int	t;
764c795
< 			while(*++p = *q++) {
---
> 			while((*++p = *q++)) {
783c814
< 		while(*++p = *q++) {
---
> 		while((*++p = *q++)) {
816,817c847,848
< char	*address(expbuf)
< char	*expbuf;
---
> char	*
> address(char *expbuf)
855,856c886,887
< cmp(a, b)
< char	*a,*b;
---
> int
> cmp(char *a, char *b)
863c894
< 	while(*++ra == *++rb)
---
> 	while ((*++ra == *++rb))
908c939,940
< dechain()
---
> void
> dechain(void)
911c943
< 	union reptr	*rptr, *trptr;
---
> 	struct reptr	*rptr, *trptr;
922,923c954,955
< 			while(trptr = rptr->lb1) {
< 				rptr->lb1 = lptr->address;
---
> 			while((trptr = rptr->u.lb1)) {
> 				rptr->u.lb1 = lptr->address;
926c958
< 			rptr->lb1 = lptr->address;
---
> 			rptr->u.lb1 = lptr->address;
931,932c963,964
< char *ycomp(expbuf)
< char	*expbuf;
---
> char *
> ycomp(char *expbuf)
952,953c984,985
< 		if((ep[c] = *tsp++) == '\\' && *tsp == 'n') {
< 			ep[c] = '\n';
---
> 		if((ep[(unsigned char)c] = *tsp++) == '\\' && *tsp == 'n') {
> 			ep[(unsigned char)c] = '\n';
956c988
< 		if(ep[c] == seof || ep[c] == '\0')
---
> 		if(ep[(unsigned char)c] == seof || ep[(unsigned char)c] == '\0')
964,965c996,997
< 		if(ep[c] == 0)
< 			ep[c] = c;
---
> 		if(ep[(unsigned char)c] == 0)
> 			ep[(unsigned char)c] = c;
```

### cmd/sed/sed1.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sed/sed1.c unix-v7-c99/cmd/sed/sed1.c || true
```

Expect:

```
3a4,10
> void	dosub(char *rhsbuf);
> void	command(struct reptr *ipc);
> void	arout(void);
> int	match(char *expbuf, int gf);
> int	advance(char *alp, char *aep);
> int	ecmp(char *a, char *b, int count);
> 
39,40c46,47
< execute(file)
< char *file;
---
> void
> execute(char *file)
43c50
< 	register union reptr	*ipc;
---
> 	register struct reptr	*ipc;
136c143
< 				if((ipc = ipc->lb1) == 0) {
---
> 				if((ipc = ipc->u.lb1) == 0) {
158,159c165,166
< match(expbuf, gf)
< char	*expbuf;
---
> int
> match(char *expbuf, int gf)
167c174
< 		while(*p1++ = *p2++);
---
> 		while((*p1++ = *p2++));
205,206c212,213
< advance(alp, aep)
< char	*alp, *aep;
---
> int
> advance(char *alp, char *aep)
213c220
< /*fprintf(stderr, "*lp = %c, %o\n*ep = %c, %o\n", *lp, *lp, *ep, *ep);	/*DEBUG*/
---
> /*fprintf(stderr, "*lp = %c, %o\n*ep = %c, %o\n", *lp, *lp, *ep, *ep);	DEBUG */
248c255
< 		braslist[*ep++] = lp;
---
> 		braslist[(unsigned char)*ep++] = lp;
252c259
< 		braelist[*ep++] = lp;
---
> 		braelist[(unsigned char)*ep++] = lp;
256,257c263,264
< 		bbeg = braslist[*ep];
< 		ct = braelist[*ep++] - bbeg;
---
> 		bbeg = braslist[(unsigned char)*ep];
> 		ct = braelist[(unsigned char)*ep++] - bbeg;
266,267c273,274
< 		bbeg = braslist[*ep];
< 		ct = braelist[*ep++] - bbeg;
---
> 		bbeg = braslist[(unsigned char)*ep];
> 		ct = braelist[(unsigned char)*ep++] - bbeg;
286c293
< 		while (*lp++ == *ep);
---
> 		while ((*lp++ == *ep));
315c322
< 			c = *(braslist[ep[1]]);
---
> 			c = *(braslist[(unsigned char)ep[1]]);
336,337c343,344
< substitute(ipc)
< union reptr	*ipc;
---
> int
> substitute(struct reptr *ipc)
339c346
< 	if(match(ipc->re1, 0) == 0)	return(0);
---
> 	if(match(ipc->u.re1, 0) == 0)	return(0);
346c353
< 			if(match(ipc->re1, 1) == 0) break;
---
> 			if(match(ipc->u.re1, 1) == 0) break;
353,354c360,361
< dosub(rhsbuf)
< char	*rhsbuf;
---
> void
> dosub(char *rhsbuf)
364c371
< 	while(c = *rp++) {
---
> 	while((c = *rp++)) {
378c385
< 	while (*sp++ = *lp++)
---
> 	while ((*sp++ = *lp++))
384c391
< 	while (*lp++ = *sp++);
---
> 	while ((*lp++ = *sp++));
387,388c394,395
< char	*place(asp, al1, al2)
< char	*asp, *al1, *al2;
---
> char	*
> place(char *asp, char *al1, char *al2)
403,404c410,411
< command(ipc)
< union reptr	*ipc;
---
> void
> command(struct reptr *ipc)
425c432
< 				for(p1 = ipc->re1; *p1; )
---
> 				for(p1 = ipc->u.re1; *p1; )
444c451
< 			while(*p2++ = *p1++);
---
> 			while((*p2++ = *p1++));
456c463
< 			while(*p1++ = *p2++);
---
> 			while((*p1++ = *p2++));
464c471
< 			while(*p1++ = *p2++)
---
> 			while((*p1++ = *p2++))
473c480
< 			while(*p1++ = *p2++);
---
> 			while((*p1++ = *p2++));
481c488
< 			while(*p1++ = *p2++)
---
> 			while((*p1++ = *p2++))
488c495
< 			for(p1 = ipc->re1; *p1; )
---
> 			for(p1 = ipc->u.re1; *p1; )
505c512
< 						while(*p2++ = *p3++)
---
> 						while((*p2++ = *p3++))
523c530
< 					while(*p2++ = *p3++)
---
> 					while((*p2++ = *p3++))
599c606
< 			if(ipc->pfl && i)
---
> 			if(ipc->pfl && i) {
604a612
> 			}
624c632
< 			while(*p2++ = *p1++);
---
> 			while((*p2++ = *p1++));
627c635
< 			while(*p2++ = *p1++);
---
> 			while((*p2++ = *p1++));
631c639
< 			while(*p2++ = *p1++);
---
> 			while((*p2++ = *p1++));
637,638c645,646
< 			p2 = ipc->re1;
< 			while(*p1 = p2[*p1])	p1++;
---
> 			p2 = ipc->u.re1;
> 			while((*p1 = p2[(unsigned char)*p1]))	p1++;
645,646c653
< gline(addr)
< char	*addr;
---
> gline(char *addr)
649c656
< 	register	c;
---
> 	register int	c;
661c668
< 			if(p2 >=  ebp) {
---
> 			if(f != 0 && p2 >=  ebp) {
683,684c690,691
< ecmp(a, b, count)
< char	*a, *b;
---
> int
> ecmp(char *a, char *b, int count)
691c698,699
< arout()
---
> void
> arout(void)
701c709
< 			for(p1 = (*aptr)->re1; *p1; )
---
> 			for(p1 = (*aptr)->u.re1; *p1; )
705c713
< 			if((fi = fopen((*aptr)->re1, "r")) == NULL)
---
> 			if((fi = fopen((*aptr)->u.re1, "r")) == NULL)
717d724
< 
```

### cmd/tc.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/tc.c unix-v7-c99/cmd/tc.c || true
```

Expect:

```
8c8
< #define	oput(c) if (pgskip==0) putchar(c); else;
---
> #define	oput(c) do { if (pgskip==0) putchar(c); } while (0)
57,59c57,68
< main(argc,argv)
< int argc;
< char **argv;
---
> int lig(char *x);
> int init(void);
> int ex(void);
> int kwait(void);
> int callunix(char line[]);
> int readch(void);
> int sendpt(void);
> int tcatoi(void);
> int getch(void);
> long tscale(int n);
> 
> int main(int argc, char **argv)
61c70
< 	register i, j;
---
> 	register int i, j;
63c72
< 	extern ex();
---
> 	extern int ex(void);
70c79
< 				if(i = atoi())pl = i/3;
---
> 				if((i = tcatoi()))pl = i/3;
78c87
< 				pgskip = atoi();
---
> 				pgskip = tcatoi();
83,84c92,93
< 				if(i = atoi())mpy = i;
< 				if(i = atoi())div = i;
---
> 				if((i = tcatoi()))mpy = i;
> 				if((i = tcatoi()))div = i;
94,95c103,104
< 	sigint = signal(SIGINT, ex);
< 	sigquit = signal(SIGQUIT, SIG_IGN);
---
> 	sigint = (int(*)())signal(SIGINT, (int)ex);
> 	sigquit = (int(*)())signal(SIGQUIT, (int)SIG_IGN);
226,227c235
< lig(x)
< char *x;
---
> int lig(char *x)
229c237
< 	register i, j;
---
> 	register int i, j;
245a254
> 	return(0);
247c256
< init(){
---
> int init(void){
261a271
> 	return(0);
263c273
< ex(){
---
> int ex(void){
271a282
> 	return(0);
273c284
< kwait(){
---
> int kwait(void){
275c286
< 	if(pgskip) return;
---
> 	if(pgskip) return(0);
290c301
< 				pgskip = atoi() + 1;
---
> 				pgskip = tcatoi() + 1;
298c309,310
< 	else	return;
---
> 	else	return(0);
> 	return(0);
300,301c312
< callunix(line)
< char line[];
---
> int callunix(char line[])
305c316
< 		signal(SIGINT,sigint); signal(SIGQUIT,sigquit);
---
> 		signal(SIGINT,(int)sigint); signal(SIGQUIT,(int)sigquit);
311,312c322,323
< 		return;
< 	else{	signal(SIGINT, SIG_IGN); signal(SIGQUIT, SIG_IGN);
---
> 		return(0);
> 	else{	signal(SIGINT, (int)SIG_IGN); signal(SIGQUIT, (int)SIG_IGN);
314c325
< 		signal(SIGINT,ex); signal(SIGQUIT,sigquit);
---
> 		signal(SIGINT,(int)ex); signal(SIGQUIT,(int)sigquit);
315a327
> 	return(0);
317c329
< readch(){
---
> int readch(void){
322c334
< sendpt(){
---
> int sendpt(void){
327c339
< 	xb = ((xx & 03) + ((yy<<2) & 014) & 017);
---
> 	xb = (((xx & 03) + ((yy<<2) & 014)) & 017);
343c355
< 	return;
---
> 	return(0);
345c357
< atoi()
---
> int tcatoi(void)
347c359
< 	register i, j, acc;
---
> 	register int i, j, acc;
350d361
< 	long tscale();
376,377c387
< long tscale(n)
< int n;
---
> long tscale(int n)
379c389
< 	register i, j;
---
> 	register int i, j;
403,404c413,414
< getch(){
< 	register i;
---
> int getch(void){
> 	register int i;
414c424
< char *asctab[128] {
---
> char *asctab[128] = {
```

### include/a.out.h

Local test:

```
diff unix-v7-c99/v7/usr/include/a.out.h unix-v7-c99/include/a.out.h || true
```

Expect:

```
33a34,35
> 
> int	nlist(char *, struct nlist *);
```

### include/ar.h

Local test:

```
diff unix-v7-c99/v7/usr/include/ar.h unix-v7-c99/include/ar.h || true
```

Expect:

```
```

### include/math.h

Local test:

```
diff unix-v7-c99/v7/usr/include/math.h unix-v7-c99/include/math.h || true
```

Expect:

```
1,7c1,29
< extern double fabs(), floor(), ceil(), fmod(), ldexp();
< extern double sqrt(), hypot(), atof();
< extern double sin(), cos(), tan(), asin(), acos(), atan(), atan2();
< extern double exp(), log(), log10(), pow();
< extern double sinh(), cosh(), tanh();
< extern double gamma();
< extern double j0(), j1(), jn(), y0(), y1(), yn();
---
> extern double fabs(double x);
> extern double floor(double x);
> extern double ceil(double x);
> extern double fmod(double x, double y);
> extern double ldexp(double x, int n);
> extern double sqrt(double x);
> extern double hypot(double x, double y);
> extern double atof(char *s);
> extern double sin(double x);
> extern double cos(double x);
> extern double tan(double x);
> extern double asin(double x);
> extern double acos(double x);
> extern double atan(double x);
> extern double atan2(double y, double x);
> extern double exp(double x);
> extern double log(double x);
> extern double log10(double x);
> extern double pow(double x, double y);
> extern double sinh(double x);
> extern double cosh(double x);
> extern double tanh(double x);
> extern double gamma(double x);
> extern double j0(double x);
> extern double j1(double x);
> extern double jn(int n, double x);
> extern double y0(double x);
> extern double y1(double x);
> extern double yn(int n, double x);
```

### include/stdio.h

Local test:

```
diff unix-v7-c99/v7/usr/include/stdio.h unix-v7-c99/include/stdio.h || true
```

Expect:

```
0a1,18
> /*
>  * stdio.h --- v7's stdio.h plus the small set of libc extern
>  * declarations the unix-v7-c99 commands lean on.  The historical
>  * stdio defs (struct _iobuf, getc/putc macros, fopen/freopen/...)
>  * are byte-identical to v7/usr/include/stdio.h; everything below
>  * the v7 block is the ad-hoc catch-all the port still needs while
>  * the rest of libc migrates out of u.h.
>  */
> #ifndef STDIO_H
> #define STDIO_H
> 
> #include <stdarg.h>
> #include <sys/types.h>
> #include <sys/stat.h>
> #include <sys/dir.h>
> #include <grp.h>		/* defines GRP_H, which gates the union-laden
> 				 * struct inode block in sys/inode.h */
> 
21a40
> #ifndef NULL
22a42
> #endif
37,41c57,198
< FILE	*fopen();
< FILE	*freopen();
< FILE	*fdopen();
< long	ftell();
< char	*fgets();
---
> FILE	*fopen(char *name, char *mode);
> FILE	*freopen(char *name, char *mode, FILE *f);
> FILE	*fdopen(int fd, char *mode);
> long	ftell(FILE *f);
> char	*fgets(char *s, int n, FILE *f);
> 
> /* -- below this line: declarations the c99 port adds to mirror what
>  * u.h used to inline.  Will shrink as libc grows real .c ports. */
> 
> #define	O_RDONLY	0
> 
> 
> int syscall3(int n, int a, int b, int c);
> 
> /* syscall stubs in sys.s */
> int read(int fd, char *buf, int n);
> int write(int fd, char *buf, int n);
> int open(char *path, int mode);
> int close(int fd);
> int creat(char *path, int mode);
> int unlink(char *path);
> int link(char *from, char *to);
> int access(char *path, int mode);
> int chdir(char *path);
> int chmod(char *path, int mode);
> int chown(char *path, int uid, int gid);
> int mknod(char *path, int mode, int dev);
> int utime(char *path, long *times);
> long lseek(int fd, long off, int whence);
> int stat(char *path, struct stat *st);
> int fstat(int fd, struct stat *st);
> int fork(void);
> int wait(int *status);
> int execve(char *path, char **argv, char **envp);
> int execv(char *path, char **argv);
> int execl(char *path, char *arg0, ...);
> int execvp(char *name, char **argv);
> int execlp(char *name, char *arg0, ...);
> void exit(int n) __attribute__((__noreturn__));
> void _exit(int n) __attribute__((__noreturn__));
> void abort(void) __attribute__((__noreturn__));
> int dup();		/* dup(fd) or dup(fd|0100, newfd); kept unprototyped because callers pass 1 or 2 args */
> int pipe(int *fd);
> int getuid(void);
> int setuid(int uid);
> int getgid(void);
> int setgid(int gid);
> int getpid(void);
> int umask(int n);
> int sync(void);
> int kill(int pid, int sig);
> /* signal()'s second argument is a function pointer or the special values
>  * SIG_DFL/SIG_IGN; left unprototyped to accept both function pointers and
>  * the integer sentinels without forcing casts at every call site. */
> int signal();
> int alarm(int n);
> int pause(void);
> int nice(int incr);
> int gtty(int fd, void *buf);
> int stty(int fd, void *buf);
> int ioctl(int fd, int cmd, char *arg);
> int mount(char *special, char *dir, int ro);
> int umount(char *special);
> int sigreturn(int *frame);
> 
> /* time */
> struct tm;
> struct timeb;
> int time(long *t);
> int stime(long *t);
> int times();		/* arg may be long * or struct tms * */
> int ftime(struct timeb *t);
> struct tm *gmtime(long *t);
> struct tm *localtime(long *t);
> char *asctime(struct tm *t);
> char *ctime(long *t);
> int dysize(int y);
> 
> /* stdio externs */
> int fclose(FILE *f);
> int fseek(FILE *f, long off, int whence);
> void rewind(FILE *f);
> void setbuf(FILE *f, char *buf);
> int fgetc(FILE *f);
> int fputc(int c, FILE *f);
> int fread(char *buf, unsigned size, unsigned n, FILE *f);
> int fwrite(char *buf, unsigned size, unsigned n, FILE *f);
> char *gets(char *buf);
> int puts();		/* v7 had no prototype -- many callers pass FILE* as a stray 2nd arg */
> int fputs(char *s, FILE *f);
> int ungetc(int c, FILE *f);
> int fflush(FILE *f);
> int _filbuf(FILE *f);
> int _flsbuf(int c, FILE *f);
> int printf(char *fmt, ...);
> int fprintf(FILE *f, char *fmt, ...);
> char *sprintf(char *buf, char *fmt, ...);
> int fscanf(FILE *f, char *fmt, ...);
> int sscanf(char *str, char *fmt, ...);
> int system(char *s);
> void perror(char *s);
> 
> /* extras */
> int isatty(int fd);
> unsigned int sleep(unsigned n);
> char *mktemp(char *s);
> char *getenv(char *name);
> extern char **environ;
> char *getlogin(void);
> char *getpass(char *prompt);
> char *ttyname(int fd);
> char *crypt(char *key, char *salt);
> char *strncat(char *s1, char *s2, int n);
> int ttyslot(void);
> int strlen(char *s);
> int strcmp(char *a, char *b);
> char *strcpy(char *a, char *b);
> char *strcat(char *a, char *b);
> char *strncpy(char *a, char *b, int n);
> int strncmp(char *a, char *b, int n);
> char *index(char *s, int c);
> char *rindex(char *s, int c);
> int atoi(char *s);
> long atol(char *s);
> double atof(char *s);
> void srand(unsigned int x);
> int rand(void);
> /* compar kept unprototyped: v7 callers pass (char *, char *), (void *,
>  * void *), and (struct lbuf **, struct lbuf **) variants. */
> void qsort(void *base, unsigned n, int size, int (*compar)());
> char *malloc(unsigned n);
> void free(char *p);
> char *realloc(char *p, unsigned n);
> char *calloc(unsigned num, unsigned size);
> void swab(char *from, char *to, int n);
> /* sbrk/brk: not declared here -- callers (sort.c) declare them with
>  * their own preferred type; the actual stubs live in lib/compat.c */
> int getargs(char **argv, int maxarg);
> long tell(int f);
> char *timezone(int zone, int dst);
> 
> #endif
```

### include/tp_defs.h

Local test:

```
diff unix-v7-c99/v7/usr/include/tp_defs.h unix-v7-c99/include/tp_defs.h || true
```

Expect:

```
```

### lib/ecvt.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/ecvt.c unix-v7-c99/lib/ecvt.c || true
```

Expect:

```
8c8
< char	*cvt();
---
> static char *cvt(double, int, int *, int *, int);
12,14c12
< ecvt(arg, ndigits, decpt, sign)
< double arg;
< int ndigits, *decpt, *sign;
---
> ecvt(double arg, int ndigits, int *decpt, int *sign)
20,22c18
< fcvt(arg, ndigits, decpt, sign)
< double arg;
< int ndigits, *decpt, *sign;
---
> fcvt(double arg, int ndigits, int *decpt, int *sign)
28,30c24
< cvt(arg, ndigits, decpt, sign, eflag)
< double arg;
< int ndigits, *decpt, *sign;
---
> cvt(double arg, int ndigits, int *decpt, int *sign, int eflag)
36c30
< 	double modf();
---
> 	double modf(double value, double *iptr);
```

### lib/fdopen.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/fdopen.c unix-v7-c99/lib/fdopen.c || true
```

Expect:

```
11,12c11
< fdopen(fd, mode)
< 	register char *mode;
---
> fdopen(int fd, register char *mode)
15c14
< 	FILE *_findiop();
---
> 	FILE *_findiop(void);
30c29
< 		/* No break */
---
> 		/* fallthrough */
```

### lib/gcvt.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/gcvt.c unix-v7-c99/lib/gcvt.c || true
```

Expect:

```
6c6
< char	*ecvt();
---
> char	*ecvt(double arg, int ndigits, int *decpt, int *sign);
9,11c9
< gcvt(number, ndigit, buf)
< double number;
< char *buf;
---
> gcvt(double number, int ndigit, char *buf)
15c13
< 	register i;
---
> 	register int i;
23,24c21,22
< 	if (decpt >= 0 && decpt-ndigit > 4
< 	 || decpt < 0 && decpt < -3) { /* use E-style */
---
> 	if ((decpt >= 0 && decpt-ndigit > 4)
> 	 || (decpt < 0 && decpt < -3)) { /* use E-style */
```

### lib/getgrent.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/getgrent.c unix-v7-c99/lib/getgrent.c || true
```

Expect:

```
15c15,16
< setgrent()
---
> void
> setgrent(void)
23c24,25
< endgrent()
---
> void
> endgrent(void)
32,34c34
< grskip(p,c)
< register char *p;
< register c;
---
> grskip(register char *p, register int c)
42c42
< getgrent()
---
> getgrent(void)
```

### lib/getgrgid.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/getgrgid.c unix-v7-c99/lib/getgrgid.c || true
```

Expect:

```
4,5c4
< getgrgid(gid)
< register gid;
---
> getgrgid(register int gid)
8d6
< 	struct group *getgrent();
```

### lib/getgrnam.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/getgrnam.c unix-v7-c99/lib/getgrnam.c || true
```

Expect:

```
0a1
> #include <stdio.h>
4,5c5
< getgrnam(name)
< register char *name;
---
> getgrnam(register char *name)
8d7
< 	struct group *getgrent();
```

### lib/getw.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/getw.c unix-v7-c99/lib/getw.c || true
```

Expect:

```
3,4c3,4
< getw(iop)
< register struct _iobuf *iop;
---
> int
> getw(register struct _iobuf *iop)
6c6
< 	register i;
---
> 	register int i;
```

### lib/putw.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/putw.c unix-v7-c99/lib/putw.c || true
```

Expect:

```
3,5c3,4
< putw(i, iop)
< register i;
< register struct _iobuf *iop;
---
> int
> putw(register int i, register struct _iobuf *iop)
8a8
> 	return(i);
```

### libm/asin.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libm/asin.c unix-v7-c99/libm/asin.c || true
```

Expect:

```
10,11c10,11
< double atan();
< double sqrt();
---
> double atan(double);
> double sqrt(double);
15c15
< asin(arg) double arg; {
---
> asin(double arg) {
40c40
< acos(arg) double arg; {
---
> acos(double arg) {
```

### libm/atan.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libm/atan.c unix-v7-c99/libm/atan.c || true
```

Expect:

```
17c17
< double static sq2p1	 =2.414213562373095048802e0;
---
> static double sq2p1	 =2.414213562373095048802e0;
31a32,34
> static double satan(double);
> static double xatan(double);
> 
39,40c42
< atan(arg)
< double arg;
---
> atan(double arg)
42,43d43
< 	double satan();
< 
57,58c57
< atan2(arg1,arg2)
< double arg1,arg2;
---
> atan2(double arg1, double arg2)
60,61d58
< 	double satan();
< 
82,83c79
< satan(arg)
< double arg;
---
> satan(double arg)
85,86d80
< 	double	xatan();
< 
101,102c95
< xatan(arg)
< double arg;
---
> xatan(double arg)
```

### libm/exp.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libm/exp.c unix-v7-c99/libm/exp.c || true
```

Expect:

```
21a22,24
> extern double floor(double);
> extern double ldexp(double, int);
> 
23,24c26
< exp(arg)
< double arg;
---
> exp(double arg)
```

### libm/fabs.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libm/fabs.c unix-v7-c99/libm/fabs.c || true
```

Expect:

```
2,3c2
< fabs(arg)
< double arg;
---
> fabs(double arg)
```

### libm/floor.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libm/floor.c unix-v7-c99/libm/floor.c || true
```

Expect:

```
6c6
< double	modf();
---
> double	modf(double, double *);
9,10c9
< floor(d)
< double d;
---
> floor(double d)
26,27c25
< ceil(d)
< double d;
---
> ceil(double d)
```

### libm/hypot.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libm/hypot.c unix-v7-c99/libm/hypot.c || true
```

Expect:

```
6c6
< double sqrt();
---
> double sqrt(double);
8,9c8
< hypot(a,b)
< double a,b;
---
> hypot(double a, double b)
35,36c34
< cabs(arg)
< struct complex arg;
---
> cabs(struct complex arg)
38c36
< 	double hypot();
---
> 	double hypot(double, double);
```

### libm/j0.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libm/j0.c unix-v7-c99/libm/j0.c || true
```

Expect:

```
42a43,44
> static void asympt(double);
> 
129c131
< j0(arg) double arg;{
---
> j0(double arg){
131c133
< 	double sin(), cos(), sqrt();
---
> 	double sin(double), cos(double), sqrt(double);
149c151
< y0(arg) double arg;{
---
> y0(double arg){
151c153
< 	double sin(), cos(), sqrt(), log(), j0();
---
> 	double sin(double), cos(double), sqrt(double), log(double), j0(double);
172,173c174
< static
< asympt(arg) double arg;{
---
> static void asympt(double arg){
```

### libm/j1.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libm/j1.c unix-v7-c99/libm/j1.c || true
```

Expect:

```
42a43,44
> static void asympt(double);
> 
131c133
< j1(arg) double arg;{
---
> j1(double arg){
133c135
< 	double sin(), cos(), sqrt();
---
> 	double sin(double), cos(double), sqrt(double);
154c156
< y1(arg) double arg;{
---
> y1(double arg){
156c158
< 	double sin(), cos(), sqrt(), log(), j1();
---
> 	double sin(double), cos(double), sqrt(double), log(double), j1(double);
178,179c180,181
< static
< asympt(arg) double arg;{
---
> static void
> asympt(double arg){
```

### libm/jn.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libm/jn.c unix-v7-c99/libm/jn.c || true
```

Expect:

```
39c39
< jn(n,x) int n; double x;{
---
> jn(int n, double x){
43c43
< 	double j0(), j1();
---
> 	double j0(double), j1(double);
81c81
< yn(n,x) int n; double x;{
---
> yn(int n, double x){
85c85
< 	double y0(), y1();
---
> 	double y0(double), y1(double);
```

### libm/log.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libm/log.c unix-v7-c99/libm/log.c || true
```

Expect:

```
14c14
< double	frexp();
---
> double	frexp(double, int *);
27,28c27
< log(arg)
< double arg;
---
> log(double arg)
57,58c56
< log10(arg)
< double arg;
---
> log10(double arg)
```

### libm/pow.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libm/pow.c unix-v7-c99/libm/pow.c || true
```

Expect:

```
8c8
< double log(), exp();
---
> double log(double), exp(double);
11,12c11
< pow(arg1,arg2)
< double arg1, arg2;
---
> pow(double arg1, double arg2)
```

### libm/sin.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libm/sin.c unix-v7-c99/libm/sin.c || true
```

Expect:

```
18a19,20
> static double sinus(double, int);
> 
20,21c22
< cos(arg)
< double arg;
---
> cos(double arg)
23d23
< 	double sinus();
30,31c30
< sin(arg)
< double arg;
---
> sin(double arg)
33d31
< 	double sinus();
38,40c36
< sinus(arg, quad)
< double arg;
< int quad;
---
> sinus(double arg, int quad)
42c38
< 	double modf();
---
> 	double modf(double, double *);
```

### libm/sinh.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libm/sinh.c unix-v7-c99/libm/sinh.c || true
```

Expect:

```
15c15
< double	exp();
---
> double	exp(double);
26,27c26
< sinh(arg)
< double arg;
---
> sinh(double arg)
30c29
< 	register sign;
---
> 	register int sign;
57,58c56
< cosh(arg)
< double arg;
---
> cosh(double arg)
```

### libm/sqrt.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libm/sqrt.c unix-v7-c99/libm/sqrt.c || true
```

Expect:

```
11c11
< double frexp();
---
> double frexp(double, int *);
14,15c14
< sqrt(arg)
< double arg;
---
> sqrt(double arg)
```

### libm/tan.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libm/tan.c unix-v7-c99/libm/tan.c || true
```

Expect:

```
23,24c23
< tan(arg)
< double arg;
---
> tan(double arg)
26c25
< 	double modf();
---
> 	double modf(double, double *);
```

### libm/tanh.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libm/tanh.c unix-v7-c99/libm/tanh.c || true
```

Expect:

```
9c9
< double sinh(), cosh();
---
> double sinh(double), cosh(double);
12,13c12
< tanh(arg)
< double arg;
---
> tanh(double arg)
```

### root/etc/group

Local test:

```
diff unix-v7-c99/v7/etc/group unix-v7-c99/root/etc/group || true
```

Expect:

```
0a1
> root::0:root
2,4c3,9
< sys::2:bin,sys
< bin::3:sys,bin
< uucp::4:
---
> bin::2:
> sys::3:
> adm::4:
> mail::5:
> news::6:
> uucp::7:
> daemon::12:
```

### root/etc/passwd

Local test:

```
diff unix-v7-c99/v7/etc/passwd unix-v7-c99/root/etc/passwd || true
```

Expect:

```
1,6c1,2
< root:VwL97VCAx1Qhs:0:1::/:
< daemon:x:1:1::/:
< sys::2:2::/usr/sys:
< bin::3:3::/bin:
< uucp::4:4::/usr/lib/uucp:/usr/lib/uucico
< dmr::7:3::/usr/dmr:
---
> root::0:0:root:/:/bin/sh
> dmr::1:1:dennis:/:/bin/sh
```

### root/etc/rc

Local test:

```
diff unix-v7-c99/v7/etc/rc unix-v7-c99/root/etc/rc || true
```

Expect:

```
5c5
< rm /etc/mtab
---
> rm -f /etc/mtab
7,10d6
< /etc/mount /dev/rp3 /usr
< rm -f /usr/spool/lpd/lock
< : /etc/accton /usr/adm/acct
< rm -f /usr/tmp/*
```

### root/etc/ttys

Local test:

```
diff unix-v7-c99/v7/etc/ttys unix-v7-c99/root/etc/ttys || true
```

Expect:

```
2,33d1
< 00tty00
< 00tty01
< 00tty02
< 00tty03
< 00tty04
< 00tty05
< 00tty06
< 00tty07
< 00tty08
< 00tty09
< 00tty10
< 00tty11
< 00tty12
< 00tty13
< 00tty14
< 00tty15
< 00tty16
< 00tty17
< 00tty18
< 00tty19
< 00tty20
< 00tty21
< 00tty22
< 00tty23
< 00tty24
< 00tty25
< 00tty26
< 00tty27
< 00tty28
< 00tty29
< 00tty30
< 00tty31
```
