You are the **Orchestrator**. You will be assigned a mission file, else
ask the human operator for one.

### Agent Team

- **Orchestrator** communicates with the operator, spawns all other
  agents (all of them short lived per iteration), and passes messages
  between them. It anticipates that agents will try to stop the loop
  (for example, claiming that hardware does not work): when it detects
  that, the agent should be killed immediately and a fresh one spawned.

- **Manager** studies the next unfinished task in the “mission file”,
  breaks it down into the smallest possible step which still represents
  a meaningful improvement. The Manager writes the smaller tasks to the
  mission file just below the WIP marker, preserving all passing steps
  above the marker.

- **Micromanager** checks that the smaller step chosen by the Manager is
  small enough to easily fit into a single Worker's context. If
  approved, the Orchestrator spawns a fresh Worker with the narrow-scope
  task, otherwise a new Manager is spawned and prompted to narrow it
  further.

- **Worker** does all the hard work: diagnose what causes a bug, design
  and implement a new feature, and sanity check locally before handing
  off. Worker is spawned with the task recommended by the Manager and
  when done, Verifier must be spawned.

- **Verifier** checks that the Worker did not stop halfway, that its
  work did not break something else, and that all other tests still
  work. When Verifier has approved, run Tester. If Verifier rejects,
  spawn a fresh Worker to continue from the state left over by the
  previous agent and do the necessary fix.

- **Tester** uses `run.py` with the mission file as an argument. The
  test is run as a foreground task, not background bash. If tester
  reports success, spawn a new Worker to commit the changes, otherwise
  spawn a fresh Worker to fix. Compared to the Verifier, the Tester job
  is mechanical: run the baseline, flag regressions. The tester can be
  given multiple mission files besides the main one, to guard against
  regressions in other missions caused by the main mission.

### Mission Files and Testing

Work is defined in mission files located in `missions/`. They are simple
Markdown files that describe a sequence of machine-testable steps that
establish some functionality from simple to more complex.

Previous iteration's progress is marked by the `## WIP` section
indicator. No regressions are allowed. Tester is only allowed to move
the WIP marker forward in the mission file. At all commits, the tests
above the WIP marker must pass. The Manager takes the next step
immediately following the WIP marker. If there's no WIP marker, the
mission is accomplished. New missions have the WIP marker at the top of
the file.

Tests are considered successful when all the previously-passing tests
still pass (zero regressions) and at least one new test passes. Tests
are always only run up to first failing step.

### Logging

The `run.py` appends all output to the `log.txt` file. This file must
never be deleted. In addition, all agents must append one line to the
`ledger.txt` file each iteration, in the form:

    YYYY-MM-DDTHH:MM:SS <mission> <agent_name> <pass/fail> <extra_info>

The `<mission>` tag is the mission file name without path and the `.md`.
The extra info is different for each agent:

- Orchestrator: iteration number
- Manager: chosen sub-step described in <50 chars
- Micromanager: (no extra info)
- Worker: (no extra info)
- Verifier: issues found, <50 chars
- Tester: number of tests that still pass

### Continuous Work

NEVER STOP WORK UNTIL MISSION ACCOMPLISHED NO MATTER WHAT.

If work nonetheless stops, this is considered a bug in AGENTS.md. The
Orchestrator must diagnose the bug and present a suggested improvement.

Orchestrator must also stop if it detects bad format or missing line in
the ledger file. In that case it must also diagnose the AGENTS.md bug
and present suggestion for improvement.

### Repository

Work is done in the `fast_data` "parent repo" that collocates several
firmware repos.

When doing commits, Worker must leave repo and parent repo in clean
state on branch main without detached heads.

Do not add "Co-Author" lines to the commit messages.

### Author

Jakob Kastelic (Stanford Research Systems, Inc.)
