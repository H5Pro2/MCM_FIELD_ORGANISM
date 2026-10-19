"""PCM -> unchanged receptor -> unchanged NJ. No material at import."""
import math,struct
from .common import *
from tools._s2uc_bounded_audio import project_window
from tools import _s2nj_private_auditory_output_projection as nj

def source_pcm(freq):
    need(len(freq)==4,'FOUR_FREQUENCIES');out=bytearray()
    for n in range(19200):
        k,t=divmod(n,4800)
        c=math.fsum(f*.1 for f in freq[:k])+(freq[k]*t)/48000
        x=(math.sin((2.*math.pi)*c)+math.sin(((2.*math.pi)*(1.5*c))+math.pi/4.))/16.
        need(math.isfinite(x) and abs(x)<=1.,'PCM_DOMAIN');out.extend(struct.pack('<f',x))
    return bytes(out)
def interval(case,i):
    need(case in CASES and 1<=i<=11,'FRAME_ID')
    if i<=8:return 'A',((i-1)%4)*4800,((i-1)%4+1)*4800
    start=(480 if case.endswith('480') else 0)+(i-9)*4800
    return case[0],start,start+4800
def cut(data,start,end):
    need(0<=start<end<=len(data)//4 and end-start==4800,'PCM_INTERVAL')
    return data[4*start:4*end]
class Calls(dict):
    def __init__(self,ledger):super().__init__(receptor=0,nj=0);self.ledger=ledger
    def __setitem__(self,k,v):
        need(v==self[k]+1,'CALL_INCREMENT')
        if k=='nj':self.ledger.bump('receptor_completed')
        self.ledger.bump(k+'_started');super().__setitem__(k,v)
def materialize(folder,mode,ledger,permit=False):
    need(mode=='neutral' or (mode=='research' and permit is True),'SOURCE_NOT_AUTHORIZED')
    budget=Budget(folder);recipe=NEUTRAL if mode=='neutral' else RECIPE
    need(mode!='neutral' or not set(sum(recipe.values(),[]))&set(sum(RECIPE.values(),[])),'RESERVED_FREQUENCY')
    budget.save('material/recipe.json',dict(mode=mode,frequencies=recipe,contract_sha256=CONTRACT_SHA))
    sources={}
    for name,freq in recipe.items():
        ledger.bump('sources');sources[name]=source_pcm(freq);budget.save('material/'+name+'.f32le',sources[name])
    calls=Calls(ledger)
    for case in CASES:
        for i in range(1,12):
            src,start,end=interval(case,i);payload=cut(sources[src],start,end)
            origin=dict(index=i,start_sample=(i-1)*4800,end_sample=i*4800)
            budget.save(f'material/{case}-{i:02}.f32le',payload)
            projection=project_window(payload,origin,calls);ledger.bump('nj_completed')
            budget.save(f'material/{case}-{i:02}.json',dict(source=src,source_interval=[start,end],source_sha256=digest(sources[src]),
                 pcm_sha256=digest(payload),origin=origin,projection=projection))
    need(calls==dict(receptor=44,nj=44),'PROJECTION_COUNT')
    files={p.name:info(p) for p in (Path(folder)/'material').iterdir()}
    budget.save('material/manifest.json',dict(mode=mode,files=files,profile_digest=nj.PROFILE_DIGEST,counts=dict(calls)))
    ledger.event('MATERIAL_SEALED',sha256=sha(Path(folder)/'material/manifest.json'))

def verify(folder,mode):
    p=Path(folder)/'material';m=read(p/'manifest.json')
    need(m['mode']==mode and m['profile_digest']==nj.PROFILE_DIGEST and m['counts']==dict(receptor=44,nj=44),'MANIFEST')
    expected={'recipe.json','A.f32le','B.f32le'}|{f'{c}-{i:02}.{ext}' for c in CASES for i in range(1,12) for ext in ('json','f32le')}
    need(set(m['files'])==expected and {x.name for x in p.iterdir()}==expected|{'manifest.json'},'MATERIAL_FILES')
    for name,item in m['files'].items():need(info(p/name)==item,'MATERIAL_HASH:'+name)
    need(read(p/'recipe.json')==dict(mode=mode,frequencies=NEUTRAL if mode=='neutral' else RECIPE,contract_sha256=CONTRACT_SHA),'RECIPE')
    sources={k:(p/(k+'.f32le')).read_bytes() for k in ('A','B')}
    for c in CASES:
        for i in range(1,12):
            row=read(p/f'{c}-{i:02}.json');src,start,end=interval(c,i);proj=row['projection']
            need(row['source']==src and row['source_interval']==[start,end] and row['source_sha256']==digest(sources[src]),'SOURCE_LINEAGE')
            payload=(p/f'{c}-{i:02}.f32le').read_bytes()
            need(payload==cut(sources[src],start,end) and row['pcm_sha256']==digest(payload),'PCM_BINDING')
            need(row['origin']==dict(index=i,start_sample=(i-1)*4800,end_sample=i*4800),'REPLAY_TIME')
            need(proj['snapshot_index']==(i-1)*10 and proj['window_start_tick']==(i-1)*4800 and proj['window_end_tick']==i*4800,'NJ_TIME')
            need(proj['profile_digest']==nj.PROFILE_DIGEST and len(proj['values'])==48,'NJ_PROFILE')
            body={k:v for k,v in proj.items() if k!='projection_digest'}
            need(proj['projection_digest']==nj.digest(body),'NJ_DIGEST')
    return m
