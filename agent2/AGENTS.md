# Agentic pattern

Small pipeline of fresh, short-lived agents. Orchestrator owns FSM,
spawns managers/workers/verifiers, relays artifacts, and commits only
after verification.

## Rig reset

The planning Manager runs rig reset exactly once per FSM iteration,
immediately before handing work to Worker. Review Managers never run rig
reset. The reset submits the FPGA `uart_echo` and verifies that the rig
is up. Run:

    cd /home/agent2/fast_data/fpga
    make build/uart/Makefile
    make -C build/uart all
    cd /home/agent2/fast_data/fpga/build/uart
    python3 -u $TEST_SERV/run_md.py \
      --ledger /home/agent2/fast_data/agent2/ledger.txt \
      --module uart \
      --log /home/agent2/fast_data/agent2/log.txt

Rig reset is green only when the current `run_md.py` invocation exits 0,
records a new `uart` ledger entry, attempts at least one block, and
reports every attempted block passed with no `test_serv` errors. If the
reset fails because `$TEST_SERV` is unset, use the default from "Test
server" and retry once. If reset still fails, Manager records the blocker
in `TODO.md` and returns BLOCKED instead of sending work to Worker.

## Test server

`$TEST_SERV` must point to the `test_serv` checkout containing
`run_md.py`. If unset, use:

    export TEST_SERV=/home/agent2/test_serv

If `/home/agent2/test_serv/run_md.py` is missing, install `test_serv`
before running hardware tests.

## Test records

All hardware test runs must pass `--ledger
/home/agent2/fast_data/agent2/ledger.txt --module <ex> --log
/home/agent2/fast_data/agent2/log.txt` to `run_md.py`. These files live
beside this file and are the persistent record across agents. Do not
write per-example ledgers or logs under `build/<ex>`.

## FSM

Trigger: "read AGENTS.md and work on `<ex>`" → assistant = Orchestrator.
Per `<ex>`, run:

    MANAGE(plan + one reset) -> WORK -> VERIFY
                                | red or NEEDS_EVIDENCE
                                v
                               next iteration

    VERIFY green -> MANAGE(review, no reset)
                 -> COMMIT -> next iteration | DONE | BLOCKED

    VERIFY red   -> next iteration

Orchestrator drives loop in foreground (state visible to user). Each
attempt gets fresh background agents; final checks use a separate
Verifier. No heartbeats; exit = status. Caps: 8 iterations total, 3
same-issue retries.

At the start and end of each iteration, Orchestrator prints a compact
progress update before any detailed phase output:

    ex=<ex> iter=<n>/8 status=<planning|reset|work|verify|green|red|blocked>
    goal=<current mission step>
    progress=<what is newly proven or changed since prior iteration>
    evidence=<latest command/result or missing evidence>
    next=<next phase or stop reason>

## Context discipline

Managers and Workers are not reused. Each starts fresh and receives only
the current task, `TODO.md`, relevant test output, target files, prior
attempt summary, current diff if any, retry count, and stop condition.
They must inspect the current filesystem before advising, diagnosing, or
editing.

## Regression discipline

Run the full baseline regression set at most once per FSM iteration. The
iteration's single baseline run may be used either for evidence-only
collection or for post-edit regression, never both. After completing its
edits to `<ex>.nw`, Worker runs the full regression set once for that
example:

    cd /home/agent2/fast_data/fpga
    make -C build/<ex> sim
    make -C build/<ex> bitstream
    make -C build/<ex> all
    cd /home/agent2/fast_data/fpga/build/<ex>
    python3 -u $TEST_SERV/run_md.py \
      --ledger /home/agent2/fast_data/agent2/ledger.txt \
      --module <ex> \
      --log /home/agent2/fast_data/agent2/log.txt

`make test` aborts on the first failing block (no `--full`); blocks past
the first failure are NOT executed. The summary `K/N BLOCKS FAILED`
counts unattempted blocks as not-failed --- never read it as `N-K
PASSED`. A green result is valid only when all blocks were attempted and
passed. If the regression fails, the iteration is red and the next Worker
retry gets that evidence; do not rerun the same baseline in Verifier.

