"""Sealed material recipe. Import/plan/validate never synthesize PCM."""
import json,hashlib,math,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
VERSION='s2uc.known-origin.material.v1'
PLAN_PATH=ROOT/'docs/S2UC_HERKUNFT_MATERIALPLAN_20260930.json'
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def plan():
    partitions={}
    for name,seeds,frequencies in [
        ('development',[104729,130363,155921,181081,205019],[[310,530,790,1130],[430,890,670,1490],[590,1010,1370,830],[310,530,1730,1970]]),
        ('evaluation',[324161,350377,376127,402581,428759],[[470,710,1090,1570],[610,1270,910,1810],[730,1430,1910,1030],[470,710,2110,2330]])]:
        episodes={letter:dict(seed=seeds[i],frequencies_hz=frequencies[i],root=name+'/'+letter,copy_prefix_from='A' if letter=='D' else None,source_stream=name+'/AC' if letter in ('A','C') else name+'/'+letter,source_start_sample=19200 if letter=='C' else 0) for i,letter in enumerate('ABCD')}
        partitions[name]=dict(episodes=episodes,derivatives={'A_half':dict(root=name+'/A',base='A',operation='gain_all',gain=.5),'A_noise':dict(root=name+'/A',base='A',operation='noise',amplitude=2**-12,seed=seeds[4]),'A_tailhalf':dict(root=name+'/A',base='A',operation='gain_window_3',gain=.5)},cases={
            'T0':dict(learn=['A','A'],query='A',truth=name+'/A',positive=True),
            'P1':dict(learn=['A','A'],query='A_half',truth=name+'/A',positive=True),
            'P2':dict(learn=['A','A'],query='A_noise',truth=name+'/A',positive=True),
            'P3':dict(learn=['A','A'],query='A_tailhalf',truth=name+'/A',positive=True),
            'N1':dict(learn=['A','A'],query='B',truth=name+'/B',positive=False),
            'N2':dict(learn=['A','A'],query='C',truth=name+'/C',positive=False),
            'N3':dict(learn=['A','A'],query='D',truth=name+'/D',positive=False),
            'N4':dict(learn=['A','A','D','D'],query='D',truth=name+'/D',positive=True,expected_identifiability='AMBIGUOUS')})
    bindings={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['tools/_s2uc_bounded_audio.py','tools/_s2nj_private_auditory_output_projection.py','mcm_field_organism/log_spectral_receptor.py','mcm_field_organism/broadband_hearing_path.py']}
    return dict(implementation_bindings=bindings,python_runtime=sys.version,python_executable_sha256=hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),version=VERSION,status='PLAN_ONLY',sample_rate=48000,samples_per_episode=19200,window=4800,external_hop=4800,profile='s2nj.auditory.hann48.output-half.v1',partitions=partitions,
        bounds=dict(partitions_per_call=1,sequences_per_partition=7,pcm_bytes_per_partition=537600,pcm_hex_bytes_per_partition=1075200,windows_per_partition=28,max_outputs_bytes_per_partition=4194304,closure_reserve_bytes=262144),
        recipe=dict(prng='xorshift32: x^=(x<<13)&0xffffffff; x^=x>>17; x^=(x<<5)&0xffffffff; mask32 each step; initial nonzero seed',
        base='two phase draws u=x/2**32; phase=2*pi*u; each window frequency f[k], continuous accumulated cycles; y=(sin(2*pi*cycles+phase1)+sin(2*pi*1.5*cycles+phase2))/16; quantize once float32-le',
        shared_prefix='D first9600 samples copied bit-for-bit from same-partition A; D tail from own seeded recipe',
        variants='transform stored float32 A samples in binary64 then round float32 once; noise draws +/-2**-12 by low PRNG bit; never clip; reject nonfinite/outside[-1,1]',
        timing='A then C are distinct scripted episodes in joint AC source timeline; C starts19200; B and D independent scripted episodes; D has explicitly shared prefix ancestry',
        comparison='learn complete4-frame sequences as listed; query first3 frames; evaluate target11 except N4 target19; all other reachable targets learning-only; cold start each case; paired phase from1'),
        qualification='Synthetic controlled identity only; different seeds/recipes do not prove general independence; no natural-world or held-out success claim from known regression material')
