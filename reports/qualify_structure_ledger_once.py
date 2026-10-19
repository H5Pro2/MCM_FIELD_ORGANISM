"""Focused administrative correction; never repeats functional tests."""
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from reports import qualify_structure_comparison_once as old
from tools import _structure_comparison as c
from tools import _structure_comparison_ledger as l
from tools import _structure_source_binding as s

ROOT=old.ROOT
Q=ROOT/'reports/s2oe/structure-location-ledger-qualification-20260912-01'
RUN=old.RUN
RESERVES={'preregistration.json':16384,'qualification.log':4096,'result.json':1024,
          'balance.json':2048,'main-binding.json':4096,'qualification.claim':5,'authorization.json':512}
REPORT_RESERVE=8192


def descriptor(path):
    name=path.relative_to(ROOT).as_posix();h,n=old.pin(path)
    return dict(path=name,kind=l.classify(name),bytes=n,sha256=h)


def signature(path):
    functions={}
    for node in ast.parse(path.read_text(encoding='utf-8-sig')).body:
        if not isinstance(node,ast.FunctionDef) or node.name=='ledger':continue
        if node.name=='execute':
            node.body=[n for n in node.body if not any(
                (isinstance(x,ast.Constant) and x.value=='PREFLIGHT_LIMIT') or
                (isinstance(x,ast.Name) and x.id=='alternatives')
                for x in ast.walk(n))]
        functions[node.name]=ast.dump(node,include_attributes=False)
    return functions


def check(refs):
    for r in refs:
        c.need(descriptor(ROOT/r['path'])==r,'REFERENCE_CHANGED')


def reference_binding(refs):
    return dict(version=l.VERSION,files=refs,report_reserve=REPORT_RESERVE)


