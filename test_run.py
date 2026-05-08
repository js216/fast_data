#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Jakob Kastelic
import io
import json
import textwrap
import unittest
from unittest import mock

from run import Runner


class AdvanceWipTests(unittest.TestCase):
    def test_moves_wip_after_one_following_section(self):
        src = textwrap.dedent("""\
            # Mission

            intro

            ## WIP

            ### First

            first body

            ### Second

            second body
            """)
        want = textwrap.dedent("""\
            # Mission

            intro

            ### First

            first body

            ## WIP

            ### Second

            second body
            """)
        self.assertEqual(Runner.advance_wip_text(src), want)

    def test_moves_wip_after_last_following_section(self):
        src = textwrap.dedent("""\
            # Mission

            ## WIP

            ### Last

            last body
            """)
        want = textwrap.dedent("""\
            # Mission

            ### Last

            last body

            ## WIP
            """)
        self.assertEqual(Runner.advance_wip_text(src), want)

    def test_moves_wip_before_next_top_level_section_area(self):
        src = textwrap.dedent("""\
            # Mission

            ## WIP

            ### SSH plugin exposes local put operation

            host-side plugin proof

            ## Planned Mission Arc

            1. Upload a small blob.
            """)
        want = textwrap.dedent("""\
            # Mission

            ### SSH plugin exposes local put operation

            host-side plugin proof

            ## WIP

            ## Planned Mission Arc

            1. Upload a small blob.
            """)
        self.assertEqual(Runner.advance_wip_text(src), want)

    def test_no_wip_is_unchanged(self):
        src = textwrap.dedent("""\
            # Mission

            ### Done

            body
            """)
        self.assertEqual(Runner.advance_wip_text(src), src)

    def test_wip_without_following_section_is_unchanged(self):
        src = textwrap.dedent("""\
            # Mission

            ### Done

            body

            ## WIP
            """)
        self.assertEqual(Runner.advance_wip_text(src), src)


class ForeignLeaseRetryTests(unittest.TestCase):
    def test_extends_only_once_after_final_foreign_lease_wait(self):
        backoffs = [0, 3]

        self.assertFalse(
            Runner._extend_retries_after_foreign_lease(backoffs, 0, 0))
        self.assertEqual(backoffs, [0, 3])

        self.assertTrue(
            Runner._extend_retries_after_foreign_lease(backoffs, 1, 0))
        self.assertEqual(backoffs, [0, 3, 0])

        self.assertFalse(
            Runner._extend_retries_after_foreign_lease(backoffs, 2, 1))
        self.assertEqual(backoffs, [0, 3, 0])

    def test_extends_only_once_after_final_watchdog_cancel(self):
        backoffs = [0, 3]

        self.assertFalse(
            Runner._extend_retries_after_watchdog_cancel(backoffs, 0, 0))
        self.assertEqual(backoffs, [0, 3])

        self.assertTrue(
            Runner._extend_retries_after_watchdog_cancel(backoffs, 1, 0))
        self.assertEqual(
            backoffs,
            [0, 3, Runner.WATCHDOG_CANCEL_RETRY_BACKOFF_S])

        self.assertFalse(
            Runner._extend_retries_after_watchdog_cancel(backoffs, 2, 1))
        self.assertEqual(
            backoffs,
            [0, 3, Runner.WATCHDOG_CANCEL_RETRY_BACKOFF_S])