def validate(p):
    assert p==plan(),'PLAN_CHANGED'
    assert set(p['partitions'])=={'development','evaluation'}
    seeds=[]
    for name,q in p['partitions'].items():
        assert len(q['episodes'])+len(q['derivatives'])==7 and set(q['cases'])=={'T0','P1','P2','P3','N1','N2','N3','N4'}
        for e in q['episodes'].values():assert e['root'].startswith(name+'/');seeds.append(e['seed'])
        seeds.append(q['derivatives']['A_noise']['seed'])
        for d in q['derivatives'].values():assert d['root']==name+'/A'
        assert q['episodes']['D']['copy_prefix_from']=='A'
    assert len(seeds)==len(set(seeds))
    return True

def draws(seed):
    x=seed
    while True:
        x=(x^((x<<13)&0xffffffff))&0xffffffff;x=(x^(x>>17))&0xffffffff;x=(x^((x<<5)&0xffffffff))&0xffffffff
        yield x

def synthesize_partition(spec):
    # Not called by development tests or plan generation. Requires authorized CLI.
    base={}
    for key,e in spec['episodes'].items():
        rng=draws(e['seed']);phases=[2*math.pi*(next(rng)/2**32) for _ in range(2)];data=bytearray()
        for n in range(19200):
            k,offset=divmod(n,4800);cycles=math.fsum(e['frequencies_hz'][:k])*.1+e['frequencies_hz'][k]*offset/48000
            v=(math.sin(2*math.pi*cycles+phases[0])+math.sin(2*math.pi*1.5*cycles+phases[1]))/16
            data.extend(struct.pack('<f',v))
        if key=='D':data[:38400]=base['A'][:38400]
        base[key]=bytes(data)
    values=struct.unpack('<19200f',base['A'])
    for key,d in spec['derivatives'].items():
        rng=draws(d['seed']) if d['operation']=='noise' else None;data=bytearray()
        for n,v in enumerate(values):
            if d['operation']=='gain_all' or (d['operation']=='gain_window_3' and 9600<=n<14400):v*=.5
            elif d['operation']=='noise':v+=d['amplitude']*(1 if next(rng)&1 else -1)
            if not math.isfinite(v) or abs(v)>1:raise ValueError('PCM_DOMAIN')
            data.extend(struct.pack('<f',v))
        base[key]=bytes(data)
    return base

def produce(auth_path):
    # Separate explicit production authorization is required; no automatic call.
    raw=PLAN_PATH.read_bytes();p=json.loads(raw);validate(p);auth=json.loads(Path(auth_path).read_text());part=auth.get('partition')
    expected=dict(status='AUTHORIZED_ONCE',action='PRODUCE_KNOWN_ORIGIN_PARTITION',partition=part,plan_sha256=hashlib.sha256(raw).hexdigest(),generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),python=sys.version)
    if part not in p['partitions'] or auth!=expected:raise ValueError('PRODUCTION_NOT_AUTHORIZED')
    from tools._s2uc_bounded_audio import OutputLedger,project_window
    out=ROOT/('reports/s2uc/known-origin-'+part+'-20260930-01');ledger=OutputLedger(out);calls=dict(receptor=0,nj=0);count=0;status='NOT_EVALUABLE';error=None
    try:
        ledger.write('claim.json',auth);materials=synthesize_partition(p['partitions'][part])
        for key,pcm in materials.items():
            e=p['partitions'][part]['episodes'].get(key);d=p['partitions'][part]['derivatives'].get(key)
            origin_root=e['root'] if e else d['root']
            # Store bounded PCM as hex within the accounted JSON, no hidden file writes.
            ledger.write(key+'-pcm.json',dict(sequence=key,root=origin_root,pcm_hex=pcm.hex(),sha256=hashlib.sha256(pcm).hexdigest()))
            for j in range(4):
                offset=e['source_start_sample'] if e else 0
                origin=dict(index=j+1,start_sample=offset+j*4800,end_sample=offset+(j+1)*4800)
                value=project_window(pcm[j*19200:(j+1)*19200],origin,calls)
                ledger.write(key+f'-{j+1}.json',dict(observer_root=origin_root,origin=origin,projection=value));count+=1
        assert count==28 and calls=={'receptor':28,'nj':28};status='MATERIAL_COMPLETE'
    except BaseException as exc:error=str(exc)
    finally:ledger.write('closure.json',dict(status=status,error=error,windows=count,calls=calls,final_evaluation_run=False),final=True)
    return status
if __name__=='__main__':
    if sys.argv[1:]==['write-plan']:
        with PLAN_PATH.open('x') as f:json.dump(plan(),f,indent=2)
    elif len(sys.argv)==3 and sys.argv[1]=='produce':print(produce(sys.argv[2]))
    else:raise SystemExit('write-plan or produce <separate-authorization.json>')
