"""Bounded synthetic material producer. No matcher or result inputs/imports."""
import hashlib,json,math,struct,sys
from pathlib import Path
from tools._s2uc_bounded_audio import OutputLedger

ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/'docs/S2UC_FAKTORFORTSETZUNG_MATERIALPLAN_20261001.json'
BINDING=ROOT/'docs/S2UC_FAKTORFORTSETZUNG_PRODUKTIONSBINDUNG_20261001.json'
CASE_IDS={'F1','FH','FD','GH','GD','GR','GP','AM','ZF','EN','NM'}
def need(ok,code):
    if not ok:raise ValueError(code)
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path,limit=524288):
    need(Path(path).stat().st_size<=limit,'INPUT_SIZE_LIMIT')
    return json.loads(Path(path).read_text(encoding='utf-8'))
def vector_hash(values):
    return hashlib.sha256(b''.join(struct.pack('<d',x) for v in values for x in v)).hexdigest()
def validate_spec(spec,partition):
    need(set(spec['episodes'])==set('ABDZ') and set(spec['cases'])==CASE_IDS,'MATERIAL_SHAPE')
    seeds=[]
    for k,e in spec['episodes'].items():
        need(e['root']==partition+'/'+k and e['frames']==4 and e['components']==48,'EPISODE_SHAPE')
        need(type(e['seed']) is int and 0<e['seed']<2**32,'SEED_INVALID');seeds.append(e['seed'])
    need(len(set(seeds))==4,'SEED_COLLISION')
    for k,c in spec['cases'].items():
        need(c['learn']==(['A','A','D','D'] if k=='AM' else ['Z','Z'] if k=='ZF' else ['A','A']),'LEARN_SHAPE')
        need(c['test_index']==(19 if k=='AM' else 11) and len(c['hint'])==2,'CASE_SHAPE')
        need(c['truth'].startswith(partition+'/') and c['truth'] in {e['root'] for e in spec['episodes'].values()},'TRUTH_SCOPE')
        for ref in c['hint']+[c['target']]:
            need(ref['base'] in spec['episodes'] and type(ref['frame']) is int and 0<=ref['frame']<4 and type(ref['gain']) is float and ref['gain'] in (.5,1.,2.),'REFERENCE_INVALID')

def synthesize(spec,partition):
    validate_spec(spec,partition);base={}
    for key in 'ABDZ':
        x=spec['episodes'][key]['seed'];frames=[]
        for _ in range(4):
            values=[]
            for _ in range(48):
                x=(x^((x<<13)&0xffffffff))&0xffffffff
                x=(x^(x>>17))&0xffffffff
                x=(x^((x<<5)&0xffffffff))&0xffffffff
                values.append((1+(x%1023))/4096)
            frames.append(values)
        base[key]=frames
    base['D'][:2]=[list(v) for v in base['A'][:2]]
    base['Z'][:2]=[[0.]*48 for _ in range(2)]
    return base

def case_data(base,spec,cid,partition,profile):
    c=spec['cases'][cid];values=[];origins=[]
    for key in c['learn']:
        for j,v in enumerate(base[key]):
            values.append(v);origins.append(dict(root=spec['episodes'][key]['root'],base=key,frame=j,gain=1.))
    for ref in c['hint']+[c['target']]:
        e={.5:-1,1.:0,2.:1}[ref['gain']]
        values.append([math.ldexp(x,e) for x in base[ref['base']][ref['frame']]])
        origins.append(dict(root=spec['episodes'][ref['base']]['root'],**ref))
    need(len(values)==c['test_index'],'FRAME_COUNT')
    return dict(partition=partition,case_id=cid,profile=profile,values=values,origins=origins,
        truth=c['truth'],positive=c['positive'],target=c['test_index'],values_sha256=vector_hash(values))

def load_binding(path):
    b=read(path);need(b['status']=='BOUND_NOT_AUTHORIZED','BINDING_STATUS')
    ppath=ROOT/b['plan_path'];need(sha(ppath)==b['plan_sha256'],'PLAN_HASH')
    p=read(ppath)
    for bindings in (p['bindings']['code'],p['bindings']['tests'],b['code']):
        for name,h in bindings.items():need(sha(ROOT/name)==h,'CODE_HASH:'+name)
    need(sys.version==p['bindings']['python'] and sha(sys.executable)==p['bindings']['python_executable_sha256'],'RUNTIME_HASH')
    need(sha(ROOT/b['contract_path'])==p['bindings']['contract_sha256'],'CONTRACT_HASH')
    need(p['bounds']['max_material_bytes']==4194304 and p['bounds']['closure_reserve_bytes']==262144,'OUTPUT_BOUNDS')
    need(p['bounds']['base_components']==768 and p['bounds']['input_frames_per_policy']==129,'QUANTITY_BOUNDS')
    return b,p