class CancelDrainTests(unittest.TestCase):
    def _runner(self):
        runner = Runner.__new__(Runner)
        runner.CANCEL_DRAIN_WAIT_S = 30
        runner._log = mock.Mock()
        return runner

    def _urlopen_responses(self, job_lists):
        payloads = [
            json.dumps(jobs).encode()
            for jobs in job_lists
        ]
        return [io.BytesIO(payload) for payload in payloads]

    def test_cancel_drain_waits_until_matching_job_inactive(self):
        desc = 'agent1: Provision SD image with SSH keys [123]'
        runner = self._runner()
        log = io.BytesIO()
        jobs = [
            [
                {'digest': 'a' * 64, 'status': 'running',
                 'meta': {'description': desc}},
                {'digest': 'b' * 64, 'status': 'running',
                 'meta': {'description': 'agent2: other job'}},
            ],
            [
                {'digest': 'a' * 64, 'status': 'done',
                 'meta': {'description': desc}},
                {'digest': 'b' * 64, 'status': 'running',
                 'meta': {'description': 'agent2: other job'}},
            ],
        ]

        with mock.patch('run.urllib.request.urlopen',
                        side_effect=self._urlopen_responses(jobs)):
            with mock.patch('run.time.sleep') as sleep:
                self.assertTrue(
                    runner._wait_for_canceled_job(desc, 'a' * 64, log))

        sleep.assert_called_once_with(1)
        self.assertIn(b'canceled job drained', log.getvalue())

    def test_cancel_drain_timeout_is_bounded_and_logged(self):
        desc = 'agent1: Provision SD image with SSH keys [123]'
        runner = self._runner()
        runner.SERVER = 'http://test.invalid'
        log = io.BytesIO()
        jobs = [[
            {'digest': 'a' * 64, 'status': 'running',
             'meta': {'description': desc}},
        ]]

        with mock.patch('run.urllib.request.urlopen',
                        side_effect=self._urlopen_responses(jobs)):
            with mock.patch('run.time.monotonic', side_effect=[100, 131]):
                self.assertFalse(
                    runner._wait_for_canceled_job(desc, 'a' * 64, log))

        self.assertIn(b'canceled job still active after 30s', log.getvalue())

    def test_cancel_drain_resolves_stale_cancel_record(self):
        desc = 'agent1: Provision SD image with SSH keys [123]'
        runner = self._runner()
        runner.SERVER = 'http://test.invalid'
        log = io.BytesIO()
        digest = 'a' * 64
        jobs = [[
            {'digest': digest, 'status': 'running',
             'meta': {'description': desc}},
        ]]
        responses = self._urlopen_responses(jobs)
        responses.append(io.BytesIO(json.dumps({
            'status': 'stale_canceled',
            'digest': digest,
        }).encode()))

        with mock.patch('run.urllib.request.urlopen',
                        side_effect=responses):
            with mock.patch('run.time.monotonic', side_effect=[100, 131]):
                self.assertTrue(
                    runner._wait_for_canceled_job(desc, digest, log))

        self.assertIn(b'stale canceled job resolved', log.getvalue())
        self.assertNotIn(b'canceled job still active', log.getvalue())

    def test_watch_submit_drains_watchdog_cancel_before_return(self):
        desc = 'agent1: Provision SD image with SSH keys [123]'
        runner = self._runner()
        runner.SERVER = 'http://test.invalid'
        runner._last_watchdog_cancel = False
        proc = mock.Mock()
        proc.poll.return_value = None
        proc.wait.return_value = None
        log = io.BytesIO()

        with mock.patch.object(
                runner, '_find_active_job_digest',
                return_value='a' * 64) as find_digest:
            with mock.patch.object(runner, 'cancel_job') as cancel_job:
                with mock.patch.object(
                        runner, '_wait_for_canceled_job',
                        return_value=True) as wait_drain:
                    with mock.patch(
                            'run.urllib.request.urlopen',
                            return_value=io.BytesIO(json.dumps([{
                                'digest': 'a' * 64,
                                'status': 'running',
                                'picked_up_at': 100.0,
                                'meta': {'description': desc},
                            }]).encode())):
                        with mock.patch(
                                'run.time.time',
                                return_value=221.0):
                            rc = runner._watch_submit(
                                proc, log, desc, max_s=60,
                                line_prefix=None)

        self.assertEqual(rc, 1)
        self.assertTrue(runner._last_watchdog_cancel)
        find_digest.assert_called_once_with(desc)
        cancel_job.assert_called_once_with('a' * 64)
        wait_drain.assert_called_once_with(desc, 'a' * 64, log)
        proc.terminate.assert_called_once_with()
        self.assertIn(b'submit.py exceeded budget', log.getvalue())

    def test_watch_submit_drains_after_nonzero_submit_exit(self):
        desc = 'agent1: Provision SD image with SSH keys [123]'
        runner = self._runner()
        proc = mock.Mock()
        proc.poll.return_value = 2
        log = io.BytesIO()

        with mock.patch.object(
                runner, '_find_active_job_digest',
                return_value='a' * 64) as find_digest:
            with mock.patch.object(runner, 'cancel_job') as cancel_job:
                with mock.patch.object(
                        runner, '_wait_for_canceled_job',
                        return_value=True) as wait_drain:
                    rc = runner._watch_submit(
                        proc, log, desc, max_s=60, line_prefix=None)

        self.assertEqual(rc, 2)
        find_digest.assert_called_once_with(desc)
        cancel_job.assert_called_once_with('a' * 64)
        wait_drain.assert_called_once_with(desc, 'a' * 64, log)


if __name__ == '__main__':
    unittest.main()
