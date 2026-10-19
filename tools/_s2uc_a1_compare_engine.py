"""U/A1 replay and observer. Source/modal annotations never enter the adapter."""
import json
from fractions import Fraction
from tools._s2uc_a1 import create, POLICY as A1
from tools._s2uc_a1_reference import Reference
from tools._s2uc_k1_reference import Reference as UReference
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


def replay(values, profile, enabled, check, fault=None):
    values = [tuple(v) for v in values]
    a = create(profile, 'comparison', 'stream', admission_policy=A1 if enabled else 'disabled', multi_policy=POLICY)
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
                        expected[k] = (ec, ep) if old is None else (.5*old[0]+.5*ec, .5*old[1]+.5*ep)
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


def identity(h):
    return tuple(h['ordinals'])+(h['offset'],)


def stage_evidence(a, values):
    """Reconstruct separate stages; a retained role alone never proves a full repeat."""
    partials=[]; full=[]; losses=[]; revision=0
    for ev in a['events']:
        i=ev['index']; admission=ev['partial_admission']
        if admission:
            need(i%2==0 and admission['full_repeat'] is False,'PARTIAL_NOT_FULL')
            partials.append(dict(at=i,**admission));revision+=1
        if i%2==0:
            f=a['forecasts'][i//2-1]
            need(f.get('a1_admission')==admission and f['read_revision']==revision,'STAGE_RECEIPT')
            revision+=2+int(i%4==0)
        if i%4==0:
            s=ev['forecast_stock']
            traces=[(0,t) for t in s['retained']]+([] if s['candidate'] is None else [(1,s['candidate'])])
            found=next(((role,t) for role,t in traces if [values[o-1] for o in t['ordinals']]==values[i-4:i]),None)
            if found:
                role,t=found
                full.append(dict(at=i,kind='FULL_RETAINED' if role==0 else 'FULL_CANDIDATE',
                    ordinals=t['ordinals'],observed=list(range(i-3,i+1)),old_key=[role,t['generation']]))
        def traces(s):return s['retained']+([] if s['candidate'] is None else [s['candidate']])
        surviving={tuple(t['ordinals']) for t in traces(ev['after'])}
        for role,ts in ((0,ev['before']['retained']),(1,[] if ev['before']['candidate'] is None else [ev['before']['candidate']])):
            for t in ts:
                if tuple(t['ordinals']) not in surviving:
                    for off in (0,1):
                        k=[role,t['generation'],off]
                        cell=next((c for c in ev['before_cells'] if c['key']==k),None)
                        losses.append(dict(at=i,ordinals=t['ordinals'],offset=off,key=k,
                            cause='PARTIAL_VICTIM' if admission and admission['victim'] and admission['victim']['ordinals']==t['ordinals'] else 'ORDINARY_CLOSE',
                            prior_feedback=[] if cell is None else cell['prior_feedback'],cell=None if cell is None else cell['values']))
    need(partials==a['partial_admissions'],'PARTIAL_EVENT_SET')
    need(full==a['full_confirmations'],'FULL_EVENT_SET')
    accepted=[];rejected=[];warm=[]
    for row in a['rows']:
        t=row['target']
        need(len(row['updates'])==len(row['hypotheses']),'FEEDBACK_COVERAGE')
        for h,u in zip(row['hypotheses'],row['updates'],strict=True):
            need(identity(h)==identity(u) and h['key']==u['key'],'FEEDBACK_IDENTITY')
            prior=[x['target'] for x in accepted if identity(x)==identity(h)]
            need(h['prior_feedback']==prior,'FEEDBACK_HISTORY')
            need((h['before'] is not None)==bool(prior),'WARM_REQUIRES_FEEDBACK')
            if prior:
                warm.append(dict(target=t,ordinals=h['ordinals'],offset=h['offset'],prior_feedback=prior,
                    after_partial=any(p['at']<t-1 and p['ordinals']==h['ordinals'] for p in partials)))
            entry=dict(target=t,**u)
            (accepted if u['live'] else rejected).append(entry)
    chains=[]
    for p in partials:
        for off in (0,1):
            line=tuple(p['ordinals'])+(off,)
            chains.append(dict(admitted_at=p['at'],ordinals=p['ordinals'],offset=off,
                processed_feedback=[u['target'] for u in accepted if identity(u)==line],
                subsequent_warm_retrievals=[w['target'] for w in warm if identity(w)==line and w['target']-1>p['at']],
                lost_at=[l['at'] for l in losses if identity(l)==line]))
    return dict(partial_admissions=len(partials),full_confirmations=len(full),
        full_candidate_confirmations=sum(f['kind']=='FULL_CANDIDATE' for f in full),
        full_retained_confirmations=sum(f['kind']=='FULL_RETAINED' for f in full),
        processed_feedback=len(accepted),discarded_feedback=len(rejected),
        warm_retrievals=len(warm),subsequent_warm_after_partial=sum(w['after_partial'] for w in warm),
        partial_victims=sum(p['victim'] is not None for p in partials),
        warm_lost_lines=sum(bool(l['prior_feedback']) for l in losses),
        losses=losses,partial_lineage_chains=chains)


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
    for u,k in zip(arms['U']['rows'],arms['A1']['rows'],strict=True):
        t=u['target']; normalized={}
        for name,row in (('U',u),('A1',k)):
            hs=[]
            for h in row['hypotheses']:
                hs.append(h|dict(actual_match=values[h['original']-1]==values[t-1],
                    modal_match=modal[t-1] is not None and values[h['original']-1]==modal[t-1],warm=h['before'] is not None and bool(h['prior_feedback']) and all(f<t for f in h['prior_feedback'])))
            selected=next((h for h in hs if row['selected'] and h['key']==row['selected']['key']),None)
            normalized[name]=row|dict(hypotheses=hs,selected=selected,modal_warm=any(h['modal_match'] and h['warm'] for h in hs))
        sets={n:{identity(h):h for h in v['hypotheses']} for n,v in normalized.items()}
        gained=[sets['A1'][x] for x in sorted(sets['A1'].keys()-sets['U'].keys())]
        lost=[sets['U'][x] for x in sorted(sets['U'].keys()-sets['A1'].keys())]
        warm={n:{x for x,h in v.items() if h['warm']} for n,v in sets.items()}
        out.append(dict(target=t,arms=normalized,gained=gained,lost=lost,
            gained_warm=[sets['A1'][x] for x in sorted(warm['A1']-warm['U'])],
            lost_warm=[sets['U'][x] for x in sorted(warm['U']-warm['A1'])],delta=k['error']-u['error'],
            decision_differs=(None if u['selected'] is None else identity(u['selected'])) !=
                             (None if k['selected'] is None else identity(k['selected']))))
    transitions={}
    for arm in ('U','A1'):
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
        for arm in ('U','A1')} for mask,tt in spec['masks'].items()}
    stages={name:stage_evidence(a,values) for name,a in arms.items()}
    return dict(stages=stages,id=spec['id'],group=spec['group'],replicate=spec.get('replicate'),rows=out,metrics=metrics,
        transitions=transitions,lifecycle=lifecycle,resources={a:r['resources'] for a,r in arms.items()},technical_errors=[])


