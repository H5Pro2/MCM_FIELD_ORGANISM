"""Bounded neutral Q1-Q5. Full 64-case neutral pass is separately invoked once."""
import ast
import copy
import gzip
import hashlib
import inspect
import io
import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools import s2uc_ulz1 as run
from tools import _s2uc_ulz1_sources as source
from tools import _s2uc_ulz1_engine as engine
from tools import _s2uc_ulz1_stats as stats
from tools._s2uc_ulz1_last import LastErrorAdapter
from tools._s2uc_multi_error import MultiErrorAdapter
from tools._s2uc_ulz1_replay import replay as arm_replay
from tools._s2uc_ulz1_resources import Meter
from tests import test_s2uc_multi_error as fixtures

OUTPUT=None

def neutral_short():
    # New technical sequence, not the four already accepted 28-frame cases.
    catalog=[[b+j/4096 for j in range(48)] for b in (.125,.5,.25,.75,.375)]
    ys=[2,2,3,3,4,2,4,4,3,3,2,4]
    return dict(catalog=catalog,ids=[k for y in ys for k in (0,1,y,0)],neutral_only=True)

def synthetic_reports(kind):
    plan=source.plan();reports=[]
    for s in plan['cases']:
        rows=[]
        for t in plan['masks']['G']:
            u,l=.25,.25
            if kind=='expected':
                if s['condition']=='S' and t in plan['masks']['Y_33_128']:u=.125
                if s['condition']=='W' and t in plan['masks']['Y_129_160']:l=.125
            elif kind=='opposite':
                if s['condition']=='S' and t in plan['masks']['Y_33_128']:l=.125
                if s['condition']=='W' and t in plan['masks']['Y_129_160']:u=.125
            elif kind=='secondary' and t in plan['masks']['G_skeleton']:u=0.
            rows.append(dict(target=t,U=u,L=l))
        metrics={m:{a:sum(x[a] for x in rows if x['target'] in ts)/len(ts) for a in ('U','L')}
                 for m,ts in plan['masks'].items()}
        reports.append(s|dict(rows=rows,metrics=metrics,complete=True))
    return reports

class ULZTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=None
        if OUTPUT is None:
            cls.tmp=tempfile.TemporaryDirectory(prefix='ulz-focused-')
            cls.folder=Path(cls.tmp.name)
        else:cls.folder=OUTPUT
    @classmethod
    def tearDownClass(cls):
        if cls.tmp:cls.tmp.cleanup()

    def test_Q1_frozen_U_and_only_last_update(self):
        binding=source.read(source.ROOT/'docs/S2UC_LZ1_V1_20261004_CODEBINDUNG.json')
        self.assertEqual(source.sha(source.ROOT/'tools/_s2uc_multi_error.py'),binding['files']['tools/_s2uc_multi_error.py'])
        # Reviewable static identity: the only overridden method is consume_feedback;
        # compare its complete source with U minus precisely the EMA branch.
        a=inspect.getsource(MultiErrorAdapter.consume_feedback)
        old='''                    if slot is not None:
                        old = CELL.unpack_from(self.bank, slot*32)
                        ec = .5*old[1]+.5*ec
                        new_ep = .5*old[2]+.5*ep
                    else:
'''
        self.assertIn(old,a)
        self.assertEqual(a.replace(old,'                    if slot is None:\n'),inspect.getsource(LastErrorAdapter.consume_feedback))
        self.assertEqual({k for k in LastErrorAdapter.__dict__ if not k.startswith('__')}, {'consume_feedback'})
        with patch.object(fixtures,'MultiErrorAdapter',LastErrorAdapter),patch.object(fixtures.adapter,'__defaults__',(LastErrorAdapter,)):
            a=fixtures.fixture()
            fixtures.seed(a,0,0,1,0,.9,.8)
            fixtures.freeze(a)
            a.consume_feedback(fixtures.sample(a,fixtures.vec(.7)))
            cell=next(c for c in fixtures.cells(a) if c[0]==1)
            self.assertAlmostEqual(cell[1],.1)
            self.assertAlmostEqual(cell[2],.4)
            a._terminate()

    def test_Q2_cell_lifecycle_six_ties_atomic_failures(self):
        methods=['test_T02_cold','test_T03_ties_and_negative_zero','test_T04_different_history_and_order',
            'test_T05_six_and_nine','test_T06_loss_no_resurrection','test_T07_promotion_open_ticket',
            'test_T08_original_not_current_store','test_T09_invalid','test_T10_every_publication_field',
            'test_T11_reentrancy_end_and_double','test_R02_resources']
        details={}
        for cls in (MultiErrorAdapter,LastErrorAdapter):
            with patch.object(fixtures,'MultiErrorAdapter',cls),patch.object(fixtures.adapter,'__defaults__',(cls,)):
                suite=unittest.TestSuite(fixtures.MultiTests(m) for m in methods)
                stream=io.StringIO();result=unittest.TextTestRunner(stream=stream).run(suite)
                self.assertTrue(result.wasSuccessful(),stream.getvalue())
                details[cls.__name__]=dict(tests=result.testsRun,output=stream.getvalue())
        if OUTPUT:run.save(OUTPUT/'Q2-details.json',details)

    def test_Q3_regular_pair_and_rejection(self):
        r=engine.replay(neutral_short(),short=True)
        self.assertTrue(r['lifecycle_equal'] and r['U']['cleanup'] and r['L']['cleanup'])
        self.assertTrue(any(len(x['hypotheses'])==3 for x in r['U']['rows']))
        self.assertTrue(any(len({h['before'][1] for h in x['hypotheses'] if h['before']})>1 for x in r['U']['rows']))
        self.assertTrue(any(x['before']['candidate'] and not x['after']['candidate'] for x in r['U']['events']))
        self.assertGreaterEqual(len(r['U']['full_confirmations']),4)
        vals=source.values(neutral_short())[:8]
        u=arm_replay(vals,'1'*64,False,lambda:None)
        l=copy.deepcopy(u);l['events'][0]['after']['candidate_serial']+=1
        with self.assertRaisesRegex(ValueError,'PAIRED_STOCK'):engine.equal_lifecycle(u,l)
        l=copy.deepcopy(u);l['rows'][0]['updates'].append({'live':False})
        with self.assertRaisesRegex(ValueError,'PAIRED_FEEDBACK'):engine.equal_lifecycle(u,l)
        if OUTPUT:run.save(OUTPUT/'Q3-short.json',r)

    def test_Q4_independent_resampling_quantiles_and_directions(self):
        ws=stats.weights();ds=[i/32 for i in range(32)]
        expanded=[]
        for z in range(10000):
            ids=[int(hashlib.sha256(('MCM-ULZ1/bootstrap/v1/z='+str(z)+'/k='+str(k)).encode()).hexdigest()[:16],16)%32 for k in range(32)]
            self.assertEqual(list(ws[z]),[ids.count(i) for i in range(32)])
            expanded.append(sum(ds[i] for i in ids)/32)
        expanded.sort()
        def independently(q):
            pos=9999*q;i=int(pos);f=pos-i
            return (1-f)*expanded[i]+f*expanded[min(i+1,9999)]
        self.assertEqual(stats.interval(ds,ws,True),[independently(.0125),independently(.9875)])
        outcomes={}
        for kind,expected in [('expected','BELEGT'),('opposite','WIDERLEGT'),('secondary','NICHT_NACHGEWIESEN')]:
            result=stats.aggregate(synthetic_reports(kind),source.plan())
            self.assertEqual(result['Abwaegung'],expected)
            prim=[x for x in result['contrasts'] if x['primary']]
            self.assertEqual(len(prim),2)
            outcomes[kind]=prim
        if OUTPUT:run.save(OUTPUT/'Q4-independent.json',outcomes)

    def test_Q4_incomplete_invalid_clusters_masks(self):
        reports=synthetic_reports('secondary')
        for kind in ('missing','cluster','target','metric','nan'):
            r=copy.deepcopy(reports)
            if kind=='missing':r.pop()
            elif kind=='cluster':r[0]['replicate']=2
            elif kind=='target':r[0]['rows'].pop()
            elif kind=='metric':r[0]['metrics']['G']['U']+=1
            else:r[0]['rows'][0]['U']=float('nan')
            with self.assertRaises(ValueError):stats.aggregate(r,source.plan())

    def test_Q5_source_gate_mask_counts(self):
        with self.assertRaises(PermissionError):source.research_choices(1,'S')
        with self.assertRaises(PermissionError):source.materialize(source.plan()['cases'][0])
        with patch.object(source,'research_choices',side_effect=AssertionError('RESEARCH_CALLED')):
            r=source.materialize(source.plan()['cases'][0],neutral=True)
        self.assertEqual(len(r['ids']),1040);self.assertTrue(r['neutral_only'])
        m=source.masks()
        self.assertEqual([len(m[k]) for k in ('G','G_Y','G_skeleton','Y_33_128','Y_129_160')],[519,256,256,96,32])
        self.assertEqual(len(source.plan()['cases']),64)

    def test_Q5_supervisor_failures_and_no_restart(self):
        plan=source.plan()|dict(cases=[])
        def invalid():raise PermissionError('NO_AUTHORIZATION')
        r=run.supervise(self.folder/'invalid',invalid,neutral=True)
        self.assertFalse(r['worker_started'])
        for fault in ('start_error','crash','worker_error','export','cancel'):
            r=run.supervise(self.folder/('fault-'+fault),lambda:(plan,0),neutral=True,fault=fault)
            self.assertEqual(r['status'],'NOT_EVALUABLE');self.assertFalse(r['worker_alive'])
        r=run.supervise(self.folder/'assessment-incomplete',lambda:(plan,0),neutral=True)
        self.assertEqual(r['status'],'NOT_EVALUABLE');self.assertFalse(r['worker_alive'])
        r=run.supervise(self.folder/'timeout',lambda:(plan,0),neutral=True,seconds=3,reserve_seconds=2,fault='hang')
        self.assertFalse(r['worker_alive']);self.assertEqual(r['status'],'NOT_EVALUABLE')
        for name,charge in (('prep-overflow',8*1048576+1),):
            r=run.supervise(self.folder/name,lambda:(plan,charge),neutral=True)
            self.assertFalse(r['worker_started'])
        r=run.supervise(self.folder/'prestart-time',lambda:(plan,0),neutral=True,seconds=2,reserve_seconds=1.999999999)
        self.assertFalse(r['worker_started'])
        old=source.sha(self.folder/'invalid/closure.json')
        r=run.supervise(self.folder/'invalid',invalid,neutral=True)
        self.assertEqual(r['status'],'REJECTED_EXISTING_OUTPUT')
        self.assertEqual(source.sha(self.folder/'invalid/closure.json'),old)

    def test_Q5_caps_and_auth(self):
        d=self.folder/'caps';d.mkdir();ledger=run.Ledger(d)
        with self.assertRaisesRegex(ValueError,'FILE_CAP'):ledger.write_bytes('x-case.json.gz',b'x'*(524288+1))
        with self.assertRaisesRegex(ValueError,'CASE_EXPANSION_LIMIT'):ledger.packed('x-case.json.gz',{'data':'x'*(4*1048576)})
        with self.assertRaisesRegex(ValueError,'FILE_CAP'):ledger.write_bytes('x-source.json',b'x'*32769)
        auth=self.folder/'pending.json';run.save(auth,dict(status='PENDING_SEPARATE_AUTHORIZATION'))
        with patch.object(run,'OUT',self.folder/'auth-reject'),patch.object(run,'verify_prestart'),patch.object(run,'expected_authorization',return_value={'status':'AUTHORIZED_ONCE'}):
            r=run.run(auth)
        self.assertFalse(r['worker_started'])
        self.assertEqual(64*(32768+524288)+1048576+8*1048576+run.RESERVE,44*1048576)

