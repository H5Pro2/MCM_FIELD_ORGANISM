import json,math,sys,unittest
from unittest.mock import patch
from tools._s2uc_signal_approx_adapter import SignalApproxAdapter,relative_l1,amplitude
from tools._s2uc_signal_approx_compare import replay,compare,report
from tools._s2uc_origin_judge import Truth,replay as original_replay,GatedReplay
from tools._s2uc_factor_recency import FactorRecencyArm
from tools._s2uc_pair_context_adapter import AdapterError,PerceptionSample
from tools._s2uc_continuation_adapter import consume_prediction

P='c'*64;V=[(x,)*48 for x in (1.,3.,7.,11.)];H=[(1.03125,)*48,(3.03125,)*48]
FACTS={}
def sample(i,v):return PerceptionSample(v,P,'owner','stream',i,(i-1)*4800,i*4800)
def run(h=H,target=None,base=V,epsilon=.1,tau=.05,measure=False):
    return replay(base+base+list(h)+[V[2] if target is None else target],P,retrieval_policy='signal_approx_v1',epsilon=epsilon,tau=tau,measure=measure)
def forecast(r):return r['targets'][-1]['forecast']
def prov(r):return json.loads(forecast(r)['provenance_json'])

class SignalApproxTests(unittest.TestCase):
    def test_A1_default_and_parameters_locked(self):
        a=SignalApproxAdapter(FactorRecencyArm(P,'owner'),'stream')
        self.assertEqual(a.retrieval_policy,'exact_v1');self.assertEqual(a.policy,'legacy_v1')
        for kw in [dict(epsilon=.1,tau=.1),dict(retrieval_policy='bad'),dict(retrieval_policy='signal_approx_v1',epsilon=0.,tau=.1),dict(retrieval_policy='signal_approx_v1',epsilon=.1,tau=float('nan')),dict(retrieval_policy='signal_approx_v1',epsilon=True,tau=.1),dict(retrieval_policy='signal_approx_v1',epsilon=.1,tau=.126)]:
            with self.assertRaises(AdapterError):SignalApproxAdapter(FactorRecencyArm(P,'owner'),'stream',**kw)
        for n in ('epsilon','tau','retrieval_policy','_epsilon','_tau','_retrieval_policy'):
            with self.assertRaises(AdapterError):setattr(a,n,0.)
            with self.assertRaises(AdapterError):delattr(a,n)
        a.accept_perception(sample(1,V[0]))
        with self.assertRaises(AdapterError):a._tau=.1
        a.finish_story()

    def test_A2_default_legacy_exact_regression(self):
        histories=[V+V+V[:3],V+V+H+[V[2]],V+V+V[2:]+[V[0]],[(0.,)*48]*11]
        for values in histories:
            a=replay(values,P);b=original_replay(values,P,len(values))
            for key in ('targets','receipts','states','final_state','admitted','pull_log','slots_released'):self.assertEqual(a[key],b[key])
        FACTS['default_exact_histories']=len(histories)

    def test_A3_epsilon_strict_boundaries_and_null(self):
        self.assertEqual(prov(run(V[:2],epsilon=1.))['status'],'ABSTAIN_LOW_SIGNAL')
        self.assertEqual(prov(run(V[:2],epsilon=math.nextafter(1.,0.)))['matches'][0]['match_quality'],'EXACT')
        self.assertEqual(prov(run([(2.,)*48,(6.,)*48],epsilon=1.))['status'],'ABSTAIN_STORED_LOW_SIGNAL')
        self.assertEqual(prov(run([(0.,)*48,V[1]]))['status'],'ABSTAIN_LOW_SIGNAL')
        z=[(0.,)*48,(0.,)*48,V[2],V[3]]
        self.assertEqual(prov(run(z[:2],base=z))['status'],'ABSTAIN_LOW_SIGNAL')

    def test_A4_tau_inclusive_and_quality_role(self):
        d=relative_l1(H[0],H[1],V[0],V[1],1.03125,3.03125,1.,3.)
        a=run(tau=d);self.assertEqual(prov(a)['matches'][0]['distance'],d)
        self.assertEqual(prov(a)['matches'][0]['match_quality'],'APPROXIMATE')
        self.assertEqual(prov(a)['matches'][0]['role'],'retained')
        self.assertEqual(prov(run(tau=math.nextafter(d,0.)))['status'],'ABSTAIN_NO_APPROX_CONTEXT')
        self.assertEqual(prov(run(tau=0.))['status'],'ABSTAIN_NO_APPROX_CONTEXT')

    def test_A5_competition_and_exact_priority(self):
        d=[(1.0625,)*48,(3.0625,)*48,V[3],V[2]]
        def story(h):return replay(V+V+d+d+h+[V[2]],P,retrieval_policy='signal_approx_v1',epsilon=.1,tau=.05)
        a=story(H);self.assertEqual(prov(a)['status'],'ABSTAIN_APPROX_AMBIGUOUS');self.assertIsNone(forecast(a)['context_values'])
        adapter=SignalApproxAdapter(FactorRecencyArm(P,'owner'),'stream',retrieval_policy='signal_approx_v1',epsilon=.1,tau=.05)
        for i,v in enumerate(V+V+d+d,1):
            if adapter.pending_prediction:adapter.release_prediction()
            adapter.accept_perception(sample(i,v))
        adapter.release_prediction()
        with patch('tools._s2uc_signal_approx_adapter.relative_l1',side_effect=AssertionError('SHOULD_NOT_FALLBACK')):
            adapter.accept_perception(sample(17,V[0]));adapter.accept_perception(sample(18,V[1]))
        self.assertEqual(json.loads(adapter.pending_prediction.provenance_json)['matches'][0]['match_quality'],'EXACT')
        adapter.finish_story()
        same=[V[0],V[1],V[3],V[2]]
        a=replay(V+V+same+same+V[:3],P,retrieval_policy='signal_approx_v1',epsilon=.1,tau=.05)
        self.assertEqual(len(prov(a)['matches']),2)

    def test_A6_numeric_failure_invalidates_whole_fallback(self):
        real=relative_l1
        def broken(h0,h1,s0,s1,*args):
            if s0==V[1]:raise OverflowError('NEUTRAL_SECOND_PAIR_UNKNOWN')
            return real(h0,h1,s0,s1,*args)
        with patch('tools._s2uc_signal_approx_adapter.relative_l1',side_effect=broken):a=run()
        self.assertEqual(prov(a)['status'],'ABSTAIN_APPROX_NUMERIC');self.assertEqual(prov(a)['matches'],[])
        self.assertIsNone(forecast(a)['context_values'])
        with patch('tools._s2uc_signal_approx_adapter.amplitude',side_effect=OverflowError('SIGNAL_UNKNOWN')):a=run()
        self.assertEqual(prov(a)['status'],'ABSTAIN_SIGNAL_NUMERIC')
        with self.assertRaises(ArithmeticError):relative_l1((sys.float_info.max,)*48,(sys.float_info.max,)*48,(-sys.float_info.max,)*48,(-sys.float_info.max,)*48,1.,1.,1.,1.)
        with self.assertRaises(ArithmeticError):relative_l1(V[0],V[1],V[0],V[1],math.ulp(0.),math.ulp(0.),math.ulp(0.),math.ulp(0.))
        with self.assertRaises(AdapterError):amplitude((float('nan'),)*48)

    def test_A7_missing_successor_and_candidate(self):
        a=run([(7.03125,)*48,(11.03125,)*48]);self.assertEqual(forecast(a)['status'],'ABSTAIN_NO_SUCCESSOR')
        a=replay(V+H+[V[2]],P,retrieval_policy='signal_approx_v1',epsilon=.1,tau=.05)
        self.assertEqual(forecast(a)['status'],'PREDICTED_CANDIDATE')
        self.assertEqual(prov(a)['matches'][0]['match_quality'],'APPROXIMATE')

    def test_A8_unchanged_confirmation_refresh(self):
        noisy=[tuple(x+.03125 for x in v) for v in V]
        values=V+V+noisy+H+[V[2]]
        a=replay(values,P);b=replay(values,P,retrieval_policy='signal_approx_v1',epsilon=.1,tau=.05)
        self.assertEqual(a['states'],b['states']);self.assertEqual(a['final_state'],b['final_state'])
        self.assertEqual(a['admitted'],list(range(1,16)))

    def test_A9_causal_equal_prefix_and_gate(self):
        a=run(target=V[2]);b=run(target=H[1]);self.assertEqual(forecast(a),forecast(b));self.assertEqual(a['states'][:10],b['states'][:10])
        count=[]
        def values():
            for v in V:count.append(1);yield v
        a=SignalApproxAdapter(FactorRecencyArm(P,'owner'),'stream',retrieval_policy='signal_approx_v1',epsilon=.1,tau=.05)
        source=GatedReplay(values(),P)
        a.accept_perception(source.take(a));a.accept_perception(source.take(a));a.release_prediction()
        with self.assertRaisesRegex(ValueError,'FUTURE_BEFORE_FORECAST'):source.take(a)
        self.assertEqual(len(count),2);self.assertTrue(a.closed)

    def test_A10_resources_receipts_and_cleanup(self):
        a=run(measure=True);stats=a['resources'];self.assertLessEqual(stats['frame_peak'],18)
        self.assertLessEqual(stats['combined_peak'],20);self.assertLessEqual(stats['receipt_bytes_peak'],16384)
        self.assertEqual(stats['temporary_numeric_vectors_peak'],0);self.assertGreater(stats['scalar_pair_comparisons'],0)
        self.assertTrue(a['slots_released']);FACTS['resources']=stats
        for n in (1,2,3):
            x=SignalApproxAdapter(FactorRecencyArm(P,'owner'),'stream',retrieval_policy='signal_approx_v1',epsilon=.1,tau=.05)
            for i,v in enumerate(V[:n],1):
                if x.pending_prediction:x.release_prediction()
                x.accept_perception(sample(i,v))
            x.finish_story();self.assertTrue(x.closed);self.assertIsNone(x.pending_prediction)
        x=SignalApproxAdapter(FactorRecencyArm(P,'owner'),'stream',retrieval_policy='signal_approx_v1',epsilon=.1,tau=.05)
        x.accept_perception(sample(1,V[0]));x.accept_perception(sample(2,V[1]))
        with self.assertRaises(AdapterError):consume_prediction(x,sample(4,V[2]))
        self.assertTrue(x.closed);self.assertIsNone(x.pending_prediction)

    def test_A11_observer_new_wrong_lost_exact_and_harm(self):
        origins={(1,2,3,4):'neutral/A',(5,6,7,8):'neutral/A'}
        truth=Truth('neutral/A',True,origins)
        c={}
        c['positive']=compare(V+V+H+[V[2]],P,truth,epsilon=.1,tau=.05)
        c['false']=compare(V+V+H+[V[2]],P,Truth('neutral/B',False,origins),epsilon=.1,tau=.05)
        c['loss']=compare(V+V+V[:3],P,truth,epsilon=1.,tau=.05)
        c['harm']=compare(V+V+H+[H[1]],P,truth,epsilon=.1,tau=.05)
        r=report(c);self.assertEqual(r['additional_wrong'],['false']);self.assertFalse(r['admissible_no_new_wrong'])
        self.assertEqual(r['signal_lost_exact_assignments'],['loss']);self.assertEqual(r['lost_correct_exact'],['loss'])
        self.assertIn('harm',[x['case_id'] for x in r['comparison']['harms_against_persistence']])
        self.assertEqual(c['false']['systems'],c['positive']['systems'])
        self.assertEqual(c['harm']['rows']['exact']['context_mae'],None)
        FACTS['observer']=r

    def test_A12_maximum_competitors_and_invalid_input_cleanup(self):
        a=[(1.,)*48]*4;b=[(1.03125,)*48]*4;c=[(1.0625,)*48]*4
        h=[(1.015625,)*48]*2
        r=replay(a+a+b+b+c+h+[a[0]],P,retrieval_policy='signal_approx_v1',epsilon=.1,tau=.05,measure=True)
        self.assertEqual(len(prov(r)['matches']),9)
        self.assertEqual(prov(r)['status'],'ABSTAIN_APPROX_AMBIGUOUS')
        self.assertEqual(r['resources']['match_metadata_peak'],9)
        self.assertLessEqual(r['resources']['receipt_transient_utf8_bytes_peak'],32768)
        self.assertEqual(r['resources']['temporary_numeric_vectors_peak'],0)
        FACTS['maximum_competition_resources']=r['resources']
        adapter=SignalApproxAdapter(FactorRecencyArm(P,'owner'),'stream',retrieval_policy='signal_approx_v1',epsilon=.1,tau=.05)
        with self.assertRaises(AdapterError):adapter.accept_perception(sample(1,(float('inf'),)*48))
        self.assertTrue(adapter.closed);self.assertIsNone(adapter.pending_prediction)

if __name__=='__main__':unittest.main()
