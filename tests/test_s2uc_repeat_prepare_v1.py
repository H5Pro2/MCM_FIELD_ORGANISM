"""Neutral integration only; raster materialization is explicitly forbidden."""
import copy
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch
from tools import s2uc_repeat_prepare_v1 as q
from tests.test_s2uc_eval_prepare import neutral

FACTS={}


def normal_worker(folder,charged,deadline):
    l=q.old.Ledger(folder,charged,claimed=True)
    l.write('neutral-payload.json',dict(text='a'*200000))
    l.write('worker-complete.json',dict(neutral=True))


def timeout_worker(folder,charged,deadline):time.sleep(20)


def broken_worker(folder,charged,deadline):raise SystemExit(7)


def integration_worker(folder,charged,deadline):
    def check():
        if time.monotonic_ns()>=deadline:raise TimeoutError('NEUTRAL_INTEGRATION_DEADLINE')
    specs=[]
    for name in ('N1','N2'):
        s=neutral(80,name);s['blocks']=q.leaf.audit.spec()['cases'][name];s['stable']=name=='N1';specs.append(s)
    def supply(s):return q.leaf.audit.fixture(s['id'])
    def validate(v,s):
        if json.loads(json.dumps(v))!=json.loads(json.dumps(supply(s))):raise RuntimeError('NEUTRAL_SOURCE_CHANGED')
    def summary(reports,specs):return dict(technical_errors=[e for r in reports for e in r['technical_errors']],neutral_only=True)
    original=q.integrated_baseline
    def checked(*args,**kwargs):
        if q.BudgetObserver.trace is not q.leaf.OLD:raise RuntimeError('PATCH_LEAK_BEFORE')
        with patch.object(q.old,'baseline_replay',wraps=q.old.baseline_replay) as wrapped:
            # Inspect the actual call boundary inside integrated_baseline.
            original_replay=wrapped._mock_wraps
            def active(*a,**kw):
                if q.BudgetObserver.trace is not q.FrameLeafBudgetObserver.trace:raise RuntimeError('LEAF_NOT_ACTIVE')
                manifest=q.old.read(Path(folder)/'manifest.json')
                if len(manifest['entries'])!=2:raise RuntimeError('MANIFEST_NOT_SEALED')
                return original_replay(*a,**kw)
            wrapped.side_effect=active
            result=original(*args,**kwargs)
        if q.BudgetObserver.trace is not q.leaf.OLD:raise RuntimeError('PATCH_LEAK_AFTER')
        return result
    with patch.object(q.old.source,'materialize',side_effect=AssertionError('RASTER_FORBIDDEN')),patch.object(q,'integrated_baseline',checked):
        q.execute(folder,specs,supply,validate,dict(entries=[],scope='NEUTRAL_ONLY'),charged,check,summarize=summary)