def verify_full(folder):
    c=source.read(folder/'closure.json');assert c['status']=='COMPLETE'
    done=source.read(folder/'worker-complete.json')
    assert (done['cases'],done['arms'],done['source_frames'],done['arm_frames'])==(64,128,66560,133120)
    maxima={a:{} for a in ('U','L')};expanded=packed=0
    for spec in source.plan()['cases']:
        p=folder/(spec['id']+'-case.json.gz');raw=gzip.decompress(p.read_bytes());r=json.loads(raw)
        expanded=max(expanded,len(raw));packed=max(packed,p.stat().st_size)
        assert r['complete'] and r['reference_equal'] and r['lifecycle_equal'] and r['neutral_only']
        assert len(r['rows'])==519
        for a in ('U','L'):
            assert r[a]['cleanup'] and r[a]['censored_target']==1041
            assert r['reference_advances'][a]==1040
            res=r['resources'][a]
            for k in ('additional_python_peak','original_frames_upper_bound','combined_upper_bound','receipt_bytes_peak','utf8_upper'):
                maxima[a][k]=max(maxima[a].get(k,0),res[k])
            for k,v in res['boundary_peaks'].items():maxima[a]['boundary_'+k]=max(maxima[a].get('boundary_'+k,0),v)
    for n,v in c['files'].items():assert source.sha(folder/n)==v['sha256'] and (folder/n).stat().st_size==v['bytes']
    run.save(folder.parent/'full-size-facts.json',dict(maxima=maxima,expanded_max=expanded,packed_max=packed,counts=done))

if __name__=='__main__':unittest.main()
