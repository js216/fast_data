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
.profile
LICENSE
Makefile
README
boot/rootfs.proto
usr/src/cmd/factor.c
usr/src/cmd/primes.c
usr/src/libc/crt0.c
usr/src/libc/crt0.s
usr/src/libc/data.c
usr/src/libc/doprnt.c
usr/src/libc/doscan.c
usr/src/libc/errlst.c
usr/src/libc/gen/abort.c
usr/src/libc/gen/exit.c
usr/src/libc/l3.c
usr/src/libc/math_helpers.c
usr/src/libc/memcpy.c
usr/src/libc/mkdir.c
usr/src/libc/sys/access.s
usr/src/libc/sys/acct.s
usr/src/libc/sys/alarm.c
usr/src/libc/sys/brk.c
usr/src/libc/sys/chdir.s
usr/src/libc/sys/chmod.s
usr/src/libc/sys/chown.s
usr/src/libc/sys/chroot.s
usr/src/libc/sys/close.s
usr/src/libc/sys/creat.s
usr/src/libc/sys/dup.c
usr/src/libc/sys/execl.c
usr/src/libc/sys/execv.c
usr/src/libc/sys/execve.c
usr/src/libc/sys/exit.s
usr/src/libc/sys/fork.s
usr/src/libc/sys/fstat.s
usr/src/libc/sys/getgid.s
usr/src/libc/sys/getpid.s
usr/src/libc/sys/getuid.s
usr/src/libc/sys/ioctl.s
usr/src/libc/sys/kill.s
usr/src/libc/sys/link.s
usr/src/libc/sys/lock.s
usr/src/libc/sys/lseek.s
usr/src/libc/sys/mknod.s
usr/src/libc/sys/mount.s
usr/src/libc/sys/nice.s
usr/src/libc/sys/open.c
usr/src/libc/sys/pause.c
usr/src/libc/sys/pipe.s
usr/src/libc/sys/profil.s
usr/src/libc/sys/ptrace.s
usr/src/libc/sys/read.s
usr/src/libc/sys/setgid.s
usr/src/libc/sys/setuid.s
usr/src/libc/sys/signal.s
usr/src/libc/sys/stat.s
usr/src/libc/sys/stime.c
usr/src/libc/sys/sync.s
usr/src/libc/sys/time.c
usr/src/libc/sys/times.s
usr/src/libc/sys/umask.s
usr/src/libc/sys/umount.s
usr/src/libc/sys/unlink.s
usr/src/libc/sys/utime.s
usr/src/libc/sys/wait.s
usr/src/libc/sys/write.s
usr/src/libc/syscall.s
usr/src/libc/ttyname.c
usr/src/libc/u.ld
usr/sys/conf/arm_qemu.ld
usr/sys/conf/conf.c
usr/sys/conf/low.s
usr/sys/conf/mch.s
usr/sys/conf/mp135.c
usr/sys/conf/mp135/memmap.h
usr/sys/conf/qemu.c
usr/sys/conf/qemu/memmap.h
usr/sys/conf/sysram.ld
usr/sys/dev/pl011.c
usr/sys/dev/stm32sd.c
usr/sys/dev/stm32usart.c
usr/sys/dev/virtio_blk.c
usr/sys/sys/machdep.c
```

### Files matching V7 exactly

Local test:

```
diff unix-v7-c99/v7/usr/include/ar.h unix-v7-c99/usr/include/ar.h || true
diff unix-v7-c99/v7/usr/include/dumprestor.h unix-v7-c99/usr/include/dumprestor.h || true
diff unix-v7-c99/v7/usr/include/execargs.h unix-v7-c99/usr/include/execargs.h || true
diff unix-v7-c99/v7/usr/include/sgtty.h unix-v7-c99/usr/include/sgtty.h || true
diff unix-v7-c99/v7/usr/include/sys/fblk.h unix-v7-c99/usr/include/sys/fblk.h || true
diff unix-v7-c99/v7/usr/include/sys/filsys.h unix-v7-c99/usr/include/sys/filsys.h || true
diff unix-v7-c99/v7/usr/include/sys/ino.h unix-v7-c99/usr/include/sys/ino.h || true
diff unix-v7-c99/v7/usr/include/tp_defs.h unix-v7-c99/usr/include/tp_defs.h || true
diff unix-v7-c99/v7/usr/include/utmp.h unix-v7-c99/usr/include/utmp.h || true
diff unix-v7-c99/v7/usr/sys/h/callo.h unix-v7-c99/usr/sys/h/callo.h || true
diff unix-v7-c99/v7/usr/src/cmd/sh/brkincr.h unix-v7-c99/usr/src/cmd/sh/brkincr.h || true
diff unix-v7-c99/v7/usr/src/cmd/sh/dup.h unix-v7-c99/usr/src/cmd/sh/dup.h || true
diff unix-v7-c99/v7/usr/src/cmd/sh/mac.h unix-v7-c99/usr/src/cmd/sh/mac.h || true
diff unix-v7-c99/v7/usr/src/cmd/sh/name.h unix-v7-c99/usr/src/cmd/sh/name.h || true
diff unix-v7-c99/v7/usr/src/cmd/sh/stak.h unix-v7-c99/usr/src/cmd/sh/stak.h || true
diff unix-v7-c99/v7/usr/src/cmd/sh/sym.h unix-v7-c99/usr/src/cmd/sh/sym.h || true
diff unix-v7-c99/v7/usr/src/cmd/sh/timeout.h unix-v7-c99/usr/src/cmd/sh/timeout.h || true
diff unix-v7-c99/v7/usr/src/cmd/tp/tp.h unix-v7-c99/usr/src/cmd/tp/tp.h || true
diff unix-v7-c99/v7/usr/src/cmd/tp/tp0.c unix-v7-c99/usr/src/cmd/tp/tp0.c || true
diff unix-v7-c99/v7/usr/include/tp_defs.h unix-v7-c99/usr/src/cmd/tp/tp_defs.h || true
diff unix-v7-c99/v7/usr/src/libc/gen/ctype_.c unix-v7-c99/usr/src/libc/ctype_.c || true
diff unix-v7-c99/v7/usr/sys/h/acct.h unix-v7-c99/usr/sys/h/acct.h || true
diff unix-v7-c99/v7/usr/sys/h/fblk.h unix-v7-c99/usr/sys/h/fblk.h || true
diff unix-v7-c99/v7/usr/sys/h/filsys.h unix-v7-c99/usr/sys/h/filsys.h || true
diff unix-v7-c99/v7/usr/sys/h/ino.h unix-v7-c99/usr/sys/h/ino.h || true
diff unix-v7-c99/v7/usr/sys/h/mount.h unix-v7-c99/usr/sys/h/mount.h || true
diff unix-v7-c99/v7/usr/sys/h/stat.h unix-v7-c99/usr/sys/h/stat.h || true
diff unix-v7-c99/v7/usr/sys/h/timeb.h unix-v7-c99/usr/sys/h/timeb.h || true
diff unix-v7-c99/v7/etc/group unix-v7-c99/etc/group || true
diff unix-v7-c99/v7/etc/passwd unix-v7-c99/etc/passwd || true
diff unix-v7-c99/v7/etc/ttys unix-v7-c99/etc/ttys || true
```

Expect:

```
```

### No blank-line-only diff churn

Note to agent: DO NOT UNDER ANY CIRCUMSTANCES WHATSOEVER MODIFY THIS SECTION IN
ANY WAY WHATSOEVER.

Local test:

```
grep -nE '^(<|>) $' missions/unix-historical-accuracy.md missions/unix-on-qemu.md | wc -l
```

Expect:

```
0
```

### Proper diff lines

Check that diff sections use plain diff only: diff, two filenames, and
|| true at the end.  No post-processing, labels, unified diff flags, or
exception language.

Note to agent: DO NOT UNDER ANY CIRCUMSTANCES WHATSOEVER MODIFY THIS SECTION IN
ANY WAY WHATSOEVER.

Local test:

```
awk '/^diff / && !/^diff [^ ]+ [^ ]+ \|\| true$/ { print; bad = 1 } END { exit bad }' missions/unix-historical-accuracy.md
```

Expect:

```
```

### usr/src/cmd/awk/b.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/awk/b.c unix-v7-c99/usr/src/cmd/awk/b.c || true
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
176,177c183,185
< first(p)			/* collects initially active leaves of p into setvec */
< register node *p;		/* returns 0 or 1 depending on whether p matches empty string */
---
> int
> first(register node *p)			/* collects initially active leaves of p into setvec */
> 				/* returns 0 or 1 depending on whether p matches empty string */
179c187
< 	register b;
---
> 	register int b;
210,211c218,219
< follow(v)
< node *v;		/* collects leaves that can follow v into setvec */
---
> int
> follow(node *v)		/* collects leaves that can follow v into setvec */
216c224
< 		return;
---
> 		return(0);
222c230
< 				return;
---
> 				return(0);
226c234
< 				return;
---
> 				return(0);
231c239
< 						return;
---
> 						return(0);
236c244
< 				return;
---
> 				return(0);
241c249
< 				return;
---
> 				return(0);
242a251
> 	return(0);
245,246c254,255
< member(c, s)	/* is c in s? */
< register char c, *s;
---
> int
> member(register char c, register char *s)	/* is c in s? */
254,257c263,266
< notin(array, n, prev)		/* is setvec in array[0] thru array[n]? */
< int **array;
< int *prev; {
< 	register i, j;
---
> int
> notin(int **array, int n, int *prev)		/* is setvec in array[0] thru array[n]? */
> {
> 	register int i, j;
272c281
< int *add(n) {		/* remember setvec */
---
> int *add(int n) {		/* remember setvec */
274c283
< 	register i;
---
> 	register int i;
288c297
< struct fa *cgotofn()
---
> struct fa *cgotofn(void)
290c299
< 	register i, k;
---
> 	register int i, k;
347,348c356,357
< 						if (isyms[*p] != 1) {
< 							isyms[*p] = 1;
---
> 						if (isyms[(unsigned char)*p] != 1) {
> 							isyms[(unsigned char)*p] = 1;
408,409c417,418
< 							if (isyms[*p] == 0 && symbol[*p] == 0) {
< 								symbol[*p] = 1;
---
> 							if (isyms[(unsigned char)*p] == 0 && symbol[(unsigned char)*p] == 0) {
> 								symbol[(unsigned char)*p] = 1;
428c437
< 			symbol[c] = 0;
---
> 			symbol[(unsigned char)c] = 0;
435c444
< 					if (k == CHAR && c == (int) right(cp)
---
> 					if ((k == CHAR && c == (int) right(cp))
437,438c446,447
< 					 || k == CCL && member(c, (char *) right(cp))
< 					 || k == NCCL && !member(c, (char *) right(cp))) {
---
> 					 || (k == CCL && member(c, (char *) right(cp)))
> 					 || (k == NCCL && !member(c, (char *) right(cp)))) {
507,509c516,517
< match(pfa, p)
< register struct fa *pfa;
< register char *p;
---
> int
> match(register struct fa *pfa, register char *p)
511c519
< 	register count;
---
> 	register int count;
```

### usr/src/cmd/pwd.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/pwd.c unix-v7-c99/usr/src/cmd/pwd.c || true
```

Expect:

```
17c17,20
< main()
---
> void prname(void);
> void cat(void);
> int
> main(void)
38c41
< 				if (read(file, (char *)&dir, sizeof(dir)) < sizeof(dir)) {
---
> 				if (read(file, (char *)&dir, sizeof(dir)) < (int)sizeof(dir)) {
45c48
< 				if(read(file, (char *)&dir, sizeof(dir)) < sizeof(dir)) {
---
> 				if(read(file, (char *)&dir, sizeof(dir)) < (int)sizeof(dir)) {
56c59,60
< prname()
---
> void
> prname(void)
66c70,71
< cat()
---
> void
> cat(void)
68c73
< 	register i, j;
---
> 	register int i, j;
```

### usr/src/cmd/sh/error.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/error.c unix-v7-c99/usr/src/cmd/sh/error.c || true
```

Expect:

```
11a12,21
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
15c25
< exitset()
---
> INT exitset(void)
17a28
> 	return(0);
20c31
< sigchk()
---
> INT sigchk(void)
28a40
> 	return(0);
31,32c43
< failed(s1,s2)
< 	STRING	s1, s2;
---
> INT failed(STRING s1, STRING s2)
38a50
> 	return(0);
41,42c53
< error(s)
< 	STRING	s;
---
> INT error(STRING s)
44a56
> 	return(0);
47,48c59,60
< exitsh(xno)
< 	INT	xno;
---
> void
> exitsh(INT xno)
65c77
< done()
---
> void done(void)
68c80
< 	IF t=trapcom[0]
---
> 	IF (t=trapcom[0])
76,77c88,89
< rmtemp(base)
< 	IOPTR		base;
---
> void
> rmtemp(IOPTR base)
```

### usr/src/cmd/sh/print.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/print.c unix-v7-c99/usr/src/cmd/sh/print.c || true
```

Expect:

```
11a12,16
> extern int write(int fd, char *buf, int n);
> INT	length(STRING as);
> INT	itos(INT n);
> INT	prn(INT n);
> INT	failed(STRING s1, STRING s2);
17,18c22,23
< newline()
< {	prc(NL);
---
> INT newline(void)
> {	prc(NL); return(0);
21,22c26,27
< blank()
< {	prc(SP);
---
> INT blank(void)
> {	prc(SP); return(0);
25c30
< prp()
---
> INT prp(void)
29a35
> 	return(0);
32,33c38
< VOID	prs(as)
< 	STRING		as;
---
> VOID	prs(STRING as)
37c42
< 	IF s=as
---
> 	IF (s=as)
39a45
> 	return(0);
42,43c48
< VOID	prc(c)
< 	CHAR		c;
---
> VOID	prc(INT cc)
44a50
> 	CHAR c = cc;
47a54
> 	return(0);
50,51c57
< prt(t)
< 	L_INT		t;
---
> INT prt(L_INT t)
58c64
< 	IF hr=t/60
---
> 	IF (hr=t/60)
62a69
> 	return(0);
65,66c72
< prn(n)
< 	INT		n;
---
> INT prn(INT n)
68a75
> 	return(0);
71c78
< itos(n)
---
> INT itos(INT n)
80a88
> 	return(0);
83,84c91,92
< stoi(icp)
< STRING	icp;
---
> INT
> stoi(STRING icp)
95a104
> 	return(0);
```

### usr/src/cmd/sh/string.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/string.c unix-v7-c99/usr/src/cmd/sh/string.c || true
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

### usr/src/cmd/tp/tp3.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/tp/tp3.c unix-v7-c99/usr/src/cmd/tp/tp3.c || true
```

Expect:

```
1a2
> #include <stdio.h>
3,4c4,8
< gettape(how)
< int (*how)();
---
> int	decode(), verify(), clrent(), bitmap(), maperr(), setmap(),
> 	wrdir(), update1(), wseek(), twrite(), phserr(), done(),
> 	rseek(), tread(), usage();
> int
> gettape(int (*how)(struct dent *))
30a35
> 	return(0);
33,34c38,39
< delete(dd)
< struct dent *dd;
---
> int
> delete(struct dent *dd)
37a43
> 	return(0);
41c47,48
< update()
---
> int
> update(void)
44c51
< 	register b, last;
---
> 	register int b, last;
67a75
> 	return(0);
71c79,80
< update1()
---
> int
> update1(void)
74c83
< 	register index;
---
> 	register int index;
88c97
< 		if ((d = id) == 0)	return;
---
> 		if ((d = id) == 0)	return(0);
101c110
< 		if (index = d->d_size % BSIZE) {
---
> 		if ((index = d->d_size % BSIZE)) {
110,111c119,121
< phserr()
< {	printf("%s -- Phase error \n", name);  }
---
> int
> phserr(void)
> {	printf("%s -- Phase error \n", name); return(0);  }
113a124
> int
117c128
< 	register count;
---
> 	register int count;
127a139
> 	return(0);
130,131c142,143
< setmap(d)
< register struct dent *d;
---
> int
> setmap(register struct dent *d)
140c152
< 	if ((c += block) >= tapsiz)		maperr();
---
> 	if ((c += block) >= (unsigned)tapsiz)		maperr();
146a159
> 	return(0);
149c162,163
< maperr()
---
> int
> maperr(void)
152a167
> 	return(0);
156c171,172
< usage()
---
> int
> usage(void)
158c174
< 	register reg,count;
---
> 	register int reg,count;
160c176
< 	static lused;
---
> 	static int lused;
186a203
> 	return(0);
190,191c207,208
< taboc(dd)
< struct dent *dd;
---
> int
> taboc(struct dent *dd)
193,194c210,211
< 	register  mode;
< 	register *m;
---
> 	register int mode;
> 	register int *m;
196c213
< 	int count, *localtime();
---
> 	int count;
215c232
< 		m = localtime(&dd->d_time);
---
> 		m = (int *)localtime(&dd->d_time);
218a236
> 	return(0);
222,223c240,241
< extract(d)
< register struct dent *d;
---
> int
> extract(register struct dent *d)
225c243
< 	register count, id;
---
> 	register int count, id;
227,228c245,246
< 	if (d->d_size==0)	return;
< 	if (verify('x') < 0)			return;
---
> 	if (d->d_size==0)	return(0);
> 	if (verify('x') < 0)			return(0);
238c256
< 	if (count = d->d_size % BSIZE) {
---
> 	if ((count = d->d_size % BSIZE)) {
243c261
< 			return;
---
> 			return(0);
247a266
> 	return(0);
```

### usr/sys/h/conf.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/conf.h unix-v7-c99/usr/sys/h/conf.h || true
```

Expect:

```

```

### usr/sys/h/file.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/file.h unix-v7-c99/usr/sys/h/file.h || true
```

Expect:

```

```

### usr/src/cmd/echo.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/echo.c unix-v7-c99/usr/src/cmd/echo.c || true
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

### usr/src/cmd/cat.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/cat.c unix-v7-c99/usr/src/cmd/cat.c || true
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
42c42
< 		if (fflg || (*++argv)[0]=='-' && (*argv)[1]=='\0')
---
> 		if (fflg || ((*++argv)[0]=='-' && (*argv)[1]=='\0'))
```

### usr/src/cmd/sync.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sync.c unix-v7-c99/usr/src/cmd/sync.c || true
```

Expect:

```
1c1,3
< main()
---
> void sync(void);
> int
> main(void)
```

### usr/src/cmd/rev.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/rev.c unix-v7-c99/usr/src/cmd/rev.c || true
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

### usr/src/cmd/yes.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/yes.c unix-v7-c99/usr/src/cmd/yes.c || true
```

Expect:

```
1,2c1,3
< main(argc, argv)
< char **argv;
---
> int printf(char *fmt, ...);
> int
> main(int argc, char *argv[])
```

### usr/src/cmd/wc.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/wc.c unix-v7-c99/usr/src/cmd/wc.c || true
```

Expect:

```
5,6c5,7
< main(argc, argv)
< char **argv;
---
> void wcp(register char *wd, long charct, long wordct, long linect);
> int
> main(int argc, char *argv[])
69,71c70,71
< wcp(wd, charct, wordct, linect)
< register char *wd;
< long charct; long wordct; long linect;
---
> void
> wcp(register char *wd, long charct, long wordct, long linect)
```

### usr/src/cmd/basename.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/basename.c unix-v7-c99/usr/src/cmd/basename.c || true
```

Expect:

```
3,4c3,4
< main(argc, argv)
< char **argv;
---
> int
> main(int argc, char *argv[])
27c27
< 	puts(p2, stdout);
---
> 	puts(p2);
```

### usr/src/cmd/sum.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sum.c unix-v7-c99/usr/src/cmd/sum.c || true
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

### usr/src/cmd/tty.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/tty.c unix-v7-c99/usr/src/cmd/tty.c || true
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

### usr/src/cmd/cmp.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/cmp.c unix-v7-c99/usr/src/cmd/cmp.c || true
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
118c118
< 	while(isdigit(*s))
---
> 	while(isdigit((unsigned char)*s))
```

### usr/src/cmd/comm.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/comm.c unix-v7-c99/usr/src/cmd/comm.c || true
```

Expect:

```
11,13c11,17
< FILE *openfil();
< main(argc,argv)
< char	*argv[];
---
> FILE *openfil(char *s);
> int rd(FILE *file, char *buf);
> void wr(char *str, int n);
> void copy(FILE *ibuf, char *lbuf, int n);
> int compare(char *a, char *b);
> int
> main(int argc, char *argv[])
93,95c97,98
< rd(file,buf)
< FILE *file;
< char *buf;
---
> int
> rd(FILE *file, char *buf)
112,113c115,116
< wr(str,n)
< 	char	*str;
---
> void
> wr(char *str, int n)
132,134c135,136
< copy(ibuf,lbuf,n)
< FILE *ibuf;
< char *lbuf;
---
> void
> copy(FILE *ibuf, char *lbuf, int n)
143,144c145,146
< compare(a,b)
< 	char	*a,*b;
---
> int
> compare(char *a, char *b)
155,156c157,158
< FILE *openfil(s)
< char *s;
---
> FILE *
> openfil(char *s)
```

### usr/src/cmd/od.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/od.c unix-v7-c99/usr/src/cmd/od.c || true
```

Expect:

```
14,15c14,21
< main(argc, argv)
< char **argv;
---
> void offset(register char *s);
> void line(long a, unsigned short *w, int n);
> void putx(unsigned n, int c);
> void cput(int c);
> void putn(long n, int b, int c);
> void pre(int n);
> int
> main(int argc, char *argv[])
18c24
< 	register n, f, same;
---
> 	register int n, f, same;
97,99c103,104
< line(a, w, n)
< long a;
< unsigned short *w;
---
> void
> line(long a, unsigned short *w, int n)
101c106
< 	register i, f, c;
---
> 	register int i, f, c;
120,121c125,126
< putx(n, c)
< unsigned n;
---
> void
> putx(unsigned n, int c)
158c163,164
< cput(c)
---
> void
> cput(int c)
190,191c196,197
< putn(n, b, c)
< long n;
---
> void
> putn(long n, int b, int c)
193c199
< 	register d;
---
> 	register int d;
205c211,212
< pre(n)
---
> void
> pre(int n)
213,214c220,221
< offset(s)
< register char *s;
---
> void
> offset(register char *s)
```

### usr/src/cmd/tail.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/tail.c unix-v7-c99/usr/src/cmd/tail.c || true
```

Expect:

```
0a1
> #include <stdio.h>
18c19
< int errno;
---
> extern int errno;
20,21c21,23
< main(argc,argv)
< char **argv;
---
> int digit(int c);
> int
> main(int argc, char *argv[])
24c26
< 	register i,j,k;
---
> 	register int i,j,k;
31c33
< 	if(argc<=1 || *arg!='-'&&*arg!='+') {
---
> 	if(argc<=1 || (*arg!='-' && *arg!='+')) {
181c183,184
< digit(c)
---
> int
> digit(int c)
```

### usr/src/cmd/test.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/test.c unix-v7-c99/usr/src/cmd/test.c || true
```

Expect:

```
18,19c18,29
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
> int
> main(int argc, char *argv[])
32c42
< char *nxtarg(mt) {
---
> char *nxtarg(int mt) {
44c54,55
< exp() {
---
> int
> exp(void) {
53c64,65
< e1() {
---
> int
> e1(void) {
62c74,75
< e2() {
---
> int
> e2(void) {
69c82,83
< e3() {
---
> int
> e3(void) {
97c111
< 	if(EQ(a, "-t"))
---
> 	if(EQ(a, "-t")) {
101a116
> 	}
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

### usr/src/cmd/look.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/look.c unix-v7-c99/usr/src/cmd/look.c || true
```

Expect:

```
14,15c14,18
< main(argc,argv)
< char **argv;
---
> void canon(char *old, char *new);
> int compare(register char *s, register char *t);
> int getword(char *w);
> int
> main(int argc, char *argv[])
17c20
< 	register c;
---
> 	register int c;
44c47
< 		return;
---
> 		return(0);
87c90
< 			return;
---
> 			return(0);
91c94
< 			return;
---
> 			return(0);
111a115
> 	return(0);
114,115c118,119
< compare(s,t)
< register char *s,*t;
---
> int
> compare(register char *s, register char *t)
126,127c130,131
< getword(w)
< char *w;
---
> int
> getword(char *w)
129c133
< 	register c;
---
> 	register int c;
142,143c146,147
< canon(old,new)
< char *old,*new;
---
> void
> canon(char *old, char *new)
145c149
< 	register c;
---
> 	register int c;
```

### usr/src/cmd/rm.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/rm.c unix-v7-c99/usr/src/cmd/rm.c || true
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

### usr/src/cmd/ln.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/ln.c unix-v7-c99/usr/src/cmd/ln.c || true
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

### usr/src/cmd/mkdir.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/mkdir.c unix-v7-c99/usr/src/cmd/mkdir.c || true
```

Expect:

```
9,10c9
< char	*strcat();
< char	*strcpy();
---
> void	mkdir(char *d);
12,13c11,12
< main(argc, argv)
< char *argv[];
---
> int
> main(int argc, char *argv[])
31,32c30,31
< mkdir(d)
< char *d;
---
> void
> mkdir(char *d)
35c34
< 	register i, slash = 0;
---
> 	register int i, slash = 0;
```

### usr/src/cmd/rmdir.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/rmdir.c unix-v7-c99/usr/src/cmd/rmdir.c || true
```

Expect:

```
11,13c11
< char	*rindex();
< char	*strcat();
< char	*strcpy();
---
> void	rmdir(char *d);
15,17c13,14
< main(argc,argv)
< int argc;
< char **argv;
---
> int
> main(int argc, char **argv)
29,30c26,27
< rmdir(d)
< char *d;
---
> void
> rmdir(char *d)
```

### usr/src/cmd/tee.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/tee.c unix-v7-c99/usr/src/cmd/tee.c || true
```

Expect:

```
18,19c18,28
< extern errno;
< long	lseek();
---
> extern int errno;
> long	lseek(int fd, long offset, int ptrname);
> int	creat(char *path, int mode);
> int	fstat(int fd, struct stat *buf);
> int	open(char *path, int mode);
> int	read(int fd, char *buf, int n);
> int	stat(char *path, struct stat *buf);
> int	write(int fd, char *buf, int n);
> int	signal(int sig, int fun);
> void	stash(int p);
> void	puts(char *s);
21,22c30,31
< main(argc,argv)
< char **argv;
---
> int
> main(int argc, char **argv)
24c33
< 	int register r,w,p;
---
> 	register int r,w,p;
70c79
< 					return;
---
> 					return(0);
79c88,89
< stash(p)
---
> void
> stash(int p)
90,91c100,101
< puts(s)
< char *s;
---
> void
> puts(char *s)
```

### usr/src/cmd/uniq.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/uniq.c unix-v7-c99/usr/src/cmd/uniq.c || true
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
21c24
< 			if (isdigit(argv[1][1]))
---
> 			if (isdigit((unsigned char)argv[1][1]))
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

### usr/src/cmd/date.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/date.c unix-v7-c99/usr/src/cmd/date.c || true
```

Expect:

```
9a10
> #include <stdio.h>
14a16,17
> int	gtime(void);
> int	gp(int dfault);
38,39c41,42
< main(argc, argv)
< char *argv[];
---
> int
> main(int argc, char *argv[])
94c97,98
< gtime()
---
> int
> gtime(void)
152c156,157
< gp(dfault)
---
> int
> gp(int dfault)
```

### usr/src/cmd/kill.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/kill.c unix-v7-c99/usr/src/cmd/kill.c || true
```

Expect:

```
5a6
> #include <stdio.h>
7,8c8,10
< main(argc, argv)
< char **argv;
---
> extern char *sys_errlist[];
> int
> main(int argc, char **argv)
10c12
< 	register signo, pid, res;
---
> 	register int signo, pid, res;
12,13c14
< 	extern char *sys_errlist[];
< 	extern errno;
---
> 	extern int errno;
```

### usr/src/cmd/nice.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/nice.c unix-v7-c99/usr/src/cmd/nice.c || true
```

Expect:

```
5,7c5,7
< main(argc, argv)
< int argc;
< char *argv[];
---
> extern char *sys_errlist[];
> int
> main(int argc, char *argv[])
10,11c10
< 	extern errno;
< 	extern char *sys_errlist[];
---
> 	extern int errno;
```

### usr/src/cmd/mknod.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/mknod.c unix-v7-c99/usr/src/cmd/mknod.c || true
```

Expect:

```
1,3c1,4
< main(argc, argv)
< int argc;
< char **argv;
---
> #include <stdio.h>
> int number(char *s);
> int
> main(int argc, char **argv)
30,31c31,32
< number(s)
< char *s;
---
> int
> number(char *s)
36c37
< 	while(c = *s++) {
---
> 	while((c = *s++)) {
```

### usr/src/cmd/who.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/who.c unix-v7-c99/usr/src/cmd/who.c || true
```

Expect:

```
13,14c13,15
< main(argc, argv)
< char **argv;
---
> void putline(void);
> int
> main(int argc, char **argv)
55c56,57
< putline()
---
> void
> putline(void)
```

### usr/src/cmd/mesg.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/mesg.c unix-v7-c99/usr/src/cmd/mesg.c || true
```

Expect:

```
19,20c19,22
< main(argc, argv)
< char *argv[];
---
> void error(char *s);
> void newmode(int m);
> int
> main(int argc, char *argv[])
44,45c46,47
< error(s)
< char *s;
---
> void
> error(char *s)
51c53,54
< newmode(m)
---
> void
> newmode(int m)
```

### usr/src/cmd/time.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/time.c unix-v7-c99/usr/src/cmd/time.c || true
```

Expect:

```
11,12c11,13
< main(argc, argv)
< char **argv;
---
> void printt(char *s, long a);
> int
> main(int argc, char **argv)
16c17
< 	register p;
---
> 	register int p;
53,55c54,55
< printt(s, a)
< char *s;
< long a;
---
> void
> printt(char *s, long a)
58c58
< 	register i;
---
> 	register int i;
```

### usr/src/cmd/checkeq.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/checkeq.c unix-v7-c99/usr/src/cmd/checkeq.c || true
```

Expect:

```
8c8,11
< main(argc, argv) char **argv; {
---
> void check(FILE *f);
> int
> main(int argc, char **argv)
> {
33,34c36,37
< check(f)
< FILE	*f;
---
> void
> check(FILE *f)
```

### usr/src/cmd/calendar.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/calendar.c unix-v7-c99/usr/src/cmd/calendar.c || true
```

Expect:

```
7a8
> #include <stdio.h>
27,28c28,30
< tprint(t)
< long t;
---
> void tprint(long t);
> void
> tprint(long t)
36c38,39
< main()
---
> int
> main(void)
44a48
> 		/* FALLTHROUGH */
47a52
> 		/* FALLTHROUGH */
```

### usr/src/cmd/col.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/col.c unix-v7-c99/usr/src/cmd/col.c || true
```

Expect:

```
19a20,25
> void outc(int c);
> void store(int lno);
> void fetch(int lno);
> void emit(char *s, int lineno);
> void incr(void);
> void decr(void);
21,22c27,28
< main (argc, argv)
< 	int argc; char **argv;
---
> int
> main (int argc, char **argv)
162,163c168,169
< outc (c)
< 	register char c;
---
> void
> outc (register int c)
208,210c214,215
< store (lno)
< {
< 	char *malloc();
---
> void
> store (int lno)
211a217
> {
223c229,230
< fetch(lno)
---
> void
> fetch(int lno)
236,238c243,244
< emit (s, lineno)
< 	char *s;
< 	int lineno;
---
> void
> emit (char *s, int lineno)
294c300,301
< incr()
---
> void
> incr(void)
308c315,316
< decr()
---
> void
> decr(void)
```

### usr/src/cmd/fgrep.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/fgrep.c unix-v7-c99/usr/src/cmd/fgrep.c || true
```

Expect:

```
33,34c33,39
< main(argc, argv)
< char **argv;
---
> void execute(char *file);
> int getargc(void);
> void cgotofn(void);
> void overflo(void);
> void cfail(void);
> int
> main(int argc, char **argv)
112,113c117,118
< execute(file)
< char *file;
---
> void
> execute(char *file)
117c122
< 	register ccount;
---
> 	register int ccount;
208c213
< 		if (*p++ == '\n')
---
> 		if (*p++ == '\n') {
215a221
> 		}
225c231,232
< getargc()
---
> int
> getargc(void)
227c234
< 	register c;
---
> 	register int c;
235,236c242,244
< cgotofn() {
< 	register c;
---
> void
> cgotofn(void) {
> 	register int c;
298c306,307
< overflo() {
---
> void
> overflo(void) {
302c311,312
< cfail() {
---
> void
> cfail(void) {
```

### usr/src/cmd/su.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/su.c unix-v7-c99/usr/src/cmd/su.c || true
```

Expect:

```
4,6c4
< struct	passwd *pwd,*getpwnam();
< char	*crypt();
< char	*getpass();
---
> struct	passwd *pwd;
9,11c7,8
< main(argc,argv)
< int	argc;
< char	**argv;
---
> int
> main(int argc, char **argv)
```

### usr/src/cmd/newgrp.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/newgrp.c unix-v7-c99/usr/src/cmd/newgrp.c || true
```

Expect:

```
5,7c5,6
< struct	group	*getgrnam(), *grp;
< struct	passwd	*getpwuid(), *pwd;
< char	*getpass(), *crypt();
---
> struct	group	*grp;
> struct	passwd	*pwd;
9,11c8,10
< main(argc,argv)
< int	argc;
< char	**argv;
---
> void done(void);
> int
> main(int argc, char **argv)
13c12
< 	register i;
---
> 	register int i;
45c44,45
< done()
---
> void
> done(void)
47c47
< 	register i;
---
> 	register int i;
```

### usr/src/cmd/random.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/random.c unix-v7-c99/usr/src/cmd/random.c || true
```

Expect:

```
4d3
< double	atof();
7c6,7
< main(argc,argv) char **argv;
---
> int
> main(int argc, char **argv)
```

### usr/src/cmd/crypt.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/crypt.c unix-v7-c99/usr/src/cmd/crypt.c || true
```

Expect:

```
13d12
< char	*getpass();
15,16c14,15
< setup(pw)
< char *pw;
---
> void
> setup(char *pw)
68,69c67,68
< main(argc, argv)
< char *argv[];
---
> int
> main(int argc, char *argv[])
71c70
< 	register i, n1, n2;
---
> 	register int i, n1, n2;
```

### usr/src/cmd/makekey.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/makekey.c unix-v7-c99/usr/src/cmd/makekey.c || true
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

### usr/src/cmd/diffh.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/diffh.c unix-v7-c99/usr/src/cmd/diffh.c || true
```

Expect:

```
17a18,30
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
> int	space(int c);
20,21c33
< char *getl(f,n)
< long n;
---
> char *getl(int f, long n)
24,25c36
< 	char *malloc();
< 	register delta, nt;
---
> 	register int delta, nt;
42c53
< 		if(t==NULL)
---
> 		if(t==NULL) {
46a58
> 		}
55,56c67,68
< clrl(f,n)
< long n;
---
> void
> clrl(int f, long n)
58c70
< 	register i,j;
---
> 	register int i,j;
66,67c78,79
< movstr(s,t)
< register char *s, *t;
---
> void
> movstr(register char *s, register char *t)
69c81
< 	while(*t++= *s++)
---
> 	while((*t++= *s++))
73,74c85,86
< main(argc,argv)
< char **argv;
---
> int
> main(int argc, char **argv)
77c89
< 	FILE *dopen();
---
> 	FILE *dopen(char *f1, char *f2);
103c115
< 		return;
---
> 		return(0);
111c123,124
< easysynch()
---
> int
> easysynch(void)
114c127
< 	register k,m;
---
> 	register int k,m;
143c156,157
< output(a,b)
---
> int
> output(int a, int b)
145c159
< 	register i;
---
> 	register int i;
174,176c188,189
< change(a,b,c,d,s)
< long a,c;
< char *s;
---
> void
> change(long a, int b, long c, int d, char *s)
184,185c197,198
< range(a,b)
< long a;
---
> void
> range(long a, int b)
195,196c208,209
< cmp(s,t)
< char *s,*t;
---
> int
> cmp(char *s, char *t)
201,203c214,216
< 		if(bflag&&isspace(*s)&&isspace(*t)) {
< 			while(isspace(*++s)) ;
< 			while(isspace(*++t)) ;
---
> 		if(bflag&&space(*s)&&space(*t)) {
> 			while(space(*++s)) ;
> 			while(space(*++t)) ;
213,214c226,234
< FILE *dopen(f1,f2)
< char *f1,*f2;
---
> int
> space(int c)
> {
> 	if(c==' ' || c=='\t' || c=='\n' || c=='\r' || c=='\f' || c=='\v')
> 		return(1);
> 	return(0);
> }
> FILE *
> dopen(char *f1, char *f2)
219c239
< 	if(cmp(f1,"-")==0)
---
> 	if(cmp(f1,"-")==0) {
223a244
> 	}
227c248,249
< 		for(bptr=b;*bptr= *f1++;bptr++) ;
---
> 		for(bptr=b;(*bptr= *f1++);bptr++)
> 			;
232c254,255
< 		while(*bptr++= *f2++) ;
---
> 		while((*bptr++= *f2++))
> 			;
242,243c265,266
< progerr(s)
< char *s;
---
> void
> progerr(char *s)
248,249c271,272
< error(s,t)
< char *s,*t;
---
> void
> error(char *s, char *t)
256c279,280
< hardsynch()
---
> int
> hardsynch(void)
```

### usr/src/cmd/stty.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/stty.c unix-v7-c99/usr/src/cmd/stty.c || true
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
> 	{ "0",	B0 },
> 	{ "50",	B50 },
> 	{ "75",	B75 },
> 	{ "110",	B110 },
> 	{ "134",	B134 },
> 	{ "134.5",B134 },
> 	{ "150",	B150 },
> 	{ "200",	B200 },
> 	{ "300",	B300 },
> 	{ "600",	B600 },
> 	{ "1200",	B1200 },
> 	{ "1800",	B1800 },
> 	{ "2400",	B2400 },
> 	{ "4800",	B4800 },
> 	{ "9600",	B9600 },
> 	{ "exta",	EXTA },
> 	{ "extb",	EXTB },
> 	{ 0,	0 },
38,39c38
< 	"even",
< 	EVENP, 0,
---
> 	{ "even",	EVENP, 0 },
41,42c40
< 	"-even",
< 	0, EVENP,
---
> 	{ "-even",	0, EVENP },
44,45c42
< 	"odd",
< 	ODDP, 0,
---
> 	{ "odd",	ODDP, 0 },
47,48c44
< 	"-odd",
< 	0, ODDP,
---
> 	{ "-odd",	0, ODDP },
50,51c46
< 	"raw",
< 	RAW, 0,
---
> 	{ "raw",	RAW, 0 },
53,54c48
< 	"-raw",
< 	0, RAW,
---
> 	{ "-raw",	0, RAW },
56,57c50
< 	"cooked",
< 	0, RAW,
---
> 	{ "cooked",	0, RAW },
59,60c52
< 	"-nl",
< 	CRMOD, 0,
---
> 	{ "-nl",	CRMOD, 0 },
62,63c54
< 	"nl",
< 	0, CRMOD,
---
> 	{ "nl",		0, CRMOD },
65,66c56
< 	"echo",
< 	ECHO, 0,
---
> 	{ "echo",	ECHO, 0 },
68,69c58
< 	"-echo",
< 	0, ECHO,
---
> 	{ "-echo",	0, ECHO },
71,72c60
< 	"LCASE",
< 	LCASE, 0,
---
> 	{ "LCASE",	LCASE, 0 },
74,75c62
< 	"lcase",
< 	LCASE, 0,
---
> 	{ "lcase",	LCASE, 0 },
77,78c64
< 	"-LCASE",
< 	0, LCASE,
---
> 	{ "-LCASE",	0, LCASE },
80,81c66
< 	"-lcase",
< 	0, LCASE,
---
> 	{ "-lcase",	0, LCASE },
83,84c68
< 	"-tabs",
< 	XTABS, 0,
---
> 	{ "-tabs",	XTABS, 0 },
86,87c70
< 	"tabs",
< 	0, XTABS,
---
> 	{ "tabs",	0, XTABS },
90,91c73
< 	"cbreak",
< 	CBREAK, 0,
---
> 	{ "cbreak",	CBREAK, 0 },
93,94c75
< 	"-cbreak",
< 	0, CBREAK,
---
> 	{ "-cbreak",	0, CBREAK },
96,97c77
< 	"cr0",
< 	CR0, CR3,
---
> 	{ "cr0",	CR0, CR3 },
99,100c79
< 	"cr1",
< 	CR1, CR3,
---
> 	{ "cr1",	CR1, CR3 },
102,103c81
< 	"cr2",
< 	CR2, CR3,
---
> 	{ "cr2",	CR2, CR3 },
105,106c83
< 	"cr3",
< 	CR3, CR3,
---
> 	{ "cr3",	CR3, CR3 },
108,109c85
< 	"tab0",
< 	TAB0, XTABS,
---
> 	{ "tab0",	TAB0, XTABS },
111,112c87
< 	"tab1",
< 	TAB1, XTABS,
---
> 	{ "tab1",	TAB1, XTABS },
114,115c89
< 	"tab2",
< 	TAB2, XTABS,
---
> 	{ "tab2",	TAB2, XTABS },
117,118c91
< 	"nl0",
< 	NL0, NL3,
---
> 	{ "nl0",	NL0, NL3 },
120,121c93
< 	"nl1",
< 	NL1, NL3,
---
> 	{ "nl1",	NL1, NL3 },
123,124c95
< 	"nl2",
< 	NL2, NL3,
---
> 	{ "nl2",	NL2, NL3 },
126,127c97
< 	"nl3",
< 	NL3, NL3,
---
> 	{ "nl3",	NL3, NL3 },
129,130c99
< 	"ff0",
< 	FF0, FF1,
---
> 	{ "ff0",	FF0, FF1 },
132,133c101
< 	"ff1",
< 	FF1, FF1,
---
> 	{ "ff1",	FF1, FF1 },
135,136c103
< 	"bs0",
< 	BS0, BS1,
---
> 	{ "bs0",	BS0, BS1 },
138,139c105
< 	"bs1",
< 	BS1, BS1,
---
> 	{ "bs1",	BS1, BS1 },
141,142c107
< 	"33",
< 	CR1, ALLDELAY,
---
> 	{ "33",		CR1, ALLDELAY },
144,145c109
< 	"tty33",
< 	CR1, ALLDELAY,
---
> 	{ "tty33",	CR1, ALLDELAY },
147,148c111
< 	"37",
< 	FF1+CR2+TAB1+NL1, ALLDELAY,
---
> 	{ "37",		FF1+CR2+TAB1+NL1, ALLDELAY },
150,151c113
< 	"tty37",
< 	FF1+CR2+TAB1+NL1, ALLDELAY,
---
> 	{ "tty37",	FF1+CR2+TAB1+NL1, ALLDELAY },
153,154c115
< 	"05",
< 	NL2, ALLDELAY,
---
> 	{ "05",		NL2, ALLDELAY },
156,157c117
< 	"vt05",
< 	NL2, ALLDELAY,
---
> 	{ "vt05",	NL2, ALLDELAY },
159,160c119
< 	"tn",
< 	CR1, ALLDELAY,
---
> 	{ "tn",		CR1, ALLDELAY },
162,163c121
< 	"tn300",
< 	CR1, ALLDELAY,
---
> 	{ "tn300",	CR1, ALLDELAY },
165,166c123
< 	"ti",
< 	CR2, ALLDELAY,
---
> 	{ "ti",		CR2, ALLDELAY },
168,169c125
< 	"ti700",
< 	CR2, ALLDELAY,
---
> 	{ "ti700",	CR2, ALLDELAY },
171,172c127
< 	"tek",
< 	FF1, ALLDELAY,
---
> 	{ "tek",	FF1, ALLDELAY },
174,175c129,130
< 	0,
< 	};
---
> 	{ 0,		0, 0 },
> };
180,181c135,140
< main(argc, argv)
< char	*argv[];
---
> int	eq(char *string);
> void	prmodes(void);
> void	delay(int m, char *s);
> void	prspeed(char *c, int s);
> int
> main(int argc, char *argv[])
232,233c191,192
< eq(string)
< char *string;
---
> int
> eq(char *string)
249c208,209
< prmodes()
---
> void
> prmodes(void)
251c211
< 	register m;
---
> 	register int m;
284,285c244,245
< delay(m, s)
< char *s;
---
> void
> delay(int m, char *s)
296,297c256,257
< prspeed(c, s)
< char *c;
---
> void
> prspeed(char *c, int s)
```

### usr/src/cmd/tabs.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/tabs.c unix-v7-c99/usr/src/cmd/tabs.c || true
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

### usr/src/cmd/wall.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/wall.c unix-v7-c99/usr/src/cmd/wall.c || true
```

Expect:

```
8,9c8
< char	*strcpy();
< char	*strcat();
---
> void	sendmes(char *tty);
11,12c10,11
< main(argc, argv)
< char *argv[];
---
> int
> main(int argc, char *argv[])
14c13
< 	register i;
---
> 	register int i;
43,44c42,43
< sendmes(tty)
< char *tty;
---
> void
> sendmes(char *tty)
46c45
< 	register i;
---
> 	register int i;
```

### usr/src/cmd/df.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/df.c unix-v7-c99/usr/src/cmd/df.c || true
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
> extern int	errno;
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

### usr/src/cmd/clri.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/clri.c unix-v7-c99/usr/src/cmd/clri.c || true
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

### usr/src/cmd/cb.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/cb.c unix-v7-c99/usr/src/cmd/cb.c || true
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

### usr/src/cmd/sp.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sp.c unix-v7-c99/usr/src/cmd/sp.c || true
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

### usr/src/cmd/ed.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/ed.c unix-v7-c99/usr/src/cmd/ed.c || true
```

Expect:

```
7a8,10
> #define	puts	u_puts
> #include <stdio.h>
> #undef	puts
13a17
> #undef	EOF
101,102c105,165
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
> int
> main(int argc, char **argv)
108,110c171,173
< 	oldquit = signal(SIGQUIT, SIG_IGN);
< 	oldhup = signal(SIGHUP, SIG_IGN);
< 	oldintr = signal(SIGINT, SIG_IGN);
---
> 	oldquit = (int (*)())(long)signal(SIGQUIT, SIG_IGN);
> 	oldhup = (int (*)())(long)signal(SIGHUP, SIG_IGN);
> 	oldintr = (int (*)())(long)signal(SIGINT, SIG_IGN);
141c204
< 		while (*p2++ = *p1++)
---
> 		while ((*p2++ = *p1++))
154c217
< 	quit();
---
> 	quit(0);
157c220,221
< commands()
---
> int
> commands(void)
159,160c223,224
< 	int getfile(), gettty();
< 	register *a1, c;
---
> 	int getfile(void), gettty(void);
> 	register int *a1, c;
203a268
> 		/* fallthrough */
265a331
> 		/* fallthrough */
281a348
> 		/* fallthrough */
285c352,353
< 		quit();
---
> 		quit(0);
> 		/* fallthrough */
327a396
> 		/* fallthrough */
367c436
< 		return;
---
> 		return(0);
375c444
< address()
---
> address(void)
377c446,447
< 	register *a1, minus, c;
---
> 	register int *a1;
> 	register int minus, c;
471c541,542
< setdot()
---
> void
> setdot(void)
479c550,551
< setall()
---
> void
> setall(void)
490c562,563
< setnoaddr()
---
> void
> setnoaddr(void)
496c569,570
< nonzero()
---
> void
> nonzero(void)
502c576,577
< newline()
---
> void
> newline(void)
504c579
< 	register c;
---
> 	register int c;
518c593,594
< filename(comm)
---
> void
> filename(int comm)
521c597
< 	register c;
---
> 	register int c;
530c606
< 		while (*p2++ = *p1++)
---
> 		while ((*p2++ = *p1++))
550c626
< 		while (*p1++ = *p2++)
---
> 		while ((*p1++ = *p2++))
555c631,632
< exfile()
---
> void
> exfile(void)
565c642,643
< onintr()
---
> int
> onintr(int sig)
566a645
> 	(void)sig;
570a650
> 	return 0;
573c653,654
< onhup()
---
> int
> onhup(int sig)
574a656
> 	(void)sig;
585c667,668
< 	quit();
---
> 	quit(0);
> 	return(0);
588,589c671,672
< error(s)
< char *s;
---
> int
> error(char *s)
591c674
< 	register c;
---
> 	register int c;
611a695
> 	return(0);
614c698,699
< getchr()
---
> int
> getchr(void)
617c702
< 	if (lastc=peekc) {
---
> 	if ((lastc=peekc)) {
633c718,719
< gettty()
---
> int
> gettty(void)
635c721
< 	register c;
---
> 	register int c;
659c745,746
< getfile()
---
> int
> getfile(void)
661c748
< 	register c;
---
> 	register int c;
695c782,783
< putfile()
---
> int
> putfile(void)
699c787
< 	register nib;
---
> 	register int nib;
731a820
> 	return(0);
734,736c823,824
< append(f, a)
< int *a;
< int (*f)();
---
> int
> append(int (*f)(), int *a)
738c826
< 	register *a1, *a2, *rdot;
---
> 	register int *a1, *a2, *rdot;
744c832
< 		if ((dol-zero)+1 >= nlall) {
---
> 		if ((unsigned)((dol-zero)+1) >= nlall) {
768c856,857
< callunix()
---
> int
> callunix(void)
770c859
< 	register (*savint)(), pid, rpid;
---
> 	register int (*savint)(), pid, rpid;
780c869
< 	savint = signal(SIGINT, SIG_IGN);
---
> 	savint = (int (*)())(long)signal(SIGINT, SIG_IGN);
784a874
> 	return(0);
787c877,878
< quit()
---
> int
> quit(int sig)
788a880
> 	(void)sig;
797c889,890
< delete()
---
> int
> delete(void)
802a896
> 	return 0;
805,806c899,900
< rdelete(ad1, ad2)
< int *ad1, *ad2;
---
> int
> rdelete(int *ad1, int *ad2)
808c902
< 	register *a1, *a2, *a3;
---
> 	register int *a1, *a2, *a3;
821a916
> 	return(0);
824c919,920
< gdelete()
---
> int
> gdelete(void)
826c922
< 	register *a1, *a2, *a3;
---
> 	register int *a1, *a2, *a3;
831c927
< 			return;
---
> 			return(0);
842a939
> 	return(0);
846c943
< getline(tl)
---
> getline(int tl)
849c946
< 	register nl;
---
> 	register int nl;
855c952
< 	while (*lp++ = *bp++)
---
> 	while ((*lp++ = *bp++))
863c960,961
< putline()
---
> int
> putline(void)
866c964
< 	register nl;
---
> 	register int nl;
875c973
< 	while (*bp = *lp++) {
---
> 	while ((*bp = *lp++)) {
892c990
< getblock(atl, iof)
---
> getblock(int atl, int iof)
894,895c992
< 	extern read(), write();
< 	register bno, off;
---
> 	register int bno, off;
941,943c1038,1039
< blkio(b, buf, iofcn)
< char *buf;
< int (*iofcn)();
---
> int
> blkio(int b, char *buf, int (*iofcn)())
948a1045
> 	return 0;
951c1048,1049
< init()
---
> int
> init(void)
953c1051
< 	register *markp;
---
> 	register int *markp;
970a1069
> 	return(0);
973c1072,1073
< global(k)
---
> int
> global(int k)
976c1076
< 	register c;
---
> 	register int c;
1012c1112
< 		return;
---
> 		return(0);
1022a1123
> 	return(0);
1025c1126,1127
< join()
---
> int
> join(void)
1028c1130
< 	register *a1;
---
> 	register int *a1;
1033c1135
< 		while (*gp = *lp++)
---
> 		while ((*gp = *lp++))
1039c1141
< 	while (*lp++ = *gp++)
---
> 	while ((*lp++ = *gp++))
1044a1147
> 	return(0);
1047c1150,1151
< substitute(inglob)
---
> int
> substitute(int inglob)
1049c1153
< 	register *markp, *a1, nl;
---
> 	register int *markp, *a1, nl;
1051c1155
< 	int getsub();
---
> 	int getsub(void);
1083a1188
> 	return(0);
1086c1191,1192
< compsub()
---
> int
> compsub(void)
1088c1194
< 	register seof, c;
---
> 	register int seof, c;
1121c1227,1228
< getsub()
---
> int
> getsub(void)
1128c1235
< 	while (*p1++ = *p2++)
---
> 	while ((*p1++ = *p2++))
1134c1241,1242
< dosub()
---
> int
> dosub(void)
1144c1252
< 	while (c = *rp++&0377) {
---
> 	while ((c = *rp++&0377)) {
1158c1266
< 	while (*sp++ = *lp++)
---
> 	while ((*sp++ = *lp++))
1163c1271
< 	while (*lp++ = *sp++)
---
> 	while ((*lp++ = *sp++))
1164a1273
> 	return(0);
1168,1169c1277
< place(sp, l1, l2)
< register char *sp, *l1, *l2;
---
> place(register char *sp, register char *l1, register char *l2)
1180c1288,1289
< move(cflag)
---
> int
> move(int cflag)
1183c1292
< 	int getcopy();
---
> 	int getcopy(void);
1209c1318
< 			return;
---
> 			return(0);
1220a1330
> 	return(0);
1223,1224c1333,1334
< reverse(a1, a2)
< register int *a1, *a2;
---
> int
> reverse(register int *a1, register int *a2)
1231c1341
< 			return;
---
> 			return(0);
1237c1347,1348
< getcopy()
---
> int
> getcopy(void)
1245c1356,1357
< compile(aeof)
---
> int
> compile(int aeof)
1247c1359
< 	register eof, c;
---
> 	register int eof, c;
1259c1371
< 		return;
---
> 		return(0);
1277c1389
< 			return;
---
> 			return(0);
1371a1484
> 	return(0);
1374,1375c1487,1488
< execute(gf, addr)
< int *addr;
---
> int
> execute(int gf, int *addr)
1380,1381c1493,1494
< 		braslist[c] = 0;
< 		braelist[c] = 0;
---
> 		braslist[(unsigned char)c] = 0;
> 		braelist[(unsigned char)c] = 0;
1388c1501
< 		while (*p1++ = *p2++)
---
> 		while ((*p1++ = *p2++))
1425,1426c1538,1539
< advance(lp, ep)
< register char *ep, *lp;
---
> int
> advance(register char *lp, register char *ep)
1467c1580
< 		braslist[*ep++] = lp;
---
> 		braslist[(unsigned char)*ep++] = lp;
1471c1584
< 		braelist[*ep++] = lp;
---
> 		braelist[(unsigned char)*ep++] = lp;
1532,1534c1645,1646
< backref(i, lp)
< register i;
< register char *lp;
---
> int
> backref(register int i, register char *lp)
1545,1546c1657,1658
< cclass(set, c, af)
< register char *set, c;
---
> int
> cclass(register char *set, register int c, int af)
1548c1660
< 	register n;
---
> 	register int n;
1559c1671,1672
< putd()
---
> int
> putd(void)
1561c1674
< 	register r;
---
> 	register int r;
1567a1681
> 	return(0);
1570,1571c1684,1685
< puts(sp)
< register char *sp;
---
> int
> puts(register char *sp)
1576a1691
> 	return(0);
1582c1697,1698
< putchr(ac)
---
> int
> putchr(int ac)
1585c1701
< 	register c;
---
> 	register int c;
1621c1737
< 		return;
---
> 		return(0);
1623a1740
> 	return(0);
1625,1628c1742,1743
< crblock(permp, buf, nchar, startn)
< char *permp;
< char *buf;
< long startn;
---
> int
> crblock(char *permp, char *buf, int nchar, long startn)
1651a1767
> 	return(0);
1654c1770,1771
< getkey()
---
> int
> getkey(void)
1660c1777
< 	register c;
---
> 	register int c;
1662c1779
< 	sig = signal(SIGINT, SIG_IGN);
---
> 	sig = (int (*)())(long)signal(SIGINT, SIG_IGN);
1685,1686c1802,1803
< crinit(keyp, permp)
< char	*keyp, *permp;
---
> int
> crinit(char *keyp, char *permp)
1689c1806
< 	register i;
---
> 	register int i;
1748,1749c1865,1866
< makekey(a, b)
< char *a, *b;
---
> int
> makekey(char *a, char *b)
1761a1879
> 	return(0);
```

### usr/src/libc/sys/ftime.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/v6/ftime.c unix-v7-c99/usr/src/libc/sys/ftime.c || true
```

Expect:

```
1d0
< #include <sys/types.h>
4,9c3,6
< static struct timeb gorp = {
< 	0L,
< 	0,
< 	5*60,
< 	1
< };
---
> #define S_FTIME 35
> int syscall3(int, int, int, int);
> int
> ftime(struct timeb *gorpp)
11,12d7
< ftime(gorpp)
< struct timeb *gorpp;
14,15c9
< 	*gorpp = gorp;
< 	return(0);
---
> 	return(syscall3(S_FTIME, (int)gorpp, 0, 0));
```

### usr/src/libc/sys/gtty.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/v6/gtty.c unix-v7-c99/usr/src/libc/sys/gtty.c || true
```

Expect:

```
1,3c1,4
< gtty(fd, buf)
< int fd;
< int *buf;
---
> #include <sgtty.h>
> int ioctl(int, int, char *);
> int
> gtty(int fd, struct sgttyb *ap)
5,7c6
< 	if (syscall(32, fd, 0, buf, 0, 0) < 0)
< 		return(-1);
< 	return(0);
---
> 	return(ioctl(fd, TIOCGETP, (char *)ap));
```

### usr/src/libc/sys/stty.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/stty.c unix-v7-c99/usr/src/libc/sys/stty.c || true
```

Expect:

```
1,3d0
< /*
<  * Writearound to old stty and gtty system calls
<  */
7,11c4
< stty(fd, ap)
< struct sgtty *ap;
< {
< 	return(ioctl(fd, TIOCSETP, ap));
< }
---
> int ioctl(int, int, char *);
13,14c6,7
< gtty(fd, ap)
< struct sgtty *ap;
---
> int
> stty(int fd, struct sgttyb *ap)
16c9
< 	return(ioctl(fd, TIOCGETP, ap));
---
> 	return(ioctl(fd, TIOCSETP, (char *)ap));
```

### usr/src/libc/gen/sleep.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/sleep.c unix-v7-c99/usr/src/libc/gen/sleep.c || true
```

Expect:

```
4a5,8
> static void sleepx(int signo);
> extern void (*signal(int sig, void (*fun)(int)))(int);
> extern int alarm(int n);
> extern int pause(void);
6,7c10,11
< sleep(n)
< unsigned n;
---
> unsigned
> sleep(unsigned n)
9d12
< 	int sleepx();
11c14
< 	int (*alsig)() = SIG_DFL;
---
> 	void (*alsig)(int) = SIG_DFL;
14c17
< 		return;
---
> 		return(0);
19c22
< 		return;
---
> 		return(0);
36,37c39,40
< static
< sleepx()
---
> static void
> sleepx(int signo)
38a42
> 	(void)signo;
```

### usr/src/libc/stdio/popen.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/popen.c unix-v7-c99/usr/src/libc/stdio/popen.c || true
```

Expect:

```
14c14,15
< 	register myside, hisside, pid;
---
> 	register int myside, hisside, pid;
> 	int stdside;
23c24,26
< 		dup2(hisside, tst(0, 1));
---
> 		stdside = tst(0, 1);
> 		close(stdside);
> 		dup(hisside);
34a38
> int
38c42
< 	register f, r, (*hstat)(), (*istat)(), (*qstat)();
---
> 	register int f, r, (*hstat)(), (*istat)(), (*qstat)();
43,45c47,49
< 	istat = signal(SIGINT, SIG_IGN);
< 	qstat = signal(SIGQUIT, SIG_IGN);
< 	hstat = signal(SIGHUP, SIG_IGN);
---
> 	istat = (int (*)())signal(SIGINT, (int)SIG_IGN);
> 	qstat = (int (*)())signal(SIGQUIT, (int)SIG_IGN);
> 	hstat = (int (*)())signal(SIGHUP, (int)SIG_IGN);
50,52c54,56
< 	signal(SIGINT, istat);
< 	signal(SIGQUIT, qstat);
< 	signal(SIGHUP, hstat);
---
> 	signal(SIGINT, (int)istat);
> 	signal(SIGQUIT, (int)qstat);
> 	signal(SIGHUP, (int)hstat);
```

### usr/sys/h/tty.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/tty.h unix-v7-c99/usr/sys/h/tty.h || true
```

Expect:

```
59c59
< 		struct tc;
---
> 		struct tc tc;
64c64
< #define	tun	tp->t_un
---
> #define	tun	tp->t_un.tc
```

### usr/sys/sys/acct.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/acct.c unix-v7-c99/usr/sys/sys/acct.c || true
```

Expect:

```
8d7
< #include "../h/seg.h"
14c13,14
< sysacct()
---
> void
> sysacct(void)
47a48
> int compress(time_t t);
51c52,53
< acct()
---
> void
> acct(void)
53c55
< 	register i;
---
> 	register int i;
60c62
< 	for (i=0; i<sizeof(acctbuf.ac_comm); i++)
---
> 	for (i=0; i<(int)sizeof(acctbuf.ac_comm); i++)
88,89c90,91
< compress(t)
< register time_t t;
---
> int
> compress(time_t t)
91c93
< 	register exp = 0, round = 0;
---
> 	register int exp = 0, round = 0;
113c115,116
< syslock()
---
> void
> syslock(void)
```

### usr/sys/sys/alloc.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/alloc.c unix-v7-c99/usr/sys/sys/alloc.c || true
```

Expect:

```
11a12,19
> void sleep(caddr_t chan, int pri);
> void wakeup(caddr_t chan);
> void prdev(char *str, dev_t dev);
> void panic(char *s);
> void brelse(struct buf *bp);
> void bwrite(struct buf *bp);
> void bflush(dev_t dev);
> void clrbuf(struct buf *bp);
13a22
> int badblock(register struct filsys *fp, daddr_t bn, dev_t dev);
26,27c35
< alloc(dev)
< dev_t dev;
---
> alloc(dev_t dev)
78,80c86,87
< free(dev, bno)
< dev_t dev;
< daddr_t bno;
---
> void
> free(dev_t dev, daddr_t bno)
120,123c127,128
< badblock(fp, bn, dev)
< register struct filsys *fp;
< daddr_t bn;
< dev_t dev;
---
> int
> badblock(register struct filsys *fp, daddr_t bn, dev_t dev)
145,146c150
< ialloc(dev)
< dev_t dev;
---
> ialloc(dev_t dev)
223,225c227,228
< ifree(dev, ino)
< dev_t dev;
< ino_t ino;
---
> void
> ifree(dev_t dev, ino_t ino)
257,258c260
< getfs(dev)
< dev_t dev;
---
> getfs(dev_t dev)
286c288,289
< update()
---
> void
> update(void)
```

### usr/sys/sys/fio.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/fio.c unix-v7-c99/usr/sys/sys/fio.c || true
```

Expect:

```
9c9
< #include "../h/reg.h"
---
> #include "../h/mount.h"
10a11,17
> void wakeup(caddr_t chan);
> void printf(char *fmt, ...);
> void fstat(void);
> void close(void);
> void dup(void);
> void seek(void);
> void read(void);
20,21c27
< getf(f)
< register int f;
---
> getf(register int f)
45,46c51,52
< closef(fp)
< register struct file *fp;
---
> void
> closef(register struct file *fp)
102,103c108,109
< openi(ip, rw)
< register struct inode *ip;
---
> void
> openi(register struct inode *ip, int rw)
114c120
< 		if(maj >= nchrdev)
---
> 		if(maj >= (unsigned int)nchrdev)
121c127
< 		if(maj >= nblkdev)
---
> 		if(maj >= (unsigned int)nblkdev)
144,145c150,151
< access(ip, mode)
< register struct inode *ip;
---
> int
> access(register struct inode *ip, int mode)
147c153
< 	register m;
---
> 	register int m;
185c191
< owner()
---
> owner(void)
204c210,211
< suser()
---
> int
> suser(void)
218c225,226
< ufalloc()
---
> int
> ufalloc(void)
220c228
< 	register i;
---
> 	register int i;
242c250
< falloc()
---
> falloc(void)
245c253
< 	register i;
---
> 	register int i;
```

### usr/sys/sys/pipe.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/pipe.c unix-v7-c99/usr/sys/sys/pipe.c || true
```

Expect:

```
7c7,8
< #include "../h/reg.h"
---
> void sleep(caddr_t chan, int pri);
> void wakeup(caddr_t chan);
25c26,27
< pipe()
---
> void
> pipe(void)
61,62c63,64
< readp(fp)
< register struct file *fp;
---
> void
> readp(register struct file *fp)
116,117c118,119
< writep(fp)
< register struct file *fp;
---
> void
> writep(register struct file *fp)
119c121
< 	register c;
---
> 	register int c;
189,190c191,192
< plock(ip)
< register struct inode *ip;
---
> void
> plock(register struct inode *ip)
207,208c209,210
< prele(ip)
< register struct inode *ip;
---
> void
> prele(register struct inode *ip)
```

### usr/sys/sys/rdwri.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/rdwri.c unix-v7-c99/usr/sys/sys/rdwri.c || true
```

Expect:

```
7a8,12
> void clrbuf(struct buf *bp);
> void brelse(struct buf *bp);
> void bdwrite(struct buf *bp);
> void bwrite(struct buf *bp);
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
136,137c142,143
< max(a, b)
< unsigned a, b;
---
> unsigned
> max(unsigned a, unsigned b)
149,150c155,156
< min(a, b)
< unsigned a, b;
---
> unsigned
> min(unsigned a, unsigned b)
173,175c179,180
< iomove(cp, n, flag)
< register caddr_t cp;
< register n;
---
> void
> iomove(register caddr_t cp, register int n, int flag)
177c182
< 	register t;
---
> 	register int t;
186,189c191
< 			if (u.u_segflg==0)
< 				t = copyin(u.u_base, (caddr_t)cp, n);
< 			else
< 				t = copyiin(u.u_base, (caddr_t)cp, n);
---
> 			t = copyin(u.u_base, (caddr_t)cp, n);
191,194c193
< 			if (u.u_segflg==0)
< 				t = copyout((caddr_t)cp, u.u_base, n);
< 			else
< 				t = copyiout((caddr_t)cp, u.u_base, n);
---
> 			t = copyout((caddr_t)cp, u.u_base, n);
```

### usr/sys/sys/sig.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/sig.c unix-v7-c99/usr/sys/sys/sig.c || true
```

Expect:

```
7d6
< #include "../h/reg.h"
9a9,37
> void sleep(caddr_t chan, int pri);
> void wakeup(caddr_t chan);
> void setrun(struct proc *p);
> int fsig(struct proc *p);
> void psignal(struct proc *p, int sig);
> int issig(void);
> int procxmt(void);
> int core(void);
> void swtch(void);
> void exit(int rv);
> void itrunc(struct inode *ip);
> void expand(int newsize);
> void copyseg(int from, int to);
> void clearseg(int a);
> int estabur(unsigned nt, unsigned nd, unsigned ns, int sep, int xrw);
> int fubyte(caddr_t addr);
> int fuword(caddr_t addr);
> int suword(caddr_t addr, int v);
> struct inode *namei(int (*func)(void), int flag);
> struct inode *maknode(int mode);
> int access(struct inode *ip, int mode);
> void writei(struct inode *ip);
> void iput(struct inode *ip);
> int save(int *lp);
> void bcopy(char *from, char *to, unsigned int n);
> #define	SINCR	20
> #define	ARM_SP	13
> #define	ARM_LR	14
> #define	ARM_PC	15
39,40c67,68
< signal(pgrp, sig)
< register pgrp;
---
> void
> signal(register int pgrp, int sig)
55,57c83,84
< psignal(p, sig)
< register struct proc *p;
< register sig;
---
> void
> psignal(register struct proc *p, register int sig)
81c108,109
< issig()
---
> int
> issig(void)
83c111
< 	register n;
---
> 	register int n;
96a125,141
>  * sigreturn: invoked by the signal trampoline (UENTRY_SIGTRAMP) to
>  * restore the pre-signal pc/r0/lr/sp that sendsig() pushed on the user
>  * stack.  trap()'s tail writes r0 from u.u_r.r_val1, so the restored r0
>  * is returned through there.
>  */
> void
> sigreturn(void)
> {
> 	register int *r = u.u_ar0;
> 	register unsigned int sp = (unsigned int)r[ARM_SP];
> 	r[ARM_PC] = *(int *)sp;
> 	u.u_r.r_val1 = *(int *)(sp + 4);
> 	r[ARM_LR] = *(int *)(sp + 8);
> 	r[ARM_SP] = (int)(sp + 12);
> 	u.u_error = 0;
> }
> /*
102c147,148
< stop()
---
> void
> stop(void)
118c164,181
< 	exit(fsig(u.u_procp));
---
> 	exit(0x100 | fsig(u.u_procp));
> }
> static void
> sendsig(int handler, int sig)
> {
> 	register int *r;
> 	register unsigned int sp;
> 	r = u.u_ar0;
> 	if(r == NULL)
> 		return;
> 	sp = (unsigned int)r[ARM_SP] - 12U;
> 	*(volatile unsigned int *)sp = (unsigned int)r[ARM_PC];
> 	*(volatile unsigned int *)(sp + 4) = (unsigned int)r[0];
> 	*(volatile unsigned int *)(sp + 8) = (unsigned int)r[ARM_LR];
> 	r[ARM_SP] = (int)sp;
> 	r[ARM_LR] = (int)UENTRY_SIGTRAMP;
> 	r[ARM_PC] = (int)handler;
> 	r[0] = sig;
128c191,192
< psig()
---
> void
> psig(void)
130c194
< 	register n, p;
---
> 	register int n, p;
134,137d197
< 	if (u.u_fpsaved==0) {
< 		savfp(&u.u_fps);
< 		u.u_fpsaved = 1;
< 	}
148c208
< 		sendsig((caddr_t)p, n);
---
> 		sendsig(p, n);
165c225
< 	exit(n);
---
> 	exit(0x100 | n);
172,173c232,233
< fsig(p)
< struct proc *p;
---
> int
> fsig(struct proc *p)
175c235
< 	register n, i;
---
> 	register int n, i;
196c256,257
< core()
---
> int
> core(void)
200c261
< 	extern schar();
---
> 	extern int schar(void);
237,238c298,299
< grow(sp)
< unsigned sp;
---
> int
> grow(unsigned sp)
240c301
< 	register si, i;
---
> 	register int si, i;
242c303
< 	register a;
---
> 	register int a;
267c328,329
< ptrace()
---
> void
> ptrace(void)
313c375,376
< procxmt()
---
> int
> procxmt(void)
316c379
< 	register *p;
---
> 	register int *p;
328c391
< 		if (fuibyte((caddr_t)ipc.ip_addr) == -1)
---
> 		if (fubyte((caddr_t)ipc.ip_addr) == -1)
330c393
< 		ipc.ip_data = fuiword((caddr_t)ipc.ip_addr);
---
> 		ipc.ip_data = fuword((caddr_t)ipc.ip_addr);
345c408
< 		ipc.ip_data = ((physadr)&u)->r[i>>1];
---
> 		ipc.ip_data = *(int *)((char *)&u + i);
354,355c417,419
< 		if (xp = u.u_procp->p_textp) {
< 			if (xp->x_count!=1 || xp->x_iptr->i_mode&ISVTX)
---
> 		xp = u.u_procp->p_textp;
> 		if (xp != NULL) {
> 			if (xp->x_count!=1 || (xp->x_iptr->i_mode&ISVTX))
360,361c424,425
< 		i = suiword((caddr_t)ipc.ip_addr, 0);
< 		suiword((caddr_t)ipc.ip_addr, ipc.ip_data);
---
> 		i = suword((caddr_t)ipc.ip_addr, 0);
> 		suword((caddr_t)ipc.ip_addr, ipc.ip_data);
379c443,445
< 		p = (int *)&((physadr)&u)->r[i>>1];
---
> 		if (i<0 || i+(int)sizeof(int) > ctob(USIZE))
> 			goto error;
> 		p = (int *)((char *)&u + i);
382,389d447
< 		for (i=0; i<8; i++)
< 			if (p == &u.u_ar0[regloc[i]])
< 				goto ok;
< 		if (p == &u.u_ar0[RPS]) {
< 			ipc.ip_data |= 0170000;	/* assure user space */
< 			ipc.ip_data &= ~0340;	/* priority 0 */
< 			goto ok;
< 		}
399d456
< 		u.u_ar0[RPS] |= TBIT;
401,402c458,462
< 		if ((int)ipc.ip_addr != 1)
< 			u.u_ar0[PC] = (int)ipc.ip_addr;
---
> 		if ((int)ipc.ip_addr != 1) {
> 			p = u.u_ar0;
> 			if (p != NULL)
> 				p[ARM_PC] = (int)ipc.ip_addr;
> 		}
410c470,471
< 		exit(fsig(u.u_procp));
---
> 		exit(0x100 | fsig(u.u_procp));
> 		return(1);
```

### usr/sys/sys/subr.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/subr.c unix-v7-c99/usr/sys/sys/subr.c || true
```

Expect:

```
3d2
< #include "../h/conf.h"
7a7,8
> void bdwrite(struct buf *bp);
> void brelse(struct buf *bp);
18,20c19
< bmap(ip, bn, rwflg)
< register struct inode *ip;
< daddr_t bn;
---
> bmap(register struct inode *ip, daddr_t bn, int rwflg)
22c21
< 	register i;
---
> 	register int i;
117c116
< 	if(i < NINDIR-1)
---
> 	if((unsigned)i < NINDIR-1)
128,129c127,128
< passc(c)
< register c;
---
> int
> passc(register int c)
131d129
< 	register id;
133c131
< 	if((id = u.u_segflg) == 1)
---
> 	if(u.u_segflg == 1)
135,139c133,136
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
153c150,151
< cpass()
---
> int
> cpass(void)
155c153
< 	register c, id;
---
> 	register int c;
159c157
< 	if((id = u.u_segflg) == 1)
---
> 	if(u.u_segflg == 1)
161,165c159,162
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
176c173,174
< nodev()
---
> int
> nodev(void)
179a178
> 	return(0);
186c185,186
< nulldev()
---
> int
> nulldev(void)
187a188
> 	return(0);
193,195c194,195
< bcopy(from, to, count)
< caddr_t from, to;
< register count;
---
> void
> bcopy(caddr_t from, caddr_t to, register unsigned int count)
```

### usr/sys/sys/sys1.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/sys1.c unix-v7-c99/usr/sys/sys/sys1.c || true
```

Expect:

```
12a13,53
> void exec(void);
> void exece(void);
> int getxfile(struct inode *ip, int nargc);
> void setregs(void);
> void rexit(void);
> void exit(int rv);
> void wait(void);
> void fork(void);
> void sbreak(void);
> int malloc(struct map *mp, int size);
> void mfree(struct map *mp, int size, int a);
> void panic(char *s);
> void printf(char *fmt, ...);
> int fuword(caddr_t addr);
> int fubyte(caddr_t addr);
> int subyte(caddr_t addr, char c);
> int suword(caddr_t addr, int v);
> int copyout(caddr_t f, caddr_t t, unsigned int n);
> void bcopy(char *from, char *to, unsigned int n);
> void xfree(void);
> void xalloc(struct inode *ip);
> int estabur(unsigned nt, unsigned nd, unsigned ns, int sep, int xrw);
> void expand(int newsize);
> void clearseg(int a);
> void acct(void);
> void wakeup(caddr_t chan);
> void setrun(struct proc *p);
> void swtch(void);
> void closef(struct file *fp);
> int fsig(struct proc *p);
> void sleep(caddr_t chan, int pri);
> void psignal(struct proc *p, int sig);
> int newproc(void);
> void copyseg(int from, int to);
> void arm_sync_icache(void);
> void readi(struct inode *ip);
> void iput(struct inode *ip);
> int access(struct inode *ip, int mode);
> void plock(struct inode *ip);
> struct inode *namei(int (*func)(void), int flag);
> int uchar(void);
22c63,64
< exec()
---
> void
> exec(void)
28c70,82
< exece()
---
> /*
>  * exece: load and run a new program image.
>  *
>  * Args/environment are collected (NUL-separated) into e_argbuf from the
>  * old user image, then -- after getxfile() builds the new image -- written
>  * as the initial stack frame (see below).  This Armv7 image has ample RAM,
>  * so no swap round-trip is needed for the arg list.  e_argbuf is a per-
>  * process kernel-stack local rather than a shared global: getxfile() sleeps
>  * on its (interrupt-driven) disk read, so a global buffer would be clobbered
>  * by a second process exec-ing concurrently (e.g. both ends of a pipe).
>  */
> void
> exece(void)
30,32d83
< 	register nc;
< 	register char *cp;
< 	register struct buf *bp;
34c85
< 	int na, ne, bno, ucp, ap, c;
---
> 	register int nc, c, ap;
35a87,88
> 	int i;
> 	char e_argbuf[UARGLEN];
39,40d91
< 	bno = 0;
< 	bp = 0;
48,53d98
< 	/*
< 	 * Collect arguments on "file" in swap space.
< 	 */
< 	na = 0;
< 	ne = 0;
< 	nc = 0;
55,56c100
< 	if ((bno = malloc(swapmap,(NCARGS+BSIZE-1)/BSIZE)) == 0)
< 		panic("Out of swap");
---
> 	nc = 0;
58,70c102,104
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
---
> 		ap = fuword((caddr_t)uap->argp);
> 		uap->argp++;
> 		if (ap == 0)
72,73c106
< 		na++;
< 		if(ap == -1)
---
> 		if (ap == -1) {
74a108,109
> 			goto bad;
> 		}
76c111,115
< 			if (nc >= NCARGS-1)
---
> 			if ((c = fubyte((caddr_t)ap++)) < 0) {
> 				u.u_error = EFAULT;
> 				goto bad;
> 			}
> 			if (nc >= UARGLEN-2) {
78c117,133
< 			if ((c = fubyte((caddr_t)ap++)) < 0)
---
> 				goto bad;
> 			}
> 			e_argbuf[nc++] = c;
> 		} while (c);
> 	}
> 	e_argbuf[nc++] = 0;		/* empty string terminates arg list */
> 	if (uap->envp) for (;;) {
> 		ap = fuword((caddr_t)uap->envp);
> 		uap->envp++;
> 		if (ap == 0)
> 			break;
> 		if (ap == -1) {
> 			u.u_error = EFAULT;
> 			goto bad;
> 		}
> 		do {
> 			if ((c = fubyte((caddr_t)ap++)) < 0) {
80d134
< 			if (u.u_error)
82,86d135
< 			if ((nc&BMASK) == 0) {
< 				if (bp)
< 					bawrite(bp);
< 				bp = getblk(swapdev, swplo+bno+(nc>>BSHIFT));
< 				cp = bp->b_un.b_addr;
88,95c137,144
< 			nc++;
< 			*cp++ = c;
< 		} while (c>0);
< 	}
< 	if (bp)
< 		bawrite(bp);
< 	bp = 0;
< 	nc = (nc + NBPW-1) & ~(NBPW-1);
---
> 			if (nc >= UARGLEN-2) {
> 				u.u_error = E2BIG;
> 				goto bad;
> 			}
> 			e_argbuf[nc++] = c;
> 		} while (c);
> 	}
> 	e_argbuf[nc++] = 0;		/* empty string terminates env list */
100c149
< 	 * copy back arglist
---
> 	 * set SUID/SGID protections, if no tracing
103,122c152,156
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
---
> 	if ((u.u_procp->p_flag&STRC)==0) {
> 		if(ip->i_mode&ISUID)
> 			if(u.u_uid != 0) {
> 				u.u_uid = ip->i_uid;
> 				u.u_procp->p_uid = ip->i_uid;
124,130c158,219
< 			subyte((caddr_t)ucp++, (c = *cp++));
< 			nc++;
< 		} while(c&0377);
< 	}
< 	suword((caddr_t)ap, 0);
< 	suword((caddr_t)ucp, 0);
< 	setregs();
---
> 		if(ip->i_mode&ISGID)
> 			u.u_gid = ip->i_gid;
> 	} else
> 		psignal(u.u_procp, SIGTRC);
> 	/*
> 	 * Build the initial user stack frame at the top of the address space
> 	 * (V7 layout): the NUL-separated string image sits at the very top,
> 	 * with the argc/argv[]/0/envp[]/0 vector just below it and sp pointing
> 	 * at argc.  crt0 reads the frame straight off sp.  Placing the strings
> 	 * at the top is also what lets ps(1) recover a process's command line.
> 	 */
> 	{
> 		unsigned int strbase, sp;
> 		int na, ne, j, k;
> 		/* leave the top word zero: ps(1) treats a non-zero top-of-stack
> 		 * word as an argv pointer, so a string there would mislead it. */
> 		strbase = (USERSIZE - 4U - (unsigned)nc) & ~3U;
> 		for (i = 0; i < nc; i++)
> 			subyte((caddr_t)(strbase + (unsigned)i), e_argbuf[i]);
> 		i = 0;
> 		na = 0;
> 		while (e_argbuf[i]) {
> 			na++;
> 			while (e_argbuf[i])
> 				i++;
> 			i++;
> 		}
> 		i++;
> 		ne = 0;
> 		while (e_argbuf[i]) {
> 			ne++;
> 			while (e_argbuf[i])
> 				i++;
> 			i++;
> 		}
> 		sp = (strbase - 4U*(unsigned)(na + ne + 3)) & ~7U;
> 		suword((caddr_t)sp, na);
> 		i = 0;
> 		j = 0;
> 		while (j < na) {
> 			suword((caddr_t)(sp + 4U*(unsigned)(1 + j)),
> 			    (int)(strbase + (unsigned)i));
> 			while (e_argbuf[i])
> 				i++;
> 			i++;
> 			j++;
> 		}
> 		suword((caddr_t)(sp + 4U*(unsigned)(1 + na)), 0);
> 		i++;
> 		k = 0;
> 		while (k < ne) {
> 			suword((caddr_t)(sp + 4U*(unsigned)(1 + na + 1 + k)),
> 			    (int)(strbase + (unsigned)i));
> 			while (e_argbuf[i])
> 				i++;
> 			i++;
> 			k++;
> 		}
> 		suword((caddr_t)(sp + 4U*(unsigned)(1 + na + 1 + ne)), 0);
> 		setregs();
> 		u.u_ar0[R6] = (int)sp;	/* user stack pointer */
> 	}
132,135d220
< 	if (bp)
< 		brelse(bp);
< 	if(bno)
< 		mfree(swapmap, (NCARGS+BSIZE-1)/BSIZE, bno);
140,142c225,226
<  * Read in and set up memory for executed file.
<  * Zero return is normal;
<  * non-zero means only the text is being replaced
---
>  * ELF32 header / program-header subset (the Armv7 toolchain emits ELF;
>  * this replaces the PDP-11 a.out reader).
144,151c228,243
< getxfile(ip, nargc)
< register struct inode *ip;
< {
< 	register unsigned ds;
< 	register sep;
< 	register unsigned ts, ss;
< 	register i, overlay;
< 	long lsize;
---
> struct elf32_ehdr {
> 	unsigned char e_ident[16];
> 	unsigned short e_type;
> 	unsigned short e_machine;
> 	unsigned int e_version;
> 	unsigned int e_entry;
> 	unsigned int e_phoff;
> 	unsigned int e_shoff;
> 	unsigned int e_flags;
> 	unsigned short e_ehsize;
> 	unsigned short e_phentsize;
> 	unsigned short e_phnum;
> 	unsigned short e_shentsize;
> 	unsigned short e_shnum;
> 	unsigned short e_shstrndx;
> };
153,162c245,255
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
---
> struct elf32_phdr {
> 	unsigned int p_type;
> 	unsigned int p_offset;
> 	unsigned int p_vaddr;
> 	unsigned int p_paddr;
> 	unsigned int p_filesz;
> 	unsigned int p_memsz;
> 	unsigned int p_flags;
> 	unsigned int p_align;
> };
> #define	PT_LOAD	1
164,166c257,262
< 	u.u_base = (caddr_t)&u.u_exdata;
< 	u.u_count = sizeof(u.u_exdata);
< 	u.u_offset = 0;
---
> static void
> readbytes(struct inode *ip, caddr_t kbuf, unsigned int off, unsigned int n)
> {
> 	u.u_base = kbuf;
> 	u.u_count = n;
> 	u.u_offset = off;
169a266,283
> }
> /*
>  * Read in and set up memory for an ELF executable.
>  * The Armv7 user image is a flat 1 MB window; arm_sureg maps it, so we
>  * allocate the image, zero it, then read each PT_LOAD segment to its
>  * virtual address.  Entry goes through u_exdata.ux_entloc (used by
>  * setregs).  Zero return is normal.
>  */
> int
> getxfile(register struct inode *ip, int nargc)
> {
> 	struct elf32_ehdr eh;
> 	struct elf32_phdr ph;
> 	register int i;
> 	int n, low, stack;
> 	unsigned int end, maxend;
> 	(void)nargc;
> 	readbytes(ip, (caddr_t)&eh, 0, sizeof(eh));
172c286,287
< 	if (u.u_count!=0) {
---
> 	if(eh.e_ident[0] != 0x7f || eh.e_ident[1] != 'E' ||
> 	   eh.e_ident[2] != 'L' || eh.e_ident[3] != 'F' || eh.e_type != 2) {
176,181c291,303
< 	sep = 0;
< 	overlay = 0;
< 	if(u.u_exdata.ux_mag == 0407) {
< 		lsize = (long)u.u_exdata.ux_dsize + u.u_exdata.ux_tsize;
< 		u.u_exdata.ux_dsize = lsize;
< 		if (lsize != u.u_exdata.ux_dsize) {	/* check overflow */
---
> 	/*
> 	 * Find text and data sizes, and try them out for possible overflow.
> 	 */
> 	maxend = 0;
> 	for(i = 0; i < (int)eh.e_phnum; i++) {
> 		readbytes(ip, (caddr_t)&ph, eh.e_phoff + i*eh.e_phentsize,
> 		    sizeof(ph));
> 		if(u.u_error)
> 			goto bad;
> 		if(ph.p_type != PT_LOAD)
> 			continue;
> 		if(ph.p_vaddr >= USERSIZE || ph.p_memsz > USERSIZE - ph.p_vaddr ||
> 		   ph.p_filesz > ph.p_memsz) {
185,196c307,309
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
---
> 		end = ph.p_vaddr + ph.p_memsz;
> 		if(end > maxend)
> 			maxend = end;
198a312,327
> 	u.u_prof.pr_scale = 0;
> 	xfree();
> 	n = USIZE + (int)(USERSIZE >> 6);
> 	expand(n);
> 	low = (int)btoc(maxend);
> 	for(i = 0; i < low; i++)
> 		clearseg(u.u_procp->p_addr + USIZE + i);
> 	stack = (int)(USERSIZE >> 6) - SSIZE;
> 	for(i = stack; i < (int)(USERSIZE >> 6); i++)
> 		clearseg(u.u_procp->p_addr + USIZE + i);
> 	u.u_tsize = 0;
> 	u.u_dsize = (unsigned)low;
> 	u.u_ssize = SSIZE;
> 	u.u_sep = 0;
> 	if(estabur(0, u.u_dsize, u.u_ssize, 0, RO))
> 		goto bad;
200,202c329
< 	 * find text and data sizes
< 	 * try them out for possible
< 	 * overflow of max sizes
---
> 	 * Load each PT_LOAD segment to its virtual address.
204,224c331,334
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
---
> 	for(i = 0; i < (int)eh.e_phnum; i++) {
> 		readbytes(ip, (caddr_t)&ph, eh.e_phoff + i*eh.e_phentsize,
> 		    sizeof(ph));
> 		if(u.u_error)
226,248c336,341
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
---
> 		if(ph.p_type != PT_LOAD || ph.p_filesz == 0)
> 			continue;
> 		u.u_base = (caddr_t)ph.p_vaddr;
> 		u.u_count = ph.p_filesz;
> 		u.u_offset = ph.p_offset;
> 		u.u_segflg = 0;
250,268c343,347
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
---
> 		if(u.u_error)
> 			goto bad;
> 	}
> 	u.u_exdata.ux_entloc = eh.e_entry;
> 	arm_sync_icache();
270c349
< 	return(overlay);
---
> 	return(0);
276c355,356
< setregs()
---
> void
> setregs(void)
280c360
< 	register i;
---
> 	register int i;
286c366
< 		u.u_ar0[*cp++] = 0;
---
> 		u.u_ar0[(int)*cp++] = 0;
296a377
> 	u.u_acflag &= ~AFORK;
300d380
< 	u.u_acflag &= ~AFORK;
308c388,389
< rexit()
---
> void
> rexit(void)
325c406,407
< exit(rv)
---
> void
> exit(int rv)
377c459,460
< wait()
---
> void
> wait(void)
379c462
< 	register f;
---
> 	register int f;
422c505,506
< fork()
---
> void
> fork(void)
425c509
< 	register a;
---
> 	register int a;
456d539
< 	p1 = u.u_procp;
458c541,542
< 		u.u_r.r_val1 = p1->p_pid;
---
> 		/* child: fork() returns 0 */
> 		u.u_r.r_val1 = 0;
469,470c553
< out:
< 	u.u_ar0[R7] += NBPW;
---
> out:	;
477c560,561
< sbreak()
---
> void
> sbreak(void)
482c566
< 	register a, n, d;
---
> 	register int a, n, d;
497d580
< 	n += USIZE+u.u_ssize;
500,508c583,585
< 	u.u_dsize += d;
< 	if(d > 0)
< 		goto bigger;
< 	a = u.u_procp->p_addr + n - u.u_ssize;
< 	i = n;
< 	n = u.u_ssize;
< 	while(n--) {
< 		copyseg(a-d, a);
< 		a++;
---
> 	if((unsigned)n > (USERSIZE >> 6) - u.u_ssize) {
> 		u.u_error = ENOMEM;
> 		return;
510,511d586
< 	expand(i);
< 	return;
513,519c588,591
< bigger:
< 	expand(n);
< 	a = u.u_procp->p_addr + n;
< 	n = u.u_ssize;
< 	while(n--) {
< 		a--;
< 		copyseg(a-d, a);
---
> 	if(d > 0) {
> 		a = u.u_procp->p_addr + USIZE + (int)u.u_dsize;
> 		for(i = 0; i < d; i++)
> 			clearseg(a + i);
521,522c593,594
< 	while(d--)
< 		clearseg(--a);
---
> 	u.u_dsize += d;
> 	return;
```

### usr/sys/sys/sys2.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/sys2.c unix-v7-c99/usr/sys/sys/sys2.c || true
```

Expect:

```
5d4
< #include "../h/reg.h"
8a8,17
> extern void readp(struct file *);
> extern void writep(struct file *);
> extern void wdir(struct inode *);
> extern void itrunc(struct inode *);
> extern void openi(struct inode *, int);
> void rdwr(int mode);
> void write(void);
> void open(void);
> void creat(void);
> void open1(struct inode *ip, int mode, int trf);
12c21,22
< read()
---
> void
> read(void)
20c30,31
< write()
---
> void
> write(void)
30,31c41,42
< rdwr(mode)
< register mode;
---
> void
> rdwr(register int mode)
80c91,92
< open()
---
> void
> open(void)
98c110,111
< creat()
---
> void
> creat(void)
124,126c137,138
< open1(ip, mode, trf)
< register struct inode *ip;
< register mode;
---
> void
> open1(register struct inode *ip, register int mode, int trf)
163c175,176
< close()
---
> void
> close(void)
181c194,195
< seek()
---
> void
> seek(void)
209c223,224
< link()
---
> void
> link(void)
259c274,275
< mknod()
---
> void
> mknod(void)
290c306,307
< saccess()
---
> void
> saccess(void)
292c309
< 	register svuid, svgid;
---
> 	register int svuid, svgid;
```

### usr/sys/sys/sys3.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/sys3.c unix-v7-c99/usr/sys/sys/sys3.c || true
```

Expect:

```
5d4
< #include "../h/reg.h"
13a13,16
> extern void xumount(dev_t);
> void brelse(struct buf *bp);
> void stat1(struct inode *ip, struct stat *ub, off_t pipeadj);
> dev_t getmdev(void);
18c21,22
< fstat()
---
> void
> fstat(void)
36c40,41
< stat()
---
> void
> stat(void)
56,59c61,62
< stat1(ip, ub, pipeadj)
< register struct inode *ip;
< struct stat *ub;
< off_t pipeadj;
---
> void
> stat1(register struct inode *ip, struct stat *ub, off_t pipeadj)
94c97,98
< dup()
---
> void
> dup(void)
101c105
< 	register i, m;
---
> 	register int i, m;
131c135,136
< smount()
---
> void
> smount(void)
197c202,203
< sumount()
---
> void
> sumount(void)
203,205d208
< 	register struct a {
< 		char	*fspec;
< 	};
240c243
< getmdev()
---
> getmdev(void)
```

### usr/sys/sys/text.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/text.c unix-v7-c99/usr/sys/sys/text.c || true
```

Expect:

```
3d2
< #include "../h/map.h"
9a9
> #include "../h/map.h"
10a11,33
> struct map;
> int malloc(struct map *mp, int size);
> void mfree(struct map *mp, int size, int a);
> void panic(char *s);
> void swap(daddr_t blkno, int coreaddr, int count, int rdflg);
> void wakeup(caddr_t chan);
> void sleep(caddr_t chan, int pri);
> extern void xlock(struct text *);
> extern void xunlock(struct text *);
> extern void xccdec(struct text *);
> extern void xuntext(struct text *);
> void xswap(register struct proc *p, int ff, int os);
> extern void xexpand(struct text *);
> extern void xfree(void);
> extern void xalloc(struct inode *);
> void readi(struct inode *ip);
> void psignal(struct proc *p, int sig);
> void printf(char *fmt, ...);
> void iput(struct inode *ip);
> void sureg(void);
> void qswtch(void);
> int estabur(unsigned nt, unsigned nd, unsigned ns, int sep, int xrw);
> int save(int *lp);
22,23c45,46
< xswap(p, ff, os)
< register struct proc *p;
---
> void
> xswap(register struct proc *p, int ff, int os)
25c48
< 	register a;
---
> 	register int a;
50c73,74
< xfree()
---
> void
> xfree(void)
84,85c108,109
< xalloc(ip)
< register struct inode *ip;
---
> void
> xalloc(register struct inode *ip)
147,148c171,172
< xexpand(xp)
< register struct text *xp;
---
> void
> xexpand(register struct text *xp)
171,172c195,196
< xlock(xp)
< register struct text *xp;
---
> void
> xlock(register struct text *xp)
182,183c206,207
< xunlock(xp)
< register struct text *xp;
---
> void
> xunlock(register struct text *xp)
195,196c219,220
< xccdec(xp)
< register struct text *xp;
---
> void
> xccdec(register struct text *xp)
216,217c240,241
< xumount(dev)
< register dev;
---
> void
> xumount(register dev_t dev)
229,230c253,254
< xrele(ip)
< register struct inode *ip;
---
> void
> xrele(register struct inode *ip)
234c258
< 	if (ip->i_flag&ITEXT==0)
---
> 	if ((ip->i_flag&ITEXT)==0)
245,246c269,270
< xuntext(xp)
< register struct text *xp;
---
> void
> xuntext(register struct text *xp)
```

### usr/sys/sys/ureg.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/ureg.c unix-v7-c99/usr/sys/sys/ureg.c || true
```

Expect:

```
7a8,9
> int estabur(unsigned nt, unsigned nd, unsigned ns, int sep, int xrw);
> void arm_sureg(int *uisa, int *uisd, int nseg);
15c17,18
< sureg()
---
> void
> sureg(void)
17,18c20,22
< 	register *udp, *uap, *rdp;
< 	int *rap, *limudp;
---
> 	register int *udp, *uap, *rap;
> 	int auisa[16];
> 	int *limudp;
28,29c32
< 	rap = (int *)UISA;
< 	rdp = (int *)UISD;
---
> 	rap = &auisa[0];
33c36
< 		*rdp++ = *udp++;
---
> 		udp++;
34a38
> 	arm_sureg(auisa, &u.u_uisd[0], limudp - &u.u_uisd[0]);
48,49c52,53
< estabur(nt, nd, ns, sep, xrw)
< unsigned nt, nd, ns;
---
> int
> estabur(unsigned nt, unsigned nd, unsigned ns, int sep, int xrw)
51c55,61
< 	register a, *ap, *dp;
---
> 	(void)sep; (void)xrw;
> 	/*
> 	 * Armv7: user memory is mapped by page tables (arm_sureg), not the
> 	 * PDP-11 8-segment scheme, so the per-segment limit checks and the
> 	 * u_uisa/u_uisd prototype build do not apply.  Validate the total
> 	 * image size against maxmem and (re)load the page tables via sureg().
> 	 */
53,131c63,65
< 	if(sep) {
< 		if(cputype == 40)
< 			goto err;
< 		if(ctos(nt) > 8 || ctos(nd)+ctos(ns) > 8)
< 			goto err;
< 	} else
< 		if(ctos(nt)+ctos(nd)+ctos(ns) > 8)
< 			goto err;
< 	if(nt+nd+ns+USIZE > maxmem)
< 		goto err;
< 	a = 0;
< 	ap = &u.u_uisa[0];
< 	dp = &u.u_uisd[0];
< 	while(nt >= 128) {
< 		*dp++ = (127<<8) | xrw|TX;
< 		*ap++ = a;
< 		a += 128;
< 		nt -= 128;
< 	}
< 	if(nt) {
< 		*dp++ = ((nt-1)<<8) | xrw|TX;
< 		*ap++ = a;
< 	}
< 	if(sep)
< 	while(ap < &u.u_uisa[8]) {
< 		*ap++ = 0;
< 		*dp++ = 0;
< 	}
< 	a = USIZE;
< 	while(nd >= 128) {
< 		*dp++ = (127<<8) | RW;
< 		*ap++ = a;
< 		a += 128;
< 		nd -= 128;
< 	}
< 	if(nd) {
< 		*dp++ = ((nd-1)<<8) | RW;
< 		*ap++ = a;
< 		a += nd;
< 	}
< 	while(ap < &u.u_uisa[8]) {
< 		if(*dp &ABS) {
< 			dp++;
< 			ap++;
< 			continue;
< 		}
< 		*dp++ = 0;
< 		*ap++ = 0;
< 	}
< 	if(sep)
< 	while(ap < &u.u_uisa[16]) {
< 		if(*dp & ABS) {
< 			dp++;
< 			ap++;
< 			continue;
< 		}
< 		*dp++ = 0;
< 		*ap++ = 0;
< 	}
< 	a += ns;
< 	while(ns >= 128) {
< 		a -= 128;
< 		ns -= 128;
< 		*--dp = (127<<8) | RW;
< 		*--ap = a;
< 	}
< 	if(ns) {
< 		*--dp = ((128-ns)<<8) | RW | ED;
< 		*--ap = a-128;
< 	}
< 	if(!sep) {
< 		ap = &u.u_uisa[0];
< 		dp = &u.u_uisa[8];
< 		while(ap < &u.u_uisa[8])
< 			*dp++ = *ap++;
< 		ap = &u.u_uisd[0];
< 		dp = &u.u_uisd[8];
< 		while(ap < &u.u_uisd[8])
< 			*dp++ = *ap++;
---
> 	if((int)(nt+nd+ns+USIZE) > maxmem) {
> 		u.u_error = ENOMEM;
> 		return(-1);
136,138d69
< err:
< 	u.u_error = ENOMEM;
< 	return(-1);
```

### usr/src/cmd/sh/blok.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/blok.c unix-v7-c99/usr/src/cmd/sh/blok.c || true
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

### usr/src/cmd/sh/builtin.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/builtin.c unix-v7-c99/usr/src/cmd/sh/builtin.c || true
```

Expect:

```
1c1
< builtin()
---
> int builtin(void)
```

### usr/src/cmd/sh/cmd.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/cmd.c unix-v7-c99/usr/src/cmd/sh/cmd.c || true
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
> LOCAL IOPTR	inout(IOPTR lastio);
> LOCAL VOID	chkword(void);
> LOCAL VOID	chksym(INT sym);
> LOCAL TREPTR	term(INT flg);
> LOCAL TREPTR	makelist(INT type, TREPTR i, TREPTR r);
> LOCAL TREPTR	list(INT flg);
> LOCAL REGPTR	syncase(REG INT esym);
> LOCAL TREPTR	item(BOOL flag);
> LOCAL INT	skipnl(void);
> LOCAL VOID	prsym(INT sym);
> LOCAL VOID	synbad(void);
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
35a43
> 	REG FORKPTR	f;
37,38c45,47
< 	t=getstak(FORKTYPE);
< 	t->forktyp=flgs|TFORK; t->forktre=i; t->forkio=0;
---
> 	t=(TREPTR)getstak(FORKTYPE);
> 	f=(FORKPTR)t;
> 	f->forktyp=flgs|TFORK; f->forktre=i; f->forkio=0;
42,44c51
< LOCAL TREPTR	makelist(type,i,r)
< 	INT		type;
< 	TREPTR		i, r;
---
> LOCAL TREPTR	makelist(INT type, TREPTR i, TREPTR r)
46c53,54
< 	REG TREPTR	t;
---
> 	REG TREPTR	t = 0;
> 	REG LSTPTR	l;
50,52c58,61
< 	ELSE	t = getstak(LSTTYPE);
< 		t->lsttyp = type;
< 		t->lstlef = i; t->lstrit = r;
---
> 	ELSE	t = (TREPTR)getstak(LSTTYPE);
> 		l = (LSTPTR)t;
> 		l->lsttyp = type;
> 		l->lstlef = i; l->lstrit = r;
65,67c74
< TREPTR	cmd(sym,flg)
< 	REG INT		sym;
< 	INT		flg;
---
> TREPTR	cmd(REG INT sym, INT flg)
87a95
> 		/* fallthrough */
90c98
< 		IF e=cmd(sym,flg|MTFLG)
---
> 		IF (e=cmd(sym,flg|MTFLG))
98a107
> 		/* fallthrough */
116c125
< LOCAL TREPTR	list(flg)
---
> LOCAL TREPTR	list(INT flg)
134c143
< LOCAL TREPTR	term(flg)
---
> LOCAL TREPTR	term(INT flg)
150,151c159
< LOCAL REGPTR	syncase(esym)
< 	REG INT	esym;
---
> LOCAL REGPTR	syncase(REG INT esym)
156c164
< 	ELSE	REG REGPTR	r=getstak(REGTYPE);
---
> 	ELSE	REG REGPTR	r=(REGPTR)getstak(REGTYPE);
189,190c197
< LOCAL TREPTR	item(flag)
< 	BOOL		flag;
---
> LOCAL TREPTR	item(BOOL flag)
204c211,213
< 		   t=getstak(SWTYPE);
---
> 		   REG SWPTR	s;
> 		   t=(TREPTR)getstak(SWTYPE);
> 		   s=(SWPTR)t;
206c215
< 		   t->swarg=wdarg->argval;
---
> 		   s->swarg=wdarg->argval;
208,209c217,218
< 		   t->swlst=syncase(wdval==INSYM?ESSYM:KTSYM);
< 		   t->swtyp=TSW;
---
> 		   s->swlst=syncase(wdval==INSYM?ESSYM:KTSYM);
> 		   s->swtyp=TSW;
216,220c225,231
< 		   t=getstak(IFTYPE);
< 		   t->iftyp=TIF;
< 		   t->iftre=cmd(THSYM,NLFLG);
< 		   t->thtre=cmd(ELSYM|FISYM|EFSYM,NLFLG);
< 		   t->eltre=((w=wdval)==ELSYM ? cmd(FISYM,NLFLG) : (w==EFSYM ? (wdval=IFSYM, item(0)) : 0));
---
> 		   REG IFPTR	it;
> 		   t=(TREPTR)getstak(IFTYPE);
> 		   it=(IFPTR)t;
> 		   it->iftyp=TIF;
> 		   it->iftre=cmd(THSYM,NLFLG);
> 		   it->thtre=cmd(ELSYM|FISYM|EFSYM,NLFLG);
> 		   it->eltre=((w=wdval)==ELSYM ? cmd(FISYM,NLFLG) : (w==EFSYM ? (wdval=IFSYM, item(0)) : 0));
227,229c238,242
< 		   t=getstak(FORTYPE);
< 		   t->fortyp=TFOR;
< 		   t->forlst=0;
---
> 		   REG FORPTR	fr;
> 		   t=(TREPTR)getstak(FORTYPE);
> 		   fr=(FORPTR)t;
> 		   fr->fortyp=TFOR;
> 		   fr->forlst=0;
231c244
< 		   t->fornam=wdarg->argval;
---
> 		   fr->fornam=wdarg->argval;
234c247
< 			t->forlst=item(0);
---
> 			fr->forlst=(COMPTR)item(0);
241c254
< 		   t->fortre=cmd(wdval==DOSYM?ODSYM:KTSYM,NLFLG);
---
> 		   fr->fortre=cmd(wdval==DOSYM?ODSYM:KTSYM,NLFLG);
248,251c261,266
< 		   t=getstak(WHTYPE);
< 		   t->whtyp=(wdval==WHSYM ? TWH : TUN);
< 		   t->whtre = cmd(DOSYM,NLFLG);
< 		   t->dotre = cmd(ODSYM,NLFLG);
---
> 		   REG WHPTR	wh;
> 		   t=(TREPTR)getstak(WHTYPE);
> 		   wh=(WHPTR)t;
> 		   wh->whtyp=(wdval==WHSYM ? TWH : TUN);
> 		   wh->whtre = cmd(DOSYM,NLFLG);
> 		   wh->dotre = cmd(ODSYM,NLFLG);
262c277
< 		   p=getstak(PARTYPE);
---
> 		   p=(PARPTR)getstak(PARTYPE);
265c280
< 		   t=makefork(0,p);
---
> 		   t=makefork(0,(TREPTR)p);
272a288
> 		/* fallthrough */
278a295
> 		   REG COMPTR	c;
280,282c297,300
< 		   t=getstak(COMTYPE);
< 		   t->comio=io; /*initial io chain*/
< 		   argtail = &(t->comarg);
---
> 		   t=(TREPTR)getstak(COMTYPE);
> 		   c=(COMPTR)t;
> 		   c->comio=io; /*initial io chain*/
> 		   argtail = &(c->comarg);
286c304
< 			THEN	argp->argnxt=argset; argset=argp;
---
> 			THEN	argp->argnxt=(ARGPTR)argset; argset=(ARGPTR *)argp;
291c309
< 			THEN t->comio=inout(t->comio);
---
> 			THEN c->comio=inout(c->comio);
295c313
< 		   t->comtyp=TCOM; t->comset=argset; *argtail=0;
---
> 		   c->comtyp=TCOM; c->comset=(ARGPTR)argset; *argtail=0;
301c319
< 	IF io=inout(io)
---
> 	IF (io=inout(io))
308c326
< LOCAL VOID	skipnl()
---
> LOCAL INT	skipnl(void)
314,315c332
< LOCAL IOPTR	inout(lastio)
< 	IOPTR		lastio;
---
> LOCAL IOPTR	inout(IOPTR lastio)
334a352
> 		/* fallthrough */
350c368
< 	iop=getstak(IOTYPE); iop->ioname=wdarg->argval; iop->iofile=iof;
---
> 	iop=(IOPTR)getstak(IOTYPE); iop->ioname=wdarg->argval; iop->iofile=iof;
358c376
< LOCAL VOID	chkword()
---
> LOCAL VOID	chkword(void)
362a381
> 	return(0);
365c384
< LOCAL VOID	chksym(sym)
---
> LOCAL VOID	chksym(INT sym)
370a390
> 	return(0);
373c393
< LOCAL VOID	prsym(sym)
---
> LOCAL VOID	prsym(INT sym)
388a409
> 	return(0);
391c412
< LOCAL VOID	synbad()
---
> LOCAL VOID	synbad(void)
405a427
> 	return(0);
```

### usr/src/cmd/sh/ctype.h

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/ctype.h unix-v7-c99/usr/src/cmd/sh/ctype.h || true
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

### usr/src/cmd/sh/fault.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/fault.c unix-v7-c99/usr/src/cmd/sh/fault.c || true
```

Expect:

```
11a12,25
> extern int signal(int sig, int fun);
> extern void execexp(STRING t, INT in);
> extern void error(STRING s);
> extern void done(void);
> extern INT setbrk(INT n);
> extern void exitset(void);
> extern void free(void *p);
> VOID	stdsigs(void);
> INT	ignsig(INT n);
> VOID	getsig(INT n);
> VOID	oldsigs(void);
> VOID	clrsig(INT i);
> VOID	chktrap(void);
> VOID	fault(INT sig);
19,20c33,34
< VOID	fault(sig)
< 	REG INT		sig;
---
> VOID
> fault(INT sig)
24c38
< 	signal(sig,fault);
---
> 	signal(sig, (int)fault);
36a51
> 	return(0);
39c54,55
< stdsigs()
---
> VOID
> stdsigs(void)
44a61
> 	return(0);
47c64,65
< ignsig(n)
---
> INT
> ignsig(INT n)
57c75,76
< getsig(n)
---
> VOID
> getsig(INT n)
62c81
< 	THEN	signal(i,fault);
---
> 	THEN	signal(i, (int)fault);
63a83
> 	return(0);
66c86,87
< oldsigs()
---
> VOID
> oldsigs(void)
79a101
> 	return(0);
82,83c104,105
< clrsig(i)
< 	INT		i;
---
> VOID
> clrsig(INT i)
87c109
< 	THEN	signal(i,fault);
---
> 	THEN	signal(i, (int)fault);
89a112
> 	return(0);
92c115,116
< chktrap()
---
> VOID
> chktrap(void)
102c126
< 		IF t=trapcom[i]
---
> 		IF (t=trapcom[i])
108a133
> 	return(0);
```

### usr/src/cmd/sh/io.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/io.c unix-v7-c99/usr/src/cmd/sh/io.c || true
```

Expect:

```
12a13,29
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
16,17c33
< initf(fd)
< 	UFD		fd;
---
> INT initf(UFD fd)
21c37,38
< 	f->fdes=fd; f->fsiz=((flags&(oneflg|ttyflg))==0 ? BUFSIZ : 1);
---
> 	f->fdes=fd; f->fsiz=(fd > 2 ? BUFSIZ :
> 	    ((flags&(oneflg|ttyflg))==0 ? BUFSIZ : 1));
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

### usr/src/cmd/sh/macro.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/macro.c unix-v7-c99/usr/src/cmd/sh/macro.c || true
```

Expect:

```
12a13,31
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
18,19c37
< LOCAL STRING	copyto(endch)
< 	REG CHAR	endch;
---
> LOCAL STRING	copyto(INT endch)
26a45
> 	return(0);
29,30c48
< LOCAL	skipto(endch)
< 	REG CHAR	endch;
---
> LOCAL INT skipto(CHAR endch)
46a65
> 	return(0);
49,50c68
< LOCAL	getch(endch)
< 	CHAR		endch;
---
> LOCAL INT getch(CHAR endch)
62c80
< 		THEN	NAMPTR		n=NIL;
---
> 		THEN	NAMPTR		n=(NAMPTR)NIL;
69c87
< 			IF bra=(c==BRACE) THEN c=readc() FI
---
> 			IF (bra=(c==BRACE)) THEN c=readc() FI
71c89
< 			THEN	argp=relstak();
---
> 			THEN	argp=(STRING)(long)relstak();
83c101
< 				v=((c==0) ? cmdadr : (c<=dolc) ? dolv[c] : (dolg=0));
---
> 				v=((c==0) ? cmdadr : (c<=dolc) ? dolv[c] : (STRING)(long)(dolg=0));
104c122
< 				THEN	argp=relstak();
---
> 				THEN	argp=(STRING)(long)relstak();
115c133
< 				THEN	LOOP WHILE c = *v++
---
> 				THEN	LOOP WHILE (c = *v++)
148,149c166
< STRING	macro(as)
< 	STRING		as;
---
> STRING	macro(STRING as)
158c175
< 	push(&fb); estabf(as);
---
> 	push((FILE)&fb); estabf(as);
168c185
< LOCAL	comsubst()
---
> LOCAL INT comsubst(void)
197c214
< 	WHILE d=readc() DO pushstak(d|quote) OD
---
> 	WHILE (d=readc()) DO pushstak(d|quote) OD
204a222
> 	return(0);
209,210c227
< subst(in,ot)
< 	INT		in, ot;
---
> INT subst(INT in, INT ot)
218c235
< 	WHILE c=(getch(DQUOTE)&STRIP)
---
> 	WHILE (c=(getch(DQUOTE)&STRIP))
225a243
> 	return(0);
228c246
< LOCAL	flush(ot)
---
> LOCAL INT flush(INT ot)
232a251
> 	return(0);
```

### usr/src/cmd/sh/main.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/main.c unix-v7-c99/usr/src/cmd/sh/main.c || true
```

Expect:

```
25c25,55
< PROC VOID	exfile();
---
> LOCAL VOID	exfile(BOOL prof);
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

### usr/src/cmd/sh/name.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/name.c unix-v7-c99/usr/src/cmd/sh/name.c || true
```

Expect:

```
12c12
< PROC BOOL	chkid();
---
> LOCAL BOOL	chkid(STRING nam);
15,21c15,42
< NAMNOD	ps2nod	= {	NIL,		NIL,		ps2name},
< 	fngnod	= {	NIL,		NIL,		fngname},
< 	pathnod = {	NIL,		NIL,		pathname},
< 	ifsnod	= {	NIL,		NIL,		ifsname},
< 	ps1nod	= {	&pathnod,	&ps2nod,	ps1name},
< 	homenod = {	&fngnod,	&ifsnod,	homename},
< 	mailnod = {	&homenod,	&ps1nod,	mailname};
---
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

### usr/src/cmd/sh/setbrk.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/setbrk.c unix-v7-c99/usr/src/cmd/sh/setbrk.c || true
```

Expect:

```
12c12,13
< setbrk(incr)
---
> extern char *sbrk(int incr);
> BYTPTR setbrk(INT incr)
```

### usr/src/cmd/sh/stak.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/stak.c unix-v7-c99/usr/src/cmd/sh/stak.c || true
```

Expect:

```
11a12,14
> extern INT setbrk(INT n);
> extern void free(void *p);
> extern void rmtemp(IOPTR base);
18,19c21
< STKPTR	getstak(asize)
< 	INT		asize;
---
> STKPTR	getstak(INT asize)
30c32
< STKPTR	locstak()
---
> STKPTR	locstak(void)
43c45
< STKPTR	savstak()
---
> STKPTR	savstak(void)
49,50c51
< STKPTR	endstak(argp)
< 	REG STRING	argp;
---
> STKPTR	endstak(REG STRING argp)
54c55
< 	oldstak=stakbot; stakbot=staktop=round(argp,BYTESPERWORD);
---
> 	oldstak=stakbot; stakbot=staktop=(STKPTR)round(argp,BYTESPERWORD);
58,59c59
< VOID	tdystak(x)
< 	REG STKPTR 	x;
---
> VOID	tdystak(REG STKPTR x)
67c67,68
< 	rmtemp(x);
---
> 	rmtemp((IOPTR)x);
> 	return(0);
70c71
< stakchk()
---
> INT stakchk(void)
74a76
> 	return(0);
77,78c79
< STKPTR	cpystak(x)
< 	STKPTR		x;
---
> STKPTR	cpystak(STKPTR x)
```

### usr/src/cmd/cal.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/cal.c unix-v7-c99/usr/src/cmd/cal.c || true
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

### usr/src/cmd/grep.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/grep.c unix-v7-c99/usr/src/cmd/grep.c || true
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
119c125
< 			} else if (islower(*p)) {
---
> 			} else if (islower((unsigned char)*p)) {
121c127
< 				*s++ = toupper(*p);
---
> 				*s++ = toupper((unsigned char)*p);
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
250a257
> 			goto defchar;
262,263c269,270
< execute(file)
< char *file;
---
> void
> execute(char *file)
266c273
< 	register c;
---
> 	register int c;
324,325c331,332
< advance(lp, ep)
< register char *lp, *ep;
---
> int
> advance(register char *lp, register char *ep)
360c367
< 		braslist[*ep++] = lp;
---
> 		braslist[(unsigned char)*ep++] = lp;
364c371
< 		braelist[*ep++] = lp;
---
> 		braelist[(unsigned char)*ep++] = lp;
368,369c375,376
< 		bbeg = braslist[*ep];
< 		if (braelist[*ep]==0)
---
> 		bbeg = braslist[(unsigned char)*ep];
> 		if (braelist[(unsigned char)*ep]==0)
371c378
< 		ct = braelist[*ep++] - bbeg;
---
> 		ct = braelist[(unsigned char)*ep++] - bbeg;
379,380c386,387
< 		bbeg = braslist[*ep];
< 		if (braelist[*ep]==0)
---
> 		bbeg = braslist[(unsigned char)*ep];
> 		if (braelist[(unsigned char)*ep]==0)
382c389
< 		ct = braelist[*ep++] - bbeg;
---
> 		ct = braelist[(unsigned char)*ep++] - bbeg;
439,440c446,447
< succeed(f)
< char *f;
---
> void
> succeed(char *f)
442c449
< 	long ftell();
---
> 	long ftell(FILE *iop);
464,465c471,472
< ecmp(a, b, count)
< char	*a, *b;
---
> int
> ecmp(char *a, char *b, int count)
467c474
< 	register cc = count;
---
> 	register int cc = count;
473,474c480,481
< errexit(s, f)
< char *s, *f;
---
> void
> errexit(char *s, char *f)
```

### usr/src/cmd/cp.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/cp.c unix-v7-c99/usr/src/cmd/cp.c || true
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
52c53
< 		while(*bp++ = *p2++)
---
> 		while((*bp++ = *p2++))
56c57
< 		while(*bp = *p1++)
---
> 		while((*bp = *p1++))
73c74
< 	while(n = read(fold,  iobuf,  BSIZE)) {
---
> 	while((n = read(fold,  iobuf,  BSIZE))) {
```

### usr/src/cmd/mv.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/mv.c unix-v7-c99/usr/src/cmd/mv.c || true
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

### usr/src/cmd/chmod.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/chmod.c unix-v7-c99/usr/src/cmd/chmod.c || true
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
65c70
< 		while (o = what()) {
---
> 		while ((o = what())) {
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

### usr/src/cmd/chown.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/chown.c unix-v7-c99/usr/src/cmd/chown.c || true
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
51,52c52,53
< 	while(c = *s++)
< 		if(!isdigit(c))
---
> 	while ((c = *s++))
> 		if (!isdigit(c))
```

### usr/src/cmd/chgrp.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/chgrp.c unix-v7-c99/usr/src/cmd/chgrp.c || true
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
49,50c50,51
< 	while(c = *s++)
< 		if(!isdigit(c))
---
> 	while ((c = *s++))
> 		if (!isdigit(c))
```

### usr/src/cmd/sleep.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sleep.c unix-v7-c99/usr/src/cmd/sleep.c || true
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

### usr/src/cmd/touch.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/touch.c unix-v7-c99/usr/src/cmd/touch.c || true
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

### usr/src/cmd/tr.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/tr.c unix-v7-c99/usr/src/cmd/tr.c || true
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
50c52
< 		while(c = next(&string1))
---
> 		while((c = next(&string1)))
71c73
< 	while(d = next(&string2))
---
> 	while((d = next(&string2)))
81c83
< 		if(c = code[c&0377]&0377)
---
> 		if((c = code[c&0377]&0377))
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

### usr/src/cmd/dmesg.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/dmesg.c unix-v7-c99/usr/src/cmd/dmesg.c || true
```

Expect:

```
12a13
> #define KMSGBASE	0x7fff0000U
20,21c21,22
< 	{"_msgbuf"},
< 	{"_msgbufp"}
---
> 	{"_msgbuf",  0, 0},
> 	{"_msgbufp", 0, 0}
24,25c25,29
< main(argc, argv)
< char **argv;
---
> int done(char *);
> int pdate(void);
> int readlive(int);
> int
> main(int argc, char **argv)
29a34
> 	int live;
45a51
> 	live = 0;
47,52c53,73
< 	read(mem, msgbuf, MSGBUFS);
< 	lseek(mem, (long)nl[1].n_value, 0);
< 	read(mem, (char *)&msgbufp, sizeof(msgbufp));
< 	if (msgbufp < (char *)nl[0].n_value || msgbufp >= (char *)nl[0].n_value+MSGBUFS)
< 		done("Namelist mismatch\n");
< 	msgbufp += msgbuf - (char *)nl[0].n_value;
---
> 	if (read(mem, msgbuf, MSGBUFS) != MSGBUFS) {
> 		if (readlive(mem) < 0)
> 			done("Namelist mismatch\n");
> 		live = 1;
> 	}
> 	if (!live) {
> 		lseek(mem, (long)nl[1].n_value, 0);
> 		if (read(mem, (char *)&msgbufp, sizeof(msgbufp)) != sizeof(msgbufp)) {
> 			if (readlive(mem) < 0)
> 				done("Namelist mismatch\n");
> 			live = 1;
> 		}
> 	}
> 	if (!live &&
> 	    (msgbufp < (char *)nl[0].n_value || msgbufp >= (char *)nl[0].n_value+MSGBUFS)) {
> 		if (readlive(mem) < 0)
> 			done("Namelist mismatch\n");
> 		live = 1;
> 	}
> 	if (!live)
> 		msgbufp += msgbuf - (char *)nl[0].n_value;
84,85c105,120
< done(s)
< char *s;
---
> int
> readlive(int mem)
> {
> 	unsigned int idx;
> 	lseek(mem, (long)KMSGBASE, 0);
> 	if (read(mem, (char *)&idx, sizeof(idx)) != sizeof(idx))
> 		return(-1);
> 	if (idx >= MSGBUFS)
> 		return(-1);
> 	if (read(mem, msgbuf, MSGBUFS) != MSGBUFS)
> 		return(-1);
> 	msgbufp = &msgbuf[idx];
> 	return(0);
> }
> int
> done(char *s)
99a135
> 	return(0);
102c138,139
< pdate()
---
> int
> pdate(void)
104,105c141,142
< 	extern char *ctime();
< 	static firstime;
---
> 	extern char *ctime(long *t);
> 	static int firstime;
112a150
> 	return(0);
```

### usr/src/cmd/du.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/du.c unix-v7-c99/usr/src/cmd/du.c || true
```

Expect:

```
17,19c17
< long	descend();
< char	*rindex();
< char	*strcpy();
---
> long	descend(char *np, char *fname);
21,22c19,20
< main(argc, argv)
< char **argv;
---
> int
> main(int argc, char **argv)
24c22
< 	register	i = 1;
---
> 	register int	i = 1;
43c41
< 		if(np = rindex(name, '/')) {
---
> 		if((np = rindex(name, '/'))) {
60,61c58
< descend(np, fname)
< char *np, *fname;
---
> descend(char *np, char *fname)
81c78
< 		static linked = 0;
---
> 		static int linked = 0;
```

### usr/src/cmd/split.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/split.c unix-v7-c99/usr/src/cmd/split.c || true
```

Expect:

```
11,12c11,12
< main(argc, argv)
< char *argv[];
---
> int
> main(int argc, char *argv[])
14c14
< 	register i, c, f;
---
> 	register int i, c, f;
56c56
< 	for(i=0; i<count; i++)
---
> 	for(i=0; (unsigned)i<count; i++)
```

### usr/src/cmd/tsort.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/tsort.c unix-v7-c99/usr/src/cmd/tsort.c || true
```

Expect:

```
8a9
> #define index tindex
29,32c30,38
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
38,39c44,45
< main(argc,argv)
< char **argv;
---
> int
> main(int argc, char **argv)
86,87c92,93
< present(i,j)
< struct nodelist *i, *j;
---
> int
> present(struct nodelist *i, struct nodelist *j)
98,99c104,105
< anypred(i)
< struct nodelist *i;
---
> int
> anypred(struct nodelist *i)
111,112c117
< index(s)
< register char *s;
---
> index(register char *s)
129c134,135
< 	while(*t++ = *s++);
---
> 	while((*t++ = *s++))
> 		;
133,134c139,140
< cmp(s,t)
< register char *s, *t;
---
> int
> cmp(register char *s, register char *t)
145,146c151,152
< error(s,t)
< char *s, *t;
---
> void
> error(char *s, char *t)
152,153c158,159
< note(s,t)
< char *s,*t;
---
> void
> note(char *s, char *t)
162c168
< findloop()
---
> findloop(void)
174c180
< 				error("error 1");
---
> 				error("error 1",empty);
185c191
< 				error("error 2");
---
> 				error("error 2",empty);
```

### usr/src/cmd/file.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/file.c unix-v7-c99/usr/src/cmd/file.c || true
```

Expect:

```
23,24c23,29
< main(argc, argv)
< char **argv;
---
> void type(char *file);
> int lookup(char *tab[]);
> int ccom(void);
> int ascom(void);
> int english(char *bp, int n);
> int
> main(int argc, char **argv)
56,57c61,62
< type(file)
< char *file;
---
> void
> type(char *file)
104a110
> 		/* fallthrough */
184c190
< 		else if(buf[j] == '\n' && isalpha(buf[j+2])){
---
> 		else if(buf[j] == '\n' && isalpha((unsigned char)buf[j+2])){
201c207
< 			else if(buf[j] == '\n' && isalpha(buf[j+2])){
---
> 			else if(buf[j] == '\n' && isalpha((unsigned char)buf[j+2])){
238c244
< 		/*.... */
---
> 		.... */
242,243c248,249
< lookup(tab)
< char *tab[];
---
> int
> lookup(char *tab[])
260c266,267
< ccom(){
---
> int
> ccom(void){
275c282,283
< ascom(){
---
> int
> ascom(void){
284,285c292,293
< english (bp, n)
< char *bp;
---
> int
> english (char *bp, int n)
```

### usr/src/cmd/join.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/join.c unix-v7-c99/usr/src/cmd/join.c || true
```

Expect:

```
25,26c25,30
< main(argc, argv)
< char *argv[];
---
> int input(int n);
> void output(int on1, int on2);
> void error(char *s1, char *s2, char *s3, char *s4, char *s5);
> int cmp(char *s1, char *s2);
> int
> main(int argc, char *argv[])
31c35
< 	long ftell();
---
> 	long ftell(FILE *iop);
88c92
< 		error("usage: join [-j1 x -j2 y] [-o list] file1 file2");
---
> 		error("usage: join [-j1 x -j2 y] [-o list] file1 file2", 0, 0, 0, 0);
96c100
< 		error("can't open %s", argv[1]);
---
> 		error("can't open %s", argv[1], 0, 0, 0);
98c102
< 		error("can't open %s", argv[2]);
---
> 		error("can't open %s", argv[2], 0, 0, 0);
105,106c109,110
< 	while(n1>0 && n2>0 || aflg!=0 && n1+n2>0) {
< 		if(n1>0 && n2>0 && comp()>0 || n1==0) {
---
> 	while((n1>0 && n2>0) || (aflg!=0 && n1+n2>0)) {
> 		if((n1>0 && n2>0 && comp()>0) || n1==0) {
110c114
< 		} else if(n1>0 && n2>0 && comp()<0 || n2==0) {
---
> 		} else if((n1>0 && n2>0 && comp()<0) || n2==0) {
126c130
< 				} else if(n1>0 && n2>0 && comp()<0 || n2==0) {
---
> 				} else if((n1>0 && n2>0 && comp()<0) || n2==0) {
141a146
> int
142a148
> int n;
169a176
> void
188,189c195,196
< 			if(olistf[i]==F1 && on1<=olist[i] ||
< 			   olistf[i]==F2 && on2<=olist[i] ||
---
> 			if((olistf[i]==F1 && on1<=olist[i]) ||
> 			   (olistf[i]==F2 && on2<=olist[i]) ||
201,202c208,209
< error(s1, s2, s3, s4, s5)
< char *s1;
---
> void
> error(char *s1, char *s2, char *s3, char *s4, char *s5)
210,211c217,218
< cmp(s1, s2)
< char *s1, *s2;
---
> int
> cmp(char *s1, char *s2)
```

### usr/src/cmd/pr.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/pr.c unix-v7-c99/usr/src/cmd/pr.c || true
```

Expect:

```
41,42c41,42
< char	*ttyname();
< char	*ctime();
---
> char	*ttyname(int f);
> char	*ctime(long *t);
44,45c44,56
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
47,48d57
< 	int nfdone;
< 	int onintr();
49a59
> 	int nfdone;
52c62
< 		signal(SIGINT, onintr);
---
> 		signal(SIGINT, (int)onintr);
107c117,118
< done()
---
> void
> done(void)
115c126,127
< onintr()
---
> void
> onintr(void)
123c135,136
< fixtty()
---
> void
> fixtty(void)
135,137c148,149
< print(fp, argp)
< char *fp;
< char **argp;
---
> void
> print(char *fp, char **argp)
139d150
< 	extern char *sprintf();
141c152
< 	register sncol;
---
> 	register int sncol;
195c206
< 	while (mflg&&nofile || (!mflg)&&tpgetc(ncol)>0) {
---
> 	while ((mflg&&nofile) || ((!mflg)&&tpgetc(ncol)>0)) {
218,219c229,230
< mopen(ap)
< char **ap;
---
> void
> mopen(char **ap)
238c249,250
< putpage()
---
> void
> putpage(void)
282c294,295
< nexbuf()
---
> void
> nexbuf(void)
305c318,319
< tpgetc(ai)
---
> int
> tpgetc(int ai)
340c354,355
< pgetc(i)
---
> int
> pgetc(int i)
372c387,388
< put(ac)
---
> void
> put(int ac)
418c434,435
< putcp(c)
---
> void
> putcp(int c)
```

### usr/src/cmd/dd.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/dd.c unix-v7-c99/usr/src/cmd/dd.c || true
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
408a419
> 		/* fallthrough */
419c430,431
< cnull(cc)
---
> void
> cnull(int cc)
421c433
< 	register c;
---
> 	register int c;
431c443,444
< null(c)
---
> void
> null(int c)
442c455,456
< ascii(cc)
---
> void
> ascii(int cc)
444c458
< 	register c;
---
> 	register int c;
469c483,484
< ebcdic(cc)
---
> void
> ebcdic(int cc)
471c486
< 	register c;
---
> 	register int c;
498c513,514
< ibm(cc)
---
> void
> ibm(int cc)
500c516
< 	register c;
---
> 	register int c;
527c543,544
< term()
---
> void
> term(void)
534c551,552
< stats()
---
> void
> stats(void)
```

### usr/src/cmd/diff.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/diff.c unix-v7-c99/usr/src/cmd/diff.c || true
```

Expect:

```
76d75
< FILE *fopen();
106c105
< char *mktemp();
---
> char *mktemp(char *as);
107a107,128
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
109c130,131
< done()
---
> void
> done(void)
115c137
< char *talloc(n)
---
> char *talloc(int n)
117c139
< 	extern char *malloc();
---
> 	extern char *malloc(unsigned n);
122a145
> 	return(NULL);
125,126c148
< char *ralloc(p,n)	/*compacting reallocation */
< char *p;
---
> char *ralloc(char *p, int n)	/*compacting reallocation */
129c151
< 	char *realloc();
---
> 	char *realloc(char *p, unsigned n);
139c161,162
< noroom()
---
> void
> noroom(void)
145,146c168,169
< sort(a,n)	/*shellsort CACM #201*/
< struct line *a;
---
> void
> sort(struct line *a, int n)	/*shellsort CACM #201*/
163,164c186,187
< 				   aim->value == ai[0].value &&
< 				   aim->serial > ai[0].serial)
---
> 				   (aim->value == ai[0].value &&
> 				    aim->serial > ai[0].serial))
177,179c200,201
< unsort(f, l, b)
< struct line *f;
< int *b;
---
> void
> unsort(struct line *f, int l, int *b)
191,192c213,214
< filename(pa1, pa2)
< char **pa1, **pa2;
---
> void
> filename(char **pa1, char **pa2)
202c224,225
< 		while(*b1++ = *a1++) ;
---
> 		while((*b1++ = *a1++))
> 			;
205c228
< 		while(*a1++ = *a2++)
---
> 		while((*a1++ = *a2++))
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
235c258
< 	for(j=0; h=readhash(input[i]);) {
---
> 	for(j=0; (h=readhash(input[i]));) {
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
454c477
< 	char c,d;
---
> 	int c,d;
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
617,618c640,641
< 		switch(t=getc(f)) {
< 		case -1:
---
> 		t = getc(f);
> 		if(t == -1)
620,621c643,645
< 		case '\t':
< 		case ' ':
---
> 		if(t == '\n')
> 			break;
> 		if(isspace(t)) {
624,629c648,649
< 		default:
< 			if(space) {
< 				shift += 7;
< 				space = 0;
< 			}
< 			sum += (long)t << (shift%=HALFLONG);
---
> 		}
> 		if(space) {
631,633c651
< 			continue;
< 		case '\n':
< 			break;
---
> 			space = 0;
635c653,654
< 		break;
---
> 		sum += (long)t << (shift%=HALFLONG);
> 		shift += 7;
641,642c660,661
< mesg(s,t)
< char *s, *t;
---
> void
> mesg(char *s, char *t)
```

### usr/src/cmd/write.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/write.c unix-v7-c99/usr/src/cmd/write.c || true
```

Expect:

```
11,12d10
< char	*strcat();
< char	*strcpy();
20,21d17
< char	*ttyname();
< char	*rindex(), *index();
23,24c19,22
< int	eof();
< int	timout();
---
> int	eof(void);
> int	timout(void);
> void	ex(char *bp);
> void	sigs(int sig);
27,28c25,26
< main(argc, argv)
< char *argv[];
---
> int
> main(int argc, char *argv[])
31c29
< 	register i;
---
> 	register int i;
106c104
< 	signal(SIGALRM, timout);
---
> 	signal(SIGALRM, (int)timout);
115c113
< 	sigs(eof);
---
> 	sigs((int)eof);
140c138,139
< timout()
---
> int
> timout(void)
144a144
> 	return(0);
147c147,148
< eof()
---
> int
> eof(void)
151a153
> 	return(0);
154,155c156,157
< ex(bp)
< char *bp;
---
> void
> ex(char *bp)
157c159
< 	register i;
---
> 	register int i;
166c168
< 		sigs((int (*)())0);
---
> 		sigs(0);
174c176
< 	sigs(eof);
---
> 	sigs((int)eof);
177,178c179,180
< sigs(sig)
< int (*sig)();
---
> void
> sigs(int sig)
180c182
< 	register i;
---
> 	register int i;
```

### usr/src/cmd/dcheck.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/dcheck.c unix-v7-c99/usr/src/cmd/dcheck.c || true
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

### usr/src/cmd/icheck.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/icheck.c unix-v7-c99/usr/src/cmd/icheck.c || true
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

### usr/src/cmd/iostat.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/iostat.c unix-v7-c99/usr/src/cmd/iostat.c || true
```

Expect:

```
0a1
> #include <stdio.h>
7,8c8
< struct
< {
---
> struct nlent {
12,15d11
< } nl[] = {
< 	"_dk_busy", 0, 0,
< 	"_io_info", 0, 0,
< 	"\0\0\0\0\0\0\0\0", 0, 0
17,18c13,23
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
39,40c44,52
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
> int
> main(int argc, char *argv[])
42,43c54,55
< 	extern char *ctime();
< 	register  i;
---
> 	extern char *ctime(long *t);
> 	register  int i;
49c61
< 	if(nl[0].type == -1) {
---
> 	if(nl[0].type == 0) {
90c102,122
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
91a124
> 		if (i >= 32) break;
139a173
> 	return(0);
149c183,184
< stats(dn)
---
> int
> stats(int dn)
151c186
< 	register i;
---
> 	register int i;
165c200
< 		return;
---
> 		return(0);
175a211
> 	return(0);
178c214,215
< stat1(o)
---
> int
> stat1(int o)
180c217
< 	register i;
---
> 	register int i;
194a232
> 	return(0);
197,198c235,236
< stats2(t)
< double t;
---
> int
> stats2(double t)
200c238
< 	register i, j;
---
> 	register int i, j;
206a245
> 	return(0);
209,210c248,249
< stats3(t)
< double t;
---
> int
> stats3(double t)
212c251
< 	register i;
---
> 	register int i;
251a291
> 	return(0);
254c294,295
< biostats()
---
> int
> biostats(void)
256c297
< register i;
---
> 	register int i;
257a299,300
> 	if (nl[1].type == 0)
> 		return(0);
270a314
> 	return(0);
```

### usr/src/cmd/ncheck.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/ncheck.c unix-v7-c99/usr/src/cmd/ncheck.c || true
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

### usr/src/cmd/find.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/find.c unix-v7-c99/usr/src/cmd/find.c || true
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
41,43c39,53
< char *rindex();
< char *sbrk();
< main(argc, argv) char *argv[];
---
> char *rindex(char *sp, int c);
> char *sbrk(int);
> int	pr(char *s);
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
48a59
> 	int pclose(FILE *);
77c88
< 		if(cp = rindex(Pathname, '/')) {
---
> 		if((cp = rindex(Pathname, '/'))) {
99,100c110,111
< struct anode *exp() { /* parse ALTERNATION (-o)  */
< 	int or();
---
> struct anode *exp(void) { /* parse ALTERNATION (-o)  */
> 	int or(register struct anode *p);
111,112c122,123
< struct anode *e1() { /* parse CONCATENATION (formerly -a) */
< 	int and();
---
> struct anode *e1(void) { /* parse CONCATENATION (formerly -a) */
> 	int and(register struct anode *p);
128,129c139,140
< struct anode *e2() { /* parse NOT (!) */
< 	int not();
---
> struct anode *e2(void) { /* parse NOT (!) */
> 	int not(register struct anode *p);
141,144c152,157
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
166c179
< 		return(mk(mtime, (struct anode *)atoi(b), (struct anode *)s));
---
> 		return(mk(mtime, (struct anode *)(long)atoi(b), (struct anode *)(long)s));
168c181
< 		return(mk(atime, (struct anode *)atoi(b), (struct anode *)s));
---
> 		return(mk(atime, (struct anode *)(long)atoi(b), (struct anode *)(long)s));
170c183
< 		return(mk(ctime, (struct anode *)atoi(b), (struct anode *)s));
---
> 		return(mk(ctime, (struct anode *)(long)atoi(b), (struct anode *)(long)s));
176c189
< 				return mk(user, (struct anode *)atoi(b), (struct anode *)s);
---
> 				return mk(user, (struct anode *)(long)atoi(b), (struct anode *)(long)s);
180c193
< 		return(mk(user, (struct anode *)i, (struct anode *)s));
---
> 		return(mk(user, (struct anode *)(long)i, (struct anode *)(long)s));
183c196
< 		return(mk(ino, (struct anode *)atoi(b), (struct anode *)s));
---
> 		return(mk(ino, (struct anode *)(long)atoi(b), (struct anode *)(long)s));
189c202
< 				return mk(group, (struct anode *)atoi(b), (struct anode *)s);
---
> 				return mk(group, (struct anode *)(long)atoi(b), (struct anode *)(long)s);
193c206
< 		return(mk(group, (struct anode *)i, (struct anode *)s));
---
> 		return(mk(group, (struct anode *)(long)i, (struct anode *)(long)s));
195c208
< 		return(mk(size, (struct anode *)atoi(b), (struct anode *)s));
---
> 		return(mk(size, (struct anode *)(long)atoi(b), (struct anode *)(long)s));
197c210
< 		return(mk(links, (struct anode *)atoi(b), (struct anode *)s));
---
> 		return(mk(links, (struct anode *)(long)atoi(b), (struct anode *)(long)s));
204c217
< 		return(mk(perm, (struct anode *)i, (struct anode *)s));
---
> 		return(mk(perm, (struct anode *)(long)i, (struct anode *)(long)s));
226c239
< 			pr("find: cannot create "), pr(s), pr("\n");
---
> 			pr("find: cannot create "), pr(b), pr("\n");
242a256
> 	return(0);
244,246c258
< struct anode *mk(f, l, r)
< int (*f)();
< struct anode *l, *r;
---
> struct anode *mk(int (*f)(), struct anode *l, struct anode *r)
254,255c266,267
< char *nxtarg() { /* get next arg from command line */
< 	static strikes = 0;
---
> char *nxtarg(void) { /* get next arg from command line */
> 	static int strikes = 0;
270,271c282,283
< and(p)
< register struct anode *p;
---
> int
> and(register struct anode *p)
275,276c287,288
< or(p)
< register struct anode *p;
---
> int
> or(register struct anode *p)
280,281c292,293
< not(p)
< register struct anode *p;
---
> int
> not(register struct anode *p)
285,286c297,298
< glob(p)
< register struct { int f; char *pat; } *p; 
---
> int
> glob(void *vp)
287a300
> 	struct { int f; char *pat; } *p = vp;
290c303,304
< print()
---
> int
> print(void)
295,296c309,310
< mtime(p)
< register struct { int f, t, s; } *p; 
---
> int
> mtime(void *vp)
297a312
> 	struct { int f, t, s; } *p = vp;
300,301c315,316
< atime(p)
< register struct { int f, t, s; } *p; 
---
> int
> atime(void *vp)
302a318
> 	struct { int f, t, s; } *p = vp;
305,306c321,322
< ctime(p)
< register struct { int f, t, s; } *p; 
---
> int
> ctime(void *vp)
307a324
> 	struct { int f, t, s; } *p = vp;
310,311c327,328
< user(p)
< register struct { int f, u, s; } *p; 
---
> int
> user(void *vp)
312a330
> 	struct { int f, u, s; } *p = vp;
315,316c333,334
< ino(p)
< register struct { int f, u, s; } *p;
---
> int
> ino(void *vp)
317a336
> 	struct { int f, u, s; } *p = vp;
320,321c339,340
< group(p)
< register struct { int f, u; } *p; 
---
> int
> group(void *vp)
322a342
> 	struct { int f, u; } *p = vp;
325,326c345,346
< links(p)
< register struct { int f, link, s; } *p; 
---
> int
> links(void *vp)
327a348
> 	struct { int f, link, s; } *p = vp;
330,331c351,352
< size(p)
< register struct { int f, sz, s; } *p; 
---
> int
> size(void *vp)
332a354
> 	struct { int f, sz, s; } *p = vp;
335,336c357,358
< perm(p)
< register struct { int f, per, s; } *p; 
---
> int
> perm(void *vp)
338c360,361
< 	register i;
---
> 	struct { int f, per, s; } *p = vp;
> 	register int i;
342,343c365,366
< type(p)
< register struct { int f, per, s; } *p;
---
> int
> type(void *vp)
344a368
> 	struct { int f, per, s; } *p = vp;
347,348c371,372
< exeq(p)
< register struct { int f, com; } *p;
---
> int
> exeq(void *vp)
349a374
> 	struct { int f, com; } *p = vp;
353,354c378,379
< ok(p)
< struct { int f, com; } *p;
---
> int
> ok(void *vp)
355a381
> 	struct { int f, com; } *p = vp;
373,374c399
< long mklong(v)
< short v[];
---
> long mklong(short v[])
383c408,409
< cpio()
---
> int
> cpio(void)
400c426
< 	register ifile, ct;
---
> 	register int ifile, ct;
402c428
< 	register i;
---
> 	register int i;
421c447
< 		return;
---
> 		return(0);
425c451
< 		return;
---
> 		return(0);
430c456
< 		return;
---
> 		return(0);
440c466
< 	return;
---
> 	return(0);
442c468,469
< newer()
---
> int
> newer(void)
448,450c475,476
< scomp(a, b, s) /* funny signed compare */
< register a, b;
< register char s;
---
> int
> scomp(register int a, register int b, register int s) /* funny signed compare */
459c485,486
< doex(com)
---
> int
> doex(int com)
461c488
< 	register np;
---
> 	register int np;
464c491
< 	static ccode;
---
> 	static int ccode;
467c494
< 	while (na=Argv[com++]) {
---
> 	while ((na=Argv[com++])) {
477c504
< 		execvp(nargv[0], nargv, np);
---
> 		execvp(nargv[0], nargv);
483,484c510,512
< getunum(f, s) char *f, *s; { /* find user/group name and return number */
< 	register i;
---
> int
> getunum(char *f, char *s) { /* find user/group name and return number */
> 	register int i;
486c514
< 	register c;
---
> 	register int c;
491a520,521
> 	if(pin == NULL)
> 		return(i);
515,517c545,546
< descend(name, fname, exlist)
< struct anode *exlist;
< char *name, *fname;
---
> int
> descend(char *name, char *fname, struct anode *exlist)
612,613c641,642
< gmatch(s, p) /* string match as in glob */
< register char *s, *p;
---
> int
> gmatch(register char *s, register char *p) /* string match as in glob */
619,620c648,649
< amatch(s, p)
< register char *s, *p;
---
> int
> amatch(register char *s, register char *p)
622c651
< 	register cc;
---
> 	register int cc;
632c661
< 		while (cc = *++p) {
---
> 		while ((cc = *++p)) {
642c671
< 				k |= lc <= scc & scc <= (cc=p[1]);
---
> 				k |= (lc <= scc) & (scc <= (cc=p[1]));
661,662c690,691
< umatch(s, p)
< register char *s, *p;
---
> int
> umatch(register char *s, register char *p)
670,672c699,700
< bwrite(rp, c)
< register short *rp;
< register c;
---
> int
> bwrite(register short *rp, register int c)
691a720
> 	return(0);
693c722,723
< chgreel(x, fl)
---
> int
> chgreel(int x, int fl)
695c725
< 	register f;
---
> 	register int f;
719,720c749,750
< pr(s)
< char *s;
---
> int
> pr(char *s)
722a753
> 	return(0);
```

### usr/src/cmd/sort.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sort.c unix-v7-c99/usr/src/cmd/sort.c || true
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
166,168c167,186
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
> int	digit(int c);
> int	blank(int c);
> int	number(char **ppa);
> int	qsort(char **a, char **l);
170,171c188,189
< main(argc, argv)
< char **argv;
---
> int
> main(int argc, char **argv)
173c191
< 	register a;
---
> 	register int a;
239a258
> 	ep = (char *)lspace + MEM;
245c264
< 	nlines /= (5*(sizeof(char *)/sizeof(char)));
---
> 	nlines /= (5*(sizeof(char *)));
262c281
< 	signal(SIGHUP, term);
---
> 	signal(SIGHUP, (int)term);
264,266c283,285
< 		signal(SIGINT, term);
< 	signal(SIGPIPE,term);
< 	signal(SIGTERM,term);
---
> 		signal(SIGINT, (int)term);
> 	signal(SIGPIPE,(int)term);
> 	signal(SIGTERM,(int)term);
272c291
< 	for(a = mflg|cflg?0:eargc; a+N<nfiles || unsafeout&&a<eargc; a=i) {
---
> 	for(a = (mflg|cflg)?0:eargc; a+N<nfiles || (unsafeout&&a<eargc); a=i) {
284a304
> 	return(0);
287c307,308
< sort()
---
> int
> sort(void)
291c312
< 	register c;
---
> 	register int c;
341a363
> 	return(0);
350c372,373
< merge(a,b)
---
> int
> merge(int a, int b)
354c377
< 	register	i;
---
> 	register int	i;
392c415
< 	muflg = mflg & uflg | cflg;
---
> 	muflg = (mflg & uflg) | cflg;
433,434c456,457
< 	}
< 	p = (struct merg *)lspace;
---
> 		}
> 		p = (struct merg *)lspace;
441a465
> 	return(0);
444,445c468,469
< rline(mp)
< struct merg *mp;
---
> int
> rline(struct merg *mp)
450c474
< 	register c;
---
> 	register int c;
466,467c490,491
< disorder(s,t)
< char *s, *t;
---
> int
> disorder(char *s, char *t)
473a498
> 	return(0);
476c501,502
< newfile()
---
> int
> newfile(void)
485a512
> 	return(0);
489c516
< setfil(i)
---
> setfil(int i)
492c519
< 	if(i < eargc)
---
> 	if(i < eargc) {
496a524
> 	}
503c531,532
< oldfile()
---
> int
> oldfile(void)
512a542
> 	return(0);
515c545,546
< safeoutfil()
---
> int
> safeoutfil(void)
521c552
< 		return;
---
> 		return(0);
523c554
< 		return;
---
> 		return(0);
530a562
> 	return(0);
533,534c565,566
< cant(f)
< char *f;
---
> int
> cant(char *f)
538a571
> 	return(0);
541,542c574,575
< diag(s,t)
< char *s, *t;
---
> int
> diag(char *s, char *t)
547a581
> 	return(0);
550c584,585
< term()
---
> int
> term(void)
552c587
< 	register i;
---
> 	register int i;
562a598
> 	return(0);
565,566c601,602
< cmp(i, j)
< char *i, *j;
---
> int
> cmp(char *i, char *j)
569c605
< 	char *skip();
---
> 	char *skip(char *pp, struct field *fp, int j);
606,607c642,643
< 			for(ipa = pa; ipa<la&&isdigit(*ipa); ipa++) ;
< 			for(ipb = pb; ipb<lb&&isdigit(*ipb); ipb++) ;
---
> 			for(ipa = pa; ipa<la&&digit(*ipa); ipa++) ;
> 			for(ipb = pb; ipb<lb&&digit(*ipb); ipb++) ;
613c649
< 					if(b = *--ipb - *--ipa)
---
> 					if((b = *--ipb - *--ipa))
627,629c663,665
< 				while(pa<la && isdigit(*pa)
< 				   && pb<lb && isdigit(*pb))
< 					if(a = *pb++ - *pa++)
---
> 				while(pa<la && digit(*pa)
> 				   && pb<lb && digit(*pb))
> 					if((a = *pb++ - *pa++))
631c667
< 			while(pa<la && isdigit(*pa))
---
> 			while(pa<la && digit(*pa))
634c670
< 			while(pb<lb && isdigit(*pb))
---
> 			while(pb<lb && digit(*pb))
642c678
< 		while(ignore[*pa])
---
> 		while(ignore[(unsigned char)*pa])
644c680
< 		while(ignore[*pb])
---
> 		while(ignore[(unsigned char)*pb])
646c682
< 		if(pa>=la || *pa=='\n')
---
> 		if(pa>=la || *pa=='\n') {
649a686
> 		}
652c689
< 		if((sa = code[*pb++]-code[*pa++]) == 0)
---
> 		if((sa = code[(unsigned char)*pb++]-code[(unsigned char)*pa++]) == 0)
661,662c698,699
< cmpa(pa, pb)
< register char *pa, *pb;
---
> int
> cmpa(register char *pa, register char *pb)
678,680c715
< skip(pp, fp, j)
< struct field *fp;
< char *pp;
---
> skip(char *pp, struct field *fp, int j)
682c717
< 	register i;
---
> 	register int i;
718,719c753
< eol(p)
< register char *p;
---
> eol(register char *p)
725c759,760
< copyproto()
---
> int
> copyproto(void)
727c762
< 	register i;
---
> 	register int i;
732c767
< 	for(i=0; i<sizeof(proto)/sizeof(*p); i++)
---
> 	for(i=0; i<(int)(sizeof(proto)/sizeof(*p)); i++)
733a769
> 	return(0);
736,737c772,773
< field(s,k)
< char *s;
---
> int
> field(char *s, int k)
740c776
< 	register d;
---
> 	register int d;
746c782
< 			return;
---
> 			return(0);
790a827
> 			/* fallthrough */
795a833
> 	return(0);
798,799c836,837
< number(ppa)
< char **ppa;
---
> int
> number(char **ppa)
805c843
< 	while(isdigit(*pa)) {
---
> 	while(digit(*pa)) {
812c850,858
< blank(c)
---
> int
> digit(int c)
> {
> 	if(c >= '0' && c <= '9')
> 		return(1);
> 	return(0);
> }
> int
> blank(int c)
822,823c868,869
< qsort(a,l)
< char **a, **l;
---
> int
> qsort(char **a, char **l)
836c882
< 		return;
---
> 		return(0);
896,900c942,945
< 		--lp;
< 		qstexc(j, lp, i);
< 		j = --hp;
< 	}
< }
---
> 			--lp;
> 			qstexc(j, lp, i);
> 			j = --hp;
> 		}
901a947
> 	}
```

### usr/src/libc/crypt.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/crypt.c unix-v7-c99/usr/src/libc/crypt.c || true
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
> static	char	S[] = {
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
282c282
< 			k = S[j][(preS[t+0]<<5)+
---
> 			k = S[j*64 + (preS[t+0]<<5)+
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

### usr/include/sys/param.h

Local test:

```
diff unix-v7-c99/v7/usr/include/sys/param.h unix-v7-c99/usr/include/sys/param.h || true
```

Expect:

```
84a85
> #ifndef NULL
85a87
> #endif
120c122
< #define	major(x)	(int)(((unsigned)x>>8))
---
> #define	major(x)	(int)(((unsigned)x>>8)&0377)
128a131
> #ifndef SYS_TYPES_H
131c134
< typedef	unsigned int	ino_t;
---
> typedef	unsigned short	ino_t;
133c136
< typedef	int		label_t[6];	/* regs 2-7 */
---
> typedef	int		label_t[10];	/* regs 2-7 */
135a139,140
> #define	SYS_TYPES_H
> #endif
```

### usr/include/sys/inode.h

Local test:

```
diff unix-v7-c99/v7/usr/include/sys/inode.h unix-v7-c99/usr/include/sys/inode.h || true
```

Expect:

```
15c15
< struct group {
---
> struct mpx_group {
19c19
< 	struct	group	*g_group;
---
> 	struct	mpx_group	*g_group;
41c41
< 		};
---
> 		} u_reg;
44,45c44,45
< 			struct	group	i_group;	/*  multiplexor group file */
< 		};
---
> 			struct	mpx_group	i_group;	/*  multiplexor group file */
> 		} u_dev;
47a48,51
> #define	i_addr	u_reg.i_addr
> #define	i_lastr	u_reg.i_lastr
> #define	i_rdev	u_dev.i_rdev
> #define	i_group	u_dev.i_group
```

### usr/sys/h/systm.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/systm.h unix-v7-c99/usr/sys/h/systm.h || true
```

Expect:

```
41a42
> extern	char	*msgbufp;	/* next saved printf character */
48,63c49,90
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
> struct file *falloc(void);
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
80c107
< 	int	(*sy_call)();		/* handler */
---
> 	void	(*sy_call)(void);	/* handler (Armv7/C99: void(void)) */
```

### usr/sys/sys/iget.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/iget.c unix-v7-c99/usr/sys/sys/iget.c || true
```

Expect:

```
10a11,22
> void sleep(caddr_t chan, int pri);
> void panic(char *s);
> void printf(char *fmt, ...);
> void brelse(struct buf *bp);
> void bdwrite(struct buf *bp);
> void iexpand(register struct inode *ip, register struct dinode *dp);
> void itrunc(register struct inode *ip);
> void tloop(dev_t dev, daddr_t bn, int f1, int f2);
> void wdir(struct inode *ip);
> void iput(register struct inode *ip);
> int iupdat(register struct inode *ip, time_t *ta, time_t *tm);
> extern dev_t rootdev;
30,32c42
< iget(dev, ino)
< dev_t dev;
< ino_t ino;
---
> iget(dev_t dev, ino_t ino)
92,94c102,103
< iexpand(ip, dp)
< register struct inode *ip;
< register struct dinode *dp;
---
> void
> iexpand(register struct inode *ip, register struct dinode *dp)
109d117
< 		*p1++ = 0;
111a120
> 		*p1++ = 0;
122,123c131,132
< iput(ip)
< register struct inode *ip;
---
> void
> iput(register struct inode *ip)
149,151c158,159
< iupdat(ip, ta, tm)
< register struct inode *ip;
< time_t *ta, *tm;
---
> int
> iupdat(register struct inode *ip, time_t *ta, time_t *tm)
161c169
< 			return;
---
> 			return(0);
165c173
< 			return;
---
> 			return(0);
177a186,187
> 			*p1++ = *p2++;
> 			*p1++ = *p2++;
181,182d190
< 			*p1++ = *p2++;
< 			*p1++ = *p2++;
192a201
> 	return(0);
204,205c213,214
< itrunc(ip)
< register struct inode *ip;
---
> void
> itrunc(register struct inode *ip)
207c216
< 	register i;
---
> 	register int i;
242,244c251,252
< tloop(dev, bn, f1, f2)
< dev_t dev;
< daddr_t bn;
---
> void
> tloop(dev_t dev, daddr_t bn, int f1, int f2)
246c254
< 	register i;
---
> 	register int i;
251a260
> 	bap = NULL;
280c289
< maknode(mode)
---
> maknode(int mode)
305,306c314,315
< wdir(ip)
< struct inode *ip;
---
> void
> wdir(struct inode *ip)
```

### usr/sys/sys/nami.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/nami.c unix-v7-c99/usr/sys/sys/nami.c || true
```

Expect:

```
7a8
> void brelse(struct buf *bp);
21,22c22
< namei(func, flag)
< int (*func)();
---
> namei(int (*func)(void), int flag)
25c25
< 	register c;
---
> 	register int c;
206c206,207
< schar()
---
> int
> schar(void)
216c217,218
< uchar()
---
> int
> uchar(void)
218c220
< 	register c;
---
> 	register int c;
```

### usr/src/cmd/login.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/login.c unix-v7-c99/usr/src/cmd/login.c || true
```

Expect:

```
15c15
< struct	passwd nouser = {"", "nope"};
---
> struct	passwd nouser = {"", "nope", 0, 0, 0, 0, 0, 0, 0};
23,29d22
< struct	passwd *getpwnam();
< char	*strcat();
< int	setpwent();
< char	*ttyname();
< char	*crypt();
< char	*getpass();
< char	*rindex(), *index();
30a24
> void	showmotd(void);
32,33c26,27
< main(argc, argv)
< char **argv;
---
> int
> main(int argc, char **argv)
131c125,126
< catch()
---
> void
> catch(int sig)
132a128
> 	(void)sig;
137c133,134
< showmotd()
---
> void
> showmotd(void)
140c137
< 	register c;
---
> 	register int c;
142c139
< 	signal(SIGINT, catch);
---
> 	signal(SIGINT, (int)catch);
```

### usr/src/cmd/ls.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/ls.c unix-v7-c99/usr/src/cmd/ls.c || true
```

Expect:

```
42,45c42,51
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
49,50c55,56
< main(argc, argv)
< char *argv[];
---
> int
> main(int argc, char *argv[])
58c64
< 	int compar();
---
> 	int compar(struct lbuf **pp1, struct lbuf **pp2);
146c152
< 		if (ep->ltype=='d' && dflg==0 || fflg) {
---
> 		if ((ep->ltype=='d' && dflg==0) || fflg) {
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
204,206c209,210
< getname(uid, buf)
< int uid;
< char buf[];
---
> int
> getname(int uid, char buf[])
239,240c243
< nblock(size)
< long size;
---
> nblock(long size)
257c260,261
< pmode(aflag)
---
> void
> pmode(int aflag)
266,267c270,271
< select(pairp)
< register int *pairp;
---
> void
> select(register int *pairp)
278,279c282
< makename(dir, file)
< char *dir, *file;
---
> makename(char *dir, char *file)
297,298c300,301
< readdir(dir)
< char *dir;
---
> void
> readdir(char *dir)
313,314c316,317
< 		 || aflg==0 && dentry.d_name[0]=='.' &&  (dentry.d_name[1]=='\0'
< 			|| dentry.d_name[1]=='.' && dentry.d_name[2]=='\0'))
---
> 		 || (aflg==0 && dentry.d_name[0]=='.' && (dentry.d_name[1]=='\0'
> 			|| (dentry.d_name[1]=='.' && dentry.d_name[2]=='\0'))))
328,329c331
< gstat(file, argfl)
< char *file;
---
> gstat(char *file, int argfl)
331d332
< 	extern char *malloc();
400,401c401,402
< compar(pp1, pp2)
< struct lbuf **pp1, **pp2;
---
> int
> compar(struct lbuf **pp1, struct lbuf **pp2)
```

### usr/src/cmd/sh/args.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/args.c unix-v7-c99/usr/src/cmd/sh/args.c || true
```

Expect:

```
12c12
< PROC STRING *copyargs();
---
> LOCAL DOLPTR	copyargs(STRING from[], INT n);
14a15,19
> INT	failed(STRING s1, STRING s2);
> DOLPTR	freeargs(DOLPTR blk);
> INT	assnum(STRING *p, INT n);
> INT	pop(void);
> extern void free(void *p);
27,29c32
< INT	options(argc,argv)
< 	STRING		*argv;
< 	INT		argc;
---
> INT	options(INT argc, STRING *argv)
68,69c71
< VOID	setargs(argi)
< 	STRING		argi[];
---
> VOID	setargs(STRING argi[])
80a83
> 	return(0);
83,84c86
< freeargs(blk)
< 	DOLPTR		blk;
---
> DOLPTR freeargs(DOLPTR blk)
90c92
< 	IF argblk=blk
---
> 	IF (argblk=blk)
93c95
< 		THEN	FOR argp=argblk->dolarg; Rcheat(*argp)!=ENDARGS; argp++
---
> 		THEN	FOR argp=(STRING *)argblk->dolarg; Rcheat(*argp)!=ENDARGS; argp++
101,102c103
< LOCAL STRING *	copyargs(from, n)
< 	STRING		from[];
---
> LOCAL DOLPTR	copyargs(STRING from[], INT n)
104c105
< 	REG STRING *	np=alloc(sizeof(STRING*)*n+3*BYTESPERWORD);
---
> 	REG DOLPTR	np=(DOLPTR)alloc(sizeof(STRING*)*n+3*BYTESPERWORD);
106c107
< 	REG STRING *	pp=np;
---
> 	REG STRING *	pp;
109,110c110,111
< 	np=np->dolarg;
< 	dolv=np;
---
> 	pp=(STRING *)np->dolarg;
> 	dolv=pp;
113,115c114,116
< 	DO *np++ = make(*fp++) OD
< 	*np++ = ENDARGS;
< 	return(pp);
---
> 	DO *pp++ = make(*fp++) OD
> 	*pp++ = ENDARGS;
> 	return(np);
118c119
< clearup()
---
> INT clearup(void)
121c122
< 	WHILE argfor=freeargs(argfor) DONE
---
> 	WHILE (argfor=freeargs(argfor)) DONE
124a126
> 	return(0);
127c129
< DOLPTR	useargs()
---
> DOLPTR	useargs(void)
```

### usr/src/cmd/sh/ctype.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/ctype.c unix-v7-c99/usr/src/cmd/sh/ctype.c || true
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

### usr/src/cmd/sh/defs.h

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/defs.h unix-v7-c99/usr/src/cmd/sh/defs.h || true
```

Expect:

```
81,108c81,104
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
139,147c135,143
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
150c146
< SYSTAB		reserved;
---
> extern SYSTAB	reserved;
158,160c154,156
< MSG		stdprompt;
< MSG		supprompt;
< MSG		profile;
---
> extern MSG	stdprompt;
> extern MSG	supprompt;
> extern MSG	profile;
172c168
< MSG		flagadr;
---
> extern MSG	flagadr;
179c175
< MSG		defpath;
---
> extern MSG	defpath;
182,188c178,184
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
191c187
< CHAR		tmpout[];
---
> extern CHAR	tmpout[];
200c196
< MSG		devnull;
---
> extern MSG	devnull;
240c236
< VOID		fault();
---
> VOID		fault(INT sig);
242,243c238,239
< STRING		trapcom[];
< BOOL		trapflg[];
---
> extern STRING	trapcom[];
> extern BOOL	trapflg[];
247,249c243,245
< CHAR		numbuf[];
< MSG		export;
< MSG		readonly;
---
> extern CHAR	numbuf[];
> extern MSG	export;
> extern MSG	readonly;
258,282c254,278
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
284c280
< address	end[];
---
> extern address	end[];
```

### usr/src/cmd/sh/expand.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/expand.c unix-v7-c99/usr/src/cmd/sh/expand.c || true
```

Expect:

```
27c27,33
< PROC VOID	addg();
---
> LOCAL VOID	addg(STRING as1, STRING as2, STRING as3);
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

### usr/src/cmd/sh/mode.h

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/mode.h unix-v7-c99/usr/src/cmd/sh/mode.h || true
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
75,76d72
< /* for functions that do not return values */
< struct void {INT vvvvvvvv;};
113a110
> STRUCT sysnod	SYSTAB[];
```

### usr/src/cmd/sh/msg.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/msg.c unix-v7-c99/usr/src/cmd/sh/msg.c || true
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

### usr/src/cmd/sh/service.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/service.c unix-v7-c99/usr/src/cmd/sh/service.c || true
```

Expect:

```
13c13,50
< PROC VOID	gsort();
---
> LOCAL VOID	gsort(STRING from[], STRING to[]);
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
68,69c105,130
< STRING	getpath(s)
< 	STRING		s;
---
> VOID	nullio(IOPTR iop)
> {
> 	REG STRING	ion;
> 	REG INT		iof, fd;
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
> STRING	getpath(STRING s)
80a142
> 	return(0);
83,84c145
< INT	pathopen(path, name)
< 	REG STRING	path, name;
---
> INT	pathopen(REG STRING path, REG STRING name)
93,95c154
< STRING	catpath(path,name)
< 	REG STRING	path;
< 	STRING		name;
---
> STRING	catpath(REG STRING path, STRING name)
112,113c171
< VOID	execa(at)
< 	STRING		at[];
---
> VOID	execa(STRING at[])
122c180
< 		WHILE path=execs(path,t) DONE
---
> 		WHILE (path=execs(path,t)) DONE
124a183
> 	return(0);
127,129c186
< LOCAL STRING	execs(ap,t)
< 	STRING		ap;
< 	REG STRING	t[];
---
> LOCAL STRING	execs(STRING ap, REG STRING t[])
150c207,209
< 		longjmp(subshell,1);
---
> 		execexp(0,input);
> 		done();
> 		/* fallthrough */
153a213
> 		/* fallthrough */
156a217
> 		/* fallthrough */
159a221
> 		/* fallthrough */
162a225
> 		/* fallthrough */
165a229
> 	return(prefix);
173c237
< postclr()
---
> INT postclr(void)
179a244
> 	return(0);
182,183c247
< VOID	post(pcsid)
< 	INT		pcsid;
---
> VOID	post(INT pcsid)
194a259
> 	return(0);
197,198c262
< VOID	await(i)
< 	INT		i;
---
> VOID	await(INT i)
225c289
< 		IF sig = w&0177
---
> 		IF (sig = w&0177)
247a312
> 	return(0);
252,253c317
< trim(at)
< 	STRING		at;
---
> INT trim(STRING at)
259,260c323,324
< 	IF p=at
< 	THEN	WHILE c = *p
---
> 	IF (p=at)
> 	THEN	WHILE (c = *p)
263a328
> 	return(0);
266,267c331
< STRING	mactrim(s)
< 	STRING		s;
---
> STRING	mactrim(STRING s)
274,275c338
< STRING	*scan(argn)
< 	INT		argn;
---
> STRING	*scan(INT argn)
277c340
< 	REG ARGPTR	argp = Rcheat(gchain)&~ARGMK;
---
> 	REG ARGPTR	argp = (ARGPTR)(long)(Rcheat(gchain)&~ARGMK);
280c343
< 	comargn=getstak(BYTESPERWORD*argn+BYTESPERWORD); comargm = comargn += argn; *comargn = ENDARGS;
---
> 	comargn=(STRING *)getstak(BYTESPERWORD*argn+BYTESPERWORD); comargm = comargn += argn; *comargn = ENDARGS;
284c347
< 		IF argp = argp->argnxt
---
> 		IF (argp = argp->argnxt)
292c355
< 		argp = Rcheat(argp)&~ARGMK;
---
> 		argp = (ARGPTR)(long)(Rcheat(argp)&~ARGMK);
297,298c360
< LOCAL VOID	gsort(from,to)
< 	STRING		from[], to[];
---
> LOCAL VOID	gsort(STRING from[], STRING to[])
303c365
< 	IF (n=to-from)<=1 THEN return FI
---
> 	IF (n=to-from)<=1 THEN return(0) FI
318a381
> 	return(0);
323,324c386
< INT	getarg(ac)
< 	COMPTR		ac;
---
> INT	getarg(COMPTR ac)
330c392
< 	IF c=ac
---
> 	IF (c=ac)
340,341c402
< LOCAL INT	split(s)
< 	REG STRING	s;
---
> LOCAL INT	split(REG STRING s)
343a405
> 	REG ARGPTR	arg;
358c420,421
< 		IF c=expand((argp=endstak(argp))->argval,0)
---
> 		arg=(ARGPTR)endstak(argp);
> 		IF (c=expand(arg->argval,0))
361c424
< 			makearg(argp); count++;
---
> 			makearg(arg); count++;
```

### usr/src/cmd/sh/word.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/word.c unix-v7-c99/usr/src/cmd/sh/word.c || true
```

Expect:

```
12a13,25
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
17c30
< word()
---
> INT word(void)
20a34
> 	REG ARGPTR	arg;
42,43c56,57
< 		argp=endstak(argp);
< 		IF !letter(argp->argval[0]) THEN wdset=0 FI
---
> 		arg=(ARGPTR)endstak(argp);
> 		IF !letter(arg->argval[0]) THEN wdset=0 FI
46c60
< 		IF argp->argval[1]==0 ANDF (d=argp->argval[0], digit(d)) ANDF (c=='>' ORF c=='<')
---
> 		IF arg->argval[1]==0 ANDF (d=arg->argval[0], digit(d)) ANDF (c=='>' ORF c=='<')
49,50c63,64
< 			IF reserv==FALSE ORF (wdval=syslook(argp->argval,reserved))==0
< 			THEN	wdarg=argp; wdval=0;
---
> 			IF reserv==FALSE ORF (wdval=syslook(arg->argval,reserved))==0
> 			THEN	wdarg=arg; wdval=0;
70,71c84,85
< nextc(quote)
< 	CHAR		quote;
---
> int
> nextc(int quote)
85c99
< readc()
---
> INT readc(void)
116c130
< LOCAL	readb()
---
> LOCAL	INT readb(void)
```

### usr/src/cmd/sh/xec.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/xec.c unix-v7-c99/usr/src/cmd/sh/xec.c || true
```

Expect:

```
12a13,65
> void	execexp(STRING s, UFD f);
> INT	sigchk(void);
> INT	getarg(COMPTR ac);
> INT	syslook(STRING w, struct sysnod syswds[]);
> INT	setlist(REG ARGPTR arg, INT xp);
> VOID	prn(INT n);
> INT	blank(void);
> INT	newline(void);
> INT	prt(L_INT t);
> INT	pathopen(REG STRING path, REG STRING name);
> INT	failed(STRING s1, STRING s2);
> INT	exitsh(INT xno);
> INT	stoi(STRING icp);
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
> INT	replace(REG STRING *a, STRING v);
> DOLPTR	freeargs(DOLPTR blk);
> INT	gmatch(REG STRING s, REG STRING p);
> INT	cf(STRING s1, STRING s2);
> INT	exitset(void);
> INT	namscan(VOID (*fn)(NAMPTR));
> INT	push(FILE af);
> INT	pop(void);
> INT	initf(UFD fd);
> INT	estabf(REG STRING s);
> INT	trim(STRING at);
> INT	tdystak(REG STKPTR x);
> INT	builtin(void);
> extern int chdir(char *p);
> extern int signal();
> extern int times(long *t);
> extern int umask(int m);
> extern int fork(void);
> extern int alarm(unsigned sec);
> extern int pause(void);
> extern int close(int fd);
> extern int dup();
15c68
< SYSTAB		commands;
---
> extern SYSTAB	commands;
22,24c75
< execute(argt, execflg, pf1, pf2)
< 	TREPTR		argt;
< 	INT		*pf1, *pf2;
---
> INT execute(TREPTR argt, INT execflg, INT *pf1, INT *pf2)
43a95
> 			COMPTR		c=(COMPTR)t;
47c99
< 			IOPTR		io=t->treio;
---
> 			IOPTR		io=c->comio;
49c101
< 			argn = getarg(t);
---
> 			argn = getarg(c);
53,54c105,106
< 			IF (internal=syslook(com[0],commands)) ORF argn==0
< 			THEN	setlist(t->comset, 0);
---
> 			IF ((internal=syslook(com[0],commands)) ORF argn==0)
> 			THEN	setlist(c->comset, 0);
88c140
< 	
---
> 					/* fallthrough */
136c188
< 	
---
> 					/* fallthrough */
140c192
< 	
---
> 					/* fallthrough */
178c230
< 					ELIF t->comset==0
---
> 					ELIF c->comset==0
185a238
> 					/* fallthrough */
199c252
< 					THEN	execexp(a1,&com[2]);
---
> 					THEN	execexp(a1,(UFD)(long)&com[2]);
205c258
<                                                 int c, i
---
> 						int c, i;
222c275
< 					internal=builtin(argn,com);
---
> 					internal=builtin(); (void)argn;
231c284
< 			ELIF t->treio==0
---
> 			ELIF c->comio==0
235c288
< 	
---
> 			/* fallthrough */
292c345
< 				THEN	execute(t->forktre,1);
---
> 				THEN	execute(((FORKPTR)t)->forktre,1,(INT *)0,(INT *)0);
294c347
< 				THEN	setlist(t->comset,N_EXPORT);
---
> 				THEN	setlist(((COMPTR)t)->comset,N_EXPORT);
298a352
> 			break;
302c356
< 			execute(t->partre,execflg);
---
> 			execute(((PARPTR)t)->partre,execflg,(INT *)0,(INT *)0);
303a358
> 			/* fallthrough */
306a362
> 			   REG LSTPTR	l=(LSTPTR)t;
308,309c364,365
< 			   IF execute(t->lstlef, 0, pf1, pv)==0
< 			   THEN	execute(t->lstrit, execflg, pv, pf2);
---
> 			   IF execute(l->lstlef, 0, pf1, pv)==0
> 			   THEN	execute(l->lstrit, execflg, pv, pf2);
316,317c372,373
< 			execute(t->lstlef,0);
< 			execute(t->lstrit,execflg);
---
> 			execute(((LSTPTR)t)->lstlef,0,(INT *)0,(INT *)0);
> 			execute(((LSTPTR)t)->lstrit,execflg,(INT *)0,(INT *)0);
321,322c377,378
< 			IF execute(t->lstlef,0)==0
< 			THEN	execute(t->lstrit,execflg);
---
> 			IF execute(((LSTPTR)t)->lstlef,0,(INT *)0,(INT *)0)==0
> 			THEN	execute(((LSTPTR)t)->lstrit,execflg,(INT *)0,(INT *)0);
327,328c383,384
< 			IF execute(t->lstlef,0)!=0
< 			THEN	execute(t->lstrit,execflg);
---
> 			IF execute(((LSTPTR)t)->lstlef,0,(INT *)0,(INT *)0)!=0
> 			THEN	execute(((LSTPTR)t)->lstrit,execflg,(INT *)0,(INT *)0);
334c390,391
< 			   NAMPTR	n = lookup(t->fornam);
---
> 			   REG FORPTR	f=(FORPTR)t;
> 			   NAMPTR	n = lookup(f->fornam);
338c395
< 			   IF t->forlst==0
---
> 			   IF f->forlst==0
343c400
< 				   trim((args=scan(getarg(t->forlst)))[0]);
---
> 				   trim((args=scan(getarg(f->forlst)))[0]);
349,350c406,407
< 				execute(t->fortre,0);
< 				IF execbrk<0 THEN execbrk=0 FI
---
> 				execute(f->fortre,0,(INT *)0,(INT *)0);
> 				IF (signed char)execbrk<0 THEN execbrk=0 FI
360a418
> 			   REG WHPTR	w=(WHPTR)t;
364,366c422,424
< 			   WHILE execbrk==0 ANDF (execute(t->whtre,0)==0)==(type==TWH)
< 			   DO i=execute(t->dotre,0);
< 			      IF execbrk<0 THEN execbrk=0 FI
---
> 			   WHILE execbrk==0 ANDF (execute(w->whtre,0,(INT *)0,(INT *)0)==0)==(type==TWH)
> 			   DO i=execute(w->dotre,0,(INT *)0,(INT *)0);
> 			      IF (signed char)execbrk<0 THEN execbrk=0 FI
374,376c432,434
< 			IF execute(t->iftre,0)==0
< 			THEN	execute(t->thtre,execflg);
< 			ELSE	execute(t->eltre,execflg);
---
> 			IF execute(((IFPTR)t)->iftre,0,(INT *)0,(INT *)0)==0
> 			THEN	execute(((IFPTR)t)->thtre,execflg,(INT *)0,(INT *)0);
> 			ELSE	execute(((IFPTR)t)->eltre,execflg,(INT *)0,(INT *)0);
382,383c440,442
< 			   REG STRING	r = mactrim(t->swarg);
< 			   t=t->swlst;
---
> 			   REG SWPTR	s=(SWPTR)t;
> 			   REG STRING	r = mactrim(s->swarg);
> 			   t=(TREPTR)s->swlst;
385c444,445
< 			   DO	ARGPTR		rex=t->regptr;
---
> 			   DO	REG REGPTR	re=(REGPTR)t;
> 				ARGPTR		rex=re->regptr;
389c449
< 					THEN	execute(t->regcom,0);
---
> 					THEN	execute(re->regcom,0,(INT *)0,(INT *)0);
394c454
< 				IF t THEN t=t->regnxt FI
---
> 				IF t THEN t=(TREPTR)re->regnxt FI
408,410c468,469
< execexp(s,f)
< 	STRING		s;
< 	UFD		f;
---
> void
> execexp(STRING s, UFD f)
415c474
< 	THEN	estabf(s); fb.feval=f;
---
> 	THEN	estabf(s); fb.feval=(STRING *)(long)f;
419c478
< 	execute(cmd(NL, NLFLG|MTFLG),0);
---
> 	execute(cmd(NL, NLFLG|MTFLG),0,(INT *)0,(INT *)0);
```

### usr/sys/h/buf.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/buf.h unix-v7-c99/usr/sys/h/buf.h || true
```

Expect:

```

```

### usr/sys/h/dir.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/dir.h unix-v7-c99/usr/sys/h/dir.h || true
```

Expect:

```

```

### usr/sys/h/inode.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/inode.h unix-v7-c99/usr/sys/h/inode.h || true
```

Expect:

```
41c41
< 		};
---
> 		} u_reg;
45c45
< 		};
---
> 		} u_dev;
46a47,50
> #define	i_addr	u_reg.i_addr
> #define	i_lastr	u_reg.i_lastr
> #define	i_rdev	u_dev.i_rdev
> #define	i_group	u_dev.i_group
```

### usr/sys/h/map.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/map.h unix-v7-c99/usr/sys/h/map.h || true
```

Expect:

```
3,4c3,4
< 	short	m_size;
< 	unsigned short m_addr;
---
> 	int		m_size;		/* Armv7: 32-bit (clicks exceed 16 bits) */
> 	unsigned int	m_addr;
```

### usr/sys/h/param.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/param.h unix-v7-c99/usr/sys/h/param.h || true
```

Expect:

```
83,84c83,85
< #define	USIZE	16		/* size of user block (*64) */
< #define	UBASE	0140000		/* abs. addr of user block */
---
> #define	USIZE	256		/* size of user block (*64): 16KB u-area+kstack */
> #define	UBASE	0x4F000000U	/* kernel VA window mapping the current u-area */
> #ifndef NULL
85a87
> #endif
94c96
< #define	CBSIZE	14		/* number of chars in a clist block */
---
> #define	CBSIZE	12		/* number of chars in a clist block */
120c122
< #define	major(x)	(int)(((unsigned)x>>8))
---
> #define	major(x)	(int)(((unsigned)x>>8)&0377)
131c133
< typedef	unsigned int	ino_t;
---
> typedef	unsigned short	ino_t;
133c135
< typedef	int		label_t[6];	/* regs 2-7 */
---
> typedef	int		label_t[10];	/* regs 2-7 */
```

### usr/sys/h/proc.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/proc.h unix-v7-c99/usr/sys/h/proc.h || true
```

Expect:

```
21,22c21,22
< 	short	p_addr;		/* address of swappable image */
< 	short	p_size;		/* size of swappable image (clicks) */
---
> 	int	p_addr;		/* address of swappable image (Armv7: 32-bit click index) */
> 	int	p_size;		/* size of swappable image (clicks) */
```

### usr/sys/h/user.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/user.h unix-v7-c99/usr/sys/h/user.h || true
```

Expect:

```
38c38
< 		};
---
> 		} u_pair;
41a42,43
> #define	r_val1	u_pair.r_val1
> #define	r_val2	u_pair.r_val2
99c101,105
< extern struct user u;
---
> /*
>  * The u-area lives at the base of each process's core image.  On Armv7,
>  * resume() maps the current process there, so `u` names that window.
>  */
> #define	u	(*(struct user *)UBASE)
```

### usr/include/ctype.h

Local test:

```
diff unix-v7-c99/v7/usr/include/ctype.h unix-v7-c99/usr/include/ctype.h || true
```

Expect:

```

```
diff unix-v7-c99/v7/usr/include/errno.h unix-v7-c99/usr/include/errno.h || true
```

Expect:

```
3a4,5
> #ifndef ERRNO_H
> #define ERRNO_H
40a43,44
> extern int errno;
> #endif
```

### usr/include/grp.h

Local test:

```
diff unix-v7-c99/v7/usr/include/grp.h unix-v7-c99/usr/include/grp.h || true
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

### usr/include/pwd.h

Local test:

```
diff unix-v7-c99/v7/usr/include/pwd.h unix-v7-c99/usr/include/pwd.h || true
```

Expect:

```
0a1,2
> #ifndef PWD_H
> #define PWD_H
11a14,19
> extern struct passwd *getpwent(void);
> extern struct passwd *getpwnam(char *);
> extern struct passwd *getpwuid(int);
> extern void setpwent(void);
> extern void endpwent(void);
> #endif
```

### usr/include/setjmp.h

Local test:

```
diff unix-v7-c99/v7/usr/include/setjmp.h unix-v7-c99/usr/include/setjmp.h || true
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

### usr/include/signal.h

Local test:

```
diff unix-v7-c99/v7/usr/include/signal.h unix-v7-c99/usr/include/signal.h || true
```

Expect:

```
19,21c19,20
< int	(*signal())();
< #define	SIG_DFL	(int (*)())0
< #define	SIG_IGN	(int (*)())1
---
> #define	SIG_DFL	0
> #define	SIG_IGN	1
```

### usr/include/sys/dir.h

Local test:

```
diff unix-v7-c99/v7/usr/include/sys/dir.h unix-v7-c99/usr/include/sys/dir.h || true
```

Expect:

```
0a1,2
> #ifndef SYS_DIR_H
> #define SYS_DIR_H
8a11
> #endif
```

### usr/include/sys/stat.h

Local test:

```
diff unix-v7-c99/v7/usr/include/sys/stat.h unix-v7-c99/usr/include/sys/stat.h || true
```

Expect:

```
0a1,3
> #ifndef SYS_STAT_H
> #define SYS_STAT_H
> #include <sys/types.h>
28a32
> #endif
```

### usr/include/sys/timeb.h

Local test:

```
diff unix-v7-c99/v7/usr/include/sys/timeb.h unix-v7-c99/usr/include/sys/timeb.h || true
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

### usr/include/sys/times.h

Local test:

```
diff unix-v7-c99/v7/usr/include/sys/times.h unix-v7-c99/usr/include/sys/times.h || true
```

Expect:

```
0a1,2
> #ifndef SYS_TIMES_H
> #define SYS_TIMES_H
9a12
> #endif
```

### usr/include/sys/types.h

Local test:

```
diff unix-v7-c99/v7/usr/include/sys/types.h unix-v7-c99/usr/include/sys/types.h || true
```

Expect:

```
1,7c1,9
< typedef	long       	daddr_t;  	/* disk address */
< typedef	char *     	caddr_t;  	/* core address */
< typedef	unsigned int	ino_t;     	/* i-node number */
< typedef	long       	time_t;   	/* a time */
< typedef	int        	label_t[6]; 	/* program status */
< typedef	int        	dev_t;    	/* device code */
< typedef	long       	off_t;    	/* offset in file */
---
> #ifndef SYS_TYPES_H
> #define SYS_TYPES_H
> typedef	long		daddr_t;	/* disk address */
> typedef	char *		caddr_t;	/* core address */
> typedef	unsigned short	ino_t;		/* i-node number */
> typedef	long		time_t;		/* a time */
> typedef	int		label_t[10];	/* program status */
> typedef	int		dev_t;		/* device code */
> typedef	long		off_t;		/* offset in file */
9c11
< #define	major(x)  	(int)(((unsigned)x>>8))
---
> #define	major(x)  	(int)(((unsigned)x>>8)&0377)
11a14
> #endif
```

### usr/include/time.h

Local test:

```
diff unix-v7-c99/v7/usr/include/time.h unix-v7-c99/usr/include/time.h || true
```

Expect:

```
0a1,2
> #ifndef TIME_H
> #define TIME_H
11a14
> #endif
```

### usr/src/libc/malloc.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/malloc.c unix-v7-c99/usr/src/libc/malloc.c || true
```

Expect:

```
64,65c64,65
< 	register nw;
< 	static temp;	/*coroutines assume no auto*/
---
> 	register int nw;
> 	static int temp;	/*coroutines assume no auto*/
124a125
> void
```

### usr/sys/sys/main.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/main.c unix-v7-c99/usr/sys/sys/main.c || true
```

Expect:

```
13a14,26
> void startup(void);
> void brelse(struct buf *bp);
> void binit(void);
> void iinit(void);
> void panic(char *s);
> void printf(char *fmt, ...);
> void clkstart(void);
> void cinit(void);
> int newproc(void);
> void expand(int newsize);
> int estabur(unsigned nt, unsigned nd, unsigned ns, int sep, int xrw);
> void sched(void);
> void arm_sync_icache(void);
30c43,44
< main()
---
> void
> main(void)
38c52
< 	proc[0].p_addr = ka6->r[0];
---
> 	proc[0].p_addr = 64;
68,69c82,86
< 		expand(USIZE + (int)btoc(szicode));
< 		estabur((unsigned)0, btoc(szicode), (unsigned)0, 0, RO);
---
> 		int dclicks = ((int)btoc(szicode) + 63) & ~63;
> 		expand(USIZE + dclicks);
> 		u.u_dsize = dclicks;
> 		u.u_ssize = 0;
> 		estabur((unsigned)0, (unsigned)dclicks, (unsigned)0, 0, RO);
70a88
> 		arm_sync_icache();
90c108,109
< iinit()
---
> void
> iinit(void)
119c138,142
< char	buffers[NBUF][BSIZE+BSLOP];
---
> /* Each buffer must be word-aligned: the STM32 SDMMC internal DMA requires a
>  * 32-bit-aligned IDMABASER, so the per-buffer stride is rounded up to a
>  * multiple of 4 (BSIZE+BSLOP=514 would leave odd buffers 2-byte aligned and
>  * the DMA would corrupt those transfers). */
> char	buffers[NBUF][(BSIZE+BSLOP+3)&~3] __attribute__((aligned(4), section(KTABLES_SECTION)));
125c148
< binit()
---
> void binit(void)
```

### usr/sys/sys/malloc.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/malloc.c unix-v7-c99/usr/sys/sys/malloc.c || true
```

Expect:

```
3a4
> void wakeup(caddr_t chan);
15,16c16,17
< malloc(mp, size)
< struct map *mp;
---
> int
> malloc(struct map *mp, int size)
29c30
< 				} while ((bp-1)->m_size = bp->m_size);
---
> 				} while (((bp-1)->m_size = bp->m_size));
43,45c44,45
< mfree(mp, size, a)
< struct map *mp;
< register int a;
---
> void
> mfree(struct map *mp, int size, int a)
52c52
< 		wakeup((caddr_t)&runin);	/* Wake scheduler when freeing core */
---
> 		wakeup((caddr_t)&runin);
54,55c54,55
< 	for (; bp->m_addr<=a && bp->m_size!=0; bp++);
< 	if (bp>mp && (bp-1)->m_addr+(bp-1)->m_size == a) {
---
> 	for (; bp->m_addr<=(unsigned)a && bp->m_size!=0; bp++);
> 	if (bp>mp && (bp-1)->m_addr+(bp-1)->m_size == (unsigned)a) {
57c57
< 		if (a+size == bp->m_addr) {
---
> 		if ((unsigned)(a+size) == bp->m_addr) {
66c66
< 		if (a+size == bp->m_addr && bp->m_size) {
---
> 		if ((unsigned)(a+size) == bp->m_addr && bp->m_size) {
77c77
< 			} while (size = t);
---
> 			} while ((size = t));
```

### usr/sys/sys/prf.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/prf.c unix-v7-c99/usr/sys/sys/prf.c || true
```

Expect:

```
2,3d1
< #include "../h/systm.h"
< #include "../h/seg.h"
5c3,4
< #include "../h/conf.h"
---
> #include <stdarg.h>
> void putchar(char c);
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
83d81
< 	update();
86c84
< 		idle();
---
> 		;
95,97c93,94
< prdev(str, dev)
< char *str;
< dev_t dev;
---
> void
> prdev(char *str, dev_t dev)
110,111c107,108
< deverror(bp, o1, o2)
< register struct buf *bp;
---
> void
> deverror(register struct buf *bp, int o1, int o2)
```

### usr/src/cmd/mount.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/mount.c unix-v7-c99/usr/src/cmd/mount.c || true
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

### usr/src/cmd/umount.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/umount.c unix-v7-c99/usr/src/cmd/umount.c || true
```

Expect:

```
0a1
> #include <stdio.h>
9,10c10,11
< main(argc, argv)
< char **argv;
---
> int
> main(int argc, char **argv)
```

### usr/src/libc/getpwent.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/getpwent.c unix-v7-c99/usr/src/libc/getpwent.c || true
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

### usr/src/libc/getpwnam.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/getpwnam.c unix-v7-c99/usr/src/libc/getpwnam.c || true
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

### usr/src/libc/getpwuid.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/getpwuid.c unix-v7-c99/usr/src/libc/getpwuid.c || true
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

### usr/src/libc/strncat.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/strncat.c unix-v7-c99/usr/src/libc/strncat.c || true
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

### usr/src/libc/ttyslot.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/ttyslot.c unix-v7-c99/usr/src/libc/ttyslot.c || true
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
> char	*getttys(int f);
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
40,41c42,43
< static char *
< getttys(f)
---
> char *
> getttys(int f)
```

### usr/src/libc/execvp.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/execvp.c unix-v7-c99/usr/src/libc/execvp.c || true
```

Expect:

```
4a5
> #include <stdio.h>
9,10c10,11
< char	*execat(), *getenv();
< extern	errno;
---
> char	*execat(register char *s1, register char *s2, char *si);
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
67,70c68,69
< static char *
< execat(s1, s2, si)
< register char *s1, *s2;
< char *si;
---
> char *
> execat(register char *s1, register char *s2, char *si)
```

### usr/src/libc/getenv.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/getenv.c unix-v7-c99/usr/src/libc/getenv.c || true
```

Expect:

```
7c7
< char	*nvmatch();
---
> char	*nvmatch(register char *s1, register char *s2);
10,11c10
< getenv(name)
< register char *name;
---
> getenv(register char *name)
29,31c28,29
< static char *
< nvmatch(s1, s2)
< register char *s1, *s2;
---
> char *
> nvmatch(register char *s1, register char *s2)
```

### usr/src/libc/atoi.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/atoi.c unix-v7-c99/usr/src/libc/atoi.c || true
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

### usr/src/libc/atol.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/atol.c unix-v7-c99/usr/src/libc/atol.c || true
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

### usr/src/libc/index.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/index.c unix-v7-c99/usr/src/libc/index.c || true
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

### usr/src/libc/rindex.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/rindex.c unix-v7-c99/usr/src/libc/rindex.c || true
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

### usr/src/libc/strcat.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/strcat.c unix-v7-c99/usr/src/libc/strcat.c || true
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

### usr/src/libc/strcmp.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/strcmp.c unix-v7-c99/usr/src/libc/strcmp.c || true
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

### usr/src/libc/strcpy.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/strcpy.c unix-v7-c99/usr/src/libc/strcpy.c || true
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

### usr/src/libc/strlen.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/strlen.c unix-v7-c99/usr/src/libc/strlen.c || true
```

Expect:

```
6,7c6,7
< strlen(s)
< register char *s;
---
> int
> strlen(register const char *s)
9c9
< 	register n;
---
> 	register int n;
```

### usr/src/libc/strncmp.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/strncmp.c unix-v7-c99/usr/src/libc/strncmp.c || true
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

### usr/src/libc/strncpy.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/strncpy.c unix-v7-c99/usr/src/libc/strncpy.c || true
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

### usr/src/libc/isatty.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/isatty.c unix-v7-c99/usr/src/libc/isatty.c || true
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

### usr/src/libc/perror.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/perror.c unix-v7-c99/usr/src/libc/perror.c || true
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

### usr/src/libc/swab.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/swab.c unix-v7-c99/usr/src/libc/swab.c || true
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

### usr/src/libc/rand.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/rand.c unix-v7-c99/usr/src/libc/rand.c || true
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

### usr/src/libc/mktemp.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/mktemp.c unix-v7-c99/usr/src/libc/mktemp.c || true
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

### usr/src/libc/qsort.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/qsort.c unix-v7-c99/usr/src/libc/qsort.c || true
```

Expect:

```
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

### usr/src/libc/calloc.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/calloc.c unix-v7-c99/usr/src/libc/calloc.c || true
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
26,28c24,25
< cfree(p, num, size)
< char *p;
< unsigned num, size;
---
> void
> cfree(char *p, unsigned num, unsigned size)
29a27,28
> 	(void)num;
> 	(void)size;
```

### usr/src/libc/tell.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/tell.c unix-v7-c99/usr/src/libc/tell.c || true
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

### usr/src/libc/system.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/system.c unix-v7-c99/usr/src/libc/system.c || true
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

### usr/src/libc/timezone.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/timezone.c unix-v7-c99/usr/src/libc/timezone.c || true
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

### usr/src/libc/getlogin.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/getlogin.c unix-v7-c99/usr/src/libc/getlogin.c || true
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

### usr/src/libc/atof.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/atof.c unix-v7-c99/usr/src/libc/atof.c || true
```

Expect:

```
9,10c9
< atof(p)
< register char *p;
---
> atof(register char *p)
12c11
< 	register c;
---
> 	register int c;
13a13
> 	double ldexp(double value, int n);
15d14
< 	double ldexp();
17c16
< 	register eexp, exp, neg, negexp, bexp;
---
> 	register int eexp, exp, neg, negexp, bexp;
```

### usr/src/libc/clrerr.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/clrerr.c unix-v7-c99/usr/src/libc/clrerr.c || true
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

### usr/src/libc/endopen.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/endopen.c unix-v7-c99/usr/src/libc/endopen.c || true
```

Expect:

```
2a3
> int create(register char *file, int rw);
5,7c6
< _endopen(file, mode, iop)
< 	char *file, *mode;
< 	register FILE *iop;
---
> _endopen(char *file, char *mode, register FILE *iop)
55,58c54,55
< static int
< create(file, rw)
< 	register char *file;
< 	int rw;
---
> int
> create(register char *file, int rw)
```

### usr/src/libc/fgetc.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/fgetc.c unix-v7-c99/usr/src/libc/fgetc.c || true
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

### usr/src/libc/fgets.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/fgets.c unix-v7-c99/usr/src/libc/fgets.c || true
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

### usr/src/libc/filbuf.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/filbuf.c unix-v7-c99/usr/src/libc/filbuf.c || true
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

### usr/src/libc/findiop.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/findiop.c unix-v7-c99/usr/src/libc/findiop.c || true
```

Expect:

```
4c4
< _findiop()
---
> _findiop(void)
```

### usr/src/libc/flsbuf.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/flsbuf.c unix-v7-c99/usr/src/libc/flsbuf.c || true
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

### usr/src/libc/fopen.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/fopen.c unix-v7-c99/usr/src/libc/fopen.c || true
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

### usr/src/libc/fprintf.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/fprintf.c unix-v7-c99/usr/src/libc/fprintf.c || true
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

### usr/src/libc/fputc.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/fputc.c unix-v7-c99/usr/src/libc/fputc.c || true
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

### usr/src/libc/fputs.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/fputs.c unix-v7-c99/usr/src/libc/fputs.c || true
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

### usr/src/libc/freopen.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/freopen.c unix-v7-c99/usr/src/libc/freopen.c || true
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

### usr/src/libc/fseek.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/fseek.c unix-v7-c99/usr/src/libc/fseek.c || true
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

### usr/src/libc/ftell.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/ftell.c unix-v7-c99/usr/src/libc/ftell.c || true
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

### usr/src/libc/getchar.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/getchar.c unix-v7-c99/usr/src/libc/getchar.c || true
```

Expect:

```
8c8,9
< getchar()
---
> int
> getchar(void)
```

### usr/src/libc/getpass.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/getpass.c unix-v7-c99/usr/src/libc/getpass.c || true
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

### usr/src/libc/gets.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/gets.c unix-v7-c99/usr/src/libc/gets.c || true
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

### usr/src/libc/printf.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/printf.c unix-v7-c99/usr/src/libc/printf.c || true
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

### usr/src/libc/putchar.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/putchar.c unix-v7-c99/usr/src/libc/putchar.c || true
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

### usr/src/libc/puts.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/puts.c unix-v7-c99/usr/src/libc/puts.c || true
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

### usr/src/libc/rdwr.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/rdwr.c unix-v7-c99/usr/src/libc/rdwr.c || true
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

### usr/src/libc/rew.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/rew.c unix-v7-c99/usr/src/libc/rew.c || true
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

### usr/src/libc/scanf.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/scanf.c unix-v7-c99/usr/src/libc/scanf.c || true
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

### usr/src/libc/setbuf.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/setbuf.c unix-v7-c99/usr/src/libc/setbuf.c || true
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

### usr/src/libc/sprintf.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/sprintf.c unix-v7-c99/usr/src/libc/sprintf.c || true
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

### usr/src/libc/strout.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/strout.c unix-v7-c99/usr/src/libc/strout.c || true
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

### usr/src/libc/ungetc.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/ungetc.c unix-v7-c99/usr/src/libc/ungetc.c || true
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

### usr/src/libc/ctime.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/ctime.c unix-v7-c99/usr/src/libc/ctime.c || true
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
76a77,79
> static int	sunday(register struct tm *t, register int d);
> int	dysize(int y);
> int	ftime(struct timeb *tp);
79,80c82
< ctime(t)
< long *t;
---
> ctime(long *t)
86,87c88
< localtime(tim)
< long *tim;
---
> localtime(long *tim)
91c92
< 	register daylbegin, daylend;
---
> 	register int daylbegin, daylend;
122,125c123,124
< static
< sunday(t, d)
< register struct tm *t;
< register int d;
---
> static int
> sunday(register struct tm *t, register int d)
133,134c132
< gmtime(tim)
< long *tim;
---
> gmtime(long *tim)
195,196c193
< asctime(t)
< struct tm *t;
---
> asctime(struct tm *t)
202c199,200
< 	for (ncp = "Day Mon 00 00:00:00 1900\n"; *cp++ = *ncp++;);
---
> 	for (ncp = "Day Mon 00 00:00:00 1900\n"; (*cp++ = *ncp++);)
> 		;
227c225,226
< dysize(y)
---
> int
> dysize(int y)
234,236c233,234
< static char *
< ct_numb(cp, n)
< register char *cp;
---
> char *
> ct_numb(register char *cp, int n)
```

### usr/src/cmd/getty.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/getty.c unix-v7-c99/usr/src/cmd/getty.c || true
```

Expect:

```
13a14,22
> int read(int fd, char *buf, int n);
> int write(int fd, char *buf, int n);
> int ioctl(int fd, int cmd, void *arg);
> int stty(int fd, void *buf);
> int execl(char *path, char *arg0, ...);
> void exit(int n);
> int getname(void);
> void puts(char *as);
> void putchr(int cc);
26c35
< 	'0', 1,
---
> 	{ '0', 1,
29c38
< 	"\n\r\033;\007login: ",
---
> 	"\n\r\033;\007login: " },
31c40
< 	1, 2,
---
> 	{ 1, 2,
34c43
< 	"\n\r\033;login: ",
---
> 	"\n\r\033;login: " },
36c45
< 	2, 3,
---
> 	{ 2, 3,
39c48
< 	"\n\r\033:\006\006\017login: ",
---
> 	"\n\r\033:\006\006\017login: " },
41c50
< 	3, '0',
---
> 	{ 3, '0',
44c53
< 	"\n\rlogin: ",
---
> 	"\n\rlogin: " },
47c56
< 	'-', '-',
---
> 	{ '-', '-',
50c59
< 	"\n\rlogin: ",
---
> 	"\n\rlogin: " },
53c62
< 	'1', '1',
---
> 	{ '1', '1',
56c65
< 	"\n\r\033:\006\006\017login: ",
---
> 	"\n\r\033:\006\006\017login: " },
59c68
< 	'2', '2',
---
> 	{ '2', '2',
62c71
< 	"\n\r\033;login: ",
---
> 	"\n\r\033;login: " },
65c74
< 	'3', '5',
---
> 	{ '3', '5',
68c77
< 	"\n\r\033;login: ",
---
> 	"\n\r\033;login: " },
71c80
< 	'5', '3',
---
> 	{ '5', '3',
74c83
< 	"\n\r\033;\007login: ",
---
> 	"\n\r\033;\007login: " },
77c86
< 	'4', '4',
---
> 	{ '4', '4',
80c89
< 	"\n\rlogin: ",
---
> 	"\n\rlogin: " },
83c92
< 	'i', 'i',
---
> 	{ 'i', 'i',
86c95
< 	"\n\rlogin: ",
---
> 	"\n\rlogin: " },
89c98
< 	'l', 'l',
---
> 	{ 'l', 'l',
92c101
< 	"*",
---
> 	"*" },
94c103
< 	'6', '6',
---
> 	{ '6', '6',
97c106
< 	"\n\rlogin: ",
---
> 	"\n\rlogin: " },
128,129c137,138
< main(argc, argv)
< char **argv;
---
> int
> main(int argc, char *argv[])
178c187,188
< getname()
---
> int
> getname(void)
181c191
< 	register c;
---
> 	register int c;
222,223c232,233
< puts(as)
< char *as;
---
> void
> puts(char *as)
232c242,243
< putchr(cc)
---
> void
> putchr(int cc)
```

### usr/src/cmd/init.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/init.c unix-v7-c99/usr/src/cmd/init.c || true
```

Expect:

```
4a5
> #include <stdio.h>
38c39,52
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
> int
> main(void)
40d53
< 	int reset();
43c56
< 	signal(SIGHUP, reset);
---
> 	signal(SIGHUP, (int)reset);
50a64
> 	return(0);
53c67,68
< shutdown()
---
> int
> shutdown(void)
55c70
< 	register i;
---
> 	register int i;
61c76
< 	signal(SIGALRM, reset);
---
> 	signal(SIGALRM, (int)reset);
70a86
> 	return(0);
73c89,90
< single()
---
> int
> single(void)
75c92
< 	register pid;
---
> 	register int pid;
92a110
> 	return(0);
95c113,114
< runcom()
---
> int
> runcom(void)
97c116
< 	register pid;
---
> 	register int pid;
108a128
> 	return(0);
111c131,132
< multiple()
---
> int
> multiple(void)
114c135
< 	register pid;
---
> 	register int pid;
119c140
< 			return;
---
> 			return(0);
128,129c149,150
< term(p)
< register struct tab *p;
---
> int
> term(struct tab *p)
137a159
> 	return(0);
140c162,163
< rline()
---
> int
> rline(void)
142c165
< 	register c, i;
---
> 	register int c, i;
174,175c197,198
< maktty(lin)
< char *lin;
---
> int
> maktty(char *lin)
177c200
< 	register i, j;
---
> 	register int i, j;
185a209
> 	return(0);
188c212,213
< get()
---
> int
> get(void)
199c224,225
< merge()
---
> int
> merge(void)
202c228
< 	register i;
---
> 	register int i;
205c231
< 	signal(SIGINT, merge);
---
> 	signal(SIGINT, (int)merge);
208c234
< 		return;
---
> 		return(0);
240a267
> 	return(0);
243,244c270,271
< dfork(p)
< struct tab *p;
---
> int
> dfork(struct tab *p)
246c273
< 	register pid;
---
> 	register int pid;
263a291
> 	return(0);
266,267c294,295
< rmut(p)
< register struct tab *p;
---
> int
> rmut(struct tab *p)
269c297
< 	register i, f;
---
> 	register int i, f;
296a325
> 	return(0);
299c328,329
< reset()
---
> void
> reset(void)
```

### usr/src/cmd/accton.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/accton.c unix-v7-c99/usr/src/cmd/accton.c || true
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
4c5,6
< 	extern errno;
---
> 	extern int errno;
> 	int acct(char *file);
```

### usr/src/cmd/update.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/update.c unix-v7-c99/usr/src/cmd/update.c || true
```

Expect:

```
5a6
> #include <stdio.h>
7a9
> int	dosync(void);
15c17,18
< main()
---
> int
> main(void)
31c34,35
< dosync()
---
> int
> dosync(void)
34c38
< 	signal(SIGALRM, dosync);
---
> 	signal(SIGALRM, (int)dosync);
35a40
> 	return(0);
```

### usr/src/cmd/atrun.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/atrun.c unix-v7-c99/usr/src/cmd/atrun.c || true
```

Expect:

```
13a14
> int	makenowtime(void), updatetime(int t), run(char *file);
18,19c19,20
< main(argc, argv)
< char **argv;
---
> int
> main(int argc, char **argv)
24a26
> 	(void)argc; (void)argv;
52c54,55
< makenowtime()
---
> int
> makenowtime(void)
55d57
< 	struct tm *localtime();
62a65
> 	return(0);
65c68,69
< updatetime(t)
---
> int
> updatetime(int t)
74a79
> 	return(0);
77,78c82,83
< run(file)
< char *file;
---
> int
> run(char *file)
81c86
< 	register pid, i;
---
> 	register int pid, i;
85c90
< 		return;
---
> 		return(0);
96c101
< 	if (pid = fork()) {
---
> 	if ((pid = fork())) {
107a113
> 	return(0);
```

### usr/src/cmd/passwd.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/passwd.c unix-v7-c99/usr/src/cmd/passwd.c || true
```

Expect:

```
13,18d12
< struct	passwd *getpwent();
< int	endpwent();
< char	*strcpy();
< char	*crypt();
< char	*getpass();
< char	*getlogin();
23,24c17,18
< main(argc, argv)
< char *argv[];
---
> int
> main(int argc, char *argv[])
75c69
< 	while(c = *p++){
---
> 	while((c = *p++)){
111,113c105,107
< 	signal(SIGHUP, SIG_IGN);
< 	signal(SIGINT, SIG_IGN);
< 	signal(SIGQUIT, SIG_IGN);
---
> 	signal(SIGHUP, (int)SIG_IGN);
> 	signal(SIGINT, (int)SIG_IGN);
> 	signal(SIGQUIT, (int)SIG_IGN);
```

### usr/src/cmd/fortune.c

Local test:

```
diff unix-v7-c99/v7/usr/src/games/fortune.c unix-v7-c99/usr/src/cmd/fortune.c || true
```

Expect:

```
6c6,7
< main()
---
> int
> main(void)
```

### usr/src/cmd/arithmetic.c

Local test:

```
diff unix-v7-c99/v7/usr/src/games/arithmetic.c unix-v7-c99/usr/src/cmd/arithmetic.c || true
```

Expect:

```
0a1
> #include <stdio.h>
4a6,7
> int	getnum(char *s), random(int range), skrand(int range);
> int	score(void), getline(char *s), delete(void);
14,15c17,18
< main(argc,argv)
< char	*argv[];
---
> int
> main(int argc, char *argv[])
20c23
< 	extern	delete();
---
> 	extern int delete(void);
22c25
< 	signal(SIGINT, delete);
---
> 	signal(SIGINT, (int)delete);
32c35
< 			while(types[dif] = argv[1][dif])
---
> 			while((types[dif] = argv[1][dif]))
121,122c124,125
< getline(s)
< char *s;
---
> int
> getline(char *s)
139a143
> 	return(0);
142,143c146,147
< getnum(s)
< char *s;
---
> int
> getnum(char *s)
156c160,161
< random(range)
---
> int
> random(int range)
161c166,168
< skrand(range){
---
> int
> skrand(int range)
> {
168c175,176
< score()
---
> int
> score(void)
175c183
< 	if(rights == 0)	return;
---
> 	if(rights == 0)	return(0);
182a191
> 	return(0);
185c194,195
< delete()
---
> int
> delete(void)
192a203
> 	return(0);
```

### usr/src/cmd/hangman.c

Local test:

```
diff unix-v7-c99/v7/usr/src/games/hangman.c unix-v7-c99/usr/src/cmd/hangman.c || true
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

### usr/src/cmd/ac.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/ac.c unix-v7-c99/usr/src/cmd/ac.c || true
```

Expect:

```
35,36c35,38
< main(argc, argv) 
< char **argv;
---
> int	loop(void), print(void), upall(int f), update(struct tbuf *tp, int f);
> int	among(int i), newday(void), pdate(void);
> int
> main(int argc, char **argv)
39c41
< 	register i;
---
> 	register int i;
92c94,95
< loop()
---
> int
> loop(void)
94c97
< 	register i;
---
> 	register int i;
100c103
< 		return;
---
> 		return(0);
104c107
< 			return;
---
> 			return(0);
108c111
< 		return;
---
> 		return(0);
125c128
< 		return;
---
> 		return(0);
134a138
> 	return(0);
137c141,142
< print()
---
> int
> print(void)
157a163
> 	return(0);
160c166,167
< upall(f)
---
> int
> upall(int f)
165a173
> 	return(0);
168,169c176,177
< update(tp, f)
< struct tbuf *tp;
---
> int
> update(struct tbuf *tp, int f)
186c194
< 		return;
---
> 		return(0);
189c197
< 		return;
---
> 		return(0);
200a209
> 	return(0);
203c212,213
< among(i)
---
> int
> among(int i)
205c215
< 	register j, k;
---
> 	register int j, k;
223c233,234
< newday()
---
> int
> newday(void)
227c238
< 	struct tm *localtime();
---
> 	struct tm *localtime(long *tim);
237a249
> 	return(0);
240c252,253
< pdate()
---
> int
> pdate(void)
243c256
< 	char *ctime();
---
> 	char *ctime(long *);
246c259
< 		return;
---
> 		return(0);
248a262
> 	return(0);
```

### usr/src/cmd/cron.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/cron.c unix-v7-c99/usr/src/cmd/cron.c || true
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
25c25,28
< main()
---
> int	slp(void), ex(char *s), init(void), number(register int c);
> int	open(char *path, int mode), close(int fd);
> int
> main(void)
28c31
< 	char *cmp();
---
> 	char *cmp(char *p, int v);
29a33
> 	struct stat cstat;
36,40c40,46
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
45,46c51,69
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
47a71
> 	for (itime+=60;; itime+=60, slp()) {
70a95
> 	return(0);
74,75c99
< cmp(p, v)
< char *p;
---
> cmp(char *p, int v)
110c134,135
< slp()
---
> int
> slp(void)
112c137
< 	register i;
---
> 	register int i;
118a144,146
> 	else
> 		sleep(1);
> 	return(0);
121,124c149,150
< ex(s)
< char *s;
< {
< 	int st;
---
> int
> ex(char *s)
125a152
> {
127,128c154,155
< 		wait(&st);
< 		return;
---
> 		wait((int *)0);
> 		return(0);
130,131d156
< 	if(fork())
< 		exit(0);
134a160
> 	return(0);
137c163,164
< init()
---
> int
> init(void)
139c166
< 	register i, c;
---
> 	register int i, c;
232c259
< 			return;
---
> 			return(0);
239,240c266,267
< number(c)
< register c;
---
> int
> number(register int c)
242c269
< 	register n = 0;
---
> 	register int n = 0;
```

### usr/src/cmd/quot.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/quot.c unix-v7-c99/usr/src/cmd/quot.c || true
```

Expect:

```
42,44c42,47
< struct	passwd	*getpwent();
< char	*malloc();
< char	*copy();
---
> char	*malloc(unsigned n);
> char	*copy(char *s);
> int	scanf(char *fmt, ...);
> int	check(char *file), acct(register struct dinode *ip);
> int	bread(unsigned bno, char *buf, int cnt);
> int	qcmp(const void *vp1, const void *vp2), report(void);
46,47c49,50
< main(argc, argv)
< char **argv;
---
> int
> main(int argc, char **argv)
87,88c90,91
< check(file)
< char *file;
---
> int
> check(char *file)
91c94
< 	register c;
---
> 	register int c;
96c99
< 		return;
---
> 		return(0);
115a119
> 	return(0);
118,119c122,123
< acct(ip)
< register struct dinode *ip;
---
> int
> acct(register struct dinode *ip)
121c125
< 	register n;
---
> 	register int n;
123c127
< 	static fino;
---
> 	static int fino;
126c130
< 		return;
---
> 		return(0);
129c133
< 			return;
---
> 			return(0);
136c140
< 		return;
---
> 		return(0);
139c143
< 		return;
---
> 		return(0);
146,149c150,153
< 				return;
< 		if (fino > ino)
< 			return;
< 		if (fino<ino) {
---
> 				return(0);
> 		if (fino > (int)ino)
> 			return(0);
> 		if (fino<(int)ino) {
155c159
< 		if (np = du[ip->di_uid].name)
---
> 		if ((np = du[ip->di_uid].name))
167a172
> 	return(0);
170,172c175,176
< bread(bno, buf, cnt)
< unsigned bno;
< char *buf;
---
> int
> bread(unsigned bno, char *buf, int cnt)
179a184
> 	return(0);
182,183c187,188
< qcmp(p1, p2)
< register struct du *p1, *p2;
---
> int
> qcmp(const void *vp1, const void *vp2)
184a190
> 	register const struct du *p1 = vp1, *p2 = vp2;
192c198,199
< report()
---
> int
> report(void)
194c201
< 	register i;
---
> 	register int i;
197c204
< 		return;
---
> 		return(0);
206c213
< 		return;
---
> 		return(0);
211c218
< 			return;
---
> 			return(0);
219a227
> 	return(0);
223,224c231
< copy(s)
< char *s;
---
> copy(char *s)
227c234
< 	register n;
---
> 	register int n;
232c239
< 	for(n=0; p[n] = s[n]; n++)
---
> 	for(n=0; (p[n] = s[n]); n++)
```

### usr/src/cmd/dump.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/dump.c unix-v7-c99/usr/src/cmd/dump.c || true
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

### usr/src/cmd/dumpdir.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/dumpdir.c unix-v7-c99/usr/src/cmd/dumpdir.c || true
```

Expect:

```
51,52c51,76
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
> int
> main(int argc, char *argv[])
54c78
< 	extern char *ctime();
---
> 	extern char *ctime(long *t);
86c110
< 	i = 0;
---
> int	i = 0;
91c115,116
< pass1()
---
> int
> pass1(void)
93c118
< 	register i;
---
> 	register int i;
95c120
< 	int	putdir(), null();
---
> 	int	putdir(char *b), null(void);
113c138
< 			return;
---
> 			return(0);
127,129c152,153
< printem(prefix, inum)
< char *prefix;
< ino_t	inum;
---
> int
> printem(char *prefix, ino_t inum)
139c163
< 	return;
---
> 	return(0);
145c169
< 			return;
---
> 			return(0);
169,172c193,194
< getfile(n, f1, f2, size)
< ino_t	n;
< int	(*f2)(), (*f1)();
< long	size;
---
> int
> getfile(ino_t n, int (*f1)(), int (*f2)(), long size)
174c196
< 	register i;
---
> 	register int i;
177a200
> 	(void)n;
187c210
< 			return;
---
> 			return(0);
205c228
< 				return;
---
> 				return(0);
215,216c238,239
< readtape(b)
< char *b;
---
> int
> readtape(char *b)
218c241
< 	register i;
---
> 	register int i;
249c272
< 			return;
---
> 			return(0);
252a276
> 	return(0);
255c279,280
< flsht()
---
> int
> flsht(void)
257a283
> 	return(0);
260,261c286,287
< copy(f, t, s)
< register char *f, *t;
---
> int
> copy(register char *f, register char *t, int s)
263c289
< 	register i;
---
> 	register int i;
268a295
> 	return(0);
271,272c298,299
< clearbuf(cp)
< register char *cp;
---
> int
> clearbuf(register char *cp)
274c301
< 	register i;
---
> 	register int i;
279a307
> 	return(0);
286,287c314,315
< putent(cp)
< char	*cp;
---
> int
> putent(char *cp)
289c317
< 	register i;
---
> 	register int i;
291c319
< 	for (i = 0; i < sizeof(ino_t); i++)
---
> 	for (i = 0; i < (int)sizeof(ino_t); i++)
296c324
< 			return;
---
> 			return(0);
298c326
< 	return;
---
> 	return(0);
301,302c329,330
< getent(bf)
< register char *bf;
---
> int
> getent(register char *bf)
304c332
< 	register i;
---
> 	register int i;
306c334
< 	for (i = 0; i < sizeof(ino_t); i++)
---
> 	for (i = 0; i < (int)sizeof(ino_t); i++)
310,311c338,339
< 			return;
< 	return;
---
> 			return(0);
> 	return(0);
317,318c345,346
< writec(c)
< char c;
---
> int
> writec(int c)
319a348
> 	char cc = c;
321c350,351
< 	fwrite(&c, 1, 1, df);
---
> 	fwrite(&cc, 1, 1, df);
> 	return(0);
324c354,355
< readc()
---
> int
> readc(void)
332,333c363,364
< mseek(pt)
< daddr_t pt;
---
> int
> mseek(daddr_t pt)
335a367
> 	return(0);
338c370,371
< flsh()
---
> int
> flsh(void)
340a374
> 	return(0);
347,348c381,382
< search(inum)
< ino_t	inum;
---
> int
> search(ino_t inum)
350c384
< 	register low, high, probe;
---
> 	register int low, high, probe;
368,369c402,403
< direq(s1, s2)
< register char *s1, *s2;
---
> int
> direq(register char *s1, register char *s2)
371c405
< 	register i;
---
> 	register int i;
386,387c420,421
< gethead(buf)
< struct spcl *buf;
---
> int
> gethead(struct spcl *buf)
398,400c432,433
< checktype(b, t)
< struct	spcl *b;
< int	t;
---
> int
> checktype(struct spcl *b, int t)
406,407c439,440
< checksum(b)
< int *b;
---
> int
> checksum(int *b)
409c442
< 	register i, j;
---
> 	register int i, j;
423,425c456,457
< checkvol(b, t)
< struct spcl *b;
< int t;
---
> int
> checkvol(struct spcl *b, int t)
432,433c464,465
< readhdr(b)
< struct	spcl *b;
---
> int
> readhdr(struct spcl *b)
442,443c474,475
< putdir(b)
< char *b;
---
> int
> putdir(char *b)
446c478
< 	register i;
---
> 	register int i;
452a485
> 	return(0);
458,459c491,492
< readbits(m)
< short	*m;
---
> int
> readbits(short *m)
461c494
< 	register i;
---
> 	register int i;
470a504
> 	return(0);
473c507
< null() { ; }
---
> int null(void) { return(0); }
```

### usr/src/cmd/restor.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/restor.c unix-v7-c99/usr/src/cmd/restor.c || true
```

Expect:

```
84,85c84,127
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
> int
> main(int argc, char *argv[])
89c131
< 	int done();
---
> 	int done(void);
120,123c162,165
< 		if (signal(SIGINT, done) == SIG_IGN)
< 			signal(SIGINT, SIG_IGN);
< 		if (signal(SIGTERM, done) == SIG_IGN)
< 			signal(SIGTERM, SIG_IGN);
---
> 		if (signal(SIGINT, (int)done) == (int)SIG_IGN)
> 			signal(SIGINT, (int)SIG_IGN);
> 		if (signal(SIGTERM, (int)done) == (int)SIG_IGN)
> 			signal(SIGTERM, (int)SIG_IGN);
143,146c185,186
< doit(command, argc, argv)
< char	command;
< int	argc;
< char	*argv[];
---
> int
> doit(int command, int argc, char *argv[])
148,149c188,189
< 	extern char *ctime();
< 	register i, k;
---
> 	extern char *ctime(long *t);
> 	register int i, k;
152c192
< 	int	xtrfile(), skip();
---
> 	int	xtrfile(char *b, long size), skip(void);
154c194
< 	int	rstrfile(), rstrskip();
---
> 	int	rstrfile(char *b, long s), rstrskip(char *b, long s);
179c219
< 		return;
---
> 		return(0);
208c248
< 			return;
---
> 			return(0);
251c291
< 					return;
---
> 				return(0);
300c340
< 			if (gets(tbf) == EOF) {
---
> 			if ((int)gets(tbf) == EOF) {
340c380
< 				return;
---
> 				return(0);
397a438
> 	return(0);
405c446,447
< pass1()
---
> int
> pass1(void)
407c449
< 	register i;
---
> 	register int i;
409c451
< 	int	putdir(), null();
---
> 	int	putdir(char *b), null();
427c469
< 			return;
---
> 			return(0);
446,449c488,489
< getfile(n, f1, f2, size)
< ino_t	n;
< int	(*f2)(), (*f1)();
< long	size;
---
> int
> getfile(ino_t n, int (*f1)(), int (*f2)(), long size)
451c491
< 	register i;
---
> 	register int i;
466c506
< 			return;
---
> 			return(0);
485c525
< 				return;
---
> 				return(0);
495,496c535,536
< readtape(b)
< char *b;
---
> int
> readtape(char *b)
498c538
< 	register i;
---
> 	register int i;
533c573
< 			return;
---
> 			return(0);
536a577
> 	return(0);
539c580,581
< flsht()
---
> int
> flsht(void)
541a584
> 	return(0);
544,545c587,588
< copy(f, t, s)
< register char *f, *t;
---
> int
> copy(register char *f, register char *t, int s)
547c590
< 	register i;
---
> 	register int i;
552a596
> 	return(0);
555,556c599,600
< clearbuf(cp)
< register char *cp;
---
> int
> clearbuf(register char *cp)
558c602
< 	register i;
---
> 	register int i;
563a608
> 	return(0);
571,572c616,617
< putent(cp)
< char	*cp;
---
> int
> putent(char *cp)
574c619
< 	register i;
---
> 	register int i;
576c621
< 	for (i = 0; i < sizeof(ino_t); i++)
---
> 	for (i = 0; i < (int)sizeof(ino_t); i++)
581c626
< 			return;
---
> 			return(0);
583c628
< 	return;
---
> 	return(0);
586,587c631,632
< getent(bf)
< register char *bf;
---
> int
> getent(register char *bf)
589c634
< 	register i;
---
> 	register int i;
591c636
< 	for (i = 0; i < sizeof(ino_t); i++)
---
> 	for (i = 0; i < (int)sizeof(ino_t); i++)
595,596c640,641
< 			return;
< 	return;
---
> 			return(0);
> 	return(0);
602,603c647,648
< writec(c)
< char c;
---
> int
> writec(int c)
610a656
> 	return(0);
613c659,660
< readc()
---
> int
> readc(void)
622,623c669,670
< mseek(pt)
< daddr_t pt;
---
> int
> mseek(daddr_t pt)
626a674
> 	return(0);
629c677,678
< flsh()
---
> int
> flsh(void)
631a681
> 	return(0);
639,641c689
< search(inum, cp)
< ino_t	inum;
< char	*cp;
---
> search(ino_t inum, char *cp)
643c691
< 	register i;
---
> 	register int i;
665,666c713,714
< psearch(n)
< char	*n;
---
> int
> psearch(char *n)
693,694c741,742
< direq(s1, s2)
< register char *s1, *s2;
---
> int
> direq(register char *s1, register char *s2)
696c744
< 	register i;
---
> 	register int i;
712,714c760,761
< dwrite(bno, b)
< daddr_t	bno;
< char	*b;
---
> int
> dwrite(daddr_t bno, char *b)
716c763
< 	register i;
---
> 	register int i;
735a783
> 	return(0);
738,740c786,787
< dread(bno, buf, cnt)
< daddr_t bno;
< char *buf;
---
> int
> dread(daddr_t bno, char *buf, int cnt)
742c789
< 	register i, j;
---
> 	register int i, j;
751c798
< 			return;
---
> 			return(0);
771a819
> 	return(0);
779,780c827,828
< clri(ip)
< struct dinode *ip;
---
> int
> clri(struct dinode *ip)
787a836
> 	return(0);
793,794c842,843
< itrunc(ip)
< register struct dinode *ip;
---
> int
> itrunc(register struct dinode *ip)
796c845
< 	register i;
---
> 	register int i;
800c849
< 		return;
---
> 		return(0);
803c852
< 		return;
---
> 		return(0);
826a876
> 	return(0);
829,831c879,880
< tloop(bn, f1, f2)
< daddr_t	bn;
< int	f1, f2;
---
> int
> tloop(daddr_t bn, int f1, int f2)
833c882
< 	register i;
---
> 	register int i;
850a900
> 	return(0);
853,854c903,904
< bfree(bn)
< daddr_t	bn;
---
> int
> bfree(daddr_t bn)
856c906
< 	register i;
---
> 	register int i;
863c913
< 		fbuf.df_nfree = sblock.s_nfree;
---
> 		fbuf.frees.df_nfree = sblock.s_nfree;
865c915
< 			fbuf.df_free[i] = sblock.s_free[i];
---
> 			fbuf.frees.df_free[i] = sblock.s_free[i];
869a920
> 	return(0);
876c927
< balloc()
---
> balloc(void)
879c930
< 	register i;
---
> 	register int i;
896c947
< 		sblock.s_nfree = fbuf.df_nfree;
---
> 		sblock.s_nfree = fbuf.frees.df_nfree;
898c949
< 			sblock.s_free[i] = fbuf.df_free[i];
---
> 			sblock.s_free[i] = fbuf.frees.df_free[i];
910,912c961
< bmap(iaddr, bn)
< daddr_t	iaddr[NADDR];
< daddr_t	bn;
---
> bmap(daddr_t iaddr[NADDR], daddr_t bn)
914c963
< 	register i;
---
> 	register int i;
976,977c1025,1026
< gethead(buf)
< struct spcl *buf;
---
> int
> gethead(struct spcl *buf)
988,989c1037,1038
< ishead(buf)
< struct spcl *buf;
---
> int
> ishead(struct spcl *buf)
996,998c1045,1046
< checktype(b, t)
< struct	spcl *b;
< int	t;
---
> int
> checktype(struct spcl *b, int t)
1004,1005c1052,1053
< checksum(b)
< int *b;
---
> int
> checksum(int *b)
1007c1055
< 	register i, j;
---
> 	register int i, j;
1021,1023c1069,1070
< checkvol(b, t)
< struct spcl *b;
< int t;
---
> int
> checkvol(struct spcl *b, int t)
1030,1031c1077,1078
< readhdr(b)
< struct	spcl *b;
---
> int
> readhdr(struct spcl *b)
1045,1047c1092,1093
< xtrfile(b, size)
< char	*b;
< long	size;
---
> int
> xtrfile(char *b, long size)
1049a1096
> 	return(0);
1052c1099
< null() {;}
---
> int null(void) {return(0);}
1054c1101,1102
< skip()
---
> int
> skip(void)
1056a1105
> 	return(0);
1061,1063c1110,1111
< rstrfile(b, s)
< char *b;
< long s;
---
> int
> rstrfile(char *b, long s)
1066a1115
> 	(void)s;
1069a1119
> 	return(0);
1072,1074c1122,1123
< rstrskip(b, s)
< char *b;
< long s;
---
> int
> rstrskip(char *b, long s)
1075a1125
> 	(void)b; (void)s;
1076a1127
> 	return(0);
1080,1081c1131,1132
< putdir(b)
< char *b;
---
> int
> putdir(char *b)
1084c1135
< 	register i;
---
> 	register int i;
1090a1142
> 	return(0);
1097,1099c1149,1150
< getdino(inum, b)
< ino_t	inum;
< struct	dinode *b;
---
> int
> getdino(ino_t inum, struct dinode *b)
1107a1159
> 	return(0);
1110,1112c1162,1163
< putdino(inum, b)
< ino_t	inum;
< struct	dinode *b;
---
> int
> putdino(ino_t inum, struct dinode *b)
1120a1172
> 	return(0);
1126,1127c1178,1179
< readbits(m)
< short	*m;
---
> int
> readbits(short *m)
1129c1181
< 	register i;
---
> 	register int i;
1138a1191
> 	return(0);
1141c1194,1195
< done()
---
> int
> done(void)
1146a1201
> 	return(0);
```

### usr/src/cmd/tk.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/tk.c unix-v7-c99/usr/src/cmd/tk.c || true
```

Expect:

```
37,39c37,39
< main(argc, argv)
< int argc;
< char **argv;
---
> int	init(void), sendpt(int a), kwait(void), execom(void);
> int
> main(int argc, char **argv)
41,42c41,42
< 	register i, j;
< 	extern ex();
---
> 	register int i, j;
> 	extern int ex(void);
47c47
< 				if (i = atoi(&argv[0][2]))
---
> 				if ((i = atoi(&argv[0][2])))
49c49
< 					yyll = MAXY + 1 - pl;
---
> 				yyll = MAXY + 1 - pl;
52c52
< 				if (i = atoi(&argv[0][1])) {
---
> 				if ((i = atoi(&argv[0][1]))) {
67c67
< 	signal(SIGINT, ex);
---
> 	signal(SIGINT, (int)ex);
75a76
> 			/* fallthrough */
150a152
> 	return(0);
153c155,156
< init()
---
> int
> init(void)
168a172
> 	return(0);
171c175,176
< ex()
---
> int
> ex(void)
177a183
> 	return(0);
180c186,187
< kwait()
---
> int
> kwait(void)
182c189
< 	register c;
---
> 	register int c;
186c193
< 		return;
---
> 		return(0);
196a204
> 	return(0);
199c207,208
< execom()
---
> int
> execom(void)
204,205c213,214
< 		si = signal(SIGINT, SIG_IGN);
< 		sq = signal(SIGQUIT, SIG_IGN);
---
> 		si = (int (*)())signal(SIGINT, (int)SIG_IGN);
> 		sq = (int (*)())signal(SIGQUIT, (int)SIG_IGN);
207,209c216,218
< 		signal(SIGINT, si);
< 		signal(SIGQUIT, sq);
< 		return;
---
> 		signal(SIGINT, (int)si);
> 		signal(SIGQUIT, (int)sq);
> 		return(0);
215a225
> 	return(0);
218c228,229
< sendpt(a)
---
> int
> sendpt(int a)
220c231
< 	register zz;
---
> 	register int zz;
224c235
< 		return;
---
> 		return(0);
228c239
< 	xb = ((xx & 03) + ((zz<<2) & 014) & 017);
---
> 	xb = (((xx & 03) + ((zz<<2) & 014)) & 017);
247a259
> 	return(0);
```

### usr/src/cmd/units.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/units.c unix-v7-c99/usr/src/cmd/units.c || true
```

Expect:

```
7,9d6
< double	getflt();
< int	fperr();
< struct	table	*hash();
21a19,25
> double	getflt(void);
> int	fperr(int sig);
> struct	table	*hash(char *name);
> int	init(void), convr(struct unit *up), units(struct unit *up);
> int	pu(int u, int i, int f);
> int	lookup(char *name, struct unit *up, int den, int c);
> int	equal(char *s1, char *s2), get(void);
29,45c33,49
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
52,53c56,57
< main(argc, argv)
< char *argv[];
---
> int
> main(int argc, char *argv[])
55c59
< 	register i;
---
> 	register int i;
72c76
< 	signal(8, fperr);
---
> 	signal(8, (int)fperr);
109,110c113,114
< units(up)
< struct unit *up;
---
> int
> units(struct unit *up)
113c117
< 	register f, i;
---
> 	register int f, i;
126a131
> 	return(0);
129c134,135
< pu(u, i, f)
---
> int
> pu(int u, int i, int f)
140c146
< 			return(2);
---
> 		return(2);
147,148c153,154
< convr(up)
< struct unit *up;
---
> int
> convr(struct unit *up)
151c157
< 	register c;
---
> 	register int c;
198,200c204,205
< lookup(name, up, den, c)
< char *name;
< struct unit *up;
---
> int
> lookup(char *name, struct unit *up, int den, int c)
204c209
< 	register i;
---
> 	register int i;
230c235
< 	for(i=0; cp1 = prefix[i].pname; i++) {
---
> 	for(i=0; (cp1 = prefix[i].pname); i++) {
252,253c257,258
< equal(s1, s2)
< char *s1, *s2;
---
> int
> equal(char *s1, char *s2)
265c270,271
< init()
---
> int
> init(void)
291c297
< 		printf("%l units; %l bytes\n\n", i, cp-names);
---
> 		printf("%d units; %d bytes\n\n", i, (int)(cp-names));
297c303
< 			units(tp);
---
> 			units((struct unit *)tp);
301c307
< 		return;
---
> 		return(0);
333c339
< 	convr(lp);
---
> 	convr((struct unit *)lp);
359c365
< getflt()
---
> getflt(void)
361c367
< 	register c, i, dp;
---
> 	register int c, i, dp;
415c421,422
< get()
---
> int
> get(void)
417c424
< 	register c;
---
> 	register int c;
419c426
< 	if(c=peekc) {
---
> 	if((c=peekc)) {
435,436c442
< hash(name)
< char *name;
---
> hash(char *name)
459c465,466
< fperr()
---
> int
> fperr(int sig)
462c469,470
< 	signal(8, fperr);
---
> 	(void)sig;
> 	signal(8, (int)fperr);
463a472
> 	return(0);
```

### usr/src/cmd/ptx.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/ptx.c unix-v7-c99/usr/src/cmd/ptx.c || true
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
116a123
> 			/* fallthrough */
228c235
< 	while(pend=getline())
---
> 	while((pend=getline()))
236a244
> 		/* fallthrough */
247c255
< 	onintr();
---
> 	onintr(0);
250,252c258,259
< msg(s,arg)
< char *s;
< char *arg;
---
> int
> msg(char *s, char *arg)
255c262
< 	return;
---
> 	return(0);
257,258c264,265
< diag(s,arg)
< char *s, *arg;
---
> int
> diag(char *s, char *arg)
262a270
> 	return(0);
266c274
< char *getline()
---
> char *getline(void)
269c277
< 	register c;
---
> 	register int c;
291c299
< 				while(isspace(*--linep));
---
> 				while(isspace((unsigned char)*--linep));
302,303c310,311
< cmpline(pend)
< char *pend;
---
> int
> cmpline(char *pend)
312c320
< 		while(pchar<pend&&!isspace(*pchar))
---
> 		while(pchar<pend&&!isspace((unsigned char)*pchar))
316c324
< 		if(isabreak(*pchar++))
---
> 		if(isabreak((unsigned char)*pchar++))
322c330
< 			if(isabreak(*pchar)) {
---
> 			if(isabreak((unsigned char)*pchar)) {
325c333
< 				while(cp = *hp++){
---
> 				while((cp = *hp++)){
346a355
> 	return(0);
349,350c358,359
< cmpword(cpp,pend,hpp)
< char *cpp, *pend, *hpp;
---
> int
> cmpword(char *cpp, char *pend, char *hpp)
356c365
< 		if((isupper(c)?tolower(c):c) != *hpp++)
---
> 		if((isupper((unsigned char)c)?tolower(c):c) != *hpp++)
363,364c372,373
< putline(strt, end)
< char *strt, *end;
---
> int
> putline(char *strt, char *end)
376a386
> 	return(0);
379c389,390
< getsort()
---
> int
> getsort(void)
381c392
< 	register c;
---
> 	register int c;
385c396
< 	char *rtrim(), *ltrim();
---
> 	char *rtrim(char *a, char *c, int d), *ltrim(char *c, char *b, int d);
400c411
< 			while(isspace(linep[-1]))
---
> 			while(isspace((unsigned char)linep[-1]))
404c415
< 				while(ref<linep&&!isspace(*ref))
---
> 				while(ref<linep&&!isspace((unsigned char)*ref))
416c427
< 			p1b = rtrim(p1a=p3b+(isspace(p3b[0])!=0),tilde,
---
> 			p1b = rtrim(p1a=p3b+(isspace((unsigned char)p3b[0])!=0),tilde,
420c431
< 			p4a = ltrim(ref,p4b=p2a-(isspace(p2a[-1])!=0),
---
> 			p4a = ltrim(ref,p4b=p2a-(isspace((unsigned char)p2a[-1])!=0),
452a464
> 			/* fallthrough */
456a469
> 	return(0);
459,460c472
< char *rtrim(a,c,d)
< char *a,*c;
---
> char *rtrim(char *a, char *c, int d)
465c477
< 		if((x==c||isspace(x[0]))&&!isspace(x[-1]))
---
> 		if((x==c||isspace((unsigned char)x[0]))&&!isspace((unsigned char)x[-1]))
467c479
< 	if(b<c&&!isspace(b[0]))
---
> 	if(b<c&&!isspace((unsigned char)b[0]))
472,473c484
< char *ltrim(c,b,d)
< char *c,*b;
---
> char *ltrim(char *c, char *b, int d)
478c489
< 		if(!isspace(x[0])&&(x==c||isspace(x[-1])))
---
> 		if(!isspace((unsigned char)x[0])&&(x==c||isspace((unsigned char)x[-1])))
480c491
< 	if(a>c&&!isspace(a[-1]))
---
> 	if(a>c&&!isspace((unsigned char)a[-1]))
485,486c496,497
< putout(strt,end)
< char *strt, *end;
---
> int
> putout(char *strt, char *end)
494a506
> 	return(0);
497c509,510
< onintr()
---
> int
> onintr(int sig)
499a513
> 	(void)sig;
502a517
> 	return(0);
505,506c520,521
< hash(strtp,endp)
< char *strtp, *endp;
---
> int
> hash(char *strtp, char *endp)
517c532
< 	i = (isupper(c)?tolower(c):c);
---
> 	i = (isupper((unsigned char)c)?tolower(c):c);
519c534
< 	j = (isupper(c)?tolower(c):c);
---
> 	j = (isupper((unsigned char)c)?tolower(c):c);
523c538
< 	k = (isupper(c)?tolower(c):c);
---
> 	k = (isupper((unsigned char)c)?tolower(c):c);
525c540
< 	j = (isupper(c)?tolower(c):c);
---
> 	j = (isupper((unsigned char)c)?tolower(c):c);
532,534c547,548
< storeh(num,strtp)
< int num;
< char *strtp;
---
> int
> storeh(int num, char *strtp)
```

### usr/src/cmd/spline.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/spline.c unix-v7-c99/usr/src/cmd/spline.c || true
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

### usr/src/cmd/vpr.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/vpr.c unix-v7-c99/usr/src/cmd/vpr.c || true
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

### usr/src/cmd/graph.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/graph.c unix-v7-c99/usr/src/cmd/graph.c || true
```

Expect:

```
43c43,76
< double	atof();
---
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
57,58c90,91
< char *realloc();
< char *malloc();
---
> char *realloc(char *p, unsigned n);
> char *malloc(unsigned n);
60,61c93
< double ident(x)
< double x;
---
> double ident(double x)
66,67c98,148
< main(argc,argv)
< char *argv[];
---
> double
> fabs(double x)
> {
> 	return(x < 0 ? -x : x);
> }
> double
> floor(double x)
> {
> 	long n;
> 	n = x;
> 	if((double)n > x)
> 		n--;
> 	return(n);
> }
> double
> ceil(double x)
> {
> 	long n;
> 	n = x;
> 	if((double)n < x)
> 		n++;
> 	return(n);
> }
> double
> log10(double x)
> {
> 	double y, y2, term, sum;
> 	int k, i;
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
> int
> main(int argc, char *argv[])
92,93c173,174
< init(p)
< struct xy *p;
---
> int
> init(struct xy *p)
96a178
> 	return(0);
99,100c181,182
< setopt(argc,argv)
< char *argv[];
---
> int
> setopt(int argc, char *argv[])
102c184
< 	char *p1, *p2;
---
> 	char *p0, *p1, *p2;
108a191
> 		p0 = argv[0];
119c202,203
< 				while (*p1++ = *p2++);
---
> 				while ((*p1++ = *p2++))
> 					;
193c277,283
< 			badarg();
---
> 			if(p0[0] == '-')
> 				badarg();
> 			if(freopen(argv[0],"r",stdin)==NULL) {
> 				perror(argv[0]);
> 				exit(1);
> 			}
> 			break;
195a286
> 	return(0);
198,201c289,290
< limread(p, argcp, argvp)
< register struct xy *p;
< int *argcp;
< char ***argvp;
---
> int
> limread(register struct xy *p, int *argcp, char ***argvp)
209c298
< 		return;
---
> 		return(0);
212c301
< 		return;
---
> 		return(0);
215c304
< 		return;
---
> 		return(0);
216a306
> 	return(0);
219,222c309,310
< numb(np, argcp, argvp)
< int *argcp;
< float *np;
< register char ***argvp;
---
> int
> numb(float *np, int *argcp, register char ***argvp)
230c318
< 	if(!(isdigit(c) || c=='-'&&(*argvp)[1][1]<'A' || c=='.'))
---
> 	if(!(isdigit((unsigned char)c) || (c=='-' && (*argvp)[1][1]<'A') || c=='.'))
238c326,327
< readin()
---
> int
> readin(void)
240c329
< 	register t;
---
> 	register int t;
253c342
< 			return;
---
> 			return(0);
259c348
< 				return;
---
> 				return(0);
261c350
< 			return;
---
> 			return(0);
268c357
< 			return;
---
> 			return(0);
272c361,362
< transpose()
---
> int
> transpose(void)
274c364
< 	register i;
---
> 	register int i;
278c368
< 		return;
---
> 		return(0);
282a373
> 	return(0);
285c376,377
< copystring(k)
---
> int
> copystring(int k)
288c380
< 	register i;
---
> 	register int i;
302,303c394
< modceil(f,t)
< float f,t;
---
> modceil(float f, float t)
311,312c402
< modfloor(f,t)
< float f,t;
---
> modfloor(float f, float t)
318,320c408,409
< getlim(p,v)
< register struct xy *p;
< struct val *v;
---
> int
> getlim(register struct xy *p, struct val *v)
322c411
< 	register i;
---
> 	register int i;
331a421
> 	return(0);
336c426,428
< } setloglim(), setlinlim();
---
> };
> struct z setloglim(int lbf, int ubf, float lb, float ub);
> struct z setlinlim(int lbf, int ubf, float xlb, float xub);
338,339c430,431
< setlim(p)
< register struct xy *p;
---
> int
> setlim(register struct xy *p)
353c445
< 		return;
---
> 		return(0);
392c484
< 			return;
---
> 			return(0);
403a496
> 	return(0);
407,408c500
< setloglim(lbf,ubf,lb,ub)
< float lb,ub;
---
> setloglim(int lbf, int ubf, float lb, float ub)
440,442c532
< setlinlim(lbf,ubf,xlb,xub)
< int lbf,ubf;
< float xlb,xub;
---
> setlinlim(int lbf, int ubf, float xlb, float xub)
482,484c572,573
< scale(p,v)
< register struct xy *p;
< struct val *v;
---
> int
> scale(register struct xy *p, struct val *v)
494a584
> 	return(0);
497c587,588
< axes()
---
> int
> axes(void)
499c590
< 	register i;
---
> 	register int i;
503c594
< 		return;
---
> 		return(0);
527a619
> 	return(0);
530,532c622,623
< setmark(xmark,p)
< int *xmark;
< register struct xy *p;
---
> int
> setmark(int *xmark, register struct xy *p)
560,564c651,652
< submark(xmark,pxn,x,p)
< int *xmark;
< int *pxn;
< float x;
< struct xy *p;
---
> int
> submark(int *xmark, int *pxn, float x, struct xy *p)
567a656
> 	return(0);
570c659,660
< plot()
---
> int
> plot(void)
594a685
> 	return(0);
597,600c688,689
< conv(xv,p,ip)
< float xv;
< register struct xy *p;
< int *ip;
---
> int
> conv(float xv, register struct xy *p, int *ip)
610,611c699,700
< getfloat(p)
< float *p;
---
> int
> getfloat(float *p)
613c702
< 	register i;
---
> 	register int i;
619c708,709
< getstring()
---
> int
> getstring(void)
621c711
< 	register i;
---
> 	register int i;
628c718
< 		if(!isdigit(*labbuf)) {
---
> 		if(!isdigit((unsigned char)*labbuf)) {
632a723
> 		/* fallthrough */
649c740,741
< symbol(ix,iy,k)
---
> int
> symbol(int ix, int iy, int k)
661c753
< 		return(!brkf|k<0);
---
> 		return((!brkf)|(k<0));
665c757,758
< title()
---
> int
> title(void)
676a770
> 	return(0);
679,681c773,774
< axlab(c,p)
< char c;
< struct xy *p;
---
> int
> axlab(int c, struct xy *p)
686a780
> 	return(0);
689c783,784
< badarg()
---
> int
> badarg(void)
692a788,871
> 	return(0);
> }
> int
> putsi(int a)
> {
> 	putc(a, stdout);
> 	putc(a >> 8, stdout);
> 	return(0);
> }
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
> int
> erase(void)
> {
> 	putc('e', stdout);
> 	return(0);
> }
> int
> move(int xi, int yi)
> {
> 	putc('m', stdout);
> 	putsi(xi);
> 	putsi(yi);
> 	return(0);
> }
> int
> cont(int xi, int yi)
> {
> 	putc('n', stdout);
> 	putsi(xi);
> 	putsi(yi);
> 	return(0);
> }
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
> int
> point(int xi, int yi)
> {
> 	putc('p', stdout);
> 	putsi(xi);
> 	putsi(yi);
> 	return(0);
> }
> int
> label(char *s)
> {
> 	int i;
> 	putc('t', stdout);
> 	for(i=0; s[i]; i++)
> 		putc(s[i], stdout);
> 	putc('\n', stdout);
> 	return(0);
> }
> int
> linemod(char *s)
> {
> 	int i;
> 	putc('f', stdout);
> 	for(i=0; s[i]; i++)
> 		putc(s[i], stdout);
> 	putc('\n', stdout);
> 	return(0);
> }
> int
> closevt(void)
> {
> 	fflush(stdout);
> 	return(0);
```

### usr/src/cmd/backgammon.c

Local test:

```
diff unix-v7-c99/v7/usr/src/games/backgammon.c unix-v7-c99/usr/src/cmd/backgammon.c || true
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
205,219c222,223
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
---
> int
> roll(void)
221d224
< roll()
224,225c227,229
< 	die1=(rand()>>8)%6+1;
< 	die2=(rand()>>8)%6+1;
---
> 	die1=(bg_rand()>>8)%6+1;
> 	die2=(bg_rand()>>8)%6+1;
> 	return(0);
228,229c232,233
< movegen(mover,movee)
< int *mover,*movee;
---
> int
> movegen(int *mover, int *movee)
237c241
< 		if((k=25-i-die1)>0&&movee[k]>=2)
---
> 		if((k=25-i-die1)>0&&movee[k]>=2) {
239a244
> 		}
250c255
< 			if((k=25-j-die2)>0&&movee[k]>=2)
---
> 			if((k=25-j-die2)>0&&movee[k]>=2) {
252a258
> 			}
268c274
< 			    if((k=25-l-die1)>0&&movee[k]>=2)
---
> 			    if((k=25-l-die1)>0&&movee[k]>=2) {
270a277
> 			    }
281c288
< 				if((k=25-m-die1)>=0&&movee[k]>=2)
---
> 				if((k=25-m-die1)>=0&&movee[k]>=2) {
283a291
> 				}
313a322
> 	return(0);
315,316c324,325
< moverecord(mover)
< int *mover;
---
> int
> moverecord(int *mover)
326a336
> 	    /* fallthrough */
329a340
> 	    /* fallthrough */
332a344
> 	    /* fallthrough */
353a366
> 	return(0);
357,358c370,371
< strategy(player,playee)
< int *player,*playee;
---
> int
> strategy(int *player, int *playee)
391c404
< 	return(goodmoves[(rand()>>4)%n]);
---
> 	return(goodmoves[(bg_rand()>>4)%n]);
394,395c407,408
< eval(player,playee,k,prob)
< int *player,*playee,k,*prob;
---
> int
> eval(int *player, int *playee, int k, int *prob)
441c454
< 		sum=+ *p++ * n;	/*remove pieces, but just barely*/
---
> 		sum+= *p++ * n;	/*remove pieces, but just barely*/
449c462
< 	    for(p=newtry;p<q;)sum=- *p++;  /*bad to be on 1st three points*/
---
> 	    for(p=newtry;p<q;)sum-= *p++;  /*bad to be on 1st three points*/
453c466
< 	    *prob=+ n*getprob(newtry,newother,6*n-5,6*n);
---
> 	    *prob+= n*getprob(newtry,newother,6*n-5,6*n);
456c469,470
< instructions()
---
> int
> instructions(void)
482a497
> 	return(0);
485,486c500,501
< getprob(player,playee,start,finish)
< int *player,*playee,start,finish;
---
> int
> getprob(int *player, int *playee, int start, int finish)
498c513
< 		    if(playee[n]!=0)sum=+probability[k];
---
> 		    if(playee[n]!=0)sum+=probability[k];
504c519,520
< prtbrd()
---
> int
> prtbrd(void)
540a557
> 	return(0);
542,543c559,560
< numline(upcol,downcol,start,fin)
< int *upcol,*downcol,start,fin;
---
> int
> numline(int *upcol, int *downcol, int start, int fin)
549a567
> 	return(0);
551,553c569,570
< colorline(upcol,c1,downcol,c2,start,fin)
< int *upcol,*downcol,start,fin;
< char c1,c2;
---
> int
> colorline(int *upcol, int c1, int *downcol, int c2, int start, int fin)
562a580
> 	return(0);
565c583
< int rrno 0;
---
> int rrno = 0;
567,569c585,589
< srand(){
< 	rrno = _look( 0x40000 );
< 	_store( 0x40000, rrno+1 );
---
> int
> bg_srand(void){
> 	rrno = _look( (int *)0x40000 );
> 	_store( (int *)0x40000, rrno+1 );
> 	return(0);
572,574c592,595
< rand(){
< 	rrno =* 0106273;
< 	rrno =+ 020202;
---
> int
> bg_rand(void){
> 	rrno *= 0106273;
> 	rrno += 020202;
578c599,600
< _look(p) int *p; {
---
> int
> _look(int *p) {
582c604,605
< _store( p, numb ) int *p; {
---
> int
> _store(int *p, int numb) {
583a607
> 	return(0);
```

### usr/src/cmd/fish.c

Local test:

```
diff unix-v7-c99/v7/usr/src/games/fish.c unix-v7-c99/usr/src/cmd/fish.c || true
```

Expect:

```
14a15,17
> int	shuffle(), choose(), draw(), error(), empty(), mark(), deal(),
> 	stats(), phand(), instruct(), game(), move(), madebook(),
> 	score(), guess(), start(), hedrew(), heguessed(), myguess();
25c28,29
< shuffle(){
---
> int
> shuffle(void){
30c34
< 	register i;
---
> 	register int i;
38a43
> 	return(0);
41c46,47
< choose( a, n ) char a[]; {
---
> int
> choose( a, n ) char a[]; int n; {
44c50
< 	register j, t;
---
> 	register int j, t;
54c60,61
< draw() {
---
> int
> draw(void) {
58a66
> int
62a71
> 	return(0);
64a74
> int
66c76
< 	register i;
---
> 	register int i;
74c84,85
< mark( cd, hand ) HAND hand; {
---
> int
> mark( cd, hand ) int cd; HAND hand; {
84c95,96
< deal( hand, n ) HAND hand; {
---
> int
> deal( hand, n ) HAND hand; int n; {
87a100
> 	return(0);
90c103
< char *cname[] {
---
> char *cname[] = {
107,108c120,122
< stats(){
< 	register i, ct, b;
---
> int
> stats(void){
> 	register int i, ct, b;
127a142
> 	return(0);
129a145
> int
131c147
< 	register i, j;
---
> 	register int i, j;
141c157
< 			register k;
---
> 			register int k;
154a171
> 	return(0);
157c174,175
< main( argc, argv ) char * argv[]; { 
---
> int
> main( argc, argv ) int argc; char * argv[]; {
159c177
< 	register c;
---
> 	register int c;
175a194
> 	return(0);
180c199
< char *inst[] {
---
> char *inst[] = {
208c227,228
< instruct(){
---
> int
> instruct(void){
215a236
> 	return(0);
218c239,240
< game(){
---
> int
> game(void){
229c251
< 		register g;
---
> 		register int g;
256c278,279
< move( hs, ht, g, v ) HAND hs, ht; {
---
> int
> move( hs, ht, g, v ) HAND hs, ht; int g, v; {
259c282
< 	register d;
---
> 	register int d;
315c338,339
< madebook( x ){
---
> int
> madebook( x ) int x; {
316a341
> 	return(0);
319,320c344,346
< score(){
< 	register my, your, i;
---
> int
> score(void){
> 	register int my, your, i;
345a372
> 	return(0);
350c377,378
< guess(){
---
> int
> guess(void){
352c380
< 	register g, go;
---
> 	register int g, go;
431a460
> int
432a462
> 	(void)h;
433a464
> 	return(0);
436c467,468
< hedrew( d ){
---
> int
> hedrew( d ) int d; {
437a470
> 	return(0);
440c473,474
< heguessed( d ){
---
> int
> heguessed( d ) int d; {
441a476
> 	return(0);
444c479,480
< myguess(){
---
> int
> myguess(void){
446c482
< 	register i, lg, t;
---
> 	register int i, lg, t;
457c493
< 		try[ntry++] = i;
---
> 		try[(unsigned char)ntry++] = i;
465c501
< 		if( hehas[try[i]] ) {
---
> 		if( hehas[(unsigned char)try[i]] ) {
474c510
< 		if( haveguessed[try[i]] < lg ) lg = haveguessed[try[i]];
---
> 		if( haveguessed[(unsigned char)try[i]] < lg ) lg = haveguessed[(unsigned char)try[i]];
480c516
< 		if( haveguessed[try[i]] == lg ) try[t++] = try[i];
---
> 		if( haveguessed[(unsigned char)try[i]] == lg ) try[t++] = try[i];
```

### usr/src/cmd/quiz.c

Local test:

```
diff unix-v7-c99/v7/usr/src/games/quiz.c unix-v7-c99/usr/src/cmd/quiz.c || true
```

Expect:

```
9a10,16
> int	readline(void), cmp(char *u, char *v), disj(int s), string(int s);
> int	eat(int s, int c), fold(int c), publish(char *t), pub1(int s);
> int	segment(char *u, char *w[]);
> int	perm(char *u[], int m, char *v[], int n, int p[]);
> int	find(char *u[], int m), readindex(void), talloc(void);
> int	query(char *r), next(void), done(void);
> int	instruct(char *info), badinfo(void), dunno(void);
26c33
< char	*malloc();
---
> char	*malloc(unsigned n);
28c35,36
< readline()
---
> int
> readline(void)
31c39
< 	register c;
---
> 	register int c;
60,61c68,69
< cmp(u,v)
< char *u, *v;
---
> int
> cmp(char *u, char *v)
72c80,81
< disj(s)
---
> int
> disj(int s)
86c95
< 			return(t|x&s);
---
> 			return(t|(x&s));
111c120,121
< string(s)
---
> int
> string(int s)
128a139
> 			/* fallthrough */
155,156c166,167
< eat(s,c)
< char c;
---
> int
> eat(int s, int c)
171,172c182,183
< fold(c)
< char c;
---
> int
> fold(int c)
179,180c190,191
< publish(t)
< char *t;
---
> int
> publish(char *t)
183a195
> 	return(0);
186c198,199
< pub1(s)
---
> int
> pub1(int s)
196c209
< 			return;
---
> 			return(0);
204a218
> 			/* fallthrough */
212,213c226,227
< segment(u,w)
< char *u, *w[];
---
> int
> segment(char *u, char *w[])
244,246c258,259
< perm(u,m,v,n,p)
< int p[];
< char *u[], *v[];
---
> int
> perm(char *u[], int m, char *v[], int n, int p[])
265,266c278,279
< find(u,m)
< char *u[];
---
> int
> find(char *u[], int m)
277c290,291
< readindex()
---
> int
> readindex(void)
287a302
> 	return(0);
290c305,306
< talloc()
---
> int
> talloc(void)
294a311
> 	return(0);
297,298c314,315
< main(argc,argv)
< char *argv[];
---
> int
> main(int argc, char *argv[])
300c317
< 	register j;
---
> 	register int j;
306c323
< 	extern done();
---
> 	extern int done(void);
310c327
< 	inc = (int)tm&077774|01;
---
> 	inc = ((int)tm&077774)|01;
335c352
< 	signal(SIGINT, done);
---
> 	signal(SIGINT, (int)done);
385,386c402,403
< query(r)
< char *r;
---
> int
> query(char *r)
404c421,422
< next()
---
> int
> next(void)
419c437,438
< done()
---
> int
> done(void)
425a445
> 	return(0);
427,428c447,448
< instruct(info)
< char *info;
---
> int
> instruct(char *info)
462a483
> 	return(0);
465c486,487
< badinfo(){
---
> int
> badinfo(void){
466a489
> 	return(0);
469c492,493
< dunno()
---
> int
> dunno(void)
472a497
> 	return(0);
```

### usr/src/cmd/wump.c

Local test:

```
diff unix-v7-c99/v7/usr/src/games/wump.c unix-v7-c99/usr/src/cmd/wump.c || true
```

Expect:

```
0a1
> #include <stdio.h>
19c20,22
< char	*intro[]
---
> int	tunnel(int i), rline(void), rnum(int n), rin(void);
> int	near(struct room *ap, int ahaz), icomp(const void *p1, const void *p2);
> char	*intro[] =
95c98,99
< main()
---
> int
> main(void)
97c101
< 	register i, j;
---
> 	register int i, j;
99c103
< 	int k, icomp();
---
> 	int k, icomp(const void *, const void *);
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
287c292,293
< tunnel(i)
---
> int
> tunnel(int i)
290c296
< 	register n, j;
---
> 	register int n, j;
309c315,316
< rline()
---
> int
> rline(void)
317c324
< 			exit();
---
> 			exit(0);
324c331,332
< rnum(n)
---
> int
> rnum(int n)
326c334
< 	static first[2];
---
> 	static int first[2];
329c337
< 		time(first);
---
> 		time((long *)first);
335c343,344
< rin()
---
> int
> rin(void)
337c346
< 	register n, c;
---
> 	register int n, c;
345c354
< 					exit();
---
> 					exit(0);
356,357c365,366
< near(ap, ahaz)
< struct room *ap;
---
> int
> near(struct room *ap, int ahaz)
360c369
< 	register haz, i;
---
> 	register int haz, i;
370,371c379,380
< icomp(p1, p2)
< int *p1, *p2;
---
> int
> icomp(const void *p1, const void *p2)
374c383
< 	return(*p1 - *p2);
---
> 	return(*(const int *)p1 - *(const int *)p2);
```

### usr/src/cmd/dc/dc.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/dc/dc.c unix-v7-c99/usr/src/cmd/dc/dc.c || true
```

Expect:

```
4,6c4,10
< main(argc,argv)
< int argc;
< char *argv[];
---
> int init(), commnds(), readc(), unreadc(), pushp(), sdump(), chsign(),
>     subt(), eqk(), binop(), dscale(), release(), log2(), print(),
>     load(), seekc(), salterwd(), putwd(), command(), cond(),
>     more(), garbage(), ospace(), redef(), tenot(), oneot(), bigot(),
>     hexot(), onintr();
> int
> main(int argc, char *argv[])
9a14
> 	return(0);
11c16,17
< commnds(){
---
> int
> commnds(void){
62c68
< 			sunputc(p);
---
> 			(void)sunputc(p);
395c401
< 				for(n = 0;n < PTRSZ-1;n++)sputc(q,0);
---
> 				for(n = 0;n < (int)PTRSZ-1;n++)sputc(q,0);
577,578c583
< div(ddivd,ddivr)
< struct blk *ddivd,*ddivr;
---
> div(struct blk *ddivd, struct blk *ddivr)
590c595
< 		errorrt("divide by 0\n");
---
> 		{printf("divide by 0\n"); return((struct blk *)1); }
697c702,703
< dscale(){
---
> int
> dscale(void){
727,728c733
< removr(p,n)
< struct blk *p;
---
> removr(struct blk *p, int n)
756,757c761
< sqrt(p)
< struct blk *p;
---
> sqrt(struct blk *p)
807,808c811
< exp(base,ex)
< struct blk *base,*ex;
---
> exp(struct blk *base, struct blk *ex)
861,863c864,865
< init(argc,argv)
< int argc;
< char *argv[];
---
> int
> init(int argc, char *argv[])
867,868c869,870
< 	if (signal(SIGINT, SIG_IGN) != SIG_IGN)
< 		signal(SIGINT,onintr);
---
> 	if (signal(SIGINT, (int)SIG_IGN) != (int)SIG_IGN)
> 		signal(SIGINT,(int)onintr);
918c920
< 	return;
---
> 	return(0);
919a922
> int
922c925
< 	signal(SIGINT,onintr);
---
> 	signal(SIGINT,(int)onintr);
928a932
> 	return(0);
930,931c934,935
< pushp(p)
< struct blk *p;
---
> int
> pushp(struct blk *p)
935c939
< 		return;
---
> 		return(0);
939c943
< 	return;
---
> 	return(0);
942c946
< pop(){
---
> pop(void){
950c954
< readin(){
---
> readin(void){
998,1000c1002
< add0(p,ct)
< int ct;
< struct blk *p;
---
> add0(struct blk *p, int ct)
1023,1024c1025
< mult(p,q)
< struct blk *p,*q;
---
> mult(struct blk *p, struct blk *q)
1078,1079c1079,1080
< chsign(p)
< struct blk *p;
---
> int
> chsign(struct blk *p)
1110c1111
< 	return;
---
> 	return(0);
1112c1113,1114
< readc(){
---
> int
> readc(void){
1132a1135
> 	return(0);
1134,1135c1137,1138
< unreadc(c)
< char c;
---
> int
> unreadc(int c)
1142c1145
< 	return;
---
> 	return(0);
1144,1145c1147,1148
< binop(c)
< char c;
---
> int
> binop(int c)
1164c1167
< 	return;
---
> 	return(0);
1166,1167c1169,1170
< print(hptr)
< struct blk *hptr;
---
> int
> print(struct blk *hptr)
1181c1184
< 			return;
---
> 			return(0);
1188c1191
< 		return;
---
> 		return(0);
1192c1195
< 	sunputc(p);
---
> 	(void)sunputc(p);
1200c1203
< 		return;
---
> 		return(0);
1204c1207
< 		return;
---
> 		return(0);
1208c1211
< 		return;
---
> 		return(0);
1227c1230
< 		return;
---
> 		return(0);
1243c1246
< 	return;
---
> 	return(0);
1247,1248c1250
< getdec(p,sc)
< struct blk *p;
---
> getdec(struct blk *p, int sc)
1278,1279c1280,1281
< tenot(p,sc)
< struct blk *p;
---
> int
> tenot(struct blk *p, int sc)
1295c1297
< 		return;
---
> 		return(0);
1325c1327
< 	return;
---
> 	return(0);
1327,1329c1329,1330
< oneot(p,sc,ch)
< struct blk *p;
< char ch;
---
> int
> oneot(struct blk *p, int sc, int ch)
1344c1345
< 	return;
---
> 	return(0);
1346,1347c1347,1348
< hexot(p,flg)
< struct blk *p;
---
> int
> hexot(struct blk *p, int flg)
1349a1351
> 	(void)flg;
1354c1356
< 		return;
---
> 		return(0);
1360c1362
< 		return;
---
> 		return(0);
1363c1365
< 	return;
---
> 	return(0);
1365,1366c1367,1368
< bigot(p,flg)
< struct blk *p;
---
> int
> bigot(struct blk *p, int flg)
1409c1411
< 			sunputc(strptr);
---
> 			(void)sunputc(strptr);
1414c1416
< 	return;
---
> 	return(0);
1417,1418c1419
< add(a1,a2)
< struct blk *a1,*a2;
---
> add(struct blk *a1, struct blk *a2)
1463c1464,1465
< eqk(){
---
> int
> eqk(void){
1493,1494c1495
< removc(p,n)
< struct blk *p;
---
> removc(struct blk *p, int n)
1515,1516c1516
< scalint(p)
< struct blk *p;
---
> scalint(struct blk *p)
1524,1525c1524
< scale(p,n)
< struct blk *p;
---
> scale(struct blk *p, int n)
1541c1540,1541
< subt(){
---
> int
> subt(void){
1552c1552,1553
< command(){
---
> int
> command(void){
1555c1556
< 	register (*savint)(),pid,rpid;
---
> 	register int (*savint)(),pid,rpid;
1574c1575
< 		savint = signal(SIGINT, SIG_IGN);
---
> 		savint = (int (*)())signal(SIGINT, (int)SIG_IGN);
1576c1577
< 		signal(SIGINT,savint);
---
> 		signal(SIGINT,(int)savint);
1581,1582c1582,1583
< cond(c)
< char c;
---
> int
> cond(int c)
1589c1590
< 	sunputc(p);
---
> 	(void)sunputc(p);
1614,1615c1615,1616
< 	if((cc<0 && (c == '<' || c == NG)) ||
< 		(cc >0) && (c == '>' || c == NL)){
---
> 	if(((signed char)cc<0 && (c == '<' || c == NG)) ||
> 		((cc >0) && (c == '>' || c == NL))){
1622c1623,1624
< load(){
---
> int
> load(void){
1653c1655
< 	return;
---
> 	return(0);
1655,1656c1657,1658
< log2(n)
< long n;
---
> int
> log2(long n)
1668,1669c1670
< salloc(size)
< int size;
---
> salloc(int size)
1688c1689
< morehd(){
---
> morehd(void){
1713,1715c1714
< copy(hptr,size)
< struct blk *hptr;
< int size;
---
> copy(struct blk *hptr, int size)
1741,1743c1740,1741
< sdump(s1,hptr)
< char *s1;
< struct blk *hptr;
---
> int
> sdump(char *s1, struct blk *hptr)
1749a1748
> 	return(0);
1751,1752c1750,1751
< seekc(hptr,n)
< struct blk *hptr;
---
> int
> seekc(struct blk *hptr, int n)
1769c1768
< 		return;
---
> 		return(0);
1773c1772
< 	return;
---
> 	return(0);
1775,1777c1774,1775
< salterwd(hptr,n)
< struct wblk *hptr;
< struct blk *n;
---
> int
> salterwd(struct wblk *hptr, struct blk *n)
1782c1780
< 	return;
---
> 	return(0);
1784,1785c1782,1783
< more(hptr)
< struct blk *hptr;
---
> int
> more(struct blk *hptr)
1804c1802
< 	return;
---
> 	return(0);
1806,1807c1804,1805
< ospace(s)
< char *s;
---
> int
> ospace(char *s)
1813a1812
> 	return(0);
1815,1816c1814,1815
< garbage(s)
< char *s;
---
> int
> garbage(char *s)
1822a1822
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

### usr/src/cmd/dc/dc.h

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/dc/dc.h unix-v7-c99/usr/src/cmd/dc/dc.h || true
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

### usr/src/cmd/tar/tar.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/tar/tar.c unix-v7-c99/usr/src/cmd/tar/tar.c || true
```

Expect:

```
7,8d6
< char	*sprintf();
< char	*strcat();
9a8,14
> int	usage(), done(), dorep(), doxtract(), dotable(), getdir(),
> 	passtape(), endtape(), getwdir(), putfile(), putempty(),
> 	flushtape(), readtape(), writetape(), backtape(), longt(),
> 	pmode(), select(), checkdir(), onintr(), onquit(), onhup(),
> 	onterm(), tomodes(), checksum(), checkw(), response(),
> 	checkupdate(), prefix(), cmp(), copy();
> int	mkdir(char *path, int mode);
55,57c60,61
< main(argc, argv)
< int	argc;
< char	*argv[];
---
> int
> main(int argc, char *argv[])
140,145c144,149
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
195c199,200
< usage()
---
> int
> usage(void)
198a204
> 	return(0);
201,202c207,208
< dorep(argv)
< char	*argv[];
---
> int
> dorep(char *argv[])
253a260
> 	return(0);
256c263,264
< endtape()
---
> int
> endtape(void)
266c274,275
< getdir()
---
> int
> getdir(void)
273c282
< 		return;
---
> 		return(0);
289a299
> 	return(0);
292c302,303
< passtape()
---
> int
> passtape(void)
298c309
< 		return;
---
> 		return(0);
304a316
> 	return(0);
307,309c319,320
< putfile(longname, shortname)
< char *longname;
< char *shortname;
---
> int
> putfile(char *longname, char *shortname)
321c332
< 		return;
---
> 		return(0);
328c339
< 		return;
---
> 		return(0);
332c343
< 		return;
---
> 		return(0);
336c347,348
< 		for (i = 0, cp = buf; *cp++ = longname[i++];);
---
> 		for (i = 0, cp = buf; (*cp++ = longname[i++]);)
> 			;
362c374
< 		return;
---
> 		return(0);
366c378
< 		return;
---
> 		return(0);
376c388
< 		return;
---
> 		return(0);
400c412
< 			return;
---
> 			return(0);
429c441,446
< 	while ((i = read(infile, buf, TBLOCK)) > 0 && blocks > 0) {
---
> 	while (blocks > 0) {
> 		for (cp = buf; cp < &buf[TBLOCK]; )
> 			*cp++ = 0;
> 		i = read(infile, buf, TBLOCK);
> 		if (i <= 0)
> 			break;
432a450,451
> 	if (blocks == 0)
> 		i = 0;
437a457
> 	return(0);
442,443c462,463
< doxtract(argv)
< char	*argv[];
---
> int
> doxtract(char *argv[])
515a536
> 	return(0);
518c539,540
< dotable()
---
> int
> dotable(void)
531a554
> 	return(0);
534c557,558
< putempty()
---
> int
> putempty(void)
541a566
> 	return(0);
544,545c569,570
< longt(st)
< register struct stat *st;
---
> int
> longt(register struct stat *st)
554a580
> 	return(0);
581,582c607,608
< pmode(st)
< register struct stat *st;
---
> int
> pmode(register struct stat *st)
587a614
> 	return(0);
590,592c617,618
< select(pairp, st)
< int *pairp;
< struct stat *st;
---
> int
> select(int *pairp, struct stat *st)
600a627
> 	return(0);
603,604c630,631
< checkdir(name)
< register char *name;
---
> int
> checkdir(register char *name)
612,616c639,646
< 				if (fork() == 0) {
< 					execl("/bin/mkdir", "mkdir", name, 0);
< 					execl("/usr/bin/mkdir", "mkdir", name, 0);
< 					fprintf(stderr, "tar: cannot find mkdir!\n");
< 					done(0);
---
> 				if (mkdir(name, 0777) < 0) {
> 					if (fork() == 0) {
> 						execl("/bin/mkdir", "mkdir", name, 0);
> 						execl("/usr/bin/mkdir", "mkdir", name, 0);
> 						fprintf(stderr, "tar: cannot find mkdir!\n");
> 						done(0);
> 					}
> 					while (wait(&i) >= 0);
618d647
< 				while (wait(&i) >= 0);
623a653
> 	return(0);
626c656,657
< onintr()
---
> int
> onintr(int sig)
628c659,660
< 	signal(SIGINT, SIG_IGN);
---
> 	(void)sig;
> 	signal(SIGINT, (int)SIG_IGN);
629a662
> 	return(0);
632c665,666
< onquit()
---
> int
> onquit(int sig)
634c668,669
< 	signal(SIGQUIT, SIG_IGN);
---
> 	(void)sig;
> 	signal(SIGQUIT, (int)SIG_IGN);
635a671
> 	return(0);
638c674,675
< onhup()
---
> int
> onhup(int sig)
640c677,678
< 	signal(SIGHUP, SIG_IGN);
---
> 	(void)sig;
> 	signal(SIGHUP, (int)SIG_IGN);
641a680
> 	return(0);
644c683,684
< onterm()
---
> int
> onterm(int sig)
646c686,687
< 	signal(SIGTERM, SIG_IGN);
---
> 	(void)sig;
> 	signal(SIGTERM, (int)SIG_IGN);
647a689
> 	return(0);
650,651c692,693
< tomodes(sp)
< register struct stat *sp;
---
> int
> tomodes(register struct stat *sp)
661a704
> 	return(0);
664c707,708
< checksum()
---
> int
> checksum(void)
666c710
< 	register i;
---
> 	register int i;
677,678c721,722
< checkw(c, name)
< char *name;
---
> int
> checkw(int c, char *name)
693c737,738
< response()
---
> int
> response(void)
704,705c749,750
< checkupdate(arg)
< char	*arg;
---
> int
> checkupdate(char *arg)
710c755
< 	daddr_t	lookup();
---
> 	daddr_t	lookup(char *s);
725c770,771
< done(n)
---
> int
> done(int n)
728a775
> 	return(0);
731,732c778,779
< prefix(s1, s2)
< register char *s1, *s2;
---
> int
> prefix(register char *s1, register char *s2)
742,743c789,790
< getwdir(s)
< char *s;
---
> int
> getwdir(char *s)
765a813
> 	return(0);
771,772c819
< lookup(s)
< char *s;
---
> lookup(char *s)
774c821
< 	register i;
---
> 	register int i;
785,787c832
< bsrch(s, n, l, h)
< daddr_t l, h;
< char *s;
---
> bsrch(char *s, int n, daddr_t l, daddr_t h)
789c834
< 	register i, j;
---
> 	register int i, j;
830,831c875,876
< cmp(b, s, n)
< char *b, *s;
---
> int
> cmp(char *b, char *s, int n)
833c878
< 	register i;
---
> 	register int i;
846,847c891,892
< readtape(buffer)
< char *buffer;
---
> int
> readtape(char *buffer)
856c901
< 		if ((i = read(mt, tbuf, TBLOCK*j)) < 0) {
---
> 		if ((i = read(mt, (char *)tbuf, TBLOCK*j)) < 0) {
878c923
< 	copy(buffer, &tbuf[recno++]);
---
> 	copy(buffer, (char *)&tbuf[recno++]);
882,883c927,928
< writetape(buffer)
< char *buffer;
---
> int
> writetape(char *buffer)
889c934
< 		if (write(mt, tbuf, TBLOCK*nblock) < 0) {
---
> 		if (write(mt, (char *)tbuf, TBLOCK*nblock) < 0) {
895c940
< 	copy(&tbuf[recno++], buffer);
---
> 	copy((char *)&tbuf[recno++], buffer);
897c942
< 		if (write(mt, tbuf, TBLOCK*nblock) < 0) {
---
> 		if (write(mt, (char *)tbuf, TBLOCK*nblock) < 0) {
906c951,952
< backtape()
---
> int
> backtape(void)
911c957
< 		if (read(mt, tbuf, TBLOCK*nblock) < 0) {
---
> 		if (read(mt, (char *)tbuf, TBLOCK*nblock) < 0) {
916a963
> 	return(0);
919c966,967
< flushtape()
---
> int
> flushtape(void)
921c969,970
< 	write(mt, tbuf, TBLOCK*nblock);
---
> 	write(mt, (char *)tbuf, TBLOCK*nblock);
> 	return(0);
924,925c973,974
< copy(to, from)
< register char *to, *from;
---
> int
> copy(register char *to, register char *from)
927c976
< 	register i;
---
> 	register int i;
932a982
> 	return(0);
```

### usr/src/cmd/awk/awk.def

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/awk/awk.def unix-v7-c99/usr/src/cmd/awk/awk.def || true
```

Expect:

```
2c2
< #define yfree free
---
> #define yfree(p) free((char *)(p))
```

### usr/src/cmd/awk/lib.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/awk/lib.c unix-v7-c99/usr/src/cmd/awk/lib.c || true
```

Expect:

```
4a5
> int error(), fldbld(), setclvar(), member(), isnumber(), awkdigit();
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
228c243
< 	if (!isdigit(*s) && *s != '.')
---
> 	if (!awkdigit(*s) && *s != '.')
230c245
< 	if (isdigit(*s)) {
---
> 	if (awkdigit(*s)) {
234c249
< 		} while (isdigit(*s));
---
> 		} while (awkdigit(*s));
242c257
< 	if (isdigit(*s)) {
---
> 	if (awkdigit(*s)) {
246c261
< 		} while (isdigit(*s));
---
> 		} while (awkdigit(*s));
248c263
< 	if (!(d1 || point && d2))
---
> 	if (!(d1 || (point && d2)))
254c269
< 		if (!isdigit(*s))
---
> 		if (!awkdigit(*s))
259c274
< 		} while (isdigit(*s));
---
> 		} while (awkdigit(*s));
270a286,292
> }
> int
> awkdigit(int c)
> {
> 	if(c >= '0' && c <= '9')
> 		return(1);
> 	return(0);
```

### usr/src/cmd/awk/parse.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/awk/parse.c unix-v7-c99/usr/src/cmd/awk/parse.c || true
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

### usr/src/cmd/awk/proc.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/awk/proc.c unix-v7-c99/usr/src/cmd/awk/proc.c || true
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

### usr/src/cmd/awk/run.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/awk/run.c unix-v7-c99/usr/src/cmd/awk/run.c || true
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

### usr/src/cmd/awk/token.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/awk/token.c unix-v7-c99/usr/src/cmd/awk/token.c || true
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

### usr/src/cmd/awk/tran.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/awk/tran.c unix-v7-c99/usr/src/cmd/awk/tran.c || true
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

### usr/src/cmd/awk/main.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/awk/main.c unix-v7-c99/usr/src/cmd/awk/main.c || true
```

Expect:

```
3a4
> int logit(), syminit(), run(), msgfiles(), error(), yyparse();
10c11
< extern	errorflag;	/* non-zero if any syntax errors; set by yyerror */
---
> extern int	errorflag;	/* non-zero if any syntax errors; set by yyerror */
15c16,17
< main(argc, argv) int argc; char *argv[]; {
---
> int
> main(int argc, char *argv[]) {
71c73
< 		write(ansfd, &errorflag, sizeof(errorflag));
---
> 		write(ansfd, (char *)&errorflag, sizeof(errorflag));
77c79,80
< logit(n, s) char *s[];
---
> int
> logit(int n, char *s[])
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
102c106,107
< yywrap()
---
> int
> yywrap(void)
107c112,113
< msgfiles()
---
> int
> msgfiles(void)
134c140
< 	xargv=s=svargv=malloc(n*sizeof(char *));
---
> 	xargv=s=svargv=(char **)malloc(n*sizeof(char *));
139a146
> 	return(0);
```

### usr/src/cmd/tp/tp1.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/tp/tp1.c unix-v7-c99/usr/src/cmd/tp/tp1.c || true
```

Expect:

```
1a2
> #include <stdio.h>
3,4c4,9
< main(argc,argv)
< char **argv;
---
> int	optap(), setcom(), useerr(), check(), done(), encode(),
> 	decode(), cmd(), cmr(), cmt(), cmx(),
> 	clrdir(), clrent(), rddir(), gettape(), wrdir(), getfiles(),
> 	update(), delete(), taboc(), extract(), usage();
> int
> main(int argc, char **argv)
7c12,13
< 	extern cmd(), cmr(),cmx(), cmt();
---
> 	extern int cmd(), cmr(),cmx(), cmt();
> 	(void)argc;
15c21
< 		while (c = *ptr++) switch(c)  {
---
> 		while ((c = *ptr++)) switch(c)  {
62a69
> 	return(0);
65c72,73
< optap()
---
> int
> optap(void)
67c75
< 	extern cmr();
---
> 	extern int cmr();
86a95
> 	return(0);
89,90c98,99
< setcom(newcom)
< int (*newcom)();
---
> int
> setcom(int (*newcom)(void))
92c101
< 	extern cmr();
---
> 	extern int cmr();
95a105
> 	return(0);
98c108,109
< useerr()
---
> int
> useerr(void)
101a113
> 	return(0);
104c116
< /*/* COMMANDS */
---
> /* COMMANDS */
106c118,119
< cmd()
---
> int
> cmd(void)
108c121
< 	extern delete();
---
> 	extern int delete(void);
115a129
> 	return(0);
118c132,133
< cmr()
---
> int
> cmr(void)
124a140
> 	return(0);
127c143,144
< cmt()
---
> int
> cmt(void)
129c146
< 	extern taboc();
---
> 	extern int taboc(struct dent *);
136a154
> 	return(0);
139c157,158
< cmx()
---
> int
> cmx(void)
141c160
< 	extern extract();
---
> 	extern int extract(struct dent *);
146a166
> 	return(0);
148a169
> int
152a174
> 	return(0);
154a177
> int
158a182
> 	return(0);
160a185
> int
168c193
< 	register n;
---
> 	register int n;
185a211
> 	return(0);
187a214
> int
194a222
> 	return(0);
```

### usr/src/cmd/tp/tp2.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/tp/tp2.c unix-v7-c99/usr/src/cmd/tp/tp2.c || true
```

Expect:

```
6a7,9
> int	rseek(), wseek(), tread(), twrite(), seekerr(), swabdir(),
> 	encode(), decode(), done(), bitmap(), fserr(), callout(),
> 	expand(), clrent();
10c13,14
< clrdir()
---
> int
> clrdir(void)
12c16
< 	register j, *p;
---
> 	register int j, *p;
17a22
> 	return(0);
20,21c25,26
< clrent(ptr)
< struct	dent *ptr;
---
> int
> clrent(struct dent *ptr)
23c28
< 	register *p, j;
---
> 	register int *p, j;
32c37
< 			return;
---
> 			return(0);
34a40
> 	return(0);
38c44,45
< rddir()
---
> int
> rddir(void)
68c75
< 		for(i=0;i<sizeof(struct tent)/sizeof(short);i++)
---
> 		for(i=0;i<(int)(sizeof(struct tent)/sizeof(short));i++)
92c99
< 	if(sum != 0)
---
> 	if(sum != 0) {
100c107
< 			return;
---
> 			return(0);
101a109
> 	}
102a111
> 	return(0);
106c115,116
< wrdir()
---
> int
> wrdir(void)
130c140
< 		if (count == 0)  return;
---
> 		if (count == 0)  return(0);
149c159
< 				for(i=0;i<sizeof(struct tent)/sizeof(short)-1;i++)
---
> 				for(i=0;i<(int)(sizeof(struct tent)/sizeof(short))-1;i++)
156c166
< 				for(i=0;i<sizeof(struct tent)/sizeof(short);i++)
---
> 				for(i=0;i<(int)(sizeof(struct tent)/sizeof(short));i++)
164c174,175
< tread()
---
> int
> tread(void)
166c177
< 	register j, *ptr;
---
> 	register int j, *ptr;
175a187
> 	return(0);
178c190,191
< twrite()
---
> int
> twrite(void)
184a198
> 	return(0);
187c201,202
< rseek(blk)
---
> int
> rseek(int blk)
190a206
> 	return(0);
193c209,210
< wseek(blk)
---
> int
> wseek(int blk)
195c212
< 	register amt, b;
---
> 	register int amt, b;
204a222
> 	return(0);
207c225,226
< seekerr()
---
> int
> seekerr(void)
210a230
> 	return(0);
213c233,234
< verify(key)
---
> int
> verify(int key)
215c236
< 	register c;
---
> 	register int c;
235c256,257
< getfiles()
---
> int
> getfiles(void)
244a267
> 	return(0);
248c271,272
< expand()
---
> int
> expand(void)
258c282
< 				return;
---
> 				return(0);
276a301
> int
280a306
> 	return(0);
282a309
> int
295c322
< 		if(mode != S_IFREG) return;
---
> 		if(mode != S_IFREG) return(0);
316c343
< 				return;
---
> 				return(0);
318c345
< 		if (verify('r') < 0)	return;
---
> 		if (verify('r') < 0)	return(0);
330c357
< 	if (verify('a') < 0)		return;
---
> 	if (verify('a') < 0)		return(0);
338a366
> 	return(0);
341,342c369,370
< swabdir(tp)
< register struct tent *tp;
---
> int
> swabdir(register struct tent *tp)
346a375
> 	return(0);
```

### usr/src/cmd/mkfs.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/mkfs.c unix-v7-c99/usr/src/cmd/mkfs.c || true
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
20a25,32
> int ltol3(cp, lp, n) char *cp; long *lp; int n; {
> 	int i; long v;
> 	for(i=0; i<n; i++) {
> 		v = lp[i];
> 		*cp++ = v; *cp++ = v >> 8; *cp++ = v >> 16;
> 	}
> 	return(0);
> }
31c43
< union {
---
> union fbuf_u {
34,37c46,47
< } fbuf;
< #ifndef STANDALONE
< struct exec head;
< #endif
---
> } fbuf_storage;
> #define fbuf fbuf_storage.fb
39c49
< union {
---
> union filsys_u {
42c52,53
< } filsys;
---
> } filsys_storage;
> #define filsys filsys_storage.fs
49,50c60,74
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
52,53c76,77
< main(argc, argv)
< char *argv[];
---
> int
> main(int argc, char *argv[])
59c83,86
< 	time(&utime);
---
> 	if ((fsys = getenv("V7_MKFS_TIME")) != NULL)
> 		utime = atol(fsys);
> 	else
> 		time(&utime);
103c130
< 		for(f=0; c=proto[f]; f++) {
---
> 		for(f=0; (c=proto[f]); f++) {
114c141
< 		if(n > 65500/NIPB)
---
> 		if((unsigned long)n > 65500/NIPB)
117c144
< 		printf("isize = %D\n", n*NIPB);
---
> 		printf("isize = %ld\n", n*NIPB);
125d151
< 	 * and read onto block 0
130,145c156,158
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
---
> 	if(f < 0)
> 		printf("%s: cannot open init\n", string);
> 	else
147d159
< f1:
155d166
< f2:
175c186
< 		printf("%ld/%ld: bad ratio\n", filsys.s_fsize, filsys.s_isize-2);
---
> 		printf("%ld/%d: bad ratio\n", filsys.s_fsize, filsys.s_isize-2);
197,198c208,209
< cfile(par)
< struct inode *par;
---
> void
> cfile(struct inode *par)
203c214
< 	daddr_t ib[NINDIR];
---
> 	daddr_t ib[MAXFILEBLK];
235c246
< 	for(i=0; i<NINDIR; i++)
---
> 	for(i=0; (unsigned)i<MAXFILEBLK; i++)
309,310c320,321
< gmode(c, s, m0, m1, m2, m3)
< char c, *s;
---
> int
> gmode(int c, char *s, int m0, int m1, int m2, int m3)
312a324
> 	int m[4] = {m0, m1, m2, m3};
316c328
< 			return((&m0)[i]);
---
> 			return(m[i]);
323c335
< getnum()
---
> getnum(void)
331c343
< 	for(i=0; c=string[i]; i++) {
---
> 	for(i=0; (c=string[i]) != 0; i++) {
342c354,355
< getstr()
---
> void
> getstr(void)
372,374c385,386
< rdfs(bno, bf)
< daddr_t bno;
< char *bf;
---
> void
> rdfs(daddr_t bno, char *bf)
386,388c398,399
< wtfs(bno, bf)
< daddr_t bno;
< char *bf;
---
> void
> wtfs(daddr_t bno, char *bf)
395c406
< 		printf("write error: %D\n", bno);
---
> 		printf("write error: %ld\n", bno);
401c412
< alloc()
---
> alloc(void)
421,422c432,433
< bfree(bno)
< daddr_t bno;
---
> void
> bfree(daddr_t bno)
437,442c448,449
< entry(inum, str, adbc, db, aibc, ib)
< ino_t inum;
< char *str;
< int *adbc, *aibc;
< char *db;
< daddr_t *ib;
---
> void
> entry(ino_t inum, char *str, int *adbc, char *db, int *aibc, daddr_t *ib)
456c463
< 	if(*adbc >= NDIRECT)
---
> 	if((unsigned)*adbc >= NDIRECT)
460,463c467,468
< newblk(adbc, db, aibc, ib)
< int *adbc, *aibc;
< char *db;
< daddr_t *ib;
---
> void
> newblk(int *adbc, char *db, int *aibc, daddr_t *ib)
467a473,477
> 	if((unsigned)*aibc >= MAXFILEBLK) {
> 		printf("indirect block full\n");
> 		error = 1;
> 		return;
> 	}
475,479d484
< 	if(*aibc >= NINDIR) {
< 		printf("indirect block full\n");
< 		error = 1;
< 		*aibc = 0;
< 	}
482c487,488
< getch()
---
> int
> getch(void)
494c500,501
< bflist()
---
> void
> bflist(void)
525c532
< 	for(i=0; i<NINDIR; i++)
---
> 	for(i=0; (unsigned)i<NINDIR; i++)
535c542
< 		if(f < filsys.s_fsize && f >= filsys.s_isize)
---
> 		if(f < filsys.s_fsize && f >= filsys.s_isize) {
537c544
< 				if(ibc >= NINDIR) {
---
> 				if((unsigned)ibc >= NINDIR) {
545a553
> 		}
550,553c558,559
< iput(ip, aibc, ib)
< struct inode *ip;
< int *aibc;
< daddr_t *ib;
---
> void
> iput(struct inode *ip, int *aibc, daddr_t *ib)
556,557c562,563
< 	daddr_t d;
< 	int i;
---
> 	daddr_t d, single[NINDIR], dbl[NINDIR];
> 	int i, j, k, n;
584,587c590,592
< 		for(i=0; i<*aibc; i++) {
< 			if(i >= LADDR)
< 				break;
< 			ip->i_un.i_addr[i] = ib[i];
---
> 		for(i=0; (unsigned)i<NINDIR; i++) {
> 			single[i] = (daddr_t)0;
> 			dbl[i] = (daddr_t)0;
589c594,601
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
591,593c603,622
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
> 			}
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
595c624
< 			wtfs(ip->i_un.i_addr[LADDR], (char *)ib);
---
> 			wtfs(ip->i_un.i_addr[LADDR+1], (char *)dbl);
596a626
> 		/* fall through */
610,611c640,641
< badblk(bno)
< daddr_t bno;
---
> int
> badblk(daddr_t bno)
613a644
> 	(void)bno;
```

### usr/src/cmd/arcv.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/arcv.c unix-v7-c99/usr/src/cmd/arcv.c || true
```

Expect:

```
5a6
> #include <stdio.h>
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
21d19
< char	*mktemp();
23a22
> static void conv(char *fil);
26c25
< 	int	magic;
---
> 	char	magic[2];
29,30c28,29
< main(argc, argv)
< char *argv[];
---
> int
> main(int argc, char **argv)
32c31,32
< 	register i;
---
> 	int i;
> 	char tbuf[] = "/tmp/arcXXXXX";
34c34
< 	tmp = mktemp("/tmp/arcXXXXX");
---
> 	tmp = mktemp(tbuf);
39a40,75
> 	return 0;
> }
> static unsigned short
> getshort(char *p)
> {
> 	return ((unsigned short)(unsigned char)p[0]) |
> 	    ((unsigned short)(unsigned char)p[1] << 8);
> }
> static void
> putshort(char *p, unsigned short v)
> {
> 	p[0] = v & 0377;
> 	p[1] = (v >> 8) & 0377;
> }
> static void
> putlong(char *p, char *v)
> {
> 	p[0] = v[0];
> 	p[1] = v[1];
> 	p[2] = v[2];
> 	p[3] = v[3];
> }
> static void
> putarhdr(char *p, struct oar_hdr *oh)
> {
> 	int i;
> 	for(i=0; i<8; i++)
> 		p[i] = oh->oname[i];
> 	for(; i<14; i++)
> 		p[i] = 0;
> 	putlong(&p[14], oh->odate);
> 	p[18] = oh->ouid;
> 	p[19] = 1;
> 	putshort(&p[20], 0666);
> 	putshort(&p[22], getshort(oh->osize));
> 	putshort(&p[24], 0);
42,43c78,79
< conv(fil)
< char *fil;
---
> static void
> conv(char *fil)
45c81,83
< 	register unsigned i, n;
---
> 	unsigned int i, n;
> 	struct oar_hdr oh;
> 	char nh[26];
59,61c97,100
< 	b.magic = 0;
< 	read(f, (char *)&b.magic, sizeof(b.magic));
< 	if(b.magic != omag) {
---
> 	b.magic[0] = 0;
> 	b.magic[1] = 0;
> 	read(f, b.magic, sizeof(b.magic));
> 	if(getshort(b.magic) != omag) {
67,68c106,107
< 	b.magic = ARMAG;
< 	write(tf, (char *)&b.magic, sizeof(b.magic));
---
> 	putshort(b.magic, ARMAG);
> 	write(tf, b.magic, sizeof(b.magic));
73,81c112,114
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
```

### usr/src/cmd/awk/awk.g.y

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/awk/awk.g.y unix-v7-c99/usr/src/cmd/awk/awk.g.y || true
```

Expect:

```
0a1
> %define api.value.type {long}
33a35,51
> int	yylex(void);
> void	yyerror(char *s);
> int	startreg(void);
> long	stat3();
> long	stat2();
> long	stat4();
> long	op1();
> long	op2();
> long	op3();
> long	valtonode();
> long	makedfa();
> long	genprint(void);
> long	pa2stat();
> long	linkum();
> long	exptostat();
> long	genjump(int a);
> char	*cclenter();
41c59
< 	  begin pa_stats end	{ if (errorflag==0) winner = stat3(PROGRAM, $1, $2, $3); }
---
> 	  begin pa_stats end	{ if (errorflag==0) winner = (node *)stat3(PROGRAM, $1, $2, $3); }
48c66
< 	| 	{ PUTS("empty XBEGIN"); $$ = nullstat; }
---
> 	| 	{ PUTS("empty XBEGIN"); $$ = (long)nullstat; }
54c72
< 	|	{ PUTS("empty END"); $$ = nullstat; }
---
> 	|	{ PUTS("empty END"); $$ = (long)nullstat; }
116c134
< 			{ PUTS("substr(e,e,e)"); $$ = op3(SUBSTR, $3, $5, nullstat); }
---
> 			{ PUTS("substr(e,e,e)"); $$ = op3(SUBSTR, $3, $5, (long)nullstat); }
120c138
< 			{ PUTS("split(e,e,e)"); $$ = op3(SPLIT, $3, $5, nullstat); }
---
> 			{ PUTS("split(e,e,e)"); $$ = op3(SPLIT, $3, $5, (long)nullstat); }
154c172
< 	| '{' stat_list '}'	{ PUTS("null pattern {...}"); $$ = stat2(PASTAT, nullstat, $2); }
---
> 	| '{' stat_list '}'	{ PUTS("null pattern {...}"); $$ = stat2(PASTAT, (long)nullstat, $2); }
159c177
< 	|	{ PUTS("null pa_stat"); $$ = nullstat; }
---
> 	|	{ PUTS("null pa_stat"); $$ = (long)nullstat; }
166a185,187
> 	| expr	{ PUTS("expr");
> 		$$ = op2(NE, $1, valtonode(lookup("0", symtab), CCON));
> 		}
175d195
< 	|		{ PUTS("null print_list"); $$ = valtonode(lookup("$record", symtab), CFLD); }
227c247
< 		{ PUTS("print list"); $$ = stat3($1, $2, nullstat, nullstat); }
---
> 		{ PUTS("print list"); $$ = stat3($1, $2, (long)nullstat, (long)nullstat); }
231c251
< 		{ PUTS("printf list"); $$ = stat3($1, $2, nullstat, nullstat); }
---
> 		{ PUTS("printf list"); $$ = stat3($1, $2, (long)nullstat, (long)nullstat); }
233c253
< 	|		{ PUTS("null simple statement"); $$ = nullstat; }
---
> 	|		{ PUTS("null simple statement"); $$ = (long)nullstat; }
239c259
< 	| if statement		{ PUTS("if stat"); $$ = stat3(IF, $1, $2, nullstat); }
---
> 	| if statement		{ PUTS("if stat"); $$ = stat3(IF, $1, $2, (long)nullstat); }
253c273
< 	|			{ PUTS("null stat list"); $$ = nullstat; }
---
> 	|			{ PUTS("null stat list"); $$ = (long)nullstat; }
264c284
< 		{ PUTS("for(e;e;e)"); $$ = stat4(FOR, $3, nullstat, $6, $9); }
---
> 		{ PUTS("for(e;e;e)"); $$ = stat4(FOR, $3, (long)nullstat, $6, $9); }
```

### usr/src/cmd/deroff.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/deroff.c unix-v7-c99/usr/src/cmd/deroff.c || true
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
55,57c70,71
< main(ac, av)
< int ac;
< char **av;
---
> int
> main(int ac, char **av)
62d75
< FILE *opn();
107c120,121
< skeqn()
---
> int
> skeqn(void)
109c123
< while((c = getc(infile)) != rdelim)
---
> while((c = getc(infile)) != rdelim) {
112,113c126,127
< 	else if(c == '"')
< 		while( (c = getc(infile)) != '"')
---
> 	else if(c == '"') {
> 		while( (c = getc(infile)) != '"') {
116c130
< 			else if(c == '\\')
---
> 			else if(c == '\\') {
118a133,136
> 			}
> 		}
> 	}
> }
123,124c141,142
< FILE *opn(p)
< register char *p;
---
> FILE *
> opn(register char *p)
138c156,157
< eof()
---
> int
> eof(void)
158c177,178
< getfname()
---
> void
> getfname(void)
164d183
< char *copys();
192,193c211,212
< fatal(s,p)
< char *s, *p;
---
> void
> fatal(char *s, char *p)
200c219,220
< work()
---
> void
> work(void)
215,216c235,236
< regline(macline)
< int macline;
---
> void
> regline(int macline)
242c262
< if(line[0] != '\0')
---
> if(line[0] != '\0') {
249a270
> }
254,255c275,276
< putmac(s)
< register char *s;
---
> void
> putmac(register char *s)
265c286
< 	if(t>s+2 && chars[ s[0] ]==LETTER && chars[ s[1] ]==LETTER)
---
> 	if(t>s+2 && chars[(unsigned char)s[0]]==LETTER && chars[(unsigned char)s[1]]==LETTER)
276,277c297,298
< putwords(macline)	/* break into words for -w option */
< int macline;
---
> void
> putwords(int macline)	/* break into words for -w option */
286c307
< 	while( chars[*p1] < DIGIT)
---
> 	while( chars[(unsigned char)*p1] < DIGIT)
289c310
< 	for(p = p1 ; (i=chars[*p]) != SPECIAL ; ++p)
---
> 	for(p = p1 ; (i=chars[(unsigned char)*p]) != SPECIAL ; ++p)
293c314
< 	   || (macline && nlet>2 && chars[ p1[0] ]==LETTER && chars[ p1[1] ]==LETTER) )
---
> 	   || (macline && nlet>2 && chars[(unsigned char)p1[0]]==LETTER && chars[(unsigned char)p1[1]]==LETTER) )
308c329,330
< comline()
---
> void
> comline(void)
363c385,386
< macro()
---
> void
> macro(void)
367c390
< 	while(C!='.' || C!='.' || C=='.');	/* look for  .. */
---
> 	while(C!='.' || C!='.' || C=='.');	look for  .. */
375c398,399
< tbl()
---
> void
> tbl(void)
382c406,407
< eqn()
---
> void
> eqn(void)
425c450,451
< backsl()	/* skip over a complete backslash construction */
---
> void
> backsl(void)	/* skip over a complete backslash construction */
449a476
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

### usr/src/cmd/egrep.y

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/egrep.y unix-v7-c99/usr/src/cmd/egrep.y || true
```

Expect:

```
26c26
< int line 1;
---
> int line = 1;
35c35
< int nxtchar 0;
---
> int nxtchar = 0;
58c58,75
< int	fname;
---
> char	*fname;
> int	yylex(void);
> int	yyerror(char *s);
> int	nextch(void);
> void	synerror(void);
> int	enter(int x);
> int	cclenter(int x);
> int	node(int x, int l, int r);
> int	unary(int x, int d);
> void	overflo(void);
> void	cfoll(int v);
> void	cgotofn(void);
> int	cstate(int v);
> int	member(int symb, int set, int torf);
> int	notin(int n);
> void	add(int *array, int n);
> void	follow(int v);
> void	execute(char *file);
63c80
< 		={ unary(FINAL, $1);
---
> 		{ unary(FINAL, $1);
68c85
< 		={ $$ = node(CAT, $1, $2); }
---
> 		{ $$ = node(CAT, $1, $2); }
70c87
< 		={ $$ = node(CAT, $2, $3); }
---
> 		{ $$ = node(CAT, $2, $3); }
72c89
< 		={ $$ = node(CAT, $2, $3); }
---
> 		{ $$ = node(CAT, $2, $3); }
74c91
< 		={ $$ = node(CAT, $1, $2); }
---
> 		{ $$ = node(CAT, $1, $2); }
77c94
< 		={ $$ = enter(DOT);
---
> 		{ $$ = enter(DOT);
81c98
< 		={ $$ = enter($1); }
---
> 		{ $$ = enter($1); }
83c100
< 		={ $$ = enter(DOT); }
---
> 		{ $$ = enter(DOT); }
85c102
< 		={ $$ = cclenter(CCL); }
---
> 		{ $$ = cclenter(CCL); }
87c104
< 		={ $$ = cclenter(NCCL); }
---
> 		{ $$ = cclenter(NCCL); }
91c108
< 		={ $$ = node(OR, $1, $3); }
---
> 		{ $$ = node(OR, $1, $3); }
93c110
< 		={ $$ = node(CAT, $1, $2); }
---
> 		{ $$ = node(CAT, $1, $2); }
95c112
< 		={ $$ = unary(STAR, $1); }
---
> 		{ $$ = unary(STAR, $1); }
97c114
< 		={ $$ = unary(PLUS, $1); }
---
> 		{ $$ = unary(PLUS, $1); }
99c116
< 		={ $$ = unary(QUEST, $1); }
---
> 		{ $$ = unary(QUEST, $1); }
101c118
< 		={ $$ = $2; }
---
> 		{ $$ = $2; }
106c123,124
< yyerror(s) {
---
> int
> yyerror(char *s) {
108a127
> 	return(0);
111c130,131
< yylex() {
---
> int
> yylex(void) {
114c134
< 	register char c, d;
---
> 	register int c, d;
156a177,178
> 			yylval = c;
> 			return (CHAR);
161,162c183,185
< nextch() {
< 	register char c;
---
> int
> nextch(void) {
> 	register int c;
170c193,194
< synerror() {
---
> void
> synerror(void) {
175c199,200
< enter(x) int x; {
---
> int
> enter(int x) {
183,184c208,210
< cclenter(x) int x; {
< 	register linno;
---
> int
> cclenter(int x) {
> 	register int linno;
190c216,217
< node(x, l, r) {
---
> int
> node(int x, int l, int r) {
200c227,228
< unary(x, d) {
---
> int
> unary(int x, int d) {
208c236,237
< overflo() {
---
> void
> overflo(void) {
213,214c242,244
< cfoll(v) {
< 	register i;
---
> void
> cfoll(int v) {
> 	register int i;
227,228c257,259
< cgotofn() {
< 	register c, i, k;
---
> void
> cgotofn(void) {
> 	register int c, i, k;
265c296
< 					for (k=0; k<nc; k++) symbol[chars[pc++]] = 1;
---
> 					for (k=0; k<nc; k++) symbol[(unsigned char)chars[pc++]] = 1;
321,322c352,354
< cstate(v) {
< 	register b;
---
> int
> cstate(int v) {
> 	register int b;
347,348c379,381
< member(symb, set, torf) {
< 	register i, num, pos;
---
> int
> member(int symb, int set, int torf) {
> 	register int i, num, pos;
356,357c389,391
< notin(n) {
< 	register i, j, pos;
---
> int
> notin(int n) {
> 	register int i, j, pos;
371,372c405,407
< add(array, n) int *array; {
< 	register i;
---
> void
> add(int *array, int n) {
> 	register int i;
383c418,419
< follow(v) int v; {
---
> void
> follow(int v) {
414,415c450,451
< main(argc, argv)
< char **argv;
---
> int
> main(int argc, char **argv)
490,491c526,527
< execute(file)
< char *file;
---
> void
> execute(char *file)
494,495c530,531
< 	register cstat;
< 	register ccount;
---
> 	register int cstat;
> 	register int ccount;
```

### usr/src/cmd/expr.y

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/expr.y unix-v7-c99/usr/src/cmd/expr.y || true
```

Expect:

```
2a3
> %define api.value.type {char *}
15a17,36
> %{
> #include <stdio.h>
> #define index expr_index
> long	atol();
> int	yylex(void);
> int	yyerror(char *s);
> char	*rel(int op, char *r1, char *r2);
> char	*arith(int op, char *r1, char *r2);
> char	*conj(int op, char *r1, char *r2);
> char	*substr(char *v, char *s, char *w);
> char	*length(char *s);
> char	*index(char *s, char *t);
> char	*match(char *s, char *p);
> int	ematch(char *s, char *p);
> void	errxx(int c);
> char	*compile(char *instring, char *ep, char *endbuf, int seof);
> int	advance(char *lp, char *ep);
> int	getrnge(char *str);
> int	ecmp(char *a, char *b, int count);
> %}
20c41
< expression:	expr NOARG = {
---
> expression:	expr NOARG {
27,45c48,66
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
---
> expr:	'(' expr ')' { $$ = $2; }
> 	| expr OR expr   { $$ = conj(OR, $1, $3); }
> 	| expr AND expr   { $$ = conj(AND, $1, $3); }
> 	| expr EQ expr   { $$ = rel(EQ, $1, $3); }
> 	| expr GT expr   { $$ = rel(GT, $1, $3); }
> 	| expr GEQ expr   { $$ = rel(GEQ, $1, $3); }
> 	| expr LT expr   { $$ = rel(LT, $1, $3); }
> 	| expr LEQ expr   { $$ = rel(LEQ, $1, $3); }
> 	| expr NEQ expr   { $$ = rel(NEQ, $1, $3); }
> 	| expr ADD expr   { $$ = arith(ADD, $1, $3); }
> 	| expr SUBT expr   { $$ = arith(SUBT, $1, $3); }
> 	| expr MULT expr   { $$ = arith(MULT, $1, $3); }
> 	| expr DIV expr   { $$ = arith(DIV, $1, $3); }
> 	| expr REM expr   { $$ = arith(REM, $1, $3); }
> 	| expr MCH expr	 { $$ = match($1, $3); }
> 	| MATCH expr expr { $$ = match($2, $3); }
> 	| SUBSTR expr expr expr { $$ = substr($2, $3, $4); }
> 	| LENGTH expr       { $$ = length($2); }
> 	| INDEX expr expr { $$ = index($2, $3); }
50d70
< #include <stdio.h>
54d73
< long atol();
63c82,83
< main(argc, argv) char **argv; {
---
> int
> main(int argc, char **argv) {
67a88
> 	return(0);
76c97,98
< yylex() {
---
> int
> yylex(void) {
78c100
< 	register i;
---
> 	register int i;
86,87c108,109
< 	for(i = 0; *operator[i]; ++i)
< 		if(EQL(operator[i], p))
---
> 	for(i = 0; *operators[i]; ++i)
> 		if(EQL(operators[i], p))
94,95c116,118
< char *rel(op, r1, r2) register char *r1, *r2; {
< 	register i;
---
> char *
> rel(int op, register char *r1, register char *r2) {
> 	register int i;
112c135,136
< char *arith(op, r1, r2) char *r1, *r2; {
---
> char *
> arith(int op, char *r1, char *r2) {
129c153
< 	sprintf(rv, "%D", i1);
---
> 	sprintf(rv, "%ld", i1);
132c156,157
< char *conj(op, r1, r2) char *r1, *r2; {
---
> char *
> conj(int op, char *r1, char *r2) {
162,163c187,189
< char *substr(v, s, w) char *v, *s, *w; {
< register si, wi;
---
> char *
> substr(char *v, char *s, char *w) {
> register int si, wi;
178,179c204,206
< char *length(s) register char *s; {
< 	register i = 0;
---
> char *
> length(register char *s) {
> 	register int i = 0;
189,190c216,218
< char *index(s, t) char *s, *t; {
< 	register i, j;
---
> char *
> index(char *s, char *t) {
> 	register int i, j;
202c230,231
< char *match(s, p)
---
> char *
> match(char *s, char *p)
218,219c247,248
< #define RETURN(c)	return
< #define ERROR(c)	errxx(c)
---
> #define RETURN(c)	return(c)
> #define ERROR(c)	do { errxx(c); return(0); } while (0)
222,224c251,252
< ematch(s, p)
< char *s;
< register char *p;
---
> int
> ematch(char *s, register char *p)
227,228c255
< 	char *compile();
< 	register num;
---
> 	register int num;
246c273,274
< errxx(c)
---
> void
> errxx(int c)
247a276
> 	(void)c;
290,292c319
< compile(instring, ep, endbuf, seof)
< register char *ep;
< char *instring, *endbuf;
---
> compile(char *instring, register char *ep, char *endbuf, int seof)
295,296c322,323
< 	register c;
< 	register eof = seof;
---
> 	register int c;
> 	register int eof = seof;
457c484
< 			/* Drop through to default to use \ to turn off special chars */
---
> 			/* fallthrough */
468,469c495,496
< step(p1, p2)
< register char *p1, *p2;
---
> int
> step(register char *p1, register char *p2)
471c498
< 	register c;
---
> 	register int c;
500,501c527,528
< advance(lp, ep)
< register char *lp, *ep;
---
> int
> advance(register char *lp, register char *ep)
504c531
< 	char c;
---
> 	int c;
537c564
< 		braslist[*ep++] = lp;
---
> 		braslist[(unsigned char)*ep++] = lp;
541c568
< 		braelist[*ep++] = lp;
---
> 		braelist[(unsigned char)*ep++] = lp;
592,593c619,620
< 		bbeg = braslist[*ep];
< 		ct = braelist[*ep++] - bbeg;
---
> 		bbeg = braslist[(unsigned char)*ep];
> 		ct = braelist[(unsigned char)*ep++] - bbeg;
602,603c629,630
< 		bbeg = braslist[*ep];
< 		ct = braelist[*ep++] - bbeg;
---
> 		bbeg = braslist[(unsigned char)*ep];
> 		ct = braelist[(unsigned char)*ep++] - bbeg;
646,647c673,674
< getrnge(str)
< register char *str;
---
> int
> getrnge(register char *str)
650a678
> 	return(0);
653,655c681,682
< ecmp(a, b, count)
< register char	*a, *b;
< register	count;
---
> int
> ecmp(register char *a, register char *b, register int count)
664c691,692
< yyerror(s)
---
> int
> yyerror(char *s)
668a697
> 	return(0);
```

### usr/include/a.out.h

Local test:

```
diff unix-v7-c99/v7/usr/include/a.out.h unix-v7-c99/usr/include/a.out.h || true
```

Expect:

```
33a34
> int	nlist(char *, struct nlist *);
```

### usr/include/math.h

Local test:

```
diff unix-v7-c99/v7/usr/include/math.h unix-v7-c99/usr/include/math.h || true
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

### usr/include/stdio.h

Local test:

```
diff unix-v7-c99/v7/usr/include/stdio.h unix-v7-c99/usr/include/stdio.h || true
```

Expect:

```
0a1,3
> #ifndef STDIO_H
> #define STDIO_H
> struct stat;
21a25
> #ifndef NULL
22a27
> #endif
37,41c42,160
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
> #define	O_RDONLY	0
> int syscall3(int n, int a, int b, int c);
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
> int dup();
> int pipe(int *fd);
> int getuid(void);
> int setuid(int uid);
> int getgid(void);
> int setgid(int gid);
> int getpid(void);
> int umask(int n);
> int sync(void);
> int kill(int pid, int sig);
> int signal();
> int alarm(int n);
> int pause(void);
> int nice(int incr);
> int gtty(int fd, void *buf);
> int stty(int fd, void *buf);
> int ioctl(int fd, int cmd, char *arg);
> int mount(char *special, char *dir, int ro);
> int umount(char *special);
> struct tm;
> struct timeb;
> int time(long *t);
> int stime(long *t);
> int times();
> int ftime(struct timeb *t);
> struct tm *gmtime(long *t);
> struct tm *localtime(long *t);
> char *asctime(struct tm *t);
> char *ctime(long *t);
> int dysize(int y);
> int fclose(FILE *f);
> int fseek(FILE *f, long off, int whence);
> void rewind(FILE *f);
> void setbuf(FILE *f, char *buf);
> int fgetc(FILE *f);
> int fputc(int c, FILE *f);
> int fread(char *buf, unsigned size, unsigned n, FILE *f);
> int fwrite(char *buf, unsigned size, unsigned n, FILE *f);
> char *gets(char *buf);
> int puts();
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
> int strlen(const char *s);
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
> void qsort(void *base, unsigned n, int size, int (*compar)());
> char *malloc(unsigned n);
> void free(char *p);
> char *realloc(char *p, unsigned n);
> char *calloc(unsigned num, unsigned size);
> void swab(char *from, char *to, int n);
> int getargs(char **argv, int maxarg);
> long tell(int f);
> char *timezone(int zone, int dst);
> #endif
```

### usr/src/cmd/osh.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/osh.c unix-v7-c99/usr/src/cmd/osh.c || true
```

Expect:

```
55c55
< char	*mesg[NSIG] {
---
> char	*mesg[NSIG] = {
78,80c78,111
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
> int
> main(int c, char **av)
82,83c113,114
< 	register f;
< 	register char *acname, **v;
---
> 	register int f;
> 	register char **v;
93d123
< 	acname = "<none>";
137c167,168
< main1()
---
> int
> main1(void)
140c171
< 	register *t;
---
> 	register int *t;
158c189
< 				return;
---
> 				return(0);
163c194
< 			execute(t);
---
> 			execute(t, 0, 0);
164a196
> 	return(0);
167c199,200
< word()
---
> int
> word(void)
187c220
< 				return;
---
> 				return(0);
204c237
< 		return;
---
> 		return(0);
217c250
< 			return;
---
> 			return(0);
223,224c256,257
< tree(n)
< int n;
---
> int *
> tree(int n)
226c259
< 	register *t;
---
> 	register int *t;
229c262
< 	treep =+ n;
---
> 	treep += n;
238c271,272
< getc()
---
> int
> getc(void)
248c282
< 		argp =- 10;
---
> 		argp -= 10;
250c284
< 		argp =+ 10;
---
> 		argp += 10;
256c290
< 		linep =- 10;
---
> 		linep -= 10;
258c292
< 		linep =+ 10;
---
> 		linep += 10;
292c326,327
< readc()
---
> int
> readc(void)
296c331
< 	register c;
---
> 	register int c;
299c334
< 		if (arginp == 1)
---
> 		if (arginp == (char *)1)
302c337
< 			arginp = 1;
---
> 			arginp = (char *)1;
309c344
< 	if((rdstat = read(0, &cc, 1)) != 1)
---
> 	if((rdstat = read(0, &cc, 1)) != 1) {
311a347
> 	}
323,324c359,364
< syntax(p1, p2)
< char **p1, **p2;
---
> int *syn1(char **p1, char **p2);
> int *syn2(char **p1, char **p2);
> int *syn3(char **p1, char **p2);
> int *syntax(char **p1, char **p2);
> int *
> syntax(char **p1, char **p2)
342,343c382,383
< syn1(p1, p2)
< char **p1, **p2;
---
> int *
> syn1(char **p1, char **p2)
346c386
< 	register *t, *t1;
---
> 	register int *t, *t1;
370c410
< 			t[DLEF] = syn2(p1, p);
---
> 			t[DLEF] = (int)(long)syn2(p1, p);
373,374c413,414
< 				t1 = t[DLEF];
< 				t1[DFLG] =| FAND|FPRS|FINT;
---
> 				t1 = (int *)(long)t[DLEF];
> 				t1[DFLG] |= FAND|FPRS|FINT;
376c416
< 			t[DRIT] = syntax(p+1, p2);
---
> 			t[DRIT] = (int)(long)syntax(p+1, p2);
392,393c432,433
< syn2(p1, p2)
< char **p1, **p2;
---
> int *
> syn2(char **p1, char **p2)
415,416c455,456
< 			t[DLEF] = syn3(p1, p);
< 			t[DRIT] = syn2(p+1, p2);
---
> 			t[DLEF] = (int)(long)syn3(p1, p);
> 			t[DRIT] = (int)(long)syn2(p+1, p2);
430,431c470,471
< syn3(p1, p2)
< char **p1, **p2;
---
> int *
> syn3(char **p1, char **p2)
435c475
< 	register *t;
---
> 	register int *t;
440c480
< 		flg =| FPAR;
---
> 		flg |= FPAR;
468c508
< 			flg =| FCAT; else
---
> 			flg |= FCAT; else
469a510
> 		/* fallthrough */
483c524
< 				i = *p;
---
> 				i = (int)(long)*p;
488c529
< 			o = *p;
---
> 			o = (int)(long)*p;
501c542
< 		t[DSPR] = syn1(lp, rp);
---
> 		t[DSPR] = (int)(long)syn1(lp, rp);
510c551
< 		t[l+DCOM] = p1[l];
---
> 		t[l+DCOM] = (int)(long)p1[l];
518,520c559,560
< scan(at, f)
< int *at;
< int (*f)();
---
> int
> scan(int *at, int (*f)())
523c563
< 	register *t;
---
> 	register int *t;
526,527c566,567
< 	while(p = *t++)
< 		while(c = *p)
---
> 	while((p = (char *)(long)*t++))
> 		while((c = *p))
528a569
> 	return(0);
531,532c572,573
< tglob(c)
< int c;
---
> int
> tglob(int c)
540,541c581,582
< trim(c)
< int c;
---
> int
> trim(int c)
547,548c588,589
< execute(t, pf1, pf2)
< int *t, *pf1, *pf2;
---
> int
> execute(int *t, int *pf1, int *pf2)
551c592
< 	register *t1;
---
> 	register int *t1;
553d593
< 	extern errno;
559c599
< 		cp1 = t[DCOM];
---
> 		cp1 = (char *)(long)t[DCOM];
562c602
< 				if(chdir(t[DCOM+1]) < 0)
---
> 				if(chdir((char *)(long)t[DCOM+1]) < 0)
566c606
< 			return;
---
> 			return(0);
571c611
< 				return;
---
> 				return(0);
576c616
< 			return;
---
> 			return(0);
580c620
< 				execv("/bin/login", t+DCOM);
---
> 				execv("/bin/login", (char **)(t+DCOM));
583c623
< 			return;
---
> 			return(0);
587c627
< 				execv("/bin/newgrp", t+DCOM);
---
> 				execv("/bin/newgrp", (char **)(t+DCOM));
590c630
< 			return;
---
> 			return(0);
594c634
< 			return;
---
> 			return(0);
597c637,638
< 			return;
---
> 			return(0);
> 		/* fallthrough */
606c647
< 			return;
---
> 			return(0);
618c659
< 				return;
---
> 				return(0);
621c662
< 			return;
---
> 			return(0);
625c666
< 			i = open(t[DLEF], 0);
---
> 			i = open((char *)(long)t[DLEF], 0);
627c668
< 				prs(t[DLEF]);
---
> 				prs((char *)(long)t[DLEF]);
634c675
< 				i = open(t[DRIT], 1);
---
> 				i = open((char *)(long)t[DRIT], 1);
640c681
< 			i = creat(t[DRIT], 0666);
---
> 			i = creat((char *)(long)t[DRIT], 0666);
642c683
< 				prs(t[DRIT]);
---
> 				prs((char *)(long)t[DRIT]);
672,674c713,715
< 			if(t1 = t[DSPR])
< 				t1[DFLG] =| f&FINT;
< 			execute(t1);
---
> 			if((t1 = (int *)(long)t[DSPR]))
> 				t1[DFLG] |= f&FINT;
> 			execute(t1, 0, 0);
680,681c721,722
< 			t[DSPR] = "/etc/glob";
< 			execv(t[DSPR], t+DSPR);
---
> 			t[DSPR] = (int)(long)"/etc/glob";
> 			execv((char *)(long)t[DSPR], (char **)(t+DSPR));
687c728
< 		texec(t[DCOM], t);
---
> 		texec((char *)(long)t[DCOM], t);
690c731
< 		while(*cp1 = *cp2++)
---
> 		while((*cp1 = *cp2++))
692,693c733,734
< 		cp2 = t[DCOM];
< 		while(*cp1++ = *cp2++);
---
> 		cp2 = (char *)(long)t[DCOM];
> 		while((*cp1++ = *cp2++));
696c737
< 		prs(t[DCOM]);
---
> 		prs((char *)(long)t[DCOM]);
703,704c744,745
< 		t1 = t[DLEF];
< 		t1[DFLG] =| FPOU | (f&(FPIN|FINT|FPRS));
---
> 		t1 = (int *)(long)t[DLEF];
> 		t1[DFLG] |= FPOU | (f&(FPIN|FINT|FPRS));
706,707c747,748
< 		t1 = t[DRIT];
< 		t1[DFLG] =| FPIN | (f&(FPOU|FINT|FAND|FPRS));
---
> 		t1 = (int *)(long)t[DRIT];
> 		t1[DFLG] |= FPIN | (f&(FPOU|FINT|FAND|FPRS));
709c750
< 		return;
---
> 		return(0);
713,719c754,760
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
721a763
> 	return(0);
724,725c766,767
< texec(f, at)
< int *at;
---
> int
> texec(char *f, int *at)
727c769
< 	extern errno;
---
> 	extern int errno;
731c773
< 	execv(f, t+DCOM);
---
> 	execv(f, (char **)(t+DCOM));
734,736c776,778
< 			t[DCOM] = linep;
< 		t[DSPR] = "/usr/bin/osh";
< 		execv(t[DSPR], t+DSPR);
---
> 			t[DCOM] = (int)(long)linep;
> 		t[DSPR] = (int)(long)"/usr/bin/osh";
> 		execv((char *)(long)t[DSPR], (char **)(t+DSPR));
741c783
< 		prs(t[DCOM]);
---
> 		prs((char *)(long)t[DCOM]);
744a787
> 	return(0);
747,749c790,791
< err(s, exitno)
< char *s;
< int exitno;
---
> int
> err(char *s, int exitno)
757a800
> 	return(0);
760,761c803,804
< prs(as)
< char *as;
---
> int
> prs(char *as)
767a811
> 	return(0);
770c814,815
< putc(c)
---
> int
> putc(int c)
775a821
> 	return(0);
778,779c824,825
< prn(n)
< int n;
---
> int
> prn(int n)
781c827
< 	register a;
---
> 	register int a;
783c829
< 	if (a = n/10)
---
> 	if ((a = n/10))
785a832
> 	return(0);
788,790c835,836
< any(c, as)
< int c;
< char *as;
---
> int
> any(int c, char *as)
801,802c847,848
< equal(as1, as2)
< char *as1, *as2;
---
> int
> equal(char *as1, char *as2)
814,815c860,861
< pwait(i, t)
< int i, *t;
---
> int
> pwait(int i, int *t)
817c863
< 	register p, e;
---
> 	register int p, e;
818a865
> 	(void)t;
840c887
< 		if (e || s&&stoperr)
---
> 		if (e || (s&&stoperr))
842c889
< 		errval =| (s>>8);
---
> 		errval |= (s>>8);
843a891
> 	return(0);
```

### usr/src/cmd/prof.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/prof.c unix-v7-c99/usr/src/cmd/prof.c || true
```

Expect:

```
11a12,15
> int min(unsigned a, unsigned b);
> int max(unsigned a, unsigned b);
> int done(void);
> int timcmp(const void *vp1, const void *vp2), valcmp(const void *vp1, const void *vp2);
42c46
< double	ftime;
---
> double	ftim;
56,57c60
< main(argc, argv)
< char **argv;
---
> int main(int argc, char **argv)
60c63
< 	int timcmp(), valcmp();
---
> 	int timcmp(const void *, const void *), valcmp(const void *, const void *);
61a65
> #ifdef plot
64d67
< 	struct cnt *cp;
65a69,70
> #endif
> 	struct cnt *cp;
83c88
< 				if(lowpc == -1)
---
> 				if(lowpc == (unsigned)-1)
121a127
> #ifdef plot
122a129
> #endif
153,154c160,161
< 		register j;
< 		unsigned UNIT ccnt;
---
> 		register int j;
> 		unsigned short ccnt;
162,165c169,172
< 		ftime = ccnt;
< 		totime += ftime;
< 		if(ftime > maxtime)
< 			maxtime = ftime;
---
> 		ftim = ccnt;
> 		totime += ftim;
> 		if(ftim > maxtime)
> 			maxtime = ftim;
172c179
< 			nl[j].time += overlap*ftime/scale;
---
> 			nl[j].time += overlap*ftim/scale;
201c208
< 		ftime = ccnt;
---
> 		ftim = ccnt;
204c211
< 		lastsx -= 2000.*ftime/totime;
---
> 		lastsx -= 2000.*ftim/totime;
210c217
< 				lastx = -ftime*2000./maxtime;
---
> 				lastx = -ftim*2000./maxtime;
223c230
< 		ftime = np->time/totime;
---
> 		ftim = np->time/totime;
252c259
< 		ftime = np->time/totime;
---
> 		ftim = np->time/totime;
254c261
< 		printf("%8.8s%6.1f%9.2f", np->name, 100*ftime, actime/60);
---
> 		printf("%8.8s%6.1f%9.2f", np->name, 100*ftim, actime/60);
264,265c271
< min(a, b)
< unsigned a, b;
---
> int min(unsigned a, unsigned b)
272,273c278
< max(a, b)
< unsigned a, b;
---
> int max(unsigned a, unsigned b)
280,281c285
< valcmp(p1, p2)
< struct nl *p1, *p2;
---
> int valcmp(const void *vp1, const void *vp2)
282a287
> 	const struct nl *p1 = vp1, *p2 = vp2;
286,287c291
< timcmp(p1, p2)
< struct nl *p1, *p2;
---
> int timcmp(const void *vp1, const void *vp2)
288a293
> 	const struct nl *p1 = vp1, *p2 = vp2;
299c304
< done()
---
> int done(void)
308a314
> 	return(0);
```

### usr/src/cmd/ps.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/ps.c unix-v7-c99/usr/src/cmd/ps.c || true
```

Expect:

```
8c8,10
< #include <core.h>
---
> #define TXTRNDSIZ 8192L
> #define stacktop(siz) (0x10000L)
> #define stackbas(siz) (0x10000L-siz)
10,11c12,13
< #include <sys/proc.h>
< #include <sys/tty.h>
---
> #include "../../sys/h/proc.h"
> struct tty;
13c15,17
< #include <sys/user.h>
---
> #include <sys/stat.h>
> #include "../../sys/h/user.h"
> #undef u
16,19c20,23
< 	{ "_proc" },
< 	{ "_swapdev" },
< 	{ "_swplo" },
< 	{ "" },
---
> 	{ "_proc",    0, 0 },
> 	{ "_swapdev", 0, 0 },
> 	{ "_swplo",   0, 0 },
> 	{ "",         0, 0 },
32,35c36,42
< long	lseek();
< char	*gettty();
< char	*getptr();
< char	*strncmp();
---
> long	lseek(int fd, long offset, int ptrname);
> char	*gettty(void);
> char	*getptr(char **adr);
> int	getdev(void);
> int	prcom(int puid);
> int	getbyte(char *adr);
> int	within(char *adr, long lbd, long ubd);
50,51c57,58
< main(argc, argv)
< char **argv;
---
> int
> main(int argc, char **argv)
154c161,162
< getdev()
---
> int
> getdev(void)
156d163
< #include <sys/stat.h>
157a165
> 	register int i;
159a168
> 	char dpath[DIRSIZ+1];
169c178,181
< 		if(stat(dbuf.d_name, &sbuf) < 0)
---
> 		for (i=0; i<DIRSIZ; i++)
> 			dpath[i] = dbuf.d_name[i];
> 		dpath[DIRSIZ] = '\0';
> 		if(stat(dpath, &sbuf) < 0)
173c185,186
< 		strcpy(devl[ndev].dname, dbuf.d_name);
---
> 		for (i=0; i<DIRSIZ; i++)
> 			devl[ndev].dname[i] = dbuf.d_name[i];
179,180c192
< 		fprintf(stderr, "Can't open /dev/swap\n");
< 		exit(1);
---
> 		swap = -1;
181a194
> 	return(0);
185,186c198
< round(a, b)
< 	long		a, b;
---
> round(long a, long b)
199c211,212
< prcom(puid)
---
> int
> prcom(int puid)
201c214
< 	char abuf[512];
---
> 	int abuf[128];
241c254
< 			"0SWRIZT"[mproc.p_stat], puid);
---
> 			"0SWRIZT"[(unsigned char)mproc.p_stat], puid);
304c317
< 	if (read(file, abuf, sizeof(abuf)) != sizeof(abuf))
---
> 	if (read(file, (char *)abuf, sizeof(abuf)) != sizeof(abuf))
306c319
< 	for (ip = (int *)&abuf[512]-2; ip > (int *)abuf; ) {
---
> 	for (ip = &abuf[128]-2; ip > abuf; ) {
312c325
< 			for (cp1 = cp; cp1 < &abuf[512]; cp1++) {
---
> 			for (cp1 = cp; cp1 < (char *)abuf + sizeof(abuf); cp1++) {
339c352
< gettty()
---
> gettty(void)
341c354
< 	register i;
---
> 	register int i;
358,359c371
< getptr(adr)
< char **adr;
---
> getptr(char **adr)
363c375
< 	register i;
---
> 	register unsigned int i;
373,374c385,386
< getbyte(adr)
< char *adr;
---
> int
> getbyte(char *adr)
395,397c407,408
< within(adr,lbd,ubd)
< char *adr;
< long lbd, ubd;
---
> int
> within(char *adr, long lbd, long ubd)
399c410
< 	return((unsigned)adr>=lbd && (unsigned)adr<ubd);
---
> 	return((unsigned long)adr>=(unsigned long)lbd && (unsigned long)adr<(unsigned long)ubd);
```

### usr/src/cmd/pstat.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/pstat.c unix-v7-c99/usr/src/cmd/pstat.c || true
```

Expect:

```
5a6
> #include <stdio.h>
7,8c8,15
< #include <sys/conf.h>
< #include <sys/tty.h>
---
> #include "../../sys/h/tty.h"
> #include "../../sys/h/inode.h"
> #include "../../sys/h/text.h"
> #include "../../sys/h/proc.h"
> #include <sys/dir.h>
> #include "../../sys/h/user.h"
> #include "../../sys/h/file.h"
> #include <a.out.h>
20c27
< 	"_inode", 0, 0,
---
> 	{"_inode", 0, 0},
22c29
< 	"_text", 0, 0,
---
> 	{"_text", 0, 0},
24c31
< 	"_proc", 0, 0,
---
> 	{"_proc", 0, 0},
26c33
< 	"_dh11", 0, 0,
---
> 	{"_dh11", 0, 0},
28c35
< 	"_ndh11", 0, 0,
---
> 	{"_ndh11", 0, 0},
30c37
< 	"_kl11", 0, 0,
---
> 	{"_kl11", 0, 0},
32,33c39,40
< 	"_file", 0, 0,
< 	0,
---
> 	{"_file", 0, 0},
> 	{"", 0, 0},
45,46c52,62
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
> int
> main(int argc, char **argv)
92c108
< 	nlist(fnlist, setup);
---
> 	nlist(fnlist, (struct nlist *)setup);
108a125
> 	return(0);
111c128,129
< doinode()
---
> int
> doinode(void)
113d130
< #include <sys/inode.h>
148a166
> 	return(0);
151c169,170
< putf(v, n)
---
> int
> putf(int v, int n)
156a176
> 	return(0);
159c179,180
< dotext()
---
> int
> dotext(void)
161d181
< #include <sys/text.h>
164c184
< 	register loc;
---
> 	register int loc;
193a214
> 	return(0);
196c217,218
< doproc()
---
> int
> doproc(void)
198d219
< #include <sys/proc.h>
201c222
< 	register loc, np;
---
> 	register int loc, np;
233a255
> 	return(0);
236c258,259
< dotty()
---
> int
> dotty(void)
250c273
< 		return;
---
> 		return(0);
257a281
> 	return(0);
260,261c284,285
< ttyprt(n, atp)
< struct tty *atp;
---
> int
> ttyprt(int n, struct tty *atp)
283a308
> 	return(0);
286c311,312
< dousr()
---
> int
> dousr(void)
288,289d313
< #include <sys/dir.h>
< #include <sys/user.h>
295c319
< 	register i;
---
> 	register int i;
352a377
> 	return(0);
355,356c380,381
< oatoi(s)
< char *s;
---
> int
> oatoi(char *s)
358c383
< 	register v;
---
> 	register int v;
366c391,392
< dofil()
---
> int
> dofil(void)
368d393
< #include <sys/file.h>
371c396
< 	register nf;
---
> 	register int nf;
392a418
> 	return(0);
```

### usr/src/cmd/sa.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sa.c unix-v7-c99/usr/src/cmd/sa.c || true
```

Expect:

```
3d2
< #include <sys/acct.h>
4a4
> #include <pwd.h>
6c6,17
< /* interpret command time accounting */
---
> struct	acct {
> 	char	ac_comm[10];
> 	char	ac_pad[2];
> 	long	ac_utime;
> 	long	ac_stime;
> 	long	ac_etime;
> 	time_t	ac_btime;
> 	short	ac_uid;
> 	short	ac_gid;
> 	short	ac_mem;
> 	short	ac_io;
> };
27c38
< struct	user {
---
> struct	user_acct {
31c42
< } user[256];
---
> } usr[256];
47d57
< time_t	expand();
49,50c59,73
< main(argc, argv)
< char **argv;
---
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
> int
> main(int argc, char **argv)
54,55d76
< 	extern tcmp(), ncmp(), bcmp();
< 	extern float sum();
135a157,158
> 	(void)acct((char *)0);
> 	(void)acct("/usr/adm/acct");
143c166
< 		return;
---
> 		return 0;
156c179
< 		for(j=0; j<NC; j++)
---
> 		for(j=0; j<(int)NC; j++)
172c195
< 		for(j=0; j<NC; j++)
---
> 		for(j=0; j<(int)NC; j++)
183c206
< 			fwrite((char *)user, sizeof(user), 1, ff);
---
> 			fwrite((char *)usr, sizeof(usr), 1, ff);
202c225
< 	qsort(tab, k, sizeof(tab[0]), nflg? ncmp: (bflg?bcmp:tcmp));
---
> 	qsort((char *)tab, k, sizeof(tab[0]), nflg? ncmp: (bflg?bcmp:tcmp));
210a234
> 	return 0;
213c237,238
< printmoney()
---
> void
> printmoney(void)
215,217c240,241
< 	register i;
< 	char buf[128];
< 	register char *cp;
---
> 	int i;
> 	struct passwd *pw;
220,221c244,246
< 		if (user[i].ncomm) {
< 			if (getpw(i, buf)!=0)
---
> 		if (usr[i].ncomm) {
> 			pw = getpwuid(i);
> 			if (pw == NULL)
223,229c248,249
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
231c251
< 			    user[i].ncomm, user[i].fctime/60);
---
> 			    usr[i].ncomm, usr[i].fctime/60);
236,237c256,257
< column(n, a, b, c)
< double n, a, b, c;
---
> void
> column(double n, double a, double b, double c)
258,259c278,279
< col(n, a, m)
< double n, a, m;
---
> void
> col(double n, double a, double m)
272,273c292,293
< doacct(f)
< char *f;
---
> void
> doacct(char *f)
279,280c299,300
< 	register char *cp;
< 	register int c;
---
> 	char *cp;
> 	int c;
302c322
< 		if (fbuf.ac_flag&AFORK) {
---
> 		if (0) {
316,317c336,337
< 		user[c].ncomm++;
< 		user[c].fctime += x/60.;
---
> 		usr[c].ncomm++;
> 		usr[c].fctime += x/60.;
334,335c354,355
< ncmp(p1, p2)
< struct tab *p1, *p2;
---
> int
> ncmp(struct tab *p1, struct tab *p2)
345,346c365,366
< bcmp(p1, p2)
< struct tab *p1, *p2;
---
> int
> bcmp(struct tab *p1, struct tab *p2)
349d368
< 	float sum();
365,366c384,385
< tcmp(p1, p2)
< struct tab *p1, *p2;
---
> int
> tcmp(struct tab *p1, struct tab *p2)
368d386
< 	extern float sum();
386,387c404,405
< float sum(p)
< struct tab *p;
---
> float
> sum(struct tab *p)
397c415,416
< init()
---
> void
> init(void)
420c439
< 	fread((char *)user, sizeof(user), 1, f);
---
> 	fread((char *)usr, sizeof(usr), 1, f);
424,425c443,444
< enter(np)
< char *np;
---
> int
> enter(char *np)
429c448
< 	for (i=j=0; i<NC; i++) {
---
> 	for (i=j=0; i<(int)NC; i++) {
435c454
< 	for (i=j=0; j<NC; j++) {
---
> 	for (i=0, j=0; j<(int)NC; j++) {
441c460
< 		for (j=0; j<NC; j++)
---
> 		for (j=0; j<(int)NC; j++)
447c466
< 	for (j=0; j<NC; j++)
---
> 	for (j=0; j<(int)NC; j++)
453c472,473
< strip()
---
> void
> strip(void)
475,476c495
< expand(t)
< unsigned t;
---
> expand(unsigned t)
478c497
< 	register time_t nt;
---
> 	time_t nt;
```

### usr/src/cmd/sed/sed.h

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sed/sed.h unix-v7-c99/usr/src/cmd/sed/sed.h || true
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
104,107c104,107
< union	reptr {
< 	struct reptr1 {
< 		char	*ad1;
< 		char	*ad2;
---
> struct reptr {
> 	char	*ad1;
> 	char	*ad2;
> 	union {
109,128c109,117
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
136,137c125,126
< 	union reptr	*chain;
< 	union reptr	*address;
---
> 	struct reptr	*chain;
> 	struct reptr	*address;
151c140
< union reptr	**cmpend[DEPTH];
---
> struct reptr	**cmpend[DEPTH];
153c142
< union reptr	*pending;
---
> struct reptr	*pending;
```

### usr/src/cmd/sed/sed0.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sed/sed0.c unix-v7-c99/usr/src/cmd/sed/sed0.c || true
```

Expect:

```
3a4,8
> void	fcomp(void);
> void	dechain(void);
> void	execute(char *file);
> int	rline(char *lbuf);
> int	cmp(char *a, char *b);
21,22c26,27
< main(argc, argv)
< char	*argv[];
---
> int
> main(int argc, char *argv[])
105c110
< /*	abort();	/*DEBUG*/
---
> /*	abort();	DEBUG */
109c114
< 	else while(--eargc >= 0) {
---
> 	else while(--eargc >= 0)
111d115
< 	}
115c119,120
< fcomp()
---
> void
> fcomp(void)
119,120c124,125
< 	char	*address();
< 	union reptr	*pt, *pt1;
---
> 	char	*address(char *expbuf);
> 	struct reptr	*pt, *pt1;
143c148
< /*	fprintf(stdout, "cp: %s\n", cp);	/*DEBUG*/
---
> /*	fprintf(stdout, "cp: %s\n", cp);	DEBUG */
210c215
< 				cmpend[depth++] = &rep->lb1;
---
> 				cmpend[depth++] = &rep->u.lb1;
261c266
< 				if(lpt = search(lab)) {
---
> 				if((lpt = search(lab))) {
290,291c295,296
< 				rep->re1 = p;
< 				p = text(rep->re1);
---
> 				rep->u.re1 = p;
> 				p = text(rep->u.re1);
300,301c305,306
< 				rep->re1 = p;
< 				p = text(rep->re1);
---
> 				rep->u.re1 = p;
> 				p = text(rep->u.re1);
314,315c319,320
< 				rep->re1 = p;
< 				p = text(rep->re1);
---
> 				rep->u.re1 = p;
> 				p = text(rep->u.re1);
345,346c350,351
< 					if(pt = labtab->chain) {
< 						while(pt1 = pt->lb1)
---
> 					if((pt = labtab->chain)) {
> 						while((pt1 = pt->u.lb1))
348c353
< 						pt->lb1 = rep;
---
> 						pt->u.lb1 = rep;
362c367
< 				if(lpt = search(lab)) {
---
> 				if((lpt = search(lab))) {
364c369
< 						rep->lb1 = lpt->address;
---
> 						rep->u.lb1 = lpt->address;
367c372
< 						while(pt1 = pt->lb1)
---
> 						while((pt1 = pt->u.lb1))
369c374
< 						pt->lb1 = rep;
---
> 						pt->u.lb1 = rep;
407,408c412,413
< 				rep->re1 = p;
< 				p = text(rep->re1);
---
> 				rep->u.re1 = p;
> 				p = text(rep->u.re1);
417c422
< 				rep->lb1 = ptrspace;
---
> 				rep->u.lb1 = ptrspace;
435,436c440,441
< 				rep->re1 = p;
< 				p = compile(rep->re1);
---
> 				rep->u.re1 = p;
> 				p = compile(rep->u.re1);
441,442c446,447
< 				if(p == rep->re1) {
< 					rep->re1 = op;
---
> 				if(p == rep->u.re1) {
> 					rep->u.re1 = op;
444c449
< 					op = rep->re1;
---
> 					op = rep->u.re1;
529,530c534,535
< 				rep->re1 = p;
< 				p = ycomp(rep->re1);
---
> 				rep->u.re1 = p;
> 				p = ycomp(rep->u.re1);
588,589c593,594
< char *compile(expbuf)
< char	*expbuf;
---
> char *
> compile(char *expbuf)
591c596
< 	register c;
---
> 	register int c;
749,750c754,755
< rline(lbuf)
< char	*lbuf;
---
> int
> rline(char *lbuf)
753c758
< 	register	t;
---
> 	register int	t;
764c769
< 			while(*++p = *q++) {
---
> 			while((*++p = *q++)) {
783c788
< 		while(*++p = *q++) {
---
> 		while((*++p = *q++)) {
816,817c821,822
< char	*address(expbuf)
< char	*expbuf;
---
> char	*
> address(char *expbuf)
855,856c860,861
< cmp(a, b)
< char	*a,*b;
---
> int
> cmp(char *a, char *b)
863c868
< 	while(*++ra == *++rb)
---
> 	while ((*++ra == *++rb))
908c913,914
< dechain()
---
> void
> dechain(void)
911c917
< 	union reptr	*rptr, *trptr;
---
> 	struct reptr	*rptr, *trptr;
922,923c928,929
< 			while(trptr = rptr->lb1) {
< 				rptr->lb1 = lptr->address;
---
> 			while((trptr = rptr->u.lb1)) {
> 				rptr->u.lb1 = lptr->address;
926c932
< 			rptr->lb1 = lptr->address;
---
> 			rptr->u.lb1 = lptr->address;
931,932c937,938
< char *ycomp(expbuf)
< char	*expbuf;
---
> char *
> ycomp(char *expbuf)
952,953c958,959
< 		if((ep[c] = *tsp++) == '\\' && *tsp == 'n') {
< 			ep[c] = '\n';
---
> 		if((ep[(unsigned char)c] = *tsp++) == '\\' && *tsp == 'n') {
> 			ep[(unsigned char)c] = '\n';
956c962
< 		if(ep[c] == seof || ep[c] == '\0')
---
> 		if(ep[(unsigned char)c] == seof || ep[(unsigned char)c] == '\0')
964,965c970,971
< 		if(ep[c] == 0)
< 			ep[c] = c;
---
> 		if(ep[(unsigned char)c] == 0)
> 			ep[(unsigned char)c] = c;
```

### usr/src/cmd/sed/sed1.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sed/sed1.c unix-v7-c99/usr/src/cmd/sed/sed1.c || true
```

Expect:

```
3a4,9
> void	dosub(char *rhsbuf);
> void	command(struct reptr *ipc);
> void	arout(void);
> int	match(char *expbuf, int gf);
> int	advance(char *alp, char *aep);
> int	ecmp(char *a, char *b, int count);
39,40c45,46
< execute(file)
< char *file;
---
> void
> execute(char *file)
43c49
< 	register union reptr	*ipc;
---
> 	register struct reptr	*ipc;
136c142
< 				if((ipc = ipc->lb1) == 0) {
---
> 				if((ipc = ipc->u.lb1) == 0) {
158,159c164,165
< match(expbuf, gf)
< char	*expbuf;
---
> int
> match(char *expbuf, int gf)
167c173
< 		while(*p1++ = *p2++);
---
> 		while((*p1++ = *p2++));
205,206c211,212
< advance(alp, aep)
< char	*alp, *aep;
---
> int
> advance(char *alp, char *aep)
213c219
< /*fprintf(stderr, "*lp = %c, %o\n*ep = %c, %o\n", *lp, *lp, *ep, *ep);	/*DEBUG*/
---
> /*fprintf(stderr, "*lp = %c, %o\n*ep = %c, %o\n", *lp, *lp, *ep, *ep);	DEBUG */
248c254
< 		braslist[*ep++] = lp;
---
> 		braslist[(unsigned char)*ep++] = lp;
252c258
< 		braelist[*ep++] = lp;
---
> 		braelist[(unsigned char)*ep++] = lp;
256,257c262,263
< 		bbeg = braslist[*ep];
< 		ct = braelist[*ep++] - bbeg;
---
> 		bbeg = braslist[(unsigned char)*ep];
> 		ct = braelist[(unsigned char)*ep++] - bbeg;
266,267c272,273
< 		bbeg = braslist[*ep];
< 		ct = braelist[*ep++] - bbeg;
---
> 		bbeg = braslist[(unsigned char)*ep];
> 		ct = braelist[(unsigned char)*ep++] - bbeg;
286c292
< 		while (*lp++ == *ep);
---
> 		while ((*lp++ == *ep));
315c321
< 			c = *(braslist[ep[1]]);
---
> 			c = *(braslist[(unsigned char)ep[1]]);
336,337c342,343
< substitute(ipc)
< union reptr	*ipc;
---
> int
> substitute(struct reptr *ipc)
339c345
< 	if(match(ipc->re1, 0) == 0)	return(0);
---
> 	if(match(ipc->u.re1, 0) == 0)	return(0);
346c352
< 			if(match(ipc->re1, 1) == 0) break;
---
> 			if(match(ipc->u.re1, 1) == 0) break;
353,354c359,360
< dosub(rhsbuf)
< char	*rhsbuf;
---
> void
> dosub(char *rhsbuf)
364c370
< 	while(c = *rp++) {
---
> 	while((c = *rp++)) {
378c384
< 	while (*sp++ = *lp++)
---
> 	while ((*sp++ = *lp++))
384c390
< 	while (*lp++ = *sp++);
---
> 	while ((*lp++ = *sp++));
387,388c393,394
< char	*place(asp, al1, al2)
< char	*asp, *al1, *al2;
---
> char	*
> place(char *asp, char *al1, char *al2)
403,404c409,410
< command(ipc)
< union reptr	*ipc;
---
> void
> command(struct reptr *ipc)
425c431
< 				for(p1 = ipc->re1; *p1; )
---
> 				for(p1 = ipc->u.re1; *p1; )
444c450
< 			while(*p2++ = *p1++);
---
> 			while((*p2++ = *p1++));
456c462
< 			while(*p1++ = *p2++);
---
> 			while((*p1++ = *p2++));
464c470
< 			while(*p1++ = *p2++)
---
> 			while((*p1++ = *p2++))
473c479
< 			while(*p1++ = *p2++);
---
> 			while((*p1++ = *p2++));
481c487
< 			while(*p1++ = *p2++)
---
> 			while((*p1++ = *p2++))
488c494
< 			for(p1 = ipc->re1; *p1; )
---
> 			for(p1 = ipc->u.re1; *p1; )
505c511
< 						while(*p2++ = *p3++)
---
> 						while((*p2++ = *p3++))
523c529
< 					while(*p2++ = *p3++)
---
> 					while((*p2++ = *p3++))
599c605
< 			if(ipc->pfl && i)
---
> 			if(ipc->pfl && i) {
604a611
> 			}
624c631
< 			while(*p2++ = *p1++);
---
> 			while((*p2++ = *p1++));
627c634
< 			while(*p2++ = *p1++);
---
> 			while((*p2++ = *p1++));
631c638
< 			while(*p2++ = *p1++);
---
> 			while((*p2++ = *p1++));
637,638c644,645
< 			p2 = ipc->re1;
< 			while(*p1 = p2[*p1])	p1++;
---
> 			p2 = ipc->u.re1;
> 			while((*p1 = p2[(unsigned char)*p1]))	p1++;
645,646c652
< gline(addr)
< char	*addr;
---
> gline(char *addr)
649c655
< 	register	c;
---
> 	register int	c;
661c667
< 			if(p2 >=  ebp) {
---
> 			if(f != 0 && p2 >=  ebp) {
683,684c689,690
< ecmp(a, b, count)
< char	*a, *b;
---
> int
> ecmp(char *a, char *b, int count)
691c697,698
< arout()
---
> void
> arout(void)
701c708
< 			for(p1 = (*aptr)->re1; *p1; )
---
> 			for(p1 = (*aptr)->u.re1; *p1; )
705c712
< 			if((fi = fopen((*aptr)->re1, "r")) == NULL)
---
> 			if((fi = fopen((*aptr)->u.re1, "r")) == NULL)
```

### usr/src/cmd/tc.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/tc.c unix-v7-c99/usr/src/cmd/tc.c || true
```

Expect:

```
8c8
< #define	oput(c) if (pgskip==0) putchar(c); else;
---
> #define	oput(c) do { if (pgskip==0) putchar(c); } while (0)
57,59c57,67
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
> int main(int argc, char **argv)
61c69
< 	register i, j;
---
> 	register int i, j;
63c71
< 	extern ex();
---
> 	extern int ex(void);
70c78
< 				if(i = atoi())pl = i/3;
---
> 				if((i = tcatoi()))pl = i/3;
78c86
< 				pgskip = atoi();
---
> 				pgskip = tcatoi();
83,84c91,92
< 				if(i = atoi())mpy = i;
< 				if(i = atoi())div = i;
---
> 				if((i = tcatoi()))mpy = i;
> 				if((i = tcatoi()))div = i;
94,95c102,103
< 	sigint = signal(SIGINT, ex);
< 	sigquit = signal(SIGQUIT, SIG_IGN);
---
> 	sigint = (int(*)())signal(SIGINT, (int)ex);
> 	sigquit = (int(*)())signal(SIGQUIT, (int)SIG_IGN);
226,227c234
< lig(x)
< char *x;
---
> int lig(char *x)
229c236
< 	register i, j;
---
> 	register int i, j;
245a253
> 	return(0);
247c255
< init(){
---
> int init(void){
261a270
> 	return(0);
263c272
< ex(){
---
> int ex(void){
271a281
> 	return(0);
273c283
< kwait(){
---
> int kwait(void){
275c285
< 	if(pgskip) return;
---
> 	if(pgskip) return(0);
290c300
< 				pgskip = atoi() + 1;
---
> 				pgskip = tcatoi() + 1;
298c308,309
< 	else	return;
---
> 	else	return(0);
> 	return(0);
300,301c311
< callunix(line)
< char line[];
---
> int callunix(char line[])
305c315
< 		signal(SIGINT,sigint); signal(SIGQUIT,sigquit);
---
> 		signal(SIGINT,(int)sigint); signal(SIGQUIT,(int)sigquit);
311,312c321,322
< 		return;
< 	else{	signal(SIGINT, SIG_IGN); signal(SIGQUIT, SIG_IGN);
---
> 		return(0);
> 	else{	signal(SIGINT, (int)SIG_IGN); signal(SIGQUIT, (int)SIG_IGN);
314c324
< 		signal(SIGINT,ex); signal(SIGQUIT,sigquit);
---
> 		signal(SIGINT,(int)ex); signal(SIGQUIT,(int)sigquit);
315a326
> 	return(0);
317c328
< readch(){
---
> int readch(void){
322c333
< sendpt(){
---
> int sendpt(void){
327c338
< 	xb = ((xx & 03) + ((yy<<2) & 014) & 017);
---
> 	xb = (((xx & 03) + ((yy<<2) & 014)) & 017);
343c354
< 	return;
---
> 	return(0);
345c356
< atoi()
---
> int tcatoi(void)
347c358
< 	register i, j, acc;
---
> 	register int i, j, acc;
350d360
< 	long tscale();
376,377c386
< long tscale(n)
< int n;
---
> long tscale(int n)
379c388
< 	register i, j;
---
> 	register int i, j;
403,404c412,413
< getch(){
< 	register i;
---
> int getch(void){
> 	register int i;
414c423
< char *asctab[128] {
---
> char *asctab[128] = {
```

### usr/src/libc/ecvt.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/ecvt.c unix-v7-c99/usr/src/libc/ecvt.c || true
```

Expect:

```
8c8
< char	*cvt();
---
> char	*cvt(double, int, int *, int *, int);
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
27,30c23,24
< static char*
< cvt(arg, ndigits, decpt, sign, eflag)
< double arg;
< int ndigits, *decpt, *sign;
---
> char*
> cvt(double arg, int ndigits, int *decpt, int *sign, int eflag)
36c30
< 	double modf();
---
> 	double modf(double value, double *iptr);
```

### usr/src/libc/fdopen.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/fdopen.c unix-v7-c99/usr/src/libc/fdopen.c || true
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

### usr/src/libc/gcvt.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/gcvt.c unix-v7-c99/usr/src/libc/gcvt.c || true
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

### usr/src/libc/getgrent.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/getgrent.c unix-v7-c99/usr/src/libc/getgrent.c || true
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

### usr/src/libc/getgrgid.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/getgrgid.c unix-v7-c99/usr/src/libc/getgrgid.c || true
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

### usr/src/libc/getgrnam.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/getgrnam.c unix-v7-c99/usr/src/libc/getgrnam.c || true
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

### usr/src/libc/getw.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/getw.c unix-v7-c99/usr/src/libc/getw.c || true
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

### usr/src/libc/putw.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/stdio/putw.c unix-v7-c99/usr/src/libc/putw.c || true
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

### usr/src/libm/asin.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libm/asin.c unix-v7-c99/usr/src/libm/asin.c || true
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

### usr/src/libm/atan.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libm/atan.c unix-v7-c99/usr/src/libm/atan.c || true
```

Expect:

```
17c17
< double static sq2p1	 =2.414213562373095048802e0;
---
> static double sq2p1	 =2.414213562373095048802e0;
31a32,33
> static double satan(double);
> static double xatan(double);
39,42c41
< atan(arg)
< double arg;
< {
< 	double satan();
---
> atan(double arg)
43a43
> {
57,60c57
< atan2(arg1,arg2)
< double arg1,arg2;
< {
< 	double satan();
---
> atan2(double arg1, double arg2)
61a59
> {
82,85c80
< satan(arg)
< double arg;
< {
< 	double	xatan();
---
> satan(double arg)
86a82
> {
101,102c97
< xatan(arg)
< double arg;
---
> xatan(double arg)
```

### usr/src/libm/exp.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libm/exp.c unix-v7-c99/usr/src/libm/exp.c || true
```

Expect:

```
21a22,23
> extern double floor(double);
> extern double ldexp(double, int);
23,24c25
< exp(arg)
< double arg;
---
> exp(double arg)
```

### usr/src/libm/fabs.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libm/fabs.c unix-v7-c99/usr/src/libm/fabs.c || true
```

Expect:

```
2,3c2
< fabs(arg)
< double arg;
---
> fabs(double arg)
```

### usr/src/libm/floor.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libm/floor.c unix-v7-c99/usr/src/libm/floor.c || true
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

### usr/src/libm/hypot.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libm/hypot.c unix-v7-c99/usr/src/libm/hypot.c || true
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

### usr/src/libm/j0.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libm/j0.c unix-v7-c99/usr/src/libm/j0.c || true
```

Expect:

```
42a43
> static void asympt(double);
129c130
< j0(arg) double arg;{
---
> j0(double arg){
131c132
< 	double sin(), cos(), sqrt();
---
> 	double sin(double), cos(double), sqrt(double);
149c150
< y0(arg) double arg;{
---
> y0(double arg){
151c152
< 	double sin(), cos(), sqrt(), log(), j0();
---
> 	double sin(double), cos(double), sqrt(double), log(double), j0(double);
172,173c173
< static
< asympt(arg) double arg;{
---
> static void asympt(double arg){
```

### usr/src/libm/j1.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libm/j1.c unix-v7-c99/usr/src/libm/j1.c || true
```

Expect:

```
42a43
> static void asympt(double);
131c132
< j1(arg) double arg;{
---
> j1(double arg){
133c134
< 	double sin(), cos(), sqrt();
---
> 	double sin(double), cos(double), sqrt(double);
154c155
< y1(arg) double arg;{
---
> y1(double arg){
156c157
< 	double sin(), cos(), sqrt(), log(), j1();
---
> 	double sin(double), cos(double), sqrt(double), log(double), j1(double);
178,179c179,180
< static
< asympt(arg) double arg;{
---
> static void
> asympt(double arg){
```

### usr/src/libm/jn.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libm/jn.c unix-v7-c99/usr/src/libm/jn.c || true
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

### usr/src/libm/log.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libm/log.c unix-v7-c99/usr/src/libm/log.c || true
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

### usr/src/libm/pow.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libm/pow.c unix-v7-c99/usr/src/libm/pow.c || true
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

### usr/src/libm/sin.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libm/sin.c unix-v7-c99/usr/src/libm/sin.c || true
```

Expect:

```
18a19
> static double sinus(double, int);
20,21c21
< cos(arg)
< double arg;
---
> cos(double arg)
23d22
< 	double sinus();
30,31c29
< sin(arg)
< double arg;
---
> sin(double arg)
33d30
< 	double sinus();
38,40c35
< sinus(arg, quad)
< double arg;
< int quad;
---
> sinus(double arg, int quad)
42c37
< 	double modf();
---
> 	double modf(double, double *);
```

### usr/src/libm/sinh.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libm/sinh.c unix-v7-c99/usr/src/libm/sinh.c || true
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

### usr/src/libm/sqrt.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libm/sqrt.c unix-v7-c99/usr/src/libm/sqrt.c || true
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

### usr/src/libm/tan.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libm/tan.c unix-v7-c99/usr/src/libm/tan.c || true
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

### usr/src/libm/tanh.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libm/tanh.c unix-v7-c99/usr/src/libm/tanh.c || true
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

### etc/rc

Local test:

```
diff unix-v7-c99/v7/etc/rc unix-v7-c99/etc/rc || true
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

### usr/sys/sys/clock.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/clock.c unix-v7-c99/usr/sys/sys/clock.c || true
```

Expect:

```
4d3
< #include "../h/seg.h"
8c7,12
< #include "../h/reg.h"
---
> #include "../h/seg.h"		/* GIC_DIST_BASE/GIC_CPU_BASE (board memmap.h) */
> extern void addupc(caddr_t pc, void *prof, int inc);
> int intr_disable(void);
> void intr_restore(int s);
> void wakeup(caddr_t chan);
> void panic(char *s);
28,30c32,33
< clock(dev, sp, r1, nps, r0, pc, ps)
< dev_t dev;
< caddr_t pc;
---
> void
> clock(dev_t dev, int sp, int r1, int nps, int r0, caddr_t pc, int ps)
35a39
> 	(void)dev; (void)sp; (void)r1; (void)nps; (void)r0;
41d44
< 	lks->r[0] = 0115;
47d49
< 	display();
71c73
< 	spl5();
---
> 	intr_disable();
79c81
< 		while(p2->c_func = p1->c_func) {
---
> 		while((p2->c_func = p1->c_func) != 0) {
114c116
< 		spl1();
---
> 		intr_disable();
154,156c156,157
< timeout(fun, arg, tim)
< int (*fun)();
< caddr_t arg;
---
> void
> timeout(int (*fun)(), caddr_t arg, int tim)
164c165
< 	s = spl7();
---
> 	s = intr_disable();
184c185,272
< 	splx(s);
---
> 	intr_restore(s);
> }
> #define GICD_BASE	GIC_DIST_BASE	/* board-specific (conf/<board>/memmap.h) */
> #define GICC_BASE	GIC_CPU_BASE
> #define GICD_CTLR	(*(volatile unsigned int *)(GICD_BASE + 0x000))
> #define GICD_ISENABLER(n) (*(volatile unsigned int *)(GICD_BASE + 0x100 + 4*(n)))
> #define GICD_IPRIORITYR(n) (*(volatile unsigned int *)(GICD_BASE + 0x400 + 4*(n)))
> #define GICC_CTLR	(*(volatile unsigned int *)(GICC_BASE + 0x000))
> #define GICC_PMR	(*(volatile unsigned int *)(GICC_BASE + 0x004))
> #define GICC_IAR	(*(volatile unsigned int *)(GICC_BASE + 0x00c))
> #define GICC_EOIR	(*(volatile unsigned int *)(GICC_BASE + 0x010))
> #define TIMER_IRQ	27
> #define TIMER_HZ	HZ
> extern unsigned int cntfrq_get(void);
> extern void cntv_tval_set(unsigned int v), cntv_ctl_set(unsigned int v);
> extern void irq_enable(void);
> extern int cnintr(void);	/* console interrupt (board console driver) */
> extern int cn_irq;		/* console GIC INTID, set by the console driver */
> extern int bdintr(void);	/* block-device interrupt (board block driver) */
> extern int bd_irq;		/* block-device GIC INTID, set by the driver */
> static unsigned int timer_reload;
> int irq_ready;
> caddr_t waitloc;	/* pc of the idle wait, for cpu-time accounting */
> void addupc(caddr_t pc, void *prof, int inc) { (void)pc; (void)prof; (void)inc; }
> /*
>  * Real-time clock interrupt: acknowledge the GIC, reprime the timer, and
>  * call the v7 clock() with the trapped pc/ps.  clock() runs with IRQs
>  * masked (we are in the IRQ handler) and never lowers priority, so it is
>  * not re-entrant; preemption happens on return to user via trap()'s tail.
>  */
> void
> clock_irq_handler(int *tf)
> {
> 	unsigned int iar = GICC_IAR;
> 	unsigned int intid = iar & 0x3ff;
> 	if(intid == 1023) return;
> 	if(intid == TIMER_IRQ) {
> 		int mode = tf[16] & 0x1f;
> 		int usermode = (mode == 0x10) || (mode == 0x1f);
> 		cntv_tval_set(timer_reload);
> 		if(u.u_procp != NULL)
> 			clock(0, 0, 0, 0, 0, (caddr_t)tf[15],
> 			    usermode ? 0xf000 : 0);
> 	} else if(cn_irq && intid == (unsigned int)cn_irq)
> 		cnintr();
> 	else if(bd_irq && intid == (unsigned int)bd_irq)
> 		bdintr();
> 	GICC_EOIR = iar;
> }
> void
> clkstart(void)
> {
> 	unsigned int freq, prio_reg, prio_off, prio_val;
> 	freq = cntfrq_get();
> 	if(freq == 0) freq = 62500000U;
> 	timer_reload = freq / TIMER_HZ;
> 	prio_reg = TIMER_IRQ / 4;
> 	prio_off = (TIMER_IRQ % 4) * 8;
> 	prio_val = GICD_IPRIORITYR(prio_reg);
> 	prio_val &= ~(0xffU << prio_off);
> 	prio_val |=  (0x80U << prio_off);
> 	GICD_IPRIORITYR(prio_reg) = prio_val;
> 	GICD_ISENABLER(TIMER_IRQ / 32) = 1U << (TIMER_IRQ % 32);
> 	if(cn_irq) {
> 		prio_reg = cn_irq / 4;
> 		prio_off = (cn_irq % 4) * 8;
> 		prio_val = GICD_IPRIORITYR(prio_reg);
> 		prio_val &= ~(0xffU << prio_off);
> 		prio_val |=  (0x80U << prio_off);
> 		GICD_IPRIORITYR(prio_reg) = prio_val;
> 		GICD_ISENABLER(cn_irq / 32) = 1U << (cn_irq % 32);
> 	}
> 	if(bd_irq) {
> 		prio_reg = bd_irq / 4;
> 		prio_off = (bd_irq % 4) * 8;
> 		prio_val = GICD_IPRIORITYR(prio_reg);
> 		prio_val &= ~(0xffU << prio_off);
> 		prio_val |=  (0x80U << prio_off);
> 		GICD_IPRIORITYR(prio_reg) = prio_val;
> 		GICD_ISENABLER(bd_irq / 32) = 1U << (bd_irq % 32);
> 	}
> 	GICD_CTLR = 1;
> 	GICC_PMR  = 0xff;
> 	GICC_CTLR = 1;
> 	cntv_tval_set(timer_reload);
> 	cntv_ctl_set(1);
> 	irq_ready = 1;
> 	irq_enable();
```

### usr/sys/h/seg.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/seg.h unix-v7-c99/usr/sys/h/seg.h || true
```

Expect:

```
2c2
<  * KT-11 addresses and bits.
---
>  * ARM user address layout and software segment bits.
5,7d4
< #define	UISD	((physadr)0177600)	/* first user I-space descriptor register */
< #define	UISA	((physadr)0177640)	/* first user I-space address register */
< #define	UDSA	((physadr)0177660)	/* first user D-space address register */
15,16c12,14
<  * structure used to address
<  * a sequence of integers.
---
>  * Physical memory layout (KERNBASE, COREBASE, CORETOP) is board-specific and
>  * comes from conf/<board>/memmap.h, selected by the Makefile -I path -- so the
>  * kernel sources are identical across boards (no conditional compilation).
18c16
< physadr	ka6;		/* 11/40 KISA6; 11/45 KDSA6 */
---
> #include "memmap.h"
21c19
<  * address to access 11/70 UNIBUS map
---
>  * User virtual memory layout.
23c21,61
< #define	UBMAP	((physadr)0170200)
---
> #define USERBASE	0x00000000U
> #define USERSIZE	0x00100000U	/* 1 MB user virtual window (VA 0..) */
> #define UENTRY		0x00000010U
> #define USTACK		0x000f0000U
> #define UARGV		0x0000f000U
> #define UARGLEN		3072
> #define UENTRY_SIGTRAMP	0x0000fe00U
> /*
>  * Physical core window.  The kernel maps KERNBASE..CORETOP as 1 MB
>  * sections (PA==VA), so all of physical core below CORETOP is directly
>  * addressable by the kernel.  Process images are allocated from coremap as
>  * "clicks" (64 bytes) within [COREBASE, CORETOP); click c is at CLKADDR(c).
>  * Click 0 is reserved (malloc returns 0 to mean "no core").
>  */
> #define NCLICK		((CORETOP-COREBASE)>>6)		/* clicks of user core */
> #define CLKADDR(c)	((char *)(COREBASE + ((unsigned)(c) << 6)))
> /*
>  * Section/page attributes.  Normal memory (kernel, user, DDR) is Normal
>  * Write-Back/Write-Allocate, shareable -- CACHED (TEX=001,C=1,B=1,S=1) -- so
>  * the CPU runs at full speed instead of stalling on every uncached access.
>  * Device memory (MMIO) stays strongly ordered.  mmu_on() enables the L1
>  * I/D caches; resume() invalidates the I-cache on context switch because the
>  * per-process user region shares VA 0 (VIPT I-cache aliasing); DMA buffers
>  * are flushed by the block driver (dcflush) on cache-incoherent hardware.
>  */
> #define SEC_KERN	0x0001140eU	/* L1 1 MB section, kernel rw, cached */
> #define SEC_DEV		0x00000c02U	/* L1 1 MB section, device (uncached) */
> #define PTE_PT		0x00000001U	/* L1 entry -> L2 coarse table */
> #define PG_RW		0x0000047eU	/* L2 small page, PL0 read/write, cached */
> #define PG_RO		0x0000046eU	/* L2 small page, PL0 read-only, cached */
> #define PG_KRW		0x0000045eU	/* L2 small page, kernel-only rw, cached */
> #define PGSHIFT		12
> #define PGSIZE		0x1000U
> /*
>  * Physical memory map, one entry per [start,end) 1 MB-section range with its
>  * L1 attribute (SEC_KERN cached, SEC_DEV device).  The board file supplies a
>  * board_map[] terminated by a zero entry; machine_init() (machdep.c) walks it
>  * to build the section table -- identical code on every board, so QEMU
>  * exercises the same machine_init() the MP135 runs.
>  */
> struct memregion { unsigned int start, end, attr; };
```

### usr/sys/dev/mem.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/mem.c unix-v7-c99/usr/sys/dev/mem.c || true
```

Expect:

```
15,16c15,17
< #include "../h/conf.h"
< #include "../h/seg.h"
---
> int passc(int c);
> int cpass(void);
> int arm_mem_read(unsigned int off, char *buf, unsigned int n);
18c19,20
< mmread(dev)
---
> int
> mmread(dev_t dev)
20,21c22,24
< 	register c, bn, on;
< 	int a, d;
---
> 	register int c;
> 	char buf[64];
> 	unsigned int n, off;
24c27
< 		return;
---
> 		return(0);
26,40c29,41
< 		bn = u.u_offset >> 6;
< 		on = u.u_offset & 077;
< 		a = UISA->r[0];
< 		d = UISD->r[0];
< 		spl7();
< 		UISA->r[0] = bn;
< 		UISD->r[0] = 077406;
< 		if(minor(dev) == 1)
< 			UISA->r[0] = (ka6-6)->r[(bn>>7)&07] + (bn & 0177);
< 		if ((c = fuibyte((caddr_t)on)) < 0)
< 			u.u_error = ENXIO;
< 		UISA->r[0] = a;
< 		UISD->r[0] = d;
< 		spl0();
< 	} while(u.u_error==0 && passc(c)>=0);
---
> 		off = (unsigned int)u.u_offset;
> 		n = u.u_count;
> 		if(n > sizeof(buf))
> 			n = sizeof(buf);
> 		if(arm_mem_read(off, buf, n) <= 0)
> 			break;
> 		for(unsigned int i = 0; i < n; i++) {
> 			c = buf[i];
> 			if(passc(c) < 0 || u.u_error != 0)
> 				return(0);
> 		}
> 	} while(u.u_count != 0 && u.u_error == 0);
> 	return(0);
43c44,45
< mmwrite(dev)
---
> int
> mmwrite(dev_t dev)
45,46c47
< 	register c, bn, on;
< 	int a, d;
---
> 	register int c;
50c51
< 		return;
---
> 		return(0);
53,55c54
< 		bn = u.u_offset >> 6;
< 		on = u.u_offset & 077;
< 		if ((c=cpass())<0 || u.u_error!=0)
---
> 		if((c = cpass()) < 0 || u.u_error != 0)
57,68c56
< 		a = UISA->r[0];
< 		d = UISD->r[0];
< 		spl7();
< 		UISA->r[0] = bn;
< 		UISD->r[0] = 077406;
< 		if(minor(dev) == 1)
< 			UISA->r[0] = (ka6-6)->r[(bn>>7)&07] + (bn & 0177);
< 		if (suibyte((caddr_t)on, c) < 0)
< 			u.u_error = ENXIO;
< 		UISA->r[0] = a;
< 		UISD->r[0] = d;
< 		spl0();
---
> 		*(char *)(unsigned int)(u.u_offset-1) = c;
69a58
> 	return(0);
```

### usr/sys/sys/prim.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/prim.c unix-v7-c99/usr/sys/sys/prim.c || true
```

Expect:

```
5a6,7
> int intr_disable(void);
> void intr_restore(int s);
19,20c21,22
< getc(p)
< register struct clist *p;
---
> int
> getc(register struct clist *p)
25c27
< 	s = spl6();
---
> 	s = intr_disable();
47c49
< 	splx(s);
---
> 	intr_restore(s);
55,57c57,58
< q_to_b(q, cp, cc)
< register struct clist *q;
< register char *cp;
---
> int
> q_to_b(register struct clist *q, register char *cp, int cc)
65c66
< 	s = spl6();
---
> 	s = intr_disable();
92c93
< 	splx(s);
---
> 	intr_restore(s);
102,103c103,104
< ndqb(q, flag)
< register struct clist *q;
---
> int
> ndqb(register struct clist *q, int flag)
105c106
< register cc;
---
> register int cc;
108c109
< 	s = spl6();
---
> 	s = intr_disable();
133c134
< 	splx(s);
---
> 	intr_restore(s);
143,145c144,145
< ndflush(q, cc)
< register struct clist *q;
< register cc;
---
> void
> ndflush(register struct clist *q, register int cc)
147c147
< register s;
---
> register int s;
149c149
< 	s = spl6();
---
> 	s = intr_disable();
189c189
< 	splx(s);
---
> 	intr_restore(s);
191,192c191,192
< putc(c, p)
< register struct clist *p;
---
> int
> putc(int c, register struct clist *p)
196c196
< 	register s;
---
> 	register int s;
198c198
< 	s = spl6();
---
> 	s = intr_disable();
201c201
< 			splx(s);
---
> 			intr_restore(s);
210c210
< 			splx(s);
---
> 			intr_restore(s);
221c221
< 	splx(s);
---
> 	intr_restore(s);
231,234c231,232
< b_to_q(cp, cc, q)
< register char *cp;
< struct clist *q;
< register int cc;
---
> int
> b_to_q(register char *cp, register int cc, struct clist *q)
238c236
< 	register s, acc;
---
> 	register int s, acc;
245c243
< 	s = spl6();
---
> 	s = intr_disable();
270c268
< 	splx(s);
---
> 	intr_restore(s);
278c276,277
< cinit()
---
> void
> cinit(void)
301,302c300,301
< getw(p)
< register struct clist *p;
---
> int
> getw(register struct clist *p)
312,313c311,312
< putw(c, p)
< register struct clist *p;
---
> int
> putw(int c, register struct clist *p)
315c314
< 	register s;
---
> 	register int s;
317c316
< 	s = spl6();
---
> 	s = intr_disable();
319c318
< 		splx(s);
---
> 		intr_restore(s);
324c323
< 	splx(s);
---
> 	intr_restore(s);
```

### usr/sys/dev/tty.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/tty.c unix-v7-c99/usr/sys/dev/tty.c || true
```

Expect:

```
11d10
< #include "../h/mx.h"
17c16
< char	partab[];
---
> extern char	partab[];
18a18,47
> int intr_enable(void);
> int intr_disable(void);
> void intr_restore(int s);
> int getc(struct clist *p);
> int putc(int c, struct clist *p);
> int b_to_q(char *cp, int cc, struct clist *q);
> void sleep(caddr_t chan, int pri);
> void wakeup(caddr_t chan);
> void signal(int pgrp, int sig);
> int copyin(caddr_t f, caddr_t t, unsigned int n);
> int copyout(caddr_t f, caddr_t t, unsigned int n);
> unsigned max(unsigned a, unsigned b);
> void ttyopen(dev_t dev, struct tty *tp);
> void ttychars(struct tty *tp);
> void ttyclose(struct tty *tp);
> void stty(void);
> void gtty(void);
> void ioctl(void);
> int ttioccomm(int com, struct tty *tp, caddr_t addr, dev_t dev);
> void wflushtty(struct tty *tp);
> void flushtty(struct tty *tp);
> int canon(struct tty *tp);
> void ttyrend(struct tty *tp, char *pb, char *pe);
> void ttyinput(int c, struct tty *tp);
> void ttyblock(struct tty *tp);
> void ttyoutput(int c, struct tty *tp);
> int ttrstrt(struct tty *tp);
> void ttstart(struct tty *tp);
> int ttread(struct tty *tp);
> caddr_t ttwrite(struct tty *tp);
61,63c90,91
< ttyopen(dev, tp)
< dev_t dev;
< register struct tty *tp;
---
> void
> ttyopen(dev_t dev, register struct tty *tp)
84,85c112,113
< ttychars(tp)
< register struct tty *tp;
---
> void
> ttychars(register struct tty *tp)
100,101c128,129
< ttyclose(tp)
< register struct tty *tp;
---
> void
> ttyclose(register struct tty *tp)
112c140,141
< stty()
---
> void
> stty(void)
119c148,149
< gtty()
---
> void
> gtty(void)
131c161,162
< ioctl()
---
> void
> ioctl(void)
141c172
< 	register fmt;
---
> 	register int fmt;
167,169c198,199
< ttioccomm(com, tp, addr, dev)
< register struct tty *tp;
< caddr_t addr;
---
> int
> ttioccomm(int com, register struct tty *tp, caddr_t addr, dev_t dev)
194c224
< 		if (t >= nldisp) {
---
> 		if (t >= (unsigned)nldisp) {
199c229
< 			(*linesw[tp->t_line].l_close)(tp);
---
> 			(*linesw[(int)tp->t_line].l_close)(tp);
220a251
> 		/* fallthrough */
263c294
< 		(*linesw[tp->t_line].l_ioctl)(com, tp, addr);
---
> 		(*linesw[(int)tp->t_line].l_ioctl)(com, tp, addr);
288,289c319,320
< wflushtty(tp)
< register struct tty *tp;
---
> void
> wflushtty(register struct tty *tp)
292c323
< 	spl5();
---
> 	intr_disable();
299c330
< 	spl0();
---
> 	intr_enable();
305,306c336,337
< flushtty(tp)
< register struct tty *tp;
---
> void
> flushtty(register struct tty *tp)
308c339
< 	register s;
---
> 	register int s;
314c345
< 	s = spl6();
---
> 	s = intr_disable();
322c353
< 	splx(s);
---
> 	intr_restore(s);
333,334c364,365
< canon(tp)
< register struct tty *tp;
---
> int
> canon(register struct tty *tp)
341,344c372,375
< 	spl5();
< 	while ((tp->t_flags&(RAW|CBREAK))==0 && tp->t_delct==0
< 	    || (tp->t_flags&(RAW|CBREAK))!=0 && tp->t_rawq.c_cc==0) {
< 		if ((tp->t_state&CARR_ON)==0 || tp->t_chan!=NULL) {
---
> 	intr_disable();
> 	while (((tp->t_flags&(RAW|CBREAK))==0 && tp->t_delct==0)
> 	    || ((tp->t_flags&(RAW|CBREAK))!=0 && tp->t_rawq.c_cc==0)) {
> 		if ((tp->t_state&CARR_ON)==0) {
349c380
< 	spl0();
---
> 	intr_enable();
401,403c432,433
< ttyrend(tp, pb, pe)
< register struct tty *tp;
< register char *pb, *pe;
---
> void
> ttyrend(register struct tty *tp, register char *pb, register char *pe)
410,412c440
< 		if (tp->t_chan)
< 			sdata(tp->t_chan); else
< 			wakeup((caddr_t)&tp->t_rawq);
---
> 		wakeup((caddr_t)&tp->t_rawq);
430,432c458,459
< ttyinput(c, tp)
< register c;
< register struct tty *tp;
---
> void
> ttyinput(register int c, register struct tty *tp)
435d461
< 	register struct chan *cp;
466,469c492
< 			if (tp->t_chan)
< 				scontrol(tp->t_chan, M_SIG, c);
< 			else
< 				signal(tp->t_pgrp, c);
---
> 			signal(tp->t_pgrp, c);
485,487c508
< 		if ((cp=tp->t_chan)!=NULL)
< 			sdata(cp); else
< 			wakeup((caddr_t)&tp->t_rawq);
---
> 		wakeup((caddr_t)&tp->t_rawq);
501,502c522,523
< ttyblock(tp)
< register struct tty *tp;
---
> void
> ttyblock(register struct tty *tp)
504c525
< register x;
---
> register int x;
526,528c547,548
< ttyoutput(c, tp)
< register c;
< register struct tty *tp;
---
> void
> ttyoutput(register int c, register struct tty *tp)
531c551
< 	register ctype;
---
> 	register int ctype;
595a616
> 		/* fallthrough */
658,659c679,680
< ttrstrt(tp)
< register struct tty *tp;
---
> int
> ttrstrt(register struct tty *tp)
663a685
> 	return(0);
672,673c694,695
< ttstart(tp)
< register struct tty *tp;
---
> void
> ttstart(register struct tty *tp)
675c697
< 	register s;
---
> 	register int s;
677c699
< 	s = spl5();
---
> 	s = intr_disable();
680c702
< 	splx(s);
---
> 	intr_restore(s);
687,688c709,710
< ttread(tp)
< register struct tty *tp;
---
> int
> ttread(register struct tty *tp)
704,705c726
< ttwrite(tp)
< register struct tty *tp;
---
> ttwrite(register struct tty *tp)
707c728
< 	register c;
---
> 	register int c;
712c733
< 		spl5();
---
> 		intr_disable();
716,717d736
< 			if (tp->t_chan) 
< 				return((caddr_t)&tp->t_outq);
720c739
< 		spl0();
---
> 		intr_enable();
```

### usr/sys/dev/partab.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/partab.c unix-v7-c99/usr/sys/dev/partab.c || true
```

Expect:

```

```
diff unix-v7-c99/v7/usr/sys/dev/sys.c unix-v7-c99/usr/sys/dev/sys.c || true
```

Expect:

```
11c11,12
< syopen(dev, flag)
---
> int
> syopen(dev_t dev, int flag)
13a15
> 	(void)dev;
16c18
< 		return;
---
> 		return(0);
18a21
> 	return(0);
21c24,25
< syread(dev)
---
> int
> syread(dev_t dev)
23a28
> 	(void)dev;
24a30
> 	return(0);
27c33,34
< sywrite(dev)
---
> int
> sywrite(dev_t dev)
29a37
> 	(void)dev;
30a39
> 	return(0);
33,34c42,43
< sysioctl(dev, cmd, addr, flag)
< caddr_t addr;
---
> int
> sysioctl(dev_t dev, int cmd, caddr_t addr, int flag)
36a46
> 	(void)dev;
37a48
> 	return(0);
```

### usr/sys/sys/sys4.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/sys4.c unix-v7-c99/usr/sys/sys/sys4.c || true
```

Expect:

```
5d4
< #include "../h/reg.h"
8a8,36
> int intr_enable(void);
> int intr_disable(void);
> void chdirec(struct inode **ipp);
> void sleep(caddr_t chan, int pri);
> void sysacct(void);
> void stat(void);
> void saccess(void);
> void link(void);
> void mknod(void);
> void smount(void);
> void sumount(void);
> struct inode *iget(dev_t dev, ino_t ino);
> void iput(struct inode *ip);
> void umask(void);
> void getuid(void);
> void getgid(void);
> void getpid(void);
> void setuid(void);
> void setgid(void);
> void sync(void);
> void nice(void);
> void gtime(void);
> void stime(void);
> void alarm(void);
> void ftime(void);
> void times(void);
> void profil(void);
> void syslock(void);
> extern struct inode *rootdir;
17c45,46
< gtime()
---
> void
> gtime(void)
26c55,56
< ftime()
---
> void
> ftime(void)
35c65
< 	spl7();
---
> 	intr_disable();
38c68
< 	spl0();
---
> 	intr_enable();
53c83,84
< stime()
---
> void
> stime(void)
64c95,96
< setuid()
---
> void
> setuid(void)
66c98
< 	register uid;
---
> 	register int uid;
80c112,113
< getuid()
---
> void
> getuid(void)
87c120,121
< setgid()
---
> void
> setgid(void)
89c123
< 	register gid;
---
> 	register int gid;
102c136,137
< getgid()
---
> void
> getgid(void)
109c144,145
< getpid()
---
> void
> getpid(void)
115c151,152
< sync()
---
> void
> sync(void)
121c158,159
< nice()
---
> void
> nice(void)
123c161
< 	register n;
---
> 	register int n;
145c183,184
< unlink()
---
> void
> unlink(void)
194c233,234
< chdir()
---
> void
> chdir(void)
199c239,240
< chroot()
---
> void
> chroot(void)
205,206c246,247
< chdirec(ipp)
< register struct inode **ipp;
---
> void
> chdirec(register struct inode **ipp)
234c275,276
< chmod()
---
> void
> chmod(void)
255c297,298
< chown()
---
> void
> chown(void)
273c316,317
< ssig()
---
> void
> ssig(void)
275c319
< 	register a;
---
> 	register int a;
292c336,337
< kill()
---
> void
> kill(void)
295c340
< 	register a;
---
> 	register int a;
327c372,373
< times()
---
> void
> times(void)
338c384,385
< profil()
---
> void
> profil(void)
357c404,405
< alarm()
---
> void
> alarm(void)
360c408
< 	register c;
---
> 	register int c;
376c424,425
< pause()
---
> void
> pause(void)
386c435,436
< umask()
---
> void
> umask(void)
391c441
< 	register t;
---
> 	register int t;
403c453,454
< utime()
---
> void
> utime(void)
```

### usr/sys/dev/bio.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/dev/bio.c unix-v7-c99/usr/sys/dev/bio.c || true
```

Expect:

```
8a9,21
> void brelse(struct buf *bp);
> void bawrite(register struct buf *bp);
> void iowait(struct buf *bp);
> void notavail(struct buf *bp);
> void geterror(struct buf *bp);
> int incore(dev_t dev, daddr_t blkno);
> void wakeup(caddr_t chan);
> void sleep(caddr_t chan, int pri);
> int intr_enable(void);
> int intr_disable(void);
> void intr_restore(int s);
> void panic(char *s);
> void mapfree(struct buf *bp);
56,58c69
< bread(dev, blkno)
< dev_t dev;
< daddr_t blkno;
---
> bread(dev_t dev, daddr_t blkno)
84,86c95
< breada(dev, blkno, rablkno)
< dev_t dev;
< daddr_t blkno, rablkno;
---
> breada(dev_t dev, daddr_t blkno, daddr_t rablkno)
125,126c134,135
< bwrite(bp)
< register struct buf *bp;
---
> void
> bwrite(struct buf *bp)
128c137
< 	register flag;
---
> 	register int flag;
154,155c163,164
< bdwrite(bp)
< register struct buf *bp;
---
> void
> bdwrite(struct buf *bp)
171,172c180,181
< bawrite(bp)
< register struct buf *bp;
---
> void
> bawrite(register struct buf *bp)
182,183c191,192
< brelse(bp)
< register struct buf *bp;
---
> void
> brelse(struct buf *bp)
186c195
< 	register s;
---
> 	register int s;
196c205
< 	s = spl6();
---
> 	s = intr_disable();
211c220
< 	splx(s);
---
> 	intr_restore(s);
218,220c227,228
< incore(dev, blkno)
< dev_t dev;
< daddr_t blkno;
---
> int
> incore(dev_t dev, daddr_t blkno)
238,240c246
< getblk(dev, blkno)
< dev_t dev;
< daddr_t blkno;
---
> getblk(dev_t dev, daddr_t blkno)
245c251
< 	register i;
---
> 	register int i;
252c258
< 	spl0();
---
> 	intr_enable();
259c265
< 		spl6();
---
> 		intr_disable();
265c271,272
< 		spl0();
---
> 		notavail(bp);
> 		intr_enable();
276d282
< 		notavail(bp);
279c285
< 	spl6();
---
> 	intr_disable();
285,286c291,293
< 	spl0();
< 	notavail(bp = bfreelist.av_forw);
---
> 	bp = bfreelist.av_forw;
> 	notavail(bp);
> 	intr_enable();
309c316
< geteblk()
---
> geteblk(void)
315c322
< 	spl6();
---
> 	intr_disable();
320d326
< 	spl0();
322c328,330
< 	notavail(bp = bfreelist.av_forw);
---
> 	bp = bfreelist.av_forw;
> 	notavail(bp);
> 	intr_enable();
343,344c351,352
< iowait(bp)
< register struct buf *bp;
---
> void
> iowait(struct buf *bp)
347c355
< 	spl6();
---
> 	intr_disable();
350c358
< 	spl0();
---
> 	intr_enable();
358,359c366,367
< notavail(bp)
< register struct buf *bp;
---
> void
> notavail(struct buf *bp)
361c369
< 	register s;
---
> 	register int s;
363c371
< 	s = spl6();
---
> 	s = intr_disable();
367c375
< 	splx(s);
---
> 	intr_restore(s);
374,375c382,383
< iodone(bp)
< register struct buf *bp;
---
> void
> iodone(struct buf *bp)
392,393c400,401
< clrbuf(bp)
< struct buf *bp;
---
> void
> clrbuf(struct buf *bp)
395,396c403,404
< 	register *p;
< 	register c;
---
> 	register int *p;
> 	register int c;
409,410c417,418
< swap(blkno, coreaddr, count, rdflg)
< register count;
---
> void
> swap(daddr_t blkno, int coreaddr, int count, int rdflg)
413c421
< 	register tcount;
---
> 	register int tcount;
419c427
< 	spl6();
---
> 	intr_disable();
435c443
< 		spl6();
---
> 		intr_disable();
444c452
< 	spl0();
---
> 	intr_enable();
456,457c464,465
< bflush(dev)
< dev_t dev;
---
> void
> bflush(dev_t dev)
462c470
< 	spl6();
---
> 	intr_disable();
471c479
< 	spl0();
---
> 	intr_enable();
484,486c492,493
< physio(strat, bp, dev, rw)
< register struct buf *bp;
< int (*strat)();
---
> void
> physio(void (*strat)(struct buf *), register struct buf *bp, dev_t dev, int rw)
515c522
< 	    && nb < 1024-u.u_ssize)
---
> 	    && (unsigned)nb < 1024-u.u_ssize)
517c524
< 	spl6();
---
> 	intr_disable();
528c535
< 	ts = (u.u_sep? UDSA: UISA)->r[nb>>7] + (nb&0177);
---
> 	ts = (u.u_sep? &u.u_uisa[8]: &u.u_uisa[0])[nb>>7] + (nb&0177);
536c543
< 	spl6();
---
> 	intr_disable();
542,543c549,550
< 	spl0();
< 	bp->b_flags &= ~(B_BUSY|B_WANTED);
---
> 	intr_enable();
> 	bp->b_flags &= ~(B_BUSY|B_WANTED|B_PHYS);
557,558c564,565
< geterror(bp)
< register struct buf *bp;
---
> void
> geterror(struct buf *bp)
```

### usr/src/cmd/diff3.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/diff3.c unix-v7-c99/usr/src/cmd/diff3.c || true
```

Expect:

```
45,46c45,55
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
> int
> main(int argc, char **argv)
48c57
< 	register i,m,n;
---
> 	register int i,m,n;
74a84
> 	return(0);
85,87c95,96
< readin(name,dd)
< char *name;
< struct diff *dd;
---
> int
> readin(char *name, struct diff *dd)
89c98
< 	register i;
---
> 	register int i;
128,129c137,138
< number(lc)
< char **lc;
---
> int
> number(char **lc)
131c140
< 	register nn;
---
> 	register int nn;
138c147,148
< digit(c)
---
> int
> digit(int c)
143,144c153,154
< getchange(b)
< FILE *b;
---
> int
> getchange(FILE *b)
152,153c162,163
< getline(b)
< FILE *b;
---
> int
> getline(FILE *b)
155,156c165,166
< 	register i, c;
< 	for(i=0;i<sizeof(line)-1;i++) {
---
> 	register int i, c;
> 	for(i=0;i<(int)sizeof(line)-1;i++) {
169c179,180
< merge(m1,m2)
---
> int
> merge(int m1, int m2)
187c198
< 		if(!t2||t1&&d1->new.to < d2->new.from) {
---
> 		if(!t2 || (t1 && d1->new.to < d2->new.from)) {
199c210
< 		if(!t1||t2&&d2->new.to < d1->new.from) {
---
> 		if(!t1 || (t2 && d2->new.to < d1->new.from)) {
265a277
> 	return(0);
268,269c280,281
< separate(s)
< char *s;
---
> int
> separate(char *s)
271a284
> 	return(0);
278,279c291,292
< change(i,rold,dup)
< struct range *rold;
---
> int
> change(int i, struct range *rold, int dup)
285c298
< 		return;
---
> 		return(0);
287c300
< 		return;
---
> 		return(0);
290a304
> 	return(0);
296,297c310,311
< prange(rold)
< struct range *rold;
---
> int
> prange(struct range *rold)
306a321
> 	return(0);
314,315c329,330
< keep(i,rold,rnew)
< struct range *rold, *rnew;
---
> int
> keep(int i, struct range *rold, struct range *rnew)
317c332
< 	register delta;
---
> 	register int delta;
318a334
> 	(void)rold;
322a339
> 	return(0);
329,330c346,347
< skip(i,from,pr)
< char *pr;
---
> int
> skip(int i, int from, char *pr)
332c349
< 	register j,n;
---
> 	register int j,n;
347,348c364,365
< duplicate(r1,r2)
< struct range *r1, *r2;
---
> int
> duplicate(struct range *r1, struct range *r2)
350,351c367,368
< 	register c,d;
< 	register nchar;
---
> 	register int c,d;
> 	register int nchar;
367c384
< 				return;
---
> 				return(0);
375c392,393
< repos(nchar)
---
> int
> repos(int nchar)
377c395
< 	register i;
---
> 	register int i;
379a398
> 	return(0);
382c401,402
< trouble()
---
> int
> trouble(void)
385a406
> 	return(0);
390,391c411,412
< edit(diff,dup,j)
< struct diff *diff;
---
> int
> edit(struct diff *diff, int dup, int j)
406c427,428
< edscript(n)
---
> int
> edscript(int n)
408c430
< 	register j,k;
---
> 	register int j,k;
420a443
> 	return(0);
```

### usr/src/cmd/at.c

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/at.c unix-v7-c99/usr/src/cmd/at.c || true
```

Expect:

```
10a11
> #define	utime	at_utime
55c56
< char	*prefix();
---
> char	*prefix(char *begin, char *full);
58,59c59,64
< main(argc, argv)
< char **argv;
---
> int	pclose(FILE *ptr);
> int	makeutime(char *pp), makeuday(int argc, char **argv);
> int	filename(char *dir, int y, int d, int t);
> int	onintr(int sig);
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
92,93c96,97
< 	if (signal(SIGINT, SIG_IGN) != SIG_IGN)
< 		signal(SIGINT, onintr);
---
> 	if ((int (*)())signal(SIGINT, (int)SIG_IGN) != (int (*)())SIG_IGN)
> 		signal(SIGINT, (int)onintr);
100,105c104,106
< 	if ((pwfil = popen("pwd", "r")) == NULL) {
< 		fprintf(stderr, "at: can't execute pwd\n");
< 		exit(1);
< 	}
< 	fgets(pwbuf, 100, pwfil);
< 	pclose(pwfil);
---
> 	pwbuf[0] = '/';
> 	pwbuf[1] = '\n';
> 	pwbuf[2] = 0;
118,119c119,120
< makeutime(pp)
< char *pp; 
---
> int
> makeutime(char *pp)
121c122
< 	register val;
---
> 	register int val;
127c128
< 	while(isdigit(*p)) {
---
> 	while(isdigit((unsigned char)*p)) {
138,139c139,140
< 			if (isdigit(*p)) {
< 				if (isdigit(p[1])) {
---
> 			if (isdigit((unsigned char)*p)) {
> 				if (isdigit((unsigned char)p[1])) {
197a199
> 	return(0);
201,202c203,204
< makeuday(argc,argv)
< char **argv;
---
> int
> makeuday(int argc, char **argv)
273,274c275
< prefix(begin, full)
< char *begin, *full;
---
> prefix(char *begin, char *full)
277c278
< 	while (c = *begin++) {
---
> 	while ((c = *begin++)) {
288,289c289,290
< filename(dir, y, d, t)
< char *dir;
---
> int
> filename(char *dir, int y, int d, int t)
291c292
< 	register i;
---
> 	register int i;
297c298
< 			return;
---
> 			return(0);
301c302,303
< onintr()
---
> int
> onintr(int sig)
302a305
> 	(void)sig;
304a308
> 	return(0);
```

### usr/src/libc/nlist.c

Local test:

```
diff unix-v7-c99/v7/usr/src/libc/gen/nlist.c unix-v7-c99/usr/src/libc/nlist.c || true
```

Expect:

```
2,3d1
< int a_magic[] = {A_MAGIC1, A_MAGIC2, A_MAGIC3, A_MAGIC4, 0};
< #define SPACE 100		/* number of symbols read at a time */
5,7c3,49
< nlist(name, list)
< char *name;
< struct nlist *list;
---
> int	open(char *, int);
> int	close(int);
> int	read(int, char *, int);
> long	lseek(int, long, int);
> #define	ELF_NIDENT	16
> #define	ELFMAG0		0177
> #define	SHT_SYMTAB	2
> #define	SHF_WRITE	1
> #define	SHF_EXECINSTR	4
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
> struct elfsym {
> 	unsigned int	st_name;
> 	unsigned int	st_value;
> 	unsigned int	st_size;
> 	unsigned char	st_info;
> 	unsigned char	st_other;
> 	unsigned short	st_shndx;
> };
> static int
> readn(int fd, char *buf, int n)
9,13c51,92
< 	register struct nlist *p, *q;
< 	int f, n, m, i;
< 	long sa;
< 	struct exec buf;
< 	struct nlist space[SPACE];
---
> 	int nr, total;
> 	total = 0;
> 	while(total < n) {
> 		nr = read(fd, buf + total, n - total);
> 		if(nr <= 0)
> 			return(total);
> 		total += nr;
> 	}
> 	return(total);
> }
> static int
> readstr(int fd, char *buf, int n)
> {
> 	int nr, total;
> 	char c;
> 	total = 0;
> 	while(total < n - 1) {
> 		nr = read(fd, &c, 1);
> 		if(nr <= 0)
> 			break;
> 		buf[total++] = c;
> 		if(c == '\0')
> 			return(total);
> 	}
> 	buf[total] = '\0';
> 	return(total);
> }
> int
> nlist(char *name, struct nlist *list)
> {
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
22,25c101,103
< 	read(f, (char *)&buf, sizeof buf);
< 	for(i=0; a_magic[i]; i++)
< 		if(a_magic[i] == buf.a_magic) break;
< 	if(a_magic[i] == 0){
---
> 	if(readn(f, (char *)&eh, sizeof(eh)) != sizeof(eh)
> 	    || eh.e_ident[0] != ELFMAG0 || eh.e_ident[1] != 'E'
> 	    || eh.e_ident[2] != 'L' || eh.e_ident[3] != 'F') {
29,33c107,110
< 	sa = buf.a_text + (long)buf.a_data;
< 	if(buf.a_flag != 1) sa *= 2;
< 	sa += sizeof buf;
< 	lseek(f, sa, 0);
< 	n = buf.a_syms;
---
> 	symoff = 0;
> 	symsz = 0;
> 	symesz = sizeof(sym);
> 	stroff = 0;
35,48c112,127
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
---
> 	for(i = 0; i < eh.e_shnum && i < 64; i++) {
> 		lseek(f, (long)(eh.e_shoff + i * eh.e_shentsize), 0);
> 		if(readn(f, (char *)&sh, sizeof(sh)) != sizeof(sh)) {
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
> 			if(readn(f, (char *)&sh, sizeof(sh)) != sizeof(sh)) {
> 				close(f);
> 				return(-1);
49a129,174
> 			stroff = sh.sh_offset;
> 		}
> 	}
> 	if(symoff == 0 || stroff == 0) {
> 		close(f);
> 		return(-1);
> 	}
> 	nsyms = (int)(symsz / symesz);
> 	for(i = 0; i < nsyms; i++) {
> 		lseek(f, (long)(symoff + i * symesz), 0);
> 		if(readn(f, (char *)&sym, sizeof(sym)) != sizeof(sym)) {
> 			close(f);
> 			return(-1);
> 		}
> 		if(sym.st_name == 0)
> 			continue;
> 		lseek(f, (long)(stroff + sym.st_name), 0);
> 		k = readstr(f, strbuf, sizeof(strbuf));
> 		if(k <= 0) {
> 			close(f);
> 			return(-1);
> 		}
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

### usr/sys/sys/slp.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/slp.c unix-v7-c99/usr/sys/sys/slp.c || true
```

Expect:

```
10a11,41
> #include "../h/seg.h"
> #include "../h/reg.h"
> void sleep(caddr_t chan, int pri);
> void wakeup(caddr_t chan);
> void setrq(struct proc *p);
> void setrun(struct proc *p);
> int setpri(struct proc *pp);
> void sched(void);
> int swapin(struct proc *p);
> void qswtch(void);
> void swtch(void);
> int newproc(void);
> void expand(int newsize);
> int issig(void);
> int intr_enable(void);
> int intr_disable(void);
> void intr_restore(int s);
> void panic(char *s);
> void printf(char *fmt, ...);
> int save(int *lp) __attribute__((returns_twice));
> void resume(int addr, int *lp);
> void sureg(void);
> void savfp(void *p);
> void idle(void);
> int malloc(struct map *mp, int size);
> void mfree(struct map *mp, int size, int a);
> void xswap(struct proc *p, int ff, int os);
> void xlock(struct text *xp);
> void xunlock(struct text *xp);
> void swap(daddr_t blkno, int coreaddr, int count, int rdflg);
> void copyseg(int from, int to);
13a45
> #define ARM_FORK_STACK_COPY 1024	/* fallback high-stack band */
27,28c59,60
< sleep(chan, pri)
< caddr_t chan;
---
> void
> sleep(caddr_t chan, int pri)
31c63
< 	register s, h;
---
> 	register int s, h;
34c66
< 	s = spl6();
---
> 	s = intr_disable();
50c82
< 			spl0();
---
> 			intr_enable();
53c85
< 		spl0();
---
> 		intr_enable();
62c94
< 		spl0();
---
> 		intr_enable();
65c97
< 	splx(s);
---
> 	intr_restore(s);
82,83c114,115
< wakeup(chan)
< register caddr_t chan;
---
> void
> wakeup(caddr_t chan)
86c118
< 	register i;
---
> 	register int i;
89c121
< 	s = spl6();
---
> 	s = intr_disable();
109c141
< 	splx(s);
---
> 	intr_restore(s);
118,119c150,151
< setrq(p)
< struct proc *p;
---
> void
> setrq(struct proc *p)
122c154
< 	register s;
---
> 	register int s;
124c156
< 	s = spl6();
---
> 	s = intr_disable();
133c165
< 	splx(s);
---
> 	intr_restore(s);
140,141c172,173
< setrun(p)
< register struct proc *p;
---
> void
> setrun(struct proc *p)
151c183
< 	if (w = p->p_wchan) {
---
> 	if ((w = p->p_wchan) != 0) {
171,172c203,204
< setpri(pp)
< register struct proc *pp;
---
> int
> setpri(struct proc *pp)
174c206
< 	register p;
---
> 	register int p;
202c234,235
< sched()
---
> void
> sched(void)
205c238
< 	register outage, inage;
---
> 	register int outage, inage;
214c247
< 	spl6();
---
> 	intr_disable();
215a249
> 	p = NULL;
230c264
< 	spl0();
---
> 	intr_enable();
247c281
< 	spl6();
---
> 	intr_disable();
257c291
< 		if (rp->p_stat==SSLEEP&&rp->p_pri>=PZERO || rp->p_stat==SSTOP) {
---
> 		if ((rp->p_stat==SSLEEP&&rp->p_pri>=PZERO) || rp->p_stat==SSTOP) {
269c303
< 	spl0();
---
> 	intr_enable();
281c315
< 	spl6();
---
> 	intr_disable();
292,293c326,327
< swapin(p)
< register struct proc *p;
---
> int
> swapin(struct proc *p)
301c335
< 	if (xp = p->p_textp) {
---
> 	if ((xp = p->p_textp) != 0) {
329c363,364
< qswtch()
---
> void
> qswtch(void)
347c382,383
< swtch()
---
> void
> swtch(void)
349c385
< 	register n;
---
> 	register int n;
380c416
< 	spl6();
---
> 	intr_disable();
383a420
> 	pq = NULL;
412c449
< 	spl0();
---
> 	intr_enable();
426c463,464
< newproc()
---
> int
> newproc(void)
430,431c468,469
< 	register struct proc *rpp, *rip;
< 	register n;
---
> 	struct proc *rpp, *rip;
> 	int n;
447c485
< 		if(rpp->p_stat == NULL && p==NULL)
---
> 		if(rpp->p_stat == 0 && p==NULL)
520c558
< 		 * There is core, so just copy.
---
> 		 * Copy the u-area, live low image, and high stack.
521a560
> 		register int low, stack;
523,524c562,583
< 		while(n--)
< 			copyseg(a1++, a2++);
---
> 		low = (int)u.u_dsize;
> 		stack = (int)u.u_ssize;
> 		if(stack < ARM_FORK_STACK_COPY)
> 			stack = ARM_FORK_STACK_COPY;
> 		stack = USIZE + (int)(USERSIZE >> 6) - stack;
> 		if(u.u_ar0 != NULL) {
> 			unsigned usp;
> 			int spclick;
> 			usp = (unsigned)u.u_ar0[R6];
> 			spclick = USIZE + (int)(usp >> 6);
> 			if(usp < USERSIZE && spclick < stack)
> 				stack = spclick;
> 		}
> 		if(low <= 0 || low > stack - USIZE) {
> 			while(n--)
> 				copyseg(a1++, a2++);
> 		} else {
> 			for(n = 0; n < USIZE + low; n++)
> 				copyseg(a1 + n, a2 + n);
> 			for(n = stack; n < rpp->p_size; n++)
> 				copyseg(a1 + n, a2 + n);
> 		}
545c604,605
< expand(newsize)
---
> void
> expand(int newsize)
547c607
< 	register i, n;
---
> 	register int i, n;
549c609
< 	register a1, a2;
---
> 	register int a1, a2;
550a611,617
> 	/*
> 	 * Armv7: a process image must start on a page boundary because the
> 	 * u-area is mapped as whole pages (UBASE window).  Round the image
> 	 * size up to a multiple of 64 clicks (one 4 KB page) so that coremap
> 	 * allocations stay page-aligned.
> 	 */
> 	newsize = (newsize + 63) & ~63;
```

### usr/sys/sys/sysent.c

Local test:

```
diff unix-v7-c99/v7/usr/sys/sys/sysent.c unix-v7-c99/usr/sys/sys/sysent.c || true
```

Expect:

```
2a3,31
> #include "../h/dir.h"
> #include "../h/user.h"
> #include "../h/proc.h"
> #include "../h/reg.h"
> #include "../h/inode.h"
> #include "../h/file.h"
> #include "../h/tty.h"
> #include "../h/seg.h"
> void nullsys(void), nosys(void);
> void rexit(void), fork(void), read(void), write(void), open(void);
> void close(void), wait(void), creat(void), link(void), unlink(void);
> void exec(void), exece(void), chdir(void), gtime(void), mknod(void);
> void chmod(void), chown(void), sbreak(void), stat(void), seek(void);
> void getpid(void), smount(void), sumount(void), setuid(void), getuid(void);
> void stime(void), ptrace(void), alarm(void), fstat(void), pause(void);
> void utime(void), saccess(void), nice(void), ftime(void), sync(void);
> void kill(void), dup(void), pipe(void), times(void), profil(void);
> void setgid(void), getgid(void), ssig(void), sysacct(void), syslock(void);
> void umask(void), chroot(void), stty(void), gtty(void), ioctl(void);
> void sigreturn(void);
> int issig(void);
> void psig(void);
> void psignal(struct proc *p, int sig);
> int setpri(struct proc *pp);
> void qswtch(void);
> void panic(char *s);
> void printf(char *fmt, ...);
> int save(int *lp) __attribute__((returns_twice));
> void bcopy(char *from, char *to, unsigned int n);
8a38,39
>  * On Armv7 all arguments arrive in registers, so
>  * sy_nrarg == sy_narg for every entry.
10,63d40
< int	alarm();
< int	mpxchan();
< int	chdir();
< int	chmod();
< int	chown();
< int	chroot();
< int	close();
< int	creat();
< int	dup();
< int	exec();
< int	exece();
< int	fork();
< int	fstat();
< int	getgid();
< int	getpid();
< int	getuid();
< int	gtime();
< int	gtty();
< int	ioctl();
< int	kill();
< int	link();
< int	mknod();
< int	nice();
< int	nosys();
< int	nullsys();
< int	open();
< int	pause();
< int	pipe();
< int	profil();
< int	ptrace();
< int	read();
< int	rexit();
< int	saccess();
< int	sbreak();
< int	seek();
< int	setgid();
< int	setuid();
< int	smount();
< int	ssig();
< int	stat();
< int	stime();
< int	stty();
< int	sumount();
< int	ftime();
< int	sync();
< int	sysacct();
< int	syslock();
< int	sysphys();
< int	times();
< int	umask();
< int	unlink();
< int	utime();
< int	wait();
< int	write();
67,130c44,107
< 	0, 0, nullsys,			/*  0 = indir */
< 	1, 1, rexit,			/*  1 = exit */
< 	0, 0, fork,			/*  2 = fork */
< 	3, 1, read,			/*  3 = read */
< 	3, 1, write,			/*  4 = write */
< 	2, 0, open,			/*  5 = open */
< 	1, 1, close,			/*  6 = close */
< 	0, 0, wait,			/*  7 = wait */
< 	2, 0, creat,			/*  8 = creat */
< 	2, 0, link,			/*  9 = link */
< 	1, 0, unlink,			/* 10 = unlink */
< 	2, 0, exec,			/* 11 = exec */
< 	1, 0, chdir,			/* 12 = chdir */
< 	0, 0, gtime,			/* 13 = time */
< 	3, 0, mknod,			/* 14 = mknod */
< 	2, 0, chmod,			/* 15 = chmod */
< 	3, 0, chown,			/* 16 = chown; now 3 args */
< 	1, 0, sbreak,			/* 17 = break */
< 	2, 0, stat,			/* 18 = stat */
< 	4, 1, seek,			/* 19 = seek; now 3 args */
< 	0, 0, getpid,			/* 20 = getpid */
< 	3, 0, smount,			/* 21 = mount */
< 	1, 0, sumount,			/* 22 = umount */
< 	1, 1, setuid,			/* 23 = setuid */
< 	0, 0, getuid,			/* 24 = getuid */
< 	2, 2, stime,			/* 25 = stime */
< 	4, 1, ptrace,			/* 26 = ptrace */
< 	1, 1, alarm,			/* 27 = alarm */
< 	2, 1, fstat,			/* 28 = fstat */
< 	0, 0, pause,			/* 29 = pause */
< 	2, 0, utime,			/* 30 = utime */
< 	2, 1, stty,			/* 31 = stty */
< 	2, 1, gtty,			/* 32 = gtty */
< 	2, 0, saccess,			/* 33 = access */
< 	1, 1, nice,			/* 34 = nice */
< 	1, 0, ftime,			/* 35 = ftime; formerly sleep */
< 	0, 0, sync,			/* 36 = sync */
< 	2, 1, kill,			/* 37 = kill */
< 	0, 0, nullsys,			/* 38 = switch; inoperative */
< 	0, 0, nullsys,			/* 39 = setpgrp (not in yet) */
< 	1, 1, nosys,			/* 40 = tell (obsolete) */
< 	2, 2, dup,			/* 41 = dup */
< 	0, 0, pipe,			/* 42 = pipe */
< 	1, 0, times,			/* 43 = times */
< 	4, 0, profil,			/* 44 = prof */
< 	0, 0, nosys,			/* 45 = unused */
< 	1, 1, setgid,			/* 46 = setgid */
< 	0, 0, getgid,			/* 47 = getgid */
< 	2, 0, ssig,			/* 48 = sig */
< 	0, 0, nosys,			/* 49 = reserved for USG */
< 	0, 0, nosys,			/* 50 = reserved for USG */
< 	1, 0, sysacct,			/* 51 = turn acct off/on */
< 	3, 0, sysphys,			/* 52 = set user physical addresses */
< 	1, 0, syslock,			/* 53 = lock user in core */
< 	3, 0, ioctl,			/* 54 = ioctl */
< 	0, 0, nosys,			/* 55 = readwrite (in abeyance) */
< 	4, 0, mpxchan,			/* 56 = creat mpx comm channel */
< 	0, 0, nosys,			/* 57 = reserved for USG */
< 	0, 0, nosys,			/* 58 = reserved for USG */
< 	3, 0, exece,			/* 59 = exece */
< 	1, 0, umask,			/* 60 = umask */
< 	1, 0, chroot,			/* 61 = chroot */
< 	0, 0, nosys,			/* 62 = x */
< 	0, 0, nosys			/* 63 = used internally */
---
> 	{0, 0, nullsys},		/*  0 = indir */
> 	{1, 1, rexit},			/*  1 = exit */
> 	{0, 0, fork},			/*  2 = fork */
> 	{3, 3, read},			/*  3 = read */
> 	{3, 3, write},			/*  4 = write */
> 	{3, 3, open},			/*  5 = open */
> 	{1, 1, close},			/*  6 = close */
> 	{0, 0, wait},			/*  7 = wait */
> 	{2, 2, creat},			/*  8 = creat */
> 	{2, 2, link},			/*  9 = link */
> 	{1, 1, unlink},			/* 10 = unlink */
> 	{2, 2, exec},			/* 11 = exec */
> 	{1, 1, chdir},			/* 12 = chdir */
> 	{0, 0, gtime},			/* 13 = time */
> 	{3, 3, mknod},			/* 14 = mknod */
> 	{2, 2, chmod},			/* 15 = chmod */
> 	{3, 3, chown},			/* 16 = chown */
> 	{1, 1, sbreak},			/* 17 = break */
> 	{2, 2, stat},			/* 18 = stat */
> 	{3, 3, seek},			/* 19 = seek */
> 	{0, 0, getpid},			/* 20 = getpid */
> 	{3, 3, smount},			/* 21 = mount */
> 	{1, 1, sumount},		/* 22 = umount */
> 	{1, 1, setuid},			/* 23 = setuid */
> 	{0, 0, getuid},			/* 24 = getuid */
> 	{1, 1, stime},			/* 25 = stime */
> 	{4, 4, ptrace},			/* 26 = ptrace */
> 	{1, 1, alarm},			/* 27 = alarm */
> 	{2, 2, fstat},			/* 28 = fstat */
> 	{0, 0, pause},			/* 29 = pause */
> 	{2, 2, utime},			/* 30 = utime */
> 	{2, 2, stty},			/* 31 = stty */
> 	{2, 2, gtty},			/* 32 = gtty */
> 	{2, 2, saccess},		/* 33 = access */
> 	{1, 1, nice},			/* 34 = nice */
> 	{1, 1, ftime},			/* 35 = ftime */
> 	{0, 0, sync},			/* 36 = sync */
> 	{2, 2, kill},			/* 37 = kill */
> 	{0, 0, nullsys},		/* 38 = switch; inoperative */
> 	{0, 0, nullsys},		/* 39 = setpgrp (not in yet) */
> 	{0, 0, nosys},			/* 40 = tell (obsolete) */
> 	{2, 2, dup},			/* 41 = dup */
> 	{0, 0, pipe},			/* 42 = pipe */
> 	{1, 1, times},			/* 43 = times */
> 	{4, 4, profil},			/* 44 = prof */
> 	{0, 0, nosys},			/* 45 = unused */
> 	{1, 1, setgid},			/* 46 = setgid */
> 	{0, 0, getgid},			/* 47 = getgid */
> 	{2, 2, ssig},			/* 48 = sig */
> 	{0, 0, nosys},			/* 49 = reserved for USG */
> 	{0, 0, nosys},			/* 50 = reserved for USG */
> 	{1, 1, sysacct},		/* 51 = turn acct off/on */
> 	{0, 0, nosys},			/* 52 = set user physical addresses */
> 	{1, 1, syslock},		/* 53 = lock user in core */
> 	{3, 3, ioctl},			/* 54 = ioctl */
> 	{0, 0, nosys},			/* 55 = readwrite (in abeyance) */
> 	{0, 0, nosys},			/* 56 = creat mpx comm channel */
> 	{0, 0, nosys},			/* 57 = reserved for USG */
> 	{0, 0, nosys},			/* 58 = reserved for USG */
> 	{3, 3, exece},			/* 59 = exece */
> 	{1, 1, umask},			/* 60 = umask */
> 	{1, 1, chroot},			/* 61 = chroot */
> 	{0, 0, nosys},			/* 62 = x */
> 	{0, 0, sigreturn}		/* 63 = sigreturn (Armv7 signal trampoline) */
131a109,183
> char	regloc[9] = { R0, R1, R2, R3, R4, R5, R6, R7, RPS };
> /*
>  * Called from svc_entry (conf/low.s) on a system call.  r is the 17-int
>  * trap frame; the syscall number is in r7 (Armv7 ABI), arguments in
>  * r0..r5.  Adapted from v7 trap.c case 6+USER plus the out: tail.
>  */
> void
> trap(int *r)
> {
> 	register int i;
> 	register struct sysent *callp;
> 	u.u_fpsaved = 0;
> 	u.u_ar0 = r;
> 	u.u_error = 0;
> 	callp = &sysent[r[7] & 077];	/* Armv7 syscall number is in r7 */
> 	for(i = 0; i < callp->sy_narg && i < 6; i++)
> 		u.u_arg[i] = r[i];
> 	u.u_dirp = (caddr_t)u.u_arg[0];
> 	/*
> 	 * Default the return registers to 0.  V7 seeded r_val1 from the
> 	 * incoming r0 and relied on each libc stub to `clr r0` on the
> 	 * success path; this port's libc returns the raw syscall register
> 	 * via syscall3, so a call that leaves r_val1 unset (access, chdir,
> 	 * close, ...) must yield 0 to mean success.
> 	 */
> 	u.u_r.r_val1 = 0;
> 	u.u_r.r_val2 = 0;
> 	u.u_ap = u.u_arg;
> 	if (save(u.u_qsav)) {
> 		if (u.u_error == 0)
> 			u.u_error = EINTR;
> 	} else {
> 		(*callp->sy_call)();
> 	}
> 	if (u.u_error)
> 		r[R0] = -u.u_error;
> 	else {
> 		r[R0] = u.u_r.r_val1;
> 		r[R1] = u.u_r.r_val2;
> 	}
> 	/* out: deliver signals and reschedule before returning to user */
> 	if (issig())
> 		psig();
> 	(void)setpri(u.u_procp);
> 	if (runrun)
> 		qswtch();
> }
> /*
>  * Called from the undef/abort entry stubs (conf/low.s) for a hardware
>  * fault.  signo is the signal it maps to; r is the trap frame.  A fault
>  * taken in kernel mode is fatal.
>  */
> void
> user_trap_handler(int signo, int *r)
> {
> 	int mode = r[RPS] & 0x1f;
> 	if(mode != 0x10 && mode != 0x1f) {
> 		unsigned int dfar, dfsr;
> 		__asm__ volatile("mrc p15,0,%0,c6,c0,0":"=r"(dfar));
> 		__asm__ volatile("mrc p15,0,%0,c5,c0,0":"=r"(dfsr));
> 		printf("kernel trap sig=%d pc=0x%x cpsr=0x%x dfar=0x%x dfsr=0x%x\n",
> 		    signo, r[15], r[RPS], dfar, dfsr);
> 		panic("kernel trap");
> 	}
> 	u.u_fpsaved = 0;
> 	u.u_ar0 = r;
> 	psignal(u.u_procp, signo);
> 	if (issig())
> 		psig();
> 	(void)setpri(u.u_procp);
> 	if (runrun)
> 		qswtch();
> }
> void nosys(void)   { u.u_error = EINVAL; }
> void nullsys(void) { }
```

### usr/src/cmd/awk/makefile

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/awk/makefile unix-v7-c99/usr/src/cmd/awk/makefile || true
```

Expect:

```
2a3,9
> LDFLAGS =
> CRT =
> LDLIBS = -lm
> YACC = bison -y
> LEX = flex
> HOSTCC = cc
> HOSTCFLAGS = -std=gnu89 -w
17a25
> GEN=awk.g.c awk.h awk.lx.c proc proc-token.o proctab.c
20c28
< 	cc -i -s $(CFLAGS) awk.g.o $(FILES) -lm -o awk
---
> 	$(CC) $(CFLAGS) $(LDFLAGS) -o awk $(CRT) awk.g.o $(FILES) $(LDLIBS)
22c30,33
< y.tab.h:	awk.g.o
---
> awk.g.c awk.h:	awk.g.y
> 	$(YACC) $(YFLAGS) awk.g.y
> 	mv y.tab.c awk.g.c
> 	mv y.tab.h awk.h
24,25c35,36
< awk.h:	y.tab.h
< 	-cmp -s y.tab.h awk.h || cp y.tab.h awk.h
---
> awk.g.o:	awk.g.c awk.h awk.def
> 	$(CC) $(CFLAGS) -c awk.g.c
29,31c40,41
< token.c:	awk.h
< 	ed - <tokenscript
< 	rm temp
---
> awk.lx.c:	awk.lx.l
> 	$(LEX) -o awk.lx.c awk.lx.l
38c48
< 	cc -p -i awk.g.o $(FILES) -lm
---
> 	$(CC) -p $(CFLAGS) awk.g.o $(FILES) $(LDLIBS)
51,53c61,66
< 	proc > proctab.c
< proc:	awk.h proc.o token.o
< 	cc -o proc proc.c token.o
---
> 	./proc > proctab.c
> proc:	awk.h proc.c token.c
> 	$(HOSTCC) $(HOSTCFLAGS) -c token.c -o proc-token.o
> 	$(HOSTCC) $(HOSTCFLAGS) -o proc proc.c proc-token.o
> clean:
> 	rm -f awk *.o $(GEN) y.tab.c y.tab.h
```

### usr/src/cmd/awk/awk.lx.l

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/awk/awk.lx.l unix-v7-c99/usr/src/cmd/awk/awk.lx.l || true
```

Expect:

```
0a1
> %option noyywrap noinput nounistd
2a4,8
> %top{
> #include <stddef.h>
> #define	_STRING_H_
> #define	_STDLIB_H_
> }
7c13
< extern int	yylval;
---
> extern YYSTYPE	yylval;
8a15,26
> cell	*fieldadr(int n);
> void	yyerror(char *s);
> int	input(void);
> int	startreg(void);
> void	*memset(void *s, int c, unsigned int n);
> #undef	YY_INPUT
> #define	YY_INPUT(buf,result,max_size) \
> do { \
> 	int c = input(); \
> 	if (c == 0) result = YY_NULL; \
> 	else { buf[0] = c; result = 1; } \
> } while (0)
10c28
< int	lineno	1;
---
> int	lineno = 1;
16c34
< #define	CADD	cbuf[clen++]=yytext[0]; if(clen>=CBUFLEN-1) {yyerror("string too long", cbuf); BEGIN A;}
---
> #define	CADD	cbuf[clen++]=yytext[0]; if(clen>=CBUFLEN-1) {yyerror("string too long"); BEGIN A;}
28c46
< 	switch (yybgin-yysvec-1) {	/* witchcraft */
---
> 	switch (YY_START) {	/* witchcraft */
66c84
< 				yylval = lookup("$record", symtab);
---
> 				yylval = (YYSTYPE)lookup("$record", symtab);
69c87
< 				yylval = fieldadr(atoi(yytext+1));
---
> 				yylval = (YYSTYPE)fieldadr(atoi(yytext+1));
74c92
< <A>NF		{ mustfld=1; yylval = setsymtab(yytext, NULL, 0.0, NUM, symtab); RETURN(VAR); }
---
> <A>NF		{ mustfld=1; yylval = (YYSTYPE)setsymtab(yytext, NULL, 0.0, NUM, symtab); RETURN(VAR); }
76c94
< 		yylval = setsymtab(yytext, NULL, atof(yytext), CON|NUM, symtab); RETURN(NUMBER); }
---
> 		yylval = (YYSTYPE)setsymtab(yytext, NULL, atof(yytext), CON|NUM, symtab); RETURN(NUMBER); }
101c119
< <A>{A}{B}*	{ yylval = setsymtab(yytext, tostring(""), 0.0, STR, symtab); RETURN(VAR); }
---
> <A>{A}{B}*	{ yylval = (YYSTYPE)setsymtab(yytext, tostring(""), 0.0, STR, symtab); RETURN(VAR); }
131c149
< <str>\"		{ BEGIN A; cbuf[clen]=0; yylval = setsymtab(cbuf, tostring(cbuf), 0.0, CON|STR, symtab); RETURN(STRING); }
---
> <str>\"		{ BEGIN A; cbuf[clen]=0; yylval = (YYSTYPE)setsymtab(cbuf, tostring(cbuf), 0.0, CON|STR, symtab); RETURN(STRING); }
140c158
< <chc>"]"	{ BEGIN reg; cbuf[clen]=0; yylval = tostring(cbuf);
---
> <chc>"]"	{ BEGIN reg; cbuf[clen]=0; yylval = (YYSTYPE)tostring(cbuf);
148c166,167
< input()
---
> int
> input(void)
150c169
< 	register c;
---
> 	register int c;
153,155c172
< 	if (yysptr > yysbuf)
< 		c = U(*--yysptr);
< 	else if (yyin == NULL)
---
> 	if (lexprog != NULL)
166c183,184
< startreg()
---
> int
> startreg(void)
168a187
> 	return(0);
```

### usr/src/cmd/sed/makefile

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sed/makefile unix-v7-c99/usr/src/cmd/sed/makefile || true
```

Expect:

```
1a2,4
> LDFLAGS =
> CRT =
> LDLIBS =
14c17
< sed:	sed0.o sed1.o; cc -s -o sed -n *.o
---
> sed:	sed0.o sed1.o; $(CC) $(CFLAGS) $(LDFLAGS) -o sed $(CRT) *.o $(LDLIBS)
```

### usr/src/cmd/sh/makefile

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/sh/makefile unix-v7-c99/usr/src/cmd/sh/makefile || true
```

Expect:

```
1a2,4
> LDFLAGS =
> CRT =
> LDLIBS =
25c28
< sh:;		cc -o sh -n -s *.o
---
> sh:;		$(CC) $(CFLAGS) $(LDFLAGS) -o sh $(CRT) *.o $(LDLIBS)
32c35
< .c.o:;	cc -O -c $<
---
> .c.o:;	$(CC) $(CFLAGS) -c $<
```

### usr/src/cmd/dc/makefile

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/dc/makefile unix-v7-c99/usr/src/cmd/dc/makefile || true
```

Expect:

```
0a1,3
> LDFLAGS =
> CRT =
> LDLIBS =
12c15
< 	cc -n -s -O dc.c -o dc
---
> 	$(CC) $(CFLAGS) $(LDFLAGS) dc.c -o dc $(CRT) $(LDLIBS)
```

### usr/src/cmd/tar/makefile

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/tar/makefile unix-v7-c99/usr/src/cmd/tar/makefile || true
```

Expect:

```
2a3,5
> LDFLAGS =
> CRT =
> LDLIBS =
15c18
< 	cc -i -s -O tar.c -o tar
---
> 	$(CC) $(CFLAGS) $(LDFLAGS) tar.c -o tar $(CRT) $(LDLIBS)
18c21
< 	cc -i -s -O *.o -o v6tar
---
> 	$(CC) $(CFLAGS) $(LDFLAGS) *.o -o v6tar $(LDLIBS)
21c24
< 	cc -c -O $?
---
> 	$(CC) $(CFLAGS) -c $?
24c27
< 	cc -c -O $?
---
> 	$(CC) $(CFLAGS) -c $?
27c30
< 	cc -c -O $?
---
> 	$(CC) $(CFLAGS) -c $?
30c33
< 	cc -c -O $?
---
> 	$(CC) $(CFLAGS) -c $?
33c36
< 	cc -c -O $?
---
> 	$(CC) $(CFLAGS) -c $?
36c39
< 	cc -c -O $?
---
> 	$(CC) $(CFLAGS) -c $?
39c42
< 	cc -c -O $?
---
> 	$(CC) $(CFLAGS) -c $?
42c45
< 	cc -c -O $?
---
> 	$(CC) $(CFLAGS) -c $?
45c48
< 	cc -c -O $?
---
> 	$(CC) $(CFLAGS) -c $?
```

### usr/src/cmd/tp/makefile

Local test:

```
diff unix-v7-c99/v7/usr/src/cmd/tp/makefile unix-v7-c99/usr/src/cmd/tp/makefile || true
```

Expect:

```
1a2,4
> LDFLAGS =
> CRT =
> LDLIBS =
15c18
< 	cc $(CFLAGS) tp0.o tp1.o tp2.o tp3.o -o tp
---
> 	$(CC) $(CFLAGS) $(LDFLAGS) tp0.o tp1.o tp2.o tp3.o -o tp $(CRT) $(LDLIBS)
```

### usr/sys/h/reg.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/reg.h unix-v7-c99/usr/sys/h/reg.h || true
```

Expect:

```
2,3c2
<  * Location of the users' stored
<  * registers relative to R0.
---
>  * Location of the users' stored registers relative to R0.
4a4,8
>  *
>  * Armv7: the trap frame built by svc_entry (conf/low.s) is 17 ints --
>  * r0..r12, then sp=r[13], lr=r[14], pc=r[15], cpsr=r[16].  u.u_ar0
>  * points at r[0].  PDP-11 register numbering does not apply, so these
>  * indices are the Armv7 frame slots (required for Armv7).
7,15c11,19
< #define	R1	(-2)
< #define	R2	(-9)
< #define	R3	(-8)
< #define	R4	(-7)
< #define	R5	(-6)
< #define	R6	(-3)
< #define	R7	(1)
< #define	PC	(1)
< #define	RPS	(2)
---
> #define	R1	(1)
> #define	R2	(2)
> #define	R3	(3)
> #define	R4	(4)
> #define	R5	(5)
> #define	R6	(13)		/* user stack pointer */
> #define	R7	(15)		/* user program counter */
> #define	PC	(15)
> #define	RPS	(16)		/* saved cpsr */
17c21
< #define	TBIT	020		/* PS trace bit */
---
> #define	TBIT	0		/* no PDP-11 trace bit on Arm */
```

### usr/sys/h/text.h

Local test:

```
diff unix-v7-c99/v7/usr/sys/h/text.h unix-v7-c99/usr/sys/h/text.h || true
```

Expect:

```
9,11c9,11
< 	short	x_daddr;	/* disk address of segment (relative to swplo) */
< 	short	x_caddr;	/* core address, if loaded */
< 	short	x_size;		/* size (clicks) */
---
> 	int	x_daddr;	/* disk address of segment (relative to swplo) */
> 	int	x_caddr;	/* core address, if loaded (Armv7: 32-bit click) */
> 	int	x_size;		/* size (clicks) */
```