def aggregate(reports,specs):
    need([r['id'] for r in reports]==[s['id'] for s in specs] and len(reports)==24,'ALL_24_CASES')
    for r,s in zip(reports,specs,strict=True):
        need(not r['technical_errors'] and [row['target'] for row in r['rows']]==s['masks']['G'],'AGGREGATE_TARGETS')
        for mask,targets in s['masks'].items():
            for arm in ('U','A1'):
                m=r['metrics'][mask][arm]
                exact=sum((Fraction(row['arms'][arm]['error']) for row in r['rows'] if row['target'] in targets),Fraction())
                need(m['count']==len(targets) and Fraction(m['error_sum_exact'])==exact,'AGGREGATE_METRICS')
    t1=[r for r in reports if r['group']=='T1']; fs=[r for r in reports if r['group']=='F']
    need(len(t1)==16 and len(fs)==8 and sum(len(r['rows']) for r in t1)==624 and sum(len(r['rows']) for r in fs)==248,'DENOMINATORS')
    def mean(r,a,mask='G'):
        m=r['metrics'][mask][a];return Fraction(m['error_sum_exact'])/m['count']
    def group_mean(rs,a):return sum((mean(r,a) for r in rs),Fraction())/len(rs)
    means={g:{a:str(group_mean(rs,a)) for a in ('U','A1')} for g,rs in (('T1',t1),('F',fs),('ALL',reports))}
    mechanism={a:sum(row['arms'][a]['modal_warm'] for r in t1 for row in r['rows']) for a in ('U','A1')}
    diagnosis={a:sum(row['arms'][a]['modal_warm'] for r,s in zip(reports,specs) if s['group']=='T1'
        for row in r['rows'] if row['target'] in s['diagnosis_targets']) for a in ('U','A1')}
    differences=[dict(id=r['id'],delta_exact=str(mean(r,'A1')-mean(r,'U')),delta=float(mean(r,'A1')-mean(r,'U'))) for r in reports]
    late=[r for r in t1 if r['metrics']['G_w']['U']['count']]
    need(len(late)==4,'LATE_DENOMINATOR')
    late_means={a:sum((mean(r,a,'G_w') for r in late),Fraction())/4 for a in ('U','A1')}
    benefit=Fraction(means['T1']['A1'])<Fraction(means['T1']['U']) and Fraction(means['F']['A1'])<=Fraction(means['F']['U']) and Fraction(means['ALL']['A1'])<Fraction(means['ALL']['U'])
    safe=all(Fraction(d['delta_exact'])<=Fraction(1,32) for d in differences) and late_means['A1']<=late_means['U']
    adaptation={}
    for a in ('U','A1'):
        switches=[(r['replicate'],s) for r in t1 for s in r['transitions'][a]]
        need(len(switches)==52 and sum(s['negative_control'] for _,s in switches)==20,'TRANSITIONS')
        groups={str(g):dict(successes=sum(s['passed'] for rg,s in switches if rg==g),denominator=sum(rg==g for rg,s in switches)) for g in (1,2,3,4)}
        successes=sum(s['passed'] for _,s in switches)
        adaptation[a]=dict(successes=successes,denominator=52,negative_controls=20,groups=groups,
            verdict='BELEGT' if successes>=26 and all(v['denominator']==13 and v['successes']>=4 for v in groups.values()) else 'NICHT_NACHGEWIESEN')
    allrows=[row for r in reports for row in r['rows']]
    counts={name:dict(hypotheses=sum(len(x[name]) for x in allrows),targets=sum(bool(x[name]) for x in allrows),
        actual=sum(h['actual_match'] for x in allrows for h in x[name]),modal=sum(h['modal_match'] for x in allrows for h in x[name])) for name in ('gained','lost','gained_warm','lost_warm')}
    for name,c in counts.items():
        c['original_traces']=len({(r['id'],tuple(h['ordinals'])) for r in reports for row in r['rows'] for h in row[name]})
        c['original_offset_lines']=len({(r['id'],identity(h)) for r in reports for row in r['rows'] for h in row[name]})
    deltas=[Fraction(x['delta']) for x in allrows]
    return dict(technical_errors=[],verdicts=dict(Technik='AUSWERTBAR',Mechanismus='BELEGT' if mechanism['A1']>mechanism['U'] else 'NICHT_NACHGEWIESEN',
        Gesamtnutzen='BELEGT' if benefit else 'NICHT_NACHGEWIESEN',Schaden='GRENZE_EINGEHALTEN' if safe else 'SCHADENSGRENZE_VERLETZT'),
        case_means_exact=means,case_differences=differences,mechanism=mechanism|dict(denominator=624),diagnosis=diagnosis|dict(denominator=324),
        G_w_exact={a:str(v) for a,v in late_means.items()},adaptation=adaptation,experience=counts,
        prediction=dict(improved=sum(d<0 for d in deltas),worse=sum(d>0 for d in deltas),equal=sum(d==0 for d in deltas),
            harm_sum_exact=str(sum((d for d in deltas if d>0),Fraction())),gain_sum_exact=str(-sum((d for d in deltas if d<0),Fraction())),
            max_harm=float(max(deltas)),worst_case_delta=max(d['delta'] for d in differences)),
        stages={arm:{k:sum(r['stages'][arm][k] for r in reports) for k in reports[0]['stages'][arm] if isinstance(reports[0]['stages'][arm][k],int)} for arm in ('U','A1')},
        known_development_only=True,transfer_claim=False)
