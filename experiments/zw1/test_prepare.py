"""Only new integration/admission checks; inherited unit suites are not replayed."""
import ast,json,unittest,copy
from pathlib import Path
from unittest.mock import patch
from . import prepare as entry,prepare_sources as src,sources

class Preparation(unittest.TestCase):
    def test_01_neutral_recipe_equivalence(self):
        for pair in (1,2):
            for blocks in (24,256):
                self.assertEqual(src.generate(pair,blocks),sources.generate(pair,blocks))
                self.assertEqual(src.reconstruct(pair,blocks),sources.reconstruct(pair,blocks))
    def test_02_research_source_gate(self):
        for f in (src.generate,src.reconstruct):
            with self.assertRaises(PermissionError):f(1,neutral=False)
            with self.assertRaises(PermissionError):f(1,neutral=False,permit=object())
        with self.assertRaises(Exception):src.admit(entry.AUTH,entry.TARGET)
    def test_03_authorization_exact(self):
        data=dict(kind='ZW1_RESEARCH_ONCE',prestart_sha256='a'*64,allow_research=True)
        with patch.object(Path,'read_bytes',return_value=json.dumps(data).encode()):entry.authorization(entry.AUTH,'a'*64)
        for bad in (data|dict(kind='ER1_V2_RESEARCH_ONCE'),data|dict(allow_research=1),data|dict(prestart_sha256='b'*64)):
            with patch.object(Path,'read_bytes',return_value=json.dumps(bad).encode()):
                with self.assertRaises(PermissionError):entry.authorization(entry.AUTH,'a'*64)
    def test_04_full_binding_coverage(self):
        files=set(entry.binding_paths())
        self.assertTrue({p.relative_to(entry.ROOT).as_posix() for p in (entry.ROOT/'experiments/zw1').rglob('*') if p.is_file()}<=files)
        self.assertEqual(entry.EXECUTION_PLAN['pairs'],16);self.assertEqual(entry.EXECUTION_PLAN['policy'],64)
        self.assertEqual(entry.sha(entry.PREP/'bootstrap.bin'),entry.MATRIX_SHA)
    def test_05_actual_supervised_integrations(self):
        for mode in entry.MODES:
            t=json.loads((entry.PREP/f'integration-{mode}/terminal.json').read_bytes())
            self.assertTrue(t['worker_ended']);self.assertTrue(t['file_cleanup_confirmed']);self.assertEqual(t['cleanup'],'CONFIRMED')
            self.assertTrue(t['job']['hard_job_limit']);self.assertLess(t['job']['peak_job_committed_bytes'],entry.LIMITS['job'])
            self.assertEqual(t['completed_cases'],[1,2] if mode=='complete' else [] if mode=='source_failure' else [1])
            self.assertEqual(t['status'],'TERMINAL_COMPLETE' if mode=='complete' else 'TECHNICAL_ABORT')
            self.assertEqual(t['arms_created'],0 if mode=='source_failure' else 4 if mode=='deadline' else 8)
            self.assertEqual(t['arms_closed'],t['arms_created'])
            for r in t.get('pair_arm_counts',[]):self.assertEqual((r['arms'],r['distinct'],r['cleanup']),(4,4,True))
    def test_06_actual_errors_and_unquittied_pair(self):
        for mode,needle in (('archive_failure','PRIOR_RECORD_HASH'),('archive_budget','PRIOR_RECORD_HASH'),('source_failure','SOURCE_CHANGED'),('deadline','WORKER_DEADLINE')):
            folder=entry.PREP/f'integration-{mode}';t=json.loads((folder/'terminal.json').read_bytes())
            self.assertIn(needle,t['first_failure']);self.assertFalse((folder/'pair-02-receipt.json').exists())
        self.assertFalse((entry.PREP/'integration-archive_budget/worker.json').exists())
        t=json.loads((entry.PREP/'integration-archive_budget/terminal.json').read_bytes());self.assertTrue(t['followup_failures'])
    def test_07_statistics_unchanged_and_compact(self):
        old=entry.ROOT/'reports/s2uc/zw1-neutral-preparation-20261018-01/dependencies.json'
        files=json.loads(old.read_bytes())['files']
        for name in ('statistics.py','matrix.py','integration.py','sources.py'):
            path='experiments/zw1/'+name;self.assertEqual(entry.sha(entry.ROOT/path),files[path])
        receipt=json.loads((entry.PREP/'integration-complete/pair-01-receipt.json').read_bytes())
        for c in receipt['conditions'].values():
            self.assertEqual(set(c),{'pair','condition','complete','cleanup','integrity','targets','E','F'})
    def test_08_no_research_created(self):
        self.assertFalse(entry.AUTH.exists());self.assertFalse(entry.TARGET.exists());self.assertFalse((entry.PREP/'CONSUMED.json').exists())
    def test_09_entry_order_and_revision_only(self):
        tree=ast.parse((entry.ROOT/'experiments/zw1/prepare.py').read_text())
        run=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='run')
        text=ast.unparse(run)
        self.assertLess(text.index('validate_binding'),text.index('TARGET.mkdir'))
        self.assertLess(text.index('authorization('),text.index('TARGET.mkdir'))
        self.assertLess(text.index('AUTH_ALREADY_CONSUMED'),text.index('TARGET.mkdir'))
        old=(entry.ROOT/'tools/_s2uc_er1_v2_archive.py').read_text()
        new=(entry.ROOT/'experiments/zw1/prepare_archive.py').read_text()
        self.assertEqual(old.replace("'ER1_V2'","'ZW1_V1'"),new)
    def test_10_binding_tampering_rejected(self):
        path=entry.PREP/'prestart.json';digest='c'*64
        template=dict(kind='ZW1_PRESTART',limits=entry.LIMITS,runtime=entry.runtime(),target=str(entry.TARGET),namespace=entry.NAMESPACE,call=entry.exact_call(),execution_plan=entry.EXECUTION_PLAN,files={n:entry.sha(entry.ROOT/n) for n in entry.binding_paths()},qualification={})
        cases=[]
        bad=copy.deepcopy(template);bad['namespace']='wrong';cases.append((bad,'PRESTART_SCOPE'))
        bad=copy.deepcopy(template);bad['files'].pop('experiments/zw1/prepare_sources.py');cases.append((bad,'BINDING_COVERAGE'))
        bad=copy.deepcopy(template);bad['files']['experiments/zw1/prepare_sources.py']='0'*64;cases.append((bad,'FILE_BINDING'))
        bad=copy.deepcopy(template);bad['call'][0]='wrong';cases.append((bad,'PRESTART_EXECUTION'))
        original_read=Path.read_bytes;original_sha=entry.sha
        for bad,reason in cases:
            with patch.object(Path,'read_bytes',lambda p:json.dumps(bad).encode() if p==path else original_read(p)),patch.object(Path,'read_text',return_value=digest),patch.object(entry,'sha',lambda p:digest if p==path else original_sha(p)):
                with self.assertRaisesRegex(ValueError,reason):entry.validate_binding(path)
    def test_11_no_target_on_missing_auth_or_consumed(self):
        with patch.object(entry,'install_job'),patch.object(entry,'validate_binding',return_value=({},'a'*64)),patch.object(entry,'authorization',side_effect=PermissionError('DENIED')),patch.object(Path,'mkdir') as mkdir:
            with self.assertRaises(PermissionError):entry.run(entry.PREP/'prestart.json',entry.AUTH)
            mkdir.assert_not_called()
        with patch.object(entry,'install_job'),patch.object(entry,'validate_binding',return_value=({},'a'*64)),patch.object(entry,'authorization'),patch.object(Path,'exists',return_value=True),patch.object(Path,'mkdir') as mkdir:
            with self.assertRaisesRegex(PermissionError,'AUTH_ALREADY_CONSUMED'):entry.run(entry.PREP/'prestart.json',entry.AUTH)
            mkdir.assert_not_called()

if __name__=='__main__':unittest.main()
