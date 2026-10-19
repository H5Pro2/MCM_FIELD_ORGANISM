"""One neutral qualification followed by one receptor-free source seal."""
import ast
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import traceback
from tools import _structure_source_binding as s

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/s2oe/structure-location-source-seal-20260912-01'
FILES=['tools/_structure_source_binding.py','tests/test_structure_source_binding.py',
       'reports/seal_structure_sources_once.py','docs/STRUKTUR_LAGE_GEGENPROBE_PLAN.md']
RESERVES=dict(preregistration=12288,execution=12288,evaluation=8192,log=8192,
              result=1024,failure=8192,balance=1024,report=4096,claims=15)


def pin(path):
    b=path.read_bytes();return dict(sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))


def save(name,value):
    # Exclusive temporary write and rename, same repository publication pattern.
    path=OUT/name;temporary=OUT/(name+'.tmp')
    s.need(not path.exists(),'OUTPUT_EXISTS')
    with temporary.open('xb') as f:f.write(s.raw(value))
    temporary.rename(path)


def check(binding):
    for name,value in binding['files'].items():s.need(pin(ROOT/name)==value,'SOURCE_CHANGED')


def prepare():
    s.need(not OUT.exists(),'OUTPUT_EXISTS')
    files=list(FILES)
    for name in ('tools/__init__.py','tests/__init__.py','reports/__init__.py'):
        if (ROOT/name).exists():
            tree=ast.parse((ROOT/name).read_text(encoding='utf-8-sig'))
            s.need(not any(isinstance(n,(ast.Import,ast.ImportFrom)) for n in ast.walk(tree)),'UNBOUND_PACKAGE_IMPORT')
            files.append(name)
    inventory={name:pin(ROOT/name) for name in files}
    execution,evaluation=s.plans()
    budget=s.budget(sum(p['bytes'] for p in inventory.values()),sum(RESERVES.values()),16384,8192)
    s.need(not budget['violations'],'PRESTART_BUDGET')
    tests=[n.name for n in ast.walk(ast.parse((ROOT/FILES[1]).read_text())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')]
    binding=dict(version=s.VERSION,files=inventory,tests=tests,reserves=RESERVES,budget=budget,
        execution_digest=s.digest(execution),evaluation_digest=s.digest(evaluation),
        python=sys.version,executable=pin(Path(sys.executable)),platform=platform.platform(),
        qualification_id='structure-location-source-qualification-20260912-01',
        allowed_calls=dict(generation=14,receptor=0,projection=0,distances=0,verification=1),
        raw_window_bytes=6220800,raw_window_count=1,raw_row_bytes_max=5760,
        planned_generated_bytes=87091200,raw_storage=False,
        future_work=evaluation['work'])
    s.need(len(s.raw(binding))<=RESERVES['preregistration'],'BINDING_LIMIT')
    s.need(len(s.raw(execution))<=RESERVES['execution'] and len(s.raw(evaluation))<=RESERVES['evaluation'],'PLAN_LIMIT')
    OUT.mkdir()
    save('preregistration.json',binding);save('execution.json',execution);save('evaluation.json',evaluation)
    print(json.dumps(budget))


def run():
    b=json.loads((OUT/'preregistration.json').read_bytes());check(b)
    s.need(pin(Path(sys.executable))==b['executable'],'INTERPRETER_CHANGED')
    e=json.loads((OUT/'execution.json').read_bytes());v=json.loads((OUT/'evaluation.json').read_bytes())
    s.need(s.digest(e)==b['execution_digest'] and s.digest(v)==b['evaluation_digest'],'PLAN_CHANGED')
    with (OUT/'qualification.claim').open('xb') as f:f.write(b'once\n')
    phase='QUALIFICATION';proofs=[]
    try:
        with (OUT/'qualification.log').open('xb') as log:
            result=subprocess.run([sys.executable,'-m','unittest','tests.test_structure_source_binding','-v'],
                cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        check(b)
        ok=result.returncode==0 and (OUT/'qualification.log').stat().st_size<=RESERVES['log']
        save('qualification.json',dict(status='QUALIFIED' if ok else 'NOT_QUALIFIED',calls=1,
            tests=len(b['tests']),exit_code=result.returncode,log=pin(OUT/'qualification.log'),sources_unchanged=True))
        s.need(ok,'QUALIFICATION_STOP')
        phase='GENERATION'
        with (OUT/'seal.claim').open('xb') as f:f.write(b'once\n')
        for source in e['sources']:
            payload=s.render(source['recipe'],e['width'],e['height'])
            proofs.append(dict(id=source['id'],source_digest=s.digest(source),bytes=len(payload),
                               sha256=hashlib.sha256(payload).hexdigest()))
            del payload
        groups={}
        for p in proofs:groups.setdefault(p['sha256'],[]).append(p['id'])
        record=dict(version=s.VERSION,execution_digest=s.digest(e),evaluation_digest=s.digest(v),
            generated=len(proofs),sources=proofs,collisions=[x for x in groups.values() if len(x)>1],
            environment_binding=s.digest(b),raw_storage=False)
        s.need(len(s.raw(record))<=16384,'RECORD_LIMIT')
        save('seal.json',record)
        phase='VERIFY'
        with (OUT/'verification.claim').open('xb') as f:f.write(b'once\n')
        check(b)
        stored=json.loads((OUT/'seal.json').read_bytes())
        verification=s.verify(stored,e,v)
        s.need(len(s.raw(verification))<=8192,'VERIFICATION_LIMIT')
        save('verification.json',verification)
        print(json.dumps(dict(status=verification['status'],generated=14,collisions=record['collisions'])))
    except Exception as exc:
        save('failure.json',dict(status='NOT_QUALIFIED' if phase=='QUALIFICATION' else 'NOT_EVALUABLE',
            phase=phase,generated=len(proofs),sources=proofs,error=str(exc),traceback=traceback.format_exc()))
        raise
    finally:
        s.GATE=False
        sizes={p.name:p.stat().st_size for p in OUT.iterdir() if p.is_file()}
        metadata=sum(n for name,n in sizes.items() if name not in ('seal.json','verification.json'))
        balance=s.budget(sum(x['bytes'] for x in b['files'].values()),metadata+1024+4096,
                         sizes.get('seal.json',0),sizes.get('verification.json',0))
        balance.update(files=sizes,remaining_balance_report_reserve=5120,gates=False)
        save('balance.json',balance)
        s.need(not balance['violations'],'FINAL_BUDGET')


if __name__=='__main__':
    {'prepare':prepare,'run':run}[sys.argv[1]]()
