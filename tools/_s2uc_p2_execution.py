"""P2 admission and closure glue; existing source adapter and memory algorithms."""
import ast
import copy
import json
import os
import re
from pathlib import Path
from tools import _s2uc_comparison_preparation as p1
from tools import _s2uc_p2_resources as resources
from tools import _s2uc_execution_v8 as core
from tools import _s2uc_source_context_v9 as context
from tools import _s2uc_record_codec as codec
from tools import _s2uc_evaluation as evaluation

ROOT=p1.ROOT
VERSION='s2uc.execution.p2.supplier-correction'
P1=ROOT/'reports/s2uc/preparation-p1-20260930-01'
TEST='tests/test_s2uc_p2.py'
ENTRIES=p1.ENTRIES+('tools/_s2uc_p2_execution.py','tools/_s2uc_p2_appendix.py',
    'tools/s2uc_p2_process.py','tools/s2uc_p2_check.py',TEST)
AUTH=dict(kind='ONE_P2_TEST_EXECUTION',max_uses=1,real_sources=False)
SYNTHETIC='SYNTHETIC_IDENTITIES'
BOUND_TEST='BOUND_NU_IDENTITIES_TEST_PCM'
need=resources.need
canonical=p1.canonical
sha=resources.inventory.sha

def current():
    inv=resources.inventory._collect(ROOT,ENTRIES,VERSION)
    inv['external']['native_runtime']=p1.old.b.current()['external']['native_runtime']
    return inv

def test_ids():
    tree=ast.parse((ROOT/TEST).read_bytes())
    return sorted(p1.test_ids()+[f'{TEST[:-3].replace("/",".")}.{c.name}.{m.name}'
        for c in tree.body if isinstance(c,ast.ClassDef) for m in c.body
        if isinstance(m,ast.FunctionDef) and m.name.startswith('test_')])

def inputs():
    ledger=json.loads((P1/'attempt-01/preparation/ledger.json').read_bytes())
    cats={r['path']:r['category'] for r in ledger['files']}
    for f in P1.rglob('*'):
        if f.is_file(): cats.setdefault(f.relative_to(ROOT).as_posix(),'static_shared')
    return [dict(ref=p1.reference(ROOT/name),category=cat) for name,cat in sorted(cats.items())]

def write_new(path,data):
    core.publication._write(Path(path),data)

def read_json(path):
    path=Path(path)
    return json.loads(resources.inventory.read_file(path.parent,path.name)[1])

def scope(value):
    need(value.get('source_identity') in (SYNTHETIC,BOUND_TEST),'P2_SOURCE_IDENTITY')
    return 'BOUND_SOURCE_TEST_P2' if value['source_identity']==BOUND_TEST else 'NEUTRAL_NONZERO_P2'

def substitutions():
    """Explicit test PCM hashes; never overwrite or claim the original source hash."""
    original=context.source_context()['adapter']['sources']
    return {name:dict(original_pcm_sha256=original[name]['pcm_sha256'],
        test_pcm_sha256=sha(context.neutral_payload(f'neutral-v9-{i}')),
        production_interface='tools._s2nu_private_source_binding.pcm_window',
        stream=2,window=i) for i,name in enumerate(context.science.IDS.values())}

def manifest_for(identity):
    need(identity in (SYNTHETIC,BOUND_TEST),'P2_SOURCE_IDENTITY')
    if identity==SYNTHETIC:return context.neutral_manifest()
    value=copy.deepcopy(context.source_context()['manifest']);mapping=substitutions()
    for event in value['events']:
        if 'endpoint' in event:
            ep=event['endpoint'];ep['pcm_sha256']=mapping[ep['source_id']]['test_pcm_sha256']
    bare={k:v for k,v in value.items() if k not in ('binding_digest','binding_bytes')}
    value.update(binding_digest=context.science.digest(bare),binding_bytes=len(canonical(bare)))
    context.science.validate(value)
    return value

