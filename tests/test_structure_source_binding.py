import copy
import hashlib
import unittest
from tools import _structure_source_binding as s


class Tests(unittest.TestCase):
    def test_determinism(self):
        recipe=dict(background=[[0,0,2,3]],foreground=[[1,1,3,2]])
        before=copy.deepcopy(recipe)
        a=s.render(recipe,4,3);b=s.render(recipe,4,3)
        self.assertEqual(a,b);self.assertEqual(recipe,before)
        expected=[]
        for y in range(3):
            for x in range(4):
                expected += [216 if y==1 and 1<=x<3 else 48 if x<2 else 24]*3
        self.assertEqual(a,bytearray(expected))

    def test_exact_identity_time(self):
        e,_=s.plans();rows=e['sources']
        self.assertEqual(len({x['id'] for x in rows}),14)
        for i,x in enumerate(rows):
            self.assertEqual(x['time'],[i,30]);self.assertEqual(x['frame_index'],i)
        for a,b in ((0,12),(6,13)):
            self.assertEqual(rows[a]['recipe'],rows[b]['recipe'])
            self.assertNotEqual(s.digest(rows[a]),s.digest(rows[b]))

    def test_pairs_criteria(self):
        _,v=s.plans()
        self.assertEqual(len(v['pairs']),22);self.assertEqual(len(v['criteria']),24)
        expected=[]
        for anchor,other in ((0,3),(3,0),(6,9),(9,6)):
            expected.extend([[anchor,t] for t in (anchor+1,anchor+2,other,other+1,other+2)])
        self.assertEqual(v['pairs'],expected+[[0,12],[6,13]])
        self.assertEqual(sum(c['kind']=='GLOBAL_STRICT' for c in v['criteria']),8)
        for c in v['criteria']:
            self.assertTrue(all(0<=i<20 for i in c['within']+c['between']))

    def test_separation(self):
        e,v=s.plans()
        self.assertFalse({'roles','pairs','criteria'} & set(e))
        self.assertEqual(set(e['sources'][0]['recipe']),{'background','foreground'})
        self.assertEqual(v['work']['differences'],19008)

    def test_budget(self):
        self.assertFalse(s.budget(0,65536,1048576,262144)['violations'])
        for args,key in (((0,65537,0,0),'metadata'),((0,0,1048577,0),'evidence'),((0,0,0,262145),'verification'),((4194305,0,0,0),'TOTAL')):
            with self.subTest(key=key):self.assertIn(key,s.budget(*args)['violations'])

    def test_binding_rejection(self):
        e,v=s.plans();h=hashlib.sha256(b'neutral').hexdigest()
        r=dict(execution_digest=s.digest(e),evaluation_digest=s.digest(v),generated=14,
            sources=[dict(id=x['id'],source_digest=s.digest(x),bytes=6220800,sha256=h) for x in e['sources']],
            collisions=[[x['id'] for x in e['sources']]])
        self.assertEqual(s.verify(r,e,v)['status'],'BINDING_VALID')
        for kind in ('missing','foreign','hash'):
            with self.subTest(kind=kind):
                bad=copy.deepcopy(r)
                if kind=='missing':bad['sources'].pop()
                if kind=='foreign':bad['sources'][0]['source_digest']='0'*64
                if kind=='hash':bad['sources'][0]['sha256']='invalid'
                with self.assertRaises(s.BindingError):s.verify(bad,e,v)
