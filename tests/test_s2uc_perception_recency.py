import unittest
from tools._s2uc_perception_recency import PerceptionRecencyArm
from tools._s2uc_provisional_hint import ProvisionalHintArm
from tools._s2uc_four_arm import tu
P='a'*64
class RecencyIntegrationTests(unittest.TestCase):
    def submit(self,a,vs,seg,ordinals):
        for v,n in zip(vs,ordinals):a.form(tu.Frame((float(v),)*48,P,a.owner,seg,n))
        return a.close_segment(seg)
    def setup_arm(self):
        a=PerceptionRecencyArm(P,'test')
        for k,v in enumerate(([1,2,3,4],[1,2,3,4],[5,6,7,8],[5,6,7,8])):self.submit(a,v,str(k),range(k*4+1,k*4+5))
        return a
    def test_original_object_and_candidate_preserved(self):
        a=self.setup_arm();t=a._retained_many[0];self.submit(a,[9,10,11,12],'z',range(17,21));c=a._candidate
        r=self.submit(a,[1,2,3,4],'again',range(21,25))
        self.assertEqual(r['action'],'TRACE_CONFIRMED_RECENT');self.assertEqual(a.inventory,(2,1));self.assertIs(a._retained_many[-1],t);self.assertIs(a._candidate,c)
    def test_incomplete(self):
        a=self.setup_arm();self.submit(a,[1,2,3],'part',range(17,20));self.assertEqual(a.inventory,(1,2))
    def test_deviation(self):
        a=self.setup_arm();self.submit(a,[1,2,3,4.5],'different',range(17,21));self.assertEqual(a.inventory,(1,2))
    def test_overlap(self):
        a=self.setup_arm();self.submit(a,[1,2,3,4],'overlap',[2,3,4,5]);self.assertEqual(a.inventory,(1,2))
    def test_interleaved_disjoint_not_later(self):
        a=PerceptionRecencyArm(P,'test');self.submit(a,[1,2,3,4],'a',[10,20,30,40]);self.submit(a,[1,2,3,4],'a2',[50,60,70,80]);self.submit(a,[5,6,7,8],'d',[90,100,110,120]);self.submit(a,[5,6,7,8],'d2',[130,140,150,160]);self.submit(a,[1,2,3,4],'interleave',[11,21,31,41]);self.assertEqual(a.inventory,(1,2))
    def test_reused_latest_interval_not_refreshed(self):
        a=self.setup_arm();self.submit(a,[1,2,3,4],'first',range(17,21))
        self.submit(a,[5,6,7,8],'d-again',range(21,25));self.assertEqual(a.inventory,(1,2))
        self.submit(a,[1,2,3,4],'reused',range(17,21));self.assertEqual(a.inventory,(1,2))
        self.submit(a,[1,2,3,4],'fresh',range(25,29));self.assertEqual(a.inventory,(2,1))
        self.assertLessEqual(len(a._observation_end),2)
        a.close_owner();self.assertEqual(a._observation_end,{})
    def test_hint_inherited(self):self.assertIs(PerceptionRecencyArm.hint,ProvisionalHintArm.hint)
    def test_hint_readonly(self):
        a=self.setup_arm();before=a.evidence()
        a.hint(tu.Frame((1.,)*48,P,a.owner,'h',10000));a.hint(tu.Frame((2.,)*48,P,a.owner,'h',10001));self.assertEqual(a.evidence(),before)
    def test_reverse(self):
        a=self.setup_arm();self.submit(a,[4,3,2,1],'reverse',range(17,21));self.assertEqual(a.inventory,(1,2))
if __name__=='__main__':unittest.main()
