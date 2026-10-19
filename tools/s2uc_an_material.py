"""Bounded PCM/NJ material connection. Import and plan creation generate no PCM."""
import hashlib
import math
import struct
import sys
from pathlib import Path

from tools.s2uc_factor_material import ROOT, need, read, sha, canonical, vector_hash
from tools.s2uc_known_origin_material_plan import draws, synthesize_partition
from tools._s2uc_bounded_audio import OutputLedger, project_window
from tools import _s2nj_private_auditory_output_projection as nj

PLAN = ROOT / 'docs/S2UC_AUDIO_NJ_MATERIALPLAN_20261001.json'
BINDING = ROOT / 'docs/S2UC_AN_PRODUKTIONSBINDUNG_20261001.json'
CONTRACT = 'docs/S2UC_AUDIO_NJ_NAEHERUNGSABRUF_PRUEFVERTRAG_20261001.txt'
IDS = ('R0','R1','R2','R3','N1','N2','N3','N4','Z0','Z1','P0')
RESERVED = {1210001,1210007,1210013,1210019,1210031,1210037,1210043,
            1310001,1310007,1310013,1310019,1310031,1310037}
WINDOW_BYTES = 19200


def spec_for(part, seeds, frequencies, output, *, evaluation=False):
    episodes = {k:dict(seed=seeds[i], frequencies_hz=frequencies[i], root=part+'/'+k,
        source_stream=part+('/AC' if k in 'AC' else '/'+k),
        source_start_sample=19200 if k=='C' else 0,
        copy_prefix_from='A' if k=='D' else None) for i,k in enumerate('ABCD')}
    cases = {}
    for cid in IDS:
        root = dict(N1='B',N2='C',N3='D',N4='M',Z0='ZERO',Z1='NOISE').get(cid,'A')
        cases[cid] = dict(learn=['A','A','B','B'] if cid=='N4' else ['A','A'],
            truth=part+'/'+root, positive=cid in ('R0','R1','R2','R3','P0'),
            test_index=19 if cid=='N4' else 11,
            query_start_samples=[0,4800,9600], operation=cid)
    return dict(partition=part, kind='EVAL' if evaluation else 'DEV', episodes=episodes,
        noise_R=dict(seed=seeds[4],samples=9600,amplitude=2**-12),
        noise_Z=dict(seed=seeds[5],samples=14400,amplitude=2**-11),
        calibration=None if evaluation else dict(seed=seeds[6],windows=8,
            amplitudes=[2**-12]*4+[2**-11]*4), small_signal_gain=2**-12,
        cases=cases, output_directory=output, windows=49 if evaluation else 57,
        pcm_bytes=940800 if evaluation else 1094400)


def plan():
    parts = {}
    for part,seeds,freqs in [
        ('AN-DEV',[1210001,1210007,1210013,1210019,1210031,1210037,1210043],
         [[340,580,820,1180],[460,920,700,1540],[640,1060,1420,880],[340,580,1780,2060]]),
        ('AN-EVAL',[1310001,1310007,1310013,1310019,1310031,1310037],
         [[490,760,1120,1620],[670,1320,970,1860],[790,1480,1960,1080],[490,760,2160,2420]])]:
        parts[part] = spec_for(part,seeds,freqs,'reports/s2uc/audio-nj-material-'+part.lower()+'-01',evaluation=part.endswith('EVAL'))
    return dict(version='s2uc.an.material.v1',status='PLAN_ONLY',partitions=parts,
        profile=nj.profile_payload(), profile_digest=nj.PROFILE_DIGEST,
        pcm=dict(format='mono-float32-le',sample_rate=48000,window=4800,external_hop=4800),
        recipe=dict(base='s2uc_known_origin_material_plan.synthesize_partition; derivatives empty',
            perturbation='stored float32 -> binary64 arithmetic -> one float32 rounding; reject nonfinite/outside[-1,1]',
            R1='A[0:9600]+bipolar(noise_R); clean A[9600:14400]',
            R2='A[0:9600]+2*bipolar(noise_R); clean A[9600:14400]',
            R3='R1[0:9600] followed by R1[4800:9600]',
            N4='float32((binary64(A[0:14400])+binary64(B[0:14400]))/2)',
            P0='float32(binary64(A[0:14400])*2^-12)',
            calibration='8 continuous PRNG PCM windows; max(mean(abs(NJ)))',
            genealogy='labels from recipe, not NJ matches; D prefix copied from A'),
        max_material_bytes=4194304,closure_reserve_bytes=262144,
        replay=dict(frames_per_arm=129,primary_targets=11,learning_targets=48,
            continuation='legacy_v1',tau_grid=[0.,1/256,1/128,1/64,1/32,1/16,1/8]))