## Test integrity

Agents must not remove tests, reorder tests, skip tests, weaken checks,
relax expected values, or change timeouts/sentinels to hide failures.
The goal is to make the existing ordered suite pass as written, then
continue through later tests. Agents may add tests or diagnostics, but
added tests must not replace, bypass, or defer existing required tests.

## Agents

Each spawned `general-purpose` with `run_in_background: true`.
Orchestrator waits for completion notification, then prints the result
before the next transition.

- **Manager**: reads `TODO.md`, latest Worker/Verifier results, current
  diff, and test evidence. Reviews progress against Mission Target and
  Next Steps. When the next step is WORK, Manager executes exactly one rig
  reset flow from "Rig reset" for that FSM iteration and confirms the rig
  is up from the `run_md.py` result before handing off to Worker. Manager
  updates `TODO.md` when progress or blockers change, and returns exactly
  one next step that moves toward mission completion, or BLOCKED if rig
  reset cannot be made green. Manager does not edit source or accept
  unverified progress.
- **Worker**: diagnoses from the evidence it was given, edits only
  relevant chunks in `<ex>.nw` (literate: named chunks + prose, no
  comment-as-structure), then runs the one baseline regression for the
  iteration: `make sim`, `make bitstream`, `make all`, and `run_md.py`
  with the required agent ledger and log. Returns status, root cause,
  changed chunks, diff, command results, warning delta, and any failing
  block tail. If current failure evidence is missing or stale, Worker
  reports NEEDS_EVIDENCE without editing. On the next iteration, Manager
  may assign WORK(evidence-only). In WORK(evidence-only), Worker performs
  no source edits and spends that iteration's single baseline run
  collecting fresh evidence for the next Manager.
- **Verifier**: independently reviews the Worker's regression evidence,
  current diff, ledger, and log after Worker reports a green regression
  with all blocks attempted. Verifier does not rerun the baseline suite in
  the same FSM iteration. Returns PASS/FAIL, whether all blocks were
  attempted, failing block name, and verbatim block tail from the Worker
  evidence.

If the first failure looks like rig-down, stale build, missing Makefile,
or other infrastructure, Worker reports that instead of editing source.

## Orchestrator rules

- One pipeline per `<ex>`, parallel across examples. Hardware access must
  go through `run_md.py`; `test_serv` serializes jobs that require the
  same device, so two FPGA jobs cannot interleave on the rig. Do not
  bypass `run_md.py` for hardware tests.
- Start with Manager to choose the next mission-relevant step from
  `TODO.md`; if that step is WORK, Manager performs the single reset for
  that FSM iteration before returning.
- On VERIFY green: spawn Manager to review mission progress, update
  `TODO.md`, and choose the next step, DONE, or BLOCKED. This review
  Manager does not run rig reset; if another Worker step is needed, the
  reset happens once at the start of the next FSM iteration.
- Then `git commit` verified source and `TODO.md` updates (no Claude
  co-author).
- Commit only files relevant to `<ex>`; message names the example and
  fixed issue.
- On warning regression, sim FAIL, VERIFY red, or Worker NEEDS_EVIDENCE:
  start the next iteration by spawning Manager with the new evidence.
  Manager decides the next Worker step and performs the single reset for
  that iteration before handing off.
- On 3 same-issue reds, including regression red, VERIFY red, or repeated
  NEEDS_EVIDENCE: spawn Manager to record the blocker in `TODO.md`, then
  stop and report blocker. Do not commit source. Leave the blocker update
  uncommitted unless the user explicitly asks for a blocker-only commit.
- Orchestrator itself never runs `make` or edits source; only spawns,
  commits, and relays. Spawned Manager/Worker agents may run the commands
  assigned to their roles.
- On Manager exit: print full review (mission progress, TODO.md changes,
  next step, completion/blocker status) before next transition.
- On Worker exit: print full result (root cause, changed chunks, command
  results, warning delta, failing block/tail) before next transition.
- On Verifier exit: print full result (PASS/FAIL, failing block name,
  all-blocks-attempted flag, verbatim tail) before next transition.
