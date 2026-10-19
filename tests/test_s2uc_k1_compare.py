"""Neutral comparison-envelope tests. No research materialization or replay."""
import copy
import json
import time
import unittest
from pathlib import Path
from unittest.mock import patch
from tools import s2uc_k1_compare as run
from tools import _s2uc_k1_compare_sources as source
from tools import _s2uc_k1_compare_engine as engine

OUTPUT=None


class ComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan=source.read(run.PLAN)
        # Same case count, lengths, phase/mask geometry and assessment path; different values.
        cls.neutral=copy.deepcopy(cls.plan)
        for s in cls.neutral['cases']:s['id']='N-'+s['id']
        cls.result=None

    def test_01_full_neutral_pipeline_24_cases(self):
        folder=OUTPUT/'integration'
        start=time.monotonic()
        result=run.supervise(folder,lambda:(self.neutral,0),neutral=True,seconds=300,reserve_seconds=20)
        self.assertEqual(result['status'],'COMPLETE',result)
        self.assertLess(time.monotonic()-start,300)
        final=source.read(folder/'worker-complete.json')
        self.assertEqual((final['cases'],final['arms'],final['admissions'],final['reference_advances'],final['targets']),(24,48,3584,3584,872))
        assessment=source.read(folder/'assessment.json')
        self.assertEqual(assessment['verdicts']['Technik'],'AUSWERTBAR')
        self.assertEqual(assessment['mechanism']['denominator'],624)
        self.assertEqual(assessment['diagnosis']['denominator'],324)
        self.assertEqual(assessment['adaptation']['K1']['denominator'],52)
        self.assertEqual(assessment['adaptation']['K1']['negative_controls'],20)
        self.assertGreater(assessment['prediction']['worse'],0)
        self.assertGreater(assessment['experience']['lost']['hypotheses'],0)
        self.assertGreater(assessment['experience']['gained']['hypotheses'],0)
        for n,v in result['files'].items():self.assertEqual(source.sha(folder/n),v['sha256'])

    def test_02_invalid_authorization_closes_before_worker(self):
        def invalid():raise PermissionError('EXACT_AUTHORIZATION_REQUIRED')
        result=run.supervise(OUTPUT/'bad-start',invalid,neutral=True)
        self.assertEqual(result['status'],'NOT_EVALUABLE')
        self.assertFalse(result['worker_started'])
        self.assertFalse(list((OUTPUT/'bad-start').glob('*source*')))
        self.assertEqual(set(result['verdicts'].values()),{'NOT_EVALUABLE'})

    def test_03_process_start_error_closes(self):
        r=run.supervise(OUTPUT/'process-start-error',lambda:(self.neutral,0),neutral=True,fault='start_error')
        self.assertFalse(r['worker_started']);self.assertIn('PROCESS_START_ERROR',r['error'])

    def test_04_timeout_terminates_and_closes(self):
        before=time.monotonic()
        r=run.supervise(OUTPUT/'timeout',lambda:(self.neutral,0),neutral=True,seconds=3,reserve_seconds=2,fault='hang')
        self.assertEqual(r['status'],'NOT_EVALUABLE');self.assertFalse(r['worker_alive'])
        self.assertLess(time.monotonic()-before,3)

    def test_05_worker_crash_closes(self):
        r=run.supervise(OUTPUT/'crash',lambda:(self.neutral,0),neutral=True,fault='crash')
        self.assertEqual(r['status'],'NOT_EVALUABLE');self.assertEqual(r['worker_exitcode'],9)
        self.assertFalse(r['worker_alive'])

    def test_06_worker_exception_closes(self):
        r=run.supervise(OUTPUT/'worker-error',lambda:(self.neutral,0),neutral=True,fault='worker_error')
        self.assertEqual(r['status'],'NOT_EVALUABLE')
        self.assertTrue((OUTPUT/'worker-error/worker-error.json').exists())

    def test_07_export_and_preparation_limits(self):
        d=OUTPUT/'small-ledger';d.mkdir()
        ledger=run.Ledger(d,limit=256,reserve=128)
        with self.assertRaisesRegex(ValueError,'EXPORT_LIMIT'):ledger.write('oversize.json',{'data':'x'*128})
        self.assertEqual(list(d.iterdir()),[])
        ledger.write('small.json',{'ok':True})
        r=run.supervise(OUTPUT/'preparation-overflow',lambda:(self.neutral,8*1048576+1),neutral=True)
        self.assertFalse(r['worker_started']);self.assertIn('PREPARATION_LIMIT',r['error'])

    def test_08_collision_preserves_prior_attempt(self):
        d=OUTPUT/'bad-start';before={p.name:source.sha(p) for p in d.iterdir()}
        r=run.supervise(d,lambda:(self.neutral,0),neutral=True)
        self.assertEqual(r['status'],'REJECTED_EXISTING_OUTPUT')
        self.assertEqual(before,{p.name:source.sha(p) for p in d.iterdir()})

    def test_09_evaluator_rejects_missing_targets_and_resource_overrun(self):
        folder=OUTPUT/'integration'
        reports=[source.read(folder/(s['id']+'-assessment.json')) for s in self.neutral['cases']]
        reports[0]['rows'].pop()
        with self.assertRaisesRegex(ValueError,'AGGREGATE_TARGETS'):engine.aggregate(reports,self.neutral['cases'])
        s=self.neutral['cases'][0];arms={a:source.read(folder/(s['id']+'-'+a+'.json')) for a in ('U','K1')}
        arms['K1']['resources']['additional_python_peak']=16385
        bundle=source.restore_record(source.read(folder/(s['id']+'-source.json')))
        with self.assertRaisesRegex(ValueError,'RESOURCE_LIMIT'):engine.assess_case(arms,bundle,s)

    def test_10_criteria_unchanged_and_strict(self):
        folder=OUTPUT/'integration'
        reports=[source.read(folder/(s['id']+'-assessment.json')) for s in self.neutral['cases']]
        # Synthetic equal-arm evidence: equality cannot count as mechanism or benefit.
        for r in reports:
            for row in r['rows']:
                row['arms']['K1']=copy.deepcopy(row['arms']['U']);row['delta']=0
            for mask in r['metrics']:r['metrics'][mask]['K1']=copy.deepcopy(r['metrics'][mask]['U'])
        equal=engine.aggregate(reports,self.neutral['cases'])
        self.assertEqual(equal['verdicts']['Mechanismus'],'NICHT_NACHGEWIESEN')
        self.assertEqual(equal['verdicts']['Gesamtnutzen'],'NICHT_NACHGEWIESEN')
        self.assertEqual(equal['verdicts']['Schaden'],'GRENZE_EINGEHALTEN')
        # A full-case loss above 1/32 must fail; no favorable subgroup can hide it.
        for row in reports[0]['rows']:
            row['arms']['K1']['error']=row['arms']['U']['error']+.0625
            row['delta']=.0625
        from fractions import Fraction
        for mask,ts in self.neutral['cases'][0]['masks'].items():
            reports[0]['metrics'][mask]['K1']['error_sum_exact']=str(sum((Fraction(row['arms']['K1']['error']) for row in reports[0]['rows'] if row['target'] in ts),Fraction()))
        bad=engine.aggregate(reports,self.neutral['cases'])
        self.assertEqual(bad['verdicts']['Schaden'],'SCHADENSGRENZE_VERLETZT')
        self.assertEqual(bad['verdicts']['Gesamtnutzen'],'NICHT_NACHGEWIESEN')

    def test_11_source_gate_and_neutral_isolation(self):
        for s in self.plan['cases']:
            with self.assertRaises(PermissionError):source.materialize(s)
        with patch.object(source,'decode',side_effect=AssertionError('RESEARCH_DECODE')):
            bundle=source.materialize(self.neutral['cases'][0],neutral=True)
            self.assertTrue(bundle['neutral_only'])
            self.assertTrue(all(v[0]<.25 for v in bundle['values']))

    def test_12_prestart_time_and_keyboard_abort(self):
        r=run.supervise(OUTPUT/'prestart-time',lambda:(self.neutral,0),neutral=True,seconds=2,reserve_seconds=1.999999999)
        self.assertFalse(r['worker_started']);self.assertEqual(r['status'],'NOT_EVALUABLE')
        def abort():raise KeyboardInterrupt('NEUTRAL_CANCEL')
        r=run.supervise(OUTPUT/'abort',abort,neutral=True)
        self.assertFalse(r['worker_started']);self.assertIn('KeyboardInterrupt',r['error'])

    def test_13_running_abort_and_worker_export_failure(self):
        r=run.supervise(OUTPUT/'running-abort',lambda:(self.neutral,0),neutral=True,fault='cancel')
        self.assertTrue(r['worker_started']);self.assertFalse(r['worker_alive'])
        self.assertEqual(r['status'],'NOT_EVALUABLE')
        r=run.supervise(OUTPUT/'export-failure',lambda:(self.neutral,0),neutral=True,fault='export')
        self.assertEqual(r['status'],'NOT_EVALUABLE');self.assertFalse(r['worker_alive'])
        self.assertTrue((OUTPUT/'export-failure/closure.json').exists())

    def test_14_real_authorization_validation_path(self):
        d=OUTPUT/'authorization-reject';auth=OUTPUT/'invalid-authorization.json'
        run.save(auth,dict(status='PENDING_SEPARATE_AUTHORIZATION'))
        with patch.object(run,'OUT',d),patch.object(run,'verify_prestart',return_value=None),patch.object(run,'expected_authorization',return_value={'status':'AUTHORIZED_ONCE'}):
            r=run.run(auth)
        self.assertFalse(r['worker_started']);self.assertIn('EXACT_AUTHORIZATION_REQUIRED',r['error'])
        with patch.object(run,'OUT',OUTPUT/'authorization-missing'),patch.object(run,'verify_prestart',return_value=None):
            r=run.run(OUTPUT/'missing.json')
        self.assertFalse(r['worker_started']);self.assertIn('FileNotFoundError',r['error'])

    def test_15_static_export_caps_and_file_limit(self):
        p=self.plan['export_caps']
        total=24*p['source_each']+48*p['arm_each']+24*p['case_assessment_each']+p['administrative_pool']+8*1048576+run.RESERVE
        self.assertEqual(total,p['maximum_with_preparation_and_closure'])
        self.assertLessEqual(total,run.LIMIT)
        d=OUTPUT/'file-cap';d.mkdir()
        with self.assertRaisesRegex(ValueError,'FILE_CAP:arm'):
            run.Ledger(d).write('neutral-U.json',{'data':'x'*(512*1024)})


if __name__=='__main__':unittest.main()
