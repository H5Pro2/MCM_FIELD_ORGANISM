"""UHR1 fixed recipe; research access requires the exact admitted one-shot worker."""
import hashlib
import json
import os
from pathlib import Path
from tools import _s2uc_hx1_sources as hx

ROOT=hx.ROOT
BINDING=ROOT/'docs/S2UC_UHR1_VORREGISTRIERUNGSBINDUNG_20261005.json'
CONTRACT='docs/S2UC_UHR1_PRUEFVERTRAG_20261005.md'
PROFILE='4309cfc91eb99fc2a999fdac99c5a7f1807ee654996e019ec0d94e3900bcbd4b'
read=hx.read;raw=hx.raw;sha=hx.sha;digest=hx.digest
NAMES=('continuation','dependent-A','dependent-B','null-cue')

def plan():
    return dict(cases=[dict(id=f'UHR1-{r:02d}-{c}',replicate=r,condition=c,orientation=(r-1)%2)
        for r in range(1,33) for c in ('D','N')],arms=['U','H'],known_sources=False,
        source_namespace='MCM-UHR1/source/v1')

class _Permit:
    def __init__(self,pid,folder):self.pid=pid;self.folder=folder

def admit(auth,folder):
    from tools import s2uc_uhr1 as runner
    runner.validate_research_admission(auth,folder)
    return _Permit(os.getpid(),Path(folder).resolve())

def gate(neutral,permit):
    if type(neutral) is not bool:raise ValueError('NEUTRAL_FLAG')
    if not neutral:
        if type(permit) is not _Permit or permit.pid!=os.getpid():raise PermissionError('UHR1_RESEARCH_LOCKED')
        if not (permit.folder/'attempt.json').is_file() or (permit.folder/'manifest.json').exists():raise PermissionError('MATERIALIZATION_PHASE_CLOSED')

class Stream:
    def __init__(self,r,name,*,neutral=False,permit=None,draw=None):
        gate(neutral,permit)
        if r not in range(1,33) or name not in NAMES:raise ValueError('STREAM_SPEC')
        if draw is not None and not neutral:raise PermissionError('DRAW_INJECTION_NEUTRAL_ONLY')
        self.r,self.name,self.neutral,self.d,self.draw=r,name,neutral,0,draw
    def below(self,n):
        if type(n) is not int or not 1<=n<=256:raise ValueError('RANDOM_RANGE')
        threshold=(1<<64)-((1<<64)%n)
        while True:
            if self.d>=4096:raise ValueError('RANDOM_DRAW_LIMIT')
            key=f"MCM-UHR1/{'neutral' if self.neutral else 'source'}/v1/r={self.r}/stream={self.name}/draw={self.d}"
            u=self.draw(self.d) if self.draw else int.from_bytes(hashlib.sha256(key.encode('utf-8')).digest()[:8],'big')
            self.d+=1
            if type(u) is not int or not 0<=u<1<<64:raise ValueError('DRAW_RANGE')
            if u<threshold:return u%n
    def permute(self,items):
        out=list(items)
        for i in range(len(out)-1,0,-1):
            j=self.below(i+1);out[i],out[j]=out[j],out[i]
        return out

def choices(r,*,neutral=False,permit=None):
    gate(neutral,permit)
    streams={s:Stream(r,s,neutral=neutral,permit=permit) for s in NAMES}
    ys=streams['continuation'].permute([3]*128+[4]*128)
    ap=streams['dependent-A'].permute([i for i,y in enumerate(ys) if y==3])
    bp=streams['dependent-B'].permute([i for i,y in enumerate(ys) if y==4])
    ka,kb=(96,32) if r%2 else (32,96)
    xs=set(ap[:ka]+bp[:kb]);d=[0 if i in xs else 1 for i in range(256)]
    n=streams['null-cue'].permute([0]*128+[1]*128)
    return ys,d,n,{s:v.d for s,v in streams.items()}

