import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools import s2uc_promotion_qualification as q
from tools._s2uc_promotion_replay import replay
from tools._s2uc_paired_error_replay import replay as old_replay
from tools._s2uc_ema_stock_observer import digest
from tests.test_s2uc_ema_stock import neutral

EXPORT_FOLDER=None
FACTS={}


def neutral_plan():
    masks=dict(G=list(range(3,16,2)),H=[7,11,15],N=[3,5,9,13],V=[7,15],D=[7],J=[15])
    return dict(stories=dict(NEUTRAL=dict(frames=16,masks=masks,expected_stock=[],expected_M_choices={})))


class RunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=None
        if EXPORT_FOLDER is None:
            cls.temp=tempfile.TemporaryDirectory();folder=Path(cls.temp.name)/'export'
        else:folder=EXPORT_FOLDER
        cls.folder=folder
        with patch.object(q,'material',side_effect=AssertionError('SWL_FORBIDDEN')):
            cls.output=q.export(folder,neutral_plan(),lambda p,s:neutral()[:16],mode='NEUTRAL_ONLY')
        FACTS['export']=dict(bytes=cls.output['bytes'],source='independent neutral prefix16',
            admissions=64,internal_reference_advances=64,SWL_generated=False,
            resources={a:r['resources'] for a,r in cls.output['results']['NEUTRAL'].items()})

    @classmethod
    def tearDownClass(cls):
        if cls.temp:cls.temp.cleanup()

    def test_Q1_four_arms_and_legacy_equivalence(self):
        profile=digest(dict(story='NEUTRAL',mode='NEUTRAL_ONLY',geometry='promotion48.v1'))
        for arm in ('E','K','P'):
            old=old_replay(neutral()[:16],profile,count=16,arm=arm)
            self.assertEqual(old['rows'],self.output['results']['NEUTRAL'][arm]['rows'])
        self.assertEqual(self.output['assessments']['NEUTRAL']['assignment'],'PASS')
        self.assertLessEqual(self.output['bytes'],4194304)
        meter=self.output['results']['NEUTRAL']['M']['resources']['meter']
        self.assertGreater(meter['transient_reference_frames_peak'],0)
        self.assertLessEqual(meter['transient_reference_frames_peak'],18)

    def test_Q2_no_authorization_no_generator(self):
        with patch.object(q,'verify'),patch.object(q,'read',return_value={'status':'PENDING'}),\
             patch.object(q,'auth',return_value={'status':'AUTHORIZED_ONCE'}),patch.object(q,'material') as source,\
             patch.object(q,'export') as export:
            with self.assertRaisesRegex(AssertionError,'PROMOTION_SEPARATE_AUTHORIZATION_REQUIRED'):q.run('pending')
            source.assert_not_called();export.assert_not_called()

    def test_Q3_existing_folder_cannot_repeat(self):
        with patch.object(q,'material') as source:
            with self.assertRaises(FileExistsError):q.export(self.folder,neutral_plan(),source,mode='NEUTRAL_ONLY')
            source.assert_not_called()

    def test_Q4_mismatched_hypothesis_is_not_repaired(self):
        results=self.output['results']['NEUTRAL'];before=copy.deepcopy(results);spec=neutral_plan()['stories']['NEUTRAL']
        spec['expected_stock']=[[8,[999],None]]
        result=q.assess(results,spec)
        self.assertEqual(result['assignment'],'NOT_EVALUABLE');self.assertTrue(result['expectation_deviations'])
        self.assertEqual(results,before)

    def test_Q5_failure_closure_and_no_retry(self):
        calls=[]
        def fail(values,profile,*,count,arm,evidence):
            calls.append(arm);evidence['phase']='injected_neutral_failure';raise RuntimeError('NEUTRAL_FAILURE')
        with tempfile.TemporaryDirectory() as tmp,patch.object(q,'replay',side_effect=fail):
            folder=Path(tmp)/'failed'
            with self.assertRaisesRegex(RuntimeError,'NEUTRAL_FAILURE'):
                q.export(folder,neutral_plan(),lambda p,s:neutral()[:16],mode='NEUTRAL_FAILURE')
            self.assertEqual(calls,['M']);self.assertEqual(q.read(folder/'closure.json')['status'],'NOT_EVALUABLE')
            self.assertEqual(q.read(folder/'partial.json')['phase'],'injected_neutral_failure')

    def test_Q6_D_cannot_hide_V_harm(self):
        r=copy.deepcopy(self.output['results']['NEUTRAL']);spec=neutral_plan()['stories']['NEUTRAL']
        for arm,result in r.items():
            for row in result['rows']:row['selected_mae']=(0. if row['target'] in spec['masks']['D'] else 4.) if arm=='M' else 1.
        result=q.assess(r,spec)
        self.assertEqual(result['baseline_benefit_V'],'SCHADEN')
        self.assertEqual(result['metrics']['D']['M']['mae'],0.)

    def test_Q7_actual_interruption_preserves_prestate_and_promotion_result(self):
        from tools._s2uc_promotion_ema import PromotionAdapter
        evidence={}
        def fail(self,stage,index):
            if stage=='generation_written':raise KeyboardInterrupt('NEUTRAL_REAL_PATH_FAILURE')
        with patch.object(PromotionAdapter,'_promotion_checkpoint',fail),self.assertRaises(KeyboardInterrupt):
            replay(neutral()[:16],'b'*64,count=16,arm='M',evidence=evidence)
        last=evidence['admissions'][-1]
        self.assertEqual(last['frame'],8);self.assertEqual(last['status'],'FAILED')
        self.assertTrue(last['cells_before']);self.assertEqual(last['cells_after'],[])
        self.assertTrue(last['terminal_closed']);self.assertEqual(last['promotion_result']['action'],'TRACE_PROMOTED')
        self.assertEqual(last['failure_stage'],'generation_written')


if __name__=='__main__':unittest.main()
