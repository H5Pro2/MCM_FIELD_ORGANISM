import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from tools._s2uc_ura1_terminal_v3 import Terminal, ReservedLedger, supervise, LIMITS, SLOT


class TerminalTests(unittest.TestCase):
    def probe(self, mode):
        with tempfile.TemporaryDirectory() as folder:
            limits = dict(LIMITS)
            limits.update(export=SLOT+2048, administration=512, closure=SLOT+512)
            t = Terminal(folder, time.monotonic(), limits=limits)
            ledger = ReservedLedger(t)
            if mode == 'export':
                (Path(folder)/'filled.gz').write_bytes(b'x'*2048)
                command = [sys.executable, '-c', 'import time;time.sleep(.05)']
                writer = lambda l:l.write('worker.json', {'status':'TECHNICAL_ABORT'})
            elif mode == 'admin':
                (Path(folder)/'filled.txt').write_bytes(b'x'*512)
                command = [sys.executable, '-c', 'pass']
                writer = lambda l:l.write('worker.json', {'status':'TECHNICAL_ABORT'})
            elif mode == 'deadline':
                command = [sys.executable, '-c', 'import time;time.sleep(10)']
                writer = None
            elif mode == 'first':
                t.fail('ORIGINAL_FAILURE');t.completed(1, True)
                command = [sys.executable, '-c', 'pass']
                writer = lambda l:(_ for _ in ()).throw(OSError('WORKER_REPORT_FAILED'))
            else:
                command = [sys.executable, '-c', 'raise SystemExit(7)']
                writer = None
            v = supervise(t, command, ledger, worker_deadline=.1 if mode=='deadline' else 5, report_writer=writer)
            persisted = json.loads(t.path.read_bytes())
            self.assertEqual(persisted, v)
            self.assertTrue(v['worker_ended'])
            self.assertEqual(t.path.stat().st_size, SLOT)
            self.assertLessEqual(sum(p.stat().st_size for p in Path(folder).iterdir()), limits['export'])
            self.assertEqual(v['status'], 'TECHNICAL_ABORT')
            return v

    def test_T01_export_report_failure(self):
        self.assertIn('EXPORT_LIMIT', self.probe('export')['first_failure'])

    def test_T02_admin_report_failure(self):
        self.assertIn('CATEGORY_LIMIT:admin', self.probe('admin')['first_failure'])

    def test_T03_deadline_saved(self):
        v = self.probe('deadline')
        self.assertIn('WORKER_DEADLINE', v['first_failure'])
        self.assertEqual(v['cleanup'], 'UNCONFIRMED')

    def test_T04_first_cause_and_progress(self):
        v = self.probe('first')
        self.assertEqual(v['first_failure'], 'ORIGINAL_FAILURE')
        self.assertEqual(v['completed_cases'], [1])
        self.assertTrue(any('WORKER_REPORT_FAILED' in x for x in v['followup_failures']))

    def test_T05_missing_worker_report(self):
        self.assertEqual(self.probe('exit')['first_failure'], 'WORKER_EXIT:7')

    def test_T06_reserve_admission(self):
        with tempfile.TemporaryDirectory() as folder:
            limits = dict(LIMITS, export=SLOT-1)
            with self.assertRaisesRegex(ValueError, 'RESERVE_EXPORT'):
                Terminal(folder, time.monotonic(), limits=limits)
            self.assertFalse((Path(folder)/'terminal.json').exists())

    def test_T07_global_reserve(self):
        with tempfile.TemporaryDirectory() as folder:
            t = Terminal(folder, time.monotonic()-6, limits=dict(LIMITS, total_seconds=10))
            v = supervise(t, [sys.executable,'-c','pass'], ReservedLedger(t))
            self.assertIn('GLOBAL_CLOSING_RESERVE', v['first_failure'])
            self.assertFalse(v['worker_started'])

    def test_T08_worker_adapter_records_before_report_failure(self):
        from unittest.mock import patch
        from tools import s2uc_ura1_prepare_v2 as original
        from tools._s2uc_ura1_terminal_v3 import worker_adapter
        with tempfile.TemporaryDirectory() as folder:
            started = time.monotonic()
            terminal = Terminal(folder, started)
            def fake_worker(start):
                ledger = original.Ledger(folder, start, 0)
                def case(number, material, current):
                    return dict(replicate=number, cleanup=True)
                original.execute([(1,None)], case, ledger, [1])
                (Path(folder)/'filled.txt').write_bytes(b'x'*LIMITS['administration'])
                ledger.write('worker.json', dict(status='TECHNICAL_ABORT', first_failure='FIRST_WORKER_ERROR'))
            with patch.object(original, 'TARGET', Path(folder)), patch.object(original, 'research_worker', fake_worker):
                with self.assertRaisesRegex(ValueError, 'CATEGORY_LIMIT'):
                    worker_adapter(started)
            terminal.refresh()
            self.assertEqual(terminal.value['first_failure'], 'FIRST_WORKER_ERROR')
            self.assertEqual(terminal.value['completed_cases'], [1])
            self.assertEqual(terminal.value['cleanup'], 'CONFIRMED')

if __name__ == '__main__':
    unittest.main()
