"""U/K1 replay and observer. Source/modal annotations never enter the adapter."""
import json
from fractions import Fraction
from tools._s2uc_k1 import create, POLICY as K1
from tools._s2uc_k1_reference import Reference
from tools._s2uc_k1_probe import snapshot, error, cellmap, keyset
from tools._s2uc_multi_observer import Meter, POLICY, PerceptionSample, HEAD, ENTRY
from tools._s2uc_t1_evidence_v2 import expected_matches, match_core, key, select


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def compact(stock):
    def item(t):
        return None if t is None else {k:v for k,v in t.items() if k != 'values'}
    return stock | dict(candidate=item(stock['candidate']), retained=[item(t) for t in stock['retained']])


def replay(values, profile, enabled, check):
    values = [tuple(v) for v in values]
    a = create(profile, 'comparison', 'stream', candidate_policy=K1 if enabled else 'disabled', multi_policy=POLICY)
    ref = Reference(enabled)
    meter = Meter(a)
    expected, history, lineage = {}, {}, {}
    rows, events, forecasts = [], [], []
    pending = None
    slots_peak = 0
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
                        expected[k] = (ec, ep) if old is None else (.5*old[0]+.5*ec, .5*old[1]+.5*ep)
                        history.setdefault(k, []).append(i)
                    updates.append(dict(key=list(k), live=live, ec=ec, ep=ep))
                chosen = pending['selected']
                predicted = values[i-2] if chosen is None else values[chosen['original']-1]
                need(tuple(a.selected_values) == predicted, 'FROZEN_OUTPUT')
                measured = error(a.selected_values, vector)
                meter.measure('feedback', lambda:a.consume_feedback(sample))
                need(cellmap(a) == expected, 'FEEDBACK_REFERENCE')
                rows.append(pending | dict(error=measured, updates=updates))
                pending = None
            before = ref.snapshot()
            receipt = meter.measure('perception', lambda:a.accept_perception(sample))
            if i % 2 == 0:
                f = json.loads(receipt.json_text)
                need(f['input_indices'] == [i-1,i] and f['profile'] == profile, 'CAUSAL_INPUT')
                need(f['read_revision'] == i-2+(i-2)//4, 'READ_REVISION')
                need(f['source_intervals'] == [[(i-2)*4800,(i-1)*4800],[(i-1)*4800,i*4800]], 'INTERVALS')
                need(sorted(map(match_core,f['matches'])) == sorted(expected_matches(before,values,i+1)), 'MATCH_REFERENCE')
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
                for ordinal in (i-1,i):
                    ref.feed(ordinal,values[ordinal-1])
                after=ref.snapshot()
                old=before['candidate']
                promoted=next((t for t in after['retained'] if old and t['ordinals']==old['ordinals'] and
                    not any(x['generation']==t['generation'] for x in before['retained'])),None)
                if promoted:
                    for k in list(expected):
                        if k[:2]==(1,old['generation']):
                            dest=(0,promoted['generation'],k[2]);expected[dest]=expected.pop(k)
                            history[dest]=history.pop(k,[])
                            lineage[dest]=lineage.pop(k,[])+[dict(at=i,old_key=list(k),new_key=list(dest))]
                live=keyset(ref)
                expected={k:v for k,v in expected.items() if k[:2] in live}
                history={k:v for k,v in history.items() if k[:2] in live}
                lineage={k:v for k,v in lineage.items() if k[:2] in live}
                need(cellmap(a)==expected,'PRUNE_PROMOTION_REFERENCE')
            need(snapshot(a.arm)==ref.snapshot(),'MEMORY_REFERENCE')
            need(len(a.bank)==416,'BANK_LIMIT')
            events.append(dict(index=i,before=compact(before),after=compact(ref.snapshot())))
        need(pending is not None and pending['target']==len(values)+1,'CENSORING')
        meter.measure('finish',a.finish_story)
        need(a.closed and not any(a.bank) and not any(a._frozen) and not a.arm._candidate and
             not a.arm._retained_many and not a.arm._forming,'CLEANUP')
        resources=meter.snapshot();resources.pop('calls')
        resources['output_slots_peak']=slots_peak
        return dict(rows=rows,events=events,forecasts=forecasts,resources=resources,
            frames=len(values),reference_advances=len(values),reference_equal=True,cleanup=True,censored_target=len(values)+1)
    finally:
        if not a.closed:a._terminate()


def identity(h):
    return tuple(h['ordinals'])+(h['offset'],)


def assess_case(arms,bundle,spec):
    values=bundle['values']; modal=bundle['modal']; targets=spec['masks']['G']
    out=[]; lifecycle=[]
    for name,a in arms.items():
        limits=dict(additional_python_peak=16384,original_frames_upper_bound=18,
            combined_upper_bound=20,output_slots_peak=2,packed=416,receipt_bytes_peak=16384,utf8_upper=32768)
        need(all(0<=a['resources'][k]<=v for k,v in limits.items()) and a['resources']['packed']==416,'RESOURCE_LIMIT')
        need([x['target'] for x in a['rows']]==targets,'TARGET_SET')
        need(a['frames']==spec['frames'] and a['reference_advances']==spec['frames'] and a['reference_equal'] and a['cleanup'],'ARM_COMPLETE')
        for ev in a['events']:
            def items(s):return s['retained']+([] if s['candidate'] is None else [s['candidate']])
            before={tuple(t['ordinals']) for t in items(ev['before'])}
            after={tuple(t['ordinals']) for t in items(ev['after'])}
            lifecycle.append(dict(arm=name,index=ev['index'],gained=sorted(after-before),lost=sorted(before-after),
                discarded_incoming=list(range(ev['index']-3,ev['index']+1)) if ev['index']%4==0 and
                tuple(range(ev['index']-3,ev['index']+1)) not in after else []))
    for u,k in zip(arms['U']['rows'],arms['K1']['rows'],strict=True):
        t=u['target']; normalized={}
        for name,row in (('U',u),('K1',k)):
            hs=[]
            for h in row['hypotheses']:
                hs.append(h|dict(actual_match=values[h['original']-1]==values[t-1],
                    modal_match=modal[t-1] is not None and values[h['original']-1]==modal[t-1],warm=h['before'] is not None))
            selected=next((h for h in hs if row['selected'] and h['key']==row['selected']['key']),None)
            normalized[name]=row|dict(hypotheses=hs,selected=selected,modal_warm=any(h['modal_match'] and h['warm'] for h in hs))
        sets={n:{identity(h):h for h in v['hypotheses']} for n,v in normalized.items()}
        gained=[sets['K1'][x] for x in sorted(sets['K1'].keys()-sets['U'].keys())]
        lost=[sets['U'][x] for x in sorted(sets['U'].keys()-sets['K1'].keys())]
        warm={n:{x for x,h in v.items() if h['warm']} for n,v in sets.items()}
        out.append(dict(target=t,arms=normalized,gained=gained,lost=lost,
            gained_warm=[sets['K1'][x] for x in sorted(warm['K1']-warm['U'])],
            lost_warm=[sets['U'][x] for x in sorted(warm['U']-warm['K1'])],delta=k['error']-u['error'],
            decision_differs=(None if u['selected'] is None else identity(u['selected'])) !=
                             (None if k['selected'] is None else identity(k['selected']))))
    transitions={}
    for arm in ('U','K1'):
        ts=[];by={x['target']:x['arms'][arm] for x in out}
        for phase in spec['phases'][1:]:
            checks=[]
            for t in phase['targets']:
                d=by[t];h=d['selected']
                checks.append(bool(h and modal[t-1] is not None and values[h['original']-1]==modal[t-1]
                    and d['reason']=='SELECTED_BY_ERROR' and h['before'] is not None and
                    any(phase['start']<=f<t for f in h['prior_feedback'])))
            deadline=min(3,len(checks))
            ts.append(phase|dict(passed=bool(checks and all(checks[deadline-1:])),checks=checks,
                latency=next((i+1 for i in range(len(checks)) if all(checks[i:])),None)))
        transitions[arm]=ts
    metrics={mask:{arm:dict(count=len(tt),error_sum_exact=str(sum((Fraction(next(r['error'] for r in arms[arm]['rows'] if r['target']==t)) for t in tt),Fraction())))
        for arm in ('U','K1')} for mask,tt in spec['masks'].items()}
    return dict(id=spec['id'],group=spec['group'],replicate=spec.get('replicate'),rows=out,metrics=metrics,
        transitions=transitions,lifecycle=lifecycle,resources={a:r['resources'] for a,r in arms.items()},technical_errors=[])


def aggregate(reports,specs):
    need([r['id'] for r in reports]==[s['id'] for s in specs] and len(reports)==24,'ALL_24_CASES')
    for r,s in zip(reports,specs,strict=True):
        need(not r['technical_errors'] and [row['target'] for row in r['rows']]==s['masks']['G'],'AGGREGATE_TARGETS')
        for mask,targets in s['masks'].items():
            for arm in ('U','K1'):
                m=r['metrics'][mask][arm]
                exact=sum((Fraction(row['arms'][arm]['error']) for row in r['rows'] if row['target'] in targets),Fraction())
                need(m['count']==len(targets) and Fraction(m['error_sum_exact'])==exact,'AGGREGATE_METRICS')
    t1=[r for r in reports if r['group']=='T1']; fs=[r for r in reports if r['group']=='F']
    need(len(t1)==16 and len(fs)==8 and sum(len(r['rows']) for r in t1)==624 and sum(len(r['rows']) for r in fs)==248,'DENOMINATORS')
    def mean(r,a,mask='G'):
        m=r['metrics'][mask][a];return Fraction(m['error_sum_exact'])/m['count']
    def group_mean(rs,a):return sum((mean(r,a) for r in rs),Fraction())/len(rs)
    means={g:{a:str(group_mean(rs,a)) for a in ('U','K1')} for g,rs in (('T1',t1),('F',fs),('ALL',reports))}
    mechanism={a:sum(row['arms'][a]['modal_warm'] for r in t1 for row in r['rows']) for a in ('U','K1')}
    diagnosis={a:sum(row['arms'][a]['modal_warm'] for r,s in zip(reports,specs) if s['group']=='T1'
        for row in r['rows'] if row['target'] in s['diagnosis_targets']) for a in ('U','K1')}
    differences=[dict(id=r['id'],delta_exact=str(mean(r,'K1')-mean(r,'U')),delta=float(mean(r,'K1')-mean(r,'U'))) for r in reports]
    late=[r for r in t1 if r['metrics']['G_w']['U']['count']]
    need(len(late)==4,'LATE_DENOMINATOR')
    late_means={a:sum((mean(r,a,'G_w') for r in late),Fraction())/4 for a in ('U','K1')}
    benefit=Fraction(means['T1']['K1'])<Fraction(means['T1']['U']) and Fraction(means['F']['K1'])<=Fraction(means['F']['U']) and Fraction(means['ALL']['K1'])<Fraction(means['ALL']['U'])
    safe=all(Fraction(d['delta_exact'])<=Fraction(1,32) for d in differences) and late_means['K1']<=late_means['U']
    adaptation={}
    for a in ('U','K1'):
        switches=[(r['replicate'],s) for r in t1 for s in r['transitions'][a]]
        need(len(switches)==52 and sum(s['negative_control'] for _,s in switches)==20,'TRANSITIONS')
        groups={str(g):dict(successes=sum(s['passed'] for rg,s in switches if rg==g),denominator=sum(rg==g for rg,s in switches)) for g in (1,2,3,4)}
        successes=sum(s['passed'] for _,s in switches)
        adaptation[a]=dict(successes=successes,denominator=52,negative_controls=20,groups=groups,
            verdict='BELEGT' if successes>=26 and all(v['denominator']==13 and v['successes']>=4 for v in groups.values()) else 'NICHT_NACHGEWIESEN')
    allrows=[row for r in reports for row in r['rows']]
    counts={name:dict(hypotheses=sum(len(x[name]) for x in allrows),targets=sum(bool(x[name]) for x in allrows),
        actual=sum(h['actual_match'] for x in allrows for h in x[name]),modal=sum(h['modal_match'] for x in allrows for h in x[name])) for name in ('gained','lost','gained_warm','lost_warm')}
    deltas=[Fraction(x['delta']) for x in allrows]
    return dict(technical_errors=[],verdicts=dict(Technik='AUSWERTBAR',Mechanismus='BELEGT' if mechanism['K1']>mechanism['U'] else 'NICHT_NACHGEWIESEN',
        Gesamtnutzen='BELEGT' if benefit else 'NICHT_NACHGEWIESEN',Schaden='GRENZE_EINGEHALTEN' if safe else 'SCHADENSGRENZE_VERLETZT'),
        case_means_exact=means,case_differences=differences,mechanism=mechanism|dict(denominator=624),diagnosis=diagnosis|dict(denominator=324),
        G_w_exact={a:str(v) for a,v in late_means.items()},adaptation=adaptation,experience=counts,
        prediction=dict(improved=sum(d<0 for d in deltas),worse=sum(d>0 for d in deltas),equal=sum(d==0 for d in deltas),
            harm_sum_exact=str(sum((d for d in deltas if d>0),Fraction())),gain_sum_exact=str(-sum((d for d in deltas if d<0),Fraction())),
            max_harm=float(max(deltas)),worst_case_delta=max(d['delta'] for d in differences)),
        known_development_only=True,transfer_claim=False)