def validate(spec, part):
    need(spec['partition']==part and spec['kind'] in ('DEV','EVAL'),'PARTITION')
    need(part.endswith('-'+spec['kind']),'PARTITION_KIND_MISMATCH')
    need(set(spec['episodes'])==set('ABCD'),'EPISODES')
    seeds=[spec['episodes'][k]['seed'] for k in 'ABCD']+[spec['noise_R']['seed'],spec['noise_Z']['seed']]
    if spec['kind']=='EVAL':
        need(spec['calibration'] is None,'EVAL_CALIBRATION_FORBIDDEN')
    else:
        need(spec['calibration'] is not None,'DEV_CALIBRATION_REQUIRED')
        seeds.append(spec['calibration']['seed'])
    need(all(type(s) is int and 0<s<2**32 for s in seeds) and len(set(seeds))==len(seeds),'SEEDS')
    frequencies=[spec['episodes'][k]['frequencies_hz'] for k in 'ABCD']
    need(all(len(fs)==4 and all(type(f) is int and 0<f<12000 for f in fs) for fs in frequencies),'FREQUENCIES')
    expected=spec_for(part,seeds,frequencies,spec['output_directory'],evaluation=spec['kind']=='EVAL')
    need(spec==expected,'SPEC_CHANGED')
    if part.startswith('AN-'):
        need(part in plan()['partitions'] and spec==plan()['partitions'][part],'RESERVED_PLAN_CHANGED')
    else:
        need(part in ('NEUTRAL-DEV','NEUTRAL-EVAL') and RESERVED.isdisjoint(seeds),'NEUTRAL_SEEDS_REQUIRED')


def pcm(values):
    data=bytearray()
    for v in values:
        need(math.isfinite(v) and abs(v)<=1,'PCM_DOMAIN')
        data.extend(struct.pack('<f',v))
    return bytes(data)


