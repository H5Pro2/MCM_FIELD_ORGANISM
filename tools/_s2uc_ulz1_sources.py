"""Frozen ULZ1 source recipe; no research construction without explicit gate."""
import hashlib
from pathlib import Path
from tools._s2uc_lz1_sources import read,sha,digest,masks,values

ROOT=Path(__file__).resolve().parents[1]
CONTRACT='docs/S2UC_UL_Z_PRUEFVERTRAG_20261004.md'

def plan():
    return dict(cases=[dict(id=f'ULZ1-{r:02d}-{c}',replicate=r,condition=c,frames=1040)
        for r in range(1,33) for c in ('S','W')],arms=['U','L'],masks=masks(),
        primary=[dict(condition='S',mask='Y_33_128',direction='negative'),
                 dict(condition='W',mask='Y_129_160',direction='positive')],
        bootstrap=dict(draws=10000,clusters=32,z_start=0,k_start=0,
            key='MCM-ULZ1/bootstrap/v1/z={z}/k={k}',primary_quantiles=[.0125,.9875],
            secondary_quantiles=[.025,.975],quantile='linear-(n-1)*p'),
        source_key='MCM-ULZ1/source/v1/r={r}/b={b}',switch_after_block=128,
        neutral_pattern=[2,2,3,4,3,3,2,4],neutral_index='(b-1+r-1)%8',
        limits=dict(total_seconds=3600,worker_seconds=3540,closure_seconds=60,
            export_bytes=64*1048576,preparation_bytes=8*1048576,closure_reserve=1048576,
            heap_each=16384,original_frames=18,outputs=2,combined=20,bank=416,receipt=16384,utf8=32768),
        export_caps=dict(source_each=32768,case_each=524288,case_expanded=4194304,
            administrative_pool=1048576,maximum_with_preparation_and_closure=44*1048576),
        contract=CONTRACT,research_materialization='AUTHORIZED_WORKER_ONLY')

def research_choices(r,c,*,authorized=False):
    if not authorized:raise PermissionError('RESEARCH_SEQUENCE_NOT_AUTHORIZED')
    if r not in range(1,33) or c not in ('S','W'):raise ValueError('SOURCE_SPEC')
    e=2+((r-1)&1);other=5-e;out=[]
    for b in range(1,257):
        u=int.from_bytes(hashlib.sha256(f'MCM-ULZ1/source/v1/r={r}/b={b}'.encode()).digest()[:8],'big')
        threshold=1 if c=='W' and b>128 else 3
        out.append(e if 5*u<threshold*2**64 else other if 5*u<4*2**64 else 4)
    return out

def materialize(spec,*,authorized=False,neutral=False):
    if not neutral and not authorized:raise PermissionError('RESEARCH_SOURCE_NOT_AUTHORIZED')
    r=spec['replicate'];c=spec['condition']
    ys=[plan()['neutral_pattern'][(b+r-2)%8] for b in range(1,257)] if neutral else research_choices(r,c,authorized=True)
    prefix=[2,2,3,3] if not ((r-1)&2) else [3,3,2,2]
    catalog=[[v+j/4096 for j in range(48)] for v in (1/8,1/2,1/4,3/4,3/8)]
    return dict(catalog=catalog,ids=[k for y in prefix+ys for k in (0,1,y,0)],neutral_only=neutral)
