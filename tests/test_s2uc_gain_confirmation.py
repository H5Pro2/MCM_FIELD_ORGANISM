import unittest
from tools._s2uc_gain_confirmation import GainConfirmationArm,scaled_equal,tu
from tools._s2uc_provisional_hint import ProvisionalHintArm


class GainTests(unittest.TestCase):
    def frames(self,values,segment,start):
        return tuple(tu.Frame((float(v),)*48,'a'*64,'owner',segment,start+i) for i,v in enumerate(values))

    def submit(self,arm,values,segment,start):
        for f in self.frames(values,segment,start):arm.form(f)
        return arm.close_segment(segment)

    def test_hint_and_other_paths_inherited(self):
        for name in ('hint','form','close_owner','resources'):
            self.assertIs(getattr(GainConfirmationArm,name),getattr(ProvisionalHintArm,name))

    def test_original_survives_scaling_no_chain(self):
        arm=GainConfirmationArm('a'*64,'owner')
        self.submit(arm,[1,2,3,4],'a',1)
        self.assertEqual(self.submit(arm,[.5,1,1.5,2],'half',5)['action'],'TRACE_PROMOTED')
        self.assertEqual(self.submit(arm,[.25,.5,.75,1],'quarter',9)['action'],'TRACE_CANDIDATE_CREATED')
        self.assertEqual(arm._retained_many[0].frames[0].segment,'a')
        self.assertEqual(arm._candidate.frames[0].segment,'quarter')

    def test_global_only_order_and_local_change_rejected(self):
        a=self.frames([1,2,3,4],'a',1)
        for vals in ([2,1.5,1,.5],[.5,2,3,4]):
            b=self.frames(vals,'b',5)
            self.assertFalse(any(scaled_equal(a,b,e) for e in (0,-1,1)))

    def test_ambiguous_sources_no_order_priority(self):
        for reverse in (False,True):
            arm=GainConfirmationArm('a'*64,'owner')
            for i,v in enumerate(([1,2,3,4],[1,2,3,4],[.25,.5,.75,1],[.25,.5,.75,1])):
                self.submit(arm,v,str(i),i*4+1)
            if reverse:arm._retained_many.reverse()
            before=arm.evidence()
            receipt=self.submit(arm,[.5,1,1.5,2],'ambiguous',17)
            self.assertEqual(receipt['action'],'ABSTAIN_AMBIGUOUS_CONFIRMATION')
            self.assertEqual({m['formation'] for m in receipt['matches']},{'0','2'})
            self.assertEqual(arm.evidence(),before)

    def test_overlap_cannot_promote(self):
        arm=GainConfirmationArm('a'*64,'owner')
        self.submit(arm,[1,2,3,4],'a',1)
        self.assertEqual(self.submit(arm,[.5,1,1.5,2],'half',1)['action'],'TRACE_CANDIDATE_OVERLAP_NOT_CONFIRMED')
        self.assertEqual(arm.inventory,())

    def test_incomplete_and_closed(self):
        arm=GainConfirmationArm('a'*64,'owner')
        self.assertEqual(self.submit(arm,[1,2],'partial',1)['action'],'TRACE_DISCARDED_INCOMPLETE')
        arm.close_owner()
        with self.assertRaises(tu.S2TUError):self.submit(arm,[1,2,3,4],'closed',5)


if __name__=='__main__':unittest.main()
