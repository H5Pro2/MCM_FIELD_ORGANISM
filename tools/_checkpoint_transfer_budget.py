"""Reachable physical publications, using unchanged native item limits."""
VERSION='checkpoint.transfer-budget.v3'
LIMITS=dict(metadata=196608,sources=196608,shared=262144,verification=262144,total=5242880)
WORK=dict(worker_checkpoint_validations=2,total_checkpoint_validations=1,
          total_record_validations=2,total_formation_checks=22,total_scan_checks=8,
          field_advances_in_verification=0,receptor_calls_in_verification=0)


def parts(k):
    # AV AV AV AV A V AV. A completed prefix retains its initial state.
    forms=min(k,4)+int(k==7)
    cues=int(k>=5)+int(k>=6)
    audio=min(k,5)+int(k==7)
    return dict(native=(forms+1)*98304+k*32768+cues*2*32767,
                nj=audio*1024,formations=forms*1536,generations=forms*1536,field=0)


def envelope(source_bytes,metadata_bytes=None):
    if metadata_bytes is None:
        raise ValueError('TRANSFER_METADATA_DERIVATION_REQUIRED')
    rows=[]
    def add(phase,items,verification=0):
        if isinstance(metadata_bytes,dict):
            if '-prefix-' in phase:
                role,n=phase.split('-prefix-');meta=metadata_bytes[role+'-failure-'+n]
            elif phase=='checkpoint-link':
                meta=max(metadata_bytes[phase],metadata_bytes['save-failure-4'])
            else:
                meta=max(metadata_bytes[p] for p in ('success','parent-failure',
                    'parent-budget-failure','final-ledger-publication','final-ledger-write-failure'))
        else:meta=metadata_bytes
        sums={key:sum(count*value[key] for count,value in items) for key in parts(0)}
        total=source_bytes+meta+verification+sum(sums.values())
        shared=source_bytes+sums['nj']+sums['formations']+sums['generations']
        amounts=dict(metadata=meta,sources=source_bytes,shared=shared,
                     verification=verification,total=total)
        rows.append(dict(phase=phase,parts=sums,totals=amounts,
            violations=[key for key,limit in LIMITS.items() if amounts[key]>limit]))
    full=parts(7)
    checkpoint=dict(parts(4),field=426580)
    for k in range(8):
        add('reference-prefix-'+str(k),[(2,parts(k))])
    for k in range(5):
        add('save-prefix-'+str(k),[(1,full),(2,parts(k))])
    add('checkpoint-link',[(1,full),(2,checkpoint)])
    for k in range(4,8):
        add('restore-prefix-'+str(k),[(1,full),(1,checkpoint),(2,parts(k))])
    add('verification',[(2,full),(1,checkpoint)],262144)
    # The verification limit is shared by permanent and temporary evidence.
    # On failure, an existing pending/public record is referenced, never copied again.
    return dict(version=VERSION,rows=rows,limits=LIMITS,work=WORK,
        violations=[r['phase'] for r in rows if r['violations']],
        metadata_scope='All common, dispatch, authorization, logs, administrative and closure files together.',
        failure_scope='Prefix alternatives include both publication names; existing evidence is referenced on later failures.')
