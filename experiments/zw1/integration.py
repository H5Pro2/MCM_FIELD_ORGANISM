"""Neutral pair receipts around unchanged ER1 policy and independent references."""
import gc,json,time,hashlib
from pathlib import Path
from . import sources
from tools._s2uc_ura1_fs_accounting_v4 import Terminal,Ledger,inventory
from tools._s2uc_er1_v2_series import policy_case
from tools._s2uc_ura1_v2_series import LIMITS

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def condition_receipt(pair,label,report):
    if not report['complete'] or not report['cleanup'] or report['integrity']!='PASS_DELTA_INTEGRITY':raise ValueError('CONDITION_INCOMPLETE')
    return dict(pair=pair,condition=label,complete=True,cleanup=True,integrity=report['integrity'],
        targets=[r['target'] for r in report['rows']],E=[r['E'] for r in report['rows']],F=[r['F'] for r in report['rows']])

def pair_receipt(pair,conditions):
    if set(conditions)!={'A','B'}:raise ValueError('PAIR_INCOMPLETE')
    for label,c in conditions.items():
        if c['pair']!=pair or c['condition']!=label or not c['complete'] or not c['cleanup'] or c['integrity']!='PASS_DELTA_INTEGRITY':raise ValueError('PAIR_BINDING')
    if conditions['A']['targets']!=conditions['B']['targets']:raise ValueError('PAIR_TARGETS')
    return dict(pair=pair,orientation=(pair-1)%2,complete=True,conditions=conditions)

def run(folder,mode,prep_bytes=0):
    if mode not in ('complete','archive_failure','source_failure'):raise PermissionError('NEUTRAL_MODE_ONLY')
    from tools import _s2uc_er1_run_engine as engine
    from tools import _s2uc_er1_v2_archive as archive
    from tools import _s2uc_ura1_delta_encode as codec
    folder=Path(folder);folder.mkdir(exist_ok=False);started=time.monotonic()
    terminal=Terminal(folder,started,prep_bytes);ledger=Ledger(terminal,prep_bytes)
    created=[];completed=[];source_manifest=[];counts=dict(policy_started=0,policy_completed=0,live_reference_completed=0,archive_reference_started=0,archive_reference_completed=0,extra_policy_measurement=0)
    original_create=engine.create;original_run=engine.run_arm;original_verify=archive.verify
    state=dict(pair=None,condition=None,barrier=False)
    def verify_seal():
        if not state['barrier'] or sha(folder/'sources-manifest.json')!=terminal.value['source_manifest_sha256']:raise ValueError('SOURCE_BARRIER')
        for item in source_manifest:
            if sha(folder/item['path'])!=item['sha256']:raise ValueError('SOURCE_CHANGED')
    def create(mode):
        verify_seal()
        if len(created)>=8:raise ValueError('NEUTRAL_ARM_LIMIT')
        a=original_create(mode)
        if a.accepted or a.closed or a.arm._candidate or a.arm._retained_many:raise ValueError('ARM_NOT_FRESH')
        if any(a is b for b in created):raise ValueError('ARM_REUSE')
        created.append(a);counts['policy_started']+=1
        return a
    def measured(*args,**kwargs):
        result=original_run(*args,**kwargs)
        counts['policy_completed']+=1;counts['live_reference_completed']+=1
        return result
    def reference(blob,proof,expected):
        counts['archive_reference_started']+=2
        if mode=='archive_failure' and state['pair']==2 and state['condition']=='B':
            # Deliberately wrong capture anchor; real archive verifier must reject it.
            expected=expected|dict(original_sha256='0'*64)
        result=original_verify(blob,proof,expected)
        counts['archive_reference_completed']+=2
        return result
    engine.create=create;engine.run_arm=measured;archive.verify=reference
    try:
        for pair in (1,2):
            description=sources.generate(pair,24);independent=sources.reconstruct(pair,24)
            if description!=independent:raise ValueError('SOURCE_RECONSTRUCTION')
            for label in ('A','B'):
                value=sources.materialize(description,label);sources.verify_material(value,independent,label)
                name=f'pair-{pair:02d}-{label}-source.json';digest=ledger.write(name,value,'source')
                source_manifest.append(dict(pair=pair,condition=label,path=name,sha256=digest))
        ledger.write('sources-manifest.json',dict(namespace=sources.NEUTRAL,all_before_policy=True,entries=source_manifest))
        terminal.value['source_manifest_sha256']=sha(folder/'sources-manifest.json');terminal.value['sources_sealed_before_policy']=not created
        state['barrier']=True;terminal.save()
        if mode=='source_failure':
            # Change only this neutral copy after sealing, before any policy arm.
            with (folder/source_manifest[0]['path']).open('ab') as f:f.write(b' ')
        for pair in (1,2):
            terminal.value['active_case']=pair;terminal.save();conditions={}
            for label in ('A','B'):
                state.update(pair=pair,condition=label);verify_seal()
                item=next(x for x in source_manifest if x['pair']==pair and x['condition']==label)
                value=json.loads((folder/item['path']).read_bytes())
                number=2*(pair-1)+(1 if label=='A' else 2)
                report=policy_case(number,value,ledger,neutral=True)
                conditions[label]=condition_receipt(pair,label,report)
                del report,value;gc.collect()
            receipt=pair_receipt(pair,conditions)
            ledger.write(f'pair-{pair:02d}-receipt.json',receipt)
            completed.append(receipt);terminal.value['completed_cases'].append(pair);terminal.save()
        terminal.value.update(status='TERMINAL_COMPLETE',active_case=None)
    except Exception as error:
        terminal.diagnose(error,'neutral_pair');terminal.value['status']='TECHNICAL_ABORT'
    finally:
        engine.create=original_create;engine.run_arm=original_run;archive.verify=original_verify
        clean=all(a.closed and not any(a.bank) for a in created) and codec.ACTIVE is None
        terminal.value.update(cleanup='CONFIRMED' if clean else 'UNCONFIRMED',arms_created=len(created),distinct_arms=len({id(a) for a in created}),executions=counts,seconds=time.monotonic()-started,partial_files=[p.name for p in folder.glob('*.partial')],research=False)
        terminal.save()
    return terminal.value,completed
