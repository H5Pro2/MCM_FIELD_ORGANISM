import unittest
from tools.s2uc_pcm_temporal_check import oracle
class TemporalTests(unittest.TestCase):
    def test_unique_position(self):
        v=[[float(i+1)]*48 for i in range(4)]
        self.assertEqual([m['offset'] for m in oracle(v,v[1:3],False)],[1])
    def test_half_requires_common_factor(self):
        v=[[float(i+1)]*48 for i in range(4)]
        self.assertEqual(oracle(v,[[1.]*48,[1.5]*48],False),[])
        self.assertEqual([m['offset'] for m in oracle(v,[[1.]*48,[1.5]*48],True)],[1])
        self.assertEqual(oracle(v,[[1.]*48,[3.]*48],True),[])
    def test_ambiguity_preserved(self):
        v=[[.25]*48]*4
        self.assertEqual([m['offset'] for m in oracle(v,v[:2],True)],[0,1,2])
    def test_reverse_not_forced_negative(self):
        v=[[.1]*48,[.2]*48,[.1]*48,[.2]*48]
        self.assertEqual([m['offset'] for m in oracle(v,[v[2],v[1]],False)],[0,2])
if __name__=='__main__': unittest.main()
