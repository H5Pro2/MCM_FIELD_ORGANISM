import copy,json,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
from tools import s2uc_er1_research_prepare as entry
from tools import _s2uc_er1_run_sources as sources
from tools._s2uc_er1_run_statistics import evaluate
from tools._s2uc_ura1_fs_accounting_v4 import Terminal,Ledger
from tools._s2uc_ura1_terminal_v3 import execute_with_receipts
from tools._s2uc_er1_run_mechanisms import witnesses

class ER1Entry(unittest.TestCase):
    def test_01_research_sources_denied_without_permit(self):
        for call in (sources.generate,sources.materialize,sources.reconstruct,sources.reference_frames):
            with self.assertRaises(PermissionError):call(1,neutral=False)
        with self.assertRaises(PermissionError):sources.materialize(1,neutral=False,permit=object())
    def test_02_invalid_authorization_has_no_start_effect(self):
        with patch.object(entry,'validate_binding',return_value=({},'a'*64)),patch.object(entry,'install_job'),patch.object(Path,'read_bytes',return_value=b'{}'),patch.object(Path,'mkdir',side_effect=AssertionError('SIDE_EFFECT')):
            with self.assertRaises(PermissionError):entry.run(entry.PREP/'prestart.json',entry.AUTH)
        with self.assertRaises(PermissionError):entry.authorization(entry.ROOT/'wrong.json','a'*64)
    def test_03_exact_authorization_content(self):
        value=dict(kind='ER1_RESEARCH_ONCE',prestart_sha256='a'*64,allow_research=True)
        with patch.object(Path,'read_bytes',return_value=json.dumps(value).encode()):
            entry.authorization(entry.AUTH,'a'*64)
            with self.assertRaises(PermissionError):entry.authorization(entry.AUTH,'b'*64)
        value['extra']=True
        with patch.object(Path,'read_bytes',return_value=json.dumps(value).encode()):
            with self.assertRaises(PermissionError):entry.authorization(entry.AUTH,'a'*64)
    def test_04_consuming_marker_exclusive_no_retry(self):
        with tempfile.TemporaryDirectory(dir=entry.ROOT/'reports/s2uc') as tmp:
            prep=Path(tmp)/'neutral-prep';prep.mkdir();target=Path(tmp)/'neutral-target'
            with patch.object(entry,'PREP',prep),patch.object(entry,'TARGET',target),patch.object(entry,'install_job'),patch.object(entry,'validate_binding',return_value=({},'a'*64)),patch.object(entry,'authorization'),patch.object(entry,'launch',return_value='NEUTRAL_LAUNCH') as launch:
                self.assertEqual(entry.run(prep/'prestart.json',prep/'nonexistent-auth.json'),'NEUTRAL_LAUNCH')
                self.assertTrue(json.loads((target/'START.json').read_bytes())['consumed'])
                self.assertTrue((prep/'CONSUMED.json').exists());self.assertFalse((prep/'nonexistent-auth.json').exists())
                with self.assertRaises(PermissionError):entry.run(prep/'prestart.json',prep/'nonexistent-auth.json')
                self.assertEqual(launch.call_count,1)
    def test_05_neutral_recipe_matches_existing(self):
        from tools import _s2uc_er1_source as previous
        for r in range(1,33):
            value=sources.materialize(r);self.assertEqual(value,previous.materialize(r));self.assertTrue(sources.verify(value,r))
    def test_06_case_receipt_only_after_success(self):
        with tempfile.TemporaryDirectory(dir=entry.ROOT/'reports/s2uc') as tmp:
            terminal=Terminal(tmp,time.monotonic());ledger=Ledger(terminal)
            def fail(number,value,current):raise ValueError('INJECTED_UNVERIFIED')
            with self.assertRaises(ValueError):execute_with_receipts([(1,None)],fail,ledger,[1])
            self.assertEqual(terminal.value['completed_cases'],[])
            terminal.value['active_case']=None
            execute_with_receipts([(1,None)],lambda n,v,l:dict(replicate=n,cleanup=True),ledger,[1])
            self.assertEqual(terminal.value['completed_cases'],[1])
    def reports(self,delta=-.125,witness=True):
        m=dict(retention_events=1,warm_uses=1,local_gains=1,first_witness=dict(target=31,origin=[1,2,3,4],offset=0,prior_live_feedback=[7]) if witness else None)
        return [dict(replicate=r,orientation=(r-1)%2,complete=True,cleanup=True,integrity='PASS_DELTA_INTEGRITY',mechanisms={'E':copy.deepcopy(m),'F':copy.deepcopy(m)},executions=dict(policy=2,live_reference=2,archive_reference=2,extra_policy_measurement=0),rows=[dict(target=t,E=.25+delta,F=.25,warm=False,E_warm=False,F_warm=False) for t in range(3,1024,2)]) for r in range(1,33)]
    def test_07_full_statistics_and_mechanism_conjunction(self):
        matrix=(entry.ROOT/'reports/s2uc/ura1-v4-preparation-20261015-01/bootstrap.bin').read_bytes()
        for delta,witness,wanted in [(-.125,True,True),(-.125,False,False),(.125,True,False),(0.,True,False)]:
            summary,reference=evaluate(self.reports(delta,witness),matrix)
            self.assertEqual(summary['primary']['count'],16352)
            self.assertEqual(summary['retention_enables_useful_reuse_global'],wanted)
            self.assertEqual(summary['execution_totals']['policy'],64)
            self.assertEqual(summary['primary']['ci'],reference['ci'])
    def test_08_incomplete_or_extra_policy_execution_no_verdict(self):
        matrix=(entry.ROOT/'reports/s2uc/ura1-v4-preparation-20261015-01/bootstrap.bin').read_bytes()
        reports=self.reports();reports[0]['executions']['policy']=4
        with self.assertRaisesRegex(ValueError,'EXECUTION_COUNTS'):evaluate(reports,matrix)
        reports=self.reports();reports[0]['integrity']='FAILED'
        with self.assertRaisesRegex(ValueError,'UNVERIFIED_CASE'):evaluate(reports,matrix)
    def test_09_real_integration_receipts_and_budget_closure(self):
        for mode in ('complete','admin','export'):
            t=json.loads((entry.PREP/f'integration-{mode}/terminal.json').read_bytes())
            self.assertTrue(t['worker_ended']);self.assertTrue(t['file_cleanup_confirmed']);self.assertEqual(t['cleanup'],'CONFIRMED')
            self.assertTrue(t['sources_sealed_before_policy'])
            self.assertEqual(t['source_manifest_sha256'],entry.sha(entry.PREP/f'integration-{mode}/sources-manifest.json'))
            self.assertEqual(t['completed_cases'],[1,2] if mode=='complete' else [1])
            self.assertEqual(t['arms_created'],4 if mode=='complete' else 3)
            self.assertEqual(t['status'],'TERMINAL_COMPLETE' if mode=='complete' else 'TECHNICAL_ABORT')
        report=json.loads((entry.PREP/'integration-complete/neutral-integrity.json').read_bytes())
        self.assertEqual(sum(c['executions']['policy'] for c in report['cases']),4)
        self.assertGreater(report['cases'][0]['mechanisms']['E']['local_gains'],0)
        self.assertGreater(report['cases'][1]['mechanisms']['F']['local_gains'],0)
    def test_10_archive_tamper_and_source_reference_rejected(self):
        value=sources.materialize(1);value['ids'][0]=7
        with self.assertRaises(ValueError):sources.verify(value,1)
        from tools._s2uc_er1_run_archive import verify
        p=entry.PREP/'integration-complete';proof=json.loads((p/'case-01-capture.json').read_bytes())
        case=json.loads((p/'case-01-summary.json').read_bytes());blob=bytearray((p/'case-01.gz').read_bytes());blob[-8]^=1
        expected={k:case['resources'][k] for k in ('original_bytes','original_sha256')}
        with self.assertRaises(Exception):verify(bytes(blob),proof,expected)

    def test_11_binding_scope_coverage_and_hashes(self):
        import sys
        binding=dict(qualification={},limits=entry.LIMITS,runtime={'test':'runtime'},target=str(entry.TARGET),namespace=entry.NAMESPACE,execution_plan=entry.EXECUTION_PLAN,files={'tools/example.py':'f'*64},call=[sys.executable,'-m','tools.s2uc_er1_research_prepare','run',str(entry.PREP/'prestart.json'),str(entry.AUTH)])
        def exercise(value,valid=False):
            with patch.object(Path,'read_bytes',return_value=json.dumps(value).encode()),patch.object(Path,'read_text',return_value='d'*64),patch.object(entry,'runtime',return_value={'test':'runtime'}),patch.object(entry,'binding_paths',return_value=['tools/example.py']),patch.object(entry,'sha',side_effect=lambda p:'d'*64 if Path(p).name=='prestart.json' else 'f'*64):
                if valid:entry.validate_binding(entry.PREP/'prestart.json')
                else:
                    with self.assertRaises(ValueError):entry.validate_binding(entry.PREP/'prestart.json')
        exercise(binding,True)
        for key,value in [('target','wrong'),('namespace','wrong'),('call',[]),('execution_plan',{}),('files',{}),('files',{'tools/example.py':'wrong'}),('runtime',{}),('limits',{})]:
            altered=copy.deepcopy(binding);altered[key]=value;exercise(altered)
        with self.assertRaises(ValueError):entry.validate_binding(entry.ROOT/'wrong-prestart.json')
