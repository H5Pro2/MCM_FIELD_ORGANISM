"""Fixed URA1 recipe; research material only inside a separately admitted run."""
import hashlib
import os
from pathlib import Path

NAMES=('continuation','dependent-A','dependent-B')


class _Permit:
    def __init__(self,folder):self.folder=Path(folder).resolve();self.pid=os.getpid()


def admit(auth,folder):
    from tools.s2uc_ura1_prepare_v2 import validate_admission
    validate_admission(auth,folder)
    return _Permit(folder)


def gate(neutral,permit=None):
    if type(neutral) is not bool:raise ValueError('NEUTRAL_FLAG')
    if not neutral:
        if type(permit) is not _Permit or permit.pid!=os.getpid():raise PermissionError('URA1_RESEARCH_LOCKED')
        if not (permit.folder/'START.json').exists() or (permit.folder/'sources-manifest.json').exists():
            raise PermissionError('SOURCE_PHASE_CLOSED')


class Stream:
    def __init__(self,r,name,*,neutral=True,permit=None,draw=None):
        gate(neutral,permit)
        if type(r) is not int or r not in range(1,33) or name not in NAMES:raise ValueError('STREAM_SPEC')
        if draw is not None and not neutral:raise PermissionError('DRAW_NEUTRAL_ONLY')
        self.r,self.name,self.neutral,self.cursor,self.draw=r,name,neutral,0,draw
    def below(self,n):
        if type(n) is not int or not 1<=n<=256:raise ValueError('DRAW_RANGE')
        cutoff=2**64-(2**64%n)
        while True:
            if self.cursor>=4096:raise ValueError('DRAW_LIMIT')
            key=f"MCM-URA1/{'neutral' if self.neutral else 'source'}/v1/r={self.r}/stream={self.name}/draw={self.cursor}"
            u=self.draw(self.cursor) if self.draw else int.from_bytes(hashlib.sha256(key.encode()).digest()[:8],'big')
            self.cursor+=1
            if type(u) is not int or not 0<=u<2**64:raise ValueError('DRAW_VALUE')
            if u<cutoff:return u%n
    def shuffle(self,items):
        items=list(items)
        for i in range(len(items)-1,0,-1):
            j=self.below(i+1);items[i],items[j]=items[j],items[i]
        return items


def generate(r,*,neutral=True,permit=None):
    gate(neutral,permit)
    streams={s:Stream(r,s,neutral=neutral,permit=permit) for s in NAMES}
    ys=streams['continuation'].shuffle([3]*128+[4]*128)
    ap=streams['dependent-A'].shuffle([i for i,v in enumerate(ys) if v==3])
    bp=streams['dependent-B'].shuffle([i for i,v in enumerate(ys) if v==4])
    a,b=(96,32) if r%2 else (32,96);xs=set(ap[:a]+bp[:b])
    return dict(replicate=r,orientation=(r-1)%2,neutral_only=neutral,
        catalog=[[x+j/4096 for j in range(48)] for x in (.125,.875,.5,.25,.75,.0625)],
        ids=[v for i,y in enumerate(ys) for v in (0 if i in xs else 1,2,y,5)],
        draws={s:x.cursor for s,x in streams.items()})


def frames(record):return [tuple(record['catalog'][i]) for i in record['ids']]