def samples(data):
    need(len(data)%4==0,'PCM_SIZE')
    values=struct.unpack('<'+str(len(data)//4)+'f',data)
    need(all(math.isfinite(x) and abs(x)<=1 for x in values),'PCM_DOMAIN')
    return values


def noise(seed, amplitudes):
    rng=draws(seed)
    return pcm(a*(1 if next(rng)&1 else -1) for a in amplitudes)


def query_pcm(base,spec):
    a=samples(base['A'][:57600]);b=samples(base['B'][:57600])
    n=samples(noise(spec['noise_R']['seed'],[2**-12]*9600))
    r1=pcm(x+y for x,y in zip(a[:9600],n))+base['A'][38400:57600]
    return dict(R0=base['A'][:57600],R1=r1,
        R2=pcm(x+2*y for x,y in zip(a[:9600],n))+base['A'][38400:57600],
        R3=r1[:38400]+r1[19200:38400],N1=base['B'][:57600],
        N2=base['C'][:57600],N3=base['D'][:57600],
        N4=pcm((x+y)/2 for x,y in zip(a,b)),Z0=bytes(57600),
        Z1=noise(spec['noise_Z']['seed'],[2**-11]*14400),P0=pcm(x*2**-12 for x in a))


def calibration_pcm(spec):
    need(spec['kind']=='DEV' and spec['calibration'] is not None,'EVAL_CALIBRATION_FORBIDDEN')
    c=spec['calibration']
    return noise(c['seed'],(a for a in c['amplitudes'] for _ in range(4800)))


def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()


def lineage(cid,spec,base):
    keys=['A','B'] if cid=='N4' else [{'N1':'B','N2':'C','N3':'D'}.get(cid,'A')] if cid not in ('Z0','Z1') else []
    result=[]
    for k in keys:
        indices=[0,1,1] if cid=='R3' else [0,1,2]
        e=spec['episodes'][k]
        result.append(dict(base=k,pcm_sha256=digest_bytes(base[k]),source_stream=e['source_stream'],
            source_windows=[dict(frame=j,start_sample=e['source_start_sample']+j*4800,
                pcm_sha256=digest_bytes(base[k][j*19200:(j+1)*19200])) for j in indices]))
    return dict(operation=cid,ancestors=result,noise=spec['noise_R'] if cid in ('R1','R2','R3') else spec['noise_Z'] if cid=='Z1' else None,
        gain=spec['small_signal_gain'] if cid=='P0' else None)


def export_sequence(ledger,key,data,start,root,ancestry,calls):
    samples(data)
    need(len(data)%WINDOW_BYTES==0,'WINDOW_SIZE')
    ledger.write(key+'-pcm.json',dict(key=key,root=root,pcm_hex=data.hex(),pcm_sha256=digest_bytes(data),lineage=ancestry))
    for j in range(len(data)//WINDOW_BYTES):
        block=data[j*WINDOW_BYTES:(j+1)*WINDOW_BYTES]
        origin=dict(index=j+1,start_sample=start+j*4800,end_sample=start+(j+1)*4800)
        projection=project_window(block,origin,calls)
        ledger.write(key+f'-{j}.json',dict(origin=origin,pcm_sha256=digest_bytes(block),projection=projection))


def materialize(spec,part,out,claim):
    """Internal connection; production entry performs code/runtime/auth binding first."""
    validate(spec,part)
    ledger=OutputLedger(out)  # exclusive claim before any generator or projection
    calls=dict(receptor=0,nj=0);status='NOT_EVALUABLE';error=None
    try:
        ledger.write('claim.json',claim)
        base=synthesize_partition(dict(episodes={k:spec['episodes'][k] for k in 'ABCD'},derivatives={}))
        queries=query_pcm(base,spec)
        for k,data in base.items():
            e=spec['episodes'][k]
            export_sequence(ledger,k,data,e['source_start_sample'],e['root'],dict(episode=e,
                copied_prefix_sha256=digest_bytes(base['A'][:38400]) if k=='D' else None),calls)
        for cid,data in queries.items():
            export_sequence(ledger,cid,data,0,spec['cases'][cid]['truth'],lineage(cid,spec,base),calls)
        if spec['kind']=='DEV':
            export_sequence(ledger,'calibration',calibration_pcm(spec),0,part+'/CALIBRATION',spec['calibration'],calls)
        need(calls==dict(receptor=spec['windows'],nj=spec['windows']),'PROJECTION_COUNTS')
        ledger.write('manifest.json',dict(partition=part,spec=spec,profile=nj.profile_payload(),
            profile_digest=nj.PROFILE_DIGEST,files={f.name:sha(f) for f in ledger.folder.iterdir()}))
        status='MATERIAL_COMPLETE'
    except BaseException as exc:
        error=type(exc).__name__+':'+str(exc)
    finally:
        ledger.write('closure.json',dict(status=status,error=error,partition=part,calls=calls,
            charged_before_closure=ledger.used,final_evaluation_run=False),final=True)
    return status


def load_binding(path=BINDING):
    import numpy as np
    b=read(path);need(b['status']=='BOUND_NOT_AUTHORIZED','BINDING_STATUS')
    need(sha(ROOT/b['plan_path'])==b['plan_sha256'],'PLAN_HASH')
    p=read(ROOT/b['plan_path']);need(p==plan(),'PLAN_CHANGED')
    need(sha(ROOT/CONTRACT)==b['contract_sha256'],'CONTRACT_HASH')
    for name,h in b['code'].items():need(sha(ROOT/name)==h,'CODE_HASH:'+name)
    need(sys.version==b['python'] and sha(sys.executable)==b['python_executable_sha256'],'RUNTIME')
    need(np.__version__==b['numpy_version'],'NUMPY_VERSION')
    for name,h in b['numpy_files'].items():need(sha(Path(np.__file__).parent/name)==h,'NUMPY_HASH')
    return b,p


def produce(auth_path,*,binding_path=BINDING):
    b,p=load_binding(binding_path);auth=read(auth_path,8192);part=auth.get('partition')
    expected=dict(status='AUTHORIZED_ONCE',action='PRODUCE_AN_PARTITION',partition=part,
        binding_sha256=sha(binding_path),plan_sha256=b['plan_sha256'],python=sys.version)
    need(auth==expected and part in p['partitions'],'PRODUCTION_NOT_AUTHORIZED')
    spec=p['partitions'][part];out=(ROOT/spec['output_directory']).resolve()
    need(out.is_relative_to((ROOT/'reports/s2uc').resolve()),'OUTPUT_SCOPE')
    return materialize(spec,part,out,auth)


def read_verified(folder,spec,part):
    """No receptor calls; verify sealed export, PCM derivations, times and NJ digests."""
    validate(spec,part);folder=Path(folder);c=read(folder/'closure.json')
    need(c['status']=='MATERIAL_COMPLETE','INCOMPLETE_MATERIAL')
    need(c['partition']==part and c['calls']==dict(receptor=spec['windows'],nj=spec['windows']),'CLOSURE_COUNTS')
    counts={**{k:4 for k in 'ABCD'},**{cid:3 for cid in IDS}}
    if spec['kind']=='DEV':counts['calibration']=8
    names={'claim.json'}|{k+'-pcm.json' for k in counts}|{k+f'-{j}.json' for k,n in counts.items() for j in range(n)}
    need({f.name for f in folder.iterdir()}==names|{'manifest.json','closure.json'},'FILE_SET')
    need(sum(f.stat().st_size for f in folder.iterdir())<=4194304,'OUTPUT_LIMIT')
    manifest=read(folder/'manifest.json')
    need(manifest['spec']==spec and manifest['partition']==part and set(manifest['files'])==names,'MANIFEST_SCOPE')
    need(manifest['profile']==nj.profile_payload() and manifest['profile_digest']==nj.PROFILE_DIGEST,'PROFILE')
    for name,h in manifest['files'].items():need(sha(folder/name)==h,'EXPORT_HASH')
    data={};values={};records={}
    for key,n in counts.items():
        record=read(folder/(key+'-pcm.json'));block=bytes.fromhex(record['pcm_hex']);samples(block)
        need(len(block)==n*WINDOW_BYTES and record['key']==key and digest_bytes(block)==record['pcm_sha256'],'PCM_BITS')
        data[key]=block;records[key]=record;values[key]=[]
        start=spec['episodes'][key]['source_start_sample'] if key in 'ABCD' else 0
        for j in range(n):
            row=read(folder/(key+f'-{j}.json'));p=dict(row['projection'])
            for field in ('carrier_ids','values','subnormal_band_indices','underflow_band_indices'):p[field]=tuple(p[field])
            projection=nj.HalfScaleAuditory48V1(**p)
            need(row['origin']==dict(index=j+1,start_sample=start+j*4800,end_sample=start+(j+1)*4800),'ORIGIN_TIME')
            need(projection.window_start_tick==start+j*4800 and projection.window_end_tick==start+(j+1)*4800,'PROJECTION_TIME')
            need(row['pcm_sha256']==digest_bytes(block[j*WINDOW_BYTES:(j+1)*WINDOW_BYTES]),'PROJECTION_PCM_BINDING')
            values[key].append(list(projection.values))
    base={k:data[k] for k in 'ABCD'}
    need(base['D'][:38400]==base['A'][:38400],'PREFIX_BITS')
    for k in 'ABCD':
        e=spec['episodes'][k]
        need(records[k]['root']==e['root'] and records[k]['lineage']==dict(episode=e,
            copied_prefix_sha256=digest_bytes(base['A'][:38400]) if k=='D' else None),'BASE_LINEAGE')
    queries=query_pcm(base,spec)
    for cid in IDS:
        need(data[cid]==queries[cid] and records[cid]['root']==spec['cases'][cid]['truth']
            and records[cid]['lineage']==lineage(cid,spec,base),'QUERY_DERIVATION')
    if spec['kind']=='DEV':
        need(data['calibration']==calibration_pcm(spec) and records['calibration']['lineage']==spec['calibration']
            and records['calibration']['root']==part+'/CALIBRATION','CALIBRATION_DERIVATION')
    rows={}
    for cid in IDS:
        case=spec['cases'][cid];v=[frame for k in case['learn'] for frame in values[k]]+values[cid]
        rows[cid]=dict(values=v,truth=case['truth'],positive=case['positive'],target=case['test_index'],
            profile_digest=nj.PROFILE_DIGEST,values_sha256=vector_hash(v))
        need(len(v)==case['test_index'],'REPLAY_COUNT')
    return rows,values.get('calibration',[])


if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='produce':
        result=produce(sys.argv[2]);print(result);raise SystemExit(0 if result=='MATERIAL_COMPLETE' else 1)
    raise SystemExit('produce <separate-authorization.json>')
