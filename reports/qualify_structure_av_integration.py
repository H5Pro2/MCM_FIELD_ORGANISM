"""Bind new composition and execute its neutral suite once, no caller media."""
import ast
from dataclasses import asdict,replace
import json
import os
from pathlib import Path
import subprocess
import sys
from tools import _structure_av_integration as x

s,b=x.s,x.b
ROOT=b.ROOT
OUT=ROOT/'reports/s2oe/structure-av-integration-qualification-20260912-03'
SOURCE=ROOT/'reports/s2oe/structure-av-source-binding-20260912-02'
DIRECT=ROOT/'reports/s2oe/structure-location-chain-20260912-01'
FILES=('tools/_structure_av_integration.py','tests/test_structure_av_closure.py','reports/qualify_structure_av_integration.py')


def write(name,value):
    s.prior.save(OUT/name,value)


def prepare():
    s.need(not OUT.exists(),'OUTPUT_EXISTS')
    inv=s.inventory();source=s.read_json(SOURCE/'record.json')
    m=b.decode_manifest(source['manifest'])
    m=b.build_manifest('structure-system-pending-01',m.events,b.digest(inv['ob']))
    paths=set(s.OWN)|set(FILES)
    refs=[s.file_reference('sources',ROOT/p) for p in sorted(paths)]
    s.need(b.canonical(s.read_json(SOURCE/'inventory.json'))==b.canonical(inv),'CURRENT_INVENTORY')
    refs.append(s.file_reference('sources',SOURCE/'inventory.json'))
    for name in ('record.json','proof.json','qualification.json','preregistration.json'):
        refs.append(s.file_reference('metadata',SOURCE/name))
    q=ROOT/'reports/s2oc/s2oc-shared-closure-qualification-20260910-03'
    for name in ('package.json','qualification.zip'):refs.append(s.file_reference('metadata',q/name))
    qref=next(r for r in refs if r[1]==(q/'package.json').relative_to(ROOT).as_posix())
    # Actual references only. Future qualification output is charged as reserve,
    # not disguised as resolvable files or a pre-existing successful result.
    reserves=dict(preregistration=12288,result=1024,log=4096,report=512,admission=4096,final_common=8192)
    common=s.build_common(m,inv,refs,qref)
    # The common object is already physically included by shared.ledger().
    # Reserve only its possible growth, not a second copy of that same file.
    reserves['final_common']=max(0,8192-len(b.canonical(common)))
    external=sum((DIRECT/p).stat().st_size for p in ('record.json','verification.json'))
    bound=x.envelope(common,external)
    for row in bound['positions']:
        for key in ('metadata','total'):row['totals'][key]+=sum(reserves.values())
        row['violations']=[k for k,n in row['totals'].items() if n>b.LIMITS[k]]
    bound['violations']=[row for row in bound['positions'] if row['violations']]
    print(json.dumps(bound))
    s.need(not bound['violations'],'PRESTART_LIMIT')
    pins={p:s.file_reference('sources',ROOT/p)[2:] for p in paths}
    tests=[n.name for n in ast.walk(ast.parse((ROOT/FILES[1]).read_text()))
           if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')]
    binding=dict(version=x.VERSION,pins=pins,budget=bound,tests=tests,reserves=reserves,
                 main_authorized=False,inventory_digest=b.digest(inv),common=common)
    s.need(len(b.canonical(binding))<=12288,'BINDING_LIMIT')
    OUT.mkdir();write('preregistration.json',binding)


def qualify():
    p=s.read_json(OUT/'preregistration.json')
    for path,pin in p['pins'].items():s.need(s.file_reference('sources',ROOT/path)[2:]==pin,'SOURCE_CHANGED')
    (OUT/'qualification.claim').open('xb').close()
    with (OUT/'qualification.log').open('xb') as log:
        child=subprocess.Popen([sys.executable,'-m','unittest','tests.test_structure_av_closure','-v'],cwd=ROOT,
            env=dict(os.environ,STRUCTURE_AV_QUAL=str(OUT),STRUCTURE_AV_INVENTORY=str(SOURCE/'inventory.json')),
            stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        left=4096;over=False
        while True:
            chunk=child.stdout.read1(min(left+1,1024))
            if not chunk:break
            overflow=len(chunk)>left;log.write(chunk[:left]);left-=min(left,len(chunk))
            if overflow:over=True;child.kill();break
        code=child.wait();child.stdout.close()
    for path,pin in p['pins'].items():s.need(s.file_reference('sources',ROOT/path)[2:]==pin,'SOURCE_CHANGED')
    result=dict(status='QUALIFIED' if code==0 and not over else 'NOT_QUALIFIED',test_calls=1,
                tests=len(p['tests']),exit_code=code,diagnostic_complete=not over,gates=False)
    write('result.json',result);print(json.dumps(result))


def bind():
    q=s.read_json(OUT/'result.json');s.need(q['status']=='QUALIFIED','QUALIFICATION_REQUIRED')
    prereg=s.read_json(OUT/'preregistration.json')
    for path,pin in prereg['pins'].items():s.need(s.file_reference('sources',ROOT/path)[2:]==pin,'SOURCE_CHANGED')
    inv=s.read_json(SOURCE/'inventory.json');old=prereg['common']
    manifest=b.decode_manifest(old['manifest'])
    refs=list(old['references'])
    for name in ('preregistration.json','result.json','qualification.log'):
        refs.append(s.file_reference('metadata',OUT/name))
    common=s.build_common(manifest,inv,refs,old['qualification'])
    s.validate_common(common,inv,qualified=True)
    cp=OUT/'common.json';s.need(len(b.canonical(common))<=8192,'COMMON_LIMIT')
    s.need(not (ROOT/'reports/s2oe/structure-av-system-20260912-01').exists(),'OUTPUT_USED')
    permit=dict(version=x.VERSION,authorized=False,neutral=False,run_id=manifest.run_id,
        output='reports/s2oe/structure-av-system-20260912-01',chain=0,source_indices=[3,4,5],
        files={k:x.pin(p) for k,p in dict(inventory=SOURCE/'inventory.json',direct=DIRECT/'record.json',
             direct_proof=DIRECT/'verification.json',qualification=OUT/'result.json').items()})
    permit['files']['common']=dict(path=cp.relative_to(ROOT).as_posix(),sha256=s.sha(b.canonical(common)),bytes=len(b.canonical(common)))
    s.need(len(b.canonical(permit))<=4096,'ADMISSION_LIMIT')
    bound=x.envelope(common,402945+len(b.canonical(permit)))
    s.need(not bound['violations'],'FINAL_BINDING_LIMIT')
    write('common.json',common);write('admission.json',permit)
    print(json.dumps(dict(admission_digest=s.sha(b.canonical(permit)),budget=bound,main_authorized=False)))


if __name__=='__main__':{'prepare':prepare,'qualify':qualify,'bind':bind}[sys.argv[1]]()
