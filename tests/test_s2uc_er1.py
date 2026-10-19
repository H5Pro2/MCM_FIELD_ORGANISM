import copy,hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from tools import _s2uc_er1_engine as engine
from tools import _s2uc_er1_source as source
from tools import _s2uc_er1_stats as stats
from tools._s2uc_er1_observer import compare,archive_form
from tools._s2uc_er1_archive import verify
from tools import _s2uc_ura1_delta_encode as codec
from tools._s2uc_ura1_capture_integrity import manifest,full_record_digest
ROOT=Path(__file__).resolve().parents[1]
def fixture(tail):
    return engine.blocks([(.125,.25)]*2+[(.875,.75)]*2+[(.125,.25)]+[(.375,.25)]*2+tail)
def run(values,mode,trace=True,fault=None):
    with patch.object(engine,'collection',list),patch.object(engine,'VALIDATE',lambda v:engine.need(v==values,'FIXTURE')):
        return engine.run_arm(values,mode,trace=trace,fault=fault)
class ER1Policy(unittest.TestCase):
    def test_01_retention_warm_origin_and_newer_loss(self):
        for tail,mode,origin in [([(.125,.25)],'E',[1,2,3,4]),([(.875,.75)],'F',[9,10,11,12])]:
            values=fixture(tail);e=run(values,'E');f=run(values,'F');o=compare(e,f)
            chosen=next(h for h in o[mode]['targets'][-1]['hypotheses'] if h['chosen'])
            self.assertEqual(chosen['origin'],origin);self.assertEqual(chosen['offset'],0)
            self.assertTrue(chosen['warm']);self.assertTrue(all(t<31 for t in chosen['prior_live_feedback']))
            self.assertTrue(chosen['prior_live_feedback'])
            self.assertEqual(o['E']['blocks'][6]['victims'],[[9,10,11,12]])
            self.assertEqual(o['F']['blocks'][6]['victims'],[[1,2,3,4]])
            self.assertEqual(o[mode]['targets'][-1]['error'],0.)
            self.assertEqual(o['F' if mode=='E' else 'E']['targets'][-1]['error'],.25)
    def test_02_equal_until_reorder_unmasked_and_equal_marks(self):
        values=fixture([(.125,.25)]);e=run(values,'E');f=run(values,'F')
        ee=e['events'];ff=f['events'];first=next(i for i,(a,b) in enumerate(zip(ee,ff)) if a!=b)
        self.assertEqual(ee[first]['state']['accepted'],20)
        self.assertEqual(ee[first]['state']['stock']['observation_end'],ff[first]['state']['stock']['observation_end'])
        self.assertEqual(ee[first]['state']['stock']['observation_end'][1],20)
        self.assertTrue(all(a==b for a,b in zip(ee[:first],ff[:first])))
        self.assertEqual(len(bytes.fromhex(ee[first]['state']['bank'])),416)
    def test_03_readmission_is_new_origin_and_downstream_cost(self):
        values=fixture([(.125,.25)]*2+[(.875,.75)]*2)
        o=compare(run(values,'E'),run(values,'F'))
        self.assertNotEqual(o['E']['blocks'][7]['action'],o['F']['blocks'][7]['action'])
        self.assertEqual(o['F']['blocks'][8]['new_originals'],[[29,30,31,32]])
        self.assertNotEqual(o['F']['blocks'][8]['new_originals'],[[1,2,3,4]])
    def test_04_corrupt_stock_and_feedback_fail_closed(self):
        for mode in ('E','F'):
            for fault in ('stock','feedback'):
                arms=[]
                with patch.object(engine,'CHECKPOINT',lambda a,m,i,s:arms.append(a) if s=='arm_cleanup' else None):
                    with self.assertRaises(ValueError):run(fixture([(.125,.25)]),mode,fault=fault)
                self.assertTrue(arms[-1].closed);self.assertFalse(any(arms[-1].bank))
    def test_05_policy_resource_limits(self):
        for mode in ('E','F'):
            r=run(fixture([(.125,.25),(.875,.75)]*2),mode,False)['resources']
            self.assertLessEqual(r['additional_python_peak'],16384)
            self.assertLessEqual(r['original_frames_upper_bound'],18)
            self.assertLessEqual(r['combined_upper_bound'],20)
            self.assertLessEqual(r['receipt_bytes_peak'],16384)
            self.assertLessEqual(r['utf8_upper'],32768)
    def test_06_long_policy_and_invalid_mode_rejected(self):
        with self.assertRaises(ValueError):run(engine.blocks([(.125,.25)]*256),'E')
        with self.assertRaises(ValueError):engine.create('C')
    def test_07_archives_independent_and_tamper(self):
        values=fixture([(.125,.25),(.875,.75)])
        with tempfile.TemporaryDirectory(dir=ROOT/'reports/s2uc') as tmp:
            with codec.store(tmp),patch.object(engine,'VALIDATE',lambda v:engine.need(v==values,'FIXTURE')):
                e=engine.run_arm(values,'E',trace=True);f=engine.run_arm(values,'F',trace=True)
                record=dict(source=values,E=e,F=f,observer=archive_form(compare(e,f),codec.collection))
                proof=manifest(record);expected=full_record_digest(record);path=Path(tmp)/'neutral.gz'
                codec.write_archive(record,path,expected)
                self.assertTrue(verify(path.read_bytes(),proof,expected)['er1_reference_equal'])
                record['observer']['counts']['affected_targets']+=1
                badproof=manifest(record);badexpected=full_record_digest(record);badpath=Path(tmp)/'bad.gz'
                codec.write_archive(record,badpath,badexpected)
                with self.assertRaisesRegex(ValueError,'ARCHIVE_OBSERVER'):verify(badpath.read_bytes(),badproof,badexpected)
        self.assertIsNone(codec.ACTIVE)
    def test_08_same_u_methods(self):
        from tools._s2uc_multi_error import MultiErrorAdapter
        from tools._s2uc_er1 import FifoAdapter
        for name in ('_receipt','consume_feedback','_admit','_promote'):
            self.assertIs(getattr(FifoAdapter,name),getattr(MultiErrorAdapter,name))
    def test_16_research_entry_denied_before_mutation(self):
        from tools import s2uc_er1_prepare as entry
        with patch('sys.argv',['er1','research']),patch.object(Path,'mkdir',side_effect=AssertionError('UNEXPECTED_WRITE')):
            with self.assertRaisesRegex(PermissionError,'ER1_RESEARCH_NOT_AUTHORIZED_OR_BOUND'):entry.main()

    def test_13_invalid_entry_initialization(self):
        from tools._s2uc_er1 import FifoAdapter,FifoObservationArm
        from tools._s2uc_multi_error import POLICY
        from tools._s2uc_pair_context_adapter import AdapterError
        for kwargs in (dict(hop=0),dict(start_sample=-1),dict(first_ordinal=True)):
            arm=FifoObservationArm(engine.PROFILE,'comparison')
            with self.assertRaises(AdapterError):FifoAdapter(arm,'stream',multi_policy=POLICY,**kwargs)
            arm.close_owner()
    def test_14_equal_selection_on_identical_stocks(self):
        from tools._s2uc_er1_reference import Reference
        cases=[[],[dict(key=(0,1,0),before=None)],[dict(key=(0,1,0),before=(0.,.25))],[dict(key=(0,1,0),before=(.5,.25))],[dict(key=(0,1,0),before=(0.,.25)),dict(key=(0,2,0),before=(0.,.25))]]
        for hs in cases:self.assertEqual(Reference.select(hs,'E'),Reference.select(hs,'F'))

