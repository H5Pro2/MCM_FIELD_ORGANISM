"""Policy-blind deterministic source specification. No IO or policy imports."""
import hashlib

EVALUATION='MCM-T1-v1'
NEUTRAL='MCM-QUALIFICATION-ONLY-v1'
SCHEDULES=(None,((3,'C',0),(17,'R',0),(2,'I',1),(23,'C',1),(5,'H',0),(30,'R',0)),
    ((10,'R',0),(1,'I',1),(29,'C',1),(4,'R',0),(36,'C',0)),
    ((7,'C',0),(13,'H',0),(6,'R',1),(19,'I',1),(35,'C',0)))


def specification(name,replicate,schedule,parts):
    phases=[];start=1
    for length,mode,bank in parts:
        if mode not in ('C','R','I','H') or bank not in (0,1) or length<1:raise ValueError('PHASE_SPEC')
        end=start+length-1
        phases.append(dict(start=start,end=end,mode=mode,bank=bank,
            targets=[t for t in range(3,81,2) if start+2<=t<=end],negative_control=mode in ('I','H')))
        start=end+1
    n=start-1
    if not 4<=n<=80 or n%2:raise ValueError('FRAME_BOUND')
    return dict(id=name,replicate=replicate,schedule=schedule,frames=n,phases=phases,
        stable=len(phases)==1,masks=dict(G=list(range(3,n,2)),G_w=list(range(11,n,2)) if len(phases)==1 else []))


def cases(*,neutral=False):
    return [specification(f'{"neutral" if neutral else "T1"}-{i}-{r}',r+100 if neutral else r,
        f'{"Q" if neutral else "S"}{i}',((80,'H' if r<=2 else 'C',0),) if i==0 else SCHEDULES[i])
        for i in range(4) for r in range(1,5)]


def word(namespace,kind,*parts):
    return hashlib.sha256('|'.join(map(str,(namespace,kind,*parts))).encode('utf-8')).digest()


def generate(spec,*,namespace=NEUTRAL,authorized=False):
    if namespace==EVALUATION:
        if not authorized or spec not in cases():raise PermissionError('T1_SOURCE_NOT_AUTHORIZED')
    elif namespace!=NEUTRAL or spec['replicate']<100 or not spec['schedule'].startswith('Q'):
        raise ValueError('NEUTRAL_NAMESPACE_REQUIRED')
    r=spec['replicate']
    library=[[[(.5+(int.from_bytes(word(namespace,'vector',r,b,s,j)[:2],'big')+1)/262144)
        for j in range(48)] for s in range(8)] for b in range(2)]
    state=int.from_bytes(word(namespace,'draw',r,spec['schedule'],0)[:4],'big')%8
    values=[];states=[];modes=[];banks=[];modal=[]
    for t in range(1,spec['frames']+1):
        phase=next(p for p in spec['phases'] if p['start']<=t<=p['end'])
        mode,bank=phase['mode'],phase['bank'];previous=state
        modal_state=None if t==1 or mode=='I' else (previous+(1 if mode=='C' else -1 if mode=='R' else 0))%8
        if t>1:
            draw=int.from_bytes(word(namespace,'draw',r,spec['schedule'],t)[:4],'big')
            if mode=='I':state=draw%8
            elif mode in ('C','R') and draw%4<3:state=(state+(1 if mode=='C' else -1))%8
        values.append(list(library[bank][state]));states.append(state);modes.append(mode);banks.append(bank)
        modal.append(None if modal_state is None else list(library[bank][modal_state]))
    return dict(values=values,library=library,states=states,modes=modes,banks=banks,modal=modal,
        namespace=namespace,replicate=r,schedule=spec['schedule'],synthetic=True,audio_video_chain=False)


def validate(bundle,spec,*,namespace=NEUTRAL,authorized=False):
    if bundle!=generate(spec,namespace=namespace,authorized=authorized):raise ValueError('SOURCE_PROVENANCE')
