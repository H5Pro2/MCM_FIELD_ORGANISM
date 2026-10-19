"""Separately authorized one-shot comparison, with bounded atomic closure."""
import json
from pathlib import Path
import hashlib
import numpy as np
from tools import _s2oc_shared_binding as shared
from tools import _visual_b_comparison as c
from tools import _visual_b_ledger as ledger
from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from reports import seal_visual_b_once as sources

SEAL='reports/s2oe/visual-b-source-seal-20260912-02/'


def read(path):
    return json.loads(Path(path).read_bytes())


def load_frozen(root,source):
    c.frozen.require(source.get('profile')=='visual.grid12x8.channels3.source1920x1080.v1','PROFILE_BINDING')
    base=root/sources.MEM
    ref=read(base/'common-reference.json')
    c.frozen.require(sources.pin(root/ref['path'])=={k:ref[k] for k in ('bytes','sha256')},'COMMON_PIN')
    common=read(root/ref['path'])
    record,_=shared.unpack(read(base/'record.json'),read(base/'session.json'),common)
    expected={k:source['frozen'][k] for k in ('memory_digest','chain_digest','births','row')}
    c.frozen.require(source['frozen']['runtime_config_digest']==common['runtime_config']['config_digest'],'PROFILE_BINDING')
    binding=c.frozen.authenticate(record,read(base/'verification.json'),expected)
    c.frozen.require(sum(s['occupied'] and s['support']>=3 for s in binding['candidates'] if s['bank']=='B')==1,
                     'FROZEN_WORK_BOUND')
    c.frozen.require(binding['candidates'][12]['generation']==expected['births'][20], 'TARGET_GENERATION')
    return binding,record['execution'],expected


def check_admission(path,expected_hash,root):
    path=Path(path).resolve();root=Path(root).resolve()
    c.frozen.require(path.is_relative_to(root) and sources.pin(path)['sha256']==expected_hash,'ADMISSION_PIN')
    permit=read(path)
    c.frozen.require(permit['authorized'] is True and permit['version']==c.VERSION and
                     permit['budget_version']==ledger.VERSION,'ADMISSION')
    files={}
    for name,item in permit['references'].items():
        p=(root/name).resolve()
        c.frozen.require(p.is_relative_to(root) and not Path(name).is_absolute(),'REFERENCE_PATH')
        c.frozen.require(sources.pin(p)=={k:item[k] for k in ('bytes','sha256')},'REFERENCE_CHANGED')
        files[name]=item
    c.frozen.require(permit['inventory'] in files and permit['qualification'] in files,'ADMISSION_REFERENCES')
    inventory=read(root/permit['inventory'])
    for name,item in inventory.items():
        p=(root/name).resolve()
        c.frozen.require(p.is_relative_to(root) and sources.pin(p)=={k:item[k] for k in ('bytes','sha256')},'SOURCE_CHANGED')
        if name in files:c.frozen.require(files[name]==item,'REFERENCE_CONFLICT')
        files[name]=item
    qualification=read(root/permit['qualification'])
    c.frozen.require(qualification['status']=='QUALIFIED' and
        qualification['inventory_digest']==c.frozen.digest(inventory) and
        qualification['version']==c.VERSION,'QUALIFICATION')
    own=path.relative_to(root).as_posix()
    c.frozen.require(own not in files,'ADMISSION_SELF_REFERENCE')
    files[own]=dict(kind='metadata',**sources.pin(path))
    output=(root/permit['output']).resolve()
    c.frozen.require(output.is_relative_to(root) and not output.exists() and
        output.name==permit['run_id'],'OUTPUT_USED')
    upper=ledger.preflight(files)
    ledger.enforce(upper)
    return permit,files,output


def materializer(source,seal,counters):
    receptor=LocalChannelGridReceptor(VisualGridConfig())
    proofs={p['id']:p for p in seal['sources']}
    def next_cue(row):
        data=sources.s.render(row['recipe'],1920,1080)
        c.frozen.require(hashlib.sha256(data).hexdigest()==row['original_sha256'],'ORIGINAL_HASH')
        c.d.modify_and_occlude(data,1920,1080,row['level'],row['rectangle'])
        c.frozen.require(hashlib.sha256(data).hexdigest()==proofs[row['id']]['sha256'],'CUE_HASH')
        frame=np.frombuffer(data,dtype=np.uint8).reshape(1080,1920,3)
        counters['analyses']+=1
        state=receptor.analyze(frame,frame_index=row['window'][0])
        c.frozen.require(all(x==0.0 for x in state.channel_values[32:]),'HIDDEN_VALUES')
        return state.channel_values[:32]
    return next_cue


