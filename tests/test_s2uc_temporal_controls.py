import unittest
from tools.s2uc_temporal_controls import selection,compare,summary,formations_from_record
class TemporalTests(unittest.TestCase):
    def test_exact_indices(self):
        s=selection();self.assertEqual(len(s['frames']),24);self.assertEqual(len(s['formations']),12)
        self.assertEqual(s['frames'][0],{'target':53,'near':52,'far':2});self.assertEqual(s['frames'][-1],{'target':99,'near':98,'far':48})
        self.assertEqual(s['formations'][0],{'target':14,'near':13,'far':1});self.assertEqual(s['formations'][-1],{'target':25,'near':24,'far':12})
        for p in s['frames']:self.assertEqual((p['target']-p['near'],p['target']-p['far']),(1,51))
        for p in s['formations']:self.assertEqual((p['target']-p['near'],p['target']-p['far']),(1,13))
    def test_known_delta_and_signs(self):
        v={1:[0.]*48,2:[.25]*48,3:[1.]*48}
        a=compare(1,2,3,v);b=compare(1,3,2,v);c=compare(1,2,2,v)
        self.assertEqual(a['delta_mae_far_minus_near'],.75);self.assertEqual(b['delta_mae_far_minus_near'],-.75)
        self.assertEqual(summary([a,b,c])['neighbor_counts'],{'smaller':1,'equal':1,'larger':1})
        self.assertEqual(a['near']['mean_abs_y'],a['far']['mean_abs_y'])
    def test_zero_and_positionwise_192(self):
        z=compare(1,2,3,{k:[0.]*192 for k in (1,2,3)});self.assertEqual(z['neighbor'],'equal')
        r=compare(1,2,3,{1:[0,1]*96,2:[1,0]*96,3:[0,1]*96});self.assertEqual(r['near']['mae'],1);self.assertEqual(r['far']['mae'],0)
    def test_origin_rejected(self):
        vectors={i:[float(i)]*48 for i in range(1,101)}
        states=[];receipts=[]
        for j in range(1,26):
            frames=[dict(ordinal=i,values=vectors[i],segment=f'p{j}') for i in range(4*j-3,4*j+1)]
            states.append(dict(index=4*j,state={'_candidate':{'candidate_generation':j,'frames':frames}}));receipts.append(dict(segment=f'p{j}',result={'candidate_generation':j}))
        record={'states':states,'formation_receipts':receipts};self.assertEqual(len(formations_from_record(record,vectors)),25)
        states[0]['state']['_candidate']['frames'][0]['ordinal']=2
        with self.assertRaisesRegex(ValueError,'FORMATION_ORDINALS'):formations_from_record(record,vectors)
if __name__=='__main__':unittest.main()
