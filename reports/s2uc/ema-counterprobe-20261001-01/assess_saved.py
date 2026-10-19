"""Assess the fixed criteria using saved results only; never replay or generate."""
import json
import math
from pathlib import Path
from tools import s2uc_ema_qualification as q

OUT=Path(__file__).resolve().parent


def save(name,value):q.save(OUT/name,value)


def mean(rows):return math.fsum(r['selected_mae'] for r in rows)/len(rows)


def assess():
    plan=q.read(q.PLAN);closure=q.read(OUT/'execution-closure.json')
    assert closure['status']=='COMPLETE'
    primary=set(plan['primary_targets']);secondary=set(plan['secondary_targets'])
    assert len(primary)==24 and len(secondary)==75 and not primary&secondary
    report={};details={};harms={};phases=[];resource_rows=[];criteria={}
    for story in plan['stories']:
        systems={arm:q.read(OUT/(story+'-'+arm+'.json'),8388608) for arm in plan['arms']}
        rows={arm:{r['target']:r for r in s['rows']} for arm,s in systems.items()}
        assert systems['E']['state_hashes']==systems['K']['state_hashes']==systems['P']['state_hashes']
        assert all(len(s['state_hashes'])==200 and s['frames']==200 and s['states_identical'] and
            s['censored_target']==201 and s['slots_released'] and s['ema_cleared'] for s in systems.values())
        assert all(set(r)==primary|secondary for r in rows.values())
        report[story]={arm:dict(primary_count=24,secondary_count=75,
            primary_mae=mean([r for t,r in data.items() if t in primary]),
            secondary_mae=mean([r for t,r in data.items() if t in secondary]),
            all99_mae=mean(list(data.values()))) for arm,data in rows.items()}
        details[story]=[];harms[story]={'primary':{},'secondary':{}}
        for target in sorted(primary|secondary):
            chosen=rows['E'][target];group='primary' if target in primary else 'secondary'
            row=dict(target=target,group=group,choice=chosen['choice'],
                E=chosen['selected_mae'],K=rows['K'][target]['selected_mae'],P=rows['P'][target]['selected_mae'])
            for baseline in ('K','P'):
                row['delta_vs_'+baseline]=row['E']-row[baseline]
                if row['delta_vs_'+baseline]>0:
                    harms[story][group].setdefault(baseline,[]).append(dict(target=target,
                        E=row['E'],baseline=row[baseline],mae_increase=row['delta_vs_'+baseline]))
            details[story].append(row)
        for arm,s in systems.items():resource_rows.append(dict(story=story,arm=arm,**s['resources']))
        # Read match ancestry, without giving any identity to the system.
        retained_A=[]
        for f in systems['E']['forecasts']:
            if f['target'] in primary:
                matches=f['receipt']['matches']
                retained_A.append(len(matches)==1 and matches[0]['role']=='retained' and matches[0]['ordinals']==[1,2,3,4])
        assert all(retained_A)
        updates=systems['E']['error_updates']
        assert [x['target'] for x in updates]==list(range(3,200,2))
        assert all(x['actual_entered'] and x['atomic_pair_verified'] for x in updates)
        if story=='constant':
            first=next(u['target'] for u in updates if u['key_live'] and u['ticket'][2]==0)
            later=[x for x in details[story] if x['target']>first]
            criteria['stable_control']=dict(first_usable_retained_outcome=first,
                passed=all(x['E']<=x['K'] for x in later),
                scope='all subsequent scored positions, not just primary targets',
                first_and_warm_losses_included=True)
        else:
            for phase,(lo,hi,wanted) in enumerate([(1,8,'CONTEXT'),(9,16,'PERSISTENCE'),(17,24,'CONTEXT')],1):
                targets=plan['primary_targets'][lo-1:hi]
                data=[rows['E'][t] for t in targets]
                reached=next((i+1 for i in range(8) if all(x['choice']==wanted for x in data[i:])),None)
                phases.append(dict(phase=phase,cycles=[lo,hi],wanted=wanted,targets=targets,
                    choices=[x['choice'] for x in data],stable_from_position=reached,
                    passed=reached is not None and reached<=3,
                    error_sums={arm:math.fsum(rows[arm][t]['selected_mae'] for t in targets) for arm in plan['arms']}))
            means=report[story]
            criteria['switch_better_than_both']=dict(passed=means['E']['primary_mae']<means['K']['primary_mae'] and
                means['E']['primary_mae']<means['P']['primary_mae'],primary_mae={k:v['primary_mae'] for k,v in means.items()})
    criteria['adaptation_by_third']=dict(passed=all(p['passed'] for p in phases),phases=phases)
    criteria['context_return']=dict(passed=phases[-1]['passed'] and phases[-1]['wanted']=='CONTEXT')
    criteria['status']='CONTROLLED_FUNCTION_CRITERIA_MET' if all(v['passed'] for v in criteria.values()) else 'CRITERIA_NOT_MET'
    save('criteria.json',criteria);save('comparison.json',report);save('decisions.json',details);save('all-harms.json',harms)
    save('phase-trajectories.json',phases);save('resource-ledger.json',resource_rows)
    pre=q.read(OUT/'preexecution.json');assert pre['code']==q.hashes()
    assert q.sha(q.PLAN)==pre['plan_sha256'] and q.sha(q.BINDING)==pre['binding_sha256']
    assert q.sha(OUT/'run_bound.py')==pre['runner_sha256']
    peaks=dict(additional_python_bytes=max(x['additional_python_peak'] for x in resource_rows),
        frame_peak=max(x['frame_meter']['frame_peak'] for x in resource_rows),
        output_peak=max(x['frame_meter']['output_slots_peak'] for x in resource_rows),
        combined_peak=max(x['frame_meter']['combined_peak'] for x in resource_rows))
    save('final-verification.json',dict(status='PASS',stories=2,arms_per_story=3,
        experimental_arm_admissions=1200,internal_reference_advances=1200,
        distinct_material_frames=400,no_midstory_reset=True,primary_per_story_per_arm=24,
        secondary_per_story_per_arm=75,censored_per_story_per_arm=201,
        states_identical_every_frame=True,updates_only_after_actual=True,lifetimes_checked=True,
        slots_released=True,bindings_unchanged=True,parameters_unchanged=True,
        A_trace_retained_at_all_primary_targets=True,peaks=peaks))
    print(json.dumps(dict(criteria=criteria,comparison=report,harms=harms,peaks=peaks),indent=2))


if __name__=='__main__':assess()
