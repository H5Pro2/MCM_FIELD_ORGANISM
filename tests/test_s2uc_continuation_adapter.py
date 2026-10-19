import unittest,json
from dataclasses import FrozenInstanceError
from tools._s2uc_continuation_adapter import ContinuationAdapter,evaluate_prediction,consume_prediction
from tools._s2uc_pair_context_adapter import PairContextAdapter,PerceptionSample,AdapterError
from tools._s2uc_factor_recency import FactorRecencyArm
from tools._s2tu_retained_trace import Frame
P='a'*64
V=[(float(x),)*48 for x in (1,3,7,11)]
def seed(a,values,segment,start):
    for j,v in enumerate(values):a.form(Frame(v,P,'owner',segment,start+j))
    return a.close_segment(segment)
def adapter(cls=ContinuationAdapter,extra=False):
    a=FactorRecencyArm(P,'owner');seed(a,V,'A1',1);seed(a,V,'A2',5)
    if extra:
        d=[V[3],V[1],V[2],V[0]];seed(a,d,'D1',9);seed(a,d,'D2',13)
    return cls(a,'stream',first_ordinal=17 if extra else 9)
def sample(i,v):return PerceptionSample(v,P,'owner','stream',i,(i-1)*4800,i*4800)
class ContinuationTests(unittest.TestCase):
    def test_before_admission_and_immutable(self):
        a=adapter();base=a._admit;seen=[]
        def check(f):seen.append(a.pending_prediction);base(f)
        a._admit=check;a.accept_perception(sample(1,V[0]));a.accept_perception(sample(2,V[1]))
        p=a.pending_prediction;self.assertTrue(all(x is p for x in seen));self.assertEqual(p.context_values,V[2]);self.assertEqual(p.read_revision,0)
        with self.assertRaises(FrozenInstanceError):p.status='x'
    def test_factor_and_end_abstain(self):
        for vals,want in (([(.5,)*48,(1.5,)*48],'FACTOR_CONTINUATION_NOT_SPECIFIED'),(V[2:],'ABSTAIN_NO_SUCCESSOR')):
            a=adapter();a.accept_perception(sample(1,vals[0]));a.accept_perception(sample(2,vals[1]));self.assertEqual(a.pending_prediction.status,want);self.assertIsNone(a.pending_prediction.context_values);a.finish_story();self.assertIsNone(a.pending_prediction)
    def test_eviction_does_not_change_prediction(self):
        a=adapter(extra=True);t=[V[3],V[3],V[0],V[1]];seed(a.arm,t,'T1',17);a.first_ordinal=21
        a.accept_perception(sample(1,t[0]));a.accept_perception(sample(2,t[1]));a.release_prediction()
        captured=[];base=a._admit
        def capture(f):captured.append(a.pending_prediction);base(f)
        a._admit=capture
        a.accept_perception(sample(3,t[2]));a.accept_perception(sample(4,t[3]));p=a.pending_prediction
        self.assertEqual(a.arm.inventory,(2,3));self.assertTrue(all(x is p for x in captured));self.assertEqual(p.status,'AMBIGUOUS_CONTEXT');self.assertIsNone(p.context_values)
        self.assertEqual(p.persistence_values,V[1]);self.assertEqual([(m['role'],m['generation'],m['offset']) for m in json.loads(p.provenance_json)['matches']],[('retained',1,0),('candidate',3,2)])
        self.assertEqual(evaluate_prediction(p,V[2])['context'],'AMBIGUOUS')
        a.release_prediction();self.assertIsNone(a.pending_prediction)
    def test_error_close_release_and_no_feedback(self):
        a=adapter();a.accept_perception(sample(1,V[0]));a.accept_perception(sample(2,V[1]));p=a.pending_prediction
        with self.assertRaises(AdapterError):a.accept_perception(sample(3,V[2]))
        self.assertTrue(a.closed);self.assertIsNone(a.pending_prediction)
        b=adapter();
        with self.assertRaises(AdapterError):b.accept_perception(p)
        self.assertTrue(b.closed)
    def test_one_ulp_not_tolerated(self):
        import math
        a=adapter();a.accept_perception(sample(1,V[0]));a.accept_perception(sample(2,V[1]));v=list(V[2]);v[0]=math.nextafter(v[0],8.)
        self.assertEqual(evaluate_prediction(a.pending_prediction,tuple(v))['context'],'MISS')
    def test_evaluation_failure_releases_slots(self):
        a=adapter();a.accept_perception(sample(1,V[0]));a.accept_perception(sample(2,V[1]))
        with self.assertRaises(AdapterError):consume_prediction(a,sample(4,V[2]))
        self.assertTrue(a.closed);self.assertIsNone(a.pending_prediction)
    def test_methods_unchanged(self):
        self.assertIs(ContinuationAdapter._admit,PairContextAdapter._admit)
if __name__=='__main__':unittest.main()
