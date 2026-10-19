import dataclasses,json,math,sys,types,unittest
from pathlib import Path
from unittest.mock import patch
from tools._s2uc_continuation_adapter import ContinuationAdapter,_scaled_continuation,consume_prediction
from tools._s2uc_pair_context_adapter import PerceptionSample,AdapterError,PairContextAdapter
from tools._s2uc_factor_recency import FactorRecencyArm
from tools._s2uc_origin_judge import replay,Truth,GatedReplay
from tools._s2uc_factor_continuation_compare import compare,summarize,ScalingBudgetObserver

P='b'*64
V=[(x,)*48 for x in (1.,3.,7.,11.)]
ROOT=Path(__file__).resolve().parents[1]
FACTS={}
def scaled(v,f):return tuple(x*f for x in v)
def sample(i,v):return PerceptionSample(v,P,'owner','stream',i,(i-1)*4800,i*4800)
def run(hint=None,target=None,base=None,learn_twice=True,policy='factor_scaled_v1',meter=None):
    b=base or V;values=b*(2 if learn_twice else 1)+(hint or b[:2])+[target or b[2]]
    return replay(values,P,len(values),policy=policy,resource_meter=meter)
def last(r):return r['targets'][-1]['forecast']

class FactorContinuationTests(unittest.TestCase):
    def test_Q1_direction_and_policy_immutable(self):
        for f in (.5,1.,2.):
            r=run([scaled(v,f) for v in V[:2]],scaled(V[2],f))
            self.assertEqual(last(r)['context_values'],scaled(V[2],f))
        a=ContinuationAdapter(FactorRecencyArm(P,'owner'),'stream')
        self.assertEqual(a.policy,'legacy_v1')
        for name in ('policy','_policy'):
            with self.assertRaises(AdapterError):setattr(a,name,'factor_scaled_v1')
            with self.assertRaises(AdapterError):delattr(a,name)
        a.accept_perception(sample(1,V[0]))
        with self.assertRaises(AdapterError):a.policy='factor_scaled_v1'
        a.finish_story()
        with self.assertRaises(AdapterError):a._policy='factor_scaled_v1'
        with self.assertRaises(AdapterError):ContinuationAdapter(FactorRecencyArm(P,'owner'),'stream',policy='other')

    def test_Q2_legacy_snapshot_and_factor_one(self):
        m=types.ModuleType('_frozen_legacy_test');sys.modules[m.__name__]=m
        exec((ROOT/'reports/s2uc/factor-continuation-development-20261001-01/legacy-adapter-before.txt').read_text(),m.__dict__)
        try:
            d=[V[0],V[1],V[3],V[2]]
            histories=[V+V+V[:3],V+V+[scaled(v,.5) for v in V[:3]],V+V+V[2:]+[V[0]],V+V+d+d+d[:3],[(0.,)*48]*11]
            for values in histories:
                current=replay(values,P,len(values))
                def old(*args,**kwargs):kwargs.pop('policy');return m.ContinuationAdapter(*args,**kwargs)
                with patch('tools._s2uc_origin_judge.ContinuationAdapter',old),patch('tools._s2uc_origin_judge.consume_prediction',m.consume_prediction):
                    frozen=replay(values,P,len(values))
                self.assertEqual(current,frozen)
            self.assertEqual(run(policy='legacy_v1'),run())
            FACTS['legacy_histories_exact']=len(histories)
        finally:sys.modules.pop(m.__name__)

    def test_Q3_competing_origins_and_offsets(self):
        d=[V[0],V[1],V[3],V[2]]
        r=replay(V+V+d+d+[scaled(v,.5) for v in d[:3]],P,19,policy='factor_scaled_v1')
        self.assertEqual(last(r)['status'],'AMBIGUOUS_CONTEXT')
        a=[V[0],V[0],V[0],V[3]]
        self.assertEqual(last(run([V[0],V[0]],base=a))['status'],'AMBIGUOUS_CONTEXT')

    def test_Q4_zero_factor_ambiguity(self):
        z=[(0.,)*48,(0.,)*48,V[2],V[3]]
        r=run(base=z)
        self.assertEqual(last(r)['status'],'ABSTAIN_AMBIGUOUS_FACTOR')
        self.assertEqual(json.loads(last(r)['provenance_json'])['matches'][0]['factors'],[.5,1.,2.])
        self.assertEqual(last(run(base=[(0.,)*48]*4))['status'],'AMBIGUOUS_CONTEXT')

    def test_Q5_missing_successor_context_and_corruption(self):
        self.assertEqual(last(run([scaled(v,.5) for v in V[2:]]))['status'],'ABSTAIN_NO_SUCCESSOR')
        self.assertEqual(last(run([(13.,)*48,(17.,)*48]))['status'],'ABSTAIN_NO_CONTEXT')
        for factors,error in [([], 'FACTOR_INVALID'),([3.], 'FACTOR_INVALID'),([1.], 'PRESTATE_SOURCE_MISSING')]:
            a=ContinuationAdapter(FactorRecencyArm(P,'owner'),'stream',policy='factor_scaled_v1')
            a.accept_perception(sample(1,V[0]))
            fake=dict(role='retained',generation=999,formation='none',ordinals=[1,2,3,4],offset=0,factors=factors)
            with patch.object(a.arm,'hint',side_effect=[None,dict(decision='x',matches=[fake])]):
                with self.assertRaisesRegex(AdapterError,error):a.accept_perception(sample(2,V[1]))
            self.assertTrue(a.closed);self.assertIsNone(a.pending_prediction)

    def test_Q6_numeric_boundaries(self):
        tiny=math.ulp(0.);minimum=sys.float_info.min;maximum=sys.float_info.max
        for x,e,status in [(maximum,1,'ABSTAIN_SCALE_OVERFLOW'),(minimum,-1,'ABSTAIN_SCALE_UNDERFLOW'),(tiny,-1,'ABSTAIN_SCALE_UNDERFLOW')]:
            self.assertEqual(_scaled_continuation((x,)*48,e),(None,status))
        for x,e in [(minimum/2,1),(-3.,1),(2.,1),(0.,-1),(-0.,1)]:
            y,error=_scaled_continuation((x,)*48,e)
            self.assertIsNone(error);self.assertEqual(y,(math.ldexp(x,e),)*48)
            if x==0:self.assertEqual(math.copysign(1.,y[0]),math.copysign(1.,x))
        mixed=(maximum,tiny)+(1.,)*46
        for v in (mixed,mixed[::-1]):self.assertEqual(_scaled_continuation(v,1)[1],'ABSTAIN_SCALE_OVERFLOW')
        b=[V[0],V[1],(tiny,)*48,V[3]]
        self.assertEqual(last(run(base=b))['context_values'],(tiny,)*48)
        with self.assertRaisesRegex(AdapterError,'STORED_VALUES_INVALID'):_scaled_continuation((float('nan'),)*48,1)
        # Normal power-of-two scaling is exact: INEXACT is defensive, not a
        # naturally reachable case after the conservative subnormal rejection.
        with patch('tools._s2uc_continuation_adapter.math.ldexp',side_effect=lambda x,e:x*2 if e==1 else x):
            self.assertEqual(_scaled_continuation((1.,)*48,1)[1],'ABSTAIN_SCALE_INEXACT')

    def test_Q7_future_gate_and_same_prefix(self):
        hint=[scaled(v,.5) for v in V[:2]]
        runs=[run(hint,t) for t in (scaled(V[2],.5),scaled(V[2],2.),V[2],hint[1])]
        for r in runs[1:]:
            self.assertEqual(last(r),last(runs[0]));self.assertEqual(r['states'][:10],runs[0]['states'][:10])
        count=[]
        def lazy():
            for v in V:count.append(1);yield v
        a=ContinuationAdapter(FactorRecencyArm(P,'owner'),'stream',policy='factor_scaled_v1');s=GatedReplay(lazy(),P)
        a.accept_perception(s.take(a));a.accept_perception(s.take(a));a.release_prediction()
        with self.assertRaisesRegex(ValueError,'FUTURE_BEFORE_FORECAST'):s.take(a)
        self.assertEqual(len(count),2);self.assertTrue(s.closed);self.assertTrue(a.closed)

    def test_Q8_roles_and_unchanged_memory(self):
        hint=[scaled(v,.5) for v in V[:2]]
        for twice,role in [(False,'CANDIDATE'),(True,'RETAINED')]:
            a=run(hint,learn_twice=twice);b=run(hint,learn_twice=twice,policy='legacy_v1')
            self.assertEqual(last(a)['status'],'PREDICTED_SCALED_'+role)
            self.assertEqual(a['states'],b['states']);self.assertEqual(a['receipts'],b['receipts'])
            self.assertEqual(a['admitted'],list(range(1,len(a['states'])+1)))
        values=V+[scaled(v,.5) for v in V]+[scaled(v,.5) for v in V[:3]]
        a=replay(values,P,11,policy='factor_scaled_v1');b=replay(values,P,11)
        self.assertEqual(a['states'],b['states']);self.assertEqual(a['receipts'],b['receipts'])
        self.assertIs(ContinuationAdapter._admit,PairContextAdapter._admit)

    def test_Q9_transients_cleanup_and_rest(self):
        meter=ScalingBudgetObserver()
        r=run([scaled(v,.5) for v in V[:2]],meter=meter)
        self.assertTrue(r['slots_released']);self.assertEqual(meter.builder_peak_components,48)
        self.assertEqual(meter.builder_components,0);self.assertEqual(meter.temporary_vector_lists,0)
        self.assertLessEqual(meter.frame_peak+meter.transient_output_slots_peak,20)
        self.assertLessEqual(meter.output_slots_peak,2)
        FACTS['scaled_resources']=vars(meter)
        for b in (V,[V[0],V[1],(sys.float_info.max,)*48,V[3]]):
            a=ContinuationAdapter(FactorRecencyArm(P,'owner'),'stream',policy='factor_scaled_v1')
            for idx,v in enumerate(b+b+[scaled(v,2.) for v in b[:2]],1):
                if a.pending_prediction:a.release_prediction()
                a.accept_perception(sample(idx,v))
            if b is not V:self.assertEqual(a.pending_prediction.status,'ABSTAIN_SCALE_OVERFLOW')
            with self.assertRaises(AdapterError):consume_prediction(a,sample(12,V[2]))
            self.assertTrue(a.closed);self.assertIsNone(a.pending_prediction);self.assertFalse(a.pair)
        for n in (1,2,3):
            a=ContinuationAdapter(FactorRecencyArm(P,'owner'),'stream',policy='factor_scaled_v1')
            for idx,v in enumerate(V[:n],1):
                if a.pending_prediction:a.release_prediction()
                a.accept_perception(sample(idx,v))
            a.finish_story();self.assertTrue(a.closed);self.assertIsNone(a.pending_prediction)

    def test_Q10_three_arms_harms_masks_and_labels(self):
        hint=[scaled(v,.5) for v in V[:2]];truth=Truth('neutral/A',True,{(1,2,3,4):'neutral/A',(5,6,7,8):'neutral/A'})
        cases={}
        for cid,target in [('FH',scaled(V[2],.5)),('GP',hint[1]),('F1',V[2])]:
            values=V+V+(V[:2] if cid=='F1' else hint)+[target]
            cases[cid]=compare(values,P,truth)
        s=summarize(cases)
        self.assertEqual(s['paired']['scaled_vs_legacy']['count'],1)
        self.assertEqual(s['paired']['scaled_vs_persistence']['count'],3)
        self.assertEqual([r['case_id'] for r in s['harms_against_persistence']],['GP'])
        self.assertEqual([r['case_id'] for r in s['harms_against_legacy']],['GP'])
        self.assertEqual(cases['GP']['rows']['legacy']['persistence_mae'],0.)
        empty=summarize({'FH':cases['FH']})['paired']['scaled_vs_legacy']
        self.assertEqual(empty['count'],0);self.assertIsNone(empty['delta'])
        changed=compare(V+V+hint+[hint[1]],P,Truth('neutral/D',False,truth.roots_by_ordinals))
        self.assertEqual(changed['systems'],cases['GP']['systems'])
        self.assertEqual(changed['rows']['scaled']['origin_category'],'WRONG')
        self.assertEqual(cases['GP']['learning_targets'],[3,5,7,9])
        FACTS['neutral_comparison']=s

if __name__=='__main__':unittest.main()
