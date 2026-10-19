"""Neutral ER1 recipe; research namespace deliberately unavailable."""
import hashlib
NAMESPACE='MCM-ER1/neutral/v1'
class Stream:
    def __init__(self,r,name): self.r=r;self.name=name;self.cursor=0
    def below(self,n):
        while self.cursor<4096:
            key=f'{NAMESPACE}/r={self.r}/stream={self.name}/draw={self.cursor}'
            self.cursor+=1
            value=int.from_bytes(hashlib.sha256(key.encode()).digest()[:8],'big')
            if value < 2**64-2**64%n:return value%n
        raise ValueError('DRAW_LIMIT')
def generate(r):
    if type(r) is not int or not 1<=r<=32:raise ValueError('STORY')
    cue=Stream(r,'cue');out=Stream(r,'outcome');blocks=[];i=cue.below(4)
    for b in range(256):
        if b and cue.below(2):i=[j for j in range(4) if j!=i][cue.below(3)]
        dominant=(i%2)^((r-1)%2)^int(b>=128)
        y=dominant ^ int(out.below(4)==0)
        blocks.append([i,y])
    return dict(replicate=r,orientation=(r-1)%2,blocks=blocks,draws=[cue.cursor,out.cursor],namespace=NAMESPACE)
def reconstruct(r):
    # Separate iterator/cursor and rejection implementation, no Stream/generate call.
    def draws(name):
        for k in range(4096):
            digest=hashlib.sha256(('MCM-ER1/neutral/v1/r=%d/stream=%s/draw=%d'%(r,name,k)).encode()).hexdigest()
            yield int(digest[:16],16)
        raise ValueError('REFERENCE_DRAW_LIMIT')
    streams={name:iter(draws(name)) for name in ('cue','outcome')};counts=dict(cue=0,outcome=0)
    def take(name,n):
        limit=(1<<64)//n*n
        while True:
            v=next(streams[name]);counts[name]+=1
            if v<limit:return v%n
    previous=take('cue',4);answer=[]
    for block in range(1,257):
        if block>1:
            keep=take('cue',2)==0
            if not keep:
                rank=take('cue',3);previous=tuple(v for v in (0,1,2,3) if v!=previous)[rank]
        a=((previous%2)+((r-1)%2)+(block>128))%2==0
        flip=take('outcome',4)==0
        answer.append([previous,int(a==flip)])
    return dict(replicate=r,orientation=(r-1)%2,blocks=answer,draws=[counts['cue'],counts['outcome']],namespace='MCM-ER1/neutral/v1')

def materialize(r):
    description=generate(r)
    bases=(1/16,3/16,5/16,7/16,1/2,1/4,3/4,15/16)
    catalog=[[x+j/4096 for j in range(48)] for x in bases]
    return dict(catalog=catalog,ids=[v for cue,y in description['blocks'] for v in (cue,4,5+y,7)])
def reference_frames(r):
    description=reconstruct(r);result=[]
    for cue,outcome in description['blocks']:
        for base in ((2*cue+1)/16,.5,.25+.5*outcome,.9375):
            result.append(tuple((4096*base+dimension)/4096 for dimension in range(48)))
    return result