def produce(auth_path,*,binding_path=BINDING):
    b,p=load_binding(binding_path);auth=read(auth_path,8192);part=auth.get('partition')
    expected=dict(status='AUTHORIZED_ONCE',action='PRODUCE_FACTOR_PARTITION',partition=part,
        binding_sha256=sha(binding_path),plan_sha256=b['plan_sha256'],python=sys.version)
    need(auth==expected and part in p['partitions'],'PRODUCTION_NOT_AUTHORIZED')
    spec=p['partitions'][part];validate_spec(spec,part)
    out=(ROOT/spec['output_directory']).resolve()
    need(out.is_relative_to((ROOT/'reports/s2uc').resolve()),'OUTPUT_SCOPE')
    ledger=OutputLedger(out)  # exclusive creation is the persistent one-shot claim
    count=frames=0;status='NOT_EVALUABLE';error=None
    try:
        ledger.write('claim.json',auth)
        profile=dict(definition=p['profile'],digest=hashlib.sha256(canonical(p['profile'])).hexdigest())
        base=synthesize(spec,part)
        for k in 'ABDZ':
            ledger.write('base-'+k+'.json',dict(partition=part,episode=k,root=spec['episodes'][k]['root'],profile=profile,values=base[k],values_sha256=vector_hash(base[k])))
        for cid in spec['cases']:
            row=case_data(base,spec,cid,part,profile)
            ledger.write('case-'+cid+'.json',row);count+=1;frames+=len(row['values'])
        need(count==11 and frames==129,'PRODUCTION_COUNTS')
        ledger.write('manifest.json',dict(partition=part,profile=profile,plan_sha256=b['plan_sha256'],spec=spec,
            files={f.name:sha(f) for f in sorted(out.iterdir())},base_components=768,case_frames=129,test_targets=11,learning_targets=48))
        status='MATERIAL_COMPLETE'
    except BaseException as exc:error=type(exc).__name__+':'+str(exc)
    finally:
        ledger.write('closure.json',dict(status=status,error=error,case_files=count,case_frames=frames,
            charged_before_closure=ledger.used,production_partition=part),final=True)
    return status

def read_verified(folder,spec,partition,profile_definition):
    """Lossless reader and recipe/derivation audit; never regenerates base data."""
    folder=Path(folder);closure=read(folder/'closure.json')
    need(closure['status']=='MATERIAL_COMPLETE','INCOMPLETE_MATERIAL')
    need(closure['case_files']==11 and closure['case_frames']==129 and closure['production_partition']==partition,'CLOSURE_COUNTS')
    need(len(list(folder.iterdir()))==18,'FILE_COUNT')
    need(sum(f.stat().st_size for f in folder.iterdir())<=4194304,'EXPORT_SIZE')
    manifest=read(folder/'manifest.json');need(manifest['spec']==spec and manifest['partition']==partition,'MANIFEST_SCOPE')
    need(set(manifest['files'])=={'claim.json'}|{'base-'+k+'.json' for k in 'ABDZ'}|{'case-'+k+'.json' for k in CASE_IDS},'MANIFEST_FILES')
    for name,h in manifest['files'].items():need(sha(folder/name)==h,'EXPORT_HASH')
    profile=dict(definition=profile_definition,digest=hashlib.sha256(canonical(profile_definition)).hexdigest())
    need(manifest['profile']==profile,'MANIFEST_PROFILE')
    base={}
    for k in 'ABDZ':
        row=read(folder/('base-'+k+'.json'));v=row['values']
        need(row['partition']==partition and row['episode']==k and row['root']==spec['episodes'][k]['root'] and row['profile']==profile,'BASE_SCOPE')
        need(len(v)==4 and all(len(a)==48 and all(type(x) is float and math.isfinite(x) for x in a) for a in v),'BASE_VALUES')
        need(vector_hash(v)==row['values_sha256'],'BASE_BITS');base[k]=v
    need(vector_hash(base['D'][:2])==vector_hash(base['A'][:2]),'PREFIX_BITS')
    need(all(struct.pack('<d',x)==b'\0'*8 for v in base['Z'][:2] for x in v),'ZERO_BITS')
    rows={}
    for cid in spec['cases']:
        row=read(folder/('case-'+cid+'.json'));expected=case_data(base,spec,cid,partition,profile)
        need(row==expected and vector_hash(row['values'])==row['values_sha256'],'CASE_DERIVATION')
        rows[cid]=row
    need(sum(len(r['values']) for r in rows.values())==129,'TOTAL_FRAMES')
    return rows

if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='produce':
        status=produce(sys.argv[2]);print(status);raise SystemExit(0 if status=='MATERIAL_COMPLETE' else 1)
    raise SystemExit('produce <explicit-authorization.json>')
