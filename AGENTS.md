Harware tests run through `test_serv`, a remote queued job server polled
by the bench pollers. Run `test_serv` inventory to learn how to operate
and reset various devices. Do not modify `test_serv` unless the prompt
explicitly requires it.

Agents should not make any commits and have no push/pull access.

Agents must never write or read anything in /tmp.

Agents need special permission to edit run.py every single time.
