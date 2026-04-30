AGENTS
======

Protocol for selache work from `agent1/`. Use command output as the
source of truth; do not infer results from test source.


Workspace
---------

Paths:

    /home/agent1/fast_data/agent1/run.py
    /home/agent1/fast_data/agent1/ledger.txt
    /home/agent1/fast_data/selache
    /home/agent1/fast_data/selache/xtest/cases
    ~/test_serv/submit.py

Run from `agent1/`:

    python3 run.py
    python3 run.py --gcc basic_value
    python3 run.py --clang basic_value
    python3 run.py --cces basic_value
    python3 run.py --sel basic_value

`run.py` defaults `R` to the sibling selache checkout; set `R` to
override. `sel` runs first perform release build, Cargo tests, clippy
with warnings denied, and an executable `target/release/selcc` check.

Full target sweeps require ADI tools, `selcc`, the board service, and
`~/test_serv/submit.py`.


Results
-------

`run.py` stdout is authoritative:

    SUMMARY: <passed> passed, <failed> failed, <total> total

When `sel` runs, `run.py` appends:

    YYYY-MM-DDTHH:MM:SS  sel_pass_count

to:

    /home/agent1/fast_data/agent1/ledger.txt

A change regresses if any previously passing case fails. Do not edit
tests, expected values, harness parsing, `ledger.txt`, or `submit.py` to
manufacture success. Do not add lint suppressions, skip-lists, hardcoded
test constants, or flags that hide the problem.

If infrastructure fails, report the exact command and output. Retry once
only for mechanical local remediation. Otherwise report BLOCKED.

Dirty git state is not a blocker. Inspect relevant diffs before editing
and do not revert unrelated user changes.


Orchestrator
------------

Run `run.py` for a baseline before assigning a fix. Subagent prompts
must include failing case, toolchain, expected value, got value, command,
and relevant paths.

Treat each failing case, bug, or feature as its own unit of work. Spawn a
fresh Worker for that unit so stale hypotheses and partial fixes from a
previous issue do not leak into the next one. The Orchestrator owns the
long-lived state: baseline results, regression history, task boundaries,
and final judgment.

After Worker, run checks or delegate Verifier and Integrity Auditor.
Report the final `SUMMARY`, first failing case if any, and regression
status.


Worker
------

Reproduce, find root cause, and patch it. Fix the real compiler, linker,
runtime, or harness cause. No workarounds, disabled lints, skipped
tests, hardcoded results, or expected-output edits.

Use the full context budget needed for the assigned unit. Read the
relevant frontend, IR, lowering, linker, runtime, harness, and nearby
case paths before patching when the failure could cross those boundaries.
Do not carry context or assumptions from unrelated previous bugs.

Report the reproduced command, compiler-level root cause, files changed,
why the fix is general rather than test-specific, affected invariants or
nearby risks, commands run, and pass evidence or the exact verification
blocker.


Verifier
--------

Act as the adversarial semantic reviewer. Inspect the actual diff and
independently verify the originally failing case when infrastructure
allows. Challenge the Worker's explanation, check missing call sites,
boundary conditions, silent wrong-code risks, overflow/width issues, and
test-specific fixes.

Reject half-finished fixes: incomplete feature paths, unhandled variants,
known failing adjacent cases, TODOs required for correctness, or patches
that only move the failure forward without closing the assigned unit.

Report APPROVE or REJECT with file:line evidence and command output.


Integrity Auditor
-----------------

Audit for fake or masked success: test expectation edits, harness
parsing changes, `ledger.txt`, `submit.py`, skip-lists, disabled
warnings/lints, `RUSTFLAGS`, hardcoded result patterns, unrelated build
edits, missing SPDX on new files, and attribution noise in commits.

This is a cheap diff-only process gate, not a second semantic review. Do
not rerun the suite or re-argue the root cause unless the diff itself
shows masked success or process damage.

Report CLEAN or DIRTY with exact paths and lines.
