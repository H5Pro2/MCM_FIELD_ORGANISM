"""Bound one-shot admission and closure. No grant-authoring or source-selection API."""
import ast
import copy
import os
import re
import sys
from pathlib import Path
from tools import _s2uc_p2_execution as e
from tools import _s2uc_p2_appendix as lineage

ROOT=e.ROOT
VERSION='s2uc.productive.v1'
TEST='tests/test_s2uc_productive.py'
ENTRIES=e.ENTRIES+('tools/_s2uc_productive.py','tools/s2uc_productive_once.py',
    'tools/s2uc_productive_check.py',TEST)
RUN='s2uc-source-comparison-real-20260920-02'
OUTPUTS={k:'reports/'+RUN+s for k,s in
         [('product',''),('observer','-observer'),('appendix','-appendix'),('admission','-admission')]}
need=e.need
same=e.core._same_typed

def current():
    inv=e.resources.inventory._collect(ROOT,ENTRIES,VERSION)
    native=[Path(sys.base_prefix)/f'python{sys.version_info.major}{sys.version_info.minor}.dll']
    native += [Path(os.environ['SystemRoot'])/'System32'/n for n in ('kernel32.dll','psapi.dll','advapi32.dll')]
    inv['external']['native_runtime']=[dict(path=str(f.resolve()),bytes=f.stat().st_size,
                                          sha256=e.sha(f.read_bytes())) for f in native]
    return inv

def test_ids():
    tree=ast.parse((ROOT/TEST).read_bytes())
    return sorted(e.test_ids()+[f'{TEST[:-3].replace("/",".")}.{c.name}.{m.name}'
        for c in tree.body if isinstance(c,ast.ClassDef) for m in c.body
        if isinstance(m,ast.FunctionDef) and m.name.startswith('test_')])

def ref(path):return e.p1.reference(path)

def read_ref(pin):
    need(type(pin) is dict and set(pin)=={'path','bytes','sha256'},'P3_REFERENCE')
    actual,data,_=e.resources.inventory.read_file(ROOT,pin['path'])
    need(actual==pin,'P3_REFERENCE_CHANGED')
    return e.read_json(ROOT/pin['path'])

def source_pin():return ref(e.P1/'attempt-01/preparation/source-context.json')

def plan_pin():return ref(ROOT/'reports/s2nu/s2nu-source-preseal-20260909-01/execution-plan.json')

def paths(value):return {k:ROOT/v for k,v in value['outputs'].items()}

def identity(value,test):
    if test:
        need(re.fullmatch(r'S2UC-P3-TEST-[0-9a-f]{32}',value['run_id']) is not None,'P3_TEST_ID')
        base=ROOT/value['test_root']
        need(base.parent==ROOT/'reports/s2uc' and base.name.startswith('p3-test-')
             and base.resolve()==base,'P3_TEST_ROOT')
        expected={k:(base/k).relative_to(ROOT).as_posix() for k in OUTPUTS}
    else:
        need(value['run_id']==RUN and value['test_root'] is None,'P3_RUN_ID')
        expected=OUTPUTS
    need(value['outputs']==expected,'P3_OUTPUTS')
    for p in paths(value).values():
        need(p.resolve()==p and not p.is_symlink() and not p.is_junction(),'P3_PATH_ALIAS')
        for parent in p.parents:
            need(not parent.is_symlink() and not parent.is_junction(),'P3_PARENT_ALIAS')
            if parent==ROOT:break

