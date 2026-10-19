"""Serialized format bounds, not fabricated runtime states or measurements."""
from tools import _memory_checkpoint_ledger as ledger
from tools import _checkpoint_transfer_budget as transfer_budget

H='f'*64


def snapshot(run_id):
    return dict(schema='s2mr.private.minimal-mcm-runtime-336.v1',runtime_id=run_id,
        config_digest=H,field_state_digest=H,memory_state_digest=H,stream_state_digest=H,
        snapshot_digest=H,status='CLOSED',field_attempt_count=7,max_event_count=7,
        memory_formation_attempt_count=5,next_ordinal=8,processed_event_count=7,scan_attempt_count=4)


def field_wrapper():
    return dict(field_component_digest=H,state_digest=H,last_end_tick=1300000000,
                phase='PRE_CONTACT',step_count=7)


def account():
    return dict(mode='CALLER_PAYLOADS',completed_events=7,
        counts=dict(payloads=12,audio=6,nj=6,visual=6,materialized_events=7),
        reads=dict(actual_read_bytes=37440000,read_operations=12))


def reference(key):return {'$checkpoint_common':key,'sha256':H}


def record(run_id,n):
    forms=min(n,4)+int(n==7);cues=int(n>=5)+int(n>=6)
    rows=[dict(x=0,formation={} if i<4 or i==6 else None,
               generations={} if i<4 or i==6 else None) for i in range(n)]
    receipts=[dict(nj=None if i==5 else {},rgb_digest=H,source_digest=H) for i in range(n)]
    # Native item bodies are omitted only in this format calculation. Their complete
    # caps are charged separately; keys, separators and native container overhead remain.
    return dict(schema='s2ob.caller.v2',status='RECORDING_COMPLETE',run_id=run_id,
        config_digest=H,runtime_config=reference('runtime_config'),binding=reference('binding'),
        initial=dict(field=field_wrapper(),memory=H,snapshot=snapshot(run_id)),final=snapshot(run_id),
        inputs=[{} for _ in range(n)],source_receipts=receipts,rows=rows,
        states={format(i,'064x'):{} for i in range(forms+1)},scans=[{} for _ in range(cues*2)],
        failure=None,main_gate=False,record_digest=H)


def point(run_id):
    return dict(snapshot=snapshot(run_id),field_component_digest=H,memory_digest=H,
                births=[None]*24,chain=H,accounting=account())


def checkpoint(run_id):
    stream=dict(schema='s2lm.role-free-perception-stream.v1',stream_id=run_id,status='OPEN',
        field_state_digest=H,memory_state_digest=H,state_digest=H,last_event_digest=H,
        field_attempt_count=7,memory_formation_attempt_count=5,next_ordinal=8,
        processed_event_count=7,scan_attempt_count=4)
    return dict(schema='mcm.system-checkpoint.v1',status='SUSPENDED_PREFIX',field_class='FIELD_CHECKPOINT.v1',
        manifest=reference('manifest'),code_digest=H,process_id=4294967295,stream=stream,field={},
        field_wrapper=field_wrapper(),prefix=record(run_id,4),births=[None]*24,chain=H,
        accounting=account(),main_gate=False,checkpoint_digest=H)


def metadata(value):return ledger.classify(ledger.size(value),value)['metadata']


def ledger_diagnostic(paths,source_paths):
    classes={k:9999999999 for k in ('metadata','sources','verification','field','nj',
                                  'formations','generations','native','input_stock')}
    files=[dict(path=p,bytes=9999999999,classes=classes,reference=True) for p in paths]
    files += [dict(path=p,bytes=9999999999,classes={'sources':9999999999},reference=True) for p in source_paths]
    totals=dict(classes,shared=9999999999,total=9999999999)
    return dict(files=files,totals=totals,limits=transfer_budget.LIMITS,violations=list(transfer_budget.LIMITS))


