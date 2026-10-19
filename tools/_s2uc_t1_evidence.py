"""Generic read-only frozen-key evidence audit; derived from sealed raster audit."""
import math

from tools._s2uc_paired_error_ema import mae48
from tools._s2uc_ema_stock_observer import digest

ARMS = ('U', 'M', 'E', 'K', 'P')



def match_core(m):
    return (key(m)[0],m['generation'],tuple(m['ordinals']),m['offset'],tuple(m['factors']))


def expected_matches(stock,vectors,t):
    matches=[]
    for role,items in ((0,stock['retained']),(1,[] if stock['candidate'] is None else [stock['candidate']])):
        for item in items:
            ords=item['ordinals']
            if len(ords)!=4 or any(not 1<=o<t-1 for o in ords):raise ValueError('STOCK_ORDINALS')
            for off in range(3):
                factors=[]
                for e in (-1,0,1):
                    if all(math.ldexp(x,e)==y for j in range(2)
                           for x,y in zip(vectors[ords[off+j]-1],vectors[t-3+j])):factors.append(math.ldexp(1.,e))
                if factors:matches.append((role,item['generation'],tuple(ords),off,tuple(factors)))
    return matches


def key(r):
    role = r['role']
    return ({'retained':0, 'candidate':1}.get(role, role), r['generation'], r['offset'])


def cellmap(rows):
    out = {}
    for r in rows:
        k = key(r)
        if k in out or r['quality'] != 0: raise ValueError('CELL_KEY')
        if any(not math.isfinite(r[n]) or r[n] < 0 for n in ('ec','ep')): raise ValueError('CELL_VALUE')
        out[k] = (r['ec'], r['ep'])
    return out


def select(pairs):
    scored = [(v[0]-v[1],k) for k,v in pairs.items() if v is not None and v[0] < v[1]]
    if not scored: return None
    low = min(d for d,k in scored)
    wins = [k for d,k in scored if d == low]
    return wins[0] if len(wins) == 1 else None


def metrics(results, masks):
    rows = {a:{r['target']:r for r in results[a]['rows']} for a in ARMS}
    values = {}
    for name, targets in masks.items():
        values[name] = {}
        for a in ARMS:
            missing = [t for t in targets if t not in rows[a]]
            s = None if missing else sum(rows[a][t]['selected_mae'] for t in targets)
            values[name][a] = dict(count=len(targets)-len(missing), missing=missing, error_sum=s,
                                  mae=None if s is None else s/len(targets) if targets else None)
    comparisons = [dict(target=t, errors={a:rows[a][t]['selected_mae'] for a in ARMS},
                        U_minus={a:rows['U'][t]['selected_mae']-rows[a][t]['selected_mae'] for a in ARMS[1:]})
                   for t in masks['G'] if all(t in rows[a] for a in ARMS)]
    net = {}
    for mask in ('G',):
        v = values[mask]
        net[mask] = 'NOT_EVALUABLE' if any(v[a]['missing'] for a in ARMS) else (
            'BELEGT' if all(v['U']['mae'] < v[a]['mae'] for a in ARMS[1:]) else 'NICHT_NACHGEWIESEN')
    return values, comparisons, net


