import ast,inspect,json,unittest
from pathlib import Path
from unittest.mock import patch
from tools import s2uc_er1_v2_prepare as entry
from tools import _s2uc_er1_v2_sources as source
from tools import _s2uc_er1_run_sources as original_source
from tools import _s2uc_er1_v2_archive as archive
from tools._s2uc_ura1_delta_fast_decode import Reader

class Integrated(unittest.TestCase):
    def terminal(self,mode):return json.loads((entry.PREP/f'integration-{mode}/terminal.json').read_bytes())
    def test_01_new_scope_same_recipe_and_limits(self):
        from tools import s2uc_er1_research_prepare as old
        self.assertEqual(entry.NAMESPACE,'MCM-ER1/source/v2');self.assertEqual(source.RESEARCH,entry.NAMESPACE)
        self.assertNotEqual(entry.TARGET,old.TARGET);self.assertNotEqual(entry.AUTH,old.AUTH)
        self.assertEqual(entry.LIMITS,old.LIMITS);self.assertEqual(entry.EXECUTION_PLAN,old.EXECUTION_PLAN)
        for name in ('Stream','generate','reconstruct','materialize','reference_frames','verify'):
            self.assertEqual(ast.dump(ast.parse(inspect.getsource(getattr(source,name)))),ast.dump(ast.parse(inspect.getsource(getattr(original_source,name)))))
        with self.assertRaises(PermissionError):source.materialize(1,neutral=False)
        with self.assertRaises(PermissionError):source.materialize(1,neutral=False,permit=object())
    def test_02_actual_complete_receipts_and_generation_transition(self):
        t=self.terminal('complete');self.assertEqual(t['status'],'TERMINAL_COMPLETE');self.assertEqual(t['completed_cases'],[1,2]);self.assertEqual(t['arms_created'],4)
        report=json.loads((entry.PREP/'integration-complete/neutral-integrity.json').read_bytes())
        self.assertEqual(sum(c['executions']['policy'] for c in report['cases']),4)
        for n in (1,2):
            r=Reader((entry.PREP/f'integration-complete/case-{n:02d}.gz').read_bytes());record=r.value(r.doc['root']);self.assertEqual(record['entry_revision'],'ER1_V2')
            self.assertEqual(len(record['source']),80)
            for mode in ('E','F'):
                rows=[json.loads(b) for b in r.records(record[mode]['events']['$sequence'])]
                state=next(x['state'] for x in rows if x['stage']=='perception:after' and x['state']['accepted']==80)
                self.assertEqual(state['stock']['observation_end'],{'9':72,'10':80})
    def test_03_semantic_negatives_after_valid_test_hashes(self):
        for mode,reason in [('endmark','ARCHIVE_STOCK'),('order','ARCHIVE_STOCK'),('observer_order','ARCHIVE_OBSERVER')]:
            t=self.terminal(mode);self.assertEqual(t['status'],'TECHNICAL_ABORT');self.assertEqual(t['first_failure'],'ValueError:'+reason)
            self.assertEqual(t['completed_cases'],[1]);self.assertEqual(t['active_case'],2);self.assertEqual(t['arms_created'],4)
            self.assertFalse((entry.PREP/f'integration-{mode}/case-02-summary.json').exists())
            self.assertTrue((entry.PREP/f'integration-{mode}/case-02-capture.json').exists())
            self.assertTrue((entry.PREP/f'integration-{mode}/case-02.gz').exists())
        # The integrated verifier performs unchanged capture integrity before these semantic checks.
        text=inspect.getsource(archive.verify)
        self.assertLess(text.index('report=integrity('),text.index("'ARCHIVE_STOCK'"))
    def test_04_failed_reference_and_exhausted_report_budget(self):
        t=self.terminal('endmark_budget');self.assertEqual(t['first_failure'],'ValueError:ARCHIVE_STOCK');self.assertEqual(t['completed_cases'],[1])
        self.assertEqual(t['status'],'TECHNICAL_ABORT');self.assertTrue((entry.PREP/'integration-endmark_budget/neutral-budget.txt').exists())
        self.assertFalse((entry.PREP/'integration-endmark_budget/worker.json').exists())
        self.assertTrue(t['followup_failures'] or 'last_followup_location' in t)
    def test_05_all_terminal_cleanup_and_source_barriers(self):
        for mode in ('complete','endmark','order','observer_order','endmark_budget'):
            t=self.terminal(mode);self.assertEqual(t['cleanup'],'CONFIRMED');self.assertTrue(t['worker_ended']);self.assertTrue(t['file_cleanup_confirmed']);self.assertEqual(t['partial_files'],[])
            self.assertTrue(t['sources_sealed_before_policy']);self.assertEqual(t['source_manifest_sha256'],entry.sha(entry.PREP/f'integration-{mode}/sources-manifest.json'))
    def test_06_new_authorization_kind_and_no_creation(self):
        old=dict(kind='ER1_RESEARCH_ONCE',prestart_sha256='a'*64,allow_research=True)
        with patch.object(Path,'read_bytes',return_value=json.dumps(old).encode()):
            with self.assertRaises(PermissionError):entry.authorization(entry.AUTH,'a'*64)
        new=old|dict(kind='ER1_V2_RESEARCH_ONCE')
        with patch.object(Path,'read_bytes',return_value=json.dumps(new).encode()):entry.authorization(entry.AUTH,'a'*64)
        self.assertFalse(entry.AUTH.exists());self.assertFalse(entry.TARGET.exists());self.assertFalse((entry.PREP/'CONSUMED.json').exists())
    def test_07_accepted_comparator_and_fault_scope(self):
        from tools._s2uc_er1_stock_structural import stock_equal,structured_equal
        self.assertIs(archive.stock_equal,stock_equal);self.assertIs(archive.structured_equal,structured_equal)
        from tools._s2uc_er1_v2_series import policy_case
        with self.assertRaises(PermissionError):policy_case(1,None,None,neutral=False,fault='endmark')
