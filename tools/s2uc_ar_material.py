"""Bounded AR vector producer; no retrieval or parameter-selection imports."""
import hashlib,math,sys
from pathlib import Path
from tools.s2uc_factor_material import ROOT,need,read,sha,canonical,vector_hash,OutputLedger
from tools.s2uc_known_origin_material_plan import draws
PLAN=ROOT/'docs/S2UC_SIGNAL_NAEHERUNGSABRUF_MATERIALPLAN_20261001.json'
BINDING=ROOT/'docs/S2UC_AR_PRODUKTIONSBINDUNG_20261001.json'
IDS={'R0','R1','R2','R3','N1','N2','N3','N4','Z0','Z1','P0'}

def load_binding(path=BINDING):
    b=read(path);need(b['status']=='BOUND_NOT_AUTHORIZED','BINDING_STATUS')
    need(sha(ROOT/b['plan_path'])==b['plan_sha256'],'PLAN_HASH');p=read(ROOT/b['plan_path'])
    for group in (p['bindings']['code'],p['bindings']['tests'],b['code']):
        for name,h in group.items():need(sha(ROOT/name)==h,'CODE_HASH:'+name)
    need(sys.version==p['bindings']['python'] and sha(sys.executable)==p['bindings']['python_executable_sha256'],'RUNTIME')
    need(sha(ROOT/b['contract_path'])==p['bindings']['contract_sha256'],'CONTRACT_HASH')
    need(b['max_material_bytes']==4194304 and b['closure_reserve_bytes']==262144,'OUTPUT_BOUNDS')
    return b,p

def validate(spec,part):
    need(set(spec['episodes'])==set('ABCD') and set(spec['cases'])==IDS,'MATERIAL_SHAPE')
    seeds=[]
    for k,e in spec['episodes'].items():
        need(e['root']==part+'/'+k and e['frames']==4 and e['components']==48,'EPISODE_SHAPE');seeds.append(e['seed'])
    for key,count in [('noise_R',2),('noise_Z',3),('calibration',spec['calibration']['frames'])]:
        e=spec[key];need(e['frames']==count and e['components']==48 and e['amplitude']==2**-10,'NOISE_SHAPE');seeds.append(e['seed'])
    need(spec['calibration']['frames'] in (0,8),'CALIBRATION_COUNT')
    if part.endswith('EVAL'):need(spec['calibration']['frames']==0,'EVAL_CALIBRATION_FORBIDDEN')
    need(all(type(s) is int and 0<s<2**32 for s in seeds) and len(set(seeds))==7,'SEEDS')
    need(spec['small_signal_gain']==2**-12,'SMALL_GAIN')
    for cid,c in spec['cases'].items():
        need(c['learn']==(['A','A','B','B'] if cid=='N4' else ['A','A']),'LEARNING_SHAPE')
        need(c['test_index']==(19 if cid=='N4' else 11) and c['truth'].startswith(part+'/'),'CASE_SCOPE')

def noise(e):
    if not e['frames']:return []  # evaluation seed is never accessed by draws
    rng=draws(e['seed'])
    return [[e['amplitude']*(1 if next(rng)&1 else -1) for _ in range(48)] for _ in range(e['frames'])]

def synthesize(spec,part):
    validate(spec,part);base={}
    for k in 'ABCD':
        rng=draws(spec['episodes'][k]['seed'])
        base[k]=[[(257+next(rng)%768)/4096. for _ in range(48)] for _ in range(4)]
    base['D'][:2]=[list(v) for v in base['A'][:2]]
    return base,{key:noise(spec[key]) for key in ('noise_R','noise_Z','calibration')}

def case_data(base,aux,spec,cid,part,profile):
    a=base['A'];n=aux['noise_R'];c=spec['cases'][cid]
    if cid=='R0':q=a[:3]
    elif cid in ('R1','R2','R3'):
        gain=2. if cid=='R2' else 1.
        hint=[[x+gain*z for x,z in zip(v,r)] for v,r in zip(a[:2],n)]
        q=hint+[hint[1] if cid=='R3' else a[2]]
    elif cid in ('N1','N2','N3'):q=base[{'N1':'B','N2':'C','N3':'D'}[cid]][:3]
    elif cid=='N4':q=[[(x+y)/2 for x,y in zip(v,w)] for v,w in zip(a[:3],base['B'][:3])]
    elif cid=='Z0':q=[[0.]*48 for _ in range(3)]
    elif cid=='Z1':q=aux['noise_Z']
    else:q=[[math.ldexp(x,-12) for x in v] for v in a[:3]]
    values=[];origins=[]
    for k in c['learn']:
        for j,v in enumerate(base[k]):
            e=spec['episodes'][k];values.append(v)
            origins.append(dict(root=e['root'],base=k,frame=j,source_stream=e['source_stream'],source_frame=e['source_start_frame']+j))
    values.extend(q)
    origins.extend([dict(root=c['truth'],expression=c['hint'],query_frame=j) for j in range(2)]+[dict(root=c['truth'],expression=c['target'],query_frame=2)])
    need(len(values)==c['test_index'],'FRAME_COUNT')
    return dict(partition=part,case_id=cid,profile=profile,values=values,origins=origins,truth=c['truth'],positive=c['positive'],target=c['test_index'],values_sha256=vector_hash(values))

