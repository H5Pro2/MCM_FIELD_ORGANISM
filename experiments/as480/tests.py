"""Q1–Q5 small artificial fixtures; no reserved PCM/receptor measurements."""
import copy,math,struct,unittest
from types import SimpleNamespace
from .common import *
from . import material,oracle
LEDGER=None
def v(x):return [float(x)]*48
def stock():return [dict(role='retained',generation=1,formation='p1',ordinals=[1,2,3,4],values=[v(.96875),v(.96875),v(3),v(4)])]
def rows():return {c:dict(E=dict(correct=c=='A0',assigned=c=='A0',error=.5),N=dict(correct=c.startswith('A'),assigned=c.startswith('A'),error=.25),P=dict(error=.5)) for c in CASES}
class Fixtures(unittest.TestCase):
    def test_Q1_intervals_and_edges(self):
        data=b''.join(struct.pack('<f',float(i)) for i in range(19200))
        for case in CASES:
            for i in range(1,12):
                _,a,b=material.interval(case,i);chunk=material.cut(data,a,b)
                self.assertEqual(len(chunk),19200);self.assertEqual(struct.unpack('<f',chunk[:4])[0],a)
                self.assertEqual(struct.unpack('<f',chunk[-4:])[0],b-1)
        self.assertEqual(material.interval('A480',11),('A',10080,14880))
        self.assertEqual(material.interval('B480',10)[2],material.interval('B480',11)[1])
        with self.assertRaisesRegex(ValueError,'PCM_INTERVAL'):material.cut(data,16000,20800)
    def test_Q1_learning_repeat_and_time(self):
        self.assertEqual([material.interval('B480',i) for i in range(1,5)],[material.interval('B480',i) for i in range(5,9)])
        self.assertEqual([(i-1)*4800 for i in (9,10,11)],[38400,43200,48000])
    def test_Q2_future_gate_before_read(self):
        from tools._s2uc_origin_judge import GatedReplay
        touched=[]
        def values():touched.append(True);yield tuple(v(.1))
        a=SimpleNamespace(closed=False,next_index=3,pending_prediction=None,_terminate=lambda:None)
        s=GatedReplay(values(),'0'*64);s.pulls=2
        with self.assertRaisesRegex(ValueError,'FUTURE_BEFORE_FORECAST'):s.take(a)
        self.assertFalse(touched)
    def test_Q2_regular_prefix(self):
        from tools._s2uc_signal_approx_adapter import SignalApproxAdapter
        from tools._s2uc_factor_recency import FactorRecencyArm
        from tools._s2uc_pair_context_adapter import PairContextAdapter
        from tools._s2uc_origin_judge import GatedReplay
        from tools._s2uc_continuation_adapter import consume_prediction
        from tools.s2uc_continuous_comparison import state
        profile='0'*64;LEDGER.bump('arms_started');a=SignalApproxAdapter(FactorRecencyArm(profile,'owner'),'stream')
        LEDGER.bump('reference_started');r=PairContextAdapter(FactorRecencyArm(profile,'owner'),'stream')
        s=GatedReplay([tuple(v(x)) for x in (.1,.3,.6,.9)*2],profile)
        try:
            for i in range(1,9):
                sample=s.take(a)
                if a.pending_prediction:consume_prediction(a,sample)
                LEDGER.bump('policy_admissions');a.accept_perception(sample)
                LEDGER.bump('reference_admissions');r.accept_perception(sample)
                self.assertEqual(state(a.arm),state(r.arm))
                if i==4:self.assertEqual([f.ordinal for f in a.arm._candidate.frames],[1,2,3,4])
            self.assertEqual(a.arm.inventory,(1,));self.assertIsNone(a.arm._candidate)
            self.assertEqual([f.ordinal for f in a.arm._retained_many[0].frames],[1,2,3,4])
            a.release_prediction();a.finish_story();r.finish_story()
            LEDGER.bump('arms_completed');LEDGER.bump('reference_completed')
        finally:
            s.close()
            if not a.closed:a._terminate()
            if not r.closed:r._terminate()
            LEDGER.bump('arms_closed');LEDGER.bump('reference_closed')
    def test_Q3_tau_boundary(self):
        h=[v(1),v(1)]
        self.assertEqual(oracle.decide(stock(),h,'signal_approx_v1',EPS,TAU)['status'],'APPROXIMATE_SINGLE_MATCH')
        self.assertEqual(oracle.decide(stock(),h,'signal_approx_v1',EPS,math.nextafter(TAU,0))['status'],'ABSTAIN_NO_APPROX_CONTEXT')
    def test_Q3_epsilon_and_zero(self):
        for x in (0,EPS):self.assertEqual(oracle.decide([], [v(x),v(x)],'signal_approx_v1',EPS,TAU)['status'],'ABSTAIN_LOW_SIGNAL')
        self.assertEqual(oracle.decide([], [v(math.nextafter(EPS,1)),v(1)],'signal_approx_v1',EPS,TAU)['status'],'ABSTAIN_NO_APPROX_CONTEXT')
    def test_Q3_exact_priority_and_ambiguity(self):
        s=stock();s[0]['values'][:2]=[v(1),v(1)]
        self.assertEqual(oracle.decide(s,[v(1),v(1)],'signal_approx_v1',EPS,TAU)['matches'][0]['match_quality'],'EXACT')
        s.append(dict(s[0],generation=2,ordinals=[5,6,7,8]))
        self.assertEqual(oracle.decide(s,[v(1),v(1)],'signal_approx_v1',EPS,TAU)['prediction'],'AMBIGUOUS_CONTEXT')
    def test_Q3_approx_ambiguity(self):
        s=stock();s.append(dict(s[0],generation=2))
        self.assertEqual(oracle.decide(s,[v(1),v(1)],'signal_approx_v1',EPS,TAU)['status'],'ABSTAIN_APPROX_AMBIGUOUS')
    def test_Q3_offset_and_factor(self):
        s=stock()
        self.assertEqual(oracle.decide(s,[v(3),v(4)],'exact_v1',EPS,TAU)['prediction'],'ABSTAIN_NO_SUCCESSOR')
        self.assertEqual(oracle.decide(s,[v(1.9375),v(1.9375)],'exact_v1',EPS,TAU)['prediction'],'FACTOR_CONTINUATION_NOT_SPECIFIED')
        rec=dict(receipt=dict(matches=[dict(role='retained',generation=1,ordinals=[1,2,3,4],offset=1,factors=[1.])]),forecast=dict(context_values=v(1)))
        self.assertEqual(oracle.assignment(rec),dict(assigned=True,correct=False))
    def test_Q3_numeric_global_abstention(self):
        s=stock();s[0]['values'][0]=v(sys.float_info.max)
        self.assertEqual(oracle.decide(s,[v(1),v(1)],'signal_approx_v1',EPS,TAU)['status'],'ABSTAIN_APPROX_NUMERIC')
    def test_Q3_oracle_rejects_wrong_production(self):
        rec=dict(stock=[],hint=[v(1),v(2)],mode='exact_v1',receipt=dict(status='ABSTAIN_NO_MATCH',matches=[]),
                 forecast=dict(status='ABSTAIN_NO_CONTEXT',context_values=None,persistence_values=v(2)),actual=v(3),error=1.,p_error=1.)
        oracle.check(rec,EPS,TAU);rec['error']=0.
        with self.assertRaisesRegex(ValueError,'ORACLE_ERROR'):oracle.check(rec,EPS,TAU)
    def test_Q3_all_verdicts_and_conditions(self):
        r=rows();self.assertEqual(oracle.verdict(r)['verdict'],'CRITERIA_MET')
        self.assertEqual(oracle.verdict(r,collision=True)['verdict'],'IDENTIFIABILITY_LIMIT')
        self.assertEqual(oracle.verdict({},technical=True)['verdict'],'TECHNICAL_ERROR')
        for key in ('S1','S2','S3','S4'):
            x=copy.deepcopy(r)
            if key=='S1':x['A480']['N']['correct']=False
            if key=='S2':x['B0']['N']['assigned']=True
            if key=='S3':x['A0']['N']['correct']=False
            if key=='S4':
                for c in x:x[c]['N']['error']=.5
            out=oracle.verdict(x);self.assertFalse(out['criteria'][key]);self.assertEqual(out['verdict'],'NO_ADDITIONAL_BENEFIT')
        with self.assertRaisesRegex(ValueError,'FOUR_CASES'):oracle.verdict({})
    def test_Q4_time_bounds(self):
        from .entry import timeout
        self.assertEqual(timeout(241,0,0),'WORKER_TIMEOUT');self.assertEqual(timeout(301,0,100),'TOTAL_TIMEOUT')
        self.assertIsNone(timeout(239,0,0))
    def test_Q4_output_bound(self):
        with self.assertRaisesRegex(ValueError,'OUTPUT_MATERIAL'):Budget(PREP).check(PREP/'material/a',4194305)
        with self.assertRaisesRegex(ValueError,'OUTPUT_PATH'):Budget(PREP).check(ROOT/'escaped',1)
    def test_Q5_authorization_separation(self):
        for auth in (None,{},dict(status='AUTHORIZED_ONCE',mode='neutral')):
            with self.assertRaises(ValueError):authorize('research',auth,'x',RESEARCH)
        authorize('neutral',None,None,PREP)
        with self.assertRaisesRegex(ValueError,'SOURCE_NOT_AUTHORIZED'):material.materialize(PREP,'research',LEDGER)
    def test_Q5_digest_and_exclusive(self):
        p=LEDGER.folder/'fixture-exclusive.txt';exclusive(p,b'fixture')
        with self.assertRaises(FileExistsError):exclusive(p,b'changed')
        from .entry import verify_files
        with self.assertRaisesRegex(ValueError,'CODE_BINDING'):verify_files({p.relative_to(ROOT).as_posix():'0'*64})
    def test_Q5_reservation(self):
        self.assertFalse(set(sum(NEUTRAL.values(),[]))&set(sum(RECIPE.values(),[])))
        self.assertEqual(sha(CONTRACT),CONTRACT_SHA)

def run(folder,ledger):
    global LEDGER;LEDGER=ledger
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Fixtures);ids=[x.id() for x in suite]
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report=dict(ids=ids,tests=result.testsRun,failures=[(str(t),s) for t,s in result.failures],errors=[(str(t),s) for t,s in result.errors],passed=result.wasSuccessful())
    Budget(folder).save('fixtures.json',report)
    need(result.wasSuccessful(),'FIXTURES_FAILED')
    return report
