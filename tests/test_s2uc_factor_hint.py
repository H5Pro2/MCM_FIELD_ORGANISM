import unittest
from tools._s2uc_factor_hint import FactorHintArm
from tools._s2uc_provisional_hint import ProvisionalHintArm
from tools._s2uc_four_arm import tu


class FactorHintTests(unittest.TestCase):
    def test_json_zero_decoding_preserves_values(self):
        from tools.s2uc_factor_hint_check import decode_values
        p={'vectors':{'Z':[[0]*48]},'cases':{'zero':{'hint_values':[[0]*48,[0]*48]}}}
        decode_values(p)
        self.assertTrue(all(type(x) is float and x==0.0 for x in p['vectors']['Z'][0]))
        self.assertTrue(all(type(x) is float for frame in p['cases']['zero']['hint_values'] for x in frame))

    def submit(self,arm,values,segment,start):
        for i,v in enumerate(values):arm.form(tu.Frame((float(v),)*48,'a'*64,'test',segment,start+i))
        return arm.close_segment(segment)

    def hint(self,arm,values):
        before=arm.evidence()
        arm.hint(tu.Frame((float(values[0]),)*48,'a'*64,'test','h',100))
        r=arm.hint(tu.Frame((float(values[1]),)*48,'a'*64,'test','h',101))
        self.assertEqual(arm.evidence(),before)
        return r

    def test_all_other_paths_inherited(self):
        for name in ('form','close_segment','close_owner','resources','evidence'):
            self.assertIs(getattr(FactorHintArm,name),getattr(ProvisionalHintArm,name))

    def test_exact_confirmation_does_not_accept_gain(self):
        arm=FactorHintArm('a'*64,'test')
        self.submit(arm,[1,3,7,15],'a',1)
        self.assertEqual(self.submit(arm,[.5,1.5,3.5,7.5],'half',5)['action'],'TRACE_CANDIDATE_REPLACED')
        self.assertEqual(arm.inventory,())

    def test_zero_grouping_and_distinct_positions(self):
        arm=FactorHintArm('a'*64,'test')
        self.submit(arm,[0,0,0,0],'zero',1)
        r=self.hint(arm,[0,0])
        self.assertEqual(r['decision'],'ABSTAIN_AMBIGUOUS')
        self.assertEqual([m['offset'] for m in r['matches']],[0,1,2])
        self.assertTrue(all(m['factors']==[.5,1.,2.] for m in r['matches']))

    def test_order_and_framewise_factor_rejected(self):
        arm=FactorHintArm('a'*64,'test')
        self.submit(arm,[1,3,7,15],'a',1)
        for hint in ([1.5,.5],[.5,3]):
            self.assertEqual(self.hint(arm,hint)['matches'],[])

    def test_bandwise_factor_rejected(self):
        arm=FactorHintArm('a'*64,'test')
        self.submit(arm,[1,3,7,15],'a',1)
        arm.hint(tu.Frame((.5,)+(1.,)*47,'a'*64,'test','h',100))
        self.assertEqual(arm.hint(tu.Frame((1.5,)*48,'a'*64,'test','h',101))['matches'],[])

    def test_invalid_owner_and_closed(self):
        arm=FactorHintArm('a'*64,'test')
        with self.assertRaises(tu.S2TUError):arm.hint(tu.Frame((1.,)*48,'a'*64,'foreign','h',1))
        arm.close_owner()
        with self.assertRaises(tu.S2TUError):self.hint(arm,[1,3])


if __name__=='__main__':unittest.main()
