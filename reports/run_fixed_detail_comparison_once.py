"""Qualified, bound, one-shot detail comparison; no automatic retry."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from tools import _s2oe_detail_closure as c

ROOT=Path(__file__).resolve().parents[1]
Q=ROOT/'reports/s2oe/fixed-detail-closure-qualification-20260912-01'
RUN=ROOT/'reports/s2oe/fixed-detail-comparison-20260912-01'
OLD=ROOT/'reports/s2oe/fixed-detail-qualification-20260912-01'
OWN=('reports/run_fixed_detail_comparison_once.py','tools/_s2oe_detail_closure.py','tests/test_s2oe_detail_closure.py')


def raw(x):return c.d.raw(x)
def pin(path):
    data=path.read_bytes();return [hashlib.sha256(data).hexdigest(),len(data)]
def save(path,x):c.publish(path,x)


def inventory():
    pending=set(OWN);found={}
    while pending:
        name=pending.pop()
        if name in found:continue
        data=(ROOT/name).read_bytes();found[name]=pin(ROOT/name)
        package=name[:-3].replace('/','.').split('.')[:-1]
        for n in ast.walk(ast.parse(data.decode('utf-8-sig'))):
            names=[]
            if isinstance(n,ast.Import):names=[x.name for x in n.names]
            if isinstance(n,ast.ImportFrom):
                prefix='.'.join(package[:len(package)-n.level+1]) if n.level else ''
                base='.'.join(x for x in (prefix,n.module) if x);names=[base,*[base+'.'+x.name for x in n.names]]
            for mod in names:
                parts=mod.split('.')
                if parts[0] not in ('tools','mcm_field_organism','tests','reports'):continue
                for i in range(1,len(parts)+1):
                    for path in ('/'.join(parts[:i])+'.py','/'.join(parts[:i])+'/__init__.py'):
                        if (ROOT/path).is_file():pending.add(path)
    return found


def check(files):
    for name,value in files.items():c.d.need(pin(ROOT/name)==value,'BOUND_SOURCE_CHANGED')


def prepare():
    c.d.need(not RUN.exists(),'OUTPUT_EXISTS');Q.mkdir(exist_ok=False)
    files=inventory();old=json.loads((OLD/'preregistration.json').read_bytes());check(old['files'])
    previous=json.loads((OLD/'result.json').read_bytes())
    c.d.need(previous['status']=='QUALIFIED' and previous['tests']['tests']==16,'ADAPTER_NOT_QUALIFIED')
    files.update(old['files'])
    files.update({p.relative_to(ROOT).as_posix():pin(p) for p in OLD.iterdir() if p.is_file()})
    total=sum(n for h,n in files.values())
    alternatives={name:c.ledger(RUN,total+65536,choices) for name,choices in (
        ('success',{p:c.CAPS[p] for p in c.CAPS if p not in ('partial.json','failure.json')}),
        ('failure',{p:n for p,n in c.CAPS.items()}))}
    value=dict(files=files,comparison=old['comparison'],alternatives=alternatives,
        tests=[n.name for n in ast.walk(ast.parse((ROOT/OWN[2]).read_bytes())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')],
        qualification_reserve=65536,python=sys.version,real_media=False)
    save(Q/'preregistration.json',value)
    print(json.dumps(dict(binding_bytes=len(raw(value)),alternatives=alternatives)))
    c.d.need(len(raw(value))<=24576 and all(not x['violations'] for x in alternatives.values()),'PRESTART_LIMIT')


def qualify():
    b=json.loads((Q/'preregistration.json').read_bytes());check(b['files'])
    with (Q/'qualification.claim').open('xb') as f:f.write(b'once\n')
    with (Q/'qualification.log').open('xb') as log:
        p=subprocess.run([sys.executable,'-m','unittest','tests.test_s2oe_detail_closure','-v'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    ok=p.returncode==0 and (Q/'qualification.log').stat().st_size<=32768
    check(b['files'])
    save(Q/'result.json',dict(status='QUALIFIED' if ok else 'NOT_QUALIFIED',test_calls=1,test_groups=8,
        exit_code=p.returncode,log=pin(Q/'qualification.log'),sources_unchanged=True,gates=False))
    if not ok:raise SystemExit('QUALIFICATION_STOP')


def bind():
    old=json.loads((Q/'preregistration.json').read_bytes());check(old['files'])
    c.d.need(json.loads((Q/'result.json').read_bytes())['status']=='QUALIFIED','QUALIFICATION_REQUIRED')
    files=dict(old['files']);files.update({p.relative_to(ROOT).as_posix():pin(p) for p in Q.iterdir() if p.is_file()})
    value=dict(old['comparison'],code={p:v for p,v in files.items() if p.endswith('.py')},references=files,
        run_id=RUN.name,output=RUN.relative_to(ROOT).as_posix(),closure_version=c.VERSION,authorized_once=True)
    total=sum(n for h,n in files.values())+len(raw(value))
    c.d.need(not RUN.exists() and not c.ledger(RUN,total,dict(c.CAPS))['violations'],'MAIN_BINDING_LIMIT')
    save(Q/'main-binding.json',value)
    print(json.dumps(dict(binding_sha256=pin(Q/'main-binding.json')[0],reference_bytes=total,
        worst=c.ledger(RUN,total,dict(c.CAPS)))))


def run():
    b=json.loads((Q/'main-binding.json').read_bytes());check(b['references'])
    c.d.need(b['authorized_once'] and b['run_id']==RUN.name and b['closure_version']==c.VERSION,'AUTHORIZATION_INVALID')
    reference=sum(n for h,n in b['references'].values())+(Q/'main-binding.json').stat().st_size
    c.execute(b,RUN,reference)
    print('RECORDING_COMPLETE / EVIDENCE_VALID')


if __name__=='__main__':{'prepare':prepare,'qualify':qualify,'bind':bind,'run':run}[sys.argv[1]]()