def execute(output,files,source,evaluation,seal,resolver,make_materializer):
    """Shared native-evidence path; neutral tests supply only neutral adapters."""
    output=Path(output)
    ledger.enforce(ledger.preflight(files))
    output.mkdir(exist_ok=False)
    counters=dict(analyses=0);completed=0;phase='FROZEN_BINDING';primary=None
    def save(name,value):
        raw=sources.s.raw(value)
        c.frozen.require(len(raw)<=ledger.RUN_CAPS[name],'OUTPUT_LIMIT:'+name)
        destination=output/name
        c.frozen.require(not destination.exists(),'ALREADY_PUBLISHED')
        tmp=output/(name+'.tmp')
        with tmp.open('xb') as f:f.write(raw)
        tmp.rename(destination)
    with (output/'claim').open('xb') as f:f.write(b'once\n')
    try:
        binding,core,expected=resolver()
        save('binding.json',binding)
        phase='MATERIALIZE'
        record=c.record_steps(source,binding,make_materializer(source,seal,counters))
        record['analyses']=counters['analyses']
        completed=len(record['rows'])
        if record['status']=='NOT_EVALUABLE':
            primary=dict(status='NOT_EVALUABLE',phase=record['phase'],completed=completed,
                         error_type=record['error_type'],error=record['error'])
        save('record.json',record)
        ledger.enforce(ledger.measure(output,files,phase=phase,completed=completed))
        phase='VERIFY'
        c.frozen.verify_binding(binding,core,expected)
        proof=c.verify(read(output/'record.json'),source,binding)
        save('verification.json',proof)
        if proof['evaluation_allowed']:
            phase='EVALUATE'
            result=c.evaluate(record,proof,evaluation,source)
            result['byte_equal_groups']=seal['collisions']
            save('evaluation.json',result)
        else:
            primary=dict(status='NOT_EVALUABLE',phase=record['phase'],completed=completed,
                         error_type=record['error_type'],error=record['error'])
    except Exception as exc:
        caught=dict(status='NOT_EVALUABLE',phase=phase,completed=completed,
            error_type=type(exc).__name__[:80],error=str(exc)[:256],
            diagnostic_overflow=len(str(exc))>256)
        if isinstance(exc,ledger.BudgetError):
            caught['budget']=dict(parts=exc.balance.get('parts'),
                violations=exc.balance['violations'][:12],limits=ledger.LIMITS)
        if primary is None:primary=caught
        else:primary['closure_error']=caught
    finally:
        c.MAIN_GATE=False
        measured=ledger.measure(output,files,phase=phase,completed=completed)
        if measured['violations'] and primary is None:
            primary=dict(status='NOT_EVALUABLE',phase=phase,completed=completed,
                error='BUDGET_INVALID',budget=dict(parts=measured['parts'],
                limits=ledger.LIMITS,violations=measured['violations'][:12]))
        if primary is not None:save('error.json',primary)
        measured=ledger.measure(output,files,phase=phase,completed=completed)
        measured.update(gates=False,analyses=counters['analyses'],status='NOT_EVALUABLE' if primary else 'RECORDING_COMPLETE')
        save('balance.json',measured)
        ledger.enforce(measured)
    return measured


def run(admission_path,expected_hash):
    c.frozen.require(c.MAIN_GATE,'GATE_CLOSED');c.MAIN_GATE=False
    root=sources.ROOT
    permit,files,output=check_admission(admission_path,expected_hash,root)
    import sys
    c.frozen.require(permit['environment']==dict(interpreter=sources.pin(Path(sys.executable)),
        numpy_version=np.__version__,numpy_init=sources.pin(Path(np.__file__))),'ENVIRONMENT_CHANGED')
    for required in (SEAL+'execution.json',SEAL+'evaluation.json',SEAL+'seal.json',SEAL+'verification.json',
                     sources.MEM+'record.json',sources.MEM+'session.json',sources.MEM+'verification.json',
                     sources.MEM+'common-reference.json'):
        c.frozen.require(required in files,'REQUIRED_REFERENCE')
    c.frozen.require(read(root/(sources.MEM+'common-reference.json'))['path'] in files,'COMMON_REFERENCE')
    source=read(root/(SEAL+'execution.json'));evaluation=read(root/(SEAL+'evaluation.json'))
    seal=read(root/(SEAL+'seal.json'));proof=read(root/(SEAL+'verification.json'))
    c.frozen.require(proof['status']=='BINDING_VALID' and proof['record_digest']==c.frozen.digest(seal)
        and seal['execution_digest']==c.frozen.digest(source) and seal['evaluation_digest']==c.frozen.digest(evaluation),
        'SEALED_ROOTS')
    c.frozen.require(permit['frozen_binding'] in files,'FROZEN_REFERENCE')
    def resolver():
        result=load_frozen(root,source)
        c.frozen.require(result[0]==read(root/permit['frozen_binding']),'FROZEN_CHANGED')
        return result
    return execute(output,files,source,evaluation,seal,resolver,materializer)


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('admission');parser.add_argument('sha256')
    args=parser.parse_args()
    try:
        c.MAIN_GATE=True
        print(json.dumps(run(args.admission,args.sha256)))
    finally:
        c.MAIN_GATE=False
