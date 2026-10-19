"""LZ1 fixed descriptions and explicitly gated source construction."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONTRACT='docs/S2UC_LERNBARKEIT_ERFAHRUNGSZYKLUS_PRUEFENTWURF_20261004.md'

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def masks():
    y=[4*b+15 for b in range(1,257)]
    post=list(range(17,1040,2))
    return dict(G=list(range(3,1040,2)),G_init=list(range(3,16,2)),G_post=post,
        G_Y=y,G_skeleton=[t for t in post if t not in y],
        Y_1_32=y[:32],Y_33_128=y[32:128],Y_129_160=y[128:160],Y_161_256=y[160:])

def plan():
    return dict(cases=[dict(id=f'LZ1-{r:02d}-{c}',replicate=r,condition=c,frames=1040)
        for r in range(1,33) for c in ('S','W','N')],arms=['P','U','H64'],masks=masks(),
        primary_mask='G_Y',primary_contrasts=['S:H64-P','W:H64-P','S:U-P','W:U-P'],
        bootstrap=dict(draws=10000,clusters=32,primary_quantiles=[.00625,.99375],secondary_quantiles=[.025,.975],
            key='MCM-LZ1/uncertainty/v1/z={z}/k={k}',mapping='first8-big-endian-mod32',quantile='linear-(n-1)*p'),
        source_key='MCM-LZ1/v1/r={r}/b={b}',switch_after_block=128,
        limits=dict(total_seconds=3600,worker_seconds=3540,closure_seconds=60,export_bytes=64*1048576,
            preparation_bytes=8*1048576,closure_reserve=1048576,U_heap=16384,H64_heap=128*1024,
            original_frames=18,outputs=2,combined=20,bank=416,receipt=16384,utf8=32768),
        export_caps=dict(source_each=32*1024,case_each=512*1024,case_expanded=4*1048576,
            administrative_pool=1048576,maximum_with_preparation_and_closure=61*1048576),
        contract=CONTRACT,scope='CAPACITY_WITHIN_TWO_RETAINED_NO_TRANSFER',research_materialization='AUTHORIZED_WORKER_ONLY')

def research_choices(r,c,*,authorized=False):
    if not authorized:raise PermissionError('RESEARCH_SEQUENCE_NOT_AUTHORIZED')
    preferred=2+((r-1)&1)
    out=[]
    for b in range(1,257):
        u=int.from_bytes(hashlib.sha256(f'MCM-LZ1/v1/r={r}/b={b}'.encode()).digest()[:8],'big')
        # Exact integer thresholds avoid rounding of the specified probabilities.
        win=2*u<2**64 if c=='N' else 5*u<(1 if c=='W' and b>128 else 4)*2**64
        out.append(preferred if win else 5-preferred)
    return out

def materialize(spec,*,authorized=False,neutral=False):
    if not neutral and not authorized:raise PermissionError('RESEARCH_SOURCE_NOT_AUTHORIZED')
    r=spec['replicate'];c=spec['condition']
    if neutral:
        bases=(.1875,.4375,.3125,.5625)
        catalog=[[v+j/131072 for j in range(48)] for v in bases]
        pattern=(2,2,3,2,3,3,2,3)
        choices=[pattern[(b+r+(3 if c=='W' and b>=128 else 1 if c=='N' else 0))%8] for b in range(256)]
    else:
        catalog=[[v+j/4096 for j in range(48)] for v in (1/8,1/2,1/4,3/4)]
        choices=research_choices(r,c,authorized=True)
    prefix=[2,2,3,3] if not ((r-1)&2) else [3,3,2,2]
    ids=[v for y in prefix+choices for v in (0,1,y,0)]
    return dict(catalog=catalog,ids=ids,neutral_only=neutral)

def values(record):
    return [tuple(record['catalog'][i]) for i in record['ids']]
