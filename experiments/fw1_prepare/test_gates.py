"""Only new entry and authorization checks; no policy histories in these tests."""
import copy,json,unittest
from pathlib import Path
from unittest.mock import patch
from . import entry,sources

class Gates(unittest.TestCase):
    def test_01_bound_short_configuration(self):
        c,h=entry.validate_binding(entry.CONFIGS['short'])
        entry.authorization(entry.auth_path(c),c,h)
        self.assertEqual(c['pairs'],1);self.assertEqual(c['frames'],96)
        self.assertEqual(len(c['sources']),2)

    def test_02_wrong_authorizations(self):
        c,h=entry.validate_binding(entry.CONFIGS['short']);path=entry.auth_path(c);good=json.loads(path.read_bytes())
        for changes in (dict(kind='FW1_RESEARCH_ONCE'),dict(allow_research=True),dict(allow_research=0),dict(prestart_sha256='0'*64),dict(target=str(entry.TARGET)),dict(extra=True)):
            with patch.object(Path,'read_bytes',return_value=json.dumps(good|changes).encode()),self.assertRaises(PermissionError):entry.authorization(path,c,h)
        with self.assertRaisesRegex(PermissionError,'AUTH_PATH'):entry.authorization(entry.AUTH,c,h)

    def test_03_tampered_bindings(self):
        original=entry.sha;c,h=entry.validate_binding(entry.CONFIGS['short'])
        for target,reason in [(entry.ROOT/next(iter(c['files'])),'FILE_BINDING'),(entry.PREP/'bootstrap.bin','MATRIX_BINDING'),(entry.ROOT/c['sources'][0]['path'],'SOURCE_BINDING')]:
            with patch.object(entry,'sha',lambda p:'0'*64 if Path(p)==target else original(p)),self.assertRaisesRegex(ValueError,reason):entry.validate_binding(entry.CONFIGS['short'])
        with patch.object(entry,'runtime',return_value={}),self.assertRaisesRegex(ValueError,'CONFIG_SCOPE'):entry.validate_binding(entry.CONFIGS['short'])

    def test_04_denial_before_target_and_worker(self):
        with patch.object(entry,'authorization',side_effect=PermissionError('DENIED')),patch.object(entry,'install_job') as job,patch.object(Path,'mkdir') as mkdir:
            with self.assertRaisesRegex(PermissionError,'DENIED'):entry.run(entry.CONFIGS['short'],entry.AUTH)
            mkdir.assert_not_called();job.assert_not_called()

    def test_05_existing_target_and_consumption(self):
        c,h=entry.validate_binding(entry.CONFIGS['short']);original=Path.exists
        for blocked,reason in [(Path(c['target']),'TARGET_EXISTS'),(entry.consumed_path(c),'AUTH_CONSUMED')]:
            with patch.object(Path,'exists',lambda p:p==blocked if p in (Path(c['target']),entry.consumed_path(c)) else original(p)),patch.object(entry,'install_job') as job,patch.object(Path,'mkdir') as mkdir:
                with self.assertRaisesRegex(Exception,reason):entry.run(entry.CONFIGS['short'],entry.auth_path(c))
                mkdir.assert_not_called();job.assert_not_called()

    def test_06_research_source_gate_and_auth_absence(self):
        for fn in (sources.generate,sources.reconstruct):
            with self.assertRaises(PermissionError):fn(1,neutral=False)
            with self.assertRaises(PermissionError):fn(1,neutral=False,permit=object())
        self.assertFalse(entry.AUTH.exists());self.assertFalse(entry.TARGET.exists())

    def test_07_delta_is_scope_only(self):
        # Compare inherited measured engine with the widened bound-validator entry.
        old=(entry.ROOT/'experiments/fw1/engine.py').read_text()
        old=old.replace('from .adapter import ResetAdapter','from experiments.fw1.adapter import ResetAdapter').replace('from .reference import Reference,mae','from experiments.fw1.reference import Reference,mae').replace('    if len(values)>128:raise PermissionError("RESEARCH_NOT_ADMITTED")\n','')
        self.assertEqual(old,(entry.ROOT/'experiments/fw1_prepare/engine.py').read_text())
        old=(entry.ROOT/'experiments/fw1/archive.py').read_text().replace('from .archive_reference import Reference','from experiments.fw1.archive_reference import Reference').replace("root['entry_revision']=='FW1_V1' and root['neutral_only'] is True","root['entry_revision']=='FW1_PREP_V1' and type(root['neutral_only']) is bool").replace('0<len(source)<=128','0<len(source)<=1024')
        self.assertEqual(old,(entry.ROOT/'experiments/fw1_prepare/archive.py').read_text())

if __name__=='__main__':
    from tools import _s2uc_hx1_windows as win
    entry.install_job();entry.journal('gate_tests_started',policy=0)
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Gates)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    entry.write_exclusive(entry.PREP/'gate-tests.json',dict(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),job=win.snapshot()))
    entry.journal('gate_tests_completed',tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),policy=0)
    raise SystemExit(not result.wasSuccessful())
