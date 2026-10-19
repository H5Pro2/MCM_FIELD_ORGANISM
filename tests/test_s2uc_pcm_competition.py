import unittest
from tools.s2uc_pcm_competition_check import oracle,assess,predictions
class CompetitionTests(unittest.TestCase):
    def setUp(self):
        self.v=[[float(i)]*48 for i in (1,3,7,11)]
        self.t=[self.v,[self.v[3],self.v[1],self.v[2],self.v[0]]]
    def test_shared_and_context(self):
        self.assertEqual(oracle(self.t,self.v[1:3],True),predictions(True)['BC'])
        self.assertEqual(oracle(self.t,self.v[:2],True),predictions(True)['XB'])
    def test_half(self):
        h=[[x*.5 for x in row] for row in self.v]
        self.assertEqual(oracle(self.t,h[1:3],True),predictions(True)['half_BC'])
        self.assertEqual(oracle(self.t,h[:2],True),predictions(True)['half_XB'])
    def test_failure_not_reclassified(self):
        self.assertEqual(assess([],predictions(True)['half_XB']),'VIOLATED')
    def test_unexpected_position_still_enumerated(self):
        hint=self.t[1][:2]
        actual=oracle(self.t,hint,True)
        self.assertEqual([(m['generation'],m['offset']) for m in actual],[(2,0)])
        self.assertEqual(assess(actual,predictions(True)['XB']),'VIOLATED')
if __name__=='__main__':unittest.main()
