"""One qualification of reference resolution, then one bound offline table."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import traceback
from tools import _s2oe_visual_diagnostic_reference as r
from tools import _s2oe_visual_transition_diagnostic as table

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/s2oe/visual-transition-e03-e04-20260912-03'
PARENT='reports/s2oe/media-memory-video-20260912-01/'
PREVIOUS='reports/s2oe/visual-transition-e03-e04-20260912-01/'
OWN=('reports/diagnose_visual_transition_v2_once.py','tools/_s2oe_visual_diagnostic_reference.py',
     'tests/test_s2oe_visual_diagnostic_reference.py')


def save(name,value):
    with (OUT/name).open('xb') as f:f.write(value if isinstance(value,bytes) else r.raw(value))


def code_inventory():
    pending=set(OWN);found={}
    while pending:
        name=pending.pop()
        if name in found:continue
        data=(ROOT/name).read_bytes();found[name]=[r.sha(data),len(data)]
        package=name[:-3].replace('/','.').split('.')[:-1]
        for node in ast.walk(ast.parse(data.decode('utf-8-sig'))):
            names=[]
            if isinstance(node,ast.Import):names=[a.name for a in node.names]
            if isinstance(node,ast.ImportFrom):
                prefix='.'.join(package[:len(package)-node.level+1]) if node.level else ''
                base='.'.join(x for x in (prefix,node.module) if x)
                names=[base,*[base+'.'+a.name for a in node.names]]
            for module in names:
                parts=module.split('.')
                if parts[0] not in ('tools','mcm_field_organism','reports'):continue
                for i in range(1,len(parts)+1):
                    for path in ('/'.join(parts[:i])+'.py','/'.join(parts[:i])+'/__init__.py'):
                        if (ROOT/path).is_file():pending.add(path)
    return found


def prepare():
    OUT.mkdir(exist_ok=False)
    files=code_inventory()
    active=sorted(files)
    r.need(not set(active).intersection(r.HISTORICAL_ONLY),'DECODER_ACTIVE_DEPENDENCY')
    def add(path,expected=None):
        data=(ROOT/path).read_bytes();actual=[r.sha(data),len(data)]
        r.need(expected is None or actual==expected,'PREPARE_REFERENCE_CHANGED')
        r.need(path not in files or files[path]==actual,'PREPARE_SOURCE_CONFLICT')
        files[path]=actual
        return data
    for n in ('record.json','session.json','verification.json','common.json'):add(PARENT+n)
    r.need(files[PARENT+'record.json'][0]=='4da6485b12ce98dca625fe5998130d1f2c0f9225d78a0fefb9c4bcf18298f3e7','PARENT_INVALID')
    common=json.loads((ROOT/(PARENT+'common.json')).read_bytes())
    unavailable={}
    for kind,path,size,digest in common['references']:
        if path in r.HISTORICAL_ONLY:
            r.need(kind=='sources' and [digest,size]==r.HISTORICAL_ONLY[path], 'HISTORICAL_ROLE_INVALID')
            unavailable[path]=[digest,size]
        else:add(path,[digest,size])
    invref=next(x for x in common['references'] if x[3]==common['inventory_sha256'])
    for path,value in r.flatten(json.loads((ROOT/invref[1]).read_bytes())).items():
        if path in unavailable:r.need(value==unavailable[path],'HISTORICAL_ROLE_INVALID')
        else:add(path,value)
    mediaref=next(x for x in common['references'] if x[3]==common['manifest']['code_digest'])
    for path,value in json.loads((ROOT/mediaref[1]).read_bytes()).items():
        if path in unavailable:r.need(value==unavailable[path],'HISTORICAL_ROLE_INVALID')
        else:add(path,value)
    # The old qualified arithmetic is evidence, not another test invocation.
    old=json.loads(add(PREVIOUS+'binding.json'))
    oldq=json.loads(add(PREVIOUS+'qualification.json'));oldlog=add(PREVIOUS+'qualification.log')
    r.need(oldq['status']=='QUALIFIED' and oldq['tests']==12 and oldq['log_sha256']==r.sha(oldlog),'PRIOR_QUALIFICATION_INVALID')
    for path,value in old['inventory'].items():add(path,value)
    tests=sorted(n.name for n in ast.walk(ast.parse((ROOT/OWN[2]).read_bytes()))
                 if isinstance(n,ast.FunctionDef) and n.name.startswith('test_'))
    sources=sum(n for p,(h,n) in files.items() if p.endswith('.py'))
    references=sum(n for p,(h,n) in files.items() if not p.endswith('.py'))
    alternatives=r.alternatives(references,sources)
    value=dict(version=r.VERSION,run_id=OUT.name,qualification_id='visual-reference-qualification-20260912-02',
        files=files,tests=tests,python=sys.version,caps=r.CAPS,limits=r.LIMITS,alternatives=alternatives,
        active_files=active,historical_unavailable=unavailable,historical_software_fully_reconstructed=False,
        primary_differences_max=1152,verification_differences_max=576,table_calls=1,verification_calls=1,
        events=[3,4],gates=False)
    save('binding.json',value)
    print(json.dumps(dict(binding_bytes=len(r.raw(value)),tests=len(tests),alternatives=alternatives)))
    r.need(len(r.raw(value))<=r.CAPS['binding'] and all(not a['violations'] for a in alternatives.values()),'PRESTART_BUDGET_STOP')


def bound():
    b=json.loads((OUT/'binding.json').read_bytes())
    r.need(b['caps']==r.CAPS and b['limits']==r.LIMITS and all(not a['violations'] for a in b['alternatives'].values()),'BUDGET_BINDING_INVALID')
    for path in b['files']:r.checked(ROOT,path,b['files'])
    r.need(b['active_files']==sorted(code_inventory()) and not set(b['active_files']).intersection(r.HISTORICAL_ONLY),'ACTIVE_BINDING_INVALID')
    return b


def qualify():
    b=bound();save('qualification.claim',b'once\n')
    with (OUT/'qualification.log').open('xb') as log:
        proc=subprocess.run([sys.executable,'-m','unittest','tests.test_s2oe_visual_diagnostic_reference','-v'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    data=(OUT/'qualification.log').read_bytes()
    ok=proc.returncode==0 and len(data)<=r.CAPS['log']
    save('qualification.json',dict(status='QUALIFIED' if ok else 'NOT_QUALIFIED',test_calls=1,tests=len(b['tests']),
        exit_code=proc.returncode,log_bytes=len(data),log_sha256=r.sha(data),binding_sha256=r.sha((OUT/'binding.json').read_bytes()),gates=False))
    r.need(ok,'QUALIFICATION_STOP')


def final_balance(b):
    sizes={p.name:p.stat().st_size for p in OUT.iterdir() if p.is_file()}
    metadata=sum(v for p,v in sizes.items() if p not in ('table.json','verification.json'))
    refs=sum(n for h,n in b['files'].values())
    value=dict(files=sizes,bound_references_bytes=refs,metadata_before_balance=metadata,
        total_before_balance=refs+sum(sizes.values()),report_reserve=r.CAPS['report'],balance_reserve=r.CAPS['balance'],gates=False)
    save('balance.json',value)
    n=(OUT/'balance.json').stat().st_size
    r.need(n<=r.CAPS['balance'] and metadata+n+r.CAPS['report']<=r.LIMITS['metadata']
           and value['total_before_balance']+n+r.CAPS['report']<=r.LIMITS['total'],'ACTUAL_BUDGET_INVALID')


def run():
    b=bound();q=json.loads((OUT/'qualification.json').read_bytes())
    r.need(q['status']=='QUALIFIED' and q['binding_sha256']==r.sha((OUT/'binding.json').read_bytes()),'QUALIFICATION_REQUIRED')
    save('calculation.claim',b'once\n');phase='REFERENCE_RESOLUTION';counts=dict(primary_differences=0,verification_differences=0)
    try:
        resolved=r.resolve(ROOT,PARENT,b['files'],b['historical_unavailable'],b['active_files'])
        phase='NATIVE_INPUT_VALIDATION';data=table.extract(*resolved)
        r.need(len([s for s in data['pre']['slots'] if s['occupied']])==2,'SCOPE_CHANGED')
        phase='TABLE';result=table.table(data);counts['primary_differences']=result['primary_differences']
        record=dict(status='TABLE_COMPLETE',binding_sha256=r.sha((OUT/'binding.json').read_bytes()),input=data,result=result)
        r.need(len(r.raw(record))<=r.CAPS['table'] and counts['primary_differences']<=1152,'TABLE_BUDGET_INVALID')
        save('table.json',record)
        phase='READ_ONLY_VERIFICATION';save('verification.claim',b'once\n')
        stored=json.loads((OUT/'table.json').read_bytes())
        independently_bound=table.extract(*r.resolve(ROOT,PARENT,b['files'],b['historical_unavailable'],b['active_files']))
        r.need(r.raw(stored['input'])==r.raw(independently_bound),'TABLE_INPUT_CHANGED')
        proof=table.verify(independently_bound,stored['result']);counts['verification_differences']=proof['comparisons']
        r.need(counts['verification_differences']<=576,'VERIFICATION_WORK_LIMIT')
        proof.update(table_sha256=r.sha((OUT/'table.json').read_bytes()),counts=counts,gates=False,
            historical_software_fully_reconstructed=False,historical_unavailable=b['historical_unavailable'])
        r.need(len(r.raw(proof))<=r.CAPS['proof'],'PROOF_LIMIT');save('verification.json',proof)
        print(json.dumps(dict(status=proof['status'],rows=[{k:v for k,v in row.items() if k!='terms'} for row in result['rows']],
            action=result['action'],selected=result['selected_slot_id'],counts=counts)))
    except Exception:
        failure=dict(status='NOT_EVALUABLE',phase=phase,counts=counts,traceback=traceback.format_exc(),gates=False)
        save('failure.json',failure)
        print(json.dumps(dict(status='NOT_EVALUABLE',phase=phase,counts=counts,failure_bytes=len(r.raw(failure)))))
        raise
    finally:final_balance(b)


if __name__=='__main__':{'prepare':prepare,'qualify':qualify,'run':run}[sys.argv[1]]()
