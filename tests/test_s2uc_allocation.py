import inspect
import unittest
from tools._s2uc_allocation import TwoCandidateOneRetainedArm
from tools._s2uc_two_candidates import TwoCandidateArm
from tools._s2uc_four_arm import tu


class AllocationTests(unittest.TestCase):
    def test_capacity_is_only_close_logic_change(self):
        expected=inspect.getsource(TwoCandidateArm.close_segment).replace('len(self._retained_many) == 2','len(self._retained_many) == 1')
        self.assertEqual(inspect.getsource(TwoCandidateOneRetainedArm.close_segment),expected)
        for method in ('form','hint','close_owner','resources'):
            self.assertIs(getattr(TwoCandidateOneRetainedArm,method),getattr(TwoCandidateArm,method))

    def test_confirmed_eviction_and_original_provenance(self):
        arm=TwoCandidateOneRetainedArm('a'*64,'test')
        for i,values in enumerate(([13,14,15,16],[13,14,15,16],[1,2,3,4],[5,6,7,8],[1,2,3,4]),1):
            for j,value in enumerate(values):
                arm.form(tu.Frame((float(value),)*48,'a'*64,'test',str(i),i*10+j))
            receipt=arm.close_segment(str(i))
        self.assertEqual(receipt['evicted'],1)
        self.assertEqual(arm.inventory,(2,))
        self.assertEqual([f.ordinal for f in arm._retained_many[0].frames],[30,31,32,33])
        self.assertEqual(arm._candidates[0].frames[0].segment,'4')

    def test_budget_rejects_second_retained_slot(self):
        arm=TwoCandidateOneRetainedArm('a'*64,'test')
        frames=tuple(tu.Frame((float(i),)*48,'a'*64,'test','a',i) for i in range(4))
        arm._retained_many=[tu.RetainedTrace(1,frames),tu.RetainedTrace(2,frames)]
        with self.assertRaises(tu.S2TUError):
            arm._check_budget()


if __name__=='__main__':
    unittest.main()
