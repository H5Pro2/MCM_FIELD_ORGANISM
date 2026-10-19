import unittest
import sys

from tools import _s2uc_four_arm as f

P = 'a' * 64


class FourArmTests(unittest.TestCase):
    def form(self, arm, values, segment, ordinal):
        owner = arm.store.owner if hasattr(arm, 'store') else arm.owner
        for index, value in enumerate(values):
            arm.form(f.tu.Frame((float(value),)*48, P, owner, segment, ordinal+index))
        return arm.close_segment(segment)

    def hint(self, arm, values, ordinal=100):
        owner = arm.store.owner if hasattr(arm, 'store') else arm.owner
        self.assertIsNone(arm.hint(f.tu.Frame((float(values[0]),)*48, P, owner, 'hint', ordinal)))
        return arm.hint(f.tu.Frame((float(values[1]),)*48, P, owner, 'hint', ordinal+1))

    def test_reference_classes_are_original(self):
        self.assertIs(f.ARMS['I2'], f.ub.ImmediateTwArm)
        self.assertIs(f.ARMS['B1'], f.ub.CandidateConfirmationArm)
        self.assertEqual((f.tu.RETAINED, f.ub.TRACE_STORAGE_LIMIT), (2, 12))

    def test_i1_exact_repeat_then_fifo(self):
        arm=f.ARMS['I1'](P,'i1')
        self.form(arm,[1,2,3,4],'a',1)
        self.assertEqual(self.form(arm,[1,2,3,4],'a2',5)['action'], 'TRACE_CONFIRMED')
        self.assertEqual(self.form(arm,[5,6,7,8],'b',9)['evicted'],1)
        self.assertEqual(arm.inventory,(2,))
        self.assertEqual(self.hint(arm,[1,2])['decision'],'ABSTAIN_NO_RETAINED_TRACE')

    def test_b2_two_retained_then_fifo_no_refresh(self):
        arm=f.ARMS['B2'](P,'b2')
        for i,values in enumerate(([1,2,3,4],[1,2,3,4],[5,6,7,8],[5,6,7,8])):
            self.form(arm,values,str(i),i*4+1)
        self.assertEqual(arm.inventory,(1,2))
        self.form(arm,[9,10,11,12],'c',17)
        candidate=arm.candidate_generation
        self.form(arm,[1,2,3,4],'repeat-a',21)
        self.assertEqual(arm.candidate_generation,candidate)
        self.assertEqual(self.form(arm,[9,10,11,12],'c2',25)['evicted'],1)
        self.assertEqual(arm.inventory,(2,3))

    def test_candidate_not_retrievable_and_hints_do_not_confirm(self):
        for name in ('B1','B2'):
            arm=f.ARMS[name](P,name)
            self.form(arm,[1,2,3,4],'a',1)
            before=arm.evidence()
            self.assertEqual(self.hint(arm,[1,2])['decision'],'ABSTAIN_NO_RETAINED_TRACE')
            self.assertEqual(arm.evidence(),before)

    def test_b2_overlap_incomplete_and_interruption(self):
        arm=f.ARMS['B2'](P,'b2')
        self.form(arm,[1,2,3,4],'a',1)
        self.assertEqual(self.form(arm,[1,2,3,4],'overlap',1)['action'],'TRACE_CANDIDATE_OVERLAP_NOT_CONFIRMED')
        self.assertEqual(self.form(arm,[1,2],'partial',5)['action'],'TRACE_DISCARDED_INCOMPLETE')
        self.form(arm,[4,3,2,1],'reverse',7)
        self.assertEqual(self.form(arm,[1,2,3,4],'a2',11)['action'],'TRACE_CANDIDATE_REPLACED')
        self.assertEqual(arm.inventory,())

    def test_b2_ambiguity_is_not_false_unique_recall(self):
        arm=f.ARMS['B2'](P,'b2')
        for i,values in enumerate(([1,2,3,4],[1,2,3,4],[1,2,7,8],[1,2,7,8])):
            self.form(arm,values,str(i),i*4+1)
        self.assertEqual(self.hint(arm,[1,2])['decision'],'ABSTAIN_AMBIGUOUS_RETAINED_TRACE')

    def test_owner_isolation_and_cleanup(self):
        for name,factory in f.ARMS.items():
            arm=factory(P,name)
            with self.assertRaises(f.tu.S2TUError):
                arm.form(f.tu.Frame((1.,)*48,P,'foreign','a',1))
            self.form(arm,[1,2,3,4],'a',1)
            arm.close_owner()
            self.assertTrue(all(v==0 for v in arm.resources().values()))
            with self.assertRaises(f.tu.S2TUError):
                self.form(arm,[1,2,3,4],'a2',5)

    def test_b2_full_budget_is_16_plus_two_hints(self):
        arm=f.ARMS['B2'](P,'b2')
        for i,values in enumerate(([1,2,3,4],[1,2,3,4],[5,6,7,8],[5,6,7,8],[9,10,11,12])):
            self.form(arm,values,str(i),i*4+1)
        for i in range(4):
            arm.form(f.tu.Frame((float(i+20),)*48,P,'b2','forming',21+i))
        self.assertEqual(arm.resources()['trace_frames'],16)

    def test_temporary_observer_sees_python_frame_locals(self):
        from tools.s2uc_four_arm_check import TemporaryObserver
        arm=f.ARMS['B2'](P,'b2')
        observer=TemporaryObserver({100,101})
        sys.settrace(observer.trace)
        try:
            for i,values in enumerate(([1,2,3,4],[1,2,3,4],[5,6,7,8],[5,6,7,8],[9,10,11,12])):
                self.form(arm,values,str(i),i*4+1)
            for i in range(4):
                arm.form(f.tu.Frame((float(i+20),)*48,P,'b2','forming',21+i))
            self.hint(arm,[1,2])
        finally:
            sys.settrace(None)
        self.assertEqual(observer.peak_trace,16)
        self.assertEqual(observer.peak_hint,2)
        self.assertEqual(observer.peak_total,18)
        self.assertEqual(self.hint(arm,[1,2])['decision'],'TRACE_MATCH')
        self.assertEqual(arm.resources()['trace_frames'],16)


if __name__ == '__main__':
    unittest.main()
