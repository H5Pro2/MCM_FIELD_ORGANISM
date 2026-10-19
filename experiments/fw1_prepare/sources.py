"""Gated FW1 recipe; neutral and admitted research use identical mathematics."""
import hashlib

NEUTRAL='MCM-FW1/neutral/v1'
RESEARCH='MCM-FW1/source/v1'
_PERMIT=None

def admit(auth,folder):
    global _PERMIT
    from .entry import validate_admission
    config,_=validate_admission(auth,folder)
    if config['mode']!='research':raise PermissionError('RESEARCH_SOURCE_AUTH_REQUIRED')
    _PERMIT=object();return _PERMIT

def namespace(neutral,permit):
    if neutral is True:return NEUTRAL
    if neutral is not False or permit is None or permit is not _PERMIT:raise PermissionError('RESEARCH_SOURCE_ADMISSION')
    return RESEARCH

def scope(pair,blocks,neutral,permit=None):
    namespace(neutral,permit)
    if type(pair) is not int or not 1<=pair<=16:raise ValueError('PAIR')
    if type(blocks) is not int or not 1<=blocks<=256:raise ValueError('BLOCKS')

class Draws:
    def __init__(self,pair,name,digest=None,*,neutral=True,permit=None):
        self.ns=namespace(neutral,permit)
        self.pair=pair;self.name=name;self.cursor=0;self.digest=digest or (lambda b:hashlib.sha256(b).digest())
    def below(self,n):
        while self.cursor<4096:
            text=f'{self.ns}/r={self.pair}/stream={self.name}/draw={self.cursor}'
            self.cursor+=1;value=int.from_bytes(self.digest(text.encode())[:8],'big')
            if value<2**64-2**64%n:return value%n
        raise ValueError('DRAW_LIMIT')

def transition(previous,u):
    if previous not in range(4) or u not in range(24):raise ValueError('TRANSITION_INPUT')
    return (previous if u<12 else [i for i in range(4) if i!=previous][(u-12)//4],u%4)

def outcome(cue,orientation,block,flip):
    return cue%2 ^ orientation ^ int(block>=129) ^ flip

def generate(pair,blocks=256,*,neutral=True,permit=None):
    scope(pair,blocks,neutral,permit);cue=Draws(pair,'cue',neutral=neutral,permit=permit);noise=Draws(pair,'outcome',neutral=neutral,permit=permit)
    a=b=cue.below(4);result={'A':[],'B':[]}
    for block in range(1,blocks+1):
        if block>1:a,b=transition(a,cue.below(24))
        flip=int(noise.below(4)==0)
        for label,i in (('A',a),('B',b)):
            result[label].append([i,outcome(i,(pair-1)%2,block,flip)])
    return dict(pair=pair,orientation=(pair-1)%2,namespace=namespace(neutral,permit),blocks=result,draws=[cue.cursor,noise.cursor])

def reconstruct(pair,blocks=256,*,neutral=True,permit=None):
    scope(pair,blocks,neutral,permit)
    ns=namespace(neutral,permit)
    def stream(name):
        for position in range(4096):
            text='%s/r=%d/stream=%s/draw=%d'%(ns,pair,name,position)
            yield int(hashlib.sha256(text.encode()).hexdigest()[:16],16)
    streams={n:iter(stream(n)) for n in ('cue','outcome')};counts=dict(cue=0,outcome=0)
    def take(name,n):
        for v in streams[name]:
            counts[name]+=1
            if v<(1<<64)//n*n:return v%n
        raise ValueError('REFERENCE_DRAW_LIMIT')
    current=take('cue',4);answer={'A':[],'B':[]}
    for position in range(blocks):
        other=current
        if position:
            draw=take('cue',24);other=draw-4*(draw//4)
            if draw>=12:
                rank=(draw-12)//4
                current=rank+int(rank>=current)
        bit=int(take('outcome',4)==0)
        for name,value in (('A',current),('B',other)):
            answer[name].append([value,(value+(pair-1)%2+int(position>=128)+bit)%2])
    return dict(pair=pair,orientation=(pair-1)%2,namespace=namespace(neutral,permit),blocks=answer,draws=[counts['cue'],counts['outcome']])

def materialize(description,condition,*,neutral=True,permit=None):
    if description['namespace']!=namespace(neutral,permit) or condition not in ('A','B'):raise PermissionError('SOURCE_SCOPE')
    bases=(1/16,3/16,5/16,7/16,.5,.25,.75,.9375)
    return dict(catalog=[[x+j/4096 for j in range(48)] for x in bases],
                ids=[v for cue,y in description['blocks'][condition] for v in (cue,4,5+y,7)])

def verify_material(value,reference,condition):
    actual=[value['catalog'][i] for i in value['ids']];expected=[]
    for cue,y in reference['blocks'][condition]:
        for x in ((2*cue+1)/16,1/2,(1+2*y)/4,15/16):
            expected.append([(4096*x+j)/4096 for j in range(48)])
    if actual!=expected:raise ValueError('SOURCE_REFERENCE')
