import copy,json,math,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from tools import s2uc_ar_material as m
from tools import s2uc_ar_compare as observer
REPORT=m.ROOT/'reports/s2uc/ar-material-qualification-20261001-01'
FACTS={}
def save(path,v):path.write_text(json.dumps(v,indent=2,allow_nan=False),encoding='utf-8')

class ARMaterialTests(unittest.TestCase):
    def setUp(self):
        self.home=Path(tempfile.mkdtemp(prefix=self._testMethodName+'-',dir=REPORT));self.configure('first')
    def configure(self,tag,evaluation=False):
        self.part='NEUTRAL-EVAL' if evaluation else 'NEUTRAL-DEV'
        self.plan=copy.deepcopy(m.read(m.PLAN));self.spec=copy.deepcopy(self.plan['partitions']['AR-EVAL' if evaluation else 'AR-DEV'])
        for k,seed in zip('ABCD',[1110001,1110007,1110013,1110019]):
            e=self.spec['episodes'][k];e['seed']=seed;e['root']=self.part+'/'+k;e['source_stream']=self.part+('/AC' if k in 'AC' else '/'+k)
        for key,seed in [('noise_R',1110031),('calibration',1110037),('noise_Z',1110043)]:self.spec[key]['seed']=seed
        for c in self.spec['cases'].values():c['truth']=self.part+'/'+c['truth'].split('/')[-1]
        self.out=self.home/(tag+'-material');self.spec['output_directory']=str(self.out.relative_to(m.ROOT)).replace('\\','/')
        self.plan['partitions']={self.part:self.spec}
        self.pp=self.home/(tag+'-plan.json');save(self.pp,self.plan)
        self.b=m.read(m.BINDING);self.b.update(plan_path=str(self.pp.relative_to(m.ROOT)).replace('\\','/'),plan_sha256=m.sha(self.pp))
        self.bp=self.home/(tag+'-binding.json');save(self.bp,self.b)
        self.auth=dict(status='AUTHORIZED_ONCE',action='PRODUCE_AR_PARTITION',partition=self.part,binding_sha256=m.sha(self.bp),plan_sha256=m.sha(self.pp),python=sys.version)
        self.ap=self.home/(tag+'-authorization.json');save(self.ap,self.auth)
    def produce(self):return m.produce(self.ap,binding_path=self.bp)
    def read(self):return m.read_verified(self.out,self.spec,self.part,self.plan['profile'])

    def test_M1_values_derivations_profiles_roundtrip_reproducibility(self):
        self.assertEqual(self.produce(),'MATERIAL_COMPLETE');rows,aux=self.read();expected={}
        for k,e in self.spec['episodes'].items():
            x=e['seed'];flat=[]
            for _ in range(192):
                x^=(x<<13)&0xffffffff;x^=x>>17;x^=(x<<5)&0xffffffff;x&=0xffffffff
                flat.append((257+x%768)/4096.)
            expected[k]=[flat[i:i+48] for i in range(0,192,48)]
        expected['D'][:2]=copy.deepcopy(expected['A'][:2])
        for k,v in expected.items():self.assertEqual(m.vector_hash(v),m.read(self.out/('source-'+k+'.json'))['values_sha256'])
        for key in ('noise_R','noise_Z','calibration'):
            x=self.spec[key]['seed'];v=[]
            for _ in range(self.spec[key]['frames']*48):
                x^=(x<<13)&0xffffffff;x^=x>>17;x^=(x<<5)&0xffffffff;x&=0xffffffff
                v.append(2**-10 if x&1 else -2**-10)
            self.assertEqual(sum(aux[key],[]),v)
        self.assertEqual(rows['R1']['values'][-3:-1],rows['R3']['values'][-3:-1])
        for j in range(2):
            self.assertEqual(rows['R2']['values'][-3+j],[a+2*n for a,n in zip(expected['A'][j],aux['noise_R'][j])])
        self.assertEqual(rows['P0']['values'][-1],[math.ldexp(x,-12) for x in expected['A'][2]])
        self.assertEqual(rows['N4']['values'][-1],[(a+b)/2 for a,b in zip(expected['A'][2],expected['B'][2])])
        self.assertEqual(rows['N4']['truth'],self.part+'/M')
        self.assertEqual(rows['N2']['truth'],self.part+'/C')
        self.assertEqual(observer.recipe_epsilon(aux['calibration']),2**-10)
        self.assertEqual(sum(len(r['values']) for r in rows.values()),129)
        first={k:m.read(self.out/('source-'+k+'.json'))['values_sha256'] for k in ['A','B','C','D','noise_R','noise_Z','calibration']}
        FACTS['full_path']=dict(folder=str(self.out.relative_to(m.ROOT)),files=len(list(self.out.iterdir())),bytes=sum(p.stat().st_size for p in self.out.iterdir()),calibration_mean_absolute=2**-10,interpretation='recipe identity; not estimated noise floor')
        self.configure('repeat');self.assertEqual(self.produce(),'MATERIAL_COMPLETE')
        self.assertEqual(first,{k:m.read(self.out/('source-'+k+'.json'))['values_sha256'] for k in first})

    def test_M2_evaluation_calibration_seed_unused(self):
        self.configure('eval',evaluation=True);used=[];draw=m.draws
        def traced(seed):used.append(seed);return draw(seed)
        with patch.object(m,'draws',side_effect=traced):self.assertEqual(self.produce(),'MATERIAL_COMPLETE')
        self.assertNotIn(self.spec['calibration']['seed'],used)
        self.assertEqual(self.read()[1]['calibration'],[])
        with self.assertRaisesRegex(ValueError,'CALIBRATION_RECIPE'):observer.recipe_epsilon([])
        FACTS['neutral_eval_seed_not_used']=True

    def test_M3_one_shot_and_no_overwrite(self):
        self.produce();before={p.name:m.sha(p) for p in self.out.iterdir()}
        with self.assertRaises(FileExistsError):self.produce()
        self.assertEqual(before,{p.name:m.sha(p) for p in self.out.iterdir()})
        ledger=m.OutputLedger(self.home/'ledger');ledger.write('a.json',{'v':1})
        with self.assertRaises(FileExistsError):ledger.write('a.json',{'v':2})
        self.assertEqual(m.read(self.home/'ledger/a.json'),{'v':1})

    def test_M4_limits_and_failure_closure(self):
        with patch.object(m.OutputLedger,'LIMIT',m.OutputLedger.RESERVE+1024):
            self.assertEqual(self.produce(),'NOT_EVALUABLE');c=m.read(self.out/'closure.json')
            self.assertIn('OUTPUT_LIMIT',c['error']);self.assertLessEqual(sum(f.stat().st_size for f in self.out.iterdir()),m.OutputLedger.LIMIT)
        FACTS['output_cap']=c
        with self.assertRaises(FileExistsError):self.produce()
        self.configure('fault');write=m.OutputLedger.write
        def failing(ledger,name,value,final=False):
            if name=='case-R3.json':raise OSError('NEUTRAL_EXPORT_FAILURE')
            return write(ledger,name,value,final)
        with patch.object(m.OutputLedger,'write',failing):self.assertEqual(self.produce(),'NOT_EVALUABLE')
        c=m.read(self.out/'closure.json');self.assertGreater(c['case_files'],0);FACTS['partial_failure']=c
        with self.assertRaisesRegex(ValueError,'INCOMPLETE_MATERIAL'):self.read()
        with self.assertRaises(FileExistsError):self.produce()

    def test_M5_authorization_shape_and_tampering(self):
        self.auth['status']='PENDING';save(self.ap,self.auth)
        with self.assertRaisesRegex(ValueError,'PRODUCTION_NOT_AUTHORIZED'):self.produce()
        self.assertFalse(self.out.exists())
        self.auth['status']='AUTHORIZED_ONCE';save(self.ap,self.auth);self.produce()
        path=self.out/'case-R1.json';row=m.read(path);row['values'][-3][0]+=1;save(path,row)
        with self.assertRaisesRegex(ValueError,'EXPORT_HASH'):self.read()
        row['values_sha256']=m.vector_hash(row['values']);save(path,row)
        manifest=m.read(self.out/'manifest.json');manifest['files'][path.name]=m.sha(path);save(self.out/'manifest.json',manifest)
        with self.assertRaisesRegex(ValueError,'CASE_DERIVATION'):self.read()
        bad=copy.deepcopy(self.spec);bad['noise_R']['frames']=3
        with self.assertRaises(ValueError):m.validate(bad,self.part)
        bad=copy.deepcopy(self.spec);bad['calibration']['frames']=9
        with self.assertRaises(ValueError):m.validate(bad,self.part)

    def test_M6_export_observer_clear_labels(self):
        self.produce();result=observer.evaluate_export(self.out,self.spec,self.part,self.plan['profile'],epsilon=2**-10,tau=1/32)
        self.assertEqual(len(result['cases']),11);self.assertEqual(sum(len(c['learning_targets']) for c in result['cases'].values()),48)
        self.assertEqual(result['continuation_policy_for_both'],'legacy_v1');self.assertFalse(result['factor_scaled_v1_used'])
        def check(obj):
            if isinstance(obj,dict):
                self.assertNotIn('legacy',obj);self.assertNotIn('scaled',obj)
                for v in obj.values():check(v)
            elif isinstance(obj,list):
                for v in obj:check(v)
        check(result)
        self.assertIsNone(result['cases']['R3']['rows']['exact_retrieval']['context_mae'])
        self.assertEqual(result['cases']['R3']['rows']['exact_retrieval']['observer_hybrid_mae'],0.)
        save(self.home/'comparison.json',result)
        FACTS['comparison']=dict(path=str((self.home/'comparison.json').relative_to(m.ROOT)),labels=result['labels'],summary=result['summary'])

    def test_M7_seven_grid_selection_neutral_outcomes(self):
        def outcomes():return [dict(tau=t,rows={cid:dict(exact_retrieval='ABSTAIN',signal_approx_retrieval='ABSTAIN') for cid in m.IDS}) for t in observer.GRID]
        r=outcomes();a=observer.select_parameters(r);self.assertIsNone(a['selected_tau']);self.assertFalse(a['evaluation_selection_allowed'])
        for i in (2,3):
            for cid in ('R1','R2'):r[i]['rows'][cid]['signal_approx_retrieval']='CORRECT'
        # Larger tau has a new wrong origin despite same positive gain: reject.
        r[3]['rows']['N1']['signal_approx_retrieval']='WRONG'
        self.assertEqual(observer.select_parameters(r)['selected_tau'],observer.GRID[2])
        r[3]['rows']['N1']['signal_approx_retrieval']='ABSTAIN'
        self.assertEqual(observer.select_parameters(r)['selected_tau'],observer.GRID[2])
        # Many other correct cases cannot improve the R1/R2-only objective.
        for cid in ('R0','N1','N2','N4','P0'):r[1]['rows'][cid]['signal_approx_retrieval']='CORRECT'
        self.assertEqual(observer.select_parameters(r)['selected_tau'],observer.GRID[2])
        for record in r:
            record['rows']['N3']['exact_retrieval']='WRONG'
            record['rows']['N3']['signal_approx_retrieval']='WRONG'
        self.assertEqual(observer.select_parameters(r)['selected_tau'],observer.GRID[2])
        r[2]['rows']['N3']['signal_approx_retrieval']='ABSTAIN';r[2]['rows']['Z1']['signal_approx_retrieval']='WRONG'
        self.assertEqual(observer.select_parameters(r)['selected_tau'],observer.GRID[3])
        for record in r:record['rows']['N1']['signal_approx_retrieval']='WRONG'
        self.assertEqual(observer.select_parameters(r)['status'],'NO_ELIGIBLE_PARAMETER')
        with self.assertRaises(ValueError):observer.select_parameters(r[:-1])
        r=outcomes();r[1]['tau']=r[0]['tau']
        with self.assertRaises(ValueError):observer.select_parameters(r)
        r=outcomes();r[1]['rows']['R0']['exact_retrieval']='CORRECT'
        with self.assertRaisesRegex(ValueError,'REFERENCE_CHANGED'):observer.select_parameters(r)
        FACTS['selection_test']='seven-grid/no-new-wrong/R1-R2-only/tie-minimum/no-gain/ref-consistency PASS; hand-authored outcomes only'

if __name__=='__main__':unittest.main()
