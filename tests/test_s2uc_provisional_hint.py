import sys
import unittest
from tools._s2uc_provisional_hint import ProvisionalHintArm
from tools._s2uc_four_arm import CandidateTwoArm,tu
from tools.s2uc_b2v_check import state,VariantObserver
from pathlib import Path


class ProvisionalTests(unittest.TestCase):
    def setUp(self):
        self.arm=ProvisionalHintArm('a'*64,'owner')

    def frame(self,value,segment,ordinal):
        return tu.Frame((float(value),)*48,'a'*64,'owner',segment,ordinal)

    def form(self,values,segment,start):
        for i,v in enumerate(values):
            self.arm.form(self.frame(v,segment,start+i))
        return self.arm.close_segment(segment)

    def hint(self,values=(1,2)):
        before=state(self.arm)
        self.assertIsNone(self.arm.hint(self.frame(values[0],'hint',1000)))
        r=self.arm.hint(self.frame(values[1],'hint',1001))
        self.assertEqual(state(self.arm),before)
        return r

    def test_only_hint_is_overridden(self):
        self.assertEqual(set(ProvisionalHintArm.__dict__)-{'__module__','__doc__','__firstlineno__','__static_attributes__'}, {'hint'})
        for name in ('form','close_segment','close_owner','resources'):
            self.assertIs(getattr(ProvisionalHintArm,name),getattr(CandidateTwoArm,name))

    def test_multiple_positions_candidate_and_retained(self):
        self.form([1,2,1,2],'a',1)
        r=self.hint()
        self.assertEqual(r['decision'],'ABSTAIN_AMBIGUOUS')
        self.assertEqual([(x['role'],x['offset']) for x in r['matches']],[('candidate',0),('candidate',2)])
        self.form([1,2,1,2],'a2',5)
        r=self.hint()
        self.assertEqual(r['decision'],'ABSTAIN_AMBIGUOUS')
        self.assertEqual([(x['role'],x['offset']) for x in r['matches']],[('retained',0),('retained',2)])

    def test_repeat_does_not_promote_or_save_replaced_candidate(self):
        self.form([1,2,3,4],'a',1)
        r=self.hint()
        self.assertEqual(r['decision'],'PROVISIONAL_CANDIDATE_MATCH')
        self.assertEqual(self.hint(),r)
        self.assertEqual(self.arm.inventory,())
        self.form([5,6,7,8],'b',5)
        self.assertEqual(self.hint()['decision'],'ABSTAIN_NO_MATCH')

    def test_foreign_owner_and_closed_rejected(self):
        with self.assertRaises(tu.S2TUError):
            self.arm.hint(tu.Frame((1.,)*48,'a'*64,'foreign','hint',1))
        self.arm.close_owner()
        with self.assertRaises(tu.S2TUError):
            self.hint()

    def test_full_budget_and_provenance_no_payload_copy(self):
        for i,values in enumerate(([1,2,3,4],[1,2,3,4],[5,6,7,8],[5,6,7,8],[9,10,11,12])):
            self.form(values,str(i),i*4+1)
        for i in range(4):
            self.arm.form(self.frame(i+20,'forming',21+i))
        obs=VariantObserver({1000,1001})
        import tools._s2uc_provisional_hint as module
        obs.files.add(str(Path(module.__file__).resolve()))
        sys.settrace(obs.trace)
        try:
            r=self.hint((9,10))
        finally:
            sys.settrace(None)
        self.assertEqual((obs.peak_trace,obs.peak_hint,obs.peak_total),(16,2,18))
        self.assertEqual(r['decision'],'PROVISIONAL_CANDIDATE_MATCH')
        self.assertEqual(set(r['matches'][0]),{'role','generation','formation','ordinals','offset'})


if __name__=='__main__':
    unittest.main()