def prepare(folder,qualification_root,*,source_test=False):
    """Create neutral test admission only. No productive grant authoring API."""
    p1.read(P1/'attempt-01/preparation')
    folder=Path(folder).absolute(); q=Path(qualification_root).absolute()
    need(folder.is_relative_to(q) and folder!=q,'P2_QUALIFICATION_ROOT')
    inv=current(); encoded=canonical(inv)
    need(len(encoded)<=16384,'P2_INVENTORY_LIMIT')
    folder.mkdir()
    run_id='S2UC-P2-NEUTRAL-'+os.urandom(16).hex()
    identity=BOUND_TEST if source_test else SYNTHETIC
    for name,value in [('inventory.json',inv),('resources.json',resources.contract()),
                        ('manifest.json',manifest_for(identity))]:
        write_new(folder/name,canonical(value))
    value=dict(version=VERSION,authorization=AUTH,run_id=run_id,source_identity=identity,
        payload_substitution=substitutions() if source_test else None,
        output=(folder/'product').as_posix(),qualification_root=q.as_posix(),
        inventory=p1.reference(folder/'inventory.json'),resources=p1.reference(folder/'resources.json'),
        manifest=p1.reference(folder/'manifest.json'),inputs=inputs(),
        source_context=p1.reference(P1/'attempt-01/preparation/source-context.json'))
    write_new(folder/'binding.json',canonical(value))
    load(folder/'binding.json')
    return folder/'binding.json'

def load(path, *, consumed=False):
    path=Path(path).absolute();value=read_json(path)
    need(path.name=='binding.json' and set(value)=={'version','authorization','run_id','output',
        'qualification_root','inventory','resources','manifest','inputs','source_context',
        'source_identity','payload_substitution'},'P2_BINDING_SCHEMA')
    need(value['version']==VERSION and core._same_typed(value['authorization'],AUTH),'P2_AUTHORIZATION')
    need(re.fullmatch(r'S2UC-P2-NEUTRAL-[0-9a-f]{32}',value['run_id']) is not None,'P2_IDENTITY')
    need(value['output']==(path.parent/'product').as_posix(),'P2_OUTPUT')
    q=Path(value['qualification_root'])
    need(q.is_absolute() and q.resolve()==q and path.parent.is_relative_to(q)
         and q.is_relative_to(ROOT/'reports/s2uc'),'P2_QUALIFICATION_ROOT')
    inv=current()
    for name in ('inventory','resources','manifest'):
        need(value[name]==p1.reference(path.parent/(name+'.json')),'P2_BOUND_FILE')
    need(read_json(path.parent/'inventory.json')==inv,'P2_CURRENT_INVENTORY')
    need(read_json(path.parent/'resources.json')==resources.contract(),'P2_CONTRACT')
    scope(value)
    need(read_json(path.parent/'manifest.json')==manifest_for(value['source_identity']),'P2_MANIFEST')
    need(value['payload_substitution']==(substitutions() if value['source_identity']==BOUND_TEST else None),
         'P2_PAYLOAD_SUBSTITUTION')
    need(value['inputs']==inputs(),'P2_INPUT_BINDING')
    need(value['source_context']==p1.reference(P1/'attempt-01/preparation/source-context.json'),
         'P2_SOURCE_CONTEXT_BINDING')
    context.validate_source_context(read_json(ROOT/value['source_context']['path']))
    p1._compatible(read_json(P1/'attempt-01/dependency-inventory.json'),inv)
    ledger=resources.Ledger(inv,[q],value['inputs']);ledger.admit()
    if not consumed:
        need(not (path.parent/'claim.json').exists() and not Path(value['output']).exists(),'P2_ALREADY_USED')
    return value,ledger

def claim(path,value,ledger):
    ledger.admit()
    receipt=dict(version=VERSION,run_id=value['run_id'],binding=p1.reference(path),
                 consumed=True,scope=scope(value),test_evidence=True,real_execution_authorized=False)
    data=canonical(receipt);ledger.project('metadata',len(data))
    write_new(Path(path).parent/'claim.json',data) # O_EXCL before Job or supplier.
    return receipt

def check_claim(path,value):
    claim_value=read_json(Path(path).parent/'claim.json')
    need(claim_value==dict(version=VERSION,run_id=value['run_id'],binding=p1.reference(path),
         consumed=True,scope=scope(value),test_evidence=True,real_execution_authorized=False),'P2_CLAIM_INVALID')