def produce(auth_path,*,binding_path=BINDING):
    b,p=load_binding(binding_path);auth=read(auth_path,8192);part=auth.get('partition')
    expected=dict(status='AUTHORIZED_ONCE',action='PRODUCE_AR_PARTITION',partition=part,binding_sha256=sha(binding_path),plan_sha256=b['plan_sha256'],python=sys.version)
    need(auth==expected and part in p['partitions'],'PRODUCTION_NOT_AUTHORIZED')
    spec=p['partitions'][part];validate(spec,part);out=(ROOT/spec['output_directory']).resolve()
    need(out.is_relative_to((ROOT/'reports/s2uc').resolve()),'OUTPUT_SCOPE')
    ledger=OutputLedger(out);count=frames=0;status='NOT_EVALUABLE';error=None
    try:
        ledger.write('claim.json',auth)
        profile=dict(definition=p['profile'],digest=hashlib.sha256(canonical(p['profile'])).hexdigest())
        base,aux=synthesize(spec,part)
        for k,v in {**base,**aux}.items():
            ledger.write('source-'+k+'.json',dict(partition=part,key=k,profile=profile,values=v,values_sha256=vector_hash(v)))
        for cid in spec['cases']:
            row=case_data(base,aux,spec,cid,part,profile);ledger.write('case-'+cid+'.json',row)
            count+=1;frames+=len(row['values'])
        need(count==11 and frames==129,'PRODUCTION_COUNTS')
        ledger.write('manifest.json',dict(partition=part,profile=profile,spec=spec,plan_sha256=b['plan_sha256'],files={f.name:sha(f) for f in out.iterdir()},calibration_interpretation='Fixed bipolar magnitude: mean absolute amplitude is constructed as 2^-10; recipe check, not estimation of unknown noise floor.'))
        status='MATERIAL_COMPLETE'
    except BaseException as exc:error=type(exc).__name__+':'+str(exc)
    finally:ledger.write('closure.json',dict(status=status,error=error,case_files=count,case_frames=frames,partition=part,charged_before_closure=ledger.used),final=True)
    return status

def read_verified(folder,spec,part,profile_definition):
    validate(spec,part);folder=Path(folder);c=read(folder/'closure.json')
    need(c['status']=='MATERIAL_COMPLETE','INCOMPLETE_MATERIAL')
    need(c['case_files']==11 and c['case_frames']==129 and c['partition']==part,'CLOSURE_COUNTS')
    names={'claim.json'}|{'source-'+k+'.json' for k in ['A','B','C','D','noise_R','noise_Z','calibration']}|{'case-'+k+'.json' for k in IDS}
    need({x.name for x in folder.iterdir()}==names|{'manifest.json','closure.json'},'FILE_SET')
    need(sum(x.stat().st_size for x in folder.iterdir())<=4194304,'OUTPUT_LIMIT')
    manifest=read(folder/'manifest.json');need(manifest['spec']==spec and manifest['partition']==part and set(manifest['files'])==names,'MANIFEST_SCOPE')
    for name,h in manifest['files'].items():need(sha(folder/name)==h,'EXPORT_HASH')
    profile=dict(definition=profile_definition,digest=hashlib.sha256(canonical(profile_definition)).hexdigest());need(manifest['profile']==profile,'PROFILE')
    base={};aux={}
    for k in ['A','B','C','D','noise_R','noise_Z','calibration']:
        row=read(folder/('source-'+k+'.json'));v=row['values'];count=4 if k in 'ABCD' else spec[k]['frames']
        need(row['partition']==part and row['key']==k and row['profile']==profile,'SOURCE_SCOPE')
        need(len(v)==count and all(len(a)==48 and all(type(x) is float and math.isfinite(x) for x in a) for a in v),'SOURCE_SHAPE')
        need(vector_hash(v)==row['values_sha256'],'SOURCE_BITS')
        if k in 'ABCD':base[k]=v
        else:
            need(all(abs(x)==spec[k]['amplitude'] for a in v for x in a),'NOISE_AMPLITUDE');aux[k]=v
    need(vector_hash(base['A'][:2])==vector_hash(base['D'][:2]),'PREFIX_BITS')
    rows={}
    for cid in spec['cases']:
        row=read(folder/('case-'+cid+'.json'));expected=case_data(base,aux,spec,cid,part,profile)
        need(row==expected and vector_hash(row['values'])==row['values_sha256'],'CASE_DERIVATION');rows[cid]=row
    need(vector_hash(rows['R1']['values'][-3:-1])==vector_hash(rows['R3']['values'][-3:-1]),'R1_R3_PREFIX')
    return rows,aux

if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='produce':
        result=produce(sys.argv[2]);print(result);raise SystemExit(0 if result=='MATERIAL_COMPLETE' else 1)
    raise SystemExit('produce <explicit-authorization.json>')
