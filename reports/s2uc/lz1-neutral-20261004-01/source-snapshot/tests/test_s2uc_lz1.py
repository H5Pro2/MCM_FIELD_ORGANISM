"""Neutral LZ1 envelope qualification; research draw function never invoked."""
import copy
import gzip
import hashlib
import json
import time
import unittest
from unittest.mock import patch
from tools import s2uc_lz1 as run
from tools import _s2uc_lz1_sources as source
from tools import _s2uc_lz1_stats as stats
from tools._s2uc_lz1_h64 import H64,VECTOR,STRIDE
from tools._s2uc_lz1_reference import H64Reference
from tools._s2uc_lz1_engine import HMeter

OUTPUT=None

def vector(n):return tuple(.0625+n/8192+j/262144 for j in range(48))

class LZ1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan=source.read(run.PLAN)
        cls.reports=[]

    def test_01_full_96_triplet_pipeline(self):
        folder=OUTPUT/'integration'
        result=run.supervise(folder,lambda:(self.plan,8*1048576),neutral=True)
        self.assertEqual(result['status'],'COMPLETE',result)
        self.assertFalse(result['worker_alive'])
        done=source.read(folder/'worker-complete.json')
        self.assertEqual((done['cases'],done['arms'],done['source_frames'],done['targets_per_arm'],done['primary_targets_per_arm']),
            (96,288,99840,49824,24576))
        self.assertLess(done['engine_seconds'],3540)
        for n,v in result['files'].items():self.assertEqual(source.sha(folder/n),v['sha256'])
        maximum=dict(U_heap=0,H64_heap=0,case_expanded=0,case_packed=0)
        for spec in self.plan['cases']:
            p=folder/(spec['id']+'-case.json.gz');data=gzip.decompress(p.read_bytes());case=json.loads(data)
            self.assertTrue(case['neutral_only'] and case['complete'] and case['reference_equal'])
            self.assertEqual(case['cycle']['prefix_originals'],[[1,2,3,4],[9,10,11,12]])
            self.assertEqual(case['cycle']['two_live_hypotheses'],256)
            self.assertEqual(case['cycle']['live_feedback'],512)
            self.assertEqual(case['cycle']['warm_hypotheses'],512)
            self.assertEqual([r['H64_prior_count'] for r in case['rows']],list(range(519)))
            self.assertEqual(next(r for r in case['rows'] if r['target']==531)['H64_prior_count'],264)
            self.assertEqual(case['U']['reference_advances'],1040)
            self.assertTrue(case['U']['cleanup'])
            self.assertEqual(len(case['U']['forecasts']),520)
            self.assertEqual(len(case['U']['events']),520)
            maximum['U_heap']=max(maximum['U_heap'],case['resources']['U']['additional_python_peak'])
            maximum['H64_heap']=max(maximum['H64_heap'],case['resources']['H64_heap_peak'])
            maximum['case_expanded']=max(maximum['case_expanded'],len(data))
            maximum['case_packed']=max(maximum['case_packed'],p.stat().st_size)
            self.reports.append({k:case[k] for k in ('id','replicate','condition','rows','metrics','complete')})
        assessment=source.read(folder/'assessment.json')
        primary=[x for x in assessment['contrasts'] if x['primary']]
        self.assertEqual(len(primary),4)
        self.assertEqual({x['mask'] for x in primary},{'G_Y'})
        self.assertEqual({x['condition'] for x in primary},{'S','W'})
        self.assertEqual(len(assessment['contrasts']),81)
        self.assertEqual(len(assessment['harms']),54)
        run.save(OUTPUT/'full-size-facts.json',dict(maximum=maximum,counts=done,neutral_only=True,
            charged_worst_case_preparation_bytes=8*1048576))

    def test_02_masks_and_source_gate(self):
        m=self.plan['masks']
        self.assertEqual([len(m[x]) for x in ('G','G_init','G_post','G_Y','G_skeleton')],[519,7,512,256,256])
        self.assertEqual(sorted(m['G_init']+m['G_post']),m['G'])
        self.assertEqual(sorted(m['G_Y']+m['G_skeleton']),m['G_post'])
        self.assertEqual(m['Y_1_32']+m['Y_33_128']+m['Y_129_160']+m['Y_161_256'],m['G_Y'])
        with patch.object(source,'research_choices',side_effect=AssertionError('FORBIDDEN_RESEARCH_DRAWS')):
            for spec in self.plan['cases']:
                with self.assertRaises(PermissionError):source.materialize(spec)
                self.assertTrue(source.materialize(spec,neutral=True)['neutral_only'])
        with self.assertRaises(PermissionError):source.research_choices(1,'S')

    def test_03_h64_ties_overwrite_and_causal_guards(self):
        h=H64();ref=H64Reference();a,b=vector(1),vector(2)
        try:
            with self.assertRaisesRegex(ValueError,'NO_PENDING'):h.feedback(a)
            self.assertEqual(h.predict(a,b),b)
            with self.assertRaisesRegex(ValueError,'PENDING'):h.predict(a,b)
            h.feedback(vector(10))
            self.assertEqual(h.predict(a,b),vector(10));h.feedback(vector(11))
            self.assertEqual(h.predict(a,b),b);h.feedback(vector(12))
            # Independent model begins from the same three observed triples.
            for n in (10,11,12):ref.predict(a,b);ref.feedback(vector(n))
            for n in range(13,150):
                self.assertEqual(h.predict(a,b),ref.predict(a,b))
                h.feedback(vector(n));ref.feedback(vector(n))
                self.assertEqual(h.count,ref.count)
            self.assertEqual(h.count,140)
            self.assertEqual(VECTOR.unpack_from(h.ring,((h.count-1)%64)*STRIDE+768),vector(149))
            self.assertNotIn(vector(10),[VECTOR.unpack_from(h.ring,i*STRIDE+768) for i in range(64)])
        finally:h.close()
        self.assertFalse(any(h.ring))

    def test_04_h64_worst_unique_target_heap(self):
        h=H64();meter=HMeter(h);a,b=vector(1),vector(2)
        for n in range(70):
            meter.call(lambda:h.predict(a,b));meter.call(lambda:h.feedback(vector(100+n)))
        meter.call(lambda:h.predict(a,b));meter.call(h.close)
        self.assertLessEqual(meter.peak,128*1024)
        run.save(OUTPUT/'h64-stress.json',dict(heap_peak=meter.peak,ring_bytes=len(h.ring),unique_outcomes=64,cleanup=not any(h.ring)))

    def test_05_independent_cluster_reference(self):
        target=next(x for x in source.read(OUTPUT/'integration/assessment.json')['contrasts'] if x['primary'])
        values=target['per_replicate'];samples=[]
        # Expanded index sampling is independent of the production count-weight matrix.
        for z in range(1,10001):
            indices=[int.from_bytes(hashlib.sha256(f'MCM-LZ1/uncertainty/v1/z={z}/k={k}'.encode()).digest()[:8],'big')%32 for k in range(1,33)]
            samples.append(sum(values[i] for i in indices)/32)
        samples.sort()
        def q(p):
            h=9999*p;i=int(h);return samples[i]+(samples[min(i+1,9999)]-samples[i])*(h-i)
        self.assertEqual(target['ci'],[q(.00625),q(.99375)])
        self.assertEqual(stats.quantile([0.,10.],.25),2.5)

    def test_06_skeleton_gain_never_becomes_primary(self):
        reports=copy.deepcopy(self.reports)
        ys=set(self.plan['masks']['G_Y'])
        for r in reports:
            for row in r['rows']:
                row['P']=.25;row['U']=row['H64']=.25 if row['target'] in ys else 0.
            r['metrics']={m:{a:sum(x[a] for x in r['rows'] if x['target'] in ts)/len(ts) for a in ('P','U','H64')} for m,ts in self.plan['masks'].items()}
        with patch.object(stats,'weights',return_value=[bytes([1]*32)]):result=stats.aggregate(reports,self.plan)
        self.assertTrue(all(x['mean']==0 and x['verdict']=='NICHT_NACHGEWIESEN' for x in result['contrasts'] if x['primary']))
        self.assertTrue(any(x['mean']<0 for x in result['contrasts'] if x['condition']=='N' and x['mask']=='G_skeleton'))

    def test_07_missing_targets_cluster_and_metrics_rejected(self):
        bad=copy.deepcopy(self.reports);bad[0]['rows'].pop()
        with self.assertRaisesRegex(ValueError,'COMPLETE_TARGETS'):stats.aggregate(bad,self.plan)
        bad=copy.deepcopy(self.reports);bad[0]['replicate']=32
        with self.assertRaisesRegex(ValueError,'CLUSTER_IDENTITY'):stats.aggregate(bad,self.plan)
        bad=copy.deepcopy(self.reports);bad[0]['metrics']['G_Y']['U']+=.1
        with self.assertRaisesRegex(ValueError,'MASK_METRICS'):stats.aggregate(bad,self.plan)

    def test_08_authorization_and_prestart_failures(self):
        def invalid():raise PermissionError('EXACT_AUTHORIZATION_REQUIRED')
        r=run.supervise(OUTPUT/'invalid',invalid,neutral=True)
        self.assertFalse(r['worker_started']);self.assertEqual(r['status'],'NOT_EVALUABLE')
        self.assertFalse(list((OUTPUT/'invalid').glob('*source*')))
        r=run.supervise(OUTPUT/'start-error',lambda:(self.plan,0),neutral=True,fault='start_error')
        self.assertFalse(r['worker_started'])
        r=run.supervise(OUTPUT/'prep-overflow',lambda:(self.plan,8*1048576+1),neutral=True)
        self.assertFalse(r['worker_started']);self.assertIn('PREPARATION_LIMIT',r['error'])
        r=run.supervise(OUTPUT/'prestart-time',lambda:(self.plan,0),neutral=True,seconds=2,reserve_seconds=1.999999999)
        self.assertFalse(r['worker_started']);self.assertIn('PRESTART_TIME_LIMIT',r['error'])

    def test_09_runtime_faults_close(self):
        for fault in ('crash','worker_error','export','assessment','cancel'):
            r=run.supervise(OUTPUT/('fault-'+fault),lambda:(self.plan,0),neutral=True,fault=fault)
            self.assertEqual(r['status'],'NOT_EVALUABLE',fault);self.assertFalse(r['worker_alive'])
            self.assertEqual(set(r['verdicts'].values()),{'NOT_EVALUABLE'})
        start=time.monotonic()
        r=run.supervise(OUTPUT/'timeout',lambda:(self.plan,0),neutral=True,seconds=3,reserve_seconds=2,fault='hang')
        self.assertFalse(r['worker_alive']);self.assertLess(time.monotonic()-start,3)

    def test_10_caps_collision_and_real_auth_gate(self):
        caps=self.plan['export_caps']
        total=96*caps['source_each']+96*caps['case_each']+caps['administrative_pool']+8*1048576+run.RESERVE
        self.assertEqual(total,61*1048576);self.assertLess(total,run.LIMIT)
        d=OUTPUT/'caps';d.mkdir();ledger=run.Ledger(d)
        with self.assertRaisesRegex(ValueError,'FILE_CAP:case'):ledger.write_bytes('x-case.json.gz',b'x'*(512*1024+1))
        with self.assertRaisesRegex(ValueError,'CASE_EXPANSION_LIMIT'):ledger.packed('x-case.json.gz',{'v':'x'*(4*1048576)})
        prior=source.sha(OUTPUT/'invalid/closure.json')
        r=run.supervise(OUTPUT/'invalid',lambda:(self.plan,0),neutral=True)
        self.assertEqual(r['status'],'REJECTED_EXISTING_OUTPUT');self.assertEqual(prior,source.sha(OUTPUT/'invalid/closure.json'))
        auth=OUTPUT/'pending-auth.json';run.save(auth,dict(status='PENDING_SEPARATE_AUTHORIZATION'))
        with patch.object(run,'OUT',OUTPUT/'auth-reject'),patch.object(run,'verify_prestart'),patch.object(run,'expected_authorization',return_value={'status':'AUTHORIZED_ONCE'}):
            r=run.run(auth)
        self.assertFalse(r['worker_started']);self.assertIn('EXACT_AUTHORIZATION_REQUIRED',r['error'])

if __name__=='__main__':unittest.main()
