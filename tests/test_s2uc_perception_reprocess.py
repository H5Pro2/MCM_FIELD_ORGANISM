import unittest,math
from tools.s2uc_perception_reprocess_check import equality_rows
from tools._s2uc_perception_recency import PerceptionRecencyArm
from tools._s2uc_four_arm import tu
class ReprocessTests(unittest.TestCase):
    def test_no_tolerance(self):
        a=[[.125]*48 for _ in range(4)];b=[row[:] for row in a];b[3][47]=math.nextafter(.125,1.)
        rows=equality_rows(a,b);self.assertEqual(len(rows),192);self.assertEqual(sum(r['numeric_equal'] for r in rows),191)
    def test_story_reset_and_hint_marks(self):
        for story in range(2):
            a=PerceptionRecencyArm('a'*64,str(story));self.assertEqual(a._observation_end,{})
            for k in range(2):
                for j in range(4):a.form(tu.Frame((float(j+1),)*48,'a'*64,a.owner,str(k),k*4+j+1))
                a.close_segment(str(k))
            self.assertEqual(a._observation_end,{1:8});before=dict(a._observation_end)
            a.hint(tu.Frame((1.,)*48,'a'*64,a.owner,'h',100));self.assertEqual(a._observation_end,before)
            a.hint(tu.Frame((2.,)*48,'a'*64,a.owner,'h',101));self.assertEqual(a._observation_end,before)
            a.close_owner();self.assertEqual(a._observation_end,{})
if __name__=='__main__':unittest.main()
