"""HX1 recipe. Research hash streams are inaccessible without the run gate."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = 'docs/S2UC_HX1_PRUEFVERTRAG_20261004.md'

def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def raw(x): return (json.dumps(x, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(x): return hashlib.sha256(raw(x)).hexdigest()
def values(record): return [tuple(record['catalog'][i]) for i in record['ids']]

def plan():
    return dict(contract=CONTRACT, cases=[dict(id=f'HX1-{r:02d}-{c}',replicate=r,condition=c,orientation=(r-1)%2)
        for r in range(1,33) for c in ('D','N')], arms=['U','G','P'],
        masks=dict(Q=list(range(3,1024,4)),G_all=list(range(3,1024,2)),S=list(range(5,1024,4))),
        primary=['D:U-G','D:U-P','(D:U-G)-(N:U-G)'],bootstrap_draws=10000,
        limits=dict(total_seconds=3600,worker_seconds=3540,process_bytes=512*1048576,
        export_bytes=64*1048576,preparation_bytes=8*1048576,admin_bytes=2*1048576),
        research_materialization='AUTHORIZED_WORKER_ONLY')

class Stream:
    def __init__(self,r,name,*,authorized=False,neutral=False,draw=None):
        if not neutral and not authorized: raise PermissionError('RESEARCH_STREAM_LOCKED')
        self.r,self.name,self.neutral,self.d,self.draw=r,name,neutral,0,draw
    def below(self,n):
        if not 1<=n<=256: raise ValueError('RANDOM_RANGE')
        limit=2**64-(2**64%n)
        while True:
            if self.d>=4096: raise ValueError('RANDOM_DRAW_LIMIT')
            key=f"MCM-HX1/{'neutral' if self.neutral else 'source'}/v1/r={self.r}/stream={self.name}/draw={self.d}"
            u=self.draw(self.d) if self.draw else int.from_bytes(hashlib.sha256(key.encode()).digest()[:8],'big')
            self.d+=1
            if u<limit: return u%n
    def permute(self,items):
        result=list(items)
        for i in range(len(result)-1,0,-1):
            j=self.below(i+1);result[i],result[j]=result[j],result[i]
        return result

def choices(r,*,authorized=False):
    if not authorized: raise PermissionError('RESEARCH_STREAM_LOCKED')
    streams={s:Stream(r,s,authorized=True) for s in ('continuation','dependent-A','dependent-B','null-cue')}
    ys=streams['continuation'].permute([3]*128+[4]*128)
    ap=streams['dependent-A'].permute([i for i,y in enumerate(ys) if y==3])
    bp=streams['dependent-B'].permute([i for i,y in enumerate(ys) if y==4])
    ka,kb=(96,32) if r%2 else (32,96)
    xs=set(ap[:ka]+bp[:kb]);d=[0 if i in xs else 1 for i in range(256)]
    n=streams['null-cue'].permute([0]*128+[1]*128)
    return ys,d,n,{s:v.d for s,v in streams.items()}

def materialize(spec,*,authorized=False,neutral=False):
    r,c=spec['replicate'],spec['condition']
    if r not in range(1,33) or c not in ('D','N'): raise ValueError('SOURCE_SPEC')
    if neutral:
        pattern=[(0,3),(0,3),(0,4),(1,4),(1,4),(1,3),(0,3),(1,4)]
        blocks=[pattern[(b+r-2)%8] for b in range(1,257)]
        if c=='N': blocks=[(1-h,y) for h,y in blocks]
        draws={}
    else:
        ys,d,n,draws=choices(r,authorized=authorized)
        blocks=list(zip(d if c=='D' else n,ys))
    return dict(catalog=[[x+j/4096 for j in range(48)] for x in (1/8,7/8,1/2,1/4,3/4,1/16)],
        ids=[v for h,y in blocks for v in (h,2,y,5)],neutral_only=neutral,draws=draws)

def reference_choices(r,*,authorized=False,neutral=False,size=256):
    """Separate permutation and hash-counter implementation, no Stream reuse."""
    if not authorized and not neutral: raise PermissionError('REFERENCE_RESEARCH_LOCKED')
    if not neutral and size!=256: raise ValueError('REFERENCE_RESEARCH_SIZE')
    if size%8 or not 8<=size<=256: raise ValueError('REFERENCE_SIZE')
    counters={}
    def shuffled(seq,name):
        seq=list(seq);cursor=0;pos=len(seq)
        while pos>1:
            threshold=(1<<64)//pos*pos
            while True:
                if cursor==4096: raise ValueError('REFERENCE_DRAW_LIMIT')
                message='MCM-HX1/'+('neutral' if neutral else 'source')+'/v1/r='+str(r)+'/stream='+name+'/draw='+str(cursor)
                integer=int(hashlib.sha256(message.encode('utf-8')).hexdigest()[:16],16);cursor+=1
                if integer<threshold: break
            destination=integer%pos;pos-=1
            previous=seq[pos];seq[pos]=seq[destination];seq[destination]=previous
        counters[name]=cursor
        return seq
    target=shuffled([3 for _ in range(size//2)]+[4 for _ in range(size//2)],'continuation')
    sets=[shuffled([p for p in range(size) if target[p]==y],name)
          for y,name in [(3,'dependent-A'),(4,'dependent-B')]]
    cue=[1]*size
    for seq,count in zip(sets,([3*size//8,size//8] if r%2 else [size//8,3*size//8])):
        for p in seq[:count]: cue[p]=0
    null=shuffled([0]*(size//2)+[1]*(size//2),'null-cue')
    return target,cue,null,counters
