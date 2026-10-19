"""Separate P2 provenance closure, using unchanged lineage/target algorithms."""
import copy
from pathlib import Path
from tools import _s2uc_p2_execution as e
from tools import _s2uc_provenance_evaluation as old

def observe(path):
    folder=Path(path).parent/'observer'
    rows={n:e.read_json(folder/(n+'.json')) for n in
        ('bootstrap','parent-admission','child-admission','after-imports','facts','result','process-exit')}
    e.need(rows['bootstrap']['product_numpy_absent'] and rows['bootstrap']['no_site'],'P2_BOOTSTRAP_PROOF')
    for name in ('parent-admission','child-admission'):
        v=rows[name]
        e.need(v['member'] is True and v['limit']==640*1048576 and v['flags']==0x2100,'P2_JOB_PROOF')
    e.need(rows['child-admission']['product_numpy_absent'] is True and
        rows['bootstrap']['ns']<rows['child-admission']['ns']<rows['after-imports']['ns'],'P2_IMPORT_ORDER')
    e.need(rows['facts']['calls']==58 and rows['facts']['real_production_calls']==0 and
        rows['facts']['gate'] is False,'P2_SOURCE_COUNTS')
    value=e.read_json(path);facts=rows['facts']
    e.need(facts['scope']==e.scope(value) and facts['test_evidence'] is True
        and rows['child-admission']['ns']<facts['source_admission_ns']<facts['first_supplier_ns'],
        'P2_SUPPLIER_ADMISSION_ORDER')
    if value['source_identity']==e.BOUND_TEST:
        manifest=e.read_json(Path(path).parent/'manifest.json');mapping=value['payload_substitution']
        expected=[[2,mapping[ev['endpoint']['source_id']]['window'],ev['endpoint']['pcm_sha256']]
                  for ev in manifest['events'] if 'endpoint' in ev]
        e.need(facts['bound_supplier_calls']==facts['replacement_calls']==58
            and facts['production_receipts']==expected
            and facts['first_supplier_ns']<=facts['first_production_ns']
            and facts['rejected_endpoints_before_production']==len(next(
                ev['endpoint'] for ev in manifest['events'] if 'endpoint' in ev))+1,
            'P2_BOUND_SUPPLIER_NOT_EXECUTED')
    e.need(rows['result']['status']==rows['process-exit']['status']=='CLOSED_NEUTRAL_P2_VERIFIED'
        and rows['process-exit']['exit_code']==0,'P2_PROCESS_NOT_CLOSED')
    e.need((folder/'stderr.txt').read_bytes()==b'' and (folder/'stdout.txt').read_bytes()==b'','P2_PROCESS_OUTPUT')
    return rows

def evaluate(record,manifest,refs):
    rows=[];registry={};changes=[]
    for si,story in enumerate(record['stories']):
        origins,events=old._origins(story,si,manifest)
        local,history=old._lineages(story,si,origins,events)
        registry.update(local);changes.extend(history)
        for hi,hint in enumerate(story['hints']):
            ordinal=hint['ordinal'];key=(story['story'],ordinal)
            target=old.targets.TARGETS[key];expected=old.legacy.EXPECTED[key]
            arms={a:old._arm_result(hint,a,ordinal,local,events,manifest,
                f'/stories/{si}/hints/{hi}',target,old.OFFSETS[key]) for a in old.ARMS}
            actual=[arms[a]['decision'] for a in old.ARMS]
            rows.append(dict(key=f'{key[0]}/{key[1]}',story=key[0],ordinal=ordinal,
                target=copy.deepcopy(target),offset=old.OFFSETS[key],arms=arms,
                legacy_expectation=dict(expected=list(expected),actual=actual,
                    fulfilled=actual==list(expected),controls_provenance=False)))
    e.need([(r['story'],r['ordinal']) for r in rows]==list(old.targets.TARGETS),'P2_SEVEN_HINTS')
    old._compare(rows,registry,changes)
    gains=[r['key'] for r in rows if r['target_recall_gain']]
    losses=[r['key'] for r in rows if r['target_recall_loss']]
    return dict(version='s2uc.provenance.p2.supplier-correction',status='EVALUATED_TEST',
        scope=record['execution']['scope'],test_evidence=True,
        inputs=refs,manifest_binding_digest=manifest['binding_digest'],run_id=record['execution']['run_id'],
        pointer_convention='Decoded codec record tree; original product-byte references.',
        hints=rows,lineages=registry,mechanisms=changes,candidate_gains=gains,candidate_losses=losses,
        gain_count=len(gains),loss_count=len(losses),coverage=dict(determinate=7,total=7),
        real_execution_authorized=False,parent_process_limited=False)

def pins(path):
    folder=Path(path).parent
    names=['binding.json','manifest.json','inventory.json','resources.json','claim.json']
    names += ['product/'+n for n in ('record.json','verification.json','terminal.json')]
    names += ['observer/'+p.name for p in sorted((folder/'observer').iterdir()) if p.is_file()]
    return [e.p1.reference(folder/n) for n in names]

def publish(path):
    value,ledger=e.load(path,consumed=True)
    folder=Path(path).parent/'appendix';folder.mkdir()
    initial=pins(path)
    try:
        observe(path);record,manifest,terminal=e.read_product(path,ledger)
        report=evaluate(record,manifest,{Path(r['path']).name:r for r in initial
            if '/product/' in r['path'] or Path(r['path']).name in ('binding.json','manifest.json')})
        e.atomic(folder/'provenance.json',e.canonical(report),ledger)
        e.need(pins(path)==initial,'P2_ORIGINAL_BYTES_CHANGED')
        closure=dict(version='s2uc.appendix.p2.supplier-correction',status='CLOSED_NEUTRAL_PROVENANCE',
            scope=e.scope(value),test_evidence=True,
            product_status=terminal['status'],originals=initial,
            report=e.p1.reference(folder/'provenance.json'),real_execution_authorized=False,
            parent_process_limited=False)
        e.atomic(folder/'appendix-terminal.json',e.canonical(closure),ledger)
        e.need(pins(path)==initial,'P2_ORIGINAL_BYTES_CHANGED')
        return dict(status=closure['status'],gain_count=report['gain_count'],loss_count=report['loss_count'],
                    real_execution_authorized=False)
    except Exception as exc: return e.fail(folder,ledger,str(exc),appendix=True)

def read(path):
    value,ledger=e.load(path,consumed=True);folder=Path(path).parent/'appendix'
    e.need(folder.is_dir() and {p.name for p in folder.iterdir()}=={'provenance.json','appendix-terminal.json'},'P2_APPENDIX_FILES')
    closure=e.read_json(folder/'appendix-terminal.json')
    e.need(closure['status']=='CLOSED_NEUTRAL_PROVENANCE' and closure['originals']==pins(path)
        and closure['report']==e.p1.reference(folder/'provenance.json'),'P2_APPENDIX_CHANGED')
    observe(path);record,manifest,_=e.read_product(path,ledger)
    report=e.read_json(folder/'provenance.json')
    refs={Path(r['path']).name:r for r in closure['originals'] if '/product/' in r['path']
        or Path(r['path']).name in ('binding.json','manifest.json')}
    e.need(e.canonical(report)==e.canonical(evaluate(record,manifest,refs)),'P2_PROVENANCE_CHANGED')
    return report
