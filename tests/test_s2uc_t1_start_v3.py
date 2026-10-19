"""Neutral administrative probes. No source generation or policy replay."""
import json
import time
import unittest
from pathlib import Path
from unittest.mock import patch
from tools import s2uc_t1_start_v3 as s


def neutral_worker(folder, charged, deadline):
    Path(folder, 'worker-complete.json').write_bytes(s.packed(dict(neutral_only=True, policy_replays=0, t1_sources=0)))


def waiting_worker(folder, charged, deadline):
    time.sleep(30)


class StartTests(unittest.TestCase):
    def setUp(self):
        self.folder = s.QUAL / self._testMethodName
        self.auth = dict(status='AUTHORIZED_ONCE', action='NEUTRAL_ADMIN_PROBE')
        self.guards = [patch.object(s.p.source, 'generate', side_effect=AssertionError('SOURCE_FORBIDDEN')),
                       patch.object(s.p, 'execute', side_effect=AssertionError('POLICY_FORBIDDEN'))]
        self.spies = [x.start() for x in self.guards]

    def tearDown(self):
        for spy in self.spies:
            spy.assert_not_called()
        for guard in self.guards:
            guard.stop()

    def go(self, **kw):
        return s.launch(self.folder, self.auth, self.auth, 4096, neutral_worker, seconds=15, closure_seconds=3, **kw)

    def closed_early(self):
        c = json.loads((self.folder/'closure.json').read_text())
        self.assertEqual(c['status'], 'FAILED')
        self.assertFalse(c['worker_started'])
        self.assertFalse(c['worker_alive'])
        self.assertFalse((self.folder/'worker-complete.json').exists())
        self.assertLessEqual((self.folder/'closure.json').stat().st_size, 524288)

    def test_A01_valid_actual_start_path(self):
        result = self.go()
        self.assertEqual(result['claim_bytes'], (self.folder/'claim.json').stat().st_size)
        self.assertLessEqual(result['claim_bytes'], 1024)
        c = json.loads((self.folder/'closure.json').read_text())
        self.assertEqual(c['status'], 'COMPLETE')
        self.assertEqual(c['worker_exitcode'], 0)
        claim = json.loads((self.folder/'claim.json').read_text())
        self.assertEqual(claim['accounting_sha256'], s.p.q.old.sha(self.folder/'start-accounting.json'))

    def test_A02_oversize_claim_before_reservation(self):
        original = s.start_records
        def big(*args):
            claim, accounting = original(*args)
            return claim | dict(excess='x'*1024), accounting
        with patch.object(s, 'start_records', side_effect=big):
            with self.assertRaisesRegex(RuntimeError, 'FILE_CAP:claim.json'):
                self.go()
        self.assertFalse(self.folder.exists())

    def test_A03_accounting_write_failure_terminal(self):
        with patch.object(s, 'checked_write', side_effect=OSError('INJECTED_ACCOUNTING_WRITE')):
            with self.assertRaisesRegex(RuntimeError, 'INJECTED_ACCOUNTING_WRITE'):
                self.go()
        self.closed_early()

    def test_A04_claim_partial_write_failure_terminal(self):
        original = s.checked_write
        def fail(folder, name, raw, cap, charged):
            if name == 'claim.json':
                (folder/name).write_bytes(raw[:7])
                raise OSError('INJECTED_PARTIAL_CLAIM_WRITE')
            return original(folder, name, raw, cap, charged)
        with patch.object(s, 'checked_write', side_effect=fail):
            with self.assertRaisesRegex(RuntimeError, 'INJECTED_PARTIAL_CLAIM_WRITE'):
                self.go()
        self.closed_early()
        self.assertEqual((self.folder/'claim.json').stat().st_size, 7)

    def test_A05_pending_authorization_before_reservation(self):
        with self.assertRaisesRegex(RuntimeError, 'EXPLICIT_SEPARATE_AUTHORIZATION_REQUIRED'):
            s.launch(self.folder, self.auth | dict(status='PENDING_SEPARATE_AUTHORIZATION'),
                     self.auth, 4096, neutral_worker)
        self.assertFalse(self.folder.exists())

    def test_A06_occupied_destination_untouched(self):
        self.folder.mkdir()
        (self.folder/'foreign.txt').write_bytes(b'preserve me')
        before = {p.name:p.read_bytes() for p in self.folder.iterdir()}
        with self.assertRaises(FileExistsError):
            self.go()
        self.assertEqual(before, {p.name:p.read_bytes() for p in self.folder.iterdir()})

    def test_A07_budget_before_reservation(self):
        with self.assertRaisesRegex(RuntimeError, 'EXPORT_LIMIT'):
            s.launch(self.folder, self.auth, self.auth, s.LIMIT, neutral_worker)
        self.assertFalse(self.folder.exists())

    def test_A08_timeout_confirms_worker_end(self):
        with self.assertRaisesRegex(RuntimeError, 'TIME_LIMIT'):
            s.launch(self.folder, self.auth, self.auth, 4096, waiting_worker, seconds=4, closure_seconds=2)
        c = json.loads((self.folder/'closure.json').read_text())
        self.assertTrue(c['worker_started'])
        self.assertFalse(c['worker_alive'])
        self.assertTrue(c['total_deadline_met'])

    def test_A09_process_start_failure_terminal(self):
        class FailedProcess:
            def start(self):
                raise OSError('INJECTED_PROCESS_START')
            def close(self):
                pass
        with patch.object(s.multiprocessing, 'get_context') as context:
            context.return_value.Process.return_value = FailedProcess()
            with self.assertRaisesRegex(RuntimeError, 'INJECTED_PROCESS_START'):
                self.go()
        self.closed_early()

    def test_A10_production_run_pending_never_launches(self):
        with patch.object(s, 'verify', return_value={}), \
             patch.object(s.p.q.old, 'read', side_effect=[dict(status='PASS', files={}),
                       self.auth | dict(status='PENDING_SEPARATE_AUTHORIZATION')]), \
             patch.object(s, 'authorization', return_value=self.auth), \
             patch.object(s, 'launch') as launch:
            with self.assertRaisesRegex(RuntimeError, 'EXPLICIT_SEPARATE_AUTHORIZATION_REQUIRED'):
                s.run('neutral-pending-fixture')
            launch.assert_not_called()

    def test_A11_exact_prospective_claim_and_accounting(self):
        # In-memory format specimen, never an operative authorization file.
        a = s.p.authorization('PENDING_SEPARATE_AUTHORIZATION') | dict(
            output=s.OUT.relative_to(s.ROOT).as_posix(), start_binding_sha256='0'*64,
            start_qualification_sha256='0'*64)
        claim, accounting = s.start_records(a, 8000000)
        (s.QUAL/'claim-format.json').write_bytes(s.packed(dict(claim=claim,
            claim_bytes=len(s.packed(claim)), accounting_bytes=len(s.packed(accounting)),
            specimen_status=a['status'])))
        self.assertLessEqual(len(s.packed(claim)),1024)
        self.assertLessEqual(len(s.packed(accounting)),524288)

    def test_A12_accounting_oversize_before_reservation(self):
        a = self.auth | dict(excess='x'*524288)
        with self.assertRaisesRegex(RuntimeError, 'FILE_CAP:start-accounting.json'):
            s.launch(self.folder, a, a, 4096, neutral_worker)
        self.assertFalse(self.folder.exists())
