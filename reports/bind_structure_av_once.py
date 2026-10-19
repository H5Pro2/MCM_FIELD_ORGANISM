"""One source qualification, then one caller-file preparation, no perception."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from dataclasses import asdict
from tools import _structure_av_sources as a
from tools import _s2oc_shared_binding as shared

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/s2oe/structure-av-source-binding-20260912-02'
OLD=ROOT/'reports/s2oe/structure-location-source-seal-20260912-01'
OWN=('tools/_structure_av_sources.py','tests/test_structure_av_sources.py','reports/bind_structure_av_once.py',
     'tools/_structure_source_binding.py','docs/STRUKTUR_LAGE_VIER_FORMATIONEN.md')
CAPS=dict(preregistration=12288,inventory=24576,record=12288,proof=2048,qualification=1024,
          log=4096,failure=1024,balance=2048,report=2048,claims=15)


def pin(p):
    data=p.read_bytes();return [hashlib.sha256(data).hexdigest(),len(data)]


def save(name,value):
    data=a.s.raw(value);a.need(len(data)<=CAPS[name],'ARTIFACT_LIMIT')
    with (OUT/(name+'.json')).open('xb') as f:f.write(data)


def check(b):
    for path,value in b['files'].items():a.need(pin(ROOT/path)==value,'CODE_CHANGED')
    a.need(pin(Path(sys.executable))==b['interpreter'],'INTERPRETER_CHANGED')


def prepare():
    a.need(not OUT.exists() and not (ROOT/a.DEST).exists(),'OUTPUT_EXISTS')
    inv=shared.inventory()
    files={p:pin(ROOT/p) for p in set(shared.OWN)|set(OWN)}
    for p in ('execution.json','seal.json','verification.json','preregistration.json'):
        path=OLD/p;files[path.relative_to(ROOT).as_posix()]=pin(path)
    qual=ROOT/'reports/s2oc/s2oc-shared-closure-qualification-20260910-03'
    for p in ('package.json','qualification.zip'):
        path=qual/p;files[path.relative_to(ROOT).as_posix()]=pin(path)
    # Hash all transitive software in the inherited inventory; count the same
    # active source attachments and inventory as the qualified OC path.
    meta=sum(v[1] for p,v in files.items() if not p.endswith(('.py','.md')))
    sources=sum(v[1] for p,v in files.items() if p.endswith(('.py','.md')))+CAPS['inventory']
    metadata=meta+sum(v for k,v in CAPS.items() if k!='inventory')+8192
    future=dict(states=6*98304,steps=5*32768,scans=2*32767,nj=5120,formations=6144,
                generations=6144,inputs=114688,verification=262144)
    total=sources+metadata+sum(future.values())
    budget=dict(sources=sources,metadata=metadata,shared=5120+6144+6144+114688,
                total=total,success=total,failure=total,limits=dict(sources=174080,metadata=65536,
                shared=262144,total=4194304),future=future)
    budget['violations']=[k for k,v in budget['limits'].items() if budget[k]>v]
    tests=[n.name for n in ast.walk(ast.parse((ROOT/OWN[1]).read_text()))
           if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')]
    b=dict(version=a.VERSION,files=files,inventory_digest=a.s.digest(inv),interpreter=pin(Path(sys.executable)),
           tests=tests,budget=budget,caps=CAPS,main_authorized=False)
    print(json.dumps(budget));a.need(not budget['violations'],'PRESTART_BUDGET')
    a.need(len(a.s.raw(inv))<=CAPS['inventory'] and len(a.s.raw(b))<=CAPS['preregistration'],'BINDING_SIZE')
    OUT.mkdir();save('inventory',inv);save('preregistration',b)


def run():
    b=json.loads((OUT/'preregistration.json').read_bytes());check(b)
    a.need(a.s.digest(shared.inventory())==b['inventory_digest'],'CURRENT_INVENTORY')
    (OUT/'qualification.claim').open('xb').close()
    phase='QUALIFICATION';generated=[]
    try:
        with (OUT/'qualification.log').open('xb') as log:
            child=subprocess.Popen([sys.executable,'-m','unittest','tests.test_structure_av_sources','-v'],
                cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            left=CAPS['log'];overflow=False
            while True:
                chunk=child.stdout.read1(min(1024,left+1))
                if not chunk:break
                over=len(chunk)>left;log.write(chunk[:left]);left-=min(left,len(chunk))
                if over:overflow=True;child.kill();break
            code=child.wait();child.stdout.close()
        check(b);save('qualification',dict(status='QUALIFIED' if code==0 and not overflow else 'NOT_QUALIFIED',
            tests=len(b['tests']),test_calls=1,exit_code=code,log_complete=not overflow))
        a.need(code==0 and not overflow,'QUALIFICATION_STOP')
        phase='SOURCE_FILES';(OUT/'source.claim').open('xb').close()
        e=json.loads((OLD/'execution.json').read_bytes());seal=json.loads((OLD/'seal.json').read_bytes())
        v=json.loads((OLD/'verification.json').read_bytes())
        a.need(seal['execution_digest']==a.s.digest(e) and v['status']=='BINDING_VALID'
               and v['record_digest']==a.s.digest(seal),'HISTORICAL_ROOT')
        audio=ROOT/a.AUDIO;a.need(pin(audio)==[a.AUDIO_HASH,19200],'AUDIO_BINDING')
        dest=ROOT/a.DEST;dest.mkdir();proofs={}
        for name in ('q04','q05','q06'):
            source=next(x for x in e['sources'] if x['id']==name)
            old=next(x for x in seal['sources'] if x['id']==name)
            payload=a.s.render(source['recipe'],1920,1080)
            h=hashlib.sha256(payload).hexdigest()
            a.need(h==old['sha256'] and len(payload)==old['bytes'],'HISTORICAL_PAYLOAD')
            with (dest/(name+'.rgb')).open('xb') as f:f.write(payload)
            proofs[name]=dict(sha256=h,bytes=len(payload),source_digest=a.s.digest(source));generated.append(name)
            if name=='q06':
                a.cue_in_place(payload,1920,1080)
                with (dest/'q06-cue.rgb').open('xb') as f:f.write(payload)
                proofs['q06-cue']=dict(sha256=hashlib.sha256(payload).hexdigest(),bytes=len(payload),
                    parent_sha256=h,components=list(range(32)));generated.append('q06-cue')
            del payload
        record=dict(version=a.VERSION,files=proofs,execution_digest=a.s.digest(e),seal_digest=a.s.digest(seal),
                    manifest=asdict(a.manifest(proofs,b['inventory_digest'])))
        save('record',record);phase='VERIFY';(OUT/'verification.claim').open('xb').close()
        # Independent read-only checks: hash files, resolve historical recipe
        # bindings and manifest. No regeneration or receptor invocation.
        for name,p in proofs.items():a.need(pin(dest/(name+'.rgb'))==[p['sha256'],p['bytes']],'STORED_HASH')
        with (dest/'q06.rgb').open('rb') as original,(dest/'q06-cue.rgb').open('rb') as masked:
            for y in range(1080):
                src=original.read(5760);cue=masked.read(5760)
                if y<135:
                    a.need(cue[:4800]==src[:4800] and cue[4800:5280:3]==src[4800:5280:3]
                        and cue[4801:5280:3]==src[4801:5280:3] and not any(cue[4802:5280:3])
                        and not any(cue[5280:]),'CUE_PIXELS')
                else:a.need(not any(cue),'CUE_PIXELS')
        proof=a.verify(json.loads((OUT/'record.json').read_bytes()),e,seal);check(b);save('proof',proof)
        proof['cue_pixel_relation_checked']=True
        sizes={p.name:p.stat().st_size for p in OUT.iterdir() if p.is_file()}
        save('balance',dict(files=sizes,prebound=b['budget'],input_stock_bytes=24902400,
            planned_runtime_read_bytes=31180800,generated_rgb_files=4,gates=False))
        print(json.dumps(proof))
    except Exception:
        save('failure',dict(status='NOT_EVALUABLE',phase=phase,generated=generated,code='SOURCE_BINDING_FAILURE'))
        raise


if __name__=='__main__':{'prepare':prepare,'run':run}[sys.argv[1]]()
