"""Separate neutral qualification and observer-only Development evaluation.

Never invokes material production for development/evaluation. The production CLI
is invoked separately once after qualification. Neutral tests replace only plan
selection/validation and output root; synthesis/export/receptor/NJ stay original.
"""
import copy, hashlib, json, math, struct, sys
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch
from tools import s2uc_known_origin_material_plan as gen
from tools import _s2uc_bounded_audio as audio
from tools import _s2nj_private_auditory_output_projection as nj
from tools._s2uc_origin_judge import Truth, evaluate_case, judge, aggregate

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'reports/s2uc/known-origin-development-analysis-20260930-01'
NEUTRAL = ROOT/'reports/s2uc/known-origin-neutral-qualification-20260930-01'

def save(path, obj):
    with path.open('x', encoding='utf-8') as f:
        json.dump(obj, f, indent=2, allow_nan=False)

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_text(encoding='utf-8'))

def verify(folder, spec):
    closure = read(folder/'closure.json')
    assert closure == dict(status='MATERIAL_COMPLETE', error=None, windows=28,
                          calls=dict(receptor=28,nj=28), final_evaluation_run=False)
    assert len(list(folder.iterdir())) == 37
    pcm, vectors, facts = {}, {}, {}
    for key, entry in {**spec['episodes'], **spec['derivatives']}.items():
        row=read(folder/(key+'-pcm.json')); raw=bytes.fromhex(row['pcm_hex'])
        assert len(raw)==76800 and row['sha256']==hashlib.sha256(raw).hexdigest()
        assert row['sequence']==key and row['root']==entry['root']
        values=struct.unpack('<19200f',raw)
        assert all(math.isfinite(x) and abs(x)<=1 for x in values)
        pcm[key]=raw; vectors[key]=[]; times=[]
        for j in range(4):
            r=read(folder/f'{key}-{j+1}.json'); p=r['projection']
            start=entry.get('source_start_sample',0)+4800*j
            assert r['origin']==dict(index=j+1,start_sample=start,end_sample=start+4800)
            assert r['observer_root']==entry['root']
            assert p['profile_digest']==nj.PROFILE_DIGEST and p['source_profile_digest']==nj.RAW_PROFILE_DIGEST
            assert p['profile_id']==nj.PROFILE_ID
            assert (p['snapshot_index'],p['window_start_tick'],p['window_end_tick'])==(start//480,start,start+4800)
            nj.HalfScaleAuditory48V1(**{k:tuple(v) if isinstance(v,list) else v for k,v in p.items()})
            assert len(p['values'])==48 and all(math.isfinite(v) for v in p['values'])
            vectors[key].append(p['values']); times.append(r['origin'])
        facts[key]=dict(root=entry['root'],pcm_sha256=row['sha256'],source_times=times,
                        mean_abs_pcm=math.fsum(abs(x) for x in values)/len(values))
    assert pcm['D'][:38400]==pcm['A'][:38400] and pcm['D'][38400:]!=pcm['A'][38400:]
    assert vectors['D'][:2]==vectors['A'][:2]
    a=struct.unpack('<19200f',pcm['A'])
    assert pcm['A_half']==b''.join(struct.pack('<f',v*.5) for v in a)
    assert pcm['A_tailhalf']==b''.join(struct.pack('<f',v*.5 if 9600<=i<14400 else v) for i,v in enumerate(a))
    # Independent scalar implementation of the prebound noise recipe.
    x=spec['derivatives']['A_noise']['seed']; noise=bytearray()
    for v in a:
        x ^= (x<<13)&0xffffffff; x ^= x>>17; x ^= (x<<5)&0xffffffff; x &= 0xffffffff
        noise.extend(struct.pack('<f',v+(2**-12 if x%2 else -2**-12)))
    assert pcm['A_noise']==noise
    total=sum(p.stat().st_size for p in folder.iterdir())
    assert total<=audio.OutputLedger.LIMIT
    assert sum(len(v) for v in pcm.values())==537600
    return dict(status='PASS',sequences=facts,windows=28,pcm_bytes=537600,
                output_bytes=total,files={p.name:sha(p) for p in sorted(folder.iterdir())}), vectors

def qualify():
    p=read(gen.PLAN_PATH); gen.validate(p)
    NEUTRAL.mkdir(exist_ok=False)
    spec=copy.deepcopy(p['partitions']['development'])
    seeds=[510001,510007,510013,510019]
    freqs=[[260,620,940,1220],[380,860,1420,1660],[540,1180,1580,2020],[260,620,2180,2540]]
    for i,(key,e) in enumerate(spec['episodes'].items()):
        e.update(seed=seeds[i],frequencies_hz=freqs[i],root='qualification/'+key,
                 source_stream='qualification/'+('AC' if key in 'AC' else key))
    for d in spec['derivatives'].values(): d['root']='qualification/A'
    spec['derivatives']['A_noise']['seed']=510031
    spec['cases']={}
    neutral={**p,'partitions':{'qualification':spec},'status':'NEUTRAL_QUALIFICATION_ONLY'}
    save(NEUTRAL/'neutral-plan.json',neutral)
    auth=dict(status='AUTHORIZED_ONCE',action='PRODUCE_KNOWN_ORIGIN_PARTITION',partition='qualification',
              plan_sha256=sha(NEUTRAL/'neutral-plan.json'),generator_sha256=sha(Path(gen.__file__)),python=sys.version)
    save(NEUTRAL/'neutral-authorization.json',auth)
    def neutral_validate(value):
        assert value==neutral
        assert all(e['root'].startswith('qualification/') for e in value['partitions']['qualification']['episodes'].values())
        return True
    results=[]
    for mode in ['success','output-cap','projection-error']:
        root=NEUTRAL/mode; (root/'reports/s2uc').mkdir(parents=True)
        with ExitStack() as stack:
            stack.enter_context(patch.object(gen,'ROOT',root))
            stack.enter_context(patch.object(gen,'PLAN_PATH',NEUTRAL/'neutral-plan.json'))
            stack.enter_context(patch.object(gen,'validate',neutral_validate))
            if mode=='output-cap': stack.enter_context(patch.object(audio.OutputLedger,'LIMIT',audio.OutputLedger.RESERVE+1024))
            if mode=='projection-error': stack.enter_context(patch.object(audio,'project_window',side_effect=RuntimeError('NEUTRAL_INJECTED_PROJECTION_ERROR')))
            status=gen.produce(NEUTRAL/'neutral-authorization.json')
            folder=root/'reports/s2uc/known-origin-qualification-20260930-01'
            c=read(folder/'closure.json')
            if mode=='success':
                assert status=='MATERIAL_COMPLETE'; integrity,_=verify(folder,spec)
                save(NEUTRAL/'neutral-integrity.json',integrity)
            else:
                assert status=='NOT_EVALUABLE' and c['windows']==0
                assert c['error']==('OUTPUT_LIMIT' if mode=='output-cap' else 'NEUTRAL_INJECTED_PROJECTION_ERROR')
                assert sum(f.stat().st_size for f in folder.iterdir())<=audio.OutputLedger.LIMIT
            before={f.name:sha(f) for f in folder.iterdir()}
            try: gen.produce(NEUTRAL/'neutral-authorization.json')
            except FileExistsError: pass
            else: raise AssertionError('RETRY_NOT_REFUSED')
            assert before=={f.name:sha(f) for f in folder.iterdir()}
            results.append(dict(test_id=mode,status='PASS',closure=c,retry_refused=True))
    gen.validate(read(gen.PLAN_PATH))
    assert not (ROOT/'reports/s2uc/known-origin-development-20260930-01').exists()
    assert not (ROOT/'reports/s2uc/known-origin-evaluation-20260930-01').exists()
    save(NEUTRAL/'tests.json',dict(status='PASS',tests=results,neutral_seam='ROOT, PLAN_PATH, exact neutral validator only; production implementation unchanged',
        plan_sha256=sha(gen.PLAN_PATH),generator_sha256=sha(Path(gen.__file__)),neutral_seeds=seeds+[510031],
        original_plan_validation=True,families_unproduced=True))
    print('NEUTRAL_QUALIFICATION_PASS')

def evaluate():
    assert read(NEUTRAL/'tests.json')['status']=='PASS'
    p=read(gen.PLAN_PATH); gen.validate(p); spec=p['partitions']['development']
    integrity,vectors=verify(ROOT/'reports/s2uc/known-origin-development-20260930-01',spec)
    OUT.mkdir(exist_ok=False); save(OUT/'integrity.json',integrity)
    results={}; learning=[]
    for cid in ['T0','P1','P2','P3','N1','N2','N3','N4']:
        case=spec['cases'][cid]; values=[]; origins={}; roots=[]
        for key in case['learn']:
            n=len(values); origins[tuple(range(n+1,n+5))]=spec['episodes'][key]['root']
            values.extend(vectors[key]); roots.extend([spec['episodes'][key]['root']]*4)
        values.extend(vectors[case['query']][:3]); roots.extend([case['truth']]*3)
        result=evaluate_case(values,nj.PROFILE_DIGEST,len(values),len(values),Truth(case['truth'],case['positive'],origins,cid),measure_resources=True)
        save(OUT/(cid+'.json'),result); results[cid]=result
        for target in result['system']['targets'][:-1]:
            root=roots[target['target']-1]
            available={indices:r for indices,r in origins.items() if indices[-1]<=target['target']-3}
            learning.append(judge(target,Truth(root,root in available.values(),available,cid)))
        print(cid,result['evaluation']['origin_category'],flush=True)
    assert len(learning)==36
    assert results['T0']['system']['targets'][-1]['forecast']==results['N3']['system']['targets'][-1]['forecast']
    assert results['T0']['system']['states'][:10]==results['N3']['system']['states'][:10]
    rows=[r['evaluation'] for r in results.values()]
    summary=dict(status='COMPLETE',test_targets=aggregate(rows),test_rows=rows,
                 learning_targets=aggregate(learning),learning_rows=learning,
                 learning_definition='All other reachable targets, including the pair crossing learning/query boundary; positive means root available in a completed prior four-frame block.',
                 T0_N3_forecasts_and_pre_future_states_identical=True,
                 total_frames=sum(len(r['system']['admitted']) for r in results.values()),
                 evaluation_unproduced=not (ROOT/'reports/s2uc/known-origin-evaluation-20260930-01').exists(),
                 evaluation_authorization=read(ROOT/'docs/S2UC_HERKUNFT_EVALUATION_VORLAGE_20260930.json')['status'])
    assert summary['total_frames']==96 and summary['evaluation_unproduced'] and summary['evaluation_authorization']=='PENDING'
    gen.validate(read(gen.PLAN_PATH)); save(OUT/'result.json',summary)
    save(OUT/'bindings.json',dict(plan_sha256=sha(gen.PLAN_PATH),generator_sha256=sha(Path(gen.__file__)),
        observer_sha256=sha(Path(__file__)),implementation_bindings=p['implementation_bindings'],
        judge_sha256=sha(ROOT/'tools/_s2uc_origin_judge.py'),python=sys.version,
        profiles=dict(nj=nj.PROFILE_DIGEST,raw=nj.RAW_PROFILE_DIGEST)))
    print(json.dumps(summary['test_targets'],indent=2))

if __name__=='__main__':
    if sys.argv[1:]==['qualify']: qualify()
    elif sys.argv[1:]==['evaluate']: evaluate()
    else: raise SystemExit('qualify | evaluate (never produces Development)')
