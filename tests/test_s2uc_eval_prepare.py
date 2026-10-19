"""Neutral preparation fixtures only. Never materialize or replay a raster case."""
import ast
import copy
import json
import tempfile
import time
import unittest
import sys
from pathlib import Path
from unittest.mock import patch

from tools import s2uc_eval_prepare as q
from tools import _s2uc_eval_source as src
from tools._s2uc_eval_assessment import aggregate, adaptation, thresholds, assess_case
from tools._s2uc_eval_evidence import select
from tools._s2uc_multi_observer import replay as historical_u
from tools._s2uc_promotion_replay import replay as historical_b

FACTS={}


def neutral(n=80, name='neutral'):
    g=list(range(3,n,2));h=list(range(7,n,4))
    return dict(id=name,frames=n,duration=0,word='N',blocks=['N']*(n//4),switches=[],stable=True,
        masks=dict(G=g,H=h,N=[t for t in g if t not in h],S=h,S_w=list(range(11,n,4)),F=[],A=[]))


def values(n):
    return [(x,)*48 for x in (1/32,7/32,19/32,29/32)*(n//4)]


def abstract_reports():
    reports=[]
    for s in src.cases():
        metrics={m:{a:dict(count=len(ts),missing=[],mae=(.125 if a=='U' else .25) if ts else None,
            error_sum=len(ts)*(.125 if a=='U' else .25)) for a in q.ARMS} for m,ts in s['masks'].items()}
        reports.append(dict(id=s['id'],duration=s['duration'],stable=s['stable'],technical_errors=[],metrics=metrics,
            switches=[dict(w,passed=True,latency=3,missing_context_targets=[]) for w in s['switches']]))
    return reports


def hang_worker(folder, charged, deadline):
    # Deliberately does not cooperate with deadline; parent must terminate it.
    time.sleep(30)


def broken_worker(folder, charged, deadline):
    q.Ledger(folder,charged,claimed=True).write('partial.json',{'neutral':True})
    raise SystemExit(7)


def complete_worker(folder,charged,deadline):
    q.Ledger(folder,charged,claimed=True).write('worker-complete.json',dict(neutral=True))


class Preparation(unittest.TestCase):
    def test_R01_complete_declarative_raster(self):
        c=src.cases()
        self.assertEqual(len(c),32);self.assertEqual(len({s['id'] for s in c}),32)
        self.assertEqual(sum(s['frames'] for s in c),2048)
        self.assertEqual(sum(s['stable'] for s in c),4)
        self.assertEqual(sum(len(s['switches']) for s in c),48)
        self.assertEqual({d:sum(len(s['switches']) for s in c if s['duration']==d) for d in (3,5)},{3:24,5:24})
        for s in c:
            self.assertEqual(sorted(s['masks']['H']+s['masks']['N']),s['masks']['G'])
            self.assertTrue(all(t in s['masks']['H'] for w in s['switches'] for t in w['targets']))
        FACTS['R01']=dict(cases=32,positions=2048,switches=48,materialized=False)

    def test_R02_generator_isolation_and_neutral_only(self):
        tree=ast.parse((q.ROOT/'tools/_s2uc_eval_source.py').read_text())
        imports=[n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
        self.assertEqual(imports,['itertools'])
        s=neutral(8);s['blocks']=['N','N']
        with patch.object(src,'cases',return_value=[s]),patch.object(src,'RECIPES',{'N':('1/32','7/32','19/32','29/32')}):
            v=src.materialize(s);src.validate(v,s)
            self.assertEqual(v,values(8))
            v[0]=(0.,)*48
            with self.assertRaisesRegex(ValueError,'SOURCE_VALUE'):src.validate(v,s)
        with self.assertRaisesRegex(ValueError,'SOURCE_SPEC'):src.materialize(s)

    def test_R03_80_neutral_positions_all_arms(self):
        s=neutral();v=values(80);r={}
        for a in q.ARMS:
            e={}
            r[a]=(q.multi_replay(v,q.digest(v),count=80,evidence=e) if a=='U' else
                q.baseline_replay(v,q.digest(v),count=80,arm=a,evidence=e))
            q.resource_check(r[a]);self.assertTrue(e['terminal_cleanup'])
            self.assertEqual(r[a]['frames'],80);self.assertEqual(r[a]['censored_target'],81)
        report=assess_case(r,v,s)
        self.assertEqual(report['technical_errors'],[])
        FACTS['R03']=dict(neutral_positions=80,experimental_admissions=400,reference_advances=400,
            resources=q.old.resource_report(r),raster_executed=False)

    def test_R04_historical_limit_unchanged_new_80_ceiling(self):
        with self.assertRaises(Exception):historical_u([], 'p',count=80)
        with self.assertRaises(Exception):historical_b([], 'p',count=80,arm='M')
        for count in (82,81,2,True):
            with self.assertRaises(Exception):q.multi_replay([], 'p',count=count)
            with self.assertRaises(Exception):q.baseline_replay([], 'p',count=count,arm='M')

    def test_R05_fresh_states_and_manifest_before_policy(self):
        specs=[neutral(12,'neutral-a'),neutral(12,'neutral-b')]
        original_u=q.multi_replay;original_b=q.baseline_replay;calls=[]
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'once';q.Ledger(folder)
            def wrap(fn, arm_label, *args, **kw):
                manifest=q.read(folder/'manifest.json');self.assertEqual(len(manifest['entries']),2)
                self.assertTrue(all((folder/e['source_file']).exists() for e in manifest['entries']))
                calls.append(arm_label);return fn(*args,**kw)
            with patch.object(q,'multi_replay',lambda *a,**kw:wrap(original_u,'U',*a,**kw)), \
                 patch.object(q,'baseline_replay',lambda *a,**kw:wrap(original_b,kw['arm'],*a,**kw)):
                q.execute(folder,specs,lambda s:values(s['frames']),lambda v,s:None,
                    dict(entries=[],scope='neutral'),0,lambda:None,
                    summarize=lambda r,s:dict(technical_errors=[],neutral=True))
            self.assertEqual(calls,list(q.ARMS)*2)
            for a in q.ARMS:
                first=q.read(folder/('neutral-a-'+a+'.json'));second=q.read(folder/('neutral-b-'+a+'.json'))
                self.assertEqual(first['rows'],second['rows'])
                ad=second['admissions'][0]
                self.assertEqual(ad['before'],[] if a=='U' else dict(candidate=None,retained=[]))
                self.assertTrue(second['terminal_cleanup'])
            FACTS['R05']=dict(serial_order=calls,all_sources_sealed_before_policy=True,fresh_states=True)

    def test_R06_feedback_causality_and_tamper(self):
        # Previously saved developmental evidence only; no evaluation source construction.
        folder=q.old.OUT
        r={a:q.read(folder/(a+'.json')) for a in q.ARMS};v=q.read(folder/'source.json')
        s=neutral(48);s['blocks']=['X']*4+['Y']*4+['X']*4
        s['switches']=[dict(wanted='Y',targets=[19,23,27,31]),dict(wanted='X',targets=[35,39,43,47])]
        self.assertEqual(assess_case(r,v,s)['technical_errors'],[])
        for kind in ('ordinal','raw','pair','future','missing','duplicate','NaN'):
            bad=copy.deepcopy(r)
            up=next(x for x in bad['U']['updates'] if x['target']==39)
            if kind=='ordinal':up['hypotheses'][0]['original_ordinal']=39
            elif kind=='raw':up['hypotheses'][0]['ec']=99
            elif kind=='pair':up['before'][0]['ep']=99
            elif kind=='future':bad['U']['forecasts'][0]['read_revision']=999
            elif kind=='missing':bad['U']['rows'].pop()
            elif kind=='duplicate':bad['U']['rows'].append(bad['U']['rows'][0])
            else:bad['P']['rows'][0]['selected_mae']=float('nan')
            self.assertTrue(assess_case(bad,v,s)['technical_errors'],kind)

    def test_R07_adaptation_deadline_cold_missing_and_regression(self):
        sw=dict(wanted='Y',targets=[7,11,15,19,23])
        rows=[dict(target=t,selected_label='Y',reason='SELECTED_BY_ERROR',strict_warm_winner=True,
            original_frozen_verified=True,prior_feedback=[7],available_labels=['X','Y']) for t in sw['targets']]
        self.assertTrue(adaptation(rows,sw)['passed'])
        for t in (15,19,23):
            for key,val in (('selected_label','P'),('reason','TIED_IMPROVEMENT'),('strict_warm_winner',False),
                ('original_frozen_verified',False),('prior_feedback',[]),('prior_feedback',[t])):
                b=copy.deepcopy(rows);next(r for r in b if r['target']==t)[key]=val
                self.assertFalse(adaptation(b,sw)['passed'])
        b=copy.deepcopy(rows);b[2]['available_labels']=[];b[2]['selected_label']='P'
        self.assertEqual(adaptation(b,sw)['missing_context_targets'],[15])
        self.assertFalse(adaptation(b,sw)['passed'])

    def test_R08_exact_39_and_18_thresholds(self):
        def ss(x,y):return [dict(duration=d,passed=i<n,missing_context_targets=[1]) for d,n in ((3,x),(5,y)) for i in range(24)]
        self.assertTrue(thresholds(ss(18,21))['passed'])
        self.assertTrue(thresholds(ss(21,18))['passed'])
        for x,y in ((18,20),(17,22),(22,17)):
            self.assertFalse(thresholds(ss(x,y))['passed'])
        self.assertFalse(thresholds(ss(24,24)[:-1])['passed'])
        self.assertEqual(thresholds(ss(18,21))['denominator'],48)

    def test_R09_equal_case_weighting_not_position_weighting(self):
        r=abstract_reports()
        for row in r:
            for m in ('G','H'):
                for a in q.ARMS:
                    x=(0. if row['duration']==3 else .75) if a=='U' else .4
                    v=row['metrics'][m][a];v.update(mae=x,error_sum=x*v['count'])
        out=aggregate(r,src.cases())
        self.assertEqual(out['summaries']['G']['U']['case_mean'],.375)
        self.assertGreater(out['summaries']['G']['U']['position_mean'],.4)
        self.assertEqual(out['verdicts']['G'],'BELEGT')

    def test_R10_strict_ties_H_G_and_selection_separate(self):
        r=abstract_reports()
        for row in r:
            row['metrics']['H']['K']=copy.deepcopy(row['metrics']['H']['U'])
            for s in row['switches']:s['passed']=False
        out=aggregate(r,src.cases())
        self.assertEqual(out['verdicts']['H'],'NICHT_NACHGEWIESEN')
        self.assertEqual(out['verdicts']['G'],'BELEGT')
        self.assertEqual(out['verdicts']['adaptation'],'NICHT_NACHGEWIESEN')
        self.assertIsNone(select({(0,1,0):(0.,.5),(0,2,0):(0.,.5)}))

    def test_R11_damage_exact_boundary_and_warm_stability(self):
        for extra,expected in ((1/32,'BELEGT'),(1/32+2**-20,'SCHADENSGRENZE_VERLETZT')):
            r=abstract_reports();m=r[0]['metrics']['G']['U'];m.update(mae=.25+extra,error_sum=(.25+extra)*m['count'])
            self.assertEqual(aggregate(r,src.cases())['verdicts']['stability_damage'],expected)
        r=abstract_reports()
        for row in r:
            if row['stable']:
                m=row['metrics']['S_w']['U'];m.update(mae=.5,error_sum=.5*m['count'])
        self.assertEqual(aggregate(r,src.cases())['verdicts']['stability_damage'],'SCHADENSGRENZE_VERLETZT')

    def test_R12_incomplete_never_positive(self):
        for kind in ('case','target','error','switch'):
            r=abstract_reports()
            if kind=='case':r.pop()
            elif kind=='target':r[0]['metrics']['G']['U']['missing']=[3]
            elif kind=='error':r[0]['technical_errors']=['broken']
            else:r[1]['switches']=[]
            out=aggregate(r,src.cases())
            self.assertFalse(out['all_criteria_met']);self.assertTrue(out['technical_errors'])
            self.assertEqual(set(out['verdicts'].values()),{'NOT_EVALUABLE'})

    def test_R13_resource_caps_and_bounds_not_measurements(self):
        v=values(12);r=q.multi_replay(v,q.digest(v),count=12)
        q.resource_check(r)
        self.assertIsNone(q.old.resource_report({'U':r})['U']['measured_original_frame_peak'])
        for key,val in (('additional_python_peak',16385),('original_frames_upper_bound',19),
            ('combined_upper_bound',21),('receipt_bytes_peak',16385),('utf8_upper',32769),('packed',417)):
            bad=copy.deepcopy(r);bad['resources'][key]=val
            with self.assertRaises(RuntimeError):q.resource_check(bad)

    def test_R14_interrupt_releases_both_adapters(self):
        for arm in q.ARMS:
            e={};calls=[]
            def check():
                calls.append(1)
                if len(calls)==9:raise TimeoutError('neutral-time')
            with self.assertRaises(TimeoutError):
                if arm=='U':q.multi_replay(values(12),q.digest(values(12)),count=12,evidence=e,check=check)
                else:q.baseline_replay(values(12),q.digest(values(12)),count=12,arm=arm,evidence=e,check=check)
            self.assertTrue(e['terminal_cleanup'])

    def test_R15_budget_shared_reserve_and_exclusive(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'only';ledger=q.Ledger(folder,charged=598305)
            self.assertEqual(ledger.LIMIT,64*1048576-598305)
            self.assertEqual(ledger.RESERVE,1048576)
            ledger.used=ledger.LIMIT-ledger.RESERVE
            with self.assertRaises(Exception):ledger.write('over.json',{'x':1})
            ledger.write('closure.json',{'status':'neutral'},final=True)
            with self.assertRaises(FileExistsError):q.supervise(folder,0,hang_worker,seconds=.2)

    def test_R16_hard_time_limit_partial_and_no_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            for target,label in ((hang_worker,'TIME_LIMIT'),(broken_worker,'WORKER_EXIT')):
                folder=Path(tmp)/label
                with self.assertRaisesRegex(RuntimeError,label):q.supervise(folder,0,target,seconds=1.5)
                c=q.read(folder/'closure.json');self.assertEqual(c['status'],'FAILED')
                self.assertFalse(c['resume_permitted'])
                if target==broken_worker:self.assertTrue((folder/'partial.json').exists())
                with self.assertRaises(FileExistsError):q.supervise(folder,0,target,seconds=.1)
                FACTS['R16-'+label]=c

    def test_R17_authorization_before_materialization(self):
        with patch.object(q,'verify'),patch.object(q,'read',return_value={'status':'PENDING'}), \
             patch.object(q,'authorization',return_value={'status':'AUTHORIZED_ONCE'}), \
             patch.object(q,'supervise') as run,patch.object(src,'materialize') as materialize:
            with self.assertRaisesRegex(RuntimeError,'AUTHORIZATION'):q.run('unused')
            run.assert_not_called();materialize.assert_not_called()

    def test_R18_overlap_marked_never_filtered(self):
        v=values(12);entry=dict(path='neutral',profile=q.digest(v),blocks=[q.digest(v[:4])],prefixes={'4':q.digest(v[:4])})
        m=q.manifest_entry(v,neutral(12),dict(entries=[entry]))
        self.assertEqual(m['novelty'],'WIEDERVERWENDET');self.assertEqual(m['full_matches'],['neutral'])
        self.assertEqual(m['overlaps'][0]['longest_common_prefix'],4)
        self.assertEqual(m['frames'],12)

    def test_R19_failure_retains_partial_before_any_next_arm(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'failure';q.Ledger(folder);calls=[]
            def fail(*a,**kw):kw['evidence']['neutral_stage']='feedback';calls.append(1);raise KeyboardInterrupt('fixture')
            with patch.object(q,'multi_replay',fail),self.assertRaises(KeyboardInterrupt):
                q.execute(folder,[neutral(12)],lambda s:values(12),lambda v,s:None,
                    dict(entries=[],scope='neutral'),0,lambda:None)
            self.assertEqual(calls,[1]);self.assertTrue((folder/'partial.json').exists())
            self.assertFalse((folder/'worker-complete.json').exists())

    def test_R20_binding_rejects_code_plan_contract_runtime_index(self):
        base=dict(code={'neutral':'h'},plan_sha256='h',contract_sha256='h',index_sha256='h',guide_sha256='h',
            python=sys.version,executable_sha256='h',previous_binding_sha256='h',
            reused_bytes=598305,reused_closures={})
        for change in (None,'code','plan_sha256','contract_sha256','index_sha256','guide_sha256','python','executable_sha256','previous_binding_sha256','reused_bytes'):
            b=copy.deepcopy(base)
            if change:b[change]='tampered'
            def reader(p):
                if p==q.BINDING:return b
                if p==q.PLAN:return json.loads(json.dumps(q.plan()))
                if p==q.INDEX:return {'entries':[]}
                raise AssertionError(p)
            with patch.object(q,'read',reader),patch.object(q,'sha',return_value='h'), \
                 patch.object(q,'code_hashes',return_value={'neutral':'h'}),patch.object(q,'prior_bytes',return_value=598305):
                if change:
                    with self.assertRaises(RuntimeError):q.verify()
                else:self.assertEqual(q.verify(),base)

    def test_R21_manifest_source_tamper_stops_before_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'tamper';q.Ledger(folder)
            def check():
                if (folder/'manifest.json').exists():
                    (folder/'neutral-source.json').write_text('[]')
            with patch.object(q,'multi_replay') as replay,self.assertRaisesRegex(RuntimeError,'SOURCE_TAMPER'):
                q.execute(folder,[neutral(12)],lambda s:values(12),lambda v,s:None,
                    dict(entries=[],scope='neutral'),0,check)
            replay.assert_not_called();self.assertTrue((folder/'partial.json').exists())

    def test_R22_partial_uses_protected_reserve(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'budget';q.Ledger(folder)
            original=q.Ledger.write
            def write(ledger,name,value,final=False):
                if name=='manifest.json':raise RuntimeError('OUTPUT_LIMIT_FIXTURE')
                return original(ledger,name,value,final=final)
            with patch.object(q.Ledger,'write',write),self.assertRaisesRegex(RuntimeError,'OUTPUT_LIMIT_FIXTURE'):
                q.execute(folder,[neutral(12)],lambda s:values(12),lambda v,s:None,
                    dict(entries=[],scope='neutral'),0,lambda:None)
            self.assertTrue((folder/'partial.json').exists())
            q.Ledger(folder,0,claimed=True).write('closure.json',{'status':'FAILED'},final=True)

    def test_R23_supervisor_complete_closure_and_consumed_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'complete';q.supervise(folder,598305,complete_worker,seconds=10)
            c=q.read(folder/'closure.json');self.assertEqual(c['status'],'COMPLETE')
            self.assertEqual(c['charged_previous_bytes'],598305)
            for n,v in c['files'].items():self.assertEqual(q.sha(folder/n),v['sha256'])
            with self.assertRaises(FileExistsError):q.supervise(folder,0,complete_worker,seconds=10)

    def test_R24_per_file_caps_and_total_structural_envelope(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger=q.Ledger(Path(tmp)/'caps')
            for name,cap in (('neutral-source.json',65536),('neutral-U.json',196608),
                             ('neutral-resources.json',32768),('neutral-U-start.json',1024),('assessment.json',524288)):
                with self.assertRaisesRegex(RuntimeError,'FILE_CAP'):ledger.write(name,'x'*cap)
        # Fixed maximum file counts; two global exports, claim/completion/start,
        # one partial and final reserve. No per-case nested ledger resets.
        bound=q.MAX_CHARGED+32*(65536+5*196608+524288+32768+5*1024)+2*524288+2*1024+q.RESERVE+q.RESERVE//2
        self.assertLess(bound,q.LIMIT)
        FACTS['R24']=dict(structural_export_upper_bound=bound,limit=q.LIMIT,reserve=q.RESERVE,
            charged_prerequisite_cap=q.MAX_CHARGED,per_file_caps_enforced=True)

    def test_R25_index_includes_array_and_wrapped_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=root/'reports/s2uc/neutral';folder.mkdir(parents=True)
            q.save(folder/'array-source.json',values(12))
            q.save(folder/'wrapped-source.json',dict(values=values(12),profile='historical-wrapper'))
            q.save(folder/'metadata-source.json',dict(description='not numeric source'))
            with patch.object(q,'ROOT',root):index=q.development_index()
            self.assertEqual(len(index['entries']),2)
            self.assertEqual(len({e['profile'] for e in index['entries']}),1)
            m=q.manifest_entry(values(12),neutral(12),index)
            self.assertEqual(len(m['full_matches']),2)
            self.assertEqual(m['novelty'],'WIEDERVERWENDET')


if __name__=='__main__':unittest.main()