def derive(run_id,administrative_parts,source_paths,external_paths):
    rows=[]
    base=sum(administrative_parts.values())
    common_names=['common.json','preregistration.json','dispatch.json']
    checkpoint_names=['checkpoint.json','checkpoint.json.consumed']
    def arm(role,n):
        value=dict(status='RECORDING_COMPLETE',record=record(run_id,n),role=role,pid=4294967295,
                   cut=point(run_id),accounts=[account() for _ in range(n)],closed=True,gate=False)
        if role=='save':
            value.pop('record');value['status']='SUSPENDED_PREFIX';value['checkpoint_digest']=H
        return value
    def add(phase,parts):
        total=base+sum(parts.values())
        rows.append(dict(phase=phase,administrative_base=base,parts=parts,
                         metadata=total,limit=transfer_budget.LIMITS['metadata'],
                         excess=max(0,total-transfer_budget.LIMITS['metadata'])))
    # Logs of all preceding successful children remain charged at the capture cap;
    # the current implementation does not require successful children to be silent.
    for role,start,end in [('reference',0,7),('save',0,4),('restore',4,7)]:
        previous=[];prior_metadata=0
        if role!='reference':
            previous+=['reference.json','reference.claim','reference.stdout','reference.stderr']
            prior_metadata+=metadata(arm('reference',7))
        if role=='restore':
            previous+=['save.json','save.claim','save.stdout','save.stderr']+checkpoint_names
            prior_metadata+=metadata(arm('save',4))+metadata(checkpoint(run_id))+64
        for n in range(start,end+1):
            names=common_names+previous+[role+'.claim',role+'.stdout',role+'.stderr',role+'-failure.json',role+'-failure.json.pending']+list(external_paths)
            diagnostic=ledger_diagnostic(names,source_paths)
            failure=dict(status='NOT_EVALUABLE',role=role,pid=4294967295,closed=True,gate=False,
                failure=dict(code='TRANSFER_BUDGET',phase='CHECKPOINT_PUBLISH',completed_events=n,
                    snapshot=snapshot(run_id),accounting=account(),details=diagnostic),
                prefix=record(run_id,n),available_evidence=None,accounting=account())
            log_count=1+int(role!='reference')+int(role=='restore')
            add(role+'-failure-'+str(n),dict(previous_records=prior_metadata,logs=log_count*8192,
                failure_publication=2*metadata(failure),role_claims=3*256))
    add('success',dict(records=metadata(arm('reference',7))+metadata(arm('save',4))+metadata(arm('restore',7)),
        checkpoint=metadata(checkpoint(run_id)),logs=3*8192,role_claims=3*256,
        process_records=ledger.size([dict(role=r,exit_code=0,wait_completed=True) for r in ('reference','save','restore')]),
        consumed_checkpoint=64,verification_claim=4))
    add('checkpoint-link',dict(previous_records=metadata(arm('reference',7)),
        checkpoint_publication=2*metadata(checkpoint(run_id)),logs=2*8192,role_claims=2*256))
    # Parent diagnostics contain the completed stages, not the child's complete ledger.
    parent=dict(status='NOT_EVALUABLE',failure=dict(code='TRANSFER_CHILD_FAILED',
        phase='PROCESS_OR_CLOSURE',details=dict(active_role='reference',completed_stages=[
            dict(role=r,exit_code=-4294967295,wait_completed=True) for r in ('reference','save','restore')]),
        progress={}),gate=False,artifact_saved=False)
    terminal_records=metadata(arm('reference',7))+metadata(arm('save',4))+metadata(arm('restore',7))+metadata(checkpoint(run_id))
    add('parent-failure',dict(records=terminal_records,logs=3*8192,
        parent_error_publication=2*metadata(parent),role_claims=3*256,checkpoint_consumption=64))
    add('initialization-failure',dict(parent_error=metadata(parent),role_claims=3*256))
    terminal_names=common_names+checkpoint_names+[
        role+suffix for role in ('reference','save','restore')
        for suffix in ('.json','.claim','.stdout','.stderr')]
    terminal_names+=['processes.json','verification.claim','verification.json','evaluation.json',
                     'final-balance.json','final-balance.json.pending','failure.json','failure.json.pending']
    diagnostic=ledger_diagnostic(terminal_names+list(external_paths),source_paths)
    final_balance=dict(diagnostic,closure=dict(final_balance_bytes=9999999999,gate=False))
    budget_failure=dict(parent)
    budget_failure['failure']=dict(code='TRANSFER_BUDGET',phase='PROCESS_OR_CLOSURE',details=diagnostic,progress={})
    add('final-ledger-publication',dict(records=terminal_records,logs=3*8192,
        final_balance_publication=2*metadata(final_balance),role_claims=3*256,checkpoint_consumption=64))
    add('parent-budget-failure',dict(records=terminal_records,logs=3*8192,
        error_publication=2*metadata(budget_failure),role_claims=3*256,checkpoint_consumption=64))
    # After link/unlink failure both ledger names may survive. The write error then
    # contains only path/existence flags, not another recursively embedded ledger.
    add('final-ledger-write-failure',dict(records=terminal_records,logs=3*8192,
        final_balance_names=2*metadata(final_balance),parent_error_names=2*metadata(parent),
        role_claims=3*256,checkpoint_consumption=64))
    return dict(version='checkpoint.metadata-forms.v2',rows=rows,administrative_parts=administrative_parts,
        maximum=max(r['metadata'] for r in rows),violations=[r['phase'] for r in rows if r['excess']],
        scope='Concrete serialized success and child-error envelopes; positive excess blocks qualification. '
              'An upper-bound excess is not a measured file size or proof of unavoidable minimum size.')