def prepare():
    c.need(not (Q/'preregistration.json').exists() and not RUN.exists(),'OUTPUT_EXISTS')
    previous=json.loads((old.Q/'preregistration.json').read_bytes())
    archive=Q/'previous_comparison.py'
    c.need(old.pin(archive)==previous['files']['tools/_structure_comparison.py'],'ARCHIVE_HASH')
    for name,value in previous['files'].items():
        if name!='tools/_structure_comparison.py':c.need(old.pin(ROOT/name)==value,'HISTORICAL_CHANGED')
    c.need(signature(archive)==signature(ROOT/'tools/_structure_comparison.py'),'FUNCTIONAL_CHANGE')
    files=old.collect()
    for name in ('tools/_structure_comparison_ledger.py','tests/test_structure_ledger.py',
                 'reports/qualify_structure_ledger_once.py','reports/s2oe/STRUCTURE_COMPARISON_CONNECTION_RESULT.md'):
        files[name]=old.pin(ROOT/name)
    for p in old.Q.rglob('*'):
        # Superseded, never-used main binding is archive, not a prerequisite.
        if p.is_file() and p.name!='main-binding.json':files[p.relative_to(ROOT).as_posix()]=old.pin(p)
    files[archive.relative_to(ROOT).as_posix()]=old.pin(archive)
    refs=[descriptor(ROOT/n) for n in sorted(files)]
    prospective=refs+[dict(path=(Q/name).relative_to(ROOT).as_posix(),kind=l.classify(name),
                          bytes=size,sha256='RESERVED') for name,size in RESERVES.items()]
    bills={name:c.ledger(RUN,reference_binding(prospective),caps) for name,caps in l.alternatives(c.CAPS).items()}
    retrospective=dict(basis='retrospective',differences=32256,verification_terms=51264,
        verification_sums=222,verification_exact_equalities=2304,primary_exact_equalities=1440,
        receptor_calls=15,projection_calls=15,criterion_evaluations=120,verification_attempts=7)
    work=l.work(l.REAL_WORK,l.VERIFY_WORK,retrospective)
    tests=[n.name for n in ast.walk(ast.parse((ROOT/'tests/test_structure_ledger.py').read_text()))
           if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')]
    b=dict(version=l.VERSION,references=refs,reserves=RESERVES,report_reserve=REPORT_RESERVE,
        alternatives=bills,tests=tests,work=work,
        new_qualification_work=dict(basis='prospective',differences=0,receptor_calls=0,
            projection_calls=0,verification_terms=0,functional_tests_repeated=0),
        limits=l.LIMITS,python=sys.version,numpy=old.np.__version__,interpreter=old.pin(Path(sys.executable)),
        functional_signature_unchanged=True,authorization=False)
    c.need(len(s.raw(b))<=RESERVES['preregistration.json'],'BINDING_LIMIT')
    c.need(all(not x['violations'] for x in bills.values()),'PRESTART_LIMIT')
    c.publish(Q/'preregistration.json',b)
    print(json.dumps(dict(bytes=len(s.raw(b)),alternatives=bills)))


def qualify():
    b=json.loads((Q/'preregistration.json').read_bytes());check(b['references'])
    with (Q/'qualification.claim').open('xb') as f:f.write(b'once\n')
    with (Q/'qualification.log').open('xb') as f:
        p=subprocess.run([sys.executable,'-m','unittest','tests.test_structure_ledger','-v'],
                         cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
    check(b['references'])
    ok=p.returncode==0 and (Q/'qualification.log').stat().st_size<=RESERVES['qualification.log']
    c.publish(Q/'result.json',dict(status='QUALIFIED' if ok else 'NOT_QUALIFIED',calls=1,
        tests=len(b['tests']),exit_code=p.returncode,log=old.pin(Q/'qualification.log'),
        sources_unchanged=True,gates=False,scope='LEDGER_ONLY'))
    if not ok:raise SystemExit('STOP_NO_RETRY')


def bind():
    b=json.loads((Q/'preregistration.json').read_bytes());check(b['references'])
    c.need(json.loads((Q/'result.json').read_bytes())['status']=='QUALIFIED','QUALIFICATION')
    c.need(not RUN.exists(),'OUTPUT_EXISTS')
    value=dict(version=l.VERSION,run_id=RUN.name,authorized=False,
        prerequisite=descriptor(Q/'preregistration.json'),qualification=descriptor(Q/'result.json'),
        log=descriptor(Q/'qualification.log'),claim=descriptor(Q/'qualification.claim'),
        execution_path=(old.OLD/'execution.json').relative_to(ROOT).as_posix(),
        evaluation_path=(old.OLD/'evaluation.json').relative_to(ROOT).as_posix(),
        seal_path=(old.OLD/'seal.json').relative_to(ROOT).as_posix())
    c.need(len(s.raw(value))<=RESERVES['main-binding.json'],'MAIN_BINDING_LIMIT')
    c.publish(Q/'main-binding.json',value)
    refs=list(b['references'])
    refs.extend(descriptor(Q/name) for name in RESERVES if (Q/name).exists())
    refs.extend(dict(path=(Q/name).relative_to(ROOT).as_posix(),kind='metadata',bytes=size,sha256='RESERVED')
                for name,size in RESERVES.items() if not (Q/name).exists())
    bills={name:c.ledger(RUN,reference_binding(refs),caps) for name,caps in l.alternatives(c.CAPS).items()}
    c.need(all(not x['violations'] for x in bills.values()),'MAIN_LIMIT')
    c.publish(Q/'balance.json',dict(alternatives=bills,report_reserve=8192,gates=False))
    c.need((Q/'balance.json').stat().st_size<=2048,'BALANCE_LIMIT')
    print(json.dumps(dict(main_binding=old.pin(Q/'main-binding.json'),alternatives=bills)))


def run():
    main=json.loads((Q/'main-binding.json').read_bytes())
    check([main[k] for k in ('prerequisite','qualification','log','claim')])
    prereg=json.loads((Q/'preregistration.json').read_bytes());check(prereg['references'])
    c.need(json.loads((Q/'result.json').read_bytes())['status']=='QUALIFIED','QUALIFICATION')
    auth=json.loads((Q/'authorization.json').read_bytes())
    c.need(auth==dict(run_id=RUN.name,binding_sha256=old.pin(Q/'main-binding.json')[0],authorized=True),'AUTHORIZATION')
    c.need(old.pin(Path(sys.executable))==prereg['interpreter'] and old.np.__version__==prereg['numpy'],'ENVIRONMENT')
    refs=list(prereg['references'])
    refs.extend(descriptor(Q/name) for name in RESERVES)
    e=json.loads((ROOT/main['execution_path']).read_bytes());ev=json.loads((ROOT/main['evaluation_path']).read_bytes())
    seal=json.loads((ROOT/main['seal_path']).read_bytes())
    bound=dict(version=c.VERSION,execution=e,seal=seal,pairs=ev['pairs'],evaluation_digest=s.digest(ev),
               main_binding_sha256=old.pin(Q/'main-binding.json')[0])
    c.MAIN_GATE=True
    try:c.execute(bound,RUN,reference_binding(refs),lambda src:s.render(src['recipe'],1920,1080),ev)
    finally:c.MAIN_GATE=False


if __name__=='__main__':
    {'prepare':prepare,'qualify':qualify,'bind':bind,'run':run}[sys.argv[1]]()