def assess(results, source, spec):
    values = {}; comparisons = []; net = {'H':'NOT_EVALUABLE','G':'NOT_EVALUABLE'}
    errors = []; decisions = {}; updates = {}; coverage = {a:{} for a in ARMS}
    def need(ok, code):
        if not ok: raise ValueError(code)
    try:
        values, comparisons, net = metrics(results, spec['masks'])
        need(len(source) == spec['frames'] and all(len(v) == 48 for v in source), 'SOURCE_SHAPE')
        vectors = [tuple(v) for v in source]  # Observer only; existing saved source, no generation.
        for a in ARMS:
            r = results[a]
            need(len(r['rows']) == len({x['target'] for x in r['rows']}), 'DUPLICATE_TARGET')
            need(all(math.isfinite(x['selected_mae']) and 0 <= x['selected_mae'] <= 1 for x in r['rows']), 'ERROR_RANGE')
            need(len(r['admissions']) == spec['frames'] and all(x['status']=='COMPLETE' for x in r['admissions']), 'ALL_ADMISSIONS')
            need(len(r['forecasts']) == spec['frames']//2 and len(r['updates'] if a=='U' else r['error_updates']) == len(spec['masks']['G']), 'EVIDENCE_COUNTS')
            need(len(r['states'] if a=='U' else r['state_hashes']) == spec['frames'], 'STATE_COUNTS')
            need([x['target'] for x in r['rows']] == spec['masks']['G'], 'TARGETS:'+a)
            need(r['frames'] == spec['frames'] and r['censored_target'] == spec['frames']+1 and r['slots_released'] and r['states_identical'], 'CLOSURE:'+a)
        need(len({digest(results[a]['states'] if a=='U' else results[a]['state_hashes']) for a in ARMS}) == 1, 'MEMORY_STATES')
        u = results['U']; forecasts = {f['input_indices'][-1]+1:f for f in u['forecasts']}
        updates = {x['target']:x for x in u['updates']}
        admissions = {x['index']:x for x in u['admissions']}
        base_events = {x['frame']:x for x in results['M']['admissions']}
        base_forecasts = {x['target']:x['receipt'] for x in results['M']['forecasts']}
        need(sorted(admissions) == list(range(1,spec['frames']+1)) and sorted(base_events) == list(range(1,spec['frames']+1)), 'ADMISSION_SET')
        need(sorted(forecasts) == list(range(3,spec['frames']+2,2)) and sorted(updates) == spec['masks']['G'], 'EVIDENCE_SET')
        rowmap = {x['target']:x for x in u['rows']}
        history = {}; current = {}
        for index in range(1,spec['frames']+1):
            if index in updates:
                up = updates[index]; f = forecasts[index]
                need(up['status']=='COMPLETE' and cellmap(up['before'])==current, 'FEEDBACK_CHAIN')
                need(f['input_indices']==[index-2,index-1] and f['read_revision']==index-3+(index-3)//4,
                     'CAUSAL_FORECAST_BOUNDARY')
                need(f['source_intervals']==[[(index-3)*4800,(index-2)*4800],[(index-2)*4800,(index-1)*4800]],
                     'FORECAST_TIME')
                need(f['profile']==digest(source), 'SOURCE_PROFILE')
                order=lambda m:(m['role'],m['generation'],m['offset'])
                need(sorted(f['matches'],key=order)==sorted(base_forecasts[index]['matches'],key=order),
                     'COMPLETE_PRESTATE_MATCHES')
                stock=base_events[index-2]['before']
                need(sorted(map(match_core,f['matches']))==sorted(expected_matches(stock,vectors,index)), 'COMPLETE_MATCH_ENUMERATION')
                expected = dict(current); candidates = {}; normalized = []; ticket_keys = {}
                need(len(f['matches'])==len(f['hypotheses']), 'MATCH_METADATA')
                for m,h in zip(f['matches'],f['hypotheses']):
                    need(h['eligible']==(m['factors']==[1.0] and m['offset'] in (0,1)), 'ELIGIBILITY')
                    if not h['eligible']: continue
                    k = key(m); ords = m['ordinals']; off=m['offset']
                    need(k not in candidates and m['factors']==[1.0] and off in (0,1), 'HYPOTHESIS_KEY')
                    store=stock['retained'] if k[0]==0 else ([] if stock['candidate'] is None else [stock['candidate']])
                    origins=[x for x in store if x['generation']==k[1]]
                    need(len(origins)==1 and origins[0]['ordinals']==ords, 'ORIGINAL_KEY_IDENTITY')
                    need(len(ords)==4 and all(1<=o<index-1 for o in ords), 'ORIGINAL_PRECEDES_HINT')
                    need(all(vectors[ords[off+j]-1]==vectors[index-3+j] for j in range(2)), 'ORIGINAL_HINT')
                    label = digest(vectors[ords[off+2]-1])
                    pair = None if h['ec'] is None else (h['ec'],h['ep'])
                    need(pair==current.get(k), 'FROZEN_ERROR_PAIR')
                    need(h['delta'] == (None if pair is None else pair[0]-pair[1]), 'FROZEN_DELTA')
                    need(h['ticket'] not in ticket_keys, 'TICKET_DUPLICATE')
                    ticket_keys[h['ticket']]=k; candidates[k]=pair
                    original=ords[off+2]
                    need(sum(key(x)==k for x in up['hypotheses'])==1,'FROZEN_HYPOTHESIS_UNIQUE')
                    raw = next(x for x in up['hypotheses'] if key(x)==k)
                    need(raw['original_ordinal']==original and raw['live'], 'FROZEN_ORIGINAL')
                    ec=mae48(vectors[original-1],vectors[index-1]); ep=mae48(vectors[index-2],vectors[index-1])
                    need((ec,ep)==(raw['ec'],raw['ep']), 'FROZEN_RAW_ERRORS')
                    expected[k]=(ec,ep) if pair is None else (.5*pair[0]+.5*ec,.5*pair[1]+.5*ep)
                    prior=list(history.get(k,[]))
                    phase_start = next(p['start'] for p in spec['phases'] if p['start']<=index<=p['end'])
                    normalized.append(dict(key=list(k),label=label,original_ordinals=ords,original_successor=original,
                        before=pair,after=expected[k],raw_errors=[ec,ep],ticket=h['ticket'],
                        prior_feedback=prior,phase_feedback=[t for t in prior if phase_start<=t<index]))
                need(len(candidates)==len(up['hypotheses']), 'MISSING_ALTERNATIVE')
                need(sorted(ticket_keys)==list(range(len(ticket_keys))), 'TICKET_SET')
                selected=None if f['choice']==0 else ticket_keys[f['choice']-1]
                need(selected==select(candidates), 'SELECTION_RULE')
                chosen=next((h for h in normalized if tuple(h['key'])==selected),None)
                need(rowmap[index]['choice']==f['choice'] and rowmap[index]['decision']==f['decision'], 'FROZEN_CHOICE')
                actual_error=mae48(vectors[index-2] if chosen is None else vectors[chosen['original_successor']-1], vectors[index-1])
                need(actual_error==rowmap[index]['selected_mae'], 'SELECTED_ERROR')
                need(cellmap(up['after'])==expected, 'ALL_ERROR_UPDATES')
                labels=[h['label'] for h in normalized]
                # Different numeric output alone cannot replace provenance and warm selection.
                distinct = chosen is not None  # Provenance is identity, not numerical inequality to P.
                decisions[index]=dict(target=index,selected_key=None if selected is None else list(selected),
                    selected_label='P' if chosen is None else chosen['label'], reason=f['decision'],
                    strict_warm_winner=selected is not None and candidates[selected] is not None,
                    original_frozen_verified=chosen is not None and distinct,
                    prior_feedback=[] if chosen is None else chosen['prior_feedback'],
                    phase_feedback=[] if chosen is None else chosen['phase_feedback'],
                    available_labels=labels,hypotheses=normalized,origin_status=f['status'])
                coverage['U'][index]=dict(eligible=len(normalized),warm=sum(v is not None for v in candidates.values()),origin=f['status'])
                for k in candidates: history.setdefault(k,[]).append(index)
                current=expected
            ad=admissions[index]
            need(ad['status']=='COMPLETE' and cellmap(ad['before'])==current, 'ADMISSION_BEFORE')
            if index%2==0:
                for frame in (index-1,index):
                    event=base_events[frame]; oldstock=event['before']; newstock=event['after']
                    new=[t for t in newstock['retained'] if t['generation'] not in [x['generation'] for x in oldstock['retained']]]
                    promoted=oldstock['candidate'] if new and newstock['candidate'] is None else None
                    if promoted:
                        need(len(new)==1 and new[0]['ordinals']==promoted['ordinals'], 'PROMOTION_ORIGINAL')
                        for k in list(current):
                            if k[:2]==(1,promoted['generation']):
                                dest=(0,new[0]['generation'],k[2]); current[dest]=current.pop(k)
                                history[dest]=history.pop(k,[])
                    live={(0,t['generation']) for t in newstock['retained']}
                    if newstock['candidate']: live.add((1,newstock['candidate']['generation']))
                    current={k:v for k,v in current.items() if k[:2] in live}
                    history={k:v for k,v in history.items() if k[:2] in live}
            need(cellmap(ad['after'])==current, 'ADMISSION_AFTER')
        for a in ARMS[1:]:
            rows={r['target']:r for r in results[a]['rows']}
            need([f['target'] for f in results[a]['forecasts']]==list(range(3,spec['frames']+2,2)), 'BASE_FORECAST_SET')
            for f in results[a]['forecasts']:
                coverage[a][f['target']]=dict(eligible=int(f['context_available']),origin=f['receipt']['status'])
                t=f['target']
                if t not in rows: continue  # Final forecast is censored, not scored.
                receipt=f['receipt']; row=rows[t]
                need(receipt['input_indices']==[t-2,t-1] and receipt['profile']==digest(source), 'BASE_CAUSAL_SOURCE')
                need(receipt['read_revision']==t-3+(t-3)//4, 'BASE_READ_REVISION')
                need(row['choice']==f['choice'], 'BASE_FROZEN_CHOICE')
                persistence=mae48(vectors[t-2],vectors[t-1])
                need(row['persistence_mae']==persistence, 'BASE_PERSISTENCE_ERROR')
                selected=vectors[t-2]
                if f['context_available']:
                    matches=receipt['matches']
                    need(len(matches)==1 and matches[0]['offset'] in (0,1) and matches[0]['factors']==[1.0], 'BASE_CONTEXT_IDENTITY')
                    m=matches[0]; ords=m['ordinals']; off=m['offset']
                    need(all(1<=o<t-1 for o in ords), 'BASE_ORIGINAL_TIME')
                    context=vectors[ords[off+2]-1]
                    need(row['context_mae']==mae48(context,vectors[t-1]), 'BASE_CONTEXT_ERROR')
                    if f['choice']=='CONTEXT':selected=context
                else: need(f['choice']=='PERSISTENCE' and row['context_mae'] is None, 'BASE_NO_CONTEXT')
                need(row['selected_mae']==mae48(selected,vectors[t-1]), 'BASE_SELECTED_ERROR')
    except (ValueError, KeyError, IndexError, StopIteration, TypeError, OverflowError) as exc:
        errors.append(type(exc).__name__+':'+str(exc))
    if errors: net={'H':'NOT_EVALUABLE','G':'NOT_EVALUABLE'}
    for name,targets in spec['masks'].items():
        if name not in values: continue
        for a in ARMS:
            values[name][a]['context_coverage']=[dict(target=t,**coverage[a].get(t,{'missing_evidence':True})) for t in targets]
    return dict(technical_errors=errors, metrics=values, comparisons=comparisons,
        decisions=list(decisions.values()), independent_evaluation='NICHT_GEPRUEFT')