def reference_choices(r,*,neutral=False,permit=None):
    """Independent counters/permutation, no Stream or production choices call."""
    gate(neutral,permit)
    if r not in range(1,33):raise ValueError('REFERENCE_REPLICATE')
    counters={}
    def shuffled(seq,name):
        seq=list(seq);cursor=0;pos=len(seq)
        while pos>1:
            threshold=((1<<64)//pos)*pos
            while True:
                if cursor==4096:raise ValueError('REFERENCE_DRAW_LIMIT')
                text='MCM-UHR1/'+('neutral' if neutral else 'source')+'/v1/r='+str(r)+'/stream='+name+'/draw='+str(cursor)
                u=int(hashlib.sha256(text.encode('ascii')).hexdigest()[:16],16);cursor+=1
                if u<threshold:break
            pos-=1;j=u%(pos+1);old=seq[pos];seq[pos]=seq[j];seq[j]=old
        counters[name]=cursor
        return seq
    target=shuffled([3 for _ in range(128)]+[4 for _ in range(128)],'continuation')
    cue=[1]*256
    for y,name,count in [(3,'dependent-A',96 if r%2 else 32),(4,'dependent-B',32 if r%2 else 96)]:
        positions=shuffled([i for i in range(256) if target[i]==y],name)
        for pos in positions[:count]:cue[pos]=0
    null=shuffled([0 for _ in range(128)]+[1 for _ in range(128)],'null-cue')
    return target,cue,null,counters

def materialize(spec,*,neutral=False,permit=None):
    gate(neutral,permit)
    if spec not in plan()['cases']:raise ValueError('SOURCE_SPEC')
    r,c=spec['replicate'],spec['condition']
    if neutral:
        pattern=[(0,3),(0,3),(0,4),(1,4),(1,4),(1,3),(0,3),(1,4)]
        blocks=[pattern[(b+r-2)%8] for b in range(1,257)]
        if c=='N':blocks=[(1-h,y) for h,y in blocks]
        draws={}
    else:
        ys,d,n,draws=choices(r,permit=permit)
        blocks=list(zip(d if c=='D' else n,ys))
    return dict(catalog=[[x+j/4096 for j in range(48)] for x in (1/8,7/8,1/2,1/4,3/4,1/16)],
        ids=[v for h,y in blocks for v in (h,2,y,5)],neutral_only=neutral,draws=draws)

def validate_record(v,spec,*,neutral=False,permit=None):
    gate(neutral,permit)
    if spec not in plan()['cases']:raise ValueError('SOURCE_SPEC')
    if set(v)!={'catalog','ids','neutral_only','draws'} or v['neutral_only'] is not neutral:raise ValueError('SOURCE_FIELDS')
    catalog=[[x+j/4096 for j in range(48)] for x in (.125,.875,.5,.25,.75,.0625)]
    if raw(v['catalog'])!=raw(catalog) or len(v['ids'])!=1024 or any(type(i) is not int for i in v['ids']):raise ValueError('SOURCE_STRUCTURE')
    r,c=spec['replicate'],spec['condition']
    if neutral:
        # Independent indexing of the frozen eight-block qualification pattern.
        cues=(0,0,0,1,1,1,0,1);targets=(3,3,4,4,4,3,3,4);expected=[]
        for b in range(256):
            pos=(b+r-1)%8;cue=cues[pos] if c=='D' else 1-cues[pos]
            expected.extend((cue,2,targets[pos],5))
        counters={}
    else:
        ys,d,n,counters=reference_choices(r,permit=permit)
        expected=[]
        for i in range(256):expected.extend(((d if c=='D' else n)[i],2,ys[i],5))
    if v['ids']!=expected or v['draws']!=counters:raise ValueError('SOURCE_RECIPE_REFERENCE')
    return True

def seal_sources(folder,ledger,*,neutral=False,permit=None,check=lambda:None):
    gate(neutral,permit);folder=Path(folder);entries=[];prior=None
    for spec in plan()['cases']:
        check();v=materialize(spec,neutral=neutral,permit=permit)
        validate_record(v,spec,neutral=neutral,permit=permit)
        targets=v['ids'][2::4]
        if spec['condition']=='D':prior=targets
        elif targets!=prior:raise ValueError('PAIRED_CONTINUATIONS')
        name=spec['id']+'-source.json';ledger.write(name,v)
        entries.append(spec|dict(path=name,bytes=(folder/name).stat().st_size,sha256=sha(folder/name),draws=v['draws']))
    manifest=dict(neutral_only=neutral,known_sources=False,all_sources_before_policy=True,
        input_mode='fixed neutral pattern' if neutral else 'new same-family sources',entries=entries,
        namespace='fixed-neutral-pattern' if neutral else 'MCM-UHR1/source/v1')
    ledger.write('manifest.json',manifest)
    return manifest,digest(manifest)

def load_sealed(folder,spec,manifest,manifest_hash):
    folder=Path(folder)
    if sha(folder/'manifest.json')!=manifest_hash or digest(manifest)!=manifest_hash:raise ValueError('MANIFEST_CHANGED')
    if [dict((k,e[k]) for k in ('id','replicate','condition','orientation')) for e in manifest['entries']]!=plan()['cases']:raise ValueError('MANIFEST_CASES')
    e=manifest['entries'][2*(spec['replicate']-1)+(spec['condition']=='N')]
    if e['id']!=spec['id'] or e['path']!=spec['id']+'-source.json':raise ValueError('SOURCE_PATH')
    data=(folder/e['path']).read_bytes()
    if len(data)!=e['bytes'] or hashlib.sha256(data).hexdigest()!=e['sha256']:raise ValueError('SOURCE_CHANGED')
    v=json.loads(data)
    if v['neutral_only'] is not manifest['neutral_only'] or raw(v)!=data:raise ValueError('SOURCE_SERIALIZATION')
    return v

def load(spec,*,neutral=False):
    return materialize(spec,neutral=neutral)
