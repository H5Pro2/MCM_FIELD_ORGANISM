import json,unittest
from pathlib import Path
from unittest.mock import patch
from tools._s2uc_origin_judge import replay,judge,Truth,aggregate,GatedReplay,evaluate_case
from tools._s2uc_factor_recency import FactorRecencyArm
from tools._s2uc_continuation_adapter import ContinuationAdapter
from tools.s2uc_known_origin_material_plan import plan,validate
ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'reports/s2uc/pcm-temporal-20260930-01/result.json').read_text())
V=[tuple(x['projection']['values']) for x in d['processed'][:4]];P=d['processed'][0]['projection']['profile_digest']
FACTS={}
class JudgeTests(unittest.TestCase):
    def test_T0_N3_same_system_output_different_truth(self):
        t0=replay(V+V+V[:3],P,11);n3=replay(V+V+[V[0],V[1],V[1]],P,11)
        x=t0['targets'][-1];y=n3['targets'][-1]
        self.assertEqual(x['forecast'],y['forecast']);self.assertEqual(t0['states'][:10],n3['states'][:10])
        FACTS['T0_N3_identical_forecast']=True
        self.assertEqual(judge(x,Truth('A',True,{(1,2,3,4):'A'}))['origin_category'],'CORRECT')
        wrong=judge(y,Truth('D',False,{(1,2,3,4):'A'}));self.assertEqual(wrong['origin_category'],'WRONG');self.assertLess(wrong['paired_delta'],0)
        self.assertEqual(judge(x,Truth('D',False,{(1,2,3,4):'A'}))['origin_category'],'WRONG')
    def test_candidate_and_retained_roles(self):
        for stream,role in [(V+V[:3],'candidate'),(V+V+V[:3],'retained')]:
            r=replay(stream,P,len(stream));j=judge(r['targets'][-1],Truth('A',True,{(1,2,3,4):'A'}))
            self.assertEqual(j['role'],role);self.assertEqual(j['origin_category'],'CORRECT');self.assertTrue(r['slots_released'])
            self.assertEqual(r['admitted'],list(range(1,len(stream)+1)))
    def test_ambiguity_is_not_resolved_with_labels(self):
        b=[V[0],V[1],V[3],V[2]];r=replay(V+V+b+b+b[:3],P,19)
        j=judge(r['targets'][-1],Truth('D',True,{(1,2,3,4):'A',(9,10,11,12):'D'}))
        self.assertEqual(j['origin_category'],'AMBIGUOUS');self.assertFalse(j['context_covered'])
    def test_abstention_and_full_coverage(self):
        r=replay(V[:3],P,3);j=judge(r['targets'][0],Truth('B',False,{}));s=aggregate([j])
        self.assertEqual(j['origin_category'],'ABSTAIN');self.assertTrue(j['correct_rejection'])
        self.assertIsNone(s['paired']['delta']);self.assertEqual(s['full_coverage']['delta'],0);self.assertEqual(s['context_coverage'],0)
    def test_known_mae_and_harm_preserved(self):
        f=dict(provenance_json=json.dumps({'matches':[]}),persistence_values=[0.]*48,context_values=[1.]*48,status='NEUTRAL_SCORE_ONLY')
        j=judge(dict(target=3,forecast=f,actual=[.25]*48),Truth('X',True,{}));s=aggregate([j])
        self.assertEqual(j['persistence_mae'],.25);self.assertEqual(j['context_mae'],.75);self.assertEqual(j['paired_delta'],-.5)
        self.assertEqual(len(s['harm_rows']),1);self.assertEqual(s['full_coverage']['delta'],-.5)
    def test_gate_before_iterator_pull(self):
        calls=[]
        def iterator():
            for i in range(3):calls.append(i);yield V[i]
        a=ContinuationAdapter(FactorRecencyArm(P,'owner'),'stream');s=GatedReplay(iterator(),P)
        for _ in range(2):a.accept_perception(s.take(a))
        a.release_prediction()
        with self.assertRaisesRegex(ValueError,'FUTURE_BEFORE_FORECAST'):s.take(a)
        self.assertEqual(calls,[0,1]);self.assertTrue(a.closed and s.closed)
    def test_unbound_origin_rejected(self):
        r=replay(V+V+V[:3],P,11)
        with self.assertRaisesRegex(ValueError,'UNBOUND_ORIGIN'):judge(r['targets'][-1],Truth('A',True,{}))
    def test_factor_recognition_without_prediction(self):
        half=[tuple(x*.5 for x in v) for v in V[:3]]
        r=replay(V+V+half,P,11);j=judge(r['targets'][-1],Truth('A',True,{(1,2,3,4):'A'},'P1-neutral'))
        self.assertEqual(j['origin_category'],'CORRECT');self.assertFalse(j['context_covered'])
        self.assertEqual(j['prediction_status'],'FACTOR_CONTINUATION_NOT_SPECIFIED')
    def test_evaluator_learning_separation_and_budget(self):
        r=evaluate_case(V+V+V[:3],P,11,11,Truth('A',True,{(1,2,3,4):'A'},'T0-regression'),measure_resources=True)
        self.assertEqual(r['learning_targets'],[3,5,7,9]);self.assertEqual(r['evaluation']['case_id'],'T0-regression')
        self.assertLessEqual(r['system']['resources']['frame_peak'],18);self.assertLessEqual(r['system']['resources']['output_slots_peak'],2)
        FACTS['resources']=r['system']['resources'];FACTS['technical_control']=r['evaluation']
    def test_material_production_requires_authorization(self):
        import tempfile
        from tools.s2uc_known_origin_material_plan import produce
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'auth.json';p.write_text('{}')
            with patch('tools.s2uc_known_origin_material_plan.synthesize_partition',side_effect=AssertionError('NO_PRODUCTION')):
                with self.assertRaisesRegex(ValueError,'PRODUCTION_NOT_AUTHORIZED'):produce(p)
    def test_material_plan_no_generation_and_partition_closure(self):
        with patch('tools.s2uc_known_origin_material_plan.synthesize_partition',side_effect=AssertionError('NO_PRODUCTION')):
            p=plan();self.assertTrue(validate(p));self.assertEqual(p['bounds']['windows_per_partition'],28)
        for name,q in p['partitions'].items():
            self.assertEqual(q['episodes']['D']['copy_prefix_from'],'A');self.assertEqual(q['episodes']['C']['source_start_sample'],19200)
            self.assertEqual(q['cases']['T0']['learn'],q['cases']['N3']['learn'])
            self.assertEqual(q['cases']['N4']['learn'],['A','A','D','D'])
        p['partitions']['evaluation']['derivatives']['A_noise']['root']='development/A'
        with self.assertRaises(AssertionError):validate(p)
if __name__=='__main__':unittest.main()
