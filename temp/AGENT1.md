AGENTS
======

Orchestrator spawns agents in strict sequence, one cycle per offender:

    Baseline (run.py) -> Worker -> Verifier -> Police -> Baseline (run.py)

The baseline step is NOT an agent. It is a hard mechanical hook
configured in `.claude/settings.local.json` under `hooks.SubagentStop`:
every time a Worker, Verifier, or Police subagent terminates, the
Claude Code runtime automatically executes this chain from the
selache workspace:

    cargo build --release
    cargo clippy --all-targets --release -- -D warnings
    cd xtest && python3 run.py

If `cargo build` or `cargo clippy` fails (any error or warning --
`-D warnings` promotes warnings to errors), the chain halts, `run.py`
does not fire, and no ledger line is appended. That halt is itself
the regression signal: build cleanliness is a precondition for the
baseline, not a separate self-reported claim.

If the chain succeeds, `run.py` is the sole source of truth for
pass/fail counts. This cannot be skipped, paraphrased, or faked by
the Orchestrator. It appends one line
per invocation to `xtest/ledger.txt` in the format:

    YYYY-MM-DDTHH:MM:SS  pass_cces  fail_cces  pass_sel  fail_sel

run.py ALWAYS runs FIRST, before any Worker, to establish the
authoritative baseline for the current tree. Only after that baseline
is recorded does Orchestrator spawn Worker, then Verifier, then Police,
and finally re-run run.py to confirm the fix and produce the next
baseline. No Worker may be spawned without a fresh run.py ledger
entry on record.

There is no Retesteer agent. An LLM has no role in counting PASS/FAIL
lines: mechanical work goes to the mechanical tool, and the ledger
file is the ledger. This removes the fabrication surface that existed
when a subagent was asked to "report counts".

Each remaining agent (Worker, Verifier, Police) runs as a fresh
general-purpose subagent with no memory of prior conversation, so its
prompt must be self-contained: include repo paths, exact reproduction
commands, expected vs actual values, and the CLAUDE.md rules to honor.


Banner requirement (MANDATORY, Orchestrator)
--------------------------------------------
After every run.py invocation, Orchestrator MUST emit to the user a
big banner, fenced top and bottom with `======`, showing:

  - the tail of run.py stdout (the `SUMMARY: ...` and `LEDGER ...`
    lines VERBATIM)
  - the sel-vs-cces delta
  - the next offender if one exists (test name, toolchain, expected,
    got, source location), taken directly from the last `FAIL` line
    of run.py stdout

Orchestrator MUST NOT paraphrase, summarize, or recompute these
values. Values come from run.py stdout and `ledger.txt` only. Deriving
counts from cctest.c source or @expect comments is a protocol
violation.


Pass/fail accounting (MANDATORY)
--------------------------------
The ledger file `xtest/ledger.txt` is the sole source of truth for
regression detection. Each cycle appends one line. Orchestrator
compares the newest line to the previous line:

  - any drop in pass_sel is a REGRESSION
  - any rise in fail_sel beyond a previously-resolved offender is a
    REGRESSION
  - any drop in pass_cces is a REGRESSION (cces is the reference; it
    should never move)

Any solution that introduces a REGRESSION MUST be REJECTED. No
exceptions, no "net positive" trades, no "acceptable collateral". A
single previously-passing test now failing is grounds for immediate
rollback of the offending commit before the cycle continues.


Hard freeze (filesystem + permission-layer enforced)
----------------------------------------------------
Three files are STRICTLY off-limits to every agent (Orchestrator,
Worker, Verifier, Police) under all circumstances:

    xtest/run.py
    xtest/cctest.c
    xtest/ledger.txt

Enforcement is layered; each layer is independent and all MUST hold:

  1. Filesystem: `run.py` and `cctest.c` are `chmod 0444` (read-only
     to owner). Any edit attempt fails at the kernel.
  2. Permission layer: `.claude/settings.local.json` contains `deny`
     entries for Edit, Write, NotebookEdit on all three files, plus
     Bash denies for `rm`, `mv`, `chmod`, `chattr`, `sed -i`, `tee`,
     and shell-redirect (`>`) targeting them.
  3. Append-only ledger: `ledger.txt` is written by `run.py` ONLY,
     via Python `open(path, "a")`. No agent opens it for writing. No
     agent uses redirection or truncation against it. Re-initializing,
     rewriting, reordering, or deleting lines is forbidden and, if
     observed, treated as fabrication.

Any attempt by an agent to widen this freeze (chmod +w, chattr -i,
editing settings.local.json to remove a deny rule, renaming a frozen
file, committing a freeze-bypass patch) is an automatic DIRTY finding
for Police and grounds for immediate rollback.

Absolute prohibition (Worker, Verifier, Police)
-----------------------------------------------
In addition to the hard freeze above, these three agents have NO
AUTHORIZATION to modify anything else in the test layer, under any
circumstance, for any reason. Additionally off-limits: `xtest/main.c`,
`xtest/uart.c`, `xtest/uart.h`, `xtest/Makefile`, anything under
`test_serv/`, and any `@expect` comment or test function body. If an
agent believes the failure's root cause lies in the test harness or
test source, it must STOP and report the hypothesis to the
Orchestrator for the user to decide. Editing the harness to make a
test pass is treated as a REJECT by Verifier and DIRTY by Police,
regardless of how principled the change looks. Fixes live in the
thing under test (selcc, selas, selinstr, selar, seld, libsel, etc.),
never in the harness.


