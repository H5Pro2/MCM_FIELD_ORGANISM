"""Evaluation-only decisions. No replay or source generation imports."""
import math
from fractions import Fraction
from tools._s2uc_eval_evidence import assess as evidence, ARMS


def adaptation(decisions, switch):
    rows = {r['target']: r for r in decisions}
    def correct(t):
        r = rows.get(t, {})
        return bool(r.get('selected_label') == switch['wanted'] and
            r.get('reason') == 'SELECTED_BY_ERROR' and r.get('strict_warm_winner') and
            r.get('original_frozen_verified') and
            any(switch['targets'][0] <= f < t for f in r.get('prior_feedback', [])))
    targets = switch['targets']
    checks = [correct(t) for t in targets]
    latency = next((i+1 for i in range(len(targets)) if all(checks[i:])), None)
    missing = [t for t in targets if switch['wanted'] not in rows.get(t, {}).get('available_labels', [])]
    return dict(**switch, passed=all(checks[2:]), latency=latency,
                missing_context_targets=missing, target_checks=dict(zip(targets, checks)))


def assess_case(results, source, spec):
    r = evidence(results, source, spec)
    # Legacy XYX-specific verdicts are deliberately not part of this evaluation.
    for name in ('selection', 'expectation_deviations', 'net_benefit_H', 'total_benefit_G'):
        r.pop(name, None)
    r.update(id=spec['id'], duration=spec['duration'], stable=spec['stable'],
             switches=[adaptation(r['decisions'], s) for s in spec['switches']])
    for d in r['decisions']:
        wanted = spec['blocks'][(d['target']-1)//4]
        hs = [h for h in d['hypotheses'] if h['label'] == wanted]
        d['availability'] = ('NO_ELIGIBLE_CONTEXT' if not d['hypotheses'] else
            'WANTED_ABSENT' if not hs else 'WANTED_COLD' if all(h['before'] is None for h in hs)
            else 'WANTED_WARM')
        d['competition'] = len(set(d['available_labels'])) > 1
    return r


def thresholds(switches):
    counts = {d: sum(bool(s['passed']) for s in switches if s['duration'] == d) for d in (3, 5)}
    denominators = {d: sum(s['duration'] == d for s in switches) for d in (3, 5)}
    total = sum(counts.values())
    valid = len(switches) == 48 and denominators == {3: 24, 5: 24}
    return dict(passed=valid and total >= 39 and min(counts.values()) >= 18,
                successes=total, denominator=len(switches), per_duration=counts,
                denominators=denominators)


def aggregate(reports, specs):
    bad = []
    if [r.get('id') for r in reports] != [s['id'] for s in specs] or len(specs) != 32:
        bad.append('CASE_SET')
    summaries = {}; differences = []; switches = []; exact = {}
    def mean(r, mask, arm):
        m=r['metrics'][mask][arm]
        return Fraction(m['error_sum'])/m['count']
    try:
        for r, s in zip(reports, specs):
            if r['technical_errors']: bad.append('TECHNICAL:'+r['id'])
            if (r['duration'], r['stable']) != (s['duration'], s['stable']): bad.append('CASE_METADATA')
            if len(r['switches']) != len(s['switches']): bad.append('SWITCH_SET')
            for sw, expected in zip(r['switches'], s['switches']):
                if any(sw[k] != v for k, v in expected.items()): bad.append('SWITCH_SPEC')
                switches.append(dict(sw, duration=s['duration'], case=s['id']))
            for mask, targets in s['masks'].items():
                for arm in ARMS:
                    m = r['metrics'][mask][arm]
                    if m['missing'] or m['count'] != len(targets): bad.append('MISSING_TARGET')
                    if targets and (m['mae'] is None or not math.isfinite(m['mae']) or not 0 <= m['mae'] <= 1):
                        bad.append('INVALID_MAE')
            for arm in ARMS[1:]:
                delta = mean(r,'G','U')-mean(r,'G',arm)
                differences.append(dict(case=s['id'], baseline=arm, delta=float(delta), exact_delta=str(delta),
                    within_damage_limit=delta<=Fraction(1,32),
                    stable=s['stable'], duration=s['duration']))
        for mask in ('G', 'H', 'N', 'S', 'S_w', 'F', 'A'):
            subset = [r for r in reports if r['metrics'][mask]['U']['count']]
            exact[mask]={a:sum((mean(r,mask,a) for r in subset),Fraction())/len(subset) if subset else None for a in ARMS}
            summaries[mask] = {a: dict(
                case_mean=float(exact[mask][a]) if subset else None,
                case_mean_exact=str(exact[mask][a]) if subset else None,
                position_mean=sum(r['metrics'][mask][a]['error_sum'] for r in subset)/sum(r['metrics'][mask][a]['count'] for r in subset) if subset else None,
                cases=len(subset), positions=sum(r['metrics'][mask][a]['count'] for r in subset)) for a in ARMS}
        adaptation_result = thresholds(switches)
        if adaptation_result['denominators'] != {3:24, 5:24}: bad.append('SWITCH_DENOMINATOR')
        verdicts = {m: 'BELEGT' if all(exact[m]['U'] < exact[m][a] for a in ARMS[1:]) else 'NICHT_NACHGEWIESEN' for m in ('H', 'G')}
        warm_ok = all(exact['S_w']['U'] <= exact['S_w'][a] for a in ARMS[1:])
        damage_ok = all(d['within_damage_limit'] for d in differences)
        verdicts.update(adaptation='BELEGT' if adaptation_result['passed'] else 'NICHT_NACHGEWIESEN',
            stability_damage='BELEGT' if warm_ok and damage_ok else 'SCHADENSGRENZE_VERLETZT')
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
        bad.append(type(exc).__name__+':'+str(exc)); adaptation_result = {}; verdicts = {}
    if bad: verdicts = {k:'NOT_EVALUABLE' for k in ('H','G','adaptation','stability_damage')}
    # Per-target and switch records remain the authoritative exhaustive diagnostics.
    damage_summary = {}
    for a in ARMS[1:]:
        rows = [d for d in differences if d['baseline'] == a]
        target_deltas=[dict(case=r['id'],target=c['target'],delta=c['U_minus'][a])
            for r in reports for c in r.get('comparisons',[])]
        damage_summary[a] = dict(worst_case=max(rows, key=lambda d:d['delta']) if rows else None,
            harmed_cases=sum(d['delta']>0 for d in rows), gained_cases=sum(d['delta']<0 for d in rows),
            loss_sum=sum(max(0,d['delta']) for d in rows), gain_sum=sum(max(0,-d['delta']) for d in rows),
            harmed_targets=sum(d['delta']>0 for d in target_deltas),gained_targets=sum(d['delta']<0 for d in target_deltas),
            target_loss_sum=sum(max(0,d['delta']) for d in target_deltas),target_gain_sum=sum(max(0,-d['delta']) for d in target_deltas),
            worst_target=max(target_deltas,key=lambda d:d['delta']) if target_deltas else None)
    groups={}
    if not bad:
        for name,predicate in (('stable',lambda r:r['stable']),('changing',lambda r:not r['stable']),
                               ('duration3',lambda r:r['duration']==3),('duration5',lambda r:r['duration']==5)):
            subset=[r for r in reports if predicate(r)]
            groups[name]={m:{a:float(sum((mean(r,m,a) for r in subset),Fraction())/len(subset)) for a in ARMS} for m in ('G','H')}
    direction_counts={k:dict(successes=sum(s['passed'] for s in switches if s.get('direction')==k),
        denominator=sum(s.get('direction')==k for s in switches)) for k in ('XY','YX')}
    return dict(technical_errors=bad, verdicts=verdicts, summaries=summaries,
        adaptation=adaptation_result, switches=switches, case_differences=differences,
        damage_summary=damage_summary,diagnostic_groups=groups,direction_counts=direction_counts,
        all_criteria_met=not bad and all(v=='BELEGT' for v in verdicts.values()),
        independent_generalization='NICHT_GEPRUEFT', scope='PROSPECTIVE_CONSTRUCTED_FAMILY_ONLY')