def qualified(value,inv):
    q=value['qualification']
    need(type(q) is dict and set(q)=={'inventory','result','protocol','ledger'},'P3_QUALIFICATION')
    qi=read_ref(q['inventory']);result=read_ref(q['result']);protocol=read_ref(q['protocol'])
    budget=read_ref(q['ledger'])
    need(qi==inv,'P3_QUALIFICATION_CODE')
    flags=dict(code_unchanged=True,expected_ids_complete=True,exit_code=0,errors=0,
               failures=0,skips=0,formal_qualification=False,real_execution_authorized=False)
    need(all(type(result.get(k)) is type(v) and result[k]==v for k,v in flags.items()),'P3_RESULT')
    ids=test_ids()
    need(result['test_ids']==ids and result['tests_run']==len(ids)
         and result['results']==dict.fromkeys(ids,'PASS') and result['inventory']==q['inventory'],
         'P3_COVERAGE')
    need(protocol['inventory']==q['inventory'] and protocol['result']==q['result']
         and sorted(protocol['prefixes'][r[0]]+'.'+r[1] for r in protocol['rows'])==ids
         and all(r[2]=='PASS' for r in protocol['rows']),'P3_PROTOCOL')
    need(budget['accounting_complete'] is True and budget['actual']['within_limits'] is True
         and budget['reserved_closure']['within_limits'] is True,'P3_QUALIFICATION_BUDGET')
    for kind in ('actual','reserved_closure'):
        need(e.resources.account(budget[kind]['categories'])==budget[kind],'P3_BUDGET_ARITHMETIC')
    consumed=[]
    input_categories={r['ref']['path']:r['category'] for r in e.inputs()}
    for row in budget['files']:
        actual=ref(Path(row['path']))
        category=input_categories.get(actual['path'],e.resources.FILES.get(Path(actual['path']).name))
        need(category is not None and category==row['category'],'P3_QUALIFICATION_CATEGORY')
        need(actual['bytes']==row['bytes'] and (actual['sha256']==row['sha256'] or
             row['sha256'] is None and actual==q['ledger']),'P3_QUALIFICATION_FILE_CHANGED')
        consumed.append(dict(ref=actual,category=row['category']))
    covered={r['ref']['path'] for r in consumed}
    need(all(pin['path'] in covered for pin in q.values()),'P3_QUALIFICATION_ACCOUNTING')
    measured=e.resources.Ledger(inv,[],consumed).admit()
    need(measured['actual']==budget['actual'] and measured['reserved_closure']==budget['reserved_closure'],
         'P3_QUALIFICATION_LEDGER_CHANGED')
    return consumed

def _load(path,*,test=False,consumed=False):
    from tools import s2uc_productive_once as boundary
    path=Path(path).absolute();value=e.read_json(path)
    need(set(value)=={'version','kind','run_id','authorization_id','decision','max_uses','outputs',
        'test_root','test_payload','inventory','resources','source_context','source_plan',
        'manifest_digest','qualification'},'P3_GRANT_SCHEMA')
    need(value['version']==VERSION and value['kind']==('ISOLATED_TEST' if test else 'OPERATIVE_ONE_SHOT')
        and type(value['max_uses']) is int and value['max_uses']==1,'P3_AUTHORITY_KIND')
    need(re.fullmatch(r'[0-9a-f]{32}',value['authorization_id']) is not None
        and type(value['decision']) is str and 0<len(value['decision'])<=512,'P3_DECISION')
    identity(value,test)
    if test:
        need(path.parent==ROOT/value['test_root'] and path.name=='binding.json'
             and value['test_payload'] in ('original_bad_hash','synthetic'),'P3_TEST_BINDING')
    else:
        need(value['test_payload'] is None,'P3_TEST_SEAM_FORBIDDEN')
        boundary.authority(path,value)
    inv=current()
    need(read_ref(value['inventory'])==inv,'P3_CODE_RUNTIME')
    need(same(read_ref(value['resources']),e.resources.contract()),'P3_RESOURCES')
    need(value['source_context']==source_pin() and value['source_plan']==plan_pin(),'P3_SOURCES')
    context=read_ref(value['source_context']);e.context.validate_source_context(context)
    read_ref(value['source_plan'])
    need(value['manifest_digest']==context['manifest']['binding_digest'],'P3_MANIFEST')
    evidence=[]
    if test:need(value['qualification'] is None,'P3_TEST_NOT_QUALIFIED')
    else:evidence=qualified(value,inv)
    roots=list(paths(value).values())
    need(not path.is_relative_to(paths(value)['admission']),'P3_GRANT_IN_OUTPUT')
    for name,p in paths(value).items():
        if not consumed:need(not p.exists(),'P3_ALREADY_USED:'+name)
    inputs=[dict(ref=ref(path),category='metadata')]
    for key,category in [('inventory','static_shared'),('resources','static_shared'),
                         ('source_context','metadata'),('source_plan','static_shared')]:
        inputs.append(dict(ref=value[key],category=category))
    for row in evidence:
        if row['ref']['path'] not in {r['ref']['path'] for r in inputs}:inputs.append(row)
    ledger=Ledger(inv,roots,inputs)
    ledger.admit()
    if consumed:check_claim(path,value)
    return value,ledger