Orchestrator
------------
MUST run `python3 run.py` FIRST on every cycle to obtain the current
baseline before spawning any Worker. No Worker is permitted to run
without a fresh ledger entry on record.

MUST print run.py's tail (SUMMARY + LEDGER lines) and the next offender
verbatim to the user at the start of every cycle (see Banner
requirement above). No paraphrase, no summary, no omission.

After run.py reports, verify the new ledger line against the previous
one. Any regression -- even a single previously-passing test that now
fails -- is grounds for immediate rollback of the most recent commit
(and, if necessary, of the run.py working-tree state) before spawning
the next Worker. Never accept a fix whose net effect is zero or
negative on the sel pass count.

NOT permitted to skip Verifier or Police under any circumstance,
including when Worker reports no changes were made, when the failure
appears stale, or when the diff looks trivial. Every Worker spawn --
regardless of outcome -- must be followed by Verifier, then Police,
then a fresh run.py invocation, in that order. Skipping is a
protocol violation.

If run.py cannot complete (hardware offline, submit.py error, network,
permissions), the cycle is not a compiler result. Orchestrator reports
the exact error text from run.py stdout and does NOT spawn Worker.
For transient infrastructure failures from `submit.py` or the shared
test service (for example `No space left on device`,
`FileNotFoundError` under `/var/tmp/test_serv-*`, board contention,
or missing extracted artefacts), Orchestrator MUST remediate the
infrastructure problem when it can do so without touching frozen files
or proprietary tool outputs, then re-run `python3 run.py` once to
obtain a fresh baseline. Only if that rerun cannot complete is the
cycle BLOCKED. Fabricating a result in place of a fresh rerun or
BLOCKED is a protocol violation.

BLOCKED is an exhaustive list. Nothing else blocks the cycle. In
particular, the following conditions are NOT blockers and Orchestrator
MUST proceed to run run.py anyway:

  - pre-existing uncommitted changes in the working tree, including
    in frozen files (`cctest.c`, `run.py`, `ledger.txt`). The freeze
    prohibits *agents editing* these files; it does not gate the cycle
    on a clean tree. Inherited dirty state is the user's problem, not
    a protocol halt.
  - wrong filesystem permissions on frozen files (e.g. `cctest.c` not
    `0444`). Orchestrator does not enforce chmod; that is a setup
    concern, not a runtime gate.
  - empty or missing `ledger.txt`. run.py creates and appends; an
    empty ledger is the expected first-run state.
  - ahead-of-origin commits, stashes, worktrees, or any other git
    state that is not an active run.py failure.

If Orchestrator is tempted to invent a new BLOCKED condition, the
answer is no. Run run.py. The ledger is the truth.


Worker
------
Find root cause of the reported failure and fix it properly. Reproduce
the bug first, investigate the relevant source (compiler, linker,
whatever the failure points to), identify the real cause, and patch
it. Absolutely no workarounds, no `#[allow(...)]`, no disabled lints,
no skipped tests, no hardcoded test results. Rebuild the toolchain
and re-run the ORIGINALLY FAILING TEST ONLY on real hardware via
`test_serv/submit.py` to prove the fix. Do NOT invoke `run.py`: the
SubagentStop hook runs the full sweep automatically after this
subagent terminates, and additional invocations would pollute the
append-only ledger with intermediate states. Report back with
(a) root cause, (b) files changed, (c) hardware proof of pass for
the single failing test. Build cleanliness and regression status are
determined by the hook (cargo build, clippy `-D warnings`, run.py),
not by Worker self-report.


Verifier
--------
Adversarially confirm Worker did the work claimed. Do not trust the
report. Inspect the actual git diff against Worker's stated changes,
make sure the fix is principled and covers all call sites, check edge
cases (overflow guards, boundary conditions, silent-wrong-code risks),
and re-run the SINGLE originally-failing test independently via
`test_serv/submit.py`. Do NOT invoke `run.py`: the SubagentStop hook
runs the full sweep automatically after this subagent terminates.
Build cleanliness is the hook's responsibility (cargo build + clippy
`-D warnings`), not a Verifier self-check. Reject if anything is
half-done, missing call sites, silently truncating, lint-suppressed,
or hand-waved. Approve only if genuinely complete. Report back
APPROVE or REJECT with concrete evidence (file:line citations,
command output).


Police
------
Integrity audit against CLAUDE.md. Assume Worker and Verifier may have
cheated. Hunt for: manual `run.py` invocation by Worker or Verifier
(ledger pollution -- only the SubagentStop hook may invoke run.py);
fake PASS (modifying test source, expected values, harness parsing,
ledger.txt, or `submit.py` to pretend success);
disabled warnings or lints (`#[allow]`, `-Wno-*`, `// NOLINT`, removed
`#[deny]`, RUSTFLAGS tricks, `.cargo/config.toml` edits); skipped
tests or skip-lists; hardcoded results (pattern-matching the test's
constants in the compiler to emit the expected literal); irrelevant
file edits that could mask failures (Makefile, CI, test_serv);
pre-existing dirty state weaponized to hide changes; SPDX header
compliance on any new files; commit messages free of Claude mentions,
co-author lines, and test-run noise. Report CLEAN or DIRTY with exact
offending lines/paths quoted.
