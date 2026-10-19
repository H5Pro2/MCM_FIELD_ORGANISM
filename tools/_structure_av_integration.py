"""Bound five-event OC composition; comparison never gates technical validity."""
import json
from pathlib import Path
from reports.s2oc import run_bound_session_once as caller
from tools import _s2oc_shared_verification as verification

s=caller.shared
b=caller.b
VERSION='structure-av.integration.v2'
MAIN_GATE=False
OUTER_CAPS={'evaluation.json':3000,'integration-error.json':1024,'integration-balance.json':1536,
            'integration.claim':5}


def candidates(state,cue):
    groups=(('B4',state['b4_state']['entries'],'values',48),
            ('FAST',state['tspm_state']['fast_state']['slots'],'visual_values',0),
            ('SLOW',visual(state)['slots'],'prototype_values',0))
    result={}
    for name,slots,key,start in groups:
        available=[];equal=[]
        for n,slot in enumerate(slots):
            values=slot[key]
            usable=len(values)>0 and (name!='SLOW' or slot['support_count']>=3)
            if usable:available.append(n)
            if usable and b.canonical(list(values[start:start+32]))==b.canonical(list(cue[:32])):equal.append(n)
        result[name]=dict(available=available,visible_equal=equal)
    return result


def visual(state):
    return state['tspm_state']['visual_ppb1_state']


def assessment(record,proof,direct):
    s.need(proof['evaluation_allowed'] and proof['core']['record_digest']==record['record_digest'],
           'EVALUATION_GATE')
    core=record['execution'];states=core['states']
    decoded={key:b.state_wire.decode(value) for key,value in states.items()}
    rows=[]
    previous=decoded[core['initial']['memory']]
    for i,row in enumerate(core['rows'][:4]):
        current=decoded[row['memory']]
        bank=visual(current);prebank=visual(previous)
        supplied=next(t['frame']['values'] for t in core['inputs'][i]['field']['timed_frames']
                      if t['frame']['modality_id']=='visual')
        reference=direct['chains'][0]
        expected=reference['states'][i] if i else reference['states'][0]
        # Comparison excludes independently bound presentation clocks/digests.
        semantic=lambda x:[{k:v for k,v in slot.items() if k in
            ('occupied','prototype_values','support_count','slot_id','last_selected_step')} for slot in x['slots']]
        rows.append(dict(ordinal=i+1,fast_support=[x['support_count'] for x in current['tspm_state']['fast_state']['slots']],
            ppb_steps=bank['accepted_step_count'],advanced=bank['accepted_step_count']!=prebank['accepted_step_count'],
            input_equal_direct=None if i==0 else b.canonical(supplied)==b.canonical(reference['steps'][i-1]['frame']['values']),
            slots_equal_direct=b.canonical(semantic(bank))==b.canonical(semantic(expected)),
            visual_support=[x['support_count'] for x in bank['slots']],generation_binding=row['chain_digest']))
        previous=current
    # Native scan details stay in the verified record; do not rescan.
    return dict(version=VERSION,status='DESCRIPTIVE_ONLY',formations=rows,
        candidates=candidates(previous,next(t['frame']['values'] for t in core['inputs'][4]['field']['timed_frames']
            if t['frame']['modality_id']=='visual')),
        cue_readonly=core['rows'][4]['memory']==core['rows'][3]['memory'],
        cue_step={k:core['rows'][4]['step'][k] for k in ('context_status','memory_status','hypothesis','step_digest')},
        scan_references=[dict(ordinal=x['ordinal'],role=x['role']) for x in core['scans']],
        public_success_not_implied_by_stability=True)


def envelope(common,external_bytes):
    upper=verification.preflight(common)
    # External historical evidence is neither session metadata nor source code.
    # It remains fully charged under the unchanged overarching total limit.
    rows=[]
    for row in upper['positions']:
        for name in ('success','failure'):
            totals=dict(row[name]);totals['total']+=external_bytes+2565
            totals['metadata']+=2565
            rows.append(dict(completed=row['completed'],alternative=name,totals=totals,
                violations=[key for key,value in totals.items() if value>b.LIMITS[key]]))
    return dict(version=VERSION,external_evidence=external_bytes,positions=rows,
                violations=[x for x in rows if x['violations']])


def pin(path):
    path=Path(path)
    return dict(path=path.relative_to(b.ROOT).as_posix(),sha256=s.sha(path.read_bytes()),bytes=path.stat().st_size)


