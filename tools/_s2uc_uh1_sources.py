"""Read-only frozen HX1 sources; research loader requires explicit admission."""
import json
import hashlib
from pathlib import Path
from tools import _s2uc_hx1_sources as hx
ROOT=hx.ROOT
BINDING=ROOT/'docs/S2UC_UH1_QUELLENBINDUNG_20261004.json'
read=hx.read;raw=hx.raw;sha=hx.sha;digest=hx.digest
PROFILE='4309cfc91eb99fc2a999fdac99c5a7f1807ee654996e019ec0d94e3900bcbd4b'
def plan():return dict(cases=[dict(id=f'UH1-{r:02d}-{c}',replicate=r,condition=c) for r in range(1,33) for c in ('D','N')],arms=['U','H'],known_sources=True)
def validate_record(v):
    expected=[[x+j/4096 for j in range(48)] for x in (.125,.875,.5,.25,.75,.0625)]
    if v['catalog']!=expected or len(v['ids'])!=1024:raise ValueError('SOURCE_STRUCTURE')
    for i in range(0,1024,4):
        if v['ids'][i] not in (0,1) or v['ids'][i+1]!=2 or v['ids'][i+2] not in (3,4) or v['ids'][i+3]!=5:raise ValueError('SOURCE_PHASE')
def validate_all():
    b=read(BINDING)
    if len(b['entries'])!=64:raise ValueError('SOURCE_COUNT')
    for p,v in b['anchors'].items():
        if sha(ROOT/p)!=v['sha256']:raise ValueError('SOURCE_ANCHOR')
    manifest=read(ROOT/'reports/s2uc/hx1-comparison-20261004-01/manifest.json')
    closure=read(ROOT/'reports/s2uc/hx1-comparison-20261004-01/closure.json')
    for i,e in enumerate(b['entries']):
        r=i//2+1;c='D' if i%2==0 else 'N';name=f'HX1-{r:02d}-{c}-source.json'
        if (e['replicate'],e['condition'],e['path'])!=(r,c,'reports/s2uc/hx1-comparison-20261004-01/'+name):raise ValueError('SOURCE_ORDER')
        p=ROOT/e['path'];data=p.read_bytes()
        if len(data)!=e['bytes'] or hashlib.sha256(data).hexdigest()!=e['sha256'] or e['sha256']!=manifest['entries'][i]['sha256'] or e['sha256']!=closure['files'][name]['sha256']:raise ValueError('SOURCE_HASH')
        v=json.loads(data);validate_record(v)
        if v['neutral_only']:raise ValueError('SOURCE_NEUTRAL')
    return b
def load(spec,*,neutral=False,authorized=False):
    if neutral:return hx.materialize(spec,neutral=True)
    if not authorized:raise PermissionError('UH1_RESEARCH_LOCKED')
    b=read(BINDING);e=b['entries'][2*(spec['replicate']-1)+(spec['condition']=='N')]
    data=(ROOT/e['path']).read_bytes()
    if len(data)!=e['bytes'] or hashlib.sha256(data).hexdigest()!=e['sha256']:raise ValueError('SOURCE_CHANGED')
    v=json.loads(data);validate_record(v);return v
