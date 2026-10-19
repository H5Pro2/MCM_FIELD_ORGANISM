import unittest,json
from tools._s2uc_pair_context_adapter import PairContextAdapter,PerceptionSample,ContextReceipt,AdapterError
from tools._s2uc_factor_recency import FactorRecencyArm
P='a'*64
class PairAdapterTests(unittest.TestCase):
    def adapter(self):return PairContextAdapter(FactorRecencyArm(P,'o'),'s')
    def sample(self,i,**kw):
        d=dict(values=(.1,)*48,profile=P,owner='o',stream='s',index=i,start_sample=(i-1)*4800,end_sample=i*4800);d.update(kw);return PerceptionSample(**d)
    def test_no_self_match_and_admission_once(self):
        a=self.adapter();self.assertIsNone(a.accept_perception(self.sample(1)));r=a.accept_perception(self.sample(2));self.assertEqual(json.loads(r.json_text)['matches'],[]);self.assertEqual((a.accepted,a.admitted),(2,2));self.assertEqual([f.ordinal for f in a.arm._forming],[1,2])
    def test_gap_terminates_no_cross_pair(self):
        a=self.adapter();a.accept_perception(self.sample(1))
        with self.assertRaises(AdapterError):a.accept_perception(self.sample(3))
        self.assertTrue(a.closed);self.assertEqual(a.pair,[]);self.assertEqual(a.arm._observation_end,{})
    def test_scope_and_time_errors(self):
        for change in ({'owner':'bad'},{'stream':'other'},{'profile':'b'*64},{'start_sample':1}):
            a=self.adapter()
            with self.assertRaises(AdapterError):a.accept_perception(self.sample(1,**change))
            self.assertTrue(a.closed)
    def test_receipt_not_input(self):
        a=self.adapter()
        with self.assertRaises(AdapterError):a.accept_perception(ContextReceipt('{}'))
    def test_remainder_and_reset(self):
        a=self.adapter();a.accept_perception(self.sample(1));r=a.finish_story();self.assertEqual(json.loads(r.json_text)['status'],'INSUFFICIENT_PAIR');self.assertEqual(a.admitted,1);self.assertEqual(a.arm.resources()['trace_frames'],0)
        b=self.adapter();self.assertIsNone(b.accept_perception(self.sample(1)));b.finish_story()
    def test_receipt_has_no_payload(self):
        a=self.adapter();a.accept_perception(self.sample(1));r=a.accept_perception(self.sample(2));self.assertNotIn('values',r.json_text);self.assertNotIn('frames',r.json_text);self.assertFalse(a.pair)
if __name__=='__main__':unittest.main()
