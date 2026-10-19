"""Neutral identifiers only; no evaluation hashes, sources or pilot replays."""
import ast
import copy
import inspect
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools import s2uc_t1_prepare as p
from tools import _s2uc_t1_evidence as ev


class StaticTests(unittest.TestCase):
    def test_T01_policy_blind_generator_and_neutral_namespace(self):
        tree=ast.parse(inspect.getsource(p.source))
        imports=[n.names[0].name for n in ast.walk(tree) if isinstance(n,ast.Import)]
        self.assertEqual(imports,['hashlib']);self.assertFalse(any(isinstance(n,ast.ImportFrom) for n in ast.walk(tree)))
        original=p.source.word;seen=[]
        def guarded(namespace,*args):
            self.assertEqual(namespace,p.source.NEUTRAL);seen.append(args);return original(namespace,*args)
        s=p.source.specification('neutral-source',301,'QA',((4,'C',0),(1,'I',1),(3,'R',1)))
        with patch.object(p.source,'word',guarded):
            b=p.source.generate(s);p.source.validate(b,s)
        self.assertTrue(seen);self.assertNotIn(('draw',301,'QA',1),seen)
        self.assertEqual(len(b['values']),8)
        self.assertTrue(all(len(set(v))>1 for v in b['values']))
        with patch.object(p.source,'word',side_effect=AssertionError('HASH_FORBIDDEN')):
            with self.assertRaises(PermissionError):p.source.generate(s,namespace=p.source.EVALUATION)

    def test_T02_formula_endianness_and_transition_no_reset(self):
        s=p.source.specification('neutral-formula',302,'QB',((2,'C',0),(2,'R',1),(2,'I',1),(2,'H',0)))
        def known(namespace,kind,*args):
            self.assertEqual(namespace,p.source.NEUTRAL)
            return bytes([1,2])+bytes(30) if kind=='vector' else bytes(32)
        with patch.object(p.source,'word',known):b=p.source.generate(s)
        self.assertEqual(b['library'][0][0][0],.5+259/262144)
        self.assertEqual(b['states'],[0,1,0,7,0,0,0,0])
        self.assertIsNone(b['modal'][4]);self.assertEqual(b['banks'],[0,0,1,1,1,1,0,0])

    def test_T03_complete_neutral_denominators_and_negative_controls(self):
        specs=p.source.cases(neutral=True)
        self.assertEqual(len(specs),16);self.assertEqual(sum(s['frames'] for s in specs),1280)
        self.assertEqual(sum(len(s['phases'])-1 for s in specs),52)
        self.assertEqual(sum(x['negative_control'] for s in specs for x in s['phases'][1:]),20)
        self.assertTrue(any(not x['targets'] for s in specs for x in s['phases'][1:]))
        self.assertTrue(all(s['masks']['G_w']==list(range(11,80,2)) for s in specs if s['stable']))

    def test_T04_lossless_codec_and_provenance(self):
        s=p.source.specification('neutral-codec',303,'QD',((80,'C',0),));b=p.source.generate(s)
        encoded=p.encode(b['values']);self.assertLess(len(json.dumps(encoded)),65536)
        self.assertEqual(p.decode(encoded),b['values'])
        self.assertEqual(p.restore(p.decode(encoded),{k:v for k,v in b.items() if k not in ('values','modal')}),b)
        bad=encoded|dict(data=encoded['data'][:-4])
        with self.assertRaises(ValueError):p.decode(bad)

    def test_T05_modal_mechanism_is_not_realized_error(self):
        s=p.source.specification('neutral-phase',304,'QE',((2,'C',0),(6,'R',0)))
        s['phases'][1]['targets']=[5,7]
        desired=[.625]*48;actual=[.7]*48
        b=dict(values=[actual]*8,modal=[desired]*8)
        decisions=[dict(target=t,selected_key=[0,1,0],selected_label=ev.digest(desired),reason='SELECTED_BY_ERROR',
            strict_warm_winner=True,original_frozen_verified=True,prior_feedback=[3]) for t in (5,7)]
        w=p.assessment.transitions(decisions,s,b)[0]
        self.assertTrue(w['passed']);self.assertNotEqual(w['details'][0]['modal_profile'],w['details'][0]['actual_profile'])
        decisions[1]['prior_feedback']=[1]
        self.assertFalse(p.assessment.transitions(decisions,s,b)[0]['passed'])
        s['phases'][1]['targets']=[]
        self.assertFalse(p.assessment.transitions([],s,b)[0]['passed'])

    def test_T06_aggregate52_fixed_late_window_and_controls(self):
        specs=p.source.cases(neutral=True);reports=[]
        for s in specs:
            switches=[dict(case=s['id'],replicate=s['replicate'],**x,passed=False) for x in s['phases'][1:]]
            metrics={m:{a:dict(count=len(ts),missing=[],error_sum=0.,mae=0. if ts else None) for a in p.q.old.ARMS} for m,ts in s['masks'].items()}
            reports.append(dict(id=s['id'],replicate=s['replicate'],technical_errors=[],switches=switches,metrics=metrics,decisions=[]))
        r=p.assessment.aggregate(reports,specs)
        self.assertEqual(r['adaptation']['denominator'],52);self.assertEqual(r['negative_controls']['count'],20)
        self.assertFalse(r['negative_controls']['prediction_failure_implied'])
        self.assertEqual(r['verdicts']['G'],'NICHT_NACHGEWIESEN')
        self.assertEqual(r['verdicts']['stability_damage'],'BELEGT')
        reports[0]['metrics']['G']['U']['missing']=[3]
        self.assertTrue(all(x=='NOT_EVALUABLE' for x in p.assessment.aggregate(reports,specs)['verdicts'].values()))

    def test_T07_provenance_overlap_does_not_select_cases(self):
        a=[[.6]*48,[.7]*48,[.6]*48,[.7]*48]
        index=dict(entries=[dict(path='neutral-only',profile=p.q.old.digest(a))],fingerprints=p.fingerprints(a))
        overlap=p.overlaps(a,index)
        self.assertEqual(overlap['full_matches'],['neutral-only'])
        self.assertTrue(all(overlap['shared'][str(n)] for n in (1,2,4)))

    def test_T08_gate_before_worker_and_source(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'pending.json';p.q.old.save(f,{'status':'PENDING'})
            with patch.object(p,'preparation_check'),patch.object(p,'authorization',return_value={'status':'AUTHORIZED_ONCE'}),\
                 patch.object(p,'supervise') as worker,patch.object(p.source,'generate') as generator:
                with self.assertRaisesRegex(RuntimeError,'EXPLICIT_SEPARATE_AUTHORIZATION'):p.run(f)
                worker.assert_not_called();generator.assert_not_called()

    def test_T09_reused_watchdog_and_real_abort(self):
        from tests.test_s2uc_repeat_prepare_v2 import normal_worker,timeout_worker
        self.assertIs(p.supervise.__code__,p.q.supervise.__code__)
        with tempfile.TemporaryDirectory() as d:
            normal=Path(d)/'normal';failed=Path(d)/'timeout'
            p.supervise(normal,0,normal_worker,5,1)
            with self.assertRaisesRegex(RuntimeError,'TIME_LIMIT'):p.supervise(failed,0,timeout_worker,2,.5)
            for folder in (normal,failed):
                events={x['event']:x for x in map(json.loads,(folder/'lifecycle.jsonl').read_text().splitlines())}
                self.assertFalse(events['worker_end_confirmed']['alive'])
                self.assertTrue(events['closure_admin_finished']['total_deadline_met'])
                self.assertEqual(events['closure_admin_finished']['closure_file_sha256'],p.q.old.sha(folder/'closure.json'))
            with self.assertRaises(FileExistsError):p.supervise(normal,0,normal_worker,5,1)


class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec=p.source.specification('neutral-hold',201,'QH',((80,'H',0),))
        cls.bundle=p.restore(p.decode(p.q.old.read(p.NEUTRAL/'neutral-hold-source.json')),
            p.q.old.read(p.NEUTRAL/'neutral-hold-provenance.json'))
        cls.results={a:p.q.old.read(p.NEUTRAL/f'neutral-hold-{a}.json') for a in p.q.old.ARMS}

    def test_T10_live_five_arm_evidence_and_cleanup(self):
        for case in ('neutral-hold','neutral-change'):
            report=p.q.old.read(p.NEUTRAL/f'{case}-assessment.json')
            self.assertEqual(report['technical_errors'],[])
            for a in p.q.old.ARMS:
                r=p.q.old.read(p.NEUTRAL/f'{case}-{a}.json');p.q.old.resource_check(r)
                self.assertTrue(r['terminal_cleanup']);self.assertEqual(r['censored_target'],81)
        self.assertEqual(p.q.old.read(p.NEUTRAL/'worker-complete.json')['namespace'],p.source.NEUTRAL)

    def test_T11_mutated_provenance_feedback_and_choice_rejected(self):
        for mutation in ('state','ordinal','feedback','choice','missing'):
            r=copy.deepcopy(self.results)
            if mutation=='state':r['U']['states'][0]='forged'
            elif mutation=='ordinal':
                u=next(x for x in r['U']['updates'] if x['hypotheses']);u['hypotheses'][0]['original_ordinal']=80
            elif mutation=='feedback':
                u=next(x for x in r['U']['updates'] if x['hypotheses']);u['hypotheses'][0]['ec']+=.125
            elif mutation=='choice':r['U']['rows'][0]['choice']=99
            else:r['U']['rows'].pop()
            self.assertTrue(p.assessment.assess_case(r,self.bundle,self.spec)['technical_errors'],mutation)

    def test_T12_complete_match_set_and_resource_overflow(self):
        r=copy.deepcopy(self.results)
        f=next(x for x in r['U']['forecasts'] if x['matches'])
        t=f['input_indices'][-1]+1;f['matches'].pop();f['hypotheses'].pop()
        next(x for x in r['M']['forecasts'] if x['target']==t)['receipt']['matches'].pop()
        self.assertTrue(p.assessment.assess_case(r,self.bundle,self.spec)['technical_errors'])
        for arm in ('U','M'):
            r=copy.deepcopy(self.results[arm]);r['resources']['additional_python_peak']=16385
            with self.assertRaisesRegex(RuntimeError,'PYTHON_LIMIT'):p.q.old.resource_check(r)
