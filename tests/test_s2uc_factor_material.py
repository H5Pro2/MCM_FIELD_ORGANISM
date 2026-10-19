import copy,json,math,struct,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from tools import s2uc_factor_material as m
from tools.s2uc_factor_material_compare import evaluate_export

REPORT=m.ROOT/'reports/s2uc/factor-material-qualification-20261001-01'
FACTS={}
def save(p,v):p.write_text(json.dumps(v,indent=2,allow_nan=False),encoding='utf-8')

class MaterialTests(unittest.TestCase):
    def setUp(self):
        self.home=Path(tempfile.mkdtemp(prefix=self._testMethodName+'-',dir=REPORT))
        self.plan=copy.deepcopy(m.read(m.PLAN));spec=copy.deepcopy(self.plan['partitions']['FC-DEV'])
        for k,seed in zip('ABDZ',[810001,810007,810013,810019]):spec['episodes'][k].update(root='FC-NEUTRAL/'+k,seed=seed)
        for c in spec['cases'].values():c['truth']=c['truth'].replace('FC-DEV/','FC-NEUTRAL/')
        spec['output_directory']=str((self.home/'material').relative_to(m.ROOT)).replace('\\','/')
        self.plan['partitions']={'FC-NEUTRAL':spec};self.spec=spec
        self.pp=self.home/'neutral-plan.json';save(self.pp,self.plan)
        self.binding=copy.deepcopy(m.read(m.BINDING));self.binding.update(plan_path=str(self.pp.relative_to(m.ROOT)).replace('\\','/'),plan_sha256=m.sha(self.pp))
        self.bp=self.home/'neutral-binding.json';save(self.bp,self.binding)
        self.auth=dict(status='AUTHORIZED_ONCE',action='PRODUCE_FACTOR_PARTITION',partition='FC-NEUTRAL',binding_sha256=m.sha(self.bp),plan_sha256=m.sha(self.pp),python=sys.version)
        self.ap=self.home/'neutral-authorization.json';save(self.ap,self.auth)
        self.out=self.home/'material'
    def produce(self):return m.produce(self.ap,binding_path=self.bp)
    def test_G1_full_path_independent_values_lossless_and_reproducible(self):
        self.assertEqual(self.produce(),'MATERIAL_COMPLETE')
        rows=m.read_verified(self.out,self.spec,'FC-NEUTRAL',self.plan['profile'])
        expected={}
        for k,e in self.spec['episodes'].items():
            x=e['seed'];flat=[]
            for _ in range(192):
                x ^= (x<<13)&0xffffffff;x ^= x>>17;x ^= (x<<5)&0xffffffff;x &= 0xffffffff
                flat.append(float(1+x%1023)/4096.)
            expected[k]=[flat[j:j+48] for j in range(0,192,48)]
        expected['D'][:2]=copy.deepcopy(expected['A'][:2]);expected['Z'][:2]=[[0.]*48,[0.]*48]
        hashes={}
        for k,v in expected.items():
            actual=m.read(self.out/('base-'+k+'.json'))['values']
            self.assertEqual(struct.pack('<192d',*sum(v,[])),struct.pack('<192d',*sum(actual,[])))
            hashes[k]=m.vector_hash(actual)
        for cid,row in rows.items():
            c=self.spec['cases'][cid]
            refs=c['hint']+[c['target']]
            wanted=[[x*r['gain'] for x in expected[r['base']][r['frame']]] for r in refs]
            self.assertEqual(row['values'][-3:],wanted)
            self.assertEqual(row['truth'],c['truth']);self.assertEqual(len(row['origins']),len(row['values']))
        # A second neutral configuration/output exercises reproducibility without
        # reusing the one-shot output. Original production partitions never used.
        self.spec['output_directory']=str((self.home/'material-repeat-neutral').relative_to(m.ROOT)).replace('\\','/')
        self.pp=self.home/'repeat-neutral-plan.json';self.bp=self.home/'repeat-neutral-binding.json';self.ap=self.home/'repeat-neutral-authorization.json'
        self.binding['plan_path']=str(self.pp.relative_to(m.ROOT)).replace('\\','/')
        save(self.pp,self.plan);self.binding['plan_sha256']=m.sha(self.pp);save(self.bp,self.binding)
        self.auth.update(plan_sha256=m.sha(self.pp),binding_sha256=m.sha(self.bp));save(self.ap,self.auth)
        self.assertEqual(self.produce(),'MATERIAL_COMPLETE')
        second=m.ROOT/self.spec['output_directory']
        for k,h in hashes.items():self.assertEqual(m.read(second/('base-'+k+'.json'))['values_sha256'],h)
        FACTS['full_path']=dict(folder=str(self.out.relative_to(m.ROOT)),base_hashes=hashes,files=18,base_components=768,case_frames=sum(len(r['values']) for r in rows.values()),bytes=sum(p.stat().st_size for p in self.out.iterdir()),reproducibility=True)
    def test_G2_exclusive_claim_no_overwrite(self):
        self.produce();before={p.name:m.sha(p) for p in self.out.iterdir()}
        with self.assertRaises(FileExistsError):self.produce()
        self.assertEqual(before,{p.name:m.sha(p) for p in self.out.iterdir()})
        ledger=m.OutputLedger(self.home/'ledger')
        ledger.write('one.json',{'x':1})
        with self.assertRaises(FileExistsError):ledger.write('one.json',{'x':2})
        self.assertEqual(m.read(self.home/'ledger/one.json'),{'x':1})
    def test_G3_output_limit_reserved_closure(self):
        with patch.object(m.OutputLedger,'LIMIT',m.OutputLedger.RESERVE+1024):
            self.assertEqual(self.produce(),'NOT_EVALUABLE')
            c=m.read(self.out/'closure.json');self.assertIn('OUTPUT_LIMIT',c['error'])
            self.assertLessEqual(sum(p.stat().st_size for p in self.out.iterdir()),m.OutputLedger.LIMIT)
        self.assertEqual(c['case_files'],0)
        with self.assertRaises(FileExistsError):self.produce()
        FACTS['output_limit']=c
    def test_G4_partial_export_error_and_reader_closed(self):
        original=m.OutputLedger.write
        def fail(ledger,name,value,final=False):
            if name=='case-GH.json':raise OSError('NEUTRAL_INJECTED_WRITE_ERROR')
            return original(ledger,name,value,final)
        with patch.object(m.OutputLedger,'write',fail):self.assertEqual(self.produce(),'NOT_EVALUABLE')
        c=m.read(self.out/'closure.json');self.assertIn('NEUTRAL_INJECTED_WRITE_ERROR',c['error']);self.assertGreater(c['case_files'],0)
        with self.assertRaisesRegex(ValueError,'INCOMPLETE_MATERIAL'):m.read_verified(self.out,self.spec,'FC-NEUTRAL',self.plan['profile'])
        with self.assertRaises(FileExistsError):self.produce()
        FACTS['partial_failure']=c
    def test_G5_auth_binding_and_quantity_rejections(self):
        for field,value in [('status','PENDING'),('partition','FC-DEV'),('binding_sha256','0'*64)]:
            bad=dict(self.auth);bad[field]=value;save(self.ap,bad)
            with self.assertRaisesRegex(ValueError,'PRODUCTION_NOT_AUTHORIZED'):self.produce()
            self.assertFalse(self.out.exists())
        save(self.ap,self.auth)
        self.pp.write_text(self.pp.read_text()+' ')
        with self.assertRaisesRegex(ValueError,'PLAN_HASH'):self.produce()
        for mutation in ('frames','seed','cases'):
            bad=copy.deepcopy(self.spec)
            if mutation=='frames':bad['episodes']['A']['frames']=5
            elif mutation=='seed':bad['episodes']['A']['seed']=0
            else:bad['cases']['EXTRA']=copy.deepcopy(bad['cases']['F1'])
            with self.assertRaises(ValueError):m.synthesize(bad,'FC-NEUTRAL')
    def test_G6_export_tamper_detected(self):
        self.produce();p=self.out/'case-FH.json';row=m.read(p);row['values'][0][0]+=1.;save(p,row)
        with self.assertRaisesRegex(ValueError,'EXPORT_HASH'):m.read_verified(self.out,self.spec,'FC-NEUTRAL',self.plan['profile'])
    def test_G7_three_arm_export_connection(self):
        self.produce();r=evaluate_export(self.out,self.spec,'FC-NEUTRAL',self.plan['profile'])
        self.assertEqual(len(r['cases']),11);self.assertEqual(sum(len(c['learning_targets']) for c in r['cases'].values()),48)
        gp=r['cases']['GP']['rows'];self.assertIsNone(gp['legacy']['context_mae'])
        self.assertFalse(gp['legacy']['context_covered']);self.assertEqual(gp['legacy']['observer_hybrid_mae'],0.)
        self.assertEqual(gp['legacy']['persistence_mae'],0.);self.assertGreater(gp['scaled']['context_mae'],0.)
        self.assertEqual(r['cases']['ZF']['rows']['scaled']['prediction_status'],'ABSTAIN_AMBIGUOUS_FACTOR')
        self.assertEqual(r['cases']['AM']['rows']['scaled']['origin_category'],'AMBIGUOUS')
        self.assertIn('GP',[x['case_id'] for x in r['summary']['harms_against_persistence']])
        for key in ('legacy','scaled'):
            forecasts=[r['cases'][cid]['systems'][key]['targets'][-1]['forecast'] for cid in ('FH','GH','GR','GP')]
            self.assertTrue(all(f==forecasts[0] for f in forecasts))
        save(self.home/'neutral-comparison.json',r)
        FACTS['comparison']=dict(path=str((self.home/'neutral-comparison.json').relative_to(m.ROOT)),GP=gp,summary=r['summary'],semantics=r['semantics'])

if __name__=='__main__':unittest.main()
