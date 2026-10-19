import unittest
from tools._s2uc_two_candidates import TwoCandidateArm,tu
from tools._s2uc_provisional_hint import ProvisionalHintArm
from tools.s2uc_k2_check import provenance


class TwoCandidateTests(unittest.TestCase):
    def setUp(self):
        self.arm=TwoCandidateArm('a'*64,'owner')

    def submit(self,values,segment,start,arm=None):
        arm=self.arm if arm is None else arm
        for i,x in enumerate(values):
            arm.form(tu.Frame((float(x),)*48,'a'*64,arm.owner,segment,start+i))
        return arm.close_segment(segment)

    def test_promote_first_original_after_interruption(self):
        self.submit([1,2,3,4],'first',1)
        self.submit([5,6,7,8],'between',5)
        receipt=self.submit([1,2,3,4],'repeat',9)
        self.assertEqual(receipt['action'],'TRACE_PROMOTED')
        self.assertEqual(provenance(self.arm)['retained'][0]['ordinals'],[1,2,3,4])
        self.assertEqual(provenance(self.arm)['candidates'][0]['formation'],'between')

    def test_promote_second_leaves_first_oldest(self):
        self.submit([1,2,3,4],'first',1)
        self.submit([5,6,7,8],'second',5)
        self.submit([5,6,7,8],'repeat',9)
        self.submit([9,10,11,12],'third',13)
        receipt=self.submit([13,14,15,16],'fourth',17)
        self.assertEqual(receipt['evicted'],1)
        self.assertEqual([x['formation'] for x in provenance(self.arm)['candidates']],['third','fourth'])

    def test_overlap_incomplete_and_reverse_do_not_confirm(self):
        self.submit([1,2,3,4],'first',1)
        self.assertEqual(self.submit([1,2,3,4],'overlap',1)['action'],'TRACE_CANDIDATE_OVERLAP_NOT_CONFIRMED')
        self.assertEqual(self.submit([1,2],'partial',5)['action'],'TRACE_DISCARDED_INCOMPLETE')
        self.submit([4,3,2,1],'reverse',7)
        self.assertEqual(self.arm.inventory,())

    def test_retained_fifo_and_candidate_unchanged_by_confirmation(self):
        for i,v in enumerate(([1,2,3,4],[1,2,3,4],[5,6,7,8],[5,6,7,8],[9,10,11,12])):
            self.submit(v,str(i),i*4+1)
        before=provenance(self.arm)['candidates']
        self.submit([1,2,3,4],'confirm-oldest',21)
        self.assertEqual(provenance(self.arm)['candidates'],before)
        self.assertEqual(self.submit([9,10,11,12],'promote-third',25)['evicted'],1)
        self.assertEqual(self.arm.inventory,(2,3))

    def test_single_candidate_path_matches_unchanged_reference(self):
        reference=ProvisionalHintArm('a'*64,'reference')
        for i,v in enumerate(([1,2,3,4],[1,2,3,4],[5,6,7,8],[5,6,7,8])):
            self.assertEqual(self.submit(v,str(i),i*4+1),self.submit(v,str(i),i*4+1,reference))
        self.assertEqual(provenance(self.arm),provenance(reference))

    def test_owner_cleanup_and_ambiguous_positions(self):
        with self.assertRaises(tu.S2TUError):
            self.arm.form(tu.Frame((1.,)*48,'a'*64,'foreign','x',1))
        self.submit([1,2,1,2],'a',1)
        before=self.arm.evidence()
        self.arm.hint(tu.Frame((1.,)*48,'a'*64,'owner','h',100))
        result=self.arm.hint(tu.Frame((2.,)*48,'a'*64,'owner','h',101))
        self.assertEqual(result['decision'],'ABSTAIN_AMBIGUOUS')
        self.assertEqual([x['offset'] for x in result['matches']],[0,2])
        self.assertEqual(self.arm.evidence(),before)
        self.arm.close_owner()
        self.assertTrue(all(v==0 for v in self.arm.resources().values()))
        with self.assertRaises(tu.S2TUError):
            self.submit([1,2,3,4],'closed',5)


if __name__=='__main__':
    unittest.main()