class IntegrationTests(unittest.TestCase):
    def test_I01_frozen_policy_limits_and_qualified_dependencies(self):
        p=q.plan();old=q.old.plan()
        for key in ('cases','recipes','arms','source_positions','criteria','policy_limits','file_caps','export_limit','closure_reserve','execution_seconds','preparation_and_reference_cap'):
            self.assertEqual(p[key],old[key])
        self.assertEqual(p['worker_seconds']+p['closure_seconds'],3600)
        self.assertEqual(q.verify()['code']['tools/_s2uc_frame_leaf_observer_v1.py'],q.old.sha(q.ROOT/'tools/_s2uc_frame_leaf_observer_v1.py'))
        FACTS['I01']=dict(reused='V01-V08 and frozen Raster32 preparation R01-R25',limits_unchanged=True)

    def test_I02_authorization_gate_before_any_start(self):
        expected={'status':'AUTHORIZED_ONCE','action':'KNOWN_DATA_TECHNICAL_REPEAT_ONCE'}
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'auth.json'
            for value in ({},expected|{'status':'PENDING_SEPARATE_AUTHORIZATION'},expected|{'action':'MATERIALIZE_AND_RUN_RASTER32_ONCE'}):
                q.old.save(path,value)
                with patch.object(q,'verify'),patch.object(q,'preparation_check'),patch.object(q,'authorization',return_value=expected),patch.object(q,'supervise') as start,patch.object(q.old.source,'materialize',side_effect=AssertionError('RASTER_FORBIDDEN')):
                    with self.assertRaisesRegex(RuntimeError,'EXPLICIT_SEPARATE_AUTHORIZATION'):q.run(path)
                    start.assert_not_called()
                path.unlink()
        q.validate_authorization(expected,expected)
        FACTS['I02']=dict(rejected=3,operative_start=False)

    def test_I03_watchdog_actual_closure_and_exclusive_start(self):
        facts={}
        for name,target,seconds,reserve in (('normal',normal_worker,5,1),('timeout',timeout_worker,2,.5),('broken',broken_worker,5,1)):
            folder=q.QUAL/('probe-'+name)
            if name=='normal':q.supervise(folder,0,target,seconds,reserve)
            else:
                with self.assertRaises(RuntimeError):q.supervise(folder,0,target,seconds,reserve)
            entries=[json.loads(x) for x in (folder/'lifecycle.jsonl').read_text().splitlines()]
            events={x['event']:x for x in entries};closure=q.old.read(folder/'closure.json')
            self.assertLessEqual(events['worker_end_confirmed']['monotonic_ns'],events['closure_admin_started']['monotonic_ns'])
            self.assertLessEqual(events['closure_admin_started']['monotonic_ns'],events['closure_admin_finished']['monotonic_ns'])
            self.assertFalse(events['worker_end_confirmed']['alive']);self.assertTrue(events['closure_admin_finished']['total_deadline_met'])
            self.assertEqual(events['closure_admin_finished']['closure_file_sha256'],q.old.sha(folder/'closure.json'))
            for n,v in closure['files'].items():self.assertEqual(q.old.sha(folder/n),v['sha256'])
            if name=='timeout':
                self.assertLessEqual(events['deadline_established']['worker_deadline_ns'],events['abort_requested']['monotonic_ns'])
                self.assertEqual(closure['error'],'TIME_LIMIT')
            elif name=='normal':self.assertNotIn('abort_requested',events)
            with self.assertRaises(FileExistsError):q.supervise(folder,0,target,seconds,reserve)
            facts[name]=dict(events=entries,error=closure['error'])
        FACTS['I03']=facts

    def test_I04_two_neutral_sources_integrated_full_path(self):
        folder=q.QUAL/'integration'
        q.supervise(folder,0,integration_worker,900,30)
        checks=[]
        for case in ('N1','N2'):
            for arm in q.old.ARMS:
                r=q.old.read(folder/f'{case}-{arm}.json');q.old.resource_check(r)
                self.assertTrue(r['terminal_cleanup'])
                if arm!='U':
                    previous=q.old.read(q.leaf.OUT/f'{case}-{arm}-NEW.json')
                    self.assertEqual(q.leaf.canonical(r),q.leaf.canonical(previous))
                    self.assertEqual(r['resources']['meter'],previous['resources']['meter'])
                checks.append(dict(case=case,arm=arm,resources=r['resources'],terminal_cleanup=True))
            self.assertEqual(q.old.read(folder/f'{case}-assessment.json')['technical_errors'],[])
        manifest=q.old.read(folder/'manifest.json')
        self.assertTrue(manifest['all_sources_before_policy'])
        self.assertTrue(all(e['evidence_status']==q.STATUS for e in manifest['entries']))
        self.assertEqual(q.old.read(folder/'assessment.json')['scope'],q.STATUS)
        self.assertEqual(q.old.read(folder/'worker-complete.json')['experimental_admissions'],800)
        FACTS['I04']=dict(replays=10,positions=800,reference_advances=800,baseline_equal_pairs=8,arms=checks)

    def test_I05_integrated_resource_guards(self):
        saved=q.old.read(q.QUAL/'integration/N1-M.json')
        changes=[('terminal_cleanup',False),('heap',16385),('frames',19),('slots',3),('combined',21),('receipt',16385),('utf8',32769)]
        for key,value in changes:
            r=copy.deepcopy(saved)
            if key=='terminal_cleanup':r[key]=value
            elif key=='heap':r['resources']['additional_python_peak']=value
            else:r['resources']['meter'][dict(frames='frame_peak',slots='output_slots_peak',combined='combined_peak',receipt='receipt_bytes_peak',utf8='receipt_transient_utf8_bytes_peak')[key]]=value
            with self.assertRaises(RuntimeError):q.old.resource_check(r)
        FACTS['I05']=dict(rejected_resource_violations=len(changes),additional_replays=0)

    def test_I06_known_data_evidence_and_time_reserve(self):
        registry=q.known_registry()
        self.assertEqual(len(registry['entries']),len(q.old.read(q.old.INDEX)['entries'])+32)
        profiles={e['profile'] for e in registry['entries']}
        self.assertTrue(all(e['profile'] in profiles for e in q.old.read(q.old.OUT/'manifest.json')['entries']))
        p=q.timeplan();self.assertLess(p['extrapolation']['reserve_seconds'],0)
        self.assertEqual(p['extrapolation']['limit'],3600)
        FACTS['I06']=dict(known32_profiles=True,untouched_evaluation=False,merge_permitted=False,timeplan=p)


if __name__=='__main__':unittest.main()
