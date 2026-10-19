import copy
import json
import math
import shutil
import struct
import unittest
from pathlib import Path
from unittest.mock import patch
from tools import s2uc_an_material as m
from tools import s2uc_an_compare as observer

REPORT=None
FACTS={}


def save(path,value):
    path.write_text(json.dumps(value,indent=2,allow_nan=False),encoding='utf-8')


def neutral(out,evaluation=False):
    part='NEUTRAL-EVAL' if evaluation else 'NEUTRAL-DEV'
    seeds=[1410001,1410007,1410013,1410019,1410031,1410037,1410043]
    if evaluation:seeds=[s+100000 for s in seeds[:6]]
    frequencies=[[370,610,850,1210],[510,950,730,1590],[690,1090,1450,910],[370,610,1810,2090]]
    return m.spec_for(part,seeds,frequencies,str(out.relative_to(m.ROOT)).replace('\\','/'),evaluation=evaluation)


class ANMaterialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if REPORT is None:raise RuntimeError('Use tools.s2uc_an_qualify for exclusive evidence directory')
        cls.out=REPORT/'neutral-dev';cls.spec=neutral(cls.out);cls.part='NEUTRAL-DEV'
        save(REPORT/'neutral-spec.json',cls.spec)
        cls.used=[];old_draw=m.draws
        from tools import s2uc_known_origin_material_plan as generator
        old_generate_draw=generator.draws
        def traced(seed):cls.used.append(seed);return old_draw(seed)
        def generator_traced(seed):cls.used.append(seed);return old_generate_draw(seed)
        with patch.object(m,'draws',side_effect=traced),patch.object(generator,'draws',side_effect=generator_traced):
            status=m.materialize(cls.spec,cls.part,cls.out,dict(status='NEUTRAL_QUALIFICATION_ONLY'))
        if status!='MATERIAL_COMPLETE':raise AssertionError(m.read(cls.out/'closure.json'))
        cls.rows,cls.calibration=m.read_verified(cls.out,cls.spec,cls.part)

    def test_AN1_full_57_projection_budget_and_reserved_seed_exclusion(self):
        c=m.read(self.out/'closure.json');size=sum(f.stat().st_size for f in self.out.iterdir())
        self.assertEqual(c['calls'],dict(receptor=57,nj=57));self.assertLessEqual(size,4194304)
        self.assertEqual(sum(len(bytes.fromhex(m.read(f)['pcm_hex'])) for f in self.out.glob('*-pcm.json')),1094400)
        self.assertTrue(m.RESERVED.isdisjoint(self.used));self.assertEqual(len(set(self.used)),7)
        self.assertEqual(sum(len(r['values']) for r in self.rows.values()),129)
        FACTS['full_dev']=dict(calls=c['calls'],bytes=size,limit=4194304,files=len(list(self.out.iterdir())),
            raw_pcm_bytes=1094400,seeds_used=sorted(set(self.used)),reserved_seeds_used=False)

    def test_AN2_independent_pcm_arithmetic_and_lineage(self):
        def data(k):return bytes.fromhex(m.read(self.out/(k+'-pcm.json'))['pcm_hex'])
        a=struct.unpack('<19200f',data('A'));b=struct.unpack('<19200f',data('B'))
        x=self.spec['noise_R']['seed'];noise=[]
        for _ in range(9600):
            x^=(x<<13)&0xffffffff;x^=x>>17;x^=(x<<5)&0xffffffff;x&=0xffffffff
            noise.append(2**-12 if x&1 else -2**-12)
        pack=lambda xs:b''.join(struct.pack('<f',v) for v in xs)
        self.assertEqual(data('R1')[:38400],pack(a[i]+noise[i] for i in range(9600)))
        self.assertEqual(data('R2')[:38400],pack(a[i]+2*noise[i] for i in range(9600)))
        self.assertEqual(data('R1')[38400:],data('A')[38400:57600])
        self.assertEqual(data('R3')[:38400],data('R1')[:38400])
        self.assertEqual(data('R3')[38400:],data('R1')[19200:38400])
        self.assertEqual(data('D')[:38400],data('A')[:38400])
        self.assertEqual(data('N4'),pack((a[i]+b[i])/2 for i in range(14400)))
        self.assertEqual(data('P0'),pack(a[i]*2**-12 for i in range(14400)))
        self.assertEqual(data('Z0'),bytes(57600))
        self.assertEqual(self.rows['N4']['truth'],self.part+'/M')
        source=m.read(self.out/'N2-pcm.json')['lineage']['ancestors'][0]
        self.assertEqual(source['source_windows'][0]['start_sample'],19200)
        self.assertEqual(source['pcm_sha256'],m.digest_bytes(data('C')))
        FACTS['pcm_derivations']='independent binary32 bit checks: R1/R2/R3,D-prefix,N4,P0,Z0,source ancestry PASS'

    def test_AN3_real_projection_digest_and_retiming(self):
        calls=dict(receptor=0,nj=0)
        # Independent replay of three representative PCM windows; separate from 57-window production.
        for key,j in [('N4',0),('P0',1),('R3',2)]:
            data=bytes.fromhex(m.read(self.out/(key+'-pcm.json'))['pcm_hex'])
            row=m.read(self.out/(key+f'-{j}.json'))
            actual=m.project_window(data[j*19200:(j+1)*19200],row['origin'],calls)
            self.assertEqual(m.canonical(actual),m.canonical(row['projection']))
        for cid in m.IDS:
            for j in range(3):
                p=m.read(self.out/(cid+f'-{j}.json'))['projection']
                self.assertEqual((p['snapshot_index'],p['window_start_tick'],p['window_end_tick']),(j*10,j*4800,(j+1)*4800))
        c=m.read(self.out/'C-0.json')['projection'];n=m.read(self.out/'N2-0.json')['projection']
        self.assertEqual(c['values'],n['values']);self.assertNotEqual(c['projection_digest'],n['projection_digest'])
        self.assertEqual(c['window_start_tick'],19200)
        r1=m.read(self.out/'R1-1.json')['projection'];r3=m.read(self.out/'R3-2.json')['projection']
        self.assertEqual(r1['values'],r3['values']);self.assertNotEqual(r1['projection_digest'],r3['projection_digest'])
        for j in range(2):self.assertEqual(m.read(self.out/f'R1-{j}.json')['projection'],m.read(self.out/f'R3-{j}.json')['projection'])
        mix=self.rows['N4']['values'][-3]
        mean=[(x+y)/2 for x,y in zip(m.read(self.out/'A-0.json')['projection']['values'],m.read(self.out/'B-0.json')['projection']['values'])]
        self.assertNotEqual(mix,mean)
        FACTS['projection_checks']=dict(independent_reprojection_calls=calls,retimed_digest_checks=True,mix_not_nj_average=True)

    def test_AN4_calibration_and_evaluation_exclusion(self):
        epsilon=observer.calibration_epsilon(self.out,self.spec,self.part)
        means=[math.fsum(abs(x) for x in v)/48 for v in self.calibration]
        self.assertEqual(epsilon,max(means));self.assertNotEqual(epsilon,2**-10)
        out=REPORT/'neutral-eval';spec=neutral(out,True);seen=[];old=m.draws
        def traced(seed):seen.append(seed);return old(seed)
        with patch.object(m,'draws',side_effect=traced):
            self.assertEqual(m.materialize(spec,'NEUTRAL-EVAL',out,dict(status='NEUTRAL_ONLY')),'MATERIAL_COMPLETE')
        self.assertEqual(m.read_verified(out,spec,'NEUTRAL-EVAL')[1],[])
        self.assertEqual(m.read(out/'closure.json')['calls'],dict(receptor=49,nj=49))
        self.assertEqual(set(seen),{spec['noise_R']['seed'],spec['noise_Z']['seed']})
        with patch.object(observer,'read_verified',side_effect=AssertionError('must reject before reading')):
            with self.assertRaisesRegex(ValueError,'EVAL_CALIBRATION_FORBIDDEN'):observer.calibration_epsilon(out,spec,'NEUTRAL-EVAL')
        bad=copy.deepcopy(spec);bad['calibration']=self.spec['calibration']
        with self.assertRaisesRegex(ValueError,'EVAL_CALIBRATION_FORBIDDEN'):m.validate(bad,'NEUTRAL-EVAL')
        with patch.object(observer,'read_verified',return_value=({},[[0.]*48]*8)):
            with self.assertRaisesRegex(ValueError,'CALIBRATION_NOT_NORMAL_POSITIVE'):observer.calibration_epsilon(self.out,self.spec,self.part)
        FACTS['calibration']=dict(neutral_only=True,epsilon=epsilon,eight_nj_means=means,
            evaluation_calibration_rejected_before_read=True,eval_windows=49)

    def test_AN5_success_failure_limit_and_one_shot(self):
        before={p.name:m.sha(p) for p in self.out.iterdir()}
        with patch.object(m,'synthesize_partition',side_effect=AssertionError('generator must not run')):
            with self.assertRaises(FileExistsError):m.materialize(self.spec,self.part,self.out,{})
        self.assertEqual(before,{p.name:m.sha(p) for p in self.out.iterdir()})
        out=REPORT/'budget-failure';spec=neutral(out)
        with patch.object(m.OutputLedger,'LIMIT',m.OutputLedger.RESERVE+1024):
            self.assertEqual(m.materialize(spec,self.part,out,{}),'NOT_EVALUABLE')
            self.assertLessEqual(sum(p.stat().st_size for p in out.iterdir()),m.OutputLedger.LIMIT)
        cap=m.read(out/'closure.json');self.assertIn('OUTPUT_LIMIT',cap['error'])
        with self.assertRaises(FileExistsError):m.materialize(spec,self.part,out,{})
        out=REPORT/'projection-failure';spec=neutral(out);original=m.project_window
        def failing(payload,origin,calls):
            if calls['receptor']==5:raise OSError('NEUTRAL_PROJECTION_FAILURE')
            return original(payload,origin,calls)
        with patch.object(m,'project_window',side_effect=failing):self.assertEqual(m.materialize(spec,self.part,out,{}),'NOT_EVALUABLE')
        failure=m.read(out/'closure.json');self.assertEqual(failure['calls']['receptor'],5)
        with self.assertRaisesRegex(ValueError,'INCOMPLETE_MATERIAL'):m.read_verified(out,spec,self.part)
        with self.assertRaises(FileExistsError):m.materialize(spec,self.part,out,{})
        for value in (float('nan'),float('inf'),1.1,-1.1):
            with self.assertRaisesRegex(ValueError,'PCM_DOMAIN'):m.pcm([value])
        ledger=m.OutputLedger(REPORT/'exclusive-file');ledger.write('one.json',{})
        with self.assertRaises(FileExistsError):ledger.write('one.json',{})
        ledger.write('closure.json',{},final=True)
        with self.assertRaisesRegex(ValueError,'OUTPUT_FINALIZED'):ledger.write('later.json',{})
        FACTS['failure_closures']=dict(budget=cap,projection=failure,repetition_rejected=True)

    def test_AN6_integrity_tamper_rejection(self):
        out=REPORT/'tamper';shutil.copytree(self.out,out)
        path=out/'R1-0.json';row=m.read(path);row['projection']['values'][0]+=.01;save(path,row)
        with self.assertRaisesRegex(ValueError,'EXPORT_HASH'):m.read_verified(out,self.spec,self.part)
        manifest=m.read(out/'manifest.json');manifest['files'][path.name]=m.sha(path);save(out/'manifest.json',manifest)
        with self.assertRaisesRegex(ValueError,'PROJECTION_DIGEST_INVALID'):m.read_verified(out,self.spec,self.part)
        shutil.copyfile(self.out/path.name,path)
        path=out/'N4-pcm.json';row=m.read(path);data=bytearray.fromhex(row['pcm_hex']);data[0]^=1
        row['pcm_hex']=data.hex();row['pcm_sha256']=m.digest_bytes(data);save(path,row)
        manifest=m.read(out/'manifest.json');manifest['files']['R1-0.json']=m.sha(out/'R1-0.json');manifest['files'][path.name]=m.sha(path);save(out/'manifest.json',manifest)
        with self.assertRaisesRegex(ValueError,'PROJECTION_PCM_BINDING'):m.read_verified(out,self.spec,self.part)
        FACTS['integrity']='file hash, NJ digest and PCM-to-projection association tampering rejected'

    def test_AN7_comparison_origins_causality_learning_and_harm(self):
        epsilon=observer.calibration_epsilon(self.out,self.spec,self.part)
        # One predeclared neutral setting, not a parameter search.
        result=observer.evaluate_export(self.out,self.spec,self.part,epsilon=epsilon,tau=1/32,measure=True)
        cases=result['cases'];self.assertEqual(len(cases),11)
        self.assertEqual(sum(len(c['learning_targets']) for c in cases.values()),48)
        self.assertEqual(result['continuation_policy_for_both'],'legacy_v1');self.assertFalse(result['factor_scaled_v1_used'])
        exact='exact_retrieval';approx='signal_approx_retrieval'
        self.assertEqual(cases['R0']['rows'][exact]['origin_category'],'CORRECT')
        self.assertEqual(cases['N3']['rows'][exact]['origin_category'],'WRONG')
        self.assertEqual(cases['N3']['rows'][exact]['true_root'],self.part+'/D')
        self.assertEqual(cases['N3']['rows'][exact]['assigned_root'],self.part+'/A')
        for left,right in [('R1','R3'),('R0','N3')]:
            for arm in (exact,approx):
                self.assertEqual(cases[left]['systems'][arm]['targets'][-1]['forecast'],cases[right]['systems'][arm]['targets'][-1]['forecast'])
        resources=[]
        for c in cases.values():
            self.assertNotIn(c['target'],c['learning_targets'])
            for system in c['systems'].values():
                self.assertEqual(system['admitted'],list(range(1,c['target']+1)));self.assertTrue(system['slots_released'])
                resources.append(system['resources'])
        self.assertEqual(cases['R3']['rows'][approx]['persistence_mae'],0.)
        self.assertGreater(cases['R3']['rows'][approx]['observer_hybrid_mae'],0.)
        harms=result['summary']['comparison']['harms_against_persistence']
        self.assertIn('R3',[r['case_id'] for r in harms])
        save(REPORT/'neutral-comparison.json',result)
        FACTS['comparison']=dict(epsilon=epsilon,tau=1/32,parameter_search=False,primary=11,learning=48,
            summary=result['summary'],resources=resources)

    def test_AN8_binding_pending_authorization_and_selector_reuse(self):
        b,p=m.load_binding();self.assertEqual(p,m.plan())
        template=m.ROOT/'docs/S2UC_AN_DEV_AUTORISIERUNG_VORLAGE_20261001.json'
        with self.assertRaisesRegex(ValueError,'PRODUCTION_NOT_AUTHORIZED'):m.produce(template)
        self.assertTrue(all(not (m.ROOT/s['output_directory']).exists() for s in p['partitions'].values()))
        from tools import s2uc_ar_compare
        self.assertIs(observer.select_parameters,s2uc_ar_compare.select_parameters)
        outcomes=[dict(tau=t,rows={cid:dict(exact_retrieval='ABSTAIN',signal_approx_retrieval='ABSTAIN') for cid in m.IDS}) for t in observer.GRID]
        self.assertIsNone(observer.select_parameters(outcomes)['selected_tau'])
        outcomes[2]['rows']['R1']['signal_approx_retrieval']='CORRECT'
        outcomes[3]['rows']['R1']['signal_approx_retrieval']='CORRECT'
        self.assertEqual(observer.select_parameters(outcomes)['selected_tau'],observer.GRID[2])
        outcomes[2]['rows']['N1']['signal_approx_retrieval']='WRONG'
        self.assertEqual(observer.select_parameters(outcomes)['selected_tau'],observer.GRID[3])
        FACTS['binding']=dict(plan_sha256=m.sha(m.PLAN),binding_sha256=m.sha(m.BINDING),
            pending_rejected=True,an_partitions_unproduced=True,selector_unchanged=True)

    def test_AN9_no_partition_relabel_or_manual_dev_epsilon(self):
        bad=copy.deepcopy(self.spec);bad['partition']='NEUTRAL-EVAL'
        with self.assertRaisesRegex(ValueError,'PARTITION_KIND_MISMATCH'):m.validate(bad,'NEUTRAL-EVAL')
        with patch.object(observer,'compare',side_effect=AssertionError('no replay before calibration check')):
            with self.assertRaisesRegex(ValueError,'DEV_EPSILON_MUST_MATCH_NJ_CALIBRATION'):
                observer.evaluate_export(self.out,self.spec,self.part,epsilon=2**-10,tau=1/32)
        FACTS['calibration_guard']='evaluation-as-development relabel and manual synthetic DEV epsilon rejected before replay'
