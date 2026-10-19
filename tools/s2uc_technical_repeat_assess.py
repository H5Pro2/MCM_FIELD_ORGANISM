"""Post-run read-only evidence audit. Never invokes a replay or source generator."""
from collections import Counter
from datetime import datetime
from fractions import Fraction
import json
from pathlib import Path
import time

from tools import s2uc_repeat_prepare_v4 as q

ROOT=q.ROOT
RUN=q.OUT
OUT=ROOT/'reports/s2uc/technical-repeat-assessment-20261003-01'
AUTH=ROOT/'docs/S2UC_TECHNISCHE_WIEDERHOLUNG_V4_AUTORISIERUNG_20261003.json'
SCRIPT=Path(__file__)
LIMIT=64*1048576
RESERVE=1048576


def size(folder):
    return sum(p.stat().st_size for p in folder.rglob('*') if p.is_file())


def charge():
    return q.charged_bytes(AUTH)+size(RUN)+size(OUT)+SCRIPT.stat().st_size


def save(name,value):
    raw=(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
    if len(raw)>524288:raise RuntimeError('REPORT_FILE_CAP:'+name)
    if charge()+len(raw)>LIMIT-RESERVE:raise RuntimeError('REPORT_BUDGET')
    with (OUT/name).open('xb') as f:f.write(raw)


def inventory(folder):
    return {p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=q.old.sha(p))
            for p in folder.rglob('*') if p.is_file()}


def sealed(folder):
    closure=q.old.read(folder/'closure.json')
    for n,v in closure['files'].items():
        if q.old.sha(folder/n)!=v['sha256'] or (folder/n).stat().st_size!=v['bytes']:
            raise RuntimeError('SEALED_FILE_CHANGED:'+str(folder/n))
    return closure


