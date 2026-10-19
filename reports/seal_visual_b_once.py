"""One neutral qualification, then one receptor-free seven-source seal."""
import ast
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

from tools import _visual_b_diagnostic as d
from tools import _structure_source_binding as s

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/s2oe/visual-b-source-seal-20260912-02'
OLD = 'reports/s2oe/structure-location-source-seal-20260912-01/'
MEM = 'reports/s2oe/structure-av-system-20260912-01/'
QUAL_ID = 'visual-b-source-qualification-20260912-03'
BUDGET_VERSION = 'visual-b.source-binding.metadata98304.v2'
METADATA_LIMIT = 98304
CAPS = {'inventory.json':32768, 'preregistration.json':4096,
        'execution.json':8192, 'evaluation.json':1024, 'qualification.log':8192,
        'qualification.json':1024, 'failure.json':4096, 'balance.json':4096,
        'REPORT.md':3072, 'seal.json':16384, 'verification.json':4096,
        'qualification.claim':5, 'seal.claim':5, 'verification.claim':5}


def pin(path):
    b = path.read_bytes()
    return dict(bytes=len(b), sha256=hashlib.sha256(b).hexdigest())


def read(name):
    return json.loads((ROOT / name).read_bytes())


def save(name, value):
    data = s.raw(value)
    d.need(len(data) <= CAPS[name], 'ARTIFACT_LIMIT')
    path = OUT / name
    d.need(not path.exists(), 'OUTPUT_EXISTS')
    temporary = OUT / (name + '.tmp')
    with temporary.open('xb') as stream:
        stream.write(data)
    temporary.rename(path)


