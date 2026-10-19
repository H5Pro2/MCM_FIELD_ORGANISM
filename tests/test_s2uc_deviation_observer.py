import unittest
from tools.s2uc_deviation_observer import measures,check_frames
class DeviationTests(unittest.TestCase):
    def test_equal_48(self):
        r=measures([.25]*48,[.25]*48);self.assertEqual(r,dict(n=48,mae=0,max_abs=0,mean_abs_x=.25,mean_abs_y=.25))
    def test_known_192(self):
        r=measures([0,.25,-.5,1]*48,[.5,0,-.25,0]*48)
        self.assertEqual(r,dict(n=192,mae=.5,max_abs=1,mean_abs_x=.4375,mean_abs_y=.1875))
    def test_zero_both(self):
        self.assertEqual(measures([0]*48,[0]*48),dict(n=48,mae=0,max_abs=0,mean_abs_x=0,mean_abs_y=0))
    def test_zero_one_side(self):
        r=measures([0]*48,[-.25]*48);self.assertEqual(r['mae'],.25);self.assertEqual(r['mean_abs_x'],0);self.assertEqual(r['mean_abs_y'],.25)
    def test_wrong_dimension_and_nonfinite(self):
        for x,y in [([],[]),([0],[0,1]),([float('nan')],[0])]:
            with self.assertRaises(ValueError):measures(x,y)
    def test_position_and_provenance(self):
        self.assertEqual(measures([0,1],[1,0])['mae'],1)
        frames=[dict(ordinal=i,values=[float(i)]*48,segment='p1') for i in range(1,5)]
        values={i:[float(i)]*48 for i in range(1,5)}
        self.assertEqual(len(check_frames(frames,values,'p1')),192)
        frames[0]['ordinal']=2
        with self.assertRaisesRegex(ValueError,'FRAME_PROVENANCE'):check_frames(frames,values,'p1')
if __name__=='__main__':unittest.main()
