"""Bound one-shot offline diagnostic, preceded by one neutral qualification."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import traceback

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/s2oe/visual-transition-e03-e04-20260912-01'
PARENT='reports/s2oe/media-memory-video-20260912-01/'
OWN=('tools/_s2oe_visual_transition_diagnostic.py','tests/test_s2oe_visual_transition_diagnostic.py',
     'reports/diagnose_visual_transition_once.py')
RESERVES=dict(binding=32768,qualification_log=16384,qualification=2048,table=196608,
              proof=4096,failure=16384,report=8192,balance=4096,claims=10)


def raw(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def sha(x):return hashlib.sha256(x).hexdigest()
def write(name,x):
    with (OUT/name).open('xb') as f:f.write(x if isinstance(x,bytes) else raw(x))


def inventory():
    pending=set(OWN);found={}
    while pending:
        rel=pending.pop()
        if rel in found:continue
        data=(ROOT/rel).read_bytes();found[rel]=[sha(data),len(data)]
        if not rel.endswith('.py'):continue
        for node in ast.walk(ast.parse(data.decode('utf-8-sig'))):
            names=[]
            if isinstance(node,ast.Import):names=[a.name for a in node.names]
            if isinstance(node,ast.ImportFrom) and node.level==0:
                names=[node.module or '',*[(node.module or '')+'.'+a.name for a in node.names]]
            for name in names:
                if name.split('.')[0] not in ('tools','mcm_field_organism'):continue
                parts=name.split('.')
                for i in range(1,len(parts)+1):
                    for candidate in ('/'.join(parts[:i])+'.py','/'.join(parts[:i])+'/__init__.py'):
                        if (ROOT/candidate).is_file():pending.add(candidate)
    return found


def prepare():
    OUT.mkdir(exist_ok=False)
    inv=inventory()
    parents={PARENT+n:[sha((ROOT/(PARENT+n)).read_bytes()),(ROOT/(PARENT+n)).stat().st_size]
             for n in ('record.json','verification.json','common.json')}
    if parents[PARENT+'record.json'][0]!='4da6485b12ce98dca625fe5998130d1f2c0f9225d78a0fefb9c4bcf18298f3e7':
        raise RuntimeError('PARENT_SHA_INVALID')
    common=json.loads((ROOT/(PARENT+'common.json')).read_bytes())
    historical=common['references'][0]
    content=(ROOT/historical[1]).read_bytes()
    if [len(content),sha(content)]!=historical[2:]:raise RuntimeError('HISTORICAL_INVENTORY_INVALID')
    parents[historical[1]]=[sha(content),len(content)]
    old=json.loads(content)
    # All shared historical code in this closure must remain identical.
    conflicts=[p for p in inv if p in old and inv[p]!=old[p]]
    if conflicts:raise RuntimeError(('HISTORICAL_CODE_CHANGED',conflicts))
    tests=sorted(n.name for n in ast.walk(ast.parse((ROOT/OWN[1]).read_bytes()))
                 if isinstance(n,ast.FunctionDef) and n.name.startswith('test_'))
    total=sum(n for h,n in inv.values())+sum(n for h,n in parents.values())+sum(RESERVES.values())
    metadata=sum(RESERVES[k] for k in ('binding','qualification_log','qualification','report','balance','claims'))
    binding=dict(version='s2oe.visual-ppb-diagnostic.v1',inventory=inv,parents=parents,
        historical_inventory=historical[1],tests=tests,qualification_id='visual-transition-qualification-20260912-01',
        run_id=OUT.name,python=sys.version,reserves=RESERVES,total_bound=total,metadata_bound=metadata,
        total_limit=4194304,metadata_limit=65536,table_limit=262144,
        primary_differences_max=1152,verification_differences_max=576,
        events=[3,4],scope='all four visual PPB slots; two occupied; no Fast distances',gates=False)
    write('binding.json',binding)
    print(json.dumps(dict(total_bound=total,metadata_bound=metadata,binding_bytes=len(raw(binding)),tests=len(tests))))
    if total>4194304 or metadata>65536 or len(raw(binding))>32768:raise SystemExit('PRESTART_BUDGET_STOP')


def bound():
    b=json.loads((OUT/'binding.json').read_bytes())
    for p,(h,n) in {**b['inventory'],**b['parents']}.items():
        data=(ROOT/p).read_bytes()
        if len(data)!=n or sha(data)!=h:raise RuntimeError(('BINDING_CHANGED',p))
    if b['total_bound']>b['total_limit'] or b['metadata_bound']>b['metadata_limit']:raise RuntimeError('BUDGET_INVALID')
    return b


def qualify():
    b=bound();write('qualification.claim',b'once\n')
    with (OUT/'qualification.log').open('xb') as log:
        p=subprocess.run([sys.executable,'-m','unittest',OWN[1].replace('/','.').removesuffix('.py'),'-v'],
                         cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    size=(OUT/'qualification.log').stat().st_size
    ok=p.returncode==0 and size<=RESERVES['qualification_log']
    write('qualification.json',dict(status='QUALIFIED' if ok else 'NOT_QUALIFIED',exit_code=p.returncode,
        tests=len(b['tests']),log_bytes=size,log_sha256=sha((OUT/'qualification.log').read_bytes()),gates=False))
    if not ok:raise SystemExit('QUALIFICATION_STOP')


def run():
    b=bound()
    if json.loads((OUT/'qualification.json').read_bytes())['status']!='QUALIFIED':raise RuntimeError('NOT_QUALIFIED')
    write('calculation.claim',b'once\n');phase='INPUT_VALIDATION'
    try:
        from tools import _s2oe_visual_transition_diagnostic as d
        records=[json.loads((ROOT/(PARENT+n)).read_bytes()) for n in ('record.json','verification.json','common.json')]
        if records[0]['common_sha256']!=sha((ROOT/(PARENT+'common.json')).read_bytes()):raise RuntimeError('COMMON_SHA_INVALID')
        data=d.extract(*records)
        if len([s for s in data['pre']['slots'] if s['occupied']])!=2:raise RuntimeError('SCOPE_CHANGED')
        phase='TABLE';result=d.table(data)
        output=dict(status='TABLE_COMPLETE',binding_sha256=sha((OUT/'binding.json').read_bytes()),input=data,result=result)
        if len(raw(output))>RESERVES['table']:raise RuntimeError('TABLE_LIMIT')
        write('table.json',output)
        phase='READ_ONLY_VERIFICATION';write('verification.claim',b'once\n')
        stored=json.loads((OUT/'table.json').read_bytes())
        # Re-resolve native values independently; do not reuse the table's input container.
        independent=d.extract(*[json.loads((ROOT/(PARENT+n)).read_bytes()) for n in ('record.json','verification.json','common.json')])
        if raw(stored['input'])!=raw(independent):raise RuntimeError('TABLE_INPUT_CHANGED')
        proof=d.verify(independent,stored['result'])
        proof.update(table_sha256=sha((OUT/'table.json').read_bytes()),gates=False)
        write('verification.json',proof)
        print(json.dumps(dict(status=proof['status'],rows=[{k:v for k,v in r.items() if k!='terms'} for r in result['rows']],
                              action=result['action'],selected=result['selected_slot_id'])))
    except Exception:
        write('failure.json',dict(status='NOT_EVALUABLE',phase=phase,traceback=traceback.format_exc(),gates=False))
        raise
    finally:
        parts={str(p.relative_to(ROOT)) : p.stat().st_size for p in OUT.iterdir() if p.is_file()}
        refs={p:n for p,(h,n) in {**b['inventory'],**b['parents']}.items()}
        write('balance.json',dict(files=parts,referenced_files=refs,total_before_balance=sum(parts.values())+sum(refs.values()),
            remaining_reserve=RESERVES['balance']+RESERVES['report'],total_limit=b['total_limit'],gates=False))


if __name__=='__main__':
    {'prepare':prepare,'qualify':qualify,'run':run}[sys.argv[1]]()