def code_closure(initial):
    """Resolve repository imports statically, including relative package imports."""
    pending = list(initial)
    seen = set()
    while pending:
        name = pending.pop()
        if name in seen or not (ROOT / name).is_file():
            continue
        seen.add(name)
        if not name.endswith('.py'):
            continue
        path = Path(name)
        package = list(path.parts[:-1])
        for parent in path.parents:
            init = (parent / '__init__.py').as_posix()
            if (ROOT / init).is_file() and init not in seen:
                pending.append(init)
        tree = ast.parse((ROOT / name).read_text(encoding='utf-8-sig'))
        modules = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules.extend(a.name.split('.') for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                base = package[:len(package)-node.level+1] if node.level else []
                base += node.module.split('.') if node.module else []
                modules.append(base)
                modules.extend(base + a.name.split('.') for a in node.names)
        for parts in modules:
            for end in range(1, len(parts)+1):
                module = '/'.join(parts[:end])
                pending.extend((module+'.py', module+'/__init__.py'))
    return seen


def inventory():
    files = {}
    initial = ['tools/_visual_b_diagnostic.py', 'reports/seal_visual_b_once.py',
               'tests/test_visual_b_binding.py', 'docs/VISUELLE_B_ANWENDBARKEIT_VERGLEICHSPLAN.md']
    for name in code_closure(initial):
        files[name] = dict(kind='sources', **pin(ROOT/name))
    for name in ('execution.json','seal.json','verification.json','preregistration.json'):
        files[OLD+name] = dict(kind='metadata', **pin(ROOT/(OLD+name)))
    for name,kind in (('record.json','evidence'),('verification.json','verification'),
                      ('common-reference.json','metadata')):
        files[MEM+name] = dict(kind=kind, **pin(ROOT/(MEM+name)))
    common_ref = read(MEM+'common-reference.json')
    d.need(pin(ROOT/common_ref['path']) == {k:common_ref[k] for k in ('bytes','sha256')}, 'COMMON')
    files[common_ref['path']] = dict(kind='metadata', **pin(ROOT/common_ref['path']))
    common = read(common_ref['path'])
    for kind,name,size,digest in common['references']:
        d.need(pin(ROOT/name)==dict(bytes=size,sha256=digest), 'HISTORICAL_REFERENCE')
        if name not in files:
            files[name] = dict(kind=kind, bytes=size, sha256=digest)
    return dict(sorted(files.items()))


def budget(files, actual=None):
    parts = dict(sources=0,metadata=0,evidence=0,verification=0)
    for item in files.values():
        parts[item['kind']] += item['bytes']
    for name,cap in CAPS.items():
        amount = actual.get(name,cap) if actual is not None else cap
        kind = {'inventory.json':'sources','seal.json':'evidence',
                'verification.json':'verification'}.get(name,'metadata')
        parts[kind] += amount
    result = s.budget(**parts)
    result['violations'] = [v for v in result['violations'] if v != 'metadata']
    if parts['metadata'] > METADATA_LIMIT:
        result['violations'].append('metadata')
    result.update(budget_version=BUDGET_VERSION,metadata_limit=METADATA_LIMIT)
    return result


def failure_record(exc,phase,completed):
    message = str(exc)
    value = dict(status='NOT_QUALIFIED' if phase=='QUALIFICATION' else 'NOT_EVALUABLE',
        phase=phase,completed_sources=completed,exception_type=type(exc).__name__[:128],
        code=message[:384],message_characters=len(message),
        diagnostic_overflow=len(message)>384 or len(type(exc).__name__)>128,
        qualification_log='qualification.log')
    if len(s.raw(value)) > CAPS['failure.json']:
        value['code']='DIAGNOSTIC_SERIALIZATION_OVERFLOW'
        value['exception_type']='OMITTED_OVERSIZE_TYPE'
        value['diagnostic_overflow']=True
    d.need(len(s.raw(value))<=CAPS['failure.json'],'FAILURE_ENVELOPE_LIMIT')
    return value


def check(files):
    for name,item in files.items():
        d.need(pin(ROOT/name)=={k:item[k] for k in ('bytes','sha256')}, 'SOURCE_CHANGED')


def prepare():
    d.need(not OUT.exists(), 'OUTPUT_EXISTS')
    files = inventory()
    e,v = d.plans()
    old_execution = read(OLD+'execution.json')
    old_seal = read(OLD+'seal.json')
    old_proof = read(OLD+'verification.json')
    d.need(old_proof['status']=='BINDING_VALID' and old_proof['record_digest']==s.digest(old_seal), 'OLD_SEAL')
    d.need(old_seal['execution_digest']==s.digest(old_execution), 'OLD_EXECUTION')
    originals = {r['id']:r for r in old_execution['sources']}
    hashes = {r['id']:r for r in old_seal['sources']}
    for row in e['rows']:
        original = originals[row['base']]
        proof = hashes[row['base']]
        d.need(proof['source_digest']==s.digest(original), 'ORIGINAL_SOURCE')
        row.update(recipe=original['recipe'], original_source_digest=s.digest(original),
                   original_sha256=proof['sha256'])
    record = read(MEM+'record.json')['record']
    proof = read(MEM+'verification.json')
    row = record['execution']['rows'][3]
    d.need(proof['evaluation_allowed'] and proof['core']['record_digest']==record['record_digest'], 'MEMORY_PROOF')
    d.need(row['memory']==e['frozen_memory_digest'] and row['generations']['event']==4, 'MEMORY_BINDING')
    e.update(width=1920,height=1080,format='RGB8',profile=old_execution['profile'],
             frozen=dict(record_path=MEM+'record.json',row=3,memory_digest=row['memory'],
                         chain_digest=row['chain_digest'],births=row['current_births'],
                         runtime_config_digest=row['post']['config_digest']),
             historical_execution_digest=s.digest(old_execution))
    testfile = ROOT/'tests/test_visual_b_binding.py'
    tests = sorted(n.name for n in ast.walk(ast.parse(testfile.read_text()))
                   if isinstance(n,ast.FunctionDef) and n.name.startswith('test_'))
    balance = budget(files)
    print(json.dumps(balance))
    d.need(not balance['violations'], 'PRESTART_BUDGET')
    binding = dict(task='VISUELLE-B-ANWENDBARKEIT-QUELLENBINDUNG', qualification_id=QUAL_ID,
        files_digest=s.digest(files),tests=tests,caps=CAPS,budget=balance,
        budget_version=BUDGET_VERSION,metadata_limit=METADATA_LIMIT,
        execution_digest=s.digest(e),evaluation_digest=s.digest(v),
        interpreter=pin(Path(sys.executable)),python=sys.version,platform=platform.platform(),
        calls=dict(source_generation=7,binding_verification=1,receptor=0,formation=0,runtime=0),
        payload=dict(frame_bytes=6220800,live_frames=1,row_bytes_max=5760,raw_storage=False),
        qualification_log_policy='full log retained; overflow stops without generation',
        future_real_comparison='NOT_AUTHORIZED; native state extraction and total verifier remain open')
    for name,value in (('inventory.json',files),('preregistration.json',binding),
                       ('execution.json',e),('evaluation.json',v)):
        d.need(len(s.raw(value))<=CAPS[name], 'PRESTART_ARTIFACT_LIMIT')
    OUT.mkdir()
    for name,value in (('inventory.json',files),('preregistration.json',binding),
                       ('execution.json',e),('evaluation.json',v)):
        save(name,value)


def run():
    files = json.loads((OUT/'inventory.json').read_bytes())
    b = json.loads((OUT/'preregistration.json').read_bytes())
    e = json.loads((OUT/'execution.json').read_bytes())
    v = json.loads((OUT/'evaluation.json').read_bytes())
    d.need(s.digest(files)==b['files_digest'] and CAPS==b['caps'], 'PREBINDING')
    check(files)
    d.need(pin(Path(sys.executable))==b['interpreter'], 'INTERPRETER')
    d.need(s.digest(e)==b['execution_digest'] and s.digest(v)==b['evaluation_digest'], 'ROOT')
    d.need(not budget(files)['violations'], 'PRESTART_BUDGET')
    with (OUT/'qualification.claim').open('xb') as stream:
        stream.write(b'once\n')
    phase = 'QUALIFICATION'
    proofs = []
    try:
        with (OUT/'qualification.log').open('xb') as log:
            result = subprocess.run([sys.executable,'-m','unittest','tests.test_visual_b_binding','-v'],
                                    cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        check(files)
        ok = result.returncode==0 and (OUT/'qualification.log').stat().st_size<=CAPS['qualification.log']
        save('qualification.json',dict(status='QUALIFIED' if ok else 'NOT_QUALIFIED',
             tests=len(b['tests']),calls=1,exit_code=result.returncode,
             log=pin(OUT/'qualification.log'),sources_unchanged=True,qualification_id=QUAL_ID))
        d.need(ok,'QUALIFICATION_STOP')
        phase = 'GENERATION'
        with (OUT/'seal.claim').open('xb') as stream:
            stream.write(b'once\n')
        for row in e['rows']:
            data = s.render(row['recipe'],e['width'],e['height'])
            d.need(hashlib.sha256(data).hexdigest()==row['original_sha256'],'ORIGINAL_PAYLOAD')
            d.modify_and_occlude(data,e['width'],e['height'],row['level'],row['rectangle'])
            proofs.append(dict(id=row['id'],source_digest=s.digest(row),bytes=len(data),
                               original_sha256=row['original_sha256'],sha256=hashlib.sha256(data).hexdigest()))
            del data
        groups = {}
        for p in proofs:
            groups.setdefault(p['sha256'],[]).append(p['id'])
        record = dict(version=d.VERSION,execution_digest=s.digest(e),evaluation_digest=s.digest(v),
            generated=len(proofs),sources=proofs,collisions=[x for x in groups.values() if len(x)>1],
            environment_binding=s.digest(b),raw_storage=False)
        save('seal.json',record)
        phase = 'VERIFICATION'
        with (OUT/'verification.claim').open('xb') as stream:
            stream.write(b'once\n')
        check(files)
        stored = json.loads((OUT/'seal.json').read_bytes())
        verification = d.verify_sources(stored,e,v,s.digest(b))
        save('verification.json',verification)
        print(json.dumps(dict(status=verification['status'],generated=len(proofs),collisions=record['collisions'])))
    except Exception as exc:
        save('failure.json',failure_record(exc,phase,len(proofs)))
        raise
    finally:
        s.GATE = False
        actual = {p.name:p.stat().st_size for p in OUT.iterdir() if p.is_file()}
        balance = budget(files,actual)
        balance.update(files=actual,gates=False,
                       absent_file_reserves={n:c for n,c in CAPS.items() if n not in actual})
        save('balance.json',balance)
        d.need(not balance['violations'],'FINAL_BUDGET')


if __name__=='__main__':
    {'prepare':prepare,'run':run}[sys.argv[1]]()
