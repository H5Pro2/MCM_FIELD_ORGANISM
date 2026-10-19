import copy,json,unittest
from tools._s2uc_er1_stock_structural import stock_equal,structured_equal,generation_map

def stock(a=9,b=10):
    return dict(retained=[dict(generation=a,ordinals=[1,2,3,4],values=[(.25,.5)]*4),dict(generation=b,ordinals=[9,10,11,12],values=[(.75,.5)]*4)],candidate=dict(generation=12,ordinals=[17,18,19,20],values=[(.125,.5)]*4),forming=[21],candidate_serial=12,retained_serial=b,observation_end={a:8,b:16})
class Structural(unittest.TestCase):
    def test_01_generation_boundaries_and_json_roundtrip(self):
        for a,b in ((9,10),(99,100)):
            original=stock(a,b);decoded=json.loads(json.dumps(original))
            self.assertNotEqual(json.dumps(original,sort_keys=True),json.dumps(decoded,sort_keys=True))
            self.assertTrue(stock_equal(original,decoded));self.assertTrue(stock_equal(decoded,original))
    def test_02_insertion_order_and_mixed_unique_types(self):
        original=stock();other=dict(reversed(list(copy.deepcopy(original).items())))
        other['observation_end']={'10':16,9:8}
        self.assertTrue(stock_equal(original,other));self.assertEqual(len(generation_map(other['observation_end'])),2)
    def test_03_invalid_generation_keys(self):
        for key in (True,False,9.,None,0,-1,'0','09','+9',' 9','9 ','9.0','9e0','９','١','',str(2**64),2**64,(9,)):
            bad=stock();bad['observation_end']={key:8}
            with self.subTest(key=key):
                with self.assertRaises(ValueError):stock_equal(bad,bad)
    def test_04_collision_and_invalid_map_rejected(self):
        for marks in ({9:8,'9':8},{9:8,'9':99},[(9,8)],None):
            bad=stock();bad['observation_end']=marks
            with self.assertRaises(ValueError):stock_equal(bad,bad)
    def test_05_missing_extra_and_changed_endmarks(self):
        for change in ('missing','extra','value','type','missing_field'):
            bad=stock()
            if change=='missing':del bad['observation_end'][9]
            if change=='extra':bad['observation_end'][11]=24
            if change=='value':bad['observation_end'][9]=9
            if change=='type':bad['observation_end'][9]='8'
            if change=='missing_field':
                del bad['observation_end']
                with self.assertRaises(ValueError):stock_equal(stock(),bad)
            else:self.assertFalse(stock_equal(stock(),bad))
    def test_06_originals_order_and_values_still_checked(self):
        mutations=[lambda s:s['retained'].reverse(),lambda s:s['retained'][0]['ordinals'].__setitem__(0,99),lambda s:s['retained'][0]['values'].__setitem__(0,(.5,.5)),lambda s:s['candidate']['ordinals'].__setitem__(0,999),lambda s:s['forming'].append(22),lambda s:s.__setitem__('retained_serial',11),lambda s:s.__setitem__('candidate_serial',13),lambda s:s['retained'].pop(),lambda s:s.__setitem__('extra_field',True)]
        for mutate in mutations:
            bad=stock();mutate(bad);self.assertFalse(stock_equal(stock(),bad))
    def test_07_numeric_values_not_coerced_or_rounded(self):
        for value in (True,1.,'1'):
            bad=stock();bad['retained'][0]['ordinals'][0]=value
            self.assertFalse(stock_equal(stock(),bad))
        a=stock();b=stock();a['retained'][0]['values'][0]=(0.,.5);b['retained'][0]['values'][0]=(-0.,.5)
        self.assertFalse(stock_equal(a,b))
    def test_08_nested_observer_stock_and_no_input_mutation(self):
        a=dict(blocks=[dict(before=stock(99,100),after=stock())]);saved=copy.deepcopy(a)
        b=json.loads(json.dumps(a));self.assertTrue(structured_equal(a,b));self.assertEqual(a,saved)
        b['blocks'][0]['after']['retained'].reverse();self.assertFalse(structured_equal(a,b))
    def test_09_upper_bound_and_nonfinite(self):
        self.assertEqual(generation_map({str(2**64-1):1}),{2**64-1:1})
        for value in (float('nan'),float('inf')):
            bad=stock();bad['retained'][0]['values'][0]=(value,.5)
            with self.assertRaises(ValueError):stock_equal(bad,bad)
    def test_10_wire_duplicate_keys_rejected(self):
        import gzip
        from tools._s2uc_ura1_delta_fast_decode import Reader
        with self.assertRaisesRegex(ValueError,'DUPLICATE_KEY'):Reader(gzip.compress(b'{"x":1,"x":2}'))