def assess():
    started=time.perf_counter_ns()
    if not (RUN/'closure.json').exists():raise RuntimeError('RUN_NOT_CLOSED')
    q.preparation_check();binding=q.verify();closure=sealed(RUN)
    auth=q.old.read(AUTH);template=q.old.read(q.TEMPLATE)
    q.validate_authorization(auth,q.authorization('AUTHORIZED_ONCE'))
    if [k for k in template if template[k]!=auth[k]]!=['status']:raise RuntimeError('AUTHORIZATION_DIFF')
    claim=q.old.read(RUN/'claim.json')['binding']
    if claim!={'authorization_sha256':q.old.sha(AUTH),'binding_sha256':q.old.sha(q.BINDING)}:
        raise RuntimeError('RUN_CLAIM_BINDING')
    events=[json.loads(s) for s in (RUN/'lifecycle.jsonl').read_text().splitlines()]
    ev={e['event']:e for e in events}
    if ev['worker_end_confirmed']['alive']:raise RuntimeError('WORKER_ALIVE')
    if ev['closure_admin_finished']['closure_file_sha256']!=q.old.sha(RUN/'closure.json'):
        raise RuntimeError('TERMINAL_CLOSURE_HASH')
    historical={}
    for folder in (q.old.OUT,ROOT/'reports/s2uc/raster32-assessment-20261003-01'):
        c=sealed(folder);historical[folder.relative_to(ROOT).as_posix()]=dict(files=len(c['files']),sha256=q.old.sha(folder/'closure.json'))
    OUT.mkdir(exist_ok=False)
    specs=q.old.read(q.PLAN)['cases'];manifest=q.old.read(RUN/'manifest.json')
    if [e['id'] for e in manifest['entries']]!=[s['id'] for s in specs]:raise RuntimeError('MANIFEST_CASE_SET')
    if not manifest['all_sources_before_policy']:raise RuntimeError('MANIFEST_ORDER')
    manifest_hash=q.old.sha(RUN/'manifest.json')
    starts=sorted([q.old.read(p) for p in RUN.glob('*-start.json')],key=lambda x:x['started_at'])
    if any(s['manifest_sha256']!=manifest_hash for s in starts):raise RuntimeError('START_MANIFEST')
    expected_order=[(s['id'],a) for s in specs for a in q.old.ARMS]
    if [(s['case'],s['arm']) for s in starts]!=expected_order[:len(starts)]:raise RuntimeError('START_ORDER')
    if starts and datetime.fromisoformat(manifest['sealed_at'])>datetime.fromisoformat(starts[0]['started_at']):
        raise RuntimeError('MANIFEST_AFTER_START')
    reports=[];resources=[];targets=[];contexts=[];switches=[];missing=[];recomputed=[]
    completed_admissions=0;completed_references=0
    for spec,entry in zip(specs,manifest['entries']):
        name=spec['id'];source=q.old.read(RUN/entry['source_file'])
        if q.old.sha(RUN/entry['source_file'])!=entry['source_sha256'] or q.old.digest(source)!=entry['profile']:
            raise RuntimeError('SOURCE_BINDING:'+name)
        if len(source)!=spec['frames'] or entry['masks']!=spec['masks']:raise RuntimeError('SOURCE_SPEC:'+name)
        results={}
        for arm in q.old.ARMS:
            path=RUN/f'{name}-{arm}.json'
            if not path.exists():missing.append(dict(case=name,arm=arm));continue
            r=q.old.read(path);q.old.resource_check(r)
            if r['frames']!=spec['frames'] or len(r['admissions'])!=spec['frames']:
                raise RuntimeError('ADMISSION_COUNT:'+name+arm)
            states=r['states'] if arm=='U' else r['state_hashes']
            if len(states)!=spec['frames'] or not r['states_identical']:raise RuntimeError('REFERENCE_COUNT')
            completed_admissions+=len(r['admissions']);completed_references+=len(states)
            results[arm]=r
            resources.append(dict(case=name,arm=arm,frames=spec['frames'],terminal_cleanup=r['terminal_cleanup'],
                slots_released=r['slots_released'],states_identical=r['states_identical'],
                ema_cleared=r.get('ema_cleared'),resources=r['resources']))
        if len(results)!=5:continue
        # Compare persisted JSON semantics (integer dictionary keys serialize as strings).
        r=json.loads(json.dumps(q.old.assess_case(results,source,spec)))
        if r['technical_errors']:raise RuntimeError('CASE_EVIDENCE:'+name+str(r['technical_errors']))
        if not (RUN/f'{name}-assessment.json').exists():
            # A killed worker may have exported five arms but not sealed its case assessment.
            save(name+'-postrun-assessment.json',r)
            recomputed.append(name)
        elif r!=q.old.read(RUN/f'{name}-assessment.json'):raise RuntimeError('CASE_REASSESSMENT_DIFFERENCE:'+name)
        reports.append(r)
        local_contexts=[]
        for d in r['decisions']:
            warm=[h['before'][0]-h['before'][1] for h in d['hypotheses'] if h['before'] is not None]
            negative=[x for x in warm if x<0]
            fallback=('CONTEXT_SELECTED' if d['selected_label']!='P' else
                'NO_ELIGIBLE_CONTEXT' if not d['hypotheses'] else
                'ALL_ELIGIBLE_COLD' if not warm else
                'NO_STRICT_IMPROVEMENT' if not negative else
                'TIED_NEGATIVE_WINNERS' if negative.count(min(negative))>1 else 'UNEXPECTED_PERSISTENCE')
            if fallback=='UNEXPECTED_PERSISTENCE':raise RuntimeError('PERSISTENCE_CLASSIFICATION')
            row=dict(case=name,duration=spec['duration'],stable=spec['stable'],
                wanted=spec['blocks'][(d['target']-1)//4],fallback_cause=fallback,
                masks=[m for m,ts in spec['masks'].items() if d['target'] in ts],**d)
            local_contexts.append(row)
            contexts.append({k:row[k] for k in ('case','duration','stable','wanted','masks','target','availability','competition','selected_label','reason','available_labels','fallback_cause')})
        save(name+'-contexts.json',local_contexts)
        for c in r['comparisons']:
            targets.append(dict(case=name,duration=spec['duration'],stable=spec['stable'],
                masks=[m for m,ts in spec['masks'].items() if c['target'] in ts],**c))
        bytarget={c['target']:c for c in r['comparisons']}
        for sw in r['switches']:
            first=sw['targets'][0]
            switches.append(dict(case=name,duration=spec['duration'],**sw,
                first_target_errors=bytarget[first]['errors'],first_target_U_minus=bytarget[first]['U_minus'],
                losses_by_target=[dict(target=t,U_minus=bytarget[t]['U_minus']) for t in sw['targets']]))
        del results,source,r
    complete=(closure['status']=='COMPLETE' and len(reports)==32 and not missing and len(starts)==160
              and completed_admissions==10240 and completed_references==10240)
    if complete:
        marker=q.old.read(RUN/'worker-complete.json')
        if (marker['cases'],marker['experimental_admissions'],marker['reference_advances'])!=(32,10240,10240):
            raise RuntimeError('COMPLETION_COUNTS')
        aggregate=q.old.aggregate(reports,specs)
        saved=q.old.read(RUN/'assessment.json')
        for k,v in aggregate.items():
            if k=='scope':continue
            if saved.get(k)!=json.loads(json.dumps(v)):raise RuntimeError('AGGREGATE_DIFFERENCE:'+k)
        if aggregate['technical_errors']:raise RuntimeError('AGGREGATE_INVALID')
        aggregate=saved
    else:
        aggregate=dict(technical_errors=['INCOMPLETE_RUN'],verdicts={k:'NOT_EVALUABLE' for k in ('adaptation','H','G','stability_damage')},
            adaptation=dict(successes=sum(s['passed'] for s in switches),denominator=48,
                observed=len(switches),unknown=48-len(switches)),all_criteria_met=False)
    save('aggregate.json',aggregate)
    save('all-target-differences.json',targets)
    save('all-switches.json',switches)
    bymask={}
    for mask in ('G','H','N','S','S_w','F','A'):
        ct=[c for c in contexts if mask in c['masks']]
        ts=[r for r in targets if mask in r['masks']]
        bymask[mask]=dict(targets=len(ts),availability=dict(Counter(c['availability'] for c in ct)),
            competition=sum(c['competition'] for c in ct),reasons=dict(Counter(c['reason'] for c in ct)),
            fallback_causes=dict(Counter(c['fallback_cause'] for c in ct)),
            selected_labels=dict(Counter(c['selected_label'] for c in ct)),
            positions_MAE={a:sum(t['errors'][a] for t in ts)/len(ts) if ts else None for a in q.old.ARMS},
            damages={a:dict(harmed_targets=sum(t['U_minus'][a]>0 for t in ts),
                gained_targets=sum(t['U_minus'][a]<0 for t in ts),
                loss_sum=sum(max(0,t['U_minus'][a]) for t in ts),gain_sum=sum(max(0,-t['U_minus'][a]) for t in ts),
                worst=max((dict(case=t['case'],target=t['target'],delta=t['U_minus'][a]) for t in ts),key=lambda t:t['delta'],default=None)) for a in q.old.ARMS[1:]} )
        if complete and len(ts)!=sum(len(s['masks'][mask]) for s in specs):raise RuntimeError('MASK_COUNT:'+mask)
    save('availability-and-costs.json',dict(masks=bymask,overlap_notice='F/A/S are diagnostic subsets; do not add to G/H/N',
        switch_groups={k:dict(count=sum(s['kind']==k for s in switches),passed=sum(s['passed'] for s in switches if s['kind']==k),
            latencies=dict(Counter(str(s['latency']) for s in switches if s['kind']==k))) for k in ('change','return')},
        first_forecast=[t for t in targets if t['target']==3]))
    resource_summary={}
    for arm in q.old.ARMS:
        rows=[r for r in resources if r['arm']==arm]
        resource_summary[arm]=dict(completed_arms=len(rows),max_heap=max((r['resources']['additional_python_peak'] for r in rows),default=None),
            all_released=all(r['terminal_cleanup'] and r['slots_released'] and r['states_identical'] for r in rows))
        if arm=='U':
            resource_summary[arm].update({k:max((r['resources'][k] for r in rows),default=None) for k in
                ('original_frames_upper_bound','combined_upper_bound','packed','receipt_bytes_peak','utf8_upper','original_frames_peak','output_slots_peak','combined_peak')})
        else:
            resource_summary[arm]['meter_maxima']={k:max((r['resources']['meter'][k] for r in rows),default=None)
                for k in rows[0]['resources']['meter']} if rows else {}
    # Detailed U per-operation resources already exist in immutable arm exports.
    save('resources.json',dict(summary=resource_summary,arms=[dict(case=r['case'],arm=r['arm'],frames=r['frames'],
        terminal_cleanup=r['terminal_cleanup'],resources={k:v for k,v in r['resources'].items() if k!='calls'}) for r in resources],
        qualification_reused=True,unmeasured_U_peaks_are_not_zero_usage=True,packed_baseline_constant_is_not_proof_of_allocation=True,
        total_process_RAM_measured=False))
    timing=dict(events=events,worker_seconds=(ev['worker_end_confirmed']['monotonic_ns']-ev['deadline_established']['monotonic_ns'])/1e9,
        closure_seconds=(ev['closure_admin_finished']['monotonic_ns']-ev['closure_admin_started']['monotonic_ns'])/1e9,
        total_seconds=(ev['closure_admin_finished']['monotonic_ns']-ev['deadline_established']['monotonic_ns'])/1e9,
        deadline_met=ev['closure_admin_finished']['total_deadline_met'],abort_requested='abort_requested' in ev,
        terminal_journal_write_excluded=True,postrun_audit_outside_execution_window=True)
    if (RUN/'phase-times.json').exists():timing['phases']=q.old.read(RUN/'phase-times.json')
    save('chronology.json',dict(timing=timing,manifest_sha256=manifest_hash,sealed_at=manifest['sealed_at'],
        first_start=starts[0] if starts else None,last_start=starts[-1] if starts else None,
        starts=len(starts),source_positions=sum(e['frames'] for e in manifest['entries']),
        known_full_source_matches=sum(bool(e['full_matches']) for e in manifest['entries']),
        sources=[dict(id=e['id'],profile=e['profile'],source_sha256=e['source_sha256'],full_matches=e['full_matches']) for e in manifest['entries']]))
    save('verification.json',dict(binding_sha256=q.old.sha(q.BINDING),bound_code_files=len(binding['code']),
        authorization_sha256=q.old.sha(AUTH),authorization_changed_fields=['status'],historical=historical,
        run_inventory=inventory(RUN),complete=complete,completed_cases=len(reports),completed_arms=len(resources),
        completed_admissions=completed_admissions,completed_reference_advances=completed_references,
        missing_arms=missing,postrun_reconstructed_case_assessments=recomputed,
        new_replays_in_audit=0,source_generation_in_audit=False,evidence_status=q.STATUS,
        old_raster_status='NOT_EVALUABLE',run_resume_permitted=False))
    save('audit-state.json',dict(status='AUDITED',run_complete=complete,verdicts=aggregate['verdicts'],
        duration_seconds=timing['total_seconds'],audit_seconds=(time.perf_counter_ns()-started)/1e9,
        budget_before_report=charge(),script_sha256=q.old.sha(SCRIPT)))
    print(json.dumps(dict(complete=complete,verdicts=aggregate['verdicts'],adaptation=aggregate['adaptation'],
        resources=resource_summary,timing={k:v for k,v in timing.items() if k not in ('events','phases')},budget=charge())))


if __name__=='__main__':assess()
