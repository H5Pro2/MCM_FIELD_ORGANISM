import unittest
from tools.s2uc_factor_transfer_check import variants,independent_matches,target_kind,classify
from tools._s2uc_provisional_hint import ProvisionalHintArm
from tools._s2uc_four_arm import tu


class TransferTests(unittest.TestCase):
    def test_variations_keep_order_except_explicit_reverse(self):
        pair=(tuple(float(i+1)/128 for i in range(48)),tuple(float(i+49)/128 for i in range(48)))
        result=variants(pair)
        self.assertEqual(result['original'],pair)
        self.assertEqual(result['reverse'],pair[::-1])
        self.assertEqual(result['local'],(result['half'][0],pair[1]))
        self.assertTrue(all(result['double'][j][b]==2*pair[j][b] for j in range(2) for b in range(48)))

    def test_target_requires_original_ordinals_and_position(self):
        target={'position':1,'origins':[{'formation':'a','ordinals':[1,2,3,4]}]}
        match=dict(role='retained',formation='a',ordinals=[1,2,3,4],offset=1)
        self.assertEqual(target_kind([match],'half',target),'TARGET_RETAINED')
        self.assertEqual(target_kind([dict(match,offset=0)],'half',target),'OTHER_RETAINED')
        self.assertEqual(target_kind([dict(match,ordinals=[5,6,7,8])],'half',target),'OTHER_RETAINED')
        self.assertEqual(target_kind([match],'reverse',target),'UNIQUE_CONTROL_ORIGIN_UNASSIGNED')

    def test_access_not_automatically_target(self):
        self.assertTrue(classify([],['match'],'OTHER_RETAINED')['other_origin_gain'])
        self.assertFalse(classify([],['match'],'OTHER_RETAINED')['correct_target_gain'])
        self.assertTrue(classify(['match'],['a','b'],'AMBIGUOUS')['lost_uniqueness'])
        self.assertTrue(classify([],['a','b'],'AMBIGUOUS')['new_competition'])

    def test_oracle_complete_positions_and_zero_factors(self):
        arm=ProvisionalHintArm('a'*64,'test')
        for i in range(4):arm.form(tu.Frame((0.,)*48,'a'*64,'test','a',i))
        arm.close_segment('a')
        matches=independent_matches(arm,((0.,)*48,(0.,)*48))
        self.assertEqual([m['offset'] for m in matches],[0,1,2])
        self.assertTrue(all(m['factors']==[.5,1.,2.] for m in matches))

    def test_oracle_requires_shared_factor_across_bands(self):
        arm=ProvisionalHintArm('a'*64,'test')
        for i,v in enumerate((1.,3.,7.,15.)):arm.form(tu.Frame((v,)*48,'a'*64,'test','a',i))
        arm.close_segment('a')
        self.assertEqual(independent_matches(arm,((.5,)+(1.,)*47,(1.5,)*48)),[])
        self.assertEqual(independent_matches(arm,((.5,)*48,(1.5,)*48))[0]['factors'],[.5])


if __name__=='__main__':unittest.main()