def load(path,*,consumed=False):return _load(path,consumed=consumed)

def _test_load(path,*,consumed=False):return _load(path,test=True,consumed=consumed)

class Ledger(e.resources.Ledger):
    """Same byte contract; absent output roots are empty before exclusive claim."""
    def snapshot(self):
        original=self.roots
        try:
            for p in original:
                need(p.resolve()==p and not p.is_symlink() and not p.is_junction(),'P3_ROOT_ALIAS')
            self.roots=[p for p in original if p.exists()]
            return super().snapshot()
        finally:self.roots=original

def claim(path,value,ledger):
    ledger.admit();folder=paths(value)['admission']
    folder.mkdir() # Atomic exclusive namespace, including corrupt/incomplete claims.
    receipt=dict(version=VERSION,binding=ref(path),run_id=value['run_id'],
                 authorization_id=value['authorization_id'],consumed=True,kind=value['kind'])
    data=e.canonical(receipt);ledger.project('metadata',len(data))
    e.write_new(folder/'claim.json',data) # flush + fsync before process creation.
    check_claim(path,value)
    return receipt

def check_claim(path,value):
    need(same(e.read_json(paths(value)['admission']/'claim.json'),dict(version=VERSION,
        binding=ref(path),run_id=value['run_id'],authorization_id=value['authorization_id'],
        consumed=True,kind=value['kind'])),'P3_CLAIM_CHANGED')

def manifest(value):
    if value['kind']=='ISOLATED_TEST' and value['test_payload']=='synthetic':
        return e.manifest_for(e.BOUND_TEST)
    return read_ref(value['source_context'])['manifest']

def scope(value):return 'P3_TEST_ONLY' if value['kind']=='ISOLATED_TEST' else 'ORIGINAL_NU_P3'

def stamp(value):
    return dict(scope=scope(value),test_evidence=value['kind']=='ISOLATED_TEST',
                real_execution_authorized=value['kind']=='OPERATIVE_ONE_SHOT')

def status(value,appendix=False):
    return ('CLOSED_TEST_P3_' if value['kind']=='ISOLATED_TEST' else 'CLOSED_ORIGINAL_P3_')+(
        'PROVENANCE' if appendix else 'VERIFIED')

def failure(folder,ledger,value,primary,*,appendix=False):
    result=dict(version=VERSION,status='NOT_EVALUABLE',primary_failure=str(primary),
                evaluation_allowed=False,secondary_failures=[],**stamp(value))
    stage=folder/'publication.tmp'
    if stage.exists():
        try:stage.unlink()
        except OSError as exc:result['secondary_failures'].append(str(exc))
    for name in (('appendix-error.json','appendix-terminal.json') if appendix else ('error.json','terminal.json')):
        try:e.atomic(folder/name,e.canonical(result),ledger)
        except Exception as exc:result['secondary_failures'].append(str(exc))
    if not (folder/('appendix-terminal.json' if appendix else 'terminal.json')).exists():
        try:e.atomic(folder/'minimal.json',e.canonical(result),ledger)
        except Exception as exc:result['secondary_failures'].append(str(exc))
    return result