def atomic(path,data,ledger):
    path=Path(path);stage=path.parent/'publication.tmp'
    need(path.name in resources.FILES and not path.exists() and not stage.exists(),'P2_PUBLICATION_EXISTS')
    ledger.project(resources.FILES[path.name],len(data))
    write_new(stage,data)
    need(stage.read_bytes()==data,'P2_STAGE_CHANGED')
    ledger.admit()
    os.rename(stage,path)
    need(path.read_bytes()==data,'P2_PUBLICATION_CHANGED')
    ledger.admit()

def fail(folder,ledger,primary,*,appendix=False):
    """First error survives cleanup/closure errors; no automatic second attempt."""
    folder=Path(folder);issues=[]
    stage=folder/'publication.tmp'
    if stage.exists():
        try: stage.unlink()
        except OSError as exc: issues.append(str(exc))
    result=dict(version=VERSION,status='NOT_EVALUABLE',primary_failure=str(primary),
                scope='P2_TEST_ONLY',test_evidence=True,
                evaluation_allowed=False,real_execution_authorized=False,secondary_failures=issues)
    for name in (('appendix-error.json','appendix-terminal.json') if appendix else ('error.json','terminal.json')):
        try: atomic(folder/name,canonical(result),ledger)
        except Exception as exc: issues.append(str(exc))
    if not (folder/('appendix-terminal.json' if appendix else 'terminal.json')).exists():
        try: atomic(folder/'minimal.json',canonical(result),ledger)
        except Exception as exc: issues.append(str(exc))
    return result

def execute_child(path,supplier,job_proof):
    """Called only after stdlib bootstrap verifies membership and code pins."""
    value,ledger=load(path,consumed=True);check_claim(path,value)
    need(job_proof.get('member') is True and job_proof.get('limit')==640*1048576
         and job_proof.get('flags')==0x2100,'P2_JOB_REQUIRED')
    from tools import s2uc_p2_process as boundary
    boundary.verify_current_job(job_proof)
    need(callable(supplier),'P2_SUPPLIER_REQUIRED')
    product=Path(value['output']);product.mkdir()
    source=None;owners=core._Owners();primary=None
    try:
        manifest=read_json(Path(path).parent/'manifest.json')
        source=core._Source(context.endpoints(manifest,scope(value)),supplier)
        try: record=core.connection.execute(manifest,source,owners=owners.create)
        finally: owner_rows=owners.close()
        if record['status']!='COMPLETE': primary=str(record['failure']['code'])
        source_rows=source.snapshot(record)
        record.update(source_completion=source_rows,owner_cleanup=owner_rows,
            execution=dict(contract_id=resources.VERSION,run_id=value['run_id'],
                binding_sha256=p1.reference(path)['sha256'],scope=scope(value),test_evidence=True))
        data=codec.dumps(record);atomic(product/'record.json',data,ledger)
        reloaded=codec.loads((product/'record.json').read_bytes())
        need((product/'record.json').read_bytes()==data,'P2_RECORD_CHANGED')
        technical=core.verify_materialized(reloaded,manifest,copy.deepcopy(source_rows),copy.deepcopy(owner_rows))
        proof=dict(version=VERSION,scope=scope(value),test_evidence=True,record=p1.reference(product/'record.json'),
            technical=technical,evaluation=None if primary else evaluation.evaluate(reloaded))
        atomic(product/'verification.json',canonical(proof),ledger)
        if primary: return fail(product,ledger,primary)
        need(source_rows['status']=='COMPLETE','P2_SOURCE_INCOMPLETE')
        terminal=dict(version=VERSION,status='CLOSED_NEUTRAL_P2_VERIFIED',
            run_id=value['run_id'],scope=scope(value),test_evidence=True,binding=p1.reference(path),record=proof['record'],
            verification=p1.reference(product/'verification.json'),primary_failure=None,
            evaluation_allowed=True,real_execution_authorized=False)
        atomic(product/'terminal.json',canonical(terminal),ledger)
        read_product(path,ledger)
        return dict(status=terminal['status'],scope=scope(value),test_evidence=True,
                    evaluation_allowed=True,real_execution_authorized=False)
    except Exception as exc:
        owners.close()
        return fail(product,ledger,primary or str(exc) or type(exc).__name__)