class ER1SourceStats(unittest.TestCase):
    def test_09_all_neutral_sources_independent(self):
        for r in range(1,33):
            self.assertEqual(source.generate(r),source.reconstruct(r))
            compact=source.materialize(r)
            self.assertLessEqual(len(json.dumps(compact,separators=(',',':')).encode()),32768)
            self.assertEqual([tuple(compact['catalog'][i]) for i in compact['ids']],source.reference_frames(r))
        with self.assertRaises(ValueError):source.generate(0)
    def reports(self,value=0.):
        return [dict(replicate=r,orientation=(r-1)%2,complete=True,rows=[dict(target=t,E=.25+value,F=.25) for t in range(3,1024,2)]) for r in range(1,33)]
    def matrix(self):return (ROOT/'reports/s2uc/ura1-v4-preparation-20261015-01/bootstrap.bin').read_bytes()
    def test_10_full_denominator_and_independent_bootstrap(self):
        reports=self.reports()
        for r in reports:
            r['rows'][0]['E']=.75 if r['orientation']==0 else .125
        a=stats.aggregate(reports,self.matrix());b=stats.reference(reports,self.matrix())
        for key in ('mean','ci','pairs'):self.assertEqual(a['primary'][key],b[key])
        self.assertEqual(a['primary']['count'],16352)
        self.assertEqual(a['primary']['mean'],'3/8176')
        self.assertEqual([x['count'] for x in a['orientation']],[8176,8176])
    def test_11_decisions_and_empty_groups(self):
        for ci,wanted in [((-2,-1),'E_BETTER'),((1,2),'E_WORSE'),((-1,1),'INCONCLUSIVE'),((0,1),'INCONCLUSIVE'),((-1,0),'INCONCLUSIVE'),((0,0),'INCONCLUSIVE')]:self.assertEqual(stats.decision(ci),wanted)
        self.assertEqual(stats.balance([])['count'],0);self.assertIsNone(stats.balance([])['mean'])
        with self.assertRaises(ValueError):stats.decision((1,-1))
    def test_15_signed_synthetic_complete_aggregates(self):
        for value,wanted in [(-.125,'E_BETTER'),(.125,'E_WORSE'),(0.,'INCONCLUSIVE')]:
            reports=self.reports(value);a=stats.aggregate(reports,self.matrix());b=stats.reference(reports,self.matrix())
            self.assertEqual(a['primary']['verdict'],wanted)
            self.assertEqual(a['primary']['mean'],str(stats.F(value)))
            self.assertEqual(a['primary']['ci'],b['ci'])
            self.assertEqual(a['descriptive']['pre']['count'],8160)
            self.assertEqual(a['descriptive']['post']['count'],8192)
    def test_12_missing_targets_cases_orientation_invalid(self):
        reports=self.reports();reports[0]['rows'].pop()
        with self.assertRaises(ValueError):stats.aggregate(reports,self.matrix())
        with self.assertRaises(ValueError):stats.reference(reports,self.matrix())
        reports=self.reports();reports[0]['orientation']=1
        with self.assertRaises(ValueError):stats.aggregate(reports,self.matrix())
        with self.assertRaises(ValueError):stats.aggregate(reports[1:],self.matrix())
        with self.assertRaises(ValueError):stats.aggregate(self.reports(),bytes(320000))
