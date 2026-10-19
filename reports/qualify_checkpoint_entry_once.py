"""Bind the new connector suite before its sole invocation; never run real inputs."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/checkpoint-entry-qualification-20260912-02'
OWN=['tools/_checkpoint_transfer_entry.py','tools/_checkpoint_transfer_budget.py',
     'tests/test_checkpoint_transfer_entry.py','reports/qualify_checkpoint_entry_once.py']

def raw(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode('ascii')
def identity(path):
    data=path.read_bytes();return dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())

def prepare():
    if OUT.exists():raise RuntimeError('qualification ID already used')
    old=json.loads((ROOT/'reports/memory-checkpoint-qualification-20260912-02/preregistration.json').read_bytes())
    files=dict(old['inventory']['files'])
    for name,bound in files.items():
        if identity(ROOT/name)!=bound:raise RuntimeError('qualified source changed: '+name)
    files.update({name:identity(ROOT/name) for name in OWN})
    inventory=dict(files=files)
    tests=[node.name for node in ast.walk(ast.parse((ROOT/OWN[2]).read_text()))
           if isinstance(node,ast.FunctionDef) and node.name.startswith('test_')]
    charged=list(dict.fromkeys(old['charged_sources']+OWN))
    references=[]
    for folder,names in [('memory-checkpoint-qualification-20260912-02',['preregistration.json','result.json','qualification.stderr']),
                          ('memory-checkpoint-focus-20260912-01',['preregistration.json','result.json','stderr.log'])]:
        for name in names:
            path=ROOT/'reports'/folder/name
            references.append(dict(path=path.relative_to(ROOT).as_posix(),**identity(path)))
    # Inventory bodies occur in the qualification, final binding and runtime preregistration.
    source_bytes=sum(files[n]['bytes'] for n in charged)+3*len(raw(inventory))
    source_bytes+=len(raw(old['inventory']))
    # Only the pure format budget module is evaluated here, before any test body.
    namespace={}
    exec(compile((ROOT/OWN[1]).read_text(),OWN[1],'exec'),namespace)
    budget=namespace['envelope'](source_bytes)
    reserves=dict(preregistration=24576,logs=8192,result=2048,report=4096,ledger=8192,claim=4)
    metadata=sum(reserves.values())+sum(ref['bytes'] for ref in references)
    # Referenced inventories belong to sources; their physical bytes remain in total.
    metadata-=len(raw(old['inventory']))
    qualification=dict(metadata=metadata,sources=source_bytes,shared=source_bytes,
        verification=0,total=metadata+source_bytes)
    violations=[k for k,cap in namespace['LIMITS'].items() if qualification[k]>cap]
    value=dict(status='READY' if not violations and not budget['violations'] else 'PRECONDITION_STOP',
        test_calls=0,tests=sorted(tests),inventory=inventory,charged_sources=charged,
        references=references,reserves=reserves,qualification_upper=qualification,
        runtime_upper=budget,source_charge=source_bytes,violations=violations,
        scope='New caller protocols only; native memory and prior process qualification not replayed.')
    if len(raw(value))>reserves['preregistration']:raise RuntimeError('complete preregistration exceeds bound')
    OUT.mkdir();(OUT/'preregistration.json').write_bytes(raw(value))
    print(json.dumps(dict(status=value['status'],tests=len(tests),qualification=qualification,
        runtime_violations=budget['violations'],violations=violations),indent=2))

def run():
    value=json.loads((OUT/'preregistration.json').read_bytes())
    if value['status']!='READY':raise RuntimeError('precondition not met; zero test calls')
    for name,bound in value['inventory']['files'].items():
        if identity(ROOT/name)!=bound:raise RuntimeError('source changed')
    with (OUT/'invocation.claim').open('xb') as f:f.write(b'once')
    with (OUT/'stdout.log').open('xb') as out,(OUT/'stderr.log').open('xb') as err:
        result=subprocess.run([sys.executable,'-m','unittest','tests.test_checkpoint_transfer_entry','-v'],
            cwd=ROOT,stdout=out,stderr=err,check=False)
    unchanged=all(identity(ROOT/n)==b for n,b in value['inventory']['files'].items())
    logs=sum((OUT/n).stat().st_size for n in ('stdout.log','stderr.log'))
    report=dict(status='QUALIFIED' if result.returncode==0 and unchanged and logs<=value['reserves']['logs'] else 'NOT_QUALIFIED',
        test_calls=1,exit_code=result.returncode,hashes_unchanged=unchanged,log_bytes=logs,
        gates=False,tests=value['tests'])
    (OUT/'result.json').write_bytes(raw(report));print(json.dumps(report,indent=2))

if __name__=='__main__':{'prepare':prepare,'run':run}[sys.argv[1]]()