def admission(path,expected_sha,output,neutral):
    value=s.read_json(path)
    s.need(s.sha(b.canonical(value))==expected_sha and value['version']==VERSION,'ADMISSION_PIN')
    s.need(value['authorized'] is True and value['neutral'] is neutral,'ADMISSION_GATE')
    s.need(Path(output).resolve()==(b.ROOT/value['output']).resolve() and not Path(output).exists(),'OUTPUT_USED')
    for item in value['files'].values():
        try:s.need(pin(b.ROOT/item['path'])==item,'ADMISSION_SOURCE')
        except OSError as exc:raise caller.entry.budget.BudgetError('ADMISSION_REFERENCE_MISSING') from exc
    qualification=s.read_json(b.ROOT/value['files']['qualification']['path'])
    s.need(qualification['status']=='QUALIFIED','ADMISSION_QUALIFICATION')
    common=s.read_json(b.ROOT/value['files']['common']['path'])
    s.need(common['manifest']['run_id']==value['run_id'],'ADMISSION_RUN')
    reference=s.read_json(b.ROOT/value['files']['direct']['path'])
    proof=s.read_json(b.ROOT/value['files']['direct_proof']['path'])
    s.need(proof['status']=='EVIDENCE_VALID' and proof['record_digest']==b.digest(reference)
           and value['chain']==0 and value['source_indices']==[3,4,5]
           and [r['source_index'] for r in reference['chains'][0]['steps']]==[3,4,5],'DIRECT_BINDING')
    return value,common,reference


def actual_balance(output,common,external):
    output=Path(output)
    record,session=s.unpack(s.read_json(output/'record.json'),s.read_json(output/'session.json'),common)
    proof_size=(output/'verification.json').stat().st_size if (output/'verification.json').exists() else 0
    measured=s.ledger(record,session,common,proof_bytes=proof_size,report_bytes=0)
    files={p.name:p.stat().st_size for p in output.iterdir() if p.is_file()}
    extra=sum(n for name,n in files.items() if name not in ('record.json','session.json','verification.json','integration-balance.json'))
    measured['totals']['metadata']+=extra+1536
    measured['totals']['total']+=extra+1536+external
    return dict(totals=measured['totals'],files=files,external_evidence=external,
        violations=[k for k,n in measured['totals'].items() if n>b.LIMITS[k]],
        incomplete_temporary_files=[n for n in files if n.endswith('.tmp')])


def run(admission_path,expected_sha,output,*,neutral=False):
    global MAIN_GATE
    s.need(MAIN_GATE,'MAIN_GATE_CLOSED');MAIN_GATE=False
    permit,common,reference=admission(admission_path,expected_sha,output,neutral)
    locate=lambda key:b.ROOT/permit['files'][key]['path']
    common_path=locate('common');inventory_path=locate('inventory')
    external=permit['files']['direct']['bytes']+permit['files']['direct_proof']['bytes']+len(b.canonical(permit))
    bound=envelope(common,external)
    s.need(not bound['violations'],'COMPLETE_BUDGET')
    terminal=None;phase='SESSION'
    try:
        caller.entry.MAIN_GATE=True
        dispatch=caller.run(common_path,s.sha(b.canonical(common)),inventory_path,output,neutral=neutral)
        terminal=dispatch
        if dispatch['status']=='RECORDING_COMPLETE':
            phase='EVALUATION'
            proof=s.read_json(Path(output)/'verification.json')
            record,_=s.unpack(s.read_json(Path(output)/'record.json'),s.read_json(Path(output)/'session.json'),common)
            result=assessment(record,proof,reference)
            s.need(len(b.canonical(result))<=3000,'EVALUATION_LIMIT')
            s.prior.save(Path(output)/'evaluation.json',result)
    except Exception as exc:
        terminal=dict(status='NOT_EVALUABLE',phase=phase,primary_code='SESSION_ERROR' if phase=='SESSION' else 'EVALUATION_ERROR',
                      underlying_code=getattr(exc,'code','UNKNOWN_ERROR')[:80],gates=False)
        try:s.prior.save(Path(output)/'integration-error.json',terminal)
        except Exception:terminal['closure_secured']=False
    finally:
        caller.entry.MAIN_GATE=False;MAIN_GATE=False
    try:
        measured=actual_balance(output,common,external)
        s.need(len(b.canonical(measured))<=1536,'OUTER_BALANCE_SIZE')
        s.prior.save(Path(output)/'integration-balance.json',measured)
        s.need(not measured['violations'] and not measured['incomplete_temporary_files'],'OUTER_BALANCE')
    except Exception:
        terminal=dict(status='CLOSURE_NOT_SECURED',primary=terminal,gates=False)
    return terminal
