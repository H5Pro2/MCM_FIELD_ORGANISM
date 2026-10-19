"""One qualified offline PPB table, without perception or memory updates."""
import ast
import json
import subprocess
import sys
import traceback
from pathlib import Path
from tools import _structure_ppb_table as p

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/s2oe/structure-location-ppb-20260912-01'
PARENT=ROOT/'reports/s2oe/structure-location-comparison-20260912-01'
SEALED=ROOT/'reports/s2oe/structure-location-source-seal-20260912-01'
RULE=ROOT/'reports/s2oe/visual-transition-e03-e04-20260912-03/binding.json'
OWN=['reports/run_structure_ppb_once.py','tools/_structure_ppb_table.py','tests/test_structure_ppb_table.py']
CAPS={'preregistration.json':12288,'qualification.log':4096,'qualification.json':1024,
      'table.json':16384,'verification.json':2048,'failure.json':8192,'balance.json':2048,
      'qualification.claim':5,'calculation.claim':5,'verification.claim':5}


def pin(path):
    import hashlib
    data=path.read_bytes();return [hashlib.sha256(data).hexdigest(),len(data)]


def save(name,value):
    path=OUT/name;tmp=OUT/(name+'.tmp')
    p.need(not path.exists(),'OUTPUT_EXISTS')
    with tmp.open('xb') as f:f.write(p.s.raw(value))
    tmp.rename(path)


def inventory():
    pending=set(OWN+['tools/_s2jw_default_live_profile.py']);files={}
    while pending:
        name=pending.pop()
        if name in files:continue
        files[name]=pin(ROOT/name);package=name[:-3].replace('/','.').split('.')[:-1]
        for n in ast.walk(ast.parse((ROOT/name).read_text(encoding='utf-8-sig'))):
            modules=[]
            if isinstance(n,ast.Import):modules=[x.name for x in n.names]
            if isinstance(n,ast.ImportFrom):
                prefix='.'.join(package[:len(package)-n.level+1]) if n.level else ''
                base='.'.join(x for x in (prefix,n.module) if x);modules=[base,*[base+'.'+x.name for x in n.names]]
            for module in modules:
                parts=module.split('.')
                if parts[0] not in ('tools','reports','tests','mcm_field_organism'):continue
                for i in range(1,len(parts)+1):
                    for path in ('/'.join(parts[:i])+'.py','/'.join(parts[:i])+'/__init__.py'):
                        if (ROOT/path).is_file():pending.add(path)
    for path in (PARENT/'record.json',PARENT/'verification.json',SEALED/'execution.json',SEALED/'seal.json',SEALED/'evaluation.json',RULE):
        files[path.relative_to(ROOT).as_posix()]=pin(path)
    return files


def inputs():
    load=lambda path:json.loads(path.read_bytes())
    return p.extract(load(PARENT/'record.json'),load(PARENT/'verification.json'),
        load(SEALED/'execution.json'),load(SEALED/'seal.json'),load(SEALED/'evaluation.json'))


def budget(files,sizes):
    source=sum(n for name,(h,n) in files.items() if name.endswith('.py'))
    evidence=sum(n for name,(h,n) in files.items() if not name.endswith('.py') and Path(name).name in ('record.json','seal.json'))
    verification=sum(n for name,(h,n) in files.items() if Path(name).name=='verification.json')
    meta=sum(n for name,(h,n) in files.items())-source-evidence-verification+8192
    for name,n in sizes.items():
        if name=='table.json':evidence+=n
        elif name=='verification.json':verification+=n
        else:meta+=n
    total=source+evidence+verification+meta
    bad=[name for name,n in sizes.items() if n>CAPS[name]]
    if meta>98304:bad.append('METADATA')
    if total>4194304:bad.append('TOTAL')
    if verification>262144:bad.append('VERIFICATION')
    return dict(sources=source,evidence=evidence,metadata=meta,verification=verification,
                total=total,report_reserve=8192,violations=bad)


def prepare():
    p.need(not OUT.exists(),'OUTPUT_EXISTS')
    files=inventory();rule=json.loads(RULE.read_bytes())
    for name in ('mcm_field_organism/_ppb1_reference.py','tools/_s2jw_default_live_profile.py'):
        p.need(files[name]==rule['files'][name],'ORIGINAL_RULE_CHANGED')
    # Shape/provenance check only; no distance or threshold evaluation here.
    inputs()
    b=dict(version=p.VERSION,files=files,python=sys.version,interpreter=pin(Path(sys.executable)),
        threshold=0.01,comparison='INCLUSIVE',reserves=CAPS,budget=budget(files,CAPS),
        work=dict(real_ppb_calls=22,real_differences=6336,verification_terms=6336,
            verification_sums=22,verification_new_differences=0,
            neutral_ppb_calls_max=24,neutral_differences_max=6912,
            neutral_verification_terms_max=6624,neutral_verification_sums_max=23),
        tests=[n.name for n in ast.walk(ast.parse((ROOT/OWN[2]).read_text())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')])
    p.need(len(p.s.raw(b))<=CAPS['preregistration.json'] and not b['budget']['violations'],'PRESTART_LIMIT')
    OUT.mkdir();save('preregistration.json',b);print(json.dumps(b['budget']))


def run():
    b=json.loads((OUT/'preregistration.json').read_bytes())
    for name,value in b['files'].items():p.need(pin(ROOT/name)==value,'SOURCE_CHANGED')
    p.need(pin(Path(sys.executable))==b['interpreter'],'INTERPRETER')
    with (OUT/'qualification.claim').open('xb') as f:f.write(b'once\n')
    phase='QUALIFICATION'
    try:
        with (OUT/'qualification.log').open('xb') as f:
            test=subprocess.run([sys.executable,'-m','unittest','tests.test_structure_ppb_table','-v'],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
        ok=test.returncode==0 and (OUT/'qualification.log').stat().st_size<=4096
        save('qualification.json',dict(status='QUALIFIED' if ok else 'NOT_QUALIFIED',calls=1,tests=6,exit_code=test.returncode))
        p.need(ok,'QUALIFICATION_STOP')
        phase='INPUT'
        for name,value in b['files'].items():p.need(pin(ROOT/name)==value,'SOURCE_CHANGED')
        vectors,old=inputs()
        with (OUT/'calculation.claim').open('xb') as f:f.write(b'once\n')
        phase='TABLE';result=p.table(vectors,old)
        result['parent_record_sha256']=b['files'][(PARENT/'record.json').relative_to(ROOT).as_posix()][0]
        p.need(len(p.s.raw(result))<=16384,'TABLE_LIMIT');save('table.json',result)
        phase='VERIFY'
        with (OUT/'verification.claim').open('xb') as f:f.write(b'once\n')
        verification=p.verify(json.loads((OUT/'table.json').read_bytes()),old)
        save('verification.json',verification)
        print('TABLE_COMPLETE / EVIDENCE_VALID')
    except Exception as exc:
        save('failure.json',dict(status='NOT_EVALUABLE',phase=phase,error=str(exc),traceback=traceback.format_exc()))
        raise
    finally:
        sizes={x.name:x.stat().st_size for x in OUT.iterdir() if x.is_file()}
        sizes['balance.json']=2048
        balance=budget(b['files'],sizes);save('balance.json',balance)
        p.need(not balance['violations'],'FINAL_BUDGET')


if __name__=='__main__':{'prepare':prepare,'run':run}[sys.argv[1]]()
