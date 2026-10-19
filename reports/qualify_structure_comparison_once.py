"""One neutral qualification; the sealed comparison remains separately gated."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import numpy as np
from tools import _structure_comparison as c
from tools import _structure_source_binding as s

ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'reports/s2oe/structure-location-source-seal-20260912-01'
Q=ROOT/'reports/s2oe/structure-location-comparison-qualification-20260912-01'
RUN=ROOT/'reports/s2oe/structure-location-comparison-20260912-01'
OWN=['tools/_structure_comparison.py','tools/_structure_comparison_verify.py',
     'tests/test_structure_comparison.py','reports/qualify_structure_comparison_once.py']


def pin(path):
    data=path.read_bytes();return [hashlib.sha256(data).hexdigest(),len(data)]


def collect():
    found={};pending=set(OWN)
    while pending:
        name=pending.pop()
        if name in found:continue
        found[name]=pin(ROOT/name)
        package=name[:-3].replace('/','.').split('.')[:-1]
        for n in ast.walk(ast.parse((ROOT/name).read_text(encoding='utf-8-sig'))):
            modules=[]
            if isinstance(n,ast.Import):modules=[x.name for x in n.names]
            if isinstance(n,ast.ImportFrom):
                prefix='.'.join(package[:len(package)-n.level+1]) if n.level else ''
                base='.'.join(x for x in (prefix,n.module) if x)
                modules=[base,*[base+'.'+x.name for x in n.names]]
            for module in modules:
                parts=module.split('.')
                if parts[0] not in ('tools','tests','reports','mcm_field_organism'):continue
                for i in range(1,len(parts)+1):
                    for path in ('/'.join(parts[:i])+'.py','/'.join(parts[:i])+'/__init__.py'):
                        if (ROOT/path).is_file():pending.add(path)
    old=json.loads((OLD/'preregistration.json').read_bytes())
    for name,p in old['files'].items():
        c.need(pin(ROOT/name)==[p['sha256'],p['bytes']],'HISTORICAL_SOURCE_CHANGED')
        found[name]=pin(ROOT/name)
    for p in OLD.iterdir():
        if p.is_file():found[p.relative_to(ROOT).as_posix()]=pin(p)
    return found


def check(files):
    for name,p in files.items():c.need(pin(ROOT/name)==p,'ACTIVE_SOURCE_CHANGED')


def prepare():
    c.need(not Q.exists() and not RUN.exists(),'OUTPUT_EXISTS')
    files=collect()
    historical_metadata=sum(p[1] for n,p in files.items() if n.startswith(OLD.relative_to(ROOT).as_posix()))
    # Shared neutral fixture: one full native record, one expected failure.
    reserves=dict(binding=8192,log=4096,result=1024,report=4096,balance=2048,
        native_evaluation=16384,native_balances=4096,native_failure=4096,
        envelope=1024,claims=20)
    metadata=historical_metadata+sum(reserves.values())
    reference_bytes=sum(p[1] for p in files.values())
    total=reference_bytes+sum(reserves.values())+1048576+1048576+8192
    budget=dict(metadata=metadata,metadata_limit=65536,total=total,total_limit=4194304,
                reference_bytes=reference_bytes,reserves=reserves,native_record=1048576,
                native_partial=1048576,verification=8192)
    tests=[n.name for n in ast.walk(ast.parse((ROOT/OWN[2]).read_text())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')]
    binding=dict(files=files,budget=budget,tests=tests,python=sys.version,numpy=np.__version__,
        interpreter=pin(Path(sys.executable)),run_id=RUN.name,main_authorized=False,
        work=dict(differences=19008,verification_terms=19008,verification_sums=88,
                  verification_exact_equalities=864,primary_exact_equalities=864,criteria=24))
    c.need(len(s.raw(binding))<=8192,'BINDING_LIMIT')
    c.need(metadata<=65536 and total<=4194304,'QUALIFICATION_BUDGET')
    Q.mkdir();c.publish(Q/'preregistration.json',binding)
    print(json.dumps(budget))


def qualify():
    b=json.loads((Q/'preregistration.json').read_bytes());check(b['files'])
    c.need(pin(Path(sys.executable))==b['interpreter'] and np.__version__==b['numpy'],'ENVIRONMENT')
    with (Q/'qualification.claim').open('xb') as f:f.write(b'once\n')
    env=dict(os.environ,STRUCTURE_NEUTRAL_OUT=str(Q/'neutral'))
    with (Q/'qualification.log').open('xb') as log:
        result=subprocess.run([sys.executable,'-m','unittest','tests.test_structure_comparison','-v'],
            cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
    check(b['files'])
    files={p.relative_to(Q).as_posix():p.stat().st_size for p in Q.rglob('*') if p.is_file()}
    meta=sum(n for name,n in files.items() if not name.endswith(('record.json','partial.json','verification.json')))
    old_meta=sum(p[1] for n,p in b['files'].items() if n.startswith(OLD.relative_to(ROOT).as_posix()))
    total=b['budget']['reference_bytes']+sum(files.values())+7168
    violations=[]
    if meta+old_meta+7168>65536:violations.append('METADATA')
    if total>4194304:violations.append('TOTAL')
    if (Q/'qualification.log').stat().st_size>4096:violations.append('LOG_RESERVE')
    ok=result.returncode==0 and not violations
    c.publish(Q/'result.json',dict(status='QUALIFIED' if ok else 'NOT_QUALIFIED',test_calls=1,
        tests=len(b['tests']),exit_code=result.returncode,sources_unchanged=True,gates=False))
    c.publish(Q/'balance.json',dict(files=files,metadata_with_reserve=meta+old_meta+7168,
        total_with_reserve=total,remaining_result_balance_report_reserve=7168,violations=violations))
    print(json.dumps(dict(status='QUALIFIED' if ok else 'NOT_QUALIFIED',violations=violations,total=total)))
    if not ok:raise SystemExit('QUALIFICATION_STOP_NO_RETRY')


def bind():
    b=json.loads((Q/'preregistration.json').read_bytes());check(b['files'])
    c.need(json.loads((Q/'result.json').read_bytes())['status']=='QUALIFIED','QUALIFICATION_REQUIRED')
    files=dict(b['files'])
    for p in Q.rglob('*'):
        if p.is_file():files[p.relative_to(ROOT).as_posix()]=pin(p)
    e=json.loads((OLD/'execution.json').read_bytes());ev=json.loads((OLD/'evaluation.json').read_bytes())
    seal=json.loads((OLD/'seal.json').read_bytes())
    oldproof=json.loads((OLD/'verification.json').read_bytes())
    c.need(oldproof['status']=='BINDING_VALID' and oldproof['record_digest']==s.digest(seal),'SOURCE_PROOF')
    binding=dict(version=c.VERSION,execution=e,seal=seal,pairs=ev['pairs'],evaluation_digest=s.digest(ev),
        references=files,run_id=RUN.name,output=RUN.relative_to(ROOT).as_posix(),authorized=False,
        python=sys.version,numpy=np.__version__,interpreter=pin(Path(sys.executable)))
    size=len(s.raw(binding));c.need(size<=12288,'MAIN_BINDING_LIMIT')
    budget=c.ledger(RUN,sum(p[1] for p in files.values())+size,c.CAPS)
    c.need(not RUN.exists() and not budget['violations'],'MAIN_BUDGET')
    c.publish(Q/'main-binding.json',binding)
    print(json.dumps(dict(binding=pin(Q/'main-binding.json'),worst=budget,authorized=False)))


def run():
    # A separate future authorization must name this exact bound attempt.
    b=json.loads((Q/'main-binding.json').read_bytes());check(b['references'])
    auth=json.loads((Q/'authorization.json').read_bytes())
    c.need(auth==dict(run_id=RUN.name,binding_sha256=pin(Q/'main-binding.json')[0],authorized=True),'AUTHORIZATION')
    c.need(pin(Path(sys.executable))==b['interpreter'] and np.__version__==b['numpy'],'ENVIRONMENT')
    ev=json.loads((OLD/'evaluation.json').read_bytes())
    reference=sum(p[1] for p in b['references'].values())+pin(Q/'main-binding.json')[1]+pin(Q/'authorization.json')[1]
    c.MAIN_GATE=True
    try:c.execute(b,RUN,reference,lambda src:s.render(src['recipe'],1920,1080),ev)
    finally:c.MAIN_GATE=False


if __name__=='__main__':
    {'prepare':prepare,'qualify':qualify,'bind':bind,'run':run}[sys.argv[1]]()
