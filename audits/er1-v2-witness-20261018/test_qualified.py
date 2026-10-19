import copy
import unittest
from checker_qualified import reconstruct, compare, counts, continuous

def fixture():
    source=[[i] for i in range(24)]
    a=((1,2,3,4),1);b=((5,6,7,8),2);c=((9,10,11,12),3)
    data={}
    for mode in ('E','F'):
        frames={i:dict(retained=[a,b] if i<16 else ([a,c] if mode=='E' else [b,c]),candidate=[],marks={1:8,2:8,3:12}) for i in range(25)}
        chosen=dict(origin=a[0],generation=1,offset=0,warm=True,prior=[7,11]) if mode=='E' else None
        data[mode]=dict(frames=frames,targets={19:dict(chosen=chosen,output=[2],error=0 if mode=='E' else .25)})
    return data,source

class Qualification(unittest.TestCase):
    def setUp(self):
        self.data,self.source=fixture();self.records,_=reconstruct(self.data,self.source)
    def test_positive(self):
        self.assertEqual([x['stage'] for x in self.records if x['keeper']=='E'],['retention','warm_use'])
        self.assertFalse(compare(self.records,self.records)['unsupported'])
    def test_false_feedback_time(self):
        self.data['E']['targets'][19]['chosen']['prior']=[19]
        expected,_=reconstruct(self.data,self.source)
        self.assertTrue(compare(expected,self.records)['unsupported'])
    def test_false_offset(self):
        bad=copy.deepcopy(self.records)
        next(x for x in bad if x['stage']=='warm_use')['offset']=1
        self.assertTrue(compare(self.records,bad)['unsupported'])
    def test_broken_origin(self):
        self.data['E']['frames'][17]['retained']=[]
        expected,_=reconstruct(self.data,self.source)
        self.assertTrue(compare(expected,self.records)['unsupported'])
    def test_missing_countervictim(self):
        self.data['F']['frames'][16]['retained']=self.data['F']['frames'][12]['retained']
        expected,_=reconstruct(self.data,self.source)
        self.assertTrue(compare(expected,self.records)['unsupported'])
    def test_asymmetric_promotion(self):
        # Keeper retains its old stock; only opponent promotes and loses the origin.
        for i in range(16,25):
            self.data['E']['frames'][i]['retained']=self.data['E']['frames'][12]['retained']
        expected,_=reconstruct(self.data,self.source)
        self.assertTrue(any(x['keeper']=='E' and x['stage']=='warm_use' for x in expected))
    def test_feedback_line_break(self):
        self.data['E']['frames'][10]['retained']=[]
        expected,_=reconstruct(self.data,self.source)
        self.assertFalse(any(x['keeper']=='E' and x['stage']=='warm_use' and 7 in x['prior_live_feedback'] for x in expected))
    def test_candidate_promotion_continuity(self):
        identity=(1,2,3,4)
        frames={i:dict(candidate=[(identity,9)] if i<12 else [],retained=[] if i<12 else [(identity,2)]) for i in range(10,15)}
        self.assertTrue(continuous(frames,identity,10,15))
        frames[11]['candidate']=[]
        self.assertFalse(continuous(frames,identity,10,15))
    def test_retained_generation_jump(self):
        identity=(1,2,3,4)
        frames={10:dict(candidate=[],retained=[(identity,1)]),11:dict(candidate=[],retained=[(identity,2)])}
        self.assertFalse(continuous(frames,identity,10,12))
    def test_omission(self):
        self.assertTrue(compare(self.records,self.records[:-1])['missing'])
    def test_duplicate(self):
        self.assertTrue(compare(self.records,self.records+self.records[:1])['duplicate_records'])
    def test_target_deduplication(self):
        warm=next(x for x in self.records if x['stage']=='warm_use')
        second=warm|dict(promotion_end=20)
        c=counts([warm,second])['E']
        self.assertEqual((c['warm_uses'],c['unique_warm_targets']),(2,1))

if __name__=='__main__':unittest.main()