def _execute(path,proof,*,test=False):
    """No supplier argument. Production binds the original closure internally."""
    from tools import s2uc_p2_process as boundary
    from tools import _s2nu_private_source_binding as nu
    value,ledger=_load(path,test=test,consumed=True)
    boundary.verify_current_job(proof)
    need(proof.get('member') is True and proof.get('flags')==0x2100
         and proof.get('limit')==640*1048576,'P3_JOB_REQUIRED')
    product=paths(value)['product'];product.mkdir()
    context=read_ref(value['source_context']);m=manifest(value)
    original=e.context.prepare_nu_supplier(context)
    calls=[];owners=e.core._Owners();primary=None
    def supply(endpoint):
        boundary.verify_current_job(proof);check_claim(path,value)
        ep=copy.deepcopy(endpoint)
        if test and value['test_payload']=='synthetic':
            expected=e.context.endpoints(m,scope(value))['sources']
            need(ep==expected.get(ep.get('source_id')),'P3_TEST_ENDPOINT')
            ep['pcm_sha256']=context['adapter']['sources'][ep['source_id']]['pcm_sha256']
        data=original(ep)
        calls.append([ep['source_id'],e.sha(data)])
        return data
    # The test subprocess installs the sole replacement; productive execution never does.
    source=e.core._Source(e.context.endpoints(m,scope(value)),supply)
    try:
        try:record=e.core.connection.execute(m,source,owners=owners.create)
        finally:owner_rows=owners.close()
        if record['status']!='COMPLETE':primary=str(record['failure']['code'])
        rows=source.snapshot(record)
        record.update(source_completion=rows,owner_cleanup=owner_rows,
            execution=dict(contract_id=e.resources.VERSION,run_id=value['run_id'],
                binding_sha256=ref(path)['sha256'],**stamp(value)))
        e.atomic(product/'record.json',e.codec.dumps(record),ledger)
        record=e.codec.loads((product/'record.json').read_bytes())
        technical=e.core.verify_materialized(record,m,copy.deepcopy(rows),copy.deepcopy(owner_rows))
        proof_value=dict(version=VERSION,record=ref(product/'record.json'),technical=technical,
                         evaluation=None if primary else e.evaluation.evaluate(record),**stamp(value))
        e.atomic(product/'verification.json',e.canonical(proof_value),ledger)
        if primary:return failure(product,ledger,value,primary)
        need(rows['status']=='COMPLETE' and len(calls)==58,'P3_SOURCE_INCOMPLETE')
        terminal=dict(version=VERSION,status=status(value),run_id=value['run_id'],binding=ref(path),
            record=proof_value['record'],verification=ref(product/'verification.json'),
            primary_failure=None,evaluation_allowed=True,**stamp(value))
        e.atomic(product/'terminal.json',e.canonical(terminal),ledger)
        _read_product(path,value,ledger)
        return dict(status=status(value),evaluation_allowed=True,**stamp(value))
    except Exception as exc:
        owners.close();return failure(product,ledger,value,primary or str(exc) or type(exc).__name__)
    finally:
        facts=dict(version=VERSION,calls=len(calls),receipts=calls,**stamp(value))
        e.atomic(paths(value)['observer']/'facts.json',e.canonical(facts),ledger)

def execute_child(path,proof):return _execute(path,proof)

def _read_product(path,value,ledger):
    check_claim(path,value);ledger.admit();p=paths(value)['product']
    need({f.name for f in p.iterdir()}=={'record.json','verification.json','terminal.json'},'P3_PRODUCT_FILES')
    terminal=e.read_json(p/'terminal.json');proof=e.read_json(p/'verification.json')
    expected=dict(version=VERSION,status=status(value),run_id=value['run_id'],binding=ref(path),
        record=ref(p/'record.json'),verification=ref(p/'verification.json'),primary_failure=None,
        evaluation_allowed=True,**stamp(value))
    need(same(terminal,expected),'P3_PRODUCT_NOT_EVALUABLE')
    record=e.codec.loads((p/'record.json').read_bytes());m=manifest(value)
    need(record['status']=='COMPLETE' and record['execution']==dict(contract_id=e.resources.VERSION,
        run_id=value['run_id'],binding_sha256=ref(path)['sha256'],**stamp(value)),'P3_RECORD_BINDING')
    technical=e.core.verify_materialized(record,m,record['source_completion'],record['owner_cleanup'])
    expected=dict(version=VERSION,record=terminal['record'],technical=technical,
                  evaluation=e.evaluation.evaluate(record),**stamp(value))
    need(e.canonical(proof)==e.canonical(expected),'P3_PROOF_CHANGED')
    return record,m,terminal

