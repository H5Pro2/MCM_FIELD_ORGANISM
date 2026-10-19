"""Separate modal mechanism, actual prediction loss, and fixed late window."""
from fractions import Fraction
from tools import _s2uc_t1_evidence_v2 as evidence

ARMS=evidence.ARMS


def transitions(decisions,spec,bundle):
    by={d['target']:d for d in decisions};out=[]
    for number,p in enumerate(spec['phases'][1:],1):
        checks=[];details=[]
        for t in p['targets']:
            d=by[t];modal=bundle['modal'][t-1]
            good=bool(modal is not None and d['selected_key'] is not None and
                d['selected_label']==evidence.digest(modal) and d['reason']=='SELECTED_BY_ERROR' and
                d['strict_warm_winner'] and d['original_frozen_verified'] and
                any(p['start']<=f<t for f in d['prior_feedback']))
            checks.append(good)
            details.append(dict(target=t,passed=good,modal_profile=None if modal is None else evidence.digest(modal),
                actual_profile=evidence.digest(bundle['values'][t-1]),selected_profile=d['selected_label'],
                phase_feedback=[f for f in d['prior_feedback'] if p['start']<=f<t]))
        deadline=min(3,len(checks))
        passed=bool(checks and all(checks[deadline-1:]))
        out.append(dict(case=spec['id'],replicate=spec['replicate'],phase=number,**p,
            passed=passed,latency=next((i+1 for i in range(len(checks)) if all(checks[i:])),None),
            mechanism_only=True,prediction_failure_implied=False,details=details))
    return out


def assess_case(results,bundle,spec):
    r=evidence.assess(results,bundle['values'],spec)
    if r['technical_errors']:return r|dict(id=spec['id'],replicate=spec['replicate'],switches=[])
    for d in r['decisions']:
        t=d['target'];actual=evidence.digest(bundle['values'][t-1]);modal=bundle['modal'][t-1]
        hs=d['hypotheses'];matching=[h for h in hs if h['label']==actual]
        d.update(actual_profile=actual,modal_profile=None if modal is None else evidence.digest(modal),
            actual_availability='NO_ELIGIBLE_CONTEXT' if not hs else 'ACTUAL_ABSENT' if not matching else
                'ACTUAL_COLD' if all(h['before'] is None for h in matching) else 'ACTUAL_WARM',
            eligible=len(hs),warm=sum(h['before'] is not None for h in hs),
            raw_matches=len(results['U']['forecasts'][(t-3)//2]['matches']))
    switches=transitions(r['decisions'],spec,bundle)
    for w in switches:
        w['phase_actual_errors']=[c for c in r['comparisons'] if w['start']<=c['target']<=w['end']]
    return r|dict(id=spec['id'],replicate=spec['replicate'],stable=spec['stable'],
        switches=switches,late_window='FIXED_TARGETS_NOT_ASSUMED_WARM')


def aggregate(reports,specs):
    errors=[]
    if [r.get('id') for r in reports]!=[s['id'] for s in specs] or len(specs)!=16:errors.append('CASE_SET')
    switches=[w for r in reports for w in r.get('switches',[])];groups=sorted({s['replicate'] for s in specs})
    if len(switches)!=52 or len(groups)!=4:errors.append('SWITCH_DENOMINATOR')
    for r,s in zip(reports,specs):
        if r['technical_errors']:errors.append('CASE_EVIDENCE:'+s['id']);continue
        if len(r['switches'])!=len(s['phases'])-1:errors.append('CASE_SWITCH_COUNT')
        for mask,ts in s['masks'].items():
            for a in ARMS:
                m=r['metrics'][mask][a]
                if m['missing'] or m['count']!=len(ts):errors.append('MISSING_TARGET')
    neutral_controls=[w for w in switches if w['negative_control']]
    if len(neutral_controls)!=20:errors.append('NEGATIVE_CONTROL_COUNT')
    verdicts={k:'NOT_EVALUABLE' for k in ('recognition','adaptation','G','stability_damage')}
    if errors:return dict(technical_errors=errors,verdicts=verdicts,denominator=52)
    def mean(r,m,a):
        v=r['metrics'][m][a];return Fraction(v['error_sum'])/v['count']
    summaries={m:{a:dict(case_mean_exact=str(sum((mean(r,m,a) for r in reports if r['metrics'][m][a]['count']),Fraction())/
        sum(bool(r['metrics'][m][a]['count']) for r in reports)),
        case_mean=float(sum((mean(r,m,a) for r in reports if r['metrics'][m][a]['count']),Fraction())/
        sum(bool(r['metrics'][m][a]['count']) for r in reports)),
        position_mean=sum(r['metrics'][m][a]['error_sum'] for r in reports)/sum(r['metrics'][m][a]['count'] for r in reports))
        for a in ARMS} for m in ('G','G_w')}
    recognized=[r for r in reports if any(d['eligible'] for d in r['decisions'])]
    counts={str(g):dict(successes=sum(w['passed'] for w in switches if w['replicate']==g),
        denominator=sum(w['replicate']==g for w in switches)) for g in groups}
    recognition=len(recognized)>=4 and len({r['replicate'] for r in recognized})>=2
    adaptation=sum(w['passed'] for w in switches)>=26 and all(v['denominator']==13 and v['successes']>=4 for v in counts.values())
    benefit=all(Fraction(summaries['G']['U']['case_mean_exact'])<Fraction(summaries['G'][a]['case_mean_exact']) for a in ARMS[1:])
    damage=[dict(case=r['id'],baseline=a,delta=float(mean(r,'G','U')-mean(r,'G',a)),
        exact_delta=str(mean(r,'G','U')-mean(r,'G',a))) for r in reports for a in ARMS[1:]]
    late=all(Fraction(summaries['G_w']['U']['case_mean_exact'])<=Fraction(summaries['G_w'][a]['case_mean_exact']) for a in ARMS[1:])
    safe=late and all(Fraction(d['exact_delta'])<=Fraction(1,32) for d in damage)
    verdicts=dict(recognition='BELEGT' if recognition else 'NICHT_NACHGEWIESEN',
        adaptation='BELEGT' if adaptation else 'NICHT_NACHGEWIESEN',G='BELEGT' if benefit else 'NICHT_NACHGEWIESEN',
        stability_damage='BELEGT' if safe else 'SCHADENSGRENZE_VERLETZT')
    return dict(technical_errors=[],verdicts=verdicts,summaries=summaries,case_differences=damage,
        switches=switches,adaptation=dict(successes=sum(w['passed'] for w in switches),denominator=52,groups=counts),
        recognition=dict(cases=len(recognized),groups=len({r['replicate'] for r in recognized}),denominator=16),
        negative_controls=dict(count=20,passed=sum(w['passed'] for w in neutral_controls),
            included_in_denominator=52,prediction_failure_implied=False,
            groups={m:dict(count=sum(w['mode']==m for w in neutral_controls),
                passed=sum(w['passed'] for w in neutral_controls if w['mode']==m)) for m in ('I','H')}),late_window='FIXED_TARGETS_NOT_ASSUMED_WARM',
        all_criteria_met=all(v=='BELEGT' for v in verdicts.values()),scope='SYNTHETIC_VECTOR_BOUNDARY_ONLY',
        audio_video_chain=False,independent_population_claim=False)
