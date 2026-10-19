"""Receptor-free caller source preparation; no runtime admission or execution."""
from dataclasses import asdict
import hashlib
from tools import _structure_source_binding as s
from tools import _s2ob_private_caller_binding as b

VERSION='structure-av.sources.v1'
ORDER=('q04','q04','q05','q06','q06-cue')
AUDIO='sources/s2ob/caller-av-basic/window.pcm'
AUDIO_HASH='f1080644e18dac7583d73cd300f9b0dda45ad123c96ba66f4740a5a17a1e6df4'
DEST='sources/structure-av-fixed'


class SourceError(ValueError):
    pass


def need(ok,code):
    if not ok:raise SourceError(code)


def cue_in_place(data,width,height):
    need(type(data) is bytearray and len(data)==width*height*3
         and width%12==0 and height%8==0,'CUE_GEOMETRY')
    for y in range(height):
        row=y//(height//8)
        for x in range(width):
            cell=row*12+x//(width//12)
            base=(y*width+x)*3
            for channel in range(3):
                if cell*3+channel>=32:data[base+channel]=0


def manifest(proofs,code_digest):
    need(set(proofs)==set(ORDER),'SOURCE_SET')
    events=[]
    for n,name in enumerate(ORDER,1):
        kind=b.AV if n<5 else b.V
        p=proofs[name]
        rgb=b.Payload(f'structure-rgb-{n:02}',f'{DEST}/{name}.rgb',p['sha256'],p['bytes'])
        pcm=b.Payload(f'structure-pcm-{n:02}',AUDIO,AUDIO_HASH,19200) if n<5 else None
        events.append(b.Event(f'structure-av-{n:02}' if n<5 else 'structure-vc-05',n,kind,
            **b.expected_times(n,kind),pcm=pcm,rgb=rgb))
    return b.build_manifest('structure-av-pending-01',tuple(events),code_digest)


def verify(record,execution,seal):
    need(record['version']==VERSION and record['execution_digest']==s.digest(execution)
         and record['seal_digest']==s.digest(seal),'ROOT_BINDING')
    proofs=record['files'];need(set(proofs)==set(ORDER),'SOURCE_SET')
    for name in ('q04','q05','q06'):
        old=next(x for x in seal['sources'] if x['id']==name)
        source=next(x for x in execution['sources'] if x['id']==name)
        need(proofs[name]==dict(sha256=old['sha256'],bytes=old['bytes'],source_digest=s.digest(source)),
             'SOURCE_BINDING')
    cue=proofs['q06-cue']
    need(cue['parent_sha256']==proofs['q06']['sha256'] and cue['components']==list(range(32))
         and cue['bytes']==6220800,'CUE_BINDING')
    expected=asdict(manifest(proofs,record['manifest']['code_digest']))
    need(s.raw(expected)==s.raw(record['manifest']),'MANIFEST_BINDING')
    return dict(status='BINDING_VALID',record_digest=s.digest(record),read_only=True,
                regenerated=False,receptor_calls=0,main_authorized=False)
