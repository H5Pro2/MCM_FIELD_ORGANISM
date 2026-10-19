"""U/A1 replay and observer. Source/modal annotations never enter the adapter."""
import json
from fractions import Fraction
from tools._s2uc_a1 import create, POLICY as A1
from tools._s2uc_a1_reference import Reference
from tools._s2uc_k1_reference import Reference as UReference
from tools._s2uc_k1_probe import snapshot, error, cellmap, keyset
from tools._s2uc_multi_observer import POLICY, PerceptionSample, HEAD, ENTRY
from tools._s2uc_ulz1_resources import Meter
from tools._s2uc_ulz1_last import LastErrorAdapter
from tools._s2uc_factor_recency import FactorRecencyArm
from tools._s2uc_t1_evidence_v2 import expected_matches, match_core, key, select


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def compact(stock):
    def item(t):
        return None if t is None else {k:v for k,v in t.items() if k != 'values'}
    return stock | dict(candidate=item(stock['candidate']), retained=[item(t) for t in stock['retained']])


def replay(values, profile, enabled, check, fault=None, last=False):
    values = [tuple(v) for v in values]
    a = create(profile, 'comparison', 'stream', admission_policy=A1 if enabled else 'disabled', multi_policy=POLICY)
    need(not enabled, 'A1_FORBIDDEN')
    if last:
        a = LastErrorAdapter(FactorRecencyArm(profile, 'comparison'), 'stream', multi_policy=POLICY)
    if fault is not None:
        need(enabled and fault in ('a1_revision','a1_receipt'),'NEUTRAL_FAULT_KIND')
        armed=False
        def checkpoint(stage,index):
            nonlocal armed
            if stage=='a1_prepared':armed=True
            if armed and stage==fault:raise RuntimeError('INJECTED_A1:'+fault)
        a._checkpoint=checkpoint
    ref = Reference() if enabled else UReference(False)
    meter = Meter(a)
    expected, history, lineage = {}, {}, {}
    rows, events, forecasts = [], [], []
    pending = None
    slots_peak = 0
    revision = 0
    admissions, confirmations = [], []
    def rekey(old, new, at, kind):
        for mapping in (expected, history, lineage):
            for k in list(mapping):
                if k[:2] == tuple(old):
                    dest = tuple(new)+(k[2],)
                    mapping[dest] = mapping.pop(k)
        for off in (0,1):
            dest = tuple(new)+(off,)
            lineage.setdefault(dest, []).append(dict(at=at,kind=kind,old_key=list(old)+[off],new_key=list(dest)))
        live=keyset(ref)
        for mapping in (expected,history,lineage):
            for k in list(mapping):
                if k[:2] not in live:del mapping[k]
    try:
        for i, vector in enumerate(values, 1):
            check()
            sample = PerceptionSample(vector, profile, 'comparison', 'stream', i, (i-1)*4800, i*4800)
            if pending is not None:
                updates = []
                for h in pending['hypotheses']:
                    k = tuple(h['key']); live = k[:2] in keyset(ref)
                    ec = error(values[h['original']-1], vector)
                    ep = error(values[i-2], vector)
                    if live:
                        old = expected.get(k)
                        expected[k] = (ec, ep) if old is None or last else (.5*old[0]+.5*ec, .5*old[1]+.5*ep)
                        history.setdefault(k, []).append(i)
                    updates.append(dict(key=list(k), ordinals=h['ordinals'], offset=h['offset'], live=live, ec=ec, ep=ep))
                chosen = pending['selected']
                predicted = values[i-2] if chosen is None else values[chosen['original']-1]
                need(tuple(a.selected_values) == predicted, 'FROZEN_OUTPUT')
                measured = error(a.selected_values, vector)
                meter.measure('feedback', lambda:a.consume_feedback(sample))
                need(cellmap(a) == expected, 'FEEDBACK_REFERENCE')
                rows.append(pending | dict(error=measured, updates=updates))
                pending = None
            before = ref.snapshot()
            before_cells=[dict(key=list(k),values=list(v),prior_feedback=list(history.get(k,[]))) for k,v in expected.items()]
            admission=None
            original=None if a.arm._candidate is None else a.arm._candidate.frames
            if i%2==0 and enabled:
                admission=ref.preforecast([(i-1,values[i-2]),(i,vector)])
                if admission:
                    rekey(admission['old_key'],admission['new_key'],i,'PARTIAL')
                    revision+=1
                    admissions.append(dict(at=i,**admission))
            forecast_stock=ref.snapshot()
            receipt = meter.measure('perception', lambda:a.accept_perception(sample))
            if i % 2 == 0:
                f = json.loads(receipt.json_text)
                need(f['input_indices'] == [i-1,i] and f['profile'] == profile, 'CAUSAL_INPUT')
                need(f['read_revision'] == revision, 'READ_REVISION')
                need(f.get('a1_admission') == admission, 'ADMISSION_REFERENCE')
                if enabled:need(f['retained_semantics']=='ADMITTED_NOT_FULL_REPEAT_PROOF','RETAINED_SEMANTICS')
                need(a.pending_prediction.provenance_json==receipt.json_text,'FROZEN_PROVENANCE')
                if admission:
                    retained=next(t for t in a.arm._retained_many if t.generation==admission['new_key'][1])
                    need(retained.frames is original,'ORIGINAL_TUPLE_IDENTITY')
                need(f['source_intervals'] == [[(i-2)*4800,(i-1)*4800],[(i-1)*4800,i*4800]], 'INTERVALS')
                need(sorted(map(match_core,f['matches'])) == sorted(expected_matches(forecast_stock,values,i+1)), 'MATCH_REFERENCE')
                hs, pairs, ticket_keys = [], {}, {}
                for m,h in zip(f['matches'],f['hypotheses'],strict=True):
                    k=key(m); eligible=m['factors']==[1.0] and m['offset']<2
                    need(h['eligible']==eligible, 'ELIGIBILITY')
                    if not eligible: continue
                    v=expected.get(k)
                    need((None if h['ec'] is None else (h['ec'],h['ep']))==v, 'PRETARGET_CELLS')
                    need(h['delta']==(None if v is None else v[0]-v[1]), 'DELTA')
                    pairs[k]=v; ticket_keys[h['ticket']]=k
                    original=m['ordinals'][m['offset']+2]
                    ticket=ENTRY.unpack_from(a.bank,208+16*h['ticket'])
                    need(ticket[:3]==(k[1],k[0],k[2]), 'FROZEN_TICKET')
                    need(a._frozen[h['ticket']].ordinal==original and a._frozen[h['ticket']].values==values[original-1], 'FROZEN_ORIGINAL')
                    hs.append(dict(key=list(k), ordinals=m['ordinals'], offset=m['offset'],original=original,
                        before=v, prior_feedback=list(history.get(k,[])), promotion_lineage=list(lineage.get(k,[]))))
                need(sorted(ticket_keys)==list(range(len(hs))) and HEAD.unpack_from(a.bank,192)[2]==len(hs), 'TICKETS')
                chosen=select(pairs)
                actual=None if f['choice']==0 else ticket_keys[f['choice']-1]
                need(chosen==actual, 'SELECTION_REFERENCE')
                need((chosen is not None)==(f['decision']=='SELECTED_BY_ERROR'), 'SELECTION_REASON')
                selected=next((h for h in hs if tuple(h['key'])==chosen),None)
                pending=dict(target=i+1, hypotheses=hs, selected=selected, reason=f['decision'],
                    no_choice_reason='SELECTED' if chosen else 'NO_ELIGIBLE' if not hs else
                    'COLD' if all(h['before'] is None for h in hs) else
                    'TIE' if sum(v is not None and v[0]<v[1] for v in pairs.values())>1 and any(v is not None and v[0]<v[1] for v in pairs.values()) else 'NO_STRICT_ADVANTAGE')
                forecasts.append(f)
                meter.receipt=max(meter.receipt,len(receipt.json_text.encode()))
                need(meter.receipt<=16384 and 2*meter.receipt<=32768, 'RECEIPT_LIMIT')
                slots=1+int(a.pending_prediction.context_values is not None)
                slots_peak=max(slots_peak,slots);need(slots<=2,'OUTPUT_LIMIT')
                if i%4==0:
                    incoming=values[i-4:i]
                    traces=[(0,t) for t in forecast_stock['retained']]+([] if forecast_stock['candidate'] is None else [(1,forecast_stock['candidate'])])
                    full=next(((role,t) for role,t in traces if t['values']==incoming),None)
                    if full:
                        role,t=full
                        confirmations.append(dict(at=i,kind='FULL_RETAINED' if role==0 else 'FULL_CANDIDATE',
                            ordinals=t['ordinals'],observed=list(range(i-3,i+1)),old_key=[role,t['generation']]))
                for ordinal in (i-1,i):
                    ref.feed(ordinal,values[ordinal-1])
                after=ref.snapshot()
                old=forecast_stock['candidate']
                promoted=next((t for t in after['retained'] if old and t['ordinals']==old['ordinals'] and
                    not any(x['generation']==t['generation'] for x in forecast_stock['retained'])),None)
                if promoted:
                    rekey((1,old['generation']),(0,promoted['generation']),i,'FULL')
                revision+=2+int(i%4==0)
                live=keyset(ref)
                expected={k:v for k,v in expected.items() if k[:2] in live}
                history={k:v for k,v in history.items() if k[:2] in live}
                lineage={k:v for k,v in lineage.items() if k[:2] in live}
                need(cellmap(a)==expected,'PRUNE_PROMOTION_REFERENCE')
            need(snapshot(a.arm)==ref.snapshot(),'MEMORY_REFERENCE')
            need(len(a.bank)==416,'BANK_LIMIT')
            events.append(dict(index=i,before=compact(before),before_cells=before_cells,forecast_stock=compact(forecast_stock),partial_admission=admission,after=compact(ref.snapshot())))
        need(pending is not None and pending['target']==len(values)+1,'CENSORING')
        meter.measure('finish',a.finish_story)
        need(a.closed and not any(a.bank) and not any(a._frozen) and not a.arm._candidate and
             not a.arm._retained_many and not a.arm._forming,'CLEANUP')
        resources=meter.snapshot();resources.pop('calls')
        resources['output_slots_peak']=slots_peak
        return dict(rows=rows,events=events,forecasts=forecasts,partial_admissions=admissions,full_confirmations=confirmations,resources=resources,
            frames=len(values),reference_advances=len(values),reference_equal=True,cleanup=True,censored_target=len(values)+1)
    except RuntimeError as exc:
        if fault and str(exc).startswith('INJECTED_A1:'):
            need(a.closed and not any(a.bank) and not any(a._frozen) and a.pending_prediction is None
                and not a.arm._retained_many and a.arm._candidate is None and not a.arm._forming,'FAULT_NOT_CLOSED_EMPTY')
            raise RuntimeError(str(exc)+':CLOSED_EMPTY') from exc
        raise
    finally:
        if not a.closed:a._terminate()

