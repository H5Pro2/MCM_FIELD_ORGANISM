"""Read-only provenance and candidate extraction from a certified frozen record."""
from tools import _visual_b_diagnostic as diagnostic
from tools import _s2ob_private_state_evidence as codec

VERSION = 'visual-b.frozen-provenance.v1'


class FrozenBindingError(ValueError):
    pass


def require(ok, code):
    if not ok:
        raise FrozenBindingError(code)


def digest(value):
    return diagnostic.source.digest(value)


def flat(state):
    return (state['b4_state']['entries'] + state['tspm_state']['fast_state']['slots']
            + state['tspm_state']['auditory_ppb1_state']['slots']
            + state['tspm_state']['visual_ppb1_state']['slots'])


def _extract(core, expected):
    """Caller must first authenticate the enclosing record and historical proof.

    This checks the stored provenance chain, not a replay of formations or an
    independent numerical proof of their updates. Values use the existing codec.
    """
    require(set(expected)=={'memory_digest','chain_digest','births','row'},'FROZEN_FORM')
    require(expected['row']==3 and len(core['rows'])>=4,'FROZEN_POSITION')
    selected=core['rows'][3]
    require(selected['memory']==expected['memory_digest'] and
            selected['chain_digest']==expected['chain_digest'] and
            selected['current_births']==expected['births'],'FROZEN_BINDING')
    previous=[None]*24
    histories=[[] for _ in range(24)]
    chain=digest(dict(initial=core['initial']['memory'],config=core['config_digest']))
    for ordinal,row in enumerate(core['rows'][:4],1):
        gen=row['generations']
        require(type(gen) is dict and gen['event']==ordinal and gen['previous']==chain,
                'GENERATION_ORDER')
        require(gen['chain_digest']==digest({k:v for k,v in gen.items() if k!='chain_digest'}),
                'GENERATION_DIGEST')
        require(gen['transaction']==row['formation']['result_digest'],'TRANSACTION_BINDING')
        require(len(gen['actions'])==len(gen['births'])==24,'GENERATION_SHAPE')
        state=codec.decode(core['states'][row['memory']])
        require(state['state_digest']==row['memory'],'STATE_BINDING')
        slots=flat(state)
        for i,(action,birth,slot) in enumerate(zip(gen['actions'],gen['births'],slots,strict=True)):
            if action in ('CREATED','REPLACED'):
                require(slot['occupied'] and birth==ordinal,'GENERATION_CREATION')
                histories[i]=[ordinal]
            elif action=='MATCHED':
                require(slot['occupied'] and previous[i] is not None and birth==previous[i],
                        'GENERATION_MATCH')
                histories[i].append(ordinal)
            elif action=='UNCHANGED':
                require(slot['occupied'] and birth==previous[i] and birth is not None,
                        'GENERATION_UNCHANGED')
            else:
                require(action in ('FREE','CLEARED') and not slot['occupied'] and birth is None,
                        'GENERATION_FREE')
                histories[i]=[]
        require(row['current_births']==gen['births'] and row['chain_digest']==gen['chain_digest'],
                'CURRENT_GENERATION')
        previous=list(gen['births']);chain=gen['chain_digest']
    candidates=[]
    for i,slot in enumerate(slots):
        if 12<=i<20:
            continue
        bank='B4' if i<9 else 'FAST' if i<12 else 'B'
        key='values' if bank=='B4' else 'visual_values' if bank=='FAST' else 'prototype_values'
        values=slot[key][48:] if bank=='B4' else slot[key]
        occupied=slot['occupied']
        require(len(values)==(288 if occupied else 0),'CANDIDATE_SHAPE')
        candidates.append(dict(bank=bank,flat_index=i,slot_id=slot['slot_id'],
            slot_digest=digest(slot),occupied=occupied,support=slot.get('support_count'),
            values=list(values),generation=previous[i],formation_ordinals=histories[i]))
    result=dict(version=VERSION,memory_digest=selected['memory'],chain_digest=chain,
                candidates=candidates,source_record_required=True,
                historical_transition_proof_required=True)
    result['binding_digest']=digest(result)
    return result


def extract(core,expected):
    try:
        return _extract(core,expected)
    except FrozenBindingError:
        raise
    except (KeyError,IndexError,TypeError,ValueError) as exc:
        raise FrozenBindingError('FROZEN_NATIVE_INVALID') from exc


def authenticate(record,proof,expected):
    try:
        require(record['record_digest']==digest({k:v for k,v in record.items() if k!='record_digest'}),
                'NATIVE_RECORD_DIGEST')
        require(proof['evaluation_allowed'] is True and proof['core']['record_digest']==record['record_digest'],
                'HISTORICAL_PROOF')
        require(record['status']=='RECORDING_COMPLETE','HISTORICAL_INCOMPLETE')
        return extract(record['execution'],expected)
    except FrozenBindingError:
        raise
    except (KeyError,IndexError,TypeError,ValueError) as exc:
        raise FrozenBindingError('HISTORICAL_FORM') from exc


def verify_binding(binding,core,expected):
    # No memory operations: resolve the authenticated source, then compare the
    # full candidate descriptors instead of accepting standalone slot labels.
    require(binding==extract(core,expected),'CANDIDATE_ORIGIN')
    return dict(status='FROZEN_BINDING_VALID',binding_digest=binding['binding_digest'],
                formation_replay=False)