def read_product(path,ledger):
    value=read_json(path);check_claim(path,value);ledger.admit()
    product=Path(value['output'])
    need({p.name for p in product.iterdir()}=={'record.json','verification.json','terminal.json'},'P2_PRODUCT_FILES')
    terminal=read_json(product/'terminal.json');proof=read_json(product/'verification.json')
    need(terminal.get('status')=='CLOSED_NEUTRAL_P2_VERIFIED' and terminal.get('primary_failure') is None
         and terminal.get('evaluation_allowed') is True and terminal.get('real_execution_authorized') is False,
         'P2_PRODUCT_NOT_EVALUABLE')
    need(terminal.get('binding')==p1.reference(path) and terminal.get('run_id')==value['run_id'],'P2_TERMINAL_BINDING')
    for name in ('record','verification'):
        need(terminal[name]==p1.reference(product/(name+'.json')),'P2_PRODUCT_CHANGED')
    need(proof['record']==terminal['record'] and proof['version']==VERSION and proof['scope']==scope(value)
         and proof.get('test_evidence') is True and terminal.get('test_evidence') is True
         and terminal.get('scope')==scope(value),
         'P2_PROOF_INVALID')
    record=codec.loads((product/'record.json').read_bytes());manifest=read_json(Path(path).parent/'manifest.json')
    need(record['status']=='COMPLETE' and record['execution']==dict(contract_id=resources.VERSION,
        run_id=value['run_id'],binding_sha256=p1.reference(path)['sha256'],scope=scope(value),test_evidence=True),'P2_RECORD_BINDING')
    need(manifest==manifest_for(value['source_identity']),'P2_MANIFEST')
    technical=core.verify_materialized(record,manifest,record['source_completion'],record['owner_cleanup'])
    need(canonical(technical)==canonical(proof['technical']) and
         canonical(evaluation.evaluate(record))==canonical(proof['evaluation']),'P2_TECHNICAL_PROOF')
    return record,manifest,terminal

def start_real(*args,**kwargs):
    core.GATE=False
    raise ValueError('P2_PRODUCTIVE_AUTHORIZATION_ABSENT')

def prepare_bound_supplier(source_context,job_proof,*,binding_path=None,test_manifest=None):
    """Use the original NU binder. Only explicit test PCM hashes are translated.

    Identity, timing, profile and all other endpoint fields must remain exact.
    The original supplier still validates its original endpoint and creates the
    WindowSpec. Tests replace pcm_window, not that supplier or materialization.
    """
    need(job_proof.get('member') is True and job_proof.get('limit')==640*1048576
         and job_proof.get('flags')==0x2100,'P2_JOB_REQUIRED')
    from tools import s2uc_p2_process as boundary
    boundary.verify_current_job(job_proof)
    bound=context.prepare_nu_supplier(source_context)
    test_sources=None;value=None
    if test_manifest is not None:
        need(binding_path is not None,'P2_TEST_BINDING_REQUIRED')
        value=read_json(binding_path);check_claim(binding_path,value)
        need(core._same_typed(value['authorization'],AUTH) and value['source_identity']==BOUND_TEST,
             'P2_TEST_AUTHORIZATION')
        need(test_manifest==manifest_for(BOUND_TEST) and value['payload_substitution']==substitutions(),
             'P2_TEST_MANIFEST')
        test_sources=context.endpoints(test_manifest,'BOUND_SOURCE_TEST_P2')['sources']
    originals=source_context['adapter']['sources']
    def supply(endpoint):
        boundary.verify_current_job(job_proof)
        if test_sources is not None:
            check_claim(binding_path,value)
            source_id=endpoint.get('source_id')
            need(source_id in test_sources and core._same_typed(endpoint,test_sources[source_id]),
                 'P2_TEST_ENDPOINT_INVALID')
            original=copy.deepcopy(endpoint)
            original['pcm_sha256']=originals[source_id]['pcm_sha256']
        else:original=endpoint
        supply.calls+=1
        return bound(original)
    supply.calls=0
    return supply