def read_product(path):
    value,ledger=load(path,consumed=True)
    observe(path,value)
    return _read_product(path,value,ledger)

def observe(path,value):
    p=paths(value)['observer']
    rows={n:e.read_json(p/(n+'.json')) for n in
          ('bootstrap','parent-admission','child-admission','after-imports','facts','result','process-exit')}
    need(rows['bootstrap']['no_site'] is True and rows['bootstrap']['product_numpy_absent'] is True,'P3_BOOTSTRAP')
    for n in ('parent-admission','child-admission'):
        r=rows[n];need(r['member'] is True and r['flags']==0x2100 and r['limit']==640*1048576,'P3_JOB_PROOF')
    need(rows['child-admission']['product_numpy_absent'] is True
        and rows['bootstrap']['ns']<rows['child-admission']['ns']<rows['after-imports']['ns'],'P3_IMPORT_ORDER')
    facts=rows['facts'];m=manifest(value)
    expected=[[ev['endpoint']['source_id'],ev['endpoint']['pcm_sha256']] for ev in m['events'] if 'endpoint' in ev]
    need(facts==dict(version=VERSION,calls=58,receipts=expected,**stamp(value)),'P3_PRODUCTION_RECEIPTS')
    need(rows['result']['status']==rows['process-exit']['status']==status(value)
         and rows['process-exit']['exit_code']==0,'P3_PROCESS_CLOSURE')
    for n in ('result','process-exit'):
        need(all(rows[n].get(k)==v for k,v in stamp(value).items()),'P3_OBSERVER_SCOPE')
    need((p/'stdout.txt').read_bytes()==(p/'stderr.txt').read_bytes()==b'','P3_PROCESS_OUTPUT')
    return rows

def pins(path,value):
    refs=[ref(path)]
    refs.extend(value[k] for k in ('inventory','resources','source_context','source_plan'))
    for name in ('admission','product','observer'):
        refs.extend(ref(p) for p in sorted(paths(value)[name].iterdir()) if p.is_file())
    return refs

def provenance(record,m,refs,value):
    result=lineage.evaluate(record,m,refs)
    result.update(version=VERSION,status='EVALUATED_TEST' if value['kind']=='ISOLATED_TEST' else 'EVALUATED_ORIGINAL',
                  **stamp(value))
    return result

def _appendix(path,*,test=False,read=False):
    value,ledger=_load(path,test=test,consumed=True);folder=paths(value)['appendix']
    if not read:folder.mkdir()
    initial=pins(path,value)
    try:
        observe(path,value);record,m,terminal=_read_product(path,value,ledger)
        report=provenance(record,m,initial,value)
        if read:
            need({p.name for p in folder.iterdir()}=={'provenance.json','appendix-terminal.json'},'P3_APPENDIX_FILES')
            need(e.canonical(e.read_json(folder/'provenance.json'))==e.canonical(report),'P3_PROVENANCE_CHANGED')
        else:e.atomic(folder/'provenance.json',e.canonical(report),ledger)
        closure=dict(version=VERSION,status=status(value,True),product_status=terminal['status'],
            originals=initial,report=ref(folder/'provenance.json'),parent_process_limited=False,**stamp(value))
        if read:need(e.read_json(folder/'appendix-terminal.json')==closure,'P3_APPENDIX_CHANGED')
        else:e.atomic(folder/'appendix-terminal.json',e.canonical(closure),ledger)
        need(pins(path,value)==initial,'P3_ORIGINAL_CHANGED')
        return report
    except Exception as exc:
        if read:raise
        return failure(folder,ledger,value,str(exc),appendix=True)

def publish_appendix(path):return _appendix(path)

def read_appendix(path):return _appendix(path,read=True)
