"""Targeted final admission corrections; zero sources and zero policy arms."""
import json,unittest
from unittest.mock import patch
from . import entry,sources

class Revision(unittest.TestCase):
    def test_08_neutral_admission_never_mints_research_permit(self):
        with patch.object(entry,'validate_admission',return_value=({'mode':'short'},'neutral')):
            with self.assertRaisesRegex(PermissionError,'RESEARCH_SOURCE_AUTH_REQUIRED'):sources.admit('neutral-auth','neutral-target')
        self.assertIsNone(sources._PERMIT)

    def test_09_reserved_terminal_on_start_write_failure(self):
        folder=entry.PREP/'start-write-failure';consumed=entry.PREP/'start-write-failure.consumed.json'
        c={'mode':'short','target':str(folder)};original=entry.write_exclusive
        def failing(path,value):
            if path.name=='START.json':raise OSError('INJECTED_START_WRITE')
            return original(path,value)
        with patch.object(entry,'validate_binding',return_value=(c,'neutral-test')),patch.object(entry,'authorization'),patch.object(entry,'consumed_path',return_value=consumed),patch.object(entry,'install_job'),patch.object(entry,'write_exclusive',failing),patch.object(entry,'launch') as launch:
            with self.assertRaisesRegex(OSError,'INJECTED_START_WRITE'):entry.run('neutral-config','neutral-auth')
            launch.assert_not_called()
        v=json.loads((folder/'terminal.json').read_bytes())
        self.assertEqual(v['status'],'TECHNICAL_ABORT');self.assertIn('INJECTED_START_WRITE',v['first_failure'])
        self.assertTrue(v['worker_ended']);self.assertFalse(v['worker_started']);self.assertTrue(consumed.exists())

if __name__=='__main__':
    from tools import _s2uc_hx1_windows as win
    entry.install_job();entry.journal('revision_tests_started',policy=0)
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Revision))
    entry.write_exclusive(entry.PREP/'revision-tests.json',dict(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),job=win.snapshot()))
    entry.journal('revision_tests_completed',tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),policy=0)
    raise SystemExit(not result.wasSuccessful())
