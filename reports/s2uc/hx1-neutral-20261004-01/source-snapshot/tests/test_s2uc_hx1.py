"""HX1 Q1-Q7: bounded neutral checks, no research stream access."""
import copy
import gzip
import hashlib
import io
import json
import tempfile
import unittest
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
from tools import _s2uc_hx1_sources as source
from tools import _s2uc_hx1_engine as engine
from tools import _s2uc_hx1_stats as stats
from tools import s2uc_hx1 as run
from tools._s2uc_hx1_baselines import GlobalMean,MeanReference,Persistence,bits
from tests import test_s2uc_multi_error as fixtures

OUTPUT=None

def short(condition='D'):
    record=source.materialize(dict(replicate=1,condition=condition),neutral=True)
    record['ids']=record['ids'][:48]
    return record

def tables():
    records=[]
    for spec in source.plan()['cases']:
        rows=[]
        for t in range(3,1024,2):
            q=t%4==3
            row=dict(target=t,U=.125 if q and spec['condition']=='D' else .25,G=.25,P=.25)
            if q: row.update(cue='X' if ((t-3)//4)%2==0 else 'Y',classification='V3')
            if q: row['class']=row.pop('classification')
            rows.append(row)
        records.append(spec|dict(rows=rows,complete=True))
    return records

class HXTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=None if OUTPUT else tempfile.TemporaryDirectory(prefix='hx-focused-')
        cls.folder=OUTPUT or Path(cls.tmp.name)
    @classmethod
    def tearDownClass(cls):
        if cls.tmp:cls.tmp.cleanup()

    def test_Q1_permutations_gates_rejection(self):
        with self.assertRaises(PermissionError):source.choices(1)
        with self.assertRaises(PermissionError):source.reference_choices(1)
        with self.assertRaises(PermissionError):source.materialize(source.plan()['cases'][0])
        with patch.object(source,'choices',side_effect=AssertionError('RESEARCH_CALLED')):
            self.assertEqual(len(source.materialize(source.plan()['cases'][0],neutral=True)['ids']),1024)
        for r in (1,2):
            ss={s:source.Stream(r,s,neutral=True) for s in ('continuation','dependent-A','dependent-B','null-cue')}
            y=ss['continuation'].permute([3]*8+[4]*8)
            a=ss['dependent-A'].permute([i for i,v in enumerate(y) if v==3])
            b=ss['dependent-B'].permute([i for i,v in enumerate(y) if v==4])
            ka,kb=(6,2) if r==1 else (2,6);x=set(a[:ka]+b[:kb])
            d=[0 if i in x else 1 for i in range(16)];n=ss['null-cue'].permute([0]*8+[1]*8)
            self.assertEqual((y,d,n,{k:s.d for k,s in ss.items()}),source.reference_choices(r,neutral=True,size=16))
        limit=2**64-(2**64%3)
        s=source.Stream(1,'test',neutral=True,draw=lambda d:limit if d==0 else limit-1)
        self.assertEqual(s.below(3),2);self.assertEqual(s.d,2)
        self.assertEqual(s.below(1),0);self.assertEqual(s.d,3)
        s.d=4096
        with self.assertRaisesRegex(ValueError,'DRAW_LIMIT'):s.below(2)
        s=source.Stream(1,'hand',neutral=True,draw=lambda d:0)
        self.assertEqual(s.permute([0,1,2,3]),[1,2,3,0])

    def test_Q2_unchanged_U_lifecycle(self):
        binding=source.read(source.ROOT/'docs/S2UC_ULZ1_V1_20261004_CODEBINDUNG.json')
        self.assertEqual(source.sha(source.ROOT/'tools/_s2uc_multi_error.py'),binding['files']['tools/_s2uc_multi_error.py'])
        names=['test_T02_cold','test_T03_ties_and_negative_zero','test_T04_different_history_and_order',
            'test_T05_six_and_nine','test_T06_loss_no_resurrection','test_T07_promotion_open_ticket',
            'test_T08_original_not_current_store','test_T09_invalid','test_T10_every_publication_field',
            'test_T11_reentrancy_end_and_double','test_R02_resources']
        stream=io.StringIO();result=unittest.TextTestRunner(stream=stream).run(unittest.TestSuite(fixtures.MultiTests(n) for n in names))
        self.assertTrue(result.wasSuccessful(),stream.getvalue())
        if OUTPUT:run.save(OUTPUT/'Q2-details.json',dict(tests=result.testsRun,output=stream.getvalue()))

    def test_Q3_baselines_causal_phase_and_pair(self):
        d=engine.replay(short('D'),short=True);n=engine.replay(short('N'),short=True)
        engine.equal_global(d,n)
        self.assertTrue(d['cleanup'] and n['cleanup'])
        self.assertEqual(d['G_Q'][0]['pre'],'00'*400)
        self.assertNotEqual(d['G_Q'][0]['pre'],d['G_Q'][0]['post'])
        broken=copy.deepcopy(n);broken['G_Q'][0]['error']+=.1
        with self.assertRaisesRegex(ValueError,'G_DN'):engine.equal_global(d,broken)
        changed=short();changed['ids'][2]=4
        other=engine.replay(changed,short=True)
        self.assertNotEqual(other['G_Q'][1]['pre'],d['G_Q'][1]['pre'])
        if OUTPUT:run.save(OUTPUT/'Q3-short.json',dict(D=d,N=n))

    def test_Q4_references_reject_corruption(self):
        original=GlobalMean.accept
        def bad(self,i,v):
            original(self,i,v)
            if i==3:self.bank[0]^=1
        with patch.object(GlobalMean,'accept',bad):
            with self.assertRaisesRegex(ValueError,'G_STATE_REFERENCE'):engine.replay(short(),short=True)
        import tools._s2uc_hx1_replay as replay
        with patch.object(replay,'select',return_value=(0,999,0)):
            with self.assertRaisesRegex(ValueError,'SELECTION_REFERENCE'):engine.replay(short(),short=True)
        g=GlobalMean()
        with self.assertRaisesRegex(ValueError,'G_INPUT'):g.accept(2,tuple([.5]*48))
        g.close()

    def test_Q5_statistics_three_required_and_reference(self):
        draws=stats.matrix()
        for z,row in enumerate(draws):
            expected=[]
            for o in range(2):
                for k in range(16):
                    h=hashlib.sha256(('MCM-HX1/bootstrap/v1/z='+str(z)+'/orientation='+str(o)+'/k='+str(k)).encode()).hexdigest()
                    expected.append(2*(int(h[:16],16)%16)+o)
            self.assertEqual(row,expected)
        for vals,verdict in [([F(-1,8)]*32,'BELEGT'),([F(0)]*32,'NICHT_NACHGEWIESEN'),([F(1,8)]*32,'WIDERLEGT')]:
            result=stats.primary([vals]*3,draws)
            self.assertTrue(all(x['verdict']==verdict for x in result['primary']))
            self.assertEqual([x['ci'] for x in result['primary']],[[str(x) for x in ci] for ci in stats.reference_primary([vals]*3,draws)])
        mixed=stats.primary([[F(-1,8)]*32,[F(-1,8)]*32,[F(0)]*32],draws)
        self.assertEqual(mixed['verdict'],'HINWEISNUTZEN_NICHT_NACHGEWIESEN')
        v=[F(i-16,32) for i in range(32)]
        self.assertEqual(stats.interval(v,draws,True),stats.reference_primary([v],draws)[0])
        self.assertEqual(stats.quantile([F(0),F(1),F(3)],F(3,4)),F(2))
        rows=tables();result=stats.aggregate(rows)
        self.assertEqual(result['verdict'],'HINWEISNUTZEN_BELEGT')
        for corrupt in (rows[:-1],copy.deepcopy(rows)):
            if len(corrupt)==64:corrupt[0]['rows'].pop()
            with self.assertRaises(ValueError):stats.aggregate(corrupt)
        if OUTPUT:run.save(OUTPUT/'Q5-handtables.json',dict(primary=result['primary'],mixed=mixed))

    def test_Q6_partition_and_export(self):
        result=engine.replay(short(),short=True)
        q=[r for r in result['rows'] if r['target']%4==3]
        self.assertEqual(len(q),12)
        self.assertTrue(all(r['class'] in ('V0','V1','V2','V3') for r in q))
        self.assertIn('V0',[r['class'] for r in q]);self.assertIn('V1',[r['class'] for r in q])
        folder=self.folder/'export';folder.mkdir();ledger=run.Ledger(folder)
        ledger.packed('neutral-case.json.gz',result)
        self.assertEqual(source.raw(json.loads(gzip.decompress((folder/'neutral-case.json.gz').read_bytes()))),source.raw(result))
        for name,size in [('x-source.json',32769),('x-case.json.gz',524289)]:
            with self.assertRaises(ValueError):ledger.write_bytes(name,b'x'*size)
        with self.assertRaisesRegex(ValueError,'CASE_EXPANSION'):ledger.packed('large-case.json.gz',{'x':'x'*(4*1048576)})
        with self.assertRaises(ValueError):engine.BaselineMeter(GlobalMean(),1).operation(lambda:None)

    def test_Q7_supervisor_memory_time_authorization(self):
        def invalid():raise PermissionError('NO_AUTHORIZATION')
        plan=source.plan()|dict(cases=[])
        r=run.supervise(self.folder/'invalid',invalid,neutral=True)
        self.assertFalse(r['worker_started'])
        for fault in ('start_error','crash','worker_error','export','cancel','memory'):
            r=run.supervise(self.folder/('fault-'+fault),lambda:(plan,0),neutral=True,fault=fault)
            self.assertEqual(r['status'],'NOT_EVALUABLE');self.assertFalse(r['worker_alive'])
        evidence=source.read(self.folder/'fault-memory/memory-enforcement.json')
        self.assertTrue(evidence['allocation_rejected'])
        self.assertEqual(r['process_memory']['limit_bytes'],512*1048576)
        r=run.supervise(self.folder/'timeout',lambda:(plan,0),neutral=True,seconds=3,reserve_seconds=2,fault='hang')
        self.assertEqual(r['status'],'NOT_EVALUABLE');self.assertFalse(r['worker_alive'])
        r=run.supervise(self.folder/'prep-over',lambda:(plan,8*1048576+1),neutral=True)
        self.assertFalse(r['worker_started'])
        before=source.sha(self.folder/'invalid/closure.json')
        r=run.supervise(self.folder/'invalid',invalid,neutral=True)
        self.assertEqual(r['status'],'REJECTED_EXISTING_OUTPUT');self.assertEqual(source.sha(self.folder/'invalid/closure.json'),before)
        with patch.object(run,'OUT',self.folder/'pending-auth'),patch.object(run,'verify_prestart'),patch.object(run,'expected_authorization',return_value={'status':'AUTHORIZED_ONCE'}):
            path=self.folder/'pending.json';run.save(path,{'status':'PENDING_SEPARATE_AUTHORIZATION'})
            r=run.run(path);self.assertFalse(r['worker_started'])

def verify_full(folder):
    closure=source.read(folder/'closure.json')
    if closure['status']!='COMPLETE':raise ValueError('FULL_NOT_COMPLETE')
    done=source.read(folder/'worker-complete.json')
    if (done['cases'],done['arms'],done['arm_frames'])!=(64,192,196608):raise ValueError('FULL_COUNTS')
    maxima={a:{} for a in ('U','G','P')};expanded=packed=0;previous=None
    for spec in source.plan()['cases']:
        path=folder/(spec['id']+'-case.json.gz');data=gzip.decompress(path.read_bytes());r=json.loads(data)
        if not r['neutral_only'] or not r['complete'] or len(r['rows'])!=511 or not r['cleanup']:raise ValueError('FULL_CASE')
        if spec['condition']=='D':previous=r['G_Q']
        else:engine.equal_global({'G_Q':previous},r)
        expanded=max(expanded,len(data));packed=max(packed,path.stat().st_size)
        for arm,res in r['resources'].items():
            for key,value in res.items():
                if isinstance(value,(int,float)):maxima[arm][key]=max(maxima[arm].get(key,0),value)
    for n,v in closure['files'].items():
        if source.sha(folder/n)!=v['sha256'] or (folder/n).stat().st_size!=v['bytes']:raise ValueError('FULL_HASH')
    run.save(folder.parent/'full-size-facts.json',dict(maxima=maxima,expanded_max=expanded,packed_max=packed,counts=done,process_memory=closure['process_memory']))

if __name__=='__main__':unittest.main()
